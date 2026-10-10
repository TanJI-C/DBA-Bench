"""Real PgBouncer connection-budget resource governance scenario."""

from __future__ import annotations

import json
import hashlib
import os
import queue
import re
import subprocess
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from io import StringIO
from pathlib import Path
from typing import Any, Mapping

from src.execution.history.metrics import MetricDefinition, MetricFrame, MetricQuery, render_metric_frame
from src.execution.history.records import (
    CapturedRecords,
    HistoricalCoverage,
    HistoricalPointRecord,
    HistoricalRecordSource,
)
from src.scenarios.evaluation.postgres.resource_governance.pgbouncer_connection_budget import (
    PgResourceGovernancePgbouncerConnectionBudgetEvaluatorCase,
    PgResourceGovernancePgbouncerConnectionBudgetSimpleEvaluatorCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.frozen_history import DecoyDirection, DecoyKind, HistoryDecoySpec, FrozenHistorySpec
from src.scenarios.workloads import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    WorkloadProfile,
)
from src.workloads.tpcds import get_tpcds_query

from ...base import (
    CaseResourceSpec,
    DifficultyCalibration,
    FaultPlan,
    PostgresCaseRuntime,
    PostgresRuntimeSpec,
    PostgresScenario,
    PostgresScenarioCase,
)


PGBOUNCER_FAULT_IMAGE_PREFIX = (
    "aiopsbench-pg-resource-governance-pgbouncer-connection-budget"
)
PGBOUNCER_DOCKERFILE = "config/docker/pgbouncer/Dockerfile"
PGBOUNCER_PORTS = {
    "postgres": 15821,
    "pgbouncer": 15822,
    "admin_helper": 15823,
    "workload_helper": 15824,
    "auxiliary": (15825, 15826, 15827, 15828, 15829),
}

_RESOURCE_SPEC = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=4096,
    container_cpu_limit=1.0,
    container_memory_mb=2048,
)


def _json_payload(raw: object) -> dict[str, Any]:
    if isinstance(raw, str):
        raw = json.loads(raw)
    if not isinstance(raw, dict) or raw.get("status") != "success":
        raise RuntimeError(f"Expected successful PostgreSQL result, got {raw!r}")
    return raw


def _sql_identifier(value: object, label: str) -> str:
    text = str(value)
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", text):
        raise ValueError(f"Invalid SQL identifier for {label}: {value!r}")
    return text


def _fault_image_name(case_id: str) -> str:
    return f"{PGBOUNCER_FAULT_IMAGE_PREFIX}-{_sql_identifier(case_id, 'case_id')}:latest"


def _escape_sql(value: object) -> str:
    return str(value).replace("'", "''")


def _docker(*args: str, check: bool = True, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=timeout)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"docker command failed: command={args!r}, returncode={result.returncode}, "
            f"stdout={result.stdout[-1000:]!r}, stderr={result.stderr[-1000:]!r}"
        )
    return result


def _port_available(port: int) -> bool:
    result = subprocess.run(
        ["ss", "-ltn", "sport", "=", f":{int(port)}"],
        capture_output=True,
        text=True,
    )
    return f":{int(port)}" not in result.stdout


def _port_owned_by_container(port: int, container_name: str) -> bool:
    """Allow the already deployed case PostgreSQL to occupy its reserved port."""
    result = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Running}}", str(container_name)],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip().casefold() == "true"


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBouncerConnectionBudgetCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    pgbouncer_fault_image: str
    dbname: str
    postgres_max_connections: int
    pool_users: tuple[str, ...]
    checkout_user: str
    report_user: str
    etl_user: str
    checkout_application: str
    report_application: str
    etl_application: str
    health_application: str
    long_report_application: str
    report_profile: str
    report_probe_profile: str
    report_query: str
    report_qps: float
    report_probe_qps: float
    minimum_report_progress: int
    minimum_etl_progress: int
    minimum_health_progress: int
    minimum_checkout_progress: int
    checkout_p99_ms: float
    checkout_success_ratio: float
    minimum_fairness_ratio: float
    max_client_connections: int
    max_database_connections: int
    max_pool_budget: int
    max_cpu_percent: float
    etl_rows: int
    etl_batch_size: int
    churn_connections: int
    checkout_clients: int
    replay_checkout_workers: int
    replay_hold_seconds: float
    replay_duration_seconds: float
    initial_pool_size: int
    initial_reserve_pool_size: int
    initial_runtime_max_database_connections: int
    normal_checkout_role_connection_limit: int
    target_checkout_role_connection_limit: int
    recovered_checkout_role_connection_limit: int
    other_role_connection_limit: int
    protected_neighbor_connections: int
    bounded_neighbor_roles: tuple[tuple[str, int], ...] = ()
    public_sql_protected_relations: tuple[str, ...] = (
        "rg_pgbouncer_etl_stage",
        "rg_pgbouncer_etl_target",
    )
    simple: bool = False


class PgResourceGovernancePgbouncerConnectionBudgetForPoolPartitionShortageScenarioCase(
    PgBouncerConnectionBudgetCase
):
    """Hard three-workload pool partition shortage case identity."""


class PgResourceGovernancePgbouncerConnectionBudgetForPoolPartitionShortageSimpleScenarioCase(
    PgBouncerConnectionBudgetCase
):
    """Easy two-workload pool partition shortage case identity."""


def _workload_profiles(case: PgBouncerConnectionBudgetCase) -> tuple[WorkloadProfile, ...]:
    profiles = [
        WorkloadProfile(
            name=case.report_profile,
            sql=get_tpcds_query(case.report_query),
            qps=case.report_qps,
            tier="MEDIUM",
            application_name=case.report_application,
            connection_pool="reporting",
        ),
        WorkloadProfile(
            name=case.report_probe_profile,
            sql="SELECT count(*) FROM pgbench_accounts WHERE aid BETWEEN 1 AND 100;",
            qps=case.report_probe_qps,
            tier="LIGHT",
            application_name=f"{case.report_application}-probe",
            connection_pool="reporting",
        ),
    ]
    if not case.simple:
        profiles.extend(
            (
                WorkloadProfile(
                    name="health_probe",
                    sql="SELECT 1;",
                    qps=0.30,
                    tier="LIGHT",
                    application_name=case.health_application,
                    connection_pool="checkout",
                ),
                WorkloadProfile(
                    name="report_long_noise",
                    sql="SELECT pg_sleep(0.15), count(*) FROM pgbench_accounts;",
                    qps=0.08,
                    tier="MEDIUM",
                    application_name=case.long_report_application,
                    connection_pool="reporting",
                ),
                WorkloadProfile(
                    name="checkout_auxiliary_read",
                    sql="SELECT count(*) FROM pgbench_accounts WHERE aid BETWEEN 901 AND 950;",
                    qps=0.05,
                    tier="LIGHT",
                    application_name="checkout-api-11",
                    connection_pool="checkout",
                ),
                WorkloadProfile(
                    name="reporting_batch_auxiliary",
                    sql="SELECT pg_sleep(0.20), count(*) FROM pgbench_accounts WHERE aid BETWEEN 1 AND 250;",
                    qps=0.05,
                    tier="MEDIUM",
                    application_name="reporting-batch-07",
                    connection_pool="reporting",
                ),
            )
        )
    return tuple(profiles)


