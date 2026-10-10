import argparse
import copy
import json
import os
import time

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.tidb import TidbSystemFailureTiCdcGcSafepointScenario
from src.execution.environment import TiDBEnv


SCENARIO = TidbSystemFailureTiCdcGcSafepointScenario()
CASE = SCENARIO.get_case("ticdc_oom_leftover_lock_and_service_safepoint")
StructuredReport.from_mapping(CASE.reference_report)


def _require_success(result: dict, operation: str) -> dict:
    if result.get("status") != "success":
        raise RuntimeError(f"K02 reference operation failed: operation={operation!r}, result={result!r}")
    return result


class K02ReferenceMockAgent(MockLLMAgent):
    """Execute the live reference path through the public Agent gateway."""

    def __init__(self, case, knowledge_mode: str, **kwargs):
        super().__init__(**kwargs)
        self.case = case
        self.knowledge_mode = knowledge_mode

    def _call(self, api: str, args: dict, thinking: str) -> dict:
        response = {"thinking": thinking, "action": {"api": api, "args": args}}
        raw = json.dumps(response, ensure_ascii=False, default=str)
        self._last_llm_output = raw
        self._conversation_history.append({"role": "assistant", "content": raw})
        self.record_action(raw, response["action"])
        result = self.execute(api, args, thinking=thinking)
        self._conversation_history.append({
            "role": "user",
            "content": f"[工具执行结果] {api}: {json.dumps(result, ensure_ascii=False, default=str)}",
        })
        return result

    def _knowledge(self) -> None:
        if self.knowledge_mode == "no-kb":
            return
        queries = (
            (
                "TiCDC ResolvedTS CheckpointTS changefeed state after capture restart",
                "architecture",
                "ticdc",
            ),
            (
                "TiKV MVCC pessimistic lock Write CF Region peer recovery",
                "recovery",
                "tikv",
            ),
            (
                "TiCDC service GC safepoint gc-ttl stopped capture PD owner cleanup",
                "recovery",
                "ticdc",
            ),
            (
                "TiCDC capture ownership changefeed diagnostics and service mapping",
                "observability",
                "ticdc",
            ),
        )
        for query, kb_type, component in queries:
            _require_success(
                self._call(
                    "search_knowledge",
                    {
                        "query": query,
                        "source_scope": "self_managed",
                        "top_k": 4,
                        "kb_type": kb_type,
                        "component": component,
                    },
                    f"Read the {self.knowledge_mode} TiDB knowledge hop before acting on {component} evidence.",
                ),
                f"search {component} knowledge",
            )

    def _ensure_target_capture_running(self, reason: str) -> None:
        state = _require_success(
            self._call(
                "manage_cluster",
                {"resource": "service", "operation": "get", "target": self.case.target_capture},
                reason,
            ),
            "get target capture state",
        )["result"]["state"]
        if not state["running"]:
            _require_success(
                self._call(
                    "manage_cluster",
                    {"resource": "service", "operation": "start", "target": self.case.target_capture},
                    "Start the target TiCDC capture immediately before the bounded cleanup/verification path.",
                ),
                "start target capture",
            )

    def _capture_changefeed_list(self, capture: str) -> list[dict]:
        deadline = time.monotonic() + 180
        result = None
        while time.monotonic() < deadline:
            result = self._call(
                "manage_cluster",
                {"resource": "changefeed", "operation": "list", "target": capture},
                f"List raw changefeed diagnostics from {capture}; wait for the capture API to become ready.",
            )
            if result.get("status") == "success":
                break
            time.sleep(2)
        result = _require_success(result, f"list changefeeds on {capture}")
        changefeeds = result["result"]["changefeeds"]
        if not isinstance(changefeeds, list):
            raise TypeError(f"K02 changefeed list must be an array: capture={capture!r}, result={result!r}")
        return changefeeds

    def _current_tso(self) -> int:
        result = _require_success(
                self._call(
                    "execute_sql",
                    {"sql_query": "BEGIN; SELECT @@tidb_current_ts; ROLLBACK"},
                    "Read the current TSO for the public target-feed catch-up window.",
                ),
            "read current TSO",
        )
        return int(result["result"][0][0])

    def _wait_for_target(self) -> None:
        deadline = time.monotonic() + self.case.catchup_window_seconds
        last = None
        while time.monotonic() < deadline:
            self._ensure_target_capture_running(
                "Check that the target TiCDC capture remains available while waiting for catch-up."
            )
            status = _require_success(
                self._call(
                    "manage_cluster",
                    {"resource": "changefeed", "operation": "get", "target": self.case.target_feed_id, "parameters": {"capture_target": self.case.target_capture}},
                    "Verify target changefeed state, checkpoint, resolved progress, and error after recovery.",
                ),
                "get target changefeed after recovery",
            )["result"]
            last = status
            checkpoint = int(status.get("checkpoint_ts", status.get("checkpoint_tso", 0)))
            resolved = int(status.get("resolved_ts", status.get("resolved_tso", 0)))
            current_tso = self._current_tso()
            lag_seconds = ((current_tso >> 18) - (checkpoint >> 18)) / 1000
            if (
                str(status.get("state", "")).casefold() == "normal"
                and not status.get("error")
                and current_tso >= resolved >= checkpoint > 0
                and lag_seconds <= self.case.catchup_window_seconds
            ):
                source = _require_success(
                    self._call(
                        "execute_sql",
                        {"sql_query": self.case.target_truth_sql},
                        "Read source target count/sum/CRC/post-OOM markers.",
                    ),
                    "read source target truth",
                )["result"]
                downstream = _require_success(
                    self._call(
                        "execute_sql",
                        {"sql_query": self.case.target_truth_sql, "target": "downstream"},
                        "Read downstream target count/sum/CRC/post-OOM markers.",
                    ),
                    "read downstream target truth",
                )["result"]
                if source == downstream and source and int(source[0][3]) > 0:
                    return
            time.sleep(3)
        raise RuntimeError(f"K02 reference target feed did not converge: last={last!r}")

    def _wait_for_gc(self) -> None:
        deadline = time.monotonic() + self.case.gc_owner_release_window_seconds
        last = None
        while time.monotonic() < deadline:
            safepoint = _require_success(
                self._call(
                    "manage_cluster",
                    {"resource": "gc_safepoint", "operation": "list"},
                    "Poll the public GC safepoint owner list until the abandoned feed cleanup releases its safepoint.",
                ),
                "poll service safepoints",
            )["result"]
            status = _require_success(
                self._call(
                    "manage_cluster",
                    {"resource": "gc_status", "operation": "get"},
                    "Poll public GC headroom, disk, compaction, and worker status after feed cleanup.",
                ),
                "poll GC status",
            )["result"]
            last = {"safepoint": safepoint, "status": status}
            workers = [
                owner
                for owner in safepoint["service_gc_safe_points"]
                if str(owner.get("service_id")) == "gc_worker"
            ]
            abandoned_prefix = f"ticdc-{self.case.runtime.replication.ticdc_cluster_ids[1]}-"
            abandoned = [
                owner
                for owner in safepoint["service_gc_safe_points"]
                if str(owner.get("service_id", "")).startswith(abandoned_prefix)
                and "-initializing-" not in str(owner.get("service_id", ""))
                and "-creating-" not in str(owner.get("service_id", ""))
            ]
            initializing = [
                owner
                for owner in safepoint["service_gc_safe_points"]
                if "-initializing-" in str(owner.get("service_id", ""))
            ]
            if len(workers) != 1 or len(abandoned) > 1:
                raise RuntimeError(
                    "K02 reference GC owner observation is not exact: "
                    f"workers={workers!r}, abandoned={abandoned!r}, initializing={initializing!r}, safepoint={safepoint!r}"
                )
            worker_safe_point = int(workers[0]["safe_point"])
            abandoned_released = not abandoned or int(abandoned[0]["safe_point"]) >= worker_safe_point
            if (
                int(safepoint["min_service_gc_safe_point"]) >= worker_safe_point
                and abandoned_released
                and int(status["gc_headroom_seconds"]) <= self.case.gc_headroom_max_seconds
                and int(status["disk_free_bytes"]) >= self.case.disk_free_bytes
                and int(status["compaction_pending"]) <= self.case.compaction_pending_limit
            ):
                return
            time.sleep(3)
        raise RuntimeError(f"K02 reference GC did not converge after abandoned feed cleanup: last={last!r}")

    def solve(self) -> dict:
        self._knowledge()
        _require_success(
            self._call(
                "manage_cluster",
                {"resource": "service", "operation": "list"},
                "List all component runtimes and identify the two TiCDC captures.",
            ),
            "list component runtimes",
        )
        self._ensure_target_capture_running(
            "Confirm that the target capture is the OOM-stopped runtime before starting it."
        )
        target_feeds = self._capture_changefeed_list(self.case.target_capture)
        if not any(str(item.get("id")) == self.case.target_feed_id for item in target_feeds):
            raise RuntimeError(f"K02 target feed was not visible after target capture start: feeds={target_feeds!r}")
        _require_success(
            self._call("manage_cluster", {"resource": "store", "operation": "list"}, "Observe the current PD Store identities before binding a Region scope."),
            "list Stores",
        )
        region_rows = _require_success(
            self._call(
                "execute_sql",
                {"sql_query": f"SELECT REGION_ID FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS WHERE DB_NAME = '{self.case.source_db}' AND TABLE_NAME = '{self.case.target_table}' AND IS_INDEX = 0 ORDER BY REGION_ID"},
                "Find the target table Region from TiDB's Region status view.",
            ),
            "find target Region",
        )["result"]
        if len(region_rows) != 1:
            raise RuntimeError(f"K02 reference expected one target Region: rows={region_rows!r}")
        region_id = int(region_rows[0][0])
        region = _require_success(
            self._call(
                "manage_cluster",
                {"resource": "region", "operation": "get", "target": "tikv/tikv-0", "parameters": {"region_id": region_id}},
                "Read the target Region peers and bind the lock scan to the complete current peer set.",
            ),
            "get target Region",
        )["result"]
        stores = _require_success(
            self._call("manage_cluster", {"resource": "store", "operation": "list"}, "Refresh the Store identity map for the target Region peers."),
            "refresh Stores",
        )["result"]["stores"]
        store_by_id = {
            int(item["store"]["id"]): f"tikv/{str(item['store']['address']).rsplit(':', 1)[0]}"
            for item in stores
        }
        store_targets = [store_by_id[int(peer["store_id"])] for peer in region["peers"]]
        lock_observation = _require_success(
            self._call(
                "manage_cluster",
                {"resource": "mvcc_lock", "operation": "list", "target": f"region/{region_id}", "parameters": {"store_targets": store_targets}},
                "Scan only the observed target Region's full peer Store scope and inspect the versioned recovery boundary.",
            ),
            "list target Region locks",
        )["result"]
        inspection = _require_success(
            self._call(
                "manage_cluster",
                {"resource": "storage_maintenance", "operation": "preflight", "target": f"region/{region_id}", "parameters": {"store_targets": store_targets}},
                "Inspect the fixed-version recovery boundary for the same Region peer scope before resolving the lock.",
            ),
            "inspect target Region recovery boundary",
        )["result"]
        inspection_id = inspection["preflight_id"]
        _require_success(
            self._call(
                "manage_cluster",
                {"resource": "mvcc_lock", "operation": "resolve", "target": f"region/{region_id}", "parameters": {"inspection_id": inspection_id}},
                "Resolve only the lock scope that was observed on every peer of the target Region.",
            ),
            "resolve target Region lock",
        )
        self._ensure_target_capture_running(
            "Restart the target TiCDC capture immediately before abandoned-feed cleanup after lock recovery."
        )
        safepoint = _require_success(
            self._call("manage_cluster", {"resource": "gc_safepoint", "operation": "list"}, "List every PD service GC safepoint owner before cleanup."),
            "list service safepoints",
        )["result"]
        owners = safepoint["service_gc_safe_points"]
        abandoned_cluster_id = self.case.runtime.replication.ticdc_cluster_ids[1]
        abandoned_service_prefix = f"ticdc-{abandoned_cluster_id}-"
        abandoned_matches = [
            owner for owner in owners
            if str(owner.get("service_id", "")).startswith(abandoned_service_prefix)
            and "-initializing-" not in str(owner.get("service_id", ""))
            and "-creating-" not in str(owner.get("service_id", ""))
        ]
        if len(abandoned_matches) != 1:
            raise RuntimeError(f"K02 reference expected one abandoned owner: matches={abandoned_matches!r}")
        _require_success(
            self._call(
                "manage_cluster",
                {
                    "resource": "gc_safepoint",
                    "operation": "remove",
                    "target": abandoned_matches[0]["service_id"],
                    "parameters": {"changefeed_id": self.case.abandoned_feed_id},
                },
                "Delete exactly the observed stale abandoned owner pin so GC can advance while the active, healthy, and backup owners are preserved.",
            ),
            "remove abandoned service safepoint",
        )
        self._wait_for_target()
        self._wait_for_gc()
        _require_success(self._call("manage_cluster", {"resource": "gc_status", "operation": "get"}, "Verify GC headroom, disk, compaction, and GC worker evidence after both repairs."), "get final GC status")
        _require_success(self._call("manage_cluster", {"resource": "gc_safepoint", "operation": "list"}, "Verify the abandoned feed is removed, its owner no longer pins below gc_worker, and protected owners remain."), "verify final service safepoints")
        _require_success(self._call("execute_sql", {"sql_query": self.case.archive_truth_sql}, "Verify the source archive counterfactual remained unchanged."), "verify source archive truth")
        _require_success(self._call("execute_sql", {"sql_query": self.case.archive_truth_sql, "target": "downstream"}, "Verify the downstream archive counterfactual remained unchanged."), "verify downstream archive truth")
        return {"report": copy.deepcopy(self.case.reference_report)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run TiDB K02 TiCDC OOM and GC service safepoint composite fault.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--knowledge-mode", choices=("no-kb", "unified-kb"), default="unified-kb")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=40)
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--port", type=int, default=4700)
    parser.add_argument("--container-name", default="tidb-k02-ticdc-gc-safepoint")
    args = parser.parse_args()
    case = SCENARIO.get_case(args.case)
    run_id = os.environ.get("AIOPS_RUN_ID", args.container_name.removeprefix("aiopsbench-"))
    env = TiDBEnv(run_id=run_id, port_base=args.port, return_window_seconds=300)
    if args.mode == "mock":
        agent = K02ReferenceMockAgent(
            case,
            args.knowledge_mode,
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB disaster-recovery DBA executing a reference path.",
            use_native_tools=False,
        )
    else:
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
            max_output_tokens=args.max_output_tokens,
        )
    result = Orchestrator(
        env,
        SCENARIO,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode="off"),
    ).run()
    if args.mode == "mock" and tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass")) != (True, True, True):
        raise RuntimeError(f"K02 reference Mock must pass DP/OP/SP: result={result!r}")
    print(json.dumps(result, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
