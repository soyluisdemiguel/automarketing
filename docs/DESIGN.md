---
Status: Active
Owner: Engineering
Last Reviewed: 2026-03-11
Source of Truth For: Repository-wide design principles and implementation decision criteria.
Related Docs: ../ARCHITECTURE.md, design-docs/core-beliefs.md, FRONTEND.md, PRODUCT_SENSE.md
---

# Design

## Principles

- Optimize for clarity over novelty.
- Make irreversible decisions explicit and reviewable.
- Keep domain rules separate from frameworks and delivery mechanisms.
- Prefer small interfaces with strong defaults over sprawling configuration.
- Write docs as part of the design, not as an afterthought.

## Decision Criteria

Choose approaches that:

- reduce hidden coupling;
- keep failure modes observable;
- preserve room for future product direction changes;
- are explainable to a new engineer or agent in one document.

## When to Write a Design Doc

Create a design doc when work changes architecture boundaries, introduces a new integration, creates a shared platform capability, or locks in a hard-to-reverse implementation strategy. Use [design-docs/template.md](design-docs/template.md).

## Review Expectations

- Link each meaningful design to a product spec or debt item
- Capture rejected alternatives when they were credible options
- Define concrete acceptance signals before implementation starts