class PgBouncerMetricHistoryProvider:
    """Capture raw PgBouncer, database and service observations for frozen history."""

    metric_names = frozenset({
        "pgbouncer_pool_clients",
        "pgbouncer_pool_servers",
        "pgbouncer_pool_rates",
        "database_capacity",
        "service_slo",
        "connection_churn",
    })

    _DEFINITIONS = {
        "pgbouncer_pool_clients": MetricDefinition(
            name="pgbouncer_pool_clients",
            value_fields=("cl_active", "cl_waiting", "maxwait_sec"),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        ),
        "pgbouncer_pool_servers": MetricDefinition(
            name="pgbouncer_pool_servers",
            value_fields=("sv_active", "sv_idle", "sv_used"),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        ),
        "pgbouncer_pool_rates": MetricDefinition(
            name="pgbouncer_pool_rates",
            value_fields=("xact_per_sec", "query_per_sec", "avg_query_ms"),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        ),
        "database_capacity": MetricDefinition(
            name="database_capacity",
            value_fields=("active_connections", "cpu_percent"),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        ),
        "service_slo": MetricDefinition(
            name="service_slo",
            value_fields=("throughput_per_sec", "p99_ms", "success_ratio", "progress_units"),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        ),
        "connection_churn": MetricDefinition(
            name="connection_churn",
            value_fields=("connects_per_sec", "disconnects_per_sec"),
            lookback_seconds=0,
            source_step_seconds=2,
            lower_bound=0.0,
            upper_bound=None,
        ),
    }

    def __init__(self, env=None, case: PgBouncerConnectionBudgetCase | None = None, injector=None) -> None:
        self.env = env
        self.case = case
        self.injector = injector
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._failure: Exception | None = None
        self._last_timestamp_ms: int | None = None
        self._samples: dict[tuple[str, str | None], list[tuple[int, dict[str, float]]]] = {}
        self._events: list[HistoricalPointRecord] = []
        self._previous_stats: dict[tuple[str, str | None], tuple[int, int, float]] = {}
        self._previous_clients_by_pool: dict[str, set[tuple[str, ...]]] = {}
        self._previous_profile_counts: dict[str, tuple[int, int]] = {}
        self._previous_churn_counts: tuple[int, int] | None = None
        self._previous_etl_rows = 0
        self._previous_sample_time: float | None = None
        self._previous_cpu_usage: tuple[float, int] | None = None
        self._target_revision_recorded = False
        self._target_sample_count = 0

    def configure(self, env, case) -> None:
        """Bind the reusable Case adapter to the run-local environment."""
        self.env = env
        self.case = case
        self.injector = None
        self.reset()

    def metric_definitions(self) -> Mapping[str, MetricDefinition]:
        return dict(self._DEFINITIONS)

    def sample_metrics(self, *, connection, timestamp_ms: int, elapsed_seconds: float, base_values) -> Mapping[str, Mapping[str, float]]:
        """The provider's own aligned thread owns RG1 sampling; no env-level extras."""
        return {}

    def target_variants(self, metric: str) -> tuple[str | None, ...]:
        normalized = str(metric).casefold()
        if normalized in {"pgbouncer_pool_clients", "pgbouncer_pool_servers", "connection_churn"}:
            return (None, *(f"{self.case.dbname}/{user}" for user in self.case.pool_users))
        if normalized == "pgbouncer_pool_rates":
            return (None,)
        if normalized == "service_slo":
            services = ("checkout", "report", "etl") if not self.case.simple else ("checkout", "report")
            # Service progress has different business units: calls for
            # checkout/report and updated rows for ETL. Do not expose a
            # ambiguous cross-service aggregate with mixed units.
            return services
        if normalized == "database_capacity":
            return (None,)
        raise ValueError(f"Unknown RG1 metric: metric={metric!r}")

    def fingerprint(self) -> str:
        return "pg-rg-mf01-pgbouncer-observation-v3"

    def agent_contract(self) -> dict[str, object]:
        return {
            "case_id": self.case.case_id,
            "history_contract": "raw frozen observations; current state may be normal after the historical incident",
            "metric_semantics": {
                "pgbouncer_pool_clients.maxwait_sec": "maximum observed client wait in seconds; derived from SHOW POOLS maxwait/maxwait_us",
                "pgbouncer_pool_rates": "database-level transaction/query rate and average query time from SHOW STATS; no per-user rate is claimed when the server does not expose a user dimension",
                "service_slo.checkout": "background checkout probe SLO from WorkloadRunner; the sustained pgbench pressure is represented by pgbouncer_pool_clients/pgbouncer_pool_servers, while its end-to-end p99 is independently measured by the joint replay artifact",
                "service_slo.report.success_ratio": "report probe successful calls divided by report calls in this sample interval, bounded to 0..1",
                "service_slo.etl": "ETL reports success when rows advanced and exposes updated rows as progress_units",
                "service_slo.progress_units": "background checkout/report probe calls and ETL updated rows during this 2-second sample interval; compare only within the same service",
                "database_capacity.active_connections": "PostgreSQL client backend sessions, including idle sessions; it is a connection-count capacity signal, not active-query count",
            },
            "metrics": {
                name: {
                    "fields": list(definition.value_fields),
                    "targets": [target for target in self.target_variants(name)],
                    "source": "real PgBouncer SHOW POOLS/SHOW STATS, PostgreSQL/cgroup sampler, and workload driver",
                }
                for name, definition in self._DEFINITIONS.items()
            },
            "public_limits": {
                "postgres_max_connections": self.case.postgres_max_connections,
                "max_database_connections": self.case.max_database_connections,
                "max_client_connections": self.case.max_client_connections,
                "max_pool_budget": self.case.max_pool_budget,
                "checkout_p99_ms": self.case.checkout_p99_ms,
                "checkout_success_ratio": self.case.checkout_success_ratio,
                "minimum_fairness_ratio": self.case.minimum_fairness_ratio,
                "minimum_health_progress": self.case.minimum_health_progress,
                "max_cpu_percent": self.case.max_cpu_percent,
                "peak_server_connections": self.case.max_database_connections,
                "pool_mode": "transaction",
            },
        }

    def reset(self) -> None:
        with self._lock:
            self._samples.clear()
            self._previous_stats.clear()
            self._previous_clients_by_pool.clear()
            self._previous_profile_counts.clear()
            self._previous_churn_counts = None
            self._previous_etl_rows = 0
            self._previous_sample_time = None
            self._previous_cpu_usage = None
            self._last_timestamp_ms = None
            self._failure = None
            self._target_revision_recorded = False
            self._target_sample_count = 0

    def reset_sampling_baselines(self) -> None:
        """Reset deltas after the owned pooler is recreated between windows."""
        with self._lock:
            self._previous_stats.clear()
            self._previous_clients_by_pool.clear()
            self._previous_profile_counts.clear()
            self._previous_churn_counts = None
            self._previous_etl_rows = 0
            self._previous_sample_time = None
            self._previous_cpu_usage = None
            self._failure = None
            self._target_revision_recorded = False
            self._target_sample_count = 0
            runner = getattr(self.env, "_workload_runner", None)
            if runner is not None:
                live = runner.get_live_activity_counts()
                profile_groups = {
                    "checkout": tuple(
                        profile.name
                        for profile in _workload_profiles(self.case)
                        if profile.connection_pool == "checkout"
                    ),
                    "report": tuple(
                        profile.name
                        for profile in _workload_profiles(self.case)
                        if profile.connection_pool == "reporting"
                    ),
                }
                self._previous_profile_counts = {
                    service: (
                        sum(int(live.get(name, {}).get("calls", 0)) for name in names),
                        sum(int(live.get(name, {}).get("ok_calls", 0)) for name in names),
                    )
                    for service, names in profile_groups.items()
                }
            if self.injector is not None:
                with self.injector._etl_lock:
                    self._previous_etl_rows = int(self.injector._etl_rows_updated)
                self._previous_churn_counts = self.injector.churn_counts()
            if self._previous_profile_counts or self._previous_etl_rows or self._previous_churn_counts:
                self._previous_sample_time = time.time()

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._failure = None
        self._thread = threading.Thread(target=self._loop, name="pg-rg-mf01-history-sampler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
        self._thread = None

    def wait_until(self, end_epoch_ms: int, timeout_seconds: float = 30.0) -> None:
        deadline = time.monotonic() + float(timeout_seconds)
        while True:
            with self._lock:
                last_timestamp_ms = self._last_timestamp_ms
                failure = self._failure
                thread = self._thread
            if failure is not None:
                raise RuntimeError(f"RG1 history sampler failed: {failure}")
            if last_timestamp_ms is not None and last_timestamp_ms >= end_epoch_ms:
                return
            if thread is None or not thread.is_alive():
                raise RuntimeError(
                    "RG1 metric capture cannot reach its requested end because the scenario sampler is not running: "
                    f"requested_end_epoch_ms={end_epoch_ms}, last_timestamp_ms={last_timestamp_ms}"
                )
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    "RG1 scenario metric sampler did not reach the requested end: "
                    f"requested_end_epoch_ms={end_epoch_ms}, last_timestamp_ms={last_timestamp_ms}"
                )
            self._stop.wait(0.05)

    def record_event(
        self,
        *,
        event_type: str,
        entity_type: str,
        entity: str,
        action: str,
        status: str,
        details: Mapping[str, object],
        correlation_id: str,
        target: str | None = None,
        timestamp_ms: int | None = None,
    ) -> None:
        timestamp_ms = int(time.time() * 1000) if timestamp_ms is None else int(timestamp_ms)
        with self._lock:
            self._events.append(HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target=str(target or entity),
                timestamp_ms=timestamp_ms,
                payload={
                    "event_type": event_type,
                    "entity_type": entity_type,
                    "entity": entity,
                    "action": action,
                    "status": status,
                    "correlation_id": correlation_id,
                    "details": dict(details),
                },
            ))

    def capture_history_records(
        self,
        sources: tuple[HistoricalRecordSource, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
    ) -> CapturedRecords:
        raise_capture_errors = getattr(self.injector, "_raise_capture_errors", None)
        if callable(raise_capture_errors):
            raise_capture_errors()
        if HistoricalRecordSource.OPERATION_EVENT not in sources:
            return CapturedRecords()
        with self._lock:
            events = tuple(
                event for event in self._events
                if start_epoch_ms <= event.timestamp_ms <= end_epoch_ms
            )
        return CapturedRecords(
            point_records=events,
            coverage=(HistoricalCoverage(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target=None,
                start_ms=start_epoch_ms,
                end_ms=end_epoch_ms,
            ),),
        )

    def query(self, metric: str, target: str | None, start_ms, end_ms) -> str:
        if start_ms is None and end_ms is None:
            with self._lock:
                samples = self._samples.get((str(metric).casefold(), target), ())
                if not samples:
                    raise RuntimeError(f"RG1 history sampler has no data: metric={metric!r}, target={target!r}")
                start_epoch_ms, end_epoch_ms = samples[0][0], samples[-1][0]
        else:
            start_epoch_ms = self._coerce_epoch_ms(start_ms, "start")
            end_epoch_ms = self._coerce_epoch_ms(end_ms, "end")
        return render_metric_frame(
            self.query_metric(MetricQuery(
                metric=metric,
                target=target,
                start_epoch_ms=start_epoch_ms,
                end_epoch_ms=end_epoch_ms,
            )),
            available_start_ms=self._available_start_ms(),
            available_end_ms=self._available_end_ms(),
            requested_start_ms=start_epoch_ms,
            requested_end_ms=end_epoch_ms,
            step_seconds=2,
        )

    def query_metric(self, query: MetricQuery) -> MetricFrame:
        metric = str(query.metric).casefold()
        if metric not in self.metric_names:
            raise ValueError(f"Unknown RG1 metric: metric={metric!r}")
        if query.target not in self.target_variants(metric):
            raise ValueError(f"Unknown RG1 metric target: metric={metric!r}, target={query.target!r}")
        with self._lock:
            samples = tuple(self._samples.get((metric, query.target), ()))
            failure = self._failure
        if failure is not None:
            raise RuntimeError(f"RG1 history sampler failed: {failure}")
        if not samples:
            raise RuntimeError(f"RG1 history sampler has no data: metric={metric!r}, target={query.target!r}")
        available_start, available_end = samples[0][0], samples[-1][0]
        start_ms = query.start_epoch_ms if query.start_epoch_ms is not None else available_start
        end_ms = query.end_epoch_ms if query.end_epoch_ms is not None else available_end
        if end_ms > available_end:
            # The aligned capture end can sit one sampler tick ahead of the
            # last stored sample; let the aligned thread reach it.
            self.wait_until(end_ms)
            with self._lock:
                samples = tuple(self._samples.get((metric, query.target), ()))
            if not samples:
                raise RuntimeError(f"RG1 history sampler has no data: metric={metric!r}, target={query.target!r}")
            available_start, available_end = samples[0][0], samples[-1][0]
        if start_ms < available_start or end_ms > available_end:
            raise ValueError(
                f"RG1 history query is outside sampler range: metric={metric!r}, target={query.target!r}, "
                f"requested=({start_ms},{end_ms}), available=({available_start},{available_end})"
            )
        selected = tuple(item for item in samples if start_ms <= item[0] <= end_ms)
        expected = tuple(range(start_ms, end_ms + 2_000, 2_000))
        actual = tuple(item[0] for item in selected)
        if actual != expected:
            raise ValueError(
                f"RG1 metric history has incomplete query grid: metric={metric!r}, target={query.target!r}, "
                f"expected={expected!r}, actual={actual!r}"
            )
        timestamps = tuple(item[0] for item in selected)
        definition = self._DEFINITIONS[metric]
        frame = MetricFrame(
            metric=metric,
            query_target=query.target,
            step_seconds=2,
            series={query.target or "postgres": {
                field: tuple(values[field] for _, values in selected)
                for field in definition.value_fields
            }},
            timestamps_ms={query.target or "postgres": timestamps},
        )
        step = query.step_seconds or 2
        if step != 2:
            frame = frame.resample(step, start_ms, end_ms)
        return frame

    def capture(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
    ) -> tuple[MetricFrame, ...]:
        if step_seconds != 2:
            raise ValueError(f"RG1 metric history capture step must be 2 seconds: step_seconds={step_seconds}")
        with self._lock:
            last_timestamp_ms = self._last_timestamp_ms
            thread = self._thread
        if (
            last_timestamp_ms is not None
            and last_timestamp_ms < end_epoch_ms
            and end_epoch_ms - last_timestamp_ms <= 8_000
            and thread is not None
            and thread.is_alive()
        ):
            # The capture window boundary and the sampler's next aligned tick
            # can race by one tick; wait briefly for the final sample instead
            # of failing the whole capture on scheduler jitter.
            try:
                self.wait_until(end_epoch_ms, timeout_seconds=6.0)
            except (TimeoutError, RuntimeError):
                pass
        frames = []
        expected = tuple(range(start_epoch_ms, end_epoch_ms + 1, 2_000))
        for metric in metrics:
            for target in self.target_variants(metric):
                frame = self.query_metric(MetricQuery(
                    metric=metric,
                    target=target,
                    start_epoch_ms=start_epoch_ms,
                    end_epoch_ms=end_epoch_ms,
                ))
                actual = frame.timestamps_ms[target or "postgres"]
                if actual != expected:
                    raise RuntimeError(
                        f"RG1 metric history has incomplete grid: metric={metric!r}, target={target!r}, "
                        f"expected={expected!r}, actual={actual!r}"
                    )
                frames.append(frame)
        return tuple(frames)

    def capture_history(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
    ) -> tuple[MetricFrame, ...]:
        """Expose the shared PostgreSQL public-history provider contract."""
        target_frames = self.capture(metrics, start_epoch_ms, end_epoch_ms, step_seconds)
        frames: list[MetricFrame] = []
        for metric in metrics:
            metric_frames = [frame for frame in target_frames if frame.metric == metric]
            if not metric_frames:
                raise RuntimeError(f"RG1 metric history capture returned no frame: metric={metric!r}")
            series = {
                target: values
                for frame in metric_frames
                for target, values in frame.series.items()
            }
            timestamps_ms = {
                target: timestamps
                for frame in metric_frames
                for target, timestamps in frame.timestamps_ms.items()
            }
            frames.append(MetricFrame(
                metric=metric,
                query_target=None,
                step_seconds=step_seconds,
                series=series,
                timestamps_ms=timestamps_ms,
            ))
        return tuple(frames)

    def _available_start_ms(self) -> int:
        with self._lock:
            values = [samples[0][0] for samples in self._samples.values() if samples]
        if not values:
            raise RuntimeError("RG1 history sampler has no available range")
        return max(values)

    def _available_end_ms(self) -> int:
        with self._lock:
            values = [samples[-1][0] for samples in self._samples.values() if samples]
        if not values:
            raise RuntimeError("RG1 history sampler has no available range")
        return min(values)

    def _loop(self) -> None:
        next_tick = (int(time.time() * 1000) // 2_000 + 1) * 2_000
        while not self._stop.is_set():
            wait_seconds = max(0.0, next_tick / 1000.0 - time.time())
            if self._stop.wait(wait_seconds):
                return
            try:
                self._sample(next_tick)
            except Exception as exc:
                with self._lock:
                    self._failure = exc
                return
            next_tick += 2_000

    def _sample(self, timestamp_ms: int) -> None:
        pools = _json_payload(self.env.manage_instance(action="pgbouncer_show_pools"))
        stats = _json_payload(self.env.manage_instance(action="pgbouncer_show_stats"))
        clients = _json_payload(self.env.pgbouncer_admin_query("SHOW CLIENTS;"))
        pool_rows = self._pool_rows(pools)
        stats_rows = self._stats_rows(stats)
        timestamp_seconds = timestamp_ms / 1000.0
        elapsed = max(2.0, timestamp_seconds - self._previous_sample_time) if self._previous_sample_time is not None else 2.0
        client_values = self._client_values(clients, elapsed)
        capacity = self._capacity_values()
        services = self._service_values(elapsed)
        values: dict[tuple[str, str | None], dict[str, float]] = {}
        pool_targets = tuple(f"{self.case.dbname}/{user}" for user in self.case.pool_users)
        for target in pool_targets:
            row = pool_rows.get(target, {})
            values[("pgbouncer_pool_clients", target)] = {
                "cl_active": float(row.get("cl_active", 0)),
                "cl_waiting": float(row.get("cl_waiting", 0)),
                "maxwait_sec": self._maxwait_seconds(row),
            }
            values[("pgbouncer_pool_servers", target)] = {
                "sv_active": float(row.get("sv_active", 0)),
                "sv_idle": float(row.get("sv_idle", 0)),
                "sv_used": float(row.get("sv_used", 0)),
            }
            values[("connection_churn", target)] = client_values.get(target, {
                "connects_per_sec": 0.0,
                "disconnects_per_sec": 0.0,
            })
        values[("pgbouncer_pool_clients", None)] = self._aggregate(
            values,
            "pgbouncer_pool_clients",
            ("cl_active", "cl_waiting", "maxwait_sec"),
            max_fields=frozenset({"maxwait_sec"}),
        )
        values[("pgbouncer_pool_servers", None)] = self._aggregate(values, "pgbouncer_pool_servers", ("sv_active", "sv_idle", "sv_used"))
        # SHOW STATS exposes database-level counters in this deployment. Keep
        # that observation at database scope instead of copying it into each
        # user pool and implying a per-pool causal rate.
        rate = stats_rows.get(self.case.dbname, {})
        previous = self._previous_stats.get((self.case.dbname, None))
        xacts = int(rate.get("total_xact_count", 0))
        queries = int(rate.get("total_query_count", 0))
        if previous is None:
            xact_rate = query_rate = 0.0
        else:
            xact_rate = max(0.0, (xacts - previous[0]) / elapsed)
            query_rate = max(0.0, (queries - previous[1]) / elapsed)
        values[("pgbouncer_pool_rates", None)] = {
            "xact_per_sec": xact_rate,
            "query_per_sec": query_rate,
            "avg_query_ms": float(rate.get("avg_query_ms", 0)),
        }
        self._previous_stats[(self.case.dbname, None)] = (
            xacts,
            queries,
            float(rate.get("avg_query_ms", 0)),
        )
        values[("connection_churn", None)] = self._aggregate(values, "connection_churn", ("connects_per_sec", "disconnects_per_sec"))
        values[("database_capacity", None)] = capacity
        for target, service in services.items():
            values[("service_slo", target)] = service
        record_target_revision = False
        with self._lock:
            if self._last_timestamp_ms is not None and timestamp_ms <= self._last_timestamp_ms:
                raise RuntimeError(f"RG1 history sampler timestamp did not advance: timestamp_ms={timestamp_ms}")
            for key, fields in values.items():
                self._samples.setdefault(key, []).append((timestamp_ms, fields))
            self._last_timestamp_ms = timestamp_ms
            self._target_sample_count += 1
            # The sampler restarts immediately before target capture. Count
            # samples from that restart rather than the retained normal
            # samples, so the revision event is placed inside the public
            # target window instead of being lost during history assembly.
            if (
                self.injector is not None
                and not self._target_revision_recorded
                and self._target_sample_count >= 2
            ):
                self._target_revision_recorded = True
                record_target_revision = True
        if record_target_revision:
            self.record_event(
                event_type="config_revision",
                entity_type="pooler_config",
                entity="pgbouncer",
                action="apply",
                status="success",
                details={
                    "revision": "config-revision-17",
                    "old_max_db_connections": self.case.initial_runtime_max_database_connections,
                    "new_max_db_connections": self.case.max_database_connections,
                    "pool_mode": "transaction",
                },
                correlation_id=getattr(self.injector, "run_id", ""),
                timestamp_ms=timestamp_ms,
            )
        self._previous_sample_time = timestamp_seconds

    @staticmethod
    def _aggregate(
        values,
        metric: str,
        fields: tuple[str, ...],
        max_fields: frozenset[str] = frozenset(),
    ) -> dict[str, float]:
        targets = [item for (name, target), item in values.items() if name == metric and target is not None]
        return {
            field: (
                max((float(item[field]) for item in targets), default=0.0)
                if field in max_fields
                else sum(float(item[field]) for item in targets)
            )
            for field in fields
        }

    @staticmethod
    def _maxwait_seconds(row: Mapping[str, object]) -> float:
        """Prefer PgBouncer's microsecond field while supporting older builds."""
        def number(value: object) -> float:
            try:
                return max(0.0, float(value or 0))
            except (TypeError, ValueError):
                return 0.0

        return max(number(row.get("maxwait")), number(row.get("maxwait_us")) / 1_000_000.0)

    def _pool_rows(self, payload: Mapping[str, object]) -> dict[str, dict[str, object]]:
        columns = list(payload.get("columns", ()))
        result = {}
        for row in payload.get("result", ()):
            if "database" not in columns or "user" not in columns:
                continue
            key = f"{row[columns.index('database')]}/{row[columns.index('user')]}"
            result[key] = {name: row[index] for index, name in enumerate(columns) if index < len(row)}
        return result

    def _stats_rows(self, payload: Mapping[str, object]) -> dict[str, dict[str, object]]:
        columns = list(payload.get("columns", ()))
        result = {}
        aggregate_by_database: dict[str, dict[str, object]] = {}
        for row in payload.get("result", ()):
            if "database" not in columns:
                continue
            database = str(row[columns.index("database")])
            item = {name: row[index] for index, name in enumerate(columns) if index < len(row)}
            if "avg_query_time" in item:
                item["avg_query_ms"] = float(item["avg_query_time"] or 0) / 1000.0
            raw_user = row[columns.index("user")] if "user" in columns else None
            user = str(raw_user) if raw_user not in (None, "") else None
            if user is None:
                aggregate_by_database[database] = item
            else:
                result[f"{database}/{user}"] = item
        if self.case.dbname in aggregate_by_database:
            result[self.case.dbname] = aggregate_by_database[self.case.dbname]
        return result

    def _client_values(self, payload: Mapping[str, object], elapsed: float) -> dict[str, dict[str, float]]:
        columns = list(payload.get("columns", ()))
        per_pool: dict[str, set[tuple[str, ...]]] = {}
        for row in payload.get("result", ()):
            if "database" not in columns or "user" not in columns:
                continue
            identity = tuple(str(row[index]) for index in range(len(row)))
            pool = f"{row[columns.index('database')]}/{row[columns.index('user')]}"
            per_pool.setdefault(pool, set()).add(identity)
        result = {}
        churn_counts = None
        if self.injector is not None:
            read_churn_counts = getattr(self.injector, "churn_counts", None)
            if callable(read_churn_counts):
                churn_counts = read_churn_counts()
        if churn_counts is not None:
            previous_churn_counts = self._previous_churn_counts
            self._previous_churn_counts = churn_counts
            if previous_churn_counts is None:
                churn_rates = (0.0, 0.0)
            else:
                churn_rates = (
                    max(0, churn_counts[0] - previous_churn_counts[0]) / elapsed,
                    max(0, churn_counts[1] - previous_churn_counts[1]) / elapsed,
                )
        else:
            churn_rates = None
        for pool in (f"{self.case.dbname}/{user}" for user in self.case.pool_users):
            current = per_pool.get(pool, set())
            previous = self._previous_clients_by_pool.get(pool, set())
            result[pool] = {
                "connects_per_sec": (
                    churn_rates[0]
                    if churn_rates is not None and pool == f"{self.case.dbname}/{self.case.checkout_user}"
                    else len(current - previous) / elapsed
                ),
                "disconnects_per_sec": (
                    churn_rates[1]
                    if churn_rates is not None and pool == f"{self.case.dbname}/{self.case.checkout_user}"
                    else len(previous - current) / elapsed
                ),
            }
            self._previous_clients_by_pool[pool] = current
        return result

    def _capacity_values(self) -> dict[str, float]:
        result = _json_payload(self.env.execute_sql_trusted(
            "SELECT count(*) FROM pg_stat_activity WHERE backend_type = 'client backend';"
        ))
        active_connections = float(result.get("result", [[0]])[0][0] if result.get("result") else 0)
        cpu_percent = 0.0
        read_cpu = getattr(self.env, "_read_cpu_usage_usec", None)
        effective_cpus = getattr(self.env, "_effective_cpus", None)
        now = time.monotonic()
        if callable(read_cpu) and callable(effective_cpus):
            current_cpu = int(read_cpu())
            if self._previous_cpu_usage is not None:
                previous_time, previous_value = self._previous_cpu_usage
                elapsed = now - previous_time
                cpus = float(effective_cpus())
                if elapsed > 0 and cpus > 0 and current_cpu >= previous_value:
                    cpu_percent = min(100.0, max(0.0, (current_cpu - previous_value) / (elapsed * 1_000_000 * cpus) * 100.0))
            self._previous_cpu_usage = (now, current_cpu)
        return {"active_connections": active_connections, "cpu_percent": cpu_percent}

    def _service_values(self, elapsed: float) -> dict[str, dict[str, float]]:
        runner = getattr(self.env, "_workload_runner", None)
        live = runner.get_live_activity_counts() if runner is not None else {}
        activity = (
            runner.get_activity(limit=100, window_seconds=max(20.0, elapsed * 5.0)).get("value", [])
            if runner is not None else []
        )
        activity_by_name = {str(item.get("fingerprint")): item for item in activity}
        profile_groups = {
            "checkout": tuple(profile.name for profile in _workload_profiles(self.case) if profile.connection_pool == "checkout"),
            "report": tuple(profile.name for profile in _workload_profiles(self.case) if profile.connection_pool == "reporting"),
        }
        services = {}
        for service, names in profile_groups.items():
            attempts = sum(int(live.get(name, {}).get("calls", 0)) for name in names)
            successes = sum(int(live.get(name, {}).get("ok_calls", 0)) for name in names)
            previous_attempts, previous_successes = self._previous_profile_counts.get(service, (0, 0))
            delta_attempts = max(0, attempts - previous_attempts)
            delta_successes = max(0, successes - previous_successes)
            p99 = max((float(activity_by_name.get(name, {}).get("p99_ms", 0)) for name in names), default=0.0)
            services[service] = {
                "throughput_per_sec": delta_successes / elapsed,
                "p99_ms": p99,
                "success_ratio": min(1.0, delta_successes / delta_attempts) if delta_attempts else 0.0,
                "progress_units": float(delta_successes),
            }
            self._previous_profile_counts[service] = (attempts, successes)
        etl_rows = 0
        if self.injector is not None:
            with self.injector._etl_lock:
                etl_rows = int(self.injector._etl_rows_updated)
        if not etl_rows:
            etl_rows = self._previous_etl_rows
        services["etl"] = {
            "throughput_per_sec": max(0, etl_rows - self._previous_etl_rows) / elapsed,
            "p99_ms": 0.0,
            "success_ratio": 1.0 if etl_rows > self._previous_etl_rows else 0.0,
            "progress_units": float(max(0, etl_rows - self._previous_etl_rows)),
        }
        self._previous_etl_rows = etl_rows
        return services

    @staticmethod
    def _coerce_epoch_ms(value: object, label: str) -> int:
        if value is None:
            raise ValueError(f"RG1 metric history requires a complete start/end window: missing={label}")
        timestamp = getattr(value, "timestamp", None)
        if callable(timestamp):
            return int(timestamp() * 1000)
        return int(value)


class PgBouncerConnectionBudgetInjector(BaseFaultInjector):
    """Own PgBouncer, pgbench, churn, ETL and all temporary Docker resources."""

    def __init__(self) -> None:
        self.env = None
        self.case: PgBouncerConnectionBudgetCase | None = None
        self.run_id = ""
        self.postgres_port = PGBOUNCER_PORTS["postgres"]
        self.pg_container = ""
        self.pgbouncer_container = ""
        self.pgbench_container = ""
        self._pgbench_containers: list[str] = []
        self._pgbench_ramp_thread: threading.Thread | None = None
        self.network = ""
        self.volume = ""
        self.pgbouncer_port = PGBOUNCER_PORTS["pgbouncer"]
        self._config_file: str | None = None
        self._auth_file: str | None = None
        self._checkout_script: str | None = None
        self._pgbench_started = False
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []
        self._seed_connections: list[object] = []
        self._etl_lock = threading.Lock()
        self._etl_rows_updated = 0
        self._etl_batches = 0
        self._etl_next_id = 1
        self._acceptance_artifact: dict[str, Any] | None = None
        self._churn_thread: threading.Thread | None = None
        self._staged_auxiliary_thread: threading.Thread | None = None
        self._target_report_noise_thread: threading.Thread | None = None
        self._target_checkout_noise_thread: threading.Thread | None = None
        self._protected_connections: list[object] = []
        self._protected_ready_count = 0
        self._protected_errors: list[str] = []
        self._history_provider: PgBouncerMetricHistoryProvider | None = None
        self._churn_lock = threading.Lock()
        self._churn_connects = 0
        self._churn_disconnects = 0
        self._capture_error_lock = threading.Lock()
        self._capture_errors: list[str] = []
        self._capture_phase = "runtime"

    def churn_counts(self) -> tuple[int, int]:
        """Return real successful short-connection lifecycle counts for metric sampling."""
        with self._churn_lock:
            return self._churn_connects, self._churn_disconnects

    def _configure(self, context: FaultLifecycleContext) -> None:
        self.env = context.env
        self.case = context.case
        self.run_id = context.run_id
        self.postgres_port = int(getattr(self.env, "port", PGBOUNCER_PORTS["postgres"]))
        ports = context.config.get("ports", PGBOUNCER_PORTS)
        self.pgbouncer_port = int(ports.get("pgbouncer", PGBOUNCER_PORTS["pgbouncer"]))
        case_slug = _sql_identifier(self.case.case_id.replace("-", "_"), "case_id")
        readable_run_slug = re.sub(r"[^a-z0-9]+", "-", self.run_id.casefold()).strip("-")[-12:] or "run"
        run_digest = hashlib.sha256(self.run_id.encode("utf-8")).hexdigest()[:12]
        run_slug = f"{readable_run_slug}-{run_digest}"
        prefix = f"aiopsbench-pg-rg-pgbouncer-{case_slug}-{run_slug}"
        self.pg_container = str(getattr(self.env.deployment, "container_name", "aiopsbench-pg"))
        self.pgbouncer_container = f"{prefix}-pooler"
        self.pgbench_container = f"{prefix}-pgbench"
        self.network = f"{prefix}-network"
        self.volume = f"{prefix}-logs"

    def configure_history_adapter(self, context: FaultLifecycleContext) -> None:
        """Attach the public Case-owned provider before frozen-history validation."""
        self._configure(context)
        case = self.case
        assert case is not None
        if getattr(case, "frozen_history", None) is None:
            return
        provider = getattr(self.env, "_scenario_metric_provider", None)
        if not isinstance(provider, PgBouncerMetricHistoryProvider):
            provider = PgBouncerMetricHistoryProvider(self.env, case, self)
        else:
            provider.env = self.env
            provider.case = case
            provider.injector = self
        self._history_provider = provider
        self.env.attach_scenario_metric_provider(provider)

    def prepare_metric_history(self, context: FaultLifecycleContext) -> None:
        """Build a healthy real pooler runtime used by the normal capture window."""
        self._configure(context)
        case = self.case
        assert case is not None
        if getattr(case, "frozen_history", None) is None:
            return
        self._bootstrap_runtime(case, target_budget=False)
        provider = self._history_provider
        if provider is None:
            raise RuntimeError(f"PgBouncer history provider is not configured: case={case.case_id!r}")
        provider.reset_sampling_baselines()
        provider.start()
        # A short, successful checkout burst is part of normal capture. It is
        # a real same-pool competitor that must be separated from the
        # sustained target deficit by duration and service progress.
        self._start_staged_auxiliary_read(case, burst_workers=8, record_schedule=True)
        # The provider's own aligned thread is the single sampler for the
        # normal-capture window; install() stops and restarts it for the
        # target capture after resetting baselines.
        history_provider = self._history_provider
        if history_provider is not None:
            history_provider.start()

    def _record_event(
        self,
        *,
        event_type: str,
        entity_type: str,
        entity: str,
        action: str,
        status: str = "success",
        details: Mapping[str, object] | None = None,
        target: str | None = None,
    ) -> None:
        provider = self._history_provider
        if provider is None:
            return
        provider.record_event(
            event_type=event_type,
            entity_type=entity_type,
            entity=entity,
            action=action,
            status=status,
            details=details or {},
            correlation_id=self.run_id,
            target=target,
        )

    def _bootstrap_runtime(self, case: PgBouncerConnectionBudgetCase, *, target_budget: bool) -> None:
        with self._capture_error_lock:
            self._capture_errors.clear()
        self._capture_phase = "target" if target_budget else "normal"
        self._preflight_ports(allow_pgbouncer=self._history_provider is not None)
        self._cleanup_owned_runtime()
        checkout_role_connection_limit = (
            case.target_checkout_role_connection_limit
            if target_budget
            else case.normal_checkout_role_connection_limit
        )
        with self.env.metrics_hidden():
            self._create_database_objects(
                case,
                checkout_role_connection_limit=checkout_role_connection_limit,
            )
        self._create_network()
        self._build_fault_image(case)
        self._write_runtime_files(
            case,
            runtime_max_database_connections=(
                case.max_database_connections
                if target_budget
                else case.initial_runtime_max_database_connections
            ),
        )
        self._start_pgbouncer(case)
        self._configure_environment_endpoints(case)
        self._start_protected_neighbors(case)
        self._start_pgbench(
            case,
            clients=2 if not case.simple else case.checkout_clients,
            ramp_target=target_budget,
        )
        # Keep one deterministic ETL checkpoint pause in normal capture so
        # the captured-benign decoy is a real, reproducible workload phase.
        self._start_etl(case, checkpoint_pause=not target_budget)
        self._start_connection_churn(case)
        if not case.simple:
            self._start_capture_report_noise(case, target_budget=target_budget)
        if target_budget:
            self._start_target_checkout_noise(case)
        self._seed_pool_connections(case)
        self._wait_until_fault_ready(case, timeout=45)
        # Do not count the deterministic readiness phase as business replay
        # progress; it only establishes the post-change pressure baseline.
        self._reset_replay_counters()

    def _record_capture_error(self, component: str, exc: Exception, *, expected: bool = False) -> None:
        if expected:
            return
        with self._capture_error_lock:
            self._capture_errors.append(f"{component}: {type(exc).__name__}: {exc}")

    def _raise_capture_errors(self) -> None:
        with self._capture_error_lock:
            errors = tuple(self._capture_errors)
        if errors:
            raise RuntimeError(
                "PG-RG-MF01 capture infrastructure: background workload/provider error: "
                + "; ".join(errors[:8])
            )

    @staticmethod
    def _is_expected_connection_failure(exc: Exception) -> bool:
        if str(getattr(exc, "pgcode", "") or "") == "53300":
            return True
        message = str(exc).casefold()
        return any(
            marker in message
            for marker in (
                "max_user_connections",
                "too many connections",
                "too many clients",
                "no more connections allowed",
            )
        )

    def _is_expected_target_timeout(self, exc: Exception) -> bool:
        return self._capture_phase == "target" and "timeout" in str(exc).casefold()

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        case = self.case
        assert case is not None
        history_provider = self._history_provider
        if history_provider is not None:
            history_provider.stop()
        self._bootstrap_runtime(case, target_budget=True)
        if history_provider is not None:
            history_provider.reset_sampling_baselines()
            history_provider.start()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        case = self.case
        assert case is not None
        self._preflight_ports(allow_pgbouncer=True)
        self._create_network()
        self._build_fault_image(case)
        self._write_runtime_files(case, runtime_max_database_connections=case.max_database_connections)
        self._start_pgbouncer(case)
        self._configure_environment_endpoints(case)
        self._start_protected_neighbors(case)
        self._start_pgbench(case)
        self._start_etl(case)
        self._start_connection_churn(case)
        self._seed_pool_connections(case)
        self._wait_until_fault_ready(case, timeout=45)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        case = self.case
        assert case is not None
        config = _json_payload(self.env.manage_instance(action="pgbouncer_show_config"))
        pools = _json_payload(self.env.manage_instance(action="pgbouncer_show_pools"))
        activity = _json_payload(
            self.env.execute_sql(
                "SELECT usename, application_name, state, count(*) "
                "FROM pg_stat_activity WHERE usename IN "
                f"('{_escape_sql(case.checkout_user)}','{_escape_sql(case.report_user)}','{_escape_sql(case.etl_user)}') "
                "GROUP BY usename, application_name, state ORDER BY usename, application_name, state;"
            )
        )
        # Keep the normal-capture competitor out of joint replay. The target
        # handoff retains the smaller auxiliary stream used by the live case.
        self._start_staged_auxiliary_read(case)
        self._record_event(
            event_type="scheduler_stage",
            entity_type="workload_stage",
            entity="peak_replay",
            action="start",
            details={"checkout": True, "report": True, "etl": True},
        )
        return {
            "pgbouncer_config": config,
            "pgbouncer_pools": pools,
            "workload_connections": activity,
            "fixed_postgres_budget": self.env.execute_sql(
                "SELECT current_setting('max_connections')::integer AS max_connections;"
            ),
            "port_allocation": {
                "postgres": self.postgres_port,
                "pgbouncer": self.pgbouncer_port,
                "admin_helper": PGBOUNCER_PORTS["admin_helper"],
                "workload_helper": PGBOUNCER_PORTS["workload_helper"],
            },
        }

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """End the historical pressure window while keeping current PgBouncer queryable."""
        if self._history_provider is not None:
            self._history_provider.stop()
        self._stop_runtime()

    def _start_replay_runtime(self, case: PgBouncerConnectionBudgetCase) -> None:
        """Recreate scenario-owned pressure for evaluator replay without rewriting Agent config."""
        self._reset_replay_counters()
        self._stop_event.clear()
        self._start_protected_neighbors(case)
        self._start_pgbench(case)
        self._start_etl(case)
        self._start_connection_churn(case)
        self._seed_pool_connections(case)
        self._wait_until_fault_ready(case, timeout=45)

    def _reset_replay_counters(self) -> None:
        """Discard capture/agent-period progress before a joint replay."""
        with self._etl_lock:
            self._etl_rows_updated = 0
            self._etl_batches = 0
        with self._churn_lock:
            self._churn_connects = 0
            self._churn_disconnects = 0

    def _quiesce_inherited_workload_runner(self) -> None:
        runner = getattr(self.env, "_workload_runner", None)
        if runner is None:
            return
        if runner._threads:
            runner.stop(join_timeout=120.0)
        while True:
            try:
                runner._queue.get_nowait()
            except queue.Empty:
                break
            else:
                runner._queue.task_done()

    def _begin_replay_observation(self, case: PgBouncerConnectionBudgetCase):
        """Scope background workload counters to the joint acceptance replay."""
        runner = getattr(self.env, "_workload_runner", None)
        if runner is None:
            runner = self.create_workload_runner(
                self.env,
                case.background_workload.profiles,
                case.background_workload.worker_count,
            )
            self.env.attach_workload_runner(runner)
        elif runner._threads:
            self._quiesce_inherited_workload_runner()
        if not runner._threads:
            runner.start()
        runner.begin_observation_window()
        runner.prime_observation_profiles(tuple(profile.name for profile in case.background_workload.profiles))
        return runner

    def _stop_replay_workload_runner_and_snapshot(self) -> dict[str, Any]:
        """Freeze the replay runner before exporting its final observation window."""
        runner = getattr(self.env, "_workload_runner", None)
        if runner is None:
            raise RuntimeError(
                "PgBouncer acceptance replay requires an attached WorkloadRunner for its final snapshot"
            )
        runner.stop(join_timeout=120.0)
        if getattr(self.env, "_workload_runner", None) is runner:
            self.env._workload_runner = None
        return runner.get_observed().get("profiles", {})

    def _replay_failure_for_invalid_pool_mode(
        self,
        case: PgBouncerConnectionBudgetCase,
        pool_mode: str,
        pools_payload: Mapping[str, object],
        config: Mapping[str, object],
    ) -> dict[str, Any]:
        """Return a complete, evaluator-readable artifact for an invalid policy.

        Statement pooling is a model-selected configuration error for this case.
        It must not be confused with a readiness or Docker failure merely because
        protected transaction-boundary connections cannot be started afterward.
        """
        columns = list(pools_payload.get("columns", ()))
        waiting_index = columns.index("cl_waiting") if "cl_waiting" in columns else None
        final_waiting = max(
            (
                int(row[waiting_index] or 0)
                for row in pools_payload.get("result", ())
                if waiting_index is not None and len(row) > waiting_index
            ),
            default=0,
        )
        return {
            "replay_status": "skipped_invalid_pool_mode",
            "policy_failure": {
                "pool_mode": pool_mode,
                "required_pool_mode": "transaction",
                "config": dict(config),
            },
            "checkout": {"attempts": 0, "successes": 0, "success_ratio": 0.0, "p99_ms": 1_000_000.0},
            "report": {"attempts": 0, "completed": 0, "success_ratio": 0.0},
            "etl": {"rows_updated": 0, "batches": 0},
            "database": {
                "max_connections": int(case.max_database_connections) + 1,
                "peak_server_connections": int(case.max_database_connections) + 1,
                "peak_cpu_percent": 101.0,
            },
            "protected_neighbor_connections": 0,
            "protected_neighbor_connections_at_replay_start": 0,
            "protected_neighbor_connections_at_replay_end": 0,
            "fairness_ratio": 0.0,
            "queue_converged": False,
            "final_cl_waiting": final_waiting,
            "final_pools": pools_payload,
            "shutdown_clients": {},
            "pgbench_container_present_after_stop": False,
            "duration_seconds": 0.0,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        if self._history_provider is not None:
            self._history_provider.stop()
        self._stop_runtime()
        self._stop_pgbouncer()
        if self.env is not None and hasattr(self.env, "clear_pgbouncer_endpoint"):
            self.env.clear_pgbouncer_endpoint()

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        if self._history_provider is not None:
            self._history_provider.stop()
            if self.env is not None and hasattr(self.env, "detach_scenario_metric_provider"):
                self.env.detach_scenario_metric_provider(self._history_provider)
            self._history_provider = None
        self._stop_runtime()
        self._stop_pgbouncer()
        if self.env is not None and hasattr(self.env, "clear_pgbouncer_endpoint"):
            self.env.clear_pgbouncer_endpoint()
        case = self.case
        database_cleanup_failure = None
        try:
            if case is not None and self.env is not None:
                with self.env.metrics_hidden():
                    self.env.execute_sql("DROP TABLE IF EXISTS rg_pgbouncer_etl_target, rg_pgbouncer_etl_stage CASCADE;")
                    self.env.execute_sql("DROP TABLE IF EXISTS pgbench_accounts CASCADE;")
                    for user in (*case.pool_users, *(name for name, _ in case.bounded_neighbor_roles)):
                        self.env.execute_sql(f"DROP ROLE IF EXISTS {_sql_identifier(user, 'pool user')};")
        except Exception as exc:
            # PostgreSQL may already be gone after a failed bootstrap. Docker
            # resources still belong to this injector and must be released.
            database_cleanup_failure = exc
        finally:
            self._remove_owned_network()
            self._remove_owned_volume()
            self._remove_runtime_files()
        if database_cleanup_failure is not None:
            raise database_cleanup_failure

    def run_acceptance_replay(self, case: PgBouncerConnectionBudgetCase) -> dict[str, Any]:
        import psycopg2

        if self._acceptance_artifact is not None:
            return dict(self._acceptance_artifact)

        # Check the agent-selected pool mode before starting replay workers. A
        # non-transaction mode is a real policy failure for this case; trying to
        # start protected transaction-boundary neighbors first would turn that
        # model error into a incorrect readiness timeout.
        config_payload = _json_payload(self.env.manage_instance(action="pgbouncer_show_config"))
        config_columns = list(config_payload.get("columns", ()))
        config_key_index = config_columns.index("key") if "key" in config_columns else None
        config_value_index = config_columns.index("value") if "value" in config_columns else None
        if config_key_index is None or config_value_index is None:
            raise RuntimeError(
                "PgBouncer SHOW CONFIG is missing key/value columns: "
                f"columns={config_columns!r}"
            )
        config = {
            str(row[config_key_index]).casefold(): str(row[config_value_index])
            for row in config_payload.get("result", ())
            if len(row) > max(config_key_index, config_value_index)
        }
        pool_mode = config.get("pool_mode", "").casefold()
        if pool_mode != "transaction":
            pools_payload = _json_payload(self.env.manage_instance(action="pgbouncer_show_pools"))
            self._acceptance_artifact = self._replay_failure_for_invalid_pool_mode(
                case,
                pool_mode,
                pools_payload,
                config,
            )
            return dict(self._acceptance_artifact)

        # Quiesce the inherited capture runner before replay pressure starts;
        # otherwise a normal report query can be trapped behind the replay
        # pool budget and cannot be stopped at the observation boundary.
        self._quiesce_inherited_workload_runner()
        self._start_replay_runtime(case)
        runner = self._begin_replay_observation(case)

        protected_payload = _json_payload(
            self.env.execute_sql(
                "SELECT count(*) FROM pg_stat_activity "
                "WHERE backend_type = 'client backend' "
                f"AND datname = '{_escape_sql(case.dbname)}' "
                f"AND application_name = '{_escape_sql(case.report_application)}' "
                "AND state IN ('active', 'idle in transaction');"
            )
        )
        protected_connections = int(protected_payload["result"][0][0]) if protected_payload.get("result") else 0

        duration = float(case.replay_duration_seconds)
        deadline = time.monotonic() + duration
        latencies: list[float] = []
        successes = 0
        attempts = 0
        unexpected_worker_errors: list[str] = []
        ambiguous_worker_errors: list[str] = []
        peak_server_connections = 0
        peak_cpu_percent = 0.0
        previous_cpu_sample: tuple[float, int] | None = None
        next_budget_sample = time.monotonic()
        stats_lock = threading.Lock()

        def _checkout_worker() -> None:
            nonlocal attempts, successes
            local_latencies: list[float] = []
            local_successes = 0
            local_attempts = 0
            local_errors: list[str] = []
            local_ambiguous_errors: list[str] = []
            while time.monotonic() < deadline:
                started = time.monotonic()
                conn = None
                local_attempts += 1
                try:
                    conn = psycopg2.connect(
                        host="127.0.0.1", port=self.pgbouncer_port,
                        user=case.checkout_user, password="password", dbname=case.dbname,
                        connect_timeout=2, application_name=case.checkout_application,
                    )
                    conn.autocommit = True
                    with conn.cursor() as cursor:
                        cursor.execute(
                            f"SELECT pg_sleep({case.replay_hold_seconds}), count(*) FROM pgbench_accounts;"
                        )
                    local_successes += 1
                    local_latencies.append((time.monotonic() - started) * 1000)
                except Exception as exc:
                    failure_class = self._checkout_failure_class(exc)
                    if failure_class == "unexpected":
                        local_errors.append(f"{type(exc).__name__}: {exc}")
                    elif failure_class == "ambiguous":
                        local_ambiguous_errors.append(f"{type(exc).__name__}: {exc}")
                finally:
                    if conn is not None:
                        conn.close()
            with stats_lock:
                attempts += local_attempts
                successes += local_successes
                latencies.extend(local_latencies)
                unexpected_worker_errors.extend(local_errors)
                ambiguous_worker_errors.extend(local_ambiguous_errors)

        worker_count = max(1, int(case.replay_checkout_workers))
        with ThreadPoolExecutor(
            max_workers=worker_count,
            thread_name_prefix="pg-rg-checkout-replay",
        ) as executor:
            futures = [executor.submit(_checkout_worker) for _ in range(worker_count)]
            while time.monotonic() < deadline:
                if time.monotonic() >= next_budget_sample:
                    peak_server_connections, peak_cpu_percent, previous_cpu_sample = self._sample_replay_budget(
                        peak_server_connections, peak_cpu_percent, previous_cpu_sample
                    )
                    next_budget_sample = time.monotonic() + 0.25
                time.sleep(0.02)
            for future in futures:
                try:
                    future.result()
                except Exception as exc:
                    unexpected_worker_errors.append(f"{type(exc).__name__}: {exc}")
        if unexpected_worker_errors or ambiguous_worker_errors:
            try:
                self.env.pgbouncer_admin_query("SHOW POOLS;")
            except Exception as exc:
                unexpected_worker_errors.append(f"endpoint health check: {type(exc).__name__}: {exc}")
            if unexpected_worker_errors:
                raise RuntimeError(
                    "PG-RG-MF01 replay infrastructure: checkout worker/provider error: "
                    + "; ".join((unexpected_worker_errors + ambiguous_worker_errors)[:8])
                )
        with self._etl_lock:
            etl_rows = self._etl_rows_updated
            etl_batches = self._etl_batches
        protected_end_payload = _json_payload(
            self.env.execute_sql(
                "SELECT count(*) FROM pg_stat_activity "
                "WHERE backend_type = 'client backend' "
                f"AND datname = '{_escape_sql(case.dbname)}' "
                f"AND application_name = '{_escape_sql(case.report_application)}' "
                "AND state IN ('active', 'idle in transaction');"
            )
        )
        protected_connections_at_replay_end = (
            int(protected_end_payload["result"][0][0])
            if protected_end_payload.get("result")
            else 0
        )
        # Stop every scenario-owned client before measuring queue convergence.
        # ETL and churn use independent psycopg2 loops, so stopping pgbench alone
        # can leave new clients arriving while SHOW POOLS is being sampled.
        self._stop_runtime()
        self._churn_thread = None
        # The runner may still be finishing report/probe SQL when the fixed
        # replay interval ends. Stop and join it before reading counters so the
        # evaluator artifact and teardown metadata use one complete snapshot.
        observed = self._stop_replay_workload_runner_and_snapshot()
        report_successes = 0
        report_attempts = 0
        health_successes = 0
        health_attempts = 0
        for name in (case.report_profile, case.report_probe_profile):
            values = observed.get(name, {})
            report_successes += int(values.get("successes", 0))
            report_attempts += int(values.get("attempts", 0))
        health_values = observed.get("health_probe", {})
        health_successes = int(health_values.get("successes", 0))
        health_attempts = int(health_values.get("attempts", 0))
        shutdown_clients = _json_payload(self.env.pgbouncer_admin_query("SHOW CLIENTS;"))
        shutdown_pools = _json_payload(self.env.pgbouncer_admin_query("SHOW POOLS;"))
        pools = shutdown_pools
        queue_converged = False
        queue_deadline = time.monotonic() + 5.0
        while time.monotonic() < queue_deadline:
            pools = _json_payload(self.env.manage_instance(action="pgbouncer_show_pools"))
            columns = pools.get("columns", [])
            waiting_index = columns.index("cl_waiting") if "cl_waiting" in columns else None
            waiting = [
                int(row[waiting_index] or 0)
                for row in pools.get("result", ())
                if waiting_index is not None and len(row) > waiting_index
            ]
            if waiting_index is not None and not any(waiting):
                queue_converged = True
                break
            time.sleep(0.25)
        columns = pools.get("columns", [])
        waiting_index = columns.index("cl_waiting") if "cl_waiting" in columns else None
        final_waiting = max(
            (int(row[waiting_index] or 0) for row in pools.get("result", ()) if waiting_index is not None),
            default=0,
        )
        database_payload = _json_payload(
            self.env.execute_sql(
                "SELECT count(*) FROM pg_stat_activity "
                "WHERE backend_type = 'client backend' "
                f"AND datname = '{_escape_sql(case.dbname)}' "
                "AND usename IN ("
                + ", ".join(f"'{_escape_sql(user)}'" for user in case.pool_users)
                + ");"
            )
        )
        max_db_connections = int(database_payload["result"][0][0])
        peak_server_connections, peak_cpu_percent, _ = self._sample_replay_budget(
            peak_server_connections, peak_cpu_percent, previous_cpu_sample
        )
        success_ratio = successes / attempts if attempts else 0.0
        report_ratio = report_successes / report_attempts if report_attempts else 0.0
        artifact = {
            "checkout": {"attempts": attempts, "successes": successes, "success_ratio": success_ratio, "p99_ms": _percentile(latencies, 0.99)},
            "report": {"attempts": report_attempts, "completed": report_successes, "success_ratio": report_ratio},
            "health": {"attempts": health_attempts, "completed": health_successes},
            "etl": {"rows_updated": etl_rows, "batches": etl_batches},
            "database": {
                "max_connections": max_db_connections,
                "peak_server_connections": peak_server_connections,
                "peak_cpu_percent": peak_cpu_percent,
            },
            "protected_neighbor_connections": protected_connections_at_replay_end,
            "protected_neighbor_connections_at_replay_start": protected_connections,
            "protected_neighbor_connections_at_replay_end": protected_connections_at_replay_end,
            "fairness_ratio": min(success_ratio, report_ratio if report_attempts else 0.0, 1.0),
            "queue_converged": queue_converged and final_waiting == 0,
            "final_cl_waiting": final_waiting,
            "final_pools": pools,
            "shutdown_clients": shutdown_clients,
            "pgbench_container_present_after_stop": _docker(
                "inspect", self.pgbench_container, check=False
            ).returncode == 0,
            "duration_seconds": duration,
        }
        self._acceptance_artifact = artifact
        return dict(artifact)

    @staticmethod
    def _checkout_failure_class(exc: Exception) -> str:
        """Classify checkout failures without hiding endpoint/provider failures."""
        if str(getattr(exc, "pgcode", "") or "") == "53300":
            return "expected"
        message = str(exc).casefold()
        if any(
            marker in message
            for marker in (
                "max_user_connections",
                "too many connections",
                "too many clients",
                "no more connections allowed",
                "server login retry",
            )
        ):
            return "expected"
        if "timeout expired" in message or "timeout waiting for connection" in message:
            return "ambiguous"
        return "unexpected"

    @staticmethod
    def _is_expected_checkout_rejection(exc: Exception) -> bool:
        """Compatibility predicate for focused tests and trace explanations."""
        return PgBouncerConnectionBudgetInjector._checkout_failure_class(exc) == "expected"

    def _sample_replay_budget(
        self,
        peak_server_connections: int,
        peak_cpu_percent: float,
        previous_cpu_sample: tuple[float, int] | None,
    ) -> tuple[int, float, tuple[float, int] | None]:
        current_connections = self._pgbouncer_downstream_server_count()
        peak_server_connections = max(peak_server_connections, current_connections)
        read_cpu = getattr(self.env, "_read_cpu_usage_usec", None)
        effective_cpus = getattr(self.env, "_effective_cpus", None)
        if not callable(read_cpu) or not callable(effective_cpus):
            return peak_server_connections, peak_cpu_percent, previous_cpu_sample
        now = time.monotonic()
        current_cpu = int(read_cpu())
        if previous_cpu_sample is not None:
            previous_time, previous_value = previous_cpu_sample
            elapsed = now - previous_time
            cpus = float(effective_cpus())
            if elapsed > 0 and cpus > 0 and current_cpu >= previous_value:
                peak_cpu_percent = max(
                    peak_cpu_percent,
                    min(
                        100.0,
                        round((current_cpu - previous_value) / (elapsed * 1_000_000 * cpus) * 100.0, 2),
                    ),
                )
        return peak_server_connections, peak_cpu_percent, (now, current_cpu)

    def _pgbouncer_downstream_server_count(self) -> int:
        """Count PgBouncer-to-PostgreSQL server sessions for the target database."""
        payload = _json_payload(self.env.pgbouncer_admin_query("SHOW SERVERS;"))
        columns = list(payload.get("columns", ()))
        if "database" not in columns:
            raise RuntimeError(
                "PG-RG-MF01 replay infrastructure: SHOW SERVERS is missing database column: "
                f"columns={columns!r}"
            )
        database_index = columns.index("database")
        return sum(
            1
            for row in payload.get("result", ())
            if len(row) > database_index
            and str(row[database_index]) == str(self.case.dbname)
        )

    def _create_database_objects(
        self,
        case: PgBouncerConnectionBudgetCase,
        *,
        checkout_role_connection_limit: int | None = None,
    ) -> None:
        checkout_role_connection_limit = (
            case.normal_checkout_role_connection_limit
            if checkout_role_connection_limit is None
            else int(checkout_role_connection_limit)
        )
        if checkout_role_connection_limit <= 0 or case.other_role_connection_limit <= 0:
            raise ValueError("RG1 role connection limits must be positive and bounded")
        for user in case.pool_users:
            identifier = _sql_identifier(user, "pool user")
            self.env.execute_sql(
                f"DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{_escape_sql(user)}') "
                f"THEN CREATE ROLE {identifier} LOGIN PASSWORD 'password'; ELSE ALTER ROLE {identifier} LOGIN PASSWORD 'password'; END IF; END $$;"
            )
            role_connection_limit = (
                checkout_role_connection_limit
                if user == case.checkout_user
                else case.other_role_connection_limit
            )
            self.env.execute_sql(
                f"ALTER ROLE {identifier} CONNECTION LIMIT {int(role_connection_limit)};"
            )
            self.env.execute_sql(f"GRANT CONNECT ON DATABASE {_sql_identifier(case.dbname, 'dbname')} TO {identifier};")
        # Deliberately bounded neighbor roles: real catalogs contain limited
        # LOGIN roles whose limits are intentional (background batch roles,
        # retired service roles). A low rolconnlimit is only evidence when it
        # contradicts the role's pool demand, so locating the incident
        # partition requires cross-checking pools and activity per role.
        for neighbor_user, neighbor_limit in case.bounded_neighbor_roles:
            neighbor_identifier = _sql_identifier(neighbor_user, "bounded neighbor user")
            self.env.execute_sql(
                f"DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{_escape_sql(neighbor_user)}') "
                f"THEN CREATE ROLE {neighbor_identifier} LOGIN PASSWORD 'password'; "
                f"ELSE ALTER ROLE {neighbor_identifier} LOGIN PASSWORD 'password'; END IF; END $$;"
            )
            self.env.execute_sql(
                f"ALTER ROLE {neighbor_identifier} CONNECTION LIMIT {int(neighbor_limit)};"
            )
            self.env.execute_sql(
                f"GRANT CONNECT ON DATABASE {_sql_identifier(case.dbname, 'dbname')} TO {neighbor_identifier};"
            )
        self.env.execute_sql(
            "CREATE TABLE IF NOT EXISTS pgbench_accounts "
            "(aid integer PRIMARY KEY, bid integer NOT NULL, abalance integer NOT NULL, filler text NOT NULL);"
        )
        self.env.execute_sql(
            "INSERT INTO pgbench_accounts (aid, bid, abalance, filler) "
            "SELECT g, g % 10, 0, repeat('x', 20) FROM generate_series(1, 1000) g ON CONFLICT (aid) DO NOTHING;"
        )
        self.env.execute_sql(
            "CREATE TABLE IF NOT EXISTS rg_pgbouncer_etl_stage "
            "(id bigint PRIMARY KEY, payload text NOT NULL, loaded_at timestamptz DEFAULT clock_timestamp());"
        )
        self.env.execute_sql(
            "CREATE TABLE IF NOT EXISTS rg_pgbouncer_etl_target "
            "(id bigint PRIMARY KEY, payload text NOT NULL, updated_at timestamptz DEFAULT clock_timestamp());"
        )
        grant_users = ", ".join(_sql_identifier(user, "pool user") for user in case.pool_users)
        self.env.execute_sql(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {grant_users};")
        self.env.execute_sql(
            f"GRANT INSERT, UPDATE, SELECT ON rg_pgbouncer_etl_stage, rg_pgbouncer_etl_target TO "
            f"{_sql_identifier(case.etl_user, 'etl user')};"
        )

    def _create_network(self) -> None:
        if _docker("network", "inspect", self.network, check=False).returncode != 0:
            result = _docker(
                "network", "create", "--label", "aiopsbench.owner=pg-rg-pgbouncer", self.network,
                check=False,
            )
            if result.returncode != 0:
                # Busy hosts can exhaust Docker's default address pool while
                # still allowing explicitly allocated private subnets.
                seed = int(hashlib.sha256(self.network.encode()).hexdigest()[:8], 16)
                created = False
                errors = []
                for offset in range(64):
                    subnet_octet = 8 + ((seed + offset) % 240)
                    subnet = f"10.250.{subnet_octet}.0/24"
                    candidate = _docker(
                        "network", "create", "--subnet", subnet,
                        "--label", "aiopsbench.owner=pg-rg-pgbouncer", self.network,
                        check=False,
                    )
                    if candidate.returncode == 0:
                        created = True
                        break
                    errors.append(f"{subnet}: {candidate.stderr.strip()}")
                if not created:
                    raise RuntimeError(
                        "Unable to create PgBouncer network using Docker default or explicit private subnets: "
                        f"network={self.network!r}, default_error={result.stderr.strip()!r}, "
                        f"explicit_errors={errors[-3:]!r}"
                    )
        connected = _docker("network", "inspect", self.network, "--format", "{{json .Containers}}", check=False)
        if self.pg_container in connected.stdout:
            _docker("network", "disconnect", "-f", self.network, self.pg_container, check=False)
        _docker("network", "connect", "--alias", "postgres", self.network, self.pg_container)

    def _build_fault_image(self, case: PgBouncerConnectionBudgetCase) -> None:
        if _docker("image", "inspect", case.pgbouncer_fault_image, check=False).returncode == 0:
            return
        project_root = Path(__file__).resolve().parents[4]
        _docker("build", "-t", case.pgbouncer_fault_image, "-f", str(project_root / PGBOUNCER_DOCKERFILE), str(project_root), timeout=600)

    def _write_runtime_files(
        self,
        case: PgBouncerConnectionBudgetCase,
        *,
        runtime_max_database_connections: int | None = None,
    ) -> None:
        runtime_budget = (
            case.initial_runtime_max_database_connections
            if runtime_max_database_connections is None
            else int(runtime_max_database_connections)
        )
        config = f"""[databases]
{case.dbname} = host=postgres port=5432 dbname={case.dbname}

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = plain
auth_file = /etc/pgbouncer/userlist.txt
admin_users = postgres
stats_users = postgres
pool_mode = transaction
default_pool_size = {case.initial_pool_size}
reserve_pool_size = {case.initial_reserve_pool_size}
reserve_pool_timeout = 1
max_client_conn = {case.max_client_connections}
max_db_connections = {runtime_budget}
logfile = /dev/stderr
pidfile = /tmp/pgbouncer.pid
ignore_startup_parameters = extra_float_digits
"""
        config_file = tempfile.NamedTemporaryFile(prefix="aiopsbench-pgbouncer-", suffix=".ini", mode="w", delete=False)
        config_file.write(config)
        config_file.close()
        os.chmod(config_file.name, 0o644)
        auth_file = tempfile.NamedTemporaryFile(prefix="aiopsbench-pgbouncer-", suffix=".users", mode="w", delete=False)
        for user in ("postgres", *case.pool_users):
            auth_file.write(f'"{user}" "password"\n')
        auth_file.close()
        os.chmod(auth_file.name, 0o644)
        checkout_script = tempfile.NamedTemporaryFile(prefix="aiopsbench-pgbouncer-", suffix=".sql", mode="w", delete=False)
        checkout_script.write("BEGIN; SELECT pg_sleep(0.08), count(*) FROM pgbench_accounts; COMMIT;\n")
        checkout_script.close()
        os.chmod(checkout_script.name, 0o644)
        self._config_file, self._auth_file, self._checkout_script = config_file.name, auth_file.name, checkout_script.name
        self._record_event(
            event_type="config_revision",
            entity_type="pooler_config",
            entity="pgbouncer",
            action="stage",
            details={
                "revision": "rg1-runtime",
                "max_db_connections": runtime_budget,
                "pool_mode": "transaction",
                "default_pool_size": case.initial_pool_size,
                "checkout_role": case.checkout_user,
                "checkout_role_connection_limit": (
                    case.target_checkout_role_connection_limit
                    if runtime_budget == case.max_database_connections
                    else case.normal_checkout_role_connection_limit
                ),
            },
        )

    def _start_pgbouncer(self, case: PgBouncerConnectionBudgetCase) -> None:
        import psycopg2

        _docker("volume", "create", "--label", "aiopsbench.owner=pg-rg-pgbouncer", self.volume, check=False)
        _docker(
            "run", "-d", "--name", self.pgbouncer_container,
            "--label", "aiopsbench.owner=pg-rg-pgbouncer", "--network", self.network,
            "--network-alias", "pooler",
            "-p", f"{self.pgbouncer_port}:6432", "-v", f"{self.volume}:/var/log/pgbouncer",
            "-v", f"{self._config_file}:/etc/pgbouncer/pgbouncer.ini:ro",
            "-v", f"{self._auth_file}:/etc/pgbouncer/userlist.txt:ro",
            case.pgbouncer_fault_image, "/etc/pgbouncer/pgbouncer.ini",
        )
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            conn = None
            try:
                conn = psycopg2.connect(
                    host="127.0.0.1", port=self.pgbouncer_port,
                    user="postgres", password="password", dbname="pgbouncer",
                    connect_timeout=2,
                )
                conn.close()
                self._record_event(
                    event_type="client_lifecycle",
                    entity_type="pooler",
                    entity="pgbouncer",
                    action="ready",
                    details={"container": self.pgbouncer_container, "port": self.pgbouncer_port},
                )
                return
            except Exception as exc:
                if conn is not None:
                    conn.close()
            time.sleep(0.5)
        logs = _docker("logs", self.pgbouncer_container, check=False).stderr.strip()
        raise RuntimeError(
            f"PgBouncer did not become ready: container={self.pgbouncer_container}, logs={logs[-2000:]!r}"
        )

    def _configure_environment_endpoints(self, case: PgBouncerConnectionBudgetCase) -> None:
        self.env.configure_pgbouncer_endpoint("127.0.0.1", self.pgbouncer_port)
        for pool, user in (("checkout", case.checkout_user), ("reporting", case.report_user), ("etl", case.etl_user)):
            self.env.configure_workload_connection_pool(
                pool, "127.0.0.1", self.pgbouncer_port,
                user=user, password="password", dbname=case.dbname,
            )
        self._record_event(
            event_type="client_lifecycle",
            entity_type="endpoint",
            entity="workload_routes",
            action="configure",
            details={"pools": ["checkout", "reporting", "etl"]},
        )

    def _remove_owned_pgbench_container(self, container_name: str) -> None:
        if not self.pgbench_container:
            raise RuntimeError(
                f"Cannot clean pgbench container before injector configuration: name={container_name!r}"
            )
        is_base_name = container_name == self.pgbench_container
        is_ramp_name = re.fullmatch(
            rf"{re.escape(self.pgbench_container)}-ramp-[0-9]+",
            container_name,
        ) is not None
        if not (is_base_name or is_ramp_name):
            raise ValueError(
                "Refusing to remove a non-owned PgBouncer pgbench container: "
                f"container_name={container_name!r}, owned_base={self.pgbench_container!r}"
            )
        _docker("rm", "-f", container_name, check=False)

    def _launch_pgbench_container(
        self,
        case: PgBouncerConnectionBudgetCase,
        *,
        container_name: str,
        clients: int,
        stage: str,
        total_clients: int,
    ) -> None:
        if clients <= 0:
            return
        self._remove_owned_pgbench_container(container_name)
        _docker(
            "run", "-d", "--name", container_name,
            "--label", "aiopsbench.owner=pg-rg-pgbouncer", "--network", self.network,
            "-e", "PGPASSWORD=password", "-v", f"{self._checkout_script}:/tmp/checkout.sql:ro",
            "postgres:16", "pgbench", "-h", "pooler", "-p", "6432",
            "-U", case.checkout_user, "-d", case.dbname, "-f", "/tmp/checkout.sql",
            "-c", str(clients), "-j", str(min(4, clients)), "-T", "86400", "-P", "1",
            "--no-vacuum",
            timeout=120,
        )
        self._pgbench_containers.append(container_name)
        self._record_event(
            event_type="job_stage",
            entity_type="workload",
            entity="checkout",
            action="start",
            details={
                "clients": clients,
                "total_clients": total_clients,
                "pool": "checkout",
                "stage": stage,
            },
            target=f"{case.dbname}/{case.checkout_user}",
        )

    def _start_pgbench(
        self,
        case: PgBouncerConnectionBudgetCase,
        *,
        clients: int | None = None,
        ramp_target: bool = False,
    ) -> None:
        initial_clients = int(case.checkout_clients if clients is None else clients)
        initial_clients = max(1, min(initial_clients, case.checkout_clients))
        self._launch_pgbench_container(
            case,
            container_name=self.pgbench_container,
            clients=initial_clients,
            stage="initial",
            total_clients=initial_clients,
        )
        self._pgbench_started = True
        if not ramp_target or case.simple or initial_clients >= case.checkout_clients:
            return
        remaining = case.checkout_clients - initial_clients
        stages = (
            (120, min(1, remaining)),
            (240, min(1, max(0, remaining - 1))),
            (360, max(0, remaining - 2)),
        )
        self._pgbench_ramp_thread = threading.Thread(
            target=self._pgbench_ramp_loop,
            args=(case, stages, initial_clients),
            name="pg-rg-pgbouncer-pgbench-ramp",
            daemon=True,
        )
        self._pgbench_ramp_thread.start()
        self._threads.append(self._pgbench_ramp_thread)

    def _pgbench_ramp_loop(
        self,
        case: PgBouncerConnectionBudgetCase,
        stages: tuple[tuple[int, int], ...],
        total_clients: int,
    ) -> None:
        ramp_started_at = time.monotonic()
        for index, (delay_seconds, clients) in enumerate(stages, start=1):
            remaining_delay = max(0.0, float(delay_seconds) - (time.monotonic() - ramp_started_at))
            if clients <= 0 or self._stop_event.wait(remaining_delay):
                return
            container_name = f"{self.pgbench_container}-ramp-{index}"
            try:
                self._launch_pgbench_container(
                    case,
                    container_name=container_name,
                    clients=clients,
                    stage=f"ramp-{index}",
                    total_clients=total_clients + clients,
                )
                total_clients += clients
                if self._stop_event.is_set():
                    _docker("rm", "-f", container_name, check=False)
            except Exception as exc:
                self._record_capture_error("checkout ramp", exc)
                self._record_event(
                    event_type="job_stage",
                    entity_type="workload",
                    entity="checkout",
                    action="ramp_failed",
                    status="error",
                    details={"stage": f"ramp-{index}", "error": str(exc)},
                    target=f"{case.dbname}/{case.checkout_user}",
                )
                return

    def _start_connection_churn(self, case: PgBouncerConnectionBudgetCase) -> None:
        if case.churn_connections <= 0:
            return
        thread = threading.Thread(
            target=self._connection_churn_loop,
            args=(case,),
            name="pg-rg-pgbouncer-churn",
            daemon=True,
        )
        self._churn_thread = thread
        thread.start()
        self._threads.append(thread)
        self._record_event(
            event_type="client_lifecycle",
            entity_type="workload",
            entity="connection_churn",
            action="start",
            details={"connections_per_cycle": case.churn_connections},
            target=f"{case.dbname}/{case.checkout_user}",
        )

    def _start_staged_auxiliary_read(
        self,
        case: PgBouncerConnectionBudgetCase,
        *,
        burst_workers: int = 4,
        record_schedule: bool = False,
    ) -> None:
        if case.simple or self._staged_auxiliary_thread is not None:
            return
        self._stop_event.clear()
        thread = threading.Thread(
            target=self._staged_auxiliary_read_loop,
            args=(case, int(burst_workers)),
            name="pg-rg-pgbouncer-staged-checkout-auxiliary",
            daemon=True,
        )
        self._staged_auxiliary_thread = thread
        thread.start()
        self._threads.append(thread)
        if record_schedule:
            self._record_event(
                event_type="client_lifecycle",
                entity_type="workload",
                entity="checkout_auxiliary",
                action="schedule",
                details={
                    "pool": "checkout",
                    "application": "checkout-api-11",
                    "period_seconds": 120,
                    "burst_seconds": 60,
                    "concurrent_clients": int(burst_workers),
                    "query_seconds": 0.30,
                    "baseline_qps": 0.05,
                    "burst_qps": 0.90,
                },
                target=f"{case.dbname}/{case.checkout_user}",
            )

    def _start_capture_report_noise(
        self,
        case: PgBouncerConnectionBudgetCase,
        *,
        target_budget: bool,
    ) -> None:
        if case.simple or self._target_report_noise_thread is not None:
            return
        self._stop_event.clear()
        thread = threading.Thread(
            target=self._target_report_noise_loop,
            args=(case, 4 if not target_budget else 2),
            name="pg-rg-pgbouncer-target-report-noise",
            daemon=True,
        )
        self._target_report_noise_thread = thread
        thread.start()
        self._threads.append(thread)
        self._record_event(
            event_type="client_lifecycle",
            entity_type="workload",
            entity="reporting_bounded_burst",
            action="start",
            details={
                "pool": "reporting",
                "application": case.long_report_application,
                "period_seconds": 120,
                "burst_seconds": 45,
                "concurrent_clients": 4 if not target_budget else 2,
                "query_seconds": 0.30,
                "capture_only": True,
                "capture_phase": "target" if target_budget else "normal",
            },
            target=f"{case.dbname}/{case.report_user}",
        )

    def _target_report_noise_loop(
        self,
        case: PgBouncerConnectionBudgetCase,
        concurrent_clients: int = 2,
    ) -> None:
        """Add a bounded reporting burst that recovers inside each capture."""
        started_at = time.monotonic()
        burst_period_seconds = 120.0
        burst_duration_seconds = 45.0
        while not self._stop_event.is_set():
            phase = (time.monotonic() - started_at) % burst_period_seconds
            burst = phase < burst_duration_seconds
            workers = int(concurrent_clients) if burst else 0
            if workers:
                with ThreadPoolExecutor(
                    max_workers=workers,
                    thread_name_prefix="pg-rg-report-noise",
                ) as executor:
                    futures = [
                        executor.submit(self._run_target_report_noise_query, case)
                        for _ in range(workers)
                    ]
                    for future in futures:
                        try:
                            future.result()
                        except Exception as exc:
                            self._record_capture_error(
                                "target report noise",
                                exc,
                                expected=self._is_expected_connection_failure(exc)
                                or self._is_expected_target_timeout(exc),
                            )
            self._stop_event.wait(1.0 if burst else max(1.0, burst_period_seconds - phase))

    def _start_target_checkout_noise(self, case: PgBouncerConnectionBudgetCase) -> None:
        if case.simple or self._target_checkout_noise_thread is not None:
            return
        self._stop_event.clear()
        thread = threading.Thread(
            target=self._target_checkout_noise_loop,
            args=(case,),
            name="pg-rg-pgbouncer-target-checkout-noise",
            daemon=True,
        )
        self._target_checkout_noise_thread = thread
        thread.start()
        self._threads.append(thread)
        self._record_event(
            event_type="client_lifecycle",
            entity_type="workload",
            entity="checkout_bounded_burst",
            action="start",
            details={
                "pool": "checkout",
                "application": "checkout-api-11-burst",
                "period_seconds": 90,
                "burst_seconds": 30,
                "concurrent_clients": 4,
                "query_seconds": 0.30,
                "capture_only": True,
            },
            target=f"{case.dbname}/{case.checkout_user}",
        )

    def _target_checkout_noise_loop(self, case: PgBouncerConnectionBudgetCase) -> None:
        """Add a recoverable same-pool checkout burst beside the target ramp."""
        started_at = time.monotonic()
        burst_period_seconds = 90.0
        burst_duration_seconds = 30.0
        while not self._stop_event.is_set():
            phase = (time.monotonic() - started_at) % burst_period_seconds
            burst = phase < burst_duration_seconds
            workers = 4 if burst else 0
            if workers:
                with ThreadPoolExecutor(
                    max_workers=workers,
                    thread_name_prefix="pg-rg-checkout-noise",
                ) as executor:
                    futures = [
                        executor.submit(self._run_target_checkout_noise_query, case)
                        for _ in range(workers)
                    ]
                    for future in futures:
                        try:
                            future.result()
                        except Exception as exc:
                            self._record_capture_error(
                                "target checkout noise",
                                exc,
                                expected=self._is_expected_connection_failure(exc)
                                or self._is_expected_target_timeout(exc),
                            )
            self._stop_event.wait(1.0 if burst else max(1.0, burst_period_seconds - phase))

    def _run_target_checkout_noise_query(self, case: PgBouncerConnectionBudgetCase) -> None:
        import psycopg2

        conn = None
        try:
            conn = psycopg2.connect(
                host="127.0.0.1", port=self.pgbouncer_port,
                user=case.checkout_user, password="password", dbname=case.dbname,
                connect_timeout=2, application_name="checkout-api-11-burst",
            )
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_sleep(0.30), count(*) FROM pgbench_accounts "
                    "WHERE aid BETWEEN 901 AND 950;"
                )
        finally:
            if conn is not None:
                conn.close()

    def _run_target_report_noise_query(self, case: PgBouncerConnectionBudgetCase) -> None:
        import psycopg2

        conn = None
        try:
            conn = psycopg2.connect(
                host="127.0.0.1", port=self.pgbouncer_port,
                user=case.report_user, password="password", dbname=case.dbname,
                connect_timeout=2, application_name=case.long_report_application,
            )
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_sleep(0.30), count(*) FROM pgbench_accounts "
                    "WHERE aid BETWEEN 1 AND 250;"
                )
        finally:
            if conn is not None:
                conn.close()

    def _staged_auxiliary_read_loop(self, case: PgBouncerConnectionBudgetCase, burst_workers: int = 4) -> None:
        """Create periodic, bounded same-pool bursts with recovery between them."""
        started_at = time.monotonic()
        burst_period_seconds = 120.0
        burst_duration_seconds = 60.0
        while not self._stop_event.is_set():
            phase = (time.monotonic() - started_at) % burst_period_seconds
            burst = phase < burst_duration_seconds
            qps = 0.90 if burst else 0.05
            workers = max(1, int(burst_workers)) if burst else 1
            with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="pg-rg-aux") as executor:
                futures = [executor.submit(self._run_staged_auxiliary_query, case) for _ in range(workers)]
                for future in futures:
                    try:
                        future.result()
                    except Exception as exc:
                        self._record_capture_error(
                            "checkout auxiliary",
                            exc,
                            expected=self._is_expected_connection_failure(exc)
                            or self._is_expected_target_timeout(exc),
                        )
            self._stop_event.wait(workers / qps)

    def _run_staged_auxiliary_query(self, case: PgBouncerConnectionBudgetCase) -> None:
        import psycopg2

        conn = None
        try:
            conn = psycopg2.connect(
                host="127.0.0.1", port=self.pgbouncer_port,
                user=case.checkout_user, password="password", dbname=case.dbname,
                connect_timeout=2, application_name="checkout-api-11",
            )
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_sleep(0.30), count(*) FROM pgbench_accounts "
                    "WHERE aid BETWEEN 901 AND 950;"
                )
        finally:
            if conn is not None:
                conn.close()

    def _start_protected_neighbors(self, case: PgBouncerConnectionBudgetCase) -> None:
        if case.protected_neighbor_connections <= 0:
            return
        self._stop_event.clear()
        with self._etl_lock:
            self._protected_ready_count = 0
            self._protected_errors.clear()
        for index in range(case.protected_neighbor_connections):
            thread = threading.Thread(
                target=self._protected_neighbor_loop,
                args=(case, index),
                name=f"pg-rg-pgbouncer-protected-{index}",
                daemon=True,
            )
            thread.start()
            self._threads.append(thread)
        self._record_event(
            event_type="client_lifecycle",
            entity_type="workload",
            entity="protected_reporting",
            action="hold",
            details={"connections": case.protected_neighbor_connections},
            target=f"{case.dbname}/{case.report_user}",
        )

    def _protected_neighbor_loop(self, case: PgBouncerConnectionBudgetCase, index: int) -> None:
        import psycopg2

        conn = None
        held = False
        try:
            deadline = time.monotonic() + 20.0
            while not self._stop_event.is_set() and time.monotonic() < deadline:
                try:
                    conn = psycopg2.connect(
                        host="127.0.0.1", port=self.pgbouncer_port,
                        user=case.report_user, password="password", dbname=case.dbname,
                        connect_timeout=3,
                        application_name=case.report_application,
                    )
                    with conn.cursor() as cursor:
                        cursor.execute("BEGIN;")
                        cursor.execute("SELECT current_timestamp;")
                    with self._etl_lock:
                        self._protected_connections.append(conn)
                        self._protected_ready_count += 1
                    held = True
                    return
                except Exception as exc:
                    with self._etl_lock:
                        self._protected_errors.append(f"{type(exc).__name__}: {exc}")
                    if conn is not None:
                        try:
                            conn.close()
                        except Exception:
                            pass
                        conn = None
                    time.sleep(0.15)
        finally:
            if conn is not None and not held:
                try:
                    conn.close()
                except Exception:
                    pass

    def _connection_churn_loop(self, case: PgBouncerConnectionBudgetCase) -> None:
        import psycopg2

        started_at = time.monotonic()
        burst_period_seconds = 30.0
        burst_duration_seconds = 10.0
        while not self._stop_event.is_set():
            phase = (time.monotonic() - started_at) % burst_period_seconds
            burst = phase < burst_duration_seconds
            burst_size = max(4, case.churn_connections // 6) if burst else 1
            for index in range(burst_size):
                if self._stop_event.is_set():
                    return
                conn = None
                connected = False
                with self._churn_lock:
                    self._churn_connects += 1
                try:
                    conn = psycopg2.connect(
                        host="127.0.0.1", port=self.pgbouncer_port,
                        user=case.checkout_user, password="password", dbname=case.dbname,
                        connect_timeout=2,
                        application_name=f"{case.checkout_application}-churn-{index}",
                    )
                    connected = True
                    conn.autocommit = True
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1;")
                except Exception as exc:
                    self._record_capture_error(
                        "connection churn",
                        exc,
                        expected=self._is_expected_connection_failure(exc)
                        or self._is_expected_target_timeout(exc),
                    )
                    pass
                finally:
                    if conn is not None:
                        conn.close()
                        if connected:
                            with self._churn_lock:
                                self._churn_disconnects += 1
                if self._stop_event.wait(0.05 if burst else 0.25):
                    return

    def _start_etl(
        self,
        case: PgBouncerConnectionBudgetCase,
        *,
        checkpoint_pause: bool = False,
    ) -> None:
        self._stop_event.clear()
        thread = threading.Thread(
            target=self._etl_loop,
            args=(case, checkpoint_pause),
            name="pg-rg-pgbouncer-etl",
            daemon=True,
        )
        thread.start()
        self._threads.append(thread)
        self._record_event(
            event_type="job_stage",
            entity_type="workload",
            entity="etl",
            action="start",
            details={"batch_size": case.etl_batch_size, "pool": "etl"},
            target=f"{case.dbname}/{case.etl_user}",
        )

    def _seed_pool_connections(self, case: PgBouncerConnectionBudgetCase) -> None:
        import psycopg2

        for user in case.pool_users:
            try:
                conn = psycopg2.connect(
                    host="127.0.0.1", port=self.pgbouncer_port,
                    user=user, password="password", dbname=case.dbname,
                    connect_timeout=3, application_name=f"{case.report_application}-pool-seed",
                )
                conn.autocommit = True
                self._seed_connections.append(conn)
            except Exception as exc:
                logs = _docker("logs", self.pgbouncer_container, check=False)
                log_text = (logs.stdout + logs.stderr).strip()
                raise RuntimeError(
                    f"Failed to seed PgBouncer pool: user={user!r}, error={exc!r}, logs={log_text[-2000:]!r}"
                ) from exc

    def _etl_loop(self, case: PgBouncerConnectionBudgetCase, checkpoint_pause: bool = False) -> None:
        import psycopg2

        completed_batches = 0
        checkpoint_pause_done = False
        # Keep the benign maintenance phase inside the normal capture while
        # making its placement independent of database batch throughput.
        checkpoint_pause_at = time.monotonic() + 45.0
        while not self._stop_event.is_set():
            conn = None
            try:
                with self._etl_lock:
                    next_id = self._etl_next_id
                conn = psycopg2.connect(
                    host="127.0.0.1", port=self.pgbouncer_port,
                    user=case.etl_user, password="password", dbname=case.dbname,
                    connect_timeout=3, application_name=case.etl_application,
                )
                with conn.cursor() as cursor:
                    rows = [(next_id + offset, f"etl-{next_id + offset}") for offset in range(case.etl_batch_size)]
                    cursor.copy_expert(
                        "COPY rg_pgbouncer_etl_stage (id, payload) FROM STDIN WITH (FORMAT csv)",
                        StringIO("".join(f"{row_id},{payload}\n" for row_id, payload in rows)),
                    )
                    cursor.execute(
                        "UPDATE rg_pgbouncer_etl_target target SET payload = stage.payload, updated_at = clock_timestamp() "
                        "FROM rg_pgbouncer_etl_stage stage WHERE target.id = stage.id AND stage.id BETWEEN %s AND %s",
                        (next_id, next_id + case.etl_batch_size - 1),
                    )
                    cursor.execute(
                        "INSERT INTO rg_pgbouncer_etl_target (id, payload) SELECT stage.id, stage.payload "
                        "FROM rg_pgbouncer_etl_stage stage WHERE stage.id BETWEEN %s AND %s ON CONFLICT (id) DO NOTHING",
                        (next_id, next_id + case.etl_batch_size - 1),
                    )
                conn.commit()
                with self._etl_lock:
                    self._etl_rows_updated += case.etl_batch_size
                    self._etl_batches += 1
                    self._etl_next_id = next_id + case.etl_batch_size
                completed_batches += 1
                if checkpoint_pause and not checkpoint_pause_done and time.monotonic() >= checkpoint_pause_at:
                    checkpoint_pause_done = True
                    self._record_event(
                        event_type="job_stage",
                        entity_type="workload",
                        entity="etl",
                        action="checkpoint_pause",
                        details={
                            "duration_seconds": 20,
                            "capture_only": True,
                            "reason": "scheduled ETL checkpoint",
                        },
                        target=f"{case.dbname}/{case.etl_user}",
                    )
                    if self._stop_event.wait(20.0):
                        return
                next_id += case.etl_batch_size
            except Exception as exc:
                if conn is not None:
                    try:
                        conn.rollback()
                    except Exception:
                        # Teardown can close PostgreSQL while a COPY is in flight.
                        pass
                self._record_capture_error(
                    "ETL workload",
                    exc,
                    expected=self._is_expected_connection_failure(exc)
                    or self._is_expected_target_timeout(exc),
                )
                time.sleep(0.15)
            finally:
                if conn is not None:
                    conn.close()
            time.sleep(0.05)

    def _wait_until_fault_ready(self, case: PgBouncerConnectionBudgetCase, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        last = None
        while time.monotonic() < deadline:
            try:
                payload = _json_payload(self.env.manage_instance(action="pgbouncer_show_pools"))
                columns = payload.get("columns", [])
                last = payload
                users = {
                    (str(row[columns.index("database")]), str(row[columns.index("user")]))
                    for row in payload.get("result", ())
                    if "database" in columns and "user" in columns
                    and len(row) > max(columns.index("database"), columns.index("user"))
                }
                if {(case.dbname, user) for user in case.pool_users}.issubset(users):
                    if case.protected_neighbor_connections:
                        with self._etl_lock:
                            protected_ready = self._protected_ready_count
                        if protected_ready < case.protected_neighbor_connections:
                            time.sleep(0.25)
                            continue
                    return
            except Exception:
                pass
            time.sleep(0.5)
        with self._etl_lock:
            protected_ready = self._protected_ready_count
            protected_errors = list(self._protected_errors[-3:])
        raise RuntimeError(
            "PgBouncer fault-ready check timed out: "
            f"last_pools={last!r}, protected_ready={protected_ready}, "
            f"protected_errors={protected_errors!r}"
        )

    def _preflight_ports(self, allow_pgbouncer: bool = False) -> None:
        for name, port in (("postgres", self.postgres_port), ("pgbouncer", self.pgbouncer_port)):
            if allow_pgbouncer and name == "pgbouncer":
                continue
            if name == "postgres" and _port_owned_by_container(port, self.pg_container):
                continue
            if not _port_available(port):
                raise RuntimeError(f"Required scenario port is already in use: name={name}, port={port}")

    def _stop_runtime(self) -> None:
        self._stop_event.set()
        # A ramp can be inside its bounded Docker remove/start sequence.
        # Join it before removing the containers it registers.
        if self._pgbench_ramp_thread is not None:
            self._pgbench_ramp_thread.join(timeout=250)
            if self._pgbench_ramp_thread.is_alive():
                raise RuntimeError(
                    "PG-RG-MF01 teardown infrastructure: pgbench ramp did not stop "
                    "after its Docker command deadlines"
                )
        self._stop_pgbench()
        for conn in self._protected_connections:
            try:
                conn.close()
            except Exception:
                pass
        self._protected_connections.clear()
        # A churn burst sweeps several bounded connects before re-checking
        # the stop event; allow one full sweep to finish instead of failing
        # teardown on scheduler jitter.
        for thread in self._threads:
            thread.join(timeout=30)
        alive_threads = [thread.name for thread in self._threads if thread.is_alive()]
        self._threads.clear()
        self._staged_auxiliary_thread = None
        self._target_report_noise_thread = None
        self._target_checkout_noise_thread = None
        for conn in self._seed_connections:
            try:
                conn.close()
            except Exception:
                pass
        self._seed_connections.clear()
        if alive_threads:
            raise RuntimeError(
                "PG-RG-MF01 teardown infrastructure: scenario-owned worker did not stop: "
                + ", ".join(alive_threads)
            )

    def _stop_pgbench(self) -> None:
        for container_name in tuple(self._pgbench_containers):
            _docker("rm", "-f", container_name, check=False)
        self._pgbench_containers.clear()
        self._pgbench_ramp_thread = None
        self._pgbench_started = False

    def _stop_pgbouncer(self) -> None:
        _docker("rm", "-f", self.pgbouncer_container, check=False)

    def _cleanup_owned_runtime(self) -> None:
        self._stop_runtime()
        self._stop_pgbouncer()
        self._remove_owned_network()
        self._remove_owned_volume()
        self._remove_runtime_files()

    def _remove_owned_network(self) -> None:
        _docker("network", "disconnect", "-f", self.network, self.pg_container, check=False)
        _docker("network", "rm", self.network, check=False)

    def _remove_owned_volume(self) -> None:
        _docker("volume", "rm", self.volume, check=False)

    def _remove_runtime_files(self) -> None:
        for path in (self._config_file, self._auth_file, self._checkout_script):
            if path:
                try:
                    os.unlink(path)
                except FileNotFoundError:
                    pass
        self._config_file = self._auth_file = self._checkout_script = None

def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return float("inf")
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int((len(ordered) - 1) * percentile)))
    return round(ordered[index], 3)


