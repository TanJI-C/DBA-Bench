import argparse
import json
import os
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgSystemFailureIoCheckpointSpikesScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload



# 6 步模板：先看 PG 整体活动（active sessions 数量，确认业务被 checkpoint 阻塞）→
# disk_io 时序 → bgwriter 验证 → ALTER + reload → 验证 pg_stat_activity 恢复 → submit。
# 不走 query_metrics(workload_activity) 因为它的 ring buffer 数据有 30s 滞后，
# 改走 pg_stat_activity 实时反映 PG 真实繁忙度。
PG_STAT_ACTIVE_SQL = """
SELECT pid, application_name, state, wait_event_type, wait_event,
       substring(query, 1, 80) AS q
FROM pg_stat_activity
WHERE datname = current_database()
ORDER BY pid;
"""


FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": (
            "Step 1: 看 PG 整体活动（active sessions + wait_event）。"
            "checkpoint 频繁刷脏时预期看到 sessions 多在 wait_event=IO/DataFileWrite 或 wait_event_type=IO。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": PG_STAT_ACTIVE_SQL}},
    },
    {
        "thinking": (
            "Step 2: 噪声确认业务写延迟周期性飙高，再看容器磁盘写入 I/O 时序，确认存在写入毛刺。"
        ),
        "action": {"api": "query_metrics", "args": {"metric_type": "disk_io"}},
    },
    {
        "thinking": (
            "Step 3: 磁盘写入毛刺常见来源是频繁 checkpoint，查询 bgwriter 统计确认 "
            "checkpoints_req 是否明显高于 checkpoints_timed。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT checkpoints_timed, checkpoints_req, buffers_checkpoint, "
                        "checkpoint_write_time, checkpoint_sync_time FROM pg_stat_bgwriter;"
                    )
                },
            },
        ],
    },
    {
        "thinking": (
            "Step 4: requested checkpoint 异常直接指向 checkpoint 参数配置过小，"
            "先调大 checkpoint 周期。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": "ALTER SYSTEM SET checkpoint_timeout = '5min';"}},
    },
    {
        "thinking": "Step 4b: 调大 WAL 容量，降低 requested checkpoint 频率。",
        "action": {"api": "execute_sql", "args": {"sql_query": "ALTER SYSTEM SET max_wal_size = '1GB';"}},
    },
    {
        "thinking": "Step 4c: 提高 completion target，让 checkpoint 写盘更平滑。",
        "action": {"api": "execute_sql", "args": {"sql_query": "ALTER SYSTEM SET checkpoint_completion_target = '0.9';"}},
    },
    {
        "thinking": "Step 4d: checkpoint 参数 reload 生效，无需 restart。",
        "action": {"api": "execute_sql", "args": {"sql_query": "SELECT pg_reload_conf(); SELECT pg_sleep(1);"}},
    },
    {
        "thinking": (
            "Step 5: 修复后重新检查参数和 bgwriter 统计，确认配置已经生效、"
            "checkpoints_req 不再异常。"
        ),
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT name, setting, unit FROM pg_settings "
                    "WHERE name IN ('checkpoint_timeout', 'max_wal_size', "
                    "'checkpoint_completion_target') ORDER BY name;"
                )
            },
        },
    },
    {
        "thinking": "Step 5b: 复查 bgwriter 统计，确认 checkpoint 压力不再继续恶化。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT checkpoints_timed, checkpoints_req, buffers_checkpoint, "
                    "checkpoint_write_time, checkpoint_sync_time FROM pg_stat_bgwriter;"
                )
            },
        },
    },
    {
        "thinking": (
            "Step 6: 配置生效、bgwriter 恢复正常，再看一次 pg_stat_activity 确认业务写延迟尖刺消失、"
            "active sessions 的 wait_event 不再集中于 IO。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": PG_STAT_ACTIVE_SQL}},
    },
    {
        "thinking": "Step 7: 证据链和修复验证完成，提交。",
        "action": {"api": "submit", "args": {"report": PgSystemFailureIoCheckpointSpikesScenario().get_case('checkout_checkpoint_spikes').reference_report}},
    },
]

