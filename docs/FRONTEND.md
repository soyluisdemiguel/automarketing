---
Status: Draft
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Frontend architecture and UI implementation conventions for the automarketing operator console.
Related Docs: ../ARCHITECTURE.md, DESIGN.md, PRODUCT_SENSE.md, design-docs/portfolio-control-plane-architecture.md, references/design-system-reference-llms.txt
---

# Frontend

The first frontend is the operator console for the automarketing control plane. It must present portfolio state, autonomous actions, and audit history clearly enough that an operator can trust or override the system. The initial implementation will be server-rendered with progressive enhancement so the control plane can ship one coherent stack before any separate SPA is justified.

## Required Decisions Before Shipping UI

- Navigation boundaries across portfolio overview, app detail, campaign workspace, automation history, and policy controls
- State ownership: the server is authoritative for metrics, campaigns, and automation state; the client owns only ephemeral filters, drafts, and local presentation state
- Data fetching strategy and loading/error conventions for long-running syncs and action execution
- Table, chart, and timeline patterns for financial, user, and visibility history
- Accessibility baseline for keyboard, screen reader, contrast, and reduced-motion support
- Performance budgets for first render, filter changes, and audit log navigation

## Conventions To Preserve

- Keep app status and risk obvious before making workflows clever.
- Treat empty, loading, stale-data, and action-failure states as first-class UI.
- Prefer reusable primitives for metric cards, timeline entries, approval states, and channel run summaries over page-level one-offs.
- Show both human-readable summaries and machine-meaningful identifiers for apps, campaigns, automations, and actions.
- Mirror important actions with MCP-consumable semantics so web and MCP stay aligned.
- Document design tokens, spacing, and typography in [references/design-system-reference-llms.txt](references/design-system-reference-llms.txt) as the design system becomes concrete.

## Future Additions

- Concrete component library and charting choices once code exists
- Form patterns for campaign configuration, policy editing, and kill-switch controls
- Analytics instrumentation rules for operator behavior
- Localization approach if needed for multilingual operators or channels
