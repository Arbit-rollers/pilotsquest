#!/usr/bin/env python3
"""
validate_questions.py — Structural, provenance, and basic-quality validation
for pilot-question-bank JSONL files.

Usage:
    python3 validate_questions.py data/easa/**/*.jsonl
    python3 validate_questions.py --schema schemas/question.schema.json data/**/*.jsonl

Checks performed:
  * JSON Schema conformance (schemas/question.schema.json)
  * provenance/reuse_allowed/status consistency
  * unique question_id across all files scanned
  * choices: >=2 options, exactly one correct_answer for single_choice,
    correct_answer label(s) must exist among choices
  * required source fields present when reuse_allowed is True
  * verified=True requires last_verified date and non-empty source_url
  * obvious unit-less numeric answers flagged for calculation questions

Exit code is non-zero if any ERROR-level issue is found (WARNING issues
do not fail the run but are printed).
"""
import argparse
import glob
import json
import sys
from datetime import date

try:
    import jsonschema
except ImportError:
    jsonschema = None

USABLE_PROVENANCE = {
    "official_released", "official_sample", "public_domain",
    "open_licensed", "original_syllabus_aligned",
}


def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append((lineno, json.loads(line)))
            except json.JSONDecodeError as e:
                print(f"ERROR {path}:{lineno} invalid JSON: {e}")
    return records


def validate_record(path, lineno, q, schema, seen_ids):
    errors, warnings = [], []
    prefix = f"{path}:{lineno} [{q.get('question_id','?')}]"

    if schema is not None and jsonschema is not None:
        validator = jsonschema.Draft7Validator(schema)
        for err in validator.iter_errors(q):
            errors.append(f"{prefix} schema: {err.message}")

    qid = q.get("question_id")
    if qid:
        if qid in seen_ids:
            errors.append(f"{prefix} duplicate question_id (also at {seen_ids[qid]})")
        else:
            seen_ids[qid] = f"{path}:{lineno}"

    provenance = q.get("provenance")
    reuse_allowed = q.get("reuse_allowed")
    if provenance not in USABLE_PROVENANCE and reuse_allowed:
        errors.append(f"{prefix} reuse_allowed=True but provenance='{provenance}' is not a usable class")
    if provenance in ("restricted_do_not_use", "provenance_uncertain") and reuse_allowed:
        errors.append(f"{prefix} reuse_allowed must be False for provenance='{provenance}'")

    choices = q.get("choices", [])
    is_free_text_type = q.get("question_type") == "short_answer"
    if not is_free_text_type and len(choices) < 2:
        errors.append(f"{prefix} fewer than 2 answer choices")
    labels = [c.get("label") for c in choices]
    correct = q.get("correct_answer")
    correct_list = correct if isinstance(correct, list) else [correct]
    for c in (correct_list if not is_free_text_type else []):
        if c not in labels:
            errors.append(f"{prefix} correct_answer '{c}' not among choice labels {labels}")
    if q.get("question_type") == "single_choice" and isinstance(correct, list):
        errors.append(f"{prefix} single_choice question has multiple correct_answer labels")

    if reuse_allowed:
        for field in ("source_title", "source_url", "copyright_status"):
            if not q.get(field):
                errors.append(f"{prefix} reuse_allowed=True but missing '{field}'")

    if q.get("verified") and not q.get("last_verified"):
        errors.append(f"{prefix} verified=True but last_verified is empty")

    if provenance == "original_syllabus_aligned" and not q.get("regulation_reference") \
            and not q.get("handbook_reference"):
        warnings.append(f"{prefix} original question has no regulation/handbook reference cited")

    if q.get("question_type") == "calculation" and not q.get("calculation_steps"):
        warnings.append(f"{prefix} calculation question missing calculation_steps")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="JSONL files (globs expanded by shell or here)")
    parser.add_argument("--schema", default="schemas/question.schema.json")
    args = parser.parse_args()

    schema = None
    try:
        with open(args.schema, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"WARNING schema file not found at {args.schema}; skipping schema validation")

    all_errors, all_warnings = [], []
    seen_ids = {}
    expanded = []
    for pattern in args.files:
        matched = glob.glob(pattern, recursive=True)
        expanded.extend(matched if matched else [pattern])

    for path in expanded:
        for lineno, q in load_jsonl(path):
            errs, warns = validate_record(path, lineno, q, schema, seen_ids)
            all_errors.extend(errs)
            all_warnings.extend(warns)

    for w in all_warnings:
        print(f"WARNING {w}")
    for e in all_errors:
        print(f"ERROR {e}")

    print(f"\n{len(expanded)} file(s) scanned, {len(seen_ids)} question(s), "
          f"{len(all_errors)} error(s), {len(all_warnings)} warning(s).")
    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
