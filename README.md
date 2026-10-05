# PilotQuest

Multi-authority pilot theory study platform.

| Folder | What it is |
|---|---|
| [`pilotquest/`](pilotquest/) | Next.js App Router study app (Step 1: UI on mock data) |
| [`pilot-question-bank/`](pilot-question-bank/) | Question bank: master JSONL data, taxonomy, pipeline scripts. Adding questions: [`question injection.md`](pilot-question-bank/question%20injection.md) |

Generated question views are not committed. Rebuild them with:

```bash
cd pilot-question-bank
python3 scripts/categorize.py --write && python3 scripts/build_views.py
```
