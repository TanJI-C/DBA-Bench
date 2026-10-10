import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.tidb import TidbBusinessChangeDmReplaceScenario
from src.execution.environment import TiDBBusinessChangeEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


SCENARIO = TidbBusinessChangeDmReplaceScenario()
CASE = SCENARIO.get_case("failed_ddl_safe_replace")
PASS_REPORT = CASE.reference_report
StructuredReport.from_mapping(PASS_REPORT)


def _dm_action_sql(case, replacement_sql: str) -> str:
    escaped = replacement_sql.replace("'", "''")
    return (
        "INSERT INTO dm_actions(task_name, action, replacement_sql, status, error_message, created_at) "
        f"VALUES ('{case.task_name}', 'replace', '{escaped}', 'pending', '', CURRENT_TIMESTAMP(6))"
    )


class DmReplaceReferenceMockAgent(MockLLMAgent):
    """Keep the scripted reference path's SQL control action synchronous."""

    _ACTION_STATUS_QUERY = (
        "SELECT action_id, status, error_message FROM dm_actions "
        "ORDER BY action_id DESC LIMIT 1"
    )

    def __init__(self, case, **kwargs):
        super().__init__(**kwargs)
        self.case = case

    def execute(self, api, args, *, thinking="", source="", action_id=None):
        result = super().execute(api, args, thinking=thinking, source=source, action_id=action_id)
        sql = str(args.get("sql_query", ""))
        if api != "execute_sql" or args.get("target") != self.case.control_database or "INSERT INTO dm_actions" not in sql:
            return result
        deadline = time.monotonic() + 90.0
        while time.monotonic() < deadline:
            status_result = super().execute(
                "execute_sql",
                {"target": self.case.control_database, "sql_query": self._ACTION_STATUS_QUERY},
                source="reference_wait",
            )
            if status_result["status"] == "error":
                raise RuntimeError(f"DM reference action status query failed: result={status_result!r}")
            rows = status_result["result"]
            if len(rows) != 1:
                raise RuntimeError(f"DM reference action status expected one row: rows={rows!r}")
            action_id, status, error_message = rows[0]
            if status == "completed":
                return result
            if status == "error":
                raise RuntimeError(
                    f"DM reference action failed: action_id={action_id!r}, error={error_message!r}"
                )
            if status not in {"pending", "processing"}:
                raise RuntimeError(
                    f"DM reference action has unexpected status: action_id={action_id!r}, status={status!r}"
                )
            time.sleep(0.1)
        raise RuntimeError("DM reference action timed out after 90 seconds")


