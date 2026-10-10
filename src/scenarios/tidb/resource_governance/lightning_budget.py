import json

import math

import os

import re

import shutil

import subprocess

import tempfile

import time

from collections.abc import Mapping

from datetime import datetime, timezone

from pathlib import Path

from src.scenarios.tidb.common import BaseFaultInjector, FaultLifecycleContext, json_object, require_sql_success
from src.execution.deployment import lightning_decoy_job_id, lightning_job_id, lightning_network_alias

"""RG05: govern a real Lightning import while frontend SQL remains online."""

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.resource_governance import (
    TidbResourceGovernanceLightningBudgetEvaluatorCase,
    TidbResourceGovernanceLightningBudgetConservativeEvaluatorCase,
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


LIGHTNING_RESTORE_CHUNK_COMPLETED_RE = re.compile(
    r"restore file completed.*?\[fileIndex=(?P<chunk>\d+)\]"
)
LIGHTNING_IMPORTED_COUNT_RE = re.compile(r"importedCount=(?P<count>\d+)")

# importedCount is an engine-ingest counter that this Lightning build only
# flushes when an engine finishes ingesting into TiKV, while the per-chunk
# "restore file completed" markers land at encode completion. The handoff
# eligibility read therefore needs a tail wide enough to keep both signals
# visible across the whole ingest phase.
CHECKPOINT_LOG_TAIL_LINES = 2000


def build_lightning_budget_noise_profiles(
    db: str = "benchops",
    business_table: str = "business_orders",
    inventory_table: str = "business_inventory",
) -> tuple[WorkloadProfile, ...]:
    orders = f"{db}.{business_table}"
    inventory = f"{db}.{inventory_table}"
    return (
        WorkloadProfile(
            name="checkout_tenant_status_rollup",
            sql=(
                f"SELECT status, COUNT(*) AS order_count, "
                f"CAST(SUM(amount) AS DECIMAL(18,2)) AS gross_amount FROM {orders} "
                "WHERE tenant_id = 17 GROUP BY status ORDER BY gross_amount DESC"
            ),
            qps=0.70,
            tier="FRONTEND_SLO",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="checkout_recent_order_search",
            sql=(
                f"SELECT order_id, status, amount, order_ts FROM {orders} "
                "WHERE tenant_id = 17 AND status IN ('OPEN','PAID') "
                "ORDER BY order_ts DESC, order_id DESC LIMIT 25"
            ),
            qps=0.90,
            tier="FRONTEND_SLO",
            application_name="order-search-api",
        ),
        WorkloadProfile(
            name="checkout_inventory_reservation_probe",
            sql=(
                f"SELECT o.tenant_id, COUNT(*) AS order_lines, "
                f"SUM(i.available_units - i.reserved_units) AS free_units "
                f"FROM {orders} o JOIN {inventory} i ON i.sku_id = o.sku_id "
                "WHERE o.tenant_id = 17 AND o.status = 'OPEN' "
                "GROUP BY o.tenant_id"
            ),
            qps=0.50,
            tier="FRONTEND_SLO",
            application_name="inventory-api",
        ),
        WorkloadProfile(
            name="billing_reconciliation_window",
            sql=(
                f"SELECT region_id, COUNT(*) AS orders, "
                f"CAST(SUM(amount) AS DECIMAL(18,2)) AS gross_amount FROM {orders} "
                "WHERE order_ts >= '2025-01-15 00:00:00' "
                "GROUP BY region_id ORDER BY gross_amount DESC LIMIT 12"
            ),
            qps=0.25,
            tier="BUSINESS_REPORT",
            application_name="billing-reconciliation",
        ),
        WorkloadProfile(
            name="warehouse_capacity_snapshot",
            sql=(
                f"SELECT warehouse_id, SUM(available_units) AS available_units, "
                f"SUM(reserved_units) AS reserved_units FROM {inventory} "
                "GROUP BY warehouse_id ORDER BY warehouse_id LIMIT 32"
            ),
            qps=0.30,
            tier="BUSINESS_REPORT",
            application_name="warehouse-dashboard",
        ),
        WorkloadProfile(
            name="release_metadata_catalog_probe",
            sql=(
                "SELECT TABLE_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_SCHEMA = 'benchops' ORDER BY TABLE_NAME"
            ),
            qps=0.35,
            tier="METADATA_DECOY",
            application_name="release-catalog",
        ),
        WorkloadProfile(
            name="fraud_risk_customer_order_rollup",
            sql=(
                f"SELECT tenant_id, status, COUNT(*) AS orders, "
                f"SUM(amount) AS gross_amount FROM {orders} "
                "WHERE order_ts >= '2025-01-20 00:00:00' "
                "GROUP BY tenant_id, status ORDER BY gross_amount DESC LIMIT 40"
            ),
            qps=0.18,
            tier="OLAP_BURST",
            application_name="fraud-risk-engine",
        ),
        WorkloadProfile(
            name="warehouse_replenishment_gap_scan",
            sql=(
                f"SELECT warehouse_id, COUNT(*) AS sku_count, "
                f"SUM(CASE WHEN available_units - reserved_units < 25 THEN 1 ELSE 0 END) AS low_stock "
                f"FROM {inventory} GROUP BY warehouse_id ORDER BY low_stock DESC"
            ),
            qps=0.22,
            tier="OLAP_BURST",
            application_name="replenishment-planner",
        ),
        WorkloadProfile(
            name="billing_daily_region_reconciliation",
            sql=(
                f"SELECT DATE(order_ts) AS order_day, region_id, "
                f"COUNT(*) AS orders, SUM(amount) AS gross_amount FROM {orders} "
                "GROUP BY DATE(order_ts), region_id ORDER BY order_day DESC, region_id LIMIT 64"
            ),
            qps=0.16,
            tier="OLAP_BURST",
            application_name="billing-reconciliation-batch",
        ),
        WorkloadProfile(
            name="checkout_sku_mix_snapshot",
            sql=(
                f"SELECT sku_id, COUNT(*) AS order_count, SUM(amount) AS gross_amount FROM {orders} "
                "WHERE tenant_id BETWEEN 1 AND 32 GROUP BY sku_id "
                "ORDER BY order_count DESC, sku_id LIMIT 50"
            ),
            qps=0.20,
            tier="BUSINESS_REPORT",
            application_name="checkout-merchandising",
        ),
        WorkloadProfile(
            name="warehouse_reserved_units_audit",
            sql=(
                f"SELECT warehouse_id, SUM(reserved_units) AS reserved_units, "
                f"SUM(available_units) AS available_units FROM {inventory} "
                "GROUP BY warehouse_id HAVING SUM(reserved_units) > 100 "
                "ORDER BY reserved_units DESC"
            ),
            qps=0.18,
            tier="BUSINESS_REPORT",
            application_name="warehouse-audit",
        ),
        WorkloadProfile(
            name="release_table_cardinality_inventory",
            sql=(
                "SELECT TABLE_NAME, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH "
                "FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'benchops' "
                "ORDER BY DATA_LENGTH DESC"
            ),
            qps=0.30,
            tier="METADATA_DECOY",
            application_name="release-catalog-cardinality",
        ),
        WorkloadProfile(
            name="fraud_order_payload_digest",
            sql=(
                f"SELECT tenant_id, COUNT(*) AS orders, "
                f"SUM(CRC32(payload)) AS payload_crc FROM {orders} "
                "GROUP BY tenant_id ORDER BY payload_crc DESC LIMIT 64"
            ),
            qps=0.30,
            tier="OLAP_BURST",
            application_name="fraud-payload-audit",
        ),
        WorkloadProfile(
            name="billing_daily_status_digest",
            sql=(
                f"SELECT DATE(order_ts) AS order_day, status, COUNT(*) AS orders, "
                f"SUM(amount) AS gross_amount FROM {orders} "
                "GROUP BY DATE(order_ts), status ORDER BY order_day DESC, status"
            ),
            qps=0.18,
            tier="BUSINESS_REPORT",
            application_name="billing-status-audit",
        ),
        WorkloadProfile(
            name="inventory_order_coverage_matrix",
            sql=(
                f"SELECT i.warehouse_id, COUNT(DISTINCT o.order_id) AS order_count, "
                f"SUM(i.available_units - i.reserved_units) AS free_units FROM {inventory} i "
                f"JOIN {orders} o ON o.sku_id = i.sku_id "
                "GROUP BY i.warehouse_id ORDER BY order_count DESC"
            ),
            qps=0.24,
            tier="OLAP_BURST",
            application_name="inventory-coverage-audit",
        ),
        WorkloadProfile(
            name="audit_order_payload_signature_scan",
            sql=(
                f"SELECT COUNT(*) AS matching_orders, "
                f"SUM(CRC32(payload)) AS payload_signature FROM {orders} "
                "WHERE payload LIKE '%business-region-%'"
            ),
            qps=0.24,
            tier="BUSINESS_REPORT",
            application_name="order-payload-audit",
        ),
        WorkloadProfile(
            name="warehouse_sku_risk_matrix",
            sql=(
                f"SELECT i.warehouse_id, COUNT(*) AS sku_count, "
                f"SUM(CASE WHEN i.available_units - i.reserved_units < 25 THEN 1 ELSE 0 END) AS low_stock, "
                f"COUNT(o.order_id) AS linked_orders FROM {inventory} i "
                f"LEFT JOIN {orders} o ON o.sku_id = i.sku_id "
                "GROUP BY i.warehouse_id ORDER BY low_stock DESC, linked_orders DESC"
            ),
            qps=0.24,
            tier="BUSINESS_REPORT",
            application_name="warehouse-risk-audit",
        ),
        WorkloadProfile(
            name="release_schema_stats_reconcile",
            sql=(
                "SELECT TABLE_NAME, TABLE_ROWS, AVG_ROW_LENGTH, DATA_LENGTH, INDEX_LENGTH "
                "FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'benchops' "
                "ORDER BY TABLE_ROWS DESC, TABLE_NAME"
            ),
            qps=0.18,
            tier="METADATA_DECOY",
            application_name="release-schema-audit",
        ),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceLightningBudgetCase(TiDBScenarioCase):
    db: str
    import_table: str
    business_table: str
    inventory_table: str
    row_count: int
    source_file_count: int
    business_row_count: int
    inventory_row_count: int
    phase1_checkpoint_deadline_seconds: int
    phase1_region_concurrency: int
    phase1_disk_quota_mb: int
    phase1_store_write_bwlimit_mib: int
    rebalance_after_rows: int
    phase2_region_concurrency_max: int
    phase2_disk_quota_mb_max: int
    phase2_store_write_bwlimit_mib_max: int
    phase2_store_write_bwlimit_mib_min: int
    staging_table: str | None
    staging_row_count: int
    frontend_slo_p95_ms: float
    frontend_min_successes: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceLightningBudgetForOnlineImportScenarioCase(
    TidbResourceGovernanceLightningBudgetCase
):
    pass


_CASE = TidbResourceGovernanceLightningBudgetForOnlineImportScenarioCase(
    case_id="lightning_import_budget",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "Ran Lightning precheck and applied an initial bounded budget for the source-defined import",
                "Rebalanced the running import from its real checkpoint and completed the second bounded budget phase"
            ],
            "verification": [
                "Lightning completed both checkpoint-controlled resource phases with the exact source row count",
                "Protected business tables remained unchanged while the import controller ran"
            ]
        },
        "summary": "The online Lightning import completed both bounded resource phases without changing protected business tables."
    },
    case_no=0,
    evaluator=TidbResourceGovernanceLightningBudgetEvaluatorCase,
    title=(
        "Govern a physical TiDB Lightning import with bounded Region concurrency, "
        "local sort space, and downstream write bandwidth while frontend SQL stays online."
    ),
    alert=(
        "P1 resource-governance alert: a physical TiDB Lightning import is waiting for an "
        "operational budget while checkout, inventory, billing reconciliation, and warehouse "
        "queries remain online on the same cluster. Bring the import online under bounded, "
        "non-zero resource settings without changing the business tables. Start by checking "
        "the Lightning requirements and the live cluster/workload state, then keep observing "
        "the import and online workload as its controller state changes. Finish with exact "
        "import completion and protected business-state verification. Do not disable safety "
        "checks, consume the whole local store, or use an unlimited write limit."
    ),
    initial_state={
        "status": "ready_to_import",
        "import": "not_started",
        "frontend": "online",
        "business_tables": "protected",
        "checkpoint": "available",
        "sort_space": "shared_with_compaction_and_snapshots",
        "budget_phases": "initial_and_rebalanced",
    },
    expected_target={
        "status": "completed",
        "import_rows": 600000,
        "checkpoint_handoff": "required",
        "budget_phases": 2,
        "precheck": "passed",
        "frontend": "online during the import controller phases",
        "business_tables": "unchanged",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=build_lightning_budget_noise_profiles(),
        worker_count=6,
        seed=50705,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=8,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.86128,
        reference_run_ids=(
            "tidb_resource_governance_lightning_budget__calibration__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=120,
        image_group_key=None,
    ),
    db="benchops",
    import_table="lightning_orders",
    business_table="business_orders",
    inventory_table="business_inventory",
    row_count=600000,
    source_file_count=6,
    business_row_count=120000,
    inventory_row_count=20000,
    phase1_checkpoint_deadline_seconds=55,
    phase1_region_concurrency=1,
    phase1_disk_quota_mb=1024,
    phase1_store_write_bwlimit_mib=16,
    rebalance_after_rows=600000,
    phase2_region_concurrency_max=2,
    phase2_disk_quota_mb_max=2048,
    phase2_store_write_bwlimit_mib_max=48,
    phase2_store_write_bwlimit_mib_min=16,
    staging_table=None,
    staging_row_count=0,
    frontend_slo_p95_ms=3000.0,
    frontend_min_successes=3,
)

