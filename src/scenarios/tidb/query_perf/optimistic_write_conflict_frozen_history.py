import threading
from collections.abc import Mapping
from dataclasses import dataclass, replace

import pymysql

from src.scenarios.evaluation.tidb.query_perf.optimistic_write_conflict_frozen_history import (
    TidbQueryPerfOptimisticWriteConflictFrozenHistoryEvaluatorCase,
    TidbQueryPerfOptimisticWriteConflictFrozenHistoryHotspotEvaluatorCase,
)
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    connect_tidb,
    join_thread,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)
from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase, WorkloadProfile

from ...base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime
from src.execution.history.records import HistoricalRecordSource


class TidbQueryPerfOptimisticWriteConflictFrozenHistoryInjector(BaseFaultInjector):
    """Create real commit-time conflicts while restoring both rows after every round."""

    retain_workload_after_metric_history = True

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""

    @staticmethod
    def _is_expected_transient_conflict(exc: pymysql.MySQLError) -> bool:
        code = exc.args[0]
        return code == 9007 or (
            code == 8022 and "txnlocknotfound" in str(exc).casefold()
        )

    def __init__(self):
        self._threads: tuple[threading.Thread, ...] = ()
        self._barriers: list[threading.Barrier] = []
        self._stop_event = threading.Event()
        self._stats_lock = threading.Lock()
        self._failures: list[Exception] = []
        self._target_stats = {"conflicts": 0, "commits": 0}
        self._competing_stats = {"conflicts": 0, "commits": 0}

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_schema(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_rows(context.env)
        self._start_runtime(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        rows = json_object(
            context.env.execute_sql(
                f"SELECT id, tenant, v, last_writer, payload FROM {self.db}.{self.table} "
                f"WHERE id IN ({self.target_id}, {self.competing_id}) ORDER BY id"
            ),
            "capture frozen-history account rows",
        )
        mode = json_object(
            context.env.execute_sql("SELECT @@tidb_txn_mode"),
            "capture current TiDB transaction mode",
        )
        retry = json_object(
            context.env.execute_sql("SHOW VARIABLES LIKE 'tidb_retry_limit'"),
            "capture TiDB retry limit",
        )
        self._verify_rows(context.env)
        self._start_runtime(context.env)
        return {
            "fault_target_probe": self._target_stats,
            "fault_competing_probe": self._competing_stats,
            "fault_rows_at_observation": rows["result"],
            "fault_transaction_mode": mode["result"],
            "fault_retry_limit": int(retry["result"][0][1]),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime(context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime(context.env)
        self._configure(context.config)
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"),
            f"drop frozen-history conflict database {self.db}",
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.target_id = int(config["target_id"])
        self.competing_id = int(config["competing_id"])
        self.target_tenant = str(config["target_tenant"])
        self.competing_tenant = str(config["competing_tenant"])
        self.probe_rounds = int(config["probe_rounds"])
        self.minimum_conflicts = int(config["minimum_conflicts"])

    def _create_schema(self, env) -> None:
        require_sql_success(
            env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {self.db}"),
            f"create frozen-history conflict database {self.db}",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.table}"),
            f"drop stale frozen-history conflict table {self.db}.{self.table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.table} ("
                "id BIGINT PRIMARY KEY, tenant VARCHAR(64) NOT NULL, v BIGINT NOT NULL, "
                "last_writer VARCHAR(64) NOT NULL, payload VARCHAR(128) NOT NULL, "
                "CHECK (v >= 0))"
            ),
            f"create frozen-history conflict table {self.db}.{self.table}",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.table} (id, tenant, v, last_writer, payload) VALUES "
                f"({self.target_id}, '{self.target_tenant}', 0, 'seed', 'account-refresh'), "
                f"({self.competing_id}, '{self.competing_tenant}', 0, 'seed', 'inventory-reconcile'), "
                "(11, 'normal-a', 0, 'seed', 'healthy-a'), "
                "(59, 'normal-b', 0, 'seed', 'healthy-b'), "
                "(91, 'normal-c', 0, 'seed', 'healthy-c')"
            ),
            f"seed frozen-history conflict rows in {self.db}.{self.table}",
        )
        self._verify_rows(env)

    def _verify_rows(self, env) -> None:
        result = json_object(
            env.execute_sql(
                f"SELECT id, tenant, v, last_writer FROM {self.db}.{self.table} "
                f"WHERE id IN ({self.target_id}, {self.competing_id}) ORDER BY id"
            ),
            "verify frozen-history conflict rows",
        )["result"]
        expected = [
            [self.target_id, self.target_tenant, 0, "seed"],
            [self.competing_id, self.competing_tenant, 0, "seed"],
        ]
        if result != expected:
            raise RuntimeError(
                "Frozen-history conflict rows are not at the expected quiescent state: "
                f"database={self.db!r}, table={self.table!r}, expected={expected!r}, actual={result!r}"
            )

    def _start_runtime(self, env) -> None:
        if self._threads:
            raise RuntimeError(
                f"Frozen-history conflict runtime is already running: database={self.db!r}, table={self.table!r}"
            )
        self._stop_event.clear()
        self._failures.clear()
        self._target_stats.update(conflicts=0, commits=0)
        self._competing_stats.update(conflicts=0, commits=0)
        target_thread = threading.Thread(
            target=self._probe_loop,
            args=(env, self.target_id, self.target_tenant, "account-refresh", self._target_stats, "target"),
            name="qp01-frozen-history-target-probe",
            daemon=True,
        )
        competing_thread = threading.Thread(
            target=self._probe_loop,
            args=(env, self.competing_id, self.competing_tenant, "inventory-reconcile", self._competing_stats, "competing"),
            name="qp01-frozen-history-competing-probe",
            daemon=True,
        )
        self._threads = (target_thread, competing_thread)
        for thread in self._threads:
            thread.start()

    def _probe_loop(self, env, row_id: int, tenant: str, application: str, stats: dict[str, int], role: str) -> None:
        start_barrier = threading.Barrier(2, timeout=30)
        commit_barrier = threading.Barrier(2, timeout=30)
        reset_barrier = threading.Barrier(2, timeout=30)
        self._barriers.extend((start_barrier, commit_barrier, reset_barrier))
        failures: list[Exception] = []
        worker_threads = tuple(
            threading.Thread(
                target=self._probe_worker,
                args=(
                    env,
                    row_id,
                    tenant,
                    application,
                    stats,
                    worker_id,
                    start_barrier,
                    commit_barrier,
                    reset_barrier,
                    failures,
                ),
                name=f"qp01-{role}-worker-{worker_id}",
                daemon=True,
            )
            for worker_id in (0, 1)
        )
        for thread in worker_threads:
            thread.start()
        for thread in worker_threads:
            thread.join()
        if failures:
            with self._stats_lock:
                self._failures.extend(failures)
            self._stop_event.set()

    def _probe_worker(
        self,
        env,
        row_id: int,
        tenant: str,
        application: str,
        stats: dict[str, int],
        worker_id: int,
        start_barrier: threading.Barrier,
        commit_barrier: threading.Barrier,
        reset_barrier: threading.Barrier,
        failures: list[Exception],
    ) -> None:
        connection = None
        try:
            connection = connect_tidb(
                env,
                database=self.db,
                autocommit=False,
                application_name=application,
                read_timeout=90,
                write_timeout=90,
            )
            with connection.cursor() as cursor:
                cursor.execute("SET SESSION tidb_txn_mode = 'OPTIMISTIC'")
                for round_no in range(self.probe_rounds):
                    if self._stop_event.is_set():
                        return
                    cursor.execute("START TRANSACTION")
                    cursor.execute(
                        f"UPDATE {self.db}.{self.table} SET v = v + 1, last_writer = %s "
                        f"WHERE id = %s AND tenant = %s AND "
                        f"{'id = id' if worker_id == 0 else 'v >= 0'}",
                        (f"{application}-{worker_id}", row_id, tenant),
                    )
                    self._wait_at_barrier(start_barrier, role=application, phase="write", round_no=round_no)
                    try:
                        connection.commit()
                    except pymysql.MySQLError as exc:
                        code = exc.args[0] if exc.args else None
                        if not self._is_expected_transient_conflict(exc):
                            raise RuntimeError(
                                "Frozen-history conflict probe returned an unexpected TiDB error: "
                                f"application={application!r}, worker={worker_id}, round={round_no}, "
                                f"code={code!r}, error={exc}"
                            ) from exc
                        connection.rollback()
                        with self._stats_lock:
                            stats["conflicts"] += 1
                    else:
                        with self._stats_lock:
                            stats["commits"] += 1
                    self._wait_at_barrier(commit_barrier, role=application, phase="commit", round_no=round_no)
                    if worker_id == 0:
                        cursor.execute("START TRANSACTION")
                        cursor.execute(
                            f"UPDATE {self.db}.{self.table} SET v = 0, last_writer = 'seed' WHERE id = %s",
                            (row_id,),
                        )
                        try:
                            connection.commit()
                        except pymysql.MySQLError as exc:
                            code = exc.args[0] if exc.args else None
                            if not self._is_expected_transient_conflict(exc):
                                raise RuntimeError(
                                    "Frozen-history conflict reset returned an unexpected TiDB error: "
                                    f"application={application!r}, worker={worker_id}, round={round_no}, "
                                    f"code={code!r}, error={exc}"
                                ) from exc
                            connection.rollback()
                    self._wait_at_barrier(reset_barrier, role=application, phase="reset", round_no=round_no)
        except Exception as exc:
            if not self._stop_event.is_set():
                failures.append(exc)
                self._stop_event.set()
                for barrier in (start_barrier, commit_barrier, reset_barrier):
                    barrier.abort()
        finally:
            if connection is not None:
                connection.close()

    def _wait_at_barrier(self, barrier: threading.Barrier, *, role: str, phase: str, round_no: int) -> None:
        try:
            barrier.wait()
        except threading.BrokenBarrierError as exc:
            if self._stop_event.is_set():
                raise
            raise RuntimeError(
                "Frozen-history conflict probe barrier broke unexpectedly: "
                f"role={role!r}, phase={phase!r}, round={round_no}"
            ) from exc

    def _stop_runtime(self, env) -> None:
        had_runtime = bool(self._threads)
        self._stop_event.set()
        for barrier in self._barriers:
            barrier.abort()
        for thread in self._threads:
            join_thread(thread, 30, f"frozen-history conflict worker {thread.name}")
        self._threads = ()
        self._barriers = []
        self._reset_rows(env)
        if self._failures:
            failures = tuple(self._failures)
            self._failures.clear()
            raise RuntimeError(
                f"Frozen-history conflict runtime failed: database={self.db!r}, table={self.table!r}, failures={failures!r}"
            ) from failures[0]
        if had_runtime:
            observed = {
                "target": dict(self._target_stats),
                "competing": dict(self._competing_stats),
            }
            if any(
                stats["conflicts"] < self.minimum_conflicts
                for stats in observed.values()
            ):
                raise RuntimeError(
                    "Frozen-history conflict runtime did not reach the required real conflict count: "
                    f"database={self.db!r}, table={self.table!r}, required={self.minimum_conflicts}, "
                    f"observed={observed!r}"
                )

    def _reset_rows(self, env) -> None:
        connection = connect_tidb(env, database=self.db, autocommit=True)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE {self.db}.{self.table} SET v = 0, last_writer = 'seed' "
                    f"WHERE id IN ({self.target_id}, {self.competing_id})"
                )
        finally:
            connection.close()


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfOptimisticWriteConflictFrozenHistoryForHistoryInvestigationScenarioCase(TiDBScenarioCase):
    db: str
    table: str
    target_id: int
    competing_id: int
    target_tenant: str
    competing_tenant: str
    target_payload: str
    competing_payload: str
    healthy_ids: tuple[int, ...]
    probe_rounds: int
    minimum_conflicts: int


