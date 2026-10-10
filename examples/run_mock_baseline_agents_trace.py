"""Run scripted DBot/DBAIOps MockAgents and export trace logs.

This demo does not start Docker or call a real LLM. It exercises the real
baseline agent control paths against a lightweight mock environment, then
exports the same visualization trace format used by normal runs.
"""

import json
import os
import sys
from dataclasses import dataclass

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.baselines.dbaiops.agent import MockDbaiopsAgent
from src.agents.baselines.dbot.agent import MockDbotAgent
from src.scenarios.evaluation.base import BaseEvaluator
from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.outcome import SqlScalarVerifier
from src.scenarios.evaluation.protocol import structured_reference_report
from src.scenarios import BaseScenario
from src.scenarios.base import (
    DatabaseSystem,
    EMPTY_BACKGROUND_WORKLOAD,
    PostgresScenarioCase,
)
from src.scenarios.runtime.orchestrator import Orchestrator
from src.visualization.exporter import export_run_trace


GRAPH_PATH = os.path.join(
    project_root, "data", "knowledge_graph", "pg_experience_graph.json"
)
TRACE_DIR = os.path.join(project_root, "logs", "traces", "mock_baselines")


class MockMissingIndexForOrdersCustomerIdEvaluatorCase(BaseEvaluator):
    scenario_id = "mock_missing_index"
    case_id = "orders_customer_id"
    diagnosis_conditions = (
        condition("missing_index", "missing index", "missing_index", critical=True),
    )
    outcome_verifiers = (
        SqlScalarVerifier(
            "orders_customer_index_exists",
            lambda case: "SELECT count(*) FROM pg_indexes WHERE tablename='orders' AND indexdef ILIKE '%customer_id%'",
            1,
            lambda actual, case: int(actual) == 1,
        ),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class MockMissingIndexForOrdersCustomerIdScenarioCase(PostgresScenarioCase):
    pass


class MockMissingIndexScenario(BaseScenario):
    system = DatabaseSystem.POSTGRESQL
    scenario_id = "mock_missing_index"
    description = "Slow query detected, full table scan on orders table."
    cases = (MockMissingIndexForOrdersCustomerIdScenarioCase(
        case_id="orders_customer_id",
        case_no=0,
        evaluator=MockMissingIndexForOrdersCustomerIdEvaluatorCase,
        title=description,
        alert=(
            "P1 Alert: slow query detected with full table scan on orders. "
            "Please diagnose the missing index root cause and restore performance."
        ),
        initial_state={"status": "degraded"},
        expected_target={"status": "recovered"},
        background_workload=EMPTY_BACKGROUND_WORKLOAD,
        reference_report=structured_reference_report(
            case_id="orders_customer_id",
            factors=("missing index on orders.customer_id",),
            changes=("CREATE INDEX idx_orders_customer_id ON orders(customer_id)",),
            verification=(
                "pg_indexes shows an index on orders covering customer_id",
            ),
            summary=(
                "Slow orders queries full-scan the table because customer_id has "
                "no index; creating the index restores performance."
            ),
        ),
    ),)

    def build_fault_plan(self, case):
        return ()


class MockTraceEnv:
    def __init__(self):
        self.metric_calls = {}
        self.index_created = False

    def deploy(self):
        print("[MockTraceEnv] deploy skipped")

    def teardown(self):
        print("[MockTraceEnv] teardown skipped")

    def configure_case(self, case) -> None:
        pass

    def base_snapshot_name(self, case):
        return None

    def snapshot_name(self, scenario_id, case):
        return None

    def select_tool_profile(self, tool_profile: str) -> None:
        self.tool_profile = tool_profile

    def build_tool_instructions(self, use_native_tools: bool = False):
        return "Use query_metrics, execute_sql, manage_instance, and submit."

    def get_tool_schemas(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "query_metrics",
                    "description": "Query metrics",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "metric_type": {"type": "string"},
                            "target": {"type": "string"},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_sql",
                    "description": "Execute SQL",
                    "parameters": {
                        "type": "object",
                        "properties": {"sql_query": {"type": "string"}},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_instance",
                    "description": "Manage instance",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"},
                            "target": {"type": "string"},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "submit",
                    "description": "Submit",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
        ]

    def help(self, tool_name=None):
        return json.dumps({"status": "success", "tool": tool_name or "all"})

    def execute_action(self, api, args):
        if api == "query_metrics":
            metric_type = args.get("metric_type", "unknown")
            self.metric_calls[metric_type] = self.metric_calls.get(metric_type, 0) + 1
            value = self._metric_value(metric_type)
            return json.dumps({
                "status": "success",
                "metric": metric_type,
                "data": {metric_type: value},
                "value": value,
            })
        if api == "execute_sql":
            sql = args.get("sql_query", "")
            upper_sql = sql.upper()
            if "CREATE INDEX" in upper_sql:
                self.index_created = True
                result = "CREATE INDEX"
            elif "FROM PG_INDEXES" in upper_sql:
                result = [[1 if self.index_created else 0]]
            elif "EXPLAIN" in upper_sql:
                result = [
                    {
                        "QUERY PLAN": (
                            "Seq Scan on orders "
                            "Filter: (customer_id = 42)"
                        )
                    }
                ]
            else:
                result = [{"rows": 1}]
            return json.dumps({
                "status": "success",
                "sql": sql,
                "result": result,
            })
        if api == "manage_instance":
            return json.dumps({"status": "success", "action": args.get("action")})
        return json.dumps({"status": "success", "api": api})

    def execute_sql(self, sql_query):
        return self.execute_action("execute_sql", {"sql_query": sql_query})

    def _metric_value(self, metric_type):
        count = self.metric_calls.get(metric_type, 1)
        if metric_type == "slow_queries":
            return 12.0
        if metric_type == "cpu":
            return 55.0
        return float(count)


def run_agent(agent, label, max_turns=8):
    print("\n" + "=" * 80)
    print(f"Running {label}")
    print("=" * 80)

    scenario = MockMissingIndexScenario()
    orchestrator = Orchestrator(
        env=MockTraceEnv(),
        scenario=scenario,
        case=scenario.get_case("orders_customer_id"),
        agent=agent,
        pretty_print=False,
        max_turns=max_turns,
    )
    orchestrator.run()
    filepath = export_run_trace(orchestrator, output_dir=TRACE_DIR)
    summarize_trace(filepath)
    return filepath


def summarize_trace(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        trace = json.load(f)

    event_types = sorted({event["type"] for event in trace.get("internal_events", [])})
    first_turn = trace.get("turns", [{}])[0]
    first_result = first_turn.get("results", [{}])[0]
    structure = trace.get("diagnostic_structure", {})

    print(f"Trace: {filepath}")
    print(f"Schema: {trace.get('$schema')}")
    print(f"Agent: {trace['metadata'].get('agent_type')}")
    print(f"Turns: {len(trace.get('turns', []))}")
    print(f"Structure: {structure.get('type')}")
    if structure.get("type") == "tree":
        tree = structure["tree"]
        snapshots = structure["tree_snapshots"]
        print(f"Tree root: {tree['root']['id']}")
        print(f"Best path: {tree['best_path']}")
        print(f"Tree snapshot reasons: {[s['reason'] for s in snapshots]}")
    print(f"Conversation history entries: {len(trace.get('conversation_history', []))}")
    print(f"Internal event types: {', '.join(event_types)}")
    print("First result:")
    print(json.dumps(first_result, ensure_ascii=False, indent=2)[:1000])


def main():
    os.makedirs(TRACE_DIR, exist_ok=True)
    dbot_trace = run_agent(
        MockDbotAgent(max_scoring_rounds=1, max_no_discovery=3),
        "MockDbotAgent",
    )
    dbaiops_trace = run_agent(
        MockDbaiopsAgent(
            graph_path=GRAPH_PATH,
            max_evolution_depth=1,
            top_k=1,
        ),
        "MockDbaiopsAgent",
    )
    print("\nGenerated traces:")
    print(dbot_trace)
    print(dbaiops_trace)


if __name__ == "__main__":
    main()
