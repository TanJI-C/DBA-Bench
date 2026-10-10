from collections.abc import Mapping

from src.database.query_results import capture_query_result_truth

from src.database.sql import execute_json_payload, execute_result_rows

from src.scenarios.tidb.common import BaseFaultInjector, FaultLifecycleContext, validate_sql_identifier

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.resource_governance.ru_budget_calibration import (
    TidbResourceGovernanceRuBudgetCalibrationEvaluatorCase,
    TidbResourceGovernanceRuBudgetCalibrationRebalancedEvaluatorCase,
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


RG01_RESOURCE_GROUPS = (
    "rg01_oltp",
    "rg01_olap",
    "rg01_batch",
    "rg01_adhoc",
)
RG01_OLTP_PROFILES = (
    "rg01_oltp_order_lookup",
    "rg01_oltp_customer_lookup",
    "rg01_oltp_status_probe",
    "rg01_oltp_order_update",
)
RG01_OLAP_PROFILES = (
    "rg01_olap_revenue_rollup",
    "rg01_olap_region_join",
)
RG01_SERVICE_OBJECTIVES = (
    (1, "2026-07-01 00:00:00", None, "orders", "rg01_oltp", "oltp_p95_ms", "<=", 500.0, "active"),
    (2, "2026-07-01 00:00:00", None, "revenue", "rg01_olap", "olap_qps", ">=", 0.18, "active"),
    (3, "2026-07-01 00:00:00", None, "cluster", "cluster", "shared_ru_per_sec", "<=", 1000.0, "active"),
    (4, "2026-07-01 00:00:00", None, "orders", "rg01_oltp", "minimum_ru_per_sec", ">=", 500.0, "active"),
    (5, "2026-07-01 00:00:00", None, "revenue", "rg01_olap", "minimum_ru_per_sec", ">=", 220.0, "active"),
    (6, "2026-07-01 00:00:00", None, "archive", "rg01_batch", "minimum_ru_per_sec", ">=", 40.0, "active"),
    (7, "2026-07-01 00:00:00", None, "dashboard", "rg01_adhoc", "minimum_ru_per_sec", ">=", 20.0, "active"),
    (11, "2026-07-01 00:00:00", None, "platform", "default", "reserved_ru_per_sec", ">=", 100.0, "active"),
    (8, "2026-01-01 00:00:00", "2026-06-30 23:59:59", "orders", "rg01_oltp", "oltp_p95_ms", "<=", 800.0, "retired"),
    (9, "2026-01-01 00:00:00", "2026-06-30 23:59:59", "revenue", "rg01_olap", "olap_qps", ">=", 0.10, "retired"),
    (10, "2026-01-01 00:00:00", "2026-06-30 23:59:59", "cluster", "cluster", "shared_ru_per_sec", "<=", 900.0, "retired"),
)
RG01_REBALANCED_SERVICE_OBJECTIVES = (
    (1, "2026-07-01 00:00:00", None, "orders", "rg01_oltp", "oltp_p95_ms", "<=", 550.0, "active"),
    (2, "2026-07-01 00:00:00", None, "revenue", "rg01_olap", "olap_qps", ">=", 0.16, "active"),
    (3, "2026-07-01 00:00:00", None, "cluster", "cluster", "shared_ru_per_sec", "<=", 900.0, "active"),
    (4, "2026-07-01 00:00:00", None, "orders", "rg01_oltp", "minimum_ru_per_sec", ">=", 420.0, "active"),
    (5, "2026-07-01 00:00:00", None, "revenue", "rg01_olap", "minimum_ru_per_sec", ">=", 180.0, "active"),
    (6, "2026-07-01 00:00:00", None, "archive", "rg01_batch", "minimum_ru_per_sec", ">=", 40.0, "active"),
    (7, "2026-07-01 00:00:00", None, "dashboard", "rg01_adhoc", "minimum_ru_per_sec", ">=", 20.0, "active"),
    (11, "2026-07-01 00:00:00", None, "platform", "default", "reserved_ru_per_sec", ">=", 80.0, "active"),
    (8, "2026-01-01 00:00:00", "2026-06-30 23:59:59", "orders", "rg01_oltp", "oltp_p95_ms", "<=", 800.0, "retired"),
    (9, "2026-01-01 00:00:00", "2026-06-30 23:59:59", "revenue", "rg01_olap", "olap_qps", ">=", 0.10, "retired"),
    (10, "2026-01-01 00:00:00", "2026-06-30 23:59:59", "cluster", "cluster", "shared_ru_per_sec", "<=", 900.0, "retired"),
)


def _rg_hint(group: str, sql: str) -> str:
    keyword, remainder = sql.split(" ", 1)
    return f"{keyword} /*+ RESOURCE_GROUP({group}) */ {remainder}"


def _build_rg01_workload(
    db: str,
    orders: str,
    customers: str,
    event_table: str,
) -> BackgroundWorkloadSpec:
    return BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="rg01_oltp_order_lookup",
                sql=_rg_hint(
                    "rg01_oltp",
                    f"SELECT order_id, tenant_id, order_status, amount FROM {db}.{orders} "
                    "WHERE order_id = 42000",
                ),
                qps=2.8,
                tier="OLTP",
            ),
            WorkloadProfile(
                name="rg01_oltp_customer_lookup",
                sql=_rg_hint(
                    "rg01_oltp",
                    f"SELECT customer_id, tenant_id, region, customer_status FROM {db}.{customers} "
                    "WHERE customer_id = 4200",
                ),
                qps=2.0,
                tier="OLTP",
            ),
            WorkloadProfile(
                name="rg01_oltp_status_probe",
                sql=_rg_hint(
                    "rg01_oltp",
                    f"SELECT order_status, COUNT(*) FROM {db}.{orders} "
                    "WHERE tenant_id = 42 AND order_ts >= '2026-01-01 00:00:00' "
                    "GROUP BY order_status",
                ),
                qps=1.2,
                tier="OLTP",
            ),
            WorkloadProfile(
                name="rg01_oltp_order_update",
                sql=_rg_hint(
                    "rg01_oltp",
                    f"UPDATE {db}.{orders} SET order_status = order_status "
                    "WHERE order_id = 42000",
                ),
                qps=0.8,
                tier="OLTP",
                commit=True,
            ),
            WorkloadProfile(
                name="rg01_olap_revenue_rollup",
                sql=_rg_hint(
                    "rg01_olap",
                    f"SELECT tenant_id, order_status, COUNT(*), SUM(amount) FROM {db}.{orders} "
                    "GROUP BY tenant_id, order_status ORDER BY tenant_id, order_status",
                ),
                qps=0.28,
                tier="OLAP",
            ),
            WorkloadProfile(
                name="rg01_olap_region_join",
                sql=_rg_hint(
                    "rg01_olap",
                    f"SELECT c.region, o.order_status, COUNT(*), SUM(o.amount) "
                    f"FROM {db}.{orders} o JOIN {db}.{customers} c ON c.customer_id = o.customer_id "
                    "GROUP BY c.region, o.order_status ORDER BY c.region, o.order_status",
                ),
                qps=0.22,
                tier="OLAP",
            ),
            WorkloadProfile(
                name="rg01_oltp_order_history_probe",
                sql=_rg_hint(
                    "rg01_oltp",
                    f"SELECT order_id, order_status, amount FROM {db}.{orders} "
                    "WHERE tenant_id = 43 AND order_ts >= '2026-01-15 00:00:00' "
                    "ORDER BY order_ts DESC LIMIT 20",
                ),
                qps=0.45,
                tier="OLTP",
            ),
            WorkloadProfile(
                name="rg01_olap_customer_mix",
                sql=_rg_hint(
                    "rg01_olap",
                    f"SELECT c.region, c.customer_status, COUNT(*), SUM(o.amount) "
                    f"FROM {db}.{customers} c JOIN {db}.{orders} o ON o.customer_id = c.customer_id "
                    "GROUP BY c.region, c.customer_status ORDER BY c.region, c.customer_status",
                ),
                qps=0.10,
                tier="OLAP",
            ),
            WorkloadProfile(
                name="rg01_batch_archive_scan",
                sql=_rg_hint(
                    "rg01_batch",
                    f"SELECT COUNT(*), SUM(amount) FROM {db}.{orders} "
                    "WHERE order_status IN ('PAID', 'SHIPPED')",
                ),
                qps=0.18,
                tier="BATCH",
            ),
            WorkloadProfile(
                name="rg01_batch_customer_rollup",
                sql=_rg_hint(
                    "rg01_batch",
                    f"SELECT tenant_id, COUNT(*) FROM {db}.{customers} "
                    "GROUP BY tenant_id ORDER BY tenant_id",
                ),
                qps=0.16,
                tier="BATCH",
            ),
            WorkloadProfile(
                name="rg01_batch_month_close",
                sql=_rg_hint(
                    "rg01_batch",
                    f"SELECT tenant_id, order_status, COUNT(*), SUM(amount) FROM {db}.{orders} "
                    "WHERE order_ts < '2026-02-01 00:00:00' "
                    "GROUP BY tenant_id, order_status",
                ),
                qps=0.10,
                tier="BATCH",
            ),
            WorkloadProfile(
                name="rg01_batch_event_rollup",
                sql=_rg_hint(
                    "rg01_batch",
                    f"SELECT event_type, COUNT(*) FROM {db}.{event_table} "
                    "WHERE event_ts >= '2026-01-01 00:00:00' GROUP BY event_type",
                ),
                qps=0.08,
                tier="BATCH",
            ),
            WorkloadProfile(
                name="rg01_adhoc_dashboard_probe",
                sql=_rg_hint(
                    "rg01_adhoc",
                    f"SELECT order_status, COUNT(*) FROM {db}.{orders} GROUP BY order_status",
                ),
                qps=0.35,
                tier="ADHOC",
            ),
            WorkloadProfile(
                name="rg01_adhoc_customer_probe",
                sql=_rg_hint(
                    "rg01_adhoc",
                    f"SELECT region, COUNT(*) FROM {db}.{customers} GROUP BY region",
                ),
                qps=0.30,
                tier="ADHOC",
            ),
            WorkloadProfile(
                name="rg01_adhoc_tenant_slice",
                sql=_rg_hint(
                    "rg01_adhoc",
                    f"SELECT tenant_id, order_status, COUNT(*) FROM {db}.{orders} "
                    "WHERE tenant_id IN (41, 42, 43) GROUP BY tenant_id, order_status",
                ),
                qps=0.20,
                tier="ADHOC",
            ),
            WorkloadProfile(
                name="rg01_adhoc_event_search",
                sql=_rg_hint(
                    "rg01_adhoc",
                    f"SELECT event_type, COUNT(*) FROM {db}.{event_table} "
                    "WHERE event_type IN ('order', 'refund', 'shipment') GROUP BY event_type",
                ),
                qps=0.18,
                tier="ADHOC",
            ),
        ),
        worker_count=8,
        seed=20260802,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=20,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceRuBudgetCalibrationCase(TiDBScenarioCase):
    db: str
    orders_table: str
    customers_table: str
    event_table: str
    objective_table: str
    service_objectives: tuple[tuple[object, ...], ...]
    resource_groups: tuple[str, ...]
    oltp_group: str
    olap_group: str
    minimum_ru_per_sec: tuple[tuple[str, int], ...]
    maximum_total_ru_per_sec: int
    maximum_oltp_p95_ms: float
    minimum_olap_qps: float
    observation_window_seconds: float
    oltp_profiles: tuple[str, ...]
    olap_profiles: tuple[str, ...]
    orders_row_count: int
    customers_row_count: int
    event_row_count: int
    business_truth_sql: str
    initial_resource_groups: tuple[tuple[str, int, str], ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceRuBudgetCalibrationForMixedOltpOlapScenarioCase(
    TidbResourceGovernanceRuBudgetCalibrationCase
):
    pass


_RG01_CASE = TidbResourceGovernanceRuBudgetCalibrationForMixedOltpOlapScenarioCase(
    case_id="mixed_oltp_olap_ru_budget_calibration",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "raised the OLTP and OLAP RU budgets within the shared cap",
                "bounded batch and adhoc groups with moderated burst behavior"
            ],
            "verification": [
                "resource control remains ON and all managed groups are finite",
                "OLTP p95, OLAP throughput, and order truth were verified"
            ]
        },
        "summary": "The mixed workload RU allocation was calibrated without changing business data."
    },
    case_no=0,
    evaluator=TidbResourceGovernanceRuBudgetCalibrationEvaluatorCase,
    title="Calibrate RU budgets for mixed OLTP and OLAP workloads.",
    alert=(
        "[SEV-2] TiDB resource governance review: order-entry and revenue services share "
        "one cluster with archive and dashboard traffic. Users report uneven response time "
        "and analytical progress while the admission allocation is under review. "
        "Use the live database and workload evidence, including the operations service "
        "objectives, to choose a finite bounded allocation for the existing resource groups. "
        "Keep service continuity and order/customer truth unchanged. Do not disable resource "
        "control or restart nodes as a shortcut."
    ),
    initial_state={
        "resource_control": "ON",
        "resource_groups": {
            "rg01_oltp": {"ru_per_sec": 120, "burstable": "BOUNDED"},
            "rg01_olap": {"ru_per_sec": 40, "burstable": "UNLIMITED"},
            "rg01_batch": {"ru_per_sec": 180, "burstable": "UNLIMITED"},
            "rg01_adhoc": {"ru_per_sec": 260, "burstable": "UNLIMITED"},
        },
    },
    expected_target={
        "resource_control": "ON",
        "minimum_ru_per_sec": {
            "rg01_oltp": 500,
            "rg01_olap": 220,
            "rg01_batch": 40,
            "rg01_adhoc": 20,
        },
        "maximum_total_ru_per_sec": 1000,
        "max_oltp_p95_ms": 500.0,
        "min_olap_qps": 0.18,
        "burstable": "NO/BOUNDED",
    },
    background_workload=_build_rg01_workload("rg01_ops", "orders", "customers", "event_log"),
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.707137,
        reference_run_ids=(
            "reference-221__"
            "tidb_resource_governance_ru_budget_calibration__"
            "mixed_oltp_olap_ru_budget_calibration__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=3,
        tidb_count=1,
        sql_timeout_seconds=120,
        image_group_key=None,
    ),
    db="rg01_ops",
    orders_table="orders",
    customers_table="customers",
    event_table="event_log",
    objective_table="service_objectives",
    service_objectives=RG01_SERVICE_OBJECTIVES,
    resource_groups=RG01_RESOURCE_GROUPS,
    oltp_group="rg01_oltp",
    olap_group="rg01_olap",
    minimum_ru_per_sec=(
        ("rg01_oltp", 500),
        ("rg01_olap", 220),
        ("rg01_batch", 40),
        ("rg01_adhoc", 20),
    ),
    maximum_total_ru_per_sec=1000,
    maximum_oltp_p95_ms=500.0,
    minimum_olap_qps=0.18,
    observation_window_seconds=20.0,
    oltp_profiles=RG01_OLTP_PROFILES,
    olap_profiles=RG01_OLAP_PROFILES,
    orders_row_count=60000,
    customers_row_count=12000,
    event_row_count=24000,
    business_truth_sql=(
        "SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
        "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, customer_id, "
        "order_status, order_ts, amount, payload))), 0) "
        "FROM rg01_ops.orders"
    ),
    initial_resource_groups=(
        ("rg01_oltp", 120, "BOUNDED"),
        ("rg01_olap", 40, "UNLIMITED"),
        ("rg01_batch", 180, "UNLIMITED"),
        ("rg01_adhoc", 260, "UNLIMITED"),
    ),
)