def _cpu_percent(raw: object) -> float:
    try:
        payload = json.loads(raw) if isinstance(raw, str) else raw
        if isinstance(payload, dict):
            for key in ("value", "cpu_percent", "usage_percent"):
                if isinstance(payload.get(key), (int, float)):
                    return float(payload[key])
    except (TypeError, ValueError, json.JSONDecodeError):
        pass
    return 0.0


def _report(case_id: str) -> dict[str, object]:
    return {
        "diagnosis": {"conditions": []},
        "outcome": {"changes": [f"governed PgBouncer budgets for {case_id}"], "verification": ["completed real mixed workload replay"]},
        "summary": "Connection budget governance was validated by a real workload replay.",
    }


def _make_case(*, case_id: str, case_no: int, evaluator: type, simple: bool, reference_run_id: str) -> PgBouncerConnectionBudgetCase:
    case_type = (
        PgResourceGovernancePgbouncerConnectionBudgetForPoolPartitionShortageSimpleScenarioCase
        if simple
        else PgResourceGovernancePgbouncerConnectionBudgetForPoolPartitionShortageScenarioCase
    )
    history_spec = None if simple else FrozenHistorySpec(
        schema_version=1,
        duration_seconds=12 * 60 * 60,
        normal_capture_seconds=120,
        fault_capture_seconds=180,
        base_step_seconds=2,
        overview_step_seconds=20,
        block_min_seconds=20,
        block_max_seconds=120,
        transition_seconds=20,
        target_age_seconds_range=(10 * 60, 60 * 60),
        required_metrics=(
            "pgbouncer_pool_clients",
            "pgbouncer_pool_servers",
            "pgbouncer_pool_rates",
            "database_capacity",
            "service_slo",
            "connection_churn",
        ),
        record_sources=(
            HistoricalRecordSource.COMPONENT_LOG,
            HistoricalRecordSource.TOPSQL,
            HistoricalRecordSource.OPERATION_EVENT,
        ),
        decoys=(
            HistoryDecoySpec(
                decoy_id="legal-long-report",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="service_slo",
                field="p99_ms",
                target="report",
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=20,
                minimum_deviation_mad=1.0,
            ),
            HistoryDecoySpec(
                decoy_id="short-connection-churn",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="connection_churn",
                field="connects_per_sec",
                target="testdb/checkout_user",
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=10,
                minimum_deviation_mad=0.1,
            ),
            HistoryDecoySpec(
                decoy_id="etl-checkpoint-pause",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="service_slo",
                field="throughput_per_sec",
                target="etl",
                direction=DecoyDirection.DIP,
                count=1,
                duration_seconds=20,
                minimum_deviation_mad=1.0,
            ),
            HistoryDecoySpec(
                decoy_id="short-checkout-queue-burst",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="pgbouncer_pool_clients",
                field="cl_waiting",
                target="testdb/checkout_user",
                direction=DecoyDirection.SPIKE,
                count=3,
                duration_seconds=60,
                minimum_deviation_mad=0.5,
            ),
            HistoryDecoySpec(
                decoy_id="short-reporting-queue-burst",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="pgbouncer_pool_clients",
                field="cl_waiting",
                target="testdb/report_user",
                direction=DecoyDirection.SPIKE,
                count=2,
                duration_seconds=30,
                minimum_deviation_mad=0.5,
            ),
        ),
        max_points_per_series=21600,
        max_scalar_samples_per_response=10000,
        max_history_query_seconds=1800,
        max_history_records_per_response=200,
        decoys_adjacent_to_target=True,
    )
    case = case_type(
        case_id=case_id,
        case_no=case_no,
        evaluator=evaluator,
        title="Focused PgBouncer connection budget governance." if simple else "PgBouncer connection budget governance under a three-workload replay.",
        alert=(
            "P2 business-capacity alert: checkout and reporting service degraded during a peak window. PostgreSQL max_connections=40 with spare capacity; reporting must complete at least one unit of work. Restore both services with transaction pooling without raising the PostgreSQL ceiling (40), the PgBouncer database-side server budget (16), or the shared pool budget cap (default_pool_size + reserve_pool_size <= 24); verify queue convergence after the change."
            if simple else
            "P1 business-capacity alert: checkout, reporting and ETL service degraded during a peak window. PostgreSQL max_connections=40. Reporting must complete at least one unit, ETL must update at least 10 rows, and a scheduled maintenance check must remain available. Restore all services with transaction pooling, keep the existing database connection ceilings, and verify queue convergence. The replay contract is checkout p99 <=1200 ms with success ratio >=0.80, fairness ratio >=0.25, peak PgBouncer-to-PostgreSQL server connections <=6, CPU <=95%, and no configured pool budget above 24."
        ),
        initial_state={"status": "degraded", "postgres_headroom": True},
        expected_target={"status": "recovered", "pool_mode": "transaction", "queue": "converged", "workloads": "fair"},
        background_workload=BackgroundWorkloadSpec(
            profiles=(), worker_count=1 if simple else 3, seed=0x5822 if simple else 0x5821,
            start_phase=(
                BackgroundWorkloadStartPhase.BEFORE_FAULTS
                if not simple
                else BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY
            ),
        ),
        reference_report=_report(case_id),
        difficulty=(
            DifficultyCalibration(
                diagnostic_depth=5,
                environmental_complexity=0.416667,
                reference_run_ids=(reference_run_id,),
            ) if simple else
            DifficultyCalibration(
                diagnostic_depth=7,
                environmental_complexity=0.816327,
                reference_run_ids=(reference_run_id,),
            )
        ),
        runtime=PostgresCaseRuntime(
            resources=_RESOURCE_SPEC,
            parameters=PostgresRuntimeSpec(
                parameters=(
                    ("max_connections", "40"),
                    ("track_io_timing", "on"),
                    ("shared_preload_libraries", "pg_stat_statements"),
                    ("logging_collector", "on"),
                    ("log_destination", "stderr"),
                    ("log_directory", "/var/log/postgresql"),
                    ("log_filename", "postgresql-%Y-%m-%d_%H%M%S.log"),
                    ("log_rotation_age", "1d"),
                    ("log_rotation_size", "100MB"),
                ),
            ),
        ),
        base_image_name="aiopsbench-pg-tpcds:latest",
        workload_tag="pgbouncer-connection-budget",
        pgbouncer_fault_image=_fault_image_name(case_id),
        dbname="testdb", postgres_max_connections=40,
        pool_users=("checkout_user", "report_user") if simple else ("checkout_user", "report_user", "etl_user"),
        checkout_user="checkout_user", report_user="report_user",
        etl_user="report_user" if simple else "etl_user",
        checkout_application="rg-checkout-pgbench", report_application="rg-reporting-tpcds",
        etl_application="rg-etl-copy-update", health_application="rg-health-probe",
        long_report_application="reporting-batch-07", report_profile="report_tpcds",
        report_probe_profile="report_probe", report_query="q3",
        report_qps=0.08 if simple else 0.12, report_probe_qps=0.18 if simple else 0.25,
        minimum_report_progress=1, minimum_etl_progress=5 if simple else 10,
        minimum_health_progress=0 if simple else 1,
        minimum_checkout_progress=60 if simple else 30,
        checkout_p99_ms=1060 if simple else 1200, checkout_success_ratio=0.80,
        minimum_fairness_ratio=0.20 if simple else 0.25, max_client_connections=64,
            max_database_connections=16 if simple else 6, max_pool_budget=24,
        max_cpu_percent=95.0, etl_rows=1000 if simple else 10000,
        etl_batch_size=25 if simple else 50, churn_connections=0 if simple else 60,
        checkout_clients=3 if simple else 8,
        replay_checkout_workers=5 if simple else 8,
        replay_hold_seconds=0.40 if simple else 0.20,
        replay_duration_seconds=10.0 if simple else 6.0,
        initial_pool_size=2 if simple else 2, initial_reserve_pool_size=0,
        initial_runtime_max_database_connections=16 if simple else 20,
        normal_checkout_role_connection_limit=20,
        target_checkout_role_connection_limit=2 if simple else 1,
        recovered_checkout_role_connection_limit=6,
        other_role_connection_limit=20,
        protected_neighbor_connections=1,
        bounded_neighbor_roles=(
            (("archive_batch_user", 2), ("report_legacy_user", 3))
        ),
        simple=simple,
        frozen_history=None,
    )
    return replace(
        case,
        background_workload=replace(
            case.background_workload,
            profiles=_workload_profiles(case),
        ),
        frozen_history=history_spec,
        frozen_history_adapter=(None if simple else PgBouncerMetricHistoryProvider()),
    )


