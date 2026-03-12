from pathlib import Path
from datetime import datetime, timezone

from automarketing.db import create_engine_from_url, create_session_factory, initialize_database
from automarketing.models import (
    ApplicationCapability,
    ApplicationOnboardingRequest,
    BenchmarkTarget,
    GrowthActionRequest,
    VisibilityConfigRequest,
)
from automarketing.sql_repository import SqlAlchemyPortfolioRepository


def build_repository(tmp_path: Path) -> SqlAlchemyPortfolioRepository:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'repository.db'}"
    engine = create_engine_from_url(database_url)
    initialize_database(engine)
    repository = SqlAlchemyPortfolioRepository(create_session_factory(engine))
    repository.seed_demo_data()
    return repository


def test_list_summaries_reads_seeded_data(tmp_path: Path) -> None:
    repository = build_repository(tmp_path)
    summaries = repository.list_summaries()

    assert len(summaries) == 2
    assert summaries[0].application.slug in {"reeldna-ai", "waterapp"}


def test_execute_growth_action_persists_campaign(tmp_path: Path) -> None:
    repository = build_repository(tmp_path)
    before = repository.list_campaign_runs("reeldna-ai")
    repository.execute_growth_action(
        "reeldna-ai",
        request=GrowthActionRequest(
            action_type="email_campaign.send",
            target_channel="email",
            budget_limit=50.0,
            requested_by="pytest",
            parameters={"goal": "Increase trials"},
        ),
    )
    after = repository.list_campaign_runs("reeldna-ai")

    assert len(after) == len(before) + 1


def test_register_application_creates_bootstrap_summary(tmp_path: Path) -> None:
    repository = build_repository(tmp_path)
    summary = repository.register_application(
        ApplicationOnboardingRequest(
            slug="pilot-app",
            name="Pilot App",
            owner="owner@example.com",
            description="Pilot app for onboarding.",
            categories=["b2b"],
            monetization_models=["subscription"],
            mcp_endpoint="https://pilot-app.example.com/mcp",
            capabilities=[
                ApplicationCapability(
                    capability="metrics.read",
                    action_family="metrics.latest",
                    channel="mcp",
                )
            ],
        )
    )

    assert summary.application.slug == "pilot-app"
    assert summary.integration_health.status == "pending"
    assert summary.latest_snapshot.revenue_eur == 0.0


def test_configure_visibility_tracking_persists_app_defaults_and_queries(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)

    config = repository.configure_visibility_tracking(
        "reeldna-ai",
        VisibilityConfigRequest(
            website_url="https://reeldna.example.com/",
            primary_language="es",
            primary_country="es",
            search_console_property="sc-domain:reeldna.example.com",
            brand_terms=["reeldna", "reeldna ai"],
            tracked_queries=[
                {
                    "query": "reeldna ai",
                    "language": "es",
                    "country": "es",
                    "surface": "web",
                    "query_kind": "brand",
                    "priority": 1,
                },
                {
                    "query": "reeldna ai mcp",
                    "language": "en",
                    "country": "us",
                    "surface": "mcp_registry",
                    "query_kind": "brand",
                    "priority": 2,
                },
            ],
        ),
    )

    app = repository.get_application("reeldna-ai")
    queries = repository.list_tracked_queries("reeldna-ai")

    assert config.primary_language == "es"
    assert app.search_console_property == "sc-domain:reeldna.example.com"
    assert app.brand_terms == ["reeldna", "reeldna ai"]
    assert len(queries) == 2
    assert queries[0].surface == "web"


def test_upsert_benchmark_targets_and_collection_runs(tmp_path: Path) -> None:
    repository = build_repository(tmp_path)

    targets = repository.upsert_benchmark_targets(
        [
            BenchmarkTarget(
                external_id="registry:agency.lona/trading",
                source="official_registry",
                name="agency.lona/trading",
                title="Lona Trading",
                description="Trading MCP benchmark.",
                website_url="https://lona.agency",
                remote_url="https://mcp.lona.agency/mcp",
                repository_url="https://github.com/mindsightventures/lona",
                last_seen_at=datetime.now(timezone.utc),
            )
        ]
    )
    run = repository.create_visibility_collection_run(
        source="official_registry", requested_by="pytest"
    )
    finished = repository.finish_visibility_collection_run(run.id, status="completed")

    assert len(targets) == 1
    assert targets[0].external_id == "registry:agency.lona/trading"
    assert finished.status == "completed"
    assert finished.finished_at is not None
