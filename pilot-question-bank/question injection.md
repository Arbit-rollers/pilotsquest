# Question Injection Guide

How the PilotQuest question bank is organized, how every question is categorized, and how to add new questions without breaking anything.

Last reorganized: 2026-10-05 (1,916 questions, 21 source files).

---

## 1. The bank's three layers

```
pilot-question-bank/
├── data/        MASTER COPY. One JSONL file per authority/licence/subject/batch.
│                The only place questions are stored. Never edited by hand
│                except to fix content; always edited through the scripts.
├── taxonomy/    THE RULES. Plain JSON/CSV files that decide how every question
│                is categorized. To change a category, change a rule here,
│                not the question.
├── views/       GENERATED OUTPUTS. One folder per purpose (app, study, reels,
│                review). Deleted and rebuilt on every build. Never edit it.
├── inbox/       DROP ZONE for new batches. Processed files move to inbox/processed/.
├── scripts/     categorize.py · build_views.py · inject_questions.py
│                + the older validate_questions.py · detect_duplicates.py · export_database.py
└── backups/pre_reorg_2026-10-05/   untouched copy of data/ from before this reorganization
```

Rule of thumb: **content lives in `data/`, decisions live in `taxonomy/`, and every output is generated.** If two consumers (the app and the reels) need the same question in different shapes, they each get it from `views/`. Nobody keeps a copy of their own.

---

## 2. How every question is categorized

The authority's own wording (`subject`, `subject_code`, `licence`, `aircraft_category`) is **never** rewritten, because a student sitting an FAA test must see FAA terms and an EASA student must see EASA terms. On top of that, `scripts/categorize.py` adds a normalized layer so that questions from all authorities can be studied, filtered and reported together:

| Field | What it means | Decided by |
|---|---|---|
| `topic` / `topic_name` | One of 15 cross-authority study areas (table below) | `taxonomy/subject_rules.csv`, then `taxonomy/topic_overrides.csv` |
| `topic_source` | `rule`, `override` or `explicit` (contributor set it) | — |
| `track_id` | The licence a question was written for, e.g. `EASA:ATPL(A)`, `FAA:PAR`, `TC:GPL` | `taxonomy/licences.json` |
| `licence_level` | recreational · private · commercial · airline_transport · instructor · remote_pilot | `taxonomy/licences.json` |
| `aircraft_class` | aeroplane · helicopter · glider · ultralight · uas | `taxonomy/licences.json` |
| `applicable_licences` | **Every** track the question is valid study material for | own track + `taxonomy/applicability.csv` + built-in EASA rules |
| `chapter_title` | Chapter/section within the subject (used for learning-map levels) | source, or backfilled from `subject` |
| `question_style` | `exam_style` (real exam format) or `concept_recall` (templated recall item) | `scripts/taxonomy.py` |
| `quality_flags` | Open issues: `quarantined`, `needs_figure`, `templated_distractors`, `non_commercial_licence`, `audit_v2_pending_provision_review`, `missing_calculation_steps` | `scripts/taxonomy.py` + `taxonomy/review_flags.csv` |

### The 15 study areas

Modelled on the EASA/ICAO subject split, because it is the most detailed scheme in use and FAA, Transport Canada, SACAA and UK CAA subjects all map onto it cleanly.

