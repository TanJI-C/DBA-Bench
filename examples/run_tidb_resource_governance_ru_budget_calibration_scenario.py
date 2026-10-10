import argparse
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.tidb import (
    TidbResourceGovernanceRuBudgetCalibrationScenario,
)
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


MOCK_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": [
            "raised the OLTP and OLAP RU budgets within the shared cap",
            "bounded batch and adhoc groups with moderated burst behavior",
            "bounded the built-in default group within the shared cap",
        ],
        "verification": [
            "resource control remains ON and all managed groups are finite",
            "OLTP p95, OLAP throughput, and order truth were verified",
        ],
    },
    "summary": "The mixed workload RU allocation was calibrated without changing business data.",
}
StructuredReport.from_mapping(MOCK_REPORT)


MOCK_RESPONSES = [
    {
        "thinking": "先从混合 workload、延迟和 CPU 观察业务分层，再把 SQL fingerprint 与资源组状态对应起来。",
        "actions": [
            {
                "api": "query_metrics",
                "args": {"metric_type": "active_connections", "target": None},
            },
            {
                "api": "query_metrics",
                "args": {"metric_type": "query_latency", "target": "tidb/tidb-0"},
            },
            {
                "api": "query_metrics",
                "args": {"metric_type": "cpu", "target": None},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT NAME, RU_PER_SEC, BURSTABLE "
                        "FROM information_schema.resource_groups ORDER BY NAME"
                    )
                },
            },
        ],
    },
    {
        "thinking": "资源组快照只能说明配置，继续查操作目标的有效期和历史版本，再关联 statement summary。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SHOW TABLES FROM rg01_ops"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT objective_id, effective_from, effective_to, service, "
                        "resource_group, metric, operator, target_value, status "
                        "FROM rg01_ops.service_objectives "
                        "ORDER BY effective_from DESC, objective_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT INSTANCE, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, "
                        "SUM_LATENCY FROM information_schema.cluster_statements_summary "
                        "ORDER BY SUM_LATENCY DESC LIMIT 40"
                    )
                },
            },
        ],
    },
    {
        "thinking": "当前有效目标要求核心业务保底、有限共享 cap 和 bounded burst；先给出一个合法的非 mock 分配，再用 workload feedback 验证。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "ALTER RESOURCE GROUP rg01_oltp RU_PER_SEC = 700 BURSTABLE=FALSE; "
                        "ALTER RESOURCE GROUP rg01_olap RU_PER_SEC = 240 BURSTABLE=FALSE; "
                        "ALTER RESOURCE GROUP rg01_batch RU_PER_SEC = 40 BURSTABLE=FALSE; "
                        "ALTER RESOURCE GROUP rg01_adhoc RU_PER_SEC = 20 BURSTABLE=FALSE"
                    )
                },
            },
            {
                "api": "query_metrics",
                "args": {"metric_type": "query_latency", "target": "tidb/tidb-0"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT NAME, RU_PER_SEC, BURSTABLE "
                        "FROM information_schema.resource_groups "
                        "WHERE NAME LIKE 'rg01_%' ORDER BY NAME"
                    )
                },
            },
        ],
    },
    {
        "thinking": "预算反馈保持核心 p95、分析吞吐、bounded 资源组和业务 truth，提交最终结构化结果。",
        "actions": [
            {
                "api": "query_metrics",
                "args": {"metric_type": "query_latency", "target": "tidb/tidb-0"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
                        "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, customer_id, "
                        "order_status, order_ts, amount, payload))), 0) "
                        "FROM rg01_ops.orders"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT NAME, RU_PER_SEC, BURSTABLE "
                        "FROM information_schema.resource_groups "
                        "WHERE NAME IN ('rg01_oltp', 'rg01_olap', 'rg01_batch', 'rg01_adhoc', 'default') "
                        "ORDER BY NAME"
                    )
                },
            },
            {"api": "submit", "args": {"report": MOCK_REPORT}},
        ],
    },
]


