#!/usr/bin/env python3
"""
taxonomy.py — Shared categorization logic for the pilot question bank.

Used by categorize.py (backfill/re-check of data/) and inject_questions.py
(new batches), so a question is categorized identically no matter how it
entered the bank.

Every record gets these derived fields (never hand-edit them; change the
rules in taxonomy/ instead and re-run categorize.py):

  topic / topic_name     cross-authority study area (taxonomy/topics.json)
  topic_source           explicit | override | rule (how topic was decided)
  track_id               "<AUTHORITY>:<LICENCE>" key the app uses
  licence_level          recreational|private|commercial|airline_transport|instructor|remote_pilot
  aircraft_class         aeroplane|helicopter|glider|ultralight|uas
  applicable_licences    own track + reviewer-approved mappings only
  chapter_title          backfilled from subject when the source had none
  question_style         exam_style | concept_recall
  quality_flags          list of open quality issues (empty = clean)

The authority's own wording (subject, subject_code, licence,
aircraft_category) is never rewritten, except for FAA ACS area-name
labels that contradicted their own ACS code (see fix_acs_area_label).
"""
import csv
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAX = os.path.join(ROOT, "taxonomy")

USABLE_PROVENANCE = {
    "official_released", "official_sample", "public_domain",
    "open_licensed", "original_syllabus_aligned",
}

# ACS Areas of Operation by test prefix (FAA-S-ACS-6C Private, -7B
# Commercial, -10B Remote Pilot). Used only to correct the human-written
# area label in front of " - " in `subject`; the ACS code itself is from
# the source and is trusted.
ACS_AREAS = {
    "PA": {"I": "Preflight Preparation", "II": "Preflight Procedures",
           "III": "Airport and Seaplane Base Operations",
           "IV": "Takeoffs, Landings, and Go-Arounds",
           "V": "Performance and Ground Reference Maneuvers", "VI": "Navigation",
           "VII": "Slow Flight and Stalls", "VIII": "Basic Instrument Maneuvers",
           "IX": "Emergency Operations", "X": "Multiengine Operations",
           "XI": "Night Operations", "XII": "Postflight Procedures"},
    "CA": {"I": "Preflight Preparation", "II": "Preflight Procedures",
           "III": "Airport and Seaplane Base Operations",
           "IV": "Takeoffs, Landings, and Go-Arounds",
           "V": "Performance Maneuvers and Ground Reference Maneuvers",
           "VI": "Navigation", "VII": "Slow Flight and Stalls",
           "VIII": "High-Altitude Operations", "IX": "Emergency Operations",
           "X": "Multiengine Operations", "XI": "Postflight Procedures"},
    "UA": {"I": "Regulations", "II": "Airspace and Requirements",
           "III": "Weather", "IV": "Loading and Performance", "V": "Operations"},
}

CONCEPT_RECALL_PATTERN = re.compile(
    r"^(What is |Why is .+ important|How should a pilot apply knowledge of |"
    r"What limitation or common mistake)")


def _load_json(name):
    with open(os.path.join(TAX, name), encoding="utf-8") as f:
        return json.load(f)


