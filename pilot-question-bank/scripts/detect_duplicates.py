#!/usr/bin/env python3
"""
detect_duplicates.py — Flags exact and near-duplicate questions within
and across pilot-question-bank JSONL files, using normalized text overlap
(no external ML dependencies required; swap in embeddings for higher
recall if available).

Usage:
    python3 detect_duplicates.py data/**/*.jsonl --threshold 0.85

Output: prints duplicate groups as
    GROUP <n> (score=0.xx): id1 <-> id2
and writes a duplicate_groups.csv summary next to the first input path's
directory (or --out).

Method:
  1. Exact-duplicate pass: normalized (lowercased, whitespace-collapsed,
     punctuation-stripped) question_text hash equality.
  2. Near-duplicate pass: Jaccard similarity over word shingles (k=3)
     between questions in the SAME exam_system_id + subject_code, to
     avoid false positives across unrelated authorities/subjects.
  3. Cross-language pass is NOT attempted here (requires translation
     alignment) — translated duplicates must be flagged manually via
     review_records until a translation-aware pass is added.

This is a recall-oriented heuristic tool for human triage, not an
authoritative duplicate resolver — always confirm before archiving.
"""
import argparse
import csv
import glob
import json
import re
from collections import defaultdict
from itertools import combinations


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def shingles(text, k=3):
    words = text.split()
    if len(words) < k:
        return {text}
    return {" ".join(words[i:i + k]) for i in range(len(words) - k + 1)}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def load_all(patterns):
    records = []
    for pattern in patterns:
        matched = glob.glob(pattern, recursive=True)
        for path in (matched if matched else [pattern]):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    q = json.loads(line)
                    q["_source_file"] = path
                    records.append(q)
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--threshold", type=float, default=0.85)
    parser.add_argument("--out", default="duplicate_groups.csv")
    args = parser.parse_args()

    records = load_all(args.files)
    for q in records:
        q["_norm"] = normalize(q.get("question_text", ""))
        q["_shingles"] = shingles(q["_norm"])

    # Bucket by exam_system/subject to limit comparisons.
    buckets = defaultdict(list)
    for q in records:
        key = (q.get("licence", ""), q.get("subject_code") or q.get("subject", ""))
        buckets[key].append(q)

    groups = []
    seen_pairs = set()

    for key, bucket in buckets.items():
        for a, b in combinations(bucket, 2):
            pair = tuple(sorted([a.get("question_id", "?"), b.get("question_id", "?")]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            if a["_norm"] == b["_norm"]:
                score = 1.0
            else:
                score = jaccard(a["_shingles"], b["_shingles"])
            if score >= args.threshold:
                groups.append((score, a.get("question_id"), b.get("question_id")))

    groups.sort(reverse=True)
    for i, (score, id_a, id_b) in enumerate(groups, start=1):
        print(f"GROUP {i} (score={score:.2f}): {id_a} <-> {id_b}")

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["group", "similarity_score", "question_id_a", "question_id_b"])
        for i, (score, id_a, id_b) in enumerate(groups, start=1):
            writer.writerow([i, f"{score:.3f}", id_a, id_b])

    print(f"\n{len(records)} question(s) scanned, {len(groups)} duplicate pair(s) found "
          f"at threshold {args.threshold}. Summary written to {args.out}.")


if __name__ == "__main__":
    main()
