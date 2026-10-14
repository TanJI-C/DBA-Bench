"""Run Panda baseline agent on PG missing index scenario."""

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.execution.environments.postgres import PGEnv
from src.scenarios.postgres import PgQueryPerfMissingIndexScenario
from src.workloads.tpcds import TPCDSWorkload
from src.agents.baselines import PandaAgent
from src.scenarios.runtime.orchestrator import Orchestrator


def main():
    print("=" * 60)
    print("Panda Baseline: PG Missing Index Scenario")
    print("=" * 60)

    mode = os.environ.get("PANDA_MODE", "panda_full")
    model = os.environ["PANDA_MODEL"]
    print(f"\nMode: {mode} | Model: {model}")

    workload = TPCDSWorkload(scale=1)
    env = PGEnv(workload=workload, port=15432)
    env.deploy()

    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")

    agent = PandaAgent(
        mode=mode,
        model=model,
        config_path="config/llm_config.json",
        use_native_tools=True,
        max_verification_retries=3,
        max_initial_metrics=5,
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