SIMPLE_FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "先确认周期性写延迟对应真实磁盘 I/O 尖峰。",
        "action": {"api": "query_metrics", "args": {"metric_type": "disk_io"}},
    },
    {
        "thinking": "检查 checkpoint 周期、WAL 上限和写入平滑参数。",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "SELECT current_setting('checkpoint_timeout'), "
                    "current_setting('max_wal_size'), "
                    "current_setting('checkpoint_completion_target');"
                )
            },
        },
    },
    {
        "thinking": "用 bgwriter 统计确认 requested checkpoint，并核对低频 calendar lookup 只是背景流量。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT checkpoints_timed, checkpoints_req, buffers_checkpoint, "
                        "checkpoint_write_time, checkpoint_sync_time FROM pg_stat_bgwriter;"
                    )
                },
            },
            {"api": "query_metrics", "args": {"metric_type": "workload_activity"}},
        ],
    },
    {
        "thinking": "恢复安全 checkpoint 参数并 reload，无需重启数据库。",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "ALTER SYSTEM SET checkpoint_timeout = '5min';"}},
            {"api": "execute_sql", "args": {"sql_query": "ALTER SYSTEM SET max_wal_size = '1GB';"}},
            {"api": "execute_sql", "args": {"sql_query": "ALTER SYSTEM SET checkpoint_completion_target = '0.9';"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT pg_reload_conf(); SELECT pg_sleep(1);"}},
        ],
    },
    {
        "thinking": "验证三项参数已生效并提交。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT current_setting('checkpoint_timeout'), "
                        "current_setting('max_wal_size'), "
                        "current_setting('checkpoint_completion_target');"
                    )
                },
            },
            {
                "api": "submit",
                "args": {
                    "report": PgSystemFailureIoCheckpointSpikesScenario().get_case('single_checkout_checkpoint_spike_simple').reference_report
                },
            },
        ],
    },
]


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "没有排查，直接提交。",
        "actions": [{"api": "submit", "args": {"report": EMPTY_REPORT}}],
    }
]


def _build_env(case, port: int, container_name: str, tool_profile: str = None) -> PGEnv:
    # 容器配额走 PGDockerDeployment.DEFAULT_RESOURCES（512MB/1CPU/256MB shm/8GB disk），
    # 更低的 256MB/0.5CPU 跑不动 HEAVY TPC-DS query，会被 runner 拖死。
    # 用 aiopsbench-pg-tpcds:latest 让 workload runner 真能跑 TPC-DS SELECT 产生 noise，
    # 否则所有 runner exec 都报 store_sales does not exist 全 fail_calls。
    resources = PGDockerDeployment.DEFAULT_RESOURCES.copy()
    workload = TPCDSWorkload(scale=case.dataset_scale)
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        resources=resources,
        image_name=case.base_image_name,
    )
    return PGEnv(
        workload=workload,
        deployment=deployment,
        port=port,
        sample_interval_sec=1,
        tool_profile=tool_profile or "general_knowledge",
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )


def _verify_fault(env, injector):
    print("\n[Setup] Verifying injected checkpoint I/O fault...")
    time.sleep(2)
    disk_io = env.query_metrics("disk_io")
    print(f"  - disk_io: {disk_io}")
    cfg_res = env.execute_sql(
        "SELECT name, setting, unit FROM pg_settings "
        "WHERE name IN ('checkpoint_timeout', 'max_wal_size', "
        "'checkpoint_completion_target') ORDER BY name;"
    )
    print(f"  - Checkpoint config: {cfg_res}")
    bgwriter_res = env.execute_sql(
        "SELECT checkpoints_timed, checkpoints_req, buffers_checkpoint, "
        "checkpoint_write_time, checkpoint_sync_time FROM pg_stat_bgwriter;"
    )
    print(f"  - pg_stat_bgwriter: {bgwriter_res}")
    print(
        "  - Injection bgwriter delta: "
        f"checkpoints_req_delta={getattr(injector, 'fault_checkpoint_req_delta', None)}"
    )


