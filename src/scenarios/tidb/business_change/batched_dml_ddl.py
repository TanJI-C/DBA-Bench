import json
import threading
from dataclasses import dataclass

import pymysql

from src.scenarios.evaluation.tidb.business_change.batched_dml_ddl import (
    TidbBusinessChangeBc03EvaluatorCase,
    TidbBusinessChangeBc03SettlementEvaluatorCase,
)
from src.scenarios.evaluation.protocol import structured_reference_report
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..common import connect_tidb, join_thread
from ..runtime import TIDB_V8_1_0, tidb_runtime


DATABASE = "benchops"
ORDERS_TABLE = "bc03_orders"
JOB_TABLE = "bc03_change_jobs"
BATCH_TABLE = "bc03_change_batches"
JOB_ID = "bc03_retention_2026q2"
ROW_COUNT = 300_000
TARGET_ROWS = 44_777
INITIAL_ARCHIVED_ROWS = 20_000
INITIAL_CHECKPOINT_ROWS = 11_251
INDEX_COLUMNS = ("archive_state", "retention_class", "order_id")
FIXTURE_INSERT_CHUNK_ROWS = 10_000
SETTLEMENT_RELEASE_GRACE_SECONDS = 2.0
SETTLEMENT_OBSERVE_SECONDS = 0.05


