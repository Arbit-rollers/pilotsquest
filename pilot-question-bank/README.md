# Pilot Question Bank

A comprehensive, syllabus-aligned study bank compiled from legally reusable official pilot theory-examination materials and original practice questions, organized separately by national/regional aviation authority.

**This is a study and training resource.** It does not claim to contain "all exam questions" for any authority, does not reproduce any confidential live examination item bank, and does not guarantee passing an examination. Where a resource is confidential or its reuse terms could not be confirmed, it is recorded as a source only — never scraped into the question bank.

## Status: Batch 1 (research + scaffolding)

This is the first research/build batch. See `reports/progress.md` for exactly what has and has not been done, `reports/unresolved_issues.md` for open questions, and `research/coverage_report.csv` for per-authority/licence/subject coverage. No questions are yet marked `status: active` (usable) — the one seed batch created this session (EASA PPL(A) Air Law) is deliberately `quarantined` pending regulatory citation verification.

## Structure

```
pilot-question-bank/
├── README.md                    — this file
├── research/                    — authority inventory, source register, copyright audit, coverage gaps
├── schemas/                     — SQL schema, JSON Schema for questions, CSV import template
├── data/<authority>/            — MASTER question store, one JSONL file per authority/licence/subject/language/batch
├── taxonomy/                    — categorization rules (study areas, licences, overrides, applicability, review flags)
├── views/                       — GENERATED per-purpose outputs (app feed, exam/flashcard sets, reel candidates, review queue)
├── inbox/                       — drop new batches here; see "question injection.md"
├── reports/                     — progress, rejected sources, legal/provenance notes, unresolved issues
└── scripts/                     — validation, duplicate-detection, and export tooling (Python 3, stdlib + optional jsonschema)
```

## Provenance classifications

Every question carries exactly one of:

- `official_released` — an authority's own released/retired live exam question
- `official_sample` — an authority-published sample/practice question (not a live item)
- `public_domain` — content from a work with no copyright restriction (e.g. many US federal publications)
- `open_licensed` — explicitly open-licensed material (e.g. CC BY government content)
- `original_syllabus_aligned` — written for this project from a verified syllabus/learning objective; never presented as a real or recalled exam question
- `third_party_reference_only` — a resource whose existence is recorded but which is not, and must not be, ingested
- `restricted_do_not_use` — confidential/restricted material (e.g. EASA's ECQB); recorded as a source only
- `provenance_uncertain` — quarantined pending manual review

Only the first five classes may ever be marked `reuse_allowed = true`, and only rows with `status = 'active'` are served to end users (see `schemas/database_schema.sql`, view `v_usable_questions`).

## Working with the data

```bash
# Validate all JSONL question files
python3 scripts/validate_questions.py "data/**/*.jsonl"

# Detect likely duplicate/near-duplicate questions
python3 scripts/detect_duplicates.py "data/**/*.jsonl"

# Re-derive categories and rebuild the per-purpose views (run after any change)
python3 scripts/categorize.py --write && python3 scripts/build_views.py

# Inject a new batch (dry run first; full guide in "question injection.md")
python3 scripts/inject_questions.py inbox/<batch>.jsonl --defaults inbox/<batch>.defaults.json

# Export usable (active + reuse_allowed) questions to flat CSV
python3 scripts/export_database.py --data-dir data --out-dir export
```

`scripts/validate_questions.py` uses the `jsonschema` package for full JSON Schema validation if installed (`pip install jsonschema`); it still runs the structural/provenance checks without it.

## Legal posture

See `reports/legal_and_provenance_notes.md` for the full policy and the specific licensing questions this batch surfaced (most importantly: Transport Canada's official sample exams are reusable with attribution for **non-commercial** use only, per Crown copyright terms captured verbatim this session).
