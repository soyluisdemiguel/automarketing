"""Add visibility intelligence schema.

Revision ID: 20260312_0002
Revises: 20260312_0001
Create Date: 2026-03-12 22:30:00
"""

from __future__ import annotations

import os
import re

from alembic import op
import sqlalchemy as sa


revision = "20260312_0002"
down_revision = "20260312_0001"
branch_labels = None
depends_on = None

SCHEMA_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _schema_name() -> str | None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return None

    schema = os.getenv("AUTOMARKETING_DATABASE_SCHEMA", "automarketing")
    if not SCHEMA_NAME_RE.match(schema):
        raise ValueError(f"Invalid database schema name: {schema}")
    return schema


def upgrade() -> None:
    schema = _schema_name()
    fk_prefix = f"{schema}." if schema else ""
    is_sqlite = op.get_bind().dialect.name == "sqlite"

    op.add_column(
        "applications",
        sa.Column("website_url", sa.String(length=500), nullable=True),
        schema=schema,
    )
    op.add_column(
        "applications",
        sa.Column("primary_language", sa.String(length=16), nullable=True),
        schema=schema,
    )
    op.add_column(
        "applications",
        sa.Column("primary_country", sa.String(length=16), nullable=True),
        schema=schema,
    )
    op.add_column(
        "applications",
        sa.Column("search_console_property", sa.String(length=255), nullable=True),
        schema=schema,
    )
    op.add_column(
        "applications",
        sa.Column(
            "brand_terms",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        schema=schema,
    )

    op.create_table(
        "tracked_queries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "application_id",
            sa.Integer(),
            sa.ForeignKey(f"{fk_prefix}applications.id"),
            nullable=False,
        ),
        sa.Column("query", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("country", sa.String(length=16), nullable=False),
        sa.Column("surface", sa.String(length=64), nullable=False),
        sa.Column("query_kind", sa.String(length=64), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema=schema,
    )
    op.create_index(
        "ix_tracked_queries_application_id",
        "tracked_queries",
        ["application_id"],
        unique=False,
        schema=schema,
    )

    op.create_table(
        "visibility_collection_runs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("requested_by", sa.String(length=120), nullable=False),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("raw_cursor", sa.Text(), nullable=True),
        schema=schema,
    )

    op.create_table(
        "benchmark_targets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        sa.Column("remote_url", sa.String(length=500), nullable=True),
        sa.Column("repository_url", sa.String(length=500), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("external_id"),
        schema=schema,
    )
    op.create_index(
        "ix_benchmark_targets_external_id",
        "benchmark_targets",
        ["external_id"],
        unique=False,
        schema=schema,
    )

    op.add_column(
        "visibility_observations",
        sa.Column(
            "source",
            sa.String(length=64),
            nullable=False,
            server_default="manual",
        ),
        schema=schema,
    )
    op.add_column(
        "visibility_observations",
        sa.Column("query_language", sa.String(length=16), nullable=True),
        schema=schema,
    )
    op.add_column(
        "visibility_observations",
        sa.Column("query_country", sa.String(length=16), nullable=True),
        schema=schema,
    )
    op.add_column(
        "visibility_observations",
        sa.Column("result_title", sa.String(length=255), nullable=True),
        schema=schema,
    )
    op.add_column(
        "visibility_observations",
        sa.Column("result_snippet", sa.Text(), nullable=True),
        schema=schema,
    )
    op.add_column(
        "visibility_observations",
        sa.Column("result_type", sa.String(length=64), nullable=True),
        schema=schema,
    )
    op.add_column(
        "visibility_observations",
        sa.Column(
            "is_owned_result",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        schema=schema,
    )
    if is_sqlite:
        op.add_column(
            "visibility_observations",
            sa.Column("collection_run_id", sa.String(length=64), nullable=True),
            schema=schema,
        )
    else:
        op.add_column(
            "visibility_observations",
            sa.Column(
                "collection_run_id",
                sa.String(length=64),
                sa.ForeignKey(f"{fk_prefix}visibility_collection_runs.id"),
                nullable=True,
            ),
            schema=schema,
        )
    op.create_index(
        "ix_visibility_observations_collection_run_id",
        "visibility_observations",
        ["collection_run_id"],
        unique=False,
        schema=schema,
    )

    op.create_table(
        "benchmark_observations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "benchmark_target_id",
            sa.Integer(),
            sa.ForeignKey(f"{fk_prefix}benchmark_targets.id"),
            nullable=False,
        ),
        sa.Column("query", sa.String(length=255), nullable=False),
        sa.Column("surface", sa.String(length=64), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("observed_url", sa.String(length=500), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("query_language", sa.String(length=16), nullable=True),
        sa.Column("query_country", sa.String(length=16), nullable=True),
        sa.Column("result_title", sa.String(length=255), nullable=True),
        sa.Column("result_snippet", sa.Text(), nullable=True),
        sa.Column("result_type", sa.String(length=64), nullable=True),
        sa.Column(
            "collection_run_id",
            sa.String(length=64),
            sa.ForeignKey(f"{fk_prefix}visibility_collection_runs.id"),
            nullable=True,
        ),
        schema=schema,
    )
    op.create_index(
        "ix_benchmark_observations_benchmark_target_id",
        "benchmark_observations",
        ["benchmark_target_id"],
        unique=False,
        schema=schema,
    )
    op.create_index(
        "ix_benchmark_observations_collection_run_id",
        "benchmark_observations",
        ["collection_run_id"],
        unique=False,
        schema=schema,
    )


def downgrade() -> None:
    schema = _schema_name()

    op.drop_index(
        "ix_benchmark_observations_collection_run_id",
        table_name="benchmark_observations",
        schema=schema,
    )
    op.drop_index(
        "ix_benchmark_observations_benchmark_target_id",
        table_name="benchmark_observations",
        schema=schema,
    )
    op.drop_table("benchmark_observations", schema=schema)
    op.drop_index(
        "ix_visibility_observations_collection_run_id",
        table_name="visibility_observations",
        schema=schema,
    )
    op.drop_column("visibility_observations", "collection_run_id", schema=schema)
    op.drop_column("visibility_observations", "is_owned_result", schema=schema)
    op.drop_column("visibility_observations", "result_type", schema=schema)
    op.drop_column("visibility_observations", "result_snippet", schema=schema)
    op.drop_column("visibility_observations", "result_title", schema=schema)
    op.drop_column("visibility_observations", "query_country", schema=schema)
    op.drop_column("visibility_observations", "query_language", schema=schema)
    op.drop_column("visibility_observations", "source", schema=schema)
    op.drop_index(
        "ix_benchmark_targets_external_id",
        table_name="benchmark_targets",
        schema=schema,
    )
    op.drop_table("benchmark_targets", schema=schema)
    op.drop_table("visibility_collection_runs", schema=schema)
    op.drop_index(
        "ix_tracked_queries_application_id",
        table_name="tracked_queries",
        schema=schema,
    )
    op.drop_table("tracked_queries", schema=schema)
    op.drop_column("applications", "brand_terms", schema=schema)
    op.drop_column("applications", "search_console_property", schema=schema)
    op.drop_column("applications", "primary_country", schema=schema)
    op.drop_column("applications", "primary_language", schema=schema)
    op.drop_column("applications", "website_url", schema=schema)
