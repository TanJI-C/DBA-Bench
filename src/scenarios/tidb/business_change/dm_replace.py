from dataclasses import dataclass

from src.scenarios.evaluation.tidb.business_change.dm_replace import (
    TidbBusinessChangeDmReplaceEvaluatorCase,
    TidbBusinessChangeDmReplaceForBillingEvaluatorCase,
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
from ..runtime import TIDB_V8_1_0, tidb_runtime


def build_dm_migration_noise_profiles(
    db: str = "benchops",
    table: str = "dm_replace_events",
    source_database: str = "order_source",
    control_database: str = "dm_control",
    archive_database: str = "dm_archive",
    first_column: str = "new_col",
    second_column: str = "release_region",
    include_decoy_profiles: bool = True,
) -> tuple[WorkloadProfile, ...]:
    qualified = f"{db}.{table}"
    profiles = (
        WorkloadProfile(
            name="order_api_pending_schema_read",
            sql=(
                f"SELECT id, account_id, amount_cents, {first_column} FROM {qualified} "
                "WHERE id >= 950 ORDER BY id DESC LIMIT 25"
            ),
            qps=1.0,
            tier="OLTP_READ",
            application_name="order-api-release-canary",
        ),
        WorkloadProfile(
            name="order_api_amount_rollup",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(amount_cents), 0) FROM {qualified} "
                "WHERE id BETWEEN 1 AND 1000"
            ),
            qps=0.7,
            tier="OLTP_READ",
            application_name="order-api-summary",
        ),
        WorkloadProfile(
            name="dm_task_status_dashboard",
            sql=(
                "SELECT task_name, stage, unit, synced, checkpoint, last_error "
                f"FROM {control_database}.dm_task_status ORDER BY task_name"
            ),
            qps=0.8,
            tier="CONTROL_READ",
            application_name="migration-dashboard",
        ),
        WorkloadProfile(
            name="dm_binlog_history_probe",
            sql=(
                f"SELECT event_id, event_type, status, source_id FROM {control_database}.dm_binlog_events "
                "ORDER BY event_id DESC LIMIT 12"
            ),
            qps=0.65,
            tier="CONTROL_READ",
            application_name="binlog-audit-console",
        ),
        WorkloadProfile(
            name="dm_worker_log_tail_probe",
            sql=(
                f"SELECT level, message FROM {control_database}.dm_worker_logs "
                "ORDER BY log_id DESC LIMIT 12"
            ),
            qps=0.55,
            tier="CONTROL_READ",
            application_name="replication-log-monitor",
        ),
        WorkloadProfile(
            name="archive_reconciliation_decoy",
            sql=(
                "SELECT COUNT(*), COALESCE(SUM(amount_cents), 0) "
                f"FROM {archive_database}.{table} WHERE id < 40"
            ),
            qps=0.6,
            tier="DECOY_READ",
            application_name="warehouse-reconciliation",
        ),
        WorkloadProfile(
            name="schema_inventory_decoy",
            sql=(
                "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, ORDINAL_POSITION "
                "FROM information_schema.columns "
                f"WHERE TABLE_SCHEMA IN ('{source_database}', '{db}', '{archive_database}') "
                "ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION"
            ),
            qps=0.5,
            tier="CATALOG_READ",
            application_name="schema-inventory",
        ),
        WorkloadProfile(
            name="dm_task_history_decoy",
            sql=(
                f"SELECT task_name, action, status FROM {control_database}.dm_task_history "
                "WHERE task_name <> 'archived-task' ORDER BY action_id DESC LIMIT 10"
            ),
            qps=0.45,
            tier="DECOY_READ",
            application_name="legacy-migration-console",
        ),
        WorkloadProfile(
            name="dm_source_lag_dashboard_decoy",
            sql=(
                f"SELECT task_name, source_id, checkpoint, master_binlog, syncer_binlog "
                f"FROM {control_database}.dm_task_status ORDER BY checkpoint DESC"
            ),
            qps=0.4,
            tier="DECOY_READ",
            application_name="source-lag-dashboard",
        ),
        WorkloadProfile(
            name="dm_failed_event_fingerprint_decoy",
            sql=(
                f"SELECT task_name, source_id, event_id, error_message "
                f"FROM {control_database}.dm_binlog_events WHERE status = 'failed' ORDER BY event_id DESC"
            ),
            qps=0.35,
            tier="DECOY_READ",
            application_name="migration-error-index",
        ),
        WorkloadProfile(
            name="release_region_rollup_probe",
            sql=(
                f"SELECT {second_column}, COUNT(*) FROM {qualified} "
                f"GROUP BY {second_column} ORDER BY {second_column}"
            ),
            qps=0.3,
            tier="OLTP_READ",
            application_name="regional-release-dashboard",
        ),
    )
    if not include_decoy_profiles:
        decoy_names = frozenset({
            "archive_reconciliation_decoy",
            "schema_inventory_decoy",
            "dm_task_history_decoy",
            "dm_source_lag_dashboard_decoy",
            "dm_failed_event_fingerprint_decoy",
        })
        return tuple(profile for profile in profiles if profile.name not in decoy_names)
    return profiles


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeDmReplaceCase(TiDBScenarioCase):
    db: str
    table: str
    source_database: str
    control_database: str
    archive_database: str
    task_name: str
    source_id: str
    peer_task_name: str
    peer_source_id: str
    peer_checkpoint: int
    warehouse_task_name: str
    warehouse_source_id: str
    warehouse_checkpoint: int
    initial_row_count: int
    failed_ddl_sql: str
    second_failed_ddl_sql: str
    pending_dml_sql: str
    second_pending_dml_sql: str
    replacement_sql: str
    second_replacement_sql: str
    pending_row_id: int
    pending_account_id: int
    pending_amount_cents: int
    pending_new_col: int
    pending_region: int | None
    second_pending_row_id: int
    second_pending_account_id: int
    second_pending_amount_cents: int
    second_pending_new_col: int
    second_pending_region: int
    final_row_count: int
    final_id_sum: int
    final_account_id_sum: int
    final_amount_sum: int
    final_new_col_sum: int
    first_column: str
    second_column: str
    first_unique_key: str
    second_unique_key: str
    reference_path: tuple[str, ...]
    reference_tool_counts: tuple[tuple[str, int, int], ...]
    seed_competing_task_entities: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeDmReplaceForFailedDdlSafeReplaceScenarioCase(
    TidbBusinessChangeDmReplaceCase
):
    pass


class TidbBusinessChangeDmReplaceForFailedDdlSafeReplaceBillingScenarioCase(
    TidbBusinessChangeDmReplaceCase
):
    pass


