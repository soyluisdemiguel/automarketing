---
Status: Active
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Recurring documentation maintenance workflow and automation checks.
Related Docs: PLANS.md, QUALITY_SCORE.md, design-docs/index.md, product-specs/index.md, references/index.md
---

# Doc Gardening

Run this workflow at least every two weeks and before major releases.

## Automated Checks

- Run `python3 scripts/validate_docs.py`
- Flag documents whose `Last Reviewed` date is older than 45 days
- Flag specs without a linked plan when implementation is in progress
- Flag active plans without a completion or supersession path
- Flag architecture and design docs whose linked local paths no longer exist
- Flag MCP contract or skills and automation reference docs that are missing owners, linked specs, or stop-rule language

## Manual Review

- Remove duplicated policy that drifted away from the source document
- Promote stable decisions from plans into specs, design docs, or architecture
- Demote stale or superseded docs by updating status and adding replacement links
- Refresh the quality score with evidence instead of intuition
- Check that the skills and automation catalog still matches active product scope and repo workflow

## Output

Each gardening pass should leave:

- updated review dates for touched docs;
- explicit debt entries for unresolved gaps;
- either a closed loop on stale plans or a new follow-up plan.
