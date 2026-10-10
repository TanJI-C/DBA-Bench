import os

import re

import shutil

import subprocess

import tempfile

import threading

from collections.abc import Mapping

from pathlib import Path

import pymysql

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    join_thread,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.resource_governance.backup_slo import (
    TidbResourceGovernanceBrSloEvaluatorCase,
    TidbResourceGovernanceBrSloStorageEnvelopeEvaluatorCase,
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


_RG03_DATABASE = "benchops"
_RG03_BUSINESS_TABLE = "orders"
_RG03_CUSTOMERS_TABLE = "customers"
_RG03_INVENTORY_TABLE = "inventory"
_RG03_NUMBERS_TABLE = "numbers"
_RG03_JOB_TABLE = "maintenance_jobs"
_RG03_JOB_ID = "maintenance_window_current"
_RG03_BASELINE_CONFIG_TABLE = "config_baseline"
_RG03_BACKUP_CATALOG = "maintenance_catalog"
_RG03_RESTORE_QUEUE = "recovery_queue"
_RG03_CAPACITY_SNAPSHOT = "store_capacity"
_RG03_CHECKSUM_AUDIT = "integrity_audit"
_RG03_ROW_COUNT = 100_000
_RG03_EXPECTED_INTEGRITY = (100_000, 5_000_050_000, 2_006_296_466)
_RG03_ARTIFACT_ROOT = str(Path(tempfile.gettempdir()) / "aiopsbench-rg03-artifacts")
_RG03_STORAGE_ARTIFACT_ROOT = str(Path(tempfile.gettempdir()) / "aiopsbench-rg03-storage-envelope-artifacts")
_RG03_BR_IMAGE = "docker.m.daocloud.io/pingcap/br:v8.1.0"


def _rg03_workload() -> BackgroundWorkloadSpec:
    profiles = (
        WorkloadProfile(
            name="checkout_point_lookup",
            sql=(
                f"SELECT order_id, tenant_id, status, amount FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} "
                "WHERE order_id = MOD(CAST(UNIX_TIMESTAMP(NOW()) AS UNSIGNED), 100000) + 1"
            ),
            qps=1.7,
            tier="OLTP_CORE",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="checkout_recent_orders",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} "
                "WHERE order_id > 97000 AND status IN ('PAID', 'SHIPPED')"
            ),
            qps=0.7,
            tier="OLTP_CORE",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="tenant_dashboard_rollup",
            sql=(
                f"SELECT tenant_id, status, COUNT(*), COALESCE(SUM(amount), 0) "
                f"FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} "
                "WHERE order_id > 50000 GROUP BY tenant_id, status ORDER BY tenant_id, status"
            ),
            qps=0.28,
            tier="OLAP_NEARLINE",
            application_name="tenant-dashboard",
        ),
        WorkloadProfile(
            name="settlement_export_preview",
            sql=(
                f"SELECT tenant_id, COUNT(*), COALESCE(SUM(amount), 0) "
                f"FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} "
                "WHERE status = 'PAID' GROUP BY tenant_id ORDER BY SUM(amount) DESC LIMIT 20"
            ),
            qps=0.25,
            tier="OLAP_NEARLINE",
            application_name="settlement-export",
        ),
        WorkloadProfile(
            name="fraud_window_scan",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(order_id), 0) FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} "
                "WHERE status = 'REVIEW' AND amount > 700.00"
            ),
            qps=0.32,
            tier="RISK_SCAN",
            application_name="fraud-scoring",
        ),
        WorkloadProfile(
            name="order_detail_join",
            sql=(
                f"SELECT o.order_id, c.customer_tier, i.stock_level "
                f"FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} o "
                f"JOIN {_RG03_DATABASE}.{_RG03_CUSTOMERS_TABLE} c ON c.customer_id = o.customer_id "
                f"JOIN {_RG03_DATABASE}.{_RG03_INVENTORY_TABLE} i ON i.sku = o.sku "
                "WHERE o.order_id = MOD(CAST(UNIX_TIMESTAMP(NOW()) AS UNSIGNED), 100000) + 1"
            ),
            qps=0.9,
            tier="OLTP_CORE",
            application_name="order-detail-api",
        ),
        WorkloadProfile(
            name="inventory_reconciliation",
            sql=(
                f"SELECT sku, SUM(stock_level), MAX(updated_at) FROM {_RG03_DATABASE}.{_RG03_INVENTORY_TABLE} "
                "GROUP BY sku ORDER BY sku LIMIT 100"
            ),
            qps=0.18,
            tier="MAINTENANCE",
            application_name="inventory-reconciliation",
        ),
        WorkloadProfile(
            name="customer_segment_preview",
            sql=(
                f"SELECT customer_tier, COUNT(*), MIN(customer_id), MAX(customer_id) "
                f"FROM {_RG03_DATABASE}.{_RG03_CUSTOMERS_TABLE} GROUP BY customer_tier"
            ),
            qps=0.22,
            tier="OLAP_NEARLINE",
            application_name="customer-segmentation",
        ),
        WorkloadProfile(
            name="business_truth_probe",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
                f"COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, status, amount, payload))), 0) "
                f"FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE}"
            ),
            qps=0.16,
            tier="VALIDATION",
            application_name="business-integrity-monitor",
        ),
        WorkloadProfile(
            name="table_status_probe",
            sql=f"SHOW TABLE STATUS FROM {_RG03_DATABASE} LIKE '{_RG03_BUSINESS_TABLE}'",
            qps=0.35,
            tier="OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="maintenance_config_probe",
            sql=(
                "SHOW CONFIG WHERE type = 'tikv' "
                "AND name IN ('backup.enable-auto-tune', 'backup.num-threads')"
            ),
            qps=0.34,
            tier="OBSERVABILITY",
            application_name="maintenance-controller",
        ),
        WorkloadProfile(
            name="cluster_config_decoy",
            sql="SHOW CONFIG WHERE type = 'tikv' AND name LIKE 'raftstore.%' LIMIT 20",
            qps=0.23,
            tier="OBSERVABILITY",
            application_name="capacity-observer",
        ),
        WorkloadProfile(
            name="store_status_probe",
            sql="SELECT * FROM INFORMATION_SCHEMA.CLUSTER_INFO ORDER BY TYPE, INSTANCE",
            qps=0.19,
            tier="OBSERVABILITY",
            application_name="cluster-observer",
        ),
        WorkloadProfile(
            name="maintenance_job_history_rollup",
            sql=(
                f"SELECT state, checksum_status, COUNT(*), COALESCE(SUM(ranges_succeeded), 0) "
                f"FROM {_RG03_DATABASE}.{_RG03_JOB_TABLE} GROUP BY state, checksum_status "
                "ORDER BY state, checksum_status"
            ),
            qps=0.18,
            tier="OBSERVABILITY_DECOY",
            application_name="maintenance-job-history",
        ),
        WorkloadProfile(
            name="maintenance_job_recent_probe",
            sql=(
                f"SELECT job_id, state, total_ranges, ranges_succeeded, ranges_failed, checksum_status, "
                f"storage_path, started_at FROM {_RG03_DATABASE}.{_RG03_JOB_TABLE} "
                "ORDER BY started_at DESC, job_id DESC LIMIT 8"
            ),
            qps=0.15,
            tier="OBSERVABILITY_DECOY",
            application_name="maintenance-job-console",
        ),
        WorkloadProfile(
            name="maintenance_catalog_rollup",
            sql=(
                f"SELECT backup_type, state, storage_backend, COUNT(*), COALESCE(SUM(size_bytes), 0) "
                f"FROM {_RG03_DATABASE}.{_RG03_BACKUP_CATALOG} "
                "GROUP BY backup_type, state, storage_backend ORDER BY backup_type, state"
            ),
            qps=0.17,
            tier="RESOURCE_DECOY",
            application_name="maintenance-catalog-dashboard",
        ),
        WorkloadProfile(
            name="maintenance_catalog_recent",
            sql=(
                f"SELECT backup_id, backup_type, state, size_bytes, created_at "
                f"FROM {_RG03_DATABASE}.{_RG03_BACKUP_CATALOG} "
                "ORDER BY created_at DESC, backup_id DESC LIMIT 20"
            ),
            qps=0.13,
            tier="RESOURCE_DECOY",
            application_name="maintenance-retention-auditor",
        ),
        WorkloadProfile(
            name="recovery_queue_rollup",
            sql=(
                f"SELECT queue_class, state, COUNT(*), MAX(wait_seconds), COALESCE(SUM(payload_bytes), 0) "
                f"FROM {_RG03_DATABASE}.{_RG03_RESTORE_QUEUE} "
                "GROUP BY queue_class, state ORDER BY queue_class, state"
            ),
            qps=0.16,
            tier="RESOURCE_DECOY",
            application_name="recovery-capacity-controller",
        ),
        WorkloadProfile(
            name="recovery_queue_critical",
            sql=(
                f"SELECT request_id, queue_class, state, priority, wait_seconds "
                f"FROM {_RG03_DATABASE}.{_RG03_RESTORE_QUEUE} "
                "WHERE state IN ('WAITING', 'RUNNING') ORDER BY priority DESC, wait_seconds DESC LIMIT 12"
            ),
            qps=0.12,
            tier="RESOURCE_DECOY",
            application_name="recovery-slo-monitor",
        ),
        WorkloadProfile(
            name="store_capacity_headroom_probe",
            sql=(
                f"SELECT store_id, zone, total_bytes, used_bytes, reserved_bytes, headroom_pct "
                f"FROM {_RG03_DATABASE}.{_RG03_CAPACITY_SNAPSHOT} "
                "ORDER BY headroom_pct ASC, store_id"
            ),
            qps=0.13,
            tier="RESOURCE_DECOY",
            application_name="capacity-headroom-monitor",
        ),
        WorkloadProfile(
            name="store_capacity_reservation_rollup",
            sql=(
                f"SELECT zone, COUNT(*), COALESCE(SUM(reserved_bytes), 0), "
                f"MIN(headroom_pct), MAX(headroom_pct) FROM {_RG03_DATABASE}.{_RG03_CAPACITY_SNAPSHOT} "
                "GROUP BY zone ORDER BY zone"
            ),
            qps=0.11,
            tier="RESOURCE_DECOY",
            application_name="capacity-reservation-auditor",
        ),
        WorkloadProfile(
            name="integrity_audit_rollup",
            sql=(
                f"SELECT check_state, COUNT(*), COALESCE(SUM(checksum_value), 0) "
                f"FROM {_RG03_DATABASE}.{_RG03_CHECKSUM_AUDIT} "
                "GROUP BY check_state ORDER BY check_state"
            ),
            qps=0.11,
            tier="VALIDATION_DECOY",
            application_name="integrity-audit-dashboard",
        ),
        WorkloadProfile(
            name="integrity_pending_probe",
            sql=(
                f"SELECT object_name, check_state, checked_at FROM {_RG03_DATABASE}.{_RG03_CHECKSUM_AUDIT} "
                "WHERE check_state <> 'PASSED' ORDER BY checked_at, object_name"
            ),
            qps=0.09,
            tier="VALIDATION_DECOY",
            application_name="integrity-audit-alert",
        ),
        WorkloadProfile(
            name="scheduler_config_decoy",
            sql=(
                "SHOW CONFIG WHERE type = 'tikv' "
                "AND (name LIKE 'raftstore.%' OR name LIKE 'coprocessor.%') LIMIT 40"
            ),
            qps=0.18,
            tier="OBSERVABILITY_DECOY",
            application_name="scheduler-budget-observer",
        ),
        WorkloadProfile(
            name="storage_config_decoy",
            sql=(
                "SHOW CONFIG WHERE type = 'tikv' "
                "AND name IN ('storage.reserve-space', 'storage.block-cache.capacity', "
                "'rocksdb.max-open-files', 'raftdb.max-open-files')"
            ),
            qps=0.16,
            tier="OBSERVABILITY_DECOY",
            application_name="storage-budget-observer",
        ),
        WorkloadProfile(
            name="missing_catalog_cache_noise",
            sql=f"SELECT COUNT(*) FROM {_RG03_DATABASE}.maintenance_catalog_cache_missing",
            qps=0.20,
            tier="LOG_NOISE",
            application_name="maintenance-catalog-refresher",
        ),
        WorkloadProfile(
            name="missing_capacity_cache_noise",
            sql=f"SELECT COUNT(*) FROM {_RG03_DATABASE}.store_capacity_cache_missing",
            qps=0.18,
            tier="LOG_NOISE",
            application_name="capacity-dashboard",
        ),
        WorkloadProfile(
            name="missing_recovery_cache_noise",
            sql=f"SELECT COUNT(*) FROM {_RG03_DATABASE}.recovery_queue_missing",
            qps=0.16,
            tier="LOG_NOISE",
            application_name="recovery-monitor",
        ),
        WorkloadProfile(
            name="missing_manifest_cache_noise",
            sql=f"SELECT COUNT(*) FROM {_RG03_DATABASE}.maintenance_manifest_cache_missing",
            qps=0.14,
            tier="LOG_NOISE",
            application_name="maintenance-manifest-refresher",
        ),
        WorkloadProfile(
            name="missing_slo_budget_noise",
            sql=f"SELECT COUNT(*) FROM {_RG03_DATABASE}.maintenance_slo_budget_cache_missing",
            qps=0.14,
            tier="LOG_NOISE",
            application_name="slo-budget-controller",
        ),
        WorkloadProfile(
            name="order_payload_length_scan",
            sql=(
                f"SELECT status, SUM(CHAR_LENGTH(payload)) FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} "
                "GROUP BY status ORDER BY status"
            ),
            qps=0.18,
            tier="OLAP_NEARLINE",
            application_name="order-audit",
        ),
        WorkloadProfile(
            name="customer_order_join_rollup",
            sql=(
                f"SELECT c.customer_tier, COUNT(o.order_id), COALESCE(SUM(o.amount), 0) "
                f"FROM {_RG03_DATABASE}.{_RG03_CUSTOMERS_TABLE} c "
                f"JOIN {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} o ON o.customer_id = c.customer_id "
                "GROUP BY c.customer_tier ORDER BY c.customer_tier"
            ),
            qps=0.14,
            tier="OLAP_NEARLINE",
            application_name="revenue-dashboard",
        ),
        WorkloadProfile(
            name="sku_order_rollup",
            sql=(
                f"SELECT sku, COUNT(*), COALESCE(SUM(amount), 0) FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} "
                "GROUP BY sku ORDER BY COUNT(*) DESC LIMIT 50"
            ),
            qps=0.16,
            tier="OLAP_NEARLINE",
            application_name="product-dashboard",
        ),
        WorkloadProfile(
            name="shipping_wave_rollup",
            sql=(
                f"SELECT tenant_id, status, COUNT(*), COALESCE(SUM(amount), 0) "
                f"FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} "
                "WHERE tenant_id = MOD(CAST(UNIX_TIMESTAMP(NOW()) AS UNSIGNED), 64) "
                "AND status IN ('NEW', 'SHIPPED') GROUP BY tenant_id, status "
                "ORDER BY tenant_id, status"
            ),
            qps=0.06,
            tier="OLAP_NEARLINE",
            application_name="shipping-wave-planner",
        ),
        WorkloadProfile(
            name="refund_reconciliation",
            sql=(
                f"SELECT status, COUNT(*), COALESCE(SUM(amount), 0), MIN(order_id), MAX(order_id) "
                f"FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} "
                "WHERE order_id > 99000 AND status IN ('CANCELLED', 'REVIEW') "
                "GROUP BY status ORDER BY status"
            ),
            qps=0.06,
            tier="OLAP_NEARLINE",
            application_name="refund-reconciliation",
        ),
        WorkloadProfile(
            name="customer_ltv_preview",
            sql=(
                f"SELECT c.customer_tier, COUNT(o.order_id), COALESCE(SUM(o.amount), 0) "
                f"FROM {_RG03_DATABASE}.{_RG03_CUSTOMERS_TABLE} c "
                f"JOIN {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} o ON o.customer_id = c.customer_id "
                "WHERE c.customer_id <= 100 AND o.order_id > 99000 "
                "GROUP BY c.customer_tier ORDER BY SUM(o.amount) DESC"
            ),
            qps=0.05,
            tier="OLAP_NEARLINE",
            application_name="customer-lifetime-value",
        ),
        WorkloadProfile(
            name="inventory_risk_scan",
            sql=(
                f"SELECT i.sku, i.stock_level, COUNT(o.order_id), COALESCE(SUM(o.amount), 0) "
                f"FROM {_RG03_DATABASE}.{_RG03_INVENTORY_TABLE} i "
                f"LEFT JOIN {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE} o ON o.sku = i.sku "
                "WHERE i.sku <= 100 AND i.stock_level < 500 GROUP BY i.sku, i.stock_level "
                "ORDER BY COUNT(o.order_id) DESC, i.sku LIMIT 100"
            ),
            qps=0.05,
            tier="RISK_SCAN",
            application_name="inventory-risk-planner",
        ),
    )
    return BackgroundWorkloadSpec(
        profiles=profiles,
        worker_count=8,
        seed=20260802,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=18,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceBrSloCase(TiDBScenarioCase):
    database: str
    business_table: str
    job_table: str
    job_id: str
    baseline_config_table: str
    row_count: int
    expected_business_integrity: tuple[int, int, int]
    business_query: str
    slo_p95_ms: float
    max_backup_bytes: int
    artifact_root: str
    br_image: str
    initial_br_concurrency: int
    initial_tikv_backup_threads: int
    reference_path: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceBrSloForFrontendSloScenarioCase(TidbResourceGovernanceBrSloCase):
    pass


_RG03_CASE = TidbResourceGovernanceBrSloForFrontendSloScenarioCase(
    case_id="br_backup_frontend_slo",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "kept the maintenance budget bounded while preserving foreground latency, storage safety, and data integrity"
            ],
            "verification": [
                "the maintenance artifact completed with all ranges and checksum 100%",
                "the local artifact exists and remains within the space budget",
                "foreground query p95 recovered below the stated SLO",
                "business table integrity is unchanged"
            ]
        },
        "summary": "The live maintenance window was governed with a bounded official resource budget while preserving SLO, space safety, and business truth."
    },
    case_no=0,
    evaluator=TidbResourceGovernanceBrSloEvaluatorCase,
    title="Govern a live maintenance window without violating foreground SLO or data integrity.",
    alert=(
        "P1 资源治理告警：夜间数据维护任务正在运行但尚未完成，checkout 前台 p95 超过 35 ms SLO。"
        "请在不修改业务数据、不关闭空间安全检查且不重启集群的前提下，"
        "找到可持续的维护资源预算，让任务完成并验证 checksum、前台 SLO 和业务真值。"
    ),
    initial_state={
        "status": "maintenance_running",
        "foreground_slo": "violated",
        "completion": "pending",
        "space_check": "enabled",
    },
    expected_target={
        "status": "maintenance_succeeded",
        "foreground_slo": "met",
        "completion": "100%",
        "space_check": "enabled",
        "business_integrity": "unchanged",
    },
    background_workload=_rg03_workload(),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=180,
        tikv_shared_volume_root=_RG03_ARTIFACT_ROOT,
    ),
    database=_RG03_DATABASE,
    business_table=_RG03_BUSINESS_TABLE,
    job_table=_RG03_JOB_TABLE,
    job_id=_RG03_JOB_ID,
    baseline_config_table=_RG03_BASELINE_CONFIG_TABLE,
    row_count=_RG03_ROW_COUNT,
    expected_business_integrity=_RG03_EXPECTED_INTEGRITY,
    business_query=(
        f"SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
        f"COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, status, amount, payload))), 0) "
        f"FROM {_RG03_DATABASE}.{_RG03_BUSINESS_TABLE}"
    ),
    slo_p95_ms=35.0,
    max_backup_bytes=8 * 1024 * 1024 * 1024,
    artifact_root=_RG03_ARTIFACT_ROOT,
    br_image=_RG03_BR_IMAGE,
    initial_br_concurrency=16,
    initial_tikv_backup_threads=1,
    reference_path=(
        "foreground p95 and maintenance completion are both outside the SLO contract",
        "maintenance pressure is shared with foreground reads and is not explained by one SQL fingerprint",
        "live maintenance progress must be separated from historical catalog, recovery-queue and capacity candidates",
        "maintenance progress, TiKV resource settings, disk I/O, space headroom and noisy business queries must be correlated",
        "select a bounded official resource budget and retain automatic protection before the maintenance window closes",
        "maintenance artifact/checksum, foreground SLO, space guard and business truth all pass",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.942143,
        reference_run_ids=(
            "reference-114__tidb_resource_governance_br_slo_adaptive_throttling__br_backup_frontend_slo__mock__r001",
            "reference-113__tidb_resource_governance_br_slo_adaptive_throttling__br_backup_frontend_slo__llm__r001",
        ),
    ),
)

