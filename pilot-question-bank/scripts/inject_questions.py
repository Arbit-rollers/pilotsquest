#!/usr/bin/env python3
"""
inject_questions.py — Import a structured batch (JSONL/CSV) into QUARANTINE.

    python3 scripts/inject_questions.py inbox/batch.jsonl --defaults inbox/batch.defaults.json   # dry run
    python3 scripts/inject_questions.py inbox/batch.jsonl --defaults ... --apply \
        --provenance-reviewed "what you read in the intake sample"

Nothing this script does can make a record active. Every imported record
lands in quarantine/ with every review status `pending`; publication happens
only through scripts/release_questions.py, which recomputes the per-record
gate (PilotQuest_Strict_PDF_Ingestion_and_Publishing_Guide.md, sections 15-17).

Pipeline:
  1. load       JSONL or CSV (schemas/import_template.csv); foreign field names mapped
  2. defaults   --defaults JSON fills missing fields on every record
  3. screen     red-flag scan + random intake sample (an intake check only — rule 3)
  4. ids        AUTHORITY-LICENCE-SUBJECT-NNNNNN continuing the bank's max
  5. originals  original wording/choices/answer preserved before anything else changes
  6. shuffle    ONLY with --shuffle (imbalance is a signal, not proof — section 14)
  7. classify   taxonomy.categorize
  8. dedupe     layered (scripts/dedupe.py) vs bank and within batch
  9. validate   schema + structural checks; unknown fields kept in source_payload
 10. route      quarantine/<authority>/<licence>/[<subject>/]<lang>/<provenance>_batch<N>.jsonl
 11. record     injection_log.csv, audit_log.jsonl, inbox -> inbox/processed, gates recomputed
"""
import argparse
import csv
import datetime
import glob
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402
import dedupe  # noqa: E402
from validate_questions import validate_record  # noqa: E402

ROOT = taxonomy.ROOT
TODAY = datetime.date.today().isoformat()
LABELS = "ABCDEFGH"

ALIASES = {"stem": "question_text", "question": "question_text", "prompt": "question_text",
           "answer": "correct_answer", "id": "source_record_id", "level": "difficulty"}
DIFFICULTY_ALIASES = {"easy": "beginner", "medium": "intermediate", "hard": "advanced"}
TYPE_ALIASES = {"multiple_choice_single_answer": "single_choice", "mcq": "single_choice",
                "multiple_choice": "single_choice", "multiple_choice_multiple_answer": "multiple_response"}

RED_FLAGS = [
    (r"\bjeppesen\b|\boxford aviation\b|\bgleim\b|\bsporty'?s\b|\bASA (textbook|test prep)|\brobson\b|\bthom\b(?= aviation)|\blibgen\b",
     "names a commercial textbook/test-prep publisher"),
    (r"\bp(age|g)\.?\s*\d{1,4}\b", "page-number citation (textbook extraction?)"),
    (r"\b(chapter|figure)\s+\d+[-.]\d+\b", "textbook-style chapter/figure numbering"),
    (r"[^\x00-\x7F°±×÷–—’‘“”…µ·²³½¼¾é]{3,}", "non-text characters (OCR junk?)"),
    (r"(\w)\1{4,}", "repeated characters (OCR junk?)"),
]
FOREIGN_SOURCE_FIELDS = ("textbook_source", "book_chapter", "source_pdf_page", "book", "page")


# ---------------------------------------------------------------- 1. load ----
def load_records(path):
    if path.endswith(".csv"):
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        out = []
        for r in rows:
            rec = {k: v for k, v in r.items() if v not in (None, "") and not k.startswith(("choice_", "incorrect_explanation_"))}
            rec["choices"] = [{"label": L, "text": r[f"choice_{L.lower()}"]} for L in LABELS
                              if r.get(f"choice_{L.lower()}")]
            rec["incorrect_answer_explanations"] = {L: r[f"incorrect_explanation_{L.lower()}"] for L in LABELS
                                                    if r.get(f"incorrect_explanation_{L.lower()}")}
            for b in ("reuse_allowed", "verified"):
                if b in rec:
                    rec[b] = str(rec[b]).strip().lower() in ("true", "1", "yes")
            out.append(rec)
        return out
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def normalize_record(r):
    r = dict(r)
    for src, dst in ALIASES.items():
        if src in r and dst not in r:
            r[dst] = r.pop(src)
    if "options" in r and "choices" not in r:
        opts = r.pop("options")
        r["choices"] = [o if isinstance(o, dict) else {"label": LABELS[i], "text": str(o)} for i, o in enumerate(opts)]
    if "correct_option_index" in r:
        r["correct_answer"] = LABELS[int(r.pop("correct_option_index"))]
    elif r.get("choices") and isinstance(r.get("correct_answer"), str) and r["correct_answer"] not in LABELS:
        # correct answer given as text -> convert to its label
        match = [c["label"] for c in r["choices"] if c["text"].strip() == r["correct_answer"].strip()]
        if match:
            r["correct_answer"] = match[0]
    r["difficulty"] = DIFFICULTY_ALIASES.get(r.get("difficulty"), r.get("difficulty"))
    r["question_type"] = TYPE_ALIASES.get(r.get("question_type"), r.get("question_type") or "single_choice")
    if r.get("topic"):
        r["topic_source"] = "explicit"
    if isinstance(r.get("tags"), str):
        r["tags"] = [t.strip() for t in r["tags"].split("|") if t.strip()]
    r.setdefault("language", "en")
    for k in ("explanation", "regulation_reference", "handbook_reference", "calculation_steps",
              "learning_objective_code", "learning_objective", "source_location"):
        r.setdefault(k, "")
    r.setdefault("incorrect_answer_explanations", {})
    r.setdefault("tags", [])
    r.setdefault("last_verified", TODAY)
    return r


