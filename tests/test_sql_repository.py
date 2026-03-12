from pathlib import Path

from automarketing.db import create_engine_from_url, create_session_factory, initialize_database
from automarketing.models import GrowthActionRequest
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
