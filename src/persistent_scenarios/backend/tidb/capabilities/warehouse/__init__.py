"""Instance-native Event capabilities for tidb_olap_warehouse_delivery.

Each capability expresses external intent as real effects on the public control plane
(queue rows, audited configuration releases) and returns structured arrival facts.
Prevention is never synthesized: a capability that cannot complete its effect raises,
and only a genuinely blocked attempt returns prevented evidence.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import threading

from src.persistent_scenarios.backend.contracts import (
    CapabilityDeclaration,
    EventActivationContext,
    EventActivationResult,
    EventAlertPayload,
    OwnershipMode,
    ResourceOwnership,
)
from src.persistent_scenarios.runtime.lifecycle import (
    AppliedEvidence,
    EventAttemptEvidence,
)

from .reports import REQUIRED_REPORT_IDS
from .runtime import WarehouseDeliveryRuntime
from .schema import BATCH_A_ID, BATCH_B_ID

CAPABILITY_BATCH_ARRIVAL = "tidb5_olap_batch_arrival"
CAPABILITY_REPORT_BATCH = "tidb5_olap_report_batch"
CAPABILITY_BACKFILL_ARRIVAL = "tidb5_olap_backfill_arrival"
CAPABILITY_QUEUE_CONCURRENCY_RELEASE = "tidb5_olap_queue_concurrency_release"

CAPABILITIES = (
    CAPABILITY_BATCH_ARRIVAL,
    CAPABILITY_REPORT_BATCH,
    CAPABILITY_BACKFILL_ARRIVAL,
    CAPABILITY_QUEUE_CONCURRENCY_RELEASE,
)

# Provisional deadline offsets from the activating event, seconds (the authoritative
# acceptance deadlines are the spec DeliverableContract values).
REPORT_DEADLINE_OFFSETS = {
    "region_daily_revenue": 600,
    "item_margin_top50": 720,
    "warehouse_throughput": 840,
    "channel_settlement": 600,
    "region_group_share": 840,
}
INGEST_DEADLINE_OFFSET = 600
CONCURRENCY_RELEASE_MAX_WORKERS = 6
MAX_ACTIVATION_SECONDS = 120


def _batch_id_from_payload(payload) -> int:
    batch = int(payload.get("batch", 0))
    if batch not in {BATCH_A_ID, BATCH_B_ID}:
        raise ValueError(f"warehouse occurrence payload must select batch 1 or 2: payload={dict(payload)!r}")
    return batch


@dataclass(frozen=True, slots=True)
class _BatchHandle:
    event_id: str
    batch_id: int
    ingest_job_id: str
    analyze_release: dict


class BatchArrivalCapability:
    """Batch data arrival: staged-batch ingest submission plus the analyze release."""

    capability_id = CAPABILITY_BATCH_ARRIVAL

    def __init__(self, runtime_provider: Callable[[], WarehouseDeliveryRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership(
                    resource_key=f"queue:ingest:{event.entity}", resource_kind="queue_row", mode=OwnershipMode.EXCLUSIVE
                ),
                ResourceOwnership(
                    resource_key=f"config:batch_registry:{event.entity}", resource_kind="control_table_row",
                    mode=OwnershipMode.EXCLUSIVE,
                ),
            ),
            max_activation_seconds=MAX_ACTIVATION_SECONDS,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        batch_id = _batch_id_from_payload(context.event.payload)
        analyze_after_ingest = bool(context.event.payload.get("analyze_after_ingest", True))
        # The scheduler release decides whether ingest workers maintain statistics after
        # publishing this batch; batch A ships with the release turned off (t=15).
        analyze_release = runtime.set_analyze_after_ingest(batch_id, analyze_after_ingest, at)
        ingest_job_id = runtime.submit_ingest(batch_id, at + INGEST_DEADLINE_OFFSET)
        handle = _BatchHandle(
            event_id=context.event.event_id,
            batch_id=batch_id,
            ingest_job_id=ingest_job_id,
            analyze_release=analyze_release,
        )
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=at,
                detail={"batch_id": batch_id, "ingest_job_id": ingest_job_id},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={"ingest_job_submitted": True, "analyze_release": analyze_release},
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _BatchHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="Warehouse ingest batch finished and report delivery is pending",
            symptoms=(
                "a new ingest batch was published into the warehouse fact table",
                "queued report jobs are waiting longer than the normal rhythm",
            ),
            severity="warning",
            category="warehouse_batch",
        )

    def cleanup(self, handle: _BatchHandle) -> None:
        # Batch data and released configuration are legitimate business state; the
        # environment is discarded whole after final evaluation.
        return None

    def assert_clean(self, handle: _BatchHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


@dataclass(frozen=True, slots=True)
class _ReportBatchHandle:
    event_id: str
    batch_id: int
    job_ids: tuple[str, ...]


class ReportBatchCapability:
    """Submits the per-batch required report delivery list bound to a batch cutoff."""

    capability_id = CAPABILITY_REPORT_BATCH

    def __init__(self, runtime_provider: Callable[[], WarehouseDeliveryRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership(
                    resource_key=f"queue:report_batch:{event.entity}", resource_kind="queue_row",
                    mode=OwnershipMode.EXCLUSIVE,
                ),
            ),
            max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        batch_id = _batch_id_from_payload(context.event.payload)
        job_ids = tuple(
            runtime.submit_required_report(report_id, batch_id, at + REPORT_DEADLINE_OFFSETS[report_id])
            for report_id in REQUIRED_REPORT_IDS
        )
        handle = _ReportBatchHandle(event_id=context.event.event_id, batch_id=batch_id, job_ids=job_ids)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=at, detail={"batch_id": batch_id, "job_count": len(job_ids)}
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(), facts={"submitted_job_ids": list(job_ids)}
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _ReportBatchHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="A required report delivery batch is due for downstream consumers",
            symptoms=(
                "five required reports queued with business deadlines",
                "delivery latency is measured from submission including queueing",
            ),
            severity="notice",
            category="warehouse_delivery",
        )

    def cleanup(self, handle: _ReportBatchHandle) -> None:
        return None

    def assert_clean(self, handle: _ReportBatchHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


@dataclass(frozen=True, slots=True)
class _BackfillHandle:
    event_id: str
    batch_id: int
    wave: threading.Thread


class BackfillArrivalCapability:
    """Upstream correction wave: the backfill that lands inside
    batch A's report window really rewrites the stage tables and atomically
    re-publishes batch A, so batch-A report truth changes mid-run and report
    deliveries over superseded inputs are honestly incomplete.

    The wave is real driver activity on its own connection (stage rewrite UPDATEs,
    one DELETE+INSERT publication transaction, registry republish marker, audit
    rows); activation returns immediately and the wave thread is joined by tests.
    """

    capability_id = CAPABILITY_BACKFILL_ARRIVAL

    def __init__(self, runtime_provider: Callable[[], WarehouseDeliveryRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership("stage:correction_wave", "stage_table", OwnershipMode.EXCLUSIVE),
                ResourceOwnership(
                    resource_key=f"registry:republish:{event.entity}", resource_kind="control_table_row",
                    mode=OwnershipMode.EXCLUSIVE,
                ),
            ),
            max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        batch_id = int(context.event.payload.get("batch", BATCH_A_ID))
        wave = runtime.start_correction_wave(batch_id, at)
        handle = _BackfillHandle(event_id=context.event.event_id, batch_id=batch_id, wave=wave)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(attempted_at_monotonic=at, detail={"correction_wave_batch": batch_id}),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={"correction_wave_started": True, "batch_id": batch_id},
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _BackfillHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="An upstream correction wave is re-delivering warehouse batch data",
            symptoms=(
                "an upstream wave is rewriting staged batch payloads and re-publishing a batch",
                "report deliveries over the affected batch may no longer match the final input",
            ),
            severity="warning",
            category="warehouse_backfill",
        )

    def cleanup(self, handle: _BackfillHandle) -> None:
        if handle.wave.is_alive():
            handle.wave.join(timeout=300)
            if handle.wave.is_alive():
                raise RuntimeError(f"correction wave did not finish during cleanup: event_id={handle.event_id!r}")

    def assert_clean(self, handle: _BackfillHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


@dataclass(frozen=True, slots=True)
class _ReleaseHandle:
    event_id: str
    queue_config: dict
    maintenance: threading.Thread


class QueueConcurrencyReleaseCapability:
    """External scheduler decision that widens the analytics worker pool.

    The same release window carries the scheduler's real
    maintenance pass - a session running FULL ANALYZE over the non-target staging
    tables rewritten by the correction wave (their statistics went stale). The
    maintenance task shares the window and the observation tools with the widened
    report pool, so latency explanations in this window are only separable by
    cross-evidence (config audit, target objects, phase comparison).
    """

    capability_id = CAPABILITY_QUEUE_CONCURRENCY_RELEASE

    def __init__(self, runtime_provider: Callable[[], WarehouseDeliveryRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership("config:queue_config", "control_table_row", OwnershipMode.EXCLUSIVE),
                ResourceOwnership("maintenance:stage_statistics", "maintenance_session", OwnershipMode.EXCLUSIVE),
            ),
            max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        max_workers = int(context.event.payload.get("max_workers", CONCURRENCY_RELEASE_MAX_WORKERS))
        if max_workers < 1:
            raise ValueError(f"released queue worker count must be positive: max_workers={max_workers}")
        new_state = runtime.apply_queue_config_release(at, max_workers=max_workers)
        maintenance = runtime.start_maintenance_analyze(at)
        handle = _ReleaseHandle(event_id=context.event.event_id, queue_config=new_state, maintenance=maintenance)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(attempted_at_monotonic=at, detail={"max_workers": max_workers}),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={"queue_config": new_state, "maintenance_analyze_started": True},
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _ReleaseHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="Reporting scheduler widened the analytics worker pool",
            symptoms=(
                "analytics worker pool widened by an external scheduler release",
                "concurrent heavy reports may compete for memory under the low quota",
            ),
            severity="notice",
            category="warehouse_scheduler",
        )

    def cleanup(self, handle: _ReleaseHandle) -> None:
        if handle.maintenance.is_alive():
            handle.maintenance.join(timeout=300)
            if handle.maintenance.is_alive():
                raise RuntimeError(
                    f"maintenance analyze did not finish during cleanup: event_id={handle.event_id!r}"
                )

    def assert_clean(self, handle: _ReleaseHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


class WarehouseCapabilityRegistry:
    """Registration entry wired by integration; the driver supplies the runtime."""

    def __init__(self, runtime_provider: Callable[[], WarehouseDeliveryRuntime]) -> None:
        self._capabilities = {
            CAPABILITY_BATCH_ARRIVAL: BatchArrivalCapability(runtime_provider),
            CAPABILITY_REPORT_BATCH: ReportBatchCapability(runtime_provider),
            CAPABILITY_BACKFILL_ARRIVAL: BackfillArrivalCapability(runtime_provider),
            CAPABILITY_QUEUE_CONCURRENCY_RELEASE: QueueConcurrencyReleaseCapability(runtime_provider),
        }

    def capability(self, capability_id: str):
        instance = self._capabilities.get(capability_id)
        if instance is None:
            raise KeyError(
                f"unknown warehouse delivery capability: capability_id={capability_id!r}, "
                f"known={sorted(self._capabilities)!r}"
            )
        return instance
