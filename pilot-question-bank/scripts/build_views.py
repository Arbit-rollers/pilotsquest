#!/usr/bin/env python3
"""
build_views.py — Generate purpose-specific views of the bank into views/.

data/ is the single source of truth. views/ is 100% generated: never edit
it by hand, never commit fixes there — fix data/ or taxonomy/ and rebuild.

Usage:
    python3 scripts/build_views.py

Outputs:
  views/app/questions.jsonl        PilotQuest import feed (camelCase, FullQuestionRecord shape)
  views/app/catalog.json           track -> topic -> chapter counts, for the learning map
  views/study/exam/<track>/<topic>.jsonl        exam-style practice per licence & subject
  views/study/flashcards/<track>/<topic>.jsonl  question -> answer recall cards
  views/reels/candidates.jsonl|.csv             ranked, screen-friendly reel questions
  views/review/queue.jsonl|.csv                 everything needing an instructor's decision
  views/MANIFEST.json                           counts per view + build date
"""
import csv
import collections
import datetime
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402

VIEWS = os.path.join(taxonomy.ROOT, "views")

# ---- Policy knobs -----------------------------------------------------------
# Flags that keep a usable question out of exam practice (it may still be a flashcard).
EXAM_BLOCKING_FLAGS = {"templated_distractors", "needs_figure", "missing_calculation_steps"}
# Flags that keep a question out of every student-facing view until reviewed.
# The Air Law audit v2 recommends holding these 230; set True to enforce it.
HOLD_PENDING_REVIEW = False
REVIEW_HOLD_FLAGS = {"audit_v2_pending_provision_review"}
REEL_LEDGER = os.path.join(taxonomy.TAX, "reels_used.csv")
# -----------------------------------------------------------------------------


def slug(track_id):
    return re.sub(r"[^a-z0-9]+", "-", track_id.lower()).strip("-")


def held(q):
    return HOLD_PENDING_REVIEW and bool(REVIEW_HOLD_FLAGS & set(q["quality_flags"]))


def modes(q):
    if not taxonomy.is_usable(q) or held(q):
        return []
    m = ["flashcard"]
    if q["question_style"] == "exam_style" and not (EXAM_BLOCKING_FLAGS & set(q["quality_flags"])):
        m.insert(0, "exam")
    return m


def correct_text(q):
    labels = q["correct_answer"] if isinstance(q["correct_answer"], list) else [q["correct_answer"]]
    by_label = {c["label"]: c["text"] for c in q.get("choices", [])}
    return " / ".join(by_label.get(l, l) for l in labels)


def app_record(q):
    media = (q.get("media") or [None])[0]
    rec = {
        "questionId": q["question_id"],
        "authority": q["authority"],
        "licence": q["licence"],
        "trackId": q["track_id"],
        "applicableTracks": q["applicable_licences"],
        "topic": q["topic"],
        "topicName": q["topic_name"],
        "subject": q["subject"],
        "chapterTitle": q["chapter_title"],
        "learningObjective": q.get("learning_objective") or None,
        "questionType": q["question_type"],
        "questionText": q["question_text"],
        "choices": q.get("choices", []),
        "correctAnswer": q["correct_answer"],
        "explanation": q.get("explanation", ""),
        "incorrectAnswerExplanations": q.get("incorrect_answer_explanations") or {},
        "regulationReference": q.get("regulation_reference") or None,
        "handbookReference": q.get("handbook_reference") or None,
        "difficulty": q["difficulty"],
        "sourceTitle": q["source_title"],
        "sourceUrl": q.get("source_url") or None,
        "lastVerified": q.get("last_verified"),
        "requiresImage": bool(media),
        "requiresScratchpad": q["question_type"] == "calculation" or bool(q.get("calculation_steps")),
        "modes": modes(q),
        "reviewPending": bool(REVIEW_HOLD_FLAGS & set(q["quality_flags"])),
        "nonCommercialOnly": "non_commercial_licence" in q["quality_flags"],
    }
    if media:
        rec["image"] = {"filePath": media["file_path"], "altText": media["alt_text"],
                        "attribution": media.get("attribution"), "licence": media["licence"]}
    return rec


def reel_score(q, used):
    """Return (score, reasons) or None if unsuitable for a 16:9 quiz board."""
    if "exam" not in modes(q) or q["question_type"] != "single_choice" or q.get("media"):
        return None
    # Reels promote PilotQuest, so non-commercial-only content is excluded.
    if q["question_id"] in used or (REVIEW_HOLD_FLAGS | {"non_commercial_licence"}) & set(q["quality_flags"]):
        return None
    choices = q.get("choices", [])
    longest = max((len(c["text"]) for c in choices), default=999)
    if not 3 <= len(choices) <= 4 or len(q["question_text"]) > 140 or longest > 70:
        return None
    score, why = 0, []
    if q["licence_level"] in ("private", "recreational"):
        score += 3; why.append("PPL-level audience")
    if len(q["question_text"]) <= 70:
        score += 2; why.append("short question")
    if longest <= 35:
        score += 1; why.append("short options")
    if q["provenance"] == "official_sample":
        score += 1; why.append("official sample")
    if q["topic"] in ("PRINCIPLES_OF_FLIGHT", "METEOROLOGY", "HUMAN_PERFORMANCE", "OPERATIONAL_PROCEDURES"):
        score += 1; why.append("visual/scenario topic")
    return score, why


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