_DB = "benchops_mf_qp02"
_TABLE = "mf_qp02_account_refresh"
_TARGET_ID = 41
_COMPETING_ID = 73
_TARGET_TENANT = "account-refresh"
_COMPETING_TENANT = "inventory-reconcile"
_TARGET_UPDATE_SQL = (
    f"UPDATE {_DB}.{_TABLE} SET v = v + 1, last_writer = 'account-refresh' "
    f"WHERE id = {_TARGET_ID} AND tenant = '{_TARGET_TENANT}' AND id = id"
)
_COMPETING_UPDATE_SQL = (
    f"UPDATE {_DB}.{_TABLE} SET v = v + 1, last_writer = 'inventory-reconcile' "
    f"WHERE id = {_COMPETING_ID} AND tenant = '{_COMPETING_TENANT}' AND v >= 0"
)

_REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "root_cause",
                "factor": "historical conflict window",
                "entity": "12-hour historical window",
                "evidence": ["conflict and abort rates rise before retry and latency"],
            },
            {
                "type": "root_cause",
                "factor": "target key id=41",
                "entity": "id=41",
                "evidence": ["account-refresh target is id=41"],
            },
            {
                "type": "root_cause",
                "factor": "competing key id=73 is a decoy",
                "entity": "id=73",
                "evidence": ["inventory-reconcile id=73 is a competing key, not the repair target"],
            },
            {
                "type": "root_cause",
                "factor": "same-key concurrent writes hit an optimistic commit-time conflict 9007",
                "entity": "TiDB optimistic commit",
                "evidence": ["the write conflict happens at optimistic commit rather than at a lock wait"],
            },
            {
                "type": "root_cause",
                "factor": "optimistic write conflicts cause retries and aborts and lower successful write throughput",
                "entity": "account-refresh write path",
                "evidence": ["retry amplification is downstream of commit conflicts"],
            },
            {
                "type": "root_cause",
                "factor": "connection surge, DDL latency, pessimistic wait, CPU and disk are excluded as primary causes",
                "entity": "competing hypotheses",
                "evidence": ["same-table competing key and unrelated maintenance are competing hypotheses, not the target root cause"],
            },
            {
                "type": "root_cause",
                "factor": "current no lock waits do not disprove the historical conflict",
                "entity": "current TiDB state",
                "evidence": ["the target row can be unlocked now while its historical optimistic conflict remains causal"],
            },
        ]
    },
    "outcome": {
        "changes": ["completed two v=v+1 increments only for id=41 in a transaction-local pessimistic session"],
        "verification": ["verified id=41 has v=2 and id=73 plus healthy rows are unchanged"],
    },
    "summary": "The ended incident was a same-key optimistic commit conflict for id=41; id=73 was a competing decoy.",
}

