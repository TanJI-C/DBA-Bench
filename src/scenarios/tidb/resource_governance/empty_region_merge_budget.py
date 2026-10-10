import re

import time

from collections.abc import Mapping

from src.database.query_results import capture_query_result_truth

from src.database.sql import parse_json_object, require_success_payload, sequence_row_source

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext

from src.scenarios.tidb.common import json_object, require_sql_success, validate_sql_identifier

from dataclasses import dataclass, replace

from src.scenarios.workloads import WorkloadProfile
from src.scenarios.evaluation.tidb.resource_governance import (
    TidbResourceGovernanceEmptyRegionMergeBudgetEvaluatorCase,
    TidbResourceGovernanceEmptyRegionMergeBudgetReducedInventoryEvaluatorCase,
)

from ...base import (
    BackgroundWorkloadSpec,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


_DB = "test"
_BUSINESS_TABLE = "rg07_orders"
_CONTROL_TABLE = "rg07_orders_control"
_AUDIT_TABLE = "rg07_order_audit"
_EMPTY_TABLE_PREFIX = "rg07_empty"
_MAINTENANCE_TABLE_PREFIX = "rg07_maintenance"
_BUSINESS_PARTITIONS = 32

_BUSINESS_QUERY = (
    "SELECT tenant_id, status, COUNT(*) AS order_count, "
    "CAST(SUM(amount) AS DECIMAL(18,2)) AS gross_amount "
    f"FROM {_DB}.{_BUSINESS_TABLE} "
    "WHERE order_day >= '2026-02-01' "
    "GROUP BY tenant_id, status "
    "ORDER BY tenant_id, status"
)

_BUSINESS_INTEGRITY_QUERY = (
    "SELECT COUNT(*) AS row_count, "
    "CAST(COALESCE(SUM(amount), 0) AS DECIMAL(18,2)) AS amount_sum, "
    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, status, amount, "
    "order_day, region, payload))), 0) AS payload_checksum "
    f"FROM {_DB}.{_BUSINESS_TABLE}"
)

_CONTROL_QUERY = (
    "SELECT region, status, COUNT(*) AS order_count "
    f"FROM {_DB}.{_CONTROL_TABLE} "
    "GROUP BY region, status ORDER BY region, status"
)

_AUDIT_QUERY = (
    "SELECT event_type, COUNT(*) AS event_count "
    f"FROM {_DB}.{_AUDIT_TABLE} "
    "GROUP BY event_type ORDER BY event_type"
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceEmptyRegionMergeBudgetCase(TiDBScenarioCase):
    db: str
    business_table: str
    control_table: str
    audit_table: str
    empty_table_prefix: str
    empty_table_count: int
    maintenance_table_prefix: str
    maintenance_table_count: int
    maintenance_rows: int
    pre_split_regions: int
    business_partition_count: int
    business_rows: int
    control_rows: int
    audit_rows: int
    minimum_empty_regions: int
    empty_region_wait_seconds: int
    maximum_empty_regions: int
    maximum_empty_ratio: float
    health_delta_allowed: int
    convergence_wait_seconds: int
    business_query: str
    business_integrity_query: str
    baseline_pd_config: dict[str, object]
    fault_pd_config: dict[str, object]
    safe_merge_schedule_limit_min: int
    safe_merge_schedule_limit_max: int
    safe_merge_region_keys_max: int
    safe_merge_region_size_max_mb: int
    safe_split_merge_interval_seconds: int
    safe_region_schedule_limit_max: int
    safe_pd_cpu_percent_max: float
    safe_operator_create_rate_max: float
    safe_merge_operator_create_rate_max: float

    @property
    def owned_tables(self) -> tuple[str, ...]:
        return (
            self.business_table,
            self.control_table,
            self.audit_table,
            *(f"{self.empty_table_prefix}_{index:03d}" for index in range(self.empty_table_count)),
            *(
                f"{self.maintenance_table_prefix}_{index:03d}"
                for index in range(self.maintenance_table_count)
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceEmptyRegionMergeBudgetForEmptyRegionMergeBudgetScenarioCase(
    TidbResourceGovernanceEmptyRegionMergeBudgetCase
):
    pass


_CASE = TidbResourceGovernanceEmptyRegionMergeBudgetForEmptyRegionMergeBudgetScenarioCase(
    case_id="empty_region_merge_budget",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "preserved non-empty business Regions and restored bounded cross-table merge scheduling"
            ],
            "verification": [
                "verified Region health, PD scheduling and order truth"
            ]
        },
        "summary": "The scripted RG07 mock applied bounded resource-governance settings and verified the final state."
    },
    case_no=0,
    evaluator=TidbResourceGovernanceEmptyRegionMergeBudgetEvaluatorCase,
    title=(
        "A live order workload coexists with a Region scheduling backlog after recent table maintenance; "
        "PD budget and protected online objects must remain healthy."
    ),
    alert=(
        "[WARNING] [Grafana/TiDB-PD/Region health] 集群 Region inventory 持续增长，"
        "PD heartbeat 处理和 operator 队列开始占用预算；订单查询仍可执行，但调度延迟和 PD CPU 有上升趋势。"
        "请在不修改在线数据、不删除业务表、不重启集群的前提下治理 Region 调度风险，"
        "选择有界的 merge/scheduler 预算，观察风险收敛，并证明没有引发新的调度风暴。"
    ),
    initial_state={
        "status": "resource_pressure",
        "region_inventory": "growing",
        "pd_scheduling": "heartbeat_and_operator_pressure",
        "business": "orders_online",
    },
    expected_target={
        "status": "converged",
        "region_risk": "within_safe_ratio",
        "pd_scheduling": "bounded",
        "business_result_preserved": True,
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="rg07_order_tenant_status_dashboard",
                sql=_BUSINESS_QUERY,
                qps=0.8,
                tier="OLAP_BURST",
                application_name="order-dashboard",
            ),
            WorkloadProfile(
                name="rg07_order_point_lookup",
                sql=(
                    f"SELECT order_id, tenant_id, status, amount FROM {_DB}.{_BUSINESS_TABLE} "
                    "WHERE order_id = MOD(UNIX_TIMESTAMP(CURRENT_TIMESTAMP), 20000) + 1"
                ),
                qps=1.8,
                tier="OLTP_CORE",
                application_name="order-api",
            ),
            WorkloadProfile(
                name="rg07_control_region_rollup",
                sql=_CONTROL_QUERY,
                qps=0.5,
                tier="OLAP_BURST",
                application_name="regional-control-report",
            ),
            WorkloadProfile(
                name="rg07_audit_reconciliation",
                sql=_AUDIT_QUERY,
                qps=0.45,
                tier="OLAP_BURST",
                application_name="audit-reconciliation",
            ),
            WorkloadProfile(
                name="rg07_table_inventory_probe",
                sql=(
                    "SELECT TABLE_NAME, TABLE_ROWS, TABLE_COMMENT, CREATE_OPTIONS "
                    "FROM INFORMATION_SCHEMA.TABLES "
                    f"WHERE TABLE_SCHEMA='{_DB}' AND TABLE_NAME LIKE 'rg07_%' "
                    "ORDER BY TABLE_NAME"
                ),
                qps=0.6,
                tier="DDL_MAINTENANCE_OBSERVABILITY",
                application_name="schema-inventory",
            ),
            WorkloadProfile(
                name="rg07_business_status_decoy",
                sql=(
                    "SELECT status, COUNT(*), CAST(SUM(amount) AS DECIMAL(18,2)) "
                    f"FROM {_DB}.{_BUSINESS_TABLE} GROUP BY status ORDER BY status"
                ),
                qps=0.7,
                tier="OLAP_BURST",
                application_name="order-status-report",
            ),
            WorkloadProfile(
                name="rg07_audit_recent_decoy",
                sql=(
                    "SELECT COUNT(*) AS recent_events "
                    f"FROM {_DB}.{_AUDIT_TABLE} WHERE event_day >= '2026-03-01'"
                ),
                qps=0.35,
                tier="LIGHT",
                application_name="audit-preview",
            ),
        ),
        worker_count=6,
        seed=20260802,
        warmup_seconds=12,
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=3,
        tidb_count=1,
        sql_timeout_seconds=300,
        bootstrap_cache_enabled=False,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.886525,
        reference_run_ids=(
            "run_tidb_resource_governance_empty_region_merge_budget_empty_region_merge_budget_"
            "MockLLMAgent.json",
        ),
    ),
    db=_DB,
    business_table=_BUSINESS_TABLE,
    control_table=_CONTROL_TABLE,
    audit_table=_AUDIT_TABLE,
    empty_table_prefix=_EMPTY_TABLE_PREFIX,
    empty_table_count=24,
    maintenance_table_prefix=_MAINTENANCE_TABLE_PREFIX,
    maintenance_table_count=4,
    maintenance_rows=512,
    pre_split_regions=2,
    business_partition_count=_BUSINESS_PARTITIONS,
    business_rows=20000,
    control_rows=8000,
    audit_rows=6000,
    minimum_empty_regions=48,
    empty_region_wait_seconds=180,
    maximum_empty_regions=12,
    maximum_empty_ratio=0.25,
    health_delta_allowed=0,
    convergence_wait_seconds=600,
    business_query=_BUSINESS_QUERY,
    business_integrity_query=_BUSINESS_INTEGRITY_QUERY,
    baseline_pd_config={
        "schedule.enable-cross-table-merge": True,
        "schedule.merge-schedule-limit": 8,
        "schedule.max-merge-region-size": 20,
        "schedule.max-merge-region-keys": 200000,
        "schedule.split-merge-interval": "1h0m0s",
    },
    fault_pd_config={
        "schedule.enable-cross-table-merge": False,
        "schedule.merge-schedule-limit": 1,
        "schedule.max-merge-region-size": 2,
        "schedule.max-merge-region-keys": 8,
        "schedule.split-merge-interval": "15m0s",
    },
    safe_merge_schedule_limit_min=2,
    safe_merge_schedule_limit_max=16,
    safe_merge_region_keys_max=1024,
    safe_merge_region_size_max_mb=8,
    safe_split_merge_interval_seconds=60,
    safe_region_schedule_limit_max=32,
    safe_pd_cpu_percent_max=85.0,
    safe_operator_create_rate_max=8.0,
    safe_merge_operator_create_rate_max=8.0,
)

