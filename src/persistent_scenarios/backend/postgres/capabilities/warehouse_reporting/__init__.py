"""Instance-native Event capabilities for pg_warehouse_batch_reporting.

Each capability expresses external intent as real effects on the public control plane
(queue rows, audited configuration releases) and returns structured arrival facts.
Prevention is never synthesized: a capability that cannot complete its effect raises,
and only a genuinely blocked attempt returns prevented evidence.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

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
    PreventionEvidence,
)

from ...workloads.warehouse_reporting.reports import REQUIRED_REPORTS, deliverable_job_id
from ...workloads.warehouse_reporting.runtime import WarehouseReportingRuntime
from ...workloads.warehouse_reporting.schema import BATCH_A_ID, BATCH_B_ID
from ...workloads.warehouse_reporting.store import (
    MAINTENANCE_INVALIDATION_NOTE,
    MAX_ATTEMPTS,
    PREMATURE_COMPLETION_MARKER_NOTE,
)

CAPABILITY_BATCH_ARRIVAL = "pg5r_olap_batch_arrival"
CAPABILITY_REPORT_BATCH = "pg5r_olap_report_batch"
CAPABILITY_QUEUE_CONCURRENCY_RELEASE = "pg5r_olap_queue_concurrency_release"
CAPABILITY_BACKUP_READ_ARRIVAL = "pg5r_olap_backup_read_arrival"
CAPABILITY_INGEST_WATERMARK_PREMATURE = "pg5r_olap_ingest_watermark_premature"
CAPABILITY_REPORT_ROLE_PLANNER_RELEASE = "pg5r_olap_report_role_planner_release"
CAPABILITY_MAINTENANCE_ATTEMPT_INVALIDATION = "pg5r_olap_maintenance_attempt_invalidation"

CAPABILITY_IDS = frozenset(
    {
        CAPABILITY_BATCH_ARRIVAL,
        CAPABILITY_REPORT_BATCH,
        CAPABILITY_QUEUE_CONCURRENCY_RELEASE,
        CAPABILITY_BACKUP_READ_ARRIVAL,
        CAPABILITY_INGEST_WATERMARK_PREMATURE,
        CAPABILITY_REPORT_ROLE_PLANNER_RELEASE,
        CAPABILITY_MAINTENANCE_ATTEMPT_INVALIDATION,
    }
)

# Deadline offsets from the activating event, seconds — frozen from the 4C/8G healthy
# ×3 baseline (pooled worst sample, ≤40% rule;
# max(old, floor): the rule validates thresholds from below, it does not tighten
# business constants that already satisfy it). The authoritative acceptance deadlines
# are the spec DeliverableContract values, which carry the same numbers.
REPORT_DEADLINE_OFFSETS = {
    "store_daily_revenue": 1672,
    "item_margin_top50": 720,
    "item_date_matrix": 1933,
    "hot_item_range": 1481,
    "batch_customer_concentration": 1155,
}
INGEST_DEADLINE_OFFSET = 600
BACKUP_DEADLINE_OFFSET = 1500
CONCURRENCY_RELEASE_MAX_WORKERS = 6
MAX_ACTIVATION_SECONDS = 120

# Zero-path data/digest sabotage: the
# batch B definition release shipped four defective report templates, so the
# deliveries complete with results that are wrong for their declared batch binding.
# The defect lives in the deployed definition (the queue row SQL), not in the fact
# data, which keeps it fully repairable through the authorized queue-control surface
# while the delivered digest mismatch itself is deterministic — every drift changes
# the result for any data state, independent of I/O topology or host load:
#   store_daily_revenue  silent channel scope drift: the release template moves the
#                        `channel = 'store'` scope into FILTER clauses on the money
#                        measures, so every group silently loses the history
#                        catalog/web contributions while the WHERE clause (and with
#                        it the grouped row set and the declared cutoff binding)
#                        stays untouched (isomorphic value drift; a plain WHERE
#                        filter is NOT isomorphic — the fixture gate measured 32886
#                        canonical groups vs 12768 store-only groups)
#   item_margin_top50    metric definition drift: the absolute margin
#                        `sum(net_profit)` is published as the profit rate
#                        `sum(net_profit) / NULLIF(sum(net_paid), 0)`; the top-50
#                        limit and the row count are untouched, every margin value
#                        and the ranking change (isomorphic value drift)
#   item_date_matrix     metric drift: the quantity column aggregates row counts
#                        (same grouped row set, every value wrong)
#   hot_item_range       hot range inflated 10x: the delivery is flooded with
#                        cold items outside the declared hot band
# batch_customer_concentration and the whole batch A cycle deploy canonical
# definitions: the exact-batch scan is the one delivery too fast to leave an honest
# repair window, so it never carries the release defect.
DEFECTIVE_DEFINITION_RELEASE_BATCH = BATCH_B_ID
DEFECTIVE_REPORT_SQL: dict[str, Callable[[int], str]] = {
    "store_daily_revenue": lambda cutoff: (
        "SELECT sold_date_sk, store_sk, "
        "sum(quantity) FILTER (WHERE channel = 'store') AS total_quantity, "
        "round(sum(net_paid) FILTER (WHERE channel = 'store'), 2) AS total_revenue "
        f"FROM wh.batch_sales WHERE batch_id <= {cutoff} "
        "GROUP BY sold_date_sk, store_sk ORDER BY sold_date_sk, store_sk"
    ),
    "item_margin_top50": lambda cutoff: (
        "SELECT item_sk, round(sum(net_profit) / NULLIF(sum(net_paid), 0), 2) AS margin "
        f"FROM wh.batch_sales WHERE batch_id <= {cutoff} "
        "GROUP BY item_sk ORDER BY margin DESC, item_sk LIMIT 50"
    ),
    "item_date_matrix": lambda cutoff: (
        "SELECT item_sk, sold_date_sk, count(*) AS total_quantity "
        f"FROM wh.batch_sales WHERE batch_id <= {cutoff} "
        "GROUP BY item_sk, sold_date_sk"
    ),
    "hot_item_range": lambda cutoff: (
        "SELECT item_sk, sum(quantity) AS total_quantity, round(sum(net_paid), 2) AS net_revenue "
        f"FROM wh.batch_sales WHERE batch_id <= {cutoff} "
        "AND item_sk BETWEEN 101 AND 2500 GROUP BY item_sk ORDER BY item_sk"
    ),
}

# Defects whose result keeps the canonical row multiset shape: only the grouped
# values drift, so a row-count sanity check cannot catch them. The
# pre-flight gate asserts on the frozen fixture that the drifted digest diverges
# from canonical while the row count stays equal.
ISOMORPHIC_VALUE_DRIFT_REPORTS = frozenset(
    {"store_daily_revenue", "item_margin_top50", "item_date_matrix"}
)


def _batch_id_from_payload(payload) -> int:
    batch = payload.get("batch")
    if batch not in {"a", "b"}:
        raise ValueError(f"warehouse occurrence payload must select batch a or b: payload={dict(payload)!r}")
    return BATCH_A_ID if batch == "a" else BATCH_B_ID


@dataclass(frozen=True, slots=True)
class _BatchHandle:
    event_id: str
    batch_id: int
    ingest_job_id: str
    ingest_control: dict


class BatchArrivalCapability:
    """Batch data arrival: ingest job submission plus the maintenance-window releases (batch A)."""

    capability_id = CAPABILITY_BATCH_ARRIVAL

    def __init__(self, runtime_provider: Callable[[], WarehouseReportingRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        resources = [
            ResourceOwnership(
                resource_key=f"queue:ingest:{event.entity}", resource_kind="queue_row", mode=OwnershipMode.EXCLUSIVE
            )
        ]
        if _batch_id_from_payload(event.payload) == BATCH_A_ID:
            resources.append(
                ResourceOwnership("config:ingest_control:1", "control_table_row", OwnershipMode.EXCLUSIVE)
            )
            resources.append(
                ResourceOwnership("guc:database:default_statistics_target", "database_guc", OwnershipMode.EXCLUSIVE)
            )
        return CapabilityDeclaration(
            capability_id=self.capability_id, resources=tuple(resources), max_activation_seconds=MAX_ACTIVATION_SECONDS
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        batch_id = _batch_id_from_payload(context.event.payload)
        if batch_id == BATCH_A_ID:
            ingest_control = runtime.apply_ingest_control_release(batch_id, False, at)
            runtime.apply_database_release(
                "ALTER DATABASE testdb SET default_statistics_target = 25;",
                "default_statistics_target",
                at,
            )
        else:
            ingest_control = {"batch_id": batch_id, "analyze_after_ingest": True}
        ingest_job_id = runtime.submit_ingest(batch_id, at + INGEST_DEADLINE_OFFSET)
        handle = _BatchHandle(
            event_id=context.event.event_id, batch_id=batch_id, ingest_job_id=ingest_job_id,
            ingest_control=ingest_control,
        )
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=at,
                detail={"batch_id": batch_id, "ingest_job_id": ingest_job_id},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={"ingest_job_submitted": True, "ingest_control": ingest_control},
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _BatchHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="Warehouse ingest batch finished and report delivery is pending",
            symptoms=(
                "ingest batch completed without a following statistics maintenance step visible",
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
    """Submits the per-batch required report delivery list bound to a batch cutoff.

    The batch B cycle publishes the defective definition release: four required
    reports enter the queue with drifted SQL while their queue rows still declare
    the contract binding (job_id suffix, batch_cutoff, binding snapshot). The
    release is audited into wh.config_audit like every other external change.
    """

    capability_id = CAPABILITY_REPORT_BATCH

    def __init__(self, runtime_provider: Callable[[], WarehouseReportingRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        resources = [
            ResourceOwnership(
                resource_key=f"queue:report_batch:{event.entity}", resource_kind="queue_row",
                mode=OwnershipMode.EXCLUSIVE,
            ),
        ]
        if _batch_id_from_payload(event.payload) == DEFECTIVE_DEFINITION_RELEASE_BATCH:
            resources.append(
                ResourceOwnership(
                    resource_key="config:report_definition_release", resource_kind="control_table_row",
                    mode=OwnershipMode.EXCLUSIVE,
                )
            )
        return CapabilityDeclaration(
            capability_id=self.capability_id, resources=tuple(resources), max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        batch_id = _batch_id_from_payload(context.event.payload)
        job_ids: list[str] = []
        deployed_definitions: dict[str, str] = {}
        for report in REQUIRED_REPORTS:
            definition_sql = None
            if batch_id == DEFECTIVE_DEFINITION_RELEASE_BATCH:
                drifted = DEFECTIVE_REPORT_SQL.get(report.report_id)
                if drifted is not None:
                    definition_sql = drifted(batch_id)
                    deployed_definitions[report.report_id] = definition_sql
            job_ids.append(
                runtime.submit_required_report(
                    report.report_id,
                    batch_id,
                    at + REPORT_DEADLINE_OFFSETS[report.report_id],
                    definition_sql=definition_sql,
                )
            )
        if deployed_definitions:
            runtime.audit_report_definition_release(batch_id, deployed_definitions, at)
        handle = _ReportBatchHandle(event_id=context.event.event_id, batch_id=batch_id, job_ids=tuple(job_ids))
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=at,
                detail={"batch_id": batch_id, "job_count": len(job_ids),
                        "defective_definitions": sorted(deployed_definitions)},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(), facts={"submitted_job_ids": list(job_ids)}
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _ReportBatchHandle) -> EventAlertPayload:
        symptoms = [
            "five required reports queued with business deadlines",
            "delivery latency is measured from submission including queueing",
        ]
        if handle.batch_id == DEFECTIVE_DEFINITION_RELEASE_BATCH:
            symptoms.append(
                "this cycle's report definitions were published by the release pipeline "
                "without a post-publish validation gate"
            )
        return EventAlertPayload(
            title="A required report delivery batch is due for downstream consumers",
            symptoms=tuple(symptoms),
            severity="notice",
            category="warehouse_delivery",
        )

    def cleanup(self, handle: _ReportBatchHandle) -> None:
        return None

    def assert_clean(self, handle: _ReportBatchHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


@dataclass(frozen=True, slots=True)
class _ReleaseHandle:
    event_id: str
    queue_config: dict


class QueueConcurrencyReleaseCapability:
    """External scheduler decision that widens the analytics worker pool."""

    capability_id = CAPABILITY_QUEUE_CONCURRENCY_RELEASE

    def __init__(self, runtime_provider: Callable[[], WarehouseReportingRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership("config:queue_config", "control_table_row", OwnershipMode.EXCLUSIVE),
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
        handle = _ReleaseHandle(event_id=context.event.event_id, queue_config=new_state)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(attempted_at_monotonic=at, detail={"max_workers": max_workers}),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(), facts={"queue_config": new_state}
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _ReleaseHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="Reporting scheduler widened the analytics worker pool",
            symptoms=(
                "analytics worker pool widened by an external scheduler release",
                "concurrent heavy reports may compete for memory",
            ),
            severity="notice",
            category="warehouse_scheduler",
        )

    def cleanup(self, handle: _ReleaseHandle) -> None:
        return None

    def assert_clean(self, handle: _ReleaseHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


@dataclass(frozen=True, slots=True)
class _BackupHandle:
    event_id: str
    job_id: str


class BackupReadArrivalCapability:
    """Routine backup verification read with its own business deadline."""

    capability_id = CAPABILITY_BACKUP_READ_ARRIVAL

    def __init__(self, runtime_provider: Callable[[], WarehouseReportingRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership("queue:backup_read", "queue_row", OwnershipMode.EXCLUSIVE),
            ),
            max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        job_id = runtime.submit_backup(at + BACKUP_DEADLINE_OFFSET)
        handle = _BackupHandle(event_id=context.event.event_id, job_id=job_id)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(attempted_at_monotonic=at, detail={"backup_job_id": job_id}),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(), facts={"backup_job_submitted": True}
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _BackupHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="Routine backup verification read is running against the warehouse",
            symptoms=(
                "full-fact verification read in progress with a completion deadline",
                "backup reads compete with report jobs for I/O",
            ),
            severity="notice",
            category="warehouse_backup",
        )

    def cleanup(self, handle: _BackupHandle) -> None:
        return None

    def assert_clean(self, handle: _BackupHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


@dataclass(frozen=True, slots=True)
class _PrematureMarkerHandle:
    event_id: str
    batch_id: int
    marker_at: float | None  # None: the publish attempt was blocked, nothing was written


# Report planner release: the reporting platform's release pipeline
# publishes a planner "tuning" to the database scope. All four warehouse services
# (and the agent) share the single superuser role on this deployment, so the minimal
# honest incident surface is the database-level setting that every NEW worker session
# inherits — no dedicated report role exists to target.
# `enable_hashjoin = off` bends every join the analytics workers execute (the
# bi_heartbeat TPC-DS queries) toward nested loop plans at the frozen 4MB work_mem:
# the heartbeat 30s budget erodes below its 90% on-time floor and poisoned heartbeat
# attempts hold the report worker pool. Single-table report aggregates carry no join,
# so the required deliveries are only hit through worker-pool contention — the effect
# is plan-shape-bound, not I/O-topology-bound.
PLANNER_RELEASE_GUC = "enable_hashjoin"
PLANNER_RELEASE_SCOPE_DATABASE = "testdb"
PLANNER_RELEASE_SETTING = "off"
PLANNER_RELEASE_SQL = f"ALTER DATABASE {PLANNER_RELEASE_SCOPE_DATABASE} SET {PLANNER_RELEASE_GUC} = {PLANNER_RELEASE_SETTING};"


@dataclass(frozen=True, slots=True)
class _PlannerReleaseHandle:
    event_id: str
    release_at: float


class ReportRolePlannerReleaseCapability:
    """Report platform release publishes `ALTER DATABASE testdb SET enable_hashjoin = off`.

    Silent external config release, audited into wh.config_audit; verified on a
    fresh session at activation (a release that did not take effect raises, never
    pretends). The agent's own session predates the release and keeps its startup
    value — discovery runs through the pg_db_role_setting catalog or the heartbeat
    degradation, and the authorized repair is ALTER DATABASE/ROLE ... SET|RESET
    (classes alter_guc/alter_object/role_admin, GUC enable_hashjoin) plus
    cancel-and-rerun of polluted attempts.
    """

    capability_id = CAPABILITY_REPORT_ROLE_PLANNER_RELEASE

    def __init__(self, runtime_provider: Callable[[], WarehouseReportingRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership(
                    f"guc:database:{PLANNER_RELEASE_SCOPE_DATABASE}:{PLANNER_RELEASE_GUC}",
                    "database_guc",
                    OwnershipMode.EXCLUSIVE,
                ),
            ),
            max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        runtime.apply_database_release(PLANNER_RELEASE_SQL, "pg_db_role_setting", at)
        effective = runtime.effective_database_guc(PLANNER_RELEASE_GUC)
        if effective != PLANNER_RELEASE_SETTING:
            raise RuntimeError(
                "report planner release did not take effect on fresh sessions: "
                f"sql={PLANNER_RELEASE_SQL!r}, expected={PLANNER_RELEASE_SETTING!r}, effective={effective!r}"
            )
        handle = _PlannerReleaseHandle(event_id=context.event.event_id, release_at=at)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(attempted_at_monotonic=at, detail={"sql": PLANNER_RELEASE_SQL}),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={
                    "guc": PLANNER_RELEASE_GUC,
                    "scope": f"database:{PLANNER_RELEASE_SCOPE_DATABASE}",
                    "setting": PLANNER_RELEASE_SETTING,
                    "effective_on_fresh_session": effective,
                    "audit_table": "pg_db_role_setting",
                },
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _PlannerReleaseHandle) -> EventAlertPayload:
        # trigger=silent: the release is only visible through wh.config_audit, the
        # pg_db_role_setting catalog and the heartbeat/report latency symptoms.
        return EventAlertPayload(
            title="Reporting platform published a planner configuration release",
            symptoms=(
                "the reporting platform's release pipeline published a planner configuration change",
                "analyst heartbeats are missing their response budget",
            ),
            severity="warning",
            category="warehouse_scheduler",
        )

    def cleanup(self, handle: _PlannerReleaseHandle) -> None:
        # The published planner setting is legitimate business configuration: it
        # persists (unrepaired) or was reset by the agent's repair, and the
        # environment is discarded whole after final evaluation.
        return None

    def assert_clean(self, handle: _PlannerReleaseHandle) -> dict[str, object]:
        """Report the observed post-run setting; the release introduces no
        undeclared side state, so the fact (not a value) is the verification."""
        effective = self._runtime_provider().effective_database_guc(PLANNER_RELEASE_GUC)
        return {"capability_id": self.capability_id, "event_id": handle.event_id,
                "status": "clean", "effective_on_fresh_session": effective}


class IngestWatermarkPrematureCapability:
    """Upstream ETL race: the publisher marks batch B complete before the ingest lands.

    While the batch B ingest is genuinely still open (queue row queued/running and
    the registry carries no completion), the upstream release tool writes the
    completion timestamps into ``wh.batch_registry`` ahead of the real ingest and
    audits the premature marker into ``wh.config_audit``. The lie is transient by
    construction: the real ``record_batch_registry`` at ingest completion overwrites
    the row with the true timestamps. An agent that trusts the premature watermark
    to schedule or bless batch B deliveries delivers against incomplete facts; the
    honest reconciliation is ``count(*) WHERE batch_id = 2`` against the watermark,
    then a delayed delivery or a cancel-and-rerun of any polluted attempt — all on
    the authorized action surface.
    """

    capability_id = CAPABILITY_INGEST_WATERMARK_PREMATURE

    def __init__(self, runtime_provider: Callable[[], WarehouseReportingRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership("config:batch_registry_marker", "control_table_row", OwnershipMode.EXCLUSIVE),
            ),
            max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        batch_id = BATCH_B_ID
        state = runtime.batch_ingest_completion_state(batch_id)
        attempt = EventAttemptEvidence(
            attempted_at_monotonic=at,
            detail={"batch_id": batch_id, **{key: state[key] for key in
                    ("job_id", "queue_status", "ingest_finished_at", "in_flight")}},
        )
        if not state["in_flight"]:
            # The true completion is already public: publishing a marker now would
            # be a lie nothing overwrites, so the upstream tool's attempt is
            # blocked by the observed registry state.
            handle = _PrematureMarkerHandle(event_id=context.event.event_id, batch_id=batch_id, marker_at=None)
            return EventActivationResult(
                handle=handle,
                attempt=attempt,
                applied=None,
                prevented=PreventionEvidence(
                    attempted=attempt,
                    mechanism="batch_ingest_no_longer_in_flight",
                    protection_state={
                        "queue_status": state["queue_status"],
                        "ingest_finished_at": state["ingest_finished_at"],
                        "note": "a premature marker would not be overwritten by the real ingest",
                    },
                    observed_at_monotonic=context.clock.monotonic(),
                ),
            )
        published = runtime.publish_premature_batch_marker(batch_id, at)
        if published is None:
            # Race lost: the real completion landed between the observation above
            # and the guarded publish UPDATE, so the lie cannot be written — the
            # attempt is blocked by the registry state it just observed changing.
            race_state = runtime.batch_ingest_completion_state(batch_id)
            handle = _PrematureMarkerHandle(event_id=context.event.event_id, batch_id=batch_id, marker_at=None)
            return EventActivationResult(
                handle=handle,
                attempt=attempt,
                applied=None,
                prevented=PreventionEvidence(
                    attempted=attempt,
                    mechanism="batch_ingest_completed_before_marker_publish",
                    protection_state={
                        "queue_status": race_state["queue_status"],
                        "ingest_started_at": race_state["ingest_started_at"],
                        "ingest_finished_at": race_state["ingest_finished_at"],
                        "note": "the guarded publish refused to overwrite the true completion",
                    },
                    observed_at_monotonic=context.clock.monotonic(),
                ),
            )
        # Keep the transient lie observable across inspection cycles: the repeat
        # monitor re-asserts it every cadence step until the real ingest lands.
        runtime.start_premature_marker_repeat(batch_id, published["marker_at"])
        handle = _PrematureMarkerHandle(
            event_id=context.event.event_id, batch_id=batch_id, marker_at=published["marker_at"]
        )
        return EventActivationResult(
            handle=handle,
            attempt=attempt,
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={
                    "premature_marker_published": True,
                    "marker_at": published["marker_at"],
                    "audit_id": published["audit_id"],
                    "audit_note": PREMATURE_COMPLETION_MARKER_NOTE,
                    "queue_status": state["queue_status"],
                },
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _PrematureMarkerHandle) -> EventAlertPayload:
        # trigger=silent: never published to the mailbox; the only surface is the
        # registry row itself plus the config_audit trail.
        return EventAlertPayload(
            title="Upstream publisher reported a warehouse batch completion",
            symptoms=(
                "the upstream publishing pipeline reported a batch completion through its registry",
            ),
            severity="notice",
            category="warehouse_batch",
        )

    def cleanup(self, handle: _PrematureMarkerHandle) -> None:
        # The marker is business state owned by the upstream registry; its
        # transient correction is the mechanism itself, not a cleanup duty.
        return None

    def assert_clean(self, handle: _PrematureMarkerHandle) -> dict[str, object]:
        """Verify the premature lie did not survive: the registry must carry either
        no completion (ingest still open) or the real, later completion."""
        if handle.marker_at is None:
            return {"capability_id": self.capability_id, "event_id": handle.event_id,
                    "status": "clean", "marker_published": False}
        state = self._runtime_provider().read_batch_registry_state(handle.batch_id)
        finished = state["ingest_finished_at"]
        if finished is not None and float(finished) > handle.marker_at:
            return {"capability_id": self.capability_id, "event_id": handle.event_id,
                    "status": "clean", "marker_published": True,
                    "ingest_finished_at": finished, "marker_at": handle.marker_at}
        raise RuntimeError(
            "premature batch completion marker survived as registry state (the real ingest "
            f"never overwrote it): batch_id={handle.batch_id}, marker_at={handle.marker_at}, "
            f"ingest_finished_at={finished}, queue_obligation_open={finished is None}"
        )


# The new fatal event: the upstream ETL platform's post-ingest
# maintenance pipeline opens a "statistics rebuild window" and enforces its
# consistency policy on the report queue — in-flight attempts of the affected
# item-path report are invalidated so they re-execute under the rebuilt
# statistics. The invalidation budget is the queue's own retry budget: each
# cancel-and-requeue burns one attempt, the third cancellation lands on
# attempts == MAX_ATTEMPTS and the report body marks the row permanently
# failed — the delivery is missing (T1 breach) with zero agent action. The
# mechanism is deterministic and I/O-topology-independent: no statistics lie,
# no planner regression and no workload slowdown is involved (the primary
# planner-statistics-poisoning direction was rejected: every cutoff-bound
# required report is a single-table aggregation whose only competitive plan is
# seq+hashagg, and PostgreSQL planner statistics can never change result
# content). The agent's authorized
# repair is queue control: requeue the failed row with the retry budget reset
# (update_data), or clear the invalidation flag mid-burn.
MAINTENANCE_INVALIDATION_REPORT_ID = "hot_item_range"
MAINTENANCE_INVALIDATION_BATCH = BATCH_B_ID


@dataclass(frozen=True, slots=True)
class _MaintenanceInvalidationHandle:
    event_id: str
    job_id: str


class MaintenanceAttemptInvalidationCapability:
    """Upstream maintenance pipeline invalidates in-flight attempts of the
    item-path report during its statistics rebuild window.

    The policy release is audited into wh.config_audit, then a runtime monitor
    enforces it against the public queue: every attempt found running gets
    cancel_requested until the retry budget (MAX_ATTEMPTS) is spent and the row
    terminates failed. Each invalidation carries its own audit row, so the burn
    is reconstructable from the audit timeline. The stated policy (plan refresh
    under rebuilt statistics) is a decoy, not a root-cause leak: the catalog
    shows the claimed rebuild never ran (last_analyze stays at the ingest-time
    ANALYZE), and the fatal defect is the burned budget, not the plan.
    """

    capability_id = CAPABILITY_MAINTENANCE_ATTEMPT_INVALIDATION

    def __init__(self, runtime_provider: Callable[[], WarehouseReportingRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        job_id = deliverable_job_id(MAINTENANCE_INVALIDATION_REPORT_ID, MAINTENANCE_INVALIDATION_BATCH)
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership(f"queue:report:{job_id}", "queue_row", OwnershipMode.EXCLUSIVE),
                ResourceOwnership("config:wh.report_queue:maintenance_invalidation",
                                  "control_table_row", OwnershipMode.EXCLUSIVE),
            ),
            max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        job_id = deliverable_job_id(MAINTENANCE_INVALIDATION_REPORT_ID, MAINTENANCE_INVALIDATION_BATCH)
        audit = runtime.audit_maintenance_invalidation_release(job_id, at)
        runtime.start_maintenance_invalidation_monitor(job_id, max_invalidations=MAX_ATTEMPTS)
        handle = _MaintenanceInvalidationHandle(event_id=context.event.event_id, job_id=job_id)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=at,
                detail={"job_id": job_id, "max_invalidations": MAX_ATTEMPTS},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={"audit_id": audit["audit_id"], "target_job_id": job_id,
                       "note": MAINTENANCE_INVALIDATION_NOTE},
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _MaintenanceInvalidationHandle) -> EventAlertPayload:
        # trigger=silent: the surface is the audited policy release, the queue
        # row's attempts/cancel_requested state and the missing delivery.
        return EventAlertPayload(
            title="The upstream maintenance pipeline opened a statistics rebuild window",
            symptoms=(
                "the upstream maintenance pipeline announced a statistics rebuild window "
                "for the warehouse",
                "in-flight report attempts may be invalidated for plan refresh while the "
                "window is open",
            ),
            severity="warning",
            category="warehouse_scheduler",
        )

    def cleanup(self, handle: _MaintenanceInvalidationHandle) -> None:
        # The burned retry budget is business state in the public queue; the
        # failed row (or the agent's repair) is the evaluated outcome.
        return None

    def assert_clean(self, handle: _MaintenanceInvalidationHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


class WarehouseCapabilityRegistry:
    """Registration entry wired by integration; the driver supplies the runtime."""

    def __init__(self, runtime_provider: Callable[[], WarehouseReportingRuntime]) -> None:
        self._capabilities = {
            CAPABILITY_BATCH_ARRIVAL: BatchArrivalCapability(runtime_provider),
            CAPABILITY_REPORT_BATCH: ReportBatchCapability(runtime_provider),
            CAPABILITY_QUEUE_CONCURRENCY_RELEASE: QueueConcurrencyReleaseCapability(runtime_provider),
            CAPABILITY_BACKUP_READ_ARRIVAL: BackupReadArrivalCapability(runtime_provider),
            CAPABILITY_INGEST_WATERMARK_PREMATURE: IngestWatermarkPrematureCapability(runtime_provider),
            CAPABILITY_REPORT_ROLE_PLANNER_RELEASE: ReportRolePlannerReleaseCapability(runtime_provider),
            CAPABILITY_MAINTENANCE_ATTEMPT_INVALIDATION: MaintenanceAttemptInvalidationCapability(runtime_provider),
        }

    def capability(self, capability_id: str):
        instance = self._capabilities.get(capability_id)
        if instance is None:
            raise KeyError(
                f"unknown warehouse reporting capability: capability_id={capability_id!r}, "
                f"known={sorted(self._capabilities)!r}"
            )
        return instance
