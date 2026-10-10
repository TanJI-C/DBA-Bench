from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import ClassVar

import time
import zlib

from src.database.sql import parse_json_object, require_result_rows
from src.scenarios.evaluation.protocol import structured_reference_report
from src.scenarios.evaluation.tidb.system_failure.pending_offline import (
    ONLINE_UNSAFE_DP_FACTORS,
    TidbSystemFailurePendingOfflineEvaluatorCase,
    TidbSystemFailurePendingOfflineStoreMigrationPendingEvaluatorCase,
)
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    require_sql_success,
    run_cleanup_steps,
    validate_sql_identifier,
)
from src.scenarios.workloads import WorkloadProfile

from ...base import BackgroundWorkloadSpec, DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from ..runtime import TIDB_V8_1_0, tidb_runtime


SF07_DB = "bench_sf07"
SF07_TABLE = "sf07_orders"
SF07_INDEX = "idx_tenant_status"
SF07_HEALTHY_TABLE = "sf07_reconciliation"
SF07_GLOBAL_SCOPE_TABLE = "sf07_payments"
SF07_NOISE_TABLES = (
    SF07_GLOBAL_SCOPE_TABLE,
    "sf07_order_audit",
    "sf07_refunds",
    "sf07_inventory_events",
    "sf07_shipments",
    "sf07_support_tickets",
    SF07_HEALTHY_TABLE,
    "sf07_marketing_attribution",
)
SF07_ROWS = 16_384
SF07_NEW_WRITE_ID = SF07_ROWS + 1
SF07_NEW_WRITE_TENANT_ID = SF07_NEW_WRITE_ID % 257
SF07_NEW_WRITE_AMOUNT = 9_001
SF07_NEW_WRITE_STATUS = "paid"
SF07_NEW_WRITE_PAYLOAD = "sf07-recovery-canary"
SF07_AFFECTED_POLICY = "sf07_layout_a"
SF07_HEALTHY_POLICY = "sf07_layout_b"
SF07_GLOBAL_SCOPE_POLICY = "sf07_layout_c"
SF07_MAINTENANCE_NODE = "tikv/tikv-6"
SF07_SCHEDULE_BASELINE = {
    "region-schedule-limit": 64,
    "replica-schedule-limit": 64,
    "max-pending-peer-count": 64,
}
SF07_STORE_ZONES = (
    "sf07-zone-01",
    "sf07-zone-02",
    "sf07-zone-03",
    "sf07-zone-04",
    "sf07-zone-05",
    "sf07-zone-06",
    "sf07-zone-07",
)


class _SF07WaitTimeout(RuntimeError):
    pass


def sf07_order_amount(order_id: int) -> int:
    return 1000 + (order_id * 37) % 9000


def sf07_order_crc(order_id: int, amount: int | None = None) -> int:
    tenant_id = order_id % 257
    actual_amount = sf07_order_amount(order_id) if amount is None else amount
    return zlib.crc32(f"sf07:{order_id}:{tenant_id}:{actual_amount}".encode()) & 0xFFFFFFFF


def sf07_order_checksum(row_count: int) -> int:
    checksum = 0
    for order_id in range(1, row_count + 1):
        checksum ^= sf07_order_crc(order_id)
    return checksum


SF07_AMOUNT_SUM = sum(sf07_order_amount(order_id) for order_id in range(1, SF07_ROWS + 1))
SF07_CHECKSUM = sf07_order_checksum(SF07_ROWS)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailurePendingOfflineCase(TiDBScenarioCase):
    snapshot_unsafe: ClassVar[bool] = True
    db: str
    table: str
    index: str
    healthy_table: str
    noise_tables: tuple[str, ...]
    failed_nodes: tuple[str, ...]
    healthy_nodes: tuple[str, ...]
    maintenance_nodes: tuple[str, ...]
    row_count: int
    expected_count: int
    expected_amount_sum: int
    expected_checksum: int
    new_write_id: int
    new_write_tenant_id: int
    new_write_amount: int
    new_write_status: str
    new_write_payload: str