| Topic | EASA | Questions (usable) | What goes here |
|---|---|---|---|
| `AIR_LAW` | 010 | 596 (578) | Licensing, rules of the air, airspace, ATS, aerodromes & markings, signals, SSR codes, registration, airworthiness rules, security, accident reporting, drone regulations |
| `AGK_AIRFRAME_SYSTEMS` | 021 | 22 (22) | Structure, controls, gear, hydraulics, electrics, cabin heat/CO |
| `AGK_POWERPLANT` | 021 | 308 (308) | Piston & turbine engines, ignition, carburettor icing, fuel, propellers |
| `INSTRUMENTS` | 022 | 31 (31) | Pitot-static, gyros, compass errors, EFIS, ASI markings |
| `MASS_BALANCE` | 031 | 22 (22) | Weight, CG, loading |
| `PERFORMANCE` | 032 | 30 (30) | Density altitude, take-off/landing distance, crosswind component, glide |
| `FLIGHT_PLANNING` | 033 | 62 (62) | Cross-country planning, fuel, NOTAM/briefing sources |
| `HUMAN_PERFORMANCE` | 040 | 101 (90) | Physiology, hypoxia, illusions, scanning, alcohol, fatigue, ADM, hazardous attitudes, CRM |
| `METEOROLOGY` | 050 | 194 (184) | Atmosphere, stability, fronts, icing, thunderstorms, METAR/TAF, winds aloft |
| `GENERAL_NAVIGATION` | 061 | 241 (227) | Earth, direction, time, charts, DR, wind triangle, 1-in-60, flight computer |
| `RADIO_NAVIGATION` | 062 | 152 (144) | NDB/ADF, VOR, DME, GNSS/RAIM |
| `OPERATIONAL_PROCEDURES` | 070 | 40 (40) | Wake turbulence, wind shear technique, emergencies, contaminated runways, towing/launch |
| `PRINCIPLES_OF_FLIGHT` | 080 | 91 (91) | Lift/drag, stalls, load factor, V-n, stability, ground effect, rotor aerodynamics |
| `COMMUNICATIONS` | 090 | 25 (25) | RT phraseology, radio procedures, comm failure |
| `INSTRUCTION` | — | 1 (1) | Fundamentals of instruction (instructor licences only) |

The weakest areas (Mass & Balance, Performance, Instruments, Airframe/Systems, Communications, Operational Procedures, Instruction) are where new batches will add the most value. Run `python3 scripts/categorize.py --report` for the live topic × licence table.

### Corrections made in this reorganization

- **Every question now has a study area.** Before, "subject" meant five different things: EASA numbers (`010`), FAA ACS codes (`PA-I-C`), FAA test codes (`PLT088`), textbook chapter codes (`CH04B`) and free text (`General / Aeronautics`).
- **Mixed-subject sources were split question by question.** For example, the Transport Canada "Aeronautics – General Knowledge" set mixes carburettor icing, hypoxia, altimeters and wake turbulence; each question is now in its correct area (`taxonomy/topic_overrides.csv` records why).
- **21 FAA subject labels fixed.** Their Area-of-Operation name contradicted their own ACS code. For example, `PA-IX-C` was labelled "Basic Instrument Maneuvers" (Area IX is *Emergency Operations*), and `UA-III-*` was labelled "Operations" (Area III is *Weather*).
- **6 FAA questions moved to the right area.** Load factor was filed as "Performance", pitot/static blockage as "Aircraft Systems", and VFR cruising altitudes and preflight action (both regulations) as "Navigation" and "Planning".
- **Licence applicability made explicit.** The 266 navigation questions came from a PPL/CPL package but were filed only under ATPL(A), and powerplant piston chapters and most Air Law chapters are PPL syllabus too. EASA:PPL(A) students now see **548** relevant questions instead of 0. EASA:CPL(A) gets the full 010/021/061/062 set.
- **The 680 templated FAA ground-school questions were reclassified as `concept_recall`.** Their wrong answers are true statements about *other* topics ("What is a NOTAM?" with a VOR fact as a distractor), so a student can pick the right answer by matching the topic. That makes them good flashcards and poor exam practice, so they are now **flashcards only**.
- **84 Transport Canada questions flagged `non_commercial_licence`.** The Crown copyright on TP 13014/TP 14454 allows only non-commercial reuse. They are excluded from reels (which promote PilotQuest) and marked `nonCommercialOnly` in the app feed.
- **230 EASA ATPL Air Law questions flagged `audit_v2_pending_provision_review`.** Your own audit (`JAA-Sets/Current_EASA_Air_Law_Audit_v2_2026-09-14/AUDIT_REPORT.md`) keeps only 40 of that batch's 270 as fully provision-checked, but the bank has been serving 260 as active. They stay active for now (see §7), are marked `reviewPending` in the app, are listed in the review queue, and are kept out of reels.

