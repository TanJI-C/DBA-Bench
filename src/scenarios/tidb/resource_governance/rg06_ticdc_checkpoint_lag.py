import threading

import time

from collections.abc import Mapping

from src.database.query_results import capture_query_result_truth

from src.database.sql import parse_json_object, require_success_payload

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext

from src.scenarios.tidb.common import json_object, require_sql_success, validate_sql_identifier

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.resource_governance.rg06_ticdc_checkpoint_lag import (
    TidbResourceGovernanceRg06EvaluatorCase,
    TidbResourceGovernanceRg06NeighborFeedEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


_RG06_BUSINESS_QUERY = (
    "SELECT event_id, tenant_id, event_type, amount, payload "
    "FROM benchops.rg06_cdc_source "
    "WHERE tenant_id = 7 AND event_type IN ('settled', 'captured') "
    "ORDER BY event_id LIMIT 128"
)

_RG06_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="rg06_source_order_lookup",
            sql=(
                "SELECT event_id, amount, event_type FROM benchops.rg06_cdc_source "
                "WHERE tenant_id = 7 AND event_id >= 700 ORDER BY event_id LIMIT 20"
            ),
            qps=0.80,
            tier="OLTP_CORE",
            application_name="order-api",
        ),
        WorkloadProfile(
            name="rg06_source_tenant_rollup",
            sql=(
                "SELECT tenant_id, event_type, COUNT(*), SUM(amount) "
                "FROM benchops.rg06_cdc_source GROUP BY tenant_id, event_type"
            ),
            qps=0.35,
            tier="OLTP_CORE",
            application_name="order-rollup",
        ),
        WorkloadProfile(
            name="rg06_sink_order_lookup",
            sql=(
                "SELECT event_id, amount, event_type FROM benchops.rg06_cdc_sink "
                "WHERE tenant_id = 7 AND event_id >= 700 ORDER BY event_id LIMIT 20"
            ),
            qps=0.80,
            tier="CDC_SINK_SLO",
            application_name="archive-reader",
        ),
        WorkloadProfile(
            name="rg06_sink_tenant_rollup",
            sql=(
                "SELECT tenant_id, event_type, COUNT(*), SUM(amount) "
                "FROM benchops.rg06_cdc_sink GROUP BY tenant_id, event_type"
            ),
            qps=0.35,
            tier="CDC_SINK_SLO",
            application_name="archive-rollup",
        ),
        WorkloadProfile(
            name="rg06_reconcile_source_lookup",
            sql=(
                "SELECT event_id, amount, event_type FROM benchops.rg06_reconcile_source "
                "WHERE tenant_id = 11 AND event_id >= 300 ORDER BY event_id LIMIT 20"
            ),
            qps=0.25,
            tier="CDC_NEIGHBOR",
            application_name="ledger-reconcile",
        ),
        WorkloadProfile(
            name="rg06_reconcile_sink_lookup",
            sql=(
                "SELECT event_id, amount, event_type FROM benchops.rg06_reconcile_sink "
                "WHERE tenant_id = 11 AND event_id >= 300 ORDER BY event_id LIMIT 20"
            ),
            qps=0.25,
            tier="CDC_NEIGHBOR",
            application_name="ledger-reconcile-reader",
        ),
        WorkloadProfile(
            name="rg06_archive_retention_scan",
            sql=(
                "SELECT COUNT(*), SUM(amount) FROM benchops.rg06_archive_audit "
                "WHERE archive_day >= '2026-07-01'"
            ),
            qps=0.30,
            tier="ARCHIVE_MAINTENANCE",
            application_name="archive-report",
        ),
        WorkloadProfile(
            name="rg06_observability_health",
            sql=(
                "SELECT component, COUNT(*), AVG(value) FROM benchops.rg06_observability_samples "
                "GROUP BY component"
            ),
            qps=0.25,
            tier="OBSERVABILITY_MAINTENANCE",
            application_name="platform-monitor",
        ),
    ),
    worker_count=6,
    seed=20260802,
    warmup_seconds=15,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceRg06ForCheckpointSinkBudgetScenarioCase(TiDBScenarioCase):
    db: str
    source_table: str
    sink_table: str
    config_table: str
    registry_table: str
    metrics_table: str
    error_table: str
    archive_table: str
    observability_table: str
    neighbor_source_table: str
    neighbor_sink_table: str
    changefeed_id: str
    neighbor_changefeed_id: str
    business_query: str
    source_row_count: int
    initial_sink_row_count: int
    neighbor_source_row_count: int
    neighbor_initial_sink_row_count: int


_RG06_CASE = TidbResourceGovernanceRg06ForCheckpointSinkBudgetScenarioCase(
    case_id="ticdc_checkpoint_sink_budget",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "raised the case-local sorter and sink budget within the tested envelope"
            ],
            "verification": [
                "verified checkpoint/resolved convergence, equal source and sink truth, GC headroom, and both SLOs"
            ]
        },
        "summary": "The changefeed caught up with a bounded sorter and sink budget while preserving the source, downstream truth, GC headroom, and foreground latency."
    },
    case_no=0,
    evaluator=TidbResourceGovernanceRg06EvaluatorCase,
    title="Tune a lagging TiCDC-style pipeline under foreground and downstream SLO constraints.",
    alert=(
        "[CRITICAL] archive freshness has breached its customer window while the replication "
        "service still reports NORMAL. Online order reads and downstream archive readers share "
        "this TiDB cluster, and the retention guard is active. Determine which registered "
        "business flow is affected and choose a bounded synchronization budget without changing "
        "business data or global resource settings."
    ),
    initial_state={
        "state": "NORMAL",
        "symptom": "archive freshness window breached",
        "foreground": "order reads remain available",
        "retention": "guard active",
    },
    expected_target={
        "state": "NORMAL",
        "max_checkpoint_lag_rows": 3,
        "min_sink_rows_per_second": 40,
        "min_gc_headroom_seconds": 600,
        "max_downstream_p95_ms": 60,
        "max_foreground_p95_ms": 75,
        "max_overload_events": 0,
        "max_error_count": 0,
        "safe_sink_workers": (4, 16),
        "safe_sorter_memory_mb": (128, 512),
        "safe_sink_batch_rows": (32, 256),
        "safe_sink_write_budget": ("0.25", "1.00"),
        "max_budget_load_factor": 32,
    },
    background_workload=_RG06_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=3,
        tidb_count=1,
        sql_timeout_seconds=120,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.927032,
        reference_run_ids=("reference-278__tidb_resource_governance_rg06__ticdc_checkpoint_sink_budget__mock__r001",),
    ),
    db="benchops",
    source_table="rg06_cdc_source",
    sink_table="rg06_cdc_sink",
    config_table="rg06_cdc_config",
    registry_table="rg06_changefeed_registry",
    metrics_table="rg06_cdc_metrics",
    error_table="rg06_cdc_errors",
    archive_table="rg06_archive_audit",
    observability_table="rg06_observability_samples",
    neighbor_source_table="rg06_reconcile_source",
    neighbor_sink_table="rg06_reconcile_sink",
    changefeed_id="archive-orders",
    neighbor_changefeed_id="reconcile-orders",
    business_query=_RG06_BUSINESS_QUERY,
    source_row_count=1800,
    initial_sink_row_count=420,
    neighbor_source_row_count=900,
    neighbor_initial_sink_row_count=840,
)

