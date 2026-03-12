---
Status: Active
Owner: Product + Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Product definition of the portfolio automarketing control plane.
Related Docs: index.md, ../PRODUCT_SENSE.md, ../design-docs/portfolio-control-plane-architecture.md, ../exec-plans/active/2026-03-12-control-plane-foundation.md
---

# Portfolio Automarketing Control Plane

## Summary

Build an internal control plane that helps operators and agents grow a portfolio of first-party apps. The system centralizes app inventory, business and usage history, visibility signals for web and MCP surfaces, and outbound growth actions across email, press, and related channels.

## Problem

Portfolio apps currently require fragmented manual work to answer basic growth questions:

- which app is healthy or declining;
- where visibility is weak across web and MCP surfaces;
- which growth action should happen next;
- whether users and revenue improved after a campaign.

Without a shared contract, each app would need bespoke integration work and growth execution would remain inconsistent and hard to automate safely.

## Target User

- Primary user: founder, product operator, or growth operator managing multiple first-party apps
- Secondary user: internal agent or automation acting through the control plane MCP surface under policy constraints

## Jobs To Be Done / Use Cases

- Register a portfolio app and declare how it makes money, who owns it, and what growth capabilities it exposes.
- Pull daily and on-demand snapshots for users, revenue, conversion, health, and visibility metrics.
- Compare app trajectories over time and detect drops or opportunities quickly.
- Launch, pause, or evaluate growth actions across email, press, SEO, and MCP discoverability workflows.
- Audit what the system changed, why it changed it, and what happened afterward.

## Scope

V1 includes:

- operator web console plus a control-plane MCP server;
- a minimum MCP contract that every portfolio app must implement;
- daily business, usage, and visibility snapshots plus on-demand refresh;
- channel support for MCP discoverability, web search visibility, email campaigns, and press outreach;
- autonomous execution by default with policy guardrails, budget caps, kill switches, and audit trails;
- documented operating skills and proposed automations for both product workflows and repo evolution.

## Non-Goals

- generic multi-tenant SaaS for third-party customers;
- paid-media buying, ad-network arbitrage, or full CRM replacement in V1;
- replacing the source analytics systems inside each app;
- supporting arbitrary workflow automation unrelated to app growth and monetization.

## UX Notes

- The primary surface is a web console optimized for quick portfolio triage and trustworthy automation oversight.
- Every important entity needs both a human-readable summary and a stable machine-readable identifier.
- Historical views must make trend changes obvious without hiding the underlying raw values.
- Any action available in the web console should map cleanly to the control-plane MCP surface.

## Success Metrics

- At least one portfolio app can be onboarded using only the documented MCP contract and no bespoke schema changes.
- Snapshot freshness for onboarded apps stays within the daily schedule and supports on-demand refresh.
- Operators can move from detected opportunity to launched action in a single workflow without external spreadsheets.
- App-level metrics can be compared by channel and time window to judge whether money, users, or visibility improved.
- Autonomous actions remain attributable, budget-bounded, and reversible or stoppable where the channel allows it.

## Rollout Notes

- Phase 0: documentation, contract definition, and execution plan
- Phase 1: one or two internal pilot apps with snapshot ingest, visibility tracking, and at least one outbound channel
- Phase 2: broader portfolio onboarding and policy tuning based on observed results

## Linked Design Docs / Plans

- [../design-docs/portfolio-control-plane-architecture.md](../design-docs/portfolio-control-plane-architecture.md)
- [../references/mcp-application-contract.md](../references/mcp-application-contract.md)
- [../references/skills-and-automations.md](../references/skills-and-automations.md)
- [../exec-plans/active/2026-03-12-control-plane-foundation.md](../exec-plans/active/2026-03-12-control-plane-foundation.md)
