from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import httpx

from automarketing.models import BenchmarkTarget, VisibilityObservation


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class RegistryPage:
    benchmarks: list[BenchmarkTarget]
    next_cursor: str | None


@dataclass
class SearchConsoleQueryMetric:
    query: str
    country: str | None
    clicks: float
    impressions: float
    ctr: float
    position: float


class OfficialMCPRegistryAdapter:
    def __init__(
        self,
        base_url: str = "https://registry.modelcontextprotocol.io/v0.1/servers",
        client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.Client(timeout=30.0)

    def fetch_page(self, cursor: str | None = None, limit: int = 100) -> dict[str, Any]:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        response = self._client.get(self._base_url, params=params)
        response.raise_for_status()
        return response.json()

    def parse_page(self, payload: dict[str, Any]) -> RegistryPage:
        benchmarks: list[BenchmarkTarget] = []
        for item in payload.get("servers", []):
            server = item.get("server") or {}
            name = server.get("name")
            if not name:
                continue

            remotes = server.get("remotes") or []
            repository = server.get("repository") or {}
            meta = item.get("_meta", {}).get("io.modelcontextprotocol.registry/official", {})
            observed_at_raw = meta.get("updatedAt") or meta.get("publishedAt")
            last_seen_at = (
                datetime.fromisoformat(observed_at_raw.replace("Z", "+00:00"))
                if observed_at_raw
                else utc_now()
            )
            benchmarks.append(
                BenchmarkTarget(
                    external_id=f"official_registry:{name}",
                    source="official_registry",
                    name=name,
                    title=server.get("title"),
                    description=server.get("description"),
                    website_url=server.get("websiteUrl"),
                    remote_url=remotes[0].get("url") if remotes else None,
                    repository_url=repository.get("url"),
                    last_seen_at=last_seen_at,
                )
            )

        return RegistryPage(
            benchmarks=benchmarks,
            next_cursor=payload.get("metadata", {}).get("nextCursor"),
        )


class SerpApiAdapter:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://serpapi.com/search",
        client: httpx.Client | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._client = client or httpx.Client(timeout=30.0)

    def search(
        self, query: str, language: str, country: str, limit: int = 20
    ) -> dict[str, Any]:
        response = self._client.get(
            self._base_url,
            params={
                "engine": "google",
                "api_key": self._api_key,
                "q": query,
                "hl": language,
                "gl": country,
                "num": limit,
            },
        )
        response.raise_for_status()
        return response.json()

    def parse_results(
        self,
        payload: dict[str, Any],
        *,
        query: str,
        language: str,
        country: str,
        source: str = "serpapi",
    ) -> list[VisibilityObservation]:
        observations: list[VisibilityObservation] = []
        for item in payload.get("organic_results", []):
            link = item.get("link")
            position = item.get("position")
            if not link or position is None:
                continue
            observations.append(
                VisibilityObservation(
                    query=query,
                    surface="web",
                    position=int(position),
                    observed_url=link,
                    observed_at=utc_now(),
                    source=source,
                    query_language=language,
                    query_country=country,
                    result_title=item.get("title"),
                    result_snippet=item.get("snippet"),
                    result_type="organic",
                    is_owned_result=False,
                )
            )
        return observations


class SearchConsoleAdapter:
    def __init__(
        self,
        access_token: str,
        base_url: str = "https://www.googleapis.com/webmasters/v3",
        client: httpx.Client | None = None,
    ) -> None:
        self._access_token = access_token
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.Client(timeout=30.0)

    def query_property(
        self,
        site_url: str,
        *,
        start_date: str,
        end_date: str,
        row_limit: int = 25000,
        start_row: int = 0,
    ) -> dict[str, Any]:
        encoded_site = quote(site_url, safe="")
        response = self._client.post(
            f"{self._base_url}/sites/{encoded_site}/searchAnalytics/query",
            headers={"Authorization": f"Bearer {self._access_token}"},
            json={
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": ["query", "country"],
                "type": "web",
                "rowLimit": row_limit,
                "startRow": start_row,
            },
        )
        response.raise_for_status()
        return response.json()

    def parse_rows(self, payload: dict[str, Any]) -> list[SearchConsoleQueryMetric]:
        metrics: list[SearchConsoleQueryMetric] = []
        for row in payload.get("rows", []):
            keys = row.get("keys") or []
            query = keys[0] if keys else None
            if not query:
                continue
            country = keys[1] if len(keys) > 1 else None
            metrics.append(
                SearchConsoleQueryMetric(
                    query=query,
                    country=country,
                    clicks=float(row.get("clicks", 0.0)),
                    impressions=float(row.get("impressions", 0.0)),
                    ctr=float(row.get("ctr", 0.0)),
                    position=float(row.get("position", 0.0)),
                )
            )
        return metrics