---

## 3. What each purpose gets (`views/`)

Built by `python3 scripts/build_views.py`. The policy settings (which flags block what) are at the top of that script.

| View | Path | Who uses it | What's in it |
|---|---|---|---|
| **App feed** | `views/app/questions.jsonl` | PilotQuest Step 2/3 (DB seed) | Every usable question in the app's `FullQuestionRecord` camelCase shape, plus `trackId`, `applicableTracks`, `topic`, `modes` (`exam`/`flashcard`), `reviewPending`, `nonCommercialOnly`. **1,855 questions: 1,175 exam + flashcard, 680 flashcard only.** |
| **Learning map** | `views/app/catalog.json` | App learning map / level unlocks | track → topic → chapter → question counts |
| **Exam practice** | `views/study/exam/<track>/<topic>.jsonl` | Mock exams, topic drills | Exam-style questions only, sorted easy → hard |
| **Flashcards** | `views/study/flashcards/<track>/<topic>.jsonl` | Spaced repetition | `front` / `back` / `explanation` / `reference` |
| **Reels** | `views/reels/candidates.csv` (and `.jsonl`) | `create-aviation-clips` skill | **477** ranked questions that fit the 16:9 board: single-choice, no figure, question ≤ 140 characters, options ≤ 70 characters, commercial-safe, not yet used. Score favours PPL-level, short, official-sample, visual topics. Includes a ready `tag_line`. |
| **Review queue** | `views/review/queue.csv` (and `.jsonl`) | Instructor review | **281** items: quarantined, missing figure, or pending audit, with reason flags |
| **Manifest** | `views/MANIFEST.json` | Sanity check | Counts per view and build date |

**Reels ledger:** after publishing a reel, add a line to `taxonomy/reels_used.csv` (`question_id,date_used,reel_folder`) and rebuild. That question then drops out of the candidates, so a question is never posted twice. The reels skill previously only *noted* the ID in `~/pilots_quest`; this ledger is what actually enforces it.

---

## 4. Injecting new questions: quick start

```bash
cd pilot-question-bank

# 1. Drop the batch in the inbox (JSONL or CSV)
cp ~/Downloads/met_batch.jsonl inbox/

# 2. (optional) fields shared by every record in the batch
cp inbox/EXAMPLE.defaults.json inbox/met_batch.defaults.json   # edit it

# 3. Dry run: nothing is written
python3 scripts/inject_questions.py inbox/met_batch.jsonl --defaults inbox/met_batch.defaults.json

# 4. READ the answer sample it prints. Fix whatever it reports. Re-run until clean.

# 5. Apply
python3 scripts/inject_questions.py inbox/met_batch.jsonl --defaults inbox/met_batch.defaults.json \
    --apply --activate --provenance-reviewed "read 15 answers across ch1-6, recalculated 3 lapse-rate items; no textbook text"
```

`--apply` writes the new file into `data/`, validates the whole bank, rebuilds `views/`, logs the batch to `reports/injection_log.csv` and moves the inbox files to `inbox/processed/`. Then add a short batch entry to `reports/progress.md`, as for every batch before.

### What the script does, in order

