"""Real read-replica LWLock slowpath and PgBouncer cascade scenario."""

from __future__ import annotations

import json
import hashlib
import threading
import time
from dataclasses import dataclass
from typing import Any, Mapping

from src.scenarios.evaluation.postgres.business_change import (
    PgBusinessChangeLwlockPgbouncerCascadeForReplicaLwlockTippingEvaluatorCase,
    PgBusinessChangeLwlockPgbouncerCascadeForReplicaLwlockTippingSimpleEvaluatorCase,
)
from src.execution.postgres_replica_fleet import (
    PgReplicaFleetRuntime,
    ReplicaFleetPorts,
)
from src.execution.history.records import HistoricalRecordSource
from src.scenarios.frozen_history import DecoyDirection, DecoyKind, HistoryDecoySpec, FrozenHistorySpec
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase, WorkloadProfile

from src.execution.specs import CaseResourceSpec
from src.scenarios.base import DifficultyCalibration, FaultPlan, PostgresScenario, PostgresScenarioCase


SCENARIO_ID = "pg_business_change_lwlock_pgbouncer_cascade"
PORTS = ReplicaFleetPorts()
POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=8,
    worker_memory_mb=2048,
    container_cpu_limit=4.0,
    container_memory_mb=1024,
)


def _read_footprint_query(variant: int = 0) -> str:
    # Keep the lock footprint above the fast-path boundary without making the
    # post-remediation N-1 replay itself permanently miss the read SLO.
    if variant in {2, 5}:
        # Keep the same real relation-lock slowpath while bounding per-query
        # memory on the 1 GiB replica used by the scenario.
        # The Agent-facing Simple workload remains a 17-relation footprint.
        # Its private admission probe uses a larger real relation-lock burst
        # so lock-manager partition work is observable under N-1 contention.
        footprint_count = 20
        # The admission probe must expose both real LockManager contention and
        # a downstream PgBouncer queue. Use the same bounded hold for both
        # cases; a 1ms hold is too short for the four-server pool to retain a
        # public cl_waiting observation.
        hold_seconds = 0.08
        joins = " ".join(
            f"CROSS JOIN rc_footprint_{index:02d} f{index}" for index in range(1, footprint_count)
        )
        return (
            "SELECT count(*) FROM rc_footprint_00 f0 "
            f"{joins} CROSS JOIN LATERAL (SELECT pg_sleep({hold_seconds})) pause "
            "WHERE f0.id = 1"
        )
    else:
        footprint_count = 20 if variant == 0 else 17 if variant in {3, 4} else 4
        row_scope = "o.id <= 8" if variant == 0 else "o.id <= 20"
        item_scope = "i.order_id <= 8" if variant == 0 else "i.order_id <= 20"
        predicate = "c.region BETWEEN 8 AND 48" if variant == 0 else "c.tier IN (1, 3, 5, 7)"
        extra_predicate = " AND o.id = o.id" if variant == 4 else ""
    joins = " ".join(
        f"CROSS JOIN rc_footprint_{index:02d} f{index}" for index in range(footprint_count)
    )
    return (
        "SELECT count(*) AS matching_orders, coalesce(sum(o.amount), 0) AS gross_amount "
        "FROM rc_orders o JOIN rc_customers c ON c.id = o.customer_id "
        "JOIN rc_order_items i ON i.order_id = o.id "
        "JOIN rc_products p ON p.id = i.sku + 1 "
        f"{joins} WHERE {predicate} AND {row_scope} AND {item_scope} AND o.status IN (1, 2, 3) "
        f"AND p.category BETWEEN 2 AND 28{extra_predicate}"
    )


def _hard_workload() -> BackgroundWorkloadSpec:
    return BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="checkout_read_footprint",
                sql=_read_footprint_query(0),
                qps=1.4,
                tier="MEDIUM",
                connection_pool="read_pool",
                application_name="checkout-read-router",
            ),
            WorkloadProfile(
                name="catalog_read_footprint",
                sql=_read_footprint_query(3),
                qps=1.1,
                tier="MEDIUM",
                connection_pool="read_pool",
                application_name="catalog-read-router",
            ),
            WorkloadProfile(
                name="order_write_probe",
                sql=(
                    "UPDATE rc_write_probe SET writes = writes + 1, "
                    "touched_at = clock_timestamp() WHERE id = 1"
                ),
                qps=0.6,
                tier="WRITE",
                target="primary",
                application_name="order-writer-primary",
                commit=True,
            ),
        ),
        worker_count=6,
        seed=0xCF02,
        warmup_seconds=2,
    )


def _easy_workload() -> BackgroundWorkloadSpec:
    return BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="checkout_read_footprint_simple",
                sql=_read_footprint_query(4),
                qps=0.7,
                tier="LIGHT",
                connection_pool="read_pool",
                application_name="checkout-read-simple",
            ),
            WorkloadProfile(
                name="order_write_probe_simple",
                sql=(
                    "UPDATE rc_write_probe SET writes = writes + 1, "
                    "touched_at = clock_timestamp() WHERE id = 1"
                ),
                qps=0.25,
                tier="WRITE",
                target="primary",
                application_name="order-writer-simple-primary",
                commit=True,
            ),
            WorkloadProfile(
                name="report_pool_short_peak",
                sql="SELECT count(*) FROM rc_orders WHERE status IN (1, 2, 3)",
                qps=0.8,
                tier="LIGHT",
                connection_pool="report_pool",
                application_name="report-pool-short-peak",
            ),
        ),
        worker_count=3,
        seed=0xCF0201,
        warmup_seconds=1,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    )


