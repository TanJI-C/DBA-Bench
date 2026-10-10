import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.tidb import TidbQueryPerfIndexMergeSelectionFailureScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


PASS_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "root_cause",
                "factor": (
                    "the OR predicate on test.qp03_admission_events falls back to TableFullScan because the "
                    "current TiDB session has tidb_enable_index_merge disabled while the global setting is ON, "
                    "despite usable index branches for the time-bounded event search"
                ),
                "entity": "test.qp03_admission_events",
                "evidence": ["EXPLAIN showed TableFullScan, SHOW VARIABLES reported OFF, and SHOW GLOBAL VARIABLES reported ON"],
            },
            {
                "type": "necessary_exclusion",
                "factor": (
                    "the leading tenant_id branch of idx_tenant_time and the event_type branch of idx_type "
                    "are the two existing index paths needed to union the time-bounded OR branches with IndexMerge"
                ),
                "entity": "test.qp03_admission_events",
                "evidence": ["SHOW INDEX confirmed both branch indexes exist"],
            },
        ]
    },
    "outcome": {
        "changes": ["enabled Index Merge for the agent session"],
        "verification": ["verified the IndexMerge plan, 450 result rows, unchanged indexes, and full-table truth"],
    },
    "summary": "The session optimizer setting caused the OR query full scan; the repaired plan preserves all business data.",
}
StructuredReport.from_mapping(PASS_REPORT)


MOCK_SCENARIO = TidbQueryPerfIndexMergeSelectionFailureScenario()
MOCK_CASE = MOCK_SCENARIO.get_case("dual_single_column_index_or_predicate")


FULL_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Select the exact target fingerprint from workload activity before inspecting its plan.",
        "actions": [
            {
                "api": "query_metrics",
                "args": {"metric_type": "active_connections", "target": None},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": f"EXPLAIN {MOCK_CASE.fault_fingerprint_sql}"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW VARIABLES LIKE 'tidb_enable_index_merge'"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW GLOBAL VARIABLES LIKE 'tidb_enable_index_merge'"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW INDEX FROM test.qp03_admission_events"},
            },
        ],
    },
    {
        "thinking": "Both columns have selective indexes, so enable Index Merge only for this diagnosis session and verify the new plan.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {"sql_query": "SET SESSION tidb_enable_index_merge = ON"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": f"EXPLAIN {MOCK_CASE.fault_fingerprint_sql}"},
            },
            {"api": "submit", "args": {"report": PASS_REPORT}},
        ],
    },
]


def main():
    scenario = TidbQueryPerfIndexMergeSelectionFailureScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB QP03 Index Merge scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--container-name", default="tidb-index-merge")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(run_id=args.container_name, port_base=args.port, return_window_seconds=300)
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a DBA agent.",
            use_native_tools=False,
        )
        agent.set_mock_responses(FULL_SCORE_MOCK_RESPONSES)
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
        ),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (True, True, True):
            raise RuntimeError(f"QP03 mock must pass DP/OP/SP, observed={observed!r}, result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
