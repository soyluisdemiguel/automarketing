---
Status: Draft
Owner: Engineering
Last Reviewed: 2026-03-11
Source of Truth For: Frontend architecture and UI implementation conventions for water.
Related Docs: ../ARCHITECTURE.md, DESIGN.md, PRODUCT_SENSE.md, references/design-system-reference-llms.txt
---

# Frontend

No frontend stack is committed yet. This document defines the expectations that future UI work must answer before implementation scales.

## Required Decisions Before Shipping UI

- Routing model and navigation boundaries
- State ownership: local, server, cached, and derived state
- Data fetching strategy and loading/error conventions
- Component layering and design system ownership
- Accessibility baseline for keyboard, screen reader, and contrast support
- Performance budgets for first render and interaction latency

## Conventions To Preserve

- Keep product flows obvious before making them clever.
- Treat empty, loading, and failure states as first-class UI.
- Prefer reusable primitives over page-level one-offs.
- Document design tokens, spacing, and typography in [references/design-system-reference-llms.txt](references/design-system-reference-llms.txt) once a design system exists.

## Future Additions

- Chosen framework and rendering model
- Form patterns
- Analytics instrumentation rules
- Localization approach if needed