def _load_csv(name):
    with open(os.path.join(TAX, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


TOPICS = {t["id"]: t for t in _load_json("topics.json")["topics"]}
_LIC = _load_json("licences.json")
SUBJECT_RULES = _load_csv("subject_rules.csv")
TOPIC_OVERRIDES = {r["question_id"]: r["topic"] for r in _load_csv("topic_overrides.csv")}
APPLICABILITY = _load_csv("applicability.csv")
STYLE_OVERRIDES = ({r["question_id"]: r["question_style"] for r in _load_csv("style_overrides.csv")}
                   if os.path.exists(os.path.join(TAX, "style_overrides.csv")) else {})
POLICY = _load_json("policy.json")
AUDIT_FLAGS = {}
if os.path.exists(os.path.join(TAX, "review_flags.csv")):
    for r in _load_csv("review_flags.csv"):
        AUDIT_FLAGS.setdefault(r["question_id"], []).append(r["flag"])


class CategorizationError(ValueError):
    pass


def licence_info(q):
    key = f"{q.get('authority')}|{q.get('licence')}"
    info = _LIC["by_authority_override"].get(key) or _LIC["licences"].get(q.get("licence"))
    if not info:
        raise CategorizationError(
            f"{q.get('question_id')}: licence '{q.get('licence')}' for authority "
            f"'{q.get('authority')}' is not in taxonomy/licences.json — add it first")
    return info


def classify_topic(q):
    """Return (topic, topic_source).

    Contributor-set topic (topic_source == "explicit") > per-question
    override > first matching rule in taxonomy/subject_rules.csv.
    """
    explicit = q.get("topic")
    if explicit in TOPICS and q.get("topic_source") == "explicit":
        return explicit, "explicit"
    qid = q.get("question_id")
    if qid in TOPIC_OVERRIDES:
        return TOPIC_OVERRIDES[qid], "override"
    authority = q.get("authority", "")
    code = q.get("subject_code", "") or ""
    subject = q.get("subject", "") or ""
    for rule in SUBJECT_RULES:
        if rule["authority"] not in ("*", authority):
            continue
        if rule["subject_code_regex"] and not re.search(rule["subject_code_regex"], code):
            continue
        if rule["subject_regex"] and not re.search(rule["subject_regex"], subject, re.I):
            continue
        return rule["topic"], "rule"
    raise CategorizationError(
        f"{qid}: no topic rule matches authority='{authority}' subject_code='{code}' "
        f"subject='{subject}'. Set \"topic\" on the record or add a rule to "
        f"taxonomy/subject_rules.csv")


def fix_acs_area_label(q):
    """Return corrected `subject` if its ACS area prefix contradicts the ACS code, else None."""
    m = re.match(r"^(PA|CA|UA)-([IVX]+)-", q.get("subject_code") or "")
    subject = q.get("subject") or ""
    if not m or " - " not in subject:
        return None
    area = ACS_AREAS[m.group(1)].get(m.group(2))
    if not area:
        return None
    rest = subject.split(" - ", 1)[1]
    # "Weather - Weather (Air Mass Stability)" -> "Weather - Air Mass Stability"
    if rest.startswith(area + " (") and rest.endswith(")"):
        rest = rest[len(area) + 2:-1]
    fixed = f"{area} - {rest}"
    return fixed if fixed != subject else None


def applicable_licences(q, info):
    """Own track, plus only documented mappings approved by a reviewer.

    Guide rules 5-6 / section 9: applicability is never inferred from broad
    rules, never crosses authorities automatically, and Air Law is never
    shared without an approved, LO-level mapping in taxonomy/applicability.csv.
    """
    tracks = [info["track_id"]]
    for rule in APPLICABILITY:
        if rule.get("review_status") != "approved" or not rule.get("reviewer"):
            continue
        if rule["add_track"].split(":")[0] != info["track_id"].split(":")[0]:
            continue  # never widen across authorities
        if rule["from_track"] == info["track_id"] and rule["subject_code"] == q.get("subject_code") \
                and rule["chapter_title"] == q.get("chapter_title") and rule["add_track"] not in tracks:
            tracks.append(rule["add_track"])
    return tracks


def regulation_dependent(q):
    if q.get("topic") in POLICY["regulation_dependent_topics"]:
        return True
    ref = re.sub(POLICY.get("syllabus_citation_regex", r"$^"), "", q.get("regulation_reference") or "")
    return bool(re.search(POLICY["regulation_citation_regex"], ref))


def needs_second_check(q):
    rule = POLICY["second_check_required_for"]
    return (q.get("question_type") in rule["question_types"] or q.get("topic") in rule["topics"]
            or bool(q.get("calculation_steps")) or (rule["regulation_dependent"] and regulation_dependent(q)))


def question_style(q):
    if q.get("question_id") in STYLE_OVERRIDES:
        return STYLE_OVERRIDES[q["question_id"]]
    if q.get("question_style") in ("exam_style", "concept_recall"):
        return q["question_style"]
    if CONCEPT_RECALL_PATTERN.match(q.get("question_text", "")) and \
            "groundschool" in (q.get("_source_file") or ""):
        return "concept_recall"
    return "exam_style"


def quality_flags(q, style):
    flags = set(AUDIT_FLAGS.get(q.get("question_id"), []))
    if style == "concept_recall":
        # Distractors are true statements about *other* topics, so the
        # answer is guessable by topic-matching. Fine for flashcards,
        # not for exam practice.
        flags.add("templated_distractors")
    text = q.get("question_text", "")
    if re.search(r"\b(refer to|figure\s*\d|appendix|in the (diagram|figure)|diagram\s*#|chart\s*#)", text, re.I) and not q.get("media"):
        flags.add("needs_figure")
    if re.search(r"non-?commercial", q.get("copyright_status", ""), re.I):
        # e.g. Transport Canada TP 13014 / TP 14454 Crown copyright terms.
        flags.add("non_commercial_licence")
    if q.get("question_type") == "calculation" and not q.get("calculation_steps"):
        flags.add("missing_calculation_steps")
    return sorted(flags)


def categorize(q):
    """Return a copy of q with all derived fields set. Raises CategorizationError."""
    out = dict(q)
    fixed = fix_acs_area_label(out)
    if fixed:
        out["subject"] = fixed
    info = licence_info(out)
    topic, topic_source = classify_topic(out)
    style = question_style(out)
    out["topic"] = topic
    out["topic_name"] = TOPICS[topic]["name"]
    out["topic_source"] = topic_source
    out["track_id"] = info["track_id"]
    out["licence_level"] = info["licence_level"]
    out["aircraft_class"] = info["aircraft_class"]
    out["applicable_licences"] = applicable_licences(out, info)
    if not out.get("chapter_title"):
        subj = out.get("subject", "")
        out["chapter_title"] = subj.split(" - ", 1)[1] if " - " in subj else subj.replace("General / ", "")
    out["question_style"] = style
    out["quality_flags"] = quality_flags(out, style)
    out.pop("extra_applicable_licences", None)
    return out


def is_usable(q):
    """Usable = passed the full activation gate (status is computed by scripts/gates.py)."""
    return q.get("status") == "active" and q.get("provenance") in USABLE_PROVENANCE


STORE_DIRS = ("data", "quarantine")


def load_bank(data_dir=None):
    """Yield (path, records) for every JSONL file under data/ and quarantine/.

    data/ holds active (released) records; quarantine/ holds everything that
    has not passed the activation gate. Both mirror the same relative layout
    (<authority>/<licence>/[<subject>/]<lang>/<file>.jsonl).
    """
    import glob
    dirs = [data_dir] if data_dir else [os.path.join(ROOT, d) for d in STORE_DIRS]
    for d in dirs:
        for path in sorted(glob.glob(os.path.join(d, "**", "*.jsonl"), recursive=True)):
            with open(path, encoding="utf-8") as f:
                recs = [json.loads(line) for line in f if line.strip()]
            yield path, recs


def rel_path(path):
    """data/x/y.jsonl or quarantine/x/y.jsonl -> x/y.jsonl"""
    rel = os.path.relpath(path, ROOT).split(os.sep)
    return os.sep.join(rel[1:]) if rel[0] in STORE_DIRS else os.sep.join(rel)


def load_logical_files():
    """{relative file: [records from data/ and quarantine/, original order by question_id]}"""
    files = {}
    for path, recs in load_bank():
        for q in recs:
            q["_source_file"] = path
        files.setdefault(rel_path(path), []).extend(recs)
    for recs in files.values():
        recs.sort(key=lambda q: q["question_id"])
    return files


def place(files):
    """Write each logical file's records to data/ (active) or quarantine/ (everything else)."""
    for rel, recs in files.items():
        for d in STORE_DIRS:
            subset = [q for q in recs if (q.get("status") == "active") == (d == "data")]
            path = os.path.join(ROOT, d, rel)
            if subset:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                write_jsonl(path, subset)
            elif os.path.exists(path):
                os.remove(path)


def write_jsonl(path, records):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps({k: v for k, v in r.items() if not k.startswith("_")},
                               ensure_ascii=False) + "\n")
    os.replace(tmp, path)
