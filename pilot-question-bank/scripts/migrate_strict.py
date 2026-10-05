#!/usr/bin/env python3
"""
migrate_strict.py — One-time migration of the existing bank to the strict
ingestion & publishing guide (PilotQuest_Strict_PDF_Ingestion_and_Publishing_Guide.md).

    python3 scripts/migrate_strict.py            # dry run: report only
    python3 scripts/migrate_strict.py --write

What it does, per record (nothing in the question/answer content changes):
  * adds the section 12 audit fields, filling them ONLY from evidence that
    already exists (source_location, batch logs, raw source files, audit v2);
    anything without per-record evidence is left `pending`
  * links each record to its raw source record (original wording, choices,
    stated answer, page) where the raw file is still on disk
  * restores the source's original subject label where categorize.py relabelled it
  * converts earlier quarantine decisions into explicit hold_reasons
  * applies the section 19 migration decisions
  * recomputes status with gates.py and moves non-active records to quarantine/
  * writes sources/source_manifest.json and appends to reports/audit_log.jsonl
Idempotent: a second --write changes nothing.
"""
import argparse
import collections
import datetime
import glob
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402
import gates  # noqa: E402
import dedupe  # noqa: E402

ROOT = taxonomy.ROOT
WS = os.path.dirname(ROOT)  # pilot_training/
TODAY = datetime.date.today().isoformat()
BACKUP = os.path.join(ROOT, "backups", "pre_reorg_2026-10-05", "data")
AUDIT_DIR = os.path.join(WS, "JAA-Sets", "Current_EASA_Air_Law_Audit_v2_2026-09-14")

# ---------------------------------------------------------------- sources ----
SOURCES = {
    # source_id: (raw file relative to pilot_training/ or None, title, publisher, url, rights_record_id, notes)
    "SRC-FAA-PAR-SAMPLE": (None, "PAR - Private Pilot Airplane sample questions", "FAA",
                           "https://www.faa.gov/training_testing/testing/test_questions", "RR-FAA-SAMPLE-QUESTIONS",
                           "par_questions.pdf not retained locally; transcribed 2026-09-10/11"),
    "SRC-FAA-CAX-SAMPLE": (None, "CAX - Commercial Pilot Airplane sample questions", "FAA",
                           "https://www.faa.gov/training_testing/testing/test_questions", "RR-FAA-SAMPLE-QUESTIONS", "PDF not retained"),
    "SRC-FAA-FIA-SAMPLE": (None, "FIA - Flight Instructor Airplane sample questions", "FAA",
                           "https://www.faa.gov/training_testing/testing/test_questions", "RR-FAA-SAMPLE-QUESTIONS", "PDF not retained"),
    "SRC-FAA-PRH-SAMPLE": (None, "PRH - Private Pilot Helicopter sample questions", "FAA",
                           "https://www.faa.gov/training_testing/testing/test_questions", "RR-FAA-SAMPLE-QUESTIONS", "PDF not retained"),
    "SRC-FAA-UAG-SAMPLE": (None, "UAG - Unmanned Aircraft General sample questions", "FAA",
                           "https://www.faa.gov/training_testing/testing/test_questions", "RR-FAA-SAMPLE-QUESTIONS", "PDF not retained"),
    "SRC-TC-TP13014": (None, "Civil Aviation Sample Examination - RPP/PPL(A) (TP 13014E)", "Transport Canada",
                       "https://tc.canada.ca/en/aviation/publications/civil-aviation-sample-examination-recreation",
                       "RR-TC-TP13014", "PDF not retained; answer key transcribed per record (source_location)"),
    "SRC-TC-TP877": (None, "Sample Examination - Glider Pilot Licence (TP 877E) 10th ed.", "Transport Canada",
                     "https://tc.canada.ca/en/aviation/publications/sample-examination-glider-pilot-licence-tp-8",
                     "RR-TC-TP877", "PDF not retained"),
    "SRC-TC-TP14454": (None, "Sample Examination - Pilot Permit Ultra-light Aeroplane (TP 14454E)", "Transport Canada",
                       "https://tc.canada.ca/en/aviation/publications/sample-examination-pilot-permit-ultra-light-",
                       "RR-TC-TP14454", "PDF not retained"),
    "SRC-USER-EASA-AIRLAW-270": ("JAA-Sets/Current_EASA_Air_Law_Audit_v2_2026-09-14/quarantined_270_review_set_230.jsonl",
                                 "User-supplied EASA ATPL Air Law 270 (short answer) + audit v2", "user-supplied", "",
                                 "RR-USER-BATCH-JEPPESEN-DERIVED",
                                 "originals split across quarantined_270_review_set_230.jsonl and active_current_core_40.jsonl"),
    "SRC-USER-FAA-GROUNDSCHOOL-680": ("datasets/Jeppesen_Private_Pilot_34_Sections_680_QA_2026-09-11.jsonl",
                                      "User-supplied FAA PPL ground-school 680 (short answer)", "user-supplied", "",
                                      "RR-USER-BATCH-JEPPESEN-DERIVED", "built on Jeppesen Private Pilot section structure"),
    "SRC-USER-POWERPLANT-280": ("JAA-Sets/Current_Powerplant_Outline_280_QA_2026-09-14/powerplant_280_QA.jsonl",
                                "User-supplied EASA ATPL Powerplant 280 (short answer)", "user-supplied", "",
                                "RR-USER-BATCH-STRUCTURE-ONLY", ""),
    "SRC-USER-NAV-266": ("datasets/navigation_ppl_cpl_qa/questions.jsonl",
                         "User-supplied PPL/CPL Navigation 266 (multiple choice)", "user-supplied", "",
                         "RR-USER-BATCH-STRUCTURE-ONLY", ""),
    "SRC-CONTRIB-FAA-PAR-15": (None, "User-contributed FAA PPL questions (Desktop JSONL, 2026-09-11)", "user-contributed",
                               "", "RR-CONTRIBUTOR-FAA-PAR-15", "raw file not retained"),
    "SRC-PROJECT-AUTHORED": (None, "Authored by this project", "project", "", "RR-PROJECT-ORIGINAL", ""),
}

