"""
LineByLine Persistence Layer
Phase 7E — Supabase database wiring AROUND the existing explanation engine.

DESIGN PRINCIPLES (critical, do not violate):
  1. Persistence is BEST-EFFORT. If Supabase is down/misconfigured, the
     tutor experience (Gemini analysis, personas, quizzes, Tutor UI) must
     continue working exactly as it did in Phase 1–6 using Flask session.
  2. NEVER rewrite the explainer. NEVER mutate the Gemini response shape.
     We only OBSERVE the return values and (optionally) persist a subset.
  3. Identity comes ONLY from the verified Supabase JWT (via auth module).
     Never accept student_id, user_id, or owner columns from request JSON.
  4. Deterministic master formula: simple arithmetic, no randomness, no ML.
  5. Concept normalisation: Gemini concepts are matched against the canonical
     `concepts` table by slug/name similarity. Unknown concepts do NOT crash
     the persistence layer — we just skip writing that misconception/progress
     row or leave concept_id = NULL where the FK allows it.
  6. learner_progress UNIQUE(student_id, concept_id): we use an upsert-like
     pattern via Supabase client — no duplicate rows possible.
  7. UUID ↔ UUID everywhere.
  8. Service-role operations only (supabase_client from auth.py has BYPASSRLS).
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Tuple

# The Supabase service-role client is initialised in auth.py and is BYPASSRLS.
from explanation_engine.auth import supabase_client


# =============================================================================
# Graceful failure helpers
# =============================================================================
def _client() -> Any:
    """Return the service-role Supabase client if available, else None."""
    return supabase_client  # may be None if env vars are missing (auth.py handles)


def _safe(func_name: str, fallback, fn):
    """Run fn() and return fallback on ANY exception. Persistence is best-effort."""
    if not _client():
        return fallback
    try:
        return fn()
    except Exception as exc:
        print(f"[persistence] WARN: {func_name} failed (continuing): {exc!r}")
        return fallback


# =============================================================================
# 1. Concept Normalisation — map Gemini free-text concepts to the canonical
#    `concepts` table. Do NOT insert new rows into concepts (curriculum-owned).
# =============================================================================

# Cached once per process to avoid a SELECT on every explain() call.
_CONCEPT_CACHE: Optional[List[Dict[str, str]]] = None
_CACHE_UPDATED_AT: float = 0.0
_CACHE_TTL = 60.0  # seconds


def _slugify(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _load_concepts(force: bool = False) -> List[Dict[str, str]]:
    global _CONCEPT_CACHE, _CACHE_UPDATED_AT
    now = time.time()
    if not force and _CONCEPT_CACHE is not None and (now - _CACHE_UPDATED_AT) < _CACHE_TTL:
        return _CONCEPT_CACHE
    if not _client():
        return []
    try:
        resp = _client().table("concepts").select("id,name,slug").execute()
        rows = getattr(resp, "data", []) or []
        _CONCEPT_CACHE = rows
        _CACHE_UPDATED_AT = now
        return rows
    except Exception as exc:
        print(f"[persistence] WARN: concepts cache load failed: {exc!r}")
        return _CONCEPT_CACHE or []


def find_canonical_concept(concept_name_or_slug: str) -> Optional[Dict[str, Any]]:
    """
    Best-effort normalise a Gemini concept name to the canonical concepts table.

    Returns a dict {id, name, slug} or None if no confident match is found.
    NEVER inserts a new concept (concepts is curriculum-owned).
    """
    if not concept_name_or_slug:
        return None
    query_slug = _slugify(concept_name_or_slug)
    query_name = (concept_name_or_slug or "").strip().lower()
    if not query_slug:
        return None
    rows = _load_concepts()
    if not rows:
        return None

    # 1. Exact slug match (strongest)
    for r in rows:
        if r.get("slug") == query_slug:
            return r
    # 2. Exact name, case-insensitive
    for r in rows:
        if (r.get("name") or "").lower() == query_name:
            return r
    # 3. Slug contains / is contained (loose substring, e.g. "list-indexing" matches "indexing")
    for r in rows:
        rslug = r.get("slug") or ""
        if rslug and (rslug in query_slug or query_slug in rslug):
            return r
    # 4. Word overlap (any shared 4+ char token)
    query_tokens = set(t for t in re.findall(r"[a-z]{4,}", query_slug) if len(t) >= 4)
    if query_tokens:
        best, best_score = None, 0
        for r in rows:
            rtokens = set(t for t in re.findall(r"[a-z]{4,}", r.get("slug") or "") if len(t) >= 4)
            overlap = len(query_tokens & rtokens)
            if overlap > best_score:
                best, best_score = r, overlap
        if best_score >= 1:
            return best
    return None


# =============================================================================
# 2. Student Profile (lazy 1:1 create with auth.users)
# =============================================================================

def ensure_student(user_id: str, display_name: Optional[str] = None) -> bool:
    """Idempotently ensure a `students` row exists for the authenticated user.
    Returns True on success or False if persistence is unavailable."""
    if not user_id:
        return False
    return _safe("ensure_student", False, lambda: _ensure_student_inner(user_id, display_name))


def _ensure_student_inner(user_id: str, display_name: Optional[str]) -> bool:
    # Supabase does not have native INSERT...ON CONFLICT DO NOTHING with returning
    # on all SDK versions, but we can try to select first, then insert, then
    # swallow the duplicate-key exception (non-destructive).
    existing = _client().table("students").select("id").eq("id", user_id).limit(1).execute()
    rows = getattr(existing, "data", []) or []
    if rows:
        # Gentle touch: if we received a display_name and DB has none, update it.
        if display_name and not (rows[0].get("display_name")):
            _client().table("students").update({"display_name": display_name}).eq("id", user_id).execute()
        return True
    try:
        payload: Dict[str, Any] = {"id": user_id}
        if display_name:
            payload["display_name"] = display_name
        _client().table("students").insert(payload, upsert=False).execute()
        return True
    except Exception:
        # Race with another thread is fine — the row now exists.
        rows2 = getattr(_client().table("students").select("id").eq("id", user_id).limit(1).execute(), "data", []) or []
        return len(rows2) > 0


# =============================================================================
# 3. Submissions
# =============================================================================

def persist_submission(
    student_id: str,
    code: str,
    language: str,
    persona: str,
    analysis_summary: Optional[str] = None,
) -> Optional[str]:
    """Insert a submissions row. Returns the new submission UUID or None."""
    if not student_id or not code:
        return None
    return _safe("persist_submission", None, lambda: _persist_submission_inner(
        student_id, code, language, persona, analysis_summary,
    ))


def _persist_submission_inner(student_id, code, language, persona, analysis_summary):
    payload = {
        "student_id": student_id,
        "code": code[:1_000_000],  # defensive cap
        "language": (language or "python")[:32],
        "persona": (persona or "beginner")[:64],
    }
    if analysis_summary:
        payload["analysis_summary"] = analysis_summary[:2000]
    resp = _client().table("submissions").insert(payload).execute()
    rows = getattr(resp, "data", []) or []
    return rows[0]["id"] if rows else None


# =============================================================================
# 4. Misconceptions (learner-specific, dynamic — NO catalog)
# =============================================================================

def persist_misconception(
    student_id: str,
    submission_id: Optional[str],
    title: str,
    explanation: Optional[str] = None,
    concept_name: Optional[str] = None,
    severity: str = "medium",
) -> Optional[str]:
    """
    Persist one learner-specific misconception. If concept_name can be
    normalised to the canonical concepts table, concept_id is set (useful
    for future joins). Unknown concepts just leave concept_id = NULL.
    """
    if not student_id or not title:
        return None
    severity_val = severity if severity in ("low", "medium", "high") else "medium"
    concept_id = None
    if concept_name:
        canon = find_canonical_concept(concept_name)
        if canon:
            concept_id = canon["id"]
    return _safe("persist_misconception", None, lambda: _persist_misconception_inner(
        student_id, submission_id, title, explanation, concept_id, severity_val,
    ))


def _persist_misconception_inner(student_id, submission_id, title, explanation, concept_id, severity_val):
    payload = {
        "student_id": student_id,
        "title": title[:200],
        "severity": severity_val,
    }
    if submission_id:
        payload["submission_id"] = submission_id
    if concept_id:
        payload["concept_id"] = concept_id
    if explanation:
        payload["explanation"] = explanation[:4000]
    resp = _client().table("misconceptions").insert(payload).execute()
    rows = getattr(resp, "data", []) or []
    return rows[0]["id"] if rows else None


# =============================================================================
# 5. Concept Checks (quiz attempts)
# =============================================================================

def persist_concept_check(
    student_id: str,
    submission_id: Optional[str],
    concept_name: Optional[str],
    question_text: Optional[str],
    selected_index: Optional[int],
    correct_index: Optional[int],
    is_correct: bool,
) -> Optional[str]:
    """Persist one MCQ attempt. concept_id is normalised when possible."""
    if not student_id:
        return None
    concept_id = None
    if concept_name:
        canon = find_canonical_concept(concept_name)
        if canon:
            concept_id = canon["id"]
    return _safe("persist_concept_check", None, lambda: _persist_concept_check_inner(
        student_id, submission_id, concept_id, concept_name,
        question_text, selected_index, correct_index, bool(is_correct),
    ))


def _persist_concept_check_inner(
    student_id, submission_id, concept_id, concept_name,
    question_text, selected_index, correct_index, is_correct,
):
    payload = {
        "student_id": student_id,
        "is_correct": bool(is_correct),
    }
    if submission_id:
        payload["submission_id"] = submission_id
    if concept_id:
        payload["concept_id"] = concept_id
    if concept_name:
        payload["concept_name"] = concept_name[:120]
    if question_text:
        payload["question_text"] = question_text[:2000]
    if selected_index is not None:
        payload["selected_index"] = int(selected_index)
    if correct_index is not None:
        payload["correct_index"] = int(correct_index)
    resp = _client().table("concept_checks").insert(payload).execute()
    rows = getattr(resp, "data", []) or []
    return rows[0]["id"] if rows else None


# =============================================================================
# 6. Learner Progress — Deterministic Mastery Algorithm
# =============================================================================
#
# MASTERY FORMULA (Phase 7E — explicit, deterministic, 0..1, no jumps)
#
# Given an existing progress row (N attempts, C correct, I incorrect, S struggles)
# and a NEW interaction at time T:
#
# Delta rules (all deltas are small, bounded):
#
#   on CORRECT concept check:
#     attempts += 1
#     correct_count += 1
#     delta_positive = 0.08 * (1.0 - current_score)       # smaller as we approach 1.0
#     mastery_score = clamp(0, 1, current + delta_positive)
#
#   on INCORRECT concept check:
#     attempts += 1
#     incorrect_count += 1
#     delta_negative = 0.05 * current_score                 # smaller as we approach 0.0
#     mastery_score = clamp(0, 1, current - delta_negative)
#
#   on STRUGGLE detected (misconception + error_type):
#     struggle_count += 1
#     delta_struggle = 0.03 * current_score                 # gentle penalty
#     mastery_score = clamp(0, 1, current - delta_struggle)
#     (applied ONCE per submission, not per misconception)
#
#   last_activity_at = now()
#   updated_at = now()
#
# Row create default: mastery_score = 0, counters = 0
# This avoids dramatic jumps: one correct answer never takes a learner
# from 0.00 to 0.70 in a single step (clamped by the (1.0 - current) multiplier).

CORRECT_DELTA = 0.08
INCORRECT_DELTA = 0.05
STRUGGLE_DELTA = 0.03


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


def apply_correct_answer(current: Dict[str, Any]) -> Dict[str, Any]:
    """Return new counter/score values after one CORRECT quiz answer."""
    score = float(current.get("mastery_score") or 0.0)
    delta = CORRECT_DELTA * (1.0 - score)
    return {
        "attempts":        int(current.get("attempts") or 0) + 1,
        "correct_count":   int(current.get("correct_count") or 0) + 1,
        "incorrect_count": int(current.get("incorrect_count") or 0),
        "struggle_count":  int(current.get("struggle_count") or 0),
        "mastery_score":   _clamp01(score + delta),
    }


def apply_incorrect_answer(current: Dict[str, Any]) -> Dict[str, Any]:
    """Return new counter/score values after one INCORRECT quiz answer."""
    score = float(current.get("mastery_score") or 0.0)
    delta = INCORRECT_DELTA * score
    return {
        "attempts":        int(current.get("attempts") or 0) + 1,
        "correct_count":   int(current.get("correct_count") or 0),
        "incorrect_count": int(current.get("incorrect_count") or 0) + 1,
        "struggle_count":  int(current.get("struggle_count") or 0),
        "mastery_score":   _clamp01(score - delta),
    }


def apply_struggle(current: Dict[str, Any]) -> Dict[str, Any]:
    """Return new counter/score values after one submission-level struggle."""
    score = float(current.get("mastery_score") or 0.0)
    delta = STRUGGLE_DELTA * score
    return {
        "attempts":        int(current.get("attempts") or 0),
        "correct_count":   int(current.get("correct_count") or 0),
        "incorrect_count": int(current.get("incorrect_count") or 0),
        "struggle_count":  int(current.get("struggle_count") or 0) + 1,
        "mastery_score":   _clamp01(score - delta),
    }


def _fetch_progress_row(student_id: str, concept_id: str) -> Optional[Dict[str, Any]]:
    resp = (_client().table("learner_progress")
            .select("*")
            .eq("student_id", student_id)
            .eq("concept_id", concept_id)
            .limit(1)
            .execute())
    rows = getattr(resp, "data", []) or []
    return rows[0] if rows else None


def _upsert_progress_row(student_id: str, concept_id: str, values: Dict[str, Any]):
    """
    Write the progress row. Supabase Python SDK supports `.upsert(..., on_conflict='student_id,concept_id')`.
    UNIQUE(student_id, concept_id) guarantee on the table keeps us safe.
    """
    payload = {
        "student_id": student_id,
        "concept_id": concept_id,
        **values,
    }
    try:
        resp = (_client().table("learner_progress")
                .upsert(payload, on_conflict="student_id,concept_id")
                .execute())
        rows = getattr(resp, "data", []) or []
        return rows[0] if rows else None
    except Exception:
        # Fallback: try insert, then update
        try:
            resp2 = _client().table("learner_progress").insert(payload).execute()
            rows2 = getattr(resp2, "data", []) or []
            return rows2[0] if rows2 else None
        except Exception:
            resp3 = (_client().table("learner_progress")
                     .update(values)
                     .eq("student_id", student_id)
                     .eq("concept_id", concept_id)
                     .execute())
            rows3 = getattr(resp3, "data", []) or []
            return rows3[0] if rows3 else None


def update_progress_for_quiz(
    student_id: str,
    concept_name: Optional[str],
    is_correct: bool,
) -> bool:
    """Apply one CORRECT or INCORRECT quiz result to learner_progress."""
    if not student_id or not concept_name:
        return False
    canon = find_canonical_concept(concept_name)
    if not canon:
        # Unknown concept: do NOT crash, do NOT invent a concept row. Skip safely.
        return False
    concept_id = canon["id"]

    def _fn():
        current = _fetch_progress_row(student_id, concept_id) or {
            "mastery_score": 0.0, "attempts": 0, "correct_count": 0,
            "incorrect_count": 0, "struggle_count": 0,
        }
        new_vals = apply_correct_answer(current) if is_correct else apply_incorrect_answer(current)
        new_vals["last_activity_at"] = "now()"
        return _upsert_progress_row(student_id, concept_id, new_vals) is not None

    return _safe("update_progress_for_quiz", False, _fn)


def update_progress_for_struggle(
    student_id: str,
    concept_name: Optional[str],
) -> bool:
    """Apply a gentle struggle penalty after a submission flagged a concept."""
    if not student_id or not concept_name:
        return False
    canon = find_canonical_concept(concept_name)
    if not canon:
        return False
    concept_id = canon["id"]

    def _fn():
        current = _fetch_progress_row(student_id, concept_id) or {
            "mastery_score": 0.0, "attempts": 0, "correct_count": 0,
            "incorrect_count": 0, "struggle_count": 0,
        }
        new_vals = apply_struggle(current)
        new_vals["last_activity_at"] = "now()"
        return _upsert_progress_row(student_id, concept_id, new_vals) is not None

    return _safe("update_progress_for_struggle", False, _fn)


# =============================================================================
# 7. Reads: return Supabase-backed progress/recommendations context for
#    authenticated learners, else None so the caller falls back to session.
# =============================================================================

def fetch_learner_overview(student_id: str) -> Optional[Dict[str, Any]]:
    """
    Return an overview dict shaped like the legacy session progress response
    so GET /api/progress can swap to DB for authenticated users with no
    frontend changes.

    Shape:
      {
        "struggles": { concept_name: count, ... },
        "errors": { error_name: count, ... },
        "concept_checks": { concept_name: {attempts, correct, incorrect}, ... },
        "recent_improvements": [ {concept, status, icon}, ... ],
        "mastery": [ {concept_id, concept_name, mastery_score, attempts, ...}, ... ],
      }
    """
    if not student_id:
        return None

    def _fn():
        client = _client()
        # Misconceptions → struggles
        mis = getattr(client.table("misconceptions")
            .select("concept_id, severity, title")
            .eq("student_id", student_id)
            .order("created_at", desc=True)
            .limit(200)
            .execute(), "data", []) or []
        struggles: Dict[str, int] = {}
        for m in mis:
            key = m.get("title") or "Unnamed Concept"
            # Prefer canonical concept name when concept_id join is possible (next call)
            struggles[key] = struggles.get(key, 0) + 1

        # Concept checks → per-concept stats and recent improvements
        ccs = getattr(client.table("concept_checks")
            .select("concept_name,concept_id,is_correct,created_at")
            .eq("student_id", student_id)
            .order("created_at", desc=True)
            .limit(300)
            .execute(), "data", []) or []
        concept_checks: Dict[str, Dict[str, int]] = {}
        recent_improvements: List[Dict[str, str]] = []
        for cc in ccs:
            name = cc.get("concept_name") or cc.get("concept_id") or "General Concept"
            stat = concept_checks.setdefault(name, {"attempts": 0, "correct": 0, "incorrect": 0})
            stat["attempts"] += 1
            if cc.get("is_correct"):
                stat["correct"] += 1
            else:
                stat["incorrect"] += 1
        # Improvements = recent correct answers (last 5)
        for cc in [c for c in ccs if c.get("is_correct")][:5]:
            name = cc.get("concept_name") or cc.get("concept_id") or "General Concept"
            recent_improvements.append({
                "concept": name,
                "status": "Passed Concept Check",
                "icon": "✓",
            })

        # Errors: synthesised from misconception severity title keywords?
        # Simpler: we don't have a direct errors table — leave as empty dict.
        errors: Dict[str, int] = {}

        # Mastery rows (top N most recently active or highest attempts)
        mastery_rows = getattr(client.table("learner_progress")
            .select("id,concept_id,mastery_score,attempts,correct_count,incorrect_count,struggle_count,last_activity_at")
            .eq("student_id", student_id)
            .order("last_activity_at", desc=True, nulls_first=False)
            .limit(50)
            .execute(), "data", []) or []
        # Map concept_id → canonical name when possible
        concept_map = {r["id"]: r for r in _load_concepts()}
        mastery_out = []
        for mr in mastery_rows:
            cid = mr.get("concept_id")
            canon = concept_map.get(cid) or {}
            mastery_out.append({
                "concept_id": cid,
                "concept_name": canon.get("name", cid) if canon else cid,
                "mastery_score": float(mr.get("mastery_score") or 0.0),
                "attempts": int(mr.get("attempts") or 0),
                "correct_count": int(mr.get("correct_count") or 0),
                "incorrect_count": int(mr.get("incorrect_count") or 0),
                "struggle_count": int(mr.get("struggle_count") or 0),
                "last_activity_at": mr.get("last_activity_at"),
            })
        # Overlay canonical names into struggles dict where possible too
        canon_lookup = {_slugify(r.get("name") or ""): r for r in concept_map.values()}
        canon_lookup.update({r.get("slug") or "": r for r in concept_map.values()})
        cleaned_struggles: Dict[str, int] = {}
        for raw, cnt in struggles.items():
            canon_match = find_canonical_concept(raw)
            key = canon_match["name"] if canon_match else raw
            cleaned_struggles[key] = cleaned_struggles.get(key, 0) + cnt

        return {
            "struggles": cleaned_struggles,
            "errors": errors,
            "concept_checks": concept_checks,
            "recent_improvements": recent_improvements,
            "mastery": mastery_out,
        }

    return _safe("fetch_learner_overview", None, _fn)


def fetch_learner_submissions(student_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve past code submissions belonging ONLY to the authenticated student_id.
    Ordered by created_at descending.
    """
    if not student_id:
        return []

    def _fn():
        client = _client()
        if not client:
            return []

        # 1. Fetch submissions
        resp = (
            client.table("submissions")
            .select("id,code,language,persona,analysis_summary,created_at")
            .eq("student_id", student_id)
            .order("created_at", desc=True)
            .limit(max(1, min(limit, 100)))
            .execute()
        )
        subs = getattr(resp, "data", []) or []
        if not subs:
            return []

        sub_ids = [s["id"] for s in subs]

        # 2. Fetch linked misconceptions for these submissions
        mis_resp = (
            client.table("misconceptions")
            .select("id,submission_id,title,explanation,severity,concept_id")
            .eq("student_id", student_id)
            .in_("submission_id", sub_ids)
            .execute()
        )
        mis_list = getattr(mis_resp, "data", []) or []

        # Group misconceptions by submission_id
        mis_by_sub: Dict[str, List[Dict[str, Any]]] = {}
        for m in mis_list:
            s_id = m.get("submission_id")
            if s_id:
                mis_by_sub.setdefault(s_id, []).append(m)

        # 3. Fetch linked concept checks for these submissions
        cc_resp = (
            client.table("concept_checks")
            .select("id,submission_id,concept_name,question_text,selected_index,correct_index,is_correct")
            .eq("student_id", student_id)
            .in_("submission_id", sub_ids)
            .execute()
        )
        cc_list = getattr(cc_resp, "data", []) or []

        cc_by_sub: Dict[str, List[Dict[str, Any]]] = {}
        for cc in cc_list:
            s_id = cc.get("submission_id")
            if s_id:
                cc_by_sub.setdefault(s_id, []).append(cc)

        # 4. Map output shape
        result = []
        for s in subs:
            s_id = s["id"]
            code_str = s.get("code") or ""
            code_preview = code_str[:160] + ("…" if len(code_str) > 160 else "")

            sub_mis = mis_by_sub.get(s_id, [])
            sub_ccs = cc_by_sub.get(s_id, [])

            concepts = []
            for m in sub_mis:
                if m.get("title") and m["title"] not in concepts:
                    concepts.append(m["title"])
            for cc in sub_ccs:
                cname = cc.get("concept_name")
                if cname and cname not in concepts:
                    concepts.append(cname)

            mis_summary = sub_mis[0].get("title") if sub_mis else None

            result.append({
                "id": s_id,
                "code": code_str,
                "code_preview": code_preview,
                "language": s.get("language") or "python",
                "persona": s.get("persona") or "beginner",
                "analysis_summary": s.get("analysis_summary"),
                "concepts": concepts,
                "misconception_summary": mis_summary,
                "misconceptions": sub_mis,
                "concept_checks": sub_ccs,
                "has_quiz": len(sub_ccs) > 0,
                "created_at": s.get("created_at"),
            })

        return result

    return _safe("fetch_learner_submissions", [], _fn)


