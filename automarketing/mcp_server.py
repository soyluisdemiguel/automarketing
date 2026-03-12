from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from automarketing.models import GrowthActionRequest
from automarketing.repository import PortfolioRepository


def build_mcp_server(repository: PortfolioRepository) -> FastMCP:
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
    async def refresh_visibility_observations(app_slug: str) -> dict[str, object]:
        observations = repository.refresh_visibility(app_slug)
        return {
            "app_slug": app_slug,
            "observations": [item.model_dump(mode="json") for item in observations],
        }

    return mcp

