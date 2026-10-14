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
class PgQueryPerfSortSpillCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    deployment_memory_mb: int
    table: str
    fault_work_mem: str
    recommended_work_mem: str
    max_safe_work_mem: str
    start_fingerprint_probe: bool
    fault_fingerprint_sql: str
    slow_queries: tuple[str, ...]

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfSortSpillForBranchOrderSortSpillScenarioCase(PgQueryPerfSortSpillCase):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfSortSpillForBranchOrderSortSpillSimpleScenarioCase(
    PgQueryPerfSortSpillCase
):
    pass


_PGQUERYPERFSORTSPILL_SIMPLE_SQL = """/* finance_reporting: branch_margin_top_simple */
WITH branch_product_margin AS MATERIALIZED (
    SELECT bol_branch_sk,
           bol_product_sk,
           SUM(bol_net_paid) AS revenue,
           SUM(bol_net_profit) AS margin
    FROM branch_order_line
    WHERE bol_sold_date_sk BETWEEN 2450815 AND 2452640
    GROUP BY bol_branch_sk, bol_product_sk
    ORDER BY margin DESC, bol_branch_sk, bol_product_sk
)
SELECT bol_branch_sk,
       bol_product_sk,
       revenue,
       margin
FROM branch_product_margin
LIMIT 20
"""


_PGQUERYPERFSORTSPILLSIMPLESCENARIO_CASE = (
    PgQueryPerfSortSpillForBranchOrderSortSpillSimpleScenarioCase(
        case_id="branch_order_sort_spill_simple",
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
        evaluator=PgQueryPerfSortSpillSimpleEvaluatorCase,
        base_image_name="aiopsbench-pg-tpcdsx:latest",
        workload_tag="tpcdsx",
        dataset_scale=1,
        deployment_memory_mb=256,
        title="Simulates a compact branch-margin ranking spilling its sort to disk.",
        alert=(
            "Alert: the branch margin dashboard's top-20 ranking is slow during the "
            "daily close, with elevated database I/O. The result set is small but "
            "the aggregation and ordering step takes much longer than usual. "
            "Identify the database resource constraint and provide a verifiable, "
            "non-destructive fix.\n\nAffected query:\n\n"
            + _PGQUERYPERFSORTSPILL_SIMPLE_SQL
        ),
        initial_state={"status": "degraded", "work_mem": "4MB", "sort_method": "external merge disk"},
        expected_target={"status": "recovered", "work_mem": "increased", "sort_method": "in-memory"},
        background_workload=EMPTY_BACKGROUND_WORKLOAD,
        difficulty=DifficultyCalibration(
            diagnostic_depth=2,
            environmental_complexity=0.25,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_query_perf_sort_spill_branch_order_sort_spill_simple_"
                "MockLLMAgent.json",
            ),
        ),
        table="branch_order_line",
        fault_work_mem="4MB",
        recommended_work_mem="256MB",
        max_safe_work_mem="256MB",
        start_fingerprint_probe=False,
        fault_fingerprint_sql=_PGQUERYPERFSORTSPILL_SIMPLE_SQL,
        slow_queries=(_PGQUERYPERFSORTSPILL_SIMPLE_SQL,),
    )
)

