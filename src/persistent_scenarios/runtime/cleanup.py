"""Reverse-order cleanup of capability-owned Event resources."""

from __future__ import annotations


def cleanup_activated_events(run, activation_order, activation_handles, event_provider) -> list[dict[str, object]]:
    """Clean up activated events in reverse activation order.

    Cleanup only reclaims infrastructure owned by each capability handle; it
    never resets shared state and therefore never undoes a legitimate repair.
    """
    errors: list[dict[str, object]] = []
    pending = list(reversed(activation_order))
    while pending:
        deferred = []
        progress = False
        round_errors = {}
        for event_run in pending:
            handle = activation_handles[event_run.event_id]
            try:
                event_provider.cleanup(handle)
                facts = event_provider.assert_clean(handle)
                event_run.cleanup_facts = dict(facts)
                progress = True
                run.cleanup.append({
                    "owner": "event",
                    "event_id": event_run.event_id,
                    "status": "cleaned",
                    "facts": dict(facts),
                })
                run.append_timeline(
                    owner="cleanup",
                    kind="cleanup_completed",
                    event_id=event_run.event_id,
                    payload={"status": "cleaned"},
                )
            except Exception as exc:
                item = {
                    "owner": "event",
                    "event_id": event_run.event_id,
                    "status": "failed",
                    "error": repr(exc),
                }
                round_errors[event_run.event_id] = item
                deferred.append(event_run)
                run.append_timeline(
                    owner="cleanup",
                    kind="cleanup_deferred",
                    event_id=event_run.event_id,
                    payload={"error": repr(exc)},
                )
        if not deferred:
            break
        if not progress:
            for event_run in deferred:
                item = round_errors[event_run.event_id]
                errors.append(item)
                run.cleanup.append(item)
            break
        pending = deferred
    return errors
