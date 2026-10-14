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
class PgQueryPerfHeavyOffsetPaginationCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    table: str
    order_column: str
    offset_value: int
    index_name: str
    fault_fingerprint_sql: str
    slow_queries: tuple[str, ...]

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfHeavyOffsetPaginationForBranchOrderDeepOffsetScenarioCase(PgQueryPerfHeavyOffsetPaginationCase):
    pass

_PGQUERYPERFHEAVYOFFSETPAGINATIONSCENARIO_CASE = PgQueryPerfHeavyOffsetPaginationForBranchOrderDeepOffsetScenarioCase(
    case_id='branch_order_deep_offset',
    runtime=PostgresCaseRuntime(resources=QUERY_PERF_RESOURCES),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "audit export deep batch query",
                    "entity": "branch_order_deep_offset",
                    "evidence": [
                        "scripted diagnostic actions observed audit export deep batch query"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "deep offset pagination",
                    "entity": "branch_order_deep_offset",
                    "evidence": [
                        "scripted diagnostic actions observed deep offset pagination"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "offset scans and discards preceding rows",
                    "entity": "branch_order_deep_offset",
                    "evidence": [
                        "scripted diagnostic actions observed offset scans and discards preceding rows"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "replace OFFSET with keyset pagination on bol_sold_date_sk"
            ],
            "verification": [
                "keyset boundary query was verified"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgQueryPerfHeavyOffsetPaginationForBranchOrderDeepOffsetEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcdsx:latest',
    workload_tag='tpcdsx',
    dataset_scale=1,
    title='Simulates high-rank pagination causing I/O waste.',
    alert='Alert: the audit export API is slow only for late batches of the same ordered event stream. The first batch returns quickly, but batch 100001+ takes seconds and the API reports elevated database I/O during those late-batch exports. Identify why late batches are disproportionately expensive and provide a verifiable fix.\n\nAffected query:\n\n/* ops_export: audit_event_batch_v5 */\nWITH\ncandidate_events AS MATERIALIZED (\n    SELECT\n        ss.bol_sold_date_sk AS event_day_sk,\n        ss.bol_receipt_number AS receipt_number,\n        ss.bol_product_sk AS product_sk,\n        ss.bol_account_sk AS account_sk,\n        ss.bol_branch_sk AS branch_sk,\n        ss.bol_quantity AS quantity,\n        ss.bol_net_paid AS net_paid,\n        ss.bol_net_profit AS net_profit\n    FROM branch_order_line ss\n    WHERE ss.bol_sold_date_sk BETWEEN 2450815 AND 2452640\n      AND ss.bol_receipt_number IS NOT NULL\n      AND ss.bol_product_sk IS NOT NULL\n),\nsequenced_export AS MATERIALIZED (\n    SELECT\n        ce.event_day_sk,\n        ce.receipt_number,\n        ce.product_sk,\n        ce.account_sk,\n        ce.branch_sk,\n        ce.quantity,\n        ce.net_paid,\n        ce.net_profit,\n        COUNT(*) OVER () AS export_total,\n        ROW_NUMBER() OVER (\n            ORDER BY ce.event_day_sk, ce.receipt_number, ce.product_sk\n        ) AS export_seq\n    FROM candidate_events ce\n)\nSELECT\n    d.cal_date AS event_ts,\n    se.event_day_sk,\n    se.receipt_number,\n    se.product_sk,\n    se.account_sk,\n    se.branch_sk,\n    se.quantity,\n    se.net_paid,\n    se.net_profit,\n    i.pr_category,\n    i.pr_brand,\n    se.export_total\nFROM sequenced_export se\nJOIN calendar_day d ON d.cal_day_sk = se.event_day_sk\nJOIN product i ON i.pr_product_sk = se.product_sk\nWHERE se.export_seq BETWEEN 1000001 AND 1000010\nORDER BY se.event_day_sk, se.receipt_number, se.product_sk\n',
    initial_state={'status': 'healthy', 'pagination': 'offset'},
    expected_target={'status': 'diagnosed', 'pagination': 'keyset'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table='branch_order_line',
    order_column='bol_sold_date_sk',
    offset_value=1000000,
    index_name='idx_aiopsbench_bol_event_order_cover',
    fault_fingerprint_sql=('\n'
 '/* ops_export: audit_event_batch_v5 */\n'
 'WITH\n'
 'candidate_events AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ss.bol_sold_date_sk AS event_day_sk,\n'
 '        ss.bol_receipt_number AS receipt_number,\n'
 '        ss.bol_product_sk AS product_sk,\n'
 '        ss.bol_account_sk AS account_sk,\n'
 '        ss.bol_branch_sk AS branch_sk,\n'
 '        ss.bol_quantity AS quantity,\n'
 '        ss.bol_net_paid AS net_paid,\n'
 '        ss.bol_net_profit AS net_profit\n'
 '    FROM branch_order_line ss\n'
 '    WHERE ss.bol_sold_date_sk BETWEEN 2450815 AND 2452640\n'
 '      AND ss.bol_receipt_number IS NOT NULL\n'
 '      AND ss.bol_product_sk IS NOT NULL\n'
 '),\n'
 'sequenced_export AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ce.event_day_sk,\n'
 '        ce.receipt_number,\n'
 '        ce.product_sk,\n'
 '        ce.account_sk,\n'
 '        ce.branch_sk,\n'
 '        ce.quantity,\n'
 '        ce.net_paid,\n'
 '        ce.net_profit,\n'
 '        COUNT(*) OVER () AS export_total,\n'
 '        ROW_NUMBER() OVER (\n'
 '            ORDER BY ce.event_day_sk, ce.receipt_number, ce.product_sk\n'
 '        ) AS export_seq\n'
 '    FROM candidate_events ce\n'
 ')\n'
 'SELECT\n'
 '    d.cal_date AS event_ts,\n'
 '    se.event_day_sk,\n'
 '    se.receipt_number,\n'
 '    se.product_sk,\n'
 '    se.account_sk,\n'
 '    se.branch_sk,\n'
 '    se.quantity,\n'
 '    se.net_paid,\n'
 '    se.net_profit,\n'
 '    i.pr_category,\n'
 '    i.pr_brand,\n'
 '    se.export_total\n'
 'FROM sequenced_export se\n'
 'JOIN calendar_day d ON d.cal_day_sk = se.event_day_sk\n'
 'JOIN product i ON i.pr_product_sk = se.product_sk\n'
 'WHERE se.export_seq BETWEEN 1000001 AND 1000010\n'
 'ORDER BY se.event_day_sk, se.receipt_number, se.product_sk\n'),
    slow_queries=('\n'
 '/* ops_export: audit_event_batch_v5 */\n'
 'WITH\n'
 'candidate_events AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ss.bol_sold_date_sk AS event_day_sk,\n'
 '        ss.bol_receipt_number AS receipt_number,\n'
 '        ss.bol_product_sk AS product_sk,\n'
 '        ss.bol_account_sk AS account_sk,\n'
 '        ss.bol_branch_sk AS branch_sk,\n'
 '        ss.bol_quantity AS quantity,\n'
 '        ss.bol_net_paid AS net_paid,\n'
 '        ss.bol_net_profit AS net_profit\n'
 '    FROM branch_order_line ss\n'
 '    WHERE ss.bol_sold_date_sk BETWEEN 2450815 AND 2452640\n'
 '      AND ss.bol_receipt_number IS NOT NULL\n'
 '      AND ss.bol_product_sk IS NOT NULL\n'
 '),\n'
 'sequenced_export AS MATERIALIZED (\n'
 '    SELECT\n'
 '        ce.event_day_sk,\n'
 '        ce.receipt_number,\n'
 '        ce.product_sk,\n'
 '        ce.account_sk,\n'
 '        ce.branch_sk,\n'
 '        ce.quantity,\n'
 '        ce.net_paid,\n'
 '        ce.net_profit,\n'
 '        COUNT(*) OVER () AS export_total,\n'
 '        ROW_NUMBER() OVER (\n'
 '            ORDER BY ce.event_day_sk, ce.receipt_number, ce.product_sk\n'
 '        ) AS export_seq\n'
 '    FROM candidate_events ce\n'
 ')\n'
 'SELECT\n'
 '    d.cal_date AS event_ts,\n'
 '    se.event_day_sk,\n'
 '    se.receipt_number,\n'
 '    se.product_sk,\n'
 '    se.account_sk,\n'
 '    se.branch_sk,\n'
 '    se.quantity,\n'
 '    se.net_paid,\n'
 '    se.net_profit,\n'
 '    i.pr_category,\n'
 '    i.pr_brand,\n'
 '    se.export_total\n'
 'FROM sequenced_export se\n'
 'JOIN calendar_day d ON d.cal_day_sk = se.event_day_sk\n'
 'JOIN product i ON i.pr_product_sk = se.product_sk\n'
 'WHERE se.export_seq BETWEEN 1000001 AND 1000010\n'
 'ORDER BY se.event_day_sk, se.receipt_number, se.product_sk\n',),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.5,
        reference_run_ids=(
            "reference-61__pg_query_perf_heavy_offset_pagination__"
            "branch_order_deep_offset__mock__r001",
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgQueryPerfHeavyOffsetPaginationForBranchOrderShallowOffsetScenarioCase(
    PgQueryPerfHeavyOffsetPaginationCase
):
    pass


_PGQUERYPERFHEAVYOFFSETPAGINATION_SIMPLIFIED_CASE = (
    PgQueryPerfHeavyOffsetPaginationForBranchOrderShallowOffsetScenarioCase(
        case_id="branch_order_shallow_offset",
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
        evaluator=PgQueryPerfHeavyOffsetPaginationForBranchOrderShallowOffsetEvaluatorCase,
        base_image_name="aiopsbench-pg-tpcdsx:latest",
        workload_tag="tpcdsx",
        dataset_scale=1,
        title="Late-page branch order export degradation.",
        alert=(
            "Alert: the branch order history export service is degraded. Users report that early "
            "pages of the same export still return in milliseconds, but late pages now take several "
            "seconds and intermittently time out. The slowdown worsened gradually as the exported "
            "history accumulated, and database CPU and I/O spike during each late-page export run. "
            "Diagnose why late-page exports degrade and restore late-page export performance with "
            "a verifiable fix. Deliver the fix as the export query itself; schema or persistent "
            "object changes are out of scope for this incident."
        ),
        initial_state={"status": "healthy", "pagination": "offset"},
        expected_target={"status": "diagnosed", "pagination": "keyset"},
        background_workload=EMPTY_BACKGROUND_WORKLOAD,
        table="branch_order_line",
        order_column="bol_sold_date_sk",
        offset_value=10000,
        index_name="idx_aiopsbench_bol_event_order_cover",
        fault_fingerprint_sql=(
            "SELECT bol_sold_date_sk, bol_receipt_number, bol_product_sk "
            "FROM (SELECT bol_sold_date_sk, bol_receipt_number, bol_product_sk, "
            "ROW_NUMBER() OVER (ORDER BY bol_sold_date_sk, bol_receipt_number, bol_product_sk) AS rn "
            "FROM branch_order_line WHERE bol_sold_date_sk BETWEEN 2450815 AND 2452640) numbered "
            "WHERE rn BETWEEN 10001 AND 10010 "
            "ORDER BY bol_sold_date_sk, bol_receipt_number, bol_product_sk"
        ),
        slow_queries=(
            "SELECT bol_sold_date_sk, bol_receipt_number, bol_product_sk "
            "FROM branch_order_line ORDER BY bol_sold_date_sk, bol_receipt_number, bol_product_sk "
            "LIMIT 10 OFFSET 10000",
        ),
        difficulty=DifficultyCalibration(
            diagnostic_depth=3,
            environmental_complexity=0.75,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_query_perf_heavy_offset_pagination_branch_order_shallow_offset_"
                "MockLLMAgent.json",
            ),
        ),
    )
)


import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from src.database.postgres import execution_time_seconds
from src.database.query_results import capture_query_result_truth
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

class PgQueryPerfHeavyOffsetPaginationInjector(BaseFaultInjector, PgQueryPerfFaultFingerprintProbe):
    """
    模拟"深度分页引起的资源浪费"故障。
    在 tpcdsx 业务表上执行高位 row_number() 批次导出查询，导致数据库
    必须排序/编号大量前序行后只返回少量结果。
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
        fault_sql = config["fault_fingerprint_sql"]
        with env.metrics_hidden():
            hidden_seed = env.execute_sql(fault_sql)
            _require_sql_success(hidden_seed, "verify high-rank pagination query")
            fault_plan = env.execute_sql(
                f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {fault_sql.rstrip(';')};"
            )
            _require_sql_success(fault_plan, "verify high-rank pagination plan")
            hidden_evidence = self._query_observability_evidence(env)
            pg_stat_statements = env.execute_sql(
                "SELECT query, calls, mean_exec_time, rows FROM pg_stat_statements "
                "WHERE query ILIKE '%branch_order_line%' AND query ILIKE '%row_number%' "
                "ORDER BY total_exec_time DESC LIMIT 10;"
            )
            _require_sql_success(
                pg_stat_statements,
                "read high-rank pagination query history",
            )
            self._assert_high_rank_observable(
                hidden_evidence["topsql"],
                pg_stat_statements,
                fault_plan,
            )

        seed_result = env.execute_sql(fault_sql)
        _require_sql_success(seed_result, "seed high-rank pagination query")
        self._seed_sibling_statement_history()
        evidence = self._query_observability_evidence(env)
        topsql_text = json.dumps(
            _json_object(evidence["topsql"], "read seeded high-rank pagination topsql").get(
                "records", []
            ),
            ensure_ascii=False,
            default=str,
        ).lower()
        if self.table not in topsql_text or "row_number" not in topsql_text:
            raise RuntimeError(
                "Seeded high-rank pagination query is not visible to the Agent: "
                f"topsql={evidence['topsql']}"
            )
        evidence.update({
            "pg_stat_statements": pg_stat_statements,
            "fault_plan": fault_plan,
            "fault_query_truth": capture_query_result_truth(seed_result, ordered=True),
            "fault_query_seconds": execution_time_seconds(fault_plan),
        })
        if evidence["fault_query_seconds"] is None:
            raise RuntimeError(
                "High-rank pagination plan has no execution time: "
                f"scenario={context.scenario_id}, case={context.case_id}, plan={fault_plan}"
            )
        return evidence

    def _assert_high_rank_observable(self, topsql, pg_stat_statements, fault_plan) -> None:
        topsql_payload = _json_object(topsql, "read high-rank pagination topsql")
        topsql_text = json.dumps(
            topsql_payload.get("records", []), ensure_ascii=False, default=str
        ).lower()
        if self.table not in topsql_text or "row_number" not in topsql_text:
            raise RuntimeError(
                "High-rank pagination query is not visible in topsql: "
                f"table={self.table}, topsql={topsql}"
            )

        pg_stat_text = json.dumps(
            _json_object(
                pg_stat_statements,
                "read high-rank pagination pg_stat_statements",
            ).get("result", []),
            ensure_ascii=False,
            default=str,
        ).lower()
        if self.table not in pg_stat_text or "row_number" not in pg_stat_text:
            raise RuntimeError(
                "High-rank pagination query is not visible in pg_stat_statements: "
                f"table={self.table}, pg_stat_statements={pg_stat_statements}"
            )

        plan_text = json.dumps(
            _json_object(fault_plan, "read high-rank pagination plan").get("result", []),
            ensure_ascii=False,
            default=str,
        ).lower()
        if "windowagg" not in plan_text and "row_number" not in plan_text:
            raise RuntimeError(
                "High-rank pagination plan does not contain WindowAgg/row_number: "
                f"plan={fault_plan}"
            )

    def quiesce(self, context: FaultLifecycleContext):
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_heavy_offset")

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
        self.order_column = _validate_sql_identifier(config["order_column"], "order_column")
        self.offset_value = int(config["offset_value"])
        self.index_name = _validate_sql_identifier(config["index_name"], "index_name")
        self.fault_fingerprint_sql = config["fault_fingerprint_sql"]

    def _install_persistent_state(self) -> None:
        print(f"[FaultInjector:PgQueryPerfHeavyOffsetPaginationInjector] "
              f"Injecting heavy offset pagination fault on {self.table}...")
        _require_sql_success(
            self.env.execute_sql("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"),
            "install pg_stat_statements for heavy-offset scenario",
        )
        self._assert_row_count()
        _require_sql_success(
            self.env.execute_sql(
                f"CREATE INDEX IF NOT EXISTS {self.index_name} "
                "ON branch_order_line (bol_sold_date_sk, bol_receipt_number, bol_product_sk) "
                "INCLUDE (bol_account_sk, bol_branch_sk, bol_quantity, bol_net_paid, bol_net_profit);"
            ),
            "install heavy-offset event-order index",
        )
        _require_sql_success(
            self.env.execute_sql(
                "CREATE INDEX IF NOT EXISTS idx_aiopsbench_bol_account_rollup "
                "ON branch_order_line (bol_account_sk) INCLUDE (bol_net_paid, bol_net_profit);"
            ),
            "install heavy-offset account rollup index",
        )
        _require_sql_success(
            self.env.execute_sql("ANALYZE branch_order_line; ANALYZE product; ANALYZE calendar_day;"),
            "analyze heavy-offset supporting tables",
        )

    def _verify_persistent_state(self) -> None:
        self._assert_row_count()
        payload = _json_object(
            self.env.execute_sql(
                "SELECT indexname FROM pg_indexes "
                f"WHERE schemaname = 'public' AND indexname IN "
                f"('{self.index_name}', 'idx_aiopsbench_bol_account_rollup') "
                "ORDER BY indexname;"
            ),
            "verify heavy-offset fault image indexes",
        )
        indexes = {row[0] for row in payload["result"]}
        required = {self.index_name, "idx_aiopsbench_bol_account_rollup"}
        if indexes != required:
            raise RuntimeError(
                f"Heavy-offset fault image index mismatch: expected={sorted(required)}, "
                f"actual={sorted(indexes)}"
            )

    def _assert_row_count(self) -> None:
        payload = _json_object(
            self.env.execute_sql(f"SELECT count(*) FROM {self.table};"),
            "read heavy-offset table row count",
        )
        actual_rows = int(payload["result"][0][0])
        if actual_rows <= self.offset_value:
            raise RuntimeError(
                f"{self.table} has {actual_rows} rows, but high-rank batch "
                f"{self.offset_value} requires more rows"
            )

    def _activate_runtime(self) -> None:
        _require_sql_success(
            self.env.execute_sql("SET statement_timeout = '300s';"),
            "set heavy-offset statement timeout",
        )
        _require_sql_success(
            self.env.execute_sql(self.fault_fingerprint_sql),
            "execute heavy-offset business query",
        )
        print(f"[FaultInjector:PgQueryPerfHeavyOffsetPaginationInjector] "
              f"Executed high-rank audit export query around row {self.offset_value}.")
        if self._env_supports_background_probe():
            self._start_fault_fingerprint_probe(
                sql=self.fault_fingerprint_sql,
                app_name="aiopsbench_fp_heavy_offset",
                idle_sleep=True,
            )

    def _seed_sibling_statement_history(self) -> None:
        """
        播种同表、同过滤窗口的真实邻近语句历史：同一导出作业的健康早页查询，
        以及同窗口的夜间 branch 汇总批处理。它们共享 branch_order_line 与过滤
        条件，但都不是晚页劣化的原因，用于要求 Agent 依据业务症状做语句级辨别。
        """
        sibling_statements = (
            "SELECT bol_sold_date_sk, bol_receipt_number, bol_product_sk "
            f"FROM {self.table} "
            "WHERE bol_sold_date_sk BETWEEN 2450815 AND 2452640 "
            "ORDER BY bol_sold_date_sk, bol_receipt_number, bol_product_sk "
            "LIMIT 20",
            "SELECT bol_branch_sk, count(*) AS orders, sum(bol_net_paid) AS net_paid_total "
            f"FROM {self.table} "
            "WHERE bol_sold_date_sk BETWEEN 2450815 AND 2452640 "
            "GROUP BY bol_branch_sk ORDER BY net_paid_total DESC",
        )
        for statement in sibling_statements:
            for _ in range(3):
                _require_sql_success(
                    self.env.execute_sql(statement),
                    "seed heavy-offset sibling statement history",
                )

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        self._configure(context.config, env)
        print(f"[FaultInjector:PgQueryPerfHeavyOffsetPaginationInjector] "
              f"Recovering supporting objects...")
        self._terminate_fault_fingerprint_probe(app_name="aiopsbench_fp_heavy_offset")
        _require_sql_success(
            env.execute_sql(
                f"DROP INDEX IF EXISTS {self.index_name}; "
                "DROP INDEX IF EXISTS idx_aiopsbench_bol_account_rollup;"
            ),
            "recover heavy-offset supporting indexes",
        )


class PgQueryPerfHeavyOffsetPaginationScenario(PostgresScenario):
    scenario_id = 'pg_query_perf_heavy_offset_pagination'
    description = 'Simulates high-rank pagination causing I/O waste.'
    cases = (
        _PGQUERYPERFHEAVYOFFSETPAGINATIONSCENARIO_CASE,
        _PGQUERYPERFHEAVYOFFSETPAGINATION_SIMPLIFIED_CASE,
    )

    def build_fault_plan(self, case: PgQueryPerfHeavyOffsetPaginationCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgQueryPerfHeavyOffsetPaginationInjector,
                config={
                    'table': case.table,
                    'order_column': case.order_column,
                    'offset_value': case.offset_value,
                    'index_name': case.index_name,
                    'fault_fingerprint_sql': case.fault_fingerprint_sql,
                },
            ),
        )