_RG03_STORAGE_CASE = replace(
    _RG03_CASE,
    case_id="br_backup_storage_envelope",
    case_no=1,
    evaluator=TidbResourceGovernanceBrSloStorageEnvelopeEvaluatorCase,
    title="Complete the live backup inside a visible storage envelope while preserving frontend SLO.",
    alert=(
        "P1 resource-governance alert: the live maintenance backup is competing with checkout reads and "
        "its artifact must stay within the published local-store envelope. Correlate maintenance progress, "
        "TiKV backup settings, disk headroom, frontend latency, and business integrity. Keep automatic "
        "space protection enabled, use a bounded official budget, and do not restart the cluster or mutate data."
    ),
    initial_state={
        "status": "maintenance_running",
        "foreground_slo": "violated",
        "completion": "pending",
        "space_envelope": "6 GiB maximum artifact size",
        "space_check": "enabled",
    },
    expected_target={
        "status": "maintenance_succeeded",
        "foreground_slo": "met",
        "completion": "100%",
        "artifact_bytes": "<= 6 GiB",
        "space_check": "enabled",
        "business_integrity": "unchanged",
    },
    slo_p95_ms=40.0,
    max_backup_bytes=6 * 1024 * 1024 * 1024,
    artifact_root=_RG03_STORAGE_ARTIFACT_ROOT,
    runtime=replace(
        _RG03_CASE.runtime,
        tikv_shared_volume_root=_RG03_STORAGE_ARTIFACT_ROOT,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.304348,
        reference_run_ids=(
            "tidb-reference-6__tidb_resource_governance_br_slo_adaptive_throttling__"
            "br_backup_storage_envelope__mock__r001",
        ),
    ),
)


