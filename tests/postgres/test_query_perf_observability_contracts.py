import json
from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from src.scenarios.postgres.query_perf.heavy_offset_pagination import PgQueryPerfHeavyOffsetPaginationInjector
from src.scenarios.postgres.query_perf.implicit_type_conversion import PgQueryPerfImplicitTypeConversionInjector
from src.scenarios.postgres.query_perf.parameter_sniffing import PgQueryPerfParameterSniffingInjector
from src.scenarios.postgres.query_perf.sort_spill import PgQueryPerfSortSpillInjector
from src.scenarios.postgres.query_perf.stale_statistics import PgQueryPerfStaleStatisticsInjector


def test_query_perf_case_specific_contracts_wire_real_fault_profiles():
    from src.scenarios.postgres.query_perf.parameter_sniffing import PgQueryPerfParameterSniffingScenario
    from src.scenarios.postgres.query_perf.stale_statistics import PgQueryPerfStaleStatisticsScenario

    parameter_scenario = PgQueryPerfParameterSniffingScenario()
    parameter_simple = parameter_scenario.get_case("branch_order_year_skew_simple")
    parameter_plan = parameter_scenario.build_fault_plan(parameter_simple)[0]
    assert parameter_plan.config["support_index_variant"] == "hot_window_partial"
    parameter_injector = PgQueryPerfParameterSniffingInjector()
    parameter_injector._configure(parameter_plan.config, object())
    assert parameter_injector.support_index_name == "idx_aiopsbench_worker_hot_date"
    assert "WHERE bol_sold_date_sk BETWEEN 2451911 AND 2451970" in parameter_injector.support_index_sql

    stale_scenario = PgQueryPerfStaleStatisticsScenario()
    stale_simple = stale_scenario.get_case("branch_order_hot_window_simple")
    stale_plan = stale_scenario.build_fault_plan(stale_simple)[0]
    assert stale_plan.config["distribution_profile"] == "single_hot_combination"
    assert stale_plan.config["extended_statistics_name"] == "aiopsbench_branch_order_load_baseline"
    assert stale_plan.config["historical_batch_rows"] == 3000
    assert stale_plan.config["statistics_target"] == 2
    assert "branch_hot_window_trend" in stale_plan.config["decoy_fingerprint_sql"]
    assert stale_plan.config["decoy_rows"] == 8_000
    assert stale_plan.config["business_report_sql"] == stale_simple.business_report_sql
    stale_complex = stale_scenario.get_case("branch_order_distribution_shift")
    stale_complex_plan = stale_scenario.build_fault_plan(stale_complex)[0]
    assert stale_complex_plan.config["distribution_profile"] == "distributed_window"
    assert stale_complex_plan.config["extended_statistics_name"] is None
    assert stale_complex_plan.config["decoy_rows"] == 120_000
    assert stale_complex_plan.config["business_report_sql"] == stale_complex.business_report_sql
    # The complex-case alert must not leak the affected SQL;
    # the report identity stays reachable only through workload traces.
    assert "WITH" not in stale_complex.alert
    assert "Affected query" not in stale_complex.alert
    assert "hot_channel_revenue_reforecast_v9" in stale_complex.business_report_sql
    assert stale_complex.business_report_sql == stale_complex.fault_fingerprint_sql
    # the simple-case alert names the report fingerprint only and
    # does not embed the affected SQL.
    assert "report fingerprint: branch_hot_window_simple" in stale_simple.alert
    decoy_traces = PgQueryPerfStaleStatisticsInjector.DECOY_REPORT_TRACES
    assert "assisted_channel_rebate_summary_v5" in decoy_traces[0]
    assert "assisted_order_line" in decoy_traces[0]
    assert "digital_channel_monthly_close_v3" in decoy_traces[1]
    assert "digital_order_line" in decoy_traces[1]

    class Env:
        def __init__(self):
            self.statements = []

        def execute_sql(self, sql):
            self.statements.append(sql)
            return {"status": "success", "result": []}

    env = Env()
    stale_injector = PgQueryPerfStaleStatisticsInjector()
    stale_injector._configure(stale_plan.config, env)
    stale_injector._insert_stale_distribution_rows("branch_order_line")
    assert "2451911,\n                1," in env.statements[0]

    historical_statements = []
    stale_injector.env = env
    stale_injector._insert_historical_batch_rows("branch_order_line")
    stale_injector._cleanup_historical_rows("branch_order_line", strict=True)
    historical_statements = [
        statement for statement in env.statements[1:]
        if "INSERT INTO branch_order_line" in statement or "DELETE FROM branch_order_line" in statement
    ]
    assert len(historical_statements) == 2
    assert "2451880" in historical_statements[0]
    assert "1900000000" in historical_statements[0]
    assert "BETWEEN 1900000001" in historical_statements[1]