def _simple_history() -> FrozenHistorySpec:
    return FrozenHistorySpec(
        schema_version=1,
        duration_seconds=21_600,
        normal_capture_seconds=120,
        fault_capture_seconds=180,
        base_step_seconds=2,
        overview_step_seconds=20,
        block_min_seconds=60,
        block_max_seconds=120,
        transition_seconds=20,
        target_age_seconds_range=(900, 5_400),
        required_metrics=(
            "router_distribution",
            "replica_service",
            "replica_lwlock",
            "query_footprint",
            "pgbouncer_pool",
            "primary_service",
        ),
        record_sources=(
            HistoricalRecordSource.TOPSQL,
            HistoricalRecordSource.SLOW_QUERIES,
            HistoricalRecordSource.OPERATION_EVENT,
        ),
        decoys=(
            HistoryDecoySpec(
                decoy_id="healthy-high-qps",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="replica_service",
                field="queries_per_sec",
                target="replica_1",
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                minimum_deviation_mad=1.0,
            ),
            HistoryDecoySpec(
                decoy_id="report-pool-short-peak",
                kind=DecoyKind.CAPTURED_BENIGN,
                metric="pgbouncer_pool",
                field="cl_waiting",
                target="report_pool",
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=60,
                minimum_deviation_mad=1.0,
            ),
        ),
        max_points_per_series=2_000,
        max_scalar_samples_per_response=8_000,
        max_history_query_seconds=1_200,
        max_history_records_per_response=120,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeLwlockPgbouncerCascadeCase(PostgresScenarioCase):
    base_image_name: str
    fault_image_name: str
    workload_tag: str
    drained_replica: str | None
    replica_names: tuple[str, ...]
    min_active_replicas: int
    min_read_apdex: float
    apdex_satisfied_ms: float
    apdex_tolerated_ms: float
    min_success_rate: float
    max_lwlock_waiters: int
    max_pool_maxwait_ms: float
    max_pool_size_cap: int
    min_primary_writes: int
    max_replication_lag_bytes: int
    replay_workers: int
    replay_seconds: float
    probe_interval_seconds: float
    replay_interval_seconds: float
    diagnostic_query: str
    lock_stress_query: str
    background_workload: BackgroundWorkloadSpec
    runtime: PgReplicaFleetRuntime


class PgBusinessChangeLwlockPgbouncerCascadeForReplicaLwlockTippingScenarioCase(
    PgBusinessChangeLwlockPgbouncerCascadeCase
):
    pass


class PgBusinessChangeLwlockPgbouncerCascadeForReplicaLwlockTippingSimpleScenarioCase(
    PgBusinessChangeLwlockPgbouncerCascadeCase
):
    pass


_REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "finding",
                "factor": "replica_lwlock_tipping",
                "entity": "affected read replica",
                "evidence": ["N-1 routing raised per-replica relation-lock demand"],
            },
            {
                "type": "finding",
                "factor": "affected_read_replica",
                "entity": "one read replica",
                "evidence": ["one read replica was unavailable and remaining replicas skewed"],
            },
            {
                "type": "finding",
                "factor": "waiters_first",
                "entity": "LWLock:lock_manager",
                "evidence": ["lock-manager waiters led query duration and pool queue"],
            },
            {
                "type": "finding",
                "factor": "pool_queue_downstream",
                "entity": "PgBouncer",
                "evidence": ["cl_waiting and maxwait followed slow replica queries"],
            },
        ]
    },
    "outcome": {
        "changes": ["restored read replica capacity and routed reads safely"],
        "verification": ["N-1 replay met read Apdex, primary write, and replication checks"],
    },
    "summary": "Replica capacity loss tipped real lock-manager slowpath demand before the downstream pool queue.",
}

_SIMPLE_REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "finding",
                "factor": "N-1 route redistribution",
                "entity": "router",
                "evidence": ["route history showed traffic moving to the remaining replicas"],
            },
            {
                "type": "finding",
                "factor": "affected read replica",
                "entity": "one read replica",
                "evidence": ["operation history showed one replica unavailable during the target window"],
            },
            {
                "type": "finding",
                "factor": "query footprint crossed the relation-lock fast path",
                "entity": "checkout read family",
                "evidence": ["query_footprint showed a broad relation footprint under N-1 load"],
            },
            {
                "type": "finding",
                "factor": "LWLock waiters preceded query latency",
                "entity": "LWLock:lock_manager",
                "evidence": ["waiters increased before replica query p95/p99"],
            },
            {
                "type": "finding",
                "factor": "query latency followed LWLock waiters",
                "entity": "read query",
                "evidence": ["replica service duration rose after the waiter samples"],
            },
            {
                "type": "finding",
                "factor": "read PgBouncer queue followed query latency",
                "entity": "read_pool",
                "evidence": ["read-pool cl_waiting/maxwait rose last"],
            },
            {
                "type": "finding",
                "factor": "healthy high-QPS small-footprint replica was excluded",
                "entity": "healthy replica",
                "evidence": ["the high-QPS benign window had no matching waiter-first chain"],
            },
            {
                "type": "finding",
                "factor": "report pool short peak was excluded",
                "entity": "report_pool",
                "evidence": ["the report-only queue had no read-replica or lock-manager support"],
            },
        ]
    },
    "outcome": {
        "changes": ["restored read replica capacity and routed reads safely"],
        "verification": ["N-1 replay met read Apdex, primary write, and replication checks"],
    },
    "summary": "N-1 route redistribution amplified a broad relation-lock footprint, with LWLock waiters before latency and the read-pool queue.",
}


