"""
ExplainX – Multi-Perspective Code Explanation Engine
Flask Backend

Phase 7B — Authenticated via Supabase Bearer token layer:
  - @require_auth   → identity MUST be verified (learner-scoped routes)
  - @optional_auth    → identity is used when available, else guest
  - @get_current_user_id()  → ONLY trusted identity source (never trust payload IDs)

Phase 7E — Supabase Persistence (added around the working system):
  - Persistence is BEST-EFFORT. If Supabase is down/misconfigured, the tutor
    experience continues exactly as Phase 1–6 via Flask session.
  - explainer, parser, resources, Gemini responses — 100% untouched.
  - We only OBSERVE return values and optionally persist a subset.
"""

import os, uuid
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path) if os.path.exists(env_path) else load_dotenv()

from flask import Flask, render_template, request, jsonify, session
from explanation_engine.explainer import ExplainXEngine
from explanation_engine.parser import CodeParser
from explanation_engine.resources import build_recommendation_payload
from explanation_engine.resources import build_rule_based_guidance  # Phase 8 fallback
from explanation_engine.resources import sanitize_resource_list   # Phase 8 URL safety gate
from explanation_engine.auth import (
    require_auth,
    optional_auth,
    get_current_user_id,
)
from explanation_engine.auth import _build_user_info  # noqa: F401  (keep visible)
from explanation_engine import persistence as _persist

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "explainx-dev-secret-2024")

engine = ExplainXEngine()
parser = CodeParser()


def _ensure_session_defaults():
    if "user_id" not in session:
        session["user_id"]             = str(uuid.uuid4())
        session["interaction_history"] = []
        session["comprehension_score"] = 50
        session["last_mode"]           = "beginner"
        session["chat_history"]        = []
    if "struggles" not in session:
        session["struggles"] = {}
    if "errors" not in session:
        session["errors"] = {}
    if "concept_checks" not in session:
        session["concept_checks"] = {}
    if "recent_improvements" not in session:
        session["recent_improvements"] = []

def _detect_error_type(code, result):
    combined = (code + " " + str(result)).lower()
    if "indexerror" in combined or "out of range" in combined or "off-by-one" in combined or "index out of bounds" in combined:
        return "IndexError"
    if "syntaxerror" in combined or "invalid syntax" in combined or "unexpected token" in combined:
        return "SyntaxError"
    if "typeerror" in combined or "unsupported operand" in combined:
        return "TypeError"
    if "keyerror" in combined:
        return "KeyError"
    return None

def _build_struggles_summary():
    struggles = session.get("struggles", {})
    errors = session.get("errors", {})
    parts = []
    for concept, count in list(struggles.items())[:3]:
        parts.append(f"encountered {concept} issues {count} times")
    for err, count in list(errors.items())[:3]:
        parts.append(f"encountered {err} {count} times")
    if not parts:
        return None
    return "Learner history: " + ", ".join(parts)


@app.route("/")
def index():
    """Health / status endpoint for the LineByLine API.
    The user-facing UI is served by the React + Vite frontend separately."""
    return jsonify({
        "status": "ok",
        "message": "LineByLine API is running",
        "api_version": "1.0",
    })


# ======================================================================
# PUBLIC (publicroutes: identity not learner-scoped; still identity
# ======================================================================


@app.route("/api/me", methods=["GET"])
@require_auth
def me():
    """Return the currently-authenticated user identity (verified, trusted)."""
    from flask import g
    user = getattr(g, "current_user", None)
    return jsonify({
        "id": user["id"],
        "email": user.get("email"),
        "display_name": user.get("display_name"),
    })


