from fastapi.testclient import TestClient

from automarketing.app import create_app


def build_client() -> TestClient:
    return TestClient(create_app())


def test_healthcheck() -> None:
    client = build_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_lists_portfolio_applications() -> None:
    client = build_client()
    response = client.get("/api/applications")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["applications"]) >= 2
    assert payload["applications"][0]["application"]["slug"]


def test_index_renders_portfolio_overview() -> None:
    client = build_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "Portfolio Overview" in response.text


def test_sync_endpoint_creates_snapshot() -> None:
    client = build_client()
    before = client.get("/api/applications/reeldna-ai/snapshots").json()
    sync_response = client.post(
        "/api/applications/reeldna-ai/sync",
        json={"reason": "manual-check", "requested_by": "pytest"},
    )
    after = client.get("/api/applications/reeldna-ai/snapshots").json()

    assert sync_response.status_code == 200
    assert len(after["snapshots"]) == len(before["snapshots"]) + 1


def test_mcp_mount_exists() -> None:
    app = create_app()
    paths = [getattr(route, "path", None) for route in app.routes]
    assert "/mcp" in paths
