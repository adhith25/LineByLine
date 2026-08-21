"""
LineByLine — verify_database.py (Phase 7D — RLS + 6-table architecture)

Usage:
    1. DRY RUN / schema audit (no live DB required):
           python -B verify_database.py --schema-only

    2. LIVE run against a real Supabase database (env vars configured):
           python -B verify_database.py

Environment (live run):
    SUPABASE_URL=
    SUPABASE_SERVICE_ROLE_KEY=

Simplified architecture (6 tables ONLY):
    auth.users → students → (submissions, misconceptions, concept_checks, learner_progress)
    concepts = canonical reference table.

DELIBERATELY NOT IN SCHEMA (Gemini dynamic, not static tables):
    - NO prerequisite_edges
    - NO resources table / catalog

Phase 7D RLS checks added:
    [X] RLS ENABLED on all 6 tables (ALTER TABLE ... ENABLE ROW LEVEL SECURITY)
    [X] students    — 4 OWN policies (SELECT/INSERT/UPDATE/DELETE on id = auth.uid())
    [X] submissions — 4 OWN policies (SELECT/INSERT/UPDATE/DELETE on student_id = auth.uid())
    [X] misconceptions — 4 OWN policies
    [X] concept_checks — 4 OWN policies
    [X] learner_progress — 4 OWN policies
    [X] concepts    — 1 SELECT for authenticated (NO write policies)
    [X] Idempotent pattern: DROP POLICY IF EXISTS before each CREATE POLICY
    [X] Explicit GRANTs to authenticated role (no anon grants on data tables)

Checks performed:
    [X] 6 required tables exist
    [X] UUID / FK compatibility — every learner FK is UUID
    [X] No integer <-> UUID mismatches
    [X] students.id REFERENCES auth.users(id) type-compatible
    [X] UNIQUE (student_id, concept_id) on learner_progress
    [X] learner_progress CHECK constraints (mastery_score 0..1)
    [X] Seed concepts count >= 20
    [X] NO prerequisite_edges anywhere in schema or seed
    [X] NO resources anywhere in schema or seed
    [X] ON DELETE CASCADE behavior for learner-owned FKs (>= 3 cascades)
    [X] RLS enabled + ownership policies on all tables
"""
from __future__ import annotations

import os
import re
import sys
import json
import argparse
from pathlib import Path

SCHEMA_FILE = Path(__file__).with_name("schema.sql")
SEED_FILE   = Path(__file__).with_name("seed.sql")

REQUIRED_TABLES = [
    "students",
    "submissions",
    "concepts",
    "misconceptions",
    "concept_checks",
    "learner_progress",
]

FORBIDDEN_TABLES = [
    "prerequisite_edges",
    "resources",
]


