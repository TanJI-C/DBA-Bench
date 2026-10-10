import argparse
import copy
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb import TidbBusinessChangeDrAutoSyncFailoverScenario


SCENARIO = TidbBusinessChangeDrAutoSyncFailoverScenario()


def _action(api, args):
    return {"api": api, "args": args}


class K09ReferenceMockAgent(MockLLMAgent):
    """Reference driver; Store IDs are still read from the live topology result."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.primary_store_ids = []

    def execute(self, api, args, *, thinking="", source="", action_id=None):
        actual_args = copy.deepcopy(args)
        if (
            api == "manage_cluster"
            and actual_args.get("resource") == "dr_replication"
            and actual_args.get("operation") == "transition"
            and actual_args.get("parameters", {}).get("failed_store_ids") == "$PRIMARY_STORE_IDS"
        ):
            actual_args["parameters"]["failed_store_ids"] = list(self.primary_store_ids)
        result = super().execute(api, actual_args, thinking=thinking, source=source, action_id=action_id)
        if (
            api == "manage_cluster"
            and actual_args.get("resource") == "dr_replication"
            and actual_args.get("operation") == "topology"
        ):
            stores = result["result"]["stores"]
            self.primary_store_ids = [
                int(store["id"])
                for store in stores
                    if store["labels"].get("zone") == "primary"
                ]
        return result

    def _wait_for_drained_endpoint(self, endpoint: str, timeout_seconds: float = 120.0):
        """Drain 后有界轮询 fence 观测，直到旧 primary 活跃连接归零。"""
        deadline = time.monotonic() + timeout_seconds
        while True:
            fence = super().execute(
                "manage_cluster",
                {"resource": "dr_replication", "operation": "fence_get"},
                source="reference_drain_wait",
            )
            routers = fence["result"]["routers"]
            drained = all(
                endpoint in status["draining"]
                and status["active_connections"].get(endpoint, 0) == 0
                for status in routers.values()
            )
            if drained:
                return fence
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "K09 reference drain did not reach zero active connections: "
                    f"endpoint={endpoint!r}, routers={routers!r}"
                )
            time.sleep(2.0)


def _planned_responses(case):
    return [
        {
            "thinking": "Observe the product mode, Store labels, placement, live endpoint and business markers before changing anything.",
            "actions": [
                _action("manage_cluster", {"resource": "service", "operation": "list"}),
                _action("manage_cluster", {"resource": "dr_replication", "operation": "get"}),
                _action("manage_cluster", {"resource": "dr_replication", "operation": "topology"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "SELECT COUNT(*), SUM(amount_cents) FROM k09_dr.ledger_markers"}),
                _action("search_knowledge", {"query": "TiDB 8.1 DR Auto-Sync sync async sync-recover Region replication versus PD Leader TSO", "source_scope": "self_managed", "top_k": 5, "kb_type": "diagnosis", "component": "pd"}),
            ],
        },
        {
            "thinking": "Use a distributing business router, drain the old primary, then wait for its active connections to disappear.",
            "actions": [
                _action("manage_cluster", {"resource": "router", "operation": "update", "target": "k09-business-router", "parameters": {"policy": "round_robin"}}),
                _action("manage_cluster", {"resource": "router", "operation": "drain", "target": case.primary_endpoint}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "SELECT SLEEP(5)"}),
                _action("manage_cluster", {"resource": "dr_replication", "operation": "fence_get"}),
                _action("search_knowledge", {"query": "TiDB 8.1 Placement Rules voter learner label constraints old writer drain fence zero connections", "source_scope": "self_managed", "top_k": 5, "kb_type": "architecture", "component": "tikv"}),
            ],
        },
        {
            "thinking": "The old route is fenced and drained. Submit the official planned role exchange rather than only moving a PD leader.",
            "actions": [
                _action("manage_cluster", {"resource": "dr_replication", "operation": "transition", "parameters": {"mode": "planned"}}),
            ],
        },
        {
            "thinking": "Accepted is not terminal; wait for DR Auto-Sync sync and placement convergence.",
            "actions": [
                _action("manage_cluster", {"resource": "dr_replication", "operation": "wait", "parameters": {"mode": "planned"}}),
                _action("search_knowledge", {"query": "TiDB 8.1 DR Auto-Sync accepted terminal convergence bounded endpoint canary business validation", "source_scope": "self_managed", "top_k": 5, "kb_type": "operation", "component": "tidb"}),
            ],
        },
        {
            "thinking": "Verify the final role, endpoint fence, Region replication status, and seed marker truth before submitting.",
            "actions": [
                _action("manage_cluster", {"resource": "dr_replication", "operation": "get"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "SELECT COUNT(*), SUM(amount_cents), BIT_XOR(CRC32(CONCAT_WS('|', marker_id, amount_cents, payload, commit_tso, origin))) FROM k09_dr.ledger_markers"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "SELECT DB_NAME, TABLE_NAME, REPLICATIONSTATUS_STATE, COUNT(*) FROM information_schema.TIKV_REGION_STATUS WHERE DB_NAME='k09_dr' AND TABLE_NAME='ledger_markers' GROUP BY DB_NAME, TABLE_NAME, REPLICATIONSTATUS_STATE"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "INSERT INTO k09_dr.endpoint_fence_canaries (endpoint_name, token) VALUES ('tidb/tidb-1', UUID())"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "SELECT endpoint_name, COUNT(*) FROM k09_dr.endpoint_fence_canaries GROUP BY endpoint_name"}),
                _action("submit", {"report": case.reference_report}),
            ],
        },
    ]


def _unplanned_responses(case):
    return [
        {
            "thinking": "The primary SQL endpoint and primary-AZ Stores are down. Inspect the raw product and business evidence first.",
            "actions": [
                _action("manage_cluster", {"resource": "service", "operation": "list"}),
                _action("manage_cluster", {"resource": "dr_replication", "operation": "get"}),
                _action("manage_cluster", {"resource": "dr_replication", "operation": "topology"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "SELECT COUNT(*), SUM(amount_cents) FROM k09_dr.ledger_markers"}),
                _action("search_knowledge", {"query": "TiDB 8.1 Online Unsafe Recovery all failed Stores accepted terminal Tombstone", "source_scope": "self_managed", "top_k": 5, "kb_type": "recovery", "component": "pd"}),
            ],
        },
        {
            "thinking": "Switch the route to a distributing policy and fence the stopped primary before any promotion request.",
            "actions": [
                _action("manage_cluster", {"resource": "router", "operation": "update", "target": "k09-business-router", "parameters": {"policy": "round_robin"}}),
                _action("manage_cluster", {"resource": "dr_replication", "operation": "fence_apply", "target": case.primary_endpoint}),
                _action("manage_cluster", {"resource": "dr_replication", "operation": "fence_get"}),
            ],
        },
        {
            "thinking": "Read every failed primary Store ID from the current Store evidence and submit the documented unsafe recovery request.",
            "actions": [
                _action("manage_cluster", {"resource": "dr_replication", "operation": "topology"}),
                _action("manage_cluster", {"resource": "dr_replication", "operation": "transition", "parameters": {"mode": "unplanned", "failed_store_ids": "$PRIMARY_STORE_IDS"}}),
                _action("search_knowledge", {"query": "TiDB 8.1 Online Unsafe Recovery complete failed Store scope no healthy Store", "source_scope": "self_managed", "top_k": 5, "kb_type": "recovery", "component": "pd"}),
            ],
        },
        {
            "thinking": "The request is only accepted. Wait for the asynchronous unsafe-recovery terminal output and do not restart Tombstone Stores.",
            "actions": [
                _action("manage_cluster", {"resource": "dr_replication", "operation": "wait", "parameters": {"mode": "unplanned"}}),
                _action("search_knowledge", {"query": "TiDB 8.1 unsafe failover TSO is not RPO proof acknowledged business boundary fence generation ADMIN CHECK TABLE", "source_scope": "self_managed", "top_k": 5, "kb_type": "operation", "component": "tidb"}),
            ],
        },
        {
            "thinking": "Verify failed Store Tombstone state, DR placement, business marker CRC, Region status, and ADMIN CHECK TABLE.",
            "actions": [
                _action("manage_cluster", {"resource": "dr_replication", "operation": "get"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "SELECT COUNT(*), SUM(amount_cents), BIT_XOR(CRC32(CONCAT_WS('|', marker_id, amount_cents, payload, commit_tso, origin))) FROM k09_dr.ledger_markers"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "SELECT DB_NAME, TABLE_NAME, REPLICATIONSTATUS_STATE, COUNT(*) FROM information_schema.TIKV_REGION_STATUS WHERE DB_NAME='k09_dr' AND TABLE_NAME='ledger_markers' GROUP BY DB_NAME, TABLE_NAME, REPLICATIONSTATUS_STATE"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": (
                    f"INSERT INTO {case.database}.{case.handoff_table} "
                    "(failover_mode, endpoint_name, acknowledged_marker_count, acknowledged_amount_sum, acknowledged_crc, fence_generation) "
                    "SELECT 'unplanned', "
                    f"'{case.dr_endpoint}', COUNT(*), COALESCE(SUM(amount_cents), 0), "
                    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', marker_id, amount_cents, payload, commit_tso, origin))), 0), 1 "
                    f"FROM {case.database}.{case.table} WHERE marker_id LIKE 'seed-%'"
                )}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": f"SELECT failover_mode, endpoint_name, acknowledged_marker_count, acknowledged_amount_sum, acknowledged_crc, fence_generation FROM {case.database}.{case.handoff_table}"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "INSERT INTO k09_dr.endpoint_fence_canaries (endpoint_name, token) VALUES ('tidb/tidb-1', UUID())"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "SELECT endpoint_name, COUNT(*) FROM k09_dr.endpoint_fence_canaries GROUP BY endpoint_name"}),
                _action("execute_sql", {"target": case.dr_endpoint, "sql_query": "ADMIN CHECK TABLE k09_dr.ledger_markers"}),
                _action("submit", {"report": case.reference_report}),
            ],
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the TiDB K09 DR Auto-Sync failover scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=8)
    parser.add_argument("--port", type=int, default=4700)
    parser.add_argument("--container-name", default="tidb-k09-dr-auto-sync")
    args = parser.parse_args()
    if args.mode == "llm" and not args.model:
        parser.error("--model is required when --mode=llm")
    case = SCENARIO.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = K09ReferenceMockAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DR Auto-Sync DBA.",
            use_native_tools=False,
        )
        responses = (
            _planned_responses(case)
            if case.failover_mode == "planned"
            else _unplanned_responses(case)
        )
        agent.set_mock_responses(responses)
    else:
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    result = Orchestrator(
        env,
        SCENARIO,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode="off"),
    ).run()
    print(f"Final result: {result}")
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (True, True, True):
            raise RuntimeError(f"K09 reference mock must pass True/True/True: observed={observed!r}, result={result!r}")


if __name__ == "__main__":
    main()