_REDUCED_INVENTORY_CASE = replace(
    _CASE,
    case_id="empty_region_merge_reduced_inventory",
    case_no=1,
    evaluator=TidbResourceGovernanceEmptyRegionMergeBudgetReducedInventoryEvaluatorCase,
    title="Reduce a smaller Empty Region inventory without widening the PD merge budget.",
    alert=(
        "[WARNING] PD scheduling pressure remains visible after a smaller maintenance inventory was "
        "cleared. Correlate Empty Region counts, table inventory, scheduler settings, and order truth; "
        "restore bounded cross-table merge scheduling and let the inventory converge. Do not modify data, "
        "drop the online order tables, or restart the cluster."
    ),
    initial_state={
        "status": "resource_pressure",
        "region_inventory": "reduced_but_growing",
        "pd_scheduling": "heartbeat_and_operator_pressure",
        "business": "orders_online",
    },
    expected_target={
        "status": "converged",
        "region_risk": "within_safe_ratio",
        "pd_scheduling": "bounded",
        "business_result_preserved": True,
        "inventory": "16 empty-region tables",
    },
    empty_table_count=16,
    pre_split_regions=1,
    minimum_empty_regions=16,
    maximum_empty_regions=8,
    maximum_empty_ratio=0.30,
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.55122,
        reference_run_ids=(
            "tidb-reference-13__tidb_resource_governance_empty_region_merge_budget__"
            "empty_region_merge_reduced_inventory__mock__r001",
        ),
    ),
)


