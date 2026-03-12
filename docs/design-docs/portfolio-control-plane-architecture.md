---
Status: Draft
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Architecture, contracts, and runtime choices for the automarketing control plane.
Related Docs: index.md, ../PRODUCT_SENSE.md, ../product-specs/portfolio-automarketing-control-plane.md, ../references/mcp-application-contract.md, ../references/skills-and-automations.md, ../exec-plans/active/2026-03-12-control-plane-foundation.md
---

# Portfolio Control Plane Architecture

## Metadata

This document fixes the first implementation shape for the automarketing control plane so the next phase can build code without reopening the core system design.

## Summary

Implement the product as a Python-first control-plane monolith with three surfaces backed by shared domain services: an operator web console, a REST API for the console, and a remote MCP server for agents. A separate worker role runs scheduled ingestion, visibility checks, and growth actions against portfolio apps and external providers. PostgreSQL stores the durable app registry, historical snapshots, campaign records, automation runs, visibility observations, and audit trails.

## Goals

- Support both human and agent operation through web and MCP surfaces.
- Onboard first-party apps through one minimum MCP contract.
- Preserve historical money, user, health, and visibility data per app.
- Execute growth actions automatically by default, but under budget, policy, and kill-switch controls.
- Keep the first implementation operationally simple enough to ship without a multi-service platform.

## Non-Goals

- Building a multi-tenant product for external customers
- Implementing real-time event sourcing as the primary data model
- Locking the system to any specific email, press, or SEO vendor in this phase
- Creating an unrestricted autonomous agent that can spend or publish without policy controls

## Constraints

- The repository is documentation-first today; this phase does not yet add runtime code.
- The control plane must align with MCP concepts and transports documented by the official protocol.
- Historical storage is snapshot-first, not event-first.
- The operator console must stay accessible and understandable without relying on a separate frontend platform.
- The first implementation should minimize moving parts and avoid unnecessary infrastructure.

## Proposed Design

### Runtime Shape

- Control plane API: Python 3.12 with FastAPI for HTTP APIs and the official Python MCP SDK for the MCP surface.
- Operator console: server-rendered HTML with progressive enhancement; no separate SPA is required in V1.
- Worker role: same codebase, separate process role for scheduled ingestion, visibility refresh, and action execution.
- Storage: PostgreSQL is the primary system of record. No external queue is required in V1; job state lives in PostgreSQL-backed tables.
- MCP transport:
  - production: Streamable HTTP
  - local development and contract tests: stdio where useful

### Internal Modules

- Portfolio registry: app identity, owners, categories, monetization model, environment, and integration endpoints
- MCP gateway: client integration to each portfolio app's MCP server plus the public MCP server exposed by the control plane
- Snapshot service: scheduled and on-demand ingestion of money, user, health, and visibility metrics
- Visibility intelligence: tracked queries, rank observations, MCP discoverability checks, and competitor notes
- Campaign orchestrator: campaign planning, execution, reconciliation, and attribution across supported channels
- Policy engine: risk levels, budget caps, approval requirements, cooldowns, and stop conditions
- Automation runner: scheduled workflows, retries, status transitions, and operator-visible run history
- Audit service: immutable records of who or what triggered each action and what changed

### Public Interfaces

#### Operator Web Console

Required views for the first implementation:

- portfolio overview with filters and health or status summaries;
- application detail with historical metrics, visibility observations, and integration health;
- campaign workspace with current runs, outcomes, and planned actions;
- automation run history with stop reasons and retry state;
- policy and budget controls, including kill switches.

#### Control-Plane MCP Surface

The control plane MCP server exposes resources for portfolio context and tools for operational control. The minimum server surface should include:

- Resources:
  - `portfolio://applications`
  - `portfolio://applications/{app_slug}`
  - `portfolio://applications/{app_slug}/snapshots`
  - `portfolio://applications/{app_slug}/campaigns`
  - `portfolio://applications/{app_slug}/visibility`
  - `portfolio://applications/{app_slug}/integration-health`
- Tools:
  - `list_applications`
  - `get_application_summary`
  - `sync_application_snapshot`
  - `plan_growth_action`
  - `execute_growth_action`
  - `pause_application_automation`
  - `resume_application_automation`
  - `refresh_visibility_observations`
