from __future__ import annotations

import json
import re
import time
import zlib
from collections.abc import Mapping
from dataclasses import dataclass, replace

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    run_sql_batches,
    validate_sql_identifier,
)
from src.execution.deployment import canonical_pd_config
from src.scenarios.workloads import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase

from ...base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from ..runtime import TIDB_V8_1_0, tidb_runtime
from src.scenarios.evaluation.tidb.system_failure.pd_total_metadata_loss_recovery import (
    TidbSystemFailurePdMetadataRecoveryEvaluatorCase,
    TidbSystemFailurePdTotalMetadataLossRecoveryEvaluatorCase,
)


K03_DB = "bench_k03"
K03_ORDERS = "orders"
K03_ORDER_ITEMS = "order_items"
K03_LIVE_EVENTS = "live_events"
K03_ORDER_ROWS = 8192
K03_ITEM_ROWS = 8192
K03_NEW_EVENT_ID = 900001
K03_CLOCK_OFFSET_LIMIT_MS = 100
_ALLOCATOR_END_PATTERN = re.compile(r"\[new-end=(\d+)\]")
_INIT_CLUSTER_ID_PATTERN = re.compile(r'\["init cluster id"\].*?\[cluster-id=(\d+)\]')
_BOOTSTRAP_CLUSTER_ID_PATTERN = re.compile(r'\["bootstrap cluster ok"\].*?\[cluster-id=(\d+)\]')


def extract_allocator_high_water(historical_logs: Mapping[str, object]) -> int:
    values = []
    for target, raw_lines in historical_logs.items():
        if not isinstance(raw_lines, list):
            raise TypeError(
                f"K03 historical PD log evidence must be a line list: target={target!r}, value={raw_lines!r}"
            )
        for line in raw_lines:
            if not isinstance(line, str):
                raise TypeError(
                    f"K03 historical PD log evidence must contain strings: target={target!r}, line={line!r}"
                )
            match = _ALLOCATOR_END_PATTERN.search(line)
            if match is not None:
                values.append(int(match.group(1)))
    if not values:
        raise RuntimeError(
            "K03 historical PD logs contain no idAllocator new-end evidence: "
            f"targets={tuple(historical_logs)!r}"
        )
    return max(values)


def extract_original_cluster_id(historical_logs: Mapping[str, object]) -> int:
    values = []
    for target, raw_lines in historical_logs.items():
        if not isinstance(raw_lines, list):
            raise TypeError(
                f"K03 historical PD log evidence must be a line list: target={target!r}, value={raw_lines!r}"
            )
        for line in raw_lines:
            if not isinstance(line, str):
                raise TypeError(
                    f"K03 historical PD log evidence must contain strings: target={target!r}, line={line!r}"
                )
            for pattern in (_INIT_CLUSTER_ID_PATTERN, _BOOTSTRAP_CLUSTER_ID_PATTERN):
                match = pattern.search(line)
                if match is not None:
                    values.append(int(match.group(1)))
    if not values:
        raise RuntimeError(
            "K03 historical PD logs contain no init cluster id evidence: "
            f"targets={tuple(historical_logs)!r}"
        )
    distinct = tuple(sorted(set(values)))
    if len(distinct) != 1:
        raise RuntimeError(
            "K03 historical PD logs disagree on the original cluster ID: "
            f"cluster_ids={distinct!r}, targets={tuple(historical_logs)!r}"
        )
    return distinct[0]


def k03_order_amount(order_id: int) -> int:
    return 1000 + (order_id * 37) % 9000


def k03_order_crc(order_id: int) -> int:
    tenant_id = order_id % 17
    amount = k03_order_amount(order_id)
    return zlib.crc32(f"k03:{order_id}:{tenant_id}:{amount}:paid".encode()) & 0xFFFFFFFF


def k03_item_qty(item_id: int) -> int:
    return 1 + item_id % 5


def k03_item_crc(item_id: int) -> int:
    order_id = (item_id - 1) % K03_ORDER_ROWS + 1
    return zlib.crc32(f"k03-item:{item_id}:{order_id}:{k03_item_qty(item_id)}".encode()) & 0xFFFFFFFF