def run_with_orchestrator(
    env, scenario, case, agent, max_turns: int,
    run_config: OrchestratorRunConfig = None,
):
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        max_turns=max_turns,
        run_config=run_config,
    )
    result = orchestrator.run()
    return result, orchestrator.action_history





def print_evaluation_basis(label: str, result: dict):
    print(f"[Evaluation:{label}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")

def run_mock_full(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - IO Checkpoint Spikes Full-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureIoCheckpointSpikesScenario()
    case = scenario.get_case(case_id)
    env = _build_env(case, port, container_name)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(
        SIMPLE_FULL_SCORE_MOCK_RESPONSES
        if case.case_id == "single_checkout_checkpoint_spike_simple"
        else FULL_SCORE_MOCK_RESPONSES
    )
    result, _ = run_with_orchestrator(
        env, scenario, case, agent, max_turns=12, run_config=run_config
    )
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - IO Checkpoint Spikes Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureIoCheckpointSpikesScenario()
    case = scenario.get_case(case_id)
    env = _build_env(case, port, container_name)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses([
        {
            "thinking": "没有排查，直接提交。",
            "actions": [{
                "api": "submit",
                "args": {"report": EMPTY_REPORT},
            }],
        }
    ])
    result, _ = run_with_orchestrator(
        env, scenario, case, agent, max_turns=3, run_config=run_config
    )
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str,
    port: int,
    container_name: str = None,
    model: str = None,
    config_path: str = None,
    max_turns: int = 30,
    agent_name: str = "llm",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
    dbot_tool_profile: str = "general_knowledge",
    run_config: OrchestratorRunConfig = None,
    ) -> float:
    print("=" * 60)
    print(f"AiOpsBench PostgreSQL - IO Checkpoint Spikes {agent_name.upper()}Agent Path")
    print("=" * 60)

    max_turns = min(max_turns, 30)
    try:
        agent = build_agent(
            agent_name=agent_name,
            model=model,
            config_path=config_path or "config/llm_config.json",
            dbaiops_graph=dbaiops_graph,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"[{agent_name.upper()}AGENT_BLOCKED] {exc}")
        return 0.0

    tool_profile = dbot_tool_profile if agent_name == "dbot" else None

    scenario = PgSystemFailureIoCheckpointSpikesScenario()
    case = scenario.get_case(case_id)
    env = _build_env(case, port, container_name, tool_profile=tool_profile)
    result, action_history = run_with_orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=max_turns,
        run_config=run_config,
    )
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
                print(
                    f"[{agent_name.upper()}AGENT_BLOCKED] Agent reached max_turns without submit; "
                    "increase --max-turns up to 30 and record this run as a blocker only if submit is still missing."
                )
    print_evaluation_basis(agent_name, result)
    print(f"[Result] {agent_name.upper()}Agent passed={passed}")
    return passed


def build_agent(
    agent_name: str,
    model: str = None,
    config_path: str = "config/llm_config.json",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
):
    return build_experiment_agent(
        model=model,
        config_path=config_path,
        use_native_tools=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Run the PG I/O checkpoint spikes scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-pg-io-checkpoint-spikes")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--llm-config", default="config/llm_config.json",
                        dest="llm_config")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot.")
    scenario_definition = PgSystemFailureIoCheckpointSpikesScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )

    if args.max_turns > 30:
        raise ValueError("--max-turns must be <= 30")
    if args.mode in ("mock", "all"):
        run_mock_full(args.case, args.port, args.container_name, run_config)
    if args.mode in ("zero", "all"):
        run_mock_zero(args.case, args.port, f"{args.container_name}-zero", run_config)
    if args.mode in ("llm", "all"):
        run_llm(args.case,
            args.port,
            args.container_name,
            args.model,
            args.llm_config,
            args.max_turns,
            agent_name=args.agent,
            dbaiops_graph=args.dbaiops_graph,
            dbot_tool_profile=args.dbot_tool_profile,
            run_config=run_config,
        )


if __name__ == "__main__":
    main()