def _workload(
    *,
    database: str = DATABASE,
    orders_table: str = ORDERS_TABLE,
    job_table: str = JOB_TABLE,
    batch_table: str = BATCH_TABLE,
    policy_table: str = "bc03_retention_policies",
    scope_table: str = "bc03_archive_scopes",
    hold_table: str = "bc03_archive_holds",
    release_queue_table: str = "bc03_release_queue",
    schema_audit_table: str = "bc03_schema_audit",
    capacity_events_table: str = "bc03_capacity_events",
    worker_count: int = 2,
    seed: int = 20260805,
    warmup_seconds: float = 20,
    include_neighbor_noise: bool = True,
) -> BackgroundWorkloadSpec:
    table = f"{database}.{orders_table}"
    profiles = (
        WorkloadProfile(
            name="bc03_checkout_point_lookup",
            sql=(
                f"SELECT order_id, tenant_id, status, amount FROM {table} "
                "WHERE order_id = MOD(CAST(UNIX_TIMESTAMP(NOW()) AS UNSIGNED), 300000) + 1"
            ),
            qps=1.2,
            tier="FOREGROUND_READ",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="bc03_checkout_order_touch",
            sql=(
                f"UPDATE {table} SET touch_version = touch_version + 1 "
                "WHERE order_id = 2 AND retention_class = 'ACTIVE'"
            ),
            qps=0.20,
            tier="FOREGROUND_WRITE",
            application_name="checkout-api",
            commit=True,
        ),
        WorkloadProfile(
            name="bc03_settlement_reconciliation",
            sql=(
                f"UPDATE /* bc03-settlement-profile */ {table} "
                "SET touch_version = touch_version + 1, updated_at = NOW() "
                "WHERE order_id = MOD(CAST(UNIX_TIMESTAMP(NOW()) AS UNSIGNED), 300000) + 1 "
                "AND status = 'SETTLED' AND retention_class = 'EXPIRED' AND archive_state = 'LIVE'"
            ),
            qps=0.25,
            tier="SETTLEMENT",
            application_name="settlement-service",
            commit=True,
        ),
        WorkloadProfile(
            name="bc03_customer_recent_orders",
            sql=(
                f"SELECT order_id, status, amount, updated_at FROM {table} "
                "WHERE customer_id = MOD(CAST(UNIX_TIMESTAMP(NOW()) AS UNSIGNED), 10000) + 1 "
                "ORDER BY updated_at DESC, order_id DESC LIMIT 30"
            ),
            qps=0.55,
            tier="FOREGROUND_READ",
            application_name="customer-order-api",
        ),
        WorkloadProfile(
            name="bc03_tenant_open_order_rollup",
            sql=(
                f"SELECT order_id, customer_id, amount, status FROM {table} "
                "WHERE tenant_id = 17 AND status = 'PAID' ORDER BY order_id DESC LIMIT 40"
            ),
            qps=0.40,
            tier="FOREGROUND_READ",
            application_name="merchant-console",
        ),
        WorkloadProfile(
            name="bc03_fulfillment_feed",
            sql=(
                f"SELECT order_id, tenant_id, customer_id, amount FROM {table} "
                "WHERE order_id = 285002 AND status = 'PAID'"
            ),
            qps=0.35,
            tier="FOREGROUND_READ",
            application_name="fulfillment-worker",
        ),
        WorkloadProfile(
            name="bc03_fraud_review_window",
            sql=(
                f"SELECT tenant_id, COUNT(*), COALESCE(SUM(amount), 0) FROM {table} "
                "WHERE order_id > 280000 AND status = 'REVIEW' AND amount > 700 "
                "GROUP BY tenant_id ORDER BY SUM(amount) DESC LIMIT 20"
            ),
            qps=0.18,
            tier="RISK_SCAN",
            application_name="fraud-scoring",
        ),
        WorkloadProfile(
            name="bc03_settlement_daily_rollup",
            sql=(
                f"SELECT tenant_id, DATE(updated_at), COUNT(*), COALESCE(SUM(amount), 0) FROM {table} "
                "WHERE order_id > 280000 AND updated_at >= '2026-07-01' AND status = 'SETTLED' "
                "GROUP BY tenant_id, DATE(updated_at) ORDER BY DATE(updated_at) DESC, tenant_id LIMIT 200"
            ),
            qps=0.04,
            tier="SETTLEMENT",
            application_name="settlement-service",
        ),
        WorkloadProfile(
            name="bc03_archive_progress_live",
            sql=(
                f"SELECT archive_state, retention_class, COUNT(*) FROM {table} "
                "WHERE order_id > 280000 GROUP BY archive_state, retention_class "
                "ORDER BY archive_state, retention_class"
            ),
            qps=0.12,
            tier="CHANGE_OBSERVABILITY",
            application_name="release-controller",
        ),
        WorkloadProfile(
            name="bc03_archive_cursor_probe",
            sql=(
                f"SELECT MIN(order_id), MAX(order_id), COUNT(*) FROM {table} "
                "WHERE order_id > 280000 AND retention_class = 'EXPIRED' AND archive_state = 'LIVE'"
            ),
            qps=0.12,
            tier="CHANGE_OBSERVABILITY",
            application_name="retention-controller",
        ),
        WorkloadProfile(
            name="bc03_live_change_job",
            sql=(
                f"SELECT job_id, state, last_pk, rows_completed, target_rows, ddl_index_name "
                f"FROM {database}.{job_table} ORDER BY updated_at DESC LIMIT 20"
            ),
            qps=0.18,
            tier="CHANGE_OBSERVABILITY",
            application_name="release-controller",
        ),
        WorkloadProfile(
            name="bc03_batch_history",
            sql=(
                f"SELECT job_id, batch_no, lower_pk, upper_pk, affected_rows, observed_p95_ms "
                f"FROM {database}.{batch_table} ORDER BY recorded_at DESC LIMIT 50"
            ),
            qps=0.14,
            tier="CHANGE_OBSERVABILITY",
            application_name="release-controller",
        ),
        WorkloadProfile(
            name="bc03_index_catalog",
            sql=f"SHOW INDEX FROM {table}",
            qps=0.12,
            tier="SCHEMA_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="bc03_ddl_job_history",
            sql="ADMIN SHOW DDL JOBS 30",
            qps=0.10,
            tier="SCHEMA_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="bc03_mdl_observer",
            sql="SELECT * FROM mysql.tidb_mdl_view ORDER BY txnstart LIMIT 30",
            qps=0.08,
            tier="SCHEMA_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="bc03_release_queue",
            sql=(
                f"SELECT release_id, service_name, change_type, state, risk_level, scheduled_at "
                f"FROM {database}.{release_queue_table} ORDER BY scheduled_at DESC LIMIT 40"
            ),
            qps=0.12,
            tier="CHANGE_NEIGHBOR",
            application_name="release-portal",
        ),
        WorkloadProfile(
            name="bc03_schema_audit",
            sql=(
                f"SELECT object_name, operation, state, duration_ms, created_at FROM {database}.{schema_audit_table} "
                "ORDER BY created_at DESC LIMIT 50"
            ),
            qps=0.12,
            tier="CHANGE_NEIGHBOR",
            application_name="schema-audit",
        ),
        WorkloadProfile(
            name="bc03_capacity_events",
            sql=(
                f"SELECT store_name, event_type, pending_bytes, write_stall_count, created_at "
                f"FROM {database}.{capacity_events_table} ORDER BY created_at DESC LIMIT 60"
            ),
            qps=0.10,
            tier="STORAGE_NEIGHBOR",
            application_name="capacity-observer",
        ),
        WorkloadProfile(
            name="bc03_retention_policy_catalog",
            sql=(
                f"SELECT policy_id, object_name, cutoff_days, state, scope_id FROM {database}.{policy_table} "
                "ORDER BY policy_id"
            ),
            qps=0.12,
            tier="CHANGE_NEIGHBOR",
            application_name="retention-controller",
        ),
        WorkloadProfile(
            name="bc03_historical_job_failures",
            sql=(
                f"SELECT job_id, state, rows_completed, target_rows, error_text FROM {DATABASE}.{JOB_TABLE} "
                "WHERE state IN ('FAILED', 'PAUSED') ORDER BY updated_at DESC"
            ),
            qps=0.10,
            tier="CHANGE_NEIGHBOR",
            application_name="release-controller",
        ),
        WorkloadProfile(
            name="bc03_compaction_config",
            sql=(
                "SHOW CONFIG WHERE type = 'tikv' AND name IN ("
                "'rocksdb.defaultcf.soft-pending-compaction-bytes-limit',"
                "'rocksdb.defaultcf.hard-pending-compaction-bytes-limit')"
            ),
            qps=0.03,
            tier="STORAGE_OBSERVABILITY",
            application_name="capacity-observer",
        ),
        WorkloadProfile(
            name="bc03_table_storage_stats",
            sql=(
                "SELECT table_schema, table_name, table_size, table_keys FROM information_schema.tikv_region_status "
                f"WHERE db_name = '{DATABASE}' ORDER BY table_size DESC LIMIT 30"
            ),
            qps=0.05,
            tier="STORAGE_OBSERVABILITY",
            application_name="capacity-observer",
        ),
        WorkloadProfile(
            name="bc03_statement_summary",
            sql=(
                "SELECT digest_text, exec_count, avg_latency, sum_latency "
                "FROM information_schema.cluster_statements_summary ORDER BY sum_latency DESC LIMIT 40"
            ),
            qps=0.05,
            tier="SQL_OBSERVABILITY",
            application_name="sql-observer",
        ),
        WorkloadProfile(
            name="bc03_tenant_42_archive_preview",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM {table} "
                "WHERE order_id > 280000 AND tenant_id = 42 AND retention_class = 'EXPIRED'"
            ),
            qps=0.10,
            tier="CHANGE_NEIGHBOR",
            application_name="tenant-data-lifecycle",
        ),
        WorkloadProfile(
            name="bc03_cancelled_order_cleanup_preview",
            sql=(
                f"SELECT MIN(order_id), MAX(order_id), COUNT(*) FROM {table} "
                "WHERE order_id > 280000 AND status = 'CANCELLED' AND updated_at < '2025-01-01'"
            ),
            qps=0.09,
            tier="CHANGE_NEIGHBOR",
            application_name="order-cleanup",
        ),
        WorkloadProfile(
            name="bc03_payload_rewrite_preview",
            sql=(
                f"SELECT LEFT(payload, 12), COUNT(*) FROM {table} WHERE order_id BETWEEN 80001 AND 85000 "
                "GROUP BY LEFT(payload, 12) ORDER BY COUNT(*) DESC LIMIT 20"
            ),
            qps=0.06,
            tier="CHANGE_NEIGHBOR",
            application_name="privacy-rewrite",
        ),
        WorkloadProfile(
            name="bc03_missing_release_budget",
            sql=f"SELECT * FROM {database}.bc03_release_slo_budget_missing ORDER BY service_name",
            qps=0.04,
            tier="LOG_NOISE",
            application_name="release-portal",
        ),
        WorkloadProfile(
            name="bc03_missing_archive_checkpoint",
            sql=f"SELECT * FROM {database}.bc03_archive_checkpoint_cache_missing ORDER BY job_id",
            qps=0.04,
            tier="LOG_NOISE",
            application_name="retention-controller",
        ),
        WorkloadProfile(
            name="bc03_missing_compaction_forecast",
            sql=f"SELECT * FROM {database}.bc03_compaction_forecast_missing ORDER BY store_name",
            qps=0.04,
            tier="LOG_NOISE",
            application_name="capacity-observer",
        ),
        WorkloadProfile(
            name="bc03_missing_ddl_eta",
            sql=f"SELECT * FROM {database}.bc03_ddl_eta_cache_missing ORDER BY job_id",
            qps=0.04,
            tier="LOG_NOISE",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="bc03_scope_membership_probe",
            sql=(
                f"SELECT scope_id, tenant_id, scope_state FROM {database}.{scope_table} "
                "ORDER BY scope_id, tenant_id LIMIT 120"
            ),
            qps=0.08,
            tier="CHANGE_NEIGHBOR",
            application_name="release-controller",
        ),
        WorkloadProfile(
            name="bc03_order_hold_probe",
            sql=(
                f"SELECT hold_id, order_id, tenant_id, hold_state FROM {database}.{hold_table} "
                "ORDER BY updated_at DESC, hold_id DESC LIMIT 120"
            ),
            qps=0.08,
            tier="CHANGE_NEIGHBOR",
            application_name="risk-controller",
        ),
        WorkloadProfile(
            name="bc03_unrelated_inventory_write",
            sql=(
                f"INSERT INTO {database}.bc03_inventory_touch (sku, touch_count, updated_at) "
                "VALUES (MOD(CAST(UNIX_TIMESTAMP(NOW()) AS UNSIGNED), 1000) + 1, 1, NOW()) "
                "ON DUPLICATE KEY UPDATE touch_count = touch_count + 1, updated_at = NOW()"
            ),
            qps=0.20,
            tier="FOREGROUND_WRITE",
            application_name="inventory-service",
            commit=True,
        ),
    )
    compact_profile_names = frozenset({
        "bc03_checkout_point_lookup",
        "bc03_checkout_order_touch",
        "bc03_settlement_reconciliation",
        "bc03_customer_recent_orders",
        "bc03_tenant_open_order_rollup",
        "bc03_fulfillment_feed",
        "bc03_archive_progress_live",
        "bc03_archive_cursor_probe",
        "bc03_live_change_job",
        "bc03_batch_history",
        "bc03_index_catalog",
        "bc03_ddl_job_history",
    })
    if not include_neighbor_noise:
        profiles = tuple(profile for profile in profiles if profile.name in compact_profile_names)
    return BackgroundWorkloadSpec(
        profiles=profiles,
        worker_count=worker_count,
        seed=seed,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=warmup_seconds,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeBc03Case(TiDBScenarioCase):
    database: str
    orders_table: str
    job_table: str
    batch_table: str
    job_id: str
    row_count: int
    target_rows: int
    index_columns: tuple[str, ...]
    immutable_truth_sql: str
    slo_profile_names: tuple[str, ...]
    slo_p95_ms: float
    reference_path: tuple[str, ...]
    target_scope_id: str
    target_policy_id: int
    policy_table: str = "bc03_retention_policies"
    scope_table: str = "bc03_archive_scopes"
    hold_table: str = "bc03_archive_holds"
    release_queue_table: str = "bc03_release_queue"
    schema_audit_table: str = "bc03_schema_audit"
    capacity_events_table: str = "bc03_capacity_events"
    initial_archived_rows: int = INITIAL_ARCHIVED_ROWS
    initial_checkpoint_rows: int = INITIAL_CHECKPOINT_ROWS
    initial_checkpoint_span: int = 25_000
    seed_change_neighbor_noise: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeBc03ForRetentionArchiveScenarioCase(TidbBusinessChangeBc03Case):
    pass


BC03_CASE = TidbBusinessChangeBc03ForRetentionArchiveScenarioCase(
    case_id="retention_archive_online_index",
    reference_report=structured_reference_report(
        case_id="retention_archive_online_index",
        factors=(
            "the target job is bound to one approved policy and tenant scope while a neighboring policy uses the same table",
            "the large-table update must leave durable progress that can survive business concurrency",
        ),
        changes=(
            "archived only the policy-bound approved-scope rows without active holds with durable progress evidence",
            "created the required public online archive_state retention_class order_id index",
        ),
        verification=(
            "job state, target-row count, progress chain, non-target checksum, and business truth were verified",
            "foreground p95 stayed within 250ms and the required index became public",
        ),
        summary="The reference path completed the policy-bound retention archive after reconciling an interrupted job and live settlement activity.",
    ),
    case_no=0,
    evaluator=TidbBusinessChangeBc03EvaluatorCase,
    title="Execute a large-table archive update and online index build under foreground SLO.",
    alert=(
        "P1 生产变更窗口：请恢复并完成 benchops.bc03_change_jobs 中 job_id='bc03_retention_2026q2' 的保留期归档。"
        "该任务处于一次中断后的恢复阶段：请先核对订单状态、当前 job 计数和本 job 的审计进度，"
        "处理已经提交但尚未留下完整审计记录的部分，再继续完成当前批准范围内的剩余目标。"
        "归档资格由当前 job 绑定的批准策略、公开租户范围和订单保护记录共同决定；请只更新已经核对过的目标订单，"
        "并为已完成的部分留下可审计的进度记录。该任务授权你在核对后的目标订单上执行归档写入，"
        "更新本次 change job，并追加本次 job 的进度记录；不授权改写其他订单的业务字段或其他控制表。"
        "同时在线建立以 archive_state、retention_class、order_id 为前三列的 public 联合索引。"
        "全过程保持 checkout/customer/merchant/fulfillment 前台 p95 不超过 250ms，不能重启集群、"
        "不能调高 TiKV 流控阈值、不能删除或截断业务数据，也不能终止业务或结算会话。环境中有并行发版、历史失败作业、"
        "相似清理任务、DDL/MDL、compaction、租户范围和订单保护记录，请只处理本次目标并验证业务真值。"
    ),
    initial_state={
        "job_state": "PAUSED",
        "target_rows": TARGET_ROWS,
        "archive_state": "20,000 already archived; 24,777 eligible still LIVE; deferred and active-hold rows excluded",
        "required_index": "absent",
        "foreground_slo_p95_ms": 250.0,
    },
    expected_target={
        "job_state": "a public complete state (SUCCEEDED, COMPLETED, or DONE)",
        "archived_target_rows": TARGET_ROWS,
        "non_target_rows_changed": 0,
        "required_index": "public",
        "foreground_slo_p95_ms": 250.0,
        "business_truth": "preserved",
    },
    background_workload=_workload(),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=180,
        tikv_memory_mb=4096,
        tidb_memory_mb=8192,
        readiness_timeout_seconds=1800,
    ),
    database=DATABASE,
    orders_table=ORDERS_TABLE,
    job_table=JOB_TABLE,
    batch_table=BATCH_TABLE,
    job_id=JOB_ID,
    row_count=ROW_COUNT,
    target_rows=TARGET_ROWS,
    index_columns=INDEX_COLUMNS,
    immutable_truth_sql=(
        f"SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
        "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, customer_id, status, amount, "
        f"retention_class, payload))), 0) FROM {DATABASE}.{ORDERS_TABLE}"
    ),
    slo_profile_names=(
        "bc03_checkout_point_lookup",
        "bc03_checkout_order_touch",
        "bc03_customer_recent_orders",
        "bc03_tenant_open_order_rollup",
        "bc03_fulfillment_feed",
    ),
    slo_p95_ms=250.0,
    reference_path=(
        "the target change is PAUSED after an interruption while foreground traffic and unrelated changes are active",
        "the live job is separated from historical and neighboring jobs and its policy binding is resolved",
        "the policy binding is followed to the public tenant scope and the approved population is separated from deferred tenants",
        "active holds are excluded while released holds remain eligible, then this scope is reconciled with orders, counters and checkpoints",
        "the missing audit state is appended for already-owned eligible rows without rewriting committed history",
        "a resume attempt meets an active settlement transaction on the remaining eligible population and the failed attempt is adapted",
        "all scoped targets, progress records, public index, foreground SLO, protected rows and immutable truth converge",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.795691,
        reference_run_ids=(
            "reference-78__tidb_business_change_batched_dml_ddl__retention_archive_online_index__mock_alt__r001",
        ),
    ),
    target_scope_id="bc03_retention_2026q2_standard",
    target_policy_id=1,
)


