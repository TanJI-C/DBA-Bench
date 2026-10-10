from dataclasses import dataclass

from src.scenarios.evaluation.tidb.business_change.rolling_upgrade import (
    TidbBusinessChangeRollingUpgradeForRollingUpgrade6_5To7_5EvaluatorCase,
    TidbBusinessChangeRollingUpgradeForRollingUpgrade7_5To8_1EvaluatorCase,
)
from src.scenarios.evaluation.protocol import structured_reference_report
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V6_5_0, TIDB_V7_5_0, TIDB_V8_1_0, tidb_runtime


def _business_workload(
    table: str,
    archive_table: str,
    database: str = "benchops",
) -> tuple[WorkloadProfile, ...]:
    return (
        WorkloadProfile(
            name="orders_api_recent_lookup",
            sql=(
                f"SELECT event_id, event_type, amount FROM {table} "
                "WHERE tenant_id = 17 ORDER BY event_time DESC LIMIT 32"
            ),
            qps=0.38,
            tier="LIGHT",
            application_name="orders-api",
        ),
        WorkloadProfile(
            name="payment_reconciliation_rollup",
            sql=(
                f"SELECT event_type, COUNT(*), SUM(amount) FROM {table} "
                "GROUP BY event_type ORDER BY event_type"
            ),
            qps=0.24,
            tier="MEDIUM",
            application_name="payment-reconciliation",
        ),
        WorkloadProfile(
            name="tenant_revenue_dashboard",
            sql=(
                f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {table} "
                "GROUP BY tenant_id ORDER BY SUM(amount) DESC LIMIT 24"
            ),
            qps=0.22,
            tier="MEDIUM",
            application_name="tenant-dashboard",
        ),
        WorkloadProfile(
            name="risk_review_queue_preview",
            sql=(
                f"SELECT event_id, tenant_id, amount FROM {table} "
                "WHERE event_type = 'REVIEW' ORDER BY event_time DESC LIMIT 48"
            ),
            qps=0.2,
            tier="MEDIUM",
            application_name="risk-review-queue",
        ),
        WorkloadProfile(
            name="store_status_dashboard_decoy",
            sql=(
                "SELECT STORE_ID, STORE_STATE_NAME, REGION_COUNT, LEADER_COUNT "
                "FROM information_schema.tikv_store_status ORDER BY STORE_ID"
            ),
            qps=0.32,
            tier="LIGHT",
            application_name="capacity-dashboard",
        ),
        WorkloadProfile(
            name="cluster_version_audit_decoy",
            sql=(
                "SELECT TYPE, INSTANCE, VERSION FROM information_schema.cluster_info "
                "ORDER BY TYPE, INSTANCE"
            ),
            qps=0.28,
            tier="LIGHT",
            application_name="release-audit",
        ),
        WorkloadProfile(
            name="ddl_owner_decoy",
            sql="SELECT OWNER_ID, OWNER_IP, OWNER_PORT FROM mysql.tidb_ddl_owner",
            qps=0.18,
            tier="LIGHT",
            application_name="schema-controller",
        ),
        WorkloadProfile(
            name="statistics_health_decoy",
            sql=(
                "SELECT TABLE_SCHEMA, TABLE_NAME, HEALTH, LAST_UPDATE "
                f"FROM information_schema.tables WHERE TABLE_SCHEMA = '{database}' "
                "ORDER BY TABLE_NAME"
            ),
            qps=0.18,
            tier="LIGHT",
            application_name="statistics-audit",
        ),
        WorkloadProfile(
            name="business_checksum_audit",
            sql=(
                f"SELECT COUNT(*), CAST(SUM(amount * 100) AS SIGNED), "
                f"CAST(SUM(tenant_id) AS SIGNED) FROM {table}"
            ),
            qps=0.14,
            tier="MEDIUM",
            application_name="business-integrity-audit",
        ),
        WorkloadProfile(
            name="schema_index_catalog_decoy",
            sql=(
                "SELECT TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, COLUMN_NAME, SEQ_IN_INDEX "
                f"FROM information_schema.statistics WHERE TABLE_SCHEMA = '{database}' "
                "ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX"
            ),
            qps=0.12,
            tier="LIGHT",
            application_name="schema-catalog",
        ),
        WorkloadProfile(
            name="column_collation_catalog_decoy",
            sql=(
                "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, COLLATION_NAME, DATA_TYPE "
                f"FROM information_schema.columns WHERE TABLE_SCHEMA = '{database}' "
                "ORDER BY TABLE_NAME, COLUMN_NAME"
            ),
            qps=0.1,
            tier="LIGHT",
            application_name="collation-audit",
        ),
        WorkloadProfile(
            name="processlist_snapshot_decoy",
            sql=(
                "SELECT ID, USER, DB, COMMAND, TIME, STATE "
                "FROM information_schema.processlist ORDER BY TIME DESC LIMIT 32"
            ),
            qps=0.1,
            tier="LIGHT",
            application_name="session-audit",
        ),
        WorkloadProfile(
            name="tidb_variable_audit_decoy",
            sql=(
                "SELECT VARIABLE_NAME, VARIABLE_VALUE FROM mysql.tidb "
                "WHERE VARIABLE_NAME IN ('new_collation_enabled', 'tidb_server_version', "
                "'tikv_gc_safe_point', 'tikv_gc_life_time')"
            ),
            qps=0.08,
            tier="LIGHT",
            application_name="compatibility-audit",
        ),
        WorkloadProfile(
            name="cluster_info_repeat_decoy",
            sql=(
                "SELECT TYPE, INSTANCE, VERSION FROM information_schema.cluster_info "
                "ORDER BY TYPE, INSTANCE"
            ),
            qps=0.1,
            tier="LIGHT",
            application_name="release-audit-secondary",
        ),
        WorkloadProfile(
            name="store_region_repeat_decoy",
            sql=(
                "SELECT STORE_ID, STORE_STATE_NAME, REGION_COUNT, LEADER_COUNT "
                "FROM information_schema.tikv_store_status ORDER BY STORE_ID"
            ),
            qps=0.08,
            tier="LIGHT",
            application_name="capacity-audit-secondary",
        ),
        WorkloadProfile(
            name="table_cardinality_decoy",
            sql=(
                "SELECT TABLE_NAME, TABLE_ROWS, AVG_ROW_LENGTH, DATA_LENGTH, UPDATE_TIME "
                f"FROM information_schema.tables WHERE TABLE_SCHEMA = '{database}' "
                "ORDER BY TABLE_NAME"
            ),
            qps=0.08,
            tier="LIGHT",
            application_name="cardinality-audit",
        ),
        WorkloadProfile(
            name="analyze_job_history_decoy",
            sql=(
                "SELECT JOB_ID, TABLE_SCHEMA, TABLE_NAME, STATE "
                "FROM mysql.analyze_jobs ORDER BY JOB_ID DESC LIMIT 16"
            ),
            qps=0.08,
            tier="LIGHT",
            application_name="statistics-history",
        ),
        WorkloadProfile(
            name="archive_orders_recent_lookup_decoy",
            sql=(
                f"SELECT event_id, event_type, amount FROM {archive_table} "
                "WHERE tenant_id = 17 ORDER BY event_time DESC LIMIT 32"
            ),
            qps=0.26,
            tier="LIGHT",
            application_name="legacy-orders-api",
        ),
        WorkloadProfile(
            name="archive_payment_reconciliation_decoy",
            sql=(
                f"SELECT event_type, COUNT(*), SUM(amount) FROM {archive_table} "
                "GROUP BY event_type ORDER BY event_type"
            ),
            qps=0.18,
            tier="MEDIUM",
            application_name="legacy-reconciliation",
        ),
        WorkloadProfile(
            name="current_archive_consistency_decoy",
            sql=(
                f"SELECT COUNT(*), SUM(current_events.amount), SUM(archive_events.amount) "
                f"FROM {table} AS current_events JOIN {archive_table} AS archive_events "
                "ON archive_events.event_id = current_events.event_id"
            ),
            qps=0.1,
            tier="MEDIUM",
            application_name="ledger-consistency-audit",
        ),
        WorkloadProfile(
            name="event_hourly_rollup_decoy",
            sql=(
                f"SELECT HOUR(event_time), event_type, COUNT(*), SUM(amount) FROM {table} "
                "GROUP BY HOUR(event_time), event_type ORDER BY HOUR(event_time), event_type"
            ),
            qps=0.1,
            tier="MEDIUM",
            application_name="operations-hourly-rollup",
        ),
        WorkloadProfile(
            name="payload_search_decoy",
            sql=(
                f"SELECT event_id, tenant_id FROM {table} "
                "WHERE payload LIKE '%order-payload-00%' ORDER BY event_id DESC LIMIT 64"
            ),
            qps=0.14,
            tier="MEDIUM",
            application_name="fraud-payload-search",
        ),
        WorkloadProfile(
            name="statistics_meta_history_decoy",
            sql=(
                "SELECT table_id, version, modify_count, count FROM mysql.stats_meta "
                "ORDER BY version DESC LIMIT 16"
            ),
            qps=0.08,
            tier="LIGHT",
            application_name="statistics-history-secondary",
        ),
        WorkloadProfile(
            name="gc_safepoint_compatibility_decoy",
            sql=(
                "SELECT VARIABLE_NAME, VARIABLE_VALUE FROM mysql.tidb "
                "WHERE VARIABLE_NAME IN ('tikv_gc_safe_point', 'tikv_gc_life_time', "
                "'tidb_enable_async_commit', 'tidb_enable_1pc')"
            ),
            qps=0.06,
            tier="LIGHT",
            application_name="storage-compatibility-audit",
        ),
        WorkloadProfile(
            name="partition_catalog_decoy",
            sql=(
                "SELECT TABLE_SCHEMA, TABLE_NAME, PARTITION_NAME, PARTITION_METHOD, TABLE_ROWS "
                "FROM information_schema.partitions WHERE TABLE_SCHEMA = 'benchops' "
                "ORDER BY TABLE_NAME, PARTITION_NAME"
            ),
            qps=0.08,
            tier="LIGHT",
            application_name="partition-catalog",
        ),
        WorkloadProfile(
            name="region_peer_catalog_decoy",
            sql=(
                "SELECT REGION_ID, PEER_ID, STORE_ID, IS_LEARNER "
                "FROM information_schema.tikv_region_peers LIMIT 64"
            ),
            qps=0.08,
            tier="LIGHT",
            application_name="region-peer-audit",
        ),
        WorkloadProfile(
            name="statement_summary_decoy",
            sql=(
                "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY "
                "FROM information_schema.cluster_statements_summary "
                "ORDER BY SUM_LATENCY DESC LIMIT 16"
            ),
            qps=0.08,
            tier="MEDIUM",
            application_name="statement-summary-audit",
        ),
        WorkloadProfile(
            name="sql_binding_decoy",
            sql="SHOW GLOBAL BINDINGS",
            qps=0.06,
            tier="LIGHT",
            application_name="sql-binding-audit",
        ),
        WorkloadProfile(
            name="resource_group_decoy",
            sql=(
                "SELECT * FROM information_schema.resource_groups "
                "ORDER BY NAME LIMIT 16"
            ),
            qps=0.06,
            tier="LIGHT",
            application_name="resource-group-audit",
        ),
        WorkloadProfile(
            name="ddl_history_decoy",
            sql="SELECT * FROM mysql.ddl_job_history ORDER BY job_id DESC LIMIT 16",
            qps=0.06,
            tier="LIGHT",
            application_name="ddl-history-audit",
        ),
        WorkloadProfile(
            name="gc_delete_range_decoy",
            sql="SELECT * FROM mysql.gc_delete_range ORDER BY job_id DESC LIMIT 16",
            qps=0.06,
            tier="LIGHT",
            application_name="gc-delete-range-audit",
        ),
        WorkloadProfile(
            name="analyze_jobs_catalog_decoy",
            sql="SELECT * FROM mysql.analyze_jobs ORDER BY table_id LIMIT 16",
            qps=0.06,
            tier="LIGHT",
            application_name="analyze-job-audit",
        ),
        WorkloadProfile(
            name="user_privilege_catalog_decoy",
            sql=(
                "SELECT User, Host, plugin FROM mysql.user "
                "ORDER BY User, Host LIMIT 32"
            ),
            qps=0.05,
            tier="LIGHT",
            application_name="privilege-audit",
        ),
        WorkloadProfile(
            name="session_variable_catalog_decoy",
            sql=(
                "SELECT VARIABLE_NAME, VARIABLE_VALUE "
                "FROM performance_schema.global_variables "
                "WHERE VARIABLE_NAME LIKE 'tidb_%' LIMIT 32"
            ),
            qps=0.05,
            tier="LIGHT",
            application_name="session-variable-audit",
        ),
        WorkloadProfile(
            name="placement_policy_decoy",
            sql="SELECT * FROM mysql.tidb_placement_policy LIMIT 16",
            qps=0.05,
            tier="LIGHT",
            application_name="placement-policy-audit",
        ),
        WorkloadProfile(
            name="schema_usage_decoy",
            sql="SELECT * FROM mysql.schema_index_usage LIMIT 16",
            qps=0.05,
            tier="LIGHT",
            application_name="schema-usage-audit",
        ),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeRollingUpgradeForRollingUpgrade6_5To7_5ScenarioCase(TiDBScenarioCase):
    database: str
    table: str
    row_count: int
    expected_amount_cents: int
    expected_tenant_sum: int
    source_version: str
    target_version: str
    latency_slo_ms: float
    reference_evidence_counts: tuple[tuple[str, int, int], ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeRollingUpgradeForRollingUpgrade7_5To8_1ScenarioCase(
    TidbBusinessChangeRollingUpgradeForRollingUpgrade6_5To7_5ScenarioCase
):
    pass


_CASE = TidbBusinessChangeRollingUpgradeForRollingUpgrade6_5To7_5ScenarioCase(
    case_id="rolling_upgrade_6_5_to_7_5",
    reference_report=structured_reference_report(
        case_id="rolling_upgrade_6_5_to_7_5",
        factors=(),
        changes=(
            "completed compatibility precheck, backup, and PD TiKV TiDB rolling upgrade from v6.5.0 to v7.5.0",
            "kept the business checksum and RPO at zero while reconnecting TiDB sessions",
        ),
        verification=(
            "before and after canary semantic results match on both TiDB endpoints",
            "Prometheus targets are covered and query p95 stays below the 250ms SLO",
            "rollback is bounded by the v6.5.0 backup with RPO=0",
        ),
        summary="The reference path completed the rolling upgrade and verified business continuity.",
    ),
    case_no=0,
    evaluator=TidbBusinessChangeRollingUpgradeForRollingUpgrade6_5To7_5EvaluatorCase,
    title="Online TiDB 6.5 to 7.5 rolling upgrade with business compatibility acceptance.",
    alert=(
        "[CHANGE] 订单平台计划在不停服窗口内把四 PD、九 TiKV、五 TiDB 从 v6.5.0 升级到 v7.5.0。"
        "前台读写必须持续可用，不能直接 stop 集群、不能修改业务表数据。请先完成升级前健康检查、"
        "可回退的备份/恢复证据和性能基线，再按 PD、TiKV、TiDB 的安全滚动顺序升级；TiKV 节点需要先"
        "迁移 leader，TiDB 节点重启后必须确认业务会话重新连接。升级过程中要关注 DDL owner、"
        "server-version、new collation 和统计信息等 6.5→7.5 兼容性边界。"
        "升级完成不能只看版本号：必须逐个通过业务 canary 的结果语义对比、前台查询 p95 250ms SLO、"
        "Prometheus 全组件 target 覆盖和 RPO=0 的回退决策，然后提交变更报告。"
    ),
    initial_state={
        "source_version": "v6.5.0",
        "target_version": "v7.5.0",
        "pd_nodes": 4,
        "tikv_nodes": 9,
        "tidb_nodes": 5,
        "online_business_queries": True,
        "active_ddl": False,
        "active_backup_or_restore": False,
        "business_data_mutation_allowed": False,
    },
    expected_target={
        "cluster_version": "v7.5.0",
        "component_order": ("pd", "tikv", "tidb"),
        "business_semantics_unchanged": True,
        "monitoring_targets_up": True,
        "rpo": "0",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_business_workload(
            "benchops.admission_events",
            "benchops.admission_events_archive",
        ),
        worker_count=16,
        seed=0xBC01075,
        warmup_seconds=8,
    ),
    runtime=tidb_runtime(
        release=TIDB_V6_5_0,
        upgrade_release=TIDB_V7_5_0,
        # 3/5/3 与 7_5_to_8_1 对齐：21 容器的隔离引导在该宿主上无法稳定完成，
        # 滚动升级语义（逐组件升级 + 前后 canary）不受影响。
        pd_count=3,
        tikv_count=5,
        tidb_count=3,
        sql_timeout_seconds=180,
        pd_cpu_limit=2.0,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.959142,
        reference_run_ids=(
            "reference-79__"
            "tidb_business_change_rolling_upgrade__rolling_upgrade_6_5_to_7_5__"
            "mock__r001",
        ),
    ),
    database="benchops",
    table="admission_events",
    row_count=12000,
    expected_amount_cents=358280600,
    expected_tenant_sum=772560,
    source_version="v6.5.0",
    target_version="v7.5.0",
    latency_slo_ms=250.0,
    reference_evidence_counts=(
        ("execute_sql(information_schema.cluster_info)", 7, 118),
        ("compatibility_variables", 8, 0),
        ("business_canary", 2, 688),
        ("backup_checksum", 1, 0),
        ("component_rollout", 2, 16),
        ("execute_sql(workload activity history)", 2, 18),
        ("query_latency", 8, 54),
        ("manage_cluster(service/list)", 0, 20),
        ("manage_cluster(store/region/operator)", 9, 6),
        ("disk_io", 0, 1),
        ("monitoring", 1, 18),
    ),
)


_BILLING_CASE = TidbBusinessChangeRollingUpgradeForRollingUpgrade7_5To8_1ScenarioCase(
    case_id="rolling_upgrade_7_5_to_8_1",
    reference_report=structured_reference_report(
        case_id="rolling_upgrade_7_5_to_8_1",
        factors=(
            "the smaller billing topology still requires component-order and leader-transfer evidence",
            "v8.1 compatibility must be checked against the billing canary rather than the release label alone",
        ),
        changes=(
            "completed compatibility precheck, backup, and PD TiKV TiDB rolling upgrade from v7.5.0 to v8.1.0",
            "preserved billing-event checksum and RPO=0 while reconnecting TiDB sessions",
        ),
        verification=(
            "before and after billing canary semantic results match on every TiDB endpoint",
            "monitoring coverage and query p95 remain within the published SLO",
            "rollback remains bounded by the v7.5.0 backup with RPO=0",
        ),
        summary="The billing rolling-upgrade reference path completed the version transition and business acceptance.",
    ),
    case_no=1,
    evaluator=TidbBusinessChangeRollingUpgradeForRollingUpgrade7_5To8_1EvaluatorCase,
    title="Online TiDB 7.5 to 8.1 rolling upgrade with billing compatibility acceptance.",
    alert=(
        "[CHANGE] 账单平台计划在不停服窗口内把三 PD、五 TiKV、三 TiDB 从 v7.5.0 升级到 v8.1.0。"
        "前台读写必须持续可用，不能直接 stop 集群、不能修改 billing 业务表数据。请完成升级前健康检查、"
        "可回退备份和性能基线，再按 PD、TiKV、TiDB 的安全滚动顺序升级；TiKV 先迁移 leader，TiDB 重启后"
        "确认业务会话重新连接。升级完成要核对兼容性、billing canary 语义、Prometheus target 覆盖、250ms p95"
        "和 RPO=0 回退边界。"
    ),
    initial_state={
        "source_version": "v7.5.0",
        "target_version": "v8.1.0",
        "pd_nodes": 3,
        "tikv_nodes": 5,
        "tidb_nodes": 3,
        "online_business_queries": True,
        "active_ddl": False,
        "active_backup_or_restore": False,
        "business_data_mutation_allowed": False,
    },
    expected_target={
        "cluster_version": "v8.1.0",
        "component_order": ("pd", "tikv", "tidb"),
        "business_semantics_unchanged": True,
        "monitoring_targets_up": True,
        "rpo": "0",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_business_workload(
            "benchops_bc01.billing_events",
            "benchops_bc01.billing_events_archive",
            "benchops_bc01",
        ),
        worker_count=10,
        seed=0xBC0181,
        warmup_seconds=6,
    ),
    runtime=tidb_runtime(
        release=TIDB_V7_5_0,
        upgrade_release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=5,
        tidb_count=3,
        sql_timeout_seconds=180,
        pd_cpu_limit=2.0,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.849544,
        reference_run_ids=(
            "tidb-reference-11__"
            "tidb_business_change_rolling_upgrade__rolling_upgrade_7_5_to_8_1__"
            "mock__r001",
        ),
    ),
    database="benchops_bc01",
    table="billing_events",
    row_count=8000,
    expected_amount_cents=238857100,
    expected_tenant_sum=514016,
    source_version="v7.5.0",
    target_version="v8.1.0",
    latency_slo_ms=250.0,
    reference_evidence_counts=(
        ("execute_sql(information_schema.cluster_info)", 6, 30),
        ("compatibility_variables", 6, 0),
        ("business_canary", 2, 90),
        ("backup_checksum", 1, 0),
        ("component_rollout", 2, 10),
        ("query_latency", 6, 24),
        ("manage_cluster(store/region/operator)", 5, 4),
        ("monitoring", 1, 12),
        ("same-window sibling release evidence", 3, 22),
    ),
)


class TidbBusinessChangeRollingUpgradeScenario(TiDBScenario):
    scenario_id = "tidb_business_change_rolling_upgrade"
    description = "Online TiDB 6.5 to 7.5 rolling upgrade with business compatibility acceptance."
    cases = (_CASE, _BILLING_CASE)

    def build_fault_plan(
        self,
        case: TidbBusinessChangeRollingUpgradeForRollingUpgrade6_5To7_5ScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangeRollingUpgradeInjector,
                config={
                    "database": case.database,
                    "table": case.table,
                    "row_count": case.row_count,
                    "expected_amount_cents": case.expected_amount_cents,
                    "expected_tenant_sum": case.expected_tenant_sum,
                    "source_version": case.source_version,
                    "target_version": case.target_version,
                },
            ),
        )

import json

from src.scenarios.tidb.runtime import canonical_tidb_version
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)


