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

## Visibility intelligence configuration

Optional environment variables for live visibility refreshes:

```bash
export AUTOMARKETING_OFFICIAL_REGISTRY_URL='https://registry.modelcontextprotocol.io/v0.1/servers'
export AUTOMARKETING_SERPAPI_API_KEY='...'
export AUTOMARKETING_GOOGLE_API_ACCESS_TOKEN='...'
```

Key endpoints:

```bash
curl http://127.0.0.1:8000/api/benchmarks
curl -X POST http://127.0.0.1:8000/api/benchmarks/refresh -H "Content-Type: application/json" -d '{"requested_by":"manual"}'
curl -X POST http://127.0.0.1:8000/api/applications/reeldna-ai/visibility/config -H "Content-Type: application/json" -d @examples/onboarding/reeldna-ai-visibility.json
curl -X POST http://127.0.0.1:8000/api/applications/reeldna-ai/visibility/refresh -H "Content-Type: application/json" -d '{"sources":["official_registry"],"requested_by":"manual"}'
curl http://127.0.0.1:8000/api/applications/reeldna-ai/visibility/report
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

Example visibility config:

```bash
cat examples/onboarding/reeldna-ai-visibility.json
```

## Prompt template for a new thread

When you want me to onboard and work on another app with MCP, open a new thread and paste this prompt filled in:

```text
Quiero que trabajes sobre esta app de nuestro portfolio y la integres en automarketing.

Contexto de la app:
- slug: <app-slug>
- nombre: <App Name>
- owner: <owner@company.com>
- descripcion: <one paragraph>
- categorias: [<cat1>, <cat2>]
- monetizacion: [<subscription|usage|services|...>]
- website_url: <https://app.example.com/>
- mcp_endpoint: <https://app.example.com/mcp>
- search_console_property: <https://app.example.com/> o <sc-domain:example.com> o <none>

Acceso MCP:
- autenticacion: <bearer|none|other>
- header de auth: <Authorization|X-...|none>
- token o secreto: <secret>
- notas de acceso: <IP allowlist / VPN / cert / rate limits / none>

Capacidades MCP declaradas:
- recursos: [app://manifest, app://health, app://metrics/current, ...]
- tools: [sync_snapshot, preview_growth_action, execute_growth_action, ...]
- action families soportadas: [email_campaign.send, seo_metadata.refresh, ...]

Configuracion de visibilidad:
- idiomas objetivo: [en, es]
- paises objetivo: [us, es]
- brand_terms: [<brand>, <brand + mcp>, ...]
- tracked_queries:
  - query: <query 1>
    language: <en|es>
    country: <us|es>
    surface: <web|mcp_registry|mcp_directory>
    query_kind: <brand|task|competitor>
    priority: <1..n>

Objetivo de este hilo:
- valida el contrato MCP
- configura visibility tracking
- refresca official registry / web / search console segun credenciales disponibles
- genera el primer visibility report
- dime gaps, oportunidades y siguientes acciones
```

Minimum secrets needed for full work in that new thread:

- MCP auth secret for the app, if the endpoint is private
- `SERPAPI` key if you want live web ranking refresh
- Google OAuth access token if you want live Search Console ingestion

## Test

```bash
.venv/bin/alembic upgrade head
.venv/bin/python -m pytest
python3 scripts/validate_docs.py
```
