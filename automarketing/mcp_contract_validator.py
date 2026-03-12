from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable
from urllib.parse import urlparse, urlunparse

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.shared._httpx_utils import create_mcp_http_client

REQUIRED_RESOURCE_URIS = {
    "app://manifest",
    "app://health",
    "app://metrics/current",
    "app://campaigns/active",
    "app://visibility/current",
    "app://integrations",
}
REQUIRED_RESOURCE_TEMPLATES = {
    "app://metrics/snapshots/{date}",
    "app://metrics/range/{start}/{end}",
}
REQUIRED_TOOL_FIELDS = {
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


@dataclass
class ValidationReport:
    endpoint_url: str
    server_name: str
    protocol_version: str
    resource_uris: list[str] = field(default_factory=list)
    resource_templates: list[str] = field(default_factory=list)
    tool_names: list[str] = field(default_factory=list)
    missing_resources: list[str] = field(default_factory=list)
    missing_resource_templates: list[str] = field(default_factory=list)
    missing_tools: list[str] = field(default_factory=list)
    tool_schema_errors: dict[str, list[str]] = field(default_factory=dict)
    read_checks: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not (
            self.missing_resources
            or self.missing_resource_templates
            or self.missing_tools
            or self.tool_schema_errors
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "endpoint_url": self.endpoint_url,
            "server_name": self.server_name,
            "protocol_version": self.protocol_version,
            "ok": self.ok,
            "resource_uris": self.resource_uris,
            "resource_templates": self.resource_templates,
            "tool_names": self.tool_names,
            "missing_resources": self.missing_resources,
            "missing_resource_templates": self.missing_resource_templates,
            "missing_tools": self.missing_tools,
            "tool_schema_errors": self.tool_schema_errors,
            "read_checks": self.read_checks,
        }

    def to_text(self) -> str:
        lines = [
            f"Endpoint: {self.endpoint_url}",
            f"Server: {self.server_name}",
            f"Protocol: {self.protocol_version}",
            f"Result: {'PASS' if self.ok else 'FAIL'}",
        ]
        if self.missing_resources:
            lines.append("Missing resources: " + ", ".join(self.missing_resources))
        if self.missing_resource_templates:
            lines.append(
                "Missing resource templates: "
                + ", ".join(self.missing_resource_templates)
            )
        if self.missing_tools:
            lines.append("Missing tools: " + ", ".join(self.missing_tools))
        if self.tool_schema_errors:
            for tool_name, errors in self.tool_schema_errors.items():
                lines.append(f"Schema errors for {tool_name}: " + ", ".join(errors))
        if self.read_checks:
            for uri, status in sorted(self.read_checks.items()):
                lines.append(f"Read check {uri}: {status}")
        return "\n".join(lines)


def extract_required_fields(schema: dict[str, Any] | None) -> set[str]:
    if not schema:
        return set()
    required = schema.get("required") or []
    return set(required)


def normalize_endpoint_url(endpoint_url: str) -> str:
    parsed = urlparse(endpoint_url)
    path = parsed.path or "/"
    if not path.endswith("/"):
        path = f"{path}/"
    return urlunparse(parsed._replace(path=path))


async def validate_mcp_contract(
    endpoint_url: str,
    *,
    headers: dict[str, str] | None = None,
    httpx_client_factory: Callable[..., Any] | None = None,
) -> ValidationReport:
    normalized_url = normalize_endpoint_url(endpoint_url)
    http_client = (
        httpx_client_factory(headers=headers, timeout=None, auth=None)
        if httpx_client_factory is not None
        else create_mcp_http_client(headers=headers)
    )

    async with http_client as client:
        async with streamable_http_client(normalized_url, http_client=client) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                initialize_result = await session.initialize()
                resources = await session.list_resources()
                templates = await session.list_resource_templates()
                tools = await session.list_tools()

                report = ValidationReport(
                    endpoint_url=endpoint_url,
                    server_name=initialize_result.serverInfo.name,
                    protocol_version=initialize_result.protocolVersion,
                    resource_uris=sorted(resource.uri for resource in resources.resources),
                    resource_templates=sorted(
                        template.uriTemplate for template in templates.resourceTemplates
                    ),
                    tool_names=sorted(tool.name for tool in tools.tools),
                )

                report.missing_resources = sorted(
                    REQUIRED_RESOURCE_URIS - set(report.resource_uris)
                )
                report.missing_resource_templates = sorted(
                    REQUIRED_RESOURCE_TEMPLATES - set(report.resource_templates)
                )
                report.missing_tools = sorted(
                    set(REQUIRED_TOOL_FIELDS) - set(report.tool_names)
                )

                tool_map = {tool.name: tool for tool in tools.tools}
                for tool_name, required_fields in REQUIRED_TOOL_FIELDS.items():
                    tool = tool_map.get(tool_name)
                    if tool is None:
                        continue
                    actual_fields = extract_required_fields(tool.inputSchema)
                    missing_fields = sorted(required_fields - actual_fields)
                    if missing_fields:
                        report.tool_schema_errors[tool_name] = missing_fields

                for uri in ("app://manifest", "app://health"):
                    if uri not in report.resource_uris:
                        continue
                    try:
                        await session.read_resource(uri)
                        report.read_checks[uri] = "ok"
                    except Exception as exc:  # pragma: no cover - defensive network boundary
                        report.read_checks[uri] = f"error: {exc}"

                return report
