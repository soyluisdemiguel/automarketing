---
Status: Draft
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Execution plan for the first runnable automarketing control plane.
Related Docs: ../../product-specs/portfolio-automarketing-control-plane.md, ../../design-docs/portfolio-control-plane-architecture.md, ../../references/mcp-application-contract.md, ../tech-debt-tracker.md
---

# Control Plane Foundation

## Summary

Build the first runnable version of the automarketing control plane described in the product spec and architecture docs. The implementation should establish the Python service foundation, PostgreSQL schema, control-plane MCP surface, portfolio app MCP validation path, operator console skeleton, and the first automation and channel workflows.

## Goal and Success Criteria

- A Python control-plane service runs locally with FastAPI, PostgreSQL connectivity, and the control-plane MCP endpoint.
- At least one sample or pilot app can be validated against the documented MCP contract and ingested into the control plane.
- Historical snapshots, campaign records, automation runs, and visibility observations have migrations and initial domain services.
- The operator console exposes portfolio overview, app detail, automation history, and campaign basics.
- The first implementation leaves no undocumented divergence from the current spec and design docs.

## Out of Scope

- Multi-tenant SaaS concerns
- Paid-media channels and ad bidding
- Advanced ML scoring beyond simple rule-based opportunity ranking
- Full provider breadth across every email, press, or SEO vendor

## Current State

- Product, architecture, MCP contract, and skill or automation expectations are now documented and published on `main`.
- A first runnable slice now exists with a FastAPI app, mounted MCP server, seeded in-memory portfolio state, operator HTML views, REST endpoints, and basic tests.
- PostgreSQL persistence, migrations, provider adapters, and the MCP conformance harness still need implementation.
- Validation now covers documentation plus Python smoke tests and HTTP route tests.

## Intended Implementation

1. Service foundation
   - Create the Python project, FastAPI service skeleton, environment configuration, and local development workflow.
   - Split roles into API server and worker process from one codebase.
2. Persistence and domain models
   - Add PostgreSQL migrations for the documented core tables.
   - Implement repositories and services for applications, snapshots, campaigns, automation runs, visibility observations, and integration health.
3. MCP surfaces
   - Implement the control-plane MCP server with the documented resources and tools.
   - Build a validator harness and fixtures for onboarding portfolio apps against the app MCP contract.
4. Ingestion and automation
   - Implement daily snapshot ingestion, on-demand sync, visibility refresh, and basic opportunity scoring.
   - Persist automation run history with stop reasons and correlation IDs.
5. Operator workflows
   - Build the server-rendered operator console for portfolio overview, app detail, campaign workspace, and automation history.
   - Surface kill switches, policy state, and recent action outcomes.
6. Channel execution
   - Integrate one initial email path and one initial press path behind channel adapters.
   - Record preview, execution, verification, and reconciliation state for each action.

## Risks and Rollback

- Provider selection may delay channel execution. Mitigation: implement adapters behind interfaces and start with one vendor per channel.
- MCP contract drift between docs and code could block onboarding. Mitigation: prioritize the validator harness and sample fixtures early.
- Autonomous execution may create unsafe behavior. Mitigation: ship preview, budget caps, and kill switches before enabling default execution on real apps.
- If delivery stalls, the rollback path is to keep the system in read-only mode with snapshots and visibility only until action policies are trustworthy.

## Verification Steps

- Run `python3 scripts/validate_docs.py` after any documentation change.
- Add automated tests for MCP resources and tools, contract validation fixtures, migration integrity, and key policy decisions.
- Use the official MCP Inspector against both the control-plane server and at least one app integration.
- Exercise the operator console with accessibility smoke checks for keyboard navigation and data-table readability.
- Verify that snapshot ingestion, action execution, and automation runs all produce auditable records tied by correlation ID.

## Open Questions / Locked Assumptions

- Locked assumption: PostgreSQL is the first and only required database in V1.
- Locked assumption: the first UI is server-rendered with progressive enhancement, not a separate SPA.
- Locked assumption: production MCP transport is Streamable HTTP and local validation may use stdio.
- Locked assumption: automation is auto by default, but policy rules can require explicit approval for high-risk or irreversible actions.