@app.route("/api/explain", methods=["POST"])
@optional_auth
def explain():
    _ensure_session_defaults()
    data       = request.get_json() or {}
    code       = data.get("code", "").strip()
    mode       = data.get("mode", "beginner")
    language   = data.get("language", "python")
    line_focus = data.get("line_focus", None)

    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        structure = parser.analyze(code, language)

        if mode == "adaptive":
            score = session.get("comprehension_score", 50)
            mode  = engine.resolve_adaptive_mode(score)
            resolved_adaptive = True
        else:
            resolved_adaptive = False

        struggles_summary = _build_struggles_summary()

        result = engine.explain(
            code=code, mode=mode, language=language,
            structure=structure, line_focus=line_focus,
            comprehension_score=session.get("comprehension_score", 50),
            struggles_summary=struggles_summary,
        )

        # Track submission-level struggles
        misconception = result.get("possible_misconception")
        if misconception and isinstance(misconception, dict):
            c_name = misconception.get("concept_name") or misconception.get("title")
            if c_name:
                struggles = dict(session.get("struggles", {}))
                struggles[c_name] = struggles.get(c_name, 0) + 1
                session["struggles"] = struggles

        # Track submission-level concrete errors
        err_type = _detect_error_type(code, result)
        if err_type:
            errors = dict(session.get("errors", {}))
            errors[err_type] = errors.get(err_type, 0) + 1
            session["errors"] = errors

        history = session.get("interaction_history", [])
        history.append({"mode": mode, "code_snippet": code[:120]})
        session["interaction_history"] = history[-10:]
        session["last_mode"]           = mode
        session["chat_history"]        = []
        session["last_code"]           = code
        session["last_language"]       = language
        session["last_mode_used"]      = mode

        # ── Phase 7E: BEST-EFFORT persistence wrap-around ──────────────────
        # Identity comes ONLY from verified Supabase JWT (never from JSON).
        user_id = get_current_user_id()
        if user_id:
            try:
                from flask import g as _g
                _u = getattr(_g, "current_user", None) or {}
                display_name = _u.get("display_name") if isinstance(_u, dict) else None
                _persist.ensure_student(user_id, display_name=display_name)
                # Build a compact analysis summary from the result (cap to avoid storing huge payloads)
                _summary = None
                if isinstance(result.get("complexity"), dict):
                    _summary_parts = []
                    for k, v in result["complexity"].items():
                        _summary_parts.append(f"{k}: {v}")
                    if _summary_parts:
                        _summary = "; ".join(_summary_parts)
                sub_id = _persist.persist_submission(
                    student_id=user_id, code=code, language=language,
                    persona=mode, analysis_summary=_summary,
                )
                # Misconception persistence (learner-specific dynamic — NO catalog)
                if misconception and isinstance(misconception, dict):
                    mc_title = (
                        misconception.get("title")
                        or misconception.get("concept_name")
                        or "Possible Misconception"
                    )
                    mc_expl = misconception.get("description") or misconception.get("explanation")
                    mc_cname = misconception.get("concept_name") or misconception.get("concept")
                    _persist.persist_misconception(
                        student_id=user_id, submission_id=sub_id,
                        title=mc_title, explanation=mc_expl,
                        concept_name=mc_cname, severity="medium",
                    )
                    # Gentle struggle mastery penalty (once per misconception concept)
                    if mc_cname:
                        _persist.update_progress_for_struggle(user_id, mc_cname)
                # Also count detected error type as a struggle on the concept
                if err_type:
                    _canon_err_concept = None
                    err_to_concept = {
                        "IndexError": "List Indexing",
                        "SyntaxError": "Operators & Expressions",
                        "TypeError": "Data Types",
                        "KeyError": "Dictionaries",
                    }
                    _canon_err_concept = err_to_concept.get(err_type)
                    if _canon_err_concept:
                        _persist.update_progress_for_struggle(user_id, _canon_err_concept)
            except Exception as _p_exc:
                # Persistence is BEST-EFFORT. NEVER break the tutor response.
                print(f"[app.py][persistence] best-effort save skipped: {_p_exc!r}")
        # ── end persistence block; original response unchanged ─────────────
        return jsonify(result)

    except ConnectionError as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": "Gemini API connection failed. " + str(e)}), 502
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500




