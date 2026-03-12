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

## Test

```bash
.venv/bin/alembic upgrade head
.venv/bin/python -m pytest
python3 scripts/validate_docs.py
```
