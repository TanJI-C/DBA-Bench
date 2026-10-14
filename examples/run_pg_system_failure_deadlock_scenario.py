import argparse
import json
import os
import signal
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.runtime.config import required_run_timeout_seconds
from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgSystemFailureDeadlockScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload


ACTIVITY_SQL = """
SELECT pid, application_name, state, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE datname = current_database()
ORDER BY pid;
"""

CHECKOUT_FUNCTION_SQL = """
SELECT pg_get_functiondef('process_checkout_job(integer)'::regprocedure) AS function_def;
"""

CHECKOUT_JOB_STEPS_SQL = """
SELECT job_id, priority_rank, order_id, source
FROM checkout_job_steps
ORDER BY job_id, priority_rank;
"""

CHECKOUT_PLAN_VIEW_SQL = """
SELECT pg_get_viewdef('checkout_job_plan'::regclass, true) AS plan_view_def;
"""

CHECKOUT_PLAN_SOURCE_SQL = """
SELECT job_id, upstream_priority, order_id, plan_version, last_synced_at
FROM checkout_plan_source
ORDER BY job_id, upstream_priority;
"""

CHECKOUT_SYNC_DEF_SQL = """
SELECT pg_get_functiondef('checkout_plan_sync()'::regprocedure) AS sync_def;
"""

RETURNS_PLAN_SOURCE_SQL = """
SELECT job_id, upstream_priority, order_id, plan_version, last_synced_at
FROM returns_plan_source
ORDER BY job_id, upstream_priority;
"""

PLAN_SYNC_REGISTRY_SQL = """
SELECT job_name, target_function, schedule_interval_seconds, status, template_revision, last_redeployed_at
FROM plan_sync_job_registry
ORDER BY job_name;
"""

REPORTING_NOISE_SQL = """
SELECT query, calls, total_exec_time, mean_exec_time, rows
FROM pg_stat_statements
WHERE query ILIKE '%refresh_dashboard_tile%'
   OR query ILIKE '%inventory_rollup_refresh%'
   OR query ILIKE '%process_checkout_job%'
ORDER BY total_exec_time DESC
LIMIT 20;
"""


def _canonical_reorder_sql(case):
    # Reference 修复（复合修复的下游组成）。
    # 两段式 UPDATE 避开 (job_id, priority_rank) 主键的中间态冲突。
    order_a, order_b = sorted(case.order_ids)
    job_ids = ", ".join(str(value) for value in case.job_ids)
    return (
        f"UPDATE {case.job_step_table} SET priority_rank = -priority_rank "
        f"WHERE job_id IN ({job_ids});"
        f"UPDATE {case.job_step_table} SET priority_rank = "
        f"CASE WHEN order_id = {order_a} THEN 10 ELSE 20 END "
        f"WHERE job_id IN ({job_ids}) AND priority_rank < 0;"
    )


def _composite_fix_sql(case):
    # Reference 复合修复：先改正上游计划源的排序（反序的真正所有权层），
    # 再执行一次 checkout_plan_sync() 发布计划包（重灌 steps + 重部署例程）。
    # 只改函数或只改 steps 会被下一个同步周期还原；只改 source 不发布则当下仍死锁。
    order_a, order_b = sorted(case.order_ids)
    job_ids = ", ".join(str(value) for value in case.job_ids)
    return (
        f"UPDATE {case.plan_source_table} SET upstream_priority = -upstream_priority "
        f"WHERE job_id IN ({job_ids});"
        f"UPDATE {case.plan_source_table} SET upstream_priority = "
        f"CASE WHEN order_id = {order_a} THEN 10 ELSE 20 END "
        f"WHERE job_id IN ({job_ids}) AND upstream_priority < 0;"
        f"SELECT {case.plan_sync_function}();"
    )


def _registry_composite_fix_sql(case):
    # Reference 控制面复合修复（仅 checkout）：sync 例程本体由
    # plan_sync_job_registry 模板周期重部署——先在控制面暂停调度作业，再改正上游
    # 计划源并执行一次同步发布。只替换/删除 sync 例程会被调度层重装还原。
    order_a, order_b = sorted(case.order_ids)
    job_ids = ", ".join(str(value) for value in case.job_ids)
    return (
        f"UPDATE {case.plan_sync_registry_table} SET status = 'paused' "
        f"WHERE target_function = '{case.plan_sync_function}';"
        f"UPDATE {case.plan_source_table} SET upstream_priority = -upstream_priority "
        f"WHERE job_id IN ({job_ids});"
        f"UPDATE {case.plan_source_table} SET upstream_priority = "
        f"CASE WHEN order_id = {order_a} THEN 10 ELSE 20 END "
        f"WHERE job_id IN ({job_ids}) AND upstream_priority < 0;"
        f"SELECT {case.plan_sync_function}();"
    )


FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": (
            "Step 1: 看 PG 整体活动（active sessions + wait_event）。"
            "关注客户侧 500 时间窗内是否仍有 Lock 等待、归档/维护会话是否只是低速率背景。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": ACTIVITY_SQL}},
    },
    {
        "thinking": (
            "Step 2: 会话快照只能看到瞬时状态，用 read_log 未过滤读取 PostgreSQL 日志，"
            "找 checkout 500 时间窗内数据库侧真实报错与等待链。"
        ),
        "action": {"api": "read_log", "args": {"log_type": "pg_log", "lines": 200}},
    },
    {
        "thinking": (
            "Step 3: 日志里有 'deadlock detected'、Process A -> Process B -> Process A 等待链、"
            "但当前 statement 只是 process_checkout_job，需要查函数体确认真实 UPDATE 来源。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": CHECKOUT_FUNCTION_SQL}},
    },
    {
        "thinking": (
            "Step 3b: 函数体按 checkout_job_plan.plan_rank 排序——这是 planner 视图，"
            "先看视图定义确认 plan_rank 的真实来源，再查底层数据。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": CHECKOUT_PLAN_VIEW_SQL}},
    },
    {
        "thinking": (
            "Step 4: 视图是 pass-through，排序实际来自 checkout_job_steps.priority_rank；"
            "查底层数据确认业务优先级顺序是否等于 canonical lock order。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": CHECKOUT_JOB_STEPS_SQL}},
    },
    {
        "thinking": (
            "Step 5: job 101 是 1001->1002，job 102 是 1002->1001，"
            "说明 checkout planner 的 priority_rank 不是稳定锁顺序。"
            "再查 pg_stat_statements 区分 reporting timeout 是否只是背景噪声。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": REPORTING_NOISE_SQL}},
    },
    {
        "thinking": (
            "Step 6: 反序数据需要确认所有权：日志里有 checkout_plan_sync 的同步行，"
            "steps.source 也是 plan_sync 前缀——查上游计划源表与同步例程定义，"
            "确认反序由上游 source 周期回写。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": CHECKOUT_PLAN_SOURCE_SQL}},
    },
    {
        "thinking": (
            "Step 6b: 读同步例程定义：它从 checkout_plan_source 重灌 steps 并重部署"
            "计划包例程。只改函数或只改 steps 都会被下一个同步周期还原。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": CHECKOUT_SYNC_DEF_SQL}},
    },
    {
        "thinking": (
            "Step 6c: 同步例程一并发布 returns 计划线——库里有两个同构计划源，"
            "必须确认事故实体唯一属于 checkout 计划源：returns_plan_source 全升序、"
            "returns job 从不出现在 deadlock ERROR 里，是健康近邻，本次修复不能碰它。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": RETURNS_PLAN_SOURCE_SQL}},
    },
    {
        "thinking": (
            "Step 6d: 重部署证据行显示 sync 例程本体由调度层从 plan_sync_job_registry "
            "模板周期重装——直接替换/删除例程都会被下一个调度 tick 还原。读控制面"
            "确认作业状态与 revision 推进（h5：复发驱动的所有权层）。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": PLAN_SYNC_REGISTRY_SQL}},
    },
    {
        "thinking": (
            "Step 7: 落地控制面复合修复：先暂停调度作业（status='paused'，合法枚举值），"
            "再把上游计划源的顺序改正为 order_id 升序并执行一次同步发布计划包；"
            "这样跨同步周期也不会复发。"
        ),
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": _registry_composite_fix_sql(
                PgSystemFailureDeadlockScenario().get_case('checkout_order_deadlock')
            )},
        },
    },
    {
        "thinking": (
            "Step 8: 修复后再看一次 pg_stat_activity，确认 deadlock 已解除、"
            "没有 waiting on Lock 的事务、active sessions 恢复正常。"
        ),
        "action": {"api": "execute_sql", "args": {"sql_query": ACTIVITY_SQL}},
    },
    {
        "thinking": (
            "Step 9: 死锁链提取完整且控制面复合修复已落地，提交业务修复报告。"
        ),
        "actions": [
            {
                "api": "submit",
                "args": {"report": PgSystemFailureDeadlockScenario().get_case('checkout_order_deadlock').reference_report},
            },
        ],
    },
]


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Submit without inspecting activity or PostgreSQL logs.",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def _simple_mock_responses(case):
    job_steps_sql = (
        f"SELECT job_id, priority_rank, order_id, source FROM {case.job_step_table} "
        "ORDER BY job_id, priority_rank;"
    )
    plan_source_sql = (
        f"SELECT job_id, upstream_priority, order_id, plan_version, last_synced_at "
        f"FROM {case.plan_source_table} ORDER BY job_id, upstream_priority;"
    )
    sync_def_sql = (
        f"SELECT pg_get_functiondef('{case.plan_sync_function}()'::regprocedure) AS sync_def;"
    )
    return [
        {
            "thinking": (
                "先看 PG 整体活动（active sessions + wait_event），再读日志确认"
                "客户侧批处理 500 对应的数据库侧真实报错，而不是只凭会话快照下结论。"
            ),
            "action": {"api": "execute_sql", "args": {"sql_query": ACTIVITY_SQL}},
        },
        {
            "thinking": (
                "会话快照只能看到瞬时状态；用 read_log 未过滤读取 PostgreSQL 日志，"
                "找批处理 500 时间窗内数据库侧真实报错与等待链。"
            ),
            "action": {"api": "read_log", "args": {"log_type": "pg_log", "lines": 200}},
        },
        {
            "thinking": (
                "日志指向 process_checkout_job，但函数名不等于根因；读取函数体确认实际锁定的表和顺序来源。"
            ),
            "action": {"api": "execute_sql", "args": {"sql_query": CHECKOUT_FUNCTION_SQL}},
        },
        {
            "thinking": (
                f"函数按 {case.job_plan_view}.plan_rank 排序——planner 视图；先看视图定义确认 plan_rank 来源。"
            ),
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": (
                    f"SELECT pg_get_viewdef('{case.job_plan_view}'::regclass, true) AS plan_view_def;"
                )},
            },
        },
        {
            "thinking": (
                "视图 pass-through，排序来自底层步骤表；读取两个 job 的 priority_rank，"
                "验证同一订单对是否以相反顺序加锁。"
            ),
            "action": {"api": "execute_sql", "args": {"sql_query": job_steps_sql}},
        },
        {
            "thinking": (
                "死锁环、冲突语句和非规范顺序证据已闭合；但 steps.source 是 plan_sync 前缀、"
                "日志里也有 checkout_plan_sync 行——反序可能由上游计划源周期回写，"
                "查 source 表确认所有权。"
            ),
            "action": {"api": "execute_sql", "args": {"sql_query": plan_source_sql}},
        },
        {
            "thinking": (
                "读同步例程定义确认它重灌 steps 并重部署计划包例程；"
                "只改函数或只改 steps 都会在下一个同步周期还原。"
            ),
            "action": {"api": "execute_sql", "args": {"sql_query": sync_def_sql}},
        },
        {
            "thinking": (
                "落地复合修复：上游计划源顺序改正为 order_id 升序并执行一次同步发布；"
                "跨同步周期不再复发，只 kill 会话无法达到该效果。"
            ),
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": _composite_fix_sql(case)},
            },
        },
        {
            "thinking": (
                "复合修复已落地，提交统一加锁顺序、上游源修正与同步发布方案。"
            ),
            "action": {
                "api": "submit",
                "args": {
                    "report": case.reference_report,
                },
            },
        },
    ]


