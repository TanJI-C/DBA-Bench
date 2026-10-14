from dataclasses import dataclass

from src.scenarios.evaluation.tidb.business_change.large_table_batch_dml import (
    TidbBusinessChangeLargeTableBatchDmlEvaluatorCase,
    TidbBusinessChangeLargeTableSettlementRebucketEvaluatorCase,
)
from src.protocols.report import structured_reference_report
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


_SOURCE_DB = "bc04_app"
_CONTROL_DB = "bc04_change_control"
_TABLE = "order_events"
_STAGE_TABLE = "order_event_change_stage"
_CHECKPOINT_TABLE = "change_checkpoints"
_JOB_TABLE = "change_jobs"
_CONTRACT_TABLE = "change_contract"
_AUDIT_TABLE = "change_batch_audit"
_GATE_TABLE = "change_wave_gate"
_DECOY_TABLES = (
    "order_events_archive",
    "order_events_replay_shadow",
    "order_events_export_preview",
    "order_events_future_release",
)
_JOB_ID = "bc04-order-risk-backfill"
_CONTRACT_ID = "bc04-approved-change"


def _business_workload(
    *,
    source_db: str = _SOURCE_DB,
    control_db: str = _CONTROL_DB,
    table: str = _TABLE,
    stage_table: str = _STAGE_TABLE,
    job_table: str = _JOB_TABLE,
    decoy_tables: tuple[str, ...] = _DECOY_TABLES,
    future_release_id: str = "risk_rebucket_2026q4",
) -> tuple[WorkloadProfile, ...]:
    return (
        WorkloadProfile(
            name="bc04_checkout_recent_order_lookup",
            sql=(
                f"SELECT event_id, tenant_id, status, amount_cents, risk_bucket "
                f"FROM {source_db}.{table} "
                "WHERE tenant_id = 17 ORDER BY event_time DESC, event_id DESC LIMIT 32"
            ),
            qps=0.85,
            tier="FRONTEND_SLO",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="bc04_risk_queue_by_bucket",
            sql=(
                f"SELECT event_id, tenant_id, amount_cents FROM {source_db}.{table} "
                "WHERE risk_bucket = 'high' ORDER BY event_time DESC, event_id DESC LIMIT 48"
            ),
            qps=0.5,
            tier="FRONTEND_SLO",
            application_name="risk-review-queue",
        ),
        WorkloadProfile(
            name="bc04_payment_status_rollup",
            sql=(
                f"SELECT status, COUNT(*), SUM(amount_cents) FROM {source_db}.{table} "
                "GROUP BY status ORDER BY status"
            ),
            qps=0.22,
            tier="FRONTEND_SLO",
            application_name="payment-reconciliation",
        ),
        WorkloadProfile(
            name="bc04_tenant_revenue_dashboard",
            sql=(
                f"SELECT tenant_id, COUNT(*), SUM(amount_cents) FROM {source_db}.{table} "
                "GROUP BY tenant_id ORDER BY SUM(amount_cents) DESC LIMIT 24"
            ),
            qps=0.2,
            tier="FRONTEND_SLO",
            application_name="tenant-dashboard",
        ),
        WorkloadProfile(
            name="bc04_business_checksum_probe",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(amount_cents), 0), "
                f"BIT_XOR(CRC32(CONCAT_WS('|', event_id, tenant_id, status, amount_cents, "
                f"event_time, payload, version, COALESCE(risk_bucket, '')))) "
                f"FROM {source_db}.{table}"
            ),
            qps=0.12,
            tier="BUSINESS_AUDIT",
            application_name="business-integrity-audit",
        ),
        WorkloadProfile(
            name="bc04_stage_release_preview",
            sql=(
                f"SELECT release_id, scope_state, COUNT(*), MIN(event_id), MAX(event_id) "
                f"FROM {control_db}.{stage_table} "
                "GROUP BY release_id, scope_state ORDER BY release_id, scope_state"
            ),
            qps=0.3,
            tier="CHANGE_NOISE",
            application_name="release-console",
        ),
        WorkloadProfile(
            name="bc04_change_job_history_decoy",
            sql=(
                f"SELECT job_id, status, last_event_id, processed_rows "
                f"FROM {control_db}.{job_table} ORDER BY updated_at DESC"
            ),
            qps=0.35,
            tier="CHANGE_NOISE",
            application_name="change-operator-console",
        ),
        WorkloadProfile(
            name="bc04_archive_reconciliation_decoy",
            sql=(
                f"SELECT COUNT(*), SUM(amount_cents) FROM {source_db}.{decoy_tables[0]} "
                "WHERE event_time >= CURRENT_TIMESTAMP - INTERVAL 7 DAY"
            ),
            qps=0.28,
            tier="SAME_DOMAIN_NOISE",
            application_name="archive-reconciliation",
        ),
        WorkloadProfile(
            name="bc04_replay_shadow_decoy",
            sql=(
                f"SELECT replay_state, COUNT(*) FROM {source_db}.{decoy_tables[1]} "
                "GROUP BY replay_state ORDER BY replay_state"
            ),
            qps=0.26,
            tier="SAME_DOMAIN_NOISE",
            application_name="event-replay-audit",
        ),
        WorkloadProfile(
            name="bc04_export_preview_decoy",
            sql=(
                f"SELECT export_batch, COUNT(*), MAX(created_at) FROM {source_db}.{decoy_tables[2]} "
                "GROUP BY export_batch ORDER BY export_batch DESC"
            ),
            qps=0.24,
            tier="SAME_DOMAIN_NOISE",
            application_name="order-export",
        ),
        WorkloadProfile(
            name="bc04_future_release_decoy",
            sql=(
                f"SELECT COUNT(*), MIN(event_id), MAX(event_id) FROM {source_db}.{decoy_tables[3]} "
                f"WHERE release_id = '{future_release_id}'"
            ),
            qps=0.3,
            tier="CHANGE_NOISE",
            application_name="future-release-planner",
        ),
        WorkloadProfile(
            name="bc04_schema_inventory_noise",
            sql=(
                "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES "
                f"WHERE TABLE_SCHEMA IN ('{source_db}', '{control_db}') "
                "ORDER BY TABLE_SCHEMA, TABLE_NAME"
            ),
            qps=0.28,
            tier="METADATA_NOISE",
            application_name="schema-inventory",
        ),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeLargeTableBatchDmlCase(TiDBScenarioCase):
    source_db: str
    control_db: str
    table: str
    stage_table: str
    checkpoint_table: str
    job_table: str
    contract_table: str
    audit_table: str
    gate_table: str
    decoy_tables: tuple[str, ...]
    pk_column: str
    target_column: str
    release_id: str
    required_scope: str
    canary_wave_id: int
    bulk_wave_id: int
    canary_row_count: int
    bulk_row_count: int
    bulk_review_row_count: int
    competing_release_id: str
    future_release_id: str
    protected_same_release_row_count: int
    allowed_index_name: str
    allowed_index_columns: tuple[str, ...]
    feedback_view: str
    source_row_count: int
    approved_row_count: int
    competing_row_count: int
    future_row_count: int
    estimated_row_count: int
    initial_batch_rows: int
    continuation_batch_rows: int
    max_batch_seconds: float
    frontend_slo_p95_ms: float
    max_change_lag_seconds: float
    reference_path: tuple[str, ...]
    reference_tool_counts: tuple[tuple[str, int, int], ...]
    job_id: str = _JOB_ID
    contract_id: str = _CONTRACT_ID


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeLargeTableBatchDmlForLargeTableBatchUpdateAndIndexScenarioCase(
    TidbBusinessChangeLargeTableBatchDmlCase
):
    pass


