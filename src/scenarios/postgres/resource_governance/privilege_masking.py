from dataclasses import dataclass
from typing import List, Mapping

from src.scenarios.evaluation.postgres.resource_governance import (
    PgResourceGovernanceAuditLoggingForAuditOrdersRoleLoggingEvaluatorCase,
    PgResourceGovernanceDataArchivingForOrderHistoryColdArchiveEvaluatorCase,
    PgResourceGovernancePrivilegeMaskingForCustomerDeveloperMaskingEvaluatorCase,
    PgResourceGovernancePrivilegeMaskingForCustomerSupportMaskingSimpleEvaluatorCase,
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
class PgResourceGovernancePrivilegeMaskingCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    table: str
    dev_role: str
    app_role: str
    view_schema: str
    inherited_role: str
    decoy_role: str
    decoy_inherited_role: str
    policy_table: str
    role_password: str
    slow_queries: tuple[str, ...]
    contractor_role: str | None = None
    default_acl_recurrence: bool = False

@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernancePrivilegeMaskingForCustomerDeveloperMaskingScenarioCase(PgResourceGovernancePrivilegeMaskingCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgResourceGovernancePrivilegeMaskingForCustomerSupportMaskingSimpleScenarioCase(PgResourceGovernancePrivilegeMaskingCase):
    pass

def build_privilege_masking_noise_profiles(
    table: str = "customer",
) -> List[WorkloadProfile]:
    """Business-shaped noise for privilege convergence / masking.

    The profiles are intentionally adjacent to the security alert but not the
    root cause itself: export previews, policy cache probes, and missing-cache
    errors make topsql/workload_activity less single-signal while the real fix
    remains inherited base-table privilege removal plus a valid masked view.
    """
    return [
        WorkloadProfile(
            name="customer_export_preview_rollup",
            sql=(
                "SELECT account_status, count(*) AS customers, "
                "min(customer_id) AS first_customer, max(customer_id) AS last_customer "
                f"FROM {table} "
                "GROUP BY account_status "
                "ORDER BY customers DESC, account_status"
            ),
            qps=0.24,
            tier="LIGHT",
            application_name="customer-export-preview",
        ),
        WorkloadProfile(
            name="masked_preview_latency_probe",
            sql=(
                "SELECT pg_sleep(0.9), count(*) AS review_customers "
                f"FROM {table} "
                "WHERE account_status = 'REVIEW'"
            ),
            qps=0.14,
            tier="SLOW_NOISE",
            application_name="masked-preview-latency-probe",
        ),
        WorkloadProfile(
            name="customer_contact_quality_scan",
            sql=(
                "SELECT substring(email from position('@' in email) + 1) AS domain, "
                "count(*) AS n "
                f"FROM {table} "
                "GROUP BY domain "
                "ORDER BY n DESC, domain "
                "LIMIT 20"
            ),
            qps=0.18,
            tier="LIGHT",
            application_name="contact-quality-scan",
        ),
        WorkloadProfile(
            name="policy_cache_refresh_probe",
            sql="SELECT count(*) FROM access_policy_cache_missing;",
            qps=0.10,
            tier="LOG_NOISE",
            application_name="policy-cache-refresh",
        ),
        WorkloadProfile(
            name="dev_preview_touch_probe",
            sql=(
                f"UPDATE {table} "
                "SET account_status = account_status "
                "WHERE customer_id = 3"
            ),
            qps=0.28,
            tier="LIGHT",
            commit=False,
            application_name="dev-preview-touch",
        ),
        WorkloadProfile(
            name="analytics_access_review_probe",
            sql=(
                "SELECT r.rolname, r.rolcanlogin, "
                "has_table_privilege(r.rolname, 'public." + table + "', 'SELECT') "
                "FROM pg_roles r WHERE r.rolname IN ('analytics_user', 'app_user') "
                "ORDER BY r.rolname"
            ),
            qps=0.12,
            tier="LOG_NOISE",
            application_name="analytics-access-review",
        ),
    ]

_PGRESOURCEGOVERNANCEPRIVILEGEMASKINGSCENARIO_CASE = PgResourceGovernancePrivilegeMaskingForCustomerDeveloperMaskingScenarioCase(
    case_id='customer_developer_masking',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "developer inherits base customer access",
                    "entity": "customer_developer_masking",
                    "evidence": [
                        "scripted diagnostic actions observed developer inherits base customer access"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "developer requires masked customer fields",
                    "entity": "customer_developer_masking",
                    "evidence": [
                        "scripted diagnostic actions observed developer requires masked customer fields"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "application role keeps base access",
                    "entity": "customer_developer_masking",
                    "evidence": [
                        "scripted diagnostic actions observed application role keeps base access"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "revoke base and grant masked view",
                    "entity": "customer_developer_masking",
                    "evidence": [
                        "scripted diagnostic actions observed revoke base and grant masked view"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "verify developer and application separately",
                    "entity": "customer_developer_masking",
                    "evidence": [
                        "scripted diagnostic actions observed verify developer and application separately"
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
    evaluator=PgResourceGovernancePrivilegeMaskingForCustomerDeveloperMaskingEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates an over-privileged non-production account that can read customer sensitive columns in clear text.',
    alert='P1 security audit alert: a non-production database account appears to have access to clear-text customer sensitive data in a production-like PostgreSQL instance. Reconcile the database-maintained customer access policy with live effective privileges, restore compliant access for the affected role, and keep approved production and fraud-review reads working.',
    initial_state={'status': 'security_exposure',
 'base_table_privilege': 'inherited_over_grant',
 'sensitive_columns': ('id_number', 'phone_number'),
 'masking_path': 'partial_preview_only'},
    expected_target={'status': 'remediated',
 'base_table_privilege': 'revoked_from_non_privileged_account',
 'masking_path': 'view_granted',
 'application_reads': 'available'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_privilege_masking_noise_profiles('customer')),
        worker_count=2,
        seed=0,
        warmup_seconds=4,
    ),
    runtime=PostgresCaseRuntime(resources=RESOURCE_GOVERNANCE_POSTGRES_RESOURCES),
    table='customer',
    dev_role='test_dev_user',
    app_role='app_user',
    view_schema='dev_access',
    inherited_role='qa_readonly_group',
    decoy_role='analytics_user',
    decoy_inherited_role='analytics_readonly_group',
    policy_table='customer_access_policy',
    role_password='password',
    slow_queries=('SELECT customer_id, full_name, phone_number, id_number FROM customer LIMIT 5;',),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.5,
        reference_run_ids=('run_pg_resource_governance_privilege_masking_customer_developer_masking_MockLLMAgent',),
    ),
)

_PGRESOURCEGOVERNANCEPRIVILEGEMASKING_SIMPLE_CASE = PgResourceGovernancePrivilegeMaskingForCustomerSupportMaskingSimpleScenarioCase(
    case_id='customer_support_masking_simple',
    case_no=1,
    evaluator=PgResourceGovernancePrivilegeMaskingForCustomerSupportMaskingSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='A support sandbox access review covering customer lookup behavior and production continuity.',
    alert='P2 security review alert: customer-support lookup behavior in a sandbox no longer matches the approved access policy. Review the account and object boundaries, preserve the production application path, and restore the approved support workflow without changing unrelated data.',
    initial_state={'status': 'security_exposure', 'base_table_privilege': 'inherited_over_grant', 'masking_path': 'missing'},
    expected_target={'status': 'remediated', 'base_table_privilege': 'revoked_from_non_privileged_account', 'masking_path': 'complete_masked_view', 'application_reads': 'available'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_privilege_masking_noise_profiles('customer_support')),
        worker_count=2,
        seed=0x5104,
        warmup_seconds=4,
    ),
    runtime=PostgresCaseRuntime(resources=RESOURCE_GOVERNANCE_POSTGRES_RESOURCES),
    table='customer_support',
    dev_role='support_dev_user',
    app_role='support_app_user',
    view_schema='support_access',
    inherited_role='support_readonly_group',
    decoy_role='support_analytics_user',
    decoy_inherited_role='support_analyst_group',
    policy_table='support_access_policy',
    contractor_role='support_contractor_user',
    default_acl_recurrence=True,
    role_password='password',
    slow_queries=('SELECT customer_id, full_name, phone_number, id_number FROM customer_support LIMIT 5;',),
    reference_report=_PGRESOURCEGOVERNANCEPRIVILEGEMASKINGSCENARIO_CASE.reference_report,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.5,
        reference_run_ids=('run_pg_resource_governance_privilege_masking_customer_support_masking_simple_MockLLMAgent',),
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

class PgResourceGovernancePrivilegeMaskingInjector(BaseFaultInjector):
    """
    模拟非特权账号对客户敏感列的过宽直接访问。
    故障态中 test/dev 账号拥有 public.customer 的 SELECT 权限，能够读取
    身份证号和手机号明文；修复应改为通过脱敏视图访问。
    """

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print(
            "[FaultInjector:PgResourceGovernancePrivilegeMaskingInjector] "
            "Preparing customer access exposure..."
        )

        with env.metrics_hidden(allow_pgss_reset=True):
            self._setup_roles_and_customer_data()
            self._verify_persistent_state()
            self._scrub_pg_stat_statements()
        env.reconnect()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config["table"], "table")
        self.dev_role = _validate_sql_identifier(config["dev_role"], "dev_role")
        self.app_role = _validate_sql_identifier(config["app_role"], "app_role")
        self.view_schema = _validate_sql_identifier(config["view_schema"], "view_schema")
        self.inherited_role = _validate_sql_identifier(
            config["inherited_role"],
            "inherited_role",
        )
        self.decoy_role = _validate_sql_identifier(config["decoy_role"], "decoy_role")
        self.decoy_inherited_role = _validate_sql_identifier(config["decoy_inherited_role"], "decoy_inherited_role")
        self.policy_table = _validate_sql_identifier(config["policy_table"], "policy_table")
        self.role_password = config["role_password"]
        self.contractor_role = (
            _validate_sql_identifier(config["contractor_role"], "contractor_role")
            if config.get("contractor_role")
            else None
        )
        self.default_acl_recurrence = bool(config.get("default_acl_recurrence"))

    def _setup_roles_and_customer_data(self):
        statements = [
            (
                f"CREATE ROLE {self.dev_role} LOGIN PASSWORD '{self.role_password}';",
                f"create privilege-masking role {self.dev_role}",
            ),
            (
                f"CREATE ROLE {self.app_role} LOGIN PASSWORD '{self.role_password}';",
                f"create privilege-masking role {self.app_role}",
            ),
            (
                f"CREATE ROLE {self.inherited_role} NOLOGIN;",
                f"create privilege-masking role {self.inherited_role}",
            ),
            (f"CREATE ROLE {self.decoy_role} LOGIN PASSWORD '{self.role_password}';", f"create healthy near-neighbor role {self.decoy_role}"),
            (f"CREATE ROLE {self.decoy_inherited_role} NOLOGIN;", f"create healthy near-neighbor group {self.decoy_inherited_role}"),
        ]
        if self.contractor_role:
            statements.append((
                f"CREATE ROLE {self.contractor_role} LOGIN PASSWORD '{self.role_password}';",
                f"create privilege-masking contractor role {self.contractor_role}",
            ))
        statements.extend([
            (
                f"""
                CREATE TABLE public.{self.table} (
                    customer_id integer PRIMARY KEY,
                    full_name text NOT NULL,
                    phone_number text NOT NULL,
                    id_number text NOT NULL,
                    email text NOT NULL,
                    account_status text NOT NULL DEFAULT 'ACTIVE'
                );
                """,
                f"create privilege-masking table public.{self.table}",
            ),
            (
                f"""
                INSERT INTO public.{self.table}
                    (customer_id, full_name, phone_number, id_number, email, account_status)
                VALUES
                    (1, 'Alice Chen', '13812345678', '110101199001011234', 'alice.chen@example.com', 'ACTIVE'),
                    (2, 'Brian Li', '13987654321', '310101198512124321', 'brian.li@example.com', 'ACTIVE'),
                    (3, 'Carla Wang', '13700001111', '440101199903039999', 'carla.wang@example.com', 'REVIEW');
                """,
                "insert privilege-masking seed customers",
            ),
            (
                f"""
                INSERT INTO public.{self.table}
                    (customer_id, full_name, phone_number, id_number, email, account_status)
                SELECT
                    g,
                    'Customer ' || g::text,
                    '13' || lpad((800000000 + g)::text, 9, '0'),
                    (110101199000000000::bigint + g)::text,
                    'customer' || g::text || '@example.com',
                    CASE WHEN g % 17 = 0 THEN 'REVIEW' ELSE 'ACTIVE' END
                FROM generate_series(4, 500) AS g;
                """,
                "insert privilege-masking generated customers",
            ),
            (
                f"GRANT USAGE ON SCHEMA public TO {self.dev_role}, {self.app_role}, {self.inherited_role};",
                "grant public schema usage for privilege-masking roles",
            ),
            (
                f"GRANT SELECT ON public.{self.table} TO {self.inherited_role};",
                f"grant inherited SELECT on public.{self.table}",
            ),
            (
                f"GRANT {self.inherited_role} TO {self.dev_role};",
                f"grant role {self.inherited_role} to {self.dev_role}",
            ),
            (
                f"GRANT SELECT ON public.{self.table} TO {self.app_role};",
                f"grant application SELECT on public.{self.table}",
            ),
            (f"GRANT USAGE ON SCHEMA public TO {self.decoy_role}, {self.decoy_inherited_role};", "grant healthy near-neighbor schema usage"),
            (f"GRANT SELECT ON public.{self.table} TO {self.decoy_inherited_role};", "grant healthy near-neighbor table access"),
            (f"GRANT {self.decoy_inherited_role} TO {self.decoy_role};", "grant healthy near-neighbor membership"),
            (
                f"""
                CREATE TABLE public.{self.policy_table} (
                    principal_role text PRIMARY KEY,
                    business_purpose text NOT NULL,
                    base_customer_read_allowed boolean NOT NULL,
                    sensitive_field_policy text NOT NULL CHECK (
                        sensitive_field_policy IN ('cleartext', 'masked_last4', 'aggregate_only')
                    ),
                    approval_state text NOT NULL CHECK (approval_state IN ('approved', 'review_required'))
                );
                """,
                "create customer access policy registry",
            ),
            (
                f"""
                INSERT INTO public.{self.policy_table}
                    (principal_role, business_purpose, base_customer_read_allowed, sensitive_field_policy, approval_state)
                VALUES
                    ('{self.dev_role}', 'non-production feature validation', false, 'masked_last4', 'review_required'),
                    ('{self.app_role}', 'production customer service', true, 'cleartext', 'approved'),
                    ('{self.decoy_role}', 'approved fraud investigation', true, 'cleartext', 'approved'),
                    ('{self.decoy_inherited_role}', 'fraud review group binding', true, 'cleartext', 'approved');
                """,
                "insert customer access policy bindings",
            ),
            (f"GRANT SELECT ON public.{self.policy_table} TO PUBLIC;", "publish customer access policy registry"),
            (
                f"CREATE SCHEMA {self.view_schema};",
                f"create privilege-masking schema {self.view_schema}",
            ),
            (
                f"""
                CREATE VIEW {self.view_schema}.customer_phone_preview AS
                SELECT
                    customer_id,
                    full_name,
                    CASE
                        WHEN length(phone_number) >= 7
                        THEN substring(phone_number from 1 for 3) || '****' || right(phone_number, 4)
                        ELSE '****'
                    END AS phone_number_masked,
                    email,
                    account_status
                FROM public.{self.table}
                WHERE account_status IN ('ACTIVE', 'REVIEW');
                """,
                "create privilege-masking preview view",
            ),
            (
                f"GRANT USAGE ON SCHEMA {self.view_schema} TO {self.dev_role};",
                f"grant schema {self.view_schema} usage to {self.dev_role}",
            ),
            (
                f"GRANT SELECT ON {self.view_schema}.customer_phone_preview TO {self.dev_role};",
                f"grant preview view SELECT to {self.dev_role}",
            ),
            (
                f"ANALYZE public.{self.table};",
                f"analyze privilege-masking table public.{self.table}",
            ),
        ])
        if self.contractor_role:
            statements.append((
                f"GRANT {self.inherited_role} TO {self.contractor_role};",
                f"grant role {self.inherited_role} to {self.contractor_role}",
            ))
            statements.append((
                f"INSERT INTO public.{self.policy_table} "
                "(principal_role, business_purpose, base_customer_read_allowed, "
                "sensitive_field_policy, approval_state) VALUES "
                f"('{self.contractor_role}', 'support sandbox contractor onboarding', "
                "false, 'masked_last4', 'review_required');",
                "insert contractor access policy binding",
            ))
        if self.default_acl_recurrence:
            statements.append((
                f"ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
                f"GRANT SELECT ON TABLES TO {self.inherited_role};",
                "grant default table privileges to the inherited group",
            ))
        for statement, context in statements:
            _require_sql_success(self.env.execute_sql(statement), context)

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{self.table}')::text, "
                f"to_regclass('{self.view_schema}.customer_phone_preview')::text, "
                f"EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{self.dev_role}'), "
                f"EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{self.app_role}'), "
                f"EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{self.inherited_role}'), "
                f"EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{self.decoy_role}'), "
                f"EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{self.decoy_inherited_role}'), "
                f"pg_has_role('{self.dev_role}', '{self.inherited_role}', 'member'), "
                f"has_table_privilege('{self.dev_role}', 'public.{self.table}', 'SELECT'), "
                f"has_table_privilege('{self.app_role}', 'public.{self.table}', 'SELECT'), "
                f"has_table_privilege('{self.decoy_role}', 'public.{self.table}', 'SELECT'), "
                f"(SELECT count(*) FROM public.{self.policy_table}), "
                "(SELECT EXISTS (SELECT 1 FROM pg_default_acl d "
                "WHERE d.defaclacl::text LIKE '%" + self.inherited_role + "%')), "
                f"(SELECT count(*) FROM public.{self.table}), "
                "(SELECT count(*) = 2 FROM information_schema.columns "
                f"WHERE table_schema = 'public' AND table_name = '{self.table}' "
                "AND column_name IN ('phone_number', 'id_number'));"
            ),
            "verify privilege-masking persistent state",
        )
        expected = [[
            self.table,
            f"{self.view_schema}.customer_phone_preview",
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            5 if self.contractor_role else 4,
            self.default_acl_recurrence,
            500,
            True,
        ]]
        if payload["result"] != expected:
            raise RuntimeError(
                f"Privilege-masking persistent state does not match the Case: "
                f"expected={expected}, observed={payload['result']}"
            )

    def _scrub_pg_stat_statements(self):
        _require_sql_success(
            self.env.execute_sql(
                "SET pg_stat_statements.track = 'none'; "
                "SELECT pg_stat_statements_reset(); "
                "RESET pg_stat_statements.track;"
            ),
            "reset pg_stat_statements after privilege-masking injection",
        )

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {}

    def quiesce(self, context: FaultLifecycleContext):
        """No background threads or runtime resources to clean up."""
        pass

    def recover(self, context: FaultLifecycleContext):
        print("[FaultInjector:PgResourceGovernancePrivilegeMaskingInjector] Recovering masking artifacts...")
        statements = [
            "RESET ROLE; RESET SESSION AUTHORIZATION;",
            f"REVOKE USAGE ON SCHEMA public FROM {self.dev_role}, {self.app_role}, {self.inherited_role};",
            f"REVOKE {self.inherited_role} FROM {self.dev_role};",
            f"REVOKE USAGE ON SCHEMA public FROM {self.decoy_role}, {self.decoy_inherited_role};",
            f"REVOKE {self.decoy_inherited_role} FROM {self.decoy_role};",
        ]
        if self.contractor_role:
            statements.insert(2, f"REVOKE {self.inherited_role} FROM {self.contractor_role};")
        if self.default_acl_recurrence:
            statements.append(
                f"ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
                f"REVOKE SELECT ON TABLES FROM {self.inherited_role};"
            )
        statements.extend([
            f"DROP SCHEMA IF EXISTS {self.view_schema} CASCADE;",
            f"DROP TABLE IF EXISTS public.{self.policy_table} CASCADE;",
            f"DROP TABLE IF EXISTS public.{self.table} CASCADE;",
            f"DROP ROLE IF EXISTS {self.dev_role};",
            f"DROP ROLE IF EXISTS {self.app_role};",
            f"DROP ROLE IF EXISTS {self.inherited_role};",
            f"DROP ROLE IF EXISTS {self.decoy_role};",
            f"DROP ROLE IF EXISTS {self.decoy_inherited_role};",
        ])
        if self.contractor_role:
            statements.append(f"DROP ROLE IF EXISTS {self.contractor_role};")
        for statement in statements:
            _require_sql_success(
                self.env.execute_sql(statement),
                f"recover privilege-masking artifact with {statement}",
            )
        self.env.reconnect()

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._verify_persistent_state()
class PgResourceGovernancePrivilegeMaskingScenario(PostgresScenario):
    scenario_id = 'pg_resource_governance_privilege_masking'
    description = 'Simulates an over-privileged non-production account that can read customer sensitive columns in clear text.'
    cases = (_PGRESOURCEGOVERNANCEPRIVILEGEMASKINGSCENARIO_CASE, _PGRESOURCEGOVERNANCEPRIVILEGEMASKING_SIMPLE_CASE)

    def build_fault_plan(self, case: PgResourceGovernancePrivilegeMaskingCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgResourceGovernancePrivilegeMaskingInjector,
                config={
                    'table': case.table,
                    'dev_role': case.dev_role,
                    'app_role': case.app_role,
                    'view_schema': case.view_schema,
                    'inherited_role': case.inherited_role,
                    'decoy_role': case.decoy_role,
                    'decoy_inherited_role': case.decoy_inherited_role,
                    'policy_table': case.policy_table,
                    'contractor_role': case.contractor_role,
                    'default_acl_recurrence': case.default_acl_recurrence,
                    'role_password': case.role_password,
                },
            ),
        )
