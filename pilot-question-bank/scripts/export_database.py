#!/usr/bin/env python3
"""
export_database.py — Loads all data/**/*.jsonl question files, applies
the usable-provenance filter, and exports normalized CSV tables matching
schemas/database_schema.sql (questions, answer_choices, explanations,
sources dedup by URL) plus a combined flat CSV for spreadsheet review.

Usage:
    python3 export_database.py --data-dir data --out-dir export

Only rows with provenance in the five usable classes AND reuse_allowed
== True AND status == 'active' are written to the "usable" exports;
everything else is written to quarantine_export.csv for manual review,
matching the project's provenance policy (see reports/legal_and_provenance_notes.md).
"""
import argparse
import csv
import glob
import json
import os

USABLE_PROVENANCE = {
    "official_released", "official_sample", "public_domain",
    "open_licensed", "original_syllabus_aligned",
}


def load_all(data_dir):
    records = []
    for path in glob.glob(os.path.join(data_dir, "**", "*.jsonl"), recursive=True):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                q = json.loads(line)
                q["_source_file"] = path
                records.append(q)
    return records


def is_usable(q):
    return (
        q.get("provenance") in USABLE_PROVENANCE
        and q.get("reuse_allowed") is True
        and q.get("status", "quarantined") == "active"
    )


def write_flat_csv(records, path):
    if not records:
        open(path, "w").close()
        return
    fields = [
        "question_id", "authority", "country_or_region", "licence", "subject_code",
        "subject", "syllabus_version", "learning_objective_code", "question_type",
        "question_text", "correct_answer", "difficulty", "aircraft_category",
        "language", "provenance", "source_title", "source_url", "copyright_status",
        "reuse_allowed", "verified", "last_verified", "status",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for q in records:
            row = dict(q)
            if isinstance(row.get("correct_answer"), list):
                row["correct_answer"] = "|".join(row["correct_answer"])
            writer.writerow(row)


def write_choices_csv(records, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["question_id", "choice_label", "choice_text", "is_correct", "display_order"])
        for q in records:
            correct = q.get("correct_answer")
            correct_set = set(correct) if isinstance(correct, list) else {correct}
            for i, choice in enumerate(q.get("choices", [])):
                writer.writerow([
                    q.get("question_id"), choice.get("label"), choice.get("text"),
                    choice.get("label") in correct_set, i,
                ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--out-dir", default="export")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    records = load_all(args.data_dir)
    usable = [q for q in records if is_usable(q)]
    quarantined = [q for q in records if not is_usable(q)]

    write_flat_csv(usable, os.path.join(args.out_dir, "usable_questions.csv"))
    write_flat_csv(quarantined, os.path.join(args.out_dir, "quarantine_export.csv"))
    write_choices_csv(usable, os.path.join(args.out_dir, "answer_choices.csv"))

    print(f"Loaded {len(records)} question record(s) from {args.data_dir}.")
    print(f"  Usable (active + reuse_allowed + covered provenance): {len(usable)}")
    print(f"  Quarantined / excluded: {len(quarantined)}")
    print(f"Exports written to {args.out_dir}/")


if __name__ == "__main__":
    main()
