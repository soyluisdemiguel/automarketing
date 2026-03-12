from automarketing.db import effective_database_schema


def test_effective_database_schema_disables_schema_for_sqlite() -> None:
    assert effective_database_schema("sqlite+pysqlite:///./test.db", "automarketing") is None


def test_effective_database_schema_keeps_schema_for_postgres() -> None:
    assert (
        effective_database_schema(
            "postgresql+psycopg://user:pass@db.example.com:5432/app", "automarketing"
        )
        == "automarketing"
    )
