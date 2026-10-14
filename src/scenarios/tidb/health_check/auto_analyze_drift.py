import time

from collections.abc import Mapping

from src.database.sql import execute_result_rows, require_success_payload

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    require_sql_success,
    validate_sql_identifier,
)

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.health_check.auto_analyze_drift import (
    TidbHealthCheckAutoAnalyzeDriftEvaluatorCase,
    TidbHealthCheckAutoAnalyzeTargetScopeEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckAutoAnalyzeDriftCase(TiDBScenarioCase):
    db: str
    target_table: str
    payments_table: str
    inventory_table: str
    events_table: str
    report_table: str
    seed_rows: int
    drift_rows: int
    protected_drift_rows: int
    expected_row_count: int
    expected_order_id_sum: int
    expected_amount_cents_sum: int
    expected_payment_count: int
    expected_payment_id_sum: int
    expected_payment_amount_cents_sum: int
    drift_auto_analyze: str
    expected_auto_analyze: str
    expected_stmt_summary: str
    focused_fixture: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckAutoAnalyzeDriftForRoutineReviewScenarioCase(
    TidbHealthCheckAutoAnalyzeDriftCase
):
    pass


HC07_DB = "benchops"
HC07_TARGET_TABLE = "hc07_orders"
HC07_PAYMENTS_TABLE = "hc07_payments"
HC07_INVENTORY_TABLE = "hc07_inventory"
HC07_EVENTS_TABLE = "hc07_order_events"
HC07_REPORT_TABLE = "hc07_review_context"
HC07_SEED_ROWS = 2400
HC07_DRIFT_ROWS = 600
HC07_PROTECTED_DRIFT_ROWS = 600
HC07_TOTAL_ROWS = HC07_SEED_ROWS + HC07_DRIFT_ROWS
HC07_TOTAL_PAYMENTS = HC07_SEED_ROWS + HC07_PROTECTED_DRIFT_ROWS
HC07_ORDER_ID_SUM = HC07_TOTAL_ROWS * (HC07_TOTAL_ROWS + 1) // 2
HC07_AMOUNT_CENTS_SUM = sum(
    100 + (order_id % 97) * 10 for order_id in range(1, HC07_TOTAL_ROWS + 1)
)
HC07_PAYMENT_ID_SUM = HC07_TOTAL_PAYMENTS * (HC07_TOTAL_PAYMENTS + 1) // 2
HC07_PAYMENT_AMOUNT_CENTS_SUM = sum(
    100 + (payment_id % 97) * 10
    for payment_id in range(1, HC07_TOTAL_PAYMENTS + 1)
)


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="hc07_checkout_order_lookup",
            sql=(
                f"SELECT order_id, customer_id, status, amount_cents "
                f"FROM {HC07_DB}.{HC07_TARGET_TABLE} "
                "WHERE order_id IN (17, 271, 983, 1777)"
            ),
            qps=0.8,
            tier="OLTP_READ",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="hc07_regional_order_rollup",
            sql=(
                f"SELECT region, status, COUNT(*), SUM(amount_cents) "
                f"FROM {HC07_DB}.{HC07_TARGET_TABLE} "
                "WHERE created_at >= '2026-07-25' "
                "GROUP BY region, status ORDER BY SUM(amount_cents) DESC LIMIT 20"
            ),
            qps=0.3,
            tier="REPORTING",
            application_name="merchant-rollup",
        ),
        WorkloadProfile(
            name="hc07_risk_payment_join",
            sql=(
                f"SELECT o.region, COUNT(*), SUM(p.amount_cents) "
                f"FROM {HC07_DB}.{HC07_TARGET_TABLE} o "
                f"JOIN {HC07_DB}.{HC07_PAYMENTS_TABLE} p ON p.order_id = o.order_id "
                "WHERE o.status IN ('PENDING', 'REVIEW') GROUP BY o.region"
            ),
            qps=0.25,
            tier="AUDIT",
            application_name="risk-audit",
        ),
        WorkloadProfile(
            name="hc07_inventory_reservation_probe",
            sql=(
                f"SELECT sku_id, available, reserved "
                f"FROM {HC07_DB}.{HC07_INVENTORY_TABLE} "
                "WHERE sku_id IN (7, 19, 31, 47) ORDER BY sku_id"
            ),
            qps=0.65,
            tier="OLTP_READ",
            application_name="inventory-worker",
        ),
        WorkloadProfile(
            name="hc07_order_event_reconciliation",
            sql=(
                f"SELECT event_type, COUNT(*), MAX(created_at) "
                f"FROM {HC07_DB}.{HC07_EVENTS_TABLE} "
                "GROUP BY event_type ORDER BY event_type"
            ),
            qps=0.35,
            tier="RECONCILIATION",
            application_name="settlement-reconciliation",
        ),
        WorkloadProfile(
            name="hc07_table_inventory_probe",
            sql=(
                "SELECT TABLE_NAME, TABLE_ROWS, UPDATE_TIME "
                "FROM INFORMATION_SCHEMA.TABLES "
                f"WHERE TABLE_SCHEMA = '{HC07_DB}' "
                "ORDER BY TABLE_NAME"
            ),
            qps=0.25,
            tier="MONITORING",
            application_name="ops-health-probe",
        ),
        WorkloadProfile(
            name="hc07_index_cardinality_review",
            sql=(
                "SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME, CARDINALITY "
                "FROM INFORMATION_SCHEMA.STATISTICS "
                f"WHERE TABLE_SCHEMA = '{HC07_DB}' "
                "ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX"
            ),
            qps=0.18,
            tier="MONITORING",
            application_name="query-review-console",
        ),
        WorkloadProfile(
            name="hc07_recent_order_sla_probe",
            sql=(
                f"SELECT status, COUNT(*), AVG(amount_cents) "
                f"FROM {HC07_DB}.{HC07_TARGET_TABLE} "
                "WHERE created_at >= '2026-07-31' GROUP BY status ORDER BY status"
            ),
            qps=0.4,
            tier="BUSINESS_SLO",
            application_name="regional-order-sla",
        ),
        WorkloadProfile(
            name="hc07_statement_summary_refresh",
            sql=(
                "SELECT DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY "
                "FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY "
                "ORDER BY SUM_LATENCY DESC LIMIT 20"
            ),
            qps=0.2,
            tier="MONITORING",
            application_name="topsql-refresh",
        ),
        WorkloadProfile(
            name="hc07_maintenance_handoff_review",
            sql=(
                "SELECT object_name, maintenance_kind, handoff_state, expected_stats_mode "
                f"FROM {HC07_DB}.{HC07_REPORT_TABLE} ORDER BY object_name"
            ),
            qps=0.15,
            tier="MONITORING",
            application_name="configuration-audit",
        ),
    ),
    worker_count=6,
    seed=0xAC07,
    start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
    warmup_seconds=15,
)


