from dataclasses import dataclass

from src.database.sql import sql_literal
from src.workloads.specs import WorkloadProfile
from src.protocols.report import structured_reference_report
from src.scenarios.evaluation.tidb.business_change.lightning_checkpoint import (
    TidbBusinessChangeLightningCheckpointForLightningCheckpointScaleOutEvaluatorCase,
    TidbBusinessChangeLightningCheckpointForPartitionResumeEvaluatorCase,
)

from src.workloads.specs import BackgroundWorkloadStartPhase, BackgroundWorkloadSpec
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeLightningCheckpointCase(TiDBScenarioCase):
    database: str
    table: str
    control_table: str
    request_table: str
    capacity_plan_table: str
    checkpoint_manifest_table: str
    capacity_reservation_table: str
    lease_journal_table: str
    resume_gate_table: str
    source_manifest_table: str
    schema_manifest_table: str
    checkpoint_identity_table: str
    checkpoint_table_manifest_table: str
    protection_state_table: str
    request_id: str
    source_rows: int
    source_seed: int
    expected_checksum: int
    initial_tikv_count: int
    target_tikv_count: int
    approved_tikv_service: str
    approved_plan_epoch: int
    approved_checkpoint_generation: int
    approved_reservation_token: str
    approved_fence_token: str
    expected_source_sha256: str
    expected_active_tikv_services: tuple[str, ...]
    checkpoint_schema: str
    order_events_table: str = "admission_order_events"
    customer_profile_table: str = "admission_customer_profile"
    invoice_rollup_table: str = "admission_invoice_rollup"
    missing_cache_table: str = "admission_order_cache_missing"
    legacy_shadow_table: str = "admission_legacy_import_shadow"
    candidate_tikv_services: tuple[str, ...] = ("tikv-5", "tikv-6", "tikv-7")
    checkpoint_verified_rows: int = 1_880_000


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeLightningCheckpointForLightningCheckpointScaleOutScenarioCase(
    TidbBusinessChangeLightningCheckpointCase
):
    pass


class TidbBusinessChangeLightningCheckpointForPartitionResumeScenarioCase(
    TidbBusinessChangeLightningCheckpointCase
):
    pass


def _background_workload(
    database: str,
    table: str,
    *,
    order_events_table: str = "admission_order_events",
    customer_profile_table: str = "admission_customer_profile",
    invoice_rollup_table: str = "admission_invoice_rollup",
    missing_cache_table: str = "admission_order_cache_missing",
    legacy_shadow_table: str = "admission_legacy_import_shadow",
    source_manifest_table: str = "admission_lightning_source_manifest",
    schema_manifest_table: str = "admission_lightning_schema_manifest",
    checkpoint_identity_table: str = "admission_lightning_checkpoint_identity",
    checkpoint_table_manifest_table: str = "admission_lightning_checkpoint_table_manifest",
    protection_state_table: str = "admission_lightning_protection_state",
) -> BackgroundWorkloadSpec:
    return BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="admission_order_status_dashboard",
                sql=(
                    f"SELECT status, COUNT(*) AS orders, SUM(amount_cents) AS gross_cents "
                    f"FROM {database}.{order_events_table} "
                    "GROUP BY status ORDER BY gross_cents DESC"
                ),
                qps=0.35,
                tier="OLTP_CORE",
                application_name="order-status-api",
            ),
            WorkloadProfile(
                name="admission_customer_account_rollup",
                sql=(
                    f"SELECT account_id, COUNT(*) AS events, SUM(amount_cents) AS total_cents "
                    f"FROM {database}.{order_events_table} "
                    "GROUP BY account_id ORDER BY total_cents DESC LIMIT 30"
                ),
                qps=0.25,
                tier="OLAP_BURST",
                application_name="customer-360-api",
            ),
            WorkloadProfile(
                name="admission_target_import_preview",
                sql=(
                    f"SELECT account_id, COUNT(*) AS rows_seen, SUM(amount_cents) AS amount_cents "
                    f"FROM {database}.{table} "
                    "GROUP BY account_id ORDER BY amount_cents DESC LIMIT 20"
                ),
                qps=0.28,
                tier="OLAP_BURST",
                application_name="migration-preview",
            ),
            WorkloadProfile(
                name="admission_customer_tier_lookup",
                sql=(
                    f"SELECT tier, COUNT(*) AS customers "
                    f"FROM {database}.{customer_profile_table} "
                    "GROUP BY tier ORDER BY customers DESC"
                ),
                qps=0.32,
                tier="OLTP_CORE",
                application_name="customer-profile-api",
            ),
            WorkloadProfile(
                name="admission_invoice_reconciliation",
                sql=(
                    f"SELECT status, COUNT(*) AS invoices, SUM(total_cents) AS total_cents "
                    f"FROM {database}.{invoice_rollup_table} "
                    "GROUP BY status ORDER BY total_cents DESC"
                ),
                qps=0.22,
                tier="OLAP_BURST",
                application_name="invoice-reconciliation",
            ),
            WorkloadProfile(
                name="admission_target_truth_probe",
                sql=(
                    f"SELECT COUNT(*) AS rows_seen, SUM(id) AS id_sum, "
                    f"SUM(account_id) AS account_sum, SUM(amount_cents) AS amount_sum "
                    f"FROM {database}.{table}"
                ),
                qps=0.16,
                tier="MIGRATION_OBSERVABILITY",
                application_name="migration-verifier",
            ),
            WorkloadProfile(
                name="admission_cluster_inventory_probe",
                sql=(
                    "SELECT TYPE, COUNT(*) AS instances "
                    "FROM information_schema.cluster_info GROUP BY TYPE"
                ),
                qps=0.42,
                tier="TOPOLOGY_CHURN",
                application_name="capacity-controller",
            ),
            WorkloadProfile(
                name="admission_processlist_probe",
                sql=(
                    "SELECT USER, COUNT(*) AS sessions "
                    "FROM information_schema.cluster_processlist GROUP BY USER"
                ),
                qps=0.38,
                tier="TOPOLOGY_CHURN",
                application_name="platform-observer",
            ),
            WorkloadProfile(
                name="admission_schema_inventory_probe",
                sql=(
                    "SELECT TABLE_NAME, TABLE_ROWS "
                    "FROM information_schema.tables "
                    f"WHERE TABLE_SCHEMA = '{database}' ORDER BY TABLE_NAME"
                ),
                qps=0.3,
                tier="DDL_MAINTENANCE",
                application_name="schema-registry",
            ),
            WorkloadProfile(
                name="admission_stats_meta_probe",
                sql=(
                    "SELECT table_id, modify_count, count "
                    "FROM mysql.stats_meta ORDER BY modify_count DESC LIMIT 20"
                ),
                qps=0.2,
                tier="DDL_MAINTENANCE",
                application_name="stats-maintenance",
            ),
            WorkloadProfile(
                name="admission_capacity_plan_watch",
                sql=(
                    f"SELECT node_name, plan_epoch, zone, device_class, capacity_gib, available_gib, "
                    f"checkpoint_compatible, lifecycle_state "
                    f"FROM {database}.admission_tikv_capacity_plan ORDER BY node_name, plan_epoch"
                ),
                qps=0.24,
                tier="TOPOLOGY_CHURN",
                application_name="capacity-controller",
            ),
            WorkloadProfile(
                name="admission_capacity_reservation_watch",
                sql=(
                    f"SELECT request_id, node_name, plan_epoch, checkpoint_generation, "
                    f"reservation_state FROM {database}.admission_tikv_capacity_reservation "
                    "ORDER BY request_id, node_name"
                ),
                qps=0.24,
                tier="TOPOLOGY_CHURN",
                application_name="capacity-controller",
            ),
            WorkloadProfile(
                name="admission_checkpoint_manifest_watch",
                sql=(
                    f"SELECT node_name, checkpoint_schema, checkpoint_generation, reuse_state, "
                    f"source_sha256, fence_token, verified_rows, lease_state "
                    f"FROM {database}.admission_checkpoint_manifest "
                    "ORDER BY node_name, checkpoint_generation"
                ),
                qps=0.22,
                tier="MIGRATION_OBSERVABILITY",
                application_name="migration-supervisor",
            ),
            WorkloadProfile(
                name="admission_resume_gate_watch",
                sql=(
                    f"SELECT gate_state, approved_service, approved_epoch, checkpoint_schema "
                    f"FROM {database}.admission_lightning_resume_gate WHERE id = 1"
                ),
                qps=0.26,
                tier="MIGRATION_OBSERVABILITY",
                application_name="migration-supervisor",
            ),
            WorkloadProfile(
                name="admission_source_manifest_watch",
                sql=(
                    f"SELECT file_name, byte_size, file_sha256, row_start, row_end, "
                    f"file_format, file_charset FROM {database}.{source_manifest_table} "
                    "ORDER BY file_name"
                ),
                qps=0.18,
                tier="MIGRATION_OBSERVABILITY",
                application_name="migration-supervisor",
            ),
            WorkloadProfile(
                name="admission_schema_manifest_watch",
                sql=(
                    f"SELECT target_table, schema_sha256, index_signature, lightning_backend, "
                    f"config_sha256 FROM {database}.{schema_manifest_table} WHERE id = 1"
                ),
                qps=0.18,
                tier="MIGRATION_OBSERVABILITY",
                application_name="migration-supervisor",
            ),
            WorkloadProfile(
                name="admission_checkpoint_identity_watch",
                sql=(
                    f"SELECT task_identity, target_table, source_sha256, schema_sha256, checkpoint_driver, "
                    f"checkpoint_schema, checkpoint_table_count, checkpoint_metadata_sha256, checkpoint_state "
                    f"FROM {database}.{checkpoint_identity_table} WHERE id = 1"
                ),
                qps=0.18,
                tier="MIGRATION_OBSERVABILITY",
                application_name="migration-supervisor",
            ),
            WorkloadProfile(
                name="admission_checkpoint_table_watch",
                sql=(
                    f"SELECT checkpoint_table_name, table_rows, column_signature "
                    f"FROM {database}.{checkpoint_table_manifest_table} ORDER BY checkpoint_table_name"
                ),
                qps=0.18,
                tier="MIGRATION_OBSERVABILITY",
                application_name="migration-supervisor",
            ),
            WorkloadProfile(
                name="admission_protection_state_watch",
                sql=(
                    f"SELECT physical_backend, pitr_state, ticdc_state, parallel_import_enabled, "
                    f"empty_region_count, empty_region_limit, target_empty_at_start "
                    f"FROM {database}.{protection_state_table} WHERE id = 1"
                ),
                qps=0.18,
                tier="MIGRATION_OBSERVABILITY",
                application_name="migration-supervisor",
            ),
            WorkloadProfile(
                name="admission_lease_journal_watch",
                sql=(
                    f"SELECT request_id, node_name, plan_epoch, checkpoint_generation, "
                    f"lease_revision, lease_state, reservation_token, fence_token, renewed_at "
                    f"FROM {database}.admission_tikv_lease_journal "
                    "ORDER BY request_id, node_name, checkpoint_generation, lease_revision"
                ),
                qps=0.24,
                tier="TOPOLOGY_CHURN",
                application_name="migration-supervisor",
            ),
            WorkloadProfile(
                name="admission_request_snapshot",
                sql=(
                    f"SELECT request_id, required_zone, required_device_class, min_free_gib, "
                    f"plan_epoch, checkpoint_generation, checkpoint_schema, request_state "
                    f"FROM {database}.admission_lightning_request WHERE id = 1"
                ),
                qps=0.18,
                tier="DDL_MAINTENANCE",
                application_name="change-management",
            ),
            WorkloadProfile(
                name="admission_missing_cache_refresh",
                sql=f"SELECT COUNT(*) FROM {database}.{missing_cache_table}",
                qps=0.6,
                tier="LOG_NOISE",
                application_name="order-cache-refresh",
            ),
            WorkloadProfile(
                name="admission_legacy_schema_probe",
                sql=f"SELECT COUNT(*) FROM {database}.{legacy_shadow_table}",
                qps=0.5,
                tier="LOG_NOISE",
                application_name="legacy-import-monitor",
            ),
        ),
        worker_count=6,
        seed=0xBC05,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=5,
    )