# -------------------------------------------------------------- 3. screen ----
def screen(records, sample_size):
    hits = []
    for i, r in enumerate(records):
        blob = " ".join(str(r.get(k, "")) for k in ("question_text", "explanation", "regulation_reference",
                                                     "handbook_reference", "source_title", "source_location"))
        blob += " " + " ".join(c.get("text", "") for c in r.get("choices", []))
        for pattern, why in RED_FLAGS:
            if re.search(pattern, blob, re.I):
                hits.append((i, why))
        for f in FOREIGN_SOURCE_FIELDS:
            if r.get(f):
                hits.append((i, f"carries '{f}' field — find out what it cites before ingesting"))
    rng = random.Random(len(records))
    sample = rng.sample(range(len(records)), min(sample_size, len(records)))
    return hits, sorted(sample)


# ----------------------------------------------------------------- 4. ids ----
def bank_index():
    recs = []
    for path, rs in taxonomy.load_bank():
        for q in rs:
            q["_source_file"] = path
            recs.append(q)
    return recs


AUDIT_DEFAULTS = {
    "extraction_method": "manual", "extraction_confidence": None, "ocr_uncertainties": [],
    "answer_match_confidence": None, "source_has_answer_key": False, "regulatory_status": "",
    "technical_review_status": "pending", "second_check_status": "pending", "editorial_review_status": "pending",
    "regulatory_review_status": "pending", "media_review_status": "not_required", "duplicate_review_status": "pending",
    "source_effective_date": "", "source_accessed_date": "", "regulation_provision": "",
    "question_version": 1, "supersedes_question_id": "", "superseded_by_question_id": "",
    "image_required": False, "hold_reasons": [], "status": "quarantined",
}


def preserve_originals(r):
    """Section 5/7/14: keep exactly what the source said before any change."""
    r.setdefault("original_question_text", r.get("question_text", ""))
    r.setdefault("original_choices", [c.get("text") for c in r.get("choices", [])])
    r.setdefault("original_stated_answer", r.get("correct_answer", ""))
    r.setdefault("original_explanation", r.get("explanation", ""))


def id_prefix_for(r, bank, override):
    if override:
        return override.rstrip("-")
    same = Counter(q["question_id"].rsplit("-", 1)[0] for q in bank
                   if q.get("authority") == r.get("authority") and q.get("licence") == r.get("licence")
                   and q.get("subject_code") == r.get("subject_code"))
    if same:
        return same.most_common(1)[0][0]
    raise SystemExit(f"No existing questions share authority/licence/subject_code "
                     f"({r.get('authority')}/{r.get('licence')}/{r.get('subject_code')}); "
                     f"pass --id-prefix, e.g. EASA-ATPLA-MET")


def assign_ids(records, bank, override):
    max_seq = defaultdict(int)
    for q in bank:
        prefix, seq = q["question_id"].rsplit("-", 1)
        max_seq[prefix] = max(max_seq[prefix], int(seq))
    for r in records:
        if r.get("question_id") and re.match(r"^[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+-\d{6}$", r["question_id"]) \
                and not any(q["question_id"] == r["question_id"] for q in bank):
            continue  # contributor supplied a valid, unused ID
        if r.get("question_id"):
            r.setdefault("source_record_id", r["question_id"])
        prefix = id_prefix_for(r, bank, override)
        max_seq[prefix] += 1
        r["question_id"] = f"{prefix}-{max_seq[prefix]:06d}"


