---
Status: Active
Owner: Product + Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Product heuristics, prioritization rules, and feature evaluation criteria.
Related Docs: DESIGN.md, FRONTEND.md, product-specs/index.md, product-specs/portfolio-automarketing-control-plane.md, design-docs/portfolio-control-plane-architecture.md, ../ARCHITECTURE.md
---

# Product Sense

## Decision Heuristics

- Solve the portfolio owner's core question in one place: which app needs attention, what action should happen next, and is it improving users or revenue.
- Prefer reusable automations and contracts that work across many first-party apps over one-off campaign workflows.
- Prioritize channels with measurable visibility, adoption, or monetization impact: MCP discoverability, web search, email, and press.
- Default to reducing operator overhead, spreadsheet work, and hidden human coordination.
- Do not ship autonomous actions unless they have a success metric, budget boundary, and stop rule.

## Prioritization Rules

Prioritize work that:

- makes a new portfolio app onboardable through the MCP contract;
- improves visibility or monetization signal quality across the portfolio;
- shortens time from detected opportunity to launched campaign;
- reduces the risk of unsafe automation, duplicate execution, or unbounded spend;
- lowers the cost of safe iteration on app growth loops.

## What Good Looks Like

- An operator can view health, users, revenue, and visibility history for every onboarded app without manual data collection.
- A new app can be added by implementing the documented MCP contract rather than a custom integration.
- Campaign and growth actions are attributable by app, channel, and time window.
- Operators and agents can use the same control-plane capabilities through web and MCP surfaces.
- Non-goals are explicit enough to stop the product from becoming a generic marketing agency platform.

## Anti-Patterns

- Running campaigns without a named KPI, spend limit, or termination condition
- Building per-app bespoke logic where the MCP contract should be extended instead
- Treating manual analyst work as part of the hidden happy path
- Expanding into paid-media or external multi-tenant workflows before the first-party portfolio loop works reliably
