from .rolling_upgrade import (
    TidbBusinessChangeRollingUpgradeForRollingUpgrade6_5To7_5ScenarioCase,
    TidbBusinessChangeRollingUpgradeForRollingUpgrade7_5To8_1ScenarioCase,
    TidbBusinessChangeRollingUpgradeScenario,
)
from .large_table_batch_dml import (
    TidbBusinessChangeLargeTableBatchDmlCase,
    TidbBusinessChangeLargeTableBatchDmlForLargeTableBatchUpdateAndIndexScenarioCase,
    TidbBusinessChangeLargeTableBatchDmlScenario,
)
from .lightning_checkpoint import (
    TidbBusinessChangeLightningCheckpointCase,
    TidbBusinessChangeLightningCheckpointForLightningCheckpointScaleOutScenarioCase,
    TidbBusinessChangeLightningCheckpointScenario,
)
from .dm_replace import (
    TidbBusinessChangeDmReplaceCase,
    TidbBusinessChangeDmReplaceForFailedDdlSafeReplaceBillingScenarioCase,
    TidbBusinessChangeDmReplaceForFailedDdlSafeReplaceScenarioCase,
    TidbBusinessChangeDmReplaceScenario,
)
from .table_recovery import (
    TidbBusinessChangeTableRecoveryCase,
    TidbBusinessChangeTableRecoveryForDroppedTableGcRecoveryScenarioCase,
    TidbBusinessChangeTableRecoveryForDroppedPaymentEventsGcRecoveryScenarioCase,
    TidbBusinessChangeTableRecoveryScenario,
)
from .x86_arm64_migration import (
    TidbBusinessChangeX86Arm64MigrationForOfflineOnlineMigrationScenarioCase,
    TidbBusinessChangeX86Arm64MigrationScenario,
)
from .online_ddl_pause_resume import (
    BusinessDecoySpec,
    TidbBusinessChangeOnlineDdlPauseResumeCase,
    TidbBusinessChangeOnlineDdlPauseResumeForPausedIndexBackfillScenarioCase,
    TidbBusinessChangeOnlineDdlPauseResumeScenario,
)
from .batched_dml_ddl import (
    BC03_SETTLEMENT_CASE,
    TidbBusinessChangeBc03Case,
    TidbBusinessChangeBc03ForRetentionArchiveScenarioCase,
    TidbBusinessChangeBatchedDmlDdlScenario,
)
from .dr_auto_sync_failover import (
    TidbBusinessChangeDrAutoSyncFailoverCase,
    TidbBusinessChangeDrAutoSyncFailoverScenario,
    TidbBusinessChangeDrAutoSyncForPlannedFailoverScenarioCase,
    TidbBusinessChangeDrAutoSyncPlannedInjector,
    TidbBusinessChangeDrAutoSyncForUnplannedFailoverScenarioCase,
    TidbBusinessChangeDrAutoSyncUnplannedInjector,
)
from .pitr_checkpoint_recovery import (
    TidbBusinessChangePitrCheckpointRecoveryForResumeFailedPitrWithoutBreakingChainScenarioCase,
    TidbBusinessChangePitrCheckpointRecoveryInjector,
    TidbBusinessChangePitrCheckpointRecoveryScenario,
)
from .timezone_ddl_backpressure import (
    TidbBusinessChangeTimezoneDdlBackpressureForDrCutoverTimezoneDdlAndSinkBackpressureScenarioCase,
    TidbBusinessChangeTimezoneDdlBackpressureInjector,
    TidbBusinessChangeTimezoneDdlBackpressureScenario,
)
from .timezone_ddl_backpressure_frozen_history import (
    TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryForHistoryInvestigationScenarioCase,
    TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryInjector,
    TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryScenario,
)

from dataclasses import dataclass

