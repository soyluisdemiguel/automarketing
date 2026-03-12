from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from automarketing.mcp_contract_validator import validate_mcp_contract
from automarketing.models import GrowthActionRequest, VisibilityConfigRequest, VisibilityRefreshRequest
from automarketing.repository import PortfolioRepository


def build_mcp_server(repository: PortfolioRepository, visibility_service) -> FastMCP:
    mcp = FastMCP(
        name="automarketing-control-plane",
        instructions=(
            "Expose portfolio application state, historical snapshots, "
            "growth actions, and visibility observations for internal operators and agents."
        ),
        streamable_http_path="/",
    )

    @mcp.resource("portfolio://applications")
    async def portfolio_applications() -> dict[str, object]:
        return {
            "applications": [
                summary.model_dump(mode="json") for summary in repository.list_summaries()
            ]
        }

    @mcp.resource("portfolio://applications/{app_slug}")
    async def application_summary(app_slug: str) -> dict[str, object]:
        return repository.build_summary(app_slug).model_dump(mode="json")

    @mcp.resource("portfolio://applications/{app_slug}/snapshots")
    async def application_snapshots(app_slug: str) -> dict[str, object]:
        return {
            "app_slug": app_slug,
            "snapshots": [
                snapshot.model_dump(mode="json")
                for snapshot in repository.list_snapshots(app_slug)
            ],
        }

    @mcp.resource("portfolio://applications/{app_slug}/campaigns")
    async def application_campaigns(app_slug: str) -> dict[str, object]:
        return {
            "app_slug": app_slug,
            "campaigns": [
                campaign.model_dump(mode="json")
                for campaign in repository.list_campaign_runs(app_slug)
            ],
        }

    @mcp.resource("portfolio://applications/{app_slug}/visibility")
    async def application_visibility(app_slug: str) -> dict[str, object]:
        return {
            "app_slug": app_slug,
            "observations": [
                observation.model_dump(mode="json")
                for observation in repository.list_visibility(app_slug)
            ],
        }

    @mcp.resource("portfolio://applications/{app_slug}/visibility/report")
    async def application_visibility_report(app_slug: str) -> dict[str, object]:
        return visibility_service.build_report(app_slug).model_dump(mode="json")

    @mcp.resource("portfolio://applications/{app_slug}/visibility/queries")
    async def application_visibility_queries(app_slug: str) -> dict[str, object]:
        return {
            "app_slug": app_slug,
            "tracked_queries": [
                item.model_dump(mode="json")
                for item in repository.list_tracked_queries(app_slug)
            ],
        }

    @mcp.resource("portfolio://benchmarks")
    async def benchmark_targets() -> dict[str, object]:
        return {
            "benchmarks": [
                item.model_dump(mode="json")
                for item in visibility_service.list_benchmarks()
            ]
        }

    @mcp.resource("portfolio://applications/{app_slug}/integration-health")
    async def application_integration_health(app_slug: str) -> dict[str, object]:
        return repository.get_integration_health(app_slug).model_dump(mode="json")

    @mcp.tool(description="List all onboarded portfolio applications and their latest summaries.")
    async def list_applications() -> dict[str, object]:
        return {
            "applications": [
                summary.model_dump(mode="json") for summary in repository.list_summaries()
            ]
        }

    @mcp.tool(description="Return the current summary for one application.")
    async def get_application_summary(app_slug: str) -> dict[str, object]:
        return repository.build_summary(app_slug).model_dump(mode="json")

    @mcp.tool(description="Trigger an on-demand snapshot refresh for one application.")
    async def sync_application_snapshot(
        app_slug: str, reason: str, requested_by: str
    ) -> dict[str, object]:
        return repository.sync_snapshot(app_slug, reason, requested_by).model_dump(
            mode="json"
        )

    @mcp.tool(description="Preview a growth action and return policy checks.")
    async def plan_growth_action(
        app_slug: str,
        action_type: str,
        target_channel: str,
        budget_limit: float,
        requested_by: str,
    ) -> dict[str, object]:
        request = GrowthActionRequest(
            action_type=action_type,
            target_channel=target_channel,
            budget_limit=budget_limit,
            requested_by=requested_by,
        )
        return repository.preview_growth_action(app_slug, request).model_dump(mode="json")

    @mcp.tool(description="Queue a growth action for execution.")
    async def execute_growth_action(
        app_slug: str,
        action_type: str,
        target_channel: str,
        budget_limit: float,
        requested_by: str,
    ) -> dict[str, object]:
        request = GrowthActionRequest(
            action_type=action_type,
            target_channel=target_channel,
            budget_limit=budget_limit,
            requested_by=requested_by,
        )
        return repository.execute_growth_action(app_slug, request).model_dump(mode="json")

    @mcp.tool(description="Pause application automation. This slice returns a stubbed policy response.")
    async def pause_application_automation(app_slug: str, reason: str) -> dict[str, object]:
        return {"app_slug": app_slug, "status": "paused", "reason": reason}

    @mcp.tool(description="Resume application automation. This slice returns a stubbed policy response.")
    async def resume_application_automation(app_slug: str) -> dict[str, object]:
        return {"app_slug": app_slug, "status": "active"}

    @mcp.tool(description="Refresh visibility observations for one application.")
    async def refresh_visibility_observations(
        app_slug: str,
        requested_by: str,
        sources: list[str] | None = None,
    ) -> dict[str, object]:
        request = VisibilityRefreshRequest(
            sources=sources or ["official_registry", "serp", "search_console"],
            requested_by=requested_by,
        )
        return visibility_service.refresh_application(app_slug, request)

    @mcp.tool(description="Configure visibility tracking defaults and tracked queries for one application.")
    async def configure_visibility_tracking(
        app_slug: str,
        website_url: str,
        primary_language: str,
        primary_country: str,
        brand_terms: list[str],
        tracked_queries: list[dict[str, object]],
        search_console_property: str | None = None,
    ) -> dict[str, object]:
        request = VisibilityConfigRequest(
            website_url=website_url,
            primary_language=primary_language,
            primary_country=primary_country,
            search_console_property=search_console_property,
            brand_terms=brand_terms,
            tracked_queries=tracked_queries,
        )
        return visibility_service.configure_tracking(app_slug, request).model_dump(
            mode="json"
        )

    @mcp.tool(description="List the imported public benchmark MCP targets.")
    async def list_benchmark_targets() -> dict[str, object]:
        return {
            "benchmarks": [
                item.model_dump(mode="json")
                for item in visibility_service.list_benchmarks()
            ]
        }

    @mcp.tool(description="Validate that a portfolio application's MCP endpoint matches the documented onboarding contract.")
    async def validate_application_contract(
        endpoint_url: str,
    ) -> dict[str, object]:
        report = await validate_mcp_contract(endpoint_url)
        return report.to_dict()

    return mcp