_CASE = TidbHealthCheckAutoAnalyzeDriftForRoutineReviewScenarioCase(
    case_id="auto_analyze_configuration_drift",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "restored automatic statistics maintenance and released only the completed order maintenance lock"
            ],
            "verification": [
                "order statistics are current while the active payment canary remains pinned and business data is unchanged"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbHealthCheckAutoAnalyzeDriftEvaluatorCase,
    title=(
        "Routine TiDB health check after an overnight statistics-maintenance handoff."
    ),
    alert=(
        "[Routine weekly health review] The commerce cluster is reachable and checkout, "
        "payment, inventory, settlement, reporting, and audit queries are all active. The "
        "overnight maintenance handoff still needs to be reconciled against its recorded "
        "operating policy. Complete the ordinary database health check, repair only the "
        "actionable maintenance drift, and preserve controls that still belong to an active "
        "change window. Keep business rows unchanged; do not restart a healthy component or "
        "make availability look better by dropping data."
    ),
    initial_state={
        "status": "available_with_routine_review_open",
        "business_window": "checkout/inventory/settlement/reporting/audit",
        "maintenance_handoff": "overnight statistics-maintenance handoff awaiting review",
    },
    expected_target={
        "status": "routine_review_closed",
        "tidb_enable_auto_analyze": "ON",
        "target_stats_healthy": 100,
        "completed_maintenance_lock": "released",
        "active_canary_lock": "preserved",
        "business_rows_unchanged": True,
    },
    background_workload=_BACKGROUND_WORKLOAD,
    # HC07 does not test quorum or replica recovery. A regular runtime also keeps each
    # run isolated from the shared image-group cold-start path.
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=120,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.739159,
        reference_run_ids=(
            "reference-89__"
            "tidb_health_check_auto_analyze_drift__auto_analyze_configuration_drift__mock__r001",
        ),
    ),
    db=HC07_DB,
    target_table=HC07_TARGET_TABLE,
    payments_table=HC07_PAYMENTS_TABLE,
    inventory_table=HC07_INVENTORY_TABLE,
    events_table=HC07_EVENTS_TABLE,
    report_table=HC07_REPORT_TABLE,
    seed_rows=HC07_SEED_ROWS,
    drift_rows=HC07_DRIFT_ROWS,
    protected_drift_rows=HC07_PROTECTED_DRIFT_ROWS,
    expected_row_count=HC07_TOTAL_ROWS,
    expected_order_id_sum=HC07_ORDER_ID_SUM,
    expected_amount_cents_sum=HC07_AMOUNT_CENTS_SUM,
    expected_payment_count=HC07_TOTAL_PAYMENTS,
    expected_payment_id_sum=HC07_PAYMENT_ID_SUM,
    expected_payment_amount_cents_sum=HC07_PAYMENT_AMOUNT_CENTS_SUM,
    drift_auto_analyze="OFF",
    expected_auto_analyze="ON",
    expected_stmt_summary="ON",
)


