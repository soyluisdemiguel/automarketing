# Automarketing Control Plane

First runnable slice of the portfolio automarketing control plane.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/python -m ensurepip --upgrade
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/alembic upgrade head
.venv/bin/python main.py
```

The app serves:

- Web console: `http://127.0.0.1:8000/`
- REST API: `http://127.0.0.1:8000/api/applications`
- MCP endpoint: `http://127.0.0.1:8000/mcp`

## PostgreSQL development setup

```bash
cp .env.example .env
docker compose up -d postgres
.venv/bin/python -m pip install -e ".[dev]"
set -a && source .env && set +a
.venv/bin/alembic upgrade head
.venv/bin/python scripts/seed_demo_data.py --reset
.venv/bin/python main.py
```

## Validate a portfolio app contract

```bash
.venv/bin/python scripts/validate_mcp_contract.py https://your-app.example.com/mcp
```

The control plane also exposes contract validation through HTTP:

```bash
curl -X POST http://127.0.0.1:8000/api/onboarding/validate-contract \
  -H "Content-Type: application/json" \
  -d '{"endpoint_url":"https://your-app.example.com/mcp"}'
```

## Connect to an existing PostgreSQL instance

Set both the database URL and the dedicated schema name before running migrations:

```bash
export AUTOMARKETING_DATABASE_URL='postgresql+psycopg://sysadmin01:***@reeldna.postgres.database.azure.com:5432/reeldna?sslmode=require'
export AUTOMARKETING_DATABASE_SCHEMA='automarketing'
.venv/bin/alembic upgrade head
```

## Minimum onboarding payload for one portfolio app

This is the minimum information needed to query one of your apps through its MCP interface and start storing historical metrics:

```json
{
  "app_slug": "reeldna-ai",
  "name": "ReelDNA AI",
  "owner": "growth@your-company.com",
  "base_url": "https://reeldna.example.com",
  "mcp_endpoint": "https://reeldna.example.com/mcp",
  "authentication": {
    "type": "bearer",
    "header_name": "Authorization",
    "token": "<secret>"
  },
  "categories": ["ai", "analytics", "b2b"],
  "monetization_models": ["subscription", "pilot-contracts"],
  "capabilities": [
    {
      "capability": "metrics.read",
      "resource": "app://metrics/latest"
    },
    {
      "capability": "campaigns.send",
      "tool": "campaign_send_email"
    }
  ],
  "expected_metrics": [
    "users_active",
    "revenue_eur",
    "conversions",
    "web_visibility_score",
    "mcp_visibility_score"
  ]
}
```

You can register that app in the control plane with:

```bash
curl -X POST http://127.0.0.1:8000/api/onboarding/applications \
  -H "Content-Type: application/json" \
  -d @examples/onboarding/reeldna-ai.json
```

## Test

```bash
.venv/bin/alembic upgrade head
.venv/bin/python -m pytest
python3 scripts/validate_docs.py
```