_CONSERVATIVE_CASE = replace(
    _CASE,
    case_id="lightning_import_conservative_rebalance",
    case_no=1,
    evaluator=TidbResourceGovernanceLightningBudgetConservativeEvaluatorCase,
    title="Complete a smaller Lightning import with an earlier checkpoint and tighter final budget.",
    alert=(
        "P1 resource-governance alert: a physical Lightning import is online beside checkout and "
        "inventory queries, but its controller must hand off at an earlier checkpoint and finish under "
        "a tighter bounded budget. Inspect the live job, requirements, disk headroom, and frontend SLO; "
        "use non-zero bounded settings, preserve business tables, and verify exact completion."
    ),
    initial_state={
        "status": "ready_to_import",
        "import": "not_started",
        "frontend": "online",
        "checkpoint": "early handoff required",
        "budget_phases": "initial and conservative rebalance",
    },
    expected_target={
        "status": "completed",
        "import_rows": 400000,
        "checkpoint_handoff": "required",
        "budget_phases": 2,
        "final_budget": "bounded by 2 regions, 2048 MiB, 48 MiB/s",
        "frontend": "online during controller phases",
        "business_tables": "unchanged",
    },
    row_count=400000,
    source_file_count=4,
    phase1_checkpoint_deadline_seconds=45,
    phase1_region_concurrency=1,
    phase1_disk_quota_mb=1024,
    phase1_store_write_bwlimit_mib=16,
    rebalance_after_rows=300000,
    phase2_region_concurrency_max=2,
    phase2_disk_quota_mb_max=2048,
    phase2_store_write_bwlimit_mib_max=48,
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.865297,
        reference_run_ids=(
            "tidb-reference-1__tidb_resource_governance_lightning_budget__"
            "lightning_import_conservative_rebalance__mock__r001",
        ),
    ),
)


LIGHTNING_IMAGE = (
    "pingcap/tidb-lightning@"
    "sha256:1e6bdabf58b3df58d073acd311923cb59f877f8017cd12a94c1187ee967bef79"
)

LIGHTNING_CPU_LIMIT = 1.5

LIGHTNING_MEMORY_LIMIT = "4g"

IMPORT_PAYLOAD_FILLER = "x" * 736

