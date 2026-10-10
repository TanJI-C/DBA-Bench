import time
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
class PgQueryPerfStaleStatisticsCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    deployment_cpus: float
    deployment_memory_mb: int
    deployment_shm_size: str
    tables: tuple[str, ...]
    fault_fingerprint_sql: str
    business_report_sql: str
    slow_queries: tuple[str, ...]
    tables_2: tuple[str, ...]
    stale_rows: int
    distribution_profile: str
    extended_statistics_name: str | None
    decoy_rows: int
    statistics_target: int = 1000
    calendar_drift: bool = False
    historical_batch_rows: int = 0
    decoy_fingerprint_sql: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfStaleStatisticsForBranchOrderHotWindowSimpleScenarioCase(
    PgQueryPerfStaleStatisticsCase
):
    pass

_SIMPLE_STALE_SQL = """/* finance_dashboard: branch_hot_window_simple */
SELECT d.cal_year, d.cal_moy, COUNT(*) AS order_lines,
       SUM(ss.bol_net_paid) AS revenue
FROM branch_order_line ss
JOIN calendar_day d ON d.cal_day_sk = ss.bol_sold_date_sk
WHERE ss.bol_product_sk = 1
  AND ss.bol_quantity = 7
  AND ss.bol_sold_date_sk = 2451911
  AND d.cal_year = 2001 AND d.cal_moy = 1
GROUP BY d.cal_year, d.cal_moy
ORDER BY revenue DESC
LIMIT 20"""

# 与受影响报表同族、同 join 形状、读上月窗的相邻 dashboard 报表。
# 仅留一条正常耗时的语句记录在 pg_stat_statements，构成第二报表实体竞争假设。
_DECOY_FINGERPRINT_SQL = """/* finance_dashboard: branch_hot_window_trend */
SELECT d.cal_year, d.cal_moy, COUNT(*) AS order_lines,
       SUM(ss.bol_net_paid) AS revenue
FROM branch_order_line ss
JOIN calendar_day d ON d.cal_day_sk = ss.bol_sold_date_sk
WHERE ss.bol_product_sk = 2
  AND ss.bol_quantity = 3
  AND ss.bol_sold_date_sk = 2451880
  AND d.cal_year = 2000 AND d.cal_moy = 12
GROUP BY d.cal_year, d.cal_moy
ORDER BY revenue DESC
LIMIT 20"""

