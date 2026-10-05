# PilotQuest Strict PDF Ingestion and Publishing Guide

This document replaces the earlier injection guide. It defines how PDF question banks, answer keys, explanations, figures, and diagrams are imported into PilotQuest without losing provenance or publishing unverified, obsolete, or restricted material.

**Core rule:** extraction, verification, and publication are separate stages. A question being successfully extracted does not make it correct, current, reusable, or publishable.

## 1. Non-negotiable corrections to the previous process

The previous guide had useful separation between master data, taxonomy, and generated views, but the following policies must change:

1. The 230 EASA Air Law questions awaiting provision review must not remain active. They stay quarantined until each record has a current controlling provision and completed regulatory review.
2. `--activate` must never publish a whole batch from a batch-level statement. Publication is decided question by question.
3. Reading a random sample is only an intake check. It is not answer verification, copyright review, or provenance approval.
4. `reuse_allowed=true` cannot be accepted merely because it appears in an imported file. It must be supported by a source licence or an internal decision record.
5. Cross-licence applicability must not be inferred from broad EASA rules alone. It requires learning-objective and scope matching.
6. Authority-specific questions must never be widened to another authority automatically.
7. An extracted textbook question is a source record, not automatically a publishable study record.
8. Image-dependent questions cannot enter exams or flashcards until the exact cleared image or an independently created accurate replacement is attached and verified.
9. Existing records are never silently overwritten. Corrections create new versions linked to the original.
10. Current-law verification must record the exact provision, revision/effective date, access date, and jurisdiction.

## 2. Repository layers

```text
pilot-question-bank/
├── sources/       Immutable PDF/document manifests and rights records
├── extracted/     Raw question, answer-key, explanation, and image extraction
├── data/          Reviewed canonical question versions
├── taxonomy/      Authority, licence, subject, objective, and mapping rules
├── media/         Cleared original/licensed figures plus manifests
├── inbox/         New PDF, JSONL, and CSV intake
├── quarantine/    Unresolved regulatory, technical, provenance, OCR, or media items
├── views/         Generated application, exam, flashcard, reel, and review outputs
├── reports/       Audit trails, coverage, conflicts, rights, and release reports
├── schemas/       JSON Schema and import contracts
└── scripts/       Extract, verify, inject, validate, deduplicate, and build tools
```

Rules:

- Source evidence lives in `sources/` and `extracted/`.
- Canonical reviewed content lives in `data/`.
- Classification decisions live in `taxonomy/`.
- Cleared media and image rights live in `media/`.
- Unresolved records live in `quarantine/`.
- Consumer outputs are generated in `views/` and are never edited manually.

## 3. Required pipeline states

Every question moves through these states:

```text
received → extracted → answer_matched → classified → rights_reviewed
→ technically_verified → regulatorily_verified → media_verified
→ duplicate_reviewed → approved → active
```

Possible terminal or holding states:

- `quarantined`
- `restricted_do_not_use`
- `historical_reference_only`
- `superseded`
- `rejected`

No step may be skipped. A state transition must create an audit record containing the reviewer or process, date, result, evidence, and notes.

## 4. PDF intake and source registration

For each uploaded PDF, create a source manifest before extracting questions:

- Stable `source_id`
- Original filename and file hash
- Title and publisher
- Edition, revision, publication date, and stated syllabus version
- Total page count
- Language
- Intended authority, jurisdiction, licence, and aircraft category
- Question-page ranges
- Answer-key ranges
- Explanation ranges
- Image/figure ranges
- Native-text or scanned status
- Copyright notice and licence text
- Commercial-use status
- Access date
- Source quality notes

Do not infer current validity, reuse permission, or authority solely from the filename, publisher, or upload description.

## 5. Raw extraction rules

Create an immutable source record for every detected question. Preserve:

- Exact original question number
- Exact original wording
- Exact original choices and their order
- Original stated answer
- Original explanation
- PDF page for each element
- Figure or table reference
- Extraction method: `native_text`, `ocr`, or `manual`
- OCR confidence and uncertain tokens
- Bounding box or page position when available
- Source record ID

