-- =============================================================================
-- LineByLine — Database Schema (Phase 7C, REVISED 6-table architecture)
-- Supabase PostgreSQL (uuid-ossp extension available).
--
-- OPERATIONS IN THIS FILE ARE SAFE (non-destructive):
--   - CREATE TABLE IF NOT EXISTS
--   - CREATE INDEX IF NOT EXISTS
--   - ALTER TABLE ... ADD CONSTRAINT ... IF NOT EXISTS
--   - CREATE EXTENSION IF NOT EXISTS
--
-- NO DROP, NO DELETE, NO TRUNCATE, NO TYPE ALTERATION.
--
-- ARCHITECTURE (simplified, no prereq/resource catalog tables):
--
--   auth.users
--       │ UUID(id)
--       ▼
--   students (1:1) ─┬── submissions
--                   ├── misconceptions
--                   ├── concept_checks
--                   └── learner_progress
--
--   concepts (canonical reference table — used to normalize Gemini output)
--
-- PREREQUISITE GRAPH / RESOURCES: NOT persisted as static tables.
--   Gemini dynamically determines prerequisite concepts and resource URLs
--   at recommendation time. Database stores LEARNER state only.
--
-- UUID/FK COMPATIBILITY:
--   Every learner-facing table uses UUID primary keys.
--   Every foreign key to a learner- or identity-facing table is UUID type.
--   students.id REFERENCES auth.users(id) directly (UUID ↔ UUID).
--   No integer PK / UUID FK mismatches anywhere.
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. students (learner profile, 1:1 with Supabase Auth)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.students (
    id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name    TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- 2. submissions (meaningful learner code submissions)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.submissions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
    code            TEXT NOT NULL,
    language        TEXT NOT NULL DEFAULT 'python',
    persona         TEXT NOT NULL DEFAULT 'beginner',
    analysis_summary TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_submissions_student_created
    ON public.submissions (student_id, created_at DESC);

-- =============================================================================
-- 3. concepts (canonical reference — seeded, curriculum-owned)
--    Used to NORMALIZE Gemini-detected concepts before storing
--    learner mastery / history in learner_progress / misconceptions etc.
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.concepts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    description     TEXT,
    language        TEXT NOT NULL DEFAULT 'python'
);

CREATE INDEX IF NOT EXISTS idx_concepts_slug ON public.concepts (slug);
CREATE INDEX IF NOT EXISTS idx_concepts_language ON public.concepts (language);