_RG06_RECONCILE_CASE = replace(
    _RG06_CASE,
    case_id="ticdc_reconcile_sink_budget",
    case_no=1,
    evaluator=TidbResourceGovernanceRg06NeighborFeedEvaluatorCase,
    title="Tune the reconciliation changefeed without disturbing the archive feed.",
    alert=(
        "[CRITICAL] the settlement reconciliation mirror has breached its freshness window while the "
        "archive feed reports normal service. Inspect the changefeed registry and raw progress, pipeline, "
        "resource, and GC evidence to identify the affected feed. Apply a bounded local sink budget, "
        "preserve the archive feed and foreground order truth, and do not change global settings or data."
    ),
    initial_state={
        "state": "NORMAL",
        "symptom": "reconciliation freshness window breached",
        "foreground": "order reads remain available",
        "protected_neighbor": "archive-orders must remain unchanged",
    },
    expected_target={
        **_RG06_CASE.expected_target,
        "target_changefeed": "reconcile-orders",
        "protected_neighbor": "archive-orders",
    },
    source_table="rg06_reconcile_source",
    sink_table="rg06_reconcile_sink",
    neighbor_source_table="rg06_cdc_source",
    neighbor_sink_table="rg06_cdc_sink",
    changefeed_id="reconcile-orders",
    neighbor_changefeed_id="archive-orders",
    business_query=(
        "SELECT event_id, tenant_id, event_type, amount, payload "
        "FROM benchops.rg06_reconcile_source "
        "WHERE tenant_id = 11 AND event_type IN ('settled', 'captured') "
        "ORDER BY event_id LIMIT 128"
    ),
    source_row_count=900,
    initial_sink_row_count=840,
    neighbor_source_row_count=1800,
    neighbor_initial_sink_row_count=420,
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.17757,
        reference_run_ids=(
            "tidb-reference-6__tidb_resource_governance_rg06__"
            "ticdc_reconcile_sink_budget__mock__r001",
        ),
    ),
)