from src.protocols.report import structured_reference_report
from src.scenarios.evaluation.tidb.business_change.cdc_dc_migration import (
    TidbBusinessChangeCdcDcMigrationForReverseCutoverEvaluatorCase,
    TidbBusinessChangeCdcDcMigrationForReverseDirectionEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


def _business_workload(
    *,
    source_dc: str = "east",
    target_dc: str = "west",
    source_db: str = "east_dc",
    target_db: str = "west_dc",
    archive_db: str = "archive_dc",
    control_db: str = "ops_control",
    order_table: str = "checkout_orders",
    intent_table: str = "order_intents",
    route_table: str = "traffic_routes",
    changefeed_table: str = "changefeed_status",
    migration_table: str = "migration_control",
    route_service: str = "checkout-api",
) -> BackgroundWorkloadSpec:
    return BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="checkout_api_order_intent_writer",
                sql=(
                    f"INSERT INTO {control_db}.{intent_table} "
                    "(intent_id, customer_id, amount_cents, request_source) VALUES "
                    f"(UUID(), FLOOR(1 + RAND() * 9000), FLOOR(100 + RAND() * 9900), '{route_service}')"
                ),
                qps=1.4,
                tier="BUSINESS_WRITE",
                commit=True,
                application_name=route_service,
            ),
            WorkloadProfile(
                name="checkout_route_summary",
                sql=(
                    "SELECT r.active_dc, COUNT(o.order_id), COALESCE(SUM(o.amount_cents), 0) "
                    f"FROM {control_db}.{route_table} r "
                    f"LEFT JOIN {source_db}.{order_table} o ON r.active_dc = '{source_dc}' "
                    f"WHERE r.service_name = '{route_service}' GROUP BY r.active_dc "
                    "UNION ALL "
                    f"SELECT r.active_dc, COUNT(o.order_id), COALESCE(SUM(o.amount_cents), 0) "
                    f"FROM {control_db}.{route_table} r "
                    f"LEFT JOIN {target_db}.{order_table} o ON r.active_dc = '{target_dc}' "
                    f"WHERE r.service_name = '{route_service}' GROUP BY r.active_dc"
                ),
                qps=0.8,
                tier="BUSINESS_READ",
                application_name=route_service,
            ),
            WorkloadProfile(
                name="customer_order_status_probe",
                sql=(
                    "SELECT order_id, status, amount_cents, updated_at "
                    f"FROM {source_db}.{order_table} WHERE order_id BETWEEN 1 AND 40 "
                    "ORDER BY order_id DESC LIMIT 20"
                ),
                qps=0.7,
                tier="BUSINESS_READ",
                application_name="customer-profile-api",
            ),
            WorkloadProfile(
                name="replication_control_dashboard",
                sql=(
                    "SELECT feed_id, direction, state, enabled, lag_events, last_error "
                    f"FROM {control_db}.{changefeed_table} ORDER BY feed_id"
                ),
                qps=0.9,
                tier="CONTROL_READ",
                application_name="replication-dashboard",
            ),
            WorkloadProfile(
                name="migration_observation_dashboard",
                sql=(
                    "SELECT observed_at, route_dc, forward_lag_events, reverse_lag_events, "
                    "p95_latency_ms, target_app_events, reverse_applied_events "
                    f"FROM {control_db}.replication_observations "
                    "ORDER BY observed_at DESC LIMIT 8"
                ),
                qps=0.8,
                tier="CONTROL_READ",
                application_name="migration-dashboard",
            ),
            WorkloadProfile(
                name="archive_dc_reconciliation_decoy",
                sql=(
                    "SELECT COUNT(*), COALESCE(SUM(amount_cents), 0) "
                    f"FROM {archive_db}.{order_table} "
                    "WHERE updated_at >= CURRENT_TIMESTAMP - INTERVAL 1 DAY"
                ),
                qps=0.7,
                tier="DECOY_READ",
                application_name="warehouse-reconciliation",
            ),
            WorkloadProfile(
                name="schema_and_route_inventory_decoy",
                sql=(
                    "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS "
                    "FROM INFORMATION_SCHEMA.TABLES "
                    f"WHERE TABLE_SCHEMA IN ('{source_db}', '{target_db}', '{archive_db}') "
                    "ORDER BY TABLE_SCHEMA, TABLE_NAME"
                ),
                qps=0.55,
                tier="CONTROL_READ",
                application_name="schema-inventory",
            ),
            WorkloadProfile(
                name="business_slo_probe",
                sql=(
                    "SELECT route_dc, p95_latency_ms, error_rate, observed_at "
                    f"FROM {control_db}.service_slo_samples "
                    "ORDER BY observed_at DESC LIMIT 5"
                ),
                qps=0.65,
                tier="SLO_READ",
                application_name="slo-monitor",
            ),
        ),
        worker_count=5,
        seed=0xBC02,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=2.0,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeCdcDcMigrationForReverseCutoverScenarioCase(TiDBScenarioCase):
    source_dc: str
    target_dc: str
    source_db: str
    target_db: str
    archive_db: str
    control_db: str
    order_table: str
    event_table: str
    intent_table: str
    route_table: str
    changefeed_table: str
    migration_table: str
    validation_table: str
    route_service: str
    migration_id: str
    forward_feed_id: str
    reverse_feed_id: str
    snapshot_rows: int
    source_rows: int
    slo_p95_ms: float
    poll_interval_seconds: float
    final_state_attempts: int
    final_state_interval_seconds: float
    initial_cutover_done: bool
    initial_route_epoch: int
    checkpoint_gap_rows: int
    reverse_region_filter: str
    source_incarnation: str
    target_incarnation: str
    retired_target_incarnation: str
    previous_target_incarnation: str
    candidate_target_incarnation: str
    reverse_event_namespace: str
    collision_history_rows: int
    producer_clock_reset_rows: int
    reference_path: tuple[str, ...]
    reference_tool_counts: tuple[tuple[str, int, int], ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeCdcDcMigrationForReverseDirectionScenarioCase(
    TidbBusinessChangeCdcDcMigrationForReverseCutoverScenarioCase
):
    pass


_TIDB_BUSINESS_CHANGE_CDC_DC_MIGRATION_CASE = TidbBusinessChangeCdcDcMigrationForReverseCutoverScenarioCase(
    case_id="cdc_dc_migration_reverse_cutover",
    reference_report=structured_reference_report(
        case_id="cdc_dc_migration_reverse_cutover",
        factors=(),
        changes=(
            "forward east-to-west changefeed caught up before the planned checkout-api cutover",
            "the imported reverse checkpoint skipped journal-covered west orders",
            "the live reverse regional selector was reconciled with the missing journal cohort before replay",
            "rollback readiness claimed by the control plane was audited against rollback-target completeness",
            "the live reverse cursor was rewound and immutable events replayed idempotently",
            "cross-incarnation delivery identity and public handoff authority were reconciled before applying producer-clock-reset updates",
        ),
        verification=(
            "both business copies have identical order identities and business values",
            "the complete west serving copy and complete east rollback copy preserve all committed orders",
            "forward and reverse links stay healthy and foreground p95 stays within the migration SLO",
        ),
        summary="The reference audited watermarks against business truth, repaired skipped event delivery, and closed with complete serving and rollback copies.",
    ),
    case_no=0,
    evaluator=TidbBusinessChangeCdcDcMigrationForReverseCutoverEvaluatorCase,
    title=(
        "Online TiCDC-style east-to-west migration with forward catch-up, a reverse "
        "changefeed, and a rollback-ready traffic cutover."
    ),
    alert=(
        "业务变更任务：checkout-api 的在线机房迁移收口尚未完成。按迁移计划，流量此时应已切到 west 并保持可安全回退，"
        "但当前迁移状态不满足收口条件，具体缺什么需要你结合环境证据自行排查。请在迁移期间保证业务数据不丢失、"
        "east 与 west 业务真值一致，收口完成后必须可安全回退。允许对本次迁移的活跃复制链路和 checkout-api 路由执行必要的定向控制面更新；"
        "两地业务副本完整一致后可保持 west 收口或安全回退 east。不得修改业务真值或事件日志，不得停掉集群、删除数据、"
        "跳过一致性校验，或用强制方式掩盖复制延迟。"
    ),
    initial_state={
        "active_dc": "west",
        "forward_changefeed": "normal_with_lag",
        "reverse_changefeed": "normal_with_lag",
        "migration_phase": "observation",
    },
    expected_target={
        "active_dc": "west_forward_closure_or_east_complete_rollback_closure",
        "forward_changefeed": "normal_lag_zero",
        "reverse_changefeed": "normal_lag_zero",
        "migration_phase": "rollback_ready_or_safely_aborted",
        "business_truth": "equal_complete_business_copies_with_no_row_loss",
        "target_lineage": "source_increment_rows_preserve_replicated_east_provenance",
    },
    background_workload=_business_workload(),
    difficulty=DifficultyCalibration(
        diagnostic_depth=12,
        environmental_complexity=369 / 504,
        reference_run_ids=("7bf02468-e882-4ecb-8290-3d2d410a16e6",),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=180,
        image_group_key="bc02-cdc-migration",
    ),
    source_dc="east",
    target_dc="west",
    source_db="east_dc",
    target_db="west_dc",
    archive_db="archive_dc",
    control_db="ops_control",
    order_table="checkout_orders",
    event_table="cdc_events",
    intent_table="order_intents",
    route_table="traffic_routes",
    changefeed_table="changefeed_status",
    migration_table="migration_control",
    validation_table="validation_requests",
    route_service="checkout-api",
    migration_id="checkout-east-west-20260801",
    forward_feed_id="checkout-east-west-forward",
    reverse_feed_id="checkout-west-east-reverse",
    snapshot_rows=1800,
    source_rows=2400,
    slo_p95_ms=12_000.0,
    poll_interval_seconds=0.25,
    final_state_attempts=40,
    final_state_interval_seconds=0.5,
    initial_cutover_done=True,
    initial_route_epoch=2,
    checkpoint_gap_rows=30,
    reverse_region_filter="west",
    source_incarnation="journal-2c4",
    target_incarnation="journal-6f2",
    retired_target_incarnation="journal-a91",
    previous_target_incarnation="journal-b37",
    candidate_target_incarnation="journal-c88",
    reverse_event_namespace="journal-a91",
    collision_history_rows=30,
    producer_clock_reset_rows=12,
    reference_path=(
        'West serves checkout with unestablished rollback completeness',
        'Bind route and live migration lineage excluding rehearsal',
        'Healthy links and resolved cursor do not establish actual business completeness',
        'Journal retains necessary west-origin orders before reverse cursor',
        'Checkpoint import interpreted applied-count as physical position',
        'Business region selector differs from event origin and discards valid records',
        'Native destination ACK conflicts with current local IDs from older incarnation',
        'Public registry binds immutable producer incarnation to replay identity',
        'Necessary retired and current producer incarnations coexist in journal with overlapping local IDs',
        'Current producer clock moved behind preexisting snapshot business timestamp',
        'Public connector orders selected envelopes using registry epoch then local revision',
        'Highest proposed epoch represents aborted validation projections rather than committed business authority; effective receipts and unchanged source business identify activated history and current writer',
        'Checkpoint-position and region loss, local-ID identity aliasing, incarnation-local clocks and unauthorized validation consumption jointly explain missing or stale business despite healthy links/cursors',
    ),
    reference_tool_counts=(
        ('raw_sealed_journal_page', 66, 304),
        ('raw_routes', 1, 0),
        ('raw_changefeeds', 2, 2),
        ('raw_migrations', 1, 1),
        ('raw_checkpoint_imports', 1, 0),
        ('raw_incarnation_registry', 5, 0),
        ('raw_handoff_decisions', 3, 0),
        ('business_truth_aggregates', 2, 0),
        ('actual_stale_existing_business', 24, 0),
        ('destination_west_envelope_window', 30, 62),
    ),
)


_TIDB_BUSINESS_CHANGE_CDC_DC_MIGRATION_REVERSE_CASE = (
    TidbBusinessChangeCdcDcMigrationForReverseDirectionScenarioCase(
        case_id="cdc_dc_migration_reverse_direction",
        reference_report=structured_reference_report(
            case_id="cdc_dc_migration_reverse_direction",
            factors=(
                "the migration starts from west and the live billing route must move to east",
                "a smaller archive cohort remains a same-domain decoy while forward and reverse lineage are reconciled",
            ),
            changes=(
                "caught up the west-to-east feed before activating the east-to-west rollback link",
                "cut the billing-api route to east only after both directions were ready",
            ),
            verification=(
                "west and east billing order truth, checksums, and counts are equal",
                "post-cutover east writes were observed on west through the reverse link",
                "foreground p95 remained under the published migration SLO",
            ),
            summary="The reverse-direction migration completed with lineage and rollback readiness verified.",
        ),
        case_no=1,
        evaluator=TidbBusinessChangeCdcDcMigrationForReverseDirectionEvaluatorCase,
        title="Online TiCDC-style west-to-east migration with rollback-ready billing cutover.",
        alert=(
            "业务变更任务：billing-api 需要在不停写的前提下从 west 机房迁移到 east 机房。"
            "请先完成全量基线和 west->east 增量追平，再建立 east->west 反向复制；只有两条链路都追平且业务真值一致时，"
            "才可以把 billing-api 流量切到 east，并保留观察期回切能力。环境中保留少量 archive 同域噪声、历史迁移和路由控制记录。"
            "不得停集群、删数据、跳过一致性校验或用强制方式掩盖复制延迟。"
        ),
        initial_state={
            "active_dc": "west",
            "forward_changefeed": "normal_with_lag",
            "reverse_changefeed": "paused_not_seeded",
            "migration_phase": "catchup",
        },
        expected_target={
            "active_dc": "east",
            "forward_changefeed": "normal_lag_zero",
            "reverse_changefeed": "normal_lag_zero",
            "migration_phase": "rollback_ready",
            "business_truth": "west_and_east_equal",
            "target_lineage": "source_increment_rows_preserve_replicated_west_provenance",
        },
        background_workload=_business_workload(
            source_dc="west",
            target_dc="east",
            source_db="bc02_west",
            target_db="bc02_east",
            archive_db="bc02_archive",
            control_db="bc02_billing_control",
            order_table="billing_orders",
            intent_table="billing_intents",
            route_table="billing_routes",
            changefeed_table="billing_changefeeds",
            migration_table="billing_migrations",
            route_service="billing-api",
        ),
        difficulty=DifficultyCalibration(
            diagnostic_depth=2,
            environmental_complexity=0.822178,
            reference_run_ids=(
                "reference-231__"
                "tidb_business_change_cdc_dc_migration__cdc_dc_migration_reverse_direction__"
                "mock__r001",
            ),
        ),
        runtime=tidb_runtime(
            release=TIDB_V8_1_0,
            pd_count=3,
            tikv_count=3,
            tidb_count=2,
            sql_timeout_seconds=180,
            image_group_key="bc02-cdc-migration",
        ),
        source_dc="west",
        target_dc="east",
        source_db="bc02_west",
        target_db="bc02_east",
        archive_db="bc02_archive",
        control_db="bc02_billing_control",
        order_table="billing_orders",
        event_table="billing_cdc_events",
        intent_table="billing_intents",
        route_table="billing_routes",
        changefeed_table="billing_changefeeds",
        migration_table="billing_migrations",
        validation_table="billing_validation_requests",
        route_service="billing-api",
        migration_id="billing-west-east-20260813",
        forward_feed_id="billing-west-east-forward",
        reverse_feed_id="billing-east-west-reverse",
        snapshot_rows=1200,
        source_rows=1700,
        slo_p95_ms=12_000.0,
        poll_interval_seconds=0.25,
        final_state_attempts=40,
        final_state_interval_seconds=0.5,
        initial_cutover_done=False,
        initial_route_epoch=1,
        checkpoint_gap_rows=0,
        reverse_region_filter="all",
        source_incarnation="billing-journal-13",
        target_incarnation="billing-journal-29",
        retired_target_incarnation="billing-journal-07",
        previous_target_incarnation="billing-journal-17",
        candidate_target_incarnation="billing-journal-candidate",
        reverse_event_namespace="billing-journal-29",
        collision_history_rows=0,
        producer_clock_reset_rows=0,
        reference_path=(
            "billing-api remains on west while the reverse-direction migration is incomplete",
            "forward lag reaching zero with equal west/east business truth and the activated "
            "east-to-west reverse link establish both-direction readiness in one correlated read",
            "billing-api cuts over to east only after both directions are caught up, and "
            "rollback-ready observation with equal truth and SLO closes the migration",
        ),
        reference_tool_counts=(
            ("workload_activity_query_latency_active_connections", 20, 40),
            ("control_plane_sql_rows", 7, 116),
            ("business_truth_and_slo_sql_rows", 3, 49),
        ),
    )
)


class TidbBusinessChangeCdcDcMigrationScenario(TiDBScenario):
    scenario_id = "tidb_business_change_cdc_dc_migration"
    description = (
        "Runs a real SQL-backed online data-center migration with a background business workload, "
        "forward and reverse changefeeds, route cutover, and rollback readiness."
    )
    cases = (
        _TIDB_BUSINESS_CHANGE_CDC_DC_MIGRATION_CASE,
        _TIDB_BUSINESS_CHANGE_CDC_DC_MIGRATION_REVERSE_CASE,
    )

    def build_fault_plan(
        self,
        case: TidbBusinessChangeCdcDcMigrationForReverseCutoverScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangeCdcDcMigrationInjector,
                config={
                    "source_dc": case.source_dc,
                    "target_dc": case.target_dc,
                    "source_db": case.source_db,
                    "target_db": case.target_db,
                    "archive_db": case.archive_db,
                    "control_db": case.control_db,
                    "order_table": case.order_table,
                    "event_table": case.event_table,
                    "intent_table": case.intent_table,
                    "route_table": case.route_table,
                    "changefeed_table": case.changefeed_table,
                    "migration_table": case.migration_table,
                    "validation_table": case.validation_table,
                    "route_service": case.route_service,
                    "migration_id": case.migration_id,
                    "forward_feed_id": case.forward_feed_id,
                    "reverse_feed_id": case.reverse_feed_id,
                    "snapshot_rows": case.snapshot_rows,
                    "source_rows": case.source_rows,
                    "slo_p95_ms": case.slo_p95_ms,
                    "poll_interval_seconds": case.poll_interval_seconds,
                    "initial_cutover_done": case.initial_cutover_done,
                    "initial_route_epoch": case.initial_route_epoch,
                    "checkpoint_gap_rows": case.checkpoint_gap_rows,
                    "reverse_region_filter": case.reverse_region_filter,
                    "source_incarnation": case.source_incarnation,
                    "target_incarnation": case.target_incarnation,
                    "retired_target_incarnation": case.retired_target_incarnation,
                    "previous_target_incarnation": case.previous_target_incarnation,
                    "candidate_target_incarnation": case.candidate_target_incarnation,
                    "reverse_event_namespace": case.reverse_event_namespace,
                    "collision_history_rows": case.collision_history_rows,
                    "producer_clock_reset_rows": case.producer_clock_reset_rows,
                },
            ),
        )


