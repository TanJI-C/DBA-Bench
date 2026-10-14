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
from src.scenarios.postgres.common import (
    build_query_perf_noise_profiles,
)
from src.workloads.specs import WorkloadProfile

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
class PgQueryPerfMissingIndexCase(PostgresScenarioCase):
    table: str
    column: str
    fault_fingerprint_sql: str
    slow_queries: tuple[str, ...]
    index_name: str
    remediation_index_name: str
    remediation_include_columns: tuple[str, ...]
    visible_column_index_name: str
    real_scan_target_seconds: float
    real_scan_batch_rows: int
    real_scan_max_rows: int
    start_slow_query_probe: bool
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    shadow_table_name: str | None = None
    neighbor_pattern_index_name: str | None = None
    # 修复决策诱饵（均为真实近邻、可由证据排除）：
    # remnant_expression_index_name —— 同列 left(col,3) 表达式索引残迹，数据语义等价
    #   但计划器按表达式语法匹配，不服务 substring 等值查询；
    # neighbor_price_index_name —— 价格列普通 b-tree，被 merch_price_band_audit
    #   profile 真实使用，配合 fingerprint 的跨列 margin 谓词构成"该在哪列建索引"
    #   的目标辨别面。
    remnant_expression_index_name: str | None = None
    neighbor_price_index_name: str | None = None
    placeholder_batch_fk_table: str | None = None
    placeholder_batch_fk_column: str | None = None
    placeholder_batch_fk_constraint: str | None = None
    placeholder_batch_campaign_sk_start: int = 900_000
    placeholder_batch_campaign_stride: int = 0

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfMissingIndexForProductCategorySubstringScenarioCase(PgQueryPerfMissingIndexCase):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfMissingIndexForProductCategoryPrefixSimpleScenarioCase(PgQueryPerfMissingIndexCase):
    pass

