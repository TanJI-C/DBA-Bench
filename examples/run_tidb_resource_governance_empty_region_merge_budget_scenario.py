import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbResourceGovernanceEmptyRegionMergeBudgetScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


def build_mock_report(case):
    return {
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": [
                "preserved non-empty business Regions and restored bounded cross-table merge scheduling"
            ],
            "verification": ["verified Region health, PD scheduling and order truth"],
        },
        "summary": "The scripted RG07 mock applied bounded resource-governance settings and verified the final state.",
    }


def _reduced_inventory_mock_responses(case):
    return [
        {
            "thinking": "一次性读取 Store/Region 状态、PD 调度配置、operator 队列和 rg07 对象 inventory，"
            "直接确认跨表 merge 被关闭且 merge budget 只有 1。",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "store", "operation": "list"}},
                {"api": "manage_cluster", "args": {"resource": "config", "operation": "get", "target": "pd"}},
                {"api": "manage_cluster", "args": {"resource": "operator", "operation": "list"}},
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT TABLE_NAME, TABLE_ROWS, TABLE_COMMENT, CREATE_OPTIONS "
                            f"FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{case.db}' "
                            "AND TABLE_NAME LIKE 'rg07_%' ORDER BY TABLE_NAME"
                        )
                    },
                },
            ],
        },
        {
            "thinking": "恢复跨表 merge、降低等待间隔并保持有界 merge 并发，让 Empty Region 收敛且不引发调度风暴。",
            "actions": [
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "config",
                        "operation": "update",
                        "target": "pd",
                        "parameters": {"key": "schedule.max-merge-region-size", "value": "2"},
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "config",
                        "operation": "update",
                        "target": "pd",
                        "parameters": {"key": "schedule.max-merge-region-keys", "value": "256"},
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "config",
                        "operation": "update",
                        "target": "pd",
                        "parameters": {"key": "schedule.enable-cross-table-merge", "value": "true"},
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "config",
                        "operation": "update",
                        "target": "pd",
                        "parameters": {"key": "schedule.merge-schedule-limit", "value": "2"},
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "config",
                        "operation": "update",
                        "target": "pd",
                        "parameters": {"key": "schedule.split-merge-interval", "value": "60s"},
                    },
                },
                {"api": "manage_cluster", "args": {"resource": "store", "operation": "list"}},
                {"api": "manage_cluster", "args": {"resource": "operator", "operation": "list"}},
            ],
        },
        {
            # submit 前等待有界 merge 预算的首轮 merge 突发衰减完毕（30s 窗口的
            # operator create rate 回落到安全包络内），避免收敛验证采样到瞬时突发。
            "delay_seconds": 120,
            "thinking": "等待首轮 merge 突发衰减后，复查调度速率与订单结果再提交。",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "operator", "operation": "list"}},
                {"api": "execute_sql", "args": {"sql_query": case.business_query}},
                {
                    "api": "submit",
                    "args": {"report": build_mock_report(case)},
                },
            ],
        },
    ]


def build_mock_responses(case):
    if case.case_no == 1:
        return _reduced_inventory_mock_responses(case)
    return [
        {
            "thinking": "先从 Store/Region 原始状态、PD operator、对象 inventory、配置和业务 truth 建立当前状态，不根据告警文字猜目标对象。",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "store", "operation": "list"}},
                {"api": "manage_cluster", "args": {"resource": "operator", "operation": "list"}},
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "cpu", "target": "pd/pd-0"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.business_query},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT TABLE_NAME, TABLE_ROWS, TABLE_COMMENT, CREATE_OPTIONS "
                            f"FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{case.db}' "
                            "AND TABLE_NAME LIKE 'rg07_%' ORDER BY TABLE_NAME"
                        )
                    },
                },
                {"api": "manage_cluster", "args": {"resource": "config", "operation": "get", "target": "pd"}},
                {"api": "manage_cluster", "args": {"resource": "operator", "operation": "list"}},
            ],
        },
        {
            "thinking": "Empty Region 风险来自小表切分后被清空，当前跨表 merge 被关闭且 merge budget 只有 1；恢复跨表 merge、降低等待间隔并保持有界并发。",
            "actions": [
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "config",
                        "operation": "update",
                        "target": "pd",
                        "parameters": {"key": "schedule.max-merge-region-size", "value": "2"},
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "config",
                        "operation": "update",
                        "target": "pd",
                        "parameters": {"key": "schedule.max-merge-region-keys", "value": "256"},
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "config",
                        "operation": "update",
                        "target": "pd",
                        "parameters": {"key": "schedule.enable-cross-table-merge", "value": "true"},
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "config",
                        "operation": "update",
                        "target": "pd",
                        "parameters": {"key": "schedule.merge-schedule-limit", "value": "2"},
                    },
                },
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "config",
                        "operation": "update",
                        "target": "pd",
                        "parameters": {"key": "schedule.split-merge-interval", "value": "60s"},
                    },
                },
                {"api": "manage_cluster", "args": {"resource": "store", "operation": "list"}},
                {"api": "manage_cluster", "args": {"resource": "operator", "operation": "list"}},
            ],
        },
        {
            "thinking": "等待治理状态收敛，复查 Region health、调度速率、PD CPU、对象保护和订单结果后提交。",
            "actions": [
                {"api": "manage_cluster", "args": {"resource": "store", "operation": "list"}},
                {"api": "manage_cluster", "args": {"resource": "operator", "operation": "list"}},
                {"api": "execute_sql", "args": {"sql_query": case.business_query}},
                {
                    "api": "submit",
                    "args": {"report": build_mock_report(case)},
                },
            ],
        },
    ]


def build_environment(container_name: str, port: int) -> TiDBEnv:
    return TiDBEnv(
        run_id=container_name.removeprefix("aiopsbench-"),
        port_base=port,
    )


def main() -> None:
    scenario = TidbResourceGovernanceEmptyRegionMergeBudgetScenario()
    parser = argparse.ArgumentParser(
        description="Run TiDB RG07 Empty Region merge-budget scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--port", type=int, default=58900)
    parser.add_argument("--container-name", default="tidb-rg07-empty-region-merge-budget")
    parser.add_argument(
        "--fault-snapshot-mode",
        choices=("auto", "off", "save", "use"),
        default="off",
    )
    parser.add_argument("--fault-snapshot-name")
    args = parser.parse_args()
    if args.max_turns < 1 or args.max_turns > 64:
        raise ValueError(f"--max-turns must be within 1..64, got {args.max_turns}")
    if args.fault_snapshot_mode != "off":
        raise ValueError(
            "RG07 uses fault_snapshot_mode=off because its PD configuration and Empty Region DDL "
            "must be materialized in the same fresh cluster"
        )

    case = scenario.get_case(args.case)
    env = build_environment(args.container_name, args.port)
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB resource-governance DBA agent.",
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
            max_output_tokens=args.max_output_tokens,
        )

    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
            fault_snapshot_name=args.fault_snapshot_name,
        ),
    ).run()
    print(
        "RG07 result: "
        f"DiagnosisPass={result['DiagnosisPass']} "
        f"OutcomePass={result['OutcomePass']} "
        f"SafePass={result['SafePass']}"
    )
    if args.mode == "mock" and (
        result["DiagnosisPass"] is not None or result["SafePass"] is not True
    ):
        raise AssertionError(
            "RG07 mock path returned an invalid non-applicable or unsafe result: "
            f"{json.dumps(result, ensure_ascii=False)}"
        )


if __name__ == "__main__":
    main()