class TidbResourceGovernanceBrSloInjector(BaseFaultInjector):
    """Run a real BR backup while the foreground workload remains active."""

    def __init__(self):
        self.database = None
        self.business_table = None
        self.job_table = None
        self.job_id = None
        self.baseline_config_table = None
        self.row_count = None
        self.expected_business_integrity = None
        self.artifact_root = None
        self._storage_uri = None
        self.br_image = None
        self.initial_br_concurrency = None
        self.initial_tikv_backup_threads = None
        self._br_process = None
        self._br_thread = None
        self._br_stop = None
        self._br_log_handle = None
        self._br_log_path = None
        self._snapshot_path = None
        self._monitor_error = None
        self._restore_threads = None
        self._restore_auto_tune = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.run_id)
        self._create_schema(context.env)
        self._capture_baseline_config(context.env)
        self._set_backup_config(context.env, auto_tune="false", threads=self.initial_tikv_backup_threads)
        self._prepare_artifact_directory()
        self._insert_job(context.env, "STARTING")
        self._start_br(context)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.run_id)
        self._load_baseline_config(context.env)
        self._verify_business_integrity(context.env)
        self._prepare_artifact_directory(reset=True)
        self._reset_job(context.env)
        self._set_backup_config(context.env, auto_tune="false", threads=self.initial_tikv_backup_threads)
        self._start_br(context)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        if self._monitor_error is not None:
            raise RuntimeError(
                "RG03 BR monitor failed before observability preparation: "
                f"run_id={context.run_id!r}, error={self._monitor_error!r}"
            ) from self._monitor_error
        if self._br_process is None:
            raise RuntimeError(f"RG03 BR process was not started: run_id={context.run_id!r}")
        job = self._job(context.env)
        if job["state"] not in {"STARTING", "RUNNING"}:
            raise RuntimeError(
                "RG03 BR job was not running at agent handoff: "
                f"run_id={context.run_id!r}, job={job!r}"
            )
        return {
            "business_integrity": self.expected_business_integrity,
            "br_job": job,
            "br_artifact": {
                "host_path": str(self._snapshot_path),
                "storage_uri": self._storage_uri,
            },
            "br_log_path": str(self._br_log_path),
            "initial_backup_config": {
                "backup.enable-auto-tune": "false",
                "backup.num-threads": self.initial_tikv_backup_threads,
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_br(context.env, mark_paused=True)

    def recover(self, context: FaultLifecycleContext) -> None:
        if self._restore_auto_tune is None or self._restore_threads is None:
            raise RuntimeError(
                "RG03 cannot recover without the persisted pre-fault TiKV backup configuration: "
                f"run_id={context.run_id!r}, database={self.database!r}, "
                f"baseline_config_table={self.baseline_config_table!r}"
            )
        self._stop_br(context.env, mark_paused=False)
        self._set_backup_config(
            context.env,
            auto_tune=self._restore_auto_tune,
            threads=self._restore_threads,
        )
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.database}"),
            f"RG03 drop owned database {self.database}",
        )
        if self.artifact_root is not None and self.artifact_root.exists():
            self._normalize_artifact_permissions(context)
            shutil.rmtree(self.artifact_root)

    def _normalize_artifact_permissions(self, context: FaultLifecycleContext) -> None:
        deployment = context.env.deployment
        command = [
            "docker", "run", "--rm", "--user", "0:0", "--entrypoint", "/bin/sh",
            "-v", f"{self.artifact_root}:/state",
            deployment.release.pd_image,
            "-c", "chmod -R a+rwX /state",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                "RG03 artifact permission normalization failed: "
                f"run_id={context.run_id!r}, artifact_root={str(self.artifact_root)!r}, "
                f"returncode={result.returncode}, stdout={result.stdout.strip()!r}, "
                f"stderr={result.stderr.strip()!r}"
            )

    def _configure(self, config: Mapping[str, object], run_id: str) -> None:
        self.database = validate_sql_identifier(str(config["database"]), "database")
        self.business_table = validate_sql_identifier(str(config["business_table"]), "business_table")
        self.job_table = validate_sql_identifier(str(config["job_table"]), "job_table")
        self.baseline_config_table = validate_sql_identifier(
            str(config["baseline_config_table"]), "baseline_config_table"
        )
        self.job_id = str(config["job_id"])
        self.row_count = int(config["row_count"])
        self.expected_business_integrity = tuple(int(value) for value in config["expected_business_integrity"])
        self.artifact_root = Path(str(config["artifact_root"])) / run_id
        self._storage_uri = f"local:///backup/{self.artifact_root.name}/snapshot"
        self.br_image = str(config["br_image"])
        self.initial_br_concurrency = int(config["initial_br_concurrency"])
        self.initial_tikv_backup_threads = int(config["initial_tikv_backup_threads"])
        if self.row_count <= 0 or self.initial_br_concurrency <= 0 or self.initial_tikv_backup_threads <= 0:
            raise ValueError(
                "RG03 injector numeric configuration must be positive: "
                f"row_count={self.row_count}, initial_br_concurrency={self.initial_br_concurrency}, "
                f"initial_tikv_backup_threads={self.initial_tikv_backup_threads}"
            )

    def _create_schema(self, env) -> None:
        require_sql_success(
            env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {self.database}"),
            f"RG03 create database {self.database}",
        )
        for table in (
            self.job_table,
            self.baseline_config_table,
            self.business_table,
            _RG03_CUSTOMERS_TABLE,
            _RG03_INVENTORY_TABLE,
            _RG03_NUMBERS_TABLE,
            _RG03_BACKUP_CATALOG,
            _RG03_RESTORE_QUEUE,
            _RG03_CAPACITY_SNAPSHOT,
            _RG03_CHECKSUM_AUDIT,
        ):
            require_sql_success(
                env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{table}"),
                f"RG03 clear owned table {self.database}.{table}",
            )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.business_table} ("
                "order_id BIGINT NOT NULL, tenant_id INT NOT NULL, customer_id BIGINT NOT NULL, "
                "sku INT NOT NULL, status VARCHAR(16) NOT NULL, amount DECIMAL(12,2) NOT NULL, "
                "payload VARCHAR(512) NOT NULL, PRIMARY KEY (order_id), "
                "KEY idx_tenant_status (tenant_id, status), KEY idx_customer (customer_id), KEY idx_sku (sku)"
                ") ENGINE=InnoDB",
            ),
            f"RG03 create business table {self.database}.{self.business_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{_RG03_CUSTOMERS_TABLE} ("
                "customer_id BIGINT PRIMARY KEY, customer_tier VARCHAR(16) NOT NULL"
                ") ENGINE=InnoDB",
            ),
            f"RG03 create customer table {self.database}.{_RG03_CUSTOMERS_TABLE}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{_RG03_INVENTORY_TABLE} ("
                "sku INT PRIMARY KEY, stock_level INT NOT NULL, updated_at DATETIME NOT NULL"
                ") ENGINE=InnoDB",
            ),
            f"RG03 create inventory table {self.database}.{_RG03_INVENTORY_TABLE}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{_RG03_NUMBERS_TABLE} ("
                "n BIGINT PRIMARY KEY"
                ") ENGINE=InnoDB",
            ),
            f"RG03 create numbers table {self.database}.{_RG03_NUMBERS_TABLE}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{_RG03_BACKUP_CATALOG} ("
                "backup_id BIGINT PRIMARY KEY, backup_type VARCHAR(16) NOT NULL, "
                "state VARCHAR(16) NOT NULL, storage_backend VARCHAR(16) NOT NULL, "
                "size_bytes BIGINT NOT NULL, created_at DATETIME NOT NULL"
                ") ENGINE=InnoDB",
            ),
            f"RG03 create backup catalog table {self.database}.{_RG03_BACKUP_CATALOG}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{_RG03_RESTORE_QUEUE} ("
                "request_id BIGINT PRIMARY KEY, queue_class VARCHAR(16) NOT NULL, "
                "state VARCHAR(16) NOT NULL, priority INT NOT NULL, wait_seconds INT NOT NULL, "
                "payload_bytes BIGINT NOT NULL, submitted_at DATETIME NOT NULL"
                ") ENGINE=InnoDB",
            ),
            f"RG03 create restore queue table {self.database}.{_RG03_RESTORE_QUEUE}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{_RG03_CAPACITY_SNAPSHOT} ("
                "store_id INT PRIMARY KEY, zone VARCHAR(16) NOT NULL, total_bytes BIGINT NOT NULL, "
                "used_bytes BIGINT NOT NULL, reserved_bytes BIGINT NOT NULL, headroom_pct DECIMAL(6,2) NOT NULL"
                ") ENGINE=InnoDB",
            ),
            f"RG03 create capacity snapshot table {self.database}.{_RG03_CAPACITY_SNAPSHOT}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{_RG03_CHECKSUM_AUDIT} ("
                "object_name VARCHAR(128) PRIMARY KEY, check_state VARCHAR(16) NOT NULL, "
                "checksum_value BIGINT NOT NULL, checked_at DATETIME NOT NULL"
                ") ENGINE=InnoDB",
            ),
            f"RG03 create checksum audit table {self.database}.{_RG03_CHECKSUM_AUDIT}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.job_table} ("
                "job_id VARCHAR(64) PRIMARY KEY, state VARCHAR(24) NOT NULL, total_ranges INT NOT NULL, "
                "ranges_succeeded INT NOT NULL, ranges_failed INT NOT NULL, checksum_status VARCHAR(16) NOT NULL, "
                "storage_path VARCHAR(255) NOT NULL, started_at DATETIME(6) NULL, finished_at DATETIME(6) NULL, "
                "last_error VARCHAR(2000) NOT NULL"
                ") ENGINE=InnoDB",
            ),
            f"RG03 create BR job table {self.database}.{self.job_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.baseline_config_table} ("
                "config_name VARCHAR(128) PRIMARY KEY, config_value VARCHAR(128) NOT NULL"
                ") ENGINE=InnoDB"
            ),
            f"RG03 create baseline config table {self.database}.{self.baseline_config_table}",
        )
        self._load_data(env)
        self._seed_job_history(env)

    def _load_data(self, env) -> None:
        digits = " UNION ALL ".join(f"SELECT {value} AS digit" for value in range(10))
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{_RG03_NUMBERS_TABLE} (n) "
                f"SELECT d0.digit + 10 * d1.digit + 100 * d2.digit + 1000 * d3.digit + "
                f"10000 * d4.digit + 1 FROM ({digits}) AS d0 "
                f"CROSS JOIN ({digits}) AS d1 "
                f"CROSS JOIN ({digits}) AS d2 "
                f"CROSS JOIN ({digits}) AS d3 "
                f"CROSS JOIN ({digits}) AS d4"
            ),
            "RG03 load number rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{_RG03_CUSTOMERS_TABLE} (customer_id, customer_tier) "
                f"SELECT n, CASE MOD(n, 4) WHEN 0 THEN 'PLATINUM' WHEN 1 THEN 'GOLD' "
                f"WHEN 2 THEN 'SILVER' ELSE 'BRONZE' END FROM {self.database}.{_RG03_NUMBERS_TABLE} "
                "WHERE n <= 10000"
            ),
            "RG03 load customer rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{_RG03_INVENTORY_TABLE} (sku, stock_level, updated_at) "
                f"SELECT n, 1000 - MOD(n, 317), NOW() FROM {self.database}.{_RG03_NUMBERS_TABLE} "
                "WHERE n <= 1000"
            ),
            "RG03 load inventory rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{_RG03_BACKUP_CATALOG} "
                "(backup_id, backup_type, state, storage_backend, size_bytes, created_at) "
                f"SELECT n, CASE MOD(n, 4) WHEN 0 THEN 'FULL' WHEN 1 THEN 'INCREMENTAL' "
                f"WHEN 2 THEN 'LOG' ELSE 'FULL' END, "
                "CASE MOD(n, 5) WHEN 0 THEN 'SUCCEEDED' WHEN 1 THEN 'EXPIRED' "
                "WHEN 2 THEN 'RUNNING' ELSE 'SUCCEEDED' END, "
                "CASE MOD(n, 3) WHEN 0 THEN 'LOCAL' WHEN 1 THEN 'S3' ELSE 'NFS' END, "
                "500000 + n * 13107, NOW() FROM "
                f"{self.database}.{_RG03_NUMBERS_TABLE} WHERE n <= 64"
            ),
            "RG03 load backup catalog rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{_RG03_RESTORE_QUEUE} "
                "(request_id, queue_class, state, priority, wait_seconds, payload_bytes, submitted_at) "
                f"SELECT n, CASE MOD(n, 3) WHEN 0 THEN 'PITR' WHEN 1 THEN 'CLONE' ELSE 'TABLE' END, "
                "CASE MOD(n, 4) WHEN 0 THEN 'WAITING' WHEN 1 THEN 'RUNNING' "
                "WHEN 2 THEN 'DONE' ELSE 'CANCELLED' END, MOD(n, 9) + 1, "
                "MOD(n * 17, 900) + 30, 200000 + n * 4096, NOW() FROM "
                f"{self.database}.{_RG03_NUMBERS_TABLE} WHERE n <= 48"
            ),
            "RG03 load restore queue rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{_RG03_CAPACITY_SNAPSHOT} "
                "(store_id, zone, total_bytes, used_bytes, reserved_bytes, headroom_pct) "
                f"SELECT n, CASE MOD(n, 3) WHEN 0 THEN 'az-a' WHEN 1 THEN 'az-b' ELSE 'az-c' END, "
                "8000000000, 4600000000 + n * 7000000, 700000000 + MOD(n, 5) * 25000000, "
                "CAST(100 - (4600000000 + n * 7000000 + 700000000 + MOD(n, 5) * 25000000) / 80000000 AS DECIMAL(6,2)) "
                f"FROM {self.database}.{_RG03_NUMBERS_TABLE} WHERE n <= 12"
            ),
            "RG03 load capacity snapshot rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{_RG03_CHECKSUM_AUDIT} "
                "(object_name, check_state, checksum_value, checked_at) "
                f"SELECT CONCAT('object_', n), "
                "CASE MOD(n, 7) WHEN 0 THEN 'PENDING' WHEN 1 THEN 'RETRY' ELSE 'PASSED' END, "
                "900000 + n * 7919, NOW() FROM "
                f"{self.database}.{_RG03_NUMBERS_TABLE} WHERE n <= 40"
            ),
            "RG03 load checksum audit rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.business_table} "
                "(order_id, tenant_id, customer_id, sku, status, amount, payload) "
                f"SELECT n, MOD(n, 64), MOD(n, 10000) + 1, MOD(n, 1000) + 1, "
                "CASE MOD(n, 5) WHEN 0 THEN 'PAID' WHEN 1 THEN 'REVIEW' WHEN 2 THEN 'NEW' "
                "WHEN 3 THEN 'SHIPPED' ELSE 'CANCELLED' END, "
                "CAST(MOD(n * 37, 100000) / 100 AS DECIMAL(12,2)), "
                "RPAD(CONCAT('order-', LPAD(n, 8, '0')), 512, 'x') "
                f"FROM {self.database}.{_RG03_NUMBERS_TABLE}"
            ),
            f"RG03 load {self.row_count} business rows",
        )
        self._verify_business_integrity(env)

    def _seed_job_history(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.job_table} "
                "(job_id, state, total_ranges, ranges_succeeded, ranges_failed, checksum_status, "
                "storage_path, started_at, finished_at, last_error) VALUES "
                "('catalog_full_20260729', 'SUCCEEDED', 11, 11, 0, '100%', "
                "'local:///maintenance/history/catalog-full-20260729', DATE_SUB(NOW(), INTERVAL 4 DAY), "
                "DATE_SUB(NOW(), INTERVAL 4 DAY), ''), "
                "('restore_rehearsal_20260730', 'FAILED', 9, 6, 3, 'FAILED', "
                "'local:///maintenance/history/restore-rehearsal-20260730', DATE_SUB(NOW(), INTERVAL 3 DAY), "
                "DATE_SUB(NOW(), INTERVAL 3 DAY), 'checksum mismatch during rehearsal'), "
                "('recovery_queue_20260731', 'PAUSED', 14, 8, 0, 'PENDING', "
                "'local:///maintenance/history/recovery-queue-20260731', DATE_SUB(NOW(), INTERVAL 2 DAY), NULL, ''), "
                "('capacity_probe_20260801', 'CANCELLED', 7, 2, 0, 'PENDING', "
                "'local:///maintenance/history/capacity-probe-20260801', DATE_SUB(NOW(), INTERVAL 1 DAY), "
                "DATE_SUB(NOW(), INTERVAL 1 DAY), 'cancelled before maintenance window'), "
                "('catalog_export_recent', 'SUCCEEDED', 16, 16, 0, '100%', "
                "'local:///maintenance/recent/catalog-export', DATE_SUB(NOW(), INTERVAL 95 SECOND), "
                "DATE_SUB(NOW(), INTERVAL 80 SECOND), ''), "
                "('recovery_rehearsal_recent', 'PAUSED', 18, 11, 0, 'PENDING', "
                "'local:///maintenance/recent/recovery-rehearsal', DATE_SUB(NOW(), INTERVAL 70 SECOND), NULL, ''), "
                "('capacity_sweep_recent', 'CANCELLED', 12, 5, 0, 'PENDING', "
                "'local:///maintenance/recent/capacity-sweep', DATE_SUB(NOW(), INTERVAL 45 SECOND), "
                "DATE_SUB(NOW(), INTERVAL 40 SECOND), 'window closed before completion')"
            ),
            "RG03 seed historical BR job records",
        )

    def _capture_baseline_config(self, env) -> None:
        rows = self._config_rows(env)
        expected = {"backup.enable-auto-tune", "backup.num-threads"}
        values: dict[str, set[str]] = {name: set() for name in expected}
        for row in rows:
            if len(row) < 4:
                raise RuntimeError(f"RG03 SHOW CONFIG row has fewer than four columns: row={row!r}")
            name = str(row[2])
            if name in values:
                values[name].add(str(row[3]))
        if set(values) != expected or any(len(items) != 1 for items in values.values()):
            raise RuntimeError(
                "RG03 baseline TiKV backup settings must have one consistent value per setting: "
                f"rows={rows!r}, values={values!r}"
            )
        self._restore_auto_tune = next(iter(values["backup.enable-auto-tune"]))
        self._restore_threads = int(float(next(iter(values["backup.num-threads"]))))
        require_sql_success(
            env.execute_sql(f"DELETE FROM {self.database}.{self.baseline_config_table}"),
            "RG03 clear persisted baseline config",
        )
        for name in sorted(expected):
            value = next(iter(values[name])).replace("'", "''")
            require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {self.database}.{self.baseline_config_table} "
                    f"(config_name, config_value) VALUES ('{name}', '{value}')"
                ),
                f"RG03 persist baseline config {name}",
            )

    def _load_baseline_config(self, env) -> None:
        payload = json_object(
            env.execute_sql(
                f"SELECT config_name, config_value FROM {self.database}.{self.baseline_config_table} "
                "ORDER BY config_name"
            ),
            "RG03 load persisted baseline config",
        )
        rows = payload["result"]
        expected = {"backup.enable-auto-tune", "backup.num-threads"}
        values: dict[str, str] = {}
        for row in rows:
            if len(row) < 2:
                raise RuntimeError(
                    "RG03 persisted baseline config row has fewer than two columns: "
                    f"database={self.database!r}, table={self.baseline_config_table!r}, row={row!r}"
                )
            name = str(row[0])
            if name in values:
                raise RuntimeError(
                    "RG03 persisted baseline config contains a duplicate setting: "
                    f"database={self.database!r}, table={self.baseline_config_table!r}, name={name!r}"
                )
            values[name] = str(row[1])
        if set(values) != expected:
            raise RuntimeError(
                "RG03 persisted baseline config is incomplete: "
                f"database={self.database!r}, table={self.baseline_config_table!r}, rows={rows!r}"
            )
        self._restore_auto_tune = values["backup.enable-auto-tune"]
        self._restore_threads = int(float(values["backup.num-threads"]))

    def _set_backup_config(self, env, *, auto_tune: str, threads: int) -> None:
        require_sql_success(
            env.execute_internal_sql(f"SET CONFIG tikv `backup.enable-auto-tune` = '{auto_tune}'"),
            f"RG03 set TiKV backup.enable-auto-tune={auto_tune}",
        )
        require_sql_success(
            env.execute_internal_sql(f"SET CONFIG tikv `backup.num-threads` = '{threads}'"),
            f"RG03 set TiKV backup.num-threads={threads}",
        )

    def _prepare_artifact_directory(self, reset: bool = False) -> None:
        if self.artifact_root is None:
            raise RuntimeError("RG03 artifact root is not configured")
        if reset and self.artifact_root.exists():
            shutil.rmtree(self.artifact_root)
        elif self.artifact_root.exists():
            raise RuntimeError(
                f"RG03 artifact directory already exists; refusing to reuse it: path={str(self.artifact_root)!r}"
            )
        self._snapshot_path = self.artifact_root / "snapshot"
        self._snapshot_path.mkdir(parents=True, exist_ok=False)
        self._br_log_path = self.artifact_root / "br.stdout.log"

    def _insert_job(self, env, state: str) -> None:
        sql = (
            f"INSERT INTO {self.database}.{self.job_table} "
            "(job_id, state, total_ranges, ranges_succeeded, ranges_failed, checksum_status, storage_path, started_at, finished_at, last_error) "
            f"VALUES ('{self.job_id}', '{state}', 0, 0, 0, 'PENDING', '{self._storage_uri}', NOW(6), NULL, '')"
        )
        require_sql_success(env.execute_sql(sql), "RG03 insert BR job record")

    def _reset_job(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"UPDATE {self.database}.{self.job_table} SET state='STARTING', total_ranges=0, "
                "ranges_succeeded=0, ranges_failed=0, checksum_status='PENDING', "
                "started_at=NOW(6), finished_at=NULL, last_error='' "
                f"WHERE job_id='{self.job_id}'"
            ),
            "RG03 reset BR job record",
        )

    def _job(self, env) -> dict[str, object]:
        payload = json_object(
            env.execute_sql(
                f"SELECT job_id, state, total_ranges, ranges_succeeded, ranges_failed, checksum_status, storage_path, last_error "
                f"FROM {self.database}.{self.job_table} WHERE job_id='{self.job_id}'"
            ),
            "RG03 read BR job record",
        )
        rows = payload["result"]
        if len(rows) != 1:
            raise RuntimeError(f"RG03 BR job record must contain one row: rows={rows!r}")
        row = rows[0]
        return {
            "job_id": str(row[0]),
            "state": str(row[1]).upper(),
            "total_ranges": int(row[2]),
            "ranges_succeeded": int(row[3]),
            "ranges_failed": int(row[4]),
            "checksum_status": str(row[5]),
            "storage_path": str(row[6]),
            "last_error": str(row[7] or ""),
        }

    def _config_rows(self, env) -> list[list[object]]:
        payload = json_object(
            env.execute_sql(
                "SHOW CONFIG WHERE type = 'tikv' "
                "AND name IN ('backup.enable-auto-tune', 'backup.num-threads')"
            ),
            "RG03 read TiKV backup configuration",
        )
        return payload["result"]

    def _verify_business_integrity(self, env) -> None:
        payload = json_object(
            env.execute_sql(
                "SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
                "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, status, amount, payload))), 0) "
                f"FROM {self.database}.{self.business_table}"
            ),
            "RG03 verify business integrity",
        )
        observed = tuple(int(value) for value in payload["result"][0])
        if observed != self.expected_business_integrity:
            raise RuntimeError(
                "RG03 business integrity mismatch: "
                f"expected={self.expected_business_integrity!r}, observed={observed!r}"
            )

    def _start_br(self, context: FaultLifecycleContext) -> None:
        if self._br_process is not None and self._br_process.poll() is None:
            raise RuntimeError(f"RG03 BR process is already running: run_id={context.run_id!r}")
        deployment = context.env.deployment
        network = f"{deployment.project_name}_default"
        container_name = f"{deployment.project_name}-br"
        self._br_log_handle = self._br_log_path.open("w", encoding="utf-8")
        command = [
            "docker", "run", "--rm", "--name", container_name,
            "--network", network,
            "--user", f"{os.getuid()}:{os.getgid()}",
            "-v", f"{self.artifact_root.parent}:/backup",
            "--entrypoint", "/br", self.br_image,
            "backup", "db",
            "--pd", "http://pd-0:2379",
            "--db", self.database,
            "--storage", self._storage_uri,
            "--concurrency", str(self.initial_br_concurrency),
            "--checksum",
        ]
        require_sql_success(
            context.env.execute_sql(
                f"UPDATE {self.database}.{self.job_table} SET state='RUNNING', started_at=NOW(6) "
                f"WHERE job_id='{self.job_id}'"
            ),
            "RG03 mark BR job running",
        )
        self._br_process = subprocess.Popen(
            command,
            stdout=self._br_log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self._br_stop = threading.Event()
        self._monitor_error = None
        self._br_thread = threading.Thread(
            target=self._monitor_br,
            args=(context.env,),
            name=f"rg03-br-monitor-{context.run_id}",
            daemon=True,
        )
        self._br_thread.start()

    def _monitor_br(self, env) -> None:
        try:
            returncode = self._br_process.wait()
            if self._br_stop.is_set():
                return
            log_text = self._br_log_path.read_text(encoding="utf-8", errors="replace")
            if returncode != 0:
                self._update_job(
                    env,
                    state="FAILED",
                    total_ranges=0,
                    ranges_succeeded=0,
                    ranges_failed=1,
                    checksum_status="FAILED",
                    last_error=log_text[-1800:],
                )
                return
            summary = self._parse_br_summary(log_text)
            self._update_job(env, state="SUCCEEDED", **summary, last_error="")
        except Exception as exc:
            self._monitor_error = exc

    @staticmethod
    def _parse_br_summary(log_text: str) -> dict[str, object]:
        total = re.search(r"total-ranges=(\d+)", log_text)
        succeeded = re.search(r"ranges-succeed=(\d+)", log_text)
        failed = re.search(r"ranges-failed=(\d+)", log_text)
        checksum = re.search(r"Checksum\s+<[^\n]*>\s+100(?:\.00)?%", log_text, re.IGNORECASE)
        if not total or not succeeded or not failed or not checksum:
            raise RuntimeError(
                "RG03 BR completed without a parseable success summary: "
                f"tail={log_text[-2400:]!r}"
            )
        return {
            "total_ranges": int(total.group(1)),
            "ranges_succeeded": int(succeeded.group(1)),
            "ranges_failed": int(failed.group(1)),
            "checksum_status": "100%",
        }

    def _update_job(
        self,
        env,
        *,
        state: str,
        total_ranges: int,
        ranges_succeeded: int,
        ranges_failed: int,
        checksum_status: str,
        last_error: str,
    ) -> None:
        connection = pymysql.connect(
            host=env.host,
            port=env.port,
            user=env.user,
            password=env.password,
            database=env.dbname,
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=5,
            read_timeout=10,
            write_timeout=10,
        )
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {self.database}.{self.job_table} SET state=%s, total_ranges=%s, "
                "ranges_succeeded=%s, ranges_failed=%s, checksum_status=%s, finished_at=NOW(6), last_error=%s "
                "WHERE job_id=%s",
                (
                    state,
                    total_ranges,
                    ranges_succeeded,
                    ranges_failed,
                    checksum_status,
                    last_error,
                    self.job_id,
                ),
            )
        connection.close()

    def _stop_br(self, env, *, mark_paused: bool) -> None:
        if self._br_stop is not None:
            self._br_stop.set()
        if self._br_process is not None and self._br_process.poll() is None:
            self._br_process.terminate()
            try:
                self._br_process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self._br_process.kill()
                self._br_process.wait(timeout=10)
        if self._br_thread is not None:
            join_thread(self._br_thread, 25, "RG03 BR monitor thread")
        if mark_paused:
            require_sql_success(
                env.execute_sql(
                    f"UPDATE {self.database}.{self.job_table} SET state='PAUSED', finished_at=NULL "
                    f"WHERE job_id='{self.job_id}'"
                ),
                "RG03 mark BR job paused",
            )
        self._br_process = None
        self._br_thread = None
        self._br_stop = None
        if self._br_log_handle is not None:
            self._br_log_handle.close()
            self._br_log_handle = None
        if self._monitor_error is not None:
            error = self._monitor_error
            self._monitor_error = None
            raise RuntimeError(f"RG03 BR monitor failed: error={error!r}") from error


class TidbResourceGovernanceBrSloAdaptiveThrottlingScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_br_slo_adaptive_throttling"
    description = "Resource governance for a live maintenance window under a foreground SLO."
    cases = (_RG03_CASE, _RG03_STORAGE_CASE)

    def build_fault_plan(self, case: TidbResourceGovernanceBrSloCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernanceBrSloInjector,
                config={
                    "database": case.database,
                    "business_table": case.business_table,
                    "job_table": case.job_table,
                    "job_id": case.job_id,
                    "baseline_config_table": case.baseline_config_table,
                    "row_count": case.row_count,
                    "expected_business_integrity": case.expected_business_integrity,
                    "artifact_root": case.artifact_root,
                    "br_image": case.br_image,
                    "initial_br_concurrency": case.initial_br_concurrency,
                    "initial_tikv_backup_threads": case.initial_tikv_backup_threads,
                },
            ),
        )
