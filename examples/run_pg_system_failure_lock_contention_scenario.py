import argparse
import json
import os
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.scenarios.postgres import PgSystemFailureLockContentionScenario
from src.execution.deployment import PGDockerDeployment
from src.execution.environment import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.workloads.tpcds import TPCDSWorkload


# 讲解主线：本入口脚本用一个 holder 和多个真实 waiter 连接制造锁等待队列；
# Agent 需要从 active_connections、pg_locks、pg_stat_activity 找到 blocker，
# 通过 pg_terminate_backend 释放锁，evaluator 再回环境确认等待链消失。
TARGET_TABLE = "customer"
MIN_EXPECTED_WAITERS = 5
MIN_EXPECTED_SLOW_NOISE = 12
# 这条 SQL 是 mock 满分路径和可观测性验收共用的“锁等待链查询”：
# blocked_lock.granted=false 是等待者，blocker_lock.granted=true 是持锁者。
LOCK_CHAIN_SQL = """
SELECT
    blocked.pid AS waiting_pid,
    blocked.application_name AS waiting_app,
    blocked.query AS waiting_query,
    blocker.pid AS blocking_pid,
    blocker.application_name AS blocking_app,
    blocker.state AS blocking_state,
    blocker.query AS blocking_query,
    waiting_lock.locktype,
    waiting_lock.mode,
    waiting_lock.relation::regclass AS locked_relation,
    blocked.wait_event_type,
    blocked.wait_event
FROM pg_stat_activity blocked
JOIN LATERAL unnest(pg_blocking_pids(blocked.pid)) AS blockers(blocking_pid) ON true
JOIN pg_stat_activity blocker ON blocker.pid = blockers.blocking_pid
LEFT JOIN pg_locks waiting_lock ON waiting_lock.pid = blocked.pid AND NOT waiting_lock.granted
WHERE blocked.wait_event_type = 'Lock'
  AND blocked.query ILIKE 'UPDATE customer%'
  AND blocker.state = 'idle in transaction';
"""
TERMINATE_HOLDER_SQL = """
WITH blocked AS (
    SELECT DISTINCT blocker.pid AS blocking_pid
    FROM pg_stat_activity waiting
    JOIN LATERAL unnest(pg_blocking_pids(waiting.pid)) AS blockers(blocking_pid) ON true
    JOIN pg_stat_activity blocker ON blocker.pid = blockers.blocking_pid
    WHERE waiting.wait_event_type = 'Lock'
      AND waiting.application_name LIKE 'checkout_api_wait_%'
      AND waiting.query ILIKE 'UPDATE customer%'
      AND blocker.state = 'idle in transaction'
)
SELECT pg_terminate_backend(blocking_pid)
FROM blocked
WHERE blocking_pid <> pg_backend_pid();
"""
# 复合锁队列的标准修复语句：终止"行 1 收结账 UPDATE 队列"中处于
# idle in transaction 的阻塞会话（不点名 application_name，不影响 row2/row3
# 健康链）。队列是多级的，第一轮只解除当前队列根；修复后必须复查——
# 队列会在下一个队列事务上重组，需要再次执行本语句直到队列为空。
QUEUE_BLOCKER_TERMINATE_SQL = """
WITH queue_waiters AS (
    SELECT pid FROM pg_stat_activity
    WHERE wait_event_type = 'Lock'
      AND application_name LIKE 'checkout_api%'
      AND query ILIKE 'UPDATE customer%'
),
queue_blockers AS (
    SELECT DISTINCT blocker.pid AS blocking_pid
    FROM queue_waiters waiting
    JOIN LATERAL unnest(pg_blocking_pids(waiting.pid)) AS blockers(blocking_pid) ON true
    JOIN pg_stat_activity blocker ON blocker.pid = blockers.blocking_pid
    WHERE blocker.state = 'idle in transaction'
)
SELECT pg_terminate_backend(blocking_pid)
FROM queue_blockers
WHERE blocking_pid <> pg_backend_pid();
"""
# 作业层：持锁的 review 会话是 fraud_review 作业的当前执行者，仅终止会话会被作业
# 重新拉起。标准修复必须先读作业控制面（表/列 COMMENT 与 CHECK 枚举是公开契约），
# 通过状态列暂停/取消复核任务，再分阶段清理剩余队列。
REVIEW_JOB_INSPECT_SQL = """
SELECT review_id, customer_sk, reason, status
FROM ops_fraud_review_queue
ORDER BY review_id;
"""
REVIEW_JOB_PAUSE_SQL = """
UPDATE ops_fraud_review_queue
SET status = 'cancelled', updated_at = now()
WHERE status = 'pending';
"""
WAITING_LOCK_SQL = """
SELECT a.pid, a.application_name, a.state, a.wait_event_type, a.wait_event, l.locktype, l.mode, l.granted
FROM pg_locks l
JOIN pg_stat_activity a ON a.pid = l.pid
WHERE a.application_name IN ('checkout_api_tx_17', 'nightly_reporting_snapshot')
   OR a.application_name LIKE 'checkout_api_wait_%'
   OR a.application_name IN ('nightly_reporting_wait_01', 'profile_read_tx_legacy', 'profile_read_wait_01')
ORDER BY a.application_name, l.granted;
"""
POST_FIX_WAITING_LOCK_SQL = "SELECT pg_sleep(1);\n" + WAITING_LOCK_SQL
WAITING_LOCK_COUNT_SQL = """
SELECT count(DISTINCT a.pid)
FROM pg_locks l
JOIN pg_stat_activity a ON a.pid = l.pid
WHERE a.application_name LIKE 'checkout_api_wait_%'
  AND a.wait_event_type = 'Lock'
  AND NOT l.granted;
"""
NOISE_CONTEXT_SQL = """
SELECT application_name, state, wait_event_type, left(query, 90) AS sample_query, count(*) AS sessions
FROM pg_stat_activity
WHERE application_name = 'nightly_reporting_snapshot'
   OR application_name IN (
      'profile_read_tx_legacy',
      'order_callback_audit_tx'
   )
   OR application_name LIKE 'dashboard_%'
   OR application_name LIKE 'etl_%'
   OR application_name LIKE 'prometheus_%'
   OR application_name IN ('nightly_reporting_wait_01', 'profile_read_wait_01')
   OR application_name LIKE 'checkout_api_pool_%'
   OR application_name LIKE 'profile_read_api_%'
GROUP BY application_name, state, wait_event_type, left(query, 90)
ORDER BY sessions DESC, application_name;
"""


FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "先查看活跃连接，确认是否存在等待写事务和异常会话堆积。",
        "action": {
            "api": "query_metrics",
            "args": {"metric_type": "active_connections", "target": None},
        },
    },
    {
        "thinking": "盘点正常连接池、读流量、报表和 exporter 噪声，避免把背景连接误当成主因。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": NOISE_CONTEXT_SQL},
        },
    },
    {
        "thinking": "关联 pg_locks、pg_stat_activity 与 pg_blocking_pids，构建锁等待链并区分 reporting 噪声。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": LOCK_CHAIN_SQL},
        },
    },
    {
        "thinking": "行 1 收结账队列是多级的：风控复核事务持有该行 FOR SHARE 是队列根，"
        "checkout 事务的 UPDATE 排在其后。先确认复核会话所属作业的控制面（任务队列与状态契约）。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": REVIEW_JOB_INSPECT_SQL},
        },
    },
    {
        "thinking": "仅终止 review 会话会被 fraud_review 作业按控制面 pending 任务重新拉起，"
        "必须先从作业层取消复核任务（状态列 CHECK 枚举公开合法值），再清理队列。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": REVIEW_JOB_PAUSE_SQL},
        },
    },
    {
        "thinking": "作业已取消，终止当前队列根（idle in transaction 的阻塞者）。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": QUEUE_BLOCKER_TERMINATE_SQL},
        },
    },
    {
        "thinking": "修复会改变队列形态，等待队列重组稳定后重新观察：确认队列是否真正排空。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": "SELECT pg_sleep(1.5);\n" + LOCK_CHAIN_SQL},
        },
    },
    {
        "thinking": "队列在 checkout 事务上重组（它获得行锁后仍未提交），继续终止该队列阻塞者。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": "SELECT pg_sleep(2);\n" + QUEUE_BLOCKER_TERMINATE_SQL},
        },
    },
    {
        "thinking": "复查目标写操作和锁等待是否恢复。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": POST_FIX_WAITING_LOCK_SQL},
        },
    },
    {
        "thinking": "锁等待已解除，再次查看 topsql 确认 fingerprint 不再 hang，提交结果。",
        "actions": [
            {"api": "query_metrics", "args": {"metric_type": "topsql", "limit": 20}},
            {"api": "submit", "args": {"report": PgSystemFailureLockContentionScenario().get_case('customer_row_lock_queue').reference_report}},
        ],
    },
]

ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "不做诊断和修复，直接提交。",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]

