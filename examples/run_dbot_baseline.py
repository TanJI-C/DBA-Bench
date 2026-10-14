"""Run D-Bot baseline agent on PG missing index scenario."""

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.execution.environments.postgres import PGEnv
from src.scenarios.postgres import PgQueryPerfMissingIndexScenario
from src.workloads.tpcds import TPCDSWorkload
from src.agents.baselines import DbotAgent
from src.scenarios.runtime.orchestrator import Orchestrator


def main():
    print("=" * 60)
    print("D-Bot Baseline: PG Missing Index Scenario")
    print("=" * 60)

    mode = os.environ.get("DBOT_MODE", "dbot_code")
    model = os.environ["DBOT_MODEL"]
    tool_profile = os.environ.get("DBOT_TOOL_PROFILE", "db_gpt")
    use_native_tools = os.environ.get("DBOT_NATIVE_TOOLS", "0") == "1"
    print(f"\nMode: {mode} | Model: {model} | PGEnv tool_profile: {tool_profile}")

    workload = TPCDSWorkload(scale=1)
    env = PGEnv(workload=workload, port=15432, tool_profile=tool_profile)

    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")

    agent = DbotAgent(
        mode=mode,
        model=model,
        config_path="config/llm_config.json",
        use_native_tools=use_native_tools,
    )

    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        max_turns=40,
    )
    orchestrator.run()


if __name__ == "__main__":
    main()