def fetch_submission_detail(student_id: str, submission_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve full submission details ONLY if it belongs to student_id.
    Enforces strict ownership check.
    """
    if not student_id or not submission_id:
        return None

    def _fn():
        client = _client()
        if not client:
            return None

        resp = (
            client.table("submissions")
            .select("id,student_id,code,language,persona,analysis_summary,created_at")
            .eq("id", submission_id)
            .limit(1)
            .execute()
        )
        rows = getattr(resp, "data", []) or []
        if not rows:
            return None

        sub = rows[0]
        # Strict ownership verification
        if str(sub.get("student_id")) != str(student_id):
            return None

        # Fetch linked misconceptions & concept checks
        mis_resp = (
            client.table("misconceptions")
            .select("id,title,explanation,severity,created_at")
            .eq("submission_id", submission_id)
            .execute()
        )
        mis_list = getattr(mis_resp, "data", []) or []

        cc_resp = (
            client.table("concept_checks")
            .select("id,concept_name,question_text,selected_index,correct_index,is_correct,created_at")
            .eq("submission_id", submission_id)
            .execute()
        )
        cc_list = getattr(cc_resp, "data", []) or []

        concepts = list(set([
            m.get("title") for m in mis_list if m.get("title")
        ] + [
            c.get("concept_name") for c in cc_list if c.get("concept_name")
        ]))

        code_str = sub.get("code") or ""
        return {
            "id": sub["id"],
            "code": code_str,
            "code_preview": code_str[:160] + ("…" if len(code_str) > 160 else ""),
            "language": sub.get("language") or "python",
            "persona": sub.get("persona") or "beginner",
            "analysis_summary": sub.get("analysis_summary"),
            "concepts": concepts,
            "misconceptions": mis_list,
            "concept_checks": cc_list,
            "has_quiz": len(cc_list) > 0,
            "created_at": sub.get("created_at"),
        }

    return _safe("fetch_submission_detail", None, _fn)

