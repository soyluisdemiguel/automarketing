---
Status: Active
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Quality scorecard dimensions, scoring rubric, and evidence expectations.
Related Docs: RELIABILITY.md, SECURITY.md, ../ARCHITECTURE.md, product-specs/portfolio-automarketing-control-plane.md, design-docs/portfolio-control-plane-architecture.md, exec-plans/tech-debt-tracker.md
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
| Product | Specs and scope discipline | 3 | [PRODUCT_SENSE.md](PRODUCT_SENSE.md) and [portfolio-automarketing-control-plane.md](product-specs/portfolio-automarketing-control-plane.md) define the target user, channels, and KPIs | No live portfolio validation yet | Product + Engineering | 2026-04-12 |
| Architecture | Boundaries and layering | 3 | [../ARCHITECTURE.md](../ARCHITECTURE.md) and [portfolio-control-plane-architecture.md](design-docs/portfolio-control-plane-architecture.md) define surfaces, modules, data boundaries, and contract ownership | Runtime code and deployment topology are not implemented yet | Engineering | 2026-04-12 |
| Delivery | Execution planning | 3 | [PLANS.md](PLANS.md) and [2026-03-12-control-plane-foundation.md](exec-plans/active/2026-03-12-control-plane-foundation.md) define the first execution sequence | No completed execution history yet | Engineering | 2026-04-12 |
| Security | Policy and review triggers | 3 | [SECURITY.md](SECURITY.md) and [mcp-application-contract.md](references/mcp-application-contract.md) define auth, action boundaries, and kill-switch expectations | Runtime enforcement, secret rotation, and approval policies are not implemented yet | Engineering | 2026-04-12 |
| Reliability | Operational readiness | 2 | [RELIABILITY.md](RELIABILITY.md) and [portfolio-control-plane-architecture.md](design-docs/portfolio-control-plane-architecture.md) define snapshot-first history, idempotency, and rollback expectations | No running service, production SLIs, or recovery drills yet | Engineering | 2026-04-12 |
| Operations | Automation governance | 3 | [skills-and-automations.md](references/skills-and-automations.md) defines required skills, automation classes, and stop rules | No live automation telemetry or operator feedback loops yet | Engineering | 2026-04-12 |

## Usage

Update scores when a capability materially changes. Link evidence to real documents, checks, dashboards, or plans instead of relying on narrative confidence.