_PGQUERYPERFSTALESTATISTICSSIMPLE_CASE = (
    PgQueryPerfStaleStatisticsForBranchOrderHotWindowSimpleScenarioCase(
        case_id="branch_order_hot_window_simple",
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
        evaluator=PgQueryPerfStaleStatisticsForBranchOrderHotWindowSimpleEvaluatorCase,
        base_image_name="aiopsbench-pg-tpcdsx:latest",
        workload_tag="tpcdsx",
        dataset_scale=1,
        deployment_cpus=0.5,
        deployment_memory_mb=256,
        deployment_shm_size="128m",
        title="Simplified hot-window report with stale branch-order statistics.",
        # 题面只保留表层症状与报表指纹，不内嵌受影响 SQL；
        # 语句由 Agent 经 pg_stat_statements / slow_queries 按指纹定位。
        alert=(
            "Alert: the January branch revenue report on the finance dashboard "
            "(report fingerprint: branch_hot_window_simple) is running far above "
            "its baseline this morning, and the January branch channel view "
            "occasionally hits the dashboard timeout. Diagnose the database-side "
            "cause and restore the report performance without changing SQL or "
            "indexes."
        ),
        initial_state={"status": "degraded", "statistics": "stale"},
        expected_target={"status": "recovered", "statistics": "updated"},
        background_workload=EMPTY_BACKGROUND_WORKLOAD,
        runtime=PostgresCaseRuntime(resources=CaseResourceSpec(
            worker_physical_cores=1,
            worker_memory_mb=512,
            container_cpu_limit=0.5,
            container_memory_mb=256,
        )),
        tables=("branch_order_line",),
        fault_fingerprint_sql=_SIMPLE_STALE_SQL,
        business_report_sql=_SIMPLE_STALE_SQL,
        slow_queries=(_SIMPLE_STALE_SQL,),
        tables_2=("branch_order_line",),
        stale_rows=1500,
        distribution_profile="single_hot_combination",
        # 统计对象名不包含 stale/hot 等根因提示字样。
        extended_statistics_name="aiopsbench_branch_order_load_baseline",
        decoy_rows=8_000,
        # 关键列统计 target 反转为低值，统计过期叠加统计粒度降级，
        # 使"只 ANALYZE / 开 autovacuum"不再充分；extended statistics target 经
        # PG16 的 max(column targets) 规则连带降级（stxstattarget=-1）。
        statistics_target=2,
        calendar_drift=True,
        historical_batch_rows=3000,
        decoy_fingerprint_sql=_DECOY_FINGERPRINT_SQL,
        difficulty=DifficultyCalibration(
            diagnostic_depth=7,
            environmental_complexity=0.825,
            reference_run_ids=(
                "pg-qp-h02c-hotwin-r4-smoke__pg_query_perf_stale_statistics__"
                "branch_order_hot_window_simple__mock__r001",
            ),
        ),
    )
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftScenarioCase(
    PgQueryPerfStaleStatisticsCase
):
    pass

_BRANCH_ORDER_DISTRIBUTION_REPORT_SQL = ('\n'
 '/* finance_dashboard: hot_channel_revenue_reforecast_v9 */\n'
 'WITH\n'
 'focus_products AS MATERIALIZED (\n'
 '    SELECT i.pr_product_sk AS item_sk\n'
 '    FROM product i\n'
 '    WHERE i.pr_product_sk BETWEEN 1 AND 40\n'
 '),\n'
 'peer_products AS MATERIALIZED (\n'
 '    SELECT i.pr_product_sk AS item_sk\n'
 '    FROM product i\n'
 '    WHERE i.pr_product_sk BETWEEN 41 AND 80\n'
 '),\n'
 'branch_hot_window AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ss.bol_product_sk AS item_sk,\n'
 '        ss.bol_sold_date_sk AS sold_date_sk,\n'
 "        'branch'::text AS channel,\n"
 '        CASE\n'
 "            WHEN c.sa_preferred_flag = 'Y' THEN 'preferred'\n"
 "            ELSE 'standard'\n"
 '        END AS account_segment,\n'
 '        SUM(ss.bol_net_paid) AS net_paid,\n'
 '        SUM(ss.bol_net_profit) AS net_profit,\n'
 '        COUNT(*) AS order_lines,\n'
 '        COUNT(*) FILTER (WHERE ss.bol_quantity >= 5) AS bulk_lines\n'
 '    FROM branch_order_line ss\n'
 '    JOIN focus_products fp ON fp.item_sk = ss.bol_product_sk\n'
 '    JOIN calendar_day d ON d.cal_day_sk = ss.bol_sold_date_sk\n'
 '    JOIN shopper_account c ON c.sa_account_sk = ss.bol_account_sk\n'
 '    WHERE d.cal_year = 2001\n'
 '      AND d.cal_moy = 1\n'
 '      AND ss.bol_sold_date_sk BETWEEN 2451911 AND 2451941\n'
 '      AND c.sa_birth_year BETWEEN 1924 AND 1992\n'
 '    GROUP BY ss.bol_product_sk, ss.bol_sold_date_sk, c.sa_preferred_flag\n'
 '),\n'
 'branch_peer_product AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ss.bol_product_sk AS item_sk,\n'
 '        ss.bol_sold_date_sk AS sold_date_sk,\n'
 "        'branch_peer_product'::text AS channel,\n"
 "        'all_accounts'::text AS account_segment,\n"
 '        SUM(ss.bol_net_paid) AS net_paid,\n'
 '        SUM(ss.bol_net_profit) AS net_profit,\n'
 '        COUNT(*) AS order_lines,\n'
 '        COUNT(*) FILTER (WHERE ss.bol_quantity >= 5) AS bulk_lines\n'
 '    FROM branch_order_line ss\n'
 '    JOIN peer_products pp ON pp.item_sk = ss.bol_product_sk\n'
 '    JOIN calendar_day d ON d.cal_day_sk = ss.bol_sold_date_sk\n'
 '    WHERE d.cal_year = 2001\n'
 '      AND d.cal_moy = 1\n'
 '      AND ss.bol_sold_date_sk BETWEEN 2451911 AND 2451941\n'
 '    GROUP BY ss.bol_product_sk, ss.bol_sold_date_sk\n'
 '),\n'
 'branch_neighbor_day AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ss.bol_product_sk AS item_sk,\n'
 '        ss.bol_sold_date_sk AS sold_date_sk,\n'
 "        'branch_neighbor_day'::text AS channel,\n"
 "        'all_accounts'::text AS account_segment,\n"
 '        SUM(ss.bol_net_paid) AS net_paid,\n'
 '        SUM(ss.bol_net_profit) AS net_profit,\n'
 '        COUNT(*) AS order_lines,\n'
 '        COUNT(*) FILTER (WHERE ss.bol_quantity >= 5) AS bulk_lines\n'
 '    FROM branch_order_line ss\n'
 '    JOIN focus_products fp ON fp.item_sk = ss.bol_product_sk\n'
 '    JOIN calendar_day d ON d.cal_day_sk = ss.bol_sold_date_sk\n'
 '    WHERE d.cal_year = 2001\n'
 '      AND d.cal_moy = 1\n'
 '      AND ss.bol_sold_date_sk BETWEEN 2451942 AND 2451972\n'
 '    GROUP BY ss.bol_product_sk, ss.bol_sold_date_sk\n'
 '),\n'
 'unified_channel AS MATERIALIZED (\n'
 '    SELECT * FROM branch_hot_window\n'
 '    UNION ALL\n'
 '    SELECT * FROM branch_peer_product\n'
 '    UNION ALL\n'
 '    SELECT * FROM branch_neighbor_day\n'
 '),\n'
 'account_rollup AS MATERIALIZED (\n'
 '    SELECT\n'
 '        uc.channel,\n'
 '        uc.sold_date_sk,\n'
 '        uc.item_sk,\n'
 '        uc.account_segment,\n'
 '        SUM(uc.net_paid) AS account_revenue,\n'
 '        SUM(uc.net_profit) AS account_margin,\n'
 '        SUM(uc.order_lines) AS account_lines,\n'
 '        SUM(uc.bulk_lines) AS account_bulk_lines\n'
 '    FROM unified_channel uc\n'
 '    GROUP BY uc.channel, uc.sold_date_sk, uc.item_sk, uc.account_segment\n'
 '),\n'
 'category_cube AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ar.channel,\n'
 '        i.pr_category,\n'
 '        i.pr_brand,\n'
 '        d.cal_year AS sales_year,\n'
 '        d.cal_moy AS sales_month,\n'
 '        ar.account_segment,\n'
 '        SUM(ar.account_lines) AS shopper_count,\n'
 '        SUM(ar.account_revenue) AS revenue,\n'
 '        SUM(ar.account_margin) AS margin,\n'
 '        SUM(ar.account_lines) AS order_lines,\n'
 '        SUM(ar.account_bulk_lines) AS bulk_lines\n'
 '    FROM account_rollup ar\n'
 '    JOIN product i ON i.pr_product_sk = ar.item_sk\n'
 '    JOIN calendar_day d ON d.cal_day_sk = ar.sold_date_sk\n'
 '    GROUP BY GROUPING SETS (\n'
 '        (ar.channel, d.cal_year, d.cal_moy, i.pr_category, i.pr_brand, ar.account_segment),\n'
 '        (ar.channel, d.cal_year, d.cal_moy, i.pr_category, ar.account_segment),\n'
 '        (ar.channel, d.cal_year, d.cal_moy),\n'
 '        ()\n'
 '    )\n'
 '),\n'
 'ranked_cube AS (\n'
 '    SELECT\n'
 '        channel,\n'
 "        COALESCE(pr_category, 'all_categories') AS category_name,\n"
 "        COALESCE(pr_brand, 'all_brands') AS brand_name,\n"
 '        sales_year,\n'
 '        sales_month,\n'
 "        COALESCE(account_segment, 'all_accounts') AS account_segment,\n"
 '        shopper_count,\n'
 '        revenue,\n'
 '        margin,\n'
 '        order_lines,\n'
 '        bulk_lines,\n'
 '        RANK() OVER (\n'
 '            PARTITION BY channel, sales_year, sales_month\n'
 '            ORDER BY revenue DESC NULLS LAST\n'
 '        ) AS channel_revenue_rank,\n'
 '        NTILE(100) OVER (\n'
 '            PARTITION BY sales_year\n'
 '            ORDER BY margin DESC NULLS LAST\n'
 '        ) AS margin_percentile\n'
 '    FROM category_cube\n'
 ')\n'
 'SELECT\n'
 '    channel,\n'
 '    category_name,\n'
 '    brand_name,\n'
 '    sales_year,\n'
 '    sales_month,\n'
 '    account_segment,\n'
 '    shopper_count,\n'
 '    revenue,\n'
 '    margin,\n'
 '    order_lines,\n'
 '    bulk_lines,\n'
 '    channel_revenue_rank,\n'
 '    margin_percentile\n'
 'FROM ranked_cube\n'
 'WHERE channel_revenue_rank <= 40\n'
 'ORDER BY sales_year, sales_month, channel, channel_revenue_rank, revenue DESC\n'
 'LIMIT 200\n')

_PGQUERYPERFSTALESTATISTICSSCENARIO_CASE = PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftScenarioCase(
    case_id='branch_order_distribution_shift',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "branch order distribution query",
                    "entity": "branch_order_distribution_shift",
                    "evidence": [
                        "scripted diagnostic actions observed branch order distribution query"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "stale branch order statistics",
                    "entity": "branch_order_distribution_shift",
                    "evidence": [
                        "scripted diagnostic actions observed stale branch order statistics"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "large row estimate error",
                    "entity": "branch_order_distribution_shift",
                    "evidence": [
                        "scripted diagnostic actions observed large row estimate error"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "degraded statistics target on bol_sold_date_sk",
                    "entity": "branch_order_distribution_shift",
                    "evidence": [
                        "scripted diagnostic actions observed degraded statistics target on bol_sold_date_sk"
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
    evaluator=PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase,
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.733333,
        reference_run_ids=(
            "reference-36__pg_query_perf_stale_statistics__"
            "branch_order_distribution_shift__mock__r001",
        ),
    ),
    base_image_name='aiopsbench-pg-tpcdsx:latest',
    workload_tag='tpcdsx',
    dataset_scale=1,
    deployment_cpus=0.5,
    deployment_memory_mb=256,
    deployment_shm_size='128m',
    title='Simulates stale statistics on target tables to cause cardinality estimation errors.',
    alert=("Alert: the January hot-channel revenue reforecast report breached its latency SLO this morning — "
           "the same report that finished within its usual runtime yesterday now runs far past the reporting threshold. "
           "Finance needs the regression resolved urgently without changing the report SQL or its session execution environment."),
    initial_state={'status': 'degraded', 'statistics': 'stale'},
    expected_target={'status': 'recovered', 'statistics': 'updated'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=CaseResourceSpec(
        worker_physical_cores=1,
        worker_memory_mb=512,
        container_cpu_limit=1.0,
        container_memory_mb=512,
    )),
    tables=('branch_order_line',),
    fault_fingerprint_sql=_BRANCH_ORDER_DISTRIBUTION_REPORT_SQL,
    business_report_sql=_BRANCH_ORDER_DISTRIBUTION_REPORT_SQL,
    slow_queries=(_BRANCH_ORDER_DISTRIBUTION_REPORT_SQL,),
    tables_2=('branch_order_line',),
        stale_rows=100_000,
        distribution_profile='distributed_window',
        extended_statistics_name=None,
        decoy_rows=120_000,
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

class PgQueryPerfStaleStatisticsInjector(BaseFaultInjector, PgQueryPerfFaultFingerprintProbe):
    """
    通过先分析基线数据、再关闭 autovacuum 并批量写入新分布数据，
    模拟"统计信息陈旧与基数估计偏差"故障。
    目标表由 config["tables"] 提供。目前该注入器针对 TPC-DS store_sales
    的验证查询构造真实数据变化，不直接修改 pg_class 统计字段。
    """

    STALE_TICKET_BASE = 2_000_000_000
    HOT_PRODUCT_MIN = 1
    HOT_PRODUCT_MAX = 40
    CLEANUP_MAX_ROWS = 1_000_000
    # 上月促销组合批量加载回放（报表窗口之外的组合，构成语句历史内的
    # 同表竞争批次；直方图覆盖其日期区域，不构成计划误差来源）。
    REPLAY_TICKET_BASE = 1_900_000_000
    REPLAY_ROWS = 3_000
    REPLAY_DATE_SK = 2_451_880
    # 维护窗部分列统计刷新。PG16 实测该形态会更新 last_analyze /
    # reltuples / n_live_tup，但不重置 n_mod_since_analyze，也不触碰
    # STATISTICS_TARGET_COLUMNS 三关键列的统计内容——表级计数器转为"新鲜"
    # 而计划误差保持，构成真实的时间/阶段归因面。
    MAINTENANCE_ANALYZE_COLUMNS = ("bol_account_sk", "bol_net_paid")
    # 当前报表（v9）由 BI 存储过程执行——CALL 记录入 pg_stat_statements，
    # 过程内语句不入语句历史（track='top' 不追踪嵌套语句，PG16 实测），表名必须经
    # pg_proc/pg_get_functiondef 过程体解析才能取得。
    INCIDENT_PROCEDURE_NAME = "sp_hot_channel_revenue_reforecast"
    # 上月版本报表痕迹——同族名、明文 SQL、走 decoy 表、12 月窗，构成
    # "最慢同族痕迹"修复目标错误陷阱；语句结构与 v9 过程体及渠道报表可区分。
    PRIOR_VERSION_REPORT_TRACE = (
        "/* finance_dashboard: hot_channel_revenue_reforecast_v8 */\n"
        "SELECT count(*) AS rebate_lines, SUM(aol.aol_sales_price) AS rebate_base\n"
        "FROM assisted_order_line aol\n"
        "JOIN calendar_day d ON d.cal_day_sk = aol.aol_sold_date_sk\n"
        "WHERE d.cal_year = 2001 AND d.cal_moy = 12\n"
        "  AND aol.aol_sold_date_sk BETWEEN 2451880 AND 2451888;"
    )
    DECOY_ORDER_BASES = {
        "assisted_order_line": 2_100_000_000,
        "digital_order_line": 2_130_000_000,
    }
    # 上月批量加载批次的 ticket 段与单一热组合（hot_window Case）。
    # 该批次在基线 ANALYZE 之前插入、被基线统计覆盖，不参与过期账目，
    # 但构成表内最大热组合与故障批次（1500 行）的组合级竞争假设。
    HISTORICAL_TICKET_BASE = 1_900_000_000
    HISTORICAL_BATCH_DATE_SK = 2451880
    HISTORICAL_BATCH_PRODUCT_SK = 1
    HISTORICAL_BATCH_QUANTITY = 7
    CALENDAR_DRIFT_TABLE = "calendar_day"
    CALENDAR_DRIFT_YEAR = 2001
    CALENDAR_DRIFT_MONTH = 1
    STATISTICS_TARGET_COLUMNS = (
        "bol_product_sk",
        "bol_quantity",
        "bol_sold_date_sk",
    )
    # 复合根因第二因子——关键日期列统计粒度降级。在 baseline 计划快照
    # 之后、漂移写入之前把 bol_sold_date_sk 的统计 target 降为低值：故障态统计
    # 内容保持逐位一致（fault plan/误差比不变），而后续任何全列 ANALYZE 只能以
    # 低粒度（MCV 上限 = target 个值、直方图 = target 桶）重采日期列，报表窗口
    # 选择度无法被分辨——"只刷新统计"的通用维护动作不再满足 OP，完整修复必须
    # 恢复列统计 target（默认 -1 或合理区间值）后再 ANALYZE。
    # 取 1 而非 2 的实测依据：target=2 下残余误差比
    # 2502/4=625.5 恰好压在 OP 阈值 max(2.0, 1251/2)=625.5 上，会随 actual rows
    # 方差翻转；target=1 下 est=3，残余比 834.0，稳定越线。
    DEGRADED_STATISTICS_COLUMN = "bol_sold_date_sk"
    DEGRADED_STATISTICS_TARGET = 1
    DISTRIBUTION_PROFILES = {
        "distributed_window": ("2451911 + (g % 9)", "1 + (g % 40)"),
        "single_hot_combination": ("2451911", "1"),
    }

    DECOY_REPORT_TRACES = (
        "/* finance_dashboard: assisted_channel_rebate_summary_v5 */\n"
        "SELECT count(*) AS rebate_lines, SUM(aol.aol_sales_price) AS rebate_base\n"
        "FROM assisted_order_line aol\n"
        "JOIN calendar_day d ON d.cal_day_sk = aol.aol_sold_date_sk\n"
        "WHERE d.cal_year = 2001 AND d.cal_moy = 1;",
        "/* finance_dashboard: digital_channel_monthly_close_v3 */\n"
        "SELECT count(*) AS close_lines, SUM(dol.dol_net_paid) AS close_revenue\n"
        "FROM digital_order_line dol\n"
        "JOIN calendar_day d ON d.cal_day_sk = dol.dol_sold_date_sk\n"
        "WHERE d.cal_year = 2001 AND d.cal_moy = 1;",
    )

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.tables = [
            _validate_sql_identifier(str(table), "table")
            for table in config["tables"]
        ]
        self.fault_fingerprint_sql = config["fault_fingerprint_sql"]
        self.business_report_sql = str(config["business_report_sql"])
        self.stale_rows = int(config["stale_rows"])
        self.distribution_profile = str(config["distribution_profile"])
        self.decoy_rows = int(config["decoy_rows"])
        self.calendar_drift = bool(config["calendar_drift"])
        self.historical_batch_rows = int(config.get("historical_batch_rows", 0))
        self.decoy_fingerprint_sql = str(config.get("decoy_fingerprint_sql", ""))
        self.statistics_target = int(config.get("statistics_target", 1000))
        self.incident_trace_seconds: dict[str, float] = {}
        if self.distribution_profile not in self.DISTRIBUTION_PROFILES:
            raise ValueError(
                "Unsupported stale-statistics distribution profile: "
                f"profile={self.distribution_profile!r}, "
                f"supported={sorted(self.DISTRIBUTION_PROFILES)}"
            )
        statistics_name = config["extended_statistics_name"]
        self.extended_statistics_name = (
            None
            if statistics_name is None
            else _validate_sql_identifier(str(statistics_name), "extended_statistics_name")
        )

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        if self.distribution_profile == "distributed_window":
            with env.metrics_hidden(allow_pgss_reset=True):
                for table in self.tables:
                    inserted_rows = self._count_injected_rows(table)
                    if inserted_rows < self.stale_rows:
                        raise RuntimeError(
                            "Stale-statistics fault image is missing injected rows: "
                            f"table={table}, expected={self.stale_rows}, actual={inserted_rows}"
                        )
                self._assert_extended_statistics_present()
                self.baseline_stats = {}
                self.baseline_plan = None
                self.baseline_query_seconds = None
                self.fault_stats = self._snapshot_stats()
                self.fault_plan = self._snapshot_plan()
                self.fault_query_seconds = self._plan_execution_time_seconds(self.fault_plan)
                self.fault_max_plan_error_ratio = self._max_plan_error_ratio(self.fault_plan)
                self.fault_injected_at = self._db_clock_timestamp()
                self._assert_stale_statistics_observable()
                self._reset_pg_stat_statements(env)
            self._seed_incident_workload_traces(env)
        else:
            # hot_window Case：安装期语句保留在语句历史中，activate 只做
            # 快照与可见性断言，不重建 pg_stat_statements 基线、不播种 incident 痕迹。
            with env.metrics_hidden():
                for table in self.tables:
                    inserted_rows = self._count_injected_rows(table)
                    if inserted_rows < self.stale_rows:
                        raise RuntimeError(
                            "Stale-statistics fault image is missing injected rows: "
                            f"table={table}, expected={self.stale_rows}, actual={inserted_rows}"
                        )
                self._assert_extended_statistics_present()
                self.baseline_stats = {}
                self.baseline_plan = None
                self.baseline_query_seconds = None
                self.fault_stats = self._snapshot_stats()
                self.fault_plan = self._snapshot_plan()
                self.fault_query_seconds = self._plan_execution_time_seconds(self.fault_plan)
                self.fault_max_plan_error_ratio = self._max_plan_error_ratio(self.fault_plan)
                self.fault_injected_at = self._db_clock_timestamp()
                self._assert_stale_statistics_observable()

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        evidence = self._query_observability_evidence(env)
        evidence.update({
            "baseline_stats": self.baseline_stats,
            "fault_stats": self.fault_stats,
            "fault_injected_at": self.fault_injected_at,
            "baseline_plan": self.baseline_plan,
            "fault_plan": self.fault_plan,
            "baseline_query_seconds": self.baseline_query_seconds,
            "fault_query_seconds": self.fault_query_seconds,
            "fault_max_plan_error_ratio": self.fault_max_plan_error_ratio,
            "incident_trace_seconds": dict(self.incident_trace_seconds),
        })
        return evidence

    def quiesce(self, context: FaultLifecycleContext):
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_stale_stats")

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        if config.get("distribution_profile") == "distributed_window":
            # 安装期合成语句被 pgss 基线重建吸收，事故窗口由业务报表痕迹构成。
            with env.metrics_hidden(allow_pgss_reset=True):
                self._install(config, env)
            self._seed_incident_workload_traces(env)
        else:
            # hot_window Case：安装期语句（历史批次 INSERT、baseline
            # ANALYZE、CREATE STATISTICS、相邻指纹报表 EXPLAIN）保留在语句历史中，
            # 构成"上月组合已被基线统计覆盖"的归因证据面。
            with env.metrics_hidden():
                self._install(config, env)

    def _install(self, config: dict, env):
        self._configure(config, env)
        self.baseline_stats = {}
        self.fault_stats = {}
        self.baseline_plan = None
        self.fault_plan = None
        self.fault_injected_at = None
        self.fault_max_plan_error_ratio = None
        if not self.tables:
            print(f"[FaultInjector:PgQueryPerfStaleStatisticsInjector] No tables specified.")
            return

        print(f"[FaultInjector:PgQueryPerfStaleStatisticsInjector] Injecting stale statistics on tables: {self.tables}")
        self._execute_sql_checked(
            "SET statement_timeout = '0';",
            "disable statement timeout for stale statistics injection",
        )
        self._execute_sql_checked(
            "ALTER SYSTEM SET autovacuum = off;",
            "disable background autovacuum noise for stale statistics injection",
        )
        self._execute_sql_checked("SELECT pg_reload_conf();", "reload autovacuum setting")
        self._cancel_autovacuum_noise()
        for table in self.tables:
            if table != "branch_order_line":
                raise ValueError(
                    "PgQueryPerfStaleStatisticsInjector currently supports the TPC-DS "
                    f"branch_order_line table only, got {table!r}."
                )
            # 先清理上次注入的 marker rows，关闭目标表 autovacuum，再 ANALYZE。
            # 后续插入的数据不会立刻刷新统计，从而自然制造“真实行数已变、统计仍旧”的状态。
            self._cleanup_historical_rows(table, strict=True)
            self._cleanup_injected_rows(table, strict=True)
            self._cleanup_decoy_rows(strict=True)
            self._cleanup_replay_rows(strict=True)
            self._drop_incident_procedure(strict=True)
            self._execute_sql_checked(
                f"ALTER TABLE {table} SET (autovacuum_enabled = false);",
                f"disable autovacuum on {table}",
            )
            for column in self.STATISTICS_TARGET_COLUMNS:
                self._execute_sql_checked(
                    f"ALTER TABLE {table} ALTER COLUMN {column} SET STATISTICS {self.statistics_target};",
                    f"set baseline statistics target for {table}.{column}",
                )
            if self.extended_statistics_name is not None:
                columns = ", ".join(self.STATISTICS_TARGET_COLUMNS)
                self._execute_sql_checked(
                    f"CREATE STATISTICS {self.extended_statistics_name} (mcv) "
                    f"ON {columns} FROM {table};",
                    f"create baseline extended statistics {self.extended_statistics_name}",
                )
            if self.historical_batch_rows > 0:
                # 上月批量加载批次必须在基线 ANALYZE 之前落库，
                # 使其组合进入基线 MCV，与故障批次形成"已覆盖 vs 未覆盖"的归因对照。
                self._insert_historical_batch_rows(table)
            self._execute_sql_checked(
                f"ANALYZE {table};",
                f"analyze baseline {table}",
            )
            self._prepare_decoy_noise_tables()

        self.baseline_stats = self._snapshot_stats()
        self.baseline_plan = self._snapshot_plan()
        self.baseline_query_seconds = self._plan_execution_time_seconds(self.baseline_plan)

        if self.distribution_profile == "distributed_window":
            # baseline 快照之后才降级关键列统计 target——故障态统计内容
            # （fault plan/误差比）与降级前逐位一致，target 降级只在下一次
            # ANALYZE 重采时生效。
            self._degrade_statistics_target()

        for table in self.tables:
            # 批量写入目标日期上的新事实行。这里不是篡改 pg_class，
            # 而是让 PostgreSQL 自己产生 stale statistics，真实性更强。
            self._insert_stale_distribution_rows(table)
            inserted_rows = self._count_injected_rows(table)
            if inserted_rows < self.stale_rows:
                raise AssertionError(
                    "stale statistics injection did not persist the expected marker rows: "
                    f"expected={self.stale_rows}, actual={inserted_rows}, table={table}"
                )
            print(
                "[FaultInjector:PgQueryPerfStaleStatisticsInjector] "
                f"Inserted {inserted_rows} post-ANALYZE rows into {table}; "
                "statistics are now naturally stale until ANALYZE runs."
            )
        self._insert_decoy_noise_rows()
        if self.calendar_drift:
            self._apply_calendar_period_marker_drift()
        if self.decoy_fingerprint_sql:
            # 相邻 dashboard 报表真实执行一次，留下正常耗时的语句记录。
            self._execute_sql_checked(
                f"EXPLAIN (ANALYZE, FORMAT JSON) {self.decoy_fingerprint_sql.rstrip(';')};",
                "execute adjacent fingerprint decoy report statement",
            )
        if self.distribution_profile == "distributed_window":
            # 维护窗部分列统计刷新（reset 前执行，语句被 pgss reset 吸收；
            # 其状态效果——last_analyze/reltuples 更新、关键列统计不动——保留）。
            # reset 后的可见窗口会再次执行同一语句作为 Agent-visible 维护记录。
            self._run_scoped_maintenance_analyze()
            # 当前报表由 BI 存储过程执行（hidden 块内创建，reset 后以 CALL 留痕）。
            self._create_incident_procedure()
        self.fault_injected_at = self._db_clock_timestamp()
        self.fault_stats = self._snapshot_stats()
        self.fault_plan = self._snapshot_plan()
        self.fault_query_seconds = self._plan_execution_time_seconds(self.fault_plan)
        self.fault_max_plan_error_ratio = self._max_plan_error_ratio(self.fault_plan)
        self._assert_stale_statistics_observable()
        if self.distribution_profile == "distributed_window":
            self._reset_pg_stat_statements(env)

    def _reset_pg_stat_statements(self, env) -> None:
        """事件起点重建 pg_stat_statements 观测基线。

        注入器安装期的合成语句（批量 INSERT、显式 ANALYZE、EXPLAIN 快照）不是
        真实 workload 形态，也不应作为"运维操作留痕"直接泄露故障机制；事故响应
        从全新观测基线开始。与 connection_bloat 注入器的既有做法一致。
        """
        self._execute_sql_checked(
            "SET pg_stat_statements.track = 'none'; "
            "SELECT pg_stat_statements_reset(); "
            "RESET pg_stat_statements.track;",
            "reset pg_stat_statements for stale-statistics incident baseline",
        )
        env._snapshot_pgss_baseline()

    def _degrade_statistics_target(self) -> None:
        """复合根因第二因子——关键日期列统计粒度降级。

        只在 distributed_window profile（branch_order_distribution_shift）生效；
        hidden 块内执行并被 pgss reset 吸收，状态效果（attstattarget）保留。
        证据面：pg_attribute.attstattarget 与 pg_stats 直方图边界数，完全
        Agent-visible。
        """
        column = self.DEGRADED_STATISTICS_COLUMN
        for table in self.tables:
            self._execute_sql_checked(
                f"ALTER TABLE {table} ALTER COLUMN {column} "
                f"SET STATISTICS {self.DEGRADED_STATISTICS_TARGET};",
                f"degrade statistics target for {table}.{column}",
            )

    def _run_scoped_maintenance_analyze(self) -> None:
        """维护窗部分列统计刷新。

        只刷新账目相关列（bol_account_sk/bol_net_paid），不触碰报表窗口选择度
        依赖的 bol_sold_date_sk/bol_product_sk/bol_quantity 三关键列。表级
        last_analyze/reltuples 由此转为"新鲜"，而关键列统计仍停留在漂移写入前，
        构成"统计看起来已维护、计划误差仍在"的真实归因面。
        """
        columns = ", ".join(self.MAINTENANCE_ANALYZE_COLUMNS)
        self._execute_sql_checked(
            f"ANALYZE branch_order_line ({columns});",
            "run scoped maintenance statistics refresh on branch_order_line",
        )

    def _create_incident_procedure(self) -> None:
        """创建承载当前报表（v9）的 BI 存储过程。

        过程体即报表 SQL 本体（含 v9 tag 注释）。CALL 记录进入
        pg_stat_statements，过程内语句不进入语句历史——报表对象必须经
        pg_proc/pg_get_functiondef 解析过程体取得。
        """
        body = self.business_report_sql.strip().rstrip(";")
        self._execute_sql_checked(
            f"CREATE PROCEDURE public.{self.INCIDENT_PROCEDURE_NAME}() LANGUAGE sql AS $incident_proc_body$\n"
            f"{body}\n"
            f"$incident_proc_body$;",
            "create BI reporting procedure for stale-statistics incident",
        )

    def _drop_incident_procedure(self, strict: bool = False) -> None:
        sql = f"DROP PROCEDURE IF EXISTS public.{self.INCIDENT_PROCEDURE_NAME}();"
        if strict:
            self._execute_sql_checked(sql, f"drop BI reporting procedure {self.INCIDENT_PROCEDURE_NAME}")
        else:
            self.env.execute_sql(sql)

    def _insert_replay_batch_rows(self) -> None:
        """上月促销组合批量加载回放（可见语句历史内的同表竞争批次）。"""
        self._execute_sql_checked(
            f"""
            INSERT INTO branch_order_line (
                bol_sold_date_sk,
                bol_product_sk,
                bol_account_sk,
                bol_receipt_number,
                bol_quantity,
                bol_wholesale_cost,
                bol_list_price,
                bol_sales_price,
                bol_ext_sales_price,
                bol_net_paid,
                bol_net_profit
            )
            SELECT
                {self.REPLAY_DATE_SK},
                1,
                1 + (g % 100000),
                {self.REPLAY_TICKET_BASE} + g,
                7,
                12.00,
                39.00,
                31.00,
                31.00,
                31.00,
                10.00
            FROM generate_series(1, {self.REPLAY_ROWS}) AS g;
            """,
            "insert last-month promotion replay batch into branch_order_line",
        )

    def _cleanup_replay_rows(self, strict: bool = False):
        sql = f"""
            DELETE FROM branch_order_line
            WHERE bol_product_sk BETWEEN {self.HOT_PRODUCT_MIN} AND {self.HOT_PRODUCT_MAX}
              AND bol_receipt_number BETWEEN {self.REPLAY_TICKET_BASE + 1}
                  AND {self.REPLAY_TICKET_BASE + self.CLEANUP_MAX_ROWS};
            """
        if strict:
            self._execute_sql_checked(sql, "cleanup promotion replay rows from branch_order_line")
        else:
            self.env.execute_sql(sql)

    def _cleanup_historical_rows(self, table: str, strict: bool = False):
        if self.historical_batch_rows <= 0:
            return
        end_ticket = self.HISTORICAL_TICKET_BASE + self.CLEANUP_MAX_ROWS
        sql = f"""
            DELETE FROM {table}
            WHERE bol_product_sk BETWEEN {self.HOT_PRODUCT_MIN} AND {self.HOT_PRODUCT_MAX}
              AND bol_receipt_number BETWEEN {self.HISTORICAL_TICKET_BASE + 1} AND {end_ticket};
            """
        if strict:
            self._execute_sql_checked(sql, f"cleanup historical batch rows from {table}")
        else:
            self.env.execute_sql(sql)

    def _insert_historical_batch_rows(self, table: str):
        self._execute_sql_checked(
            f"""
            INSERT INTO {table} (
                bol_sold_date_sk,
                bol_product_sk,
                bol_account_sk,
                bol_receipt_number,
                bol_quantity,
                bol_wholesale_cost,
                bol_list_price,
                bol_sales_price,
                bol_ext_sales_price,
                bol_net_paid,
                bol_net_profit
            )
            SELECT
                {self.HISTORICAL_BATCH_DATE_SK},
                {self.HISTORICAL_BATCH_PRODUCT_SK},
                1 + (g % 100000),
                {self.HISTORICAL_TICKET_BASE} + g,
                {self.HISTORICAL_BATCH_QUANTITY},
                12.00,
                39.00,
                31.00,
                31.00,
                31.00,
                10.00
            FROM generate_series(1, {self.historical_batch_rows}) AS g;
            """,
            "insert previous-month bulk-load batch into branch_order_line",
        )

    def _seed_incident_workload_traces(self, env) -> None:
        """事故起点后的业务报表执行痕迹。

        pg_stat_statements 基线重建后，以业务身份真实执行目标报表与两条同窗
        decoy 渠道报表；三者留在 pg_stat_statements/topsql/slow_queries 的
        事故窗口增量中，是 Agent 定位受影响 SQL 的唯一 workload 痕迹。
        注入器安装期语句不在此列（已在 metrics_hidden 块内执行并被 reset 吸收）。
        """
        self._execute_sql_checked(
            "SET statement_timeout = '600s';",
            "bound incident trace execution time for stale-statistics scenario",
        )
        self.incident_trace_seconds = {}
        # 可见语句历史内的同域维护记录（scoped 维护 ANALYZE + 上月组合
        # 回放批次），与业务报表痕迹共同构成 Agent 定位与归因的关键路径。
        self._run_scoped_maintenance_analyze()
        self._insert_replay_batch_rows()
        self._execute_sql_checked(
            "SELECT pg_stat_force_next_flush();",
            "flush pg stats after incident-window records",
        )
        # 目标报表经存储过程执行（CALL 留痕，表名在过程体内），并叠加
        # 上月版本 v8 明文痕迹作为修复目标竞争项。
        traces = (
            ("target_report", f"CALL public.{self.INCIDENT_PROCEDURE_NAME}();"),
            ("prior_version_report", self.PRIOR_VERSION_REPORT_TRACE),
            ("assisted_report", self.DECOY_REPORT_TRACES[0]),
            ("digital_report", self.DECOY_REPORT_TRACES[1]),
        )
        for label, sql in traces:
            started = time.monotonic()
            self._execute_sql_checked(sql, f"execute {label} incident trace")
            self.incident_trace_seconds[label] = round(time.monotonic() - started, 3)
        self._execute_sql_checked(
            "RESET statement_timeout;",
            "restore session statement timeout after incident traces",
        )

    def _assert_stale_statistics_observable(self) -> None:
        for table in self.tables:
            inserted_rows = self._count_injected_rows(table)
            if inserted_rows < self.stale_rows:
                raise RuntimeError(
                    "Stale-statistics injected row count is below the Case requirement: "
                    f"table={table}, expected={self.stale_rows}, actual={inserted_rows}"
                )

            stats_payload = _json_object(
                self.fault_stats[table],
                f"read stale-statistics visibility for {table}",
            )
            rows = stats_payload.get("result", [])
            if not rows:
                raise RuntimeError(
                    f"Stale-statistics visibility query returned no row for table={table}"
                )
            row = rows[0]
            reltuples = float(row[0])
            n_live_tup = float(row[2] or 0)
            n_mod_since_analyze = float(row[4] or 0)
            if n_mod_since_analyze < 2500 and n_live_tup <= reltuples:
                raise RuntimeError(
                    "Stale-statistics mutation is not visible in PostgreSQL statistics: "
                    f"table={table}, reltuples={reltuples}, n_live_tup={n_live_tup}, "
                    f"n_mod_since_analyze={n_mod_since_analyze}"
                )

        if self.fault_max_plan_error_ratio is None:
            raise RuntimeError(
                "Stale-statistics fault plan snapshot did not yield a plan error ratio; "
                f"fault_plan={self.fault_plan!r}"
            )
        if self.fault_max_plan_error_ratio < 10.0:
            raise RuntimeError(
                "Stale-statistics plan does not show the required estimate/actual mismatch: "
                f"ratio={self.fault_max_plan_error_ratio}, required=10.0, "
                f"plan={self.fault_plan}"
            )

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        self._configure(context.config, env)
        print(f"[FaultInjector:PgQueryPerfStaleStatisticsInjector] Recovering statistics and autovacuum for tables: {self.tables}")
        _require_sql_success(env.execute_sql("SET statement_timeout = '0';"), "disable recovery statement timeout")
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_stale_stats")
        for table in self.tables:
            self._cleanup_historical_rows(table)
            self._cleanup_injected_rows(table, strict=True)
            self._cleanup_decoy_rows()
            self._cleanup_replay_rows(strict=True)
            self._drop_incident_procedure(strict=True)
            for column in self.STATISTICS_TARGET_COLUMNS:
                _require_sql_success(
                    env.execute_sql(
                        f"ALTER TABLE {table} ALTER COLUMN {column} SET STATISTICS -1;"
                    ),
                    f"restore default statistics target for {table}.{column}",
                )
            _require_sql_success(
                env.execute_sql(f"ALTER TABLE {table} RESET (autovacuum_enabled); ANALYZE {table};"),
                f"restore stale-statistics table {table}",
            )
        for table in self.DECOY_ORDER_BASES:
            _require_sql_success(
                env.execute_sql(f"ALTER TABLE {table} RESET (autovacuum_enabled); ANALYZE {table};"),
                f"restore stale-statistics decoy table {table}",
            )
        if self.calendar_drift:
            # 值保持型维护 UPDATE 无业务值需要还原；ANALYZE 清掉漂移期统计账目。
            _require_sql_success(
                env.execute_sql(f"ANALYZE {self.CALENDAR_DRIFT_TABLE};"),
                "restore calendar_day statistics after stale-statistics scenario",
            )
        if self.extended_statistics_name is not None:
            # Agent 可能已在修复中删除该统计对象（合法 SQL）；恢复必须幂等。
            _require_sql_success(
                env.execute_sql(f"DROP STATISTICS IF EXISTS {self.extended_statistics_name};"),
                f"drop stale-statistics extended statistics {self.extended_statistics_name}",
            )
        _require_sql_success(
            env.execute_sql("ALTER SYSTEM RESET autovacuum;"),
            "reset autovacuum after stale-statistics scenario",
        )
        _require_sql_success(
            env.execute_sql("SELECT pg_reload_conf();"),
            "reload autovacuum after stale-statistics scenario",
        )

    def _cleanup_injected_rows(self, table: str, strict: bool = False):
        end_ticket = self.STALE_TICKET_BASE + self.CLEANUP_MAX_ROWS
        sql = f"""
            DELETE FROM {table}
            WHERE bol_product_sk BETWEEN {self.HOT_PRODUCT_MIN} AND {self.HOT_PRODUCT_MAX}
              AND bol_receipt_number BETWEEN {self.STALE_TICKET_BASE + 1} AND {end_ticket};
            """
        if strict:
            self._execute_sql_checked(sql, f"cleanup injected rows from {table}")
        else:
            self.env.execute_sql(sql)

    def _cancel_autovacuum_noise(self):
        self._execute_sql_checked(
            """
            SELECT pg_cancel_backend(pid)
            FROM pg_stat_activity
            WHERE backend_type = 'autovacuum worker';
            """,
            "cancel background autovacuum workers before stale statistics injection",
        )

    def _insert_stale_distribution_rows(self, table: str):
        date_expression, product_expression = self.DISTRIBUTION_PROFILES[self.distribution_profile]
        batch_size = 10_000
        for start_offset in range(1, self.stale_rows + 1, batch_size):
            end_offset = min(start_offset + batch_size - 1, self.stale_rows)
            start_ticket = self.STALE_TICKET_BASE + start_offset
            end_ticket = self.STALE_TICKET_BASE + end_offset
            self._execute_sql_checked(
                f"""
            INSERT INTO {table} (
                bol_sold_date_sk,
                bol_product_sk,
                bol_account_sk,
                bol_receipt_number,
                bol_quantity,
                bol_wholesale_cost,
                bol_list_price,
                bol_sales_price,
                bol_ext_sales_price,
                bol_net_paid,
                bol_net_profit
            )
            SELECT
                {date_expression},
                {product_expression},
                1 + (g % 100000),
                {self.STALE_TICKET_BASE} + g,
                7,
                12.00,
                39.00,
                31.00,
                31.00,
                31.00,
                10.00
            FROM generate_series({start_offset}, {end_offset}) AS g
            WHERE {self.STALE_TICKET_BASE} + g BETWEEN {start_ticket} AND {end_ticket};
            """,
                f"insert stale rows {start_offset}-{end_offset} into {table}",
            )
        self._execute_sql_checked("SELECT pg_stat_force_next_flush();", "flush pg stats after stale row insert")

    def _assert_extended_statistics_present(self) -> None:
        if self.extended_statistics_name is None:
            return
        payload = self._execute_sql_checked(
            "SELECT stxname FROM pg_statistic_ext "
            f"WHERE stxnamespace = 'public'::regnamespace AND stxname = '{self.extended_statistics_name}';",
            f"verify stale-statistics extended statistics {self.extended_statistics_name}",
        )
        rows = payload.get("result", [])
        if rows != [[self.extended_statistics_name]]:
            raise RuntimeError(
                "Stale-statistics fault image is missing the required extended statistics: "
                f"name={self.extended_statistics_name!r}, rows={rows!r}"
            )

    def _prepare_decoy_noise_tables(self):
        for table in self.DECOY_ORDER_BASES:
            self._execute_sql_checked(
                f"ALTER TABLE {table} SET (autovacuum_enabled = false);",
                f"disable autovacuum on decoy table {table}",
            )
            self._execute_sql_checked(f"ANALYZE {table};", f"analyze baseline decoy table {table}")

    def _cleanup_decoy_rows(self, strict: bool = False):
        for table, base in self.DECOY_ORDER_BASES.items():
            prefix = "aol" if table == "assisted_order_line" else "dol"
            sql = f"""
                DELETE FROM {table}
                WHERE {prefix}_order_number BETWEEN {base + 1} AND {base + self.CLEANUP_MAX_ROWS};
                """
            if strict:
                self._execute_sql_checked(sql, f"cleanup stale statistics decoy rows from {table}")
            else:
                self.env.execute_sql(sql)

    def _insert_decoy_noise_rows(self):
        if self.distribution_profile == "single_hot_combination":
            self._insert_hot_window_decoy_noise_rows()
            return
        self._execute_sql_checked(
            f"""
            INSERT INTO assisted_order_line (
                aol_sold_date_sk,
                aol_product_sk,
                aol_bill_account_sk,
                aol_order_number,
                aol_quantity,
                aol_wholesale_cost,
                aol_list_price,
                aol_sales_price,
                aol_ext_sales_price,
                aol_net_paid,
                aol_net_profit
            )
            SELECT
                2451930 + (g % 5),
                3 + (g % 17),
                1 + (g % 100000),
                {self.DECOY_ORDER_BASES["assisted_order_line"]} + g,
                2 + (g % 4),
                11.00,
                34.00,
                27.00,
                27.00,
                27.00,
                8.00
            FROM generate_series(1, {self.decoy_rows}) AS g;
            """,
            "insert assisted_order_line stale-statistics decoy rows",
        )
        self._execute_sql_checked(
            f"""
            INSERT INTO digital_order_line (
                dol_sold_date_sk,
                dol_product_sk,
                dol_bill_account_sk,
                dol_order_number,
                dol_quantity,
                dol_wholesale_cost,
                dol_list_price,
                dol_sales_price,
                dol_ext_sales_price,
                dol_net_paid,
                dol_net_profit
            )
            SELECT
                2451980 + (g % 7),
                23 + (g % 19),
                1 + (g % 100000),
                {self.DECOY_ORDER_BASES["digital_order_line"]} + g,
                1 + (g % 5),
                9.00,
                29.00,
                21.00,
                21.00,
                21.00,
                6.00
            FROM generate_series(1, {self.decoy_rows}) AS g;
            """,
            "insert digital_order_line stale-statistics decoy rows",
        )
        self._execute_sql_checked("SELECT pg_stat_force_next_flush();", "flush pg stats after stale-statistics decoy insert")

    def _insert_hot_window_decoy_noise_rows(self):
        # 渠道表 decoy 与目标故障同窗、同热销形态：assisted 渠道 1 月上旬促销
        # （与故障相同的 2451911..2451919 窗口、热销品 1..40、数量 5..9），
        # digital 渠道紧随其后的 2 月窗口（2451942..2451972）。修改量（各 8000 行）
        # 高于目标表（stale_rows=1500），使"最近哪些表改了"的调查必须结合报表
        # 实际读取的表与计划误差节点做渠道归属判定，而不是按修改量排序修复。
        self._execute_sql_checked(
            f"""
            INSERT INTO assisted_order_line (
                aol_sold_date_sk,
                aol_product_sk,
                aol_bill_account_sk,
                aol_order_number,
                aol_quantity,
                aol_wholesale_cost,
                aol_list_price,
                aol_sales_price,
                aol_ext_sales_price,
                aol_net_paid,
                aol_net_profit
            )
            SELECT
                2451911 + (g % 9),
                1 + (g % 40),
                1 + (g % 100000),
                {self.DECOY_ORDER_BASES["assisted_order_line"]} + g,
                5 + (g % 5),
                12.00,
                39.00,
                31.00,
                31.00,
                31.00,
                10.00
            FROM generate_series(1, {self.decoy_rows}) AS g;
            """,
            "insert assisted_order_line stale-statistics decoy rows",
        )
        self._execute_sql_checked(
            f"""
            INSERT INTO digital_order_line (
                dol_sold_date_sk,
                dol_product_sk,
                dol_bill_account_sk,
                dol_order_number,
                dol_quantity,
                dol_wholesale_cost,
                dol_list_price,
                dol_sales_price,
                dol_ext_sales_price,
                dol_net_paid,
                dol_net_profit
            )
            SELECT
                2451942 + (g % 31),
                1 + (g % 40),
                1 + (g % 100000),
                {self.DECOY_ORDER_BASES["digital_order_line"]} + g,
                4 + (g % 6),
                9.00,
                29.00,
                21.00,
                21.00,
                21.00,
                6.00
            FROM generate_series(1, {self.decoy_rows}) AS g;
            """,
            "insert digital_order_line stale-statistics decoy rows",
        )
        self._execute_sql_checked("SELECT pg_stat_force_next_flush();", "flush pg stats after stale-statistics decoy insert")

    def _apply_calendar_period_marker_drift(self):
        # 与促销期渠道批量加载同一维护窗的维表例行收尾。
        # 对受影响查询 join 的 calendar_day 2001-01 行做值保持型期间标记清理，
        # 产生真实的统计漂移（n_mod_since_analyze/n_dead_tup）与语句历史记录，
        # 形成"同机制、错误对象"的竞争假设；这些行的标记本就为 'N'，不改变
        # 任何报表可读到的业务值，恢复时无需还原数据。
        self._execute_sql_checked(
            f"""
            UPDATE {self.CALENDAR_DRIFT_TABLE}
            SET cal_current_month = 'N',
                cal_current_year = 'N'
            WHERE cal_year = {self.CALENDAR_DRIFT_YEAR}
              AND cal_moy = {self.CALENDAR_DRIFT_MONTH};
            """,
            "apply calendar_day period-marker maintenance drift",
        )

    def _count_injected_rows(self, table: str) -> int:
        end_ticket = self.STALE_TICKET_BASE + self.stale_rows
        result = self._execute_sql_checked(
            f"""
            SELECT COUNT(*)
            FROM {table}
            WHERE bol_product_sk BETWEEN {self.HOT_PRODUCT_MIN} AND {self.HOT_PRODUCT_MAX}
              AND bol_receipt_number BETWEEN {self.STALE_TICKET_BASE + 1} AND {end_ticket};
            """,
            f"count injected rows in {table}",
        )
        rows = result.get("result", [])
        if not rows or not rows[0]:
            return 0
        return int(rows[0][0] or 0)

    def _execute_sql_checked(self, sql: str, context: str) -> dict:
        result = self.env.execute_sql(sql)
        if isinstance(result, str):
            try:
                payload = json.loads(result)
            except Exception as exc:
                raise AssertionError(f"{context} returned non-JSON result: {result}") from exc
        elif isinstance(result, dict):
            payload = result
        else:
            raise AssertionError(f"{context} returned unexpected result type: {type(result).__name__}")
        if payload.get("status") == "error":
            raise AssertionError(f"{context} failed: {json.dumps(payload, ensure_ascii=False, default=str)}")
        return payload

    def _snapshot_stats(self) -> dict:
        snapshots = {}
        for table in getattr(self, "tables", []):
            sql = (
                "SELECT c.reltuples, c.relpages, s.n_live_tup, s.last_analyze, s.n_mod_since_analyze "
                "FROM pg_class c "
                "LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid "
                f"WHERE c.relname = '{table}';"
            )
            snapshots[table] = self.env.execute_sql(sql)
        return snapshots

    def _snapshot_plan(self):
        if not getattr(self, "fault_fingerprint_sql", None):
            return None
        # TPC-DS scale=1 fault plans can exceed 300s on the 1-CPU constrained
        # PG Docker profile when the host's allocated cores are contended by
        # unrelated load (cancel at 300s with a busy SMT
        # sibling; warm-cache snapshot otherwise runs 20-60s). Setup-only
        # snapshots get a timeout safely above that worst case; the session is
        # discarded before the Agent is admitted.
        self.env.execute_sql("SET statement_timeout = '600s';")
        return self.env.execute_sql(
            f"EXPLAIN (ANALYZE, FORMAT JSON) {self.fault_fingerprint_sql.rstrip(';')};"
        )

    def _plan_execution_time_seconds(self, raw_plan):
        if isinstance(raw_plan, str):
            try:
                raw_plan = json.loads(raw_plan)
            except Exception:
                return None
        rows = raw_plan.get("result", []) if isinstance(raw_plan, dict) else []
        if not rows or not rows[0]:
            return None
        payload = rows[0][0] if isinstance(rows[0], (list, tuple)) and rows[0] else rows[0]
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                return None
        if isinstance(payload, list) and payload:
            payload = payload[0]
        if not isinstance(payload, dict):
            return None
        try:
            return float(payload.get("Execution Time")) / 1000.0
        except (TypeError, ValueError):
            return None

    def _db_clock_timestamp(self):
        payload = self._execute_sql_checked(
            "SELECT clock_timestamp();",
            "capture stale statistics injection timestamp",
        )
        rows = payload.get("result", [])
        if not rows or not rows[0]:
            raise AssertionError(f"clock_timestamp returned no rows: {payload}")
        return rows[0][0]

    def _max_plan_error_ratio(self, raw_plan):
        if isinstance(raw_plan, str):
            try:
                raw_plan = json.loads(raw_plan)
            except Exception:
                return None
        rows = raw_plan.get("result", []) if isinstance(raw_plan, dict) else []
        if not rows or not rows[0]:
            return None
        payload = rows[0][0] if isinstance(rows[0], (list, tuple)) and rows[0] else rows[0]
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                return None
        if isinstance(payload, list) and payload:
            payload = payload[0]
        plan = payload.get("Plan") if isinstance(payload, dict) else None
        ratios = []
        self._collect_plan_error_ratios(plan, ratios)
        return max(ratios) if ratios else None

    def _collect_plan_error_ratios(self, plan, ratios: list):
        if not isinstance(plan, dict):
            return
        if plan.get("Relation Name") == "branch_order_line":
            try:
                plan_rows = float(plan.get("Plan Rows", 0) or 0)
                actual_rows = float(plan.get("Actual Rows", 0) or 0)
                if plan_rows > 0:
                    ratios.append(max(actual_rows / plan_rows, plan_rows / max(actual_rows, 1.0)))
            except (TypeError, ValueError):
                pass
        for child in plan.get("Plans", []) or []:
            self._collect_plan_error_ratios(child, ratios)


class PgQueryPerfStaleStatisticsScenario(PostgresScenario):
    scenario_id = 'pg_query_perf_stale_statistics'
    description = 'Simulates stale statistics on target tables to cause cardinality estimation errors.'
    cases = (_PGQUERYPERFSTALESTATISTICSSCENARIO_CASE, _PGQUERYPERFSTALESTATISTICSSIMPLE_CASE)

    def build_fault_plan(self, case: PgQueryPerfStaleStatisticsCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgQueryPerfStaleStatisticsInjector,
                config={
                    'tables': case.tables_2,
                    'stale_rows': case.stale_rows,
                    'fault_fingerprint_sql': case.fault_fingerprint_sql,
                    'business_report_sql': case.business_report_sql,
                    'distribution_profile': case.distribution_profile,
                    'extended_statistics_name': case.extended_statistics_name,
                    'decoy_rows': case.decoy_rows,
                    'calendar_drift': case.calendar_drift,
                    'historical_batch_rows': case.historical_batch_rows,
                    'decoy_fingerprint_sql': case.decoy_fingerprint_sql,
                    'statistics_target': case.statistics_target,
                },
            ),
        )
