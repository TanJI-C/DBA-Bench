import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import StructuredReport
from src.scenarios.tidb import TidbResourceGovernanceRg06Scenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


PASS_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": [
            "raised the case-local sorter and sink budget within the tested envelope",
        ],
        "verification": [
            "verified checkpoint/resolved convergence, equal source and sink truth, GC headroom, and both SLOs",
        ],
    },
    "summary": (
        "The changefeed caught up with a bounded sorter and sink budget while preserving the source, "
        "downstream truth, GC headroom, and foreground latency."
    ),
}
StructuredReport.from_mapping(PASS_REPORT)


def _metrics_query(case, family: str, target: str | None = None) -> dict:
    target_filter = f" AND target = '{target}'" if target is not None else ""
    return {
        "api": "execute_sql",
        "args": {
            "sql_query": (
                "SELECT sample_id, sample_ts, component, metric_name, target, value, text_value, unit "
                f"FROM {case.db}.{case.metrics_table} "
                f"WHERE family = '{family}'{target_filter} "
                "ORDER BY sample_ts DESC, sample_id DESC LIMIT 200"
            )
        },
    }


def _reconcile_mock_responses(case, metrics):
    return [
        {
            "thinking": "从 registry、目标 feed 的 progress 原始窗口和当前 config 一次性确认受影响的 reconciliation feed 及其过小的 sink 预算。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT feed_id, owner, source_table, sink_table, business_purpose, "
                            "state, lag_slo_rows, downstream_slo_ms "
                            f"FROM {case.db}.{case.registry_table} ORDER BY feed_id"
                        )
                    },
                },
                metrics("progress", case.changefeed_id),
                {"api": "execute_sql", "args": {"sql_query": f"SELECT * FROM {case.db}.{case.config_table}"}},
            ],
        },
        {
            "thinking": "用有界联合 sink/sorter 预算提升吞吐，只改 case-local config 行，不触碰全局设置和相邻 feed。",
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"UPDATE {case.db}.{case.config_table} SET sorter_memory_mb = 256, "
                        "sink_workers = 8, sink_batch_rows = 100, sink_write_budget = 0.75 "
                        "WHERE config_id = 1"
                    )
                },
            },
        },
        {
            "thinking": "让有界管线追平后验证最终指标与业务真值。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(10)"}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(10)"}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(10)"}},
                metrics("progress", case.changefeed_id),
                metrics("pipeline", case.changefeed_id),
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def build_mock_responses(case):
    metrics = lambda family, target=None: _metrics_query(case, family, target)
    if case.case_no == 1:
        return _reconcile_mock_responses(case, metrics)
    return [
    {
        "thinking": "Inspect the raw progress and pipeline windows before changing the local budget.",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT feed_id, owner, source_table, sink_table, business_purpose, "
                        "state, lag_slo_rows, downstream_slo_ms "
                        f"FROM {case.db}.{case.registry_table} ORDER BY feed_id"
                    )
                },
            },
            metrics("progress"),
            metrics("pipeline"),
            metrics("resource"),
            {"api": "query_metrics", "args": {"metric_type": "active_connections", "target": None}},
            {"api": "execute_sql", "args": {"sql_query": f"SELECT * FROM {case.db}.{case.config_table}"}},
        ],
    },
    {
        "thinking": "The sink is the limiting stage; use a bounded joint sorter and sink budget, not an unlimited burst.",
        "action": {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    f"UPDATE {case.db}.{case.config_table} SET sorter_memory_mb = 256, "
                    "sink_workers = 8, sink_batch_rows = 100, sink_write_budget = 0.75 "
                    "WHERE config_id = 1"
                )
            },
        },
    },
    {
        "thinking": "Allow the bounded pipeline to drain, then verify the final metrics and business truth.",
        "actions": [
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(10)"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(10)"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(10)"}},
            {"api": "execute_sql", "args": {"sql_query": "SELECT SLEEP(10)"}},
            metrics("progress", case.changefeed_id),
            metrics("pipeline", case.changefeed_id),
            metrics("resource", case.changefeed_id),
            {"api": "submit", "args": {"report": case.reference_report}},
        ],
    },
    ]


def main():
    scenario = TidbResourceGovernanceRg06Scenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB RG06 TiCDC checkpoint-lag resource-governance scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--port", type=int, default=4400)
    parser.add_argument("--container-name", default="tidb-rg06")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
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
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
        ),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (None, True, True):
            raise RuntimeError(
                f"RG06 mock must pass DP=None/OP=True/SP=True, observed={observed!r}, result={result!r}"
            )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
