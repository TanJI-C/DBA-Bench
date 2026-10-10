import argparse
import os
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.agent import MockLLMAgent
from src.scenarios.tidb import TidbDemoScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator


MOCK_RESPONSES = [
    {"thinking": "确认 TiDB 集群状态。", "action": {"api": "execute_sql", "args": {"sql_query": "SELECT TYPE, INSTANCE, VERSION, START_TIME, UPTIME FROM information_schema.cluster_info ORDER BY TYPE, INSTANCE"}}},
    {"thinking": "检查 TiDB 版本和 DDL 状态。", "actions": [
        {"api": "execute_sql", "args": {"sql_query": "SELECT VERSION()"}},
        {"api": "execute_sql", "args": {"sql_query": "ADMIN SHOW DDL JOBS 5"}},
    ]},
    {"thinking": "健康检查完成。", "action": {"api": "submit", "args": {
        "report": TidbDemoScenario().get_case('minimal_healthy').reference_report
    }}},
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="tidb-demo")
    parser.add_argument("--port-base", type=int, default=4000)
    args = parser.parse_args()

    print("=" * 60)
    print("AiOpsBench TiDB Docker Demo (PD + TiKV + TiDB containers)")
    print("=" * 60)
    started = time.time()
    env = TiDBEnv(run_id=args.run_id, port_base=args.port_base)
    print(f"\n[Timing] Setup objects: {time.time() - started:.2f}s")

    scenario = TidbDemoScenario()
    case = scenario.get_case("minimal_healthy")
    agent = MockLLMAgent(
        url="mock", api_key="mock", system_prompt="You are a TiDB DBA agent.", use_native_tools=False
    )
    agent.set_mock_responses(MOCK_RESPONSES)
    Orchestrator(env=env, scenario=scenario, case=case, agent=agent, max_turns=15).run()
    print(f"\n[Timing] Total demo time: {time.time() - started:.2f}s")


if __name__ == "__main__":
    main()
