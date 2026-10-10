import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbSystemFailureSf01Scenario
from src.execution.environment import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


class Sf01FullPassMockAgent(MockLLMAgent):
    """Deterministic reference path that derives both fault targets from live evidence."""

    def __init__(self, case):
        super().__init__(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB distributed-systems DBA.",
            use_native_tools=False,
        )
        self.case = case

    def _reference_action(self, api, args, thinking):
        return self.execute(api, args, thinking=thinking)

    @staticmethod
    def _select_evicted_store_id(inspection):
        if "evict-leader-scheduler" not in inspection["schedulers"]:
            raise RuntimeError(f"SF01 mock expected evict-leader-scheduler: {inspection!r}")
        candidates = []
        for item in inspection["stores"]:
            store = item["store"]
            status = item["status"]
            if store["state_name"] == "Up" and int(status["region_count"]) > 0:
                candidates.append(
                    (int(store["id"]), int(status["leader_count"]), int(status["region_count"]))
                )
        if len(candidates) != 3:
            raise RuntimeError(
                "SF01 mock expected three healthy TiKV stores with Region evidence: "
                f"candidates={candidates!r}"
            )
        ranked = sorted(candidates, key=lambda item: item[1] / item[2])
        best, second = ranked[:2]
        if best[1] * second[2] >= second[1] * best[2]:
            raise RuntimeError(
                "SF01 mock cannot identify a unique evicted TiKV from leader/Region evidence: "
                f"candidates={candidates!r}"
            )
        return best[0]

    @staticmethod
    def _first_row(payload):
        rows = payload["result"]
        if len(rows) != 1:
            raise RuntimeError(f"SF01 mock expected one SQL result row: payload={payload!r}")
        return rows[0]

    @staticmethod
    def _select_faulty_pd_from_logs(logs):
        candidates = []
        for target, payload in logs.items():
            content = payload["content"]
            if any(
                "SF01 phase=storage_flush" in line and "term_epoch=1" in line
                for line in content.splitlines()
            ):
                candidates.append(target)
        if len(candidates) != 1:
            raise RuntimeError(
                "SF01 mock expected exactly one PD with post-term storage flush evidence: "
                f"candidates={candidates!r}, logs={logs!r}"
            )
        return candidates[0]

    @staticmethod
    def _select_scheduler_store_from_logs(logs, stores):
        candidates = []
        for target, payload in logs.items():
            for line in payload["content"].splitlines():
                if "SF01 phase=scheduler_create" not in line or "store_id=" not in line:
                    continue
                store_id = int(
                    next(
                        token.split("=", 1)[1]
                        for token in line.split()
                        if token.startswith("store_id=")
                    )
                )
                candidates.append((target, store_id))
        if len(candidates) != 1:
            raise RuntimeError(
                "SF01 mock expected one raw scheduler-create store identity: "
                f"candidates={candidates!r}, logs={logs!r}"
            )
        store_id = candidates[0][1]
        if store_id not in {int(item["store"]["id"]) for item in stores}:
            raise RuntimeError(
                "SF01 mock scheduler target is absent from the Store observation: "
                f"store_id={store_id!r}, stores={stores!r}"
            )
        return store_id

    def solve(self):
        services_payload = self._reference_action(
            "manage_cluster",
            {"resource": "service", "operation": "list"},
            "Discover stable PD and TiKV service identities before joining control-plane evidence.",
        )
        pd_targets = sorted(
            target
            for target in services_payload["result"]["nodes"]
            if target.startswith("pd/")
        )
        if len(pd_targets) != 3:
            raise RuntimeError(f"SF01 mock expected three PD services: payload={services_payload!r}")
        stores_payload = self._reference_action(
            "manage_cluster",
            {"resource": "store", "operation": "list"},
            "Correlate the live Store states and leader counts before changing anything.",
        )
        scheduler_payload = self._reference_action(
            "manage_cluster",
            {"resource": "scheduler", "operation": "list"},
            "Observe scheduler identities through the generic PD resource interface.",
        )
        schedulers = scheduler_payload["result"]
        if not isinstance(schedulers, list):
            raise RuntimeError(
                "SF01 mock expected manage_cluster scheduler/list to return a scheduler list: "
                f"payload={scheduler_payload!r}"
            )
        inspection = {
            "stores": stores_payload["result"]["stores"],
            "schedulers": schedulers,
        }
        disk = self._reference_action(
            "query_metrics",
            {"metric_type": "disk_io"},
            "Compare raw PD write series with the phase and role evidence; a single maximum is not enough.",
        )
        logs = {
            target: self._reference_action(
                "read_log",
                {
                    "target": target,
                    "lines": 200,
                    "match_key": "SF01 phase=storage_flush",
                },
                "Compare raw PD phase, role, duration, and term markers across the three members.",
            )
            for target in pd_targets
        }
        faulty_target = self._select_faulty_pd_from_logs(logs)
        scheduler_logs = {
            target: self._reference_action(
                "read_log",
                {
                    "target": target,
                    "lines": 200,
                    "match_key": "SF01 phase=scheduler_create",
                },
                "Read the raw scheduler creation record and join its Store identity to the Store observation.",
            )
            for target in pd_targets
        }
        store_id = self._select_scheduler_store_from_logs(scheduler_logs, inspection["stores"])
        store = next(
            item["store"]
            for item in inspection["stores"]
            if int(item["store"]["id"]) == store_id
        )
        store_target = f"tikv/{str(store['address']).split(':', 1)[0]}"
        self._reference_action(
            "manage_cluster",
            {"resource": "region", "operation": "list", "target": store_target},
            "Confirm the scheduler target retained its Regions despite the leader movement.",
        )
        if faulty_target not in disk["series"]:
            raise RuntimeError(
                f"SF01 mock log-selected PD is absent from disk series: target={faulty_target!r}, "
                f"series={sorted(disk['series'])!r}"
            )
        self._reference_action(
            "manage_cluster",
            {
                "resource": "scheduler",
                "operation": "remove",
                "target": f"evict-leader-scheduler/{store_id}",
            },
            "Remove only the observed scheduler attached to the selected healthy TiKV.",
        )
        repaired = self._reference_action(
            "manage_cluster",
            {"resource": "service", "operation": "restart", "target": faulty_target},
            "Restart the affected PD service after preserving the disk evidence.",
        )
        if repaired.get("status") != "success":
            raise RuntimeError(f"SF01 mock disk repair failed: {repaired!r}")
        leader_settled = False
        store_snapshot = []
        for attempt in range(18):
            store_snapshot = self._reference_action(
                "manage_cluster",
                {"resource": "store", "operation": "list"},
                thinking=f"等待 evict-leader-scheduler 移除后 Leader 回迁到被驱逐 Store（第 {attempt + 1} 次观察）。",
            )["result"]["stores"]
            running_store_ids = [
                int(item["store"]["id"])
                for item in store_snapshot
                if item["store"]["state_name"] == "Up"
            ]
            status_by_store = {
                int(item["store"]["id"]): item["status"] for item in store_snapshot
            }
            # The outcome contract requires the evicted Store to recover at least
            # half of its pre-fault leader share. Half of the observed cluster
            # leader total is the tool-visible proxy for that threshold; only the
            # evicted Store's own leaders were drained, so its fair share tracks
            # one third to one half of the total and total//4 stays conservative.
            victim_minimum = max(1, sum(
                int(status["leader_count"]) for status in status_by_store.values()
            ) // 4)
            leader_settled = (
                len(running_store_ids) == 3
                and all(
                    int(status_by_store[store]["leader_count"]) > 0
                    for store in running_store_ids
                )
                and int(status_by_store[store_id]["leader_count"]) >= victim_minimum
            )
            if leader_settled:
                break
            if attempt < 17:
                self._reference_action(
                    "execute_sql",
                    {"sql_query": "SELECT SLEEP(10)"},
                    thinking="Leader 回迁尚未完成，等待下一轮观察，不能带着 0 Leader 的健康 Store 提交。",
                )
        if not leader_settled:
            raise RuntimeError(
                "SF01 mock leader distribution did not converge after scheduler removal: "
                f"stores={store_snapshot!r}"
            )
        self._reference_action(
            "execute_sql",
            {
                "sql_query": (
                    f"INSERT INTO {self.case.db}.{self.case.table} "
                    "(event_id, event_amount, event_state, record_crc, region_code, settlement_day) "
                    f"VALUES ({self.case.insert_row_id},{self.case.insert_amount},'paid',"
                    f"{self.case.insert_crc},'{self.case.insert_region_code}',"
                    f"'{self.case.insert_settlement_day}')"
                )
            },
            "Verify that business writes continue after scheduling recovery.",
        )
        aggregate = self._first_row(
            self._reference_action(
                "execute_sql",
                {
                    "sql_query": (
                        "SELECT COUNT(*), SUM(event_amount), BIT_XOR(record_crc), MAX(event_id) "
                        f"FROM {self.case.db}.{self.case.table} WHERE event_state = 'paid'"
                    )
                },
                "Derive post-write settlement totals from the base business table.",
            )
        )
        self._reference_action(
            "execute_sql",
            {
                "sql_query": (
                    f"UPDATE {self.case.db}.{self.case.reconciliation_table} "
                    f"SET order_count={aggregate[0]}, "
                    f"paid_amount={aggregate[1]}, "
                    f"checksum={aggregate[2]}, "
                    f"last_event_id={aggregate[3]}, status='closed' "
                    "WHERE summary_id=1"
                )
            },
            "Close the settlement summary against the post-write business aggregate.",
        )
        self._reference_action(
            "execute_sql",
            {
                "sql_query": (
                    f"UPDATE {self.case.db}.{self.case.rollup_table} r "
                    f"JOIN (SELECT region_code, COUNT(*) event_count, "
                    "SUM(event_amount) paid_amount, BIT_XOR(record_crc) checksum, "
                    f"MAX(event_id) last_event_id FROM {self.case.db}.{self.case.table} "
                    "WHERE event_state = 'paid' GROUP BY region_code) a "
                    "ON r.region_code = a.region_code "
                    "SET r.event_count=a.event_count, r.paid_amount=a.paid_amount, "
                    "r.checksum=a.checksum, r.last_event_id=a.last_event_id, r.status='closed' "
                    f"WHERE r.region_code IN ({','.join(repr(code) for code in self.case.region_codes)})"
                )
            },
            "Rebuild every region audit rollup row from the base table, not from supplied totals.",
        )
        self._reference_action(
            "execute_sql",
            {
                "sql_query": (
                    f"UPDATE {self.case.db}.{self.case.exceptions_table} "
                    "SET count_delta=0, amount_delta=0, checksum_delta=0, status='closed' "
                    "WHERE status <> 'closed' OR count_delta <> 0 "
                    "OR amount_delta <> 0 OR checksum_delta <> 0"
                )
            },
            "Close and zero the pending reconciliation exceptions after both derived controls match.",
        )
        for table in (
            self.case.table,
            self.case.reconciliation_table,
            self.case.rollup_table,
            self.case.exceptions_table,
        ):
            self._reference_action(
                "execute_sql",
                {"sql_query": f"ADMIN CHECK TABLE {self.case.db}.{table}"},
                f"Run the final TiDB integrity check for {table}.",
            )
        return {"report": self.case.reference_report}


def main():
    scenario = TidbSystemFailureSf01Scenario()
    parser = argparse.ArgumentParser(description="Run TiDB distributed scenario SF01.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=18)
    parser.add_argument("--port", type=int, default=4100)
    parser.add_argument("--container-name", default="aiopsbench-tidb-sf01")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="auto")
    parser.add_argument("--cold-start-timeout", type=int, default=1800)
    parser.add_argument("--warm-start-timeout", type=int, default=300)
    parser.add_argument("--diagnosis-match-mode", choices=("exact", "semantic"), default="exact")
    parser.add_argument("--diagnosis-semantic-model", default=None, help="Diagnosis judge model; defaults to --model")
    parser.add_argument("--diagnosis-semantic-config-path", default=None)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        tidb_readiness_timeout_sec=args.cold_start_timeout,
        warm_tidb_readiness_timeout_sec=args.warm_start_timeout,
    )
    if args.mode == "mock":
        agent = Sf01FullPassMockAgent(case)
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            # protocol remains available for the same structured action loop.
            use_native_tools=not args.no_native_tools,
        )
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
            diagnosis_match_mode=args.diagnosis_match_mode,
            diagnosis_semantic_model=args.diagnosis_semantic_model or args.model,
            diagnosis_semantic_config_path=args.diagnosis_semantic_config_path or args.config_path,
        ),
    ).run()
    print(f"Final result: {json.dumps(result, ensure_ascii=False, default=str)}")


if __name__ == "__main__":
    main()