def build_mock_responses(case):
    source = case.source_database
    control = case.control_database
    archive = case.archive_database
    target = f"{case.db}.{case.table}"
    return [
        {
            "thinking": "Discover the live SQL connection surfaces before choosing any execute_sql target.",
            "actions": [{"api": "help", "args": {"tool_name": "execute_sql"}}],
        },
        {
            "thinking": "Inspect the migration task, source schema, downstream schema, worker log, and live workload before choosing a DDL action.",
            "actions": [
                {"api": "execute_sql", "args": {"target": control, "sql_query": "SELECT * FROM dm_task_status ORDER BY task_name"}},
                {"api": "execute_sql", "args": {"target": control, "sql_query": "SELECT event_id, task_name, source_id, event_type, status, error_message FROM dm_binlog_events ORDER BY event_id"}},
                {"api": "execute_sql", "args": {"target": source, "sql_query": f"SHOW CREATE TABLE {case.table}"}},
                {"api": "execute_sql", "args": {"target": source, "sql_query": (
                    f"SELECT id, account_id, amount_cents, {case.first_column}, {case.second_column} "
                    f"FROM {case.table} WHERE id IN ({case.pending_row_id}, {case.second_pending_row_id}) ORDER BY id"
                )}},
                {"api": "execute_sql", "args": {"sql_query": f"SHOW CREATE TABLE {target}"}},
                {"api": "execute_sql", "args": {"sql_query": f"SHOW CREATE TABLE {archive}.{case.table}"}},
                {"api": "query_metrics", "args": {"metric_type": "qps"}},
                {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
                {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
                {"api": "execute_sql", "args": {"target": control, "sql_query": "SELECT level, message FROM dm_worker_logs ORDER BY log_id DESC LIMIT 40"}},
            ],
        },
        {
            "thinking": "The first failed DDL is safe to replace as two statements; submit that repair through the active migration task.",
            "actions": [{"api": "execute_sql", "args": {"target": control, "sql_query": _dm_action_sql(case, case.replacement_sql)}}],
        },
        {
            "thinking": "Observe the asynchronous DM action and the active task before choosing the next repair.",
            "actions": [
                {"api": "execute_sql", "args": {"target": control, "sql_query": "SELECT action_id, action, status, error_message FROM dm_actions ORDER BY action_id DESC LIMIT 4"}},
                {"api": "execute_sql", "args": {"target": control, "sql_query": "SELECT * FROM dm_task_status ORDER BY task_name"}},
                {"api": "execute_sql", "args": {"target": control, "sql_query": "SELECT event_id, task_name, source_id, event_type, status, error_message FROM dm_binlog_events ORDER BY event_id"}},
            ],
        },
        {
            "thinking": "The active task has advanced through the first replacement and exposed the second release DDL; submit its column-specific replacement.",
            "actions": [{"api": "execute_sql", "args": {"target": control, "sql_query": _dm_action_sql(case, case.second_replacement_sql)}}],
        },
        {
            "thinking": "Observe the second asynchronous DM action before checking the final business state.",
            "actions": [
                {"api": "execute_sql", "args": {"target": control, "sql_query": "SELECT action_id, action, status, error_message FROM dm_actions ORDER BY action_id DESC LIMIT 4"}},
                {"api": "execute_sql", "args": {"target": control, "sql_query": "SELECT * FROM dm_task_status ORDER BY task_name"}},
                {"api": "execute_sql", "args": {"target": control, "sql_query": "SELECT event_id, task_name, source_id, event_type, status, error_message FROM dm_binlog_events ORDER BY event_id"}},
            ],
        },
        {
            "thinking": "Verify the active task and business aggregate, then submit the structured outcome report.",
            "actions": [
                {"api": "execute_sql", "args": {"target": control, "sql_query": "SELECT * FROM dm_task_status ORDER BY task_name"}},
                {"api": "execute_sql", "args": {"sql_query": f"SELECT COUNT(*), SUM(id), SUM(account_id), SUM(amount_cents), SUM({case.first_column}) FROM {target}"}},
                {"api": "execute_sql", "args": {"target": source, "sql_query": f"SELECT COUNT(*), SUM(id), SUM(account_id), SUM(amount_cents), SUM({case.first_column}) FROM {case.table}"}},
                {"api": "execute_sql", "args": {"sql_query": f"SHOW CREATE TABLE {target}"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"SELECT id, account_id, amount_cents, {case.first_column}, {case.second_column} FROM {target} "
                    f"WHERE id IN ({case.pending_row_id}, {case.second_pending_row_id}) ORDER BY id"
                )}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]


MOCK_RESPONSES = build_mock_responses(CASE)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the TiDB BC06 DM failed-DDL replacement scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=["mock", "llm"], default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=35)
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--container-name", default="tidb-business-change-dm-replace")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="off")
    args = parser.parse_args()

    case = SCENARIO.get_case(args.case)
    env = TiDBBusinessChangeEnv(
        run_id=args.container_name,
        port_base=args.port,
        return_window_seconds=300,
        image_group_key=case.runtime.image_group_key,
    )
    if args.mode == "mock":
        agent = DmReplaceReferenceMockAgent(
            case,
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA responsible for safe business migration operations.",
            use_native_tools=False,
        )
        agent.set_mock_responses(build_mock_responses(case))
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)

    result = Orchestrator(
        env,
        SCENARIO,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (None, True, True):
            raise RuntimeError(f"BC06 mock must pass N/A/True/True, observed={observed!r}, result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