BC03_SETTLEMENT_CASE = TidbBusinessChangeBc03ForRetentionArchiveScenarioCase(
    case_id="settlement_archive_online_index",
    reference_report=structured_reference_report(
        case_id="settlement_archive_online_index",
        factors=(
            "the settlement archive job has a distinct policy and tenant cohort on the same business table",
            "the interrupted checkpoint still requires bounded recovery and an online index",
        ),
        changes=(
            "reconciled the settlement archive cohort without touching held or deferred tenants",
            "completed the durable checkpoint chain and public archive lookup index",
        ),
        verification=(
            "the settlement job, target checksum, protected control state and foreground SLO converged",
            "the online index became public without rewriting committed checkpoints",
        ),
        summary="The settlement archive reference path completed a bounded resumable DML and online DDL change.",
    ),
    case_no=1,
    evaluator=TidbBusinessChangeBc03SettlementEvaluatorCase,
    title="Resume a settlement archive and build its online index under checkout SLO.",
    alert=(
        "P1 生产变更窗口：请恢复 benchops.settlement_orders 中 job_id='settlement_archive_2026q3' 的归档。"
        "先核对当前 job、持久 checkpoint、批准策略、公开范围和 settlement hold，再处理已经提交但尚未审计的部分；"
        "只更新当前批准范围内的目标订单，追加本 job 的审计进度，并在线建立 archive_state、retention_class、order_id 前缀索引。"
        "请保持 checkout、settlement、merchant 和 fulfillment 前台 p95 不超过 250ms；不得重启集群、修改金额等业务字段、"
        "删除数据、改写已提交 checkpoint、终止业务会话或修改 TiKV 流控参数。"
    ),
    initial_state={
        "job_state": "PAUSED",
        "target_rows": 26_777,
        "archive_state": "12,000 already archived; remaining approved settlement rows are LIVE",
        "required_index": "absent",
        "foreground_slo_p95_ms": 250.0,
    },
    expected_target={
        "job_state": "a public complete state",
        "archived_target_rows": 26_777,
        "non_target_rows_changed": 0,
        "required_index": "public",
        "foreground_slo_p95_ms": 250.0,
        "business_truth": "preserved",
    },
    background_workload=_workload(
        database="benchops",
        orders_table="settlement_orders",
        job_table="settlement_change_jobs",
        batch_table="settlement_change_batches",
        policy_table="settlement_retention_policies",
        scope_table="settlement_archive_scopes",
        hold_table="settlement_archive_holds",
        release_queue_table="settlement_release_queue",
        schema_audit_table="settlement_schema_audit",
        capacity_events_table="settlement_capacity_events",
        worker_count=2,
        seed=20260813,
        warmup_seconds=12,
        include_neighbor_noise=False,
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0, pd_count=3, tikv_count=3, tidb_count=2,
        sql_timeout_seconds=180, tikv_memory_mb=4096, tidb_memory_mb=8192,
        readiness_timeout_seconds=1800,
    ),
    database="benchops",
    orders_table="settlement_orders",
    job_table="settlement_change_jobs",
    batch_table="settlement_change_batches",
    job_id="settlement_archive_2026q3",
    row_count=180_000,
    target_rows=26_777,
    index_columns=("archive_state", "retention_class", "order_id"),
    immutable_truth_sql=(
        "SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
        "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, customer_id, status, amount, "
        "retention_class, payload))), 0) FROM benchops.settlement_orders"
    ),
    slo_profile_names=(
        "bc03_checkout_point_lookup", "bc03_checkout_order_touch",
        "bc03_customer_recent_orders", "bc03_tenant_open_order_rollup",
        "bc03_fulfillment_feed",
    ),
    slo_p95_ms=250.0,
    reference_path=(
        "the settlement archive job is paused after a partial commit while live checkout traffic continues",
        "the job binding, public tenant scope, archive holds and the committed checkpoint prefix resolve the "
        "eligible population and its unaudited orphan batch in one reconciliation",
        "bounded resumable batches complete the archive, the checkpoint chain closes, and the public online "
        "index and foreground SLO verify completion",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.0,
        reference_run_ids=(
            "tidb-reference-12__"
            "tidb_business_change_batched_dml_ddl__settlement_archive_online_index__"
            "mock__r001",
        ),
    ),
    target_scope_id="settlement_archive_2026q3_standard",
    target_policy_id=11,
    policy_table="settlement_retention_policies",
    scope_table="settlement_archive_scopes",
    hold_table="settlement_archive_holds",
    release_queue_table="settlement_release_queue",
    schema_audit_table="settlement_schema_audit",
    capacity_events_table="settlement_capacity_events",
    initial_archived_rows=12_000,
    initial_checkpoint_rows=6_751,
    initial_checkpoint_span=15_000,
    seed_change_neighbor_noise=False,
)