K03_ORDER_AMOUNT_SUM = sum(k03_order_amount(order_id) for order_id in range(1, K03_ORDER_ROWS + 1))
K03_ORDER_CHECKSUM = 0
for _order_id in range(1, K03_ORDER_ROWS + 1):
    K03_ORDER_CHECKSUM ^= k03_order_crc(_order_id)
K03_ITEM_QTY_SUM = sum(k03_item_qty(item_id) for item_id in range(1, K03_ITEM_ROWS + 1))
K03_ITEM_CHECKSUM = 0
for _item_id in range(1, K03_ITEM_ROWS + 1):
    K03_ITEM_CHECKSUM ^= k03_item_crc(_item_id)


K03_DP_FACTORS = (
    "the same maintenance record showed pd-0, pd-1, and pd-2 data directories non-empty before maintenance and empty after the wipe while the original TiKV data remained",
    "the rebuilt PD exposed a new cluster ID and the preserved TiKV members rejected it as a cluster ID mismatch",
    "the original cluster ID must be recovered from pre-loss TiKV or PD evidence rather than accepting the rebuilt PD identity",
    "the pd-recover alloc-id must be strictly higher than the largest observed allocator high-water value",
    "pd-recover does not repair TSO, so clock evidence and post-recovery TSO monotonicity are required",
    "a healthy rebuilt PD endpoint is insufficient because the preserved TiKV Store and Region metadata is not served under the rebuilt identity",
    "force-new-cluster or accepting the rebuilt cluster ID would create a different cluster and is not recovery of the original data",
)


def _reference_report() -> dict:
    same_record_loss_evidence = (
        "same record_id=reference-full-loss: pd-0 before non-empty -> after empty; "
        "pd-1 before non-empty -> after empty; pd-2 before non-empty -> after empty; "
        "TiKV data retained"
    )
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": factor,
                    "entity": "pd_all_metadata_lost_restore_original_cluster",
                    "evidence": [
                        same_record_loss_evidence
                        if factor == K03_DP_FACTORS[0]
                        else f"reference observed {factor}"
                    ],
                }
                for factor in K03_DP_FACTORS
            ]
        },
        "outcome": {
            "changes": [
                "stopped database services, executed the fixed-version pd-recover against the original identity, and restarted the original topology",
                "inserted one new live event only after the original control plane recovered",
            ],
            "verification": [
                "original PD cluster identity, quorum, allocator high-water, Store/Region registration, pre-recovery clock evidence, and TSO checks passed",
                "orders and order_items checksums remained unchanged and the new live event committed",
            ],
        },
        "summary": "The original TiDB control plane was recovered after total PD metadata loss without rebuilding the business data.",
    }


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailurePdTotalMetadataLossRecoveryCase(TiDBScenarioCase):
    db: str
    orders_table: str
    order_items_table: str
    live_events_table: str
    order_rows: int
    item_rows: int
    expected_order_amount_sum: int
    expected_order_checksum: int
    expected_item_qty_sum: int
    expected_item_checksum: int
    new_event_id: int
    clock_offset_limit_ms: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailurePdTotalMetadataLossRecoveryForPdAllMetadataLostRestoreOriginalClusterScenarioCase(
    TidbSystemFailurePdTotalMetadataLossRecoveryCase
):
    pass