class TidbBusinessChangeRollingUpgradeInjector(BaseFaultInjector):
    """Create the live business workload and preserve the pre-change truth."""

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._create_business_table(context.env)
        self._load_business_rows(context.env)
        self._verify_initial_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_initial_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        self._verify_initial_state(context.env)
        cluster_payload = json.loads(context.env.observe_metric("cluster_info"))
        return {
            "business_checksum": json_object(
                context.env.execute_sql(
                    f"SELECT COUNT(*), CAST(SUM(amount * 100) AS SIGNED), "
                    f"CAST(SUM(tenant_id) AS SIGNED) FROM {self.database}.{self.table}"
                ),
                "capture BC01 business checksum",
            ),
            "source_cluster_info": cluster_payload,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.database}"),
            f"drop BC01 database {self.database}",
        )

    def _configure(self, config, env) -> None:
        self.env = env
        self.database = validate_sql_identifier(str(config["database"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.archive_table = validate_sql_identifier(f"{self.table}_archive", "archive table")
        self.row_count = int(config["row_count"])
        self.expected_amount_cents = int(config["expected_amount_cents"])
        self.expected_tenant_sum = int(config["expected_tenant_sum"])
        self.source_version = str(config["source_version"])
        self.target_version = str(config["target_version"])

    def _create_business_table(self, env) -> None:
        statements = (
            f"CREATE DATABASE IF NOT EXISTS {self.database}",
            f"DROP TABLE IF EXISTS {self.database}.{self.archive_table}",
            f"DROP TABLE IF EXISTS {self.database}.{self.table}",
            f"CREATE TABLE {self.database}.{self.table} ("
            "event_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, "
            "event_type VARCHAR(16) NOT NULL, amount DECIMAL(12,2) NOT NULL, "
            "event_time DATETIME NOT NULL, payload VARCHAR(96) NOT NULL, "
            "KEY idx_tenant_time (tenant_id, event_time), KEY idx_event_type (event_type)"
            ")",
            f"CREATE TABLE {self.database}.{self.archive_table} LIKE {self.database}.{self.table}",
        )
        for statement in statements:
            require_sql_success(env.execute_sql(statement), f"BC01 schema statement: {statement}")

    def _load_business_rows(self, env) -> None:
        event_types = ("PAID", "SETTLED", "REVIEW", "REFUND")
        batch_size = 500
        for start in range(1, self.row_count + 1, batch_size):
            stop = min(start + batch_size, self.row_count + 1)
            values = []
            for event_id in range(start, stop):
                tenant_id = event_id % 128 + 1
                event_type = event_types[event_id % len(event_types)]
                amount_cents = (event_id % 401 + 99) * 100
                hour = event_id % 24
                minute = event_id % 60
                values.append(
                    f"({event_id}, {tenant_id}, '{event_type}', {amount_cents / 100:.2f}, "
                    f"'2026-07-01 {hour:02d}:{minute:02d}:00', 'order-payload-{event_id:05d}')"
                )
            require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {self.database}.{self.table} "
                    "(event_id, tenant_id, event_type, amount, event_time, payload) VALUES "
                    + ",".join(values)
                ),
                f"load BC01 business rows {start}:{stop - 1}",
            )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.archive_table} "
                f"SELECT * FROM {self.database}.{self.table} WHERE MOD(event_id, 3) = 0"
            ),
            "load BC01 archive decoy rows",
        )

    def _verify_initial_state(self, env) -> None:
        checksum = json_object(
            env.execute_sql(
                f"SELECT COUNT(*), CAST(SUM(amount * 100) AS SIGNED), "
                f"CAST(SUM(tenant_id) AS SIGNED) FROM {self.database}.{self.table}"
            ),
            "verify BC01 initial business checksum",
        )
        expected = [[self.row_count, self.expected_amount_cents, self.expected_tenant_sum]]
        if checksum["result"] != expected:
            raise RuntimeError(
                "BC01 initial business checksum mismatch: "
                f"expected={expected!r}, observed={checksum['result']!r}"
            )
        cluster_payload = json.loads(env.observe_metric("cluster_info"))
        observed_versions = {
            str(row["TYPE"]): str(row["VERSION"])
            for row in cluster_payload["snapshot"]["nodes"]
        }
        expected_version = canonical_tidb_version(self.source_version)
        if not observed_versions or any(
            canonical_tidb_version(version) != expected_version
            for version in observed_versions.values()
        ):
            raise RuntimeError(
                "BC01 initial cluster is not on the source version: "
                f"expected_source={self.source_version!r}, observed={observed_versions!r}"
            )
