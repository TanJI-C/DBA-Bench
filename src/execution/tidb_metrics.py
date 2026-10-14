"""TiDB metric catalog and Prometheus adapter for the shared history core."""

from __future__ import annotations

import hashlib
import json
import math
import re
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlencode
from urllib.request import urlopen

from src.execution.deployments.tidb_support import lightning_job_id
from src.execution.history.metrics import (
    MetricDefinition,
    MetricFrame,
    MetricQuery,
    MetricService,
    format_utc_timestamp,
    metric_variant_sort_key,
    parse_utc_timestamp,
    render_metric_frame,
    validate_metric_frame,
)


# Prometheus and PD API snapshots can arrive a few scrape rounds late while a
# TiDB container is busy. Regridding is bounded so a missing sampler is still
# reported instead of being turned into an invented value.
_MAX_REGRID_AGE_INTERVALS = 60
# A workload query reaches INFORMATION_SCHEMA statements summary asynchronously;
# digest binding at capture start polls for the digests instead of failing on
# the first empty read. A COUNT(*) can likewise race the concurrent
# fault-install table rebuild (ER_NO_SUCH_TABLE) and is retried.
_PLAN_DIGEST_BIND_ATTEMPTS = 15
_PLAN_DIGEST_BIND_RETRY_SECONDS = 2.0
_STATISTICS_REBUILD_RETRY_ATTEMPTS = 5
_STATISTICS_REBUILD_RETRY_SECONDS = 2.0
# Under host load a range query can be served while the window's samples are
# still being scraped into Prometheus; an empty series polls briefly before
# being treated as fatal.
_PROMETHEUS_EMPTY_SERIES_POLLS = 5
_PROMETHEUS_EMPTY_SERIES_POLL_SECONDS = 2.0
PD_EMPTY_REGION_COUNT_QUERY = 'max(pd_regions_status{type="empty-region-count"})'
PD_SPLIT_RATE_QUERY = (
    '60 * sum(rate(pd_scheduler_event_count{name="new-operator",type="split-bucket-scheduler"}[30s]))'
)
PD_MERGE_RATE_QUERY = (
    '60 * sum(rate(pd_scheduler_event_count{name="new-operator",type="random-merge-scheduler"}[30s]))'
)


@dataclass(frozen=True, slots=True, kw_only=True)
class _TiDBMetricQueryDefinition:
    target_kind: str
    all_target_shape: str
    promql_templates: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class _PdMetricSnapshot:
    timestamp_ms: int
    region_inventory: tuple[float, ...]
    region_activity: tuple[float, ...]
    leader_distribution: Mapping[str, tuple[float, ...]]


def _definition(
    name: str,
    fields: tuple[str, ...],
    target_kind: str,
    all_target_shape: str,
    lookback_seconds: int,
    source_scrape_seconds: int,
    lower_bound: float | None,
    upper_bound: float | None,
    templates: tuple[tuple[str, str], ...],
) -> tuple[MetricDefinition, _TiDBMetricQueryDefinition]:
    return (
        MetricDefinition(
            name=name,
            value_fields=fields,
            lookback_seconds=lookback_seconds,
            source_step_seconds=source_scrape_seconds,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        ),
        _TiDBMetricQueryDefinition(
            target_kind=target_kind,
            all_target_shape=all_target_shape,
            promql_templates=templates,
        ),
    )


_TIDB_DEFINITION_PAIRS = {
    "cpu": _definition(
        "cpu", ("percent",), "deployment_node", "database_nodes", 10, 2, 0.0, None,
        # cpu percent is measured per single core, so containers with a multi-core
        # cgroup quota legitimately report values above 100.
        (("percent", "sum(rate(container_cpu_usage_seconds_total{selector}[10s]))"),),
    ),
    "memory": _definition(
        "memory", ("percent",), "deployment_node", "database_nodes", 0, 2, 0.0, 100.0,
        (("percent", "100 * sum(container_memory_working_set_bytes{selector}) / sum(container_spec_memory_limit_bytes{selector})"),),
    ),
    "disk_io": _definition(
        "disk_io", ("read_mb_per_second", "write_mb_per_second"), "deployment_node", "database_nodes", 10, 2, 0.0, None,
        (
            ("read_mb_per_second", "sum(rate(container_fs_reads_bytes_total{selector}[10s]))"),
            ("write_mb_per_second", "sum(rate(container_fs_writes_bytes_total{selector}[10s]))"),
        ),
    ),
    "disk_usage": _definition(
        "disk_usage", ("megabytes",), "deployment_node", "cluster", 0, 5, 0.0, None,
        (("megabytes", "sum(container_fs_usage_bytes{selector})"),),
    ),
    "network_io": _definition(
        "network_io", ("megabytes_per_second",), "deployment_node", "cluster", 10, 2, 0.0, None,
        (("megabytes_per_second", "sum(rate(container_network_receive_bytes_total{selector}[10s]) + rate(container_network_transmit_bytes_total{selector}[10s]))"),),
    ),
    "qps": _definition(
        "qps", ("queries_per_second",), "tidb_endpoint", "cluster", 10, 2, 0.0, None,
        (("queries_per_second", "sum(rate(tidb_server_query_total{selector}[10s]))"),),
    ),
    "query_latency": _definition(
        "query_latency", ("average_ms", "p95_ms", "p99_ms"), "tidb_endpoint", "cluster", 10, 2, 0.0, None,
        (
            ("average_ms", "sum(rate(tidb_server_handle_query_duration_seconds_sum{selector}[10s])) / sum(rate(tidb_server_handle_query_duration_seconds_count{selector}[10s]))"),
            ("p95_ms", "histogram_quantile(0.95, sum by (le) (rate(tidb_server_handle_query_duration_seconds_bucket{selector}[10s])))"),
            ("p99_ms", "histogram_quantile(0.99, sum by (le) (rate(tidb_server_handle_query_duration_seconds_bucket{selector}[10s])))"),
        ),
    ),
    "active_connections": _definition(
        "active_connections", ("connections",), "tidb_endpoint", "tidb_endpoints", 0, 2, 0.0, None,
        (("connections", "sum(tidb_server_connections{selector})"),),
    ),
    "pd_region_inventory": _definition(
        "pd_region_inventory",
        ("total_regions", "empty_regions", "zero_key_regions"),
        "pd_cluster",
        "cluster",
        0,
        2,
        0.0,
        None,
        (),
    ),
    "pd_region_activity": _definition(
        "pd_region_activity",
        ("splits_per_minute", "merges_per_minute", "operators_active"),
        "pd_cluster",
        "cluster",
        0,
        2,
        0.0,
        None,
        (),
    ),
    "pd_leader_distribution": _definition(
        "pd_leader_distribution",
        ("leader_count", "leader_score", "region_count"),
        "tikv_node",
        "tikv_nodes",
        0,
        2,
        0.0,
        None,
        (),
    ),
    "ticdc_progress": _definition(
        "ticdc_progress",
        ("checkpoint_lag_seconds", "resolved_lag_seconds"),
        "changefeed",
        "changefeed",
        30,
        2,
        0.0,
        None,
        (
            (
                "checkpoint_lag_seconds",
                "sum(rate(ticdc_owner_checkpoint_lag_histogram_sum{selector}[{rate_window}s])) / "
                "sum(rate(ticdc_owner_checkpoint_lag_histogram_count{selector}[{rate_window}s]))",
            ),
            (
                "resolved_lag_seconds",
                "sum(rate(ticdc_owner_resolved_ts_lag_histogram_sum{selector}[{rate_window}s])) / "
                "sum(rate(ticdc_owner_resolved_ts_lag_histogram_count{selector}[{rate_window}s]))",
            ),
        ),
    ),
    "ticdc_sink": _definition(
        "ticdc_sink",
        ("rows_per_second", "worker_flush_cycles_per_second", "flush_samples_per_second"),
        "changefeed",
        "changefeed",
        30,
        2,
        0.0,
        None,
        (
            (
                "rows_per_second",
                "sum(rate(ticdc_sink_table_sink_total_rows_count{selector}[{rate_window}s]))",
            ),
            (
                "worker_flush_cycles_per_second",
                "sum(rate(ticdc_sink_txn_worker_total_duration_count{selector}[{rate_window}s]))",
            ),
            (
                "flush_samples_per_second",
                "sum(rate(ticdc_sink_flush_lag_histogram_count{selector}[{rate_window}s]))",
            ),
        ),
    ),
    "resource_group_usage": _definition(
        "resource_group_usage",
        ("read_ru_per_second", "write_ru_per_second", "total_ru_per_second"),
        "resource_group",
        "explicit_resource_groups",
        10,
        2,
        0.0,
        None,
        (
            (
                "total_ru_per_second",
                "sum(rate(resource_manager_resource_unit_read_request_unit_sum{{{selector}}}[10s])) + "
                "sum(rate(resource_manager_resource_unit_write_request_unit_sum{{{selector}}}[10s]))",
            ),
        ),
    ),
    "resource_group_throttle": _definition(
        "resource_group_throttle",
        ("wait_p95_ms", "throttled_requests_per_second", "rejected_requests_per_second"),
        "resource_group",
        "explicit_resource_groups",
        10,
        2,
        0.0,
        None,
        (),
    ),
    "transaction_commit": _definition(
        "transaction_commit",
        ("commits_per_second", "aborts_per_second", "retries_per_second", "p95_ms"),
        "tidb_endpoint",
        "tidb_endpoints",
        10,
        2,
        0.0,
        None,
        (),
    ),
    "statistics_state": _definition(
        "statistics_state",
        ("physical_rows", "statistics_rows", "modify_count", "analyzed_age_seconds"),
        "sql_history",
        "tables",
        0,
        10,
        0.0,
        None,
        (),
    ),
    "plan_cardinality": _definition(
        "plan_cardinality",
        ("estimated_rows", "actual_rows", "scanned_rows"),
        "sql_history",
        "sql_digests",
        0,
        10,
        0.0,
        None,
        (),
    ),
    "lightning_progress": _definition(
        "lightning_progress",
        (
            "estimated_chunks",
            "pending_chunks",
            "running_chunks",
            "finished_chunks",
            "failed_chunks",
            "written_bytes",
            "imported_bytes",
            "progress_percent",
        ),
        "lightning_job",
        "lightning_job",
        0,
        2,
        0.0,
        None,
        (
            ("estimated_chunks", 'sum(lightning_chunks{{{selector}, state="estimated"}}) or vector(0)'),
            ("pending_chunks", 'sum(lightning_chunks{{{selector}, state="pending"}}) or vector(0)'),
            ("running_chunks", 'sum(lightning_chunks{{{selector}, state="running"}}) or vector(0)'),
            ("finished_chunks", 'sum(lightning_chunks{{{selector}, state="finished"}}) or vector(0)'),
            ("failed_chunks", 'sum(lightning_chunks{{{selector}, state="failed"}}) or vector(0)'),
            ("written_bytes", 'sum(lightning_bytes{{{selector}, state="written"}}) or vector(0)'),
            ("imported_bytes", 'sum(lightning_bytes{{{selector}, state="imported"}}) or vector(0)'),
            (
                "progress_percent",
                '100 * (sum(lightning_chunks{{{selector}, state="finished"}}) or vector(0)) / '
                'clamp_min((sum(lightning_chunks{{{selector}, state="estimated"}}) or vector(0)), 1)',
            ),
        ),
    ),
    "lightning_throughput": _definition(
        "lightning_throughput",
        ("read_mb_per_second", "deliver_mb_per_second", "ingest_mb_per_second"),
        "lightning_job",
        "lightning_job",
        10,
        2,
        0.0,
        None,
        (
            ("read_mb_per_second", "sum(rate(lightning_row_read_bytes_sum{{{selector}}}[10s])) / 1024^2 or vector(0)"),
            ("deliver_mb_per_second", "sum(rate(lightning_block_deliver_bytes_sum{{{selector}}}[10s])) / 1024^2 or vector(0)"),
            ("ingest_mb_per_second", 'sum(rate(lightning_bytes{{{selector}, state="imported"}}[10s])) / 1024^2 or vector(0)'),
        ),
    ),
    "lightning_workers": _definition(
        "lightning_workers",
        ("idle_region", "idle_io", "idle_closed_engine", "open_engines"),
        "lightning_job",
        "lightning_job",
        0,
        2,
        0.0,
        None,
        (
            ("idle_region", 'sum(lightning_idle_workers{{{selector}, name="region"}}) or vector(0)'),
            ("idle_io", 'sum(lightning_idle_workers{{{selector}, name="io"}}) or vector(0)'),
            ("idle_closed_engine", 'sum(lightning_idle_workers{{{selector}, name="closed-engine"}}) or vector(0)'),
            (
                "open_engines",
                'clamp_min((sum(lightning_importer_engine{{{selector}, type="open"}}) or vector(0)) - '
                '(sum(lightning_importer_engine{{{selector}, type="closed"}}) or vector(0)), 0)',
            ),
        ),
    ),
    "workload_profile": _definition(
        "workload_profile",
        ("ok_per_second", "error_per_second", "p95_ms"),
        "workload_profile",
        "frontend_profiles",
        0,
        2,
        0.0,
        None,
        (),
    ),
}


