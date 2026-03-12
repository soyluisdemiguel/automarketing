---
Status: Active
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Prioritized technical debt ledger for automarketing.
Related Docs: ../QUALITY_SCORE.md, ../PLANS.md, ../../ARCHITECTURE.md, ../design-docs/portfolio-control-plane-architecture.md
---

# Tech Debt Tracker

| Debt | Why it exists | User/ops impact | Priority | Owner | Resolution path | Linked plan |
| --- | --- | --- | --- | --- | --- | --- |
| Channel provider selection is still abstract | The control plane is now defined at the architecture level, but email, press, and visibility providers are intentionally left as adapters until implementation starts | Channel execution cannot begin until vendor choices and credential models are fixed | High | Product + Engineering | Pick the first provider set during the implementation phase and update the design doc with concrete adapters | [2026-03-12-control-plane-foundation.md](active/2026-03-12-control-plane-foundation.md) |
| Real portfolio app fixtures are not wired into the MCP contract validator yet | The validator CLI and library exist, but they still need live fixture coverage or CI integration against real app endpoints | Contract drift could still slip through if no real app is exercised regularly | Medium | Engineering | Add fixture servers or CI checks for the first onboarded portfolio apps | [2026-03-12-control-plane-foundation.md](active/2026-03-12-control-plane-foundation.md) |
| Runtime scaffolding and migrations are not implemented | This phase only defined the product, architecture, and operating model | No service can be executed, persisted, or integration-tested yet | High | Engineering | Implement the Python control plane, PostgreSQL migrations, and worker roles in the next phase | [2026-03-12-control-plane-foundation.md](active/2026-03-12-control-plane-foundation.md) |
