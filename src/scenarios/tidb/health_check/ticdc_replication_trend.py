import json
import re

import socket

import subprocess

import threading

import time

from collections.abc import Mapping

from datetime import datetime, timedelta

from typing import Any

from urllib.error import HTTPError

from urllib.request import Request, urlopen
from pymysql.err import OperationalError

from src.database.sql import sql_escape

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    join_thread,
    require_sql_success,
    run_sql_batches,
    validate_sql_identifier,
)

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.health_check.ticdc_replication_trend import (
    TidbHealthCheckTiCdcReplicationTrendEvaluatorCase,
    TidbHealthCheckTiCdcReplicationTrendForDownstreamCapacityEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime



@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckTiCdcReplicationTrendCase(TiDBScenarioCase):
    db: str
    observation_table: str
    history_table: str
    orders_table: str
    payments_table: str
    inventory_table: str
    events_table: str
    seed_rows: int
    source_checksum: int
    source_batch_rows: int
    downstream_index_count: int
    replica_port_offset: int
    cdc_port_offset: int
    changefeed_id: str
    initial_sink_cpu: float
    initial_downstream_cpu: float
    sink_worker_count: int
    sink_max_txn_row: int
    sink_batch_dml_enable: bool
    max_lag_slo_seconds: float
    max_authorized_sink_cpu: float
    max_authorized_downstream_cpu: float
    convergence_samples: int
    convergence_interval_seconds: float
    gc_safety_margin_seconds: int
    history_sample_count: int = 2016
    history_transient_decoys: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckTiCdcReplicationTrendForCapacityReviewScenarioCase(
    TidbHealthCheckTiCdcReplicationTrendCase
):
    pass


HC05_DB = "benchops"
HC05_OBSERVATION_TABLE = "hc05_replication_observations"
HC05_HISTORY_TABLE = "hc05_capacity_history"
HC05_ORDERS_TABLE = "hc05_orders"
HC05_PAYMENTS_TABLE = "hc05_payments"
HC05_INVENTORY_TABLE = "hc05_inventory"
HC05_EVENTS_TABLE = "hc05_event_log"
HC05_SEED_ROWS = 2400
HC05_SOURCE_CHECKSUM = HC05_SEED_ROWS * (HC05_SEED_ROWS + 1) // 2
HC05_SOURCE_BATCH_ROWS = 256
HC05_BASE_DOWNSTREAM_INDEX_COUNT = 5
HC05_SINK_ONLY_INDEX_COUNT = 17
HC05_DOWNSTREAM_INDEX_COUNT = HC05_BASE_DOWNSTREAM_INDEX_COUNT + HC05_SINK_ONLY_INDEX_COUNT
HC05_HEALTHY_SIBLING_ID = "hc05-warehouse-replication"


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="hc05_checkout_order_lookup",
            sql=(
                f"SELECT o.order_id, o.status, o.amount, p.payment_status "
                f"FROM {HC05_DB}.{HC05_ORDERS_TABLE} o "
                f"LEFT JOIN {HC05_DB}.{HC05_PAYMENTS_TABLE} p ON p.order_id = o.order_id "
                "WHERE o.order_id IN (17, 271, 983, 1777)"
            ),
            qps=1.2,
            tier="OLTP_READ",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="hc05_merchant_revenue_rollup",
            sql=(
                f"SELECT tenant_id, status, COUNT(*), SUM(amount) "
                f"FROM {HC05_DB}.{HC05_ORDERS_TABLE} "
                "WHERE created_at >= '2026-07-25' "
                "GROUP BY tenant_id, status ORDER BY SUM(amount) DESC LIMIT 30"
            ),
            qps=0.35,
            tier="REPORTING",
            application_name="merchant-rollup",
        ),
        WorkloadProfile(
            name="hc05_risk_audit_join",
            sql=(
                f"SELECT o.tenant_id, COUNT(*), SUM(p.amount) "
                f"FROM {HC05_DB}.{HC05_ORDERS_TABLE} o "
                f"JOIN {HC05_DB}.{HC05_PAYMENTS_TABLE} p ON p.order_id = o.order_id "
                f"JOIN {HC05_DB}.{HC05_EVENTS_TABLE} e ON e.order_id = o.order_id "
                "WHERE o.status IN ('pending', 'review') GROUP BY o.tenant_id"
            ),
            qps=0.4,
            tier="AUDIT",
            application_name="risk-audit",
        ),
        WorkloadProfile(
            name="hc05_inventory_replenishment",
            sql=(
                f"UPDATE {HC05_DB}.{HC05_INVENTORY_TABLE} "
                "SET available = available + 1, updated_at = CURRENT_TIMESTAMP "
                "WHERE sku_id IN (7, 19, 31, 47)"
            ),
            qps=0.75,
            tier="OLTP_WRITE",
            commit=True,
            application_name="inventory-worker",
        ),
        WorkloadProfile(
            name="hc05_event_ingest_batch",
            sql=(
                f"INSERT INTO {HC05_DB}.{HC05_EVENTS_TABLE} "
                "(event_id, order_id, event_type, created_at) "
                "SELECT CAST(UNIX_TIMESTAMP(CURRENT_TIMESTAMP(6)) * 1000000 AS UNSIGNED) "
                "+ CONNECTION_ID() * 1000000 + seq, 17 + MOD(seq, 2000), "
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
            name="hc05_payment_status_update",
            sql=(
                f"UPDATE {HC05_DB}.{HC05_PAYMENTS_TABLE} "
                "SET payment_status = IF(payment_status = 'authorized', 'captured', 'authorized') "
                "WHERE payment_id IN (17, 271, 983, 1777)"
            ),
            qps=0.65,
            tier="OLTP_WRITE",
            commit=True,
            application_name="payment-worker",
        ),
        WorkloadProfile(
            name="hc05_inventory_snapshot",
            sql=(
                f"SELECT i.sku_id, i.available, i.reserved, COUNT(e.event_id) "
                f"FROM {HC05_DB}.{HC05_INVENTORY_TABLE} i "
                f"LEFT JOIN {HC05_DB}.{HC05_EVENTS_TABLE} e ON e.order_id = i.sku_id "
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
                f"FROM {HC05_DB}.{HC05_ORDERS_TABLE} "
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
                f"FROM {HC05_DB}.{HC05_INVENTORY_TABLE} i "
                f"LEFT JOIN {HC05_DB}.{HC05_EVENTS_TABLE} e ON e.order_id = i.sku_id "
                "GROUP BY i.sku_id, i.available, i.reserved "
                "ORDER BY i.sku_id DESC LIMIT 120"
            ),
            qps=0.25,
            tier="WAREHOUSE_READ",
            application_name="warehouse-reconciliation",
        ),
        WorkloadProfile(
            name="hc05_statement_summary_noise",
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
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=18,
        )
_CASE = TidbHealthCheckTiCdcReplicationTrendForCapacityReviewScenarioCase(
    case_id="ticdc_replication_capacity_review",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "sustained_replication_backpressure",
                    "entity": "ticdc/ticdc-0 and downstream/mysql-0",
                    "evidence": [
                        "source ingress remains above combined sink processing capacity",
                        "checkpoint lag grows while the changefeed remains Normal",
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": "transaction_shape_fragmentation",
                    "entity": "hc05-commerce-replication",
                    "evidence": [
                        "source transactions are split into many sink transactions",
                        "the changefeed execution configuration exposes a small max transaction row limit",
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": "sink_write_amplification_counterfactual",
                    "entity": "benchops.hc05_event_log on downstream/mysql-0",
                    "evidence": [
                        "the target downstream table maintains more indexes than the warehouse sibling",
                        "the sibling remains stable under the same resource window and business data is verifiable",
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
    evaluator=TidbHealthCheckTiCdcReplicationTrendEvaluatorCase,
    title=(
        "Routine TiDB replication-capacity review with a Normal TiCDC changefeed, "
        "a degrading checkpoint trend, and mixed business traffic."
    ),
    alert=(
        "[Routine Data Protection Review] Cross-site delivery remains green and no customer-facing "
        "page is active, but the review window overlaps checkout, payments, inventory, merchant "
        "reporting, risk audit, and monitoring. Under the continuing business workload, determine "
        "whether the delivery path satisfies the checkpoint-lag SLO of at most 3 seconds with no "
        "replication error and verifiable upstream/downstream data. Separate transient variation "
        "from a sustained issue and identify its cause. This online maintenance window authorizes "
        "necessary, reversible, bounded changes through the available operations tools without "
        "waiting for another approval, including a brief pause/resume of the current changefeed "
        "when required to apply its execution configuration. The authorization does not include stopping business traffic, "
        "deleting or rewriting business data, deleting or changing protected reporting indexes, "
        "restarting TiDB/TiKV/PD, or changing cluster topology. Verify the final state and submit."
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
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.843747,
        reference_run_ids=(
            "reference-243__"
            "tidb_health_check_ticdc_replication_trend__"
            "ticdc_replication_capacity_review__mock_reference__r001",
        ),
    ),
    db=HC05_DB,
    observation_table=HC05_OBSERVATION_TABLE,
    history_table=HC05_HISTORY_TABLE,
    orders_table=HC05_ORDERS_TABLE,
    payments_table=HC05_PAYMENTS_TABLE,
    inventory_table=HC05_INVENTORY_TABLE,
    events_table=HC05_EVENTS_TABLE,
    seed_rows=HC05_SEED_ROWS,
    source_checksum=HC05_SOURCE_CHECKSUM,
    source_batch_rows=HC05_SOURCE_BATCH_ROWS,
    downstream_index_count=HC05_DOWNSTREAM_INDEX_COUNT,
    replica_port_offset=20,
    cdc_port_offset=21,
    changefeed_id="hc05-commerce-replication",
    initial_sink_cpu=0.25,
    initial_downstream_cpu=0.20,
    sink_worker_count=4,
    sink_max_txn_row=1,
    sink_batch_dml_enable=True,
    max_lag_slo_seconds=3.0,
    max_authorized_sink_cpu=6.0,
    max_authorized_downstream_cpu=3.0,
    convergence_samples=4,
    convergence_interval_seconds=2.0,
    gc_safety_margin_seconds=60,
)


_NEW_CASE = replace(
    _CASE,
    case_id="ticdc_downstream_capacity_review",
    case_no=1,
    evaluator=TidbHealthCheckTiCdcReplicationTrendForDownstreamCapacityEvaluatorCase,
    title="A TiDB replication review for a constrained downstream MySQL sink under continuing source writes.",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "a sustained downstream sink processing deficit is below source ingress, so checkpoint lag grows while the changefeed remains Normal",
                    "entity": "downstream/mysql-0",
                    "evidence": ["source progress continues while checkpoint lag grows and downstream throughput is bounded"],
                },
                {
                    "type": "root_cause",
                    "factor": "downstream sink resource bottleneck",
                    "entity": "downstream/mysql-0",
                    "evidence": ["TiCDC and TiDB/TiKV/PD remain healthy while only the downstream target is constrained"],
                },
            ]
        },
        "outcome": {
            "changes": ["resized only the authorized downstream MySQL sink"],
            "verification": ["verified continuous source progress, checkpoint convergence, watermark integrity, and GC headroom"],
        },
        "summary": "The downstream capacity bottleneck was isolated and recovered within the authorized resource bound.",
    },
    alert=(
        "例行跨站复制巡检：TiCDC feed 仍为 Normal，但持续业务写入下 checkpoint lag 超出三秒 SLO。"
        "请把 source progress、sink throughput、历史窗口和组件资源关联起来，排除 TiDB/TiKV/PD 与一次性 burst，"
        "只调整授权的 downstream MySQL 资源并在持续窗口内验证收敛。禁止停业务、停 feed、改业务行或变更拓扑。"
    ),
    expected_target={
        "status": "replication_slo_recovered",
        "outcome": "downstream-only bounded capacity repair",
        "diagnostic_contract": "attribute lag to downstream sink after excluding TiCDC and TiDB/TiKV/PD",
    },
    runtime=replace(_CASE.runtime, bootstrap_cache_enabled=False),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.181818,
        reference_run_ids=(
            "tidb-reference-11__"
            "tidb_health_check_ticdc_replication_trend__"
            "ticdc_downstream_capacity_review__mock__r001",
        ),
    ),
    initial_sink_cpu=1.0,
    initial_downstream_cpu=0.20,
    max_authorized_sink_cpu=1.0,
    max_authorized_downstream_cpu=3.0,
    convergence_samples=3,
    history_sample_count=144,
    history_transient_decoys=False,
    background_workload=replace(
        _CASE.background_workload,
        profiles=tuple(
            profile
            for profile in _CASE.background_workload.profiles
            if profile.name not in {"hc05_statement_summary_noise", "warehouse_reconciliation_scan"}
        ),
        worker_count=5,
        warmup_seconds=15,
    ),
)