class TidbBusinessChangeBatchedDmlDdlScenario(TiDBScenario):
    scenario_id = "tidb_business_change_batched_dml_ddl"
    description = "Resumable large-table DML and online DDL under a live TiDB foreground SLO."
    cases = (BC03_CASE, BC03_SETTLEMENT_CASE)

    def build_fault_plan(self, case: TidbBusinessChangeBc03Case) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangeBc03Injector,
                config={
                    "database": case.database,
                    "orders_table": case.orders_table,
                    "job_table": case.job_table,
                    "batch_table": case.batch_table,
                    "job_id": case.job_id,
                    "row_count": case.row_count,
                    "target_rows": case.target_rows,
                    "target_scope_id": case.target_scope_id,
                    "target_policy_id": case.target_policy_id,
                    "policy_table": case.policy_table,
                    "scope_table": case.scope_table,
                    "hold_table": case.hold_table,
                    "release_queue_table": case.release_queue_table,
                    "schema_audit_table": case.schema_audit_table,
                    "capacity_events_table": case.capacity_events_table,
                    "initial_archived_rows": case.initial_archived_rows,
                    "initial_checkpoint_rows": case.initial_checkpoint_rows,
                    "initial_checkpoint_span": case.initial_checkpoint_span,
                    "seed_change_neighbor_noise": case.seed_change_neighbor_noise,
                    "index_columns": case.index_columns,
                    "immutable_truth_sql": case.immutable_truth_sql,
                },
            ),
        )


__all__ = (
    "TidbBusinessChangeBc03Case",
    "TidbBusinessChangeBc03ForRetentionArchiveScenarioCase",
    "BC03_SETTLEMENT_CASE",
    "TidbBusinessChangeBatchedDmlDdlScenario",
)

from collections.abc import Mapping

from src.database.sql import require_result_rows
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.tidb.common import (
    require_sql_success,
    validate_sql_identifier,
)


