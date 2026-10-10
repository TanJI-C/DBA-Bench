from collections.abc import Mapping

import pymysql

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)

from dataclasses import dataclass, replace

from src.scenarios.workloads import WorkloadProfile
from src.scenarios.evaluation.tidb.resource_governance import (
    TidbResourceGovernanceRunawayQueryEvaluatorCase,
    TidbResourceGovernanceRunawayQueryProtectedExportEvaluatorCase,
)

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
class TidbResourceGovernanceRunawayQueryForProtectedBatchScenarioCase(TiDBScenarioCase):
    db: str
    runaway_table: str
    batch_table: str
    report_group: str
    batch_group: str
    dashboard_group: str
    adhoc_group: str
    runaway_row_count: int
    batch_row_count: int
    batch_id: str
    runaway_query: str
    batch_update: str


def _workload_profiles(
    *,
    db: str,
    runaway_table: str,
    batch_table: str,
    report_group: str,
    batch_group: str,
    dashboard_group: str,
    adhoc_group: str,
    batch_id: str,
) -> tuple[WorkloadProfile, ...]:
    runaway_target = f"{db}.{runaway_table}"
    batch_target = f"{db}.{batch_table}"
    return (
        WorkloadProfile(
            name="rg02_customer_activity_rollup",
            sql=(
                f"SELECT /*+ RESOURCE_GROUP({report_group}) */ region_id, COUNT(*) AS event_count, "
                "SUM(SLEEP(0.002)) AS cpu_delay "
                f"FROM {runaway_target} "
                "WHERE event_day >= '2026-07-01' AND event_day < '2026-08-01' "
                "GROUP BY region_id ORDER BY region_id"
            ),
            qps=0.12,
            tier="CUSTOMER_ANALYTICS",
            application_name="customer-insights-api",
        ),
        WorkloadProfile(
            name="rg02_finance_close_delta",
            sql=(
                f"UPDATE /*+ RESOURCE_GROUP({batch_group}) */ {batch_target} "
                "SET processed_at = NOW() "
                f"WHERE processed_at IS NULL AND batch_id = '{batch_id}' AND SLEEP(0.003) = 0"
            ),
            qps=0.04,
            tier="FINANCE_OPERATIONS",
            commit=True,
            application_name="finance-monthly-close",
        ),
        WorkloadProfile(
            name="rg02_customer_region_breakdown",
            sql=(
                f"SELECT /*+ RESOURCE_GROUP({report_group}) */ region_id, COUNT(*), SUM(amount) "
                f"FROM {runaway_target} WHERE event_type IN ('purchase', 'refund') "
                "GROUP BY region_id ORDER BY SUM(amount) DESC LIMIT 20"
            ),
            qps=0.25,
            tier="CUSTOMER_ANALYTICS",
            application_name="customer-insights-api",
        ),
        WorkloadProfile(
            name="rg02_finance_close_progress",
            sql=(
                f"SELECT /*+ RESOURCE_GROUP({batch_group}) */ COUNT(*), COUNT(processed_at), "
                f"COALESCE(SUM(amount), 0) FROM {batch_target} WHERE batch_id = '{batch_id}'"
            ),
            qps=0.40,
            tier="FINANCE_OPERATIONS",
            application_name="finance-monthly-close-monitor",
        ),
        WorkloadProfile(
            name="rg02_customer_portal_preview",
            sql=(
                f"SELECT /*+ RESOURCE_GROUP({dashboard_group}) */ COUNT(*), SUM(SLEEP(0.08)) "
                f"FROM {runaway_target} WHERE event_id <= 32"
            ),
            qps=0.20,
            tier="CUSTOMER_ANALYTICS",
            application_name="customer-dashboard",
        ),
        WorkloadProfile(
            name="rg02_customer_revenue_preview",
            sql=(
                f"SELECT /*+ RESOURCE_GROUP({adhoc_group}) */ event_type, COUNT(*), SUM(amount) "
                f"FROM {runaway_target} WHERE region_id BETWEEN 1 AND 4 "
                "GROUP BY event_type ORDER BY event_type"
            ),
            qps=0.20,
            tier="CUSTOMER_ANALYTICS",
            application_name="analyst-notebook",
        ),
        WorkloadProfile(
            name="rg02_resource_inventory",
            sql=(
                "SELECT NAME, RU_PER_SEC, PRIORITY, BURSTABLE, QUERY_LIMIT "
                "FROM INFORMATION_SCHEMA.RESOURCE_GROUPS ORDER BY NAME"
            ),
            qps=0.10,
            tier="CONTROL_PLANE",
            application_name="platform-observer",
        ),
        WorkloadProfile(
            name="rg02_history_snapshot",
            sql=(
                "SELECT resource_group_name, time, match_type, action, original_sql, plan_digest, tidb_server "
                "FROM mysql.tidb_runaway_queries ORDER BY time DESC LIMIT 20"
            ),
            qps=0.10,
            tier="CONTROL_PLANE",
            application_name="legacy-reporting",
        ),
        WorkloadProfile(
            name="rg02_legacy_rollup_probe",
            sql="SELECT COUNT(*) FROM test.rg02_legacy_daily_rollup",
            qps=0.10,
            tier="CONTROL_PLANE",
            application_name="legacy-reporting",
        ),
    )


