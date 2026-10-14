from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.health_check import (
    PgHealthCheckBackupRecoverabilityForMissingWalRecoveryGapEvaluatorCase,
    PgHealthCheckCapacityTrendForSalesEventStorageGrowthEvaluatorCase,
    PgHealthCheckConfigDriftForMemoryResizeConfigDriftEvaluatorCase,
    PgHealthCheckLongRunningTxForCheckoutPoolIdleTransactionEvaluatorCase,
    PgHealthCheckSequenceExhaustionForBillingCanaryInt4SequenceExhaustionEvaluatorCase,
    PgHealthCheckTableBloatForStoreReturnsTableIndexBloatEvaluatorCase,
    PgHealthCheckUnusedIndexesForCustomerRedundantIndexesEvaluatorCase,
    PgHealthCheckBackupRecoverabilityForSingleMissingWalGapSimpleEvaluatorCase,
    PgHealthCheckCapacityTrendForArchiveGrowthForecastSimpleEvaluatorCase,
    PgHealthCheckConfigDriftForCacheBaselineDriftSimpleEvaluatorCase,
    PgHealthCheckLongRunningTxForSingleIdleTransactionCleanupSimpleEvaluatorCase,
    PgHealthCheckSequenceExhaustionForBillingSequenceCapacityRiskSimpleEvaluatorCase,
    PgHealthCheckTableBloatForStoreReturnsBloatSimpleEvaluatorCase,
    PgHealthCheckUnusedIndexesForCustomerUnusedIndexSimpleEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.scenarios.base import DifficultyCalibration, PostgresScenario, FaultPlan, PostgresScenarioCase
from src.workloads.specs import EMPTY_BACKGROUND_WORKLOAD
from src.execution.specs import PostgresCaseRuntime, CaseResourceSpec


POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)

