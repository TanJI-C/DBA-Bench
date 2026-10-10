"""Instance 4 (tidb_cdc_downstream_freshness) event capability bindings.

Each capability follows the core ``PersistentScenarioEventCapability``
protocol: bounded declaration, activate with applied|prevented evidence,
symptom-only alerts, and cleanup that reverts only capability-owned state -
durable operator repairs (restored privileges, retuned batch schedules) are
run facts and are never undone.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Mapping

from src.persistent_scenarios.backend.contracts import (
    CapabilityDeclaration,
    EventActivationResult,
    EventAlertPayload,
    EventAttemptEvidence,
    AppliedEvidence,
    OwnershipMode,
    ResourceOwnership,
)
from src.persistent_scenarios.runtime.lifecycle import (
    EventArrivalStatus,
)

from .schema import BATCH_CONTROL_TABLE, DOWNSTREAM_DATABASE, OPS_DATABASE, TRAFFIC_CONTROL_TABLE, UPSTREAM_DATABASE
from .safepoint import sample_upstream_gc_state

_SINK_USER = "cdc_sink"
_POLL_SECONDS = 0.5


def _now(clock) -> float:
    return clock.monotonic()


def _wait_for(clock, stop, predicate, budget_seconds: float):
    deadline = clock.monotonic() + budget_seconds
    while True:
        value = predicate()
        if value is not None:
            return value
        if clock.monotonic() >= deadline:
            return None
        clock.wait_until(clock.monotonic() + _POLL_SECONDS, stop)


class _CdcCapabilityBase:
    """Shared SQL surfaces: the environment must expose upstream()/downstream()
    connection factories plus a monotonic clock (core EventActivationContext)."""

    capability_id: str = ""

    @staticmethod
    def _event(event) -> object:
        return event

    def _declaration(self, event, resources, max_activation_seconds: int) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=resources,
            max_activation_seconds=max_activation_seconds,
        )


# ---------------------------------------------------------------------------
# Event 1 / 4: downstream fulfilment batch window
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class _BatchWindowHandle:
    event_id: str
    clock: object
    stop: threading.Event = field(default_factory=threading.Event)
    closer: threading.Thread | None = None
    observation: dict = field(default_factory=dict)
    finished: bool = False


class CdcDownstreamBatchCapability(_CdcCapabilityBase):
    """A fulfilment-side batch processing window competes with the sink writes.

    The window is scheduled through the public ``batch_control`` row. Operator
    retunes (batch_rows / batch_pause_seconds changed away from the campaign
    defaults) are durable and are respected by later occurrences; cleanup only
    closes the enabled flag if this handle still owns the window.
    """

    capability_id = "cdc_downstream_batch"
    _PARAMS = frozenset({"batch_rows", "batch_pause_seconds", "window_seconds", "campaign"})
    _CAMPAIGN_NOTE_PREFIX = "campaign:"

    def declaration(self, event):
        return self._declaration(
            event,
            (ResourceOwnership(
                resource_key=f"downstream:batch-schedule:{event.entity}",
                resource_kind="downstream_control_row",
                mode=OwnershipMode.EXCLUSIVE,
            ),),
            max_activation_seconds=60,
        )

    def activate(self, context) -> EventActivationResult:
        event = context.event
        unknown = set(event.payload) - self._PARAMS
        if unknown:
            raise ValueError(f"unknown payload fields for {event.event_id}: {sorted(unknown)!r}")
        batch_rows = int(event.payload["batch_rows"])
        pause = float(event.payload["batch_pause_seconds"])
        window_seconds = float(event.payload["window_seconds"])
        campaign = str(event.payload["campaign"])
        started_at = _now(context.clock)

        conn = context.environment.downstream()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT enabled, batch_rows, batch_pause_seconds, note FROM "
                f"{DOWNSTREAM_DATABASE}.{BATCH_CONTROL_TABLE} WHERE id = 1"
            )
            previous = cursor.fetchall()[0]
            note = str(previous[3])
            operator_tuned = not note.startswith(self._CAMPAIGN_NOTE_PREFIX) and note != "batch window closed"
            effective_rows = int(previous[1]) if operator_tuned else batch_rows
            effective_pause = float(previous[2]) if operator_tuned else pause
            new_note = note if operator_tuned else f"{self._CAMPAIGN_NOTE_PREFIX}{campaign}"
            cursor.execute(
                f"UPDATE {DOWNSTREAM_DATABASE}.{BATCH_CONTROL_TABLE} SET enabled = 1, "
                f"batch_rows = {effective_rows}, batch_pause_seconds = {effective_pause}, "
                f"note = '{new_note}', updated_at = NOW(3) WHERE id = 1"
            )
        finally:
            conn.close()

        handle = _BatchWindowHandle(event_id=event.event_id, clock=context.clock)

        def window_effect():
            conn = context.environment.downstream()
            try:
                cursor = conn.cursor()

                # Window advancement is observed on the batch_no marker stream,
                # not the staging row count: each batch transaction writes the
                # new batch and drops the previous one in one commit, so the
                # row count returns to rest after the first run and a count
                # baseline would leave every later window unobservable
                # (t=65 rerun).
                def latest_batch_no() -> int:
                    cursor.execute(
                        f"SELECT COALESCE(MAX(batch_no), -1) "
                        f"FROM {DOWNSTREAM_DATABASE}.fulfilment_batches"
                    )
                    return int(cursor.fetchall()[0][0])

                baseline = latest_batch_no()

                def batch_advancement():
                    latest = latest_batch_no()
                    return {"batches_advanced": latest - baseline} if latest > baseline else None

                evidence = _wait_for(
                    context.clock, handle.stop, batch_advancement, budget_seconds=30.0,
                )
                if evidence is not None:
                    handle.observation.update(evidence)
                    handle.finished = True
            finally:
                conn.close()

        thread = threading.Thread(target=window_effect, name=f"{event.event_id}-effect", daemon=True)
        thread.start()
        evidence = _wait_for(context.clock, handle.stop,
                             lambda: handle.observation or None, budget_seconds=45.0)
        if evidence is None:
            raise RuntimeError(
                f"batch window did not produce observed batch advancement: "
                f"event_id={event.event_id!r}, batch_rows={batch_rows}, pause={pause}"
            )

        def close_window_later():
            deadline = time.monotonic() + window_seconds
            while time.monotonic() < deadline and not handle.stop.is_set():
                handle.stop.wait(1.0)
            conn = context.environment.downstream()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE {DOWNSTREAM_DATABASE}.{BATCH_CONTROL_TABLE} SET enabled = 0, "
                    f"updated_at = NOW(3) WHERE id = 1 AND note LIKE '{self._CAMPAIGN_NOTE_PREFIX}%'"
                )
            finally:
                conn.close()

        handle.closer = threading.Thread(target=close_window_later, name=f"{event.event_id}-closer", daemon=True)
        handle.closer.start()
        attempt = EventAttemptEvidence(attempted_at_monotonic=started_at, detail={
            "batch_rows_requested": batch_rows, "batch_pause_seconds_requested": pause,
            "effective_batch_rows": effective_rows, "effective_batch_pause_seconds": effective_pause,
            "operator_tuned_schedule": operator_tuned,
        })
        return EventActivationResult(
            handle=handle, attempt=attempt,
            applied=AppliedEvidence(observed_at_monotonic=_now(context.clock), facts={
                "batch_window_open": True,
                "batches_advanced_during_activation": evidence["batches_advanced"],
                "effective_schedule": {"batch_rows": effective_rows, "batch_pause_seconds": effective_pause},
                "window_seconds": window_seconds,
            }),
            prevented=None,
        )

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="下游履约批处理窗口开启",
            symptoms=(
                "履约侧批处理开始大批量写入，与订单读模型更新共享下游资源",
                "批处理持续期间下游写入延迟与资源占用上升",
            ),
            severity="notice",
            category="downstream_batch",
        )

    def cleanup(self, handle) -> None:
        handle.stop.set()
        if handle.closer is not None:
            handle.closer.join(timeout=30)

    def assert_clean(self, handle) -> Mapping[str, object]:
        return {"event_id": handle.event_id, "window_closed": handle.finished or handle.stop.is_set()}


# ---------------------------------------------------------------------------
# Event 2: upstream schema release meets downstream privilege drift
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Event 3: order peak on the upstream order store
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class _OrderPeakHandle:
    event_id: str
    clock: object
    peak_rate: float
    observation: dict = field(default_factory=dict)


class CdcOrderPeakCapability(_CdcCapabilityBase):
    """Raises the externally planned order arrival rate through the public
    traffic-control row. The rate stays raised until retuned durably."""

    capability_id = "cdc_order_peak"
    _PARAMS = frozenset({"target_orders_per_sec", "note"})

    def declaration(self, event):
        return self._declaration(
            event,
            (ResourceOwnership(
                resource_key=f"upstream:traffic-control:{event.entity}",
                resource_kind="upstream_control_row",
                mode=OwnershipMode.EXCLUSIVE,
            ),),
            max_activation_seconds=60,
        )

    def activate(self, context) -> EventActivationResult:
        event = context.event
        unknown = set(event.payload) - self._PARAMS
        if unknown:
            raise ValueError(f"unknown payload fields for {event.event_id}: {sorted(unknown)!r}")
        target_rate = float(event.payload["target_orders_per_sec"])
        note = str(event.payload["note"])
        started_at = _now(context.clock)
        conn = context.environment.upstream()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT target_orders_per_sec FROM {OPS_DATABASE}.{TRAFFIC_CONTROL_TABLE} WHERE id = 1")
            previous_rate = float(cursor.fetchall()[0][0])
            cursor.execute(
                f"UPDATE {OPS_DATABASE}.{TRAFFIC_CONTROL_TABLE} SET target_orders_per_sec = {target_rate}, "
                f"note = '{note}', updated_at = NOW(3) WHERE id = 1"
            )
        finally:
            conn.close()

        handle = _OrderPeakHandle(event_id=event.event_id, clock=context.clock, peak_rate=target_rate)

        def arrival_rate():
            conn = context.environment.upstream()
            try:
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {UPSTREAM_DATABASE}.orders WHERE order_id >= 1000000")
                return float(cursor.fetchall()[0][0])
            finally:
                conn.close()

        baseline = arrival_rate()
        observed = _wait_for(
            context.clock, threading.Event(),
            lambda: {"rows": arrival_rate() - baseline} if arrival_rate() - baseline >= 2 else None,
            budget_seconds=30.0,
        )
        if observed is None:
            raise RuntimeError(
                f"order peak did not raise observed arrivals: event_id={event.event_id!r}, "
                f"target_rate={target_rate}, baseline_rows={baseline}"
            )
        handle.observation.update(observed)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(attempted_at_monotonic=started_at, detail={
                "previous_rate": previous_rate, "target_rate": target_rate, "note": note,
            }),
            applied=AppliedEvidence(observed_at_monotonic=_now(context.clock), facts={
                "target_orders_per_sec": target_rate,
                "rows_added_during_activation": observed["rows"],
            }),
            prevented=None,
        )

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="订单提交进入高峰段",
            symptoms=(
                "上游订单提交速率明显高于日常水平并持续",
                "下游复制与批处理需要跟上涨峰写入",
            ),
            severity="notice",
            category="order_peak",
        )

    def cleanup(self, handle) -> None:
        pass  # the raised rate is an external business input, not injector state

    def assert_clean(self, handle) -> Mapping[str, object]:
        return {"event_id": handle.event_id, "peak_rate": handle.peak_rate}


@dataclass(slots=True)
class _SchemaReleaseHandle:
    event_id: str
    clock: object
    released_column: str
    probe_order_id: int
    stall_started_at: float
    pin_release_after_seconds: float
    observation: dict = field(default_factory=dict)


class CdcSchemaReleaseCapability(_CdcCapabilityBase):
    """A normal upstream schema release meets downstream privilege drift and
    escalates into a GC safepoint checkpoint stall (composite root cause).

    Factor A: the activation applies the drift (sink user loses ALTER, live
    sink sessions are invalidated) and then executes the normal upstream
    release. On TiCDC v8.1.0 the DDL apply then fails on the sink: the
    changefeed keeps reporting ``state=normal`` while the checkpoint freezes
    and downstream visibility stops - verified by a probe order that never
    arrives.

    Factor B develops BECAUSE of factor A: the retrying changefeed pins its
    checkpoint, the pinned checkpoint holds the upstream GC safepoint
    (``tikv_gc_safe_point`` freezes), and after the fail-fast pin release the
    replication stays parked until the operator secures the GC boundary and
    resumes it. Repairing only one factor leaves the watermark contract
    honestly unmet; the activation records the stall anchor and the real
    upstream GC surfaces as applied evidence.
    """

    capability_id = "cdc_schema_release"
    _PARAMS = frozenset({
        "column_name", "column_type", "release_note", "probe_order_id",
        "gc_pin_release_seconds", "upstream_gc_life_time",
    })
    _VISIBILITY_STALL_SECONDS = 20.0

    def declaration(self, event):
        return self._declaration(
            event,
            (ResourceOwnership(
                resource_key=f"upstream:schema:orders:{event.entity}",
                resource_kind="upstream_schema",
                mode=OwnershipMode.EXCLUSIVE,
            ),
             ResourceOwnership(
                resource_key=f"downstream:sink-privilege:{event.entity}",
                resource_kind="downstream_privilege",
                mode=OwnershipMode.EXCLUSIVE,
            ),
             ResourceOwnership(
                resource_key=f"upstream:gc-safepoint:{event.entity}",
                resource_kind="upstream_gc_safepoint",
                mode=OwnershipMode.EXCLUSIVE,
            ),),
            max_activation_seconds=120,
        )

    def activate(self, context) -> EventActivationResult:
        event = context.event
        unknown = set(event.payload) - self._PARAMS
        if unknown:
            raise ValueError(f"unknown payload fields for {event.event_id}: {sorted(unknown)!r}")
        column = str(event.payload["column_name"])
        column_type = str(event.payload["column_type"])
        note = str(event.payload["release_note"])
        probe_order_id = int(event.payload["probe_order_id"])
        pin_release_after_seconds = float(event.payload["gc_pin_release_seconds"])
        gc_life_time = str(event.payload["upstream_gc_life_time"])
        started_at = _now(context.clock)

        conn = context.environment.downstream()
        try:
            cursor = conn.cursor()
            cursor.execute(f"REVOKE ALTER ON *.* FROM '{_SINK_USER}'@'%'")
            cursor.execute("SELECT id FROM information_schema.processlist WHERE user = %s", (_SINK_USER,))
            sink_sessions = [int(row[0]) for row in cursor.fetchall()]
            for session_id in sink_sessions:
                cursor.execute(f"KILL {session_id}")
        finally:
            conn.close()

        conn = context.environment.upstream()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"ALTER TABLE {UPSTREAM_DATABASE}.orders ADD COLUMN {column} {column_type} "
                f"DEFAULT NULL COMMENT '{note}'"
            )
        finally:
            conn.close()

        # probe: a fresh source commit must become visible downstream; the
        # stalled apply leaves it missing while the changefeed state stays normal
        marker = f"probe-{probe_order_id}"
        conn = context.environment.upstream()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO {UPSTREAM_DATABASE}.orders "
                "(order_id, version, state, amount, marker, updated_at) VALUES "
                f"({probe_order_id}, 1, 'paid', 13.37, '{marker}', NOW(3))"
            )
        finally:
            conn.close()

        handle = _SchemaReleaseHandle(event_id=event.event_id, clock=context.clock,
                                      released_column=column, probe_order_id=probe_order_id,
                                      stall_started_at=_now(context.clock),
                                      pin_release_after_seconds=pin_release_after_seconds)

        def probe_visible():
            conn = context.environment.downstream()
            try:
                cursor = conn.cursor()
                cursor.execute(f"SELECT marker FROM {DOWNSTREAM_DATABASE}.orders WHERE order_id = {probe_order_id}")
                return cursor.fetchall()
            finally:
                conn.close()

        # _wait_for resolves on the first non-None value, so the predicate must
        # return evidence only when the probe is missing; False would otherwise
        # count as observed drift even though the probe arrived downstream
        stall = _wait_for(context.clock, threading.Event(),
                          lambda: {"probe_missing": True} if probe_visible() == () else None,
                          budget_seconds=self._VISIBILITY_STALL_SECONDS)
        if stall is None:
            raise RuntimeError(
                f"schema release did not stall downstream visibility (probe {probe_order_id} arrived): "
                f"the drift/apply failure is not reproduced on this version"
            )

        # the pinned checkpoint holds the upstream GC safepoint: record the
        # real upstream GC surfaces as the composite factor-B evidence
        conn = context.environment.upstream()
        try:
            gc_state = dict(sample_upstream_gc_state(conn.cursor()))
        finally:
            conn.close()

        handle.observation.update({
            "probe_order_id": probe_order_id,
            "probe_missing_seconds": self._VISIBILITY_STALL_SECONDS,
            "invalidated_sink_sessions": len(sink_sessions),
            "released_column": column,
            "stall": {
                "stall_started_at_monotonic": handle.stall_started_at,
                "pin_release_after_seconds": pin_release_after_seconds,
                "upstream_gc_life_time": gc_life_time,
                **gc_state,
            },
        })
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(attempted_at_monotonic=started_at, detail={
                "released_column": column, "column_type": column_type,
                "sink_sessions_invalidated": len(sink_sessions),
            }),
            applied=AppliedEvidence(observed_at_monotonic=_now(context.clock), facts=dict(handle.observation)),
            prevented=None,
        )

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="履约读模型更新停滞",
            symptoms=(
                "订单提交侧写入正常，履约侧长时间看不到新订单",
                "下游读模型的最新订单停留在较早时间点",
            ),
            severity="high",
            category="downstream_visibility",
        )

    def cleanup(self, handle) -> None:
        pass  # the release column and the probe order are run facts; nothing to revert

    def assert_clean(self, handle) -> Mapping[str, object]:
        return {"event_id": handle.event_id, "released_column": handle.released_column}
