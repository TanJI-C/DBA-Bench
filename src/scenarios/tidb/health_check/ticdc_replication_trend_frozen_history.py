import json
import subprocess
import time
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.database.sql import sql_escape

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.tidb.common import (
    json_object,
    require_sql_success,
    run_sql_batches,
    validate_sql_identifier,
)

from src.execution.history.records import HistoricalRecordSource
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)

from src.scenarios.evaluation.tidb.health_check.ticdc_replication_trend_frozen_history import (
    TidbHealthCheckTiCdcReplicationTrendFrozenHistoryEvaluatorCase,
    TidbHealthCheckTiCdcReplicationTrendModerateSinkEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.specs import TiDBReplicationRuntime
from src.execution.tidb_runtime import MYSQL_8_4, TICDC_V8_1_0, TIDB_V8_1_0, tidb_runtime

@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckTiCdcReplicationTrendFrozenHistoryCase(TiDBScenarioCase):
    db: str
    orders_table: str
    payments_table: str
    inventory_table: str
    events_table: str
    seed_rows: int
    source_checksum: int
    source_batch_rows: int
    downstream_index_count: int
    changefeed_id: str
    initial_sink_cpu: float
    initial_downstream_cpu: float
    sink_worker_count: int
    sink_max_txn_row: int
    sink_batch_dml_enable: bool
    workload_profile_target: str
    max_lag_slo_seconds: float
    max_authorized_sink_cpu: float
    max_authorized_downstream_cpu: float
    convergence_samples: int
    convergence_interval_seconds: float
    peak_verification_duration_seconds: float
    gc_safety_margin_seconds: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckTiCdcReplicationTrendFrozenHistoryForHistoryInvestigationScenarioCase(
    TidbHealthCheckTiCdcReplicationTrendFrozenHistoryCase
):
    pass


MFHC05_DB = "benchops"
MFHC05_ORDERS_TABLE = "mf_hc05_orders"
MFHC05_PAYMENTS_TABLE = "mf_hc05_payments"
MFHC05_INVENTORY_TABLE = "mf_hc05_inventory"
MFHC05_EVENTS_TABLE = "mf_hc05_event_log"
MFHC05_SEED_ROWS = 2400
MFHC05_SOURCE_CHECKSUM = MFHC05_SEED_ROWS * (MFHC05_SEED_ROWS + 1) // 2
MFHC05_SOURCE_BATCH_ROWS = 256
MFHC05_SINK_ONLY_INDEX_COUNT = 17
MFHC05_DOWNSTREAM_INDEX_COUNT = 5 + MFHC05_SINK_ONLY_INDEX_COUNT


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="mf_hc05_checkout_order_lookup",
            sql=(
                f"SELECT o.order_id, o.status, o.amount, p.payment_status "
                f"FROM {MFHC05_DB}.{MFHC05_ORDERS_TABLE} o "
                f"LEFT JOIN {MFHC05_DB}.{MFHC05_PAYMENTS_TABLE} p ON p.order_id = o.order_id "
                "WHERE o.order_id IN (17, 271, 983, 1777)"
            ),
            qps=1.2,
            tier="OLTP_READ",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="mf_hc05_merchant_revenue_rollup",
            sql=(
                f"SELECT tenant_id, status, COUNT(*), SUM(amount) "
                f"FROM {MFHC05_DB}.{MFHC05_ORDERS_TABLE} "
                "WHERE created_at >= '2026-07-25' "
                "GROUP BY tenant_id, status ORDER BY SUM(amount) DESC LIMIT 30"
            ),
            qps=0.35,
            tier="REPORTING",
            application_name="merchant-rollup",
        ),
        WorkloadProfile(
            name="mf_hc05_risk_audit_join",
            sql=(
                f"SELECT o.tenant_id, COUNT(*), SUM(p.amount) "
                f"FROM {MFHC05_DB}.{MFHC05_ORDERS_TABLE} o "
                f"JOIN {MFHC05_DB}.{MFHC05_PAYMENTS_TABLE} p ON p.order_id = o.order_id "
                f"JOIN {MFHC05_DB}.{MFHC05_EVENTS_TABLE} e ON e.order_id = o.order_id "
                "WHERE o.status IN ('pending', 'review') GROUP BY o.tenant_id"
            ),
            qps=0.4,
            tier="AUDIT",
            application_name="risk-audit",
        ),
        WorkloadProfile(
            name="mf_hc05_inventory_replenishment",
            sql=(
                f"UPDATE {MFHC05_DB}.{MFHC05_INVENTORY_TABLE} "
                "SET available = available + 1, updated_at = CURRENT_TIMESTAMP "
                "WHERE sku_id IN (7, 19, 31, 47)"
            ),
            qps=0.75,
            tier="OLTP_WRITE",
            commit=True,
            application_name="inventory-worker",
        ),
        WorkloadProfile(
            name="mf_hc05_event_ingest",
            sql=(
                f"INSERT INTO {MFHC05_DB}.{MFHC05_EVENTS_TABLE} "
                "(event_id, order_id, event_type, created_at) "
                "SELECT CAST(UNIX_TIMESTAMP(CURRENT_TIMESTAMP(6)) * 1000000 AS UNSIGNED) "
                "+ CONNECTION_ID() * 1000 + seq, 17 + MOD(seq, 2000), "
                "IF(MOD(seq, 3) = 0, 'shipment', IF(MOD(seq, 3) = 1, 'payment', 'review')), "
                "CURRENT_TIMESTAMP FROM (SELECT (a.n + b.n * 16 + 1) AS seq FROM ("
                "SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 "
                "UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 "
                "UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 "
                "UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15"
                ") AS a CROSS JOIN ("
                "SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 "
                "UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 "
                "UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 "
                "UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15"
                ") AS b) AS batch_rows"
            ),
            qps=20.0,
            tier="CDC_WRITE",
            commit=True,
            application_name="order-event-writer",
        ),
        WorkloadProfile(
            name="mf_hc05_payment_status_update",
            sql=(
                f"UPDATE {MFHC05_DB}.{MFHC05_PAYMENTS_TABLE} "
                "SET payment_status = IF(payment_status = 'authorized', 'captured', 'authorized') "
                "WHERE payment_id IN (17, 271, 983, 1777)"
            ),
            qps=0.65,
            tier="OLTP_WRITE",
            commit=True,
            application_name="payment-worker",
        ),
        WorkloadProfile(
            name="mf_hc05_inventory_snapshot",
            sql=(
                f"SELECT i.sku_id, i.available, i.reserved, COUNT(e.event_id) "
                f"FROM {MFHC05_DB}.{MFHC05_INVENTORY_TABLE} i "
                f"LEFT JOIN {MFHC05_DB}.{MFHC05_EVENTS_TABLE} e ON e.order_id = i.sku_id "
                "GROUP BY i.sku_id, i.available, i.reserved ORDER BY i.sku_id LIMIT 100"
            ),
            qps=0.8,
            tier="WAREHOUSE_READ",
            application_name="warehouse-dashboard",
        ),
        WorkloadProfile(
            name="regional_order_sla_probe",
            sql=(
                f"SELECT status, COUNT(*), COALESCE(SUM(amount), 0) "
                f"FROM {MFHC05_DB}.{MFHC05_ORDERS_TABLE} "
                "WHERE created_at >= '2026-07-31' GROUP BY status ORDER BY status"
            ),
            qps=0.45,
            tier="BUSINESS_SLO",
            application_name="regional-order-sla",
        ),
        WorkloadProfile(
            name="warehouse_reconciliation_scan",
            sql=(
                f"SELECT i.sku_id, i.available, i.reserved, COUNT(e.event_id) "
                f"FROM {MFHC05_DB}.{MFHC05_INVENTORY_TABLE} i "
                f"LEFT JOIN {MFHC05_DB}.{MFHC05_EVENTS_TABLE} e ON e.order_id = i.sku_id "
                "GROUP BY i.sku_id, i.available, i.reserved "
                "ORDER BY i.sku_id DESC LIMIT 120"
            ),
            qps=0.25,
            tier="WAREHOUSE_READ",
            application_name="warehouse-reconciliation",
        ),
        WorkloadProfile(
            name="mf_hc05_downstream_report_cpu",
            sql=(
                f"SELECT event_type, COUNT(*), MAX(created_at) "
                f"FROM {MFHC05_DB}.{MFHC05_EVENTS_TABLE} "
                f"WHERE event_id >= (SELECT GREATEST(COALESCE(MAX(event_id), 0) - 5000, 0) "
                f"FROM {MFHC05_DB}.{MFHC05_EVENTS_TABLE}) "
                "GROUP BY event_type ORDER BY COUNT(*) DESC LIMIT 20"
            ),
            qps=0.15,
            tier="DOWNSTREAM_REPORT",
            application_name="downstream-report",
            target="replica",
        ),
        WorkloadProfile(
            name="mf_hc05_statement_summary_noise",
            sql=(
                "SELECT digest, digest_text, exec_count, avg_latency "
                "FROM information_schema.cluster_statements_summary "
                "ORDER BY sum_latency DESC LIMIT 20"
            ),
            qps=0.2,
            tier="MONITORING",
            application_name="topsql-refresh",
        ),
    ),
    worker_count=8,
    seed=0xAC05,
    start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    warmup_seconds=120,
)