_RG02_DB = "test"
_RG02_RUNAWAY_TABLE = "rg02_customer_events"
_RG02_BATCH_TABLE = "rg02_monthly_close_items"
_RG02_REPORT_GROUP = "rg02_report_api"
_RG02_BATCH_GROUP = "rg02_critical_batch"
_RG02_DASHBOARD_GROUP = "rg02_dashboard"
_RG02_ADHOC_GROUP = "rg02_adhoc"
_RG02_BATCH_ID = "july-close"
_RG02_RUNAWAY_ROW_COUNT = 4096
_RG02_BATCH_ROW_COUNT = 1200
_RG02_RUNAWAY_QUERY = (
    "SELECT /*+ RESOURCE_GROUP(rg02_report_api) */ region_id, COUNT(*) AS event_count, "
    "SUM(SLEEP(0.002)) AS cpu_delay "
    "FROM test.rg02_customer_events "
    "WHERE event_day >= '2026-07-01' AND event_day < '2026-08-01' "
    "GROUP BY region_id ORDER BY region_id"
)
_RG02_BATCH_UPDATE = (
    "UPDATE /*+ RESOURCE_GROUP(rg02_critical_batch) */ test.rg02_monthly_close_items "
    "SET processed_at = NOW() "
    "WHERE processed_at IS NULL AND batch_id = 'july-close' AND SLEEP(0.003) = 0"
)

_RG02_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=_workload_profiles(
        db=_RG02_DB,
        runaway_table=_RG02_RUNAWAY_TABLE,
        batch_table=_RG02_BATCH_TABLE,
        report_group=_RG02_REPORT_GROUP,
        batch_group=_RG02_BATCH_GROUP,
        dashboard_group=_RG02_DASHBOARD_GROUP,
        adhoc_group=_RG02_ADHOC_GROUP,
        batch_id=_RG02_BATCH_ID,
    ),
    worker_count=4,
    seed=20260802,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=12,
)


_RG02_CASE = TidbResourceGovernanceRunawayQueryForProtectedBatchScenarioCase(
    case_id="runaway_query_protected_batch",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "activated a finite ACTION=KILL runaway policy for the customer-insights report resource group",
                "left the protected monthly-close resource group unchanged"
            ],
            "verification": [
                "target report SQL appears in mysql.tidb_runaway_queries with action=kill",
                "all 1,200 monthly-close rows have processed_at",
                "no monthly-close runaway kill record exists"
            ]
        },
        "summary": "The runaway report is governed by its own resource-group policy while the protected monthly-close batch completes."
    },
    case_no=0,
    evaluator=TidbResourceGovernanceRunawayQueryEvaluatorCase,
    title="Stabilize a TiDB customer-facing workload without interrupting a legitimate monthly-close batch.",
    alert=(
        "[P1] customer-facing analytics endpoint P99 从 180ms 升到 8s 以上，"
        "TiDB 仍可用但一个 customer-facing workload 的 CPU 和 processed keys 持续升高。"
        "同一时间 finance monthly-close 正在处理 1,200 行，业务要求本批必须完成；"
        "同一 TiDB 实例上还有 customer portal preview、analyst preview 和 finance progress probe。"
        "请根据历史 workload/TopSQL 证据确定需要治理的 SQL 与 resource group，"
        "上线可持续的资源治理规则和观察窗口，只限制真正失控的请求，不要按执行时长粗暴终止合法批处理。"
    ),
    initial_state={
        "status": "degraded",
        "resource_control": "enabled",
        "runaway_policy": "absent",
        "report_group": _RG02_REPORT_GROUP,
        "batch_group": _RG02_BATCH_GROUP,
        "batch_rows": _RG02_BATCH_ROW_COUNT,
        "batch_processed": 0,
    },
    expected_target={
        "status": "governed",
        "runaway_policy": "kill",
        "runaway_history": True,
        "batch_processed": _RG02_BATCH_ROW_COUNT,
        "batch_runaway_kills": 0,
    },
    background_workload=_RG02_BACKGROUND_WORKLOAD,
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.868852,
        reference_run_ids=(
            "tidb-rg02-reference__tidb_resource_governance_runaway_query__"
            "runaway_query_protected_batch__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=180,
    ),
    db=_RG02_DB,
    runaway_table=_RG02_RUNAWAY_TABLE,
    batch_table=_RG02_BATCH_TABLE,
    report_group=_RG02_REPORT_GROUP,
    batch_group=_RG02_BATCH_GROUP,
    dashboard_group=_RG02_DASHBOARD_GROUP,
    adhoc_group=_RG02_ADHOC_GROUP,
    runaway_row_count=_RG02_RUNAWAY_ROW_COUNT,
    batch_row_count=_RG02_BATCH_ROW_COUNT,
    batch_id=_RG02_BATCH_ID,
    runaway_query=_RG02_RUNAWAY_QUERY,
    batch_update=_RG02_BATCH_UPDATE,
)

