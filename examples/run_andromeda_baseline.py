"""Run Andromeda baseline agent on a PG scenario."""

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.execution.environment import PGEnv
from src.scenarios.postgres import PgQueryPerfMissingIndexScenario
from src.workloads.tpcds import TPCDSWorkload
from src.agents.baselines import AndromedaAgent
from src.scenarios.runtime.orchestrator import Orchestrator


def main():
    print("=" * 60)
    print("Andromeda Baseline: PG Scenario")
    print("=" * 60)

    model = os.environ["ANDROMEDA_MODEL"]
    print(f"\nModel: {model}")

    workload = TPCDSWorkload(scale=1)
    env = PGEnv(workload=workload, port=15432)

    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")

    agent = AndromedaAgent(
        model=model,
        config_path="config/llm_config.json",
        use_native_tools=True,
    )

    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
    )
    orchestrator.run()


if __name__ == "__main__":
    main()