class TidbSystemFailurePendingOfflineForOnlineUnsafeRecoveryScenarioCase(
    TidbSystemFailurePendingOfflineCase
):
    pass


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="sf07_checkout_order_detail",
            sql=(
                f"SELECT order_id, tenant_id, amount, status FROM {SF07_DB}.{SF07_TABLE} "
                "WHERE order_id BETWEEN 9800 AND 10020 ORDER BY order_id LIMIT 32"
            ),
            qps=0.32,
            tier="CRITICAL",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="sf07_checkout_tenant_total",
            sql=(
                f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {SF07_DB}.{SF07_TABLE} "
                "WHERE tenant_id IN (7, 19, 31, 43) GROUP BY tenant_id ORDER BY tenant_id"
            ),
            qps=0.18,
            tier="CRITICAL",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="sf07_settlement_checksum_probe",
            sql=(
                f"SELECT COUNT(*), SUM(amount), BIT_XOR(row_crc) FROM {SF07_DB}.{SF07_TABLE} "
                f"WHERE order_id BETWEEN 1 AND {SF07_ROWS}"
            ),
            qps=0.08,
            tier="CRITICAL",
            application_name="settlement-worker",
        ),
        WorkloadProfile(
            name="sf07_healthy_reconciliation_probe",
            sql=(
                f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {SF07_DB}.{SF07_HEALTHY_TABLE} "
                "GROUP BY tenant_id ORDER BY tenant_id LIMIT 32"
            ),
            qps=0.18,
            tier="BUSINESS_NEIGHBOR",
            application_name="finance-reconciliation",
        ),
        WorkloadProfile(
            name="sf07_payment_rollup",
            sql=(
                f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {SF07_DB}.sf07_payments "
                "GROUP BY tenant_id ORDER BY SUM(amount) DESC LIMIT 16"
            ),
            qps=0.20,
            tier="BUSINESS_NOISE",
            application_name="payment-ledger",
        ),
        WorkloadProfile(
            name="sf07_audit_window",
            sql=(
                f"SELECT event_status, COUNT(*), SUM(amount) FROM {SF07_DB}.sf07_order_audit "
                "WHERE event_id BETWEEN 600 AND 1800 GROUP BY event_status"
            ),
            qps=0.20,
            tier="BUSINESS_NOISE",
            application_name="risk-audit",
        ),
        WorkloadProfile(
            name="sf07_refund_reconcile",
            sql=(
                f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {SF07_DB}.sf07_refunds "
                "WHERE event_id >= 900 GROUP BY tenant_id ORDER BY tenant_id"
            ),
            qps=0.18,
            tier="BUSINESS_NOISE",
            application_name="refund-reconcile",
        ),
        WorkloadProfile(
            name="sf07_inventory_allocation",
            sql=(
                f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {SF07_DB}.sf07_inventory_events "
                "GROUP BY tenant_id ORDER BY SUM(amount) DESC LIMIT 12"
            ),
            qps=0.18,
            tier="BUSINESS_NOISE",
            application_name="inventory-service",
        ),
        WorkloadProfile(
            name="sf07_region_store_monitor",
            sql=(
                "SELECT STORE_ID, STORE_STATE_NAME, LEADER_COUNT, REGION_COUNT, AVAILABLE "
                "FROM INFORMATION_SCHEMA.TIKV_STORE_STATUS ORDER BY STORE_ID"
            ),
            qps=0.26,
            tier="MONITOR",
            application_name="pd-dashboard",
        ),
        WorkloadProfile(
            name="sf07_region_status_monitor",
            sql=(
                "SELECT DB_NAME, TABLE_NAME, TABLE_ID, INDEX_ID, REGION_ID, IS_INDEX, "
                "APPROXIMATE_SIZE, APPROXIMATE_KEYS "
                "FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
                "ORDER BY WRITTEN_BYTES DESC LIMIT 80"
            ),
            qps=0.18,
            tier="MONITOR",
            application_name="region-dashboard",
        ),
        WorkloadProfile(
            name="sf07_region_peer_monitor",
            sql=(
                "SELECT REGION_ID, STORE_ID, IS_LEARNER, IS_LEADER, STATUS, DOWN_SECONDS "
                "FROM INFORMATION_SCHEMA.TIKV_REGION_PEERS ORDER BY DOWN_SECONDS DESC LIMIT 80"
            ),
            qps=0.16,
            tier="MONITOR",
            application_name="replication-dashboard",
        ),
        WorkloadProfile(
            name="sf07_cluster_inventory_monitor",
            sql=(
                "SELECT TYPE, INSTANCE, VERSION, UPTIME FROM INFORMATION_SCHEMA.CLUSTER_INFO "
                "ORDER BY TYPE, INSTANCE"
            ),
            qps=0.14,
            tier="MONITOR",
            application_name="cluster-dashboard",
        ),
        WorkloadProfile(
            name="sf07_missing_cache_error_noise",
            sql=f"SELECT COUNT(*) FROM {SF07_DB}.sf07_missing_dashboard_cache",
            qps=0.14,
            tier="ERROR_NOISE",
            application_name="dashboard-cache",
        ),
        WorkloadProfile(
            name="sf07_missing_archive_error_noise",
            sql=f"SELECT COUNT(*) FROM {SF07_DB}.sf07_legacy_archive_snapshot",
            qps=0.12,
            tier="ERROR_NOISE",
            application_name="legacy-reporting",
        ),
    ),
    worker_count=8,
    seed=20260819,
    warmup_seconds=18,
)