SIMPLE_FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": (
            "查询锁等待链，比较受影响 profile 写队列与同时存在的 reporting 锁，"
            "定位真正阻塞最多目标写入的未提交事务。"
        ),
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": LOCK_CHAIN_SQL},
        },
    },
    {
        "thinking": "只终止目标 profile 写队列推导出的主 blocker，保留 reporting 事务。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": TERMINATE_HOLDER_SQL},
        },
    },
    {
        "thinking": "复查目标 customer 行的等待队列已经清空，且非因果 reporting 链仍可区分。",
        "action": {
            "api": "execute_sql",
            "args": {"sql_query": POST_FIX_WAITING_LOCK_SQL},
        },
    },
    {
        "thinking": "目标 profile 写入恢复，提交结构化诊断、定向修复和验证证据。",
        "action": {
            "api": "submit",
            "args": {
                "report": PgSystemFailureLockContentionScenario().get_case('customer_profile_lock_queue_simple').reference_report
            },
        },
    },
]


def full_score_mock_responses(case_id: str):
    if case_id == "customer_profile_lock_queue_simple":
        return SIMPLE_FULL_SCORE_MOCK_RESPONSES
    return FULL_SCORE_MOCK_RESPONSES


def zero_score_mock_responses(case_id: str):
    return [
        {
            "thinking": "不做诊断和修复，直接提交。",
            "action": {
                "api": "submit",
                "args": {
                    "report": EMPTY_REPORT,
                },
            },
        }
    ]


def build_env(case, port: int, container_name: str, image_name: str = None, tool_profile: str = None,
              cold_start_timeout: int = 600) -> PGEnv:
    # 使用 TPC-DS customer 表作为热点写入对象；锁机制本身与具体业务表无关。
    workload = TPCDSWorkload(scale=case.dataset_scale)
    deployment = PGDockerDeployment(
        container_name=container_name,
        resources={
            "cpus": 0.5,
            "memory_mb": 512,
            "shm_size": "128m",
            "disk_quota_mb": workload.disk_quota_mb,
        },
        postgres_user="postgres",
        postgres_password="password",
        postgres_db="testdb",
        port=port,
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=workload.data_dir,
        image_name=image_name or case.base_image_name,
        initialization_timeout_seconds=cold_start_timeout,
    )
    env_kwargs = {
        "workload": workload,
        "deployment": deployment,
        "port": port,
        "allow_sampler_reconnect": True,
    }
    if tool_profile:
        env_kwargs["tool_profile"] = tool_profile
    return PGEnv(**env_kwargs)










def _assert_lock_contention_observable(raw_connections: str, raw_locks: str, raw_waiter_count: str):
    connections_text = raw_connections.lower()
    locks = json.loads(raw_locks)
    locks_text = json.dumps(locks.get("result", []), ensure_ascii=False, default=str).lower()
    waiter_count = json.loads(raw_waiter_count).get("result", [[0]])[0][0]
    if "idle in transaction" not in connections_text:
        raise AssertionError(f"holder state was not visible in active_connections: {raw_connections}")
    if "lock_waiting_sessions" not in connections_text:
        raise AssertionError(f"lock waiting session count was not visible in active_connections: {raw_connections}")
    if "checkout_api_tx_17" not in locks_text:
        raise AssertionError(f"holder session was not visible in pg_locks join: {raw_locks}")
    if "checkout_api_wait_" not in locks_text:
        raise AssertionError(f"waiter sessions were not visible in pg_locks join: {raw_locks}")
    for expected in ("nightly_reporting_wait_01", "profile_read_wait_01"):
        if expected not in locks_text:
            raise AssertionError(f"decoy lock waiter {expected} was not visible in pg_locks join: {raw_locks}")
    if "false" not in locks_text and "f" not in locks_text:
        raise AssertionError(f"waiting lock was not visible in pg_locks: {raw_locks}")
    if int(waiter_count or 0) < MIN_EXPECTED_WAITERS:
        raise AssertionError(f"expected at least {MIN_EXPECTED_WAITERS} waiting sessions, got {raw_waiter_count}")


def _assert_noise_floor_observable(raw_noise_context: str):
    rows = json.loads(raw_noise_context).get("result", [])
    text = json.dumps(rows, ensure_ascii=False, default=str).lower()
    for expected in (
        "checkout_api_pool_",
        "profile_read_api_",
        "nightly_reporting_snapshot",
        "nightly_reporting_wait_01",
        "profile_read_tx_legacy",
        "profile_read_wait_01",
        "dashboard_profile_rollup",
    ):
        if expected not in text:
            raise AssertionError(f"expected noise session {expected} was not visible: {raw_noise_context}")


