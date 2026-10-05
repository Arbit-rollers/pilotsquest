#!/usr/bin/env python3
"""
dedupe.py — Layered duplicate detection (guide section 13).

Layers run here:
  1. exact      normalized stem + sorted choices hash
  2. stem       choice-independent normalized stem equality
  3. token      word 3-shingle Jaccard  >= 0.85
  4. char       character 4-gram Jaccard >= 0.90
  5. template   stems identical once numbers are masked (numeric variants)
Layers NOT available in this environment, reported as not_run:
  semantic similarity, translation/cross-language, perceptual image hash.

Scope: every pair within the same topic, across batches, licences and
authorities. Cross-authority matches are flagged for review, never merged.
Pairs a reviewer has resolved live in taxonomy/duplicate_decisions.csv.

    python3 scripts/dedupe.py            # report to reports/duplicate_report.csv
"""
import csv
import os
import re
import sys
from collections import defaultdict
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402

NOT_RUN = ["semantic", "translation", "image_hash"]
DECISIONS = os.path.join(taxonomy.TAX, "duplicate_decisions.csv")


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (t or "").lower())).strip()


def shingles(words, k=3):
    return {" ".join(words[i:i + k]) for i in range(max(1, len(words) - k + 1))}


def grams(s, k=4):
    return {s[i:i + k] for i in range(max(1, len(s) - k + 1))}


def jac(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def load_decisions():
    if not os.path.exists(DECISIONS):
        return {}
    with open(DECISIONS, encoding="utf-8", newline="") as f:
        return {tuple(sorted((r["question_id_a"], r["question_id_b"]))): r for r in csv.DictReader(f)}


def features(q):
    stem = norm(q.get("question_text"))
    choices = "|".join(sorted(norm(c.get("text")) for c in q.get("choices", [])))
    return {"id": q["question_id"], "topic": q.get("topic"), "track": q.get("track_id"),
            "authority": q.get("authority"), "stem": stem, "full": stem + "#" + choices,
            "sh": shingles(stem.split()), "cg": grams(stem), "tmpl": re.sub(r"\d+(\.\d+)?", "#", stem)}


def find_pairs(records):
    buckets = defaultdict(list)
    for q in records:
        f = features(q)
        buckets[f["topic"]].append(f)
    pairs = []
    for bucket in buckets.values():
        for a, b in combinations(bucket, 2):
            layer, score = None, 0.0
            if a["full"] == b["full"]:
                layer, score = "exact", 1.0
            elif a["stem"] == b["stem"]:
                layer, score = "stem", 1.0
            elif a["tmpl"] == b["tmpl"] and "#" in a["tmpl"]:
                layer, score = "template", 1.0
            else:
                t = jac(a["sh"], b["sh"])
                c = jac(a["cg"], b["cg"])
                if t >= 0.85:
                    layer, score = "token", t
                elif c >= 0.90:
                    layer, score = "char", c
            if layer:
                scope = ("cross_authority" if a["authority"] != b["authority"] else
                         "cross_licence" if a["track"] != b["track"] else "same_track")
                pairs.append({"question_id_a": a["id"], "question_id_b": b["id"], "layer": layer,
                              "score": round(score, 3), "scope": scope})
    return pairs


def review_status(records):
    """Return ({question_id: (status, similarity, group_id)}, pairs) after applying reviewer decisions."""
    decisions = load_decisions()
    pairs = find_pairs(records)
    out = {q["question_id"]: ("passed", None, "") for q in records}
    for i, p in enumerate(pairs, 1):
        key = tuple(sorted((p["question_id_a"], p["question_id_b"])))
        d = decisions.get(key)
        p["decision"] = d["decision"] if d else ""
        if p["layer"] == "template" and not d:
            p["decision"] = "info_only_numeric_variant"
            continue
        if d and d["decision"] == "distinct":
            continue
        gid = f"DUP-{i:05d}"
        for qid in key:
            # 'duplicate' decision: the later ID loses; undecided: both pending
            if d and d["decision"] == "duplicate" and qid == key[0]:
                continue
            out[qid] = ("failed" if d else "pending", p["score"], gid)
    return out, pairs


def main():
    records = [q for _, rs in taxonomy.load_bank() for q in rs]
    status, pairs = review_status(records)
    path = os.path.join(taxonomy.ROOT, "reports", "duplicate_report.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["question_id_a", "question_id_b", "layer", "score", "scope", "decision"])
        w.writeheader()
        w.writerows(pairs)
    from collections import Counter
    print(f"{len(records)} records, {len(pairs)} pair(s): {dict(Counter((p['layer'], p['scope']) for p in pairs))}")
    print(f"pending review: {sum(1 for s in status.values() if s[0] == 'pending')}; layers not run: {NOT_RUN}")
    print(f"report: {os.path.relpath(path, taxonomy.ROOT)}")


if __name__ == "__main__":
    main()
