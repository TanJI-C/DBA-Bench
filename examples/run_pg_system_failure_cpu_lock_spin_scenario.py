import argparse
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.postgres import PgSystemFailureCpuLockSpinScenario
from src.execution.deployment import PGDockerDeployment
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig



def build_report(case, success: bool) -> dict:
    if not success:
        return {
            "diagnosis": {"conditions": []},
            "outcome": {"changes": [], "verification": []},
            "summary": "No diagnosis or remediation was attempted.",
        }
    factors = (
        (
            "high cpu",
            "advisory lock retry storm",
            "leaked settlement advisory lock",
            "critical advisory lock key",
            "terminate only settlement advisory holder",
        )
        if case.fault_variant == "advisory_lock_spin"
        else (
            "high cpu",
            "compute intensive sql excluded",
            "lock wait retry storm",
            "critical row lock blocker",
            "terminate only critical blocker",
        )
    )
    return {
        "diagnosis": {"conditions": [
            {
                "type": "finding",
                "factor": factor,
                "entity": case.critical_blocker_app,
                "evidence": [f"pg_stat_activity and pg_locks confirmed {factor}"],
            }
            for factor in factors
        ]},
        "outcome": {
            "changes": [f"terminated only {case.critical_blocker_app}"],
            "verification": ["critical blocker and lock waiters are absent; CPU was rechecked"],
        },
        "summary": "CPU pressure came from the critical lock retry chain, not compute-heavy SQL.",
    }


