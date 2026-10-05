-- =====================================================================
-- Pilot Theory Examination Question Bank — Normalized Relational Schema
-- Target dialect: PostgreSQL 14+ (portable to SQLite/MySQL with minor
-- changes: swap BOOLEAN/TIMESTAMPTZ/TEXT[] as needed).
--
-- Design principles:
--   * Every authority/exam system/licence keeps its own official
--     terminology — nothing is collapsed into a generic cross-authority
--     taxonomy (see `subjects.official_subject_name` vs
--     `subjects.normalized_subject_name`).
--   * Every question traces to exactly one `sources` row and carries an
--     explicit `provenance_classification`. Only questions whose
--     provenance is in the "usable" set may be surfaced to end users —
--     enforce this in the application layer via the
--     v_usable_questions view below, not by deleting quarantined rows.
--   * IDs are human-readable TEXT keys (e.g. 'EASA', 'EASA-PPLA-AL',
--     'EASA-PPLA-AL-000001') to keep exports/JSONL self-describing.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Lookup / enum-like domains (implemented as CHECK constraints so the
-- schema stays portable; swap for native ENUM types on Postgres if
-- preferred).
-- ---------------------------------------------------------------------

-- provenance_classification values:
--   official_released, official_sample, public_domain, open_licensed,
--   original_syllabus_aligned, third_party_reference_only,
--   restricted_do_not_use, provenance_uncertain
-- Only the first five may be flagged reuse_allowed = TRUE.

