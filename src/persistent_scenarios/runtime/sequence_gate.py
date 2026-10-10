"""Structured evidence for the Persistent Scenario development gates.

Gates are development-time validation evidence, never model scoring. They are
computed from append-only run facts: arrival evidence, mailbox protocol
history, ledger seals and cleanup records.
"""

from __future__ import annotations

from collections.abc import Mapping

from src.persistent_scenarios.runtime.lifecycle import EventArrivalStatus
from src.persistent_scenarios.model.spec import EventTrigger

# Prefix state promised at follower arrival, in the live impact vocabulary
# reported by the engine's ``_prefix_event_statuses``: an unresolved prefix
# impact is still applied, a resolved one was repaired by the agent, and a
# prevented one never landed.
_RESERVED_PREFIX_STATES = {
    "unresolved-prefix": "applied",
    "resolved-prefix": "resolved",
    "prevented-prefix": "prevented",
}

_OLD_CONTROL_APIS = frozenset({
    "incident_update",
    "incident_close",
    "finding_update",
    "finding_close",
    "inspection_finding",
    "inspection_complete",
    "heartbeat",
    "checkpoint",
    "get_mailbox_status",
    "complete_mailbox_tasks",
})


def _mailbox_actions(persistent_scenario_run) -> list[Mapping[str, object]]:
    return [entry for entry in persistent_scenario_run.action_history if entry.get("api") == "mailbox"]


def _mailbox_contract(persistent_scenario_run, event_activation: bool) -> dict[str, bool]:
    if not event_activation:
        return {
            "mailbox_tool_pass": True,
            "mailbox_read_pass": True,
            "mailbox_write_report_pass": True,
            "mailbox_completion_pass": True,
            "mailbox_wait_pass": True,
            "agent_idle_pass": True,
            "mailbox_session_pass": True,
            "mailbox_conversation_pass": True,
        }

    control_entries = [
        entry
        for entry in persistent_scenario_run.action_history
        if entry.get("surface") == "control" or entry.get("api") in _OLD_CONTROL_APIS
    ]
    control_api_names = {entry.get("api") for entry in control_entries}
    mailbox_entries = _mailbox_actions(persistent_scenario_run)
    mailbox_tool_pass = bool(mailbox_entries) and control_api_names == {"mailbox"}

    read_entries = [
        entry
        for entry in mailbox_entries
        if isinstance(entry.get("args"), Mapping) and entry["args"].get("operation") == "read"
    ]
    mailbox_read_pass = bool(read_entries) and all(
        isinstance(entry.get("result"), Mapping)
        and isinstance(entry["result"].get("pending"), list)
        and isinstance(entry["result"].get("completed"), list)
        for entry in read_entries
    )

    write_entries = [
        entry
        for entry in mailbox_entries
        if isinstance(entry.get("args"), Mapping) and entry["args"].get("operation") == "write"
    ]
    mailbox_write_report_pass = bool(write_entries) and all(
        isinstance(entry["args"].get("task_ids"), list)
        and bool(entry["args"]["task_ids"])
        and isinstance(entry["args"].get("report"), Mapping)
        and isinstance(entry["args"]["report"].get("diagnosis"), Mapping)
        and isinstance(entry["args"]["report"].get("outcome"), Mapping)
        and isinstance(entry["args"]["report"].get("summary"), str)
        and isinstance(entry.get("result"), Mapping)
        for entry in write_entries
    )

    completed_by_id = {
        item["task_id"]: item
        for item in persistent_scenario_run.mailbox_state.get("completed", [])
        if isinstance(item, Mapping) and item.get("task_id") is not None
    }

    def write_completed(entry: Mapping[str, object]) -> bool:
        args = entry.get("args")
        result = entry.get("result")
        if not isinstance(args, Mapping) or not isinstance(result, Mapping):
            return False
        task_ids = args.get("task_ids")
        completed_task_ids = result.get("completed_task_ids")
        if not isinstance(task_ids, list) or not isinstance(completed_task_ids, list):
            return False
        return all(task_id in completed_by_id and task_id in completed_task_ids for task_id in task_ids)

    mailbox_completion_pass = bool(write_entries) and all(write_completed(entry) for entry in write_entries)

    wait_entries = [
        entry
        for entry in mailbox_entries
        if isinstance(entry.get("args"), Mapping) and entry["args"].get("operation") == "wait"
    ]
    started_waits = [
        entry for entry in persistent_scenario_run.canonical_timeline if entry.get("kind") == "mailbox_wait_started"
    ]
    completed_waits = [
        entry for entry in persistent_scenario_run.canonical_timeline if entry.get("kind") == "mailbox_wait_completed"
    ]
    published_during_wait = any(
        any(
            started["sequence"] < change["sequence"] < completed["sequence"]
            for started in started_waits
            for completed in completed_waits
            if started.get("payload", {}).get("session_id") == completed.get("payload", {}).get("session_id")
        )
        for change in persistent_scenario_run.canonical_timeline
        if change.get("kind") == "mailbox_document_changed" and change.get("payload", {}).get("operation") == "published"
    )
    mailbox_wait_pass = bool(wait_entries) and bool(started_waits) and bool(completed_waits) and published_during_wait

    agent_states = [
        entry.get("payload", {}).get("state")
        for entry in persistent_scenario_run.canonical_timeline
        if entry.get("kind") == "agent_mailbox_state"
    ]
    agent_idle_pass = "idle" in agent_states and "woken" in agent_states

    session_ids = {
        entry.get("payload", {}).get("session_id")
        for entry in persistent_scenario_run.canonical_timeline
        if entry.get("kind") == "agent_session_started"
    }
    session_records = getattr(persistent_scenario_run, "agent_sessions", [])
    mailbox_session_pass = session_ids == {"session-0001"} and len(session_records) == 1
    action_session_ids = {entry.get("session_id") for entry in persistent_scenario_run.action_history}
    mailbox_session_pass = mailbox_session_pass and action_session_ids <= {"session-0001"}
    conversation_phases = getattr(persistent_scenario_run, "agent_conversation_phases", [])
    mailbox_conversation_pass = bool(conversation_phases) and all(
        phase.get("session_id", "session-0001") == "session-0001" for phase in conversation_phases
    )
    return {
        "mailbox_tool_pass": mailbox_tool_pass,
        "mailbox_read_pass": mailbox_read_pass,
        "mailbox_write_report_pass": mailbox_write_report_pass,
        "mailbox_completion_pass": mailbox_completion_pass,
        "mailbox_wait_pass": mailbox_wait_pass,
        "agent_idle_pass": agent_idle_pass,
        "mailbox_session_pass": mailbox_session_pass,
        "mailbox_conversation_pass": mailbox_conversation_pass,
    }