@app.route("/api/teach", methods=["POST"])
@optional_auth
def teach():
    data          = request.get_json() or {}
    code          = data.get("code", session.get("last_code", "")).strip()
    misconception = data.get("misconception", "")
    concept       = data.get("concept", "")
    mode          = data.get("mode", session.get("last_mode", "academic"))
    language      = data.get("language", session.get("last_language", "python"))

    try:
        result = engine.teach_concept(
            code=code,
            misconception=misconception,
            concept=concept,
            mode=mode,
            language=language
        )
        return jsonify(result)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/concept-check", methods=["POST"])
@optional_auth
def concept_check():
    data     = request.get_json() or {}
    code     = data.get("code", session.get("last_code", "")).strip()
    concept  = data.get("concept", "")
    mode     = data.get("mode", session.get("last_mode", "academic"))
    language = data.get("language", session.get("last_language", "python"))

    try:
        result = engine.generate_concept_check(
            code=code,
            concept=concept,
            mode=mode,
            language=language
        )
        return jsonify(result)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ======================================================================
# LEARNER-SCOPED ROUTES: MUST be authenticated
# ======================================================================


@app.route("/api/quiz-result", methods=["POST"])
@require_auth
def quiz_result():
    _ensure_session_defaults()
    data       = request.get_json() or {}
    concept    = data.get("concept", "General Concept").strip()
    is_correct = bool(data.get("is_correct", False))
    quiz_ctx   = data.get("quiz_context") or {}

    # ── Phase 7E: Persist quiz attempt + mastery update ───────────────────
    user_id = get_current_user_id()  # NEVER from payload, ALWAYS from JWT
    if user_id:
        try:
            _persist.ensure_student(user_id)
            # Persist the full concept_check row (MCQ attempt)
            if isinstance(quiz_ctx, dict):
                _persist.persist_concept_check(
                    student_id=user_id,
                    submission_id=(session.get("last_submission_id") if False else None),
                    concept_name=concept,
                    question_text=quiz_ctx.get("question"),
                    selected_index=(quiz_ctx.get("selected_index")
                                    if quiz_ctx.get("selected_index") is not None
                                    else None),
                    correct_index=(quiz_ctx.get("correct_index")
                                   if quiz_ctx.get("correct_index") is not None
                                   else None),
                    is_correct=is_correct,
                )
            else:
                _persist.persist_concept_check(
                    student_id=user_id, submission_id=None, concept_name=concept,
                    question_text=None, selected_index=None, correct_index=None,
                    is_correct=is_correct,
                )
            # Update learner_progress mastery (deterministic formula)
            _persist.update_progress_for_quiz(user_id, concept, is_correct)
        except Exception as _p_exc:
            # BEST-EFFORT. Never break the response.
            print(f"[app.py][quiz-result persistence] skipped: {_p_exc!r}")

    # Original session-tracking (unchanged, still works for guests + display)
    checks = dict(session.get("concept_checks", {}))
    c_stat = checks.get(concept, {"attempts": 0, "correct": 0, "incorrect": 0})
    c_stat["attempts"] += 1
    if is_correct:
        c_stat["correct"] += 1
    else:
        c_stat["incorrect"] += 1
    checks[concept] = c_stat
    session["concept_checks"] = checks

    # Record recent improvement if correct answer achieved
    if is_correct:
        improvements = list(session.get("recent_improvements", []))
        improvements.append({
            "concept": concept,
            "status": "Passed Concept Check",
            "icon": "✓"
        })
        session["recent_improvements"] = improvements[-5:]

    return jsonify({"status": "ok", "stats": c_stat})