_PGQUERYPERFMISSINGINDEXSCENARIO_CASE = PgQueryPerfMissingIndexForProductCategorySubstringScenarioCase(
    case_id='product_category_substring',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "product category substring query",
                    "entity": "product_category_substring",
                    "evidence": [
                        "scripted diagnostic actions observed product category substring query"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "missing substring expression index",
                    "entity": "product_category_substring",
                    "evidence": [
                        "scripted diagnostic actions observed missing substring expression index"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "substring predicate forces sequential scan",
                    "entity": "product_category_substring",
                    "evidence": [
                        "scripted diagnostic actions observed substring predicate forces sequential scan"
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
    evaluator=PgQueryPerfMissingIndexForProductCategorySubstringEvaluatorCase,
    title='Simulates inefficient predicate access patterns on a table.',
    alert=(
        "Alert: postgres-primary-1 reporting API p95 latency jumped from ~200ms to ~8s "
        "starting around 14:30 today. The degradation is confined to the analytics "
        "reporting service — the monthly store SKU velocity report family — while "
        "checkout and browsing endpoints stay at normal latency. Identify the cause "
        "and restore performance without rewriting the application."
    ),
    initial_state={'status': 'degraded', 'target_index': 'missing', 'plan': 'seq_scan'},
    expected_target={'status': 'recovered', 'index': 'created'},
    background_workload=BackgroundWorkloadSpec(
        profiles=build_query_perf_noise_profiles({75}, light_n=3) + (
            WorkloadProfile(
                name='catalog_autocomplete',
                sql=(
                    "/* app: catalog_autocomplete */\n"
                    "SELECT pr_product_sk, pr_product_name FROM product "
                    "WHERE pr_category LIKE 'Sho%' ORDER BY pr_product_name LIMIT 20"
                ),
                qps=0.25,
                tier='LIGHT',
                application_name='catalog_autocomplete',
            ),
            # 商品价格带审计——同窗同库非因果报表，真实使用
            # idx_product_pr_current_price（价格列诱饵索引的"被使用"证据源）。
            WorkloadProfile(
                name='merch_price_band_audit',
                sql=(
                    "/* app: merch_price_band_audit */\n"
                    "SELECT count(*) FROM product "
                    "WHERE pr_current_price BETWEEN 20 AND 40"
                ),
                qps=0.2,
                tier='LIGHT',
                application_name='merch_price_band_audit',
            ),
        ),
        worker_count=6,
        seed=0x5170,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
    ),
    table='product',
    column='pr_category',
    shadow_table_name='product_prestage_base',
    neighbor_pattern_index_name='idx_product_pr_category_pattern',
    remnant_expression_index_name='idx_product_pr_category_left',
    neighbor_price_index_name='idx_product_pr_current_price',
    placeholder_batch_fk_table='campaign',
    placeholder_batch_fk_column='camp_product_sk',
    placeholder_batch_fk_constraint='fk_campaign_product',
    placeholder_batch_campaign_sk_start=900_000,
    placeholder_batch_campaign_stride=37,
    # fingerprint 增加第二个真实业务谓词（margin 正值过滤）。跨列谓词
    # 无常量边界，任何单列 b-tree 都无法服务——配合价格列诱饵索引构成"该在哪列建
    # 什么索引"的目标辨别面；根因（缺 substring 表达式索引）与 OP 验收语义不变。
    fault_fingerprint_sql=('\n'
 '/* report: monthly_store_sku_velocity_q3_shoe_focus */\n'
 'WITH\n'
 'filtered_product AS MATERIALIZED (\n'
 '    SELECT\n'
 '        i.pr_product_sk,\n'
 '        i.pr_category,\n'
 '        i.pr_brand,\n'
 '        i.pr_class,\n'
 '        i.pr_current_price,\n'
 '        i.pr_wholesale_cost,\n'
 '        i.pr_manager_id\n'
 '    FROM product i\n'
 "    WHERE substring(i.pr_category, 1, 3) = 'Sho'\n"
 '      AND i.pr_wholesale_cost < i.pr_current_price\n'
 '),\n'
 'category_brand_rollup AS MATERIALIZED (\n'
 '    SELECT\n'
 '        fp.pr_category,\n'
 '        fp.pr_brand,\n'
 '        fp.pr_class,\n'
 '        COUNT(*) AS product_count,\n'
 '        AVG(fp.pr_current_price) AS avg_price,\n'
 '        SUM(fp.pr_current_price - fp.pr_wholesale_cost) AS gross_spread,\n'
 '        MAX(fp.pr_manager_id) AS max_manager\n'
 '    FROM filtered_product fp\n'
 '    GROUP BY fp.pr_category, fp.pr_brand, fp.pr_class\n'
 '),\n'
 'ranked_segments AS (\n'
 '    SELECT\n'
 '        cbr.*,\n'
 '        DENSE_RANK() OVER (\n'
 '            PARTITION BY cbr.pr_category\n'
 '            ORDER BY cbr.gross_spread DESC, cbr.product_count DESC, cbr.pr_brand\n'
 '        ) AS segment_rank,\n'
 '        PERCENT_RANK() OVER (\n'
 '            PARTITION BY cbr.pr_category\n'
 '            ORDER BY cbr.avg_price DESC\n'
 '        ) AS price_pct\n'
 '    FROM category_brand_rollup cbr\n'
 '),\n'
 'product_velocity AS (\n'
 '    SELECT\n'
 '        fp.pr_product_sk,\n'
 '        fp.pr_category,\n'
 '        fp.pr_brand,\n'
 '        fp.pr_class,\n'
 '        fp.pr_current_price,\n'
 '        rs.product_count,\n'
 '        rs.avg_price,\n'
 '        rs.gross_spread,\n'
 '        rs.max_manager,\n'
 '        rs.segment_rank,\n'
 '        rs.price_pct,\n'
 '        ROW_NUMBER() OVER (\n'
 '            PARTITION BY fp.pr_brand\n'
 '            ORDER BY fp.pr_current_price DESC, fp.pr_product_sk\n'
 '        ) AS brand_price_rank\n'
 '    FROM filtered_product fp\n'
 '    JOIN ranked_segments rs\n'
 '      ON rs.pr_category = fp.pr_category\n'
 '     AND rs.pr_brand = fp.pr_brand\n'
 '     AND rs.pr_class = fp.pr_class\n'
 '    WHERE rs.segment_rank <= 20\n'
 ')\n'
 'SELECT\n'
 '    pv.pr_category,\n'
 '    pv.pr_brand,\n'
 '    pv.pr_class,\n'
 '    pv.pr_product_sk,\n'
 '    pv.pr_current_price,\n'
 '    pv.product_count,\n'
 '    pv.avg_price,\n'
 '    pv.gross_spread,\n'
 '    pv.max_manager,\n'
 '    pv.segment_rank,\n'
 '    pv.price_pct,\n'
 '    pv.brand_price_rank\n'
 'FROM product_velocity pv\n'
 'WHERE pv.brand_price_rank <= 50\n'
 'ORDER BY pv.segment_rank, pv.gross_spread DESC, pv.pr_current_price DESC\n'
 'LIMIT 100\n'),
    slow_queries=('\n'
 '/* report: monthly_store_sku_velocity_q3_shoe_focus */\n'
 'WITH\n'
 'filtered_product AS MATERIALIZED (\n'
 '    SELECT\n'
 '        i.pr_product_sk,\n'
 '        i.pr_category,\n'
 '        i.pr_brand,\n'
 '        i.pr_class,\n'
 '        i.pr_current_price,\n'
 '        i.pr_wholesale_cost,\n'
 '        i.pr_manager_id\n'
 '    FROM product i\n'
 "    WHERE substring(i.pr_category, 1, 3) = 'Sho'\n"
 '      AND i.pr_wholesale_cost < i.pr_current_price\n'
 '),\n'
 'category_brand_rollup AS MATERIALIZED (\n'
 '    SELECT\n'
 '        fp.pr_category,\n'
 '        fp.pr_brand,\n'
 '        fp.pr_class,\n'
 '        COUNT(*) AS product_count,\n'
 '        AVG(fp.pr_current_price) AS avg_price,\n'
 '        SUM(fp.pr_current_price - fp.pr_wholesale_cost) AS gross_spread,\n'
 '        MAX(fp.pr_manager_id) AS max_manager\n'
 '    FROM filtered_product fp\n'
 '    GROUP BY fp.pr_category, fp.pr_brand, fp.pr_class\n'
 '),\n'
 'ranked_segments AS (\n'
 '    SELECT\n'
 '        cbr.*,\n'
 '        DENSE_RANK() OVER (\n'
 '            PARTITION BY cbr.pr_category\n'
 '            ORDER BY cbr.gross_spread DESC, cbr.product_count DESC, cbr.pr_brand\n'
 '        ) AS segment_rank,\n'
 '        PERCENT_RANK() OVER (\n'
 '            PARTITION BY cbr.pr_category\n'
 '            ORDER BY cbr.avg_price DESC\n'
 '        ) AS price_pct\n'
 '    FROM category_brand_rollup cbr\n'
 '),\n'
 'product_velocity AS (\n'
 '    SELECT\n'
 '        fp.pr_product_sk,\n'
 '        fp.pr_category,\n'
 '        fp.pr_brand,\n'
 '        fp.pr_class,\n'
 '        fp.pr_current_price,\n'
 '        rs.product_count,\n'
 '        rs.avg_price,\n'
 '        rs.gross_spread,\n'
 '        rs.max_manager,\n'
 '        rs.segment_rank,\n'
 '        rs.price_pct,\n'
 '        ROW_NUMBER() OVER (\n'
 '            PARTITION BY fp.pr_brand\n'
 '            ORDER BY fp.pr_current_price DESC, fp.pr_product_sk\n'
 '        ) AS brand_price_rank\n'
 '    FROM filtered_product fp\n'
 '    JOIN ranked_segments rs\n'
 '      ON rs.pr_category = fp.pr_category\n'
 '     AND rs.pr_brand = fp.pr_brand\n'
 '     AND rs.pr_class = fp.pr_class\n'
 '    WHERE rs.segment_rank <= 20\n'
 ')\n'
 'SELECT\n'
 '    pv.pr_category,\n'
 '    pv.pr_brand,\n'
 '    pv.pr_class,\n'
 '    pv.pr_product_sk,\n'
 '    pv.pr_current_price,\n'
 '    pv.product_count,\n'
 '    pv.avg_price,\n'
 '    pv.gross_spread,\n'
 '    pv.max_manager,\n'
 '    pv.segment_rank,\n'
 '    pv.price_pct,\n'
 '    pv.brand_price_rank\n'
 'FROM product_velocity pv\n'
 'WHERE pv.brand_price_rank <= 50\n'
 'ORDER BY pv.segment_rank, pv.gross_spread DESC, pv.pr_current_price DESC\n'
 'LIMIT 100\n',),
    index_name='idx_product_pr_category',
    remediation_index_name='idx_product_pr_category_func',
    remediation_include_columns=(
        'pr_product_sk',
        'pr_category',
        'pr_brand',
        'pr_class',
        'pr_current_price',
        'pr_wholesale_cost',
        'pr_manager_id',
    ),
    visible_column_index_name='idx_product_pr_category_visible',
    real_scan_target_seconds=5.0,
    real_scan_batch_rows=500000,
    # probe Seq Scan 在 2.0 CPU 资源合同下实测约 0.87s/50 万行，3M 行上限最多只能
    # 到 ~2.6s，达不到 5s 校准目标。上限取 8M：静默宿主上 ~6M 行真实达到 5s，
    # 故障校准按行数自适应灌行；行数不是难度来源（probe 目标仍 5s）。
    real_scan_max_rows=8000000,
    start_slow_query_probe=False,
    base_image_name='aiopsbench-pg-tpcdsx:latest',
    workload_tag='tpcdsx',
    dataset_scale=1,
    # 资源合同说明：0.5 CPU / 256MB 容器（shared_buffers=128MB、最高 300 万行
    # feed 批次 + autovacuum + 7 个后台 profile）会触发 cgroup OOM 崩溃恢复并摧毁
    # fault 数据集，使 OP 在任何正确修复下都无法通过。故障校准由 Injector 按
    # real_scan_target_seconds 自适应灌行，资源加大不改变难度，只保证环境在一个
    # run 内存活。
    runtime=PostgresCaseRuntime(resources=CaseResourceSpec(
        worker_physical_cores=2,
        worker_memory_mb=2048,
        container_cpu_limit=2.0,
        container_memory_mb=2048,
    )),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.666667,
        reference_run_ids=(
            "logs/traces/"
            "run_pg_query_perf_missing_index_product_category_substring_"
            "MockLLMAgent.json",
        ),
    ),
)

_PGQUERYPERFMISSINGINDEXSCENARIO_SIMPLE_CASE = PgQueryPerfMissingIndexForProductCategoryPrefixSimpleScenarioCase(
    case_id='product_category_prefix_simple',
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
    evaluator=PgQueryPerfMissingIndexForProductCategoryPrefixSimpleEvaluatorCase,
    title='A single-table category-prefix report lacks a matching expression index.',
    alert=(
        "Alert: postgres-primary-1 reporting API response time has spiked from "
        "~200ms to ~8s starting around 14:30 today. The regression is concentrated "
        "on a single reporting query against the product relation. Identify the cause "
        "and restore performance without rewriting the application.\n\n"
        "Affected query:\n\n"
        "/* report: product_category_prefix_simple */\n"
        "SELECT pr_product_sk\n"
        "FROM product\n"
        "WHERE substring(pr_category, 1, 3) = 'Sho';\n\n"
        "Hint: focus on access paths — the query plan changed recently."
    ),
    initial_state={'status': 'degraded', 'target_index': 'missing', 'plan': 'seq_scan'},
    expected_target={'status': 'recovered', 'index': 'created'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table='product',
    column='pr_category',
    fault_fingerprint_sql=(
        "/* report: product_category_prefix_simple */\n"
        "SELECT pr_product_sk\n"
        "FROM product\n"
        "WHERE substring(pr_category, 1, 3) = 'Sho'"
    ),
    slow_queries=(
        "/* report: product_category_prefix_simple */\n"
        "SELECT pr_product_sk\n"
        "FROM product\n"
        "WHERE substring(pr_category, 1, 3) = 'Sho'",
    ),
    index_name='idx_product_pr_category',
    remediation_index_name='idx_product_pr_category_prefix_simple',
    remediation_include_columns=('pr_product_sk',),
    visible_column_index_name='idx_product_pr_category_visible',
    real_scan_target_seconds=5.0,
    real_scan_batch_rows=500000,
    real_scan_max_rows=3000000,
    start_slow_query_probe=False,
    base_image_name='aiopsbench-pg-tpcdsx:latest',
    workload_tag='tpcdsx',
    dataset_scale=1,
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.4,
        reference_run_ids=(
            "logs/traces/"
            "run_pg_query_perf_missing_index_product_category_prefix_simple_"
            "MockLLMAgent.json",
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

class PgQueryPerfMissingIndexInjector(BaseFaultInjector, PgQueryPerfFaultFingerprintProbe):
    """
    通过删除指定表的索引，或者提供非 SARGable 的查询语句，
    模拟"索引缺失与非 SARGable 谓词"故障。

    故障表为 item / i_category：shadow table 机制（rename + LIKE 复制）、
    表达式索引清理、可见列索引、数据扩容 probe 全部针对 item 表。substring 谓词
    substring(i_category, 1, 3)='Sho' 触发 Seq Scan；fingerprint 是 q75 + substring
    改造（Injector 内部通过 PgQueryPerfFaultFingerprintProbe mixin 在后台循环跑）。
    """
    SLOW_QUERY_APP = "report_api_product_category_probe"

    def __init__(self):
        self.env = None
        self._shadow_activated = False
        self._slow_query_thread = None
        self._slow_query_conn = None
        self._stopping_slow_query = False
        self._slow_query_error = None
        self.fault_query_seconds = None

    def _configure_from_config(self, config: dict, env):
        self.env = env
        self.table = _validate_sql_identifier(config["table"], "table")
        self.index_name = _validate_sql_identifier(
            config["index_name"], "index_name"
        )
        self.column = _validate_sql_identifier(
            config["column"], "column"
        )
        self.remediation_index_name = _validate_sql_identifier(
            config["remediation_index_name"],
            "remediation_index_name",
        )
        self.visible_column_index_name = _validate_sql_identifier(
            config["visible_column_index_name"],
            "visible_column_index_name",
        )
        self.shadow_table_name = _validate_sql_identifier(
            config["shadow_table_name"] or f"aiopsbench_{self.table}_base",
            "shadow_table_name",
        )
        self.neighbor_pattern_index_name = (
            _validate_sql_identifier(
                config["neighbor_pattern_index_name"],
                "neighbor_pattern_index_name",
            )
            if config["neighbor_pattern_index_name"]
            else None
        )
        self.remnant_expression_index_name = (
            _validate_sql_identifier(
                config["remnant_expression_index_name"],
                "remnant_expression_index_name",
            )
            if config["remnant_expression_index_name"]
            else None
        )
        self.neighbor_price_index_name = (
            _validate_sql_identifier(
                config["neighbor_price_index_name"],
                "neighbor_price_index_name",
            )
            if config["neighbor_price_index_name"]
            else None
        )
        self.placeholder_batch_fk_table = (
            _validate_sql_identifier(
                config["placeholder_batch_fk_table"],
                "placeholder_batch_fk_table",
            )
            if config["placeholder_batch_fk_table"]
            else None
        )
        self.placeholder_batch_fk_column = (
            _validate_sql_identifier(
                config["placeholder_batch_fk_column"],
                "placeholder_batch_fk_column",
            )
            if config["placeholder_batch_fk_column"]
            else None
        )
        self.placeholder_batch_fk_constraint = (
            _validate_sql_identifier(
                config["placeholder_batch_fk_constraint"],
                "placeholder_batch_fk_constraint",
            )
            if config["placeholder_batch_fk_constraint"]
            else None
        )
        self.placeholder_batch_campaign_sk_start = int(
            config["placeholder_batch_campaign_sk_start"]
        )
        self.placeholder_batch_campaign_stride = int(
            config["placeholder_batch_campaign_stride"]
        )
        self.real_scan_target_seconds = float(config["real_scan_target_seconds"])
        self.real_scan_batch_rows = int(config["real_scan_batch_rows"])
        self.real_scan_max_rows = int(config["real_scan_max_rows"])
        self.start_slow_query_probe = bool(config["start_slow_query_probe"])
        self.synthetic_key_start = 2_000_000_000
        self.placeholder_feed_rows = 0
        self.fault_fingerprint_sql = config["fault_fingerprint_sql"]

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure_from_config(config, env)

        print(f"[FaultInjector:PgQueryPerfMissingIndexInjector] Injecting missing index fault on {self.table}...")

        # 准备阶段（删索引 / 起 shadow 表 / 拷数据 / ANALYZE / 数据扩容校准）的 DDL+SQL
        # 都不该被 agent 通过 topsql/slow_queries 看到——它们是"舞台搭建"，不是故障症状。
        # _start_slow_query_probe 留在外面：那是 agent 应该发现的症状。
        with env.metrics_hidden():
            self._activate_shadow_table()
            # 只清理表达式索引。普通列索引必须保留/可见，用于检验 Agent 是否能识别
            # substring(...) 需要表达式索引，而不是误以为普通 c_last_name 索引缺失。
            self._drop_target_expression_indexes()
            self._prepare_real_scan_dataset()
            self._ensure_visible_column_index()
            self._ensure_neighbor_pattern_index()
            self._ensure_repair_decision_decoy_indexes()
            self._protect_placeholder_batch()
            self._assert_plain_column_index_observable()
        print(
            "[FaultInjector:PgQueryPerfMissingIndexInjector] Dropped expression indexes "
            f"matching {self.remediation_index_name}; ordinary {self.column} indexes are preserved."
        )

        self._activate_runtime(wait_seconds=6.0)

    def activate(self, context: FaultLifecycleContext):
        """Attach to a database that already contains this fault state and restart live symptoms."""
        config = context.config
        env = context.env
        wait_seconds = 6.0

        self._configure_from_config(config, env)
        print(
            "[FaultInjector:PgQueryPerfMissingIndexInjector] "
            "Activating existing missing-index fault state..."
        )
        with env.metrics_hidden():
            self._verify_persistent_state()
            self._shadow_activated = True
            self.fault_plan, self.fault_query_seconds = self._capture_explain_analyze(
                self.fault_fingerprint_sql,
                timeout_seconds=300,
            )
            self._assert_missing_index_plan(self.fault_plan)
        self._activate_runtime(wait_seconds=wait_seconds)

    def _review_key_sql(self) -> str:
        return self.review_key.replace("'", "''")

    def _verify_persistent_state(self) -> None:
        if not self._table_exists(self.table) or not self._table_exists(self.shadow_table_name):
            raise RuntimeError(
                "Missing-index fault image does not contain the active and shadow tables: "
                f"table={self.table}, shadow_table={self.shadow_table_name}"
            )
        if not self._column_index_exists():
            raise RuntimeError(
                "Missing-index fault image lost the visible ordinary index: "
                f"table={self.table}, column={self.column}"
            )
        if self.neighbor_pattern_index_name and not self._index_exists(
            self.neighbor_pattern_index_name
        ):
            raise RuntimeError(
                "Missing-index fault image lost the neighbor pattern index: "
                f"table={self.table}, index={self.neighbor_pattern_index_name}"
            )
        if self.remnant_expression_index_name and not self._index_exists(
            self.remnant_expression_index_name
        ):
            raise RuntimeError(
                "Missing-index fault image lost the remnant prefix expression index: "
                f"table={self.table}, index={self.remnant_expression_index_name}"
            )
        if self.neighbor_price_index_name and not self._index_exists(
            self.neighbor_price_index_name
        ):
            raise RuntimeError(
                "Missing-index fault image lost the neighbor price column index: "
                f"table={self.table}, index={self.neighbor_price_index_name}"
            )
        if self.placeholder_batch_fk_constraint and not self._constraint_exists(
            self.placeholder_batch_fk_constraint
        ):
            raise RuntimeError(
                "Missing-index fault image lost the placeholder batch foreign key: "
                f"constraint={self.placeholder_batch_fk_constraint}, "
                f"table={self.placeholder_batch_fk_table}"
            )
        expression_indexes = self._target_expression_index_names()
        if expression_indexes:
            raise RuntimeError(
                "Missing-index fault image contains a remediation expression index: "
                f"indexes={sorted(expression_indexes)}"
            )

    def _activate_runtime(self, wait_seconds: float) -> None:
        import time

        if self.start_slow_query_probe:
            self._start_slow_query_probe()
            time.sleep(wait_seconds)
            if self._slow_query_error is not None:
                raise RuntimeError(
                    f"Missing-index slow-query probe failed: {self._slow_query_error}"
                ) from self._slow_query_error
            if self._slow_query_thread is None or not self._slow_query_thread.is_alive():
                raise RuntimeError("Missing-index slow-query probe exited before setup completed")
            if not self.env.reconnect():
                raise RuntimeError(
                    f"Missing-index activation could not reconnect to {self.env.host}:{self.env.port}"
                )
        if self._env_supports_background_probe():
            self._start_fault_fingerprint_probe(
                sql=self.fault_fingerprint_sql,
                app_name="report_api_batch",
            )

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        self._terminate_slow_query_probe()
        self._terminate_fault_fingerprint_probe(app_name="report_api_batch")
        if not self._shadow_activated:
            return
        print(
            "[FaultInjector:PgQueryPerfMissingIndexInjector] Recovering by restoring "
            f"{self.shadow_table_name} as {self.table}..."
        )
        self._release_placeholder_batch()
        self._restore_shadow_table()
        _require_sql_success(
            env.execute_sql(
                f"CREATE INDEX IF NOT EXISTS {self.index_name} "
                f"ON {self.table}({self.column});"
            ),
            f"restore missing-index base index {self.index_name}",
        )
        self._shadow_activated = False

    def _release_placeholder_batch(self) -> None:
        # 先清掉本场景注入的 onboarding campaign 行并解除 FK，否则恢复 shadow 表时
        # DROP TABLE 会因 campaign 的外键依赖失败。
        fk_table = self.placeholder_batch_fk_table
        if not fk_table:
            return
        self.env.execute_sql(f"SET statement_timeout = '0';")
        _require_sql_success(
            self.env.execute_sql(
                f"DELETE FROM {fk_table} "
                f"WHERE {self.placeholder_batch_fk_column} >= {self.synthetic_key_start};"
            ),
            f"remove injected placeholder batch rows from {fk_table}",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"ALTER TABLE {fk_table} DROP CONSTRAINT IF EXISTS "
                f"{self.placeholder_batch_fk_constraint};"
            ),
            f"drop placeholder batch foreign key {self.placeholder_batch_fk_constraint}",
        )
        self.env.execute_sql(f"ANALYZE {fk_table};")

    def prepare_observability(self, context: FaultLifecycleContext):
        import time

        config = context.config
        env = context.env
        seed_result = env.execute_sql(
            "SET statement_timeout = '60s';\n"
            + self._target_select_sql("report_api_product_category_probe")
        )
        _require_sql_success(seed_result, "seed missing-index business query")
        env.reconnect()
        deadline = time.monotonic() + 20.0
        slow_queries = env.query_metrics("slow_queries")
        while not self._slow_query_is_observable(slow_queries):
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "Missing-index query did not become visible in slow_queries within 20 seconds: "
                    f"table={self.table}, column={self.column}, slow_queries={slow_queries}"
                )
            time.sleep(1.0)
            slow_queries = env.query_metrics("slow_queries")

        # 数据集装载/舞台搭建的一次性 COPY/DDL 会以巨型 mean_exec_time 常驻
        # pg_stat_statements，把持续运行的退化指纹挤出 Agent 的检索视野。
        # 按 DBA 惯例在大批量维护后重置统计：Agent 只看到 handoff 之后真实
        # 运行的语句（probe 循环会立即重新累积）。
        env.execute_sql("SELECT pg_stat_statements_reset();")

        evidence = {
            "topsql": env.query_metrics("topsql"),
            "slow_queries": slow_queries,
        }
        evidence.update({
            "fault_query_seconds": self.fault_query_seconds,
            "seed_result": seed_result,
            "fault_plan": self.fault_plan,
        })
        return evidence

    def _assert_missing_index_plan(self, fault_plan) -> None:
        plan_text = self._result_to_text(fault_plan).lower()
        if self.table not in plan_text or "substring" not in plan_text:
            raise RuntimeError(
                "Missing-index fault plan does not contain the target substring predicate: "
                f"table={self.table}, column={self.column}, plan={fault_plan}"
            )
        if "seq scan" not in plan_text:
            raise RuntimeError(
                "Missing-index fault plan does not contain the expected sequential scan: "
                f"table={self.table}, plan={fault_plan}"
            )

    def _assert_plain_column_index_observable(self) -> None:
        if not self._column_index_exists():
            raise RuntimeError(
                "Missing-index scenario ordinary column index is not visible: "
                f"table={self.table}, column={self.column}"
            )

    def _slow_query_is_observable(self, slow_queries) -> bool:
        payload = _json_object(slow_queries, "read missing-index slow_queries")
        text = json.dumps(
            payload.get("records", []), ensure_ascii=False, default=str
        ).lower()
        return all(token in text for token in ("substring", self.column, self.table))

    def quiesce(self, context: FaultLifecycleContext):
        self._terminate_slow_query_probe()
        self._terminate_fault_fingerprint_probe(app_name="report_api_batch")

    def _start_slow_query_probe(self):
        import threading

        self._slow_query_thread = threading.Thread(
            target=self._run_slow_query_probe,
            daemon=True,
        )
        self._stopping_slow_query = False
        self._slow_query_thread.start()

    def _run_slow_query_probe(self):
        import psycopg2

        conn = None
        try:
            # 使用中性的 application_name，让 Agent 能定位业务接口，但不泄露 missing-index 根因。
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.dbname,
                connect_timeout=5,
                application_name=self.SLOW_QUERY_APP,
            )
            conn.autocommit = True
            self._slow_query_conn = conn
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                while not self._stopping_slow_query:
                    cur.execute(self._target_select_sql(comment=self.SLOW_QUERY_APP))
        except Exception as exc:
            exc_text = str(exc)
            if (
                self._stopping_slow_query
                or "server closed the connection unexpectedly" in exc_text
                or "terminating connection" in exc_text
            ):
                print("[FaultInjector:PgQueryPerfMissingIndexInjector] Slow query probe terminated.")
            else:
                self._slow_query_error = exc
                print(f"[FaultInjector:PgQueryPerfMissingIndexInjector] Slow query probe stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            self._slow_query_conn = None

    def _terminate_slow_query_probe(self):
        self._stopping_slow_query = True
        if self.env is not None:
            # 按 application_name 清理，只终止本场景 probe，不影响 Agent 或其他 workload 连接。
            self.env.execute_sql(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE application_name = '{self.SLOW_QUERY_APP}'
                  AND pid <> pg_backend_pid();
            """)

        if self._slow_query_conn is not None:
            try:
                self._slow_query_conn.close()
            except Exception:
                pass
            self._slow_query_conn = None

        if self._slow_query_thread is not None and self._slow_query_thread.is_alive():
            self._slow_query_thread.join(timeout=5)
        self._slow_query_thread = None
        self._stopping_slow_query = False

    def _drop_target_expression_indexes(self):
        # Agent 可能使用自定义索引名，恢复/重复注入时按表达式定义查找并清理。
        index_names = self._target_expression_index_names()
        index_names.add(self.remediation_index_name)
        for index_name in sorted(index_names):
            self.env.execute_sql(f"DROP INDEX IF EXISTS {index_name};")

    def _target_expression_index_names(self) -> set[str]:
        index_names = set()
        index_sql = (
            "SELECT indexname FROM pg_indexes "
            f"WHERE tablename = '{self.table}' "
            "AND indexdef ILIKE '%substring%' "
            f"AND indexdef ILIKE '%{self.column}%';"
        )
        for row in self._result_rows(self.env.execute_sql(index_sql)):
            if row:
                index_names.add(_validate_sql_identifier(str(row[0]), "index_name"))
        return index_names

    def _ensure_visible_column_index(self):
        # Shadow 表机制会新建一个可丢弃的 customer 表；原始普通索引仍挂在 shadow 表上，
        # 所以这里要确保 Agent 查询当前 customer 的 pg_indexes 时能看到普通列索引。
        if self._column_index_exists():
            return
        self.env.execute_sql("SET statement_timeout = '0';")
        self.env.execute_sql(
            f"CREATE INDEX IF NOT EXISTS {self.visible_column_index_name} "
            f"ON {self.table}({self.column});"
        )
        self.env.execute_sql(f"ANALYZE {self.table};")

    def _column_index_exists(self) -> bool:
        index_sql = (
            "SELECT indexname, indexdef FROM pg_indexes "
            f"WHERE tablename = '{self.table}' "
            f"AND indexdef ILIKE '%({self.column})%' "
            "AND indexdef NOT ILIKE '%substring%';"
        )
        return bool(self._result_rows(self.env.execute_sql(index_sql)))

    def _ensure_neighbor_pattern_index(self) -> None:
        # 同列的真实近邻索引：prefix 自动补全查询走 bpchar_pattern_ops，
        # 对 substring(...) 等值结构性不可用——Agent 必须用目录和计划证据鉴别。
        if not self.neighbor_pattern_index_name:
            return
        self.env.execute_sql("SET statement_timeout = '0';")
        self.env.execute_sql(
            f"CREATE INDEX IF NOT EXISTS {self.neighbor_pattern_index_name} "
            f"ON {self.table}({self.column} bpchar_pattern_ops);"
        )
        self.env.execute_sql(f"ANALYZE {self.table};")

    def _ensure_repair_decision_decoy_indexes(self) -> None:
        # 修复决策诱饵：
        # 1) 前任工程师留下的同列 left(col,3) 表达式索引残迹——left 与 substring 数据
        #    语义等价，但表达式索引按规范化表达式精确匹配，left 不服务 substring 等值
        #    查询，故障机制不受影响；"表达式索引已存在但仍 Seq Scan"要求 Agent 比对
        #    indexdef 文本而非套用"表达式索引已试过"的误判。
        # 2) 价格列普通 b-tree（merch 价格带审计真实使用）——fingerprint 的跨列 margin
        #    谓词无常量边界，任何单列索引都不被计划器采纳；排除证据是 pg_stats 与
        #    一次 COUNT 验证，全部 Agent-visible。
        # 两者都在 Agent 接管前建好，进入 state integrity 基线，不计入 new indexes。
        if self.remnant_expression_index_name:
            self.env.execute_sql("SET statement_timeout = '0';")
            self.env.execute_sql(
                f"CREATE INDEX IF NOT EXISTS {self.remnant_expression_index_name} "
                f"ON {self.table}((left({self.column}, 3)));"
            )
        if self.neighbor_price_index_name:
            self.env.execute_sql("SET statement_timeout = '0';")
            self.env.execute_sql(
                f"CREATE INDEX IF NOT EXISTS {self.neighbor_price_index_name} "
                f"ON {self.table}(pr_current_price);"
            )

    def _protect_placeholder_batch(self) -> None:
        # 供应商 feed 批次是正式目录数据：恢复主键、挂上 onboarding campaign 的外键引用，
        # 让"删除占位行"的数据治理旁路在数据库层直接报错。
        fk_table = self.placeholder_batch_fk_table
        if not fk_table:
            return
        if self.placeholder_batch_campaign_stride <= 0:
            raise ValueError(
                "placeholder batch protection requires a positive campaign stride: "
                f"fk_table={fk_table}, stride={self.placeholder_batch_campaign_stride}"
            )
        self.env.execute_sql("SET statement_timeout = '0';")
        self.env.execute_sql(
            f"ALTER TABLE {self.table} ADD CONSTRAINT {self.table}_pkey "
            f"PRIMARY KEY (pr_product_sk);"
        )
        self.env.execute_sql(
            f"ALTER TABLE {fk_table} ADD CONSTRAINT {self.placeholder_batch_fk_constraint} "
            f"FOREIGN KEY ({self.placeholder_batch_fk_column}) "
            f"REFERENCES {self.table} (pr_product_sk);"
        )
        campaign_count = self.placeholder_feed_rows // self.placeholder_batch_campaign_stride
        self.env.execute_sql(
            f"""
            INSERT INTO {fk_table} (
                camp_campaign_sk,
                camp_campaign_id,
                camp_start_date_sk,
                camp_end_date_sk,
                camp_product_sk,
                camp_cost,
                camp_response_target,
                camp_campaign_name,
                camp_channel_dmail,
                camp_channel_email,
                camp_channel_catalog,
                camp_channel_tv,
                camp_channel_radio,
                camp_channel_press,
                camp_channel_event,
                camp_channel_details,
                camp_purpose,
                camp_discount_active
            )
            SELECT
                {self.placeholder_batch_campaign_sk_start} + gs,
                ('ONBOARD' || lpad(gs::text, 9, '0'))::char(16),
                (SELECT cal_day_sk FROM calendar_day WHERE cal_date = DATE '2026-08-01'),
                (SELECT cal_day_sk FROM calendar_day WHERE cal_date = DATE '2026-11-30'),
                {self.synthetic_key_start} + gs * {self.placeholder_batch_campaign_stride},
                1500.00,
                1,
                ('Q3 supplier onboarding launch ' || gs)::char(50),
                'N',
                'Y',
                'Y',
                'N',
                'N',
                'N',
                'N',
                ('feed-batch-' || lpad(gs::text, 6, '0'))::varchar(100),
                'LAUNCH',
                'Y'
            FROM generate_series(1, {campaign_count}) AS gs
            """
        )
        self.env.execute_sql(f"ANALYZE {fk_table};")

    def _index_exists(self, index_name: str) -> bool:
        rows = self._result_rows(
            self.env.execute_sql(
                "SELECT indexname FROM pg_indexes "
                f"WHERE schemaname = 'public' AND indexname = '{index_name}';"
            )
        )
        return bool(rows)

    def _constraint_exists(self, constraint_name: str) -> bool:
        rows = self._result_rows(
            self.env.execute_sql(
                "SELECT conname FROM pg_constraint "
                f"WHERE conname = '{constraint_name}';"
            )
        )
        return bool(rows)

    def _prepare_real_scan_dataset(self):
        # 这里是真实性核心：不断增加真实 customer 数据并测量目标 SELECT wall time，
        # 让慢查询来自真实 Seq Scan 成本，而不是直接 pg_sleep 或 mock 指标。
        measured_seconds = self._measure_target_query_seconds()
        # 逐批扩容 customer，让慢来自真实非 SARGable Seq Scan；达到阈值后停止，避免无上限膨胀。
        inserted_rows = 0
        while measured_seconds < self.real_scan_target_seconds and inserted_rows < self.real_scan_max_rows:
            batch_rows = min(self.real_scan_batch_rows, self.real_scan_max_rows - inserted_rows)
            self._insert_synthetic_rows(inserted_rows + 1, inserted_rows + batch_rows)
            inserted_rows += batch_rows
            self.env.execute_sql(f"ANALYZE {self.table};")
            measured_seconds = self._measure_target_query_seconds()
            print(
                "[FaultInjector:PgQueryPerfMissingIndexInjector] Real scan calibration: "
                f"synthetic_rows={inserted_rows}, measured_seconds={measured_seconds:.3f}"
            )

        if measured_seconds < self.real_scan_target_seconds:
            raise RuntimeError(
                "Missing-index real scan did not reach the declared Case threshold: "
                f"target_seconds={self.real_scan_target_seconds}, "
                f"measured_seconds={measured_seconds:.3f}, inserted_rows={inserted_rows}, "
                f"max_rows={self.real_scan_max_rows}"
            )
        self.placeholder_feed_rows = inserted_rows
        self.fault_plan, self.fault_query_seconds = self._capture_explain_analyze(
            self.fault_fingerprint_sql,
            timeout_seconds=300,
        )
        self._assert_missing_index_plan(self.fault_plan)

    def _activate_shadow_table(self):
        # 真实大扫描数据放在可丢弃的 shadow customer 中，完整 recover 可用 DROP+RENAME 快速恢复。
        # 这样不会永久污染原始 TPC-DS customer 表，也能让重复运行保持幂等。
        if not self._table_exists(self.table):
            raise RuntimeError(f"Missing-index base table does not exist: table={self.table}")
        if self._table_exists(self.shadow_table_name):
            raise RuntimeError(
                f"Missing-index base image already contains shadow table {self.shadow_table_name}"
            )
        self.env.execute_sql(f"ALTER TABLE {self.table} RENAME TO {self.shadow_table_name};")
        self._shadow_activated = True
        self.env.execute_sql(
            f"CREATE UNLOGGED TABLE {self.table} "
            f"(LIKE {self.shadow_table_name} INCLUDING DEFAULTS);"
        )
        self.env.execute_sql(f"INSERT INTO {self.table} SELECT * FROM {self.shadow_table_name};")
        self.env.execute_sql(f"ANALYZE {self.table};")

    def _restore_shadow_table(self) -> None:
        if not self._table_exists(self.shadow_table_name):
            raise RuntimeError(
                f"Missing-index shadow table disappeared before recovery: "
                f"table={self.shadow_table_name}"
            )
        _require_sql_success(
            self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table};"),
            f"drop expanded missing-index table {self.table}",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"ALTER TABLE {self.shadow_table_name} RENAME TO {self.table};"
            ),
            f"restore missing-index shadow table {self.shadow_table_name}",
        )

    def _table_exists(self, table_name: str) -> bool:
        table_name = _validate_sql_identifier(table_name, "table_name")
        rows = self._result_rows(
            self.env.execute_sql(f"SELECT to_regclass('public.{table_name}') IS NOT NULL;")
        )
        if not rows or not rows[0]:
            return False
        return str(rows[0][0]).lower() in ("true", "t", "1")

    def _insert_synthetic_rows(self, start_offset: int, end_offset: int):
        # Q3 供应商 feed 批次：逐批扩容 product，让慢来自真实非 SARGable Seq Scan。
        # 每 10000 行放 1 行 'Sho' 前缀（目标前缀，feed 中已分类的鞋类记录），保证谓词
        # 选择率低；大多数行是 'Zzz' 前缀的"待分类"占位类别——它们是正式目录数据
        # （campaign 外键引用），不是可删除的垃圾行。
        self.env.execute_sql(
            f"""
            INSERT INTO {self.table} (
                pr_product_sk,
                pr_product_id,
                pr_rec_start_date,
                pr_rec_end_date,
                pr_product_desc,
                pr_current_price,
                pr_wholesale_cost,
                pr_brand_id,
                pr_brand,
                pr_class_id,
                pr_class,
                pr_category_id,
                pr_category,
                pr_manufact_id,
                pr_manufact,
                pr_size,
                pr_formulation,
                pr_color,
                pr_units,
                pr_container,
                pr_manager_id,
                pr_product_name
            )
            SELECT
                {self.synthetic_key_start} + gs,
                ('SUPFDR' || lpad(gs::text, 10, '0'))::char(16),
                date '2026-07-01',
                date '2030-01-01',
                ('supplier onboarding feed record ' || gs)::varchar(200),
                10.00,
                5.00,
                1,
                'UNCLASSIFIED',
                1,
                'UNCLASSIFIED',
                1,
                (
                    CASE WHEN gs % 10000 = 0
                         THEN 'Sho' || lpad(gs::text, 27, '0')
                         ELSE 'Zzz' || lpad(gs::text, 27, '0')
                    END
                )::char(50),
                1,
                'UNCLASSIFIED',
                'Medium',
                'std',
                'red',
                'Each',
                'Box',
                1,
                ('ONBOARD-SKU-' || lpad(gs::text, 8, '0'))::varchar(50)
            FROM generate_series({start_offset}, {end_offset}) AS gs
            """
        )

    def _measure_target_query_seconds(self) -> float:
        # 用普通 SELECT 的 wall time 校准，而不是 EXPLAIN ANALYZE，确保 slow_queries 里的会话也真的会慢。
        # 单表 probe 只用来校准可观测慢查询；fault baseline 由重型 fingerprint 单独测。
        return self._measure_sql_seconds(self._target_select_sql(), timeout_seconds=120)

    def _measure_sql_seconds(self, sql: str, timeout_seconds: int) -> float:
        import time

        self.env.execute_sql(f"SET statement_timeout = '{int(timeout_seconds)}s';")
        started_at = time.monotonic()
        result = self.env.execute_sql(sql)
        elapsed = time.monotonic() - started_at
        result_text = self._result_to_text(result)
        if '"status": "error"' in result_text.lower():
            raise AssertionError(f"missing-index baseline SQL failed: {result_text}")
        return elapsed

    def _measure_explain_analyze_seconds(self, sql: str, timeout_seconds: int) -> float:
        _, seconds = self._capture_explain_analyze(sql, timeout_seconds)
        return seconds

    def _capture_explain_analyze(self, sql: str, timeout_seconds: int):
        explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql.rstrip(';')};"
        self.env.execute_sql(f"SET statement_timeout = '{int(timeout_seconds)}s';")
        result = self.env.execute_sql(explain_sql)
        result_text = self._result_to_text(result)
        if '"status": "error"' in result_text.lower():
            raise AssertionError(f"missing-index baseline EXPLAIN ANALYZE failed: {result_text}")
        from src.database.postgres import execution_time_seconds
        seconds = execution_time_seconds(result)
        if seconds is None:
            raise AssertionError(f"missing-index baseline EXPLAIN ANALYZE had no Execution Time: {result_text}")
        return result, seconds

    def _target_select_sql(self, comment: str = None) -> str:
        # substring probe 用来制造持续慢查询让 pg_stat_activity 看到。
        # 这条 SQL 是单表 substring SELECT（不是 alert 里的 q75 重型 SQL），目的是把
        # substring(i_category, 1, 3)='Sho' 谓词的 Seq Scan 成本压到 12s+。
        # alert / fingerprint / evaluator 看的是完整 q75；probe 看的是这条简化版。
        prefix = f"/* {comment} */\n" if comment else ""
        return (
            prefix
            + f"SELECT pr_product_sk FROM {self.table} "
            + f"WHERE substring({self.column}, 1, 3) = 'Sho';"
        )

    def _result_rows(self, raw_result):
        if isinstance(raw_result, str):
            try:
                raw_result = json.loads(raw_result)
            except Exception:
                return []
        if isinstance(raw_result, dict):
            rows = raw_result.get("result", [])
            return rows if isinstance(rows, list) else []
        return []

    def _result_to_text(self, raw_result) -> str:
        if raw_result is None:
            return ""
        if isinstance(raw_result, str):
            try:
                raw_result = json.loads(raw_result)
            except Exception:
                return raw_result
        return json.dumps(raw_result, ensure_ascii=False, default=str)


class PgQueryPerfMissingIndexScenario(PostgresScenario):
    scenario_id = 'pg_query_perf_missing_index'
    description = 'Simulates inefficient predicate access patterns on a table.'
    cases = (
        _PGQUERYPERFMISSINGINDEXSCENARIO_CASE,
        _PGQUERYPERFMISSINGINDEXSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgQueryPerfMissingIndexCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgQueryPerfMissingIndexInjector,
                config={
                    'table': case.table,
                    'index_name': case.index_name,
                    'column': case.column,
                    'remediation_index_name': case.remediation_index_name,
                    'visible_column_index_name': case.visible_column_index_name,
                    'shadow_table_name': case.shadow_table_name,
                    'neighbor_pattern_index_name': case.neighbor_pattern_index_name,
                    'remnant_expression_index_name': case.remnant_expression_index_name,
                    'neighbor_price_index_name': case.neighbor_price_index_name,
                    'placeholder_batch_fk_table': case.placeholder_batch_fk_table,
                    'placeholder_batch_fk_column': case.placeholder_batch_fk_column,
                    'placeholder_batch_fk_constraint': case.placeholder_batch_fk_constraint,
                    'placeholder_batch_campaign_sk_start': case.placeholder_batch_campaign_sk_start,
                    'placeholder_batch_campaign_stride': case.placeholder_batch_campaign_stride,
                    'fault_fingerprint_sql': case.fault_fingerprint_sql,
                    'real_scan_target_seconds': case.real_scan_target_seconds,
                    'real_scan_batch_rows': case.real_scan_batch_rows,
                    'real_scan_max_rows': case.real_scan_max_rows,
                    'start_slow_query_probe': case.start_slow_query_probe,
                },
            ),
        )