def main():
    bank = []
    for path, recs in taxonomy.load_bank():
        for q in recs:
            if "topic" not in q:
                sys.exit(f"{q['question_id']} is not categorized — run scripts/categorize.py --write first")
            bank.append(q)

    if os.path.isdir(VIEWS):
        shutil.rmtree(VIEWS)
    manifest = {"built": datetime.date.today().isoformat(), "bank_total": len(bank), "views": {}}

    # --- app -----------------------------------------------------------------
    app = [app_record(q) for q in bank if modes(q)]
    write_jsonl(os.path.join(VIEWS, "app", "questions.jsonl"), app)
    catalog = {}
    for r in app:
        for track in r["applicableTracks"]:
            t = catalog.setdefault(track, {"topics": {}})
            tp = t["topics"].setdefault(r["topic"], {"name": r["topicName"], "exam": 0,
                                                      "flashcard": 0, "chapters": {}})
            for m in r["modes"]:
                tp[m] += 1
            tp["chapters"][r["chapterTitle"]] = tp["chapters"].get(r["chapterTitle"], 0) + 1
    with open(os.path.join(VIEWS, "app", "catalog.json"), "w", encoding="utf-8") as f:
        json.dump({"built": manifest["built"], "tracks": dict(sorted(catalog.items()))}, f,
                  ensure_ascii=False, indent=1)
    manifest["views"]["app"] = {"questions": len(app),
                                "exam": sum("exam" in r["modes"] for r in app),
                                "flashcard_only": sum(r["modes"] == ["flashcard"] for r in app)}

    # --- study: exam practice + flashcards, per licence track and topic -------
    exam_buckets, card_buckets = collections.defaultdict(list), collections.defaultdict(list)
    level_rank = {"beginner": 0, "intermediate": 1, "advanced": 2}
    for q in sorted(bank, key=lambda q: (level_rank[q["difficulty"]], q["question_id"])):
        m = modes(q)
        for track in q["applicable_licences"]:
            if "exam" in m:
                exam_buckets[(track, q["topic"])].append(q)
            if "flashcard" in m:
                card_buckets[(track, q["topic"])].append({
                    "question_id": q["question_id"], "topic": q["topic"],
                    "chapter_title": q["chapter_title"], "difficulty": q["difficulty"],
                    "front": q["question_text"], "back": correct_text(q),
                    "explanation": q.get("explanation", ""),
                    "reference": q.get("regulation_reference") or q.get("handbook_reference") or ""})
    for (track, topic), rows in exam_buckets.items():
        write_jsonl(os.path.join(VIEWS, "study", "exam", slug(track), f"{topic.lower()}.jsonl"), rows)
    for (track, topic), rows in card_buckets.items():
        write_jsonl(os.path.join(VIEWS, "study", "flashcards", slug(track), f"{topic.lower()}.jsonl"), rows)
    manifest["views"]["study"] = {
        "exam_files": len(exam_buckets), "flashcard_files": len(card_buckets),
        "exam_by_track": dict(sorted(collections.Counter(t for (t, _), v in exam_buckets.items()
                                                         for _ in v).items())),
        "flashcards_by_track": dict(sorted(collections.Counter(t for (t, _), v in card_buckets.items()
                                                               for _ in v).items()))}

    # --- reels ----------------------------------------------------------------
    used = set()
    if os.path.exists(REEL_LEDGER):
        with open(REEL_LEDGER, encoding="utf-8") as f:
            used = {r["question_id"] for r in csv.DictReader(f)}
    reels = []
    for q in bank:
        s = reel_score(q, used)
        if s:
            reels.append({"reel_score": s[0], "why": "; ".join(s[1]), "question_id": q["question_id"],
                          "track_id": q["track_id"], "topic": q["topic"],
                          "tag_line": f"{q['licence_level'].replace('_', ' ').upper()} · {q['topic_name'].upper()}",
                          "question_text": q["question_text"], "choices": q["choices"],
                          "correct_answer": q["correct_answer"], "correct_text": correct_text(q),
                          "explanation": q.get("explanation", "")})
    reels.sort(key=lambda r: (-r["reel_score"], r["question_id"]))
    os.makedirs(os.path.join(VIEWS, "reels"), exist_ok=True)
    write_jsonl(os.path.join(VIEWS, "reels", "candidates.jsonl"), reels)
    write_csv(os.path.join(VIEWS, "reels", "candidates.csv"),
              [dict(r, choices=" | ".join(f"{c['label']}) {c['text']}" for c in r["choices"])) for r in reels],
              ["reel_score", "question_id", "topic", "question_text", "choices", "correct_answer",
               "correct_text", "why"])
    manifest["views"]["reels"] = {"candidates": len(reels), "already_used": len(used)}

    # --- review queue -----------------------------------------------------------
    review = []
    for q in bank:
        flags = [f for f in q["quality_flags"] if f not in ("templated_distractors", "non_commercial_licence")]
        if flags or not taxonomy.is_usable(q):
            review.append({"question_id": q["question_id"], "status": q["status"],
                           "reuse_allowed": q["reuse_allowed"], "flags": flags,
                           "track_id": q["track_id"], "topic": q["topic"],
                           "chapter_title": q["chapter_title"],
                           "question_text": q["question_text"], "correct_text": correct_text(q),
                           "regulation_reference": q.get("regulation_reference", "")})
    write_jsonl(os.path.join(VIEWS, "review", "queue.jsonl"), review)
    write_csv(os.path.join(VIEWS, "review", "queue.csv"),
              [dict(r, flags="|".join(r["flags"])) for r in review],
              ["question_id", "status", "reuse_allowed", "flags", "track_id", "topic",
               "chapter_title", "question_text", "correct_text", "regulation_reference"])
    manifest["views"]["review"] = {"items": len(review),
                                   "by_flag": dict(collections.Counter(f for r in review for f in r["flags"]))}

    with open(os.path.join(VIEWS, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    print(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
