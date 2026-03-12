from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect

from automarketing.db import create_engine_from_url, create_session_factory, initialize_database
from automarketing.mcp_contract_validator import validate_mcp_contract
from automarketing.mcp_server import build_mcp_server
from automarketing.models import (
    ContractValidationRequest,
    GrowthActionRequest,
    SyncRequest,
)
from automarketing.settings import get_settings
from automarketing.sql_repository import SqlAlchemyPortfolioRepository

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def create_app(repository: Any | None = None) -> FastAPI:
    settings = get_settings()
    repo = repository
    if repo is None:
        engine = create_engine_from_url(settings.database_url, echo=settings.database_echo)
        if settings.bootstrap_schema:
            initialize_database(engine)
        repo = SqlAlchemyPortfolioRepository(create_session_factory(engine))
        if settings.seed_demo_data and inspect(engine).has_table("applications"):
            repo.seed_demo_data()

    app = FastAPI(title=settings.app_name)
    app.state.repository = repo

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "automarketing-control-plane"}

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return TEMPLATES.TemplateResponse(
            request,
            "index.html",
            {
                "request": request,
                "summaries": repo.list_summaries(),
                "title": settings.app_name,
            },
        )

    @app.get("/applications/{app_slug}", response_class=HTMLResponse)
    async def application_detail(request: Request, app_slug: str) -> HTMLResponse:
        try:
            summary = repo.build_summary(app_slug)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Application not found") from exc

        return TEMPLATES.TemplateResponse(
            request,
            "application_detail.html",
            {"request": request, "summary": summary},
        )

    @app.get("/api/applications")
    async def api_list_applications() -> dict[str, object]:
        return {
            "applications": [
                summary.model_dump(mode="json") for summary in repo.list_summaries()
            ]
        }

    @app.get("/api/applications/{app_slug}")
    async def api_get_application(app_slug: str) -> dict[str, object]:
        try:
            return repo.build_summary(app_slug).model_dump(mode="json")
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Application not found") from exc

    @app.get("/api/applications/{app_slug}/snapshots")
    async def api_list_snapshots(app_slug: str) -> dict[str, object]:
        try:
            snapshots = repo.list_snapshots(app_slug)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Application not found") from exc
        return {
            "app_slug": app_slug,
            "snapshots": [snapshot.model_dump(mode="json") for snapshot in snapshots],
        }

    @app.post("/api/applications/{app_slug}/sync")
    async def api_sync_snapshot(app_slug: str, payload: SyncRequest) -> dict[str, object]:
        try:
            snapshot = repo.sync_snapshot(app_slug, payload.reason, payload.requested_by)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Application not found") from exc
        return snapshot.model_dump(mode="json")

    @app.post("/api/applications/{app_slug}/actions/preview")
    async def api_preview_action(
        app_slug: str, payload: GrowthActionRequest
    ) -> dict[str, object]:
        try:
            preview = repo.preview_growth_action(app_slug, payload)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Application not found") from exc
        return preview.model_dump(mode="json")

    @app.post("/api/applications/{app_slug}/actions/execute")
    async def api_execute_action(
        app_slug: str, payload: GrowthActionRequest
    ) -> dict[str, object]:
        try:
            execution = repo.execute_growth_action(app_slug, payload)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Application not found") from exc
        return execution.model_dump(mode="json")

    @app.post("/api/onboarding/validate-contract")
    async def api_validate_contract(
        payload: ContractValidationRequest,
    ) -> dict[str, object]:
        report = await validate_mcp_contract(
            payload.endpoint_url,
            headers=payload.headers or None,
        )
        return report.to_dict()

    app.mount("/mcp", build_mcp_server(repo).streamable_http_app())

    return app
