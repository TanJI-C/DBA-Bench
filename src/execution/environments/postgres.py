from collections import deque
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
import inspect
import json
import os
import re
import subprocess
import threading
import time
from typing import Any, Dict, Mapping, Optional, Sequence

from src.agent_language import agent_text
from src.database.system import DatabaseSystem
from src.execution.deployments.base import BaseDeployment
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.base import BaseEnv
from src.execution.environments.sql import (
    PG_SQL_RESULT_MAX_BYTES,
    PG_SQL_RESULT_MAX_ROWS,
    SQL_TRUNCATION_HINT,
    SQL_TRUNCATION_HINT_EN,
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
)
from src.execution.history.records import (
    CapturedRecords,
    HistoricalRecordSource,
    HistoricalCoverage,
)
from src.execution.history.sql_archive import FrozenHistoricalSqlArchive
from src.execution.history.timeline import FrozenHistoricalTimeline
from src.execution.postgres_history import (
    ADDITIVE_COUNTER_FIELDS,
    PG_STATEMENT_SNAPSHOT_SQL,
    PgStatementCounters,
    PgStatementSnapshot,
    build_slow_query_records_from_logs,
    build_topsql_delta_records,
    capture_statement_snapshot,
    parse_postgres_log_records,
    reject_postgres_public_historical_sql,
)
from src.execution.postgres_metrics import (
    LivePostgresSamplerMetricProvider,
    POSTGRES_METRIC_CATALOG,
    postgres_default_query_metrics_tool_definition,
    PostgresScenarioMetricCatalog,
    postgres_query_metrics_tool_definition,
)
from src.execution.sampler_grid import SAMPLER_LAG_TOLERANCE_INTERVALS, SamplerGridStrikes
from src.execution.specs import PostgresCaseRuntime
from src.execution.tools import Tool, lazy_agent_text
from src.knowledge.pg_knowledge_base import PGKnowledgeBase


HOST_PROC_ROOT = "/proc"
HOST_CGROUP_ROOT = "/sys/fs/cgroup"


def _bounded_cpu_percent(cpu_us_delta: int, elapsed_us: int, cpus: float) -> float:
    """Convert cgroup CPU usage to the catalog's bounded percentage metric."""
    raw_percent = (cpu_us_delta / elapsed_us / cpus) * 100.0
    return round(min(100.0, max(0.0, raw_percent)), 2)


def _pg_unavailable_error() -> str:
    return agent_text(
        zh="PostgreSQL 服务未运行或无法连接。请使用 manage_instance('start') 启动服务。",
        en="The PostgreSQL service is not running or cannot be reached. Use manage_instance('start') to start the service.",
    )