def _wait_for_slow_query_noise(env: PGEnv) -> str:
    deadline = time.monotonic() + 8
    raw = ""
    while time.monotonic() < deadline:
        raw = env.query_metrics("slow_queries", threshold_ms=1000, limit=20)
        rows = json.loads(raw).get("records", [])
        background_count = sum(
            1 for row in rows
            if "store_sales ss" in json.dumps(row, ensure_ascii=False).lower()
            and "date_dim d" in json.dumps(row, ensure_ascii=False).lower()
        )
        if background_count >= MIN_EXPECTED_SLOW_NOISE:
            return raw
        time.sleep(0.5)
    raise AssertionError(f"expected at least {MIN_EXPECTED_SLOW_NOISE} background slow queries: {raw}")








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
    return result, orchestrator.action_history


def print_evaluation_basis(label: str, result: dict):
    print(f"[Evaluation:{label}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")

def run_mock_full(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None,
                  cold_start_timeout: int = 600) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Lock Contention Full-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureLockContentionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None, cold_start_timeout=cold_start_timeout)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(full_score_mock_responses(case_id))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=12)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None,
                  cold_start_timeout: int = 600) -> float:
    print("=" * 60)
    print("AiOpsBench PostgreSQL - Lock Contention Zero-Score Mock Path")
    print("=" * 60)

    scenario = PgSystemFailureLockContentionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None, cold_start_timeout=cold_start_timeout)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(zero_score_mock_responses(case_id))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str, port: int, container_name: str, model: str = None, config_path: str = "config/llm_config.json", max_turns: int = 20, run_config: OrchestratorRunConfig = None,
            agent_name: str = "llm", dbaiops_graph: str = "data/knowledge_graph/pg_experience_graph.json",
            dbot_tool_profile: str = "general_knowledge", cold_start_timeout: int = 600,
            max_output_tokens: int = None) -> float:
    print("=" * 60)
    print(f"AiOpsBench PostgreSQL - Lock Contention {agent_name.upper()}Agent Path")
    print("=" * 60)

    max_turns = min(max_turns, 30)
    try:
        agent = build_agent(
            agent_name=agent_name,
            model=model,
            config_path=config_path,
            dbaiops_graph=dbaiops_graph,
            max_output_tokens=max_output_tokens,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"[{agent_name.upper()}AGENT_BLOCKED] {exc}")
        return 0.0

    tool_profile = dbot_tool_profile if agent_name == "dbot" else None

    scenario = PgSystemFailureLockContentionScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case,
        port,
        container_name,
        image_name=None,
        tool_profile=tool_profile,
        cold_start_timeout=cold_start_timeout,
    )
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis(agent_name, result)
    if not any(action.get("api") == "submit" for action in action_history):
                print(f"[{agent_name.upper()}AGENT_BLOCKED] Agent did not submit before max_turns.")
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
    parser = argparse.ArgumentParser(description="Run pg_system_failure_lock_contention scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--agent", choices=["llm", "dbot", "dbaiops"], default="llm",
                        help="Which agent drives the --mode llm path. Default: llm.")
    parser.add_argument("--port", type=int, default=15446)
    parser.add_argument("--container-name", default="aiopsbench-pg-queryperf-03")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--llm-config", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--dbaiops-graph", default="data/knowledge_graph/pg_experience_graph.json",
                        help="Knowledge graph path used by --agent dbaiops.")
    parser.add_argument("--dbot-tool-profile", default="general_knowledge",
                        help="PGEnv tool_profile forwarded to --agent dbot. Default: general_knowledge.")
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--cold-start-timeout", type=int, default=600,
                        help="PostgreSQL initialization timeout in seconds.")
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--fault-snapshot-name")
    scenario_definition = PgSystemFailureLockContentionScenario()
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
        run_mock_full(args.case, args.port, args.container_name, run_config,
                      cold_start_timeout=args.cold_start_timeout)
    if args.mode in ("zero", "all"):
        run_mock_zero(args.case, args.port, args.container_name, run_config,
                      cold_start_timeout=args.cold_start_timeout)
    if args.mode in ("llm", "all"):
        run_llm(args.case,
            args.port,
            args.container_name,
            model=args.model,
            config_path=args.llm_config,
            max_turns=args.max_turns,
            run_config=run_config,
            agent_name=args.agent,
            dbaiops_graph=args.dbaiops_graph,
            dbot_tool_profile=args.dbot_tool_profile,
            cold_start_timeout=args.cold_start_timeout,
            max_output_tokens=args.max_output_tokens,
        )


if __name__ == "__main__":
    main()
