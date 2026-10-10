"""Run the target-LLM-only frozen-history Lightning budget Case."""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.execution.deployment import lightning_job_id
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb import TidbResourceGovernanceLightningBudgetFrozenHistoryScenario


def build_reference_mock_responses(case, job_target):
    budget_update = {
        "api": "manage_cluster",
        "args": {
            "resource": "job",
            "operation": "update",
            "parameters": {
                "job_id": job_target,
                "region_concurrency": 1,
                "disk_quota_mb": 1024,
                "store_write_bwlimit_mib": 16,
            },
        },
    }
    return [
        {
            "thinking": "先从 job registry 确认 checkpoint handoff、source 和 phase1 partial state，再从历史 Lightning 指标和 TiKV/前端时序定位事故窗口，据此排除 paused 的 backfill job 并锁定客户导入 job。",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "job", "operation": "get"}},
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "lightning_progress", "target": job_target},
                },
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "lightning_throughput", "target": job_target},
                },
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "lightning_workers", "target": job_target},
                },
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "cpu", "target": "tikv/tikv-0"},
                },
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "disk_io", "target": "tikv/tikv-0"},
                },
            ],
        },
        {
            "thinking": "历史指标显示 Lightning 活动与 TiKV 写入压力存在耦合，当前 reconfigure_required 是同一 job 的 checkpoint 暂停；选择三维均非零且处于 phase2 上限内的预算恢复。",
            "actions": [
                budget_update,
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "job",
                        "operation": "wait",
                        "parameters": {"timeout_seconds": 900},
                    },
                },
                {"api": "manage_cluster", "args": {"resource": "job", "operation": "get"}},
            ],
        },
        {
            "thinking": "最后用当前业务连接和保护状态完成验证，然后提交完整诊断、处置和验证闭环。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "workload_profile"}},
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT COUNT(*) AS imported_rows FROM "
                            f"{case.db}.{case.import_table}"
                        )
                    },
                },
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def main() -> None:
    scenario = TidbResourceGovernanceLightningBudgetFrozenHistoryScenario()
    parser = argparse.ArgumentParser(
        description="Run the target-LLM-only TiDB frozen-history Lightning budget scenario."
    )
    parser.add_argument("--mode", choices=["mock", "llm"], default="llm")
    parser.add_argument(
        "--case",
        required=True,
        choices=[case.case_id for case in scenario.cases],
    )
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--port", type=int, default=24730)
    parser.add_argument("--container-name", default="rg03-lightning-frozen-history")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--storage-key")
    parser.add_argument("--storage-root")
    args = parser.parse_args()
    if (args.storage_key is None) != (args.storage_root is None):
        parser.error("--storage-key and --storage-root must be supplied together")

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=600,
        storage_key=args.storage_key,
        storage_root=args.storage_root,
    )
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA reference agent.",
            use_native_tools=False,
        )
        agent.set_mock_responses(
            build_reference_mock_responses(case, lightning_job_id(env.run_id))
        )
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
        expected = (True, True, True)
        actual = (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"])
        if actual != expected:
            raise RuntimeError(
                f"RG05 frozen-history reference mock did not pass DP/OP/SP: "
                f"expected={expected}, actual={actual}, result={result!r}"
            )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
