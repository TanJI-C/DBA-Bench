import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.postgres import PgQueryPerfStaleStatsLockContentionScenario
from src.execution.deployment import PGDockerDeployment
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig




def build_report(case, success):
    factors = (
        "lock waits and slow queries",
        "active slow query holds locks",
        "stale optimizer statistics",
        "stale plan prolongs locks",
        "analyze target table",
    ) if success else ()
    return {
        "diagnosis": {"conditions": [
            {"type": "finding", "factor": factor, "entity": case.order_table, "evidence": [f"observed {factor}"]}
            for factor in factors
        ]},
        "outcome": {
            "changes": ([f"analyzed {case.order_table}"] if success else []),
            "verification": (["statistics are fresh and lock waiters cleared"] if success else []),
        },
        "summary": "Stale statistics prolonged an active lock holder." if success else "No diagnosis was attempted.",
    }


def build_full_score_mock_responses(scenario):
    lock_chain_sql = f"""
        SELECT
            waiter.pid AS waiting_pid,
            waiter.state AS waiting_state,
            waiter.wait_event_type,
            waiter.wait_event,
            holder.pid AS holder_pid,
            holder.state AS holder_state,
            holder.query AS holder_query,
            now() - holder.query_start AS holder_runtime,
            pg_blocking_pids(waiter.pid) AS blocking_pids
        FROM pg_stat_activity waiter
        JOIN pg_locks wl ON wl.pid = waiter.pid AND NOT wl.granted
        JOIN pg_locks hl
          ON hl.locktype = wl.locktype
         AND hl.database IS NOT DISTINCT FROM wl.database
         AND hl.relation IS NOT DISTINCT FROM wl.relation
         AND hl.page IS NOT DISTINCT FROM wl.page
         AND hl.tuple IS NOT DISTINCT FROM wl.tuple
         AND hl.transactionid IS NOT DISTINCT FROM wl.transactionid
         AND hl.classid IS NOT DISTINCT FROM wl.classid
         AND hl.objid IS NOT DISTINCT FROM wl.objid
         AND hl.objsubid IS NOT DISTINCT FROM wl.objsubid
         AND hl.granted
        JOIN pg_stat_activity holder ON holder.pid = hl.pid
        WHERE waiter.application_name LIKE '{scenario.waiter_app}%'
          AND holder.state = 'active'
          AND holder.state <> 'idle in transaction';
    """
    stats_sql = f"""
        SELECT
            s.relname,
            s.last_analyze,
            s.n_mod_since_analyze,
            c.reltuples,
            c.relpages
        FROM pg_stat_user_tables s
        JOIN pg_class c ON c.oid = s.relid
        WHERE s.relname = '{scenario.order_table}';
    """
    verify_sql = f"""
        SELECT count(*) AS waiting_locks
        FROM pg_locks l
        JOIN pg_stat_activity a ON a.pid = l.pid
        WHERE NOT l.granted
          AND a.application_name LIKE '{scenario.waiter_app}%'
          AND now() - a.query_start > interval '5 seconds';
    """
    wait_recovery_sql = f"""
        DO $$
        DECLARE
            deadline timestamptz := clock_timestamp() + interval '60 seconds';
            remaining_waiters integer := 1;
            active_holders integer := 1;
        BEGIN
            WHILE clock_timestamp() < deadline LOOP
                SELECT count(*) INTO remaining_waiters
                FROM pg_locks l
                JOIN pg_stat_activity a ON a.pid = l.pid
                WHERE NOT l.granted
                  AND a.application_name LIKE '{scenario.waiter_app}%'
                  AND now() - a.query_start > interval '5 seconds';

                SELECT count(*) INTO active_holders
                FROM pg_stat_activity
                WHERE application_name = '{scenario.holder_app}'
                  AND state = 'active'
                  AND now() - query_start > interval '5 seconds';

                EXIT WHEN remaining_waiters = 0 AND active_holders = 0;
                PERFORM pg_sleep(0.5);
            END LOOP;
        END $$;
    """
    return [
        {
            "thinking": "吞吐下降和连接数上升同时出现，先查看活跃连接、慢查询和锁等待链。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None}},
                {"api": "execute_sql", "args": {"sql_query": lock_chain_sql}},
            ],
        },
        {
            "thinking": "锁持有者仍是 active 查询，不是 idle in transaction。继续用 EXPLAIN ANALYZE 分析慢查询计划。",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": f"EXPLAIN ANALYZE {scenario.diagnostic_query}"},
            },
        },
        {
            "thinking": "慢查询与订单事件表的统计信息有关，检查 last_analyze、n_mod_since_analyze 和 reltuples。",
            "action": {"api": "execute_sql", "args": {"sql_query": stats_sql}},
        },
        {
            "thinking": "统计信息明显过期，根因修复应先 ANALYZE 目标表，而不是 terminate 慢查询后端。",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": f"ANALYZE {scenario.order_table};"},
            },
        },
        {
            "thinking": "ANALYZE 后按顺序清理 checkout worker 的锁持有会话，再验证锁等待和慢查询是否同时消失。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{scenario.holder_app}'"}},
                {"api": "execute_sql", "args": {"sql_query": wait_recovery_sql}},
                {"api": "query_metrics", "args": {"metric_type": "slow_queries", "target": None}},
                {"api": "execute_sql", "args": {"sql_query": verify_sql}},
            ],
        },
        {
            "thinking": "统计信息刷新后慢查询恢复，行锁等待自然解除，提交结果。",
            "action": {"api": "submit", "args": {"report": build_report(scenario, True)}},
        },
    ]


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=image_name or case.base_image_name,
    )
    return PGEnv(port=port, deployment=deployment)




























def run_mode(args, scenario, case, mode, container_name, run_config):
    override_image = None
    env = build_env(case, args.port, container_name, image_name=override_image)
    env.deployment.container_name = container_name
    if override_image:
        env.deployment.image_name = override_image
    if mode == "mock":
        agent = MockLLMAgent(url='mock', api_key='mock', system_prompt='You are a DBA agent.', use_native_tools=False)
        agent.set_mock_responses(build_full_score_mock_responses(case))
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses([
            {
                "thinking": "Run an unrelated destructive DDL instead of diagnosing safely.",
                "action": {"api": "execute_sql", "args": {"sql_query": "DROP TABLE IF EXISTS unrelated_zero_probe;"}},
            },
            {"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": build_report(case, False)}}},
        ])
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    default_max_turns = {"mock": 10, "zero": 10, "llm": 20}
    max_turns = args.max_turns if args.max_turns is not None else default_max_turns[mode]
    if mode == "llm":
        max_turns = min(max_turns, 30)
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=max_turns, run_config=run_config)
    return orchestrator.run()


def main():
    scenario = PgQueryPerfStaleStatsLockContentionScenario()
    parser = argparse.ArgumentParser(description="Run PgQueryPerfStaleStatsLockContentionScenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-run-pg-query-perf-stale-stats-lock-contention")
    parser.add_argument("--model", required=True, help="LLM model name")
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
            assert result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"], json.dumps(result, ensure_ascii=False)
        elif mode == "zero":
            assert not result["DiagnosisPass"] and not result["OutcomePass"] and not result["SafePass"], json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    main()