SAFE_REGION_CONCURRENCY_MAX = 6

SAFE_DISK_QUOTA_MB_MIN = 1024

SAFE_DISK_QUOTA_MB_MAX = 4096

SAFE_WRITE_BWLIMIT_MIB_MIN = 16

SAFE_WRITE_BWLIMIT_MIB_MAX = 128

def _require_positive_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer, got {value!r}")
    return value

def _parse_docker_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    if "." not in normalized:
        return datetime.fromisoformat(normalized)
    prefix, fraction_and_offset = normalized.split(".", 1)
    offset_index = next(
        (index for index, character in enumerate(fraction_and_offset) if character in "+-"),
        -1,
    )
    if offset_index < 0:
        raise ValueError(f"Docker timestamp has no timezone offset: value={value!r}")
    fraction = fraction_and_offset[:offset_index]
    if not fraction.isdigit():
        raise ValueError(f"Docker timestamp has invalid fractional seconds: value={value!r}")
    return datetime.fromisoformat(
        f"{prefix}.{fraction[:6].ljust(6, '0')}{fraction_and_offset[offset_index:]}"
    )

class LightningBudgetController:
    """Own one external Lightning container and expose only explicit state changes."""

    def __init__(self, env, config: Mapping[str, object]):
        self.env = env
        self.run_id = env.run_id
        self.db = str(config["db"])
        self.import_table = str(config["import_table"])
        self.business_table = str(config["business_table"])
        self.inventory_table = str(config["inventory_table"])
        self.row_count = int(config["row_count"])
        self.source_file_count = int(config["source_file_count"])
        self.business_row_count = int(config["business_row_count"])
        self.inventory_row_count = int(config["inventory_row_count"])
        self.phase1_checkpoint_deadline_seconds = int(config["phase1_checkpoint_deadline_seconds"])
        self.phase1_region_concurrency = int(config["phase1_region_concurrency"])
        self.phase1_disk_quota_mb = int(config["phase1_disk_quota_mb"])
        self.phase1_store_write_bwlimit_mib = int(config["phase1_store_write_bwlimit_mib"])
        self.rebalance_after_rows = int(config["rebalance_after_rows"])
        self.engine_batch_size_bytes: int | None = (
            int(config["engine_batch_size_bytes"])
            if config.get("engine_batch_size_bytes") is not None
            else None
        )
        self.phase2_region_concurrency_max = int(config["phase2_region_concurrency_max"])
        self.phase2_disk_quota_mb_max = int(config["phase2_disk_quota_mb_max"])
        self.phase2_store_write_bwlimit_mib_max = int(config["phase2_store_write_bwlimit_mib_max"])
        self.phase2_store_write_bwlimit_mib_min = int(config["phase2_store_write_bwlimit_mib_min"])
        self.staging_table: str | None = config["staging_table"]
        self.staging_row_count = int(config["staging_row_count"])
        self.runtime_dir = Path(
            tempfile.mkdtemp(prefix=f"aiopsbench-rg05-{self.run_id}-")
        )
        self.source_dir = self.runtime_dir / "dump"
        self.sorted_dir = self.runtime_dir / "sorted"
        self.checkpoint_dir = self.runtime_dir / "checkpoint"
        self.config_path = self.runtime_dir / "lightning.toml"
        self.staging_source_dir = self.runtime_dir / "dump_staging"
        self.staging_checkpoint_dir = self.runtime_dir / "checkpoint_staging"
        self.staging_sorted_dir = self.runtime_dir / "sorted_staging"
        self.staging_config_path = self.runtime_dir / "lightning_staging.toml"
        self.container_name = f"{self.run_id}-lightning"
        self.network_alias = lightning_network_alias(self.run_id)
        self.network_name = f"aiopsbench-{self.run_id}_default"
        self.tidb_host = "tidb-0"
        self.pd_urls = ",".join(
            f"{service}:2379" for service in env.deployment.COMPONENTS["pd"]
        )
        self.precheck_passed = False
        self.budget: dict[str, int] | None = None
        self.budget_history: list[dict[str, object]] = []
        self.phase = "ready_to_import"
        self.rebalance_required = False
        self.rebalance_count = 0
        self.phase1_rows: int | None = None
        self.phase1_visible_rows: int | None = None
        self.phase1_completed_chunks: tuple[int, ...] = ()
        self.phase2_started_at: float | None = None
        self.phase2_finished_at: float | None = None
        self.other_jobs: tuple[dict[str, object], ...] = ()
        self.phase1_log_tail = ""
        self.failure_stage: str | None = None
        self.failure_reason: str | None = None
        self.failure_log_tail = ""
        self.total_started_at: float | None = None
        self.total_finished_at: float | None = None
        self._history_logs = ""
        self._prepared = False

    @property
    def safe_bounds(self) -> dict[str, object]:
        return {
            "initial": {
                "region_concurrency": {
                    "min": 1,
                    "max": SAFE_REGION_CONCURRENCY_MAX,
                },
                "disk_quota_mb": {
                    "min": SAFE_DISK_QUOTA_MB_MIN,
                    "max": SAFE_DISK_QUOTA_MB_MAX,
                },
                "store_write_bwlimit_mib": {
                    "min": SAFE_WRITE_BWLIMIT_MIB_MIN,
                    "max": SAFE_WRITE_BWLIMIT_MIB_MAX,
                },
            },
            "rebalanced": {
                "region_concurrency": {
                    "min": 1,
                    "max": self.phase2_region_concurrency_max,
                },
                "disk_quota_mb": {
                    "min": SAFE_DISK_QUOTA_MB_MIN,
                    "max": self.phase2_disk_quota_mb_max,
                },
                "store_write_bwlimit_mib": {
                    "min": self.phase2_store_write_bwlimit_mib_min,
                    "max": self.phase2_store_write_bwlimit_mib_max,
                },
            },
        }

    def prepare(self) -> None:
        self.source_dir.mkdir(parents=True, exist_ok=False)
        self.sorted_dir.mkdir()
        self.checkpoint_dir.mkdir()
        self._create_database_state()
        self._write_source_files()
        if self.staging_table is not None:
            self.staging_source_dir.mkdir()
            self.staging_checkpoint_dir.mkdir()
            self.staging_sorted_dir.mkdir()
            self._create_staging_table()
            self._write_staging_source_file()
            self._write_staging_config()
        self._write_config(
            region_concurrency=self.phase1_region_concurrency,
            disk_quota_mb=self.phase1_disk_quota_mb,
            store_write_bwlimit_mib=self.phase1_store_write_bwlimit_mib,
            engine_batch_size_bytes=self.engine_batch_size_bytes,
        )
        self._prepared = True

    def _create_database_state(self) -> None:
        require_sql_success(
            self.env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {self.db}"),
            f"create RG05 database {self.db}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.db}.{self.import_table} ("
                "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, "
                "status VARCHAR(16) NOT NULL, order_ts DATETIME NOT NULL, "
                "amount DECIMAL(12,2) NOT NULL, sku_id BIGINT NOT NULL, "
                "region_id INT NOT NULL, payload VARCHAR(1024) NOT NULL, "
                "KEY idx_import_tenant_status (tenant_id, status), "
                "KEY idx_import_order_ts (order_ts)"
                ")"
            ),
            f"create empty Lightning target {self.db}.{self.import_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.db}.{self.business_table} ("
                "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, "
                "status VARCHAR(16) NOT NULL, order_ts DATETIME NOT NULL, "
                "amount DECIMAL(12,2) NOT NULL, sku_id BIGINT NOT NULL, "
                "region_id INT NOT NULL, payload VARCHAR(64) NOT NULL, "
                "KEY idx_business_tenant_status (tenant_id, status), "
                "KEY idx_business_order_ts (order_ts)"
                ")"
            ),
            f"create business table {self.db}.{self.business_table}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.db}.{self.inventory_table} ("
                "sku_id BIGINT PRIMARY KEY, available_units INT NOT NULL, "
                "reserved_units INT NOT NULL, warehouse_id INT NOT NULL, "
                "KEY idx_inventory_warehouse (warehouse_id)"
                ")"
            ),
            f"create business inventory table {self.db}.{self.inventory_table}",
        )
        self._insert_business_rows()
        self._insert_inventory_rows()

    def _insert_business_rows(self) -> None:
        statuses = ("OPEN", "PAID", "PACKED", "CANCELLED")
        batch_size = 2000
        for start in range(1, self.business_row_count + 1, batch_size):
            end = min(start + batch_size, self.business_row_count + 1)
            values = []
            for order_id in range(start, end):
                tenant_id = order_id % 64 + 1
                status = statuses[order_id % len(statuses)]
                amount = f"{(order_id * 17 % 100000) / 100:.2f}"
                values.append(
                    f"({order_id},{tenant_id},'{status}',"
                    f"'2025-01-{order_id % 28 + 1:02d} 12:{order_id % 60:02d}:00',"
                    f"{amount},{order_id % 20000 + 1},{order_id % 32 + 1},"
                    f"'business-region-{order_id % 17:02d}')"
                )
            require_sql_success(
                self.env.execute_sql(
                    f"INSERT INTO {self.db}.{self.business_table} "
                    "(order_id,tenant_id,status,order_ts,amount,sku_id,region_id,payload) VALUES "
                    + ",".join(values)
                ),
                f"load business order rows {start}:{end - 1}",
            )

    def _insert_inventory_rows(self) -> None:
        batch_size = 2000
        for start in range(1, self.inventory_row_count + 1, batch_size):
            end = min(start + batch_size, self.inventory_row_count + 1)
            values = [
                f"({sku_id},{100 + sku_id % 900},{sku_id % 70},{sku_id % 32 + 1})"
                for sku_id in range(start, end)
            ]
            require_sql_success(
                self.env.execute_sql(
                    f"INSERT INTO {self.db}.{self.inventory_table} "
                    "(sku_id,available_units,reserved_units,warehouse_id) VALUES "
                    + ",".join(values)
                ),
                f"load inventory rows {start}:{end - 1}",
            )

    def _write_source_files(self) -> None:
        rows_per_file = math.ceil(self.row_count / self.source_file_count)
        row_id = 1
        for file_number in range(1, self.source_file_count + 1):
            path = self.source_dir / f"{self.db}.{self.import_table}.{file_number:03d}.csv"
            with path.open("w", encoding="ascii", newline="") as handle:
                handle.write("order_id,tenant_id,status,order_ts,amount,sku_id,region_id,payload\n")
                for _ in range(rows_per_file):
                    if row_id > self.row_count:
                        break
                    tenant_id = row_id % 128 + 1
                    status = ("OPEN", "PAID", "PACKED", "CANCELLED")[row_id % 4]
                    amount = f"{(row_id * 19 % 150000) / 100:.2f}"
                    handle.write(
                        f"{row_id},{tenant_id},{status},2025-02-{row_id % 28 + 1:02d} "
                        f"{row_id % 24:02d}:{row_id % 60:02d}:00,{amount},"
                        f"{row_id % self.inventory_row_count + 1},{row_id % 32 + 1},"
                        f"import-region-{row_id % 23:02d}-order-{row_id:09d}-{IMPORT_PAYLOAD_FILLER}\n"
                    )
                    row_id += 1
        if row_id != self.row_count + 1:
            raise RuntimeError(
                f"RG05 source generation row mismatch: expected={self.row_count}, generated={row_id - 1}, "
                f"source_dir={self.source_dir}"
            )

    def _write_config(
        self,
        *,
        region_concurrency: int,
        disk_quota_mb: int,
        store_write_bwlimit_mib: int,
        engine_batch_size_bytes: int | None,
    ) -> None:
        disk_quota = f"{disk_quota_mb}MB" if disk_quota_mb else "0"
        write_bwlimit = f"{store_write_bwlimit_mib}MiB" if store_write_bwlimit_mib else "0"
        mydumper_lines = [
            "[mydumper]",
            f'data-source-dir = "{self._container_path(self.source_dir)}"',
            "strict-format = true",
        ]
        if engine_batch_size_bytes is not None:
            mydumper_lines.append(f"batch-size = {engine_batch_size_bytes}")
        self.config_path.write_text(
            "\n".join((
                "[lightning]",
                'level = "info"',
                "region-concurrency = " + str(region_concurrency),
                "check-requirements = true",
                "index-concurrency = 2",
                "table-concurrency = 2",
                "io-concurrency = 2",
                "",
                "[checkpoint]",
                "enable = true",
                "keep-after-success = true",
                'driver = "file"',
                f'dsn = "{self._container_path(self.checkpoint_dir)}/checkpoint.db"',
                "",
                "[tikv-importer]",
                'backend = "local"',
                f'sorted-kv-dir = "{self._container_path(self.sorted_dir)}"',
                f'disk-quota = "{disk_quota}"',
                f'store-write-bwlimit = "{write_bwlimit}"',
                "",
                "[tidb]",
                f'host = "{self.tidb_host}"',
                "port = 4000",
                "status-port = 10080",
                'user = "root"',
                'password = ""',
                f'pd-addr = "{self.pd_urls}"',
                "",
                *mydumper_lines,
                "",
                "[mydumper.csv]",
                "header = true",
                'separator = ","',
                "",
                "[post-restore]",
                'checksum = "required"',
                'analyze = "required"',
                "",
            )),
            encoding="ascii",
        )

    def _create_staging_table(self) -> None:
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.db}.{self.staging_table} ("
                "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, "
                "status VARCHAR(16) NOT NULL, order_ts DATETIME NOT NULL, "
                "amount DECIMAL(12,2) NOT NULL, sku_id BIGINT NOT NULL, "
                "region_id INT NOT NULL, payload VARCHAR(256) NOT NULL, "
                "KEY idx_staging_tenant_status (tenant_id, status)"
                ")"
            ),
            f"create empty staging table {self.db}.{self.staging_table}",
        )

    def _write_staging_source_file(self) -> None:
        path = self.staging_source_dir / f"{self.db}.{self.staging_table}.001.csv"
        with path.open("w", encoding="ascii", newline="") as handle:
            handle.write("order_id,tenant_id,status,order_ts,amount,sku_id,region_id,payload\n")
            for row_id in range(1, self.staging_row_count + 1):
                tenant_id = row_id % 64 + 1
                status = ("OPEN", "PAID")[row_id % 2]
                amount = f"{(row_id * 13 % 90000) / 100:.2f}"
                handle.write(
                    f"{row_id},{tenant_id},{status},2025-03-{row_id % 28 + 1:02d} "
                    f"{row_id % 24:02d}:{row_id % 60:02d}:00,{amount},"
                    f"{row_id % 5000 + 1},{row_id % 16 + 1},"
                    f"staging-region-{row_id % 9:02d}-batch-{row_id:08d}\n"
                )

    def _write_staging_config(self) -> None:
        self.staging_config_path.write_text(
            "\n".join((
                "[lightning]",
                'level = "info"',
                "region-concurrency = 4",
                "check-requirements = true",
                "index-concurrency = 2",
                "table-concurrency = 2",
                "io-concurrency = 2",
                "",
                "[checkpoint]",
                "enable = true",
                "keep-after-success = true",
                'driver = "file"',
                f'dsn = "{self._container_path(self.staging_checkpoint_dir)}/checkpoint.db"',
                "",
                "[tikv-importer]",
                'backend = "local"',
                f'sorted-kv-dir = "{self._container_path(self.staging_sorted_dir)}"',
                'disk-quota = "1024MB"',
                'store-write-bwlimit = "48MiB"',
                "",
                "[tidb]",
                f'host = "{self.tidb_host}"',
                "port = 4000",
                "status-port = 10080",
                'user = "root"',
                'password = ""',
                f'pd-addr = "{self.pd_urls}"',
                "",
                "[mydumper]",
                f'data-source-dir = "{self._container_path(self.staging_source_dir)}"',
                "strict-format = true",
                "",
                "[mydumper.csv]",
                "header = true",
                'separator = ","',
                "",
                "[post-restore]",
                'checksum = "required"',
                'analyze = "required"',
                "",
            )),
            encoding="ascii",
        )

    def run_staging_import(self) -> None:
        """Run the benign staging load to safe completion before the main import.

        The staging container reuses the controller container name and network
        alias, so its Lightning metrics flow through the same run-scoped
        Prometheus target and land in the frozen history as a real completed
        same-shape window next to the main import's truncated arc. The
        container replay resumes from the staging checkpoint, which covers
        transient docker-DNS failures during Lightning's post-process phase.
        """
        failure_log_tail = ""
        for attempt in range(3):
            if attempt:
                time.sleep(5 * attempt)
            self._run_lightning(
                detached=True,
                config_path=self.staging_config_path,
                source_dir=self.staging_source_dir,
                sorted_dir=self.staging_sorted_dir,
                checkpoint_dir=self.staging_checkpoint_dir,
            )
            failure_log_tail = self._await_staging_exit()
            self._remove_container()
            if failure_log_tail is None:
                return
        raise RuntimeError(
            f"RG05 staging import failed after retries: run_id={self.run_id!r}, "
            f"log_tail={failure_log_tail[-2000:]!r}"
        )

    def _await_staging_exit(self) -> str | None:
        """Wait for the staging container to exit; None on exit 0, else the
        failure description (log tail, lost container, or deadline overrun)."""
        deadline = time.monotonic() + 180
        while True:
            state = self._container_state()
            if state is None:
                return "container lost before completion"
            if not state["Running"]:
                if int(state["ExitCode"]) != 0:
                    logs = self._docker(["logs", self.container_name], timeout=30)
                    return logs
                return None
            if time.monotonic() > deadline:
                self._docker(["stop", "--time", "10", self.container_name], timeout=60)
                return "exceeded 180s before completing"
            time.sleep(2)

    @staticmethod
    def _container_path(path: Path) -> str:
        return "/var/lib/lightning/" + path.name

    def _docker(self, args: list[str], *, timeout: int = 120) -> str:
        command = ["docker", *args]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"RG05 Docker command failed: run_id={self.run_id!r}, command={command!r}, "
                f"returncode={result.returncode}, stdout={result.stdout[-2000:]!r}, "
                f"stderr={result.stderr[-2000:]!r}"
            )
        return result.stdout.strip()

    def _container_state(self) -> dict[str, object] | None:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{json .State}}", self.container_name],
            capture_output=True,
            text=True,
        )
        if result.returncode == 1 and "no such object" in result.stderr.casefold():
            return None
        if result.returncode != 0:
            raise RuntimeError(
                f"RG05 could not inspect Lightning container: name={self.container_name!r}, "
                f"returncode={result.returncode}, stderr={result.stderr.strip()!r}"
            )
        return json.loads(result.stdout)

    def _run_lightning(
        self,
        *,
        detached: bool,
        config_path: Path,
        source_dir: Path,
        sorted_dir: Path,
        checkpoint_dir: Path,
    ) -> str:
        command = [
            "run",
            "--name", self.container_name,
            "--network", self.network_name,
            "--network-alias", self.network_alias,
            "--user", f"{os.getuid()}:{os.getgid()}",
            "--cpus", str(LIGHTNING_CPU_LIMIT),
            "--memory", LIGHTNING_MEMORY_LIMIT,
            "-v", f"{config_path}:{self._container_path(config_path)}:ro",
            "-v", f"{source_dir}:{self._container_path(source_dir)}:ro",
            "-v", f"{sorted_dir}:{self._container_path(sorted_dir)}",
            "-v", f"{checkpoint_dir}:{self._container_path(checkpoint_dir)}",
            "--detach" if detached else "--rm",
            LIGHTNING_IMAGE,
            "/tidb-lightning",
            "--config", self._container_path(config_path),
            "--log-file", "-",
            "--status-addr", "0.0.0.0:8287",
            "--d", self._container_path(source_dir),
            "--no-schema",
            "--pd-urls", self.pd_urls,
            "--tidb-host", self.tidb_host,
            "--tidb-port", "4000",
            "--tidb-status", "10080",
            "--tidb-user", "root",
            "--backend", "local",
            "--sorted-kv-dir", self._container_path(sorted_dir),
            "--enable-checkpoint",
            "--checksum", "required",
            "--analyze", "required",
        ]
        return self._docker(command, timeout=180)

    def _run_lightning_precheck(self) -> str:
        """Run Lightning's requirement checks without selecting any source table."""
        command = [
            "run",
            "--name", self.container_name,
            "--network", self.network_name,
            "--user", f"{os.getuid()}:{os.getgid()}",
            "--cpus", str(LIGHTNING_CPU_LIMIT),
            "--memory", LIGHTNING_MEMORY_LIMIT,
            "-v", f"{self.config_path}:{self._container_path(self.config_path)}:ro",
            "-v", f"{self.source_dir}:{self._container_path(self.source_dir)}:ro",
            "-v", f"{self.sorted_dir}:{self._container_path(self.sorted_dir)}",
            "-v", f"{self.checkpoint_dir}:{self._container_path(self.checkpoint_dir)}",
            "--rm",
            LIGHTNING_IMAGE,
            "/tidb-lightning",
            "--config", self._container_path(self.config_path),
            "--log-file", "-",
            "--d", self._container_path(self.source_dir),
            "-f", "__rg05_precheck_never_matches__.*",
            "--no-schema",
            "--pd-urls", self.pd_urls,
            "--tidb-host", self.tidb_host,
            "--tidb-port", "4000",
            "--tidb-status", "10080",
            "--tidb-user", "root",
            "--backend", "local",
            "--sorted-kv-dir", self._container_path(self.sorted_dir),
            "--enable-checkpoint",
            "--checksum", "off",
            "--analyze", "off",
        ]
        return self._docker(command, timeout=180)

    def _ignore_controlled_checkpoint_error(self) -> str:
        table = f"`{self.db}`.`{self.import_table}`"
        command = [
            "run",
            "--name", self.container_name,
            "--network", self.network_name,
            "--user", f"{os.getuid()}:{os.getgid()}",
            "-v", f"{self.config_path}:{self._container_path(self.config_path)}:ro",
            "-v", f"{self.checkpoint_dir}:{self._container_path(self.checkpoint_dir)}",
            "--rm",
            LIGHTNING_IMAGE,
            "/tidb-lightning-ctl",
            "--config", self._container_path(self.config_path),
            f"--checkpoint-error-ignore={table}",
        ]
        return self._docker(command, timeout=180)

    def precheck(self) -> dict[str, object]:
        if not self._prepared:
            raise RuntimeError(f"RG05 Lightning controller is not prepared: run_id={self.run_id!r}")
        if self._container_state() is not None:
            raise RuntimeError(
                f"RG05 precheck requires no running import container: container={self.container_name!r}"
            )
        rows_before = self._target_row_count()
        if rows_before != 0:
            raise RuntimeError(
                f"RG05 precheck requires an empty target table: table={self.db}.{self.import_table}, "
                f"rows={rows_before}"
            )
        output = self._run_lightning_precheck()
        rows_after = self._target_row_count()
        if rows_after != rows_before:
            raise RuntimeError(
                f"RG05 precheck changed target rows: table={self.db}.{self.import_table}, "
                f"before={rows_before}, after={rows_after}"
            )
        self.precheck_passed = True
        return {
            "status": "success",
            "action": "precheck",
            "precheck": "passed",
            "import_started": False,
            "target_rows": rows_after,
            "requirements": "cluster, permissions, disk, Region layout",
            "output_tail": output[-2000:],
        }

    def apply_budget(
        self,
        *,
        region_concurrency: object,
        disk_quota_mb: object,
        store_write_bwlimit_mib: object,
        job_id: object,
    ) -> dict[str, object]:
        active_job_id = lightning_job_id(self.run_id)
        if job_id == active_job_id:
            return self._apply_active_budget(
                region_concurrency=region_concurrency,
                disk_quota_mb=disk_quota_mb,
                store_write_bwlimit_mib=store_write_bwlimit_mib,
            )
        return self._apply_seeded_job_budget(
            job_id,
            region_concurrency=region_concurrency,
            disk_quota_mb=disk_quota_mb,
            store_write_bwlimit_mib=store_write_bwlimit_mib,
        )

    def _apply_seeded_job_budget(
        self,
        job_id: object,
        *,
        region_concurrency: object,
        disk_quota_mb: object,
        store_write_bwlimit_mib: object,
    ) -> dict[str, object]:
        for job in self.other_jobs:
            if job["job_id"] != job_id:
                continue
            region = _require_positive_int(region_concurrency, "region_concurrency")
            quota = _require_positive_int(disk_quota_mb, "disk_quota_mb")
            bwlimit = _require_positive_int(store_write_bwlimit_mib, "store_write_bwlimit_mib")
            self._validate_budget(region, quota, bwlimit, rebalance=True)
            if job["state"] != "reconfigure_required":
                raise RuntimeError(
                    f"RG05 seeded job is not accepting a budget: job_id={job_id!r}, "
                    f"state={job['state']!r}"
                )
            job["budget"] = {
                "region_concurrency": region,
                "disk_quota_mb": quota,
                "store_write_bwlimit_mib": bwlimit,
            }
            job["state"] = "completed"
            job["phase"] = "completed"
            job["reconfigure_required"] = False
            job["exit_code"] = 0
            job["target_rows"] = job["expected_rows"]
            return {
                "status": "success",
                "job_id": job_id,
                "action": "apply_budget",
                "phase": "rebalanced",
                "budget": job["budget"],
                "checkpoint": "enabled",
                "import_state": "completed",
                "reconfigure_required": False,
            }
        raise ValueError(
            f"RG05 job update targets an unknown job: requested_job_id={job_id!r}, "
            f"known_jobs={sorted([lightning_job_id(self.run_id), *[job['job_id'] for job in self.other_jobs]])}"
        )

    def _apply_active_budget(
        self,
        *,
        region_concurrency: object,
        disk_quota_mb: object,
        store_write_bwlimit_mib: object,
    ) -> dict[str, object]:
        if not self.precheck_passed:
            raise RuntimeError("RG05 apply_budget requires a successful precheck first")
        if self.failure_reason is not None:
            raise RuntimeError(
                f"RG05 import cannot accept a budget after failure: "
                f"stage={self.failure_stage!r}, reason={self.failure_reason!r}"
            )
        region = _require_positive_int(region_concurrency, "region_concurrency")
        quota = _require_positive_int(disk_quota_mb, "disk_quota_mb")
        bwlimit = _require_positive_int(store_write_bwlimit_mib, "store_write_bwlimit_mib")
        rebalance = self.rebalance_required and self.rebalance_count == 0
        if self.budget is not None and not rebalance:
            raise RuntimeError(
                f"RG05 budget phase is not accepting apply_budget: phase={self.phase!r}, "
                f"rebalance_required={self.rebalance_required}, rebalance_count={self.rebalance_count}"
            )
        self._validate_budget(region, quota, bwlimit, rebalance=rebalance)
        state = self._container_state()
        if state is not None and not rebalance:
            raise RuntimeError(
                f"RG05 cannot apply the initial budget while import container exists: "
                f"container={self.container_name!r}, status={state['Status']!r}"
            )
        if rebalance and state is not None:
            self._remove_container()
        self._write_config(
            region_concurrency=region,
            disk_quota_mb=quota,
            store_write_bwlimit_mib=bwlimit,
            engine_batch_size_bytes=self.engine_batch_size_bytes,
        )
        if rebalance:
            self._ignore_controlled_checkpoint_error()
        self._run_lightning(
            detached=True,
            config_path=self.config_path,
            source_dir=self.source_dir,
            sorted_dir=self.sorted_dir,
            checkpoint_dir=self.checkpoint_dir,
        )
        if self.total_started_at is None:
            self.total_started_at = time.monotonic()
        self.budget = {
            "region_concurrency": region,
            "disk_quota_mb": quota,
            "store_write_bwlimit_mib": bwlimit,
        }
        phase_name = "rebalanced" if rebalance else "initial"
        self.budget_history.append({"phase": phase_name, **self.budget})
        if rebalance:
            self.rebalance_required = False
            self.rebalance_count += 1
            self.phase = "final_running"
            self.phase2_started_at = time.time()
        else:
            self.phase = "initial_running"
        return {
            "status": "success",
            "job_id": lightning_job_id(self.run_id),
            "action": "apply_budget",
            "phase": phase_name,
            "budget": self.budget,
            "checkpoint": "enabled",
            "import_state": "running",
            "reconfigure_required": False,
        }

    def _validate_budget(
        self,
        region: int,
        quota: int,
        bwlimit: int,
        *,
        rebalance: bool,
    ) -> None:
        phase = "rebalanced" if rebalance else "initial"
        region_max = self.phase2_region_concurrency_max if rebalance else SAFE_REGION_CONCURRENCY_MAX
        quota_max = self.phase2_disk_quota_mb_max if rebalance else SAFE_DISK_QUOTA_MB_MAX
        bwlimit_max = self.phase2_store_write_bwlimit_mib_max if rebalance else SAFE_WRITE_BWLIMIT_MIB_MAX
        bwlimit_min = self.phase2_store_write_bwlimit_mib_min if rebalance else SAFE_WRITE_BWLIMIT_MIB_MIN
        if region > region_max:
            raise ValueError(
                f"RG05 region_concurrency is outside the phase policy: value={region}, phase={phase!r}, "
                f"max={region_max}"
            )
        if not SAFE_DISK_QUOTA_MB_MIN <= quota <= quota_max:
            raise ValueError(
                f"RG05 disk_quota_mb is outside the phase policy: value={quota}, phase={phase!r}, "
                f"range={SAFE_DISK_QUOTA_MB_MIN}..{quota_max}"
            )
        if not bwlimit_min <= bwlimit <= bwlimit_max:
            raise ValueError(
                f"RG05 store_write_bwlimit_mib is outside the phase policy: value={bwlimit}, phase={phase!r}, "
                f"range={bwlimit_min}..{bwlimit_max}"
            )

    def wait(self, timeout_seconds: object) -> dict[str, object]:
        timeout = _require_positive_int(timeout_seconds, "timeout_seconds")
        deadline = time.monotonic() + timeout
        while True:
            result = self.status()
            import_state = result["import"]["state"]
            if import_state in {"reconfigure_required", "completed", "failed"}:
                return result
            if import_state == "ready_to_import":
                raise RuntimeError(
                    f"RG05 wait requires an active import: phase={self.phase!r}, "
                    f"container={self.container_name!r}"
                )
            if time.monotonic() >= deadline:
                return result
            time.sleep(1)

    def monitor_checkpoint(self) -> str:
        state = self._container_state()
        if state is None:
            return "stopped"
        logs = self._docker(
            ["logs", "--tail", str(CHECKPOINT_LOG_TAIL_LINES), self.container_name],
            timeout=30,
        )
        completed_chunks = self._completed_restore_chunks(logs)
        if self._reached_rebalance_threshold(logs, completed_chunks):
            self._request_rebalance(state, logs, completed_chunks)
            return "reconfigure_required"
        if not state["Running"]:
            return "stopped"
        return "running"

    def seed_history_jobs(self) -> None:
        """Park paused imports beside the active one so job triage needs evidence.

        Every decoy mirrors the active job's registry shape and presents the
        same ``reconfigure_required`` pause; only the frozen history separates
        them (per-job lightning series and incident-window records exist for
        the active job alone). Ids, target-table family (the incident's import
        table plus a batch suffix), sizes (one identical to the active row
        count, the rest straddling it), staging paths under the same scene
        root, and sorted order carry no signal, so blind guessing succeeds 1/8.
        """
        if self.other_jobs:
            raise RuntimeError(
                f"RG05 history jobs are already seeded: run_id={self.run_id!r}, "
                f"count={len(self.other_jobs)}"
            )
        size_ratios = (1.6, 0.7, 1.0, 0.45, 2.25, 0.85, 1.95)
        decoys = []
        for index, ratio in enumerate(size_ratios, start=1):
            table = f"{self.db}.{self.import_table}_batch{index:02d}"
            require_sql_success(
                self.env.execute_sql(
                    f"CREATE TABLE {table} ("
                    "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, "
                    "status VARCHAR(16) NOT NULL, order_ts DATETIME NOT NULL, "
                    "amount DECIMAL(12,2) NOT NULL, sku_id BIGINT NOT NULL, "
                    "region_id INT NOT NULL, payload VARCHAR(1024) NOT NULL, "
                    "KEY idx_batch_tenant_status (tenant_id, status), "
                    "KEY idx_batch_order_ts (order_ts)"
                    ")"
                ),
                f"create paused batch table {table}",
            )
            batch_root = self.source_dir.parent / f"batch{index:02d}"
            decoys.append({
                "job_id": lightning_decoy_job_id(self.run_id, index),
                "target": table,
                "state": "reconfigure_required",
                "phase": "reconfigure_required",
                "reconfigure_required": True,
                "exit_code": None,
                "expected_rows": int(self.row_count * ratio),
                "target_rows": 0,
                "phase1_rows": 0,
                "duration_seconds": None,
                "source_directory": str(batch_root / "dump"),
                "checkpoint_directory": str(batch_root / "checkpoint"),
            })
        self.other_jobs = tuple(decoys)

    def manage(
        self,
        *,
        action: str,
        region_concurrency: object,
        disk_quota_mb: object,
        store_write_bwlimit_mib: object,
        timeout_seconds: object,
        job_id: object = None,
    ) -> dict[str, object]:
        if action == "precheck":
            return self.precheck()
        if action == "apply_budget":
            return self.apply_budget(
                region_concurrency=region_concurrency,
                disk_quota_mb=disk_quota_mb,
                store_write_bwlimit_mib=store_write_bwlimit_mib,
                job_id=job_id,
            )
        if action == "wait":
            return self.wait(timeout_seconds)
        raise ValueError(f"RG05 unknown Lightning action: action={action!r}")

    def status(self) -> dict[str, object]:
        now = time.monotonic() if self.total_started_at is not None else None
        state = self._container_state()
        import_state = "failed" if self.failure_reason is not None else "ready_to_import"
        exit_code = None
        logs = ""
        duration_seconds = None
        rows = self._target_row_count()
        if (
            self.failure_reason is None
            and self.budget is not None
            and self.rebalance_count == 0
            and not self.rebalance_required
            and state is not None
        ):
            logs = self._docker(["logs", "--timestamps", self.container_name], timeout=30)
            completed_chunks = self._completed_restore_chunks(logs)
            if self._reached_rebalance_threshold(logs, completed_chunks):
                self._request_rebalance(state, logs, completed_chunks)
                state = None
            elif (
                state["Running"]
                and now is not None
                and now - self.total_started_at >= self.phase1_checkpoint_deadline_seconds
            ):
                self._fail_initial_checkpoint(
                    rows,
                    now,
                    "the initial budget did not reach the checkpoint handoff before the operational window expired",
                )
                state = None
            elif not state["Running"]:
                self._fail_initial_checkpoint(
                    rows,
                    now if now is not None else time.monotonic(),
                    "the initial import exited before the controller observed the required checkpoint handoff",
                )
                state = None
        if self.failure_reason is not None:
            import_state = "failed"
        elif self.rebalance_required:
            import_state = "reconfigure_required"
        elif state is not None:
            exit_code = int(state["ExitCode"])
            import_state = "running" if state["Running"] else ("completed" if exit_code == 0 else "failed")
            started_at = _parse_docker_timestamp(state["StartedAt"])
            if state["Running"]:
                finished_at = datetime.now(timezone.utc)
            else:
                finished_at = _parse_docker_timestamp(state["FinishedAt"])
            duration_seconds = round((finished_at - started_at).total_seconds(), 3)
            logs = self._docker(["logs", "--tail", "40", self.container_name], timeout=30)
            if not state["Running"]:
                self.phase = "completed" if exit_code == 0 else "failed"
                if self.phase2_started_at is not None and self.phase2_finished_at is None:
                    self.phase2_finished_at = time.time()
                if self.total_finished_at is None:
                    self.total_finished_at = now if now is not None else time.monotonic()
        elapsed_total = (
            None
            if self.total_started_at is None
            else round(
                (self.total_finished_at or now or time.monotonic()) - self.total_started_at,
                3,
            )
        )
        return {
            "status": "success",
            "job_id": lightning_job_id(self.run_id),
            "target": f"{self.db}.{self.import_table}",
            "import": {
                "state": import_state,
                "container": self.container_name,
                "exit_code": exit_code,
                "target_rows": rows,
                "expected_rows": self.row_count,
                "duration_seconds": duration_seconds,
                "deadline_seconds": None,
                "elapsed_total_seconds": elapsed_total,
                "phase": self.phase,
                "phase1_rows": self.phase1_rows,
                "phase1_visible_rows": self.phase1_visible_rows,
                "phase1_completed_chunks": list(self.phase1_completed_chunks),
                "phase2_started_at": self.phase2_started_at,
                "phase2_finished_at": self.phase2_finished_at,
                "reconfigure_required": self.rebalance_required,
                "failure_stage": self.failure_stage,
                "failure_reason": self.failure_reason,
                "failure_log_tail": self.failure_log_tail,
                "phase1_log_tail": self.phase1_log_tail,
                "log_tail": logs[-6000:],
            },
            "budget": self.budget,
            "budget_history": self.budget_history,
            "rebalance_count": self.rebalance_count,
            "other_jobs": list(self.other_jobs),
            "precheck": self.precheck_passed,
            "checkpoint_enabled": True,
            "safe_bounds": self.safe_bounds,
            "source": {
                "rows": self.row_count,
                "files": self.source_file_count,
                "directory": str(self.source_dir),
                "checkpoint_directory": str(self.checkpoint_dir),
            },
        }

    def _fail_initial_checkpoint(self, rows: int, finished_at: float, failure_reason: str) -> None:
        self.phase1_rows = rows
        self._history_logs = self._docker(
            ["logs", "--timestamps", self.container_name],
            timeout=30,
        )
        self.phase1_log_tail = self._history_logs[-6000:]
        state = self._container_state()
        if state is not None and state["Running"]:
            self._docker(["stop", "--time", "30", self.container_name], timeout=60)
        if state is not None:
            self._docker(["rm", self.container_name], timeout=60)
        self.failure_stage = "initial_checkpoint"
        self.failure_reason = failure_reason
        self.failure_log_tail = self.phase1_log_tail
        self.phase = "failed"
        self.total_finished_at = finished_at

    def _checkpoint_rows(self, logs: str) -> int | None:
        counts = [int(match.group("count")) for match in LIGHTNING_IMPORTED_COUNT_RE.finditer(logs)]
        if not counts:
            return None
        checkpoint_rows = max(counts)
        return checkpoint_rows if checkpoint_rows >= self.rebalance_after_rows else None

    def _handoff_chunk_count(self) -> int:
        return self.source_file_count

    def _phase1_checkpoint_rows(self, visible_rows: int, logs: str, chunks: tuple[int, ...]) -> int:
        return max(visible_rows, self._imported_rows(logs))

    def _reached_rebalance_threshold(self, logs: str, completed_chunks: tuple[int, ...]) -> bool:
        """Accept ingest progress or the controller's required restore chunk count."""
        return (
            self._checkpoint_rows(logs) is not None
            or len(completed_chunks) >= self._handoff_chunk_count()
        )

    def _request_rebalance(
        self,
        state: Mapping[str, object],
        logs: str,
        completed_chunks: tuple[int, ...],
    ) -> None:
        if not state["Running"]:
            raise RuntimeError(
                "RG05 Lightning completion was observed after the container stopped: "
                f"run_id={self.run_id!r}, container={self.container_name!r}, state={state!r}"
            )
        if len(completed_chunks) < self._handoff_chunk_count():
            raise RuntimeError(
                "RG05 Lightning partial handoff was requested before enough restore chunks completed: "
                f"run_id={self.run_id!r}, completed_chunks={completed_chunks!r}, "
                f"required_chunks={self._handoff_chunk_count()}"
            )
        if "import whole table completed" in logs or "restore table completed" in logs:
            raise RuntimeError(
                "RG05 Lightning log proves the table completed before the partial checkpoint handoff: "
                f"run_id={self.run_id!r}, container={self.container_name!r}, "
                f"completed_chunks={completed_chunks!r}, threshold={self.rebalance_after_rows}"
            )
        self._history_logs = self._docker(
            ["logs", "--timestamps", self.container_name],
            timeout=30,
        )
        self._docker(["stop", "--time", "5", self.container_name], timeout=60)
        stopped_logs = self._docker(
            ["logs", "--timestamps", self.container_name],
            timeout=30,
        )
        stopped_chunks = self._completed_restore_chunks(stopped_logs)
        if "import whole table completed" in stopped_logs or "restore table completed" in stopped_logs:
            raise RuntimeError(
                "RG05 Lightning completed the table while stopping instead of preserving remaining work: "
                f"run_id={self.run_id!r}, container={self.container_name!r}, "
                f"completed_chunks={stopped_chunks!r}"
            )
        if len(stopped_chunks) >= self.source_file_count * 2:
            raise RuntimeError(
                "RG05 Lightning completed every data engine before the partial checkpoint was retained: "
                f"run_id={self.run_id!r}, container={self.container_name!r}, "
                f"completed_chunks={stopped_chunks!r}, expected_chunks={self.source_file_count * 2}"
            )
        stopped_rows = self._target_row_count()
        if stopped_rows >= self.row_count:
            raise RuntimeError(
                "RG05 Lightning SQL target reached the full source count during the partial handoff: "
                f"run_id={self.run_id!r}, visible_rows={stopped_rows}, expected_rows={self.row_count}"
            )
        checkpoint_file = self.checkpoint_dir / "checkpoint.db"
        if not checkpoint_file.is_file() or checkpoint_file.stat().st_size == 0:
            raise RuntimeError(
                "RG05 Lightning did not leave a non-empty checkpoint database after partial handoff: "
                f"run_id={self.run_id!r}, checkpoint={str(checkpoint_file)!r}, "
                f"visible_rows={stopped_rows}, completed_chunks={stopped_chunks!r}"
            )
        self._docker(["rm", self.container_name], timeout=60)
        self.phase1_rows = self._phase1_checkpoint_rows(stopped_rows, stopped_logs, stopped_chunks)
        self.phase1_visible_rows = stopped_rows
        self.phase1_completed_chunks = stopped_chunks
        self._history_logs = stopped_logs
        self.phase1_log_tail = stopped_logs[-6000:]
        self.rebalance_required = True
        self.phase = "reconfigure_required"

    @staticmethod
    def _imported_rows(logs: str) -> int:
        counts = [int(match.group("count")) for match in LIGHTNING_IMPORTED_COUNT_RE.finditer(logs)]
        return max(counts, default=0)

    @staticmethod
    def _completed_restore_chunks(logs: str) -> tuple[int, ...]:
        chunks = {
            int(match.group("chunk"))
            for match in LIGHTNING_RESTORE_CHUNK_COMPLETED_RE.finditer(logs)
        }
        return tuple(sorted(chunks))

    def _remove_container(self) -> None:
        state = self._container_state()
        if state is None:
            return
        if state["Running"]:
            self._docker(["stop", "--time", "30", self.container_name], timeout=60)
        self._docker(["rm", self.container_name], timeout=60)

    def _target_row_count(self) -> int:
        payload = json_object(
            self.env.execute_sql(f"SELECT COUNT(*) FROM {self.db}.{self.import_table}"),
            f"count RG05 target {self.db}.{self.import_table}",
        )
        return int(payload["result"][0][0])

    def history_log_output(self, start_ms: int, end_ms: int) -> str:
        if self._history_logs:
            return self._history_logs
        state = self._container_state()
        if state is None:
            return ""
        return self._docker(["logs", "--timestamps", self.container_name], timeout=30)

    def cleanup(self) -> None:
        state = self._container_state()
        if state is not None:
            self._docker(["rm", "--force", self.container_name], timeout=60)
        if self.runtime_dir.exists():
            shutil.rmtree(self.runtime_dir)