CONFIG_DRIFT_POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=65536,
    container_cpu_limit=1.0,
    container_memory_mb=65536,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckConfigDriftCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    memory_limit_mb: int
    ops_schema: str
    old_baseline_params: Mapping[str, object]
    recommended_params: Mapping[str, object]

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckConfigDriftForMemoryResizeConfigDriftScenarioCase(PgHealthCheckConfigDriftCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckConfigDriftForCacheBaselineDriftSimpleScenarioCase(PgHealthCheckConfigDriftCase):
    pass

_PGHEALTHCHECKCONFIGDRIFTSCENARIO_CASE = PgHealthCheckConfigDriftForMemoryResizeConfigDriftScenarioCase(
    case_id='memory_resize_config_drift',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "host memory resized to 64gb",
                    "entity": "memory_resize_config_drift",
                    "evidence": [
                        "scripted diagnostic actions observed host memory resized to 64gb"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "postgres memory settings drift from baseline",
                    "entity": "memory_resize_config_drift",
                    "evidence": [
                        "scripted diagnostic actions observed postgres memory settings drift from baseline"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "work_mem and max connections are not drift targets",
                    "entity": "memory_resize_config_drift",
                    "evidence": [
                        "scripted diagnostic actions observed work_mem and max connections are not drift targets"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "recommend shared buffers effective cache and maintenance work mem",
                    "entity": "memory_resize_config_drift",
                    "evidence": [
                        "scripted diagnostic actions observed recommend shared buffers effective cache and maintenance work mem"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "shared buffers maintenance restart window",
                    "entity": "memory_resize_config_drift",
                    "evidence": [
                        "scripted diagnostic actions observed shared buffers maintenance restart window"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "plan shared_buffers, effective_cache_size, and maintenance_work_mem changes"
            ],
            "verification": [
                "maintenance window, rollback, and workload validation documented"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgHealthCheckConfigDriftForMemoryResizeConfigDriftEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates a capacity review where PostgreSQL runtime settings lag behind the current instance profile amid normal operational noise.',
    alert='[Routine Fleet Health] The weekly capacity review for pg-primary-17 shows lower cache headroom and throughput elasticity than peers with the same instance class. The window also includes reporting jobs, connection-pool churn, and post-maintenance notes. Inspect the live instance profile and database state, separate actionable baseline variance from normal operational noise, and submit a production-safe change plan with validation steps.',
    initial_state={'status': 'needs_review',
 'memory_mb': 65536,
 'postgres_memory_params': {'shared_buffers': '1GB',
                            'effective_cache_size': '6GB',
                            'maintenance_work_mem': '256MB',
                            'work_mem': '8MB',
                            'max_connections': '300',
                            'autovacuum_naptime': '5min'}},
    expected_target={'status': 'audited',
 'drift_identified': True,
 'recommended_params': {'shared_buffers': '4GB-8GB after workload validation',
                        'effective_cache_size': '48GB',
                        'maintenance_work_mem': '1GB',
                        'work_mem': 'keep 8MB until per-role concurrency is reviewed'}},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=CONFIG_DRIFT_POSTGRES_RESOURCES),
    memory_limit_mb=65536,
    ops_schema='ops_config_audit',
    old_baseline_params={'shared_buffers': '1GB',
 'effective_cache_size': '6GB',
 'maintenance_work_mem': '256MB',
 'work_mem': '8MB',
 'max_connections': '300',
 'autovacuum_naptime': '5min'},
    recommended_params={'shared_buffers': '4GB-8GB after workload validation',
 'effective_cache_size': '48GB',
 'maintenance_work_mem': '1GB',
 'work_mem': 'keep 8MB until per-role concurrency is reviewed'},
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.535714,
        reference_run_ids=(
            "reference-53__pg_health_check_config_drift__"
            "memory_resize_config_drift__mock__r001",
        ),
    ),
)

_PGHEALTHCHECKCONFIGDRIFT_SIMPLE_CASE = PgHealthCheckConfigDriftForCacheBaselineDriftSimpleScenarioCase(
    case_id='cache_baseline_drift_simple',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "host memory capacity increased",
                    "entity": "cache_baseline_drift_simple",
                    "evidence": [
                        "scripted diagnostic actions observed host memory capacity increased"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "postgres cache settings remain on the old baseline",
                    "entity": "cache_baseline_drift_simple",
                    "evidence": [
                        "scripted diagnostic actions observed postgres cache settings remain on the old baseline"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "work mem is an intentional guardrail",
                    "entity": "cache_baseline_drift_simple",
                    "evidence": [
                        "scripted diagnostic actions observed work mem is an intentional guardrail"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "shared buffers change needs a maintenance window",
                    "entity": "cache_baseline_drift_simple",
                    "evidence": [
                        "scripted diagnostic actions observed shared buffers change needs a maintenance window"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "plan shared_buffers and effective_cache_size changes"
            ],
            "verification": [
                "maintenance window and rollback documented"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=1,
    evaluator=PgHealthCheckConfigDriftForCacheBaselineDriftSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='A focused post-resize audit with two stale cache parameters and one intentional work_mem guardrail.',
    alert='[Routine Fleet Review] Cache headroom on a resized PostgreSQL node trails comparable instances. Inspect the live allocation and settings sources, separate intentional concurrency limits from stale cache sizing, and provide a staged change, validation, and rollback plan.',
    initial_state={'status': 'needs_review', 'memory_mb': 65536, 'postgres_memory_params': {'shared_buffers': '1GB', 'effective_cache_size': '6GB', 'work_mem': '8MB'}},
    expected_target={'status': 'audited', 'drift_identified': True, 'recommended_params': {'shared_buffers': '6GB', 'effective_cache_size': '48GB', 'work_mem': 'keep 8MB'}},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=CONFIG_DRIFT_POSTGRES_RESOURCES),
    memory_limit_mb=65536,
    ops_schema='ops_cache_audit',
    old_baseline_params={'shared_buffers': '1GB', 'effective_cache_size': '6GB', 'work_mem': '8MB'},
    recommended_params={'shared_buffers': '6GB', 'effective_cache_size': '48GB', 'work_mem': '8MB'},
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.25,
        reference_run_ids=('run_pg_health_check_config_drift_cache_baseline_drift_simple_MockLLMAgent',),
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

class PgHealthCheckConfigDriftInjector(BaseFaultInjector):
    """
    模拟配置基线漂移：实例内存容量已提升，但 PostgreSQL 内存参数仍为旧基线。
    """

    CONFIG_PARAMS = (
        "shared_buffers",
        "effective_cache_size",
        "maintenance_work_mem",
        "work_mem",
        "max_connections",
        "autovacuum_naptime",
    )

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print("[FaultInjector:PgHealthCheckConfigDriftInjector] Applying noisy post-maintenance baseline...")
        with env.metrics_hidden(allow_pgss_reset=True):
            self._setup_observability_noise()
            for param in self.config_params:
                value = self.old_baseline_params[param]
                _require_sql_success(
                    env.execute_sql(f"ALTER SYSTEM SET {param} = '{value}';"),
                    f"install config-drift setting {param}={value}",
                )
            _require_sql_success(
                env.execute_sql("SELECT pg_reload_conf();"),
                "reload config-drift settings",
            )
            _require_sql_success(
                env.manage_instance("restart"),
                "restart PostgreSQL after installing config drift",
            )
            self._assert_fault_observable()
            self._scrub_pg_stat_statements()

        print("[FaultInjector:PgHealthCheckConfigDriftInjector] Fault injection complete.")

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.old_baseline_params = dict(config["old_baseline_params"])
        self.config_params = tuple(self.old_baseline_params)
        self.ops_schema = _validate_sql_identifier(str(config["ops_schema"]), "ops_schema")

    def _assert_fault_observable(self) -> None:
        expressions = ", ".join(
            f"current_setting('{param}')" for param in self.config_params
        )
        payload = _json_object(
            self.env.execute_sql(f"SELECT {expressions};"),
            "verify config-drift fault settings",
        )
        observed = dict(zip(self.config_params, payload["result"][0]))
        mismatches = {
            param: {
                "expected": str(self.old_baseline_params[param]),
                "observed": str(observed[param]),
            }
            for param in self.config_params
            if str(observed[param]).lower()
            != str(self.old_baseline_params[param]).lower()
        }
        if mismatches:
            raise RuntimeError(
                f"Config-drift fault settings do not match the Case: {mismatches}"
            )

    def _setup_observability_noise(self) -> None:
        schema = self.ops_schema
        statements = (
            (f"DROP SCHEMA IF EXISTS {schema} CASCADE;", "drop old config audit schema"),
            (f"CREATE SCHEMA {schema};", "create config audit schema"),
            (f"""
                CREATE TABLE {schema}.instance_inventory (
                    observed_at timestamptz NOT NULL,
                    source text NOT NULL,
                    memory_mb integer NOT NULL,
                    cpu_count numeric NOT NULL,
                    note text NOT NULL
                );
            """, "create instance inventory"),
            (f"""
                INSERT INTO {schema}.instance_inventory VALUES
                (now() - interval '38 days', 'cmdb-before-maintenance', 8192, 4, 'retired small class retained for audit history'),
                (now() - interval '3 days', 'container-cgroup-live', 65536, 16, 'current limit exposed to PostgreSQL container'),
                (now() - interval '3 days', 'hypervisor-host', 131072, 32, 'shared host capacity, not fully assigned to this instance');
            """, "seed instance inventory"),
            (f"""
                CREATE TABLE {schema}.maintenance_events (
                    event_at timestamptz NOT NULL,
                    actor text NOT NULL,
                    change_summary text NOT NULL,
                    requires_restart boolean NOT NULL,
                    completed boolean NOT NULL,
                    note text NOT NULL
                );
            """, "create maintenance events"),
            (f"""
                INSERT INTO {schema}.maintenance_events VALUES
                (now() - interval '3 days 2 hours', 'platform', 'moved pg-primary-17 to mem-64g class', true, true, 'container restarted during approved window'),
                (now() - interval '3 days 1 hour', 'dba', 'raised max_connections for pool migration', true, true, 'unrelated to cache sizing'),
                (now() - interval '2 days 22 hours', 'app', 'reporting role kept work_mem override at 8MB', false, true, 'intentional guardrail for 120 pooled sessions'),
                (now() - interval '7 hours', 'monitor', 'autovacuum_naptime left at conservative value after vacuum review', false, true, 'acceptable for current bloat metrics');
            """, "seed maintenance events"),
            (f"""
                CREATE TABLE {schema}.workload_observations (
                    observed_at timestamptz NOT NULL,
                    application_name text NOT NULL,
                    signal text NOT NULL,
                    sample_value text NOT NULL,
                    verdict text NOT NULL
                );
            """, "create workload observations"),
            (f"""
                INSERT INTO {schema}.workload_observations VALUES
                (now() - interval '50 minutes', 'bi-month-end-rollup', 'historical slow SQL', 'TPC-DS report scan 94s', 'scheduled reporting noise'),
                (now() - interval '45 minutes', 'prometheus-postgres-exporter', 'monitor probe', 'pg_settings sampled every 30s', 'normal monitoring'),
                (now() - interval '40 minutes', 'checkout-pool', 'connection pool', '110 active of 300 max_connections during peak', 'pool migration noise'),
                (now() - interval '35 minutes', 'autovacuum launcher', 'dead tuple sweep', 'no table over bloat threshold', 'not root cause');
            """, "seed workload observations"),
        )
        for sql, context in statements:
            _require_sql_success(self.env.execute_sql(sql), context)

    def _scrub_pg_stat_statements(self) -> None:
        _require_sql_success(
            self.env.execute_sql(
                "SET pg_stat_statements.track = 'none'; "
                "SELECT pg_stat_statements_reset(); "
                "RESET pg_stat_statements.track;"
            ),
            "reset pg_stat_statements after config-drift injection",
        )
        self.env.refresh_pgss_baseline()

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {}

    def quiesce(self, context: FaultLifecycleContext):
        """No background threads or runtime resources to clean up."""
        pass

    def recover(self, context: FaultLifecycleContext):
        print("[FaultInjector:PgHealthCheckConfigDriftInjector] Recovering...")
        self._configure(context.config, context.env)
        for param in self.config_params:
            _require_sql_success(
                self.env.execute_sql(f"ALTER SYSTEM RESET {param};"),
                f"recover config-drift setting {param}",
            )
        _require_sql_success(
            self.env.execute_sql(f"DROP SCHEMA IF EXISTS {self.ops_schema} CASCADE;"),
            "drop config audit schema",
        )
        _require_sql_success(
            self.env.execute_sql("SELECT pg_reload_conf();"),
            "reload recovered config-drift settings",
        )
        _require_sql_success(
            self.env.manage_instance("restart"),
            "restart PostgreSQL after recovering config drift",
        )

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden(allow_pgss_reset=True):
            self._assert_fault_observable()
            self._scrub_pg_stat_statements()


class PgHealthCheckConfigDriftScenario(PostgresScenario):
    scenario_id = 'pg_health_check_config_drift'
    description = 'Simulates a capacity-upgraded PostgreSQL instance whose memory settings still reflect an old baseline.'
    cases = (_PGHEALTHCHECKCONFIGDRIFTSCENARIO_CASE, _PGHEALTHCHECKCONFIGDRIFT_SIMPLE_CASE)

    def build_fault_plan(self, case: PgHealthCheckConfigDriftCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgHealthCheckConfigDriftInjector,
                config={
                    'memory_limit_mb': case.memory_limit_mb,
                    'ops_schema': case.ops_schema,
                    'old_baseline_params': case.old_baseline_params,
                },
            ),
        )
