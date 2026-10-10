"""Run DBAIOps baseline agent on PG missing index scenario."""

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.execution.environment import PGEnv
from src.scenarios.postgres import PgQueryPerfMissingIndexScenario
from src.workloads.tpcds import TPCDSWorkload
from src.agents.baselines import DbaiopsAgent
from src.scenarios.runtime.orchestrator import Orchestrator


def main():
    print("=" * 60)
    print("DBAIOps Baseline: PG Missing Index Scenario")
    print("=" * 60)

    model = os.environ.get("DBAIOPS_MODEL")
    if not model:
        raise SystemExit("DBAIOPS_MODEL environment variable is required")
    graph_path = os.environ.get(
        "DBAIOPS_GRAPH",
        "data/knowledge_graph/pg_experience_graph.json",
    )
    print(f"\nModel: {model} | Graph: {graph_path}")

    workload = TPCDSWorkload(scale=1)
    env = PGEnv(workload=workload, port=15432)
    env.deploy()

    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")

    agent = DbaiopsAgent(
        model=model,
        graph_path=graph_path,
        config_path="config/llm_config.json",
        adf_theta=10.0,
        adf_score_threshold=1.2,
        max_evolution_depth=4,
    )

    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
    )
    orchestrator.run()
