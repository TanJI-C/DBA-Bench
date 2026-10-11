from dataclasses import dataclass
from typing import List, Mapping

from src.scenarios.evaluation.postgres.resource_governance import (
    PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase,
    PgResourceGovernanceDataArchivingForOrderHistoryColdArchiveEvaluatorCase,
    PgResourceGovernanceDataArchivingForOrderHistoryQuarterArchiveSimpleEvaluatorCase,
    PgResourceGovernancePrivilegeMaskingForCustomerDeveloperMaskingEvaluatorCase,
    PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    PostgresCaseRuntime,
    PostgresScenario,
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    CaseResourceSpec,
    PostgresRuntimeSpec,
    PostgresScenarioCase,
)


RESOURCE_GOVERNANCE_POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceDataArchivingCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    table: str
    archive_table: str
    cold_rows: int
    hot_rows: int
    slow_queries: tuple[str, ...]
    live_sentinel_rows: int
    payload_repeat: int

@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceDataArchivingForOrderHistoryColdArchiveScenarioCase(PgResourceGovernanceDataArchivingCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceDataArchivingForOrderHistoryQuarterArchiveSimpleScenarioCase(PgResourceGovernanceDataArchivingCase):
    pass

def build_data_archiving_noise_profiles(
    table: str = "order_history",
    archive_table: str = "order_history_archive",
) -> List[WorkloadProfile]:
    """Business-shaped noise for the data archiving / space reclaim scenario.

    The profile names intentionally sound like normal reporting and retention
    work. They should make slow_queries, topsql, active connections, and
    workload_activity contain plausible but non-root-cause candidates.
    """
    return [
        WorkloadProfile(
            name="order_retention_dashboard_rollup",
            sql=(
                "SELECT status, date_trunc('month', order_ts) AS order_month, "
                "count(*) AS orders, coalesce(sum(amount), 0) AS gross_amount "
                f"FROM {table} "
                "WHERE order_ts > now() - interval '18 months' "
                "GROUP BY status, order_month "
                "ORDER BY order_month DESC, gross_amount DESC "
                "LIMIT 48"
            ),
            qps=0.25,
            tier="MEDIUM",
        ),
        WorkloadProfile(
            name="customer_history_payload_rollup",
            sql=(
                "SELECT customer_id, count(*) AS orders, sum(length(payload)) AS payload_bytes "
                f"FROM {table} "
                "GROUP BY customer_id "
                "ORDER BY payload_bytes DESC, customer_id "
                "LIMIT 100"
            ),
            qps=0.20,
            tier="MEDIUM",
        ),
        WorkloadProfile(
            name="recent_order_touch_probe",
            sql=(
                f"UPDATE {table} "
                "SET amount = amount "
                f"WHERE id = (SELECT max(id) FROM {table} WHERE order_ts >= now() - interval '90 days')"
            ),
            qps=0.35,
            tier="LIGHT",
            commit=False,
            application_name="orders-api-live-touch",
        ),
        WorkloadProfile(
            name="archive_table_existence_probe",
            sql=(
                "SELECT to_regclass('public."
                f"{archive_table}"
                "') AS archive_relation, count(*) AS known_tables "
                "FROM pg_class WHERE relkind = 'r'"
            ),
            qps=0.18,
            tier="LIGHT",
        ),
        WorkloadProfile(
            name="missing_retention_summary_log_noise",
            sql="SELECT count(*) FROM retention_summary_cache_missing;",
            qps=0.10,
            tier="LOG_NOISE",
        ),
    ]

_PGRESOURCEGOVERNANCEDATAARCHIVINGSCENARIO_CASE = PgResourceGovernanceDataArchivingForOrderHistoryColdArchiveScenarioCase(
    case_id='order_history_cold_archive',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "cold order history identified",
                    "entity": "order_history_cold_archive",
                    "evidence": [
                        "scripted diagnostic actions observed cold order history identified"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "cold rows consume live table space",
                    "entity": "order_history_cold_archive",
                    "evidence": [
                        "scripted diagnostic actions observed cold rows consume live table space"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "copy swap rewrite avoids vacuum full",
                    "entity": "order_history_cold_archive",
                    "evidence": [
                        "scripted diagnostic actions observed copy swap rewrite avoids vacuum full"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "archive manifest and live sentinels",
                    "entity": "order_history_cold_archive",
                    "evidence": [
                        "scripted diagnostic actions observed archive manifest and live sentinels"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "archive cold rows and swap compact table",
                    "entity": "order_history_cold_archive",
                    "evidence": [
                        "scripted diagnostic actions observed archive cold rows and swap compact table"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "archived cold rows and swapped the compact live table"
            ],
            "verification": [
                "table swap reclaimed space without VACUUM FULL"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgResourceGovernanceDataArchivingForOrderHistoryColdArchiveEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates cold order-history archiving and physical space reclaim under online workload constraints.',
    alert='P1 存储容量告警：PostgreSQL 单机实例数据目录使用率持续高于 80%，order_history 表占用增长明显且冷数据比例异常。业务仍在线写入，当前没有停机窗口，禁止使用会长时间持有 ACCESS EXCLUSIVE 锁的回收方式。请归档一年以前冷数据并回收物理空间，同时避免阻塞核心交易。',
    alert_en="P1 storage capacity alert: data directory usage of the standalone PostgreSQL instance stays above 80%, the space used by the order_history table is growing noticeably, and the proportion of cold data is abnormal. The business is still writing online, there is no downtime window, and reclamation methods that hold an ACCESS EXCLUSIVE lock for a long time are forbidden. Archive the cold data older than one year and reclaim the physical space, while avoiding blocking core transactions.",
    initial_state={'status': 'storage_warning', 'cold_data': 'present', 'physical_space': 'not_reclaimed'},
    expected_target={'status': 'recovered',
 'cold_data': 'archived',
 'physical_space': 'reclaimed',
 'strategy': 'non_blocking_rewrite'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_data_archiving_noise_profiles('order_history', 'order_history_archive')),
        worker_count=2,
        seed=0,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=3,
    ),
    runtime=PostgresCaseRuntime(resources=RESOURCE_GOVERNANCE_POSTGRES_RESOURCES),
    table='order_history',
    archive_table='order_history_archive',
    cold_rows=18000,
    hot_rows=2000,
    slow_queries=("SELECT count(*), pg_size_pretty(pg_total_relation_size('order_history')) FROM order_history "
 "WHERE order_ts < NOW() - INTERVAL '1 year';",),
    live_sentinel_rows=20,
    payload_repeat=80,
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.444444,
        reference_run_ids=(
            "reference-51__pg_resource_governance_data_archiving__"
            "order_history_cold_archive__mock__r001",
        ),
    ),
)

_PGRESOURCEGOVERNANCEDATAARCHIVING_SIMPLE_CASE = PgResourceGovernanceDataArchivingForOrderHistoryQuarterArchiveSimpleScenarioCase(
    case_id='order_history_quarter_archive_simple',
    case_no=1,
    evaluator=PgResourceGovernanceDataArchivingForOrderHistoryQuarterArchiveSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='A smaller cold order-history archive with one live sentinel stream and one decoy read profile.',
    alert='P2 storage governance alert: order_history_q1 has a compact set of one-year-old rows consuming live-table space while checkout writes continue. Archive the cold slice and reclaim physical space without long ACCESS EXCLUSIVE maintenance or VACUUM FULL.',
    initial_state={'status': 'storage_warning', 'cold_data': 'present', 'physical_space': 'not_reclaimed'},
    expected_target={'status': 'recovered', 'cold_data': 'archived', 'physical_space': 'reclaimed', 'strategy': 'non_blocking_rewrite'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_data_archiving_noise_profiles('order_history_q1', 'order_history_q1_archive')[:1]),
        worker_count=1,
        seed=0x5101,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=2,
    ),
    runtime=PostgresCaseRuntime(resources=RESOURCE_GOVERNANCE_POSTGRES_RESOURCES),
    table='order_history_q1',
    archive_table='order_history_q1_archive',
    cold_rows=4000,
    hot_rows=900,
    slow_queries=("SELECT count(*), pg_size_pretty(pg_total_relation_size('order_history_q1')) FROM order_history_q1 WHERE order_ts < NOW() - INTERVAL '1 year';",),
    live_sentinel_rows=8,
    payload_repeat=32,
    reference_report=_PGRESOURCEGOVERNANCEDATAARCHIVINGSCENARIO_CASE.reference_report,
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.285714,
        reference_run_ids=('run_pg_resource_governance_data_archiving_order_history_quarter_archive_simple_MockLLMAgent',),
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

class PgResourceGovernanceDataArchivingInjector(BaseFaultInjector):
    """
    模拟历史数据归档与物理空间回收场景。
    构造一个包含大量一年以前冷数据的订单历史表，使 Agent 必须选择
    新表重构/切换等低阻塞策略，而不是直接 DELETE 或 VACUUM FULL。
    """

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._install(env)

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config["table"], "table")
        self.archive_table = _validate_sql_identifier(
            config["archive_table"], "archive_table"
        )
        self.cold_rows = int(config["cold_rows"])
        self.hot_rows = int(config["hot_rows"])
        self.live_sentinel_rows = int(config["live_sentinel_rows"])
        self.payload_repeat = int(config["payload_repeat"])
        self.baseline_table = f"{self.table}_reclaim_baseline"
        self.live_sequence = f"{self.table}_live_seq"

    def _install(self, env) -> None:
        print(
            "[FaultInjector:PgResourceGovernanceDataArchivingInjector] "
            f"Preparing {self.table} with {self.cold_rows} cold rows and {self.hot_rows} hot rows..."
        )
        self._cleanup()

        env.execute_sql(f"""
            CREATE TABLE {self.table} (
                id BIGINT PRIMARY KEY,
                order_ts TIMESTAMP NOT NULL,
                customer_id INTEGER NOT NULL,
                amount NUMERIC(12, 2) NOT NULL,
                status TEXT NOT NULL,
                payload TEXT NOT NULL
            );
        """)
        env.execute_sql(f"ALTER TABLE {self.table} SET (autovacuum_enabled = false);")
        env.execute_sql(f"""
            INSERT INTO {self.table} (id, order_ts, customer_id, amount, status, payload)
            SELECT
                g,
                NOW() - INTERVAL '18 months' - (g % 30) * INTERVAL '1 day',
                (g % 5000) + 1,
                ((g % 10000)::numeric / 100) + 1,
                'ARCHIVE_READY',
                repeat(md5(g::text), {self.payload_repeat})
            FROM generate_series(1, {self.cold_rows}) AS g;
        """)
        env.execute_sql(f"""
            INSERT INTO {self.table} (id, order_ts, customer_id, amount, status, payload)
            SELECT
                {self.cold_rows} + g,
                NOW() - (g % 60) * INTERVAL '1 day',
                (g % 5000) + 1,
                ((g % 10000)::numeric / 100) + 1,
                'HOT',
                repeat(md5(({self.cold_rows} + g)::text), {self.payload_repeat})
            FROM generate_series(1, {self.hot_rows}) AS g;
        """)
        env.execute_sql(f"""
            INSERT INTO {self.table} (id, order_ts, customer_id, amount, status, payload)
            SELECT
                {self.cold_rows + self.hot_rows} + g,
                NOW() - (g % 5) * INTERVAL '1 minute',
                900000 + g,
                1.00,
                'LIVE_SENTINEL',
                repeat(md5(('live-sentinel-' || g)::text), {self.payload_repeat})
            FROM generate_series(1, {self.live_sentinel_rows}) AS g;
        """)
        env.execute_sql(f"CREATE INDEX idx_{self.table}_order_ts ON {self.table}(order_ts);")
        env.execute_sql(f"ANALYZE {self.table};")
        env.execute_sql(f"CREATE SEQUENCE {self.live_sequence} START WITH {self.cold_rows + self.hot_rows + self.live_sentinel_rows + 1};")
        env.execute_sql(f"""
            CREATE TABLE {self.baseline_table} AS
            SELECT
                count(*) FILTER (WHERE order_ts < NOW() - INTERVAL '1 year')::bigint AS cold_rows,
                coalesce(sum(id) FILTER (WHERE order_ts < NOW() - INTERVAL '1 year'), 0)::bigint AS cold_id_sum,
                count(*) FILTER (WHERE status = 'LIVE_SENTINEL')::bigint AS live_sentinel_rows
            FROM {self.table};
        """)
        env.reconnect()

    def _cleanup(self):
        for suffix in ("_new", "_old"):
            self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table}{suffix} CASCADE;")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table}_reclaim_baseline CASCADE;")
        self.env.execute_sql(f"DROP SEQUENCE IF EXISTS {self.table}_live_seq CASCADE;")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.archive_table}_manifest CASCADE;")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.archive_table} CASCADE;")
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table} CASCADE;")

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {
            "table_state": env.execute_sql(
                f"SELECT count(*) AS total_rows, "
                f"count(*) FILTER (WHERE order_ts < NOW() - INTERVAL '1 year') AS cold_rows, "
                f"pg_size_pretty(pg_total_relation_size('{self.table}')) AS total_size "
                f"FROM {self.table};"
            ),
            "disk_usage": env.query_metrics("disk_usage", self.table),
        }

    def quiesce(self, context: FaultLifecycleContext):
        """No background threads or runtime resources to clean up."""
        pass

    def recover(self, context: FaultLifecycleContext):
        print("[FaultInjector:PgResourceGovernanceDataArchivingInjector] Recovering archive scenario artifacts...")
        self._cleanup()
        self.env.reconnect()

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._verify_persistent_state()

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT count(*) FILTER (WHERE order_ts < NOW() - INTERVAL '1 year'), "
                f"count(*) FILTER (WHERE status = 'HOT'), "
                f"count(*) FILTER (WHERE status = 'LIVE_SENTINEL'), "
                f"to_regclass('public.{self.baseline_table}')::text, "
                f"to_regclass('public.{self.live_sequence}')::text "
                f"FROM {self.table};"
            ),
            "verify data-archiving fault image",
        )
        observed = payload["result"][0]
        expected = [
            self.cold_rows,
            self.hot_rows,
            self.live_sentinel_rows,
            self.baseline_table,
            self.live_sequence,
        ]
        if observed != expected:
            raise RuntimeError(
                f"Data-archiving fault image does not match the Case: "
                f"expected={expected}, observed={observed}"
            )


class PgResourceGovernanceDataArchivingScenario(PostgresScenario):
    scenario_id = 'pg_resource_governance_data_archiving'
    description = 'Simulates cold order-history archiving and physical space reclaim under online workload constraints.'
    cases = (_PGRESOURCEGOVERNANCEDATAARCHIVINGSCENARIO_CASE, _PGRESOURCEGOVERNANCEDATAARCHIVING_SIMPLE_CASE)

    def build_fault_plan(self, case: PgResourceGovernanceDataArchivingCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgResourceGovernanceDataArchivingInjector,
                config={
                    'table': case.table,
                    'archive_table': case.archive_table,
                    'cold_rows': case.cold_rows,
                    'hot_rows': case.hot_rows,
                    'live_sentinel_rows': case.live_sentinel_rows,
                    'payload_repeat': case.payload_repeat,
                },
            ),
        )
