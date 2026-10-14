from __future__ import annotations

import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass, replace

import pymysql

from src.database.sql import execute_result_rows, require_one_result_row
from src.protocols.report import StructuredReport
from src.scenarios.evaluation.tidb.system_failure.table_cache_lease_frozen_history import (
    TidbSystemFailureTableCacheLeaseFrozenHistoryEvaluatorCase,
    TidbSystemFailureTableCacheLeaseNarrowCatalogEvaluatorCase,
)
from src.execution.history.records import HistoricalRecordSource
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)
from src.scenarios.tidb.common import join_thread, validate_sql_identifier
from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase

from ...base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime
from src.scenarios.tidb_frozen_history_table_cache_helpers import (
    TableCacheLeaseTables,
    business_summary_sql,
    build_workload_profiles,
    cache_state,
    capture_business_truth,
    configure_tables,
    create_and_seed_schema,
    drop_schema,
    dual_cache_read_replay,
    enable_cache_and_verify,
    table_integrity_sql,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureTableCacheLeaseFrozenHistoryInvestigationScenarioCase(TiDBScenarioCase):
    db: str
    cache_table: str
    cache_table_names: tuple[str, ...]
    pricing_table: str
    healthy_cache_table_names: tuple[str, ...]
    orders_table: str
    inventory_table: str
    catalog_row_count: int
    business_summary_sql: str
    table_integrity_sql: str
    target_profile_names: tuple[str, ...]
    recovery_lease_seconds: int
    recovery_lease_max_seconds: int


_TABLES = TableCacheLeaseTables(
    db="benchops_mf_ma02",
    catalog="mf_ma02_product_catalog",
    inventory="mf_ma02_inventory",
    pricing="mf_ma02_pricing_rules",
    orders="mf_ma02_orders",
    healthy_aux="mf_ma02_catalog_aux",
)
_PROFILES = build_workload_profiles(_TABLES)
_TARGET_PROFILE_NAMES = tuple(profile.name for profile in _PROFILES[:12])
_ORDERS_PHASE_PROBE_COUNT = 420
_ORDERS_OVERLAP_INTERVAL_SECONDS = 1.5

_HISTORY = FrozenHistorySpec(
    schema_version=1,
    duration_seconds=12 * 60 * 60,
    normal_capture_seconds=120,
    fault_capture_seconds=480,
    base_step_seconds=60,
    overview_step_seconds=60,
    block_min_seconds=60,
    block_max_seconds=120,
    transition_seconds=60,
    target_age_seconds_range=(1800, 3600),
    required_metrics=("cpu", "disk_io", "qps", "query_latency", "active_connections"),
    # cAdvisor scrapes every 5s with a 4s timeout; under host load a 10s rate
    # window loses whole samples.  A 30s window tolerates isolated scrape
    # misses while the completeness validator still rejects real gaps.
    metric_rate_windows={"cpu": 30, "disk_io": 30},
    # Cached tables and the lease variable must exist before the workload
    # starts, and the conflict runtime only activates ahead of the target
    # capture, so install happens before the normal capture phase.
    install_before_normal_capture=True,
    metric_targets={
        "cpu": (
            "tidb/tidb-0",
            "tidb/tidb-1",
            "tikv/tikv-0",
            "tikv/tikv-1",
            "tikv/tikv-2",
        ),
        "disk_io": ("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
        "qps": (None,),
        "query_latency": (None,),
        "active_connections": (None,),
    },
    record_sources=(
        HistoricalRecordSource.COMPONENT_LOG,
        HistoricalRecordSource.TOPSQL,
        HistoricalRecordSource.SLOW_QUERIES,
    ),
    decoys=(
        HistoryDecoySpec(
            decoy_id="orders-9007-window",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=60,
            amplitude_mad=1.0,
        ),
        HistoryDecoySpec(
            decoy_id="single-endpoint-cache-window",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=60,
            minimum_deviation_mad=0.1,
        ),
        HistoryDecoySpec(
            decoy_id="ddl-prewrite-window",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=60,
            amplitude_mad=1.5,
        ),
        HistoryDecoySpec(
            decoy_id="cluster-load-window",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=60,
            amplitude_mad=2.0,
        ),
        HistoryDecoySpec(
            decoy_id="missing-catalog-window",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.DIP,
            count=1,
            duration_seconds=60,
            amplitude_mad=1.5,
        ),
    ),
    max_points_per_series=5000,
    max_scalar_samples_per_response=12000,
    max_history_records_per_response=200,
)

_REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "timeline",
                "factor": "the correct historical window shows an early ordinary orders conflict followed by a persistent internal metadata conflict",
                "entity": "the current handoff is quiet because target workers stopped while cache configuration remained unchanged",
                "evidence": ["aligned qps, latency, and component-log timestamps"],
            },
            {
                "type": "root_cause",
                "factor": "the later 9007 or Prewrite failures are write conflicts on mysql.table_cache_meta for cached business tables rather than business-row conflicts",
                "entity": "the conflicting transaction keys map to the three causal cached tables",
                "evidence": ["internal metadata key and table-ID mapping in the target history window"],
            },
            {
                "type": "mechanism",
                "factor": "the TiDB cached-table read path renews a shared lease through lock cached table for read and collides while updating lease metadata",
                "entity": "the cache lease and oldReadLease rows shared by both TiDB endpoints",
                "evidence": ["cached-read log messages and mysql.table_cache_meta lease fields"],
            },
            {
                "type": "scope",
                "factor": "tidb/tidb-0 and tidb/tidb-1 read all three causal cached tables while the auxiliary cached table is single-endpoint",
                "entity": "mf_ma02_product_catalog, mf_ma02_inventory, and mf_ma02_pricing_rules",
                "evidence": ["current catalog IDs, SHOW CREATE markers, and endpoint-specific TopSQL"],
            },
            {
                "type": "necessary_exclusion",
                "factor": "the early orders same-row conflict is bounded and retryable, and TiKV CPU/I/O or unrelated DDL activity does not explain the later causal error window",
                "entity": "orders, unrelated DDL, missing-object probes, and TiKV stores",
                "evidence": ["orders retry converges before internal metadata conflicts persist"],
            },
            {
                "type": "necessary_exclusion",
                "factor": "the single-endpoint cached auxiliary table has no shared-lease conflict and must remain CACHED ON",
                "entity": "benchops_mf_ma02.mf_ma02_catalog_aux",
                "evidence": ["auxiliary TopSQL and cache marker remain healthy"],
            },
        ],
    },
    "outcome": {
        "changes": ["removed cache mode from the three causal tables or raised the global lease within the published bounded range"],
        "verification": ["fresh dual-endpoint replay has no cache conflicts; business truth, schema, TSO, and the auxiliary cache are preserved"],
        "plan": {
            "incident_window": "UTC target window selected from the metric overview and confirmed by bounded history queries",
            "timeline": "orders conflict -> two-endpoint cached reads -> internal metadata conflict -> current quiet handoff",
            "exclusions": ["orders same-row retry", "single-endpoint auxiliary cache", "unrelated DDL", "TiKV I/O"],
            "repair_family": "causal NOCACHE or global tidb_table_cache_lease in 6..30",
        },
    },
    "summary": "The historical target window identifies shared cached-table lease contention across both TiDB endpoints; the repair is bounded to the three causal cache markers or the published lease range and preserves the auxiliary cache and business truth.",
}
StructuredReport.from_mapping(_REFERENCE_REPORT)


