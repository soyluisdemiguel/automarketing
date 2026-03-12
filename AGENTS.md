---
Status: Active
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Agent navigation and repository operating rules.
Related Docs: ARCHITECTURE.md, docs/PLANS.md, docs/DESIGN.md, docs/PRODUCT_SENSE.md, docs/product-specs/portfolio-automarketing-control-plane.md, docs/design-docs/portfolio-control-plane-architecture.md
---

# AGENTS.md

`docs/` is the source of truth for this repository. This file stays short on purpose and points agents to the right document instead of duplicating policy.

## Start Here

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system boundaries and expected topology.
- Read [docs/product-specs/portfolio-automarketing-control-plane.md](docs/product-specs/portfolio-automarketing-control-plane.md) before proposing product, channel, or automation changes.
- Read [docs/design-docs/portfolio-control-plane-architecture.md](docs/design-docs/portfolio-control-plane-architecture.md) before making implementation or integration decisions.
- Read [docs/PRODUCT_SENSE.md](docs/PRODUCT_SENSE.md) before proposing user-facing changes.
- Read [docs/DESIGN.md](docs/DESIGN.md) and [docs/FRONTEND.md](docs/FRONTEND.md) before making implementation decisions.
- Read [docs/SECURITY.md](docs/SECURITY.md) and [docs/RELIABILITY.md](docs/RELIABILITY.md) for release-impacting work.
- Read [docs/references/mcp-application-contract.md](docs/references/mcp-application-contract.md) for portfolio app integrations.
- Read [docs/references/skills-and-automations.md](docs/references/skills-and-automations.md) for continuous research, growth workflows, and repo automation planning.

## Commands

- Validate the documentation scaffold: `python3 scripts/validate_docs.py`
- Until app code exists, there are no build, test, or deploy commands beyond docs validation.

## Planning Rules

- Create an ExecPlan for multi-hour, risky, or cross-cutting work.
- Draft active plans in [docs/exec-plans/active/README.md](docs/exec-plans/active/README.md) using the format in [docs/PLANS.md](docs/PLANS.md).
- Move completed plans into [docs/exec-plans/completed/README.md](docs/exec-plans/completed/README.md) and update linked specs or debt items.

## Guardrails

- Update metadata in every governed document you touch.
- Prefer links to the source document instead of restating policy.
- Keep architectural assumptions explicit and synchronize contract changes across architecture, design docs, and references.
- Nested `AGENTS.md` files are allowed near future code, but this root file remains the global map.
