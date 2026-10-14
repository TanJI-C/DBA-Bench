import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import StructuredReport
from src.scenarios.tidb import TidbResourceGovernanceLightningBudgetScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


PASS_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": [
            "Ran Lightning precheck and applied an initial bounded budget for the source-defined import",
            "Rebalanced the running import from its real checkpoint and completed the second bounded budget phase",
        ],
        "verification": [
            "Lightning completed both checkpoint-controlled resource phases with the exact source row count",
            "Protected business tables remained unchanged while the import controller ran",
        ],
    },
    "summary": "The online Lightning import completed both bounded resource phases without changing protected business tables.",
}
StructuredReport.from_mapping(PASS_REPORT)


def build_mock_responses(case):
    target = f"{case.db}.{case.import_table}"
    return [
        {
            "thinking": "Inspect the actual import state, source contract, and live frontend workload before changing resources.",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "job", "operation": "get"}},
                {"api": "query_metrics", "args": {"metric_type": "cpu"}},
                {"api": "query_metrics", "args": {"metric_type": "disk_io"}},
                {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
            ],
        },
        {
            "thinking": "The import is waiting for governance. Validate Lightning requirements before choosing a bounded budget.",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "job", "operation": "check"}},
            ],
        },
        {
            "thinking": "Use a bounded budget that keeps the online frontend SLO inside its contract while still reaching the checkpoint handoff.",
            "actions": [
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "job",
                        "operation": "update",
                        "parameters": {
                            "region_concurrency": case.phase1_region_concurrency,
                            "disk_quota_mb": case.phase1_disk_quota_mb,
                            "store_write_bwlimit_mib": case.phase1_store_write_bwlimit_mib,
                        },
                    },
                },
                {"api": "manage_cluster", "args": {"resource": "job", "operation": "wait", "parameters": {"timeout_seconds": 900}}},
            ],
        },
        {
            "thinking": "The first budget reached a real checkpoint handoff. Select a more conservative final budget from the current controller state and resume the same import.",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "job", "operation": "get"}},
                {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "job",
                        "operation": "update",
                        "parameters": {
                            "region_concurrency": 2,
                            "disk_quota_mb": 2048,
                            "store_write_bwlimit_mib": 48,
                        },
                    },
                },
                {"api": "manage_cluster", "args": {"resource": "job", "operation": "wait", "parameters": {"timeout_seconds": 900}}},
            ],
        },
        {
            "thinking": "The two-stage import completed; verify only the core target count and protected business state before submitting.",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "job", "operation": "get"}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT COUNT(*) FROM {target}"}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def main():
    scenario = TidbResourceGovernanceLightningBudgetScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB RG05 Lightning resource-governance scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=16)
    parser.add_argument("--port", type=int, default=24700)
    parser.add_argument("--container-name", default="rg05-lightning-budget")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="off")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=300,
    )
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA agent.",
            use_native_tools=False,
        )
        agent.set_mock_responses(build_mock_responses(case))
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )

    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (None, True, True):
            raise RuntimeError(
                f"RG05 mock must pass N/A/True/True, observed={observed!r}, result={result!r}"
            )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
