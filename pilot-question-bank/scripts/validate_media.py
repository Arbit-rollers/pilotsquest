#!/usr/bin/env python3
"""
validate_media.py — Check every image-dependent question against guide section 11.

    python3 scripts/validate_media.py            # report -> reports/media_report.csv
    python3 scripts/validate_media.py --fill-dimensions   # also record image_width/height from the file

Reports, per record: missing structured fields, missing file, rights record
missing or not permitting the intended use, alt text, verification flags.
It never marks anything verified — that is a review decision recorded via
scripts/release_questions.py (review_type media / accessibility).
"""
import argparse
import csv
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402
import gates  # noqa: E402

REQUIRED = ["image_id", "image_status", "image_path", "image_source_title", "image_license",
            "image_copyright_status", "image_attribution", "image_alt_text", "image_width", "image_height"]


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", head[16:24])
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fill-dimensions", action="store_true")
    args = ap.parse_args()
    files = taxonomy.load_logical_files()
    rows, changed = [], False
    for recs in files.values():
        for q in recs:
            if not q.get("image_required"):
                continue
            path = os.path.join(taxonomy.ROOT, q.get("image_path") or "")
            exists = bool(q.get("image_path")) and os.path.exists(path)
            if args.fill_dimensions and exists and not q.get("image_width"):
                w, h = png_size(path)
                if w:
                    q["image_width"], q["image_height"], changed = w, h, True
            rights = gates.RIGHTS.get(q.get("image_rights_record_id") or q.get("rights_record_id") or "")
            problems = [f"missing {k}" for k in REQUIRED if not q.get(k)]
            if not exists:
                problems.append("file not found")
            if not rights or rights["rights_review_status"] != "passed":
                problems.append("image rights not approved")
            elif taxonomy.POLICY["platform_commercial"] and rights["commercial_use"] != "permitted":
                problems.append("image rights forbid commercial use")
            if not q.get("image_verified"):
                problems.append("technical image review pending")
            if not q.get("image_accessibility_verified"):
                problems.append("accessibility review pending")
            rows.append({"question_id": q["question_id"], "image_status": q.get("image_status"),
                         "image_path": q.get("image_path", ""), "problems": "; ".join(problems) or "ok"})
    if changed:
        taxonomy.place(files)
    out = os.path.join(taxonomy.ROOT, "reports", "media_report.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["question_id", "image_status", "image_path", "problems"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} image-dependent record(s); ok: {sum(r['problems'] == 'ok' for r in rows)}; report: reports/media_report.csv")


if __name__ == "__main__":
    main()
