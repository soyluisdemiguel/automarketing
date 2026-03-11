---
Status: Draft
Owner: Engineering
Last Reviewed: 2026-03-11
Source of Truth For: High-level system shape, boundaries, and documentation flow for water.
Related Docs: AGENTS.md, docs/DESIGN.md, docs/FRONTEND.md, docs/generated/db-schema.md
---

# Architecture

## Current State

`water` is currently a greenfield repository. No runtime components, deployment topology, or persistence model are checked in yet. This document defines the architecture contract that future implementation must fill in rather than leaving those decisions implicit.

## Planned Architecture Sections

### Product Domains

- Core product domain: `TBD`
- Supporting domains: onboarding, content, observability, security, and operations once they exist
- Each domain should eventually map to a product spec and, when needed, a design doc

### System Boundaries

- Client surfaces: `TBD`
- Application services: `TBD`
- Data stores: represented in [docs/generated/db-schema.md](docs/generated/db-schema.md) once a schema exists
- External integrations: document here before adding them to code

### Dependency Direction

- Product specs define intended behavior
- Design docs define implementation choices
- Architecture sets boundaries and layering rules
- Generated artifacts summarize derived state and must never become the primary source of truth

### Layering Rules

- Domain logic should not depend on delivery details
- Integration code should sit at system edges
- UI concerns should be isolated from business rules
- Security and reliability requirements must be captured before production exposure

## Required Future Additions

- A diagram or narrative showing request/data flow
- Explicit runtime stack and hosting model
- Authentication and authorization boundaries
- Persistence and migration strategy
- Observability boundaries, SLI ownership, and failure domains

## Documentation Flow

- Use [docs/product-specs/index.md](docs/product-specs/index.md) for feature intent
- Use [docs/design-docs/index.md](docs/design-docs/index.md) for implementation decisions
- Use [docs/exec-plans/tech-debt-tracker.md](docs/exec-plans/tech-debt-tracker.md) to track structural gaps that should not be forgotten
