"""Run PG-SF-CA01 with the unified Orchestrator path."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from statistics import median

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.factory import build_experiment_agent
from src.agents.agent import MockLLMAgent
from src.scenarios.evaluation.base import evaluation_passed
from src.protocols.report import EMPTY_REPORT
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.config import required_run_timeout_seconds
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.postgres.system_failure.checkpoint_archive import (
    ARCHIVE_TARGET_CONTAINER_PATH,
    ARCHIVE_BINDING_STATE_TABLE,
    ARCHIVE_GUARD_TABLE,
    ARCHIVE_POLICY_TABLE,
    ARCHIVE_ROUTE_STATE_TABLE,
    ARCHIVE_REPOSITORY_TABLE,
    ARCHIVE_TARGET_REGISTRY_TABLE,
    ARCHIVE_SHADOW_DIRECTORY,
    BACKFILL_CONFIG_TABLE,
    CheckpointArchiveDeployment,
    PgSystemFailureCheckpointArchiveCase,
    PgSystemFailureCheckpointArchiveScenario,
    _policy_archive_command,
)
from src.workloads.tpcds import TPCDSWorkload


try:
    DATASET_INITIALIZATION_TIMEOUT_SECONDS = int(
        os.environ.get("AIOPS_PG_CHECKPOINT_ARCHIVE_DATASET_INIT_TIMEOUT_SECONDS", "1800")
    )
except ValueError as exc:
    raise ValueError("AIOPS_PG_CHECKPOINT_ARCHIVE_DATASET_INIT_TIMEOUT_SECONDS must be an integer") from exc
if DATASET_INITIALIZATION_TIMEOUT_SECONDS <= 0:
    raise ValueError("AIOPS_PG_CHECKPOINT_ARCHIVE_DATASET_INIT_TIMEOUT_SECONDS must be positive")


def build_report(case: PgSystemFailureCheckpointArchiveCase, success: bool) -> dict:
    return case.reference_report if success else EMPTY_REPORT


def _public_history_window(conversation: list[dict], duration_minutes: int = 10) -> tuple[str, str]:
    """Derive a bounded query window from the public help response."""
    marker = "[工具执行结果] help: "
    for message in reversed(conversation):
        content = message.get("content", "") if isinstance(message, dict) else ""
        if not content.startswith(marker):
            continue
        try:
            payload = json.loads(content[len(marker):])
        except json.JSONDecodeError:
            continue
        runtime = payload.get("runtime") or payload.get("definition", {}).get("runtime", {})
        available_start = runtime.get("available_start")
        available_end = runtime.get("available_end")
        if not available_start or not available_end:
            continue
        end = datetime.strptime(available_end, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        start = max(
            datetime.strptime(available_start, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
            end - timedelta(minutes=duration_minutes),
        )
        return start.strftime("%Y-%m-%d %H:%M:%S"), available_end
    raise RuntimeError("Mock frozen history requires public help runtime.available_start/end")


def _public_candidate_windows(
    conversation: list[dict], duration_minutes: int = 10,
) -> list[tuple[str, str]]:
    """Select candidate windows from public overview metrics, with a boundary fallback."""
    marker = "[工具执行结果] help: "
    overview_series = []
    for message in conversation:
        content = message.get("content", "") if isinstance(message, dict) else ""
        query_marker = "[工具执行结果] query_metrics: "
        if not content.startswith(query_marker):
            continue
        try:
            payload = json.loads(content[len(query_marker):])
        except json.JSONDecodeError:
            continue
        window = payload.get("window") or {}
        series = (payload.get("series") or {}).get("postgres")
        timestamps = series.get("timestamps") if isinstance(series, dict) else None
        if (
            payload.get("kind") == "series"
            and isinstance(series, dict)
            and isinstance(timestamps, list)
            and len(timestamps) > 2
            and int(window.get("step_seconds", 0) or 0) >= 2
        ):
            overview_series.append((payload, series, window))
    if overview_series:
        timestamps = overview_series[0][1]["timestamps"]
        available_start = str(overview_series[0][2].get("available_start") or timestamps[0])
        available_end = str(overview_series[0][2].get("available_end") or timestamps[-1])
        scores = [0.0] * len(timestamps)
        for _payload, series, _window in overview_series:
            if series.get("timestamps") != timestamps:
                continue
            for field, raw_values in series.items():
                if field == "timestamps" or not isinstance(raw_values, list) or len(raw_values) != len(timestamps):
                    continue
                try:
                    values = [float(value) for value in raw_values]
                except (TypeError, ValueError):
                    continue
                if not all(math.isfinite(value) for value in values):
                    continue
                center = median(values)
                mad = median(abs(value - center) for value in values)
                scale = mad if mad > 0 else max((max(values) - min(values)) / 4.0, 1.0)
                for index, value in enumerate(values):
                    scores[index] += max(0.0, (value - center) / scale)
        step_seconds = max(2, int(overview_series[0][2].get("step_seconds", 20) or 20))
        min_separation = max(1, int((duration_minutes * 60) / step_seconds))
        ranked = sorted(range(len(scores)), key=scores.__getitem__, reverse=True)
        selected_indices: list[int] = []
        for index in ranked:
            if scores[index] <= 0:
                break
            if any(abs(index - selected) < min_separation for selected in selected_indices):
                continue
            selected_indices.append(index)
            if len(selected_indices) == 3:
                break
        if selected_indices:
            available_start_dt = datetime.strptime(available_start, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            available_end_dt = datetime.strptime(available_end, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            duration = timedelta(minutes=duration_minutes)
            windows = []
            for index in selected_indices:
                center_dt = datetime.strptime(str(timestamps[index]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                start_dt = max(available_start_dt, center_dt - duration / 2)
                end_dt = min(available_end_dt, start_dt + duration)
                start_dt = max(available_start_dt, end_dt - duration)
                windows.append((start_dt.strftime("%Y-%m-%d %H:%M:%S"), end_dt.strftime("%Y-%m-%d %H:%M:%S")))
            if len(windows) == 3:
                return windows
    for message in reversed(conversation):
        content = message.get("content", "") if isinstance(message, dict) else ""
        if not content.startswith(marker):
            continue
        try:
            payload = json.loads(content[len(marker):])
        except json.JSONDecodeError:
            continue
        runtime = payload.get("runtime") or payload.get("definition", {}).get("runtime", {})
        available_start = runtime.get("available_start")
        available_end = runtime.get("available_end")
        if not available_start or not available_end:
            continue
        start = datetime.strptime(available_start, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        end = datetime.strptime(available_end, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        duration = timedelta(minutes=duration_minutes)
        if end - start < duration:
            raise RuntimeError("Mock frozen history boundary is shorter than candidate window")
        candidates = (
            (start, start + duration),
            (start + (end - start - duration) / 2, start + (end - start - duration) / 2 + duration),
            (end - duration, end),
        )
        return [
            (candidate_start.strftime("%Y-%m-%d %H:%M:%S"), candidate_end.strftime("%Y-%m-%d %H:%M:%S"))
            for candidate_start, candidate_end in candidates
        ]
    raise RuntimeError("Mock frozen history requires public help runtime.available_start/end")


def build_mock_responses(case: PgSystemFailureCheckpointArchiveCase) -> list[dict]:
    use_neighbor_repair = case.frozen_history is not None
    repair_target_name = case.archive_neighbor_target_name if use_neighbor_repair else case.archive_target_name
    repair_repository_name = case.archive_neighbor_repository_name if use_neighbor_repair else case.archive_repository_name
    repair_target_path = (
        f"{ARCHIVE_TARGET_CONTAINER_PATH}/{ARCHIVE_SHADOW_DIRECTORY}"
        if use_neighbor_repair
        else f"{ARCHIVE_TARGET_CONTAINER_PATH}/{case.archive_target_name}"
    )
    def history_actions(conversation: list[dict]) -> list[dict]:
        history_start_text, history_end_text = _public_history_window(conversation)
        candidate_windows = _public_candidate_windows(conversation)
        actions = [
            {"api": "query_metrics", "args": {"metric_type": "storage_pressure", "target": None}},
            {"api": "query_metrics", "args": {"metric_type": "batch_progress", "target": None}},
            {"api": "read_log", "args": {"log_type": "operation_event", "start_timestamp": history_start_text, "end_timestamp": history_end_text, "target": "postgres", "filters": {"event_type": "archive_attempt"}, "lines": 100}},
            {"api": "read_log", "args": {"log_type": "operation_event", "start_timestamp": history_start_text, "end_timestamp": history_end_text, "target": "postgres", "filters": {"event_type": "job_batch"}, "lines": 100}},
            {"api": "read_log", "args": {"log_type": "operation_event", "start_timestamp": history_start_text, "end_timestamp": history_end_text, "target": "postgres", "filters": {"event_type": "backup_run"}, "lines": 100}},
            {"api": "read_log", "args": {"log_type": "operation_event", "start_timestamp": history_start_text, "end_timestamp": history_end_text, "target": "postgres", "filters": {"event_type": "config_revision"}, "lines": 100}},
            {"api": "execute_sql", "args": {"sql_query": (
                f"SELECT t.target_name, t.repository_name, t.target_path, t.enabled, t.role, "
                f"r.quota_mb, r.reserved_mb, r.safe_spare_mb "
                f"FROM {ARCHIVE_TARGET_REGISTRY_TABLE} t "
                f"JOIN {ARCHIVE_REPOSITORY_TABLE} r USING (repository_name) "
                "ORDER BY t.target_name;"
            )}},
            {"api": "execute_sql", "args": {"sql_query": (
                f"SELECT t.target_name, t.binding_generation, l.binding_generation, "
                f"route.binding_generation, route.worker_activation_epoch, "
                f"(l.lease_expires_at > clock_timestamp()) AS lease_valid "
                f"FROM {ARCHIVE_TARGET_REGISTRY_TABLE} t "
                f"JOIN {ARCHIVE_BINDING_STATE_TABLE} l ON l.target_name = t.target_name "
                f"JOIN {ARCHIVE_ROUTE_STATE_TABLE} route ON route.target_name = t.target_name "
                "WHERE t.enabled AND route.enabled ORDER BY t.target_name;"
            )}},
        ]
        for candidate_start, candidate_end in candidate_windows:
            for metric_type in (
                "wal_generation", "checkpoint_activity", "archive_delivery", "archive_backlog", "service_slo",
            ):
                actions.append({
                    "api": "query_metrics",
                    "args": {
                        "metric_type": metric_type,
                        "target": None,
                        "start_timestamp": candidate_start,
                        "end_timestamp": candidate_end,
                        "step_seconds": 2,
                    },
                })
            actions.append({
                "api": "read_log",
                "args": {
                    "log_type": "operation_event",
                    "start_timestamp": candidate_start,
                    "end_timestamp": candidate_end,
                    "target": "postgres",
                    "filters": {"event_type": "archive_attempt"},
                    "lines": 100,
                },
            })
        return actions
    static_conversation = [{
        "role": "user",
        "content": (
            "[工具执行结果] help: "
            + json.dumps({
                "runtime": {
                    "available_start": "1970-01-01 00:00:00",
                    "available_end": "1970-01-01 12:00:00",
                },
            })
        ),
    }]
    return [
        {
            "thinking": "Read the public metric contract and frozen UTC boundary before selecting candidate windows.",
            "actions": [
                {"api": "help", "args": {"tool_name": "query_metrics"}},
                {"api": "help", "args": {"tool_name": "read_log"}},
            ],
        },
        {
            "thinking": "Separate the write/checkpoint signal from the archive signal before changing anything.",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "wal_generation", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "checkpoint_activity", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "archive_delivery", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "archive_backlog", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "service_slo", "target": None}},
            ],
        },
        {
            "thinking": "The archive target is behind WAL generation independently of checkpoint pressure; inspect archiver state and the active settings.",
            "actions": history_actions(static_conversation),
            "_actions_factory": history_actions,
        },
        {
            "thinking": "Reduce the write/checkpoint burst and remove the archive command delay while retaining durability and the recovery chain.",
            "actions": [
                {"api": "manage_instance", "args": {"action": "set_config", "target": "checkpoint_timeout", "value": "5min"}},
                {"api": "manage_instance", "args": {"action": "set_config", "target": "max_wal_size", "value": "256MB"}},
                {"api": "manage_instance", "args": {"action": "set_config", "target": "checkpoint_completion_target", "value": "0.9"}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {BACKFILL_CONFIG_TABLE} "
                    f"SET batch_rows = {case.backfill_batch_rows_target}, pause_ms = {case.backfill_pause_ms_target} "
                    f"WHERE job_name = '{case.write_job_name}';"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {ARCHIVE_POLICY_TABLE} "
                    f"SET max_segments_per_minute = {case.archive_segments_per_minute_target}, "
                    f"pause_ms = {case.archive_pause_ms_target} "
                    f"WHERE policy_name = '{case.archive_policy_name}';"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {ARCHIVE_GUARD_TABLE} "
                    f"SET enabled = {'true' if case.archive_guard_enabled_target else 'false'}, "
                    f"max_segments_per_minute = {case.archive_segments_per_minute_target}, "
                    f"pause_ms = {case.archive_pause_ms_target} "
                    f"WHERE guard_name = '{case.archive_guard_name}';"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {ARCHIVE_REPOSITORY_TABLE} "
                    f"SET quota_mb = {case.archive_repository_quota_mb_target}, "
                    f"reserved_mb = {case.archive_repository_reserved_mb} "
                    f"WHERE repository_name = '{repair_repository_name}';"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {ARCHIVE_TARGET_REGISTRY_TABLE} SET role = CASE WHEN target_name = '{repair_target_name}' "
                    "THEN 'active' ELSE 'neighbor' END "
                    f"WHERE target_name IN ('{case.archive_target_name}', '{case.archive_neighbor_target_name}');"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {ARCHIVE_TARGET_REGISTRY_TABLE} SET repository_name = '{repair_repository_name}', "
                    f"target_path = '{repair_target_path}', enabled = true, role = 'active', binding_generation = 17 "
                    f"WHERE target_name = '{repair_target_name}';"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    "UPDATE archive_endpoint_binding_state SET "
                    "lease_expires_at = clock_timestamp() + interval '1 hour', binding_generation = 17 "
                    f"WHERE target_name = '{repair_target_name}';"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    f"UPDATE {ARCHIVE_ROUTE_STATE_TABLE} SET route_name = '{repair_target_name}_route', "
                    f"target_path = '{repair_target_path}', enabled = true, binding_generation = 17, "
                    f"worker_activation_epoch = 17 WHERE target_name = '{repair_target_name}';"
                )}},
                {"api": "manage_instance", "args": {"action": "set_config", "target": "archive_command", "value": _policy_archive_command(case.archive_target_name)}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT pg_reload_conf();"}},
            ],
        },
        {
            "thinking": "Submit only after the next joint replay and marker restore are verified by the evaluator.",
            "action": {"api": "submit", "args": {"report": build_report(case, True)}},
        },
    ]


def build_zero_responses(case: PgSystemFailureCheckpointArchiveCase) -> list[dict]:
    return [
        {
            "thinking": "Disable WAL archiving instead of diagnosing the dual fault.",
            "action": {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER SYSTEM SET archive_command = 'true';"},
            },
        },
        {
            "thinking": "Reload the unsafe archive setting and submit without a diagnosis.",
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": "SELECT pg_reload_conf();"}},
                {"api": "submit", "args": {"report": EMPTY_REPORT}},
            ],
        },
    ]


def build_env(case: PgSystemFailureCheckpointArchiveCase, port: int, container_name: str) -> PGEnv:
    archive_port, restore_port = allocate_ports(port)
    workload = TPCDSWorkload(scale=case.dataset_scale)
    resource_suffix = hashlib.sha256(container_name.encode("utf-8")).hexdigest()[:12]
    # A fresh host-owned bind-mount directory prevents a previous container's
    # postgres-owned files from blocking a repeated or parallel run.
    archive_target_root = tempfile.mkdtemp(
        prefix=f"aiopsbench-pg-sf-ca01-archive-{case.case_id}-",
    )
    deployment = CheckpointArchiveDeployment(
        container_name=container_name,
        port=port,
        image_name=case.base_image_name,
        postgres_user="postgres",
        postgres_password="password",
        postgres_db="testdb",
        init_sql_path=workload.get_init_sql_path(),
        workload_data_dir=workload.data_dir,
        archive_target_root=archive_target_root,
        archive_target_name=case.archive_target_name,
        wal_volume_name=f"{case.wal_volume_name}-{resource_suffix}",
        network_name=f"{case.network_name}-{resource_suffix}",
        archive_port=archive_port,
        restore_port=restore_port,
        initialization_timeout_seconds=DATASET_INITIALIZATION_TIMEOUT_SECONDS,
    )
    # Frozen history requires the same fixed two-second grid as the public metric
    # catalog; scenario metrics are sampled by the attached history adapter.
    return PGEnv(
        workload=workload,
        deployment=deployment,
        port=port,
        sample_interval_sec=2,
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )


def allocate_ports(primary_port: int) -> tuple[int, int]:
    if primary_port > 65533:
        raise ValueError(f"primary port leaves no room for archive/restore ports: primary={primary_port}")
    return primary_port + 1, primary_port + 2


def check_startup_resources(port: int, container_name: str) -> None:
    """Fail before deployment when Docker or any task-owned host port is unavailable."""
    docker = shutil.which("docker")
    if docker is None:
        raise RuntimeError("Docker CLI is required for this PostgreSQL scenario")
    docker_info = None
    docker_info_error = None
    for _ in range(3):
        try:
            candidate = subprocess.run(
                [docker, "version", "--format", "{{.Server.Version}}"],
                capture_output=True,
                text=True,
                timeout=15,
            )
        except subprocess.TimeoutExpired as exc:
            docker_info_error = f"Docker daemon info timed out: {exc}"
            continue
        if candidate.returncode == 0:
            docker_info = candidate
            break
        docker_info_error = candidate.stderr.strip() or "docker info returned a non-zero status"
    if docker_info is None:
        raise RuntimeError(f"Docker daemon is unavailable: {docker_info_error}")
    ss = shutil.which("ss")
    if ss is None:
        raise RuntimeError("ss is required to verify the PostgreSQL/archive/restore ports")
    ports = (port, *allocate_ports(port))
    listening = subprocess.run([ss, "-ltnH"], capture_output=True, text=True, timeout=10)
    if listening.returncode != 0:
        raise RuntimeError(f"ss failed while checking ports: {listening.stderr.strip()}")
    occupied = [
        candidate
        for candidate in ports
        if any(re.search(rf":{candidate}(?:\s|$)", line) for line in listening.stdout.splitlines())
    ]
    if occupied:
        raise RuntimeError(f"task ports are already listening: {occupied}; container={container_name}")


def build_run_config(case: PgSystemFailureCheckpointArchiveCase, args) -> OrchestratorRunConfig:
    default_seed = 0xCA1001 if case.case_id == "checkpoint_archive_dual_fault" else 0xCA1002
    return OrchestratorRunConfig(
        fault_snapshot_mode="off" if case.frozen_history is not None else args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name or case.fault_image_name,
        history_seed=getattr(args, "history_seed", None) if getattr(args, "history_seed", None) is not None else default_seed,
    )


def run_mode(case, mode: str, port: int, container_name: str, model: str | None, config_path: str, max_turns: int, reasoning_effort: str, run_config):
    scenario = PgSystemFailureCheckpointArchiveScenario()
    env = build_env(case, port, container_name)
    if mode == "mock":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(build_mock_responses(case))
        turns = 12
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(build_zero_responses(case))
        turns = 3
    else:
        agent = build_experiment_agent(
            model=model,
            config_path=config_path,
            use_native_tools=True,
            reasoning_effort=reasoning_effort if os.environ.get("AIOPS_AGENT_MODE") in {"llm", "v-expel"} else None,
        )
        turns = min(max_turns, 30)
    result = Orchestrator(env, scenario, case, agent, max_turns=turns, run_config=run_config).run()
    archive_port, restore_port = allocate_ports(port)
    print(f"[{mode}] case={case.case_id} primary={port} archive={archive_port} restore={restore_port} "
          f"DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")
    if mode == "mock" and not evaluation_passed(result):
        raise AssertionError(json.dumps(result, ensure_ascii=False, default=str))
    if mode == "zero" and evaluation_passed(result):
        raise AssertionError(json.dumps(result, ensure_ascii=False, default=str))
    return result


def main() -> None:
    scenario = PgSystemFailureCheckpointArchiveScenario()
    parser = argparse.ArgumentParser(description=scenario.description)
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm"], default="mock")
    parser.add_argument("--port", type=int, default=15841, help="primary PostgreSQL host port; task-external ports derive archive/restore as +1/+2")
    parser.add_argument("--container-name", default="aiopsbench-pg-system-failure-checkpoint-archive")
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high", "xhigh"], default="xhigh")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    parser.add_argument("--seed", "--history-seed", dest="history_seed", type=int)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65533:
        parser.error("--port must be between 1024 and 65533")
    case = scenario.get_case(args.case)
    check_startup_resources(args.port, f"{args.container_name}-{case.case_id}-{args.mode}")
    run_config = build_run_config(case, args)
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("scenario timeout")))
    signal.alarm(required_run_timeout_seconds())
    try:
        run_mode(case, args.mode, args.port, f"{args.container_name}-{case.case_id}-{args.mode}", args.model, args.config_path, args.max_turns, args.reasoning_effort, run_config)
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
