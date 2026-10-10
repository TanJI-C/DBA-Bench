import argparse
from datetime import datetime, timedelta

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb.query_perf.optimistic_write_conflict_frozen_history import (
    TidbQueryPerfOptimisticWriteConflictFrozenHistoryScenario,
)


class FrozenHistoryReferenceMockAgent(MockLLMAgent):
    """Exercise the public history path before applying the reference repair."""

    def solve(self):
        overview = self.execute(
            "query_metrics",
            {"metric_type": "transaction_commit"},
            thinking="Locate the historical transaction window before reading current rows.",
        )
        available_end = overview["window"]["available_end"]
        end = datetime.strptime(available_end, "%Y-%m-%d %H:%M:%S")
        # The procedural reference bundle places the target capture just before this window.
        history_end = end - timedelta(seconds=3120)
        start = history_end - timedelta(seconds=900)
        self.execute(
            "read_log",
            {
                "target": "tidb/tidb-0",
                "start_timestamp": start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_timestamp": history_end.strftime("%Y-%m-%d %H:%M:%S"),
                "lines": 320,
            },
            thinking="Correlate commit records with the component log in a bounded window.",
        )
        case = TidbQueryPerfOptimisticWriteConflictFrozenHistoryScenario().get_case(
            "optimistic_write_conflict_history_investigation"
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT id, tenant, v, last_writer, payload FROM {case.db}.{case.table} "
                    f"WHERE id IN ({case.target_id}, {case.competing_id}) ORDER BY id"
                )
            },
            thinking="Confirm the target and competing rows before compensation.",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SET SESSION tidb_txn_mode = 'PESSIMISTIC'; "
                    "START TRANSACTION; "
                    f"UPDATE {case.db}.{case.table} SET v = v + 1, last_writer = 'dba-agent' "
                    f"WHERE id = {case.target_id} AND tenant = '{case.target_tenant}'; "
                    f"UPDATE {case.db}.{case.table} SET v = v + 1, last_writer = 'dba-agent' "
                    f"WHERE id = {case.target_id} AND tenant = '{case.target_tenant}'; "
                    "COMMIT;"
                )
            },
            thinking="Complete two guarded increments in one session-local pessimistic transaction.",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT id, tenant, v, last_writer, payload FROM {case.db}.{case.table} "
                    f"WHERE id IN ({case.target_id}, {case.competing_id}) ORDER BY id"
                )
            },
            thinking="Verify the target value and unchanged competing row.",
        )
        return {"report": case.reference_report}


def _build_agent(mode: str, model: str, config_path: str):
    if mode == "mock":
        return FrozenHistoryReferenceMockAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA agent.",
            use_native_tools=False,
        )
    return build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)


def main() -> None:
    scenario = TidbQueryPerfOptimisticWriteConflictFrozenHistoryScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB frozen-history optimistic write-conflict investigation scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--port", type=int, default=58520)
    parser.add_argument("--container-name", default="aiopsbench-tidb-frozen-history-qp01")
    parser.add_argument("--seed", dest="history_seed", type=int, default=20260816)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    agent = _build_agent(args.mode, args.model, args.config_path)
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode="off",
            history_seed=args.history_seed,
        ),
    ).run()
    print(
        "QP01 frozen-history result: "
        f"DiagnosisPass={result['DiagnosisPass']} "
        f"OutcomePass={result['OutcomePass']} "
        f"SafePass={result['SafePass']}"
    )
    if args.mode == "mock" and (
        result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]
    ) != (True, True, True):
        raise AssertionError(f"QP01 frozen-history mock path did not fully pass: {result!r}")


if __name__ == "__main__":
    main()