_CASE = TidbSystemFailurePendingOfflineForOnlineUnsafeRecoveryScenarioCase(
    case_id="online_unsafe_recovery_failed_stores",
    case_no=0,
    evaluator=TidbSystemFailurePendingOfflineEvaluatorCase,
    title="Restore a TiDB v8.1 checkout data range after a storage availability incident.",
    alert=(
        "[CRITICAL] Checkout orders are unavailable for one storage-backed data range while an unrelated "
        "reconciliation workload remains serviceable. Inspect the live Store, Region, peer, release, "
        "control-plane, business-truth, log, and versioned TiDB knowledge evidence. Restore service with "
        "a supported, scoped product operation only after the current affected scope, release-specific "
        "preconditions, and business boundary are established. Verify the product result, public table/index "
        "integrity checks, and restore the captured PD scheduling baseline "
        "(region-schedule-limit=64, replica-schedule-limit=64, max-pending-peer-count=64), "
        "insert exactly one authorized canary "
        f"order (order_id={SF07_NEW_WRITE_ID}, tenant_id={SF07_NEW_WRITE_TENANT_ID}, "
        f"amount={SF07_NEW_WRITE_AMOUNT}, status='{SF07_NEW_WRITE_STATUS}', "
        f"payload='{SF07_NEW_WRITE_PAYLOAD}'). Its row_crc is generated by the table schema from "
        "order_id, tenant_id, and amount; omit that column from the INSERT. Submit an outcome.plan "
        "with one boundary field (last_confirmed_boundary or last_confirmed_commit_boundary), one "
        "unconfirmed-window field (unconfirmed_write_window or unconfirmed_interval), and an RPO field "
        "(observed_rpo or rpo_observation), describing "
        "the last confirmed commit boundary, the unconfirmed interval, and the observed RPO. Do not delete peers manually, restart failed "
        "Stores or PD quorum, alter existing business rows, include a pre-existing maintenance-only Store in the "
        "recovery request, or claim general losslessness from one checksum. The structured submission shape is "
        "report={diagnosis, outcome={changes, verification, plan={...}}, summary}; plan belongs inside outcome, "
        "never at the report top level."
    ),
    initial_state={
        "status": "affected_region_unavailable",
        "replica_layout": "two permanently failed peers plus one surviving peer",
        "global_recovery_scope": "a third permanently failed Store owns a separate sf07_payments Region with two healthy peers",
        "maintenance_boundary": "one pre-existing maintenance-only Store is outside this incident and must not be included in Online Unsafe Recovery",
        "control_plane": "PD Online Unsafe Recovery is idle",
        "schedule_baseline": "region-schedule-limit=64, replica-schedule-limit=64, max-pending-peer-count=64",
        "business_boundary": "last committed truth captured before the three Store failures",
    },
    expected_target={
        "case": "online_unsafe_recovery_failed_stores",
        "recovery": "Unsafe recovery Finished",
        "affected_replication": "three normal peers with a leader and no failed Store",
        "recovery_scope": "checkout record/index Regions plus the same-incident sf07_payments Regions converge outside all failed Stores",
        "maintenance_scope": "the pre-existing maintenance-only Store remains serving and outside the recovery request; it may receive a normal replacement peer after recovery",
        "schedule": "region-schedule-limit=64, replica-schedule-limit=64, max-pending-peer-count=64",
        "business_truth": (
            "the captured pre-fault row count and amount sum remain unchanged before the canary; "
            "row_crc is a generated column and is not a caller-supplied business value"
        ),
        "new_write": f"order_id={SF07_NEW_WRITE_ID} committed after terminal recovery",
        "rpo": "last confirmed boundary and unconfirmed interval explicitly reported",
    },
    background_workload=_BACKGROUND_WORKLOAD,
    reference_report=structured_reference_report(
        case_id="online_unsafe_recovery_failed_stores",
        factors=ONLINE_UNSAFE_DP_FACTORS,
        changes=(
            "confirmed the complete permanently failed Store set from live Store evidence; only two of those Stores belong to the unavailable checkout Region",
            "used the v8.1 Online Unsafe Recovery product entry point and waited for Finished",
            "restored the pre-fault PD scheduling gate values after the recovery task completed",
            "committed the authorized canary order after the terminal recovery state",
        ),
        verification=(
            "affected record and index Regions have a leader and three normal peers outside failed Stores",
            "ADMIN CHECK TABLE, pre-fault truth, healthy-neighbor truth, and the canary row all pass",
            "the report identifies the last confirmed boundary, unconfirmed interval, and observed RPO",
        ),
        summary="The checkout two-of-three peer loss and the same-incident global failed Store scope were recovered through the asynchronous v8.1 Online Unsafe Recovery boundary without claiming general losslessness.",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.801556,
        reference_run_ids=(
            "reference-136__"
            "tidb_system_failure_pending_offline__online_unsafe_recovery_failed_stores__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=7,
        tidb_count=2,
        sql_timeout_seconds=300,
        tikv_store_zones=SF07_STORE_ZONES,
        pd_location_labels=("zone",),
        bootstrap_cache_enabled=False,
    ),
    db=SF07_DB,
    table=SF07_TABLE,
    index=SF07_INDEX,
    healthy_table=SF07_HEALTHY_TABLE,
    noise_tables=SF07_NOISE_TABLES,
    failed_nodes=("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
    healthy_nodes=("tikv/tikv-3", "tikv/tikv-4", "tikv/tikv-5"),
    maintenance_nodes=(SF07_MAINTENANCE_NODE,),
    row_count=SF07_ROWS,
    expected_count=SF07_ROWS,
    expected_amount_sum=SF07_AMOUNT_SUM,
    expected_checksum=SF07_CHECKSUM,
    new_write_id=SF07_NEW_WRITE_ID,
    new_write_tenant_id=SF07_NEW_WRITE_TENANT_ID,
    new_write_amount=SF07_NEW_WRITE_AMOUNT,
    new_write_status=SF07_NEW_WRITE_STATUS,
    new_write_payload=SF07_NEW_WRITE_PAYLOAD,
)


class TidbSystemFailurePendingOfflineInjector(BaseFaultInjector):
    """Create a checkout majority loss plus a same-incident global failed Store scope."""

    _SCHEDULE_KEYS = (
        "region-schedule-limit",
        "replica-schedule-limit",
        "max-pending-peer-count",
    )
    _REGION_PREPARATION_TIMEOUT = 300
    _FAULT_TIMEOUT = 180

    def __init__(self):
        self.env = None
        self.db = None
        self.table = None
        self.index = None
        self.healthy_table = None
        self.noise_tables = ()
        self.failed_nodes = ()
        self.healthy_nodes = ()
        self.maintenance_nodes = ()
        self.row_count = None
        self.expected_count = None
        self.expected_amount_sum = None
        self.expected_checksum = None
        self.new_write_id = None
        self.new_write_tenant_id = None
        self.new_write_amount = None
        self.new_write_status = None
        self.new_write_payload = None
        self.failed_store_ids = ()
        self.healthy_store_ids = ()
        self.maintenance_store_ids = ()
        self.healthy_leader_store_id = None
        self.global_scope_failed_store_id = None
        self.global_scope_leader_store_id = None
        self.global_scope_healthy_store_ids = ()
        self.affected_region_ids = ()
        self.global_scope_region_ids = ()
        self.recovery_region_ids = ()
        self.affected_failed_store_ids = ()
        self.affected_table_id = None
        self.affected_index_ids = ()
        self.healthy_region_ids = ()
        self.affected_region_peer_baseline = ()
        self.global_scope_region_peer_baseline = ()
        self.healthy_region_peer_baseline = ()
        self.original_schedule = None
        self.pre_fault_truth = None
        self.pre_fault_tso = None
        self.healthy_truth = None
        self.global_scope_truth = None
        self._fault_started = False

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._establish_schedule_baseline()
        self._capture_pd_state()
        self._create_business_state()
        self._capture_region_scope()
        self._prepare_region_placement()
        self._block_scheduling()
        self._detach_initial_placement_policies()
        self._capture_business_boundary()
        self._stop_failed_stores()
        self._fault_started = True
        self._verify_fault_state()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._resolve_store_ids()
        if self.original_schedule is None:
            raise RuntimeError(
                "SF07 activate requires the install-time PD schedule baseline; "
                f"run_id={context.run_id!r}, case_id={context.case_id!r}"
            )
        self._capture_region_scope()
        self._verify_fault_state()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._resolve_store_ids()
        if (
            self.original_schedule is None
            or self.pre_fault_truth is None
            or self.pre_fault_tso is None
            or self.healthy_truth is None
            or self.global_scope_truth is None
        ):
            raise RuntimeError(
                "SF07 observability preparation lacks the install-time boundary: "
                f"run_id={context.run_id!r}, original_schedule={self.original_schedule!r}, "
                f"pre_fault_truth={self.pre_fault_truth!r}, pre_fault_tso={self.pre_fault_tso!r}"
            )
        self._capture_region_scope()
        affected_regions = tuple(
            (region_id, tuple(sorted(self._peer_store_ids(region_id))))
            for region_id in self.affected_region_ids
        )
        global_scope_regions = tuple(
            (region_id, tuple(sorted(self._peer_store_ids(region_id))))
            for region_id in self.global_scope_region_ids
        )
        healthy_regions = tuple(
            (region_id, tuple(sorted(self._peer_store_ids(region_id))))
            for region_id in self.healthy_region_ids
        )
        maintenance_stores = tuple(
            (store_id, str(self._store(store_id).get("state_name", "")))
            for store_id in self.maintenance_store_ids
        )
        return {
            "failed_store_ids": tuple(self.failed_store_ids),
            "affected_failed_store_ids": tuple(self.affected_failed_store_ids),
            "healthy_store_ids": tuple(self.healthy_store_ids),
            "maintenance_store_ids": tuple(self.maintenance_store_ids),
            "maintenance_store_states": maintenance_stores,
            "affected_region_ids": tuple(self.affected_region_ids),
            "global_scope_region_ids": tuple(self.global_scope_region_ids),
            "recovery_region_ids": tuple(self.recovery_region_ids),
            "affected_table_id": int(self.affected_table_id),
            "affected_index_ids": tuple(self.affected_index_ids),
            "healthy_region_ids": tuple(self.healthy_region_ids),
            "affected_region_peer_baseline": affected_regions,
            "global_scope_region_peer_baseline": global_scope_regions,
            "healthy_region_peer_baseline": healthy_regions,
            "pre_fault_truth": tuple(self.pre_fault_truth),
            "pre_fault_tso": int(self.pre_fault_tso),
            "healthy_truth": tuple(self.healthy_truth),
            "global_scope_truth": tuple(self.global_scope_truth),
            "post_boundary_attempts": (),
            "original_schedule": dict(self.original_schedule),
            "business_database": self.db,
            "business_table": self.table,
            "healthy_table": self.healthy_table,
            "new_write": {
                "order_id": self.new_write_id,
                "tenant_id": self.new_write_tenant_id,
                "amount": self.new_write_amount,
                "status": self.new_write_status,
                "payload": self.new_write_payload,
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        for node in self.failed_nodes:
            state = context.env.deployment.node_states()[node]
            if state["running"]:
                raise RuntimeError(
                    "SF07 quiesce found a failed TiKV process running: "
                    f"run_id={context.run_id!r}, node={node!r}, state={state!r}"
                )

    def recover(self, context: FaultLifecycleContext) -> None:
        if self.original_schedule is None:
            raise RuntimeError(
                "SF07 recover has no captured PD schedule baseline: "
                f"run_id={context.run_id!r}"
            )
        run_cleanup_steps(
            f"SF07 cleanup run_id={context.run_id!r}",
            (
                ("wait Online Unsafe Recovery terminal", self._wait_for_recovery_terminal),
                (
                    "restore Case-owned TiKV stores",
                    lambda: self.env.deployment.restore_tikv_stores(tuple(self.failed_nodes)),
                ),
                ("restore PD scheduling baseline", self._restore_schedule),
                ("drop SF07 database", self._drop_database),
                ("drop SF07 placement policies", self._drop_placement_policies),
            ),
        )

    def _wait_for_recovery_terminal(self) -> None:
        if not self.env.deployment.online_unsafe_recovery_started:
            return
        if self._recovery_terminal(self._unsafe_recovery_status()):
            return
        self._wait_for(
            lambda: self._recovery_terminal(self._unsafe_recovery_status()),
            "SF07 Online Unsafe Recovery to reach a terminal state before teardown",
            30,
        )

    def _restore_schedule(self) -> None:
        for key, value in self.original_schedule.items():
            self._set_schedule_config(key, value)

    def _drop_database(self) -> None:
        self.env.reconnect()
        last_response = None

        def drop_when_schema_is_ready() -> bool:
            nonlocal last_response
            sql = f"DROP DATABASE IF EXISTS {self.db}"
            payload = parse_json_object(self.env.execute_sql(sql), f"drop SF07 database {self.db}: sql={sql!r}")
            if payload.get("status") == "success":
                return True
            error = str(payload.get("error", ""))
            if "1008" in error or "database doesn't exist" in error.casefold():
                return True
            if payload.get("status") != "error" or not (
                "8027" in error
                or "schema is out of date" in error.casefold()
                or "schema failed to update" in error.casefold()
                or "9005" in error
                or "Region is unavailable" in error
            ):
                raise RuntimeError(
                    f"drop SF07 database {self.db} returned an unexpected failure: payload={payload!r}"
                )
            last_response = payload
            self.env.reconnect()
            return False

        try:
            self._wait_for(
                drop_when_schema_is_ready,
                f"SF07 database {self.db} schema lease to recover",
                600,
            )
        except _SF07WaitTimeout as exc:
            raise RuntimeError(
                f"drop SF07 database {self.db} did not become cleanable: last_response={last_response!r}"
            ) from exc

    def _drop_placement_policies(self) -> None:
        transient = (
            "8027", "schema is out of date", "9005", "Region is unavailable",
            "8241", "is in use", "1227", "Access denied",
        )
        for policy in (SF07_AFFECTED_POLICY, SF07_GLOBAL_SCOPE_POLICY, SF07_HEALTHY_POLICY):
            sql = f"DROP PLACEMENT POLICY IF EXISTS {policy}"
            for attempt in range(60):
                payload = parse_json_object(
                    self.env.execute_sql(sql),
                    f"drop SF07 placement policy {policy}: sql={sql!r}",
                )
                error = str(payload.get("error", ""))
                if payload.get("status") != "error":
                    break
                if "8239" in error or "Unknown placement policy" in error:
                    break
                if not any(token in error for token in transient):
                    raise RuntimeError(
                        f"drop SF07 placement policy {policy} returned an unexpected failure: "
                        f"payload={payload!r}"
                    )
                if attempt < 59:
                    self.env.execute_sql("SELECT SLEEP(10)")
            else:
                # 策略对象随 compose down 一并销毁，不会泄漏到任何复用存储；
                # TiDB 在 GC 压力下可能对该 DROP 持续返回对象级瞬态错误，
                # 记录残留后继续 teardown，不再让已完成的评测被污染。
                print(
                    f"[FaultInjector:SF07] WARNING: placement policy {policy} not dropped at teardown; "
                    f"residual={payload!r}"
                )

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.index = validate_sql_identifier(str(config["index"]), "index")
        self.healthy_table = validate_sql_identifier(str(config["healthy_table"]), "healthy table")
        self.noise_tables = tuple(
            validate_sql_identifier(str(table), "noise table")
            for table in config["noise_tables"]
        )
        self.failed_nodes = tuple(str(node) for node in config["failed_nodes"])
        self.healthy_nodes = tuple(str(node) for node in config["healthy_nodes"])
        self.maintenance_nodes = tuple(str(node) for node in config["maintenance_nodes"])
        self.row_count = int(config["row_count"])
        self.expected_count = int(config["expected_count"])
        self.expected_amount_sum = int(config["expected_amount_sum"])
        self.expected_checksum = int(config["expected_checksum"])
        self.new_write_id = int(config["new_write_id"])
        self.new_write_tenant_id = int(config["new_write_tenant_id"])
        self.new_write_amount = int(config["new_write_amount"])
        self.new_write_status = str(config["new_write_status"])
        self.new_write_payload = str(config["new_write_payload"])
        configured_nodes = set(env.deployment.NODES)
        if len(self.failed_nodes) != 3 or len(set(self.failed_nodes)) != 3:
            raise ValueError(f"SF07 requires three unique failed TiKV nodes: failed_nodes={self.failed_nodes!r}")
        if len(self.healthy_nodes) != 3 or len(set(self.healthy_nodes)) != 3:
            raise ValueError(f"SF07 requires three unique healthy TiKV nodes: healthy_nodes={self.healthy_nodes!r}")
        if len(self.maintenance_nodes) != 1 or len(set(self.maintenance_nodes)) != 1:
            raise ValueError(
                f"SF07 requires one unique maintenance-only TiKV node: maintenance_nodes={self.maintenance_nodes!r}"
            )
        all_nodes = (*self.failed_nodes, *self.healthy_nodes, *self.maintenance_nodes)
        if len(set(all_nodes)) != 7 or set(all_nodes) != {node for node in configured_nodes if node.startswith("tikv/")}:
            raise ValueError(
                "SF07 failed/healthy/maintenance nodes must partition the seven configured TiKV nodes: "
                f"failed_nodes={self.failed_nodes!r}, healthy_nodes={self.healthy_nodes!r}, "
                f"maintenance_nodes={self.maintenance_nodes!r}, "
                f"configured_tikv_nodes={sorted(node for node in configured_nodes if node.startswith('tikv/'))!r}"
            )
        if self.healthy_table not in self.noise_tables:
            raise ValueError(
                f"SF07 healthy table must be created as a neighbor table: healthy_table={self.healthy_table!r}, "
                f"noise_tables={self.noise_tables!r}"
            )
        if SF07_GLOBAL_SCOPE_TABLE not in self.noise_tables:
            raise ValueError(
                "SF07 global failed Store scope table must be created with the noise tables: "
                f"scope_table={SF07_GLOBAL_SCOPE_TABLE!r}, noise_tables={self.noise_tables!r}"
            )
        if self.row_count != SF07_ROWS or self.new_write_id != SF07_NEW_WRITE_ID:
            raise ValueError(
                "SF07 business boundary constants changed: "
                f"row_count={self.row_count!r}, new_write_id={self.new_write_id!r}"
            )

    def _capture_pd_state(self) -> None:
        schedule = self.env.deployment.pd_request("GET", "/pd/api/v1/config")["schedule"]
        missing = [key for key in self._SCHEDULE_KEYS if key not in schedule]
        if missing:
            raise RuntimeError(
                f"SF07 PD schedule baseline is missing required keys: missing={missing!r}, schedule={schedule!r}"
            )
        self.original_schedule = {key: schedule[key] for key in self._SCHEDULE_KEYS}
        self._resolve_store_ids()

    def _establish_schedule_baseline(self) -> None:
        for key, value in SF07_SCHEDULE_BASELINE.items():
            self._set_schedule_config(key, value)

    def _resolve_store_ids(self) -> None:
        stores = self.env.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
        by_node = {}
        for item in stores:
            service = str(item["store"]["address"]).split(":", 1)[0]
            node = f"tikv/{service}"
            if node in by_node:
                raise RuntimeError(f"SF07 PD returned duplicate TiKV node mapping: node={node!r}, stores={stores!r}")
            by_node[node] = item["store"]
        missing = [
            node for node in (*self.failed_nodes, *self.healthy_nodes, *self.maintenance_nodes)
            if node not in by_node
        ]
        if missing:
            raise RuntimeError(
                "SF07 failed/healthy/maintenance TiKV node mapping is incomplete: "
                f"missing={missing!r}, observed={sorted(by_node)!r}"
            )
        self.failed_store_ids = tuple(sorted(int(by_node[node]["id"]) for node in self.failed_nodes))
        self.healthy_store_ids = tuple(sorted(int(by_node[node]["id"]) for node in self.healthy_nodes))
        self.maintenance_store_ids = tuple(sorted(int(by_node[node]["id"]) for node in self.maintenance_nodes))
        self.healthy_leader_store_id = int(by_node[self.healthy_nodes[0]]["id"])
        self.affected_failed_store_ids = tuple(
            sorted(int(by_node[node]["id"]) for node in self.failed_nodes[:2])
        )
        self.global_scope_failed_store_id = int(by_node[self.failed_nodes[2]]["id"])
        self.global_scope_leader_store_id = int(by_node[self.healthy_nodes[1]]["id"])
        self.global_scope_healthy_store_ids = (
            int(by_node[self.healthy_nodes[1]]["id"]),
            int(by_node[self.healthy_nodes[2]]["id"]),
        )
        if set(self.failed_store_ids) & set(self.healthy_store_ids):
            raise RuntimeError(
                "SF07 failed and healthy Store IDs overlap: "
                f"failed_store_ids={self.failed_store_ids!r}, healthy_store_ids={self.healthy_store_ids!r}"
            )
        if set(self.maintenance_store_ids) & (set(self.failed_store_ids) | set(self.healthy_store_ids)):
            raise RuntimeError(
                "SF07 maintenance and incident Store IDs overlap: "
                f"maintenance_store_ids={self.maintenance_store_ids!r}, failed_store_ids={self.failed_store_ids!r}, "
                f"healthy_store_ids={self.healthy_store_ids!r}"
            )

    def _create_business_state(self) -> None:
        require_sql_success(
            self.env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"),
            f"clear SF07 database {self.db}",
        )
        for policy in (SF07_AFFECTED_POLICY, SF07_GLOBAL_SCOPE_POLICY, SF07_HEALTHY_POLICY):
            require_sql_success(
                self.env.execute_sql(f"DROP PLACEMENT POLICY IF EXISTS {policy}"),
                f"clear SF07 placement policy {policy}",
            )
        self._create_placement_policies()
        require_sql_success(
            self.env.execute_sql(f"CREATE DATABASE {self.db}"),
            f"create SF07 database {self.db}",
        )
        self._create_orders()
        for table in self.noise_tables:
            self._create_noise_table(
                table,
                regions=8 if table == self.healthy_table else 2,
                row_count=8192 if table == self.healthy_table else 2400,
            )

    def _create_placement_policies(self) -> None:
        policies = (
            (
                SF07_AFFECTED_POLICY,
                "LEADER_CONSTRAINTS='[+zone=sf07-zone-04]' "
                "FOLLOWER_CONSTRAINTS='{\"+zone=sf07-zone-01\": 1, \"+zone=sf07-zone-02\": 1}'",
            ),
            (
                SF07_HEALTHY_POLICY,
                "LEADER_CONSTRAINTS='[+zone=sf07-zone-04]' "
                "FOLLOWER_CONSTRAINTS='{\"+zone=sf07-zone-05\": 1, \"+zone=sf07-zone-06\": 1}'",
            ),
            (
                SF07_GLOBAL_SCOPE_POLICY,
                "LEADER_CONSTRAINTS='[+zone=sf07-zone-05]' "
                "FOLLOWER_CONSTRAINTS='{\"+zone=sf07-zone-03\": 1, \"+zone=sf07-zone-06\": 1}'",
            ),
        )
        for policy, constraints in policies:
            require_sql_success(
                self.env.execute_sql(f"CREATE PLACEMENT POLICY {policy} FOLLOWERS=2 {constraints}"),
                f"create SF07 placement policy {policy}",
            )

    def _create_orders(self) -> None:
        table = f"{self.db}.{self.table}"
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {table} ("
                "order_id INT PRIMARY KEY, tenant_id INT NOT NULL, amount INT NOT NULL, "
                "status VARCHAR(20) NOT NULL, "
                "row_crc BIGINT UNSIGNED AS "
                "(CRC32(CONCAT('sf07:', order_id, ':', tenant_id, ':', amount))) STORED, "
                "payload VARCHAR(96) NOT NULL, "
                f"KEY {self.index} (tenant_id, status)) "
                f"PLACEMENT POLICY={SF07_AFFECTED_POLICY}"
            ),
            f"create SF07 business table {table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"SPLIT TABLE {table} BETWEEN (0) AND ({self.row_count + 1}) REGIONS 16"
            ),
            f"split SF07 business table {table}",
        )
        for start in range(1, self.row_count + 1, 512):
            end = min(start + 512, self.row_count + 1)
            values = []
            for order_id in range(start, end):
                tenant_id = order_id % 257
                amount = sf07_order_amount(order_id)
                status = ("paid", "packed", "shipped", "review")[order_id % 4]
                values.append(
                    f"({order_id}, {tenant_id}, {amount}, '{status}', "
                    f"'sf07-order-{order_id % 19:02d}')"
                )
            require_sql_success(
                self.env.execute_sql(
                    f"INSERT INTO {table} "
                    "(order_id, tenant_id, amount, status, payload) VALUES "
                    + ",".join(values)
                ),
                f"load SF07 business rows {start}-{end - 1}",
            )
        require_sql_success(self.env.execute_sql(f"ANALYZE TABLE {table}"), f"analyze SF07 business table {table}")

    def _create_noise_table(self, table: str, *, regions: int, row_count: int) -> None:
        full_table = f"{self.db}.{table}"
        placement_policy = {
            self.healthy_table: SF07_HEALTHY_POLICY,
            SF07_GLOBAL_SCOPE_TABLE: SF07_GLOBAL_SCOPE_POLICY,
        }.get(table, SF07_HEALTHY_POLICY)
        placement = f" PLACEMENT POLICY={placement_policy}"
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {full_table} ("
                "event_id INT PRIMARY KEY, tenant_id INT NOT NULL, amount INT NOT NULL, "
                "event_status VARCHAR(20) NOT NULL, payload VARCHAR(96) NOT NULL, "
                "KEY idx_tenant (tenant_id), KEY idx_status (event_status)"
                f"){placement}"
            ),
            f"create SF07 neighbor table {full_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"SPLIT TABLE {full_table} BETWEEN (0) AND ({row_count + 1}) REGIONS {regions}"
            ),
            f"split SF07 neighbor table {full_table}",
        )
        for start in range(1, row_count + 1, 512):
            end = min(start + 512, row_count + 1)
            values = []
            for event_id in range(start, end):
                tenant_id = (event_id * 11) % 311
                amount = 50 + (event_id * 23) % 4000
                status = ("ready", "queued", "closed", "hold")[event_id % 4]
                values.append(
                    f"({event_id}, {tenant_id}, {amount}, '{status}', "
                    f"'sf07-{table}-{event_id % 31:02d}')"
                )
            require_sql_success(
                self.env.execute_sql(
                    f"INSERT INTO {full_table} "
                    "(event_id, tenant_id, amount, event_status, payload) VALUES "
                    + ",".join(values)
                ),
                f"load SF07 neighbor rows {table} {start}-{end - 1}",
            )
        require_sql_success(self.env.execute_sql(f"ANALYZE TABLE {full_table}"), f"analyze SF07 neighbor table {full_table}")

    def _capture_region_scope(self) -> None:
        affected_records = self._table_region_records(self.table)
        global_scope_records = self._table_region_records(SF07_GLOBAL_SCOPE_TABLE)
        healthy_records = self._table_region_records(self.healthy_table)
        affected_regions = tuple(sorted({int(row[0]) for row in affected_records}))
        global_scope_regions = tuple(sorted({int(row[0]) for row in global_scope_records}))
        healthy_regions = tuple(sorted({int(row[0]) for row in healthy_records}))
        table_ids = {int(row[1]) for row in affected_records}
        index_ids = {int(row[2]) for row in affected_records if row[2] is not None}
        if len(table_ids) != 1 or not index_ids or not affected_regions:
            raise RuntimeError(
                "SF07 affected table/index Region scope is incomplete: "
                f"table={self.table!r}, records={affected_records!r}, table_ids={sorted(table_ids)!r}, "
                f"index_ids={sorted(index_ids)!r}"
            )
        if not healthy_regions:
            raise RuntimeError(f"SF07 healthy neighbor has no Region scope: table={self.healthy_table!r}")
        if not global_scope_regions:
            raise RuntimeError(
                f"SF07 global failed Store scope has no Region scope: table={SF07_GLOBAL_SCOPE_TABLE!r}"
            )
        self.affected_region_ids = affected_regions
        self.global_scope_region_ids = global_scope_regions
        self.recovery_region_ids = tuple(sorted(set(affected_regions) | set(global_scope_regions)))
        self.affected_table_id = next(iter(table_ids))
        self.affected_index_ids = tuple(sorted(index_ids))
        self.healthy_region_ids = healthy_regions

    def _table_region_records(self, table: str) -> tuple[tuple[object, ...], ...]:
        sql = (
            "SELECT REGION_ID, TABLE_ID, INDEX_ID, IS_INDEX "
            "FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
            f"WHERE DB_NAME = '{self.db}' AND TABLE_NAME = '{table}' "
            "ORDER BY REGION_ID, IS_INDEX, INDEX_ID"
        )
        rows = require_result_rows(self.env.execute_sql(sql), f"list SF07 Region scope for {table}")
        if not rows:
            raise RuntimeError(f"SF07 Region scope query returned no rows: table={table!r}, sql={sql!r}")
        return tuple(tuple(row) for row in rows)

    def _prepare_region_placement(self) -> None:
        if len(self.affected_region_ids) < 16:
            raise RuntimeError(
                f"SF07 affected Region split is too small: region_count={len(self.affected_region_ids)}, "
                f"region_ids={self.affected_region_ids!r}"
            )
        if self.healthy_leader_store_id is None:
            raise RuntimeError("SF07 placement requires the first healthy Store to resolve before scheduling")
        if len(self.failed_store_ids) != 3 or len(self.healthy_store_ids) != 3:
            raise RuntimeError(
                "SF07 placement requires three failed and three healthy Stores: "
                f"failed_store_ids={self.failed_store_ids!r}, healthy_store_ids={self.healthy_store_ids!r}"
            )
        self._wait_for(
            self._region_placement_converged,
            "SF07 placement policies to converge for checkout, global failed Store, and healthy Regions",
            self._REGION_PREPARATION_TIMEOUT,
        )
        self.affected_region_peer_baseline = self._region_peer_baseline(self.affected_region_ids)
        self.global_scope_region_peer_baseline = self._region_peer_baseline(self.global_scope_region_ids)
        self.healthy_region_peer_baseline = self._region_peer_baseline(self.healthy_region_ids)

    def _detach_initial_placement_policies(self) -> None:
        require_sql_success(
            self.env.execute_sql(f"ALTER TABLE {self.db}.{self.table} PLACEMENT POLICY=DEFAULT"),
            f"detach SF07 initial-placement policy from {self.db}.{self.table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"ALTER TABLE {self.db}.{SF07_GLOBAL_SCOPE_TABLE} PLACEMENT POLICY=DEFAULT"
            ),
            f"detach SF07 initial-placement policy from {self.db}.{SF07_GLOBAL_SCOPE_TABLE}",
        )

    def _region_placement_converged(self) -> bool:
        affected_peers = set(self.affected_failed_store_ids) | {self.healthy_leader_store_id}
        global_scope_peers = {
            self.global_scope_failed_store_id,
            *self.global_scope_healthy_store_ids,
        }
        healthy_peers = set(self.healthy_store_ids)
        return (
            all(
                self._peer_store_ids(region_id) == affected_peers
                and self._region_leader(region_id) == self.healthy_leader_store_id
                for region_id in self.affected_region_ids
            )
            and all(
                self._peer_store_ids(region_id) == global_scope_peers
                and self._region_leader(region_id) == self.global_scope_leader_store_id
                for region_id in self.global_scope_region_ids
            )
            and all(
                self._peer_store_ids(region_id) == healthy_peers
                and self._region_leader(region_id) == self.healthy_leader_store_id
                for region_id in self.healthy_region_ids
            )
        )

    def _capture_business_boundary(self) -> None:
        truth_sql = f"SELECT COUNT(*), SUM(amount), BIT_XOR(row_crc) FROM {self.db}.{self.table}"
        truth_rows = require_result_rows(self.env.execute_sql(truth_sql), "capture SF07 pre-fault business truth")
        if len(truth_rows) != 1 or len(truth_rows[0]) != 3:
            raise ValueError(f"SF07 pre-fault truth query returned an invalid row: sql={truth_sql!r}, rows={truth_rows!r}")
        self.pre_fault_truth = tuple(int(value) for value in truth_rows[0])
        expected_truth = (self.expected_count, self.expected_amount_sum, self.expected_checksum)
        if self.pre_fault_truth != expected_truth:
            raise RuntimeError(
                f"SF07 pre-fault truth mismatch: expected={expected_truth!r}, observed={self.pre_fault_truth!r}"
            )
        healthy_sql = f"SELECT COUNT(*), SUM(amount) FROM {self.db}.{self.healthy_table}"
        healthy_rows = require_result_rows(self.env.execute_sql(healthy_sql), "capture SF07 healthy truth")
        if len(healthy_rows) != 1 or len(healthy_rows[0]) != 2:
            raise ValueError(f"SF07 healthy truth query returned an invalid row: sql={healthy_sql!r}, rows={healthy_rows!r}")
        self.healthy_truth = tuple(int(value) for value in healthy_rows[0])
        global_scope_sql = f"SELECT COUNT(*), SUM(amount) FROM {self.db}.{SF07_GLOBAL_SCOPE_TABLE}"
        global_scope_rows = require_result_rows(
            self.env.execute_sql(global_scope_sql),
            "capture SF07 global recovery-scope truth",
        )
        if len(global_scope_rows) != 1 or len(global_scope_rows[0]) != 2:
            raise ValueError(
                f"SF07 global recovery-scope truth query returned an invalid row: "
                f"sql={global_scope_sql!r}, rows={global_scope_rows!r}"
            )
        self.global_scope_truth = tuple(int(value) for value in global_scope_rows[0])
        tso_rows = require_result_rows(self.env.execute_sql("SELECT @@tidb_current_ts"), "capture SF07 pre-fault TSO")
        if len(tso_rows) != 1 or len(tso_rows[0]) != 1:
            raise ValueError(f"SF07 TSO query returned an invalid row: rows={tso_rows!r}")
        self.pre_fault_tso = int(tso_rows[0][0])

    def _block_scheduling(self) -> None:
        for key in self._SCHEDULE_KEYS:
            self._set_schedule_config(key, 0)

    def _stop_failed_stores(self) -> None:
        for node in self.failed_nodes:
            self.env.deployment.stop_component(node)
        self._wait_for(
            lambda: all(not self.env.deployment.node_states()[node]["running"] for node in self.failed_nodes),
            "SF07 failed TiKV processes to stop",
            60,
        )
        self._wait_for(
            lambda: all(
                str(self._store(store_id).get("state_name", "")).casefold() not in {"up", "serving"}
                for store_id in self.failed_store_ids
            ),
            "SF07 failed TiKV Stores to disconnect from PD",
            self._FAULT_TIMEOUT,
        )

    def _verify_fault_state(self) -> None:
        if self.original_schedule is None:
            raise RuntimeError("SF07 fault verification requires the captured schedule baseline")
        for node in self.failed_nodes:
            state = self.env.deployment.node_states()[node]
            if state["running"]:
                raise RuntimeError(f"SF07 failed TiKV process is still running: node={node!r}, state={state!r}")
        for node in self.maintenance_nodes:
            state = self.env.deployment.node_states()[node]
            if not state["running"]:
                raise RuntimeError(
                    f"SF07 maintenance-only TiKV process is not serving: node={node!r}, state={state!r}"
                )
        for store_id in self.maintenance_store_ids:
            store = self._store(store_id)
            if str(store.get("state_name", "")).casefold() not in {"up", "serving"}:
                raise RuntimeError(
                    "SF07 maintenance-only Store is not serving outside the incident: "
                    f"store_id={store_id!r}, store={store!r}"
                )
        for region_id in self.affected_region_ids:
            peers = self._peer_store_ids(region_id)
            expected = set(self.affected_failed_store_ids) | {self.healthy_leader_store_id}
            if peers != expected:
                raise RuntimeError(
                    f"SF07 affected Region lost its planned two-of-three checkout placement: "
                    f"region_id={region_id}, expected={sorted(expected)!r}, observed={sorted(peers)!r}"
                )
        for region_id in self.global_scope_region_ids:
            peers = self._peer_store_ids(region_id)
            expected = {
                self.global_scope_failed_store_id,
                *self.global_scope_healthy_store_ids,
            }
            if peers != expected:
                raise RuntimeError(
                    "SF07 global failed Store scope lost its planned peer placement: "
                    f"region_id={region_id}, expected={sorted(expected)!r}, observed={sorted(peers)!r}"
                )
        for region_id in self.healthy_region_ids:
            peers = self._peer_store_ids(region_id)
            if peers != set(self.healthy_store_ids):
                raise RuntimeError(
                    f"SF07 healthy neighbor Region crossed into a failed Store: "
                    f"region_id={region_id}, healthy_store_ids={self.healthy_store_ids!r}, peers={sorted(peers)!r}"
                )
        target_payload = parse_json_object(
            self.env.execute_sql(f"SELECT COUNT(*) FROM {self.db}.{self.table}"),
            "verify SF07 affected business query failure",
        )
        if target_payload.get("status") != "error":
            raise RuntimeError(
                f"SF07 affected business query remained available after checkout majority loss: payload={target_payload!r}"
            )
        healthy_payload = parse_json_object(
            self.env.execute_sql(f"SELECT COUNT(*), SUM(amount) FROM {self.db}.{self.healthy_table}"),
            "verify SF07 healthy neighbor availability",
        )
        if healthy_payload.get("status") != "success":
            raise RuntimeError(f"SF07 healthy neighbor query failed after fault injection: payload={healthy_payload!r}")
        healthy_rows = healthy_payload.get("result")
        if not isinstance(healthy_rows, list) or len(healthy_rows) != 1 or len(healthy_rows[0]) != 2:
            raise RuntimeError(
                f"SF07 healthy neighbor truth query returned an invalid shape: payload={healthy_payload!r}"
            )
        observed_healthy_truth = tuple(int(value) for value in healthy_rows[0])
        if observed_healthy_truth != self.healthy_truth:
            raise RuntimeError(
                f"SF07 healthy neighbor truth changed during fault injection: "
                f"expected={self.healthy_truth!r}, observed={observed_healthy_truth!r}"
            )
        global_scope_payload = parse_json_object(
            self.env.execute_sql(f"SELECT COUNT(*), SUM(amount) FROM {self.db}.{SF07_GLOBAL_SCOPE_TABLE}"),
            "verify SF07 global recovery-scope availability",
        )
        if global_scope_payload.get("status") != "success":
            raise RuntimeError(
                "SF07 global recovery-scope table became unavailable after the third Store failure: "
                f"payload={global_scope_payload!r}"
            )
        global_scope_rows = global_scope_payload.get("result")
        if not isinstance(global_scope_rows, list) or len(global_scope_rows) != 1 or len(global_scope_rows[0]) != 2:
            raise RuntimeError(
                f"SF07 global recovery-scope truth query returned an invalid shape: payload={global_scope_payload!r}"
            )
        observed_global_scope_truth = tuple(int(value) for value in global_scope_rows[0])
        if observed_global_scope_truth != self.global_scope_truth:
            raise RuntimeError(
                "SF07 global recovery-scope truth changed during fault injection: "
                f"expected={self.global_scope_truth!r}, observed={observed_global_scope_truth!r}"
            )

    def _region_peer_baseline(self, region_ids: tuple[int, ...]) -> tuple[tuple[int, tuple[int, ...]], ...]:
        return tuple((region_id, tuple(sorted(self._peer_store_ids(region_id)))) for region_id in region_ids)

    def _peer_store_ids(self, region_id: int) -> set[int]:
        # A peers-less record is the transient pending/merge shape; it reads as
        # "not converged yet" inside the placement wait loop.
        return {int(peer["store_id"]) for peer in self._region(region_id).get("peers") or ()}

    def _region_leader(self, region_id: int) -> int | None:
        leader = self._region(region_id).get("leader")
        return None if leader is None else int(leader["store_id"])

    def _store(self, store_id: int) -> dict:
        stores = self.env.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
        matches = [
            item["store"] | {"status": item["status"]}
            for item in stores
            if int(item["store"]["id"]) == int(store_id)
        ]
        if len(matches) != 1:
            raise RuntimeError(f"SF07 PD Store lookup is not unique: store_id={store_id}, matches={matches!r}")
        return matches[0]

    def _region(self, region_id: int) -> dict:
        return self.env.deployment.pd_request("GET", f"/pd/api/v1/region/id/{int(region_id)}")

    def _set_schedule_config(self, key: str, value: object) -> None:
        self.env.deployment.pd_request("POST", "/pd/api/v1/config", {key: value})

    def _unsafe_recovery_status(self):
        output = self.env.deployment.online_unsafe_recovery("get")
        if output in ([], {}, None):
            return None
        return output

    @staticmethod
    def _recovery_terminal(output: object) -> bool:
        text = str(output).casefold()
        return "unsafe recovery finished" in text or "unsafe recovery failed" in text

    @staticmethod
    def _wait_for(predicate, description: str, timeout: int) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(1)
        raise _SF07WaitTimeout(f"Timed out waiting for {description}: timeout={timeout}")


