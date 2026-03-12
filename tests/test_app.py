from pathlib import Path

from fastapi.testclient import TestClient

from automarketing.app import create_app
from automarketing.db import create_engine_from_url, create_session_factory, initialize_database
from automarketing.sql_repository import SqlAlchemyPortfolioRepository


def build_client(tmp_path: Path) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'test.db'}"
    engine = create_engine_from_url(database_url)
    initialize_database(engine)
    repository = SqlAlchemyPortfolioRepository(create_session_factory(engine))
    repository.seed_demo_data()
    return TestClient(create_app(repository=repository))


def test_healthcheck(tmp_path: Path) -> None:
    client = build_client(tmp_path)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_lists_portfolio_applications(tmp_path: Path) -> None:
    client = build_client(tmp_path)
    response = client.get("/api/applications")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["applications"]) >= 2
    assert payload["applications"][0]["application"]["slug"]


def test_index_renders_portfolio_overview(tmp_path: Path) -> None:
    client = build_client(tmp_path)
    response = client.get("/")
    assert response.status_code == 200
    assert "Portfolio Overview" in response.text


def test_sync_endpoint_creates_snapshot(tmp_path: Path) -> None:
    client = build_client(tmp_path)
    before = client.get("/api/applications/reeldna-ai/snapshots").json()
    sync_response = client.post(
        "/api/applications/reeldna-ai/sync",
        json={"reason": "manual-check", "requested_by": "pytest"},
    )
    after = client.get("/api/applications/reeldna-ai/snapshots").json()

    assert sync_response.status_code == 200
    assert len(after["snapshots"]) == len(before["snapshots"]) + 1


def test_mcp_mount_exists() -> None:
    app = create_app(repository=SqlAlchemyPortfolioRepository(create_session_factory(create_engine_from_url("sqlite+pysqlite:///:memory:"))))
    paths = [getattr(route, "path", None) for route in app.routes]
    assert "/mcp" in paths


def test_contract_validation_endpoint(monkeypatch, tmp_path: Path) -> None:
    async def fake_validate(endpoint_url: str, headers=None):
        return type(
            "Report",
            (),
            {
                "to_dict": lambda self: {
                    "endpoint_url": endpoint_url,
                    "headers": headers or {},
                    "ok": True,
                }
            },
        )()

    monkeypatch.setattr("automarketing.app.validate_mcp_contract", fake_validate)

    client = build_client(tmp_path)
    response = client.post(
        "/api/onboarding/validate-contract",
        json={
            "endpoint_url": "https://portfolio-app.example.com/mcp",
            "headers": {"Authorization": "Bearer test-token"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["endpoint_url"] == "https://portfolio-app.example.com/mcp"


def test_onboarding_endpoint_registers_application(tmp_path: Path) -> None:
    client = build_client(tmp_path)
    response = client.post(
        "/api/onboarding/applications",
        json={
            "slug": "new-app",
            "name": "New App",
            "owner": "growth@example.com",
            "description": "New portfolio app.",
            "categories": ["saas"],
            "monetization_models": ["subscription"],
            "status": "onboarding",
            "mcp_endpoint": "https://new-app.example.com/mcp",
            "capabilities": [
                {
                    "capability": "metrics.read",
                    "action_family": "metrics.latest",
                    "channel": "mcp",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["application"]["slug"] == "new-app"
    assert payload["latest_snapshot"]["users_active"] == 0