def _zero_mock_responses(case):
    return [{
        "thinking": "Submit without inspecting PostgreSQL logs or the batch ordering.",
        "action": {
            "api": "submit",
            "args": {"report": EMPTY_REPORT},
        },
    }]


HARD_TIMEOUT_SEC = 420


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str, tool_profile: str = None) -> PGEnv:
    # 用 aiopsbench-pg-tpcds:latest 作 base image（已含 TPC-DS schema + data），
    # workload runner 才能跑 TPC-DS 业务 SQL 产生真实 noise。DemoWorkload 只准备
    # 一个空 schema，runner exec 全部 store_sales does not exist fail。
    workload = TPCDSWorkload(scale=case.dataset_scale)
    resources = PGDockerDeployment.DEFAULT_RESOURCES.copy()
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        resources=resources,
        image_name=image_name or case.base_image_name,
    )
    return PGEnv(
        workload=workload,
        deployment=deployment,
        port=port,
        tool_profile=tool_profile or "general_knowledge",
    )


def _json_result(raw):
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return {"status": "error", "raw": raw}











def run_with_orchestrator(
    env, scenario, case, agent, run_config, max_turns: int,
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
    return result, orchestrator.action_history, orchestrator.turn_history



def run_mock_full(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Deadlock Full-Score Mock Path")
    print("=" * 70)

    scenario = PgSystemFailureDeadlockScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(
        _simple_mock_responses(case)
        if case.case_id == "single_order_pair_deadlock_simple"
        else FULL_SCORE_MOCK_RESPONSES
    )
    # checkout mock 路径覆盖 returns_plan_source 排除跳、plan_sync_job_registry
    # 控制面跳（h5）与控制面复合修复；simple 以开场 activity 跳开始。
    result, _, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=15)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Deadlock Zero-Score Mock Path")
    print("=" * 70)

    scenario = PgSystemFailureDeadlockScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(
        _zero_mock_responses(case)
        if case.case_id == "single_order_pair_deadlock_simple"
        else ZERO_SCORE_MOCK_RESPONSES
    )
    result, _, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
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
    max_output_tokens: int = None,
    ) -> float:
    print("=" * 70)
    print(f"AiOpsBench PostgreSQL - Deadlock {agent_name.upper()}Agent Path")
    print("=" * 70)

    max_turns = min(max_turns, 30)
    try:
        agent = build_agent(
            agent_name=agent_name,
            model=model,
            config_path=config_path or "config/llm_config.json",
            dbaiops_graph=dbaiops_graph,
            max_output_tokens=max_output_tokens,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"[{agent_name.upper()}AGENT_BLOCKED] {exc}")
        return 0.0

    tool_profile = dbot_tool_profile if agent_name == "dbot" else None

    scenario = PgSystemFailureDeadlockScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(
        case,
        port,
        container_name,
        None,
        tool_profile=tool_profile,
    )
    result, action_history, turn_history = run_with_orchestrator(
        env, scenario, case, agent, run_config, max_turns=max_turns
    )
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
                print(
                    f"[{agent_name.upper()}AGENT_BLOCKED] Agent reached max_turns without submit; "
                    "inspect the printed turn trace before changing scenario code."
                )
    print(f"[Trace] turns={len(turn_history)}, actions={len(action_history)}")
    print(f"[Result] {agent_name.upper()}Agent passed={passed}")
    return passed


