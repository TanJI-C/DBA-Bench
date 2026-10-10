import json

import re

from collections.abc import Mapping

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.system_failure.pd_metadata_recovery import (
    TidbSystemFailureSf01ForPdMixedDiskEvictionEvaluatorCase,
    TidbSystemFailureSf01FocusedEvaluatorCase,
)
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureSf01Case(TiDBScenarioCase):
    db: str
    table: str
    reconciliation_table: str
    rollup_table: str
    exceptions_table: str
    row_count: int
    expected_amount_sum: int
    expected_checksum: int
    expected_region_count: int
    region_codes: tuple[str, ...]
    insert_row_id: int
    insert_amount: int
    insert_crc: int
    insert_region_code: str
    insert_settlement_day: str
    expected_exception_count: int
    expected_inserted_amount_sum: int
    expected_post_checksum: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureSf01ForPdMixedDiskEvictionScenarioCase(TidbSystemFailureSf01Case):
    pass


_TIDB_SYSTEM_FAILURE_SF01_CASE = TidbSystemFailureSf01ForPdMixedDiskEvictionScenarioCase(
    case_id="pd_mixed_disk_eviction",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "a PD/TiDB mixed-node storage fsync tail delayed PD heartbeat or lease handling before the PD term and leader changed",
                    "entity": "pd_mixed_disk_eviction",
                    "evidence": [
                        "scripted diagnostic actions observed the mixed-node storage fsync tail, delayed heartbeat handling, and the preceding term change"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the heartbeat and term change preceded the PD leader switch, which preceded the erroneous scheduler action",
                    "entity": "pd_mixed_disk_eviction",
                    "evidence": [
                        "scripted diagnostic actions observed heartbeat and term change before the PD leader switch and scheduler action"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the new PD leader attached evict-leader-scheduler to a healthy TiKV whose process and data stayed available after the stale health action",
                    "entity": "pd_mixed_disk_eviction",
                    "evidence": [
                        "scripted diagnostic actions observed the new PD leader attached evict-leader-scheduler to a healthy TiKV whose process and data stayed available"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "Region count and replica data stayed intact while leader count fell, so the incident is leader placement rather than Region loss",
                    "entity": "pd_mixed_disk_eviction",
                    "evidence": [
                        "scripted diagnostic actions observed Region count stayed intact while leader count fell, so the incident is leader placement rather than Region loss"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "applied the case-specific remediation"
            ],
            "verification": [
                "verified the case-specific final state"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbSystemFailureSf01ForPdMixedDiskEvictionEvaluatorCase,
    title="TiDB write latency and Region placement are unstable during a control-plane incident.",
    alert=(
        "[CRITICAL] A portion of TiDB write traffic has become slower and Region leadership is uneven, "
        "while TiDB/TiKV endpoints and most business reads remain available. The incident window also "
        "contains component restarts, placement changes, storage telemetry, and unrelated business "
        "reconciliation noise. Determine whether the dominant issue is data/replica health, placement "
        "state, node/storage behavior, or transient workload by correlating PD, TiKV, Region, latency, "
        "and log evidence before changing control-plane state. Restore stable service and complete the "
        "affected business integrity checks without changing unrelated data or metadata. Within the affected "
        "SF01 business scope, you are authorized to insert the required audit event and update the derived "
        "reconciliation controls after observing the live business aggregates; do not change historical rows "
        "or unrelated metadata."
    ),
    initial_state={
        "status": "healthy",
        "pd_leader": "stable",
        "tikv_leader_distribution": "balanced",
        "evict_leader_scheduler": "absent",
    },
    expected_target={
        "status": "recovered",
        "pd_scheduler": "injected eviction removed",
        "disk_fault": "repaired_or_isolated",
        "business_reconciliation": "all derived controls closed from base aggregates",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="sf01_business_recent_paid_orders",
                sql=(
                    "SELECT event_state, COUNT(*), SUM(event_amount) "
                    "FROM test.sf01_business_events "
                    "WHERE event_id BETWEEN 1 AND 1000 "
                    "GROUP BY event_state"
                ),
                qps=0.75,
                tier="BUSINESS_READ",
                application_name="sf01_order_dashboard",
            ),
            WorkloadProfile(
                name="sf01_business_settlement_dashboard",
                sql=(
                    "SELECT s.summary_id, s.order_count, s.paid_amount, s.checksum, "
                    "a.actual_count, a.actual_amount, a.actual_checksum "
                    "FROM test.sf01_settlement_summary s "
                    "JOIN (SELECT COUNT(*) actual_count, SUM(event_amount) actual_amount, "
                    "BIT_XOR(record_crc) actual_checksum FROM test.sf01_business_events "
                    "WHERE event_id <= 1000) a ON s.summary_id = 1"
                ),
                qps=0.45,
                tier="BUSINESS_READ",
                application_name="sf01_settlement_dashboard",
            ),
            WorkloadProfile(
                name="sf01_business_region_rollup_dashboard",
                sql=(
                    "SELECT r.region_code, r.event_count, r.paid_amount, r.checksum, "
                    "a.actual_count, a.actual_amount, a.actual_checksum "
                    "FROM test.sf01_region_audit_rollup r "
                    "JOIN (SELECT region_code, COUNT(*) actual_count, "
                    "SUM(event_amount) actual_amount, BIT_XOR(record_crc) actual_checksum "
                    "FROM test.sf01_business_events WHERE event_state = 'paid' "
                    "GROUP BY region_code) a ON a.region_code = r.region_code"
                ),
                qps=0.35,
                tier="BUSINESS_READ",
                application_name="sf01_region_audit_dashboard",
            ),
            WorkloadProfile(
                name="sf01_business_exception_queue",
                sql=(
                    "SELECT exception_id, control_name, scope_key, count_delta, "
                    "amount_delta, checksum_delta, status "
                    "FROM test.sf01_reconciliation_exceptions "
                    "WHERE status <> 'closed' OR count_delta <> 0 "
                    "OR amount_delta <> 0 OR checksum_delta <> 0 "
                    "ORDER BY exception_id"
                ),
                qps=0.3,
                tier="BUSINESS_READ",
                application_name="sf01_exception_worker",
            ),
            WorkloadProfile(
                name="sf01_business_reconciliation_drift",
                sql=(
                    "SELECT s.order_count - a.actual_count, "
                    "s.paid_amount - a.actual_amount, s.checksum ^ a.actual_checksum "
                    "FROM test.sf01_settlement_summary s "
                    "JOIN (SELECT COUNT(*) actual_count, SUM(event_amount) actual_amount, "
                    "BIT_XOR(record_crc) actual_checksum FROM test.sf01_business_events "
                    "WHERE event_id <= 1000) a ON s.summary_id = 1"
                ),
                qps=0.4,
                tier="BUSINESS_READ",
                application_name="sf01_reconciliation_worker",
            ),
            WorkloadProfile(
                name="sf01_business_point_lookup",
                sql=(
                    "SELECT event_id, event_amount, event_state, record_crc "
                    "FROM test.sf01_business_events "
                    "WHERE event_id IN (17, 101, 509, 997)"
                ),
                qps=1.15,
                tier="BUSINESS_READ",
                application_name="sf01_customer_support_lookup",
            ),
            WorkloadProfile(
                name="sf01_business_hot_row_touch",
                sql=(
                    "UPDATE test.sf01_business_events SET record_crc = record_crc "
                    "WHERE event_id IN (41, 241, 641)"
                ),
                qps=0.35,
                tier="BUSINESS_WRITE",
                commit=True,
                application_name="sf01_idempotent_settlement_worker",
            ),
            WorkloadProfile(
                name="sf01_business_region_probe",
                sql=(
                    "SELECT TABLE_NAME, COUNT(DISTINCT REGION_ID) "
                    "FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
                    "WHERE DB_NAME = 'test' AND TABLE_NAME IN "
                    "('sf01_business_events', 'sf01_settlement_summary', "
                    "'sf01_region_audit_rollup', 'sf01_reconciliation_exceptions') "
                    "GROUP BY TABLE_NAME"
                ),
                qps=0.3,
                tier="BUSINESS_READ",
                application_name="sf01_capacity_probe",
            ),
        ),
        worker_count=8,
        seed=0x5F01,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=0,
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=1,
        image_group_key="sf01-pd-mixed-disk-eviction",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.572316,
        reference_run_ids=(
            "reference-281__tidb_system_failure_sf01__pd_mixed_disk_eviction__mock__r001",
        ),
    ),
    db="test",
    table="sf01_business_events",
    reconciliation_table="sf01_settlement_summary",
    rollup_table="sf01_region_audit_rollup",
    exceptions_table="sf01_reconciliation_exceptions",
    row_count=1000,
    expected_amount_sum=11511500,
    expected_checksum=38174471,
    expected_region_count=16,
    region_codes=("north", "south", "east", "west"),
    insert_row_id=1001,
    insert_amount=23023,
    insert_crc=424242,
    insert_region_code="north",
    insert_settlement_day="2026-08-01",
    expected_exception_count=2,
    expected_inserted_amount_sum=11534523,
    expected_post_checksum=37750325,
)


_FOCUSED_SF01_WORKLOAD = replace(
    _TIDB_SYSTEM_FAILURE_SF01_CASE.background_workload,
    profiles=tuple(
        profile
        for profile in _TIDB_SYSTEM_FAILURE_SF01_CASE.background_workload.profiles
        if profile.name in {
            "sf01_business_recent_paid_orders",
            "sf01_business_settlement_dashboard",
            "sf01_business_region_rollup_dashboard",
            "sf01_business_exception_queue",
            "sf01_business_region_probe",
        }
    ),
    worker_count=4,
)

_FOCUSED_SF01_CASE = replace(
    _TIDB_SYSTEM_FAILURE_SF01_CASE,
    case_id="pd_mixed_disk_eviction_simple",
    case_no=1,
    evaluator=TidbSystemFailureSf01FocusedEvaluatorCase,
    background_workload=_FOCUSED_SF01_WORKLOAD,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": (
                        "a PD/TiDB mixed-node storage fsync tail delayed PD heartbeat or lease handling, the PD term "
                        "and leader then changed, and the new PD leader attached evict-leader-scheduler to a healthy "
                        "TiKV whose process and data stayed available after the stale health action"
                    ),
                    "entity": "pd_mixed_disk_eviction_simple",
                    "evidence": [
                        "pd log shows the mixed-node fsync tail and heartbeat delay preceding the term change, and "
                        "the new leader's scheduler action evicted leaders from a TiKV store that stayed Up"
                    ],
                },
                {
                    "type": "finding",
                    "factor": (
                        "Region count and replica data stayed intact while leader count fell, so the incident is "
                        "leader placement rather than Region loss"
                    ),
                    "entity": "pd_mixed_disk_eviction_simple",
                    "evidence": [
                        "region and store views show all Regions and replicas retained while only leader counts fell"
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "applied the case-specific remediation"
            ],
            "verification": [
                "verified the case-specific final state"
            ]
        },
        "summary": "The focused scripted mock completed its diagnosis and verification.",
    },
    alert=(
        _TIDB_SYSTEM_FAILURE_SF01_CASE.alert
        + " The authorized business repair scope for this focused case is one pending audit event: "
        "insert event_id=1002 with event_amount=24500, event_state='paid', record_crc=525252, "
        "region_code='north', and settlement_day='2026-08-01' into the business event table. "
        "Do not modify existing event_id <= 1000 or unrelated business tables. Rebuild the settlement "
        "summary and every region rollup from the base-table aggregate, use the table's legal status "
        "values, and close every reconciliation exception only after count, amount, and checksum deltas "
        "are zero."
    ),
    insert_row_id=1002,
    insert_amount=24500,
    insert_crc=525252,
    expected_inserted_amount_sum=11536000,
    expected_post_checksum=38698179,
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.497673,
        reference_run_ids=(
            "tidb-reference-7__"
            "tidb_system_failure_sf01__pd_mixed_disk_eviction_simple__mock__r001",
        ),
    ),
)


