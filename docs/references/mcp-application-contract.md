---
Status: Active
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Minimum MCP contract that each portfolio app must expose to the automarketing control plane.
Related Docs: index.md, ../design-docs/portfolio-control-plane-architecture.md, ../product-specs/portfolio-automarketing-control-plane.md, ../../ARCHITECTURE.md
---

# MCP Application Contract

## Purpose

Every portfolio app integrates with the control plane through one MCP contract instead of bespoke APIs. The contract standardizes discovery, health, metrics, historical access, and side-effectful growth actions.

## Protocol Alignment

- MCP primitives map to contract responsibilities:
  - resources for read-only context
  - tools for operational actions
  - prompts for optional operator-guided workflows
- Production transport should be Streamable HTTP.
- Local development or conformance checks may use stdio.
- For HTTP transport, prefer auth that aligns with MCP's authorization model; for same-organization deployments, per-app bearer credentials are acceptable if rotation and audit requirements are documented.

## Required Resources

| Resource URI | Purpose | Notes |
| --- | --- | --- |
| `app://manifest` | App identity, owner, categories, monetization model, environment, and contract version | Required for onboarding |
| `app://health` | Current health state, dependency status, and alert summary | Used for overview and incident triage |
| `app://metrics/current` | Current revenue, users, conversion, retention, and health summary | Returned as structured JSON |
| `app://metrics/snapshots/{date}` | Snapshot for a specific date | Used for reconciliation and backfill |
| `app://metrics/range/{start}/{end}` | Historical range access | Supports charting and analysis |
| `app://campaigns/active` | Active campaigns and current execution state | Includes budget and outcome summary |
| `app://visibility/current` | Current SEO and MCP discoverability observations known to the app | May include sitemap, metadata, or index health |
| `app://integrations` | Declared outbound integrations and auth status | Used for risk and dependency views |

## Required Tools

| Tool | Purpose | Minimum inputs |
| --- | --- | --- |
| `sync_snapshot` | Force a fresh data pull from the app's source systems | `reason`, `requested_by` |
| `preview_growth_action` | Validate a proposed action, estimate risk, and return impacted entities before execution | `action_type`, `target_channel`, `parameters`, `budget_limit` |
| `execute_growth_action` | Execute an allowed action against the app | `action_type`, `target_channel`, `parameters`, `budget_limit`, `idempotency_key`, `requested_by` |
| `pause_growth_action` | Pause or cancel an active automation or campaign | `target_id`, `reason`, `requested_by` |
| `resume_growth_action` | Resume a paused automation or campaign if policy allows it | `target_id`, `requested_by` |
| `list_budget_policies` | Report applicable limits and policy thresholds | `scope` |

`execute_growth_action` must support at least these action families when the app declares the corresponding capability:

- `email_campaign.send`
- `press_pitch.publish`
- `web_copy.update`
- `seo_metadata.refresh`
- `promotion.set`
- `pricing.update`
- `content_sync.run`

## Optional Prompts

Prompts are optional because MCP treats them as user-controlled rather than automatically executed. Apps may expose prompts such as:

- `summarize_growth_state`
- `draft_press_pitch`
- `propose_onboarding_copy`

These prompts should package app-specific context for operators, not replace the required resources and tools.

## Action Payload Rules

Every side-effectful action payload must include:

- `action_type`
- `target_channel`
- `parameters`
- `budget_limit`
- `idempotency_key`
- `requested_by`
- `scheduled_for`
- `dry_run` when the caller wants validation only

Apps must reject undeclared action types or channels and return structured validation errors.

## Security And Safety Requirements

- Every app must expose its supported capabilities and allowed action families through `app://manifest` or `app://integrations`.
- Every side-effectful tool must enforce budget caps, allowlists, and idempotency.
- Every app must provide a kill-switch-compatible pause path through the pause tool.
- All executions must return a correlation ID so control-plane audit logs can join request and result records.
- Credential rotation expectations and endpoint ownership must be recorded during onboarding.

## Conformance Checklist

An app is considered onboardable only when it:

- serves the required resources;
- implements the required tools for its declared capabilities;
- supports Streamable HTTP in environments used by the control plane;
- returns structured JSON that matches the documented fields;
- passes `scripts/validate_mcp_contract.py` against its MCP endpoint;
- can be inspected successfully with the official MCP Inspector during validation.

Official MCP references used for this contract:

- [Understanding MCP servers](https://modelcontextprotocol.io/docs/learn/server-concepts)
- [MCP SDKs](https://modelcontextprotocol.io/docs/sdk)
- [MCP basic specification overview](https://modelcontextprotocol.io/specification/2025-06-18/basic/index)
