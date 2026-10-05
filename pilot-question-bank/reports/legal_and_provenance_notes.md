# Legal and Provenance Notes

Status: Batch 1 (research phase). Last updated 2026-09-10.

## Core policy

This project only classifies a question as usable (enters `v_usable_questions`) if:
1. `provenance_classification` is one of `official_released`, `official_sample`, `public_domain`, `open_licensed`, `original_syllabus_aligned`; AND
2. `reuse_allowed = TRUE`; AND
3. `status = 'active'` (i.e. it has passed human/regulatory review — nothing is auto-promoted from `quarantined`).

Everything discovered this batch is either (a) a *source record only* — no questions extracted — or (b) an original question authored from a public regulation, seeded with `status = quarantined` because the specific paragraph citations have not yet been independently re-verified by a live fetch/human reviewer this session. Nothing in this batch is live/active yet. See `research/coverage_report.csv`.

## The single most important licensing decision found this batch: Transport Canada TP 13014

Transport Canada publishes a genuine, official, government-authored sample examination (TP 13014, "Civil Aviation Sample Examination — Recreational Pilot Permit and Private Pilot Licence — Aeroplane") containing ~100 real multiple-choice questions with a full answer key, covering Air Law, Aeronautics, Meteorology and Navigation. This is the strongest `official_sample` candidate found across all 8 priority authorities.

However, the copyright notice on the publication (captured verbatim this session) reads:

> © Her Majesty the Queen in Right of Canada, represented by the Minister of Transport, 2005.
> "Transport Canada grants permission to copy and/or reproduce the contents of this publication for personal and **public non-commercial use**. Users must reproduce the materials accurately, identify Transport Canada as the source and not present theirs as an official version, or as having been produced with the help or the endorsement of Transport Canada."

**This is explicitly non-commercial-only.** Since this project's stated goal is an "international aviation study platform" (which may or may not be a commercial product), a decision is needed before any verbatim TP 13014 questions are ingested as `official_sample` with `reuse_allowed = true`:
- If the platform will be non-commercial / free-to-use with no monetisation, verbatim reuse with attribution appears permitted on the terms found.
- If the platform is or may become commercial, either (a) obtain explicit written permission from Transport Canada for commercial reuse, or (b) do not copy TP 13014 verbatim — instead use it only as a reference to write new `original_syllabus_aligned` questions in the platform's own wording.

The same caveat is provisionally applied to the other three TC sample-exam documents identified (TP 877 Glider, TP 13728 Private/Commercial Helicopter, TP 14454 Ultra-light) pending individual confirmation of their own copyright pages — see `research/copyright_audit.csv`.

## Confidential / restricted sources identified (do not scrape)

- **EASA European Central Question Bank (ECQB)** — the confidential theory-question bank used by EASA member-state exam authorities (and, per this batch's research, also drawn on by Türkiye's SHGM for its Part-FCL-aligned exams). Its existence is recorded; no content has been or should be extracted.
- **FAA live knowledge-test item bank** — the FAA explicitly states current knowledge-test questions are not released publicly; separate "sample question" PDFs are published for study and are a distinct, lower-stakes resource (see below).
- **CASA (Australia) theory exams** — confirmed as "closed tests"; the live item bank is not publicly released. Multiple commercial third-party sites claim to sell CASA-aligned or reconstructed questions — these are `restricted_do_not_use` / `third_party_reference_only` and must never be scraped.
- **SACAA-aligned commercial prep sites** — identified but not accessed.

## Public-domain material (strong basis for original questions)

FAA handbooks (e.g. Pilot's Handbook of Aeronautical Knowledge, FAA-H-8083-25 series) are U.S. federal government works and are public domain under 17 U.S.C. §105. This is the most legally unambiguous source category found this batch and should be prioritised as a citation basis for FAA-aligned `original_syllabus_aligned` questions in the next batch, once verbatim text has actually been fetched and read (not yet done this session — faa.gov blocked automated fetches with HTTP 403 on every URL tried).

## Regulation text vs. question wording

EU regulations (SERA — Regulation (EU) No 923/2012; Part-FCL — Regulation (EU) No 1178/2011) and equivalent national primary legislation are public law and may be cited, paraphrased, and used as the factual basis for original questions. This is distinct from copying an authority's own *document layout, commentary, or worked examples* (e.g. EASA's "Easy Access Rules" typographic compilation), which may carry separate terms not yet confirmed this session.