_CASE = TidbSystemFailureTableCacheLeaseFrozenHistoryInvestigationScenarioCase(
    case_id="table_cache_lease_history_investigation",
    case_no=0,
    evaluator=TidbSystemFailureTableCacheLeaseFrozenHistoryEvaluatorCase,
    title="Investigate a 12-hour TiDB transaction alert whose current window is quiet.",
    alert=(
        "[CRITICAL] [Commerce transaction path] A 12-hour review window contains intermittent commit and "
        "Prewrite failures across catalog, inventory, pricing, and order traffic. The current handoff window "
        "is quiet, but the business path still reports a historical reliability regression. Use the frozen "
        "metric overview to select a bounded UTC evidence window, correlate component records and current "
        "catalog state, separate the primary cause from same-code neighbors, and restore service without "
        "changing business rows or broadening the blast radius. The task permits only reversible, bounded "
        "operational changes on evidence-identified objects or settings; preserve the "
        "same-domain auxiliary cache, cluster topology, and historical telemetry. Verify the fresh replay, "
        "business truth, schema, TSO, and workload before submitting."
    ),
    initial_state={
        "status": "historical_investigation_pending",
        "symptoms": ("historical 2PC/Prewrite failures", "intermittent business errors", "current window quiet"),
        "tidb_instances": 2,
        "history_duration_hours": 12,
    },
    expected_target={
        "status": "recovered",
        "causal_cache_policy": "all three causal tables NOCACHE or global lease in 6..30",
        "auxiliary_cache": "CACHED ON",
        "business_truth": "unchanged",
        "fresh_replay": "no dual-endpoint cache conflicts",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_PROFILES,
        worker_count=12,
        seed=20260816,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        warmup_seconds=180,
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=120,
        readiness_timeout_seconds=3600,
    ),
    reference_report=_REFERENCE_REPORT,
    frozen_history=_HISTORY,
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.829167,
        reference_run_ids=("UNMEASURED: TiDB capture was not run; difficulty values are design estimates",),
    ),
    db=_TABLES.db,
    cache_table=_TABLES.catalog,
    cache_table_names=_TABLES.causal,
    pricing_table=_TABLES.pricing,
    healthy_cache_table_names=(_TABLES.healthy_aux,),
    orders_table=_TABLES.orders,
    inventory_table=_TABLES.inventory,
    catalog_row_count=192,
    business_summary_sql=business_summary_sql(_TABLES),
    table_integrity_sql=table_integrity_sql(_TABLES),
    target_profile_names=_TARGET_PROFILE_NAMES,
    recovery_lease_seconds=6,
    recovery_lease_max_seconds=30,
)

