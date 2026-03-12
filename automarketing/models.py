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
    capabilities: list[ApplicationCapability]