_CASE = TidbBusinessChangeDmReplaceForFailedDdlSafeReplaceScenarioCase(
    case_id="failed_ddl_safe_replace",
    reference_report=structured_reference_report(
        case_id="failed_ddl_safe_replace",
        factors=(),
        changes=(
            "replaced each failed DM DDL with its column-specific ADD COLUMN and ADD UNIQUE KEY pair",
            "resumed the migration checkpoint without changing upstream business data",
        ),
        verification=(
            "query-status is Running/Sync and synced with equal binlog positions",
            "upstream and downstream schemas, aggregates, and both post-DDL rows are equal",
        ),
        summary="The reference path repaired the paused DM DDL sequence and verified replication correctness.",
    ),
    case_no=0,
    evaluator=TidbBusinessChangeDmReplaceEvaluatorCase,
    title=(
        "Keep a DM migration correct after a downstream-incompatible schema DDL pauses synchronization."
    ),
    alert=(
        "[CRITICAL] 一条 DM 迁移任务的 checkpoint 停止前进，下游业务表仍是旧 schema，"
        "上游发布窗口已经连续提交了依赖两个新字段的业务事件。请在不丢失任一事件、不破坏已有数据、"
        "不扩大变更范围的前提下逐个恢复同步，并给出可复核的上下游一致性证据。"
    ),
    initial_state={
        "migration": "paused",
        "downstream_schema": "pre-release",
        "pending_business_events": 2,
    },
    expected_target={
        "migration": "running_and_synced",
        "downstream_schema": "equivalent_to_upstream",
        "pending_business_events": "replicated",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=build_dm_migration_noise_profiles(
            db="benchops",
            table="dm_replace_events",
        ),
        worker_count=6,
        seed=48134,
        warmup_seconds=8,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=9,
        environmental_complexity=0.677419,
        reference_run_ids=(
            "reference-155__"
            "tidb_business_change_dm_replace__failed_ddl_safe_replace__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=120,
    ),
    db="benchops",
    table="dm_replace_events",
    source_database="order_source",
    control_database="dm_control",
    archive_database="dm_archive",
    task_name="admission-replace",
    source_id="mysql-admission-source",
    peer_task_name="admission-canary",
    peer_source_id="mysql-admission-source",
    peer_checkpoint=12,
    warehouse_task_name="warehouse-replay",
    warehouse_source_id="mysql-admission-source",
    warehouse_checkpoint=0,
    initial_row_count=1000,
    failed_ddl_sql=(
        "ALTER TABLE `benchops`.`dm_replace_events` ADD COLUMN `new_col` INT UNIQUE"
    ),
    second_failed_ddl_sql=(
        "ALTER TABLE `benchops`.`dm_replace_events` "
        "ADD COLUMN `release_region` INT UNIQUE"
    ),
    pending_dml_sql=(
        "INSERT INTO `benchops`.`dm_replace_events` "
        "(id, account_id, amount_cents, payload, new_col) "
        "VALUES (1001, 1, 4242, 'post_release_event', 42)"
    ),
    second_pending_dml_sql=(
        "INSERT INTO `benchops`.`dm_replace_events` "
        "(id, account_id, amount_cents, payload, new_col, release_region) "
        "VALUES (1002, 2, 5151, 'post_region_event', 43, 7)"
    ),
    replacement_sql=(
        "ALTER TABLE `benchops`.`dm_replace_events` ADD COLUMN `new_col` INT;"
        "ALTER TABLE `benchops`.`dm_replace_events` "
        "ADD UNIQUE KEY `uk_dm_replace_events_new_col` (`new_col`)"
    ),
    second_replacement_sql=(
        "ALTER TABLE `benchops`.`dm_replace_events` "
        "ADD COLUMN `release_region` INT;"
        "ALTER TABLE `benchops`.`dm_replace_events` "
        "ADD UNIQUE KEY `uk_dm_replace_events_release_region` (`release_region`)"
    ),
    pending_row_id=1001,
    pending_account_id=1,
    pending_amount_cents=4242,
    pending_new_col=42,
    pending_region=None,
    second_pending_row_id=1002,
    second_pending_account_id=2,
    second_pending_amount_cents=5151,
    second_pending_new_col=43,
    second_pending_region=7,
    final_row_count=1002,
    final_id_sum=502503,
    final_account_id_sum=50503,
    final_amount_sum=4390893,
    final_new_col_sum=85,
    first_column="new_col",
    second_column="release_region",
    first_unique_key="uk_dm_replace_events_new_col",
    second_unique_key="uk_dm_replace_events_release_region",
    reference_path=(
        "DM checkpoint stops while two release events are still pending",
        "task, source, and checkpoint identity expose active, healthy same-source, and warehouse same-source candidates",
        "event target and the release business event chain separate benchops admission-replace from dm_archive warehouse-replay",
        "query-status and worker logs tie the stopped checkpoint to the first failed downstream DDL",
        "upstream schema and the first pending DML prove the first DDL cannot simply be skipped",
        "the first equivalent replacement applies the middle DML and exposes a second failed DDL",
        "the first replacement is applied and event 2 is copied while event 3 remains failed; warehouse event 7001 is outside the active task",
        "the second upstream schema and pending DML require a different column-specific replacement",
        "the second replacement and controlled continuation return the active task to running and synced",
        "downstream schema, business aggregates, and both post-DDL rows prove lossless continuation",
    ),
    reference_tool_counts=(
        ("execute_sql(target=dm_control,task/event)", 20, 11),
        ("execute_sql(target=order_source)", 4, 0),
        ("execute_sql(target=primary)", 5, 1),
        ("execute_sql(target=dm_worker_logs)", 1, 3),
        ("query_metrics(qps/query_latency/active_connections)", 0, 48),
    ),
)


_BILLING_CASE = TidbBusinessChangeDmReplaceForFailedDdlSafeReplaceBillingScenarioCase(
    case_id="failed_ddl_safe_replace_billing",
    reference_report=structured_reference_report(
        case_id="failed_ddl_safe_replace_billing",
        factors=(
            "the billing DM task pauses on two downstream-incompatible release DDLs ahead of two post-DDL events",
            "the billing source keeps both post-DDL events and the target must catch up without source mutation",
        ),
        changes=(
            "replaced each billing DDL with its matching column and unique constraint through the active DM task",
            "continued the billing checkpoint without skipping either post-DDL event",
        ),
        verification=(
            "billing task status is Running/Sync with equal binlog positions",
            "billing source and target schema, aggregate truth, and both pending rows match",
        ),
        summary="The billing migration resumed after two equivalent downstream schema replacements.",
    ),
    case_no=1,
    evaluator=TidbBusinessChangeDmReplaceForBillingEvaluatorCase,
    title="Resume a billing DM stream after two incompatible release DDLs without losing events.",
    alert=(
        "[CRITICAL] billing-api 的 DM checkpoint 停止前进，billing 下游仍缺少本次发布的两个字段，"
        "但 billing source 已经提交了依赖这两个字段的订单事件。请逐个修复下游 schema 并让同步无损恢复；"
        "不得修改 source business rows、跳过未等价修复的 DDL 或扩大控制面写入范围。"
    ),
    initial_state={"migration": "paused", "downstream_schema": "pre-release", "pending_business_events": 2},
    expected_target={"migration": "running_and_synced", "downstream_schema": "equivalent_to_source", "pending_business_events": "replicated"},
    background_workload=BackgroundWorkloadSpec(
        profiles=build_dm_migration_noise_profiles(
            db="benchops_bc06_billing",
            table="billing_replace_events",
            source_database="billing_source",
            control_database="billing_dm_control",
            archive_database="billing_dm_archive",
            first_column="billing_tier",
            second_column="settlement_region",
            include_decoy_profiles=False,
        ),
        worker_count=4,
        seed=0xBC0607,
        warmup_seconds=8,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=8,
        environmental_complexity=0.066002,
        reference_run_ids=(
            "tidb-reference-12__"
            "tidb_business_change_dm_replace__failed_ddl_safe_replace_billing__"
            "mock__r001",
        ),
    ),
    runtime=tidb_runtime(release=TIDB_V8_1_0, pd_count=1, tikv_count=1, tidb_count=1, sql_timeout_seconds=120),
    db="benchops_bc06_billing",
    table="billing_replace_events",
    source_database="billing_source",
    control_database="billing_dm_control",
    archive_database="billing_dm_archive",
    task_name="billing-admission-replace",
    source_id="mysql-billing-source",
    peer_task_name="billing-canary",
    peer_source_id="mysql-billing-source",
    peer_checkpoint=19,
    warehouse_task_name="billing-warehouse-replay",
    warehouse_source_id="mysql-billing-source",
    warehouse_checkpoint=0,
    initial_row_count=1800,
    failed_ddl_sql="ALTER TABLE `benchops_bc06_billing`.`billing_replace_events` ADD COLUMN `billing_tier` INT UNIQUE",
    second_failed_ddl_sql="ALTER TABLE `benchops_bc06_billing`.`billing_replace_events` ADD COLUMN `settlement_region` INT UNIQUE",
    pending_dml_sql="INSERT INTO `benchops_bc06_billing`.`billing_replace_events` (id, account_id, amount_cents, payload, billing_tier) VALUES (2001, 2, 7777, 'billing_release_event', 52)",
    second_pending_dml_sql="INSERT INTO `benchops_bc06_billing`.`billing_replace_events` (id, account_id, amount_cents, payload, billing_tier, settlement_region) VALUES (2002, 3, 8888, 'billing_region_event', 53, 9)",
    replacement_sql="ALTER TABLE `benchops_bc06_billing`.`billing_replace_events` ADD COLUMN `billing_tier` INT; ALTER TABLE `benchops_bc06_billing`.`billing_replace_events` ADD UNIQUE KEY `uk_billing_replace_events_tier` (`billing_tier`)",
    second_replacement_sql="ALTER TABLE `benchops_bc06_billing`.`billing_replace_events` ADD COLUMN `settlement_region` INT; ALTER TABLE `benchops_bc06_billing`.`billing_replace_events` ADD UNIQUE KEY `uk_billing_replace_events_region` (`settlement_region`)",
    pending_row_id=2001,
    pending_account_id=2,
    pending_amount_cents=7777,
    pending_new_col=52,
    pending_region=None,
    second_pending_row_id=2002,
    second_pending_account_id=3,
    second_pending_amount_cents=8888,
    second_pending_new_col=53,
    second_pending_region=9,
    final_row_count=1802,
    final_id_sum=1624903,
    final_account_id_sum=90905,
    final_amount_sum=12943365,
    final_new_col_sum=105,
    first_column="billing_tier",
    second_column="settlement_region",
    first_unique_key="uk_billing_replace_events_tier",
    second_unique_key="uk_billing_replace_events_region",
    reference_path=(
        "the billing checkpoint is paused with two post-DDL events pending",
        "task/source identity confirms the paused active billing stream is the migration task to repair",
        "source and target schemas show the first billing DDL is incompatible downstream",
        "the failed event and worker log identify the first column-specific replacement",
        "the first equivalent replacement lets the first DML advance and exposes the second failed DDL",
        "the second source schema and pending row require the region-specific replacement",
        "the second replacement and controlled continuation return billing to Running/Sync",
        "schema, aggregate truth, and both billing rows prove lossless recovery",
    ),
    reference_tool_counts=(
        ("execute_sql(target=control,task/event)", 25, 0),
        ("execute_sql(target=source/primary)", 5, 0),
        ("query_metrics", 70, 0),
    ),
    seed_competing_task_entities=False,
)


class TidbBusinessChangeDmReplaceScenario(TiDBScenario):
    scenario_id = "tidb_business_change_dm_replace"
    description = (
        "A real SQL-backed TiDB Data Migration task pauses twice on downstream-incompatible "
        "release DDLs and must resume without losing either following business event."
    )
    cases = (_CASE, _BILLING_CASE)

    def build_fault_plan(
        self,
        case: TidbBusinessChangeDmReplaceCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangeDmReplaceInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "source_database": case.source_database,
                    "control_database": case.control_database,
                    "archive_database": case.archive_database,
                    "task_name": case.task_name,
                    "source_id": case.source_id,
                    "peer_task_name": case.peer_task_name,
                    "peer_source_id": case.peer_source_id,
                    "peer_checkpoint": case.peer_checkpoint,
                    "warehouse_task_name": case.warehouse_task_name,
                    "warehouse_source_id": case.warehouse_source_id,
                    "warehouse_checkpoint": case.warehouse_checkpoint,
                    "initial_row_count": case.initial_row_count,
                    "failed_ddl_sql": case.failed_ddl_sql,
                    "second_failed_ddl_sql": case.second_failed_ddl_sql,
                    "pending_dml_sql": case.pending_dml_sql,
                    "second_pending_dml_sql": case.second_pending_dml_sql,
                    "replacement_sql": case.replacement_sql,
                    "second_replacement_sql": case.second_replacement_sql,
                    "pending_row_id": case.pending_row_id,
                    "pending_account_id": case.pending_account_id,
                    "pending_amount_cents": case.pending_amount_cents,
                    "pending_new_col": case.pending_new_col,
                    "pending_region": case.pending_region,
                    "second_pending_row_id": case.second_pending_row_id,
                    "second_pending_account_id": case.second_pending_account_id,
                    "second_pending_amount_cents": case.second_pending_amount_cents,
                    "second_pending_new_col": case.second_pending_new_col,
                    "second_pending_region": case.second_pending_region,
                    "final_row_count": case.final_row_count,
                    "final_id_sum": case.final_id_sum,
                    "final_account_id_sum": case.final_account_id_sum,
                    "final_amount_sum": case.final_amount_sum,
                    "final_new_col_sum": case.final_new_col_sum,
                    "first_column": case.first_column,
                    "second_column": case.second_column,
                    "first_unique_key": case.first_unique_key,
                    "second_unique_key": case.second_unique_key,
                    "seed_competing_task_entities": case.seed_competing_task_entities,
                },
            ),
        )