Never silently repair spelling, units, formulas, answer labels, or OCR errors in the raw layer. Corrections belong in a separate reviewed version.

If words, symbols, units, superscripts, answer labels, or diagrams are unclear, mark the record `extraction_uncertain` and quarantine it.

## 6. Answer-key matching

Answer matching is a distinct validation step. Check:

- Numbering continuity
- Renumbered editions
- Duplicate or missing numbers
- Multi-column layouts
- Separate answer keys by chapter
- Corrections or errata
- Scanned-page ordering
- Answer-key version compatibility

Store an `answer_match_confidence` score and the exact answer-key page. A low-confidence or ambiguous match cannot proceed to publication.

## 7. Original content versus publishable content

Use two linked records where necessary:

1. **Source extraction record:** immutable representation of what the PDF contains.
2. **Study question version:** reviewed, corrected, and publishable version when legal and technically valid.

If the PDF is copyrighted and reuse is not clearly permitted:

- Mark the source record `restricted_do_not_use`.
- Do not expose its wording or figures in student views.
- Identify the underlying syllabus objective.
- Write a genuinely original question from current official sources.
- Do not closely paraphrase the source.
- Link the original replacement to the objective, not as a copy of the restricted item.

## 8. Provenance and rights controls

Allowed provenance values:

- `official_released`
- `official_sample`
- `public_domain`
- `open_licensed`
- `original_syllabus_aligned`
- `third_party_reference_only`
- `restricted_do_not_use`
- `provenance_uncertain`

Only the first five may become active, and only after rights review.

`reuse_allowed` is derived from a rights record, not trusted from imported data. The rights record must include:

- Copyright owner
- Licence or statutory basis
- Source URL or document location
- Commercial-use permission
- Modification permission
- Attribution requirement
- Territory or platform restrictions
- Reviewer and review date

If PilotQuest is commercial or promotes a commercial product, non-commercial material must be excluded from the app, reels, advertising, and public exports unless permission is obtained.

## 9. Authority and syllabus separation

The following layers must remain distinct:

```text
Framework → Authority → Jurisdiction → Exam system → Licence/rating
→ Aircraft category → Syllabus version → Official subject
→ Learning objective → Question version
```

- ICAO is a standards framework, not a generic national exam authority.
- EASA and UK CAA content must remain separate.
- SHGM questions must be verified against current Turkish implementation and official Turkish sources.
- FAA ACS Areas of Operation, Tasks, and Elements must be retained alongside normalized topics.
- CASA terminology and exam structure must remain authority-specific.
- Normalized topics support analytics only; they never replace official subject names or learning objectives.

Cross-licence or cross-authority applicability requires a documented mapping with scope, syllabus version, rationale, and reviewer. Air Law and operational rules are never automatically shared.

## 10. Current-law and technical verification

The PDF answer is evidence of what the PDF says, not evidence of what is currently correct.

For regulation-dependent questions, record:

- Current controlling authority
- Exact regulation/document identifier
- Exact article, paragraph, section, or learning objective
- Edition or amendment
- Effective date
- Access date
- Jurisdiction and operational scope
- Verification reviewer and date

Regulatory status values:

- `current_verified`
- `current_pending_second_review`
- `outdated_but_corrected`
- `historical_reference_only`
- `superseded`
- `jurisdiction_uncertain`
- `quarantined`
- `rejected`

Only `current_verified` may become active for regulation-dependent material.

For technical and calculation questions:

- Recalculate independently.
- Record formulas, assumptions, units, rounding, and steps.
- Confirm that one and only one option is defensible.
- Require a second check for safety-critical, regulatory, and multi-step calculation questions.

## 11. Images, figures, charts, and tables

Every media-dependent question must contain structured image fields, including:

- `image_required`
- `image_answer_dependency`
- `image_id`
- `image_status`
- `image_pdf_page`
- `image_position`
- `image_path` or approved URL
- `image_source_title`
- `image_source_location`
- `image_license`
- `image_copyright_status`
- `image_attribution`
- `image_alt_text`
- `image_caption`
- `image_width` and `image_height`
- `image_annotations`
- `image_hotspots`
- `image_verified`
- `image_accessibility_verified`