@app.route("/api/progress", methods=["GET"])
@require_auth
def get_progress():
    _ensure_session_defaults()
    # ── Phase 7E: Authenticated users get DB-backed overview. ────────────
    # Supabase is BEST-EFFORT. If unavailable, fall back to session (legacy behavior).
    # Response shape is IDENTICAL to legacy session shape so Progress.jsx renders unchanged.
    user_id = get_current_user_id()
    db_overview = None
    if user_id:
        db_overview = _persist.fetch_learner_overview(user_id)

    if db_overview:
        # Merge DB data with any fresh session-only data (quiz results this request)
        merged = dict(db_overview)
        # Session has latest concept_checks — merge them on top for freshness
        sess_cc = session.get("concept_checks") or {}
        if sess_cc:
            final_cc = dict(merged.get("concept_checks") or {})
            for name, st in sess_cc.items():
                cur = final_cc.get(name, {"attempts": 0, "correct": 0, "incorrect": 0})
                for k in ("attempts", "correct", "incorrect"):
                    cur[k] = max(cur.get(k, 0), st.get(k, 0))
                final_cc[name] = cur
            merged["concept_checks"] = final_cc
        # Session struggles + recent improvements are already live; prefer if fresher
        if not merged.get("struggles"):
            merged["struggles"] = session.get("struggles", {})
        if not merged.get("recent_improvements"):
            merged["recent_improvements"] = session.get("recent_improvements", [])
        return jsonify(merged)

    # Legacy fallback (session-backed, same shape, frontend unchanged)
    return jsonify({
        "struggles": session.get("struggles", {}),
        "errors": session.get("errors", {}),
        "concept_checks": session.get("concept_checks", {}),
        "recent_improvements": session.get("recent_improvements", [])
    })


@app.route("/api/submissions", methods=["GET"])
@require_auth
def get_submissions():
    """
    Return the authenticated learner's submission history.
    Identity comes ONLY from verified Supabase JWT (never trusted from input).
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    limit = request.args.get("limit", default=50, type=int)
    submissions = _persist.fetch_learner_submissions(user_id, limit=limit)
    return jsonify({"submissions": submissions})


@app.route("/api/submissions/<submission_id>", methods=["GET"])
@require_auth
def get_submission_detail(submission_id):
    """
    Return full submission details ONLY if owned by the authenticated learner.
    Returns 404 if submission doesn't exist OR belongs to another learner.
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    detail = _persist.fetch_submission_detail(user_id, submission_id)
    if not detail:
        return jsonify({"error": "Submission not found"}), 404

    return jsonify(detail)



