import argparse
import os

from src.agents.baselines.dbot import DbotAgent
from src.scenarios.postgres import PgQueryPerfMissingIndexScenario
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator
from src.workloads.tpcds import TPCDSXWorkload


def main():
    scenario = PgQueryPerfMissingIndexScenario()
    parser = argparse.ArgumentParser(description="Run D-Bot against a missing-index Case.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--max-turns", type=int, default=40)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = PGEnv(
        workload=TPCDSXWorkload(scale=case.dataset_scale),
        port=args.port,
        tool_profile=os.environ.get("DBOT_TOOL_PROFILE", "db_gpt"),
    )
    agent = DbotAgent(
        mode="dbot_code",
        model=args.model,
        use_native_tools=os.environ.get("DBOT_NATIVE_TOOLS", "0") == "1",
    )
    Orchestrator(env, scenario, case, agent, max_turns=args.max_turns).run()


if __name__ == "__main__":
    main()
