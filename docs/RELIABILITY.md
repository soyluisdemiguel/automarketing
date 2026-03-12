---
Status: Draft
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Reliability expectations, readiness checks, and incident-response baseline for the automarketing control plane.
Related Docs: QUALITY_SCORE.md, SECURITY.md, ../ARCHITECTURE.md, design-docs/portfolio-control-plane-architecture.md, DOC_GARDENING.md
---

# Reliability

## Baseline Expectations

Before any production release, define:

- the user-visible service boundary across the web console, MCP surface, automation scheduler, and outbound campaign execution;
- primary failure modes, especially stale snapshots, duplicate action execution, provider outages, and app integration failures;
- SLIs and target SLOs for API availability, snapshot freshness, automation success rate, and action latency;
- logging, metrics, and tracing expectations with correlation IDs spanning app, campaign, and automation runs;
- backup and recovery strategy for PostgreSQL and campaign or audit artifacts;
- on-call or escalation ownership for both platform health and outbound action anomalies.

## Readiness Checklist

| Area | Required Evidence | Current State |
| --- | --- | --- |
| Availability | Defined SLIs/SLOs and alert thresholds | Service boundaries and required SLIs are documented; numerical targets will be set with the first deployable service |
| Degradation | Known partial-failure behavior and graceful fallbacks | Design requires stale-data labeling, provider kill switches, and per-app automation pause controls |
| Recovery | Runbook for rollback, restore, or failover | The first exec plan requires rollback paths for campaigns, budgets, and action execution before launch |
| Data Safety | Backup cadence and restore test result | PostgreSQL is the planned source of truth; backup cadence and restore drills remain implementation work |
| Incident Learning | Post-incident review path and owner | Ownership is Product + Engineering until a dedicated operations role exists |

## Operating Rules

- No automated action without an idempotency key, audit record, and stop condition.
- No launch without at least one documented rollback path for outbound campaigns and policy changes.
- No critical dependency without a failure-handling story, rate-limit posture, and safe-disable path.
- No recurring alert without a named owner and response expectation.
