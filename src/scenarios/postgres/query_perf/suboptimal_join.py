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
from src.execution.specs import PostgresCaseRuntime, CaseResourceSpec
from src.scenarios.base import PostgresScenario, DifficultyCalibration, FaultPlan, PostgresScenarioCase
from src.workloads.specs import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    EMPTY_BACKGROUND_WORKLOAD,
)


QUERY_PERF_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfSuboptimalJoinCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    deployment_cpus: float
    deployment_memory_mb: int
    deployment_shm_size: str
    table: str
    app_role: str
    app_password: str
    fault_enable_hashjoin: str
    fault_enable_mergejoin: str
    support_index: str
    create_account_first_index: bool
    minimum_slowdown_seconds: float
    minimum_slowdown_ratio: float
    warm_plans_before_measurement: bool
    fault_disable_memoize: bool
    start_fingerprint_probe: bool
    fault_fingerprint_sql: str
    slow_queries: tuple[str, ...]

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfSuboptimalJoinForSalesReportRolePlannerDriftScenarioCase(PgQueryPerfSuboptimalJoinCase):
    pass

class PgQueryPerfSuboptimalJoinForDailyAccountSummaryScenarioCase(PgQueryPerfSuboptimalJoinCase):
    pass

_PGQUERYPERFSUBOPTIMALJOINSCENARIO_CASE = PgQueryPerfSuboptimalJoinForSalesReportRolePlannerDriftScenarioCase(
    case_id='sales_report_role_planner_drift',
    runtime=PostgresCaseRuntime(resources=QUERY_PERF_RESOURCES),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "branch account margin report",
                    "entity": "sales_report_role_planner_drift",
                    "evidence": [
                        "scripted diagnostic actions observed branch account margin report"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "role disables hashjoin and mergejoin",
                    "entity": "sales_report_role_planner_drift",
                    "evidence": [
                        "scripted diagnostic actions observed role disables hashjoin and mergejoin"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "suboptimal nested loop join",
                    "entity": "sales_report_role_planner_drift",
                    "evidence": [
                        "scripted diagnostic actions observed suboptimal nested loop join"
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
    evaluator=PgQueryPerfSuboptimalJoinForSalesReportRolePlannerDriftEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcdsx:latest',
    workload_tag='tpcdsx',
    dataset_scale=1,
    deployment_cpus=1.0,
    deployment_memory_mb=256,
    deployment_shm_size='128m',
    title='Simulates suboptimal join method regression from role-level planner setting drift.',
    alert='Alert: the branch account margin report has slowed from ~2s to over 30s since this morning. CPU and read I/O rise during the report, while row counts, application SQL, and visible indexes have not changed. Identify the database-side cause and provide a verifiable fix.\n\nAffected query:\n\n/* crm_reporting: branch_account_margin_v3_with_decile */\nWITH\norder_lines AS MATERIALIZED (\n    SELECT\n        ol.bol_account_sk,\n        ol.bol_branch_sk,\n        ol.bol_sold_date_sk,\n        ol.bol_product_sk,\n        ol.bol_net_paid,\n        ol.bol_net_profit\n    FROM branch_order_line ol\n    WHERE ol.bol_sold_date_sk BETWEEN 2451911 AND 2451925\n),\naccount_segments AS MATERIALIZED (\n    SELECT\n        acct.sa_account_sk,\n        acct.sa_current_addr_sk,\n        acct.sa_preferred_flag,\n        acct.sa_birth_country\n    FROM shopper_account acct\n    WHERE acct.sa_account_sk BETWEEN 1 AND 15000\n),\nqualified_orders AS MATERIALIZED (\n    SELECT\n        seg.sa_account_sk,\n        seg.sa_preferred_flag,\n        seg.sa_birth_country,\n        ord.bol_branch_sk,\n        ord.bol_sold_date_sk,\n        ord.bol_product_sk,\n        prod.pr_category,\n        prod.pr_brand,\n        ord.bol_net_paid,\n        ord.bol_net_profit\n    FROM account_segments seg\n    JOIN account_address addr ON addr.aa_address_sk = seg.sa_current_addr_sk\n    JOIN branch br ON br.br_state = addr.aa_state\n    JOIN order_lines ord ON ord.bol_account_sk = seg.sa_account_sk\n                         AND ord.bol_branch_sk = br.br_branch_sk\n    JOIN product prod ON prod.pr_product_sk = ord.bol_product_sk\n    JOIN calendar_day cal ON cal.cal_day_sk = ord.bol_sold_date_sk\n                         AND cal.cal_year = 2001\n),\naccount_profit AS MATERIALIZED (\n    SELECT\n        qo.sa_account_sk,\n        qo.sa_preferred_flag,\n        qo.sa_birth_country,\n        qo.pr_category,\n        qo.pr_brand,\n        SUM(qo.bol_net_paid)   AS total_revenue,\n        SUM(qo.bol_net_profit) AS total_profit,\n        COUNT(*)               AS line_count,\n        NTILE(100) OVER (ORDER BY SUM(qo.bol_net_profit) DESC) AS profit_decile,\n        ROW_NUMBER() OVER (\n            PARTITION BY qo.pr_category\n            ORDER BY SUM(qo.bol_net_profit) DESC, qo.sa_account_sk\n        ) AS category_rank\n    FROM qualified_orders qo\n    GROUP BY qo.sa_account_sk, qo.sa_preferred_flag, qo.sa_birth_country, qo.pr_category, qo.pr_brand\n)\nSELECT\n    ap.sa_account_sk,\n    ap.sa_preferred_flag,\n    ap.sa_birth_country,\n    ap.pr_category,\n    ap.pr_brand,\n    ap.total_revenue,\n    ap.total_profit,\n    ap.line_count,\n    ap.profit_decile,\n    ap.category_rank,\n    (\n        SELECT MAX(dol.dol_net_paid)\n        FROM digital_order_line dol\n        WHERE dol.dol_bill_account_sk = ap.sa_account_sk\n    ) AS max_digital_order,\n    (\n        SELECT COUNT(DISTINCT aol.aol_order_number)\n        FROM assisted_order_line aol\n        WHERE aol.aol_bill_account_sk = ap.sa_account_sk\n    ) AS assisted_order_count\nFROM account_profit ap\nWHERE ap.profit_decile <= 10\n  AND ap.category_rank <= 50\nORDER BY ap.total_profit DESC, ap.sa_account_sk\nLIMIT 50\n\n\nHint: compare the current execution plan with the expected shape for this multi-stage report.',
    initial_state={'status': 'degraded',
 'app_role': 'sales_report_app',
 'role_enable_hashjoin': 'off',
 'role_enable_mergejoin': 'off',
 'join_method': 'suboptimal'},
    expected_target={'status': 'recovered',
 'app_role': 'sales_report_app',
 'join_method': 'optimal'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table='branch_order_line',
    app_role='sales_report_app',
    app_password='aiopsbench',
    fault_enable_hashjoin='off',
    fault_enable_mergejoin='off',
    support_index='idx_aiopsbench_branch_order_line_account_date_branch_product',
    create_account_first_index=True,
    minimum_slowdown_seconds=1.0,
    minimum_slowdown_ratio=1.30,
    warm_plans_before_measurement=False,
    fault_disable_memoize=False,
    start_fingerprint_probe=True,
    fault_fingerprint_sql=('\n'
 '/* crm_reporting: branch_account_margin_v3_with_decile */\n'
 'WITH\n'
 'order_lines AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ol.bol_account_sk,\n'
 '        ol.bol_branch_sk,\n'
 '        ol.bol_sold_date_sk,\n'
 '        ol.bol_product_sk,\n'
 '        ol.bol_net_paid,\n'
 '        ol.bol_net_profit\n'
 '    FROM branch_order_line ol\n'
 '    WHERE ol.bol_sold_date_sk BETWEEN 2451911 AND 2451925\n'
 '),\n'
 'account_segments AS MATERIALIZED (\n'
 '    SELECT\n'
 '        acct.sa_account_sk,\n'
 '        acct.sa_current_addr_sk,\n'
 '        acct.sa_preferred_flag,\n'
 '        acct.sa_birth_country\n'
 '    FROM shopper_account acct\n'
 '    WHERE acct.sa_account_sk BETWEEN 1 AND 15000\n'
 '),\n'
 'qualified_orders AS MATERIALIZED (\n'
 '    SELECT\n'
 '        seg.sa_account_sk,\n'
 '        seg.sa_preferred_flag,\n'
 '        seg.sa_birth_country,\n'
 '        ord.bol_branch_sk,\n'
 '        ord.bol_sold_date_sk,\n'
 '        ord.bol_product_sk,\n'
 '        prod.pr_category,\n'
 '        prod.pr_brand,\n'
 '        ord.bol_net_paid,\n'
 '        ord.bol_net_profit\n'
 '    FROM account_segments seg\n'
 '    JOIN account_address addr ON addr.aa_address_sk = seg.sa_current_addr_sk\n'
 '    JOIN branch br ON br.br_state = addr.aa_state\n'
 '    JOIN order_lines ord ON ord.bol_account_sk = seg.sa_account_sk\n'
 '                         AND ord.bol_branch_sk = br.br_branch_sk\n'
 '    JOIN product prod ON prod.pr_product_sk = ord.bol_product_sk\n'
 '    JOIN calendar_day cal ON cal.cal_day_sk = ord.bol_sold_date_sk\n'
 '                         AND cal.cal_year = 2001\n'
 '),\n'
 'account_profit AS MATERIALIZED (\n'
 '    SELECT\n'
 '        qo.sa_account_sk,\n'
 '        qo.sa_preferred_flag,\n'
 '        qo.sa_birth_country,\n'
 '        qo.pr_category,\n'
 '        qo.pr_brand,\n'
 '        SUM(qo.bol_net_paid)   AS total_revenue,\n'
 '        SUM(qo.bol_net_profit) AS total_profit,\n'
 '        COUNT(*)               AS line_count,\n'
 '        NTILE(100) OVER (ORDER BY SUM(qo.bol_net_profit) DESC) AS profit_decile,\n'
 '        ROW_NUMBER() OVER (\n'
 '            PARTITION BY qo.pr_category\n'
 '            ORDER BY SUM(qo.bol_net_profit) DESC, qo.sa_account_sk\n'
 '        ) AS category_rank\n'
 '    FROM qualified_orders qo\n'
 '    GROUP BY qo.sa_account_sk, qo.sa_preferred_flag, qo.sa_birth_country, qo.pr_category, '
 'qo.pr_brand\n'
 ')\n'
 'SELECT\n'
 '    ap.sa_account_sk,\n'
 '    ap.sa_preferred_flag,\n'
 '    ap.sa_birth_country,\n'
 '    ap.pr_category,\n'
 '    ap.pr_brand,\n'
 '    ap.total_revenue,\n'
 '    ap.total_profit,\n'
 '    ap.line_count,\n'
 '    ap.profit_decile,\n'
 '    ap.category_rank,\n'
 '    (\n'
 '        SELECT MAX(dol.dol_net_paid)\n'
 '        FROM digital_order_line dol\n'
 '        WHERE dol.dol_bill_account_sk = ap.sa_account_sk\n'
 '    ) AS max_digital_order,\n'
 '    (\n'
 '        SELECT COUNT(DISTINCT aol.aol_order_number)\n'
 '        FROM assisted_order_line aol\n'
 '        WHERE aol.aol_bill_account_sk = ap.sa_account_sk\n'
 '    ) AS assisted_order_count\n'
 'FROM account_profit ap\n'
 'WHERE ap.profit_decile <= 10\n'
 '  AND ap.category_rank <= 50\n'
 'ORDER BY ap.total_profit DESC, ap.sa_account_sk\n'
 'LIMIT 50\n'),
    slow_queries=('\n'
 '/* crm_reporting: branch_account_margin_v3_with_decile */\n'
 'WITH\n'
 'order_lines AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ol.bol_account_sk,\n'
 '        ol.bol_branch_sk,\n'
 '        ol.bol_sold_date_sk,\n'
 '        ol.bol_product_sk,\n'
 '        ol.bol_net_paid,\n'
 '        ol.bol_net_profit\n'
 '    FROM branch_order_line ol\n'
 '    WHERE ol.bol_sold_date_sk BETWEEN 2451911 AND 2451925\n'
 '),\n'
 'account_segments AS MATERIALIZED (\n'
 '    SELECT\n'
 '        acct.sa_account_sk,\n'
 '        acct.sa_current_addr_sk,\n'
 '        acct.sa_preferred_flag,\n'
 '        acct.sa_birth_country\n'
 '    FROM shopper_account acct\n'
 '    WHERE acct.sa_account_sk BETWEEN 1 AND 15000\n'
 '),\n'
 'qualified_orders AS MATERIALIZED (\n'
 '    SELECT\n'
 '        seg.sa_account_sk,\n'
 '        seg.sa_preferred_flag,\n'
 '        seg.sa_birth_country,\n'
 '        ord.bol_branch_sk,\n'
 '        ord.bol_sold_date_sk,\n'
 '        ord.bol_product_sk,\n'
 '        prod.pr_category,\n'
 '        prod.pr_brand,\n'
 '        ord.bol_net_paid,\n'
 '        ord.bol_net_profit\n'
 '    FROM account_segments seg\n'
 '    JOIN account_address addr ON addr.aa_address_sk = seg.sa_current_addr_sk\n'
 '    JOIN branch br ON br.br_state = addr.aa_state\n'
 '    JOIN order_lines ord ON ord.bol_account_sk = seg.sa_account_sk\n'
 '                         AND ord.bol_branch_sk = br.br_branch_sk\n'
 '    JOIN product prod ON prod.pr_product_sk = ord.bol_product_sk\n'
 '    JOIN calendar_day cal ON cal.cal_day_sk = ord.bol_sold_date_sk\n'
 '                         AND cal.cal_year = 2001\n'
 '),\n'
 'account_profit AS MATERIALIZED (\n'
 '    SELECT\n'
 '        qo.sa_account_sk,\n'
 '        qo.sa_preferred_flag,\n'
 '        qo.sa_birth_country,\n'
 '        qo.pr_category,\n'
 '        qo.pr_brand,\n'
 '        SUM(qo.bol_net_paid)   AS total_revenue,\n'
 '        SUM(qo.bol_net_profit) AS total_profit,\n'
 '        COUNT(*)               AS line_count,\n'
 '        NTILE(100) OVER (ORDER BY SUM(qo.bol_net_profit) DESC) AS profit_decile,\n'
 '        ROW_NUMBER() OVER (\n'
 '            PARTITION BY qo.pr_category\n'
 '            ORDER BY SUM(qo.bol_net_profit) DESC, qo.sa_account_sk\n'
 '        ) AS category_rank\n'
 '    FROM qualified_orders qo\n'
 '    GROUP BY qo.sa_account_sk, qo.sa_preferred_flag, qo.sa_birth_country, qo.pr_category, '
 'qo.pr_brand\n'
 ')\n'
 'SELECT\n'
 '    ap.sa_account_sk,\n'
 '    ap.sa_preferred_flag,\n'
 '    ap.sa_birth_country,\n'
 '    ap.pr_category,\n'
 '    ap.pr_brand,\n'
 '    ap.total_revenue,\n'
 '    ap.total_profit,\n'
 '    ap.line_count,\n'
 '    ap.profit_decile,\n'
 '    ap.category_rank,\n'
 '    (\n'
 '        SELECT MAX(dol.dol_net_paid)\n'
 '        FROM digital_order_line dol\n'
 '        WHERE dol.dol_bill_account_sk = ap.sa_account_sk\n'
 '    ) AS max_digital_order,\n'
 '    (\n'
 '        SELECT COUNT(DISTINCT aol.aol_order_number)\n'
 '        FROM assisted_order_line aol\n'
 '        WHERE aol.aol_bill_account_sk = ap.sa_account_sk\n'
 '    ) AS assisted_order_count\n'
 'FROM account_profit ap\n'
 'WHERE ap.profit_decile <= 10\n'
 '  AND ap.category_rank <= 50\n'
 'ORDER BY ap.total_profit DESC, ap.sa_account_sk\n'
 'LIMIT 50\n',),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.6,
        reference_run_ids=(
            "reference-61__pg_query_perf_suboptimal_join__"
            "sales_report_role_planner_drift__mock__r001",
        ),
    ),
)

_DAILY_ACCOUNT_SUMMARY_SQL = """
/* crm_reporting: daily_account_summary_v1 */
SELECT
    COUNT(DISTINCT acct.sa_account_sk) AS active_accounts,
    COUNT(*) AS order_line_count,
    SUM(ol.bol_net_paid) AS revenue
FROM shopper_account acct
JOIN branch_order_line ol
  ON ol.bol_account_sk = acct.sa_account_sk
WHERE ol.bol_sold_date_sk BETWEEN 2451911 AND 2451970
  AND acct.sa_account_sk BETWEEN 1 AND 100000
"""

_PGQUERYPERFSUBOPTIMALJOINSCENARIO_SIMPLE_CASE = PgQueryPerfSuboptimalJoinForDailyAccountSummaryScenarioCase(
    case_id="daily_account_summary_planner_drift",
    runtime=PostgresCaseRuntime(resources=QUERY_PERF_RESOURCES),
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [],
            "verification": []
        },
        "summary": "No diagnosis or remediation was attempted."
    },
    case_no=1,
    evaluator=PgQueryPerfSuboptimalJoinForDailyAccountSummaryEvaluatorCase,
    base_image_name="aiopsbench-pg-tpcdsx:latest",
    workload_tag="tpcdsx",
    dataset_scale=1,
    deployment_cpus=1.0,
    deployment_memory_mb=256,
    deployment_shm_size="128m",
    title="Simulates a smaller daily account summary slowed by role-level join planner drift.",
    alert=(
        "Alert: the daily account summary has slowed and read I/O increased, while row "
        "counts and indexes are unchanged. Inspect the affected query plan and database "
        "configuration, then provide a verifiable fix.\n\nAffected query:\n\n"
        + _DAILY_ACCOUNT_SUMMARY_SQL
    ),
    initial_state={
        "status": "degraded",
        "app_role": "sales_report_app",
        "role_enable_hashjoin": "off",
        "role_enable_mergejoin": "off",
        "join_method": "suboptimal",
    },
    expected_target={
        "status": "recovered",
        "app_role": "sales_report_app",
        "join_method": "optimal",
    },
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table="branch_order_line",
    app_role="sales_report_app",
    app_password="aiopsbench",
    fault_enable_hashjoin="off",
    fault_enable_mergejoin="off",
    support_index="idx_aiopsbench_branch_order_line_account_date_branch_product",
    create_account_first_index=False,
    minimum_slowdown_seconds=0.03,
    minimum_slowdown_ratio=1.15,
    warm_plans_before_measurement=True,
    fault_disable_memoize=True,
    start_fingerprint_probe=True,
    fault_fingerprint_sql=_DAILY_ACCOUNT_SUMMARY_SQL,
    slow_queries=(_DAILY_ACCOUNT_SUMMARY_SQL,),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.6,
        reference_run_ids=(
            "pg_query_perf_suboptimal_simple_flash__pg_query_perf_suboptimal_join__"
            "daily_account_summary_planner_drift__mock__r001",
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

class PgQueryPerfSuboptimalJoinInjector(BaseFaultInjector, PgQueryPerfFaultFingerprintProbe):
    """
    模拟"连接顺序与算法选择错误"故障。
    通过报表应用角色的会话级 planner 配置漂移，迫使该角色下的完整报表
    查询走差 Join 顺序和大量 Nested Loop。DBA 会话里的 SHOW 参数保持正常。
    """

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.app_role = _validate_sql_identifier(config["app_role"], "app_role")
        self.app_password = config["app_password"]
        self.enable_hashjoin = config["enable_hashjoin"]
        self.enable_mergejoin = config["enable_mergejoin"]
        self.fault_fingerprint_sql = config["fault_fingerprint_sql"]
        self.start_fingerprint_probe = bool(config["start_fingerprint_probe"])
        self.support_index = _validate_sql_identifier(
            config["support_index"],
            "support_index",
        )
        self.create_account_first_index = bool(config["create_account_first_index"])
        self.minimum_slowdown_seconds = float(config["minimum_slowdown_seconds"])
        self.minimum_slowdown_ratio = float(config["minimum_slowdown_ratio"])
        self.warm_plans_before_measurement = bool(config["warm_plans_before_measurement"])
        self.fault_disable_memoize = bool(config["fault_disable_memoize"])

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._capture_and_assert_fault()
        if self.start_fingerprint_probe and self._env_supports_background_probe():
            self._start_fault_fingerprint_probe(
                sql=self.fault_fingerprint_sql,
                app_name="aiopsbench_fp_suboptimal_join",
                interval_seconds=8.0,
                db_user=self.app_role,
                db_password=self.app_password,
            )

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        with env.metrics_hidden():
            self._install(config, env)
        if self.start_fingerprint_probe and self._env_supports_background_probe():
            self._start_fault_fingerprint_probe(
                sql=self.fault_fingerprint_sql,
                app_name="aiopsbench_fp_suboptimal_join",
                interval_seconds=8.0,
                db_user=self.app_role,
                db_password=self.app_password,
            )

    def _install(self, config: dict, env):
        self._configure(config, env)

        print(f"[FaultInjector:PgQueryPerfSuboptimalJoinInjector] Injecting suboptimal join fault...")

        # Keep the scenario focused on planner Join choices: the supporting
        # fact-table index prevents raw heap scans from dominating both the
        # healthy and faulty plans.
        env.execute_sql("DROP INDEX IF EXISTS idx_aiopsbench_branch_order_line_date_account_branch;")
        env.execute_sql("DROP INDEX IF EXISTS idx_aiopsbench_branch_order_line_account_date_branch;")
        if self.create_account_first_index:
            env.execute_sql(
                f"CREATE INDEX IF NOT EXISTS {self.support_index} "
                "ON branch_order_line (bol_account_sk, bol_sold_date_sk, bol_branch_sk, bol_product_sk) "
                "INCLUDE (bol_net_paid, bol_net_profit);"
            )
        else:
            env.execute_sql(
                f"CREATE INDEX IF NOT EXISTS {self.support_index} "
                "ON branch_order_line (bol_sold_date_sk, bol_account_sk, bol_branch_sk, bol_product_sk) "
                "INCLUDE (bol_net_paid, bol_net_profit);"
            )
        env.execute_sql(
            "CREATE INDEX IF NOT EXISTS idx_aiopsbench_branch_order_line_date_account_branch_product "
            "ON branch_order_line (bol_sold_date_sk, bol_account_sk, bol_branch_sk, bol_product_sk) "
            "INCLUDE (bol_net_paid, bol_net_profit);"
        )
        env.execute_sql(
            "CREATE INDEX IF NOT EXISTS idx_aiopsbench_digital_order_line_bill_account "
            "ON digital_order_line (dol_bill_account_sk) INCLUDE (dol_net_paid);"
        )
        env.execute_sql(
            "CREATE INDEX IF NOT EXISTS idx_aiopsbench_assisted_order_line_bill_account "
            "ON assisted_order_line (aol_bill_account_sk, aol_order_number);"
        )
        env.execute_sql("ANALYZE branch_order_line;")
        env.execute_sql("ANALYZE digital_order_line; ANALYZE assisted_order_line;")
        env.execute_sql(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{self.app_role}') THEN
                    CREATE ROLE {self.app_role} LOGIN PASSWORD '{self.app_password}';
                END IF;
            END $$;
        """)
        env.execute_sql(f"ALTER ROLE {self.app_role} WITH LOGIN PASSWORD '{self.app_password}';")
        env.execute_sql(f"GRANT USAGE ON SCHEMA public TO {self.app_role};")
        env.execute_sql(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {self.app_role};")
        env.execute_sql(f"ALTER ROLE {self.app_role} SET enable_hashjoin = {self.enable_hashjoin};")
        env.execute_sql(f"ALTER ROLE {self.app_role} SET enable_mergejoin = {self.enable_mergejoin};")
        if self.fault_disable_memoize:
            env.execute_sql(f"ALTER ROLE {self.app_role} SET enable_memoize = off;")

        print(f"[FaultInjector:PgQueryPerfSuboptimalJoinInjector] "
              f"app_role={self.app_role}, "
              f"enable_hashjoin={self.enable_hashjoin}, "
              f"enable_mergejoin={self.enable_mergejoin} applied to role.")

        self._capture_and_assert_fault()

    def prepare_observability(self, context: FaultLifecycleContext):
        import time

        config = context.config
        env = context.env
        deadline = time.monotonic() + 15.0
        evidence = self._query_observability_evidence(env)
        while not self._suboptimal_join_target_visible(evidence):
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "Suboptimal-join target report did not become visible within 15 seconds: "
                    f"topsql={evidence['topsql']}, slow_queries={evidence['slow_queries']}"
                )
            time.sleep(1.0)
            evidence = self._query_observability_evidence(env)
        self._assert_suboptimal_join_target_visible(evidence)
        evidence["role_settings"] = env.execute_sql(
            "SELECT rolname, rolconfig FROM pg_roles "
            f"WHERE rolname = '{self.app_role}';"
        )
        evidence.update({
            "baseline_plan": self.baseline_plan,
            "fault_plan": self.fault_plan,
            "baseline_query_seconds": self.baseline_query_seconds,
            "fault_query_seconds": self.fault_query_seconds,
        })
        return evidence

    def _capture_and_assert_fault(self) -> None:
        _require_sql_success(
            self.env.execute_sql("SET statement_timeout = '300s';"),
            "set suboptimal-join verification timeout",
        )
        if self.warm_plans_before_measurement:
            _require_sql_success(
                self.env.execute_sql("SET jit = off; SET work_mem = '64MB';"),
                "set stable suboptimal-join measurement session",
            )
        _require_sql_success(
            self.env.execute_sql(
                "SET enable_hashjoin = on; SET enable_mergejoin = on; SET enable_memoize = on;"
            ),
            "set suboptimal-join healthy planner context",
        )
        if self.warm_plans_before_measurement:
            healthy_warmup = self.env.execute_sql(
                f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
                f"{self.fault_fingerprint_sql.rstrip(';')};"
            )
            _require_sql_success(healthy_warmup, "warm suboptimal-join healthy plan")
            _require_sql_success(
                self.env.execute_sql(
                    "SET enable_hashjoin = off; SET enable_mergejoin = off; "
                    + ("SET enable_memoize = off;" if self.fault_disable_memoize else "")
                ),
                "set suboptimal-join faulty warmup context",
            )
            fault_warmup = self.env.execute_sql(
                f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
                f"{self.fault_fingerprint_sql.rstrip(';')};"
            )
            _require_sql_success(fault_warmup, "warm suboptimal-join faulty plan")
            _require_sql_success(
                self.env.execute_sql(
                    "SET enable_hashjoin = on; SET enable_mergejoin = on; SET enable_memoize = on;"
                ),
                "restore suboptimal-join healthy measurement context",
            )
        self.baseline_plan = self.env.execute_sql(
            f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
            f"{self.fault_fingerprint_sql.rstrip(';')};"
        )
        _require_sql_success(self.baseline_plan, "capture suboptimal-join healthy plan")
        _require_sql_success(
            self.env.execute_sql(
                "SET enable_hashjoin = off; SET enable_mergejoin = off; "
                + ("SET enable_memoize = off;" if self.fault_disable_memoize else "")
            ),
            "set suboptimal-join faulty planner context",
        )
        self.fault_plan = self.env.execute_sql(
            f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
            f"{self.fault_fingerprint_sql.rstrip(';')};"
        )
        _require_sql_success(self.fault_plan, "capture suboptimal-join faulty plan")
        _require_sql_success(
            self.env.execute_sql(
                "RESET enable_hashjoin; RESET enable_mergejoin; RESET enable_memoize;"
            ),
            "reset suboptimal-join verification context",
        )
        role_settings = self.env.execute_sql(
            "SELECT rolname, rolconfig FROM pg_roles "
            f"WHERE rolname = '{self.app_role}';"
        )
        _require_sql_success(role_settings, "read suboptimal-join role settings")

        from src.database.postgres import execution_time_seconds

        self.baseline_query_seconds = execution_time_seconds(self.baseline_plan)
        self.fault_query_seconds = execution_time_seconds(self.fault_plan)
        settings_text = json.dumps(role_settings, ensure_ascii=False, default=str).lower()
        for expected in (
            self.app_role,
            f"enable_hashjoin={self.enable_hashjoin}",
            f"enable_mergejoin={self.enable_mergejoin}",
        ):
            if expected not in settings_text:
                raise RuntimeError(
                    "Suboptimal-join role drift is not observable: "
                    f"expected={expected!r}, role_settings={role_settings}"
                )

        baseline_text = json.dumps(self.baseline_plan, ensure_ascii=False, default=str).lower()
        fault_text = json.dumps(self.fault_plan, ensure_ascii=False, default=str).lower()
        if "nested loop" not in fault_text:
            raise RuntimeError(
                f"Suboptimal-join faulty plan does not contain Nested Loop: {self.fault_plan}"
            )
        if "hash join" not in baseline_text and "merge join" not in baseline_text:
            raise RuntimeError(
                "Suboptimal-join healthy plan does not contain Hash Join or Merge Join: "
                f"{self.baseline_plan}"
            )
        if self.baseline_query_seconds is None or self.fault_query_seconds is None:
            raise RuntimeError(
                "Suboptimal-join plans do not contain execution times: "
                f"baseline={self.baseline_plan}, fault={self.fault_plan}"
            )
        if not (
            self.fault_query_seconds
            >= self.baseline_query_seconds + self.minimum_slowdown_seconds
            and self.fault_query_seconds
            >= self.baseline_query_seconds * self.minimum_slowdown_ratio
        ):
            raise RuntimeError(
                "Suboptimal-join fault is not meaningfully slower than the healthy plan: "
                f"baseline_seconds={self.baseline_query_seconds}, "
                f"fault_seconds={self.fault_query_seconds}"
            )

    def _suboptimal_join_target_visible(self, evidence: Mapping[str, object]) -> bool:
        text = "\n".join(
            json.dumps(value, ensure_ascii=False, default=str).lower()
            for value in (evidence["topsql"], evidence["slow_queries"])
        )
        return "branch_order_line" in text and "shopper_account" in text

    def _assert_suboptimal_join_target_visible(self, evidence: Mapping[str, object]) -> None:
        text = "\n".join(
            json.dumps(value, ensure_ascii=False, default=str).lower()
            for value in (evidence["topsql"], evidence["slow_queries"])
        )
        leaked_terms = (
            "alter system",
            "enable_hashjoin",
            "enable_mergejoin",
            "nested loop",
            "q77",
            "suboptimal join",
        )
        leaked = [term for term in leaked_terms if term in text]
        if leaked:
            raise RuntimeError(
                f"Suboptimal-join observability leaks setup/root-cause terms {leaked}: {evidence}"
            )

    def quiesce(self, context: FaultLifecycleContext):
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_suboptimal_join")

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        self._configure(context.config, env)
        print(f"[FaultInjector:PgQueryPerfSuboptimalJoinInjector] Recovering...")
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_suboptimal_join")
        _require_sql_success(
            env.execute_sql(
                f"ALTER ROLE {self.app_role} RESET enable_hashjoin; "
                f"ALTER ROLE {self.app_role} RESET enable_mergejoin; "
                f"ALTER ROLE {self.app_role} RESET enable_memoize;"
            ),
            f"restore planner settings for role {self.app_role}",
        )
        print(f"[FaultInjector:PgQueryPerfSuboptimalJoinInjector] Recovery complete.")
class PgQueryPerfSuboptimalJoinScenario(PostgresScenario):
    scenario_id = 'pg_query_perf_suboptimal_join'
    description = 'Simulates suboptimal join method regression from role-level planner setting drift.'
    cases = (
        _PGQUERYPERFSUBOPTIMALJOINSCENARIO_CASE,
        _PGQUERYPERFSUBOPTIMALJOINSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgQueryPerfSuboptimalJoinCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgQueryPerfSuboptimalJoinInjector,
                config={
                    'app_role': case.app_role,
                    'app_password': case.app_password,
                    'enable_hashjoin': case.fault_enable_hashjoin,
                    'enable_mergejoin': case.fault_enable_mergejoin,
                    'support_index': case.support_index,
                    'create_account_first_index': case.create_account_first_index,
                    'minimum_slowdown_seconds': case.minimum_slowdown_seconds,
                    'minimum_slowdown_ratio': case.minimum_slowdown_ratio,
                    'warm_plans_before_measurement': case.warm_plans_before_measurement,
                    'fault_disable_memoize': case.fault_disable_memoize,
                    'start_fingerprint_probe': case.start_fingerprint_probe,
                    'fault_fingerprint_sql': case.fault_fingerprint_sql,
                },
            ),
        )
