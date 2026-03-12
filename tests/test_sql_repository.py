from pathlib import Path

from automarketing.db import create_engine_from_url, create_session_factory, initialize_database
from automarketing.models import ApplicationCapability, ApplicationOnboardingRequest, GrowthActionRequest
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