**Important caveat on the EASA seed batch created this session** (`data/easa/ppl-a/air-law/en/original_syllabus_aligned_batch1.jsonl`, 8 questions): the regulatory facts used (right-of-way rules, airspace classification, required documents, definition of night, semi-circular cruising levels) are well-established, stable aviation-law facts, but the *exact SERA/Part-FCL paragraph numbers* cited in `regulation_reference` were drawn from trained knowledge and were **not re-verified against a freshly fetched EUR-Lex page this session**. All 8 questions are therefore seeded with `verified: false` and `status: quarantined` pending a human or a follow-up-session regulatory check that confirms the exact paragraph citations before promotion to `status: active`.

## Recommendation

Before Phase 4 (large-scale extraction) proceeds: (1) resolve the TP 13014-class commercial/non-commercial licensing question with the platform owner, (2) obtain working PDF-text-extraction tooling (none was available in this environment this session — `poppler-utils` / `pdftotext` was not installed) so that genuine `official_sample` question text can actually be read and ingested rather than only cited, and (3) find a fetch path around FAA's bot protection (e.g. a different user agent/browser-based fetch) since faa.gov returned HTTP 403 to every automated request this session despite the URLs being real and publicly indexed.

## Incident log: pirated-textbook-adjacent source (2026-09-11)