@app.route("/api/recommendations", methods=["GET"])
@require_auth
def get_recommendations():
    """
    Phase 5 — Verified Learning Recommendations.

    ZERO AI-HALLUCINATED URL GUARANTEE:
    - All URLs come from a hand-curated library in explanation_engine/resources.py
    - Gemini (or the explainer) only determines the *topic & rationale* via session.
    - URLs are resolved from trusted domains (docs.python.org, MDN, GeeksforGeeks,
      freeCodeCamp, etc.) — never fabricated.
    - As a last resort, safe search links on trusted domains are returned.

    Phase 7E — For authenticated users with DB-backed learner_progress, we pass
    the LOWEST-mastery canonical concept as the teaching_concept. This lets the
    existing Phase 5 resources library surface resources tailored to their
    actual weakest skills (no prerequisite_edges table, no resources table).

    Phase 8 — Dynamic prerequisite chain + next-step guidance:
    - GEMINI-FIRST:   engine.generate_prerequisite_chain() infers the prerequisite
                       chain dynamically (no prerequisite_edges table, ever).
    - RULE-FALLBACK:   build_rule_based_guidance() in resources.py produces the
                       SAME SHAPE deterministically when Gemini is unavailable.
    - ADDITIVE SHAPE:  prerequisite_chain, next_steps, recommended_action,
                       guidance_summary are added on top of the existing Phase 5
                       response. No existing fields are removed or modified.
    - BEST-EFFORT:     any exception → silently skip guidance, return the
                       original Phase 5/7E response (no crash).
    """
    _ensure_session_defaults()

    # ── Phase 7E: pick teaching concept from DB mastery if available. ────
    teaching_concept = None
    user_id = get_current_user_id()
    overview = None
    mastery = []
    if user_id:
        overview = _persist.fetch_learner_overview(user_id)
        if overview and overview.get("mastery"):
            mastery = overview["mastery"]
            # Weakest concept = lowest mastery_score, tie-break by more attempts/struggles
            weakest = sorted(
                mastery,
                key=lambda m: (float(m.get("mastery_score") or 0.0),
                               -(int(m.get("struggle_count") or 0) + int(m.get("attempts") or 0))),
            )
            if weakest:
                teaching_concept = weakest[0].get("concept_name") or weakest[0].get("concept_id")

    # Legacy fallback if no DB data or we're session-only
    if not teaching_concept:
        last_concept_checks = session.get("concept_checks", {}) or {}
        if last_concept_checks:
            sorted_concepts = sorted(
                last_concept_checks.items(),
                key=lambda kv: -(kv[1].get("incorrect", 0) * 2 + kv[1].get("attempts", 0))
            )
            teaching_concept = sorted_concepts[0][0]

    sess_struggles = session.get("struggles", {})
    sess_errors = session.get("errors", {})

    # Session struggles/errors still inform the existing resource-library selection
    payload = build_recommendation_payload(
        struggles=sess_struggles,
        errors=sess_errors,
        teaching_concept=teaching_concept,
        language=session.get("last_language", "python"),
    )

    # ── Phase 8: Dynamic prerequisite guidance (BEST-EFFORT, additive) ──
    # Strategy: Gemini first (rich, tailored), rule-based fallback (deterministic).
    # On ANY failure → skip guidance entirely (original payload shape preserved).
    if teaching_concept:
        try:
            language = session.get("last_language", "python")
            guidance = engine.generate_prerequisite_chain(
                target_concept=teaching_concept,
                mastery_snapshot=mastery,
                struggles=sess_struggles,
                errors=sess_errors,
                language=language,
            )
            if not guidance:
                guidance = build_rule_based_guidance(
                    target_concept=teaching_concept,
                    mastery_snapshot=mastery,
                    struggles=sess_struggles,
                    errors=sess_errors,
                    language=language,
                )
            if guidance and isinstance(guidance, dict):
                # Merge ADDITIVELY on top. NEVER overwrite existing keys.
                for k in ("prerequisite_chain", "next_steps",
                          "recommended_action", "guidance_summary", "source"):
                    if (k in guidance) and (k not in payload):
                        payload[k] = guidance[k]
        except Exception as _g_exc:
            # Best-effort — never break the recommendations response.
            print(f"[app.py][recommendations guidance] best-effort skipped: {_g_exc!r}")

    # ── Phase 8 Addendum: ZERO HALLUCINATED URL ENFORCEMENT ─────────────
    # Belt-and-braces URL sanitization pass. Resources are already known-safe
    # (they come from CURATED_LIBRARY). This pass guarantees the response
    # never contains an untrusted/invalid/placeholder URL — any bad entry
    # (or future integration bug that injects a Gemini URL) is discarded
    # and replaced with find_resources() output on the same concept.
    try:
        primary = payload.get("primary_concept") or teaching_concept or "Programming Fundamentals"
        lang = session.get("last_language", "python")
        payload["resources"] = sanitize_resource_list(
            resources=payload.get("resources", []),
            fallback_concept=primary,
            language=lang,
            max_resources=6,
        )
    except Exception as _s_exc:
        print(f"[app.py][recommendations sanitizer] best-effort fallback: {_s_exc!r}")
        # Absolute safety fallback — rebuild resources from find_resources
        # only, drop any list that failed sanitization.
        try:
            from explanation_engine.resources import find_resources
            primary = payload.get("primary_concept") or teaching_concept or "Programming Fundamentals"
            lang = session.get("last_language", "python")
            fresh = find_resources(primary, max_resources=6, language=lang)
            # Final sanity filter — should always pass.
            payload["resources"] = [r for r in fresh if (
                r.get("url")
                and (r["url"].startswith("http://") or r["url"].startswith("https://"))
            )][:6]
        except Exception:
            payload["resources"] = []

    return jsonify(payload)