_CASE = TidbBusinessChangeLightningCheckpointForLightningCheckpointScaleOutScenarioCase(
    case_id="lightning_checkpoint_scale_out",
    reference_report=structured_reference_report(
        case_id="lightning_checkpoint_scale_out",
        factors=(),
        changes=("resumed the original Lightning checkpoint after adding the sixth TiKV",),
        verification=("row count, aggregate truth, checksum, stats, and Store health were verified",),
        summary="The reference path resumed the checkpointed import and verified the completed load.",
    ),
    case_no=0,
    evaluator=TidbBusinessChangeLightningCheckpointForLightningCheckpointScaleOutEvaluatorCase,
    title="Complete an interrupted 5M-row Lightning import with safe capacity admission.",
    alert=(
        "[CRITICAL] [Migration Control Plane] 一次 5M 行 CSV Lightning 导入在资源压力窗口中断，"
        "checkpoint 已保留，业务订单、客户和对账查询仍在运行。当前容量变更尚未完成，只有部分 TiKV Store "
        "正在承载导入，仍有尚未投入服务的候选容量。请从集群和控制面现状判断安全的恢复范围，保持源文件、目标表和 "
        "checkpoint 不变，完成原 checkpoint 的恢复；恢复前要确认容量准入以及租约/版本状态与当前 checkpoint 一致。"
        "恢复后必须验证 5,000,000 行、业务聚合、ADMIN CHECKSUM、ANALYZE/stats 和目标 Store 状态，不能只依据 "
        "Lightning 进程退出码判定成功，也不能停止 Store、重建 checkpoint、删除或改写目标数据。"
    ),
    initial_state={
        "import_status": "checkpointed",
        "source_rows": 5_000_000,
        "active_tikv": 5,
        "checkpoint": "valid_and_reusable",
        "deferred_tikv_candidates": 3,
        "resume_gate": "pending",
        "capacity_reservation": "available",
        "lease_journal": "requires_fresh_renewal_after_manifest",
    },
    expected_target={
        "import_status": "completed",
        "source_rows": 5_000_000,
        "active_tikv": 6,
        "approved_tikv_service": "control_plane_selected",
        "deferred_tikv_remaining": 2,
        "resume_gate": "approved",
        "capacity_reservation": "committed",
        "lease_journal": "fresh_and_token_aligned",
        "checksum": 4_643_765_965_520_552_603,
        "analyze": "completed",
    },
    background_workload=_background_workload("benchops", "admission_lightning_high"),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.971328,
        reference_run_ids=(
            "reference-147__"
            "tidb_business_change_lightning_checkpoint__lightning_checkpoint_scale_out__mock_reference__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=8,
        tidb_count=2,
        sql_timeout_seconds=180,
        deferred_tikv_count=3,
        tikv_memory_mb=4096,
    ),
    database="benchops",
    table="admission_lightning_high",
    control_table="admission_lightning_control",
    request_table="admission_lightning_request",
    capacity_plan_table="admission_tikv_capacity_plan",
    checkpoint_manifest_table="admission_checkpoint_manifest",
    capacity_reservation_table="admission_tikv_capacity_reservation",
    lease_journal_table="admission_tikv_lease_journal",
    resume_gate_table="admission_lightning_resume_gate",
    source_manifest_table="admission_lightning_source_manifest",
    schema_manifest_table="admission_lightning_schema_manifest",
    checkpoint_identity_table="admission_lightning_checkpoint_identity",
    checkpoint_table_manifest_table="admission_lightning_checkpoint_table_manifest",
    protection_state_table="admission_lightning_protection_state",
    request_id="BC05-LH-20260802-0042",
    source_rows=5_000_000,
    source_seed=20260801,
    expected_checksum=4_643_765_965_520_552_603,
    initial_tikv_count=5,
    target_tikv_count=6,
    approved_tikv_service="tikv-7",
    approved_plan_epoch=43,
    approved_checkpoint_generation=7003,
    approved_reservation_token="rsv-35355678219d4cd6bfbf64ca886561bb72ecb6422dc5929be4182e9a44e3d000",
    approved_fence_token="fence-ed61207cea950fc023a5440fbf331b4474f3ffd1699119b5ee6727a50c18bbfa",
    expected_source_sha256="04b076cd80fb52738cbe3706e7c274fb58c82d21a994126a1a756db1754b33b4",
    expected_active_tikv_services=("tikv-0", "tikv-1", "tikv-2", "tikv-3", "tikv-4", "tikv-7"),
    checkpoint_schema="bc05_lightning_checkpoint",
)


_PARTITION_RESUME_CASE = TidbBusinessChangeLightningCheckpointForPartitionResumeScenarioCase(
    case_id="lightning_checkpoint_partition_resume",
    reference_report=structured_reference_report(
        case_id="lightning_checkpoint_partition_resume",
        factors=(
            "the smaller billing import has two deferred capacity candidates with only one matching the current checkpoint lease",
            "manifest, reservation, and lease rows still require cross-table token alignment before resume",
        ),
        changes=(
            "selected the compatible billing capacity candidate and committed its reservation",
            "resumed the original partition checkpoint without rewriting source files or target rows",
        ),
        verification=(
            "billing row aggregates, checksum, stats, checkpoint phase, and selected Store state passed",
            "the lease was renewed after manifest verification and all unrelated candidates stayed untouched",
        ),
        summary="The billing partition import resumed from its existing checkpoint after capacity admission was reconciled.",
    ),
    case_no=1,
    evaluator=TidbBusinessChangeLightningCheckpointForPartitionResumeEvaluatorCase,
    title="Resume an interrupted billing partition import with checkpoint-safe capacity admission.",
    alert=(
        "[CRITICAL] billing_events 的分区 CSV Lightning 导入在容量压力窗口中断，原 checkpoint 仍可复用。"
        "请核对 billing 控制面、当前容量计划、reservation、manifest 和 lease；只启动与当前 checkpoint generation、"
        "source digest 和 fence 一致的候选 TiKV，提交准入并批准恢复 gate。恢复后验证 billing 行数、聚合、ADMIN CHECKSUM、"
        "stats 和 Store health。不得重写 checkpoint/source、修改 billing 数据、停止 Store 或启动未获批准的候选。"
    ),
    initial_state={
        "import_status": "checkpointed",
        "source_rows": 5_000_000,
        "active_tikv": 4,
        "checkpoint": "valid_and_reusable",
        "deferred_tikv_candidates": 2,
        "resume_gate": "pending",
        "capacity_reservation": "available",
        "lease_journal": "requires_fresh_renewal_after_manifest",
    },
    expected_target={
        "import_status": "completed",
        "source_rows": 5_000_000,
        "active_tikv": 5,
        "approved_tikv_service": "control_plane_selected",
        "resume_gate": "approved",
        "capacity_reservation": "committed",
        "lease_journal": "fresh_and_token_aligned",
        "checksum": 4_643_765_965_520_552_603,
        "analyze": "completed",
    },
    background_workload=_background_workload(
        "benchops_bc05_billing",
        "billing_events",
        order_events_table="billing_order_events",
        customer_profile_table="billing_customer_profile",
        invoice_rollup_table="billing_invoice_rollup",
        missing_cache_table="billing_order_cache_missing",
        legacy_shadow_table="billing_legacy_import_shadow",
        source_manifest_table="billing_lightning_source_manifest",
        schema_manifest_table="billing_lightning_schema_manifest",
        checkpoint_identity_table="billing_lightning_checkpoint_identity",
        checkpoint_table_manifest_table="billing_lightning_checkpoint_table_manifest",
        protection_state_table="billing_lightning_protection_state",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.0,
        reference_run_ids=(
            "tidb-reference-12__"
            "tidb_business_change_lightning_checkpoint__lightning_checkpoint_partition_resume__"
            "mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0, pd_count=3, tikv_count=6, tidb_count=2,
        sql_timeout_seconds=180, deferred_tikv_count=2, tikv_memory_mb=4096,
    ),
    database="benchops_bc05_billing",
    table="billing_events",
    control_table="billing_lightning_control",
    request_table="billing_lightning_request",
    capacity_plan_table="billing_tikv_capacity_plan",
    checkpoint_manifest_table="billing_checkpoint_manifest",
    capacity_reservation_table="billing_tikv_capacity_reservation",
    lease_journal_table="billing_tikv_lease_journal",
    resume_gate_table="billing_lightning_resume_gate",
    source_manifest_table="billing_lightning_source_manifest",
    schema_manifest_table="billing_lightning_schema_manifest",
    checkpoint_identity_table="billing_lightning_checkpoint_identity",
    checkpoint_table_manifest_table="billing_lightning_checkpoint_table_manifest",
    protection_state_table="billing_lightning_protection_state",
    request_id="BC05-BILL-20260813-0007",
    source_rows=5_000_000,
    source_seed=20260801,
    expected_checksum=4_643_765_965_520_552_603,
    initial_tikv_count=4,
    target_tikv_count=5,
    approved_tikv_service="tikv-5",
    approved_plan_epoch=61,
    approved_checkpoint_generation=8103,
    approved_reservation_token="rsv-billing-8103-current",
    approved_fence_token="fence-billing-8103-current",
    expected_source_sha256="04b076cd80fb52738cbe3706e7c274fb58c82d21a994126a1a756db1754b33b4",
    expected_active_tikv_services=("tikv-0", "tikv-1", "tikv-2", "tikv-3", "tikv-5"),
    checkpoint_schema="billing_lightning_partition_checkpoint",
    order_events_table="billing_order_events",
    customer_profile_table="billing_customer_profile",
    invoice_rollup_table="billing_invoice_rollup",
    missing_cache_table="billing_order_cache_missing",
    legacy_shadow_table="billing_legacy_import_shadow",
    candidate_tikv_services=("tikv-4", "tikv-5"),
    checkpoint_verified_rows=1_880_000,
)


class TidbBusinessChangeLightningCheckpointScenario(TiDBScenario):
    scenario_id = "tidb_business_change_lightning_checkpoint"
    description = "Complete an interrupted Lightning import under the current capacity plan."
    cases = (_CASE, _PARTITION_RESUME_CASE)

    def build_fault_plan(
        self,
        case: TidbBusinessChangeLightningCheckpointForLightningCheckpointScaleOutScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangeLightningCheckpointInjector,
                config={
                    "database": case.database,
                    "table": case.table,
                    "control_table": case.control_table,
                    "request_table": case.request_table,
                    "capacity_plan_table": case.capacity_plan_table,
                    "checkpoint_manifest_table": case.checkpoint_manifest_table,
                    "capacity_reservation_table": case.capacity_reservation_table,
                    "lease_journal_table": case.lease_journal_table,
                    "resume_gate_table": case.resume_gate_table,
                    "source_manifest_table": case.source_manifest_table,
                    "schema_manifest_table": case.schema_manifest_table,
                    "checkpoint_identity_table": case.checkpoint_identity_table,
                    "checkpoint_table_manifest_table": case.checkpoint_table_manifest_table,
                    "protection_state_table": case.protection_state_table,
                    "request_id": case.request_id,
                    "source_rows": case.source_rows,
                    "source_seed": case.source_seed,
                    "target_tikv_count": case.target_tikv_count,
                    "approved_tikv_service": case.approved_tikv_service,
                    "approved_plan_epoch": case.approved_plan_epoch,
                    "approved_checkpoint_generation": case.approved_checkpoint_generation,
                    "approved_reservation_token": case.approved_reservation_token,
                    "approved_fence_token": case.approved_fence_token,
                    "checkpoint_schema": case.checkpoint_schema,
                    "order_events_table": case.order_events_table,
                    "customer_profile_table": case.customer_profile_table,
                    "invoice_rollup_table": case.invoice_rollup_table,
                    "missing_cache_table": case.missing_cache_table,
                    "legacy_shadow_table": case.legacy_shadow_table,
                    "candidate_tikv_services": case.candidate_tikv_services,
                    "checkpoint_verified_rows": case.checkpoint_verified_rows,
                },
            ),
        )


