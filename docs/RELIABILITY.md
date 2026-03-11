---
Status: Draft
Owner: Engineering
Last Reviewed: 2026-03-11
Source of Truth For: Reliability expectations, readiness checks, and incident-response baseline for water.
Related Docs: QUALITY_SCORE.md, SECURITY.md, ../ARCHITECTURE.md, DOC_GARDENING.md
---

# Reliability

## Baseline Expectations

Before any production release, define:

- the user-visible service boundary;
- primary failure modes;
- SLIs and target SLOs;
- logging, metrics, and tracing expectations;
- backup and recovery strategy;
- on-call or escalation ownership.

## Readiness Checklist

| Area | Required Evidence | Current State |
| --- | --- | --- |
| Availability | Defined SLIs/SLOs and alert thresholds | TBD |
| Degradation | Known partial-failure behavior and graceful fallbacks | TBD |
| Recovery | Runbook for rollback, restore, or failover | TBD |
| Data Safety | Backup cadence and restore test result | TBD |
| Incident Learning | Post-incident review path and owner | TBD |

## Operating Rules

- No launch without at least one documented rollback path
- No critical dependency without a failure-handling story
- No recurring alert without a named owner and response expectation