_CASE = TidbSystemFailurePdTotalMetadataLossRecoveryForPdAllMetadataLostRestoreOriginalClusterScenarioCase(
    case_id="pd_all_metadata_lost_restore_original_cluster",
    case_no=0,
    evaluator=TidbSystemFailurePdTotalMetadataLossRecoveryEvaluatorCase,
    title="The existing TiDB checkout database is unavailable after maintenance.",
    alert=(
        "[SEV1] The checkout database stopped accepting reads and writes after a maintenance window. Health probes "
        "respond, but the existing orders and order_items data are not being served. Preserve those business tables "
        "and restore the declared 3 PD + 3 TiKV + 2 TiDB topology. In this isolated recovery case you may inspect "
        "bounded component evidence, manage declared services, use an exposed recovery procedure, and insert exactly "
        f"one non-empty row into {K03_DB}.{K03_LIVE_EVENTS} with event_id={K03_NEW_EVENT_ID} after recovery. Do not "
        "rewrite the protected business tables or run destructive SQL. "
        "Establish the causal failure and recovery preconditions from component state, logs, and clock observations "
        "before acting."
    ),
    initial_state={
        "status": "healthy_before_maintenance_outage",
        "topology": "3 PD + 3 TiKV + 2 TiDB",
        "business_data": f"{K03_DB}.{K03_ORDERS} and {K03_DB}.{K03_ORDER_ITEMS} are readable",
        "control_plane": "one original PD cluster identity and quorum",
    },
    expected_target={
        "status": "original_cluster_recovered",
        "cluster_identity": "sealed original identity, not the rebuilt identity",
        "pd_quorum": "3 members, one leader, no temporary recovery service",
        "stores_regions": "all original Stores Up and original Region inventory visible",
        "clock_precondition": "before pd-recover, maximum absolute observed container offset <= 100 ms",
        "business_truth": (
            f"orders=({K03_ORDER_ROWS},{K03_ORDER_AMOUNT_SUM},{K03_ORDER_CHECKSUM}), "
            f"order_items=({K03_ITEM_ROWS},{K03_ITEM_QTY_SUM},{K03_ITEM_CHECKSUM})"
        ),
        "new_write": f"{K03_DB}.{K03_LIVE_EVENTS} contains event_id={K03_NEW_EVENT_ID}",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=(),
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        worker_count=1,
        seed=20260818,
        warmup_seconds=0,
    ),
    reference_report=_reference_report(),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.473684,
        reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
        protocol_version='difficulty-v2',
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=120,
        bootstrap_cache_enabled=False,
    ),
    db=K03_DB,
    orders_table=K03_ORDERS,
    order_items_table=K03_ORDER_ITEMS,
    live_events_table=K03_LIVE_EVENTS,
    order_rows=K03_ORDER_ROWS,
    item_rows=K03_ITEM_ROWS,
    expected_order_amount_sum=K03_ORDER_AMOUNT_SUM,
    expected_order_checksum=K03_ORDER_CHECKSUM,
    expected_item_qty_sum=K03_ITEM_QTY_SUM,
    expected_item_checksum=K03_ITEM_CHECKSUM,
    new_event_id=K03_NEW_EVENT_ID,
    clock_offset_limit_ms=K03_CLOCK_OFFSET_LIMIT_MS,
)

_RECOVERY_AUDIT_CASE = replace(
    _CASE,
    case_id="pd_metadata_recovery",
    case_no=1,
    evaluator=TidbSystemFailurePdMetadataRecoveryEvaluatorCase,
    title="The existing TiDB recovery-audit database is unavailable after maintenance.",
    alert=(
        "[SEV1] The recovery-audit database stopped accepting reads and writes after a maintenance window. "
        "Health probes respond, but the existing recovery_orders and recovery_order_items data are not being "
        "served. Preserve those business tables and restore the declared 3 PD + 3 TiKV + 2 TiDB topology. "
        "After recovery, insert exactly one non-empty row into recovery_audit.recovery_events with "
        "event_id=2026090101. Do not rewrite the protected business tables or run destructive SQL. Establish "
        "the causal failure and recovery preconditions from component state, logs, and clock observations before acting."
    ),
    initial_state={
        **_CASE.initial_state,
        "business_data": "recovery_audit.recovery_orders and recovery_audit.recovery_order_items are readable",
    },
    expected_target={
        **_CASE.expected_target,
        "new_write": "recovery_audit.recovery_events contains event_id=2026090101",
    },
    db="recovery_audit",
    orders_table="recovery_orders",
    order_items_table="recovery_order_items",
    live_events_table="recovery_events",
    new_event_id=2026090101,
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.5,
        reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
        protocol_version='difficulty-v2',
    ),
)


