from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.query_perf import (
    PgQueryPerfCachePollutionForAnalyticsCursorCacheChurnEvaluatorCase,
    PgQueryPerfCachePollutionForArchiveScanCachePollutionEvaluatorCase,
    PgQueryPerfCachePollutionForBillingExportScanCacheChurnEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    PostgresCaseRuntime,
    PostgresScenario,
    BackgroundWorkloadSpec,
    EMPTY_BACKGROUND_WORKLOAD,
    DifficultyCalibration,
    FaultPlan,
    CaseResourceSpec,
    PostgresScenarioCase,
)


IO_SATURATION_POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfCachePollutionCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    fault_variant: str
    hot_table: str
    archive_table: str
    control_table: str
    scan_app_name: str
    oltp_app_name: str
    customer_noise_table: str
    inventory_noise_table: str
    customer_noise_app: str
    inventory_noise_app: str
    hot_rows: int
    archive_rows: int
    customer_noise_rows: int
    inventory_noise_rows: int
    shared_buffers: str
    scan_seconds: int
    dead_tuple_threshold: int
    noise_profiles: tuple[object, ...]

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfCachePollutionForArchiveScanCachePollutionScenarioCase(PgQueryPerfCachePollutionCase):
    pass

_PGQUERYPERFCACHEPOLLUTIONSCENARIO_CASE = PgQueryPerfCachePollutionForArchiveScanCachePollutionScenarioCase(
    case_id='archive_scan_cache_pollution',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "low cache hit ratio",
                    "entity": "orders_current",
                    "evidence": [
                        "cache_hit_ratio showed degradation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "archive scan cache pollution",
                    "entity": "svc_audit_rollup",
                    "evidence": [
                        "pg_stat_activity identified the reporting scan"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "memory sizing is not root cause",
                    "entity": "shared_buffers",
                    "evidence": [
                        "pg_settings showed the intended memory configuration"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "hot page displacement",
                    "entity": "orders_current",
                    "evidence": [
                        "pg_buffercache showed archive pages displacing hot OLTP pages"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "workload isolation",
                    "entity": "svc_audit_rollup",
                    "evidence": [
                        "the recurrence control isolates and limits this reporting workload"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "terminated only svc_audit_rollup",
                "persisted recurrence control in ops_workload_controls"
            ],
            "verification": [
                "svc_audit_rollup is absent",
                "orders_current probe succeeds"
            ]
        },
        "summary": "Targeted remediation removed cache pressure without resizing memory or restarting PostgreSQL."
    },
    case_no=0,
    evaluator=PgQueryPerfCachePollutionForArchiveScanCachePollutionEvaluatorCase,
    base_image_name='aiopsbench-pg-default:latest',
    workload_tag='default',
    fault_variant='scan_cache_pollution',
    title='Shared buffer hit-ratio alert caused by a mixed reporting scan evicting OLTP pages.',
    alert='[FIRING: WARNING] alertname=PostgresSharedBufferHitRatioLow service=tpcc-order-entry instance=postgresql-primary severity=warning\nsummary=PostgreSQL shared buffer hit ratio dropped sharply during TPC-C order-entry traffic\ndescription=cache_hit_ratio fell below 85% while order-entry read latency increased. The memory dashboard marks shared buffer pressure as the initial suspect. Diagnose the database cause and restore OLTP cache behavior without blindly increasing memory.',
    initial_state={'status': 'degraded',
 'alert': 'shared_buffer_hit_ratio_low',
 'hot_table': 'orders_current',
 'archive_table': 'orders_audit_archive',
 'visible_symptom': 'cache_hit_ratio_drop_with_oltp_latency_increase',
 'shared_buffers': '32MB'},
    expected_target={'status': 'recovered',
 'hot_table': 'orders_current',
 'archive_table': 'orders_audit_archive',
 'active_reporting_scans': 0,
 'mitigation': 'limit_or_isolate_large_reporting_scans',
 'root_cause': 'mixed_workload_cache_pollution'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=IO_SATURATION_POSTGRES_RESOURCES),
    hot_table='orders_current',
    archive_table='orders_audit_archive',
    control_table='ops_workload_controls',
    scan_app_name='svc_audit_rollup',
    oltp_app_name='order_entry_probe',
    customer_noise_table='customer_activity_log',
    inventory_noise_table='inventory_snapshot',
    customer_noise_app='customer-history-api',
    inventory_noise_app='inventory-rebalance',
    hot_rows=8000,
    archive_rows=90000,
    customer_noise_rows=45000,
    inventory_noise_rows=36000,
    shared_buffers='32MB',
    scan_seconds=600,
    dead_tuple_threshold=0,
    noise_profiles=(WorkloadProfile(name='order_entry_recent_status_lookup',
                 sql='SELECT customer_id, count(*), sum(amount) FROM orders_current WHERE order_id '
                     'BETWEEN 1 + floor(random() * 6000)::int AND 2000 + floor(random() * '
                     '6000)::int GROUP BY customer_id ORDER BY sum(amount) DESC LIMIT 20',
                 qps=0.8,
                 tier='OLTP_NOISE',
                 commit=False,
                 application_name='order-entry-api'),
 WorkloadProfile(name='customer_history_rollup',
                 sql='SELECT customer_id, count(*), sum(length(payload)) FROM '
                     "customer_activity_log WHERE event_ts > now() - interval '90 days' GROUP BY "
                     'customer_id ORDER BY sum(length(payload)) DESC LIMIT 50',
                 qps=0.35,
                 tier='REPORT_NOISE',
                 commit=False,
                 application_name='customer-history-api'),
 WorkloadProfile(name='inventory_snapshot_reconciliation',
                 sql='SELECT warehouse_id, count(*), sum(length(payload)) FROM inventory_snapshot '
                     'GROUP BY warehouse_id ORDER BY sum(length(payload)) DESC',
                 qps=0.3,
                 tier='REPORT_NOISE',
                 commit=False,
                 application_name='inventory-rebalance')),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.458333,
        reference_run_ids=(
            "reference-70__pg_cache_pollution__"
            "archive_scan_cache_pollution__mock__r001",
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfCachePollutionForBillingExportScanCacheChurnScenarioCase(PgQueryPerfCachePollutionCase):
    pass

_PGQUERYPERFCACHEPOLLUTIONSCENARIO_BILLING_EXPORT_CASE = PgQueryPerfCachePollutionForBillingExportScanCacheChurnScenarioCase(
    case_id='billing_export_scan_cache_churn',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "low cache hit ratio",
                    "entity": "checkout_hot_orders",
                    "evidence": [
                        "cache_hit_ratio showed degradation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "billing export scan cache churn",
                    "entity": "billing_export_scan",
                    "evidence": [
                        "pg_stat_activity identified the reporting scan"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "memory sizing is not root cause",
                    "entity": "shared_buffers",
                    "evidence": [
                        "pg_settings showed the intended memory configuration"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "hot page displacement",
                    "entity": "checkout_hot_orders",
                    "evidence": [
                        "pg_buffercache showed archive pages displacing hot OLTP pages"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "workload isolation",
                    "entity": "billing_export_scan",
                    "evidence": [
                        "the recurrence control isolates and limits this reporting workload"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "terminated only billing_export_scan",
                "persisted recurrence control in ops_workload_controls"
            ],
            "verification": [
                "billing_export_scan is absent",
                "checkout_hot_orders probe succeeds"
            ]
        },
        "summary": "Targeted remediation removed cache pressure without resizing memory or restarting PostgreSQL."
    },
    case_no=1,
    evaluator=PgQueryPerfCachePollutionForBillingExportScanCacheChurnEvaluatorCase,
    base_image_name='aiopsbench-pg-default:latest',
    workload_tag='simple-cache-churn',
    fault_variant='scan_cache_pollution',
    title='Buffer hit-ratio alert caused by a billing export scan displacing checkout hot pages.',
    alert='[FIRING: WARNING] alertname=PostgresSharedBufferHitRatioLow service=checkout-api instance=postgresql-primary severity=warning\nsummary=Shared buffer hit ratio dropped while checkout point-lookups became slower\ndescription=The memory dashboard flags shared buffer pressure during a scheduled billing export. Diagnose the actual database cause of the cache degradation and restore checkout cache behavior without resizing memory or restarting PostgreSQL. Record the recurrence-control measure for the responsible workload in ops_workload_controls so the next export window stays bounded.',
    initial_state={'status': 'degraded',
 'alert': 'shared_buffer_hit_ratio_low',
 'hot_table': 'checkout_hot_orders',
 'archive_table': 'billing_export_history',
 'visible_symptom': 'cache_hit_ratio_drop_with_checkout_lookup_latency',
 'shared_buffers': '32MB'},
    expected_target={'status': 'recovered',
 'hot_table': 'checkout_hot_orders',
 'archive_table': 'billing_export_history',
 'active_reporting_scans': 0,
 'mitigation': 'schedule_or_limit_billing_export_scan',
 'root_cause': 'export_scan_cache_churn'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=IO_SATURATION_POSTGRES_RESOURCES),
    hot_table='checkout_hot_orders',
    archive_table='billing_export_history',
    control_table='ops_workload_controls',
    scan_app_name='billing_export_scan',
    oltp_app_name='checkout_hot_lookup_probe',
    customer_noise_table='checkout_customer_noise',
    inventory_noise_table='checkout_inventory_noise',
    customer_noise_app='checkout-customer-summary',
    inventory_noise_app='checkout-inventory-summary',
    hot_rows=6000,
    archive_rows=52000,
    customer_noise_rows=16000,
    inventory_noise_rows=14000,
    shared_buffers='32MB',
    scan_seconds=420,
    dead_tuple_threshold=0,
    noise_profiles=(),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.458333,
        reference_run_ids=(
            "reference-70__pg_cache_pollution__"
            "billing_export_scan_cache_churn__mock__r001",
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfCachePollutionForAnalyticsCursorCacheChurnScenarioCase(PgQueryPerfCachePollutionCase):
    pass

_PGQUERYPERFCACHEPOLLUTIONSCENARIO_ANALYTICS_CURSOR_CASE = PgQueryPerfCachePollutionForAnalyticsCursorCacheChurnScenarioCase(
    case_id='analytics_cursor_cache_churn',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "low cache hit ratio",
                    "entity": "order_status_hot_pages",
                    "evidence": [
                        "cache_hit_ratio showed degradation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "long analytics cursor",
                    "entity": "analytics-cursor-snapshot-11",
                    "evidence": [
                        "pg_stat_activity showed an old backend_xmin"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "vacuum blocked by old snapshot",
                    "entity": "order_status_hot_pages",
                    "evidence": [
                        "dead tuples remained while the cursor held its snapshot"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "cursor blocks vacuum causing cache churn",
                    "entity": "order_status_hot_pages",
                    "evidence": [
                        "session age, dead tuples, and cache pressure formed one causal chain"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate analytics cursor then vacuum",
                    "entity": "analytics-cursor-snapshot-11",
                    "evidence": [
                        "only the culprit cursor was terminated before cleanup"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "terminated only analytics-cursor-snapshot-11",
                "persisted recurrence control in ops_workload_controls"
            ],
            "verification": [
                "analytics-cursor-snapshot-11 is absent",
                "order_status_hot_pages probe succeeds"
            ]
        },
        "summary": "Targeted remediation removed cache pressure without resizing memory or restarting PostgreSQL."
    },
    case_no=2,
    evaluator=PgQueryPerfCachePollutionForAnalyticsCursorCacheChurnEvaluatorCase,
    base_image_name='aiopsbench-pg-default:latest',
    workload_tag='long-tx-cache-churn',
    fault_variant='long_tx_cache_churn',
    title='Buffer hit-ratio alert caused by a long analytics cursor blocking cleanup of hot OLTP pages.',
    alert='[FIRING: WARNING] alertname=PostgresSharedBufferHitRatioLow service=order-read-api instance=postgresql-primary severity=warning\nsummary=Shared buffer hit ratio dropped while order status lookups became slower\ndescription=The memory dashboard flags cache pressure as the initial suspect while a mix of analytics and OLTP activity is present. Diagnose the actual database cause and restore order-read latency online; do not change instance configuration or restart PostgreSQL during this incident drill. Record the recurrence-control measure for the responsible workload in ops_workload_controls, and verify that maintenance cleanup of the affected tables recovers before submit. Preventive settings may be recorded only as recommendations in the final report.',
    initial_state={'status': 'degraded',
 'alert': 'shared_buffer_hit_ratio_low',
 'hot_table': 'order_status_hot_pages',
 'archive_table': 'analytics_cursor_source',
 'visible_symptom': 'cache_hit_ratio_drop_with_dead_tuple_bloat',
 'shared_buffers': '32MB',
 'fault_mechanism': 'long_transaction_blocks_vacuum_cleanup'},
    expected_target={'status': 'recovered',
 'hot_table': 'order_status_hot_pages',
 'archive_table': 'analytics_cursor_source',
 'active_reporting_scans': 0,
 'mitigation': 'limit_analytics_cursor_lifetime_and_isolate_long_snapshots',
 'root_cause': 'long_analytics_cursor_blocks_vacuum_cleanup'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=IO_SATURATION_POSTGRES_RESOURCES),
    hot_table='order_status_hot_pages',
    archive_table='analytics_cursor_source',
    control_table='ops_workload_controls',
    scan_app_name='analytics-cursor-snapshot-11',
    oltp_app_name='order-status-hot-lookup',
    customer_noise_table='analytics_cursor_customer_noise',
    inventory_noise_table='analytics_cursor_inventory_noise',
    customer_noise_app='analytics-customer-decoy',
    inventory_noise_app='analytics-inventory-decoy',
    hot_rows=10000,
    archive_rows=42000,
    customer_noise_rows=8000,
    inventory_noise_rows=8000,
    shared_buffers='32MB',
    scan_seconds=420,
    dead_tuple_threshold=6000,
    noise_profiles=(),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.5,
        reference_run_ids=(
            "reference-63__pg_cache_pollution__"
            "analytics_cursor_cache_churn__mock__r001",
        ),
    ),
)


import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import (
    PgQueryPerfFaultFingerprintProbe,
    _cancel_open_connection,
    _join_thread,
    _json_object,
    _json_response,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)

class PgQueryPerfCachePollutionInjector(BaseFaultInjector):
    """
    Simulate a memory/cache alert where mixed reporting scans evict
    OLTP pages from PostgreSQL shared buffers.
    """
    def __init__(self):
        self.env = None
        self.fault_variant = "scan_cache_pollution"
        self.hot_table = "orders_current"
        self.archive_table = "orders_audit_archive"
        self.control_table = "ops_workload_controls"
        self.scan_app_name = "svc_audit_rollup"
        self.oltp_app_name = "order_entry_probe"
        self.customer_noise_table = "customer_activity_log"
        self.inventory_noise_table = "inventory_snapshot"
        self.customer_noise_app = "customer-history-api"
        self.inventory_noise_app = "inventory-rebalance"
        self.hot_rows = 8000
        self.archive_rows = 90000
        self.customer_noise_rows = 45000
        self.inventory_noise_rows = 36000
        self.scan_seconds = 600
        self.dead_tuple_threshold = 0
        self.noise_profiles = []
        self._stop_event = None
        self._scan_thread = None
        self._oltp_thread = None
        self._long_tx_conn = None
        self._decoy_threads = []
        self._connections = []
        self._noise_runner = None

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self.quiesce(context)
        self._verify_persistent_state()
        self._start_runtime()

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print("[FaultInjector:PgQueryPerfCachePollutionInjector] Preparing cache hit-ratio scenario...")
        self.recover(context)
        self.env = env
        with env.metrics_hidden(allow_pgss_reset=True):
            self._setup_schema()
        self._start_runtime()

    def _configure(self, config, env):
        self.env = env
        self.fault_variant = str(config["fault_variant"])
        self.hot_table = _validate_sql_identifier(config["hot_table"], "hot_table")
        self.archive_table = _validate_sql_identifier(config["archive_table"], "archive_table")
        self.control_table = _validate_sql_identifier(config["control_table"], "control_table")
        self.customer_noise_table = _validate_sql_identifier(
            config["customer_noise_table"], "customer_noise_table"
        )
        self.inventory_noise_table = _validate_sql_identifier(
            config["inventory_noise_table"], "inventory_noise_table"
        )
        self.scan_app_name = config["scan_app_name"]
        self.oltp_app_name = config["oltp_app_name"]
        self.customer_noise_app = config["customer_noise_app"]
        self.inventory_noise_app = config["inventory_noise_app"]
        self.hot_rows = int(config["hot_rows"])
        self.archive_rows = int(config["archive_rows"])
        self.customer_noise_rows = int(config["customer_noise_rows"])
        self.inventory_noise_rows = int(config["inventory_noise_rows"])
        self.scan_seconds = int(config["scan_seconds"])
        self.dead_tuple_threshold = int(config["dead_tuple_threshold"])
        self.noise_profiles = list(config["noise_profiles"])

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT (SELECT count(*) FROM {self.hot_table}), "
                f"(SELECT count(*) FROM {self.archive_table}), "
                f"(SELECT count(*) FROM {self.customer_noise_table}), "
                f"(SELECT count(*) FROM {self.inventory_noise_table}), "
                f"to_regclass('public.{self.control_table}')::text;"
            ),
            "verify cache-pollution fault image",
        )
        expected = [[
            self.hot_rows,
            self.archive_rows,
            self.customer_noise_rows,
            self.inventory_noise_rows,
            self.control_table,
        ]]
        if payload["result"] != expected:
            raise RuntimeError(
                f"Cache-pollution fault image does not match the Case: "
                f"expected={expected}, observed={payload['result']}"
            )

    def _start_runtime(self):
        import threading
        import time

        self._stop_event = threading.Event()
        self._oltp_thread = threading.Thread(target=self._run_oltp_probe, daemon=True)
        self._oltp_thread.start()
        time.sleep(1.0)

        scan_target = self._run_long_tx_cursor if self.fault_variant == "long_tx_cache_churn" else self._run_reporting_scan
        self._scan_thread = threading.Thread(target=scan_target, daemon=True)
        self._scan_thread.start()
        if self.fault_variant == "long_tx_cache_churn":
            time.sleep(1.0)
            self._create_long_tx_dead_tuples()
        if self.fault_variant != "long_tx_cache_churn":
            self._start_decoy_scans()
        self._start_noise_runner()
        self._wait_until_observable(timeout_seconds=20)
        self.env.reconnect()
        print(
            "[FaultInjector:PgQueryPerfCachePollutionInjector] "
            f"Reporting scan '{self.scan_app_name}' is active against {self.archive_table}."
        )

    def _connect(self, application_name: str):
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=5,
            application_name=application_name,
        )
        conn.autocommit = True
        self._connections.append(conn)
        return conn

    def _setup_schema(self):
        self._terminate_leftover_sessions()
        self.env.execute_sql("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
        self.env.execute_sql("CREATE EXTENSION IF NOT EXISTS pg_buffercache;")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.archive_table} CASCADE;")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.hot_table} CASCADE;")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.customer_noise_table} CASCADE;")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.inventory_noise_table} CASCADE;")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.control_table} CASCADE;")
        self.env.execute_sql(f"""
            CREATE TABLE {self.hot_table} (
                order_id integer PRIMARY KEY,
                customer_id integer NOT NULL,
                district_id integer NOT NULL,
                status text NOT NULL,
                amount numeric(12, 2) NOT NULL,
                payload text NOT NULL,
                updated_at timestamptz NOT NULL DEFAULT now()
            );
        """)
        self.env.execute_sql(f"""
            CREATE TABLE {self.archive_table} (
                audit_id integer PRIMARY KEY,
                order_id integer NOT NULL,
                customer_id integer NOT NULL,
                warehouse_id integer NOT NULL,
                event_ts timestamptz NOT NULL,
                amount numeric(12, 2) NOT NULL,
                payload text NOT NULL
            );
        """)
        self.env.execute_sql(f"""
            CREATE TABLE {self.customer_noise_table} (
                event_id integer PRIMARY KEY,
                customer_id integer NOT NULL,
                event_ts timestamptz NOT NULL,
                event_type text NOT NULL,
                payload text NOT NULL
            );
        """)
        self.env.execute_sql(f"""
            CREATE TABLE {self.inventory_noise_table} (
                snapshot_id integer PRIMARY KEY,
                warehouse_id integer NOT NULL,
                item_id integer NOT NULL,
                observed_at timestamptz NOT NULL,
                quantity integer NOT NULL,
                payload text NOT NULL
            );
        """)
        # control_name legal values mirror the scan_app_name of the three cases above;
        # the CHECK keeps the key domain visible in \d for OP exact-match verification.
        self.env.execute_sql(f"""
            CREATE TABLE {self.control_table} (
                control_name text PRIMARY KEY CHECK (control_name IN (
                    'svc_audit_rollup', 'billing_export_scan', 'analytics-cursor-snapshot-11'
                )),
                recommendation text NOT NULL,
                applied_at timestamptz NOT NULL DEFAULT now()
            );
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.hot_table} (order_id, customer_id, district_id, status, amount, payload)
            SELECT
                g,
                (g % 3000) + 1,
                (g % 20) + 1,
                CASE WHEN g % 13 = 0 THEN 'PENDING' ELSE 'COMMITTED' END,
                ((g % 100000)::numeric / 100) + 1,
                repeat(md5('current-' || g::text), 16)
            FROM generate_series(1, {self.hot_rows}) AS g;
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.archive_table} (audit_id, order_id, customer_id, warehouse_id, event_ts, amount, payload)
            SELECT
                g,
                ((g - 1) % {self.hot_rows}) + 1,
                (g % 8000) + 1,
                (g % 64) + 1,
                now() - (g % 730) * interval '1 day',
                ((g % 200000)::numeric / 100) + 1,
                repeat(md5('archive-' || g::text), 16)
            FROM generate_series(1, {self.archive_rows}) AS g;
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.customer_noise_table} (event_id, customer_id, event_ts, event_type, payload)
            SELECT
                g,
                (g % 12000) + 1,
                now() - (g % 180) * interval '1 day',
                CASE WHEN g % 5 = 0 THEN 'address_check' ELSE 'order_lookup' END,
                repeat(md5('customer-noise-' || g::text), 14)
            FROM generate_series(1, {self.customer_noise_rows}) AS g;
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.inventory_noise_table} (snapshot_id, warehouse_id, item_id, observed_at, quantity, payload)
            SELECT
                g,
                (g % 64) + 1,
                (g % 40000) + 1,
                now() - (g % 30) * interval '1 hour',
                (g % 500) + 1,
                repeat(md5('inventory-noise-' || g::text), 12)
            FROM generate_series(1, {self.inventory_noise_rows}) AS g;
        """)
        self.env.execute_sql(f"CREATE INDEX idx_{self.archive_table}_customer_ts ON {self.archive_table}(customer_id, event_ts);")
        self.env.execute_sql(f"CREATE INDEX idx_{self.archive_table}_warehouse ON {self.archive_table}(warehouse_id);")
        self.env.execute_sql(f"CREATE INDEX idx_{self.customer_noise_table}_customer_ts ON {self.customer_noise_table}(customer_id, event_ts);")
        self.env.execute_sql(f"CREATE INDEX idx_{self.inventory_noise_table}_warehouse ON {self.inventory_noise_table}(warehouse_id);")
        self.env.execute_sql(f"ANALYZE {self.hot_table};")
        self.env.execute_sql(f"ANALYZE {self.archive_table};")
        self.env.execute_sql(f"ANALYZE {self.customer_noise_table};")
        self.env.execute_sql(f"ANALYZE {self.inventory_noise_table};")

        for _ in range(8):
            self.env.execute_sql(
                f"SELECT count(*), sum(length(payload)) FROM {self.hot_table} "
                f"WHERE order_id BETWEEN 1 AND {self.hot_rows};"
            )
        self.env.execute_sql("SELECT pg_stat_statements_reset();")

    def _run_reporting_scan(self):
        import time

        conn = None
        deadline = time.time() + self.scan_seconds
        try:
            conn = self._connect(self.scan_app_name)
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                cur.execute("SET work_mem = '8MB';")
                cur.execute("SET max_parallel_workers_per_gather = 0;")
                while time.time() < deadline and not self._stop_event.is_set():
                    cur.execute(f"""
                        SELECT count(*), sum(length(payload))
                        FROM (
                            SELECT payload
                            FROM {self.archive_table}
                            WHERE payload IS NOT NULL
                            ORDER BY payload
                        ) AS archive_report;
                    """)
                    cur.fetchall()
                    time.sleep(0.05)
        except Exception as exc:
            print(f"[FaultInjector:PgQueryPerfCachePollutionInjector] Reporting scan stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _run_long_tx_cursor(self):
        import time

        conn = None
        deadline = time.time() + self.scan_seconds
        try:
            conn = self._connect(self.scan_app_name)
            conn.autocommit = False
            self._long_tx_conn = conn
            with conn.cursor() as cur:
                cur.execute("BEGIN ISOLATION LEVEL REPEATABLE READ;")
                cur.execute(f"DECLARE analytics_cursor NO SCROLL CURSOR FOR SELECT * FROM {self.archive_table} ORDER BY payload;")
                cur.execute("FETCH 25 FROM analytics_cursor;")
                while time.time() < deadline and not self._stop_event.is_set():
                    cur.execute("FETCH 25 FROM analytics_cursor;")
                    cur.fetchall()
                    time.sleep(0.4)
            conn.rollback()
        except Exception as exc:
            print(f"[FaultInjector:PgQueryPerfCachePollutionInjector] Long analytics cursor stopped: {exc}")
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            self._long_tx_conn = None

    def _create_long_tx_dead_tuples(self):
        self.env.execute_sql(f"""
            UPDATE {self.hot_table}
            SET status = CASE WHEN status = 'PENDING' THEN 'COMMITTED' ELSE 'PENDING' END,
                updated_at = now(),
                payload = payload || 'x'
            WHERE order_id <= {self.hot_rows};
        """)
        self.env.execute_sql(f"VACUUM {self.hot_table};")
        self.env.execute_sql(f"ANALYZE {self.hot_table};")

    def _start_decoy_scans(self):
        import threading

        self._decoy_threads = []
        for app_name, table in (
            (self.customer_noise_app, self.customer_noise_table),
            (self.inventory_noise_app, self.inventory_noise_table),
        ):
            thread = threading.Thread(target=self._run_decoy_scan, args=(app_name, table), daemon=True)
            thread.start()
            self._decoy_threads.append(thread)

    def _run_decoy_scan(self, application_name: str, table: str):
        import time

        conn = None
        deadline = time.time() + self.scan_seconds
        try:
            conn = self._connect(application_name)
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                cur.execute("SET work_mem = '8MB';")
                cur.execute("SET max_parallel_workers_per_gather = 0;")
                while time.time() < deadline and not self._stop_event.is_set():
                    cur.execute(f"""
                        SELECT count(*), sum(length(payload))
                        FROM (
                            SELECT payload
                            FROM {table}
                            WHERE payload IS NOT NULL
                            ORDER BY payload
                        ) AS business_rollup;
                    """)
                    cur.fetchall()
                    time.sleep(0.35)
        except Exception as exc:
            print(f"[FaultInjector:PgQueryPerfCachePollutionInjector] Noise scan {application_name} stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _start_noise_runner(self):
        if not self.noise_profiles:
            return
        runner = self.create_workload_runner(self.env, self.noise_profiles, 2)
        runner.start()
        self._noise_runner = runner

    def _run_oltp_probe(self):
        import random
        import time

        conn = None
        try:
            conn = self._connect(self.oltp_app_name)
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '3s';")
                while self._stop_event is not None and not self._stop_event.is_set():
                    low = random.randint(1, max(1, self.hot_rows - 200))
                    high = min(self.hot_rows, low + 199)
                    cur.execute(
                        f"SELECT sum(amount), sum(length(payload)) FROM {self.hot_table} "
                        "WHERE order_id BETWEEN %s AND %s;",
                        (low, high),
                    )
                    cur.fetchall()
                    time.sleep(0.05)
        except Exception as exc:
            print(f"[FaultInjector:PgQueryPerfCachePollutionInjector] OLTP probe stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _wait_until_observable(self, timeout_seconds: int = 20):
        import json
        import time

        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            if self.fault_variant == "long_tx_cache_churn":
                state = self.env.execute_sql(f"""
                    SELECT
                        count(*) FILTER (
                            WHERE application_name = '{self.scan_app_name}'
                              AND state = 'idle in transaction'
                              AND backend_xmin IS NOT NULL
                        ) AS long_tx_sessions,
                        COALESCE((
                            SELECT n_dead_tup
                            FROM pg_stat_user_tables
                            WHERE relname = '{self.hot_table}'
                        ), 0) AS dead_tuples
                    FROM pg_stat_activity
                    WHERE datname = current_database();
                """)
                row = _json_object(state, "read long-tx cache-churn visibility")["result"][0]
                if int(row[0] or 0) > 0 and int(row[1] or 0) >= self.dead_tuple_threshold:
                    return
                time.sleep(1.0)
                continue
            state = self.env.execute_sql(f"""
                SELECT
                    count(*) FILTER (
                        WHERE application_name = '{self.scan_app_name}' AND state = 'active'
                    ) AS scan_sessions,
                    coalesce((
                        SELECT count(*)
                        FROM pg_buffercache b
                        JOIN pg_class c ON b.relfilenode = pg_relation_filenode(c.oid)
                        WHERE c.relname = '{self.archive_table}'
                    ), 0) AS archive_buffers
                FROM pg_stat_activity
                WHERE datname = current_database();
            """)
            row = _json_object(state, "read cache-pollution visibility")["result"][0]
            if int(row[0] or 0) > 0 and int(row[1] or 0) > 0:
                return
            time.sleep(1.0)
        raise RuntimeError(
            f"Cache-pollution fault did not become observable within {timeout_seconds} seconds"
        )

    def _terminate_leftover_sessions(self):
        escaped_scan = self.scan_app_name.replace("'", "''")
        escaped_oltp = self.oltp_app_name.replace("'", "''")
        escaped_customer_noise = self.customer_noise_app.replace("'", "''")
        escaped_inventory_noise = self.inventory_noise_app.replace("'", "''")
        _require_sql_success(
            self.env.execute_sql(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE application_name IN (
                    '{escaped_scan}', '{escaped_oltp}',
                    '{escaped_customer_noise}', '{escaped_inventory_noise}',
                    'order-entry-api', 'aiopsbench_workload_runner',
                    'analytics-cursor-snapshot-11', 'order-status-hot-lookup'
                )
                  AND pid <> pg_backend_pid();
            """),
            "terminate cache-pollution sessions",
        )

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        cache_hit_ratio = env.query_metrics("cache_hit_ratio")

        if self.fault_variant == "long_tx_cache_churn":
            sessions = env.execute_sql(
                "SET statement_timeout = '5s'; "
                "SELECT pid, application_name, state, backend_xmin, xact_start, "
                "now() - xact_start AS xact_age, left(query, 180) AS query "
                "FROM pg_stat_activity WHERE datname = current_database() "
                f"AND application_name IN ('{self.scan_app_name}', '{self.oltp_app_name}') "
                "ORDER BY application_name, xact_start NULLS LAST;"
            )
        else:
            sessions = env.execute_sql(
                "SET statement_timeout = '5s'; "
                "SELECT pid, application_name, state, wait_event_type, "
                "now() - query_start AS duration, left(query, 180) AS query "
                "FROM pg_stat_activity WHERE datname = current_database() "
                f"AND application_name IN ('{self.scan_app_name}', '{self.oltp_app_name}') "
                "ORDER BY application_name, query_start NULLS LAST;"
            )
        buffers = env.execute_sql(
            "CREATE EXTENSION IF NOT EXISTS pg_buffercache; "
            "SELECT c.relname, count(*) AS buffers, "
            "round(count(*) * 8 / 1024.0, 2) AS mb "
            "FROM pg_buffercache b "
            "JOIN pg_class c ON b.relfilenode = pg_relation_filenode(c.oid) "
            f"WHERE c.relname IN ('{self.hot_table}', '{self.archive_table}') "
            "GROUP BY c.relname ORDER BY buffers DESC;"
        )
        session_rows = _json_object(sessions, "cache-pollution sessions")["result"]
        if not any(row[1] == self.scan_app_name for row in session_rows):
            raise RuntimeError(
                f"Cache-pollution scan session {self.scan_app_name!r} is not visible: {sessions}"
            )
        if self.fault_variant == "long_tx_cache_churn":
            dead_tuples = env.execute_sql(
                "SELECT relname, n_dead_tup, last_autovacuum, last_vacuum "
                "FROM pg_stat_user_tables "
                f"WHERE relname = '{self.hot_table}';"
            )
            dead_rows = _json_object(dead_tuples, "long-transaction dead tuples")["result"]
            if not dead_rows or int(dead_rows[0][1] or 0) < self.dead_tuple_threshold:
                raise RuntimeError(
                    f"Long-transaction cache churn dead tuples are not visible: {dead_tuples}"
                )
            return {
                "cache_hit_ratio": cache_hit_ratio,
                "sessions": sessions,
                "buffers": buffers,
                "dead_tuples": dead_tuples,
            }
        buffer_rows = _json_object(buffers, "cache-pollution buffers")["result"]
        if not any(row[0] == self.archive_table and int(row[1]) > 0 for row in buffer_rows):
            raise RuntimeError(
                f"Cache-pollution archive buffers for {self.archive_table!r} are not visible: {buffers}"
            )
        return {
            "cache_hit_ratio": cache_hit_ratio,
            "sessions": sessions,
            "buffers": buffers,
        }

    def quiesce(self, context: FaultLifecycleContext):
        self._stop_runtime(context)

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        self.env = context.env
        if self._noise_runner is not None:
            self._noise_runner.stop()
            self._noise_runner = None
        if self._stop_event is not None:
            self._stop_event.set()
        self._terminate_leftover_sessions()
        threads = (self._scan_thread, self._oltp_thread, *self._decoy_threads)
        steps = [
            (f"close cache-pollution connection {index}", conn.close)
            for index, conn in enumerate(self._connections)
            if not conn.closed
        ]
        steps.extend(
            (
                f"join cache-pollution thread {index}",
                lambda thread=thread, index=index: _join_thread(
                    thread,
                    5,
                    f"cache-pollution thread {index}",
                ),
            )
            for index, thread in enumerate(threads)
            if thread is not None
        )
        _run_cleanup_steps(
            f"Cache-pollution cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._connections = []
        self._long_tx_conn = None
        self._scan_thread = None
        self._oltp_thread = None
        self._decoy_threads = []
        self._stop_event = None

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        print("[FaultInjector:PgQueryPerfCachePollutionInjector] Recovering cache hit-ratio fault...")
        self._stop_runtime(context)
        if not self.env.reconnect():
            raise RuntimeError(
                f"Cache-pollution recovery could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        for table in (
            self.archive_table,
            self.hot_table,
            self.customer_noise_table,
            self.inventory_noise_table,
            self.control_table,
        ):
            _validate_sql_identifier(table, "table")
            _require_sql_success(
                self.env.execute_sql(f"DROP TABLE IF EXISTS {table} CASCADE;"),
                f"drop cache-pollution table {table}",
            )
class PgQueryPerfCachePollutionScenario(PostgresScenario):
    scenario_id = 'pg_query_perf_cache_pollution'
    description = 'Shared buffer hit-ratio alert caused by a mixed reporting scan evicting OLTP pages.'
    cases = (
        _PGQUERYPERFCACHEPOLLUTIONSCENARIO_CASE,
        _PGQUERYPERFCACHEPOLLUTIONSCENARIO_BILLING_EXPORT_CASE,
        _PGQUERYPERFCACHEPOLLUTIONSCENARIO_ANALYTICS_CURSOR_CASE,
    )

    def build_fault_plan(self, case: PgQueryPerfCachePollutionCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgQueryPerfCachePollutionInjector,
                config={
                    'hot_table': case.hot_table,
                    'fault_variant': case.fault_variant,
                    'archive_table': case.archive_table,
                    'control_table': case.control_table,
                    'scan_app_name': case.scan_app_name,
                    'oltp_app_name': case.oltp_app_name,
                    'customer_noise_table': case.customer_noise_table,
                    'inventory_noise_table': case.inventory_noise_table,
                    'customer_noise_app': case.customer_noise_app,
                    'inventory_noise_app': case.inventory_noise_app,
                    'hot_rows': case.hot_rows,
                    'archive_rows': case.archive_rows,
                    'customer_noise_rows': case.customer_noise_rows,
                    'inventory_noise_rows': case.inventory_noise_rows,
                    'scan_seconds': case.scan_seconds,
                    'dead_tuple_threshold': case.dead_tuple_threshold,
                    'noise_profiles': case.noise_profiles,
                },
            ),
        )