_NARROW_CATALOG_CASE = replace(
    _CASE,
    case_id="table_cache_lease_narrow_catalog_investigation",
    case_no=1,
    evaluator=TidbSystemFailureTableCacheLeaseNarrowCatalogEvaluatorCase,
    title="Investigate shared cached-table lease contention over a smaller commerce catalog.",
    catalog_row_count=96,
    target_profile_names=_CASE.target_profile_names[:8],
    background_workload=replace(_CASE.background_workload, worker_count=8),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.763636,
        reference_run_ids=('UNMEASURED: TiDB capture was not run; difficulty values are design estimates',),
        protocol_version='difficulty-v2',
    ),
)


class TidbSystemFailureTableCacheLeaseFrozenHistoryScenario(TiDBScenario):
    scenario_id = "tidb_system_failure_table_cache_lease_frozen_history"
    description = "Investigate a historical TiDB transaction reliability regression under mixed commerce traffic."
    cases = (_CASE, _NARROW_CATALOG_CASE)

    def build_fault_plan(self, case: TidbSystemFailureTableCacheLeaseFrozenHistoryInvestigationScenarioCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureTableCacheLeaseFrozenHistoryInjector,
                config={
                    "db": case.db,
                    "catalog_table": case.cache_table,
                    "cache_table_names": case.cache_table_names,
                    "inventory_table": case.inventory_table,
                    "pricing_table": case.pricing_table,
                    "orders_table": case.orders_table,
                    "healthy_aux_table": case.healthy_cache_table_names[0],
                    "catalog_row_count": case.catalog_row_count,
                    "target_profile_names": case.target_profile_names,
                    "recovery_lease_seconds": case.recovery_lease_seconds,
                    "recovery_lease_max_seconds": case.recovery_lease_max_seconds,
                },
            ),
        )