_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="account_refresh_update",
            sql=_TARGET_UPDATE_SQL,
            qps=0.75,
            tier="BUSINESS_WRITE",
            application_name="account-refresh",
            commit=False,
        ),
        WorkloadProfile(
            name="inventory_reconcile_update",
            sql=_COMPETING_UPDATE_SQL,
            qps=0.65,
            tier="BUSINESS_WRITE",
            application_name="inventory-reconcile",
            commit=False,
        ),
        WorkloadProfile(
            name="account_state_read",
            sql=(
                f"SELECT id, tenant, v, last_writer FROM {_DB}.{_TABLE} "
                f"WHERE id IN ({_TARGET_ID}, {_COMPETING_ID}) ORDER BY id"
            ),
            qps=0.45,
            tier="BUSINESS_READ",
            application_name="account-refresh-read",
        ),
        WorkloadProfile(
            name="retry_setting_observation",
            sql="SHOW VARIABLES LIKE 'tidb_retry_limit'",
            qps=0.35,
            tier="CONTROL_READ",
            application_name="incident-observer",
        ),
        WorkloadProfile(
            name="transaction_mode_observation",
            sql="SELECT @@tidb_txn_mode",
            qps=0.35,
            tier="CONTROL_READ",
            application_name="incident-observer",
        ),
        WorkloadProfile(
            name="uniform_key_refresh",
            sql=f"UPDATE {_DB}.{_TABLE} SET v = v + 1 WHERE id IN (11, 59, 91)",
            qps=0.55,
            tier="BACKGROUND_WRITE",
            application_name="batch-reconcile",
            commit=False,
        ),
        WorkloadProfile(
            name="connection_surge_probe",
            sql="SELECT 1",
            qps=1.5,
            tier="CONNECTION_PROBE",
            application_name="health-probe",
        ),
        WorkloadProfile(
            name="reset_marker_shape",
            sql=(
                f"UPDATE {_DB}.{_TABLE} SET v = 0, last_writer = 'seed' "
                f"WHERE id IN ({_TARGET_ID}, {_COMPETING_ID})"
            ),
            qps=0.15,
            tier="MAINTENANCE_WRITE",
            application_name="maintenance-reconcile",
            commit=False,
        ),
    ),
    worker_count=6,
    seed=20260816,
    start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    warmup_seconds=5,
)


