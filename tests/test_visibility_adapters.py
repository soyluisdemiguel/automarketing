import json
from pathlib import Path

import httpx

from automarketing.visibility_adapters import (
    OfficialMCPRegistryAdapter,
    SearchConsoleAdapter,
    SerpApiAdapter,
)


FIXTURES = Path(__file__).parent / "fixtures" / "visibility"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_official_registry_adapter_parses_benchmark_targets() -> None:
    payload = load_fixture("official_registry_page.json")
    adapter = OfficialMCPRegistryAdapter()

    page = adapter.parse_page(payload)

    assert page.next_cursor == "agency.lona/trading:2.0.0"
    assert len(page.benchmarks) == 1
    assert page.benchmarks[0].external_id == "official_registry:agency.lona/trading"
    assert page.benchmarks[0].remote_url == "https://mcp.lona.agency/mcp"


def test_official_registry_adapter_fetches_catalog_page() -> None:
    payload = load_fixture("official_registry_page.json")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v0.1/servers"
        assert request.url.params["limit"] == "2"
        return httpx.Response(200, json=payload)

    adapter = OfficialMCPRegistryAdapter(
        base_url="https://registry.modelcontextprotocol.io/v0.1/servers",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    response = adapter.fetch_page(limit=2)

    assert response["metadata"]["count"] == 1


def test_serpapi_adapter_parses_organic_results() -> None:
    payload = load_fixture("serpapi_results.json")
    adapter = SerpApiAdapter(api_key="test-key")

    observations = adapter.parse_results(
        payload,
        query="reeldna ai mcp",
        language="en",
        country="us",
    )

    assert len(observations) == 2
    assert observations[0].position == 1
    assert observations[0].result_title == "ReelDNA AI"
    assert observations[0].source == "serpapi"
    assert observations[0].query_language == "en"


def test_serpapi_adapter_sends_expected_query_params() -> None:
    payload = load_fixture("serpapi_results.json")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/search"
        assert request.url.params["engine"] == "google"
        assert request.url.params["api_key"] == "test-key"
        assert request.url.params["q"] == "reeldna ai mcp"
        assert request.url.params["hl"] == "en"
        assert request.url.params["gl"] == "us"
        assert request.url.params["num"] == "20"
        return httpx.Response(200, json=payload)

    adapter = SerpApiAdapter(
        api_key="test-key",
        base_url="https://serpapi.com/search",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    response = adapter.search("reeldna ai mcp", "en", "us", limit=20)

    assert len(response["organic_results"]) == 2


def test_search_console_adapter_parses_query_rows() -> None:
    payload = load_fixture("search_console_query.json")
    adapter = SearchConsoleAdapter(access_token="token")

    rows = adapter.parse_rows(payload)

    assert len(rows) == 2
    assert rows[0].query == "reeldna ai"
    assert rows[0].country == "usa"
    assert rows[0].clicks == 14.0


def test_search_console_adapter_posts_expected_request() -> None:
    payload = load_fixture("search_console_query.json")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith(
            "/sites/https://reeldna.example.com//searchAnalytics/query"
        )
        assert request.headers["Authorization"] == "Bearer token"
        body = json.loads(request.content.decode("utf-8"))
        assert body["dimensions"] == ["query", "country"]
        assert body["rowLimit"] == 25000
        return httpx.Response(200, json=payload)

    adapter = SearchConsoleAdapter(
        access_token="token",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    response = adapter.query_property(
        "https://reeldna.example.com/",
        start_date="2026-02-12",
        end_date="2026-03-11",
    )

    assert len(response["rows"]) == 2