_PGQUERYPERFSORTSPILLSCENARIO_CASE = PgQueryPerfSortSpillForBranchOrderSortSpillScenarioCase(
    case_id='branch_order_sort_spill',
    runtime=PostgresCaseRuntime(resources=QUERY_PERF_RESOURCES),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "finance channel revenue report",
                    "entity": "branch_order_sort_spill",
                    "evidence": [
                        "scripted diagnostic actions observed finance channel revenue report"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "work_mem too low for report",
                    "entity": "branch_order_sort_spill",
                    "evidence": [
                        "scripted diagnostic actions observed work_mem too low for report"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "sort spills to disk",
                    "entity": "branch_order_sort_spill",
                    "evidence": [
                        "scripted diagnostic actions observed sort spills to disk"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "set the targeted report work_mem"
            ],
            "verification": [
                "verified an in-memory sort"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgQueryPerfSortSpillForBranchOrderSortSpillEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcdsx:latest',
    workload_tag='tpcdsx',
    dataset_scale=1,
    deployment_memory_mb=768,
    title='Simulates sort spill to disk due to insufficient work_mem.',
    alert="Alert: the finance channel revenue report slowed sharply after 10:00. The same monthly channel margin query that usually finishes quickly now runs for much longer, while monitoring shows elevated database read/write I/O during the report window. Identify the cause and provide a verifiable, non-destructive fix.\n\nAffected query:\n\n/* finance_reporting: top_200_channel_revenue_q3_with_margin_decile */\nWITH\ncatalog_revenue AS MATERIALIZED (\n    SELECT\n        cs.aol_product_sk,\n        DATE_TRUNC('month', d.cal_date) AS revenue_month,\n        SUM(cs.aol_net_paid)   AS gross_revenue,\n        SUM(cs.aol_net_profit) AS contribution_margin,\n        COUNT(*)              AS order_count,\n        COUNT(*) FILTER (WHERE cs.aol_net_paid > 100) AS premium_lines\n    FROM assisted_order_line cs\n    JOIN calendar_day d ON d.cal_day_sk = cs.aol_sold_date_sk\n    WHERE d.cal_year = 2001\n      AND d.cal_moy = 7\n    GROUP BY cs.aol_product_sk, DATE_TRUNC('month', d.cal_date)\n),\nstore_revenue AS MATERIALIZED (\n    SELECT\n        ss.bol_product_sk,\n        DATE_TRUNC('month', d.cal_date) AS revenue_month,\n        SUM(ss.bol_net_paid)   AS gross_revenue,\n        SUM(ss.bol_net_profit) AS contribution_margin,\n        COUNT(*)              AS order_count,\n        COUNT(*) FILTER (WHERE ss.bol_quantity > 5) AS bulk_lines\n    FROM branch_order_line ss\n    JOIN calendar_day d ON d.cal_day_sk = ss.bol_sold_date_sk\n    WHERE d.cal_year = 2001\n      AND d.cal_moy = 7\n    GROUP BY ss.bol_product_sk, DATE_TRUNC('month', d.cal_date)\n),\nweb_revenue AS MATERIALIZED (\n    SELECT\n        ws.dol_product_sk,\n        DATE_TRUNC('month', d.cal_date) AS revenue_month,\n        SUM(ws.dol_net_paid)   AS gross_revenue,\n        SUM(ws.dol_net_profit) AS contribution_margin,\n        COUNT(*)              AS order_count,\n        COUNT(*) FILTER (WHERE ws.dol_net_paid > 50) AS web_premium_lines\n    FROM digital_order_line ws\n    JOIN calendar_day d ON d.cal_day_sk = ws.dol_sold_date_sk\n    WHERE d.cal_year = 2001\n      AND d.cal_moy = 7\n    GROUP BY ws.dol_product_sk, DATE_TRUNC('month', d.cal_date)\n),\nchannel_union AS MATERIALIZED (\n    SELECT 'catalog'::text AS channel,\n           cr.aol_product_sk AS item_sk,\n           cr.revenue_month,\n           cr.gross_revenue,\n           cr.contribution_margin,\n           cr.order_count,\n           cr.premium_lines AS premium_lines\n    FROM catalog_revenue cr\n    UNION ALL\n    SELECT 'branch'::text,\n           sr.bol_product_sk,\n           sr.revenue_month,\n           sr.gross_revenue,\n           sr.contribution_margin,\n           sr.order_count,\n           sr.bulk_lines\n    FROM store_revenue sr\n    UNION ALL\n    SELECT 'web'::text,\n           wr.dol_product_sk,\n           wr.revenue_month,\n           wr.gross_revenue,\n           wr.contribution_margin,\n           wr.order_count,\n           wr.web_premium_lines\n    FROM web_revenue wr\n),\nqualified_top AS MATERIALIZED (\n    SELECT\n        cu.channel,\n        cu.revenue_month,\n        cu.item_sk,\n        cu.gross_revenue,\n        cu.contribution_margin,\n        cu.order_count,\n        cu.premium_lines,\n        i.pr_category,\n        i.pr_brand,\n        i.pr_class,\n        RANK() OVER (\n            PARTITION BY cu.revenue_month, cu.channel\n            ORDER BY cu.contribution_margin DESC\n        ) AS margin_rank,\n        NTILE(100) OVER (\n            PARTITION BY cu.channel\n            ORDER BY cu.contribution_margin DESC\n        ) AS margin_decile\n    FROM channel_union cu\n    JOIN product i ON i.pr_product_sk = cu.item_sk\n),\nfinance_rollup AS MATERIALIZED (\n    SELECT\n        qt.channel,\n        qt.pr_category,\n        qt.pr_brand,\n        qt.revenue_month,\n        GROUPING(qt.channel) AS channel_rollup,\n        GROUPING(qt.pr_category) AS category_rollup,\n        GROUPING(qt.pr_brand) AS brand_rollup,\n        SUM(qt.gross_revenue)       AS monthly_revenue,\n        SUM(qt.contribution_margin) AS monthly_margin,\n        SUM(qt.order_count)         AS monthly_order_count,\n        SUM(qt.premium_lines)       AS monthly_premium_lines,\n        AVG(qt.contribution_margin / NULLIF(qt.gross_revenue, 0)) AS avg_margin_ratio,\n        COUNT(*) FILTER (WHERE qt.margin_decile <= 5) AS top_decile_count,\n        NTILE(20) OVER (\n            PARTITION BY qt.revenue_month\n            ORDER BY SUM(qt.contribution_margin) DESC\n        ) AS month_margin_tile\n    FROM qualified_top qt\n    WHERE qt.margin_rank <= 100\n    GROUP BY GROUPING SETS (\n        (qt.channel, qt.pr_category, qt.pr_brand, qt.revenue_month),\n        (qt.channel, qt.pr_category, qt.revenue_month),\n        (qt.revenue_month)\n    )\n)\nSELECT\n    fr.channel,\n    fr.pr_category,\n    fr.pr_brand,\n    fr.revenue_month,\n    fr.channel_rollup,\n    fr.category_rollup,\n    fr.brand_rollup,\n    fr.monthly_revenue,\n    fr.monthly_margin,\n    fr.monthly_order_count,\n    fr.monthly_premium_lines,\n    fr.avg_margin_ratio,\n    fr.top_decile_count,\n    fr.month_margin_tile,\n    RANK() OVER (\n        PARTITION BY fr.revenue_month, fr.channel_rollup\n        ORDER BY fr.monthly_revenue DESC, fr.monthly_margin DESC\n    ) AS revenue_rank\nFROM finance_rollup fr\nWHERE fr.month_margin_tile <= 10\nORDER BY fr.revenue_month, fr.monthly_revenue DESC, fr.pr_category, fr.pr_brand\nLIMIT 200\n\n\nDo not replace this with a simplified probe; validate the affected business report itself.",
    initial_state={'status': 'degraded', 'work_mem': '4MB', 'sort_method': 'external merge disk'},
    expected_target={'status': 'recovered', 'work_mem': 'increased', 'sort_method': 'in-memory'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table='branch_order_line',
    fault_work_mem='4MB',
    recommended_work_mem='256MB',
    max_safe_work_mem='256MB',
    start_fingerprint_probe=False,
    fault_fingerprint_sql=('\n'
 '/* finance_reporting: top_200_channel_revenue_q3_with_margin_decile */\n'
 'WITH\n'
 'catalog_revenue AS MATERIALIZED (\n'
 '    SELECT\n'
 '        cs.aol_product_sk,\n'
 "        DATE_TRUNC('month', d.cal_date) AS revenue_month,\n"
 '        SUM(cs.aol_net_paid)   AS gross_revenue,\n'
 '        SUM(cs.aol_net_profit) AS contribution_margin,\n'
 '        COUNT(*)              AS order_count,\n'
 '        COUNT(*) FILTER (WHERE cs.aol_net_paid > 100) AS premium_lines\n'
 '    FROM assisted_order_line cs\n'
 '    JOIN calendar_day d ON d.cal_day_sk = cs.aol_sold_date_sk\n'
 '    WHERE d.cal_year = 2001\n'
 '      AND d.cal_moy = 7\n'
 "    GROUP BY cs.aol_product_sk, DATE_TRUNC('month', d.cal_date)\n"
 '),\n'
 'store_revenue AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ss.bol_product_sk,\n'
 "        DATE_TRUNC('month', d.cal_date) AS revenue_month,\n"
 '        SUM(ss.bol_net_paid)   AS gross_revenue,\n'
 '        SUM(ss.bol_net_profit) AS contribution_margin,\n'
 '        COUNT(*)              AS order_count,\n'
 '        COUNT(*) FILTER (WHERE ss.bol_quantity > 5) AS bulk_lines\n'
 '    FROM branch_order_line ss\n'
 '    JOIN calendar_day d ON d.cal_day_sk = ss.bol_sold_date_sk\n'
 '    WHERE d.cal_year = 2001\n'
 '      AND d.cal_moy = 7\n'
 "    GROUP BY ss.bol_product_sk, DATE_TRUNC('month', d.cal_date)\n"
 '),\n'
 'web_revenue AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ws.dol_product_sk,\n'
 "        DATE_TRUNC('month', d.cal_date) AS revenue_month,\n"
 '        SUM(ws.dol_net_paid)   AS gross_revenue,\n'
 '        SUM(ws.dol_net_profit) AS contribution_margin,\n'
 '        COUNT(*)              AS order_count,\n'
 '        COUNT(*) FILTER (WHERE ws.dol_net_paid > 50) AS web_premium_lines\n'
 '    FROM digital_order_line ws\n'
 '    JOIN calendar_day d ON d.cal_day_sk = ws.dol_sold_date_sk\n'
 '    WHERE d.cal_year = 2001\n'
 '      AND d.cal_moy = 7\n'
 "    GROUP BY ws.dol_product_sk, DATE_TRUNC('month', d.cal_date)\n"
 '),\n'
 'channel_union AS MATERIALIZED (\n'
 "    SELECT 'catalog'::text AS channel,\n"
 '           cr.aol_product_sk AS item_sk,\n'
 '           cr.revenue_month,\n'
 '           cr.gross_revenue,\n'
 '           cr.contribution_margin,\n'
 '           cr.order_count,\n'
 '           cr.premium_lines AS premium_lines\n'
 '    FROM catalog_revenue cr\n'
 '    UNION ALL\n'
 "    SELECT 'branch'::text,\n"
 '           sr.bol_product_sk,\n'
 '           sr.revenue_month,\n'
 '           sr.gross_revenue,\n'
 '           sr.contribution_margin,\n'
 '           sr.order_count,\n'
 '           sr.bulk_lines\n'
 '    FROM store_revenue sr\n'
 '    UNION ALL\n'
 "    SELECT 'web'::text,\n"
 '           wr.dol_product_sk,\n'
 '           wr.revenue_month,\n'
 '           wr.gross_revenue,\n'
 '           wr.contribution_margin,\n'
 '           wr.order_count,\n'
 '           wr.web_premium_lines\n'
 '    FROM web_revenue wr\n'
 '),\n'
 'qualified_top AS MATERIALIZED (\n'
 '    SELECT\n'
 '        cu.channel,\n'
 '        cu.revenue_month,\n'
 '        cu.item_sk,\n'
 '        cu.gross_revenue,\n'
 '        cu.contribution_margin,\n'
 '        cu.order_count,\n'
 '        cu.premium_lines,\n'
 '        i.pr_category,\n'
 '        i.pr_brand,\n'
 '        i.pr_class,\n'
 '        RANK() OVER (\n'
 '            PARTITION BY cu.revenue_month, cu.channel\n'
 '            ORDER BY cu.contribution_margin DESC\n'
 '        ) AS margin_rank,\n'
 '        NTILE(100) OVER (\n'
 '            PARTITION BY cu.channel\n'
 '            ORDER BY cu.contribution_margin DESC\n'
 '        ) AS margin_decile\n'
 '    FROM channel_union cu\n'
 '    JOIN product i ON i.pr_product_sk = cu.item_sk\n'
 '),\n'
 'finance_rollup AS MATERIALIZED (\n'
 '    SELECT\n'
 '        qt.channel,\n'
 '        qt.pr_category,\n'
 '        qt.pr_brand,\n'
 '        qt.revenue_month,\n'
 '        GROUPING(qt.channel) AS channel_rollup,\n'
 '        GROUPING(qt.pr_category) AS category_rollup,\n'
 '        GROUPING(qt.pr_brand) AS brand_rollup,\n'
 '        SUM(qt.gross_revenue)       AS monthly_revenue,\n'
 '        SUM(qt.contribution_margin) AS monthly_margin,\n'
 '        SUM(qt.order_count)         AS monthly_order_count,\n'
 '        SUM(qt.premium_lines)       AS monthly_premium_lines,\n'
 '        AVG(qt.contribution_margin / NULLIF(qt.gross_revenue, 0)) AS avg_margin_ratio,\n'
 '        COUNT(*) FILTER (WHERE qt.margin_decile <= 5) AS top_decile_count,\n'
 '        NTILE(20) OVER (\n'
 '            PARTITION BY qt.revenue_month\n'
 '            ORDER BY SUM(qt.contribution_margin) DESC\n'
 '        ) AS month_margin_tile\n'
 '    FROM qualified_top qt\n'
 '    WHERE qt.margin_rank <= 100\n'
 '    GROUP BY GROUPING SETS (\n'
 '        (qt.channel, qt.pr_category, qt.pr_brand, qt.revenue_month),\n'
 '        (qt.channel, qt.pr_category, qt.revenue_month),\n'
 '        (qt.revenue_month)\n'
 '    )\n'
 ')\n'
 'SELECT\n'
 '    fr.channel,\n'
 '    fr.pr_category,\n'
 '    fr.pr_brand,\n'
 '    fr.revenue_month,\n'
 '    fr.channel_rollup,\n'
 '    fr.category_rollup,\n'
 '    fr.brand_rollup,\n'
 '    fr.monthly_revenue,\n'
 '    fr.monthly_margin,\n'
 '    fr.monthly_order_count,\n'
 '    fr.monthly_premium_lines,\n'
 '    fr.avg_margin_ratio,\n'
 '    fr.top_decile_count,\n'
 '    fr.month_margin_tile,\n'
 '    RANK() OVER (\n'
 '        PARTITION BY fr.revenue_month, fr.channel_rollup\n'
 '        ORDER BY fr.monthly_revenue DESC, fr.monthly_margin DESC\n'
 '    ) AS revenue_rank\n'
 'FROM finance_rollup fr\n'
 'WHERE fr.month_margin_tile <= 10\n'
 'ORDER BY fr.revenue_month, fr.monthly_revenue DESC, fr.pr_category, fr.pr_brand\n'
 'LIMIT 200\n'),
    slow_queries=('\n'
 '/* finance_reporting: top_200_channel_revenue_q3_with_margin_decile */\n'
 'WITH\n'
 'catalog_revenue AS MATERIALIZED (\n'
 '    SELECT\n'
 '        cs.aol_product_sk,\n'
 "        DATE_TRUNC('month', d.cal_date) AS revenue_month,\n"
 '        SUM(cs.aol_net_paid)   AS gross_revenue,\n'
 '        SUM(cs.aol_net_profit) AS contribution_margin,\n'
 '        COUNT(*)              AS order_count,\n'
 '        COUNT(*) FILTER (WHERE cs.aol_net_paid > 100) AS premium_lines\n'
 '    FROM assisted_order_line cs\n'
 '    JOIN calendar_day d ON d.cal_day_sk = cs.aol_sold_date_sk\n'
 '    WHERE d.cal_year = 2001\n'
 '      AND d.cal_moy = 7\n'
 "    GROUP BY cs.aol_product_sk, DATE_TRUNC('month', d.cal_date)\n"
 '),\n'
 'store_revenue AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ss.bol_product_sk,\n'
 "        DATE_TRUNC('month', d.cal_date) AS revenue_month,\n"
 '        SUM(ss.bol_net_paid)   AS gross_revenue,\n'
 '        SUM(ss.bol_net_profit) AS contribution_margin,\n'
 '        COUNT(*)              AS order_count,\n'
 '        COUNT(*) FILTER (WHERE ss.bol_quantity > 5) AS bulk_lines\n'
 '    FROM branch_order_line ss\n'
 '    JOIN calendar_day d ON d.cal_day_sk = ss.bol_sold_date_sk\n'
 '    WHERE d.cal_year = 2001\n'
 '      AND d.cal_moy = 7\n'
 "    GROUP BY ss.bol_product_sk, DATE_TRUNC('month', d.cal_date)\n"
 '),\n'
 'web_revenue AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ws.dol_product_sk,\n'
 "        DATE_TRUNC('month', d.cal_date) AS revenue_month,\n"
 '        SUM(ws.dol_net_paid)   AS gross_revenue,\n'
 '        SUM(ws.dol_net_profit) AS contribution_margin,\n'
 '        COUNT(*)              AS order_count,\n'
 '        COUNT(*) FILTER (WHERE ws.dol_net_paid > 50) AS web_premium_lines\n'
 '    FROM digital_order_line ws\n'
 '    JOIN calendar_day d ON d.cal_day_sk = ws.dol_sold_date_sk\n'
 '    WHERE d.cal_year = 2001\n'
 '      AND d.cal_moy = 7\n'
 "    GROUP BY ws.dol_product_sk, DATE_TRUNC('month', d.cal_date)\n"
 '),\n'
 'channel_union AS MATERIALIZED (\n'
 "    SELECT 'catalog'::text AS channel,\n"
 '           cr.aol_product_sk AS item_sk,\n'
 '           cr.revenue_month,\n'
 '           cr.gross_revenue,\n'
 '           cr.contribution_margin,\n'
 '           cr.order_count,\n'
 '           cr.premium_lines AS premium_lines\n'
 '    FROM catalog_revenue cr\n'
 '    UNION ALL\n'
 "    SELECT 'branch'::text,\n"
 '           sr.bol_product_sk,\n'
 '           sr.revenue_month,\n'
 '           sr.gross_revenue,\n'
 '           sr.contribution_margin,\n'
 '           sr.order_count,\n'
 '           sr.bulk_lines\n'
 '    FROM store_revenue sr\n'
 '    UNION ALL\n'
 "    SELECT 'web'::text,\n"
 '           wr.dol_product_sk,\n'
 '           wr.revenue_month,\n'
 '           wr.gross_revenue,\n'
 '           wr.contribution_margin,\n'
 '           wr.order_count,\n'
 '           wr.web_premium_lines\n'
 '    FROM web_revenue wr\n'
 '),\n'
 'qualified_top AS MATERIALIZED (\n'
 '    SELECT\n'
 '        cu.channel,\n'
 '        cu.revenue_month,\n'
 '        cu.item_sk,\n'
 '        cu.gross_revenue,\n'
 '        cu.contribution_margin,\n'
 '        cu.order_count,\n'
 '        cu.premium_lines,\n'
 '        i.pr_category,\n'
 '        i.pr_brand,\n'
 '        i.pr_class,\n'
 '        RANK() OVER (\n'
 '            PARTITION BY cu.revenue_month, cu.channel\n'
 '            ORDER BY cu.contribution_margin DESC\n'
 '        ) AS margin_rank,\n'
 '        NTILE(100) OVER (\n'
 '            PARTITION BY cu.channel\n'
 '            ORDER BY cu.contribution_margin DESC\n'
 '        ) AS margin_decile\n'
 '    FROM channel_union cu\n'
 '    JOIN product i ON i.pr_product_sk = cu.item_sk\n'
 '),\n'
 'finance_rollup AS MATERIALIZED (\n'
 '    SELECT\n'
 '        qt.channel,\n'
 '        qt.pr_category,\n'
 '        qt.pr_brand,\n'
 '        qt.revenue_month,\n'
 '        GROUPING(qt.channel) AS channel_rollup,\n'
 '        GROUPING(qt.pr_category) AS category_rollup,\n'
 '        GROUPING(qt.pr_brand) AS brand_rollup,\n'
 '        SUM(qt.gross_revenue)       AS monthly_revenue,\n'
 '        SUM(qt.contribution_margin) AS monthly_margin,\n'
 '        SUM(qt.order_count)         AS monthly_order_count,\n'
 '        SUM(qt.premium_lines)       AS monthly_premium_lines,\n'
 '        AVG(qt.contribution_margin / NULLIF(qt.gross_revenue, 0)) AS avg_margin_ratio,\n'
 '        COUNT(*) FILTER (WHERE qt.margin_decile <= 5) AS top_decile_count,\n'
 '        NTILE(20) OVER (\n'
 '            PARTITION BY qt.revenue_month\n'
 '            ORDER BY SUM(qt.contribution_margin) DESC\n'
 '        ) AS month_margin_tile\n'
 '    FROM qualified_top qt\n'
 '    WHERE qt.margin_rank <= 100\n'
 '    GROUP BY GROUPING SETS (\n'
 '        (qt.channel, qt.pr_category, qt.pr_brand, qt.revenue_month),\n'
 '        (qt.channel, qt.pr_category, qt.revenue_month),\n'
 '        (qt.revenue_month)\n'
 '    )\n'
 ')\n'
 'SELECT\n'
 '    fr.channel,\n'
 '    fr.pr_category,\n'
 '    fr.pr_brand,\n'
 '    fr.revenue_month,\n'
 '    fr.channel_rollup,\n'
 '    fr.category_rollup,\n'
 '    fr.brand_rollup,\n'
 '    fr.monthly_revenue,\n'
 '    fr.monthly_margin,\n'
 '    fr.monthly_order_count,\n'
 '    fr.monthly_premium_lines,\n'
 '    fr.avg_margin_ratio,\n'
 '    fr.top_decile_count,\n'
 '    fr.month_margin_tile,\n'
 '    RANK() OVER (\n'
 '        PARTITION BY fr.revenue_month, fr.channel_rollup\n'
 '        ORDER BY fr.monthly_revenue DESC, fr.monthly_margin DESC\n'
 '    ) AS revenue_rank\n'
 'FROM finance_rollup fr\n'
 'WHERE fr.month_margin_tile <= 10\n'
 'ORDER BY fr.revenue_month, fr.monthly_revenue DESC, fr.pr_category, fr.pr_brand\n'
 'LIMIT 200\n',),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.625,
        reference_run_ids=(
            "reference-61__pg_query_perf_sort_spill__"
            "branch_order_sort_spill__mock__r001",
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

class PgQueryPerfSortSpillInjector(BaseFaultInjector, PgQueryPerfFaultFingerprintProbe):
    """
    模拟"排序溢写与工作内存耗尽"故障。
    通过 ALTER SYSTEM SET work_mem 为较小值，使得包含 ORDER BY / GROUP BY 的查询
    触发 External Merge Disk 排序，产生大量临时文件写入。
    """

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._verify_persistent_state()
            self._activate_runtime()

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        fault_sql = config["fault_fingerprint_sql"].rstrip(";")
        with env.metrics_hidden():
            env.reconnect()
            fault_baseline_plan = env.execute_sql(
                f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {fault_sql};"
            )
            _require_sql_success(fault_baseline_plan, "capture sort-spill fault baseline")
            _require_sql_success(
                env.execute_sql(f"SET work_mem = '{self.recommended_work_mem}';"),
                "set sort-spill in-memory probe work_mem",
            )
            fixed_probe_plan = env.execute_sql(
                f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {fault_sql};"
            )
            _require_sql_success(fixed_probe_plan, "capture sort-spill in-memory probe")
            _require_sql_success(
                env.execute_sql("RESET work_mem;"),
                "reset sort-spill in-memory probe work_mem",
            )
            self._assert_sort_spill_observable(fault_baseline_plan, fixed_probe_plan)
        env.reconnect()
        seed_result = env.execute_sql(fault_sql)
        _require_sql_success(seed_result, "seed sort-spill business query")
        evidence = self._query_observability_evidence(env)
        self._assert_sort_spill_target_visible(evidence["topsql"])
        evidence.update({
            "fault_query_truth": capture_query_result_truth(seed_result, ordered=True),
            "work_mem": env.execute_sql("SHOW work_mem;"),
            "fault_baseline_plan": fault_baseline_plan,
            "fixed_probe_plan": fixed_probe_plan,
        })
        return evidence

    def _assert_sort_spill_observable(self, fault_plan, fixed_plan) -> None:
        fault_text = json.dumps(fault_plan, ensure_ascii=False, default=str).lower()
        fixed_text = json.dumps(fixed_plan, ensure_ascii=False, default=str).lower()
        if "external merge" not in fault_text and "sort space type" not in fault_text:
            raise RuntimeError(f"Sort-spill fault plan does not expose an external sort: {fault_plan}")
        if "disk" not in fault_text and "temp written blocks" not in fault_text:
            raise RuntimeError(f"Sort-spill fault plan does not expose disk/temp I/O: {fault_plan}")
        if "external merge" in fixed_text or '"sort space type": "disk"' in fixed_text:
            raise RuntimeError(
                "Sort-spill probe still spills after increasing work_mem: "
                f"work_mem={self.recommended_work_mem}, plan={fixed_plan}"
            )

    def _assert_sort_spill_target_visible(self, topsql) -> None:
        payload = _json_object(topsql, "read sort-spill topsql")
        text = json.dumps(payload.get("records", []), ensure_ascii=False, default=str).lower()
        if "branch_order_line" not in text or "bol_net_profit" not in text:
            raise RuntimeError(f"Sort-spill target report is not visible in topsql: {topsql}")
        leaked_terms = (
            "alter system",
            "pg_reload_conf",
            "external merge",
            "work_mem",
            "q80",
            "sort spill",
        )
        leaked = [term for term in leaked_terms if term in text]
        if leaked:
            raise RuntimeError(
                f"Sort-spill topsql leaks setup/root-cause terms {leaked}: {topsql}"
            )

    def quiesce(self, context: FaultLifecycleContext):
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_sort_spill")

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._install_persistent_state()
            self._activate_runtime()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.work_mem = config["work_mem"]
        self.recommended_work_mem = config["recommended_work_mem"]
        self.fault_fingerprint_sql = config["fault_fingerprint_sql"]
        self.start_fingerprint_probe = bool(config["start_fingerprint_probe"])

    def _install_persistent_state(self) -> None:
        print(f"[FaultInjector:PgQueryPerfSortSpillInjector] Injecting sort spill fault (work_mem={self.work_mem})...")
        _require_sql_success(
            self.env.execute_sql(f"ALTER SYSTEM SET work_mem = '{self.work_mem}';"),
            "install sort-spill work_mem setting",
        )
        _require_sql_success(
            self.env.execute_sql("SELECT pg_reload_conf();"),
            "reload sort-spill work_mem setting",
        )
        print(f"[FaultInjector:PgQueryPerfSortSpillInjector] work_mem set to {self.work_mem} globally.")

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql("SHOW work_mem;"),
            "verify sort-spill work_mem setting",
        )
        actual = str(payload["result"][0][0])
        if actual.lower() != str(self.work_mem).lower():
            raise RuntimeError(
                f"Sort-spill fault image work_mem mismatch: expected={self.work_mem!r}, "
                f"actual={actual!r}"
            )

    def _activate_runtime(self) -> None:
        if self.start_fingerprint_probe and self._env_supports_background_probe():
            self._start_fault_fingerprint_probe(
                sql=self.fault_fingerprint_sql,
                app_name="aiopsbench_fp_sort_spill",
            )

    def recover(self, context: FaultLifecycleContext):
        self._configure(context.config, context.env)
        print(f"[FaultInjector:PgQueryPerfSortSpillInjector] Recovering: resetting work_mem...")
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_sort_spill")
        _require_sql_success(
            self.env.execute_sql("ALTER SYSTEM RESET work_mem;"),
            "recover sort-spill work_mem setting",
        )
        _require_sql_success(
            self.env.execute_sql("SELECT pg_reload_conf();"),
            "reload recovered sort-spill work_mem setting",
        )
        print(f"[FaultInjector:PgQueryPerfSortSpillInjector] Recovery complete.")


class PgQueryPerfSortSpillScenario(PostgresScenario):
    scenario_id = 'pg_query_perf_sort_spill'
    description = 'Simulates sort spill to disk due to insufficient work_mem.'
    cases = (
        _PGQUERYPERFSORTSPILLSCENARIO_CASE,
        _PGQUERYPERFSORTSPILLSIMPLESCENARIO_CASE,
    )

    def build_fault_plan(self, case: PgQueryPerfSortSpillCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgQueryPerfSortSpillInjector,
                config={
                    'work_mem': case.fault_work_mem,
                    'recommended_work_mem': case.recommended_work_mem,
                    'start_fingerprint_probe': case.start_fingerprint_probe,
                    'fault_fingerprint_sql': case.fault_fingerprint_sql,
                },
            ),
        )