_NEW_CASE = replace(
    _CASE,
    case_id="auto_analyze_target_scope_review",
    case_no=1,
    evaluator=TidbHealthCheckAutoAnalyzeTargetScopeEvaluatorCase,
    title="A scoped TiDB statistics-maintenance review for one completed target and one protected payment canary.",
    reference_report={
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": ["restored global automatic statistics maintenance and refreshed only the completed target"],
            "verification": ["the payment canary remained locked with its statistics unchanged and both business checksums matched"],
        },
        "summary": "The target statistics scope was reconciled without widening the active payment canary protection.",
    },
    alert=(
        "例行统计维护复核：小批次订单维护已经完成，但全局 auto analyze 开关仍处于维护窗口状态。"
        "请确认目标表的统计信息需要刷新，同时保留仍属于 active payment canary 的 lock 和统计快照。"
        "恢复全局策略，只解锁并分析已完成目标，保持业务行、组件和其它表不变。"
    ),
    expected_target={
        "status": "routine_review_closed",
        "tidb_enable_auto_analyze": "ON",
        "target_stats_healthy": 100,
        "completed_maintenance_lock": "released",
        "active_canary_lock": "preserved",
        "business_rows_unchanged": True,
    },
    background_workload=replace(
        _CASE.background_workload,
        profiles=tuple(
            profile
            for profile in _CASE.background_workload.profiles
            if profile.name
            not in {"hc07_inventory_reservation_probe", "hc07_order_event_reconciliation"}
        ),
        worker_count=5,
        warmup_seconds=12,
    ),
    runtime=replace(_CASE.runtime, bootstrap_cache_enabled=False, sql_timeout_seconds=120),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.473684,
        reference_run_ids=(
            "tidb-reference-10__"
            "tidb_health_check_auto_analyze_drift__"
            "auto_analyze_target_scope_review__mock__r001",
        ),
    ),
    drift_rows=300,
    protected_drift_rows=300,
    expected_row_count=2700,
    expected_order_id_sum=3646350,
    expected_amount_cents_sum=1560330,
    expected_payment_count=2700,
    expected_payment_id_sum=3646350,
    expected_payment_amount_cents_sum=1560330,
    focused_fixture=True,
)


