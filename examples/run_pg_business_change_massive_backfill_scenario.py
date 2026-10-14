import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.base import evaluation_passed
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import (
    PgBusinessChangeMassiveBackfillCase,
    PgBusinessChangeMassiveBackfillScenario,
)
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


def build_final_void_exclusion(case: PgBusinessChangeMassiveBackfillCase, stage_alias: str) -> str:
    """Exclude rows whose latest operation-event ruling is an annulment.

    Rows annulled after the freeze roll to the next release window and must
    stay uncorrected; a later row_restored event puts a row back into scope.
    """
    event_table = case.operation_event_table
    if not event_table:
        return ""
    return (
        f"\n              AND NOT EXISTS (SELECT 1 FROM {event_table} e "
        f"WHERE e.{case.pk_column} = {stage_alias}.{case.pk_column} "
        f"AND e.release_batch_id = '{case.release_batch_id}' "
        f"AND e.event_type = 'row_annulled' "
        f"AND NOT EXISTS (SELECT 1 FROM {event_table} e2 "
        f"WHERE e2.{case.pk_column} = e.{case.pk_column} "
        f"AND e2.release_batch_id = e.release_batch_id "
        f"AND e2.event_type = 'row_restored' "
        f"AND e2.event_at > e.event_at))"
    )


def build_batch_backfill_sql(case: PgBusinessChangeMassiveBackfillCase) -> str:
    table = case.table
    pk = case.pk_column
    target = case.target_column
    stage_table = case.stage_table
    stage_value = case.stage_value_column
    release_batch = case.release_batch_id
    batch_size = case.batch_size
    freeze_predicate = (
        f"\n              AND s.loaded_at <= '{case.release_freeze_cutoff}'"
        if case.release_freeze_cutoff
        else ""
    )
    void_predicate = build_final_void_exclusion(case, "s")
    return f"""
DO $$
DECLARE
    v_batch_size integer := {batch_size};
    v_last_pk bigint := -9223372036854775808;
    v_max_pk bigint;
    v_updated integer := 0;
BEGIN
    LOOP
        WITH batch AS (
            SELECT s.{pk}
            FROM {stage_table} s
            JOIN {table} t USING ({pk})
            WHERE s.release_batch_id = '{release_batch}'
              AND t.{target} IS DISTINCT FROM s.{stage_value}
              AND s.{pk} > v_last_pk{freeze_predicate}{void_predicate}
            ORDER BY s.{pk}
            LIMIT v_batch_size
        ),
        bounds AS (
            SELECT min({pk}) AS min_pk, max({pk}) AS max_pk
            FROM batch
        )
        UPDATE {table} AS t
        SET {target} = s.{stage_value},
            c_last_update = now()
        FROM bounds b
        JOIN {stage_table} s
          ON s.{pk} BETWEEN b.min_pk AND b.max_pk
         AND s.release_batch_id = '{release_batch}'{freeze_predicate}{void_predicate}
        WHERE b.min_pk IS NOT NULL
          AND t.{pk} = s.{pk}
          AND t.{target} IS DISTINCT FROM s.{stage_value};

        GET DIAGNOSTICS v_updated = ROW_COUNT;
        EXIT WHEN v_updated = 0;

        SELECT max(s.{pk}) INTO v_max_pk
        FROM {stage_table} s
        JOIN {table} t USING ({pk})
        WHERE s.release_batch_id = '{release_batch}'{freeze_predicate}
          AND t.{target} IS NOT DISTINCT FROM s.{stage_value}
          AND s.{pk} > v_last_pk;
        v_last_pk := COALESCE(v_max_pk, v_last_pk);

        PERFORM pg_sleep(0.05);
    END LOOP;
END $$;
"""


