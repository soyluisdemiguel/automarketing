"""Initial control-plane schema.

Revision ID: 20260312_0001
Revises:
Create Date: 2026-03-12 13:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260312_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("owner", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("categories", sa.JSON(), nullable=False),
        sa.Column("monetization_models", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("mcp_endpoint", sa.String(length=500), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_applications_slug", "applications", ["slug"], unique=False)

    op.create_table(
        "application_capabilities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("capability", sa.String(length=120), nullable=False),
        sa.Column("action_family", sa.String(length=120), nullable=False),
        sa.Column("channel", sa.String(length=64), nullable=False),
    )

    op.create_table(
        "metric_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("users_active", sa.Integer(), nullable=False),
        sa.Column("revenue_eur", sa.Float(), nullable=False),
        sa.Column("conversions", sa.Integer(), nullable=False),
        sa.Column("health_score", sa.Integer(), nullable=False),
        sa.Column("web_visibility_score", sa.Integer(), nullable=False),
        sa.Column("mcp_visibility_score", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_metric_snapshots_application_id", "metric_snapshots", ["application_id"], unique=False)
    op.create_index("ix_metric_snapshots_snapshot_date", "metric_snapshots", ["snapshot_date"], unique=False)

    op.create_table(
        "campaign_runs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("channel", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("budget_eur", sa.Float(), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("launched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
    )
    op.create_index("ix_campaign_runs_application_id", "campaign_runs", ["application_id"], unique=False)

    op.create_table(
        "growth_actions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("action_type", sa.String(length=120), nullable=False),
        sa.Column("target_channel", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("budget_limit", sa.Float(), nullable=False),
        sa.Column("requested_by", sa.String(length=120), nullable=False),
        sa.Column("correlation_id", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("correlation_id"),
    )
    op.create_index("ix_growth_actions_application_id", "growth_actions", ["application_id"], unique=False)

    op.create_table(
        "automation_runs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("automation_name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("stop_reason", sa.Text(), nullable=True),
    )
    op.create_index("ix_automation_runs_application_id", "automation_runs", ["application_id"], unique=False)

    op.create_table(
        "visibility_observations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("query", sa.String(length=255), nullable=False),
        sa.Column("surface", sa.String(length=64), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("observed_url", sa.String(length=500), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_visibility_observations_application_id",
        "visibility_observations",
        ["application_id"],
        unique=False,
    )

    op.create_table(
        "integration_health",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("auth_state", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.UniqueConstraint("application_id"),
    )
    op.create_index("ix_integration_health_application_id", "integration_health", ["application_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_integration_health_application_id", table_name="integration_health")
    op.drop_table("integration_health")
    op.drop_index("ix_visibility_observations_application_id", table_name="visibility_observations")
    op.drop_table("visibility_observations")
    op.drop_index("ix_automation_runs_application_id", table_name="automation_runs")
    op.drop_table("automation_runs")
    op.drop_index("ix_growth_actions_application_id", table_name="growth_actions")
    op.drop_table("growth_actions")
    op.drop_index("ix_campaign_runs_application_id", table_name="campaign_runs")
    op.drop_table("campaign_runs")
    op.drop_index("ix_metric_snapshots_snapshot_date", table_name="metric_snapshots")
    op.drop_index("ix_metric_snapshots_application_id", table_name="metric_snapshots")
    op.drop_table("metric_snapshots")
    op.drop_table("application_capabilities")
    op.drop_index("ix_applications_slug", table_name="applications")
    op.drop_table("applications")

