#!/usr/bin/env python3
"""
build_views.py — Generate purpose-specific views from the gate results.

data/ (active) + quarantine/ (held) are the source of truth; views/ is 100%
generated. View policies follow guide section 16:

  views/app/questions.jsonl      active records that pass the full gate (exam and/or flashcard mode)
  views/app/catalog.json         track -> topic -> chapter counts
  views/study/exam/<track>/<topic>.jsonl        exam gate only
  views/study/flashcards/<track>/<topic>.jsonl  flashcard gate only
  views/reels/candidates.jsonl|.csv             exam gate + commercial rights + concise + not yet used
  views/review/queue.jsonl|.csv                 every non-active record with reasons and next action
  views/MANIFEST.json                           counts
  reports/publishable_summary.md                the human-readable publishable-questions table
"""
import collections
import csv
import datetime
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402
import gates  # noqa: E402

VIEWS = os.path.join(taxonomy.ROOT, "views")
REEL_LEDGER = os.path.join(taxonomy.TAX, "reels_used.csv")


def slug(track_id):
    return re.sub(r"[^a-z0-9]+", "-", track_id.lower()).strip("-")


def correct_text(q):
    labels = q["correct_answer"] if isinstance(q["correct_answer"], list) else [q["correct_answer"]]
    by_label = {c["label"]: c["text"] for c in q.get("choices", [])}
    return " / ".join(by_label.get(l, l) for l in labels)


def app_record(q, ev):
    rec = {
        "questionId": q["question_id"], "questionVersion": q.get("question_version", 1),
        "authority": q["authority"], "licence": q["licence"], "trackId": q["track_id"],
        "applicableTracks": q["applicable_licences"], "topic": q["topic"], "topicName": q["topic_name"],
        "subject": q["subject"], "chapterTitle": q["chapter_title"],
        "learningObjective": q.get("learning_objective") or None,
        "learningObjectiveCode": q.get("learning_objective_code") or None,
        "questionType": q["question_type"], "questionText": q["question_text"], "choices": q.get("choices", []),
        "correctAnswer": q["correct_answer"], "explanation": q.get("explanation", ""),
        "incorrectAnswerExplanations": q.get("incorrect_answer_explanations") or {},
        "regulationReference": q.get("regulation_reference") or None,
        "handbookReference": q.get("handbook_reference") or None,
        "difficulty": q["difficulty"], "sourceTitle": q["source_title"], "sourceUrl": q.get("source_url") or None,
        "lastVerified": q.get("last_verified"),
        "requiresImage": bool(q.get("image_required")),
        "requiresScratchpad": q["question_type"] == "calculation" or bool(q.get("calculation_steps")),
        "modes": [m for m in ("exam", "flashcard") if ev[m]],
        "publicationTier": ev["tier"],
        "studyNotice": taxonomy.POLICY["study_tier"]["study_notice"],
    }
    if ev["tier"] == "study" and taxonomy.regulation_dependent(q):
        rec["regulatoryNotice"] = taxonomy.POLICY["study_tier"]["regulatory_notice"]
    if q.get("image_required"):
        rec["image"] = {"filePath": q["image_path"], "altText": q.get("image_alt_text"),
                        "attribution": q.get("image_attribution"), "licence": q.get("image_license")}
    return rec


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def reel_ok(q, used):
    choices = q.get("choices", [])
    return (q["question_id"] not in used and 3 <= len(choices) <= 4 and len(q["question_text"]) <= 140
            and max(len(c["text"]) for c in choices) <= 70)