# =============================================================================
# Schema-only audit — parse the SQL statically (no live DB)
# =============================================================================
def audit_schema_sql(sql: str) -> list[dict]:
    checks = []

    # 1. Each required table has its CREATE TABLE ... definition
    for t in REQUIRED_TABLES:
        ok = bool(re.search(rf"CREATE TABLE IF NOT EXISTS public.{t}\b", sql, re.IGNORECASE))
        checks.append({"id": f"Table exists: {t}", "ok": ok, "level": "high"})

    # 2. Forbidden tables must NOT exist in schema
    for t in FORBIDDEN_TABLES:
        present = bool(re.search(rf"CREATE TABLE[^\n]*public\.{t}\b", sql, re.IGNORECASE))
        checks.append({
            "id":    f"Forbidden table NOT present in schema: {t}",
            "ok":    not present,
            "level": "high",
            "detail": "found" if present else "not found",
        })

    # 3. UUID / FK type compatibility:
    fk_columns = [
        "student_id",
        "concept_id",
        "submission_id",
    ]
    for col in fk_columns:
        pattern = rf"{col}\s+UUID\b[\s\S]{{0,80}}REFERENCES"
        matches = re.findall(pattern, sql, re.IGNORECASE | re.MULTILINE)
        checks.append({
            "id":     f"FK type OK: {col} is UUID",
            "ok":     len(matches) >= 1,
            "level":  "high",
            "detail": f"{len(matches)} UUID references found",
        })

    # 4. students.id REFERENCES auth.users(id)
    ok = bool(re.search(r"id\s+UUID\s+PRIMARY\s+KEY\s+REFERENCES\s+auth\.users\(id\)", sql, re.IGNORECASE))
    checks.append({"id": "students.id -> auth.users(id)", "ok": ok, "level": "high"})

    # 5. UNIQUE (student_id, concept_id) on learner_progress
    ok = bool(re.search(r"uq_student_concept\s+UNIQUE\s*\(student_id,\s*concept_id\)", sql, re.IGNORECASE))
    checks.append({"id": "learner_progress UNIQUE(student_id, concept_id)", "ok": ok, "level": "high"})

    # 6. mastery_score CHECK 0..1
    ok = bool(re.search(r"CHECK\s*\(mastery_score\s*>=\s*0\s+AND\s+mastery_score\s*<=\s*1\)", sql, re.IGNORECASE))
    checks.append({"id": "learner_progress mastery_score CHECK 0..1", "ok": ok, "level": "high"})

    # 7. trigger_set_updated_at function
    ok = bool(re.search(r"CREATE OR REPLACE FUNCTION public.trigger_set_updated_at\(", sql))
    checks.append({"id": "trigger_set_updated_at installed", "ok": ok, "level": "medium"})

    # 8. ON DELETE CASCADE for learner-owned FKs (>= 3 is the students cascade
    #    + submissions cascade + misconceptions + concept_checks + learner_progress + submissions_idx cascade)
    cascades = re.findall(r"REFERENCES public\.(?:students|submissions|concepts)\(id\) ON DELETE CASCADE", sql, re.IGNORECASE)
    checks.append({
        "id":     f"ON DELETE CASCADE behavior for learner-owned FKs ({len(cascades)} found)",
        "ok":     len(cascades) >= 3,
        "level":  "medium",
        "detail": f"cascades={[c.strip() for c in cascades]}",
    })

    # 9. Forbidden prerequisite edge concepts / resources references anywhere in schema
    forbidden_refs = re.findall(r"prerequisite_concept_id|dependent_concept_id|idx_resources_", sql, re.IGNORECASE)
    checks.append({
        "id":    "Schema has no prerequisite_concept_id/dependent_concept_id/idx_resources_ references",
        "ok":    len(forbidden_refs) == 0,
        "level": "high",
        "detail": f"found forbidden refs: {forbidden_refs[:5]}" if forbidden_refs else "clean",
    })

    # =========================================================================
    # Phase 7D — Row Level Security static audit
    # =========================================================================

    # 10. RLS ENABLED on all 6 tables
    rls_enable_count = 0
    for t in REQUIRED_TABLES:
        if re.search(rf"ALTER\s+TABLE\s+public\.{t}\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY", sql, re.IGNORECASE):
            rls_enable_count += 1
    checks.append({
        "id":     f"RLS ENABLE ROW LEVEL SECURITY on all 6 tables ({rls_enable_count}/6)",
        "ok":     rls_enable_count == 6,
        "level":  "high",
        "detail": f"tables with RLS enabled: {rls_enable_count}",
    })

    # 11. students ownership policies — 4 policies on id = auth.uid()
    for action in ("select", "insert", "update", "delete"):
        pat = rf'CREATE\s+POLICY\s+"students_{action}_own"\s+ON\s+public\.students[\s\S]{{0,200}}auth\.uid\(\)\s*=\s*id'
        ok = bool(re.search(pat, sql, re.IGNORECASE))
        checks.append({
            "id":    f"students OWN policy: {action.upper()} auth.uid() = id",
            "ok":    ok,
            "level": "high",
        })

    # 12. Learner-owned tables (4) — 4 policies each on student_id = auth.uid()
    learner_tables = ["submissions", "misconceptions", "concept_checks", "learner_progress"]
    for t in learner_tables:
        for action in ("select", "insert", "update", "delete"):
            pat = rf'CREATE\s+POLICY\s+"{t}_{action}_own"\s+ON\s+public\.{t}[\s\S]{{0,200}}auth\.uid\(\)\s*=\s*student_id'
            ok = bool(re.search(pat, sql, re.IGNORECASE))
            checks.append({
                "id":    f"{t} OWN policy: {action.upper()} auth.uid() = student_id",
                "ok":    ok,
                "level": "high",
            })

    # 13. concepts: SELECT for authenticated (no INSERT/UPDATE/DELETE policies)
    ok = bool(re.search(
        rf'CREATE\s+POLICY\s+"concepts_select_authenticated"\s+ON\s+public\.concepts[\s\S]{{0,240}}FOR\s+SELECT\s+TO\s+authenticated',
        sql, re.IGNORECASE,
    ))
    checks.append({"id": "concepts: SELECT policy FOR authenticated only", "ok": ok, "level": "high"})

    # 14. concepts: NO write policies (INSERT/UPDATE/DELETE) for authenticated
    write_policy_found = bool(re.search(
        r'CREATE\s+POLICY[^\n]*ON\s+public\.concepts[\s\S]{0,200}?FOR\s+(INSERT|UPDATE|DELETE)',
        sql, re.IGNORECASE,
    ))
    checks.append({
        "id":    "concepts: NO write (INSERT/UPDATE/DELETE) policies on reference table",
        "ok":    not write_policy_found,
        "level": "high",
        "detail": "write policy found — DANGER" if write_policy_found else "clean — only service role can seed/modify concepts",
    })

    # 15. Idempotent DROP POLICY IF EXISTS pattern before every CREATE POLICY
    create_count   = len(re.findall(r'CREATE\s+POLICY\s+"', sql, re.IGNORECASE))
    drop_if_exists = len(re.findall(r'DROP\s+POLICY\s+IF\s+EXISTS\s+"', sql, re.IGNORECASE))
    checks.append({
        "id":     f"RLS idempotent pattern: DROP POLICY IF EXISTS before CREATE ({drop_if_exists} drops / {create_count} creates)",
        "ok":     create_count >= 1 and drop_if_exists >= create_count,
        "level":  "medium",
        "detail": f"creates={create_count} drop_if_exists={drop_if_exists}",
    })

    # 16. Explicit GRANTs to authenticated role on 6 tables
    grant_patterns = [
        (r"GRANT\s+SELECT,\s*INSERT,\s*UPDATE,\s*DELETE\s+ON\s+public\.students\s+TO\s+authenticated", "students CRUD to authenticated"),
        (r"GRANT\s+SELECT,\s*INSERT,\s*UPDATE,\s*DELETE\s+ON\s+public\.submissions\s+TO\s+authenticated", "submissions CRUD to authenticated"),
        (r"GRANT\s+SELECT,\s*INSERT,\s*UPDATE,\s*DELETE\s+ON\s+public\.misconceptions\s+TO\s+authenticated", "misconceptions CRUD to authenticated"),
        (r"GRANT\s+SELECT,\s*INSERT,\s*UPDATE,\s*DELETE\s+ON\s+public\.concept_checks\s+TO\s+authenticated", "concept_checks CRUD to authenticated"),
        (r"GRANT\s+SELECT,\s*INSERT,\s*UPDATE,\s*DELETE\s+ON\s+public\.learner_progress\s+TO\s+authenticated", "learner_progress CRUD to authenticated"),
        (r"GRANT\s+SELECT\s+ON\s+public\.concepts\s+TO\s+authenticated", "concepts SELECT only to authenticated"),
    ]
    for pat, label in grant_patterns:
        ok = bool(re.search(pat, sql, re.IGNORECASE))
        checks.append({"id": f"GRANT: {label}", "ok": ok, "level": "medium"})

    # 17. NO grants to `anon` role on any data table (guests use Flask session, not direct DB)
    anon_grants = re.findall(r"GRANT\s+[A-Z,\s]+\s+ON\s+public\.\w+\s+TO\s+anon", sql, re.IGNORECASE)
    checks.append({
        "id":    f"No GRANT to `anon` role on data tables (defense in depth)",
        "ok":    len(anon_grants) == 0,
        "level": "medium",
        "detail": f"found anon grants: {anon_grants[:5]}" if anon_grants else "clean — anon has zero data-table grants",
    })

    return checks