# ------------------------------------------------------------- 5. shuffle ----
def maybe_shuffle(records):
    mc = [r for r in records if r.get("question_type") == "single_choice" and len(r.get("choices", [])) >= 3]
    if not mc:
        return None
    dist = Counter(r["correct_answer"] for r in mc)
    top_share = dist.most_common(1)[0][1] / len(mc)
    if len(mc) < 8 or top_share <= 0.40:
        return None
    return {"imbalance": dict(dist)}


def shuffle(records):
    mc = [r for r in records if r.get("question_type") == "single_choice" and len(r.get("choices", [])) >= 3]
    dist = Counter(r["correct_answer"] for r in mc)
    for r in mc:
        old = {c["label"]: c["text"] for c in r["choices"]}
        texts = [old[L] for L in sorted(old)]
        right = old[r["correct_answer"]]
        others = [t for t in texts if t != right]
        pos = int(hashlib.md5(r["question_id"].encode()).hexdigest(), 16) % len(texts)
        order = others[:pos] + [right] + others[pos:]
        text_to_old = {v: k for k, v in old.items()}
        new_label = {text_to_old[t]: LABELS[i] for i, t in enumerate(order)}
        r["choices"] = [{"label": LABELS[i], "text": t} for i, t in enumerate(order)]
        r["correct_answer"] = LABELS[pos]
        r["incorrect_answer_explanations"] = {new_label[k]: v for k, v in
                                              (r.get("incorrect_answer_explanations") or {}).items() if k in new_label}
        r["shuffle_algorithm"] = "md5(question_id) mod n -> correct-answer position; v1"
        r["shuffle_seed"] = r["question_id"]
        if re.search(r"\b(above|below|all of the|none of the|both of the)\b", " ".join(texts), re.I):
            r.setdefault("quality_flags_import", []).append("shuffle_check_option_references")
    return dict(dist)


# --------------------------------------------------------------- 9. route ----
def route(r, bank, target_dir):
    """Return the logical directory (relative to data/ and quarantine/) for a record."""
    if target_dir:
        return target_dir.split("/", 1)[1] if target_dir.startswith(("data/", "quarantine/")) else target_dir
    rel_of = lambda q: os.path.dirname(taxonomy.rel_path(q["_source_file"]))
    same_subject = [rel_of(q) for q in bank if q.get("track_id") == r["track_id"]
                    and q.get("subject_code") == r.get("subject_code")]
    same_track = [rel_of(q) for q in bank if q.get("track_id") == r["track_id"]]
    if same_subject:
        return Counter(same_subject).most_common(1)[0][0]
    if same_track:
        parts = Counter(same_track).most_common(1)[0][0].split(os.sep)
        if len(parts) == 3:  # <authority>/<licence>/<lang> (FAA layout: no subject folder)
            return os.sep.join(parts)
        subj = re.sub(r"[^a-z0-9]+", "-", r["subject"].lower()).strip("-")
        return os.path.join(parts[0], parts[1], subj, r.get("language", "en"))
    raise SystemExit(f"{r['question_id']}: no folder exists yet for track {r['track_id']}; "
                     f"pass --target-dir <authority>/<licence>/<subject>/<lang>")


def batch_file(directory, provenance, label, planned):
    existing = []
    for store in taxonomy.STORE_DIRS:
        existing += glob.glob(os.path.join(ROOT, store, directory, f"{provenance}_batch*.jsonl"))
    existing += [p for p in planned if os.path.dirname(p) == directory and os.path.basename(p).startswith(provenance)]
    nums = [int(m.group(1)) for p in existing if (m := re.search(r"_batch(\d+)", os.path.basename(p)))]
    n = max(nums, default=0) + 1
    suffix = f"_{re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')}" if label else ""
    return os.path.join(directory, f"{provenance}_batch{n}{suffix}.jsonl")


