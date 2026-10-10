import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.execution.environment import PGEnv
from src.scenarios.postgres import DemoScenario
from src.workloads.postgres import DemoWorkload
from src.agents.agent import MockLLMAgent
from src.scenarios.runtime.orchestrator import Orchestrator


def main():
    print("="*60)
    print("AiOpsBench MockLLMAgent Demo")
    print("="*60)

    workload = DemoWorkload()

    env = PGEnv(workload=workload, port=15432)

    scenario = DemoScenario()
    case = scenario.get_case("minimal_healthy")


    agent = MockLLMAgent(
        url="http://localhost:8000",
        api_key="mock-key",
        system_prompt="Mock system prompt; Orchestrator injects the Env prompt before run.",
        enable_log=True
    )

    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent
    )

    orchestrator.run()

    print("\n" + "="*60)
    print("MockLLMAgent 对话历史:")
    print("="*60)
    agent.print_history()


if __name__ == "__main__":
    main()
