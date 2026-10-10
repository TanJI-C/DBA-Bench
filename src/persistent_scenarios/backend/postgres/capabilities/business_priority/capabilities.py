"""Instance 1 (business priority) event capability bindings, interface v1 shapes.

Each capability declares its owned resources, activates with
attempted/applied|prevented evidence, emits symptom-only alerts and cleans
only its own resources. Published configuration and agent repairs are run
facts: cleanup never reverts them.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Mapping

from ...workloads.business_priority.archive import (
    ArchiveRunReport,
    ArchiveWorker,
    read_archive_state,
)
from ...workloads.business_priority.config import HISTORY_CUTOFF_CREATED_AT
from ...workloads.business_priority.leak import LEAK_APPLICATION_NAME, run_tx_leak
from ...workloads.business_priority.maintenance import (
    MAINTENANCE_APPLICATION_NAME,
    MAINTENANCE_AUDIT_SQL,
    MAINTENANCE_LEDGER_TASK_ID,
    MaintenanceLedgerWorker,
)
from ...workloads.oltp_core.capability import (
    CapabilityContext,
    CapabilityRegistry,
    PromoTierCapability,
    CapabilityDeclaration,
    EventActivationResult,
    EventOccurrence,
    ResourceOwnership,
    require_driver,
)

LEAK_IMPACT_SQL = (
    "SELECT pid, state, extract(epoch FROM (now() - xact_start)) "
    "FROM pg_stat_activity WHERE application_name = %(app)s AND state = 'idle in transaction' "
    "AND pid <> pg_backend_pid();"
)
CONFIG_UPDATE_SQL = (
    "UPDATE ops.client_config SET config_version = %(config_version)s, "
    "request_timeout_ms = %(request_timeout_ms)s, max_retries = %(max_retries)s, "
    "retry_backoff_ms = %(retry_backoff_ms)s, retry_jitter_ms = %(retry_jitter_ms)s "
    "WHERE id = 1;"
)
ARCHIVE_ENABLE_SQL = "UPDATE ops.archive_state SET enabled = TRUE WHERE job_id = %(job_id)s;"
ARCHIVE_MOVED_ROWS_SQL = "SELECT rows_moved FROM ops.archive_state WHERE job_id = %(job_id)s;"

MAINTENANCE_REGISTRY_LOOKUP_SQL = (
    "SELECT 1 FROM ops.maintenance_registry WHERE task_id = %(task_id)s;"
)
MAINTENANCE_REGISTRY_INSERT_SQL = (
    "INSERT INTO ops.maintenance_registry (task_id, job_name, application_name, "
    "max_transaction_seconds, scope_note) VALUES "
    "(%(task_id)s, %(job_name)s, %(application_name)s, %(max_transaction_seconds)s, %(scope_note)s);"
)
MAINTENANCE_CLEAN_SQL = (
    "SELECT count(*) FROM pg_stat_activity WHERE application_name = %(app)s "
    "AND pid <> pg_backend_pid();"
)

ACTIVATION_BUDGET_SECONDS = 20.0
IMPACT_POLL_SECONDS = 0.5


def _wait_for(predicate, *, clock, stop, budget_seconds: float):
    deadline = clock.monotonic() + budget_seconds
    while True:
        value = predicate()
        if value is not None:
            return value
        if clock.monotonic() >= deadline:
            return None
        clock.wait_until(clock.monotonic() + IMPACT_POLL_SECONDS, stop)


@dataclass(slots=True)
class _LeakHandle:
    event_id: str
    sku: str
    application_name: str
    clock: object
    source: object
    thread: threading.Thread | None = None
    stop: threading.Event = field(default_factory=threading.Event)
    observation_slot: list = field(default_factory=list)

    def observation(self):
        return self.observation_slot[0] if self.observation_slot else None


class WorkerTxLeakCapability:
    """One application worker updates a promo hot-row and idles uncommitted.

    The activation result distinguishes the held case (an idle-in-transaction
    session observable in pg_stat_activity) from the prevented case (effective
    role protection terminated the session; the observation records the
    protecting GUC values).

    An occurrence may masquerade as a scheduled maintenance job: it then
    announces a maintenance-looking `application_name` and self-registers a
    plausible registry row plus one `started` audit entry before holding the
    hot-row lock. The registry/audit writes are run facts (never reverted) and
    the masquerade leaves zero trace in alert payloads — the diagnosis has to
    cross the audit trajectory, the transaction age and the session's last
    query against the registry claims.
    """

    capability_id = "worker_tx_leak"
    _PARAMS = frozenset({
        "sku", "hold_seconds",
        "application_name", "registry_task_id", "registry_job_name",
        "registry_scope_note", "registry_max_transaction_seconds",
    })
    _MASQUERADE_PARAMS = (
        "application_name", "registry_task_id", "registry_job_name",
        "registry_scope_note", "registry_max_transaction_seconds",
    )

    def declaration(self, occurrence: EventOccurrence) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            ownership=(ResourceOwnership(
                resource_key=f"session:tx-leak:{occurrence.entity}",
                resource_kind="database_session",
            ),),
            max_activation_seconds=ACTIVATION_BUDGET_SECONDS,
        )

    def _masquerade(self, occurrence: EventOccurrence) -> dict[str, object] | None:
        """Parses the masquerade params when the occurrence carries them; a
        partial masquerade payload is a spec defect, not a partial disguise."""

        present = set(occurrence.params) & set(self._MASQUERADE_PARAMS)
        if not present:
            return None
        missing = set(self._MASQUERADE_PARAMS) - present
        if missing:
            raise ValueError(
                f"Masquerade payload is incomplete: event_id={occurrence.event_id!r}, "
                f"missing={sorted(missing)!r}"
            )
        return {
            "application_name": occurrence.require_str("application_name"),
            "registry_task_id": occurrence.require_str("registry_task_id"),
            "registry_job_name": occurrence.require_str("registry_job_name"),
            "registry_scope_note": occurrence.require_str("registry_scope_note"),
            "registry_max_transaction_seconds": int(
                occurrence.require_number("registry_max_transaction_seconds")
            ),
        }

    def _publish_masquerade_artifacts(self, context: CapabilityContext, masquerade: dict[str, object]) -> None:
        """Self-registers the poisoned job: one registry row + one `started`
        audit entry, both timestamped server-side. The registry insert is the
        masquerade's own announcement; the audit trail stays at exactly one
        row while a legitimate job journals every committed batch."""

        connection = context.admin_source.connection("maintenance_registrar")
        try:
            with connection.cursor() as cursor:
                cursor.execute(MAINTENANCE_REGISTRY_INSERT_SQL, {
                    "task_id": masquerade["registry_task_id"],
                    "job_name": masquerade["registry_job_name"],
                    "application_name": masquerade["application_name"],
                    "max_transaction_seconds": masquerade["registry_max_transaction_seconds"],
                    "scope_note": masquerade["registry_scope_note"],
                })
                cursor.execute(MAINTENANCE_AUDIT_SQL, {
                    "task_id": masquerade["registry_task_id"],
                    "event": "started",
                    "detail": "maintenance job started",
                })
            connection.commit()
        finally:
            connection.close()

    def activate(self, context: CapabilityContext) -> EventActivationResult:
        context.occurrence.reject_unknown_params(self._PARAMS)
        sku = context.occurrence.require_str("sku")
        hold_seconds = context.occurrence.require_number("hold_seconds")
        masquerade = self._masquerade(context.occurrence)
        application_name = (
            str(masquerade["application_name"]) if masquerade is not None else LEAK_APPLICATION_NAME
        )
        if masquerade is not None:
            self._publish_masquerade_artifacts(context, masquerade)
        handle = _LeakHandle(
            event_id=context.occurrence.event_id,
            sku=sku,
            application_name=application_name,
            clock=context.clock,
            source=context.source,
        )

        def run() -> None:
            observation = run_tx_leak(
                source=context.source,
                clock=context.clock,
                sku=sku,
                hold_seconds=hold_seconds,
                stop=handle.stop,
                application_name=application_name,
            )
            handle.observation_slot.append(observation)

        handle.thread = threading.Thread(target=run, name=f"pg5-tx-leak-{handle.event_id}", daemon=True)
        handle.thread.start()
        context.evidence.append({
            "kind": "capability_activation",
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "sku": sku,
            "application_name": application_name,
            "masquerade": dict(masquerade) if masquerade is not None else None,
        })

        def evidence_now():
            observation = handle.observation()
            if observation is not None and observation.prevented:
                return {
                    "observation": {
                        "held_seconds": observation.held_seconds,
                        "detail": observation.detail,
                        "protection_gucs": dict(observation.protection_gucs),
                    },
                }
            connection = handle.source.connection(f"leak-impact-{handle.event_id}")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(LEAK_IMPACT_SQL, {"app": application_name})
                    rows = cursor.fetchall()
            finally:
                connection.close()
            if rows:
                return {
                    "observation": {
                        "idle_in_tx_sessions": [
                            {"pid": int(row[0]), "state": str(row[1]), "xact_age_seconds": float(row[2])}
                            for row in rows
                        ],
                    },
                }
            return None

        attempt = _wait_for(evidence_now, clock=handle.clock, stop=handle.stop, budget_seconds=ACTIVATION_BUDGET_SECONDS)
        if attempt is None:
            raise RuntimeError(
                f"Transaction leak impact absent and not prevented: event_id={handle.event_id!r}, "
                f"observation={handle.observation()!r}"
            )
        observation = handle.observation()
        attempt = {"event_id": handle.event_id, "sku": sku, **attempt}
        outcome = "prevented" if observation is not None and observation.prevented else "applied"
        if outcome == "prevented":
            attempt["mechanism"] = observation.mechanism
            attempt["protection_state"] = dict(observation.protection_gucs)
        return EventActivationResult(attempt=attempt, outcome=outcome, handle=handle)

    def alert(self, context: CapabilityContext, handle: object) -> Mapping[str, object]:
        handle = self._handle(handle)
        return {
            "title": "交易下单/支付成功率下降",
            "symptoms": [
                "下单与支付请求在库存热点上排队，端到端时延显著上升",
                "存在长时间未提交的事务持锁（事务年龄异常增长）",
            ],
            "severity": "critical",
            "category": "trade_degradation",
        }

    def cleanup(self, handle: object) -> None:
        handle = self._handle(handle)
        handle.stop.set()
        handle.thread.join(timeout=60)
        if handle.thread.is_alive():
            raise RuntimeError(
                f"Transaction leak session did not stop within its join timeout: event_id={handle.event_id!r}"
            )

    def assert_clean(self, handle: object) -> Mapping[str, object]:
        handle = self._handle(handle)
        connection = handle.source.connection(f"leak-clean-{handle.event_id}")
        try:
            with connection.cursor() as cursor:
                cursor.execute(LEAK_IMPACT_SQL, {"app": handle.application_name})
                rows = cursor.fetchall()
        finally:
            connection.close()
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "application_name": handle.application_name,
            "clean": not rows,
            "remaining_sessions": len(rows),
        }

    def _handle(self, handle: object) -> _LeakHandle:
        if not isinstance(handle, _LeakHandle):
            raise ValueError(f"Unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


@dataclass(slots=True)
class _ConfigReleaseHandle:
    event_id: str
    config_version: int


class ClientConfigReleaseCapability:
    """Publishes the client retry configuration through the control table.

    The database trigger appends the audit row; the driver poller adopts the
    values within its poll interval. Publication is a fact of the run.
    """

    capability_id = "client_config_release"
    _PARAMS = frozenset({
        "config_version", "request_timeout_ms", "max_retries", "retry_backoff_ms", "retry_jitter_ms",
    })

    def declaration(self, occurrence: EventOccurrence) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            ownership=(ResourceOwnership(
                resource_key="table:ops.client_config",
                resource_kind="control_table",
                mode="exclusive",
            ),),
            max_activation_seconds=30.0,
        )

    def activate(self, context: CapabilityContext) -> EventActivationResult:
        occurrence = context.occurrence
        occurrence.reject_unknown_params(self._PARAMS)
        payload = {
            "config_version": int(occurrence.require_number("config_version")),
            "request_timeout_ms": int(occurrence.require_number("request_timeout_ms")),
            "max_retries": int(occurrence.require_number("max_retries")),
            "retry_backoff_ms": int(occurrence.require_number("retry_backoff_ms")),
            "retry_jitter_ms": int(occurrence.require_number("retry_jitter_ms")),
        }
        driver = require_driver(context, self.capability_id)
        connection = context.admin_source.connection("config_publisher")
        try:
            with connection.cursor() as cursor:
                cursor.execute(CONFIG_UPDATE_SQL, payload)
            connection.commit()
        finally:
            connection.close()
        adoption_budget = driver.control_poll_seconds * 4 + 2.0

        def adopted():
            version = driver.applied_config_version()
            return version if version == payload["config_version"] else None

        adopted_version = _wait_for(
            adopted, clock=context.clock, stop=threading.Event(), budget_seconds=adoption_budget,
        )
        if adopted_version is None:
            raise RuntimeError(
                f"Client config publication was not adopted by the driver: "
                f"event_id={occurrence.event_id!r}, config_version={payload['config_version']!r}"
            )
        return EventActivationResult(
            attempt={"event_id": occurrence.event_id, "config_version": payload["config_version"]},
            outcome="applied",
            handle=_ConfigReleaseHandle(
                event_id=occurrence.event_id, config_version=payload["config_version"]
            ),
        )

    def alert(self, context: CapabilityContext, handle: object) -> Mapping[str, object]:
        return {
            "title": "客户端版本发布完成",
            "symptoms": ["新版客户端重试策略生效：短超时、高重试次数、无退避"],
            "severity": "info",
            "category": "client_release",
        }

    def cleanup(self, handle: object) -> None:
        return None

    def assert_clean(self, handle: object) -> Mapping[str, object]:
        return {"capability_id": self.capability_id, "clean": True}

    def _handle(self, handle: object) -> _ConfigReleaseHandle:
        if not isinstance(handle, _ConfigReleaseHandle):
            raise ValueError(f"Unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


@dataclass(slots=True)
class _ArchiveHandle:
    event_id: str
    job_id: str
    clock: object
    source: object
    worker: ArchiveWorker


class ArchiveJobCapability:
    """Arrival of the scheduled history archive run: enables and starts the worker."""

    capability_id = "archive_job"
    _PARAMS = frozenset({"job_id"})

    def declaration(self, occurrence: EventOccurrence) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            ownership=(ResourceOwnership(
                resource_key=f"job:archive:{occurrence.entity}",
                resource_kind="background_job",
                mode="shared",
            ),),
            max_activation_seconds=ACTIVATION_BUDGET_SECONDS,
        )

    def activate(self, context: CapabilityContext) -> EventActivationResult:
        context.occurrence.reject_unknown_params(self._PARAMS)
        job_id = context.occurrence.require_str("job_id")
        connection = context.admin_source.connection("archive_scheduler")
        try:
            with connection.cursor() as cursor:
                cursor.execute(ARCHIVE_ENABLE_SQL, {"job_id": job_id})
            connection.commit()
        finally:
            connection.close()
        worker = ArchiveWorker(source=context.source, clock=context.clock, evidence=context.evidence, job_id=job_id)
        worker.start_in_background()
        handle = _ArchiveHandle(
            event_id=context.occurrence.event_id,
            job_id=job_id,
            clock=context.clock,
            source=context.source,
            worker=worker,
        )
        context.evidence.append({
            "kind": "capability_activation",
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "job_id": job_id,
        })

        def moved_rows():
            connection = handle.source.connection(f"archive-impact-{handle.event_id}")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(ARCHIVE_MOVED_ROWS_SQL, {"job_id": handle.job_id})
                    row = cursor.fetchone()
                connection.commit()
                if row is not None and int(row[0]) > 0:
                    return int(row[0])
                return None
            finally:
                connection.close()

        rows = _wait_for(moved_rows, clock=handle.clock, stop=threading.Event(), budget_seconds=ACTIVATION_BUDGET_SECONDS)
        if rows is None:
            raise RuntimeError(
                f"Archive job moved no rows after activation: event_id={handle.event_id!r}, "
                f"job_id={handle.job_id!r}"
            )
        return EventActivationResult(
            attempt={"event_id": handle.event_id, "job_id": handle.job_id, "rows_moved": rows},
            outcome="applied",
            handle=handle,
        )

    def alert(self, context: CapabilityContext, handle: object) -> Mapping[str, object]:
        return {
            "title": "历史归档作业按排程启动",
            "symptoms": ["归档批处理开始读取历史订单，I/O 与行锁占用上升"],
            "severity": "info",
            "category": "scheduled_maintenance",
        }

    def cleanup(self, handle: object) -> None:
        handle = self._handle(handle)
        report: ArchiveRunReport = handle.worker.stop()
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "delivery_note": report.delivery_note,
            "rows_moved": report.rows_moved,
        }

    def assert_clean(self, handle: object) -> Mapping[str, object]:
        handle = self._handle(handle)
        state = read_archive_state(handle.source.connection(f"archive-clean-{handle.event_id}"), handle.job_id)
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "clean": True,
            "rows_moved": state.rows_moved,
        }

    def _handle(self, handle: object) -> _ArchiveHandle:
        if not isinstance(handle, _ArchiveHandle):
            raise ValueError(f"Unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


@dataclass(slots=True)
class _MaintenanceHandle:
    event_id: str
    task_id: str
    source: object
    worker: MaintenanceLedgerWorker


class ScheduledMaintenanceCapability:
    """Arrival of the scheduled ledger-rebuild maintenance window: journals the
    window start and runs the legitimate read-only statistics worker.

    This is the honest maintenance job the poisoned tx_leak_2 masquerade hides
    behind: its registry claim is seeded, its audit trajectory is dense (one
    `started` row plus one `batch_committed` row per committed batch), and its
    session transaction age stays bounded.
    """

    capability_id = "scheduled_maintenance"
    _PARAMS = frozenset({"task_id"})

    def declaration(self, occurrence: EventOccurrence) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            ownership=(ResourceOwnership(
                resource_key=f"session:maintenance:{occurrence.entity}",
                resource_kind="database_session",
                mode="shared",
            ),),
            max_activation_seconds=ACTIVATION_BUDGET_SECONDS,
        )

    def activate(self, context: CapabilityContext) -> EventActivationResult:
        context.occurrence.reject_unknown_params(self._PARAMS)
        task_id = context.occurrence.require_str("task_id")
        connection = context.admin_source.connection("maintenance_scheduler")
        try:
            with connection.cursor() as cursor:
                cursor.execute(MAINTENANCE_REGISTRY_LOOKUP_SQL, {"task_id": task_id})
                if cursor.fetchone() is None:
                    raise RuntimeError(
                        f"Scheduled maintenance task is not in the registry; the dataset image "
                        f"is stale: task_id={task_id!r}"
                    )
                cursor.execute(MAINTENANCE_AUDIT_SQL, {
                    "task_id": task_id, "event": "started", "detail": "maintenance window opened",
                })
            connection.commit()
        finally:
            connection.close()
        worker = MaintenanceLedgerWorker(
            source=context.source,
            clock=context.clock,
            evidence=context.evidence,
            task_id=task_id,
            cutoff_created_at=HISTORY_CUTOFF_CREATED_AT,
        )
        worker.start_in_background()
        if not worker.wait_for_first_batch(ACTIVATION_BUDGET_SECONDS):
            raise RuntimeError(
                f"Scheduled maintenance worker committed no batch after activation: "
                f"event_id={context.occurrence.event_id!r}, task_id={task_id!r}"
            )
        context.evidence.append({
            "kind": "capability_activation",
            "capability_id": self.capability_id,
            "event_id": context.occurrence.event_id,
            "task_id": task_id,
        })
        return EventActivationResult(
            attempt={"event_id": context.occurrence.event_id, "task_id": task_id},
            outcome="applied",
            handle=_MaintenanceHandle(
                event_id=context.occurrence.event_id,
                task_id=task_id,
                source=context.source,
                worker=worker,
            ),
        )

    def alert(self, context: CapabilityContext, handle: object) -> Mapping[str, object]:
        return {
            "title": "促销日维护窗口开启",
            "symptoms": ["历史订单台账重建维护作业按排程启动（只读统计，短事务分批）"],
            "severity": "info",
            "category": "scheduled_maintenance",
        }

    def cleanup(self, handle: object) -> None:
        handle = self._handle(handle)
        report = handle.worker.stop()
        return {"batches": report.batches}

    def assert_clean(self, handle: object) -> Mapping[str, object]:
        handle = self._handle(handle)
        connection = handle.source.connection(f"maintenance-clean-{handle.event_id}")
        try:
            with connection.cursor() as cursor:
                cursor.execute(MAINTENANCE_CLEAN_SQL, {"app": MAINTENANCE_APPLICATION_NAME})
                row = cursor.fetchone()
        finally:
            connection.close()
        remaining = int(row[0]) if row is not None else 0
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "clean": remaining == 0,
            "remaining_sessions": remaining,
        }

    def _handle(self, handle: object) -> _MaintenanceHandle:
        if not isinstance(handle, _MaintenanceHandle):
            raise ValueError(f"Unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


CAPABILITY_REGISTRY = CapabilityRegistry((
    PromoTierCapability(),
    WorkerTxLeakCapability(),
    ClientConfigReleaseCapability(),
    ArchiveJobCapability(),
    ScheduledMaintenanceCapability(),
))
