from dataclasses import dataclass
from typing import List, Mapping

from src.scenarios.evaluation.postgres.resource_governance import (
    PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase,
    PgResourceGovernanceAuditLoggingForOrdersWriteAuditScopeSimpleEvaluatorCase,
    PgResourceGovernanceDataArchivingForOrderHistoryColdArchiveEvaluatorCase,
    PgResourceGovernancePrivilegeMaskingForCustomerDeveloperMaskingEvaluatorCase,
    PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.workloads.specs import WorkloadProfile

from src.execution.specs import PostgresCaseRuntime, CaseResourceSpec, PostgresRuntimeSpec
from src.scenarios.base import PostgresScenario, DifficultyCalibration, FaultPlan, PostgresScenarioCase
from src.workloads.specs import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    EMPTY_BACKGROUND_WORKLOAD,
)


RESOURCE_GOVERNANCE_POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceAuditLoggingCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    table: str
    audit_role: str
    worker_count: int
    slow_queries: tuple[str, ...]

@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingScenarioCase(PgResourceGovernanceAuditLoggingCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernanceAuditLoggingForOrdersWriteAuditScopeSimpleScenarioCase(PgResourceGovernanceAuditLoggingCase):
    pass

def build_audit_logging_noise_profiles(
    table: str = "audit_orders",
) -> List[WorkloadProfile]:
    """Business-shaped noise for the audit logging scenario.

    The real fault remains broad statement/audit logging. These profiles add
    plausible checkout, reporting, temp-spill, and log-noise candidates so the
    agent cannot rely on a single topsql row to identify the root cause.
    """
    return [
        WorkloadProfile(
            name="checkout_status_rollup",
            sql=(
                "SELECT status, count(*) AS orders, "
                "coalesce(sum(amount), 0) AS gross_amount "
                f"FROM {table} "
                "WHERE customer_id BETWEEN 50 AND 2500 "
                "GROUP BY status "
                "ORDER BY gross_amount DESC"
            ),
            qps=0.24,
            tier="MEDIUM",
            application_name="checkout-dashboard-refresh",
        ),
        WorkloadProfile(
            name="payment_reconciliation_preview",
            sql=(
                "SET LOCAL work_mem = '64kB'; "
                "SELECT customer_id, status, count(*) AS orders, "
                "coalesce(sum(amount), 0) AS gross_amount "
                f"FROM {table} "
                "GROUP BY customer_id, status "
                "ORDER BY gross_amount DESC, customer_id "
                "LIMIT 250"
            ),
            qps=0.18,
            tier="TEMP_SPILL",
            application_name="payment-reconcile-preview",
        ),
        WorkloadProfile(
            name="checkout_live_touch_probe",
            sql=(
                f"UPDATE {table} "
                "SET amount = amount "
                "WHERE id = 17"
            ),
            qps=0.32,
            tier="LIGHT",
            commit=False,
            application_name="checkout-api-live-touch",
        ),
        WorkloadProfile(
            name="receipt_latency_probe",
            sql=(
                "SELECT pg_sleep(1.4), count(*) AS pending_receipts "
                f"FROM {table} "
                "WHERE status = 'REVIEW'"
            ),
            qps=0.16,
            tier="SLOW_NOISE",
            application_name="receipt-latency-probe",
        ),
        WorkloadProfile(
            name="missing_compliance_cache_log_noise",
            sql="SELECT count(*) FROM compliance_receipt_cache_missing;",
            qps=0.12,
            tier="LOG_NOISE",
            application_name="compliance-cache-refresh",
        ),
    ]

_PGRESOURCEGOVERNANCEAUDITLOGGINGSCENARIO_CASE = PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingScenarioCase(
    case_id='audit_orders_role_logging',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "statement logging overload",
                    "entity": "audit_orders_role_logging",
                    "evidence": [
                        "scripted diagnostic actions observed statement logging overload"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "sensitive writes ddl and role changes need audit",
                    "entity": "audit_orders_role_logging",
                    "evidence": [
                        "scripted diagnostic actions observed sensitive writes ddl and role changes need audit"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "log_statement all is too broad",
                    "entity": "audit_orders_role_logging",
                    "evidence": [
                        "scripted diagnostic actions observed log_statement all is too broad"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "configure scoped pgaudit role",
                    "entity": "audit_orders_role_logging",
                    "evidence": [
                        "scripted diagnostic actions observed configure scoped pgaudit role"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "verify business throughput after audit change",
                    "entity": "audit_orders_role_logging",
                    "evidence": [
                        "scripted diagnostic actions observed verify business throughput after audit change"
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
    evaluator=PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates excessive audit logging that amplifies disk writes under a high-QPS OLTP workload.',
    alert='P1 production alert: after a compliance logging rollout, checkout transaction throughput dropped by more than half and disk write bandwidth is near saturation. WAL volume and table bloat do not explain the write amplification. Identify the logging source and restore transaction throughput without disabling required compliance coverage.',
    initial_state={'status': 'degraded',
 'disk_write_amplification': 'audit_logging',
 'audit_scope': 'all_statements',
 'transaction_throughput': 'low'},
    expected_target={'status': 'recovered',
 'audit_scope': 'scoped_sensitive_activity',
 'statement_logging': 'not_all',
 'transaction_throughput': 'recovered'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_audit_logging_noise_profiles('audit_orders')),
        worker_count=2,
        seed=0,
        warmup_seconds=4,
    ),
    runtime=PostgresCaseRuntime(
        parameters=PostgresRuntimeSpec(parameters=(
            ("shared_preload_libraries", "pg_stat_statements"),
        )),
        resources=RESOURCE_GOVERNANCE_POSTGRES_RESOURCES,
    ),
    table='audit_orders',
    audit_role='compliance_audit_role',
    worker_count=3,
    slow_queries=('SELECT amount FROM audit_orders WHERE id = 42;',),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.3,
        reference_run_ids=(
            "reference-52__pg_resource_governance_audit_logging__"
            "audit_orders_role_logging__mock__r001",
        ),
    ),
)

_PGRESOURCEGOVERNANCEAUDITLOGGING_SIMPLE_CASE = PgResourceGovernanceAuditLoggingForOrdersWriteAuditScopeSimpleScenarioCase(
    case_id='orders_write_audit_scope_simple',
    case_no=1,
    evaluator=PgResourceGovernanceAuditLoggingForOrdersWriteAuditScopeSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='A focused audit logging case with one checkout table and one compliance role.',
    alert='P2 compliance rollout alert: checkout write throughput dropped after audit logging was enabled. Disk writes are elevated, but WAL and table growth do not explain the spike. Keep required write/DDL/role audit coverage while restoring transaction throughput.',
    initial_state={'status': 'degraded', 'disk_write_amplification': 'audit_logging', 'audit_scope': 'all_statements'},
    expected_target={'status': 'recovered', 'audit_scope': 'scoped_sensitive_activity', 'statement_logging': 'not_all'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_audit_logging_noise_profiles('audit_orders_simple')[:1]),
        worker_count=1,
        seed=0x5103,
        warmup_seconds=2,
    ),
    runtime=PostgresCaseRuntime(
        parameters=PostgresRuntimeSpec(parameters=(("shared_preload_libraries", "pg_stat_statements"),)),
        resources=RESOURCE_GOVERNANCE_POSTGRES_RESOURCES,
    ),
    table='audit_orders_simple',
    audit_role='compliance_audit_role_simple',
    worker_count=1,
    slow_queries=('SELECT amount FROM audit_orders_simple WHERE id = 42;',),
    reference_report=_PGRESOURCEGOVERNANCEAUDITLOGGINGSCENARIO_CASE.reference_report,
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.285714,
        reference_run_ids=('run_pg_resource_governance_audit_logging_orders_write_audit_scope_simple_MockLLMAgent',),
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

class PgResourceGovernanceAuditLoggingInjector(BaseFaultInjector):
    """
    模拟全量审计/语句日志导致的高并发日志写入放大。
    业务线程只执行高频点查，数据页和 WAL 压力很小；写 I/O 主要来自
    log_statement=all 与 pgaudit.log=all 暴露的审计策略。
    """

    def __init__(self):
        self._stop_event = None
        self._workers = []
        self._worker_conns = []

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print(
            "[FaultInjector:PgResourceGovernanceAuditLoggingInjector] "
            "Preparing high-frequency workload with full audit logging..."
        )
        with env.metrics_hidden(allow_pgss_reset=True):
            self._setup_table_and_role()
            self._register_custom_guc("pgaudit.log")
            self._register_custom_guc("pgaudit.role")
            self._set_config("pgaudit.log", "all")
            self._set_config("pgaudit.role", self.audit_role)
            self._set_config("log_statement", "all")
            self._set_config("log_min_duration_statement", "-1")
            _require_sql_success(
                env.execute_sql("SELECT pg_reload_conf();"),
                "reload audit-logging settings",
            )
            self._reset_session_custom_guc("pgaudit.log")
            self._reset_session_custom_guc("pgaudit.role")
            # The custom pgaudit GUCs were registered in this setup session.
            # Verify the post-reload values through the same fresh-connection
            # boundary used by workload workers and the Agent.
            env.reconnect()
            self._verify_persistent_state()
            self._scrub_agent_visible_history()
        self._start_runtime()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config["table"], "table")
        self.audit_role = _validate_sql_identifier(
            config["audit_role"],
            "audit_role",
        )
        self.worker_count = int(config["worker_count"])

    def _start_runtime(self) -> None:
        import threading
        import time

        self._stop_event = threading.Event()
        self._workers = [
            threading.Thread(target=self._run_checkout_workload, args=(idx,), daemon=True)
            for idx in range(self.worker_count)
        ]
        for worker in self._workers:
            worker.start()
        time.sleep(4.0)
        self.fault_log_growth_bytes_per_sec = self._measure_log_growth(seconds=2.0)
        self.env.reconnect()

    def _setup_table_and_role(self):
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table} CASCADE;")
        self.env.execute_sql(f"DROP ROLE IF EXISTS {self.audit_role};")
        self.env.execute_sql(f"CREATE ROLE {self.audit_role};")
        self.env.execute_sql(f"""
            CREATE TABLE {self.table} (
                id integer PRIMARY KEY,
                customer_id integer NOT NULL,
                amount numeric(12, 2) NOT NULL,
                status text NOT NULL,
                updated_at timestamptz NOT NULL DEFAULT now()
            );
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.table} (id, customer_id, amount, status)
            SELECT
                g,
                (g % 3000) + 1,
                ((g % 10000)::numeric / 100) + 1,
                CASE WHEN g % 11 = 0 THEN 'REVIEW' ELSE 'PAID' END
            FROM generate_series(1, 30000) AS g;
        """)
        self.env.execute_sql(f"GRANT SELECT ON {self.table} TO {self.audit_role};")
        self.env.execute_sql(f"ANALYZE {self.table};")

    def _set_config(self, param: str, value: str):
        result = self.env.execute_sql(f"ALTER SYSTEM SET {param} = '{value}';")
        _require_sql_success(result, f"set audit-logging config {param}={value}")

    def _register_custom_guc(self, param: str):
        result = self.env.execute_sql(f"SET {param} = 'none';")
        _require_sql_success(result, f"register audit-logging custom GUC {param}")

    def _reset_session_custom_guc(self, param: str):
        result = self.env.execute_sql(f"RESET {param};")
        _require_sql_success(result, f"reset audit-logging session GUC {param}")

    def _reset_config(self, param: str):
        result = self.env.execute_sql(f"ALTER SYSTEM RESET {param};")
        _require_sql_success(result, f"reset audit-logging config {param}")

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{self.table}')::text, "
                f"EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{self.audit_role}'), "
                f"(SELECT count(*) FROM {self.table}), "
                "current_setting('pgaudit.log'), current_setting('pgaudit.role'), "
                "current_setting('log_statement'), current_setting('log_min_duration_statement');"
            ),
            "verify audit-logging fault image",
        )
        expected = [[self.table, True, 30000, "all", self.audit_role, "all", "-1"]]
        if payload["result"] != expected:
            raise RuntimeError(
                f"Audit-logging fault image does not match the Case: "
                f"expected={expected}, observed={payload['result']}"
            )

    def _scrub_pg_stat_statements(self):
        _require_sql_success(
            self.env.execute_sql(
                "SET pg_stat_statements.track = 'none'; "
                "SELECT pg_stat_statements_reset(); "
                "RESET pg_stat_statements.track;"
            ),
            "reset pg_stat_statements after audit-logging injection",
        )

    def _scrub_agent_visible_history(self):
        self._scrub_pg_stat_statements()
        self.env.refresh_pgss_baseline()

    def _run_checkout_workload(self, worker_id: int):
        import psycopg2
        import time

        conn = None
        try:
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.dbname,
                application_name="checkout_api",
                connect_timeout=5,
            )
            conn.autocommit = True
            self._worker_conns.append(conn)
            i = worker_id
            with conn.cursor() as cur:
                while self._stop_event is not None and not self._stop_event.is_set():
                    i = (i + self.worker_count) % 30000
                    cur.execute(f"SELECT amount FROM {self.table} WHERE id = %s;", (i + 1,))
                    time.sleep(0.002)
        except Exception as exc:
            if self._stop_event is not None and not self._stop_event.is_set():
                print(f"[FaultInjector:PgResourceGovernanceAuditLoggingInjector] checkout workload stopped: {exc}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _measure_log_growth(self, seconds: float = 2.0) -> float:
        import time

        before = self._log_size()
        time.sleep(seconds)
        after = self._log_size()
        if after < before:
            raise RuntimeError(
                f"PostgreSQL audit log shrank during measurement: before={before}, after={after}"
            )
        return (after - before) / seconds

    def _log_size(self):
        payload = _json_object(
            self.env.execute_sql(
                "SELECT (pg_stat_file('/var/log/postgresql/postgresql.log')).size;"
            ),
            "read PostgreSQL audit log size",
        )
        return int(payload["result"][0][0])

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {
            "fault_log_growth_bytes_per_sec": self.fault_log_growth_bytes_per_sec,
            "active_sessions": env.execute_sql(
                "SELECT pid, application_name, state, left(query, 120) "
                "FROM pg_stat_activity WHERE application_name = 'checkout_api' "
                "ORDER BY pid;"
            ),
            "audit_settings": env.execute_sql(
                "SELECT name, setting, source FROM pg_settings "
                "WHERE name IN ('pgaudit.log', 'pgaudit.role', 'log_statement', "
                "'log_min_duration_statement') ORDER BY name;"
            ),
            "disk_io": env.query_metrics("disk_io"),
        }

    def quiesce(self, context: FaultLifecycleContext):
        """Clean up background audit worker threads for teardown."""
        print("[FaultInjector:PgResourceGovernanceAuditLoggingInjector] quiesce...")
        if self._stop_event:
            self._stop_event.set()
        steps = [
            (f"close worker connection {index}", conn.close)
            for index, conn in enumerate(self._worker_conns)
        ]
        steps.extend(
            (
                f"join audit worker {index}",
                lambda worker=worker, index=index: _join_thread(
                    worker,
                    5,
                    f"audit logging worker {index}",
                ),
            )
            for index, worker in enumerate(self._workers)
        )
        _run_cleanup_steps(
            f"Audit-logging cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._workers = []
        self._worker_conns = []
        self._stop_event = None

    def recover(self, context: FaultLifecycleContext):
        self.quiesce(context)
        print("[FaultInjector:PgResourceGovernanceAuditLoggingInjector] Recovering audit logging artifacts...")
        _require_sql_success(
            self.env.execute_sql(
                "SELECT pg_terminate_backend(pid) "
                "FROM pg_stat_activity "
                "WHERE application_name = 'checkout_api';"
            ),
            "terminate audit-logging workers",
        )
        for param in (
            "log_statement",
            "log_min_duration_statement",
            "pgaudit.log",
            "pgaudit.role",
        ):
            self._reset_config(param)
        _require_sql_success(
            self.env.execute_sql("SELECT pg_reload_conf();"),
            "reload recovered audit-logging settings",
        )
        _require_sql_success(
            self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table} CASCADE;"),
            f"drop audit-logging table {self.table}",
        )
        _require_sql_success(
            self.env.execute_sql(f"DROP ROLE IF EXISTS {self.audit_role};"),
            f"drop audit-logging role {self.audit_role}",
        )
        self.env.reconnect()

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden(allow_pgss_reset=True):
            self._verify_persistent_state()
            self._scrub_agent_visible_history()
        self._start_runtime()
        print("[FaultInjector:PgResourceGovernanceAuditLoggingInjector] Audit workload re-activated.")


class PgResourceGovernanceAuditLoggingScenario(PostgresScenario):
    scenario_id = 'pg_resource_governance_audit_logging'
    description = 'Simulates excessive audit logging that amplifies disk writes under a high-QPS OLTP workload.'
    cases = (_PGRESOURCEGOVERNANCEAUDITLOGGINGSCENARIO_CASE, _PGRESOURCEGOVERNANCEAUDITLOGGING_SIMPLE_CASE)

    def build_fault_plan(self, case: PgResourceGovernanceAuditLoggingCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgResourceGovernanceAuditLoggingInjector,
                config={
                    'table': case.table,
                    'audit_role': case.audit_role,
                    'worker_count': case.worker_count,
                },
            ),
        )