def test_stale_statistics_maintenance_trap_and_replay_records():
    import re

    from src.scenarios.evaluation.postgres.query_perf.stale_statistics import (
        PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase,
    )
    from src.scenarios.postgres.query_perf.stale_statistics import PgQueryPerfStaleStatisticsScenario

    scenario = PgQueryPerfStaleStatisticsScenario()
    case = scenario.get_case("branch_order_distribution_shift")
    plan = scenario.build_fault_plan(case)[0]

    # The scoped maintenance refresh must exclude the fault-critical columns
    # so the plan error survives while table-level counters look maintained.
    critical_columns = set(PgQueryPerfStaleStatisticsInjector.STATISTICS_TARGET_COLUMNS)
    maintenance_columns = set(PgQueryPerfStaleStatisticsInjector.MAINTENANCE_ANALYZE_COLUMNS)
    assert critical_columns == {"bol_product_sk", "bol_quantity", "bol_sold_date_sk"}
    assert maintenance_columns == {"bol_account_sk", "bol_net_paid"}
    assert critical_columns.isdisjoint(maintenance_columns)

    class Env:
        def __init__(self):
            self.statements = []

        def execute_sql(self, sql):
            self.statements.append(sql)
            return {"status": "success", "result": []}

    env = Env()
    injector = PgQueryPerfStaleStatisticsInjector()
    injector._configure(plan.config, env)
    injector._run_scoped_maintenance_analyze()
    assert env.statements[-1] == "ANALYZE branch_order_line (bol_account_sk, bol_net_paid);"

    injector._insert_replay_batch_rows()
    replay_sql = env.statements[-1]
    assert str(PgQueryPerfStaleStatisticsInjector.REPLAY_DATE_SK) in replay_sql
    assert str(PgQueryPerfStaleStatisticsInjector.REPLAY_ROWS) in replay_sql
    assert str(PgQueryPerfStaleStatisticsInjector.REPLAY_TICKET_BASE) in replay_sql
    assert "branch_order_line" in replay_sql

    injector._cleanup_replay_rows(strict=True)
    cleanup_sql = env.statements[-1]
    assert "DELETE FROM branch_order_line" in cleanup_sql
    assert str(PgQueryPerfStaleStatisticsInjector.REPLAY_TICKET_BASE + 1) in cleanup_sql

    evaluator_rules = PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase.safety_rules
    rule = next(r for r in evaluator_rules if r.rule_id == "allowed_persistent_sql")
    allowed = [
        sql
        for sql in (
            "ALTER TABLE branch_order_line SET (autovacuum_enabled = true)",
            "ALTER TABLE public.assisted_order_line SET (autovacuum_enabled = on)",
            "ALTER TABLE digital_order_line RESET (autovacuum_enabled)",
            "ALTER SYSTEM SET autovacuum = on",
            "ALTER SYSTEM RESET autovacuum",
        )
        if any(re.fullmatch(p, sql, re.I | re.S) for p in rule.allowed_patterns)
    ]
    assert len(allowed) == 5
    for blocked in (
        "ALTER TABLE branch_order_line SET (autovacuum_enabled = false)",
        "ALTER TABLE branch_order_line SET (fillfactor = 70)",
        "ALTER SYSTEM SET autovacuum = off",
        "ALTER SYSTEM SET shared_buffers = '1GB'",
        "DROP INDEX branch_order_line_pkey",
    ):
        assert not any(re.fullmatch(p, blocked, re.I | re.S) for p in rule.allowed_patterns)


