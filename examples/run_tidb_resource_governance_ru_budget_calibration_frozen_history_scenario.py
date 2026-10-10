from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.execution.environment import TiDBEnv
from src.execution.history.metrics import format_utc_timestamp
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb.resource_governance.ru_budget_calibration_frozen_history import (
    TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryScenario,
    build_frozen_history_reference_report,
)


def build_mock_responses(case, report, target_window):
    groups_sql = (
        "SELECT NAME, RU_PER_SEC, BURSTABLE FROM information_schema.resource_groups "
        "WHERE NAME IN ('mf_rg01_checkout', 'mf_rg01_revenue', 'mf_rg01_archive', 'mf_rg01_dashboard') "
        "ORDER BY NAME"
    )
    return [
        {
            "thinking": "先看冻结的历史 resource-group RU/wait 序列，再核对当前配置。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "resource_group_usage"}},
                {"api": "query_metrics", "args": {"metric_type": "resource_group_throttle"}},
                {"api": "query_metrics", "args": {"metric_type": "query_latency", "target": "tidb/tidb-0"}},
                {
                    "api": "read_log",
                    "args": {
                        "target": "tidb/tidb-0",
                        "start_timestamp": target_window["start_timestamp"],
                        "end_timestamp": target_window["end_timestamp"],
                        "lines": 100,
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "target": "history",
                        "sql_query": f"SELECT * FROM statement_summary WHERE event_start_utc < '{target_window['end_timestamp']}' AND event_end_utc >= '{target_window['start_timestamp']}' ORDER BY sum_latency DESC LIMIT 100",
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "target": "history",
                        "sql_query": f"SELECT * FROM slow_query WHERE event_time_utc >= '{target_window['start_timestamp']}' AND event_time_utc < '{target_window['end_timestamp']}' ORDER BY wait_time_ms DESC LIMIT 100",
                    },
                },
                {"api": "execute_sql", "args": {"sql_query": groups_sql}},
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT objective_id, effective_from, effective_to, service, resource_group, "
                            "metric, operator, target_value, status FROM benchops_mf_rg01.service_objectives "
                            "ORDER BY effective_from DESC, objective_id"
                        )
                    },
                },
            ],
        },
        {
            "thinking": "按当前 active objectives 保留平台预留，将四个 managed group 设为 finite bounded allocation。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": "ALTER RESOURCE GROUP mf_rg01_checkout RU_PER_SEC = 700 BURSTABLE=FALSE"
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "ALTER RESOURCE GROUP mf_rg01_revenue RU_PER_SEC = 240 BURSTABLE=FALSE"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "ALTER RESOURCE GROUP mf_rg01_archive RU_PER_SEC = 40 BURSTABLE=FALSE"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "ALTER RESOURCE GROUP mf_rg01_dashboard RU_PER_SEC = 20 BURSTABLE=FALSE"},
                },
                {"api": "query_metrics", "args": {"metric_type": "resource_group_throttle"}},
                {"api": "execute_sql", "args": {"sql_query": groups_sql}},
            ],
        },
        {
            "thinking": "四组均已 bounded，managed total 不超过 cap；提交历史因果、处置和验证结果。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "resource_group_usage"}},
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.business_truth_sql},
                },
                {"api": "execute_sql", "args": {"sql_query": groups_sql}},
                {"api": "submit", "args": {"report": report}},
            ],
        },
    ]


class FrozenHistoryReferenceMockAgent(MockLLMAgent):
    def __init__(self, *, case, env):
        super().__init__(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB resource governance DBA.",
            use_native_tools=False,
        )
        self.case = case
        self.env = env

    def solve(self):
        report = build_frozen_history_reference_report(
            self.env._history_timeline.audit,
            self.env._history_timeline,
        )
        target_window = self.env._history_timeline.audit["target_window"]
        self.set_mock_responses(build_mock_responses(self.case, report, {
            "start_timestamp": format_utc_timestamp(int(target_window["start_ms"])),
            "end_timestamp": format_utc_timestamp(int(target_window["end_ms"])),
        }))
        return super().solve()


def main() -> None:
    scenario = TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB frozen-history RU budget history calibration scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--port", type=int, default=53000)
    parser.add_argument("--container-name", default="tidb-frozen-history-rg01")
    parser.add_argument("--seed", type=int, default=20260816)
    parser.add_argument("--storage-key")
    parser.add_argument("--storage-root")
    parser.add_argument("--cold-start-timeout", type=int, default=1800)
    parser.add_argument("--warm-start-timeout", type=int, default=300)
    args = parser.parse_args()

    if (args.storage_key is None) != (args.storage_root is None):
        raise ValueError("--storage-key and --storage-root must be supplied together")

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        tidb_readiness_timeout_sec=args.cold_start_timeout,
        warm_tidb_readiness_timeout_sec=args.warm_start_timeout,
        return_window_seconds=300,
        storage_key=args.storage_key,
        storage_root=args.storage_root,
    )
    if args.mode == "mock":
        agent = FrozenHistoryReferenceMockAgent(case=case, env=env)
    else:
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
            fault_snapshot_mode="off",
            history_seed=args.seed,
            diagnosis_match_mode="exact",
        ),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (True, True, True):
            raise RuntimeError(
                "Frozen-history RG01 mock must pass True/True/True: "
                f"observed={observed!r}, result={result!r}"
            )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