class TidbSystemFailureSf01PdMixedDiskEvictionInjector(BaseFaultInjector):
    """Create a mixed-node storage incident with a deterministic control-plane cascade."""

    _DISK_PID_FILE = "/tmp/aiopsbench-sf01-disk-fault.pid"
    _MAINTENANCE_PID_FILE = "/tmp/aiopsbench-sf01-maintenance-flush.pid"
    _BUFFER_FILE = "/data/pd/sf01-controller-buffer"
    _MAINTENANCE_SECONDS = 240
    _SCHEDULER_NAME = "evict-leader-scheduler"

    def __init__(self):
        self.db = None
        self.table = None
        self.reconciliation_table = None
        self.rollup_table = None
        self.exceptions_table = None
        self.row_count = None
        self.expected_amount_sum = None
        self.expected_checksum = None
        self.expected_region_count = None
        self.region_codes = None
        self.insert_amount = None
        self.insert_crc = None
        self.insert_region_code = None
        self.expected_exception_count = None
        self._baseline = None
        self._faulty_pd_target = None
        self._maintenance_pd_target = None
        self._evicted_store_id = None
        self._scheduler_id = None
        self._leader_schedule_limit = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        env = context.env
        deployment = env.deployment
        self._seed_business_tables(env)
        self._wait_for_regions(env)
        self._install_runtime_fault(context, self._capture_cluster_state(deployment))

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._install_runtime_fault(
            context,
            self._capture_cluster_state(context.env.deployment),
        )

    def _install_runtime_fault(self, context: FaultLifecycleContext, baseline: dict) -> None:
        env = context.env
        deployment = env.deployment
        self._baseline = baseline
        self._faulty_pd_target = baseline["leader_target"]
        self._maintenance_pd_target = self._pd_observer_target()
        self._evicted_store_id = self._select_eviction_store(baseline["stores"])
        self._leader_schedule_limit = self._read_leader_schedule_limit(deployment)
        self._set_leader_schedule_limit(deployment, 0)
        print(
            "[FaultInjector:TidbSystemFailureSf01PdMixedDiskEvictionInjector] "
            f"baseline leader={self._faulty_pd_target}, eviction_store={self._evicted_store_id}"
        )
        self._emit_phase_marker(
            deployment,
            self._maintenance_pd_target,
            phase="storage_flush",
            role="follower",
            term_epoch=0,
            raw_duration_ns=0,
        )
        self._start_maintenance_flush(deployment, self._maintenance_pd_target)
        self._start_disk_fault(deployment, self._faulty_pd_target)
        self._emit_phase_marker(
            deployment,
            self._faulty_pd_target,
            phase="storage_flush",
            role="leader",
            term_epoch=0,
            raw_duration_ns=0,
        )
        self._stop_disk_fault(deployment, self._faulty_pd_target)
        deployment.stop_component(self._faulty_pd_target)
        self._emit_phase_marker(
            deployment,
            self._maintenance_pd_target,
            phase="heartbeat_term",
            role="follower",
            term_epoch=1,
            raw_duration_ns=0,
        )
        deployment._wait(
            self._pd_observer_target(),
            lambda: self._leader_target(deployment) != self._faulty_pd_target,
            90,
        )
        leader_after_switch = self._leader_target(deployment)
        self._emit_phase_marker(
            deployment,
            self._maintenance_pd_target,
            phase="leader_change",
            role="leader",
            term_epoch=1,
            raw_duration_ns=0,
            leader=leader_after_switch,
        )
        deployment.start_component(self._faulty_pd_target)
        deployment._wait(
            "pd",
            deployment._check_pd,
            deployment.warm_tidb_readiness_timeout_sec,
        )
        self._start_disk_fault(
            deployment,
            self._faulty_pd_target,
            term_epoch=1,
            role="follower",
        )
        self._emit_phase_marker(
            deployment,
            self._faulty_pd_target,
            phase="storage_flush",
            role="follower",
            term_epoch=1,
            raw_duration_ns=0,
        )
        self._emit_phase_marker(
            deployment,
            self._faulty_pd_target,
            phase="heartbeat_term",
            role="follower",
            term_epoch=1,
            raw_duration_ns=0,
        )
        self._scheduler_id = self._SCHEDULER_NAME
        self._add_eviction_scheduler(deployment, self._evicted_store_id)
        self._emit_phase_marker(
            deployment,
            self._leader_target(deployment),
            phase="scheduler_create",
            role="leader",
            term_epoch=1,
            raw_duration_ns=0,
            store_id=self._evicted_store_id,
        )
        deployment._wait(
            "pd",
            lambda: self._eviction_is_visible(deployment),
            120,
        )
        print(
            "[FaultInjector:TidbSystemFailureSf01PdMixedDiskEvictionInjector] "
            f"PD disk fault on {self._faulty_pd_target} caused leader switch; "
            f"evicting leaders from healthy store_id={self._evicted_store_id}"
        )

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        return {
            "faulty_pd_target": self._faulty_pd_target,
            "evicted_store_id": self._evicted_store_id,
            "scheduler_id": self._scheduler_id,
            "baseline_leader_target": self._baseline["leader_target"],
            "baseline_stores": self._baseline["stores"],
            "expected_region_count": self.expected_region_count,
            "expected_amount_sum": self.expected_amount_sum,
            "expected_checksum": self.expected_checksum,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        deployment = context.env.deployment
        states = deployment.node_states()
        if states[self._faulty_pd_target]["running"]:
            self._stop_disk_fault(deployment, self._faulty_pd_target)
        if self._maintenance_pd_target is not None and states[self._maintenance_pd_target]["running"]:
            self._stop_maintenance_flush(deployment, self._maintenance_pd_target)
        if self._scheduler_id in self._scheduler_names(deployment):
            self._remove_eviction_scheduler(deployment, self._evicted_store_id)
        self._restore_leader_schedule_limit(deployment)

    def recover(self, context: FaultLifecycleContext) -> None:
        if self._faulty_pd_target is None:
            return
        deployment = context.env.deployment
        states = deployment.node_states()
        if not states[self._faulty_pd_target]["running"]:
            deployment.start_component(self._faulty_pd_target)
            deployment._wait(
                "pd",
                deployment._check_pd,
                deployment.warm_tidb_readiness_timeout_sec,
            )
        self._stop_disk_fault(deployment, self._faulty_pd_target)
        if self._maintenance_pd_target is not None:
            self._stop_maintenance_flush(deployment, self._maintenance_pd_target)
        if self._scheduler_id in self._scheduler_names(deployment):
            self._remove_eviction_scheduler(deployment, self._evicted_store_id)
        self._restore_leader_schedule_limit(deployment)

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "db")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.reconciliation_table = validate_sql_identifier(
            str(config["reconciliation_table"]), "reconciliation_table"
        )
        self.rollup_table = validate_sql_identifier(str(config["rollup_table"]), "rollup_table")
        self.exceptions_table = validate_sql_identifier(
            str(config["exceptions_table"]), "exceptions_table"
        )
        self.row_count = int(config["row_count"])
        self.expected_amount_sum = int(config["expected_amount_sum"])
        self.expected_checksum = int(config["expected_checksum"])
        self.expected_region_count = int(config["expected_region_count"])
        self.region_codes = tuple(str(region_code) for region_code in config["region_codes"])
        self.insert_amount = int(config["insert_amount"])
        self.insert_crc = int(config["insert_crc"])
        self.insert_region_code = str(config["insert_region_code"])
        self.expected_exception_count = int(config["expected_exception_count"])

    def _read_leader_schedule_limit(self, deployment) -> int:
        payload = deployment.pd_request("GET", "/pd/api/v1/config")
        return int(payload["schedule"]["leader-schedule-limit"])

    def _set_leader_schedule_limit(self, deployment, value: int) -> None:
        deployment.pd_request(
            "POST",
            "/pd/api/v1/config",
            {"schedule.leader-schedule-limit": int(value)},
        )

    def _restore_leader_schedule_limit(self, deployment) -> None:
        if self._leader_schedule_limit is None:
            raise RuntimeError("SF01 leader schedule limit was not captured before fault activation")
        self._set_leader_schedule_limit(deployment, self._leader_schedule_limit)

    def _seed_business_tables(self, env) -> None:
        for table in (
            self.exceptions_table,
            self.rollup_table,
            self.reconciliation_table,
            self.table,
        ):
            require_sql_success(
                env.execute_bootstrap_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"),
                f"clear SF01 table {table}",
            )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"CREATE TABLE {self.db}.{self.table} ("
                "event_id INT PRIMARY KEY, event_amount BIGINT NOT NULL, "
                "event_state ENUM('paid') NOT NULL, record_crc BIGINT NOT NULL, "
                "region_code VARCHAR(16) NOT NULL, settlement_day DATE NOT NULL)"
            ),
            "create SF01 business table",
        )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"CREATE TABLE {self.db}.{self.reconciliation_table} ("
                "summary_id INT PRIMARY KEY, scope_key VARCHAR(32) NOT NULL, "
                "order_count INT NOT NULL, "
                "paid_amount BIGINT NOT NULL, checksum BIGINT NOT NULL, "
                "last_event_id INT NOT NULL, status ENUM('open','closed') NOT NULL)"
            ),
            "create SF01 reconciliation table",
        )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"CREATE TABLE {self.db}.{self.rollup_table} ("
                "region_code VARCHAR(16) PRIMARY KEY, event_count INT NOT NULL, "
                "paid_amount BIGINT NOT NULL, checksum BIGINT NOT NULL, "
                "last_event_id INT NOT NULL, status ENUM('open','closed') NOT NULL)"
            ),
            "create SF01 region audit rollup table",
        )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"CREATE TABLE {self.db}.{self.exceptions_table} ("
                "exception_id INT PRIMARY KEY, control_name VARCHAR(64) NOT NULL, "
                "scope_key VARCHAR(32) NOT NULL, count_delta BIGINT NOT NULL, "
                "amount_delta BIGINT NOT NULL, checksum_delta BIGINT NOT NULL, "
                "status ENUM('open','closed') NOT NULL)"
            ),
            "create SF01 reconciliation exceptions table",
        )
        base_crc = {
            event_id: (event_id * 104729 + 17) % 2147483647
            for event_id in range(1, self.row_count + 1)
        }
        tuned_crc = self.expected_checksum
        for event_id in range(2, self.row_count + 1):
            tuned_crc ^= base_crc[event_id]
        base_crc[1] = tuned_crc
        rows = [
            f"({event_id},{10010 + event_id * 3},'paid',{base_crc[event_id]},"
            f"'{self._region_code(event_id)}','2026-07-31')"
            for event_id in range(1, self.row_count + 1)
        ]
        require_sql_success(
            env.execute_bootstrap_sql(f"INSERT INTO {self.db}.{self.table} VALUES " + ",".join(rows)),
            "load SF01 business truth",
        )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"INSERT INTO {self.db}.{self.reconciliation_table} "
                f"SELECT 1, 'all_paid', COUNT(*), SUM(event_amount), BIT_XOR(record_crc), "
                f"MAX(event_id), 'open' FROM {self.db}.{self.table} WHERE event_state = 'paid'"
            ),
            "load SF01 reconciliation truth",
        )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"INSERT INTO {self.db}.{self.rollup_table} "
                f"SELECT region_code, COUNT(*), SUM(event_amount), BIT_XOR(record_crc), "
                f"MAX(event_id), 'open' FROM {self.db}.{self.table} "
                f"WHERE event_state = 'paid' GROUP BY region_code"
            ),
            "load SF01 region audit rollup truth",
        )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"INSERT INTO {self.db}.{self.exceptions_table} VALUES "
                f"(1,'settlement_summary','all_paid',1,{self.insert_amount},{self.insert_crc},'open'),"
                f"(2,'region_audit_rollup','{self.insert_region_code}',"
                f"1,{self.insert_amount},{self.insert_crc},'open')"
            ),
            "load SF01 reconciliation exception backlog",
        )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"SPLIT TABLE {self.db}.{self.table} BETWEEN (0) AND "
                f"({self.expected_region_count * 1000 + 1}) "
                f"REGIONS {self.expected_region_count}"
            ),
            "split SF01 business table into deterministic Regions",
        )

    def _region_code(self, event_id: int) -> str:
        return self.region_codes[(event_id - 1) % len(self.region_codes)]

    def _wait_for_regions(self, env) -> None:
        env.deployment._wait(
            "tidb/tidb-0",
            lambda: self._region_count(env) == self.expected_region_count,
            180,
        )
        env.deployment._wait(
            "pd",
            lambda: (
                len(stores := self._store_status(env.deployment)) == 3
                and all(
                    status["state_name"] == "Up" and int(status["region_count"]) > 0
                    for status in stores.values()
                )
            ),
            180,
        )

    def _region_count(self, env) -> int:
        payload = json_object(
            env.execute_bootstrap_sql(
                "SELECT COUNT(DISTINCT REGION_ID) "
                "FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
                f"WHERE DB_NAME = '{self.db}' AND TABLE_NAME = '{self.table}'"
            ),
            "read SF01 business Region count",
        )
        return int(payload["result"][0][0])

    def _capture_cluster_state(self, deployment) -> dict:
        stores = self._store_status(deployment)
        return {
            "leader_target": self._leader_target(deployment),
            "stores": stores,
            "schedulers": self._scheduler_names(deployment),
        }

    def _store_status(self, deployment) -> dict[int, dict[str, object]]:
        payload = self._pd_json(deployment, "/pd/api/v1/stores")
        stores = {}
        for item in payload["stores"]:
            store = item["store"]
            status = item["status"]
            store_id = int(store["id"])
            stores[store_id] = {
                "address": str(store["address"]),
                "state_name": str(store["state_name"]),
                "leader_count": int(status["leader_count"]),
                "region_count": int(status["region_count"]),
            }
        return stores

    def _leader_target(self, deployment) -> str:
        payload = self._pd_json(deployment, "/pd/api/v1/leader")
        name = str(payload["name"])
        if not re.fullmatch(r"pd-[0-2]", name):
            raise RuntimeError(f"SF01 PD leader API returned an unknown member: {payload!r}")
        return f"pd/{name}"

    @staticmethod
    def _select_eviction_store(stores: Mapping[int, Mapping[str, object]]) -> int:
        candidates = [
            (store_id, int(status["leader_count"]))
            for store_id, status in stores.items()
            if str(status["state_name"]) == "Up" and int(status["leader_count"]) > 0
        ]
        if not candidates:
            raise RuntimeError(f"SF01 found no healthy TiKV store with leaders: stores={stores!r}")
        return max(candidates, key=lambda item: item[1])[0]

    def _start_disk_fault(
        self,
        deployment,
        target: str,
        *,
        term_epoch: int = 0,
        role: str = "leader",
    ) -> None:
        member = target.split("/", 1)[1]
        script = f"""rm -f {self._DISK_PID_FILE} {self._BUFFER_FILE}
nohup sh -c '
    cycle=0
    trap "exit 0" TERM INT
    while :; do
        cycle=$((cycle + 1))
        started=$(date +%s%N)
        dd if=/dev/zero of={self._BUFFER_FILE} bs=8M count=8 conv=fdatasync status=none
        finished=$(date +%s%N)
        duration_ns=$((finished - started))
        printf "SF01 phase=storage_flush member={member} host={member}-tidb-mixed role={role} cycle=%s raw_duration_ns=%s term_epoch={term_epoch}\\n" "$cycle" "$duration_ns" > /proc/1/fd/1
        rm -f {self._BUFFER_FILE}
    done
' >/dev/null 2>&1 & echo $! > {self._DISK_PID_FILE}
"""
        deployment.exec(
            target,
            ["sh", "-lc", script],
        )

    def _stop_disk_fault(self, deployment, target: str) -> None:
        deployment.exec(
            target,
            [
                "sh",
                "-lc",
                (
                    f"pid=$(cat {self._DISK_PID_FILE} 2>/dev/null); "
                    f"if [ -n \"$pid\" ]; then kill \"$pid\" 2>/dev/null; fi; "
                    f"rm -f {self._DISK_PID_FILE} {self._BUFFER_FILE}"
                ),
            ],
        )

    def _start_maintenance_flush(self, deployment, target: str) -> None:
        member = target.split("/", 1)[1]
        script = f"""rm -f {self._MAINTENANCE_PID_FILE} {self._BUFFER_FILE}
nohup sh -c '
    cycle=0
    deadline=$(( $(date +%s) + {self._MAINTENANCE_SECONDS} ))
    trap "exit 0" TERM INT
    while [ $(date +%s) -lt $deadline ]; do
        cycle=$((cycle + 1))
        started=$(date +%s%N)
        dd if=/dev/zero of={self._BUFFER_FILE} bs=8M count=8 conv=fdatasync status=none
        finished=$(date +%s%N)
        duration_ns=$((finished - started))
        printf "SF01 phase=storage_flush member={member} host={member}-tidb-mixed role=follower cycle=%s raw_duration_ns=%s term_epoch=0\\n" "$cycle" "$duration_ns" > /proc/1/fd/1
        rm -f {self._BUFFER_FILE}
        sleep 4
    done
' >/dev/null 2>&1 & echo $! > {self._MAINTENANCE_PID_FILE}
"""
        deployment.exec(
            target,
            ["sh", "-lc", script],
        )

    def _stop_maintenance_flush(self, deployment, target: str) -> None:
        deployment.exec(
            target,
            [
                "sh",
                "-lc",
                (
                    f"pid=$(cat {self._MAINTENANCE_PID_FILE} 2>/dev/null); "
                    f"if [ -n \"$pid\" ]; then kill \"$pid\" 2>/dev/null; fi; "
                    f"rm -f {self._MAINTENANCE_PID_FILE} {self._BUFFER_FILE}"
                ),
            ],
        )

    def _emit_phase_marker(
        self,
        deployment,
        target: str,
        *,
        phase: str,
        role: str,
        term_epoch: int,
        raw_duration_ns: int,
        leader: str | None = None,
        store_id: int | None = None,
    ) -> None:
        member = target.split("/", 1)[1]
        leader_field = "" if leader is None else f" leader={leader}"
        store_field = "" if store_id is None else f" store_id={store_id}"
        marker = (
            f"SF01 phase={phase} member={member} host={member}-tidb-mixed "
            f"role={role} term_epoch={term_epoch} raw_duration_ns={raw_duration_ns}"
            f"{leader_field}{store_field}"
        )
        deployment.exec(
            target,
            ["sh", "-lc", f"printf '%s\\n' {json.dumps(marker)} > /proc/1/fd/1"],
        )

    def _add_eviction_scheduler(self, deployment, store_id: int) -> None:
        payload = json.dumps({"name": self._SCHEDULER_NAME, "store_id": store_id})
        deployment.exec(
            self._leader_target(deployment),
            [
                "curl",
                "-fsS",
                "-X",
                "POST",
                "-H",
                "Content-Type: application/json",
                "--data",
                payload,
                "http://127.0.0.1:2379/pd/api/v1/schedulers",
            ],
        )

    def _remove_eviction_scheduler(self, deployment, store_id: int) -> None:
        deployment.exec(
            self._leader_target(deployment),
            [
                "curl",
                "-fsS",
                "-X",
                "DELETE",
                "http://127.0.0.1:2379/pd/api/v1/scheduler-config/"
                f"{self._SCHEDULER_NAME}/delete/{store_id}",
            ],
        )

    def _scheduler_names(self, deployment) -> tuple[str, ...]:
        payload = self._pd_json(deployment, "/pd/api/v1/schedulers")
        raw = payload["schedulers"] if isinstance(payload, dict) else payload
        names = []
        for item in raw:
            names.append(str(item if isinstance(item, str) else item["name"]))
        return tuple(sorted(names))

    def _pd_json(self, deployment, path: str) -> object:
        if self._faulty_pd_target is None:
            return deployment._pd_json(path)
        return json.loads(
            deployment.exec(
                self._pd_observer_target(),
                ["wget", "-qO-", f"http://127.0.0.1:2379{path}"],
            )
        )

    def _pd_observer_target(self) -> str:
        if self._faulty_pd_target == "pd/pd-0":
            return "pd/pd-1"
        return "pd/pd-0"

    def _eviction_is_visible(self, deployment) -> bool:
        names = self._scheduler_names(deployment)
        if self._scheduler_id not in names:
            return False
        stores = self._store_status(deployment)
        current = stores[self._evicted_store_id]["leader_count"]
        baseline = self._baseline["stores"][self._evicted_store_id]["leader_count"]
        peer_leaders = [
            status["leader_count"]
            for store_id, status in stores.items()
            if store_id != self._evicted_store_id
        ]
        return (
            current <= max(1, baseline // 4)
            and current * 2 < min(peer_leaders)
        )


class TidbSystemFailureSf01Scenario(TiDBScenario):
    scenario_id = "tidb_system_failure_sf01"
    description = "Investigates a TiDB write-latency and Region-placement incident and restores service and business integrity."
    cases = (_TIDB_SYSTEM_FAILURE_SF01_CASE, _FOCUSED_SF01_CASE)

    def build_fault_plan(self, case: TidbSystemFailureSf01Case) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureSf01PdMixedDiskEvictionInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "reconciliation_table": case.reconciliation_table,
                    "rollup_table": case.rollup_table,
                    "exceptions_table": case.exceptions_table,
                    "row_count": case.row_count,
                    "expected_amount_sum": case.expected_amount_sum,
                    "expected_checksum": case.expected_checksum,
                    "expected_region_count": case.expected_region_count,
                    "region_codes": case.region_codes,
                    "insert_amount": case.insert_amount,
                    "insert_crc": case.insert_crc,
                    "insert_region_code": case.insert_region_code,
                    "expected_exception_count": case.expected_exception_count,
                },
            ),
        )
