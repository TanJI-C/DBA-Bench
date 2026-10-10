from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.query_perf import (
    PgQueryPerfHeavyOffsetPaginationForBranchOrderDeepOffsetEvaluatorCase,
    PgQueryPerfHeavyOffsetPaginationForBranchOrderShallowOffsetEvaluatorCase,
    PgQueryPerfImplicitTypeConversionForBranchOrderImplicitCastEvaluatorCase,
    PgQueryPerfImplicitTypeConversionForBranchOrderImplicitCastSimpleEvaluatorCase,
    PgQueryPerfMissingIndexForProductCategoryPrefixSimpleEvaluatorCase,
    PgQueryPerfMissingIndexForProductCategorySubstringEvaluatorCase,
    PgQueryPerfParameterSniffingForBranchOrderYearSkewEvaluatorCase,
    PgQueryPerfParameterSniffingForBranchOrderYearSkewSimpleEvaluatorCase,
    PgQueryPerfSortSpillForBranchOrderSortSpillEvaluatorCase,
    PgQueryPerfSortSpillSimpleEvaluatorCase,
    PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase,
    PgQueryPerfStaleStatisticsForBranchOrderHotWindowSimpleEvaluatorCase,
    PgQueryPerfSuboptimalJoinForSalesReportRolePlannerDriftEvaluatorCase,
    PgQueryPerfSuboptimalJoinForDailyAccountSummaryEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from ...base import (
    PostgresCaseRuntime,
    PostgresScenario,
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    CaseResourceSpec,
    PostgresScenarioCase,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfParameterSniffingCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    deployment_cpus: float
    deployment_memory_mb: int
    deployment_shm_size: str
    table: str
    stmt_name: str
    hot_year: int
    rare_year: int
    slow_queries: tuple[str, ...]
    fault_fingerprint_sql: str
    start_fingerprint_probe: bool
    support_index_variant: str

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfParameterSniffingForBranchOrderYearSkewScenarioCase(PgQueryPerfParameterSniffingCase):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfParameterSniffingForBranchOrderYearSkewSimpleScenarioCase(PgQueryPerfParameterSniffingCase):
    pass

_PGQUERYPERFPARAMETERSNIFFINGSCENARIO_CASE = PgQueryPerfParameterSniffingForBranchOrderYearSkewScenarioCase(
    case_id='branch_order_year_skew',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "customer 360 hot year query",
                    "entity": "branch_order_year_skew",
                    "evidence": [
                        "scripted diagnostic actions observed customer 360 hot year query"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "generic prepared plan reused under parameter skew",
                    "entity": "branch_order_year_skew",
                    "evidence": [
                        "scripted diagnostic actions observed generic prepared plan reused under parameter skew"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "hot year uses unsuitable cached plan",
                    "entity": "branch_order_year_skew",
                    "evidence": [
                        "scripted diagnostic actions observed hot year uses unsuitable cached plan"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "use a custom plan for the hot year"
            ],
            "verification": [
                "hot and rare parameters were rechecked"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgQueryPerfParameterSniffingForBranchOrderYearSkewEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcdsx:latest',
    workload_tag='tpcdsx',
    dataset_scale=1,
    deployment_cpus=1.0,
    deployment_memory_mb=512,
    deployment_shm_size='256m',
    title='Parameterized customer revenue report has regressed for high-volume bind values.',
    alert='Alert: customer 360 revenue segmentation dashboard latency is unstable. The report is usually fast for smaller historical cohorts, but the January-February 2001 customer segment now exceeds the dashboard SLO and dominates recent topsql mean/max latency. Diagnose the production query path from database evidence and restore the slow dashboard without changing report semantics.',
    initial_state={'status': 'degraded', 'report': 'customer_360_hot_year_slow'},
    expected_target={'status': 'recovered', 'report': 'customer_360_hot_year_fast'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=CaseResourceSpec(
        worker_physical_cores=1,
        worker_memory_mb=512,
        container_cpu_limit=1.0,
        container_memory_mb=512,
    )),
    table='branch_order_line',
    stmt_name='customer_360_segment_revenue',
    hot_year=2001,
    rare_year=1900,
    slow_queries=('EXECUTE customer_360_segment_revenue(2001);',),
    fault_fingerprint_sql=('\n'
 '/* customer_360: top_revenue_by_year_segmentation */\n'
 'WITH\n'
 'year_sales AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ss.bol_account_sk,\n'
 '        SUM(ss.bol_net_paid)   AS yearly_revenue,\n'
 '        SUM(ss.bol_net_profit) AS yearly_margin,\n'
 '        COUNT(*)              AS order_count,\n'
 '        COUNT(*) FILTER (WHERE ss.bol_net_paid > 100) AS big_order_count,\n'
 '        COUNT(*) FILTER (WHERE ss.bol_quantity > 5)   AS bulk_order_lines\n'
 '    FROM branch_order_line ss\n'
 '    JOIN calendar_day d ON d.cal_day_sk = ss.bol_sold_date_sk\n'
 '    WHERE d.cal_year = $1\n'
 '      AND d.cal_moy BETWEEN 1 AND 2\n'
 '      AND (\n'
 '          ($1 = 2001 AND ss.bol_sold_date_sk BETWEEN 2451911 AND 2451970)\n'
 '          OR\n'
 '          ($1 <> 2001 AND ss.bol_sold_date_sk BETWEEN 1 AND 60)\n'
 '      )\n'
 '    GROUP BY ss.bol_account_sk\n'
 '),\n'
 'customer_cohort AS MATERIALIZED (\n'
 '    SELECT\n'
 '        c.sa_account_sk,\n'
 '        c.sa_birth_country,\n'
 '        c.sa_preferred_flag,\n'
 '        CASE\n'
 "            WHEN c.sa_current_profile_sk IS NULL THEN 'unknown'\n"
 "            WHEN (c.sa_current_profile_sk % 3) = 0 THEN 'married'\n"
 "            ELSE 'single'\n"
 '        END AS cohort_segment,\n'
 '        ys.yearly_revenue,\n'
 '        ys.yearly_margin,\n'
 '        ys.order_count,\n'
 '        ys.big_order_count,\n'
 '        ys.bulk_order_lines\n'
 '    FROM year_sales ys\n'
 '    JOIN shopper_account c ON c.sa_account_sk = ys.bol_account_sk\n'
 '),\n'
 'qualified_top AS MATERIALIZED (\n'
 '    SELECT\n'
 '        cc.*,\n'
 '        PERCENT_RANK() OVER (ORDER BY cc.yearly_revenue DESC) AS revenue_pct,\n'
 '        NTILE(100) OVER (ORDER BY cc.yearly_revenue DESC) AS revenue_decile\n'
 '    FROM customer_cohort cc\n'
 '),\n'
 'channel_attribution AS MATERIALIZED (\n'
 '    SELECT\n'
 '        qt.sa_account_sk,\n'
 '        COALESCE(SUM(ws.dol_net_paid), 0)  AS web_revenue,\n'
 '        COALESCE(SUM(cs.aol_net_paid), 0)  AS catalog_revenue,\n'
 '        COUNT(DISTINCT ws.dol_order_number) AS web_orders,\n'
 '        COUNT(DISTINCT cs.aol_order_number) AS catalog_orders\n'
 '    FROM qualified_top qt\n'
 '    LEFT JOIN digital_order_line     ws ON ws.dol_bill_account_sk = qt.sa_account_sk\n'
 '                              AND ws.dol_sold_date_sk = 2451911\n'
 '    LEFT JOIN assisted_order_line cs ON cs.aol_bill_account_sk = qt.sa_account_sk\n'
 '                              AND cs.aol_sold_date_sk = 2451911\n'
 '    WHERE qt.revenue_decile <= 100\n'
 '    GROUP BY qt.sa_account_sk\n'
 ')\n'
 'SELECT\n'
 '    qt.cohort_segment,\n'
 '    qt.sa_preferred_flag,\n'
 '    COUNT(*)                                AS customer_count,\n'
 '    SUM(qt.yearly_revenue)                  AS cohort_revenue,\n'
 '    SUM(qt.yearly_margin)                   AS cohort_margin,\n'
 '    SUM(qt.big_order_count)                 AS cohort_big_orders,\n'
 '    SUM(qt.bulk_order_lines)                AS cohort_bulk_lines,\n'
 '    SUM(ca.web_revenue)                     AS cohort_web_revenue,\n'
 '    SUM(ca.catalog_revenue)                 AS cohort_catalog_revenue,\n'
 '    AVG(qt.revenue_pct)                     AS avg_revenue_pct,\n'
 '    AVG(qt.yearly_revenue / NULLIF(qt.order_count, 0)) AS avg_order_value\n'
 'FROM qualified_top qt\n'
 'JOIN channel_attribution ca ON ca.sa_account_sk = qt.sa_account_sk\n'
 'WHERE qt.revenue_decile <= 100\n'
 'GROUP BY qt.cohort_segment, qt.sa_preferred_flag\n'
 'ORDER BY cohort_revenue DESC, cohort_segment, qt.sa_preferred_flag\n'),
    start_fingerprint_probe=False,
    support_index_variant='full',
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.7,
        reference_run_ids=(
            "reference-65__pg_query_perf_parameter_sniffing__"
            "branch_order_year_skew__mock__r001",
        ),
    ),
)

_PGQUERYPERFPARAMETERSNIFFINGSCENARIO_SIMPLE_CASE = PgQueryPerfParameterSniffingForBranchOrderYearSkewSimpleScenarioCase(
    case_id='branch_order_year_skew_simple',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "hot and rare year cardinality skew",
                    "entity": "branch_order_year_skew_simple",
                    "evidence": [
                        "scripted diagnostic actions observed hot and rare year cardinality skew"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "generic prepared plan reused",
                    "entity": "branch_order_year_skew_simple",
                    "evidence": [
                        "scripted diagnostic actions observed generic prepared plan reused"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "parameter sniffing plan mismatch",
                    "entity": "branch_order_year_skew_simple",
                    "evidence": [
                        "scripted diagnostic actions observed parameter sniffing plan mismatch"
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
    case_no=1,
    evaluator=PgQueryPerfParameterSniffingForBranchOrderYearSkewSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcdsx:latest',
    workload_tag='tpcdsx',
    dataset_scale=1,
    deployment_cpus=1.0,
    deployment_memory_mb=512,
    deployment_shm_size='256m',
    title='A compact customer revenue lookup regresses for one high-volume bind value.',
    alert='Alert: the customer revenue lookup is slow only for the January-February 2001 cohort. The same prepared report is fast for an empty historical cohort. Diagnose the database-side cause and restore the report without changing its result.',
    initial_state={'status': 'degraded', 'report': 'customer_revenue_lookup_slow'},
    expected_target={'status': 'recovered', 'report': 'customer_revenue_lookup_fast'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=CaseResourceSpec(
        worker_physical_cores=1,
        worker_memory_mb=512,
        container_cpu_limit=1.0,
        container_memory_mb=512,
    )),
    table='branch_order_line',
    stmt_name='customer_revenue_lookup',
    hot_year=2001,
    rare_year=1900,
    slow_queries=('EXECUTE customer_revenue_lookup(2001);',),
    fault_fingerprint_sql=(
        '/* customer_revenue_lookup: bind-sensitive revenue total */ '
        'SELECT d.cal_year, COUNT(*) AS order_lines, '
        'SUM(b.bol_net_paid) AS revenue '
        'FROM branch_order_line b '
        'JOIN calendar_day d ON d.cal_day_sk = b.bol_sold_date_sk '
        'WHERE d.cal_year = $1 AND d.cal_moy BETWEEN 1 AND 2 '
        'AND (($1 = 2001 AND b.bol_sold_date_sk BETWEEN 2451911 AND 2451970) '
        'OR ($1 <> 2001 AND b.bol_sold_date_sk BETWEEN 1 AND 60)) '
        'GROUP BY d.cal_year'
    ),
    start_fingerprint_probe=False,
    support_index_variant='hot_window_partial',
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.25,
        reference_run_ids=('mock-branch_order_year_skew_simple-v1',),
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

class PgQueryPerfParameterSniffingInjector(BaseFaultInjector, PgQueryPerfFaultFingerprintProbe):
    """
    模拟"参数嗅探与执行计划退化"故障。
    利用 PostgreSQL 的 Prepared Statement 机制：
    在 tpcdsx customer_360 报表上利用年份绑定值分布差异：
    1. 稀有年份几乎无事实表行，执行很快
    2. 热点年份命中大量 branch_order_line 行
    3. 场景会话固定使用 generic plan，使热点参数复用不适合高选择率的计划
    """

    SUPPORT_INDEX_VARIANTS = {
        "full": (
            "idx_aiopsbench_branch_order_line_date_account_branch",
            "CREATE INDEX IF NOT EXISTS idx_aiopsbench_branch_order_line_date_account_branch "
            "ON branch_order_line (bol_sold_date_sk, bol_account_sk, bol_branch_sk, bol_product_sk) "
            "INCLUDE (bol_net_paid, bol_net_profit, bol_quantity);",
        ),
        "hot_window_partial": (
            "idx_aiopsbench_worker_hot_date",
            "CREATE INDEX idx_aiopsbench_worker_hot_date "
            "ON branch_order_line (bol_sold_date_sk) INCLUDE (bol_net_paid) "
            "WHERE bol_sold_date_sk BETWEEN 2451911 AND 2451970;",
        ),
    }

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._verify_persistent_state()
            self._activate_runtime()

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._install_persistent_state()
            self._activate_runtime()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(str(config["table"]), "table")
        self.stmt_name = _validate_sql_identifier(str(config["stmt_name"]), "stmt_name")
        self.hot_year = int(config["hot_year"])
        self.rare_year = int(config["rare_year"])
        self.fault_fingerprint_sql = str(config["fault_fingerprint_sql"])
        self.start_fingerprint_probe = bool(config["start_fingerprint_probe"])
        self.support_index_variant = str(config["support_index_variant"])
        if self.support_index_variant not in self.SUPPORT_INDEX_VARIANTS:
            raise ValueError(
                "Unsupported parameter-sniffing support index variant: "
                f"variant={self.support_index_variant!r}, "
                f"supported={sorted(self.SUPPORT_INDEX_VARIANTS)}"
            )
        self.support_index_name, self.support_index_sql = self.SUPPORT_INDEX_VARIANTS[
            self.support_index_variant
        ]

    def _install_persistent_state(self) -> None:
        print(f"[FaultInjector:PgQueryPerfParameterSniffingInjector] Injecting parameter sniffing fault...")
        if not self.env.reconnect():
            raise RuntimeError(
                "Parameter-sniffing install could not establish the scenario SQL session: "
                f"host={self.env.host!r}, port={self.env.port!r}, dbname={self.env.dbname!r}"
            )
        self._execute_checked(
            "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;",
            "install pg_stat_statements for parameter-sniffing scenario",
        )
        self._ensure_tpcdsx_support()

    def _verify_persistent_state(self) -> None:
        self._execute_checked(
            """
            DO $aiopsbench$
            DECLARE
                missing_object text;
            BEGIN
                SELECT object_name INTO missing_object
                FROM unnest(ARRAY[
                    'branch_order_line',
                    'digital_order_line',
                    'assisted_order_line',
                    '{self.support_index_name}',
                    'idx_aiopsbench_calendar_day_year_day',
                    'idx_aiopsbench_shopper_account_demo',
                    'idx_aiopsbench_digital_order_line_bill_account',
                    'idx_aiopsbench_assisted_order_line_bill_account'
                ]) AS required(object_name)
                WHERE to_regclass('public.' || object_name) IS NULL
                LIMIT 1;
                IF missing_object IS NOT NULL THEN
                    RAISE EXCEPTION 'parameter-sniffing fault image is missing object %', missing_object;
                END IF;
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_extension
                    WHERE extname = 'pg_stat_statements'
                ) THEN
                    RAISE EXCEPTION 'parameter-sniffing fault image is missing pg_stat_statements';
                END IF;
                IF EXISTS (
                    SELECT 1
                    FROM unnest(ARRAY[
                        'branch_order_line',
                        'digital_order_line',
                        'assisted_order_line'
                    ]) AS required(table_name)
                    JOIN pg_class c ON c.oid = to_regclass('public.' || required.table_name)
                    WHERE NOT COALESCE(
                        'autovacuum_enabled=false' = ANY (c.reloptions),
                        false
                    )
                ) THEN
                    RAISE EXCEPTION 'parameter-sniffing fault image lost an autovacuum setting';
                END IF;
            END
            $aiopsbench$;
            """,
            "verify parameter-sniffing fault image state",
        )

    def _activate_runtime(self) -> None:
        if not self.env.reconnect():
            raise RuntimeError(
                "Parameter-sniffing activation could not establish the scenario SQL session: "
                f"host={self.env.host!r}, port={self.env.port!r}, dbname={self.env.dbname!r}"
            )
        self._execute_checked(
            "SET plan_cache_mode = 'force_generic_plan';",
            "force a generic plan in the parameter-sniffing session",
        )
        self._prepare_decoy_statements()
        self._execute_checked(
            f"PREPARE {self.stmt_name}(int) AS {self.fault_fingerprint_sql.rstrip(';')};",
            f"prepare parameter-sniffing statement {self.stmt_name}",
        )

        print(f"[FaultInjector:PgQueryPerfParameterSniffingInjector] Executing low-volume year...")
        for _ in range(6):
            self._execute_checked(
                f"EXECUTE {self.stmt_name}({self.rare_year});",
                f"prime parameter-sniffing statement with rare_year={self.rare_year}",
            )

        print(f"[FaultInjector:PgQueryPerfParameterSniffingInjector] Executing high-volume year...")
        import time
        start = time.monotonic()
        self._execute_checked(
            f"EXECUTE {self.stmt_name}({self.hot_year});",
            f"execute parameter-sniffing statement with hot_year={self.hot_year}",
        )
        self.fault_query_seconds = time.monotonic() - start

        self.plan_mode = self._execute_checked(
            "SHOW plan_cache_mode;",
            "read parameter-sniffing plan_cache_mode",
        )
        self.prepared_statements = self._execute_checked(
            "SELECT name, generic_plans, custom_plans, statement "
            "FROM pg_prepared_statements ORDER BY name;",
            "read parameter-sniffing prepared statements",
        )
        self.fault_plan = self._execute_checked(
            f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
            f"EXECUTE {self.stmt_name}({self.hot_year});",
            "verify parameter-sniffing fault plan",
        )
        self._assert_parameter_sniffing_fault(
            self.plan_mode,
            self.prepared_statements,
            self.fault_plan,
        )

        print(f"[FaultInjector:PgQueryPerfParameterSniffingInjector] Fault injection complete.")
        if self.start_fingerprint_probe and self._env_supports_background_probe():
            self._start_fault_fingerprint_probe(
                sql=self.fault_fingerprint_sql,
                app_name="aiopsbench_fp_param_sniffing",
                bind_year=self.hot_year,
            )

    def _prepare_decoy_statements(self) -> None:
        for name, sql in (
            ("regional_revenue_snapshot", """
            PREPARE regional_revenue_snapshot(int) AS
            SELECT d.cal_moy, SUM(bol.bol_net_paid) AS revenue, COUNT(*) AS lines
            FROM branch_order_line bol
            JOIN calendar_day d ON d.cal_day_sk = bol.bol_sold_date_sk
            WHERE d.cal_year = $1
              AND d.cal_moy BETWEEN 1 AND 2
            GROUP BY d.cal_moy
            ORDER BY revenue DESC;
            """),
            ("loyalty_segment_rollup", """
            PREPARE loyalty_segment_rollup(int) AS
            SELECT sa.sa_preferred_flag, COUNT(*) AS accounts, SUM(bol.bol_net_paid) AS revenue
            FROM branch_order_line bol
            JOIN shopper_account sa ON sa.sa_account_sk = bol.bol_account_sk
            JOIN calendar_day d ON d.cal_day_sk = bol.bol_sold_date_sk
            WHERE d.cal_year = $1
              AND d.cal_moy BETWEEN 1 AND 2
            GROUP BY sa.sa_preferred_flag;
            """),
            ("digital_channel_closeout", """
            PREPARE digital_channel_closeout(int) AS
            SELECT d.cal_moy, COUNT(*) AS orders, SUM(dol.dol_net_paid) AS revenue
            FROM digital_order_line dol
            JOIN calendar_day d ON d.cal_day_sk = dol.dol_sold_date_sk
            WHERE d.cal_year = $1
              AND d.cal_moy BETWEEN 1 AND 2
            GROUP BY d.cal_moy
            ORDER BY d.cal_moy;
            """),
            ("assisted_channel_closeout", """
            PREPARE assisted_channel_closeout(int) AS
            SELECT d.cal_moy, COUNT(*) AS orders, SUM(aol.aol_net_paid) AS revenue
            FROM assisted_order_line aol
            JOIN calendar_day d ON d.cal_day_sk = aol.aol_sold_date_sk
            WHERE d.cal_year = $1
              AND d.cal_moy BETWEEN 1 AND 2
            GROUP BY d.cal_moy
            ORDER BY d.cal_moy;
            """),
        ):
            self._execute_checked(sql, f"prepare parameter-sniffing decoy {name}")

    def _ensure_tpcdsx_support(self) -> None:
        if self.table != "branch_order_line":
            raise ValueError(
                "PgQueryPerfParameterSniffingInjector supports tpcdsx branch_order_line only, "
                f"got {self.table!r}."
            )
        for table in ("branch_order_line", "digital_order_line", "assisted_order_line"):
            self._execute_checked(
                f"ALTER TABLE {table} SET (autovacuum_enabled = false);",
                f"disable autovacuum on parameter-sniffing table {table}",
            )
        self._execute_checked(
            self.support_index_sql,
            f"install parameter-sniffing branch order index {self.support_index_name}",
        )
        self._execute_checked(
            "CREATE INDEX IF NOT EXISTS idx_aiopsbench_calendar_day_year_day "
            "ON calendar_day (cal_year, cal_day_sk);",
            "install parameter-sniffing calendar index",
        )
        self._execute_checked(
            "CREATE INDEX IF NOT EXISTS idx_aiopsbench_shopper_account_demo "
            "ON shopper_account (sa_account_sk, sa_current_profile_sk) "
            "INCLUDE (sa_birth_country, sa_preferred_flag);",
            "install parameter-sniffing shopper account index",
        )
        self._execute_checked(
            "CREATE INDEX IF NOT EXISTS idx_aiopsbench_digital_order_line_bill_account "
            "ON digital_order_line (dol_bill_account_sk, dol_sold_date_sk) "
            "INCLUDE (dol_net_paid, dol_order_number);",
            "install parameter-sniffing digital order index",
        )
        self._execute_checked(
            "CREATE INDEX IF NOT EXISTS idx_aiopsbench_assisted_order_line_bill_account "
            "ON assisted_order_line (aol_bill_account_sk, aol_sold_date_sk) "
            "INCLUDE (aol_net_paid, aol_order_number);",
            "install parameter-sniffing assisted order index",
        )

    def _execute_checked(self, sql: str, context: str):
        return _require_sql_success(self.env.execute_sql(sql), context)

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._execute_checked(
            "SELECT pg_stat_statements_reset();",
            "reset parameter-sniffing query history",
        )
        env.refresh_pgss_baseline()
        seed_sqls = (
            f"EXECUTE regional_revenue_snapshot({self.hot_year});",
            f"EXECUTE loyalty_segment_rollup({self.hot_year});",
            f"EXECUTE digital_channel_closeout({self.hot_year});",
            f"EXECUTE assisted_channel_closeout({self.hot_year});",
            f"EXECUTE {self.stmt_name}({self.rare_year});",
            f"EXECUTE {self.stmt_name}({self.rare_year});",
            f"EXECUTE {self.stmt_name}({self.hot_year});",
            f"EXECUTE {self.stmt_name}({self.hot_year});",
        )
        seed_results = [
            self._execute_checked(sql, f"seed parameter-sniffing business query {sql}")
            for sql in seed_sqls
        ]
        evidence = self._query_observability_evidence(env)
        self._assert_parameter_sniffing_topsql(evidence["topsql"])
        evidence.update({
            "fault_query_seconds": self.fault_query_seconds,
            "seed_results": seed_results,
            "plan_mode": self.plan_mode,
            "prepared_statements": self.prepared_statements,
            "fault_plan": self.fault_plan,
            "support_index_variant": self.support_index_variant,
            "support_index_name": self.support_index_name,
        })
        return evidence

    def _assert_parameter_sniffing_fault(
        self,
        plan_mode,
        prepared_statements,
        fault_plan,
    ) -> None:
        mode_text = json.dumps(plan_mode, ensure_ascii=False, default=str).lower()
        if "force_generic_plan" not in mode_text:
            raise RuntimeError(
                f"Parameter-sniffing session is not using force_generic_plan: {plan_mode}"
            )

        prepared_rows = _json_object(
            prepared_statements,
            "read parameter-sniffing prepared statement rows",
        ).get("result", [])
        target_rows = [row for row in prepared_rows if row and row[0] == self.stmt_name]
        if len(target_rows) != 1 or len(target_rows[0]) < 4:
            raise RuntimeError(
                "Parameter-sniffing prepared statement is not observable with plan counters: "
                f"statement={self.stmt_name}, prepared={prepared_statements}"
            )
        if int(target_rows[0][1]) <= 0:
            raise RuntimeError(
                "Parameter-sniffing target statement has not used a generic plan: "
                f"statement={self.stmt_name}, row={target_rows[0]}"
            )

        plan_text = json.dumps(fault_plan, ensure_ascii=False, default=str).lower()
        if "branch_order_line" not in plan_text or "calendar_day" not in plan_text:
            raise RuntimeError(
                "Parameter-sniffing fault plan does not contain the complete report path: "
                f"plan={fault_plan}"
            )

    def _assert_parameter_sniffing_topsql(self, topsql) -> None:
        topsql_payload = _json_object(topsql, "read parameter-sniffing topsql")
        values = topsql_payload.get("records", [])
        topsql_text = json.dumps(values, ensure_ascii=False, default=str).lower()
        target_marker = (
            "customer_360"
            if self.stmt_name.lower().startswith("customer_360")
            else self.stmt_name.lower()
        )
        if target_marker not in topsql_text or "branch_order_line" not in topsql_text:
            raise RuntimeError(
                f"Parameter-sniffing target report is not visible in topsql: {topsql}"
            )
        target_calls = sum(
            int(entry.get("calls") or 0)
            for entry in values
            if isinstance(entry, dict)
            and target_marker in str(entry.get("query", "")).lower()
            and "branch_order_line" in str(entry.get("query", "")).lower()
        )
        if target_calls < 4:
            raise RuntimeError(
                "Parameter-sniffing topsql does not contain the complete seeded bind workload: "
                f"calls={target_calls}, expected_at_least=4, topsql={topsql}"
            )

    def quiesce(self, context: FaultLifecycleContext):
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_param_sniffing")

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        self._configure(context.config, env)
        print(f"[FaultInjector:PgQueryPerfParameterSniffingInjector] Recovering...")
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_param_sniffing")
        if not env.reconnect():
            raise RuntimeError(
                f"Parameter-sniffing recovery could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        _require_sql_success(
            env.execute_sql(
                "DEALLOCATE ALL; SET plan_cache_mode = 'auto';"
            ),
            "restore parameter-sniffing session plan_cache_mode",
        )
        _require_sql_success(
            env.execute_sql("ALTER SYSTEM SET plan_cache_mode = 'auto';"),
            "restore parameter-sniffing system plan_cache_mode",
        )
        _require_sql_success(
            env.execute_sql("SELECT pg_reload_conf();"),
            "reload parameter-sniffing plan_cache_mode",
        )
        for table in ("branch_order_line", "digital_order_line", "assisted_order_line"):
            _require_sql_success(
                env.execute_sql(f"ALTER TABLE {table} RESET (autovacuum_enabled);"),
                f"restore parameter-sniffing autovacuum for {table}",
            )
        print(f"[FaultInjector:PgQueryPerfParameterSniffingInjector] Recovery complete.")


class PgQueryPerfParameterSniffingScenario(PostgresScenario):
    scenario_id = 'pg_query_perf_parameter_sniffing'
    description = 'Parameterized customer revenue report has regressed for high-volume bind values.'
    cases = (
        _PGQUERYPERFPARAMETERSNIFFINGSCENARIO_CASE,
        _PGQUERYPERFPARAMETERSNIFFINGSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgQueryPerfParameterSniffingCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgQueryPerfParameterSniffingInjector,
                config={
                    'table': case.table,
                    'stmt_name': case.stmt_name,
                    'hot_year': case.hot_year,
                    'rare_year': case.rare_year,
                    'fault_fingerprint_sql': case.fault_fingerprint_sql,
                    'start_fingerprint_probe': case.start_fingerprint_probe,
                    'support_index_variant': case.support_index_variant,
                },
            ),
        )