The extraction process must preserve labels, legends, scale, orientation, color meaning, units, and every visual fact needed to answer the question.

Commercial textbook figures must not be published without permission. If a replacement is created, it must be independently drawn, technically reviewed, and must not imitate protectable design elements unnecessarily.

An image-dependent question is blocked unless `image_status=ready`, rights are approved, the media file exists, and both technical and accessibility verification are complete.

## 12. Canonical question record

Preserve the established PilotQuest fields and add the following mandatory audit fields:

```json
{
  "source_id": "",
  "source_record_id": "",
  "source_pdf_filename": "",
  "source_page": null,
  "source_question_number": "",
  "source_answer_page": null,
  "original_question_text": "",
  "original_choices": [],
  "original_stated_answer": "",
  "original_explanation": "",
  "extraction_method": "native_text|ocr|manual",
  "extraction_confidence": null,
  "answer_match_confidence": null,
  "ocr_uncertainties": [],
  "regulatory_status": "",
  "source_effective_date": "",
  "source_accessed_date": "",
  "rights_record_id": "",
  "technical_review_status": "pending|passed|failed",
  "regulatory_review_status": "pending|passed|failed|not_applicable",
  "editorial_review_status": "pending|passed|failed",
  "media_review_status": "pending|passed|failed|not_required",
  "duplicate_review_status": "pending|passed|failed",
  "question_version": 1,
  "supersedes_question_id": "",
  "superseded_by_question_id": "",
  "duplicate_group_id": "",
  "similarity_score": null,
  "active_study_bank": false
}
```

Imported unknown fields must not be silently dropped. Preserve them in `source_payload` or report them as a blocking schema issue until mapped deliberately.

## 13. Deduplication policy

Do not rely only on 0.85 word overlap. Use layered detection:

1. Normalized exact-text hash
2. Choice-independent stem comparison
3. Token and character similarity
4. Semantic similarity
5. Numerical-template comparison
6. Translation and cross-language comparison
7. Image hash and perceptual-image similarity
8. Learning-objective and scenario comparison

Deduplication must run within the batch, within the same track, across licences, and across authorities. A cross-authority match is flagged for review, not automatically merged.

## 14. Answer-choice handling

Deterministic shuffling is permitted only after extraction and verification. Preserve the original order in the source record.

When shuffling:

- Remap the correct-answer label.
- Remap every incorrect-answer explanation.
- Remap image hotspots or option-linked annotations.
- Revalidate grammar and references such as “the option above.”
- Store the shuffle algorithm version and seed.

Answer-letter imbalance is a reporting signal, not proof that reshuffling is required.

## 15. Activation gate

Activation is calculated per record. A question may be active only when all applicable conditions are true:

- Extraction is complete and unambiguous.
- Answer-key matching is confirmed.
- Authority, jurisdiction, licence, category, and syllabus version are known.
- One learning objective is mapped.
- One defensible answer is technically verified.
- Regulation-dependent content is `current_verified`.
- Primary-source citation is sufficiently precise.
- Provenance is usable.
- Rights review permits the intended use.
- Required calculations are independently checked.
- Required media is ready, cleared, technically verified, and accessible.
- Duplicate review passed.
- Editorial review passed.
- No blocking quality flags remain.
- `verified=true`.

There is no `--allow-red-flags` route to active publication. Overrides may import a record into quarantine, never directly into an active view.

## 16. View policies

### Application and exam views

Contain only active records that pass the complete activation gate.

### Flashcard view

May include verified concept-recall material, but not unverified regulations, restricted wording, unresolved figures, or incorrect/ambiguous answers.

### Reels view

Requires commercial-use permission, current verification, no unresolved image dependency, concise wording, and no pending review. A publication ledger must prevent accidental reuse.

### Review view

Contains every quarantined, pending, historical, superseded, restricted, or rejected item with explicit reasons and required next action.

Student-facing labels such as `reviewPending` do not make an unverified question acceptable. Pending regulatory material must be excluded from student study and exam views.