class TidbSystemFailurePendingOfflineScenario(TiDBScenario):
    scenario_id = "tidb_system_failure_pending_offline"
    description = "Restore a TiDB v8.1 checkout data range after a storage availability incident."
    cases = (
        _CASE,
        replace(_CASE, case_id="store_migration_pending_offline", case_no=1,
                evaluator=TidbSystemFailurePendingOfflineStoreMigrationPendingEvaluatorCase,
                difficulty=DifficultyCalibration(
                    diagnostic_depth=6,
                    environmental_complexity=0.473684,
                    reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
                    protocol_version='difficulty-v2',
                ),
                background_workload=replace(_CASE.background_workload, worker_count=4, seed=20260820)),
    )

    def build_fault_plan(
        self,
        case: TidbSystemFailurePendingOfflineCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailurePendingOfflineInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "index": case.index,
                    "healthy_table": case.healthy_table,
                    "noise_tables": case.noise_tables,
                    "failed_nodes": case.failed_nodes,
                    "healthy_nodes": case.healthy_nodes,
                    "maintenance_nodes": case.maintenance_nodes,
                    "row_count": case.row_count,
                    "expected_count": case.expected_count,
                    "expected_amount_sum": case.expected_amount_sum,
                    "expected_checksum": case.expected_checksum,
                    "new_write_id": case.new_write_id,
                    "new_write_tenant_id": case.new_write_tenant_id,
                    "new_write_amount": case.new_write_amount,
                    "new_write_status": case.new_write_status,
                    "new_write_payload": case.new_write_payload,
                },
            ),
        )
