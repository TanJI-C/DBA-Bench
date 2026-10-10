import time
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import List

import pymysql

from src.database.sql import sql_literal
from src.scenarios.evaluation.tidb.health_check.long_transaction_mvcc import (
    TidbHealthCheckLongTransactionMvccEvaluatorCase,
    TidbHealthCheckLongTransactionMvccForSingleHandoffEvaluatorCase,
)
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    run_cleanup_steps,
    validate_sql_identifier,
)
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


_WORKER_ALIASES = tuple(f"worker-{index:02d}" for index in range(1, 14))
_HISTORICAL_PROCESSLIST_ALIASES = tuple(
    f"worker-history-{index:02d}" for index in range(1, 9)
)
_STALE_WORKER_ID = 7
_NON_BLOCKING_ABANDONED_WORKER_IDS = (2, 8, 12)
_DELAYED_CHECKPOINT_WORKER_IDS = (1, 5, 9, 13)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckLongTransactionMvccCase(TiDBScenarioCase):
    database: str
    table: str
    audit_table: str
    lease_table: str
    history_table: str
    checkpoint_table: str
    row_count: int
    versioned_row_count: int
    updated_version: int
    worker_aliases: tuple[str, ...]
    historical_processlist_aliases: tuple[str, ...]
    stale_worker_id: int
    non_blocking_abandoned_worker_ids: tuple[int, ...]
    delayed_checkpoint_worker_ids: tuple[int, ...]

    @property
    def qualified_table(self) -> str:
        return f"{self.database}.{self.table}"

    @property
    def qualified_audit_table(self) -> str:
        return f"{self.database}.{self.audit_table}"

    @property
    def qualified_lease_table(self) -> str:
        return f"{self.database}.{self.lease_table}"

    @property
    def qualified_history_table(self) -> str:
        return f"{self.database}.{self.history_table}"

    @property
    def qualified_checkpoint_table(self) -> str:
        return f"{self.database}.{self.checkpoint_table}"

    @property
    def target_worker_alias(self) -> str:
        return self.worker_aliases[self.stale_worker_id - 1]

    @property
    def noise_transaction_count(self) -> int:
        return len(self.worker_aliases)

    @property
    def history_row_count(self) -> int:
        return len(self.worker_aliases) + 1 + len(self.non_blocking_abandoned_worker_ids)

    @property
    def checkpoint_row_count(self) -> int:
        return (
            len(self.worker_aliases) * 3
            + 1
            + len(self.delayed_checkpoint_worker_ids)
        )

    @property
    def integrity_sql(self) -> str:
        return (
            f"SELECT COUNT(*), SUM(version = {self.updated_version}), "
            "BIT_XOR(CRC32(CONCAT_WS('#', order_id, customer_id, status, amount, "
            "version, updated_at, payload))) "
            f"FROM {self.qualified_table}"
        )

    @property
    def lease_registry_sql(self) -> str:
        return (
            "SELECT worker_id, worker_alias, workload_class, run_state, lease_state, "
            "heartbeat_at, lease_expires_at, session_id "
            f"FROM {self.qualified_lease_table} ORDER BY worker_id"
        )

    @property
    def lease_history_sql(self) -> str:
        return (
            "SELECT event_id, worker_id, worker_alias, lease_generation, event_state, "
            "observed_at, observed_session_id, handoff_reason "
            f"FROM {self.qualified_history_table} ORDER BY worker_id, event_id"
        )

    @property
    def checkpoint_sql(self) -> str:
        return (
            "SELECT checkpoint_id, worker_id, checkpoint_at, checkpoint_state, "
            "commit_tso, batch_name, checkpoint_note "
            f"FROM {self.qualified_checkpoint_table} "
            "ORDER BY worker_id, checkpoint_at, checkpoint_id"
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckLongTransactionMvccForDailyReconciliationSnapshotTransactionScenarioCase(
    TidbHealthCheckLongTransactionMvccCase
):
    pass


def build_tidb_hc09_business_profiles(
    table: str = "hc09_order_versions",
    audit_table: str = "hc09_order_audit",
    lease_table: str = "hc09_job_state",
    history_table: str = "hc09_job_events",
    checkpoint_table: str = "hc09_run_checkpoints",
) -> List[WorkloadProfile]:
    return [
        WorkloadProfile(
            name="checkout_order_point_lookup",
            sql=(
                f"SELECT order_id, status, amount, version FROM {table} "
                "WHERE order_id = 17"
            ),
            qps=0.8,
            tier="LIGHT",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="customer_order_history_rollup",
            sql=(
                "SELECT customer_id, COUNT(*) AS order_count, "
                f"SUM(amount) AS gross_amount FROM {table} "
                "WHERE customer_id BETWEEN 10 AND 90 GROUP BY customer_id "
                "ORDER BY gross_amount DESC LIMIT 20"
            ),
            qps=0.35,
            tier="MEDIUM",
            application_name="customer-360-api",
        ),
        WorkloadProfile(
            name="order_status_dashboard",
            sql=(
                f"SELECT status, COUNT(*) AS order_count, SUM(amount) AS gross_amount "
                f"FROM {table} GROUP BY status ORDER BY status"
            ),
            qps=0.45,
            tier="LIGHT",
            application_name="operations-dashboard",
        ),
        WorkloadProfile(
            name="recent_order_feed",
            sql=(
                f"SELECT order_id, customer_id, status, updated_at FROM {table} "
                "WHERE updated_at >= NOW() - INTERVAL 30 DAY "
                "ORDER BY updated_at DESC, order_id DESC LIMIT 40"
            ),
            qps=0.3,
            tier="LIGHT",
            application_name="order-feed-api",
        ),
        WorkloadProfile(
            name="reconciliation_crc_sample",
            sql=(
                "SELECT COUNT(*) AS row_count, "
                "BIT_XOR(CRC32(CONCAT_WS('#', order_id, version, amount, payload))) "
                f"AS crc FROM {table} WHERE order_id BETWEEN 1 AND 200"
            ),
            qps=0.25,
            tier="MEDIUM",
            application_name="reconciliation-monitor",
        ),
        WorkloadProfile(
            name="order_audit_recent_rollup",
            sql=(
                f"SELECT event_type, COUNT(*) AS event_count FROM {audit_table} "
                "GROUP BY event_type ORDER BY event_type"
            ),
            qps=0.3,
            tier="LIGHT",
            application_name="audit-service",
        ),
        WorkloadProfile(
            name="fulfillment_status_preview",
            sql=(
                f"SELECT status, MIN(updated_at), MAX(updated_at), COUNT(*) FROM {table} "
                "WHERE order_id BETWEEN 50 AND 150 GROUP BY status"
            ),
            qps=0.25,
            tier="MEDIUM",
            application_name="fulfillment-planner",
        ),
        WorkloadProfile(
            name="worker_supervisor_health",
            sql=(
                "SELECT worker_id, run_state, lease_state, lease_expires_at "
                f"FROM {lease_table} ORDER BY worker_id"
            ),
            qps=0.18,
            tier="MONITOR",
            application_name="worker-supervisor",
        ),
        WorkloadProfile(
            name="handoff_audit_sample",
            sql=(
                "SELECT worker_id, worker_alias, lease_generation, event_state, "
                "observed_at, observed_session_id, handoff_reason "
                f"FROM {history_table} ORDER BY worker_id, event_id"
            ),
            qps=0.14,
            tier="MONITOR",
            application_name="worker-supervisor",
        ),
        WorkloadProfile(
            name="reconciliation_progress_sample",
            sql=(
                "SELECT checkpoint_id, worker_id, checkpoint_at, checkpoint_state, "
                f"commit_tso, batch_name FROM {checkpoint_table} "
                "ORDER BY worker_id, checkpoint_at, checkpoint_id"
            ),
            qps=0.13,
            tier="MONITOR",
            application_name="reconciliation-monitor",
        ),
        WorkloadProfile(
            name="transaction_health_sample",
            sql=(
                "SELECT SESSION_ID, START_TIME, STATE, USER, DB "
                "FROM INFORMATION_SCHEMA.CLUSTER_TIDB_TRX "
                "ORDER BY START_TIME, SESSION_ID LIMIT 80"
            ),
            qps=0.12,
            tier="MONITOR",
            application_name="transaction-monitor",
        ),
    ]


_CASE = TidbHealthCheckLongTransactionMvccForDailyReconciliationSnapshotTransactionScenarioCase(
    case_id="daily_reconciliation_snapshot_transaction",
    reference_report={
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": ["ended the one pre-write abandoned worker session"],
            "verification": [
                "current workers, post-write abandoned retries, checkpoint history, "
                "20 new versions, and the post-write CRC were preserved"
            ],
        },
        "summary": (
            "The reference path correlated worker handoffs, checkpoint windows, and "
            "live transaction TSO before applying one session-scoped repair."
        ),
    },
    case_no=0,
    evaluator=TidbHealthCheckLongTransactionMvccEvaluatorCase,
    title="Routine health review of retained MVCC versions and worker handoffs.",
    alert=(
        "例行 TiDB 集群健康检查：订单业务查询和 QPS 仍在正常范围，但历史版本保留窗口在扩大。"
        "请把集群事务、进程列表和业务运行时的交接记录关联起来复核。会话名称很相似，其中既有"
        "当前服务读取，也有换岗后的旧读取和历史审计连接。请识别真正影响版本回收的对象，只做"
        "最小范围处理，并保持当前服务和已提交业务数据不变。"
    ),
    initial_state={
        "status": "serving",
        "snapshot_transactions": 17,
        "historical_processlist_connections": 8,
        "worker_lease_registry_rows": 13,
        "worker_session_history_rows": 17,
        "checkpoint_rows": 44,
        "new_versions": 20,
    },
    expected_target={
        "pre_write_abandoned_session": "gone",
        "current_worker_sessions": 13,
        "post_write_abandoned_sessions": 3,
        "historical_processlist_connections": 8,
        "checkpoint_rows": 44,
        "new_versions": 20,
        "business_integrity": "post-write row count and CRC unchanged",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(
            build_tidb_hc09_business_profiles(
                "test.hc09_order_versions",
                "test.hc09_order_audit",
                "test.hc09_job_state",
                "test.hc09_job_events",
                "test.hc09_run_checkpoints",
            )
        ),
        worker_count=4,
        seed=9109,
        warmup_seconds=8,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.940171,
        reference_run_ids=(
            "reference-211__"
            "tidb_health_check_long_transaction_mvcc__"
            "daily_reconciliation_snapshot_transaction__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=120,
    ),
    database="test",
    table="hc09_order_versions",
    audit_table="hc09_order_audit",
    lease_table="hc09_job_state",
    history_table="hc09_job_events",
    checkpoint_table="hc09_run_checkpoints",
    row_count=200,
    versioned_row_count=20,
    updated_version=2,
    worker_aliases=_WORKER_ALIASES,
    historical_processlist_aliases=_HISTORICAL_PROCESSLIST_ALIASES,
    stale_worker_id=_STALE_WORKER_ID,
    non_blocking_abandoned_worker_ids=_NON_BLOCKING_ABANDONED_WORKER_IDS,
    delayed_checkpoint_worker_ids=_DELAYED_CHECKPOINT_WORKER_IDS,
)


_NEW_CASE = replace(
    _CASE,
    case_id="single_handoff_mvcc_review",
    case_no=1,
    evaluator=TidbHealthCheckLongTransactionMvccForSingleHandoffEvaluatorCase,
    title="A focused TiDB MVCC review for one stale worker handoff boundary.",
    reference_report={
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": ["ended only the pre-write abandoned session identified by its worker handoff and checkpoint"],
            "verification": ["current workers, one post-write retry, checkpoints, new versions, and business CRC remained protected"],
        },
        "summary": "The single handoff review correlated the worker checkpoint boundary with the live transaction TSO before one session-scoped repair.",
    },
    alert=(
        "例行 MVCC 健康复核：订单服务有一个 abandoned worker session 的 snapshot 早于交接写入边界。"
        "请关联当前 worker lease、handoff history、worker-specific checkpoint 和 live TxnStart，区分唯一 stale session、"
        "当前 worker 与 post-write retry。只结束该 session，保留其它连接、checkpoint 和已提交业务数据。"
    ),
    initial_state={
        "status": "serving",
        "snapshot_transactions": 5,
        "historical_processlist_connections": 0,
        "worker_session_history_rows": 5,
        "checkpoint_rows": 10,
        "new_versions": 12,
    },
    expected_target={
        "pre_write_abandoned_session": "gone",
        "current_worker_sessions": 3,
        "post_write_abandoned_sessions": 1,
        "historical_processlist_connections": 0,
        "checkpoint_rows": 10,
        "new_versions": 12,
        "business_integrity": "post-write row count and CRC unchanged",
    },
    background_workload=replace(_CASE.background_workload, worker_count=3, warmup_seconds=6),
    runtime=replace(_CASE.runtime, bootstrap_cache_enabled=False, sql_timeout_seconds=120),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.735294,
        reference_run_ids=(
            "tidb-reference-11__"
            "tidb_health_check_long_transaction_mvcc__"
            "single_handoff_mvcc_review__mock__r001",
        ),
    ),
    versioned_row_count=12,
    worker_aliases=tuple(f"worker-{index:02d}" for index in range(1, 4)),
    historical_processlist_aliases=(),
    stale_worker_id=3,
    non_blocking_abandoned_worker_ids=(2,),
    delayed_checkpoint_worker_ids=(),
)


