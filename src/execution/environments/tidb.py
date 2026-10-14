from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
import os
import re
import shutil
import subprocess
import time
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlglot import exp, parse
from sqlglot.errors import ParseError

from src.database.system import DatabaseSystem
from src.execution.deployments.base import BaseDeployment
from src.execution.deployments.tidb import TiDBDockerDeployment
from src.execution.deployments.tidb_support import lightning_job_id, lightning_network_alias
from src.execution.environments.base import BaseEnv
from src.execution.environments.sql import (
    SQL_TRUNCATION_HINT,
    SqlConnectionSurface,
    _bound_sql_rows,
)
from src.execution.history.metrics import (
    MetricFrame,
    MetricQuery,
    MetricService,
    bound_metric_result,
    format_utc_timestamp,
    parse_utc_timestamp,
    render_metric_frame,
    validate_metric_frame,
)
from src.execution.history.records import (
    CapturedRecords,
    FrozenHistoricalRecordStore,
    HistoricalRecordSource,
    HistoricalCoverage,
)
from src.execution.history.sql_archive import FrozenHistoricalSqlArchive
from src.execution.history.timeline import FrozenHistoricalTimeline, FrozenHistoryMetricProvider
from src.execution.sampler_grid import SAMPLER_LAG_TOLERANCE_INTERVALS, SamplerGridStrikes
from src.execution.specs import TiDBCaseRuntime
from src.execution.tidb_cluster_control import TiDBClusterControl
from src.execution.tidb_connection_router import TiDBConnectionRouter
from src.execution.tidb_history import (
    build_slow_query_records,
    build_topsql_records,
    parse_docker_log_records,
    reject_tidb_public_historical_sql,
)
from src.execution.tidb_metrics import (
    CASE_ONLY_METRICS,
    LivePrometheusMetricProvider,
    PdMetricSampler,
    SQL_BACKED_METRICS,
    TiDBSQLMetricSampler,
    TIDB_METRIC_CATALOG,
)
from src.execution.tidb_tool_definitions import TIDB_TOOL_DEFINITIONS
from src.execution.tools import Tool
from src.knowledge.tidb_knowledge_base import TiDBKnowledgeBase


class ReplicationProgressUnavailableError(RuntimeError):
    """A TiCDC feed exists, but its current progress cannot prove delivery health."""

    def __init__(
        self,
        *,
        changefeed_id: str,
        reason: str,
        state: object,
        error: object,
        upstream_tso: int,
        resolved_tso: int,
        checkpoint_tso: int,
    ) -> None:
        self.details = {
            "changefeed_id": changefeed_id,
            "reason": reason,
            "state": state,
            "error": error,
            "upstream_tso": upstream_tso,
            "resolved_tso": resolved_tso,
            "checkpoint_tso": checkpoint_tso,
        }
        super().__init__(
            "TiCDC replication progress is unavailable: "
            f"changefeed_id={changefeed_id!r}, reason={reason!r}, state={state!r}, "
            f"error={error!r}, upstream_tso={upstream_tso}, resolved_tso={resolved_tso}, "
            f"checkpoint_tso={checkpoint_tso}"
        )