def _prefix_state_preserved(gate: str, persistent_scenario_run) -> tuple[bool, str | None]:
    """Under a prefix gate, the second event must have arrived while the first
    event was in the state the gate name promises (unresolved / prevented /
    resolved), without waiting for it."""
    events = tuple(persistent_scenario_run.spec.events)
    if len(events) < 2 or gate not in _RESERVED_PREFIX_STATES:
        return True, None
    prefix_id = events[0].event_id
    follower_id = events[1].event_id
    follower_arrival = next(
        (
            entry
            for entry in persistent_scenario_run.canonical_timeline
            if entry.get("kind") == "event_arrival_recorded" and entry.get("event_id") == follower_id
        ),
        None,
    )
    if follower_arrival is None:
        return False, None
    prefix_status = follower_arrival.get("payload", {}).get("prefix_event_statuses", {}).get(prefix_id)
    expected = _RESERVED_PREFIX_STATES[gate]
    return prefix_status == expected, prefix_status


def build_gate_result(
    gate: str,
    persistent_scenario_run,
    *,
    event_activation: bool,
    runtime_evidence: Mapping[str, object],
    cleanup_errors: tuple[Mapping[str, object], ...],
) -> dict[str, object]:
    expected_event_ids = {event.event_id for event in persistent_scenario_run.spec.events}
    arrivals = {
        event.event_id: event.arrival
        for event in persistent_scenario_run.events
        if event.arrival is not None
    }
    event_activation_pass = not event_activation or set(arrivals) == expected_event_ids and all(
        arrival.status in {EventArrivalStatus.APPLIED, EventArrivalStatus.PREVENTED}
        for arrival in arrivals.values()
    )
    alert_event_ids = {
        event.event_id
        for event in persistent_scenario_run.spec.events
        if event.trigger is EventTrigger.ALERT
    }
    alert_task_ids = {
        entry["event_id"]
        for entry in persistent_scenario_run.canonical_timeline
        if entry.get("kind") == "alert_published" and entry.get("event_id") is not None
    }
    alert_pass = not event_activation or alert_task_ids == alert_event_ids
    cleanup_event_ids = {
        item.get("event_id")
        for item in persistent_scenario_run.cleanup
        if item.get("owner") == "event" and item.get("status") == "cleaned"
    }
    cleanup_pass = not cleanup_errors and cleanup_event_ids == set(arrivals)
    session_ids = {
        entry.get("payload", {}).get("session_id")
        for entry in persistent_scenario_run.canonical_timeline
        if entry.get("kind") == "agent_session_started"
    }
    single_mailbox_session_pass = not event_activation or session_ids == {"session-0001"}
    prefix_state_preserved, prefix_status = _prefix_state_preserved(gate, persistent_scenario_run)
    environment_alive = runtime_evidence.get("environment_deployed") is True
    ledger_seal_pass = not event_activation or (
        bool(persistent_scenario_run.ledgers)
        and runtime_evidence.get("ledger_event_count", 0) > 0
        and runtime_evidence.get("ledgers_sealed") is True
    )
    telemetry_measurable = runtime_evidence.get("telemetry_sample_count", 0) > 0
    mailbox_contract = _mailbox_contract(persistent_scenario_run, event_activation and gate != "no-agent")
    mailbox_contract_pass = all(mailbox_contract.values())
    result = {
        "gate": gate,
        "sequence_pass": all((
            event_activation_pass,
            alert_pass,
            single_mailbox_session_pass,
            prefix_state_preserved,
            environment_alive,
            ledger_seal_pass,
            telemetry_measurable,
            cleanup_pass,
            mailbox_contract_pass,
        )),
        "event_activation_pass": event_activation_pass,
        "alert_pass": alert_pass,
        "single_mailbox_session_pass": single_mailbox_session_pass,
        "prefix_state_preserved": prefix_state_preserved,
        "prefix_status": prefix_status,
        "environment_alive": environment_alive,
        "ledger_seal_pass": ledger_seal_pass,
        "telemetry_measurable": telemetry_measurable,
        "final_teardown_pass": cleanup_pass,
        "mailbox_contract_pass": mailbox_contract_pass,
        **mailbox_contract,
        "cleanup_errors": [dict(item) for item in cleanup_errors],
        "runtime_evidence": dict(runtime_evidence),
    }
    return result
