#!/usr/bin/env python3
"""
categorize.py — (Re)apply the taxonomy to every question in data/.

Usage:
    python3 scripts/categorize.py            # dry run: report what would change
    python3 scripts/categorize.py --write    # rewrite data/**/*.jsonl in place
    python3 scripts/categorize.py --report   # print the topic x track matrix

Idempotent: run it after editing anything in taxonomy/ (rules, overrides,
licences, review flags) and every record is re-derived from the same rules.
Records are rewritten field-for-field otherwise unchanged; line order is kept.
"""
import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402

DERIVED = ("topic", "topic_name", "topic_source", "track_id", "licence_level", "aircraft_class",
           "applicable_licences", "chapter_title", "question_style", "quality_flags", "subject")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    changed_files, changed_recs, errors = 0, collections.Counter(), []
    all_recs = []
    for path, recs in taxonomy.load_bank():
        new = []
        for q in recs:
            q["_source_file"] = path
            try:
                c = taxonomy.categorize(q)
            except taxonomy.CategorizationError as e:
                errors.append(str(e))
                c = q
            for k in DERIVED:
                if q.get(k) != c.get(k):
                    changed_recs[k] += 1
            new.append(c)
        all_recs.extend(new)
        if any(a != b for a, b in zip(recs, new)) and args.write:
            taxonomy.write_jsonl(path, new)
            changed_files += 1

    for e in errors:
        print("ERROR", e)
    print(f"{len(all_recs)} records; field changes: {dict(changed_recs)}")
    if args.write:
        print(f"{changed_files} file(s) rewritten")

    if args.report:
        m = collections.Counter((q.get("topic"), q.get("track_id")) for q in all_recs)
        tracks = sorted({t for _, t in m})
        print("\n" + "topic".ljust(24) + "".join(t.split(":")[1][:9].rjust(10) for t in tracks))
        for topic in taxonomy.TOPICS:
            print(topic[:24].ljust(24) + "".join(str(m.get((topic, t), "")).rjust(10) for t in tracks))
        print("\nflags:", collections.Counter(f for q in all_recs for f in q.get("quality_flags", [])))
        print("styles:", collections.Counter(q.get("question_style") for q in all_recs))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