__all__ = (
    "TidbBusinessChangeCdcDcMigrationForReverseCutoverScenarioCase",
    "TidbBusinessChangeCdcDcMigrationForReverseDirectionScenarioCase",
    "TidbBusinessChangeCdcDcMigrationScenario",
    "TidbBusinessChangeRollingUpgradeForRollingUpgrade6_5To7_5ScenarioCase",
    "TidbBusinessChangeRollingUpgradeForRollingUpgrade7_5To8_1ScenarioCase",
    "TidbBusinessChangeRollingUpgradeScenario",
    "TidbBusinessChangeLargeTableBatchDmlCase",
    "TidbBusinessChangeLargeTableBatchDmlForLargeTableBatchUpdateAndIndexScenarioCase",
    "TidbBusinessChangeLargeTableBatchDmlScenario",
    "TidbBusinessChangeLightningCheckpointCase",
    "TidbBusinessChangeLightningCheckpointForLightningCheckpointScaleOutScenarioCase",
    "TidbBusinessChangeLightningCheckpointScenario",
    "TidbBusinessChangeDmReplaceCase",
    "TidbBusinessChangeDmReplaceForFailedDdlSafeReplaceScenarioCase",
    "TidbBusinessChangeDmReplaceScenario",
    "TidbBusinessChangeTableRecoveryCase",
    "TidbBusinessChangeTableRecoveryForDroppedTableGcRecoveryScenarioCase",
    "TidbBusinessChangeTableRecoveryScenario",
    "BusinessDecoySpec",
    "TidbBusinessChangeOnlineDdlPauseResumeCase",
    "TidbBusinessChangeOnlineDdlPauseResumeForPausedIndexBackfillScenarioCase",
    "TidbBusinessChangeOnlineDdlPauseResumeScenario",
    "TidbBusinessChangeBc03Case",
    "TidbBusinessChangeBc03ForRetentionArchiveScenarioCase",
    "TidbBusinessChangeBatchedDmlDdlScenario",
    "TidbBusinessChangeDrAutoSyncFailoverCase",
    "TidbBusinessChangeDrAutoSyncFailoverScenario",
    "TidbBusinessChangeDrAutoSyncForPlannedFailoverScenarioCase",
    "TidbBusinessChangeDrAutoSyncPlannedInjector",
    "TidbBusinessChangeDrAutoSyncForUnplannedFailoverScenarioCase",
    "TidbBusinessChangeDrAutoSyncUnplannedInjector",
)


import threading
from collections.abc import Mapping
from datetime import datetime, timedelta

import pymysql

from src.database.sql import execute_result_rows, require_success_payload

from src.scenarios.tidb.common import BaseFaultInjector, FaultLifecycleContext, validate_sql_identifier