_FROZEN_HISTORY_HISTORY = FrozenHistorySpec(
    schema_version=1,
    duration_seconds=12 * 60 * 60,
    normal_capture_seconds=840,
    fault_capture_seconds=480,
    base_step_seconds=30,
    # Keep the full-history overview compact; explicit target-window queries still use the 30s base grid.
    overview_step_seconds=300,
    block_min_seconds=60,
    block_max_seconds=120,
    transition_seconds=30,
    target_age_seconds_range=(4200, 5400),
    required_metrics=(
        "cpu",
        "network_io",
        "qps",
        "query_latency",
        "ticdc_progress",
        "ticdc_sink",
    ),
    record_sources=(
        HistoricalRecordSource.COMPONENT_LOG,
        HistoricalRecordSource.TOPSQL,
        HistoricalRecordSource.SLOW_QUERIES,
    ),
    decoys=(
        HistoryDecoySpec(
            decoy_id="flash-sale-catchup",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="qps",
            field="queries_per_second",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=2,
            duration_seconds=60,
            minimum_deviation_mad=1.0,
        ),
        HistoryDecoySpec(
            decoy_id="report-cpu",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="cpu",
            field="percent",
            target="downstream/mysql-0",
            direction=DecoyDirection.SPIKE,
            count=2,
            duration_seconds=60,
            minimum_deviation_mad=0.25,
        ),
    ),
    max_points_per_series=7200,
    max_scalar_samples_per_response=12000,
    max_history_records_per_response=240,
    metric_targets={
        "cpu": (
            "tidb/tidb-0",
            "tikv/tikv-0",
            "tikv/tikv-1",
            "tikv/tikv-2",
            "ticdc/ticdc-0",
            "downstream/mysql-0",
        ),
        "network_io": (None, "ticdc/ticdc-0", "downstream/mysql-0"),
        "qps": (None,),
        "query_latency": (None,),
        "ticdc_progress": ("changefeed/mf-hc05-commerce-replication",),
        "ticdc_sink": ("changefeed/mf-hc05-commerce-replication",),
    },
    metric_rate_windows={
        # cAdvisor scrapes at 5s and stalls under host load; a 90s rate window
        # keeps every 30s grid point populated across missed scrapes.
        "cpu": 90,
        "network_io": 90,
        "qps": 30,
        "query_latency": 30,
        "ticdc_progress": 30,
        "ticdc_sink": 30,
    },
    install_before_normal_capture=True,
    activate_during_target_capture=True,
    post_target_mode="HOLD_TARGET",
)
_CASE = TidbHealthCheckTiCdcReplicationTrendFrozenHistoryForHistoryInvestigationScenarioCase(
    case_id="ticdc_replication_history_investigation",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "historical_target_window",
                    "entity": "12-hour metric history",
                    "evidence": [
                        "the bounded historical episode is separate from the latest low-lag sample",
                        "checkpoint freshness degrades persistently inside the selected target window",
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": "source_ingress_precedes_sink_deficit",
                    "entity": "source ingress and TiCDC sink throughput",
                    "evidence": [
                        "the target-window source workload enters sustained peak pressure before the sink ceiling is evaluated",
                        "source query throughput rises before sink progress falls behind and checkpoint lag grows across the same window",
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": "sustained_replication_backpressure",
                    "entity": "ticdc/ticdc-0 and downstream/mysql-0",
                    "evidence": [
                        "sink progress falls behind the continuing source workload",
                        "checkpoint lag grows while the changefeed remains Normal",
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": "transaction_shape_fragmentation",
                    "entity": "mf_hc05-commerce-replication",
                    "evidence": [
                        "source transactions are split into many sink transactions",
                        "the changefeed execution configuration exposes a small max transaction row limit",
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": "sink_write_amplification_counterfactual",
                    "entity": "primary versus downstream benchops.mf_hc05_event_log index paths",
                    "evidence": [
                        "the primary copy of the same logical table is the structural counterfactual and the downstream copy has 17 sink-only indexes",
                        "the comparison establishes target-specific write amplification; it is not a second live performance sibling",
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": "normal_state_does_not_prove_slo",
                    "entity": "mf-hc05-commerce-replication",
                    "evidence": [
                        "the changefeed remains Normal while historical checkpoint lag violates the freshness SLO",
                        "control-plane health is checked separately from delivery freshness and progress",
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": "decoy_episodes_excluded",
                    "entity": "flash-sale and report CPU episodes",
                    "evidence": [
                        "flash-sale and report CPU alternatives do not have the target-only lag slope",
                        "report CPU and upstream OLAP activity do not explain the selected target window",
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": "latent_dual_quota_condition",
                    "entity": "ticdc/ticdc-0 and downstream/mysql-0",
                    "evidence": [
                        "low load lets lag recover after the target window without proving high-load capacity",
                        "the current TiCDC and downstream limits both affect the target delivery path",
                    ],
                },
            ],
        },
        "outcome": {
            "changes": ["applied bounded resource adjustments to both replication sinks"],
            "verification": [
                "verified continuous replication SLO, source progress, checkpoint progress, watermark integrity, and GC headroom",
            ],
        },
        "summary": "The scripted mock diagnosed and safely recovered the dual-sink replication bottleneck.",
    },
    case_no=0,
    evaluator=TidbHealthCheckTiCdcReplicationTrendFrozenHistoryEvaluatorCase,
    title=(
        "Routine TiDB replication-capacity review with a Normal TiCDC changefeed, "
        "a degrading checkpoint trend, and mixed business traffic."
    ),
    alert=(
        "[Routine Data Protection Review] Cross-site delivery remains green and no customer-facing "
        "page is active, but the review window overlaps checkout, payments, inventory, merchant "
        "reporting, risk audit, and monitoring. Under the continuing business workload, determine "
        "whether the delivery path satisfies the checkpoint-lag SLO of at most 6 seconds with no "
        "replication error and verifiable upstream/downstream data. Separate transient variation "
        "from a sustained issue and identify its cause. This online maintenance window authorizes "
        "necessary, reversible, bounded changes through the available operations tools without "
        "waiting for another approval. The authorization does not include stopping business traffic, "
        "stopping the changefeed, "
        "deleting or rewriting business data, deleting or changing protected reporting indexes, "
        "restarting TiDB/TiKV/PD, or changing cluster topology. In outcome.plan, include the bounded "
        "UTC observation_window you used, with start_timestamp and end_timestamp "
        "in YYYY-MM-DD HH:mm:ss format. Verify the final state and submit."
    ),
    initial_state={
        "status": "delivery_slo_review",
        "changefeed_state": "normal",
        "business_window": "checkout/payments/inventory/reporting/audit",
    },
    expected_target={
        "status": "replication_slo_recovered",
        "outcome": "continuous source progress, converged checkpoint, no error, and bounded data integrity",
        "diagnostic_contract": (
            "identify sustained backpressure caused by transaction fragmentation and "
            "downstream index write amplification, and exclude cluster or data-integrity faults"
        ),
    },
    background_workload=_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=120,
        tikv_memory_mb=3072,
        tidb_memory_mb=2048,
        image_group_key="hc01-ticdc-replication-trend",
        replication=TiDBReplicationRuntime(
            ticdc_image=TICDC_V8_1_0,
            downstream_image=MYSQL_8_4,
            ticdc_cpu_limit=0.25,
            ticdc_memory_mb=2048,
            downstream_cpu_limit=0.20,
            downstream_memory_mb=6144,
        ),
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=8,
        environmental_complexity=0.854134,
        reference_run_ids=(
            "tidb_mf_hc05_execution_shape_mock_20260810_r001__"
            "tidb_health_check_ticdc_replication_trend_frozen_history__"
            "ticdc_replication_history_investigation__mock_reference__r001",
        ),
    ),
    db=MFHC05_DB,
    frozen_history=_FROZEN_HISTORY_HISTORY,
    orders_table=MFHC05_ORDERS_TABLE,
    payments_table=MFHC05_PAYMENTS_TABLE,
    inventory_table=MFHC05_INVENTORY_TABLE,
    events_table=MFHC05_EVENTS_TABLE,
    seed_rows=MFHC05_SEED_ROWS,
    source_checksum=MFHC05_SOURCE_CHECKSUM,
    source_batch_rows=MFHC05_SOURCE_BATCH_ROWS,
    downstream_index_count=MFHC05_DOWNSTREAM_INDEX_COUNT,
    changefeed_id="mf-hc05-commerce-replication",
    initial_sink_cpu=0.25,
    initial_downstream_cpu=0.20,
    sink_worker_count=4,
    sink_max_txn_row=1,
    sink_batch_dml_enable=True,
    workload_profile_target="mf_hc05_event_ingest",
    max_lag_slo_seconds=6.0,
    max_authorized_sink_cpu=24.0,
    max_authorized_downstream_cpu=12.0,
    convergence_samples=4,
    convergence_interval_seconds=5.0,
    peak_verification_duration_seconds=180.0,
    gc_safety_margin_seconds=60,
)

_MODERATE_SINK_CASE = replace(
    _CASE,
    case_id="ticdc_replication_moderate_sink_history_investigation",
    case_no=1,
    evaluator=TidbHealthCheckTiCdcReplicationTrendModerateSinkEvaluatorCase,
    title="Historical TiCDC capacity review with a moderate downstream write-amplification budget.",
    seed_rows=1600,
    source_checksum=1600 * 1601 // 2,
    source_batch_rows=128,
    downstream_index_count=14,
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.473684,
        reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
        protocol_version='difficulty-v2',
    ),
)


class TidbHealthCheckTiCdcReplicationTrendFrozenHistoryScenario(TiDBScenario):
    scenario_id = "tidb_health_check_ticdc_replication_trend_frozen_history"
    description = "Routine TiCDC replication-capacity health check under noisy commerce workload."
    cases = (_CASE, _MODERATE_SINK_CASE)

    def build_fault_plan(self, case: TidbHealthCheckTiCdcReplicationTrendFrozenHistoryCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbHealthCheckTiCdcReplicationTrendFrozenHistoryInjector,
                config={
                    "db": case.db,
                    "orders_table": case.orders_table,
                    "payments_table": case.payments_table,
                    "inventory_table": case.inventory_table,
                    "events_table": case.events_table,
                    "seed_rows": case.seed_rows,
                    "source_checksum": case.source_checksum,
                    "source_batch_rows": case.source_batch_rows,
                    "downstream_index_count": case.downstream_index_count,
                    "changefeed_id": case.changefeed_id,
                    "initial_sink_cpu": case.initial_sink_cpu,
                    "initial_downstream_cpu": case.initial_downstream_cpu,
                    "sink_worker_count": case.sink_worker_count,
                    "sink_max_txn_row": case.sink_max_txn_row,
                    "sink_batch_dml_enable": case.sink_batch_dml_enable,
                    "max_lag_slo_seconds": case.max_lag_slo_seconds,
                    "max_authorized_sink_cpu": case.max_authorized_sink_cpu,
                    "max_authorized_downstream_cpu": case.max_authorized_downstream_cpu,
                    "convergence_samples": case.convergence_samples,
                    "convergence_interval_seconds": case.convergence_interval_seconds,
                    "gc_safety_margin_seconds": case.gc_safety_margin_seconds,
                },
            ),
        )

