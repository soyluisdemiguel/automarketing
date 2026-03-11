---
Status: Active
Owner: Engineering
Last Reviewed: 2026-03-11
Source of Truth For: Quality scorecard dimensions, scoring rubric, and evidence expectations.
Related Docs: RELIABILITY.md, SECURITY.md, ../ARCHITECTURE.md, exec-plans/tech-debt-tracker.md
---

# Quality Score

## Rubric

| Score | Meaning |
| --- | --- |
| 0 | Missing or unknown |
| 1 | Exists informally; not reliable |
| 2 | Defined but incomplete |
| 3 | Working and regularly used |
| 4 | Strong, measured, and low-friction |

## Scorecard

| Area | Dimension | Score | Evidence | Gap | Owner | Next Review |
| --- | --- | --- | --- | --- | --- | --- |
| Product | Specs and scope discipline | 2 | Product and planning docs exist | Product domain is still TBD | Product + Engineering | 2026-04-11 |
| Architecture | Boundaries and layering | 2 | [ARCHITECTURE.md](../ARCHITECTURE.md) and [DESIGN.md](DESIGN.md) define rules | Runtime shape not yet chosen | Engineering | 2026-04-11 |
| Delivery | Execution planning | 3 | [PLANS.md](PLANS.md) and plan folders are in place | No completed plans yet | Engineering | 2026-04-11 |
| Security | Policy and review triggers | 2 | [SECURITY.md](SECURITY.md) exists | Contacts and implementation controls are incomplete | Engineering | 2026-04-11 |
| Reliability | Operational readiness | 1 | [RELIABILITY.md](RELIABILITY.md) defines the rubric | No running service or SLOs yet | Engineering | 2026-04-11 |

## Usage

Update scores when a capability materially changes. Link evidence to real documents, checks, dashboards, or plans instead of relying on narrative confidence.
