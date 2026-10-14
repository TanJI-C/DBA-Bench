from collections.abc import Mapping

from src.scenarios.tidb.resource_governance.contract import business_truth

from src.database.sql import execute_json_payload

from src.scenarios.tidb.common import BaseFaultInjector, FaultLifecycleContext, validate_sql_identifier

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.resource_governance.pd_api_security import (
    TidbResourceGovernancePdApiSecurityEvaluatorCase,
    TidbResourceGovernancePdApiSecurityStagedRoutesEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernancePdApiSecurityCase(TiDBScenarioCase):
    db: str
    account_table: str
    order_table: str
    event_table: str
    consumer_route_table: str
    account_rows: int
    order_rows: int
    event_rows: int
    consumer_route_data: tuple[tuple[object, ...], ...]
    consumer_route_rows: int
    pd_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernancePdApiSecurityForAccessHardeningScenarioCase(TidbResourceGovernancePdApiSecurityCase):
    pass


RG09_DB = "benchops_rg09"
RG09_ACCOUNTS = "rg09_accounts"
RG09_ORDERS = "rg09_orders"
RG09_EVENTS = "rg09_audit_events"
RG09_CONSUMER_ROUTES = "consumer_routes"
RG09_ACCOUNT_ROWS = 1000
RG09_ORDER_ROWS = 10000
RG09_EVENT_ROWS = 30000

RG09_CLUSTER_CONFIG_SQL = (
    "SELECT * FROM information_schema.cluster_config "
    "WHERE TYPE = 'pd' ORDER BY INSTANCE"
)
RG09_CLUSTER_INFO_SQL = (
    "SELECT TYPE, INSTANCE, VERSION, START_TIME, UPTIME "
    "FROM information_schema.cluster_info ORDER BY TYPE, INSTANCE"
)
RG09_CONSUMER_ROUTE_SQL = (
    f"SELECT route_id, consumer_name, endpoint_role, endpoint, state, history_mode, owner, "
    f"source_zone, path_scope, route_stage, last_seen "
    f"FROM {RG09_DB}.{RG09_CONSUMER_ROUTES} ORDER BY route_id"
)
RG09_CONSUMER_ROUTE_SUMMARY_SQL = (
    f"SELECT endpoint_role, state, history_mode, route_stage, source_zone, path_scope, COUNT(*) "
    f"FROM {RG09_DB}.{RG09_CONSUMER_ROUTES} "
    "GROUP BY endpoint_role, state, history_mode, route_stage, source_zone, path_scope "
    "ORDER BY endpoint_role, state, history_mode, route_stage, source_zone, path_scope"
)

RG09_CONSUMER_ROUTE_ROWS = (
    (1, "checkout-sql", "sql", "tidb-sql", "active", "none", "checkout-api", "app-vpc", "sql", "current", "2026-08-08 00:00:00"),
    (2, "checkout-sql", "sql", "tidb-sql-canary", "standby", "pending", "checkout-api", "app-vpc", "sql", "candidate", "2026-08-08 00:15:00"),
    (3, "control-session", "management", "pd-member-a", "active", "none", "platform-ops", "ops-vpc", "pd-client", "current", "2026-08-08 00:00:00"),
    (4, "control-session", "management", "pd-member-b", "standby", "pending", "platform-ops", "ops-vpc", "pd-client", "candidate", "2026-08-08 00:20:00"),
    (5, "portal-live", "dashboard", "pd-member-a", "active", "local", "merchant-dashboard", "dashboard-vpc", "dashboard", "current", "2026-08-08 00:00:00"),
    (6, "portal-live", "dashboard", "pd-member-c", "standby", "pending", "merchant-dashboard", "dashboard-vpc", "dashboard", "candidate", "2026-08-08 00:25:00"),
    (7, "portal-legacy", "dashboard", "pd-member-b", "retired", "exported", "merchant-dashboard", "dashboard-vpc", "dashboard", "retired", "2026-08-07 23:00:00"),
    (8, "search-legacy", "dashboard", "pd-member-c", "retired", "unknown", "search-console", "dashboard-vpc", "dashboard", "retired", "2026-08-07 22:00:00"),
    (9, "backup-runner", "data-movement", "pd-member-a", "active", "none", "backup-controller", "backup-vpc", "pd-client", "current", "2026-08-08 00:00:00"),
    (10, "backup-runner", "data-movement", "pd-member-c", "standby", "pending", "backup-controller", "backup-vpc", "pd-client", "candidate", "2026-08-08 00:30:00"),
    (11, "import-runner", "data-movement", "pd-member-b", "active", "none", "import-controller", "import-vpc", "pd-client", "current", "2026-08-08 00:00:00"),
    (12, "import-runner", "data-movement", "pd-member-a", "standby", "pending", "import-controller", "import-vpc", "pd-client", "candidate", "2026-08-08 00:35:00"),
    (13, "metrics-scrape", "metrics", "pd-member-c", "active", "none", "metrics-collector", "metrics-vpc", "metrics", "current", "2026-08-08 00:00:00"),
    (14, "metrics-scrape", "metrics", "pd-member-b", "standby", "pending", "metrics-collector", "metrics-vpc", "metrics", "candidate", "2026-08-08 00:40:00"),
    (15, "grafana-query", "metrics", "pd-member-c", "active", "none", "grafana", "analytics-vpc", "metrics", "current", "2026-08-08 00:00:00"),
    (16, "grafana-query", "metrics", "pd-member-a", "standby", "pending", "grafana", "analytics-vpc", "metrics", "candidate", "2026-08-08 00:45:00"),
    (17, "audit-console", "business", "tidb-sql", "active", "none", "audit-console", "audit-vpc", "sql", "current", "2026-08-08 00:00:00"),
    (18, "audit-console", "business", "tidb-sql-canary", "standby", "pending", "audit-console", "audit-vpc", "sql", "candidate", "2026-08-08 00:50:00"),
    (19, "health-review", "management", "pd-member-c", "active", "none", "health-auditor", "ops-vpc", "pd-client", "current", "2026-08-08 00:00:00"),
    (20, "health-review", "management", "pd-member-a", "standby", "pending", "health-auditor", "ops-vpc", "pd-client", "candidate", "2026-08-08 00:55:00"),
    (21, "schema-observer", "management", "pd-member-b", "retired", "none", "schema-observer", "tools-vpc", "pd-client", "retired", "2026-08-07 21:00:00"),
    (22, "schema-observer", "management", "pd-member-a", "retired", "exported", "schema-observer", "tools-vpc", "pd-client", "retired", "2026-08-07 20:00:00"),
    (23, "release-verifier", "data-movement", "pd-member-b", "retired", "exported", "release-ops", "release-vpc", "pd-client", "retired", "2026-08-07 19:00:00"),
    (24, "metrics-archive", "metrics", "pd-member-a", "retired", "unknown", "metrics-collector", "archive-vpc", "metrics", "retired", "2026-08-07 18:00:00"),
)


def rg09_reference_route_controls() -> list[dict[str, object]]:
    return rg09_route_controls(RG09_CONSUMER_ROUTE_ROWS)


def rg09_route_controls(
    rows: tuple[tuple[object, ...], ...],
) -> list[dict[str, object]]:
    controls = []
    for row in rows:
        route_id, consumer, role, endpoint, state, _, _, source_zone, path_scope, stage, _ = row
        if stage == "current":
            control = "keep this current route behind the selected boundary"
            validation = "verify the authorized consumer reaches the current endpoint"
        elif stage == "candidate":
            control = "keep this candidate disabled until staged health gates pass"
            validation = "validate the candidate separately before any cutover"
        else:
            control = "revoke this retired route and retain its audit history"
            validation = "confirm the retired endpoint is denied and history remains available"
        controls.append({
            "route_id": route_id,
            "consumer": consumer,
            "role": role,
            "endpoint": endpoint,
            "state": state,
            "stage": stage,
            "source_zone": source_zone,
            "path_scope": path_scope,
            "control": control,
            "validation": validation,
        })
    return controls


def _profile(name: str, sql: str, qps: float, tier: str, application_name: str) -> WorkloadProfile:
    return WorkloadProfile(
        name=name,
        sql=sql,
        qps=qps,
        tier=tier,
        application_name=application_name,
    )


RG09_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        _profile(
            "account_lookup",
            f"SELECT account_id, region, tier FROM {RG09_DB}.{RG09_ACCOUNTS} WHERE account_id IN (17, 271, 983)",
            0.45,
            "OLTP_CORE",
            "checkout-api",
        ),
        _profile(
            "order_lookup",
            f"SELECT order_id, status, amount FROM {RG09_DB}.{RG09_ORDERS} WHERE account_id = 271 ORDER BY order_id DESC LIMIT 20",
            0.35,
            "OLTP_CORE",
            "checkout-api",
        ),
        _profile(
            "region_rollup",
            f"SELECT a.region, COUNT(*), SUM(o.amount) FROM {RG09_DB}.{RG09_ACCOUNTS} AS a JOIN {RG09_DB}.{RG09_ORDERS} AS o ON o.account_id = a.account_id GROUP BY a.region",
            0.18,
            "REPORTING",
            "merchant-dashboard",
        ),
        _profile(
            "status_rollup",
            f"SELECT status, COUNT(*), SUM(amount) FROM {RG09_DB}.{RG09_ORDERS} GROUP BY status ORDER BY status",
            0.18,
            "REPORTING",
            "merchant-dashboard",
        ),
        _profile(
            "event_timeline",
            f"SELECT event_id, event_type, event_day, source FROM {RG09_DB}.{RG09_EVENTS} WHERE order_id BETWEEN 100 AND 160 ORDER BY event_id",
            0.25,
            "AUDIT_READ",
            "audit-console",
        ),
        _profile(
            "event_type_rollup",
            f"SELECT event_type, COUNT(*), MIN(event_day), MAX(event_day) FROM {RG09_DB}.{RG09_EVENTS} GROUP BY event_type",
            0.20,
            "AUDIT_READ",
            "audit-console",
        ),
        _profile(
            "event_source_rollup",
            f"SELECT source, COUNT(*) FROM {RG09_DB}.{RG09_EVENTS} GROUP BY source ORDER BY source",
            0.18,
            "AUDIT_READ",
            "risk-analytics",
        ),
        _profile(
            "daily_order_rollup",
            f"SELECT order_day, COUNT(*), SUM(amount) FROM {RG09_DB}.{RG09_ORDERS} GROUP BY order_day ORDER BY order_day",
            0.16,
            "OLAP_READ",
            "finance-rollup",
        ),
        _profile(
            "daily_event_rollup",
            f"SELECT event_day, COUNT(*) FROM {RG09_DB}.{RG09_EVENTS} GROUP BY event_day ORDER BY event_day",
            0.16,
            "OLAP_READ",
            "finance-rollup",
        ),
        _profile(
            "platform_snapshot",
            RG09_CLUSTER_CONFIG_SQL,
            0.28,
            "CONTROL_PLANE",
            "cluster-auditor",
        ),
        _profile(
            "platform_members",
            RG09_CLUSTER_INFO_SQL,
            0.28,
            "CONTROL_PLANE",
            "cluster-auditor",
        ),
        _profile(
            "ops_event_feed",
            "SELECT TIME, TYPE, LEVEL, MESSAGE FROM information_schema.cluster_log ORDER BY TIME DESC LIMIT 20",
            0.20,
            "CONTROL_PLANE",
            "ops-log-poller",
        ),
        _profile(
            "health_review",
            "SELECT RULE, ITEM, TYPE, INSTANCE, SEVERITY, DETAILS FROM information_schema.inspection_result ORDER BY SEVERITY, RULE LIMIT 30",
            0.18,
            "CONTROL_PLANE",
            "health-auditor",
        ),
        _profile(
            "workload_summary",
            "SELECT DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY FROM information_schema.cluster_statements_summary ORDER BY SUM_LATENCY DESC LIMIT 20",
            0.20,
            "OBSERVABILITY",
            "grafana-refresh",
        ),
        _profile(
            "latency_review",
            "SELECT INSTANCE, DIGEST, QUERY, QUERY_TIME FROM information_schema.cluster_slow_query ORDER BY TIME DESC LIMIT 20",
            0.18,
            "OBSERVABILITY",
            "slow-query-poller",
        ),
        _profile(
            "schema_status",
            f"SHOW TABLE STATUS FROM {RG09_DB} LIKE '{RG09_ACCOUNTS}'",
            0.16,
            "SCHEMA_OBSERVABILITY",
            "schema-observer",
        ),
        _profile(
            "access_path_review",
            f"SHOW INDEX FROM {RG09_DB}.{RG09_ORDERS}",
            0.16,
            "SCHEMA_OBSERVABILITY",
            "schema-observer",
        ),
        _profile(
            "audit_access_review",
            f"SHOW INDEX FROM {RG09_DB}.{RG09_EVENTS}",
            0.16,
            "SCHEMA_OBSERVABILITY",
            "schema-observer",
        ),
        _profile(
            "cache_maintenance_check",
            f"SELECT COUNT(*) FROM {RG09_DB}.dashboard_cache_missing",
            0.10,
            "OPERATIONS",
            "dashboard-cache-refresher",
        ),
        _profile(
            "backup_manifest_check",
            f"SELECT COUNT(*) FROM {RG09_DB}.br_manifest_missing",
            0.10,
            "OPERATIONS",
            "backup-verifier",
        ),
        _profile(
            "audit_archive_check",
            f"SELECT COUNT(*) FROM {RG09_DB}.audit_archive_missing",
            0.10,
            "OPERATIONS",
            "audit-retention-monitor",
        ),
        _profile(
            "route_inventory",
            RG09_CONSUMER_ROUTE_SQL,
            0.22,
            "CONTROL_PLANE",
            "platform-router",
        ),
        _profile(
            "route_state_rollup",
            RG09_CONSUMER_ROUTE_SUMMARY_SQL,
            0.18,
            "CONTROL_PLANE",
            "platform-router",
        ),
        _profile(
            "platform_health_snapshot",
            RG09_CLUSTER_INFO_SQL,
            0.20,
            "OPERATIONS",
            "service-health",
        ),
        _profile(
            "platform_config_refresh",
            RG09_CLUSTER_CONFIG_SQL,
            0.20,
            "OPERATIONS",
            "change-manager",
        ),
    ),
    worker_count=4,
    seed=20260802,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=12,
)