_RG02_EXPORT_CASE = replace(
    _RG02_CASE,
    case_id="runaway_query_protected_export",
    case_no=1,
    evaluator=TidbResourceGovernanceRunawayQueryProtectedExportEvaluatorCase,
    title="Govern a runaway customer report without interrupting a protected export batch.",
    alert=(
        "[P1] A customer analytics endpoint has accumulated long-running work while a finance export "
        "must finish as one business batch. Inspect the live statement, resource-group and runaway-history "
        "evidence, then apply a persistent bounded policy only to the runaway report. The export rows and "
        "resource group are protected; do not manually kill sessions or disable resource control."
    ),
    initial_state={
        "status": "degraded",
        "resource_control": "enabled",
        "runaway_policy": "absent",
        "report_group": _RG02_REPORT_GROUP,
        "batch_group": _RG02_BATCH_GROUP,
        "batch_id": "july-export",
        "batch_rows": _RG02_BATCH_ROW_COUNT,
        "batch_processed": 0,
    },
    expected_target={
        "status": "governed",
        "runaway_policy": "kill",
        "runaway_history": True,
        "batch_processed": _RG02_BATCH_ROW_COUNT,
        "batch_runaway_kills": 0,
    },
    batch_id="july-export",
    batch_update=(
        "UPDATE /*+ RESOURCE_GROUP(rg02_critical_batch) */ test.rg02_monthly_close_items "
        "SET processed_at = NOW() WHERE processed_at IS NULL AND batch_id = 'july-export' "
        "AND SLEEP(0.003) = 0"
    ),
    background_workload=replace(
        _RG02_BACKGROUND_WORKLOAD,
        profiles=_workload_profiles(
            db=_RG02_DB,
            runaway_table=_RG02_RUNAWAY_TABLE,
            batch_table=_RG02_BATCH_TABLE,
            report_group=_RG02_REPORT_GROUP,
            batch_group=_RG02_BATCH_GROUP,
            dashboard_group=_RG02_DASHBOARD_GROUP,
            adhoc_group=_RG02_ADHOC_GROUP,
            batch_id="july-export",
        ),
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.894737,
        reference_run_ids=(
            "tidb-reference-6__tidb_resource_governance_runaway_query__"
            "runaway_query_protected_export__mock__r001",
        ),
    ),
)


