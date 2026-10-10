#!/usr/bin/env python
"""Three-path calibration harness for pg5 instance 4 (pg_htap_replica_freshness).

Contract §10 gate harness: deploys the real streaming primary/standby topology
(physical slot replication, isolated WAL volume, tc tbf link throttle) and
drives the freshness workload runtime plus the native capabilities with the
same business calendar / dataset seed / clock across paths. Event payloads come
from the frozen instance YAML; --seconds compresses the arrival timeline only.

Paths (contract §10 + §12.14 prefixes):
  healthy                   no fault events; repeated baseline
  reference                 all events; long snapshot resolved by termination,
                            report governance applied, throttled link repaired
                            (catch-up), then a prevention probe: a second
                            long-snapshot activation terminated by the tightened
                            standby idle-in-transaction guard (prevented prefix)
  zero                      all events, no action (unresolved prefix)
  wrong-drop-slot           drop the active replication slot mid-run
  wrong-promote-standby     promote the standby to a second primary
  wrong-unbounded-feedback  enable hot_standby_feedback unboundedly

Example (calibration run, compressed timeline):
  conda run -n aiops python scripts/pg5r_htap_replica_freshness_three_paths.py \
      --path zero --seconds 720 --run-id htap4-zero-r1 --primary-port 25240 --standby-port 25241
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.persistent_scenarios.backend.contracts import EventActivationContext
from src.persistent_scenarios.backend.postgres.capabilities.htap_replica_freshness import CAPABILITIES_BY_ID
from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness import (
    FreshnessDatasetScale,
    HtapReplicaFreshnessWorkloadProvider,
    HtapReplicaTopology,
    ReplicaTopologyConfig,
    bootstrap,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness.calendar import (
    FreshnessBusinessCalendar,
    ReportSubmission,
)
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.persistent_scenarios.model.spec import EventSpec
from src.persistent_scenarios.runtime.clock import RealClock
from src.persistent_scenarios.runtime.ledger import LedgerView

PRODUCTION_HORIZON_SECONDS = 5400
FULL_SCALE = FreshnessDatasetScale()
SMOKE_SCALE = FreshnessDatasetScale(order_rows=20000, event_rows=80000)
YAML_PATH = Path("src/persistent_scenarios/postgres/pg_htap_replica_freshness.yaml")
EVENT_IDS = (
    "frs_long_snapshot_a",
    "frs_update_surge_a",
    "frs_link_degraded",
    "frs_link_degraded_b",
    "frs_long_snapshot_b",
    "frs_update_surge_b",
)


@dataclass(frozen=True, slots=True)
class OracleAction:
    """One scripted remediation action, expressed in business seconds.

    ``target`` routes the statement to the topology node the object lives on:
    standby backends terminate on the standby, governance rows and role GUCs
    live on the primary (role GUCs replicate physically). The engine-path gate
    script (``backend/postgres/gate_scripts.py``) converts these to agent
    actions, so every statement must classify inside the instance safety
    whitelist.
    """

    at_seconds: int
    label: str
    sql: str
    target: str = "primary"


ORACLE_ACTIONS = (
    OracleAction(
        726,
        "terminate_stuck_report_snapshot",
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
        "WHERE application_name LIKE 'pg5r-htap4-capability-long-snapshot%' AND pid <> pg_backend_pid();",
        target="standby",
    ),
    OracleAction(
        732,
        "report_role_idle_guard",
        "ALTER ROLE frs_report SET idle_in_transaction_session_timeout = '45s';",
    ),
    OracleAction(
        738,
        "report_statement_budget",
        "UPDATE frs_work_control SET control_value = '15000', updated_by = 'dba', "
        "updated_at = clock_timestamp() WHERE control_key = 'report_statement_timeout_ms';",
    ),
    OracleAction(
        1812,
        "replication_link_qos_restore",
        "UPDATE frs_work_control SET control_value = '0', updated_by = 'dba', "
        "updated_at = clock_timestamp() WHERE control_key = 'replication_link_rate_kbit';",
    ),
    # The second report tenant's snapshot inside the critical window gets its
    # own response: an alert-driven DBA terminates it, not just the role guard.
    OracleAction(
        3000,
        "terminate_stuck_report_snapshot_b",
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
        "WHERE application_name LIKE 'pg5r-htap4-capability-long-snapshot%' AND pid <> pg_backend_pid();",
        target="standby",
    ),
    # The link competition deepens as the critical window opens: each stage of
    # the degradation is repaired on its own alert, not just the first.
    OracleAction(
        2532,
        "replication_link_qos_restore_b",
        "UPDATE frs_work_control SET control_value = '0', updated_by = 'dba', "
        "updated_at = clock_timestamp() WHERE control_key = 'replication_link_rate_kbit';",
    ),
)

WRONG_ACTIONS = (
    OracleAction(
        2412,
        "wrong_drop_active_slot",
        "SELECT pg_terminate_backend(active_pid) FROM pg_replication_slots "
        "WHERE slot_name = 'frs_replication_slot' AND active_pid IS NOT NULL; "
        "SELECT pg_drop_replication_slot('frs_replication_slot');",
    ),
)

# The oracle's incident explanation, in the diagnosis contract's own readable
# terms (the condition aliases): the reference answer the exact-match DP
# contract validates against.
REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "replica_snapshot_conflict",
                "factor": "a long-open standby report snapshot blocked replay and recovery conflicts cancelled report queries",
                "entity": "analytics_standby",
                "evidence": [
                    "standby recovery conflict counter increments",
                    "report jobs restarted after cancellation",
                ],
            },
            {
                "type": "replication_link_degradation",
                "factor": "degraded replication link bandwidth grew replay lag and primary WAL retention on the physical slot",
                "entity": "replication_link",
                "evidence": [
                    "pg_replication_slots retained WAL growing",
                    "replay LSN falling behind the primary commit watermark",
                    "the shaped rate covered the steady-state write rate so replay lag surfaced only while update surges ran",
                    "the throttled replication link was the dominant freshness constraint in the critical window and replay still lagged after both report snapshots were cleared",
                ],
            },
        ]
    },
    "outcome": {
        "changes": [action.label for action in ORACLE_ACTIONS],
        "verification": [
            "critical reports delivered fresh and on time",
            "slot retention inside the configured quota with the slot still streaming",
        ],
    },
    "summary": (
        "A long-open standby report snapshot blocked replay and recovery conflicts cancelled report queries; "
        "the second snapshot in the critical window stalled replay again but was not the binding freshness "
        "constraint once it was cleared. The replication link was degraded in two stages: the first stage's "
        "shaped rate covered the steady-state write rate so replay lag surfaced only while update surges ran, "
        "and the throttled replication link was the dominant freshness constraint in the critical window with "
        "replay still lagging after both report snapshots were cleared. Snapshots were governed and each link "
        "degradation was repaired through the public control row."
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        required=True,
        choices=[
            "healthy",
            "reference",
            "zero",
            "wrong-drop-slot",
            "wrong-promote-standby",
            "wrong-unbounded-feedback",
        ],
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=PRODUCTION_HORIZON_SECONDS,
        help="scoring horizon; values below the production horizon compress the arrival timeline",
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--primary-port", type=int, default=25240)
    parser.add_argument("--standby-port", type=int, default=25241)
    parser.add_argument("--cpuset", default=None, help="cpuset-cpus for the PG nodes when two paths run in parallel")
    parser.add_argument("--artifacts-root", default="artifacts/pg5r-htap4-three-paths")
    parser.add_argument("--keep", action="store_true")
    return parser.parse_args()


def scaled_event(event: EventSpec, ratio: float) -> EventSpec:
    payload = dict(event.payload)
    if event.capability_id == "frs_primary_update_surge":
        payload["surge_seconds"] = max(10, int(int(payload["surge_seconds"]) * ratio))
    if event.capability_id == "frs_standby_long_snapshot":
        payload["max_hold_seconds"] = max(20, int(int(payload["max_hold_seconds"]) * ratio))
    return replace(event, payload=payload, start_seconds=max(1, int(event.start_seconds * ratio)))


def compressed_calendar(scoring_seconds: int) -> FreshnessBusinessCalendar:
    ratio = scoring_seconds / PRODUCTION_HORIZON_SECONDS

    def scaled(value: int) -> int:
        return max(1, int(value * ratio))

    routine_budget = max(20, int(120 * ratio))
    critical_budget = max(15, int(60 * ratio))
    submissions: list[ReportSubmission] = []
    at = scaled(120)
    while at < scaled(2400):
        submissions.append(
            ReportSubmission(
                at_seconds=at,
                report_kind=f"routine_{at:04d}",
                freshness_budget_seconds=routine_budget,
                deadline_seconds=at + max(20, int(150 * ratio)),
            )
        )
        at += max(15, int(180 * ratio))
    first_critical = scaled(2520)
    for offset, kind in enumerate(("critical_exec", "critical_finance", "critical_supply", "critical_growth", "critical_final")):
        submit = first_critical + offset * max(15, int(180 * ratio))
        submissions.append(
            ReportSubmission(
                at_seconds=submit,
                report_kind=kind,
                freshness_budget_seconds=critical_budget,
                deadline_seconds=submit + max(30, int(780 * ratio)),
            )
        )
    return FreshnessBusinessCalendar(
        horizon_seconds=scoring_seconds,
        submissions=tuple(submissions),
        input_stop_seconds=scaled(4560),
        critical_window_start_seconds=scaled(2520),
    )


class Runner:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.scoring_seconds = args.seconds
        self.ratio = self.scoring_seconds / PRODUCTION_HORIZON_SECONDS
        self.scale = FULL_SCALE if self.scoring_seconds >= PRODUCTION_HORIZON_SECONDS else SMOKE_SCALE
        self.plan_faults = args.path != "healthy"
        self.reference = args.path == "reference"
        self.wrong_action = args.path.removeprefix("wrong-") if args.path.startswith("wrong-") else None
        self.topology = HtapReplicaTopology(
            ReplicaTopologyConfig(
                run_id=args.run_id,
                primary_port=args.primary_port,
                standby_port=args.standby_port,
                max_standby_streaming_delay_ms=5000,
                cpuset=args.cpuset,
            )
        )
        self.spec = load_persistent_scenario(YAML_PATH)
        self.events = {event.event_id: scaled_event(event, self.ratio) for event in self.spec.events if event.event_id in EVENT_IDS}
        # Oracle actions are authored in production business seconds; the
        # compressed harness runs them on the same compressed arrival timeline
        # as the events and the report calendar.
        self.oracle_actions = tuple(
            replace(action, at_seconds=max(1, int(action.at_seconds * self.ratio)))
            for action in ORACLE_ACTIONS
        )
        self.activated: set[str] = set()
        self.handles: list[tuple[str, object]] = []
        self.event_evidence: list[dict] = []
        self.applied_actions: list[str] = []
        self.timeline: list[dict] = []
        self.wrong_evidence: dict = {}
        self._last_sample = -10.0

    def _activate(self, event: EventSpec) -> None:
        capability = CAPABILITIES_BY_ID[event.capability_id]
        context = EventActivationContext(
            run_id=self.args.run_id, spec=self.spec, event=event, environment=self.topology, clock=self.clock
        )
        result = capability.activate(context)
        alert = capability.alert(context, result.handle)
        self.handles.append((event.capability_id, result.handle))
        self.event_evidence.append(
            {
                "event_id": event.event_id,
                "capability_id": event.capability_id,
                "outcome": "prevented" if result.prevented is not None else "applied",
                "prevented_mechanism": result.prevented.mechanism if result.prevented else None,
                "protection_state": dict(result.prevented.protection_state) if result.prevented else None,
                "facts": dict(result.applied.facts) if result.applied else dict(result.attempt.detail),
                "alert": {"title": alert.title, "severity": alert.severity, "category": alert.category},
                "business_seconds": round(self.runtime.business_seconds_now(), 1),
            }
        )

    def _sample(self) -> None:
        now = self.runtime.business_seconds_now()
        if now - self._last_sample < 5.0:
            return
        self._last_sample = now
        try:
            facts = self.topology.replication_facts()
            primary = self.topology.primary_sql(
                "SELECT COALESCE(sum(n_dead_tup), 0) FROM pg_stat_user_tables WHERE relname LIKE 'frs_%';"
            )
            feedback = self.topology.standby_sql("SHOW hot_standby_feedback;")
        except Exception as exc:  # noqa: BLE001 - sampler evidence only
            self.timeline.append({"t": round(now, 1), "error": repr(exc)})
            return
        self.timeline.append(
            {
                "t": round(now, 1),
                "slot_retained_bytes": facts["slot_retained_bytes"],
                "slot_wal_status": facts["slot_wal_status"],
                "replay_lag_bytes": facts["replay_lag_bytes"],
                "recovery_conflicts": facts["standby_recovery_conflicts"],
                "standby_in_recovery": facts["standby_in_recovery"],
                "primary_dead_tuples": int(primary[0][0]),
                "hot_standby_feedback": str(feedback[0][0]),
            }
        )

    def _execute_oracle_action(self, action: OracleAction) -> None:
        connection = self.topology.open_workload_connection(f"pg5r-htap4-oracle-{action.label}", action.target)
        try:
            with connection.cursor() as cursor:
                cursor.execute(action.sql)
            connection.commit()
        finally:
            connection.close()
        self.applied_actions.append(f"oracle:{action.label}")

    def _prevention_probe(self, snapshot_event: EventSpec) -> None:
        # Behavioral guard: the standby holder keepalive is 15s, so a 10s
        # standby-wide idle-in-transaction guard genuinely terminates a fresh
        # long-snapshot session (new sessions only; ALTER SYSTEM + reload).
        self.topology.standby_sql("ALTER SYSTEM SET idle_in_transaction_session_timeout = '10s';")
        self.topology.standby_sql("SELECT pg_reload_conf();")
        self.applied_actions.append("prevention_guard=standby_idle_in_tx_10s")
        probe = replace(
            snapshot_event,
            event_id="frs_long_snapshot_prevented",
            occurrence=3,
            entity="report_tenant_probe",
            payload={"max_hold_seconds": max(30, int(600 * self.ratio))},
            start_seconds=int(self.runtime.business_seconds_now()) + 1,
        )
        evidence_index = len(self.event_evidence)
        self._activate(probe)
        self._record_prevention_outcome(evidence_index, "standby_idle_in_transaction_session_timeout=10s")

    def _record_prevention_outcome(self, evidence_index: int, guard: str) -> None:
        """The guard terminates the fresh holder inside its first keepalive gap.

        Activation reports applied the moment the session exists; the trusted
        protection's termination of it is the prevented-prefix fact, observed
        from the holder's own phase.
        """
        _, handle = self.handles[-1]
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if handle.facts.get("phase") in ("terminated_by_server", "released_naturally"):
                break
            time.sleep(2.0)
        self.event_evidence[evidence_index]["prevention_prefix"] = {
            "guard": guard,
            "post_activation_phase": handle.facts.get("phase"),
            "prevented": handle.facts.get("phase") == "terminated_by_server",
        }

    def _wrong_action(self) -> None:
        if self.wrong_action == "drop-slot":
            self.topology.drop_replication_slot()
            self.wrong_evidence["slot"] = "dropped mid-run"
        elif self.wrong_action == "promote-standby":
            self.topology.standby_sql("SELECT pg_promote();")
            self.wrong_evidence["standby"] = "promoted to a second primary"
        elif self.wrong_action == "unbounded-feedback":
            self.topology.standby_sql("ALTER SYSTEM SET hot_standby_feedback = 'on';")
            self.topology.standby_sql("SELECT pg_reload_conf();")
            self.wrong_evidence["hot_standby_feedback"] = "on, unbounded"
        else:
            raise ValueError(f"Unknown wrong action: action={self.wrong_action!r}")
        self.applied_actions.append(f"wrong:{self.wrong_action}")

    def run(self) -> dict:
        artifacts = Path(self.args.artifacts_root) / self.args.run_id
        artifacts.mkdir(parents=True, exist_ok=True)
        finished = False
        try:
            self.topology.deploy()
            bootstrap(self.topology.open_workload_connection, self.scale)
            provider = HtapReplicaFreshnessWorkloadProvider(calendar=compressed_calendar(self.scoring_seconds), ledger_dir=artifacts / "ledgers")
            self.clock = RealClock()
            self.runtime = provider.create_runtime(self.topology, self.spec, self.args.run_id, self.clock, persistent_scenario_started=time.monotonic())
            self.runtime.start()
            self.runtime.wait_for_warmup()
            schedule = {event_id: event.start_seconds for event_id, event in self.events.items()}
            while self.runtime.business_seconds_now() < self.scoring_seconds:
                now = self.runtime.business_seconds_now()
                if self.plan_faults:
                    for event_id in EVENT_IDS:
                        if event_id not in self.activated and now >= schedule[event_id]:
                            self.activated.add(event_id)
                            self._activate(self.events[event_id])
                    if self.reference:
                        # Scripted oracle remediation: each action fires once at
                        # its (compressed) business second; the link QoS restore
                        # lands on the control row and the LinkPolicyGovernor
                        # applies it.
                        for action in self.oracle_actions:
                            label = f"oracle:{action.label}"
                            if label not in self.applied_actions and now >= action.at_seconds:
                                self._execute_oracle_action(action)
                    if (
                        self.reference
                        and "oracle:report_role_idle_guard" in self.applied_actions
                        and "frs_long_snapshot_prevented" not in self.activated
                        and now >= schedule["frs_long_snapshot_a"] + 40
                    ):
                        self.activated.add("frs_long_snapshot_prevented")
                        self._prevention_probe(self.events["frs_long_snapshot_a"])
                    if self.wrong_action and now >= schedule["frs_update_surge_a"] + 10:
                        self.activated.add("wrong-action")
                        self._wrong_action()
                self._sample()
                time.sleep(0.5)
            verdict = self._finish(artifacts)
            finished = True
            return verdict
        finally:
            if not finished and getattr(self, "runtime", None) is not None:
                self.runtime.stop_forced()
            if not self.args.keep:
                self.topology.teardown()

    def _finish(self, artifacts: Path) -> dict:
        self.runtime.stop_new_requests()
        self.runtime.drain()
        self.runtime.stop()
        ledgers = self.runtime.ledgers()
        trusted = ledgers["trusted"]
        seal_digest = trusted.seal()
        trusted.verify()
        view = LedgerView(trusted)

        orders = [t for t in view.logical_transactions() if t.tx_kind == "order_submit"]
        jobs = [job for job in view.jobs() if job.job_kind == "report"]
        samples = view.freshness_samples()

        deliveries = ledgers["report_deliveries"].read_all()
        delivered = [record for record in deliveries if record["kind"] == "report_delivered"]
        missed = [record for record in deliveries if record["kind"] == "report_deadline_missed"]
        cancelled = [record for record in deliveries if record["kind"] == "report_attempt_cancelled"]

        def split(records, key="report_kind"):
            critical = [record for record in records if str(record.get(key, "")).startswith("critical")]
            return {"critical": len(critical), "routine": len(records) - len(critical)}

        lags = [sample.lag_seconds for sample in samples if sample.lag_seconds is not None]
        retention_peak = max((entry["slot_retained_bytes"] for entry in self.timeline if "slot_retained_bytes" in entry), default=0)
        verdict = {
            "path": self.args.path,
            "run_id": self.args.run_id,
            "scoring_seconds": self.scoring_seconds,
            "timeline_ratio": round(self.ratio, 4),
            "dataset_scale": {"order_rows": self.scale.order_rows, "event_rows": self.scale.event_rows},
            "applied_actions": self.applied_actions,
            "wrong_evidence": self.wrong_evidence,
            "event_evidence": self.event_evidence,
            "orders": {
                "total": len(orders),
                "good": sum(1 for record in orders if record.good),
                "terminals": {
                    terminal.name: sum(1 for record in orders if record.terminal is terminal)
                    for terminal in {record.terminal for record in orders}
                },
            },
            "reports": {
                "jobs_planned": len(jobs),
                "jobs_delivered_on_time": sum(1 for job in jobs if job.delivered_on_time),
                "ledger_delivered": split(delivered),
                "ledger_deadline_missed": {
                    **split(missed),
                    "reasons": sorted({str(record.get("reason")) for record in missed}),
                },
                "ledger_attempt_cancelled": split(cancelled),
            },
            "freshness": {
                "samples": len(samples),
                "max_lag_seconds": max(lags) if lags else None,
                "nonzero_lag_samples": sum(1 for lag in lags if lag > 0),
                "tail": [
                    {"lag_seconds": sample.lag_seconds, "detail": dict(sample.detail)}
                    for sample in samples[-5:]
                ],
            },
            "replication_end": self.topology.replication_facts(),
            "throttle_facts": self.topology.throttle_facts(),
            "wal_retention": {
                "peak_retained_bytes": retention_peak,
                "max_slot_wal_keep_size_mb": self.topology.config.max_slot_wal_keep_size_mb,
                "max_wal_size_mb": self.topology.config.max_wal_size_mb,
                "wal_status_seen": sorted({entry["slot_wal_status"] for entry in self.timeline if "slot_wal_status" in entry}),
            },
            "business_facts": self.runtime.business_facts(),
            "baseline_facts": self.runtime.baseline_facts(),
            "timeline": self.timeline,
            "ledger_integrity": {
                "trusted_seal_digest": seal_digest,
                "trusted_verify": "ok",
                "trusted_events": {
                    "planned_transaction": trusted.event_count("planned_transaction"),
                    "transaction_terminal": trusted.event_count("transaction_terminal"),
                    "job_planned": trusted.event_count("job_planned"),
                    "job_terminal": trusted.event_count("job_terminal"),
                    "freshness_sample": trusted.event_count("freshness_sample"),
                },
            },
        }
        for capability_id, handle in self.handles:
            CAPABILITIES_BY_ID[capability_id].cleanup(handle)
        verdict["cleanup"] = [
            CAPABILITIES_BY_ID[capability_id].assert_clean(handle) for capability_id, handle in self.handles
        ]
        for name, ledger in (("trusted", trusted), ("report_deliveries", ledgers["report_deliveries"])):
            digest = hashlib.sha256(ledger.path.read_bytes()).hexdigest()
            verdict["ledger_integrity"][f"{name}_sha256"] = digest
        (artifacts / "verdict.json").write_text(json.dumps(verdict, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        print(
            json.dumps(
                {
                    key: verdict[key]
                    for key in ("path", "run_id", "orders", "reports", "freshness", "wal_retention", "replication_end", "applied_actions")
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return verdict


def main() -> int:
    Runner(parse_args()).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
