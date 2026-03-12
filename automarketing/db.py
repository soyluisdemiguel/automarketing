from __future__ import annotations

from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from automarketing.db_models import Base


def create_engine_from_url(database_url: str, echo: bool = False) -> Engine:
    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(database_url, echo=echo, future=True, connect_args=connect_args)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def initialize_database(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)


def sqlite_path(database_url: str) -> Path | None:
    prefix = "sqlite+pysqlite:///"
    if database_url.startswith(prefix):
        return Path(database_url.removeprefix(prefix))
    return None