- Prompts are optional and should package human-guided workflows rather than hidden automation.

#### Portfolio App MCP Contract

Each managed app must expose the contract defined in [../references/mcp-application-contract.md](../references/mcp-application-contract.md). That contract uses MCP resources for discovery and read-only state, tools for side effects, and optional prompts for app-specific operator assistance.

### Data Model

The first relational model should include these tables:

- `applications`: canonical app registry and default operating policy
- `application_capabilities`: declared actions, channels, and MCP contract version per app
- `metric_snapshots`: immutable daily and on-demand snapshots of users, revenue, conversion, and health
- `campaigns`: campaign definitions with app, channel, KPI, and budget ownership
- `campaign_runs`: per-execution outcomes, spend, timestamps, and provider payload references
- `growth_actions`: individual planned or executed actions, including risk level, payload, and result
- `automation_runs`: scheduled workflow executions with inputs, outputs, stop reason, and status
- `visibility_observations`: rank and discoverability observations across tracked web and MCP queries
- `integration_health`: latency, auth state, last success, and failure summaries for each app integration

`docs/generated/db-schema.md` remains a placeholder until real migrations exist. When code lands, generated schema output must reflect this model or document any deliberate divergence.

### Historical Data Policy

- Default schedule: one daily snapshot per onboarded app at 02:00 UTC for business, usage, health, and visibility metrics.
- On-demand sync: operators and MCP clients can request an immediate refresh for a single app.
- Snapshot records are append-only; corrections or backfills must create explicit new records with provenance.
- Visibility observations should capture query, rank, source surface, competitor context, and observed URL so trends remain explainable.

### Automation and Action Policy

- Execution mode is auto by default, but every action must pass through `preview -> policy evaluation -> execution -> verification -> audit`.
- Every action payload requires:
  - `action_type`
  - `target_channel`
  - `idempotency_key`
  - `budget_limit`
  - `requested_by`
  - `scheduled_for`
  - channel-specific parameters
- Actions that exceed policy thresholds, increase spend beyond app limits, or are classified as irreversible must require an explicit policy rule to proceed.
- Every app must support a control-plane kill switch that pauses new automated actions immediately.
- Retry behavior must be channel-aware and idempotent; no blind retries on publish-or-spend operations.

### Skills and Automations

The operating catalog in [../references/skills-and-automations.md](../references/skills-and-automations.md) defines the skills and recurring workflows the repo and product need. Implementation should model product automations as first-class scheduled jobs and keep Codex automations documented but inactive until explicitly enabled.

## Alternatives Considered

- Separate frontend SPA plus backend API: rejected for V1 because it adds another platform surface before the operator workflow is proven.
- Multi-service architecture with dedicated queue and orchestrator: rejected for V1 because the product needs fast iteration more than infrastructure isolation.
- Event-sourced history as the primary store: rejected for V1 because snapshot-first storage better matches operator reporting and implementation speed.

## Risks

- Provider sprawl could fragment campaign logic. Mitigation: keep provider adapters behind channel-specific interfaces.
- Automatic execution could overspend or publish unsafe changes. Mitigation: policy engine, budget caps, preview step, audit records, and kill switches.
- Portfolio apps may expose inconsistent metrics. Mitigation: versioned MCP contract plus validation harness in the next phase.
- Daily snapshots may miss fast-moving regressions. Mitigation: on-demand refresh and targeted automation triggers on integration or visibility anomalies.

## Acceptance Signals

- The implementation team can begin backend work without reopening core choices about surfaces, transport, storage, or automation policy.
- The MCP contract, data model, and required tables are documented and cross-linked.
- Web and MCP surfaces are defined tightly enough that tests and initial routes can be derived directly from this document.
- Residual uncertainty is limited to provider selection and code execution details tracked as explicit debt.

## Related Specs and Plans

- [../product-specs/portfolio-automarketing-control-plane.md](../product-specs/portfolio-automarketing-control-plane.md)
- [../references/mcp-application-contract.md](../references/mcp-application-contract.md)
- [../references/skills-and-automations.md](../references/skills-and-automations.md)
- [../exec-plans/active/2026-03-12-control-plane-foundation.md](../exec-plans/active/2026-03-12-control-plane-foundation.md)