def build_agent(
    agent_name: str,
    model: str = None,
    config_path: str = "config/llm_config.json",
    dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
    max_output_tokens: int = None,
):
    return build_experiment_agent(
        model=model,
        config_path=config_path,
        use_native_tools=True,
        max_output_tokens=max_output_tokens,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-pg-system-failure-deadlock")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config", default="config/llm_config.json",
                        dest="config", help="LLM config JSON path.")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot.")
    parser.add_argument("--max-output-tokens", type=int, default=None,
                        help="LLM max output tokens forwarded to the llm agent.")
    scenario_definition = PgSystemFailureDeadlockScenario()
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

    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(required_run_timeout_seconds())

    try:
        if args.mode in ("mock", "all"):
            run_mock_full(args.case, args.port, args.container_name, run_config)
        if args.mode in ("zero", "all"):
            run_mock_zero(args.case, args.port, f"{args.container_name}-zero", run_config)
        if args.mode in ("llm", "all"):
            run_llm(args.case,
                args.port,
                args.container_name,
                model=args.model,
                config_path=args.config,
                max_turns=args.max_turns,
                agent_name=args.agent,
                dbaiops_graph=args.dbaiops_graph,
                dbot_tool_profile=args.dbot_tool_profile,
                run_config=run_config,
                max_output_tokens=args.max_output_tokens,
            )
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
