from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload, sessionmaker

from automarketing.db_models import (
    ApplicationCapabilityRecord,
    ApplicationRecord,
    AutomationRunRecord,
    CampaignRunRecord,
    GrowthActionRecord,
    IntegrationHealthRecord,
    MetricSnapshotRecord,
    VisibilityObservationRecord,
)
from automarketing.models import (
    Application,
    ApplicationCapability,
    ApplicationSummary,
    AutomationRun,
    CampaignRun,
    GrowthActionExecution,
    GrowthActionPreview,
    GrowthActionRequest,
    IntegrationHealth,
    MetricSnapshot,
    VisibilityObservation,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SqlAlchemyPortfolioRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def seed_demo_data(self) -> None:
        with self._session_factory() as session:
            existing = session.scalar(select(ApplicationRecord.id).limit(1))
            if existing is not None:
                return

            now = utc_now()
            yesterday = (now - timedelta(days=1)).date()
            two_days_ago = (now - timedelta(days=2)).date()

            reeldna = ApplicationRecord(
                slug="reeldna-ai",
                name="ReelDNA AI",
                owner="Growth",
                description="Recipe and process intelligence assistant for pilot manufacturing data.",
                categories=["analytics", "ai", "b2b"],
                monetization_models=["subscription", "pilot-contracts"],
                status="active",
                mcp_endpoint="https://reeldna.example.com/mcp",
                capabilities=[
                    ApplicationCapabilityRecord(
                        capability="email_campaigns",
                        action_family="email_campaign.send",
                        channel="email",
                    ),
                    ApplicationCapabilityRecord(
                        capability="seo_refresh",
                        action_family="seo_metadata.refresh",
                        channel="web",
                    ),
                ],
                snapshots=[
                    MetricSnapshotRecord(
                        snapshot_date=two_days_ago,
                        users_active=118,
                        revenue_eur=1490.0,
                        conversions=9,
                        health_score=92,
                        web_visibility_score=61,
                        mcp_visibility_score=48,
                        recorded_at=now - timedelta(days=2),
                    ),
                    MetricSnapshotRecord(
                        snapshot_date=yesterday,
                        users_active=124,
                        revenue_eur=1610.0,
                        conversions=11,
                        health_score=95,
                        web_visibility_score=65,
                        mcp_visibility_score=54,
                        recorded_at=now - timedelta(days=1),
                    ),
                ],
                campaigns=[
                    CampaignRunRecord(
                        id="cmp-reeldna-001",
                        channel="email",
                        status="running",
                        budget_eur=120.0,
                        goal="Increase pilot signups from manufacturing leads",
                        launched_at=now - timedelta(hours=20),
                        summary="Pilot nurture sequence for warm prospects.",
                    )
                ],
                automations=[
                    AutomationRunRecord(
                        id="auto-reeldna-001",
                        automation_name="daily-snapshot-ingestion",
                        status="completed",
                        triggered_at=now - timedelta(hours=6),
                    )
                ],
                visibility_observations=[
                    VisibilityObservationRecord(
                        query="recipe advisor mcp",
                        surface="mcp",
                        position=3,
                        observed_url="https://reeldna.example.com/mcp",
                        observed_at=now - timedelta(hours=8),
                    ),
                    VisibilityObservationRecord(
                        query="recipe advisor manufacturing ai",
                        surface="web",
                        position=8,
                        observed_url="https://reeldna.example.com/",
                        observed_at=now - timedelta(hours=9),
                    ),
                ],
                integration_health=IntegrationHealthRecord(
                    status="healthy",
                    latency_ms=142,
                    last_success_at=now - timedelta(minutes=12),
                    auth_state="verified",
                    summary="Snapshot and campaign endpoints responding normally.",
                ),
            )

            waterapp = ApplicationRecord(
                slug="waterapp",
                name="WaterApp",
                owner="Product",
                description="Operational dashboard for water process monitoring and reporting.",
                categories=["operations", "saas"],
                monetization_models=["subscription"],
                status="active",
                mcp_endpoint="https://waterapp.example.com/mcp",
                capabilities=[
                    ApplicationCapabilityRecord(
                        capability="press_outreach",
                        action_family="press_pitch.publish",
                        channel="press",
                    ),
                    ApplicationCapabilityRecord(
                        capability="promotions",
                        action_family="promotion.set",
                        channel="web",
                    ),
                ],
                snapshots=[
                    MetricSnapshotRecord(
                        snapshot_date=two_days_ago,
                        users_active=76,
                        revenue_eur=880.0,
                        conversions=5,
                        health_score=89,
                        web_visibility_score=52,
                        mcp_visibility_score=36,
                        recorded_at=now - timedelta(days=2),
                    ),
                    MetricSnapshotRecord(
                        snapshot_date=yesterday,
                        users_active=81,
                        revenue_eur=920.0,
                        conversions=6,
                        health_score=90,
                        web_visibility_score=55,
                        mcp_visibility_score=39,
                        recorded_at=now - timedelta(days=1),
                    ),
                ],
                campaigns=[
                    CampaignRunRecord(
                        id="cmp-waterapp-001",
                        channel="press",
                        status="planned",
                        budget_eur=80.0,
                        goal="Secure niche trade-media mentions for new reporting module",
                        launched_at=now - timedelta(hours=30),
                        summary="Targeted outreach to water industry outlets.",
                    )
                ],
                automations=[
                    AutomationRunRecord(
                        id="auto-waterapp-001",
                        automation_name="visibility-refresh",
                        status="completed",
                        triggered_at=now - timedelta(hours=4),
                    )
                ],
                visibility_observations=[
                    VisibilityObservationRecord(
                        query="water reporting dashboard",
                        surface="web",
                        position=11,
                        observed_url="https://waterapp.example.com/",
                        observed_at=now - timedelta(hours=7),
                    ),
                    VisibilityObservationRecord(
                        query="water process monitoring mcp",
                        surface="mcp",
                        position=5,
                        observed_url="https://waterapp.example.com/mcp",
                        observed_at=now - timedelta(hours=5),
                    ),
                ],
                integration_health=IntegrationHealthRecord(
                    status="healthy",
                    latency_ms=198,
                    last_success_at=now - timedelta(minutes=16),
                    auth_state="verified",
                    summary="Visibility and press capabilities available.",
                ),
            )

            session.add_all([reeldna, waterapp])
            session.commit()

    def list_applications(self) -> list[Application]:
        with self._session_factory() as session:
            records = session.scalars(
                select(ApplicationRecord)
                .options(joinedload(ApplicationRecord.capabilities))
                .order_by(ApplicationRecord.slug)
            ).unique()
            return [self._to_application(record) for record in records]

    def get_application(self, app_slug: str) -> Application:
        with self._session_factory() as session:
            record = self._get_application_record(session, app_slug)
            return self._to_application(record)

    def list_snapshots(self, app_slug: str) -> list[MetricSnapshot]:
        with self._session_factory() as session:
            app = self._get_application_record(session, app_slug)
            records = session.scalars(
                select(MetricSnapshotRecord)
                .where(MetricSnapshotRecord.application_id == app.id)
                .order_by(MetricSnapshotRecord.snapshot_date)
            )
            return [self._to_snapshot(record) for record in records]

    def list_campaign_runs(self, app_slug: str) -> list[CampaignRun]:
        with self._session_factory() as session:
            app = self._get_application_record(session, app_slug)
            records = session.scalars(
                select(CampaignRunRecord)
                .where(CampaignRunRecord.application_id == app.id)
                .order_by(CampaignRunRecord.launched_at.desc())
            )
            return [self._to_campaign(record, app.slug) for record in records]

    def list_automation_runs(self, app_slug: str) -> list[AutomationRun]:
        with self._session_factory() as session:
            app = self._get_application_record(session, app_slug)
            records = session.scalars(
                select(AutomationRunRecord)
                .where(AutomationRunRecord.application_id == app.id)
                .order_by(AutomationRunRecord.triggered_at)
            )
            return [self._to_automation(record, app.slug) for record in records]

    def list_visibility(self, app_slug: str) -> list[VisibilityObservation]:
        with self._session_factory() as session:
            app = self._get_application_record(session, app_slug)
            records = session.scalars(
                select(VisibilityObservationRecord)
                .where(VisibilityObservationRecord.application_id == app.id)
                .order_by(VisibilityObservationRecord.observed_at.desc())
            )
            return [self._to_visibility(record) for record in records]

    def get_integration_health(self, app_slug: str) -> IntegrationHealth:
        with self._session_factory() as session:
            app = self._get_application_record(session, app_slug)
            record = session.scalar(
                select(IntegrationHealthRecord).where(
                    IntegrationHealthRecord.application_id == app.id
                )
            )
            if record is None:
                raise KeyError(app_slug)
            return self._to_integration_health(record, app.slug)

    def build_summary(self, app_slug: str) -> ApplicationSummary:
        snapshots = self.list_snapshots(app_slug)
        automations = self.list_automation_runs(app_slug)
        latest_visibility = self.list_visibility(app_slug)[:3]
        return ApplicationSummary(
            application=self.get_application(app_slug),
            latest_snapshot=snapshots[-1],
            active_campaigns=self.list_campaign_runs(app_slug),
            latest_automation=automations[-1] if automations else None,
            latest_visibility=list(reversed(latest_visibility)),
            integration_health=self.get_integration_health(app_slug),
        )

    def list_summaries(self) -> list[ApplicationSummary]:
        return [self.build_summary(app.slug) for app in self.list_applications()]

    def sync_snapshot(self, app_slug: str, reason: str, requested_by: str) -> MetricSnapshot:
        with self._session_factory() as session:
            app = self._get_application_record(session, app_slug)
            latest = session.scalar(
                select(MetricSnapshotRecord)
                .where(MetricSnapshotRecord.application_id == app.id)
                .order_by(MetricSnapshotRecord.snapshot_date.desc(), MetricSnapshotRecord.id.desc())
            )
            if latest is None:
                raise KeyError(app_slug)

            snapshot = MetricSnapshotRecord(
                application_id=app.id,
                snapshot_date=utc_now().date(),
                users_active=latest.users_active + 3,
                revenue_eur=round(latest.revenue_eur + 45.0, 2),
                conversions=latest.conversions + 1,
                health_score=min(latest.health_score + 1, 100),
                web_visibility_score=min(latest.web_visibility_score + 2, 100),
                mcp_visibility_score=min(latest.mcp_visibility_score + 1, 100),
                recorded_at=utc_now(),
            )
            session.add(snapshot)
            session.add(
                AutomationRunRecord(
                    id=f"auto-{uuid4().hex[:8]}",
                    application_id=app.id,
                    automation_name="on-demand-snapshot-sync",
                    status="completed",
                    triggered_at=utc_now(),
                    stop_reason=f"reason={reason};requested_by={requested_by}",
                )
            )
            session.commit()
            session.refresh(snapshot)
            return self._to_snapshot(snapshot)

    def preview_growth_action(
        self, app_slug: str, request: GrowthActionRequest
    ) -> GrowthActionPreview:
        capabilities = self.get_application(app_slug).capabilities
        has_channel = any(
            capability.channel == request.target_channel for capability in capabilities
        )
        checks = [
            f"budget <= {request.budget_limit:.2f} EUR",
            f"channel capability declared for {request.target_channel}: {has_channel}",
            f"requested by {request.requested_by}",
        ]
        risk_level = "medium" if request.budget_limit > 100 else "low"
        return GrowthActionPreview(
            app_slug=app_slug,
            action_type=request.action_type,
            target_channel=request.target_channel,
            risk_level=risk_level,
            estimated_budget_eur=request.budget_limit,
            checks=checks,
        )

    def execute_growth_action(
        self, app_slug: str, request: GrowthActionRequest
    ) -> GrowthActionExecution:
        correlation_id = f"corr-{uuid4().hex[:12]}"
        with self._session_factory() as session:
            app = self._get_application_record(session, app_slug)
            action_id = f"act-{uuid4().hex[:8]}"
            campaign_id = f"cmp-{uuid4().hex[:8]}"
            now = utc_now()

            session.add(
                GrowthActionRecord(
                    id=action_id,
                    application_id=app.id,
                    action_type=request.action_type,
                    target_channel=request.target_channel,
                    status="queued",
                    budget_limit=request.budget_limit,
                    requested_by=request.requested_by,
                    correlation_id=correlation_id,
                    created_at=now,
                )
            )
            session.add(
                CampaignRunRecord(
                    id=campaign_id,
                    application_id=app.id,
                    channel=request.target_channel,
                    status="queued",
                    budget_eur=request.budget_limit,
                    goal=request.parameters.get("goal", "Run portfolio growth action"),
                    launched_at=now,
                    summary=f"{request.action_type} requested by {request.requested_by}",
                )
            )
            session.commit()

        return GrowthActionExecution(
            app_slug=app_slug,
            action_type=request.action_type,
            target_channel=request.target_channel,
            status="queued",
            correlation_id=correlation_id,
            scheduled_for=utc_now(),
            budget_limit=request.budget_limit,
        )

    def refresh_visibility(self, app_slug: str) -> list[VisibilityObservation]:
        with self._session_factory() as session:
            app = self._get_application_record(session, app_slug)
            latest = session.scalar(
                select(VisibilityObservationRecord)
                .where(VisibilityObservationRecord.application_id == app.id)
                .order_by(VisibilityObservationRecord.observed_at.desc())
            )
            position = latest.position - 1 if latest is not None else 10
            record = VisibilityObservationRecord(
                application_id=app.id,
                query=f"{app_slug} mcp visibility",
                surface="mcp",
                position=max(position, 1),
                observed_url=app.mcp_endpoint,
                observed_at=utc_now(),
            )
            session.add(record)
            session.commit()

        return self.list_visibility(app_slug)[:3]

    def reset(self) -> None:
        with self._session_factory() as session:
            for model in (
                IntegrationHealthRecord,
                VisibilityObservationRecord,
                AutomationRunRecord,
                GrowthActionRecord,
                CampaignRunRecord,
                MetricSnapshotRecord,
                ApplicationCapabilityRecord,
                ApplicationRecord,
            ):
                session.execute(delete(model))
            session.commit()

    def _get_application_record(self, session, app_slug: str) -> ApplicationRecord:
        record = session.scalar(
            select(ApplicationRecord)
            .options(joinedload(ApplicationRecord.capabilities))
            .where(ApplicationRecord.slug == app_slug)
        )
        if record is None:
            raise KeyError(app_slug)
        return record

    @staticmethod
    def _to_application(record: ApplicationRecord) -> Application:
        return Application(
            slug=record.slug,
            name=record.name,
            owner=record.owner,
            description=record.description,
            categories=list(record.categories),
            monetization_models=list(record.monetization_models),
            status=record.status,
            mcp_endpoint=record.mcp_endpoint,
            capabilities=[
                ApplicationCapability(
                    capability=item.capability,
                    action_family=item.action_family,
                    channel=item.channel,
                )
                for item in record.capabilities
            ],
        )

    @staticmethod
    def _to_snapshot(record: MetricSnapshotRecord) -> MetricSnapshot:
        return MetricSnapshot(
            snapshot_date=record.snapshot_date,
            users_active=record.users_active,
            revenue_eur=record.revenue_eur,
            conversions=record.conversions,
            health_score=record.health_score,
            web_visibility_score=record.web_visibility_score,
            mcp_visibility_score=record.mcp_visibility_score,
            recorded_at=record.recorded_at,
        )

    @staticmethod
    def _to_campaign(record: CampaignRunRecord, app_slug: str) -> CampaignRun:
        return CampaignRun(
            id=record.id,
            app_slug=app_slug,
            channel=record.channel,
            status=record.status,
            budget_eur=record.budget_eur,
            goal=record.goal,
            launched_at=record.launched_at,
            summary=record.summary,
        )

    @staticmethod
    def _to_automation(record: AutomationRunRecord, app_slug: str) -> AutomationRun:
        return AutomationRun(
            id=record.id,
            app_slug=app_slug,
            automation_name=record.automation_name,
            status=record.status,
            triggered_at=record.triggered_at,
            stop_reason=record.stop_reason,
        )

    @staticmethod
    def _to_visibility(record: VisibilityObservationRecord) -> VisibilityObservation:
        return VisibilityObservation(
            query=record.query,
            surface=record.surface,
            position=record.position,
            observed_url=record.observed_url,
            observed_at=record.observed_at,
        )

    @staticmethod
    def _to_integration_health(
        record: IntegrationHealthRecord, app_slug: str
    ) -> IntegrationHealth:
        return IntegrationHealth(
            app_slug=app_slug,
            status=record.status,
            latency_ms=record.latency_ms,
            last_success_at=record.last_success_at,
            auth_state=record.auth_state,
            summary=record.summary,
        )

