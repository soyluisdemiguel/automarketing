---
Status: Active
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Repository-wide design principles and implementation decision criteria.
Related Docs: ../ARCHITECTURE.md, design-docs/core-beliefs.md, design-docs/portfolio-control-plane-architecture.md, FRONTEND.md, PRODUCT_SENSE.md, references/mcp-application-contract.md
---

# Design

## Principles

- Optimize for clarity over novelty.
- Make irreversible decisions explicit and reviewable.
- Keep domain rules separate from frameworks and delivery mechanisms.
- Prefer small interfaces with strong defaults over sprawling configuration.
- Write docs as part of the design, not as an afterthought.
- Prefer contract-first integrations so every portfolio app can be onboarded the same way.
- Keep autonomous execution observable, budget-aware, and policy-constrained.

## Decision Criteria

Choose approaches that:

- reduce hidden coupling across apps, channels, and providers;
- keep failure modes observable and auditable per app, automation, and campaign;
- preserve room for future channel additions without redesigning the core data model;
- can be explained to a new engineer or agent in one document;
- let the control plane expose the same capability through both web and MCP surfaces.

## When to Write a Design Doc

Create a design doc when work changes architecture boundaries, introduces a new integration, creates a shared platform capability, changes the MCP contract, or locks in a hard-to-reverse implementation strategy. Use [design-docs/template.md](design-docs/template.md).

## Review Expectations

- Link each meaningful design to a product spec or debt item
- Capture rejected alternatives when they were credible options
- Define concrete acceptance signals before implementation starts
- Include security and reliability implications whenever a new autonomous action or external provider is introduced