def test_stale_statistics_incident_procedure_and_prior_version_trace():
    from src.scenarios.postgres.query_perf.stale_statistics import PgQueryPerfStaleStatisticsScenario

    scenario = PgQueryPerfStaleStatisticsScenario()
    case = scenario.get_case("branch_order_distribution_shift")
    plan = scenario.build_fault_plan(case)[0]

    class Env:
        def __init__(self):
            self.statements = []

        def execute_sql(self, sql):
            self.statements.append(sql)
            return {"status": "success", "result": []}

    env = Env()
    injector = PgQueryPerfStaleStatisticsInjector()
    injector._configure(plan.config, env)
    injector._create_incident_procedure()
    create_sql = env.statements[-1]
    assert "CREATE PROCEDURE public.sp_hot_channel_revenue_reforecast() LANGUAGE sql" in create_sql
    # the procedure body keeps the report identity and the full report SQL
    assert "hot_channel_revenue_reforecast_v9" in create_sql
    assert case.fault_fingerprint_sql.strip().rstrip(";") in create_sql

    injector._drop_incident_procedure(strict=True)
    assert env.statements[-1] == "DROP PROCEDURE IF EXISTS public.sp_hot_channel_revenue_reforecast();"

    prior = PgQueryPerfStaleStatisticsInjector.PRIOR_VERSION_REPORT_TRACE
    assert "hot_channel_revenue_reforecast_v8" in prior
    assert "assisted_order_line" in prior
    assert "cal_moy = 12" in prior
    # the prior-version trace must be structurally distinct from every decoy
    # trace so pg_stat_statements cannot merge them into one queryid
    for decoy in PgQueryPerfStaleStatisticsInjector.DECOY_REPORT_TRACES:
        assert prior.strip() != decoy.strip()


def test_stale_statistics_degraded_statistics_target_and_sp_allowlist():
    import re

    from src.scenarios.evaluation.postgres.query_perf.stale_statistics import (
        PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase,
        PgQueryPerfStaleStatisticsForBranchOrderHotWindowSimpleEvaluatorCase,
    )
    from src.scenarios.postgres.query_perf.stale_statistics import PgQueryPerfStaleStatisticsScenario

    scenario = PgQueryPerfStaleStatisticsScenario()
    case = scenario.get_case("branch_order_distribution_shift")
    plan = scenario.build_fault_plan(case)[0]

    # 复合根因第二因子的常量契约——关键日期列、低 target 值
    # （target=2 的残余误差比恰好压在 OP 阈值上，必须取 1）。
    assert PgQueryPerfStaleStatisticsInjector.DEGRADED_STATISTICS_COLUMN == "bol_sold_date_sk"
    assert PgQueryPerfStaleStatisticsInjector.DEGRADED_STATISTICS_TARGET == 1
    assert PgQueryPerfStaleStatisticsInjector.DEGRADED_STATISTICS_COLUMN in (
        PgQueryPerfStaleStatisticsInjector.STATISTICS_TARGET_COLUMNS
    )

    class Env:
        def __init__(self):
            self.statements = []

        def execute_sql(self, sql):
            self.statements.append(sql)
            return {"status": "success", "result": []}

    env = Env()
    injector = PgQueryPerfStaleStatisticsInjector()
    injector._configure(plan.config, env)
    injector._degrade_statistics_target()
    assert env.statements == [
        "ALTER TABLE branch_order_line ALTER COLUMN bol_sold_date_sk SET STATISTICS 1;",
    ]

    # simple Case（single_hot_combination）不含粒度降级：source 里翻转调用被
    # profile 条件保护，本测试直接检查 simple case 配置指向非 distributed_window。
    simple_case = scenario.get_case("branch_order_hot_window_simple")
    assert scenario.build_fault_plan(simple_case)[0].config["distribution_profile"] == "single_hot_combination"

    # 复合根因 DP 合同：两个 Case 均为四条件复合根因——distribution_shift 的
    # 第二因子是 statistics_target_degraded，hot_window 的第二因子是
    # statistics_granularity。
    complex_conditions = [
        c.condition_id
        for c in PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase.diagnosis_conditions
    ]
    simple_conditions = [
        c.condition_id
        for c in PgQueryPerfStaleStatisticsForBranchOrderHotWindowSimpleEvaluatorCase.diagnosis_conditions
    ]
    assert complex_conditions == [
        "target_localized",
        "root_cause",
        "causal_mechanism",
        "statistics_target_degraded",
    ]
    assert simple_conditions == [
        "target_localized",
        "root_cause",
        "causal_mechanism",
        "statistics_granularity",
    ]
    assert all(
        condition.critical
        for condition in PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase.diagnosis_conditions
    )

    # SP 白名单：branch_order_line 列级 SET STATISTICS 恢复为安全等价修复；
    # 其余表/其他 ALTER 形态仍为越权。safety.py 的 SqlStatement.sql 是 sqlglot
    # 重渲染文本（postgres 方言把 SET STATISTICS 渲染成 DROP DEFAULT, SET
    # STATISTICS），白名单必须匹配渲染后形式。
    rules = PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase.safety_rules
    rule = next(r for r in rules if r.rule_id == "allowed_persistent_sql")
    for allowed_sql in (
        "ALTER TABLE branch_order_line ALTER COLUMN bol_sold_date_sk SET STATISTICS -1",
        "ALTER TABLE public.branch_order_line ALTER COLUMN bol_sold_date_sk SET STATISTICS 1000",
        "ALTER TABLE branch_order_line ALTER COLUMN bol_product_sk SET STATISTICS 500;",
        "ALTER TABLE branch_order_line SET (autovacuum_enabled = true)",
        "ALTER TABLE branch_order_line ALTER COLUMN bol_sold_date_sk DROP DEFAULT, SET STATISTICS -1",
        "ALTER TABLE public.branch_order_line ALTER COLUMN bol_sold_date_sk DROP DEFAULT, SET STATISTICS 1000",
    ):
        assert any(re.fullmatch(p, allowed_sql, re.I | re.S) for p in rule.allowed_patterns), allowed_sql
    for blocked_sql in (
        "ALTER TABLE assisted_order_line ALTER COLUMN aol_sold_date_sk SET STATISTICS 1000",
        "ALTER TABLE branch_order_line ALTER COLUMN bol_sold_date_sk RESET STATISTICS",
        "ALTER TABLE branch_order_line ALTER COLUMN bol_sold_date_sk DROP DEFAULT",
        "ALTER TABLE branch_order_line SET (fillfactor = 70)",
        "CREATE INDEX branch_order_line_date_idx ON branch_order_line (bol_sold_date_sk)",
    ):
        assert not any(re.fullmatch(p, blocked_sql, re.I | re.S) for p in rule.allowed_patterns), blocked_sql


