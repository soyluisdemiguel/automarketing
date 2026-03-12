---
Status: Active
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Required skills and proposed automation catalog for operating and evolving the automarketing control plane.
Related Docs: index.md, ../product-specs/portfolio-automarketing-control-plane.md, ../design-docs/portfolio-control-plane-architecture.md, ../exec-plans/active/2026-03-12-control-plane-foundation.md
---

# Skills And Automations

## Required Skills

The following skills should exist before the product scales beyond the first pilot apps. These are design-time requirements in this phase; they are not yet active Codex assets unless explicitly installed later.

| Skill | Purpose | Expected inputs | Expected output |
| --- | --- | --- | --- |
| `portfolio-app-onboarding` | Register a new app, validate ownership, and map its MCP contract into the control plane | App URL, owner, monetization model, MCP endpoint, auth notes | Onboarding checklist, missing fields, and recommended capabilities |
| `mcp-contract-validator` | Verify that an app conforms to the documented MCP contract | Endpoint, credentials, contract version, expected capabilities | Pass or fail report with missing resources, tools, or schema drift |
| `visibility-research` | Research web and MCP discoverability, tracked queries, competitors, and content gaps | App identity, target queries, markets, competitors | Visibility report with ranked opportunities and risks |
| `campaign-orchestrator` | Prepare and review email campaigns and related growth sequences | App, KPI, segment, budget, content inputs | Campaign plan, execution checklist, and tracking expectations |
| `press-opportunity-scout` | Identify press, directories, and media opportunities | App positioning, launches, proof points, target outlets | Prioritized outlet list, pitch angles, and deadlines |
| `docs-gardener-automarketing` | Keep specs, plans, scorecards, and references aligned with current scope | Changed docs, stale dates, open debt, active plans | Documentation maintenance report and follow-up tasks |

## Product Automations

These automations belong to the product itself and should be implemented as scheduled or event-driven jobs in the control plane.

| Automation | Trigger | Inputs / sources | Output | Success criteria | Stop / safety rule |
| --- | --- | --- | --- | --- | --- |
| `daily-snapshot-ingestion` | Daily at 02:00 UTC plus manual trigger | App MCP metrics resources and health resources | New `metric_snapshots` and `integration_health` rows | Snapshot freshness SLA met for onboarded apps | Stop after repeated auth or schema failures; pause the app automation on threshold breach |
| `official-registry-ingestion` | Daily at 01:00 UTC plus manual trigger | Official MCP registry `GET /v0.1/servers` catalog pages | New or refreshed `benchmark_targets` and registry metadata | Public benchmark catalog freshness stays within one day | Stop on repeated registry transport or schema failures and keep last successful catalog |
| `visibility-refresh` | Daily at 02:00 UTC for tracked queries plus manual trigger | Search visibility sources, MCP discovery checks, app metadata, Search Console property | New `visibility_observations`, reachability status, and rank deltas | New or changed visibility signals recorded for tracked surfaces in EN and ES | Stop when provider quotas or app limits are exceeded |
| `benchmark-comparison-refresh` | Daily at 03:00 UTC | Public benchmark catalog, owned visibility observations, tracked queries | Ranked benchmark cohort and missed-opportunity summaries | Each owned app has an explainable benchmark cohort within one day | Stop when benchmark inputs are stale or insufficient |
| `opportunity-scoring` | After snapshot or visibility refresh | Historical metrics, visibility deltas, active campaigns | Ranked opportunities per app | Operators receive a prioritized next-action list | Stop when inputs are stale or confidence is below threshold |
| `email-campaign-runner` | Scheduled per approved or auto-allowed campaign | App capabilities, audience config, content assets, budget policy | Campaign run record and delivery outcome | Campaign executes within budget and records attributable results | Stop on provider errors, unsubscribe risk, or budget breach |
| `press-opportunity-monitor` | Twice weekly | App launches, changelogs, visibility gaps, outlet lists | Candidate press targets and pitch tasks | New outlet opportunities appear with rationale | Stop when no fresh launch or evidence exists |
| `campaign-outcome-reconciliation` | Daily for active or recently finished campaigns | Campaign run records, app metrics, provider reports | Attribution summaries and follow-up recommendations | Outcome data is attached to campaign runs within one day | Stop when source metrics are incomplete or attribution confidence is low |

## Codex Automations For This Repo

These are proposed recurring automations for the repository and team workflow. They remain documented only until explicitly created.

| Automation | Suggested cadence | Inputs / sources | Output | Success criteria | Stop / safety rule |
| --- | --- | --- | --- | --- | --- |
| `docs-gap-review` | Daily 09:00 Europe/Madrid | Repo docs, metadata dates, validator output | Inbox item listing stale docs, broken links, or missing references | Documentation drift is identified before implementation spreads | Stop if the validator already fails for unrelated reasons and escalate instead |
| `weekly-visibility-report` | Mondays 08:30 Europe/Madrid | Visibility research notes, app list, tracked queries | Weekly portfolio visibility brief | Operators get one actionable visibility summary per week | Stop if no app inventory exists yet |
| `mcp-contract-audit` | Wednesdays 10:00 Europe/Madrid | MCP contract doc, app inventory, conformance reports | Drift report and follow-up tasks | Contract drift is caught before onboarding more apps | Stop if no validator harness exists yet; report the blocker |
| `portfolio-delta-watch` | Daily 07:30 Europe/Madrid | Snapshot tables, campaign summaries, integration health | Short report of money, user, or health deltas | Material changes are surfaced within one day | Stop if snapshot freshness is below the documented baseline |
| `plan-hygiene-check` | Fridays 16:00 Europe/Madrid | Active exec plans, debt tracker, quality score | Plan maintenance report | Active work retains a current plan and explicit debt links | Stop if there is no active implementation work |

## Operating Rules

- Every automation definition must declare its owner, trigger, inputs, outputs, success criteria, and stop rule before implementation.
- Product automations must create auditable run records in `automation_runs`.
- Repo automations should open actionable inbox items rather than silently mutating tracked files.
- If a skill or automation becomes obsolete, update this document first and then adjust the linked spec, design doc, or debt entry.
- Visibility automations must distinguish reachable MCP endpoints from open MCP endpoints and preserve both signals in storage and reporting.