_RG09_CASE = TidbResourceGovernancePdApiSecurityForAccessHardeningScenarioCase(
    case_id="pd_api_access_hardening",
    reference_report={
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": [
                "Recommended primary control: firewall/iptables network allowlist on the PD client API, permitting only internal TiDB/TiKV, pd-ctl, BR, Lightning, Prometheus, and Grafana sources.",
                "The rollout uses a maintenance change window, validates one PD member and quorum before continuing, and keeps a rollback rule ready."
            ],
            "verification": [
                "Test an unauthenticated request to the PD API and require 403/denied/blocked, then use authenticated pd-ctl control with the authorized internal path.",
                "Verify cluster_info, PD leader/quorum, TiDB SQL business queries, BR backup/restore, TiDB Lightning, Dashboard, Prometheus, and Grafana after the allowlist change.",
                "Preserve Dashboard traffic visualization and historical search records; export or back up history before any alternate-port migration.",
                "Rollback the firewall rule if SQL, PD control, BR, Lightning, Dashboard, Prometheus, Grafana, leader, or quorum checks fail."
            ],
            "plan": {
                "primary_control": "network_allowlist",
                "consumer_controls": {
                    "pd_api": {"control": "allow internal management clients", "validation": "negative and positive access tests"},
                    "pd_control": {"control": "retain authorized control path", "validation": "authenticated control command succeeds"},
                    "dashboard": {"control": "keep the current service route", "validation": "live dashboard request succeeds"},
                    "br": {"control": "retain the backup route", "validation": "backup and restore smoke checks succeed"},
                    "lightning": {"control": "retain the import route", "validation": "precheck and import connectivity succeed"},
                    "prometheus": {"control": "retain metrics scrape route", "validation": "targets remain healthy"},
                    "grafana": {"control": "retain query route", "validation": "dashboard panels query successfully"},
                    "sql_business": {"control": "leave SQL path unchanged", "validation": "business truth is unchanged"},
                },
                "route_controls": rg09_reference_route_controls(),
                "access_validation": {
                    "unauthenticated_test": "unauthorized request is denied",
                    "authenticated_test": "authorized control request succeeds",
                    "health_gates": ["cluster health", "leader", "quorum", "SQL"],
                },
                "history": {
                    "disposition": "preserve",
                    "mitigation": "export history before any endpoint migration",
                },
                "rollout": {
                    "maintenance_window": True,
                    "availability_impact": "announce the change window",
                    "topology_guardrail": "validate one member and quorum before continuing",
                    "rollback_condition": "rollback when any dependency or health gate fails",
                },
            },
        },
        "summary": "The plan preserves authorized operations while closing the exposed management path.",
    },
    case_no=0,
    evaluator=TidbResourceGovernancePdApiSecurityEvaluatorCase,
    title="在不破坏在线业务、管理面与监控可达性的前提下制定访问加固方案。",
    alert=(
        "[Security Operations] 外部扫描器可以读取分布式数据库管理面的元数据，"
        "当前管理访问缺少可靠的边界。请先从真实拓扑、配置、健康指标、日志、业务 workload "
        "和 TiDB 知识库确认影响面，然后提交一份可执行的访问加固方案。"
        "方案必须在 outcome.plan 中给出一个主控制、所有消费者映射、每个观测 route identity 的控制与验证、"
        "负面/正面访问测试、"
        "变更窗口、拓扑健康门、回滚条件和历史处置。在线 SQL、管理控制、数据迁移、"
        "Dashboard 与监控路径都必须保持可达；不要直接重启健康组件或修改业务数据。"
    ),
    initial_state={
        "status": "management_plane_access_exposure",
        "topology": "distributed database with multiple management members",
        "dependent_paths": "online SQL, management control, data movement, dashboard, and monitoring",
    },
    expected_target={
        "status": "remediation_plan_ready",
        "primary_control": "TLS or network/port isolation or controlled PD replacement",
        "unauthenticated_api": "blocked",
        "authorized_operations": "verified",
        "business_and_dashboard": "preserved or explicitly disclosed",
    },
    background_workload=RG09_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=120,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.95664,
        reference_run_ids=(
            "reference-121__"
            "tidb_resource_governance_pd_api_security__pd_api_access_hardening__mock__r001",
        ),
    ),
    db=RG09_DB,
    account_table=RG09_ACCOUNTS,
    order_table=RG09_ORDERS,
    event_table=RG09_EVENTS,
    consumer_route_table=RG09_CONSUMER_ROUTES,
    account_rows=RG09_ACCOUNT_ROWS,
    order_rows=RG09_ORDER_ROWS,
    event_rows=RG09_EVENT_ROWS,
    consumer_route_data=RG09_CONSUMER_ROUTE_ROWS,
    consumer_route_rows=len(RG09_CONSUMER_ROUTE_ROWS),
    pd_count=3,
)