class TidbBusinessChangeBc03Injector(BaseFaultInjector):
    """Create BC03's live large-table retention change and production-like neighbors."""

    def __init__(self):
        self._runtime_stop: threading.Event | None = None
        self._runtime_ready: threading.Event | None = None
        self._runtime_thread: threading.Thread | None = None
        self._runtime_error: Exception | None = None
        self._previous_lock_wait_timeout: int | None = None
        self._previous_session_lock_wait_timeout: int | None = None
        self._previous_session_txn_mode: str | None = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        with context.env.metrics_hidden():
            self._create_schema(context.env)
            self._load_fixture(context.env)
            self._verify_initial_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._set_lock_wait_timeout(context.env)
        self._verify_initial_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        state = self._initial_state(context.env)
        if self.seed_change_neighbor_noise:
            self._start_settlement_interference(context.env)
        return {
            "bc03_immutable_business_truth": self._immutable_truth(context.env),
            "bc03_initial_state": state,
            "bc03_target_distribution": self._target_distribution(context.env),
            "bc03_initial_checkpoints": self._checkpoint_rows(context.env),
            "bc03_initial_indexes": self._index_rows(context.env),
            "bc03_neighbor_counts": self._neighbor_counts(context.env),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._stop_settlement_interference()
        self._restore_lock_wait_timeout(context.env)
        self._initial_state(context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._stop_settlement_interference()
        self._restore_lock_wait_timeout(context.env)
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.database}"),
            f"BC03 drop owned database {self.database}",
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.database = validate_sql_identifier(str(config["database"]), "database")
        self.orders_table = validate_sql_identifier(str(config["orders_table"]), "orders table")
        self.job_table = validate_sql_identifier(str(config["job_table"]), "job table")
        self.batch_table = validate_sql_identifier(str(config["batch_table"]), "batch table")
        self.job_id = str(config["job_id"])
        self.row_count = int(config["row_count"])
        self.target_rows = int(config["target_rows"])
        self.target_scope_id = str(config["target_scope_id"])
        self.target_policy_id = int(config["target_policy_id"])
        self.policy_table = validate_sql_identifier(str(config["policy_table"]), "policy table")
        self.scope_table = validate_sql_identifier(str(config["scope_table"]), "scope table")
        self.hold_table = validate_sql_identifier(str(config["hold_table"]), "hold table")
        self.release_queue_table = validate_sql_identifier(
            str(config["release_queue_table"]), "release queue table"
        )
        self.schema_audit_table = validate_sql_identifier(
            str(config["schema_audit_table"]), "schema audit table"
        )
        self.capacity_events_table = validate_sql_identifier(
            str(config["capacity_events_table"]), "capacity events table"
        )
        self.initial_archived_rows = int(config["initial_archived_rows"])
        self.initial_checkpoint_rows = int(config["initial_checkpoint_rows"])
        self.initial_checkpoint_span = int(config["initial_checkpoint_span"])
        self.seed_change_neighbor_noise = bool(config["seed_change_neighbor_noise"])
        self.index_columns = tuple(str(value) for value in config["index_columns"])
        self.immutable_truth_sql = str(config["immutable_truth_sql"])
        if self.row_count <= 0 or self.target_rows <= 0:
            raise ValueError(
                "BC03 row counts must be positive: "
                f"row_count={self.row_count}, target_rows={self.target_rows}"
            )
    def _sql(self, env, sql: str, operation: str) -> None:
        require_sql_success(env.execute_sql(sql), operation)

    def _target_membership(self, alias: str = "o") -> str:
        return (
            f"{alias}.retention_class = 'EXPIRED' "
            f"AND EXISTS (SELECT 1 FROM {self.database}.{self.job_table} j "
            f"JOIN {self.database}.{self.policy_table} p "
            f"ON p.policy_id = j.policy_id AND p.scope_id = j.scope_id "
            f"JOIN {self.database}.{self.scope_table} s "
            f"ON s.scope_id = p.scope_id AND s.tenant_id = {alias}.tenant_id "
            "AND s.scope_state = 'APPROVED' "
            f"WHERE j.job_id = '{self.job_id}' AND j.object_name = '{self.orders_table}' "
            f"AND j.policy_id = {self.target_policy_id} AND j.scope_id = '{self.target_scope_id}' "
            f"AND p.object_name = '{self.orders_table}' AND p.state = 'APPROVED') "
            f"AND NOT EXISTS (SELECT 1 FROM {self.database}.{self.hold_table} h "
            f"WHERE h.order_id = {alias}.order_id AND h.hold_state = 'ACTIVE')"
        )

    def _create_schema(self, env) -> None:
        self._sql(env, f"DROP DATABASE IF EXISTS {self.database}", "BC03 clear owned database")
        self._sql(env, f"CREATE DATABASE {self.database}", "BC03 create owned database")
        self._set_lock_wait_timeout(env)
        self._sql(
            env,
            f"CREATE TABLE {self.database}.{self.orders_table} ("
            "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, customer_id BIGINT NOT NULL, "
            "status VARCHAR(16) NOT NULL, amount DECIMAL(12,2) NOT NULL, "
            "retention_class ENUM('ACTIVE', 'EXPIRED') NOT NULL, "
            "archive_state ENUM('LIVE', 'ARCHIVED') NOT NULL, "
            "archive_batch VARCHAR(64) NULL, archived_at DATETIME NULL, touch_version BIGINT NOT NULL, "
            "updated_at DATETIME NOT NULL, payload VARCHAR(384) NOT NULL, "
            "KEY idx_tenant_status (tenant_id, status), "
            "KEY idx_customer_updated (customer_id, updated_at), "
            "KEY idx_status_updated (status, updated_at)"
            ") ENGINE=InnoDB",
            "BC03 create orders table",
        )
        self._sql(
            env,
            f"CREATE TABLE {self.database}.{self.job_table} ("
            "job_id VARCHAR(64) PRIMARY KEY, object_name VARCHAR(64) NOT NULL, "
            "policy_id INT NOT NULL, scope_id VARCHAR(64) NOT NULL, "
            "scope_predicate VARCHAR(255) NOT NULL, "
            "state ENUM('PLANNED', 'RUNNING', 'PAUSED', 'FAILED', 'SUCCEEDED', 'COMPLETED', 'DONE') NOT NULL, "
            "CONSTRAINT chk_bc03_change_jobs_state CHECK (state IN "
            "('PLANNED', 'RUNNING', 'PAUSED', 'FAILED', 'SUCCEEDED', 'COMPLETED', 'DONE')), "
            "last_pk BIGINT NOT NULL, rows_completed BIGINT NOT NULL, target_rows BIGINT NOT NULL, "
            "ddl_index_name VARCHAR(64) NULL, "
            "error_text VARCHAR(255) NOT NULL, updated_at DATETIME NOT NULL"
            ") ENGINE=InnoDB",
            "BC03 create change jobs table",
        )
        self._sql(
            env,
            f"CREATE TABLE {self.database}.{self.batch_table} ("
            "job_id VARCHAR(64) NOT NULL, batch_no INT NOT NULL, "
            "lower_pk BIGINT NOT NULL COMMENT 'previous committed cursor boundary', "
            "upper_pk BIGINT NOT NULL COMMENT 'new committed cursor boundary', "
            "affected_rows INT NOT NULL, observed_p95_ms DECIMAL(10,3) NOT NULL, "
            "recorded_at DATETIME NOT NULL, PRIMARY KEY (job_id, batch_no), "
            "KEY idx_batch_recorded (recorded_at)"
            ") ENGINE=InnoDB",
            "BC03 create batch checkpoint table",
        )
        self._sql(
            env,
            f"CREATE TABLE {self.database}.{self.policy_table} ("
            "policy_id INT PRIMARY KEY, object_name VARCHAR(64) NOT NULL, cutoff_days INT NOT NULL, "
            "state ENUM('APPROVED', 'DRAFT', 'PAUSED', 'REJECTED') NOT NULL, "
            "scope_id VARCHAR(64) NOT NULL"
            ") ENGINE=InnoDB",
            "BC03 create retention policy table",
        )
        self._sql(
            env,
            f"CREATE TABLE {self.database}.{self.scope_table} ("
            "scope_id VARCHAR(64) NOT NULL, tenant_id INT NOT NULL, "
            "scope_state ENUM('APPROVED', 'DEFERRED') NOT NULL, "
            "updated_at DATETIME NOT NULL, PRIMARY KEY (scope_id, tenant_id), "
            "KEY idx_scope_tenant (tenant_id, scope_id)"
            ") ENGINE=InnoDB",
            "BC03 create archive scope table",
        )
        self._sql(
            env,
            f"CREATE TABLE {self.database}.{self.hold_table} ("
            "hold_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, tenant_id INT NOT NULL, "
            "hold_state ENUM('ACTIVE', 'RELEASED') NOT NULL, updated_at DATETIME NOT NULL, "
            "KEY idx_hold_order (order_id, hold_state)"
            ") ENGINE=InnoDB",
            "BC03 create archive hold table",
        )
        self._sql(
            env,
            f"CREATE TABLE {self.database}.{self.release_queue_table} ("
            "release_id BIGINT PRIMARY KEY, service_name VARCHAR(64) NOT NULL, "
            "change_type VARCHAR(32) NOT NULL, state VARCHAR(16) NOT NULL, "
            "risk_level VARCHAR(16) NOT NULL, scheduled_at DATETIME NOT NULL"
            ") ENGINE=InnoDB",
            "BC03 create release queue",
        )
        self._sql(
            env,
            f"CREATE TABLE {self.database}.{self.schema_audit_table} ("
            "audit_id BIGINT PRIMARY KEY, object_name VARCHAR(64) NOT NULL, operation VARCHAR(32) NOT NULL, "
            "state VARCHAR(16) NOT NULL, duration_ms BIGINT NOT NULL, created_at DATETIME NOT NULL"
            ") ENGINE=InnoDB",
            "BC03 create schema audit",
        )
        self._sql(
            env,
            f"CREATE TABLE {self.database}.{self.capacity_events_table} ("
            "event_id BIGINT PRIMARY KEY, store_name VARCHAR(32) NOT NULL, event_type VARCHAR(32) NOT NULL, "
            "pending_bytes BIGINT NOT NULL, write_stall_count INT NOT NULL, created_at DATETIME NOT NULL"
            ") ENGINE=InnoDB",
            "BC03 create capacity events",
        )
        self._sql(
            env,
            f"CREATE TABLE {self.database}.bc03_inventory_touch ("
            "sku INT PRIMARY KEY, touch_count BIGINT NOT NULL, updated_at DATETIME NOT NULL"
            ") ENGINE=InnoDB",
            "BC03 create inventory touch table",
        )
        self._sql(
            env,
            f"CREATE TABLE {self.database}.bc03_numbers (n BIGINT PRIMARY KEY) ENGINE=InnoDB",
            "BC03 create numbers table",
        )

    def _load_fixture(self, env) -> None:
        self._sql(env, f"INSERT INTO {self.database}.bc03_numbers VALUES (1)", "BC03 seed numbers")
        generated = 1
        while generated < self.row_count:
            extension = min(generated, self.row_count - generated)
            self._sql(
                env,
                f"INSERT INTO {self.database}.bc03_numbers "
                f"SELECT n + {generated} FROM {self.database}.bc03_numbers WHERE n <= {extension}",
                f"BC03 extend numbers from {generated} by {extension}",
            )
            generated += extension
        for lower_pk in range(0, self.row_count, FIXTURE_INSERT_CHUNK_ROWS):
            upper_pk = min(lower_pk + FIXTURE_INSERT_CHUNK_ROWS, self.row_count)
            self._sql(
                env,
                f"INSERT INTO {self.database}.{self.orders_table} "
                "(order_id, tenant_id, customer_id, status, amount, retention_class, archive_state, "
                "archive_batch, archived_at, touch_version, updated_at, payload) "
                "SELECT n, MOD(n, 64) + 1, MOD(n, 10000) + 1, "
                "CASE MOD(n, 10) WHEN 0 THEN 'CANCELLED' WHEN 1 THEN 'REVIEW' WHEN 2 THEN 'PAID' "
                "WHEN 3 THEN 'SHIPPED' ELSE 'SETTLED' END, "
                "CAST(MOD(n * 7919, 100000) / 100.0 + 1 AS DECIMAL(12,2)), "
                "CASE WHEN MOD(n, 5) = 0 THEN 'EXPIRED' ELSE 'ACTIVE' END, "
                "'LIVE', NULL, NULL, 0, DATE_SUB('2026-08-05', INTERVAL MOD(n, 120) DAY), "
                "RPAD(CONCAT('bc03-order-', n, '-'), 384, CHAR(97 + MOD(n, 26))) "
                f"FROM {self.database}.bc03_numbers WHERE n > {lower_pk} AND n <= {upper_pk}",
                f"BC03 load order rows in primary-key window ({lower_pk}, {upper_pk}]",
            )
        job_values = [
            f"('{self.job_id}', '{self.orders_table}', {self.target_policy_id}, '{self.target_scope_id}', "
            "\"scope_state = 'APPROVED' AND no ACTIVE hold\", "
            f"'PAUSED', {self.initial_checkpoint_span * 3}, {self.initial_checkpoint_rows}, {self.target_rows}, NULL, '', NOW())"
        ]
        if self.seed_change_neighbor_noise:
            job_values.extend([
                f"('bc03_customer_erasure_042', '{self.orders_table}', 7, 'bc03_customer_erasure_scope', \"tenant_id = 42\", 'PAUSED', {self.row_count // 2}, 3500, 4688, NULL, 'legal hold review', DATE_SUB(NOW(), INTERVAL 3 HOUR))",
                f"('bc03_cancelled_cleanup', '{self.orders_table}', 8, 'bc03_cancelled_cleanup_scope', \"status = 'CANCELLED'\", 'FAILED', {self.row_count // 3}, 18000, 30000, NULL, 'write conflict retry exhausted', DATE_SUB(NOW(), INTERVAL 7 HOUR))",
                f"('bc03_payload_rewrite', '{self.orders_table}', 9, 'bc03_payload_rewrite_scope', \"order_id BETWEEN 80001 AND 130000\", 'RUNNING', {self.row_count // 2}, 25000, 50000, NULL, '', DATE_SUB(NOW(), INTERVAL 12 MINUTE))",
                f"('bc03_legacy_archive_2025q4', '{self.orders_table}', 10, 'bc03_legacy_archive_scope', \"retention_class = 'LEGACY'\", 'SUCCEEDED', {self.row_count}, 0, 0, 'idx_legacy_archive', '', DATE_SUB(NOW(), INTERVAL 120 DAY))",
            ])
        self._sql(
            env,
            f"INSERT INTO {self.database}.{self.job_table} "
            "(job_id, object_name, policy_id, scope_id, scope_predicate, state, last_pk, rows_completed, "
            f"target_rows, ddl_index_name, error_text, updated_at) VALUES {', '.join(job_values)}",
            "BC03 load live and neighboring change jobs",
        )
        if self.seed_change_neighbor_noise:
            self._sql(
                env,
                f"INSERT INTO {self.database}.{self.batch_table} "
                "SELECT 'bc03_payload_rewrite', n, (n - 1) * 2500, n * 2500, 2500, "
                "CAST(45 + MOD(n * 17, 80) AS DECIMAL(10,3)), DATE_SUB(NOW(), INTERVAL n MINUTE) "
                f"FROM {self.database}.bc03_numbers WHERE n <= 10",
                "BC03 load neighboring batch history",
            )
        policy_values = [
            f"({self.target_policy_id}, '{self.orders_table}', 365, 'APPROVED', '{self.target_scope_id}')"
        ]
        if self.seed_change_neighbor_noise:
            policy_values.extend([
                f"({self.target_policy_id + 1}, '{self.orders_table}', 730, 'APPROVED', '{self.target_scope_id}_regulated')",
                "(3, 'bc03_order_events', 180, 'DRAFT', 'bc03_order_events_scope')",
                "(4, 'bc03_payment_attempts', 730, 'PAUSED', 'bc03_payment_attempts_scope')",
                "(5, 'bc03_customer_sessions', 90, 'REJECTED', 'bc03_customer_sessions_scope')",
                "(6, 'bc03_audit_log', 2555, 'APPROVED', 'bc03_audit_log_scope')",
            ])
        self._sql(
            env,
            f"INSERT INTO {self.database}.{self.policy_table} VALUES {', '.join(policy_values)}",
            "BC03 load retention policies",
        )
        scope_select = (
            f"SELECT '{self.target_scope_id}', n, "
            "CASE WHEN n <= 48 THEN 'APPROVED' ELSE 'DEFERRED' END, NOW() "
            f"FROM {self.database}.bc03_numbers WHERE n <= 64"
        )
        if self.seed_change_neighbor_noise:
            scope_select += (
                f" UNION ALL SELECT '{self.target_scope_id}_regulated', n, "
                "CASE WHEN n <= 48 THEN 'DEFERRED' ELSE 'APPROVED' END, NOW() "
                f"FROM {self.database}.bc03_numbers WHERE n <= 64"
            )
        self._sql(
            env,
            f"INSERT INTO {self.database}.{self.scope_table} "
            f"(scope_id, tenant_id, scope_state, updated_at) {scope_select}",
            "BC03 load policy-bound tenant scopes",
        )
        self._sql(
            env,
            f"INSERT INTO {self.database}.{self.hold_table} "
            "(hold_id, order_id, tenant_id, hold_state, updated_at) "
            "SELECT 1000000 + ROW_NUMBER() OVER (ORDER BY order_id), order_id, tenant_id, 'ACTIVE', NOW() "
            f"FROM {self.database}.{self.orders_table} o "
            f"WHERE {self._target_membership()} AND o.order_id <> 158805 "
            "ORDER BY order_id DESC LIMIT 225",
            "BC03 load active archive holds",
        )
        self._sql(
            env,
            f"INSERT INTO {self.database}.{self.hold_table} "
            "(hold_id, order_id, tenant_id, hold_state, updated_at) "
            "SELECT 2000000 + ROW_NUMBER() OVER (ORDER BY o.order_id), o.order_id, o.tenant_id, 'RELEASED', NOW() "
            f"FROM {self.database}.{self.orders_table} o "
            f"WHERE {self._target_membership()} AND o.order_id <> 158805 "
            f"AND NOT EXISTS (SELECT 1 FROM {self.database}.{self.hold_table} h "
            "WHERE h.order_id = o.order_id) "
            "ORDER BY o.order_id DESC LIMIT 134",
            "BC03 load released archive holds",
        )
        self._sql(
            env,
            f"UPDATE {self.database}.{self.orders_table} "
            "AS o SET archive_state = 'ARCHIVED', archive_batch = "
            f"'{self.job_id}', archived_at = NOW(), touch_version = touch_version + 1, updated_at = NOW() "
            f"WHERE {self._target_membership()} AND o.archive_state = 'LIVE' "
            f"ORDER BY o.order_id LIMIT {self.initial_archived_rows}",
            "BC03 materialize committed and interrupted archive batches",
        )
        first_checkpoint_upper = self.initial_checkpoint_span
        second_checkpoint_upper = self.initial_checkpoint_span * 2
        third_checkpoint_upper = self.initial_checkpoint_span * 3
        checkpoint_part_1 = self.initial_checkpoint_rows // 3
        checkpoint_part_2 = self.initial_checkpoint_rows // 3
        checkpoint_part_3 = self.initial_checkpoint_rows - checkpoint_part_1 - checkpoint_part_2
        self._sql(
            env,
            f"INSERT INTO {self.database}.{self.batch_table} "
            f"(job_id, batch_no, lower_pk, upper_pk, affected_rows, observed_p95_ms, recorded_at) VALUES "
            f"('{self.job_id}', 1, 0, {first_checkpoint_upper}, {checkpoint_part_1}, 120.000, NOW()), "
            f"('{self.job_id}', 2, {first_checkpoint_upper}, {second_checkpoint_upper}, {checkpoint_part_2}, 120.000, NOW()), "
            f"('{self.job_id}', 3, {second_checkpoint_upper}, {third_checkpoint_upper}, {checkpoint_part_3}, 120.000, NOW())",
            "BC03 load committed checkpoint prefix",
        )
        if self.seed_change_neighbor_noise:
            self._sql(
                env,
                f"INSERT INTO {self.database}.{self.release_queue_table} "
                "SELECT n, CONCAT('service-', MOD(n, 17)), "
                "CASE MOD(n, 4) WHEN 0 THEN 'ADD_INDEX' WHEN 1 THEN 'BACKFILL' WHEN 2 THEN 'COLUMN_CHANGE' ELSE 'CONFIG' END, "
                "CASE MOD(n, 5) WHEN 0 THEN 'FAILED' WHEN 1 THEN 'RUNNING' WHEN 2 THEN 'PAUSED' ELSE 'SUCCEEDED' END, "
                "CASE MOD(n, 3) WHEN 0 THEN 'HIGH' WHEN 1 THEN 'MEDIUM' ELSE 'LOW' END, "
                "DATE_SUB(NOW(), INTERVAL n MINUTE) "
                f"FROM {self.database}.bc03_numbers WHERE n <= 80",
                "BC03 load release queue",
            )
            self._sql(
                env,
                f"INSERT INTO {self.database}.{self.schema_audit_table} "
                "SELECT n, CONCAT('table_', MOD(n, 23)), "
                "CASE MOD(n, 4) WHEN 0 THEN 'ADD INDEX' WHEN 1 THEN 'MODIFY COLUMN' WHEN 2 THEN 'DROP INDEX' ELSE 'ADD COLUMN' END, "
                "CASE MOD(n, 5) WHEN 0 THEN 'FAILED' WHEN 1 THEN 'QUEUEING' ELSE 'SYNCED' END, "
                "MOD(n * 1297, 900000), DATE_SUB(NOW(), INTERVAL n * 2 MINUTE) "
                f"FROM {self.database}.bc03_numbers WHERE n <= 100",
                "BC03 load schema audit",
            )
            self._sql(
                env,
                f"INSERT INTO {self.database}.{self.capacity_events_table} "
                "SELECT n, CONCAT('tikv-', MOD(n, 3)), "
                "CASE MOD(n, 4) WHEN 0 THEN 'COMPACTION' WHEN 1 THEN 'GC' WHEN 2 THEN 'FLUSH' ELSE 'SNAPSHOT' END, "
                "MOD(n * 1073741824, 68719476736), MOD(n, 7), DATE_SUB(NOW(), INTERVAL n * 3 MINUTE) "
                f"FROM {self.database}.bc03_numbers WHERE n <= 60",
                "BC03 load capacity events",
            )
        self._sql(
            env,
            f"ANALYZE TABLE {self.database}.{self.orders_table}",
            "BC03 analyze orders table",
        )

    def _verify_initial_state(self, env) -> None:
        state = self._initial_state(env)
        expected = {
            "total_rows": self.row_count,
            "target_live_rows": self.target_rows - self.initial_archived_rows,
            "target_archived_rows": self.initial_archived_rows,
            "job_state": "PAUSED",
            "last_pk": self.initial_checkpoint_span * 3,
            "rows_completed": self.initial_checkpoint_rows,
            "required_index_count": 0,
        }
        if state != expected:
            raise RuntimeError(f"BC03 initial state mismatch: expected={expected!r}, actual={state!r}")

    def _initial_state(self, env) -> dict[str, object]:
        counts = require_result_rows(
            env.execute_sql(
                f"SELECT COUNT(*), "
                f"SUM({self._target_membership()} AND o.archive_state = 'LIVE'), "
                f"SUM({self._target_membership()} AND o.archive_state = 'ARCHIVED' "
                f"AND archive_batch = '{self.job_id}') "
                f"FROM {self.database}.{self.orders_table} o"
            ),
            "BC03 read initial order state",
        )
        if len(counts) != 1:
            raise RuntimeError(f"BC03 order state query returned unexpected rows: rows={counts!r}")
        job = require_result_rows(
            env.execute_sql(
                f"SELECT state, last_pk, rows_completed FROM {self.database}.{self.job_table} "
                f"WHERE job_id = '{self.job_id}'"
            ),
            "BC03 read target change job",
        )
        if len(job) != 1:
            raise RuntimeError(f"BC03 target job query returned unexpected rows: rows={job!r}")
        index_count = sum(
            1
            for row in self._index_rows(env)
            if tuple(str(value).casefold() for value in row[2])[: len(self.index_columns)]
            == tuple(value.casefold() for value in self.index_columns)
        )
        return {
            "total_rows": int(counts[0][0]),
            "target_live_rows": int(counts[0][1]),
            "target_archived_rows": int(counts[0][2]),
            "job_state": str(job[0][0]),
            "last_pk": int(job[0][1]),
            "rows_completed": int(job[0][2]),
            "required_index_count": index_count,
        }

    def _immutable_truth(self, env) -> tuple[int, int, int]:
        rows = require_result_rows(
            env.execute_sql(self.immutable_truth_sql),
            "BC03 capture immutable business truth",
        )
        if len(rows) != 1 or len(rows[0]) != 3:
            raise RuntimeError(
                f"BC03 immutable truth query returned an unexpected shape: rows={rows!r}"
            )
        return tuple(int(value) for value in rows[0])

    def _target_distribution(self, env) -> tuple[tuple[object, ...], ...]:
        rows = require_result_rows(
            env.execute_sql(
                f"SELECT MIN(o.order_id), MAX(o.order_id), COUNT(*) "
                f"FROM {self.database}.{self.orders_table} o WHERE {self._target_membership()}"
            ),
            "BC03 capture target primary-key distribution",
        )
        return tuple(tuple(row) for row in rows)

    def _checkpoint_rows(self, env) -> tuple[tuple[object, ...], ...]:
        rows = require_result_rows(
            env.execute_sql(
                f"SELECT batch_no, lower_pk, upper_pk, affected_rows, observed_p95_ms "
                f"FROM {self.database}.{self.batch_table} WHERE job_id = '{self.job_id}' ORDER BY batch_no"
            ),
            "BC03 capture committed checkpoint prefix",
        )
        return tuple(tuple(row) for row in rows)

    def _index_rows(self, env) -> tuple[tuple[str, bool, tuple[str, ...]], ...]:
        rows = require_result_rows(
            env.execute_sql(f"SHOW INDEX FROM {self.database}.{self.orders_table}"),
            "BC03 inspect orders indexes",
        )
        indexes: dict[str, dict[str, object]] = {}
        for row in rows:
            name = str(row[2])
            indexes.setdefault(name, {"non_unique": bool(int(row[1])), "columns": []})
            indexes[name]["columns"].append((int(row[3]), str(row[4])))
        return tuple(
            (
                name,
                bool(values["non_unique"]),
                tuple(column for _, column in sorted(values["columns"])),
            )
            for name, values in sorted(indexes.items())
        )

    def _neighbor_counts(self, env) -> dict[str, int]:
        tables = (
            self.job_table,
            self.batch_table,
            self.policy_table,
            self.release_queue_table,
            self.schema_audit_table,
            self.capacity_events_table,
        )
        counts = {}
        for table in tables:
            rows = require_result_rows(
                env.execute_sql(f"SELECT COUNT(*) FROM {self.database}.{table}"),
                f"BC03 count neighbor table {table}",
            )
            counts[table] = int(rows[0][0])
        return counts

    def _start_settlement_interference(self, env) -> None:
        if self._runtime_thread is not None:
            raise RuntimeError("BC03 settlement interference was started twice")
        self._runtime_stop = threading.Event()
        self._runtime_ready = threading.Event()
        self._runtime_error = None
        self._runtime_thread = threading.Thread(
            target=self._settlement_loop,
            args=(env,),
            name="bc03-settlement-interference",
            daemon=True,
        )
        self._runtime_thread.start()
        if not self._runtime_ready.wait(10):
            try:
                self._stop_settlement_interference()
            except RuntimeError as error:
                raise RuntimeError(
                    "BC03 settlement interference failed before readiness: "
                    f"database={self.database!r}, job_id={self.job_id!r}, error={error}"
                ) from error
            raise RuntimeError(
                "BC03 settlement interference did not acquire its business row lock: "
                f"database={self.database!r}, job_id={self.job_id!r}"
            )
        if self._runtime_error is not None:
            error = self._runtime_error
            self._stop_settlement_interference()
            raise RuntimeError(f"BC03 settlement interference failed before readiness: {error}") from error

    def _stop_settlement_interference(self) -> None:
        if self._runtime_thread is None:
            return
        if self._runtime_stop is None:
            raise RuntimeError("BC03 settlement interference stop event is missing")
        self._runtime_stop.set()
        join_thread(self._runtime_thread, 8, "BC03 settlement interference")
        self._runtime_thread = None
        self._runtime_stop = None
        self._runtime_ready = None
        if self._runtime_error is not None:
            error = self._runtime_error
            self._runtime_error = None
            raise RuntimeError(f"BC03 settlement interference failed: {error}") from error

    def _settlement_loop(self, env) -> None:
        holder = None
        observer = None
        lock_order_id = None
        try:
            holder = connect_tidb(
                env,
                database=self.database,
                autocommit=False,
                application_name="settlement-service",
                read_timeout=10,
                write_timeout=10,
            )
            with holder.cursor() as cur:
                cur.execute("SELECT CONNECTION_ID()")
                holder_session_id = int(cur.fetchone()[0])
                cur.execute("SET SESSION innodb_lock_wait_timeout = 2")
                cur.execute("BEGIN PESSIMISTIC")
                cur.execute(
                    f"SELECT MIN(o.order_id) FROM {self.database}.{self.orders_table} o "
                    f"WHERE {self._target_membership()} AND o.archive_state = 'LIVE' "
                    "AND o.status = 'CANCELLED'"
                )
                row = cur.fetchone()
                if row is None or row[0] is None:
                    raise RuntimeError(
                        "BC03 settlement holder could not find a live approved CANCELLED target: "
                        f"database={self.database!r}, job_id={self.job_id!r}, target_status='CANCELLED'"
                    )
                lock_order_id = int(row[0])
                cur.execute(
                    f"UPDATE /* settlement-service */ {self.database}.{self.orders_table} "
                    "SET touch_version = touch_version + 1, updated_at = NOW() "
                    f"WHERE order_id = {lock_order_id} AND status = 'CANCELLED' "
                    "AND retention_class = 'EXPIRED' "
                    "AND archive_state = 'LIVE'"
                )
                if cur.rowcount != 1:
                    raise RuntimeError(
                        "BC03 settlement holder update did not lock exactly one target row: "
                        f"database={self.database!r}, job_id={self.job_id!r}, "
                        f"order_id={lock_order_id}, affected_rows={cur.rowcount}"
                    )

            observer = connect_tidb(
                env,
                database=self.database,
                autocommit=False,
                application_name="settlement-observer",
                read_timeout=10,
                write_timeout=10,
            )
            with observer.cursor() as cur:
                cur.execute("SET SESSION tidb_txn_mode = 'pessimistic'")
                cur.execute("SET SESSION innodb_lock_wait_timeout = 1")
            probe_attempts = 0
            while True:
                probe_attempts += 1
                try:
                    with observer.cursor() as cur:
                        cur.execute("BEGIN PESSIMISTIC")
                        cur.execute(
                            f"SELECT order_id FROM {self.database}.{self.orders_table} "
                            f"WHERE order_id = {lock_order_id} FOR UPDATE NOWAIT"
                        )
                        cur.fetchall()
                except pymysql.err.OperationalError as error:
                    code = int(error.args[0]) if error.args and str(error.args[0]).isdigit() else None
                    observer.rollback()
                    if code in {1205, 3572} or "lock" in str(error).casefold():
                        break
                    raise RuntimeError(
                        "BC03 settlement lock probe returned an unexpected error: "
                        f"database={self.database!r}, job_id={self.job_id!r}, "
                        f"order_id={lock_order_id}, attempt={probe_attempts}, error={error}"
                    ) from error
                observer.rollback()
                if self._runtime_stop is not None and self._runtime_stop.wait(SETTLEMENT_OBSERVE_SECONDS):
                    return
            if self._runtime_ready is not None:
                self._runtime_ready.set()
            while self._runtime_stop is not None and not self._runtime_stop.is_set():
                with observer.cursor() as cur:
                    cur.execute(
                        "SELECT KEY_INFO FROM INFORMATION_SCHEMA.DATA_LOCK_WAITS"
                    )
                    target_lock_wait_seen = any(
                        (
                            lock_info := json.loads(row[0])
                        )["db_name"] == self.database
                        and lock_info["table_name"] == self.orders_table
                        and str(lock_info.get("handle_value")) == str(lock_order_id)
                        for row in cur.fetchall()
                    )
                if target_lock_wait_seen:
                    self._runtime_stop.wait(SETTLEMENT_RELEASE_GRACE_SECONDS)
                    try:
                        holder.commit()
                    except pymysql.err.OperationalError as error:
                        if not self._holder_was_terminated(observer, holder_session_id, error):
                            raise
                    return
                self._runtime_stop.wait(SETTLEMENT_OBSERVE_SECONDS)
        except Exception as exc:
            self._runtime_error = exc
            if holder is not None:
                holder.rollback()
        finally:
            if observer is not None:
                observer.close()
            if holder is not None:
                holder.close()

    @staticmethod
    def _holder_was_terminated(observer, holder_session_id: int, error: Exception) -> bool:
        if not isinstance(error, pymysql.err.OperationalError):
            return False
        if len(error.args) < 2 or int(error.args[0]) != 2013:
            return False
        if "lost connection to mysql server" not in str(error.args[1]).casefold():
            return False
        with observer.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM information_schema.cluster_tidb_trx "
                "WHERE SESSION_ID = %s",
                (holder_session_id,),
            )
            row = cur.fetchone()
        if row is None or len(row) != 1:
            raise RuntimeError(
                "BC03 holder termination check returned an unexpected row: "
                f"session_id={holder_session_id}, row={row!r}"
            )
        return int(row[0]) == 0

    def _set_lock_wait_timeout(self, env) -> None:
        if (
            self._previous_lock_wait_timeout is None
            or self._previous_session_lock_wait_timeout is None
        ):
            rows = require_result_rows(
                env.execute_sql("SELECT @@GLOBAL.innodb_lock_wait_timeout"),
                "BC03 read global lock wait timeout",
            )
            if len(rows) != 1 or len(rows[0]) != 1:
                raise RuntimeError(
                    "BC03 global lock wait timeout query returned an unexpected shape: "
                    f"rows={rows!r}"
                )
            self._previous_lock_wait_timeout = int(rows[0][0])
            rows = require_result_rows(
                env.execute_sql("SELECT @@SESSION.innodb_lock_wait_timeout"),
                "BC03 read session lock wait timeout",
            )
            if len(rows) != 1 or len(rows[0]) != 1:
                raise RuntimeError(
                    "BC03 session lock wait timeout query returned an unexpected shape: "
                    f"rows={rows!r}"
                )
            self._previous_session_lock_wait_timeout = int(rows[0][0])
            rows = require_result_rows(
                env.execute_sql("SELECT @@SESSION.tidb_txn_mode"),
                "BC03 read session transaction mode",
            )
            if len(rows) != 1 or len(rows[0]) != 1:
                raise RuntimeError(
                    "BC03 session transaction mode query returned an unexpected shape: "
                    f"rows={rows!r}"
                )
            self._previous_session_txn_mode = str(rows[0][0])
        self._sql(env, "SET GLOBAL innodb_lock_wait_timeout = 1", "BC03 set business global lock wait timeout")
        self._sql(env, "SET SESSION innodb_lock_wait_timeout = 1", "BC03 set business session lock wait timeout")
        self._sql(env, "SET SESSION tidb_txn_mode = 'pessimistic'", "BC03 set business transaction mode")

    def _restore_lock_wait_timeout(self, env) -> None:
        if (
            self._previous_lock_wait_timeout is None
            or self._previous_session_lock_wait_timeout is None
            or self._previous_session_txn_mode is None
        ):
            return
        previous_global = self._previous_lock_wait_timeout
        previous_session = self._previous_session_lock_wait_timeout
        previous_session_txn_mode = self._previous_session_txn_mode
        self._sql(
            env,
            f"SET SESSION innodb_lock_wait_timeout = {previous_session}",
            "BC03 restore session lock wait timeout",
        )
        self._sql(
            env,
            f"SET GLOBAL innodb_lock_wait_timeout = {previous_global}",
            "BC03 restore global lock wait timeout",
        )
        self._sql(
            env,
            f"SET SESSION tidb_txn_mode = '{previous_session_txn_mode}'",
            "BC03 restore session transaction mode",
        )
        self._previous_lock_wait_timeout = None
        self._previous_session_lock_wait_timeout = None
        self._previous_session_txn_mode = None