class TidbBusinessChangeCdcDcMigrationInjector(BaseFaultInjector):
    """Create a real SQL-backed online migration and run its changefeed workers.

    The benchmark uses two databases in one TiDB cluster because the fixed Docker lane
    does not ship a second TiDB deployment or a TiCDC binary. The replication process is
    still real: it consumes committed change rows, applies them through TiDB SQL, updates
    checkpoints, and exposes its observed state through control tables.
    """

    def __init__(self):
        self._thread = None
        self._stop_event = None
        self._worker_error = None
        self._last_route = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._create_databases()
        self._create_tables()
        self._seed_data()
        self._verify_initial_state()
        self._start_controller()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_persistent_state()
        self._start_controller()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config, context.env)
        self._verify_persistent_state()
        return {
            "bc02_route": self._rows(
                f"SELECT service_name, active_dc, route_epoch FROM {self.control_db}.{self.route_table}",
                "capture BC02 route observability",
            ),
            "bc02_changefeeds": self._rows(
                f"SELECT feed_id, direction, state, enabled, lag_events "
                f"FROM {self.control_db}.{self.changefeed_table} ORDER BY feed_id",
                "capture BC02 changefeed observability",
            ),
            "bc02_business_baseline": self._rows(
                f"SELECT COUNT(*), COALESCE(SUM(amount_cents), 0) "
                f"FROM {self.source_db}.{self.order_table}",
                "capture BC02 business baseline",
            ),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._stop_controller(raise_worker_error=True)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        worker_error = self._stop_controller(raise_worker_error=False)
        if worker_error is not None:
            raise RuntimeError(
                f"BC02 controller failed before recovery: database={self.source_db}/{self.target_db}, "
                f"error={worker_error!r}"
            ) from worker_error

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.source_dc = str(config["source_dc"])
        self.target_dc = str(config["target_dc"])
        self.source_db = validate_sql_identifier(str(config["source_db"]), "source_db")
        self.target_db = validate_sql_identifier(str(config["target_db"]), "target_db")
        self.archive_db = validate_sql_identifier(str(config["archive_db"]), "archive_db")
        self.control_db = validate_sql_identifier(str(config["control_db"]), "control_db")
        self.order_table = validate_sql_identifier(str(config["order_table"]), "order_table")
        self.event_table = validate_sql_identifier(str(config["event_table"]), "event_table")
        self.intent_table = validate_sql_identifier(str(config["intent_table"]), "intent_table")
        self.route_table = validate_sql_identifier(str(config["route_table"]), "route_table")
        self.changefeed_table = validate_sql_identifier(str(config["changefeed_table"]), "changefeed_table")
        self.migration_table = validate_sql_identifier(str(config["migration_table"]), "migration_table")
        self.validation_table = validate_sql_identifier(str(config["validation_table"]), "validation_table")
        self.route_service = str(config["route_service"])
        self.migration_id = str(config["migration_id"])
        self.forward_feed_id = str(config["forward_feed_id"])
        self.reverse_feed_id = str(config["reverse_feed_id"])
        self.snapshot_rows = int(config["snapshot_rows"])
        self.source_rows = int(config["source_rows"])
        self.slo_p95_ms = float(config["slo_p95_ms"])
        self.poll_interval_seconds = float(config["poll_interval_seconds"])
        self.initial_cutover_done = bool(config["initial_cutover_done"])
        self.initial_route_epoch = int(config["initial_route_epoch"])
        self.checkpoint_gap_rows = int(config["checkpoint_gap_rows"])
        self.reverse_region_filter = str(config["reverse_region_filter"])
        self.source_incarnation = str(config["source_incarnation"])
        self.target_incarnation = str(config["target_incarnation"])
        self.retired_target_incarnation = str(config["retired_target_incarnation"])
        self.previous_target_incarnation = str(config["previous_target_incarnation"])
        self.candidate_target_incarnation = str(config["candidate_target_incarnation"])
        self.reverse_event_namespace = str(config["reverse_event_namespace"])
        self.collision_history_rows = int(config["collision_history_rows"])
        self.producer_clock_reset_rows = int(config["producer_clock_reset_rows"])
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        if self.source_dc == self.target_dc:
            raise ValueError(f"BC02 source and target data centers must differ: dc={self.source_dc!r}")
        if not 0 < self.snapshot_rows < self.source_rows:
            raise ValueError(
                f"BC02 snapshot must be a strict prefix of source rows: "
                f"snapshot_rows={self.snapshot_rows}, source_rows={self.source_rows}"
            )
        if self.slo_p95_ms <= 0 or self.poll_interval_seconds <= 0:
            raise ValueError(
                f"BC02 runtime thresholds must be positive: "
                f"slo_p95_ms={self.slo_p95_ms}, poll_interval_seconds={self.poll_interval_seconds}"
            )
        if self.initial_route_epoch < 1 or self.checkpoint_gap_rows < 0:
            raise ValueError(
                f"BC02 initial route epoch must be positive and the unreplicable backlog non-negative: "
                f"initial_route_epoch={self.initial_route_epoch}, "
                f"checkpoint_gap_rows={self.checkpoint_gap_rows}"
            )
        if self.initial_cutover_done and self.initial_route_epoch < 2:
            raise ValueError(
                f"BC02 a completed cutover implies the route already moved once: "
                f"initial_cutover_done={self.initial_cutover_done}, initial_route_epoch={self.initial_route_epoch}"
            )

    def _connect(self, database: str | None = None, *, autocommit: bool = True):
        timeout = self.env.sql_timeout_seconds
        return pymysql.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            database=database,
            charset="utf8mb4",
            autocommit=autocommit,
            connect_timeout=5,
            read_timeout=timeout,
            write_timeout=timeout,
        )

    def _sql(self, sql: str, context: str) -> dict:
        return require_success_payload(self.env.execute_sql(sql), f"{context}: sql={sql!r}")

    def _rows(self, sql: str, context: str) -> list:
        return execute_result_rows(self.env.execute_sql, sql, context)

    def _create_databases(self) -> None:
        for database in (self.source_db, self.target_db, self.archive_db, self.control_db):
            self._sql(f"DROP DATABASE IF EXISTS {database}", f"clear BC02 database {database}")
            self._sql(f"CREATE DATABASE {database}", f"create BC02 database {database}")

    def _create_tables(self) -> None:
        for database in (self.source_db, self.target_db):
            self._sql(
                f"""
                CREATE TABLE {database}.{self.order_table} (
                    order_id BIGINT PRIMARY KEY,
                    customer_id BIGINT NOT NULL,
                    status VARCHAR(24) NOT NULL,
                    amount_cents BIGINT NOT NULL,
                    region VARCHAR(16) NOT NULL,
                    version BIGINT NOT NULL COMMENT 'Revision carried by the accepted business value.',
                    updated_at DATETIME(6) NOT NULL,
                    payload VARCHAR(128) NOT NULL,
                    authority_epoch BIGINT NOT NULL DEFAULT 1
                        COMMENT 'Producer registry epoch carried by the accepted business value.',
                    KEY idx_customer_status (customer_id, status),
                    KEY idx_updated_at (updated_at)
                )
                """,
                f"create BC02 order table {database}.{self.order_table}",
            )
            self._sql(
                f"""
                CREATE TABLE {database}.{self.event_table} (
                    event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    order_id BIGINT NOT NULL,
                    customer_id BIGINT NOT NULL,
                    status VARCHAR(24) NOT NULL,
                    amount_cents BIGINT NOT NULL,
                    region VARCHAR(16) NOT NULL,
                    version BIGINT NOT NULL COMMENT 'Committed business revision; handoff_validation projections have no business revision and use zero.',
                    updated_at DATETIME(6) NOT NULL,
                    origin_dc VARCHAR(16) NOT NULL,
                    event_source VARCHAR(24) NOT NULL COMMENT 'application is a committed business mutation; handoff_validation is a committed outbox projection with no business mutation; replication is a delivery envelope.',
                    origin_event_id BIGINT NOT NULL,
                    event_ts DATETIME(6) NOT NULL,
                    source_incarnation VARCHAR(96) NOT NULL,
                    event_namespace VARCHAR(96) NOT NULL,
                    UNIQUE KEY uq_origin_event (event_namespace, origin_dc, origin_event_id),
                    KEY idx_origin_event (origin_dc, event_id)
                )
                """,
                f"create BC02 event table {database}.{self.event_table}",
            )
        self._sql(
            f"""
            CREATE TABLE {self.archive_db}.{self.order_table} (
                order_id BIGINT PRIMARY KEY,
                customer_id BIGINT NOT NULL,
                status VARCHAR(24) NOT NULL,
                amount_cents BIGINT NOT NULL,
                region VARCHAR(16) NOT NULL,
                version BIGINT NOT NULL,
                updated_at DATETIME(6) NOT NULL,
                payload VARCHAR(128) NOT NULL,
                authority_epoch BIGINT NOT NULL DEFAULT 1
            )
            """,
            f"create BC02 archive decoy table {self.archive_db}.{self.order_table}",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.{self.intent_table} (
                intent_seq BIGINT AUTO_INCREMENT PRIMARY KEY,
                intent_id VARCHAR(64) NOT NULL,
                customer_id BIGINT NOT NULL,
                amount_cents BIGINT NOT NULL,
                request_source VARCHAR(64) NOT NULL,
                status ENUM('pending', 'processed') NOT NULL DEFAULT 'pending',
                processed_dc VARCHAR(16),
                processed_at DATETIME(6),
                requested_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                UNIQUE KEY uq_intent_id (intent_id),
                KEY idx_intent_status (status, requested_at)
            )
            """,
            f"create BC02 intent table {self.control_db}.{self.intent_table}",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.{self.route_table} (
                service_name VARCHAR(64) PRIMARY KEY,
                active_dc ENUM('east', 'west') NOT NULL,
                route_epoch BIGINT NOT NULL,
                changed_at DATETIME(6) NOT NULL
            )
            """,
            f"create BC02 route table {self.control_db}.{self.route_table}",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.{self.changefeed_table} (
                feed_id VARCHAR(96) PRIMARY KEY,
                direction ENUM('east_to_west', 'west_to_east') NOT NULL,
                source_dc ENUM('east', 'west') NOT NULL,
                target_dc ENUM('east', 'west') NOT NULL,
                state ENUM('normal', 'paused') NOT NULL,
                enabled TINYINT NOT NULL,
                region_filter ENUM('all', 'north', 'south', 'east', 'west', 'live') NOT NULL
                    COMMENT 'Business region coverage; all selects every region. Consumed checkpoint includes excluded events.',
                event_namespace VARCHAR(96) NOT NULL
                    COMMENT 'Destination idempotence namespace; duplicate event UIDs are acknowledged before business apply.',
                namespace_binding ENUM('fixed','source_incarnation') NOT NULL DEFAULT 'fixed'
                    COMMENT 'fixed uses event_namespace; source_incarnation uses event_namespace root + / + immutable source_incarnation.',
                source_incarnation_filter VARCHAR(96) NOT NULL DEFAULT 'all'
                    COMMENT 'all consumes all source incarnations; a registered incarnation selects that source and acknowledges excluded rows.',
                apply_ordering ENUM('version','business_time','authority_epoch') NOT NULL
                    COMMENT 'version compares local revision; business_time compares producer updated_at; authority_epoch compares registry epoch then local revision. Duplicate UIDs never reapply.',
                last_applied_event_id BIGINT NOT NULL,
                resolved_event_id BIGINT NOT NULL,
                lag_events BIGINT NOT NULL,
                last_error VARCHAR(512),
                activated_at DATETIME(6),
                updated_at DATETIME(6) NOT NULL
            )
            """,
            f"create BC02 changefeed table {self.control_db}.{self.changefeed_table}",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.{self.migration_table} (
                migration_id VARCHAR(96) PRIMARY KEY,
                phase ENUM('catchup', 'reverse_required', 'unsafe_cutover', 'cutover_observed', 'rollback_ready', 'observation') NOT NULL,
                current_primary ENUM('east', 'west') NOT NULL,
                unsafe_cutover_attempt TINYINT NOT NULL,
                rollback_ready TINYINT NOT NULL,
                target_app_events BIGINT NOT NULL,
                reverse_applied_events BIGINT NOT NULL,
                p95_latency_ms DECIMAL(10,3) NOT NULL,
                reverse_ready_observed_at DATETIME(6),
                cutover_observed_at DATETIME(6),
                cutover_event_id BIGINT,
                updated_at DATETIME(6) NOT NULL
            )
            """,
            f"create BC02 migration control table {self.control_db}.{self.migration_table}",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.{self.validation_table} (
                request_id VARCHAR(96) PRIMARY KEY,
                validation_kind VARCHAR(48) NOT NULL,
                status VARCHAR(24) NOT NULL,
                requested_at DATETIME(6) NOT NULL,
                result_note VARCHAR(512)
            )
            """,
            f"create BC02 validation table {self.control_db}.{self.validation_table}",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.replication_observations (
                observation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                observed_at DATETIME(6) NOT NULL,
                route_dc VARCHAR(16) NOT NULL,
                forward_lag_events BIGINT NOT NULL,
                reverse_lag_events BIGINT NOT NULL,
                p95_latency_ms DECIMAL(10,3) NOT NULL,
                target_app_events BIGINT NOT NULL,
                reverse_applied_events BIGINT NOT NULL,
                source_order_count BIGINT NOT NULL,
                target_order_count BIGINT NOT NULL,
                KEY idx_observed_at (observed_at)
            )
            """,
            "create BC02 replication observations table",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.service_slo_samples (
                sample_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                observed_at DATETIME(6) NOT NULL,
                route_dc VARCHAR(16) NOT NULL,
                p95_latency_ms DECIMAL(10,3) NOT NULL,
                error_rate DECIMAL(8,5) NOT NULL
            )
            """,
            "create BC02 SLO sample table",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.migration_audit (
                audit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                event_type VARCHAR(32) NOT NULL,
                previous_dc VARCHAR(16),
                current_dc VARCHAR(16) NOT NULL,
                forward_lag_events BIGINT NOT NULL,
                reverse_state VARCHAR(24) NOT NULL,
                observed_at DATETIME(6) NOT NULL
            )
            """,
            "create BC02 migration audit table",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.checkpoint_imports (
                import_id BIGINT PRIMARY KEY,
                source_feed_id VARCHAR(96) NOT NULL,
                source_position_kind ENUM('applied_event_count', 'event_id') NOT NULL,
                source_position BIGINT NOT NULL,
                destination_feed_id VARCHAR(96) NOT NULL,
                imported_at DATETIME(6) NOT NULL
            )
            """,
            "create BC02 checkpoint import provenance",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.stream_incarnations (
                incarnation_id VARCHAR(96) PRIMARY KEY,
                source_dc VARCHAR(16) NOT NULL,
                service_name VARCHAR(64) NOT NULL,
                lifecycle ENUM('current', 'retired', 'candidate') NOT NULL,
                opened_at DATETIME(6) NOT NULL,
                closed_at DATETIME(6),
                version_scope ENUM('global_order_revision','incarnation_local') NOT NULL,
                authority_epoch BIGINT NOT NULL COMMENT 'Proposed handoff epoch; activation decisions establish effective business authority.',
                clock_scope ENUM('global_business_time','producer_local') NOT NULL
                    COMMENT 'Scope of producer updated_at and event_ts wall clocks.',
                outbox_mode ENUM('business_commit','handoff_validation') NOT NULL
                    COMMENT 'business_commit emits committed business revisions; handoff_validation emits projected values without committing business mutations.'
            )
            """,
            "create BC02 producer incarnation registry",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.handoff_decisions (
                decision_id BIGINT PRIMARY KEY,
                service_name VARCHAR(64) NOT NULL,
                source_dc VARCHAR(16) NOT NULL,
                incarnation_id VARCHAR(96) NOT NULL,
                proposed_epoch BIGINT NOT NULL,
                decision ENUM('activate','abort') NOT NULL,
                effective_at DATETIME(6) NOT NULL
            )
            """,
            "create BC02 raw handoff decision receipt ledger",
        )

    def _seed_data(self) -> None:
        now = datetime(2026, 6, 29, 12, 0, 0) if self.producer_clock_reset_rows else datetime.utcnow()
        connection = self._connect(self.source_db, autocommit=False)
        try:
            with connection.cursor() as cursor:
                orders = []
                events = []
                for order_id in range(1, self.source_rows + 1):
                    updated_at = now - timedelta(seconds=self.source_rows - order_id)
                    customer_id = 1000 + (order_id % 9000)
                    status = ("paid", "packed", "shipped", "delivered")[order_id % 4]
                    amount = 100 + (order_id * 37) % 9900
                    region = ("north", "south", "east", "west")[order_id % 4]
                    payload = f"seed-order-{order_id}"
                    orders.append((order_id, customer_id, status, amount, region, order_id, updated_at, payload))
                    events.append((order_id, order_id, customer_id, status, amount, region, order_id, updated_at, self.source_dc, "snapshot_seed", order_id, updated_at, self.source_incarnation, self.source_incarnation))
                cursor.executemany(
                    f"INSERT INTO {self.order_table} "
                    "(order_id, customer_id, status, amount_cents, region, version, updated_at, payload) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    orders,
                )
                cursor.executemany(
                    f"INSERT INTO {self.event_table} "
                    "(event_id, order_id, customer_id, status, amount_cents, region, version, updated_at, "
                    "origin_dc, event_source, origin_event_id, event_ts, source_incarnation, event_namespace) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    events,
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        self._sql(
            f"INSERT INTO {self.target_db}.{self.order_table} "
            f"SELECT * FROM {self.source_db}.{self.order_table} WHERE order_id <= {self.snapshot_rows}",
            "seed BC02 target snapshot",
        )
        self._sql(
            f"INSERT INTO {self.archive_db}.{self.order_table} "
            f"SELECT * FROM {self.source_db}.{self.order_table} WHERE order_id <= {self.snapshot_rows // 2}",
            "seed BC02 archive decoy",
        )
        initial_route_dc = self.target_dc if self.initial_cutover_done else self.source_dc
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.route_table}
                (service_name, active_dc, route_epoch, changed_at)
            VALUES ('{self.route_service}', '{initial_route_dc}', {self.initial_route_epoch}, CURRENT_TIMESTAMP(6))
            """,
            "seed BC02 initial route",
        )
        reverse_seed_state = "normal" if self.initial_cutover_done else "paused"
        reverse_seed_enabled = 1 if self.initial_cutover_done else 0
        reverse_checkpoint = self.rehearsal_window_events if self.checkpoint_gap_rows else 0
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.changefeed_table}
                (feed_id, direction, source_dc, target_dc, state, enabled, region_filter, event_namespace, apply_ordering,
                 last_applied_event_id, resolved_event_id, lag_events, last_error, updated_at)
            VALUES
                ('{self.forward_feed_id}', '{self.source_dc}_to_{self.target_dc}', '{self.source_dc}', '{self.target_dc}',
                 'normal', 1, 'all', '{self.source_incarnation}', 'version', {self.snapshot_rows}, {self.source_rows},
                 {self.source_rows - self.snapshot_rows}, NULL, CURRENT_TIMESTAMP(6)),
                ('{self.reverse_feed_id}', '{self.target_dc}_to_{self.source_dc}', '{self.target_dc}', '{self.source_dc}',
                 '{reverse_seed_state}', {reverse_seed_enabled}, '{self.reverse_region_filter}', '{self.reverse_event_namespace}', 'version', {reverse_checkpoint}, {reverse_checkpoint}, 0, NULL,
                 CURRENT_TIMESTAMP(6))
            """,
            "seed BC02 changefeeds",
        )
        if self.initial_cutover_done:
            self._sql(
                f"""
                INSERT INTO {self.control_db}.{self.migration_table}
                    (migration_id, phase, current_primary, unsafe_cutover_attempt, rollback_ready,
                     target_app_events, reverse_applied_events, p95_latency_ms,
                     reverse_ready_observed_at, cutover_observed_at, cutover_event_id, updated_at)
                VALUES ('{self.migration_id}', 'observation', '{self.target_dc}', 0, 0, 0, 0, 0,
                        CURRENT_TIMESTAMP(6), CURRENT_TIMESTAMP(6), 0, CURRENT_TIMESTAMP(6))
                """,
                "seed BC02 migration control after the planned cutover",
            )
        else:
            self._sql(
                f"""
                INSERT INTO {self.control_db}.{self.migration_table}
                    (migration_id, phase, current_primary, unsafe_cutover_attempt, rollback_ready,
                     target_app_events, reverse_applied_events, p95_latency_ms, updated_at)
                VALUES ('{self.migration_id}', 'catchup', '{self.source_dc}', 0, 0, 0, 0, 0, CURRENT_TIMESTAMP(6))
                """,
                "seed BC02 migration control",
            )
        self._sql(
            f"INSERT INTO {self.control_db}.{self.validation_table} "
            "(request_id, validation_kind, status, requested_at, result_note) VALUES "
            "('old-snapshot-check-20260731', 'snapshot_checksum', 'expired', CURRENT_TIMESTAMP(6), 'old migration validation')",
            "seed BC02 validation decoy",
        )
        self._seed_rehearsal_fleet()
        if self.checkpoint_gap_rows:
            self._sql(
                f"INSERT INTO {self.control_db}.checkpoint_imports VALUES "
                f"(1, '{self.rehearsal_reverse_feed_id}', 'applied_event_count', "
                f"{self.rehearsal_window_events}, '{self.reverse_feed_id}', CURRENT_TIMESTAMP(6))",
                "record BC02 imported rehearsal checkpoint position",
            )
        self._sql(
            f"INSERT INTO {self.control_db}.stream_incarnations VALUES "
            f"('{self.source_incarnation}', '{self.source_dc}', '{self.route_service}', "
            "'current', '2026-01-01 00:00:00', NULL, 'global_order_revision', 1, 'global_business_time', 'business_commit'), "
            f"('{self.target_incarnation}', '{self.target_dc}', '{self.route_service}', "
            f"'current', '2026-07-01 00:00:00', NULL, '{'incarnation_local' if self.producer_clock_reset_rows else 'global_order_revision'}', {3 if self.producer_clock_reset_rows else 1}, '{'producer_local' if self.producer_clock_reset_rows else 'global_business_time'}', 'business_commit'), "
            f"('{self.retired_target_incarnation}', '{self.target_dc}', '{self.route_service}', "
            f"'retired', '2026-01-01 00:00:00', '2026-06-29 00:00:00', '{'incarnation_local' if self.producer_clock_reset_rows else 'global_order_revision'}', 0, '{'producer_local' if self.producer_clock_reset_rows else 'global_business_time'}', 'business_commit')",
            "register actual current and retired source incarnations",
        )
        if self.producer_clock_reset_rows:
            self._sql(
                f"INSERT INTO {self.control_db}.stream_incarnations VALUES "
                f"('{self.previous_target_incarnation}', '{self.target_dc}', '{self.route_service}', "
                "'retired', '2026-06-30 00:00:00', '2026-07-01 00:00:00', 'incarnation_local', 2, 'producer_local', 'business_commit'), "
                f"('{self.candidate_target_incarnation}', '{self.target_dc}', '{self.route_service}', "
                "'candidate', '2026-07-02 00:00:00', '2026-07-02 00:05:00', 'incarnation_local', 4, 'producer_local', 'handoff_validation')",
                "register committed previous producer handoff authority",
            )
            self._sql(
                f"INSERT INTO {self.control_db}.handoff_decisions VALUES "
                f"(1,'{self.route_service}','{self.target_dc}','{self.previous_target_incarnation}',2,'activate','2026-06-30 00:00:00'), "
                f"(2,'{self.route_service}','{self.target_dc}','{self.target_incarnation}',3,'activate','2026-07-01 00:00:00'), "
                f"(3,'{self.route_service}','{self.target_dc}','{self.candidate_target_incarnation}',4,'abort','2026-07-02 00:05:00')",
                "seed actual producer activation and aborted candidate decision receipts",
            )
        if self.collision_history_rows:
            self._sql(
                f"INSERT INTO {self.source_db}.{self.event_table} "
                "(order_id, customer_id, status, amount_cents, region, version, updated_at, "
                "origin_dc, event_source, origin_event_id, event_ts, source_incarnation, event_namespace) "
                "SELECT order_id, customer_id, status, amount_cents, region, 0, "
                f"'2026-06-29 12:00:00', '{self.target_dc}', 'replication', order_id, "
                f"'2026-06-29 12:00:00', '{self.retired_target_incarnation}', "
                f"'{self.retired_target_incarnation}' FROM {self.source_db}.{self.order_table} "
                f"WHERE order_id <= {self.collision_history_rows}",
                "retain genuine old producer events for earlier snapshot-order versions",
            )

    def _seed_rehearsal_fleet(self) -> None:
        """Park the previous rehearsal migration fleet next to the live migration.

        The rehearsal rows share the schema, direction pairs, and service prefix of the
        live migration but belong to the closed 2026-07-01 rehearsal window. They are
        never advanced by the controller, so their frozen updated_at/stale lag is the
        Agent-visible discriminant against the live migration lineage.

        The rehearsal window also left real business orders in the target DC that the
        parked reverse link never synced back: west-only rehearsal orders make the two
        DCs' business truth unequal until the live reverse feed replicates them.
        """
        rehearsal_window_note = "parked after the 2026-07-01 rehearsal window closed"
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.changefeed_table}
                (feed_id, direction, source_dc, target_dc, state, enabled, region_filter, event_namespace, apply_ordering,
                 last_applied_event_id, resolved_event_id, lag_events, last_error,
                 activated_at, updated_at)
            VALUES
                ('{self.rehearsal_forward_feed_id}', '{self.source_dc}_to_{self.target_dc}',
                 '{self.source_dc}', '{self.target_dc}', 'paused', 0, 'all', '{self.source_incarnation}', 'version',
                 {self.source_rows}, {self.source_rows}, 0, '{rehearsal_window_note}',
                 '2026-07-01 10:00:00', '2026-07-02 09:00:00'),
                ('{self.rehearsal_reverse_feed_id}', '{self.target_dc}_to_{self.source_dc}',
                 '{self.target_dc}', '{self.source_dc}', 'normal', 1, '{self.reverse_region_filter}', '{self.retired_target_incarnation}', 'version',
                 {self.rehearsal_window_events}, {self.rehearsal_window_events}, 0, NULL,
                 '2026-07-01 10:45:00', '2026-07-02 09:00:00')
            """,
            "seed BC02 rehearsal changefeed fleet",
        )
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.migration_table}
                (migration_id, phase, current_primary, unsafe_cutover_attempt, rollback_ready,
                 target_app_events, reverse_applied_events, p95_latency_ms,
                 reverse_ready_observed_at, cutover_observed_at, cutover_event_id, updated_at)
            VALUES ('{self.rehearsal_migration_id}', 'observation', '{self.target_dc}', 0, 0,
                    {self.rehearsal_window_events}, {self.rehearsal_window_events}, 11.500,
                    '2026-07-01 11:20:00', '2026-07-01 11:05:00',
                    {self.rehearsal_window_events}, '2026-07-02 09:00:00')
            """,
            "seed BC02 rehearsal migration control",
        )
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.validation_table}
                (request_id, validation_kind, status, requested_at, result_note)
            VALUES ('{self.rehearsal_migration_id}-validation', 'snapshot_checksum', 'passed',
                    '2026-07-01 10:30:00', '2026-07-01 rehearsal window validation passed')
            """,
            "seed BC02 rehearsal validation decoy",
        )
        self._sql(
            f"""
            INSERT INTO {self.control_db}.migration_audit
                (event_type, previous_dc, current_dc, forward_lag_events, reverse_state, observed_at)
            VALUES
                ('route_cutover', '{self.source_dc}', '{self.target_dc}', 0, 'normal', '2026-07-01 11:05:00'),
                ('route_cutover', '{self.target_dc}', '{self.source_dc}', 0, 'normal', '2026-07-01 11:40:00')
            """,
            "seed BC02 rehearsal audit history",
        )
        self._seed_rehearsal_target_backlog()
        if self.producer_clock_reset_rows:
            self._sql(
                f"UPDATE {self.target_db}.{self.order_table} SET authority_epoch=3 WHERE order_id>=3000000",
                "bind committed current-producer backlog authority",
            )
            self._seed_clock_reset_updates()
            self._seed_previous_incarnation_updates()
            self._seed_candidate_validation_outbox()

    def _seed_rehearsal_target_backlog(self) -> None:
        """Write the rehearsal-window orders that exist only in the target DC.

        These rows are real business truth (protected: agents must not mutate them).
        The journal-covered cohort rides the target event table as west-origin
        application events, so the live reverse feed drains it as soon as it runs.
        The checkpoint-gap cohort has complete immutable journal coverage below the
        imported reverse cursor. Normal catchup skips it, while rewinding the live
        cursor replays the missing deliveries without changing business truth.
        """
        base_order_id = 3_000_000
        checkpoint_gap_base_order_id = 3_100_000
        connection = self._connect(self.target_db, autocommit=False)
        try:
            with connection.cursor() as cursor:
                orders = []
                events = []
                for index in range(1, self.rehearsal_window_events + 1):
                    order_id = base_order_id + index
                    updated_at = datetime(2026, 7, 1, 11, 0, 0) + timedelta(seconds=index)
                    customer_id = 1000 + (index % 9000)
                    status = "paid"
                    amount = 100 + (index * 53) % 9900
                    region = "west"
                    payload = f"rehearsal-order-{index}"
                    orders.append((order_id, customer_id, status, amount, region, index, updated_at, payload))
                    event_id = self.rehearsal_window_events + index if self.checkpoint_gap_rows else index
                    events.append((event_id, order_id, customer_id, status, amount, region, index, updated_at, self.target_dc, "application", event_id, updated_at, self.target_incarnation, self.target_incarnation))
                for index in range(1, self.checkpoint_gap_rows + 1):
                    order_id = checkpoint_gap_base_order_id + index
                    updated_at = datetime(2026, 7, 1, 11, 30, 0) + timedelta(seconds=index)
                    customer_id = 1000 + (index % 9000)
                    status = "paid"
                    amount = 100 + (index * 71) % 9900
                    region = self.source_dc
                    payload = f"rehearsal-order-window-{index}"
                    orders.append((order_id, customer_id, status, amount, region, index, updated_at, payload))
                    events.append((index, order_id, customer_id, status, amount, region, index, updated_at, self.target_dc, "application", index, updated_at, self.target_incarnation, self.target_incarnation))
                cursor.executemany(
                    f"INSERT INTO {self.order_table} "
                    "(order_id, customer_id, status, amount_cents, region, version, updated_at, payload) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    orders,
                )
                cursor.executemany(
                    f"INSERT INTO {self.event_table} "
                    "(event_id, order_id, customer_id, status, amount_cents, region, version, updated_at, "
                    "origin_dc, event_source, origin_event_id, event_ts, source_incarnation, event_namespace) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    events,
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _seed_clock_reset_updates(self) -> None:
        connection = self._connect(self.target_db, autocommit=False)
        try:
            with connection.cursor() as cursor:
                for index in range(1, self.producer_clock_reset_rows + 1):
                    order_id = 100 + index
                    event_id = self.checkpoint_gap_rows + index
                    updated_at = datetime(2026, 6, 28, 11, 30, 0) + timedelta(seconds=event_id)
                    customer_id = 1000 + order_id
                    amount = 50 + index
                    cursor.execute(
                        f"UPDATE {self.order_table} SET status='cancelled', amount_cents=%s, "
                        "region='west', version=%s, updated_at=%s, authority_epoch=3 WHERE order_id=%s",
                        (amount, event_id, updated_at, order_id),
                    )
                    cursor.execute(
                        f"INSERT INTO {self.event_table} "
                        "(event_id, order_id, customer_id, status, amount_cents, region, version, updated_at, "
                        "origin_dc, event_source, origin_event_id, event_ts, source_incarnation, event_namespace) "
                        "VALUES (%s,%s,%s,'cancelled',%s,'west',%s,%s,%s,'application',%s,%s,%s,%s)",
                        (event_id, order_id, customer_id, amount, event_id, updated_at,
                         self.target_dc, event_id, updated_at, self.target_incarnation, self.target_incarnation),
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _seed_previous_incarnation_updates(self) -> None:
        connection = self._connect(self.target_db, autocommit=False)
        try:
            with connection.cursor() as cursor:
                for index in range(1, self.producer_clock_reset_rows + 1):
                    order_id = 200 + index
                    updated_at = datetime(2026, 6, 30, 11, 0, 0) + timedelta(seconds=index)
                    amount = 70 + index
                    cursor.execute(
                        f"UPDATE {self.order_table} SET status='refunded', amount_cents=%s, "
                        "region='west', version=%s, updated_at=%s, authority_epoch=2 WHERE order_id=%s",
                        (amount, index, updated_at, order_id),
                    )
                    cursor.execute(
                        f"INSERT INTO {self.event_table} "
                        "(event_id, order_id, customer_id, status, amount_cents, region, version, updated_at, "
                        "origin_dc, event_source, origin_event_id, event_ts, source_incarnation, event_namespace) "
                        "VALUES (%s,%s,%s,'refunded',%s,'west',%s,%s,%s,'application',%s,%s,%s,%s)",
                        (2 * self.rehearsal_window_events + index, order_id, 1000 + order_id,
                         amount, index, updated_at, self.target_dc, index, updated_at,
                         self.previous_target_incarnation, self.previous_target_incarnation),
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _seed_candidate_validation_outbox(self) -> None:
        """Commit dry-run outbox projections, without allocating a business revision."""
        connection = self._connect(self.target_db, autocommit=False)
        try:
            with connection.cursor() as cursor:
                for index in range(1, self.producer_clock_reset_rows + 1):
                    observed_at = datetime(2026, 7, 2, 0, 1, 0) + timedelta(seconds=index)
                    cursor.execute(
                        f"INSERT INTO {self.event_table} "
                        "(event_id,order_id,customer_id,status,amount_cents,region,version,updated_at,"
                        "origin_dc,event_source,origin_event_id,event_ts,source_incarnation,event_namespace) "
                        "VALUES (%s,%s,%s,'refunded',%s,'west',0,%s,%s,'handoff_validation',%s,%s,%s,%s)",
                        (2 * self.rehearsal_window_events + self.producer_clock_reset_rows + index,
                         100 + index, 1100 + index, 7000 + index, observed_at, self.target_dc,
                         index, observed_at, self.candidate_target_incarnation, self.candidate_target_incarnation),
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @property
    def rehearsal_migration_id(self) -> str:
        return f"{self.migration_id.rsplit('-', 1)[0]}-20260701-rehearsal"

    @property
    def rehearsal_forward_feed_id(self) -> str:
        return f"{self.forward_feed_id}-20260701"

    @property
    def rehearsal_reverse_feed_id(self) -> str:
        return f"{self.reverse_feed_id}-20260701"

    @property
    def rehearsal_window_events(self) -> int:
        return 45

    def _verify_initial_state(self) -> None:
        initial_route_dc = self.target_dc if self.initial_cutover_done else self.source_dc
        rows = self._rows(
            f"SELECT active_dc, route_epoch FROM {self.control_db}.{self.route_table} "
            f"WHERE service_name = '{self.route_service}'",
            "verify BC02 initial route",
        )
        if rows != [[initial_route_dc, self.initial_route_epoch]]:
            raise RuntimeError(
                f"BC02 initial route mismatch: expected={initial_route_dc!r}/{self.initial_route_epoch}, rows={rows!r}"
            )
        rows = self._rows(
            f"SELECT state, enabled, lag_events FROM {self.control_db}.{self.changefeed_table} "
            f"WHERE feed_id = '{self.forward_feed_id}'",
            "verify BC02 forward changefeed",
        )
        if rows != [["normal", 1, self.source_rows - self.snapshot_rows]]:
            raise RuntimeError(f"BC02 forward changefeed mismatch: rows={rows!r}")
        rows = self._rows(
            f"SELECT state, enabled FROM {self.control_db}.{self.changefeed_table} "
            f"WHERE feed_id = '{self.reverse_feed_id}'",
            "verify BC02 reverse changefeed",
        )
        expected_reverse_state = ["normal", 1] if self.initial_cutover_done else ["paused", 0]
        if rows != [expected_reverse_state]:
            raise RuntimeError(f"BC02 reverse changefeed must start {expected_reverse_state[0]}: rows={rows!r}")
        source_count = self._rows(
            f"SELECT COUNT(*) FROM {self.source_db}.{self.order_table}",
            "verify BC02 source rows",
        )
        target_count = self._rows(
            f"SELECT COUNT(*) FROM {self.target_db}.{self.order_table}",
            "verify BC02 target snapshot rows",
        )
        expected_target_rows = self.snapshot_rows + self.rehearsal_window_events + self.checkpoint_gap_rows
        if source_count != [[self.source_rows]] or target_count != [[expected_target_rows]]:
            raise RuntimeError(
                f"BC02 initial snapshot mismatch: source={source_count!r}, target={target_count!r}, "
                f"expected={self.source_rows}/{expected_target_rows}"
            )

    def _verify_persistent_state(self) -> None:
        initial_route_dc = self.target_dc if self.initial_cutover_done else self.source_dc
        route_rows = self._rows(
            f"SELECT active_dc, route_epoch FROM {self.control_db}.{self.route_table} "
            f"WHERE service_name = '{self.route_service}'",
            "verify BC02 persistent route",
        )
        if route_rows != [[initial_route_dc, self.initial_route_epoch]]:
            raise RuntimeError(f"BC02 persistent route mismatch before Agent actions: rows={route_rows!r}")
        feed_rows = self._rows(
            f"SELECT feed_id, state, enabled, lag_events FROM {self.control_db}.{self.changefeed_table} "
            "ORDER BY feed_id",
            "verify BC02 persistent changefeeds",
        )
        expected_ids = {
            self.forward_feed_id,
            self.reverse_feed_id,
            self.rehearsal_forward_feed_id,
            self.rehearsal_reverse_feed_id,
        }
        observed_ids = {row[0] for row in feed_rows}
        if observed_ids != expected_ids:
            raise RuntimeError(
                f"BC02 persistent changefeed IDs mismatch: expected={sorted(expected_ids)}, rows={feed_rows!r}"
            )
        forward = next(row for row in feed_rows if row[0] == self.forward_feed_id)
        reverse = next(row for row in feed_rows if row[0] == self.reverse_feed_id)
        rehearsal_forward = next(row for row in feed_rows if row[0] == self.rehearsal_forward_feed_id)
        rehearsal_reverse = next(row for row in feed_rows if row[0] == self.rehearsal_reverse_feed_id)
        if forward[1:3] != ["normal", 1] or int(forward[3]) < 0:
            raise RuntimeError(f"BC02 persistent forward feed is invalid: row={forward!r}")
        expected_reverse_state = ["normal", 1] if self.initial_cutover_done else ["paused", 0]
        if reverse[1:3] != expected_reverse_state:
            raise RuntimeError(f"BC02 persistent reverse feed changed before Agent actions: row={reverse!r}")
        if rehearsal_forward[1:3] != ["paused", 0] or int(rehearsal_forward[3]) != 0:
            raise RuntimeError(f"BC02 rehearsal forward feed drifted before Agent actions: row={rehearsal_forward!r}")
        if rehearsal_reverse[1:3] != ["normal", 1] or int(rehearsal_reverse[3]) != 0:
            raise RuntimeError(f"BC02 rehearsal reverse feed drifted before Agent actions: row={rehearsal_reverse!r}")
        source_count = int(self._rows(
            f"SELECT COUNT(*) FROM {self.source_db}.{self.order_table}",
            "verify BC02 persistent source rows",
        )[0][0])
        target_count = int(self._rows(
            f"SELECT COUNT(*) FROM {self.target_db}.{self.order_table}",
            "verify BC02 persistent target rows",
        )[0][0])
        if source_count < self.source_rows or not self.snapshot_rows <= target_count <= source_count + self.checkpoint_gap_rows:
            raise RuntimeError(
                f"BC02 persistent snapshot bounds are invalid: source_count={source_count}, "
                f"target_count={target_count}, snapshot_rows={self.snapshot_rows}, source_rows={self.source_rows}"
            )

    def _start_controller(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            raise RuntimeError("BC02 controller is already running")
        self._stop_event = threading.Event()
        self._worker_error = None
        self._last_route = self.target_dc if self.initial_cutover_done else self.source_dc
        self._thread = threading.Thread(
            target=self._controller_main,
            name="aiopsbench-bc02-changefeed-controller",
            daemon=True,
        )
        self._thread.start()

    def _stop_controller(self, *, raise_worker_error: bool) -> BaseException | None:
        if self._thread is None:
            return None
        if self._stop_event is not None:
            self._stop_event.set()
        timeout = self.env.sql_timeout_seconds + self.poll_interval_seconds
        self._thread.join(timeout=timeout)
        if self._thread.is_alive():
            raise RuntimeError(f"BC02 controller did not stop within {timeout} seconds")
        error = self._worker_error
        self._thread = None
        self._stop_event = None
        self._worker_error = None
        if raise_worker_error and error is not None:
            raise RuntimeError(f"BC02 controller failed: error={error!r}") from error
        return error

    def _controller_main(self) -> None:
        try:
            while not self._stop_event.is_set():
                self._process_intents()
                self._advance_feed(
                    self.forward_feed_id,
                    self.source_db,
                    self.target_db,
                    self.source_dc,
                )
                self._advance_feed(
                    self.reverse_feed_id,
                    self.target_db,
                    self.source_db,
                    self.target_dc,
                )
                self._refresh_state()
                self._stop_event.wait(self.poll_interval_seconds)
        except BaseException as exc:
            self._worker_error = exc
            self._stop_event.set()

    def _process_intents(self) -> None:
        connection = self._connect(self.control_db, autocommit=False)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT intent_seq, intent_id, customer_id, amount_cents, requested_at "
                    f"FROM {self.intent_table} WHERE status = 'pending' "
                    "ORDER BY intent_seq LIMIT 32"
                )
                intents = cursor.fetchall()
                for intent_seq, intent_id, customer_id, amount_cents, requested_at in intents:
                    cursor.execute(
                        f"SELECT active_dc FROM {self.route_table} WHERE service_name = %s",
                        (self.route_service,),
                    )
                    route = cursor.fetchone()
                    if route is None:
                        raise RuntimeError(f"BC02 route disappeared while processing intent={intent_id!r}")
                    active_dc = route[0]
                    if active_dc == self.source_dc:
                        database = self.source_db
                        incarnation = self.source_incarnation
                    elif active_dc == self.target_dc:
                        database = self.target_db
                        incarnation = self.target_incarnation
                    else:
                        raise RuntimeError(
                            f"BC02 route contains unknown data center: service={self.route_service!r}, "
                            f"active_dc={active_dc!r}, expected={self.source_dc!r}/{self.target_dc!r}"
                        )
                    order_id = 1_000_000 + int(intent_seq)
                    status = "paid"
                    region = active_dc if self.checkpoint_gap_rows else "live"
                    version = int(intent_seq)
                    payload = f"live-intent-{intent_id}"
                    cursor.execute(
                        f"INSERT INTO {database}.{self.order_table} "
                        "(order_id, customer_id, status, amount_cents, region, version, updated_at, payload, authority_epoch) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                        "ON DUPLICATE KEY UPDATE customer_id=VALUES(customer_id), status=VALUES(status), "
                        "amount_cents=VALUES(amount_cents), region=VALUES(region), version=VALUES(version), "
                        "updated_at=VALUES(updated_at), payload=VALUES(payload), authority_epoch=VALUES(authority_epoch)",
                        (order_id, customer_id, status, amount_cents, region, version, requested_at, payload,
                         3 if active_dc == self.target_dc and self.producer_clock_reset_rows else 1),
                    )
                    cursor.execute(
                        f"INSERT INTO {database}.{self.event_table} "
                        "(order_id, customer_id, status, amount_cents, region, version, updated_at, "
                        "origin_dc, event_source, origin_event_id, event_ts, source_incarnation, event_namespace) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'application',-1,%s,%s,%s)",
                        (order_id, customer_id, status, amount_cents, region, version, requested_at, active_dc, requested_at, incarnation, incarnation),
                    )
                    event_id = cursor.lastrowid
                    cursor.execute(
                        f"UPDATE {database}.{self.event_table} SET origin_event_id = event_id WHERE event_id = %s",
                        (event_id,),
                    )
                    cursor.execute(
                        f"UPDATE {self.intent_table} SET status='processed', processed_dc=%s, "
                        "processed_at=CURRENT_TIMESTAMP(6) WHERE intent_seq=%s AND status='pending'",
                        (active_dc, intent_seq),
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _advance_feed(self, feed_id: str, source_db: str, target_db: str, origin_dc: str) -> None:
        connection = self._connect(self.control_db, autocommit=False)
        try:
            with connection.cursor() as cursor:
                cursor.execute("BEGIN PESSIMISTIC")
                cursor.execute(
                    f"SELECT state, enabled, last_applied_event_id, region_filter, event_namespace, apply_ordering, namespace_binding, source_incarnation_filter "
                    f"FROM {self.changefeed_table} WHERE feed_id = %s FOR UPDATE",
                    (feed_id,),
                )
                state = cursor.fetchone()
                if state is None:
                    raise RuntimeError(f"BC02 changefeed disappeared: feed_id={feed_id!r}")
                feed_state, enabled, last_applied, region_filter, event_namespace, apply_ordering, namespace_binding, incarnation_filter = state
                cursor.execute(
                    f"SELECT COALESCE(MAX(event_id), 0) FROM {source_db}.{self.event_table} WHERE origin_dc = %s",
                    (origin_dc,),
                )
                resolved = int(cursor.fetchone()[0])
                if feed_state != "normal" or int(enabled) != 1:
                    cursor.execute(
                        f"UPDATE {self.changefeed_table} SET resolved_event_id=%s, "
                        "updated_at=CURRENT_TIMESTAMP(6) WHERE feed_id=%s",
                        (resolved, feed_id),
                    )
                else:
                    cursor.execute(
                        f"SELECT ev.event_id, ev.order_id, ev.customer_id, ev.status, ev.amount_cents, ev.region, ev.version, ev.updated_at, "
                        "ev.origin_dc, ev.event_source, ev.origin_event_id, ev.event_ts, ev.source_incarnation, inc.authority_epoch "
                        f"FROM {source_db}.{self.event_table} ev "
                        f"JOIN {self.control_db}.stream_incarnations inc ON inc.incarnation_id=ev.source_incarnation "
                        "WHERE ev.event_id > %s AND ev.origin_dc = %s ORDER BY ev.event_id LIMIT 64",
                        (last_applied, origin_dc),
                    )
                    events = cursor.fetchall()
                    applied = last_applied
                    for event in events:
                        (
                            event_id, order_id, customer_id, status, amount_cents, region,
                            version, updated_at, event_origin_dc, event_source, origin_event_id, event_ts, source_incarnation, authority_epoch,
                        ) = event
                        applied = int(event_id)
                        if region_filter != "all" and region != region_filter:
                            continue
                        if incarnation_filter != "all" and source_incarnation != incarnation_filter:
                            continue
                        bound_namespace = {
                            "fixed": event_namespace,
                            "source_incarnation": f"{event_namespace}/{source_incarnation}",
                        }[namespace_binding]
                        cursor.execute(
                            f"INSERT IGNORE INTO {target_db}.{self.event_table} "
                            "(order_id, customer_id, status, amount_cents, region, version, updated_at, "
                            "origin_dc, event_source, origin_event_id, event_ts, source_incarnation, event_namespace) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'replication',%s,%s,%s,%s)",
                            (order_id, customer_id, status, amount_cents, region, version, updated_at,
                             event_origin_dc, origin_event_id, event_ts, source_incarnation, bound_namespace),
                        )
                        if cursor.rowcount == 0:
                            continue
                        columns = ("customer_id", "status", "amount_cents", "region", "payload", "version", "updated_at", "authority_epoch")
                        if apply_ordering == "authority_epoch":
                            decision = "(VALUES(authority_epoch)>authority_epoch OR (VALUES(authority_epoch)=authority_epoch AND VALUES(version)>=version))"
                            ordered_columns = tuple(column for column in columns if column not in {"version", "authority_epoch"}) + ("version", "authority_epoch")
                        else:
                            comparison = {"version": "version", "business_time": "updated_at"}[apply_ordering]
                            decision = f"VALUES({comparison})>={comparison}"
                            ordered_columns = tuple(column for column in columns if column != comparison) + (comparison,)
                        business_updates = ", ".join(
                            f"{column}=IF({decision},VALUES({column}),{column})"
                            for column in ordered_columns
                        )
                        cursor.execute(
                            f"INSERT INTO {target_db}.{self.order_table} "
                            "(order_id, customer_id, status, amount_cents, region, version, updated_at, payload, authority_epoch) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                            f"ON DUPLICATE KEY UPDATE {business_updates}",
                            (order_id, customer_id, status, amount_cents, region, version, updated_at,
                             f"replicated-{event_origin_dc}-{origin_event_id}", authority_epoch),
                        )
                    cursor.execute(
                        f"UPDATE {self.changefeed_table} SET last_applied_event_id=%s, resolved_event_id=%s, "
                        "lag_events=GREATEST(%s-%s, 0), updated_at=CURRENT_TIMESTAMP(6) WHERE feed_id=%s",
                        (applied, resolved, resolved, applied, feed_id),
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _refresh_state(self) -> None:
        connection = self._connect(self.control_db, autocommit=False)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT active_dc, route_epoch FROM {self.route_table} WHERE service_name=%s",
                    (self.route_service,),
                )
                route = cursor.fetchone()
                if route is None:
                    raise RuntimeError(f"BC02 route row disappeared: service={self.route_service!r}")
                active_dc, route_epoch = route
                if active_dc not in {self.source_dc, self.target_dc}:
                    raise RuntimeError(
                        f"BC02 route contains unknown data center during refresh: "
                        f"service={self.route_service!r}, active_dc={active_dc!r}"
                    )
                cursor.execute(
                    f"SELECT state, enabled, lag_events FROM {self.changefeed_table} WHERE feed_id=%s",
                    (self.forward_feed_id,),
                )
                forward_state, forward_enabled, forward_lag = cursor.fetchone()
                cursor.execute(
                    f"SELECT state, enabled, lag_events FROM {self.changefeed_table} WHERE feed_id=%s",
                    (self.reverse_feed_id,),
                )
                reverse_state, reverse_enabled, reverse_lag = cursor.fetchone()
                cursor.execute(
                    f"SELECT COUNT(*) FROM {self.target_db}.{self.event_table} "
                    "WHERE origin_dc=%s AND event_source='application'",
                    (self.target_dc,),
                )
                target_app_events = int(cursor.fetchone()[0])
                cursor.execute(
                    f"SELECT COUNT(*) FROM {self.target_db}.{self.event_table} s "
                    "WHERE s.origin_dc=%s AND s.event_source='application' AND EXISTS ("
                    f"SELECT 1 FROM {self.source_db}.{self.event_table} d "
                    "WHERE d.event_source='replication' AND "
                    + " AND ".join(f"d.{column}=s.{column}" for column in (
                        "source_incarnation", "origin_dc", "origin_event_id", "order_id", "customer_id",
                        "status", "amount_cents", "region", "version", "updated_at", "event_ts",
                    )) + ")",
                    (self.target_dc,),
                )
                reverse_applied_events = int(cursor.fetchone()[0])
                p95_latency = self._p95_latency(cursor)
                cursor.execute(
                    f"SELECT COUNT(*) FROM {self.source_db}.{self.order_table}"
                )
                source_order_count = int(cursor.fetchone()[0])
                cursor.execute(
                    f"SELECT COUNT(*) FROM {self.target_db}.{self.order_table}"
                )
                target_order_count = int(cursor.fetchone()[0])
                reverse_ready = (
                    int(forward_lag) == 0
                    and reverse_state == "normal"
                    and int(reverse_enabled) == 1
                )
                if reverse_ready:
                    cursor.execute(
                        f"UPDATE {self.migration_table} SET reverse_ready_observed_at="
                        "COALESCE(reverse_ready_observed_at, CURRENT_TIMESTAMP(6)), updated_at=CURRENT_TIMESTAMP(6) "
                        "WHERE migration_id=%s",
                        (self.migration_id,),
                    )
                if active_dc == self.target_dc and self._last_route != self.target_dc:
                    if int(forward_lag) != 0 or not reverse_ready:
                        cursor.execute(
                            f"UPDATE {self.migration_table} SET unsafe_cutover_attempt=1, updated_at=CURRENT_TIMESTAMP(6) "
                            "WHERE migration_id=%s",
                            (self.migration_id,),
                        )
                    cursor.execute(
                        f"UPDATE {self.migration_table} SET cutover_observed_at="
                        "COALESCE(cutover_observed_at, CURRENT_TIMESTAMP(6)), cutover_event_id=%s, "
                        "updated_at=CURRENT_TIMESTAMP(6) WHERE migration_id=%s",
                        (target_app_events, self.migration_id),
                    )
                    cursor.execute(
                        f"INSERT INTO migration_audit "
                        "(event_type, previous_dc, current_dc, forward_lag_events, reverse_state, observed_at) "
                        "VALUES ('route_cutover', %s, %s, %s, %s, CURRENT_TIMESTAMP(6))",
                        (self._last_route, active_dc, forward_lag, reverse_state),
                    )
                self._last_route = active_dc
                cursor.execute(
                    f"SELECT reverse_ready_observed_at, cutover_observed_at, unsafe_cutover_attempt "
                    f"FROM {self.migration_table} WHERE migration_id=%s",
                    (self.migration_id,),
                )
                reverse_observed, cutover_observed, unsafe = cursor.fetchone()
                if active_dc == self.source_dc:
                    phase = "catchup" if int(forward_lag) else "reverse_required"
                elif int(unsafe):
                    phase = "unsafe_cutover"
                elif cutover_observed is None:
                    phase = "cutover_observed" if reverse_observed is not None else "reverse_required"
                elif (
                    int(reverse_lag) == 0
                    and target_app_events >= 1
                    and reverse_applied_events >= 1
                ):
                    phase = "rollback_ready"
                else:
                    phase = "observation"
                rollback_ready = int(
                    phase == "rollback_ready"
                    and int(unsafe) == 0
                    and active_dc == self.target_dc
                )
                cursor.execute(
                    f"UPDATE {self.migration_table} SET phase=%s, current_primary=%s, rollback_ready=%s, "
                    "target_app_events=%s, reverse_applied_events=%s, p95_latency_ms=%s, updated_at=CURRENT_TIMESTAMP(6) "
                    "WHERE migration_id=%s",
                    (phase, active_dc, rollback_ready, target_app_events, reverse_applied_events, p95_latency, self.migration_id),
                )
                cursor.execute(
                    "INSERT INTO replication_observations "
                    "(observed_at, route_dc, forward_lag_events, reverse_lag_events, p95_latency_ms, "
                    "target_app_events, reverse_applied_events, source_order_count, target_order_count) "
                    "VALUES (CURRENT_TIMESTAMP(6), %s, %s, %s, %s, %s, %s, %s, %s)",
                    (active_dc, forward_lag, reverse_lag, p95_latency, target_app_events, reverse_applied_events, source_order_count, target_order_count),
                )
                cursor.execute(
                    "INSERT INTO service_slo_samples "
                    "(observed_at, route_dc, p95_latency_ms, error_rate) "
                    "VALUES (CURRENT_TIMESTAMP(6), %s, %s, 0)",
                    (active_dc, p95_latency),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _p95_latency(self, cursor) -> float:
        cursor.execute(
            f"SELECT requested_at, processed_at FROM {self.intent_table} "
            "WHERE status='processed' AND processed_at IS NOT NULL "
            "ORDER BY processed_at DESC LIMIT 100"
        )
        latencies = [
            max(0.0, (processed_at - requested_at).total_seconds() * 1000.0)
            for requested_at, processed_at in cursor.fetchall()
        ]
        if not latencies:
            return 0.0
        latencies.sort()
        index = min(len(latencies) - 1, max(0, int(len(latencies) * 0.95) - 1))
        return round(latencies[index], 3)