@app.route("/api/followup", methods=["POST"])
@optional_auth
def followup():
    """Handle follow-up questions and re-explanation requests."""
    data                = request.get_json()
    message             = data.get("message", "").strip()
    action              = data.get("action", None)
    code                = data.get("code", session.get("last_code", ""))
    language            = data.get("language", session.get("last_language", "python"))
    current_explanation = data.get("current_explanation", "")

    if not message and not action:
        return jsonify({"error": "No message provided"}), 400

    try:
        chat_history = session.get("chat_history", [])

        result = engine.followup(
            code=code,
            language=language,
            current_explanation=current_explanation,
            message=message,
            action=action,
            chat_history=chat_history,
            comprehension_score=session.get("comprehension_score", 50),
        )

        chat_history.append({"role": "user",      "content": message or action})
        chat_history.append({"role": "assistant",  "content": result["reply"]})
        session["chat_history"] = chat_history[-20:]

        # Lower score slightly when user signals confusion
        if action in ("simpler", "analogy", "eli5"):
            session["comprehension_score"] = max(0, session.get("comprehension_score", 50) - 5)

        return jsonify(result)

    except ConnectionError as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": "Gemini API connection failed. " + str(e)}), 502
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/explain-blocks", methods=["POST"])
@optional_auth
def explain_blocks():
    data     = request.get_json()
    code     = data.get("code", "").strip()
    mode     = data.get("mode", "beginner")
    language = data.get("language", "python")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        if mode == "adaptive":
            score = session.get("comprehension_score", 50)
            mode  = engine.resolve_adaptive_mode(score)

        blocks  = parser.split_into_blocks(code, language)
        results = engine.explain_blocks(blocks, mode, language)
        return jsonify(results)

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback", methods=["POST"])
@optional_auth
def feedback():
    data       = request.get_json()
    correct    = data.get("correct", False)
    difficulty = data.get("difficulty", "medium")

    score     = session.get("comprehension_score", 50)
    delta_map = {"easy": 3, "medium": 7, "hard": 12}
    delta     = delta_map.get(difficulty, 7)
    score     = min(100, score + delta) if correct else max(0, score - delta)

    session["comprehension_score"] = score
    return jsonify({"score": score})


@app.route("/api/line-explain", methods=["POST"])
@optional_auth
def line_explain():
    data     = request.get_json()
    code     = data.get("code", "")
    line_num = data.get("line", 1)
    mode     = data.get("mode", session.get("last_mode", "beginner"))
    language = data.get("language", "python")
    result   = engine.explain_line(code=code, line_num=line_num, mode=mode, language=language)
    return jsonify(result)


@app.route("/api/session", methods=["GET"])
@optional_auth
def get_session():
    return jsonify({"score": session.get("comprehension_score", 50)})


@app.route("/api/reset", methods=["POST"])
@require_auth
def reset_session():
    session["comprehension_score"] = 50
    session["interaction_history"] = []
    session["last_mode"]           = "beginner"
    session["chat_history"]        = []
    return jsonify({"status": "ok"})


def _score_message(score):
    if score >= 80: return "🚀 Excellent grasp! Pushing to advanced explanations."
    if score >= 60: return "👍 Good progress! Balancing detail and clarity."
    if score >= 40: return "📖 Building foundations. Keeping explanations clear."
    return "🌱 Starting fresh. Using simple, friendly language."


if __name__ == "__main__":
    app.run(debug=True, port=5000)
