import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from automarketing.db import create_engine_from_url, create_session_factory, initialize_database
from automarketing.models import BenchmarkObservation, BenchmarkTarget, VisibilityObservation, VisibilityRefreshRequest
from automarketing.settings import Settings
from automarketing.sql_repository import SqlAlchemyPortfolioRepository
from automarketing.visibility_service import REACHABLE_STATUSES, VisibilityService


def build_repository(tmp_path: Path) -> SqlAlchemyPortfolioRepository:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'visibility-service.db'}"
    engine = create_engine_from_url(database_url)
    initialize_database(engine)
    repository = SqlAlchemyPortfolioRepository(create_session_factory(engine))
    repository.seed_demo_data()
    return repository


def build_service(tmp_path: Path) -> VisibilityService:
    return VisibilityService(
        build_repository(tmp_path),
        Settings(
            seed_demo_data=False,
            serpapi_api_key=None,
            google_api_access_token=None,
        ),
    )


def test_visibility_report_includes_registry_and_benchmark_deltas(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    repository = service._repository

    repository.upsert_benchmark_targets(
        [
            BenchmarkTarget(
                external_id="official_registry:reeldna-ai",
                source="official_registry",
                name="reeldna-ai",
                title="ReelDNA AI MCP",
                description="Official ReelDNA AI MCP listing.",
                website_url="https://reeldna.example.com/",
                remote_url="https://reeldna.example.com/mcp",
                repository_url="https://github.com/example/reeldna",
                last_seen_at=datetime.now(timezone.utc),
            )
        ]
    )
    repository.record_visibility_observations(
        "reeldna-ai",
        [
            VisibilityObservation(
                query="reeldna ai mcp",
                surface="mcp_registry",
                position=1,
                observed_url="https://reeldna.example.com/mcp",
                observed_at=service._repository.list_visibility("reeldna-ai")[0].observed_at,
                source="official_registry",
                result_type="reachable_auth_required",
                is_owned_result=True,
            ),
            VisibilityObservation(
                query="recipe advisor manufacturing ai",
                surface="web",
                position=4,
                observed_url="https://reeldna.example.com/",
                observed_at=service._repository.list_visibility("reeldna-ai")[0].observed_at,
                source="serpapi",
                is_owned_result=True,
            ),
        ],
    )
    repository.record_benchmark_observations(
        [
            BenchmarkObservation(
                benchmark_external_id="official_registry:reeldna-ai",
                query="recipe advisor manufacturing ai",
                surface="web",
                position=2,
                observed_url="https://reeldna.example.com/",
                observed_at=service._repository.list_visibility("reeldna-ai")[0].observed_at,
                source="serpapi",
            )
        ]
    )

    report = service.build_report("reeldna-ai")

    assert report.mcp_visibility_score >= 60
    assert report.mcp_breakdown.remote_reachability == 25
    assert report.web_visibility_score >= 10
    assert report.benchmark_comparison


def test_classify_remote_endpoint_maps_reachable_categories(monkeypatch, tmp_path: Path) -> None:
    service = build_service(tmp_path)

    class Response:
        def __init__(self, status_code: int) -> None:
            self.status_code = status_code

    monkeypatch.setattr("automarketing.visibility_service.httpx.get", lambda *a, **k: Response(401))
    assert service.classify_remote_endpoint("https://example.com/mcp") == "reachable_auth_required"

    monkeypatch.setattr("automarketing.visibility_service.httpx.get", lambda *a, **k: Response(406))
    assert (
        service.classify_remote_endpoint("https://example.com/mcp")
        == "reachable_negotiation_required"
    )


@pytest.mark.skipif(
    os.getenv("AUTOMARKETING_RUN_LIVE_VISIBILITY_TESTS") != "1",
    reason="Set AUTOMARKETING_RUN_LIVE_VISIBILITY_TESTS=1 to enable live visibility smoke tests.",
)
def test_live_official_registry_smoke(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    benchmarks, run = service.refresh_benchmarks(requested_by="pytest-live", max_pages=1)

    assert run.status == "completed"
    assert benchmarks


@pytest.mark.skipif(
    os.getenv("AUTOMARKETING_RUN_LIVE_VISIBILITY_TESTS") != "1",
    reason="Set AUTOMARKETING_RUN_LIVE_VISIBILITY_TESTS=1 to enable live visibility smoke tests.",
)
def test_live_remote_mcp_reachability_smoke(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    benchmarks, _ = service.refresh_benchmarks(requested_by="pytest-live", max_pages=1)

    statuses = [
        service.classify_remote_endpoint(item.remote_url)
        for item in benchmarks[:5]
        if item.remote_url
    ]

    assert statuses
    assert all(status in REACHABLE_STATUSES or status.startswith("unreachable_") for status in statuses)
    assert any(status in REACHABLE_STATUSES for status in statuses)


@pytest.mark.skipif(
    os.getenv("AUTOMARKETING_RUN_LIVE_APP_VISIBILITY_TEST") != "1",
    reason="Set AUTOMARKETING_RUN_LIVE_APP_VISIBILITY_TEST=1 after wiring a real owned app and credentials.",
)
def test_live_owned_app_visibility_refresh(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    service.refresh_application(
        "reeldna-ai",
        VisibilityRefreshRequest(
            sources=["official_registry"],
            requested_by="pytest-live",
        ),
    )
    report = service.build_report("reeldna-ai")

    assert report.mcp_visibility_score >= 0
