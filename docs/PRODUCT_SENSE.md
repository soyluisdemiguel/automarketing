---
Status: Active
Owner: Product + Engineering
Last Reviewed: 2026-03-11
Source of Truth For: Product heuristics, prioritization rules, and feature evaluation criteria.
Related Docs: DESIGN.md, FRONTEND.md, product-specs/index.md, ../ARCHITECTURE.md
---

# Product Sense

## Decision Heuristics

- Solve a user problem that can be named in one sentence.
- Prefer shorter paths to user value over broader surface area.
- Default to reducing confusion, setup cost, and operational burden.
- Avoid features that require hidden human process to work reliably.

## Prioritization Rules

Prioritize work that:

- unlocks learning about the core user problem;
- removes a bottleneck in onboarding, activation, or retention;
- lowers the cost of safe iteration;
- reduces irreversible product or technical risk.

## What Good Looks Like

- A feature has a clear target user and job to be done
- Scope is intentionally narrow for the current learning stage
- Success metrics are observable without heroic analytics work
- Non-goals are explicit enough to prevent accidental sprawl

## Anti-Patterns

- Shipping a broad feature without a measurable outcome
- Building internal complexity before user value is proven
- Treating edge-case flexibility as a substitute for product clarity