## 17. Safer import commands

The injector should support separate operations:

```bash
# Register and extract only; never publishes
python3 scripts/ingest_pdf.py inbox/source.pdf --extract

# Import structured extraction into quarantine
python3 scripts/inject_questions.py inbox/batch.jsonl --apply --status quarantined

# Run automated checks and build review queues
python3 scripts/validate_questions.py data/ quarantine/
python3 scripts/detect_duplicates.py data/ quarantine/
python3 scripts/validate_media.py media/ data/ quarantine/
python3 scripts/check_regulatory_currency.py data/ quarantine/

# Publish only individually approved records that pass computed gates
python3 scripts/release_questions.py --approval-file reviews/approved_records.csv

# Rebuild derived outputs
python3 scripts/categorize.py --write
python3 scripts/build_views.py
```

`release_questions.py` must recompute every gate and refuse records with unresolved failures. An approval file cannot override failed gates.

## 18. Batch report

Every PDF batch report must state:

- Pages inspected and pages processed
- Questions detected and extracted
- Answers matched and unmatched
- OCR uncertainties
- Original figures detected and extracted
- Figures awaiting recreation or permission
- Current verified questions
- Corrected outdated questions
- Historical/superseded questions
- Quarantined and rejected questions
- Restricted questions
- Exact and near duplicates
- Learning objectives covered and missing
- Active records released
- Sources and provisions used for verification
- Files created or changed
- Items requiring qualified instructor or regulatory review

The total extracted count must never be presented as the usable or active count.

## 19. Immediate migration decisions

Apply these decisions now:

1. Set the 230 provision-pending EASA Air Law questions to `quarantined` and remove them from app, exam, flashcard, and reel views until individually cleared.
2. Keep the 40 fully provision-checked Air Law questions active only if their effective-date, source, rights, and media gates also pass.
3. Keep the 680 weak-distractor FAA items flashcard-only only after technical, source, rights, and currency review; otherwise quarantine them. Rewrite their distractors before exam use.
4. Exclude the 84 non-commercial Transport Canada questions from every commercial or promotional output unless commercial permission is documented.
5. Recalculate the manifest after these changes. Report separately: extracted, canonical, active exam, active flashcard, quarantined, restricted, historical, and rejected counts.

## 20. Definition of done

A PDF batch is complete only when every detected question, answer-key entry, explanation, and question-dependent image is accounted for as active, quarantined, restricted, historical, superseded, or rejected—with a recorded reason and next action.

Completeness means full accounting and traceability. It does not mean publishing every extracted question.

## 21. Amendment — study tier (owner decision, 2026-10-05)

PilotQuest is study and practice material. It does not guarantee that any question appears in an examination or that a student will pass. On that basis the owner decided that a record may be published in a **study tier** before it completes the full verified-tier gate in section 15.

**Never relaxed in either tier:** rights (section 8; the 950 Jeppesen-derived and 116 Transport Canada records stay blocked), provenance, one defensible answer confirmed by a recorded per-record technical review, editorial review, required media (section 11), duplicate review, and blocking quality flags.

**Relaxed in the study tier only:**

- Exactly one *official* learning-objective code (topic and chapter mapping is sufficient).
- Syllabus version (`classification_optional_fields`).
- The second independent check for calculation, safety-critical and regulation-dependent items.
- Regulation-dependent items may publish at `current_pending_second_review`. That status still requires a first check against current controlling text fetched at review time, with the provision, edition and access date recorded. Memory is never enough.
- Hold reasons that concern documentation rather than correctness (`study_tier.nonblocking_hold_reason_substrings`).

**Student-facing labelling:** every app record carries `publicationTier` and `studyNotice`. Study-tier regulation-dependent records also carry `regulatoryNotice` ("Rules change and differ by State. Check the current regulation before relying on this answer."). Reels use study-tier records only when they are not regulation-dependent.

A study-tier record is promoted to the verified tier automatically once its remaining gates pass. Configuration lives in `taxonomy/policy.json` → `study_tier`. This amendment overrides section 16's exclusion of pending regulatory material for the study tier only.