RG09_STAGED_ROUTE_ROWS = tuple(
    row for row in RG09_CONSUMER_ROUTE_ROWS if int(row[0]) not in {21, 22, 23, 24}
)

_RG09_STAGED_CASE = replace(
    _RG09_CASE,
    case_id="pd_api_staged_route_hardening",
    case_no=1,
    evaluator=TidbResourceGovernancePdApiSecurityStagedRoutesEvaluatorCase,
    title="Harden the PD API boundary after reducing stale route inventory.",
    alert=(
        "[Security Operations] The PD client API is reachable beyond the intended management boundary, "
        "and a staged route inventory contains both active and candidate paths. Correlate current route "
        "identity, topology, access tests, and dependency health; submit an executable boundary-hardening "
        "plan that preserves authorized SQL, control, backup, import, dashboard, and monitoring paths."
    ),
    initial_state={
        "status": "management_plane_access_exposure",
        "topology": "distributed database with active and candidate management routes",
        "route_inventory": "stale retired routes require explicit disposition",
        "dependent_paths": "online SQL, management control, data movement, dashboard, and monitoring",
    },
    expected_target={
        **_RG09_CASE.expected_target,
        "route_inventory": "all observed active/candidate routes mapped; stale routes explicitly disposed",
    },
    consumer_route_data=RG09_STAGED_ROUTE_ROWS,
    consumer_route_rows=len(RG09_STAGED_ROUTE_ROWS),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.951691,
        reference_run_ids=(
            "reference-275__tidb_resource_governance_pd_api_security__"
            "pd_api_staged_route_hardening__mock__r001",
        ),
    ),
)