1. **Load.** Reads JSONL, or CSV in `schemas/import_template.csv` format. It also maps the field names other generators use: `stem`/`question`→`question_text`, `options` (list)→`choices` with A/B/C/D, `correct_option_index`→letter, an answer given as text→its letter, `easy/medium/hard`→`beginner/intermediate/advanced`, `multiple_choice_single_answer`→`single_choice`.
2. **Defaults.** Fills in any field from `--defaults` that a record doesn't already have.
3. **Screen.** Flags commercial-textbook names (Jeppesen, Oxford, Gleim, Sporty's, Robson…), page or "Figure 3-2" citations, OCR junk, and fields like `textbook_source`/`book_chapter`. It also prints a **random sample of question + correct answer that you must actually read** (the standing provenance rule: the provenance label proves nothing; the answer text does). Red flags block `--apply` unless you pass `--allow-red-flags` after checking.
4. **IDs.** Assigns `AUTHORITY-LICENCE-SUBJECT-NNNNNN`, continuing from the highest number already in the bank for that prefix. A contributor's own ID is kept in `source_record_id`. For a subject new to the bank, pass `--id-prefix` (e.g. `EASA-ATPLA-MET`).
5. **Shuffle.** If more than 40 % of correct answers share one letter (generators love "A"), choices are reshuffled the same way every time (based on the question_id), with the wrong-answer explanations remapped to match.
6. **Classify.** Runs the same `taxonomy.categorize()` used for the whole bank, so injected questions are indistinguishable from existing ones.
7. **Dedupe.** Exact and near-duplicate (≥ 0.85 word-overlap similarity) check against the bank, within the same track and topic, and within the batch. Duplicates are skipped unless `--allow-duplicates`.
8. **Validate.** The same checks as `validate_questions.py` plus JSON-schema enums. `short_answer` records are rejected because the app serves multiple choice, so write 3 distractors first. Fields that aren't in the schema are dropped and listed.
9. **Route.** Writes to `data/<authority>/<licence>/[<subject>/]<lang>/<provenance>_batch<N>[_label].jsonl`, next to existing files of the same licence and subject, or into a new subject folder. One file per batch, and **provenance classes are never mixed in one file**.
10. **Publish.** Status is `quarantined` by default. `--activate` makes a record `active` only if its provenance is usable, `reuse_allowed` is true, it is not a duplicate, and it has no `needs_figure`/`missing_calculation_steps` flag.

### Minimum record (JSONL)

```json
{"authority": "EASA", "licence": "ATPL(A)", "subject_code": "050", "subject": "Meteorology",
 "question_text": "In the ICAO Standard Atmosphere, what is the mean sea-level temperature?",
 "choices": [{"label":"A","text":"+15 °C"},{"label":"B","text":"0 °C"},{"label":"C","text":"+20 °C"},{"label":"D","text":"-15 °C"}],
 "correct_answer": "A",
 "explanation": "ISA at MSL: 1013.25 hPa and +15 °C, decreasing 1.98 °C per 1,000 ft to the tropopause.",
 "difficulty": "beginner", "provenance": "original_syllabus_aligned",
 "regulation_reference": "EASA LO 050 01 02",
 "source_title": "...", "source_url": "https://...", "copyright_status": "...",
 "reuse_allowed": true, "verified": true}
```

Optional fields that improve the record: `chapter_title`, `learning_objective(_code)`, `incorrect_answer_explanations` (`{"B": "why B is wrong", …}`), `calculation_steps` (required for calculation questions), `handbook_reference`, `tags`, `media` (for any question that shows a figure), `topic` (only to override the rules, which sets `topic_source: explicit`), and `question_style: "concept_recall"` for recall-only items.

---

## 5. Common situations

| Situation | What to do |
|---|---|
| **Error: `licence '…' is not in taxonomy/licences.json`** | Add the licence (authority, code, level, aircraft class, `track_id`) to `taxonomy/licences.json`. |
| **Error: `no topic rule matches …`** | Add a line to `taxonomy/subject_rules.csv` (authority, subject-code regex, subject regex, topic) so future batches classify automatically, or set `topic` on the records. |
| **A question is in the wrong study area** | Add `question_id,topic,reason` to `taxonomy/topic_overrides.csv` → `python3 scripts/categorize.py --write && python3 scripts/build_views.py`. Don't edit the record. |
| **Content applies to another licence too** | Add a row to `taxonomy/applicability.csv` (e.g. ATPL chapter → PPL track) and re-run categorize + build. |
| **A whole batch needs holding pending review** | Add `question_id,flag,reason` rows to `taxonomy/review_flags.csv`. To keep a flag out of student views, add it to `REVIEW_HOLD_FLAGS` in `build_views.py`. |
| **New authority or licence with no folder yet** | `--target-dir data/<authority>/<licence>/<subject>/en` and `--id-prefix`. |
| **Question needs a chart/diagram** | Put a cleared image (public domain or self-drawn, **never** a textbook page) in `media/` next to the JSONL, and add a `media` entry. Without one, the question is flagged `needs_figure` and stays out of exams. |
| **Batch arrives with a `textbook_source`/page citations** | Stop. Read the answer text in detail, compare against the source, and log the outcome in `reports/legal_and_provenance_notes.md` before anything goes in. Three past batches failed this check and two passed; only the text tells them apart. |
| **Fixing a typo in an existing question** | Edit the record in `data/`, then `python3 scripts/categorize.py --write && python3 scripts/build_views.py`. |

After any change to `taxonomy/` or `data/`, these two commands bring everything back in sync. They are safe to run as often as you like, and re-running them changes nothing.

```bash
python3 scripts/categorize.py --write      # re-derive categories (idempotent)
python3 scripts/build_views.py             # regenerate views/
python3 scripts/validate_questions.py "data/**/*.jsonl"
```

---

## 6. The instructor's quality bar for new questions

Treat these as acceptance criteria for any batch, generated or hand-written:

1. **One defensible correct answer.** If an examiner could argue for two options, rewrite the question. "Most correct" questions need the deciding condition stated in the question.
2. **Plausible distractors from the same concept.** Wrong options should be the mistakes students actually make (QNH vs QFE, 7600 vs 7700, true vs magnetic), in the same grammatical form and similar length as the right one. No "all/none of the above". No true-but-off-topic statements (that is exactly why the 680 ground-school items were downgraded to flashcards).
3. **Cite the controlling source.** Name the regulation paragraph, LO code or handbook chapter, not just "SERA" or "PHAK". Air Law without an exact provision ends up in the review queue.
4. **Calculations show working.** `calculation_steps` must be filled in, and the answer must be recalculated by a second person or tool before `--activate`.
5. **No hidden figure.** Never write "refer to the figure" without a `media` entry.
6. **Jurisdiction stated where rules differ.** If the answer is only true under one authority (cloud clearances, VFR minima, transponder rules), the question belongs to that authority's track only. Don't widen its applicability.
7. **Difficulty means exam level, not effort.** `beginner` = recall a single fact, `intermediate` = apply a rule or concept to a situation, `advanced` = a multi-step calculation or a judgment between competing considerations.
8. **Original wording.** Never copy, closely paraphrase or "lightly edit" commercial textbooks or test-prep products, and never ship their figures. Official samples are only reused within their licence terms (watch Transport Canada's non-commercial clause).

---

## 7. Decisions still open (owner's call)

1. **Hold the 230 audit-pending EASA Air Law questions?** Your audit v2 says only 40 of the 270 are fully provision-checked, but the bank currently serves 260. To follow the audit, set `HOLD_PENDING_REVIEW = True` in `scripts/build_views.py` and rebuild. They leave the app, exams and flashcards until each one is cleared (by removing its row from `taxonomy/review_flags.csv`).
2. **Is PilotQuest commercial?** If it is, the 84 `nonCommercialOnly` Transport Canada questions must be filtered out of the app (and Canadian students lose most of their exam content). This is the same open question noted in `reports/legal_and_provenance_notes.md`.
3. **The 680 FAA ground-school items:** keep them as flashcards only (current setting), or rewrite their distractors so they qualify as exam practice. FAA Private Pilot exam practice is only 56 questions until one of these is done.
