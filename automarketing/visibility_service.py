from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta, timezone, datetime
from urllib.parse import urlparse

import httpx

from automarketing.models import (
    Application,
    BenchmarkObservation,
    BenchmarkTarget,
    TrackedQuery,
    VisibilityBenchmarkComparison,
    VisibilityCollectionRun,
    VisibilityConfig,
    VisibilityConfigRequest,
    VisibilityObservation,
    VisibilityRefreshRequest,
    VisibilityReport,
    VisibilityScoreBreakdown,
)
from automarketing.settings import Settings
from automarketing.visibility_adapters import (
    OfficialMCPRegistryAdapter,
    SearchConsoleAdapter,
    SearchConsoleQueryMetric,
    SerpApiAdapter,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


REACHABLE_STATUSES = {
    "reachable_open",
    "reachable_auth_required",
    "reachable_negotiation_required",
}


@dataclass
class RefreshSummary:
    app_slug: str
    requested_sources: list[str]
    completed_sources: list[str]
    skipped_sources: list[str]
    run_ids: list[str]
    observations_recorded: int
    benchmark_observations_recorded: int


class VisibilityService:
    def __init__(self, repository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings
        self._registry = OfficialMCPRegistryAdapter(base_url=settings.official_registry_url)

    def configure_tracking(
        self, app_slug: str, request: VisibilityConfigRequest
    ) -> VisibilityConfig:
        return self._repository.configure_visibility_tracking(app_slug, request)

    def list_benchmarks(self) -> list[BenchmarkTarget]:
        return self._repository.list_benchmark_targets()

    def refresh_benchmarks(
        self, requested_by: str = "system", max_pages: int = 5
    ) -> tuple[list[BenchmarkTarget], VisibilityCollectionRun]:
        run = self._repository.create_visibility_collection_run(
            source="official_registry",
            requested_by=requested_by,
        )
        cursor: str | None = None
        pages = 0
        collected: list[BenchmarkTarget] = []

        try:
            while pages < max_pages:
                payload = self._registry.fetch_page(cursor=cursor, limit=100)
                page = self._registry.parse_page(payload)
                collected.extend(page.benchmarks)
                cursor = page.next_cursor
                pages += 1
                if not cursor:
                    break
            stored = self._repository.upsert_benchmark_targets(collected)
            finished = self._repository.finish_visibility_collection_run(
                run.id,
                status="completed",
                raw_cursor=cursor,
            )
            return stored, finished
        except Exception as exc:
            finished = self._repository.finish_visibility_collection_run(
                run.id,
                status="failed",
                error_summary=str(exc),
                raw_cursor=cursor,
            )
            raise RuntimeError(f"Official registry refresh failed: {exc}") from exc

    def refresh_application(
        self, app_slug: str, request: VisibilityRefreshRequest
    ) -> dict[str, object]:
        sources = request.sources or ["official_registry", "serp", "search_console"]
        app = self._repository.get_application(app_slug)
        tracked_queries = self._repository.list_tracked_queries(app_slug)
        benchmark_targets = self._repository.list_benchmark_targets()
        if "official_registry" in sources and not benchmark_targets:
            benchmark_targets, _ = self.refresh_benchmarks(request.requested_by)

        completed: list[str] = []
        skipped: list[str] = []
        run_ids: list[str] = []
        observations_recorded = 0
        benchmark_observations_recorded = 0

        if "official_registry" in sources:
            run = self._repository.create_visibility_collection_run(
                source="official_registry",
                requested_by=request.requested_by,
            )
            run_ids.append(run.id)
            observations = self._build_registry_observations(app, benchmark_targets, run.id)
            if observations:
                observations_recorded += len(
                    self._repository.record_visibility_observations(app_slug, observations)
                )
            self._repository.finish_visibility_collection_run(run.id, status="completed")
            completed.append("official_registry")

        if "serp" in sources:
            if not self._settings.serpapi_api_key:
                skipped.append("serp")
            else:
                run = self._repository.create_visibility_collection_run(
                    source="serp",
                    requested_by=request.requested_by,
                )
                run_ids.append(run.id)
                serp = SerpApiAdapter(
                    api_key=self._settings.serpapi_api_key,
                    base_url=self._settings.serpapi_base_url,
                )
                owned_observations: list[VisibilityObservation] = []
                benchmark_observations: list[BenchmarkObservation] = []
                for tracked_query in tracked_queries:
                    payload = serp.search(
                        tracked_query.query,
                        tracked_query.language,
                        tracked_query.country,
                        limit=20,
                    )
                    parsed = serp.parse_results(
                        payload,
                        query=tracked_query.query,
                        language=tracked_query.language,
                        country=tracked_query.country,
                    )
                    for item in parsed:
                        item.is_owned_result = self._url_matches_owned_app(item.observed_url, app)
                        owned_observations.append(item)
                        benchmark = self._match_benchmark_by_url(
                            item.observed_url, benchmark_targets
                        )
                        if benchmark is not None:
                            benchmark_observations.append(
                                BenchmarkObservation(
                                    benchmark_external_id=benchmark.external_id,
                                    query=item.query,
                                    surface=item.surface,
                                    position=item.position,
                                    observed_url=item.observed_url,
                                    observed_at=item.observed_at,
                                    source=item.source,
                                    query_language=item.query_language,
                                    query_country=item.query_country,
                                    result_title=item.result_title,
                                    result_snippet=item.result_snippet,
                                    result_type=item.result_type,
                                    collection_run_id=run.id,
                                )
                            )
                if owned_observations:
                    observations_recorded += len(
                        self._repository.record_visibility_observations(
                            app_slug,
                            [
                                item.model_copy(update={"collection_run_id": run.id})
                                for item in owned_observations
                            ],
                        )
                    )
                if benchmark_observations:
                    benchmark_observations_recorded += len(
                        self._repository.record_benchmark_observations(benchmark_observations)
                    )
                self._repository.finish_visibility_collection_run(run.id, status="completed")
                completed.append("serp")

        if "search_console" in sources:
            if not self._settings.google_api_access_token or not app.search_console_property:
                skipped.append("search_console")
            else:
                run = self._repository.create_visibility_collection_run(
                    source="search_console",
                    requested_by=request.requested_by,
                )
                run_ids.append(run.id)
                search_console = SearchConsoleAdapter(
                    access_token=self._settings.google_api_access_token,
                    base_url=self._settings.google_search_console_base_url,
                )
                today = date.today()
                start = today - timedelta(days=28)
                payload = search_console.query_property(
                    app.search_console_property,
                    start_date=start.isoformat(),
                    end_date=today.isoformat(),
                )
                metrics = search_console.parse_rows(payload)
                observations = self._search_console_observations(app, metrics, run.id)
                if observations:
                    observations_recorded += len(
                        self._repository.record_visibility_observations(app_slug, observations)
                    )
                self._repository.finish_visibility_collection_run(run.id, status="completed")
                completed.append("search_console")

        if "directories" in sources:
            skipped.append("directories")

        return {
            "app_slug": app_slug,
            "requested_sources": sources,
            "completed_sources": completed,
            "skipped_sources": skipped,
            "run_ids": run_ids,
            "observations_recorded": observations_recorded,
            "benchmark_observations_recorded": benchmark_observations_recorded,
        }

    def build_report(self, app_slug: str) -> VisibilityReport:
        app = self._repository.get_application(app_slug)
        owned_observations = self._repository.list_visibility(app_slug)
        benchmark_targets = self._repository.list_benchmark_targets()
        benchmark_observations = self._repository.list_benchmark_observations()

        matched_target = self._match_owned_target(app, benchmark_targets)
        latest_remote_status = self._latest_remote_status(owned_observations, app.mcp_endpoint)

        branded_queries = {
            item.query for item in self._repository.list_tracked_queries(app_slug)
            if item.query_kind == "brand"
        }
        task_queries = {
            item.query for item in self._repository.list_tracked_queries(app_slug)
            if item.query_kind == "task"
        }

        mcp_breakdown = VisibilityScoreBreakdown(
            value=0,
            active_listing=35 if matched_target else 0,
            metadata_completeness=self._metadata_completeness_points(matched_target),
            remote_reachability=25 if latest_remote_status in REACHABLE_STATUSES else 0,
            directory_presence=0,
            branded_web_rank=self._branded_mcp_rank_points(owned_observations, branded_queries),
        )
        mcp_breakdown.value = (
            mcp_breakdown.active_listing
            + mcp_breakdown.metadata_completeness
            + mcp_breakdown.remote_reachability
            + mcp_breakdown.directory_presence
            + mcp_breakdown.branded_web_rank
        )

        web_breakdown = VisibilityScoreBreakdown(
            value=0,
            branded_rank=self._web_rank_points(owned_observations, branded_queries, cap=40),
            task_rank=self._web_rank_points(owned_observations, task_queries, cap=30),
            search_console_trend=self._search_console_points(owned_observations),
            indexability=10 if app.website_url else 0,
        )
        web_breakdown.value = (
            web_breakdown.branded_rank
            + web_breakdown.task_rank
            + web_breakdown.search_console_trend
            + web_breakdown.indexability
        )

        confidence = "partial"
        if app.search_console_property and any(
            item.source == "search_console" for item in owned_observations
        ):
            confidence = "full"

        comparison = self._build_benchmark_comparison(
            benchmark_targets, benchmark_observations, owned_observations
        )
        opportunities = self._top_missed_opportunities(
            app,
            matched_target=matched_target,
            latest_remote_status=latest_remote_status,
            branded_queries=branded_queries,
            task_queries=task_queries,
            owned_observations=owned_observations,
        )

        return VisibilityReport(
            app_slug=app_slug,
            web_visibility_score=web_breakdown.value,
            mcp_visibility_score=mcp_breakdown.value,
            confidence=confidence,
            web_breakdown=web_breakdown,
            mcp_breakdown=mcp_breakdown,
            owned_observations=owned_observations[:20],
            benchmark_comparison=comparison,
            top_missed_opportunities=opportunities,
        )

    def run_official_registry_ingestion(
        self, requested_by: str = "system"
    ) -> tuple[list[BenchmarkTarget], VisibilityCollectionRun]:
        return self.refresh_benchmarks(requested_by=requested_by)

    def run_owned_app_visibility_refresh(
        self, app_slug: str, requested_by: str = "system"
    ) -> dict[str, object]:
        return self.refresh_application(
            app_slug,
            VisibilityRefreshRequest(
                sources=["official_registry", "serp", "search_console"],
                requested_by=requested_by,
            ),
        )

    def run_benchmark_comparison_refresh(self, app_slug: str) -> VisibilityReport:
        return self.build_report(app_slug)

    def _build_registry_observations(
        self,
        app: Application,
        benchmark_targets: list[BenchmarkTarget],
        run_id: str,
    ) -> list[VisibilityObservation]:
        observations: list[VisibilityObservation] = []
        matched_target = self._match_owned_target(app, benchmark_targets)
        brand_query = f"{(app.brand_terms or [app.slug])[0]} mcp"
        if matched_target is not None:
            observations.append(
                VisibilityObservation(
                    query=brand_query,
                    surface="mcp_registry",
                    position=1,
                    observed_url=matched_target.remote_url
                    or matched_target.website_url
                    or app.mcp_endpoint,
                    observed_at=utc_now(),
                    source="official_registry",
                    query_language=app.primary_language,
                    query_country=app.primary_country,
                    result_title=matched_target.title or matched_target.name,
                    result_snippet=matched_target.description,
                    result_type="registry",
                    is_owned_result=True,
                    collection_run_id=run_id,
                )
            )
        remote_status = self.classify_remote_endpoint(app.mcp_endpoint)
        observations.append(
            VisibilityObservation(
                query=f"{app.slug} remote status",
                surface="mcp_registry",
                position=1,
                observed_url=app.mcp_endpoint,
                observed_at=utc_now(),
                source="official_registry",
                query_language=app.primary_language,
                query_country=app.primary_country,
                result_title=app.name,
                result_type=remote_status,
                is_owned_result=True,
                collection_run_id=run_id,
            )
        )
        return observations

    def _search_console_observations(
        self,
        app: Application,
        metrics: list[SearchConsoleQueryMetric],
        run_id: str,
    ) -> list[VisibilityObservation]:
        observations: list[VisibilityObservation] = []
        for metric in metrics:
            observations.append(
                VisibilityObservation(
                    query=metric.query,
                    surface="web",
                    position=max(int(round(metric.position)), 1),
                    observed_url=app.website_url or app.mcp_endpoint,
                    observed_at=utc_now(),
                    source="search_console",
                    query_country=metric.country,
                    result_title=app.name,
                    result_snippet=json.dumps(
                        {
                            "clicks": metric.clicks,
                            "impressions": metric.impressions,
                            "ctr": metric.ctr,
                            "position": metric.position,
                        }
                    ),
                    result_type="search_console",
                    is_owned_result=True,
                    collection_run_id=run_id,
                )
            )
        return observations

    def classify_remote_endpoint(self, url: str) -> str:
        try:
            response = httpx.get(url, timeout=15.0, follow_redirects=True)
            status = response.status_code
            if 200 <= status < 300:
                return "reachable_open"
            if status in {401, 403}:
                return "reachable_auth_required"
            if status in {405, 406}:
                return "reachable_negotiation_required"
            return "unreachable_other"
        except httpx.TimeoutException:
            return "unreachable_timeout"
        except httpx.ConnectError as exc:
            message = str(exc).lower()
            if "certificate" in message or "ssl" in message or "tls" in message:
                return "unreachable_tls"
            if "name or service not known" in message or "nodename nor servname" in message:
                return "unreachable_dns"
            return "unreachable_other"
        except Exception:
            return "unreachable_other"

    def _url_matches_owned_app(self, observed_url: str, app: Application) -> bool:
        candidates = [item for item in [app.website_url, app.mcp_endpoint] if item]
        return any(observed_url.startswith(candidate) for candidate in candidates)

    def _match_benchmark_by_url(
        self, observed_url: str, benchmarks: list[BenchmarkTarget]
    ) -> BenchmarkTarget | None:
        for benchmark in benchmarks:
            for candidate in (
                benchmark.website_url,
                benchmark.remote_url,
                benchmark.repository_url,
            ):
                if candidate and observed_url.startswith(candidate):
                    return benchmark
        return None

    def _match_owned_target(
        self, app: Application, benchmarks: list[BenchmarkTarget]
    ) -> BenchmarkTarget | None:
        brand_terms = {term.lower() for term in app.brand_terms} | {app.slug.lower()}
        for benchmark in benchmarks:
            if benchmark.remote_url and benchmark.remote_url == app.mcp_endpoint:
                return benchmark
            if app.website_url and benchmark.website_url == app.website_url:
                return benchmark
            name_bits = " ".join(filter(None, [benchmark.name, benchmark.title])).lower()
            if any(term in name_bits for term in brand_terms):
                return benchmark
        return None

    def _metadata_completeness_points(self, benchmark: BenchmarkTarget | None) -> int:
        if benchmark is None:
            return 0
        present = sum(
            1
            for item in [
                benchmark.name or benchmark.title,
                benchmark.description,
                benchmark.website_url,
                benchmark.remote_url,
                benchmark.repository_url,
            ]
            if item
        )
        return int(round((present / 5) * 20))

    def _latest_remote_status(
        self, observations: list[VisibilityObservation], mcp_endpoint: str
    ) -> str | None:
        for observation in observations:
            if observation.observed_url == mcp_endpoint and observation.result_type in {
                "reachable_open",
                "reachable_auth_required",
                "reachable_negotiation_required",
                "unreachable_dns",
                "unreachable_tls",
                "unreachable_timeout",
                "unreachable_other",
            }:
                return observation.result_type
        return None

    def _branded_mcp_rank_points(
        self, observations: list[VisibilityObservation], branded_queries: set[str]
    ) -> int:
        owned = [
            item.position
            for item in observations
            if item.is_owned_result
            and item.query in branded_queries
            and item.surface == "mcp_registry"
        ]
        if not owned:
            return 0
        best = min(owned)
        if best <= 3:
            return 10
        if best <= 10:
            return 5
        return 0

    def _web_rank_points(
        self, observations: list[VisibilityObservation], queries: set[str], cap: int
    ) -> int:
        owned = [
            item.position
            for item in observations
            if item.surface == "web"
            and item.is_owned_result
            and item.query in queries
            and item.source != "search_console"
        ]
        if not owned:
            return 0
        best = min(owned)
        if best <= 3:
            return cap
        if best <= 10:
            return max(cap - 10, 0)
        if best <= 20:
            return max(cap - 20, 0)
        return 0

    def _search_console_points(self, observations: list[VisibilityObservation]) -> int:
        metrics = []
        for observation in observations:
            if observation.source != "search_console" or not observation.result_snippet:
                continue
            try:
                parsed = json.loads(observation.result_snippet)
            except json.JSONDecodeError:
                continue
            metrics.append(parsed)
        if not metrics:
            return 0
        clicks = sum(item.get("clicks", 0.0) for item in metrics)
        impressions = sum(item.get("impressions", 0.0) for item in metrics)
        if impressions >= 100 and clicks > 0:
            return 20
        if impressions > 0:
            return 10
        return 0

    def _build_benchmark_comparison(
        self,
        benchmarks: list[BenchmarkTarget],
        benchmark_observations: list[BenchmarkObservation],
        owned_observations: list[VisibilityObservation],
    ) -> list[VisibilityBenchmarkComparison]:
        owned_best: dict[str, int] = {}
        for observation in owned_observations:
            if not observation.is_owned_result:
                continue
            owned_best[observation.query] = min(
                owned_best.get(observation.query, observation.position),
                observation.position,
            )

        benchmark_map = {item.external_id: item for item in benchmarks}
        outrankers: dict[str, list[str]] = {}
        for observation in benchmark_observations:
            owned_position = owned_best.get(observation.query)
            if owned_position is None or observation.position >= owned_position:
                continue
            outrankers.setdefault(observation.benchmark_external_id, []).append(
                observation.query
            )

        comparisons: list[VisibilityBenchmarkComparison] = []
        for external_id, queries in sorted(
            outrankers.items(),
            key=lambda item: (-len(item[1]), item[0]),
        )[:20]:
            benchmark = benchmark_map.get(external_id)
            if benchmark is None:
                continue
            comparisons.append(
                VisibilityBenchmarkComparison(
                    benchmark=benchmark,
                    overlap_score=len(queries),
                    outranks_owned_queries=sorted(set(queries)),
                )
            )
        return comparisons

    def _top_missed_opportunities(
        self,
        app: Application,
        *,
        matched_target: BenchmarkTarget | None,
        latest_remote_status: str | None,
        branded_queries: set[str],
        task_queries: set[str],
        owned_observations: list[VisibilityObservation],
    ) -> list[str]:
        items: list[str] = []
        if matched_target is None:
            items.append("No active official-registry listing matched to the app yet.")
        if latest_remote_status not in REACHABLE_STATUSES:
            items.append("Remote MCP endpoint is not currently reachable.")
        if not app.search_console_property:
            items.append("Search Console property is not configured.")
        if branded_queries and not any(
            item.is_owned_result and item.query in branded_queries for item in owned_observations
        ):
            items.append("Owned branded queries are missing from current observations.")
        if task_queries and not any(
            item.is_owned_result and item.query in task_queries for item in owned_observations
        ):
            items.append("Task queries are not producing owned results in the current sample.")
        return items[:5]