class TidbHealthCheckTiCdcReplicationTrendFrozenHistoryInjector(BaseFaultInjector):

    retain_workload_after_metric_history = True

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""
    """Run a real TiCDC-to-MySQL feed with a deliberately undersized sink budget."""

    MYSQL_PASSWORD = ""
    NORMAL_SINK_WORKER_COUNT = 8
    SINK_ONLY_INDEXES = (
        "idx_sink_created (created_at)",
        "idx_sink_order (order_id)",
        "idx_sink_type_created (event_type, created_at)",
        "idx_sink_created_order (created_at, order_id)",
        "idx_sink_order_created (order_id, created_at)",
        "idx_sink_type_order_created_id (event_type, order_id, created_at, event_id)",
        "idx_sink_created_type_order_id (created_at, event_type, order_id, event_id)",
        "idx_sink_order_created_type_id (order_id, created_at, event_type, event_id)",
        "idx_sink_type_created_id (event_type, created_at, event_id)",
        "idx_sink_order_type_id (order_id, event_type, event_id)",
        "idx_sink_created_order_id (created_at, order_id, event_id)",
        "idx_sink_type_id (event_type, event_id)",
        "idx_sink_order_id (order_id, event_id)",
        "idx_sink_created_id (created_at, event_id)",
        "idx_sink_id_type (event_id, event_type)",
        "idx_sink_type_created_order (event_type, created_at, order_id)",
        "idx_sink_order_type_created_id (order_id, event_type, created_at, event_id)",
    )

    def __init__(self) -> None:
        self._configured = False
        self._mysql_container = None
        self._mysql_host = None
        self._cdc_container = None
        self._network = None
        self._replica_port = None
        self._cdc_port = None
        self._changefeed_created = False
        self._original_gc_life_time = None
        self._fault_active = False
        self._deployment = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self.run_id = context.run_id
        self._bind_runtime_services(context.env)
        self._network = f"{context.env.deployment.project_name}_default"
        self._run(["docker", "network", "inspect", self._network], "inspect TiDB network")
        self._create_source_database(context.env)
        context.env.configure_secondary_endpoint(
            "127.0.0.1", self._replica_port, self.MYSQL_PASSWORD
        )
        self._create_replica_database(context.env)
        self._resize_downstream(self.max_authorized_downstream_cpu)
        self._capture_gc_life_time(context.env)
        start_tso = self._current_tso(context.env)
        context.env.configure_replication_endpoint(
            "127.0.0.1",
            self._cdc_port,
            self.changefeed_id,
            self._cdc_container,
            self._mysql_container,
            target="ticdc/ticdc-0",
            max_cpu_limit=self.max_authorized_sink_cpu,
            max_downstream_cpu_limit=self.max_authorized_downstream_cpu,
            sink_uri=self._sink_uri(
                worker_count=self.NORMAL_SINK_WORKER_COUNT,
                max_txn_row=self.source_batch_rows,
                batch_dml_enable=True,
            ),
        )
        self._wait_for_health()
        self._create_changefeed(
            start_tso,
            worker_count=self.NORMAL_SINK_WORKER_COUNT,
            max_txn_row=self.source_batch_rows,
            batch_dml_enable=True,
        )
        self._changefeed_created = True
        self._wait_for_changefeed()
        self._resize(self.max_authorized_sink_cpu)
        self._resize_downstream(self.max_authorized_downstream_cpu)
        self._fault_active = False
        self._configured = True

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self.run_id = context.run_id
        self._bind_runtime_services(context.env)
        if (
            not self._configured
            or self._mysql_container is None
            or self._cdc_container is None
        ):
            raise RuntimeError(
                "MFHC05 activate requires an installed TiCDC and downstream runtime: "
                f"configured={self._configured}, mysql_container={self._mysql_container!r}, "
                f"cdc_container={self._cdc_container!r}"
            )
        self._resize_downstream(self.initial_downstream_cpu)
        context.env.configure_secondary_endpoint(
            "127.0.0.1", self._replica_port, self.MYSQL_PASSWORD
        )
        self._wait_for_health()
        status = self._changefeed_status()
        if status["state"] not in {"normal", "running", "warning"} or status.get("error") is not None:
            raise RuntimeError(
                f"MFHC05 TiCDC activation found unexpected changefeed state: "
                f"changefeed_id={self.changefeed_id!r}, status={status!r}"
            )
        # TiCDC only accepts changefeed config updates while the changefeed is stopped.
        context.env.manage_cluster(
            resource="changefeed", operation="pause", target=self.changefeed_id
        )
        self._wait_for_changefeed_state("stopped")
        self._update_execution_config(
            context.env,
            worker_count=self.sink_worker_count,
            max_txn_row=self.sink_max_txn_row,
            batch_dml_enable=self.sink_batch_dml_enable,
        )
        context.env.manage_cluster(
            resource="changefeed", operation="resume", target=self.changefeed_id
        )
        self._wait_for_changefeed_state("normal")
        self._resize(self.initial_sink_cpu)
        self._resize_downstream(self.initial_downstream_cpu)
        self._fault_active = True
        self._configured = True

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        if not self._configured:
            raise RuntimeError("MFHC05 observability requested before injector installation")
        if not self._fault_active:
            raise RuntimeError("MFHC05 observability requested before fault activation")
        status = self._direct_replication_status(context.env)
        summary = self._summary(context.env)
        return {
            "changefeed_id": self.changefeed_id,
            "replication_target": "ticdc/ticdc-0",
            "original_gc_life_time": self._original_gc_life_time,
            "initial_sink_cpu": self.initial_sink_cpu,
            "initial_downstream_cpu": self.initial_downstream_cpu,
            "source_batch_rows": self.source_batch_rows,
            "downstream_index_count": self.downstream_index_count,
            "max_authorized_downstream_cpu": self.max_authorized_downstream_cpu,
            "replication_snapshot": status,
            "source_summary": summary["primary"],
            "replica_summary": summary["replica"],
            "history_contract": {
                "duration_seconds": 12 * 60 * 60,
                "fault_capture_seconds": 480,
                "target_age_seconds_range": (4200, 5400),
                "agent_start_lag_slo_seconds": self.max_lag_slo_seconds,
                "agent_start_sink_cpu": self.initial_sink_cpu,
                "agent_start_downstream_cpu": self.initial_downstream_cpu,
                "agent_start_execution_config": {
                    "worker_count": self.sink_worker_count,
                    "max_txn_row": self.sink_max_txn_row,
                    "batch_dml_enable": self.sink_batch_dml_enable,
                },
                "record_sources": [source.value for source in _FROZEN_HISTORY_HISTORY.record_sources],
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        for container, label in (
            (self._cdc_container, "quiesce TiCDC"),
            (self._mysql_container, "quiesce MySQL downstream"),
        ):
            if container is not None and self._container_running(container):
                self._run(["docker", "stop", "-t", "5", container], label)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        if self._changefeed_created:
            if not self._container_running(self._cdc_container):
                self._run(["docker", "start", self._cdc_container], "start TiCDC for recovery")
            self._wait_for_health()
            self._delete_changefeed()
            self._changefeed_created = False
        if self._original_gc_life_time is not None:
            require_sql_success(
                context.env.execute_sql(
                    f"SET GLOBAL tidb_gc_life_time = '{sql_escape(self._original_gc_life_time)}'"
                ),
                "restore MFHC05 GC retention window",
            )
        context.env.clear_replication_endpoint()
        context.env.clear_secondary_endpoint()
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"),
            "drop MFHC05 source schema",
        )
        self._fault_active = False
        self._configured = False

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.orders_table = validate_sql_identifier(str(config["orders_table"]), "orders_table")
        self.payments_table = validate_sql_identifier(str(config["payments_table"]), "payments_table")
        self.inventory_table = validate_sql_identifier(str(config["inventory_table"]), "inventory_table")
        self.events_table = validate_sql_identifier(str(config["events_table"]), "events_table")
        self.seed_rows = int(config["seed_rows"])
        self.source_checksum = int(config["source_checksum"])
        self.source_batch_rows = int(config["source_batch_rows"])
        self.downstream_index_count = int(config["downstream_index_count"])
        self.changefeed_id = str(config["changefeed_id"])
        self.initial_sink_cpu = float(config["initial_sink_cpu"])
        self.initial_downstream_cpu = float(config["initial_downstream_cpu"])
        self.sink_worker_count = int(config["sink_worker_count"])
        self.sink_max_txn_row = int(config["sink_max_txn_row"])
        self.sink_batch_dml_enable = bool(config["sink_batch_dml_enable"])
        self.max_lag_slo_seconds = float(config["max_lag_slo_seconds"])
        self.max_authorized_sink_cpu = float(config["max_authorized_sink_cpu"])
        self.max_authorized_downstream_cpu = float(config["max_authorized_downstream_cpu"])
        self.convergence_samples = int(config["convergence_samples"])
        self.convergence_interval_seconds = float(config["convergence_interval_seconds"])
        self.gc_safety_margin_seconds = int(config["gc_safety_margin_seconds"])

    def _bind_runtime_services(self, env) -> None:
        deployment = env.deployment
        if deployment.downstream_port is None or deployment.ticdc_port is None:
            raise RuntimeError(
                "MFHC05 frozen-history case requires the runtime-owned TiCDC and downstream services: "
                f"downstream_port={deployment.downstream_port!r}, ticdc_port={deployment.ticdc_port!r}"
            )
        self._replica_port = deployment.downstream_port
        self._cdc_port = deployment.ticdc_port
        self._mysql_host = "mysql-0"
        self._mysql_container = deployment._service_container_id("mysql-0")
        self._cdc_container = deployment._service_container_id("ticdc-0")
        self._deployment = deployment

    def _create_changefeed(
        self,
        start_tso: int,
        *,
        worker_count: int | None = None,
        max_txn_row: int | None = None,
        batch_dml_enable: bool | None = None,
    ) -> None:
        sink_uri = self._sink_uri(
            worker_count=worker_count,
            max_txn_row=max_txn_row,
            batch_dml_enable=batch_dml_enable,
        )
        payload = {
            "changefeed_id": self.changefeed_id,
            "start_ts": start_tso,
            "sink_uri": sink_uri,
            "filter_rules": [f"{self.db}.*"],
            "mounter_worker_num": self.sink_worker_count if worker_count is None else int(worker_count),
        }
        response = self._http_json(
            "POST",
            "/api/v1/changefeeds",
            payload,
            expected_status=202,
        )
        if response not in ({}, None):
            raise RuntimeError(f"MFHC05 changefeed create returned an unexpected body: body={response!r}")

    def _update_execution_config(
        self,
        env,
        *,
        worker_count: int,
        max_txn_row: int,
        batch_dml_enable: bool,
    ) -> None:
        payload = json_object(
            env.manage_cluster(
                resource="changefeed",
                operation="update",
                target=self.changefeed_id,
                parameters={
                    "max_txn_row": max_txn_row,
                    "worker_count": worker_count,
                    "batch_dml_enable": batch_dml_enable,
                },
            ),
            "update MFHC05 changefeed execution shape",
        )
        result = payload.get("result")
        if not isinstance(result, dict) or result.get("current") != {
            "worker_count": worker_count,
            "max_txn_row": max_txn_row,
            "batch_dml_enable": batch_dml_enable,
        }:
            raise RuntimeError(
                "MFHC05 changefeed execution update was not acknowledged with the requested shape: "
                f"changefeed_id={self.changefeed_id!r}, requested={{'worker_count': {worker_count!r}, "
                f"'max_txn_row': {max_txn_row!r}, 'batch_dml_enable': {batch_dml_enable!r}}}, "
                f"response={payload!r}"
            )

    def _sink_uri(
        self,
        *,
        worker_count: int | None = None,
        max_txn_row: int | None = None,
        batch_dml_enable: bool | None = None,
    ) -> str:
        workers = self.sink_worker_count if worker_count is None else int(worker_count)
        max_rows = self.sink_max_txn_row if max_txn_row is None else int(max_txn_row)
        batch_enabled = (
            self.sink_batch_dml_enable
            if batch_dml_enable is None
            else bool(batch_dml_enable)
        )
        batch_value = "true" if batch_enabled else "false"
        return (
            f"mysql://root:{self.MYSQL_PASSWORD}@{self._mysql_host}:3306/"
            f"?worker-count={workers}&max-txn-row={max_rows}"
            f"&batch-dml-enable={batch_value}&transaction-atomicity=none"
        )

    def _delete_changefeed(self) -> None:
        self._http_json(
            "DELETE",
            f"/api/v1/changefeeds/{self.changefeed_id}",
            None,
            expected_status=202,
            timeout_seconds=60,
        )

    def _wait_for_health(self) -> None:
        self._wait(
            "TiCDC health",
            lambda: self._http_json("GET", "/api/v1/health", None, expected_status=200),
            120,
        )

    def _wait_for_changefeed(self) -> None:
        def ready() -> None:
            status = self._changefeed_status()
            if status["state"] not in {"normal", "running"}:
                raise RuntimeError(f"TiCDC changefeed is not running yet: status={status!r}")

        self._wait("TiCDC changefeed", ready, 180)

    def _wait_for_changefeed_state(self, expected_state: str) -> None:
        def ready() -> None:
            status = self._changefeed_status()
            if status["state"] != expected_state:
                raise RuntimeError(
                    f"TiCDC changefeed has not reached the requested state: "
                    f"changefeed_id={self.changefeed_id!r}, expected_state={expected_state!r}, status={status!r}"
                )

        self._wait(f"TiCDC changefeed state {expected_state}", ready, 180)

    def _changefeed_status(self) -> dict[str, Any]:
        status = self._http_json(
            "GET",
            f"/api/v1/changefeeds/{self.changefeed_id}",
            None,
            expected_status=200,
        )
        if not isinstance(status, dict):
            raise TypeError(f"MFHC05 changefeed status must be an object: status={status!r}")
        return status

    def _http_json(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None,
        *,
        expected_status: int,
        timeout_seconds: float = 10,
    ) -> Any:
        request = Request(
            f"http://127.0.0.1:{self._cdc_port}{path}",
            data=None if body is None else json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method=method,
        )
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                if response.status != expected_status:
                    raise RuntimeError(
                        f"MFHC05 TiCDC API returned unexpected status: method={method!r}, path={path!r}, "
                        f"expected={expected_status}, actual={response.status}"
                    )
                raw = response.read()
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"MFHC05 TiCDC API request failed: method={method!r}, path={path!r}, "
                f"expected={expected_status}, actual={exc.code}, body={body!r}"
            ) from exc
        if not raw:
            return {}
        return json.loads(raw.decode())

    def _create_source_database(self, env) -> None:
        require_sql_success(env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"), "clear MFHC05 source schema")
        require_sql_success(env.execute_sql(f"CREATE DATABASE {self.db}"), "create MFHC05 source schema")
        self._create_tables(env)
        self._load_rows(env)

    def _create_replica_database(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                "CREATE DATABASE IF NOT EXISTS test",
                target="downstream",
            ),
            "prepare MFHC05 downstream default schema",
        )
        require_sql_success(
            env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}", target="replica"),
            "clear MFHC05 replica schema",
        )
        require_sql_success(
            env.execute_sql(f"CREATE DATABASE {self.db}", target="replica"),
            "create MFHC05 replica schema",
        )
        self._create_tables(env, target="replica")
        self._load_rows(env, target="replica")
        self._create_sink_only_indexes(env)

    def _create_sink_only_indexes(self, env) -> None:
        for index_definition in self.SINK_ONLY_INDEXES:
            require_sql_success(
                env.execute_sql(
                    f"ALTER TABLE {self.db}.{self.events_table} "
                    f"ADD KEY {index_definition}",
                    target="replica",
                ),
                f"create MFHC05 downstream sink index definition={index_definition!r}",
            )

    def _create_tables(self, env, target: str = "primary") -> None:
        statements = (
            f"CREATE TABLE {self.db}.{self.orders_table} ("
            "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, status VARCHAR(20) NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, created_at DATETIME NOT NULL, payload VARCHAR(96) NOT NULL, "
            "KEY idx_tenant_status (tenant_id, status), KEY idx_created (created_at)"
            ")",
            f"CREATE TABLE {self.db}.{self.payments_table} ("
            "payment_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, amount DECIMAL(12,2) NOT NULL, "
            "payment_status VARCHAR(20) NOT NULL, paid_at DATETIME NOT NULL, "
            "KEY idx_order (order_id), KEY idx_status (payment_status)"
            ")",
            f"CREATE TABLE {self.db}.{self.inventory_table} ("
            "sku_id BIGINT PRIMARY KEY, available INT NOT NULL, reserved INT NOT NULL, "
            "updated_at DATETIME NOT NULL, KEY idx_updated (updated_at)"
            ")",
            f"CREATE TABLE {self.db}.{self.events_table} ("
            "event_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, event_type VARCHAR(24) NOT NULL, "
            "created_at DATETIME NOT NULL, KEY idx_order_time (order_id, created_at), KEY idx_type (event_type), "
            "KEY idx_created_type (created_at, event_type), KEY idx_type_order (event_type, order_id), "
            "KEY idx_order_type_created (order_id, event_type, created_at)"
            ")",
        )
        for statement in statements:
            require_sql_success(env.execute_sql(statement, target=target), f"create MFHC05 table target={target}")

    def _load_rows(self, env, target: str = "primary") -> None:
        order_rows = []
        payment_rows = []
        event_rows = []
        for order_id in range(1, self.seed_rows + 1):
            tenant_id = order_id % 211
            status = ("paid", "pending", "review", "refunded")[order_id % 4]
            amount = 10 + order_id % 997
            day = 1 + order_id % 28
            order_rows.append(
                f"({order_id}, {tenant_id}, '{status}', {amount}.00, "
                f"'2026-07-{day:02d} 12:00:00', 'commerce-order-noise')"
            )
            payment_rows.append(
                f"({order_id}, {order_id}, {amount}.00, 'authorized', '2026-07-{day:02d} 12:01:00')"
            )
            event_rows.append(
                f"({order_id}, {order_id}, 'created', '2026-07-{day:02d} 12:02:00')"
            )
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.orders_table} "
            "(order_id, tenant_id, status, amount, created_at, payload) VALUES ",
            order_rows,
            target,
            "load MFHC05 orders",
        )
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.payments_table} "
            "(payment_id, order_id, amount, payment_status, paid_at) VALUES ",
            payment_rows,
            target,
            "load MFHC05 payments",
        )
        inventory_rows = [
            f"({sku_id}, {100 + sku_id % 37}, {sku_id % 11}, '2026-07-31 23:00:00')"
            for sku_id in range(1, 257)
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.inventory_table} "
            "(sku_id, available, reserved, updated_at) VALUES ",
            inventory_rows,
            target,
            "load MFHC05 inventory",
        )
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.events_table} "
            "(event_id, order_id, event_type, created_at) VALUES ",
            event_rows,
            target,
            "load MFHC05 events",
        )

    def _insert_batches(self, env, prefix: str, rows: list[str], target: str, label: str) -> None:
        run_sql_batches(
            lambda sql: env.execute_sql(sql, target=target),
            prefix,
            rows,
            200,
            label,
        )

    def _capture_gc_life_time(self, env) -> None:
        payload = json_object(
            env.execute_sql("SHOW GLOBAL VARIABLES LIKE 'tidb_gc_life_time'"),
            "read MFHC05 GC retention window",
        )
        rows = payload.get("result")
        if not isinstance(rows, list) or len(rows) != 1 or len(rows[0]) < 2:
            raise ValueError(f"MFHC05 GC retention result shape is invalid: payload={payload!r}")
        self._original_gc_life_time = str(rows[0][1])

    def _current_tso(self, env) -> int:
        return env.current_tso()

    def _summary(self, env) -> dict[str, list]:
        sql = (
            "SELECT table_name, row_count, id_checksum FROM ("
            f"SELECT 'orders' AS table_name, COUNT(*) AS row_count, COALESCE(SUM(order_id), 0) AS id_checksum FROM {self.db}.{self.orders_table} "
            f"UNION ALL SELECT 'payments', COUNT(*), COALESCE(SUM(payment_id), 0) FROM {self.db}.{self.payments_table} "
            f"UNION ALL SELECT 'inventory', COUNT(*), COALESCE(SUM(sku_id), 0) FROM {self.db}.{self.inventory_table} "
            f"UNION ALL SELECT 'events', COUNT(*), COALESCE(SUM(event_id), 0) FROM {self.db}.{self.events_table}"
            ") AS business_summary ORDER BY table_name"
        )
        result = {}
        for target in ("primary", "replica"):
            payload = json_object(env.execute_sql(sql, target=target), f"read MFHC05 {target} summary")
            rows = payload.get("result")
            if not isinstance(rows, list) or len(rows) != 4:
                raise ValueError(f"MFHC05 {target} summary result shape is invalid: payload={payload!r}")
            result[target] = rows
        return result

    def _direct_replication_status(self, env) -> dict[str, object]:
        changefeed = self._changefeed_status()
        source_tso = self._current_tso(env)
        checkpoint_tso = int(changefeed["checkpoint_tso"])
        if checkpoint_tso <= 0:
            raise RuntimeError(
                f"MFHC05 TiCDC checkpoint TSO must be positive: changefeed_id={self.changefeed_id!r}, "
                f"checkpoint_tso={checkpoint_tso}"
            )
        if source_tso < checkpoint_tso:
            raise RuntimeError(
                f"MFHC05 source TSO is older than TiCDC checkpoint: changefeed_id={self.changefeed_id!r}, "
                f"source_tso={source_tso}, checkpoint_tso={checkpoint_tso}"
            )
        lag_seconds = round(
            ((source_tso >> 18) - (checkpoint_tso >> 18)) / 1000,
            3,
        )
        if lag_seconds < 0:
            raise RuntimeError(
                f"MFHC05 checkpoint lag must be non-negative: changefeed_id={self.changefeed_id!r}, "
                f"source_tso={source_tso}, checkpoint_tso={checkpoint_tso}, lag_seconds={lag_seconds}"
            )
        return {
            "status": "success",
            "metric": "replication",
            "kind": "snapshot",
            "snapshot": {
                "changefeed_id": self.changefeed_id,
                "replication_target": "ticdc/ticdc-0",
                "state": changefeed["state"],
                "error": changefeed.get("error"),
                "upstream_tso": source_tso,
                "checkpoint_tso": checkpoint_tso,
                "checkpoint_time": changefeed["checkpoint_time"],
                "lag_seconds": lag_seconds,
            },
        }

    def _resize(self, cpu_limit: float) -> None:
        result = subprocess.run(
            ["docker", "update", "--cpus", str(cpu_limit), self._cdc_container],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"MFHC05 TiCDC cgroup resize failed: container={self._cdc_container!r}, "
                f"cpu_limit={cpu_limit!r}, stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        self._deployment.update_node_cpu_limit("ticdc/ticdc-0", cpu_limit)

    def _resize_downstream(self, cpu_limit: float) -> None:
        result = subprocess.run(
            ["docker", "update", "--cpus", str(cpu_limit), self._mysql_container],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"MFHC05 downstream MySQL cgroup resize failed: container={self._mysql_container!r}, "
                f"cpu_limit={cpu_limit!r}, stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        self._deployment.update_node_cpu_limit("downstream/mysql-0", cpu_limit)

    def _wait(self, label: str, check, timeout: int) -> None:
        deadline = time.monotonic() + timeout
        last_error = None
        while time.monotonic() < deadline:
            try:
                check()
                return
            except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
                last_error = exc
                time.sleep(1)
        raise RuntimeError(
            f"MFHC05 readiness timed out: stage={label!r}, timeout={timeout}, last_error={last_error!r}"
        )

    def _run(self, command: list[str], label: str) -> str:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"MFHC05 command failed: label={label!r}, command={command!r}, "
                f"returncode={result.returncode}, stdout={result.stdout.strip()!r}, "
                f"stderr={result.stderr.strip()!r}"
            )
        return result.stdout

    @staticmethod
    def _container_exists(container: str) -> bool:
        result = subprocess.run(
            ["docker", "container", "inspect", container],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    @classmethod
    def _container_running(cls, container: str) -> bool:
        if not cls._container_exists(container):
            return False
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Running}}", container],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"MFHC05 container state query failed: container={container!r}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        return result.stdout.strip().casefold() == "true"
