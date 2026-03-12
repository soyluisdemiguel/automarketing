#!/usr/bin/env python3

from __future__ import annotations

import argparse

from automarketing.db import create_engine_from_url, create_session_factory, initialize_database
from automarketing.settings import get_settings
from automarketing.sql_repository import SqlAlchemyPortfolioRepository


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seed the configured database with demo automarketing data."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing portfolio data before seeding.",
    )
    parser.add_argument(
        "--bootstrap-schema",
        action="store_true",
        help="Create tables directly before seeding. Prefer Alembic for normal flows.",
    )
    args = parser.parse_args()

    settings = get_settings()
    engine = create_engine_from_url(settings.database_url, echo=settings.database_echo)

    if args.bootstrap_schema:
        initialize_database(engine)

    repository = SqlAlchemyPortfolioRepository(create_session_factory(engine))
    if args.reset:
        repository.reset()

    repository.seed_demo_data()
    print(f"Seeded demo data into {settings.database_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