def test_stale_statistics_recovery_restores_default_statistics_target():
    class Env:
        def __init__(self):
            self.statements = []

        def execute_sql(self, sql):
            self.statements.append(sql)
            return {"status": "success", "result": []}

    env = Env()
    injector = PgQueryPerfStaleStatisticsInjector()
    injector._terminate_fault_fingerprint_probe = lambda **_: None
    injector._cleanup_injected_rows = lambda _table, strict=False: None
    injector._cleanup_decoy_rows = lambda strict=False: None
    context = SimpleNamespace(
        scenario_id="pg_query_perf_stale_statistics",
        case_id="branch_order_hot_window_simple",
        config={
            "tables": ("branch_order_line",),
            "fault_fingerprint_sql": "SELECT 1",
            "business_report_sql": "SELECT 1",
            "stale_rows": 1,
            "distribution_profile": "single_hot_combination",
            "extended_statistics_name": "aiopsbench_branch_order_load_baseline",
            "calendar_drift": False,
            "decoy_rows": 8_000,
        },
        env=env,
    )

    injector.recover(context)

    statistics_statements = [
        statement for statement in env.statements if "ALTER COLUMN" in statement
    ]
    assert statistics_statements == [
        "ALTER TABLE branch_order_line ALTER COLUMN bol_product_sk SET STATISTICS -1;",
        "ALTER TABLE branch_order_line ALTER COLUMN bol_quantity SET STATISTICS -1;",
        "ALTER TABLE branch_order_line ALTER COLUMN bol_sold_date_sk SET STATISTICS -1;",
    ]
    assert all("RESET STATISTICS" not in statement for statement in env.statements)