class TidbHealthCheckAutoAnalyzeDriftInjector(BaseFaultInjector):
    """Create real business tables, then disable automatic statistics maintenance."""

    def __init__(self) -> None:
        self._configured = False
        self._original_auto_analyze: str | None = None
        self._original_stmt_summary: str | None = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        env = context.env
        with env.metrics_hidden():
            self._install_fixture(env, context.run_id)

    def _install_fixture(self, env, run_id: str) -> None:
        self._original_auto_analyze = self._read_auto_analyze(env)
        if self._original_auto_analyze.casefold() != self.expected_auto_analyze.casefold():
            raise RuntimeError(
                "HC07 requires the fresh-cluster automatic statistics baseline to be ON: "
                f"observed={self._original_auto_analyze!r}, expected={self.expected_auto_analyze!r}, "
                f"run_id={run_id!r}"
            )
        self._original_stmt_summary = self._read_stmt_summary(env)
        if self._original_stmt_summary.casefold() != self.expected_stmt_summary.casefold():
            raise RuntimeError(
                "HC07 requires statement summary collection to be ON before setup: "
                f"observed={self._original_stmt_summary!r}, "
                f"expected={self.expected_stmt_summary!r}, run_id={run_id!r}"
            )
        require_sql_success(
            env.execute_sql("SET GLOBAL tidb_enable_stmt_summary = OFF"),
            "pause statement summary collection during HC07 fixture setup",
        )
        require_sql_success(
            env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"),
            "clear HC07 database",
        )
        require_sql_success(
            env.execute_sql(f"CREATE DATABASE {self.db}"),
            "create HC07 database",
        )
        self._configured = True
        self._create_schema(env)
        self._insert_orders(env, 1, self.seed_rows)
        self._insert_payments(env, 1, self.seed_rows)
        if not self.focused_fixture:
            self._insert_inventory(env)
            self._insert_events(env)
        require_sql_success(
            env.execute_sql(
                f"ANALYZE TABLE {self.db}.{self.target_table}, "
                f"{self.db}.{self.payments_table}"
            ),
            "analyze HC07 maintenance tables before drift",
        )
        self._wait_for_healthy_statistics(env, self.target_table)
        self._wait_for_healthy_statistics(env, self.payments_table)
        require_sql_success(
            env.execute_sql(
                f"LOCK STATS {self.db}.{self.target_table}, "
                f"{self.db}.{self.payments_table}"
            ),
            "lock HC07 statistics during the maintenance window",
        )
        require_sql_success(
            env.execute_sql(
                f"SET GLOBAL tidb_enable_auto_analyze = {self.drift_auto_analyze}"
            ),
            "disable HC07 automatic statistics maintenance during the maintenance window",
        )
        self._insert_orders(env, self.seed_rows + 1, self.expected_row_count)
        self._insert_payments(
            env,
            self.seed_rows + 1,
            self.expected_payment_count,
        )
        self._wait_for_statistics_lag(env, self.target_table, self.expected_row_count)
        self._wait_for_statistics_lag(
            env,
            self.payments_table,
            self.expected_payment_count,
        )
        self._assert_checksums(env)
        require_sql_success(
            env.execute_sql("SET GLOBAL tidb_enable_stmt_summary = ON"),
            "resume statement summary collection for HC07 observability",
        )

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        # Fault snapshots are restored in a fresh injector process.  The fixture
        # and its expected baseline are persisted in TiDB, not in this object.
        self._configured = True
        self._original_auto_analyze = self.expected_auto_analyze
        self._original_stmt_summary = self.expected_stmt_summary
        current = self._read_auto_analyze(context.env)
        health = {
            self.target_table: self._stats_health(context.env, self.target_table),
            self.payments_table: self._stats_health(context.env, self.payments_table),
        }
        stats_meta = {
            self.target_table: self._stats_signature(context.env, self.target_table),
            self.payments_table: self._stats_signature(context.env, self.payments_table),
        }
        locked_tables = self._locked_tables(context.env)
        if current.casefold() != self.drift_auto_analyze.casefold():
            raise RuntimeError(
                "HC07 activation found an unexpected automatic statistics setting: "
                f"observed={current!r}, expected={self.drift_auto_analyze!r}"
            )
        expected_row_counts = {
            self.target_table: self.seed_rows,
            self.payments_table: self.seed_rows,
        }
        if any(
            stats_meta[table]["row_count"] != expected_row_count
            for table, expected_row_count in expected_row_counts.items()
        ):
            raise RuntimeError(
                "HC07 activation lost the intended locked statistics lag: "
                f"database={self.db!r}, health={health!r}, stats_meta={stats_meta!r}"
            )
        expected_locked = {self.target_table, self.payments_table}
        if locked_tables != expected_locked:
            raise RuntimeError(
                "HC07 activation found an unexpected statistics-lock scope: "
                f"expected={sorted(expected_locked)!r}, actual={sorted(locked_tables)!r}"
            )
        self._assert_checksums(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        if not self._configured or self._original_auto_analyze is None:
            raise RuntimeError(
                "HC07 observability requested before installation: "
                f"configured={self._configured}, run_id={context.run_id!r}"
            )
        health = {
            self.target_table: self._stats_health(context.env, self.target_table),
            self.payments_table: self._stats_health(context.env, self.payments_table),
        }
        stats_meta = {
            self.target_table: self._stats_signature(context.env, self.target_table),
            self.payments_table: self._stats_signature(context.env, self.payments_table),
        }
        current = self._read_auto_analyze(context.env)
        checksums = self._checksums(context.env)
        return {
            "hc07_original_auto_analyze": self._original_auto_analyze,
            "hc07_observed_auto_analyze": current,
            "hc07_stats_health": health,
            "hc07_stats_meta": stats_meta,
            "hc07_locked_tables": sorted(self._locked_tables(context.env)),
            "hc07_business_checksums": {
                table: list(checksum) for table, checksum in checksums.items()
            },
            "hc07_protected_stats_signature": self._stats_signature(
                context.env,
                self.payments_table,
            ),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        if not self._configured:
            raise RuntimeError(
                "HC07 quiesce requested before installation: "
                f"run_id={context.run_id!r}"
            )

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        if self._original_auto_analyze is None or self._original_stmt_summary is None:
            raise RuntimeError(
                "HC07 recovery has no captured global settings: "
                f"auto_analyze={self._original_auto_analyze!r}, "
                f"stmt_summary={self._original_stmt_summary!r}, run_id={context.run_id!r}"
            )
        require_sql_success(
            context.env.execute_sql(
                f"SET GLOBAL tidb_enable_auto_analyze = {self._original_auto_analyze}"
            ),
            "restore HC07 automatic statistics setting",
        )
        require_sql_success(
            context.env.execute_sql(
                f"UNLOCK STATS {self.db}.{self.target_table}, "
                f"{self.db}.{self.payments_table}"
            ),
            "release HC07 injector-owned statistics locks",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"),
            "remove HC07 database fixture",
        )
        require_sql_success(
            context.env.execute_sql(
                f"SET GLOBAL tidb_enable_stmt_summary = {self._original_stmt_summary}"
            ),
            "restore HC07 statement summary setting",
        )
        self._configured = False
        self._original_auto_analyze = None
        self._original_stmt_summary = None

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.target_table = validate_sql_identifier(str(config["target_table"]), "target_table")
        self.payments_table = validate_sql_identifier(str(config["payments_table"]), "payments_table")
        self.inventory_table = validate_sql_identifier(str(config["inventory_table"]), "inventory_table")
        self.events_table = validate_sql_identifier(str(config["events_table"]), "events_table")
        self.report_table = validate_sql_identifier(str(config["report_table"]), "report_table")
        self.seed_rows = int(config["seed_rows"])
        self.drift_rows = int(config["drift_rows"])
        self.protected_drift_rows = int(config["protected_drift_rows"])
        self.expected_row_count = int(config["expected_row_count"])
        self.expected_order_id_sum = int(config["expected_order_id_sum"])
        self.expected_amount_cents_sum = int(config["expected_amount_cents_sum"])
        self.expected_payment_count = int(config["expected_payment_count"])
        self.expected_payment_id_sum = int(config["expected_payment_id_sum"])
        self.expected_payment_amount_cents_sum = int(
            config["expected_payment_amount_cents_sum"]
        )
        self.drift_auto_analyze = str(config["drift_auto_analyze"])
        self.expected_auto_analyze = str(config["expected_auto_analyze"])
        self.expected_stmt_summary = str(config["expected_stmt_summary"])
        self.focused_fixture = bool(config["focused_fixture"])
        if self.expected_row_count != self.seed_rows + self.drift_rows:
            raise ValueError(
                "HC07 row contract is inconsistent: "
                f"seed_rows={self.seed_rows}, drift_rows={self.drift_rows}, "
                f"expected_row_count={self.expected_row_count}"
            )
        if self.expected_payment_count != self.seed_rows + self.protected_drift_rows:
            raise ValueError(
                "HC07 protected-table row contract is inconsistent: "
                f"seed_rows={self.seed_rows}, protected_drift_rows={self.protected_drift_rows}, "
                f"expected_payment_count={self.expected_payment_count}"
            )

    def _create_schema(self, env) -> None:
        statements = [
            f"CREATE TABLE {self.db}.{self.target_table} ("
            "order_id BIGINT PRIMARY KEY, customer_id BIGINT NOT NULL, "
            "status VARCHAR(16) NOT NULL, amount_cents BIGINT NOT NULL, "
            "region VARCHAR(16) NOT NULL, created_at DATETIME NOT NULL, "
            "payload VARCHAR(64) NOT NULL, "
            "KEY idx_customer_status (customer_id, status), KEY idx_created (created_at)"
            ")",
            f"CREATE TABLE {self.db}.{self.payments_table} ("
            "payment_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, "
            "payment_status VARCHAR(16) NOT NULL, amount_cents BIGINT NOT NULL, "
            "paid_at DATETIME NOT NULL, KEY idx_order (order_id)"
            ")",
        ]
        if not self.focused_fixture:
            statements.extend((
                f"CREATE TABLE {self.db}.{self.inventory_table} ("
                "sku_id BIGINT PRIMARY KEY, available INT NOT NULL, reserved INT NOT NULL, "
                "updated_at DATETIME NOT NULL"
                ")",
                f"CREATE TABLE {self.db}.{self.events_table} ("
                "event_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, "
                "event_type VARCHAR(20) NOT NULL, created_at DATETIME NOT NULL, "
                "KEY idx_event_order (order_id, created_at)"
                ")",
            ))
        statements.extend((
            f"CREATE TABLE {self.db}.{self.report_table} ("
            "object_name VARCHAR(64) PRIMARY KEY, maintenance_kind VARCHAR(32) NOT NULL, "
            "handoff_state VARCHAR(32) NOT NULL, expected_stats_mode VARCHAR(16) NOT NULL"
            ")",
            f"INSERT INTO {self.db}.{self.report_table} VALUES "
            "('hc07_orders', 'bulk_load', 'completed', 'AUTO'),"
            "('hc07_payments', 'plan_canary', 'active', 'PINNED')",
        ))
        if not self.focused_fixture:
            statements.append(
                f"INSERT INTO {self.db}.{self.report_table} VALUES "
                "('hc07_inventory', 'routine_refresh', 'completed', 'AUTO'),"
                "('hc07_order_events', 'retention_review', 'scheduled', 'AUTO')"
            )
        for statement in statements:
            require_sql_success(env.execute_sql(statement), f"create HC07 schema statement: {statement}")

    def _insert_orders(self, env, first_order_id: int, last_order_id: int) -> None:
        batch_size = 200
        for batch_start in range(first_order_id, last_order_id + 1, batch_size):
            batch_end = min(last_order_id, batch_start + batch_size - 1)
            values = ",".join(
                (
                    f"({order_id}, {order_id % 240 + 1}, "
                    f"'{('PAID', 'PENDING', 'REVIEW')[order_id % 3]}', "
                    f"{100 + (order_id % 97) * 10}, "
                    f"'{('east', 'west', 'north', 'south')[order_id % 4]}', "
                    f"'2026-07-{order_id % 28 + 1:02d} 12:00:00', "
                    f"'order_payload_{order_id % 17}')"
                )
                for order_id in range(batch_start, batch_end + 1)
            )
            require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {self.db}.{self.target_table} "
                    "(order_id, customer_id, status, amount_cents, region, created_at, payload) "
                    f"VALUES {values}"
                ),
                f"insert HC07 orders {batch_start}-{batch_end}",
            )

    def _insert_payments(self, env, first_payment_id: int, last_payment_id: int) -> None:
        payment_rows = [
            f"({payment_id}, {payment_id}, 'captured', "
            f"{100 + (payment_id % 97) * 10}, '2026-07-15 12:00:00')"
            for payment_id in range(first_payment_id, last_payment_id + 1)
        ]
        for batch_start in range(0, len(payment_rows), 200):
            batch = payment_rows[batch_start:batch_start + 200]
            require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {self.db}.{self.payments_table} "
                    "(payment_id, order_id, payment_status, amount_cents, paid_at) VALUES "
                    + ",".join(batch)
                ),
                "insert HC07 payments "
                f"{first_payment_id + batch_start}-"
                f"{first_payment_id + batch_start + len(batch) - 1}",
            )

    def _insert_inventory(self, env) -> None:
        values = ",".join(
            f"({sku_id}, {1000 - sku_id}, {sku_id % 19}, '2026-08-01 00:00:00')"
            for sku_id in range(1, 121)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.inventory_table} "
                "(sku_id, available, reserved, updated_at) VALUES "
                f"{values}"
            ),
            "insert HC07 inventory",
        )

    def _insert_events(self, env) -> None:
        values = ",".join(
            f"({event_id}, {event_id % self.seed_rows + 1}, "
            f"'{('payment', 'shipment', 'review')[event_id % 3]}', '2026-08-01 00:00:00')"
            for event_id in range(1, 361)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.events_table} "
                "(event_id, order_id, event_type, created_at) VALUES "
                f"{values}"
            ),
            "insert HC07 order events",
        )

    def _read_auto_analyze(self, env) -> str:
        rows = execute_result_rows(
            env.execute_sql,
            "SHOW GLOBAL VARIABLES LIKE 'tidb_enable_auto_analyze'",
            "HC07 automatic statistics setting",
        )
        if len(rows) != 1 or len(rows[0]) < 2:
            raise RuntimeError(
                "HC07 automatic statistics query returned an unexpected shape: "
                f"rows={rows!r}"
            )
        return str(rows[0][1])

    def _read_stmt_summary(self, env) -> str:
        rows = execute_result_rows(
            env.execute_sql,
            "SHOW GLOBAL VARIABLES LIKE 'tidb_enable_stmt_summary'",
            "HC07 statement summary setting",
        )
        if len(rows) != 1 or len(rows[0]) < 2:
            raise RuntimeError(
                "HC07 statement summary query returned an unexpected shape: "
                f"rows={rows!r}"
            )
        return str(rows[0][1])

    def _stats_health(self, env, table: str) -> int:
        rows = execute_result_rows(
            env.execute_sql,
            "SHOW STATS_HEALTHY "
            f"WHERE Db_name = '{self.db}' AND Table_name = '{table}'",
            f"HC07 statistics health for {table}",
        )
        if len(rows) != 1 or len(rows[0]) < 4:
            raise RuntimeError(
                "HC07 statistics query returned an unexpected shape: "
                f"database={self.db!r}, table={table!r}, rows={rows!r}"
            )
        return int(rows[0][3])

    def _wait_for_healthy_statistics(self, env, table: str) -> None:
        deadline = time.monotonic() + 120
        observed = None
        while time.monotonic() < deadline:
            observed = self._stats_health(env, table)
            if observed == 100:
                return
            time.sleep(2)
        raise RuntimeError(
            "HC07 ANALYZE did not restore target statistics health before the drift window: "
            f"database={self.db!r}, table={table!r}, healthy={observed!r}"
        )

    def _wait_for_statistics_lag(
        self,
        env,
        table: str,
        expected_actual_rows: int,
    ) -> None:
        deadline = time.monotonic() + 120
        observed = None
        while time.monotonic() < deadline:
            actual = self._checksum(
                env,
                table,
                "order_id" if table == self.target_table else "payment_id",
            )[0]
            observed = self._stats_signature(env, table)
            if actual == expected_actual_rows and observed["row_count"] < actual:
                return
            time.sleep(2)
        raise RuntimeError(
            "HC07 locked statistics did not lag the appended rows before the drift window: "
            f"database={self.db!r}, table={table!r}, expected_actual_rows={expected_actual_rows}, "
            f"observed_stats_meta={observed!r}"
        )

    def _checksum(
        self,
        env,
        table: str,
        id_column: str,
    ) -> tuple[int, int, int]:
        rows = execute_result_rows(
            env.execute_sql,
            f"SELECT COUNT(*), COALESCE(SUM({id_column}), 0), "
            f"COALESCE(SUM(amount_cents), 0) FROM {self.db}.{table}",
            f"HC07 business checksum for {table}",
        )
        if len(rows) != 1 or len(rows[0]) != 3:
            raise RuntimeError(
                "HC07 checksum query returned an unexpected shape: "
                f"table={table!r}, rows={rows!r}"
            )
        return tuple(int(value) for value in rows[0])

    def _checksums(self, env) -> dict[str, tuple[int, int, int]]:
        return {
            self.target_table: self._checksum(env, self.target_table, "order_id"),
            self.payments_table: self._checksum(env, self.payments_table, "payment_id"),
        }

    def _assert_checksums(self, env) -> None:
        actual = self._checksums(env)
        expected = {
            self.target_table: (
                self.expected_row_count,
                self.expected_order_id_sum,
                self.expected_amount_cents_sum,
            ),
            self.payments_table: (
                self.expected_payment_count,
                self.expected_payment_id_sum,
                self.expected_payment_amount_cents_sum,
            ),
        }
        if actual != expected:
            raise RuntimeError(
                "HC07 business fixture checksum changed during injection: "
                f"expected={expected}, actual={actual}"
            )

    def _locked_tables(self, env) -> set[str]:
        rows = execute_result_rows(
            env.execute_sql,
            "SHOW STATS_LOCKED",
            "HC07 statistics-lock inventory",
        )
        return {
            str(row[1])
            for row in rows
            if len(row) >= 4
            and str(row[0]).casefold() == self.db.casefold()
            and str(row[3]).casefold() == "locked"
        }

    def _stats_signature(self, env, table: str) -> dict[str, object]:
        payload = require_success_payload(
            env.execute_sql(
                "SHOW STATS_META "
                f"WHERE Db_name = '{self.db}' AND Table_name = '{table}'"
            ),
            f"HC07 statistics metadata for {table}",
        )
        columns = [str(column).casefold() for column in payload["columns"]]
        rows = [dict(zip(columns, row)) for row in payload["result"]]
        if len(rows) != 1:
            raise RuntimeError(
                "HC07 statistics metadata expected one row: "
                f"database={self.db!r}, table={table!r}, rows={rows!r}"
            )
        row = rows[0]
        return {
            "modify_count": int(row["modify_count"]),
            "row_count": int(row["row_count"]),
        }