class ChunkCheckpointLightningBudgetController(LightningBudgetController):
    """Ordinary RG05 counts encoded source coverage as checkpoint progress."""

    def _chunk_rows(self) -> int:
        return (self.row_count + self.source_file_count - 1) // self.source_file_count

    def _handoff_chunk_count(self) -> int:
        return (self.rebalance_after_rows + self._chunk_rows() - 1) // self._chunk_rows()

    def _phase1_checkpoint_rows(self, visible_rows: int, logs: str, chunks: tuple[int, ...]) -> int:
        return max(
            super()._phase1_checkpoint_rows(visible_rows, logs, chunks),
            len(chunks) * self._chunk_rows(),
        )


class TidbResourceGovernanceLightningBudgetInjector(BaseFaultInjector):
    """Provision an online business workload beside a real Lightning import."""

    def __init__(self) -> None:
        self.controller: LightningBudgetController | None = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self.controller.prepare()
        context.env.attach_import_controller(self.controller)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        context.env.attach_import_controller(self.controller)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context)
        business = json_object(
            context.env.execute_sql(
                f"SELECT COUNT(*), COALESCE(SUM(amount),0), MIN(order_id), MAX(order_id) "
                f"FROM {self.controller.db}.{self.controller.business_table}"
            ),
            "capture RG05 business baseline",
        )
        return {
            "rg05_import_contract": {
                "row_count": self.controller.row_count,
                "source_file_count": self.controller.source_file_count,
                "target": f"{self.controller.db}.{self.controller.import_table}",
                "checksum": "ADMIN CHECKSUM TABLE required",
                "analyze": "required",
            },
            "rg05_budget_bounds": self.controller.safe_bounds,
            "rg05_business_baseline": business["result"],
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self.controller.cleanup()
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.controller.db}"),
            f"drop RG05 database {self.controller.db}",
        )

    def _configure(self, context: FaultLifecycleContext) -> None:
        if self.controller is None:
            self.controller = ChunkCheckpointLightningBudgetController(context.env, context.config)


class TidbResourceGovernanceLightningBudgetScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_lightning_budget"
    description = (
        "Govern a real TiDB Lightning import under frontend workload, local sort-space, "
        "and downstream write-bandwidth constraints."
    )
    cases = (_CASE, _CONSERVATIVE_CASE)

    def build_fault_plan(
        self,
        case: TidbResourceGovernanceLightningBudgetCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernanceLightningBudgetInjector,
                config={
                    "db": case.db,
                    "import_table": case.import_table,
                    "business_table": case.business_table,
                    "inventory_table": case.inventory_table,
                    "row_count": case.row_count,
                    "source_file_count": case.source_file_count,
                    "business_row_count": case.business_row_count,
                    "inventory_row_count": case.inventory_row_count,
                    "phase1_checkpoint_deadline_seconds": case.phase1_checkpoint_deadline_seconds,
                    "phase1_region_concurrency": case.phase1_region_concurrency,
                    "phase1_disk_quota_mb": case.phase1_disk_quota_mb,
                    "phase1_store_write_bwlimit_mib": case.phase1_store_write_bwlimit_mib,
                    "rebalance_after_rows": case.rebalance_after_rows,
                    "phase2_region_concurrency_max": case.phase2_region_concurrency_max,
                    "phase2_disk_quota_mb_max": case.phase2_disk_quota_mb_max,
                    "phase2_store_write_bwlimit_mib_max": case.phase2_store_write_bwlimit_mib_max,
                    "phase2_store_write_bwlimit_mib_min": case.phase2_store_write_bwlimit_mib_min,
                    "staging_table": case.staging_table,
                    "staging_row_count": case.staging_row_count,
                },
            ),
        )