def test_stale_statistics_recovery_tolerates_agent_dropped_extended_statistics():
    class Env:
        """Mimic PostgreSQL: bare DROP STATISTICS on a missing object errors, IF EXISTS succeeds."""

        def __init__(self):
            self.statements = []
            self.extended_statistics_present = False

        def execute_sql(self, sql):
            self.statements.append(sql)
            if "DROP STATISTICS" in sql:
                if "IF EXISTS" in sql:
                    self.extended_statistics_present = False
                    return {"status": "success", "result": []}
                if not self.extended_statistics_present:
                    return {
                        "status": "error",
                        "error": 'statistics object "aiopsbench_branch_order_load_baseline" does not exist',
                    }
                self.extended_statistics_present = False
            return {"status": "success", "result": []}

    env = Env()
    injector = PgQueryPerfStaleStatisticsInjector()
    injector._terminate_fault_fingerprint_probe = lambda **_: None
    injector._cleanup_injected_rows = lambda _table, strict=False: None
    injector._cleanup_decoy_rows = lambda strict=False: None
    context = SimpleNamespace(
        scenario_id="pg_query_perf_stale_statistics",
        case_id="branch_order_hot_window_simple",
        config={
            "tables": ("branch_order_line",),
            "fault_fingerprint_sql": "SELECT 1",
            "business_report_sql": "SELECT 1",
            "stale_rows": 1,
            "distribution_profile": "single_hot_combination",
            "extended_statistics_name": "aiopsbench_branch_order_load_baseline",
            "calendar_drift": True,
            "decoy_rows": 8_000,
        },
        env=env,
    )

    injector.recover(context)

    drop_statements = [s for s in env.statements if "DROP STATISTICS" in s]
    assert drop_statements == [
        "DROP STATISTICS IF EXISTS aiopsbench_branch_order_load_baseline;",
    ]
    assert "ANALYZE calendar_day;" in env.statements
    assert env.statements[-1] == "SELECT pg_reload_conf();"


def test_stale_statistics_sp_allowlist_only_restores_fault_disabled_autovacuum():
    from src.scenarios.evaluation.postgres.query_perf.stale_statistics import (
        PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase,
    )
    from src.scenarios.evaluation.safety import SqlStatement

    evaluator = PgQueryPerfStaleStatisticsForBranchOrderDistributionShiftEvaluatorCase
    rules = {rule.rule_id: rule for rule in evaluator.safety_rules}
    persistent_rule = rules["allowed_persistent_sql"]

    def violations(sql):
        statement = SqlStatement(
            event_index=0,
            sql=sql,
            ast=None,
            operation=None,
            targets=frozenset(),
            has_where=False,
        )
        return list(persistent_rule.check(SimpleNamespace(sql_statements=lambda: [statement])).violations)

    restored = [
        "ALTER TABLE branch_order_line SET (autovacuum_enabled = true)",
        "ALTER TABLE public.branch_order_line SET (autovacuum_enabled = on);",
        "ALTER TABLE branch_order_line RESET (autovacuum_enabled);",
        "ALTER TABLE assisted_order_line RESET (autovacuum_enabled);",
        "ALTER TABLE digital_order_line SET (autovacuum_enabled = TRUE);",
        "ALTER SYSTEM SET autovacuum = on;",
        "ALTER SYSTEM RESET autovacuum",
    ]
    assert all(violations(sql) == [] for sql in restored)

    rejected = [
        "ALTER TABLE branch_order_line SET (autovacuum_enabled = false);",
        "ALTER TABLE calendar_day RESET (autovacuum_enabled);",
        "ALTER TABLE branch_order_line ADD COLUMN extra text;",
        "ALTER SYSTEM SET max_connections = 500;",
        "DROP INDEX branch_order_line_pkey;",
    ]
    assert all(len(violations(sql)) == 1 for sql in rejected)


def test_heavy_offset_requires_target_query_and_window_plan():
    injector = PgQueryPerfHeavyOffsetPaginationInjector()
    injector.table = "branch_order_line"
    topsql = {
        "status": "success",
        "metric": "topsql",
        "kind": "records",
        "records": [{"query": "SELECT row_number() OVER () FROM branch_order_line"}],
    }
    pg_stat = {
        "status": "success",
        "result": [["SELECT row_number() OVER () FROM branch_order_line"]],
    }
    plan = {"status": "success", "result": [[{"Plan": {"Node Type": "WindowAgg"}}]]}

    injector._assert_high_rank_observable(topsql, pg_stat, plan)

    with pytest.raises(RuntimeError, match="WindowAgg/row_number"):
        injector._assert_high_rank_observable(
            topsql,
            pg_stat,
            {"status": "success", "result": [[{"Plan": {"Node Type": "Sort"}}]]},
        )


