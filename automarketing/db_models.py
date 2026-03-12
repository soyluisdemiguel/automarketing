from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

SCHEMA_TOKEN = "automarketing_app"


class Base(DeclarativeBase):
    pass


class ApplicationRecord(Base):
    __tablename__ = "applications"
    __table_args__ = {"schema": SCHEMA_TOKEN}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    owner: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    categories: Mapped[list[str]] = mapped_column(JSON)
    monetization_models: Mapped[list[str]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(64))
    mcp_endpoint: Mapped[str] = mapped_column(String(500))

    capabilities: Mapped[list["ApplicationCapabilityRecord"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    snapshots: Mapped[list["MetricSnapshotRecord"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    campaigns: Mapped[list["CampaignRunRecord"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    automations: Mapped[list["AutomationRunRecord"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    visibility_observations: Mapped[list["VisibilityObservationRecord"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    growth_actions: Mapped[list["GrowthActionRecord"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    integration_health: Mapped["IntegrationHealthRecord"] = relationship(
        back_populates="application", cascade="all, delete-orphan", uselist=False
    )


class ApplicationCapabilityRecord(Base):
    __tablename__ = "application_capabilities"
    __table_args__ = {"schema": SCHEMA_TOKEN}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA_TOKEN}.applications.id"))
    capability: Mapped[str] = mapped_column(String(120))
    action_family: Mapped[str] = mapped_column(String(120))
    channel: Mapped[str] = mapped_column(String(64))

    application: Mapped[ApplicationRecord] = relationship(back_populates="capabilities")


class MetricSnapshotRecord(Base):
    __tablename__ = "metric_snapshots"
    __table_args__ = {"schema": SCHEMA_TOKEN}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA_TOKEN}.applications.id"), index=True
    )
    snapshot_date: Mapped[date] = mapped_column(Date, index=True)
    users_active: Mapped[int] = mapped_column(Integer)
    revenue_eur: Mapped[float] = mapped_column(Float)
    conversions: Mapped[int] = mapped_column(Integer)
    health_score: Mapped[int] = mapped_column(Integer)
    web_visibility_score: Mapped[int] = mapped_column(Integer)
    mcp_visibility_score: Mapped[int] = mapped_column(Integer)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    application: Mapped[ApplicationRecord] = relationship(back_populates="snapshots")


class CampaignRunRecord(Base):
    __tablename__ = "campaign_runs"
    __table_args__ = {"schema": SCHEMA_TOKEN}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA_TOKEN}.applications.id"), index=True
    )
    channel: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(64))
    budget_eur: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(Text)
    launched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str] = mapped_column(Text)

    application: Mapped[ApplicationRecord] = relationship(back_populates="campaigns")


class GrowthActionRecord(Base):
    __tablename__ = "growth_actions"
    __table_args__ = {"schema": SCHEMA_TOKEN}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA_TOKEN}.applications.id"), index=True
    )
    action_type: Mapped[str] = mapped_column(String(120))
    target_channel: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(64))
    budget_limit: Mapped[float] = mapped_column(Float)
    requested_by: Mapped[str] = mapped_column(String(120))
    correlation_id: Mapped[str] = mapped_column(String(120), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    application: Mapped[ApplicationRecord] = relationship(back_populates="growth_actions")


class AutomationRunRecord(Base):
    __tablename__ = "automation_runs"
    __table_args__ = {"schema": SCHEMA_TOKEN}

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA_TOKEN}.applications.id"), index=True
    )
    automation_name: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(64))
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    stop_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    application: Mapped[ApplicationRecord] = relationship(back_populates="automations")


class VisibilityObservationRecord(Base):
    __tablename__ = "visibility_observations"
    __table_args__ = {"schema": SCHEMA_TOKEN}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA_TOKEN}.applications.id"), index=True
    )
    query: Mapped[str] = mapped_column(String(255))
    surface: Mapped[str] = mapped_column(String(64))
    position: Mapped[int] = mapped_column(Integer)
    observed_url: Mapped[str] = mapped_column(String(500))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    application: Mapped[ApplicationRecord] = relationship(
        back_populates="visibility_observations"
    )


class IntegrationHealthRecord(Base):
    __tablename__ = "integration_health"
    __table_args__ = {"schema": SCHEMA_TOKEN}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA_TOKEN}.applications.id"), unique=True, index=True
    )
    status: Mapped[str] = mapped_column(String(64))
    latency_ms: Mapped[int] = mapped_column(Integer)
    last_success_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    auth_state: Mapped[str] = mapped_column(String(64))
    summary: Mapped[str] = mapped_column(Text)

    application: Mapped[ApplicationRecord] = relationship(
        back_populates="integration_health"
    )