class TidbResourceGovernancePdApiSecurityInjector(BaseFaultInjector):
    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_tables(context.env)
        self._load_data(context.env)
        self._verify_fault_state(context.env, context.case)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env, context.case)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_fault_state(context.env, context.case)
        return {
            "pd_configuration": self._pd_configuration(context.env),
            "cluster_info": self._execute(
                context.env,
                "SELECT TYPE, INSTANCE, VERSION, START_TIME, UPTIME "
                "FROM information_schema.cluster_info ORDER BY TYPE, INSTANCE",
                "capture RG09 cluster info",
            )["result"],
            "consumer_routes": self._execute(
                context.env,
                RG09_CONSUMER_ROUTE_SQL,
                "capture RG09 consumer routes",
            )["result"],
            "business_truth": business_truth(context.env, context.case),
            "table_status": self._execute(
                context.env,
                f"SHOW TABLE STATUS FROM {self.db}",
                "capture RG09 business table status",
            )["result"],
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        return None

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        for table in (
            self.consumer_route_table,
            self.event_table,
            self.order_table,
            self.account_table,
        ):
            self._execute(context.env, f"DROP TABLE IF EXISTS {self.db}.{table}", f"drop RG09 table {table}")
        self._execute(context.env, f"DROP DATABASE IF EXISTS {self.db}", f"drop RG09 database {self.db}")

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.account_table = validate_sql_identifier(str(config["account_table"]), "account_table")
        self.order_table = validate_sql_identifier(str(config["order_table"]), "order_table")
        self.event_table = validate_sql_identifier(str(config["event_table"]), "event_table")
        self.consumer_route_table = validate_sql_identifier(
            str(config["consumer_route_table"]),
            "consumer_route_table",
        )
        self.account_rows = int(config["account_rows"])
        self.order_rows = int(config["order_rows"])
        self.event_rows = int(config["event_rows"])
        self.consumer_route_data = tuple(
            tuple(row) for row in config["consumer_route_data"]
        )
        self.consumer_route_rows = int(config["consumer_route_rows"])
        self.pd_count = int(config["pd_count"])

    @staticmethod
    def _execute(env, sql: str, context: str) -> dict:
        return execute_json_payload(env.execute_sql, sql, context)

    @staticmethod
    def _sql_value(value: object) -> str:
        if isinstance(value, str):
            return "'" + value.replace("'", "''") + "'"
        return str(value)

    def _insert_batches(self, env, table: str, columns: tuple[str, ...], rows: list[tuple[object, ...]], context: str) -> None:
        rendered_columns = ", ".join(columns)
        for start in range(0, len(rows), 1000):
            batch = rows[start:start + 1000]
            values = ", ".join(
                "(" + ", ".join(self._sql_value(value) for value in row) + ")"
                for row in batch
            )
            self._execute(
                env,
                f"INSERT INTO {self.db}.{table} ({rendered_columns}) VALUES {values}",
                f"{context}: start={start}",
            )

    def _create_tables(self, env) -> None:
        self._execute(env, f"CREATE DATABASE IF NOT EXISTS {self.db}", f"create RG09 database {self.db}")
        for table in (self.event_table, self.order_table, self.account_table):
            self._execute(env, f"DROP TABLE IF EXISTS {self.db}.{table}", f"clear RG09 table {table}")
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.account_table} ("
            "account_id BIGINT PRIMARY KEY, region VARCHAR(16) NOT NULL, tier INT NOT NULL, "
            "created_day DATE NOT NULL, KEY idx_account_region (region, account_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            "create RG09 accounts",
        )
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.order_table} ("
            "order_id BIGINT PRIMARY KEY, account_id BIGINT NOT NULL, order_day DATE NOT NULL, "
            "status VARCHAR(16) NOT NULL, amount DECIMAL(12,2) NOT NULL, "
            "KEY idx_order_account (account_id, order_id), KEY idx_order_day (order_day, status)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            "create RG09 orders",
        )
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.event_table} ("
            "event_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, event_type VARCHAR(16) NOT NULL, "
            "event_day DATE NOT NULL, source VARCHAR(24) NOT NULL, payload VARCHAR(64) NOT NULL, "
            "KEY idx_event_order (order_id, event_id), KEY idx_event_day (event_day, event_type)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            "create RG09 audit events",
        )
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.consumer_route_table} ("
            "route_id INT PRIMARY KEY, consumer_name VARCHAR(32) NOT NULL, "
            "endpoint_role VARCHAR(24) NOT NULL, endpoint VARCHAR(64) NOT NULL, "
            "state VARCHAR(16) NOT NULL, history_mode VARCHAR(16) NOT NULL, "
            "owner VARCHAR(32) NOT NULL, source_zone VARCHAR(32) NOT NULL, "
            "path_scope VARCHAR(32) NOT NULL, route_stage VARCHAR(16) NOT NULL, "
            "last_seen DATETIME NOT NULL, "
            "KEY idx_route_role_state (endpoint_role, state), "
            "KEY idx_route_stage (route_stage, last_seen)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            "create RG09 consumer route inventory",
        )

    def _load_data(self, env) -> None:
        regions = ("north", "south", "east", "west", "central")
        accounts = [
            (
                account_id,
                regions[account_id % len(regions)],
                (account_id * 17) % 11,
                f"2025-12-{(account_id % 28) + 1:02d}",
            )
            for account_id in range(1, self.account_rows + 1)
        ]
        orders = [
            (
                order_id,
                ((order_id - 1) % self.account_rows) + 1,
                f"2026-01-{(order_id % 28) + 1:02d}",
                ("new", "paid", "shipped", "closed")[order_id % 4],
                f"{((order_id * 7919) % 100000) / 100:.2f}",
            )
            for order_id in range(1, self.order_rows + 1)
        ]
        event_types = ("created", "authorized", "captured", "reviewed", "closed")
        sources = ("checkout", "risk", "settlement", "dashboard")
        events = [
            (
                event_id,
                ((event_id - 1) % self.order_rows) + 1,
                event_types[event_id % len(event_types)],
                f"2026-02-{(event_id % 28) + 1:02d}",
                sources[event_id % len(sources)],
                f"event-{event_id % 257:03d}",
            )
            for event_id in range(1, self.event_rows + 1)
        ]
        self._insert_batches(
            env,
            self.account_table,
            ("account_id", "region", "tier", "created_day"),
            accounts,
            "load RG09 accounts",
        )
        self._insert_batches(
            env,
            self.order_table,
            ("order_id", "account_id", "order_day", "status", "amount"),
            orders,
            "load RG09 orders",
        )
        self._insert_batches(
            env,
            self.event_table,
            ("event_id", "order_id", "event_type", "event_day", "source", "payload"),
            events,
            "load RG09 audit events",
        )
        self._insert_batches(
            env,
            self.consumer_route_table,
            (
                "route_id",
                "consumer_name",
                "endpoint_role",
                "endpoint",
                "state",
                "history_mode",
                "owner",
                "source_zone",
                "path_scope",
                "route_stage",
                "last_seen",
            ),
            list(self.consumer_route_data),
            "load RG09 consumer route inventory",
        )
        for table in (
            self.account_table,
            self.order_table,
            self.event_table,
            self.consumer_route_table,
        ):
            self._execute(env, f"ANALYZE TABLE {self.db}.{table}", f"analyze RG09 table {table}")

    def _pd_configuration(self, env) -> list:
        return self._execute(
            env,
            "SELECT * FROM information_schema.cluster_config "
            "WHERE TYPE = 'pd' ORDER BY INSTANCE",
            "capture RG09 PD configuration",
        )["result"]

    def _verify_fault_state(self, env, case) -> None:
        pd_rows = self._pd_configuration(env)
        cluster_rows = self._execute(
            env,
            "SELECT TYPE, INSTANCE FROM information_schema.cluster_info "
            "WHERE TYPE = 'pd' ORDER BY INSTANCE",
            "verify RG09 PD topology",
        )["result"]
        instances = {str(row[1]) for row in cluster_rows if len(row) >= 2}
        http_values = [str(row[3]).casefold() for row in pd_rows if len(row) >= 4]
        if len(instances) != self.pd_count:
            raise RuntimeError(
                f"RG09 PD topology mismatch: expected={self.pd_count}, "
                f"actual_instances={sorted(instances)!r}, cluster_info_rows={cluster_rows!r}"
            )
        if not any("http://" in value and "https://" not in value for value in http_values):
            raise RuntimeError(f"RG09 PD API exposure is not observable in cluster_config: rows={pd_rows!r}")
        for table, expected_rows in (
            (self.account_table, self.account_rows),
            (self.order_table, self.order_rows),
            (self.event_table, self.event_rows),
            (self.consumer_route_table, self.consumer_route_rows),
        ):
            row = self._execute(
                env,
                f"SELECT COUNT(*) FROM {self.db}.{table}",
                f"verify RG09 row count: table={table}",
            )["result"][0]
            if int(row[0]) != expected_rows:
                raise RuntimeError(
                    f"RG09 table row count mismatch: table={self.db}.{table}, "
                    f"expected={expected_rows}, actual={row[0]}"
                )


class TidbResourceGovernancePdApiSecurityScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_pd_api_security"
    description = (
        "Plan PD API access hardening while preserving TiDB SQL, PD control, Dashboard, backup, import, and monitoring paths."
    )
    cases = (_RG09_CASE, _RG09_STAGED_CASE)

    def build_fault_plan(
        self,
        case: TidbResourceGovernancePdApiSecurityCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernancePdApiSecurityInjector,
                config={
                    "db": case.db,
                    "account_table": case.account_table,
                    "order_table": case.order_table,
                    "event_table": case.event_table,
                    "consumer_route_table": case.consumer_route_table,
                    "account_rows": case.account_rows,
                    "order_rows": case.order_rows,
                    "event_rows": case.event_rows,
                    "consumer_route_data": case.consumer_route_data,
                    "consumer_route_rows": case.consumer_route_rows,
                    "pd_count": case.pd_count,
                },
            ),
        )