class PgBusinessChangeLwlockPgbouncerCascadeScenario(PostgresScenario):
    scenario_id = SCENARIO_ID
    description = "A streaming read-replica N-1 replay that exposes LWLock slowpath demand and downstream PgBouncer queueing."
    cases = (
        PgBusinessChangeLwlockPgbouncerCascadeForReplicaLwlockTippingScenarioCase(
            case_id="replica_lwlock_tipping",
            case_no=0,
            evaluator=PgBusinessChangeLwlockPgbouncerCascadeForReplicaLwlockTippingEvaluatorCase,
            base_image_name="aiopsbench-pg-replica-cascade-base:latest",
            fault_image_name="aiopsbench-pg-fault-pg-business-change-lwlock-pgbouncer-cascade-replica-lwlock-tipping:latest",
            workload_tag="replica-cascade",
            title="N-1 read-replica LWLock slowpath and PgBouncer queue cascade.",
            alert=(
                "[SEV1] Read traffic is planned to run with one replica drained for maintenance. "
                "Historical N-1 replay showed partial read tail-latency and pool queue symptoms. "
                "Prove a safe capacity and routing plan while keeping primary writes healthy."
            ),
            initial_state={"status": "degraded", "topology": "N-1 read capacity", "pool": "queueing downstream"},
            expected_target={"status": "recovered", "active_read_replicas": 3, "writer": "primary", "consistency": "preserved"},
            reference_report=_REFERENCE_REPORT,
            difficulty=DifficultyCalibration(
                diagnostic_depth=4,
                environmental_complexity=0.272727,
                reference_run_ids=("reference-57__pg_lwlock_pgbouncer_cascade__replica_lwlock_tipping__mock__r001",),
            ),
            drained_replica="replica_0",
            replica_names=("replica_0", "replica_1", "replica_2"),
            min_active_replicas=3,
            min_read_apdex=0.80,
            apdex_satisfied_ms=9000.0,
            apdex_tolerated_ms=15000.0,
            min_success_rate=0.90,
            max_lwlock_waiters=8,
            max_pool_maxwait_ms=5000.0,
            max_pool_size_cap=128,
            min_primary_writes=1,
            max_replication_lag_bytes=4 * 1024 * 1024,
            replay_workers=12,
            replay_seconds=5.0,
            probe_interval_seconds=0.08,
            replay_interval_seconds=0.10,
            diagnostic_query=_read_footprint_query(0),
            lock_stress_query=_read_footprint_query(2),
            background_workload=_hard_workload(),
            runtime=PgReplicaFleetRuntime(resources=POSTGRES_RESOURCES, ports=PORTS),
        ),
        PgBusinessChangeLwlockPgbouncerCascadeForReplicaLwlockTippingSimpleScenarioCase(
            case_id="replica_lwlock_tipping_simple",
            case_no=1,
            evaluator=PgBusinessChangeLwlockPgbouncerCascadeForReplicaLwlockTippingSimpleEvaluatorCase,
            base_image_name="aiopsbench-pg-replica-cascade-base:latest",
            fault_image_name="aiopsbench-pg-fault-pg-business-change-lwlock-pgbouncer-cascade-replica-lwlock-tipping-simple:latest",
            workload_tag="replica-cascade-simple",
            title="N-1 read-replica LWLock slowpath and PgBouncer queue cascade.",
            alert=(
                "[SEV2] Read-service tail latency and intermittent waits were reported during capacity planning. "
                "Establish a safe read-capacity plan and verify it without changing writer consistency."
            ),
            initial_state={
                "status": "current fleet healthy; historical read-service investigation",
                "service": "read path",
                "writer": "primary protected",
                "history": "frozen history describes a past window; current snapshots are healthy",
            },
            expected_target={"status": "recovered", "active_read_replicas": 3, "writer": "primary", "consistency": "preserved"},
            reference_report=_SIMPLE_REFERENCE_REPORT,
            difficulty=DifficultyCalibration(
                diagnostic_depth=8,
                environmental_complexity=0.25,
                reference_run_ids=("reference-57__pg_lwlock_pgbouncer_cascade__replica_lwlock_tipping_simple__mock__r001",),
            ),
            drained_replica=None,
            replica_names=("replica_0", "replica_1", "replica_2"),
            min_active_replicas=3,
            min_read_apdex=0.75,
            apdex_satisfied_ms=5000.0,
            apdex_tolerated_ms=10000.0,
            min_success_rate=0.85,
            max_lwlock_waiters=12,
            max_pool_maxwait_ms=1500.0,
            max_pool_size_cap=128,
            min_primary_writes=1,
            max_replication_lag_bytes=8 * 1024 * 1024,
            replay_workers=6,
            replay_seconds=5.0,
            probe_interval_seconds=0.12,
            replay_interval_seconds=0.20,
            diagnostic_query=_read_footprint_query(3),
            lock_stress_query=_read_footprint_query(2),
            background_workload=_easy_workload(),
            runtime=PgReplicaFleetRuntime(resources=POSTGRES_RESOURCES, ports=PORTS),
            frozen_history=_simple_history(),
        ),
    )

    def build_fault_plan(self, case: PgBusinessChangeLwlockPgbouncerCascadeCase) -> tuple[FaultPlan, ...]:
        frozen_history_simple = case.frozen_history is not None
        return (
            FaultPlan(
                injector_type=PgBusinessChangeLwlockPgbouncerCascadeInjector,
                config={
                    "drained_replica": case.drained_replica,
                    "drained_replicas": case.replica_names,
                    "replica_names": case.replica_names,
                    "diagnostic_query": case.diagnostic_query,
                    "probe_query": case.lock_stress_query,
                    "probe_workers": 80 if case.case_no == 0 else (64 if frozen_history_simple else max(2, case.replay_workers // 2)),
                    "probe_interval_seconds": 0.02 if frozen_history_simple else case.probe_interval_seconds,
                    "probe_connection_pool": "read_pool" if case.case_no == 0 or frozen_history_simple else None,
                    "probe_pool_workers": 24 if case.case_no == 0 else (18 if frozen_history_simple else 0),
                    # Let direct contention lead the routed pool queue for both
                    # live and frozen-history admission. The public history gate
                    # still requires the waiter -> duration -> queue chain.
                    "probe_pool_start_delay_seconds": 45.0,
                    "probe_direct_target": "spread" if frozen_history_simple else "first",
                    "require_lwlock_waiters": case.case_no == 0 or frozen_history_simple,
                },
            ),
        )


class PgBusinessChangeLwlockPgbouncerCascadeInjector(BaseFaultInjector):
    """Drain one real replica and sustain direct plus routed read pressure.

    Direct probes create real relation-lock footprint on the remaining
    replicas; case background workload and replay stay on the PgBouncer/router
    path so pool queueing remains an observable downstream effect.
    """

    TARGET_CAPTURE_GRACE_SECONDS = 5.0
    TARGET_DURATION_WAIT_TIMEOUT_SECONDS = 300.0

    def __init__(self) -> None:
        self._stop_event: threading.Event | None = None
        self._threads: list[threading.Thread] = []
        self._connections: list[Any] = []
        self._connection_lock = threading.Lock()
        self._env: Any = None
        self._drained_replica: str | None = None
        self._baseline: Mapping[str, Any] | None = None
        self._probe_error_count = 0
        self._last_probe_error: str | None = None
        self._probe_start_barrier: threading.Barrier | None = None
        self._ready_observation: Mapping[str, Any] | None = None
        self._last_readiness_observation: Mapping[str, Any] | None = None
        self._configured_drained_replica: str | None = None
        self._fault_started_at_ms: int | None = None
        self._benign_stop_event: threading.Event | None = None
        self._benign_threads: list[threading.Thread] = []
        self._benign_connections: list[Any] = []
        self._benign_connection_lock = threading.Lock()
        self._frozen_history_required = False
        self._direct_duration_observed = False
        self._observation_window_baseline_started_at: float | None = None
        self._pool_start_release: threading.Event | None = None
        self._pool_start_pending = False
        self._pool_start_error: str | None = None

    def _apply_config(self, config: Mapping[str, Any]) -> None:
        self._replica_names = tuple(str(value) for value in config["replica_names"])
        configured_target = config.get("drained_replica")
        self._configured_drained_replica = (
            str(configured_target) if configured_target not in (None, "", "random") else None
        )
        candidates = tuple(str(value) for value in config.get("drained_replicas", self._replica_names))
        if not candidates or any(value not in self._replica_names for value in candidates):
            raise ValueError(
                "drained_replicas must contain only configured replicas: "
                f"candidates={candidates!r}, replicas={self._replica_names!r}"
            )
        self._drained_candidates = candidates
        self._diagnostic_query = str(config["diagnostic_query"])
        self._probe_query = str(config.get("probe_query", self._diagnostic_query))
        self._probe_workers = int(config["probe_workers"])
        self._probe_interval_seconds = float(config["probe_interval_seconds"])
        self._probe_connection_pool = config.get("probe_connection_pool")
        self._probe_pool_workers = max(0, int(config.get("probe_pool_workers", 0)))
        self._probe_pool_start_delay_seconds = max(
            0.0, float(config.get("probe_pool_start_delay_seconds", 0.0))
        )
        self._probe_direct_target = str(config.get("probe_direct_target", "first"))
        self._require_lwlock_waiters = bool(config.get("require_lwlock_waiters", False))
        self._ready_observation = None
        self._last_readiness_observation = None
        self._fault_started_at_ms = None
        self._direct_duration_observed = False
        self._observation_window_baseline_started_at = None
        self._pool_start_release = None
        self._pool_start_pending = False
        self._pool_start_error = None
        if self._probe_workers <= 0:
            raise ValueError("probe_workers must be positive")
        if self._probe_interval_seconds <= 0:
            raise ValueError("probe_interval_seconds must be positive")
        if self._probe_direct_target not in {"first", "spread"}:
            raise ValueError("probe_direct_target must be 'first' or 'spread'")

    def _select_drained_replica(self, context: FaultLifecycleContext) -> None:
        if self._configured_drained_replica is not None:
            if self._configured_drained_replica not in self._drained_candidates:
                raise ValueError(
                    "configured drained replica is outside the candidate set: "
                    f"target={self._configured_drained_replica!r}, candidates={self._drained_candidates!r}"
                )
            self._drained_replica = self._configured_drained_replica
            return
        material = f"{context.run_id}:{context.scenario_id}:{context.case_id}:drain".encode("utf-8")
        index = int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % len(self._drained_candidates)
        self._drained_replica = self._drained_candidates[index]

    def prepare_metric_history(self, context: FaultLifecycleContext) -> None:
        """Start real benign windows before normal capture and choose the target."""
        self._env = context.env
        self._frozen_history_required = getattr(context.case, "frozen_history", None) is not None
        self._apply_config(context.config)
        self._select_drained_replica(context)
        if getattr(context.case, "frozen_history", None) is not None:
            self._start_benign_windows()

    def _benign_query_loop(
        self,
        *,
        application_name: str,
        target: str | None = None,
        connection_pool: str | None = None,
        sql: str,
        qps: float,
        active_seconds: float,
    ) -> None:
        connection = None
        started_at = time.monotonic()
        try:
            while self._benign_stop_event is not None and not self._benign_stop_event.is_set():
                elapsed = time.monotonic() - started_at
                if elapsed >= active_seconds:
                    self._benign_stop_event.wait(0.25)
                    continue
                query_started = time.monotonic()
                try:
                    if connection is None or getattr(connection, "closed", False):
                        connection = self._env.open_workload_connection(
                            application_name,
                            target=target,
                            connection_pool=connection_pool,
                        )
                        with self._benign_connection_lock:
                            self._benign_connections.append(connection)
                    with connection.cursor() as cursor:
                        cursor.execute(sql)
                        cursor.fetchall()
                    connection.rollback()
                except Exception:
                    if connection is not None:
                        try:
                            connection.close()
                        except Exception:
                            pass
                        with self._benign_connection_lock:
                            try:
                                self._benign_connections.remove(connection)
                            except ValueError:
                                pass
                        connection = None
                self._benign_stop_event.wait(max(0.0, 1.0 / qps - (time.monotonic() - query_started)))
        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass
                with self._benign_connection_lock:
                    try:
                        self._benign_connections.remove(connection)
                    except ValueError:
                        pass

    def _start_benign_windows(self) -> None:
        self._stop_benign_windows()
        self._benign_stop_event = threading.Event()
        benign_specs = [
            {
                "application_name": "checkout-read-simple-high-qps",
                "target": "replica_1",
                "sql": "SELECT count(*) AS matching_orders FROM rc_orders o WHERE o.id = o.id",
                "qps": 5.0,
                "workers": 1,
            },
            {
                "application_name": "report-pool-benign-peak",
                "connection_pool": "report_pool",
                "sql": "SELECT pg_sleep(1.6), count(*) FROM rc_orders WHERE status IN (1, 2, 3)",
                "qps": 0.8,
                "workers": 2,
            },
        ]
        for spec in benign_specs:
            worker_count = int(spec.pop("workers"))
            for worker_index in range(worker_count):
                thread = threading.Thread(
                    target=self._benign_query_loop,
                    kwargs={**spec, "active_seconds": 240.0},
                    name=f"lwlock-benign-{spec['application_name']}-{worker_index}",
                    daemon=True,
                )
                thread.start()
                self._benign_threads.append(thread)

    def _stop_benign_windows(self) -> None:
        if self._benign_stop_event is not None:
            self._benign_stop_event.set()
        with self._benign_connection_lock:
            connections = tuple(self._benign_connections)
            self._benign_connections.clear()
        for connection in connections:
            try:
                connection.close()
            except Exception:
                pass
        join_deadline = time.monotonic() + 10
        for thread in reversed(self._benign_threads):
            remaining = max(0.0, join_deadline - time.monotonic())
            if remaining <= 0:
                break
            thread.join(timeout=remaining)
        self._benign_threads.clear()
        self._benign_stop_event = None

    def _stop_runtime(self) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
        if self._pool_start_release is not None:
            self._pool_start_release.set()
        if self._probe_start_barrier is not None:
            self._probe_start_barrier.abort()
        with self._connection_lock:
            connections = tuple(self._connections)
            self._connections.clear()
        for connection in connections:
            try:
                connection.close()
            except Exception:
                pass
        join_deadline = time.monotonic() + 10
        for thread in reversed(self._threads):
            remaining = max(0.0, join_deadline - time.monotonic())
            if remaining <= 0:
                break
            thread.join(timeout=remaining)
        self._threads.clear()
        self._stop_event = None
        self._pool_start_release = None
        self._pool_start_pending = False
        self._pool_start_error = None

    def _release_pool_start(self) -> None:
        if self._pool_start_release is not None:
            self._pool_start_release.set()

    def _probe_loop(
        self,
        ready: threading.Event,
        target: str,
        connection_pool: str | None = None,
        start_barrier: threading.Barrier | None = None,
    ) -> None:
        connection = None
        waiting_for_start = start_barrier is not None
        ready.set()
        try:
            while self._stop_event is not None and not self._stop_event.is_set():
                try:
                    if connection is None or getattr(connection, "closed", False):
                        if connection_pool:
                            connection = self._env.open_workload_connection(
                                "lwlock-cascade-probe",
                                connection_pool=connection_pool,
                            )
                        else:
                            connection = self._env.open_workload_connection(
                                "lwlock-cascade-probe", target=target
                            )
                        with self._connection_lock:
                            self._connections.append(connection)
                    if waiting_for_start:
                        try:
                            start_barrier.wait(timeout=15)
                        except threading.BrokenBarrierError:
                            return
                        waiting_for_start = False
                    with connection.cursor() as cursor:
                        cursor.execute(self._probe_query)
                        cursor.fetchall()
                    connection.rollback()
                except Exception as exc:
                    if waiting_for_start and start_barrier is not None:
                        start_barrier.abort()
                    with self._connection_lock:
                        self._probe_error_count += 1
                        self._last_probe_error = f"{type(exc).__name__}: {exc}"
                    if connection is not None:
                        try:
                            connection.close()
                        except Exception:
                            pass
                        with self._connection_lock:
                            try:
                                self._connections.remove(connection)
                            except ValueError:
                                pass
                        connection = None
                if self._stop_event.wait(self._probe_interval_seconds):
                    break
        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass
                with self._connection_lock:
                    try:
                        self._connections.remove(connection)
                    except ValueError:
                        pass

    def _start_probes(self) -> None:
        self._stop_event = threading.Event()
        targets = tuple(value for value in self._replica_names if value != self._drained_replica)
        if not targets:
            raise RuntimeError("LWLock cascade has no active replica probe target")
        pool_workers = min(self._probe_pool_workers, self._probe_workers)
        self._pool_start_error = None
        self._pool_start_pending = False
        self._direct_duration_observed = False
        direct_target = (
            targets[0]
            if self._probe_connection_pool and self._probe_direct_target == "first"
            else None
        )

        def start_worker(index: int, *, connection_pool: str | None, start_barrier: threading.Barrier | None) -> None:
            ready = threading.Event()
            target = direct_target or targets[index % len(targets)]
            thread = threading.Thread(
                target=self._probe_loop,
                args=(ready, target, connection_pool, start_barrier),
                daemon=True,
            )
            thread.start()
            if not ready.wait(timeout=5):
                raise RuntimeError("LWLock cascade probe did not start")
            self._threads.append(thread)

        direct_indexes = tuple(range(pool_workers, self._probe_workers))

        history_samples_gate = getattr(self._env, "history_has_waiter_samples", None)

        def start_direct_workers(worker_indexes: tuple[int, ...]) -> None:
            if self._stop_event is None:
                self._stop_event = threading.Event()
            synchronize = not self._frozen_history_required
            self._probe_start_barrier = (
                threading.Barrier(len(worker_indexes) + 1)
                if worker_indexes and synchronize
                else None
            )
            for index in worker_indexes:
                start_worker(
                    index,
                    connection_pool=None,
                    start_barrier=self._probe_start_barrier,
                )
            if self._probe_start_barrier is not None:
                try:
                    self._probe_start_barrier.wait(timeout=20)
                except threading.BrokenBarrierError as exc:
                    self._stop_runtime()
                    raise RuntimeError("LWLock cascade probes did not reach synchronized start") from exc
                self._probe_start_barrier = None

        # Use the configured direct pressure for admission. Simple spreads
        # these workers across the remaining replicas, so a small lead batch
        # can stay below the real LockManager contention threshold.
        start_direct_workers(direct_indexes)
        if self._probe_pool_start_delay_seconds > 0:
            # Let the direct phase produce several real waiter observations
            # before adding routed pool pressure. The same bounded observation
            # loop records history and counts the real waiter/duration lead.
            lead_deadline = time.monotonic() + self._probe_pool_start_delay_seconds
            duration_wait_seconds = (
                self.TARGET_DURATION_WAIT_TIMEOUT_SECONDS
                if self._frozen_history_required
                else max(45.0, self._probe_pool_start_delay_seconds)
            )
            waiter_observation_deadline = lead_deadline + max(
                duration_wait_seconds,
                self._probe_pool_start_delay_seconds,
            )
            waiter_samples = 0
            duration_observed = False
            duration_signal_ms = float(
                getattr(self._env, "FLEET_HISTORY_DURATION_SIGNAL_MS", 2_000.0)
            )
            while time.monotonic() < waiter_observation_deadline:
                observation = self._env.capture_fleet_observation(
                    record_history=True,
                    waiter_sample_count=10,
                )
                waiter_samples += sum(
                    int(value.get("lwlock_wait_samples", 0) or 0)
                    for value in observation.get("replicas", {}).values()
                    if value.get("healthy")
                )
                duration_observed = duration_observed or any(
                    max(
                        float(value.get("p95_query_duration_ms", 0.0) or 0.0),
                        float(value.get("p99_query_duration_ms", 0.0) or 0.0),
                    ) >= duration_signal_ms
                    for value in observation.get("replicas", {}).values()
                    if value.get("healthy")
                )
                now = time.monotonic()
                history_samples_visible = bool(
                    history_samples_gate is None
                    or history_samples_gate(min_waiter_samples=3)
                )
                if (
                    waiter_samples >= 3
                    and history_samples_visible
                    and now >= lead_deadline
                    and (duration_observed or self._frozen_history_required)
                ):
                    break
                remaining = max(0.05, min(0.25, waiter_observation_deadline - now))
                if self._stop_event.wait(remaining):
                    return
            if waiter_samples < 3:
                # Do not manufacture the downstream symptom when the
                # upstream real contention was not observable. install()
                # will report this as an invalid fixture admission.
                return
            if duration_observed:
                self._direct_duration_observed = True
            if self._frozen_history_required and pool_workers:
                workload_runner = getattr(self._env, "_workload_runner", None)
                if workload_runner is None:
                    raise RuntimeError(
                        "LWLock cascade frozen-history pool release requires the active workload runner"
                    )
                started_at = getattr(workload_runner, "started_at", None)
                if started_at is None:
                    raise RuntimeError(
                        "LWLock cascade frozen-history pool release requires workload runner start time"
                    )
                self._observation_window_baseline_started_at = float(started_at)
                release = threading.Event()
                self._pool_start_release = release
                self._pool_start_pending = True

                def start_deferred_pool() -> None:
                    release.wait()
                    stop_event = self._stop_event
                    if stop_event is None or stop_event.is_set():
                        return
                    try:
                        baseline_started_at = self._observation_window_baseline_started_at
                        if baseline_started_at is None:
                            raise RuntimeError(
                                "LWLock cascade target-window pool release has no workload baseline"
                            )
                        while True:
                            current_started_at = getattr(workload_runner, "started_at", None)
                            if current_started_at is None:
                                raise RuntimeError(
                                    "LWLock cascade target-window pool release lost workload start time"
                                )
                            if float(current_started_at) > baseline_started_at:
                                break
                            if stop_event.wait(0.05):
                                return
                        grace_deadline = time.monotonic() + self.TARGET_CAPTURE_GRACE_SECONDS
                        while time.monotonic() < grace_deadline:
                            if stop_event.wait(max(0.01, min(0.25, grace_deadline - time.monotonic()))):
                                return
                        duration_signal_ms = float(
                            getattr(self._env, "FLEET_HISTORY_DURATION_SIGNAL_MS", 2_000.0)
                        )
                        duration_deadline = time.monotonic() + self.TARGET_DURATION_WAIT_TIMEOUT_SECONDS
                        duration_observed = False
                        while time.monotonic() < duration_deadline:
                            observation = self._env.capture_fleet_observation(
                                record_history=True,
                                waiter_sample_count=10,
                            )
                            duration_observed = any(
                                max(
                                    float(value.get("p95_query_duration_ms", 0.0) or 0.0),
                                    float(value.get("p99_query_duration_ms", 0.0) or 0.0),
                                ) >= duration_signal_ms
                                for value in observation.get("replicas", {}).values()
                                if value.get("healthy")
                            )
                            if duration_observed:
                                break
                            if stop_event.wait(0.25):
                                return
                        if not duration_observed:
                            raise RuntimeError(
                                "LWLock cascade target history did not expose duration before pool release: "
                                f"timeout_seconds={self.TARGET_DURATION_WAIT_TIMEOUT_SECONDS}"
                            )
                        for index in range(pool_workers):
                            start_worker(
                                index,
                                connection_pool=self._probe_connection_pool,
                                start_barrier=None,
                            )
                    except Exception as exc:
                        self._pool_start_error = f"{type(exc).__name__}: {exc}"
                    finally:
                        self._pool_start_pending = False

                pool_thread = threading.Thread(
                    target=start_deferred_pool,
                    name="lwlock-cascade-deferred-pool",
                    daemon=True,
                )
                self._threads.append(pool_thread)
                pool_thread.start()
                return
        for index in range(pool_workers):
            start_worker(
                index,
                connection_pool=self._probe_connection_pool,
                start_barrier=None,
            )

    def inject(self, context: FaultLifecycleContext) -> None:
        self.install(context)

    def install(self, context: FaultLifecycleContext) -> None:
        self._env = context.env
        self._frozen_history_required = getattr(context.case, "frozen_history", None) is not None
        self._apply_config(context.config)
        self._select_drained_replica(context)
        self._stop_benign_windows()
        self._stop_runtime()
        for replica in self._replica_names:
            self._env.deployment.start_replica(replica)
        if not self._env.deployment.wait_for_ready(timeout=90):
            raise RuntimeError("replica fleet was not ready before LWLock cascade injection")
        self._baseline = self._env.capture_fleet_observation()
        route_drain = getattr(self._env.deployment, "set_router_backends", None)
        if route_drain is not None and not route_drain(excluded_replicas=(self._drained_replica,)):
            raise RuntimeError(f"failed to drain read route for {self._drained_replica}")
        reset_pool = getattr(self._env, "reset_read_pool", None)
        if reset_pool is not None and not reset_pool():
            raise RuntimeError("read pool did not reset after route drain")
        if not self._env.deployment.stop_replica(self._drained_replica):
            raise RuntimeError(f"failed to drain replica: {self._drained_replica}")
        self._fault_started_at_ms = int(time.time() * 1000)
        self._start_probes()
        # The lock-manager signal is sampled from short real contention
        # windows. Allow several sampler intervals for a stable three-sample
        # admission without weakening the waiter-first history gate.
        # The real waiter bursts are intermittent even after the high-rate
        # probe starts. Give the admission sampler enough time to collect the
        # required three samples without weakening the ordering gate.
        deadline = time.time() + 180
        while time.time() < deadline and not self.fault_ready(context):
            time.sleep(0.25)
        if not self.fault_ready(context):
            with self._connection_lock:
                probe_error_count = self._probe_error_count
                last_probe_error = self._last_probe_error
            observation = self._last_readiness_observation or {}
            replica_summary = {
                target: {
                    "healthy": bool(value.get("healthy")),
                    "qps": value.get("queries_per_sec"),
                    "waiters": value.get("lwlock_waiters"),
                    "wait_samples": value.get("lwlock_wait_samples"),
                    "p95_ms": value.get("p95_query_duration_ms"),
                    "error": value.get("error"),
                }
                for target, value in observation.get("replicas", {}).items()
                if isinstance(value, Mapping)
            }
            pool_summary = [
                {
                    "database": row.get("database"),
                    "user": row.get("user"),
                    "cl_waiting": row.get("cl_waiting"),
                    "maxwait": row.get("maxwait"),
                }
                for row in observation.get("pool", {}).get("rows", ())
                if isinstance(row, Mapping)
            ]
            detail = (
                f"probe_errors={probe_error_count}, last_probe_error={last_probe_error!r}"
                if probe_error_count
                else "probe_errors=0"
            )
            raise RuntimeError(
                "LWLock cascade fault did not become ready after replica drain; "
                + detail
                + f"; drained_replica={self._drained_replica!r}; replicas={replica_summary!r}; "
                + f"pool={pool_summary!r}; pool_waiting_clients="
                + f"{observation.get('pool', {}).get('waiting_clients')!r}; "
                + f"direct_duration_observed={self._direct_duration_observed!r}; "
                + f"pool_start_pending={self._pool_start_pending!r}"
            )

    def activate(self, context: FaultLifecycleContext) -> None:
        self._env = context.env
        self._frozen_history_required = getattr(context.case, "frozen_history", None) is not None
        self._apply_config(context.config)
        self._select_drained_replica(context)
        self._stop_runtime()
        self._baseline = self._env.capture_fleet_observation()
        route_drain = getattr(self._env.deployment, "set_router_backends", None)
        if route_drain is not None and not route_drain(excluded_replicas=(self._drained_replica,)):
            raise RuntimeError(f"failed to drain read route for {self._drained_replica}")
        reset_pool = getattr(self._env, "reset_read_pool", None)
        if reset_pool is not None and not reset_pool():
            raise RuntimeError("read pool did not reset after route drain")
        if not self._env.deployment.stop_replica(self._drained_replica):
            raise RuntimeError(f"failed to re-apply replica drain: {self._drained_replica}")
        self._fault_started_at_ms = int(time.time() * 1000)
        self._start_probes()

    def fault_ready(self, context: FaultLifecycleContext | None = None) -> bool:
        if self._env is None:
            return False
        if self._pool_start_error is not None:
            raise RuntimeError(
                "LWLock cascade deferred pool start failed: "
                f"error={self._pool_start_error!r}"
            )
        if self._ready_observation is not None:
            return True
        observation = self._env.capture_fleet_observation()
        self._last_readiness_observation = observation
        replicas = observation.get("replicas", {})
        active = sum(
            1
            for target in self._replica_names
            if replicas.get(target, {}).get("healthy")
        )
        topology_ready = (
            active == len(self._replica_names) - 1
            and not replicas.get(self._drained_replica, {}).get("healthy", True)
        )
        if not topology_ready:
            return False
        if not self._require_lwlock_waiters:
            return True
        # Do not hand the Agent a partial incident that only has the
        # downstream PgBouncer symptom.  This is an admission check for the
        # fault fixture, not an evaluator rule or a diagnosis requirement.
        history_gate = getattr(self._env, "history_has_waiter_lead", None)
        waiter_history_gate = getattr(self._env, "history_has_waiter_samples", None)
        waiter_history_visible = bool(
            waiter_history_gate is not None
            and waiter_history_gate(
                min_waiter_samples=3,
                start_ms=self._fault_started_at_ms,
            )
        )
        history_lock_visible = bool(
            history_gate is not None
            and history_gate(
                min_waiter_samples=3,
                start_ms=self._fault_started_at_ms,
            )
        )
        lock_visible = any(
            int(value.get("lwlock_wait_samples", 0) or 0) >= 3
            for value in replicas.values()
            if value.get("healthy")
        ) or history_lock_visible
        pool_rows = observation.get("pool", {}).get("rows", ())
        read_pool_visible = any(
            str(row.get("database", "")).casefold() == "testdb"
            and int(row.get("cl_waiting", 0) or 0) > 0
            for row in pool_rows
        )
        pool_visible = read_pool_visible or int(observation.get("pool", {}).get("waiting_clients", 0) or 0) > 0
        if lock_visible and pool_visible:
            # Frozen-history history is the Agent-visible incident evidence.
            # Direct probe sampling may stage the downstream workload, but it
            # must never substitute for the frozen public waiter ordering.
            if self._frozen_history_required and not history_lock_visible:
                return False
            if history_gate is not None and not history_lock_visible:
                return False
            self._ready_observation = observation
            return True
        if (
            self._frozen_history_required
            and self._pool_start_pending
            and not pool_visible
        ):
            if not waiter_history_visible:
                return False
            self._ready_observation = observation
            return True
        return False

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, Any]:
        if not self.fault_ready(context):
            raise RuntimeError("cannot publish observability before fault-ready")
        self._release_pool_start()
        # The incident evidence is now durable in fleet history and the
        # latched observation. Frozen-history setup captures the target window
        # after this hook, so retain real pressure until that capture ends.
        fault_observation = self._ready_observation or self._env.capture_fleet_observation()
        if getattr(context.case, "frozen_history", None) is None:
            self._stop_runtime()
        return {
            "baseline": self._baseline,
            "fault_observation": fault_observation,
            "drained_replica": self._drained_replica,
            "ports": self._env.deployment.ports.as_dict(),
            "probe_workers": self._probe_workers,
            "probe_interval_seconds": self._probe_interval_seconds,
            "current_fleet_observation": None,
        }

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Recover only after the real target history window is captured."""
        pool_start_error = self._pool_start_error
        self.recover(context)
        if pool_start_error is not None:
            raise RuntimeError(
                "LWLock cascade deferred pool start failed during target capture: "
                f"error={pool_start_error!r}"
            )

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime()

    def recover(self, context: FaultLifecycleContext) -> None:
        self._stop_benign_windows()
        self._stop_runtime()
        if self._env is None:
            return
        for replica in self._replica_names:
            self._env.deployment.start_replica(replica)
        if not self._env.deployment.wait_for_ready(timeout=90):
            raise RuntimeError("replica fleet did not recover")
        restore_routes = getattr(self._env.deployment, "set_router_backends", None)
        if restore_routes is not None and not restore_routes():
            raise RuntimeError("replica read routes did not recover")
        reset_pool = getattr(self._env, "reset_read_pool", None)
        if reset_pool is not None and not reset_pool():
            raise RuntimeError("read pool did not reset after route recovery")

    def cleanup(self, context: FaultLifecycleContext) -> None:
        self.recover(context)