_BUSINESS_PAYLOAD_CHUNKS = 128

class TidbResourceGovernanceEmptyRegionMergeBudgetInjector(BaseFaultInjector):
    """Create split-and-truncated tables and constrain their PD merge budget."""

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._capture_pd_config(context.env)
        self._set_fault_pd_config(context.env)
        self._create_business_tables(context.env)
        self._create_empty_region_tables(context.env)
        self._create_maintenance_tables(context.env)
        self._verify_fault_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._wait_for_empty_regions(context.env)
        self._verify_fault_state(context.env)
        business_result = self._payload(
            context.env,
            self.business_query,
            "capture RG07 business result truth",
        )
        business_integrity = self._payload(
            context.env,
            self.business_integrity_query,
            "capture RG07 business integrity",
        )["result"]
        region_health = self._metric(context.env, "region_health")
        pd_scheduling = self._metric(context.env, "pd_scheduling")
        pd_config = self._pd_config(context.env)
        pd_operators = self._pd_operators(context.env)
        workload_activity = self._metric(context.env, "workload_activity")
        return {
            "business_result_truth": capture_query_result_truth(business_result, ordered=True),
            "business_integrity": business_integrity,
            "region_health": region_health,
            "pd_scheduling": pd_scheduling,
            "pd_config": pd_config,
            "pd_operators": pd_operators,
            "workload_activity": workload_activity,
            "empty_region_table_count": self.empty_table_count,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        for key, value in self.recovery_pd_config.items():
            self._set_pd_config_value(context.env, key, value)
        for table in self.owned_tables:
            self._require_success(
                context.env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"),
                f"drop RG07 owned table {self.db}.{table}",
            )
        self._assert_tables_absent(context.env)

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.business_table = validate_sql_identifier(str(config["business_table"]), "business table")
        self.control_table = validate_sql_identifier(str(config["control_table"]), "control table")
        self.audit_table = validate_sql_identifier(str(config["audit_table"]), "audit table")
        self.empty_table_prefix = validate_sql_identifier(
            str(config["empty_table_prefix"]), "empty table prefix"
        )
        self.empty_table_count = int(config["empty_table_count"])
        self.maintenance_table_prefix = validate_sql_identifier(
            str(config["maintenance_table_prefix"]), "maintenance table prefix"
        )
        self.maintenance_table_count = int(config["maintenance_table_count"])
        self.maintenance_rows = int(config["maintenance_rows"])
        self.pre_split_regions = int(config["pre_split_regions"])
        self.business_partition_count = int(config["business_partition_count"])
        self.business_rows = int(config["business_rows"])
        self.control_rows = int(config["control_rows"])
        self.audit_rows = int(config["audit_rows"])
        self.business_query = str(config["business_query"])
        self.business_integrity_query = str(config["business_integrity_query"])
        self.minimum_empty_regions = int(config["minimum_empty_regions"])
        self.empty_region_wait_seconds = int(config["empty_region_wait_seconds"])
        self.fault_pd_config = dict(config["fault_pd_config"])
        self.baseline_pd_config = dict(config["baseline_pd_config"])
        self.empty_region_tables = tuple(
            f"{self.empty_table_prefix}_{index:03d}" for index in range(self.empty_table_count)
        )
        self.maintenance_tables = tuple(
            f"{self.maintenance_table_prefix}_{index:03d}"
            for index in range(self.maintenance_table_count)
        )
        self.owned_tables = (
            self.business_table,
            self.control_table,
            self.audit_table,
            *self.empty_region_tables,
            *self.maintenance_tables,
        )

    @staticmethod
    def _payload(env, sql: str, context: str) -> dict:
        return require_success_payload(env.execute_sql(sql), f"{context}: sql={sql!r}")

    @staticmethod
    def _require_success(raw, context: str) -> dict:
        return require_success_payload(raw, context)

    @staticmethod
    def _metric(env, metric: str) -> dict:
        return require_success_payload(env.observe_metric(metric), f"RG07 metric={metric}")

    def _pd_config(self, env) -> dict:
        result = env.get_deployment().pd_request("GET", "/pd/api/v1/config")
        if not isinstance(result, dict) or not isinstance(result.get("schedule"), dict):
            raise TypeError(f"RG07 PD config has no schedule mapping: result={result!r}")
        return result

    def _pd_operators(self, env) -> object:
        return env.get_deployment().pd_request("GET", "/pd/api/v1/operators")

    def _capture_pd_config(self, env) -> None:
        observed = self._pd_config(env)["schedule"]
        self.recovery_pd_config = {
            key: observed[key.removeprefix("schedule.")]
            for key in self.fault_pd_config
        }

    def _set_fault_pd_config(self, env) -> None:
        for key, value in self.fault_pd_config.items():
            self._set_pd_config_value(env, key, value)

    def _set_pd_config_value(self, env, key: str, value: object) -> None:
        if not key.startswith("schedule.") or key.count(".") != 1:
            raise ValueError(f"RG07 owns only schedule.* PD config keys: key={key!r}")
        api_value = str(value).casefold() if isinstance(value, bool) else value
        result = env.get_deployment().pd_request(
            "POST",
            "/pd/api/v1/config",
            {key: api_value},
        )
        if result is not None and not isinstance(result, (dict, str)):
            raise TypeError(
                f"RG07 PD config update returned an invalid payload: key={key!r}, result={result!r}"
            )

    @staticmethod
    def _normalize_pd_value(key: str, value: object) -> object:
        if key.endswith("enable-cross-table-merge"):
            return str(value).casefold() in {"true", "1", "on"}
        if key.endswith("merge-schedule-limit"):
            return int(value)
        if key.endswith("split-merge-interval"):
            text = str(value).strip().casefold()
            matches = re.fullmatch(
                r"(?:(?P<hours>[0-9]+(?:\.[0-9]+)?)h)?"
                r"(?:(?P<minutes>[0-9]+(?:\.[0-9]+)?)m)?"
                r"(?:(?P<seconds>[0-9]+(?:\.[0-9]+)?)s)?",
                text,
            )
            if matches is None or not any(matches.group(name) for name in ("hours", "minutes", "seconds")):
                raise ValueError(f"RG07 invalid PD duration: key={key!r}, value={value!r}")
            return round(
                float(matches.group("hours") or 0) * 3600
                + float(matches.group("minutes") or 0) * 60
                + float(matches.group("seconds") or 0),
                6,
            )
        return str(value).casefold()

    def _verify_fault_state(self, env) -> None:
        schedule = self._pd_config(env)["schedule"]
        observed = {
            key: schedule[key.removeprefix("schedule.")]
            for key in self.fault_pd_config
        }
        normalized_observed = {
            key: self._normalize_pd_value(key, value)
            for key, value in observed.items()
        }
        normalized_expected = {
            key: self._normalize_pd_value(key, value)
            for key, value in self.fault_pd_config.items()
        }
        if normalized_observed != normalized_expected:
            raise RuntimeError(
                "RG07 fault PD configuration is not active: "
                f"expected={self.fault_pd_config!r}, observed={observed!r}"
            )

    def _create_business_tables(self, env) -> None:
        self._require_success(
            env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {self.db}"),
            f"create RG07 database {self.db}",
        )
        self._require_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.business_table}"),
            f"clear RG07 business table {self.db}.{self.business_table}",
        )
        self._require_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.control_table}"),
            f"clear RG07 control table {self.db}.{self.control_table}",
        )
        self._require_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.audit_table}"),
            f"clear RG07 audit table {self.db}.{self.audit_table}",
        )
        business_schema = (
            "order_id BIGINT NOT NULL, tenant_id INT NOT NULL, status VARCHAR(16) NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, order_day DATE NOT NULL, "
            "region VARCHAR(8) NOT NULL, payload VARCHAR(8192) NOT NULL, "
            "PRIMARY KEY (order_id, tenant_id), "
            "KEY idx_rg07_tenant_day (tenant_id, order_day)"
            f") PARTITION BY HASH (tenant_id) PARTITIONS {self.business_partition_count}"
        )
        control_schema = (
            "order_id BIGINT NOT NULL PRIMARY KEY, "
            "tenant_id INT NOT NULL, status VARCHAR(16) NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, order_day DATE NOT NULL, "
            "region VARCHAR(8) NOT NULL, payload VARCHAR(64) NOT NULL, "
            "KEY idx_rg07_tenant_day (tenant_id, order_day)"
            ")"
        )
        for table, description, table_schema in (
            (self.business_table, "business", business_schema),
            (self.control_table, "control", control_schema),
        ):
            self._require_success(
                env.execute_sql(f"CREATE TABLE {self.db}.{table} ({table_schema}"),
                f"create RG07 {description} table {self.db}.{table}",
            )
        self._require_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.audit_table} ("
                "audit_id BIGINT NOT NULL PRIMARY KEY, order_id BIGINT NOT NULL, "
                "event_type VARCHAR(16) NOT NULL, event_day DATE NOT NULL, "
                "payload VARCHAR(64) NOT NULL, KEY idx_rg07_audit_order (order_id))"
            ),
            f"create RG07 audit table {self.db}.{self.audit_table}",
        )
        self._insert_order_rows(env, self.business_table, self.business_rows, "business")
        self._insert_order_rows(env, self.control_table, self.control_rows, "control")
        self._require_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.audit_table} "
                "(audit_id, order_id, event_type, event_day, payload) "
                f"SELECT n, MOD(n, {self.business_rows}) + 1, "
                "IF(MOD(n, 4)=0, 'SETTLED', 'CHECKED'), "
                "DATE_ADD('2026-01-01', INTERVAL MOD(n, 90) DAY), "
                "CONCAT('rg07-audit-', n) "
                f"FROM ({sequence_row_source(self.audit_rows)}) source"
            ),
            f"load RG07 audit rows={self.audit_rows}",
        )

    def _insert_order_rows(self, env, table: str, rows: int, label: str) -> None:
        payload_expression = (
            "CONCAT("
            + ", ".join(
                f"SHA2(CONCAT('rg07-{label}-{chunk}-', n), 256)"
                for chunk in range(_BUSINESS_PAYLOAD_CHUNKS)
            )
            + ")"
            if label == "business"
            else f"CONCAT('rg07-{label}-order-', n)"
        )
        self._require_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{table} "
                "(order_id, tenant_id, status, amount, order_day, region, payload) "
                f"SELECT n, MOD(n, 32), IF(MOD(n, 5)=0, 'PENDING', 'PAID'), "
                "CAST(MOD(n, 100000) / 100 AS DECIMAL(12,2)), "
                "DATE_ADD('2026-01-01', INTERVAL MOD(n, 90) DAY), "
                "CONCAT('r', LPAD(MOD(n, 8), 2, '0')), "
                f"{payload_expression} "
                f"FROM ({sequence_row_source(rows)}) source"
            ),
            f"load RG07 {label} order rows={rows}",
        )

    def _create_maintenance_tables(self, env) -> None:
        for table in self.maintenance_tables:
            self._require_success(
                env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"),
                f"clear RG07 maintenance table {self.db}.{table}",
            )
            self._require_success(
                env.execute_sql(
                    f"CREATE TABLE {self.db}.{table} ("
                    "maintenance_id BIGINT NOT NULL, "
                    "maintenance_class VARCHAR(16) NOT NULL, "
                    "payload VARCHAR(8192) NOT NULL, "
                    "KEY idx_rg07_maintenance_id (maintenance_id), "
                    "KEY idx_rg07_maintenance_class (maintenance_class)) "
                    "COMMENT='online maintenance ledger'"
                ),
                f"create RG07 maintenance table {self.db}.{table}",
            )
            self._require_success(
                env.execute_sql(
                    f"INSERT INTO {self.db}.{table} "
                    "(maintenance_id, maintenance_class, payload) "
                    "SELECT n, IF(MOD(n, 2)=0, 'ACTIVE', 'HOLD'), "
                    "REPEAT(CONCAT('rg07-maintenance-', n, '-'), 360) "
                    f"FROM ({sequence_row_source(self.maintenance_rows)}) source"
                ),
                f"load RG07 maintenance rows={self.maintenance_rows} table={self.db}.{table}",
            )

    def _create_empty_region_tables(self, env) -> None:
        for table in self.empty_region_tables:
            self._require_success(
                env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"),
                f"clear RG07 empty-region table {self.db}.{table}",
            )
            self._require_success(
                env.execute_sql(
                    f"CREATE TABLE {self.db}.{table} ("
                    "id BIGINT NOT NULL, payload VARCHAR(32) NOT NULL, "
                    "KEY idx_rg07_empty_id (id)) "
                    f"SHARD_ROW_ID_BITS = 2 PRE_SPLIT_REGIONS = {self.pre_split_regions}"
                ),
                f"create RG07 empty-region table {self.db}.{table}",
            )
            self._require_success(
                env.execute_sql(
                    f"INSERT INTO {self.db}.{table} VALUES (1, 'region-seed')"
                ),
                f"seed RG07 empty-region table {self.db}.{table}",
            )
            self._require_success(
                env.execute_sql(f"TRUNCATE TABLE {self.db}.{table}"),
                f"truncate RG07 empty-region table {self.db}.{table}",
            )

    def _wait_for_empty_regions(self, env) -> None:
        deadline = time.monotonic() + self.empty_region_wait_seconds
        last_health = None
        while time.monotonic() < deadline:
            last_health = self._metric(env, "region_health")["snapshot"]
            if int(last_health["empty_regions"]) >= self.minimum_empty_regions:
                return
            time.sleep(1)
        raise RuntimeError(
            "RG07 did not materialize the required Empty Regions before observability: "
            f"minimum_empty_regions={self.minimum_empty_regions}, "
            f"wait_seconds={self.empty_region_wait_seconds}, last_health={last_health!r}"
        )

    def _assert_tables_absent(self, env) -> None:
        placeholders = ", ".join(f"'{name}'" for name in self.owned_tables)
        payload = self._payload(
            env,
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_SCHEMA='{self.db}' AND TABLE_NAME IN ({placeholders})",
            "verify RG07 owned tables were removed",
        )
        if payload["result"]:
            raise RuntimeError(
                f"RG07 recovery left owned tables behind: expected_absent={self.owned_tables!r}, "
                f"observed={payload['result']!r}"
            )