class TidbHealthCheckTiCdcReplicationTrendScenario(TiDBScenario):
    scenario_id = "tidb_health_check_ticdc_replication_trend"
    description = "Routine TiCDC replication-capacity health check under noisy commerce workload."
    cases = (_CASE, _NEW_CASE)

    def build_fault_plan(self, case: TidbHealthCheckTiCdcReplicationTrendCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbHealthCheckTiCdcReplicationTrendInjector,
                config={
                    "db": case.db,
                    "observation_table": case.observation_table,
                    "history_table": case.history_table,
                    "orders_table": case.orders_table,
                    "payments_table": case.payments_table,
                    "inventory_table": case.inventory_table,
                    "events_table": case.events_table,
                    "seed_rows": case.seed_rows,
                    "source_checksum": case.source_checksum,
                    "source_batch_rows": case.source_batch_rows,
                    "downstream_index_count": case.downstream_index_count,
                    "replica_port_offset": case.replica_port_offset,
                    "cdc_port_offset": case.cdc_port_offset,
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
                    "history_sample_count": case.history_sample_count,
                    "history_transient_decoys": case.history_transient_decoys,
                },
            ),
        )

class TidbHealthCheckTiCdcReplicationTrendInjector(BaseFaultInjector):
    """Run a real TiCDC-to-MySQL feed with a deliberately undersized sink budget."""

    MYSQL_IMAGE = "mysql:8.0"
    TICDC_IMAGE = "pingcap/ticdc@sha256:7832063b5215b3107d33b7280b2653a79667e9ba54e4b0596ed1092b4a486015"
    MYSQL_PASSWORD = "hc05_sink_password"
    MONITOR_JOIN_TIMEOUT_SECONDS = 45
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
        self._monitor_stop = threading.Event()
        self._monitor_thread = None
        self._monitor_error = None
        self._last_sink_sample = None
        self._last_lag_sample = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self.run_id = context.run_id
        self._replica_port = context.env.port + self.replica_port_offset
        self._cdc_port = context.env.port + self.cdc_port_offset
        self._verify_images()
        self._verify_ports()
        self._network = f"{context.env.deployment.project_name}_default"
        self._run(["docker", "network", "inspect", self._network], "inspect TiDB network")
        self._create_source_database(context.env)
        self._start_mysql()
        context.env.configure_secondary_endpoint(
            "127.0.0.1", self._replica_port, self.MYSQL_PASSWORD
        )
        self._create_replica_database(context.env)
        self._resize_downstream(self.initial_downstream_cpu)
        self._capture_gc_life_time(context.env)
        start_tso = self._current_tso(context.env)
        self._start_ticdc()
        context.env.configure_replication_endpoint(
            "127.0.0.1",
            self._cdc_port,
            self.changefeed_id,
            self._cdc_container,
            self._mysql_container,
            target="ticdc/ticdc-0",
            max_cpu_limit=self.max_authorized_sink_cpu,
            max_downstream_cpu_limit=self.max_authorized_downstream_cpu,
            sink_uri=self._sink_uri(),
        )
        self._wait_for_health()
        self._create_changefeed(start_tso)
        self._changefeed_created = True
        self._wait_for_changefeed()
        self._configured = True

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self.run_id = context.run_id
        self._replica_port = context.env.port + self.replica_port_offset
        self._cdc_port = context.env.port + self.cdc_port_offset
        if (
            not self._configured
            or self._mysql_container is None
            or self._cdc_container is None
        ):
            raise RuntimeError(
                "HC05 activate requires an installed TiCDC and downstream runtime: "
                f"configured={self._configured}, mysql_container={self._mysql_container!r}, "
                f"cdc_container={self._cdc_container!r}"
            )
        if not self._container_running(self._mysql_container):
            self._run(["docker", "start", self._mysql_container], "activate MySQL downstream")
        self._mysql_host = self._resolve_mysql_host()
        self._resize_downstream(self.initial_downstream_cpu)
        if not self._container_running(self._cdc_container):
            self._run(["docker", "start", self._cdc_container], "activate TiCDC")
        context.env.configure_secondary_endpoint(
            "127.0.0.1", self._replica_port, self.MYSQL_PASSWORD
        )
        context.env.configure_replication_endpoint(
            "127.0.0.1",
            self._cdc_port,
            self.changefeed_id,
            self._cdc_container,
            self._mysql_container,
            target="ticdc/ticdc-0",
            max_cpu_limit=self.max_authorized_sink_cpu,
            max_downstream_cpu_limit=self.max_authorized_downstream_cpu,
            sink_uri=self._sink_uri(),
        )
        self._wait_for_health()
        status = self._changefeed_status()
        if status["state"] not in {"normal", "running"}:
            raise RuntimeError(
                f"HC05 TiCDC activation found unexpected changefeed state: "
                f"changefeed_id={self.changefeed_id!r}, status={status!r}"
            )
        self._resize(self.initial_sink_cpu)
        self._resize_downstream(self.initial_downstream_cpu)
        self._configured = True

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        if not self._configured:
            raise RuntimeError("HC05 observability requested before injector installation")
        self._raise_monitor_error()
        status = self._direct_replication_status(context.env)
        summary = self._summary(context.env)
        self._record_live_observation(context.env, status, summary)
        self._monitor_stop.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(context.env,),
            name=f"hc05-replication-monitor-{context.run_id}",
            daemon=True,
        )
        self._monitor_thread.start()
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
            "reference_observation_units": {
                "replication_observations": {"causal": 8, "noise": 28},
                "downstream_schema": {"causal": 8, "noise": 14},
                "historical_rows": {"causal": 30, "noise": 4060},
                "changefeed_get": {"causal": 6, "noise": 4},
                "workload_profiles": {"causal": 3, "noise": 7},
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._stop_monitor()
        for container, label in (
            (self._cdc_container, "quiesce TiCDC"),
            (self._mysql_container, "quiesce MySQL downstream"),
        ):
            if container is not None and self._container_running(container):
                self._run(["docker", "stop", "-t", "5", container], label)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._stop_monitor()
        self._raise_monitor_error()
        if self._changefeed_created:
            if not self._container_running(self._cdc_container):
                self._run(["docker", "start", self._cdc_container], "start TiCDC for recovery")
                self._wait_for_health()
            self._delete_changefeed()
            self._changefeed_created = False
        if self._cdc_container is not None and self._container_exists(self._cdc_container):
            self._run(["docker", "rm", "-f", self._cdc_container], "remove TiCDC")
        if self._mysql_container is not None and self._container_exists(self._mysql_container):
            self._run(["docker", "rm", "-f", self._mysql_container], "remove MySQL downstream")
        if self._original_gc_life_time is not None:
            require_sql_success(
                context.env.execute_sql(
                    f"SET GLOBAL tidb_gc_life_time = '{sql_escape(self._original_gc_life_time)}'"
                ),
                "restore HC05 GC retention window",
            )
        context.env.clear_replication_endpoint()
        context.env.clear_secondary_endpoint()
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"),
            "drop HC05 source schema",
        )
        self._configured = False

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.observation_table = validate_sql_identifier(
            str(config["observation_table"]), "observation_table"
        )
        self.history_table = validate_sql_identifier(str(config["history_table"]), "history_table")
        self.orders_table = validate_sql_identifier(str(config["orders_table"]), "orders_table")
        self.payments_table = validate_sql_identifier(str(config["payments_table"]), "payments_table")
        self.inventory_table = validate_sql_identifier(str(config["inventory_table"]), "inventory_table")
        self.events_table = validate_sql_identifier(str(config["events_table"]), "events_table")
        self.seed_rows = int(config["seed_rows"])
        self.source_checksum = int(config["source_checksum"])
        self.source_batch_rows = int(config["source_batch_rows"])
        self.downstream_index_count = int(config["downstream_index_count"])
        self.replica_port_offset = int(config["replica_port_offset"])
        self.cdc_port_offset = int(config["cdc_port_offset"])
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
        self.history_sample_count = int(config["history_sample_count"])
        self.history_transient_decoys = bool(config["history_transient_decoys"])

    def _verify_images(self) -> None:
        for image in (self.MYSQL_IMAGE, self.TICDC_IMAGE):
            result = subprocess.run(
                ["docker", "image", "inspect", image],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"HC05 required image is missing: image={image!r}, "
                    f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
                )

    def _verify_ports(self) -> None:
        for port in (self._replica_port, self._cdc_port):
            with socket.socket() as sock:
                try:
                    sock.bind(("127.0.0.1", port))
                except OSError as exc:
                    raise RuntimeError(
                        f"HC05 external port is unavailable: port={port}, error={exc}"
                    ) from exc

    def _start_mysql(self) -> None:
        self._mysql_container = f"aiopsbench-{self.run_id}-hc05-mysql"
        self._run(
            [
                "docker", "run", "--detach",
                "--name", self._mysql_container,
                "--network", self._network,
                "--publish", f"127.0.0.1:{self._replica_port}:3306",
                "--cpus", "0.5",
                "--memory", "2g",
                "--tmpfs", "/var/lib/mysql:rw,size=2G",
                "--env", f"MYSQL_ROOT_PASSWORD={self.MYSQL_PASSWORD}",
                "--env", "MYSQL_DATABASE=test",
                self.MYSQL_IMAGE,
            ],
            "start HC05 MySQL downstream",
        )
        self._wait(
            "MySQL downstream readiness",
            lambda: self._run(
                [
                    "docker", "exec", self._mysql_container,
                    "mysqladmin", "ping", "-h127.0.0.1", "-uroot",
                    f"-p{self.MYSQL_PASSWORD}", "--silent",
                ],
                "probe MySQL downstream",
            ),
            90,
        )
        self._mysql_host = self._resolve_mysql_host()

    def _start_ticdc(self) -> None:
        self._cdc_container = f"aiopsbench-{self.run_id}-hc05-ticdc"
        self._run(
            [
                "docker", "run", "--detach",
                "--name", self._cdc_container,
                "--network", self._network,
                "--publish", f"127.0.0.1:{self._cdc_port}:8300",
                "--cpus", str(self.initial_sink_cpu),
                "--memory", "768m",
                "--storage-opt", "size=2G",
                self.TICDC_IMAGE,
                "/cdc", "server",
                "--pd=http://pd-0:2379",
                "--addr=0.0.0.0:8300",
                f"--advertise-addr={self._cdc_container}:8300",
                "--log-file=/dev/stderr",
            ],
            "start HC05 TiCDC",
        )

    def _resolve_mysql_host(self) -> str:
        host = self._run(
            [
                "docker",
                "inspect",
                "--format",
                "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
                self._mysql_container,
            ],
            "resolve HC05 MySQL network address",
        ).strip()
        if not host:
            raise RuntimeError(
                f"HC05 MySQL container has no network address: container={self._mysql_container!r}, "
                f"network={self._network!r}"
            )
        return host

    def _create_changefeed(self, start_tso: int) -> None:
        sink_uri = self._sink_uri()
        payload = {
            "changefeed_id": self.changefeed_id,
            "start_ts": start_tso,
            "sink_uri": sink_uri,
            "filter_rules": [f"{self.db}.*"],
            "mounter_worker_num": self.sink_worker_count,
        }
        response = self._http_json(
            "POST",
            "/api/v1/changefeeds",
            payload,
            expected_status=202,
        )
        if response not in ({}, None):
            raise RuntimeError(f"HC05 changefeed create returned an unexpected body: body={response!r}")

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

    def _changefeed_status(self) -> dict[str, Any]:
        status = self._http_json(
            "GET",
            f"/api/v1/changefeeds/{self.changefeed_id}",
            None,
            expected_status=200,
        )
        if not isinstance(status, dict):
            raise TypeError(f"HC05 changefeed status must be an object: status={status!r}")
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
                        f"HC05 TiCDC API returned unexpected status: method={method!r}, path={path!r}, "
                        f"expected={expected_status}, actual={response.status}"
                    )
                raw = response.read()
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"HC05 TiCDC API request failed: method={method!r}, path={path!r}, "
                f"expected={expected_status}, actual={exc.code}, body={body!r}"
            ) from exc
        if not raw:
            return {}
        return json.loads(raw.decode())

    def _create_source_database(self, env) -> None:
        require_sql_success(env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"), "clear HC05 source schema")
        require_sql_success(env.execute_sql(f"CREATE DATABASE {self.db}"), "create HC05 source schema")
        self._create_tables(env)
        self._load_rows(env)
        self._load_history(env)

    def _create_replica_database(self, env) -> None:
        require_sql_success(
            env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}", target="replica"),
            "clear HC05 replica schema",
        )
        require_sql_success(
            env.execute_sql(f"CREATE DATABASE {self.db}", target="replica"),
            "create HC05 replica schema",
        )
        self._create_tables(env, target="replica")
        self._load_rows(env, target="replica")
        self._create_sink_only_indexes(env)
        self._load_history(env, target="replica")

    def _create_sink_only_indexes(self, env) -> None:
        for index_definition in self.SINK_ONLY_INDEXES:
            require_sql_success(
                env.execute_sql(
                    f"ALTER TABLE {self.db}.{self.events_table} "
                    f"ADD KEY {index_definition}",
                    target="replica",
                ),
                f"create HC05 downstream sink index definition={index_definition!r}",
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
            f"CREATE TABLE {self.db}.{self.observation_table} ("
            "observation_id BIGINT PRIMARY KEY AUTO_INCREMENT, observed_at DATETIME NOT NULL, "
            "changefeed_id VARCHAR(96) NOT NULL, "
            "state VARCHAR(32) NOT NULL, upstream_tso BIGINT NOT NULL, checkpoint_tso BIGINT NOT NULL, "
            "checkpoint_lag_seconds DECIMAL(12,3) NOT NULL, sink_rows_per_second DECIMAL(12,3) NOT NULL, "
            "error_count INT NOT NULL, gc_headroom_seconds INT NOT NULL, source_event_rows BIGINT NOT NULL, "
            "replica_event_rows BIGINT NOT NULL, source_transaction_rows BIGINT NOT NULL, "
            "sink_transaction_rows BIGINT NOT NULL, downstream_index_count INT NOT NULL, "
            "sink_worker_count INT NOT NULL, sink_max_txn_row INT NOT NULL, sink_batch_dml_enable TINYINT NOT NULL, "
            "lag_slope_seconds_per_minute DECIMAL(12,3) NOT NULL, note VARCHAR(160) NOT NULL, "
            "KEY idx_observed_at (observed_at), KEY idx_lag (checkpoint_lag_seconds)"
            ")",
            f"CREATE TABLE {self.db}.{self.history_table} ("
            "history_id BIGINT PRIMARY KEY, changefeed_id VARCHAR(96) NOT NULL, "
            "observed_at DATETIME NOT NULL, state VARCHAR(32) NOT NULL, "
            "checkpoint_lag_seconds DECIMAL(12,3) NOT NULL, sink_rows_per_second DECIMAL(12,3) NOT NULL, "
            "gc_headroom_seconds INT NOT NULL, error_count INT NOT NULL, source_qps DECIMAL(12,3) NOT NULL, "
            "source_transaction_rows BIGINT NOT NULL, sink_transaction_rows BIGINT NOT NULL, "
            "downstream_index_count INT NOT NULL, sink_worker_count INT NOT NULL, sink_max_txn_row INT NOT NULL, "
            "sink_batch_dml_enable TINYINT NOT NULL, lag_slope_seconds_per_minute DECIMAL(12,3) NOT NULL, "
            "note VARCHAR(160) NOT NULL, KEY idx_history_time (observed_at), KEY idx_history_lag (checkpoint_lag_seconds)"
            ")",
        )
        for statement in statements:
            require_sql_success(env.execute_sql(statement, target=target), f"create HC05 table target={target}")

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
            "load HC05 orders",
        )
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.payments_table} "
            "(payment_id, order_id, amount, payment_status, paid_at) VALUES ",
            payment_rows,
            target,
            "load HC05 payments",
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
            "load HC05 inventory",
        )
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.events_table} "
            "(event_id, order_id, event_type, created_at) VALUES ",
            event_rows,
            target,
            "load HC05 events",
        )

    def _load_history(self, env, target: str = "primary") -> None:
        rows = []
        start = datetime(2026, 7, 18)
        sample_count = self.history_sample_count
        for index in range(sample_count):
            progress = index / (sample_count - 1)
            lag = 0.35 + progress**3 * 10.6 + (index % 9) * 0.03
            throughput = 480.0 - progress * 365.0 + (index % 5) * 2.0
            headroom = max(900, int(86400 - progress * 76000))
            source_qps = 18.0 + progress * 25.0 + (index % 11) * 0.4
            lag_slope = 0.015 + progress * 0.055 + (index % 7) * 0.002
            observed_at = start + timedelta(minutes=index * 10)
            rows.append(
                f"({index * 2 + 1}, '{sql_escape(self.changefeed_id)}', "
                f"'{observed_at:%Y-%m-%d %H:%M:%S}', 'normal', "
                f"{lag:.3f}, {throughput:.3f}, {headroom}, 0, {source_qps:.3f}, "
                f"{self.source_batch_rows}, {self.source_batch_rows // self.sink_max_txn_row}, "
                f"{self.downstream_index_count}, {self.sink_worker_count}, {self.sink_max_txn_row}, "
                f"{1 if self.sink_batch_dml_enable else 0}, {lag_slope:.3f}, "
                "'historical commerce delivery-capacity observation')"
            )
            noise_lag = 0.5 + (index % 17) * 0.11
            if self.history_transient_decoys and index % 97 in {0, 1, 2}:
                noise_lag += 7.0
            noise_throughput = 360.0 + (index % 13) * 3.0
            noise_qps = source_qps * (0.98 + (index % 5) * 0.005)
            sibling_lag_slope = ((index % 11) - 5) * 0.001
            rows.append(
                f"({index * 2 + 2}, '{HC05_HEALTHY_SIBLING_ID}', "
                f"'{observed_at:%Y-%m-%d %H:%M:%S}', 'normal', "
                f"{noise_lag:.3f}, {noise_throughput:.3f}, {max(1200, headroom // 2)}, 0, "
                f"{noise_qps:.3f}, {self.source_batch_rows}, 1, {HC05_BASE_DOWNSTREAM_INDEX_COUNT}, "
                f"{self.sink_worker_count}, {self.source_batch_rows}, "
                f"{1 if self.sink_batch_dml_enable else 0}, {sibling_lag_slope:.3f}, "
                "'historical warehouse delivery-capacity observation')"
            )
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.history_table} "
            "(history_id, changefeed_id, observed_at, state, checkpoint_lag_seconds, sink_rows_per_second, "
            "gc_headroom_seconds, error_count, source_qps, source_transaction_rows, sink_transaction_rows, "
            "downstream_index_count, sink_worker_count, sink_max_txn_row, sink_batch_dml_enable, "
            "lag_slope_seconds_per_minute, note) VALUES ",
            rows,
            target,
            "load HC05 history",
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
            "read HC05 GC retention window",
        )
        rows = payload.get("result")
        if not isinstance(rows, list) or len(rows) != 1 or len(rows[0]) < 2:
            raise ValueError(f"HC05 GC retention result shape is invalid: payload={payload!r}")
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
            payload = json_object(env.execute_sql(sql, target=target), f"read HC05 {target} summary")
            rows = payload.get("result")
            if not isinstance(rows, list) or len(rows) != 4:
                raise ValueError(f"HC05 {target} summary result shape is invalid: payload={payload!r}")
            result[target] = rows
        return result

    def _record_live_observation(
        self,
        env,
        status_payload: dict,
        summary: dict[str, list],
        *,
        direct: bool = False,
    ) -> None:
        snapshot = status_payload["snapshot"]
        source_events = int(self._summary_row(summary["primary"], "events")[1])
        replica_events = int(self._summary_row(summary["replica"], "events")[1])
        now = time.monotonic()
        sink_rows_per_second = 0.0
        if self._last_sink_sample is not None:
            previous_time, previous_rows = self._last_sink_sample
            elapsed = now - previous_time
            if elapsed <= 0:
                raise RuntimeError(f"HC05 monitor elapsed time is non-positive: elapsed={elapsed!r}")
            sink_rows_per_second = max(0.0, (replica_events - previous_rows) / elapsed)
        self._last_sink_sample = (now, replica_events)
        lag = float(snapshot["lag_seconds"])
        lag_slope = 0.0
        if self._last_lag_sample is not None:
            previous_time, previous_lag = self._last_lag_sample
            elapsed = now - previous_time
            if elapsed <= 0:
                raise RuntimeError(f"HC05 lag sample elapsed time is non-positive: elapsed={elapsed!r}")
            lag_slope = (lag - previous_lag) / elapsed * 60.0
        self._last_lag_sample = (now, lag)
        headroom = self._gc_headroom_seconds(lag)
        sink_transaction_rows = (self.source_batch_rows + self.sink_max_txn_row - 1) // self.sink_max_txn_row
        sql = (
            f"INSERT INTO {self.db}.{self.observation_table} "
            "(observed_at, changefeed_id, state, upstream_tso, checkpoint_tso, checkpoint_lag_seconds, "
            "sink_rows_per_second, error_count, gc_headroom_seconds, source_event_rows, "
            "replica_event_rows, source_transaction_rows, sink_transaction_rows, downstream_index_count, "
            "sink_worker_count, sink_max_txn_row, sink_batch_dml_enable, lag_slope_seconds_per_minute, note) "
            "VALUES (CURRENT_TIMESTAMP, "
            f"'{sql_escape(self.changefeed_id)}', '{sql_escape(str(snapshot['state']))}', "
            f"{int(snapshot['upstream_tso'])}, "
            f"{int(snapshot['checkpoint_tso'])}, {lag:.3f}, {sink_rows_per_second:.3f}, "
            f"{0 if snapshot.get('error') is None else 1}, {headroom}, {source_events}, "
            f"{replica_events}, {self.source_batch_rows}, {sink_transaction_rows}, "
            f"{self.downstream_index_count}, {self.sink_worker_count}, {self.sink_max_txn_row}, "
            f"{1 if self.sink_batch_dml_enable else 0}, {lag_slope:.3f}, "
            "'live TiCDC API and source/replica CRC observation')"
        )
        result = self._direct_execute(env, sql) if direct else env.execute_sql(sql)
        require_sql_success(
            result,
            "record HC05 live observation",
        )

    def _summary_direct(self, env) -> dict[str, list]:
        sql = (
            "SELECT table_name, row_count, id_checksum FROM ("
            f"SELECT 'orders' AS table_name, COUNT(*) AS row_count, COALESCE(SUM(order_id), 0) AS id_checksum FROM {self.db}.{self.orders_table} "
            f"UNION ALL SELECT 'payments', COUNT(*), COALESCE(SUM(payment_id), 0) FROM {self.db}.{self.payments_table} "
            f"UNION ALL SELECT 'inventory', COUNT(*), COALESCE(SUM(sku_id), 0) FROM {self.db}.{self.inventory_table} "
            f"UNION ALL SELECT 'events', COUNT(*), COALESCE(SUM(event_id), 0) FROM {self.db}.{self.events_table}"
            ") AS business_summary ORDER BY table_name"
        )
        return {
            target: self._direct_rows(env, sql, target)
            for target in ("primary", "replica")
        }

    @staticmethod
    def _summary_row(rows: list[list], table_name: str) -> list:
        matches = [row for row in rows if row[0] == table_name]
        if len(matches) != 1:
            raise ValueError(
                f"HC05 business summary must contain exactly one {table_name!r} row: rows={rows!r}"
            )
        return matches[0]

    def _direct_execute(self, env, sql: str) -> dict[str, object]:
        self._direct_rows(env, sql, "primary")
        return {"status": "success", "result": []}

    def _direct_rows(self, env, sql: str, target: str) -> list[list]:
        import pymysql

        port = env.port if target == "primary" else self._replica_port
        conn = pymysql.connect(
            host="127.0.0.1",
            port=port,
            user="root",
            password="" if target == "primary" else self.MYSQL_PASSWORD,
            database=self.db,
            autocommit=True,
            connect_timeout=5,
            read_timeout=35,
            write_timeout=35,
        )
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = list(cursor.fetchall()) if cursor.description else []
        conn.close()
        return rows

    def _monitor_loop(self, env) -> None:
        try:
            while not self._monitor_stop.wait(2.0):
                try:
                    status = self._direct_replication_status(env)
                    self._record_live_observation(
                        env,
                        status,
                        self._summary_direct(env),
                        direct=True,
                    )
                except (TimeoutError, OSError, OperationalError):
                    # A transient endpoint interruption can miss one telemetry sample; final OP probes directly.
                    continue
        except Exception as exc:
            self._monitor_error = exc
            self._monitor_stop.set()

    def _direct_replication_status(self, env) -> dict[str, object]:
        changefeed = self._changefeed_status()
        source_tso = self._current_tso(env)
        checkpoint_tso = int(changefeed["checkpoint_tso"])
        if checkpoint_tso <= 0:
            raise RuntimeError(
                f"HC05 TiCDC checkpoint TSO must be positive: changefeed_id={self.changefeed_id!r}, "
                f"checkpoint_tso={checkpoint_tso}"
            )
        if source_tso < checkpoint_tso:
            raise RuntimeError(
                f"HC05 source TSO is older than TiCDC checkpoint: changefeed_id={self.changefeed_id!r}, "
                f"source_tso={source_tso}, checkpoint_tso={checkpoint_tso}"
            )
        lag_seconds = round(
            ((source_tso >> 18) - (checkpoint_tso >> 18)) / 1000,
            3,
        )
        if lag_seconds < 0:
            raise RuntimeError(
                f"HC05 checkpoint lag must be non-negative: changefeed_id={self.changefeed_id!r}, "
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

    def _gc_headroom_seconds(self, lag_seconds: float) -> int:
        if self._original_gc_life_time is None:
            raise RuntimeError("HC05 GC lifetime must be captured before live observations")
        value = self._original_gc_life_time.strip()
        matches = tuple(re.finditer(r"(\d+)([smhd])", value))
        if not matches or "".join(match.group(0) for match in matches) != value:
            raise ValueError(
                "HC05 cannot calculate GC headroom from tidb_gc_life_time: "
                f"value={self._original_gc_life_time!r}"
            )
        seconds = sum(
            int(match.group(1)) * {"s": 1, "m": 60, "h": 3600, "d": 86400}[match.group(2)]
            for match in matches
        )
        return int(seconds - float(lag_seconds))

    def _stop_monitor(self) -> None:
        self._monitor_stop.set()
        if self._monitor_thread is not None:
            join_thread(
                self._monitor_thread,
                self.MONITOR_JOIN_TIMEOUT_SECONDS,
                "HC05 replication monitor",
            )
            self._monitor_thread = None

    def _raise_monitor_error(self) -> None:
        if self._monitor_error is not None:
            error = self._monitor_error
            self._monitor_error = None
            raise RuntimeError(f"HC05 replication monitor failed: error={error!r}") from error

    def _resize(self, cpu_limit: float) -> None:
        result = subprocess.run(
            ["docker", "update", "--cpus", str(cpu_limit), self._cdc_container],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"HC05 TiCDC cgroup resize failed: container={self._cdc_container!r}, "
                f"cpu_limit={cpu_limit!r}, stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )

    def _resize_downstream(self, cpu_limit: float) -> None:
        result = subprocess.run(
            ["docker", "update", "--cpus", str(cpu_limit), self._mysql_container],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"HC05 downstream MySQL cgroup resize failed: container={self._mysql_container!r}, "
                f"cpu_limit={cpu_limit!r}, stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )

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
            f"HC05 readiness timed out: stage={label!r}, timeout={timeout}, last_error={last_error!r}"
        )

    def _run(self, command: list[str], label: str) -> str:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"HC05 command failed: label={label!r}, command={command!r}, "
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
                f"HC05 container state query failed: container={container!r}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        return result.stdout.strip().casefold() == "true"
