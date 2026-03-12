from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from automarketing.db_models import Base, SCHEMA_TOKEN

SCHEMA_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite")


def effective_database_schema(database_url: str, schema: str | None) -> str | None:
    if is_sqlite_url(database_url):
        return None
    if not schema:
        return None
    if not SCHEMA_NAME_RE.match(schema):
        raise ValueError(f"Invalid database schema name: {schema}")
    return schema


def create_engine_from_url(
    database_url: str, echo: bool = False, schema: str | None = None
) -> Engine:
    connect_args: dict[str, object] = {}
    if is_sqlite_url(database_url):
        connect_args["check_same_thread"] = False

    engine = create_engine(database_url, echo=echo, future=True, connect_args=connect_args)
    return engine.execution_options(
        schema_translate_map={SCHEMA_TOKEN: effective_database_schema(database_url, schema)}
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def initialize_database(engine: Engine, schema: str | None = None) -> None:
    if schema:
        with engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
            Base.metadata.create_all(bind=connection)
        return

    Base.metadata.create_all(bind=engine)


def sqlite_path(database_url: str) -> Path | None:
    prefix = "sqlite+pysqlite:///"
    if database_url.startswith(prefix):
        return Path(database_url.removeprefix(prefix))
    return None