def summary_table(bank, evs, path):
    """reports/publishable_summary.md — guide section 19.5 / 18 reporting."""
    rows = collections.OrderedDict()
    for q in sorted(bank, key=lambda q: (q["authority"], q["track_id"], q["topic"])):
        ev = evs[q["question_id"]]
        k = (q["authority"], q["track_id"])
        r = rows.setdefault(k, collections.Counter())
        r["canonical"] += 1
        r["exam"] += ev["exam"]
        r["flashcard"] += ev["flashcard"]
        r["verified_tier"] += ev["tier"] == "verified"
        r["study_tier"] += ev["tier"] == "study"
        r["reel"] += ev["reel"]
        r[q["status"]] += 1
        r["rights_blocked"] += "rights" in ev["failed"]
    tot = sum(rows.values(), collections.Counter())
    first = collections.Counter((evs[q["question_id"]]["failed"] or ["—"])[0] for q in bank)
    anyfail = collections.Counter(g for q in bank for g in evs[q["question_id"]]["failed"])
    states = collections.Counter(q["pipeline_state"] for q in bank)
    topics = collections.defaultdict(collections.Counter)
    for q in bank:
        ev = evs[q["question_id"]]
        topics[q["topic"]]["canonical"] += 1
        topics[q["topic"]]["exam"] += ev["exam"]
        topics[q["topic"]]["flashcard"] += ev["flashcard"]

    L = [f"# Publishable questions — {datetime.date.today().isoformat()}", "",
         "Generated by `scripts/build_views.py` from the per-record activation gate "
         "(`scripts/gates.py`, guide §15). Canonical count is **not** a usable count (guide §18).", "",
         f"Policy: platform_commercial = **{taxonomy.POLICY['platform_commercial']}**; "
         f"study tier enabled = **{taxonomy.POLICY['study_tier']['enabled']}** "
         "(verified tier = every gate; study tier = same correctness, rights and media gates, relaxed process gates).", "",
         "## By licence track", "",
         "| Authority | Track | Canonical | Published | of which verified tier | of which study tier | Active exam | Active flashcard | Reel-eligible | Quarantined | of which rights-blocked | Restricted | Historical/superseded | Rejected |",
         "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for (auth, track), r in rows.items():
        L.append(f"| {auth} | {track} | {r['canonical']} | {r['active']} | {r['verified_tier']} | {r['study_tier']} | {r['exam']} | {r['flashcard']} | {r['reel']} | "
                 f"{r['quarantined']} | {r['rights_blocked']} | {r['restricted_do_not_use']} | "
                 f"{r['historical_reference_only'] + r['superseded']} | {r['rejected']} |")
    L.append(f"| **Total** | | **{tot['canonical']}** | **{tot['active']}** | **{tot['verified_tier']}** | **{tot['study_tier']}** | **{tot['exam']}** | **{tot['flashcard']}** | **{tot['reel']}** | "
             f"**{tot['quarantined']}** | **{tot['rights_blocked']}** | **{tot['restricted_do_not_use']}** | "
             f"**{tot['historical_reference_only'] + tot['superseded']}** | **{tot['rejected']}** |")
    L += ["", "## By study area", "", "| Topic | Canonical | Active exam | Active flashcard |", "|---|---:|---:|---:|"]
    for t in taxonomy.TOPICS:
        c = topics.get(t, collections.Counter())
        L.append(f"| {t} | {c['canonical']} | {c['exam']} | {c['flashcard']} |")
    L += ["", "## Why records are held", "",
          "| Gate | First blocker (records) | Failing at all (records) | Next action |", "|---|---:|---:|---|"]
    for g in gates.NEXT_ACTION:
        if anyfail[g]:
            L.append(f"| {g} | {first[g]} | {anyfail[g]} | {gates.NEXT_ACTION[g]} |")
    L += ["", "## Pipeline state", "", "| State | Records |", "|---|---:|"]
    for s in gates.PIPELINE:
        if states[s]:
            L.append(f"| {s} | {states[s]} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    return tot


def main():
    bank = [q for _, rs in taxonomy.load_bank() for q in rs]
    evs = {q["question_id"]: gates.evaluate(q) for q in bank}

    if os.path.isdir(VIEWS):
        shutil.rmtree(VIEWS)
    manifest = {"built": datetime.date.today().isoformat(), "canonical": len(bank), "views": {}}

    active = [q for q in bank if q["status"] == "active" and evs[q["question_id"]]["flashcard"]]
    app = [app_record(q, evs[q["question_id"]]) for q in active]
    write_jsonl(os.path.join(VIEWS, "app", "questions.jsonl"), app)
    catalog = {}
    for r in app:
        for track in r["applicableTracks"]:
            tp = catalog.setdefault(track, {"topics": {}})["topics"].setdefault(
                r["topic"], {"name": r["topicName"], "exam": 0, "flashcard": 0, "chapters": {}})
            for m in r["modes"]:
                tp[m] += 1
            tp["chapters"][r["chapterTitle"]] = tp["chapters"].get(r["chapterTitle"], 0) + 1
    with open(os.path.join(VIEWS, "app", "catalog.json"), "w", encoding="utf-8") as f:
        json.dump({"built": manifest["built"], "tracks": dict(sorted(catalog.items()))}, f, ensure_ascii=False, indent=1)

    exam_b, card_b = collections.defaultdict(list), collections.defaultdict(list)
    rank = {"beginner": 0, "intermediate": 1, "advanced": 2}
    for q in sorted(active, key=lambda q: (rank[q["difficulty"]], q["question_id"])):
        ev = evs[q["question_id"]]
        for track in q["applicable_licences"]:
            if ev["exam"]:
                exam_b[(track, q["topic"])].append(q)
            card_b[(track, q["topic"])].append({
                "question_id": q["question_id"], "topic": q["topic"], "chapter_title": q["chapter_title"],
                "difficulty": q["difficulty"], "front": q["question_text"], "back": correct_text(q),
                "explanation": q.get("explanation", ""),
                "reference": q.get("regulation_reference") or q.get("handbook_reference") or ""})
    for (track, topic), rows in exam_b.items():
        write_jsonl(os.path.join(VIEWS, "study", "exam", slug(track), f"{topic.lower()}.jsonl"), rows)
    for (track, topic), rows in card_b.items():
        write_jsonl(os.path.join(VIEWS, "study", "flashcards", slug(track), f"{topic.lower()}.jsonl"), rows)

    used = set()
    if os.path.exists(REEL_LEDGER):
        with open(REEL_LEDGER, encoding="utf-8") as f:
            used = {r["question_id"] for r in csv.DictReader(f)}
    reels = [{"question_id": q["question_id"], "track_id": q["track_id"], "topic": q["topic"],
              "tag_line": f"{q['licence_level'].replace('_', ' ').upper()} · {q['topic_name'].upper()}",
              "question_text": q["question_text"], "choices": q["choices"], "correct_answer": q["correct_answer"],
              "correct_text": correct_text(q), "explanation": q.get("explanation", "")}
             for q in active if evs[q["question_id"]]["reel"] and reel_ok(q, used)]
    reels.sort(key=lambda r: (len(r["question_text"]), r["question_id"]))
    os.makedirs(os.path.join(VIEWS, "reels"), exist_ok=True)
    write_jsonl(os.path.join(VIEWS, "reels", "candidates.jsonl"), reels)
    write_csv(os.path.join(VIEWS, "reels", "candidates.csv"),
              [dict(r, choices=" | ".join(f"{c['label']}) {c['text']}" for c in r["choices"])) for r in reels],
              ["question_id", "topic", "tag_line", "question_text", "choices", "correct_answer", "correct_text"])

    review = [{"question_id": q["question_id"], "status": q["status"], "pipeline_state": q["pipeline_state"],
               "failed_gates": evs[q["question_id"]]["failed"], "next_action": evs[q["question_id"]]["next_action"],
               "hold_reasons": q.get("hold_reasons", []), "track_id": q["track_id"], "topic": q["topic"],
               "question_text": q["question_text"], "correct_text": correct_text(q)}
              for q in bank if q["status"] != "active"]
    write_jsonl(os.path.join(VIEWS, "review", "queue.jsonl"), review)
    write_csv(os.path.join(VIEWS, "review", "queue.csv"),
              [dict(r, failed_gates="|".join(r["failed_gates"]), hold_reasons="|".join(r["hold_reasons"])) for r in review],
              ["question_id", "status", "pipeline_state", "failed_gates", "next_action", "hold_reasons",
               "track_id", "topic", "question_text", "correct_text"])

    tot = summary_table(bank, evs, os.path.join(taxonomy.ROOT, "reports", "publishable_summary.md"))
    manifest["views"] = {"app": len(app), "exam": tot["exam"], "flashcard": tot["flashcard"], "reels": len(reels),
                         "review": len(review), "status": dict(collections.Counter(q["status"] for q in bank))}
    with open(os.path.join(VIEWS, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    print(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