class TidbResourceGovernanceRunawayQueryInjector(BaseFaultInjector):
    """Build the real RG02 business tables, resource groups, and workload surface."""

    def __init__(self):
        self._runtime_active = False

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_tables(context.env)
        self._seed_tables(context.env)
        self._enable_resource_control(context.env)
        self._create_resource_groups(context.env)
        self._verify_persistent_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_persistent_state(context.env)
        self._runtime_active = True

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._verify_persistent_state(context.env)
        return {
            "rg02_runaway_table": self.runaway_table,
            "rg02_batch_table": self.batch_table,
            "rg02_batch_immutable_truth": self._immutable_batch_truth(context.env),
            "rg02_batch_row_count": self.batch_row_count,
            "rg02_runaway_row_count": self.runaway_row_count,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._runtime_active = False

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._remove_runaway_watches(context.env)
        for group in self.groups:
            require_sql_success(
                context.env.execute_sql(f"DROP RESOURCE GROUP {group}"),
                f"drop RG02 resource group: group={group!r}",
            )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE {self.db}.{self.runaway_table}"),
            f"drop RG02 runaway table: table={self.db}.{self.runaway_table!r}",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE {self.db}.{self.batch_table}"),
            f"drop RG02 batch table: table={self.db}.{self.batch_table!r}",
        )
        require_sql_success(
            context.env.execute_sql("SET GLOBAL tidb_enable_resource_control = OFF"),
            "disable RG02 resource control after recovery",
        )
        self._runtime_active = False

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "db")
        self.runaway_table = validate_sql_identifier(str(config["runaway_table"]), "runaway_table")
        self.batch_table = validate_sql_identifier(str(config["batch_table"]), "batch_table")
        self.report_group = validate_sql_identifier(str(config["report_group"]), "report_group")
        self.batch_group = validate_sql_identifier(str(config["batch_group"]), "batch_group")
        self.dashboard_group = validate_sql_identifier(str(config["dashboard_group"]), "dashboard_group")
        self.adhoc_group = validate_sql_identifier(str(config["adhoc_group"]), "adhoc_group")
        self.groups = (
            self.report_group,
            self.batch_group,
            self.dashboard_group,
            self.adhoc_group,
        )
        self.runaway_row_count = int(config["runaway_row_count"])
        self.batch_row_count = int(config["batch_row_count"])
        self.batch_id = str(config["batch_id"])
        self.runaway_query = str(config["runaway_query"])
        self.batch_update = str(config["batch_update"])

    def _create_tables(self, env: object) -> None:
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.runaway_table} ("
                "event_id INT PRIMARY KEY, region_id INT NOT NULL, "
                "event_type VARCHAR(16) NOT NULL, event_day DATE NOT NULL, "
                "amount DECIMAL(12, 2) NOT NULL, payload VARCHAR(64) NOT NULL)"
            ),
            f"create RG02 runaway table: table={self.db}.{self.runaway_table!r}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.batch_table} ("
                "item_id INT PRIMARY KEY, batch_id VARCHAR(32) NOT NULL, "
                "customer_id INT NOT NULL, amount DECIMAL(12, 2) NOT NULL, "
                "processed_at DATETIME NULL, payload VARCHAR(64) NOT NULL)"
            ),
            f"create RG02 batch table: table={self.db}.{self.batch_table!r}",
        )

    def _seed_tables(self, env: object) -> None:
        connection = pymysql.connect(
            host=env.host,
            port=env.port,
            user=env.user,
            password=env.password,
            database=self.db,
            charset="utf8mb4",
            autocommit=False,
            connect_timeout=10,
            read_timeout=180,
            write_timeout=180,
        )
        with connection.cursor() as cursor:
            runaway_rows = [
                (
                    event_id,
                    event_id % 32,
                    "refund" if event_id % 11 == 0 else "purchase" if event_id % 3 else "renewal",
                    "2026-07-%02d" % (event_id % 28 + 1),
                    (event_id * 7919) % 100000 / 100,
                    f"customer-event-{event_id:05d}",
                )
                for event_id in range(1, self.runaway_row_count + 1)
            ]
            cursor.executemany(
                f"INSERT INTO {self.runaway_table} "
                "(event_id, region_id, event_type, event_day, amount, payload) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                runaway_rows,
            )
            batch_rows = [
                (
                    item_id,
                    self.batch_id,
                    100000 + item_id % 250,
                    (item_id * 3571) % 50000 / 100,
                    f"close-item-{item_id:05d}",
                )
                for item_id in range(1, self.batch_row_count + 1)
            ]
            cursor.executemany(
                f"INSERT INTO {self.batch_table} "
                "(item_id, batch_id, customer_id, amount, payload) "
                "VALUES (%s, %s, %s, %s, %s)",
                batch_rows,
            )
        connection.commit()
        connection.close()

    def _enable_resource_control(self, env: object) -> None:
        require_sql_success(
            env.execute_sql("SET GLOBAL tidb_enable_resource_control = ON"),
            "enable TiDB resource control for RG02",
        )

    def _create_resource_groups(self, env: object) -> None:
        statements = (
            (
                self.report_group,
                f"CREATE RESOURCE GROUP {self.report_group} RU_PER_SEC = 400 BURSTABLE",
            ),
            (
                self.batch_group,
                f"CREATE RESOURCE GROUP {self.batch_group} RU_PER_SEC = 800 PRIORITY = HIGH",
            ),
            (
                self.dashboard_group,
                f"CREATE RESOURCE GROUP {self.dashboard_group} RU_PER_SEC = 200 "
                "QUERY_LIMIT=(EXEC_ELAPSED='2s', ACTION=COOLDOWN)",
            ),
            (
                self.adhoc_group,
                f"CREATE RESOURCE GROUP {self.adhoc_group} RU_PER_SEC = 150 PRIORITY = LOW",
            ),
        )
        for group, sql in statements:
            require_sql_success(
                env.execute_sql(sql),
                f"create RG02 resource group: group={group!r}",
            )

    def _verify_persistent_state(self, env: object) -> None:
        resource_control = json_object(
            env.execute_sql("SELECT @@GLOBAL.tidb_enable_resource_control"),
            "verify RG02 resource control",
        )["result"]
        if resource_control != [[1]]:
            raise RuntimeError(
                "RG02 resource control is not enabled: "
                f"expected=[[1]], actual={resource_control!r}"
            )
        runaway_count = json_object(
            env.execute_sql(f"SELECT COUNT(*) FROM {self.db}.{self.runaway_table}"),
            "verify RG02 runaway rows",
        )["result"]
        if runaway_count != [[self.runaway_row_count]]:
            raise RuntimeError(
                "RG02 runaway table row count mismatch: "
                f"table={self.db}.{self.runaway_table!r}, expected={self.runaway_row_count}, "
                f"actual={runaway_count!r}"
            )
        batch_count = json_object(
            env.execute_sql(
                f"SELECT COUNT(*) FROM {self.db}.{self.batch_table} "
                f"WHERE batch_id = '{self.batch_id}'"
            ),
            "verify RG02 batch rows",
        )["result"]
        if batch_count != [[self.batch_row_count]]:
            raise RuntimeError(
                "RG02 batch table row count mismatch: "
                f"table={self.db}.{self.batch_table!r}, batch_id={self.batch_id!r}, "
                f"expected={self.batch_row_count}, actual={batch_count!r}"
            )
        groups = json_object(
            env.execute_sql(
                "SELECT NAME FROM INFORMATION_SCHEMA.RESOURCE_GROUPS "
                "WHERE NAME IN ("
                + ",".join(f"'{group}'" for group in self.groups)
                + ") ORDER BY NAME"
            ),
            "verify RG02 resource groups",
        )["result"]
        observed = {str(row[0]).casefold() for row in groups}
        expected = {group.casefold() for group in self.groups}
        if observed != expected:
            raise RuntimeError(
                "RG02 resource group inventory mismatch: "
                f"expected={sorted(expected)!r}, actual={sorted(observed)!r}"
            )

    def _immutable_batch_truth(self, env: object) -> tuple[int, int, int]:
        rows = json_object(
            env.execute_sql(
                "SELECT COUNT(*), COALESCE(SUM(item_id), 0), "
                "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', item_id, batch_id, customer_id, amount))), 0) "
                f"FROM {self.db}.{self.batch_table} WHERE batch_id = '{self.batch_id}'"
            ),
            "capture RG02 batch truth",
        )["result"]
        if len(rows) != 1:
            raise RuntimeError(f"RG02 batch truth expected one row: rows={rows!r}")
        return tuple(int(value) for value in rows[0])

    def _remove_runaway_watches(self, env: object) -> None:
        watches = json_object(
            env.execute_sql(
                "SELECT ID FROM INFORMATION_SCHEMA.RUNAWAY_WATCHES "
                f"WHERE RESOURCE_GROUP_NAME = '{self.report_group}' ORDER BY ID"
            ),
            "list RG02 runaway watches for recovery",
        )["result"]
        for row in watches:
            watch_id = int(row[0])
            require_sql_success(
                env.execute_sql(f"QUERY WATCH REMOVE {watch_id}"),
                f"remove RG02 runaway watch: id={watch_id}",
            )


class TidbResourceGovernanceRunawayQueryScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_runaway_query"
    description = "Govern a TiDB customer-facing workload without interrupting a protected business batch."
    cases = (_RG02_CASE, _RG02_EXPORT_CASE)

    def build_fault_plan(
        self,
        case: TidbResourceGovernanceRunawayQueryForProtectedBatchScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernanceRunawayQueryInjector,
                config={
                    "db": case.db,
                    "runaway_table": case.runaway_table,
                    "batch_table": case.batch_table,
                    "report_group": case.report_group,
                    "batch_group": case.batch_group,
                    "dashboard_group": case.dashboard_group,
                    "adhoc_group": case.adhoc_group,
                    "runaway_row_count": case.runaway_row_count,
                    "batch_row_count": case.batch_row_count,
                    "batch_id": case.batch_id,
                    "runaway_query": case.runaway_query,
                    "batch_update": case.batch_update,
                },
            ),
        )
