# Question Injection — superseded

This guide was replaced on 2026-10-05 by
**[PilotQuest_Strict_PDF_Ingestion_and_Publishing_Guide.md](PilotQuest_Strict_PDF_Ingestion_and_Publishing_Guide.md)**,
operationalised as the Claude Code skill **`/inject-questions`**
(`.claude/skills/inject-questions/SKILL.md` at the repository root).

What changed from this guide:

| Old | Now |
|---|---|
| `--activate` published a batch | Nothing is imported active. Every record is gated individually by `scripts/gates.py` and released with `scripts/release_questions.py`. |
| Reading a sample = provenance check | A sample is an intake check only. Technical, editorial, regulatory, media and duplicate reviews are recorded per record. |
| `reuse_allowed` taken from the import | Derived from `taxonomy/rights_records.csv` + `taxonomy/policy.json`. |
| EASA ATPL content auto-widened to PPL/CPL | Only reviewer-approved rows in `taxonomy/applicability.csv`. |
| 230 audit-pending Air Law items active | Quarantined. |
| Unknown import fields dropped | Kept in `source_payload`. |
| One store, `data/` | `data/` = active only; `quarantine/` = everything else, with `gate_failures` and `next_action`. |

Current numbers: `reports/publishable_summary.md`.