import re
import threading
import time
from collections.abc import Mapping

import pymysql
from pymysql.constants import CLIENT

from src.database.sql import execute_result_rows, require_success_payload

from src.scenarios.tidb.common import BaseFaultInjector, FaultLifecycleContext, validate_sql_identifier


_TASK_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


class TidbBusinessChangeDmReplaceInjector(BaseFaultInjector):
    """Run a real SQL-backed DM relay with a failed DDL checkpoint."""

    source_database = "order_source"
    control_database = "dm_control"
    archive_database = "dm_archive"

    def __init__(self) -> None:
        self.env = None
        self._thread: threading.Thread | None = None
        self._stop_event: threading.Event | None = None
        self._worker_error: BaseException | None = None
        self._registered_connection_surfaces: set[str] = set()

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._create_databases()
        self._create_tables()
        self._seed_rows()
        self._start_relay()
        self._wait_for_synced(45.0)
        self._emit_failed_ddl()
        self._wait_for_paused(45.0)
        self._emit_pending_dml()
        self._verify_persistent_state()
        self._register_connection_surfaces()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_persistent_state()
        self._register_connection_surfaces()
        self._start_relay()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config, context.env)
        self._verify_persistent_state()
        self.env.set_sql_connection_surface_write_policy(self.control_database, "dm_action")
        return {
            "dm_status_before_repair": self._rows(
                "SELECT task_name, stage, unit, synced, checkpoint, master_binlog, "
                f"syncer_binlog, blocking_ddls, last_error FROM {self.control_database}.dm_task_status",
                "capture DM status",
            ),
            "order_source_schema_before_repair": self._rows(
                f"SHOW CREATE TABLE {self.source_database}.{self.table}",
                "capture upstream DM schema",
            ),
            "dm_downstream_schema_before_repair": self._rows(
                f"SHOW CREATE TABLE {self.db}.{self.table}",
                "capture downstream DM schema",
            ),
            "dm_worker_log_before_repair": self._rows(
                f"SELECT level, message FROM {self.control_database}.dm_worker_logs "
                "ORDER BY log_id DESC LIMIT 40",
                "capture DM worker log",
            ),
            "dm_failed_ddl": self.failed_ddl_sql,
            "dm_pending_dml": self.pending_dml_sql,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._stop_relay(raise_worker_error=True)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._stop_relay(raise_worker_error=True)
        if self.control_database in self._registered_connection_surfaces:
            self.env.set_sql_connection_surface_write_policy(self.control_database, "unrestricted")
        for database in (
            self.source_database,
            self.control_database,
            self.archive_database,
            self.db,
        ):
            self._sql(
                f"DROP DATABASE IF EXISTS {database}",
                f"remove DM database {database}",
            )
        for name in sorted(self._registered_connection_surfaces):
            self.env.unregister_sql_connection_surface(name)
        self._registered_connection_surfaces.clear()

    def _register_connection_surfaces(self) -> None:
        self.env.register_sql_connection_surface(
            self.source_database,
            database=self.source_database,
            description=(
                "订单业务源端数据库；用于读取源端表结构、源端业务数据和源端 schema 变化。"
            ),
            query_examples=(
                "SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA = DATABASE()",
                "SHOW CREATE TABLE <observed_table>",
                "SELECT ... FROM <observed_table>",
            ),
        )
        self._registered_connection_surfaces.add(self.source_database)
        self.env.register_sql_connection_surface(
            self.control_database,
            database=self.control_database,
            description=(
                "迁移控制面数据库；用于查询任务状态、事件、动作历史和 worker 记录。"
                "控制表由 DM worker 管理，唯一允许的写操作是向 dm_actions 提交单条 replace、inject、skip 或 resume action。"
            ),
            query_examples=(
                "SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA = DATABASE()",
                "SELECT ... FROM <observed_control_table>",
            ),
        )
        self._registered_connection_surfaces.add(self.control_database)

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.source_database = validate_sql_identifier(
            str(config.get("source_database", self.source_database)), "source_database"
        )
        self.control_database = validate_sql_identifier(
            str(config.get("control_database", self.control_database)), "control_database"
        )
        self.archive_database = validate_sql_identifier(
            str(config.get("archive_database", self.archive_database)), "archive_database"
        )
        self.db = validate_sql_identifier(str(config["db"]), "db")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.task_name = self._validate_token(str(config["task_name"]), "task_name")
        self.source_id = self._validate_token(str(config["source_id"]), "source_id")
        self.peer_task_name = self._validate_token(str(config["peer_task_name"]), "peer_task_name")
        self.peer_source_id = self._validate_token(str(config["peer_source_id"]), "peer_source_id")
        self.peer_checkpoint = int(config["peer_checkpoint"])
        self.warehouse_task_name = self._validate_token(
            str(config["warehouse_task_name"]), "warehouse_task_name"
        )
        self.warehouse_source_id = self._validate_token(
            str(config["warehouse_source_id"]), "warehouse_source_id"
        )
        self.warehouse_checkpoint = int(config["warehouse_checkpoint"])
        self.initial_row_count = int(config["initial_row_count"])
        self.failed_ddl_sql = str(config["failed_ddl_sql"])
        self.second_failed_ddl_sql = str(config["second_failed_ddl_sql"])
        self.pending_dml_sql = str(config["pending_dml_sql"])
        self.second_pending_dml_sql = str(config["second_pending_dml_sql"])
        self.replacement_sql = str(config["replacement_sql"])
        self.second_replacement_sql = str(config["second_replacement_sql"])
        self.pending_row_id = int(config["pending_row_id"])
        self.pending_account_id = int(config["pending_account_id"])
        self.pending_amount_cents = int(config["pending_amount_cents"])
        self.pending_new_col = int(config["pending_new_col"])
        self.pending_region = config["pending_region"]
        self.second_pending_row_id = int(config["second_pending_row_id"])
        self.second_pending_account_id = int(config["second_pending_account_id"])
        self.second_pending_amount_cents = int(config["second_pending_amount_cents"])
        self.second_pending_new_col = int(config["second_pending_new_col"])
        self.second_pending_region = config["second_pending_region"]
        self.final_row_count = int(config["final_row_count"])
        self.final_id_sum = int(config["final_id_sum"])
        self.final_account_id_sum = int(config["final_account_id_sum"])
        self.final_amount_sum = int(config["final_amount_sum"])
        self.final_new_col_sum = int(config["final_new_col_sum"])
        self.first_column = self._validate_token(str(config["first_column"]), "first_column")
        self.second_column = self._validate_token(str(config["second_column"]), "second_column")
        self.first_unique_key = self._validate_token(str(config["first_unique_key"]), "first_unique_key")
        self.second_unique_key = self._validate_token(str(config["second_unique_key"]), "second_unique_key")
        self.seed_competing_task_entities = bool(config["seed_competing_task_entities"])
        if self.initial_row_count <= 0:
            raise ValueError(
                f"DM fixture row count must be positive: task={self.task_name!r}, "
                f"initial_row_count={self.initial_row_count}"
            )

    @staticmethod
    def _validate_token(value: str, name: str) -> str:
        if not _TASK_TOKEN_RE.fullmatch(value):
            raise ValueError(f"Invalid DM {name}: value={value!r}")
        return value

    @staticmethod
    def _quote(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def _connect(self, database: str | None = None):
        return pymysql.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            database=database,
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=5,
            read_timeout=self.env.sql_timeout_seconds,
            write_timeout=self.env.sql_timeout_seconds,
            client_flag=CLIENT.MULTI_STATEMENTS,
        )

    def _sql(self, sql: str, context: str) -> dict:
        return require_success_payload(self.env.execute_sql(sql), f"{context}: sql={sql!r}")

    def _rows(self, sql: str, context: str) -> list:
        return execute_result_rows(self.env.execute_sql, sql, context)

    @staticmethod
    def _direct_execute(connection, sql: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            while cursor.nextset():
                pass

    def _create_databases(self) -> None:
        for database in (
            self.source_database,
            self.control_database,
            self.archive_database,
            self.db,
        ):
            self._sql(f"DROP DATABASE IF EXISTS {database}", f"clear DM database {database}")
            self._sql(f"CREATE DATABASE {database}", f"create DM database {database}")

    def _create_tables(self) -> None:
        for database in (self.source_database, self.db, self.archive_database):
            self._sql(
                f"""
                CREATE TABLE {database}.{self.table} (
                    id INT NOT NULL PRIMARY KEY,
                    account_id INT NOT NULL,
                    amount_cents INT NOT NULL,
                    payload VARCHAR(64) NOT NULL
                ) ENGINE=InnoDB
                """,
                f"create DM fixture table {database}.{self.table}",
            )
        self._sql(
            f"""
            CREATE TABLE {self.control_database}.dm_task_status (
                task_name VARCHAR(64) NOT NULL PRIMARY KEY,
                source_id VARCHAR(64) NOT NULL,
                stage ENUM('Running', 'Paused') NOT NULL,
                unit ENUM('Dump', 'Load', 'Sync') NOT NULL,
                synced TINYINT NOT NULL,
                checkpoint BIGINT NOT NULL,
                master_binlog BIGINT NOT NULL,
                syncer_binlog BIGINT NOT NULL,
                blocking_ddls TEXT NOT NULL,
                unresolved_groups TEXT NOT NULL,
                last_error TEXT NOT NULL,
                updated_at DATETIME(6) NOT NULL
            ) ENGINE=InnoDB
            """,
            "create DM task status table",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_database}.dm_binlog_events (
                event_id BIGINT NOT NULL PRIMARY KEY,
                task_name VARCHAR(64) NOT NULL,
                source_id VARCHAR(64) NOT NULL,
                event_type ENUM('DDL', 'DML') NOT NULL,
                event_sql TEXT NOT NULL,
                status ENUM('pending', 'failed', 'applied', 'replaced', 'skipped') NOT NULL,
                error_message TEXT NOT NULL,
                replacement_sql TEXT NOT NULL,
                created_at DATETIME(6) NOT NULL
            ) ENGINE=InnoDB
            """,
            "create DM binlog table",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_database}.dm_actions (
                action_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                task_name VARCHAR(64) NOT NULL,
                action ENUM('replace', 'inject', 'skip', 'resume') NOT NULL,
                replacement_sql TEXT NOT NULL,
                status ENUM('pending', 'processing', 'completed', 'error') NOT NULL,
                error_message TEXT NOT NULL,
                created_at DATETIME(6) NOT NULL
            ) ENGINE=InnoDB
            """,
            "create DM action table",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_database}.dm_worker_logs (
                log_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                level ENUM('INFO', 'WARN', 'ERROR') NOT NULL,
                message VARCHAR(512) NOT NULL,
                created_at DATETIME(6) NOT NULL
            ) ENGINE=InnoDB
            """,
            "create DM worker log table",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_database}.dm_task_history (
                action_id BIGINT NOT NULL,
                task_name VARCHAR(64) NOT NULL,
                action ENUM('replace', 'inject', 'skip', 'resume') NOT NULL,
                status ENUM('completed') NOT NULL,
                created_at DATETIME(6) NOT NULL
            ) ENGINE=InnoDB
            """,
            "create DM task history table",
        )

    def _seed_rows(self) -> None:
        for database, count in (
            (self.source_database, self.initial_row_count),
            (self.db, self.initial_row_count),
            (self.archive_database, 30),
        ):
            for start in range(1, count + 1, 200):
                end = min(count, start + 199)
                values = ", ".join(
                    f"({row_id}, {(row_id % 100) + 1}, {878 + row_id * 7}, "
                    f"'seed-order-{row_id}')"
                    for row_id in range(start, end + 1)
                )
                self._sql(
                    f"INSERT INTO {database}.{self.table} "
                    f"(id, account_id, amount_cents, payload) VALUES {values}",
                    f"seed DM rows database={database} start={start} end={end}",
                )
        self._sql(
            f"""
            INSERT INTO {self.control_database}.dm_task_status
                (task_name, source_id, stage, unit, synced, checkpoint, master_binlog,
                 syncer_binlog, blocking_ddls, unresolved_groups, last_error, updated_at)
            VALUES (
                {self._quote(self.task_name)}, {self._quote(self.source_id)}, 'Running', 'Sync',
                1, 0, 0, 0, '', '', '', CURRENT_TIMESTAMP(6)
            )
            """,
            "seed DM task status",
        )
        if self.seed_competing_task_entities:
            self._sql(
                f"""
                INSERT INTO {self.control_database}.dm_task_status
                    (task_name, source_id, stage, unit, synced, checkpoint, master_binlog,
                     syncer_binlog, blocking_ddls, unresolved_groups, last_error, updated_at)
                VALUES
                    ({self._quote(self.warehouse_task_name)}, {self._quote(self.warehouse_source_id)},
                     'Paused', 'Sync', 0, {self.warehouse_checkpoint}, {self.warehouse_checkpoint},
                     {self.warehouse_checkpoint},
                     'ALTER TABLE `{self.archive_database}`.`{self.table}` ADD COLUMN `legacy_tag` INT UNIQUE',
                     '', '(8200, "unsupported add column legacy_tag constraint UNIQUE KEY")', CURRENT_TIMESTAMP(6)),
                    ('{self.task_name}-shadow', '{self.source_id}-legacy', 'Running', 'Sync', 1, 12, 12, 12,
                     '', '', '', CURRENT_TIMESTAMP(6))
                """,
                "seed DM task decoys",
            )
            self._sql(
                f"INSERT INTO {self.control_database}.dm_task_status "
                "(task_name, source_id, stage, unit, synced, checkpoint, master_binlog, "
                "syncer_binlog, blocking_ddls, unresolved_groups, last_error, updated_at) "
                f"VALUES ({self._quote(self.peer_task_name)}, {self._quote(self.peer_source_id)}, "
                f"'Running', 'Sync', 1, {self.peer_checkpoint}, {self.peer_checkpoint}, "
                f"{self.peer_checkpoint}, '', '', '', CURRENT_TIMESTAMP(6))",
                "seed same-source healthy DM task",
            )
            self._sql(
                f"INSERT INTO {self.control_database}.dm_task_history "
                "(action_id, task_name, action, status, created_at) "
                "VALUES (9001, 'warehouse-history', 'skip', 'completed', CURRENT_TIMESTAMP(6))",
                "seed warehouse DM task noise",
            )
            self._sql(
                f"""
                INSERT INTO {self.control_database}.dm_binlog_events
                    (event_id, task_name, source_id, event_type, event_sql, status,
                     error_message, replacement_sql, created_at)
                VALUES
                    (7001, {self._quote(self.warehouse_task_name)}, {self._quote(self.warehouse_source_id)}, 'DDL',
                     'ALTER TABLE `{self.archive_database}`.`{self.table}` ADD COLUMN `legacy_tag` INT UNIQUE',
                     'failed', '(8200, "unsupported add column legacy_tag constraint UNIQUE KEY")',
                     '', CURRENT_TIMESTAMP(6))
                """,
                "seed warehouse DM event noise",
            )
        self._sql(
            f"INSERT INTO {self.control_database}.dm_worker_logs (level, message, created_at) "
            "VALUES ('INFO', 'DM worker registered source and started full-plus-incremental sync', CURRENT_TIMESTAMP(6))",
            "seed DM worker log",
        )
        if self.seed_competing_task_entities:
            self._sql(
                f"INSERT INTO {self.control_database}.dm_worker_logs (level, message, created_at) VALUES "
                f"('ERROR', '{self.warehouse_task_name} source {self.warehouse_source_id} failed legacy_tag DDL at event 7001', CURRENT_TIMESTAMP(6)), "
                "('WARN', 'admission-shadow source mysql-admission-source-legacy has an old successful checkpoint', CURRENT_TIMESTAMP(6))",
                "seed DM competing worker logs",
            )

    def _start_relay(self) -> None:
        if self._thread is not None:
            raise RuntimeError(f"DM relay already running: task={self.task_name!r}")
        self._stop_event = threading.Event()
        self._worker_error = None
        self._thread = threading.Thread(
            target=self._relay_loop,
            name=f"aiopsbench-dm-{self.task_name}",
            daemon=True,
        )
        self._thread.start()

    def _stop_relay(self, *, raise_worker_error: bool) -> None:
        if self._thread is None:
            return
        if self._stop_event is None:
            raise RuntimeError(f"DM relay has a thread but no stop event: task={self.task_name!r}")
        self._stop_event.set()
        self._thread.join(timeout=self.env.sql_timeout_seconds + 5)
        if self._thread.is_alive():
            raise RuntimeError(f"DM relay did not stop: task={self.task_name!r}")
        thread_error = self._worker_error
        self._thread = None
        self._stop_event = None
        self._worker_error = None
        if raise_worker_error and thread_error is not None:
            raise RuntimeError(
                f"DM relay failed: task={self.task_name!r}, error={thread_error!r}"
            ) from thread_error

    def _relay_loop(self) -> None:
        try:
            with self._connect(self.control_database) as control:
                while not self._stop_event.is_set():
                    action = self._next_action(control)
                    if action is not None:
                        self._process_action(control, action)
                        continue
                    state = self._task_row(control)
                    if state["stage"] == "Running":
                        event = self._next_pending_event(control)
                        if event is not None:
                            self._process_event(control, event)
                            continue
                    time.sleep(0.05)
        except Exception as exc:
            self._worker_error = exc
            self._stop_event.set()

    def _task_row(self, control) -> dict[str, object]:
        with control.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT task_name, source_id, stage, unit, synced, checkpoint, master_binlog, "
                "syncer_binlog, blocking_ddls, unresolved_groups, last_error "
                "FROM dm_task_status WHERE task_name = %s",
                (self.task_name,),
            )
            rows = cursor.fetchall()
        if len(rows) != 1:
            raise RuntimeError(f"DM task status row mismatch: task={self.task_name!r}, rows={rows!r}")
        if rows[0]["source_id"] != self.source_id:
            raise RuntimeError(
                f"DM task source mismatch: task={self.task_name!r}, "
                f"expected_source={self.source_id!r}, observed_source={rows[0]['source_id']!r}"
            )
        return rows[0]

    def _next_action(self, control):
        with control.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT action_id, task_name, action, replacement_sql "
                "FROM dm_actions WHERE task_name = %s AND status = 'pending' "
                "ORDER BY action_id LIMIT 1",
                (self.task_name,),
            )
            return cursor.fetchone()

    def _next_pending_event(self, control):
        with control.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT event_id, event_type, event_sql FROM dm_binlog_events "
                "WHERE task_name = %s AND status = 'pending' ORDER BY event_id LIMIT 1",
                (self.task_name,),
            )
            return cursor.fetchone()

    def _process_event(self, control, event: dict[str, object]) -> None:
        event_id = int(event["event_id"])
        event_type = str(event["event_type"])
        sql = str(event["event_sql"])
        try:
            with self._connect(self.db) as target:
                self._direct_execute(target, sql)
        except pymysql.MySQLError as exc:
            self._mark_event_failed(control, event_id, sql, str(exc))
            return
        if event_type == "DDL":
            raise RuntimeError(
                f"DM fault DDL unexpectedly succeeded downstream: task={self.task_name!r}, "
                f"event_id={event_id}, sql={sql!r}"
            )
        self._mark_event_applied(control, event_id)

    def _process_action(self, control, action: dict[str, object]) -> None:
        action_id = int(action["action_id"])
        action_name = str(action["action"])
        replacement_sql = str(action["replacement_sql"])
        with control.cursor() as cursor:
            cursor.execute(
                "UPDATE dm_actions SET status = 'processing' WHERE action_id = %s",
                (action_id,),
            )
        try:
            state = self._task_row(control)
            if action_name in {"replace", "inject"}:
                if state["stage"] != "Paused":
                    raise RuntimeError(f"DM replace requires Paused task: state={state!r}")
                event = self._failed_event(control)
                if event is None:
                    raise RuntimeError(f"DM replace has no failed event: task={self.task_name!r}")
                with self._connect(self.db) as target:
                    self._direct_execute(target, replacement_sql)
                self._complete_repair(control, int(event["event_id"]), replacement_sql)
                self._complete_pending_event(control, action_name)
            elif action_name == "skip":
                event = self._failed_event(control)
                if event is None:
                    raise RuntimeError(f"DM skip has no failed event: task={self.task_name!r}")
                self._skip_failed_event(control, int(event["event_id"]), replacement_sql)
                self._complete_pending_event(control, action_name)
            elif action_name == "resume":
                with control.cursor() as cursor:
                    cursor.execute(
                        "UPDATE dm_task_status SET stage = 'Running', updated_at = CURRENT_TIMESTAMP(6) "
                        "WHERE task_name = %s",
                        (self.task_name,),
                    )
                    self._log(control, "INFO", "DM task resume requested")
            else:
                raise ValueError(f"Unknown DM action in relay: action={action_name!r}")
        except (pymysql.MySQLError, RuntimeError, ValueError) as exc:
            with control.cursor() as cursor:
                cursor.execute(
                    "UPDATE dm_actions SET status = 'error', error_message = %s WHERE action_id = %s",
                    (str(exc), action_id),
                )
            self._log(control, "ERROR", f"DM action {action_name} failed: {exc}")
            return
        with control.cursor() as cursor:
            cursor.execute(
                "UPDATE dm_actions SET status = 'completed', error_message = '' WHERE action_id = %s",
                (action_id,),
            )
            cursor.execute(
                "INSERT INTO dm_task_history (action_id, task_name, action, status, created_at) "
                "VALUES (%s, %s, %s, 'completed', CURRENT_TIMESTAMP(6))",
                (action_id, self.task_name, action_name),
            )
        self._log(control, "INFO", f"DM action {action_name} completed")

    def _failed_event(self, control):
        with control.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT event_id, event_sql FROM dm_binlog_events "
                "WHERE task_name = %s AND status = 'failed' ORDER BY event_id LIMIT 1",
                (self.task_name,),
            )
            return cursor.fetchone()

    def _mark_event_failed(self, control, event_id: int, sql: str, error: str) -> None:
        with control.cursor() as cursor:
            cursor.execute(
                "UPDATE dm_binlog_events SET status = 'failed', error_message = %s "
                "WHERE event_id = %s",
                (error, event_id),
            )
            cursor.execute(
                "UPDATE dm_task_status SET stage = 'Paused', synced = 0, blocking_ddls = %s, "
                "last_error = %s, updated_at = CURRENT_TIMESTAMP(6) WHERE task_name = %s",
                (sql, error, self.task_name),
            )
        self._log(control, "ERROR", f"DM downstream DDL failed at event {event_id}: {error}")

    def _mark_event_applied(self, control, event_id: int) -> None:
        with control.cursor() as cursor:
            cursor.execute(
                "UPDATE dm_binlog_events SET status = 'applied' WHERE event_id = %s",
                (event_id,),
            )
            cursor.execute(
                "UPDATE dm_task_status SET checkpoint = %s, master_binlog = %s, syncer_binlog = %s, "
                "synced = 1, blocking_ddls = '', last_error = '', updated_at = CURRENT_TIMESTAMP(6) "
                "WHERE task_name = %s",
                (event_id, event_id, event_id, self.task_name),
            )
        self._log(control, "INFO", f"DM applied event {event_id}")

    def _complete_pending_event(self, control, action_name: str) -> None:
        event = self._next_pending_event(control)
        if event is None:
            raise RuntimeError(
                f"DM action has no pending event to apply: task={self.task_name!r}, action={action_name!r}"
            )
        self._process_event(control, event)
        next_event = self._next_pending_event(control)
        if next_event is not None and str(next_event["event_type"]) == "DDL":
            self._process_event(control, next_event)
        state = self._task_row(control)
        if state["stage"] == "Paused" and state["blocking_ddls"]:
            return
        if (
            state["stage"] != "Running"
            or int(state["synced"]) != 1
            or state["blocking_ddls"]
            or state["unresolved_groups"]
            or state["master_binlog"] != state["syncer_binlog"]
        ):
            raise RuntimeError(
                f"DM action did not reach synced state: task={self.task_name!r}, action={action_name!r}, "
                f"state={state!r}"
            )

    def _complete_repair(self, control, event_id: int, replacement_sql: str) -> None:
        with control.cursor() as cursor:
            cursor.execute(
                "UPDATE dm_binlog_events SET status = 'replaced', replacement_sql = '', "
                "error_message = '' WHERE event_id = %s",
                (event_id,),
            )
            cursor.execute(
                "UPDATE dm_task_status SET stage = 'Running', synced = 0, checkpoint = %s, "
                "master_binlog = %s, syncer_binlog = %s, blocking_ddls = '', last_error = '', "
                "updated_at = CURRENT_TIMESTAMP(6) WHERE task_name = %s",
                (event_id, event_id + 1, event_id, self.task_name),
            )
        self._log(control, "INFO", f"DM replaced failed DDL at event {event_id}: {replacement_sql}")

    def _skip_failed_event(self, control, event_id: int, replacement_sql: str) -> None:
        with control.cursor() as cursor:
            cursor.execute(
                "UPDATE dm_binlog_events SET status = 'skipped', replacement_sql = %s, "
                "error_message = '' WHERE event_id = %s",
                (replacement_sql, event_id),
            )
            cursor.execute(
                "UPDATE dm_task_status SET stage = 'Running', synced = 0, checkpoint = %s, "
                "master_binlog = %s, syncer_binlog = %s, blocking_ddls = '', last_error = '', "
                "updated_at = CURRENT_TIMESTAMP(6) WHERE task_name = %s",
                (event_id, event_id + 1, event_id, self.task_name),
            )
        self._log(control, "INFO", f"DM skipped failed DDL at event {event_id}")

    def _log(self, control, level: str, message: str) -> None:
        with control.cursor() as cursor:
            cursor.execute(
                "INSERT INTO dm_worker_logs (level, message, created_at) "
                "VALUES (%s, %s, CURRENT_TIMESTAMP(6))",
                (level, message[:512]),
            )

    def _wait_for_synced(self, timeout: float) -> None:
        deadline = time.monotonic() + float(timeout)
        while time.monotonic() < deadline:
            state = self._task_state()
            if state["stage"] == "Running" and int(state["synced"]) == 1:
                return
            time.sleep(0.1)
        raise RuntimeError(f"DM task did not become synced: task={self.task_name!r}, state={self._task_state()!r}")

    def _wait_for_paused(self, timeout: float) -> None:
        deadline = time.monotonic() + float(timeout)
        while time.monotonic() < deadline:
            state = self._task_state()
            if state["stage"] == "Paused" and state["blocking_ddls"]:
                return
            time.sleep(0.1)
        raise RuntimeError(f"DM task did not pause on failed DDL: task={self.task_name!r}, state={self._task_state()!r}")

    def _task_state(self) -> dict[str, object]:
        rows = self._rows(
            "SELECT task_name, source_id, stage, unit, synced, checkpoint, master_binlog, "
            f"syncer_binlog, blocking_ddls, unresolved_groups, last_error "
            f"FROM {self.control_database}.dm_task_status WHERE task_name = "
            f"{self._quote(self.task_name)}",
            "query DM task state",
        )
        if len(rows) != 1:
            raise RuntimeError(f"DM task state must contain exactly one task: task={self.task_name!r}, rows={rows!r}")
        names = (
            "task_name", "source_id", "stage", "unit", "synced", "checkpoint",
            "master_binlog", "syncer_binlog", "blocking_ddls", "unresolved_groups", "last_error",
        )
        return dict(zip(names, rows[0], strict=True))

    def _emit_failed_ddl(self) -> None:
        self._sql(
            f"ALTER TABLE {self.source_database}.{self.table} ADD COLUMN {self.first_column} INT",
            "apply upstream DM release column",
        )
        self._sql(
            f"ALTER TABLE {self.source_database}.{self.table} "
            f"ADD UNIQUE KEY {self.first_unique_key} ({self.first_column})",
            "apply upstream DM release unique constraint",
        )
        self._sql(
            f"ALTER TABLE {self.source_database}.{self.table} "
            f"ADD COLUMN {self.second_column} INT",
            "apply upstream DM release region column",
        )
        self._sql(
            f"ALTER TABLE {self.source_database}.{self.table} "
            f"ADD UNIQUE KEY {self.second_unique_key} ({self.second_column})",
            "apply upstream DM release region unique constraint",
        )
        self._sql(
            f"INSERT INTO {self.control_database}.dm_binlog_events "
            "(event_id, task_name, source_id, event_type, event_sql, status, error_message, replacement_sql, created_at) "
            f"VALUES (1, {self._quote(self.task_name)}, {self._quote(self.source_id)}, 'DDL', "
            f"{self._quote(self.failed_ddl_sql)}, 'pending', '', '', CURRENT_TIMESTAMP(6))",
            "emit upstream failed DM DDL",
        )
        self._sql(
            f"INSERT INTO {self.control_database}.dm_binlog_events "
            "(event_id, task_name, source_id, event_type, event_sql, status, error_message, replacement_sql, created_at) "
            f"VALUES (3, {self._quote(self.task_name)}, {self._quote(self.source_id)}, 'DDL', "
            f"{self._quote(self.second_failed_ddl_sql)}, 'pending', '', '', CURRENT_TIMESTAMP(6))",
            "emit upstream second failed DM DDL",
        )

    def _emit_pending_dml(self) -> None:
        upstream_sql = self.pending_dml_sql.replace(
            f"`{self.db}`.", f"`{self.source_database}`."
        )
        self._sql(upstream_sql, "emit upstream post-DDL business DML")
        self._sql(
            f"INSERT INTO {self.control_database}.dm_binlog_events "
            "(event_id, task_name, source_id, event_type, event_sql, status, error_message, replacement_sql, created_at) "
            f"VALUES (2, {self._quote(self.task_name)}, {self._quote(self.source_id)}, 'DML', "
            f"{self._quote(self.pending_dml_sql)}, 'pending', '', '', CURRENT_TIMESTAMP(6))",
            "queue pending DM DML",
        )
        second_upstream_sql = self.second_pending_dml_sql.replace(
            f"`{self.db}`.", f"`{self.source_database}`."
        )
        self._sql(second_upstream_sql, "emit upstream second post-DDL business DML")
        self._sql(
            f"INSERT INTO {self.control_database}.dm_binlog_events "
            "(event_id, task_name, source_id, event_type, event_sql, status, error_message, replacement_sql, created_at) "
            f"VALUES (4, {self._quote(self.task_name)}, {self._quote(self.source_id)}, 'DML', "
            f"{self._quote(self.second_pending_dml_sql)}, 'pending', '', '', CURRENT_TIMESTAMP(6))",
            "queue second pending DM DML",
        )

    def _verify_persistent_state(self) -> None:
        state = self._task_state()
        if state["stage"] != "Paused" or int(state["synced"]) != 0:
            raise RuntimeError(f"DM persisted task is not paused: task={self.task_name!r}, state={state!r}")
        source_columns = self._rows(
            f"SELECT COUNT(*) FROM information_schema.columns WHERE TABLE_SCHEMA = "
            f"{self._quote(self.source_database)} AND TABLE_NAME = {self._quote(self.table)} "
            f"AND COLUMN_NAME = {self._quote(self.first_column)}",
            "validate upstream DM failed-DDL column",
        )
        target_columns = self._rows(
            f"SELECT COUNT(*) FROM information_schema.columns WHERE TABLE_SCHEMA = "
            f"{self._quote(self.db)} AND TABLE_NAME = {self._quote(self.table)} "
            f"AND COLUMN_NAME = {self._quote(self.first_column)}",
            "validate downstream DM failed-DDL schema",
        )
        source_region_columns = self._rows(
            f"SELECT COUNT(*) FROM information_schema.columns WHERE TABLE_SCHEMA = "
            f"{self._quote(self.source_database)} AND TABLE_NAME = {self._quote(self.table)} "
            f"AND COLUMN_NAME = {self._quote(self.second_column)}",
            "validate upstream DM second failed-DDL column",
        )
        target_region_columns = self._rows(
            f"SELECT COUNT(*) FROM information_schema.columns WHERE TABLE_SCHEMA = "
            f"{self._quote(self.db)} AND TABLE_NAME = {self._quote(self.table)} "
            f"AND COLUMN_NAME = {self._quote(self.second_column)}",
            "validate downstream DM second failed-DDL schema",
        )
        events = self._rows(
            f"SELECT event_id, event_type, status FROM {self.control_database}.dm_binlog_events "
            "WHERE task_name = "
            f"{self._quote(self.task_name)} ORDER BY event_id",
            "validate DM event checkpoint",
        )
        expected_events = [
            [1, "DDL", "failed"],
            [2, "DML", "pending"],
            [3, "DDL", "pending"],
            [4, "DML", "pending"],
        ]
        if (
            source_columns != [[1]]
            or target_columns != [[0]]
            or source_region_columns != [[1]]
            or target_region_columns != [[0]]
            or events != expected_events
        ):
            raise RuntimeError(
                "TiDB DM fault activation found an invalid persisted schema state: "
                f"task={self.task_name!r}, status={state!r}, source_columns={source_columns!r}, "
                f"target_columns={target_columns!r}, source_region_columns={source_region_columns!r}, "
                f"target_region_columns={target_region_columns!r}, events={events!r}"
            )