__all__ = (
    "TidbBusinessChangeLightningCheckpointCase",
    "TidbBusinessChangeLightningCheckpointForLightningCheckpointScaleOutScenarioCase",
    "TidbBusinessChangeLightningCheckpointScenario",
)

import csv
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
from collections.abc import Mapping
from datetime import date, timedelta
from pathlib import Path

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)


class TidbBusinessChangeLightningCheckpointInjector(BaseFaultInjector):
    """Run a real Lightning import, interrupt it, and resume it after TiKV scale-out."""

    LIGHTNING_IMAGE = os.environ.get(
        "AIOPS_TIDB_LIGHTNING_IMAGE",
        "docker.m.daocloud.io/pingcap/tidb-lightning:v8.1.0",
    )
    CHECKPOINT_IMAGE = os.environ.get("AIOPS_BC05_CHECKPOINT_IMAGE", "mysql:8.0")
    CHECKPOINT_READY_MARKER = "MySQL init process done. Ready for start up."
    CHECKPOINT_WAIT_SECONDS = 900
    LIGHTNING_WAIT_SECONDS = 600

    def __init__(self) -> None:
        self.workspace = None
        self.source_dir = None
        self.sort_dir = None
        self.probe_dir = None
        self.source_sha256 = ""
        self.source_bundle_sha256 = ""
        self.source_file_manifest = ()
        self.target_schema_snapshot = {}
        self.target_schema_sha256 = ""
        self.target_index_signature = ""
        self.lightning_config_sha256 = ""
        self.checkpoint_identity_snapshot = {}
        self.checkpoint_table_manifest = ()
        self.partial_target_rows = 0
        self.supervisor = None
        self.supervisor_connection = None
        self.supervisor_stop = threading.Event()
        self.supervisor_error = None
        self.lightning_running = False
        self.checkpoint_started = False

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._prepare_workspace()
        self._write_source_files()
        self._prepare_cluster()
        self._write_lightning_config()
        self._start_checkpoint_store()
        self._start_lightning()
        self._wait_for_checkpoint()
        self._stop_lightning()
        self._capture_checkpoint_identity()
        self._set_phase("checkpointed")
        self._start_supervisor()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._assert_phase("checkpointed")
        self._load_persisted_checkpoint_identity()
        self._start_supervisor()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config, context.env)
        self._raise_supervisor_error()
        self._assert_phase("checkpointed")
        if not self.checkpoint_identity_snapshot:
            self._load_persisted_checkpoint_identity()
        control = json_object(
            context.env.execute_sql(
                f"SELECT phase, source_rows, source_sha256, checkpoint_schema "
                f"FROM {self.database}.{self.control_table} WHERE id = 1"
            ),
            "read BC05 Lightning control state",
        )
        node_health = json_object(
            context.env.observe_metric("node_health"),
            "read BC05 initial TiKV health",
        )
        source_manifest = json_object(
            context.env.execute_sql(
                f"SELECT file_name, byte_size, file_sha256, row_start, row_end, file_format, "
                f"file_charset, has_header, bundle_sha256 FROM {self.database}.{self.source_manifest_table} "
                "ORDER BY file_name"
            ),
            "read BC05 source manifest",
        )
        schema_manifest = json_object(
            context.env.execute_sql(
                f"SELECT target_table, schema_sha256, index_signature, create_statement, source_format, "
                f"source_charset, lightning_backend, config_sha256 FROM {self.database}.{self.schema_manifest_table} "
                "WHERE id = 1"
            ),
            "read BC05 schema manifest",
        )
        checkpoint_identity = json_object(
            context.env.execute_sql(
                f"SELECT task_identity, target_table, source_sha256, source_bundle_sha256, schema_sha256, "
                f"checkpoint_driver, checkpoint_host, checkpoint_schema, checkpoint_generation, "
                f"checkpoint_table_count, checkpoint_table_names, checkpoint_metadata_sha256, config_sha256, "
                f"partial_target_rows, checkpoint_state FROM {self.database}.{self.checkpoint_identity_table} "
                "WHERE id = 1"
            ),
            "read BC05 checkpoint identity",
        )
        checkpoint_tables = json_object(
            context.env.execute_sql(
                f"SELECT checkpoint_table_name, table_rows, column_signature, checkpoint_state "
                f"FROM {self.database}.{self.checkpoint_table_manifest_table} ORDER BY checkpoint_table_name"
            ),
            "read BC05 checkpoint table manifest",
        )
        protection_state = json_object(
            context.env.execute_sql(
                f"SELECT physical_backend, pitr_state, ticdc_state, parallel_import_enabled, "
                f"empty_region_count, empty_region_limit, target_empty_at_start, observed_target "
                f"FROM {self.database}.{self.protection_state_table} WHERE id = 1"
            ),
            "read BC05 physical import protection state",
        )
        return {
            "bc05_control_state": control,
            "bc05_initial_node_health": node_health,
            "bc05_source_files": {
                "rows": self.source_rows,
                "file_count": len(tuple(self.source_dir.glob("*.csv"))),
                "sha256": self.source_sha256,
                "bundle_sha256": self.source_bundle_sha256,
            },
            "bc05_source_manifest": source_manifest,
            "bc05_schema_manifest": schema_manifest,
            "bc05_checkpoint_identity": checkpoint_identity,
            "bc05_checkpoint_table_manifest": checkpoint_tables,
            "bc05_protection_state": protection_state,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._stop_lightning_if_running()
        supervisor_error = self._stop_supervisor()
        if supervisor_error is not None:
            raise RuntimeError(
                f"BC05 Lightning resume supervisor failed: {supervisor_error}"
            ) from supervisor_error

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._stop_lightning_if_running()
        supervisor_error = self._stop_supervisor()
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.database}"),
            f"drop BC05 database {self.database}",
        )
        self._remove_container_if_present(self.lightning_container)
        if self.checkpoint_started:
            self._remove_container_if_present(self.checkpoint_container)
        if self.workspace is not None:
            shutil.rmtree(self.workspace)
        if supervisor_error is not None:
            raise RuntimeError(
                f"BC05 Lightning resume supervisor failed: {supervisor_error}"
            ) from supervisor_error

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.deployment = env.get_deployment()
        self.database = validate_sql_identifier(str(config["database"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.control_table = validate_sql_identifier(str(config["control_table"]), "control_table")
        self.request_table = validate_sql_identifier(str(config["request_table"]), "request_table")
        self.capacity_plan_table = validate_sql_identifier(
            str(config["capacity_plan_table"]), "capacity_plan_table"
        )
        self.checkpoint_manifest_table = validate_sql_identifier(
            str(config["checkpoint_manifest_table"]), "checkpoint_manifest_table"
        )
        self.capacity_reservation_table = validate_sql_identifier(
            str(config["capacity_reservation_table"]), "capacity_reservation_table"
        )
        self.lease_journal_table = validate_sql_identifier(
            str(config["lease_journal_table"]), "lease_journal_table"
        )
        self.resume_gate_table = validate_sql_identifier(
            str(config["resume_gate_table"]), "resume_gate_table"
        )
        self.source_manifest_table = validate_sql_identifier(
            str(config["source_manifest_table"]), "source_manifest_table"
        )
        self.schema_manifest_table = validate_sql_identifier(
            str(config["schema_manifest_table"]), "schema_manifest_table"
        )
        self.checkpoint_identity_table = validate_sql_identifier(
            str(config["checkpoint_identity_table"]), "checkpoint_identity_table"
        )
        self.checkpoint_table_manifest_table = validate_sql_identifier(
            str(config["checkpoint_table_manifest_table"]), "checkpoint_table_manifest_table"
        )
        self.protection_state_table = validate_sql_identifier(
            str(config["protection_state_table"]), "protection_state_table"
        )
        self.request_id = str(config["request_id"])
        self.checkpoint_schema = validate_sql_identifier(
            str(config["checkpoint_schema"]), "checkpoint_schema"
        )
        self.source_rows = int(config["source_rows"])
        self.source_seed = int(config["source_seed"])
        self.target_tikv_count = int(config["target_tikv_count"])
        self.approved_tikv_service = str(config["approved_tikv_service"])
        self.approved_plan_epoch = int(config["approved_plan_epoch"])
        self.approved_checkpoint_generation = int(config["approved_checkpoint_generation"])
        self.approved_reservation_token = str(config["approved_reservation_token"])
        self.approved_fence_token = str(config["approved_fence_token"])
        self.lightning_container = f"{self.deployment.project_name}-{self.table}-lightning"
        self.checkpoint_container = f"{self.deployment.project_name}-{self.table}-checkpoint"
        self.checkpoint_host = f"{self.table}-checkpoint"
        self.order_events_table = validate_sql_identifier(
            str(config.get("order_events_table", "admission_order_events")), "order_events_table"
        )
        self.customer_profile_table = validate_sql_identifier(
            str(config.get("customer_profile_table", "admission_customer_profile")), "customer_profile_table"
        )
        self.invoice_rollup_table = validate_sql_identifier(
            str(config.get("invoice_rollup_table", "admission_invoice_rollup")), "invoice_rollup_table"
        )
        self.missing_cache_table = validate_sql_identifier(
            str(config.get("missing_cache_table", "admission_order_cache_missing")), "missing_cache_table"
        )
        self.legacy_shadow_table = validate_sql_identifier(
            str(config.get("legacy_shadow_table", "admission_legacy_import_shadow")), "legacy_shadow_table"
        )
        self.candidate_tikv_services = tuple(
            str(value) for value in config.get("candidate_tikv_services", ("tikv-5", "tikv-6", "tikv-7"))
        )
        self.checkpoint_verified_rows = int(config.get("checkpoint_verified_rows", 1_880_000))
        self.network = f"{self.deployment.project_name}_default"

    def _opaque_token(self, kind: str, node: str, plan_epoch: int, generation: int) -> str:
        material = f"BC05/{kind}/{self.request_id}/{node}/{plan_epoch}/{generation}"
        return f"{kind}-{hashlib.sha256(material.encode()).hexdigest()}"

    def _prepare_workspace(self) -> None:
        self.workspace = Path(
            tempfile.mkdtemp(
                prefix=f"aiopsbench-bc05-{self.env.run_id}-",
            )
        )
        self.source_dir = self.workspace / "source"
        self.sort_dir = self.workspace / "sort"
        self.probe_dir = self.workspace / "probe"
        self.source_dir.mkdir()
        self.sort_dir.mkdir()
        self.probe_dir.mkdir()

    def _prepare_cluster(self) -> None:
        require_sql_success(
            self.env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {self.database}"),
            f"create BC05 database {self.database}",
        )
        require_sql_success(
            self.env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{self.table}"),
            f"clear BC05 target table {self.database}.{self.table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.table} ("
                "id BIGINT NOT NULL PRIMARY KEY, "
                "account_id BIGINT NOT NULL, "
                "amount_cents BIGINT NOT NULL, "
                "event_date DATE NOT NULL, "
                "payload VARCHAR(96) NOT NULL"
                ")"
            ),
            f"create BC05 target table {self.database}.{self.table}",
        )
        self.target_schema_snapshot = self._read_target_schema_snapshot()
        self.target_schema_sha256 = self.target_schema_snapshot["schema_sha256"]
        self.target_index_signature = self.target_schema_snapshot["index_signature"]
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.order_events_table} ("
                "event_id BIGINT PRIMARY KEY, account_id BIGINT NOT NULL, "
                "status VARCHAR(16) NOT NULL, amount_cents BIGINT NOT NULL, occurred_at DATE NOT NULL"
                ")"
            ),
            "create BC05 order workload table",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.customer_profile_table} ("
                "account_id BIGINT PRIMARY KEY, tier VARCHAR(16) NOT NULL, last_seen DATE NOT NULL"
                ")"
            ),
            "create BC05 customer workload table",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.invoice_rollup_table} ("
                "invoice_id BIGINT PRIMARY KEY, account_id BIGINT NOT NULL, "
                "status VARCHAR(16) NOT NULL, total_cents BIGINT NOT NULL"
                ")"
            ),
            "create BC05 invoice workload table",
        )
        self._insert_decoy_rows()
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.control_table} ("
                "id TINYINT PRIMARY KEY, phase ENUM('checkpointed', 'resuming', 'completed', 'failed') NOT NULL, source_rows BIGINT NOT NULL, "
                "source_sha256 CHAR(64) NOT NULL, checkpoint_schema VARCHAR(64) NOT NULL, "
                "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
                ")"
            ),
            f"create BC05 control table {self.database}.{self.control_table}",
        )
        self._prepare_evidence_tables()
        self._prepare_capacity_control_plane()

    def _prepare_evidence_tables(self) -> None:
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.source_manifest_table} ("
                "file_name VARCHAR(255) PRIMARY KEY, byte_size BIGINT NOT NULL, "
                "file_sha256 CHAR(64) NOT NULL, row_start BIGINT NOT NULL, row_end BIGINT NOT NULL, "
                "file_format VARCHAR(16) NOT NULL, file_charset VARCHAR(32) NOT NULL, "
                "has_header TINYINT NOT NULL, bundle_sha256 CHAR(64) NOT NULL"
                ")"
            ),
            f"create BC05 source manifest {self.database}.{self.source_manifest_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.schema_manifest_table} ("
                "id TINYINT PRIMARY KEY, target_table VARCHAR(255) NOT NULL, "
                "schema_sha256 CHAR(64) NOT NULL, index_signature CHAR(64) NOT NULL, "
                "create_statement TEXT NOT NULL, source_format VARCHAR(16) NOT NULL, "
                "source_charset VARCHAR(32) NOT NULL, lightning_backend VARCHAR(16) NOT NULL, "
                "config_sha256 CHAR(64) NOT NULL"
                ")"
            ),
            f"create BC05 schema manifest {self.database}.{self.schema_manifest_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.checkpoint_identity_table} ("
                "id TINYINT PRIMARY KEY, task_identity VARCHAR(255) NOT NULL, "
                "target_table VARCHAR(255) NOT NULL, source_sha256 CHAR(64) NOT NULL, "
                "source_bundle_sha256 CHAR(64) NOT NULL, schema_sha256 CHAR(64) NOT NULL, "
                "checkpoint_driver VARCHAR(16) NOT NULL, checkpoint_host VARCHAR(128) NOT NULL, "
                "checkpoint_schema VARCHAR(64) NOT NULL, checkpoint_generation INT NOT NULL, "
                "checkpoint_table_count INT NOT NULL, checkpoint_table_names TEXT NOT NULL, "
                "checkpoint_metadata_sha256 CHAR(64) NOT NULL, config_sha256 CHAR(64) NOT NULL, "
                "partial_target_rows BIGINT NOT NULL, checkpoint_state ENUM('checkpointed', 'completed') NOT NULL"
                ")"
            ),
            f"create BC05 checkpoint identity {self.database}.{self.checkpoint_identity_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.checkpoint_table_manifest_table} ("
                "checkpoint_table_name VARCHAR(128) PRIMARY KEY, table_rows BIGINT NOT NULL, "
                "column_signature CHAR(64) NOT NULL, checkpoint_state ENUM('checkpointed', 'completed') NOT NULL"
                ")"
            ),
            f"create BC05 checkpoint table manifest {self.database}.{self.checkpoint_table_manifest_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.protection_state_table} ("
                "id TINYINT PRIMARY KEY, physical_backend VARCHAR(16) NOT NULL, "
                "pitr_state ENUM('disabled', 'enabled') NOT NULL, "
                "ticdc_state ENUM('no_changefeed', 'running') NOT NULL, "
                "parallel_import_enabled TINYINT NOT NULL, empty_region_count INT NOT NULL, "
                "empty_region_limit INT NOT NULL, target_empty_at_start TINYINT NOT NULL, "
                "observed_target VARCHAR(255) NOT NULL"
                ")"
            ),
            f"create BC05 protection state {self.database}.{self.protection_state_table}",
        )
        self._seed_evidence_manifests()

    def _seed_evidence_manifests(self) -> None:
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.source_manifest_table} "
                "(file_name, byte_size, file_sha256, row_start, row_end, file_format, file_charset, "
                "has_header, bundle_sha256) VALUES "
                + ", ".join(
                    "(" + ", ".join(
                        sql_literal(value)
                        for value in (
                            item["file_name"], item["byte_size"], item["file_sha256"],
                            item["row_start"], item["row_end"], "csv", "utf-8", 1,
                            self.source_bundle_sha256,
                        )
                    ) + ")"
                    for item in self.source_file_manifest
                )
            ),
            f"seed BC05 source manifest {self.database}.{self.source_manifest_table}",
        )
        schema = self.target_schema_snapshot
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.schema_manifest_table} "
                "(id, target_table, schema_sha256, index_signature, create_statement, source_format, "
                "source_charset, lightning_backend, config_sha256) VALUES (1, "
                + ", ".join(
                    sql_literal(value)
                    for value in (
                        f"{self.database}.{self.table}",
                        schema["schema_sha256"],
                        schema["index_signature"],
                        schema["create_statement"],
                        "csv", "utf-8", "local", "pending",
                    )
                )
                + ")"
            ),
            f"seed BC05 schema manifest {self.database}.{self.schema_manifest_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.protection_state_table} "
                "(id, physical_backend, pitr_state, ticdc_state, parallel_import_enabled, "
                "empty_region_count, empty_region_limit, target_empty_at_start, observed_target) VALUES "
                f"(1, 'local', 'disabled', 'no_changefeed', 0, 0, 1000, 1, "
                f"{sql_literal(f'{self.database}.{self.table}')})"
            ),
            f"seed BC05 protection state {self.database}.{self.protection_state_table}",
        )

    def _prepare_capacity_control_plane(self) -> None:
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.request_table} ("
                "id TINYINT PRIMARY KEY, request_id VARCHAR(64) NOT NULL, "
                "target_table VARCHAR(128) NOT NULL, required_zone VARCHAR(32) NOT NULL, "
                "required_device_class VARCHAR(32) NOT NULL, min_free_gib INT NOT NULL, "
                "plan_epoch INT NOT NULL, checkpoint_schema VARCHAR(64) NOT NULL, "
                "checkpoint_generation INT NOT NULL, "
                "request_state ENUM('PENDING', 'APPROVED') NOT NULL"
                ")"
            ),
            f"create BC05 Lightning request table {self.database}.{self.request_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.request_table} "
                "(id, request_id, target_table, required_zone, required_device_class, "
                "min_free_gib, plan_epoch, checkpoint_schema, checkpoint_generation, request_state) VALUES "
                f"(1, '{self.request_id}', '{self.table}', 'az-b', 'nvme-10g', 6, "
                f"{self.approved_plan_epoch}, '{self.checkpoint_schema}', "
                f"{self.approved_checkpoint_generation}, 'PENDING')"
            ),
            f"seed BC05 Lightning request {self.request_id}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.capacity_plan_table} ("
                "node_name VARCHAR(32) NOT NULL, plan_epoch INT NOT NULL, "
                "zone VARCHAR(32) NOT NULL, device_class VARCHAR(32) NOT NULL, "
                "capacity_gib INT NOT NULL, available_gib INT NOT NULL, "
                "checkpoint_compatible TINYINT NOT NULL, lifecycle_state ENUM('retired', 'provisioned') NOT NULL, "
                "lease_state ENUM('expired', 'current') NOT NULL, observed_at DATETIME NOT NULL, "
                "PRIMARY KEY (node_name, plan_epoch)"
                ")"
            ),
            f"create BC05 TiKV capacity plan {self.database}.{self.capacity_plan_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.capacity_plan_table} "
                "(node_name, plan_epoch, zone, device_class, capacity_gib, available_gib, "
                "checkpoint_compatible, lifecycle_state, lease_state, observed_at) VALUES "
                + ", ".join(
                    f"('{node}', {epoch}, 'az-b', 'nvme-10g', 16, 12, 1, 'retired', 'expired', "
                    "'2026-07-01 00:00:00')"
                    for node in self.candidate_tikv_services
                    for epoch in range(self.approved_plan_epoch - 24, self.approved_plan_epoch)
                )
                + ", "
                + ", ".join(
                    self._capacity_plan_current_row(node)
                    for node in self.candidate_tikv_services
                )
            ),
            f"seed BC05 TiKV capacity plan {self.database}.{self.capacity_plan_table}",
        )

        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.capacity_reservation_table} ("
                "request_id VARCHAR(64) NOT NULL, node_name VARCHAR(32) NOT NULL, "
                "plan_epoch INT NOT NULL, checkpoint_generation INT NOT NULL, "
                "reservation_token VARCHAR(96) NOT NULL, reservation_state ENUM('released', 'expired', 'available', 'committed') NOT NULL, "
                "updated_at DATETIME NOT NULL, PRIMARY KEY (request_id, node_name, checkpoint_generation)"
                ")"
            ),
            f"create BC05 capacity reservation table {self.database}.{self.capacity_reservation_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.capacity_reservation_table} "
                "(request_id, node_name, plan_epoch, checkpoint_generation, reservation_token, "
                "reservation_state, updated_at) VALUES "
                + ", ".join(
                    f"('{self.request_id}', '{node}', {self.approved_plan_epoch - (self.approved_checkpoint_generation - generation)}, "
                    f"{generation}, '{self._opaque_token('rsv', node, self.approved_plan_epoch - (self.approved_checkpoint_generation - generation), generation)}', "
                    "'released', '2026-07-01 00:00:00')"
                    for node in self.candidate_tikv_services
                    for generation in range(
                        self.approved_checkpoint_generation - 24,
                        self.approved_checkpoint_generation,
                    )
                )
                + ", "
                + ", ".join(
                    f"('{self.request_id}', '{node}', {self.approved_plan_epoch}, "
                    f"{self.approved_checkpoint_generation}, "
                    f"'{self.approved_reservation_token if node == self.approved_tikv_service else self._opaque_token('rsv', node, self.approved_plan_epoch, self.approved_checkpoint_generation)}', "
                    f"'{('available' if node == self.approved_tikv_service or index else 'expired')}', "
                    f"'{('2026-08-02 10:42:00' if node == self.approved_tikv_service or index else '2026-08-02 10:40:00')}')"
                    for index, node in enumerate(self.candidate_tikv_services)
                )
            ),
            f"seed BC05 capacity reservations {self.database}.{self.capacity_reservation_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.checkpoint_manifest_table} ("
                "node_name VARCHAR(32) NOT NULL, checkpoint_schema VARCHAR(64) NOT NULL, "
                "checkpoint_generation INT NOT NULL, source_sha256 CHAR(64) NOT NULL, "
                "fence_token VARCHAR(128) NOT NULL, verified_rows BIGINT NOT NULL, "
                "reuse_state ENUM('retired', 'reusable') NOT NULL, "
                "lease_state ENUM('expired', 'current') NOT NULL, observed_at DATETIME NOT NULL, "
                "PRIMARY KEY (node_name, checkpoint_schema, checkpoint_generation)"
                ")"
            ),
            f"create BC05 checkpoint manifest {self.database}.{self.checkpoint_manifest_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.checkpoint_manifest_table} "
                "(node_name, checkpoint_schema, checkpoint_generation, source_sha256, "
                "fence_token, verified_rows, reuse_state, lease_state, observed_at) VALUES "
                + ", ".join(
                    f"('{node}', '{self.checkpoint_schema}', {generation}, '{self.source_sha256}', "
                    f"'{self._opaque_token('fence', node, self.approved_plan_epoch - (self.approved_checkpoint_generation - generation), generation)}', "
                    f"{self.checkpoint_verified_rows}, 'retired', 'expired', '2026-07-01 00:00:00')"
                    for node in self.candidate_tikv_services
                    for generation in range(
                        self.approved_checkpoint_generation - 24,
                        self.approved_checkpoint_generation,
                    )
                )
                + ", "
                + ", ".join(
                    f"('{node}', '{self.checkpoint_schema}', {self.approved_checkpoint_generation}, "
                    f"'{self.source_sha256}', "
                    f"'{self.approved_fence_token if node == self.approved_tikv_service else self._opaque_token('fence', node, self.approved_plan_epoch, self.approved_checkpoint_generation)}', "
                    f"{self.checkpoint_verified_rows}, 'reusable', "
                    f"'{('current' if node == self.approved_tikv_service or index else 'expired')}', "
                    f"'{('2026-08-02 10:42:00' if node == self.approved_tikv_service or index else '2026-08-02 09:40:00')}')"
                    for index, node in enumerate(self.candidate_tikv_services)
                )
            ),
            f"seed BC05 checkpoint manifest {self.database}.{self.checkpoint_manifest_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.lease_journal_table} ("
                "request_id VARCHAR(64) NOT NULL, node_name VARCHAR(32) NOT NULL, "
                "plan_epoch INT NOT NULL, checkpoint_generation INT NOT NULL, "
                "lease_revision INT NOT NULL, lease_state ENUM('released', 'expired', 'current') NOT NULL, "
                "reservation_token VARCHAR(96) NOT NULL, fence_token VARCHAR(128) NOT NULL, "
                "renewed_at DATETIME NOT NULL, "
                "PRIMARY KEY (request_id, node_name, checkpoint_generation, lease_revision)"
                ")"
            ),
            f"create BC05 lease journal {self.database}.{self.lease_journal_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.lease_journal_table} "
                "(request_id, node_name, plan_epoch, checkpoint_generation, lease_revision, "
                "lease_state, reservation_token, fence_token, renewed_at) VALUES "
                + ", ".join(
                    f"('{self.request_id}', '{node}', "
                    f"{self.approved_plan_epoch - (self.approved_checkpoint_generation - generation)}, "
                    f"{generation}, {generation}, 'released', "
                    f"'{self._opaque_token('rsv', node, self.approved_plan_epoch - (self.approved_checkpoint_generation - generation), generation)}', "
                    f"'{self._opaque_token('fence', node, self.approved_plan_epoch - (self.approved_checkpoint_generation - generation), generation)}', "
                    "'2026-07-01 00:00:00')"
                    for node in self.candidate_tikv_services
                    for generation in range(
                        self.approved_checkpoint_generation - 24,
                        self.approved_checkpoint_generation,
                    )
                )
                + ", "
                + ", ".join(
                    f"('{self.request_id}', '{node}', {self.approved_plan_epoch}, "
                    f"{self.approved_checkpoint_generation}, {712 if node == self.approved_tikv_service else 510 + index}, "
                    f"'{('current' if node == self.approved_tikv_service or index else 'expired')}', "
                    f"'{self.approved_reservation_token if node == self.approved_tikv_service else self._opaque_token('rsv', node, self.approved_plan_epoch, self.approved_checkpoint_generation)}', "
                    f"'{self.approved_fence_token if node == self.approved_tikv_service else self._opaque_token('fence', node, self.approved_plan_epoch, self.approved_checkpoint_generation)}', "
                    f"'{('2026-08-02 10:44:00' if node == self.approved_tikv_service else '2026-08-02 10:41:00')}')"
                    for index, node in enumerate(self.candidate_tikv_services)
                )
            ),
            f"seed BC05 lease journal {self.database}.{self.lease_journal_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.database}.{self.resume_gate_table} ("
                "id TINYINT PRIMARY KEY, request_id VARCHAR(64) NOT NULL, "
                "gate_state ENUM('pending', 'approved') NOT NULL, approved_service VARCHAR(32) NOT NULL, "
                "approved_epoch INT NOT NULL, checkpoint_schema VARCHAR(64) NOT NULL, "
                "checkpoint_source_sha256 CHAR(64) NOT NULL, approved_fence_token VARCHAR(128) NOT NULL, "
                "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
                ")"
            ),
            f"create BC05 Lightning resume gate {self.database}.{self.resume_gate_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.resume_gate_table} "
                "(id, request_id, gate_state, approved_service, approved_epoch, checkpoint_schema, "
                "checkpoint_source_sha256, approved_fence_token) VALUES "
                f"(1, '{self.request_id}', 'pending', '', 0, '{self.checkpoint_schema}', '', '')"
            ),
            f"seed BC05 Lightning resume gate {self.database}.{self.resume_gate_table}",
        )

    def _capacity_plan_current_row(self, node: str) -> str:
        capacity_gib = 8 if node == self.approved_tikv_service else 16
        available_gib = 7 if node == self.approved_tikv_service else 14
        lease_state = "current" if node != self.candidate_tikv_services[0] else "expired"
        observed_at = "2026-08-02 10:42:00" if lease_state == "current" else "2026-08-02 10:40:00"
        return (
            f"('{node}', {self.approved_plan_epoch}, 'az-b', 'nvme-10g', {capacity_gib}, "
            f"{available_gib}, 1, 'provisioned', '{lease_state}', '{observed_at}')"
        )

    def _insert_decoy_rows(self) -> None:
        source = (
            "SELECT ROW_NUMBER() OVER (ORDER BY a.table_name, b.table_name), "
            "MOD(ROW_NUMBER() OVER (ORDER BY a.table_name, b.table_name), 1000) + 1, "
            "CASE MOD(ROW_NUMBER() OVER (ORDER BY a.table_name, b.table_name), 3) "
            "WHEN 0 THEN 'PAID' WHEN 1 THEN 'PENDING' ELSE 'REFUND' END, "
            "100 + MOD(ROW_NUMBER() OVER (ORDER BY a.table_name, b.table_name) * 13, 90000), "
            "DATE_ADD('2024-01-01', INTERVAL MOD(ROW_NUMBER() OVER (ORDER BY a.table_name, b.table_name), 365) DAY) "
            "FROM (SELECT table_name FROM information_schema.tables LIMIT 64) a "
            "CROSS JOIN (SELECT table_name FROM information_schema.tables LIMIT 64) b LIMIT 2000"
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.order_events_table} "
                f"(event_id, account_id, status, amount_cents, occurred_at) {source}"
            ),
            "load BC05 order workload table",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.customer_profile_table} (account_id, tier, last_seen) "
                "SELECT n, CASE MOD(n, 4) WHEN 0 THEN 'GOLD' WHEN 1 THEN 'SILVER' "
                "WHEN 2 THEN 'BRONZE' ELSE 'TRIAL' END, '2024-01-01' "
                "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_name) AS n "
                "FROM information_schema.tables LIMIT 1000) AS rows_source"
            ),
            "load BC05 customer workload table",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.invoice_rollup_table} (invoice_id, account_id, status, total_cents) "
                "SELECT n, MOD(n, 1000) + 1, CASE MOD(n, 2) WHEN 0 THEN 'SETTLED' ELSE 'OPEN' END, "
                "1000 + n * 17 FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_name) AS n "
                "FROM information_schema.tables LIMIT 1000) AS rows_source"
            ),
            "load BC05 invoice workload table",
        )

    def _read_target_schema_snapshot(self) -> dict[str, str]:
        create_payload = json_object(
            self.env.execute_sql(f"SHOW CREATE TABLE {self.database}.{self.table}"),
            "read BC05 target SHOW CREATE",
        )
        create_rows = create_payload["result"]
        if len(create_rows) != 1 or len(create_rows[0]) < 2:
            raise RuntimeError(
                f"BC05 target SHOW CREATE shape is invalid: target={self.database}.{self.table!s}, "
                f"rows={create_rows!r}"
            )
        create_statement = str(create_rows[0][1])
        index_payload = json_object(
            self.env.execute_sql(
                "SELECT INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME, NON_UNIQUE, INDEX_TYPE "
                "FROM information_schema.statistics "
                f"WHERE TABLE_SCHEMA = {sql_literal(self.database)} "
                f"AND TABLE_NAME = {sql_literal(self.table)} "
                "ORDER BY INDEX_NAME, SEQ_IN_INDEX"
            ),
            "read BC05 target indexes",
        )
        index_rows = index_payload["result"]
        index_text = json.dumps(index_rows, ensure_ascii=False, sort_keys=True, default=str)
        index_signature = hashlib.sha256(index_text.encode()).hexdigest()
        schema_text = create_statement + "\n" + index_text
        return {
            "create_statement": create_statement,
            "schema_sha256": hashlib.sha256(schema_text.encode()).hexdigest(),
            "index_signature": index_signature,
        }

    def _write_source_files(self) -> None:
        rows_per_file = 500_000
        source_hash = hashlib.sha256()
        start = 1
        file_index = 0
        epoch = date(2024, 1, 1)
        while start <= self.source_rows:
            end = min(self.source_rows, start + rows_per_file - 1)
            path = self.source_dir / f"{self.database}.{self.table}.{file_index:06d}.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, lineterminator="\n")
                writer.writerow(("id", "account_id", "amount_cents", "event_date", "payload"))
                for row_id in range(start, end + 1):
                    account_id = 1 + ((row_id - 1) % 10_000)
                    amount_cents = 100 + ((row_id - 1) % 1_000)
                    row = (
                        row_id,
                        account_id,
                        amount_cents,
                        epoch + timedelta(days=(row_id - 1) % 365),
                        f"order-{self.source_seed}-{row_id % 1000:04d}",
                    )
                    writer.writerow(row)
                    source_hash.update(
                        (f"{row[0]},{row[1]},{row[2]},{row[3].isoformat()},{row[4]}\n").encode()
                    )
            start = end + 1
            file_index += 1
        self.source_sha256 = source_hash.hexdigest()
        manifest = self._read_source_file_manifest()
        bundle_text = "".join(
            f"{item['file_name']}\t{item['byte_size']}\t{item['file_sha256']}\t"
            f"{item['row_start']}\t{item['row_end']}\n"
            for item in manifest
        )
        self.source_file_manifest = tuple(manifest)
        self.source_bundle_sha256 = hashlib.sha256(bundle_text.encode()).hexdigest()

    def _read_source_file_manifest(self) -> list[dict[str, object]]:
        rows_per_file = 500_000
        manifest = []
        for index, path in enumerate(sorted(self.source_dir.glob("*.csv"))):
            byte_size = path.stat().st_size
            file_hash = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    file_hash.update(chunk)
            row_start = index * rows_per_file + 1
            row_end = min(self.source_rows, row_start + rows_per_file - 1)
            manifest.append({
                "file_name": path.name,
                "byte_size": byte_size,
                "file_sha256": file_hash.hexdigest(),
                "row_start": row_start,
                "row_end": row_end,
            })
        return manifest

    def _write_lightning_config(self) -> None:
        pd_services = self.deployment.COMPONENTS["pd"]
        current_leader = self.deployment.current_pd_leader()
        pd_order = (current_leader,) + tuple(
            service for service in pd_services if service != current_leader
        )
        pd_addresses = ",".join(f"{service}:2379" for service in pd_order)
        config = f'''[lightning]
level = "info"
file = "/probe/tidb-lightning.log"
check-requirements = true
index-concurrency = 1
table-concurrency = 1
region-concurrency = 1

[tikv-importer]
backend = "local"
sorted-kv-dir = "/sort"
store-write-bwlimit = "4MiB"
disk-quota = "4GiB"

[mydumper]
data-source-dir = "/data"
no-schema = true
filter = ["{self.database}.{self.table}"]
batch-size = "64MiB"
strict-format = true

[mydumper.csv]
separator = ","
delimiter = '"'
header = true
header-schema-match = true
not-null = true
backslash-escape = true

[tidb]
host = "tidb-0"
port = 4000
user = "root"
password = ""
status-port = 10080
pd-addr = "{pd_addresses}"
tls = "false"

[checkpoint]
enable = true
schema = "{self.checkpoint_schema}"
driver = "mysql"
dsn = "root:@tcp({self.checkpoint_host}:3306)/"
keep-after-success = true

[post-restore]
checksum = "required"
checksum-via-sql = true
analyze = "required"
'''
        (self.probe_dir / "lightning.toml").write_text(config, encoding="utf-8")
        self.lightning_config_sha256 = hashlib.sha256(config.encode()).hexdigest()

    def _start_checkpoint_store(self) -> None:
        self._remove_container_if_present(self.checkpoint_container)
        self._run_host(
            [
                "docker", "run", "--detach", "--name", self.checkpoint_container,
                "--network", self.network,
                "--network-alias", self.checkpoint_host,
                "--env", "MYSQL_ALLOW_EMPTY_PASSWORD=yes",
                "--tmpfs", "/var/lib/mysql:rw,nosuid,nodev,size=512m",
                self.CHECKPOINT_IMAGE,
            ],
            "start BC05 checkpoint store",
        )
        self.checkpoint_started = True
        deadline = time.monotonic() + self.CHECKPOINT_WAIT_SECONDS
        result = None
        while time.monotonic() < deadline:
            logs = subprocess.run(
                ["docker", "logs", self.checkpoint_container],
                capture_output=True,
                text=True,
            )
            if logs.returncode != 0:
                raise RuntimeError(
                    f"BC05 checkpoint log query failed: container={self.checkpoint_container!r}, "
                    f"returncode={logs.returncode}, stdout={logs.stdout.strip()!r}, "
                    f"stderr={logs.stderr.strip()!r}"
                )
            if self.CHECKPOINT_READY_MARKER not in f"{logs.stdout}\n{logs.stderr}":
                time.sleep(1)
                continue
            result = subprocess.run(
                [
                    "docker", "exec", self.checkpoint_container, "mysql", "-N", "-B", "-uroot",
                    "-e", "SELECT 1",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip() == "1":
                return
            time.sleep(1)
        raise RuntimeError(
            f"BC05 checkpoint MySQL did not become ready: container={self.checkpoint_container!r}, "
            f"stdout={result.stdout.strip() if result else ''!r}, "
            f"stderr={result.stderr.strip() if result else ''!r}"
        )

    def _checkpoint_query(self, sql: str) -> list[list[str]]:
        result = subprocess.run(
            [
                "docker", "exec", self.checkpoint_container, "mysql", "-N", "-B", "-uroot",
                "-e", sql,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"BC05 checkpoint metadata query failed: container={self.checkpoint_container!r}, "
                f"sql={sql!r}, returncode={result.returncode}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        return [line.split("\t") for line in result.stdout.splitlines() if line.strip()]

    def _read_checkpoint_snapshot(self) -> dict[str, object]:
        table_rows = self._checkpoint_query(
            "SELECT table_name, COALESCE(table_rows, 0) "
            "FROM information_schema.tables "
            f"WHERE table_schema = {sql_literal(self.checkpoint_schema)} ORDER BY table_name"
        )
        column_rows = self._checkpoint_query(
            "SELECT table_name, ordinal_position, column_name, column_type "
            "FROM information_schema.columns "
            f"WHERE table_schema = {sql_literal(self.checkpoint_schema)} "
            "ORDER BY table_name, ordinal_position"
        )
        columns_by_table = {}
        for table_name, ordinal, column_name, column_type in column_rows:
            columns_by_table.setdefault(table_name, []).append(
                (int(ordinal), column_name, column_type)
            )
        tables = []
        for table_name, row_count in table_rows:
            columns = columns_by_table.get(table_name, [])
            column_signature = hashlib.sha256(
                json.dumps(columns, ensure_ascii=False, sort_keys=True).encode()
            ).hexdigest()
            tables.append({
                "checkpoint_table_name": table_name,
                "table_rows": int(row_count),
                "column_signature": column_signature,
            })
        metadata_text = json.dumps(
            [(item["checkpoint_table_name"], item["column_signature"]) for item in tables],
            ensure_ascii=False,
            sort_keys=True,
        )
        return {
            "table_count": len(tables),
            "table_names": tuple(item["checkpoint_table_name"] for item in tables),
            "metadata_sha256": hashlib.sha256(metadata_text.encode()).hexdigest(),
            "tables": tuple(tables),
        }

    def _capture_checkpoint_identity(self) -> None:
        snapshot = self._read_checkpoint_snapshot()
        self.partial_target_rows = self._target_row_count()
        if not 0 < self.partial_target_rows < self.source_rows:
            raise RuntimeError(
                f"BC05 checkpoint did not preserve a partial target: target={self.database}.{self.table!s}, "
                f"partial_rows={self.partial_target_rows}, source_rows={self.source_rows}"
            )
        task_identity = f"BC05/{self.request_id}/{self.database}.{self.table}"
        self.checkpoint_identity_snapshot = {
            "task_identity": task_identity,
            "target_table": f"{self.database}.{self.table}",
            "source_sha256": self.source_sha256,
            "source_bundle_sha256": self.source_bundle_sha256,
            "schema_sha256": self.target_schema_sha256,
            "checkpoint_driver": "mysql",
            "checkpoint_host": self.checkpoint_host,
            "checkpoint_schema": self.checkpoint_schema,
            "checkpoint_generation": self.approved_checkpoint_generation,
            "checkpoint_table_count": snapshot["table_count"],
            "checkpoint_table_names": json.dumps(snapshot["table_names"]),
            "checkpoint_metadata_sha256": snapshot["metadata_sha256"],
            "config_sha256": self.lightning_config_sha256,
            "partial_target_rows": self.partial_target_rows,
            "checkpoint_state": "checkpointed",
        }
        self.checkpoint_table_manifest = snapshot["tables"]
        require_sql_success(
            self.env.execute_sql(
                f"UPDATE {self.database}.{self.schema_manifest_table} "
                f"SET config_sha256 = {sql_literal(self.lightning_config_sha256)} WHERE id = 1"
            ),
            "record BC05 Lightning config identity",
        )
        identity = self.checkpoint_identity_snapshot
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.checkpoint_identity_table} "
                "(id, task_identity, target_table, source_sha256, source_bundle_sha256, schema_sha256, "
                "checkpoint_driver, checkpoint_host, checkpoint_schema, checkpoint_generation, "
                "checkpoint_table_count, checkpoint_table_names, checkpoint_metadata_sha256, config_sha256, "
                "partial_target_rows, checkpoint_state) VALUES (1, "
                + ", ".join(sql_literal(identity[key]) for key in (
                    "task_identity", "target_table", "source_sha256", "source_bundle_sha256", "schema_sha256",
                    "checkpoint_driver", "checkpoint_host", "checkpoint_schema", "checkpoint_generation",
                    "checkpoint_table_count", "checkpoint_table_names", "checkpoint_metadata_sha256",
                    "config_sha256", "partial_target_rows", "checkpoint_state",
                ))
                + ")"
            ),
            f"seed BC05 checkpoint identity {self.database}.{self.checkpoint_identity_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.checkpoint_table_manifest_table} "
                "(checkpoint_table_name, table_rows, column_signature, checkpoint_state) VALUES "
                + ", ".join(
                    "(" + ", ".join(sql_literal(item[key]) for key in (
                        "checkpoint_table_name", "table_rows", "column_signature",
                    )) + ", 'checkpointed')"
                    for item in self.checkpoint_table_manifest
                )
            ),
            f"seed BC05 checkpoint table manifest {self.database}.{self.checkpoint_table_manifest_table}",
        )

    def _start_lightning(self) -> None:
        self._remove_container_if_present(self.lightning_container)
        self._write_lightning_config()
        self._run_host(
            [
                "docker", "run", "--detach", "--name", self.lightning_container,
                "--network", self.network,
                "--user", f"{os.getuid()}:{os.getgid()}",
                "--entrypoint", "/tidb-lightning",
                "--volume", f"{self.source_dir}:/data:ro",
                "--volume", f"{self.sort_dir}:/sort",
                "--volume", f"{self.probe_dir}:/probe",
                self.LIGHTNING_IMAGE,
                "--config", "/probe/lightning.toml",
            ],
            "start BC05 Lightning",
        )
        self.lightning_running = True

    def _wait_for_checkpoint(self) -> None:
        deadline = time.monotonic() + self.LIGHTNING_WAIT_SECONDS
        while time.monotonic() < deadline:
            checkpoint_table_count = self._checkpoint_row_count()
            target_rows = self._target_row_count()
            if target_rows >= self.source_rows:
                raise RuntimeError(
                    "BC05 Lightning completed before the controlled interruption; "
                    f"target={self.database}.{self.table!s}, target_rows={target_rows}, "
                    f"source_rows={self.source_rows}, checkpoint_tables={checkpoint_table_count}"
                )
            if checkpoint_table_count > 0 and 0 < target_rows < self.source_rows:
                if not self._container_running(self.lightning_container):
                    self.lightning_running = False
                    logs = self._container_logs(self.lightning_container)
                    raise RuntimeError(
                        "BC05 Lightning exited after exposing partial target rows: "
                        f"container={self.lightning_container!r}, target_rows={target_rows}, "
                        f"source_rows={self.source_rows}, logs={logs[-4000:]!r}"
                    )
                return
            if not self._container_running(self.lightning_container):
                self.lightning_running = False
                logs = self._container_logs(self.lightning_container)
                raise RuntimeError(
                    "BC05 Lightning exited before a reusable partial checkpoint was written: "
                    f"container={self.lightning_container!r}, checkpoint_tables={checkpoint_table_count}, "
                    f"target_rows={target_rows}, source_rows={self.source_rows}, logs={logs[-4000:]!r}"
                )
            time.sleep(1)
        raise RuntimeError(
            "BC05 Lightning did not expose a reusable partial checkpoint within the setup deadline: "
            f"container={self.lightning_container!r}, checkpoint_schema={self.checkpoint_schema!r}, "
            f"source_rows={self.source_rows}"
        )

    def _stop_lightning(self) -> None:
        if not self._container_running(self.lightning_container):
            raise RuntimeError(
                f"BC05 Lightning was not running at interruption point: container={self.lightning_container!r}"
            )
        self._run_host(
            ["docker", "kill", "--signal", "TERM", self.lightning_container],
            "interrupt BC05 Lightning with SIGTERM",
        )
        self._run_host(["docker", "wait", self.lightning_container], "wait for BC05 Lightning interruption")
        self.lightning_running = False
        logs = self._container_logs(self.lightning_container)
        if "the whole procedure completed" in logs.casefold():
            raise RuntimeError(
                "BC05 Lightning completed before the controlled interruption; the checkpoint fault was not created"
            )

    def _start_supervisor(self) -> None:
        self._raise_supervisor_error()
        if self.supervisor is not None and self.supervisor.is_alive():
            raise RuntimeError("BC05 Lightning resume supervisor is already running")
        self.supervisor_stop = threading.Event()
        self.supervisor_error = None
        self.supervisor_connection = self.env.open_workload_connection(
            "bc05-lightning-supervisor"
        )
        self.supervisor = threading.Thread(
            target=self._resume_after_scale_out,
            name=f"bc05-lightning-supervisor-{self.env.run_id}",
            daemon=True,
        )
        self.supervisor.start()

    def _load_persisted_checkpoint_identity(self) -> None:
        source_payload = json_object(
            self.env.execute_sql(
                f"SELECT file_name, byte_size, file_sha256, row_start, row_end, bundle_sha256 "
                f"FROM {self.database}.{self.source_manifest_table} ORDER BY file_name"
            ),
            "load BC05 source manifest",
        )
        source_rows = source_payload["result"]
        self.source_file_manifest = tuple(
            {
                "file_name": row[0], "byte_size": int(row[1]), "file_sha256": row[2],
                "row_start": int(row[3]), "row_end": int(row[4]),
            }
            for row in source_rows
        )
        if source_rows:
            bundle_values = {str(row[5]) for row in source_rows}
            if len(bundle_values) != 1:
                raise RuntimeError(
                    f"BC05 persisted source manifest has multiple bundle hashes: "
                    f"table={self.source_manifest_table!r}, hashes={sorted(bundle_values)!r}"
                )
            self.source_bundle_sha256 = next(iter(bundle_values))
        schema_payload = json_object(
            self.env.execute_sql(
                f"SELECT target_table, schema_sha256, index_signature, create_statement, config_sha256 "
                f"FROM {self.database}.{self.schema_manifest_table} WHERE id = 1"
            ),
            "load BC05 schema manifest",
        )
        schema_rows = schema_payload["result"]
        if len(schema_rows) != 1:
            raise RuntimeError(
                f"BC05 persisted schema manifest row shape is invalid: table={self.schema_manifest_table!r}, "
                f"rows={schema_rows!r}"
            )
        target_table, self.target_schema_sha256, self.target_index_signature, create_statement, self.lightning_config_sha256 = schema_rows[0]
        self.target_schema_snapshot = {
            "create_statement": create_statement,
            "schema_sha256": self.target_schema_sha256,
            "index_signature": self.target_index_signature,
        }
        identity_payload = json_object(
            self.env.execute_sql(
                f"SELECT task_identity, target_table, source_sha256, source_bundle_sha256, schema_sha256, "
                f"checkpoint_driver, checkpoint_host, checkpoint_schema, checkpoint_generation, "
                f"checkpoint_table_count, checkpoint_table_names, checkpoint_metadata_sha256, config_sha256, "
                f"partial_target_rows, checkpoint_state FROM {self.database}.{self.checkpoint_identity_table} WHERE id = 1"
            ),
            "load BC05 checkpoint identity",
        )
        identity_rows = identity_payload["result"]
        if len(identity_rows) != 1:
            raise RuntimeError(
                f"BC05 persisted checkpoint identity row shape is invalid: table={self.checkpoint_identity_table!r}, "
                f"rows={identity_rows!r}"
            )
        keys = (
            "task_identity", "target_table", "source_sha256", "source_bundle_sha256", "schema_sha256",
            "checkpoint_driver", "checkpoint_host", "checkpoint_schema", "checkpoint_generation",
            "checkpoint_table_count", "checkpoint_table_names", "checkpoint_metadata_sha256",
            "config_sha256", "partial_target_rows", "checkpoint_state",
        )
        self.checkpoint_identity_snapshot = dict(zip(keys, identity_rows[0], strict=True))
        self.source_sha256 = str(self.checkpoint_identity_snapshot["source_sha256"])
        self.partial_target_rows = int(self.checkpoint_identity_snapshot["partial_target_rows"])
        if target_table != f"{self.database}.{self.table}":
            raise RuntimeError(
                f"BC05 persisted schema target mismatch: expected={self.database}.{self.table!r}, "
                f"observed={target_table!r}"
            )

    def _source_manifest_matches(self) -> bool:
        current = self._read_source_file_manifest()
        if tuple(current) != tuple(self.source_file_manifest):
            return False
        bundle_text = "".join(
            f"{item['file_name']}\t{item['byte_size']}\t{item['file_sha256']}\t"
            f"{item['row_start']}\t{item['row_end']}\n"
            for item in current
        )
        return hashlib.sha256(bundle_text.encode()).hexdigest() == self.source_bundle_sha256

    def _persisted_identity_matches(self) -> bool:
        payload = json_object(
            self.env.execute_sql(
                f"SELECT task_identity, target_table, source_sha256, source_bundle_sha256, schema_sha256, "
                f"checkpoint_driver, checkpoint_host, checkpoint_schema, checkpoint_generation, "
                f"checkpoint_table_count, checkpoint_table_names, checkpoint_metadata_sha256, config_sha256, "
                f"partial_target_rows, checkpoint_state FROM {self.database}.{self.checkpoint_identity_table} WHERE id = 1"
            ),
            "verify BC05 persisted checkpoint identity",
        )
        rows = payload["result"]
        if len(rows) != 1:
            return False
        expected = self.checkpoint_identity_snapshot
        keys = (
            "task_identity", "target_table", "source_sha256", "source_bundle_sha256", "schema_sha256",
            "checkpoint_driver", "checkpoint_host", "checkpoint_schema", "checkpoint_generation",
            "checkpoint_table_count", "checkpoint_table_names", "checkpoint_metadata_sha256",
            "config_sha256", "partial_target_rows", "checkpoint_state",
        )
        return tuple(map(str, rows[0])) == tuple(str(expected[key]) for key in keys)

    def _protection_state_matches(self) -> bool:
        payload = json_object(
            self.env.execute_sql(
                f"SELECT physical_backend, pitr_state, ticdc_state, parallel_import_enabled, "
                f"empty_region_count, empty_region_limit, target_empty_at_start, observed_target "
                f"FROM {self.database}.{self.protection_state_table} WHERE id = 1"
            ),
            "verify BC05 physical import protection state",
        )
        rows = payload["result"]
        expected = ("local", "disabled", "no_changefeed", 0, 0, 1000, 1, f"{self.database}.{self.table}")
        return len(rows) == 1 and tuple(map(str, rows[0])) == tuple(map(str, expected))

    def _checkpoint_identity_matches(self) -> bool:
        current = self._read_checkpoint_snapshot()
        expected = self.checkpoint_identity_snapshot
        return (
            current["table_count"] == int(expected["checkpoint_table_count"])
            and tuple(current["table_names"]) == tuple(json.loads(expected["checkpoint_table_names"]))
            and current["metadata_sha256"] == expected["checkpoint_metadata_sha256"]
        )

    def _immutable_resume_state_is_ready(self) -> bool:
        return (
            bool(self.checkpoint_identity_snapshot)
            and self._source_manifest_matches()
            and self._read_target_schema_snapshot()["schema_sha256"] == self.target_schema_sha256
            and self._read_target_schema_snapshot()["index_signature"] == self.target_index_signature
            and self._persisted_identity_matches()
            and self._protection_state_matches()
            and self._checkpoint_identity_matches()
        )

    def _resume_after_scale_out(self) -> None:
        connection = self.supervisor_connection
        try:
            while not self.supervisor_stop.wait(1):
                if not self._resume_gate_is_ready(connection):
                    continue
                self._set_phase_with_connection(connection, "resuming")
                self._start_lightning()
                exit_code = self._run_host(
                    ["docker", "wait", self.lightning_container],
                    "wait for BC05 Lightning resume",
                ).strip()
                self.lightning_running = False
                if exit_code != "0":
                    raise RuntimeError(
                        f"BC05 Lightning resume failed: container={self.lightning_container!r}, exit_code={exit_code!r}, "
                        f"logs={self._container_logs(self.lightning_container)[-4000:]!r}"
                    )
                self._set_checkpoint_state_with_connection(connection, "completed")
                self._set_phase_with_connection(connection, "completed")
                return
        except Exception as exc:
            self.supervisor_error = exc
            try:
                self._set_phase_with_connection(connection, "failed")
            except Exception as phase_error:
                self.supervisor_error = RuntimeError(
                    f"BC05 Lightning resume failed and failed to persist phase=failed: "
                    f"resume_error={exc!r}, phase_error={phase_error!r}"
                )
        finally:
            connection.close()
            self.supervisor_connection = None

    def _resume_gate_is_ready(self, connection) -> bool:
        payload = json_object(
            self._execute_sql_on_connection(
                connection,
                f"SELECT r.request_state, r.plan_epoch, r.checkpoint_generation, "
                f"g.gate_state, g.approved_service, g.approved_epoch, g.checkpoint_schema, "
                f"g.checkpoint_source_sha256, g.approved_fence_token, "
                f"c.node_name, c.plan_epoch, c.checkpoint_generation, c.reservation_token, "
                f"c.reservation_state, m.source_sha256, m.fence_token, m.reuse_state, m.lease_state, "
                f"l.reservation_token, l.fence_token, l.renewed_at, m.observed_at, control.source_sha256 "
                f"FROM {self.database}.{self.request_table} r "
                f"JOIN {self.database}.{self.resume_gate_table} g "
                "ON g.request_id = r.request_id AND g.id = 1 "
                f"LEFT JOIN {self.database}.{self.capacity_reservation_table} c "
                "ON c.request_id = r.request_id AND c.node_name = g.approved_service "
                "AND c.checkpoint_generation = r.checkpoint_generation "
                f"LEFT JOIN {self.database}.{self.checkpoint_manifest_table} m "
                "ON m.node_name = g.approved_service "
                "AND m.checkpoint_schema = r.checkpoint_schema "
                "AND m.checkpoint_generation = r.checkpoint_generation "
                f"LEFT JOIN {self.database}.{self.lease_journal_table} l "
                "ON l.request_id = r.request_id "
                "AND l.node_name = g.approved_service "
                "AND l.plan_epoch = r.plan_epoch "
                "AND l.checkpoint_generation = r.checkpoint_generation "
                "AND l.lease_state = 'current' "
                f"JOIN {self.database}.{self.control_table} control ON control.id = 1 "
                "WHERE r.id = 1"
            ),
            "read BC05 Lightning admission state",
        )
        rows = payload["result"]
        if len(rows) != 1 or len(rows[0]) != 23:
            raise RuntimeError(
                f"BC05 admission state row shape is invalid: request_table={self.request_table!r}, "
                f"reservation_table={self.capacity_reservation_table!r}, gate_table={self.resume_gate_table!r}, "
                f"rows={rows!r}"
            )
        (
            request_state,
            request_epoch,
            request_generation,
            gate_state,
            approved_service,
            approved_epoch,
            checkpoint_schema,
            gate_source_sha256,
            gate_fence_token,
            reservation_service,
            reservation_epoch,
            reservation_generation,
            reservation_token,
            reservation_state,
            manifest_source_sha256,
            manifest_fence_token,
            manifest_reuse_state,
            manifest_lease_state,
            journal_reservation_token,
            journal_fence_token,
            journal_renewed_at,
            manifest_observed_at,
            control_source_sha256,
        ) = rows[0]
        admission_ready = (
            request_state == "APPROVED"
            and int(request_epoch) == self.approved_plan_epoch
            and int(request_generation) == self.approved_checkpoint_generation
            and gate_state == "approved"
            and approved_service == self.approved_tikv_service
            and int(approved_epoch) == self.approved_plan_epoch
            and checkpoint_schema == self.checkpoint_schema
            and gate_source_sha256 == manifest_source_sha256 == control_source_sha256
            and gate_fence_token == manifest_fence_token == self.approved_fence_token
            and manifest_reuse_state == "reusable"
            and manifest_lease_state == "current"
            and journal_reservation_token == reservation_token
            and journal_fence_token == manifest_fence_token
            and journal_renewed_at is not None
            and manifest_observed_at is not None
            and journal_renewed_at > manifest_observed_at
            and reservation_service == self.approved_tikv_service
            and int(reservation_epoch) == self.approved_plan_epoch
            and int(reservation_generation) == self.approved_checkpoint_generation
            and reservation_token == self.approved_reservation_token
            and reservation_state == "committed"
            and self.approved_tikv_service in self.deployment.active_tikv_services
            and len(self.deployment.active_tikv_services) == self.target_tikv_count
        )
        if not admission_ready:
            return False
        if not self._immutable_resume_state_is_ready():
            return False
        stores = self.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
        selected_stores = tuple(
            item
            for item in stores
            if item["store"]["address"] == f"{self.approved_tikv_service}:20160"
        )
        return len(selected_stores) == 1 and selected_stores[0]["store"]["state_name"] == "Up"

    def _execute_sql_on_connection(self, connection, sql: str) -> dict:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = [list(row) for row in cursor.fetchall()]
                return {
                    "status": "success",
                    "columns": columns,
                    "result": rows,
                    "row_count": len(rows),
                }
            return {
                "status": "success",
                "columns": [],
                "result": [],
                "row_count": cursor.rowcount,
            }

    def _stop_supervisor(self):
        if self.supervisor is None:
            return self.supervisor_error
        self.supervisor_stop.set()
        self.supervisor.join(timeout=30)
        if self.supervisor.is_alive():
            raise RuntimeError(
                f"BC05 Lightning supervisor did not stop: thread={self.supervisor.name!r}"
            )
        self.supervisor = None
        return self.supervisor_error

    def _stop_lightning_if_running(self) -> None:
        if not self.lightning_running:
            return
        self._run_host(
            ["docker", "kill", "--signal", "TERM", self.lightning_container],
            "stop running BC05 Lightning",
        )
        self._run_host(["docker", "wait", self.lightning_container], "wait for BC05 Lightning stop")
        self.lightning_running = False

    def _set_phase(self, phase: str) -> None:
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.database}.{self.control_table} "
                f"(id, phase, source_rows, source_sha256, checkpoint_schema) VALUES "
                f"(1, '{phase}', {self.source_rows}, '{self.source_sha256}', '{self.checkpoint_schema}') "
                "ON DUPLICATE KEY UPDATE phase=VALUES(phase), updated_at=CURRENT_TIMESTAMP"
            ),
            f"set BC05 control phase {phase}",
        )

    def _set_phase_with_connection(self, connection, phase: str) -> None:
        require_sql_success(
            self._execute_sql_on_connection(
                connection,
                f"INSERT INTO {self.database}.{self.control_table} "
                f"(id, phase, source_rows, source_sha256, checkpoint_schema) VALUES "
                f"(1, '{phase}', {self.source_rows}, '{self.source_sha256}', '{self.checkpoint_schema}') "
                "ON DUPLICATE KEY UPDATE phase=VALUES(phase), updated_at=CURRENT_TIMESTAMP",
            ),
            f"set BC05 control phase {phase}",
        )

    def _set_checkpoint_state_with_connection(self, connection, state: str) -> None:
        require_sql_success(
            self._execute_sql_on_connection(
                connection,
                f"UPDATE {self.database}.{self.checkpoint_identity_table} "
                f"SET checkpoint_state = {sql_literal(state)} WHERE id = 1",
            ),
            f"set BC05 checkpoint state {state}",
        )
        require_sql_success(
            self._execute_sql_on_connection(
                connection,
                f"UPDATE {self.database}.{self.checkpoint_table_manifest_table} "
                f"SET checkpoint_state = {sql_literal(state)}",
            ),
            f"set BC05 checkpoint table state {state}",
        )

    def _assert_phase(self, expected: str) -> None:
        payload = json_object(
            self.env.execute_sql(
                f"SELECT phase FROM {self.database}.{self.control_table} WHERE id = 1"
            ),
            "read BC05 control phase",
        )
        rows = payload["result"]
        if rows != [[expected]]:
            raise RuntimeError(
                f"BC05 control phase mismatch: expected={expected!r}, observed={rows!r}"
            )

    def _checkpoint_row_count(self) -> int:
        result = subprocess.run(
            [
                "docker", "exec", self.checkpoint_container, "mysql", "-N", "-B", "-uroot",
                "-e",
                f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{self.checkpoint_schema}'",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"BC05 checkpoint query failed: container={self.checkpoint_container!r}, "
                f"returncode={result.returncode}, stdout={result.stdout.strip()!r}, "
                f"stderr={result.stderr.strip()!r}"
            )
        return int(result.stdout.strip())

    def _target_row_count(self) -> int:
        payload = json_object(
            self.env.execute_sql(f"SELECT COUNT(*) FROM {self.database}.{self.table}"),
            "read BC05 target row count",
        )
        rows = payload["result"]
        if len(rows) != 1 or len(rows[0]) != 1:
            raise RuntimeError(
                f"BC05 target row-count shape is invalid: target={self.database}.{self.table!s}, "
                f"rows={rows!r}"
            )
        return int(rows[0][0])

    def _container_running(self, name: str) -> bool:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Running}}", name],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"BC05 Lightning container inspection failed: container={name!r}, "
                f"returncode={result.returncode}, stdout={result.stdout.strip()!r}, "
                f"stderr={result.stderr.strip()!r}"
            )
        state = result.stdout.strip()
        if state not in {"true", "false"}:
            raise RuntimeError(
                f"BC05 Lightning container inspection returned invalid state: "
                f"container={name!r}, state={state!r}"
            )
        return state == "true"

    def _container_logs(self, name: str) -> str:
        result = subprocess.run(["docker", "logs", name], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"Cannot read BC05 container logs: container={name!r}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        return f"{result.stdout}\n{result.stderr}"

    def _remove_container_if_present(self, name: str) -> None:
        result = subprocess.run(["docker", "inspect", name], capture_output=True, text=True)
        if result.returncode == 0:
            self._remove_container(name)
            return
        if "no such object" not in result.stderr.lower():
            raise RuntimeError(
                f"Cannot inspect BC05 container: container={name!r}, "
                f"returncode={result.returncode}, stdout={result.stdout.strip()!r}, "
                f"stderr={result.stderr.strip()!r}"
            )

    def _raise_supervisor_error(self) -> None:
        if self.supervisor_error is not None:
            raise RuntimeError(
                f"BC05 Lightning resume supervisor failed: {self.supervisor_error}"
            ) from self.supervisor_error

    def _remove_container(self, name: str) -> None:
        self._run_host(["docker", "rm", "--force", name], f"remove BC05 container {name}")

    @staticmethod
    def _run_host(command: list[str], operation: str) -> str:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"{operation} failed: command={command!r}, returncode={result.returncode}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        return result.stdout
