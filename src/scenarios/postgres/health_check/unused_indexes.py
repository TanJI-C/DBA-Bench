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
class PgHealthCheckUnusedIndexesCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    table: str
    required_drop_indexes: tuple[str, ...]
    preserved_index: str
    protected_indexes: tuple[str, ...]
    must_keep_indexes: tuple[str, ...]
    injected_indexes: tuple[str, ...]
    attribution_table: str = ""
    attribution_probe_updates: int = 0

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckUnusedIndexesForCustomerRedundantIndexesScenarioCase(PgHealthCheckUnusedIndexesCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckUnusedIndexesForCustomerUnusedIndexSimpleScenarioCase(PgHealthCheckUnusedIndexesCase):
    pass

_PGHEALTHCHECKUNUSEDINDEXESSCENARIO_CASE = PgHealthCheckUnusedIndexesForCustomerRedundantIndexesScenarioCase(
    case_id='customer_redundant_indexes',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "unused index statistics reviewed",
                    "entity": "customer_redundant_indexes",
                    "evidence": [
                        "scripted diagnostic actions observed unused index statistics reviewed"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "three target unused indexes",
                    "entity": "customer_redundant_indexes",
                    "evidence": [
                        "scripted diagnostic actions observed three target unused indexes"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "redundant prefix and constraint indexes preserved",
                    "entity": "customer_redundant_indexes",
                    "evidence": [
                        "scripted diagnostic actions observed redundant prefix and constraint indexes preserved"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "drop target indexes concurrently",
                    "entity": "customer_redundant_indexes",
                    "evidence": [
                        "scripted diagnostic actions observed drop target indexes concurrently"
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
    evaluator=PgHealthCheckUnusedIndexesForCustomerRedundantIndexesEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='Simulates production index maintenance overhead hidden inside a routine health check.',
    alert='[INFO] [PostgreSQL/Primary] Nightly health-check ticket: write latency and WAL generated per business transaction are 12-18% above last week\'s baseline on the customer domain. The same window also contains normal OLTP traffic, BI reports, monitoring probes, and a recent release rollback plan. Triage the production signals, explain what is safe to change now, apply the safe remediation, and verify that protected release/reporting paths remain intact.',
    initial_state={'status': 'degraded', 'unused_indexes': 'present'},
    expected_target={'status': 'recovered',
 'unused_indexes': 'cleaned',
 'required_drop_indexes': ('idx_unused_birth_country', 'idx_unused_email', 'idx_redundant_last'),
 'preserved_index': 'idx_redundant_last_first',
 'must_keep_indexes': ('idx_redundant_last_first',
                       'idx_customer_id_unique_guard',
                       'idx_fk_customer_current_addr',
                       'idx_recent_customer_login_release',
                       'idx_expr_lower_customer_email',
                       'idx_partial_preferred_customer',
                       'idx_rollback_customer_review',
                       'idx_lowfreq_customer_review',
                       'idx_reporting_birth_year_month')},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    table='customer',
    required_drop_indexes=('idx_unused_birth_country', 'idx_unused_email', 'idx_redundant_last'),
    preserved_index='idx_redundant_last_first',
    protected_indexes=('idx_customer_id_unique_guard',
                       'idx_fk_customer_current_addr',
                       'idx_recent_customer_login_release',
                       'idx_expr_lower_customer_email',
                       'idx_partial_preferred_customer',
                       'idx_rollback_customer_review',
                       'idx_lowfreq_customer_review',
                       'idx_reporting_birth_year_month'),
    must_keep_indexes=('idx_redundant_last_first',
                       'idx_customer_id_unique_guard',
                       'idx_fk_customer_current_addr',
                       'idx_recent_customer_login_release',
                       'idx_expr_lower_customer_email',
                       'idx_partial_preferred_customer',
                       'idx_rollback_customer_review',
                       'idx_lowfreq_customer_review',
                       'idx_reporting_birth_year_month'),
    injected_indexes=('idx_unused_birth_country',
                      'idx_unused_email',
                      'idx_redundant_last',
                      'idx_redundant_last_first',
                      'idx_customer_id_unique_guard',
                      'idx_fk_customer_current_addr',
                      'idx_recent_customer_login_release',
                      'idx_expr_lower_customer_email',
                      'idx_partial_preferred_customer',
                      'idx_rollback_customer_review',
                      'idx_lowfreq_customer_review',
                      'idx_reporting_birth_year_month'),
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.416667,
        reference_run_ids=(
            "reference-50__pg_health_check_unused_indexes__"
            "customer_redundant_indexes__mock__r001",
        ),
    ),
)

_PGHEALTHCHECKUNUSEDINDEXES_SIMPLE_CASE = PgHealthCheckUnusedIndexesForCustomerUnusedIndexSimpleScenarioCase(
    case_id='customer_unused_index_simple', case_no=1,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "customer index usage and definitions reviewed",
                    "entity": "customer_unused_index_simple",
                    "evidence": [
                        "scripted diagnostic actions observed customer index usage and definitions reviewed"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "non-HOT update volume maintains every customer secondary index and drives write overhead",
                    "entity": "customer_unused_index_simple",
                    "evidence": [
                        "scripted diagnostic actions observed non-HOT update volume maintains every customer secondary index and drives write overhead"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the write amplification sits on customer, whose updates almost never take the HOT path, while customer_address updates take the HOT path and maintain no extra indexes",
                    "entity": "customer_unused_index_simple",
                    "evidence": [
                        "scripted diagnostic actions observed the write amplification sits on customer, whose updates almost never take the HOT path, while customer_address updates take the HOT path and maintain no extra indexes"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "one unused customer index is safe to drop",
                    "entity": "customer_unused_index_simple",
                    "evidence": [
                        "scripted diagnostic actions observed one unused customer index is safe to drop"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "unique and reporting indexes are preserved",
                    "entity": "customer_unused_index_simple",
                    "evidence": [
                        "scripted diagnostic actions observed unique and reporting indexes are preserved"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "indexes below the 14-day observation window are preserved",
                    "entity": "customer_unused_index_simple",
                    "evidence": [
                        "scripted diagnostic actions observed indexes below the 14-day observation window are preserved"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "drop the unused index concurrently",
                    "entity": "customer_unused_index_simple",
                    "evidence": [
                        "scripted diagnostic actions observed drop the unused index concurrently"
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
    evaluator=PgHealthCheckUnusedIndexesForCustomerUnusedIndexSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcds:latest', workload_tag='tpcds', dataset_scale=1,
    title='A focused customer-domain cleanup review with competing low-usage candidates across two tables and protected operational paths.',
    alert='[Nightly PostgreSQL Review] Write overhead across the customer domain (customer, customer_address) rose above its weekly baseline. Review index usage, definitions, dependencies, operational notes, and the recorded index change history; remove only the indexes that are safe to retire and implicated in the reported overhead, and verify protected paths remain available.',
    initial_state={'status': 'degraded', 'unused_indexes': 'present'},
    expected_target={'status': 'recovered', 'required_drop_indexes': ('idx_unused_birth_country',), 'must_keep_indexes': ('idx_redundant_last_first', 'idx_customer_id_unique_guard', 'idx_reporting_birth_year_month', 'idx_fk_customer_current_addr', 'idx_expr_lower_customer_email', 'idx_recent_customer_login_release', 'idx_rollback_customer_review', 'idx_customer_segment_probe', 'idx_customer_address_location_probe')},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    table='customer', required_drop_indexes=('idx_unused_birth_country',), preserved_index='idx_redundant_last_first',
    protected_indexes=('idx_customer_id_unique_guard', 'idx_reporting_birth_year_month', 'idx_fk_customer_current_addr', 'idx_expr_lower_customer_email', 'idx_recent_customer_login_release', 'idx_rollback_customer_review', 'idx_customer_segment_probe', 'idx_customer_address_location_probe'),
    must_keep_indexes=('idx_redundant_last_first', 'idx_customer_id_unique_guard', 'idx_reporting_birth_year_month', 'idx_fk_customer_current_addr', 'idx_expr_lower_customer_email', 'idx_recent_customer_login_release', 'idx_rollback_customer_review', 'idx_customer_segment_probe', 'idx_customer_address_location_probe'),
    injected_indexes=('idx_unused_birth_country', 'idx_redundant_last_first', 'idx_customer_id_unique_guard', 'idx_reporting_birth_year_month', 'idx_fk_customer_current_addr', 'idx_expr_lower_customer_email', 'idx_recent_customer_login_release', 'idx_rollback_customer_review', 'idx_customer_segment_probe', 'idx_customer_address_location_probe'),
    attribution_table='customer_address',
    attribution_probe_updates=3000,
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.545455,
        reference_run_ids=('run_pg_health_check_unused_indexes_customer_unused_index_simple_MockLLMAgent',),
    ),
)


import json
import re
import time
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

class PgHealthCheckUnusedIndexesInjector(BaseFaultInjector):
    """
    模拟"冗余与失效索引"故障。
    混入约束、近期发布、partial/expression、低频报表和回滚保留索引，
    让 Agent 必须做风险排除后才能清理。
    """

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config['table'], "table")
        self.required_drop_indexes = [
            _validate_sql_identifier(index, "required_drop_index")
            for index in config['required_drop_indexes']
        ]
        self.preserved_index = _validate_sql_identifier(
            config['preserved_index'],
            "preserved_index",
        )
        self.protected_indexes = [
            _validate_sql_identifier(index, "protected_index")
            for index in config['protected_indexes']
        ]
        self.must_keep_indexes = [self.preserved_index] + self.protected_indexes
        self.injected_indexes = list(self.required_drop_indexes) + self.must_keep_indexes
        self.attribution_table = str(config.get('attribution_table', ''))
        self.attribution_probe_updates = int(config.get('attribution_probe_updates', 0))
        if self.attribution_table:
            _validate_sql_identifier(self.attribution_table, "attribution_table")

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)

        print(f"[FaultInjector:PgHealthCheckUnusedIndexesInjector] Injecting unused indexes on {self.table}...")

        with env.metrics_hidden():
            self.recover(context)
            for sql in self._index_setup_sql():
                _require_sql_success(
                    env.execute_sql(sql),
                    "create unused-index scenario index",
                )
                print(f"[FaultInjector:PgHealthCheckUnusedIndexesInjector] Created injected index.")

            self._reset_table_stats()
            self._assert_fault_observable()
            self._seed_production_noise()
            self._seed_non_hot_updates()
            if self.attribution_table:
                self._seed_attribution_contrast()
            self._create_change_log()
            _require_sql_success(
                self.env.execute_sql(f"ANALYZE {self.table};"),
                f"analyze unused-index table {self.table}",
            )

        print(f"[FaultInjector:PgHealthCheckUnusedIndexesInjector] Fault injection complete.")

    def _index_setup_sql(self):
        statements = {
            "idx_unused_birth_country": f"CREATE INDEX IF NOT EXISTS idx_unused_birth_country ON {self.table}(c_birth_country);",
            "idx_unused_email": f"CREATE INDEX IF NOT EXISTS idx_unused_email ON {self.table}(c_email_address);",
            "idx_redundant_last_first": f"CREATE INDEX IF NOT EXISTS idx_redundant_last_first ON {self.table}(c_last_name, c_first_name);",
            "idx_redundant_last": f"CREATE INDEX IF NOT EXISTS idx_redundant_last ON {self.table}(c_last_name);",
            "idx_customer_id_unique_guard": f"CREATE UNIQUE INDEX IF NOT EXISTS idx_customer_id_unique_guard ON {self.table}(c_customer_id);",
            "idx_fk_customer_current_addr": f"CREATE INDEX IF NOT EXISTS idx_fk_customer_current_addr ON {self.table}(c_current_addr_sk);",
            "idx_recent_customer_login_release": f"CREATE INDEX IF NOT EXISTS idx_recent_customer_login_release ON {self.table}(c_login);",
            "idx_expr_lower_customer_email": f"CREATE INDEX IF NOT EXISTS idx_expr_lower_customer_email ON {self.table}((lower(c_email_address)));",
            "idx_partial_preferred_customer": f"CREATE INDEX IF NOT EXISTS idx_partial_preferred_customer ON {self.table}(c_customer_sk) WHERE c_preferred_cust_flag = 'Y';",
            "idx_rollback_customer_review": f"CREATE INDEX IF NOT EXISTS idx_rollback_customer_review ON {self.table}(c_last_review_date_sk);",
            "idx_lowfreq_customer_review": f"CREATE INDEX IF NOT EXISTS idx_lowfreq_customer_review ON {self.table}(c_first_sales_date_sk);",
            "idx_reporting_birth_year_month": f"CREATE INDEX IF NOT EXISTS idx_reporting_birth_year_month ON {self.table}(c_birth_year, c_birth_month);",
            "idx_customer_segment_probe": f"CREATE INDEX IF NOT EXISTS idx_customer_segment_probe ON {self.table}(c_current_cdemo_sk);",
            "idx_customer_address_location_probe": f"CREATE INDEX IF NOT EXISTS idx_customer_address_location_probe ON {self.attribution_table}(ca_location_type);",
        }
        extras = [
            f"COMMENT ON INDEX idx_customer_id_unique_guard IS 'business key uniqueness guard; idx_scan may stay low';",
            f"COMMENT ON INDEX idx_fk_customer_current_addr IS 'supports customer_current_addr_fk parent maintenance path';",
            f"COMMENT ON INDEX idx_recent_customer_login_release IS 'release 2026-07-08 login rollout; observe for 14 days before any cleanup';",
            f"COMMENT ON INDEX idx_expr_lower_customer_email IS 'case-insensitive support lookup expression index';",
            f"COMMENT ON INDEX idx_partial_preferred_customer IS 'partial index for preferred-customer emergency segment';",
            f"COMMENT ON INDEX idx_rollback_customer_review IS 'rollback hold for customer review batch until release close';",
            f"COMMENT ON INDEX idx_lowfreq_customer_review IS 'monthly compliance lookup; low scan but critical';",
            f"COMMENT ON INDEX idx_reporting_birth_year_month IS 'BI cohort report path; write cost accepted';",
        ]
        selected = [statements[name] for name in self.injected_indexes]
        selected.extend(sql for sql in extras if any(name in sql for name in self.injected_indexes))
        if "idx_fk_customer_current_addr" in self.injected_indexes:
            selected.append(
                f"ALTER TABLE {self.table} ADD CONSTRAINT customer_current_addr_fk "
                "FOREIGN KEY (c_current_addr_sk) REFERENCES customer_address(ca_address_sk) NOT VALID;"
            )
        return selected

    def _reset_table_stats(self):
        result = self.env.execute_sql(f"SELECT oid FROM pg_class WHERE relname = '{self.table}';")
        payload = _json_object(result, "read unused-index table oid")
        if not payload.get("result"):
            raise RuntimeError(f"Could not find table oid for {self.table}: {result}")
        table_oid = payload["result"][0][0]
        # pg_stat_reset_single_table_counters 会让调用后端对该表的后续统计读取永久
        # 命中陈旧快照（stats_fetch_consistency=cache），必须用独立连接执行重置，
        # 否则 Agent 通过 env 连接读到的 n_tup_* 恒为 0。
        conn = self._stats_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_stat_reset_single_table_counters(%s);", (table_oid,))
        finally:
            conn.close()
        print(f"[FaultInjector:PgHealthCheckUnusedIndexesInjector] Reset stats for {self.table} (oid={table_oid})")

    def _stats_connection(self):
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=10,
        )
        conn.autocommit = True
        return conn

    def _seed_production_noise(self):
        for sql in [
            f"SET enable_seqscan = off; SELECT count(*) FROM {self.table} WHERE c_current_addr_sk IS NOT NULL; RESET enable_seqscan;",
            f"SET enable_seqscan = off; SELECT count(*) FROM {self.table} WHERE c_first_sales_date_sk IS NOT NULL; RESET enable_seqscan;",
            f"SET enable_seqscan = off; SELECT count(*) FROM {self.table} WHERE c_birth_year BETWEEN 1960 AND 1970 AND c_birth_month = 7; RESET enable_seqscan;",
            f"SELECT count(*) FROM {self.table} WHERE c_preferred_cust_flag = 'Y';",
            f"SELECT count(*) FROM {self.table} WHERE lower(c_email_address) LIKE 'a%';",
            "SELECT 1 AS monitoring_probe;",
        ]:
            _require_sql_success(
                self.env.execute_sql(sql),
                f"seed production index noise SQL={sql!r}",
            )

    def _seed_non_hot_updates(self):
        """contact-preference 批量更新：触碰索引列使更新无法走 HOT。批量行数超过 env
        连接的 statement_timeout 预算，走独立连接执行（统计全局可见）。"""
        conn = self._stats_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = 0;")
                cur.execute(
                    f"UPDATE {self.table} SET c_login = c_login "
                    f"WHERE c_customer_sk <= 3600;"
                )
        finally:
            conn.close()

    def _seed_attribution_contrast(self):
        """归因对照：attribution 表的批量更新触碰非索引列且页内有空间（fillfactor=50
        重写保证），更新全部走 HOT，不构成索引维护放大。重写、计数器重置与断言读数走
        独立连接（fresh backend、无 statement_timeout 限制），env 连接只执行 DML，
        避免统计快照毒化与超时配置影响 Agent 会话。"""
        table = self.attribution_table
        conn = self._stats_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = 0;")
                cur.execute(f"ALTER TABLE {table} SET (fillfactor=50);")
                cur.execute(f"VACUUM FULL {table};")
        finally:
            conn.close()
        result = self.env.execute_sql(f"SELECT oid FROM pg_class WHERE relname = '{table}';")
        payload = _json_object(result, "read attribution table oid")
        if not payload.get("result"):
            raise RuntimeError(f"Could not find table oid for {table}: {result}")
        # 不对该表调用 pg_stat_reset_single_table_counters：镜像装载只产生 COPY 插入
        # （n_tup_upd 基线为 0），且 reset 的异步生效会抹掉随后 UPDATE 写入的统计。
        conn = self._stats_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = 0;")
                cur.execute(
                    f"UPDATE {table} SET ca_street_number = ca_street_number "
                    f"WHERE ca_address_sk <= {self.attribution_probe_updates};"
                )
        finally:
            conn.close()
        stats = self._wait_for_attribution_stats(table)
        if self.table not in stats or table not in stats:
            raise RuntimeError(
                f"Write-amplification attribution stats missing tables: stats={stats}"
            )
        cust_upd, cust_hot = stats[self.table]
        addr_upd, addr_hot = stats[table]
        if cust_upd < 1000 or cust_hot > cust_upd * 0.1:
            raise RuntimeError(
                "Customer non-HOT write amplification is not observable: "
                f"n_tup_upd={cust_upd}, n_tup_hot_upd={cust_hot}"
            )
        if addr_upd < self.attribution_probe_updates or addr_hot < addr_upd * 0.8:
            raise RuntimeError(
                "Attribution-table HOT contrast is not observable: "
                f"table={table}, n_tup_upd={addr_upd}, n_tup_hot_upd={addr_hot}"
            )

    def _wait_for_attribution_stats(self, table, rounds: int = 10):
        """PG 统计上报按 500ms 节流且挂在事务提交/连接退出上；轮询 fresh 后端直到
        两个表的更新计数可见，超时抛错。"""
        deadline_stats = {}
        for _ in range(rounds):
            time.sleep(0.6)
            conn = self._stats_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT relname, n_tup_upd, n_tup_hot_upd "
                        "FROM pg_stat_user_tables WHERE relname IN (%s, %s);",
                        (self.table, table),
                    )
                    rows = cur.fetchall()
            finally:
                conn.close()
            deadline_stats = {row[0]: (int(row[1] or 0), int(row[2] or 0)) for row in rows}
            if (
                self.table in deadline_stats
                and table in deadline_stats
                and deadline_stats[self.table][0] >= 1000
                and deadline_stats[table][0] >= self.attribution_probe_updates
            ):
                return deadline_stats
        return deadline_stats

    def _create_change_log(self):
        _require_sql_success(
            self.env.execute_sql("""
                CREATE SCHEMA IF NOT EXISTS ops_maintenance;
                CREATE TABLE IF NOT EXISTS ops_maintenance.index_changes (
                    change_id text PRIMARY KEY,
                    applied_at timestamptz NOT NULL,
                    table_name text NOT NULL,
                    index_name text NOT NULL,
                    action text NOT NULL,
                    observation_policy text NOT NULL,
                    note text NOT NULL
                );
            """),
            "create index change log table",
        )
        policy = "index retirement requires at least 14 days of usage observation"
        rows = [
            ("chg-customer-idx-011", "95 days", self.table, "idx_unused_birth_country", "nightly country-rollup candidate from retired batching request"),
            ("chg-customer-idx-014", "90 days", self.table, "idx_redundant_last_first", "composite name lookup for support desk"),
            ("chg-customer-idx-101", "60 days", self.table, "idx_customer_id_unique_guard", "business key uniqueness guard"),
            ("chg-customer-idx-118", "45 days", self.table, "idx_reporting_birth_year_month", "BI cohort reporting path"),
            ("chg-customer-idx-203", "40 days", self.table, "idx_fk_customer_current_addr", "address FK lookup support"),
            ("chg-customer-idx-044", "30 days", self.table, "idx_expr_lower_customer_email", "case-insensitive email lookup"),
            ("chg-customer-idx-052", "25 days", self.table, "idx_recent_customer_login_release", "login rollout support"),
            ("chg-customer-idx-018", "20 days", self.table, "idx_rollback_customer_review", "rollback hold for review batch"),
            ("chg-customer-idx-007", "2 days", self.table, "idx_customer_segment_probe", "marketing segment-rollup probe request"),
        ]
        if self.attribution_table:
            rows.append(
                ("chg-customer-addr-201", "60 days", self.attribution_table, "idx_customer_address_location_probe", "fulfillment location-type rollup probe")
            )
        values = ", ".join(
            f"('{change_id}', now() - interval '{age}', '{table_name}', '{index_name}', "
            f"'create', '{policy}', '{note}')"
            for change_id, age, table_name, index_name, note in rows
        )
        _require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO ops_maintenance.index_changes VALUES {values};"
            ),
            "seed index change log entries",
        )

    def _assert_fault_observable(self):
        names_sql = ",".join(f"'{idx}'" for idx in self.injected_indexes)
        result = self.env.execute_sql(f"""
            SET statement_timeout = '5s';
            SELECT relname, indexrelname, idx_scan
            FROM pg_stat_user_indexes
            WHERE indexrelname IN ({names_sql})
            ORDER BY indexrelname;
        """)
        rows = _json_object(result, "read unused-index visibility")["result"]
        visible = {row[1]: int(row[2] or 0) for row in rows}
        missing = [idx for idx in self.injected_indexes if idx not in visible]
        not_unused = [idx for idx in self.required_drop_indexes if visible.get(idx, 0) != 0]
        if missing or not_unused:
            raise RuntimeError(
                "Unused index fault is not observable: "
                f"missing={missing}, not_unused={not_unused}, raw={result}"
            )

        if {'idx_redundant_last', 'idx_redundant_last_first'} <= set(self.injected_indexes):
            overlap = self.env.execute_sql(f"""
            SET statement_timeout = '5s';
            SELECT c.relname, i.indisunique, i.indisprimary, i.indkey::text
            FROM pg_index i
            JOIN pg_class c ON c.oid = i.indexrelid
            WHERE i.indrelid = '{self.table}'::regclass
              AND c.relname IN ('idx_redundant_last', 'idx_redundant_last_first')
            ORDER BY c.relname;
        """)
            overlap_rows = _json_object(overlap, "read redundant-index overlap")["result"]
            if len(overlap_rows) < 2:
                raise RuntimeError(f"Redundant index pair is not observable: {overlap}")

        if self.attribution_table:
            overlap = self.env.execute_sql(f"""
            SET statement_timeout = '5s';
            SELECT c.relname
            FROM pg_index i
            JOIN pg_class c ON c.oid = i.indexrelid
            WHERE i.indrelid = '{self.attribution_table}'::regclass
              AND c.relname = 'idx_customer_address_location_probe'
            ORDER BY c.relname;
        """)
            overlap_rows = _json_object(overlap, "read attribution probe visibility")["result"]
            if not overlap_rows:
                raise RuntimeError(
                    f"Attribution probe index is not observable on {self.attribution_table}: {overlap}"
                )

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {}

    def quiesce(self, context: FaultLifecycleContext):
        """No background threads or runtime resources to clean up."""
        pass

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        self._configure(context.config, env)
        print(f"[FaultInjector:PgHealthCheckUnusedIndexesInjector] Recovering: dropping injected indexes...")
        _require_sql_success(
            env.execute_sql(
                # The constraint drop needs ACCESS EXCLUSIVE on the table: an
                # unresolved long-transaction blocker (no-agent runs, or an
                # agent that never repaired) would hold it forever. Bound the
                # wait so the activation fails fast and the timeline survives.
                "SET lock_timeout = '30s'; "
                f"ALTER TABLE IF EXISTS {self.table} DROP CONSTRAINT IF EXISTS customer_current_addr_fk; "
                "RESET lock_timeout;"
            ),
            "drop unused-index scenario FK constraint customer_current_addr_fk",
        )
        _require_sql_success(
            env.execute_sql("DROP SCHEMA IF EXISTS ops_maintenance CASCADE;"),
            "drop index change log schema ops_maintenance",
        )
        for idx_name in self.injected_indexes:
            _require_sql_success(
                env.execute_sql(f"DROP INDEX IF EXISTS {idx_name};"),
                f"drop unused-index scenario index {idx_name}",
            )

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        """Re-activate fault from pre-built image state. Unused indexes persist in PG schema."""
        self._configure(config, env)
        self._assert_fault_observable()
        self._seed_production_noise()
        self._seed_non_hot_updates()
class PgHealthCheckUnusedIndexesScenario(PostgresScenario):
    scenario_id = 'pg_health_check_unused_indexes'
    description = 'Simulates production index maintenance overhead hidden inside a routine health check.'
    cases = (_PGHEALTHCHECKUNUSEDINDEXESSCENARIO_CASE, _PGHEALTHCHECKUNUSEDINDEXES_SIMPLE_CASE)

    def build_fault_plan(self, case: PgHealthCheckUnusedIndexesCase) -> tuple[FaultPlan, ...]:
        return (
                FaultPlan(
                    injector_type=PgHealthCheckUnusedIndexesInjector,
                    config={
                        'table': case.table,
                        'required_drop_indexes': case.required_drop_indexes,
                        'preserved_index': case.preserved_index,
                        'protected_indexes': case.protected_indexes,
                        'attribution_table': case.attribution_table,
                        'attribution_probe_updates': case.attribution_probe_updates,
                    },
                ),
        )
