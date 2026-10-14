import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.scenarios.tidb import TidbHealthCheckBackupRecoverabilityScenario
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb.health_check.runtime.backup_recoverability import BackupRecoverabilityEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


def full_pass_report(case) -> dict:
    if case.continuity_only:
        return case.reference_report
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "archive_integrity_failure",
                    "factor": (
                        "the requested checkpoint cannot be reached because the active primary copies of log "
                        "segments A3, A4, A5, A7, and A8 are corrupted while their authorized replicas remain usable"
                    ),
                    "entity": "the selected primary restore chain",
                    "evidence": [
                        "the selected primary object checksum differs from the authorized replica checksum"
                    ],
                },
                {
                    "type": "archive_availability_gap",
                    "factor": (
                        "segment A6 is absent from the replicated archive chain even though its bytes are "
                        "readable and an authorized copy exists, so restore continuity remains broken"
                    ),
                    "entity": "the selected primary restore chain segment A6",
                    "evidence": [
                        "A6 is present=0, replica_status=NOT_REPLICATED, and usable_for_restore=0"
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "repaired all five checksum-invalid archive objects and restored the unreplicated continuity segment",
                "reran the isolated restore validation",
            ],
            "verification": [
                "the latest restore attempt reached the requested checkpoint and completed all critical table checks",
                "all four critical sandbox table checksums matched while production truth stayed unchanged",
            ],
        },
    "summary": "The approved archive chain was repaired and the isolated recovery contract passed.",
    }


