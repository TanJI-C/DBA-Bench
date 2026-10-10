import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.execution.environment import PGEnv
from src.scenarios.postgres import DemoScenario
from src.workloads.postgres import DemoWorkload
from src.agents.agent import HumanAgent
from src.scenarios.runtime.orchestrator import Orchestrator

def main():
    print("="*60)
    print("AiOpsBench Minimal Demo")
    print("="*60)

    # 1. Workload：提供数据（带缓存能力）
    workload = DemoWorkload()

    # 2. Env：运行中的 PG 容器，持有 Workload 的引用
    env = PGEnv(workload=workload, port=15432)

    # 3. Scenario：描述故障注入计划（DemoScenario 用的是 NoopFaultInjector）
    scenario = DemoScenario()
    case = scenario.get_case("minimal_healthy")

    # 4. Evaluator：评估结果

    # 5. HumanAgent：解析人类输入为 JSON action（不持有 Orchestrator）
    agent = HumanAgent()

    # 6. Orchestrator：主导整个生命周期，持有所有组件引用
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent
    )

    # 7. 由 Orchestrator 主导运行
    orchestrator.run()

if __name__ == "__main__":
    main()
