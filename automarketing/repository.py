from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from threading import RLock
from uuid import uuid4

from automarketing.models import (
    Application,
    ApplicationCapability,
    ApplicationOnboardingRequest,
    ApplicationSummary,
    AutomationRun,
    BenchmarkObservation,
    BenchmarkTarget,
    CampaignRun,
    GrowthActionExecution,
    GrowthActionPreview,
    GrowthActionRequest,
    IntegrationHealth,
    MetricSnapshot,
    TrackedQuery,
    VisibilityCollectionRun,
    VisibilityConfig,
    VisibilityConfigRequest,
    VisibilityObservation,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PortfolioRepository:
    """In-memory portfolio state used to stabilize product surfaces before PostgreSQL."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._applications: dict[str, Application] = {}
        self._snapshots: dict[str, list[MetricSnapshot]] = {}
        self._campaign_runs: dict[str, list[CampaignRun]] = {}
        self._automation_runs: dict[str, list[AutomationRun]] = {}
        self._visibility: dict[str, list[VisibilityObservation]] = {}
        self._integration_health: dict[str, IntegrationHealth] = {}
        self._seed()

    def _seed(self) -> None:
        now = utc_now()
        yesterday = (now - timedelta(days=1)).date()
        two_days_ago = (now - timedelta(days=2)).date()

        apps = [
            Application(
                slug="reeldna-ai",
                name="ReelDNA AI",
                owner="Growth",
                description="Recipe and process intelligence assistant for pilot manufacturing data.",
                categories=["analytics", "ai", "b2b"],
                monetization_models=["subscription", "pilot-contracts"],
                status="active",
                mcp_endpoint="https://reeldna.example.com/mcp",
                website_url="https://reeldna.example.com/",
                primary_language="en",
                primary_country="us",
                brand_terms=["reeldna", "reeldna ai"],
                capabilities=[
                    ApplicationCapability(
                        capability="email_campaigns",
                        action_family="email_campaign.send",
                        channel="email",
                    ),
                    ApplicationCapability(
                        capability="seo_refresh",
                        action_family="seo_metadata.refresh",
                        channel="web",
                    ),
                ],
            ),
            Application(
                slug="waterapp",
                name="WaterApp",
                owner="Product",
                description="Operational dashboard for water process monitoring and reporting.",
                categories=["operations", "saas"],
                monetization_models=["subscription"],
                status="active",
                mcp_endpoint="https://waterapp.example.com/mcp",
                website_url="https://waterapp.example.com/",
                primary_language="en",
                primary_country="us",
                brand_terms=["waterapp"],
                capabilities=[
                    ApplicationCapability(
                        capability="press_outreach",
                        action_family="press_pitch.publish",
                        channel="press",
                    ),
                    ApplicationCapability(
                        capability="promotions",
                        action_family="promotion.set",
                        channel="web",
                    ),
                ],
            ),
        ]

        for app in apps:
            self._applications[app.slug] = app

        self._snapshots = {
            "reeldna-ai": [
                MetricSnapshot(
                    snapshot_date=two_days_ago,
                    users_active=118,
                    revenue_eur=1490.0,
                    conversions=9,
                    health_score=92,
                    web_visibility_score=61,
                    mcp_visibility_score=48,
                    recorded_at=now - timedelta(days=2),
                ),
                MetricSnapshot(
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
            "waterapp": [
                MetricSnapshot(
                    snapshot_date=two_days_ago,
                    users_active=76,
                    revenue_eur=880.0,
                    conversions=5,
                    health_score=89,
                    web_visibility_score=52,
                    mcp_visibility_score=36,
                    recorded_at=now - timedelta(days=2),
                ),
                MetricSnapshot(
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
        }

        self._campaign_runs = {
            "reeldna-ai": [
                CampaignRun(
                    id="cmp-reeldna-001",
                    app_slug="reeldna-ai",
                    channel="email",
                    status="running",
                    budget_eur=120.0,
                    goal="Increase pilot signups from manufacturing leads",
                    launched_at=now - timedelta(hours=20),
                    summary="Pilot nurture sequence for warm prospects.",
                )
            ],
            "waterapp": [
                CampaignRun(
                    id="cmp-waterapp-001",
                    app_slug="waterapp",
                    channel="press",
                    status="planned",
                    budget_eur=80.0,
                    goal="Secure niche trade-media mentions for new reporting module",
                    launched_at=now - timedelta(hours=30),
                    summary="Targeted outreach to water industry outlets.",
                )
            ],
        }

        self._automation_runs = {
            "reeldna-ai": [
                AutomationRun(
                    id="auto-reeldna-001",
                    app_slug="reeldna-ai",
                    automation_name="daily-snapshot-ingestion",
                    status="completed",
                    triggered_at=now - timedelta(hours=6),
                )
            ],
            "waterapp": [
                AutomationRun(
                    id="auto-waterapp-001",
                    app_slug="waterapp",
                    automation_name="visibility-refresh",
                    status="completed",
                    triggered_at=now - timedelta(hours=4),
                )
            ],
        }

        self._visibility = {
            "reeldna-ai": [
                VisibilityObservation(
                    query="recipe advisor mcp",
                    surface="mcp",
                    position=3,
                    observed_url="https://reeldna.example.com/mcp",
                    observed_at=now - timedelta(hours=8),
                    source="seed",
                    query_language="en",
                    query_country="us",
                    result_title="ReelDNA AI MCP",
                    result_type="registry",
                ),
                VisibilityObservation(
                    query="recipe advisor manufacturing ai",
                    surface="web",
                    position=8,
                    observed_url="https://reeldna.example.com/",
                    observed_at=now - timedelta(hours=9),
                    source="seed",
                    query_language="en",
                    query_country="us",
                    result_title="ReelDNA AI",
                    result_type="organic",
                ),
            ],
            "waterapp": [
                VisibilityObservation(
                    query="water reporting dashboard",
                    surface="web",
                    position=11,
                    observed_url="https://waterapp.example.com/",
                    observed_at=now - timedelta(hours=7),
                    source="seed",
                    query_language="en",
                    query_country="us",
                    result_title="WaterApp",
                    result_type="organic",
                ),
                VisibilityObservation(
                    query="water process monitoring mcp",
                    surface="mcp",
                    position=5,
                    observed_url="https://waterapp.example.com/mcp",
                    observed_at=now - timedelta(hours=5),
                    source="seed",
                    query_language="en",
                    query_country="us",
                    result_title="WaterApp MCP",
                    result_type="registry",
                ),
            ],
        }

        self._tracked_queries: dict[str, list[TrackedQuery]] = {
            "reeldna-ai": [
                TrackedQuery(
                    query="reeldna ai",
                    language="en",
                    country="us",
                    surface="web",
                    query_kind="brand",
                    priority=1,
                    active=True,
                    created_at=now - timedelta(days=2),
                ),
                TrackedQuery(
                    query="reeldna ai mcp",
                    language="en",
                    country="us",
                    surface="mcp_registry",
                    query_kind="brand",
                    priority=1,
                    active=True,
                    created_at=now - timedelta(days=2),
                ),
            ],
            "waterapp": [
                TrackedQuery(
                    query="waterapp mcp",
                    language="en",
                    country="us",
                    surface="mcp_registry",
                    query_kind="brand",
                    priority=1,
                    active=True,
                    created_at=now - timedelta(days=2),
                )
            ],
        }
        self._benchmark_targets: dict[str, BenchmarkTarget] = {}
        self._collection_runs: dict[str, VisibilityCollectionRun] = {}
        self._benchmark_observations: list[BenchmarkObservation] = []

        self._integration_health = {
            "reeldna-ai": IntegrationHealth(
                app_slug="reeldna-ai",
                status="healthy",
                latency_ms=142,
                last_success_at=now - timedelta(minutes=12),
                auth_state="verified",
                summary="Snapshot and campaign endpoints responding normally.",
            ),
            "waterapp": IntegrationHealth(
                app_slug="waterapp",
                status="healthy",
                latency_ms=198,
                last_success_at=now - timedelta(minutes=16),
                auth_state="verified",
                summary="Visibility and press capabilities available.",
            ),
        }

    def list_applications(self) -> list[Application]:
        with self._lock:
            return [deepcopy(app) for app in self._applications.values()]

    def get_application(self, app_slug: str) -> Application:
        with self._lock:
            return deepcopy(self._applications[app_slug])

    def list_snapshots(self, app_slug: str) -> list[MetricSnapshot]:
        with self._lock:
            return deepcopy(self._snapshots[app_slug])

    def list_campaign_runs(self, app_slug: str) -> list[CampaignRun]:
        with self._lock:
            return deepcopy(self._campaign_runs[app_slug])

    def list_automation_runs(self, app_slug: str) -> list[AutomationRun]:
        with self._lock:
            return deepcopy(self._automation_runs[app_slug])

    def list_visibility(self, app_slug: str) -> list[VisibilityObservation]:
        with self._lock:
            return deepcopy(self._visibility[app_slug])

    def get_integration_health(self, app_slug: str) -> IntegrationHealth:
        with self._lock:
            return deepcopy(self._integration_health[app_slug])

    def build_summary(self, app_slug: str) -> ApplicationSummary:
        snapshots = self.list_snapshots(app_slug)
        automations = self.list_automation_runs(app_slug)
        return ApplicationSummary(
            application=self.get_application(app_slug),
            latest_snapshot=snapshots[-1],
            active_campaigns=self.list_campaign_runs(app_slug),
            latest_automation=automations[-1] if automations else None,
            latest_visibility=self.list_visibility(app_slug),
            integration_health=self.get_integration_health(app_slug),
        )

    def list_summaries(self) -> list[ApplicationSummary]:
        return [self.build_summary(app.slug) for app in self.list_applications()]

    def register_application(
        self, request: ApplicationOnboardingRequest
    ) -> ApplicationSummary:
        with self._lock:
            if request.slug in self._applications:
                raise ValueError(f"Application already exists: {request.slug}")
            now = utc_now()
            app = Application(
                slug=request.slug,
                name=request.name,
                owner=request.owner,
                description=request.description,
                categories=request.categories,
                monetization_models=request.monetization_models,
                status=request.status,
                mcp_endpoint=request.mcp_endpoint,
                website_url=request.website_url,
                primary_language=request.primary_language,
                primary_country=request.primary_country,
                search_console_property=request.search_console_property,
                brand_terms=list(request.brand_terms),
                capabilities=deepcopy(request.capabilities),
            )
            self._applications[request.slug] = app
            self._snapshots[request.slug] = [
                MetricSnapshot(
                    snapshot_date=now.date(),
                    users_active=0,
                    revenue_eur=0.0,
                    conversions=0,
                    health_score=0,
                    web_visibility_score=0,
                    mcp_visibility_score=0,
                    recorded_at=now,
                )
            ]
            self._campaign_runs[request.slug] = []
            self._automation_runs[request.slug] = [
                AutomationRun(
                    id=f"auto-{uuid4().hex[:8]}",
                    app_slug=request.slug,
                    automation_name="portfolio-app-onboarding",
                    status="completed",
                    triggered_at=now,
                    stop_reason="initial registration",
                )
            ]
            self._visibility[request.slug] = []
            self._tracked_queries[request.slug] = []
            self._integration_health[request.slug] = IntegrationHealth(
                app_slug=request.slug,
                status="pending",
                latency_ms=0,
                last_success_at=now,
                auth_state="not-configured",
                summary="App registered; MCP validation and first sync pending.",
            )
            return self.build_summary(request.slug)

    def configure_visibility_tracking(
        self, app_slug: str, request: VisibilityConfigRequest
    ) -> VisibilityConfig:
        with self._lock:
            app = deepcopy(self._applications[app_slug])
            app.website_url = request.website_url
            app.primary_language = request.primary_language
            app.primary_country = request.primary_country
            app.search_console_property = request.search_console_property
            app.brand_terms = list(request.brand_terms)
            self._applications[app_slug] = app
            self._tracked_queries[app_slug] = [
                TrackedQuery(
                    query=item.query,
                    language=item.language,
                    country=item.country,
                    surface=item.surface,
                    query_kind=item.query_kind,
                    priority=item.priority,
                    active=item.active,
                    created_at=utc_now(),
                )
                for item in request.tracked_queries
            ]
            return VisibilityConfig(
                website_url=app.website_url,
                primary_language=app.primary_language,
                primary_country=app.primary_country,
                search_console_property=app.search_console_property,
                brand_terms=list(app.brand_terms),
                tracked_queries=deepcopy(self._tracked_queries[app_slug]),
            )

    def list_tracked_queries(self, app_slug: str) -> list[TrackedQuery]:
        with self._lock:
            return deepcopy(self._tracked_queries[app_slug])

    def list_benchmark_targets(self) -> list[BenchmarkTarget]:
        with self._lock:
            return sorted(
                (deepcopy(item) for item in self._benchmark_targets.values()),
                key=lambda item: (item.source, item.name),
            )

    def upsert_benchmark_targets(
        self, targets: list[BenchmarkTarget]
    ) -> list[BenchmarkTarget]:
        with self._lock:
            for target in targets:
                self._benchmark_targets[target.external_id] = deepcopy(target)
            return self.list_benchmark_targets()

    def create_visibility_collection_run(
        self, source: str, requested_by: str, raw_cursor: str | None = None
    ) -> VisibilityCollectionRun:
        with self._lock:
            run = VisibilityCollectionRun(
                id=f"visrun-{uuid4().hex[:10]}",
                source=source,
                status="running",
                started_at=utc_now(),
                requested_by=requested_by,
                raw_cursor=raw_cursor,
            )
            self._collection_runs[run.id] = run
            return deepcopy(run)

    def finish_visibility_collection_run(
        self,
        run_id: str,
        status: str,
        error_summary: str | None = None,
        raw_cursor: str | None = None,
    ) -> VisibilityCollectionRun:
        with self._lock:
            run = deepcopy(self._collection_runs[run_id])
            run.status = status
            run.error_summary = error_summary
            run.raw_cursor = raw_cursor
            run.finished_at = utc_now()
            self._collection_runs[run_id] = run
            return deepcopy(run)

    def record_visibility_observations(
        self, app_slug: str, observations: list[VisibilityObservation]
    ) -> list[VisibilityObservation]:
        with self._lock:
            self._visibility.setdefault(app_slug, []).extend(deepcopy(observations))
            return self.list_visibility(app_slug)

    def record_benchmark_observations(
        self, observations: list[BenchmarkObservation]
    ) -> list[BenchmarkObservation]:
        with self._lock:
            self._benchmark_observations.extend(deepcopy(observations))
            return deepcopy(self._benchmark_observations)

    def sync_snapshot(self, app_slug: str, reason: str, requested_by: str) -> MetricSnapshot:
        with self._lock:
            latest = self._snapshots[app_slug][-1]
            next_snapshot = MetricSnapshot(
                snapshot_date=utc_now().date(),
                users_active=latest.users_active + 3,
                revenue_eur=round(latest.revenue_eur + 45.0, 2),
                conversions=latest.conversions + 1,
                health_score=min(latest.health_score + 1, 100),
                web_visibility_score=min(latest.web_visibility_score + 2, 100),
                mcp_visibility_score=min(latest.mcp_visibility_score + 1, 100),
                recorded_at=utc_now(),
            )
            self._snapshots[app_slug].append(next_snapshot)
            self._automation_runs[app_slug].append(
                AutomationRun(
                    id=f"auto-{uuid4().hex[:8]}",
                    app_slug=app_slug,
                    automation_name="on-demand-snapshot-sync",
                    status="completed",
                    triggered_at=utc_now(),
                    stop_reason=f"reason={reason};requested_by={requested_by}",
                )
            )
            return deepcopy(next_snapshot)

    def preview_growth_action(
        self, app_slug: str, request: GrowthActionRequest
    ) -> GrowthActionPreview:
        checks = [
            f"budget <= {request.budget_limit:.2f} EUR",
            f"channel capability declared for {request.target_channel}",
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
        campaign = CampaignRun(
            id=f"cmp-{uuid4().hex[:8]}",
            app_slug=app_slug,
            channel=request.target_channel,
            status="queued",
            budget_eur=request.budget_limit,
            goal=request.parameters.get("goal", "Run portfolio growth action"),
            launched_at=utc_now(),
            summary=f"{request.action_type} requested by {request.requested_by}",
        )
        with self._lock:
            self._campaign_runs[app_slug].append(campaign)
        return GrowthActionExecution(
            app_slug=app_slug,
            action_type=request.action_type,
            target_channel=request.target_channel,
            status="queued",
            correlation_id=f"corr-{uuid4().hex[:12]}",
            scheduled_for=utc_now(),
            budget_limit=request.budget_limit,
        )

    def refresh_visibility(self, app_slug: str) -> list[VisibilityObservation]:
        with self._lock:
            refreshed = VisibilityObservation(
                query=f"{app_slug} mcp visibility",
                surface="mcp",
                position=max(self._visibility[app_slug][0].position - 1, 1),
                observed_url=self._applications[app_slug].mcp_endpoint,
                observed_at=utc_now(),
            )
            self._visibility[app_slug].append(refreshed)
            return deepcopy(self._visibility[app_slug][-3:])
