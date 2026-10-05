# Rejected / Excluded Sources

Status: Batch 1. Last updated 2026-09-10. This log records resources that were identified during research but deliberately NOT scraped or ingested, and why.

| Source | Authority | Reason for exclusion | Classification |
|---|---|---|---|
| European Central Question Bank (ECQB) | EASA | Confidential theory-question bank distributed only to authorised ATOs/exam authorities; no public access | `restricted_do_not_use` |
| Live FAA Airman Knowledge Testing item bank (delivered via PSI testing vendor) | FAA | FAA explicitly states current test questions are not released to the public; copying/removing questions from a test centre is prohibited | `restricted_do_not_use` |
| CASA live theory-exam item bank ("closed tests") | CASA (Australia) | Confirmed not publicly released | `restricted_do_not_use` |
| pilotpracticeexams.com, thepilotexam.com, pplprep.com, open-exam-prep.com and similar commercial CASA-style question sites | CASA (Australia) | Third-party commercial test-prep content of unverified/likely-reconstructed provenance; not scraped | `third_party_reference_only` |
| Scribd/Docsity/Course Hero/Studocu uploads of exam-style material (e.g. uploaded copies of TP 13014, CASA-style question sets) | Multiple | User-uploaded copies of uncertain fidelity/currency and uncertain upload rights; the underlying official document was instead sourced directly from the issuing authority's own domain where possible | `third_party_reference_only` |
| Commercial FAA/Canada/CASA test-prep vendors generally (e.g. Sheppard Air, Gleim, ASA-style products referenced in search results) | FAA / general | Commercial, copyrighted question banks; existence noted only, no content accessed | `restricted_do_not_use` |
| SACAA-aligned commercial prep sites (identified via search, not named individually in this log — see fork notes in `research/authority_inventory.csv`) | SACAA | Third-party commercial content; not accessed | `third_party_reference_only` |
| privatepilotexams.com/faa ("PPE") | FAA | Commercial freemium test-prep product (1,600+ questions, $9.90/week–$60/4mo subscription, email registration required for even the free tier). Not official FAA material; no copyright/reuse statement found on the page. User asked 2026-09-11 whether this could be used as a source — declined; not accessed beyond the public landing page, no content extracted, no login/paywall bypass attempted. Note: the fetched page content included an anomalous, out-of-place line unrelated to aviation, consistent with a prompt-injection attempt against the page-summarization step — flagged to the user, not acted on. | `restricted_do_not_use` |

## Sources attempted but not yet accessible (technical, not legal, reasons)

| Source | Authority | Issue |
|---|---|---|
| faa.gov PDF/HTML pages (ACS documents, sample-question PDFs, FAQ page) | FAA | Every direct WebFetch attempt this session returned HTTP 403 (bot protection). URLs are real and were confirmed to exist via search-engine indexing, but content has not been read. Not rejected — flagged for a follow-up session with different fetch tooling. |
| casa.gov.au sub-pages | CASA (Australia) | WebFetch timed out on homepage and several sub-pages during one research pass; findings for CASA are currently search-snippet-derived only, not independently fetched. |
| aviation.govt.nz syllabus-assistance page | CAA New Zealand | Fetch returned a blank response; other pages timed out. Findings are search-snippet-derived only. |
| Individual Transport Canada TP publication pages for TP 877, TP 13728, TP 14454 | Transport Canada | Only the index page listing these was fetched; individual per-document URLs/copyright pages were not yet retrieved. |
| ~~tp13014e.pdf (binary PDF content)~~ | Transport Canada | **RESOLVED (batch 2):** `poppler` installed; PDF fetched and text-extracted successfully. All 20 Air Law questions ingested — see `data/transport-canada/rpp-ppl-a/air-law/en/official_sample_tp13014_batch1.jsonl`. |

None of the above technical-access failures were worked around via login bypass, CAPTCHA solving, or paywall circumvention, per project rules.
