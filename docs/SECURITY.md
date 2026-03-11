---
Status: Draft
Owner: Engineering
Last Reviewed: 2026-03-11
Source of Truth For: Security policy, engineering guardrails, and review triggers for water.
Related Docs: RELIABILITY.md, QUALITY_SCORE.md, ../ARCHITECTURE.md, ../AGENTS.md
---

# Security

## Reporting

Until a dedicated security contact exists, do not disclose vulnerabilities publicly first. Prefer private reporting through the repository owners or GitHub private vulnerability reporting if it is enabled for this repository.

## Engineering Guardrails

- Never commit secrets, tokens, or production credentials
- Prefer least privilege for every future integration
- Document authentication and authorization boundaries before exposure
- Review data retention and deletion expectations before storing user data
- Track dependency update policy once a runtime stack exists

## Security Review Triggers

Perform a security review when work:

- introduces authentication or authorization logic;
- stores sensitive or user-generated data;
- adds third-party integrations, webhooks, or file uploads;
- changes network exposure or deployment boundaries.

## Supported Versions

| Version | Supported |
| --- | --- |
| `main` | Yes |

Update this table when release branches exist.