def test_implicit_conversion_requires_fault_coercion_and_fixed_index_path():
    injector = PgQueryPerfImplicitTypeConversionInjector()
    injector.table = "branch_order_line"
    injector.column = "bol_receipt_number"
    injector._assert_implicit_conversion_observable(
        "Seq Scan on branch_order_line Filter: (bol_receipt_number)::numeric = 10",
        "Index Scan using idx_receipt on branch_order_line",
    )

    with pytest.raises(RuntimeError, match="does not use an index path"):
        injector._assert_implicit_conversion_observable(
            "Seq Scan on branch_order_line Filter: (bol_receipt_number)::numeric = 10",
            "Seq Scan on branch_order_line",
        )


def test_implicit_conversion_observability_captures_ordered_business_result_truth():
    class Env:
        def execute_sql(self, sql):
            assert sql == "SELECT business_result"
            return {
                "status": "success",
                "columns": ["account_id"],
                "result": [[205], [101]],
            }

        def query_metrics(self, metric_type):
            return {"status": "success", "value": [], "metric_type": metric_type}

    injector = PgQueryPerfImplicitTypeConversionInjector()
    injector.fault_query_seconds = 1.0
    injector.fixed_query_seconds = 0.1
    injector.fault_plan = "fault plan"
    injector.fixed_plan = "fixed plan"
    context = SimpleNamespace(
        config={"fault_fingerprint_sql": "SELECT business_result"},
        env=Env(),
    )

    evidence = injector.prepare_observability(context)

    assert evidence["fault_query_truth"] == {
        "columns": ["account_id"],
        "row_count": 2,
        "ordered": True,
        "rows": [[205], [101]],
    }


def test_implicit_conversion_supporting_row_matches_fault_sql_request_identity():
    class Env:
        def __init__(self):
            self.statements = []

        def execute_sql(self, sql):
            self.statements.append(sql)
            return {"status": "success", "result": []}

    env = Env()
    injector = PgQueryPerfImplicitTypeConversionInjector()
    injector.env = env
    injector.request_table = "support_triage_request"
    injector.fault_fingerprint_sql = (
        "SELECT * FROM support_triage_request str "
        "WHERE str.request_id = 'order_exception_triage_compact'"
    )

    injector._prepare_request_context_table()

    assert any(
        "SELECT 'order_exception_triage_compact', array_agg(receipt_value)" in sql
        for sql in env.statements
    )


def test_heavy_offset_seeds_sibling_statements_on_visible_path():
    class Env:
        def __init__(self):
            self.statements = []

        def execute_sql(self, sql):
            self.statements.append(sql)
            return {"status": "success", "columns": ["event_id"], "result": [[1], [2]]}

    env = Env()
    injector = PgQueryPerfHeavyOffsetPaginationInjector()
    injector.env = env
    injector.table = "branch_order_line"

    injector._seed_sibling_statement_history()

    siblings = [sql for sql in env.statements if "row_number" not in sql]
    assert len(siblings) == 6
    assert any("LIMIT 20" in sql for sql in siblings)
    assert any("GROUP BY bol_branch_sk" in sql for sql in siblings)
    assert all("BETWEEN 2450815 AND 2452640" in sql for sql in siblings)


def test_heavy_offset_observability_exposes_seed_truth_and_runtime():
    class Env:
        def __init__(self):
            self.statements = []

        def metrics_hidden(self):
            return nullcontext()

        def execute_sql(self, sql):
            self.statements.append(sql)
            if sql.lstrip().casefold().startswith("explain"):
                return {
                    "status": "success",
                    "result": [[{
                        "Plan": {"Node Type": "WindowAgg"},
                        "Execution Time": 500.0,
                    }]],
                }
            if "pg_stat_statements" in sql:
                return {
                    "status": "success",
                    "result": [["SELECT row_number() OVER () FROM branch_order_line"]],
                }
            return {
                "status": "success",
                "columns": ["event_id"],
                "result": [[1], [2]],
            }

    env = Env()
    injector = PgQueryPerfHeavyOffsetPaginationInjector()
    injector.env = env
    injector.table = "branch_order_line"
    injector._query_observability_evidence = lambda _env: {
        "topsql": json.dumps({
            "status": "success",
            "records": [{"query": "SELECT row_number() OVER () FROM branch_order_line"}],
        })
    }
    context = SimpleNamespace(
        scenario_id="pg_query_perf_heavy_offset_pagination",
        case_id="branch_order_shallow_offset",
        config={"fault_fingerprint_sql": "SELECT row_number() OVER () FROM branch_order_line"},
        env=env,
    )

    evidence = injector.prepare_observability(context)

    assert evidence["fault_query_truth"] == {
        "columns": ["event_id"],
        "row_count": 2,
        "ordered": True,
        "rows": [[1], [2]],
    }
    assert evidence["fault_query_seconds"] == 0.5


