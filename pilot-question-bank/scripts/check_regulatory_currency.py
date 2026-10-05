#!/usr/bin/env python3
"""
check_regulatory_currency.py — List every regulation-dependent record and
what is missing before it can be `current_verified` (guide section 10).

    python3 scripts/check_regulatory_currency.py   # report -> reports/regulatory_currency.csv

Flags: no exact provision, no effective date, no access date, access older
than policy.regulatory_currency_max_age_days, status not current_verified,
second review outstanding. It does not fetch regulations or change status —
verification is a recorded review (review_type regulatory) applied by
scripts/release_questions.py with the provision, effective date and access date.
"""
import collections
import csv
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy  # noqa: E402


def main():
    max_age = taxonomy.POLICY["regulatory_currency_max_age_days"]
    today = datetime.date.today()
    rows = []
    for _, recs in taxonomy.load_bank():
        for q in recs:
            if not taxonomy.regulation_dependent(q):
                continue
            issues = []
            if not q.get("regulation_provision"):
                issues.append("no exact provision")
            if not q.get("source_effective_date"):
                issues.append("no effective date")
            acc = q.get("source_accessed_date")
            if not acc:
                issues.append("no access date")
            else:
                try:
                    if (today - datetime.date.fromisoformat(acc)).days > max_age:
                        issues.append(f"access older than {max_age} days")
                except ValueError:
                    issues.append("bad access date")
            if q.get("regulatory_status") != "current_verified":
                issues.append(f"status {q.get('regulatory_status') or 'unset'}")
            if q.get("regulatory_review_status") != "passed":
                issues.append("regulatory review outstanding")
            rows.append({"question_id": q["question_id"], "authority": q["authority"], "track_id": q["track_id"],
                         "regulatory_status": q.get("regulatory_status"), "regulation_provision": q.get("regulation_provision", ""),
                         "regulation_reference": q.get("regulation_reference", ""), "issues": "; ".join(issues) or "ok"})
    out = os.path.join(taxonomy.ROOT, "reports", "regulatory_currency.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["question_id"])
        w.writeheader()
        w.writerows(rows)
    c = collections.Counter((r["authority"], r["regulatory_status"]) for r in rows)
    print(f"{len(rows)} regulation-dependent record(s); current_verified: {sum(r['regulatory_status'] == 'current_verified' for r in rows)}")
    for k, v in sorted(c.items()):
        print(f"  {k[0]:<18} {k[1] or 'unset':<32} {v}")
    print("report: reports/regulatory_currency.csv")


if __name__ == "__main__":
    main()
