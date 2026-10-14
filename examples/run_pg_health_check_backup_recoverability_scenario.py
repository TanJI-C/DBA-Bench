import argparse
import json
import os
import signal
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.runtime.config import required_run_timeout_seconds
from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgHealthCheckBackupRecoverabilityScenario
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


HARD_TIMEOUT_SEC = 1800


ZERO_SCORE_MOCK_RESPONSES = [
    {
        "thinking": "Do not inspect the backup catalog or run restore validation; submit immediately.",
        "action": {"api": "submit", "args": {"report": EMPTY_REPORT}},
    }
]


def build_full_score_mock_responses(case) -> list:
    summary = (
        f"Audit request {case.drill_batch_id} selected {case.backup_id} for "
        f"{case.recovery_window_label} at {case.requested_recovery_target_time}. "
        f"The selected primary chain is not recoverable: archived WAL "
        f"{case.missing_wal_file} is missing for {case.missing_range[0]} through "
        f"{case.missing_range[1]}. The latest_recoverable_time is "
        f"{case.latest_recoverable_time}, so the RPO/data-loss exposure is about "
        "14 minutes for the requested recovery point. Object-storage inventory and "
        "cross-region checksum metadata also show A7 is not usable for restore. The "
        "same-day standby seed is technically recoverable, but the recovery runbook "
        "approval and restore artifact mark it as smoke-test-only, not an approved "
        "checkout-ledger recovery source. Reporting clone failure, prior retention "
        "expiry, old sandbox_config restore failure, success mail, archive-lag warning, "
        "and BI slow report are context or noise, not the selected checkout-ledger "
        "recovery objective. Mark the current chain incomplete and repair/archive the "
        "missing WAL before relying on later PITR."
    )
    report = dict(case.reference_report)
    report["outcome"] = {
        "changes": [
            f"The selected chain is blocked by missing WAL {case.missing_wal_file}; "
            f"latest recoverable time is {case.latest_recoverable_time}."
        ],
        "verification": [
            f"The requested recovery target {case.requested_recovery_target_time} "
            "exceeds the validated recovery point, so the business RPO is not met."
        ],
    }
    report["summary"] = summary
    return [
        {
            "thinking": "Inspect the audit request, selected backup chain, and file checksums first.",
            "action": {"api": "execute_sql", "args": {"sql_query": backup_catalog_query()}},
        },
        {
            "thinking": "Check archived WAL continuity by backup_id/timeline and separate retention-expired gaps.",
            "action": {"api": "execute_sql", "args": {"sql_query": archive_continuity_query()}},
        },
        {
            "thinking": "Read restore drill, retention, and monitoring noise before blaming the wrong chain.",
            "action": {"api": "execute_sql", "args": {"sql_query": operational_noise_query()}},
        },
        {
            "thinking": "Run sandbox restore validation against the physical backup path.",
            "action": {
                "api": "manage_instance",
                "args": {
                    "action": "validate_backup",
                    "target": case.backup_path,
                },
            },
        },
        {
            "thinking": "Report the missing WAL gap and latest recoverable point.",
            "action": {
                "api": "submit",
                "args": {"report": report},
            },
        },
    ]


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)


def build_env(case, port: int, container_name: str, image_name: str = None) -> PGEnv:
    env = PGEnv(port=port, allow_sampler_jitter=True, allow_sampler_reconnect=True)
    env.deployment.container_name = container_name
    env.deployment.image_name = image_name or case.base_image_name
    return env


def _json_result(raw):
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return {"status": "error", "raw": raw}


def backup_catalog_query() -> str:
    return """
        SET statement_timeout = '5s';
        SELECT
            bs.backup_id,
            ar.audit_batch_id,
            ar.business_service,
            ar.selected_backup_id,
            ar.review_reason,
            bs.drill_batch_id,
            bs.recovery_window_label,
            bs.timeline,
            bs.status,
            bs.backup_path,
            bs.manifest_path,
            bs.archive_dir,
            bs.requested_recovery_target_time,
            bf.relative_path,
            bf.size_bytes,
            bf.checksum_status
        FROM ops_dr.backup_sets bs
        LEFT JOIN ops_dr.audit_requests ar ON ar.selected_backup_id = bs.backup_id
        JOIN ops_dr.backup_files bf USING (backup_id)
        ORDER BY bf.relative_path;
    """


def archive_continuity_query() -> str:
    return """
        SET statement_timeout = '5s';
        SELECT
            backup_id,
            timeline,
            wal_file,
            segment_no,
            present,
            retention_state,
            first_record_time,
            last_record_time,
            lag(segment_no) OVER (ORDER BY segment_no) AS previous_segment_no
        FROM ops_dr.archive_segments
        ORDER BY backup_id, timeline, segment_no;
        SELECT backup_id, wal_file, local_checksum_status, object_checksum_status,
               replica_region, replica_status, usable_for_restore, notes
        FROM ops_dr.archive_replica_checksums
        ORDER BY backup_id, wal_file;
        SELECT backup_id, source_role, timeline, start_wal_file, stop_wal_file,
               upstream_timeline, label_summary
        FROM ops_dr.backup_label_chain
        ORDER BY backup_id;
        SELECT timeline, predecessor_timeline, promoted_at, promoted_host,
               promotion_lsn, promotion_reason
        FROM ops_dr.timeline_promotion_history
        ORDER BY timeline;
    """


