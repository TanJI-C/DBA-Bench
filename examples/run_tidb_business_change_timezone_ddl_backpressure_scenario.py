import argparse
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import StructuredReport
from src.scenarios.tidb import TidbBusinessChangeTimezoneDdlBackpressureScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


SCENARIO = TidbBusinessChangeTimezoneDdlBackpressureScenario()
CASE = SCENARIO.get_case("dr_cutover_timezone_ddl_and_sink_backpressure")


PASS_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "timezone_sensitive_ddl",
                "factor": "timezone_sensitive_ddl",
                "entity": "timezone_sensitive_ddl",
                "evidence": ["TiCDC log exposed one downstream DDL rejection and its failed commit TSO."],
            },
            {
                "type": "checkpoint_resolved_split",
                "factor": "checkpoint_resolved_split",
                "entity": "checkpoint_resolved_split",
                "evidence": ["The control-plane state stayed normal while checkpoint stopped at the failed DDL and resolved progress advanced."],
            },
            {
                "type": "failed_commit_epoch",
                "factor": "failed_commit_epoch",
                "entity": "failed_commit_epoch",
                "evidence": ["The unique failed DDL CommitTs defined the first safe recovery TSO."],
            },
            {
                "type": "downstream_sink_backpressure",
                "factor": "downstream_sink_backpressure",
                "entity": "downstream_sink_backpressure",
                "evidence": ["SHOW TRIGGERS distinguished the slow write trigger on the replicated business table from the healthy archive trigger."],
            },
            {
                "type": "post_ddl_data_risk",
                "factor": "post_ddl_data_risk",
                "entity": "post_ddl_data_risk",
                "evidence": ["The recovery preserved business rows committed after the failed DDL and the fixed live-writer row."],
            },
            {
                "type": "scope_exclusion",
                "factor": "scope_exclusion",
                "entity": "scope_exclusion",
                "evidence": ["The healthy topology and archive neighbor were excluded from the root cause."],
            },
        ]
    },
    "outcome": {
        "changes": [
            "created the equivalent downstream timestamp DDL",
            "recreated the same changefeed immediately after the observed failed DDL commit TSO",
            "removed the slow write behavior from the replicated business table",
        ],
        "verification": [
            "the changefeed returned NORMAL with resolved progress caught up from the required recovery epoch",
            "the downstream DDL and complete business rows matched the source",
        ],
    },
    "summary": "The recovery separated the downstream DDL compatibility issue from real business-table sink backpressure and preserved all cutover-window rows.",
}
StructuredReport.from_mapping(PASS_REPORT)


def _require_success(result: dict, operation: str) -> dict:
    if result.get("status") != "success":
        raise RuntimeError(f"timezone-ddl mock operation failed: operation={operation!r}, result={result!r}")
    return result