class PGEnv(BaseEnv):
    """
    单机 PostgreSQL 环境。
    使用 PGDockerDeployment 进行容器管理。
    """

    # Crash recovery in a small container can take minutes (WAL replay may
    # itself OOM and restart), so one 180s window is not enough. The sampler
    # opens a fresh window per round and only dies after all rounds fail.
    SAMPLER_RECONNECT_TIMEOUT_SEC = 180.0
    SAMPLER_RECONNECT_MAX_ROUNDS = 3
    # Agent-facing SQL shares TiDB's sql_timeout_seconds=35: one runaway
    # diagnostic query (temp spill / unbounded write) must cancel, not fill
    # the disk and kill the environment mid-run. Workload/sampler pools keep
    # their own connections and are unaffected.
    SQL_STATEMENT_TIMEOUT_SECONDS = 35
    # Grid tolerance lives in src/execution/sampler_grid.py and is shared with
    # the TiDB metric-capture grid alignment.

    system = DatabaseSystem.POSTGRESQL

    TOOL_PROFILES = {
        "general_knowledge": (
            "query_metrics",
            "execute_sql",
            "manage_instance",
            "read_log",
            "query_general_knowledge_base",
            "help",
            "submit",
            "exit",
        ),
        "hierarchical_knowledge": (
            "query_metrics",
            "execute_sql",
            "manage_instance",
            "read_log",
            "query_hierarchical_knowledge_base",
            "help",
            "submit",
            "exit",
        ),
        "no_knowledge": (
            "query_metrics",
            "execute_sql",
            "manage_instance",
            "read_log",
            "help",
            "submit",
            "exit",
        ),
        "db_gpt": (
            "whether_is_abnormal_metric",
            "match_diagnose_knowledge",
            "optimize_index_selection",
            "query_metrics",
            "execute_sql",
            "manage_instance",
            "read_log",
            "help",
            "submit",
            "exit",
        ),
    }

    # Keep the Agent surface limited to raw environment observations and
    # scenario-owned providers. SQL-derived detail remains available through
    # execute_sql or direct internal query_metrics() calls.
    AGENT_METRICS = frozenset({
        "cpu",
        "memory",
        "disk_io",
        "active_connections",
        "disk_usage",
        "qps",
        "cache_hit_ratio",
        "workload_activity",
        "filesystem_io",
        "bufferio_waiters",
        "host_pressure",
        "partition_lifecycle",
    })
    FROZEN_HISTORY_PUBLIC_TOOLS = (
        "query_metrics",
        "execute_sql",
        "manage_instance",
        "read_log",
        "help",
        "submit",
        "exit",
    )

    def _frozen_history_public_tools(self) -> tuple[str, ...]:
        tools = [
            "query_metrics",
            "execute_sql",
            "manage_instance",
            "read_log",
        ]
        if self.tool_profile == "general_knowledge":
            tools.append("query_general_knowledge_base")
        elif self.tool_profile == "hierarchical_knowledge":
            tools.append("query_hierarchical_knowledge_base")
        elif self.tool_profile == "db_gpt":
            tools.extend((
                "whether_is_abnormal_metric",
                "match_diagnose_knowledge",
                "optimize_index_selection",
            ))
        elif self.tool_profile != "no_knowledge":
            raise ValueError(
                f"Unsupported PGEnv tool_profile for frozen-history surface: tool_profile={self.tool_profile!r}"
            )
        tools.extend(("help", "submit", "exit"))
        return tuple(tools)

    def select_tool_profile(self, tool_profile: str) -> None:
        self.tool_profile = tool_profile
        try:
            selected_tools = self.TOOL_PROFILES[tool_profile]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported PGEnv tool_profile: {tool_profile}. "
                f"Supported profiles: {', '.join(sorted(self.TOOL_PROFILES))}"
            ) from exc
        self._configure_tools(selected_tools)

    def __init__(self,
                 workload=None,
                 deployment: Optional[BaseDeployment] = None,
                 host: str = "localhost",
                 port: int = 5432,
                 user: str = "postgres",
                 password: str = "password",
                 dbname: str = "testdb",
                 sample_interval_sec: int = 2,
                 tool_profile: str = "general_knowledge",
                 enabled_tools: Optional[Sequence[str]] = None,
                 allow_sampler_jitter: bool = False,
                 allow_sampler_reconnect: bool = False):
        self.tool_profile = tool_profile
        selected_tools = enabled_tools
        if selected_tools is None:
            try:
                selected_tools = self.TOOL_PROFILES[self.tool_profile]
            except KeyError as exc:
                raise ValueError(
                    f"Unsupported PGEnv tool_profile: {self.tool_profile}. "
                    f"Supported profiles: {', '.join(sorted(self.TOOL_PROFILES))}"
                ) from exc
        super().__init__(workload, deployment, enabled_tools=selected_tools)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        if not isinstance(sample_interval_sec, int) or isinstance(sample_interval_sec, bool) or sample_interval_sec <= 0:
            raise ValueError(f"PostgreSQL sample_interval_sec must be a positive integer: sample_interval_sec={sample_interval_sec!r}")
        if not isinstance(allow_sampler_jitter, bool):
            raise ValueError(f"PostgreSQL allow_sampler_jitter must be boolean: value={allow_sampler_jitter!r}")
        if not isinstance(allow_sampler_reconnect, bool):
            raise ValueError(
                f"PostgreSQL allow_sampler_reconnect must be boolean: value={allow_sampler_reconnect!r}"
            )
        self.sample_interval_sec = sample_interval_sec
        self.allow_sampler_jitter = allow_sampler_jitter
        self.allow_sampler_reconnect = allow_sampler_reconnect
        self._metric_catalog = POSTGRES_METRIC_CATALOG
        self._metric_service = MetricService(
            catalog=self._metric_catalog,
            live=LivePostgresSamplerMetricProvider(sample_interval_sec=sample_interval_sec),
        )
        self._sampler_thread: Optional[threading.Thread] = None
        self._sampler_stop = threading.Event()
        self._sampler_condition = threading.Condition()
        self._sampler_conn = None  # 后台线程独立 DB 连接
        self._sampler_reconnected = False
        self._pgss_sampler_reset_observed = False
        self._sampler_failure: Exception | None = None
        self._sampler_grid_strikes = SamplerGridStrikes()
        self._expected_sampler_disconnect_reason: str | None = None
        self._expected_sampler_disconnect_evidence: dict[str, str] | None = None
        self._sampler_last_timestamp_ms: int | None = None
        self._host_cgroup_base: str | None = None
        self._pg_statement_snapshots: deque[PgStatementSnapshot] = deque(maxlen=300)
        self._pg_statement_excluded_queryids: frozenset[int] = frozenset()
        self._case = None
        self._history_timeline: FrozenHistoricalTimeline | None = None
        self._history_sql_archive: FrozenHistoricalSqlArchive | None = None
        # workload runner：后台持续发业务查询，制造"多 fingerprint 噪声"让 agent 自己挑慢的。
        # runner 由 Orchestrator.setup() 启动，env 仅持引用用于查询和 teardown。
        self._workload_runner = None
        # pg_stat_statements 启动基线：deploy 完成时记录的 (userid,dbid,queryid)→counters，
        # topsql 查询时减去基线，从而剔除初始化 SQL 影响、又不破坏历史。
        self._pgss_baseline: PgStatementSnapshot | None = None
        # metrics_hidden() 用：进入 with 块时拍 enter 快照，退出时与 exit 快照差分合入
        # _pgss_baseline，让块内执行的 SQL 对 topsql / slow_queries(finished) 隐身。
        # 用 depth 计数支持嵌套，仅最外层进出生效。
        self._metrics_hidden_depth: int = 0
        self._metrics_hidden_enter_snap: PgStatementSnapshot | None = None
        self._metrics_hidden_allow_pgss_reset: bool | None = None
        self._pg_log_visible_offsets: dict[str, int] = {}
        self._pg_log_hidden_enter_offsets: dict[str, int] | None = None
        self._pg_knowledge_bases: Dict[str, PGKnowledgeBase] = {}
        self._scenario_metric_provider = None
        self._pgbouncer_endpoint: Optional[Dict[str, object]] = None
        self._pgbouncer_runtime_overrides: Dict[str, str] = {}
        self._workload_connection_endpoints: Dict[str, Dict[str, object]] = {}

        if self.deployment is None:
            init_sql_path = None
            workload_data_dir = None
            dataset_manifest_path = None
            image_tag = "default"
            # 临时文件密集的校准负载需要磁盘余量，默认给 8192MB；workload 路径会覆盖成 tpcds 默认值。
            disk_quota_mb = 8192

            if self.workload is not None:
                init_sql_path = self.workload.get_init_sql_path()
                workload_data_dir = self.workload.data_dir
                dataset_manifest_path = self.workload.manifest_path
                image_tag = self.workload.workload_name
                disk_quota_mb = getattr(self.workload, "disk_quota_mb", 8192)

            self.deployment = PGDockerDeployment(
                container_name="aiopsbench-pg",
                postgres_user=user,
                postgres_password=password,
                postgres_db=dbname,
                port=port,
                init_sql_path=init_sql_path,
                workload_data_dir=workload_data_dir,
                dataset_manifest_path=dataset_manifest_path,
                image_name=f"aiopsbench-pg-{image_tag}:latest",
                # 512MB/1CPU 是 Light TPC-DS 在 30s statement timeout 内能跑完的最低配额。
                # resources 参与 baseline 文件命名，改配额会切换到新 baseline 文件。
                # disk_quota 由 env 顶部 disk_quota_mb 传入（workload 默认 8192）。
                resources={
                    "cpus": 1.0,
                    "memory_mb": 512,
                    "shm_size": "256m",
                    "disk_quota_mb": disk_quota_mb,
                },
            )

    def metric_history_catalog(self):
        return self._metric_catalog

    def validate_metric_history_case(self, spec, background_workload) -> None:
        spec.validate(background_workload)
        catalog = self.metric_history_catalog()
        for metric in spec.required_metrics:
            catalog.definition(metric)
            catalog.target_variants(metric, self.deployment)
        for decoy in spec.decoys:
            definition = catalog.definition(decoy.metric)
            if decoy.field not in definition.value_fields:
                raise ValueError(
                    f"Frozen-history decoy field is not in PostgreSQL catalog: decoy_id={decoy.decoy_id!r}, "
                    f"metric={decoy.metric!r}, field={decoy.field!r}, fields={definition.value_fields!r}"
                )
            # HistoryDecoySpec.target selects an assembler source series; it is
            # not the Agent-facing MetricQuery.target contract. Run-local alias
            # targets cannot be validated at configure time and are matched by
            # the assembler's benign-source selection instead.
        unsupported = set(spec.record_sources) - set(HistoricalRecordSource)
        if unsupported:
            raise ValueError(
                f"PostgreSQL frozen history has unsupported record sources: "
                f"sources={sorted(item.value for item in unsupported)!r}"
            )

    def metric_history_warmup_seconds(self, required_metrics: tuple[str, ...]) -> float:
        provider = getattr(self, "_scenario_metric_provider", None)
        provider_warmup = getattr(provider, "metric_history_warmup_seconds", None)
        if callable(provider_warmup):
            return float(provider_warmup())
        return max(
            float(self.sample_interval_sec * 2),
            max(float(self.metric_history_catalog().definition(metric).lookback_seconds) for metric in required_metrics),
        )

    def configure_case(self, case) -> None:
        super().configure_case(case)
        self._case = case
        adapter = (
            case.frozen_history_adapter
            if case.frozen_history is not None
            else None
        )
        if adapter is not None:
            if not callable(getattr(adapter, "configure", None)) or not callable(
                getattr(adapter, "metric_definitions", None)
            ):
                raise TypeError(
                    "PostgreSQL frozen history adapter must expose configure and metric_definitions: "
                    f"adapter={type(adapter).__name__!r}, case={case.case_id!r}"
                )
            adapter.configure(self, case)
            self._scenario_metric_provider = adapter
            self._metric_catalog = PostgresScenarioMetricCatalog(adapter)
            history_spec = case.frozen_history
            max_points = max(
                300,
                (
                    max(history_spec.normal_capture_seconds, history_spec.fault_capture_seconds)
                    + self.sample_interval_sec - 1
                ) // self.sample_interval_sec + 60,
            )
            self._pg_statement_snapshots = deque(self._pg_statement_snapshots, maxlen=max_points)
            self._metric_service = MetricService(
                catalog=self._metric_catalog,
                live=LivePostgresSamplerMetricProvider(
                    sample_interval_sec=self.sample_interval_sec,
                    max_points=max_points,
                    catalog=self._metric_catalog,
                ),
            )
        spec = getattr(case, "frozen_history", None)
        if spec is not None:
            self.validate_metric_history_case(spec, case.background_workload)
            self._configure_tools(self._frozen_history_public_tools())
            self._refresh_metric_query_tool_spec()

    def _refresh_metric_query_tool_spec(self) -> None:
        definition = postgres_query_metrics_tool_definition(self._metric_catalog)
        history_spec = getattr(getattr(self, "_case", None), "frozen_history", None)
        visible_metrics = tuple(
            getattr(history_spec, "required_metrics", self._metric_catalog.metric_names)
        )
        metric_names = sorted(set(visible_metrics))
        definition["metric_definitions"] = [
            item for item in definition["metric_definitions"]
            if item["metric_name"] in metric_names
        ]
        for parameter in definition["parameter_definitions"]:
            if parameter.get("parameter_name") == "metric_type":
                parameter["allowed_values"] = metric_names
        metric_description = agent_text(
            zh="指标类型，可选当前 Case catalog 值: ",
            en="Metric type; allowed values from the current Case catalog: ",
        ) + ", ".join(metric_names)
        self._enabled_tool_specs = [
            replace(
                spec,
                parameters=tuple(
                    replace(parameter, description=metric_description)
                    if parameter.name == "metric_type"
                    else parameter
                    for parameter in spec.parameters
                ),
                definition=deepcopy(definition),
            )
            if spec.alias == "query_metrics"
            else spec
            for spec in self._enabled_tool_specs
        ]
        self._alias_to_tool_spec = {
            spec.alias: spec for spec in self._enabled_tool_specs
        }

    def _additional_tool_help(self, tool_name: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        if tool_name in {"query_metrics", "execute_sql", "read_log"} and self._history_timeline is not None:
            spec = self._case.frozen_history
            result["runtime"] = {
                "timezone": "UTC",
                "available_start": format_utc_timestamp(self._history_timeline.visible_start_ms),
                "available_end": format_utc_timestamp(self._history_timeline.visible_end_ms),
                "base_step_seconds": self._history_timeline.base_step_seconds,
                "overview_step_seconds": self._history_timeline.overview_step_seconds,
                "max_history_query_seconds": spec.max_history_query_seconds,
                "enabled_sources": [source.value for source in spec.record_sources],
                "max_history_records_per_response": spec.max_history_records_per_response,
            }
        if tool_name == "execute_sql" and self._history_sql_archive is not None:
            result.setdefault("runtime", {})["connection_surfaces"] = [
                {
                    "name": "primary",
                    "kind": "database",
                    "description": agent_text(zh="当前 PostgreSQL 实例", en="Current PostgreSQL instance"),
                },
                {
                    "name": "history",
                    "kind": "frozen_history",
                    "description": agent_text(
                        zh="当前 Case 的只读冻结历史 SQL archive",
                        en="Read-only frozen history SQL archive of the current Case",
                    ),
                    "tables": ["statement_summary", "slow_query"],
                    "write_policy": "read_only",
                    "requires_utc_time_bounds": True,
                },
            ]
        if tool_name == "read_log" and self._history_timeline is not None:
            enabled = set(self._case.frozen_history.record_sources)
            historical_log_types = []
            if HistoricalRecordSource.COMPONENT_LOG in enabled:
                historical_log_types.append("pg_log")
            if HistoricalRecordSource.OPERATION_EVENT in enabled:
                historical_log_types.append("operation_event")
            result.setdefault("runtime", {})["historical_log_types"] = historical_log_types
        if tool_name == "query_metrics":
            provider = getattr(self, "_scenario_metric_provider", None)
            contract = getattr(provider, "agent_contract", None)
            if callable(contract):
                result["case_contract"] = contract()
        return result

    def configure_history_observability(self, spec) -> None:
        self._stop_sampler()
        if not self._ensure_connection():
            raise RuntimeError(
                f"Cannot configure PostgreSQL history observability: host={self.host!r}, port={self.port}, database={self.dbname!r}"
            )
        with self._conn.cursor() as cursor:
            cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'pg_stat_statements'")
            if cursor.fetchone() is None:
                raise RuntimeError(
                    f"PostgreSQL history requires pg_stat_statements extension: database={self.dbname!r}, "
                    f"image={getattr(self.deployment, 'image_name', None)!r}, required_preload='pg_stat_statements'"
                )
            cursor.execute("SHOW shared_preload_libraries")
            preload = str(cursor.fetchone()[0] or "")
            if "pg_stat_statements" not in {item.strip() for item in preload.split(",") if item.strip()}:
                raise RuntimeError(
                    f"PostgreSQL pg_stat_statements is not in shared_preload_libraries: database={self.dbname!r}, "
                    f"shared_preload_libraries={preload!r}"
                )
            for name, value in (
                ("timezone", "UTC"),
                ("log_timezone", "UTC"),
                ("log_line_prefix", "%m [%p] app=%a user=%u db=%d "),
                ("log_min_duration_statement", "0"),
                ("log_lock_waits", "on"),
            ):
                cursor.execute(f"ALTER SYSTEM SET {name} = '{value}'")
            cursor.execute("SELECT pg_reload_conf()")
            if cursor.fetchone()[0] is not True:
                raise RuntimeError("PostgreSQL pg_reload_conf() returned false while configuring history observability")
            reload_deadline = time.monotonic() + 10
            while True:
                cursor.execute(
                    "SELECT current_setting('timezone'), current_setting('log_timezone'), "
                    "current_setting('logging_collector'), current_setting('log_destination'), "
                    "current_setting('log_line_prefix'), current_setting('log_min_duration_statement'), "
                    "current_setting('log_lock_waits')"
                )
                (
                    timezone_value,
                    log_timezone_value,
                    logging_collector,
                    log_destination,
                    log_prefix,
                    log_duration,
                    log_lock_waits,
                ) = (str(value) for value in cursor.fetchone())
                if (
                    timezone_value.casefold() in {"utc", "etc/utc"}
                    and log_timezone_value.casefold() in {"utc", "etc/utc"}
                    and logging_collector.casefold() == "on"
                    and "stderr" in log_destination.casefold()
                    and all(part in log_prefix for part in ("%m", "%p", "%a", "%u", "%d"))
                    and log_duration == "0"
                    and log_lock_waits.casefold() == "on"
                ):
                    break
                if time.monotonic() >= reload_deadline:
                    raise RuntimeError(
                        "PostgreSQL history observability reload did not become active: "
                        f"timezone={timezone_value!r}, log_timezone={log_timezone_value!r}, "
                        f"logging_collector={logging_collector!r}, log_destination={log_destination!r}, "
                        f"log_line_prefix={log_prefix!r}, log_min_duration_statement={log_duration!r}, "
                        f"log_lock_waits={log_lock_waits!r}"
                    )
                time.sleep(0.1)
        required_prefix_parts = ("%m", "%p", "%a", "%u", "%d")
        utc_timezone_names = {"utc", "etc/utc"}
        if (
            timezone_value.casefold() not in utc_timezone_names
            or log_timezone_value.casefold() not in utc_timezone_names
        ):
            raise RuntimeError(
                f"PostgreSQL history timezone configuration is not UTC: timezone={timezone_value!r}, log_timezone={log_timezone_value!r}"
            )
        if logging_collector != "on" or "stderr" not in log_destination:
            raise RuntimeError(
                f"PostgreSQL logs are not capturable: logging_collector={logging_collector!r}, log_destination={log_destination!r}"
            )
        if any(part not in log_prefix for part in required_prefix_parts) or log_duration != "0":
            raise RuntimeError(
                f"PostgreSQL log prefix/duration contract is not active: log_line_prefix={log_prefix!r}, "
                f"log_min_duration_statement={log_duration!r}"
            )
        if log_lock_waits != "on":
            raise RuntimeError(f"PostgreSQL log_lock_waits is not active: log_lock_waits={log_lock_waits!r}")
        # pg_stat_statements updates the currently executing statement after its
        # result is produced, so one snapshot query cannot observe its own entry.
        capture_statement_snapshot(self._conn, int(time.time() * 1000))
        snapshot = capture_statement_snapshot(self._conn, int(time.time() * 1000) + 1)
        expected_query = " ".join(PG_STATEMENT_SNAPSHOT_SQL.split())
        collector_queryids = frozenset(
            key.queryid
            for key, counter in snapshot.counters.items()
            if " ".join(counter.query.split()) == expected_query
        )
        if not collector_queryids:
            raise RuntimeError(
                "PostgreSQL history collector queryid could not be identified by exact normalized SQL: "
                f"expected_query={expected_query!r}, observed_queries={tuple(sorted({counter.query for counter in snapshot.counters.values()}))!r}"
            )
        self._pg_statement_excluded_queryids = collector_queryids
        self._metric_service.live.reset()
        with self._metric_service.live.lock:
            self._pg_statement_snapshots.clear()
        with self._sampler_condition:
            self._sampler_last_timestamp_ms = None
        self._start_sampler()

    def capture_metric_history(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
        *,
        metric_targets: Mapping[str, tuple[str | None, ...]] | None = None,
        rate_windows: Mapping[str, int] | None = None,
    ) -> tuple[MetricFrame, ...]:
        provider = getattr(self, "_scenario_metric_provider", None)
        capture = getattr(provider, "capture_history", None)
        if callable(capture):
            return tuple(capture(metrics, start_epoch_ms, end_epoch_ms, step_seconds))
        with self._sampler_condition:
            while (
                self._sampler_last_timestamp_ms is None
                or self._sampler_last_timestamp_ms < end_epoch_ms
            ):
                self._raise_sampler_failure()
                if self._sampler_thread is None or self._sampler_stop.is_set():
                    raise RuntimeError(
                        "PostgreSQL metric capture cannot reach its requested end because the sampler is not running: "
                        f"requested_end_epoch_ms={end_epoch_ms}, last_timestamp_ms={self._sampler_last_timestamp_ms}"
                    )
                self._sampler_condition.wait()
        self._raise_sampler_failure()
        return self._metric_service.live.capture(metrics, start_epoch_ms, end_epoch_ms, step_seconds)

    @staticmethod
    def _history_snapshot_capacity(spec, sample_interval_sec: int) -> int:
        """Keep capture ticks plus sampler warm-up before the first window."""
        if sample_interval_sec <= 0:
            raise ValueError("sample_interval_sec must be positive")
        capture_seconds = max(int(spec.normal_capture_seconds), int(spec.fault_capture_seconds))
        warmup_seconds = max(60, int(spec.transition_seconds))
        return max(300, capture_seconds // sample_interval_sec + warmup_seconds // sample_interval_sec + 2)

    def capture_history_records(
        self,
        sources: tuple[HistoricalRecordSource, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
    ) -> CapturedRecords:
        provider = getattr(self, "_scenario_metric_provider", None)
        point_records: list = []
        interval_records: list = []
        coverage: list[HistoricalCoverage] = []
        if HistoricalRecordSource.COMPONENT_LOG in sources or HistoricalRecordSource.SLOW_QUERIES in sources:
            raw = self.deployment.read_logs_at_range(start_epoch_ms, end_epoch_ms)
            log_records = parse_postgres_log_records(raw, start_epoch_ms, end_epoch_ms)
            if HistoricalRecordSource.COMPONENT_LOG in sources:
                point_records.extend(log_records)
                coverage.append(HistoricalCoverage(
                    source=HistoricalRecordSource.COMPONENT_LOG,
                    target="postgres",
                    start_ms=start_epoch_ms,
                    end_ms=end_epoch_ms,
                ))
            if HistoricalRecordSource.SLOW_QUERIES in sources:
                point_records.extend(build_slow_query_records_from_logs(log_records))
                coverage.append(HistoricalCoverage(
                    source=HistoricalRecordSource.SLOW_QUERIES,
                    target="postgres",
                    start_ms=start_epoch_ms,
                    end_ms=end_epoch_ms,
                ))
        if HistoricalRecordSource.TOPSQL in sources:
            with self._metric_service.live.lock:
                snapshots = tuple(
                    snapshot
                    for snapshot in self._pg_statement_snapshots
                    if start_epoch_ms <= snapshot.timestamp_ms <= end_epoch_ms
                )
            expected = tuple(range(start_epoch_ms, end_epoch_ms + 1, self.sample_interval_sec * 1000))
            actual = tuple(snapshot.timestamp_ms for snapshot in snapshots)
            if actual != expected:
                raise RuntimeError(
                    f"PostgreSQL TopSQL snapshot coverage is incomplete: requested=({start_epoch_ms},{end_epoch_ms}), "
                    f"expected={expected!r}, actual={actual!r}"
                )
            for previous, current in zip(snapshots, snapshots[1:]):
                interval_records.extend(build_topsql_delta_records(
                    previous,
                    current,
                    excluded_queryids=self._pg_statement_excluded_queryids,
                ))
            coverage.append(HistoricalCoverage(
                source=HistoricalRecordSource.TOPSQL,
                target="postgres",
                start_ms=start_epoch_ms,
                end_ms=end_epoch_ms,
            ))
        provider = self._scenario_metric_provider
        if provider is not None:
            capture = getattr(provider, "capture_history_records", None)
            if callable(capture):
                scenario_records = capture(sources, start_epoch_ms, end_epoch_ms)
                point_records.extend(scenario_records.point_records)
                interval_records.extend(scenario_records.interval_records)
                coverage.extend(scenario_records.coverage)
        return CapturedRecords(
            point_records=tuple(point_records),
            interval_records=tuple(interval_records),
            coverage=tuple(coverage),
        )

    def _sample_additional_metrics(
        self,
        connection,
        timestamp_ms: int,
        base_values: Mapping[str, Mapping[str, float]],
    ) -> Mapping[str, Mapping[str, float]]:
        provider = self._scenario_metric_provider
        if provider is None:
            return {}
        sample = getattr(provider, "sample_metrics", None)
        if not callable(sample):
            raise TypeError(
                "PostgreSQL scenario metric provider must expose sample_metrics: "
                f"provider={type(provider).__name__!r}, case={self._case.case_id!r}"
            )
        values = sample(
            connection=connection,
            timestamp_ms=timestamp_ms,
            elapsed_seconds=float(self.sample_interval_sec),
            base_values=base_values,
        )
        if not isinstance(values, Mapping):
            raise TypeError(
                "PostgreSQL scenario metric provider returned non-mapping samples: "
                f"provider={type(provider).__name__!r}, values={values!r}"
            )
        return values

    def bind_metric_history(self, timeline: FrozenHistoricalTimeline) -> None:
        if self._case is None or getattr(self._case, "frozen_history", None) is None:
            raise RuntimeError(
                f"Cannot bind metric history to a non-history PostgreSQL Case: case={getattr(self._case, 'case_id', None)!r}"
            )
        if not isinstance(timeline, FrozenHistoricalTimeline):
            raise TypeError(f"PostgreSQL metric history must be FrozenHistoricalTimeline, got {type(timeline).__name__}")
        self._metric_service.bind_history(timeline.metric_provider)
        self._history_timeline = timeline
        spec = self._case.frozen_history
        self._history_sql_archive = FrozenHistoricalSqlArchive(
            timeline.record_store,
            max_rows=min(200, int(getattr(spec, "max_history_records_per_response", 200))),
            visible_start_ms=timeline.visible_start_ms,
            visible_end_ms=timeline.visible_end_ms,
            sql_dialect="postgres",
            require_time_bounds=True,
            max_response_bytes=PG_SQL_RESULT_MAX_BYTES,
        )
        self._configure_tools(self._frozen_history_public_tools())
        # Binding frozen history rebuilds the enabled tool list. Refresh the
        # case-owned metric contract afterward so the Agent never receives the
        # generic catalog after setup has completed.
        self._refresh_metric_query_tool_spec()
        refresh_case_tools = getattr(self, "_refresh_rpo_tool_specs", None)
        if callable(refresh_case_tools):
            refresh_case_tools()

    def observe_metric(self, metric_type: str, target: str | None = None) -> str:
        frame = self._metric_service.query_live(MetricQuery(metric=metric_type, target=target))
        start_ms, end_ms = self._metric_service.live.available_range
        return render_metric_frame(
            frame,
            available_start_ms=start_ms,
            available_end_ms=end_ms,
            requested_start_ms=start_ms,
            requested_end_ms=end_ms,
            step_seconds=frame.step_seconds,
        )

    def query_history(
        self,
        source: str,
        start_timestamp: str,
        end_timestamp: str,
        target: str | None = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> str:
        try:
            result = self._query_frozen_history_records(
                source=HistoricalRecordSource(source),
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                target=target,
                filters=filters,
                limit=limit,
            )
            return json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str)
        except (ValueError, RuntimeError, TypeError, KeyError) as exc:
            return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)

    def _query_frozen_history_records(
        self,
        *,
        source: HistoricalRecordSource,
        start_timestamp: str,
        end_timestamp: str,
        target: str | None,
        filters: Optional[Dict[str, Any]],
        limit: int,
    ) -> Dict[str, Any]:
        if self._history_timeline is None or self._case is None or getattr(self._case, "frozen_history", None) is None:
            raise RuntimeError(
                f"Frozen PostgreSQL history requires a bound frozen-history Case: case={getattr(self._case, 'case_id', None)!r}"
            )
        spec = self._case.frozen_history
        if source not in spec.record_sources:
            raise ValueError(
                f"History source is not enabled by Case: source={source.value!r}, "
                f"enabled={[item.value for item in spec.record_sources]!r}"
            )
        if limit <= 0 or limit > spec.max_history_records_per_response:
            raise ValueError(
                f"History record limit is outside Case budget: source={source.value!r}, limit={limit}, "
                f"max_history_records_per_response={spec.max_history_records_per_response}"
            )
        return self._history_timeline.record_store.query(
            source=source,
            start_ms=parse_utc_timestamp(start_timestamp, "start_timestamp"),
            end_ms=parse_utc_timestamp(end_timestamp, "end_timestamp"),
            target=target,
            filters=filters,
            limit=limit,
            max_window_seconds=getattr(spec, "max_history_query_seconds", None) or None,
            max_response_chars=min(
                PG_SQL_RESULT_MAX_BYTES,
                int(getattr(spec, "max_history_response_chars", PG_SQL_RESULT_MAX_BYTES)),
            ),
        )

    def deploy(self):
        """部署 PG 环境"""
        if self.deployment is None:
            raise RuntimeError("No deployment configured")

        if self.workload is not None:
            print(f"[Env:PGEnv] Preparing workload...")
            self.workload.prepare()

        print(f"[Env:PGEnv] Deploying PostgreSQL...")
        self.deployment.deploy()

        if not self.deployment.wait_for_ready(timeout=600):
            raise RuntimeError("Failed to deploy PostgreSQL: not ready")

        self._ensure_connection()
        if self.workload is not None and self.workload.workload_name == "tpcds":
            from src.workloads.tpcds import TPCDSWorkload

            if not isinstance(self.workload, TPCDSWorkload):
                raise TypeError(
                    "PGEnv workload name and implementation disagree: "
                    f"workload_name={self.workload.workload_name!r}, type={type(self.workload).__name__!r}"
                )
            self.workload.validate_database(self)
        # Frozen-history setup starts its shared workload runner before history
        # observability; avoid sampling the provider during the deployment gap.
        if self._scenario_metric_provider is None:
            self._start_sampler()
        self._snapshot_pgss_baseline()
        print(f"[Env:PGEnv] Deployment complete.")

    def configure_runtime(self, runtime: PostgresCaseRuntime) -> None:
        if not isinstance(runtime, PostgresCaseRuntime):
            raise TypeError(
                f"PGEnv requires PostgresCaseRuntime, got {type(runtime).__name__}"
            )
        if runtime.parameters is not None:
            self.deployment.postgres_runtime_options = runtime.parameters.as_command_line()
        self.deployment.host_port_offsets = runtime.host_ports.offsets
        if runtime.resources is not None:
            self.deployment.resources = {
                **self.deployment.resources,
                "cpus": runtime.resources.container_cpu_limit,
                "memory_mb": runtime.resources.container_memory_mb,
            }

    def base_snapshot_name(self, case) -> Optional[str]:
        if getattr(case, "snapshot_unsafe", False):
            return None
        return case.base_image_name

    def snapshot_name(self, scenario_id: str, case) -> Optional[str]:
        base_snapshot_name = self.base_snapshot_name(case)
        if base_snapshot_name is None:
            return None
        repository = base_snapshot_name.partition(":")[0]
        prefix = "aiopsbench-pg-"
        if not repository.startswith(prefix):
            raise ValueError(
                f"Unsupported PostgreSQL base snapshot: case={case.case_id!r}, "
                f"base_snapshot={base_snapshot_name!r}"
            )
        identity = f"{scenario_id}-{case.case_id}".replace("_", "-")
        return f"aiopsbench-pg-fault-{identity}:{repository.removeprefix(prefix)}"

    def snapshot_exists(self, snapshot_name: str) -> bool:
        return PGDockerDeployment.image_exists(snapshot_name)

    def select_snapshot(self, snapshot_name: str, base_snapshot_name: str) -> None:
        self.deployment.image_name = snapshot_name
        self.baseline_image_name = base_snapshot_name

    def save_snapshot(self, snapshot_name: str, labels: Dict[str, str]) -> None:
        import subprocess

        # 快照保存会 stop/start PostgreSQL（docker commit 前后）。后台 sampler
        # 与 reboot/restart 路径一样必须在停机窗口内暂停，否则 allow_sampler_
        # reconnect=False 时 sampler 线程会把停机当故障记录，run 在 teardown
        # 阶段整体失败。与 _run_lifecycle_with_sampler 保持同一语义。
        sampler_was_running = (
            self._sampler_thread is not None and self._sampler_thread.is_alive()
        )
        if sampler_was_running:
            self._stop_sampler()
        try:
            checkpoint = self.execute_sql("SET statement_timeout = '300s'; CHECKPOINT;")
            checkpoint_text = checkpoint if isinstance(checkpoint, str) else json.dumps(
                checkpoint, ensure_ascii=False, default=str
            )
            if '"status": "error"' in checkpoint_text.lower():
                raise RuntimeError(
                    f"PostgreSQL checkpoint failed before snapshot: result={checkpoint_text}"
                )
            deployment = self.deployment
            if not deployment.is_container_running():
                raise RuntimeError(
                    f"Cannot save PostgreSQL snapshot: container={deployment.container_name!r} is not running"
                )
            if not deployment.stop_pg():
                raise RuntimeError(
                    f"Cannot stop PostgreSQL before snapshot: container={deployment.container_name!r}"
                )
            command = ["docker", "commit"]
            for key, value in labels.items():
                command.extend(["--change", f"LABEL {key}={json.dumps(str(value))}"])
            command.extend([deployment.container_name, snapshot_name])
            result = subprocess.run(command, capture_output=True, text=True)
            if not deployment.start_pg():
                raise RuntimeError(
                    f"Cannot restart PostgreSQL after snapshot: container={deployment.container_name!r}, "
                    f"snapshot={snapshot_name!r}, commit_returncode={result.returncode}, "
                    f"commit_stderr={result.stderr.strip()!r}"
                )
            if result.returncode != 0:
                raise RuntimeError(
                    f"PostgreSQL snapshot commit failed: snapshot={snapshot_name!r}, "
                    f"container={deployment.container_name!r}, returncode={result.returncode}, "
                    f"stderr={result.stderr.strip()!r}"
                )
            if not deployment.wait_for_ready(timeout=600):
                raise RuntimeError(
                    f"PostgreSQL did not become ready after snapshot: snapshot={snapshot_name!r}"
                )
            if not self.reconnect():
                raise RuntimeError(
                    f"PostgreSQL reconnect failed after snapshot: snapshot={snapshot_name!r}, "
                    f"container={deployment.container_name!r}"
                )
            self.refresh_pgss_baseline()
        finally:
            if sampler_was_running:
                self._start_sampler()

    def _capture_pgss_snapshot(self) -> PgStatementSnapshot:
        if not self._ensure_connection():
            raise RuntimeError(
                f"PostgreSQL pg_stat_statements snapshot connection failed: host={self.host!r}, "
                f"port={self.port}, database={self.dbname!r}"
            )
        with self._conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'")
            if cursor.fetchone() is None:
                raise RuntimeError(
                    f"PostgreSQL pg_stat_statements snapshot requires installed extension: "
                    f"database={self.dbname!r}, image={getattr(self.deployment, 'image_name', None)!r}"
                )
        return capture_statement_snapshot(self._conn, int(time.time() * 1000))

    def _snapshot_pgss_baseline(self):
        """部署完成时刻拍一张 pg_stat_statements 快照，作为 topsql 减去初始化 SQL 累计的基线。

        不调用 pg_stat_statements_reset()——它会清空所有历史；这里改用差分模型，
        既保留全量历史给手动诊断，也允许 topsql 给出"故障注入后增量"视图。
        """
        snap = self._capture_pgss_snapshot()
        self._pgss_baseline = snap
        print(f"[Env:PGEnv] pg_stat_statements baseline snapshot: {len(snap.counters)} entries.")

    def refresh_pgss_baseline(self):
        # 场景注入器在隐藏准备工作后需要重拍 pgss baseline，保留手动刷新入口。
        return self._snapshot_pgss_baseline()

    @contextmanager
    def metrics_hidden(self, *, allow_pgss_reset: bool = False):
        """块内执行的 SQL 对 topsql / slow_queries(finished) 隐身。

        机制：进入时拍 pg_stat_statements 快照 enter，退出时拍 exit，将 (exit-enter) 增量
        合入 _pgss_baseline。topsql / slow_queries 内部已做 (current - baseline) delta 过滤，
        因此块内执行的 SQL 计数贡献被吸收，agent 看不到。

        - 仅作用于基于 pg_stat_statements 的指标；pg_stat_activity 实时态、cgroup 资源指标
          不受影响（这些指标本身在 SQL 跑完后就回到正常水位，不需要隐身）。
        - 同时推进 PostgreSQL 日志可见 offset，使故障注入期间的 reload/config 日志
          不会通过 read_log(pg_log) 泄露给 Agent；hidden 块之后的新日志仍可见。
        - 支持嵌套：用 depth 计数器，仅最外层 enter/exit 真正拍快照。
        - 跨 with 边界的 queryid（块前已有、块内继续执行）只吸收块内增量，块外执行仍可见。
        - 只有显式声明 allow_pgss_reset=True 的生命周期块才允许块内 PostgreSQL 重启或
          pg_stat_statements_reset() 使快照键消失；此时退出快照成为新的 baseline。
        - enter/exit snapshot 或日志 offset 读取失败直接抛错。
        """
        if self._metrics_hidden_depth == 0:
            self._metrics_hidden_enter_snap = self._capture_pgss_snapshot()
            self._pg_log_hidden_enter_offsets = self._pg_log_snapshot()
            self._metrics_hidden_allow_pgss_reset = allow_pgss_reset
        elif allow_pgss_reset and not self._metrics_hidden_allow_pgss_reset:
            raise RuntimeError(
                "PostgreSQL metrics_hidden nested block cannot enable pg_stat_statements reset "
                "after the outer block was created without allow_pgss_reset=True"
            )
        self._metrics_hidden_depth += 1
        try:
            yield
        finally:
            self._metrics_hidden_depth -= 1
            if self._metrics_hidden_depth == 0:
                enter_snap = self._metrics_hidden_enter_snap
                self._metrics_hidden_enter_snap = None
                reset_allowed = bool(self._metrics_hidden_allow_pgss_reset)
                self._metrics_hidden_allow_pgss_reset = None
                if enter_snap is None:
                    raise RuntimeError("PostgreSQL metrics_hidden exit has no enter statement snapshot")
                exit_snap = self._capture_pgss_snapshot()
                self._absorb_pgss_delta(
                    enter_snap,
                    exit_snap,
                    allow_pgss_reset=reset_allowed,
                )
                exit_log_offsets = self._pg_log_snapshot()
                if self._pg_log_hidden_enter_offsets is None:
                    raise RuntimeError("PostgreSQL metrics_hidden exit has no enter log snapshot")
                missing = tuple(sorted(
                    set(self._pg_log_hidden_enter_offsets) - set(exit_log_offsets)
                ))
                if missing:
                    raise RuntimeError(
                        "PostgreSQL log file disappeared during metrics_hidden: "
                        f"missing_files={missing!r}, enter_offsets={self._pg_log_hidden_enter_offsets!r}, "
                        f"exit_offsets={exit_log_offsets!r}"
                    )
                shrinking = {
                    path: (self._pg_log_hidden_enter_offsets[path], exit_log_offsets[path])
                    for path in self._pg_log_hidden_enter_offsets
                    if exit_log_offsets[path] < self._pg_log_hidden_enter_offsets[path]
                }
                if shrinking:
                    raise RuntimeError(
                        "PostgreSQL log file shrank during metrics_hidden: "
                        f"files={shrinking!r}"
                    )
                self._pg_log_visible_offsets = exit_log_offsets
                self._pg_log_hidden_enter_offsets = None

    def _absorb_pgss_delta(
        self,
        enter_snap: PgStatementSnapshot,
        exit_snap: PgStatementSnapshot,
        *,
        allow_pgss_reset: bool = False,
    ):
        """将 (exit - enter) 增量累加进 _pgss_baseline。

        - 块内首次出现的 queryid（enter 没有）：完整吸收 → topsql/slow_queries 看不到
        - 跨边界 queryid：只吸收块内部分，块外执行仍然可见（calls_delta 仍 > 0）
        """
        if enter_snap.timestamp_ms >= exit_snap.timestamp_ms:
            raise RuntimeError(
                f"PostgreSQL hidden snapshots are not increasing: enter_timestamp_ms={enter_snap.timestamp_ms}, "
                f"exit_timestamp_ms={exit_snap.timestamp_ms}"
            )
        if self._pgss_baseline is None:
            raise RuntimeError("PostgreSQL metrics_hidden requires an initialized pg_stat_statements baseline")
        zero = PgStatementCounters(
            query="",
            calls=0,
            total_exec_time_ms=0.0,
            rows=0,
            shared_blks_hit=0,
            shared_blks_read=0,
            shared_blks_written=0,
            temp_blks_read=0,
            temp_blks_written=0,
        )
        missing_keys = sorted(
            key
            for key, counter in enter_snap.counters.items()
            if key not in exit_snap.counters
            and any(getattr(counter, field) != 0 for field in ADDITIVE_COUNTER_FIELDS)
        )
        if missing_keys:
            if not allow_pgss_reset:
                raise RuntimeError(
                    "PostgreSQL pg_stat_statements key disappeared during metrics_hidden: "
                    f"enter_timestamp_ms={enter_snap.timestamp_ms}, exit_timestamp_ms={exit_snap.timestamp_ms}, "
                    f"keys={missing_keys!r}"
                )
            self._pgss_baseline = PgStatementSnapshot(
                timestamp_ms=exit_snap.timestamp_ms,
                counters=exit_snap.counters,
            )
            print(
                "[Env:PGEnv] metrics_hidden observed an explicit PostgreSQL stats reset/restart; "
                f"new baseline entries={len(exit_snap.counters)}."
            )
            self._pgss_sampler_reset_observed = True
            return
        counters = dict(self._pgss_baseline.counters)
        absorbed = 0
        for key, current in exit_snap.counters.items():
            previous = enter_snap.counters.get(key, zero)
            base = self._pgss_baseline.counters.get(key, zero)
            values: dict[str, int | float] = {}
            decreasing = {}
            for field in ADDITIVE_COUNTER_FIELDS:
                delta = getattr(current, field) - getattr(previous, field)
                if delta < 0:
                    decreasing[field] = delta
                values[field] = getattr(base, field) + delta
            if decreasing:
                raise RuntimeError(
                    "PostgreSQL pg_stat_statements counter moved backwards during metrics_hidden: "
                    f"query_key={key!r}, enter_timestamp_ms={enter_snap.timestamp_ms}, "
                    f"exit_timestamp_ms={exit_snap.timestamp_ms}, fields={decreasing!r}"
                )
            counters[key] = PgStatementCounters(
                query=current.query or base.query,
                calls=int(values["calls"]),
                total_exec_time_ms=float(values["total_exec_time_ms"]),
                rows=int(values["rows"]),
                shared_blks_hit=int(values["shared_blks_hit"]),
                shared_blks_read=int(values["shared_blks_read"]),
                shared_blks_written=int(values["shared_blks_written"]),
                temp_blks_read=int(values["temp_blks_read"]),
                temp_blks_written=int(values["temp_blks_written"]),
            )
            if values["calls"] - getattr(previous, "calls") > 0:
                absorbed += 1
        self._pgss_baseline = PgStatementSnapshot(
            timestamp_ms=exit_snap.timestamp_ms,
            counters=counters,
        )
        print(f"[Env:PGEnv] metrics_hidden absorbed pgss delta on {absorbed} queryid(s).")

    def teardown(self):
        """销毁 PG 环境（保留数据）"""
        failures = []
        if self._history_sql_archive is not None:
            archive = self._history_sql_archive
            self._history_sql_archive = None
            try:
                archive.close()
            except Exception as exc:
                failures.append(("close history SQL archive", exc))
        for operation, callback in (
            ("stop sampler", self._stop_sampler),
            ("stop workload runner", self._stop_workload_runner),
            ("clear PgBouncer endpoint", self.clear_pgbouncer_endpoint),
        ):
            try:
                callback()
            except Exception as exc:
                failures.append((operation, exc))
        if self.deployment is not None:
            try:
                self.deployment.teardown()
            except Exception as exc:
                failures.append(("teardown deployment", exc))
        self._conn = None
        self._scenario_metric_provider = None
        if failures:
            details = "; ".join(f"{operation}: {exc!r}" for operation, exc in failures)
            raise RuntimeError(f"PostgreSQL environment teardown failed: {details}") from failures[0][1]

    def attach_scenario_metric_provider(self, provider) -> None:
        if self._scenario_metric_provider is not None and self._scenario_metric_provider is not provider:
            raise RuntimeError("a scenario metric provider is already attached")
        self._scenario_metric_provider = provider

    def detach_scenario_metric_provider(self, provider=None) -> None:
        if provider is None or self._scenario_metric_provider is provider:
            self._scenario_metric_provider = None

    def attach_workload_runner(self, runner):
        """Attach a WorkloadRunner instance. Caller is responsible for start()/stop()."""
        # 仅持有引用；连接与线程由 runner 自管，teardown 时统一停止。
        self._workload_runner = runner

    def _query_workload_activity(self, limit: int = 20) -> str:
        """返回 workload runner 内部聚合的 fingerprint 实时 mean_ms / p95_ms。

        进程内 ring buffer 聚合，500 条记录的 sort+group ≈ 0.1ms；不走 DB。
        """
        runner = getattr(self, "_workload_runner", None)
        if runner is None:
            return json.dumps({
                "status": "error",
                "error": "workload runner not attached",
            }, ensure_ascii=False)
        activity = runner.get_activity(limit=limit)
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

    def _stop_workload_runner(self):
        runner = getattr(self, "_workload_runner", None)
        if runner is None:
            return
        try:
            runner.stop()
        except Exception:
            pass
        self._workload_runner = None

    def _ensure_connection(self):
        """确保数据库连接可用"""
        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute("SELECT 1")
                return True
            except Exception:
                self._conn = None
        import psycopg2
        for attempt in range(10):
            try:
                self._conn = psycopg2.connect(
                    host=self.host, port=self.port,
                    user=self.user, password=self.password, dbname=self.dbname,
                    connect_timeout=3
                )
                self._conn.autocommit = True
                with self._conn.cursor() as _timeout_cursor:
                    _timeout_cursor.execute(
                        f"SET statement_timeout = {self.SQL_STATEMENT_TIMEOUT_SECONDS * 1000}"
                    )
                print(f"[Env:PGEnv] Connected to PostgreSQL.")
                return True
            except Exception as e:
                if attempt == 0:
                    print(f"[Env:PGEnv] Connection attempt {attempt+1} failed: {e}")
                time.sleep(1)
        print("[Env:PGEnv] Failed to connect after 10 attempts.")
        return False

    def reconnect(self):
        """强制重新建立数据库连接"""
        previous = self._conn
        self._conn = None
        if previous is not None:
            previous.close()
        return self._ensure_connection()

    def open_workload_connection(self, application_name: str, target: Optional[str] = None):
        import psycopg2
        endpoint = None
        if target is not None:
            endpoint = self._workload_connection_endpoints.get(str(target))
            if endpoint is None:
                raise ValueError(
                    "PostgreSQL workload pool is not configured: "
                    f"target={target!r}, pools={sorted(self._workload_connection_endpoints)}"
                )
        conn = psycopg2.connect(
            host=str(endpoint["host"]) if endpoint else self.host,
            port=int(endpoint["port"]) if endpoint else self.port,
            user=str(endpoint["user"]) if endpoint else self.user,
            password=str(endpoint["password"]) if endpoint else self.password,
            dbname=str(endpoint["dbname"]) if endpoint else self.dbname,
            connect_timeout=3,
            application_name=application_name,
        )
        conn.autocommit = False
        return conn

    def configure_pgbouncer_endpoint(
        self,
        host: str,
        port: int,
        *,
        admin_user: str = "postgres",
        admin_password: str = "password",
        admin_dbname: str = "pgbouncer",
    ) -> None:
        """Register a scenario-owned PgBouncer admin endpoint.

        The endpoint is opt-in so ordinary PostgreSQL cases retain their existing
        tool surface and workload routing semantics.
        """
        if int(port) <= 0:
            raise ValueError(f"PgBouncer port must be positive: port={port!r}")
        self._pgbouncer_endpoint = {
            "host": str(host),
            "port": int(port),
            "user": str(admin_user),
            "password": str(admin_password),
            "dbname": str(admin_dbname),
        }
        self._pgbouncer_runtime_overrides.clear()

    def clear_pgbouncer_endpoint(self) -> None:
        self._pgbouncer_endpoint = None
        self._pgbouncer_runtime_overrides.clear()
        self._workload_connection_endpoints.clear()

    def configure_workload_connection_pool(
        self,
        pool: str,
        host: str,
        port: int,
        *,
        user: str,
        password: str,
        dbname: str,
    ) -> None:
        pool_name = str(pool).strip()
        if not pool_name:
            raise ValueError("PgBouncer workload pool name must not be empty")
        if int(port) <= 0:
            raise ValueError(f"PgBouncer workload port must be positive: port={port!r}")
        self._workload_connection_endpoints[pool_name] = {
            "host": str(host),
            "port": int(port),
            "user": str(user),
            "password": str(password),
            "dbname": str(dbname),
        }

    def _pgbouncer_admin_query(self, sql: str) -> tuple[list[str], list[list[object]]]:
        if self._pgbouncer_endpoint is None:
            raise RuntimeError("PgBouncer admin endpoint is not configured for this environment")
        import psycopg2

        endpoint = self._pgbouncer_endpoint
        conn = psycopg2.connect(
            host=str(endpoint["host"]),
            port=int(endpoint["port"]),
            user=str(endpoint["user"]),
            password=str(endpoint["password"]),
            dbname=str(endpoint["dbname"]),
            connect_timeout=3,
        )
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                columns = [column.name for column in cur.description] if cur.description else []
                rows = [list(row) for row in cur.fetchall()] if cur.description else []
            return columns, rows
        finally:
            conn.close()

    def pgbouncer_admin_query(self, sql: str) -> str:
        try:
            columns, rows = self._pgbouncer_admin_query(sql)
            return json.dumps(
                {"status": "success", "columns": columns, "result": rows},
                default=str,
                ensure_ascii=False,
            )
        except Exception as exc:
            return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)

    def configure_workload_session(self, connection, profile):
        from src.workloads.specs import WORKLOAD_LOCK_TIMEOUT, WORKLOAD_STATEMENT_TIMEOUT
        with connection.cursor() as cur:
            if profile.application_name:
                cur.execute(
                    "SELECT set_config('application_name', %s, false);",
                    (profile.application_name,),
                )
            cur.execute(f"SET LOCAL statement_timeout = '{WORKLOAD_STATEMENT_TIMEOUT}';")
            cur.execute(f"SET LOCAL lock_timeout = '{WORKLOAD_LOCK_TIMEOUT}';")

    def execute_workload_profile(self, connection, profile):
        with connection.cursor() as cur:
            cur.execute(profile.sql)
            result_rows = len(cur.fetchall()) if cur.description else cur.rowcount
        connection.commit() if profile.commit else connection.rollback()
        return {"session_setup_statements": 0, "result_rows": result_rows}

    def _start_sampler(self):
        """Start the background sampler on the fixed UTC epoch-ms grid."""
        if getattr(self, "disable_generic_sampler", False):
            return
        if self._sampler_thread is not None and self._sampler_thread.is_alive():
            return
        self._raise_sampler_failure()
        self._sampler_stop.clear()
        self._sampler_grid_strikes = SamplerGridStrikes()
        self._sampler_thread = threading.Thread(
            target=self._run_resource_sampler, daemon=True)
        self._sampler_thread.start()

    def _stop_sampler(self):
        """Stop the sampler and surface any failure raised by its thread."""
        self._sampler_stop.set()
        if self._sampler_thread is not None:
            self._sampler_thread.join(timeout=10)
            if self._sampler_thread.is_alive():
                raise RuntimeError("PostgreSQL sampler thread did not stop within 10 seconds")
            self._sampler_thread = None
        if self._sampler_conn is not None:
            self._sampler_conn.close()
            self._sampler_conn = None
        self._raise_sampler_failure()

    def _reset_cgroup_io_sampler_state(self) -> None:
        """Reset host-side cgroup state after the Docker container is recreated."""
        self._prev_io_sample = None
        self._host_cgroup_base = None

    def _run_lifecycle_with_sampler(self, action: str, perform) -> str:
        """Run a PG process lifecycle action with the background sampler kept consistent.

        The instance downtime the action causes is marked as an expected sampler
        disconnect (so a sampler failure already recorded from that downtime is
        accepted once instead of failing the rest of the run), sampling is paused
        for the duration like in the reboot path, and ``finally`` resumes sampling
        so the run cannot stay dead after the instance recovers.
        """
        sampler_was_running = self._sampler_thread is not None and self._sampler_thread.is_alive()
        self._expected_sampler_disconnect_reason = f"manage_instance('{action}')"
        self._expected_sampler_disconnect_evidence = {
            "action": action,
            "sampler_was_running": str(sampler_was_running),
        }
        try:
            if sampler_was_running:
                self._stop_sampler()
            return perform()
        finally:
            if self._scenario_metric_provider is None:
                self._start_sampler()
            self._expected_sampler_disconnect_reason = None
            self._expected_sampler_disconnect_evidence = None

    def _drop_sampler_tick(self, exc: Exception, timestamp_ms: int) -> None:
        """Discard a sampler tick whose PostgreSQL connection died mid-query.

        Only used when the scenario opted into sampler reconnect tolerance
        (``allow_sampler_reconnect``); the dead connection is closed so the
        next tick reconnects from scratch.
        """
        print(f"[Env:PGEnv] Sampler tick dropped after PostgreSQL connection loss: "
              f"timestamp_ms={timestamp_ms}, error={exc}")
        if self._sampler_conn is not None:
            try:
                self._sampler_conn.close()
            except Exception:
                pass
            self._sampler_conn = None
        self._sampler_reconnected = True

    def _accept_expected_sampler_failure(self) -> bool:
        """Swallow the one pending sampler failure when a lifecycle action
        declared its instance downtime as an expected disconnect."""
        if self._sampler_failure is None:
            return False
        reason = self._expected_sampler_disconnect_reason
        if reason is None:
            return False
        print(
            "[Env:PGEnv] Sampler failure accepted as expected disconnect: "
            f"reason={reason!r}, evidence={self._expected_sampler_disconnect_evidence!r}, "
            f"error={self._sampler_failure}"
        )
        self._expected_sampler_disconnect_reason = None
        self._expected_sampler_disconnect_evidence = None
        self._sampler_failure = None
        return True

    def _raise_sampler_failure(self) -> None:
        if self._accept_expected_sampler_failure():
            return
        failure = self._sampler_failure
        if failure is not None:
            raise RuntimeError(f"PostgreSQL sampler thread failed: error={failure}") from failure

    @property
    def _sampler_lag_strikes(self) -> int:
        return self._sampler_grid_strikes.strikes

    def _sampler_record_tick_lag(self, tick_elapsed_seconds: float) -> None:
        """Count sustained over-tolerance ticks; in-tolerance ticks decay the count.

        A single slow tick (host stall, crash-recovery reconnect inside the tick)
        must not kill the sampler: it raises the strike count by one while any
        tick finishing within SAMPLER_LAG_TOLERANCE_INTERVALS grid intervals
        decays the count back toward zero. Only SAMPLER_LAG_STRIKES_LIMIT net
        strikes mean the fixed-grid contract is unmet and the sampler gives up.
        """
        if tick_elapsed_seconds <= self.sample_interval_sec * SAMPLER_LAG_TOLERANCE_INTERVALS:
            self._sampler_grid_strikes.decay()
            return
        self._sampler_grid_strikes.strike(
            detail=(
                f"tick_elapsed_seconds={tick_elapsed_seconds:.3f}, "
                f"tolerance_seconds={self.sample_interval_sec * SAMPLER_LAG_TOLERANCE_INTERVALS}"
            )
        )

    def _run_resource_sampler(self) -> None:
        try:
            self._resource_sampler_loop()
        except Exception as exc:
            self._sampler_failure = exc
            self._sampler_stop.set()
            with self._sampler_condition:
                self._sampler_condition.notify_all()

    def _sampler_ensure_conn(self):
        """为后台采集线程维护独立 DB 连接。"""
        if self._sampler_conn is not None:
            try:
                with self._sampler_conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                return self._sampler_conn
            except Exception:
                if not self.allow_sampler_reconnect:
                    raise
                try:
                    self._sampler_conn.close()
                except Exception:
                    pass
                self._sampler_conn = None
                self._sampler_reconnected = True
        import psycopg2
        last_error = None
        reconnect_rounds = self.SAMPLER_RECONNECT_MAX_ROUNDS if self.allow_sampler_reconnect else 1
        for round_index in range(1, reconnect_rounds + 1):
            reconnect_deadline = (
                time.monotonic() + self.SAMPLER_RECONNECT_TIMEOUT_SEC
                if self.allow_sampler_reconnect
                else None
            )
            while True:
                if self._sampler_stop.is_set():
                    return self._sampler_conn
                try:
                    self._sampler_conn = psycopg2.connect(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        dbname=self.dbname,
                        connect_timeout=3,
                        application_name="aiopsbench-history-sampler",
                    )
                    self._sampler_conn.autocommit = True
                    return self._sampler_conn
                except Exception as exc:
                    last_error = exc
                    if not self.allow_sampler_reconnect:
                        raise
                    remaining = reconnect_deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    if self._sampler_stop.wait(min(0.5, remaining)):
                        return self._sampler_conn
            print(
                f"[Env:PGEnv] Sampler reconnect window {round_index}/{reconnect_rounds} exhausted, "
                f"opening another window: timeout_sec={self.SAMPLER_RECONNECT_TIMEOUT_SEC}, "
                f"error={last_error}"
            )
        raise RuntimeError(
            "PostgreSQL sampler could not reconnect within the allowed restart windows: "
            f"rounds={reconnect_rounds}, timeout_sec_per_round={self.SAMPLER_RECONNECT_TIMEOUT_SEC}, "
            f"error={last_error}"
        ) from last_error

    def _resource_sampler_loop(self):
        """Collect all PG metrics on one fixed UTC epoch-ms grid."""
        import psycopg2

        previous_cpu_us = None
        previous_cpu_timestamp = None
        previous_hits = None
        previous_reads = None
        previous_snapshot = None
        interval_ms = self.sample_interval_sec * 1000
        next_timestamp_ms = (int(time.time() * 1000) // interval_ms + 1) * interval_ms

        while not self._sampler_stop.is_set():
            wait_seconds = next_timestamp_ms / 1000 - time.time()
            if wait_seconds > 0 and self._sampler_stop.wait(wait_seconds):
                return
            if self._sampler_stop.is_set():
                return
            timestamp_ms = next_timestamp_ms
            tick_started_mono = time.monotonic()
            values: dict[str, dict[str, float]] = {}

            cpu_us = self._read_cpu_usage_usec()
            if previous_cpu_us is not None:
                if cpu_us < previous_cpu_us:
                    raise RuntimeError(
                        f"PostgreSQL cgroup CPU counter moved backwards: previous={previous_cpu_us}, current={cpu_us}, "
                        f"timestamp_ms={timestamp_ms}"
                    )
                elapsed_us = (timestamp_ms - previous_cpu_timestamp) * 1000
                cpus = self._effective_cpus()
                if elapsed_us <= 0 or cpus <= 0:
                    raise RuntimeError(
                        f"PostgreSQL CPU sampler interval is invalid: previous_timestamp_ms={previous_cpu_timestamp}, "
                        f"timestamp_ms={timestamp_ms}, cpus={cpus}"
                    )
                values["cpu"] = {
                    "percent": _bounded_cpu_percent(cpu_us - previous_cpu_us, elapsed_us, cpus)
                }
            previous_cpu_us = cpu_us
            previous_cpu_timestamp = timestamp_ms

            values["memory"] = {"percent": self._sample_memory()}
            io = self._sample_disk_io()
            if io is not None:
                values["disk_io"] = {
                    "read_mb_per_second": io[0],
                    "write_mb_per_second": io[1],
                }

            sampler_conn = self._sampler_ensure_conn()
            if sampler_conn is None:
                return
            if self._sampler_reconnected:
                # A PostgreSQL restart can reset SQL statistics counters while
                # the container cgroup counters remain continuous.
                previous_hits = None
                previous_reads = None
                previous_snapshot = None
                self._sampler_reconnected = False
            try:
                with sampler_conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT count(*) FROM pg_stat_activity WHERE backend_type = 'client backend'"
                    )
                    values["active_connections"] = {"connections": float(cursor.fetchone()[0] or 0)}
                    cursor.execute(
                        "SELECT sum(blks_hit), sum(blks_read) FROM pg_stat_database "
                        "WHERE datname = current_database()"
                    )
                    hits, reads = (int(value or 0) for value in cursor.fetchone())
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as exc:
                if not self.allow_sampler_reconnect:
                    raise
                # A fault lifecycle may restart PostgreSQL mid-tick. Drop the
                # tick, refresh the connection and delta baselines at the next
                # tick, and keep the sampler alive for the rest of the run.
                self._drop_sampler_tick(exc, timestamp_ms)
                previous_hits = None
                previous_reads = None
                previous_snapshot = None
                next_timestamp_ms += interval_ms
                continue
            if previous_hits is not None:
                delta_hits = hits - previous_hits
                delta_reads = reads - previous_reads
                if delta_hits < 0 or delta_reads < 0:
                    raise RuntimeError(
                        f"PostgreSQL pg_stat_database counters moved backwards: previous=({previous_hits},{previous_reads}), "
                        f"current=({hits},{reads}), timestamp_ms={timestamp_ms}"
                    )
                if delta_hits + delta_reads > 0:
                    values["cache_hit_ratio"] = {
                        "percent": round(delta_hits * 100.0 / (delta_hits + delta_reads), 2)
                    }
            previous_hits = hits
            previous_reads = reads

            try:
                snapshot = capture_statement_snapshot(sampler_conn, timestamp_ms)
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as exc:
                if not self.allow_sampler_reconnect:
                    raise
                self._drop_sampler_tick(exc, timestamp_ms)
                previous_hits = None
                previous_reads = None
                previous_snapshot = None
                next_timestamp_ms += interval_ms
                continue
            calls = sum(
                counter.calls
                for key, counter in snapshot.counters.items()
                if key.queryid not in self._pg_statement_excluded_queryids
            )
            if previous_snapshot is not None:
                previous_calls = sum(
                    counter.calls
                    for key, counter in previous_snapshot.counters.items()
                    if key.queryid not in self._pg_statement_excluded_queryids
                )
                if calls < previous_calls:
                    # pg_stat_statements is reset by several legitimate fault
                    # lifecycles (and may reset on a PostgreSQL restart). The
                    # sampler starts a fresh delta window at the reset tick.
                    self._pgss_sampler_reset_observed = False
                else:
                    elapsed_seconds = (snapshot.timestamp_ms - previous_snapshot.timestamp_ms) / 1000
                    if elapsed_seconds <= 0:
                        raise RuntimeError(
                            f"PostgreSQL statement snapshot interval is invalid: previous={previous_snapshot.timestamp_ms}, "
                            f"current={snapshot.timestamp_ms}"
                        )
                    values["qps"] = {"queries_per_second": round((calls - previous_calls) / elapsed_seconds, 3)}
            previous_snapshot = snapshot

            try:
                values.update(self._sample_additional_metrics(sampler_conn, timestamp_ms, values))
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as exc:
                if not self.allow_sampler_reconnect:
                    raise
                self._drop_sampler_tick(exc, timestamp_ms)
                previous_hits = None
                previous_reads = None
                previous_snapshot = None
                next_timestamp_ms += interval_ms
                continue

            with self._metric_service.live.lock:
                self._metric_service.live.append_sample(timestamp_ms, values)
                self._pg_statement_snapshots.append(snapshot)
            with self._sampler_condition:
                self._sampler_last_timestamp_ms = timestamp_ms
                self._sampler_condition.notify_all()
            next_timestamp_ms += interval_ms
            tick_elapsed_seconds = time.monotonic() - tick_started_mono
            if (
                tick_elapsed_seconds > self.sample_interval_sec * SAMPLER_LAG_TOLERANCE_INTERVALS
                and self.allow_sampler_jitter
            ):
                # Some scenario workloads deliberately make one generic
                # catalog sample slower than its nominal period. Preserve
                # the aligned metric contract, skip only the missed grid
                # points, and resume at the next future tick. Scenario-
                # owned observers remain responsible for causal evidence.
                next_timestamp_ms = (
                    int(time.time() * 1000) // interval_ms + 1
                ) * interval_ms
                continue
            self._sampler_record_tick_lag(tick_elapsed_seconds)

    def _read_cpu_usage_usec(self) -> int:
        """读取容器 cgroup CPU 累计使用微秒数。"""
        if self._detect_cgroup_version():
            stat = self._cgroup_read("/sys/fs/cgroup/cpu.stat")
            for line in stat.splitlines():
                if line.startswith("usage_usec"):
                    return int(line.split()[1])
            raise RuntimeError(f"PostgreSQL cgroup cpu.stat lacks usage_usec: stat={stat!r}")
        raw = self._cgroup_read("/sys/fs/cgroup/cpuacct/cpuacct.usage")
        return int(raw.strip()) // 1000

    def _effective_cpus(self) -> float:
        """读取容器 CPU 配额（核数）。"""
        if self._detect_cgroup_version():
            cpu_max = self._cgroup_read("/sys/fs/cgroup/cpu.max")
            parts = cpu_max.split()
            if len(parts) != 2 or parts[0] == "max":
                raise RuntimeError(f"PostgreSQL cgroup cpu.max does not define a finite quota: value={cpu_max!r}")
            quota, period = int(parts[0]), int(parts[1])
            if quota <= 0 or period <= 0:
                raise RuntimeError(f"PostgreSQL cgroup cpu.max quota is invalid: value={cpu_max!r}")
            return quota / period
        else:
            quota = self._cgroup_read("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
            period = self._cgroup_read("/sys/fs/cgroup/cpu/cpu.cfs_period_us")
            quota_value, period_value = int(quota.strip()), int(period.strip())
            if quota_value <= 0 or period_value <= 0:
                raise RuntimeError(f"PostgreSQL cgroup CPU quota is invalid: quota={quota!r}, period={period!r}")
            return quota_value / period_value

    def _container_top_cpu_processes(self) -> dict:
        """Return a generic top-process CPU snapshot from inside the PG container."""
        import subprocess

        deployment = getattr(self, "deployment", None)
        container_name = getattr(deployment, "container_name", None)
        if not container_name:
            return {"top_processes": [], "external_cpu_percent": 0.0}
        try:
            result = subprocess.run(
                [
                    "docker", "exec", container_name,
                    "bash", "-lc",
                    "ps -eo pid=,ppid=,comm=,pcpu=,args= --sort=-pcpu",
                ],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode != 0:
                return {"top_processes": [], "external_cpu_percent": 0.0}
            rows = []
            postgres_cpu = 0.0
            external_cpu = 0.0
            for line in result.stdout.splitlines():
                parts = line.strip().split(None, 4)
                if len(parts) < 5:
                    continue
                pid_raw, ppid_raw, comm, pcpu_raw, args = parts
                if "ps -eo" in args or "head -n" in args:
                    # Skip the snapshot's own observation shell.
                    continue
                try:
                    pid = int(pid_raw)
                    ppid = int(ppid_raw)
                    pcpu = float(pcpu_raw)
                except ValueError:
                    continue
                lowered = f"{comm} {args}".lower()
                is_db = any(term in lowered for term in ("postgres", "postmaster", "pg_ctl"))
                rows.append({
                    "pid": pid,
                    "ppid": ppid,
                    "comm": comm,
                    "args": args[:120],
                    "cpu_percent": pcpu,
                    "process_type": "database" if is_db else "external",
                })
                if is_db:
                    postgres_cpu += pcpu
                else:
                    external_cpu += pcpu
            return {
                "top_processes": rows,
                "postgres_cpu_percent": round(postgres_cpu, 1),
                "external_cpu_percent": round(external_cpu, 1),
            }
        except Exception:
            return {"top_processes": [], "external_cpu_percent": 0.0}

    def _sample_memory(self) -> float:
        """采样内存使用率（去 page cache 后的真实压力百分比）。"""
        cur, mx, stat, inactive_key = self._memory_cgroup_snapshot()
        used = int(cur.strip())
        limit = self._parse_cgroup_memory_limit(mx)
        if limit is None:
            raise RuntimeError(f"PostgreSQL cgroup memory limit is unavailable: raw_limit={mx!r}")
        inactive_file = None
        for line in stat.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] == inactive_key:
                inactive_file = int(parts[1])
                break
        if inactive_file is None:
            raise RuntimeError(f"PostgreSQL cgroup memory.stat lacks {inactive_key}: stat={stat!r}")
        if used < inactive_file:
            raise RuntimeError(
                f"PostgreSQL cgroup memory counters are inconsistent: used_bytes={used}, "
                f"inactive_file_bytes={inactive_file}"
            )
        real_used = used - inactive_file
        return round(real_used / limit * 100.0, 1)

    def _memory_cgroup_snapshot(self):
        if self._detect_cgroup_version():
            return (
                self._cgroup_read("/sys/fs/cgroup/memory.current"),
                self._cgroup_read("/sys/fs/cgroup/memory.max"),
                self._cgroup_read("/sys/fs/cgroup/memory.stat"),
                "inactive_file",
            )
        return (
            self._cgroup_read("/sys/fs/cgroup/memory/memory.usage_in_bytes"),
            self._cgroup_read("/sys/fs/cgroup/memory/memory.limit_in_bytes"),
            self._cgroup_read("/sys/fs/cgroup/memory/memory.stat"),
            "total_inactive_file",
        )

    def _parse_cgroup_memory_limit(self, raw: Optional[str]) -> Optional[int]:
        if raw is None:
            return None
        value = raw.strip()
        if not value or value == "max":
            return None
        limit = int(value)
        if limit > (1 << 62):
            return None
        return limit

    def _memory_limit_context(self) -> dict:
        try:
            _, mx, _, _ = self._memory_cgroup_snapshot()
            limit = self._parse_cgroup_memory_limit(mx)
            if limit is None:
                return {"memory_limit_mb": None, "memory_limit_bytes": None}
            return {
                "memory_limit_mb": round(limit / 1024 / 1024, 2),
                "memory_limit_bytes": limit,
            }
        except Exception:
            return {"memory_limit_mb": None, "memory_limit_bytes": None}

    def _sample_disk_io(self) -> Optional[tuple[float, float]]:
        """采样容器 cgroup 累计读/写字节并计算本 tick 吞吐。"""
        total_r = total_w = 0
        if self._detect_cgroup_version():
            stat = self._cgroup_read("/sys/fs/cgroup/io.stat")
            for line in stat.splitlines():
                for token in line.split():
                    if token.startswith("rbytes="):
                        total_r += int(token.split("=", 1)[1])
                    elif token.startswith("wbytes="):
                        total_w += int(token.split("=", 1)[1])
        else:
            stat = self._cgroup_read("/sys/fs/cgroup/blkio/blkio.io_service_bytes_recursive")
            for line in stat.splitlines():
                parts = line.split()
                if len(parts) == 3 and parts[1] == "Read":
                    total_r += int(parts[2])
                elif len(parts) == 3 and parts[1] == "Write":
                    total_w += int(parts[2])
        now_mono = time.monotonic()
        previous = getattr(self, "_prev_io_sample", None)
        self._prev_io_sample = (now_mono, total_r, total_w)
        if previous is None:
            return None
        if total_r < previous[1] or total_w < previous[2]:
            raise RuntimeError(
                f"PostgreSQL cgroup I/O counters moved backwards: previous=({previous[1]},{previous[2]}), "
                f"current=({total_r},{total_w})"
            )
        elapsed_seconds = now_mono - previous[0]
        if elapsed_seconds <= 0:
            raise RuntimeError(f"PostgreSQL cgroup I/O sampler interval is invalid: elapsed_seconds={elapsed_seconds}")
        return (
            round((total_r - previous[1]) / (1024 ** 2) / elapsed_seconds, 3),
            round((total_w - previous[2]) / (1024 ** 2) / elapsed_seconds, 3),
        )

    def _cgroup_read(self, path: str) -> str:
        """Read a container cgroup file without routing every sample through Docker CLI."""
        import subprocess

        if self._host_cgroup_base is None:
            inspect = subprocess.run(
                ["docker", "inspect", "--format", "{{.Id}} {{.State.Pid}}", self.deployment.container_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            fields = inspect.stdout.split()
            if inspect.returncode == 0 and len(fields) == 2 and fields[1].isdigit():
                container_id, pid = fields
                try:
                    with open(os.path.join(HOST_PROC_ROOT, pid, "cgroup"), encoding="utf-8") as cgroup_file:
                        cgroup_lines = cgroup_file.read().splitlines()
                    unified = next(
                        (line.split(":", 2)[2] for line in cgroup_lines if line.startswith("0::")),
                        None,
                    )
                    # With Docker Desktop or a rootless daemon the PID belongs to another PID namespace,
                    # and a host process may carry the same number. Only a cgroup path that names the
                    # container (cgroupfs and systemd drivers both put its id there) is the container's.
                    if unified and container_id in unified:
                        candidate = os.path.join(HOST_CGROUP_ROOT, unified.lstrip("/"))
                        if os.path.isdir(candidate):
                            self._host_cgroup_base = candidate
                except (OSError, IndexError):
                    pass

        if self._host_cgroup_base is not None:
            relative_path = path.removeprefix("/sys/fs/cgroup/").lstrip("/")
            host_path = os.path.join(self._host_cgroup_base, relative_path)
            try:
                with open(host_path, encoding="utf-8") as cgroup_file:
                    return cgroup_file.read()
            except OSError:
                self._host_cgroup_base = None

        result = subprocess.run(
            ["docker", "exec", self.deployment.container_name, "cat", path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"PostgreSQL cgroup read failed: path={path!r}, returncode={result.returncode}, "
                f"stderr={result.stderr.strip()!r}"
            )
        return result.stdout


    def _detect_cgroup_version(self) -> bool:
        """探测容器 cgroup 版本，True 表示 v2。结果缓存。"""
        if getattr(self, "_cgroup_v2", None) is not None:
            return self._cgroup_v2
        try:
            self._cgroup_read("/sys/fs/cgroup/cgroup.controllers")
            self._cgroup_v2 = True
        except RuntimeError:
            self._cgroup_v2 = False
        return self._cgroup_v2

    def _connection_snapshot(self, cur) -> dict:
        cur.execute(
            "SELECT state, count(*) FROM pg_stat_activity "
            "WHERE backend_type = 'client backend' GROUP BY state;")
        states = {row[0] or "null": int(row[1]) for row in cur.fetchall()}
        cur.execute(
            "SELECT wait_event_type, count(*) FROM pg_stat_activity "
            "WHERE backend_type = 'client backend' AND wait_event_type IS NOT NULL "
            "GROUP BY wait_event_type;")
        wait_types = {row[0] or "null": int(row[1]) for row in cur.fetchall()}
        cur.execute("SHOW max_connections;")
        return {
            "max_connections": int(cur.fetchone()[0]),
            "states": states,
            "wait_types": wait_types,
            "lock_waiting_sessions": wait_types.get("Lock", 0),
        }

    def _get_pg_knowledge_base(self, knowledge_base_mode: str) -> PGKnowledgeBase:
        if knowledge_base_mode not in self._pg_knowledge_bases:
            self._pg_knowledge_bases[knowledge_base_mode] = PGKnowledgeBase(
                knowledge_base_mode=knowledge_base_mode,
            )
        return self._pg_knowledge_bases[knowledge_base_mode]

    def _query_pg_knowledge_base(self, query: str, top_k: int,
                                 max_chars_per_result: int,
                                 knowledge_base_mode: str,
                                 kb_type: Optional[str] = None) -> str:
        knowledge_base = self._get_pg_knowledge_base(knowledge_base_mode)
        try:
            top_k_int = int(top_k)
        except (TypeError, ValueError):
            top_k_int = 5
        try:
            max_chars_int = int(max_chars_per_result)
        except (TypeError, ValueError):
            max_chars_int = 1600
        result = knowledge_base.query(
            query=query,
            top_k=top_k_int,
            max_chars_per_result=max_chars_int,
            kb_type=kb_type,
        )
        return json.dumps(result, ensure_ascii=False, default=str)

    @Tool(
        alias="query_knowledge_base",
        description=lazy_agent_text(
            zh=(
                "检索本地PostgreSQL 16官方文档通用知识库。该工具不做类型过滤，"
                "适合查询系统视图含义、参数语义、SQL语法、诊断线索、修复动作、索引/锁/"
                "MVCC/autovacuum/WAL等官方文档内容。"
            ),
            en=(
                "Search the local general knowledge base of the official PostgreSQL 16 documentation. "
                "This tool applies no type filter and suits looking up official documentation on system view "
                "meanings, parameter semantics, SQL syntax, diagnostic clues, remediation actions, "
                "indexes/locks/MVCC/autovacuum/WAL and similar topics."
            ),
        ),
        arg_descriptions={
            "query": lazy_agent_text(
                zh="面向PostgreSQL文档的自然语言检索问题",
                en="Natural-language search question about the PostgreSQL documentation",
            ),
            "top_k": lazy_agent_text(
                zh="返回片段数量，默认5，最大20",
                en="Number of passages to return, default 5, maximum 20",
            ),
            "max_chars_per_result": lazy_agent_text(
                zh="每个片段最多返回字符数，默认1600",
                en="Maximum characters returned per passage, default 1600",
            ),
        },
    )
    def query_general_knowledge_base(self, query: str, top_k: int = 5,
                                     max_chars_per_result: int = 1600) -> str:
        return self._query_pg_knowledge_base(
            query=query,
            top_k=top_k,
            max_chars_per_result=max_chars_per_result,
            knowledge_base_mode="general",
            kb_type=None,
        )

    @Tool(
        alias="query_knowledge_base",
        description=lazy_agent_text(
            zh=(
                "检索本地PostgreSQL 16官方文档层级知识库。可用 kb_type 限定 "
                "configuration/guide/solution/fact；不同类型分别覆盖配置、原理、操作建议和事实信息。"
            ),
            en=(
                "Search the local hierarchical knowledge base of the official PostgreSQL 16 documentation. "
                "kb_type can restrict results to configuration/guide/solution/fact; the types cover "
                "configuration, principles, operational recommendations and factual information respectively."
            ),
        ),
        arg_descriptions={
            "query": lazy_agent_text(
                zh="面向PostgreSQL文档的自然语言检索问题",
                en="Natural-language search question about the PostgreSQL documentation",
            ),
            "top_k": lazy_agent_text(
                zh="返回片段数量，默认5，最大20",
                en="Number of passages to return, default 5, maximum 20",
            ),
            "max_chars_per_result": lazy_agent_text(
                zh="每个片段最多返回字符数，默认1600",
                en="Maximum characters returned per passage, default 1600",
            ),
            "kb_type": lazy_agent_text(
                zh="可选知识类型过滤: configuration, guide, solution, fact",
                en="Optional knowledge type filter: configuration, guide, solution, fact",
            ),
        },
    )
    def query_hierarchical_knowledge_base(self, query: str, top_k: int = 5,
                                          max_chars_per_result: int = 1600,
                                          kb_type: Optional[str] = None) -> str:
        return self._query_pg_knowledge_base(
            query=query,
            top_k=top_k,
            max_chars_per_result=max_chars_per_result,
            knowledge_base_mode="hierarchical",
            kb_type=kb_type,
        )

    @Tool(
        alias="query_metrics",
        tool_id="query_metrics",
        description=lambda: postgres_default_query_metrics_tool_definition()["tool_description"],
        arg_descriptions={
            "metric_type": lazy_agent_text(
                zh=(
                    "指标类型，可选 catalog 值: "
                    + ", ".join(sorted(POSTGRES_METRIC_CATALOG.metric_names))
                    + "; 当前 I/O 上下文 Case 还可用 filesystem_io、bufferio_waiters、host_pressure、"
                    "partition_lifecycle 四类原始场景观测；先用 help('query_metrics') 查看字段、单位、"
                    "baseline、采样窗口和最终恢复合同"
                ),
                en=(
                    "Metric type; allowed catalog values: "
                    + ", ".join(sorted(POSTGRES_METRIC_CATALOG.metric_names))
                    + "; the current Case may also offer four kinds of raw scenario observations: filesystem_io, "
                    "bufferio_waiters, host_pressure, partition_lifecycle; first use help('query_metrics') to see the "
                    "fields, units, baseline, sampling window and final recovery contract"
                ),
            ),
            "target": lazy_agent_text(
                zh="目标对象；cpu 传 top_process/top_processes 返回容器内 top CPU 进程快照，disk_usage 返回根文件系统观测，其他指标按场景定义",
                en=(
                    "Target object; for cpu, pass top_process/top_processes to get a snapshot of the top CPU processes "
                    "in the container; disk_usage returns root filesystem observations; other metrics are defined by the scenario"
                ),
            ),
            "limit": lazy_agent_text(
                zh="workload_activity 或场景 provider 使用，返回前 N 条记录，默认 20",
                en="Used by workload_activity or scenario providers; returns the first N records, default 20",
            ),
            "start_timestamp": lazy_agent_text(
                zh="时序指标开始时间，必须与 end_timestamp 同时提供，格式 YYYY-MM-DD HH:mm:ss",
                en="Start time of the time-series metric; must be provided together with end_timestamp, format YYYY-MM-DD HH:mm:ss",
            ),
            "end_timestamp": lazy_agent_text(
                zh="时序指标结束时间，必须与 start_timestamp 同时提供，格式 YYYY-MM-DD HH:mm:ss",
                en="End time of the time-series metric; must be provided together with start_timestamp, format YYYY-MM-DD HH:mm:ss",
            ),
        },
        definition=postgres_default_query_metrics_tool_definition,
    )
    def _query_metrics_for_agent(
        self,
        metric_type: str,
        target: str = None,
        limit: Optional[int] = None,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None,
        step_seconds: Optional[int] = None,
    ) -> str:
        metric = str(metric_type or "").strip().lower()
        case_catalog = getattr(self, "_metric_catalog", None)
        case_metrics = getattr(case_catalog, "metric_names", ())
        history_spec = getattr(getattr(self, "_case", None), "frozen_history", None)
        if history_spec is not None:
            case_metrics = set(history_spec.required_metrics)
        allowed_metrics = case_metrics if history_spec is not None else self.AGENT_METRICS | set(case_metrics)
        if metric not in allowed_metrics:
            return json.dumps({
                "status": "error",
                "metric": metric,
                "error": f"Unknown PG environment metric_type: {metric_type}",
            }, ensure_ascii=False)
        if metric == "disk_usage":
            return self._query_container_filesystem_usage_for_agent()
        return bound_metric_result(self.query_metrics(
            metric_type=metric_type,
            target=target,
            limit=limit,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            step_seconds=step_seconds,
        ))

    def _query_container_filesystem_usage_for_agent(self) -> str:
        """Return only container filesystem capacity, not database size detail."""
        import subprocess

        container = getattr(self.deployment, "container_name", None)
        if not container:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": "No deployment container configured",
            }, ensure_ascii=False)
        try:
            result = subprocess.run(
                [
                    "docker", "exec", container,
                    "df", "--output=used,avail,pcent", "-B1", "/",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception as exc:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": str(exc),
            }, ensure_ascii=False)
        if result.returncode != 0:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": result.stderr.strip() or f"df exit_code={result.returncode}",
            }, ensure_ascii=False)
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if len(lines) < 2:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": "Container df returned no filesystem row",
            }, ensure_ascii=False)
        fields = lines[-1].split()
        if len(fields) < 3:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": f"Unexpected container df output: {result.stdout.strip()}",
            }, ensure_ascii=False)
        try:
            used_bytes = int(fields[0])
            available_bytes = int(fields[1])
            usage_percent = float(fields[2].rstrip("%"))
        except ValueError as exc:
            return json.dumps({
                "status": "error",
                "metric": "disk_usage",
                "error": f"Invalid container df output: {exc}",
            }, ensure_ascii=False)
        return self._metric_success(
            "disk_usage",
            "snapshot",
            snapshot={
                "filesystem": "/",
                "used_mb": round(used_bytes / (1024 ** 2), 2),
                "available_mb": round(available_bytes / (1024 ** 2), 2),
                "usage_percent": usage_percent,
                "source": "container_df",
            },
        )

    def query_metrics(self, metric_type: str, target: str = None,
                      threshold_ms: Optional[int] = None,
                      tables: Optional[str] = None,
                      limit: Optional[int] = None,
                      start_timestamp: Optional[str] = None,
                      end_timestamp: Optional[str] = None,
                      step_seconds: Optional[int] = None) -> str:
        self._raise_sampler_failure()
        start_time, end_time = self._metric_time_range(
            start_timestamp, end_timestamp
        )
        metric_lower = metric_type.lower()
        if metric_lower == "cpu" and target in {"top_process", "top_processes"}:
            series = json.loads(self.query_metrics(
                metric_type=metric_type,
                target=None,
                threshold_ms=threshold_ms,
                tables=tables,
                limit=limit,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                step_seconds=step_seconds,
            ))
            if series.get("status") != "success":
                return json.dumps(series, ensure_ascii=False)
            series["current"] = self._container_top_cpu_processes()
            return json.dumps(series, ensure_ascii=False)
        provider = getattr(self, "_scenario_metric_provider", None)
        provider_query = getattr(provider, "query", None)
        if callable(provider_query) and metric_lower in {
            "filesystem_io",
            "bufferio_waiters",
            "host_pressure",
            "partition_lifecycle",
        }:
            return provider_query(metric_lower, target, start_time, end_time)
        if metric_lower in self._metric_catalog.metric_names:
            try:
                start_ms = parse_utc_timestamp(start_timestamp, "start_timestamp") if start_timestamp is not None else None
                end_ms = parse_utc_timestamp(end_timestamp, "end_timestamp") if end_timestamp is not None else None
                history_timeline = self._history_timeline
                if history_timeline is not None:
                    # Frozen-history observations must be served by the frozen
                    # timeline.  Querying the live service first returns the
                    # sampler's 2-second grid and only changes the envelope
                    # metadata afterwards, which can expand a wide overview
                    # into hundreds of thousands of prompt tokens.
                    frame = history_timeline.metric_provider.query(MetricQuery(
                        metric=metric_lower,
                        target=target,
                        start_epoch_ms=start_ms,
                        end_epoch_ms=end_ms,
                        step_seconds=step_seconds,
                    ))
                else:
                    frame = self._metric_service.query_public(MetricQuery(
                        metric=metric_lower,
                        target=target,
                        start_epoch_ms=start_ms,
                        end_epoch_ms=end_ms,
                        step_seconds=step_seconds,
                    ))
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
                    available_start_ms, available_end_ms = self._metric_service.live.available_range
                    requested_start_ms = start_ms if start_ms is not None else available_start_ms
                    requested_end_ms = end_ms if end_ms is not None else available_end_ms
                    requested_step = step_seconds or frame.step_seconds
                return render_metric_frame(
                    frame,
                    available_start_ms=available_start_ms,
                    available_end_ms=available_end_ms,
                    requested_start_ms=requested_start_ms,
                    requested_end_ms=requested_end_ms,
                    step_seconds=requested_step,
                    # `limit` is an overview budget. Explicit historical
                    # windows must retain their complete evidence series;
                    # their size is controlled by the window/step contract.
                    max_points=(
                        (limit if limit is not None else 20)
                        if start_timestamp is None and end_timestamp is None
                        else None
                    ),
                )
            except (ValueError, RuntimeError, TypeError, KeyError) as exc:
                return json.dumps({"status": "error", "metric": metric_lower, "error": str(exc)}, ensure_ascii=False)
        if not self._ensure_connection():
            return json.dumps({"status": "error", "error": "No database connection."}, ensure_ascii=False)
        # workload_activity 是进程内数据，不走 DB。
        if metric_type.lower() == "workload_activity":
            return self._query_workload_activity(limit=limit or 20)
        try:
            with self._conn.cursor() as cur:
                metric_lower = metric_type.lower()
                if metric_lower == "slow_queries":
                    threshold = int(threshold_ms) if threshold_ms is not None else 5000
                    if threshold <= 0:
                        raise ValueError(
                            f"slow_queries threshold_ms must be positive: threshold_ms={threshold_ms!r}"
                        )
                    threshold_sec = threshold / 1000.0
                    # 1) 当前仍在执行的长查询 + idle in transaction 长事务
                    cur.execute(
                        """
                        SELECT pid, usename AS username, datname AS database_name,
                               state, wait_event_type, wait_event, query,
                               extract(epoch from (NOW() - query_start)) as query_duration_sec,
                               extract(epoch from (NOW() - xact_start)) as xact_duration_sec
                        FROM pg_stat_activity
                        WHERE ((state = 'active' AND query_start < NOW() - make_interval(secs => %s))
                           OR (state = 'idle in transaction' AND xact_start < NOW() - INTERVAL '30 seconds'))
                          AND backend_type = 'client backend'
                          AND pid <> pg_backend_pid();
                        """,
                        (threshold_sec,))
                    columns = [desc[0] for desc in cur.description]
                    running = [dict(zip(columns, row)) for row in cur.fetchall()]
                    for r in running:
                        r["source"] = "running" if r.get("state") == "active" else "idle_in_transaction"
                    # 2) 已完成的慢 SQL（pg_stat_statements）
                    finished = []
                    cur.execute(
                        """
                        SELECT userid, dbid, queryid, query,
                               round(mean_exec_time::numeric, 2) AS mean_ms,
                               round(max_exec_time::numeric, 2) AS max_ms,
                               calls
                        FROM pg_stat_statements
                        WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
                          AND (mean_exec_time > %s OR max_exec_time > %s)
                        ORDER BY mean_exec_time DESC
                        LIMIT 10;
                        """,
                        (threshold, threshold))
                    baseline = self._pgss_baseline.counters if self._pgss_baseline is not None else {}
                    for row in cur.fetchall():
                        uid, did, qid, query, mean_ms, max_ms, calls = row
                        calls = int(calls or 0)
                        base = baseline.get((uid, did, qid))
                        base_calls = base.calls if base is not None else 0
                        if calls < base_calls:
                            raise RuntimeError(
                                "PostgreSQL pg_stat_statements calls counter moved backwards while reading slow_queries: "
                                f"query_key={(uid, did, qid)!r}, baseline_calls={base_calls}, current_calls={calls}"
                            )
                        calls_delta = calls - base_calls
                        if base is not None and calls_delta <= 0:
                            continue
                        finished.append({
                            "queryid": qid,
                            "query": query,
                            "mean_ms": mean_ms,
                            "max_ms": max_ms,
                            "calls": calls_delta if base else calls,
                            "source": "finished",
                        })
                    results = running + finished
                    return self._metric_success(
                        "slow_queries", "records",
                        threshold_ms=threshold,
                        records=results,
                    )
                elif metric_lower in {"active_connections", "cpu", "memory", "disk_io"}:
                    raise AssertionError(
                        f"PostgreSQL sampler metric reached the SQL branch unexpectedly: metric={metric_lower!r}"
                    )
                elif metric_lower == "disk_usage":
                    if isinstance(target, str) and target.isidentifier():
                        cur.execute("SELECT to_regclass(%s)::text;", (target,))
                        # Fall through to a direct table query if the target relation exists.
                        relation = cur.fetchone()[0]
                        if relation:
                            cur.execute("""
                                SELECT
                                    pg_total_relation_size(to_regclass(%s))::bigint AS total_bytes,
                                    pg_relation_size(to_regclass(%s))::bigint AS heap_bytes;
                            """, (target, target))
                            total_bytes, heap_bytes = cur.fetchone()
                            cur.execute(f"SELECT reltuples::bigint FROM pg_class WHERE oid = to_regclass(%s);", (target,))
                            estimated_rows = cur.fetchone()[0]
                            return self._metric_success(
                                "disk_usage", "snapshot", target=target,
                                snapshot={
                                    "total_mb": round(total_bytes / (1024**2), 2),
                                    "heap_mb": round(heap_bytes / (1024**2), 2),
                                    "estimated_rows": int(estimated_rows or 0),
                                },
                            )

                    try:
                        cur.execute("SELECT coalesce(sum(size), 0) FROM pg_ls_waldir();")
                        wal_bytes = int(cur.fetchone()[0] or 0)
                    except Exception:
                        wal_bytes = 0

                    # --- 四类明细：data / wal / temp / log ---
                    wal_mb = round(wal_bytes / (1024**2), 2)

                    # data: 所有数据库大小汇总
                    try:
                        cur.execute("SELECT coalesce(sum(pg_database_size(oid)), 0)::bigint FROM pg_database;")
                        data_mb = round(int(cur.fetchone()[0] or 0) / (1024**2), 2)
                    except Exception:
                        self._conn.rollback()
                        data_mb = 0.0

                    # temp: pg_ls_tmpdir() 实时临时文件（PG12+）
                    try:
                        cur.execute("SELECT coalesce(sum(size), 0) FROM pg_ls_tmpdir();")
                        temp_mb = round(int(cur.fetchone()[0] or 0) / (1024**2), 2)
                    except Exception:
                        self._conn.rollback()
                        temp_mb = 0.0

                    # log: 容器内日志文件大小
                    import subprocess as _sp
                    log_mb = 0.0
                    try:
                        container_name = self.deployment.container_name
                        r = _sp.run([
                            "docker", "exec", container_name,
                            "bash", "-c", "du -sb /var/log/postgresql 2>/dev/null | cut -f1"
                        ], capture_output=True, text=True, timeout=10)
                        if r.returncode == 0 and r.stdout.strip():
                            log_mb = round(int(r.stdout.strip()) / (1024**2), 2)
                    except Exception:
                        pass

                    used_mb = round(data_mb + wal_mb + temp_mb + log_mb, 2)

                    # --- 可写层剩余空间（df 读取） ---
                    import subprocess as _sp
                    available_mb = None
                    try:
                        container_name = self.deployment.container_name
                        r = _sp.run([
                            "docker", "exec", container_name,
                            "df", "--output=avail", "-B1", "/"
                        ], capture_output=True, text=True, timeout=10)
                        if r.returncode == 0:
                            lines = r.stdout.strip().splitlines()
                            if len(lines) >= 2:
                                available_mb = round(int(lines[1].strip()) / (1024 ** 2), 2)
                    except Exception:
                        pass

                    return self._metric_success(
                        "disk_usage", "snapshot",
                        snapshot={
                            "used_mb": used_mb,
                            "available_mb": available_mb,
                            "data_mb": data_mb,
                            "wal_mb": wal_mb,
                            "temp_mb": temp_mb,
                            "log_mb": log_mb,
                        },
                    )
                elif metric_lower == "qps":
                    raise AssertionError("PostgreSQL qps metric must be served by the sampler provider")
                elif metric_lower == "topsql":
                    if self._pgss_baseline is None:
                        raise RuntimeError("PostgreSQL topsql requires an initialized pg_stat_statements baseline")
                    current = capture_statement_snapshot(self._conn, int(time.time() * 1000))
                    interval_records = build_topsql_delta_records(
                        self._pgss_baseline,
                        current,
                        excluded_queryids=self._pg_statement_excluded_queryids,
                    )
                    rows = [
                        {
                            "queryid": int(record.payload["digest"]),
                            "query": record.payload["sql_text"],
                            "calls": record.payload["exec_count"],
                            "total_ms": round(float(record.payload["sum_latency"]), 2),
                            "mean_ms": round(float(record.payload["avg_latency"]), 2),
                            "rows": record.payload["rows"],
                            "shared_blks_hit": record.payload["shared_blks_hit"],
                            "shared_blks_read": record.payload["shared_blks_read"],
                            "shared_blks_written": record.payload["shared_blks_written"],
                            "temp_blks_read": record.payload["temp_blks_read"],
                            "temp_blks_written": record.payload["temp_blks_written"],
                        }
                        for record in interval_records
                    ]
                    rows.sort(key=lambda row: row["total_ms"], reverse=True)
                    return self._metric_success(
                        "topsql", "records", scope="since_deploy", records=rows[:10]
                    )
                elif metric_lower == "cache_hit_ratio":
                    raise AssertionError("PostgreSQL cache_hit_ratio metric must be served by the sampler provider")
                elif metric_lower == "dead_tuples":
                    table_list = []
                    if isinstance(tables, str) and tables.strip():
                        for raw in tables.split(","):
                            name = raw.strip()
                            # 仅保留合法标识符，避免 SQL 注入
                            if name and name.replace("_", "").isalnum():
                                table_list.append(name)
                    if table_list:
                        placeholders = ",".join(["%s"] * len(table_list))
                        cur.execute(f"""
                            SELECT schemaname, relname AS table_name, n_live_tup, n_dead_tup,
                                   round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0), 4) AS dead_ratio,
                                   last_autovacuum, last_vacuum
                            FROM pg_stat_user_tables
                            WHERE relname IN ({placeholders})
                            ORDER BY n_dead_tup DESC;
                        """, tuple(table_list))
                    else:
                        cur.execute("""
                            SELECT schemaname, relname AS table_name, n_live_tup, n_dead_tup,
                                   round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0), 4) AS dead_ratio,
                                   last_autovacuum, last_vacuum
                            FROM pg_stat_user_tables
                            ORDER BY n_dead_tup DESC
                            LIMIT 10;
                        """)
                    columns = [desc[0] for desc in cur.description]
                    results = [dict(zip(columns, row)) for row in cur.fetchall()]
                    for r in results:
                        if r.get("dead_ratio") is not None:
                            r["dead_ratio"] = float(r["dead_ratio"])
                    return self._metric_success(
                        "dead_tuples", "records", records=results
                    )
                else:
                    return json.dumps({"status": "error", "error": f"Unknown metric_type: {metric_type}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)

    def set_agent_sql_timeouts(self, statement_timeout: str, lock_timeout: str) -> None:
        """Bound blocking agent SQL like a real client timeout would.

        Only the Agent action path uses this: an agent statement that waits on
        a lock or runs forever must fail with a visible timeout instead of
        wedging the scenario run. Trusted injector/evaluator SQL is unaffected.
        """
        with self._sql_connection_lock:
            if not self._ensure_connection():
                return
            try:
                with self._conn.cursor() as cur:
                    cur.execute(f"SET statement_timeout = '{statement_timeout}'; SET lock_timeout = '{lock_timeout}';")
            except Exception:
                self._conn = None

    def reset_agent_sql_timeouts(self) -> None:
        with self._sql_connection_lock:
            if self._conn is None:
                return
            try:
                with self._conn.cursor() as cur:
                    cur.execute("SET statement_timeout = 0; SET lock_timeout = 0;")
            except Exception:
                self._conn = None

    @Tool(
        description=lazy_agent_text(
            zh=(
                "执行 PostgreSQL 当前实例或只读冻结历史连接面上的 SQL。"
                "返回结果最多 200 行且不超过 128 KiB，超限时 truncated=true 并附带 truncation_hint；"
                "此时请缩小查询窗口：只选需要的列、加 WHERE/LIMIT，或改用聚合后分页查看。"
            ),
            en=(
                "Execute SQL on the current PostgreSQL instance or on the read-only frozen history connection surface. "
                "The result has at most 200 rows and no more than 128 KiB; beyond that, truncated=true is set and "
                "truncation_hint is attached; in that case narrow the query window: select only the columns you need, "
                "add WHERE/LIMIT, or aggregate and then page through the result."
            ),
        ),
        arg_descriptions={
            "sql_query": lazy_agent_text(zh="要执行的 SQL 语句", en="SQL statement to execute"),
            "target": lazy_agent_text(
                zh="连接面名称；不传、传 'primary' 或传告警中的实例名 'postgresql-primary' 使用当前 PostgreSQL 实例，'history' 表示只读冻结历史",
                en=(
                    "Connection surface name; omitting it, passing 'primary', or passing the instance name from the alert "
                    "'postgresql-primary' uses the current PostgreSQL instance; 'history' means the read-only frozen history"
                ),
            ),
        },
    )
    def execute_sql(self, sql_query: str, target: Optional[str] = None) -> str:
        if target == "history":
            if self._history_sql_archive is None:
                return json.dumps({"status": "error", "error": "PostgreSQL history SQL surface is unavailable"}, ensure_ascii=False)
            try:
                columns, rows, row_count, truncated = self._history_sql_archive.execute(sql_query)
                payload = {"status": "success", "columns": columns, "result": rows, "row_count": row_count, "truncated": truncated}
                if truncated:
                    payload["truncation_hint"] = agent_text(zh=SQL_TRUNCATION_HINT, en=SQL_TRUNCATION_HINT_EN)
                return json.dumps(payload, ensure_ascii=False, default=str)
            except (ValueError, RuntimeError, TypeError) as exc:
                return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)
        if target == "postgresql-primary":
            # Alerts and docs name the instance postgresql-primary; agents echo
            # that name back as the SQL target. It is the primary surface.
            target = "primary"
        if target == "standby":
            return self._execute_standby_sql(sql_query)
        if target not in {None, "primary"}:
            return json.dumps({"status": "error", "error": f"Unknown PostgreSQL SQL target: {target!r}; valid targets: omit the argument, 'primary' (current instance), 'postgresql-primary' (alert instance name), 'standby' (read-only replica endpoint, when configured), or 'history' (frozen history)"}, ensure_ascii=False)
        return self._execute_sql_surface(sql_query, enforce_history_guard=True)

    def _execute_standby_sql(self, sql_query: str) -> str:
        """Read-only SQL against the configured standby endpoint.

        The route only exists when a scenario registered a "standby" workload
        connection pool; the session is forced read-only so remediation SQL
        can never reach the replica by accident.
        """
        endpoint = self._workload_connection_endpoints.get("standby")
        if endpoint is None:
            return json.dumps({"status": "error", "error": f"PostgreSQL standby endpoint is not configured: pools={sorted(self._workload_connection_endpoints)}"}, ensure_ascii=False)
        import psycopg2

        try:
            connection = psycopg2.connect(
                host=str(endpoint["host"]),
                port=int(endpoint["port"]),
                user=str(endpoint["user"]),
                password=str(endpoint["password"]),
                dbname=str(endpoint["dbname"]),
                connect_timeout=3,
                application_name="aiopsbench-standby-sql",
            )
        except psycopg2.Error as exc:
            return json.dumps({"status": "error", "error": f"PostgreSQL standby connection failed: {exc!r}"}, ensure_ascii=False)
        try:
            connection.set_session(readonly=True, autocommit=True)
            with connection.cursor() as cur:
                cur.execute(sql_query)
                if cur.description:
                    fetchmany = getattr(cur, "fetchmany", None)
                    fetched = fetchmany(PG_SQL_RESULT_MAX_ROWS + 1) if callable(fetchmany) else cur.fetchall()
                    result, truncated = _bound_sql_rows(fetched)
                    payload = {"status": "success", "columns": [column.name for column in cur.description], "result": result}
                    if truncated:
                        payload.update({"truncated": True, "returned_rows": len(result), "row_limit": PG_SQL_RESULT_MAX_ROWS, "byte_limit": PG_SQL_RESULT_MAX_BYTES})
                else:
                    payload = {"status": "success", "columns": [], "result": []}
            return json.dumps(payload, ensure_ascii=False, default=str)
        except psycopg2.Error as exc:
            return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)
        finally:
            connection.close()

    def execute_sql_trusted(self, sql_query: str) -> str:
        """Execute current-state SQL for evaluator and injector trusted checks."""
        return self._execute_sql_surface(sql_query, enforce_history_guard=False)

    def _execute_sql_surface(self, sql_query: str, *, enforce_history_guard: bool) -> str:
        with self._sql_connection_lock:
            return self._execute_sql_surface_locked(sql_query, enforce_history_guard)

    def _execute_sql_surface_locked(self, sql_query: str, enforce_history_guard: bool) -> str:
        if not self._ensure_connection():
            return json.dumps({"status": "error", "error": _pg_unavailable_error()}, ensure_ascii=False)
        if enforce_history_guard and self._history_timeline is not None:
            try:
                reject_postgres_public_historical_sql(sql_query)
            except (ValueError, RuntimeError, TypeError) as exc:
                return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)
        connection = self._conn
        if connection is None:
            # A concurrent caller's failure may have dropped the shared
            # connection between the readiness check and here; reconnect once.
            if not self._ensure_connection():
                return json.dumps({"status": "error", "error": _pg_unavailable_error()}, ensure_ascii=False)
            connection = self._conn
        try:
            with connection.cursor() as cur:
                cur.execute(sql_query)
                if cur.description:
                    fetchmany = getattr(cur, "fetchmany", None)
                    fetched = (
                        fetchmany(PG_SQL_RESULT_MAX_ROWS + 1)
                        if callable(fetchmany)
                        else cur.fetchall()
                    )
                    result, truncated = _bound_sql_rows(fetched)
                    payload = {
                        "status": "success",
                        "columns": [column.name for column in cur.description],
                        "result": result,
                    }
                    if truncated:
                        payload.update({
                            "truncated": True,
                            "returned_rows": len(result),
                            "row_limit": PG_SQL_RESULT_MAX_ROWS,
                            "byte_limit": PG_SQL_RESULT_MAX_BYTES,
                            "truncation_hint": agent_text(zh=SQL_TRUNCATION_HINT, en=SQL_TRUNCATION_HINT_EN),
                        })
                    return json.dumps(payload, default=str, ensure_ascii=False)
                else:
                    connection.commit()
                    return json.dumps({"status": "success", "message": "SQL executed."}, ensure_ascii=False)
        except Exception as e:
            self._conn = None
            return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)

    @Tool(
        description="DB-GPT D-Bot semantic tool：检查指定指标是否异常",
        arg_descriptions={
            "metric_name": "指标名称，如 cpu_usage、memory_usage、io_usage、slow_queries、workload、query",
        },
    )
    def whether_is_abnormal_metric(self, metric_name: str) -> str:
        metric_type = self._db_gpt_metric_name(metric_name)
        return self.query_metrics(metric_type=metric_type)

    @Tool(
        description=(
            "DB-GPT D-Bot semantic tool：按专家类型聚合诊断证据，包含系统指标、workload、"
            "slow queries 和可选 PostgreSQL 知识库片段"
        ),
        arg_descriptions={
            "metric_name": "专家名或指标名，如 CpuExpert、MemoryExpert、IoExpert、QueryExpert",
            "alert_metric": "告警指标或告警摘要，可选",
        },
    )
    def match_diagnose_knowledge(self, metric_name: str, alert_metric: str = "") -> str:
        metric_prefix = self._db_gpt_metric_prefix(metric_name)
        system_metrics = {
            "cpu": ["cpu", "active_connections", "qps"],
            "io": ["disk_io", "disk_usage", "cache_hit_ratio"],
            "memory": ["memory", "cache_hit_ratio", "active_connections"],
        }[metric_prefix]
        metrics = system_metrics + ["topsql", "slow_queries"]
        results = []
        for metric in metrics:
            kwargs: Dict[str, Any] = {"metric_type": metric}
            if metric == "slow_queries":
                kwargs["threshold_ms"] = 1000
            results.append(json.loads(self.query_metrics(**kwargs)))

        knowledge = []
        if "query_knowledge_base" in self._alias_to_tool_spec:
            query = " ".join([metric_name, alert_metric, *metrics]).strip()
            knowledge = json.loads(self.execute_action("query_knowledge_base", {"query": query, "top_k": 5}))

        return json.dumps({
            "status": "success",
            "metric_prefix": metric_prefix,
            "system_metrics": system_metrics,
            "workload_metrics": ["topsql"],
            "slow_query_metrics": ["slow_queries"],
            "results": results,
            "knowledge": knowledge,
        }, ensure_ascii=False, default=str)

    @Tool(
        description=(
            "DB-GPT D-Bot semantic tool：收集索引优化所需的 workload、schema、列统计、已有索引"
            "和 hypopg 可用性证据"
        ),
        arg_descriptions={
            "start_time": "诊断窗口开始时间，可选",
            "end_time": "诊断窗口结束时间，可选",
        },
    )
    def optimize_index_selection(self, start_time: str = "", end_time: str = "") -> str:
        queries = [
            (
                "workload",
                "SELECT current_database() AS dbname, query AS sql, calls, "
                "total_exec_time, mean_exec_time "
                "FROM pg_stat_statements "
                "WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database()) "
                "AND query NOT ILIKE '%pg_stat_statements%' "
                "AND query NOT ILIKE 'EXPLAIN%' "
                "ORDER BY total_exec_time DESC LIMIT 10;",
            ),
            (
                "schema",
                "SELECT table_schema, table_name, column_name, data_type "
                "FROM information_schema.columns "
                "WHERE table_schema NOT IN ('pg_catalog', 'information_schema') "
                "ORDER BY table_schema, table_name, ordinal_position;",
            ),
            (
                "column_statistics",
                "SELECT schemaname, tablename, attname, null_frac, n_distinct, "
                "most_common_vals::text AS most_common_vals, histogram_bounds::text AS histogram_bounds "
                "FROM pg_stats "
                "WHERE schemaname NOT IN ('pg_catalog', 'information_schema') "
                "ORDER BY schemaname, tablename, attname;",
            ),
            (
                "existing_indexes",
                "SELECT schemaname, tablename, indexname, indexdef "
                "FROM pg_indexes "
                "WHERE schemaname NOT IN ('pg_catalog', 'information_schema') "
                "ORDER BY schemaname, tablename, indexname;",
            ),
            (
                "hypopg_available",
                "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'hypopg') "
                "AS hypopg_available;",
            ),
        ]
        evidence = [
            {"name": name, "result": json.loads(self.execute_sql(sql_query))}
            for name, sql_query in queries
        ]
        return json.dumps({
            "status": "success",
            "start_time": start_time,
            "end_time": end_time,
            "evidence": evidence,
        }, ensure_ascii=False, default=str)

    @staticmethod
    def _db_gpt_metric_name(metric_name: str) -> str:
        name = str(metric_name).strip().lower()
        aliases = {
            "cpu_usage": "cpu",
            "memory_usage": "memory",
            "mem_usage": "memory",
            "io_usage": "disk_io",
            "io": "disk_io",
            "disk": "disk_usage",
            "index": "topsql",
            "query": "slow_queries",
            "workload": "topsql",
            "configuration": "active_connections",
            "recovery": "disk_usage",
        }
        return aliases.get(name, name)

    @staticmethod
    def _db_gpt_metric_prefix(metric_name: str) -> str:
        name = str(metric_name).strip().lower()
        if "cpu" in name or "workload" in name or "index" in name or "query" in name:
            return "cpu"
        if "write" in name or "io" in name:
            return "io"
        if "mem" in name:
            return "memory"
        return "cpu"

    def _restart_pg_instance(self) -> str:
        if not self.deployment.restart_pg():
            return json.dumps({"status": "error", "error": "pg_ctl restart failed"})
        self._conn = None
        if not self.deployment.wait_for_ready(timeout=60):
            return json.dumps({"status": "error", "error": "PG not ready after restart"})
        self._ensure_connection()
        return json.dumps({"status": "success", "action": "restart"})

    def _start_pg_instance(self) -> str:
        if not self.deployment.start_pg():
            return json.dumps({"status": "error", "error": "pg_ctl start failed"})
        if not self.deployment.wait_for_ready(timeout=60):
            return json.dumps({"status": "error", "error": "PG not ready after start"})
        self._ensure_connection()
        return json.dumps({"status": "success", "action": "start"})

    @Tool(
        description=lazy_agent_text(
            zh=(
                "管理数据库实例（进程控制与配置管理）。"
                "get_config/set_config/reset_config 的 target 可以是 PostgreSQL 参数，"
                "也可以是少量实例级 OS 进程资源限制。"
                "terminate_process 仅用于终止容器内指定的非 PostgreSQL OS 进程；"
                "数据库会话应通过 execute_sql 执行 pg_terminate_backend。"
                "validate_backup 仅用于备份/RPO 场景，校验容器内物理备份文件和归档 WAL 可恢复链；"
                "它不是通用 SQL 查询，也不能由普通数据库连接替代。"
                "配置 PgBouncer endpoint 后，pgbouncer_show_*、pgbouncer_set_config 和 "
                "pgbouncer_reload 用于真实连接池 admin 操作。"
            ),
            en=(
                "Manage the database instance (process control and configuration management). "
                "The target of get_config/set_config/reset_config can be a PostgreSQL parameter "
                "or one of a few instance-level OS process resource limits. "
                "terminate_process is only for terminating a specified non-PostgreSQL OS process in the container; "
                "database sessions should be terminated with pg_terminate_backend through execute_sql. "
                "validate_backup is only for backup/RPO scenarios and checks the physical backup files in the container "
                "and the recoverable chain of archived WAL; "
                "it is not a general SQL query and cannot be replaced by an ordinary database connection. "
                "When a PgBouncer endpoint is configured, pgbouncer_show_*, pgbouncer_set_config and "
                "pgbouncer_reload perform real connection pool admin operations."
            ),
        ),
        arg_descriptions={
            "action": lazy_agent_text(
                zh="操作类型，可选值: restart, start, stop, reboot, get_config, set_config, reset_config, terminate_process, validate_backup, pgbouncer_show_pools, pgbouncer_show_config, pgbouncer_show_stats, pgbouncer_set_config, pgbouncer_reload。terminate_process 只面向非 PostgreSQL OS 进程；validate_backup 只面向备份/RPO 场景；reboot 为重启整台机器的高危操作，仅在明确需要机器级重启时使用",
                en=(
                    "Operation type, allowed values: restart, start, stop, reboot, get_config, set_config, reset_config, "
                    "terminate_process, validate_backup, pgbouncer_show_pools, pgbouncer_show_config, pgbouncer_show_stats, "
                    "pgbouncer_set_config, pgbouncer_reload. terminate_process targets only non-PostgreSQL OS processes; "
                    "validate_backup applies only to backup/RPO scenarios; reboot is a high-risk operation that restarts "
                    "the whole machine, use it only when a machine-level restart is clearly required"
                ),
            ),
            "target": lazy_agent_text(
                zh="目标实例名、配置参数名、进程资源名、进程标识或备份目录；terminate_process 使用 PID 或简单进程名；validate_backup 使用容器内备份目录或 manifest 路径",
                en=(
                    "Target instance name, configuration parameter name, process resource name, process identifier or "
                    "backup directory; terminate_process takes a PID or a simple process name; validate_backup takes a "
                    "backup directory or manifest path inside the container"
                ),
            ),
            "value": lazy_agent_text(
                zh="配置值（用于 set_config 或 pgbouncer_set_config；validate_backup、SHOW 和 reload 可留空）",
                en="Configuration value (for set_config or pgbouncer_set_config; may be left empty for validate_backup, SHOW and reload)",
            ),
        },
    )
    def manage_instance(self, action: str, target: str = None, value: str = None) -> str:
        controller = getattr(self, "_rpo_controller", None)
        if controller is not None and action in {
            "archive_status",
            "rpo_topology",
            "recover_archive",
            "pitr_restore",
            "validate_backup",
        }:
            return controller.handle_manage_instance(action, target, value)
        if self.deployment is None:
            return json.dumps({"status": "error", "error": "No deployment configured"})

        if action == "pgbouncer_show_pools":
            return self.pgbouncer_admin_query("SHOW POOLS;")
        elif action == "pgbouncer_show_config":
            return self.pgbouncer_admin_query("SHOW CONFIG;")
        elif action == "pgbouncer_show_stats":
            return self.pgbouncer_admin_query("SHOW STATS;")
        elif action == "pgbouncer_reload":
            return self._reload_pgbouncer()
        elif action == "pgbouncer_set_config":
            return self._set_pgbouncer_config(target, value)
        elif action == "restart":
            print(f"[Env:PGEnv] Restarting PostgreSQL process...")
            return self._run_lifecycle_with_sampler("restart", self._restart_pg_instance)
        elif action == "stop":
            print(f"[Env:PGEnv] Stopping PostgreSQL process...")
            if not self.deployment.stop_pg():
                return json.dumps({"status": "error", "error": "pg_ctl stop failed"})
            self._conn = None
            return json.dumps({"status": "success", "action": "stop"})
        elif action == "start":
            print(f"[Env:PGEnv] Starting PostgreSQL process...")
            return self._run_lifecycle_with_sampler("start", self._start_pg_instance)
        elif action == "reboot":
            print(f"[Env:PGEnv] Rebooting machine (docker stop/start)...")
            sampler_was_running = self._sampler_thread is not None and self._sampler_thread.is_alive()
            self._expected_sampler_disconnect_reason = "manage_instance('reboot')"
            self._expected_sampler_disconnect_evidence = {
                "action": "reboot",
                "sampler_was_running": str(sampler_was_running),
            }
            if sampler_was_running:
                self._stop_sampler()
            self._reset_cgroup_io_sampler_state()
            try:
                if not self.deployment.reboot_machine():
                    return json.dumps({"status": "error", "error": "Machine reboot failed"})
                self._conn = None
                timeout = int(self.deployment.resources.get("reboot_ready_timeout_sec", 120))
                if not self.deployment.wait_for_ready(timeout=timeout):
                    return json.dumps({"status": "error", "error": "PG not ready after reboot"})
                self._ensure_connection()
                return json.dumps({"status": "success", "action": "reboot"})
            finally:
                self._reset_cgroup_io_sampler_state()
                if self._scenario_metric_provider is None:
                    self._start_sampler()
                self._expected_sampler_disconnect_reason = None
                self._expected_sampler_disconnect_evidence = None
        elif action == "get_config":
            return self._get_config(target)
        elif action == "set_config":
            return self._set_config(target, value)
        elif action == "reset_config":
            return self._reset_config(target)
        elif action == "terminate_process":
            return self._terminate_process(target)
        elif action == "validate_backup":
            return self._validate_backup(target)
        else:
            return json.dumps({"status": "error", "error": f"Unknown action: {action}"})

    def _set_pgbouncer_config(self, target: str, value: str) -> str:
        allowed = {
            "pool_mode",
            "default_pool_size",
            "reserve_pool_size",
            "reserve_pool_timeout",
            "max_db_connections",
            "max_user_connections",
            "max_client_conn",
        }
        key = str(target or "").strip().casefold()
        if key not in allowed:
            return json.dumps(
                {"status": "error", "error": f"Unsupported PgBouncer setting: {target!r}", "allowed": sorted(allowed)},
                ensure_ascii=False,
            )
        if value is None or not str(value).strip():
            return json.dumps({"status": "error", "error": "Missing PgBouncer setting value"}, ensure_ascii=False)
        normalized = str(value).strip()
        if len(normalized) > 64 or any(character in normalized for character in "\r\n;'\\"):
            return json.dumps({"status": "error", "error": "Invalid PgBouncer setting value"}, ensure_ascii=False)
        result = self.pgbouncer_admin_query(f"SET {key} = '{normalized}';")
        try:
            payload = json.loads(result)
        except json.JSONDecodeError:
            payload = {}
        if payload.get("status") == "success":
            self._pgbouncer_runtime_overrides[key] = normalized
        return result

    def _reload_pgbouncer(self) -> str:
        result = self.pgbouncer_admin_query("RELOAD;")
        try:
            payload = json.loads(result)
        except json.JSONDecodeError:
            payload = {}
        if payload.get("status") != "success":
            return result
        reapplied = []
        for key, value in self._pgbouncer_runtime_overrides.items():
            reapplied_result = self.pgbouncer_admin_query(f"SET {key} = '{value}';")
            try:
                reapplied_payload = json.loads(reapplied_result)
            except json.JSONDecodeError:
                reapplied_payload = {}
            if reapplied_payload.get("status") != "success":
                return json.dumps(
                    {"status": "error", "error": f"Failed to reapply PgBouncer setting: {key}"},
                    ensure_ascii=False,
                )
            reapplied.append(key)
        return json.dumps(
            {"status": "success", "action": "reload", "reapplied": reapplied},
            ensure_ascii=False,
        )

    def _get_config(self, param_name: str) -> str:
        if not param_name:
            return json.dumps({"status": "error", "error": "Missing param name (target)"})
        import subprocess
        if self._is_nofile_config(param_name):
            try:
                payload = self.deployment.get_pg_nofile_limit()
                if payload.get("status") != "success":
                    return json.dumps(payload, ensure_ascii=False)
                return json.dumps({
                    "status": "success",
                    "param": "nofile",
                    "value": payload.get("configured", "(default)"),
                    "running_soft": payload.get("running_soft", "(unknown)"),
                    "running_hard": payload.get("running_hard", "(unknown)"),
                    "source": "os_process_limit",
                }, ensure_ascii=False)
            except Exception as e:
                return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)
        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute(f"SHOW {param_name};")
                    val = cur.fetchone()[0]
                return json.dumps({"status": "success", "param": param_name, "value": val, "source": "runtime"})
            except Exception:
                pass
        container = self.deployment.container_name
        try:
            result = subprocess.run(
                ["docker", "exec", container, "cat",
                 f"{self.deployment.pgdata}/postgresql.auto.conf"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                if key.strip() == param_name:
                    return json.dumps({"status": "success", "param": param_name, "value": val.strip().strip("'"), "source": "auto.conf"})
            return json.dumps({"status": "success", "param": param_name, "value": "(default)", "source": "default"})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

    def _set_config(self, param_name: str, value: str) -> str:
        if not param_name or value is None:
            return json.dumps({"status": "error", "error": "Missing param name (target) or value"})
        import psycopg2
        from psycopg2 import sql
        if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*", param_name) is None:
            return json.dumps({"status": "error", "error": f"Invalid PostgreSQL parameter name: param={param_name!r}"})
        if self._is_nofile_config(param_name):
            try:
                limit = int(str(value).strip())
            except ValueError:
                return json.dumps({"status": "error", "error": "nofile value must be an integer"}, ensure_ascii=False)
            if limit < 8:
                return json.dumps({"status": "error", "error": "nofile value is too low"}, ensure_ascii=False)
            try:
                if not self.deployment.set_pg_nofile_limit(limit):
                    return json.dumps({"status": "error", "error": "failed to write nofile limit"}, ensure_ascii=False)
                return json.dumps({
                    "status": "success",
                    "action": "set_config",
                    "param": "nofile",
                    "value": str(limit),
                    "note": "OS process nofile limit written; restart PostgreSQL to apply",
                }, ensure_ascii=False)
            except Exception as e:
                return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)
        if self._conn is not None and not self._conn.closed:
            try:
                with self._conn.cursor() as cur:
                    cur.execute(
                        sql.SQL("ALTER SYSTEM SET {} = %s;").format(sql.Identifier(param_name)),
                        (value,),
                    )
                return json.dumps({"status": "success", "action": "set_config", "param": param_name, "value": value, "note": agent_text(zh="需要 restart/reload 生效", en="requires restart/reload to take effect")})
            except psycopg2.Error as error:
                return json.dumps({"status": "error", "error": f"ALTER SYSTEM SET failed: param={param_name!r}, error={error}"})
        container = self.deployment.container_name
        config_path = f"{self.deployment.pgdata}/postgresql.auto.conf"
        try:
            result = subprocess.run(
                ["docker", "exec", container, "cat", config_path],
                capture_output=True, text=True, timeout=10, check=True,
            )
            setting = re.compile(rf"^\s*{re.escape(param_name)}\s*=", re.IGNORECASE)
            contents = "".join(
                line for line in result.stdout.splitlines(keepends=True)
                if not setting.match(line)
            )
            quoted_value = (
                value.replace("\\", "\\\\").replace("'", "''")
                .replace("\n", "\\n").replace("\r", "\\r")
            )
            contents = contents.rstrip("\n") + f"\n{param_name} = '{quoted_value}'\n"
            subprocess.run(
                ["docker", "exec", "-i", container, "tee", config_path],
                input=contents, capture_output=True, text=True, timeout=10, check=True,
            )
            return json.dumps({"status": "success", "action": "set_config", "param": param_name, "value": value, "note": agent_text(zh="已写入 auto.conf，需要 start/restart 生效", en="written to auto.conf; requires start/restart to take effect")})
        except (OSError, subprocess.SubprocessError) as error:
            return json.dumps({"status": "error", "error": f"Cannot write PostgreSQL setting: container={container!r}, path={config_path!r}, param={param_name!r}, error={error}"})

    def _reset_config(self, param_name: str) -> str:
        if not param_name:
            return json.dumps({"status": "error", "error": "Missing param name (target)"})
        import subprocess
        if self._is_nofile_config(param_name):
            try:
                if not self.deployment.reset_pg_nofile_limit():
                    return json.dumps({"status": "error", "error": "failed to reset nofile limit"}, ensure_ascii=False)
                return json.dumps({
                    "status": "success",
                    "action": "reset_config",
                    "param": "nofile",
                    "note": "OS process nofile limit reset; restart PostgreSQL to apply",
                }, ensure_ascii=False)
            except Exception as e:
                return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)
        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute(f"ALTER SYSTEM RESET {param_name};")
                return json.dumps({"status": "success", "action": "reset_config", "param": param_name})
            except Exception:
                pass
        container = self.deployment.container_name
        try:
            subprocess.run(
                ["docker", "exec", container, "sed", "-i",
                 f"/^{param_name}/d", f"{self.deployment.pgdata}/postgresql.auto.conf"],
                capture_output=True, text=True, timeout=10, check=True
            )
            return json.dumps({"status": "success", "action": "reset_config", "param": param_name, "note": agent_text(zh="已从 auto.conf 移除，需要 start/restart 生效", en="removed from auto.conf; requires start/restart to take effect")})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

    def _is_nofile_config(self, param_name: str) -> bool:
        return str(param_name or "").lower().strip() in {
            "nofile",
            "ulimit_n",
            "ulimit_nofile",
            "max_open_files",
            "open_files",
        }

    def _terminate_process(self, target: str) -> str:
        import re
        import subprocess

        if not target:
            return json.dumps({"status": "error", "error": "Missing process target"})
        target_text = str(target).strip()
        if target_text.casefold() in {"postgres", "postmaster", "postgresql"}:
            return json.dumps({
                "status": "error",
                "action": "terminate_process",
                "target": target_text,
                "error": (
                    "Refusing to terminate the PostgreSQL server process; use a lifecycle action "
                    "or execute_sql with pg_terminate_backend for a database session"
                ),
            }, ensure_ascii=False)
        if target_text.isdigit():
            pid = int(target_text)
            command = (
                f"comm=$(ps -p {pid} -o comm= 2>/dev/null || true); "
                "case \"$comm\" in postgres|postmaster|postgres:*) exit 4;; esac; "
                f"kill -TERM {pid} && printf '%s\\n' {pid}"
            )
        else:
            if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", target_text):
                return json.dumps({"status": "error", "error": "Process target must be a PID or simple name"}, ensure_ascii=False)
            command = (
                "roots=$(ps -eo pid=,args= | awk "
                f"'$0 ~ /{target_text}/ && $0 !~ /awk/ && $0 !~ /ps -eo/ {{print $1}}'); "
                "test -n \"$roots\" || exit 3; "
                "all=\"$roots\"; frontier=\"$roots\"; "
                "for depth in $(seq 1 8); do "
                "children=''; "
                "for parent in $frontier; do "
                "found=$(pgrep -P \"$parent\" 2>/dev/null || true); "
                "children=\"$children $found\"; "
                "done; "
                "frontier=$(printf '%s\\n' $children | awk 'NF && !seen[$1]++'); "
                "test -n \"$frontier\" || break; "
                "all=\"$all $frontier\"; "
                "done; "
                "pids=$(printf '%s\\n' $all | awk 'NF && !seen[$1]++'); "
                "kill -TERM $pids; "
                "sleep 0.2; "
                "kill -KILL $roots 2>/dev/null || true; "
                "printf '%s\\n' $pids"
            )
        try:
            result = subprocess.run(
                ["docker", "exec", self.deployment.container_name, "bash", "-lc", command],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode not in (0,):
                return json.dumps({
                    "status": "error",
                    "action": "terminate_process",
                    "target": target_text,
                    "error": result.stderr.strip() or result.stdout.strip() or f"exit_code={result.returncode}",
                }, ensure_ascii=False)
            killed = [line.strip() for line in result.stdout.splitlines() if line.strip().isdigit()]
            return json.dumps({
                "status": "success",
                "action": "terminate_process",
                "target": target_text,
                "killed_pids": killed,
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False)

    def _safe_container_path(self, path: str, label: str) -> str:
        import posixpath
        import re

        if not path:
            raise ValueError(f"Missing {label}")
        normalized = posixpath.normpath(str(path).strip())
        allowed_prefixes = (
            "/tmp/",
            "/var/tmp/",
            "/var/lib/postgresql/backup/",
        )
        if not normalized.startswith(allowed_prefixes):
            raise ValueError(f"{label} must be under /tmp, /var/tmp, or /var/lib/postgresql/backup")
        if not re.fullmatch(r"[A-Za-z0-9_./:=@+-]+", normalized):
            raise ValueError(f"{label} contains unsupported characters")
        return normalized

    def _docker_read_text(self, path: str) -> str:
        import subprocess

        result = subprocess.run(
            ["docker", "exec", self.deployment.container_name, "cat", path],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            raise FileNotFoundError(result.stderr.strip() or result.stdout.strip() or path)
        return result.stdout

    def _docker_file_size(self, path: str):
        import subprocess

        result = subprocess.run(
            [
                "docker", "exec", self.deployment.container_name,
                "bash", "-lc", f"test -f '{path}' && stat -c %s '{path}'",
            ],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return None
        try:
            return int(result.stdout.strip())
        except ValueError:
            return None

    def _validate_backup(self, target: str) -> str:
        import posixpath
        import subprocess

        try:
            target_path = self._safe_container_path(target, "backup target")
            if target_path.endswith(".json"):
                manifest_path = target_path
                backup_root = posixpath.dirname(target_path)
            else:
                backup_root = target_path
                manifest_path = posixpath.join(target_path, "backup_manifest.json")

            manifest = json.loads(self._docker_read_text(manifest_path))
            backup_root = self._safe_container_path(
                manifest.get("base_backup_path") or backup_root,
                "base backup path",
            )
            archive_dir = self._safe_container_path(
                manifest.get("archive_dir"),
                "archive directory",
            )
            backup_id = str(manifest.get("backup_id") or posixpath.basename(backup_root))

            sandbox_dir = f"/tmp/pg_restore_sandbox/{backup_id}"
            subprocess.run(
                [
                    "docker", "exec", self.deployment.container_name,
                    "bash", "-lc", f"rm -rf '{sandbox_dir}' && mkdir -p '{sandbox_dir}'",
                ],
                capture_output=True, text=True, timeout=15,
            )

            recovery_log = [
                f"restore sandbox initialized at {sandbox_dir}",
                f"loaded backup manifest {manifest_path}",
            ]
            checked_files = []
            base_backup_ok = True
            for item in manifest.get("files", []):
                rel_path = str(item.get("path") or "")
                expected_size = int(item.get("size_bytes") or 0)
                full_path = self._safe_container_path(
                    posixpath.join(backup_root, rel_path),
                    "backup file path",
                )
                actual_size = self._docker_file_size(full_path)
                ok = actual_size == expected_size and expected_size > 0
                checked_files.append({
                    "path": rel_path,
                    "expected_size_bytes": expected_size,
                    "actual_size_bytes": actual_size,
                    "ok": ok,
                })
                if not ok:
                    base_backup_ok = False
            recovery_log.append(
                f"base backup file check {'passed' if base_backup_ok else 'failed'} "
                f"({sum(1 for item in checked_files if item['ok'])}/{len(checked_files)} files)"
            )

            missing_segments = []
            previous_end_time = manifest.get("backup_stop_time")
            wal_chain = sorted(
                manifest.get("wal_chain", []),
                key=lambda item: int(item.get("sequence", 0)),
            )
            for segment in wal_chain:
                wal_file = str(segment.get("wal_file") or "")
                wal_path = self._safe_container_path(
                    posixpath.join(archive_dir, wal_file),
                    "archive WAL path",
                )
                size = self._docker_file_size(wal_path)
                if size is None or size <= 0:
                    missing_segments.append({
                        "wal_file": wal_file,
                        "sequence": int(segment.get("sequence") or 0),
                        "start_time": segment.get("start_time"),
                        "end_time": segment.get("end_time"),
                        "path": wal_path,
                    })
                    break
                recovery_log.append(
                    f"replayed archived WAL {wal_file} through {segment.get('end_time')}"
                )
                previous_end_time = segment.get("end_time") or previous_end_time

            archive_chain_ok = not missing_segments
            requested_target_time = manifest.get("requested_recovery_target_time")
            latest_recoverable_time = (
                previous_end_time
                or manifest.get("latest_recoverable_time")
                or manifest.get("backup_stop_time")
            )
            if missing_segments:
                first_missing = missing_segments[0]
                recovery_log.append(
                    "archive gap detected: missing "
                    f"{first_missing['wal_file']} covering "
                    f"{first_missing.get('start_time')}..{first_missing.get('end_time')}"
                )
                recovery_log.append(
                    f"recovery cannot proceed past {latest_recoverable_time}; "
                    f"requested target was {requested_target_time}"
                )
            else:
                recovery_log.append(
                    f"archive chain is continuous through requested target {requested_target_time}"
                )

            return json.dumps({
                "status": "success",
                "action": "validate_backup",
                "backup_id": backup_id,
                "backup_path": backup_root,
                "manifest_path": manifest_path,
                "archive_dir": archive_dir,
                "validation_status": "passed" if base_backup_ok and archive_chain_ok else "failed",
                "base_backup_ok": base_backup_ok,
                "archive_chain_ok": archive_chain_ok,
                "recoverable": bool(base_backup_ok and archive_chain_ok),
                "checked_files": checked_files,
                "missing_wal_segments": missing_segments,
                "latest_recoverable_time": latest_recoverable_time,
                "requested_recovery_target_time": requested_target_time,
                "recovery_log": recovery_log,
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "action": "validate_backup",
                "error": str(e),
            }, ensure_ascii=False)

    def _pg_log_size(self) -> int:
        return sum(self._pg_log_snapshot().values())

    def _pg_log_snapshot(self) -> dict[str, int]:
        snapshot = self.deployment.postgres_log_sizes()
        if not snapshot:
            raise RuntimeError(
                f"PostgreSQL log snapshot is empty: container={self.deployment.container_name!r}"
            )
        return snapshot

    def _reset_pg_log_visibility(self) -> None:
        self._pg_log_visible_offsets = self._pg_log_snapshot()

    def _read_visible_pg_log(self) -> str:
        output, offsets = self.deployment.read_postgres_logs_after(self._pg_log_visible_offsets)
        self._pg_log_visible_offsets = offsets
        return output.strip()

    @Tool(
        description=lazy_agent_text(
            zh="读取系统、数据库日志或当前 Case 声明的冻结 operation event 记录",
            en="Read system or database logs, or the frozen operation event records declared by the current Case",
        ),
        arg_descriptions={
            "log_type": lazy_agent_text(
                zh="日志类型，可选值: dmesg, docker_logs, pg_log, operation_event；operation_event 必须同时提供 start_timestamp 与 end_timestamp",
                en="Log type, allowed values: dmesg, docker_logs, pg_log, operation_event; operation_event requires both start_timestamp and end_timestamp",
            ),
            "lines": lazy_agent_text(
                zh="返回行数/记录数上限；operation_event 只支持此分页上限，不支持 start_line/end_line/match_key",
                en="Maximum number of lines/records to return; operation_event supports only this page limit, not start_line/end_line/match_key",
            ),
            "start_line": lazy_agent_text(
                zh="1-based 起始行号；仅文本日志可用，operation_event 禁止使用",
                en="1-based start line number; text logs only, not allowed for operation_event",
            ),
            "end_line": lazy_agent_text(
                zh="1-based 结束行号；仅文本日志可用，operation_event 禁止使用",
                en="1-based end line number; text logs only, not allowed for operation_event",
            ),
            "match_key": lazy_agent_text(
                zh="文本日志关键字；operation_event 禁止使用，应改用 filters",
                en="Text log keyword; not allowed for operation_event, use filters instead",
            ),
            "start_timestamp": lazy_agent_text(
                zh="冻结历史窗口起点；必须与 end_timestamp 一起提供（operation_event 必填）",
                en="Start of the frozen history window; must be provided together with end_timestamp (required for operation_event)",
            ),
            "end_timestamp": lazy_agent_text(
                zh="冻结历史窗口终点；必须与 start_timestamp 一起提供（operation_event 必填）",
                en="End of the frozen history window; must be provided together with start_timestamp (required for operation_event)",
            ),
            "target": lazy_agent_text(
                zh="可选的冻结历史记录目标；不传时覆盖 Case 中该来源的所有目标",
                en="Optional frozen history record target; when omitted, all targets of this source in the Case are covered",
            ),
            "filters": lazy_agent_text(
                zh="可选的冻结历史字段过滤条件；仅适用于 operation_event",
                en="Optional frozen history field filter conditions; applies only to operation_event",
            ),
        },
    )
    def read_log(
        self,
        log_type: str,
        lines: int = 100,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        match_key: Optional[str] = None,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None,
        target: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        import subprocess
        container_name = self.deployment.container_name
        try:
            if (start_timestamp is None) != (end_timestamp is None):
                raise ValueError("read_log.start_timestamp and read_log.end_timestamp must be provided together")
            if start_timestamp is not None:
                history_limit = int(lines)
                if history_limit <= 0:
                    raise ValueError(f"Historical log line limit must be positive: lines={lines!r}")
                source = {
                    "pg_log": HistoricalRecordSource.COMPONENT_LOG,
                    "operation_event": HistoricalRecordSource.OPERATION_EVENT,
                }.get(log_type)
                if source is None:
                    raise ValueError(
                        "Frozen PostgreSQL log windows support log_type='pg_log' or 'operation_event'"
                    )
                if log_type == "pg_log" and filters:
                    raise ValueError("read_log.filters is supported only for operation_event")
                if log_type == "operation_event" and (start_line is not None or end_line is not None or match_key is not None):
                    raise ValueError(
                        "operation_event returns structured records and does not support line slicing or match_key"
                    )
                result = self._query_frozen_history_records(
                    source=source,
                    start_timestamp=start_timestamp,
                    end_timestamp=end_timestamp,
                    target=target,
                    filters=filters,
                    limit=min(history_limit, int(getattr(self._case.frozen_history, "max_history_records_per_response", 200))),
                )
                if log_type == "operation_event":
                    return json.dumps({"log_type": log_type, **result}, ensure_ascii=False, separators=(",", ":"), default=str)
                records = result["records"]
                content = "\n".join(f"{record['timestamp']} {record.get('message', '')}" for record in records)
                page = self._slice_log_output(content, lines, start_line, end_line, match_key)
                return json.dumps({
                    "status": "success",
                    "log_type": log_type,
                    "window": result["window"],
                    "coverage": result["coverage"],
                    "truncated": result["truncated"],
                    **page,
                }, ensure_ascii=False)
            if log_type == "operation_event":
                raise ValueError("operation_event requires start_timestamp and end_timestamp")
            controller = getattr(self, "_rpo_controller", None)
            if controller is not None:
                delegated = controller.read_log(log_type)
                if delegated is not None:
                    return delegated
            if log_type == "dmesg":
                result = subprocess.run(
                    ["dmesg"], capture_output=True, text=True, timeout=10
                )
                output = result.stdout.strip()
                page = self._slice_log_output(output, lines, start_line, end_line, match_key)
                if not page["content"]:
                    page["content"] = f"(no log entries matched match_key: {match_key})" if match_key else "(no kernel log entries available)"
                return json.dumps({"status": "success", "log_type": "dmesg", **page}, ensure_ascii=False)

            elif log_type == "docker_logs":
                result = subprocess.run(
                    ["docker", "logs", container_name],
                    capture_output=True, text=True, timeout=10
                )
                output = (result.stdout + result.stderr).strip()
                page = self._slice_log_output(output, lines, start_line, end_line, match_key)
                if not page["content"]:
                    page["content"] = f"(no log entries matched match_key: {match_key})" if match_key else "(no docker log entries)"
                return json.dumps({"status": "success", "log_type": "docker_logs", **page}, ensure_ascii=False)

            elif log_type == "pg_log":
                output = self._read_visible_pg_log()
                page = self._slice_log_output(output, lines, start_line, end_line, match_key)
                if not page["content"]:
                    page["content"] = f"(no log entries matched match_key: {match_key})" if match_key else "(no PostgreSQL log entries)"
                return json.dumps({"status": "success", "log_type": "pg_log", **page}, ensure_ascii=False)

            else:
                return json.dumps({"status": "error", "error": f"Unknown log_type: {log_type}. Supported: dmesg, docker_logs, pg_log, operation_event"})
        except subprocess.TimeoutExpired:
            return json.dumps({"status": "error", "error": f"Timeout reading {log_type} logs"})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

    def get_deployment(self) -> BaseDeployment:
        """获取部署器引用"""
        return self.deployment