class TidbResourceGovernanceEmptyRegionMergeBudgetScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_empty_region_merge_budget"
    description = (
        "Govern Empty Region heartbeat and merge scheduling pressure without changing live order data."
    )
    cases = (_CASE, _REDUCED_INVENTORY_CASE)

    def build_fault_plan(
        self,
        case: TidbResourceGovernanceEmptyRegionMergeBudgetCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernanceEmptyRegionMergeBudgetInjector,
                config={
                    "db": case.db,
                    "business_table": case.business_table,
                    "control_table": case.control_table,
                    "audit_table": case.audit_table,
                    "empty_table_prefix": case.empty_table_prefix,
                    "empty_table_count": case.empty_table_count,
                    "maintenance_table_prefix": case.maintenance_table_prefix,
                    "maintenance_table_count": case.maintenance_table_count,
                    "maintenance_rows": case.maintenance_rows,
                    "pre_split_regions": case.pre_split_regions,
                    "business_partition_count": case.business_partition_count,
                    "business_rows": case.business_rows,
                    "control_rows": case.control_rows,
                    "audit_rows": case.audit_rows,
                    "business_query": case.business_query,
                    "business_integrity_query": case.business_integrity_query,
                    "minimum_empty_regions": case.minimum_empty_regions,
                    "empty_region_wait_seconds": case.empty_region_wait_seconds,
                    "fault_pd_config": case.fault_pd_config,
                    "baseline_pd_config": case.baseline_pd_config,
                },
            ),
        )