class TidbResourceGovernanceRg06Injector(BaseFaultInjector):
    """Install a SQL-backed TiCDC pipeline with a deliberately small sink budget."""

    _CAUSAL_METRICS = {
        "capture_rows_per_second",
        "resolved_event_id",
        "sorter_rows_per_second",
        "sorter_queue_rows",
        "sink_write_rows_per_second",
        "checkpoint_event_id",
        "checkpoint_lag_rows",
        "sink_write_p95_ms",
        "downstream_write_p95_ms",
        "gc_headroom_seconds",
        "changefeed_state",
        "error_count",
        "overload_events",
        "foreground_p95_ms",
    }

    def __init__(self):
        self._pipeline_thread = None
        self._stop_event = threading.Event()
        self._thread_error = None

    def install(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._create_tables(context.env)
        self._verify_fault_state(context.env)
        self._start_pipeline(context.env)

    def activate(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._verify_fault_state(context.env)
        self._start_pipeline(context.env)

    def prepare_observability(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._check_thread(context)
        source_truth_payload = self._payload(
            context.env,
            self._business_query,
            "capture RG06 source business truth",
        )
        progress = self._metric_payload(context.env, "ticdc_progress")
        pipeline = self._metric_payload(context.env, "ticdc_pipeline")
        gc_progress = self._metric_payload(context.env, "gc_progress")
        return {
            "source_business_truth": capture_query_result_truth(
                source_truth_payload,
                ordered=True,
            ),
            "source_integrity": self._integrity(context.env, self._source_table),
            "sink_integrity": self._integrity(context.env, self._sink_table),
            "fault_config": self._config_row(context.env),
            "ticdc_progress": progress,
            "ticdc_pipeline": pipeline,
            "gc_progress": gc_progress,
            "reference_observation_units": self._reference_observation_units(
                progress,
                pipeline,
                gc_progress,
            ),
        }

    def quiesce(self, context: FaultLifecycleContext):
        self._configure(context.config)
        self._stop_pipeline()

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config)
        try:
            self._stop_pipeline()
        finally:
            self._drop_tables(context.env)

    def _configure(self, config: Mapping[str, object]) -> None:
        self._db = validate_sql_identifier(str(config["db"]), "db")
        self._source_table = validate_sql_identifier(str(config["source_table"]), "source_table")
        self._sink_table = validate_sql_identifier(str(config["sink_table"]), "sink_table")
        self._config_table = validate_sql_identifier(str(config["config_table"]), "config_table")
        self._registry_table = validate_sql_identifier(str(config["registry_table"]), "registry_table")
        self._metrics_table = validate_sql_identifier(str(config["metrics_table"]), "metrics_table")
        self._error_table = validate_sql_identifier(str(config["error_table"]), "error_table")
        self._archive_table = validate_sql_identifier(str(config["archive_table"]), "archive_table")
        self._observability_table = validate_sql_identifier(
            str(config["observability_table"]), "observability_table"
        )
        self._neighbor_source_table = validate_sql_identifier(
            str(config["neighbor_source_table"]), "neighbor_source_table"
        )
        self._neighbor_sink_table = validate_sql_identifier(
            str(config["neighbor_sink_table"]), "neighbor_sink_table"
        )
        self._business_query = str(config["business_query"])
        self._source_row_count = int(config["source_row_count"])
        self._initial_sink_row_count = int(config["initial_sink_row_count"])
        self._neighbor_source_row_count = int(config["neighbor_source_row_count"])
        self._neighbor_initial_sink_row_count = int(config["neighbor_initial_sink_row_count"])
        self._changefeed_id = str(config["changefeed_id"])
        self._gc_ttl_seconds = int(config["gc_ttl_seconds"])
        self._initial_sink_workers = int(config["initial_sink_workers"])
        self._initial_sorter_memory_mb = int(config["initial_sorter_memory_mb"])
        self._initial_sink_batch_rows = int(config["initial_sink_batch_rows"])
        self._initial_sink_write_budget = str(config["initial_sink_write_budget"])
        self._neighbor_changefeed_id = str(config["neighbor_changefeed_id"])
        self._safe_sink_workers_min = int(config["safe_sink_workers_min"])
        self._safe_sink_workers_max = int(config["safe_sink_workers_max"])
        self._safe_sorter_memory_mb_min = int(config["safe_sorter_memory_mb_min"])
        self._safe_sorter_memory_mb_max = int(config["safe_sorter_memory_mb_max"])
        self._safe_sink_batch_rows_min = int(config["safe_sink_batch_rows_min"])
        self._safe_sink_batch_rows_max = int(config["safe_sink_batch_rows_max"])
        self._safe_sink_write_budget_min = float(config["safe_sink_write_budget_min"])
        self._safe_sink_write_budget_max = float(config["safe_sink_write_budget_max"])

    @staticmethod
    def _execute(env, sql: str, context: str) -> dict:
        return require_success_payload(env.execute_sql(sql), f"{context}: sql={sql!r}")

    @staticmethod
    def _payload(env, sql: str, context: str) -> dict:
        return require_success_payload(parse_json_object(env.execute_sql(sql), context), context)

    def _create_tables(self, env) -> None:
        self._execute(env, f"CREATE DATABASE IF NOT EXISTS {self._db}", f"create RG06 database {self._db}")
        self._drop_tables(env)
        self._execute(
            env,
            f"CREATE TABLE {self._db}.{self._source_table} ("
            "event_id BIGINT NOT NULL PRIMARY KEY, "
            "tenant_id INT NOT NULL, "
            "event_type VARCHAR(16) NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, "
            "payload VARCHAR(128) NOT NULL, "
            "source_ts DATETIME(6) NOT NULL, "
            "KEY idx_rg06_source_tenant (tenant_id, event_id), "
            "KEY idx_rg06_source_type (event_type, event_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG06 source table {self._source_table}",
        )
        self._execute(
            env,
            f"CREATE TABLE {self._db}.{self._sink_table} ("
            "event_id BIGINT NOT NULL PRIMARY KEY, "
            "tenant_id INT NOT NULL, "
            "event_type VARCHAR(16) NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, "
            "payload VARCHAR(128) NOT NULL, "
            "source_ts DATETIME(6) NOT NULL, "
            "applied_ts DATETIME(6) NOT NULL, "
            "KEY idx_rg06_sink_tenant (tenant_id, event_id), "
            "KEY idx_rg06_sink_type (event_type, event_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG06 sink table {self._sink_table}",
        )
        self._execute(
            env,
            f"CREATE TABLE {self._db}.{self._neighbor_source_table} ("
            "event_id BIGINT NOT NULL PRIMARY KEY, "
            "tenant_id INT NOT NULL, "
            "event_type VARCHAR(16) NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, "
            "payload VARCHAR(128) NOT NULL, "
            "source_ts DATETIME(6) NOT NULL, "
            "KEY idx_rg06_neighbor_source_tenant (tenant_id, event_id), "
            "KEY idx_rg06_neighbor_source_type (event_type, event_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG06 neighbor source table {self._neighbor_source_table}",
        )
        self._execute(
            env,
            f"CREATE TABLE {self._db}.{self._neighbor_sink_table} ("
            "event_id BIGINT NOT NULL PRIMARY KEY, "
            "tenant_id INT NOT NULL, "
            "event_type VARCHAR(16) NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, "
            "payload VARCHAR(128) NOT NULL, "
            "source_ts DATETIME(6) NOT NULL, "
            "applied_ts DATETIME(6) NOT NULL, "
            "KEY idx_rg06_neighbor_sink_tenant (tenant_id, event_id), "
            "KEY idx_rg06_neighbor_sink_type (event_type, event_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG06 neighbor sink table {self._neighbor_sink_table}",
        )
        self._execute(
            env,
            f"CREATE TABLE {self._db}.{self._config_table} ("
            "config_id TINYINT NOT NULL PRIMARY KEY, "
            "changefeed_id VARCHAR(64) NOT NULL, "
            "state VARCHAR(16) NOT NULL, "
            "capture_workers INT NOT NULL, "
            "sorter_memory_mb INT NOT NULL, "
            "sink_workers INT NOT NULL, "
            "sink_batch_rows INT NOT NULL, "
            "sink_write_budget DECIMAL(8,3) NOT NULL, "
            "gc_ttl_seconds INT NOT NULL, "
            "overload_events INT NOT NULL, "
            "error_count INT NOT NULL, "
            "last_checkpoint_id BIGINT NOT NULL, "
            "last_resolved_id BIGINT NOT NULL"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG06 config table {self._config_table}",
        )
        self._execute(
            env,
            f"CREATE TABLE {self._db}.{self._registry_table} ("
            "feed_id VARCHAR(64) NOT NULL PRIMARY KEY, "
            "owner VARCHAR(64) NOT NULL, "
            "source_table VARCHAR(128) NOT NULL, "
            "sink_table VARCHAR(128) NOT NULL, "
            "business_purpose VARCHAR(128) NOT NULL, "
            "state VARCHAR(16) NOT NULL, "
            "lag_slo_rows INT NOT NULL, "
            "downstream_slo_ms INT NOT NULL"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG06 changefeed registry {self._registry_table}",
        )
        self._execute(
            env,
            f"CREATE TABLE {self._db}.{self._metrics_table} ("
            "sample_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
            "sample_ts DATETIME(6) NOT NULL, "
            "family VARCHAR(16) NOT NULL, "
            "component VARCHAR(32) NOT NULL, "
            "metric_name VARCHAR(64) NOT NULL, "
            "target VARCHAR(64) NOT NULL, "
            "value DECIMAL(20,6) NULL, "
            "text_value VARCHAR(64) NULL, "
            "unit VARCHAR(32) NOT NULL, "
            "KEY idx_rg06_metric_window (family, sample_ts, metric_name)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG06 metrics table {self._metrics_table}",
        )
        self._execute(
            env,
            f"CREATE TABLE {self._db}.{self._error_table} ("
            "error_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
            "event_ts DATETIME(6) NOT NULL, "
            "error_code VARCHAR(32) NOT NULL, "
            "message VARCHAR(255) NOT NULL"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG06 errors table {self._error_table}",
        )
        self._execute(
            env,
            f"CREATE TABLE {self._db}.{self._archive_table} ("
            "archive_id BIGINT NOT NULL PRIMARY KEY, archive_day DATE NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG06 archive audit table {self._archive_table}",
        )
        self._execute(
            env,
            f"CREATE TABLE {self._db}.{self._observability_table} ("
            "sample_id BIGINT NOT NULL PRIMARY KEY, component VARCHAR(32) NOT NULL, "
            "value DECIMAL(20,6) NOT NULL"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
            f"create RG06 observability samples {self._observability_table}",
        )
        self._seed_source(env)
        self._seed_neighbor_source(env)
        self._execute(
            env,
            f"INSERT INTO {self._db}.{self._sink_table} "
            "(event_id, tenant_id, event_type, amount, payload, source_ts, applied_ts) "
            f"SELECT event_id, tenant_id, event_type, amount, payload, source_ts, NOW(6) "
            f"FROM {self._db}.{self._source_table} "
            f"WHERE event_id <= {self._initial_sink_row_count}",
            "seed RG06 sink prefix",
        )
        self._execute(
            env,
            f"INSERT INTO {self._db}.{self._neighbor_sink_table} "
            "(event_id, tenant_id, event_type, amount, payload, source_ts, applied_ts) "
            f"SELECT event_id, tenant_id, event_type, amount, payload, source_ts, NOW(6) "
            f"FROM {self._db}.{self._neighbor_source_table} "
            f"WHERE event_id <= {self._neighbor_initial_sink_row_count}",
            "seed RG06 neighbor sink prefix",
        )
        self._execute(
            env,
            f"INSERT INTO {self._db}.{self._config_table} "
            "(config_id, changefeed_id, state, capture_workers, sorter_memory_mb, "
            "sink_workers, sink_batch_rows, sink_write_budget, gc_ttl_seconds, "
            "overload_events, error_count, last_checkpoint_id, last_resolved_id) VALUES "
            f"(1, '{self._changefeed_id}', 'NORMAL', 4, {self._initial_sorter_memory_mb}, "
            f"{self._initial_sink_workers}, {self._initial_sink_batch_rows}, "
            f"{self._initial_sink_write_budget}, {self._gc_ttl_seconds}, 0, 0, "
            f"{self._initial_sink_row_count}, {self._source_row_count})",
            "seed RG06 changefeed config",
        )
        self._execute(
            env,
            f"INSERT INTO {self._db}.{self._registry_table} "
            "(feed_id, owner, source_table, sink_table, business_purpose, state, "
            "lag_slo_rows, downstream_slo_ms) VALUES "
            f"('{self._changefeed_id}', 'order-api', '{self._db}.{self._source_table}', "
            f"'{self._db}.{self._sink_table}', 'customer archive order replication', 'NORMAL', 3, 60), "
            f"('{self._neighbor_changefeed_id}', 'ledger-reconcile', '{self._db}.{self._neighbor_source_table}', "
            f"'{self._db}.{self._neighbor_sink_table}', 'settlement reconciliation mirror', 'NORMAL', 12, 80)",
            "seed RG06 changefeed registry",
        )
        self._execute(
            env,
            f"INSERT INTO {self._db}.{self._archive_table} (archive_id, archive_day, amount) "
            "SELECT n, DATE_ADD('2026-07-01', INTERVAL MOD(n, 31) DAY), "
            "CAST(MOD(n * 97, 100000) / 100 AS DECIMAL(12,2)) "
            "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) AS n "
            "FROM information_schema.columns LIMIT 96) AS numbers",
            "seed RG06 archive audit rows",
        )
        self._execute(
            env,
            f"INSERT INTO {self._db}.{self._observability_table} (sample_id, component, value) "
            "SELECT n, ELT(MOD(n, 4) + 1, 'pd', 'tikv', 'tidb', 'dashboard'), "
            "MOD(n * 37, 1000) / 10 "
            "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) AS n "
            "FROM information_schema.columns LIMIT 128) AS numbers",
            "seed RG06 observability sample rows",
        )
        self._seed_retained_neighbor_observations(env)

    def _seed_retained_neighbor_observations(self, env) -> None:
        for family in ("progress", "pipeline", "resource"):
            self._execute(
                env,
                f"INSERT INTO {self._db}.{self._metrics_table} "
                "(sample_ts, family, component, metric_name, target, value, text_value, unit) "
                "SELECT TIMESTAMPADD(SECOND, -MOD(n, 45), NOW(6)), "
                f"'{family}', ELT(MOD(n, 6) + 1, 'capture', 'sorter', 'sink', 'downstream', 'gc', 'tikv'), "
                "ELT(MOD(n, 12) + 1, "
                "'capture_rows_per_second', 'resolved_event_id', 'sorter_rows_per_second', "
                "'sorter_queue_rows', 'sink_write_rows_per_second', 'sink_write_p95_ms', "
                "'downstream_write_p95_ms', 'gc_headroom_seconds', 'tikv_cpu_percent', "
                "'disk_write_mb_per_second', 'network_rtt_ms', 'downstream_connections'), "
                f"'{self._neighbor_changefeed_id}', "
                "CASE MOD(n, 12) "
                "WHEN 0 THEN 82.0 WHEN 1 THEN 890.0 WHEN 2 THEN 78.0 WHEN 3 THEN 3.0 "
                "WHEN 4 THEN 76.0 WHEN 5 THEN 14.0 WHEN 6 THEN 18.0 WHEN 7 THEN 1120.0 "
                "WHEN 8 THEN 24.0 WHEN 9 THEN 8.0 WHEN 10 THEN 4.5 ELSE 6.0 END, "
                "NULL, 'gauge' "
                "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) AS n "
                "FROM information_schema.columns LIMIT 180) AS numbers",
                f"seed RG06 {family} retained neighbor observations",
            )

    def _seed_source(self, env) -> None:
        batch_size = 600
        inserted = 0
        while inserted < self._source_row_count:
            size = min(batch_size, self._source_row_count - inserted)
            start = inserted
            self._execute(
                env,
                f"INSERT INTO {self._db}.{self._source_table} "
                "(event_id, tenant_id, event_type, amount, payload, source_ts) "
                "SELECT "
                f"{start} + n, MOD({start} + n, 64), "
                f"CASE WHEN MOD({start} + n, 5) = 0 THEN 'settled' "
                f"WHEN MOD({start} + n, 5) = 1 THEN 'captured' "
                f"WHEN MOD({start} + n, 5) = 2 THEN 'authorized' "
                "ELSE 'cancelled' END, "
                f"CAST(MOD(({start} + n) * 7919, 100000) / 100 AS DECIMAL(12,2)), "
                f"CONCAT('order-', {start} + n), "
                f"TIMESTAMPADD(SECOND, {start} + n, TIMESTAMP'2026-07-01 00:00:00') "
                "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) AS n "
                f"FROM information_schema.columns LIMIT {size}) AS numbers",
                f"seed RG06 source rows starting at {start}",
            )
            inserted += size

    def _seed_neighbor_source(self, env) -> None:
        batch_size = 300
        inserted = 0
        while inserted < self._neighbor_source_row_count:
            size = min(batch_size, self._neighbor_source_row_count - inserted)
            start = inserted
            self._execute(
                env,
                f"INSERT INTO {self._db}.{self._neighbor_source_table} "
                "(event_id, tenant_id, event_type, amount, payload, source_ts) "
                "SELECT "
                f"{start} + n, 11 + MOD({start} + n, 4), "
                f"CASE WHEN MOD({start} + n, 3) = 0 THEN 'settled' "
                f"WHEN MOD({start} + n, 3) = 1 THEN 'captured' "
                "ELSE 'authorized' END, "
                f"CAST(MOD(({start} + n) * 6151, 100000) / 100 AS DECIMAL(12,2)), "
                f"CONCAT('reconcile-', {start} + n), "
                f"TIMESTAMPADD(SECOND, {start} + n, TIMESTAMP'2026-07-01 00:00:00') "
                "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) AS n "
                f"FROM information_schema.columns LIMIT {size}) AS numbers",
                f"seed RG06 neighbor source rows starting at {start}",
            )
            inserted += size

    def _verify_fault_state(self, env) -> None:
        config = self._config_row(env)
        expected = (
            self._changefeed_id,
            "NORMAL",
            4,
            self._initial_sorter_memory_mb,
            self._initial_sink_workers,
            self._initial_sink_batch_rows,
            float(self._initial_sink_write_budget),
        )
        observed = (
            config["changefeed_id"],
            config["state"],
            int(config["capture_workers"]),
            int(config["sorter_memory_mb"]),
            int(config["sink_workers"]),
            int(config["sink_batch_rows"]),
            float(config["sink_write_budget"]),
        )
        if observed != expected:
            raise RuntimeError(
                "RG06 fault config mismatch before agent handoff: "
                f"expected={expected!r}, observed={observed!r}"
            )
        source_count = self._integrity(env, self._source_table)[0]
        sink_count = self._integrity(env, self._sink_table)[0]
        neighbor_source_count = self._integrity(env, self._neighbor_source_table)[0]
        neighbor_sink_count = self._integrity(env, self._neighbor_sink_table)[0]
        if (
            source_count != self._source_row_count
            or sink_count != self._initial_sink_row_count
            or neighbor_source_count != self._neighbor_source_row_count
            or neighbor_sink_count != self._neighbor_initial_sink_row_count
        ):
            raise RuntimeError(
                "RG06 replication fixture mismatch before agent handoff: "
                f"source_count={source_count}, expected_source={self._source_row_count}, "
                f"sink_count={sink_count}, expected_sink={self._initial_sink_row_count}, "
                f"neighbor_source_count={neighbor_source_count}, "
                f"expected_neighbor_source={self._neighbor_source_row_count}, "
                f"neighbor_sink_count={neighbor_sink_count}, "
                f"expected_neighbor_sink={self._neighbor_initial_sink_row_count}"
            )

    def _config_row(self, env) -> dict:
        payload = self._payload(
            env,
            f"SELECT changefeed_id, state, capture_workers, sorter_memory_mb, sink_workers, "
            f"sink_batch_rows, sink_write_budget, gc_ttl_seconds, overload_events, error_count, "
            f"last_checkpoint_id, last_resolved_id FROM {self._db}.{self._config_table} "
            "WHERE config_id = 1",
            "read RG06 config",
        )
        rows = payload["result"]
        if len(rows) != 1:
            raise RuntimeError(f"RG06 config must contain one row: rows={rows!r}")
        row = rows[0]
        return {
            "changefeed_id": row[0],
            "state": row[1],
            "capture_workers": row[2],
            "sorter_memory_mb": row[3],
            "sink_workers": row[4],
            "sink_batch_rows": row[5],
            "sink_write_budget": row[6],
            "gc_ttl_seconds": row[7],
            "overload_events": row[8],
            "error_count": row[9],
            "last_checkpoint_id": row[10],
            "last_resolved_id": row[11],
        }

    def _integrity(self, env, table: str) -> tuple[int, int, int]:
        payload = self._payload(
            env,
            f"SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_type, amount, payload))), 0) "
            f"FROM {self._db}.{table}",
            f"read RG06 integrity for {table}",
        )
        row = payload["result"]
        if len(row) != 1:
            raise RuntimeError(f"RG06 integrity query returned no single row: table={table!r}, result={row!r}")
        return int(row[0][0]), int(row[0][1]), int(row[0][2])

    def _metric_payload(self, env, metric: str) -> dict:
        return require_success_payload(
            parse_json_object(
                env.observe_metric(metric),
                f"capture RG06 metric {metric}",
            ),
            f"capture RG06 metric {metric}",
        )

    def _reference_observation_units(self, *payloads: dict) -> dict[str, dict[str, int]]:
        result = {}
        for payload in payloads:
            metric = str(payload["metric"])
            records = payload.get("records", [])
            if metric == "gc_progress":
                causal_names = {"gc_headroom_seconds", "error_count", "overload_events"}
            else:
                causal_names = self._CAUSAL_METRICS
            causal = sum(
                1
                for row in records
                if row.get("target") == self._changefeed_id
                and row.get("metric_name") in causal_names
            )
            result[metric] = {"causal": causal, "noise": len(records) - causal}
        return result

    def _drop_tables(self, env) -> None:
        for table in (
            self._observability_table,
            self._archive_table,
            self._error_table,
            self._metrics_table,
            self._registry_table,
            self._config_table,
            self._neighbor_sink_table,
            self._neighbor_source_table,
            self._sink_table,
            self._source_table,
        ):
            self._execute(env, f"DROP TABLE IF EXISTS {self._db}.{table}", f"drop RG06 table {table}")

    def _start_pipeline(self, env) -> None:
        if self._pipeline_thread is not None and self._pipeline_thread.is_alive():
            raise RuntimeError("RG06 pipeline is already running")
        self._stop_event.clear()
        self._thread_error = None
        self._pipeline_thread = threading.Thread(
            target=self._pipeline_loop,
            args=(env,),
            name="aiopsbench-rg06-ticdc",
            daemon=True,
        )
        self._pipeline_thread.start()

    def _stop_pipeline(self) -> None:
        if self._pipeline_thread is None:
            return
        self._stop_event.set()
        self._pipeline_thread.join(timeout=20)
        if self._pipeline_thread.is_alive():
            raise RuntimeError("RG06 pipeline thread did not stop within 20 seconds")
        thread_error = self._thread_error
        self._pipeline_thread = None
        if thread_error is not None:
            raise RuntimeError(f"RG06 pipeline failed: {thread_error!r}") from thread_error

    def _check_thread(self, context: FaultLifecycleContext) -> None:
        if self._pipeline_thread is None or not self._pipeline_thread.is_alive():
            raise RuntimeError(
                "RG06 pipeline is not running before observability: "
                f"run_id={context.run_id!r}, error={self._thread_error!r}"
            )
        if self._thread_error is not None:
            raise RuntimeError(
                "RG06 pipeline failed before observability: "
                f"run_id={context.run_id!r}, error={self._thread_error!r}"
            ) from self._thread_error

    def _pipeline_loop(self, env) -> None:
        connection = env.open_workload_connection("ticdc-rg06-simulator")
        try:
            while not self._stop_event.wait(0.5):
                self._pipeline_tick(connection)
        except Exception as exc:
            self._thread_error = exc
            raise
        finally:
            connection.close()

    def _advance_neighbor_pipeline(self, cursor) -> tuple[tuple[object, ...], ...]:
        cursor.execute(
            f"SELECT COALESCE(MAX(event_id), 0) FROM {self._db}.{self._neighbor_source_table}"
        )
        next_event_id = int(cursor.fetchone()[0]) + 1
        neighbor_rows = []
        for event_id in range(next_event_id, next_event_id + 2):
            neighbor_rows.append(
                (
                    event_id,
                    11 + event_id % 4,
                    ("settled", "captured", "authorized")[event_id % 3],
                    f"{(event_id * 6151) % 100000 / 100:.2f}",
                    f"reconcile-{event_id}",
                )
            )
        cursor.executemany(
            f"INSERT INTO {self._db}.{self._neighbor_source_table} "
            "(event_id, tenant_id, event_type, amount, payload, source_ts) "
            "VALUES (%s, %s, %s, %s, %s, NOW(6))",
            neighbor_rows,
        )
        cursor.execute(
            f"SELECT COUNT(*), COALESCE(MAX(event_id), 0) "
            f"FROM {self._db}.{self._neighbor_source_table}"
        )
        source_count, resolved_event_id = cursor.fetchone()
        cursor.execute(
            f"SELECT COUNT(*), COALESCE(MAX(event_id), 0) "
            f"FROM {self._db}.{self._neighbor_sink_table}"
        )
        sink_count_before, checkpoint_before = cursor.fetchone()
        cursor.execute(
            f"INSERT IGNORE INTO {self._db}.{self._neighbor_sink_table} "
            "(event_id, tenant_id, event_type, amount, payload, source_ts, applied_ts) "
            f"SELECT s.event_id, s.tenant_id, s.event_type, s.amount, s.payload, s.source_ts, NOW(6) "
            f"FROM {self._db}.{self._neighbor_source_table} AS s "
            f"LEFT JOIN {self._db}.{self._neighbor_sink_table} AS k ON k.event_id = s.event_id "
            "WHERE k.event_id IS NULL ORDER BY s.event_id LIMIT 128"
        )
        copied = max(0, int(cursor.rowcount))
        cursor.execute(
            f"SELECT COUNT(*), COALESCE(MAX(event_id), 0) "
            f"FROM {self._db}.{self._neighbor_sink_table}"
        )
        sink_count, checkpoint_event_id = cursor.fetchone()
        lag_rows = max(0, int(source_count) - int(sink_count))
        sink_rate = round(max(1.0, copied / 0.5), 3)
        target = self._neighbor_changefeed_id
        return (
            ("progress", "capture", "resolved_event_id", target, resolved_event_id, None, "event_id"),
            ("progress", "sink", "checkpoint_event_id", target, checkpoint_event_id, None, "event_id"),
            ("progress", "changefeed", "checkpoint_lag_rows", target, lag_rows, None, "rows"),
            ("progress", "changefeed", "changefeed_state", target, None, "NORMAL", "state"),
            ("progress", "changefeed", "error_count", target, 0, None, "errors"),
            ("progress", "changefeed", "overload_events", target, 0, None, "events"),
            ("pipeline", "capture", "capture_rows_per_second", target, 8.0, None, "rows/s"),
            ("pipeline", "sorter", "sorter_rows_per_second", target, 8.0, None, "rows/s"),
            ("pipeline", "sorter", "sorter_queue_rows", target, lag_rows, None, "rows"),
            ("pipeline", "sink", "sink_write_rows_per_second", target, sink_rate, None, "rows/s"),
            ("pipeline", "sink", "sink_write_p95_ms", target, 12.0, None, "ms"),
            ("pipeline", "downstream", "downstream_write_p95_ms", target, 12.0, None, "ms"),
            ("pipeline", "foreground", "foreground_p95_ms", target, 15.0, None, "ms"),
            ("pipeline", "mounter", "mounter_rows_per_second", target, 7.8, None, "rows/s"),
            ("pipeline", "puller", "puller_rows_per_second", target, 8.5, None, "rows/s"),
            ("pipeline", "sorter", "sorter_disk_mb", target, 0.0, None, "MB"),
            ("pipeline", "sink", "sink_retry_rate", target, 0.01, None, "ratio"),
            ("pipeline", "network", "network_rtt_ms", target, 4.5, None, "ms"),
            ("pipeline", "downstream", "downstream_connections", target, 6.0, None, "connections"),
            ("resource", "gc", "gc_headroom_seconds", target, 1180.0, None, "seconds"),
            ("resource", "tikv", "tikv_cpu_percent", target, 24.0, None, "%"),
            ("resource", "tikv", "tikv_memory_percent", target, 39.0, None, "%"),
            ("resource", "pd", "pd_cpu_percent", target, 11.0, None, "%"),
            ("resource", "tikv", "disk_write_mb_per_second", target, 7.0, None, "MB/s"),
            ("resource", "tikv", "region_count", target, 384.0, None, "regions"),
            ("resource", "gc", "gc_safepoint_age_seconds", target, 3.0, None, "seconds"),
        )

    def _pipeline_tick(self, connection) -> None:
        tick_started = time.monotonic()
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT sink_workers, sorter_memory_mb, sink_batch_rows, sink_write_budget, "
                f"gc_ttl_seconds, overload_events, error_count FROM {self._db}.{self._config_table} "
                "WHERE config_id = 1"
            )
            config = cursor.fetchone()
            if config is None:
                raise RuntimeError("RG06 pipeline config row disappeared")
            sink_workers, sorter_memory_mb, sink_batch_rows, sink_write_budget, gc_ttl, overload_events, error_count = config
            sink_workers = int(sink_workers)
            sorter_memory_mb = int(sorter_memory_mb)
            sink_batch_rows = int(sink_batch_rows)
            sink_write_budget = float(sink_write_budget)
            gc_ttl = int(gc_ttl)
            cursor.execute(
                f"SELECT COUNT(*), COALESCE(MAX(event_id), 0) FROM {self._db}.{self._source_table}"
            )
            source_count, resolved_event_id = cursor.fetchone()
            cursor.execute(
                f"SELECT COUNT(*), COALESCE(MAX(event_id), 0) FROM {self._db}.{self._sink_table}"
            )
            sink_count_before, checkpoint_before = cursor.fetchone()
            load_factor = sink_workers * sink_write_budget * (sorter_memory_mb / 128.0)
            overloaded = (
                sink_workers > self._safe_sink_workers_max
                or sorter_memory_mb > self._safe_sorter_memory_mb_max
                or sink_batch_rows > self._safe_sink_batch_rows_max
                or sink_write_budget > self._safe_sink_write_budget_max
                or load_factor > 32.0
            )
            capacity = max(
                1,
                min(
                    int(sink_workers * sink_batch_rows * sink_write_budget),
                    int(sorter_memory_mb / 2),
                ),
            )
            if overloaded:
                capacity = max(1, int(capacity / 4))
            capacity = min(capacity, 2000)
            cursor.execute(
                f"INSERT IGNORE INTO {self._db}.{self._sink_table} "
                "(event_id, tenant_id, event_type, amount, payload, source_ts, applied_ts) "
                f"SELECT s.event_id, s.tenant_id, s.event_type, s.amount, s.payload, s.source_ts, NOW(6) "
                f"FROM {self._db}.{self._source_table} AS s "
                f"LEFT JOIN {self._db}.{self._sink_table} AS k ON k.event_id = s.event_id "
                "WHERE k.event_id IS NULL ORDER BY s.event_id LIMIT %s",
                (capacity,),
            )
            copied = max(0, int(cursor.rowcount))
            cursor.execute(
                f"SELECT COUNT(*), COALESCE(MAX(event_id), 0) FROM {self._db}.{self._sink_table}"
            )
            sink_count, checkpoint_event_id = cursor.fetchone()
            neighbor_metrics = self._advance_neighbor_pipeline(cursor)
            cursor.execute(
                f"SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM {self._db}.{self._source_table} "
                "WHERE tenant_id = 7"
            )
            probe_started = time.monotonic()
            cursor.fetchone()
            foreground_probe_ms = round((time.monotonic() - probe_started) * 1000, 3)
            elapsed_seconds = max(time.monotonic() - tick_started, 0.001)
            capture_rate = round(max(1.0, min(float(source_count) / 12.0, 240.0)), 3)
            sorter_rate = round(min(capture_rate, sorter_memory_mb * 2.0), 3)
            sink_rate = round(max(1.0, copied / elapsed_seconds if copied else capacity), 3)
            lag_rows = max(0, int(source_count) - int(sink_count))
            sink_p95_ms = round(max(foreground_probe_ms, 8.0 + load_factor * 1.5), 3)
            foreground_p95_ms = round(max(foreground_probe_ms, 10.0 + load_factor * 1.2), 3)
            gc_headroom = round(
                max(0.0, gc_ttl - lag_rows / max(capture_rate, 1.0)),
                3,
            )
            next_overload_events = int(overload_events) + int(overloaded)
            next_error_count = int(error_count) + int(overloaded)
            cursor.execute(
                f"UPDATE {self._db}.{self._config_table} SET overload_events = %s, error_count = %s, "
                "last_checkpoint_id = %s, last_resolved_id = %s WHERE config_id = 1",
                (next_overload_events, next_error_count, checkpoint_event_id, resolved_event_id),
            )
            if overloaded:
                cursor.execute(
                    f"INSERT INTO {self._db}.{self._error_table} (event_ts, error_code, message) "
                    "VALUES (NOW(6), 'RESOURCE_OVERLOAD', %s)",
                    (
                        f"sink_workers={sink_workers}, sorter_memory_mb={sorter_memory_mb}, "
                        f"sink_batch_rows={sink_batch_rows}, sink_write_budget={sink_write_budget}",
                    ),
                )
            target = self._changefeed_id
            metrics = (
                ("progress", "capture", "resolved_event_id", target, resolved_event_id, None, "event_id"),
                ("progress", "sink", "checkpoint_event_id", target, checkpoint_event_id, None, "event_id"),
                ("progress", "changefeed", "checkpoint_lag_rows", target, lag_rows, None, "rows"),
                ("progress", "changefeed", "changefeed_state", target, None, "NORMAL", "state"),
                ("progress", "changefeed", "error_count", target, next_error_count, None, "errors"),
                ("progress", "changefeed", "overload_events", target, next_overload_events, None, "events"),
                ("pipeline", "capture", "capture_rows_per_second", target, capture_rate, None, "rows/s"),
                ("pipeline", "sorter", "sorter_rows_per_second", target, sorter_rate, None, "rows/s"),
                ("pipeline", "sorter", "sorter_queue_rows", target, lag_rows, None, "rows"),
                ("pipeline", "sink", "sink_write_rows_per_second", target, sink_rate, None, "rows/s"),
                ("pipeline", "sink", "sink_write_p95_ms", target, sink_p95_ms, None, "ms"),
                ("pipeline", "downstream", "downstream_write_p95_ms", target, sink_p95_ms, None, "ms"),
                ("pipeline", "foreground", "foreground_p95_ms", target, foreground_p95_ms, None, "ms"),
                ("pipeline", "mounter", "mounter_rows_per_second", target, round(capture_rate * 0.97, 3), None, "rows/s"),
                ("pipeline", "puller", "puller_rows_per_second", target, round(capture_rate * 1.08, 3), None, "rows/s"),
                ("pipeline", "sorter", "sorter_disk_mb", target, round(lag_rows / 16.0, 3), None, "MB"),
                ("pipeline", "sink", "sink_retry_rate", target, round(0.02 + int(overloaded) * 0.5, 3), None, "ratio"),
                ("pipeline", "network", "network_rtt_ms", target, 4.5, None, "ms"),
                ("pipeline", "downstream", "downstream_connections", target, 8, None, "connections"),
                ("resource", "gc", "gc_headroom_seconds", target, gc_headroom, None, "seconds"),
                ("resource", "tikv", "tikv_cpu_percent", target, round(min(99.0, 18.0 + load_factor * 3), 3), None, "%"),
                ("resource", "tikv", "tikv_memory_percent", target, round(min(99.0, 35.0 + sorter_memory_mb / 32), 3), None, "%"),
                ("resource", "pd", "pd_cpu_percent", target, 11.0, None, "%"),
                ("resource", "tikv", "disk_write_mb_per_second", target, round(3.0 + sink_rate / 18, 3), None, "MB/s"),
                ("resource", "tikv", "region_count", target, 384, None, "regions"),
                ("resource", "gc", "gc_safepoint_age_seconds", target, round(lag_rows / 4.0, 3), None, "seconds"),
            )
            metrics = metrics + neighbor_metrics
            cursor.executemany(
                f"INSERT INTO {self._db}.{self._metrics_table} "
                "(sample_ts, family, component, metric_name, target, value, text_value, unit) "
                "VALUES (NOW(6), %s, %s, %s, %s, %s, %s, %s)",
                metrics,
            )
            connection.commit()


class TidbResourceGovernanceRg06Scenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_rg06"
    description = (
        "TiCDC checkpoint lag and sink budget governance with a real SQL source/sink harness, "
        "foreground business workload, and GC headroom constraints."
    )
    cases = (_RG06_CASE, _RG06_RECONCILE_CASE)

    def build_fault_plan(self, case: TiDBScenarioCase) -> tuple[FaultPlan, ...]:
        if not isinstance(case, TidbResourceGovernanceRg06ForCheckpointSinkBudgetScenarioCase):
            raise TypeError(
                "RG06 requires "
                "TidbResourceGovernanceRg06ForCheckpointSinkBudgetScenarioCase, "
                f"got {type(case).__name__}"
            )
        return (
            FaultPlan(
                injector_type=TidbResourceGovernanceRg06Injector,
                config={
                    "db": case.db,
                    "source_table": case.source_table,
                    "sink_table": case.sink_table,
                    "config_table": case.config_table,
                    "registry_table": case.registry_table,
                    "metrics_table": case.metrics_table,
                    "error_table": case.error_table,
                    "archive_table": case.archive_table,
                    "observability_table": case.observability_table,
                    "neighbor_source_table": case.neighbor_source_table,
                    "neighbor_sink_table": case.neighbor_sink_table,
                    "business_query": case.business_query,
                    "source_row_count": case.source_row_count,
                    "initial_sink_row_count": case.initial_sink_row_count,
                    "neighbor_source_row_count": case.neighbor_source_row_count,
                    "neighbor_initial_sink_row_count": case.neighbor_initial_sink_row_count,
                    "changefeed_id": case.changefeed_id,
                    "neighbor_changefeed_id": case.neighbor_changefeed_id,
                    "gc_ttl_seconds": 1200,
                    "initial_sink_workers": 1,
                    "initial_sorter_memory_mb": 64,
                    "initial_sink_batch_rows": 8,
                    "initial_sink_write_budget": "0.05",
                    "safe_sink_workers_min": 4,
                    "safe_sink_workers_max": 16,
                    "safe_sorter_memory_mb_min": 128,
                    "safe_sorter_memory_mb_max": 512,
                    "safe_sink_batch_rows_min": 32,
                    "safe_sink_batch_rows_max": 256,
                    "safe_sink_write_budget_min": "0.25",
                    "safe_sink_write_budget_max": "1.00",
                },
            ),
        )


__all__ = (
    "TidbResourceGovernanceRg06ForCheckpointSinkBudgetScenarioCase",
    "TidbResourceGovernanceRg06Scenario",
)
