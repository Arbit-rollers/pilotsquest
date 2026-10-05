#!/usr/bin/env python3
"""
ingest_pdf.py — Register a PDF source and extract raw question records.
Never publishes and never writes to data/ or quarantine/.

  1. Register (guide section 4) — hash, page count, text/scanned detection, manifest entry:
     python3 scripts/ingest_pdf.py inbox/tp13014.pdf --register --source-id SRC-TC-TP13014 \
         --title "..." --publisher "Transport Canada" --rights-record RR-TC-TP13014

  2. Extract (section 5) — per-page text + raw question records, exact wording, no repairs:
     python3 scripts/ingest_pdf.py inbox/tp13014.pdf --extract --source-id SRC-TC-TP13014 \
         --question-pages 5-30 [--answer-key-pages 38-40]

  3. Build an injectable batch (sections 6-7) from the raw records:
     python3 scripts/ingest_pdf.py --to-batch --source-id SRC-TC-TP13014 --defaults inbox/tp13014.defaults.json
     -> inbox/SRC-TC-TP13014.jsonl, then scripts/inject_questions.py as usual

Output:
  sources/source_manifest.json                     registration entry (fill the TODO fields by hand)
  extracted/<source_id>/pages/page-NNN.txt         raw page text (pdftotext -layout)
  extracted/<source_id>/raw_questions.jsonl        immutable source extraction records
  extracted/<source_id>/answer_key.jsonl           parsed answer-key entries
  extracted/<source_id>/extraction_report.md       section 18 counts for this PDF

extracted/ is git-ignored: it can contain copyrighted wording that must never be published.
Question segmentation is heuristic (numbered stems, lettered/numbered options); every
record the parser is unsure about is marked extraction_uncertain and will quarantine.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "sources", "source_manifest.json")
TODAY = datetime.date.today().isoformat()
Q_START = re.compile(r"^\s*(\d{1,4})[.)]\s+(\S.*)$")
OPT = re.compile(r"^\s*(?:\(?([A-Ea-e])[.)]|\(([1-5])\))\s+(\S.*)$")
KEY = re.compile(r"(\d{1,4})\s*[-.:)]\s*\(?([A-Ea-e1-5])\)?")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def pages(spec):
    out = []
    for part in (spec or "").split(","):
        if "-" in part:
            a, b = part.split("-")
            out += range(int(a), int(b) + 1)
        elif part.strip():
            out.append(int(part))
    return out


def load_manifest():
    return json.load(open(MANIFEST, encoding="utf-8")) if os.path.exists(MANIFEST) else {}


def register(args):
    info = run(["pdfinfo", args.pdf])
    n = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    sample = [p for p in range(1, n + 1, max(1, n // 10))]
    chars = [len(run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", args.pdf, "-"]).strip()) for p in sample]
    scanned = sum(c < 80 for c in chars) > len(chars) / 2
    h = hashlib.sha256(open(args.pdf, "rb").read()).hexdigest()
    m = load_manifest()
    m[args.source_id] = {
        "source_id": args.source_id, "original_filename": os.path.basename(args.pdf), "sha256": h,
        "title": args.title or "TODO", "publisher": args.publisher or "TODO", "edition_or_revision": "TODO",
        "publication_date": "TODO", "stated_syllabus_version": "TODO", "page_count": n, "language": "TODO",
        "intended_authority": "TODO", "jurisdiction": "TODO", "licence": "TODO", "aircraft_category": "TODO",
        "question_pages": "TODO", "answer_key_pages": "TODO", "explanation_pages": "TODO", "figure_pages": "TODO",
        "native_text_or_scanned": "scanned" if scanned else "native_text",
        "copyright_notice": "TODO (copy verbatim from the PDF)", "commercial_use": "TODO",
        "rights_record_id": args.rights_record or "TODO", "accessed_date": TODAY,
        "quality_notes": "", "registered": TODAY, "raw_file": os.path.relpath(os.path.abspath(args.pdf), os.path.dirname(ROOT)),
        "_rule": "Do not infer validity, reuse permission or authority from filename/publisher/upload description (section 4).",
    }
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    json.dump(m, open(MANIFEST, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"registered {args.source_id}: {n} pages, {'SCANNED (OCR needed)' if scanned else 'native text'}, sha256 {h[:12]}…")
    print("Fill every TODO in sources/source_manifest.json before extracting.")


def extract(args):
    m = load_manifest()
    src = m.get(args.source_id)
    if not src:
        sys.exit("register the source first (--register)")
    todo = [k for k, v in src.items() if v == "TODO"]
    if todo:
        print(f"WARNING manifest still has TODO fields: {todo}")
    if hashlib.sha256(open(args.pdf, "rb").read()).hexdigest() != src["sha256"]:
        sys.exit("file hash differs from the registered source — register this edition separately")
    out = os.path.join(ROOT, "extracted", args.source_id)
    os.makedirs(os.path.join(out, "pages"), exist_ok=True)
    method = "ocr" if src["native_text_or_scanned"] == "scanned" else "native_text"
    if method == "ocr":
        sys.exit("scanned PDF: run OCR first (e.g. ocrmypdf) and register the OCR'd file as its own source")

    recs, cur, opt_label = [], None, None
    for p in pages(args.question_pages):
        text = run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", args.pdf, "-"])
        open(os.path.join(out, "pages", f"page-{p:03d}.txt"), "w", encoding="utf-8").write(text)
        for line in text.splitlines():
            q, o = Q_START.match(line), OPT.match(line)
            if o and cur is not None:
                cur["original_choices"].append({"label": (o.group(1) or o.group(2)).upper(), "text": o.group(3).rstrip()})
                opt_label = True
            elif q and (cur is None or cur["original_choices"]):
                cur = {"source_id": args.source_id, "source_record_id": f"{args.source_id}-Q{q.group(1)}",
                       "source_question_number": q.group(1), "source_page": p,
                       "original_question_text": q.group(2).rstrip(), "original_choices": [],
                       "extraction_method": method, "ocr_uncertainties": [],
                       "figure_reference": "", "extracted": TODAY}
                recs.append(cur)
                opt_label = False
            elif cur is not None and line.strip():
                tgt = cur["original_choices"][-1] if opt_label and cur["original_choices"] else cur
                key = "text" if tgt is not cur else "original_question_text"
                tgt[key] = (tgt[key] + " " + line.strip()).strip()
    # uncertainty marking (never repaired in the raw layer)
    nums = [int(r["source_question_number"]) for r in recs]
    for r in recs:
        why = []
        labels = [c["label"] for c in r["original_choices"]]
        if len(labels) < 2:
            why.append("fewer than 2 options detected")
        if labels and labels != sorted(labels):
            why.append("option labels out of order")
        if re.search(r"(refer to|figure|appendix|diagram|chart)", r["original_question_text"], re.I):
            r["figure_reference"] = "yes"
        if re.search(r"[^\x00-\x7F°±×÷–—’‘“”…µ·²³]", r["original_question_text"]):
            why.append("non-ASCII symbols: check units/superscripts")
        if nums.count(int(r["source_question_number"])) > 1:
            why.append("duplicate question number")
        r["ocr_uncertainties"] = why
        r["extraction_uncertain"] = bool(why)
    gaps = sorted(set(range(min(nums), max(nums) + 1)) - set(nums)) if nums else []

    key = {}
    for p in pages(args.answer_key_pages):
        text = run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", args.pdf, "-"])
        open(os.path.join(out, "pages", f"page-{p:03d}.txt"), "w", encoding="utf-8").write(text)
        for n, a in KEY.findall(text):
            key.setdefault(n, []).append({"answer": a.upper(), "page": p})
    with open(os.path.join(out, "answer_key.jsonl"), "w", encoding="utf-8") as f:
        for n, v in sorted(key.items(), key=lambda x: int(x[0])):
            f.write(json.dumps({"question_number": n, "entries": v}) + "\n")
    for r in recs:
        hits = key.get(r["source_question_number"], [])
        labels = {c["label"] for c in r["original_choices"]}
        if len(hits) == 1 and hits[0]["answer"] in labels:
            r.update(original_stated_answer=hits[0]["answer"], source_answer_page=hits[0]["page"], answer_match_confidence=1.0)
        elif hits:
            r.update(original_stated_answer=hits[0]["answer"], source_answer_page=hits[0]["page"],
                     answer_match_confidence=0.5, answer_match_note=f"{len(hits)} key entries or label not among options")
        else:
            r.update(original_stated_answer="", source_answer_page=None, answer_match_confidence=0.0 if key else None)
    with open(os.path.join(out, "raw_questions.jsonl"), "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    c = Counter(r["answer_match_confidence"] for r in recs)
    report = [f"# Extraction report — {args.source_id} ({TODAY})", "",
              f"- Pages inspected: question pages {args.question_pages}, answer-key pages {args.answer_key_pages or 'none'}",
              f"- Questions detected: {len(recs)} (numbers {min(nums) if nums else '-'}–{max(nums) if nums else '-'}; gaps: {gaps or 'none'})",
              f"- Extraction uncertain: {sum(r['extraction_uncertain'] for r in recs)}",
              f"- Figure/table references: {sum(r['figure_reference'] == 'yes' for r in recs)}",
              f"- Answers matched (confidence 1.0): {c[1.0]}; ambiguous: {c[0.5]}; unmatched: {c[0.0] + c[None]}",
              "- Extracted count is NOT a usable count. Everything goes through inject → quarantine → review → release."]
    open(os.path.join(out, "extraction_report.md"), "w", encoding="utf-8").write("\n".join(report) + "\n")
    print("\n".join(report))


def to_batch(args):
    raw = os.path.join(ROOT, "extracted", args.source_id, "raw_questions.jsonl")
    defaults = json.load(open(args.defaults, encoding="utf-8")) if args.defaults else {}
    out = os.path.join(ROOT, "inbox", f"{args.source_id}.jsonl")
    n = 0
    with open(out, "w", encoding="utf-8") as f:
        for line in open(raw, encoding="utf-8"):
            r = json.loads(line)
            rec = {**defaults, **{k: v for k, v in r.items() if k not in ("extracted",)}}
            rec["question_text"] = r["original_question_text"]
            # display labels A-D; the source's own labels stay in extracted/ and original_stated_answer
            to_letter = {c["label"]: "ABCDE"[i] for i, c in enumerate(r["original_choices"])}
            rec["choices"] = [{"label": to_letter[c["label"]], "text": c["text"]} for c in r["original_choices"]]
            rec["correct_answer"] = to_letter.get(r.get("original_stated_answer", ""), "")
            rec["original_choices"] = [c["text"] for c in r["original_choices"]]
            rec["source_has_answer_key"] = r.get("answer_match_confidence") is not None
            rec["hold_reasons"] = (["extraction uncertain: " + "; ".join(r["ocr_uncertainties"])] if r.get("extraction_uncertain") else [])
            if r.get("figure_reference") == "yes":
                rec.update(image_required=True, image_status="missing", media_review_status="pending",
                           image_verified=False, image_accessibility_verified=False)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    print(f"{n} record(s) -> {os.path.relpath(out, ROOT)}; next: scripts/inject_questions.py {os.path.relpath(out, ROOT)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("--source-id", required=True)
    ap.add_argument("--register", action="store_true")
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--to-batch", action="store_true")
    ap.add_argument("--title")
    ap.add_argument("--publisher")
    ap.add_argument("--rights-record")
    ap.add_argument("--question-pages")
    ap.add_argument("--answer-key-pages", default="")
    ap.add_argument("--defaults")
    args = ap.parse_args()
    if args.register:
        register(args)
    if args.extract:
        if not args.question_pages:
            sys.exit("--question-pages is required")
        extract(args)
    if args.to_batch:
        to_batch(args)


if __name__ == "__main__":
    main()