def _rewrite_case(value, case):
    if isinstance(value, str):
        return value.replace(
            "ALTER RESOURCE GROUP rg01_oltp RU_PER_SEC = 700 BURSTABLE=FALSE; "
            "ALTER RESOURCE GROUP rg01_olap RU_PER_SEC = 240 BURSTABLE=FALSE; "
            "ALTER RESOURCE GROUP rg01_batch RU_PER_SEC = 40 BURSTABLE=FALSE; "
            "ALTER RESOURCE GROUP rg01_adhoc RU_PER_SEC = 20 BURSTABLE=FALSE",
            _budget_sql(case),
        )
    if isinstance(value, list):
        return [_rewrite_case(item, case) for item in value]
    if isinstance(value, dict):
        return {
            key: (case.reference_report if key == "report" else _rewrite_case(item, case))
            for key, item in value.items()
        }
    return value


def _default_reservation_ru(case):
    for row in case.service_objectives:
        if row[4] == "default" and row[8] == "active":
            return int(float(row[7]))
    raise RuntimeError(
        "RG01 mock requires an active default-group platform reservation in service_objectives: "
        f"case={case.case_id!r}"
    )


def _budget_sql(case):
    minimums = dict(case.minimum_ru_per_sec)
    default_ru = _default_reservation_ru(case)
    extra = case.maximum_total_ru_per_sec - sum(minimums.values()) - default_ru
    oltp_extra = min(200, extra)
    allocation = {
        case.oltp_group: minimums[case.oltp_group] + oltp_extra,
        case.olap_group: minimums[case.olap_group] + extra - oltp_extra,
        "rg01_batch": minimums["rg01_batch"],
        "rg01_adhoc": minimums["rg01_adhoc"],
        "default": default_ru,
    }
    return "; ".join(
        f"ALTER RESOURCE GROUP {group} RU_PER_SEC = {allocation[group]} BURSTABLE=FALSE"
        for group in (case.oltp_group, case.olap_group, "rg01_batch", "rg01_adhoc", "default")
    )


def _rebalanced_mock_responses(case):
    return [
        {
            "thinking": "资源组当前分配与 active 服务目标合并在同一证据状态里读取，直接支撑缩减预留下的重平衡决策。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT NAME, RU_PER_SEC, BURSTABLE "
                            "FROM information_schema.resource_groups "
                            "WHERE NAME LIKE 'rg01_%' ORDER BY NAME"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT objective_id, service, resource_group, metric, "
                            "operator, target_value FROM rg01_ops.service_objectives "
                            "WHERE status = 'active' ORDER BY objective_id"
                        )
                    },
                },
            ],
        },
        {
            "thinking": "在平台预留内一次性给出有限有界的组预算，并用 workload 反馈与业务 truth 验证后提交。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {"sql_query": _budget_sql(case)},
                },
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "query_latency", "target": "tidb/tidb-0"},
                },
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT NAME, RU_PER_SEC, BURSTABLE "
                            "FROM information_schema.resource_groups "
                            "WHERE NAME IN ('rg01_oltp', 'rg01_olap', 'rg01_batch', 'rg01_adhoc', 'default') "
                            "ORDER BY NAME"
                        )
                    },
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": case.business_truth_sql},
                },
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def build_mock_responses(case):
    if case.case_no == 1:
        return _rebalanced_mock_responses(case)
    return _rewrite_case(copy.deepcopy(MOCK_RESPONSES), case)


def main() -> None:
    scenario = TidbResourceGovernanceRuBudgetCalibrationScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB RG01 mixed OLTP/OLAP RU budget calibration scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=16)
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--container-name", default="tidb-rg01")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    parser.add_argument("--cold-start-timeout", type=int, default=900)
    parser.add_argument("--warm-start-timeout", type=int, default=300)
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
            system_prompt="You are a TiDB resource governance DBA.",
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
                "RG01 mock must pass N/A/True/True: "
                f"observed={observed!r}, result={result!r}"
            )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