-- =====================================================================
-- AUTHORITIES
-- =====================================================================
CREATE TABLE authorities (
    authority_id        TEXT PRIMARY KEY,          -- e.g. 'EASA', 'UK-CAA', 'FAA'
    authority_name       TEXT NOT NULL,             -- full legal/official name
    abbreviation         TEXT NOT NULL,
    country               TEXT,                      -- NULL for multi-state bodies (EASA)
    jurisdiction          TEXT NOT NULL,             -- e.g. 'European Union (EASA Member States)'
    official_website      TEXT NOT NULL,
    notes                 TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- SOURCES  (declared before exam_systems/questions because both hold a
-- FK to it)
-- =====================================================================
CREATE TABLE sources (
    source_id             TEXT PRIMARY KEY,          -- e.g. 'SRC-EASA-PARTFCL-2024'
    title                   TEXT NOT NULL,
    publisher               TEXT NOT NULL,
    direct_url               TEXT NOT NULL,
    publication_date         DATE,
    revision                  TEXT,
    accessed_date             DATE NOT NULL,
    source_type               TEXT NOT NULL
                                CHECK (source_type IN (
                                  'regulation','official_syllabus','learning_objectives',
                                  'examination_guide','handbook','sample_exam',
                                  'released_question_set','open_data_portal',
                                  'open_licensed_material','authority_webpage','other')),
    licence                    TEXT,                    -- verbatim licence/copyright statement
    reuse_status                TEXT NOT NULL
                                CHECK (reuse_status IN (
                                  'reusable_verbatim','reusable_with_attribution',
                                  'reference_only_no_reuse','restricted','unknown')),
    reliability                 TEXT NOT NULL
                                CHECK (reliability IN ('primary_official','secondary_official',
                                  'reputable_secondary','unverified')),
    notes                        TEXT,
    created_at                   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- EXAM SYSTEMS  (a licence/certificate as examined by one authority)
-- =====================================================================
CREATE TABLE exam_systems (
    exam_system_id       TEXT PRIMARY KEY,          -- e.g. 'EASA-PPLA'
    authority_id          TEXT NOT NULL REFERENCES authorities(authority_id),
    official_name         TEXT NOT NULL,             -- authority's own term, verbatim
    licence_code           TEXT NOT NULL,             -- e.g. 'PPL(A)', 'CPL(H)', 'Part 61 PPL'
    licence_name            TEXT NOT NULL,
    aircraft_category      TEXT,                      -- Aeroplane / Helicopter / Sailplane / Balloon / Drone / n-a
    exam_language           TEXT NOT NULL,             -- primary language of the official exam
    current_version         TEXT,                      -- syllabus / LO issue in force
    effective_date          DATE,
    status                   TEXT NOT NULL DEFAULT 'active'
                              CHECK (status IN ('active','superseded','proposed','withdrawn')),
    source_id                TEXT REFERENCES sources(source_id),
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- SUBJECTS
-- =====================================================================
CREATE TABLE subjects (
    subject_id              TEXT PRIMARY KEY,       -- e.g. 'EASA-AGK' (Air Law = 010 etc.)
    authority_id              TEXT NOT NULL REFERENCES authorities(authority_id),
    official_subject_code      TEXT,                  -- e.g. EASA '010'
    official_subject_name       TEXT NOT NULL,          -- authority's own wording, verbatim
    normalized_subject_name     TEXT NOT NULL,          -- cross-authority mapping, UI/search only
    created_at                   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- SYLLABUS OBJECTIVES
-- =====================================================================
CREATE TABLE syllabus_objectives (
    objective_id             TEXT PRIMARY KEY,       -- e.g. 'EASA-PPLA-AL-010-01-01'
    exam_system_id             TEXT NOT NULL REFERENCES exam_systems(exam_system_id),
    subject_id                  TEXT NOT NULL REFERENCES subjects(subject_id),
    official_reference_code      TEXT,                  -- authority LO numbering, verbatim
    objective_text                TEXT NOT NULL,
    syllabus_version               TEXT NOT NULL,
    source_id                       TEXT NOT NULL REFERENCES sources(source_id),
    created_at                       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- QUESTIONS
-- =====================================================================
CREATE TABLE questions (
    question_id                TEXT PRIMARY KEY,      -- e.g. 'EASA-PPLA-AL-000001'
    authority_id                 TEXT NOT NULL REFERENCES authorities(authority_id),
    exam_system_id                 TEXT NOT NULL REFERENCES exam_systems(exam_system_id),
    subject_id                      TEXT NOT NULL REFERENCES subjects(subject_id),
    objective_id                     TEXT REFERENCES syllabus_objectives(objective_id),
    question_text                     TEXT NOT NULL,
    question_type                      TEXT NOT NULL
                                        CHECK (question_type IN
                                          ('single_choice','multiple_response','true_false',
                                           'calculation','chart_plotting','short_answer')),
    difficulty                          TEXT NOT NULL
                                        CHECK (difficulty IN ('beginner','intermediate','advanced')),
    aircraft_category                    TEXT,
    language                              TEXT NOT NULL DEFAULT 'en',
    provenance_classification              TEXT NOT NULL
                                        CHECK (provenance_classification IN (
                                          'official_released','official_sample','public_domain',
                                          'open_licensed','original_syllabus_aligned',
                                          'third_party_reference_only','restricted_do_not_use',
                                          'provenance_uncertain')),
    official_status                        TEXT NOT NULL DEFAULT 'not_official'
                                        CHECK (official_status IN ('official','not_official')),
    source_id                               TEXT NOT NULL REFERENCES sources(source_id),
    source_location                          TEXT,        -- page/section/paragraph within the source
    copyright_status                          TEXT,
    reuse_allowed                             BOOLEAN NOT NULL DEFAULT FALSE,
    created_by                                 TEXT NOT NULL,  -- 'original_authoring:<model/person>' or 'extracted'
    verified_at                                 TIMESTAMPTZ,
    status                                       TEXT NOT NULL DEFAULT 'quarantined'
                                        CHECK (status IN ('quarantined','active','archived','rejected')),
    created_at                                   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                                   TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Only the five reusable provenance classes may set reuse_allowed = TRUE.
    CONSTRAINT chk_reuse_matches_provenance CHECK (
      (reuse_allowed = FALSE) OR
      (provenance_classification IN (
        'official_released','official_sample','public_domain',
        'open_licensed','original_syllabus_aligned'))
    )
);

CREATE INDEX idx_questions_exam_system ON questions(exam_system_id);
CREATE INDEX idx_questions_subject ON questions(subject_id);
CREATE INDEX idx_questions_provenance ON questions(provenance_classification);
CREATE INDEX idx_questions_status ON questions(status);

-- =====================================================================
-- ANSWER CHOICES
-- =====================================================================
CREATE TABLE answer_choices (
    choice_id           TEXT PRIMARY KEY,
    question_id           TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    choice_label           TEXT NOT NULL,             -- 'A','B','C','D' (adapt per authority format)
    choice_text              TEXT NOT NULL,
    is_correct                 BOOLEAN NOT NULL DEFAULT FALSE,
    display_order               INTEGER NOT NULL,
    UNIQUE (question_id, choice_label)
);

-- =====================================================================
-- EXPLANATIONS
-- =====================================================================
CREATE TABLE explanations (
    explanation_id                    TEXT PRIMARY KEY,
    question_id                         TEXT NOT NULL UNIQUE REFERENCES questions(question_id) ON DELETE CASCADE,
    correct_answer_explanation            TEXT NOT NULL,
    incorrect_answer_explanations           JSONB,      -- {"B": "...", "C": "...", "D": "..."}
    regulation_reference                     TEXT,
    handbook_reference                        TEXT,
    calculation_steps                          TEXT,
    safety_note                                 TEXT
);

-- =====================================================================
-- MEDIA
-- =====================================================================
CREATE TABLE media (
    media_id           TEXT PRIMARY KEY,
    question_id           TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    media_type              TEXT NOT NULL CHECK (media_type IN
                              ('image','chart','diagram','audio','video','document')),
    file_path                 TEXT NOT NULL,
    alt_text                    TEXT NOT NULL,
    attribution                  TEXT,
    licence                       TEXT NOT NULL
);

-- =====================================================================
-- REVIEW RECORDS
-- =====================================================================
CREATE TABLE review_records (
    review_id           TEXT PRIMARY KEY,
    question_id           TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    reviewer                 TEXT NOT NULL,
    review_type                TEXT NOT NULL CHECK (review_type IN
                                ('provenance_check','factual_check','regulatory_check',
                                 'calculation_check','duplicate_check','language_check','final_approval')),
    result                       TEXT NOT NULL CHECK (result IN ('pass','fail','needs_revision')),
    notes                          TEXT,
    reviewed_at                      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- TRANSLATIONS
-- =====================================================================
CREATE TABLE question_translations (
    translation_id       TEXT PRIMARY KEY,
    question_id             TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    language                  TEXT NOT NULL,
    question_text_translated    TEXT NOT NULL,
    choices_translated              JSONB,
    explanation_translated            TEXT,
    translation_method                  TEXT NOT NULL CHECK (translation_method IN
                                        ('official_source','human_translator','machine_assisted_reviewed',
                                         'machine_unreviewed')),
    translated_by                        TEXT,
    verified                              BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (question_id, language)
);

-- =====================================================================
-- QUESTION VERSIONS  (regulatory changes, wording fixes, re-verification)
-- =====================================================================
CREATE TABLE question_versions (
    version_id           TEXT PRIMARY KEY,
    question_id             TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    version_number             INTEGER NOT NULL,
    snapshot                     JSONB NOT NULL,        -- full question+choices+explanation at this version
    change_reason                  TEXT NOT NULL,
    changed_by                       TEXT NOT NULL,
    changed_at                         TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (question_id, version_number)
);

-- =====================================================================
-- DUPLICATE GROUPS  (similarity / duplicate-detection support)
-- =====================================================================
CREATE TABLE duplicate_groups (
    duplicate_group_id      TEXT PRIMARY KEY,
    best_question_id           TEXT NOT NULL REFERENCES questions(question_id),
    detection_method              TEXT NOT NULL CHECK (detection_method IN
                                    ('exact_text','near_duplicate_similarity','translated_duplicate',
                                     'scenario_cosmetic_variant','manual')),
    notes                           TEXT,
    created_at                        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE duplicate_group_members (
    duplicate_group_id      TEXT NOT NULL REFERENCES duplicate_groups(duplicate_group_id) ON DELETE CASCADE,
    question_id                TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    similarity_score              NUMERIC(4,3) NOT NULL CHECK (similarity_score BETWEEN 0 AND 1),
    is_best_version                 BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (duplicate_group_id, question_id)
);

-- =====================================================================
-- TAGS
-- =====================================================================
CREATE TABLE tags (
    tag_id       TEXT PRIMARY KEY,
    tag_name        TEXT NOT NULL UNIQUE,
    tag_category      TEXT   -- e.g. 'topic','exam-technique','regulation-family'
);

CREATE TABLE question_tags (
    question_id     TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    tag_id             TEXT NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (question_id, tag_id)
);

-- =====================================================================
-- USER REPORTS  (learner-flagged issues)
-- =====================================================================
CREATE TABLE user_reports (
    report_id       TEXT PRIMARY KEY,
    question_id        TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    reported_by            TEXT NOT NULL,
    report_reason            TEXT NOT NULL CHECK (report_reason IN
                              ('factual_error','ambiguous_wording','outdated_regulation',
                               'wrong_answer_key','typo','copyright_concern','other')),
    report_text                TEXT,
    status                        TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','resolved','dismissed')),
    created_at                     TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at                      TIMESTAMPTZ
);

-- =====================================================================
-- EXAMINATION ATTEMPTS / SAVED QUESTIONS / PERFORMANCE ANALYTICS
-- (product-layer tables — included for platform completeness)
-- =====================================================================
CREATE TABLE users (
    user_id      TEXT PRIMARY KEY,
    email           TEXT UNIQUE,
    display_name       TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE exam_attempts (
    attempt_id        TEXT PRIMARY KEY,
    user_id               TEXT NOT NULL REFERENCES users(user_id),
    exam_system_id           TEXT NOT NULL REFERENCES exam_systems(exam_system_id),
    started_at                 TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at                 TIMESTAMPTZ,
    score_percent                  NUMERIC(5,2),
    passed                            BOOLEAN
);

CREATE TABLE exam_attempt_answers (
    attempt_id        TEXT NOT NULL REFERENCES exam_attempts(attempt_id) ON DELETE CASCADE,
    question_id           TEXT NOT NULL REFERENCES questions(question_id),
    chosen_choice_id         TEXT REFERENCES answer_choices(choice_id),
    is_correct                  BOOLEAN NOT NULL,
    time_spent_seconds             INTEGER,
    PRIMARY KEY (attempt_id, question_id)
);

CREATE TABLE saved_questions (
    user_id       TEXT NOT NULL REFERENCES users(user_id),
    question_id      TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    saved_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, question_id)
);

CREATE TABLE performance_analytics (
    user_id           TEXT NOT NULL REFERENCES users(user_id),
    subject_id            TEXT NOT NULL REFERENCES subjects(subject_id),
    exam_system_id           TEXT NOT NULL REFERENCES exam_systems(exam_system_id),
    questions_attempted         INTEGER NOT NULL DEFAULT 0,
    questions_correct             INTEGER NOT NULL DEFAULT 0,
    last_attempt_at                  TIMESTAMPTZ,
    PRIMARY KEY (user_id, subject_id, exam_system_id)
);

-- =====================================================================
-- VIEW: only rows fit to serve to end users
-- =====================================================================
CREATE VIEW v_usable_questions AS
SELECT q.*
FROM questions q
WHERE q.status = 'active'
  AND q.reuse_allowed = TRUE
  AND q.provenance_classification IN (
    'official_released','official_sample','public_domain',
    'open_licensed','original_syllabus_aligned');
