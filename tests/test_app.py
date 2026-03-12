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


def test_visibility_config_endpoint_uses_service(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    client.app.state.visibility_service.configure_tracking = lambda app_slug, payload: type(
        "Config",
        (),
        {
            "model_dump": lambda self, mode="json": {
                "website_url": payload.website_url,
                "primary_language": payload.primary_language,
                "tracked_queries": [item.model_dump(mode="json") for item in payload.tracked_queries],
            }
        },
    )()

    response = client.post(
        "/api/applications/reeldna-ai/visibility/config",
        json={
            "website_url": "https://reeldna.example.com/",
            "primary_language": "en",
            "primary_country": "us",
            "brand_terms": ["reeldna"],
            "tracked_queries": [
                {
                    "query": "reeldna ai",
                    "language": "en",
                    "country": "us",
                    "surface": "web",
                    "query_kind": "brand",
                    "priority": 1,
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["website_url"] == "https://reeldna.example.com/"
    assert payload["tracked_queries"][0]["query"] == "reeldna ai"


def test_visibility_report_endpoint_uses_service(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    client.app.state.visibility_service.build_report = lambda app_slug: type(
        "Report",
        (),
        {
            "model_dump": lambda self, mode="json": {
                "app_slug": app_slug,
                "web_visibility_score": 72,
                "mcp_visibility_score": 68,
                "confidence": "partial",
                "owned_observations": [],
                "benchmark_comparison": [],
                "top_missed_opportunities": [],
                "web_breakdown": {"value": 72},
                "mcp_breakdown": {"value": 68},
            }
        },
    )()

    response = client.get("/api/applications/reeldna-ai/visibility/report")

    assert response.status_code == 200
    payload = response.json()
    assert payload["web_visibility_score"] == 72
    assert payload["mcp_visibility_score"] == 68


def test_visibility_refresh_endpoint_uses_service(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    client.app.state.visibility_service.refresh_application = lambda app_slug, payload: {
        "app_slug": app_slug,
        "requested_sources": payload.sources,
        "completed_sources": ["official_registry"],
        "skipped_sources": ["search_console"],
        "run_ids": ["visrun-001"],
        "observations_recorded": 3,
        "benchmark_observations_recorded": 1,
    }

    response = client.post(
        "/api/applications/reeldna-ai/visibility/refresh",
        json={"sources": ["official_registry", "search_console"], "requested_by": "pytest"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["completed_sources"] == ["official_registry"]
    assert payload["skipped_sources"] == ["search_console"]


def test_benchmark_refresh_endpoint_uses_service(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    client.app.state.visibility_service.refresh_benchmarks = lambda requested_by="api": (
        [
            type(
                "Benchmark",
                (),
                {
                    "model_dump": lambda self, mode="json": {
                        "external_id": "official_registry:agency.lona/trading"
                    }
                },
            )()
        ],
        type(
            "Run",
            (),
            {
                "model_dump": lambda self, mode="json": {
                    "id": "visrun-123",
                    "status": "completed",
                }
            },
        )(),
    )

    response = client.post("/api/benchmarks/refresh", json={"requested_by": "pytest"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["run"]["status"] == "completed"
    assert payload["benchmarks"][0]["external_id"] == "official_registry:agency.lona/trading"
