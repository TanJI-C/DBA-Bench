"""Run the PostgreSQL replica LWLock/PgBouncer cascade cases."""

from __future__ import annotations

import argparse
import json
import os
import signal
from datetime import datetime, timedelta, timezone

from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.execution.postgres_replica_fleet import (
    PgReplicaFleetDeployment,
    PgReplicaFleetEnv,
    ReplicaFleetPorts,
)
from src.scenarios.runtime.config import required_run_timeout_seconds
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.postgres.business_change.lwlock_pgbouncer_cascade import (
    PgBusinessChangeLwlockPgbouncerCascadeScenario,
)



class HistoryAwareMockLLMAgent(MockLLMAgent):
    """Reference agent that derives its history window from public metric output."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._incident_at: datetime | None = None

    @staticmethod
    def _timestamp_ms(value: str) -> int:
        parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return int(parsed.timestamp() * 1000)

    def _observe_waiter_series(self, result: object) -> None:
        if not isinstance(result, dict) or result.get("status") != "success":
            return
        payload = result.get("data")
        if not isinstance(payload, dict):
            payload = result
        for fields in (payload.get("series") or {}).values():
            waiter_values = fields.get("lock_manager_waiters")
            timestamps = fields.get("timestamps")
            if not isinstance(waiter_values, list) or not waiter_values or timestamps is None:
                continue
            if isinstance(timestamps, dict):
                start = self._timestamp_ms(str(timestamps["start"]))
                step_ms = int(timestamps["step_seconds"]) * 1000
                candidates = [start + index * step_ms for index in range(len(waiter_values))]
            elif isinstance(timestamps, list):
                candidates = [self._timestamp_ms(str(value)) for value in timestamps]
            else:
                continue
            index = max(range(len(waiter_values)), key=lambda item: float(waiter_values[item] or 0.0))
            if float(waiter_values[index] or 0.0) <= 0:
                continue
            observed_at = datetime.fromtimestamp(candidates[index] / 1000, tz=timezone.utc)
            if self._incident_at is None or observed_at > self._incident_at:
                self._incident_at = observed_at

    def execute(self, api: str, args: dict, *, thinking: str = "", source: str = "", action_id: str | None = None):
        resolved_args = dict(args or {})
        window_requested = (
            resolved_args.get("start_timestamp") == "__METRIC_DERIVED__"
            or resolved_args.get("end_timestamp") == "__METRIC_DERIVED__"
        )
        history_sql = api == "execute_sql" and resolved_args.get("target") == "history"
        if api in {"read_log", "query_metrics"} and (api == "read_log" or window_requested) or history_sql:
            if self._incident_at is None:
                raise RuntimeError("reference mock has no metric-derived incident window")
            start = self._incident_at - timedelta(seconds=120)
            end = self._incident_at + timedelta(seconds=240)
            start_text = start.strftime("%Y-%m-%d %H:%M:%S")
            end_text = end.strftime("%Y-%m-%d %H:%M:%S")
            if history_sql:
                resolved_args["sql_query"] = str(resolved_args["sql_query"]).replace("__START__", start_text).replace("__END__", end_text)
            else:
                resolved_args["start_timestamp"] = start_text
                resolved_args["end_timestamp"] = end_text
        result = super().execute(api, resolved_args, thinking=thinking, source=source, action_id=action_id)
        if api == "query_metrics" and str(resolved_args.get("metric_type", "")).casefold() == "replica_lwlock":
            self._observe_waiter_series(result)
        return result


def _timeout_handler(signum, frame):
    raise TimeoutError("replica cascade run exceeded its configured timeout")


def build_env(case, port: int, container_name: str):
    if port <= 0 or port + 8 > 65535:
        raise ValueError(f"replica fleet requires nine consecutive TCP ports: primary_port={port}")
    runtime = case.runtime
    ports = ReplicaFleetPorts(
        primary=port,
        replica_0=port + 1,
        replica_1=port + 2,
        replica_2=port + 3,
        pgbouncer=port + 4,
        router=port + 5,
        metrics=port + 6,
        probe=port + 7,
        auxiliary=port + 8,
    )
    deployment = PgReplicaFleetDeployment(
        identity=f"{container_name}-{case.case_id}",
        ports=ports,
        image_name=case.base_image_name,
        fault_image_name=case.fault_image_name,
        resources={
            "cpus": runtime.resources.container_cpu_limit,
            "memory_mb": runtime.resources.container_memory_mb,
            "shm_size": "256m",
        },
    )
    return PgReplicaFleetEnv(
        deployment=deployment,
        sample_interval_sec=1,
        allow_sampler_jitter=True,
    )


def build_run_config(args, case) -> OrchestratorRunConfig:
    return OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
        runtime_warmup_seconds=case.background_workload.warmup_seconds,
        history_seed=args.seed,
    )


def _report(case, complete: bool) -> dict:
    if not complete:
        return {
            "diagnosis": {"conditions": []},
            "outcome": {"changes": [], "verification": []},
            "summary": "No diagnosis or remediation was attempted.",
        }
    conditions = [
        {
            "type": "finding",
            "factor": "replica capacity reduction caused per-replica LWLock slowpath tipping",
            "entity": "affected read replica",
            "evidence": ["N-1 read capacity increased relation-lock demand"],
        },
        {
            "type": "finding",
            "factor": "affected read replica",
            "entity": "one read replica",
            "evidence": ["one replica was unavailable and remaining replicas carried the route"],
        },
        {
            "type": "finding",
            "factor": "LWLock waiters preceded query duration",
            "entity": "LWLock:lock_manager",
            "evidence": ["waiters increased before duration and queue"],
        },
        {
            "type": "finding",
            "factor": "PgBouncer queue was a downstream result",
            "entity": "PgBouncer",
            "evidence": ["cl_waiting followed slow replica queries"],
        },
    ]
    if case.frozen_history is not None:
        conditions.extend([
            {"type": "finding", "factor": "N-1 route redistribution", "entity": "router", "evidence": ["route revision history"]},
            {"type": "finding", "factor": "query footprint crossed the relation-lock fast path", "entity": "checkout read family", "evidence": ["footprint history"]},
            {"type": "finding", "factor": "query latency followed LWLock waiters", "entity": "read query", "evidence": ["ordered service history"]},
            {"type": "finding", "factor": "healthy high-QPS small-footprint replica was excluded", "entity": "healthy replica", "evidence": ["no waiter chain"]},
            {"type": "finding", "factor": "report pool short peak was excluded", "entity": "report_pool", "evidence": ["report-only queue"]},
        ])
    return {
        "diagnosis": {
            "conditions": conditions,
        },
        "outcome": {
            "changes": ["restored replica capacity and kept writes on primary"],
            "verification": ["N-1 replay met Apdex, waiter, pool, write, and lag contracts"],
            "plan": {
                "causal_chain": [
                    "router redistribution",
                    "broad query footprint",
                    "LockManager LWLock waiters",
                    "query duration",
                    "read_pool queue",
                ],
                "protected_boundaries": [
                    "primary remains the writer",
                    "replication stays asynchronous and read-only",
                ],
                "validation": [
                    "randomized N-1 replay checks read Apdex, waiter, pool, primary write, and replication lag",
                ],
            },
        },
        "summary": "The N-1 replica state tipped lock-manager slowpath demand before PgBouncer queueing.",
    }


def build_mock_responses(case):
    if case.frozen_history is not None:
        return [
            {
                "thinking": "Inspect the frozen fleet history instead of treating the healthy current fleet as the incident.",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "router_distribution", "target": None}},
                    {"api": "query_metrics", "args": {"metric_type": "replica_service", "target": None}},
                    {"api": "query_metrics", "args": {"metric_type": "replica_lwlock", "target": None}},
                ],
            },
            {
                "thinking": "Compare the lock-manager, query-footprint, and separated pool history, excluding healthy high-QPS and report-only peaks.",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "query_footprint", "target": None}},
                    {"api": "query_metrics", "args": {"metric_type": "pgbouncer_pool", "target": None}},
                    {"api": "query_metrics", "args": {"metric_type": "primary_service", "target": None}},
                ],
            },
            {
                "thinking": "Use the waiter-derived window to inspect public operation history and TopSQL evidence, then separate the route and pool decoys.",
                "actions": [
                    {
                        "api": "query_metrics",
                        "args": {"metric_type": "router_distribution", "target": None, "start_timestamp": "__METRIC_DERIVED__", "end_timestamp": "__METRIC_DERIVED__", "step_seconds": 2},
                    },
                    {
                        "api": "query_metrics",
                        "args": {"metric_type": "replica_service", "target": None, "start_timestamp": "__METRIC_DERIVED__", "end_timestamp": "__METRIC_DERIVED__", "step_seconds": 2},
                    },
                    {
                        "api": "query_metrics",
                        "args": {"metric_type": "replica_lwlock", "target": None, "start_timestamp": "__METRIC_DERIVED__", "end_timestamp": "__METRIC_DERIVED__", "step_seconds": 2},
                    },
                    {
                        "api": "query_metrics",
                        "args": {"metric_type": "query_footprint", "target": None, "start_timestamp": "__METRIC_DERIVED__", "end_timestamp": "__METRIC_DERIVED__", "step_seconds": 2},
                    },
                    {
                        "api": "query_metrics",
                        "args": {"metric_type": "pgbouncer_pool", "target": None, "start_timestamp": "__METRIC_DERIVED__", "end_timestamp": "__METRIC_DERIVED__", "step_seconds": 2},
                    },
                ],
            },
            {
                "thinking": "The raw window confirms waiter-first, latency-second, and read-pool-last. Query bounded history records for support and exclusion evidence.",
                "actions": [
                    {
                        "api": "read_log",
                        "args": {
                            "log_type": "operation_event",
                            "start_timestamp": "__METRIC_DERIVED__",
                            "end_timestamp": "__METRIC_DERIVED__",
                            "filters": {"event_type": "router_revision"},
                            "lines": 120,
                        },
                    },
                    {
                        "api": "execute_sql",
                        "args": {
                            "target": "history",
                            "sql_query": "SELECT * FROM slow_query WHERE event_time_utc >= '__START__' AND event_time_utc < '__END__' ORDER BY query_time_ms DESC LIMIT 120",
                        },
                    },
                    {
                        "api": "execute_sql",
                        "args": {
                            "target": "history",
                            "sql_query": "SELECT * FROM statement_summary WHERE event_start_utc < '__END__' AND event_end_utc >= '__START__' ORDER BY sum_latency DESC LIMIT 120",
                        },
                    },
                ],
            },
            {
                "thinking": "The current fleet is healthy, which does not erase the frozen incident. Confirm current replication and pool state, then submit a safe N-1 plan for evaluator-owned replay.",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "replica_health", "target": None}},
                    {"api": "query_metrics", "args": {"metric_type": "pool", "target": None}},
                    {"api": "execute_sql", "args": {"sql_query": "SELECT application_name, state, flush_lag, replay_lag FROM pg_stat_replication ORDER BY application_name"}},
                    {"api": "submit", "args": {"report": _report(case, True)}},
                ],
            },
        ]
    return [
        {
            "thinking": "First compare the actual read-replica health and PgBouncer pool state.",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "replica_health", "target": None}},
                {"api": "query_metrics", "args": {"metric_type": "pool", "target": None}},
            ],
        },
        {
            "thinking": "The remaining replicas are carrying skewed load. Check primary replication evidence and keep the writer on primary.",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": "SELECT application_name, state, flush_lag, replay_lag FROM pg_stat_replication ORDER BY application_name"
                    },
                },
                {"api": "query_metrics", "args": {"metric_type": "replication", "target": None}},
            ],
        },
        {
            "thinking": "Restore the drained replica before accepting the N-1 replay.",
            "actions": [
                {"api": "manage_instance", "args": {"action": "start", "target": case.drained_replica, "value": None}},
            ],
        },
        {
            "thinking": "The fleet is restored; submit the causal diagnosis and the replay checks.",
            "actions": [{"api": "submit", "args": {"report": _report(case, True)}}],
        },
    ]


def build_zero_responses(case):
    return [
        {
            "thinking": "Inspect only a current symptom and do not establish the historical N-1 causal chain.",
            "actions": [
                {"api": "query_metrics", "args": {"metric_type": "pool", "target": None}},
            ],
        },
        {
            "thinking": "Submit an empty report.",
            "actions": [{"api": "submit", "args": {"report": _report(case, False)}}],
        },
    ]


def run_mode(args, scenario, case, mode: str):
    env = build_env(case, args.port, f"{args.container_name}-{mode}")
    run_config = build_run_config(args, case)
    if mode == "mock":
        agent = HistoryAwareMockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(build_mock_responses(case))
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses(build_zero_responses(case))
    elif mode == "llm":
        model = args.model
        agent = build_experiment_agent(model=model, config_path=args.config_path, use_native_tools=True)
    else:
        raise ValueError(f"unsupported CF2 run mode: {mode!r}")
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent,
        pretty_print=False,
        max_turns=args.max_turns,
        run_config=run_config,
    )
    result = orchestrator.run()
    print(f"[{mode}] case={case.case_id} DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")
    artifact = getattr(env, "_last_replay_artifact", None)
    if artifact is not None:
        print(json.dumps({
            "mode": mode,
            "case": case.case_id,
            "latency_stats": artifact.get("latency_stats"),
            "read_apdex": artifact.get("read_apdex"),
            "success_rate": artifact.get("success_rate"),
            "max_lwlock_waiters": artifact.get("max_lwlock_waiters"),
            "pool_maxwait_ms": artifact.get("pool_maxwait_ms"),
            "max_query_duration_ms": artifact.get("max_query_duration_ms"),
            "max_pool_waiting_clients": artifact.get("max_pool_waiting_clients"),
            "observation_count": len(artifact.get("observation_samples", ())),
        }, ensure_ascii=False))
    if mode == "mock" and tuple(result[key] for key in ("DiagnosisPass", "OutcomePass", "SafePass")) != (True, True, True):
        raise AssertionError(json.dumps(result, ensure_ascii=False))
    if mode == "zero" and tuple(result[key] for key in ("DiagnosisPass", "OutcomePass", "SafePass")) != (False, False, True):
        raise AssertionError(json.dumps(result, ensure_ascii=False))
    return result


def main() -> None:
    scenario = PgBusinessChangeLwlockPgbouncerCascadeScenario()
    parser = argparse.ArgumentParser(description="Run the PostgreSQL replica LWLock/PgBouncer cascade scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument(
        "--mode",
        choices=["mock", "zero", "llm", "all"],
        default="mock",
        help="all runs Mock, Zero, and the explicitly qualified LLM mode",
    )
    parser.add_argument("--port", type=int, default=15851)
    parser.add_argument("--container-name", default="aiopsbench-pg-business-change-lwlock-pgbouncer-cascade")
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--seed", type=int, default=None, help="Deterministic frozen history seed.")
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="off")
    parser.add_argument("--fault-snapshot-name")
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(required_run_timeout_seconds())
    try:
        modes = ("mock", "zero", "llm") if args.mode == "all" else (args.mode,)
        for mode in modes:
            run_mode(args, scenario, scenario.get_case(args.case), mode)
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
