---
name: inject-questions
description: Ingest, verify and publish PilotQuest pilot exam questions under the strict PDF ingestion & publishing guide. Use for any new question source (PDF, JSONL, CSV), for recording technical/editorial/regulatory/media reviews, for releasing approved questions, for re-organizing or re-gating the whole question bank, and for producing the publishable-questions table. Triggers: "inject questions", "import this PDF/question bank", "add these questions", "review/approve questions", "how many questions are publishable", "re-organize the bank".
---

# /inject-questions — PilotQuest strict ingestion & publishing

The governing document is
`pilot-question-bank/PilotQuest_Strict_PDF_Ingestion_and_Publishing_Guide.md`.
Read the sections named below before acting; where this skill and the guide
differ, the guide wins.

**Core rule:** extraction, verification and publication are separate stages.
Extracted ≠ correct ≠ current ≠ reusable ≠ publishable. Never present an
extracted or canonical count as a usable count.

All commands run from `pilot-question-bank/`.

## 0. Orient (every invocation)

```bash
cd pilot-question-bank
python3 scripts/release_questions.py --dry-run     # current status + first failing gate per record
cat reports/publishable_summary.md                 # last published table
```

Know the layers (guide §2): `sources/` manifests and rights · `extracted/` raw
PDF extraction (git-ignored) · `data/` **active records only** · `quarantine/`
everything not yet released · `taxonomy/` rules, rights records, policy ·
`reviews/` review decision files · `views/` generated, never edited ·
`reports/` audit trail.

Then pick the matching flow.

## 1. New PDF (guide §4–7)

1. Copy the PDF into `inbox/`. Register it **before** extracting:
   `python3 scripts/ingest_pdf.py inbox/X.pdf --register --source-id SRC-… --title … --publisher … --rights-record RR-…`
2. Open the PDF and fill **every** `TODO` in `sources/source_manifest.json`
   (edition, syllabus version, page ranges, copyright notice verbatim,
   commercial-use status). Never infer validity, authority or reuse rights
   from the filename, publisher or the user's description.
3. If no rights record covers the source, add one to `taxonomy/rights_records.csv`
   (owner, licence/statutory basis, commercial use, modification, attribution,
   restrictions, reviewer, date). Unknown commercial permission is `unconfirmed`,
   not `permitted`.
4. Extract: `python3 scripts/ingest_pdf.py inbox/X.pdf --extract --source-id SRC-… --question-pages A-B --answer-key-pages C-D`.
   Read `extracted/SRC-…/extraction_report.md`. Look at several page dumps
   yourself and compare against the raw records; fix nothing in the raw layer.
5. Copyrighted source without clear reuse permission (guide §7): do **not**
   build a batch from its wording. Mark the source `restricted_do_not_use`,
   identify the syllabus objectives it covers, and write genuinely original
   questions from current official sources (flow 2, provenance
   `original_syllabus_aligned`, rights `RR-PROJECT-ORIGINAL`).
6. Otherwise: `python3 scripts/ingest_pdf.py --to-batch --source-id SRC-… --defaults inbox/X.defaults.json`
   then continue with flow 2.

## 2. Structured batch (JSONL / CSV)

```bash
python3 scripts/inject_questions.py inbox/B.jsonl --defaults inbox/B.defaults.json \
    --source-id SRC-… --rights-record RR-…                     # dry run
python3 scripts/inject_questions.py … --apply --provenance-reviewed "<what you read>"
```

- Read the printed intake sample **and** open the file to read more answers
  across the whole range. Look for verbatim textbook sentences, OCR junk,
  page/figure numbering, publisher names. A self-declared provenance label
  proves nothing; an intake sample is not verification (guide rule 3).
- Red flags or duplicates block import. `--allow-red-flags` / `--allow-duplicates`
  import into quarantine only, flagged; never into an active view.
- Never pass `--shuffle` before answers are verified. Answer-letter imbalance
  is a reporting signal (§14).
- Unknown fields are kept in `source_payload`; map them deliberately later.
- Every imported record lands in `quarantine/` with all reviews `pending`.
  There is no import route to `active`.

## 3. Reviews (guide §10, §11, §15)

