#!/usr/bin/env python3
"""
gates.py — The per-record activation gate (guide section 15) and pipeline state.

A record is active only when every applicable gate passes. Nothing here
can be overridden by a flag, an approval file or a batch-level statement:
approvals only change review *statuses*, and this module re-derives the
outcome from those statuses every time.

    evaluate(q) -> {"gates": {name: (passed, reason)}, "exam": bool,
                    "flashcard": bool, "reel": bool, "status": str,
                    "pipeline_state": str, "blockers": [..], "next_action": str}
"""
import csv
import os
from collections import OrderedDict

import taxonomy

POLICY = taxonomy.POLICY
PIPELINE = ["received", "extracted", "answer_matched", "classified", "rights_reviewed",
            "technically_verified", "regulatorily_verified", "media_verified",
            "duplicate_reviewed", "approved", "active"]
TERMINAL = {"restricted_do_not_use", "historical_reference_only", "superseded", "rejected"}

with open(os.path.join(taxonomy.TAX, "rights_records.csv"), encoding="utf-8", newline="") as _f:
    RIGHTS = {r["rights_record_id"]: r for r in csv.DictReader(_f)}

NEXT_ACTION = {
    "extraction": "re-extract or fix OCR uncertainty in a new version",
    "answer_match": "confirm the answer against the source answer key page",
    "classification": "fill authority/jurisdiction/licence/category/syllabus_version",
    "objective": "map exactly one official learning objective (learning_objective_code)",
    "technical": "independent technical review (one defensible answer)",
    "second_check": "second independent check (calculation / safety-critical / regulatory)",
    "regulatory": "verify against the current controlling provision; record provision, effective & access dates",
    "citation": "add a precise primary-source citation",
    "provenance": "provenance class is not publishable",
    "rights": "rights record missing, pending, or forbids the intended (commercial) use",
    "media": "attach a cleared, verified, accessible image",
    "duplicate": "resolve the duplicate group",
    "editorial": "editorial review (clarity, grammar, distractor quality)",
    "hold": "resolve the recorded hold reason",
    "flags": "resolve blocking quality flags",
}


def _rights_ok(q):
    r = RIGHTS.get(q.get("rights_record_id") or "")
    if not r:
        return False, "no rights record"
    if r["rights_review_status"] != "passed":
        return False, f"{r['rights_record_id']}: review {r['rights_review_status']}"
    if POLICY["platform_commercial"] and r["commercial_use"] != "permitted":
        return False, f"{r['rights_record_id']}: commercial use {r['commercial_use']}"
    return True, r["rights_record_id"]


def evaluate(q):
    g = OrderedDict()
    flags = set(q.get("quality_flags") or [])

    g["extraction"] = (q.get("extraction_method") in ("native_text", "ocr", "manual")
                       and not q.get("ocr_uncertainties")
                       and (q.get("extraction_confidence") is None
                            or q["extraction_confidence"] >= POLICY["extraction_min_confidence"]),
                       q.get("extraction_method") or "no extraction method")
    if q.get("source_has_answer_key"):
        c = q.get("answer_match_confidence")
        g["answer_match"] = (c is not None and c >= POLICY["answer_match_min_confidence"],
                             f"confidence {c}")
    else:
        g["answer_match"] = (True, "no source key (answer carried by technical review)")
    missing = [k for k in ("authority", "country_or_region", "licence", "aircraft_category",
                           "syllabus_version", "track_id") if not q.get(k)]
    g["classification"] = (not missing, "missing " + ",".join(missing) if missing else "ok")
    g["objective"] = (bool(q.get("learning_objective_code")), q.get("learning_objective_code") or "no LO code")
    g["rights"] = _rights_ok(q)
    g["technical"] = (q.get("technical_review_status") == "passed", q.get("technical_review_status"))
    if taxonomy.needs_second_check(q):
        g["second_check"] = (q.get("second_check_status") == "passed", q.get("second_check_status"))
    if taxonomy.regulation_dependent(q):
        ok = (q.get("regulatory_status") == "current_verified"
              and q.get("regulatory_review_status") == "passed"
              and all(q.get(k) for k in ("regulation_provision", "source_effective_date", "source_accessed_date")))
        g["regulatory"] = (ok, q.get("regulatory_status") or "not verified")
    g["citation"] = (bool(q.get("regulation_reference") or q.get("handbook_reference")), "")
    g["provenance"] = (q.get("provenance") in taxonomy.USABLE_PROVENANCE, q.get("provenance"))
    if q.get("image_required"):
        path = os.path.join(taxonomy.ROOT, q.get("image_path") or "")
        ok = (q.get("image_status") == "ready" and q.get("image_verified") is True
              and q.get("image_accessibility_verified") is True and q.get("media_review_status") == "passed"
              and bool(q.get("image_path")) and os.path.exists(path))
        g["media"] = (ok, f"image_status={q.get('image_status')}")
    g["duplicate"] = (q.get("duplicate_review_status") == "passed", q.get("duplicate_review_status"))
    g["editorial"] = (q.get("editorial_review_status") == "passed", q.get("editorial_review_status"))
    g["hold"] = (not q.get("hold_reasons"), "; ".join(q.get("hold_reasons") or []))
    blocking = flags & set(POLICY["blocking_quality_flags"])
    g["flags"] = (not blocking, ",".join(sorted(blocking)))

    verified_failed = [k for k, (ok, _) in g.items() if not ok]
    study_g = study_gates(q, g)
    study_failed = [k for k, (ok, _) in study_g.items() if not ok]
    tier = "verified" if not verified_failed else ("study" if POLICY["study_tier"]["enabled"] and not study_failed else "")
    failed = [] if tier else study_failed
    reg = taxonomy.regulation_dependent(q)
    flashcard = bool(tier)
    exam = flashcard and q.get("question_style") == "exam_style" \
        and not (flags & set(POLICY["exam_only_blocking_flags"]))
    reel = exam and q.get("question_type") == "single_choice" and not q.get("image_required") \
        and (tier == "verified" or not reg or POLICY["study_tier"]["reels_allow_regulation_dependent"])

    if q.get("provenance") == "restricted_do_not_use":
        status = "restricted_do_not_use"
    elif q.get("status") in TERMINAL:
        status = q["status"]
    elif q.get("regulatory_status") in ("historical_reference_only", "superseded"):
        status = q["regulatory_status"]
    else:
        status = "active" if flashcard else "quarantined"

    return {"gates": g, "study_gates": study_g, "failed": failed, "tier": tier,
            "verified_gaps": verified_failed if tier == "study" else [],
            "exam": exam, "flashcard": flashcard, "reel": reel,
            "status": status, "pipeline_state": pipeline_state(g, status),
            "next_action": NEXT_ACTION[failed[0]] if failed else ""}