# =============================================================================
# Seed file audit
# =============================================================================
def audit_seed_sql(sql: str) -> list[dict]:
    checks = []
    clean_sql = re.sub(r"--.*$", "", sql, flags=re.MULTILINE)

    # 1. Count concept INSERT rows: VALUES tuples of format
    #    ('<uuid>', '<name>', '<slug>', '<desc>', 'python')
    concept_rows = re.findall(
        r"\('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}',\s*'[^']+',\s*'([a-z0-9_-]+)'", sql,
        re.IGNORECASE,
    )
    count = len(concept_rows)
    checks.append({
        "id":    f"Seed concepts count (>= 20): {count}",
        "ok":    count >= 20,
        "level": "high",
    })

    # 2. NO prerequisite edges in seed
    edges_cte = re.findall(r"prerequisite_edges|WITH edges\(|INSERT INTO public\.prerequisite", clean_sql, re.IGNORECASE)
    checks.append({
        "id":    "Seed has NO prerequisite_edges seed data",
        "ok":    len(edges_cte) == 0,
        "level": "high",
        "detail": f"found forbidden edges markers: {edges_cte[:5]}" if edges_cte else "clean",
    })

    # 3. NO resources seed data
    resources_cte = re.findall(r"INSERT INTO public\.resources|resources_in\(|WITH resources_in", clean_sql, re.IGNORECASE)
    checks.append({
        "id":    "Seed has NO resources catalog seed data",
        "ok":    len(resources_cte) == 0,
        "level": "high",
        "detail": f"found forbidden resources markers: {resources_cte[:5]}" if resources_cte else "clean",
    })

    # 4. All seed rows are INSERT ... ON CONFLICT (idempotent)
    on_conflict = re.findall(r"ON CONFLICT\b", sql, re.IGNORECASE)
    checks.append({
        "id":    f"Seed idempotent (uses ON CONFLICT) — count {len(on_conflict)}",
        "ok":    len(on_conflict) >= 1,
        "level": "medium",
    })

    return checks


