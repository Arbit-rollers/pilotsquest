#!/usr/bin/env python3
"""
inject_questions.py — Bring a new batch of questions into the bank.

    python3 scripts/inject_questions.py inbox/my_batch.jsonl [--defaults inbox/my_batch.defaults.json]
    python3 scripts/inject_questions.py inbox/my_batch.jsonl --apply \
        --provenance-reviewed "read 20 answers across ch1-12; no textbook text"

Without --apply nothing is written: you get a full dry-run report.
See "question injection.md" at the bank root for the complete workflow.

Pipeline (each stage can stop the run):
  1. load      JSONL or CSV (schemas/import_template.csv columns); common
               foreign field names are mapped (stem/options/correct_option_index …)
  2. defaults  --defaults JSON fills fields missing on every record
  3. screen    red-flag scan (textbook names, page cites, OCR junk) + a random
               answer sample you must read; --apply needs --provenance-reviewed
  4. ids       AUTHORITY-LICENCE-SUBJECT-NNNNNN, continuing the bank's max
  5. shuffle   rebalance correct-answer letters if the batch is skewed
  6. classify  taxonomy.categorize (topic, track, applicability, flags)
  7. dedupe    exact + near-duplicate check vs bank and within batch
  8. validate  the same checks as validate_questions.py
  9. route     data/<authority>/<licence>/[<subject>/]<lang>/<provenance>_batch<N>.jsonl
 10. publish   write, rebuild views/, log to reports/injection_log.csv,
               move the inbox file to inbox/processed/
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
from detect_duplicates import normalize, shingles, jaccard  # noqa: E402
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
    return dict(dist)


# -------------------------------------------------------------- 7. dedupe ----
def find_duplicates(records, bank, threshold):
    pool = defaultdict(list)
    for q in bank:
        n = normalize(q["question_text"])
        pool[(q.get("track_id"), q.get("topic"))].append((q["question_id"], n, shingles(n)))
    dups = []
    for r in records:
        n = normalize(r["question_text"])
        sh = shingles(n)
        key = (r.get("track_id"), r.get("topic"))
        for qid, n2, sh2 in pool[key]:
            score = 1.0 if n == n2 else jaccard(sh, sh2)
            if score >= threshold:
                dups.append((r["question_id"], qid, round(score, 2)))
                break
        pool[key].append((r["question_id"], n, sh))
    return dups


# --------------------------------------------------------------- 9. route ----
def route(r, bank, target_dir):
    if target_dir:
        d = os.path.join(ROOT, target_dir)
    else:
        same_subject = [q["_source_file"] for q in bank if q.get("track_id") == r["track_id"]
                        and q.get("subject_code") == r.get("subject_code")]
        same_track = [q["_source_file"] for q in bank if q.get("track_id") == r["track_id"]]
        if same_subject:
            d = os.path.dirname(Counter(same_subject).most_common(1)[0][0])
        elif same_track:
            track_dir = os.path.dirname(Counter(same_track).most_common(1)[0][0])
            rel = os.path.relpath(track_dir, os.path.join(ROOT, "data")).split(os.sep)
            if len(rel) == 3:  # data/<authority>/<licence>/<lang> (FAA layout: no subject folder)
                d = track_dir
            else:              # data/<authority>/<licence>/<subject>/<lang>
                subj = re.sub(r"[^a-z0-9]+", "-", r["subject"].lower()).strip("-")
                d = os.path.join(ROOT, "data", rel[0], rel[1], subj, r.get("language", "en"))
        else:
            raise SystemExit(f"{r['question_id']}: no folder exists yet for track {r['track_id']}; "
                             f"pass --target-dir data/<authority>/<licence>/<subject>/<lang>")
    return d


def batch_file(directory, provenance, label, planned):
    existing = glob.glob(os.path.join(directory, f"{provenance}_batch*.jsonl")) + \
        [p for p in planned if os.path.dirname(p) == directory and os.path.basename(p).startswith(provenance)]
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
    ap.add_argument("--activate", action="store_true",
                    help="set status=active on records that pass every check (default: quarantined)")
    ap.add_argument("--id-prefix", help="e.g. EASA-ATPLA-MET when the subject is new to the bank")
    ap.add_argument("--target-dir", help="override routing, relative to the bank root")
    ap.add_argument("--label", default="", help="short batch label for the file name, e.g. 'icing'")
    ap.add_argument("--allow-red-flags", action="store_true")
    ap.add_argument("--allow-duplicates", action="store_true")
    ap.add_argument("--dup-threshold", type=float, default=0.85)
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

    # 4-6. ids, shuffle, classify
    bank = bank_index()
    assign_ids(records, bank, args.id_prefix)
    skew = maybe_shuffle(records)
    if skew:
        print(f"\nCorrect-answer letters were skewed {skew}; reshuffled deterministically.")
    errors = []
    for i, r in enumerate(records):
        r["_source_file"] = ""
        if r.get("status") not in ("active", "quarantined", "archived", "rejected"):
            r["status"] = "quarantined"
        try:
            records[i] = taxonomy.categorize(r)
        except taxonomy.CategorizationError as e:
            errors.append(str(e))

    # 7. dedupe
    dups = [] if errors else find_duplicates(records, bank, args.dup_threshold)
    if dups:
        print(f"\nDUPLICATES ({len(dups)}):")
        for new, old, s in dups:
            print(f"  {new} ~ {old} (similarity {s})")

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
    dropped = Counter(k for r in records for k in r if k not in allowed and not k.startswith("_"))
    if dropped:
        print(f"\nDropping fields not in the schema: {dict(dropped)}")
        records = [{k: v for k, v in r.items() if k in allowed or k.startswith("_")} for r in records]

    dup_ids = {d[0] for d in dups}
    if args.activate:
        for r in records:
            if r["question_id"] not in dup_ids and r["provenance"] in taxonomy.USABLE_PROVENANCE \
                    and r.get("reuse_allowed") and not ({"needs_figure", "missing_calculation_steps"} & set(r["quality_flags"])):
                r["status"] = "active"
                r["quality_flags"] = [f for f in r["quality_flags"] if f != "quarantined"]

    # 9. route
    plan = defaultdict(list)
    if not errors:
        planned = []
        for r in records:
            if r["question_id"] in dup_ids and not args.allow_duplicates:
                continue
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
        print(f"  -> {os.path.relpath(path, ROOT)}: {len(rs)} ({rs[0]['question_id']} … {rs[-1]['question_id']})")
    for e in errors:
        print("ERROR", e)

    blocked = bool(errors) or (hits and not args.allow_red_flags) or (dups and not args.allow_duplicates)
    if not args.apply:
        print("\nDry run only." + (" Fix the problems above first." if blocked else
                                  " Re-run with --apply --provenance-reviewed \"<what you checked>\"."))
        sys.exit(1 if errors else 0)
    if blocked:
        sys.exit("\nNot applied: resolve errors / red flags / duplicates (or pass the matching --allow-* flag).")
    if not args.provenance_reviewed:
        sys.exit("\nNot applied: --provenance-reviewed \"<what you checked in the answer sample>\" is required.")

    # 10. publish
    for path, rs in plan.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        taxonomy.write_jsonl(path, rs)
    log = os.path.join(ROOT, "reports", "injection_log.csv")
    new_log = not os.path.exists(log)
    with open(log, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_log:
            w.writerow(["date", "inbox_file", "target_file", "count", "first_id", "last_id",
                        "status_counts", "provenance_review_note"])
        for path, rs in plan.items():
            w.writerow([TODAY, os.path.basename(args.batch), os.path.relpath(path, ROOT), len(rs),
                        rs[0]["question_id"], rs[-1]["question_id"],
                        json.dumps(dict(Counter(r["status"] for r in rs))), args.provenance_reviewed])
    done = os.path.join(ROOT, "inbox", "processed")
    os.makedirs(done, exist_ok=True)
    for p in [args.batch] + ([args.defaults] if args.defaults else []):
        if os.path.abspath(p).startswith(os.path.join(ROOT, "inbox")):
            shutil.move(p, os.path.join(done, f"{TODAY}_{os.path.basename(p)}"))
    print("\nWritten. Rebuilding views …")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "validate_questions.py"),
                    os.path.join(ROOT, "data", "**", "*.jsonl"),
                    "--schema", os.path.join(ROOT, "schemas", "question.schema.json")], check=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_views.py")], check=True,
                   stdout=subprocess.DEVNULL)
    print("Views rebuilt. Add a batch entry to reports/progress.md.")


if __name__ == "__main__":
    main()