_CASE = TidbBusinessChangeLargeTableBatchDmlForLargeTableBatchUpdateAndIndexScenarioCase(
    case_id="large_table_batch_update_and_index",
    reference_report=structured_reference_report(
        case_id="large_table_batch_update_and_index",
        factors=(),
        changes=(
            "processed only the approved release stage with primary-key cursor batches and persistent checkpoints",
            "selected only the public apply cohort and preserved the same-release hold cohort",
            "read the committed change feedback after the first batch and reduced continuation batches to the returned allowance",
            "paused at the public mid-bulk review boundary, recorded the second proceed gate, and resumed only after the remaining-scope check",
            "added the approved online covering index without mutating stage, contract, or same-domain decoys",
        ),
        verification=(
            "verified approved-row checksum, protected-scope checksum, batch audit, checkpoint, and query plan",
            "verified frontend p95 SLO, immutable contract, adaptive batch feedback, canary gate, future release exclusion, and rollback boundary",
        ),
        summary="The reference path completed the bounded DML/index change and verified business invariants.",
    ),
    case_no=0,
    evaluator=TidbBusinessChangeLargeTableBatchDmlEvaluatorCase,
    title="Apply an approved large-table change in bounded batches while preserving foreground SLO.",
    alert=(
        "[CHANGE WINDOW] A live order_events table is estimated at 100 million rows. "
        "A signed business change must backfill risk_bucket/version and add one approved covering index "
        "while checkout, payment, risk, archive, export, and release-console traffic continues. "
        "Inspect the change-control records and the live workload before acting. Keep the operation "
        "bounded and auditable, re-read the public change-control feedback after the first recorded batch and "
        "whenever it reports a review boundary because the permitted continuation batch size or authorization "
        "phase may change, preserve the requested scope, and leave "
        "foreground SLO within its budget. "
        "For the canary proceed decision, record the foreground p95 from the canary batch audit; "
        "cluster query_latency is health context and is not an equivalent gate measurement. "
        "Only rows whose public change-control scope_state is apply are approved; same-release hold rows are protected. "
        "Do not run an unbounded UPDATE/DELETE, mutate immutable change-control metadata or same-domain "
        "decoys, change global settings, or restart TiDB."
    ),
    initial_state={
        "status": "change_requested",
        "estimated_table_rows": 100_000_000,
        "business_goal": "complete the signed risk_bucket/version change and approved covering index",
        "online_workload": "foreground_slo_active",
        "guardrails": "bounded scope, auditable progress, immutable change-control records",
        "adaptive_batch_policy": "follow public change-control feedback after the first audit row and every public review boundary",
        "mid_bulk_review": "pause after the public first-bulk-segment boundary and obtain a second proceed decision",
        "protected_same_release_scope": "only public scope_state=apply rows may change; hold rows remain unchanged",
    },
    expected_target={
        "status": "business change complete",
        "requested_scope_only": True,
        "required_scope": "apply",
        "business_truth": "matches signed change contract",
        "progress": "approved rows complete and auditable",
        "adaptive_batch_audit": "each continuation batch stays within the returned allowance",
        "canary_gate": "canary truth is verified before the bulk wave is authorized",
        "mid_bulk_review_gate": "the remaining bulk segment is authorized only after the public review boundary",
        "approved_index": "present",
        "frontend_slo": "within_budget",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_business_workload(),
        worker_count=6,
        seed=0xBC04,
        warmup_seconds=8,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=9,
        environmental_complexity=0.0,
        reference_run_ids=(
            "reference-82__"
            "tidb_business_change_large_table_batch_dml__large_table_batch_update_and_index__"
            "mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=300,
    ),
    source_db=_SOURCE_DB,
    control_db=_CONTROL_DB,
    table=_TABLE,
    stage_table=_STAGE_TABLE,
    checkpoint_table=_CHECKPOINT_TABLE,
    job_table=_JOB_TABLE,
    contract_table=_CONTRACT_TABLE,
    audit_table=_AUDIT_TABLE,
    gate_table=_GATE_TABLE,
    decoy_tables=_DECOY_TABLES,
    pk_column="event_id",
    target_column="risk_bucket",
    release_id="risk_rebucket_2026q3",
    required_scope="apply",
    canary_wave_id=1,
    bulk_wave_id=2,
    canary_row_count=2_000,
    bulk_row_count=16_000,
    bulk_review_row_count=8_000,
    competing_release_id="risk_rebucket_2026q2",
    future_release_id="risk_rebucket_2026q4",
    protected_same_release_row_count=6_000,
    allowed_index_name="idx_order_events_tenant_risk_event",
    allowed_index_columns=("tenant_id", "risk_bucket", "event_time", "event_id"),
    feedback_view="change_execution_feedback",
    source_row_count=40_000,
    approved_row_count=18_000,
    competing_row_count=6_000,
    future_row_count=6_000,
    estimated_row_count=100_000_000,
    initial_batch_rows=1_000,
    continuation_batch_rows=500,
    max_batch_seconds=1.8,
    frontend_slo_p95_ms=2_000.0,
    max_change_lag_seconds=8.0,
    reference_path=(
        "the live business change request is understood",
        "the immutable contract identifies the signed release, canary wave, bulk wave, and gate truth",
        "the multi-row stage result is correlated with the contract and q3 apply is separated into canary, bulk, hold, and q2",
        "the selected stage scope and wave define the target and protected remainder",
        "the foreground workload establishes the change budget",
        "the bounded canary wave creates committed wave audit state",
        "the public feedback gate is verified and a proceed decision is recorded before the bulk wave",
        "the first bulk segment reaches the public review boundary and the feedback requires a second proceed decision",
        "the second gate is recorded before the final bulk segment and the safe continuation follows the public budget",
        "the final business truth, gate ordering, index, SLO, and recovery state are verified",
    ),
    reference_tool_counts=(
        ("execute_sql", 24, 0),
        ("query_metrics", 90, 0),
    ),
)


_SETTLEMENT_CASE = TidbBusinessChangeLargeTableBatchDmlForLargeTableBatchUpdateAndIndexScenarioCase(
    case_id="large_table_settlement_rebucket",
    reference_report=structured_reference_report(
        case_id="large_table_settlement_rebucket",
        factors=(
            "the settlement table has an approved rebucket contract with one public canary and one bulk review boundary",
            "same-release holds and a future release share the source table and must remain untouched",
        ),
        changes=(
            "applied the settlement risk rebucket with feedback-sized batches",
            "recorded both proceed gates before the final online covering index",
        ),
        verification=(
            "approved and protected checksums, checkpoint, gates, index, and foreground SLO passed",
            "the billing settlement release remained isolated from future and replay cohorts",
        ),
        summary="The settlement rebucket reference path completed the signed large-table change safely.",
    ),
    case_no=1,
    evaluator=TidbBusinessChangeLargeTableSettlementRebucketEvaluatorCase,
    title="Apply the settlement risk rebucket with canary and review gates.",
    alert=(
        "[CHANGE WINDOW] settlement_events 的已签名 risk rebucket 需要在前台结算和账单查询持续运行时完成。"
        "请先读取 immutable contract、公开 stage、canary/bulk gate 和反馈视图；仅处理 scope_state=apply 的 settlement cohort，"
        "首批与每个公开 review boundary 后重新读取允许批大小，记录真实 SLO gate，再建立批准的 online covering index。"
        "不得修改 hold/future/replay cohort、不可变控制面、全局设置或重启 TiDB。"
    ),
    initial_state={
        "status": "change_requested",
        "estimated_table_rows": 60_000_000,
        "business_goal": "complete the signed settlement risk_bucket/version change",
        "online_workload": "settlement_frontend_slo_active",
        "protected_scope": "same-release hold and future release rows",
    },
    expected_target={
        "status": "business change complete",
        "requested_scope_only": True,
        "business_truth": "matches signed contract",
        "progress": "approved rows complete and auditable",
        "canary_gate": "verified",
        "mid_bulk_review_gate": "verified",
        "approved_index": "present",
        "frontend_slo": "within_budget",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_business_workload(
            source_db="bc04_settlement",
            control_db="bc04_settlement_control",
            table="settlement_events",
            stage_table="settlement_change_stage",
            job_table="settlement_change_jobs",
            decoy_tables=(
                "settlement_events_archive",
                "settlement_events_replay",
                "settlement_events_export",
                "settlement_events_future",
            ),
            future_release_id="settlement_rebucket_2026q4",
        ),
        worker_count=4, seed=0xBC0413, warmup_seconds=8,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.0,
        reference_run_ids=(
            "tidb-reference-12__"
            "tidb_business_change_large_table_batch_dml__large_table_settlement_rebucket__"
            "mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0, pd_count=3, tikv_count=3, tidb_count=2,
        sql_timeout_seconds=300,
    ),
    source_db="bc04_settlement",
    control_db="bc04_settlement_control",
    table="settlement_events",
    stage_table="settlement_change_stage",
    checkpoint_table="settlement_checkpoints",
    job_table="settlement_change_jobs",
    contract_table="settlement_change_contract",
    audit_table="settlement_batch_audit",
    gate_table="settlement_wave_gate",
    decoy_tables=(
        "settlement_events_archive", "settlement_events_replay",
        "settlement_events_export", "settlement_events_future",
    ),
    pk_column="event_id",
    target_column="risk_bucket",
    release_id="settlement_rebucket_2026q3",
    required_scope="apply",
    canary_wave_id=1,
    bulk_wave_id=2,
    canary_row_count=1_200,
    bulk_row_count=10_800,
    bulk_review_row_count=5_200,
    competing_release_id="settlement_rebucket_2026q2",
    future_release_id="settlement_rebucket_2026q4",
    protected_same_release_row_count=3_000,
    allowed_index_name="idx_settlement_tenant_risk_event",
    allowed_index_columns=("tenant_id", "risk_bucket", "event_time", "event_id"),
    feedback_view="settlement_change_feedback",
    source_row_count=24_000,
    approved_row_count=12_000,
    competing_row_count=3_000,
    future_row_count=3_000,
    estimated_row_count=60_000_000,
    initial_batch_rows=800,
    continuation_batch_rows=400,
    max_batch_seconds=1.8,
    frontend_slo_p95_ms=1_600.0,
    max_change_lag_seconds=8.0,
    reference_path=(
        "the settlement change request and its immutable contract are identified",
        "stage rows are correlated with the approved release and separated from hold/future cohorts",
        "the foreground workload defines the published batch budget",
        "the canary is applied and its public gate is recorded",
        "the first bulk segment reaches the review boundary and feedback lowers continuation size",
        "the second gate authorizes the remaining segment",
        "final checksum, checkpoint, index and SLO establish completion",
    ),
    reference_tool_counts=(("execute_sql", 24, 0), ("query_metrics", 93, 0)),
    job_id="settlement-risk-rebucket",
    contract_id="settlement-approved-rebucket",
)


class TidbBusinessChangeLargeTableBatchDmlScenario(TiDBScenario):
    scenario_id = "tidb_business_change_large_table_batch_dml"
    description = "Run an approved large-table DML and online index change in bounded batches under foreground SLO."
    cases = (_CASE, _SETTLEMENT_CASE)

    def build_fault_plan(
        self,
        case: TidbBusinessChangeLargeTableBatchDmlCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangeLargeTableBatchDmlInjector,
                config={
                    "source_db": case.source_db,
                    "control_db": case.control_db,
                    "table": case.table,
                    "stage_table": case.stage_table,
                    "checkpoint_table": case.checkpoint_table,
                    "job_table": case.job_table,
                    "contract_table": case.contract_table,
                    "audit_table": case.audit_table,
                    "gate_table": case.gate_table,
                    "decoy_tables": case.decoy_tables,
                    "pk_column": case.pk_column,
                    "target_column": case.target_column,
                    "release_id": case.release_id,
                    "required_scope": case.required_scope,
                    "canary_wave_id": case.canary_wave_id,
                    "bulk_wave_id": case.bulk_wave_id,
                    "canary_row_count": case.canary_row_count,
                    "bulk_row_count": case.bulk_row_count,
                    "bulk_review_row_count": case.bulk_review_row_count,
                    "competing_release_id": case.competing_release_id,
                    "future_release_id": case.future_release_id,
                    "protected_same_release_row_count": case.protected_same_release_row_count,
                    "allowed_index_name": case.allowed_index_name,
                    "allowed_index_columns": case.allowed_index_columns,
                    "feedback_view": case.feedback_view,
                    "source_row_count": case.source_row_count,
                    "approved_row_count": case.approved_row_count,
                    "competing_row_count": case.competing_row_count,
                    "future_row_count": case.future_row_count,
                    "estimated_row_count": case.estimated_row_count,
                    "initial_batch_rows": case.initial_batch_rows,
                    "continuation_batch_rows": case.continuation_batch_rows,
                    "max_batch_seconds": case.max_batch_seconds,
                    "frontend_slo_p95_ms": case.frontend_slo_p95_ms,
                    "max_change_lag_seconds": case.max_change_lag_seconds,
                    "job_id": case.job_id,
                    "contract_id": case.contract_id,
                },
            ),
        )


__all__ = (
    "TidbBusinessChangeLargeTableBatchDmlCase",
    "TidbBusinessChangeLargeTableBatchDmlForLargeTableBatchUpdateAndIndexScenarioCase",
    "TidbBusinessChangeLargeTableBatchDmlScenario",
)

from datetime import datetime, timedelta
from collections.abc import Mapping
import re

import pymysql

from src.database.sql import execute_result_rows, require_success_payload
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.tidb.common import validate_sql_identifier


_TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]+$")
class TidbBusinessChangeLargeTableBatchDmlInjector(BaseFaultInjector):
    """Install the live data and immutable change-control surface for BC04."""

    job_id = "bc04-order-risk-backfill"
    contract_id = "bc04-approved-change"

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._create_databases()
        self._create_tables()
        self._seed_source_rows()
        self._seed_release_stage_and_truth()
        self._verify_persistent_state()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_persistent_state()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config, context.env)
        self._verify_persistent_state()
        return {
            "bc04_change_contract": self._rows(
                f"SELECT contract_id, release_id, required_scope, expected_rows, expected_sum_cents, expected_crc, "
                f"out_of_scope_rows, out_of_scope_crc, first_event_id, last_event_id, index_columns, "
                f"max_batch_seconds, frontend_slo_p95_ms, immutable_marker, initial_batch_rows, "
                f"continuation_batch_rows, feedback_view, canary_wave_id, canary_expected_rows, "
                f"canary_expected_crc, bulk_wave_id, bulk_expected_rows, bulk_baseline_crc, gate_table "
                f", bulk_review_rows, bulk_review_last_event_id, bulk_review_expected_crc, bulk_review_remaining_crc "
                f"FROM {self.control_db}.{self.contract_table} WHERE contract_id='{self.contract_id}'",
                "capture BC04 immutable change contract",
            ),
            "bc04_change_feedback": self._rows(
                f"SELECT job_id, release_id, completed_batches, last_event_id, processed_rows, "
                f"max_next_rows, feedback_phase, phase_id, next_wave_id, gate_required, gate_state, "
                f"canary_rows, bulk_rows, bulk_review_gate_state FROM {self.control_db}.{self.feedback_view} "
                f"WHERE job_id='{self.job_id}'",
                "capture BC04 adaptive change feedback",
            ),
            "bc04_release_stage": self._rows(
                f"SELECT release_id, scope_state, wave_id, COUNT(*), MIN(event_id), MAX(event_id) "
                f"FROM {self.control_db}.{self.stage_table} "
                f"GROUP BY release_id, scope_state, wave_id ORDER BY release_id, scope_state, wave_id",
                "capture BC04 release-stage bounds",
            ),
            "bc04_existing_indexes": self._rows(
                "SELECT INDEX_NAME, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) "
                f"FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA='{self.source_db}' "
                f"AND TABLE_NAME='{self.table}' GROUP BY INDEX_NAME",
                "capture BC04 existing indexes",
            ),
            "bc04_change_job": self._rows(
                f"SELECT job_id, release_id, status, last_event_id, processed_rows, batch_size, "
                f"index_name, index_state FROM {self.control_db}.{self.job_table} WHERE job_id='{self.job_id}'",
                "capture BC04 change job",
            ),
            "bc04_wave_gate": self._rows(
                f"SELECT gate_id, job_id, wave_id, verified_rows, verified_crc, remaining_apply_rows, "
                f"remaining_apply_crc, frontend_p95_ms, decision_code FROM {self.control_db}.{self.gate_table} "
                f"WHERE job_id='{self.job_id}' ORDER BY gate_id",
                "capture BC04 canary gate ledger",
            ),
            "bc04_source_truth": self._rows(
                f"SELECT COUNT(*), COALESCE(SUM(amount_cents), 0), "
                f"COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', event_id, tenant_id, status, amount_cents, "
                f"event_time, payload, version, COALESCE(risk_bucket, '')))), 0) "
                f"FROM {self.source_db}.{self.table}",
                "capture BC04 source truth",
            ),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._sql(f"DROP DATABASE IF EXISTS {self.control_db}", "drop BC04 control database")
        self._sql(f"DROP DATABASE IF EXISTS {self.source_db}", "drop BC04 source database")
        self._databases_created = False
        self._configured = False

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.source_db = validate_sql_identifier(str(config["source_db"]), "source_db")
        self.control_db = validate_sql_identifier(str(config["control_db"]), "control_db")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.stage_table = validate_sql_identifier(str(config["stage_table"]), "stage_table")
        self.checkpoint_table = validate_sql_identifier(str(config["checkpoint_table"]), "checkpoint_table")
        self.job_table = validate_sql_identifier(str(config["job_table"]), "job_table")
        self.contract_table = validate_sql_identifier(str(config["contract_table"]), "contract_table")
        self.audit_table = validate_sql_identifier(str(config["audit_table"]), "audit_table")
        self.gate_table = validate_sql_identifier(str(config["gate_table"]), "gate_table")
        self.decoy_tables = tuple(
            validate_sql_identifier(str(value), "decoy_table")
            for value in config["decoy_tables"]
        )
        self.pk_column = validate_sql_identifier(str(config["pk_column"]), "pk_column")
        self.target_column = validate_sql_identifier(str(config["target_column"]), "target_column")
        self.job_id = self._token(str(config["job_id"]), "job_id")
        self.contract_id = self._token(str(config["contract_id"]), "contract_id")
        self.release_id = self._token(str(config["release_id"]), "release_id")
        self.required_scope = self._token(str(config["required_scope"]), "required_scope")
        self.canary_wave_id = int(config["canary_wave_id"])
        self.bulk_wave_id = int(config["bulk_wave_id"])
        self.canary_row_count = int(config["canary_row_count"])
        self.bulk_row_count = int(config["bulk_row_count"])
        self.bulk_review_row_count = int(config["bulk_review_row_count"])
        self.bulk_review_last_event_id = (
            self.canary_row_count + self.bulk_review_row_count
        ) * 2
        self.competing_release_id = self._token(str(config["competing_release_id"]), "competing_release_id")
        self.future_release_id = self._token(str(config["future_release_id"]), "future_release_id")
        self.allowed_index_name = validate_sql_identifier(
            str(config["allowed_index_name"]), "allowed_index_name"
        )
        self.allowed_index_columns = tuple(str(value) for value in config["allowed_index_columns"])
        self.feedback_view = validate_sql_identifier(str(config["feedback_view"]), "feedback_view")
        self.source_row_count = int(config["source_row_count"])
        self.approved_row_count = int(config["approved_row_count"])
        self.competing_row_count = int(config["competing_row_count"])
        self.protected_same_release_row_count = int(config["protected_same_release_row_count"])
        self.future_row_count = int(config["future_row_count"])
        self.estimated_row_count = int(config["estimated_row_count"])
        self.initial_batch_rows = int(config["initial_batch_rows"])
        self.continuation_batch_rows = int(config["continuation_batch_rows"])
        self.max_batch_seconds = float(config["max_batch_seconds"])
        self.frontend_slo_p95_ms = float(config["frontend_slo_p95_ms"])
        self.max_change_lag_seconds = float(config["max_change_lag_seconds"])
        self._configured = True
        self._databases_created = getattr(self, "_databases_created", False)
        self._validate_configuration()

    @staticmethod
    def _token(value: str, name: str) -> str:
        if not _TOKEN_RE.fullmatch(value):
            raise ValueError(f"BC04 {name} must be an ASCII token: value={value!r}")
        return value

    def _validate_configuration(self) -> None:
        values = {
            "source_row_count": self.source_row_count,
            "approved_row_count": self.approved_row_count,
            "competing_row_count": self.competing_row_count,
            "protected_same_release_row_count": self.protected_same_release_row_count,
            "future_row_count": self.future_row_count,
            "estimated_row_count": self.estimated_row_count,
            "initial_batch_rows": self.initial_batch_rows,
            "continuation_batch_rows": self.continuation_batch_rows,
            "canary_wave_id": self.canary_wave_id,
            "bulk_wave_id": self.bulk_wave_id,
            "canary_row_count": self.canary_row_count,
            "bulk_row_count": self.bulk_row_count,
            "bulk_review_row_count": self.bulk_review_row_count,
        }
        invalid = {name: value for name, value in values.items() if value <= 0}
        if invalid:
            raise ValueError(f"BC04 positive configuration values required: {invalid}")
        if self.approved_row_count >= self.source_row_count:
            raise ValueError(
                "BC04 approved release must be a strict subset: "
                f"approved={self.approved_row_count}, source={self.source_row_count}"
            )
        if self.continuation_batch_rows > self.initial_batch_rows:
            raise ValueError(
                "BC04 continuation batch allowance must not exceed the initial allowance: "
                f"initial={self.initial_batch_rows}, continuation={self.continuation_batch_rows}"
            )
        if self.canary_wave_id == self.bulk_wave_id:
            raise ValueError(
                f"BC04 canary and bulk wave IDs must differ: canary={self.canary_wave_id}, bulk={self.bulk_wave_id}"
            )
        if self.canary_row_count + self.bulk_row_count != self.approved_row_count:
            raise ValueError(
                "BC04 canary and bulk rows must cover the approved cohort: "
                f"canary={self.canary_row_count}, bulk={self.bulk_row_count}, approved={self.approved_row_count}"
            )
        if not 0 < self.bulk_review_row_count < self.bulk_row_count:
            raise ValueError(
                "BC04 mid-bulk review must split the bulk cohort into two non-empty segments: "
                f"review={self.bulk_review_row_count}, bulk={self.bulk_row_count}"
            )
        if self.competing_release_id in {self.release_id, self.future_release_id}:
            raise ValueError(
                "BC04 competing release must be distinct from approved and future releases: "
                f"competing={self.competing_release_id!r}, approved={self.release_id!r}, future={self.future_release_id!r}"
            )
        stage_tail = (
            self.protected_same_release_row_count + self.competing_row_count
        ) * 2
        if stage_tail > self.source_row_count:
            raise ValueError(
                "BC04 protected and competing stage bounds must fit inside source table: "
                f"protected={self.protected_same_release_row_count}, competing={self.competing_row_count}, "
                f"stage_tail={stage_tail}, source={self.source_row_count}"
            )
        if self.future_row_count >= self.source_row_count:
            raise ValueError(
                "BC04 future release must fit inside source table: "
                f"future={self.future_row_count}, source={self.source_row_count}"
            )
        if not self.allowed_index_columns:
            raise ValueError("BC04 approved index must contain at least one column")
        if self.max_batch_seconds <= 0 or self.frontend_slo_p95_ms <= 0 or self.max_change_lag_seconds <= 0:
            raise ValueError(
                "BC04 change thresholds must be positive: "
                f"max_batch_seconds={self.max_batch_seconds}, "
                f"frontend_slo_p95_ms={self.frontend_slo_p95_ms}, "
                f"max_change_lag_seconds={self.max_change_lag_seconds}"
            )
        if len(self.decoy_tables) != 4:
            raise ValueError(f"BC04 requires four same-domain decoy tables: decoy_tables={self.decoy_tables!r}")

    def _sql(self, sql: str, context: str) -> dict:
        return require_success_payload(self.env.execute_sql(sql), f"{context}: sql={sql!r}")

    def _rows(self, sql: str, context: str) -> list:
        return execute_result_rows(self.env.execute_sql, sql, context)

    def _connect(self, database: str | None = None):
        return pymysql.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            database=database,
            charset="utf8mb4",
            autocommit=False,
            connect_timeout=5,
            read_timeout=120,
            write_timeout=120,
        )

    def _create_databases(self) -> None:
        self._sql(f"DROP DATABASE IF EXISTS {self.control_db}", "clear BC04 control database")
        self._sql(f"DROP DATABASE IF EXISTS {self.source_db}", "clear BC04 source database")
        self._sql(f"CREATE DATABASE {self.source_db}", "create BC04 source database")
        self._sql(f"CREATE DATABASE {self.control_db}", "create BC04 control database")
        self._databases_created = True

    def _create_tables(self) -> None:
        self._sql(
            f"""
            CREATE TABLE {self.source_db}.{self.table} (
                event_id BIGINT PRIMARY KEY,
                tenant_id INT NOT NULL,
                status VARCHAR(24) NOT NULL,
                amount_cents BIGINT NOT NULL,
                event_time DATETIME(6) NOT NULL,
                payload VARCHAR(128) NOT NULL,
                version INT NOT NULL,
                risk_bucket VARCHAR(16) NULL,
                KEY idx_order_events_tenant_event (tenant_id, event_time, event_id),
                KEY idx_order_events_status_event (status, event_time, event_id)
            )
            """,
            "create BC04 business table",
        )
        for table in self.decoy_tables[:3]:
            self._sql(
                f"""
                CREATE TABLE {self.source_db}.{table} (
                    event_id BIGINT PRIMARY KEY,
                    tenant_id INT NOT NULL,
                    status VARCHAR(24) NOT NULL,
                    amount_cents BIGINT NOT NULL,
                    event_time DATETIME(6) NOT NULL,
                    payload VARCHAR(128) NOT NULL,
                    version INT NOT NULL,
                    risk_bucket VARCHAR(16) NULL,
                    replay_state VARCHAR(24) NOT NULL,
                    export_batch VARCHAR(64) NOT NULL,
                    created_at DATETIME(6) NOT NULL
                )
                """,
                f"create BC04 decoy table {table}",
            )
        self._sql(
            f"""
            CREATE TABLE {self.source_db}.{self.decoy_tables[3]} (
                event_id BIGINT NOT NULL,
                release_id VARCHAR(64) NOT NULL,
                expected_risk_bucket VARCHAR(16) NOT NULL,
                expected_version INT NOT NULL,
                source_reason VARCHAR(128) NOT NULL,
                PRIMARY KEY (release_id, event_id),
                KEY idx_future_event (event_id)
            )
            """,
            "create BC04 future release decoy",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.{self.stage_table} (
                event_id BIGINT NOT NULL,
                release_id VARCHAR(64) NOT NULL,
                scope_state VARCHAR(16) NOT NULL,
                wave_id INT NOT NULL,
                expected_risk_bucket VARCHAR(16) NOT NULL,
                expected_version INT NOT NULL,
                source_reason VARCHAR(128) NOT NULL,
                PRIMARY KEY (release_id, event_id),
                KEY idx_stage_event (event_id)
            )
            """,
            "create BC04 immutable release stage",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.{self.contract_table} (
                contract_id VARCHAR(64) PRIMARY KEY,
                release_id VARCHAR(64) NOT NULL,
                required_scope VARCHAR(16) NOT NULL,
                expected_rows BIGINT NOT NULL,
                expected_sum_cents BIGINT NOT NULL,
                expected_crc BIGINT NOT NULL,
                out_of_scope_rows BIGINT NOT NULL,
                out_of_scope_crc BIGINT NOT NULL,
                first_event_id BIGINT NOT NULL,
                last_event_id BIGINT NOT NULL,
                index_columns VARCHAR(256) NOT NULL,
                max_batch_seconds DECIMAL(10,3) NOT NULL,
                frontend_slo_p95_ms DECIMAL(10,3) NOT NULL,
                immutable_marker VARCHAR(64) NOT NULL,
                initial_batch_rows INT NOT NULL,
                continuation_batch_rows INT NOT NULL,
                feedback_view VARCHAR(128) NOT NULL,
                canary_wave_id INT NOT NULL,
                canary_expected_rows BIGINT NOT NULL,
                canary_expected_crc BIGINT NOT NULL,
                bulk_wave_id INT NOT NULL,
                bulk_expected_rows BIGINT NOT NULL,
                bulk_baseline_crc BIGINT NOT NULL,
                gate_table VARCHAR(128) NOT NULL,
                bulk_review_rows BIGINT NOT NULL,
                bulk_review_last_event_id BIGINT NOT NULL,
                bulk_review_expected_crc BIGINT NOT NULL,
                bulk_review_remaining_crc BIGINT NOT NULL,
                created_at DATETIME(6) NOT NULL
            )
            """,
            "create BC04 immutable change contract",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.{self.job_table} (
                job_id VARCHAR(64) PRIMARY KEY,
                release_id VARCHAR(64) NOT NULL,
                target_table VARCHAR(128) NOT NULL,
                target_column VARCHAR(64) NOT NULL,
                status VARCHAR(24) NOT NULL,
                last_event_id BIGINT NOT NULL,
                processed_rows BIGINT NOT NULL,
                batch_size INT NOT NULL,
                index_name VARCHAR(128) NOT NULL,
                index_state VARCHAR(24) NOT NULL,
                updated_at DATETIME(6) NOT NULL
            )
            """,
            "create BC04 change job",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.{self.checkpoint_table} (
                job_id VARCHAR(64) PRIMARY KEY,
                last_event_id BIGINT NOT NULL,
                processed_rows BIGINT NOT NULL,
                batch_count INT NOT NULL,
                checkpoint_state VARCHAR(24) NOT NULL,
                updated_at DATETIME(6) NOT NULL
            )
            """,
            "create BC04 checkpoint table",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.{self.audit_table} (
                audit_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                job_id VARCHAR(64) NOT NULL,
                wave_id INT NOT NULL DEFAULT 2,
                first_event_id BIGINT NOT NULL,
                last_event_id BIGINT NOT NULL,
                rows_changed INT NOT NULL,
                batch_seconds DECIMAL(10,3) NOT NULL,
                frontend_p95_ms DECIMAL(10,3) NOT NULL,
                action VARCHAR(24) NOT NULL,
                created_at DATETIME(6) NOT NULL
            )
            """,
            "create BC04 batch audit table",
        )
        self._sql(
            f"""
            CREATE TABLE {self.control_db}.{self.gate_table} (
                gate_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                job_id VARCHAR(64) NOT NULL,
                wave_id INT NOT NULL,
                verified_rows BIGINT NOT NULL,
                verified_crc BIGINT NOT NULL,
                remaining_apply_rows BIGINT NOT NULL,
                remaining_apply_crc BIGINT NOT NULL,
                frontend_p95_ms DECIMAL(10,3) NOT NULL,
                decision_code TINYINT NOT NULL,
                created_at DATETIME(6) NOT NULL
            )
            """,
            "create BC04 canary gate ledger",
        )
        self._sql(
            f"""
            CREATE VIEW {self.control_db}.{self.feedback_view} AS
            SELECT j.job_id, j.release_id,
                COUNT(a.audit_id) AS completed_batches,
                COALESCE(MAX(a.last_event_id), 0) AS last_event_id,
                COALESCE(SUM(a.rows_changed), 0) AS processed_rows,
                CASE WHEN COUNT(a.audit_id) = 0
                    THEN c.initial_batch_rows ELSE c.continuation_batch_rows END AS max_next_rows,
                CASE WHEN COUNT(a.audit_id) = 0
                    THEN 'initial' ELSE 'continuation_feedback' END AS feedback_phase,
                CASE
                    WHEN COALESCE(SUM(CASE WHEN a.wave_id=c.canary_wave_id THEN a.rows_changed ELSE 0 END), 0)
                        < c.canary_expected_rows THEN 1
                    WHEN COALESCE(g.canary_gate_state, 0) <> 1 THEN 2
                    WHEN COALESCE(SUM(CASE WHEN a.wave_id=c.bulk_wave_id THEN a.rows_changed ELSE 0 END), 0)
                        < c.bulk_review_rows THEN 3
                    WHEN COALESCE(g.bulk_review_gate_state, 0) <> 1 THEN 4
                    WHEN COALESCE(SUM(CASE WHEN a.wave_id=c.bulk_wave_id THEN a.rows_changed ELSE 0 END), 0)
                        < c.bulk_expected_rows THEN 5
                    ELSE 6
                END AS phase_id,
                CASE
                    WHEN COALESCE(SUM(CASE WHEN a.wave_id=c.canary_wave_id THEN a.rows_changed ELSE 0 END), 0)
                        < c.canary_expected_rows THEN c.canary_wave_id
                    WHEN COALESCE(g.canary_gate_state, 0) <> 1 THEN c.bulk_wave_id
                    WHEN COALESCE(SUM(CASE WHEN a.wave_id=c.bulk_wave_id THEN a.rows_changed ELSE 0 END), 0)
                        < c.bulk_review_rows THEN c.bulk_wave_id
                    WHEN COALESCE(g.bulk_review_gate_state, 0) <> 1 THEN c.bulk_wave_id
                    WHEN COALESCE(SUM(CASE WHEN a.wave_id=c.bulk_wave_id THEN a.rows_changed ELSE 0 END), 0)
                        < c.bulk_expected_rows THEN c.bulk_wave_id
                    ELSE 0
                END AS next_wave_id,
                CASE
                    WHEN COALESCE(SUM(CASE WHEN a.wave_id=c.canary_wave_id THEN a.rows_changed ELSE 0 END), 0)
                        >= c.canary_expected_rows AND COALESCE(g.canary_gate_state, 0) <> 1 THEN 1
                    WHEN COALESCE(SUM(CASE WHEN a.wave_id=c.bulk_wave_id THEN a.rows_changed ELSE 0 END), 0)
                        >= c.bulk_review_rows AND COALESCE(g.bulk_review_gate_state, 0) <> 1 THEN 1
                    ELSE 0
                END AS gate_required,
                COALESCE(g.canary_gate_state, 0) AS gate_state,
                COALESCE(SUM(CASE WHEN a.wave_id=c.canary_wave_id THEN a.rows_changed ELSE 0 END), 0) AS canary_rows,
                COALESCE(SUM(CASE WHEN a.wave_id=c.bulk_wave_id THEN a.rows_changed ELSE 0 END), 0) AS bulk_rows,
                COALESCE(g.bulk_review_gate_state, 0) AS bulk_review_gate_state
            FROM {self.control_db}.{self.job_table} j
            JOIN {self.control_db}.{self.contract_table} c ON c.release_id=j.release_id
            LEFT JOIN {self.control_db}.{self.audit_table} a ON a.job_id=j.job_id
            LEFT JOIN (
                SELECT job_id,
                    MAX(CASE WHEN wave_id=1 THEN decision_code ELSE 0 END) AS canary_gate_state,
                    MAX(CASE WHEN wave_id=2 THEN decision_code ELSE 0 END) AS bulk_review_gate_state
                FROM {self.control_db}.{self.gate_table}
                GROUP BY job_id
            ) g ON g.job_id=j.job_id
            WHERE j.job_id='{self.job_id}'
            GROUP BY j.job_id, j.release_id, c.initial_batch_rows, c.continuation_batch_rows,
                c.canary_wave_id, c.canary_expected_rows, c.bulk_wave_id, c.bulk_expected_rows,
                c.bulk_review_rows, g.canary_gate_state, g.bulk_review_gate_state
            """,
            "create BC04 adaptive change feedback view",
        )
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.job_table} (
                job_id, release_id, target_table, target_column, status, last_event_id,
                processed_rows, batch_size, index_name, index_state, updated_at
            ) VALUES (
                '{self.job_id}', '{self.release_id}', '{self.source_db}.{self.table}',
                '{self.target_column}', 'pending', 0, 0, {self.initial_batch_rows},
                '{self.allowed_index_name}', 'pending', CURRENT_TIMESTAMP(6)
            )
            """,
            "seed BC04 change job",
        )
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.checkpoint_table} (
                job_id, last_event_id, processed_rows, batch_count, checkpoint_state, updated_at
            ) VALUES ('{self.job_id}', 0, 0, 0, 'not_started', CURRENT_TIMESTAMP(6))
            """,
            "seed BC04 checkpoint",
        )

    def _seed_source_rows(self) -> None:
        connection = self._connect(self.source_db)
        try:
            base_time = datetime(2026, 1, 1)
            statuses = ("paid", "packed", "shipped", "review")
            rows = [
                (
                    event_id,
                    1 + (event_id % 64),
                    statuses[event_id % len(statuses)],
                    100 + ((event_id * 37) % 100_000),
                    base_time + timedelta(seconds=event_id),
                    f"order-event-{event_id:08d}",
                    1,
                    None,
                )
                for event_id in range(1, self.source_row_count + 1)
            ]
            with connection.cursor() as cursor:
                cursor.executemany(
                    f"INSERT INTO {self.table} "
                    "(event_id, tenant_id, status, amount_cents, event_time, payload, version, risk_bucket) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    rows,
                )
            connection.commit()
        finally:
            connection.close()
        for index, table in enumerate(self.decoy_tables[:3]):
            replay_state = ("ready", "shadow", "preview")[index]
            export_batch = ("archive-batch-2026q3", "replay-shadow-2026q3", "export-preview-2026q3")[index]
            self._sql(
                f"""
                INSERT INTO {self.source_db}.{table} (
                    event_id, tenant_id, status, amount_cents, event_time, payload, version,
                    risk_bucket, replay_state, export_batch, created_at
                )
                SELECT event_id, tenant_id, status, amount_cents, event_time, payload, version,
                    risk_bucket, '{replay_state}', '{export_batch}', CURRENT_TIMESTAMP(6)
                FROM {self.source_db}.{self.table} WHERE event_id <= 2000
                """,
                f"seed BC04 decoy table {table}",
            )
        future_start = self.source_row_count - self.future_row_count
        self._sql(
            f"""
            INSERT INTO {self.source_db}.{self.decoy_tables[3]} (
                event_id, release_id, expected_risk_bucket, expected_version, source_reason
            )
            SELECT event_id, '{self.future_release_id}',
                CASE
                    WHEN amount_cents >= 90000 THEN 'critical'
                    WHEN amount_cents >= 60000 THEN 'high'
                    WHEN status = 'review' THEN 'review'
                    ELSE 'standard'
                END,
                version + 1, 'future-release-planning'
            FROM {self.source_db}.{self.table}
            WHERE event_id > {future_start} AND event_id <= {self.source_row_count}
            """,
            "seed BC04 future release decoy",
        )

    def _seed_release_stage_and_truth(self) -> None:
        canary_last = self.canary_row_count * 2
        approved_last = self.approved_row_count * 2
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.stage_table} (
                event_id, release_id, scope_state, wave_id, expected_risk_bucket, expected_version, source_reason
            )
            SELECT event_id, '{self.release_id}', 'apply',
                {self.canary_wave_id},
                CASE
                    WHEN amount_cents >= 90000 THEN 'critical'
                    WHEN amount_cents >= 60000 THEN 'high'
                    WHEN status = 'review' THEN 'review'
                    ELSE 'standard'
                END,
                version + 1, 'approved-risk-policy-2026q3'
            FROM {self.source_db}.{self.table}
            WHERE event_id <= {canary_last} AND MOD(event_id, 2) = 0
            """,
            "seed BC04 canary release stage",
        )
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.stage_table} (
                event_id, release_id, scope_state, wave_id, expected_risk_bucket, expected_version, source_reason
            )
            SELECT event_id, '{self.release_id}', 'apply',
                {self.bulk_wave_id},
                CASE
                    WHEN amount_cents >= 90000 THEN 'critical'
                    WHEN amount_cents >= 60000 THEN 'high'
                    WHEN status = 'review' THEN 'review'
                    ELSE 'standard'
                END,
                version + 1, 'approved-risk-policy-2026q3-bulk'
            FROM {self.source_db}.{self.table}
            WHERE event_id > {canary_last} AND event_id <= {approved_last} AND MOD(event_id, 2) = 0
            """,
            "seed BC04 bulk release stage",
        )
        hold_last = self.protected_same_release_row_count * 2
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.stage_table} (
                event_id, release_id, scope_state, wave_id, expected_risk_bucket, expected_version, source_reason
            )
            SELECT event_id, '{self.release_id}', 'hold',
                0,
                CASE
                    WHEN amount_cents >= 90000 THEN 'critical'
                    WHEN amount_cents >= 60000 THEN 'high'
                    WHEN status = 'review' THEN 'review'
                    ELSE 'standard'
                END,
                version + 1, 'approved-risk-policy-2026q3-hold'
            FROM {self.source_db}.{self.table}
            WHERE event_id <= {hold_last} AND MOD(event_id, 2) = 1
            """,
            "seed BC04 protected same-release hold stage",
        )
        competing_start = hold_last
        competing_last = (
            self.protected_same_release_row_count + self.competing_row_count
        ) * 2
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.stage_table} (
                event_id, release_id, scope_state, wave_id, expected_risk_bucket, expected_version, source_reason
            )
            SELECT event_id, '{self.competing_release_id}', 'historical',
                0,
                CASE
                    WHEN amount_cents >= 90000 THEN 'critical'
                    WHEN amount_cents >= 60000 THEN 'high'
                    WHEN status = 'review' THEN 'review'
                    ELSE 'standard'
                END,
                version + 1, 'historical-risk-policy-2026q2'
            FROM {self.source_db}.{self.table}
            WHERE event_id > {competing_start} AND event_id <= {competing_last} AND MOD(event_id, 2) = 1
            """,
            "seed BC04 competing historical release stage",
        )
        approved = self._rows(
            f"""
            SELECT COUNT(*), COALESCE(SUM(t.amount_cents), 0),
                COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, t.status,
                    t.amount_cents, t.event_time, t.payload, s.expected_version,
                    s.expected_risk_bucket))), 0),
                MIN(t.event_id), MAX(t.event_id)
            FROM {self.source_db}.{self.table} t
            JOIN {self.control_db}.{self.stage_table} s ON s.event_id=t.event_id
            WHERE s.release_id='{self.release_id}' AND s.scope_state='{self.required_scope}'
            """,
            "calculate BC04 approved change truth",
        )
        scope = self._rows(
            f"""
            SELECT COUNT(*), COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id,
                t.status, t.amount_cents, t.event_time, t.payload, t.version,
                COALESCE(t.risk_bucket, '')))), 0)
            FROM {self.source_db}.{self.table} t
            WHERE NOT EXISTS (
                SELECT 1 FROM {self.control_db}.{self.stage_table} s
                WHERE s.release_id='{self.release_id}' AND s.scope_state='{self.required_scope}'
                    AND s.event_id=t.event_id
            )
            """,
            "calculate BC04 out-of-scope truth",
        )
        canary = self._rows(
            f"""
            SELECT COUNT(*), COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, t.status,
                t.amount_cents, t.event_time, t.payload, s.expected_version,
                s.expected_risk_bucket))), 0)
            FROM {self.source_db}.{self.table} t
            JOIN {self.control_db}.{self.stage_table} s ON s.event_id=t.event_id
            WHERE s.release_id='{self.release_id}' AND s.wave_id={self.canary_wave_id}
            """,
            "calculate BC04 canary truth",
        )
        bulk_baseline = self._rows(
            f"""
            SELECT COUNT(*), COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, t.status,
                t.amount_cents, t.event_time, t.payload, t.version,
                COALESCE(t.risk_bucket, '')))), 0)
            FROM {self.source_db}.{self.table} t
            JOIN {self.control_db}.{self.stage_table} s ON s.event_id=t.event_id
            WHERE s.release_id='{self.release_id}' AND s.wave_id={self.bulk_wave_id}
            """,
            "calculate BC04 bulk baseline truth",
        )
        bulk_review = self._rows(
            f"""
            SELECT COUNT(*), COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, t.status,
                t.amount_cents, t.event_time, t.payload, s.expected_version,
                s.expected_risk_bucket))), 0)
            FROM {self.source_db}.{self.table} t
            JOIN {self.control_db}.{self.stage_table} s ON s.event_id=t.event_id
            WHERE s.release_id='{self.release_id}' AND s.wave_id={self.bulk_wave_id}
                AND s.event_id <= {self.bulk_review_last_event_id}
            """,
            "calculate BC04 first bulk review truth",
        )
        bulk_review_remaining = self._rows(
            f"""
            SELECT COUNT(*), COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, t.status,
                t.amount_cents, t.event_time, t.payload, t.version,
                COALESCE(t.risk_bucket, '')))), 0)
            FROM {self.source_db}.{self.table} t
            JOIN {self.control_db}.{self.stage_table} s ON s.event_id=t.event_id
            WHERE s.release_id='{self.release_id}' AND s.wave_id={self.bulk_wave_id}
                AND s.event_id > {self.bulk_review_last_event_id}
            """,
            "calculate BC04 remaining bulk review baseline",
        )
        if (
            len(approved) != 1 or len(approved[0]) != 5
            or len(scope) != 1 or len(scope[0]) != 2
            or len(canary) != 1 or len(canary[0]) != 2
            or len(bulk_baseline) != 1 or len(bulk_baseline[0]) != 2
            or len(bulk_review) != 1 or len(bulk_review[0]) != 2
            or len(bulk_review_remaining) != 1 or len(bulk_review_remaining[0]) != 2
        ):
            raise RuntimeError(
                "BC04 truth shape invalid: "
                f"approved={approved!r}, scope={scope!r}, canary={canary!r}, bulk_baseline={bulk_baseline!r}, "
                f"bulk_review={bulk_review!r}, bulk_review_remaining={bulk_review_remaining!r}"
            )
        expected = approved[0]
        out_of_scope = scope[0]
        if int(expected[0]) != self.approved_row_count:
            raise RuntimeError(
                f"BC04 approved stage cardinality mismatch: expected={self.approved_row_count}, observed={expected[0]}"
            )
        self._sql(
            f"""
            INSERT INTO {self.control_db}.{self.contract_table} (
                contract_id, release_id, required_scope, expected_rows, expected_sum_cents, expected_crc,
                out_of_scope_rows, out_of_scope_crc, first_event_id, last_event_id,
                index_columns, max_batch_seconds, frontend_slo_p95_ms, immutable_marker,
                initial_batch_rows, continuation_batch_rows, feedback_view,
                canary_wave_id, canary_expected_rows, canary_expected_crc,
                bulk_wave_id, bulk_expected_rows, bulk_baseline_crc, gate_table,
                bulk_review_rows, bulk_review_last_event_id, bulk_review_expected_crc,
                bulk_review_remaining_crc, created_at
            ) VALUES (
                '{self.contract_id}', '{self.release_id}', '{self.required_scope}', {int(expected[0])},
                {int(expected[1])}, {int(expected[2])}, {int(out_of_scope[0])}, {int(out_of_scope[1])},
                {int(expected[3])}, {int(expected[4])},
                '{','.join(self.allowed_index_columns)}', {self.max_batch_seconds}, {self.frontend_slo_p95_ms},
                'bc04-contract-immutable-v1', {self.initial_batch_rows}, {self.continuation_batch_rows},
                '{self.feedback_view}', {self.canary_wave_id}, {int(canary[0][0])}, {int(canary[0][1])},
                {self.bulk_wave_id}, {int(bulk_baseline[0][0])}, {int(bulk_baseline[0][1])},
                '{self.gate_table}', {int(bulk_review[0][0])}, {self.bulk_review_last_event_id},
                {int(bulk_review[0][1])}, {int(bulk_review_remaining[0][1])}, CURRENT_TIMESTAMP(6)
            )
            """,
            "record BC04 immutable change truth",
        )

    def _verify_persistent_state(self) -> None:
        if not self._configured or not self._databases_created:
            raise RuntimeError(
                "BC04 persistent state verification requires installed databases: "
                f"configured={self._configured}, databases_created={self._databases_created}"
            )
        stage = self._rows(
            f"SELECT release_id, scope_state, wave_id, COUNT(*), MIN(event_id), MAX(event_id) "
            f"FROM {self.control_db}.{self.stage_table} "
            f"GROUP BY release_id, scope_state, wave_id ORDER BY release_id, scope_state, wave_id",
            "verify BC04 release stage",
        )
        contract = self._rows(
            f"SELECT release_id, required_scope, expected_rows, expected_sum_cents, expected_crc, "
            f"out_of_scope_rows, out_of_scope_crc, "
            f"first_event_id, last_event_id, index_columns, max_batch_seconds, frontend_slo_p95_ms, immutable_marker, "
            f"initial_batch_rows, continuation_batch_rows, feedback_view, canary_wave_id, canary_expected_rows, "
            f"canary_expected_crc, bulk_wave_id, bulk_expected_rows, bulk_baseline_crc, gate_table, "
            f"bulk_review_rows, bulk_review_last_event_id, bulk_review_expected_crc, bulk_review_remaining_crc "
            f"FROM {self.control_db}.{self.contract_table} WHERE contract_id='{self.contract_id}'",
            "verify BC04 change contract",
        )
        feedback = self._rows(
            f"SELECT completed_batches, last_event_id, processed_rows, max_next_rows, feedback_phase, phase_id, "
            f"next_wave_id, gate_required, gate_state, canary_rows, bulk_rows, bulk_review_gate_state "
            f"FROM {self.control_db}.{self.feedback_view} WHERE job_id='{self.job_id}'",
            "verify BC04 initial adaptive feedback",
        )
        job = self._rows(
            f"SELECT release_id, target_table, target_column, status, last_event_id, processed_rows "
            f"FROM {self.control_db}.{self.job_table} WHERE job_id='{self.job_id}'",
            "verify BC04 change job",
        )
        gates = self._rows(
            f"SELECT gate_id, job_id, wave_id, verified_rows, verified_crc, remaining_apply_rows, "
            f"remaining_apply_crc, frontend_p95_ms, decision_code FROM {self.control_db}.{self.gate_table} "
            f"WHERE job_id='{self.job_id}' ORDER BY gate_id",
            "verify BC04 initial canary gate",
        )
        expected_stage = (
            (
                self.competing_release_id,
                "historical",
                0,
                self.competing_row_count,
                self.protected_same_release_row_count * 2 + 1,
                (self.protected_same_release_row_count + self.competing_row_count) * 2 - 1,
            ),
            (self.release_id, self.required_scope, self.canary_wave_id, self.canary_row_count, 2, self.canary_row_count * 2),
            (
                self.release_id,
                self.required_scope,
                self.bulk_wave_id,
                self.bulk_row_count,
                self.canary_row_count * 2 + 2,
                self.approved_row_count * 2,
            ),
            (
                self.release_id,
                "hold",
                0,
                self.protected_same_release_row_count,
                1,
                self.protected_same_release_row_count * 2 - 1,
            ),
        )
        observed_stage = tuple(
            (str(row[0]), str(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5]))
            for row in stage
            if len(row) == 6
        )
        if (
            observed_stage != expected_stage
            or len(contract) != 1
            or len(contract[0]) != 27
            or len(feedback) != 1
            or len(feedback[0]) != 12
            or len(job) != 1
            or len(job[0]) != 6
            or gates
        ):
            raise RuntimeError(
                "BC04 persistent state shape invalid: "
                f"stage={stage!r}, contract={contract!r}, feedback={feedback!r}, job={job!r}, gates={gates!r}"
            )
        if int(contract[0][2]) != self.approved_row_count:
            raise RuntimeError(
                f"BC04 approved row count mismatch: stage={stage!r}, contract={contract[0]!r}, "
                f"expected={self.approved_row_count}"
            )
        expected_feedback = (0, 0, 0, self.initial_batch_rows, "initial", 1, self.canary_wave_id, 0, 0, 0, 0, 0)
        observed_feedback = (
            int(feedback[0][0]),
            int(feedback[0][1]),
            int(feedback[0][2]),
            int(feedback[0][3]),
            str(feedback[0][4]),
            int(feedback[0][5]),
            int(feedback[0][6]),
            int(feedback[0][7]),
            int(feedback[0][8]),
            int(feedback[0][9]),
            int(feedback[0][10]),
            int(feedback[0][11]),
        )
        observed_contract = (
            str(contract[0][1]),
            int(contract[0][13]),
            int(contract[0][14]),
            str(contract[0][15]),
            int(contract[0][16]),
            int(contract[0][17]),
            int(contract[0][19]),
            int(contract[0][20]),
            str(contract[0][22]),
        )
        if observed_contract != (
            self.required_scope,
            self.initial_batch_rows,
            self.continuation_batch_rows,
            self.feedback_view,
            self.canary_wave_id,
            self.canary_row_count,
            self.bulk_wave_id,
            self.bulk_row_count,
            self.gate_table,
        ):
            raise RuntimeError(
                "BC04 adaptive contract mismatch: "
                f"expected={(self.initial_batch_rows, self.continuation_batch_rows, self.feedback_view)!r}, "
                f"observed={observed_contract!r}"
            )
        observed_review_contract = (
            int(contract[0][23]),
            int(contract[0][24]),
            int(contract[0][25]),
            int(contract[0][26]),
        )
        if observed_review_contract[:2] != (
            self.bulk_review_row_count,
            self.bulk_review_last_event_id,
        ) or observed_review_contract[2:] == (0, 0):
            raise RuntimeError(
                "BC04 mid-bulk review contract mismatch: "
                f"expected_rows={self.bulk_review_row_count}, expected_last={self.bulk_review_last_event_id}, "
                f"observed={observed_review_contract!r}"
            )
        if observed_feedback != expected_feedback:
            raise RuntimeError(
                f"BC04 initial feedback mismatch: expected={expected_feedback!r}, observed={observed_feedback!r}"
            )
        expected_job = (
            self.release_id,
            f"{self.source_db}.{self.table}",
            self.target_column,
            "pending",
            "0",
            "0",
        )
        observed_job = tuple(str(value) for value in job[0])
        if observed_job != expected_job:
            raise RuntimeError(f"BC04 initial job state mismatch: expected={expected_job!r}, observed={observed_job!r}")


__all__ = ("TidbBusinessChangeLargeTableBatchDmlInjector",)