_RG01_REBALANCED_CASE = replace(
    _RG01_CASE,
    case_id="mixed_oltp_olap_ru_budget_rebalanced",
    case_no=1,
    evaluator=TidbResourceGovernanceRuBudgetCalibrationRebalancedEvaluatorCase,
    title="Rebalance mixed OLTP and OLAP RU budgets under a tighter platform reservation.",
    alert=(
        "[SEV-2] The order-entry and revenue workloads are both online, but the platform reservation "
        "for the next reporting window is smaller than the previous allocation. Use current workload and "
        "service-objective evidence to choose finite budgets for the existing groups, preserve order truth, "
        "and keep resource control enabled. Do not disable admission control or restart nodes."
    ),
    initial_state={
        "resource_control": "ON",
        "resource_groups": "existing groups have a stale allocation for a reduced platform reservation",
        "platform_reservation": "900 RU/s",
    },
    expected_target={
        "resource_control": "ON",
        "minimum_ru_per_sec": {
            "rg01_oltp": 420,
            "rg01_olap": 180,
            "rg01_batch": 40,
            "rg01_adhoc": 20,
        },
        "maximum_total_ru_per_sec": 900,
        "max_oltp_p95_ms": 550.0,
        "min_olap_qps": 0.16,
        "burstable": "NO/BOUNDED",
    },
    maximum_oltp_p95_ms=550.0,
    minimum_olap_qps=0.16,
    service_objectives=RG01_REBALANCED_SERVICE_OBJECTIVES,
    minimum_ru_per_sec=(
        ("rg01_oltp", 420),
        ("rg01_olap", 180),
        ("rg01_batch", 40),
        ("rg01_adhoc", 20),
    ),
    maximum_total_ru_per_sec=900,
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.0,
        reference_run_ids=(
            "tidb-reference-5__tidb_resource_governance_ru_budget_calibration__"
            "mixed_oltp_olap_ru_budget_rebalanced__mock__r001",
        ),
    ),
)