A review is recorded in a CSV under `reviews/` and applied with
`scripts/release_questions.py --approval-file reviews/<file>.csv`.
Columns: `question_id, review_type, result, reviewer, date, evidence, notes`
(+ `regulatory_status, regulation_provision, source_effective_date, source_accessed_date`
for regulatory reviews). `review_type` ∈ technical · second_check · editorial ·
regulatory · media · accessibility. `result` ∈ passed · failed · pending.

When **you** (Claude) review:

- Read the full record: stem, every option, the key, the explanation. Never
  pass a record you have not read in full; never pass by batch or sample.
- **technical**: exactly one defensible option; recompute every number
  (record formula, units, rounding in `calculation_steps`). If the key is
  disputed or two options are defensible → `failed` with the reason.
- **editorial**: clarity, grammar, distractor quality, no "option above"
  references after shuffling. Official-sample wording is never edited; an
  ambiguous official item fails editorial and gets a new original version.
- **regulatory**: only from the current controlling text that you actually
  fetched in this session. Record exact provision, edition/effective date
  and access date; otherwise leave `pending`. Never mark `current_verified`
  from memory.
- **second_check**: must be a different reviewer from the first check. You
  may never second-check your own first check — leave it `pending` for a
  human instructor.
- Reviewer value: `claude-<model-id> (AI first-pass)`. Put what you
  actually checked in `evidence`.
- Corrections never overwrite: create a new version (new question_id,
  `question_version+1`, `supersedes_question_id`), mark the old one
  `superseded_by_question_id` (guide rule 9).

## 4. Release and report

```bash
python3 scripts/release_questions.py --approval-file reviews/<file>.csv   # or no flag to recompute everything
python3 scripts/validate_questions.py "data/**/*.jsonl" "quarantine/**/*.jsonl"
python3 scripts/dedupe.py
python3 scripts/validate_media.py
python3 scripts/check_regulatory_currency.py
```

`release_questions.py` recomputes every gate in `scripts/gates.py`; an
approval cannot override a failed gate. It moves records between `data/`
and `quarantine/`, appends `reports/audit_log.jsonl`, and rebuilds `views/`
and `reports/publishable_summary.md`.

Report to the user (guide §18) using `reports/publishable_summary.md`:
canonical, active exam, active flashcard, reel-eligible, quarantined (and
how many are rights-blocked), restricted, historical/superseded, rejected,
the blocker table, and what was reviewed in this session, by whom, with
which failures. Add a batch entry to `reports/progress.md`.

## 5. Re-organize / re-gate the whole bank

- After editing anything in `taxonomy/` (rules, overrides, policy, rights,
  applicability, duplicate decisions): `python3 scripts/categorize.py --write`
  (recategorizes, then recomputes gates and placement).
- `scripts/migrate_strict.py` was the one-time migration (2026-10-05); it is
  idempotent but should not be needed again.
- Cross-licence applicability only via an approved row in
  `taxonomy/applicability.csv` (scope, syllabus version, rationale, reviewer).
  Never across authorities; Air Law never by default.

## Publication tiers (guide §21, owner decision 2026-10-05)

- **verified**: every gate in §15 passes.
- **study**: same rights, provenance, technical (first check), editorial, media, duplicate and flag gates; official LO code, syllabus version and second check are relaxed; regulation-dependent items need `current_pending_second_review` from a first check against **fetched** current text. Records carry `publicationTier`, `studyNotice` and, for rules, `regulatoryNotice`.
- Rights are never relaxed by the tier. Settings: `taxonomy/policy.json` → `study_tier`.
- Flashcard-only decisions (implausible distractors): `taxonomy/style_overrides.csv`.

## Hard rules (guide §1, §15, §16, §21)

- Nothing becomes active except through the per-record gate (verified or study tier).
- Regulation-dependent content needs `current_verified` + exact provision +
  effective & access dates + second review.
- `reuse_allowed` and `verified` are derived — never set them from imports.
- With `policy.platform_commercial = true`, non-commercial material is
  excluded from the app, reels, ads and public exports.
- Image-dependent questions need a cleared, verified, accessible image —
  never a commercial textbook figure.
- Regulatory material in student views needs at least a first check against
  fetched current text (`current_pending_second_review`) and carries `regulatoryNotice`.
- `extracted/` may hold copyrighted text: it is git-ignored and never published.
- Ask the owner before changing `taxonomy/policy.json` or approving a rights record.