class HC04ReferenceMockAgent(MockLLMAgent):
    """Follow the visible HC04 evidence path and derive repair arguments at runtime."""

    def __init__(self, case):
        super().__init__(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA responsible for backup recovery validation.",
            use_native_tools=False,
        )
        self.case = case

    def _turn(self, thinking: str, actions: list[dict]) -> list[dict]:
        response = {"thinking": thinking, "actions": actions}
        raw = json.dumps(response, ensure_ascii=False)
        self._last_llm_output = raw
        self._conversation_history.append({"role": "assistant", "content": raw})
        results = []
        for action in actions:
            api = action["api"]
            args = action.get("args", {})
            self.record_action(raw, {"api": api, "args": args})
            result = self.execute(api, args, thinking=thinking, source="")
            results.append(result)
            self._conversation_history.append(
                {
                    "role": "user",
                    "content": f"[工具执行结果] {api}: {json.dumps(result, ensure_ascii=False, default=str)}",
                }
            )
        return results

    def _submit(self, report: dict) -> dict:
        action = {"api": "submit", "args": {"report": report}}
        response = {"thinking": "Submit the root cause and the verified final state.", "action": action}
        raw = json.dumps(response, ensure_ascii=False)
        self._last_llm_output = raw
        self._conversation_history.append({"role": "assistant", "content": raw})
        self.record_action(raw, action)
        return action["args"]

    def solve(self) -> dict:
        case = self.case
        join_sql = (
            f"SELECT r.request_key, r.selected_backup_id, r.selected_drill_id, r.target_ts, "
            f"r.authorized_source_role, a.source_object_id, a.source_segment, a.source_role, "
            f"a.restore_mode, a.approval_state, a.approved_by "
            f"FROM {case.db}.{case.audit_request_table} r "
            f"JOIN {case.db}.{case.approval_table} a "
            "ON a.request_key = r.request_key AND a.selected_backup_id = r.selected_backup_id "
            "ORDER BY a.approved_at, a.approval_id"
        )
        audit_rows = self._turn(
            "Establish the current validation request and inspect its complete approval history.",
            [{"api": "execute_sql", "args": {"sql_query": join_sql}}],
        )[0]["result"]
        request_key = str(audit_rows[0][0])
        selected_backup_id = str(audit_rows[0][1])
        selected_drill_id = str(audit_rows[0][2])

        catalog_rows = self._turn(
            "Compare the selected request with the unfiltered backup catalog.",
            [{
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"SELECT backup_id, source_role, status, metadata_status, checkpoint_ts, "
                        f"requested_target_ts, latest_recoverable_ts FROM {case.db}.{case.backup_catalog_table} "
                        "ORDER BY backup_id"
                    )
                },
            }],
        )[0]["result"]
        if len([row for row in catalog_rows if str(row[0]) == selected_backup_id]) != 1:
            raise RuntimeError(f"HC04 reference catalog did not identify one selected backup: backup_id={selected_backup_id!r}")

        drill_rows = self._turn(
            "Compare the selected request with the unfiltered restore-drill history.",
            [{
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"SELECT drill_id, backup_id, source_role, target_ts, status, isolated, "
                        f"checkpoint_status, checksum_status FROM {case.db}.{case.restore_drill_table} "
                        "ORDER BY drill_id"
                    )
                },
            }],
        )[0]["result"]
        if len([row for row in drill_rows if str(row[0]) == selected_drill_id]) != 1:
            raise RuntimeError(f"HC04 reference drill did not identify one selected drill: drill_id={selected_drill_id!r}")

        archive = self._turn(
            "Inspect the selected backup's unfiltered objects and segment continuity state.",
            [{"api": "inspect_backup_archive", "args": {"backup_id": selected_backup_id}}],
        )[0]
        fault_segments = tuple(sorted(
            str(row[0]) for row in archive["segments"] if int(row[5]) == 0
        ))
        expected_fault_count = 1 if case.continuity_only else 6
        if len(fault_segments) != expected_fault_count:
            raise RuntimeError(
                "HC04 reference path found an unexpected unusable-segment count: "
                f"expected={expected_fault_count}, segments={fault_segments!r}"
            )
        fault_objects = [
            row
            for row in archive["objects"]
            if str(row[2]) in fault_segments and (str(row[4]) == "CORRUPT" or int(row[6]) == 0)
        ]
        if len(fault_objects) != expected_fault_count:
            raise RuntimeError(
                "HC04 reference path found an unexpected active fault-object count: "
                f"expected={expected_fault_count}, rows={fault_objects!r}"
            )

        self._turn(
            "Cross-check monitoring events and live workload profiles before choosing a repair.",
            [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            f"SELECT event_id, event_time, severity, source, related_backup_id, message "
                            f"FROM {case.db}.{case.monitoring_table} ORDER BY event_id"
                        )
                    },
                },
                {"api": "query_metrics", "args": {"metric_type": "workload_activity"}},
            ],
        )

        approved_rows = [
            row
            for row in audit_rows
            if str(row[1]) == selected_backup_id
            and str(row[6]) in fault_segments
            and str(row[7]) == "primary"
            and str(row[8]) == "isolated"
            and str(row[9]) == "APPROVED"
            and str(row[10]) == "dr-owner"
        ]
        source_by_segment = {str(row[6]): int(row[5]) for row in approved_rows}
        if set(source_by_segment) != set(fault_segments) or len(source_by_segment) != len(fault_segments):
            raise RuntimeError(
                "HC04 reference approval join did not identify one source per fault segment: "
                f"request_key={request_key!r}, source_by_segment={source_by_segment!r}"
            )
        repair_actions = [
            {
                "api": "repair_backup_archive",
                "args": {"source_object_id": source_by_segment[segment], "target_segment": segment},
            }
            for segment in fault_segments
        ]
        self._turn("Apply the sources selected by the visible approval and archive evidence.", repair_actions)
        self._turn(
            "Run the isolated restore after repair and inspect the trusted final state.",
            [
                {"api": "run_isolated_restore", "args": {}},
                {"api": "inspect_isolated_restore", "args": {}},
            ],
        )
        return self._submit(full_pass_report(case))


def main() -> None:
    scenario = TidbHealthCheckBackupRecoverabilityScenario()
    parser = argparse.ArgumentParser(
        description="Run the TiDB HC04 backup-chain repair and isolated restore scenario."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=24)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--port", type=int, default=28660)
    parser.add_argument("--container-name", default="aiopsbench-tidb-hc04-repairable")
    parser.add_argument("--diagnosis-match-mode", choices=("exact", "semantic"), default="exact")
    parser.add_argument("--diagnosis-semantic-model")
    parser.add_argument("--diagnosis-semantic-config-path")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = BackupRecoverabilityEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = HC04ReferenceMockAgent(case)
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
            max_output_tokens=args.max_output_tokens,
        )
    semantic_model = args.diagnosis_semantic_model or OrchestratorRunConfig().diagnosis_semantic_model
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            diagnosis_match_mode=args.diagnosis_match_mode,
            diagnosis_semantic_model=semantic_model,
            diagnosis_semantic_config_path=args.diagnosis_semantic_config_path or args.config_path,
        ),
    ).run()
    if args.mode == "mock" and (
        result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]
    ) != (True, True, True):
        raise RuntimeError(f"HC04 full mock path did not pass DP/OP/SP: result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