class TidbResourceGovernanceRuBudgetCalibrationInjector(BaseFaultInjector):
    """Create the mixed-workload RU budget calibration environment."""

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_schema(context.env)
        self._create_resource_groups(context.env)
        self._verify_persistent_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_persistent_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_persistent_state(context.env)
        group_rows = execute_result_rows(
            context.env.execute_sql,
            self._resource_group_sql(),
            "capture RG01 resource groups",
        )
        truth_payload = execute_json_payload(
            context.env.execute_sql,
            self.business_truth_sql,
            "capture RG01 business truth",
        )
        return {
            "rg01_initial_resource_groups": group_rows,
            "rg01_business_truth": capture_query_result_truth(truth_payload, ordered=True),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        groups = execute_result_rows(
            context.env.execute_sql,
            self._resource_group_sql(),
            "list RG01 resource groups for recovery",
        )
        for row in reversed(groups):
            group = validate_sql_identifier(str(row[0]), "resource_group")
            self._execute(
                context.env,
                f"DROP RESOURCE GROUP {group}",
                f"drop RG01 resource group {group}",
            )
        self._execute(
            context.env,
            f"DROP DATABASE IF EXISTS {self.db}",
            f"drop RG01 database {self.db}",
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.orders_table = validate_sql_identifier(str(config["orders_table"]), "orders_table")
        self.customers_table = validate_sql_identifier(str(config["customers_table"]), "customers_table")
        self.event_table = validate_sql_identifier(str(config["event_table"]), "event_table")
        self.objective_table = validate_sql_identifier(str(config["objective_table"]), "objective_table")
        self.resource_groups = tuple(
            validate_sql_identifier(str(group), "resource_group")
            for group in config["resource_groups"]
        )
        self.initial_resource_groups = tuple(
            (validate_sql_identifier(str(group), "resource_group"), int(ru), str(burstable))
            for group, ru, burstable in config["initial_resource_groups"]
        )
        self.orders_row_count = int(config["orders_row_count"])
        self.customers_row_count = int(config["customers_row_count"])
        self.event_row_count = int(config["event_row_count"])
        self.business_truth_sql = str(config["business_truth_sql"])
        self.service_objectives = tuple(tuple(row) for row in config["service_objectives"])

    @staticmethod
    def _execute(env, sql: str, context: str) -> dict:
        return execute_json_payload(env.execute_sql, sql, f"{context}: sql={sql!r}")

    def _create_schema(self, env) -> None:
        self._execute(env, f"DROP DATABASE IF EXISTS {self.db}", f"clear RG01 database {self.db}")
        self._execute(env, f"CREATE DATABASE {self.db}", f"create RG01 database {self.db}")
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.orders_table} ("
            "order_id BIGINT NOT NULL, "
            "tenant_id INT NOT NULL, "
            "customer_id BIGINT NOT NULL, "
            "order_status VARCHAR(16) NOT NULL, "
            "order_ts DATETIME NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, "
            "payload VARCHAR(96) NOT NULL, "
            "PRIMARY KEY (order_id), "
            "KEY idx_orders_tenant_ts (tenant_id, order_ts), "
            "KEY idx_orders_customer (customer_id), "
            "KEY idx_orders_status_ts (order_status, order_ts)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG01 orders table {self.db}.{self.orders_table}",
        )
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.customers_table} ("
            "customer_id BIGINT NOT NULL, "
            "tenant_id INT NOT NULL, "
            "region VARCHAR(16) NOT NULL, "
            "customer_status VARCHAR(16) NOT NULL, "
            "profile VARCHAR(96) NOT NULL, "
            "PRIMARY KEY (customer_id), "
            "KEY idx_customers_tenant (tenant_id), "
            "KEY idx_customers_region (region)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG01 customers table {self.db}.{self.customers_table}",
        )
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.event_table} ("
            "event_id BIGINT NOT NULL, "
            "event_type VARCHAR(16) NOT NULL, "
            "event_ts DATETIME NOT NULL, "
            "payload VARCHAR(128) NOT NULL, "
            "PRIMARY KEY (event_id), KEY idx_event_type_ts (event_type, event_ts)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG01 event table {self.db}.{self.event_table}",
        )
        self._create_numbers(env)
        self._load_orders(env)
        self._load_customers(env)
        self._load_events(env)
        self._create_service_objectives(env)
        self._execute(
            env,
            f"DROP TABLE {self.db}._rg01_numbers",
            "drop RG01 seed number table",
        )
        self._assert_row_count(env, self.orders_table, self.orders_row_count)
        self._assert_row_count(env, self.customers_table, self.customers_row_count)
        self._assert_row_count(env, self.event_table, self.event_row_count)

    def _create_service_objectives(self, env) -> None:
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.objective_table} ("
            "objective_id INT NOT NULL PRIMARY KEY, "
            "effective_from DATETIME NOT NULL, "
            "effective_to DATETIME NULL, "
            "service VARCHAR(32) NOT NULL, "
            "resource_group VARCHAR(32) NOT NULL, "
            "metric VARCHAR(32) NOT NULL, "
            "operator VARCHAR(4) NOT NULL, "
            "target_value DECIMAL(12,3) NOT NULL, "
            "status VARCHAR(16) NOT NULL"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG01 objective table {self.db}.{self.objective_table}",
        )
        for row in self.service_objectives:
            (
                objective_id,
                effective_from,
                effective_to,
                service,
                resource_group,
                metric,
                operator,
                target_value,
                status,
            ) = row
            effective_to_sql = "NULL" if effective_to is None else f"'{effective_to}'"
            self._execute(
                env,
                f"INSERT INTO {self.db}.{self.objective_table} "
                "(objective_id, effective_from, effective_to, service, resource_group, "
                "metric, operator, target_value, status) VALUES "
                f"({int(objective_id)}, '{effective_from}', {effective_to_sql}, "
                f"'{service}', '{resource_group}', '{metric}', '{operator}', "
                f"{float(target_value):.3f}, '{status}')",
                f"load RG01 service objective objective_id={objective_id}",
            )

    def _create_numbers(self, env) -> None:
        self._execute(
            env,
            f"CREATE TABLE {self.db}._rg01_numbers (n INT NOT NULL PRIMARY KEY)",
            "create RG01 seed number table",
        )
        digits = "(SELECT 0 AS digit UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9)"
        for offset in range(0, self.orders_row_count, 10000):
            expression = (
                f"{offset} + a.digit + 10 * b.digit + 100 * c.digit + "
                "1000 * d.digit + 1"
            )
            self._execute(
                env,
                f"INSERT INTO {self.db}._rg01_numbers (n) "
                f"SELECT {expression} FROM {digits} a CROSS JOIN {digits} b "
                f"CROSS JOIN {digits} c CROSS JOIN {digits} d "
                f"WHERE {expression} <= {self.orders_row_count}",
                f"load RG01 seed numbers start={offset + 1}",
            )

    def _load_orders(self, env) -> None:
        self._load_batches(
            env,
            self.orders_table,
            self.orders_row_count,
            "(order_id, tenant_id, customer_id, order_status, order_ts, amount, payload)",
            "n, MOD(n, 1024), MOD(n, 12000) + 1, "
            "ELT(MOD(n, 4) + 1, 'PAID', 'PENDING', 'CANCELLED', 'SHIPPED'), "
            "TIMESTAMPADD(SECOND, n, TIMESTAMP'2026-01-01 00:00:00'), "
            "CAST(MOD(n * 7919, 1000000) / 100 AS DECIMAL(12,2)), "
            "RPAD(CONCAT('order-', n), 64, 'x')",
            "orders",
        )

    def _load_customers(self, env) -> None:
        self._load_batches(
            env,
            self.customers_table,
            self.customers_row_count,
            "(customer_id, tenant_id, region, customer_status, profile)",
            "n, MOD(n, 1024), ELT(MOD(n, 8) + 1, 'north', 'south', 'east', 'west', "
            "'central', 'intl', 'metro', 'rural'), "
            "ELT(MOD(n, 3) + 1, 'active', 'trial', 'paused'), "
            "RPAD(CONCAT('customer-', n), 64, 'c')",
            "customers",
        )

    def _load_events(self, env) -> None:
        self._load_batches(
            env,
            self.event_table,
            self.event_row_count,
            "(event_id, event_type, event_ts, payload)",
            "n, ELT(MOD(n, 5) + 1, 'audit', 'login', 'order', 'refund', 'shipment'), "
            "TIMESTAMPADD(SECOND, n, TIMESTAMP'2026-01-01 00:00:00'), "
            "RPAD(CONCAT('event-', n), 80, 'e')",
            "events",
        )

    def _load_batches(
        self,
        env,
        table: str,
        row_count: int,
        columns: str,
        expressions: str,
        label: str,
    ) -> None:
        for start in range(1, row_count + 1, 10000):
            end = min(start + 9999, row_count)
            self._execute(
                env,
                f"INSERT INTO {self.db}.{table} {columns} "
                f"SELECT {expressions} FROM {self.db}._rg01_numbers "
                f"WHERE n BETWEEN {start} AND {end}",
                f"load RG01 {label} rows={start}-{end}",
            )

    def _create_resource_groups(self, env) -> None:
        self._execute(env, "SET GLOBAL tidb_enable_resource_control = ON", "enable RG01 resource control")
        for group, ru, burstable in self.initial_resource_groups:
            burst_clause = {
                "BOUNDED": "BURSTABLE=FALSE",
                "UNLIMITED": "BURSTABLE=TRUE",
            }[burstable]
            self._execute(
                env,
                f"CREATE RESOURCE GROUP {group} RU_PER_SEC = {ru} {burst_clause}",
                f"create RG01 resource group {group}",
            )

    def _resource_group_sql(self) -> str:
        names = ", ".join(f"'{group}'" for group in self.resource_groups)
        return (
            "SELECT NAME, RU_PER_SEC, BURSTABLE FROM information_schema.resource_groups "
            f"WHERE NAME IN ({names}) ORDER BY NAME"
        )

    def _verify_persistent_state(self, env) -> None:
        global_setting = execute_result_rows(
            env.execute_sql,
            "SHOW GLOBAL VARIABLES LIKE 'tidb_enable_resource_control'",
            "verify RG01 resource control",
        )
        if len(global_setting) != 1 or str(global_setting[0][1]).casefold() != "on":
            raise RuntimeError(
                "RG01 requires tidb_enable_resource_control=ON before agent handoff: "
                f"observed={global_setting!r}"
            )
        groups = execute_result_rows(env.execute_sql, self._resource_group_sql(), "verify RG01 resource groups")
        observed = {str(row[0]) for row in groups}
        if observed != set(self.resource_groups):
            raise RuntimeError(
                "RG01 resource group set mismatch before agent handoff: "
                f"expected={self.resource_groups!r}, observed={sorted(observed)!r}"
            )

    def _assert_row_count(self, env, table: str, expected: int) -> None:
        rows = execute_result_rows(
            env.execute_sql,
            f"SELECT COUNT(*) FROM {self.db}.{table}",
            f"verify RG01 row count {self.db}.{table}",
        )
        observed = int(rows[0][0])
        if observed != expected:
            raise RuntimeError(
                "RG01 data load row count mismatch: "
                f"table={self.db}.{table}, expected={expected}, observed={observed}"
            )


class TidbResourceGovernanceRuBudgetCalibrationScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_ru_budget_calibration"
    description = "Calibrates RU budgets for mixed OLTP and OLAP workloads under a shared cap."
    cases = (_RG01_CASE, _RG01_REBALANCED_CASE)

    def build_fault_plan(
        self,
        case: TidbResourceGovernanceRuBudgetCalibrationCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernanceRuBudgetCalibrationInjector,
                config={
                    "db": case.db,
                    "orders_table": case.orders_table,
                    "customers_table": case.customers_table,
                    "event_table": case.event_table,
                    "objective_table": case.objective_table,
                    "service_objectives": case.service_objectives,
                    "resource_groups": case.resource_groups,
                    "initial_resource_groups": case.initial_resource_groups,
                    "orders_row_count": case.orders_row_count,
                    "customers_row_count": case.customers_row_count,
                    "event_row_count": case.event_row_count,
                    "business_truth_sql": case.business_truth_sql,
                },
            ),
        )