class TidbSystemFailureTableCacheLeaseFrozenHistoryInjector(BaseFaultInjector):

    retain_workload_after_metric_history = True

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""
    """Create the persistent cached-table state and a deterministic target capture."""

    def __init__(self) -> None:
        self.tables: TableCacheLeaseTables | None = None
        self.catalog_row_count = 0
        self.target_profile_names: tuple[str, ...] = ()
        self.recovery_lease_seconds = 0
        self.recovery_lease_max_seconds = 0
        self._configured = False
        self._activated = False
        self._business_stop = threading.Event()
        self._causal_stop = threading.Event()
        self._business_gate = threading.Event()
        self._business_thread: threading.Thread | None = None
        self._causal_thread: threading.Thread | None = None
        self._business_failure: BaseException | None = None
        self._causal_failure: BaseException | None = None
        self._business_conflicts = 0
        self._causal_conflicts: dict[str, int] = {}

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        create_and_seed_schema(context.env, self.tables, self.catalog_row_count)
        enable_cache_and_verify(context.env, self.tables)
        self._configured = True

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        if not self._configured:
            raise RuntimeError("table-cache-lease activation requires completed persistent installation")
        self._verify_persistent_state(context.env)
        self._activated = True

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        if not self._activated:
            raise RuntimeError("table-cache-lease observability requires activated persistent state")
        self._verify_persistent_state(context.env)
        state = cache_state(context.env, self.tables)
        self._start_target_runtime(context.env)
        lease_rows = execute_result_rows(
            context.env.execute_sql,
            "SHOW GLOBAL VARIABLES LIKE 'tidb_table_cache_lease'",
            "capture table-cache-lease lease variable",
        )
        return {
            "ma01_table_ids": {table: int(value["table_id"]) for table, value in state.items()},
            "ma01_cache_state": state,
            "ma01_business_truth": capture_business_truth(context.env, self.tables),
            "ma01_lease_variable": lease_rows,
            "ma01_history_contract": {
                "duration_seconds": _HISTORY.duration_seconds,
                "target_age_seconds_range": _HISTORY.target_age_seconds_range,
                "record_sources": [source.value for source in _HISTORY.record_sources],
                "current_handoff": "target runtime quiesces before the Agent handoff; persistent cache state remains unchanged",
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_target_runtime()

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._stop_target_runtime()
        drop_schema(context.env, self.tables)
        self._configured = False
        self._activated = False

    def _configure(self, config: Mapping[str, object]) -> None:
        self.tables = configure_tables(config)
        self.catalog_row_count = int(config["catalog_row_count"])
        self.target_profile_names = tuple(validate_sql_identifier(str(item), "target profile") for item in config["target_profile_names"])
        self.recovery_lease_seconds = int(config["recovery_lease_seconds"])
        self.recovery_lease_max_seconds = int(config["recovery_lease_max_seconds"])

    def _verify_persistent_state(self, env: object) -> None:
        lease_rows = execute_result_rows(
            env.execute_sql,
            "SHOW GLOBAL VARIABLES LIKE 'tidb_table_cache_lease'",
            "verify table-cache-lease persistent lease",
        )
        lease_row = require_one_result_row(lease_rows, "verify table-cache-lease persistent lease")
        if int(lease_row[1]) != 3:
            raise RuntimeError(f"table-cache-lease persistent state must retain lease=3 before remediation: rows={lease_rows!r}")
        observed = cache_state(env, self.tables)
        missing = [table for table in self.tables.cached if not observed[table]["cached_on"]]
        if missing:
            raise RuntimeError(f"table-cache-lease persistent state lost cache markers: missing={missing!r}, state={observed!r}")

    def _start_target_runtime(self, env: object) -> None:
        if self._business_thread is not None or self._causal_thread is not None:
            raise RuntimeError("table-cache-lease target runtime is already running")
        self._business_stop.clear()
        self._causal_stop.clear()
        self._business_gate.clear()
        self._business_failure = None
        self._causal_failure = None
        self._business_conflicts = 0
        self._causal_conflicts = {table: 0 for table in self.tables.causal}
        self._business_thread = threading.Thread(target=self._business_phase, args=(env,), name="orders-phase", daemon=True)
        self._causal_thread = threading.Thread(target=self._causal_phase, args=(env,), name="cache-phase", daemon=True)
        self._business_thread.start()
        self._causal_thread.start()

    def _business_phase(self, env: object) -> None:
        try:
            order_ids = tuple(18 + index % 8 for index in range(_ORDERS_PHASE_PROBE_COUNT))
            for order_id in order_ids:
                if self._business_stop.is_set():
                    return
                evidence = self._run_business_conflict_probe(env, order_id)
                self._business_conflicts += int(evidence["conflicts"])
                if self._business_stop.wait(0.25):
                    return
            self._business_gate.set()
            deadline = time.monotonic() + 320
            probe_index = 0
            while time.monotonic() < deadline and not self._business_stop.is_set():
                order_id = 18 + probe_index % 8
                evidence = self._run_business_conflict_probe(env, order_id)
                self._business_conflicts += int(evidence["conflicts"])
                probe_index += 1
                if self._business_stop.wait(_ORDERS_OVERLAP_INTERVAL_SECONDS):
                    return
        except BaseException as exc:
            self._business_failure = exc
            self._business_gate.set()

    def _causal_phase(self, env: object) -> None:
        try:
            if not self._business_gate.wait(450):
                raise RuntimeError("table-cache-lease causal phase did not observe the deterministic orders phase gate")
            deadline = time.monotonic() + 320
            round_no = 0
            while time.monotonic() < deadline and not self._causal_stop.is_set():
                table = self.tables.causal[round_no % len(self.tables.causal)]
                result = dual_cache_read_replay(env, self.tables, ("tidb/tidb-0", "tidb/tidb-1"), rounds=1)
                self._causal_conflicts[table] += int(result[table])
                round_no += 1
                if self._causal_stop.wait(0.35):
                    return
        except BaseException as exc:
            self._causal_failure = exc

    def _stop_target_runtime(self) -> None:
        self._business_stop.set()
        self._causal_stop.set()
        if self._business_thread is not None:
            join_thread(self._business_thread, 90, "table-cache-lease orders phase")
            self._business_thread = None
        if self._causal_thread is not None:
            join_thread(self._causal_thread, 90, "table-cache-lease cache phase")
            self._causal_thread = None
        if self._business_failure is not None:
            raise RuntimeError(f"table-cache-lease orders phase failed: error={self._business_failure!r}") from self._business_failure
        if self._causal_failure is not None:
            raise RuntimeError(f"table-cache-lease cache phase failed: error={self._causal_failure!r}") from self._causal_failure

    def _run_business_conflict_probe(self, env: object, order_id: int) -> dict[str, int]:
        targets = ("tidb/tidb-0", "tidb/tidb-1")
        baseline_connection = env.open_workload_connection("orders-baseline", target=targets[0])
        try:
            with baseline_connection.cursor() as cursor:
                cursor.execute(f"SELECT write_attempts FROM {self.tables.db}.{self.tables.orders} WHERE order_id = {order_id}")
                baseline = int(cursor.fetchone()[0])
                baseline_connection.rollback()
        finally:
            baseline_connection.close()
        barrier = threading.Barrier(2, timeout=30)
        write_barrier = threading.Barrier(2, timeout=30)
        first_commit = threading.Event()
        failures: list[BaseException] = []
        counts = {"commits": 0, "conflicts": 0, "retries": 0}
        lock = threading.Lock()

        def worker(worker_id: int, target: str) -> None:
            connection = env.open_workload_connection(f"orders-worker-{worker_id}", target=target)
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SET SESSION tidb_txn_mode = 'OPTIMISTIC'")
                    cursor.execute("START TRANSACTION")
                    cursor.execute(f"SELECT write_attempts FROM {self.tables.db}.{self.tables.orders} WHERE order_id = {order_id}")
                    cursor.fetchall()
                    barrier.wait()
                    try:
                        cursor.execute(
                            f"UPDATE {self.tables.db}.{self.tables.orders} "
                            f"SET write_attempts = write_attempts + 1 WHERE order_id = {order_id}"
                        )
                        write_barrier.wait()
                        if worker_id == 1 and not first_commit.wait(30):
                            raise RuntimeError(f"table-cache-lease orders probe timed out waiting for first commit: order_id={order_id}")
                        connection.commit()
                    except pymysql.MySQLError as exc:
                        code = exc.args[0] if exc.args else None
                        if code != 9007:
                            raise RuntimeError(
                                "table-cache-lease orders probe returned an unexpected SQL error: "
                                f"order_id={order_id}, worker={worker_id}, code={code!r}, error={exc}"
                            ) from exc
                        connection.rollback()
                        with lock:
                            counts["conflicts"] += 1
                        cursor.execute("START TRANSACTION")
                        cursor.execute(
                            f"UPDATE {self.tables.db}.{self.tables.orders} "
                            f"SET write_attempts = write_attempts + 1 WHERE order_id = {order_id}"
                        )
                        connection.commit()
                        with lock:
                            counts["retries"] += 1
                    else:
                        with lock:
                            counts["commits"] += 1
                    finally:
                        if worker_id == 0:
                            first_commit.set()
            except BaseException as exc:
                failures.append(exc)
                barrier.abort()
                write_barrier.abort()
            finally:
                connection.close()

        threads = tuple(
            threading.Thread(target=worker, args=(worker_id, target), name=f"orders-{worker_id}", daemon=True)
            for worker_id, target in enumerate(targets)
        )
        for thread in threads:
            thread.start()
        for thread in threads:
            join_thread(thread, 60, f"table-cache-lease orders probe {thread.name}")
        if failures:
            raise RuntimeError(f"table-cache-lease orders probe failed: order_id={order_id}, failures={failures!r}") from failures[0]
        if counts["conflicts"] < 1 or counts["retries"] < 1:
            raise RuntimeError(f"table-cache-lease orders probe did not produce a retryable 9007: order_id={order_id}, counts={counts!r}")
        restore = env.open_workload_connection("orders-restore", target=targets[0])
        try:
            with restore.cursor() as cursor:
                cursor.execute(
                    f"UPDATE {self.tables.db}.{self.tables.orders} SET write_attempts = {baseline} WHERE order_id = {order_id}"
                )
            restore.commit()
        finally:
            restore.close()
        return counts


__all__ = (
    "TidbSystemFailureTableCacheLeaseFrozenHistoryInvestigationScenarioCase",
    "TidbSystemFailureTableCacheLeaseFrozenHistoryInjector",
    "TidbSystemFailureTableCacheLeaseFrozenHistoryScenario",
)