FILE_SOURCE = [  # (path regex on relative file, source_id)
    (r"faa/par/en/official_sample", "SRC-FAA-PAR-SAMPLE"), (r"faa/cax/", "SRC-FAA-CAX-SAMPLE"),
    (r"faa/fia/", "SRC-FAA-FIA-SAMPLE"), (r"faa/prh/", "SRC-FAA-PRH-SAMPLE"), (r"faa/uag/", "SRC-FAA-UAG-SAMPLE"),
    (r"tp13014", "SRC-TC-TP13014"), (r"tp877", "SRC-TC-TP877"), (r"tp14454", "SRC-TC-TP14454"),
    (r"easa/atpl-a/air-law/en/original_syllabus_aligned_batch1", "SRC-USER-EASA-AIRLAW-270"),
    (r"groundschool", "SRC-USER-FAA-GROUNDSCHOOL-680"), (r"easa/atpl-a/powerplant", "SRC-USER-POWERPLANT-280"),
    (r"easa/atpl-a/(general|radio)-navigation", "SRC-USER-NAV-266"),
    (r"faa/par/en/original_syllabus_aligned_batch1", "SRC-CONTRIB-FAA-PAR-15"),
    (r".", "SRC-PROJECT-AUTHORED"),
]

HOLD_REASONS = [  # (predicate on previously-quarantined record, reason)
    (lambda q, rel: "easa/ppl-a/air-law" in rel, "regulation paragraph citations not independently re-verified (unresolved_issues #9)"),
    (lambda q, rel: "uk-caa" in rel, "CAP 1298 (2015) currency as UK PPL(A) syllabus unconfirmed (unresolved_issues #13)"),
    (lambda q, rel: "sacaa" in rel, "SACAA syllabus citation conflict unresolved (unresolved_issues #2)"),
    (lambda q, rel: "navigation" in rel, "requires an original diagram; extracted textbook figure may not be published"),
    (lambda q, rel: "Air Traffic Advisory" in (q.get("chapter_title") or ""), "legacy / State-AIP-dependent chapter (contributor self-flagged)"),
    (lambda q, rel: "faa/par" in rel, "judgment-based ADM scenario with no official key; instructor review needed"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(t):
    return re.sub(r"\W+", " ", (t or "").lower()).strip()


def load_raw():
    """{source_id: {normalized stem: raw record}}"""
    raw = collections.defaultdict(dict)
    files = {"SRC-USER-EASA-AIRLAW-270": [os.path.join(AUDIT_DIR, "quarantined_270_review_set_230.jsonl"),
                                          os.path.join(AUDIT_DIR, "active_current_core_40.jsonl")]}
    for sid, spec in SOURCES.items():
        if spec[0] and sid not in files:
            files[sid] = [os.path.join(WS, spec[0])]
    for sid, paths in files.items():
        for p in paths:
            if not os.path.exists(p):
                continue
            for line in open(p, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    r["_raw_file"] = os.path.relpath(p, WS)
                    raw[sid][norm(r.get("question_text") or r.get("stem"))] = r
    return raw


def backup_subjects():
    out = {}
    for p in glob.glob(os.path.join(BACKUP, "**", "*.jsonl"), recursive=True):
        for line in open(p, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                out[r["question_id"]] = (r.get("subject"), r.get("status"))
    return out


def provision(ref):
    m = re.findall(r"(14 CFR (?:§\s*)?\d+\.\d+[a-z0-9()]*|SERA\.\d+[a-z0-9()]*|FCL\.\d+|CAR \d+\.\d+|Article \d+)", ref or "")
    return "; ".join(dict.fromkeys(m))


def migrate(q, rel, raw, prior):
    sid = next(s for pat, s in FILE_SOURCE if re.search(pat, rel))
    src = SOURCES[sid]
    q.setdefault("source_id", sid)
    q.setdefault("rights_record_id", src[4])
    loc = q.get("source_location") or ""
    official = q.get("provenance") in ("official_sample", "official_released")

    # --- raw-source linkage (immutable originals) ---
    r = raw.get(sid, {}).get(norm(q["question_text"]))
    if "source_record_id" not in q:
        q["source_record_id"] = (r or {}).get("question_id") or (r or {}).get("id") or ""
    if "original_question_text" not in q:
        if r:
            opts = r.get("options") or [c.get("text") for c in r.get("choices", [])]
            q["original_question_text"] = r.get("stem") or r.get("question_text")
            q["original_choices"] = opts or []
            q["original_stated_answer"] = (opts[r["correct_option_index"]] if "correct_option_index" in r
                                           else r.get("correct_answer", ""))
            q["original_explanation"] = r.get("explanation", "")
            q["source_page"] = r.get("source_pdf_page") or r.get("source_page_start")
            q["source_raw_file"] = r["_raw_file"]
        else:
            # transcribed official items and project-authored items: the record IS the original
            q["original_question_text"] = q["question_text"]
            q["original_choices"] = [c["text"] for c in q.get("choices", [])]
            q["original_stated_answer"] = (q["correct_answer"] if sid.startswith("SRC-TC") else "")
            q["original_explanation"] = "" if official else q.get("explanation", "")
            q["source_page"] = None
            q["source_raw_file"] = ""
    m = re.search(r"Question (\d+)", loc)
    q.setdefault("source_question_number", m.group(1) if m else "")
    m = re.search(r"Answer Key p\.(\d+)", loc)
    q.setdefault("source_answer_page", int(m.group(1)) if m else None)
    q.setdefault("source_pdf_filename", (re.match(r"([\w ]+?\.pdf|TP \d+E PDF)", loc) or [""])[0] if official else "")
    q.setdefault("extraction_method", "native_text" if official else "manual")
    q.setdefault("extraction_confidence", None)
    q.setdefault("ocr_uncertainties", [])
    q.setdefault("source_has_answer_key", sid.startswith("SRC-TC"))
    q.setdefault("answer_match_confidence", 1.0 if sid.startswith("SRC-TC") and q["source_answer_page"] else None)
    if sid in ("SRC-USER-NAV-266",) or "groundschool" in rel or rel.endswith("air-law/en/original_syllabus_aligned_batch1.jsonl") \
            or "powerplant" in rel:
        q.setdefault("shuffle_algorithm", "md5(question_id) mod n -> correct-answer position; v1 (batches 11/13/14)")
        q.setdefault("shuffle_seed", q["question_id"])

    # --- source label preservation (rule 9: no silent overwrite) ---
    old_subject, old_status = prior.get(q["question_id"], (q.get("subject"), q.get("status")))
    if old_subject != q.get("subject"):
        q.setdefault("source_subject_label", old_subject)

    # --- review statuses: only from per-record evidence ---
    cs = q.get("copyright_status", "")
    faa_sample = sid.startswith("SRC-FAA") and official
    audit40 = q["question_id"] in AUDIT40
    if "technical_review_status" not in q:
        if faa_sample and "judgment-based" not in cs:
            q["technical_review_status"] = "passed"
            q["technical_review_evidence"] = ("answer independently determined per record from the cited "
                                              "regulation/handbook (batches 3-8, 2026-09-10/11); see copyright_status")
        elif audit40:
            q["technical_review_status"] = "passed"
            q["technical_review_evidence"] = "EASA Air Law audit v2 (2026-09-14): checked against cited SERA provision family"
        else:
            q["technical_review_status"] = "pending"
    if "second_check_status" not in q:
        q["second_check_status"] = ("passed" if faa_sample and re.search(r"verified this session both by", cs)
                                    else "pending" if taxonomy.needs_second_check(q) else "not_required")
    q.setdefault("editorial_review_status", "pending")
    reg = taxonomy.regulation_dependent(q)
    if "regulatory_status" not in q:
        if not reg:
            q["regulatory_status"], q["regulatory_review_status"] = "", "not_applicable"
        elif q["question_id"] in AUDIT230:
            q["regulatory_status"], q["regulatory_review_status"] = "quarantined", "pending"
        elif audit40 or (faa_sample and provision(q.get("regulation_reference"))):
            q["regulatory_status"], q["regulatory_review_status"] = "current_pending_second_review", "pending"
        else:
            q["regulatory_status"], q["regulatory_review_status"] = "quarantined", "pending"
            q.setdefault("regulatory_note", "no current-law verification on record at provision level")
    q.setdefault("regulation_provision", provision(q.get("regulation_reference")))
    q.setdefault("source_effective_date", "")
    q.setdefault("source_accessed_date", "2026-09-14" if audit40 else (q.get("last_verified") if faa_sample else ""))

    # --- media fields (section 11) ---
    media = (q.get("media") or [None])[0]
    if media and "image_required" not in q:
        rights = "RR-FAA-AKTS-FIGURES" if "akts" in media["file_path"] else q["rights_record_id"]
        q.update({"image_required": True, "image_answer_dependency": "required", "image_id": os.path.basename(media["file_path"]),
                  "image_status": "ready", "image_pdf_page": None, "image_position": "",
                  "image_path": os.path.relpath(os.path.join(os.path.dirname(os.path.join(ROOT, "data", rel)), media["file_path"]), ROOT)
                  if not media["file_path"].startswith("data/") else media["file_path"],
                  "image_source_title": media.get("attribution", ""), "image_source_location": "",
                  "image_license": media.get("licence", ""), "image_rights_record_id": rights,
                  "image_copyright_status": media.get("licence", ""), "image_attribution": media.get("attribution", ""),
                  "image_alt_text": media.get("alt_text", ""), "image_caption": "", "image_width": None, "image_height": None,
                  "image_annotations": [], "image_hotspots": [], "image_verified": False,
                  "image_accessibility_verified": False})
        q.setdefault("media_review_status", "pending")
    elif old_status == "quarantined" and "navigation" in rel and "image_required" not in q:
        q.update({"image_required": True, "image_answer_dependency": "required", "image_status": "missing",
                  "image_verified": False, "image_accessibility_verified": False})
        q.setdefault("media_review_status", "pending")
    else:
        q.setdefault("image_required", False)
        q.setdefault("media_review_status", "not_required")

    # --- holds (earlier human quarantine decisions become explicit reasons) ---
    if "hold_reasons" not in q:
        q["hold_reasons"] = []
        if old_status == "quarantined" and q["question_id"] not in AUDIT230:
            q["hold_reasons"] = [next((why for pred, why in HOLD_REASONS if pred(q, rel)),
                                      "quarantined before migration; reason not recorded")]
    q.setdefault("question_version", 1)
    q.setdefault("supersedes_question_id", "")
    q.setdefault("superseded_by_question_id", "")
    return q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    global AUDIT40, AUDIT230
    a40 = {norm(json.loads(l)["question_text"]) for l in open(os.path.join(AUDIT_DIR, "active_current_core_40.jsonl")) if l.strip()}
    files = taxonomy.load_logical_files()
    AUDIT40 = {q["question_id"] for rs in files.values() for q in rs
               if q["question_id"].startswith("EASA-ATPLA-AL") and norm(q["question_text"]) in a40}
    AUDIT230 = {r for r, fl in taxonomy.AUDIT_FLAGS.items() if "audit_v2_pending_provision_review" in fl}
    raw, prior = load_raw(), backup_subjects()

    before = collections.Counter()
    all_recs = []
    for rel, recs in files.items():
        for i, q in enumerate(recs):
            before[q.get("status")] += 1
            src_file = q.get("_source_file")
            q = taxonomy.categorize(q)
            q["_source_file"] = src_file
            recs[i] = migrate(q, rel, raw, prior)
            all_recs.append(recs[i])

    dup, _ = dedupe.review_status(all_recs)
    log, after = [], collections.Counter()
    for q in all_recs:
        st, sim, gid = dup[q["question_id"]]
        q["duplicate_review_status"], q["similarity_score"], q["duplicate_group_id"] = st, sim, gid
        old = q.get("status")
        ev = gates.apply(q)
        after[q["status"]] += 1
        log.append({"date": TODAY, "question_id": q["question_id"], "process": "migrate_strict.py",
                    "from_status": old, "to_status": q["status"], "pipeline_state": q["pipeline_state"],
                    "result": "active" if q["status"] == "active" else "held",
                    "evidence": {k: v[1] for k, v in ev["gates"].items() if not v[0]},
                    "notes": "strict-guide migration (section 19)"})

    print(f"records: {len(all_recs)}  before: {dict(before)}  after: {dict(after)}")
    print("pipeline states:", dict(collections.Counter(q["pipeline_state"] for q in all_recs)))
    print("first failing gate:", dict(collections.Counter((q["gate_failures"] or ["none"])[0] for q in all_recs)))
    if not args.write:
        print("dry run; use --write")
        return

    manifest = {}
    for sid, (path, title, pub, url, rr, notes) in SOURCES.items():
        full = os.path.join(WS, path) if path else None
        manifest[sid] = {"source_id": sid, "title": title, "publisher": pub, "url": url, "rights_record_id": rr,
                         "raw_file": path or "", "sha256": sha256(full) if full and os.path.exists(full) else None,
                         "notes": notes, "registered": TODAY}
    with open(os.path.join(ROOT, "sources", "source_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
    taxonomy.place(files)
    with open(os.path.join(ROOT, "reports", "audit_log.jsonl"), "a", encoding="utf-8") as f:
        for e in log:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print("written: data/ (active) + quarantine/ (held), sources/source_manifest.json, reports/audit_log.jsonl")


if __name__ == "__main__":
    main()