class TimezoneDdlMockLLMAgent(MockLLMAgent):
    """A live-environment reference path with no hidden injector state."""

    def __init__(self, case, **kwargs):
        super().__init__(**kwargs)
        self.case = case

    def _call(self, api: str, args: dict, thinking: str) -> dict:
        response = {
            "thinking": thinking,
            "action": {"api": api, "args": args},
        }
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

    @staticmethod
    def _commit_ts(log_content: str) -> int:
        matches = sorted(set(re.findall(
            r'(?:\\?"CommitTs\\?"\s*:\s*|commitTs=)(\d+)',
            log_content,
            flags=re.IGNORECASE,
        )))
        if len(matches) != 1:
            raise RuntimeError(f"timezone-ddl mock expected one failed DDL CommitTs: matches={matches!r}")
        return int(matches[0])

    def _wait_for_replication(self) -> dict:
        deadline = time.monotonic() + 120
        last = None
        projection = "id, amount, state, updated_at, note"
        while time.monotonic() < deadline:
            result = self._call(
                "manage_cluster",
                {"resource": "changefeed", "operation": "get", "target": self.case.changefeed_id},
                "Wait for the recreated changefeed to become normal and catch up.",
            )
            if result.get("status") == "success":
                status = result["result"]
                checkpoint = int(status.get("checkpoint_tso", 0))
                resolved = int(status.get("resolved_tso", 0))
                if (
                    str(status.get("state", "")).casefold() == "normal"
                    and not status.get("error")
                    and checkpoint > 0
                    and resolved >= checkpoint
                ):
                    source_result = _require_success(
                        self._call(
                            "execute_sql",
                            {"sql_query": f"SELECT {projection} FROM {self.case.source_db}.{self.case.source_table}"},
                            "Check that the source includes all post-DDL business changes before declaring catch-up.",
                        ),
                        "read source business checksum while waiting",
                    )
                    downstream_result = _require_success(
                        self._call(
                            "execute_sql",
                            {"sql_query": f"SELECT {projection} FROM {self.case.source_db}.{self.case.source_table}", "target": "downstream"},
                            "Check that the downstream sink has applied all post-DDL business changes before declaring catch-up.",
                        ),
                        "read downstream business checksum while waiting",
                    )
                    source_rows = source_result.get("result", [])
                    downstream_rows = downstream_result.get("result", [])
                    source_rows = [tuple(str(value) for value in row) for row in source_rows]
                    downstream_rows = [tuple(str(value) for value in row) for row in downstream_rows]
                    required_ids = {
                        *range(1, self.case.seeded_rows + 1),
                        *range(self.case.post_fault_start_id, self.case.post_fault_end_id + 1),
                        self.case.live_writer_id,
                    }
                    if (
                        {int(row[0]) for row in source_rows}.issuperset(required_ids)
                        and source_rows == downstream_rows
                    ):
                        return status
                    last = {
                        "status": status,
                        "source_checksum": source_rows,
                        "downstream_checksum": downstream_rows,
                    }
                else:
                    last = status
            time.sleep(2)
        raise RuntimeError(f"timezone-ddl mock replication did not catch up: last_status={last!r}")

    def _search_knowledge_hops(self) -> None:
        for hop in self.case.knowledge_contract["hops"]:
            result = _require_success(
                self._call(
                    "search_knowledge",
                    {
                        "query": hop["query"],
                        "source_scope": "self_managed",
                        "kb_type": hop["kb_type"],
                        "component": hop["component"],
                        "top_k": 3,
                    },
                    f"Use version-bound TiDB knowledge for {hop['hop_id']}: {hop['knowledge_question']}",
                ),
                f"search unified TiDB knowledge {hop['hop_id']}",
            )
            if int(result.get("count", 0)) < 1:
                raise RuntimeError(
                    f"timezone-ddl unified knowledge returned no result for {hop['hop_id']}: "
                    f"query={hop['query']!r}, kb_type={hop['kb_type']!r}, component={hop['component']!r}"
                )
            content = "\n".join(
                str(row.get("content", ""))
                for row in result.get("results", [])
            ).casefold()
            missing_markers = [
                marker
                for marker in hop["retrieval_markers"]
                if str(marker).casefold() not in content
            ]
            if missing_markers:
                raise RuntimeError(
                    f"timezone-ddl unified knowledge returned semantically incomplete results for {hop['hop_id']}: "
                    f"query={hop['query']!r}, missing_markers={missing_markers!r}, "
                    f"titles={[row.get('title') for row in result.get('results', [])]!r}"
                )

    def solve(self):
        self._call(
            "query_metrics",
            {"metric_type": "qps"},
            "Check whether source write throughput continues while replication freshness is behind.",
        )
        self._call(
            "execute_sql",
            {
                "sql_query": (
                    f"SELECT id, amount, state, updated_at, note FROM "
                    f"{self.case.source_db}.{self.case.source_table} ORDER BY id DESC LIMIT 10"
                )
            },
            "Check the newest source business rows before correlating them with replication progress.",
        )
        log_result = _require_success(
            self._call(
                "read_log",
                {"target": "ticdc/ticdc-0", "lines": 200},
                "Read the first TiCDC log page and locate the exact failed DDL CommitTs.",
            ),
            "read first TiCDC log page",
        )
        log_pages = [log_result["content"]]
        next_line = int(log_result["end_line"]) + 1
        total_lines = int(log_result["total_lines"])
        while next_line <= total_lines:
            page = _require_success(
                self._call(
                    "read_log",
                    {
                        "target": "ticdc/ticdc-0",
                        "start_line": next_line,
                        "end_line": min(next_line + 199, total_lines),
                    },
                    "Read the next TiCDC log page to complete the failed DDL evidence.",
                ),
                "read TiCDC log page",
            )
            log_pages.append(page["content"])
            next_line = int(page["end_line"]) + 1
        commit_ts = self._commit_ts("\n".join(log_pages))
        self._expected_start_ts = commit_ts + 1
        self._search_knowledge_hops()
        _require_success(
            self._call(
                "manage_cluster",
                {"resource": "changefeed", "operation": "get", "target": self.case.changefeed_id},
                "Observe the target changefeed checkpoint, resolved progress, and control-plane state before repair.",
            ),
            "observe stalled changefeed before repair",
        )
        self._call(
            "execute_sql",
            {"sql_query": f"SHOW CREATE TABLE {self.case.source_db}.{self.case.ddl_table}"},
            "Confirm the upstream DDL definition and its UTC session context.",
        )
        self._call(
            "execute_sql",
            {"sql_query": "SELECT @@session.time_zone, @@global.time_zone"},
            "Confirm the upstream session timezone used by the DDL.",
        )
        self._call(
            "execute_sql",
            {"sql_query": f"SHOW CREATE TABLE {self.case.source_db}.{self.case.source_table}", "target": "downstream"},
            "Confirm that the downstream sink is the affected MySQL target.",
        )
        self._call(
            "execute_sql",
            {"sql_query": "SELECT @@session.time_zone, @@global.time_zone, @@system_time_zone", "target": "downstream"},
            "Confirm the downstream MySQL timezone that rejects the replicated lower-bound default.",
        )
        trigger_result = _require_success(
            self._call(
                "execute_sql",
                {"sql_query": f"SHOW TRIGGERS FROM {self.case.source_db}", "target": "downstream"},
                "Compare all downstream triggers and identify the slow write trigger on the affected business table.",
            ),
            "inspect downstream sink triggers",
        )
        trigger_rows = trigger_result.get("result", [])
        slow_rows = [
            row
            for row in trigger_rows
            if len(row) >= 4
            and str(row[2]).casefold() == self.case.source_table.casefold()
            and re.search(r"\bSLEEP\s*\(", str(row[3]), re.IGNORECASE)
        ]
        archive_rows = [
            row
            for row in trigger_rows
            if len(row) >= 4
            and str(row[2]).casefold() == self.case.archive_table.casefold()
            and not re.search(r"\bSLEEP\s*\(", str(row[3]), re.IGNORECASE)
        ]
        if len(slow_rows) != 1 or len(archive_rows) != 1:
            raise RuntimeError(
                "timezone-ddl mock expected one slow business trigger and one healthy archive trigger: "
                f"slow_rows={slow_rows!r}, archive_rows={archive_rows!r}, rows={trigger_rows!r}"
            )
        self._call(
            "execute_sql",
            {
                "sql_query": (
                    f"CREATE TABLE {self.case.source_db}.{self.case.ddl_table} ("
                    f"id BIGINT PRIMARY KEY, {self.case.ddl_column} TIMESTAMP NOT NULL "
                    "DEFAULT '1970-01-01 08:00:01')"
                ),
                "target": "downstream",
            },
            "Create the equivalent downstream TIMESTAMP default in the +08:00 sink timezone.",
        )
        _require_success(
            self._call(
                "manage_cluster",
                {
                    "resource": "changefeed",
                    "operation": "recreate",
                    "target": self.case.changefeed_id,
                    "parameters": {"start_ts": commit_ts + 1},
                },
                "Recreate the same changefeed from the first safe TSO after the observed failed DDL.",
            ),
            "skip failed DDL",
        )
        _require_success(
            self._call(
                "execute_sql",
                {"sql_query": f"DROP TRIGGER IF EXISTS {self.case.source_db}.{self.case.business_trigger}", "target": "downstream"},
                "Remove the slow write behavior from the affected business table after confirming its scope.",
            ),
            "remove business slow-write trigger",
        )
        self._wait_for_replication()
        self._call(
            "manage_cluster",
            {"resource": "changefeed", "operation": "get", "target": self.case.changefeed_id},
            "Record the recovered changefeed state as agent-visible evidence.",
        )
        projection = "id, amount, state, updated_at, note"
        _require_success(
            self._call(
                "execute_sql",
                {"sql_query": f"SELECT {projection} FROM {self.case.source_db}.{self.case.source_table} ORDER BY id"},
                "Verify the complete source business rows include the post-DDL and live-writer rows.",
            ),
            "verify final source business rows",
        )
        _require_success(
            self._call(
                "execute_sql",
                {"sql_query": f"SELECT {projection} FROM {self.case.source_db}.{self.case.source_table} ORDER BY id", "target": "downstream"},
                "Verify the complete downstream business rows match the source.",
            ),
            "verify final downstream business rows",
        )
        archive_projection = "id, tenant_id, amount, updated_at, note"
        _require_success(
            self._call(
                "execute_sql",
                {"sql_query": f"SELECT {archive_projection} FROM {self.case.source_db}.{self.case.archive_table} ORDER BY id"},
                "Verify the source archive truth remains unchanged.",
            ),
            "verify final source archive rows",
        )
        _require_success(
            self._call(
                "execute_sql",
                {"sql_query": f"SELECT {archive_projection} FROM {self.case.source_db}.{self.case.archive_table} ORDER BY id", "target": "downstream"},
                "Verify the downstream archive truth remains unchanged.",
            ),
            "verify final downstream archive rows",
        )
        _require_success(
            self._call(
                "execute_sql",
                {"sql_query": f"SHOW TRIGGERS FROM {self.case.source_db}", "target": "downstream"},
                "Verify the archive audit trigger remains and the business slow-write trigger is gone.",
            ),
            "verify final trigger scope",
        )
        return {"report": PASS_REPORT}


def main():
    parser = argparse.ArgumentParser(description="Run the TiDB timezone-ddl bounded scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in SCENARIO.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--max-output-tokens", type=int)
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--container-name", default="tidb-timezone-ddl")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off"), default="auto")
    args = parser.parse_args()

    case = SCENARIO.get_case(args.case)
    run_id = os.environ.get("AIOPS_RUN_ID", args.container_name.removeprefix("aiopsbench-"))
    env = TiDBEnv(
        run_id=run_id,
        port_base=args.port,
        return_window_seconds=300,
    )
    if args.mode == "mock":
        agent = TimezoneDdlMockLLMAgent(
            case,
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB disaster-recovery DBA.",
            use_native_tools=False,
        )
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
        SCENARIO,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (True, True, True):
            raise RuntimeError(f"timezone-ddl mock must pass DP/OP/SP, observed={observed!r}, result={result!r}")
    print(f"Final result: {json.dumps(result, ensure_ascii=False, default=str)}")


if __name__ == "__main__":
    main()