class TidbSystemFailurePdTotalMetadataLossRecoveryInjector(BaseFaultInjector):
    def __init__(self) -> None:
        self.env = None
        self.db = None
        self.orders_table = None
        self.order_items_table = None
        self.live_events_table = None
        self.order_rows = None
        self.item_rows = None
        self.new_event_id = None
        self.clock_offset_limit_ms = None
        self.original_identity = None
        self.original_cluster_id = None
        self.new_cluster_id = None
        self.allocator_high_water = None
        self.safe_allocator_floor = None
        self.pre_fault_tso = None
        self.original_store_ids = ()
        self.original_region_count = None
        self.original_pd_config = None
        self.business_truth = None
        self._configured = False

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._create_business_state()
        deployment = self.env.deployment
        recovery_artifact = deployment.capture_pd_recovery_artifact()
        self._capture_original_state(recovery_artifact)
        for target in (*self._database_targets("tidb"), *self._database_targets("tikv")):
            deployment.stop_component(target)
        for target in self._database_targets("pd"):
            deployment.stop_component(target)
        deployment.wipe_pd_metadata()
        for target in self._database_targets("pd"):
            deployment.start_component(target)
        deployment._wait(
            "pd",
            self._rebuilt_pd_is_ready,
            180,
        )
        for target in (*self._database_targets("tikv"), *self._database_targets("tidb")):
            deployment.start_component(target)
        self._wait_for_fault_evidence()
        self._verify_fault_state()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_fault_state()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._verify_fault_state()
        deployment = self.env.deployment
        current_identity = deployment.pd_identity_observation()
        inspection = deployment.pd_recovery_inspection()
        clock = deployment.clock_status_observation()
        mismatch_targets = tuple(
            target
            for target in self._database_targets("tikv")
            if self._cluster_mismatch_lines(target)
        )
        if not mismatch_targets:
            raise RuntimeError(
                "K03 fault has no TiKV cluster-ID mismatch evidence: "
                f"run_id={context.run_id!r}, targets={self._database_targets('tikv')!r}"
            )
        return {
            "original_cluster_id": self.original_cluster_id,
            "new_cluster_id": self.new_cluster_id,
            "allocator_high_water": self.allocator_high_water,
            "safe_allocator_floor": self.safe_allocator_floor,
            "pre_fault_tso": self.pre_fault_tso,
            "original_store_ids": self.original_store_ids,
            "original_region_count": self.original_region_count,
            "original_pd_config": self.original_pd_config,
            "business_truth": self.business_truth,
            "clock_offset_limit_ms": self.clock_offset_limit_ms,
            "fault_record_id": deployment.pd_recovery_current_record_id(),
            "mismatch_targets": mismatch_targets,
            "fault_identity": current_identity,
            "inspection_snapshot": inspection,
            "clock_snapshot": clock,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        deployment = self.env.deployment
        states = deployment.node_states()
        for target in (*self._database_targets("tidb"), *self._database_targets("tikv"), *self._database_targets("pd")):
            if states[target]["running"]:
                deployment.stop_component(target)

    def recover(self, context: FaultLifecycleContext) -> None:
        if self.env is None:
            raise RuntimeError("K03 recovery was called before injector configuration")
        if self.env.deployment.is_ready():
            require_sql_success(
                self.env.execute_sql_trusted(f"DROP DATABASE {self.db}"),
                f"drop K03 database {self.db}",
            )

    def _configure(self, config: Mapping[str, object], env) -> None:
        if self._configured:
            if self.env is not env:
                raise RuntimeError("K03 injector cannot change environment after configuration")
            return
        self.env = env
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.orders_table = validate_sql_identifier(str(config["orders_table"]), "orders table")
        self.order_items_table = validate_sql_identifier(
            str(config["order_items_table"]), "order_items table"
        )
        self.live_events_table = validate_sql_identifier(
            str(config["live_events_table"]), "live_events table"
        )
        self.order_rows = int(config["order_rows"])
        self.item_rows = int(config["item_rows"])
        self.new_event_id = int(config["new_event_id"])
        self.clock_offset_limit_ms = int(config["clock_offset_limit_ms"])
        if self.env.deployment.image_group_enabled or self.env.deployment.bootstrap_cache_enabled:
            raise RuntimeError(
                "K03 requires bootstrap_cache_enabled=false and no image group: "
                f"run_id={self.env.run_id!r}, image_group={self.env.deployment.image_group_enabled}, "
                f"bootstrap_cache={self.env.deployment.bootstrap_cache_enabled}"
            )
        self._configured = True

    def _database_targets(self, component: str) -> tuple[str, ...]:
        return tuple(f"{component}/{service}" for service in self.env.deployment.COMPONENTS[component])

    def _create_business_state(self) -> None:
        require_sql_success(
            self.env.execute_sql(f"CREATE DATABASE {self.db}"),
            f"create K03 database {self.db}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.db}.{self.orders_table} ("
                "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, amount BIGINT NOT NULL, "
                "status VARCHAR(16) NOT NULL, record_crc BIGINT NOT NULL"
                ")"
            ),
            "create K03 orders table",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.db}.{self.order_items_table} ("
                "item_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, sku BIGINT NOT NULL, "
                "qty INT NOT NULL, item_crc BIGINT NOT NULL, KEY idx_order_id (order_id)"
                ")"
            ),
            "create K03 order_items table",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.db}.{self.live_events_table} ("
                "event_id BIGINT PRIMARY KEY, payload VARCHAR(128) NOT NULL, "
                "created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)"
                ")"
            ),
            "create K03 live_events table",
        )
        order_values = (
            f"({order_id},{order_id % 17},{k03_order_amount(order_id)},'paid',{k03_order_crc(order_id)})"
            for order_id in range(1, self.order_rows + 1)
        )
        run_sql_batches(
            self.env.execute_sql,
            f"INSERT INTO {self.db}.{self.orders_table} "
            "(order_id,tenant_id,amount,status,record_crc) VALUES ",
            order_values,
            128,
            "insert K03 orders",
        )
        item_values = (
            f"({item_id},{(item_id - 1) % self.order_rows + 1},{100000 + item_id},"
            f"{k03_item_qty(item_id)},{k03_item_crc(item_id)})"
            for item_id in range(1, self.item_rows + 1)
        )
        run_sql_batches(
            self.env.execute_sql,
            f"INSERT INTO {self.db}.{self.order_items_table} "
            "(item_id,order_id,sku,qty,item_crc) VALUES ",
            item_values,
            128,
            "insert K03 order_items",
        )
        require_sql_success(
            self.env.execute_sql(
                f"SPLIT TABLE {self.db}.{self.orders_table} BETWEEN (0) AND ({self.order_rows + 1}) REGIONS 8"
            ),
            "split K03 orders into Regions",
        )
        require_sql_success(
            self.env.execute_sql(
                f"SPLIT TABLE {self.db}.{self.order_items_table} BETWEEN (0) AND ({self.item_rows + 1}) REGIONS 8"
            ),
            "split K03 order_items into Regions",
        )
        self._wait_for_region_count(minimum=4, timeout=180)

    def _capture_original_state(self, recovery_artifact: Mapping[str, object]) -> None:
        identity = recovery_artifact["historical_identity"]
        self.original_cluster_id = int(identity["cluster"]["id"])
        self.allocator_high_water = extract_allocator_high_water(
            recovery_artifact["historical_pd_logs"]
        )
        self.safe_allocator_floor = self.allocator_high_water + 1
        self.pre_fault_tso = self.env.current_tso()
        stores = recovery_artifact["historical_stores"]["stores"]
        self.original_store_ids = tuple(sorted(int(item["store"]["id"]) for item in stores))
        if len(self.original_store_ids) != 3:
            raise RuntimeError(
                f"K03 requires exactly three original TiKV Stores: stores={self.original_store_ids!r}"
            )
        self.original_region_count = self._region_count()
        if self.original_region_count < 4:
            raise RuntimeError(
                f"K03 business data did not produce enough Regions: region_count={self.original_region_count}"
            )
        self.original_pd_config = canonical_pd_config(
            self.env.deployment.pd_request("GET", "/pd/api/v1/config")
        )
        self.business_truth = self._business_truth()
        self.original_identity = identity

    def _business_truth(self) -> dict[str, int]:
        orders = json_object(
            self.env.execute_sql_trusted(
                f"SELECT COUNT(*), SUM(amount), BIT_XOR(record_crc) "
                f"FROM {self.db}.{self.orders_table}"
            ),
            "K03 orders truth",
        )["result"]
        items = json_object(
            self.env.execute_sql_trusted(
                f"SELECT COUNT(*), SUM(qty), BIT_XOR(item_crc) "
                f"FROM {self.db}.{self.order_items_table}"
            ),
            "K03 order_items truth",
        )["result"]
        if len(orders) != 1 or len(items) != 1:
            raise RuntimeError(f"K03 business truth returned unexpected rows: orders={orders!r}, items={items!r}")
        return {
            "orders_count": int(orders[0][0]),
            "orders_amount_sum": int(orders[0][1]),
            "orders_checksum": int(orders[0][2]),
            "items_count": int(items[0][0]),
            "items_qty_sum": int(items[0][1]),
            "items_checksum": int(items[0][2]),
        }

    def _region_count(self) -> int:
        rows = json_object(
            self.env.execute_sql_trusted(
                "SELECT COUNT(DISTINCT REGION_ID) "
                "FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
                f"WHERE DB_NAME = '{self.db}'"
            ),
            "K03 Region count",
        )["result"]
        if len(rows) != 1 or len(rows[0]) != 1:
            raise RuntimeError(f"K03 Region count returned unexpected rows: rows={rows!r}")
        return int(rows[0][0])

    def _wait_for_region_count(self, minimum: int, timeout: int) -> None:
        deadline = time.monotonic() + timeout
        last_count = None
        while time.monotonic() < deadline:
            last_count = self._region_count()
            if last_count >= minimum:
                return
            time.sleep(1)
        raise RuntimeError(
            f"K03 Region count did not reach the required minimum: minimum={minimum}, observed={last_count}, timeout={timeout}"
        )

    def _rebuilt_pd_is_ready(self) -> None:
        deployment = self.env.deployment
        members = deployment.pd_request("GET", "/pd/api/v1/members")["members"]
        leader = deployment.pd_request("GET", "/pd/api/v1/leader")
        if len(members) != 3 or leader.get("name") not in self.env.deployment.COMPONENTS["pd"]:
            raise RuntimeError(
                f"K03 rebuilt PD quorum is not ready: members={members!r}, leader={leader!r}"
            )

    def _wait_for_fault_evidence(self) -> None:
        deadline = time.monotonic() + 180
        last_targets = ()
        while time.monotonic() < deadline:
            last_targets = tuple(
                target
                for target in self._database_targets("tikv")
                if self._cluster_mismatch_lines(target)
            )
            if last_targets:
                return
            time.sleep(1)
        raise RuntimeError(
            f"K03 TiKV cluster-ID mismatch evidence did not appear: targets={last_targets!r}, timeout=180"
        )

    def _cluster_mismatch_lines(self, target: str) -> tuple[str, ...]:
        content = self.env.deployment.read_logs(target, lines=10000)
        return tuple(
            line
            for line in content.splitlines()
            if "cluster" in line.casefold()
            and any(token in line.casefold() for token in ("mismatch", "different", "reject", "not match"))
        )

    def _verify_fault_state(self) -> None:
        identity = self.env.deployment.pd_identity_observation()
        current_cluster_id = int(identity["cluster"]["id"])
        self.new_cluster_id = current_cluster_id
        if current_cluster_id == self.original_cluster_id:
            raise RuntimeError(
                f"K03 fault did not create a new PD identity: original={self.original_cluster_id}, current={current_cluster_id}"
            )
        mismatch_targets = tuple(
            target
            for target in self._database_targets("tikv")
            if self._cluster_mismatch_lines(target)
        )
        if not mismatch_targets:
            raise RuntimeError(
                f"K03 TiKV cluster-ID mismatch is not visible: original={self.original_cluster_id}, current={current_cluster_id}"
            )


class TidbSystemFailurePdTotalMetadataLossRecoveryScenario(TiDBScenario):
    scenario_id = "tidb_system_failure_pd_metadata_recovery"
    description = "Restores the declared TiDB checkout topology after a maintenance outage while preserving business data."
    cases = (_CASE, _RECOVERY_AUDIT_CASE)

    def build_fault_plan(
        self,
        case: TidbSystemFailurePdTotalMetadataLossRecoveryCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailurePdTotalMetadataLossRecoveryInjector,
                config={
                    "db": case.db,
                    "orders_table": case.orders_table,
                    "order_items_table": case.order_items_table,
                    "live_events_table": case.live_events_table,
                    "order_rows": case.order_rows,
                    "item_rows": case.item_rows,
                    "new_event_id": case.new_event_id,
                    "clock_offset_limit_ms": case.clock_offset_limit_ms,
                },
            ),
        )
