---
Status: Draft
Owner: Engineering
Last Reviewed: 2026-03-12
Source of Truth For: Security policy, engineering guardrails, and review triggers for the automarketing control plane.
Related Docs: RELIABILITY.md, QUALITY_SCORE.md, ../ARCHITECTURE.md, ../AGENTS.md, references/mcp-application-contract.md
---

# Security

## Reporting

Until a dedicated security contact exists, do not disclose vulnerabilities publicly first. Prefer private reporting through the repository owners or GitHub private vulnerability reporting if it is enabled for this repository.

## Engineering Guardrails

- Never commit secrets, tokens, or production credentials.
- Prefer least privilege for every integration, especially per-app MCP credentials and outbound provider tokens.
- Document authentication and authorization boundaries before exposing a new MCP action or web control.
- Require action allowlists, budget caps, and kill-switch support for autonomous execution.
- Review data retention and deletion expectations before storing user, campaign, or provider payloads.
- Record audit correlation IDs for every outbound action so security and reliability investigations share the same trail.

## Security Review Triggers

Perform a security review when work:

- introduces or changes authentication or authorization logic;
- stores sensitive, user-generated, or provider-returned data;
- adds third-party integrations, webhooks, or file uploads;
- changes MCP action scope, approval rules, or budget enforcement;
- changes network exposure or deployment boundaries.

## Supported Versions

| Version | Supported |
| --- | --- |
| `main` | Yes |

Update this table when release branches exist.