# ---------------------------------------------------------------- main -------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("batch")
    ap.add_argument("--defaults", help="JSON object of fields to fill on every record")
    ap.add_argument("--apply", action="store_true", help="write to data/ (default: dry run)")
    ap.add_argument("--provenance-reviewed", metavar="NOTE",
                    help="required with --apply: what you checked in the answer sample")
    ap.add_argument("--shuffle", action="store_true",
                    help="rebalance correct-answer letters (only after verification; records algorithm + seed)")
    ap.add_argument("--source-id", help="registered source_id (sources/source_manifest.json) for every record")
    ap.add_argument("--rights-record", help="rights_record_id (taxonomy/rights_records.csv) for every record")
    ap.add_argument("--id-prefix", help="e.g. EASA-ATPLA-MET when the subject is new to the bank")
    ap.add_argument("--target-dir", help="override routing, relative to the bank root")
    ap.add_argument("--label", default="", help="short batch label for the file name, e.g. 'icing'")
    ap.add_argument("--allow-red-flags", action="store_true",
                    help="import flagged records anyway — into quarantine only, flagged; never into an active view")
    ap.add_argument("--allow-duplicates", action="store_true", help="import duplicates into quarantine for review")
    ap.add_argument("--sample", type=int, default=15)
    args = ap.parse_args()

    raw = load_records(args.batch)
    defaults = {}
    if args.defaults:
        with open(args.defaults, encoding="utf-8") as f:
            defaults = json.load(f)
    records = [normalize_record({**defaults, **r}) for r in raw]
    print(f"Loaded {len(records)} record(s) from {args.batch}")

    # 3. screen
    hits, sample = screen(records, args.sample)
    if hits:
        print(f"\nRED FLAGS ({len(hits)}):")
        for i, why in hits[:40]:
            print(f"  #{i + 1}: {why} — {records[i].get('question_text', '')[:90]}")
    print(f"\nANSWER SAMPLE — read these before trusting the batch's provenance label:")
    for i in sample:
        r = records[i]
        right = next((c["text"] for c in r.get("choices", []) if c["label"] == r.get("correct_answer")),
                     r.get("correct_answer"))
        print(f"  #{i + 1} Q: {r.get('question_text', '')[:110]}\n       A: {str(right)[:110]}")

    # 4-7. ids, originals, (shuffle), classify
    bank = bank_index()
    manifest_path = os.path.join(ROOT, "sources", "source_manifest.json")
    manifest = json.load(open(manifest_path, encoding="utf-8")) if os.path.exists(manifest_path) else {}
    rights_ids = {row["rights_record_id"] for row in csv.DictReader(open(os.path.join(ROOT, "taxonomy", "rights_records.csv")))}
    assign_ids(records, bank, args.id_prefix)
    errors = []
    for r in records:
        preserve_originals(r)
        r["reuse_allowed"] = False     # rule 4: derived from the rights record by gates.py, never trusted from import
        r["verified"] = False          # derived from review statuses by gates.py
        for k, v in AUDIT_DEFAULTS.items():
            r.setdefault(k, v)
        r["status"] = "quarantined"     # rules 2 & 15: nothing is imported active
        if args.source_id:
            r["source_id"] = args.source_id
        if args.rights_record:
            r["rights_record_id"] = args.rights_record
        if r.get("source_id") not in manifest:
            errors.append(f"{r['question_id']}: source_id '{r.get('source_id')}' not registered in sources/source_manifest.json")
        if r.get("rights_record_id") not in rights_ids:
            errors.append(f"{r['question_id']}: rights_record_id '{r.get('rights_record_id')}' not in taxonomy/rights_records.csv")
        if hits and any(i == records.index(r) for i, _ in hits):
            r.setdefault("hold_reasons", []).append("intake red flag — provenance/copyright check required")
    imbalance = maybe_shuffle(records)
    if imbalance:
        print(f"\nAnswer-letter imbalance {imbalance['imbalance']} (reporting signal only).")
        if args.shuffle:
            shuffle(records)
            print("  --shuffle given: reshuffled deterministically; algorithm + seed recorded per record.")
    for i, r in enumerate(records):
        r["_source_file"] = ""
        try:
            records[i] = taxonomy.categorize(r)
        except taxonomy.CategorizationError as e:
            errors.append(str(e))
        for extra in records[i].pop("quality_flags_import", []):
            records[i]["quality_flags"] = sorted(set(records[i]["quality_flags"]) | {extra})

    # 8. dedupe (layered, vs bank and within batch)
    dups = []
    if not errors:
        new_ids = {r["question_id"] for r in records}
        for p in dedupe.find_pairs(bank + records):
            if p["layer"] != "template" and (p["question_id_a"] in new_ids or p["question_id_b"] in new_ids):
                dups.append(p)
    if dups:
        print(f"\nDUPLICATES ({len(dups)}):")
        for p in dups:
            print(f"  {p['question_id_a']} ~ {p['question_id_b']} ({p['layer']} {p['score']}, {p['scope']})")
    dup_ids = {p[k] for p in dups for k in ("question_id_a", "question_id_b")} & {r["question_id"] for r in records}

    # 8. validate
    with open(os.path.join(ROOT, "schemas", "question.schema.json"), encoding="utf-8") as f:
        schema = json.load(f)
    seen = {q["question_id"]: q["_source_file"] for q in bank}
    for i, r in enumerate(records):
        errs, warns = validate_record(args.batch, i + 1, r, schema, seen)
        errors += errs
        for w in warns:
            print("WARNING", w)
        if r.get("question_type") == "short_answer":
            errors.append(f"{r['question_id']}: short_answer — write 3 distractors first (the app serves multiple choice)")

    allowed = set(schema["properties"])
    unknown = Counter(k for r in records for k in r if k not in allowed and not k.startswith("_"))
    if unknown:
        print(f"\nUnknown fields preserved in source_payload (map them deliberately later): {dict(unknown)}")
        for r in records:
            extra = {k: r.pop(k) for k in list(r) if k not in allowed and not k.startswith("_")}
            if extra:
                r["source_payload"] = {**r.get("source_payload", {}), **extra}

    # 9. route
    plan = defaultdict(list)
    if not errors:
        planned = []
        for r in records:
            if r["question_id"] in dup_ids:
                if not args.allow_duplicates:
                    continue
                r["duplicate_review_status"] = "pending"
            d = route(r, bank, args.target_dir)
            key = (d, r["provenance"])
            if key not in {(os.path.dirname(p), pv) for p, pv in planned}:
                planned.append((batch_file(d, r["provenance"], args.label, [p for p, _ in planned]), r["provenance"]))
            path = next(p for p, pv in planned if os.path.dirname(p) == d and pv == r["provenance"])
            plan[path].append(r)

    print("\nSUMMARY")
    print(f"  topics:  {dict(Counter(r.get('topic') for r in records))}")
    print(f"  tracks:  {dict(Counter(r.get('track_id') for r in records))}")
    print(f"  status:  {dict(Counter(r.get('status') for r in records))}")
    print(f"  flags:   {dict(Counter(f for r in records for f in r.get('quality_flags', [])))}")
    for path, rs in plan.items():
        print(f"  -> quarantine/{path}: {len(rs)} ({rs[0]['question_id']} … {rs[-1]['question_id']})")
    for e in errors:
        print("ERROR", e)

    blocked = bool(errors) or (bool(hits) and not args.allow_red_flags) or (bool(dups) and not args.allow_duplicates)
    if not args.apply:
        print("\nDry run only." + (" Fix the problems above first." if blocked else
                                  " Re-run with --apply --provenance-reviewed \"<what you checked>\"."))
        sys.exit(1 if errors else 0)
    if blocked:
        sys.exit("\nNot applied: resolve errors / red flags / duplicates (--allow-* imports into quarantine only).")
    if not args.provenance_reviewed:
        sys.exit("\nNot applied: --provenance-reviewed \"<what you checked in the answer sample>\" is required.")

    # 10-11. write to quarantine/, log, recompute gates
    for path, rs in plan.items():
        full = os.path.join(ROOT, "quarantine", path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        taxonomy.write_jsonl(full, rs)
    log = os.path.join(ROOT, "reports", "injection_log.csv")
    new_log = not os.path.exists(log)
    with open(log, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_log:
            w.writerow(["date", "inbox_file", "target_file", "count", "first_id", "last_id",
                        "status_counts", "provenance_review_note"])
        for path, rs in plan.items():
            w.writerow([TODAY, os.path.basename(args.batch), "quarantine/" + path, len(rs),
                        rs[0]["question_id"], rs[-1]["question_id"],
                        json.dumps(dict(Counter(r["status"] for r in rs))), args.provenance_reviewed])
    with open(os.path.join(ROOT, "reports", "audit_log.jsonl"), "a", encoding="utf-8") as f:
        for path, rs in plan.items():
            for r in rs:
                f.write(json.dumps({"date": TODAY, "question_id": r["question_id"], "process": "inject_questions.py",
                                    "from_status": None, "to_status": "quarantined", "pipeline_state": "received",
                                    "evidence": {"inbox_file": os.path.basename(args.batch),
                                                 "intake_note": args.provenance_reviewed}}, ensure_ascii=False) + "\n")
    done = os.path.join(ROOT, "inbox", "processed")
    os.makedirs(done, exist_ok=True)
    for p in [args.batch] + ([args.defaults] if args.defaults else []):
        if os.path.abspath(p).startswith(os.path.join(ROOT, "inbox")):
            shutil.move(p, os.path.join(done, f"{TODAY}_{os.path.basename(p)}"))
    print("\nImported into quarantine/. Recomputing gates and views …")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "release_questions.py")], check=True)
    print("Next: review records and release them with scripts/release_questions.py --approval-file reviews/<file>.csv")


if __name__ == "__main__":
    main()
