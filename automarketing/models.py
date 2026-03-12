from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class ApplicationCapability(BaseModel):
    capability: str
    action_family: str
    channel: str


class Application(BaseModel):
    slug: str
    name: str
    owner: str
    description: str
    categories: list[str]
    monetization_models: list[str]
    status: str
    mcp_endpoint: str
    website_url: str | None = None
    primary_language: str | None = None
    primary_country: str | None = None
    search_console_property: str | None = None
    brand_terms: list[str] = Field(default_factory=list)
    capabilities: list[ApplicationCapability]


class MetricSnapshot(BaseModel):
    snapshot_date: date
    users_active: int
    revenue_eur: float
    conversions: int
    health_score: int
    web_visibility_score: int
    mcp_visibility_score: int
    recorded_at: datetime


class CampaignRun(BaseModel):
    id: str
    app_slug: str
    channel: str
    status: str
    budget_eur: float
    goal: str
    launched_at: datetime
    summary: str


class AutomationRun(BaseModel):
    id: str
    app_slug: str
    automation_name: str
    status: str
    triggered_at: datetime
    stop_reason: str | None = None


class VisibilityObservation(BaseModel):
    query: str
    surface: str
    position: int
    observed_url: str
    observed_at: datetime
    source: str = "manual"
    query_language: str | None = None
    query_country: str | None = None
    result_title: str | None = None
    result_snippet: str | None = None
    result_type: str | None = None
    is_owned_result: bool = True
    collection_run_id: str | None = None


class TrackedQuery(BaseModel):
    query: str
    language: str
    country: str
    surface: str
    query_kind: str
    priority: int
    active: bool
    created_at: datetime


class TrackedQueryInput(BaseModel):
    query: str
    language: str
    country: str
    surface: str
    query_kind: str
    priority: int
    active: bool = True


class VisibilityConfig(BaseModel):
    website_url: str | None = None
    primary_language: str | None = None
    primary_country: str | None = None
    search_console_property: str | None = None
    brand_terms: list[str] = Field(default_factory=list)
    tracked_queries: list[TrackedQuery] = Field(default_factory=list)


class VisibilityConfigRequest(BaseModel):
    website_url: str
    primary_language: str
    primary_country: str
    search_console_property: str | None = None
    brand_terms: list[str] = Field(default_factory=list)
    tracked_queries: list[TrackedQueryInput] = Field(default_factory=list)


class VisibilityCollectionRun(BaseModel):
    id: str
    source: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    requested_by: str
    error_summary: str | None = None
    raw_cursor: str | None = None


class BenchmarkTarget(BaseModel):
    id: int | None = None
    external_id: str
    source: str
    name: str
    title: str | None = None
    description: str | None = None
    website_url: str | None = None
    remote_url: str | None = None
    repository_url: str | None = None
    last_seen_at: datetime


class BenchmarkObservation(BaseModel):
    benchmark_external_id: str
    query: str
    surface: str
    position: int
    observed_url: str
    observed_at: datetime
    source: str
    query_language: str | None = None
    query_country: str | None = None
    result_title: str | None = None
    result_snippet: str | None = None
    result_type: str | None = None
    collection_run_id: str | None = None


class VisibilityScoreBreakdown(BaseModel):
    value: int
    active_listing: int = 0
    metadata_completeness: int = 0
    remote_reachability: int = 0
    directory_presence: int = 0
    branded_web_rank: int = 0
    branded_rank: int = 0
    task_rank: int = 0
    search_console_trend: int = 0
    indexability: int = 0


class VisibilityBenchmarkComparison(BaseModel):
    benchmark: BenchmarkTarget
    overlap_score: int
    outranks_owned_queries: list[str] = Field(default_factory=list)


class VisibilityReport(BaseModel):
    app_slug: str
    web_visibility_score: int
    mcp_visibility_score: int
    confidence: str
    web_breakdown: VisibilityScoreBreakdown
    mcp_breakdown: VisibilityScoreBreakdown
    owned_observations: list[VisibilityObservation]
    benchmark_comparison: list[VisibilityBenchmarkComparison]
    top_missed_opportunities: list[str]


class IntegrationHealth(BaseModel):
    app_slug: str
    status: str
    latency_ms: int
    last_success_at: datetime
    auth_state: str
    summary: str


class ApplicationSummary(BaseModel):
    application: Application
    latest_snapshot: MetricSnapshot
    active_campaigns: list[CampaignRun]
    latest_automation: AutomationRun | None
    latest_visibility: list[VisibilityObservation]
    integration_health: IntegrationHealth


class SyncRequest(BaseModel):
    reason: str
    requested_by: str


class GrowthActionRequest(BaseModel):
    action_type: str
    target_channel: str
    budget_limit: float
    requested_by: str
    parameters: dict[str, str] = Field(default_factory=dict)


class GrowthActionPreview(BaseModel):
    app_slug: str
    action_type: str
    target_channel: str
    risk_level: str
    estimated_budget_eur: float
    checks: list[str]


class GrowthActionExecution(BaseModel):
    app_slug: str
    action_type: str
    target_channel: str
    status: str
    correlation_id: str
    scheduled_for: datetime
    budget_limit: float


class ContractValidationRequest(BaseModel):
    endpoint_url: str
    headers: dict[str, str] = Field(default_factory=dict)


class ApplicationOnboardingRequest(BaseModel):
    slug: str
    name: str
    owner: str
    description: str
    categories: list[str]
    monetization_models: list[str]
    status: str = "onboarding"
    mcp_endpoint: str
    website_url: str | None = None
    primary_language: str | None = None
    primary_country: str | None = None
    search_console_property: str | None = None
    brand_terms: list[str] = Field(default_factory=list)
    capabilities: list[ApplicationCapability]
