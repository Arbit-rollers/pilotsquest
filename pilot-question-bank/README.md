# Pilot Question Bank

A comprehensive, syllabus-aligned study bank compiled from legally reusable official pilot theory-examination materials and original practice questions, organized separately by national/regional aviation authority.

**This is a study and training resource.** It does not claim to contain "all exam questions" for any authority, does not reproduce any confidential live examination item bank, and does not guarantee passing an examination. Where a resource is confidential or its reuse terms could not be confirmed, it is recorded as a source only — never scraped into the question bank.

## Status

Governed by `PilotQuest_Strict_PDF_Ingestion_and_Publishing_Guide.md` (since 2026-10-05). Every question is gated individually; only records that pass every gate live in `data/` and reach student views. Current counts: `reports/publishable_summary.md`. History: `reports/progress.md`.

## Structure

```
pilot-question-bank/
├── README.md                    — this file
├── research/                    — authority inventory, source register, copyright audit, coverage gaps
├── schemas/                     — SQL schema, JSON Schema for questions, CSV import template
├── sources/                     — source manifests (hash, edition, rights) — sources/source_manifest.json
├── extracted/                   — raw PDF extraction (git-ignored; may contain copyrighted text)
├── data/<authority>/            — ACTIVE records only (passed the per-record activation gate)
├── quarantine/<authority>/      — every record not yet released, with gate_failures + next_action
├── taxonomy/                    — categorization rules, rights records, publication policy, review decisions
├── reviews/                     — review decision files applied by release_questions.py
├── views/                       — GENERATED per-purpose outputs (app, study, reels, review queue)
├── inbox/                       — drop new PDFs/batches here
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
python3 scripts/validate_questions.py "data/**/*.jsonl" "quarantine/**/*.jsonl"

# Detect likely duplicate/near-duplicate questions
python3 scripts/detect_duplicates.py "data/**/*.jsonl"

# Strict pipeline — see PilotQuest_Strict_PDF_Ingestion_and_Publishing_Guide.md and the /inject-questions skill
python3 scripts/ingest_pdf.py inbox/X.pdf --register --source-id SRC-...   # then --extract, --to-batch
python3 scripts/inject_questions.py inbox/B.jsonl --defaults inbox/B.defaults.json   # lands in quarantine/
python3 scripts/release_questions.py --approval-file reviews/<file>.csv   # apply reviews, recompute gates
python3 scripts/validate_questions.py "data/**/*.jsonl" "quarantine/**/*.jsonl"
cat reports/publishable_summary.md

# Export usable (active + reuse_allowed) questions to flat CSV
python3 scripts/export_database.py --data-dir data --out-dir export
```

`scripts/validate_questions.py` uses the `jsonschema` package for full JSON Schema validation if installed (`pip install jsonschema`); it still runs the structural/provenance checks without it.

## Legal posture

See `reports/legal_and_provenance_notes.md` for the full policy and the specific licensing questions this batch surfaced (most importantly: Transport Canada's official sample exams are reusable with attribution for **non-commercial** use only, per Crown copyright terms captured verbatim this session).