def build_mock_responses(case: PgBusinessChangeMassiveBackfillCase):
    table = case.table
    pk = case.pk_column
    target = case.target_column
    stage_table = case.stage_table
    release_batch = case.release_batch_id
    stage_value = case.stage_value_column
    batch_sql = build_batch_backfill_sql(case)
    survey_actions = [
        {"api": "execute_sql", "args": {"sql_query":
            f"SELECT c.relname, c.reltuples::bigint AS estimated_rows, "
            f"pg_size_pretty(pg_relation_size(c.oid)) AS table_size, s.n_live_tup, s.n_dead_tup "
            f"FROM pg_class c JOIN pg_stat_user_tables s ON s.relid = c.oid "
            f"WHERE c.relname IN ('{table}', '{stage_table}', '{case.preview_table}', '{case.audit_table}') "
            f"ORDER BY c.relname;"}},
        {"api": "execute_sql", "args": {"sql_query":
            f"SELECT s.release_batch_id, count(*) AS pending_rows, min(s.{pk}) AS first_pk, max(s.{pk}) AS last_pk, "
            f"count(*) FILTER (WHERE t.{target} IS DISTINCT FROM s.{stage_value}) AS not_matching_stage "
            f"FROM {stage_table} s JOIN {table} t USING ({pk}) "
            f"WHERE s.release_batch_id = '{release_batch}' AND t.{target} IS NULL "
            f"GROUP BY s.release_batch_id;"}},
        {"api": "query_metrics", "args": {"metric_type": "qps", "target": None}},
        {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
    ]
    if case.operation_event_table:
        survey_actions.insert(1, {"api": "execute_sql", "args": {"sql_query":
            f"SELECT event_type, release_batch_id, count(*) AS event_rows, "
            f"min(event_at) AS first_event, max(event_at) AS last_event "
            f"FROM {case.operation_event_table} "
            f"GROUP BY event_type, release_batch_id "
            f"ORDER BY event_type, release_batch_id;"}})
    freeze_verify = (
        f" AND s.loaded_at <= '{case.release_freeze_cutoff}'" if case.release_freeze_cutoff else ""
    )
    void_verify = (
        f"\n                    AND NOT EXISTS (SELECT 1 FROM {case.operation_event_table} e "
        f"WHERE e.{pk} = s.{pk} AND e.release_batch_id = '{release_batch}' "
        f"AND e.event_type = 'row_annulled' "
        f"AND NOT EXISTS (SELECT 1 FROM {case.operation_event_table} e2 "
        f"WHERE e2.{pk} = e.{pk} AND e2.release_batch_id = e.release_batch_id "
        f"AND e2.event_type = 'row_restored' AND e2.event_at > e.event_at))"
        if case.operation_event_table
        else ""
    )
    return [
        {
            "thinking": "先评估目标表规模、发布 stage 切片、发布操作事件裁定、待回填行数和直接全量 UPDATE 风险，同时采集 QPS 与磁盘 I/O。",
            "actions": survey_actions,
        },
        {
            "thinking": "待回填行数较多，采用发布 stage 驱动的主键范围加 LIMIT 批处理，并在批次间 pg_sleep 限流；最新裁定为作废的清单行滚入下一窗口、不在本次订正。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": batch_sql}},
            ],
        },
        {
            "thinking": "回填后再次采集 QPS 和磁盘 I/O，确认负载没有继续恶化。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "qps", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "disk_io", "target": None}},
            ],
        },
        {
            "thinking": "验证目标列已经按 release stage 完成订正、作废行保持未订正且没有越界更新。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query":
                    f"SELECT count(*) FILTER (WHERE t.{target} IS NULL) AS pending_rows, "
                    f"count(*) FILTER (WHERE t.{target} IS DISTINCT FROM s.{stage_value}) AS incorrect_rows "
                    f"FROM {table} t JOIN {stage_table} s USING ({pk}) "
                    f"WHERE s.release_batch_id = '{release_batch}'"
                    + freeze_verify + void_verify + ";"}},
                {"api": "execute_sql", "args": {"sql_query":
                    f"SELECT count(*) FROM {table} t "
                    f"WHERE t.{target} IS NOT NULL "
                    f"AND NOT EXISTS (SELECT 1 FROM {stage_table} s "
                    f"WHERE s.{pk} = t.{pk} AND s.release_batch_id = '{release_batch}');"}},
            ],
        },
        {
            "thinking": "分批回填完成且负载已复核，提交结果。",
            "actions": [
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def run_mode(args, scenario, case, mode, container_name, run_config):
    env = PGEnv(port=args.port, allow_sampler_jitter=True)
    env.deployment.container_name = container_name
    if mode == "mock":
        agent = MockLLMAgent(url='mock', api_key='mock', system_prompt='You are a DBA agent.', use_native_tools=False)
        agent.set_mock_responses(build_mock_responses(case))
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses([{"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": EMPTY_REPORT}}}])
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    default_max_turns = {"mock": 10, "zero": 3, "llm": 12}
    max_turns = args.max_turns if args.max_turns is not None else default_max_turns[mode]
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=max_turns, run_config=run_config)
    return orchestrator.run()


def main():
    scenario = PgBusinessChangeMassiveBackfillScenario()
    parser = argparse.ArgumentParser(description="Run PgBusinessChangeMassiveBackfillScenario.")
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario.cases],
    )
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-run-pg-business-change-massive-backfill-scenario")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )
    case = scenario.get_case(args.case)
    modes = ("mock", "zero", "llm") if args.mode == "all" else (args.mode,)
    for mode in modes:
        result = run_mode(
            args,
            scenario,
            case,
            mode,
            f"{args.container_name}-{case.case_id}-{mode}",
            run_config,
        )
        print(f"[{mode}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")
        if mode == "mock":
            assert evaluation_passed(result), json.dumps(result, ensure_ascii=False)
        elif mode == "zero":
            assert not evaluation_passed(result), json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    main()
