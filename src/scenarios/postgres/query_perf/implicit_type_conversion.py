from dataclasses import dataclass
from typing import Mapping

from src.database.query_results import capture_query_result_truth
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
from src.scenarios.postgres.common import (
    build_query_perf_noise_profiles,
)

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


QUERY_PERF_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfImplicitTypeConversionCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    deployment_cpus: float
    deployment_memory_mb: int
    deployment_shm_size: str
    table: str
    column: str
    index_name: str
    expression_index_name: str
    request_table: str
    fault_fingerprint_sql: str
    fixed_fingerprint_sql: str
    slow_queries: tuple[str, ...]

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfImplicitTypeConversionForBranchOrderImplicitCastScenarioCase(PgQueryPerfImplicitTypeConversionCase):
    pass


class PgQueryPerfImplicitTypeConversionForBranchOrderImplicitCastSimpleScenarioCase(PgQueryPerfImplicitTypeConversionCase):
    pass

_PGQUERYPERFIMPLICITTYPECONVERSIONSCENARIO_CASE = PgQueryPerfImplicitTypeConversionForBranchOrderImplicitCastScenarioCase(
    case_id='branch_order_implicit_cast',
    runtime=PostgresCaseRuntime(resources=QUERY_PERF_RESOURCES),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "order exception triage query",
                    "entity": "branch_order_implicit_cast",
                    "evidence": [
                        "scripted diagnostic actions observed order exception triage query"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "request values have wrong type",
                    "entity": "branch_order_implicit_cast",
                    "evidence": [
                        "scripted diagnostic actions observed request values have wrong type"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "implicit cast bypasses integer index",
                    "entity": "branch_order_implicit_cast",
                    "evidence": [
                        "scripted diagnostic actions observed implicit cast bypasses integer index"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "cast request values to integer before comparison"
            ],
            "verification": [
                "typed request query was verified"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgQueryPerfImplicitTypeConversionForBranchOrderImplicitCastEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcdsx:latest',
    workload_tag='tpcdsx',
    dataset_scale=1,
    deployment_cpus=1.0,
    deployment_memory_mb=512,
    deployment_shm_size='256m',
    title='Simulates implicit type conversion causing index bypass on an indexed integer column.',
    alert='Alert: the order exception triage report has regressed from ~300ms to multi-second latency during support escalations. The slow SQL is concentrated on branch_order_line; rows scanned per execution are far higher than the number of returned accounts. Identify the exact predicate or access path causing the scan amplification and provide a verifiable, semantically equivalent fix.',
    initial_state={'status': 'healthy', 'index': 'exists_but_bypassed'},
    expected_target={'status': 'recovered', 'query': 'rewritten_with_correct_type'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table='branch_order_line',
    column='bol_receipt_number',
    index_name='idx_branch_order_line_bol_receipt_number_int',
    expression_index_name='idx_branch_order_line_bol_receipt_number_expr',
    request_table='support_triage_request',
    fault_fingerprint_sql=('\n'
 '/* ops_support: order_exception_triage_v3 */\n'
 'WITH\n'
 'request_context AS MATERIALIZED (\n'
 '    SELECT\n'
 '        str.receipt_watchlist\n'
 '    FROM support_triage_request str\n'
 "    WHERE str.request_id = 'order_exception_triage_v3'\n"
 '),\n'
 'candidate_lines AS MATERIALIZED (\n'
 '    SELECT\n'
 '        bol.bol_product_sk,\n'
 '        bol.bol_receipt_number,\n'
 '        bol.bol_account_sk,\n'
 '        bol.bol_sold_date_sk,\n'
 '        bol.bol_branch_sk,\n'
 '        bol.bol_quantity,\n'
 '        bol.bol_ext_discount_amt,\n'
 '        bol.bol_net_paid,\n'
 '        bol.bol_net_profit\n'
 '    FROM branch_order_line bol\n'
 '    JOIN request_context rc\n'
 '      ON bol.bol_receipt_number = ANY(rc.receipt_watchlist)\n'
 '),\n'
 'product_enriched AS MATERIALIZED (\n'
 '    SELECT\n'
 '        cl.*,\n'
 '        pr.pr_product_id,\n'
 '        pr.pr_category,\n'
 '        pr.pr_brand,\n'
 '        pr.pr_class,\n'
 '        pr.pr_current_price\n'
 '    FROM candidate_lines cl\n'
 '    JOIN product pr ON pr.pr_product_sk = cl.bol_product_sk\n'
 '),\n'
 'account_rollup AS MATERIALIZED (\n'
 '    SELECT\n'
 '        pe.bol_account_sk,\n'
 '        COUNT(*) AS line_count,\n'
 '        SUM(pe.bol_net_paid) AS net_paid,\n'
 '        SUM(pe.bol_net_profit) AS net_profit,\n'
 '        AVG(pe.bol_quantity) AS avg_quantity,\n'
 '        COUNT(*) FILTER (WHERE pe.bol_ext_discount_amt > 0) AS discounted_lines,\n'
 '        MAX(pe.bol_receipt_number) AS latest_receipt,\n'
 '        COUNT(DISTINCT pe.bol_product_sk) AS product_count,\n'
 '        MIN(pe.pr_product_id) AS sample_product_id,\n'
 '        MIN(pe.pr_category) AS sample_category,\n'
 '        MIN(pe.pr_brand) AS sample_brand\n'
 '    FROM product_enriched pe\n'
 '    GROUP BY pe.bol_account_sk\n'
 '    HAVING SUM(pe.bol_net_paid) > 0\n'
 '),\n'
 'daily_branch_context AS MATERIALIZED (\n'
 '    SELECT\n'
 '        pe.bol_account_sk,\n'
 '        pe.bol_branch_sk,\n'
 '        cd.cal_year,\n'
 '        cd.cal_moy,\n'
 '        COUNT(*) AS day_lines,\n'
 '        SUM(pe.bol_net_paid) AS day_net_paid\n'
 '    FROM product_enriched pe\n'
 '    JOIN calendar_day cd ON cd.cal_day_sk = pe.bol_sold_date_sk\n'
 '    GROUP BY pe.bol_account_sk, pe.bol_branch_sk, cd.cal_year, cd.cal_moy\n'
 '),\n'
 'ranked_accounts AS (\n'
 '    SELECT\n'
 '        ar.*,\n'
 '        RANK() OVER (\n'
 '            ORDER BY ar.net_paid DESC, ar.line_count DESC, ar.latest_receipt DESC\n'
 '        ) AS spend_rank,\n'
 '        NTILE(5) OVER (ORDER BY ar.avg_quantity DESC NULLS LAST) AS quantity_bucket\n'
 '    FROM account_rollup ar\n'
 ')\n'
 'SELECT\n'
 '    ra.bol_account_sk,\n'
 '    sa.sa_first_name,\n'
 '    sa.sa_last_name,\n'
 '    sa.sa_preferred_flag,\n'
 '    dbc.bol_branch_sk,\n'
 '    br.br_branch_name,\n'
 '    dbc.cal_year,\n'
 '    dbc.cal_moy,\n'
 '    ra.product_count,\n'
 '    ra.sample_product_id,\n'
 '    ra.sample_category,\n'
 '    ra.sample_brand,\n'
 '    ra.line_count,\n'
 '    ra.net_paid,\n'
 '    ra.net_profit,\n'
 '    ra.avg_quantity,\n'
 '    ra.discounted_lines,\n'
 '    ra.spend_rank,\n'
 '    ra.quantity_bucket,\n'
 '    dbc.day_lines,\n'
 '    dbc.day_net_paid\n'
 'FROM ranked_accounts ra\n'
 'JOIN shopper_account sa ON sa.sa_account_sk = ra.bol_account_sk\n'
 'JOIN daily_branch_context dbc ON dbc.bol_account_sk = ra.bol_account_sk\n'
 'JOIN branch br ON br.br_branch_sk = dbc.bol_branch_sk\n'
 'WHERE ra.spend_rank <= 50\n'
 'ORDER BY ra.spend_rank, ra.net_paid DESC, dbc.day_net_paid DESC, ra.bol_account_sk\n'
 'LIMIT 50\n'),
    fixed_fingerprint_sql=('\n'
 '/* ops_support: order_exception_triage_v3 */\n'
 'WITH\n'
 'request_context AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ARRAY(\n'
 '            SELECT receipt_value::integer\n'
 '            FROM unnest(str.receipt_watchlist) AS receipt_value\n'
 '            WHERE receipt_value = trunc(receipt_value)\n'
 '        ) AS receipt_watchlist\n'
 '    FROM support_triage_request str\n'
 "    WHERE str.request_id = 'order_exception_triage_v3'\n"
 '),\n'
 'candidate_lines AS MATERIALIZED (\n'
 '    SELECT\n'
 '        bol.bol_product_sk,\n'
 '        bol.bol_receipt_number,\n'
 '        bol.bol_account_sk,\n'
 '        bol.bol_sold_date_sk,\n'
 '        bol.bol_branch_sk,\n'
 '        bol.bol_quantity,\n'
 '        bol.bol_ext_discount_amt,\n'
 '        bol.bol_net_paid,\n'
 '        bol.bol_net_profit\n'
 '    FROM branch_order_line bol\n'
 '    JOIN request_context rc\n'
 '      ON bol.bol_receipt_number = ANY(rc.receipt_watchlist)\n'
 '),\n'
 'product_enriched AS MATERIALIZED (\n'
 '    SELECT\n'
 '        cl.*,\n'
 '        pr.pr_product_id,\n'
 '        pr.pr_category,\n'
 '        pr.pr_brand,\n'
 '        pr.pr_class,\n'
 '        pr.pr_current_price\n'
 '    FROM candidate_lines cl\n'
 '    JOIN product pr ON pr.pr_product_sk = cl.bol_product_sk\n'
 '),\n'
 'account_rollup AS MATERIALIZED (\n'
 '    SELECT\n'
 '        pe.bol_account_sk,\n'
 '        COUNT(*) AS line_count,\n'
 '        SUM(pe.bol_net_paid) AS net_paid,\n'
 '        SUM(pe.bol_net_profit) AS net_profit,\n'
 '        AVG(pe.bol_quantity) AS avg_quantity,\n'
 '        COUNT(*) FILTER (WHERE pe.bol_ext_discount_amt > 0) AS discounted_lines,\n'
 '        MAX(pe.bol_receipt_number) AS latest_receipt,\n'
 '        COUNT(DISTINCT pe.bol_product_sk) AS product_count,\n'
 '        MIN(pe.pr_product_id) AS sample_product_id,\n'
 '        MIN(pe.pr_category) AS sample_category,\n'
 '        MIN(pe.pr_brand) AS sample_brand\n'
 '    FROM product_enriched pe\n'
 '    GROUP BY pe.bol_account_sk\n'
 '    HAVING SUM(pe.bol_net_paid) > 0\n'
 '),\n'
 'daily_branch_context AS MATERIALIZED (\n'
 '    SELECT\n'
 '        pe.bol_account_sk,\n'
 '        pe.bol_branch_sk,\n'
 '        cd.cal_year,\n'
 '        cd.cal_moy,\n'
 '        COUNT(*) AS day_lines,\n'
 '        SUM(pe.bol_net_paid) AS day_net_paid\n'
 '    FROM product_enriched pe\n'
 '    JOIN calendar_day cd ON cd.cal_day_sk = pe.bol_sold_date_sk\n'
 '    GROUP BY pe.bol_account_sk, pe.bol_branch_sk, cd.cal_year, cd.cal_moy\n'
 '),\n'
 'ranked_accounts AS (\n'
 '    SELECT\n'
 '        ar.*,\n'
 '        RANK() OVER (\n'
 '            ORDER BY ar.net_paid DESC, ar.line_count DESC, ar.latest_receipt DESC\n'
 '        ) AS spend_rank,\n'
 '        NTILE(5) OVER (ORDER BY ar.avg_quantity DESC NULLS LAST) AS quantity_bucket\n'
 '    FROM account_rollup ar\n'
 ')\n'
 'SELECT\n'
 '    ra.bol_account_sk,\n'
 '    sa.sa_first_name,\n'
 '    sa.sa_last_name,\n'
 '    sa.sa_preferred_flag,\n'
 '    dbc.bol_branch_sk,\n'
 '    br.br_branch_name,\n'
 '    dbc.cal_year,\n'
 '    dbc.cal_moy,\n'
 '    ra.product_count,\n'
 '    ra.sample_product_id,\n'
 '    ra.sample_category,\n'
 '    ra.sample_brand,\n'
 '    ra.line_count,\n'
 '    ra.net_paid,\n'
 '    ra.net_profit,\n'
 '    ra.avg_quantity,\n'
 '    ra.discounted_lines,\n'
 '    ra.spend_rank,\n'
 '    ra.quantity_bucket,\n'
 '    dbc.day_lines,\n'
 '    dbc.day_net_paid\n'
 'FROM ranked_accounts ra\n'
 'JOIN shopper_account sa ON sa.sa_account_sk = ra.bol_account_sk\n'
 'JOIN daily_branch_context dbc ON dbc.bol_account_sk = ra.bol_account_sk\n'
 'JOIN branch br ON br.br_branch_sk = dbc.bol_branch_sk\n'
 'WHERE ra.spend_rank <= 50\n'
 'ORDER BY ra.spend_rank, ra.net_paid DESC, dbc.day_net_paid DESC, ra.bol_account_sk\n'
 'LIMIT 50\n'),
    slow_queries=('\n'
 '/* ops_support: order_exception_triage_v3 */\n'
 'WITH\n'
 'request_context AS MATERIALIZED (\n'
 '    SELECT\n'
 '        str.receipt_watchlist\n'
 '    FROM support_triage_request str\n'
 "    WHERE str.request_id = 'order_exception_triage_v3'\n"
 '),\n'
 'candidate_lines AS MATERIALIZED (\n'
 '    SELECT\n'
 '        bol.bol_product_sk,\n'
 '        bol.bol_receipt_number,\n'
 '        bol.bol_account_sk,\n'
 '        bol.bol_sold_date_sk,\n'
 '        bol.bol_branch_sk,\n'
 '        bol.bol_quantity,\n'
 '        bol.bol_ext_discount_amt,\n'
 '        bol.bol_net_paid,\n'
 '        bol.bol_net_profit\n'
 '    FROM branch_order_line bol\n'
 '    JOIN request_context rc\n'
 '      ON bol.bol_receipt_number = ANY(rc.receipt_watchlist)\n'
 '),\n'
 'product_enriched AS MATERIALIZED (\n'
 '    SELECT\n'
 '        cl.*,\n'
 '        pr.pr_product_id,\n'
 '        pr.pr_category,\n'
 '        pr.pr_brand,\n'
 '        pr.pr_class,\n'
 '        pr.pr_current_price\n'
 '    FROM candidate_lines cl\n'
 '    JOIN product pr ON pr.pr_product_sk = cl.bol_product_sk\n'
 '),\n'
 'account_rollup AS MATERIALIZED (\n'
 '    SELECT\n'
 '        pe.bol_account_sk,\n'
 '        COUNT(*) AS line_count,\n'
 '        SUM(pe.bol_net_paid) AS net_paid,\n'
 '        SUM(pe.bol_net_profit) AS net_profit,\n'
 '        AVG(pe.bol_quantity) AS avg_quantity,\n'
 '        COUNT(*) FILTER (WHERE pe.bol_ext_discount_amt > 0) AS discounted_lines,\n'
 '        MAX(pe.bol_receipt_number) AS latest_receipt,\n'
 '        COUNT(DISTINCT pe.bol_product_sk) AS product_count,\n'
 '        MIN(pe.pr_product_id) AS sample_product_id,\n'
 '        MIN(pe.pr_category) AS sample_category,\n'
 '        MIN(pe.pr_brand) AS sample_brand\n'
 '    FROM product_enriched pe\n'
 '    GROUP BY pe.bol_account_sk\n'
 '    HAVING SUM(pe.bol_net_paid) > 0\n'
 '),\n'
 'daily_branch_context AS MATERIALIZED (\n'
 '    SELECT\n'
 '        pe.bol_account_sk,\n'
 '        pe.bol_branch_sk,\n'
 '        cd.cal_year,\n'
 '        cd.cal_moy,\n'
 '        COUNT(*) AS day_lines,\n'
 '        SUM(pe.bol_net_paid) AS day_net_paid\n'
 '    FROM product_enriched pe\n'
 '    JOIN calendar_day cd ON cd.cal_day_sk = pe.bol_sold_date_sk\n'
 '    GROUP BY pe.bol_account_sk, pe.bol_branch_sk, cd.cal_year, cd.cal_moy\n'
 '),\n'
 'ranked_accounts AS (\n'
 '    SELECT\n'
 '        ar.*,\n'
 '        RANK() OVER (\n'
 '            ORDER BY ar.net_paid DESC, ar.line_count DESC, ar.latest_receipt DESC\n'
 '        ) AS spend_rank,\n'
 '        NTILE(5) OVER (ORDER BY ar.avg_quantity DESC NULLS LAST) AS quantity_bucket\n'
 '    FROM account_rollup ar\n'
 ')\n'
 'SELECT\n'
 '    ra.bol_account_sk,\n'
 '    sa.sa_first_name,\n'
 '    sa.sa_last_name,\n'
 '    sa.sa_preferred_flag,\n'
 '    dbc.bol_branch_sk,\n'
 '    br.br_branch_name,\n'
 '    dbc.cal_year,\n'
 '    dbc.cal_moy,\n'
 '    ra.product_count,\n'
 '    ra.sample_product_id,\n'
 '    ra.sample_category,\n'
 '    ra.sample_brand,\n'
 '    ra.line_count,\n'
 '    ra.net_paid,\n'
 '    ra.net_profit,\n'
 '    ra.avg_quantity,\n'
 '    ra.discounted_lines,\n'
 '    ra.spend_rank,\n'
 '    ra.quantity_bucket,\n'
 '    dbc.day_lines,\n'
 '    dbc.day_net_paid\n'
 'FROM ranked_accounts ra\n'
 'JOIN shopper_account sa ON sa.sa_account_sk = ra.bol_account_sk\n'
 'JOIN daily_branch_context dbc ON dbc.bol_account_sk = ra.bol_account_sk\n'
 'JOIN branch br ON br.br_branch_sk = dbc.bol_branch_sk\n'
 'WHERE ra.spend_rank <= 50\n'
 'ORDER BY ra.spend_rank, ra.net_paid DESC, dbc.day_net_paid DESC, ra.bol_account_sk\n'
'LIMIT 50\n',),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.625,
        reference_run_ids=(
            "reference-61__pg_query_perf_implicit_type_conversion__"
            "branch_order_implicit_cast__mock__r001",
        ),
    ),
)

_SIMPLE_FAULT_SQL = """/* ops_support: order_exception_triage_compact */
WITH request_context AS MATERIALIZED (
    SELECT str.receipt_watchlist
    FROM support_triage_request str
    WHERE str.request_id = 'order_exception_triage_compact'
)
SELECT bol.bol_receipt_number, bol.bol_account_sk
FROM branch_order_line bol
JOIN request_context rc
  ON bol.bol_receipt_number = ANY(rc.receipt_watchlist)
ORDER BY bol.bol_receipt_number
LIMIT 20
"""

_SIMPLE_FIXED_SQL = """/* ops_support: order_exception_triage_compact */
WITH request_context AS MATERIALIZED (
    SELECT ARRAY(
        SELECT receipt_value::integer
        FROM unnest(str.receipt_watchlist) AS receipt_value
        WHERE receipt_value = trunc(receipt_value)
    ) AS receipt_watchlist
    FROM support_triage_request str
    WHERE str.request_id = 'order_exception_triage_compact'
)
SELECT bol.bol_receipt_number, bol.bol_account_sk
FROM branch_order_line bol
JOIN request_context rc
  ON bol.bol_receipt_number = ANY(rc.receipt_watchlist)
ORDER BY bol.bol_receipt_number
LIMIT 20
"""

_PGQUERYPERFIMPLICITTYPECONVERSIONSCENARIO_SIMPLE_CASE = PgQueryPerfImplicitTypeConversionForBranchOrderImplicitCastSimpleScenarioCase(
    case_id="branch_order_implicit_cast_simple",
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
    evaluator=PgQueryPerfImplicitTypeConversionForBranchOrderImplicitCastSimpleEvaluatorCase,
    base_image_name="aiopsbench-pg-tpcdsx:latest",
    workload_tag="tpcdsx",
    dataset_scale=1,
    deployment_cpus=1.0,
    deployment_memory_mb=512,
    deployment_shm_size="256m",
    title="Compact support lookup with an implicit numeric-to-integer conversion.",
    alert="Alert: a compact support lookup over branch_order_line is slow. Inspect the plan, verify the existing integer index, and restore the lookup without changing returned rows.",
    initial_state={"status": "healthy", "index": "exists_but_bypassed"},
    expected_target={"status": "recovered", "query": "rewritten_with_correct_type"},
    background_workload=BackgroundWorkloadSpec(
        profiles=build_query_perf_noise_profiles({75}, light_n=1, medium_n=0),
        worker_count=1,
        seed=0x5171,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.25,
        reference_run_ids=(
            "logs/traces/"
            "run_pg_query_perf_implicit_type_conversion_branch_order_implicit_cast_simple_"
            "MockLLMAgent.json",
        ),
    ),
    table="branch_order_line",
    column="bol_receipt_number",
    index_name="idx_branch_order_line_bol_receipt_number_int",
    expression_index_name="idx_branch_order_line_bol_receipt_number_expr",
    request_table="support_triage_request",
    fault_fingerprint_sql=_SIMPLE_FAULT_SQL,
    fixed_fingerprint_sql=_SIMPLE_FIXED_SQL,
    slow_queries=(_SIMPLE_FAULT_SQL,),
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

class PgQueryPerfImplicitTypeConversionInjector(BaseFaultInjector, PgQueryPerfFaultFingerprintProbe):
    """
    模拟"隐式类型转换导致索引失效"故障。
    在 tpcdsx branch_order_line 上构造列侧类型转换 membership 谓词，触发普通整数索引
    无法使用。故障本身来自完整业务 SQL；injector 只准备索引、统计信息和
    可见的后台 fingerprint。
    """

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
        self.table = _validate_sql_identifier(config["table"], "table")
        self.column = _validate_sql_identifier(config["column"], "column")
        self.index_name = _validate_sql_identifier(
            config["index_name"],
            "index_name",
        )
        self.expression_index_name = _validate_sql_identifier(
            config["expression_index_name"],
            "expression_index_name",
        )
        self.request_table = _validate_sql_identifier(
            config["request_table"],
            "request_table",
        )
        self.fault_fingerprint_sql = config["fault_fingerprint_sql"]
        self.fixed_fingerprint_sql = config["fixed_fingerprint_sql"]

    def _install_persistent_state(self) -> None:
        print(f"[FaultInjector:PgQueryPerfImplicitTypeConversionInjector] "
              f"Preparing implicit type conversion fault on "
              f"{self.table}.{self.column}...")

        self._drop_known_expression_workarounds()
        self._prepare_request_context_table()
        _require_sql_success(
            self.env.execute_sql("SET statement_timeout = '0';"),
            "disable statement timeout while installing implicit-conversion fault",
        )
        if not self._column_index_exists():
            _require_sql_success(
                self.env.execute_sql(
                    f"CREATE INDEX {self.index_name} ON {self.table}({self.column});"
                ),
                "install implicit-conversion ordinary index",
            )

        print(f"[FaultInjector:PgQueryPerfImplicitTypeConversionInjector] "
              f"Index {self.index_name} ensured on "
              f"{self.table}({self.column}). "
              f"Column-side cast queries will bypass ordinary integer indexes.")

    def _verify_persistent_state(self) -> None:
        if not self._table_exists(self.request_table):
            raise RuntimeError(
                f"Implicit-conversion fault image is missing request table {self.request_table}"
            )
        if not self._column_index_exists():
            raise RuntimeError(
                "Implicit-conversion fault image is missing the ordinary index: "
                f"table={self.table}, column={self.column}, index={self.index_name}"
            )
        expression_indexes = self._known_expression_workaround_names()
        if expression_indexes:
            raise RuntimeError(
                "Implicit-conversion fault image contains a remediation expression index: "
                f"indexes={sorted(expression_indexes)}"
            )

    def _activate_runtime(self) -> None:
        import time

        self.fault_plan, self.fault_query_seconds = self._capture_explain_analyze(
            self.fault_fingerprint_sql,
            timeout_seconds=300,
        )
        self.fixed_plan, self.fixed_query_seconds = self._capture_explain_analyze(
            self.fixed_fingerprint_sql,
            timeout_seconds=300,
        )
        self._assert_implicit_conversion_observable(self.fault_plan, self.fixed_plan)
        if self._env_supports_background_probe():
            self._start_fault_fingerprint_probe(
                sql=self.fault_fingerprint_sql,
                app_name="aiopsbench_fp_implicit_cast",
            )
            time.sleep(6.0)
            if not self.env.reconnect():
                raise RuntimeError(
                    f"Implicit-conversion activation could not reconnect to "
                    f"{self.env.host}:{self.env.port}"
                )

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        seed_result = env.execute_sql(config["fault_fingerprint_sql"])
        _require_sql_success(seed_result, "seed implicit-conversion business query")
        evidence = self._query_observability_evidence(env)
        evidence.update({
            "fault_query_truth": capture_query_result_truth(seed_result, ordered=True),
            "fault_query_seconds": self.fault_query_seconds,
            "fixed_query_seconds": self.fixed_query_seconds,
            "fault_plan": self.fault_plan,
            "fixed_plan": self.fixed_plan,
        })
        return evidence

    def _assert_implicit_conversion_observable(self, fault_plan, fixed_plan) -> None:
        fault_text = self._result_to_text(fault_plan).lower()
        fixed_text = self._result_to_text(fixed_plan).lower()
        if self.table not in fault_text:
            raise RuntimeError(
                f"Implicit-conversion fault plan does not touch table {self.table}: {fault_plan}"
            )
        coercions = (f"{self.column})::numeric", f"{self.column}::numeric")
        if not any(coercion in fault_text for coercion in coercions):
            raise RuntimeError(
                "Implicit-conversion fault plan does not expose the numeric column coercion: "
                f"column={self.column}, plan={fault_plan}"
            )
        if "index scan" not in fixed_text and "bitmap index scan" not in fixed_text:
            raise RuntimeError(
                f"Implicit-conversion fixed query does not use an index path: {fixed_plan}"
            )
        if f"seq scan on {self.table}" in fixed_text:
            raise RuntimeError(
                f"Implicit-conversion fixed query still uses Seq Scan on {self.table}: {fixed_plan}"
            )

    def quiesce(self, context: FaultLifecycleContext):
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_implicit_cast")

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_implicit_cast")
        self._drop_known_expression_workarounds()
        _require_sql_success(
            self.env.execute_sql(
                f"DROP TABLE IF EXISTS {self.request_table}; "
                f"DROP INDEX IF EXISTS {self.index_name};"
            ),
            "recover implicit-conversion supporting objects",
        )
        print(f"[FaultInjector:PgQueryPerfImplicitTypeConversionInjector]"
              f" Recovery complete; scenario-owned auxiliary objects removed.")

    def _drop_known_expression_workarounds(self):
        index_names = self._known_expression_workaround_names()
        index_names.add(self.expression_index_name)
        for index_name in sorted(index_names):
            _require_sql_success(
                self.env.execute_sql(f"DROP INDEX IF EXISTS {index_name};"),
                f"drop implicit-conversion expression index {index_name}",
            )

    def _known_expression_workaround_names(self) -> set[str]:
        index_names = set()
        rows = self._result_rows(self.env.execute_sql(
            "SELECT indexname FROM pg_indexes "
            f"WHERE tablename = '{self.table}' "
            f"AND indexdef ILIKE '%{self.column}%' "
            "AND (indexdef ILIKE '%::text%' OR indexdef ILIKE '%::numeric%' "
            "OR indexdef ILIKE '%text%' OR indexdef ILIKE '%numeric%');"
        ))
        for row in rows:
            if row:
                index_names.add(_validate_sql_identifier(str(row[0]), "index_name"))
        return index_names

    def _prepare_request_context_table(self):
        request_id_match = re.search(
            r"\brequest_id\s*=\s*'([^']+)'",
            self.fault_fingerprint_sql,
            re.IGNORECASE,
        )
        if request_id_match is None:
            raise RuntimeError(
                "Implicit-conversion fault SQL has no request identity: "
                f"table={self.request_table}, sql={self.fault_fingerprint_sql!r}"
            )
        request_id = request_id_match.group(1)
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.request_table};")
        self.env.execute_sql(f"""
            CREATE TABLE {self.request_table} (
                request_id text PRIMARY KEY,
                receipt_watchlist numeric[] NOT NULL
            );
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.request_table}
                (request_id, receipt_watchlist)
            SELECT '{request_id}', array_agg(receipt_value)
            FROM (
                SELECT gs::numeric AS receipt_value
                FROM generate_series(1, 50) AS gs
                UNION ALL
                SELECT gs::numeric + 0.5 AS receipt_value
                FROM generate_series(1001, 1020) AS gs
            ) receipt_values;
        """)

    def _table_exists(self, table_name: str) -> bool:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{table_name}') IS NOT NULL;"
            ),
            f"check implicit-conversion table {table_name}",
        )
        return bool(payload["result"][0][0])

    def _column_index_exists(self) -> bool:
        rows = self._result_rows(self.env.execute_sql(
            "SELECT indexname, indexdef FROM pg_indexes "
            f"WHERE tablename = '{self.table}' "
            f"AND (indexdef ILIKE '%({self.column})%' OR indexdef ILIKE '%({self.column},%') "
            "AND indexdef NOT ILIKE '%::text%' "
            "AND indexdef NOT ILIKE '%CAST%';"
        ))
        return bool(rows)

    def _measure_explain_analyze_seconds(self, sql: str, timeout_seconds: int) -> float:
        _, runtime = self._capture_explain_analyze(sql, timeout_seconds)
        return runtime

    def _capture_explain_analyze(self, sql: str, timeout_seconds: int):
        self.env.execute_sql(f"SET statement_timeout = '{int(timeout_seconds)}s';")
        result = self.env.execute_sql(
            f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql.rstrip(';')};"
        )
        text = self._result_to_text(result)
        if '"status": "error"' in text.lower():
            raise AssertionError(f"implicit-type conversion EXPLAIN ANALYZE failed: {text}")
        runtime = self._execution_time_seconds(result)
        if runtime is None:
            raise AssertionError(f"implicit-type conversion EXPLAIN ANALYZE had no Execution Time: {text}")
        return result, runtime

    def _execution_time_seconds(self, raw_result):
        if isinstance(raw_result, str):
            match = re.search(r"Execution Time:\s*([0-9.]+)\s*ms", raw_result, re.IGNORECASE)
            if match:
                return float(match.group(1)) / 1000.0
            raw_result = json.loads(raw_result)
        for value in self._walk_json_values(raw_result):
            if isinstance(value, dict) and "Execution Time" in value:
                return float(value["Execution Time"]) / 1000.0
        return None

    def _walk_json_values(self, value):
        yield value
        if isinstance(value, dict):
            for child in value.values():
                yield from self._walk_json_values(child)
        elif isinstance(value, list):
            for child in value:
                yield from self._walk_json_values(child)

    def _result_rows(self, raw_result):
        if isinstance(raw_result, str):
            raw_result = json.loads(raw_result)
        if isinstance(raw_result, dict):
            rows = raw_result.get("result", [])
            return rows if isinstance(rows, list) else []
        return []

    def _result_to_text(self, raw_result) -> str:
        if isinstance(raw_result, str):
            return raw_result
        return json.dumps(raw_result, ensure_ascii=False, default=str)


class PgQueryPerfImplicitTypeConversionScenario(PostgresScenario):
    scenario_id = 'pg_query_perf_implicit_type_conversion'
    description = 'Simulates implicit type conversion causing index bypass on an indexed integer column.'
    cases = (
        _PGQUERYPERFIMPLICITTYPECONVERSIONSCENARIO_CASE,
        _PGQUERYPERFIMPLICITTYPECONVERSIONSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgQueryPerfImplicitTypeConversionCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgQueryPerfImplicitTypeConversionInjector,
                config={
                    'table': case.table,
                    'column': case.column,
                    'index_name': case.index_name,
                    'expression_index_name': case.expression_index_name,
                    'request_table': case.request_table,
                    'fault_fingerprint_sql': case.fault_fingerprint_sql,
                    'fixed_fingerprint_sql': case.fixed_fingerprint_sql,
                },
            ),
        )