A file was found in `sources/` (a folder outside this project's own defined structure, added directly by the user): a PDF of *Jeppesen Air Law: JAA ATPL Training* (2004), sourced from `libgen.li` — a shadow library that hosts copyrighted books without publisher/author permission. This was flagged to the user rather than used, consistent with the policy above (commercial, copyrighted, non-openly-licensed course material must not be used as a source).

The user then supplied a second file, `Current_EASA_Air_Law_270_QA_2026-09-11.jsonl` (270 `original_syllabus_aligned` Air Law questions), for integration. Before integrating, inspection showed every one of the 270 records cited that same Jeppesen PDF as `handbook_reference`, and the file's own 27-chapter organizational structure exactly mirrored that book's table of contents — evidence of derivation from the pirated textbook, regardless of the file's self-declared `copyright_status` ("original wording, no textbook passage reproduced"). This was flagged to the user, who confirmed the questions were in fact created through a different process and approved integration.

Resolution applied before ingestion (2026-09-11):
1. The Jeppesen PDF was deleted from the project (both the original and a renamed duplicate found in the same folder).
2. The `handbook_reference` field was stripped from all 270 records (the Jeppesen citation was inaccurate per the user's clarification, so removing it is correct regardless of the copyright question).
3. Content was spot-checked for factual accuracy across a spread of chapters — found accurate, standard, well-established ICAO/EASA Air Law facts at a definitional level.
4. The 10 records the source file itself flagged as `restricted_legacy_reference` (Chapter 18, Air Traffic Advisory Service — a largely superseded ICAO ATS classification) were kept `status: quarantined`, `reuse_allowed: false`.
5. Question IDs were renamed to fit this project's `AUTHORITY-LICENCE-SUBJECT-NNNNNN` convention; chapter metadata and the EASA/ICAO `regulation_reference` citations were otherwise preserved.

See `research/coverage_report.csv` (EASA / ATPL(A) row) for the full accounting. Result: `data/easa/atpl-a/air-law/en/original_syllabus_aligned_batch1.jsonl`, 270 questions (260 active, 10 quarantined) — first EASA ATPL(A) content in the bank.

## Incident log: second pirated-textbook-adjacent source (2026-09-11, same day)

A second file was supplied for integration: `Jeppesen_Private_Pilot_34_Sections_680_QA_2026-09-11.jsonl` (680 questions, `/Users/sam/Projects/apps/pilot_training/datasets/`). Same pattern as the EASA Air Law incident above, one step more explicit: every record carried a `textbook_source` field naming *"Jeppesen Private Pilot Manual / Private Pilot Textbook (2018 copy supplied by user)"* plus page-level `source_page_start`/`textbook_location` citations (e.g. "starts at 1-2"), and the file's 34-section structure mirrored that book's table of contents. A corresponding PDF — *Jeppesen - Private Pilot Manual Private Pilot Textbook (2018, Jeppesen) - libgen.li.pdf* — was found in a `books/` folder elsewhere in the project (outside this project's own structure) and deleted, consistent with the resolution already agreed for the Air Law incident.

Per the user's standing instruction to apply the same resolution: the `textbook_source`/`textbook_location` fields were stripped from all 680 records before ingestion, leaving only the legitimate FAA PHAK/AIM/eCFR `current_source_url` citations (now `source_url`). Content was spot-checked across a spread of chapters — all correct, standard, non-copyrightable definitional facts (e.g. "What is lift?", "What is density altitude?"). All 680 records were ingested `status: active` (no internally-self-flagged restricted subset in this file, unlike the Air Law batch's Chapter 18). Result: `data/faa/par/en/original_syllabus_aligned_batch2_groundschool.jsonl`.

## Incident log: third source — declined direct integration, authored fresh instead (2026-09-14)

The user pointed to `/Users/sam/Projects/apps/pilot_training/JAA-Sets/jaa_airlaw_3520/` — a folder containing `JAA_ATPL_Air_Law_176_sections_3520_QA.jsonl` (3,520 short-answer records, a 21-chapter/176-section JAA ATPL Air Law topic map recovered from a scanned manual), `section_inventory.json`, `image_manifest.json`, and 34 cropped diagram images (`images/*.jpg`), all built from the same Oxford Aviation/Jeppesen JAA ATPL 010 Air Law manual whose PDFs live in this project's `books/` folder (`JAA-ATPL-1-Airlaw.pdf`, `JAA_ATPL_10_OXFORD.pdf`). The user instructed not to delete any book files this time.

Unlike the two incidents above, this dataset was **not** just citing the book — inspection of a random sample showed a meaningful share of `correct_answer` text was either verbatim sentences lifted from the copyrighted textbook (e.g. *"The date, consisting of the day, month (by name) and year, must be the publication date or the effective date..."*) or raw OCR garbage/page-header fragments used as if they were answers (e.g. *"... ce cen eet n eens 12-1 12.2 TRAFFIC AND TAXI CIRCUITS 2.0.2..."*, or a bare table caption *"Table 4.5 Classification of Aircraft 4-3 AIR LAW AIRCRAFT NATIONALITY AND REGISTRATION MARKS..."*). Questions were mechanically templated around extracted noun-phrases rather than authored (e.g. *"What stated value or condition is associated with cen eet eens?"*). The dataset's own metadata self-flagged every one of its 3,520 records as `active_study_bank: false`, `verified: false`, with `copyright_status` explicitly stating *"requiring editorial paraphrase review before publication"* — i.e. the source itself was not claiming to be ready for use. The 34 image crops are excerpts of the commercial textbook's own diagrams (procedure-design figures etc.), a materially different copyright situation from the public-domain/government charts used elsewhere in the bank (Transport Canada GFA chart, FAA AKTS supplement figures).

This was flagged to the user with concrete examples rather than cleaned up and integrated (stripping a citation field would not fix verbatim-copied or garbled answer text). The user chose: (1) do not integrate the 3,520-record file's Q&A text at all; instead author entirely fresh original questions using `section_inventory.json`'s chapter/section titles only as a topic checklist (no book text reused, no book text even read beyond what was needed to confirm the quality problem), sourced against current ICAO/EASA/UK regulatory material; and (2) exclude the 34 textbook-page image crops entirely rather than embed them as question media.

Resulting batch: `data/easa/atpl-a/air-law/en/original_syllabus_aligned_batch3_jaa_topics.jsonl`, 102 fresh `single_choice` questions (IDs EASA-ATPLA-AL-000271–000372), covering the JAA topic map's chapters that go meaningfully deeper than the existing 270-question batch1: Continuing Airworthiness (ch3), PANS-OPS instrument procedure design (ch7 — departure/approach segments, track reversal, missed approach, circling, RNAV, holding, parallel-runway operations), Area Control (ch10), Approach Control including stacking and parallel-runway ops (ch11), Aerodrome Control radar procedures (ch12), aerodrome physical characteristics (ch14), aerodrome lighting systems (ch15), obstacles/RFFS/bird hazard (ch16), and a Facilitation supplement (ch17). The book PDFs and the JAA-Sets folder (JSONL, images, manifests) were left untouched, per instruction. See `research/coverage_report.csv` for the full accounting.

## Clean integration: navigation batch, same book-topic-map-only pattern as Powerplant (2026-09-17)

The user pointed to `/Users/sam/Projects/apps/pilot_training/datasets/navigation_ppl_cpl_qa/` — 266 original multiple-choice questions split across EASA subjects 061 (General Navigation, 178 questions) and 062 (Radio Navigation, 88 questions), the package's `README.md` stating it was "generated from the user-supplied 2021 David Robson navigation volume, then mapped to current EASA/SHGM-oriented subject areas."

This followed the same check-before-integrate diligence as every prior batch, and — like the Powerplant batch, unlike the three Jeppesen/JAA incidents above — **passed**:

1. **`currency_audit.md`** (included in the package) explicitly states the book was used for topic/chapter structure only, flags which content is jurisdiction-neutral core theory vs. Australian-CASA-specific material that must not be carried over as EASA/SHGM guidance, and notes outdated framing (legacy GPS-only presentation, imprecise UTC/GMT wording) that should not be reproduced uncritically.
2. Spot-checked ~12 questions across topics with **manual re-derivation of the underlying calculations** (1-in-60 rule track-error-plus-closing-angle, fuel-flow arithmetic, speed-distance-time, VOR radial-to-inbound-course reciprocal, chart-scale ground-distance conversion) — every one checked out correct, and none read as copied textbook prose (unlike the JAA Air Law 3,520 incident's OCR garbage/verbatim sentences).
3. **`images_manifest.json`** marks every one of the 17 extracted textbook-page reference images `"publish_directly": false`, `"usage": "redraw_reference_only"` — the package's own pipeline already enforces this project's standing policy. None of those images were shipped. The 22 questions (14 in 061, 8 in 062) that need a diagram were kept as real content but set `status: quarantined`, `reuse_allowed: false`, with no image field populated at all — they can be promoted once an original (non-derivative) diagram is drawn, consistent with how the FAA PAR ADM judgment question was quarantined-not-discarded in an earlier batch.

Cleanup applied before ingestion: renamed IDs to `EASA-ATPLA-NAV-NNNNNN` (061) / `EASA-ATPLA-RNAV-NNNNNN` (062); applied the same deterministic MD5-hash correct-answer-position shuffle used in prior conversions (the source data self-skewed ~45% of correct answers to position A); regulation_reference/source_title/source_url point to EASA's own Appendix 1 to FCL.025 (Subjects 061/062), not the source book. `scripts/detect_duplicates.py` flagged one near-duplicate pair within the new batch (`EASA-ATPLA-NAV-000123`/`000127`) — checked and confirmed a false positive: both are legitimate 1-in-60-rule drill questions with different numeric inputs and independently-verified-correct answers, the same templated-drill pattern already used throughout the bank's calculation content (e.g. the repeated "Fuel flow is X L/h for Y minutes" questions).

Result: `data/easa/atpl-a/general-navigation/en/original_syllabus_aligned_batch1.jsonl` (178 questions, 164 active / 14 quarantined) and `data/easa/atpl-a/radio-navigation/en/original_syllabus_aligned_batch1.jsonl` (88 questions, 80 active / 8 quarantined) — first EASA content of any kind for both subjects. See `research/coverage_report.csv` for the full accounting.
