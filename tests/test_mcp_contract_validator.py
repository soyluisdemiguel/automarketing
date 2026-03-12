from __future__ import annotations

from contextlib import asynccontextmanager
from types import SimpleNamespace

import anyio

from automarketing import mcp_contract_validator


class DummyAsyncClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


class FakeClientSession:
    def __init__(
        self,
        _read_stream,
        _write_stream,
        *,
        resources: list[str],
        resource_templates: list[str],
        tools: dict[str, set[str]],
    ) -> None:
        self._resources = resources
        self._resource_templates = resource_templates
        self._tools = tools

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def initialize(self):
        return SimpleNamespace(
            serverInfo=SimpleNamespace(name="portfolio-app"),
            protocolVersion="2025-06-18",
        )

    async def list_resources(self):
        return SimpleNamespace(
            resources=[SimpleNamespace(uri=uri) for uri in self._resources]
        )

    async def list_resource_templates(self):
        return SimpleNamespace(
            resourceTemplates=[
                SimpleNamespace(uriTemplate=uri_template)
                for uri_template in self._resource_templates
            ]
        )

    async def list_tools(self):
        return SimpleNamespace(
            tools=[
                SimpleNamespace(name=name, inputSchema={"required": sorted(required)})
                for name, required in self._tools.items()
            ]
        )

    async def read_resource(self, _uri: str):
        return {"ok": True}


def install_fake_client(monkeypatch, *, missing_tool: str | None = None) -> None:
    resources = [
        "app://manifest",
        "app://health",
        "app://metrics/current",
        "app://campaigns/active",
        "app://visibility/current",
        "app://integrations",
    ]
    resource_templates = [
        "app://metrics/snapshots/{date}",
        "app://metrics/range/{start}/{end}",
    ]
    tools = {
        "sync_snapshot": {"reason", "requested_by"},
        "preview_growth_action": {
            "action_type",
            "target_channel",
            "parameters",
            "budget_limit",
        },
        "execute_growth_action": {
            "action_type",
            "target_channel",
            "parameters",
            "budget_limit",
            "idempotency_key",
            "requested_by",
        },
        "pause_growth_action": {"target_id", "reason", "requested_by"},
        "resume_growth_action": {"target_id", "requested_by"},
        "list_budget_policies": {"scope"},
    }
    if missing_tool is not None:
        tools.pop(missing_tool)

    @asynccontextmanager
    async def fake_streamable_http_client(_url: str, *, http_client=None):
        yield object(), object(), lambda: None

    def fake_client_session(read_stream, write_stream):
        return FakeClientSession(
            read_stream,
            write_stream,
            resources=resources,
            resource_templates=resource_templates,
            tools=tools,
        )

    monkeypatch.setattr(
        mcp_contract_validator, "streamable_http_client", fake_streamable_http_client
    )
    monkeypatch.setattr(mcp_contract_validator, "ClientSession", fake_client_session)


def test_validator_accepts_compliant_server(monkeypatch) -> None:
    install_fake_client(monkeypatch)
    report = anyio.run(
        lambda: mcp_contract_validator.validate_mcp_contract(
            "http://testserver/mcp",
            httpx_client_factory=lambda **_: DummyAsyncClient(),
        )
    )

    assert report.ok is True
    assert report.missing_tools == []
    assert report.missing_resources == []


def test_validator_flags_missing_tool(monkeypatch) -> None:
    install_fake_client(monkeypatch, missing_tool="list_budget_policies")
    report = anyio.run(
        lambda: mcp_contract_validator.validate_mcp_contract(
            "http://testserver/mcp",
            httpx_client_factory=lambda **_: DummyAsyncClient(),
        )
    )

    assert report.ok is False
    assert "list_budget_policies" in report.missing_tools