_CASE = TidbQueryPerfOptimisticWriteConflictFrozenHistoryForHistoryInvestigationScenarioCase(
    case_id="optimistic_write_conflict_history_investigation",
    case_no=0,
    evaluator=TidbQueryPerfOptimisticWriteConflictFrozenHistoryEvaluatorCase,
    title="Historical optimistic-write conflict investigation with two incomplete increments.",
    alert=(
        "[SEV1] 过去 12 小时 account refresh 接口出现过多次 p95 波动，其中一次伴随成功吞吐下降；"
        "当前没有活跃锁等待，但仍有两次业务 increment 尚待可靠补做。请定位已经结束的事故窗口、"
        "受影响的业务实体与数据库机制，并在题面授权的两行范围内安全完成补偿。"
    ),
    initial_state={
        "historical_incident": "ended",
        "active_lock_waits": "normal",
        "pending_increments": 2,
        "authorized_rows": [_TARGET_ID],
    },
    expected_target={
        "target_row": _TARGET_ID,
        "target_v": 2,
        "competing_row_unchanged": _COMPETING_ID,
        "transaction_scope": "session_or_transaction_local_pessimistic",
    },
    background_workload=_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=180,
        image_group_key="qp01-frozen-history-optimistic-write-v1",
    ),
        frozen_history=FrozenHistorySpec(
        schema_version=1,
        duration_seconds=43_200,
        normal_capture_seconds=60,
        fault_capture_seconds=120,
        base_step_seconds=2,
        overview_step_seconds=300,
        block_min_seconds=30,
        block_max_seconds=60,
        transition_seconds=10,
        target_age_seconds_range=(1_200, 3_600),
        required_metrics=(
            "transaction_commit",
            "qps",
            "query_latency",
            "active_connections",
            "cpu",
            "disk_io",
        ),
        record_sources=(
            HistoricalRecordSource.COMPONENT_LOG,
            HistoricalRecordSource.TOPSQL,
            HistoricalRecordSource.SLOW_QUERIES,
        ),
        # Pin the node-level metrics to database nodes like the RG05
        # investigation case does: the default expansion includes the
        # monitoring containers, and cAdvisor intermittently stops exporting
        # its own container's filesystem series for minutes, which hard-fails
        # the disk_io capture (measured, 2026-09-29 pilot runs).
        metric_targets={
            "cpu": (
                "tidb/tidb-0",
                "tidb/tidb-1",
                "tikv/tikv-0",
                "tikv/tikv-1",
                "tikv/tikv-2",
            ),
            "disk_io": ("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
        },
        decoys=(
            HistoryDecoySpec(
                decoy_id="latency-maintenance",
                kind=DecoyKind.METRIC_ONLY,
                metric="query_latency",
                field="p99_ms",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=2,
                duration_seconds=60,
                amplitude_mad=2.5,
            ),
        ),
        max_points_per_series=1_200,
        max_scalar_samples_per_response=20_000,
        max_history_records_per_response=320,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.761111,
        reference_run_ids=(
            "reference-214__tidb_query_perf_optimistic_write_conflict_frozen_history__optimistic_write_conflict_history_investigation__mock_reference__r001",
        ),
    ),
    reference_report=_REFERENCE_REPORT,
    db=_DB,
    table=_TABLE,
    target_id=_TARGET_ID,
    competing_id=_COMPETING_ID,
    target_tenant=_TARGET_TENANT,
    competing_tenant=_COMPETING_TENANT,
    target_payload="account-refresh",
    competing_payload="inventory-reconcile",
    healthy_ids=(11, 59, 91),
    probe_rounds=32,
    minimum_conflicts=20,
)

