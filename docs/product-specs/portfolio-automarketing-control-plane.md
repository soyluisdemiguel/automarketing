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
- visibility intelligence centered on the official MCP registry plus web search, with community directories treated as secondary evidence;
- bilingual `EN + ES` query coverage for brand, task, and competitor visibility baselines;
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
- The system can explain an app's MCP visibility using official-registry presence, metadata completeness, and remote reachability as separate signals.
- The system can explain an app's web visibility using tracked EN and ES queries plus Search Console data when the property is verified.

## Visibility Defaults

- Primary positioning surfaces in V1 are the official MCP registry and web search.
- Community MCP directories are secondary signals and should not block onboarding or reporting if they rate-limit, require auth, or block automation.
- The first scoring model is fixed for implementation:
  - `mcp_visibility_score`
    - 35 points: active listing in the official MCP registry
    - 20 points: metadata completeness across name or title, description, website, remote, and repository
    - 25 points: remote MCP reachability
    - 10 points: secondary public directory presence
    - 10 points: branded web rank for `<brand> mcp`
  - `web_visibility_score`
    - 40 points: branded rank across EN and ES queries
    - 30 points: task-query rank across EN and ES queries
    - 20 points: Search Console 28-day impressions and clicks trend
    - 10 points: indexability and metadata checks
- If Search Console is not configured, `web_visibility_score` remains partial and the visibility report must declare partial confidence rather than renormalizing.

## Real-Data Baseline

- On March 12, 2026, the official MCP registry exposed `GET /v0.1/servers` as a public API for catalog ingestion.
- Sampling the first 500 registry entries showed `91.6%` with a declared remote endpoint and `74.8%` with a repository URL.
- Probing 5 public registry remotes returned JSON HTTP responses in the `401` and `406` families, so V1 must distinguish "reachable MCP" from "open MCP" in scoring and health checks.

## Rollout Notes

- Phase 0: documentation, contract definition, and execution plan
- Phase 1: one or two internal pilot apps with snapshot ingest, visibility tracking, and at least one outbound channel
- Phase 2: broader portfolio onboarding and policy tuning based on observed results

## Linked Design Docs / Plans

- [../design-docs/portfolio-control-plane-architecture.md](../design-docs/portfolio-control-plane-architecture.md)
- [../references/mcp-application-contract.md](../references/mcp-application-contract.md)
- [../references/skills-and-automations.md](../references/skills-and-automations.md)
- [../exec-plans/active/2026-03-12-control-plane-foundation.md](../exec-plans/active/2026-03-12-control-plane-foundation.md)