class TiDBEnv(BaseEnv):
    """TiDB database semantics and agent tools for one benchmark run."""

    system = DatabaseSystem.TIDB
    cluster_control_type = TiDBClusterControl
    agent_sql_observers: tuple[Callable[[str, str], None], ...] = ()
    additional_log_sources: tuple[str, ...] = ()
    CONNECTION_ROUTER_TARGET = "connection-router"
    SQL_TIMEOUT_SECONDS = 35
    BOOTSTRAP_SQL_TIMEOUT_SECONDS = 300
    EXTERNAL_LOG_MAX_LINE_CHARS = 4000
    EXTERNAL_LOG_MAX_CONTENT_CHARS = 24000

    PUBLIC_TOOLS = (
        "query_metrics",
        "execute_sql",
        "manage_cluster",
        "read_log",
        "search_knowledge",
        "help",
        "submit",
        "exit",
    )
    FROZEN_HISTORY_PUBLIC_TOOLS = PUBLIC_TOOLS
    COMPOSE_SERVICE_LABEL = "container_label_com_docker_compose_service"
    CASE_ONLY_HISTORY_METRICS = CASE_ONLY_METRICS
    RESOURCE_QUERIES = {
        "cpu": ("sum(rate(container_cpu_usage_seconds_total{selector}[10s]))", "cores"),
        "disk_usage": ("sum(container_fs_usage_bytes{selector})", "bytes"),
        "network_io": (
            "sum(rate(container_network_receive_bytes_total{selector}[10s]) + "
            "rate(container_network_transmit_bytes_total{selector}[10s]))",
            "bytes_per_second",
        ),
    }
    TIME_SERIES_METRICS = TIDB_METRIC_CATALOG.metric_names

    def __init__(
        self,
        *,
        run_id: Optional[str] = None,
        workload=None,
        deployment: Optional[BaseDeployment] = None,
        port_base: int = 4000,
        tidb_readiness_timeout_sec: int = 1800,
        warm_tidb_readiness_timeout_sec: int = 300,
        user: str = "root",
        password: str = "",
        dbname: str = "test",
        sample_interval_sec: float = 2.0,
        return_window_seconds: int = 60,
        workload_runner_config: Optional[Dict[str, Any]] = None,
        image_group_key: Optional[str] = None,
        storage_key: Optional[str] = None,
        storage_root: Optional[str] = None,
        enabled_tools: Optional[Sequence[str]] = None,
    ):
        if deployment is None:
            if run_id is None:
                raise ValueError("TiDBEnv requires run_id when deployment is not provided")
            deployment = TiDBDockerDeployment(
                run_id=run_id,
                port_base=port_base,
                storage_key=storage_key,
                storage_root=storage_root,
                image_group_key=image_group_key,
                tidb_readiness_timeout_sec=tidb_readiness_timeout_sec,
                warm_tidb_readiness_timeout_sec=warm_tidb_readiness_timeout_sec,
            )
        elif any(
            value is not None
            for value in (image_group_key, storage_key, storage_root)
        ):
            raise ValueError(
                "TiDBEnv deployment options require the default TiDBDockerDeployment: "
                f"deployment={type(deployment).__name__}, image_group_key={image_group_key!r}, "
                f"storage_key={storage_key!r}, storage_root={storage_root!r}"
            )
        self._sql_connection_surfaces: Dict[str, SqlConnectionSurface] = {}
        super().__init__(
            workload,
            deployment,
            enabled_tools=self.PUBLIC_TOOLS if enabled_tools is None else enabled_tools,
        )
        self.run_id = deployment.run_id
        self.host, self.port = deployment.primary_tidb_endpoint
        self.user = user
        self.password = password
        self.dbname = dbname
        self.sample_interval_sec = sample_interval_sec
        self.return_window_seconds = return_window_seconds
        self.sql_timeout_seconds = 35
        self.workload_runner_config = workload_runner_config or {}
        self._conn = None
        self._secondary_conn = None
        self._secondary_host = None
        self._secondary_port = None
        self._secondary_password = None
        self._replication_endpoint = None
        self._workload_runner = None
        self._connection_routers: Dict[str, TiDBConnectionRouter] = {}
        self._clock_status_observed = False
        self._connection_router_connections: Dict[int, str] = {}
        self._workload_connection_invalidation_generation = 0
        self._workload_session_setups: Dict[int, dict[str, object]] = {}
        self._connection_router_invalidation_rules: Dict[
            str, tuple[frozenset[str], tuple[str, ...]]
        ] = {}
        self._visible_since = time.time()
        self._metrics_hidden_depth = 0
        self._log_visible_lines: Dict[str, int] = {}
        self._tidb_knowledge_bases: Dict[str, TiDBKnowledgeBase] = {}
        self._import_controller = None
        self._storage_recovery_contract = None
        self._known_store_ids: Dict[str, int] = {}
        self._observed_gc_safepoint: dict[str, object] | None = None
        self._observed_changefeed_diagnostics: dict[tuple[str, str], dict[str, object]] = {}
        self._observed_region_ids: Dict[str, set[int]] = {}
        self._case = None
        self._history_sql_archive: FrozenHistoricalSqlArchive | None = None
        if int(sample_interval_sec) != sample_interval_sec or sample_interval_sec <= 0:
            raise ValueError(
                f"TiDB sample_interval_sec must be a positive whole number: sample_interval_sec={sample_interval_sec!r}"
            )
        self._sql_metric_sampler = TiDBSQLMetricSampler(run_id=self.run_id)
        self._pd_metric_sampler = PdMetricSampler(
            deployment=self.deployment,
            run_id=self.run_id,
            sample_interval_sec=int(sample_interval_sec),
        )
        self._metric_service = MetricService(
            catalog=TIDB_METRIC_CATALOG,
            live=LivePrometheusMetricProvider(
                deployment=self.deployment,
                run_id=self.run_id,
                sample_interval_sec=int(sample_interval_sec),
                return_window_seconds=return_window_seconds,
                sql_metric_provider=self._sql_metric_sampler.query,
                pd_metric_provider=self._pd_metric_sampler.query,
                workload_profile_provider=self._capture_workload_profile_metric,
            )
        )
        self._history_timeline: FrozenHistoricalTimeline | None = None
        self._metric_capture_padding_events: list[dict[str, object]] = []

    def metric_history_catalog(self):
        return TIDB_METRIC_CATALOG

    def _case_query_metrics_definition(self) -> dict[str, Any] | None:
        history_spec = getattr(getattr(self, "_case", None), "frozen_history", None)
        if history_spec is None:
            return None
        definition = deepcopy(TIDB_TOOL_DEFINITIONS["query_metrics"])
        static_metrics = {
            item["metric_name"]: item
            for item in definition.get("metric_definitions", [])
        }
        target_scopes = {
            "resource_group_usage": "explicit resource-group name selected by this Case",
            "resource_group_throttle": "explicit resource-group name selected by this Case",
            "transaction_commit": "TiDB endpoint selected by this Case",
            "statistics_state": "SQL-backed table series selected by this Case",
            "plan_cardinality": "SQL digest series selected by this Case",
            "lightning_progress": "the Case Lightning job",
            "lightning_throughput": "the Case Lightning job",
            "lightning_workers": "the Case Lightning job",
            "workload_profile": "the Case frontend workload profiles",
            "pd_region_inventory": "the Case PD cluster Region inventory",
            "pd_region_activity": "the Case PD cluster scheduling activity",
            "pd_leader_distribution": "the Case TiKV leader distribution",
            "ticdc_progress": "the Case changefeed checkpoint and resolved progress",
            "ticdc_sink": "the Case changefeed sink throughput and flush activity",
        }
        metric_definitions = []
        for raw_metric in history_spec.required_metrics:
            metric = str(raw_metric).casefold()
            item = static_metrics.get(metric)
            if item is None:
                item = {
                    "metric_name": metric,
                    "metric_description": "Case-scoped raw historical series.",
                    "target_scope": target_scopes.get(metric, "Case-selected target"),
                }
            metric_definitions.append(item)
        definition["metric_definitions"] = metric_definitions
        for parameter in definition["parameter_definitions"]:
            if parameter["parameter_name"] == "metric_type":
                parameter["allowed_values"] = [
                    str(metric).casefold() for metric in history_spec.required_metrics
                ]
                break
        return definition

    def _configure_tools(self, enabled_tools: Optional[Sequence[str]] = None) -> None:
        super()._configure_tools(enabled_tools)
        metric_definition = self._case_query_metrics_definition()
        if metric_definition is None:
            return
        self._enabled_tool_specs = [
            replace(spec, definition=deepcopy(metric_definition))
            if spec.alias == "query_metrics" and metric_definition is not None
            else spec
            for spec in self._enabled_tool_specs
        ]
        self._alias_to_tool_spec = {
            spec.alias: spec for spec in self._enabled_tool_specs
        }

    def validate_metric_history_case(self, spec, background_workload) -> None:
        spec.validate(background_workload)
        catalog = self.metric_history_catalog()
        for metric in spec.required_metrics:
            catalog.definition(metric)
            normalized_metric = str(metric).casefold()
            selected_targets = spec.metric_targets.get(normalized_metric)
            if normalized_metric == "workload_profile":
                if selected_targets is not None and tuple(selected_targets) != (None,):
                    raise ValueError(
                        "TiDB workload_profile history must capture the Case frontend profiles through target=None: "
                        f"selected_targets={tuple(selected_targets)!r}"
                    )
                targets = (None,)
            else:
                targets = (
                    tuple(selected_targets)
                    if selected_targets is not None
                    else catalog.target_variants(normalized_metric, self.deployment)
                )
            if not targets or len(set(targets)) != len(targets):
                raise ValueError(
                    "TiDB frozen-history Case target selection must be non-empty and unique: "
                    f"metric={normalized_metric!r}, targets={targets!r}"
                )
            for target in targets:
                catalog.validate_target(normalized_metric, target, self.deployment)
        for decoy in spec.decoys:
            definition = catalog.definition(decoy.metric)
            if decoy.field not in definition.value_fields:
                raise ValueError(
                    f"Frozen-history decoy field is not in catalog: decoy_id={decoy.decoy_id!r}, "
                    f"metric={decoy.metric!r}, field={decoy.field!r}, fields={definition.value_fields!r}"
                )
            if str(decoy.metric).casefold() == "workload_profile":
                frontend_profiles = {
                    profile.name
                    for profile in background_workload.profiles
                    if profile.tier == "FRONTEND_SLO"
                }
                if decoy.target not in frontend_profiles:
                    raise ValueError(
                        "TiDB workload_profile decoy target must be a Case frontend profile: "
                        f"decoy_id={decoy.decoy_id!r}, target={decoy.target!r}, "
                        f"frontend_profiles={sorted(frontend_profiles)!r}"
                    )
            else:
                catalog.validate_target(decoy.metric, decoy.target, self.deployment)
            selected_targets = spec.metric_targets.get(str(decoy.metric).casefold())
            if selected_targets is not None and str(decoy.metric).casefold() != "workload_profile":
                series_targets = {
                    target
                    for target in selected_targets
                    if target is not None
                }
                if decoy.target is not None and decoy.target not in series_targets:
                    raise ValueError(
                        "TiDB frozen-history decoy target is outside the Case target selection: "
                        f"decoy_id={decoy.decoy_id!r}, metric={decoy.metric!r}, target={decoy.target!r}, "
                        f"selected={tuple(selected_targets)!r}"
                    )
        unsupported = set(spec.record_sources) - set(HistoricalRecordSource)
        if unsupported:
            raise ValueError(
                f"TiDB frozen history has unsupported record sources: sources={sorted(item.value for item in unsupported)!r}"
            )

    def metric_samples_fresh(self, window_seconds: int = 30) -> bool:
        return self.deployment.prometheus_services_fresh(window_seconds)

    def metric_history_warmup_seconds(self, required_metrics: tuple[str, ...]) -> float:
        spec = getattr(self._case, "frozen_history", None)
        rate_windows = getattr(spec, "metric_rate_windows", {}) if spec is not None else {}
        return max(
            max(
                float(self.metric_history_catalog().definition(metric).lookback_seconds),
                float(rate_windows.get(str(metric).casefold(), 0)),
            )
            for metric in required_metrics
        )

    def configure_case(self, case) -> None:
        history_spec = getattr(case, "frozen_history", None)
        if (
            history_spec is not None
            and "lightning_progress" in tuple(history_spec.required_metrics)
        ):
            # Must be declared before super().configure_case() renders the
            # Prometheus scrape configuration for the deployment.
            self.deployment.enable_lightning_scrape_target(
                f"{lightning_network_alias(self.deployment.run_id)}:8287"
            )
        super().configure_case(case)
        self._case = case
        changefeed_id = getattr(case, "changefeed_id", None)
        self.deployment.metric_changefeed_target = (
            f"changefeed/{changefeed_id}" if changefeed_id is not None else None
        )
        if history_spec is not None:
            self.validate_metric_history_case(history_spec, case.background_workload)
            self._configure_tools(self.FROZEN_HISTORY_PUBLIC_TOOLS)

    def configure_runtime(self, runtime: TiDBCaseRuntime) -> None:
        if not isinstance(runtime, TiDBCaseRuntime):
            raise TypeError(
                f"TiDBEnv requires TiDBCaseRuntime, got {type(runtime).__name__}"
            )
        self.deployment.configure_runtime(runtime)
        self.sql_timeout_seconds = runtime.sql_timeout_seconds
        self.host, self.port = self.deployment.primary_tidb_endpoint

    def configure_history_observability(self, spec) -> None:
        """Configure the real TiDB statement summary before frozen-history capture."""
        connection = self._ensure_connection()
        statements = (
            "SET GLOBAL tidb_enable_stmt_summary = 1",
            "SET GLOBAL tidb_stmt_summary_refresh_interval = 30",
            "SET GLOBAL tidb_stmt_summary_history_size = 60",
            "SET GLOBAL tidb_stmt_summary_max_stmt_count = 10000",
        )
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
        sql_metrics = tuple(
            str(metric).casefold()
            for metric in spec.required_metrics
            if str(metric).casefold() in SQL_BACKED_METRICS
        )
        if sql_metrics:
            contract = getattr(self._case, "metric_history_adapter_config", None)
            if contract is None:
                raise RuntimeError(
                    "TiDB SQL-backed metric history requires metric_history_adapter_config: "
                    f"run_id={self.run_id!r}, case={getattr(self._case, 'case_id', None)!r}, metrics={sql_metrics!r}"
                )
            if "statistics_state" in sql_metrics:
                self._wait_statistics_meta_ready(contract)
            self._sql_metric_sampler.configure(
                metrics=sql_metrics,
                step_seconds=spec.base_step_seconds,
                contract=contract,
                connection_factory=lambda application_name: self._connect(
                    self.dbname,
                    application_name=application_name,
                ),
            )
            self._sql_metric_sampler.start()
        if {
            "pd_region_inventory",
            "pd_region_activity",
            "pd_leader_distribution",
        }.intersection(str(metric).casefold() for metric in spec.required_metrics):
            self._pd_metric_sampler.start()

    def _wait_statistics_meta_ready(self, contract: Mapping[str, object]) -> None:
        """Block until every contract table has an ANALYZE row in SHOW STATS_META.

        The SQL metric sampler asserts a stats-meta row per contract table on
        every step; ANALYZE in the workload kit publishes that row
        asynchronously, so wait here rather than failing the first sample.
        """
        database = str(contract["database"])
        tables = tuple(str(item) for item in contract["tables"])
        deadline = time.monotonic() + 120
        missing: tuple[str, ...] = tables
        while True:
            connection = self._ensure_connection()
            with connection.cursor() as cursor:
                present = set()
                for table in tables:
                    cursor.execute(
                        "SHOW STATS_META WHERE Db_name=%s AND Table_name=%s",
                        (database, table),
                    )
                    if cursor.fetchall():
                        present.add(table)
            missing = tuple(table for table in tables if table not in present)
            if not missing:
                return
            if time.monotonic() > deadline:
                raise RuntimeError(
                    "TiDB statistics metadata was not published before frozen-history capture: "
                    f"run_id={self.run_id!r}, database={database!r}, missing_tables={missing!r}"
                )
            time.sleep(2)

    def capture_metric_history(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
        *,
        metric_targets: Mapping[str, tuple[str | None, ...]] | None = None,
        rate_windows: Mapping[str, int] | None = None,
    ) -> tuple:
        if start_epoch_ms >= end_epoch_ms:
            raise ValueError(
                "TiDB metric capture window must be positive: "
                f"run_id={self.run_id!r}, start_epoch_ms={start_epoch_ms}, end_epoch_ms={end_epoch_ms}"
            )
        if step_seconds <= 0 or (end_epoch_ms - start_epoch_ms) % (step_seconds * 1000):
            raise ValueError(
                "TiDB metric capture window must align to a positive step: "
                f"run_id={self.run_id!r}, start_epoch_ms={start_epoch_ms}, "
                f"end_epoch_ms={end_epoch_ms}, step_seconds={step_seconds}"
            )
        self._sql_metric_sampler.raise_if_failed()
        expected_timestamps = tuple(
            range(start_epoch_ms, end_epoch_ms + 1, step_seconds * 1000)
        )
        controller = self._import_controller
        frames: list[MetricFrame] = []
        lightning_metrics = {
            "lightning_progress",
            "lightning_throughput",
            "lightning_workers",
        }
        for raw_metric in metrics:
            metric = str(raw_metric).casefold()
            definition = self.metric_history_catalog().definition(metric)
            selected_targets = (
                metric_targets.get(metric)
                if metric_targets is not None
                else None
            )
            if metric == "workload_profile":
                targets = (None,)
            elif metric in lightning_metrics:
                job_target = lightning_job_id(self.run_id)
                if selected_targets is None or tuple(selected_targets) == (None,):
                    targets = (job_target,)
                elif tuple(selected_targets) == (job_target,):
                    targets = (job_target,)
                else:
                    raise ValueError(
                        "TiDB frozen-history Lightning capture requires one Case job target: "
                        f"metric={metric!r}, selected_targets={tuple(selected_targets)!r}, "
                        f"expected={job_target!r}"
                    )
            else:
                targets = (
                    tuple(selected_targets)
                    if selected_targets is not None
                    else self.metric_history_catalog().target_variants(metric, self.deployment)
                )
            if not targets or len(set(targets)) != len(targets):
                raise ValueError(
                    "TiDB metric capture target selection must be non-empty and unique: "
                    f"run_id={self.run_id!r}, metric={metric!r}, targets={targets!r}"
                )
            for target in targets:
                is_lightning = metric in lightning_metrics
                if (
                    is_lightning
                    and controller is not None
                    and controller.phase == "ready_to_import"
                ):
                    frame = MetricFrame(
                        metric=metric,
                        query_target=target,
                        step_seconds=step_seconds,
                        series={target: {
                            field: tuple(0.0 for _ in expected_timestamps)
                            for field in definition.value_fields
                        }},
                        timestamps_ms={target: expected_timestamps},
                    )
                else:
                    frame = self._metric_service.live.query(MetricQuery(
                        metric=metric,
                        target=target,
                        start_epoch_ms=start_epoch_ms,
                        end_epoch_ms=end_epoch_ms,
                        step_seconds=step_seconds,
                        rate_window_seconds=(
                            rate_windows.get(metric)
                            if rate_windows is not None
                            else None
                        ),
                    ))
                    if (
                        is_lightning
                        and controller is not None
                        and controller.phase == "reconfigure_required"
                    ):
                        frame = self._pad_stopped_lightning_frame(
                            frame,
                            expected_timestamps,
                            run_id=self.run_id,
                            metric=metric,
                            query_target=target,
                        )
                frame = self._align_metric_capture_to_grid(
                    frame,
                    expected_timestamps,
                    run_id=self.run_id,
                    metric=metric,
                    query_target=target,
                )
                validate_metric_frame(frame, self.metric_history_catalog())
                if is_lightning:
                    # 冻结历史报错会逐字枚举帧级 target；帧挂 job id 等于把事故身份
                    # 递给任何一次失败查询。事故与诱饵的判别只能在 series 层做。
                    frame = replace(frame, query_target=None)
                frames.append(frame)
        return tuple(frames)

    @staticmethod
    def _pad_stopped_lightning_frame(
        frame: MetricFrame,
        expected_timestamps: tuple[int, ...],
        *,
        run_id: str,
        metric: str,
        query_target: str | None,
    ) -> MetricFrame:
        if len(frame.series) != 1:
            raise RuntimeError(
                "Stopped Lightning metric must contain exactly one series: "
                f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}, "
                f"series={tuple(frame.series)!r}"
            )
        series_target, observed_fields = next(iter(frame.series.items()))
        observed_timestamps = frame.timestamps_ms[series_target]
        if not observed_timestamps:
            raise RuntimeError(
                "Stopped Lightning metric has no observed samples before handoff: "
                f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}"
            )
        expected_index = {timestamp: index for index, timestamp in enumerate(expected_timestamps)}
        if any(timestamp not in expected_index for timestamp in observed_timestamps):
            raise RuntimeError(
                "Stopped Lightning metric contains a sample outside the capture grid: "
                f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}, "
                f"observed_timestamps={observed_timestamps!r}, expected_timestamps={expected_timestamps!r}"
            )
        first_index = expected_index[observed_timestamps[0]]
        last_index = expected_index[observed_timestamps[-1]]
        expected_observed = expected_timestamps[first_index:last_index + 1]
        if observed_timestamps != expected_observed:
            raise RuntimeError(
                "Stopped Lightning metric has a gap while the container was observable: "
                f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}, "
                f"observed_timestamps={observed_timestamps!r}, expected_observed={expected_observed!r}"
            )
        padded_fields = {
            field: tuple(
                0.0 if index < first_index or index > last_index
                else values[index - first_index]
                for index, _ in enumerate(expected_timestamps)
            )
            for field, values in observed_fields.items()
        }
        return MetricFrame(
            metric=frame.metric,
            query_target=frame.query_target,
            step_seconds=frame.step_seconds,
            series={series_target: padded_fields},
            timestamps_ms={series_target: expected_timestamps},
        )

    @staticmethod
    def _metric_capture_tolerance_ms(step_seconds: int) -> int:
        """A sample may land at most 4 grid steps (never below 10s) away from its slot."""
        return max(4 * step_seconds, 10) * 1000

    def _align_metric_capture_to_grid(
        self,
        frame: MetricFrame,
        expected_timestamps: tuple[int, ...],
        *,
        run_id: str,
        metric: str,
        query_target: str | None,
    ) -> MetricFrame:
        if all(
            timestamps == expected_timestamps
            for timestamps in frame.timestamps_ms.values()
        ):
            return frame
        step_ms = frame.step_seconds * 1000
        tolerance_ms = self._metric_capture_tolerance_ms(frame.step_seconds)
        grid_start_ms = expected_timestamps[0]
        aligned_series: dict[str, dict[str, tuple[float, ...]]] = {}
        aligned_timestamps: dict[str, tuple[int, ...]] = {}
        for series_target, observed_timestamps in frame.timestamps_ms.items():
            if observed_timestamps == expected_timestamps:
                aligned_series[series_target] = dict(frame.series[series_target])
                aligned_timestamps[series_target] = expected_timestamps
                continue
            if not observed_timestamps:
                raise RuntimeError(
                    "TiDB metric capture series has no observed samples: "
                    f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}, "
                    f"series_target={series_target!r}, expected_timestamps={expected_timestamps!r}"
                )
            # One Prometheus-side scrape outage produces the same gap run
            # in every series at once, so each series carries its own
            # strike budget: a correlated outage counts once per series
            # instead of multiplying into a shared counter, and only
            # sustained degradation of one series fails the frame.
            strikes = SamplerGridStrikes()
            # Anchor every sample to its nearest grid slot. A sample beyond the
            # slot tolerance is skipped like a missed sample, and two candidates
            # for one slot keep the closer one — both count toward the shared
            # strike budget instead of failing the frame outright.
            assignments: dict[int, int] = {}
            skipped_samples = 0
            max_deviation_ms = 0
            for observed_index, timestamp in enumerate(observed_timestamps):
                raw_offset = round((timestamp - grid_start_ms) / step_ms)
                nearest_index = min(max(raw_offset, 0), len(expected_timestamps) - 1)
                deviation_ms = abs(timestamp - expected_timestamps[nearest_index])
                if deviation_ms > tolerance_ms:
                    skipped_samples += 1
                    continue
                if nearest_index in assignments:
                    incumbent_index, incumbent_deviation = assignments[nearest_index]
                    if deviation_ms < incumbent_deviation:
                        assignments[nearest_index] = observed_index
                        skipped_samples += 1
                    continue
                assignments[nearest_index] = observed_index
                max_deviation_ms = max(max_deviation_ms, deviation_ms)
            observed_fields = frame.series[series_target]
            gap_indices = [index for index in range(len(expected_timestamps)) if index not in assignments]
            if gap_indices:
                started_at_ms = self._restart_padded_target_started_at_ms(
                    series_target,
                    grid_start_ms,
                    expected_timestamps[-1],
                )
                # Contiguous missing-slot runs are one anomaly event each; a
                # stretch of at least SAMPLER_LAG_TOLERANCE_INTERVALS anchored
                # slots between events decays the count. Jitter padding fills
                # the skipped slots with 0.0; restart-explained padding keeps
                # its own provenance and does not strike.
                strike_detail = (
                    f"run_id={run_id!r}, metric={metric!r}, query_target={query_target!r}, "
                    f"series_target={series_target!r}, tolerance_ms={tolerance_ms}, "
                    f"skipped_samples={skipped_samples}"
                )
                anchored_run = 0
                gap_lookup = set(gap_indices)
                for index in range(len(expected_timestamps)):
                    if index in gap_lookup:
                        if anchored_run >= SAMPLER_LAG_TOLERANCE_INTERVALS:
                            strikes.decay()
                        anchored_run = 0
                        continue
                    anchored_run += 1
                for gap_run in self._contiguous_index_runs(gap_indices):
                    if started_at_ms is None:
                        strikes.strike(detail=strike_detail)
                        self._record_metric_capture_padding(
                            run_id=run_id,
                            metric=metric,
                            query_target=query_target,
                            series_target=series_target,
                            padded_timestamps_ms=tuple(
                                expected_timestamps[index] for index in gap_run
                            ),
                            container_started_at_ms=None,
                            max_reanchor_deviation_ms=max_deviation_ms,
                            reason="jitter",
                        )
                aligned_series[series_target] = {
                    field: tuple(
                        values[assignments[index]] if index in assignments else 0.0
                        for index in range(len(expected_timestamps))
                    )
                    for field, values in observed_fields.items()
                }
                aligned_timestamps[series_target] = expected_timestamps
                if started_at_ms is not None:
                    self._record_metric_capture_padding(
                        run_id=run_id,
                        metric=metric,
                        query_target=query_target,
                        series_target=series_target,
                        padded_timestamps_ms=tuple(
                            expected_timestamps[index] for index in gap_indices
                        ),
                        container_started_at_ms=started_at_ms,
                        max_reanchor_deviation_ms=max_deviation_ms,
                        reason="restart",
                    )
                continue
            aligned_series[series_target] = {
                field: tuple(values[assignments[index]] for index in range(len(expected_timestamps)))
                for field, values in observed_fields.items()
            }
            aligned_timestamps[series_target] = expected_timestamps
        return MetricFrame(
            metric=frame.metric,
            query_target=frame.query_target,
            step_seconds=frame.step_seconds,
            series=aligned_series,
            timestamps_ms=aligned_timestamps,
        )

    @staticmethod
    def _contiguous_index_runs(indices: list[int]) -> list[list[int]]:
        runs: list[list[int]] = []
        for index in indices:
            if runs and index == runs[-1][-1] + 1:
                runs[-1].append(index)
            else:
                runs.append([index])
        return runs

    def _restart_padded_target_started_at_ms(
        self,
        series_target: str,
        window_start_ms: int,
        window_end_ms: int,
    ) -> int | None:
        """Return when the target container last started if that start happened inside the window."""
        if series_target not in self.deployment.NODES:
            return None
        service = self.deployment.NODES[series_target]
        container_id = self.deployment._service_container_id(service)
        inspect = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.StartedAt}}", container_id],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if inspect.returncode != 0:
            raise RuntimeError(
                "TiDB metric capture could not read the container start time for restart padding: "
                f"series_target={series_target!r}, container_id={container_id!r}, "
                f"returncode={inspect.returncode}, stderr={inspect.stderr.strip()!r}"
            )
        started_at_ms = self._parse_docker_started_at_ms(inspect.stdout)
        if window_start_ms < started_at_ms <= window_end_ms:
            return started_at_ms
        return None

    @staticmethod
    def _parse_docker_started_at_ms(value: str) -> int:
        match = re.fullmatch(
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?Z",
            value.strip(),
        )
        if match is None:
            raise RuntimeError(
                f"Docker inspect returned an unparsable UTC StartedAt: value={value!r}"
            )
        started_at = datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        milliseconds = int((match.group(2) or "").ljust(3, "0")[:3] or 0)
        return int(started_at.timestamp()) * 1000 + milliseconds

    def _record_metric_capture_padding(
        self,
        *,
        run_id: str,
        metric: str,
        query_target: str | None,
        series_target: str,
        padded_timestamps_ms: tuple[int, ...],
        container_started_at_ms: int | None,
        max_reanchor_deviation_ms: int,
        reason: str,
    ) -> None:
        event = {
            "run_id": run_id,
            "metric": metric,
            "query_target": query_target,
            "series_target": series_target,
            "padded_timestamps_ms": padded_timestamps_ms,
            "fill_value": 0.0,
            "container_started_at_ms": container_started_at_ms,
            "max_reanchor_deviation_ms": max_reanchor_deviation_ms,
            "reason": reason,
        }
        self._metric_capture_padding_events.append(event)
        print(
            f">>> [TiDBEnv] Padded {len(padded_timestamps_ms)} restart-gap sample(s) with 0.0 for "
            f"{metric!r}/{series_target!r}: padded_timestamps_ms={padded_timestamps_ms!r}, "
            f"container_started_at_ms={container_started_at_ms}"
        )

    @property
    def metric_capture_padding_events(self) -> tuple[dict[str, object], ...]:
        """Deterministic restart-padding metadata recorded during metric capture."""
        return tuple(self._metric_capture_padding_events)


    def finalize_metric_history_capture(self, start_epoch_ms: int, end_epoch_ms: int) -> None:
        controller = self._import_controller
        if controller is not None:
            status = controller.status()
            if status["import"]["state"] != "reconfigure_required":
                raise RuntimeError(
                    "TiDB frozen-history Lightning target capture did not finish at checkpoint handoff: "
                    f"run_id={self.run_id!r}, start_epoch_ms={start_epoch_ms}, "
                    f"end_epoch_ms={end_epoch_ms}, status={status!r}"
                )
        self._sql_metric_sampler.stop()
        self._sql_metric_sampler.raise_if_failed()
        self._pd_metric_sampler.stop()

    def _capture_workload_profile_metric(self, query: MetricQuery) -> MetricFrame:
        runner = self._workload_runner
        if runner is None:
            raise RuntimeError(
                f"TiDB workload_profile history requires an attached WorkloadRunner: run_id={self.run_id!r}"
            )
        spec = self._case.frozen_history
        selected = spec.metric_targets.get("workload_profile")
        if selected is not None and tuple(selected) != (None,):
            raise ValueError(
                "TiDB workload_profile capture only accepts target=None and uses the Case frontend profiles: "
                f"selected_targets={tuple(selected)!r}"
            )
        profile_names = tuple(
            profile.name
            for profile in self._case.background_workload.profiles
            if profile.tier == "FRONTEND_SLO"
        )
        if query.start_epoch_ms is None or query.end_epoch_ms is None:
            raise ValueError(
                f"TiDB workload_profile history requires an explicit capture window: query={query!r}"
            )
        return runner.capture_profile_metric(
            start_epoch_ms=query.start_epoch_ms,
            end_epoch_ms=query.end_epoch_ms,
            step_seconds=query.step_seconds or spec.base_step_seconds,
            profile_names=profile_names,
        )

    def capture_history_records(
        self,
        sources: tuple[HistoricalRecordSource, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
    ) -> CapturedRecords:
        point_records = []
        interval_records = []
        coverage = []
        if HistoricalRecordSource.COMPONENT_LOG in sources:
            for target in self.deployment.list_nodes():
                if target.startswith("monitoring/"):
                    continue
                raw = self.deployment.read_logs_at_range(target, start_epoch_ms, end_epoch_ms)
                point_records.extend(parse_docker_log_records(raw, target, start_epoch_ms, end_epoch_ms))
                coverage.append(HistoricalCoverage(
                    source=HistoricalRecordSource.COMPONENT_LOG,
                    target=target,
                    start_ms=start_epoch_ms,
                    end_ms=end_epoch_ms,
                ))
            controller = self._import_controller
            if controller is not None:
                raw = controller.history_log_output(start_epoch_ms, end_epoch_ms)
                if raw is None:
                    raise RuntimeError(
                        f"Lightning controller did not provide history logs: run_id={self.run_id!r}, "
                        f"window=({start_epoch_ms},{end_epoch_ms})"
                    )
                target = "lightning/lightning-0"
                point_records.extend(
                    parse_docker_log_records(raw, target, start_epoch_ms, end_epoch_ms)
                )
                coverage.append(HistoricalCoverage(
                    source=HistoricalRecordSource.COMPONENT_LOG,
                    target=target,
                    start_ms=start_epoch_ms,
                    end_ms=end_epoch_ms,
                ))
        if HistoricalRecordSource.TOPSQL in sources:
            rows = self._query_rows(
                "SELECT INSTANCE, RESOURCE_GROUP, DIGEST, PLAN_DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY, "
                "AVG_TOTAL_KEYS, AVG_PROCESSED_KEYS, AVG_MEM, MAX_MEM, AVG_DISK, MAX_DISK, "
                "SUMMARY_BEGIN_TIME, SUMMARY_END_TIME "
                "FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY_HISTORY "
                "WHERE SUMMARY_END_TIME >= FROM_UNIXTIME(%s) AND SUMMARY_BEGIN_TIME <= FROM_UNIXTIME(%s) "
                "UNION ALL "
                "SELECT INSTANCE, RESOURCE_GROUP, DIGEST, PLAN_DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY, "
                "AVG_TOTAL_KEYS, AVG_PROCESSED_KEYS, AVG_MEM, MAX_MEM, AVG_DISK, MAX_DISK, "
                "SUMMARY_BEGIN_TIME, SUMMARY_END_TIME "
                "FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY "
                "WHERE SUMMARY_END_TIME >= FROM_UNIXTIME(%s) AND SUMMARY_BEGIN_TIME <= FROM_UNIXTIME(%s)",
                (start_epoch_ms / 1000, end_epoch_ms / 1000, start_epoch_ms / 1000, end_epoch_ms / 1000),
            )
            interval_records.extend(build_topsql_records(rows, "cluster", start_epoch_ms, end_epoch_ms))
            coverage.append(HistoricalCoverage(
                source=HistoricalRecordSource.TOPSQL,
                target="cluster",
                start_ms=start_epoch_ms,
                end_ms=end_epoch_ms,
            ))
        if HistoricalRecordSource.SLOW_QUERIES in sources:
            rows = self._query_rows(
                "SELECT TIME, INSTANCE, DIGEST, QUERY, QUERY_TIME, PROCESS_TIME, WAIT_TIME, BACKOFF_TIME, "
                "TOTAL_KEYS, PROCESS_KEYS, MEM_MAX, DISK_MAX "
                "FROM INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY "
                "WHERE TIME BETWEEN FROM_UNIXTIME(%s) AND FROM_UNIXTIME(%s)",
                (start_epoch_ms / 1000, end_epoch_ms / 1000),
            )
            point_records.extend(build_slow_query_records(rows, "cluster", start_epoch_ms, end_epoch_ms))
            coverage.append(HistoricalCoverage(
                source=HistoricalRecordSource.SLOW_QUERIES,
                target="cluster",
                start_ms=start_epoch_ms,
                end_ms=end_epoch_ms,
            ))
        return CapturedRecords(
            point_records=tuple(point_records),
            interval_records=tuple(interval_records),
            coverage=tuple(coverage),
        )

    def register_sql_connection_surface(
        self,
        name: str,
        *,
        database: str,
        description: str,
        query_examples: Sequence[str],
        write_policy: str = "unrestricted",
    ) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValueError(f"Invalid SQL connection surface name: name={name!r}")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", database):
            raise ValueError(
                f"Invalid SQL connection surface database: name={name!r}, database={database!r}"
            )
        if not description.strip():
            raise ValueError(f"SQL connection surface description is empty: name={name!r}")
        examples = tuple(query_examples)
        if not examples or any(not example.strip() for example in examples):
            raise ValueError(
                f"SQL connection surface requires non-empty query examples: name={name!r}"
            )
        if write_policy not in {"unrestricted", "dm_action", "read_only"}:
            raise ValueError(
                f"Unsupported SQL connection surface write policy: name={name!r}, "
                f"write_policy={write_policy!r}"
            )
        if name in {"primary", "replica", "downstream"} or name in self.deployment.tidb_endpoints:
            raise ValueError(f"SQL connection surface name is reserved: name={name!r}")
        surface = SqlConnectionSurface(
            name=name,
            database=database,
            description=description,
            query_examples=examples,
            write_policy=write_policy,
        )
        existing = self._sql_connection_surfaces.get(name)
        if existing is not None and existing != surface:
            raise RuntimeError(
                f"SQL connection surface registration conflicts: name={name!r}, "
                f"existing={existing!r}, requested={surface!r}"
            )
        self._sql_connection_surfaces[name] = surface

    @staticmethod
    def _sql_mutation_candidate(sql_query: str) -> bool:
        return bool(re.search(
            r"(?:^|;)\s*(?:ALTER|CREATE|DROP|TRUNCATE|INSERT|UPDATE|DELETE|REPLACE|MERGE|CALL|GRANT|REVOKE|WITH)\b",
            sql_query,
            re.IGNORECASE,
        ))

    @staticmethod
    def _is_read_only_sql_statement(statement: exp.Expression) -> bool:
        return statement.key in {"select", "show", "describe", "explain"}

    @staticmethod
    def _is_dm_action_insert(statement: exp.Expression) -> bool:
        if not isinstance(statement, exp.Insert):
            return False
        target = statement.this.this if isinstance(statement.this, exp.Schema) else statement.this
        if not isinstance(target, exp.Table):
            return False
        return target.name.casefold() == "dm_actions" and (
            not target.db or target.db.casefold() == "dm_control"
        )

    @classmethod
    def _validate_sql_write_policy(
        cls,
        sql_query: str,
        *,
        surface: SqlConnectionSurface,
        allow_action_insert: bool,
    ) -> None:
        if not cls._sql_mutation_candidate(sql_query):
            return
        try:
            statements = parse(sql_query, read="mysql")
        except ParseError as exc:
            raise ValueError(
                f"SQL write-policy validation could not parse query: "
                f"surface={surface.name!r}, query={sql_query!r}, error={exc}"
            ) from exc
        if not statements:
            raise ValueError(
                f"SQL write-policy validation found no statement: surface={surface.name!r}, "
                f"query={sql_query!r}"
            )
        if all(cls._is_read_only_sql_statement(statement) for statement in statements):
            return
        if allow_action_insert and len(statements) == 1 and cls._is_dm_action_insert(statements[0]):
            return
        raise ValueError(
            f"SQL write policy rejected mutation: surface={surface.name!r}, "
            f"write_policy={surface.write_policy!r}; only a single INSERT INTO dm_actions "
            "is writable"
        )

    @classmethod
    def _validate_registered_sql_write_policies(
        cls,
        sql_query: str,
        *,
        selected_target: str,
        surfaces: Dict[str, SqlConnectionSurface],
    ) -> None:
        selected_surface = surfaces.get(selected_target)
        if selected_surface is not None and selected_surface.write_policy != "unrestricted":
            cls._validate_sql_write_policy(
                sql_query,
                surface=selected_surface,
                allow_action_insert=True,
            )
        for surface in surfaces.values():
            if surface.write_policy == "unrestricted" or surface is selected_surface:
                continue
            database_pattern = rf"(?:`{re.escape(surface.database)}`|{re.escape(surface.database)})\s*\."
            use_pattern = rf"\bUSE\s+(?:`{re.escape(surface.database)}`|{re.escape(surface.database)})\b"
            database_ddl_pattern = (
                rf"\b(?:ALTER|CREATE|DROP)\s+(?:DATABASE|SCHEMA)\s+"
                rf"(?:IF\s+(?:NOT\s+)?EXISTS\s+)?"
                rf"(?:`{re.escape(surface.database)}`|{re.escape(surface.database)})\b"
            )
            if (
                re.search(database_pattern, sql_query, re.IGNORECASE)
                or re.search(use_pattern, sql_query, re.IGNORECASE)
                or re.search(database_ddl_pattern, sql_query, re.IGNORECASE)
            ):
                cls._validate_sql_write_policy(
                    sql_query,
                    surface=surface,
                    allow_action_insert=False,
                )

    def unregister_sql_connection_surface(self, name: str) -> None:
        if name not in self._sql_connection_surfaces:
            raise ValueError(f"SQL connection surface is not registered: name={name!r}")
        del self._sql_connection_surfaces[name]

    def set_sql_connection_surface_write_policy(self, name: str, write_policy: str) -> None:
        if name not in self._sql_connection_surfaces:
            raise ValueError(f"SQL connection surface is not registered: name={name!r}")
        if write_policy not in {"unrestricted", "dm_action", "read_only"}:
            raise ValueError(
                f"Unsupported SQL connection surface write policy: name={name!r}, "
                f"write_policy={write_policy!r}"
            )
        surface = self._sql_connection_surfaces[name]
        self._sql_connection_surfaces[name] = SqlConnectionSurface(
            name=surface.name,
            database=surface.database,
            description=surface.description,
            query_examples=surface.query_examples,
            write_policy=write_policy,
        )

    def _sql_connection_surface_help(self) -> list[dict[str, Any]]:
        surfaces = [
            {
                "name": "primary",
                "kind": "tidb_endpoint",
                "database": self.dbname,
                "description": "默认 TiDB SQL endpoint；查询当前集群业务数据、information_schema 和 TiDB 系统表。",
                "query_examples": [
                    "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables",
                    "SELECT ... FROM <observed_table>",
                ],
            },
        ]
        if self._secondary_host is not None:
            surfaces.append({
                "name": "replica",
                "kind": "tidb_endpoint",
                "database": self.dbname,
                "description": "已配置的第二个 TiDB SQL endpoint；用于读取副本侧 schema、数据和状态。",
                "query_examples": [
                    "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables",
                    "SELECT ... FROM <observed_table>",
                ],
            })
        for target in sorted(self.deployment.tidb_endpoints):
            surfaces.append({
                "name": target,
                "kind": "tidb_endpoint",
                "database": self.dbname,
                "description": "指定 TiDB SQL endpoint；用于比较该实例的 SQL 可见状态。",
                "query_examples": [
                    "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables",
                    "SELECT ... FROM <observed_table>",
                ],
            })
        if getattr(self.deployment, "downstream_port", None) is not None:
            surfaces.append({
                "name": "downstream",
                "kind": "database_endpoint",
                "description": "复制运行时的独立下游数据库 endpoint；用于读取下游 schema、业务数据和复制结果。",
                "query_examples": [
                    "SHOW DATABASES",
                    "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables",
                    "SELECT ... FROM <observed_table>",
                ],
            })
        surfaces.extend(
            self._surface_help_payload(surface)
            for surface in self._sql_connection_surfaces.values()
        )
        return surfaces

    @staticmethod
    def _surface_help_payload(surface: SqlConnectionSurface) -> dict[str, object]:
        payload = {
            "name": surface.name,
            "kind": "frozen_history" if surface.name == "history" else "database",
            "database": surface.database,
            "description": surface.description,
            "query_examples": list(surface.query_examples),
        }
        if surface.write_policy != "unrestricted":
            payload["write_policy"] = surface.write_policy
        return payload

    def _additional_tool_help(self, tool_name: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        history_spec = getattr(getattr(self, "_case", None), "frozen_history", None)
        if tool_name == "query_metrics" and history_spec is not None:
            result["runtime"] = {
                "allowed_metrics": [
                    str(metric).casefold() for metric in history_spec.required_metrics
                ],
            }
        if tool_name == "execute_sql":
            result["runtime"] = {
                "connection_surfaces": self._sql_connection_surface_help(),
            }
        if tool_name in {"query_metrics", "execute_sql"} and self._history_timeline is not None:
            spec = self._case.frozen_history
            result.setdefault("runtime", {}).update({
                "timezone": "UTC",
                "available_start": format_utc_timestamp(self._history_timeline.visible_start_ms),
                "available_end": format_utc_timestamp(self._history_timeline.visible_end_ms),
                "base_step_seconds": self._history_timeline.base_step_seconds,
                "overview_step_seconds": self._history_timeline.overview_step_seconds,
                "enabled_sources": [source.value for source in spec.record_sources],
                "max_history_records_per_response": spec.max_history_records_per_response,
            })
        return result

    def _pd_store(self, target: str) -> dict:
        service = target.rsplit("/", 1)[-1]
        stores = self.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
        matches = [
            item["store"] | {"status": item["status"]}
            for item in stores
            if service == str(item["store"]["address"]).split(":", 1)[0]
        ]
        if len(matches) == 1:
            store = matches[0]
            self._known_store_ids[service] = int(store["id"])
            return store
        if len(matches) > 1:
            raise ValueError(
                f"TiDB target does not resolve to exactly one PD store: target={target!r}, "
                f"matches={matches!r}"
            )
        store_id = self._known_store_ids.get(service)
        if store_id is None:
            raise ValueError(
                f"TiDB target is absent from active PD stores and has no observed Store ID: "
                f"target={target!r}, known_store_ids={self._known_store_ids!r}"
            )
        payload = self.deployment.pd_request("GET", f"/pd/api/v1/store/{store_id}")
        store = payload["store"] | {"status": payload["status"]}
        if str(store["address"]).split(":", 1)[0] != service:
            raise ValueError(
                f"PD Store identity changed while resolving target: target={target!r}, "
                f"expected_service={service!r}, observed_store={store!r}"
            )
        return store

    def _remember_pd_stores(self, payload: dict) -> None:
        for item in payload["stores"]:
            service = str(item["store"]["address"]).split(":", 1)[0]
            self._known_store_ids[service] = int(item["store"]["id"])

    @staticmethod
    def _mvcc_region_id(target: str) -> int:
        match = re.fullmatch(r"region/([1-9][0-9]*)", str(target))
        if match is None:
            raise ValueError(f"MVCC target must use region/<positive-id>: target={target!r}")
        return int(match.group(1))

    def _mvcc_gc_phase_status(self) -> dict[str, Any]:
        phase_queries = {
            "gc_worker": '{__name__=~"tikv_.*gc.*"}',
            "resolve_locks": '{__name__=~".*resolve.*lock.*"}',
            "delete_ranges": '{__name__=~".*delete.*range.*"}',
            "do_gc": '{__name__=~".*do_gc.*"}',
        }
        prometheus = {
            phase: self._prometheus_instant_payload(query)
            for phase, query in phase_queries.items()
        }
        return {
            "prometheus_raw": prometheus,
        }

    def _changefeed_diagnostics(
        self,
        operation: str,
        capture_target: str,
        changefeed_id: str | None = None,
    ) -> dict[str, object]:
        if operation == "list":
            result = self.deployment.changefeed_diagnostics(capture_target)
            for item in result["changefeeds"]:
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    self._observed_changefeed_diagnostics[(capture_target, item["id"])] = item
            return result
        if changefeed_id is None:
            raise ValueError("changefeed diagnostics get requires changefeed_id")
        result = self.deployment.changefeed_diagnostics(capture_target, changefeed_id)
        self._observed_changefeed_diagnostics[(capture_target, changefeed_id)] = result["changefeeds"]
        return result

    def _gc_safepoint_list(self) -> dict[str, object]:
        result = self.deployment.gc_safepoint_list()
        self._observed_gc_safepoint = result
        return result

    def _gc_safepoint_remove(
        self,
        service_id: str,
        parameters: dict[str, Any],
    ) -> dict[str, object]:
        if set(parameters) != {"changefeed_id"}:
            raise ValueError(
                "gc_safepoint remove requires exactly parameters.changefeed_id: "
                f"service_id={service_id!r}, parameters={sorted(parameters)}"
            )
        if self._observed_gc_safepoint is None:
            raise ValueError("gc_safepoint remove requires a prior gc_safepoint list observation")
        changefeed_id = str(parameters["changefeed_id"])
        owners = [
            owner
            for owner in self._observed_gc_safepoint["service_gc_safe_points"]
            if isinstance(owner, dict) and str(owner.get("service_id")) == service_id
        ]
        if len(owners) != 1:
            raise ValueError(
                "gc_safepoint remove requires exactly one previously observed owner: "
                f"service_id={service_id!r}, matches={owners!r}"
            )
        owner_before_safe_point = int(owners[0]["safe_point"])
        workers_before = [
            owner
            for owner in self._observed_gc_safepoint["service_gc_safe_points"]
            if isinstance(owner, dict) and str(owner.get("service_id")) == "gc_worker"
        ]
        if len(workers_before) != 1:
            raise ValueError(
                "gc_safepoint remove requires exactly one previously observed gc_worker owner: "
                f"service_id={service_id!r}, workers={workers_before!r}"
            )
        worker_before_safe_point = int(workers_before[0]["safe_point"])
        if service_id == "gc_worker":
            raise ValueError("gc_safepoint remove cannot target gc_worker")
        capture_targets = sorted({
            capture_target
            for capture_target, observed_changefeed_id in self._observed_changefeed_diagnostics
            if observed_changefeed_id == changefeed_id
        })
        states = self.deployment.node_states()
        stopped_captures = sorted(
            target
            for target, state in states.items()
            if target.startswith("ticdc/") and not state["running"]
        )
        if capture_targets:
            if len(capture_targets) != 1:
                raise ValueError(
                    "gc_safepoint remove requires one observed capture for the exact changefeed: "
                    f"service_id={service_id!r}, changefeed_id={changefeed_id!r}, "
                    f"capture_targets={capture_targets!r}"
                )
            capture_target = capture_targets[0]
            if states.get(capture_target, {}).get("running"):
                if len(stopped_captures) != 1:
                    raise ValueError(
                        "gc_safepoint remove cannot uniquely bind the stopped owner capture: "
                        f"service_id={service_id!r}, changefeed_id={changefeed_id!r}, "
                        f"capture_target={capture_target!r}, stopped_captures={stopped_captures!r}"
                    )
                owner_runtime_target = stopped_captures[0]
            else:
                owner_runtime_target = capture_target
        else:
            # abandoned capture 处于停止状态，其 changefeed 无法经由任何合法观察
            # 进入 diagnostics 记录；此时 owner 只能绑定到当前唯一停止的 TiCDC capture。
            if len(stopped_captures) != 1:
                raise ValueError(
                    "gc_safepoint remove requires exactly one stopped TiCDC capture to bind the "
                    f"abandoned owner: service_id={service_id!r}, changefeed_id={changefeed_id!r}, "
                    f"stopped_captures={stopped_captures!r}"
                )
            capture_target = stopped_captures[0]
            owner_runtime_target = capture_target
        if owner_runtime_target not in states or not owner_runtime_target.startswith("ticdc/"):
            raise ValueError(
                "gc_safepoint remove owner_runtime_target is not a TiCDC service: "
                f"owner_runtime_target={owner_runtime_target!r}, states={sorted(states)!r}"
            )
        if states[owner_runtime_target]["running"]:
            raise ValueError(
                "gc_safepoint remove requires the mapped abandoned capture to be stopped: "
                f"owner_runtime_target={owner_runtime_target!r}, state={states[owner_runtime_target]!r}"
            )
        if capture_target not in states or not capture_target.startswith("ticdc/"):
            raise ValueError(
                "gc_safepoint remove capture_target is not a TiCDC service: "
                f"capture_target={capture_target!r}, states={sorted(states)!r}"
            )
        capture_was_stopped = not states[capture_target]["running"]
        if capture_was_stopped:
            if capture_target != owner_runtime_target:
                raise ValueError(
                    "gc_safepoint remove can only temporarily start the stopped owner capture: "
                    f"capture_target={capture_target!r}, owner_runtime_target={owner_runtime_target!r}"
                )
            self.deployment.start_component(capture_target)
            self.deployment._wait(
                capture_target,
                lambda: self.deployment.changefeed_diagnostics(capture_target, changefeed_id),
                180,
            )
        self._changefeed_diagnostics("get", capture_target, changefeed_id)
        before = self.deployment.gc_safepoint_list()
        result = self.deployment.remove_changefeed(capture_target, changefeed_id)

        def wait_for_owner_release() -> None:
            current = self.deployment.gc_safepoint_list()
            matches = [
                owner
                for owner in current["service_gc_safe_points"]
                if isinstance(owner, dict) and str(owner.get("service_id")) == service_id
            ]
            if len(matches) > 1:
                raise RuntimeError(
                    "TiCDC service GC safepoint has duplicate exact owners after changefeed removal: "
                    f"service_id={service_id!r}, changefeed_id={changefeed_id!r}, owners={matches!r}"
                )
            workers = [
                owner
                for owner in current["service_gc_safe_points"]
                if isinstance(owner, dict) and str(owner.get("service_id")) == "gc_worker"
            ]
            if len(workers) != 1:
                raise RuntimeError(
                    "TiCDC service GC safepoint cleanup requires exactly one gc_worker owner: "
                    f"service_id={service_id!r}, changefeed_id={changefeed_id!r}, workers={workers!r}"
                )
            feeds = self.deployment.changefeed_diagnostics(capture_target)["changefeeds"]
            if any(
                isinstance(feed, dict) and str(feed.get("id")) == changefeed_id
                for feed in feeds
            ):
                raise RuntimeError(
                    "TiCDC changefeed still exists after removal request: "
                    f"capture_target={capture_target!r}, changefeed_id={changefeed_id!r}, feeds={feeds!r}"
                )
            if matches:
                owner_safe_point = int(matches[0]["safe_point"])
                worker_safe_point = int(workers[0]["safe_point"])
                baseline_was_released = owner_before_safe_point >= worker_before_safe_point
                owner_advanced = owner_safe_point > owner_before_safe_point
                if owner_safe_point < worker_safe_point or not (baseline_was_released or owner_advanced):
                    raise RuntimeError(
                        "TiCDC service GC safepoint owner did not release after exact changefeed removal: "
                        f"service_id={service_id!r}, changefeed_id={changefeed_id!r}, "
                        f"owner_before={owner_before_safe_point}, owner_after={owner_safe_point}, "
                        f"worker_before={worker_before_safe_point}, worker_after={worker_safe_point}"
                    )

        self.deployment._wait(capture_target, wait_for_owner_release, 180)
        after = self.deployment.gc_safepoint_list()
        self._observed_gc_safepoint = after
        return {
            "service_id": service_id,
            "changefeed_id": changefeed_id,
            "owner_runtime_target": owner_runtime_target,
            "before": before,
            "cleanup": result,
            "after": after,
            "capture_started_for_cleanup": capture_was_stopped,
            "capture_running_after_cleanup": bool(
                self.deployment.node_states()[capture_target]["running"]
            ),
        }


    def base_snapshot_name(self, case) -> Optional[str]:
        return self.deployment.snapshots.base_image_snapshot_name()

    def snapshot_name(self, scenario_id: str, case) -> Optional[str]:
        return self.deployment.snapshots.image_group_snapshot_name()

    def disable_image_group(self) -> None:
        self.deployment.snapshots.disable_image_group()

    def snapshot_exists(self, snapshot_name: str) -> bool:
        return self.deployment.snapshots.image_group_exists(snapshot_name)

    def select_snapshot(self, snapshot_name: str, base_snapshot_name: str) -> None:
        self.deployment.snapshots.select_image_group(snapshot_name, base_snapshot_name)

    def save_snapshot(self, snapshot_name: str, labels: Dict[str, str]) -> None:
        self.deployment.snapshots.save_image_group(snapshot_name, labels)

    def _connect(
        self,
        database: Optional[str] = None,
        application_name: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        target: Optional[str] = None,
    ):
        if timeout_seconds is None:
            timeout_seconds = self.sql_timeout_seconds
        if target is None:
            host, port = self.host, self.port
        else:
            if target not in self.deployment.tidb_endpoints:
                raise ValueError(
                    f"Unknown TiDB SQL target {target!r}; "
                    f"expected one of {sorted(self.deployment.tidb_endpoints)}"
            )
            host, port = self.deployment.tidb_endpoints[target]
        return self._connect_at(
            host,
            port,
            database=database,
            application_name=application_name,
            read_timeout=timeout_seconds,
            write_timeout=timeout_seconds,
        )

    def _connect_at(
        self,
        host: str,
        port: int,
        *,
        database: Optional[str] = None,
        application_name: Optional[str] = None,
        read_timeout: int = SQL_TIMEOUT_SECONDS,
        write_timeout: int = SQL_TIMEOUT_SECONDS,
        password: Optional[str] = None,
    ):
        import pymysql
        from pymysql.constants import CLIENT

        conn = pymysql.connect(
            host=host,
            port=port,
            user=self.user,
            password=self.password if password is None else password,
            database=database,
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=5,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            client_flag=CLIENT.MULTI_STATEMENTS,
        )
        if application_name:
            with conn.cursor() as cur:
                cur.execute("SET @aiopsbench_application_name = %s", (application_name,))
        return conn

    def deploy(self):
        if self.workload is not None:
            self.workload.prepare()
        self.deployment.deploy()
        if not isinstance(self.deployment, TiDBDockerDeployment):
            raise TypeError(
                f"TiDBEnv requires TiDBDockerDeployment for deploy, got {type(self.deployment).__name__}"
            )
        try:
            if self.deployment.snapshots.image_group_reused:
                print(
                    f"[Env:TiDBEnv] Skipping init SQL because TiDB data image was reused: "
                    f"snapshot={self.deployment.snapshots.image_group_name!r}, "
                    f"image_group_key={self.deployment.snapshots.image_group_key!r}"
                )
            elif self.deployment.snapshots.persistent_state_reused:
                print(
                    f"[Env:TiDBEnv] Skipping init SQL because persistent baseline was reused: "
                    f"storage_key={self.deployment.snapshots.storage_key!r}"
                )
            else:
                self._execute_init_sql()
                if self.deployment.snapshots.persistent_storage_enabled:
                    self.deployment.snapshots.persist_initial_state()
        finally:
            self.deployment.snapshots.release_persistence_lock()
            self.deployment.snapshots.release_image_group_lock()
        self.reconnect()
        self._visible_since = time.time()
        self._log_visible_lines = {
            target: len(self.deployment.read_logs(target, lines=10000).splitlines())
            for target in self.deployment.list_nodes()
        }

    def _execute_init_sql(self):
        if self.workload is None:
            conn = self._connect(
                timeout_seconds=self.BOOTSTRAP_SQL_TIMEOUT_SECONDS,
            )
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.dbname}")
            conn.close()
            return
        path = self.workload.get_init_sql_path()
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"TiDB init SQL not found: run_id={self.run_id!r}, path={path!r}"
            )
        with open(path, encoding="utf-8") as handle:
            sql = handle.read()
        conn = self._connect(
            timeout_seconds=self.BOOTSTRAP_SQL_TIMEOUT_SECONDS,
        )
        with conn.cursor() as cur:
            cur.execute(sql)
            while cur.nextset():
                pass
        conn.close()

    def teardown(self):
        self._sql_metric_sampler.stop()
        self._pd_metric_sampler.stop()
        self._stop_workload_runner()
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        if self._secondary_conn is not None:
            self._secondary_conn.close()
            self._secondary_conn = None
        self._secondary_password = None
        if self._history_sql_archive is not None:
            self._history_sql_archive.close()
            self._history_sql_archive = None
        self.deployment.teardown()

    def _ensure_connection(self, target: str = "primary"):
        if target == "primary":
            if self._conn is not None:
                try:
                    self._conn.ping(reconnect=False)
                    return self._conn
                except Exception:
                    self._conn.close()
                    self._conn = None
            self._conn = self._connect(
                self.dbname,
                timeout_seconds=self.sql_timeout_seconds,
            )
            return self._conn
        if target == "replica":
            if (
                self._secondary_host is None
                or self._secondary_port is None
                or self._secondary_password is None
            ):
                raise RuntimeError(
                    f"TiDB secondary endpoint is not configured: run_id={self.run_id!r}"
                )
            if self._secondary_conn is not None:
                try:
                    self._secondary_conn.ping(reconnect=False)
                    return self._secondary_conn
                except Exception:
                    self._secondary_conn.close()
                    self._secondary_conn = None
            self._secondary_conn = self._connect_at(
                self._secondary_host,
                self._secondary_port,
                database=self.dbname,
                read_timeout=self.sql_timeout_seconds,
                write_timeout=self.sql_timeout_seconds,
                password=self._secondary_password,
            )
            return self._secondary_conn
        raise ValueError(
            f"Unsupported TiDB SQL target {target!r}; expected 'primary' or 'replica'"
        )

    def configure_secondary_endpoint(self, host: str, port: int, password: str) -> None:
        if self._secondary_conn is not None:
            self._secondary_conn.close()
            self._secondary_conn = None
        self._secondary_host = host
        self._secondary_port = int(port)
        self._secondary_password = password

    def clear_secondary_endpoint(self) -> None:
        if self._secondary_conn is not None:
            self._secondary_conn.close()
            self._secondary_conn = None
        self._secondary_host = None
        self._secondary_port = None
        self._secondary_password = None

    def configure_replication_endpoint(
        self,
        host: str,
        port: int,
        changefeed_id: str,
        container_name: str,
        downstream_container_name: str,
        *,
        target: str,
        max_cpu_limit: float,
        max_downstream_cpu_limit: float,
        sink_uri: str,
    ) -> None:
        parsed_sink_uri = urlsplit(str(sink_uri))
        sink_parameters = dict(parse_qsl(parsed_sink_uri.query, keep_blank_values=True))
        required_parameters = {"worker-count", "max-txn-row", "batch-dml-enable"}
        missing_parameters = sorted(required_parameters - sink_parameters.keys())
        if missing_parameters:
            raise ValueError(
                "TiDB replication endpoint sink URI is missing execution parameters: "
                f"changefeed_id={changefeed_id!r}, missing={missing_parameters!r}, sink_uri={sink_uri!r}"
            )
        self._replication_endpoint = {
            "host": host,
            "port": int(port),
            "changefeed_id": changefeed_id,
            "container_name": container_name,
            "downstream_container_name": downstream_container_name,
            "target": target,
            "max_cpu_limit": float(max_cpu_limit),
            "max_downstream_cpu_limit": float(max_downstream_cpu_limit),
            "sink_uri": str(sink_uri),
        }

    def clear_replication_endpoint(self) -> None:
        self._replication_endpoint = None

    def current_tso(self) -> int:
        conn = self._connect()
        try:
            conn.begin()
            with conn.cursor() as cur:
                cur.execute("SELECT @@tidb_current_ts AS current_tso")
                rows = cur.fetchall()
            conn.rollback()
        finally:
            conn.close()
        if len(rows) != 1 or len(rows[0]) != 1:
            raise RuntimeError(
                f"TiDB current TSO query returned an invalid result: run_id={self.run_id!r}, rows={rows!r}"
            )
        tso = int(rows[0][0])
        if tso <= 0:
            raise RuntimeError(
                f"TiDB current TSO must be positive after starting a transaction: run_id={self.run_id!r}, tso={tso}"
            )
        return tso

    def _replication_metric(self) -> str:
        if self._replication_endpoint is None:
            raise RuntimeError(f"TiCDC endpoint is not configured: run_id={self.run_id!r}")
        from urllib.request import urlopen

        endpoint = self._replication_endpoint
        url = (
            f"http://{endpoint['host']}:{endpoint['port']}/api/v1/changefeeds/"
            f"{endpoint['changefeed_id']}"
        )
        with urlopen(url, timeout=5) as response:
            changefeed = json.load(response)
        source_tso = self.current_tso()
        checkpoint_tso = int(changefeed["checkpoint_tso"])
        if checkpoint_tso <= 0:
            raise RuntimeError(
                f"TiCDC checkpoint TSO must be positive: changefeed_id={endpoint['changefeed_id']!r}, "
                f"checkpoint_tso={checkpoint_tso}"
            )
        if source_tso < checkpoint_tso:
            raise RuntimeError(
                f"TiDB current TSO is older than TiCDC checkpoint: changefeed_id={endpoint['changefeed_id']!r}, "
                f"source_tso={source_tso}, checkpoint_tso={checkpoint_tso}"
            )
        source_physical_ms = source_tso >> 18
        checkpoint_physical_ms = checkpoint_tso >> 18
        lag_seconds = round((source_physical_ms - checkpoint_physical_ms) / 1000, 3)
        if lag_seconds < 0:
            raise RuntimeError(
                f"TiCDC checkpoint lag must be non-negative: changefeed_id={endpoint['changefeed_id']!r}, "
                f"source_tso={source_tso}, checkpoint_tso={checkpoint_tso}, lag_seconds={lag_seconds}"
            )
        return self._metric_success(
            "replication",
            "snapshot",
            snapshot={
                "changefeed_id": endpoint["changefeed_id"],
                "replication_target": endpoint["target"],
                "state": changefeed["state"],
                "error": changefeed.get("error"),
                "upstream_tso": source_tso,
                "checkpoint_tso": checkpoint_tso,
                "checkpoint_time": changefeed["checkpoint_time"],
                "lag_seconds": lag_seconds,
            },
        )

    def _replication_cpu_limit(self) -> float:
        if self._replication_endpoint is None:
            raise RuntimeError(f"TiCDC endpoint is not configured: run_id={self.run_id!r}")
        endpoint = self._replication_endpoint
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.HostConfig.NanoCpus}}", endpoint["container_name"]],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"TiCDC CPU limit query failed: target={endpoint['target']!r}, "
                f"container={endpoint['container_name']!r}, stdout={result.stdout.strip()!r}, "
                f"stderr={result.stderr.strip()!r}"
            )
        nano_cpus = int(result.stdout.strip())
        if nano_cpus <= 0:
            raise RuntimeError(
                f"TiCDC CPU limit must be positive: target={endpoint['target']!r}, "
                f"container={endpoint['container_name']!r}, nano_cpus={nano_cpus}"
            )
        return round(nano_cpus / 1_000_000_000, 3)

    def _replication_downstream_cpu_limit(self) -> float:
        if self._replication_endpoint is None:
            raise RuntimeError(f"TiCDC endpoint is not configured: run_id={self.run_id!r}")
        endpoint = self._replication_endpoint
        result = subprocess.run(
            [
                "docker",
                "inspect",
                "--format",
                "{{.HostConfig.NanoCpus}}",
                endpoint["downstream_container_name"],
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"TiCDC downstream CPU limit query failed: target='downstream/mysql-0', "
                f"container={endpoint['downstream_container_name']!r}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        nano_cpus = int(result.stdout.strip())
        if nano_cpus <= 0:
            raise RuntimeError(
                "TiCDC downstream CPU limit must be positive: "
                f"target='downstream/mysql-0', container={endpoint['downstream_container_name']!r}, "
                f"nano_cpus={nano_cpus}"
            )
        return round(nano_cpus / 1_000_000_000, 3)

    def reconnect(self):
        if self._conn is not None:
            self._conn.close()
        self._conn = self._connect(self.dbname)
        return self._conn

    def open_workload_connection(
        self,
        application_name: str,
        connection_pool: Optional[str] = None,
        *,
        target: Optional[str] = None,
    ):
        if connection_pool is not None and target is not None:
            raise ValueError(
                "TiDB workload connection cannot select both a connection pool and a target: "
                f"application_name={application_name!r}, connection_pool={connection_pool!r}, "
                f"target={target!r}"
            )
        if target is not None:
            if target == "replica":
                return self._connect_at(
                    self._secondary_host,
                    self._secondary_port,
                    database=self.dbname,
                    application_name=application_name,
                    password=self._secondary_password,
                )
            return self._connect(self.dbname, application_name, target=target)
        if not self._connection_routers:
            if connection_pool is not None:
                raise ValueError(
                    "TiDB workload connection pool is not configured: "
                    f"application_name={application_name!r}, connection_pool={connection_pool!r}"
                )
            return self._connect(self.dbname, application_name)
        if connection_pool is None:
            if len(self._connection_routers) != 1:
                raise ValueError(
                    "TiDB workload connection pool is required when multiple routers exist: "
                    f"application_name={application_name!r}, pools={sorted(self._connection_routers)}"
                )
            connection_pool = next(iter(self._connection_routers))
        router = self._connection_routers[connection_pool]
        target = router.target_for_new_connection()
        host, port = self.deployment.tidb_endpoints[target]
        connection = self._connect_at(
            host,
            port,
            database=self.dbname,
            application_name=application_name,
        )
        router.register_connection(connection, target)
        self._connection_router_connections[id(connection)] = connection_pool
        return connection

    def close_workload_connection(self, connection) -> None:
        self._workload_session_setups.pop(id(connection), None)
        connection_pool = self._connection_router_connections.pop(id(connection), None)
        if connection_pool is not None:
            self._connection_routers[connection_pool].release_connection(connection)
        if connection.open:
            connection.close()

    def should_recycle_workload_connection(self, connection) -> bool:
        connection_pool = self._connection_router_connections.get(id(connection))
        if connection_pool is None:
            return False
        return self._connection_routers[connection_pool].should_recycle(connection)

    def invalidate_workload_connections(self) -> None:
        """Invalidate application connections after an internal control-plane write."""
        for router in self._connection_routers.values():
            router.invalidate_connections()
        self._workload_connection_invalidation_generation += 1

    def workload_connection_invalidation_generation(self) -> int:
        return self._workload_connection_invalidation_generation

    def open_long_running_connection(self, application_name: str):
        return self._connect(
            self.dbname,
            application_name,
            timeout_seconds=300,
        )




    def initialize_connection_routers(self, routers: Dict[str, Dict[str, object]]) -> None:
        if self._connection_routers:
            raise RuntimeError(
                f"TiDB connection routers are already initialized: run_id={self.run_id!r}"
            )
        self._connection_routers = {
            name: TiDBConnectionRouter(
                self.deployment.tidb_endpoints,
                str(config["initial_target"]),
            )
            for name, config in routers.items()
        }

    def connection_router_status(self, router_name: str) -> dict[str, object]:
        if router_name not in self._connection_routers:
            raise RuntimeError(
                f"Unknown TiDB connection router: run_id={self.run_id!r}, "
                f"router={router_name!r}, routers={sorted(self._connection_routers)}"
            )
        return self._connection_routers[router_name].status()

    def connection_router_statuses(self) -> Dict[str, dict[str, object]]:
        if not self._connection_routers:
            raise RuntimeError(
                f"TiDB connection routers are not initialized: run_id={self.run_id!r}"
            )
        return {
            name: router.status()
            for name, router in self._connection_routers.items()
        }

    def set_connection_router_policy(self, router_name: str, policy: str) -> dict[str, object]:
        if router_name not in self._connection_routers:
            raise ValueError(
                f"Unknown TiDB connection router: run_id={self.run_id!r}, "
                f"router={router_name!r}, routers={sorted(self._connection_routers)}"
            )
        return self._connection_routers[router_name].set_policy(policy)

    def register_connection_router_invalidation(
        self,
        name: str,
        *,
        tables: Sequence[str],
        routers: Sequence[str],
    ) -> None:
        normalized_tables = frozenset(str(table).casefold() for table in tables)
        router_names = tuple(str(router) for router in routers)
        missing = sorted(set(router_names) - set(self._connection_routers))
        if missing:
            raise ValueError(
                "TiDB router invalidation references unknown routers: "
                f"name={name!r}, missing={missing!r}, routers={sorted(self._connection_routers)!r}"
            )
        rule = (normalized_tables, router_names)
        existing = self._connection_router_invalidation_rules.get(name)
        if existing is not None and existing != rule:
            raise RuntimeError(
                "TiDB router invalidation registration conflicts: "
                f"name={name!r}, existing={existing!r}, requested={rule!r}"
            )
        self._connection_router_invalidation_rules[name] = rule

    def unregister_connection_router_invalidation(self, name: str) -> None:
        if name not in self._connection_router_invalidation_rules:
            raise ValueError(f"TiDB router invalidation is not registered: name={name!r}")
        del self._connection_router_invalidation_rules[name]

    def _invalidate_connection_routers_for_sql(self, sql_query: str) -> None:
        if not self._connection_router_invalidation_rules:
            return
        if re.match(r"^\s*(?:INSERT|UPDATE|DELETE)\b", sql_query, re.IGNORECASE) is None:
            return
        from sqlglot import exp, parse

        mutated_tables = set()
        for statement in parse(sql_query, read="mysql"):
            if not isinstance(statement, (exp.Insert, exp.Update, exp.Delete)):
                continue
            table = statement.find(exp.Table)
            if table is None:
                raise ValueError(f"TiDB mutation has no target table: sql={sql_query!r}")
            mutated_tables.add(
                f"{table.db}.{table.name}".casefold() if table.db else table.name.casefold()
            )
        invalidated = False
        for tables, routers in self._connection_router_invalidation_rules.values():
            if mutated_tables.isdisjoint(tables):
                continue
            for router_name in routers:
                self._connection_routers[router_name].invalidate_connections()
            invalidated = True
        if invalidated:
            self._workload_connection_invalidation_generation += 1

    def drain_connection_routers(self, target: str) -> Dict[str, dict[str, object]]:
        if not self._connection_routers:
            raise RuntimeError(
                f"TiDB connection routers are not initialized: run_id={self.run_id!r}"
            )
        for router in self._connection_routers.values():
            router.validate_drain(target)
        return {
            name: router.drain(target)
            for name, router in self._connection_routers.items()
        }

    def reset_connection_routers(self) -> None:
        if not self._connection_routers:
            raise RuntimeError(
                f"TiDB connection routers are not initialized: run_id={self.run_id!r}"
            )
        for router in self._connection_routers.values():
            router.reset()
        self._connection_router_connections.clear()
        self._connection_routers = {}

    def probe_database_backends(self) -> dict[str, object]:
        probes = {}
        for target, (host, port) in self.deployment.tidb_endpoints.items():
            connection = self._connect_at(
                host,
                port,
                database=self.dbname,
                application_name=f"rg08-backend-probe-{target.rsplit('/', 1)[1]}",
            )
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
            connection.close()
            if row != (1,):
                raise RuntimeError(
                    f"TiDB backend probe returned an unexpected result: target={target!r}, row={row!r}"
                )
            probes[target] = {"host": host, "port": port, "select_1": True}
        return probes

    def workload_activity_snapshot(self) -> dict[str, object]:
        if self._workload_runner is None:
            raise RuntimeError(
                f"TiDB workload runner is not attached: run_id={self.run_id!r}"
            )
        return self._workload_runner.get_activity(limit=50)

    def workload_activity_observation(self, limit: int = 50) -> str:
        if self._workload_runner is None:
            raise RuntimeError(f"TiDB workload runner is not attached: run_id={self.run_id!r}")
        activity = self._workload_runner.get_activity(limit=limit)
        return self._metric_success(
            "workload_activity",
            "snapshot",
            snapshot={
                "total_runs": activity["total_runs"],
                "active_profiles": activity["active_profiles"],
                "worker_count": activity["worker_count"],
                "window_seconds": activity["window_seconds"],
                "profiles": activity["value"],
            },
        )

    def cluster_info_observation(self) -> str:
        rows = self._query_rows(
            "SELECT TYPE, INSTANCE, VERSION, START_TIME, UPTIME "
            "FROM INFORMATION_SCHEMA.CLUSTER_INFO ORDER BY TYPE, INSTANCE"
        )
        return self._metric_success("cluster_info", "snapshot", snapshot={"nodes": rows})

    def node_health_observation(self) -> str:
        return self._metric_success(
            "node_health", "snapshot", snapshot={"nodes": self.deployment.node_states()}
        )

    def region_count_observation(self, target: Optional[str] = None) -> str:
        return self._region_count_metric(target, None, None)

    def region_health_observation(self) -> str:
        snapshot = self._region_health_snapshot()
        snapshot.update(self.deployment.stores.region_health_observation())
        return self._metric_success(
            "region_health",
            "snapshot",
            snapshot=snapshot,
        )

    def pd_scheduling_observation(self) -> str:
        return self._pd_scheduling_metric()

    def placement_progress_observation(self) -> str:
        rows = self._query_rows("SHOW PLACEMENT")
        return self._metric_success(
            "placement_progress", "snapshot", snapshot={"nodes": rows}
        )

    def replication_observation(self) -> str:
        return self._replication_metric()

    def ticdc_progress_observation(self, target: Optional[str] = None) -> str:
        if getattr(self.deployment, "replication_runtime", None) is not None:
            return self._live_ticdc_progress_metric(target, None)
        return self._ticdc_metric("ticdc_progress", target, None, None)

    def ticdc_pipeline_observation(self, target: Optional[str] = None) -> str:
        return self._ticdc_metric("ticdc_pipeline", target, None, None)

    def gc_progress_observation(self, target: Optional[str] = None) -> str:
        return self._ticdc_metric("gc_progress", target, None, None)

    def _mvcc_gc_status(self) -> dict[str, Any]:
        variables = self._query_rows(
            "SELECT VARIABLE_NAME AS variable_name, VARIABLE_VALUE AS variable_value FROM mysql.tidb "
            "WHERE VARIABLE_NAME IN ('tikv_gc_safe_point', 'tikv_gc_last_run_time', 'tikv_gc_life_time') "
            "ORDER BY VARIABLE_NAME"
        )
        global_variables = self._query_rows(
            "SHOW GLOBAL VARIABLES WHERE Variable_name IN ('tidb_gc_life_time', 'tidb_gc_enable')"
        )
        safe_rows = [r for r in variables if str(r["variable_name"]).casefold() == "tikv_gc_safe_point"]
        if len(safe_rows) != 1:
            raise RuntimeError(f"TiDB GC status requires one safe-point row: rows={safe_rows!r}")
        safe_text = str(safe_rows[0]["variable_value"])
        try:
            safe_ms = int(datetime.strptime(safe_text, "%Y%m%d-%H:%M:%S.%f %z").timestamp() * 1000)
        except ValueError as exc:
            raise RuntimeError(f"TiDB GC safe point has invalid timestamp: value={safe_text!r}") from exc
        pending = []
        for service in self.deployment.COMPONENTS["tikv"]:
            output = self.deployment.exec(f"tikv/{service}", ["wget", "-qO-", "-T", "5", "http://127.0.0.1:20180/metrics"])
            values = [float(line.rsplit(None, 1)[-1]) for line in output.splitlines() if re.match(r"^tikv_engine_pending_compaction_bytes(?:{|\\s)", line)]
            if not values:
                raise RuntimeError(f"TiKV metrics contain no pending compaction series: service={service!r}")
            pending.extend(values)
        docker_root = self.deployment._docker_info()[2]
        current_tso = self.current_tso()
        prometheus_raw = {
            phase: self._prometheus_instant_payload(query)
            for phase, query in {
                "gc_worker": '{__name__=~"tikv_.*gc.*"}',
                "resolve_locks": '{__name__=~".*resolve.*lock.*"}',
                "delete_ranges": '{__name__=~".*delete.*range.*"}',
                "do_gc": '{__name__=~".*do_gc.*"}',
            }.items()
        }
        return {
            "sql_variables": variables,
            "global_variables": global_variables,
            "current_tso": current_tso,
            "gc_safe_point_tso": safe_ms << 18,
            "gc_headroom_seconds": int((current_tso >> 18) / 1000 - safe_ms / 1000),
            "disk_free_bytes": int(shutil.disk_usage(docker_root).free),
            "compaction_pending": int(max(pending)),
            "prometheus_raw": prometheus_raw,
        }

    def slow_queries_observation(self) -> str:
        start, end = self._prometheus_range(None, None)
        rows = self._query_rows(
            "SELECT TIME, INSTANCE, DIGEST, QUERY, QUERY_TIME, PROCESS_TIME, "
            "WAIT_TIME, BACKOFF_TIME, TOTAL_KEYS, PROCESS_KEYS, MEM_MAX, DISK_MAX "
            "FROM INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY "
            "WHERE TIME BETWEEN FROM_UNIXTIME(%s) AND FROM_UNIXTIME(%s) "
            "ORDER BY TIME DESC LIMIT 50",
            (start, end),
        )
        return self._metric_success("slow_queries", "records", records=rows)

    def topsql_observation(self) -> str:
        start, end = self._prometheus_range(None, None)
        rows = self._query_rows(
            "SELECT INSTANCE, RESOURCE_GROUP, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY, "
            "AVG_TOTAL_KEYS, AVG_PROCESSED_KEYS, AVG_MEM, MAX_MEM, AVG_DISK, MAX_DISK "
            "FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY "
            "WHERE SUMMARY_END_TIME >= FROM_UNIXTIME(%s) "
            "AND SUMMARY_BEGIN_TIME <= FROM_UNIXTIME(%s) "
            "ORDER BY SUM_LATENCY DESC LIMIT 50",
            (start, end),
        )
        return self._metric_success("topsql", "records", records=rows)

    def observe_metric(
        self,
        metric: str,
        target: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> str:
        """Trusted scenario/evaluator observation; never registered as an agent tool."""
        metric = metric.casefold()
        if metric == "workload_activity":
            return self.workload_activity_observation(50 if limit is None else limit)
        if metric == "cluster_info":
            return self.cluster_info_observation()
        if metric == "node_health":
            return self.node_health_observation()
        if metric == "region_count":
            return self.region_count_observation(target)
        if metric == "region_health":
            return self.region_health_observation()
        if metric == "pd_scheduling":
            return self.pd_scheduling_observation()
        if metric == "placement_progress":
            return self.placement_progress_observation()
        if metric == "replication":
            return self.replication_observation()
        if metric == "ticdc_progress":
            return self.ticdc_progress_observation(target)
        if metric == "ticdc_pipeline":
            return self.ticdc_pipeline_observation(target)
        if metric == "gc_progress":
            return self.gc_progress_observation(target)
        if metric == "slow_queries":
            return self.slow_queries_observation()
        if metric == "topsql":
            return self.topsql_observation()
        if metric in self.TIME_SERIES_METRICS:
            frame = self._metric_service.query_live(MetricQuery(metric=metric, target=target))
            timestamps = [timestamp for values in frame.timestamps_ms.values() for timestamp in values]
            return render_metric_frame(
                frame,
                available_start_ms=min(timestamps),
                available_end_ms=max(timestamps),
                requested_start_ms=min(timestamps),
                requested_end_ms=max(timestamps),
                step_seconds=frame.step_seconds,
            )
        raise ValueError(f"Unknown trusted TiDB metric: metric={metric!r}")

    @staticmethod
    def _execute_sql_on_connection(connection, sql_query: str, *, bound_result: bool = False) -> str:
        result, columns, row_count, fetched = [], [], 0, 0
        byte_truncated = False
        with connection.cursor() as cur:
            cur.execute(sql_query)
            while True:
                if cur.description:
                    columns = [column[0] for column in cur.description]
                    rows = cur.fetchmany(201)
                    fetched = len(rows)
                    row_count = fetched
                    if bound_result:
                        # agent 面：与 PG 路径同一套边界（单值 2048 字符 + 128KiB
                        # 总量）。宽表（如 information_schema.statements_summary）
                        # 单行可达数百 KB，不设上限时一次查询即可撑爆对话上下文。
                        result, byte_truncated = _bound_sql_rows(rows)
                    else:
                        # 场景内部/评估器面：夹具校验与证据读取需要完整结果。
                        result = rows[:200]
                else:
                    row_count = cur.rowcount
                if not cur.nextset():
                    break
        truncated = fetched > 200 or byte_truncated
        payload = {
            "status": "success",
            "columns": columns,
            "result": result,
            "row_count": row_count,
            "truncated": truncated,
        }
        if truncated and bound_result:
            payload["truncation_hint"] = SQL_TRUNCATION_HINT
        return json.dumps(payload, ensure_ascii=False, default=str)

    def initialize_workload_session(self, connection, profile):
        connection_id = id(connection)
        if connection_id in self._workload_session_setups:
            raise RuntimeError(
                "TiDB workload session was initialized twice: "
                f"profile={profile.name!r}, connection_id={connection_id}"
            )
        with connection.cursor() as cur:
            for statement in profile.connection_setup_statements:
                cur.execute(statement)
            if profile.session_setup is not None:
                self._cache_workload_session_config(cur, connection_id, profile)

    def _cache_workload_session_config(self, cur, connection_id, profile):
        cur.execute(profile.session_setup.config_query)
        rows = cur.fetchall()
        if len(rows) != 1:
            raise RuntimeError(
                "TiDB workload session setup configuration must return exactly one row: "
                f"profile={profile.name!r}, query={profile.session_setup.config_query!r}, "
                f"rows={rows!r}"
            )
        self._workload_session_setups[connection_id] = {
            "configuration": tuple(rows[0]),
            "checkout_number": 0,
        }

    def configure_workload_session(self, connection, profile):
        return None

    def execute_workload_profile(self, connection, profile):
        if profile.transactional:
            connection.begin()
        session_setup_statements = 0
        with connection.cursor() as cur:
            if profile.session_setup is not None:
                connection_id = id(connection)
                if connection_id not in self._workload_session_setups:
                    self._cache_workload_session_config(cur, connection_id, profile)
                state = self._workload_session_setups[connection_id]
                state["checkout_number"] = int(state["checkout_number"]) + 1
                session_setup_statements = profile.session_setup.statement_count(
                    state["configuration"],
                    int(state["checkout_number"]),
                )
                if session_setup_statements < 0:
                    raise ValueError(
                        "TiDB workload session setup count must be non-negative: "
                        f"profile={profile.name!r}, count={session_setup_statements}"
                    )
                for _ in range(session_setup_statements):
                    cur.execute(profile.session_setup.statement)
            cur.execute(profile.sql)
            result_rows = len(cur.fetchall()) if cur.description else cur.rowcount
        if profile.transactional:
            connection.commit() if profile.commit else connection.rollback()
        if self._connection_routers:
            connection_pool = self._connection_router_connections.get(id(connection))
            if connection_pool is None:
                raise RuntimeError(
                    f"TiDB workload connection is not registered: connection_id={id(connection)}"
                )
            router = self._connection_routers[connection_pool]
            if router.should_recycle(connection):
                self.close_workload_connection(connection)
        return {
            "session_setup_statements": session_setup_statements,
            "result_rows": result_rows,
        }

    def attach_workload_runner(self, runner):
        if self._workload_runner is not None:
            raise RuntimeError(f"TiDB workload runner already attached: run_id={self.run_id!r}")
        self._workload_runner = runner

    def begin_workload_observation_window(self, before_reset: Optional[Callable[[], None]] = None) -> None:
        if self._workload_runner is None:
            raise RuntimeError(
                "TiDB workload observation window requires an attached runner: "
                f"run_id={self.run_id!r}"
            )
        self._workload_runner.begin_observation_window(before_reset=before_reset)

    def wait_for_workload_observation_window(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError(
                "TiDB workload observation wait must be non-negative: "
                f"seconds={seconds!r}"
            )
        time.sleep(seconds)

    def attach_import_controller(self, controller) -> None:
        if self._import_controller is not None:
            raise RuntimeError(
                f"TiDB import controller already attached: run_id={self.run_id!r}"
            )
        self._import_controller = controller

    @property
    def import_controller(self):
        if self._import_controller is None:
            raise RuntimeError(f"TiDB import controller is not attached: run_id={self.run_id!r}")
        return self._import_controller

    def _stop_workload_runner(self):
        if self._workload_runner is not None:
            self._workload_runner.stop()
            self._workload_runner = None

    @contextmanager
    def metrics_hidden(self):
        self._metrics_hidden_depth += 1
        try:
            yield
        finally:
            self._metrics_hidden_depth -= 1
            if self._metrics_hidden_depth == 0:
                self._visible_since = time.time()
                self._log_visible_lines = {
                    target: len(self.deployment.read_logs(target, lines=10000).splitlines())
                    for target in self.deployment.list_nodes()
                }

    def _query_rows(
        self,
        sql: str,
        args=(),
        target: str = "primary",
    ) -> List[Dict[str, Any]]:
        import pymysql
        with self._ensure_connection(target).cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, args)
            return list(cur.fetchall())








    def _prometheus_range(
        self,
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> tuple[float, float]:
        if start_timestamp is None:
            end = time.time()
            return max(self._visible_since, end - self.return_window_seconds), end
        start = start_timestamp.timestamp()
        end = end_timestamp.timestamp()
        visible_since_second = int(self._visible_since)
        if start < visible_since_second:
            raise ValueError(
                "query_metrics.start_timestamp precedes the TiDB metric visibility boundary: "
                f"start_timestamp={start_timestamp:%Y-%m-%d %H:%M:%S}, "
                f"visible_since={datetime.fromtimestamp(self._visible_since):%Y-%m-%d %H:%M:%S}"
            )
        if start < self._visible_since:
            rounding_gap = self._visible_since - start
            if start_timestamp.microsecond and rounding_gap <= 1e-6:
                return self._visible_since, end
        return start, end

    def _prometheus_payload(
        self,
        query: str,
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> list:
        start, end = self._prometheus_range(start_timestamp, end_timestamp)
        return self._prometheus_payload_at_range(query, start, end)

    def _prometheus_payload_at_range(
        self,
        query: str,
        start: float,
        end: float,
    ) -> list:
        from urllib.parse import urlencode
        from urllib.request import urlopen

        params = urlencode({
            "query": query,
            "start": start,
            "end": end,
            "step": self.sample_interval_sec,
        })
        url = f"http://127.0.0.1:{self.deployment.prometheus_port}/api/v1/query_range?{params}"
        with urlopen(url, timeout=5) as response:
            payload = json.load(response)
        result = payload["data"]["result"]
        if payload["status"] != "success":
            raise RuntimeError(
                f"Prometheus query failed: run_id={self.run_id!r}, "
                f"query={query!r}, payload={payload!r}"
            )
        return result

    def _prometheus_instant_payload(self, query: str) -> list[dict[str, Any]]:
        from urllib.parse import urlencode
        from urllib.request import urlopen

        params = urlencode({"query": query})
        url = f"http://127.0.0.1:{self.deployment.prometheus_port}/api/v1/query?{params}"
        with urlopen(url, timeout=5) as response:
            payload = json.load(response)
        if payload["status"] != "success":
            raise RuntimeError(
                f"Prometheus instant query failed: run_id={self.run_id!r}, "
                f"query={query!r}, payload={payload!r}"
            )
        result = payload["data"]["result"]
        if not isinstance(result, list):
            raise TypeError(
                f"Prometheus instant query returned a non-list result: "
                f"run_id={self.run_id!r}, query={query!r}, result={result!r}"
            )
        return result

    def _prometheus_instant_scalar(self, query: str) -> float:
        result = self._prometheus_instant_payload(query)
        if len(result) != 1:
            raise RuntimeError(
                f"Prometheus instant query must return exactly one series: "
                f"run_id={self.run_id!r}, query={query!r}, series={len(result)}"
            )
        return float(result[0]["value"][1])

    @staticmethod
    def _prometheus_samples(result: dict) -> tuple[list[str], list[float]]:
        samples = result["values"]
        return (
            [datetime.fromtimestamp(float(item[0])).strftime("%Y-%m-%d %H:%M:%S") for item in samples],
            [float(item[1]) for item in samples],
        )

    def _prometheus_query(
        self,
        query: str,
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> tuple[list[str], list[float]]:
        result = self._prometheus_payload(query, start_timestamp, end_timestamp)
        if len(result) != 1:
            raise RuntimeError(
                f"Prometheus query must return exactly one series: "
                f"run_id={self.run_id!r}, query={query!r}, series={len(result)}"
            )
        return self._prometheus_samples(result[0])

    def _prometheus_query_at_range(
        self,
        query: str,
        start: float,
        end: float,
    ) -> tuple[list[str], list[float]]:
        result = self._prometheus_payload_at_range(query, start, end)
        if len(result) != 1:
            raise RuntimeError(
                f"Prometheus query must return exactly one series: "
                f"run_id={self.run_id!r}, query={query!r}, series={len(result)}"
            )
        return self._prometheus_samples(result[0])

    def _prometheus_query_by_service(
        self,
        query: str,
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> dict[str, tuple[list[str], list[float]]]:
        return self._prometheus_query_by_label(
            query, self.COMPOSE_SERVICE_LABEL, start_timestamp, end_timestamp
        )

    def _prometheus_query_by_label(
        self,
        query: str,
        label: str,
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> dict[str, tuple[list[str], list[float]]]:
        result = self._prometheus_payload(query, start_timestamp, end_timestamp)
        series = {}
        for item in result:
            key = item["metric"][label]
            if key in series:
                raise RuntimeError(
                    f"Prometheus query returned duplicate {label!r} series: "
                    f"run_id={self.run_id!r}, query={query!r}, value={key!r}"
                )
            series[key] = self._prometheus_samples(item)
        return series

    def _resource_selector(self, target: Optional[str]) -> str:
        labels = [
            f'container_label_com_docker_compose_project="{self.deployment.project_name}"'
        ]
        if target is not None:
            labels.append(
                f'container_label_com_docker_compose_service="{self.deployment.NODES[target]}"'
            )
        return "{" + ",".join(labels) + "}"

    def _metric(self, metric: str, target: str, timestamps, **values):
        return self._metric_success(
            metric,
            "series",
            series={target: {"timestamps": timestamps, **values}},
        )

    def _cpu_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if target is None:
            selector = self._resource_selector(None)
            query = (
                f"sum by ({self.COMPOSE_SERVICE_LABEL}) "
                f"(rate(container_cpu_usage_seconds_total{selector}[10s]))"
            )
            by_service = self._prometheus_query_by_service(
                query, start_timestamp, end_timestamp
            )
            service_to_target = {
                service: node
                for node, service in self.deployment.NODES.items()
                if node in self.deployment.database_nodes
            }
            missing = sorted(set(service_to_target) - set(by_service))
            if missing:
                raise RuntimeError(
                    f"Prometheus CPU query is missing TiDB services: "
                    f"run_id={self.run_id!r}, services={missing}"
                )
            series = {}
            for service, node in service_to_target.items():
                timestamps, cores = by_service[service]
                cpu_limit = self.deployment.node_cpu_limits[node]
                values = [round(value / cpu_limit * 100, 2) for value in cores]
                series[node] = {
                    "timestamps": timestamps,
                    "percent": values,
                }
            return self._metric_success("cpu", "series", series=series)

        if target not in self.deployment.NODES:
            raise ValueError(
                f"Unknown TiDB target {target!r}; expected one of {self.deployment.list_nodes()}"
            )
        selector = self._resource_selector(target)
        query = f"sum(rate(container_cpu_usage_seconds_total{selector}[10s]))"
        timestamps, cores = self._prometheus_query(
            query, start_timestamp, end_timestamp
        )
        cpu_limit = self.deployment.node_cpu_limits[target]
        values = [round(value / cpu_limit * 100, 2) for value in cores]
        return self._metric("cpu", target, timestamps, percent=values)

    def _resource_metric(
        self,
        metric: str,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if metric == "cpu":
            return self._cpu_metric(target, start_timestamp, end_timestamp)
        if target is not None and target not in self.deployment.NODES:
            raise ValueError(
                f"Unknown TiDB target {target!r}; expected one of {self.deployment.list_nodes()}"
            )
        template, _ = self.RESOURCE_QUERIES[metric]
        query = template.format(selector=self._resource_selector(target))
        timestamps, values = self._prometheus_query(
            query, start_timestamp, end_timestamp
        )
        value_name = "megabytes" if metric == "disk_usage" else "megabytes_per_second"
        converted = [round(value / 1024**2, 3) for value in values]
        return self._metric(
            metric, target or "cluster", timestamps, **{value_name: converted}
        )

    def _database_service_targets(self, node_type: Optional[str] = None) -> dict[str, str]:
        return {
            service: target
            for target, service in self.deployment.NODES.items()
            if target in self.deployment.database_nodes
            and (node_type is None or target.startswith(f"{node_type}/"))
        }

    def _require_service_series(self, metric: str, expected_services, *series_maps) -> None:
        for series in series_maps:
            missing = sorted(set(expected_services) - set(series))
            if missing:
                raise RuntimeError(
                    f"Prometheus {metric} query is missing TiDB services: "
                    f"run_id={self.run_id!r}, services={missing}"
                )

    def _memory_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if target is not None and target not in self.deployment.NODES:
            raise ValueError(
                f"Unknown TiDB target {target!r}; expected one of {self.deployment.list_nodes()}"
            )
        selector = self._resource_selector(target)
        group = f" by ({self.COMPOSE_SERVICE_LABEL})" if target is None else ""
        query = (
            f"100 * sum{group}(container_memory_working_set_bytes{selector}) / "
            f"sum{group}(container_spec_memory_limit_bytes{selector})"
        )
        if target is not None:
            timestamps, values = self._prometheus_query(
                query, start_timestamp, end_timestamp
            )
            return self._metric(
                "memory", target, timestamps,
                percent=[round(value, 2) for value in values],
            )

        by_service = self._prometheus_query_by_service(
            query, start_timestamp, end_timestamp
        )
        service_to_target = self._database_service_targets()
        self._require_service_series("memory", service_to_target, by_service)
        series = {}
        for service, node in service_to_target.items():
            timestamps, samples = by_service[service]
            values = [round(value, 2) for value in samples]
            series[node] = {
                "timestamps": timestamps,
                "percent": values,
            }
        return self._metric_success("memory", "series", series=series)

    def _disk_io_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if target is not None and target not in self.deployment.NODES:
            raise ValueError(
                f"Unknown TiDB target {target!r}; expected one of {self.deployment.list_nodes()}"
            )
        selector = self._resource_selector(target)
        group = f" by ({self.COMPOSE_SERVICE_LABEL})" if target is None else ""
        queries = {
            "read_bytes_per_second": (
                f"sum{group}(rate(container_fs_reads_bytes_total{selector}[10s]))"
            ),
            "write_bytes_per_second": (
                f"sum{group}(rate(container_fs_writes_bytes_total{selector}[10s]))"
            ),
        }
        if target is not None:
            read_timestamps, reads = self._prometheus_query(
                queries["read_bytes_per_second"], start_timestamp, end_timestamp
            )
            write_timestamps, writes = self._prometheus_query(
                queries["write_bytes_per_second"], start_timestamp, end_timestamp
            )
            if read_timestamps != write_timestamps:
                raise RuntimeError(
                    f"Prometheus disk_io timestamps differ: run_id={self.run_id!r}, "
                    f"target={target!r}"
                )
            return self._metric(
                "disk_io", target, read_timestamps,
                read_mb_per_second=[round(value / 1024**2, 3) for value in reads],
                write_mb_per_second=[round(value / 1024**2, 3) for value in writes],
            )

        read_by_service = self._prometheus_query_by_service(
            queries["read_bytes_per_second"], start_timestamp, end_timestamp
        )
        write_by_service = self._prometheus_query_by_service(
            queries["write_bytes_per_second"], start_timestamp, end_timestamp
        )
        service_to_target = self._database_service_targets()
        self._require_service_series(
            "disk_io", service_to_target, read_by_service, write_by_service
        )
        series = {}
        for service, node in service_to_target.items():
            timestamps, reads = read_by_service[service]
            write_timestamps, writes = write_by_service[service]
            if timestamps != write_timestamps:
                raise RuntimeError(
                    f"Prometheus disk_io timestamps differ: run_id={self.run_id!r}, "
                    f"target={node!r}"
                )
            series[node] = {
                "timestamps": timestamps,
                "read_mb_per_second": [round(value / 1024**2, 3) for value in reads],
                "write_mb_per_second": [round(value / 1024**2, 3) for value in writes],
            }
        return self._metric_success("disk_io", "series", series=series)

    def _qps_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        selector = ""
        if target is not None:
            if target not in self.deployment.tidb_endpoints:
                raise ValueError(
                    f"QPS target must be a TiDB node: target={target!r}, "
                    f"expected={list(self.deployment.tidb_endpoints)}"
                )
            selector = f'{{instance="{self.deployment.NODES[target]}:10080"}}'
        query = f"sum(rate(tidb_server_query_total{selector}[10s]))"
        timestamps, values = self._prometheus_query(
            query, start_timestamp, end_timestamp
        )
        return self._metric(
            "qps", target or "cluster", timestamps, queries_per_second=values
        )

    def _latency_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if start_timestamp is None:
            end_timestamp = datetime.fromtimestamp(time.time())
            start_timestamp = datetime.fromtimestamp(
                max(
                    self._visible_since,
                    end_timestamp.timestamp() - self.return_window_seconds,
                ) + 1e-6
            )
        matcher = ""
        if target is not None:
            if target not in self.deployment.tidb_endpoints:
                raise ValueError(f"query_latency target must be a TiDB node: target={target!r}")
            matcher = f'instance="{self.deployment.NODES[target]}:10080"'
        selector = "{" + matcher + "}" if matcher else ""
        queries = {
            "average_seconds": (
                f"sum(rate(tidb_server_handle_query_duration_seconds_sum{selector}[10s])) / "
                f"sum(rate(tidb_server_handle_query_duration_seconds_count{selector}[10s]))"
            ),
            "p95_seconds": (
                "histogram_quantile(0.95, sum by (le) "
                f"(rate(tidb_server_handle_query_duration_seconds_bucket{selector}[10s])))"
            ),
            "p99_seconds": (
                "histogram_quantile(0.99, sum by (le) "
                f"(rate(tidb_server_handle_query_duration_seconds_bucket{selector}[10s])))"
            ),
        }
        range_start, range_end = self._prometheus_range(
            start_timestamp, end_timestamp
        )
        series = {
            name: self._prometheus_query_at_range(query, range_start, range_end)
            for name, query in queries.items()
        }
        timestamps = series["average_seconds"][0]
        if any(data[0] != timestamps for data in series.values()):
            raise RuntimeError(f"Prometheus latency timestamps differ: run_id={self.run_id!r}")
        return self._metric(
            "query_latency", target or "cluster", timestamps,
            average_ms=[round(value * 1000, 3) for value in series["average_seconds"][1]],
            p95_ms=[round(value * 1000, 3) for value in series["p95_seconds"][1]],
            p99_ms=[round(value * 1000, 3) for value in series["p99_seconds"][1]],
        )

    def _active_connections_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        if target is not None and target not in self.deployment.tidb_endpoints:
            raise ValueError(
                f"active_connections target must be a TiDB node: target={target!r}, "
                f"expected={list(self.deployment.tidb_endpoints)}"
            )
        matcher = (
            f'{{instance="{self.deployment.NODES[target]}:10080"}}'
            if target is not None else ""
        )
        query = f"sum{' by (instance)' if target is None else ''}(tidb_server_connections{matcher})"
        if target is not None:
            timestamps, values = self._prometheus_query(
                query, start_timestamp, end_timestamp
            )
            return self._metric(
                "active_connections", target, timestamps, connections=values
            )

        by_instance = self._prometheus_query_by_label(
            query, "instance", start_timestamp, end_timestamp
        )
        instance_to_target = {
            f"{service}:10080": node
            for service, node in self._database_service_targets("tidb").items()
        }
        self._require_service_series(
            "active_connections", instance_to_target, by_instance
        )
        series = {}
        for instance, node in instance_to_target.items():
            timestamps, values = by_instance[instance]
            series[node] = {
                "timestamps": timestamps,
                "connections": values,
            }
        return self._metric_success(
            "active_connections", "series", series=series
        )

    def _region_count_metric(
        self,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        tikv_targets = self._database_service_targets("tikv")
        if target is not None and target not in tikv_targets.values():
            raise ValueError(
                f"region_count target must be a TiKV node: target={target!r}, "
                f"expected={list(tikv_targets.values())}"
            )
        matcher = (
            f',address="{self.deployment.NODES[target]}:20160"'
            if target is not None else ""
        )
        group = " by (address, store)" if target is None else ""
        query = (
            f'max{group}(pd_scheduler_store_status{{type="region_count"{matcher}}})'
        )
        if target is not None:
            timestamps, values = self._prometheus_query(
                query, start_timestamp, end_timestamp
            )
            return self._metric(
                "region_count", target, timestamps,
                regions=[int(value) for value in values],
            )

        result = self._prometheus_payload(query, start_timestamp, end_timestamp)
        by_address = {}
        for item in result:
            address = item["metric"]["address"]
            if address in by_address:
                raise RuntimeError(
                    f"Prometheus region_count query returned duplicate address series: "
                    f"run_id={self.run_id!r}, address={address!r}"
                )
            timestamps, values = self._prometheus_samples(item)
            by_address[address] = (timestamps, [int(value) for value in values])
        address_to_target = {
            f"{service}:20160": node for service, node in tikv_targets.items()
        }
        self._require_service_series("region_count", address_to_target, by_address)
        series = {}
        for address, node in address_to_target.items():
            timestamps, values = by_address[address]
            series[node] = {
                "timestamps": timestamps,
                "regions": values,
            }
        return self._metric_success("region_count", "series", series=series)

    def _region_health_metric(self) -> str:
        return self._metric_success(
            "region_health",
            "snapshot",
            snapshot=self._region_health_snapshot(),
        )

    def _region_health_snapshot(self) -> dict[str, object]:
        total_regions = self._prometheus_instant_scalar(
            'max(pd_scheduler_store_status{type="region_count"})'
        )
        empty_regions = self._prometheus_instant_scalar(
            'max(pd_regions_status{type="empty-region-count"})'
        )
        undersized_regions = self._prometheus_instant_scalar(
            'max(pd_regions_status{type="undersized-region-count"})'
        )
        pending_peer_regions = self._prometheus_instant_scalar(
            'max(pd_regions_status{type="pending-peer-region-count"})'
        )
        if total_regions <= 0:
            raise RuntimeError(
                f"PD reported a non-positive region count: run_id={self.run_id!r}, "
                f"total_regions={total_regions}"
            )
        return {
            "total_regions": int(total_regions),
            "empty_regions": int(empty_regions),
            "empty_ratio": round(empty_regions / total_regions, 6),
            "undersized_regions": int(undersized_regions),
            "pending_peer_regions": int(pending_peer_regions),
        }

    def _pd_scheduling_metric(self) -> str:
        queries = {
            "heartbeat_rate": (
                'sum(rate(pd_scheduler_region_heartbeat{type="report",status="recv"}[30s])) '
                "or vector(0)"
            ),
            "heartbeat_handle_rate": (
                "sum(rate(pd_scheduler_handle_region_heartbeat_duration_seconds_count[30s])) "
                "or vector(0)"
            ),
            "operator_create_rate": (
                'sum(rate(pd_schedule_operators_count{event="create"}[30s])) or vector(0)'
            ),
            "operator_finish_rate": (
                'sum(rate(pd_schedule_operators_count{event="finish"}[30s])) or vector(0)'
            ),
            "merge_operator_create_rate": (
                'sum(rate(pd_schedule_operators_count{event="create",type=~".*merge.*"}[30s])) '
                "or vector(0)"
            ),
            "merge_operator_finish_rate": (
                'sum(rate(pd_schedule_operators_count{event="finish",type=~".*merge.*"}[30s])) '
                "or vector(0)"
            ),
            "region_operator_limit": (
                'max(pd_config_status{type="region-schedule-limit"}) or vector(0)'
            ),
            "pd_cpu_percent": (
                "max(pd_server_cluster_state_cpu_usage) or vector(0)"
            ),
        }
        values = {
            name: round(self._prometheus_instant_scalar(query), 6)
            for name, query in queries.items()
        }
        return self._metric_success("pd_scheduling", "snapshot", snapshot=values)

    def _get_tidb_knowledge_base(self, knowledge_base_mode: str) -> TiDBKnowledgeBase:
        if knowledge_base_mode not in self._tidb_knowledge_bases:
            self._tidb_knowledge_bases[knowledge_base_mode] = TiDBKnowledgeBase(
                knowledge_base_mode=knowledge_base_mode,
            )
        return self._tidb_knowledge_bases[knowledge_base_mode]

    def _search_tidb_knowledge(
        self,
        *,
        query: str,
        source_scope: str,
        top_k: int,
        max_chars_per_result: int,
        knowledge_base_mode: str,
        kb_type: Optional[str] = None,
        component: Optional[str] = None,
    ) -> str:
        try:
            result = self._get_tidb_knowledge_base(knowledge_base_mode).query(
                query=query,
                source_scope=source_scope,
                top_k=top_k,
                kb_type=kb_type,
                component=component,
                max_chars_per_result=max_chars_per_result,
            )
            allowed = {"status", "query", "source_scope", "kb_type", "component", "top_k", "count", "results"}
            projected = {key: value for key, value in result.items() if key in allowed}
            projected["results"] = [
                {key: value for key, value in row.items() if key in {"rank", "score", "title", "version", "kb_type", "component", "source_scope", "content"}}
                for row in result.get("results", [])
            ]
            return json.dumps(projected, ensure_ascii=False, default=str)
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            return json.dumps({
                "status": "error",
                "error": (
                    f"TiDB knowledge query failed: mode={knowledge_base_mode!r}, "
                    f"query={query!r}, source_scope={source_scope!r}, kb_type={kb_type!r}, "
                    f"component={component!r}, top_k={top_k!r}, "
                    f"max_chars_per_result={max_chars_per_result!r}, error={exc}"
                ),
            }, ensure_ascii=False)

    @Tool(
        description=(
            "检索 TiDB 8.1 官方文档知识库。所有 TiDB 场景使用同一检索接口；"
            "过滤条件只限定文档范围，不提供场景结论或故障状态。"
        ),
        arg_descriptions={
            "query": "面向 TiDB 官方文档的自然语言或精确标识符查询",
            "source_scope": "文档范围: self_managed, cloud, kubernetes, developer, shared, all；默认 all",
            "top_k": "返回结果数量，默认 5，范围 1-20",
            "kb_type": "可选文档分类",
            "component": "可选组件分类",
        },
        definition=TIDB_TOOL_DEFINITIONS["search_knowledge"],
    )
    def search_knowledge(
        self,
        query: str,
        source_scope: str = "all",
        top_k: int = 5,
        kb_type: Optional[str] = None,
        component: Optional[str] = None,
    ) -> str:
        return self._search_tidb_knowledge(
            query=query,
            source_scope=source_scope,
            top_k=top_k,
            kb_type=kb_type,
            component=component,
            max_chars_per_result=1600,
            knowledge_base_mode="hierarchical",
        )

    @Tool(
        description=(
            "查询通用 TiDB 基础资源和服务时序。结果只包含原始时间序列，"
            "SQL-backed 的查询明细、集群表和控制面状态请通过 execute_sql 或 manage_cluster 观察。"
        ),
        arg_descriptions={
            "metric_type": (
                "当前 Case 在 help('query_metrics') 返回的 allowed_metrics 中声明的指标；"
                "非历史 Case 只允许基础资源和服务时序"
            ),
            "target": "稳定节点身份，例如 tikv/tikv-0；不传时返回集群或各服务时序",
            "start_timestamp": "时序指标开始时间，必须与 end_timestamp 同时提供，格式 YYYY-MM-DD HH:mm:ss",
            "end_timestamp": "时序指标结束时间，必须与 start_timestamp 同时提供，格式 YYYY-MM-DD HH:mm:ss",
            "step_seconds": "历史时序采样步长；必须是 Case base step 的正整数倍",
        },
        definition=TIDB_TOOL_DEFINITIONS["query_metrics"],
    )
    def query_metrics(
        self,
        metric_type: str,
        target: Optional[str] = None,
        limit: Optional[int] = None,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None,
        step_seconds: Optional[int] = None,
    ) -> str:
        metric = metric_type.lower()
        try:
            history_spec = getattr(self._case, "frozen_history", None)
            allowed_metrics = (
                frozenset(str(item).casefold() for item in history_spec.required_metrics)
                if history_spec is not None
                else self.TIME_SERIES_METRICS - self.CASE_ONLY_HISTORY_METRICS
            )
            if metric not in allowed_metrics:
                raise ValueError(f"Unknown TiDB metric_type {metric_type!r}")
            if (start_timestamp is None) != (end_timestamp is None):
                raise ValueError(
                    "query_metrics.start_timestamp and query_metrics.end_timestamp must be provided together"
                )
            start_ms = parse_utc_timestamp(start_timestamp, "start_timestamp") if start_timestamp is not None else None
            end_ms = parse_utc_timestamp(end_timestamp, "end_timestamp") if end_timestamp is not None else None
            query = MetricQuery(
                metric=metric,
                target=target,
                start_epoch_ms=start_ms,
                end_epoch_ms=end_ms,
                step_seconds=step_seconds,
            )
            frame = self._metric_service.query_public(query)
            if self._history_timeline is not None:
                available_start_ms = self._history_timeline.visible_start_ms
                available_end_ms = self._history_timeline.visible_end_ms
                requested_start_ms = start_ms if start_ms is not None else available_start_ms
                requested_end_ms = end_ms if end_ms is not None else available_end_ms
                requested_step = step_seconds or (
                    self._history_timeline.base_step_seconds
                    if start_ms is not None
                    else self._history_timeline.overview_step_seconds
                )
            else:
                timestamps = [timestamp for values in frame.timestamps_ms.values() for timestamp in values]
                available_start_ms = min(timestamps)
                available_end_ms = max(timestamps)
                requested_start_ms = start_ms if start_ms is not None else available_start_ms
                requested_end_ms = end_ms if end_ms is not None else available_end_ms
                requested_step = step_seconds or frame.step_seconds
            return bound_metric_result(render_metric_frame(
                frame,
                available_start_ms=available_start_ms,
                available_end_ms=available_end_ms,
                requested_start_ms=requested_start_ms,
                requested_end_ms=requested_end_ms,
                step_seconds=requested_step,
                # Keep explicit evidence windows complete; only compact
                # no-window overviews use the per-target point limit.
                max_points=(
                    (limit if limit is not None else 20)
                    if start_timestamp is None and end_timestamp is None
                    else None
                ),
            ))
        except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
            return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)

    def bind_metric_history(self, timeline: FrozenHistoricalTimeline) -> None:
        if self._case is None or getattr(self._case, "frozen_history", None) is None:
            raise RuntimeError(
                f"Cannot bind metric history to a non-history Case: run_id={self.run_id!r}, case={getattr(self._case, 'case_id', None)!r}"
            )
        if not isinstance(timeline, FrozenHistoricalTimeline):
            raise TypeError(f"TiDB metric history must be FrozenHistoricalTimeline, got {type(timeline).__name__}")
        self._metric_service.bind_history(timeline.metric_provider)
        self._history_timeline = timeline
        spec = self._case.frozen_history
        self._history_sql_archive = FrozenHistoricalSqlArchive(
            timeline.record_store,
            max_rows=min(200, spec.max_history_records_per_response),
            visible_start_ms=timeline.visible_start_ms,
            visible_end_ms=timeline.visible_end_ms,
        )
        self.register_sql_connection_surface(
            "history",
            database="aiops_metric_history",
            description="当前 Case 的只读冻结历史；UTC 时间轴与 query_metrics 一致。只能查询 statement_summary 和 slow_query。",
            query_examples=(
                "SELECT * FROM statement_summary WHERE event_start_utc < '2030-01-01 00:10:00' AND event_end_utc >= '2030-01-01 00:00:00'",
                "SELECT * FROM slow_query WHERE event_time_utc >= '2030-01-01 00:00:00' AND event_time_utc < '2030-01-01 00:10:00'",
            ),
            write_policy="read_only",
        )
        self._configure_tools(self.FROZEN_HISTORY_PUBLIC_TOOLS)

    def get_frozen_history_record_store_for_evaluator(self) -> FrozenHistoricalRecordStore:
        if self._history_timeline is None:
            raise RuntimeError(
                f"TiDB frozen history record store is unavailable before history binding: run_id={self.run_id!r}"
            )
        return self._history_timeline.record_store

    def get_frozen_history_metric_provider_for_evaluator(self) -> FrozenHistoryMetricProvider:
        if self._history_timeline is None:
            raise RuntimeError(
                f"TiDB frozen history metric provider is unavailable before history binding: run_id={self.run_id!r}"
            )
        return self._history_timeline.metric_provider

    def _live_ticdc_progress_metric(
        self,
        changefeed_id: Optional[str],
        start_timestamp: Optional[datetime],
    ) -> str:
        if changefeed_id is None:
            raise ValueError(
                "Live TiCDC ticdc_progress requires target=changefeed_id: "
                f"run_id={self.run_id!r}"
            )
        if start_timestamp is not None:
            raise ValueError(
                "Live TiCDC ticdc_progress is a current snapshot and does not accept a time range: "
                f"changefeed_id={changefeed_id!r}"
            )
        changefeed = self.replication_status(changefeed_id)
        checkpoint_tso = int(changefeed["checkpoint_tso"])
        resolved_tso = int(changefeed["resolved_ts"])
        if checkpoint_tso <= 0 or resolved_tso <= 0:
            raise ReplicationProgressUnavailableError(
                changefeed_id=changefeed_id,
                reason="non_positive_tso",
                state=changefeed.get("state"),
                error=changefeed.get("error"),
                upstream_tso=0,
                resolved_tso=resolved_tso,
                checkpoint_tso=checkpoint_tso,
            )
        if resolved_tso < checkpoint_tso:
            raise ReplicationProgressUnavailableError(
                changefeed_id=changefeed_id,
                reason="resolved_before_checkpoint",
                state=changefeed.get("state"),
                error=changefeed.get("error"),
                upstream_tso=0,
                resolved_tso=resolved_tso,
                checkpoint_tso=checkpoint_tso,
            )
        lag_seconds = round(
            ((resolved_tso >> 18) - (checkpoint_tso >> 18)) / 1000,
            3,
        )
        return self._metric_success(
            "ticdc_progress",
            "snapshot",
            snapshot={
                "changefeed_id": changefeed_id,
                "state": changefeed["state"],
                "error": changefeed.get("error"),
                "resolved_tso": resolved_tso,
                "checkpoint_tso": checkpoint_tso,
                "checkpoint_time": changefeed["checkpoint_time"],
                "lag_seconds": lag_seconds,
            },
        )

    def _ticdc_metric(
        self,
        metric: str,
        target: Optional[str],
        start_timestamp: Optional[datetime],
        end_timestamp: Optional[datetime],
    ) -> str:
        family = {
            "ticdc_progress": "progress",
            "ticdc_pipeline": "pipeline",
            "gc_progress": "resource",
        }[metric]
        end = end_timestamp or datetime.now()
        start = start_timestamp or end - timedelta(seconds=self.return_window_seconds)
        clauses = ["family = %s", "sample_ts BETWEEN %s AND %s"]
        parameters = [family, start, end]
        if target is not None:
            clauses.append("target = %s")
            parameters.append(target)
        rows = self._query_rows(
            "SELECT sample_id, sample_ts, component, metric_name, target, value, "
            "text_value, unit FROM benchops.rg06_cdc_metrics WHERE "
            + " AND ".join(clauses)
            + " ORDER BY sample_ts DESC, sample_id DESC LIMIT 200",
            parameters,
        )
        return self._metric_success(
            metric,
            "records",
            window={
                "start_timestamp": start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_timestamp": end.strftime("%Y-%m-%d %H:%M:%S"),
            },
            records=rows,
        )

    @Tool(
        description=(
            "执行当前环境可访问 SQL 连接面上的 SQL，最多返回 200 行。"
            "连接面、用途和查询方式请先通过 help('execute_sql') 获取。"
            "SQL 结果由查询本身决定，不预先聚合为场景结论。"
        ),
        arg_descriptions={
            "sql_query": "要执行的 SQL 语句",
            "target": "连接面名称；先通过 help('execute_sql') 获取当前可用连接面；不传时使用 primary",
        },
        definition=TIDB_TOOL_DEFINITIONS["execute_sql"],
    )
    def execute_sql(self, sql_query: str, target: Optional[str] = None) -> str:
        return self._execute_sql_surface(sql_query, target, enforce_history_guard=True)

    def execute_sql_trusted(self, sql_query: str, target: Optional[str] = None) -> str:
        """Execute current-state SQL for evaluator and injector trusted checks."""
        return self._execute_sql_surface(sql_query, target, enforce_history_guard=False)

    def _execute_sql_surface(
        self,
        sql_query: str,
        target: Optional[str],
        *,
        enforce_history_guard: bool,
    ) -> str:
        import pymysql

        selected_target = target or "primary"
        if enforce_history_guard:
            for observer in self.agent_sql_observers:
                observer(selected_target, sql_query)
        connection = None
        close_connection = True
        try:
            if selected_target == "history":
                if self._history_sql_archive is None:
                    raise RuntimeError(
                        f"TiDB history SQL surface is unavailable: run_id={self.run_id!r}"
                    )
                columns, rows, row_count, truncated = self._history_sql_archive.execute(sql_query)
                payload = {
                    "status": "success",
                    "columns": columns,
                    "result": rows,
                    "row_count": row_count,
                    "truncated": truncated,
                }
                if truncated:
                    payload["truncation_hint"] = SQL_TRUNCATION_HINT
                return json.dumps(payload, ensure_ascii=False, default=str)
            if enforce_history_guard and selected_target != "downstream" and self._history_timeline is not None:
                reject_tidb_public_historical_sql(sql_query)
            self._validate_registered_sql_write_policies(
                sql_query,
                selected_target=selected_target,
                surfaces=self._sql_connection_surfaces,
            )
            if selected_target == "downstream":
                connection = self._downstream_connection()
            elif selected_target == "primary":
                connection = self._ensure_connection()
                close_connection = False
            elif selected_target == "replica":
                connection = self._ensure_connection("replica")
                close_connection = False
            elif selected_target in self._sql_connection_surfaces:
                connection = self._connect(
                    self._sql_connection_surfaces[selected_target].database
                )
            elif selected_target in self.deployment.tidb_endpoints:
                connection = self._connect(self.dbname, target=selected_target)
            else:
                raise ValueError(
                    f"Unknown TiDB SQL connection surface: target={selected_target!r}. "
                    "Call help('execute_sql') to inspect the current connection surfaces."
                )
            result = self._execute_sql_on_connection(
                connection, sql_query, bound_result=enforce_history_guard
            )
            if enforce_history_guard:
                for observer in self.agent_sql_observers:
                    observer(selected_target, sql_query)
            self._invalidate_connection_routers_for_sql(sql_query)
            return result
        except (pymysql.MySQLError, ValueError, RuntimeError) as exc:
            return json.dumps({
                "status": "error",
                "error": f"TiDB SQL failed: target={selected_target!r}, query={sql_query!r}, error={exc}",
            }, ensure_ascii=False)
        finally:
            if close_connection and connection is not None:
                connection.close()

    def execute_internal_sql(self, sql_query: str) -> str:
        """Execute scenario-owned SQL on a private control-plane connection."""
        connection = self._connect(self.dbname)
        try:
            result = self._execute_sql_on_connection(connection, sql_query)
            self._invalidate_connection_routers_for_sql(sql_query)
            return result
        finally:
            connection.close()

    def _manage_connection_router(
        self,
        action: str,
        target: str,
        value: Optional[str],
    ) -> str:
        if not self._connection_routers:
            raise RuntimeError(
                f"TiDB connection routers are not initialized: run_id={self.run_id!r}"
            )
        if action == "get_config":
            if target != self.CONNECTION_ROUTER_TARGET or value is not None:
                raise ValueError(
                    "get_config for TiDB connection routers requires target='connection-router' "
                    f"and no value: target={target!r}, value={value!r}"
                )
            payload = {"routers": self.connection_router_statuses()}
        elif action == "set_load_balance":
            if target not in self._connection_routers or value is None:
                raise ValueError(
                    "set_load_balance requires target to be a configured router and value to be "
                    "round_robin or least_connections: "
                    f"target={target!r}, value={value!r}, routers={sorted(self._connection_routers)}"
                )
            payload = self.set_connection_router_policy(target, value)
        elif action == "drain":
            if target not in self.deployment.NODES or value is not None:
                raise ValueError(
                    "drain requires a TiDB backend target and no value: "
                    f"target={target!r}, value={value!r}"
                )
            payload = {"routers": self.drain_connection_routers(target)}
        else:
            raise ValueError(
                f"Unknown TiDB connection-router action: action={action!r}, target={target!r}, "
                f"routers={sorted(self._connection_routers)}"
            )
        return json.dumps(
            {"status": "success", "action": action, "target": target, **payload},
            ensure_ascii=False,
        )

    def _read_tikv_runtime_config(self, target: str) -> dict[str, Any]:
        output = self.deployment.exec(
            target,
            ["sh", "-lc", "wget -qO- --timeout=5 http://127.0.0.1:20180/config"],
        )
        payload = json.loads(output)
        return {
            "storage": {
                "io_rate_limit": payload["storage"]["io-rate-limit"],
            },
        }

    def tikv_io_rate_limit(self, target: str) -> dict[str, Any]:
        return dict(self._read_tikv_runtime_config(target)["storage"]["io_rate_limit"])

    def set_tikv_io_rate_limit(
        self,
        target: str,
        max_bytes_per_sec: int | str,
    ) -> dict[str, Any]:
        key = "storage.io-rate-limit.max-bytes-per-sec"
        body = json.dumps({key: max_bytes_per_sec}, separators=(",", ":"))
        output = self.deployment.exec(
            target,
            [
                "wget", "-qO-", "--timeout=5", "--content-on-error",
                "--method=POST", "--header=Content-Type: application/json",
                f"--body-data={body}", "http://127.0.0.1:20180/config",
            ],
        )
        if output.strip() and output.strip() != "{}":
            payload = json.loads(output)
            if payload.get("error"):
                raise RuntimeError(
                    f"TiKV config update failed: target={target!r}, "
                    f"max_bytes_per_sec={max_bytes_per_sec!r}, response={payload!r}"
                )
        return self.tikv_io_rate_limit(target)

    def _service_states(self) -> Dict[str, Dict[str, Any]]:
        states = self.deployment.node_states()
        return {
            target: {
                key: value
                for key, value in state.items()
                if key != "container_id"
            }
            for target, state in states.items()
        }

    def _control_service(self, operation: str, target: str) -> Dict[str, Any]:
        external = self._replication_endpoint
        if external is not None and target == "ticdc/ticdc-0":
            if operation not in {"start", "stop", "restart"}:
                raise ValueError(
                    f"Unsupported TiCDC service operation: operation={operation!r}"
                )
            completed = subprocess.run(
                ["docker", operation, external["container_name"]],
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"TiCDC service operation failed: operation={operation!r}, "
                    f"target={target!r}, stdout={completed.stdout.strip()!r}, "
                    f"stderr={completed.stderr.strip()!r}"
                )
            return {"target": target, "running": operation != "stop"}
        if target == "pd":
            if operation != "restart":
                raise ValueError(
                    f"Unsupported TiDB PD quorum service operation: operation={operation!r}"
                )
            self.deployment.restart_pd_quorum()
            states = self._service_states()
            pd_names = sorted(name for name in states if name.startswith("pd/"))
            for name in pd_names:
                self.deployment._wait(
                    name,
                    self.deployment._check_pd,
                    self.deployment.warm_tidb_readiness_timeout_sec,
                )
            return {"nodes": pd_names}
        if target not in self.deployment.NODES:
            raise ValueError(
                f"Unknown TiDB service target {target!r}; expected one of {self.deployment.list_nodes()}"
            )
        method = {
            "restart": self.deployment.restart_component,
            "start": self.deployment.start_component,
            "stop": self.deployment.stop_component,
        }[operation]
        method(target)
        if target == "tidb/tidb-0":
            if self._conn is not None:
                self._conn.close()
                self._conn = None
            if operation != "stop":
                self.deployment._wait(
                    target,
                    self.reconnect,
                    self.deployment.warm_tidb_readiness_timeout_sec,
                )
        elif operation != "stop" and target.startswith("pd/"):
            self.deployment._wait(
                target,
                self.deployment._check_pd,
                self.deployment.warm_tidb_readiness_timeout_sec,
            )
        elif operation != "stop" and target.startswith("tikv/"):
            service = target.split("/", 1)[1]
            self.deployment._wait(
                target,
                lambda: self.deployment._check_tikv_target(service),
                self.deployment.warm_tidb_readiness_timeout_sec,
            )
        return {"target": target, "state": self._service_states().get(target)}

    def _resize_service(self, target: str, cpu_limit: float) -> Dict[str, Any]:
        if cpu_limit <= 0:
            raise ValueError(
                f"service resize requires a positive CPU limit: target={target!r}, cpu_limit={cpu_limit!r}"
            )
        external = self._replication_endpoint
        if external is not None and target == external["target"]:
            if cpu_limit > external["max_cpu_limit"]:
                raise ValueError(
                    f"TiCDC resize exceeds the authorized bound: target={target!r}, "
                    f"cpu_limit={cpu_limit!r}, max_cpu_limit={external['max_cpu_limit']!r}"
                )
            previous_cpu_limit = self._replication_cpu_limit()
            completed = subprocess.run(
                ["docker", "update", "--cpus", str(cpu_limit), external["container_name"]],
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"TiCDC resize failed: target={target!r}, cpu_limit={cpu_limit!r}, "
                    f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
                )
            return {
                "target": target,
                "previous_cpu_limit": previous_cpu_limit,
                "cpu_limit": float(cpu_limit),
            }
        if external is not None and target == "downstream/mysql-0":
            if cpu_limit > external["max_downstream_cpu_limit"]:
                raise ValueError(
                    "downstream MySQL resize exceeds the authorized bound: "
                    f"target={target!r}, cpu_limit={cpu_limit!r}, "
                    f"max_cpu_limit={external['max_downstream_cpu_limit']!r}"
                )
            previous_cpu_limit = self._replication_downstream_cpu_limit()
            completed = subprocess.run(
                [
                    "docker",
                    "update",
                    "--cpus",
                    str(cpu_limit),
                    external["downstream_container_name"],
                ],
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    "downstream MySQL resize failed: "
                    f"target={target!r}, cpu_limit={cpu_limit!r}, "
                    f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
                )
            return {
                "target": target,
                "previous_cpu_limit": previous_cpu_limit,
                "cpu_limit": float(cpu_limit),
            }
        raise ValueError(f"service resize is unsupported for target={target!r}")

    def _changefeed_state(self, changefeed_id: str) -> Dict[str, Any]:
        if self._replication_endpoint is not None:
            if changefeed_id != self._replication_endpoint["changefeed_id"]:
                raise ValueError(
                    f"Unknown configured changefeed: target={changefeed_id!r}, "
                    f"expected={self._replication_endpoint['changefeed_id']!r}"
                )
            changefeed = self.replication_status(changefeed_id)
            checkpoint_tso = int(changefeed["checkpoint_tso"])
            resolved_tso = int(changefeed.get("resolved_ts") or changefeed.get("resolved_tso") or self.current_tso())
            if checkpoint_tso <= 0 or resolved_tso <= 0:
                raise RuntimeError(
                    f"TiCDC TSOs must be positive: changefeed_id={changefeed_id!r}, "
                    f"checkpoint_tso={checkpoint_tso}, resolved_tso={resolved_tso}"
                )
            lag_seconds = round(((resolved_tso >> 18) - (checkpoint_tso >> 18)) / 1000, 3)
            return {
                "changefeed_id": changefeed_id,
                "state": changefeed["state"],
                "error": changefeed.get("error"),
                "resolved_tso": resolved_tso,
                "checkpoint_tso": checkpoint_tso,
                "checkpoint_time": changefeed["checkpoint_time"],
                "lag_seconds": lag_seconds,
                "execution_config": self._replication_sink_config(),
            }
        changefeed = self.replication_status(changefeed_id)
        result = {
            "changefeed_id": changefeed_id,
            "state": changefeed.get("state"),
            "error": changefeed.get("error"),
            "checkpoint_tso": changefeed.get("checkpoint_tso"),
            "checkpoint_time": changefeed.get("checkpoint_time"),
        }
        if "resolved_ts" in changefeed:
            result["resolved_tso"] = changefeed["resolved_ts"]
        if "resolved_tso" in changefeed:
            result["resolved_tso"] = changefeed["resolved_tso"]
        return result

    def _replication_sink_config(self) -> dict[str, object]:
        endpoint = self._replication_endpoint
        if endpoint is None:
            raise RuntimeError(f"TiDB replication endpoint is not configured: run_id={self.run_id!r}")
        parsed = urlsplit(endpoint["sink_uri"])
        parameters = dict(parse_qsl(parsed.query, keep_blank_values=True))
        try:
            worker_count = int(parameters["worker-count"])
            max_txn_row = int(parameters["max-txn-row"])
            batch_dml_enable = parameters["batch-dml-enable"].casefold()
        except (KeyError, ValueError) as exc:
            raise ValueError(
                "TiDB replication endpoint sink URI has invalid execution parameters: "
                f"changefeed_id={endpoint['changefeed_id']!r}, sink_uri={endpoint['sink_uri']!r}"
            ) from exc
        if batch_dml_enable not in {"true", "false"}:
            raise ValueError(
                "TiDB replication endpoint batch-dml-enable must be true or false: "
                f"changefeed_id={endpoint['changefeed_id']!r}, value={batch_dml_enable!r}"
            )
        return {
            "worker_count": worker_count,
            "max_txn_row": max_txn_row,
            "batch_dml_enable": batch_dml_enable == "true",
        }

    def _update_replication_sink_config(
        self,
        changefeed_id: str,
        parameters: Dict[str, Any],
    ) -> dict[str, object]:
        endpoint = self._replication_endpoint
        if endpoint is None or changefeed_id != endpoint["changefeed_id"]:
            raise ValueError(
                "TiDB replication execution update requires the registered changefeed: "
                f"requested={changefeed_id!r}, registered="
                f"{None if endpoint is None else endpoint['changefeed_id']!r}"
            )
        allowed = {"max_txn_row", "worker_count", "batch_dml_enable"}
        unknown = sorted(set(parameters) - allowed)
        if unknown:
            raise ValueError(
                "TiDB replication execution update contains unsupported parameters: "
                f"changefeed_id={changefeed_id!r}, unknown={unknown!r}, allowed={sorted(allowed)!r}"
            )
        if not parameters:
            raise ValueError(
                "TiDB replication execution update requires at least one parameter: "
                f"changefeed_id={changefeed_id!r}"
            )
        previous = self._replication_sink_config()
        current = dict(previous)
        if "max_txn_row" in parameters:
            max_txn_row = int(parameters["max_txn_row"])
            if not 1 <= max_txn_row <= 256:
                raise ValueError(
                    "TiDB replication max_txn_row is outside the public range: "
                    f"changefeed_id={changefeed_id!r}, max_txn_row={max_txn_row!r}, allowed=1..256"
                )
            current["max_txn_row"] = max_txn_row
        if "worker_count" in parameters:
            worker_count = int(parameters["worker_count"])
            if not 1 <= worker_count <= 32:
                raise ValueError(
                    "TiDB replication worker_count is outside the public range: "
                    f"changefeed_id={changefeed_id!r}, worker_count={worker_count!r}, allowed=1..32"
                )
            current["worker_count"] = worker_count
        if "batch_dml_enable" in parameters:
            batch_dml_enable = parameters["batch_dml_enable"]
            if not isinstance(batch_dml_enable, bool):
                raise TypeError(
                    "TiDB replication batch_dml_enable must be boolean: "
                    f"changefeed_id={changefeed_id!r}, value={batch_dml_enable!r}"
                )
            current["batch_dml_enable"] = batch_dml_enable

        parsed = urlsplit(endpoint["sink_uri"])
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query.update({
            "worker-count": str(current["worker_count"]),
            "max-txn-row": str(current["max_txn_row"]),
            "batch-dml-enable": "true" if current["batch_dml_enable"] else "false",
        })
        sink_uri = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))
        completed = subprocess.run(
            [
                "docker",
                "exec",
                endpoint["container_name"],
                "/cdc",
                "cli",
                "changefeed",
                "update",
                "--server=http://127.0.0.1:8300",
                "--changefeed-id",
                changefeed_id,
                "--sink-uri",
                sink_uri,
                "--no-confirm",
            ],
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "TiDB replication execution update failed: "
                f"changefeed_id={changefeed_id!r}, requested={parameters!r}, "
                f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
            )
        endpoint["sink_uri"] = sink_uri
        return {
            "changefeed_id": changefeed_id,
            "previous": previous,
            "current": current,
            "controller_acknowledgement": completed.stdout.strip(),
        }

    def _changefeed_lifecycle(self, operation: str, changefeed_id: str) -> Dict[str, Any]:
        if operation not in {"pause", "resume"}:
            raise ValueError(
                f"Unsupported changefeed lifecycle operation: operation={operation!r}"
            )
        output = self._run_ticdc_cli([
            operation,
            "--server=http://127.0.0.1:8300",
            f"--changefeed-id={changefeed_id}",
        ])
        return {"changefeed_id": changefeed_id, "operation": operation, "output": output}

    def _recreate_changefeed(self, changefeed_id: str, start_ts: int) -> Dict[str, Any]:
        if start_ts <= 0:
            raise ValueError(
                f"changefeed recreate requires a positive start_ts: changefeed_id={changefeed_id!r}, start_ts={start_ts}"
            )
        self._run_ticdc_cli([
            "remove",
            "--server=http://127.0.0.1:8300",
            f"--changefeed-id={changefeed_id}",
        ])
        from time import monotonic, sleep
        from urllib.error import HTTPError

        deadline = monotonic() + 60
        while monotonic() < deadline:
            try:
                self.replication_status(changefeed_id)
            except HTTPError as exc:
                if exc.code == 404:
                    break
                if exc.code == 400:
                    body = exc.read().decode("utf-8", errors="replace")
                    if "CDC:ErrChangeFeedNotExists" in body:
                        break
                raise
            sleep(1)
        else:
            raise RuntimeError(
                f"TiCDC changefeed did not disappear after remove: changefeed_id={changefeed_id!r}"
            )
        output = self._run_ticdc_cli([
            "create",
            "--server=http://127.0.0.1:8300",
            "--sink-uri=mysql://root@mysql-0:3306/",
            f"--changefeed-id={changefeed_id}",
            f"--start-ts={int(start_ts)}",
            "--no-confirm",
        ])
        return {
            "changefeed_id": changefeed_id,
            "state": "running",
            "start_ts": int(start_ts),
            "output": output,
        }


    @staticmethod
    def _agent_import_status(status: Dict[str, Any]) -> Dict[str, Any]:
        import_status = status["import"]
        active_job = {
            "job_id": status["job_id"],
            "target": status["target"],
            "state": import_status["state"],
            "phase": import_status["phase"],
            "reconfigure_required": import_status["reconfigure_required"],
            "exit_code": import_status["exit_code"],
            "expected_rows": import_status["expected_rows"],
            "target_rows": import_status["target_rows"],
            "phase1_rows": import_status["phase1_rows"],
            "duration_seconds": import_status["duration_seconds"],
            "source_directory": status["source"]["directory"],
            "checkpoint_directory": status["source"]["checkpoint_directory"],
        }
        return {
            "precheck": status["precheck"],
            "checkpoint_enabled": status["checkpoint_enabled"],
            "safe_bounds": status["safe_bounds"],
            # 列表位置不能携带信号：事故 job 固定排第一就是"第一个=事故"的捷径。
            "jobs": sorted(
                [active_job, *status["other_jobs"]],
                key=lambda job: job["job_id"],
            ),
        }






    def execute_bootstrap_sql(self, sql_query: str) -> str:
        """Execute scenario-owned setup SQL without changing the Agent SQL contract."""
        import pymysql

        try:
            connection = self._connect(
                timeout_seconds=self.BOOTSTRAP_SQL_TIMEOUT_SECONDS,
            )
            try:
                return self._execute_sql_on_connection(connection, sql_query)
            finally:
                connection.close()
        except pymysql.MySQLError as exc:
            return json.dumps({
                "status": "error",
                "error": f"TiDB bootstrap SQL failed: query={sql_query!r}, error={exc}",
            }, ensure_ascii=False)

    @Tool(
        description=(
            "对集群资源执行通用观察和维护。resource 表示资源类别，operation 表示通用操作，"
            "target 标识资源，parameters 承载该资源的具体值。返回原始资源状态或操作结果，"
            "不返回场景、故障或修复结论。"
        ),
        arg_descriptions={
            "resource": "service, store, region, mvcc_lock, gc_status, storage_maintenance, unsafe_recovery, pd_identity, pd_recovery, clock_status, dr_replication, restore, operator, scheduler, config, network, router, changefeed_diagnostics, gc_safepoint, changefeed, job, release 或 monitoring",
            "operation": "list, get, start, refresh_binding, stop, restart, update, remove, pause, resume, recreate, wait 或 verify",
            "target": "稳定资源身份；观察集合时可不传",
            "parameters": "资源操作参数，例如标识符、配置值、时间点或等待秒数",
        },
        definition=TIDB_TOOL_DEFINITIONS["manage_cluster"],
    )
    def manage_cluster(
        self,
        resource: str,
        operation: str,
        target: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self.cluster_control_type(self).execute(resource, operation, target, parameters)

    def execute_sql_with_timeout(self, sql_query: str, timeout_seconds: int) -> str:
        import pymysql

        conn = self._connect(self.dbname, timeout_seconds=timeout_seconds)
        try:
            return self._execute_sql_on_connection(conn, sql_query)
        except pymysql.MySQLError as exc:
            return json.dumps({
                "status": "error",
                "error": f"TiDB SQL failed: query={sql_query!r}, error={exc}",
            }, ensure_ascii=False)
        finally:
            conn.close()

    def _downstream_connection(self):
        import pymysql
        from pymysql.constants import CLIENT

        port = self.deployment.downstream_port
        if port is None:
            raise RuntimeError(f"TiDB replication downstream is not configured: run_id={self.run_id!r}")
        return pymysql.connect(
            host="127.0.0.1",
            port=port,
            user="root",
            password="",
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=5,
            read_timeout=self.sql_timeout_seconds,
            write_timeout=self.sql_timeout_seconds,
            client_flag=CLIENT.MULTI_STATEMENTS,
        )

    def _ticdc_url(self, path: str) -> str:
        port = self.deployment.ticdc_port
        if port is None:
            raise RuntimeError(f"TiCDC is not configured: run_id={self.run_id!r}")
        return f"http://127.0.0.1:{port}{path}"

    def replication_status(self, changefeed_id: str) -> dict:
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", changefeed_id):
            raise ValueError(f"Invalid TiCDC changefeed_id: {changefeed_id!r}")
        from urllib.request import urlopen

        endpoint = self._replication_endpoint
        if endpoint is not None:
            if changefeed_id != endpoint["changefeed_id"]:
                raise ValueError(
                    "External TiCDC status requires the registered changefeed: "
                    f"requested={changefeed_id!r}, registered={endpoint['changefeed_id']!r}"
                )
            url = (
                f"http://{endpoint['host']}:{endpoint['port']}/api/v1/changefeeds/"
                f"{changefeed_id}"
            )
        else:
            url = self._ticdc_url(f"/api/v1/changefeeds/{changefeed_id}")
        with urlopen(url, timeout=5) as response:
            payload = json.load(response)
        if not isinstance(payload, dict):
            raise TypeError(
                f"TiCDC changefeed status must be an object: changefeed_id={changefeed_id!r}, "
                f"payload_type={type(payload).__name__}"
            )
        return payload

    def _run_ticdc_cli(self, arguments: list[str]) -> str:
        endpoint = self._replication_endpoint
        if endpoint is not None:
            completed = subprocess.run(
                [
                    "docker",
                    "exec",
                    endpoint["container_name"],
                    "/cdc",
                    "cli",
                    "changefeed",
                    *arguments,
                ],
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    "External TiCDC CLI command failed: "
                    f"container={endpoint['container_name']!r}, arguments={arguments!r}, "
                    f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
                )
            return completed.stdout.strip()
        return self.deployment.exec("ticdc/ticdc-0", ["/cdc", "cli", "changefeed", *arguments])

    @Tool(
        description="读取指定集群组件的可见日志；默认返回最多 200 行，支持按行号范围或关键字上下文读取。",
        arg_descriptions={
            "target": "稳定组件身份，例如 pd/pd-0、tikv/tikv-0、tidb/tidb-0 或 ticdc/ticdc-0",
            "lines": "尾部行数，默认 200，最大 200",
            "start_line": "可选的 1-based 起始行号；传入后按范围读取日志",
            "end_line": "可选的 1-based 结束行号，闭区间；-1 表示最后一行",
            "match_key": "可选关键字；返回每条命中行的上一行到下两行上下文，大小写不敏感",
            "start_timestamp": "可选的冻结历史窗口起点；必须与 end_timestamp 一起提供",
            "end_timestamp": "可选的冻结历史窗口终点；必须与 start_timestamp 一起提供",
        },
        definition=TIDB_TOOL_DEFINITIONS["read_log"],
    )
    def read_log(
        self,
        target: str,
        lines: int = 200,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        match_key: Optional[str] = None,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None,
    ) -> str:
        page_limit = min(max(int(lines), 1), 200)
        try:
            if (start_timestamp is None) != (end_timestamp is None):
                raise ValueError("read_log.start_timestamp and read_log.end_timestamp must be provided together")
            if start_timestamp is not None:
                if self._history_timeline is None or self._case is None:
                    raise RuntimeError(f"Frozen historical logs are unavailable: run_id={self.run_id!r}")
                if not target:
                    raise ValueError("Historical log reads require an explicit component target")
                start_ms = parse_utc_timestamp(start_timestamp, "start_timestamp")
                end_ms = parse_utc_timestamp(end_timestamp, "end_timestamp")
                if start_ms >= end_ms:
                    raise ValueError(
                        "Historical log window must be positive: "
                        f"start_timestamp={start_timestamp!r}, end_timestamp={end_timestamp!r}"
                    )
                records = self._history_timeline.record_store.query(
                    source=HistoricalRecordSource.COMPONENT_LOG,
                    start_ms=start_ms,
                    end_ms=end_ms,
                    target=target,
                    filters=None,
                    limit=min(page_limit, self._case.frozen_history.max_history_records_per_response),
                )["records"]
                content = "\n".join(
                    f"{record['timestamp']} {record.get('message', '')}" for record in records
                )
                page = self._slice_log_output(content, page_limit, start_line, end_line, match_key)
                page["page_limit"] = page_limit
                return json.dumps(
                    {"status": "success", "target": target, "records": records, **page},
                    ensure_ascii=False,
                )
            external = self._replication_endpoint
            if external is not None and target == "ticdc/ticdc-0":
                result = subprocess.run(
                    ["docker", "logs", "--timestamps", external["container_name"]],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(
                        f"TiCDC log read failed: target={target!r}, "
                        f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
                    )
                visible = (result.stdout + result.stderr).splitlines()
                page = self._slice_log_output(
                    "\n".join(visible),
                    page_limit,
                    start_line,
                    end_line,
                    match_key,
                )
                page["content"], page["content_truncated"] = self._bound_external_log_content(
                    page["content"].splitlines()
                )
                page["page_limit"] = page_limit
                if not page["content"] and match_key:
                    page["content"] = f"(no log entries matched match_key: {match_key})"
                return json.dumps({"status": "success", "target": target, **page}, ensure_ascii=False)
            if external is not None and target == "downstream/mysql-0":
                result = subprocess.run(
                    ["docker", "logs", "--timestamps", external["downstream_container_name"]],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(
                        f"downstream log read failed: target={target!r}, "
                        f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
                    )
                visible = (result.stdout + result.stderr).splitlines()
                page = self._slice_log_output(
                    "\n".join(visible),
                    page_limit,
                    start_line,
                    end_line,
                    match_key,
                )
                page["content"], page["content_truncated"] = self._bound_external_log_content(
                    page["content"].splitlines()
                )
                page["page_limit"] = page_limit
                if not page["content"] and match_key:
                    page["content"] = f"(no log entries matched match_key: {match_key})"
                return json.dumps({"status": "success", "target": target, **page}, ensure_ascii=False)
            if target in self.additional_log_sources:
                content = self.read_additional_log(target)
                page = self._slice_log_output(content, page_limit, start_line, end_line, match_key)
                page["content"], page["content_truncated"] = self._bound_external_log_content(
                    page["content"].splitlines()
                )
                page["page_limit"] = page_limit
                if not page["content"] and match_key:
                    page["content"] = f"(no log entries matched match_key: {match_key})"
                return json.dumps({"status": "success", "target": target, **page}, ensure_ascii=False)
            if target not in self.deployment.NODES:
                raise ValueError(
                    f"Unknown TiDB target {target!r}; expected one of {self.deployment.list_nodes()}"
                )
            all_lines = self.deployment.read_logs(target, lines=10000).splitlines()
            visible = all_lines[self._log_visible_lines.get(target, 0):]
            page = self._slice_log_output(
                "\n".join(visible),
                page_limit,
                start_line,
                end_line,
                match_key,
            )
            if match_key:
                page["content"], content_truncated = self._bound_external_log_content(
                    page["content"].splitlines()
                )
                if content_truncated:
                    page["content_truncated"] = True
            page["page_limit"] = page_limit
            if not page["content"] and match_key:
                page["content"] = f"(no log entries matched match_key: {match_key})"
            return json.dumps({"status": "success", "target": target, **page}, ensure_ascii=False)
        except (ValueError, RuntimeError) as exc:
            return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)

    @classmethod
    def _bound_external_log_content(cls, lines: list[str]) -> tuple[str, bool]:
        chunks = []
        content_length = 0
        truncated = False
        for line in lines:
            if len(line) > cls.EXTERNAL_LOG_MAX_LINE_CHARS:
                marker = " ... [line truncated by TiDBEnv]"
                line = line[: cls.EXTERNAL_LOG_MAX_LINE_CHARS - len(marker)] + marker
                truncated = True
            separator_length = 1 if chunks else 0
            remaining = cls.EXTERNAL_LOG_MAX_CONTENT_CHARS - content_length - separator_length
            if remaining <= 0:
                truncated = True
                break
            if len(line) > remaining:
                marker = " ... [content truncated by TiDBEnv]"
                if remaining <= len(marker):
                    chunks.append(marker[:remaining])
                else:
                    chunks.append(line[: remaining - len(marker)] + marker)
                truncated = True
                break
            chunks.append(line)
            content_length += separator_length + len(line)
        return "\n".join(chunks), truncated

    def get_deployment(self) -> BaseDeployment:
        return self.deployment


    def read_additional_log(self, target: str) -> str:
        raise NotImplementedError(f"Log source has no reader: environment={type(self).__name__}, target={target!r}")


class TiDBBusinessChangeEnv(TiDBEnv):
    """TiDB environment exposing the SQL-backed DM control plane."""

    def __init__(
        self,
        *,
        run_id: Optional[str] = None,
        workload=None,
        deployment: Optional[BaseDeployment] = None,
        port_base: int = 4000,
        user: str = "root",
        password: str = "",
        dbname: str = "test",
        sample_interval_sec: float = 2.0,
        return_window_seconds: int = 60,
        workload_runner_config: Optional[Dict[str, Any]] = None,
        image_group_key: Optional[str] = None,
    ):
        super().__init__(
            run_id=run_id,
            workload=workload,
            deployment=deployment,
            port_base=port_base,
            user=user,
            password=password,
            dbname=dbname,
            sample_interval_sec=sample_interval_sec,
            return_window_seconds=return_window_seconds,
            workload_runner_config=workload_runner_config,
            image_group_key=image_group_key,
        )
