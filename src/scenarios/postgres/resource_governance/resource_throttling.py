from dataclasses import dataclass
from typing import List, Mapping

from src.scenarios.evaluation.postgres.resource_governance import (
    PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase,
    PgResourceGovernanceDataArchivingForOrderHistoryColdArchiveEvaluatorCase,
    PgResourceGovernancePrivilegeMaskingForCustomerDeveloperMaskingEvaluatorCase,
    PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingEvaluatorCase,
    PgResourceGovernanceResourceThrottlingForSingleReportRoleLimitSimpleEvaluatorCase,
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
class PgResourceGovernanceResourceThrottlingCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    oltp_role: str
    report_role: str
    table: str
    root_application_name: str
    noise_roles: tuple[str, ...]
    role_password: str
    slow_queries: tuple[str, ...]
    report_role_connection_limit_max: int
    report_role_work_mem_max_mb: int
    oltp_probe_latency_ms: int

@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingScenarioCase(PgResourceGovernanceResourceThrottlingCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceResourceThrottlingForSingleReportRoleLimitSimpleScenarioCase(PgResourceGovernanceResourceThrottlingCase):
    pass

def build_resource_throttling_noise_profiles(
    table: str = "tenant_orders",
) -> List[WorkloadProfile]:
    """Business-shaped noise for the mixed workload resource throttling scenario.

    These profiles intentionally create plausible reporting, export, and OLTP
    activity around the same table as the fault. They should make slow queries,
    topsql, pg_stat_activity, and workload_activity contain multiple candidates
    without changing the real root cause: the unbounded report role.
    """
    return [
        WorkloadProfile(
            name="tenant_dashboard_rollup",
            sql=(
                "SELECT tenant_id, status, count(*) AS orders, "
                "coalesce(sum(amount), 0) AS gross_amount "
                f"FROM {table} "
                "WHERE created_at > now() - interval '7 days' "
                "GROUP BY tenant_id, status "
                "ORDER BY gross_amount DESC, tenant_id "
                "LIMIT 40"
            ),
            qps=0.22,
            tier="MEDIUM",
            application_name="bi-dashboard-refresh",
        ),
        WorkloadProfile(
            name="customer_segment_export_preview",
            sql=(
                "SELECT customer_id, count(*) AS order_count, "
                "sum(length(payload)) AS payload_bytes "
                f"FROM {table} "
                "WHERE status = 'PAID' "
                "GROUP BY customer_id "
                "ORDER BY payload_bytes DESC, customer_id "
                "LIMIT 120"
            ),
            qps=0.28,
            tier="MEDIUM",
            application_name="tenant-revenue-export-preview",
        ),
        WorkloadProfile(
            name="etl_ledger_backfill_probe",
            sql=(
                "SELECT tenant_id, date_trunc('hour', created_at) AS hour_bucket, "
                "count(*) AS rows_seen, coalesce(avg(amount), 0) AS avg_amount "
                f"FROM {table} "
                "WHERE created_at > now() - interval '3 days' "
                "GROUP BY tenant_id, hour_bucket "
                "ORDER BY hour_bucket DESC, tenant_id "
                "LIMIT 96"
            ),
            qps=0.24,
            tier="MEDIUM",
            application_name="etl-ledger-backfill",
        ),
        WorkloadProfile(
            name="order_api_point_probe",
            sql=(
                f"UPDATE {table} "
                "SET amount = amount "
                f"WHERE id = (SELECT max(id) FROM {table} WHERE tenant_id BETWEEN 1 AND 4)"
            ),
            qps=0.35,
            tier="LIGHT",
            commit=False,
            application_name="orders-api-live-touch",
        ),
        WorkloadProfile(
            name="missing_report_cache_log_noise",
            sql="SELECT count(*) FROM tenant_report_cache_missing;",
            qps=0.10,
            tier="LOG_NOISE",
            application_name="report-cache-refresher",
        ),
    ]

_PGRESOURCEGOVERNANCERESOURCETHROTTLINGSCENARIO_CASE = PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingScenarioCase(
    case_id='tenant_report_role_throttling',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "report tenant degrades oltp latency",
                    "entity": "tenant_report_role_throttling",
                    "evidence": [
                        "scripted diagnostic actions observed report tenant degrades oltp latency"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "report user export is culprit",
                    "entity": "tenant_report_role_throttling",
                    "evidence": [
                        "scripted diagnostic actions observed report user export is culprit"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "report role has no resource guardrails",
                    "entity": "tenant_report_role_throttling",
                    "evidence": [
                        "scripted diagnostic actions observed report role has no resource guardrails"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "applied the case-specific remediation"
            ],
            "verification": [
                "verified the case-specific final state"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates mixed OLTP and reporting workload contention and requires role-level resource isolation.',
    alert='P1 混合业务资源告警：PostgreSQL 单机实例 CPU 使用率持续偏高，核心交易接口 P95 延迟从毫秒级升高到秒级，QPS 明显下降。同实例活跃会话数量上升且存在长耗时 SQL，请排查资源占用来源，在不重启实例且符合安全合规要求的前提下恢复核心交易延迟，并降低复发风险。',
    alert_en="P1 mixed-workload resource alert: CPU usage of the standalone PostgreSQL instance stays high, the P95 latency of core transaction APIs has risen from milliseconds to seconds, and QPS has dropped noticeably. The number of active sessions on the same instance is rising and there are long-running SQL statements. Investigate the source of the resource usage, restore core transaction latency without restarting the instance and in compliance with security and compliance requirements, and reduce the risk of recurrence.",
    initial_state={'status': 'degraded',
 'resource_contention': 'reporting_query_consuming_cpu',
 'transaction_latency': 'high'},
    expected_target={'status': 'recovered',
 'resource_isolation': 'role_limits_applied',
 'report_query': 'terminated_or_throttled',
 'transaction_latency': 'normal'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_resource_throttling_noise_profiles('tenant_orders')),
        worker_count=2,
        seed=0,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=4,
    ),
    runtime=PostgresCaseRuntime(resources=RESOURCE_GOVERNANCE_POSTGRES_RESOURCES),
    oltp_role='oltp_user',
    report_role='report_user',
    table='tenant_orders',
    root_application_name='tenant-revenue-export',
    noise_roles=('analytics_user', 'etl_user'),
    role_password='password',
    slow_queries=('SELECT amount FROM tenant_orders WHERE id = 42;',),
    report_role_connection_limit_max=2,
    report_role_work_mem_max_mb=4,
    oltp_probe_latency_ms=1000,
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.291667,
        reference_run_ids=(
            "reference-51__pg_resource_governance_resource_throttling__"
            "tenant_report_role_throttling__mock__r001",
        ),
    ),
)

_PGRESOURCEGOVERNANCERESOURCETHROTTLING_SIMPLE_CASE = PgResourceGovernanceResourceThrottlingForSingleReportRoleLimitSimpleScenarioCase(
    case_id='single_report_role_limit_simple',
    case_no=1,
    evaluator=PgResourceGovernanceResourceThrottlingForSingleReportRoleLimitSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='A focused resource isolation case with one report role, one OLTP role, and one nearby analytics decoy.',
    alert='P2 mixed workload alert: checkout point reads on the shared PostgreSQL instance have slowed from millisecond latency to several hundred milliseconds while instance CPU usage stays elevated and the number of active sessions keeps growing. Investigate the source of the resource usage, restore core transaction latency without restarting the instance, and reduce the risk of recurrence.',
    initial_state={'status': 'degraded', 'resource_contention': 'reporting_query_consuming_cpu', 'transaction_latency': 'high'},
    expected_target={'status': 'recovered', 'resource_isolation': 'role_limits_applied', 'report_query': 'terminated_or_throttled', 'transaction_latency': 'normal'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_resource_throttling_noise_profiles('tenant_orders_simple')[:4]),
        worker_count=4,
        seed=0x5102,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=2,
    ),
    runtime=PostgresCaseRuntime(resources=RESOURCE_GOVERNANCE_POSTGRES_RESOURCES),
    oltp_role='oltp_simple_user',
    report_role='report_simple_user',
    table='tenant_orders_simple',
    root_application_name='tenant-simple-export',
    noise_roles=('analytics_simple_user',),
    role_password='password',
    slow_queries=('SELECT amount FROM tenant_orders_simple WHERE id = 42;',),
    report_role_connection_limit_max=2,
    report_role_work_mem_max_mb=4,
    oltp_probe_latency_ms=1000,
    reference_report=_PGRESOURCEGOVERNANCERESOURCETHROTTLINGSCENARIO_CASE.reference_report,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.6,
        reference_run_ids=('run_pg_resource_governance_resource_throttling_single_report_role_limit_simple_MockLLMAgent',),
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

class PgResourceGovernanceResourceThrottlingInjector(BaseFaultInjector):
    """
    模拟多租户混合业务资源争抢。
    创建交易账号和只读报表账号，后台以报表账号运行长时间 CPU/内存消耗查询，
    使 Agent 可通过 pg_stat_activity 识别分析任务并通过角色级限制隔离。
    """

    def __init__(self):
        self._report_thread = None
        self._maintenance_thread = None
        self._stop_event = None
        self._report_conn = None
        self._maintenance_conn = None
        self.root_application_name = "tenant-revenue-export"
        self.noise_roles = ("analytics_user", "etl_user")

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print(
            "[FaultInjector:PgResourceGovernanceResourceThrottlingInjector] "
            f"Preparing mixed workload roles {self.oltp_role}/{self.report_role}..."
        )
        with env.metrics_hidden():
            self._setup_roles_and_data()
            self._set_admin_statement_timeout()
        self._start_runtime()

    def _configure(self, config, env):
        self.env = env
        self.oltp_role = config["oltp_role"]
        self.report_role = config["report_role"]
        self.table = config["table"]
        self.root_application_name = config["root_application_name"]
        self.noise_roles = tuple(config["noise_roles"])
        self.role_password = str(config["role_password"]).replace("'", "''")
        for identifier in (self.oltp_role, self.report_role, self.table, *self.noise_roles):
            if not identifier.isidentifier():
                raise ValueError(f"Invalid resource-throttling identifier: {identifier!r}")

    def _start_runtime(self):
        import threading
        import time

        self._stop_event = threading.Event()
        self._report_thread = threading.Thread(target=self._run_report_query, daemon=True)
        self._report_thread.start()
        self._maintenance_thread = threading.Thread(target=self._run_maintenance_decoy, daemon=True)
        self._maintenance_thread.start()
        time.sleep(2.0)
        self.env.reconnect()

    def _run_maintenance_decoy(self):
        """Recurring same-table maintenance job on the analytics role.

        Business-grounded nightly-style maintenance: repeated bounded ANALYZE and
        aggregation sweeps that look heavy in pg_stat_activity/topsql but are
        short-lived and waiting-free compared with the unbounded report export.
        The agent must distinguish the sustained runaway export from this decoy.
        """
        import psycopg2
        import time

        conn = None
        try:
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.noise_roles[0],
                password=self.role_password,
                dbname=self.env.dbname,
                application_name="analytics-nightly-maintenance",
                connect_timeout=5,
            )
            conn.autocommit = True
            self._maintenance_conn = conn
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '5s';")
                while self._stop_event is not None and not self._stop_event.is_set():
                    cur.execute(
                        f"SELECT tenant_id, count(*), sum(hashtext(payload)) "
                        f"FROM {self.table} "
                        "WHERE created_at > NOW() - INTERVAL '30 days' "
                        "GROUP BY tenant_id;"
                    )
                    time.sleep(0.2)
        except Exception as exc:
            if self._stop_event is not None and not self._stop_event.is_set():
                print(f"[FaultInjector:PgResourceGovernanceResourceThrottlingInjector] Maintenance decoy stopped: {exc}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            self._maintenance_conn = None

    def _verify_persistent_state(self) -> None:
        noise_role_checks = ", ".join(
            f"EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}')"
            for role in self.noise_roles
        )
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{self.table}')::text, "
                f"(SELECT count(*) FROM {self.table}), "
                f"EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{self.oltp_role}'), "
                f"EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{self.report_role}'), "
                f"{noise_role_checks};"
            ),
            "verify resource-throttling fault image",
        )
        expected = [[self.table, 60000, True, True, *([True] * len(self.noise_roles))]]
        if payload["result"] != expected:
            raise RuntimeError(
                f"Resource-throttling fault image does not match the Case: "
                f"expected={expected}, observed={payload['result']}"
            )

    def _setup_roles_and_data(self):
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table} CASCADE;")
        self.env.execute_sql(f"DROP ROLE IF EXISTS {self.oltp_role};")
        self.env.execute_sql(f"DROP ROLE IF EXISTS {self.report_role};")
        for role in self.noise_roles:
            self.env.execute_sql(f"DROP ROLE IF EXISTS {role};")
        self.env.execute_sql(f"CREATE ROLE {self.oltp_role} LOGIN PASSWORD '{self.role_password}';")
        self.env.execute_sql(f"CREATE ROLE {self.report_role} LOGIN PASSWORD '{self.role_password}';")
        for role in self.noise_roles:
            self.env.execute_sql(f"CREATE ROLE {role} LOGIN PASSWORD '{self.role_password}';")
        self.env.execute_sql(f"ALTER ROLE {self.report_role} RESET work_mem;")
        self.env.execute_sql(f"ALTER ROLE {self.report_role} CONNECTION LIMIT -1;")
        self.env.execute_sql(f"""
            CREATE TABLE {self.table} (
                id integer PRIMARY KEY,
                tenant_id integer NOT NULL,
                customer_id integer NOT NULL,
                amount numeric(12, 2) NOT NULL,
                status text NOT NULL,
                created_at timestamptz NOT NULL DEFAULT now(),
                payload text NOT NULL
            );
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.table} (id, tenant_id, customer_id, amount, status, created_at, payload)
            SELECT
                g,
                (g % 16) + 1,
                (g % 5000) + 1,
                ((g % 10000)::numeric / 100) + 1,
                CASE WHEN g % 7 = 0 THEN 'PENDING' ELSE 'PAID' END,
                NOW() - (g % 30) * INTERVAL '1 minute',
                repeat(md5(g::text), 8)
            FROM generate_series(1, 60000) AS g;
        """)
        self.env.execute_sql(f"CREATE INDEX idx_{self.table}_tenant_created ON {self.table}(tenant_id, created_at);")
        self.env.execute_sql(f"GRANT SELECT, UPDATE ON {self.table} TO {self.oltp_role};")
        self.env.execute_sql(f"GRANT SELECT ON {self.table} TO {self.report_role};")
        for role in getattr(self, "noise_roles", ()):
            self.env.execute_sql(f"GRANT SELECT ON {self.table} TO {role};")
        self.env.execute_sql(f"ANALYZE {self.table};")

    def _run_report_query(self):
        import psycopg2

        conn = None
        try:
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.report_role,
                password=self.role_password,
                dbname=self.env.dbname,
                application_name=self.root_application_name,
                connect_timeout=5,
            )
            conn.autocommit = True
            self._report_conn = conn
            with conn.cursor() as cur:
                cur.execute("SET work_mem = '64MB';")
                cur.execute("SET statement_timeout = '0';")
                cur.execute(f"""
                    SELECT sum((a.amount * b.amount)::numeric)
                    FROM {self.table} a
                    JOIN {self.table} b ON (a.tenant_id = b.tenant_id)
                    JOIN generate_series(1, {1000 if self.table.endswith('_simple') else 250}) g ON true
                    WHERE a.status IN ('PAID', 'PENDING')
                      AND a.created_at > NOW() - INTERVAL '30 days';
                """)
        except Exception as exc:
            if self._stop_event is not None and not self._stop_event.is_set():
                print(f"[FaultInjector:PgResourceGovernanceResourceThrottlingInjector] Report query stopped: {exc}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            self._report_conn = None

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        noise_apps = ("'bi-dashboard-refresh'", "'tenant-revenue-export-preview'", "'etl-ledger-backfill'", "'orders-api-live-touch'", "'analytics-nightly-maintenance'")
        return {
            "active_sessions": env.execute_sql(
                "SELECT pid, usename, application_name, state, left(query, 120) "
                "FROM pg_stat_activity "
                f"WHERE usename IN ('{self.oltp_role}', '{self.report_role}') "
                f"OR application_name = '{self.root_application_name}' "
                f"OR application_name IN ({', '.join(noise_apps)}) "
                "ORDER BY query_start NULLS LAST;"
            ),
            "transaction_probe": env.execute_sql(
                f"SELECT amount FROM {self.table} WHERE id = 42;"
            ),
            "cpu": env.query_metrics("cpu"),
            "qps": env.query_metrics("qps"),
        }

    def _set_admin_statement_timeout(self) -> None:
        _require_sql_success(
            self.env.execute_sql(
                "ALTER ROLE postgres SET statement_timeout = '30s'; "
                "SET statement_timeout = '30s';"
            ),
            "set resource-throttling administrator statement timeout",
        )

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        if self._stop_event:
            self._stop_event.set()
        _require_sql_success(
            context.env.execute_sql(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE usename = '{self.report_role}'
                   OR application_name = '{self.root_application_name}';
            """),
            "terminate resource-throttling report sessions",
        )
        steps = []
        if self._report_conn is not None:
            steps.append(("close report connection", self._report_conn.close))
        if self._report_thread is not None:
            steps.append((
                "join report thread",
                lambda: _join_thread(
                    self._report_thread,
                    5,
                    "resource-throttling report thread",
                ),
            ))
        if self._maintenance_conn is not None:
            steps.append(("close maintenance decoy connection", self._maintenance_conn.close))
        if self._maintenance_thread is not None:
            steps.append((
                "join maintenance decoy thread",
                lambda: _join_thread(
                    self._maintenance_thread,
                    5,
                    "resource-throttling maintenance decoy thread",
                ),
            ))
        _run_cleanup_steps(
            f"Resource-throttling cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._report_thread = None
        self._report_conn = None
        self._maintenance_thread = None
        self._maintenance_conn = None
        self._stop_event = None

    def quiesce(self, context: FaultLifecycleContext):
        """Clean up background report query thread for teardown."""
        print("[FaultInjector:PgResourceGovernanceResourceThrottlingInjector] quiesce...")
        self._stop_runtime(context)

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        self._stop_runtime(context)
        print("[FaultInjector:PgResourceGovernanceResourceThrottlingInjector] Recovering resource throttling artifacts...")
        if not context.env.reconnect():
            raise RuntimeError(
                f"Resource-throttling recovery could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        _require_sql_success(
            context.env.execute_sql(
                "ALTER ROLE postgres RESET statement_timeout; RESET statement_timeout;"
            ),
            "reset resource-throttling administrator statement timeout",
        )
        statements = [
            f"DROP TABLE IF EXISTS {self.table} CASCADE;",
            f"DROP ROLE IF EXISTS {self.oltp_role};",
            f"DROP ROLE IF EXISTS {self.report_role};",
            *(f"DROP ROLE IF EXISTS {role};" for role in self.noise_roles),
        ]
        for statement in statements:
            _require_sql_success(
                context.env.execute_sql(statement),
                f"recover resource-throttling artifact with {statement}",
            )

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._verify_persistent_state()
            self._set_admin_statement_timeout()
        self._start_runtime()
        print("[FaultInjector:PgResourceGovernanceResourceThrottlingInjector] Report query re-activated.")


class PgResourceGovernanceResourceThrottlingScenario(PostgresScenario):
    scenario_id = 'pg_resource_governance_resource_throttling'
    description = 'Simulates mixed OLTP and reporting workload contention and requires role-level resource isolation.'
    cases = (_PGRESOURCEGOVERNANCERESOURCETHROTTLINGSCENARIO_CASE, _PGRESOURCEGOVERNANCERESOURCETHROTTLING_SIMPLE_CASE)

    def build_fault_plan(self, case: PgResourceGovernanceResourceThrottlingCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgResourceGovernanceResourceThrottlingInjector,
                config={
                    'oltp_role': case.oltp_role,
                    'report_role': case.report_role,
                    'table': case.table,
                    'root_application_name': case.root_application_name,
                    'noise_roles': case.noise_roles,
                    'role_password': case.role_password,
                },
            ),
        )
