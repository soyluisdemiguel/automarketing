---
Status: Draft
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: High-level system shape, boundaries, and documentation flow for the automarketing control plane.
Related Docs: AGENTS.md, docs/product-specs/portfolio-automarketing-control-plane.md, docs/design-docs/portfolio-control-plane-architecture.md, docs/references/mcp-application-contract.md, docs/generated/db-schema.md
---

# Architecture

## Current State

`automarketing` is a greenfield control-plane product with documentation-first decisions already fixed. No runtime code is checked in yet, but the product scope, system boundaries, MCP integration shape, and first implementation plan are defined so future code does not invent them ad hoc.

## Product Domains

- Core product domain: portfolio automarketing for first-party applications
- Supporting domains: app onboarding, visibility intelligence, campaign execution, automation governance, security, observability, and operator workflows
- Each domain maps back to [docs/product-specs/portfolio-automarketing-control-plane.md](docs/product-specs/portfolio-automarketing-control-plane.md) and the linked design docs or execution plans

## System Boundaries

- Client surfaces:
  - operator web console for humans
  - MCP server over Streamable HTTP for agents and other MCP-capable clients
- Application services:
  - portfolio registry
  - MCP integration gateway for portfolio apps
  - metrics snapshot ingestion
  - visibility intelligence for web and MCP discoverability
  - campaign orchestrator for email, press, and content actions
  - automation scheduler and runner
  - policy, budget, and audit services
- Data stores:
  - PostgreSQL as the source of truth for relational state and historical snapshots
  - optional artifact storage later for large campaign assets or exports
- External integrations:
  - portfolio applications exposing the documented MCP contract
  - email delivery providers
  - press and directory distribution providers
  - SEO, web analytics, and search visibility data sources

## Topology Contract

- The control plane owns the operator console, the public MCP surface, scheduling, policy enforcement, and durable history.
- Each portfolio app owns its product-specific logic and exposes a minimum MCP contract for discovery, metrics, status, and declared actions.
- Human operators work through the web console. External agents work through the control plane MCP server. Neither surface bypasses policy, budget, or audit enforcement.
- Historical state is snapshot-first: daily business, usage, and visibility snapshots plus on-demand refreshes triggered by users, agents, or automation policies.

## Dependency Direction

- Product specs define intended behavior.
- Design docs define implementation choices.
- Architecture sets boundaries and layering rules.
- Generated artifacts summarize derived state and must never become the primary source of truth.

## Layering Rules

- Growth policy, budget rules, and automation stop conditions live in domain services, not in provider adapters.
- MCP contract definitions stay independent from internal persistence tables so apps can evolve behind a stable integration boundary.
- Web and MCP surfaces share the same application services and audit trails.
- Integration code sits at the edges and must declare failure handling, retry policy, and kill-switch behavior.
- Security and reliability requirements must be captured before enabling a new action or channel in autonomous mode.

## Required Future Additions At Code Time

- Replace conceptual data model guidance with generated schema output in [docs/generated/db-schema.md](docs/generated/db-schema.md) once migrations exist.
- Add request/data-flow diagrams and deployment topology when the first runtime components are implemented.
- Record concrete provider selections for email, press, and visibility intelligence in the design docs before integration code lands.

## Documentation Flow

- Use [docs/product-specs/index.md](docs/product-specs/index.md) for feature intent and the canonical product spec.
- Use [docs/design-docs/index.md](docs/design-docs/index.md) for implementation decisions, especially the control-plane architecture doc.
- Use [docs/references/mcp-application-contract.md](docs/references/mcp-application-contract.md) for portfolio app integration requirements.
- Use [docs/references/skills-and-automations.md](docs/references/skills-and-automations.md) for the operating skill and automation catalog.
- Use [docs/exec-plans/active/2026-03-12-control-plane-foundation.md](docs/exec-plans/active/2026-03-12-control-plane-foundation.md) for the first implementation sequence and [docs/exec-plans/tech-debt-tracker.md](docs/exec-plans/tech-debt-tracker.md) for unresolved structural gaps.