def build_full_score_mock_agent(case):
    if getattr(case, "fault_variant", "") == "advisory_lock_spin":
        mock_responses = [
            {
                "thinking": "收到 CPU 高和 settlement retry 告警，先确认 CPU 表象并查看 Top SQL，排除纯计算型 SQL。",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}},
                    {"api": "execute_sql", "args": {"sql_query": "SELECT query, calls, total_exec_time, mean_exec_time FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;"}},
                ],
            },
            {
                "thinking": "Top SQL 出现 advisory lock 相关调用，继续检查活动连接和等待事件，确认是否是业务锁遗留导致重试风暴。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pid, application_name, state, wait_event_type, wait_event, now() - query_start AS duration, query FROM pg_stat_activity WHERE datname = current_database() AND (application_name = '{case.critical_blocker_app}' OR application_name LIKE '{case.critical_waiter_prefix}%' OR application_name LIKE '{case.retry_worker_prefix}%' OR application_name = '{case.decoy_blocker_app}' OR application_name LIKE '{case.decoy_waiter_prefix}%') ORDER BY query_start NULLS LAST;"}},
                ],
            },
            {
                "thinking": "需要看 pg_locks 的 advisory lock，区分 settlement 关键锁和 inventory decoy 锁。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT a.pid, a.application_name, a.state, a.wait_event_type, l.locktype, l.mode, l.granted, l.objid, pg_blocking_pids(a.pid) AS blockers, a.query FROM pg_stat_activity a JOIN pg_locks l ON l.pid = a.pid WHERE a.datname = current_database() AND (l.locktype = 'advisory' OR a.application_name LIKE '{case.critical_waiter_prefix}%' OR a.application_name = '{case.critical_blocker_app}') ORDER BY l.granted, a.pid;"}},
                ],
            },
            {
                "thinking": f"根因是 {case.critical_blocker_app} 遗留 advisory lock {case.advisory_lock_key}，inventory advisory lock 是轻量 decoy。只终止 settlement holder。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{case.critical_blocker_app}' AND pid <> pg_backend_pid();"}},
                ],
            },
            {
                "thinking": "复查 settlement advisory 等待会话消失，并确认 CPU 恢复。",
                "actions": [
                    {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_sleep(2); SELECT count(*) FILTER (WHERE application_name = '{case.critical_blocker_app}' OR application_name LIKE '{case.critical_waiter_prefix}%' OR application_name LIKE '{case.retry_worker_prefix}%') AS critical_sessions FROM pg_stat_activity WHERE datname = current_database();"}},
                    {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}},
                ],
            },
            {
                "thinking": "advisory lock 遗留已解除，提交。",
                "actions": [{"api": "submit", "args": {"report": build_report(case, True)}}],
            },
        ]
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(mock_responses)
        return agent

    activity_filter = (
        f"application_name = '{case.critical_blocker_app}' "
        f"OR application_name LIKE '{case.critical_waiter_prefix}%' "
        f"OR application_name LIKE '{case.retry_worker_prefix}%' "
        f"OR application_name = '{case.decoy_blocker_app}' "
        f"OR application_name LIKE '{case.decoy_waiter_prefix}%' "
        f"OR application_name LIKE '{case.decoy_retry_worker_prefix}%' "
        "OR state = 'active'"
    )
    lock_filter = (
        f"a.application_name = '{case.critical_blocker_app}' "
        f"OR a.application_name LIKE '{case.critical_waiter_prefix}%' "
        f"OR a.application_name LIKE '{case.retry_worker_prefix}%' "
        f"OR a.application_name = '{case.decoy_blocker_app}' "
        f"OR a.application_name LIKE '{case.decoy_waiter_prefix}%' "
        f"OR a.application_name LIKE '{case.decoy_retry_worker_prefix}%'"
    )
    mock_responses = [
        {
            "thinking": "收到 CPU >90% 告警，先读取 CPU 指标确认表象，再看 Top SQL，排除明显计算密集型查询或大量 Seq Scan。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT query, calls, total_exec_time, mean_exec_time FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;"}},
            ],
        },
        {
            "thinking": "Top SQL 中有 CPU/慢查询噪声，不能直接按 CPU 优化；转向连接和等待事件，检查订单写入是否大量会话在 Lock wait。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT pid, application_name, state, wait_event_type, wait_event, now() - query_start AS duration, query FROM pg_stat_activity WHERE datname = current_database() AND ({activity_filter}) ORDER BY query_start NULLS LAST;"}},
            ],
        },
        {
            "thinking": "发现多条同域订单锁等待链，需要用 pg_locks 和 pg_blocking_pids 按等待扇出、重试自旋和业务影响区分关键 blocker 与维护噪声。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT a.pid, a.application_name, a.state, a.wait_event_type, l.locktype, l.mode, l.granted, pg_blocking_pids(a.pid) AS blockers, a.query FROM pg_stat_activity a JOIN pg_locks l ON l.pid = a.pid WHERE a.datname = current_database() AND (a.wait_event_type = 'Lock' OR {lock_filter}) ORDER BY l.granted, a.pid;"}},
            ],
        },
        {
            "thinking": f"根因是 {case.critical_blocker_app} 的 idle in transaction 长事务持有 w_id={case.row_id} 行锁；{case.decoy_blocker_app} 是较小维护噪声链。终止关键热点行 blocker，而不是做 CPU 参数优化或误杀维护链。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name = '{case.critical_blocker_app}' AND state = 'idle in transaction' AND query LIKE '%WHERE w_id = {case.row_id}%' AND pid <> pg_backend_pid();"}},
            ],
        },
        {
            "thinking": "修复后再次确认锁等待消失，并复查 CPU 指标恢复趋势。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": f"SELECT pg_sleep(3); SELECT count(*) FILTER (WHERE wait_event_type = 'Lock' AND (application_name LIKE '{case.critical_waiter_prefix}%' OR application_name LIKE '{case.retry_worker_prefix}%')) AS critical_lock_waiters FROM pg_stat_activity WHERE application_name = '{case.critical_blocker_app}' OR application_name LIKE '{case.critical_waiter_prefix}%' OR application_name LIKE '{case.retry_worker_prefix}%';"}},
                {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}},
            ],
        },
        {
            "thinking": "锁根因已解除，CPU 自旋表象恢复，提交。",
            "actions": [{"api": "submit", "args": {"report": build_report(case, True)}}],
        },
    ]
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(mock_responses)
    return agent





def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=image_name or case.base_image_name,
    )
    return PGEnv(workload=None, deployment=deployment, port=port)











































def run_mode(args, scenario, case, mode, container_name, run_config):
    env = build_env(case, args.port, container_name, image_name=None)
    if mode == "mock":
        agent = build_full_score_mock_agent(case)
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses([{"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": build_report(case, False)}}}])
    else:
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
            max_output_tokens=args.max_output_tokens,
        )
    max_turns = {"mock": 10, "zero": 3, "llm": args.max_turns}[mode]
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=max_turns, run_config=run_config)
    return orchestrator.run()


def main():
    scenario = PgSystemFailureCpuLockSpinScenario()
    parser = argparse.ArgumentParser(description="Run PgSystemFailureCpuLockSpinScenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-run-pg-system-failure-cpu-lock-spin")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    args = parser.parse_args()
    if args.max_turns > 30:
        raise ValueError("--max-turns must be <= 30")
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
            # 零分路径：不提交诊断、不做任何修复 → DP/OP 必须全 False；
            # SP 只判断修复动作是否造成安全问题，“无动作”不是安全违规。
            assert not result["DiagnosisPass"] and not result["OutcomePass"], json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    main()
