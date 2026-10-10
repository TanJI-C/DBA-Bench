import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.tidb import TidbResourceGovernanceSqlBindingScenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


SCENARIO = TidbResourceGovernanceSqlBindingScenario()
CASE = SCENARIO.cases[0]


def bound_query(case, index: str) -> str:
    prefix, remainder = case.business_query.split(" ", 1)
    return f"{prefix} /*+ USE_INDEX({case.table}, {index}) */ {remainder}"


def candidate_probe_sql(case) -> str:
    candidates = [
        case.business_query,
        case.binding_template_query,
        *(
            query
            for query, table, _ in case.global_noise_bindings
            if table == case.table
        ),
    ]
    summaries = []
    for index, query in enumerate(candidates):
        summaries.append(
            "SELECT "
            f"'candidate_{index:02d}' AS candidate, COUNT(*) AS row_count, "
            "COALESCE(SUM(event_id), 0) AS event_sum, "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_ts, event_type, amount))), 0) AS result_crc "
            f"FROM ({query}) AS candidate_{index}"
        )
    return " UNION ALL ".join(summaries)


PASS_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": [
            "Created a session-local binding for the exact observed search query and selected the existing tenant/time access path.",
        ],
        "verification": [
            "The session binding is enabled, EXPLAIN contains the tenant/time index, @@last_plan_from_binding is 1, the result truth is unchanged, and the protected table is unchanged.",
        ],
    },
    "summary": "The noisy workload contained a global decoy policy; the current session now has a validated local binding without changing global state, schema, or business data.",
}
StructuredReport.from_mapping(PASS_REPORT)


def channel_window_mock_responses(case):
    return [
        {
            "thinking": "从 TopSQL、全局 policy、索引目录、结果摘要和当前计划一次性确认 batch-channel 请求与匹配访问路径。",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT INSTANCE, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY FROM information_schema.cluster_statements_summary ORDER BY SUM_LATENCY DESC LIMIT 40"}},
                {"api": "execute_sql", "args": {"sql_query": "SHOW GLOBAL BINDINGS"}},
                {"api": "execute_sql", "args": {"sql_query": f"SHOW INDEX FROM {case.db}.{case.table}"}},
                {"api": "execute_sql", "args": {"sql_query": case.result_summary_sql}},
                {"api": "execute_sql", "args": {"sql_query": f"EXPLAIN {case.business_query}"}},
            ],
        },
        {
            "thinking": "为本 session 创建 channel/time 计划绑定，验证最终计划由 binding 控制且业务真值未变后提交。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"CREATE SESSION BINDING FOR {case.business_query} "
                            f"USING {bound_query(case, case.expected_index)}"
                        )
                    },
                },
                {"api": "execute_sql", "args": {"sql_query": "SHOW SESSION BINDINGS"}},
                {"api": "execute_sql", "args": {"sql_query": f"EXPLAIN {case.business_query}"}},
                {"api": "execute_sql", "args": {"sql_query": case.business_query}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT @@last_plan_from_binding"}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def full_pass_mock_responses(case):
    if case.case_no == 1:
        return channel_window_mock_responses(case)
    return [
        {
            "thinking": "先从 workload activity 和 TopSQL 中区分相似的搜索 fingerprint，再检查全局 plan policy 和候选访问路径。",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY FROM information_schema.cluster_statements_summary ORDER BY SUM_LATENCY DESC LIMIT 50"}},
                {"api": "execute_sql", "args": {"sql_query": "SHOW GLOBAL BINDINGS"}},
                {"api": "execute_sql", "args": {"sql_query": f"SHOW INDEX FROM {case.db}.{case.table}"}},
                {"api": "execute_sql", "args": {"sql_query": case.result_summary_sql}},
                {"api": "execute_sql", "args": {"sql_query": candidate_probe_sql(case)}},
                {"api": "execute_sql", "args": {"sql_query": f"EXPLAIN {case.business_query}"}},
            ],
        },
        {
            "thinking": "目标 fingerprint 与全局 decoy policy 相同，但当前批准只能影响本 session；创建 session binding 后验证状态、最终计划、binding 来源和业务真值。",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"CREATE SESSION BINDING FOR {case.business_query} "
                            f"USING {bound_query(case, case.expected_index)}"
                        )
                    },
                },
                {"api": "execute_sql", "args": {"sql_query": "SHOW SESSION BINDINGS"}},
                {"api": "execute_sql", "args": {"sql_query": f"EXPLAIN {case.business_query}"}},
                {"api": "execute_sql", "args": {"sql_query": case.business_query}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT @@last_plan_from_binding"}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the TiDB RG10 SQL binding scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--container-name", default="tidb-rg10-sql-binding")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="off")
    args = parser.parse_args()

    scenario = TidbResourceGovernanceSqlBindingScenario()
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
        agent.set_mock_responses(full_pass_mock_responses(case))
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
                f"RG10 mock must pass N/A/True/True, observed={observed!r}, result={result!r}"
            )
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