-- =============================================================================
-- 4. misconceptions (learner-specific dynamic records — NOT a global catalog)
--    Each record is one detected possible misconception for a learner.
--    Gemini produces: { title, description }
--    Severity is a lightweight learner-side annotation (optional).
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.misconceptions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
    submission_id   UUID REFERENCES public.submissions(id) ON DELETE SET NULL,
    concept_id      UUID REFERENCES public.concepts(id) ON DELETE SET NULL,
    title           TEXT NOT NULL,
    explanation     TEXT,
    severity        TEXT CHECK (severity IN ('low', 'medium', 'high')) DEFAULT 'medium',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_misconceptions_student
    ON public.misconceptions (student_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_misconceptions_submission
    ON public.misconceptions (submission_id);
CREATE INDEX IF NOT EXISTS idx_misconceptions_concept
    ON public.misconceptions (concept_id);

-- =============================================================================
-- 5. concept_checks (learner quiz attempts / MCQ results)
--    One row per learner quiz interaction.
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.concept_checks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
    concept_id      UUID REFERENCES public.concepts(id) ON DELETE SET NULL,
    submission_id   UUID REFERENCES public.submissions(id) ON DELETE SET NULL,
    concept_name    TEXT,
    question_text   TEXT,
    selected_index  INTEGER,
    correct_index   INTEGER,
    is_correct      BOOLEAN NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_concept_checks_student
    ON public.concept_checks (student_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_concept_checks_concept
    ON public.concept_checks (concept_id);

-- =============================================================================
-- 6. learner_progress (aggregated learner mastery — 1 row per student+concept)
--    This is the SOURCE OF TRUTH for personalized learning.
--    Mastery bands (Phase 8): 0.00–0.39 Weak, 0.40–0.69 Developing, 0.70–1.00 Strong
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.learner_progress (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
    concept_id      UUID NOT NULL REFERENCES public.concepts(id) ON DELETE CASCADE,
    mastery_score   NUMERIC(5, 4) NOT NULL DEFAULT 0
        CHECK (mastery_score >= 0 AND mastery_score <= 1),
    attempts        INTEGER NOT NULL DEFAULT 0,
    correct_count   INTEGER NOT NULL DEFAULT 0,
    incorrect_count INTEGER NOT NULL DEFAULT 0,
    struggle_count  INTEGER NOT NULL DEFAULT 0,
    last_activity_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_student_concept UNIQUE (student_id, concept_id)
);

CREATE INDEX IF NOT EXISTS idx_learner_progress_student
    ON public.learner_progress (student_id);
CREATE INDEX IF NOT EXISTS idx_learner_progress_concept
    ON public.learner_progress (concept_id);
CREATE INDEX IF NOT EXISTS idx_learner_progress_mastery
    ON public.learner_progress (student_id, mastery_score);

-- =============================================================================
-- AUTO-UPDATED_AT TRIGGERS (install once per table that needs updated_at)
-- =============================================================================
CREATE OR REPLACE FUNCTION public.trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_students_updated_at    ON public.students;
CREATE TRIGGER trg_students_updated_at
    BEFORE UPDATE ON public.students
    FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();

DROP TRIGGER IF EXISTS trg_learner_progress_updated_at ON public.learner_progress;
CREATE TRIGGER trg_learner_progress_updated_at
    BEFORE UPDATE ON public.learner_progress
    FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();

-- =============================================================================
-- Phase 7D — Row Level Security (RLS)
-- =============================================================================
--
-- SECURITY MODEL:
--   Backend (Flask) uses SUPABASE_SERVICE_ROLE_KEY  →  BYPASSRLS  →  continues
--     working with zero code changes (requirement 6).
--   Frontend Supabase JS client uses anon key        →  RLS APPLIED  →
--     anon/authenticated roles are restricted to OWN rows only (defense-in-depth).
--   RLS is also enforced for anyone else connecting to this DB (defense-in-depth).
--
-- TABLE OWNERSHIP PATTERN:
--   students                — row owner = id (= auth.uid())
--   submissions             — row owner = student_id (= auth.uid())
--   misconceptions          — row owner = student_id (= auth.uid())
--   concept_checks          — row owner = student_id (= auth.uid())
--   learner_progress        — row owner = student_id (= auth.uid())
--   concepts (reference)    — no owner; authenticated users MAY READ only;
--                             NO INSERT/UPDATE/DELETE for anon/authenticated
--                             (canonical curriculum-owned table).
--
-- ALL POLICIES ARE IDEMPOTENT: DROP IF EXISTS, then (re)create.
-- NO DROP TABLE, NO DATA LOSS, NO DESTRUCTIVE OPERATIONS.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Step 1 — Enable RLS on every learner-owned table + concepts reference table.
--   ALTER TABLE ... ENABLE ROW LEVEL SECURITY is safe to run repeatedly;
--   it is a no-op when RLS is already enabled.
-- -----------------------------------------------------------------------------
ALTER TABLE public.students         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.submissions      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.misconceptions   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.concept_checks   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learner_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.concepts         ENABLE ROW LEVEL SECURITY;

-- -----------------------------------------------------------------------------
-- Step 2 — Explicit role grants (idempotent: GRANT repeated is a no-op).
--   Service-role backend bypasses RLS entirely (BYPASSRLS attribute).
--   Authenticated frontend users: CRUD their own rows (RLS scopes to owner).
--   Anon (guest) frontend users: NO direct access to any application table —
--     guests continue working through Flask session storage + service-role
--     backend, never by touching Supabase tables directly.
-- -----------------------------------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE ON public.students         TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.submissions      TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.misconceptions   TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.concept_checks   TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.learner_progress TO authenticated;
GRANT SELECT                              ON public.concepts         TO authenticated;

-- -----------------------------------------------------------------------------
-- Step 3 — students table: row owner = id (= auth.users.id = auth.uid())
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "students_select_own" ON public.students;
CREATE POLICY "students_select_own" ON public.students
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "students_insert_own" ON public.students;
CREATE POLICY "students_insert_own" ON public.students
    FOR INSERT WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "students_update_own" ON public.students;
CREATE POLICY "students_update_own" ON public.students
    FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "students_delete_own" ON public.students;
CREATE POLICY "students_delete_own" ON public.students
    FOR DELETE USING (auth.uid() = id);

-- -----------------------------------------------------------------------------
-- Step 4 — submissions table: row owner = student_id (= auth.uid())
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "submissions_select_own" ON public.submissions;
CREATE POLICY "submissions_select_own" ON public.submissions
    FOR SELECT USING (auth.uid() = student_id);

DROP POLICY IF EXISTS "submissions_insert_own" ON public.submissions;
CREATE POLICY "submissions_insert_own" ON public.submissions
    FOR INSERT WITH CHECK (auth.uid() = student_id);

DROP POLICY IF EXISTS "submissions_update_own" ON public.submissions;
CREATE POLICY "submissions_update_own" ON public.submissions
    FOR UPDATE USING (auth.uid() = student_id) WITH CHECK (auth.uid() = student_id);

DROP POLICY IF EXISTS "submissions_delete_own" ON public.submissions;
CREATE POLICY "submissions_delete_own" ON public.submissions
    FOR DELETE USING (auth.uid() = student_id);

-- -----------------------------------------------------------------------------
-- Step 5 — misconceptions table: row owner = student_id (= auth.uid())
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "misconceptions_select_own" ON public.misconceptions;
CREATE POLICY "misconceptions_select_own" ON public.misconceptions
    FOR SELECT USING (auth.uid() = student_id);

DROP POLICY IF EXISTS "misconceptions_insert_own" ON public.misconceptions;
CREATE POLICY "misconceptions_insert_own" ON public.misconceptions
    FOR INSERT WITH CHECK (auth.uid() = student_id);

DROP POLICY IF EXISTS "misconceptions_update_own" ON public.misconceptions;
CREATE POLICY "misconceptions_update_own" ON public.misconceptions
    FOR UPDATE USING (auth.uid() = student_id) WITH CHECK (auth.uid() = student_id);

DROP POLICY IF EXISTS "misconceptions_delete_own" ON public.misconceptions;
CREATE POLICY "misconceptions_delete_own" ON public.misconceptions
    FOR DELETE USING (auth.uid() = student_id);

-- -----------------------------------------------------------------------------
-- Step 6 — concept_checks table: row owner = student_id (= auth.uid())
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "concept_checks_select_own" ON public.concept_checks;
CREATE POLICY "concept_checks_select_own" ON public.concept_checks
    FOR SELECT USING (auth.uid() = student_id);

DROP POLICY IF EXISTS "concept_checks_insert_own" ON public.concept_checks;
CREATE POLICY "concept_checks_insert_own" ON public.concept_checks
    FOR INSERT WITH CHECK (auth.uid() = student_id);

DROP POLICY IF EXISTS "concept_checks_update_own" ON public.concept_checks;
CREATE POLICY "concept_checks_update_own" ON public.concept_checks
    FOR UPDATE USING (auth.uid() = student_id) WITH CHECK (auth.uid() = student_id);

DROP POLICY IF EXISTS "concept_checks_delete_own" ON public.concept_checks;
CREATE POLICY "concept_checks_delete_own" ON public.concept_checks
    FOR DELETE USING (auth.uid() = student_id);

-- -----------------------------------------------------------------------------
-- Step 7 — learner_progress table: row owner = student_id (= auth.uid())
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "learner_progress_select_own" ON public.learner_progress;
CREATE POLICY "learner_progress_select_own" ON public.learner_progress
    FOR SELECT USING (auth.uid() = student_id);

DROP POLICY IF EXISTS "learner_progress_insert_own" ON public.learner_progress;
CREATE POLICY "learner_progress_insert_own" ON public.learner_progress
    FOR INSERT WITH CHECK (auth.uid() = student_id);

DROP POLICY IF EXISTS "learner_progress_update_own" ON public.learner_progress;
CREATE POLICY "learner_progress_update_own" ON public.learner_progress
    FOR UPDATE USING (auth.uid() = student_id) WITH CHECK (auth.uid() = student_id);

DROP POLICY IF EXISTS "learner_progress_delete_own" ON public.learner_progress;
CREATE POLICY "learner_progress_delete_own" ON public.learner_progress
    FOR DELETE USING (auth.uid() = student_id);

-- -----------------------------------------------------------------------------
-- Step 8 — concepts canonical reference table
--   Authenticated users may READ concepts (frontend concept normalization).
--   NO INSERT/UPDATE/DELETE policies for authenticated users — canonical
--   concepts are curriculum-owned and seeded via service role only.
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "concepts_select_authenticated" ON public.concepts;
CREATE POLICY "concepts_select_authenticated" ON public.concepts
    FOR SELECT TO authenticated USING (true);