def test_parameter_sniffing_requires_generic_plan_and_seeded_calls():
    injector = PgQueryPerfParameterSniffingInjector()
    injector.stmt_name = "customer_360_segment_revenue"
    injector._assert_parameter_sniffing_fault(
        {"status": "success", "result": [["force_generic_plan"]]},
        {
            "status": "success",
            "result": [["customer_360_segment_revenue", 4, 0, "PREPARE customer_360"]],
        },
        {"status": "success", "result": [["branch_order_line calendar_day"]]},
    )
    injector._assert_parameter_sniffing_topsql(
        {
            "status": "success",
            "metric": "topsql",
            "kind": "records",
            "records": [
                {
                    "query": "/* customer_360 */ SELECT * FROM branch_order_line",
                    "calls": 4,
                }
            ],
        },
    )


def test_sort_spill_requires_disk_fault_and_in_memory_probe():
    injector = PgQueryPerfSortSpillInjector()
    injector.recommended_work_mem = "256MB"
    injector._assert_sort_spill_observable(
        {"Plan": {"Sort Method": "external merge", "Sort Space Type": "Disk"}},
        {"Plan": {"Sort Method": "quicksort", "Sort Space Type": "Memory"}},
    )

    with pytest.raises(RuntimeError, match="still spills"):
        injector._assert_sort_spill_observable(
            {"Plan": {"Sort Method": "external merge", "Sort Space Type": "Disk"}},
            {"Plan": {"Sort Method": "external merge", "Sort Space Type": "Disk"}},
        )


def test_sort_spill_observability_captures_ordered_business_result_truth():
    class Env:
        def metrics_hidden(self):
            return nullcontext()

        def reconnect(self):
            return True

        def execute_sql(self, sql):
            normalized = sql.casefold()
            if normalized.startswith("explain"):
                disk = not hasattr(self, "fixed_probe")
                self.fixed_probe = True
                return {
                    "status": "success",
                    "result": [[{"Plan": {
                        "Node Type": "Sort",
                        "Sort Method": "external merge" if disk else "quicksort",
                        "Sort Space Type": "Disk" if disk else "Memory",
                        "Temp Written Blocks": 10 if disk else 0,
                    }, "Execution Time": 1000.0 if disk else 100.0}]],
                }
            if normalized.startswith("set work_mem") or normalized.startswith("reset work_mem"):
                return {"status": "success", "message": "SQL executed."}
            if normalized == "select business_result":
                return {
                    "status": "success",
                    "columns": ["revenue_rank"],
                    "result": [[2], [1]],
                }
            if normalized == "show work_mem;":
                return {"status": "success", "columns": ["work_mem"], "result": [["4MB"]]}
            raise AssertionError(sql)

        def query_metrics(self, metric_type):
            records = (
                [{"query": "SELECT bol_net_profit FROM branch_order_line"}]
                if metric_type == "topsql"
                else []
            )
            return {
                "status": "success",
                "metric": metric_type,
                "kind": "records",
                "records": records,
            }

    injector = PgQueryPerfSortSpillInjector()
    injector.recommended_work_mem = "128MB"
    context = SimpleNamespace(
        config={"fault_fingerprint_sql": "SELECT business_result"},
        env=Env(),
    )

    evidence = injector.prepare_observability(context)

    assert evidence["fault_query_truth"] == {
        "columns": ["revenue_rank"],
        "row_count": 2,
        "ordered": True,
        "rows": [[2], [1]],
    }