_HOTSPOT_WORKLOAD = replace(
    _BACKGROUND_WORKLOAD,
    profiles=tuple(
        replace(profile, qps=profile.qps * 0.7)
        for profile in _BACKGROUND_WORKLOAD.profiles
        if profile.name not in {"connection_surge_probe", "reset_marker_shape"}
    ),
    worker_count=4,
    seed=20260901,
)
_HOTSPOT_CASE = replace(
    _CASE,
    case_id="optimistic_write_conflict_hotspot_history_investigation",
    case_no=1,
    evaluator=TidbQueryPerfOptimisticWriteConflictFrozenHistoryHotspotEvaluatorCase,
    title="Investigate a concentrated optimistic-write hotspot and compensate only its authorized key.",
    alert=(
        "[SEV2] 过去 6 小时 account refresh 的一个热点实体出现短时成功吞吐下降；当前没有活跃锁等待，"
        "但仍有两次 increment 待补做。请从冻结历史中区分真实提交冲突与一次维护延迟窗口，并只在授权行完成补偿。"
    ),
    background_workload=_HOTSPOT_WORKLOAD,
    frozen_history=replace(
        _CASE.frozen_history,
        duration_seconds=21_600,
        normal_capture_seconds=40,
        fault_capture_seconds=120,
        block_min_seconds=20,
        block_max_seconds=40,
        transition_seconds=20,
        overview_step_seconds=180,
        target_age_seconds_range=(900, 2_400),
        decoys=tuple(
            replace(decoy, duration_seconds=30)
            for decoy in _CASE.frozen_history.decoys
        ),
        metric_targets={
            "transaction_commit": (None,),
            "qps": (None,),
            "query_latency": (None,),
            "active_connections": (None,),
            "cpu": ("tidb/tidb-0", "tikv/tikv-0"),
            "disk_io": ("tikv/tikv-0",),
        },
        metric_rate_windows={
            "transaction_commit": 30,
            "qps": 30,
            "query_latency": 30,
            "cpu": 30,
            "disk_io": 30,
        },
    ),
    runtime=replace(_CASE.runtime, image_group_key="qp01-frozen-history-optimistic-hotspot-v1"),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.761905,
        reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
        protocol_version='difficulty-v2',
    ),
    probe_rounds=24,
    minimum_conflicts=14,
)


class TidbQueryPerfOptimisticWriteConflictFrozenHistoryScenario(TiDBScenario):
    scenario_id = "tidb_query_perf_optimistic_write_conflict_frozen_history"
    description = "Frozen-history historical investigation of an ended optimistic-write conflict incident."
    cases = (_CASE, _HOTSPOT_CASE)

    def build_fault_plan(
        self,
        case: TidbQueryPerfOptimisticWriteConflictFrozenHistoryForHistoryInvestigationScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbQueryPerfOptimisticWriteConflictFrozenHistoryInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "target_id": case.target_id,
                    "competing_id": case.competing_id,
                    "target_tenant": case.target_tenant,
                    "competing_tenant": case.competing_tenant,
                    "probe_rounds": case.probe_rounds,
                    "minimum_conflicts": case.minimum_conflicts,
                },
            ),
        )


__all__ = (
    "TidbQueryPerfOptimisticWriteConflictFrozenHistoryForHistoryInvestigationScenarioCase",
    "TidbQueryPerfOptimisticWriteConflictFrozenHistoryInjector",
    "TidbQueryPerfOptimisticWriteConflictFrozenHistoryScenario",
)
