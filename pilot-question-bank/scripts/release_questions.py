#!/usr/bin/env python3
"""
release_questions.py — Apply recorded review decisions, recompute every gate,
and place records in data/ (active) or quarantine/ (held).

    python3 scripts/release_questions.py --approval-file reviews/<file>.csv [--dry-run]
    python3 scripts/release_questions.py                # just recompute gates for the whole bank

Review file columns:
    question_id, review_type, result, reviewer, date, evidence, notes
    [, regulatory_status, regulation_provision, source_effective_date, source_accessed_date]

review_type: technical | second_check | editorial | regulatory | media | accessibility
result:      passed | failed | pending

An approval only sets a review status. Activation is always recomputed by
scripts/gates.py, so an approval can never override a failed gate
(guide sections 15 and 17). Every change is appended to reports/audit_log.jsonl.
"""
import argparse
import collections
import csv
import datetime
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402
import gates  # noqa: E402
import dedupe  # noqa: E402

ROOT = taxonomy.ROOT
TODAY = datetime.date.today().isoformat()
FIELD = {"technical": "technical_review_status", "second_check": "second_check_status",
         "editorial": "editorial_review_status", "regulatory": "regulatory_review_status",
         "media": "media_review_status"}
RESULTS = {"passed", "failed", "pending"}


def load_reviews(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    bad = [r for r in rows if r["review_type"] not in set(FIELD) | {"accessibility"} or r["result"] not in RESULTS
           or not r.get("reviewer") or not r.get("date")]
    if bad:
        sys.exit(f"{len(bad)} invalid review row(s), e.g. {bad[0]} — need review_type, result, reviewer, date")
    return rows


def apply_review(q, r):
    t = r["review_type"]
    if t == "accessibility":
        q["image_accessibility_verified"] = r["result"] == "passed"
    else:
        q[FIELD[t]] = r["result"]
    if t == "media":
        q["image_verified"] = r["result"] == "passed"
    if t == "regulatory":
        for k in ("regulatory_status", "regulation_provision", "source_effective_date", "source_accessed_date"):
            if r.get(k):
                q[k] = r[k]
    q.setdefault("review_history", []).append(
        {k: r.get(k, "") for k in ("review_type", "result", "reviewer", "date", "evidence", "notes")})


def normalize_applicability(q):
    """Keep review statuses consistent when policy changes what a record needs."""
    if not taxonomy.regulation_dependent(q) and q.get("regulatory_review_status") == "pending" \
            and q.get("regulatory_status") in ("", "quarantined"):
        q["regulatory_status"], q["regulatory_review_status"] = "", "not_applicable"
        q.pop("regulatory_note", None)
    if taxonomy.regulation_dependent(q) and q.get("regulatory_review_status") == "not_applicable":
        q["regulatory_status"], q["regulatory_review_status"] = "quarantined", "pending"
    needs = taxonomy.needs_second_check(q)
    if not needs and q.get("second_check_status") == "pending":
        q["second_check_status"] = "not_required"
    if needs and q.get("second_check_status") == "not_required":
        q["second_check_status"] = "pending"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--approval-file")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = taxonomy.load_logical_files()
    by_id = {q["question_id"]: q for recs in files.values() for q in recs}
    before = {qid: (q.get("status"), q.get("pipeline_state")) for qid, q in by_id.items()}

    if args.approval_file:
        reviews = load_reviews(args.approval_file)
        unknown = [r["question_id"] for r in reviews if r["question_id"] not in by_id]
        if unknown:
            sys.exit(f"unknown question_id(s): {unknown[:5]}")
        for r in reviews:
            apply_review(by_id[r["question_id"]], r)
        print(f"applied {len(reviews)} review decision(s) from {args.approval_file}")

    # re-derive categories and duplicate status, then the gate
    for rel, recs in files.items():
        for i, q in enumerate(recs):
            src = q.get("_source_file")
            recs[i] = taxonomy.categorize(q)
            recs[i]["_source_file"] = src
    all_recs = [q for recs in files.values() for q in recs]
    dup, _ = dedupe.review_status(all_recs)
    log = []
    for q in all_recs:
        q["duplicate_review_status"], q["similarity_score"], q["duplicate_group_id"] = dup[q["question_id"]]
        normalize_applicability(q)
        ev = gates.apply(q)
        old = before.get(q["question_id"])
        if old != (q["status"], q["pipeline_state"]):
            log.append({"date": TODAY, "question_id": q["question_id"], "process": "release_questions.py",
                        "approval_file": args.approval_file or "", "from_status": old[0] if old else None,
                        "to_status": q["status"], "from_state": old[1] if old else None,
                        "pipeline_state": q["pipeline_state"],
                        "evidence": {k: v[1] for k, v in ev["gates"].items() if not v[0]}})

    c = collections.Counter(q["status"] for q in all_recs)
    print(f"status: {dict(c)}; transitions: {len(log)}")
    print("first failing gate:", dict(collections.Counter((q["gate_failures"] or ["none"])[0] for q in all_recs)))
    if args.dry_run:
        print("dry run — nothing written")
        return
    taxonomy.place(files)
    with open(os.path.join(ROOT, "reports", "audit_log.jsonl"), "a", encoding="utf-8") as f:
        for e in log:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_views.py")], check=True,
                   stdout=subprocess.DEVNULL)
    print("placed records, logged transitions, rebuilt views/")


if __name__ == "__main__":
    main()