_HARD_CASE = _make_case(case_id="pool_partition_shortage", case_no=0, evaluator=PgResourceGovernancePgbouncerConnectionBudgetEvaluatorCase, simple=False, reference_run_id="pg_rg_mf01_pool_partition_shortage_mock_reference")
_EASY_CASE = _make_case(case_id="pool_partition_shortage_simple", case_no=1, evaluator=PgResourceGovernancePgbouncerConnectionBudgetSimpleEvaluatorCase, simple=True, reference_run_id="pg_rg_mf01_pool_partition_shortage_simple_mock_reference")


class PgResourceGovernancePgbouncerConnectionBudgetScenario(PostgresScenario):
    scenario_id = "pg_resource_governance_pgbouncer_connection_budget"
    description = "Govern PgBouncer transaction-pool budgets across checkout, reporting and ETL workloads."
    cases = (_HARD_CASE, _EASY_CASE)

    def build_fault_plan(self, case: PgBouncerConnectionBudgetCase) -> tuple[FaultPlan, ...]:
        ports = dict(PGBOUNCER_PORTS)
        configured_port = os.environ.get("AIOPS_PGBOUNCER_PORT")
        if configured_port is not None:
            ports["pgbouncer"] = int(configured_port)
        return (FaultPlan(
            injector_type=PgBouncerConnectionBudgetInjector,
            config={"ports": ports, "base_image_name": case.base_image_name, "pgbouncer_fault_image": case.pgbouncer_fault_image},
        ),)


__all__ = (
    "PGBOUNCER_FAULT_IMAGE_PREFIX", "PGBOUNCER_PORTS", "PgBouncerConnectionBudgetCase",
    "PgBouncerConnectionBudgetInjector", "PgResourceGovernancePgbouncerConnectionBudgetScenario",
)