def study_gates(q, g):
    """Study tier (owner decision 2026-10-05): same correctness/legal/media gates, relaxed process gates."""
    st = POLICY["study_tier"]
    sg = OrderedDict((k, v) for k, v in g.items() if k not in st["relaxed_gates"])
    optional = set(st["classification_optional_fields"])
    missing = [k for k in ("authority", "country_or_region", "licence", "aircraft_category",
                           "syllabus_version", "track_id") if not q.get(k) and k not in optional]
    sg["classification"] = (not missing, "missing " + ",".join(missing) if missing else "ok")
    if "regulatory" in sg:
        ok = q.get("regulatory_status") in st["regulatory_statuses_allowed"] and bool(q.get("regulation_provision"))
        sg["regulatory"] = (ok, q.get("regulatory_status") or "no first-pass rule check")
    holds = [h for h in (q.get("hold_reasons") or [])
             if not any(sub in h for sub in st["nonblocking_hold_reason_substrings"])]
    sg["hold"] = (not holds, "; ".join(holds))
    return sg


def pipeline_state(g, status):
    if status == "active":
        return "active"
    order = [("extracted", ["extraction"]), ("answer_matched", ["answer_match"]),
             ("classified", ["classification", "objective"]), ("rights_reviewed", ["rights", "provenance"]),
             ("technically_verified", ["technical", "second_check", "citation"]),
             ("regulatorily_verified", ["regulatory"]), ("media_verified", ["media"]),
             ("duplicate_reviewed", ["duplicate"]),
             ("approved", ["editorial", "hold", "flags"])]
    state = "received"
    for name, keys in order:
        if all(g.get(k, (True,))[0] for k in keys):
            state = name
        else:
            break
    return state


def apply(q):
    """Write gate outcome fields onto the record; returns the evaluation."""
    ev = evaluate(q)
    q["status"] = ev["status"]
    q["pipeline_state"] = ev["pipeline_state"]
    q["active_study_bank"] = ev["status"] == "active"
    q["gate_failures"] = ev["failed"]
    q["next_action"] = ev["next_action"]
    q["publication_tier"] = ev["tier"]
    q["verified_tier_gaps"] = ev["verified_gaps"]
    q["reuse_allowed"] = ev["gates"]["rights"][0] and q.get("provenance") in taxonomy.USABLE_PROVENANCE
    # verified is derived: true only when every applicable review has passed
    reviews = ("technical", "second_check", "regulatory", "media", "duplicate", "editorial")
    q["verified"] = all(ev["gates"][k][0] for k in reviews if k in ev["gates"])
    dates = [h.get("date") for h in q.get("review_history") or [] if h.get("date")]
    if q["verified"] and dates:
        q["last_verified"] = max(dates + [q.get("last_verified") or ""])
    return ev