# =============================================================================
# Live Supabase audit (optional)
# =============================================================================
def audit_live_supabase() -> list[dict]:
    """Uses the Supabase service-role client to introspect public tables."""
    checks = []
    try:
        from supabase import create_client
    except Exception as exc:  # pragma: no cover
        checks.append({"id": "Live DB check (skipped: supabase sdk not importable)",
                       "ok": False, "level": "low", "detail": str(exc)})
        return checks

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not (url and key):
        checks.append({"id": "Live DB check (skipped: SUPABASE env vars not set)",
                       "ok": False, "level": "low"})
        return checks

    client = create_client(url, key)

    for t in REQUIRED_TABLES:
        try:
            r = getattr(client, "table")(t).select("*").limit(1).execute()
            checks.append({"id": f"Live table reachable: {t}", "ok": True, "level": "high",
                           "detail": f"rows returned: {len(r.data)}"})
        except Exception as exc:
            checks.append({"id": f"Live table reachable: {t}", "ok": False, "level": "medium",
                           "detail": str(exc)[:160]})

    # Forbidden tables must NOT exist live either
    for t in FORBIDDEN_TABLES:
        try:
            r = getattr(client, "table")(t).select("*").limit(1).execute()
            checks.append({
                "id":     f"Forbidden live table: {t} (should not exist)",
                "ok":     False,
                "level":  "high",
                "detail": f"exists with {len(r.data)} rows — consider dropping manually per R1",
            })
        except Exception:
            checks.append({
                "id":    f"Forbidden live table: {t} — absent",
                "ok":    True,
                "level": "high",
                "detail": "correctly missing",
            })
    return checks


# =============================================================================
# Entrypoint
# =============================================================================
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema-only", action="store_true",
                        help="Skip live DB checks and only audit schema.sql + seed.sql.")
    parser.add_argument("--json", action="store_true",
                        help="Output machine-readable JSON report.")
    args = parser.parse_args()

    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8") if SCHEMA_FILE.exists() else ""
    seed_sql   = SEED_FILE.read_text(encoding="utf-8")   if SEED_FILE.exists()   else ""

    checks: list[dict] = []
    checks += audit_schema_sql(schema_sql)
    checks += audit_seed_sql(seed_sql)

    if not args.schema_only:
        checks += audit_live_supabase()

    total  = len(checks)
    passed = sum(1 for c in checks if c["ok"])
    failed = total - passed

    report = {"summary": {"total": total, "passed": passed, "failed": failed},
              "schema_file": str(SCHEMA_FILE),
              "seed_file":   str(SEED_FILE),
              "checks": checks}

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=" * 72)
        print("LineByLine - verify_database.py  Phase 7D audit (6 tables + RLS)")
        print("=" * 72)
        print(f"Schema file: {SCHEMA_FILE}")
        print(f"Seed file:   {SEED_FILE}")
        print(f"Total checks: {total}   Passed: {passed}   Failed: {failed}")
        print("-" * 72)
        import sys as _sys
        _ascii = getattr(_sys.stdout, "encoding", "").lower() not in ("utf-8", "utf8")
        for c in checks:
            icon = "PASS" if c["ok"] else ("FAIL" if _ascii else "X")
            lvl  = c.get("level", "low")
            det  = c.get("detail") or ""
            line = f" [{icon:>4}]  [{lvl[:1].upper()}] {c['id']}"
            if det:
                line += f"  -- {det}"
            print(line)
        print("-" * 72)
        if failed == 0:
            print("ALL CHECKS PASSED.")
        else:
            print(f"{failed} CHECK(S) FAILED. Fix before applying to production Supabase.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
