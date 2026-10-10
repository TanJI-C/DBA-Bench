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
from ...base import (
    DifficultyCalibration,
    PostgresCaseRuntime,
    PostgresScenario,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    CaseResourceSpec,
    PostgresScenarioCase,
)


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
class PgHealthCheckTableBloatCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    tables: tuple[str, ...]
    noise_tables: tuple[str, ...]
    update_column: str
    table_update_columns: Mapping[str, str]
    batch_size: int
    rounds: int
    noise_update_plan: Mapping[str, tuple[int, int]]
    index_name: str
    target_table: str

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckTableBloatForStoreReturnsTableIndexBloatScenarioCase(PgHealthCheckTableBloatCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckTableBloatForStoreReturnsBloatSimpleScenarioCase(PgHealthCheckTableBloatCase):
    pass

_PGHEALTHCHECKTABLEBLOATSCENARIO_CASE = PgHealthCheckTableBloatForStoreReturnsTableIndexBloatScenarioCase(
    case_id='store_returns_table_index_bloat',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "target table and index bloat measured",
                    "entity": "store_returns_table_index_bloat",
                    "evidence": [
                        "scripted diagnostic actions observed target table and index bloat measured"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "store returns is the true bloat target",
                    "entity": "store_returns_table_index_bloat",
                    "evidence": [
                        "scripted diagnostic actions observed store returns is the true bloat target"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "vacuum full requires maintenance window",
                    "entity": "store_returns_table_index_bloat",
                    "evidence": [
                        "scripted diagnostic actions observed vacuum full requires maintenance window"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "vacuum full target and reindex target index",
                    "entity": "store_returns_table_index_bloat",
                    "evidence": [
                        "scripted diagnostic actions observed vacuum full target and reindex target index"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "rebuild the target table and index"
            ],
            "verification": [
                "maintenance window and ACCESS EXCLUSIVE lock impact assessed"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgHealthCheckTableBloatForStoreReturnsTableIndexBloatEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='Simulates a production health check with one truly bloated fact table hidden among normal dead tuple, reporting, and maintenance noise.',
    alert='Scheduled PostgreSQL health-check ticket: relation-level storage growth on the primary breached the housekeeping threshold since the last maintenance window. Several large relations and routine reporting jobs were active during the interval. Review relation space and maintenance indicators, identify which relation crossed the threshold, and perform only safe maintenance-window work when the evidence is sufficient.',
    initial_state={'status': 'degraded', 'table_bloat': 'high', 'index_bloat': 'high'},
    expected_target={'status': 'recovered',
 'table_bloat': 'cleaned',
 'index_bloat': 'rebuilt'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    tables=('store_returns', 'store_sales', 'catalog_sales', 'inventory'),
    noise_tables=('store_sales', 'catalog_sales', 'inventory'),
    update_column='sr_return_quantity',
    table_update_columns={
        'store_returns': 'sr_return_quantity',
        'store_sales': 'ss_quantity',
        'catalog_sales': 'cs_quantity',
        'inventory': 'inv_quantity_on_hand',
    },
    batch_size=12000,
    rounds=8,
    noise_update_plan={
        'store_sales': (50000, 1),
        'catalog_sales': (50000, 1),
        'inventory': (80000, 1),
    },
    index_name='idx_store_returns_sr_return_quantity_bloat_probe',
    target_table='store_returns',
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.5,
        reference_run_ids=(
            "reference-62__pg_health_check_table_bloat__"
            "store_returns_table_index_bloat__mock__r001",
        ),
    ),
)

_PGHEALTHCHECKTABLEBLOAT_SIMPLE_CASE = PgHealthCheckTableBloatForStoreReturnsBloatSimpleScenarioCase(
    case_id='store_returns_bloat_simple', case_no=1,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "store returns dead tuples and index growth measured",
                    "entity": "store_returns_bloat_simple",
                    "evidence": [
                        "scripted diagnostic actions observed store returns dead tuples and index growth measured"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "store returns exceeds the comparison table",
                    "entity": "store_returns_bloat_simple",
                    "evidence": [
                        "scripted diagnostic actions observed store returns exceeds the comparison table"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "vacuum full requires a maintenance window",
                    "entity": "store_returns_bloat_simple",
                    "evidence": [
                        "scripted diagnostic actions observed vacuum full requires a maintenance window"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "vacuum full store returns and reindex its probe index",
                    "entity": "store_returns_bloat_simple",
                    "evidence": [
                        "scripted diagnostic actions observed vacuum full store returns and reindex its probe index"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "rebuild the target table and index"
            ],
            "verification": [
                "maintenance window and ACCESS EXCLUSIVE lock impact assessed"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    evaluator=PgHealthCheckTableBloatForStoreReturnsBloatSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcds:latest', workload_tag='tpcds', dataset_scale=1,
    title='A focused bloat review with one target fact table and one lower-ratio comparison table.',
    alert='[Scheduled PostgreSQL Health Check] Relation storage and dead-tuple indicators exceeded the maintenance threshold. Compare the affected relations, identify the one requiring maintenance, assess locking impact, and perform only the targeted maintenance-window repair.',
    initial_state={'status': 'degraded', 'table_bloat': 'high'},
    expected_target={'status': 'recovered', 'table_bloat': 'cleaned', 'index_bloat': 'rebuilt'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    tables=('store_returns', 'store_sales'), noise_tables=('store_sales',),
    update_column='sr_return_quantity', table_update_columns={'store_returns': 'sr_return_quantity', 'store_sales': 'ss_quantity'},
    batch_size=4000, rounds=3, noise_update_plan={'store_sales': (2000, 1)},
    index_name='idx_store_returns_quantity_bloat_simple', target_table='store_returns',
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.2,
        reference_run_ids=('run_pg_health_check_table_bloat_store_returns_bloat_simple_MockLLMAgent',),
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

class PgHealthCheckTableBloatInjector(BaseFaultInjector):
    """
    模拟"表与索引膨胀/碎片化"故障。
    多张表都有 dead tuples 和报表痕迹，只有 target_table 的 dead ratio 真正超阈值。
    target_table 使用 per-table autovacuum 高阈值模拟历史维护策略残留。
    """

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self.table_sizes_before = {}
        self.table_sizes_after_inject = {}
        self.index_sizes_before = {}
        self.index_sizes_after_inject = {}

        print(f"[FaultInjector:PgHealthCheckTableBloatInjector] Injecting table bloat on tables: {self.tables}")
        with env.metrics_hidden():
            for table in self.tables:
                self.env.execute_sql(f"VACUUM ANALYZE {table};")
                if table == self.target_table:
                    self.table_sizes_before[table] = self._relation_size(table, total=True)
                    self.env.execute_sql(
                        f"ALTER TABLE {table} SET (autovacuum_vacuum_scale_factor = 0.95, autovacuum_vacuum_threshold = 100000000);"
                    )
                    self.env.execute_sql(f"DROP INDEX IF EXISTS {self.index_name};")
                    self.env.execute_sql(f"CREATE INDEX {self.index_name} ON {table} ({self.update_column});")
                    self.env.execute_sql(f"ANALYZE {table};")
                    self.index_sizes_before[table] = self._relation_size(self.index_name)
                else:
                    self.env.execute_sql(
                        f"ALTER TABLE {table} SET (autovacuum_vacuum_scale_factor = 0.2, autovacuum_vacuum_threshold = 50000);"
                    )

                column = self.table_update_columns.get(table, self.update_column)
                batch_size, rounds = self.noise_update_plan.get(table, (self.batch_size, self.rounds))
                for i in range(rounds):
                    sql_update = (
                        f"UPDATE {table} "
                        f"SET {column} = COALESCE({column}, 0) + {i + 1} "
                        f"WHERE ctid IN (SELECT ctid FROM {table} LIMIT {batch_size});"
                    )
                    self.env.execute_sql(sql_update)
                self.env.execute_sql(f"ANALYZE {table};")
                if table == self.target_table:
                    self.table_sizes_after_inject[table] = self._relation_size(table, total=True)
                    self.index_sizes_after_inject[table] = self._relation_size(self.index_name)
                total = batch_size * rounds
                print(f"[FaultInjector:PgHealthCheckTableBloatInjector] Generated dead tuples on {table} ({total} row updates)")

        _require_sql_success(
            self.env.execute_sql(
                "SET statement_timeout = '120s'; "
                "SELECT count(*), sum(ss_net_profit) FROM store_sales WHERE ss_quantity BETWEEN 1 AND 5;"
            ),
            "seed table-bloat reporting noise",
        )

        if not env.reconnect():
            raise RuntimeError(
                f"Table-bloat injection could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.tables = [_validate_sql_identifier(table, "table") for table in config['tables']]
        self.target_table = _validate_sql_identifier(config['target_table'], "target_table")
        self.noise_tables = [_validate_sql_identifier(table, "noise_table") for table in config['noise_tables']]
        self.update_column = _validate_sql_identifier(config['update_column'], "update_column")
        self.table_update_columns = {
            _validate_sql_identifier(table, "table_update_column_table"): _validate_sql_identifier(column, "table_update_column")
            for table, column in config['table_update_columns'].items()
        }
        self.batch_size = config['batch_size']
        self.rounds = config['rounds']
        self.noise_update_plan = config['noise_update_plan']
        self.index_name = _validate_sql_identifier(
            config['index_name'],
            "index_name",
        )

    def _relation_size(self, relname: str, total: bool = False) -> int:
        fn = "pg_total_relation_size" if total else "pg_relation_size"
        payload = _json_object(
            self.env.execute_sql(f"SELECT {fn}('{relname}'::regclass);"),
            f"read relation size for {relname}",
        )
        return int(payload["result"][0][0])

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {
            "table_sizes_after_inject": self.table_sizes_after_inject,
            "index_sizes_before": self.index_sizes_before,
            "index_sizes_after_inject": self.index_sizes_after_inject,
        }

    def quiesce(self, context: FaultLifecycleContext):
        """No background threads or runtime resources to clean up."""
        pass

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        self._configure(context.config, env)
        print(f"[FaultInjector:PgHealthCheckTableBloatInjector] Recovering target table and resetting table reloptions...")
        if not env.reconnect():
            raise RuntimeError(
                f"Table-bloat recovery could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        for table in self.tables:
            if table == self.target_table:
                _require_sql_success(
                    env.execute_sql(f"VACUUM FULL {table};"),
                    f"vacuum recovered table {table}",
                )
                _require_sql_success(
                    env.execute_sql(f"DROP INDEX IF EXISTS {self.index_name};"),
                    f"drop table-bloat index {self.index_name} before baseline restore",
                )
                _require_sql_success(
                    env.execute_sql(
                        f"CREATE INDEX {self.index_name} "
                        f"ON {self.target_table} ({self.update_column});"
                    ),
                    f"restore table-bloat index {self.index_name}",
                )
            _require_sql_success(
                env.execute_sql(
                    f"ALTER TABLE {table} RESET (autovacuum_vacuum_scale_factor, autovacuum_vacuum_threshold);"
                ),
                f"restore autovacuum for table {table}",
            )

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self.table_sizes_after_inject = {self.target_table: self._relation_size(self.target_table, total=True)}
        index_size = self._relation_size(self.index_name)
        if index_size <= 0:
            raise RuntimeError(
                f"Table-bloat fault image index is empty: index={self.index_name}, size={index_size}"
            )
        self.index_sizes_before = {}
        self.index_sizes_after_inject = {self.target_table: index_size}


class PgHealthCheckTableBloatScenario(PostgresScenario):
    scenario_id = 'pg_health_check_table_bloat'
    description = 'Simulates table and index bloat by disabling autovacuum and generating dead tuples via bulk updates.'
    cases = (_PGHEALTHCHECKTABLEBLOATSCENARIO_CASE, _PGHEALTHCHECKTABLEBLOAT_SIMPLE_CASE)

    def build_fault_plan(self, case: PgHealthCheckTableBloatCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgHealthCheckTableBloatInjector,
                config={
                    'tables': case.tables,
                    'target_table': case.target_table,
                    'noise_tables': case.noise_tables,
                    'update_column': case.update_column,
                    'table_update_columns': case.table_update_columns,
                    'batch_size': case.batch_size,
                    'rounds': case.rounds,
                    'noise_update_plan': case.noise_update_plan,
                    'index_name': case.index_name,
                },
            ),
        )
