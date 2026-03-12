---
Status: Active
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: When and how to write ExecPlans for automarketing.
Related Docs: ../AGENTS.md, exec-plans/active/README.md, exec-plans/completed/README.md, exec-plans/tech-debt-tracker.md, product-specs/portfolio-automarketing-control-plane.md
---

# PLANS

Use an ExecPlan when work is expected to take more than one focused session, touches multiple subsystems, carries user or operational risk, or requires staged validation. Small, local, low-risk edits do not need a plan.

## Plan Lifecycle

1. Open or update a product spec or design doc if intent is not stable.
2. Create an active plan under [exec-plans/active/README.md](exec-plans/active/README.md) using the template below.
3. Link the plan from the relevant spec, design doc, or debt item.
4. Keep the plan current while work is in progress.
5. Move the finished plan into [exec-plans/completed/README.md](exec-plans/completed/README.md) and record follow-up debt in [exec-plans/tech-debt-tracker.md](exec-plans/tech-debt-tracker.md).

## Required Sections

- Summary
- Goal and success criteria
- Out of scope
- Current state
- Intended implementation
- Risks and rollback
- Verification steps
- Open questions or locked assumptions

## Template

```md
---
Status: Draft
Owner: Engineering
Last Reviewed: YYYY-MM-DD
Source of Truth For: Execution plan for <initiative>.
Related Docs: <spec>, <design doc>, <debt item>
---

# <Plan Title>

## Summary

## Goal and Success Criteria

## Out of Scope

## Current State

## Intended Implementation

## Risks and Rollback

## Verification Steps

## Open Questions / Locked Assumptions
```

## Plan Hygiene

- Prefer one active plan per meaningful initiative.
- Keep plans implementation-ready; avoid vague TODO lists.
- Close the loop by updating linked docs after execution.