class TidbHealthCheckAutoAnalyzeDriftScenario(TiDBScenario):
    scenario_id = "tidb_health_check_auto_analyze_drift"
    description = "Routine TiDB health check for automatic statistics configuration drift."
    cases = (_CASE, _NEW_CASE)

    def build_fault_plan(
        self,
        case: TidbHealthCheckAutoAnalyzeDriftCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbHealthCheckAutoAnalyzeDriftInjector,
                config={
                    "db": case.db,
                    "target_table": case.target_table,
                    "payments_table": case.payments_table,
                    "inventory_table": case.inventory_table,
                    "events_table": case.events_table,
                    "report_table": case.report_table,
                    "seed_rows": case.seed_rows,
                    "drift_rows": case.drift_rows,
                    "protected_drift_rows": case.protected_drift_rows,
                    "expected_row_count": case.expected_row_count,
                    "expected_order_id_sum": case.expected_order_id_sum,
                    "expected_amount_cents_sum": case.expected_amount_cents_sum,
                    "expected_payment_count": case.expected_payment_count,
                    "expected_payment_id_sum": case.expected_payment_id_sum,
                    "expected_payment_amount_cents_sum": (
                        case.expected_payment_amount_cents_sum
                    ),
                    "drift_auto_analyze": case.drift_auto_analyze,
                    "expected_auto_analyze": case.expected_auto_analyze,
                    "expected_stmt_summary": case.expected_stmt_summary,
                    "focused_fixture": case.focused_fixture,
                },
            ),
        )