class TidbHealthCheckLongTransactionMvccInjector(BaseFaultInjector):
    def __init__(self):
        self._snapshot_connections: list[tuple[str, object]] = []
        self._historical_connections: list[tuple[str, object]] = []
        self._target_session_id: int | None = None
        self._valid_session_ids: list[int] = []
        self._non_blocking_abandoned_session_ids: list[int] = []
        self._historical_session_ids: list[int] = []
        self._target_snapshot_tso: int | None = None
        self._write_boundary_tso: int | None = None
        self._pre_write_integrity: tuple[int, int, int] | None = None
        self._post_write_integrity: tuple[int, int, int] | None = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._create_tables(context.env)
        self._load_business_rows(context.env)
        self._start_runtime_fault(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._reset_persisted_state(context.env)
        self._start_runtime_fault(context.env)

    def prepare_observability(
        self,
        context: FaultLifecycleContext,
    ) -> Mapping[str, object]:
        self._configure(context.config, context.env)
        transaction_rows = self._read_transaction_rows(context.env)
        processlist_rows = self._read_processlist_rows(context.env)
        registry_rows = self._read_lease_registry(context.env)
        history_rows = self._read_lease_history(context.env)
        checkpoint_rows = self._read_checkpoints(context.env)

        expected_transaction_ids = set(self._known_runtime_session_ids())
        expected_process_ids = expected_transaction_ids | set(
            self._historical_session_ids
        )
        transaction_ids = {int(row[0]) for row in transaction_rows}
        process_ids = {int(row[0]) for row in processlist_rows}
        observed = {
            "transactions": len(transaction_rows),
            "processes": len(processlist_rows),
            "registry": len(registry_rows),
            "history": len(history_rows),
            "checkpoints": len(checkpoint_rows),
        }
        if (
            transaction_ids != expected_transaction_ids
            or process_ids != expected_process_ids
            or len(registry_rows) != len(self.worker_aliases)
            or len(history_rows) != self.history_row_count
            or len(checkpoint_rows) != self.checkpoint_row_count
        ):
            raise RuntimeError(
                "HC09 observability row contract mismatch: "
                f"expected_transaction_ids={sorted(expected_transaction_ids)}, "
                f"observed_transaction_ids={sorted(transaction_ids)}, "
                f"expected_process_ids={sorted(expected_process_ids)}, "
                f"observed_process_ids={sorted(process_ids)}, "
                f"raw_row_counts={observed!r}"
            )
        if self._post_write_integrity is None:
            raise RuntimeError("HC09 post-write integrity was not captured")
        return {
            "target_session_id": self._target_session_id,
            "valid_session_ids": list(self._valid_session_ids),
            "non_blocking_abandoned_session_ids": list(
                self._non_blocking_abandoned_session_ids
            ),
            "historical_session_ids": list(self._historical_session_ids),
            "target_snapshot_tso": self._target_snapshot_tso,
            "write_boundary_tso": self._write_boundary_tso,
            "post_write_integrity": list(self._post_write_integrity),
            "transaction_rows": transaction_rows,
            "processlist_rows": processlist_rows,
            "lease_registry_rows": registry_rows,
            "lease_history_rows": history_rows,
            "checkpoint_rows": checkpoint_rows,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime(context)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime(context)
        self._drop_tables()

    def _configure(self, config: Mapping[str, object], env: object) -> None:
        self.env = env
        self.database = validate_sql_identifier(str(config["database"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.audit_table = validate_sql_identifier(
            str(config["audit_table"]), "audit_table"
        )
        self.lease_table = validate_sql_identifier(
            str(config["lease_table"]), "lease_table"
        )
        self.history_table = validate_sql_identifier(
            str(config["history_table"]), "history_table"
        )
        self.checkpoint_table = validate_sql_identifier(
            str(config["checkpoint_table"]), "checkpoint_table"
        )
        self.row_count = int(config["row_count"])
        self.versioned_row_count = int(config["versioned_row_count"])
        self.updated_version = int(config["updated_version"])
        self.worker_aliases = tuple(str(value) for value in config["worker_aliases"])
        self.historical_processlist_aliases = tuple(
            str(value) for value in config["historical_processlist_aliases"]
        )
        self.stale_worker_id = int(config["stale_worker_id"])
        self.non_blocking_abandoned_worker_ids = tuple(
            int(value) for value in config["non_blocking_abandoned_worker_ids"]
        )
        self.delayed_checkpoint_worker_ids = tuple(
            int(value) for value in config["delayed_checkpoint_worker_ids"]
        )
        if self.stale_worker_id in self.non_blocking_abandoned_worker_ids:
            raise ValueError(
                "HC09 stale worker cannot also be a non-blocking abandoned worker: "
                f"stale_worker_id={self.stale_worker_id}, "
                f"non_blocking={self.non_blocking_abandoned_worker_ids!r}"
            )
        if len(set(self.worker_aliases)) != len(self.worker_aliases):
            raise ValueError(f"HC09 worker aliases must be unique: {self.worker_aliases!r}")
        if self.row_count < self.versioned_row_count or self.versioned_row_count <= 0:
            raise ValueError(
                "HC09 row contract is invalid: "
                f"row_count={self.row_count}, versioned_row_count={self.versioned_row_count}"
            )

    @property
    def qualified_table(self) -> str:
        return f"{self.database}.{self.table}"

    @property
    def qualified_audit_table(self) -> str:
        return f"{self.database}.{self.audit_table}"

    @property
    def qualified_lease_table(self) -> str:
        return f"{self.database}.{self.lease_table}"

    @property
    def qualified_history_table(self) -> str:
        return f"{self.database}.{self.history_table}"

    @property
    def qualified_checkpoint_table(self) -> str:
        return f"{self.database}.{self.checkpoint_table}"

    @property
    def history_row_count(self) -> int:
        return len(self.worker_aliases) + 1 + len(
            self.non_blocking_abandoned_worker_ids
        )

    @property
    def checkpoint_row_count(self) -> int:
        return (
            len(self.worker_aliases) * 3
            + 1
            + len(self.delayed_checkpoint_worker_ids)
        )

    @property
    def integrity_sql(self) -> str:
        return (
            f"SELECT COUNT(*), SUM(version = {self.updated_version}), "
            "BIT_XOR(CRC32(CONCAT_WS('#', order_id, customer_id, status, amount, "
            "version, updated_at, payload))) "
            f"FROM {self.qualified_table}"
        )

    def _create_tables(self, env: object) -> None:
        for table in (
            self.qualified_checkpoint_table,
            self.qualified_history_table,
            self.qualified_lease_table,
            self.qualified_audit_table,
            self.qualified_table,
        ):
            require_sql_success(
                env.execute_sql(f"DROP TABLE IF EXISTS {table}"),
                f"clear HC09 table {table}",
            )
        statements = (
            (
                self.qualified_table,
                "order_id BIGINT PRIMARY KEY, customer_id BIGINT NOT NULL, "
                "status VARCHAR(16) NOT NULL, amount DECIMAL(12,2) NOT NULL, "
                "version INT NOT NULL, updated_at DATETIME(6) NOT NULL, "
                "payload VARCHAR(128) NOT NULL, "
                "KEY idx_customer_status (customer_id, status), "
                "KEY idx_updated_at (updated_at)",
            ),
            (
                self.qualified_audit_table,
                "event_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, "
                "event_type VARCHAR(16) NOT NULL, created_at DATETIME(6) NOT NULL, "
                "KEY idx_audit_order (order_id), KEY idx_audit_type (event_type)",
            ),
            (
                self.qualified_lease_table,
                "worker_id INT PRIMARY KEY, worker_alias VARCHAR(64) NOT NULL, "
                "workload_class VARCHAR(32) NOT NULL, run_state VARCHAR(16) NOT NULL, "
                "lease_state VARCHAR(16) NOT NULL, heartbeat_at DATETIME(6) NOT NULL, "
                "lease_expires_at DATETIME(6) NOT NULL, session_id BIGINT NOT NULL",
            ),
            (
                self.qualified_history_table,
                "event_id BIGINT PRIMARY KEY, worker_id INT NOT NULL, "
                "worker_alias VARCHAR(64) NOT NULL, lease_generation INT NOT NULL, "
                "event_state VARCHAR(16) NOT NULL, observed_at DATETIME(6) NOT NULL, "
                "observed_session_id BIGINT NOT NULL, handoff_reason VARCHAR(64) NOT NULL, "
                "KEY idx_handoff_worker_time (worker_id, observed_at)",
            ),
            (
                self.qualified_checkpoint_table,
                "checkpoint_id BIGINT PRIMARY KEY, worker_id INT NOT NULL, "
                "checkpoint_at DATETIME(6) NOT NULL, checkpoint_state VARCHAR(16) NOT NULL, "
                "commit_tso DECIMAL(20,0) NOT NULL, batch_name VARCHAR(64) NOT NULL, "
                "checkpoint_note VARCHAR(96) NOT NULL, "
                "KEY idx_checkpoint_worker_time (worker_id, checkpoint_at)",
            ),
        )
        for table, columns in statements:
            require_sql_success(
                env.execute_sql(f"CREATE TABLE {table} ({columns})"),
                f"create HC09 table {table}",
            )

    def _business_values(self) -> tuple[list[str], list[str]]:
        statuses = ("PAID", "PACKED", "SHIPPED", "REFUND")
        orders = []
        audits = []
        for order_id in range(1, self.row_count + 1):
            customer_id = 10 + (order_id % 90)
            status = statuses[(order_id - 1) % len(statuses)]
            amount = f"{80 + (order_id % 70) + 0.25:.2f}"
            day = (order_id - 1) % 28 + 1
            updated_at = f"2026-07-{day:02d} 12:00:00.000000"
            orders.append(
                f"({order_id}, {customer_id}, {sql_literal(status)}, {amount}, 1, "
                f"{sql_literal(updated_at)}, {sql_literal(f'order-{order_id:04d}-v1')})"
            )
            event_type = ("created", "paid", "packed")[order_id % 3]
            audits.append(
                f"({order_id}, {order_id}, {sql_literal(event_type)}, "
                f"{sql_literal(updated_at)})"
            )
        return orders, audits

    def _load_business_rows(self, env: object) -> None:
        orders, audits = self._business_values()
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.qualified_table} "
                "(order_id, customer_id, status, amount, version, updated_at, payload) VALUES "
                + ",".join(orders)
            ),
            "load HC09 order rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.qualified_audit_table} "
                "(event_id, order_id, event_type, created_at) VALUES "
                + ",".join(audits)
            ),
            "load HC09 audit rows",
        )

    def _reset_persisted_state(self, env: object) -> None:
        for table in (
            self.qualified_checkpoint_table,
            self.qualified_history_table,
            self.qualified_lease_table,
            self.qualified_audit_table,
            self.qualified_table,
        ):
            require_sql_success(
                env.execute_sql(f"DELETE FROM {table}"),
                f"reset HC09 table {table}",
            )
        self._load_business_rows(env)

    def _connection(
        self,
        *,
        autocommit: bool = False,
        read_timeout: int = 35,
        write_timeout: int = 35,
    ):
        return pymysql.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            database=self.database,
            charset="utf8mb4",
            autocommit=autocommit,
            connect_timeout=5,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
        )

    def _read_current_tso(self) -> int:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("START TRANSACTION")
                cursor.execute("SELECT @@tidb_current_ts")
                row = cursor.fetchone()
            connection.rollback()
        finally:
            connection.close()
        tso = int(row[0])
        if tso <= 0:
            raise RuntimeError(f"HC09 expected a positive TiDB TSO, observed={tso}")
        return tso

    def _start_snapshot(
        self,
        alias: str,
        query: str,
    ) -> tuple[object, int, int]:
        connection = self._connection()
        with connection.cursor() as cursor:
            cursor.execute(f"SET SESSION tidb_session_alias = {sql_literal(alias)}")
            cursor.execute("START TRANSACTION WITH CONSISTENT SNAPSHOT")
            cursor.execute("SELECT @@tidb_current_ts")
            snapshot_tso = int(cursor.fetchone()[0])
            cursor.execute(query)
            cursor.fetchall()
        if snapshot_tso <= 0:
            connection.close()
            raise RuntimeError(
                f"HC09 snapshot TSO must be positive: alias={alias!r}, tso={snapshot_tso}"
            )
        return connection, int(connection.thread_id()), snapshot_tso

    def _start_runtime_fault(self, env: object) -> None:
        if self._snapshot_connections or self._historical_connections:
            raise RuntimeError("HC09 runtime connections already exist")
        self._pre_write_integrity = self._read_integrity(env)
        target_alias = self.worker_aliases[self.stale_worker_id - 1]
        target = self._start_snapshot(
            target_alias,
            f"SELECT order_id, version, amount FROM {self.qualified_table} "
            f"WHERE order_id BETWEEN 1 AND {self.versioned_row_count} ORDER BY order_id",
        )
        self._snapshot_connections.append((target_alias, target[0]))
        self._target_session_id = target[1]
        self._target_snapshot_tso = target[2]

        self._commit_new_versions()
        self._write_boundary_tso = self._read_current_tso()
        if self._target_snapshot_tso >= self._write_boundary_tso:
            raise RuntimeError(
                "HC09 target snapshot must precede the write boundary: "
                f"snapshot_tso={self._target_snapshot_tso}, "
                f"write_boundary_tso={self._write_boundary_tso}"
            )

        abandoned_by_worker = {}
        self._non_blocking_abandoned_session_ids = []
        for worker_id in self.non_blocking_abandoned_worker_ids:
            alias = self.worker_aliases[worker_id - 1]
            snapshot = self._start_snapshot(
                alias,
                f"SELECT customer_id, COUNT(*), SUM(amount) FROM {self.qualified_table} "
                f"WHERE customer_id BETWEEN {10 + worker_id} AND {35 + worker_id} "
                "GROUP BY customer_id",
            )
            if snapshot[2] <= self._write_boundary_tso:
                raise RuntimeError(
                    "HC09 non-blocking retry snapshot must follow the write boundary: "
                    f"worker_id={worker_id}, snapshot_tso={snapshot[2]}, "
                    f"write_boundary_tso={self._write_boundary_tso}"
                )
            self._snapshot_connections.append((alias, snapshot[0]))
            self._non_blocking_abandoned_session_ids.append(snapshot[1])
            abandoned_by_worker[worker_id] = snapshot[1]

        current_by_worker = {}
        self._valid_session_ids = []
        for worker_id, alias in enumerate(self.worker_aliases, start=1):
            snapshot = self._start_snapshot(
                alias,
                f"SELECT status, COUNT(*), SUM(amount) FROM {self.qualified_table} "
                f"WHERE order_id BETWEEN {worker_id} AND {worker_id + 60} GROUP BY status",
            )
            if snapshot[2] <= self._write_boundary_tso:
                raise RuntimeError(
                    "HC09 current worker snapshot must follow the write boundary: "
                    f"worker_id={worker_id}, snapshot_tso={snapshot[2]}, "
                    f"write_boundary_tso={self._write_boundary_tso}"
                )
            self._snapshot_connections.append((alias, snapshot[0]))
            self._valid_session_ids.append(snapshot[1])
            current_by_worker[worker_id] = snapshot[1]

        self._historical_session_ids = []
        for alias in self.historical_processlist_aliases:
            connection = self._connection()
            with connection.cursor() as cursor:
                cursor.execute(f"SET SESSION tidb_session_alias = {sql_literal(alias)}")
                cursor.execute("SELECT 1")
                cursor.fetchone()
            self._historical_connections.append((alias, connection))
            self._historical_session_ids.append(int(connection.thread_id()))

        post_runtime_tso = self._read_current_tso()
        self._write_runtime_rows(current_by_worker, abandoned_by_worker, post_runtime_tso)
        self._post_write_integrity = self._read_integrity(env)
        self._verify_runtime_state(env)

    def _commit_new_versions(self) -> None:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("START TRANSACTION")
                for order_id in range(1, self.versioned_row_count + 1):
                    cursor.execute(
                        f"UPDATE {self.qualified_table} "
                        "SET version = version + 1, amount = amount + 1.25, "
                        "updated_at = NOW(6), payload = CONCAT(payload, '-v2') "
                        f"WHERE order_id = {order_id}"
                    )
            connection.commit()
        finally:
            connection.close()

    def _write_runtime_rows(
        self,
        current_by_worker: Mapping[int, int],
        abandoned_by_worker: Mapping[int, int],
        post_runtime_tso: int,
    ) -> None:
        state_values = []
        history_values = []
        checkpoint_values = []
        checkpoint_id = 1
        event_id = 1
        historical_tso = self._target_snapshot_tso - 1
        for worker_id, alias in enumerate(self.worker_aliases, start=1):
            workload_class = ("orders", "inventory", "finance")[(worker_id - 1) % 3]
            state_values.append(
                f"({worker_id}, {sql_literal(alias)}, {sql_literal(workload_class)}, "
                "'RUNNING', 'VALID', '2026-08-07 11:30:00.000000', "
                f"'2026-08-07 12:00:00.000000', {current_by_worker[worker_id]})"
            )
            history_values.append(
                f"({event_id}, {worker_id}, {sql_literal(alias)}, 2, 'CURRENT', "
                f"'2026-08-07 11:30:00.000000', {current_by_worker[worker_id]}, "
                "'supervisor replacement active')"
            )
            event_id += 1
            for checkpoint_at, state, tso, batch, note in (
                (
                    "2026-08-07 09:00:00.000000",
                    "COMMITTED",
                    historical_tso,
                    "morning-carryover",
                    "prior settled batch",
                ),
                (
                    "2026-08-07 10:00:00.000000",
                    "COMMITTED",
                    self._write_boundary_tso,
                    "order-version-rollout",
                    "committed order version boundary",
                ),
                (
                    "2026-08-07 11:00:00.000000",
                    "COMMITTED",
                    post_runtime_tso,
                    "supervisor-settled",
                    "current generation heartbeat",
                ),
            ):
                checkpoint_values.append(
                    f"({checkpoint_id}, {worker_id}, {sql_literal(checkpoint_at)}, "
                    f"{sql_literal(state)}, {tso}, {sql_literal(batch)}, {sql_literal(note)})"
                )
                checkpoint_id += 1

        history_values.append(
            f"({event_id}, {self.stale_worker_id}, "
            f"{sql_literal(self.worker_aliases[self.stale_worker_id - 1])}, 1, "
            f"'ABANDONED', '2026-08-07 10:15:00.000000', {self._target_session_id}, "
            "'handoff acknowledgement missing')"
        )
        event_id += 1
        for worker_id in self.non_blocking_abandoned_worker_ids:
            history_values.append(
                f"({event_id}, {worker_id}, {sql_literal(self.worker_aliases[worker_id - 1])}, "
                f"1, 'ABANDONED', '2026-08-07 10:15:00.000000', "
                f"{abandoned_by_worker[worker_id]}, 'post-commit retry detached')"
            )
            event_id += 1

        for worker_id in (*self.delayed_checkpoint_worker_ids, self.stale_worker_id):
            checkpoint_values.append(
                f"({checkpoint_id}, {worker_id}, '2026-08-07 10:30:00.000000', "
                f"'REPLAYED', {historical_tso}, 'delayed-replay', "
                f"'late visibility for worker-{worker_id:02d}')"
            )
            checkpoint_id += 1

        statements = (
            (
                f"INSERT INTO {self.qualified_lease_table} "
                "(worker_id, worker_alias, workload_class, run_state, lease_state, "
                "heartbeat_at, lease_expires_at, session_id) VALUES "
                + ",".join(state_values),
                "write HC09 worker state",
            ),
            (
                f"INSERT INTO {self.qualified_history_table} "
                "(event_id, worker_id, worker_alias, lease_generation, event_state, "
                "observed_at, observed_session_id, handoff_reason) VALUES "
                + ",".join(history_values),
                "write HC09 worker history",
            ),
            (
                f"INSERT INTO {self.qualified_checkpoint_table} "
                "(checkpoint_id, worker_id, checkpoint_at, checkpoint_state, commit_tso, "
                "batch_name, checkpoint_note) VALUES "
                + ",".join(checkpoint_values),
                "write HC09 checkpoint history",
            ),
        )
        for statement, context in statements:
            require_sql_success(self.env.execute_sql(statement), context)

    def _known_runtime_session_ids(self) -> tuple[int, ...]:
        values = (
            [self._target_session_id]
            + self._valid_session_ids
            + self._non_blocking_abandoned_session_ids
        )
        if any(value is None for value in values):
            raise RuntimeError(f"HC09 runtime session IDs are incomplete: {values!r}")
        return tuple(int(value) for value in values)

    def _read_transaction_rows(self, env: object) -> list:
        ids = self._known_runtime_session_ids()
        payload = json_object(
            env.execute_sql(
                "SELECT SESSION_ID, START_TIME, STATE, USER, DB "
                "FROM INFORMATION_SCHEMA.CLUSTER_TIDB_TRX WHERE SESSION_ID IN ("
                + ",".join(str(value) for value in ids)
                + ") ORDER BY START_TIME, SESSION_ID"
            ),
            "read HC09 cluster transactions",
        )
        return payload["result"]

    def _read_processlist_rows(self, env: object) -> list:
        ids = self._known_runtime_session_ids() + tuple(self._historical_session_ids)
        payload = json_object(
            env.execute_sql(
                "SELECT ID, SESSION_ALIAS, TxnStart, COMMAND "
                "FROM INFORMATION_SCHEMA.CLUSTER_PROCESSLIST WHERE ID IN ("
                + ",".join(str(value) for value in ids)
                + ") ORDER BY ID"
            ),
            "read HC09 cluster processlist",
        )
        return payload["result"]

    def _read_lease_registry(self, env: object) -> list:
        return json_object(
            env.execute_sql(
                "SELECT worker_id, worker_alias, workload_class, run_state, lease_state, "
                "heartbeat_at, lease_expires_at, session_id "
                f"FROM {self.qualified_lease_table} ORDER BY worker_id"
            ),
            "read HC09 worker state",
        )["result"]

    def _read_lease_history(self, env: object) -> list:
        return json_object(
            env.execute_sql(
                "SELECT event_id, worker_id, worker_alias, lease_generation, event_state, "
                "observed_at, observed_session_id, handoff_reason "
                f"FROM {self.qualified_history_table} ORDER BY worker_id, event_id"
            ),
            "read HC09 worker history",
        )["result"]

    def _read_checkpoints(self, env: object) -> list:
        return json_object(
            env.execute_sql(
                "SELECT checkpoint_id, worker_id, checkpoint_at, checkpoint_state, "
                "commit_tso, batch_name, checkpoint_note "
                f"FROM {self.qualified_checkpoint_table} "
                "ORDER BY worker_id, checkpoint_at, checkpoint_id"
            ),
            "read HC09 checkpoint history",
        )["result"]

    def _read_integrity(self, env: object) -> tuple[int, int, int]:
        rows = json_object(
            env.execute_sql(self.integrity_sql),
            "read HC09 business integrity",
        )["result"]
        if len(rows) != 1 or len(rows[0]) != 3:
            raise RuntimeError(
                f"HC09 integrity result has unexpected shape: rows={rows!r}"
            )
        return int(rows[0][0]), int(rows[0][1]), int(rows[0][2])

    def _verify_runtime_state(self, env: object) -> None:
        if self._pre_write_integrity is None or self._post_write_integrity is None:
            raise RuntimeError("HC09 integrity snapshots are incomplete")
        if self._pre_write_integrity[0] != self.row_count:
            raise RuntimeError(
                "HC09 pre-write row count mismatch: "
                f"expected={self.row_count}, observed={self._pre_write_integrity!r}"
            )
        if self._post_write_integrity[:2] != (
            self.row_count,
            self.versioned_row_count,
        ):
            raise RuntimeError(
                "HC09 post-write integrity mismatch: "
                f"expected_rows={self.row_count}, "
                f"expected_versioned={self.versioned_row_count}, "
                f"observed={self._post_write_integrity!r}"
            )
        transaction_ids = {int(row[0]) for row in self._read_transaction_rows(env)}
        expected = set(self._known_runtime_session_ids())
        if transaction_ids != expected:
            raise RuntimeError(
                "HC09 transaction session set mismatch: "
                f"expected={sorted(expected)}, observed={sorted(transaction_ids)}"
            )

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        steps = [
            (f"close HC09 snapshot session {alias}", connection.close)
            for alias, connection in reversed(self._snapshot_connections)
        ]
        steps.extend(
            (
                f"close HC09 historical connection {alias}",
                connection.close,
            )
            for alias, connection in reversed(self._historical_connections)
        )
        run_cleanup_steps(
            f"HC09 runtime cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._snapshot_connections = []
        self._historical_connections = []
        self._target_session_id = None
        self._valid_session_ids = []
        self._non_blocking_abandoned_session_ids = []
        self._historical_session_ids = []

    def _drop_tables(self) -> None:
        connection = self._connection(
            autocommit=True,
            read_timeout=180,
            write_timeout=180,
        )
        try:
            with connection.cursor() as cursor:
                for table in (
                    self.qualified_checkpoint_table,
                    self.qualified_history_table,
                    self.qualified_lease_table,
                    self.qualified_audit_table,
                    self.qualified_table,
                ):
                    try:
                        cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    except pymysql.MySQLError as exc:
                        raise RuntimeError(
                            f"HC09 recovery failed while dropping table {table!r}: {exc}"
                        ) from exc
        finally:
            connection.close()


class TidbHealthCheckLongTransactionMvccScenario(TiDBScenario):
    scenario_id = "tidb_health_check_long_transaction_mvcc"
    description = (
        "Routine TiDB review of retained MVCC versions across worker handoffs "
        "and checkpoint windows."
    )
    cases = (_CASE, _NEW_CASE)

    def build_fault_plan(
        self,
        case: TidbHealthCheckLongTransactionMvccCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbHealthCheckLongTransactionMvccInjector,
                config={
                    "database": case.database,
                    "table": case.table,
                    "audit_table": case.audit_table,
                    "lease_table": case.lease_table,
                    "history_table": case.history_table,
                    "checkpoint_table": case.checkpoint_table,
                    "row_count": case.row_count,
                    "versioned_row_count": case.versioned_row_count,
                    "updated_version": case.updated_version,
                    "worker_aliases": case.worker_aliases,
                    "historical_processlist_aliases": (
                        case.historical_processlist_aliases
                    ),
                    "stale_worker_id": case.stale_worker_id,
                    "non_blocking_abandoned_worker_ids": (
                        case.non_blocking_abandoned_worker_ids
                    ),
                    "delayed_checkpoint_worker_ids": (
                        case.delayed_checkpoint_worker_ids
                    ),
                },
            ),
        )