def operational_noise_query() -> str:
    return """
        SET statement_timeout = '5s';
        SELECT 'restore_drill' AS source, backup_id, target_time::text, result, failure_class, log_excerpt
        FROM ops_dr.restore_drill_runs
        UNION ALL
        SELECT 'audit_request', selected_backup_id, requested_recovery_target_time::text, priority, business_service, review_reason
        FROM ops_dr.audit_requests
        UNION ALL
        SELECT 'retention', NULL, cutoff_time::text, action, 'timeline=' || timeline::text, notes
        FROM ops_dr.archive_retention_events
        UNION ALL
        SELECT 'monitoring', related_backup_id, event_time::text, severity, source, message
        FROM ops_dr.monitoring_events
        UNION ALL
        SELECT 'runbook', selected_backup_id, approved_at::text, approval_state, approved_source_role, approval_notes
        FROM ops_dr.recovery_runbook_approvals
        UNION ALL
        SELECT 'object_inventory', backup_id, NULL, replication_status, region, notes
        FROM ops_dr.archive_object_inventory
        UNION ALL
        SELECT 'restore_artifact', backup_id, target_time::text, artifact_status, signed_by, notes
        FROM ops_dr.restore_drill_artifacts
        ORDER BY source, target_time;
    """






def print_evaluation_basis(label: str, result: dict):
    print(f"[Evaluation:{label}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")

def run_with_orchestrator(
    env, scenario, case, agent, run_config, max_turns: int,
):
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        max_turns=max_turns,
        run_config=run_config,
    )
    result = orchestrator.run()
    return result, orchestrator.action_history



def run_mock_full(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Backup Recoverability Full-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckBackupRecoverabilityScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(build_full_score_mock_responses(case))
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=8)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("mock", result)
    assert passed is True, json.dumps(result, ensure_ascii=False)
    return passed


def run_mock_zero(case_id: str, port: int, container_name: str, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Backup Recoverability Zero-Score Mock Path")
    print("=" * 70)

    scenario = PgHealthCheckBackupRecoverabilityScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
    agent.set_mock_responses(ZERO_SCORE_MOCK_RESPONSES)
    result, _ = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=3)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    print_evaluation_basis("zero", result)
    assert passed is False, json.dumps(result, ensure_ascii=False)
    return passed


def run_llm(case_id: str, port: int, container_name: str, model: str = None,
            config_path: str = "config/llm_config.json",
            max_turns: int = 20, run_config: OrchestratorRunConfig = None) -> float:
    print("=" * 70)
    print("AiOpsBench PostgreSQL - Backup Recoverability LLMAgent Path")
    print("=" * 70)

    max_turns = min(max_turns, 30)
    agent = build_experiment_agent(model=model, config_path=config_path, use_native_tools=True)

    scenario = PgHealthCheckBackupRecoverabilityScenario()
    case = scenario.get_case(case_id)
    run_config = run_config or OrchestratorRunConfig()
    env = build_env(case, port, container_name, image_name=None)
    result, action_history = run_with_orchestrator(env, scenario, case, agent, run_config, max_turns=max_turns)
    passed = result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]
    if not any(action.get("api") == "submit" for action in action_history):
            print("[LLMAGENT_BLOCKED] Agent reached max_turns without submit.")
    print_evaluation_basis("llm", result)
    print(f"[Result] LLMAgent passed={passed}")
    return passed


def main():
    parser = argparse.ArgumentParser(description="Run the PG backup recoverability health-check scenario.")
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--port", type=int, default=15745)
    parser.add_argument("--container-name", default="aiopsbench-pg-health-36")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    parser.add_argument("--diagnosis-match-mode", choices=("exact", "semantic"), default="exact")
    parser.add_argument("--diagnosis-semantic-model")
    parser.add_argument("--diagnosis-semantic-config")
    scenario_definition = PgHealthCheckBackupRecoverabilityScenario()
    parser.add_argument(
        "--case", required=True,
        choices=[case.case_id for case in scenario_definition.cases],
    )
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
        diagnosis_match_mode=args.diagnosis_match_mode,
        diagnosis_semantic_model=args.diagnosis_semantic_model or OrchestratorRunConfig().diagnosis_semantic_model,
        diagnosis_semantic_config_path=args.diagnosis_semantic_config or args.config_path,
    )
    case = scenario_definition.get_case(args.case)

    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(required_run_timeout_seconds())
    try:
        if args.mode in ("mock", "all"):
            run_mock_full(args.case, args.port, f"{args.container_name}-{case.case_id}-mock", run_config)
        if args.mode in ("zero", "all"):
            run_mock_zero(args.case, args.port, f"{args.container_name}-{case.case_id}-zero", run_config)
        if args.mode in ("llm", "all"):
            run_llm(args.case, args.port, f"{args.container_name}-{case.case_id}-llm", args.model, args.config_path, args.max_turns, run_config=run_config)
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
