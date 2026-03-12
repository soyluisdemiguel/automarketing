# Automarketing Control Plane

First runnable slice of the portfolio automarketing control plane.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/python -m ensurepip --upgrade
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python main.py
```

The app serves:

- Web console: `http://127.0.0.1:8000/`
- REST API: `http://127.0.0.1:8000/api/applications`
- MCP endpoint: `http://127.0.0.1:8000/mcp`

## Test

```bash
.venv/bin/python -m pytest
python3 scripts/validate_docs.py
```