SQL_BACKED_METRICS = frozenset({"statistics_state", "plan_cardinality"})
CASE_ONLY_METRICS = frozenset({
    "transaction_commit",
    "statistics_state",
    "plan_cardinality",
    "resource_group_usage",
    "resource_group_throttle",
    "lightning_progress",
    "lightning_throughput",
    "lightning_workers",
    "workload_profile",
    "pd_region_inventory",
    "pd_region_activity",
    "pd_leader_distribution",
    "ticdc_progress",
    "ticdc_sink",
})
_SQL_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _sql_identifier(value: object, field: str) -> str:
    text = str(value)
    if not _SQL_IDENTIFIER.fullmatch(text):
        raise ValueError(
            f"TiDB SQL metric contract has an invalid identifier: field={field!r}, value={value!r}"
        )
    return text


class TiDBSQLMetricSampler:
    """Capture Case-scoped SQL facts on a private connection."""

    def __init__(self, *, run_id: str) -> None:
        self.run_id = run_id
        self._condition = threading.Condition()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._connection = None
        self._connection_factory: Callable[[str], object] | None = None
        self._contract: Mapping[str, object] | None = None
        self._metrics: tuple[str, ...] = ()
        self._step_seconds = 10
        self._samples: dict[str, dict[str, dict[str, dict[int, float]]]] = {}
        self._last_timestamp_ms: int | None = None
        self._failure: Exception | None = None
        self._digest_by_role: dict[str, str] = {}

    def configure(
        self,
        *,
        metrics: Sequence[str],
        step_seconds: int,
        contract: Mapping[str, object],
        connection_factory: Callable[[str], object],
    ) -> None:
        if self._thread is not None and self._thread.is_alive():
            raise RuntimeError(f"TiDB SQL metric sampler is already running: run_id={self.run_id!r}")
        if step_seconds <= 0:
            raise ValueError(
                f"TiDB SQL metric sampler step must be positive: run_id={self.run_id!r}, step_seconds={step_seconds}"
            )
        selected = tuple(
            dict.fromkeys(
                str(metric).casefold()
                for metric in metrics
                if str(metric).casefold() in SQL_BACKED_METRICS
            )
        )
        if not selected:
            raise ValueError(
                f"TiDB SQL metric sampler requires a SQL-backed metric: run_id={self.run_id!r}, metrics={tuple(metrics)!r}"
            )
        self._validate_contract(contract, selected)
        self._metrics = selected
        self._step_seconds = int(step_seconds)
        self._contract = MappingProxyType(dict(contract))
        self._connection_factory = connection_factory
        self._samples = {metric: {} for metric in selected}
        self._last_timestamp_ms = None
        self._failure = None
        self._digest_by_role = {}

    def start(self) -> None:
        if not self._metrics:
            raise RuntimeError(f"TiDB SQL metric sampler was not configured: run_id={self.run_id!r}")
        if self._thread is not None:
            raise RuntimeError(f"TiDB SQL metric sampler cannot be started twice: run_id={self.run_id!r}")
        if self._connection_factory is None:
            raise RuntimeError(f"TiDB SQL metric sampler has no connection factory: run_id={self.run_id!r}")
        self._connection = self._connection_factory("aiopsbench-metric-sampler")
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            name=f"tidb-sql-metric-sampler-{self.run_id}",
            daemon=True,
        )
        self._thread.start()

    def _sample_once(self) -> None:
        snapshot = self._read_snapshot(int(time.time() * 1000))
        with self._condition:
            self._store_snapshot(snapshot)
            self._condition.notify_all()

    def stop(self) -> None:
        thread = self._thread
        if thread is None:
            return
        self._stop.set()
        with self._condition:
            self._condition.notify_all()
        thread.join(timeout=40)
        if thread.is_alive():
            raise RuntimeError(f"TiDB SQL metric sampler did not stop: run_id={self.run_id!r}")
        if self._connection is not None:
            self._connection.close()
        self._connection = None
        self._thread = None

    def raise_if_failed(self) -> None:
        with self._condition:
            failure = self._failure
        if failure is not None:
            raise RuntimeError(
                f"TiDB SQL metric sampler failed: run_id={self.run_id!r}, error={failure}"
            ) from failure

    def query(self, query: MetricQuery) -> MetricFrame:
        if query.metric not in self._metrics:
            raise ValueError(
                f"TiDB SQL metric was not enabled for this Case: run_id={self.run_id!r}, "
                f"metric={query.metric!r}, enabled={self._metrics!r}"
            )
        self.raise_if_failed()
        start_ms = query.start_epoch_ms
        end_ms = query.end_epoch_ms
        if start_ms is None:
            timestamps = [
                timestamp
                for fields in self._samples[query.metric].values()
                for values in fields.values()
                for timestamp in values
            ]
            if not timestamps:
                raise RuntimeError(
                    f"TiDB SQL metric sampler has no stored samples: run_id={self.run_id!r}, metric={query.metric!r}"
                )
            start_ms, end_ms = min(timestamps), max(timestamps)
        if start_ms >= end_ms:
            raise ValueError(
                f"TiDB SQL metric query window must be positive: run_id={self.run_id!r}, metric={query.metric!r}, "
                f"start={start_ms}, end={end_ms}"
            )
        step = query.step_seconds or self._step_seconds
        if step <= 0 or step % self._step_seconds:
            raise ValueError(
                f"TiDB SQL metric query step must be a positive sampler-step multiple: run_id={self.run_id!r}, "
                f"metric={query.metric!r}, step={step}, sampler_step={self._step_seconds}"
            )
        self._wait_until(int(end_ms))
        return self._frame(query.metric, int(start_ms), int(end_ms), step)

    def _wait_until(self, end_ms: int) -> None:
        with self._condition:
            while self._last_timestamp_ms is None or self._last_timestamp_ms < end_ms:
                if self._failure is not None:
                    failure = self._failure
                    raise RuntimeError(
                        f"TiDB SQL metric sampler failed: run_id={self.run_id!r}, error={failure}"
                    ) from failure
                if self._stop.is_set():
                    raise RuntimeError(
                        f"TiDB SQL metric sampler stopped before requested end: run_id={self.run_id!r}, "
                        f"end_ms={end_ms}, last_timestamp_ms={self._last_timestamp_ms}"
                    )
                self._condition.wait(timeout=1.0)

    def _frame(self, metric: str, start_ms: int, end_ms: int, step: int) -> MetricFrame:
        expected = tuple(range(start_ms, end_ms + self._step_seconds * 1000, self._step_seconds * 1000))
        selected_series: dict[str, dict[str, tuple[float, ...]]] = {}
        selected_timestamps: dict[str, tuple[int, ...]] = {}
        with self._condition:
            channels = self._samples[metric]
            for target in sorted(channels):
                fields = channels[target]
                if any(timestamp not in values for values in fields.values() for timestamp in expected):
                    raise RuntimeError(
                        f"TiDB SQL metric sampler has incomplete coverage: run_id={self.run_id!r}, metric={metric!r}, "
                        f"target={target!r}, expected_start={start_ms}, expected_end={end_ms}"
                    )
                selected_timestamps[target] = expected
                selected_series[target] = {
                    field: tuple(values[timestamp] for timestamp in expected)
                    for field, values in fields.items()
                }
        if step != self._step_seconds:
            selected_timestamps = {
                target: tuple(
                    timestamp
                    for timestamp in timestamps
                    if (timestamp - start_ms) % (step * 1000) == 0
                )
                for target, timestamps in selected_timestamps.items()
            }
            selected_series = {
                target: {
                    field: tuple(
                        value
                        for index, value in enumerate(values)
                        if (expected[index] - start_ms) % (step * 1000) == 0
                    )
                    for field, values in fields.items()
                }
                for target, fields in selected_series.items()
            }
        frame = MetricFrame(
            metric=metric,
            query_target=None,
            step_seconds=step,
            series=selected_series,
            timestamps_ms=selected_timestamps,
        )
        validate_metric_frame(frame, TIDB_METRIC_CATALOG)
        return frame

    def _run(self) -> None:
        step_ms = self._step_seconds * 1000
        next_timestamp = ((int(time.time() * 1000) // step_ms) + 1) * step_ms
        try:
            while not self._stop.is_set():
                remaining = next_timestamp / 1000 - time.time()
                if remaining > 0:
                    self._stop.wait(remaining)
                    if self._stop.is_set():
                        break
                snapshot = self._read_snapshot(next_timestamp)
                with self._condition:
                    self._store_snapshot(next_timestamp, snapshot)
                    self._last_timestamp_ms = next_timestamp
                    self._condition.notify_all()
                next_timestamp += step_ms
        except Exception as exc:
            with self._condition:
                self._failure = exc
                self._condition.notify_all()

    def _read_snapshot(self, timestamp_ms: int) -> Mapping[str, Mapping[str, Mapping[str, float]]]:
        if self._connection is None or self._contract is None:
            raise RuntimeError(f"TiDB SQL metric sampler is not connected/configured: run_id={self.run_id!r}")
        snapshot: dict[str, Mapping[str, Mapping[str, float]]] = {}
        if "statistics_state" in self._metrics:
            snapshot["statistics_state"] = self._read_statistics(timestamp_ms)
        if "plan_cardinality" in self._metrics:
            snapshot["plan_cardinality"] = self._read_plans()
        return snapshot

    def _read_statistics(self, timestamp_ms: int) -> Mapping[str, Mapping[str, float]]:
        contract = self._contract
        assert contract is not None
        database = _sql_identifier(contract["database"], "database")
        tables = tuple(_sql_identifier(item, "tables[]") for item in contract["tables"])
        result: dict[str, Mapping[str, float]] = {}
        import pymysql
        with self._connection.cursor(pymysql.cursors.DictCursor) as cursor:
            for table in tables:
                result[table] = self._read_table_statistics(
                    cursor, pymysql, database, table, timestamp_ms,
                )
        return result

    def _read_table_statistics(
        self,
        cursor,
        pymysql,
        database: str,
        table: str,
        timestamp_ms: int,
    ) -> Mapping[str, float]:
        # The first COUNT(*) can race the concurrent fault-install table
        # rebuild (ER_NO_SUCH_TABLE); retry briefly before giving up.
        for attempt in range(_STATISTICS_REBUILD_RETRY_ATTEMPTS):
            try:
                cursor.execute(f"SELECT COUNT(*) AS physical_rows FROM `{database}`.`{table}`")
                physical = list(cursor.fetchall())
                break
            except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as error:
                if int(error.args[0]) != 1146 or attempt == _STATISTICS_REBUILD_RETRY_ATTEMPTS - 1:
                    raise
                time.sleep(_STATISTICS_REBUILD_RETRY_SECONDS)
        if len(physical) != 1:
            raise RuntimeError(
                f"TiDB statistics sampler count returned an invalid shape: run_id={self.run_id!r}, "
                f"table={table!r}, rows={physical!r}"
            )
        cursor.execute(f"SHOW STATS_META WHERE Db_name='{database}' AND Table_name='{table}'")
        rows = list(cursor.fetchall())
        if len(rows) != 1:
            raise RuntimeError(
                f"TiDB statistics sampler stats-meta returned an invalid shape: run_id={self.run_id!r}, "
                f"table={table!r}, rows={rows!r}"
            )
        row = rows[0]
        analyzed = row.get("Last_analyze_time")
        if analyzed is None:
            raise RuntimeError(
                f"TiDB statistics sampler observed a missing analyze timestamp: run_id={self.run_id!r}, "
                f"table={table!r}, row={row!r}"
            )
        parsed = analyzed if isinstance(analyzed, datetime) else datetime.fromisoformat(str(analyzed).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        analyzed_ms = int(parsed.astimezone(timezone.utc).timestamp() * 1000)
        return {
            "physical_rows": float(physical[0]["physical_rows"]),
            "statistics_rows": float(row["Row_count"]),
            "modify_count": float(row["Modify_count"]),
            "analyzed_age_seconds": max(0.0, (timestamp_ms - analyzed_ms) / 1000),
        }

    def _bind_plan_digests(self) -> None:
        missing = self._bind_plan_digests_once()
        if missing:
            role, tables = missing[0]
            raise RuntimeError(
                f"TiDB plan sampler has no digest candidate yet: run_id={self.run_id!r}, "
                f"role={role!r}, tables={tables!r}"
            )

    def _bind_plan_digests_once(self) -> list[tuple[str, tuple[str, ...]]]:
        """Run one digest bind sweep; commit nothing unless every role binds.

        Returns the roles whose digest had not reached the statements summary.
        """
        contract = self._contract
        assert contract is not None
        matchers = {
            str(role): tuple(str(item).casefold() for item in tables)
            for role, tables in contract["statement_matchers"].items()
        }
        import pymysql
        with self._connection.cursor(pymysql.cursors.DictCursor) as cursor:
            for sql in {str(query) for query in contract["plan_queries"].values()}:
                cursor.execute(sql)
                cursor.fetchall()
            cursor.execute(
                "SELECT DIGEST, DIGEST_TEXT FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY"
            )
            rows = list(cursor.fetchall())
        bound: dict[str, str] = {}
        missing: list[tuple[str, tuple[str, ...]]] = []
        for role, tables in matchers.items():
            candidates = tuple(
                row for row in rows
                if all(table in str(row["DIGEST_TEXT"]).casefold() for table in tables)
            )
            if len(candidates) > 1:
                raise RuntimeError(
                    f"TiDB plan sampler bound multiple digests: run_id={self.run_id!r}, role={role!r}, "
                    f"tables={tables!r}, candidates={candidates!r}"
                )
            if not candidates:
                missing.append((role, tables))
                continue
            bound[role] = str(candidates[0]["DIGEST"])
        if missing:
            return missing
        for role, digest in bound.items():
            previous = self._digest_by_role.get(role)
            if previous is not None and previous != digest:
                raise RuntimeError(
                    f"TiDB plan sampler digest binding changed: run_id={self.run_id!r}, role={role!r}, "
                    f"previous={previous!r}, current={digest!r}"
                )
            self._digest_by_role[role] = digest
        return []

    def _bind_plan_digests_for_start(self) -> None:
        """Eagerly bind digests at capture start; the workload's digests reach
        the statements summary asynchronously, so poll briefly for them."""
        missing: list[tuple[str, tuple[str, ...]]] = []
        for _ in range(_PLAN_DIGEST_BIND_ATTEMPTS):
            missing = self._bind_plan_digests_once()
            if not missing:
                return
            time.sleep(_PLAN_DIGEST_BIND_RETRY_SECONDS)
        role, tables = missing[0]
        raise RuntimeError(
            f"TiDB plan sampler has no digest candidate yet: run_id={self.run_id!r}, "
            f"role={role!r}, tables={tables!r}"
        )

    def _read_plans(self) -> Mapping[str, Mapping[str, float]]:
        contract = self._contract
        assert contract is not None
        if not self._digest_by_role:
            self._bind_plan_digests_for_start()
        result: dict[str, Mapping[str, float]] = {}
        for role, sql in {str(role): str(query) for role, query in contract["plan_queries"].items()}.items():
            if role not in self._digest_by_role:
                raise RuntimeError(
                    f"TiDB plan sampler has no digest binding: run_id={self.run_id!r}, role={role!r}"
                )
            with self._connection.cursor() as cursor:
                cursor.execute(f"EXPLAIN ANALYZE {sql}")
                rows = cursor.fetchall()
                columns = tuple(str(item[0]).casefold() for item in cursor.description or ())
            if "estrows" not in columns or "actrows" not in columns:
                raise RuntimeError(
                    f"TiDB plan sampler result lacks estRows/actRows: run_id={self.run_id!r}, role={role!r}, "
                    f"columns={columns!r}, rows={rows!r}"
                )
            candidates = []
            for row in rows:
                operator = str(row[0]).casefold()
                if "scan" not in operator:
                    continue
                estimate = float(row[columns.index("estrows")])
                actual = float(row[columns.index("actrows")])
                if estimate <= 0 or actual < 0:
                    raise RuntimeError(
                        f"TiDB plan sampler observed invalid cardinality: run_id={self.run_id!r}, role={role!r}, row={row!r}"
                    )
                candidates.append((estimate, actual))
            if not candidates:
                raise RuntimeError(
                    f"TiDB plan sampler found no scan nodes: run_id={self.run_id!r}, role={role!r}, rows={rows!r}"
                )
            estimated = sum(item[0] for item in candidates)
            actual = sum(item[1] for item in candidates)
            result[f"sql_digest/{self._digest_by_role[role]}"] = {
                "estimated_rows": estimated,
                "actual_rows": actual,
                "scanned_rows": actual,
            }
        return result

    def _store_snapshot(
        self,
        timestamp_ms: int,
        snapshot: Mapping[str, Mapping[str, Mapping[str, float]]],
    ) -> None:
        for metric in self._metrics:
            if metric not in snapshot:
                raise RuntimeError(
                    f"TiDB SQL metric sampler snapshot is missing a requested metric: run_id={self.run_id!r}, metric={metric!r}"
                )
            for target, fields in snapshot[metric].items():
                metric_targets = self._samples[metric].setdefault(str(target), {})
                for field, value in fields.items():
                    numeric = float(value)
                    if not math.isfinite(numeric) or numeric < 0:
                        raise ValueError(
                            f"TiDB SQL metric sampler produced an invalid value: run_id={self.run_id!r}, metric={metric!r}, "
                            f"target={target!r}, field={field!r}, value={value!r}"
                        )
                    metric_targets.setdefault(str(field), {})[timestamp_ms] = numeric
            if not self._samples[metric]:
                raise RuntimeError(
                    f"TiDB SQL metric sampler produced no series: run_id={self.run_id!r}, metric={metric!r}"
                )

    @staticmethod
    def _validate_contract(contract: Mapping[str, object], metrics: tuple[str, ...]) -> None:
        if not isinstance(contract, Mapping):
            raise TypeError(f"TiDB SQL metric contract must be a mapping: contract={contract!r}")
        required = {"database", "tables"}
        if "plan_cardinality" in metrics:
            required.update(("plan_queries", "statement_matchers"))
        missing = required - set(contract)
        if missing:
            raise ValueError(
                f"TiDB SQL metric contract is missing fields: missing={sorted(missing)!r}, contract={contract!r}"
            )
        if not contract["tables"]:
            raise ValueError(f"TiDB SQL metric contract has no tables: contract={contract!r}")
        if "plan_cardinality" in metrics and (
            not contract["plan_queries"] or not contract["statement_matchers"]
        ):
            raise ValueError(f"TiDB SQL metric contract has empty plan sections: contract={contract!r}")


class TiDBMetricCatalog:
    system = "tidb"

    def __init__(self) -> None:
        self._definitions = MappingProxyType({metric: pair[0] for metric, pair in _TIDB_DEFINITION_PAIRS.items()})
        self._queries = MappingProxyType({metric: pair[1] for metric, pair in _TIDB_DEFINITION_PAIRS.items()})

    @property
    def metric_names(self) -> frozenset[str]:
        return frozenset(self._definitions)

    def definition(self, metric: str) -> MetricDefinition:
        normalized = str(metric).casefold()
        try:
            return self._definitions[normalized]
        except KeyError as exc:
            raise ValueError(
                f"Unknown TiDB time-series metric: metric={metric!r}, expected={sorted(self.metric_names)!r}"
            ) from exc

    def target_variants(self, metric: str, deployment: object) -> tuple[str | None, ...]:
        definition = self.definition(metric)
        query_definition = self._queries[definition.name]
        if query_definition.target_kind == "sql_history":
            return (None,)
        if query_definition.target_kind == "deployment_node":
            return (None, *tuple(deployment.NODES))
        if query_definition.target_kind == "tidb_endpoint":
            return (None, *tuple(deployment.tidb_endpoints))
        if query_definition.target_kind == "tikv_node":
            return (
                None,
                *tuple(node for node in deployment.NODES if node.startswith("tikv/")),
            )
        if query_definition.target_kind == "changefeed":
            target = getattr(deployment, "metric_changefeed_target", None)
            if target is None:
                raise ValueError(
                    f"TiCDC metric target is unavailable before the Case is configured: metric={metric!r}"
                )
            return (target,)
        if query_definition.target_kind == "resource_group":
            raise ValueError(
                f"TiDB resource-group metric requires Case metric_targets: metric={metric!r}"
            )
        if query_definition.target_kind == "lightning_job":
            return (None, lightning_job_id(deployment.run_id))
        if query_definition.target_kind == "workload_profile":
            return (None,)
        raise AssertionError(
            f"Unsupported TiDB metric target kind: metric={metric!r}, kind={query_definition.target_kind!r}"
        )

    def validate_target(self, metric: str, target: str | None, deployment: object) -> None:
        definition = self.definition(metric)
        if target is None:
            return
        query_definition = self._queries[definition.name]
        if query_definition.target_kind == "sql_history":
            raise ValueError(
                f"SQL-backed TiDB metric does not accept a query target: metric={metric!r}, target={target!r}"
            )
        if (
            query_definition.target_kind == "deployment_node"
            and target not in deployment.NODES
            and not target.startswith("lightning/")
        ):
            raise ValueError(
                f"Invalid TiDB metric target: metric={metric!r}, target={target!r}, "
                f"expected deployment nodes={tuple(deployment.NODES)!r}"
            )
        if query_definition.target_kind == "tidb_endpoint" and target not in deployment.tidb_endpoints:
            raise ValueError(
                f"Invalid TiDB metric target: metric={metric!r}, target={target!r}, "
                f"expected TiDB endpoints={tuple(deployment.tidb_endpoints)!r}"
            )
        if query_definition.target_kind == "tikv_node" and target not in {
            node for node in deployment.NODES if node.startswith("tikv/")
        }:
            raise ValueError(
                f"Invalid TiKV metric target: metric={metric!r}, target={target!r}, "
                f"expected TiKV nodes={tuple(node for node in deployment.NODES if node.startswith('tikv/'))!r}"
            )
        if query_definition.target_kind == "changefeed":
            expected = getattr(deployment, "metric_changefeed_target", None)
            if target != expected:
                raise ValueError(
                    f"Invalid TiCDC metric target: metric={metric!r}, target={target!r}, expected={expected!r}"
                )
        if query_definition.target_kind == "resource_group":
            if not isinstance(target, str) or not target:
                raise ValueError(
                    f"TiDB resource-group metric target must be a non-empty resource-group name: "
                    f"metric={metric!r}, target={target!r}"
                )
        if query_definition.target_kind == "lightning_job":
            expected = lightning_job_id(deployment.run_id)
            if target != expected:
                raise ValueError(
                    f"Invalid Lightning metric target: metric={metric!r}, target={target!r}, expected={expected!r}"
                )
        if query_definition.target_kind == "workload_profile":
            raise ValueError(
                f"workload_profile accepts only target=None: metric={metric!r}, target={target!r}"
            )

    def promql(self, metric: str, field: str) -> str:
        definition = self.definition(metric)
        for template_field, query in self._queries[definition.name].promql_templates:
            if template_field == field:
                return query
        raise KeyError(f"Metric has no PromQL template: metric={metric!r}, field={field!r}")

    def fingerprint(self) -> str:
        payload = {
            "system": self.system,
            "metrics": [
                {
                    "name": definition.name,
                    "fields": definition.value_fields,
                    "lookback_seconds": definition.lookback_seconds,
                    "source_step_seconds": definition.source_step_seconds,
                    "lower_bound": definition.lower_bound,
                    "upper_bound": definition.upper_bound,
                    "target_kind": self._queries[definition.name].target_kind,
                    "all_target_shape": self._queries[definition.name].all_target_shape,
                    "promql": self._queries[definition.name].promql_templates,
                }
                for definition in self._definitions.values()
            ],
        }
        return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


TIDB_METRIC_CATALOG = TiDBMetricCatalog()


def _parse_prometheus_samples(
    result: Mapping[str, Any],
    *,
    run_id: str,
    query: str,
    nan_value: float | None = None,
) -> tuple[tuple[int, ...], tuple[float, ...]]:
    samples = result.get("values")
    if not isinstance(samples, list):
        raise TypeError(f"Prometheus range result has no values list: run_id={run_id!r}, query={query!r}, result={result!r}")
    timestamps: list[int] = []
    values: list[float] = []
    for sample in samples:
        if not isinstance(sample, (list, tuple)) or len(sample) != 2:
            raise ValueError(f"Prometheus sample must be [timestamp, value]: run_id={run_id!r}, query={query!r}, sample={sample!r}")
        timestamp_ms = int(round(float(sample[0]) * 1000))
        value = float(sample[1])
        if not math.isfinite(value):
            if nan_value is None:
                raise ValueError(
                    f"Prometheus sample is non-finite: run_id={run_id!r}, query={query!r}, sample={sample!r}"
                )
            value = nan_value
        timestamps.append(timestamp_ms)
        values.append(value)
    return tuple(timestamps), tuple(values)


class PdMetricSampler:
    """Capture raw PD and Prometheus state for one frozen-history Case."""

    def __init__(
        self,
        *,
        deployment: object,
        run_id: str,
        sample_interval_sec: int = 2,
        request_instant: Callable[[str], list[dict[str, Any]]] | None = None,
    ) -> None:
        if sample_interval_sec <= 0:
            raise ValueError(
                f"PD metric sampler interval must be positive: run_id={run_id!r}, "
                f"sample_interval_sec={sample_interval_sec}"
            )
        self.deployment = deployment
        self.run_id = run_id
        self.sample_interval_sec = int(sample_interval_sec)
        self._request_instant = request_instant or self._query_prometheus_instant
        self._condition = threading.Condition()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._snapshots: list[_PdMetricSnapshot] = []
        self._failure: BaseException | None = None

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError(f"PD metric sampler started twice: run_id={self.run_id!r}")
        self._stop.clear()
        self._sample_once()
        self._thread = threading.Thread(
            target=self._run,
            name=f"aiops-pd-metrics-{self.run_id}",
            daemon=True,
        )
        self._thread.start()

    def _sample_once(self) -> None:
        snapshot = self._read_snapshot(int(time.time() * 1000))
        with self._condition:
            self._store_snapshot(snapshot)
            self._condition.notify_all()

    def stop(self) -> None:
        thread = self._thread
        if thread is None:
            return
        self._stop.set()
        with self._condition:
            self._condition.notify_all()
        thread.join(timeout=max(5.0, self.sample_interval_sec * 3.0))
        if thread.is_alive():
            raise RuntimeError(f"PD metric sampler did not stop: run_id={self.run_id!r}")
        self._thread = None
        self._raise_failure()

    def _run(self) -> None:
        step_ms = self.sample_interval_sec * 1000
        next_timestamp = ((int(time.time() * 1000) // step_ms) + 1) * step_ms
        try:
            while not self._stop.is_set():
                remaining = next_timestamp / 1000 - time.time()
                if remaining > 0:
                    self._stop.wait(remaining)
                    if self._stop.is_set():
                        break
                snapshot = self._read_snapshot(next_timestamp)
                with self._condition:
                    self._store_snapshot(snapshot)
                    self._condition.notify_all()
                next_timestamp += step_ms
        except BaseException as exc:
            with self._condition:
                self._failure = exc
                self._condition.notify_all()
            self._stop.set()

    def _raise_failure(self) -> None:
        if self._failure is not None:
            raise RuntimeError(
                f"PD metric sampler failed: run_id={self.run_id!r}, failure={self._failure!r}"
            ) from self._failure

    def _read_snapshot(self, timestamp_ms: int) -> _PdMetricSnapshot:
        regions_payload = self.deployment.pd_request("GET", "/pd/api/v1/regions")
        stores_payload = self.deployment.pd_request("GET", "/pd/api/v1/stores")
        operators_payload = self.deployment.pd_request("GET", "/pd/api/v1/operators")
        regions = self._list_payload(regions_payload, "regions", "/pd/api/v1/regions")
        stores = self._list_payload(stores_payload, "stores", "/pd/api/v1/stores")
        operators = self._operator_list(operators_payload)
        total_regions, zero_key_regions = self._region_inventory(regions)
        empty_regions = self._prometheus_scalar(
            self._request_instant(PD_EMPTY_REGION_COUNT_QUERY),
            query=PD_EMPTY_REGION_COUNT_QUERY,
        )
        split_rate = self._prometheus_scalar(
            self._request_instant(PD_SPLIT_RATE_QUERY),
            query=PD_SPLIT_RATE_QUERY,
        )
        merge_rate = self._prometheus_scalar(
            self._request_instant(PD_MERGE_RATE_QUERY),
            query=PD_MERGE_RATE_QUERY,
        )
        return _PdMetricSnapshot(
            timestamp_ms=timestamp_ms,
            region_inventory=(total_regions, empty_regions, zero_key_regions),
            region_activity=(split_rate, merge_rate, float(len(operators))),
            leader_distribution=self._leader_distribution(stores),
        )

    def _store_snapshot(self, snapshot: _PdMetricSnapshot) -> None:
        if self._snapshots and self._snapshots[-1].timestamp_ms >= snapshot.timestamp_ms:
            if self._snapshots[-1].timestamp_ms == snapshot.timestamp_ms:
                self._snapshots[-1] = snapshot
                return
            raise RuntimeError(
                "PD metric sampler timestamps are not increasing: "
                f"run_id={self.run_id!r}, previous={self._snapshots[-1].timestamp_ms}, "
                f"current={snapshot.timestamp_ms}"
            )
        self._snapshots.append(snapshot)

    @staticmethod
    def _list_payload(payload: object, key: str, endpoint: str) -> list[dict[str, object]]:
        if not isinstance(payload, Mapping) or not isinstance(payload.get(key), list):
            raise TypeError(
                f"PD API response has no list payload: endpoint={endpoint!r}, payload={payload!r}"
            )
        return payload[key]

    @staticmethod
    def _operator_list(payload: object) -> list[object]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, Mapping) and isinstance(payload.get("operators"), list):
            return payload["operators"]
        raise TypeError(f"PD operators API response has no operator list: payload={payload!r}")

    @staticmethod
    def _region_inventory(regions: list[dict[str, object]]) -> tuple[float, float]:
        zero_key = 0
        for region in regions:
            keys = int(region["approximate_keys"])
            int(region["approximate_size"])
            if keys == 0:
                zero_key += 1
        return float(len(regions)), float(zero_key)

    @staticmethod
    def _prometheus_scalar(result: list[dict[str, Any]], *, query: str) -> float:
        if len(result) != 1:
            raise RuntimeError(
                "PD Prometheus instant query must return exactly one series: "
                f"query={query!r}, series={len(result)}"
            )
        item = result[0]
        if not isinstance(item, Mapping) or not isinstance(item.get("value"), (list, tuple)):
            raise TypeError(
                "PD Prometheus instant query returned an invalid scalar sample: "
                f"query={query!r}, item={item!r}"
            )
        sample = item["value"]
        if len(sample) != 2:
            raise ValueError(
                "PD Prometheus instant query sample must contain timestamp and value: "
                f"query={query!r}, sample={sample!r}"
            )
        value = float(sample[1])
        if not math.isfinite(value):
            raise ValueError(
                "PD Prometheus instant query returned a non-finite scalar: "
                f"query={query!r}, sample={sample!r}"
            )
        return value

    def _query_prometheus_instant(self, query: str) -> list[dict[str, Any]]:
        params = urlencode({"query": query})
        url = f"http://127.0.0.1:{self.deployment.prometheus_port}/api/v1/query?{params}"
        with urlopen(url, timeout=5) as response:
            payload = json.load(response)
        if payload.get("status") != "success":
            raise RuntimeError(
                "PD Prometheus instant query failed: "
                f"run_id={self.run_id!r}, query={query!r}, payload={payload!r}"
            )
        result = payload.get("data", {}).get("result")
        if not isinstance(result, list):
            raise TypeError(
                "PD Prometheus instant query result must be a list: "
                f"run_id={self.run_id!r}, query={query!r}, result={result!r}"
            )
        return result

    def _leader_distribution(self, stores: list[dict[str, object]]) -> Mapping[str, tuple[float, ...]]:
        result: dict[str, tuple[float, ...]] = {}
        node_by_address = {
            f"{service}:20160": node
            for node, service in self.deployment.NODES.items()
            if node.startswith("tikv/")
        }
        for item in stores:
            if not isinstance(item, Mapping):
                raise TypeError(f"PD store response row is not an object: item={item!r}")
            store = item["store"]
            status = item["status"]
            if not isinstance(store, Mapping) or not isinstance(status, Mapping):
                raise TypeError(f"PD store response has invalid store/status objects: item={item!r}")
            target = node_by_address.get(str(store["address"]))
            if target is not None:
                result[target] = (
                    float(status["leader_count"]),
                    float(status["leader_score"]),
                    float(status["region_count"]),
                )
        expected = set(node_by_address.values())
        if set(result) != expected:
            raise RuntimeError(
                "PD store response does not cover all TiKV targets: "
                f"run_id={self.run_id!r}, expected={sorted(expected)!r}, "
                f"actual={sorted(result)!r}, stores={stores!r}"
            )
        return result

    def _snapshots_for(self, start_ms: int, end_ms: int, step_seconds: int) -> tuple[_PdMetricSnapshot, ...]:
        if start_ms > end_ms:
            raise ValueError(
                f"PD metric capture window is reversed: run_id={self.run_id!r}, start_ms={start_ms}, end_ms={end_ms}"
            )
        expected = tuple(range(start_ms, end_ms + 1, step_seconds * 1000))
        with self._condition:
            while not self._stop.is_set() and (
                not self._snapshots or self._snapshots[-1].timestamp_ms < end_ms
            ):
                self._raise_failure()
                self._condition.wait(timeout=self.sample_interval_sec)
            self._raise_failure()
            snapshots = tuple(self._snapshots)
        selected: list[_PdMetricSnapshot] = []
        cursor = 0
        current: _PdMetricSnapshot | None = None
        max_age_ms = max(step_seconds, self.sample_interval_sec) * _MAX_REGRID_AGE_INTERVALS * 1000
        for timestamp_ms in expected:
            while cursor < len(snapshots) and snapshots[cursor].timestamp_ms <= timestamp_ms:
                current = snapshots[cursor]
                cursor += 1
            if current is None:
                raise RuntimeError(
                    "PD metric capture has incomplete sample coverage: "
                    f"run_id={self.run_id!r}, start_ms={start_ms}, end_ms={end_ms}, "
                    f"missing_timestamp={timestamp_ms}, sample_count={len(snapshots)}"
                )
            age_ms = timestamp_ms - current.timestamp_ms
            if age_ms > max_age_ms:
                raise RuntimeError(
                    "PD metric capture has stale sample coverage: "
                    f"run_id={self.run_id!r}, start_ms={start_ms}, end_ms={end_ms}, "
                    f"requested_timestamp_ms={timestamp_ms}, sample_timestamp_ms={current.timestamp_ms}, "
                    f"age_ms={age_ms}, max_age_ms={max_age_ms}"
                )
            selected.append(current)
        return tuple(selected)

    def frame(self, query: MetricQuery) -> MetricFrame:
        start_ms = query.start_epoch_ms
        end_ms = query.end_epoch_ms
        if start_ms is None:
            if self._snapshots:
                start_ms = end_ms = self._snapshots[-1].timestamp_ms
            else:
                raise RuntimeError(f"PD metric sampler has no samples: run_id={self.run_id!r}")
        step_seconds = query.step_seconds or self.sample_interval_sec
        if step_seconds <= 0 or step_seconds % self.sample_interval_sec:
            raise ValueError(
                "PD metric query step must be a positive sampler-step multiple: "
                f"run_id={self.run_id!r}, metric={query.metric!r}, step={step_seconds}, "
                f"sampler_step={self.sample_interval_sec}"
            )
        snapshots = self._snapshots_for(int(start_ms), int(end_ms), step_seconds)
        timestamps = tuple(range(int(start_ms), int(end_ms) + 1, step_seconds * 1000))
        if query.metric == "pd_region_inventory":
            return MetricFrame(
                metric=query.metric,
                query_target=query.target,
                step_seconds=step_seconds,
                series={"pd/cluster": {
                    field: tuple(snapshot.region_inventory[index] for snapshot in snapshots)
                    for index, field in enumerate(TIDB_METRIC_CATALOG.definition(query.metric).value_fields)
                }},
                timestamps_ms={"pd/cluster": timestamps},
            )
        if query.metric == "pd_region_activity":
            return MetricFrame(
                metric=query.metric,
                query_target=query.target,
                step_seconds=step_seconds,
                series={"pd/cluster": {
                    field: tuple(snapshot.region_activity[index] for snapshot in snapshots)
                    for index, field in enumerate(TIDB_METRIC_CATALOG.definition(query.metric).value_fields)
                }},
                timestamps_ms={"pd/cluster": timestamps},
            )
        if query.metric == "pd_leader_distribution":
            if not snapshots:
                raise RuntimeError(f"PD leader metric has no samples: run_id={self.run_id!r}")
            selected_targets = (
                (query.target,)
                if query.target not in (None, "pd/cluster")
                else tuple(sorted(snapshots[0].leader_distribution))
            )
            return MetricFrame(
                metric=query.metric,
                query_target=query.target,
                step_seconds=step_seconds,
                series={
                    target: {
                        field: tuple(snapshot.leader_distribution[target][index] for snapshot in snapshots)
                        for index, field in enumerate(TIDB_METRIC_CATALOG.definition(query.metric).value_fields)
                    }
                    for target in selected_targets
                },
                timestamps_ms={target: timestamps for target in selected_targets},
            )
        raise AssertionError(f"PD metric sampler cannot build metric frame: metric={query.metric!r}")

    def query(self, query: MetricQuery) -> MetricFrame:
        self._raise_failure()
        if query.metric not in {
            "pd_region_inventory",
            "pd_region_activity",
            "pd_leader_distribution",
        }:
            raise ValueError(
                f"PD metric sampler received an unsupported metric: run_id={self.run_id!r}, metric={query.metric!r}"
            )
        if query.end_epoch_ms is not None:
            with self._condition:
                while not self._stop.is_set() and (
                    not self._snapshots or self._snapshots[-1].timestamp_ms < query.end_epoch_ms
                ):
                    self._raise_failure()
                    self._condition.wait(timeout=self.sample_interval_sec)
        return self.frame(query)


class LivePrometheusMetricProvider:
    """Read canonical TiDB metrics from the current Prometheus instance."""

    def __init__(
        self,
        *,
        deployment: object,
        run_id: str,
        sample_interval_sec: int = 2,
        return_window_seconds: int = 60,
        request_range: Callable[[str, int, int, int], list[dict[str, Any]]] | None = None,
        catalog: TiDBMetricCatalog = TIDB_METRIC_CATALOG,
        sql_metric_provider: Callable[[MetricQuery], MetricFrame] | None = None,
        pd_metric_provider: Callable[[MetricQuery], MetricFrame] | None = None,
        workload_profile_provider: Callable[[MetricQuery], MetricFrame] | None = None,
    ) -> None:
        if sample_interval_sec <= 0 or return_window_seconds <= 0:
            raise ValueError(
                f"Live metric provider timing values must be positive: run_id={run_id!r}, "
                f"sample_interval_sec={sample_interval_sec}, return_window_seconds={return_window_seconds}"
            )
        self.deployment = deployment
        self.run_id = run_id
        self.sample_interval_sec = sample_interval_sec
        self.return_window_seconds = return_window_seconds
        self.catalog = catalog
        self._request_range = request_range or self._query_prometheus
        self._sql_metric_provider = sql_metric_provider
        self._pd_metric_provider = pd_metric_provider
        self._workload_profile_provider = workload_profile_provider

    def _query_prometheus(self, query: str, start_epoch_ms: int, end_epoch_ms: int, step_seconds: int) -> list[dict[str, Any]]:
        params = urlencode({
            "query": query,
            "start": start_epoch_ms / 1000,
            "end": end_epoch_ms / 1000,
            "step": step_seconds,
        })
        url = f"http://127.0.0.1:{self.deployment.prometheus_port}/api/v1/query_range?{params}"
        with urlopen(url, timeout=5) as response:
            payload = json.load(response)
        if payload.get("status") != "success":
            raise RuntimeError(
                f"Prometheus range query failed: run_id={self.run_id!r}, query={query!r}, "
                f"start_epoch_ms={start_epoch_ms}, end_epoch_ms={end_epoch_ms}, payload={payload!r}"
            )
        result = payload.get("data", {}).get("result")
        if not isinstance(result, list):
            raise TypeError(
                f"Prometheus range result must be a list: run_id={self.run_id!r}, query={query!r}, result={result!r}"
            )
        return result

    def _range(self, query: MetricQuery) -> tuple[int, int, int]:
        step_seconds = query.step_seconds or self.sample_interval_sec
        if step_seconds <= 0:
            raise ValueError(f"Metric query step must be positive: query={query!r}")
        if query.start_epoch_ms is None:
            end_epoch_ms = int(time.time() * 1000)
            start_epoch_ms = end_epoch_ms - self.return_window_seconds * 1000
        else:
            start_epoch_ms = query.start_epoch_ms
            end_epoch_ms = query.end_epoch_ms
        if start_epoch_ms > end_epoch_ms:
            raise ValueError(f"Live metric query window is reversed: query={query!r}")
        return start_epoch_ms, end_epoch_ms, step_seconds

    def _selector(self, target: str | None) -> str:
        labels = [f'container_label_com_docker_compose_project="{self.deployment.project_name}"']
        if target is not None:
            if target.startswith("lightning/"):
                service = "lightning"
            else:
                try:
                    service = self.deployment.NODES[target]
                except KeyError as exc:
                    raise ValueError(
                        f"Metric target is not a deployment node: run_id={self.run_id!r}, target={target!r}, "
                        f"nodes={tuple(self.deployment.NODES)!r}"
                    ) from exc
            labels.append(f'container_label_com_docker_compose_service="{service}"')
        return "{" + ",".join(labels) + "}"

    def _endpoint_selector(self, target: str | None) -> str:
        if target is None:
            return ""
        try:
            service = self.deployment.NODES[target]
        except KeyError as exc:
            raise ValueError(
                f"Metric target is not a TiDB endpoint: run_id={self.run_id!r}, target={target!r}, "
                f"endpoints={tuple(self.deployment.tidb_endpoints)!r}"
            ) from exc
        return f'{{instance="{service}:10080"}}'

    def _ticdc_selector(self, target: str | None) -> str:
        if target is None:
            raise ValueError(
                f"TiCDC metric query requires a changefeed target: run_id={self.run_id!r}"
            )
        expected = getattr(self.deployment, "metric_changefeed_target", None)
        if target != expected:
            raise ValueError(
                f"Invalid TiCDC metric target: run_id={self.run_id!r}, target={target!r}, expected={expected!r}"
            )
        prefix = "changefeed/"
        if not target.startswith(prefix):
            raise ValueError(
                f"TiCDC metric target must use changefeed/<id>: run_id={self.run_id!r}, target={target!r}"
            )
        changefeed_id = target[len(prefix):]
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", changefeed_id):
            raise ValueError(
                f"TiCDC metric target contains an invalid changefeed id: run_id={self.run_id!r}, "
                f"target={target!r}, changefeed_id={changefeed_id!r}"
            )
        return f'{{changefeed="{changefeed_id}",namespace="default"}}'

    def _one(
        self,
        query: str,
        start: int,
        end: int,
        step: int,
        *,
        nan_value: float | None = None,
    ) -> tuple[tuple[int, ...], tuple[float, ...]]:
        empty_series_polls = 0
        result = self._request_range(query, start, end, step)
        while not result and empty_series_polls < _PROMETHEUS_EMPTY_SERIES_POLLS:
            time.sleep(_PROMETHEUS_EMPTY_SERIES_POLL_SECONDS)
            empty_series_polls += 1
            result = self._request_range(query, start, end, step)
        if len(result) != 1:
            raise RuntimeError(
                f"Prometheus query must return one series: run_id={self.run_id!r}, query={query!r}, "
                f"series={len(result)}, empty_series_polls={empty_series_polls}"
            )
        return _parse_prometheus_samples(
            result[0], run_id=self.run_id, query=query, nan_value=nan_value
        )

    def _by_label(
        self,
        query: str,
        label: str,
        start: int,
        end: int,
        step: int,
        *,
        nan_value: float | None = None,
    ) -> dict[str, tuple[tuple[int, ...], tuple[float, ...]]]:
        result = self._request_range(query, start, end, step)
        series: dict[str, tuple[tuple[int, ...], tuple[float, ...]]] = {}
        for item in result:
            labels = item.get("metric", {})
            if label not in labels:
                raise KeyError(
                    f"Prometheus result lacks required label: run_id={self.run_id!r}, query={query!r}, "
                    f"label={label!r}, item={item!r}"
                )
            key = str(labels[label])
            if key in series:
                raise RuntimeError(
                    f"Prometheus query returned duplicate label series: run_id={self.run_id!r}, query={query!r}, "
                    f"label={label!r}, value={key!r}"
                )
            series[key] = _parse_prometheus_samples(
                item,
                run_id=self.run_id,
                query=query,
                nan_value=nan_value,
            )
        return series

    def _frame(self, metric: str, query_target: str | None, step: int, target: str, timestamps: tuple[int, ...], **fields: tuple[float, ...]) -> MetricFrame:
        frame = MetricFrame(
            metric=metric,
            query_target=query_target,
            step_seconds=step,
            series={target: fields},
            timestamps_ms={target: timestamps},
        )
        validate_metric_frame(frame, self.catalog)
        return frame

    def _resource_query(
        self,
        metric: str,
        target: str | None,
        start: int,
        end: int,
        step: int,
        rate_window_seconds: int | None,
    ) -> MetricFrame:
        selector = self._selector(target)
        definition = self.catalog.definition(metric)
        rate_window = rate_window_seconds or definition.lookback_seconds
        if rate_window <= 0 and metric not in {"memory", "disk_usage"}:
            raise ValueError(
                f"TiDB Prometheus rate window must be positive: run_id={self.run_id!r}, "
                f"metric={metric!r}, rate_window_seconds={rate_window}"
            )
        if metric == "cpu":
            if target is not None and target.startswith("lightning/"):
                query = (
                    "100 * sum(rate(container_cpu_usage_seconds_total{selector}[{window}s])) / "
                    "sum(container_spec_cpu_quota{selector} / container_spec_cpu_period{selector})"
                ).format(selector=selector, window=rate_window)
                timestamps, values = self._one(query, start, end, step)
                return self._frame(
                    metric,
                    target,
                    step,
                    target,
                    timestamps,
                    percent=tuple(round(min(value, 100.0), 2) for value in values),
                )
            query = f"sum(rate(container_cpu_usage_seconds_total{selector}[{rate_window}s]))" if target else (
                "sum by (container_label_com_docker_compose_service) "
                f"(rate(container_cpu_usage_seconds_total{selector}[{rate_window}s]))"
            )
            if target is not None:
                timestamps, cores = self._one(query, start, end, step)
                cpu_limit = self.deployment.node_cpu_limits[target]
                return self._frame(metric, target, step, target, timestamps, percent=tuple(round(value / cpu_limit * 100, 2) for value in cores))
            by_service = self._by_label(query, "container_label_com_docker_compose_service", start, end, step)
            service_to_target = {
                service: node
                for node, service in self.deployment.NODES.items()
                if node in self.deployment.database_nodes
            }
            missing = sorted(set(service_to_target) - set(by_service))
            if missing:
                raise RuntimeError(f"Prometheus CPU query is missing database services: run_id={self.run_id!r}, missing={missing!r}")
            series = {}
            timestamps_ms = {}
            for service, node in service_to_target.items():
                timestamps, cores = by_service[service]
                cpu_limit = self.deployment.node_cpu_limits[node]
                series[node] = {"percent": tuple(round(value / cpu_limit * 100, 2) for value in cores)}
                timestamps_ms[node] = timestamps
            frame = MetricFrame(metric=metric, query_target=None, step_seconds=step, series=series, timestamps_ms=timestamps_ms)
            validate_metric_frame(frame, self.catalog)
            return frame

        if metric == "memory":
            group = "" if target else " by (container_label_com_docker_compose_service)"
            query = (
                "100 * sum" + group + f"(container_memory_working_set_bytes{selector}) / "
                "sum" + group + f"(container_spec_memory_limit_bytes{selector})"
            )
            if target is not None:
                timestamps, values = self._one(query, start, end, step)
                return self._frame(metric, target, step, target, timestamps, percent=tuple(round(value, 2) for value in values))
            by_service = self._by_label(query, "container_label_com_docker_compose_service", start, end, step)
            service_to_target = {service: node for node, service in self.deployment.NODES.items() if node in self.deployment.database_nodes}
            missing = sorted(set(service_to_target) - set(by_service))
            if missing:
                raise RuntimeError(f"Prometheus memory query is missing database services: run_id={self.run_id!r}, missing={missing!r}")
            series = {}
            timestamps_ms = {}
            for service, node in service_to_target.items():
                timestamps, values = by_service[service]
                series[node] = {"percent": tuple(round(value, 2) for value in values)}
                timestamps_ms[node] = timestamps
            frame = MetricFrame(metric=metric, query_target=None, step_seconds=step, series=series, timestamps_ms=timestamps_ms)
            validate_metric_frame(frame, self.catalog)
            return frame

        if metric == "disk_io":
            group = "" if target else " by (container_label_com_docker_compose_service)"
            queries = {
                "read_mb_per_second": f"sum{group}(rate(container_fs_reads_bytes_total{selector}[{rate_window}s]))",
                "write_mb_per_second": f"sum{group}(rate(container_fs_writes_bytes_total{selector}[{rate_window}s]))",
            }
            if target is not None:
                read_ts, reads = self._one(queries["read_mb_per_second"], start, end, step)
                write_ts, writes = self._one(queries["write_mb_per_second"], start, end, step)
                if read_ts != write_ts:
                    raise RuntimeError(f"Prometheus disk_io timestamps differ: run_id={self.run_id!r}, target={target!r}")
                return self._frame(
                    metric, target, step, target, read_ts,
                    read_mb_per_second=tuple(round(value / 1024**2, 3) for value in reads),
                    write_mb_per_second=tuple(round(value / 1024**2, 3) for value in writes),
                )
            read_by_service = self._by_label(queries["read_mb_per_second"], "container_label_com_docker_compose_service", start, end, step)
            write_by_service = self._by_label(queries["write_mb_per_second"], "container_label_com_docker_compose_service", start, end, step)
            service_to_target = {service: node for node, service in self.deployment.NODES.items() if node in self.deployment.database_nodes}
            missing_read = sorted(set(service_to_target) - set(read_by_service))
            missing_write = sorted(set(service_to_target) - set(write_by_service))
            missing = {"read": missing_read, "write": missing_write}
            if any(missing.values()):
                raise RuntimeError(f"Prometheus disk_io query is missing database services: run_id={self.run_id!r}, missing={missing!r}")
            series = {}
            timestamps_ms = {}
            for service, node in service_to_target.items():
                read_ts, reads = read_by_service[service]
                write_ts, writes = write_by_service[service]
                if read_ts != write_ts:
                    raise RuntimeError(f"Prometheus disk_io timestamps differ: run_id={self.run_id!r}, target={node!r}")
                series[node] = {
                    "read_mb_per_second": tuple(round(value / 1024**2, 3) for value in reads),
                    "write_mb_per_second": tuple(round(value / 1024**2, 3) for value in writes),
                }
                timestamps_ms[node] = read_ts
            frame = MetricFrame(metric=metric, query_target=None, step_seconds=step, series=series, timestamps_ms=timestamps_ms)
            validate_metric_frame(frame, self.catalog)
            return frame

        query = self.catalog.promql(metric, definition.value_fields[0]).format(selector=selector)
        query = query.replace("[10s]", f"[{rate_window}s]")
        timestamps, values = self._one(query, start, end, step)
        field = definition.value_fields[0]
        unit_values = tuple(round(value / 1024**2, 3) for value in values)
        return self._frame(metric, target, step, target or "cluster", timestamps, **{field: unit_values})

    def _qps(
        self,
        target: str | None,
        start: int,
        end: int,
        step: int,
        rate_window_seconds: int | None,
    ) -> MetricFrame:
        selector = self._endpoint_selector(target)
        rate_window = rate_window_seconds or self.catalog.definition("qps").lookback_seconds
        if rate_window <= 0:
            raise ValueError(
                f"TiDB Prometheus rate window must be positive: run_id={self.run_id!r}, "
                f"metric='qps', rate_window_seconds={rate_window}"
            )
        query = f"sum(rate(tidb_server_query_total{selector}[{rate_window}s]))"
        timestamps, values = self._one(query, start, end, step)
        return self._frame("qps", target, step, target or "cluster", timestamps, queries_per_second=values)

    def _latency(
        self,
        target: str | None,
        start: int,
        end: int,
        step: int,
        rate_window_seconds: int | None,
    ) -> MetricFrame:
        selector = self._endpoint_selector(target)
        rate_window = rate_window_seconds or self.catalog.definition("query_latency").lookback_seconds
        if rate_window <= 0:
            raise ValueError(
                f"TiDB Prometheus rate window must be positive: run_id={self.run_id!r}, "
                f"metric='query_latency', rate_window_seconds={rate_window}"
            )
        queries = {
            "average_ms": f"sum(rate(tidb_server_handle_query_duration_seconds_sum{{selector}}[{rate_window}s])) / sum(rate(tidb_server_handle_query_duration_seconds_count{{selector}}[{rate_window}s]))",
            "p95_ms": f"histogram_quantile(0.95, sum by (le) (rate(tidb_server_handle_query_duration_seconds_bucket{{selector}}[{rate_window}s])))",
            "p99_ms": f"histogram_quantile(0.99, sum by (le) (rate(tidb_server_handle_query_duration_seconds_bucket{{selector}}[{rate_window}s])))",
        }
        samples = {field: self._one(query.format(selector=selector), start, end, step) for field, query in queries.items()}
        timestamps = samples["average_ms"][0]
        if any(item[0] != timestamps for item in samples.values()):
            raise RuntimeError(f"Prometheus query_latency timestamps differ: run_id={self.run_id!r}, target={target!r}")
        return self._frame(
            "query_latency", target, step, target or "cluster", timestamps,
            average_ms=tuple(round(value * 1000, 3) for value in samples["average_ms"][1]),
            p95_ms=tuple(round(value * 1000, 3) for value in samples["p95_ms"][1]),
            p99_ms=tuple(round(value * 1000, 3) for value in samples["p99_ms"][1]),
        )

    def _ticdc(
        self,
        metric: str,
        target: str,
        start: int,
        end: int,
        step: int,
        rate_window_seconds: int | None,
    ) -> MetricFrame:
        selector = self._ticdc_selector(target)
        definition = self.catalog.definition(metric)
        rate_window = rate_window_seconds or definition.lookback_seconds
        if rate_window <= 0:
            raise ValueError(
                f"TiCDC metric rate window must be positive: run_id={self.run_id!r}, "
                f"metric={metric!r}, rate_window_seconds={rate_window}"
            )
        samples = {
            field: self._one(
                self.catalog.promql(metric, field).format(
                    selector=selector,
                    rate_window=rate_window,
                ),
                start,
                end,
                step,
            )
            for field in definition.value_fields
        }
        timestamps = samples[definition.value_fields[0]][0]
        if any(item[0] != timestamps for item in samples.values()):
            raise RuntimeError(
                f"Prometheus {metric} timestamps differ: run_id={self.run_id!r}, target={target!r}"
            )
        return self._frame(
            metric,
            target,
            step,
            target,
            timestamps,
            **{
                field: tuple(round(value, 6) for value in samples[field][1])
                for field in definition.value_fields
            },
        )

    def _active_connections(self, target: str | None, start: int, end: int, step: int) -> MetricFrame:
        selector = self._endpoint_selector(target)
        query = f"sum{' by (instance)' if target is None else ''}(tidb_server_connections{selector})"
        if target is not None:
            timestamps, values = self._one(query, start, end, step)
            return self._frame("active_connections", target, step, target, timestamps, connections=values)
        by_instance = self._by_label(query, "instance", start, end, step)
        instance_to_target = {
            f"{self.deployment.NODES[target_name]}:10080": target_name
            for target_name in self.deployment.tidb_endpoints
        }
        missing = sorted(set(instance_to_target) - set(by_instance))
        if missing:
            raise RuntimeError(f"Prometheus active_connections query is missing endpoints: run_id={self.run_id!r}, missing={missing!r}")
        series = {}
        timestamps_ms = {}
        for instance, endpoint in instance_to_target.items():
            timestamps, values = by_instance[instance]
            series[endpoint] = {"connections": values}
            timestamps_ms[endpoint] = timestamps
        frame = MetricFrame(metric="active_connections", query_target=None, step_seconds=step, series=series, timestamps_ms=timestamps_ms)
        validate_metric_frame(frame, self.catalog)
        return frame

    def _transaction_selector(self, target: str | None, labels: tuple[str, ...] = ()) -> str:
        selected = list(labels)
        if target is not None:
            service = self.deployment.NODES[target]
            selected.append(f'instance="{service}:10080"')
        return "{" + ",".join(selected) + "}" if selected else ""

    def _transaction_commit(
        self,
        target: str | None,
        start: int,
        end: int,
        step: int,
        rate_window_seconds: int | None,
    ) -> MetricFrame:
        rate_window = rate_window_seconds or self.catalog.definition("transaction_commit").lookback_seconds
        if rate_window <= 0:
            raise ValueError(
                f"TiDB transaction rate window must be positive: run_id={self.run_id!r}, "
                f"rate_window_seconds={rate_window}"
            )
        queries = {
            "commits_per_second": (
                "sum by (instance) (rate(tidb_tikvclient_commit_txn_counter%s[%ss]))"
                % (self._transaction_selector(target, ('type="ok"',)), rate_window)
            ),
            "aborts_per_second": (
                "sum by (instance) (rate(tidb_tikvclient_commit_txn_counter%s[%ss]))"
                % (self._transaction_selector(target, ('type="err"',)), rate_window)
            ),
            "retries_per_second": (
                "sum by (instance) (rate(tidb_session_retry_num_sum%s[%ss]))"
                % (self._transaction_selector(target, ('scope="general"',)), rate_window)
            ),
            "p95_ms": (
                "histogram_quantile(0.95, sum by (instance, le) "
                "(rate(tidb_tikvclient_txn_cmd_duration_seconds_bucket%s[%ss])))"
                % (self._transaction_selector(target, ('scope="general"', 'type="commit"')), rate_window)
            ),
        }
        if target is not None:
            samples = {
                field: self._one(
                    query,
                    start,
                    end,
                    step,
                    nan_value=0.0 if field == "p95_ms" else None,
                )
                for field, query in queries.items()
            }
            timestamps = samples["commits_per_second"][0]
            if any(sample[0] != timestamps for sample in samples.values()):
                raise RuntimeError(
                    f"TiDB transaction_commit timestamps differ: run_id={self.run_id!r}, target={target!r}"
                )
            return self._frame(
                "transaction_commit",
                target,
                step,
                target,
                timestamps,
                commits_per_second=samples["commits_per_second"][1],
                aborts_per_second=samples["aborts_per_second"][1],
                retries_per_second=samples["retries_per_second"][1],
                p95_ms=tuple(round(value * 1000, 6) for value in samples["p95_ms"][1]),
            )
        by_field = {
            field: self._by_label(
                query,
                "instance",
                start,
                end,
                step,
                nan_value=0.0 if field == "p95_ms" else None,
            )
            for field, query in queries.items()
        }
        expected_instances = {
            f"{self.deployment.NODES[endpoint]}:10080": endpoint
            for endpoint in self.deployment.tidb_endpoints
        }
        missing = {
            field: sorted(set(expected_instances) - set(values))
            for field, values in by_field.items()
        }
        if any(missing.values()):
            raise RuntimeError(
                f"TiDB transaction_commit query is missing endpoints: run_id={self.run_id!r}, missing={missing!r}"
            )
        series = {}
        timestamps_ms = {}
        for instance, endpoint in expected_instances.items():
            samples = {field: values[instance] for field, values in by_field.items()}
            timestamps = samples["commits_per_second"][0]
            if any(sample[0] != timestamps for sample in samples.values()):
                raise RuntimeError(
                    f"TiDB transaction_commit timestamps differ: run_id={self.run_id!r}, endpoint={endpoint!r}"
                )
            series[endpoint] = {
                "commits_per_second": samples["commits_per_second"][1],
                "aborts_per_second": samples["aborts_per_second"][1],
                "retries_per_second": samples["retries_per_second"][1],
                "p95_ms": tuple(round(value * 1000, 6) for value in samples["p95_ms"][1]),
            }
            timestamps_ms[endpoint] = timestamps
        frame = MetricFrame(
            metric="transaction_commit",
            query_target=None,
            step_seconds=step,
            series=series,
            timestamps_ms=timestamps_ms,
        )
        validate_metric_frame(frame, self.catalog)
        return frame

    def _lightning_selector(self, target: str | None) -> str:
        expected = lightning_job_id(self.deployment.run_id)
        if target is not None and target != expected:
            raise ValueError(
                f"Lightning Prometheus target does not match deployment run: run_id={self.run_id!r}, "
                f"target={target!r}, expected={expected!r}"
            )
        return 'job="lightning"'

    def _lightning_query(
        self,
        metric: str,
        target: str | None,
        start: int,
        end: int,
        step: int,
        rate_window_seconds: int | None,
    ) -> MetricFrame:
        selector = self._lightning_selector(target)
        rate_window = rate_window_seconds or self.catalog.definition(metric).lookback_seconds
        if rate_window <= 0 and metric not in {"lightning_progress", "lightning_workers"}:
            raise ValueError(
                f"TiDB Lightning rate window must be positive: run_id={self.run_id!r}, "
                f"metric={metric!r}, rate_window_seconds={rate_window}"
            )
        fields = {}
        timestamps = None
        for field in self.catalog.definition(metric).value_fields:
            query = self.catalog.promql(metric, field).format(selector=selector)
            query = query.replace("[10s]", f"[{rate_window}s]")
            field_timestamps, values = self._one(query, start, end, step)
            if timestamps is None:
                timestamps = field_timestamps
            elif field_timestamps != timestamps:
                raise RuntimeError(
                    f"Lightning metric timestamps differ: run_id={self.run_id!r}, metric={metric!r}, field={field!r}"
                )
            fields[field] = tuple(round(value, 3) for value in values)
        if timestamps is None:
            raise RuntimeError(f"Lightning metric has no fields: run_id={self.run_id!r}, metric={metric!r}")
        series_target = target or lightning_job_id(self.deployment.run_id)
        return self._frame(metric, target, step, series_target, timestamps, **fields)

    @staticmethod
    def _resource_group_selector(target: str) -> str:
        escaped = target.replace("\\", "\\\\").replace('"', '\\"')
        return f'{{resource_group="{escaped}"}}'

    def _resource_group_query(
        self,
        metric: str,
        target: str | None,
        start: int,
        end: int,
        step: int,
        rate_window_seconds: int | None,
    ) -> MetricFrame:
        if target is None:
            raise ValueError(
                f"TiDB {metric} requires an explicit resource-group target; "
                f"querying all resource groups is disabled"
            )
        rate_window = rate_window_seconds or self.catalog.definition(metric).lookback_seconds
        if rate_window <= 0:
            raise ValueError(
                f"TiDB Prometheus rate window must be positive: run_id={self.run_id!r}, "
                f"metric={metric!r}, rate_window_seconds={rate_window}"
            )
        selector = self._resource_group_selector(target)
        if metric == "resource_group_usage":
            queries = {
                "read_ru_per_second": (
                    f"sum(rate(resource_manager_resource_unit_read_request_unit_sum{selector}[{rate_window}s]))"
                ),
                "write_ru_per_second": (
                    f"sum(rate(resource_manager_resource_unit_write_request_unit_sum{selector}[{rate_window}s]))"
                ),
            }
        else:
            queries = {
                "wait_p95_ms": (
                    f"(histogram_quantile(0.95, sum by (le) (rate(resource_manager_client_request_success_bucket"
                    f"{selector}[{rate_window}s]))) * 1000 "
                    f"and (sum(rate(resource_manager_client_request_success_count{selector}[{rate_window}s])) > 0)) "
                    f"or (0 * sum(rate(resource_manager_client_request_success_count{selector}[{rate_window}s])))"
                ),
                "throttled_requests_per_second": (
                    f"rate(resource_manager_client_request_limit_reserve_time_failed_count{selector}[{rate_window}s])"
                ),
                "rejected_requests_per_second": (
                    f"rate(resource_manager_client_request_fail{selector}[{rate_window}s])"
                ),
            }
        samples = {
            field: self._one(query, start, end, step, nan_value=0.0 if field == "wait_p95_ms" else None)
            for field, query in queries.items()
        }
        timestamps = next(iter(samples.values()))[0]
        if any(sample[0] != timestamps for sample in samples.values()):
            raise RuntimeError(
                f"Prometheus {metric} timestamps differ: run_id={self.run_id!r}, target={target!r}"
            )
        fields = {
            field: tuple(round(value, 6) for value in sample[1])
            for field, sample in samples.items()
        }
        if metric == "resource_group_usage":
            fields["total_ru_per_second"] = tuple(
                round(read + write, 6)
                for read, write in zip(
                    fields["read_ru_per_second"],
                    fields["write_ru_per_second"],
                    strict=True,
                )
            )
        return self._frame(metric, target, step, target, timestamps, **fields)

    def query(self, query: MetricQuery) -> MetricFrame:
        start, end, step = self._range(query)
        self.catalog.definition(query.metric)
        self.catalog.validate_target(query.metric, query.target, self.deployment)
        if query.metric in {"cpu", "memory", "disk_io", "disk_usage", "network_io"}:
            return self._resource_query(
                query.metric,
                query.target,
                start,
                end,
                step,
                query.rate_window_seconds,
            )
        if query.metric == "qps":
            return self._qps(query.target, start, end, step, query.rate_window_seconds)
        if query.metric == "query_latency":
            return self._latency(query.target, start, end, step, query.rate_window_seconds)
        if query.metric in {"ticdc_progress", "ticdc_sink"}:
            return self._ticdc(
                query.metric,
                query.target,
                start,
                end,
                step,
                query.rate_window_seconds,
            )
        if query.metric == "active_connections":
            return self._active_connections(query.target, start, end, step)
        if query.metric in {
            "pd_region_inventory",
            "pd_region_activity",
            "pd_leader_distribution",
        }:
            if self._pd_metric_provider is None:
                raise RuntimeError(
                    f"TiDB PD metric requires a Case sampler: run_id={self.run_id!r}, metric={query.metric!r}"
                )
            return self._pd_metric_provider(query)
        if query.metric == "transaction_commit":
            return self._transaction_commit(
                query.target,
                start,
                end,
                step,
                query.rate_window_seconds,
            )
        if query.metric in SQL_BACKED_METRICS:
            if self._sql_metric_provider is None:
                raise RuntimeError(
                    f"TiDB SQL-backed metric requires a Case sampler: run_id={self.run_id!r}, metric={query.metric!r}"
                )
            return self._sql_metric_provider(query)
        if query.metric in {"lightning_progress", "lightning_throughput", "lightning_workers"}:
            return self._lightning_query(
                query.metric,
                query.target,
                start,
                end,
                step,
                query.rate_window_seconds,
            )
        if query.metric == "workload_profile":
            if self._workload_profile_provider is None:
                raise RuntimeError(
                    f"workload_profile requires the Case WorkloadRunner: run_id={self.run_id!r}"
                )
            return self._workload_profile_provider(query)
        if query.metric in {"resource_group_usage", "resource_group_throttle"}:
            return self._resource_group_query(
                query.metric,
                query.target,
                start,
                end,
                step,
                query.rate_window_seconds,
            )
        raise AssertionError(f"Unreachable metric provider branch: query={query!r}")

    def capture(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
        target_selection: Mapping[str, tuple[str | None, ...]] | None = None,
        rate_windows: Mapping[str, int] | None = None,
    ) -> tuple[MetricFrame, ...]:
        if start_epoch_ms >= end_epoch_ms:
            raise ValueError(
                f"Metric capture window must have positive duration: run_id={self.run_id!r}, "
                f"start_epoch_ms={start_epoch_ms}, end_epoch_ms={end_epoch_ms}"
            )
        if step_seconds <= 0:
            raise ValueError(f"Metric capture step must be positive: run_id={self.run_id!r}, step_seconds={step_seconds}")
        if (end_epoch_ms - start_epoch_ms) % (step_seconds * 1000):
            raise ValueError(
                "Metric capture window must align to the requested step: "
                f"run_id={self.run_id!r}, start_epoch_ms={start_epoch_ms}, end_epoch_ms={end_epoch_ms}, step_seconds={step_seconds}"
            )
        if len(set(metrics)) != len(metrics):
            raise ValueError(f"Metric capture has duplicate metrics: run_id={self.run_id!r}, metrics={metrics!r}")
        normalized_metrics = {str(metric).casefold() for metric in metrics}
        for option_name, options in (("target_selection", target_selection), ("rate_windows", rate_windows)):
            if options is not None:
                unknown = set(options) - normalized_metrics
                if unknown:
                    raise ValueError(
                        f"TiDB metric capture {option_name} contains unrequested metrics: "
                        f"run_id={self.run_id!r}, unknown={sorted(unknown)!r}, metrics={tuple(metrics)!r}"
                    )
        expected_timestamps = tuple(range(start_epoch_ms, end_epoch_ms + 1, step_seconds * 1000))
        frames: list[MetricFrame] = []
        for metric in metrics:
            normalized_metric = str(metric).casefold()
            self.catalog.definition(normalized_metric)
            targets = (
                tuple(target_selection[normalized_metric])
                if target_selection is not None and normalized_metric in target_selection
                else self.catalog.target_variants(normalized_metric, self.deployment)
            )
            if not targets or len(set(targets)) != len(targets):
                raise ValueError(
                    "TiDB metric capture target selection must contain unique targets: "
                    f"run_id={self.run_id!r}, metric={normalized_metric!r}, targets={targets!r}"
                )
            rate_window = rate_windows.get(normalized_metric) if rate_windows is not None else None
            for target in targets:
                self.catalog.validate_target(normalized_metric, target, self.deployment)
                frame = self.query(MetricQuery(
                    metric=normalized_metric,
                    target=target,
                    start_epoch_ms=start_epoch_ms,
                    end_epoch_ms=end_epoch_ms,
                    step_seconds=step_seconds,
                    rate_window_seconds=rate_window,
                ))
                actual_timestamps = {
                    series_target: timestamps
                    for series_target, timestamps in frame.timestamps_ms.items()
                }
                if any(timestamps != expected_timestamps for timestamps in actual_timestamps.values()):
                    raise RuntimeError(
                        "TiDB metric capture has missing, shifted, or extra Prometheus samples: "
                        f"run_id={self.run_id!r}, metric={metric!r}, target={target!r}, "
                        f"expected_timestamps={expected_timestamps!r}, actual_timestamps={actual_timestamps!r}"
                    )
                frames.append(frame)
        return tuple(frames)


__all__ = [
    "CASE_ONLY_METRICS",
    "LivePrometheusMetricProvider",
    "PD_EMPTY_REGION_COUNT_QUERY",
    "PD_MERGE_RATE_QUERY",
    "PD_SPLIT_RATE_QUERY",
    "PdMetricSampler",
    "SQL_BACKED_METRICS",
    "TiDBMetricCatalog",
    "TIDB_METRIC_CATALOG",
]
