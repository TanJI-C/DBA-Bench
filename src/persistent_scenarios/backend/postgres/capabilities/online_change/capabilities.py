"""Instance 5 (online change) event capability bindings, interface v1 shapes."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Mapping

from ...workloads.online_change.backfill import BackfillWorker
from ...workloads.online_change.longtx import LONG_TX_APPLICATION_NAME, run_legacy_long_tx
from ...workloads.online_change.release import RELEASE_APPLICATION_NAME, ReleaseWorker
from ...workloads.oltp_core.capability import (
    CapabilityContext,
    CapabilityRegistry,
    CapabilityDeclaration,
    EventActivationResult,
    EventOccurrence,
    ResourceOwnership,
    require_driver,
)
from ...workloads.oltp_core.control import read_release_task

LONG_TX_IMPACT_SQL = (
    "SELECT pid, state, extract(epoch FROM (now() - xact_start)) "
    "FROM pg_stat_activity WHERE application_name = %(app)s AND state = 'idle in transaction' "
    "AND pid <> pg_backend_pid();"
)
DDL_WAIT_SQL = (
    "SELECT pid, wait_event_type, wait_event, state "
    "FROM pg_stat_activity WHERE application_name = %(app)s;"
)
PROMO_CAMPAIGN_OPEN_SQL = (
    "UPDATE ops.promo_campaign SET state = 'active', activated_at = %(activated_at)s "
    "WHERE campaign_id = %(campaign_id)s AND state = 'scheduled';"
)
PROMO_CAMPAIGN_STATE_SQL = (
    "SELECT state, activated_at FROM ops.promo_campaign WHERE campaign_id = %(campaign_id)s;"
)

ACTIVATION_BUDGET_SECONDS = 20.0
RELEASE_START_GRACE_SECONDS = 3.0
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
class _LongTxHandle:
    event_id: str
    clock: object
    source: object
    thread: threading.Thread | None = None
    stop: threading.Event = field(default_factory=threading.Event)
    observation_slot: list = field(default_factory=list)

    def observation(self):
        return self.observation_slot[0] if self.observation_slot else None


class LegacyClientLongTxCapability:
    """An old reporting client idles inside a REPEATABLE READ snapshot."""

    capability_id = "legacy_client_long_tx"
    _PARAMS = frozenset({"cutoff_created_at", "hold_seconds"})

    def declaration(self, occurrence: EventOccurrence) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            ownership=(ResourceOwnership(
                resource_key=f"session:legacy-long-tx:{occurrence.entity}",
                resource_kind="database_session",
            ),),
            max_activation_seconds=ACTIVATION_BUDGET_SECONDS,
        )

    def activate(self, context: CapabilityContext) -> EventActivationResult:
        context.occurrence.reject_unknown_params(self._PARAMS)
        cutoff = context.occurrence.require_number("cutoff_created_at")
        hold_seconds = context.occurrence.require_number("hold_seconds")
        handle = _LongTxHandle(
            event_id=context.occurrence.event_id, clock=context.clock, source=context.source,
        )

        def run() -> None:
            observation = run_legacy_long_tx(
                source=context.source,
                clock=context.clock,
                cutoff_created_at=cutoff,
                hold_seconds=hold_seconds,
                stop=handle.stop,
            )
            handle.observation_slot.append(observation)

        handle.thread = threading.Thread(target=run, name=f"pg5-longtx-{handle.event_id}", daemon=True)
        handle.thread.start()
        context.evidence.append({
            "kind": "capability_activation",
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
        })

        def evidence_now():
            observation = handle.observation()
            if observation is not None and observation.prevented:
                return {"observation": {
                    "held_seconds": observation.held_seconds,
                    "detail": observation.detail,
                    "protection_gucs": dict(observation.protection_gucs),
                }}
            connection = handle.source.connection(f"longtx-impact-{handle.event_id}")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(LONG_TX_IMPACT_SQL, {"app": LONG_TX_APPLICATION_NAME})
                    rows = cursor.fetchall()
            finally:
                connection.close()
            if rows:
                return {"observation": {
                    "idle_in_tx_sessions": [
                        {"pid": int(row[0]), "state": str(row[1]), "xact_age_seconds": float(row[2])}
                        for row in rows
                    ],
                }}
            return None

        attempt = _wait_for(evidence_now, clock=handle.clock, stop=handle.stop, budget_seconds=ACTIVATION_BUDGET_SECONDS)
        if attempt is None:
            raise RuntimeError(
                f"Legacy long transaction impact absent and not prevented: event_id={handle.event_id!r}"
            )
        observation = handle.observation()
        attempt = {"event_id": handle.event_id, **attempt}
        outcome = "prevented" if observation is not None and observation.prevented else "applied"
        if outcome == "prevented":
            attempt["mechanism"] = observation.mechanism
            attempt["protection_state"] = dict(observation.protection_gucs)
        return EventActivationResult(attempt=attempt, outcome=outcome, handle=handle)

    def alert(self, context: CapabilityContext, handle: object) -> Mapping[str, object]:
        return {
            "title": "存在长时间未提交的报表会话",
            "symptoms": ["旧版报表客户端事务年龄异常增长，持有订单表快照"],
            "severity": "warning",
            "category": "idle_in_transaction",
        }

    def cleanup(self, handle: object) -> None:
        handle = self._handle(handle)
        handle.stop.set()
        handle.thread.join(timeout=60)
        if handle.thread.is_alive():
            raise RuntimeError(
                f"Legacy long transaction session did not stop within its join timeout: "
                f"event_id={handle.event_id!r}"
            )

    def assert_clean(self, handle: object) -> Mapping[str, object]:
        handle = self._handle(handle)
        connection = handle.source.connection(f"longtx-clean-{handle.event_id}")
        try:
            with connection.cursor() as cursor:
                cursor.execute(LONG_TX_IMPACT_SQL, {"app": LONG_TX_APPLICATION_NAME})
                rows = cursor.fetchall()
        finally:
            connection.close()
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "clean": not rows,
            "remaining_sessions": len(rows),
        }

    def _handle(self, handle: object) -> _LongTxHandle:
        if not isinstance(handle, _LongTxHandle):
            raise ValueError(f"Unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


@dataclass(slots=True)
class _ReleaseHandle:
    event_id: str
    task_id: str
    clock: object
    source: object
    join_budget: float
    thread: threading.Thread | None = None
    stop: threading.Event = field(default_factory=threading.Event)
    report_slot: list = field(default_factory=list)
    started: threading.Event = field(default_factory=threading.Event)

    def report(self):
        return self.report_slot[0] if self.report_slot else None


class ReleaseWorkerDdlCapability:
    """One deploy-tool pass over the release plan (submit or deploy-timeout retry)."""

    capability_id = "release_worker_ddl"
    _PARAMS = frozenset({"task_id", "deploy_timeout_seconds"})

    def declaration(self, occurrence: EventOccurrence) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            ownership=(ResourceOwnership(
                resource_key=f"job:release-plan:{occurrence.entity}",
                resource_kind="background_job",
                mode="exclusive",
            ),),
            max_activation_seconds=60.0,
        )

    def activate(self, context: CapabilityContext) -> EventActivationResult:
        context.occurrence.reject_unknown_params(self._PARAMS)
        task_id = context.occurrence.require_str("task_id")
        deploy_timeout_seconds = context.occurrence.require_number("deploy_timeout_seconds")
        driver = require_driver(context, self.capability_id)
        worker = ReleaseWorker(
            source=context.source,
            clock=context.clock,
            evidence=context.evidence,
            scenario_origin_monotonic=driver.scoring_origin,
        )
        handle = _ReleaseHandle(
            event_id=context.occurrence.event_id,
            task_id=task_id,
            clock=context.clock,
            source=context.source,
            join_budget=deploy_timeout_seconds + 60.0,
        )

        def run() -> None:
            handle.started.set()
            report = worker.run_release_plan(
                start_task_id=task_id,
                deploy_timeout_seconds=deploy_timeout_seconds,
                stop=handle.stop,
            )
            handle.report_slot.append(report)

        handle.thread = threading.Thread(target=run, name=f"pg5-release-{handle.event_id}", daemon=True)
        handle.thread.start()
        context.evidence.append({
            "kind": "capability_activation",
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "task_id": task_id,
        })

        activated_at = handle.clock.monotonic()

        def evidence_now():
            report = handle.report()
            if report is not None:
                return {"final_outcome": report.final_outcome, "steps": [step.outcome for step in report.steps]}
            connection = handle.source.connection(f"release-impact-{handle.event_id}")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(DDL_WAIT_SQL, {"app": RELEASE_APPLICATION_NAME})
                    rows = cursor.fetchall()
            finally:
                connection.close()
            for row in rows:
                if str(row[1]) == "Lock":
                    return {
                        "observed": "ddl_waiting_for_lock",
                        "pid": int(row[0]),
                        "wait_event": str(row[2]),
                        "state": str(row[3]),
                    }
            # A healthy release pass never waits on a lock and may outlive the
            # activation budget (e.g. the dependent index build). Once the pass
            # has started and had time to either block or finish, initiation is
            # the observable activation state; step outcomes land in the job
            # ledger as terminal facts sampled at final evaluation.
            if handle.started.is_set() and handle.clock.monotonic() - activated_at >= RELEASE_START_GRACE_SECONDS:
                return {"observed": "release_pass_started"}
            return None

        attempt = _wait_for(evidence_now, clock=handle.clock, stop=handle.stop, budget_seconds=ACTIVATION_BUDGET_SECONDS)
        if attempt is None:
            raise RuntimeError(
                f"Release pass produced no observable state: event_id={handle.event_id!r}, "
                f"task_id={handle.task_id!r}"
            )
        # The deploy tool executed its pass; per-attempt step outcomes (applied,
        # lock_timeout, statement_timeout) live in the attempt evidence. A
        # deploy-timeout failure is an applied external input with a terminal
        # outcome, not a prevented one.
        outcome = "applied"
        return EventActivationResult(
            attempt={"event_id": handle.event_id, "task_id": handle.task_id, **attempt},
            outcome=outcome,
            handle=handle,
        )

    def alert(self, context: CapabilityContext, handle: object) -> Mapping[str, object]:
        return {
            "title": "发布任务排队，订单读写延迟上升",
            "symptoms": ["发布 DDL 等待表级锁，后续新事务排在 DDL 之后"],
            "severity": "critical",
            "category": "release_blocked",
        }

    def cleanup(self, handle: object) -> None:
        handle = self._handle(handle)
        handle.stop.set()
        handle.thread.join(timeout=handle.join_budget)
        if handle.thread.is_alive():
            raise RuntimeError(
                f"Release worker pass did not stop within its join timeout: "
                f"event_id={handle.event_id!r}, task_id={handle.task_id!r}"
            )

    def assert_clean(self, handle: object) -> Mapping[str, object]:
        handle = self._handle(handle)
        connection = handle.source.connection(f"release-clean-{handle.event_id}")
        try:
            with connection.cursor() as cursor:
                cursor.execute(DDL_WAIT_SQL, {"app": RELEASE_APPLICATION_NAME})
                rows = cursor.fetchall()
        finally:
            connection.close()
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "clean": not rows,
            "remaining_sessions": len(rows),
        }

    def _handle(self, handle: object) -> _ReleaseHandle:
        if not isinstance(handle, _ReleaseHandle):
            raise ValueError(f"Unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


@dataclass(slots=True)
class _BackfillHandle:
    event_id: str
    task_id: str
    clock: object
    source: object
    worker: BackfillWorker


class BackfillWorkerCapability:
    """The persistent backfill task starts (or waits for its schema dependency)."""

    capability_id = "backfill_worker"
    _PARAMS = frozenset({"task_id"})

    def declaration(self, occurrence: EventOccurrence) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            ownership=(ResourceOwnership(
                resource_key=f"job:backfill:{occurrence.entity}",
                resource_kind="background_job",
                mode="shared",
            ),),
            max_activation_seconds=ACTIVATION_BUDGET_SECONDS,
        )

    def activate(self, context: CapabilityContext) -> EventActivationResult:
        context.occurrence.reject_unknown_params(self._PARAMS)
        task_id = context.occurrence.require_str("task_id")
        worker = BackfillWorker(source=context.source, clock=context.clock, evidence=context.evidence)
        worker.start_in_background(task_id=task_id)
        handle = _BackfillHandle(
            event_id=context.occurrence.event_id,
            task_id=task_id,
            clock=context.clock,
            source=context.source,
            worker=worker,
        )
        context.evidence.append({
            "kind": "capability_activation",
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "task_id": task_id,
        })

        def task_started():
            connection = handle.source.connection(f"backfill-impact-{handle.event_id}")
            try:
                task = read_release_task(connection, handle.task_id)
                if task.status in {"waiting_dependency", "running", "done"}:
                    return {"task_status": task.status, "rows_done": task.rows_done}
                return None
            finally:
                connection.close()

        attempt = _wait_for(
            task_started, clock=handle.clock, stop=threading.Event(), budget_seconds=ACTIVATION_BUDGET_SECONDS
        )
        if attempt is None:
            raise RuntimeError(
                f"Backfill task never reached a started state: event_id={handle.event_id!r}, "
                f"task_id={handle.task_id!r}"
            )
        return EventActivationResult(
            attempt={"event_id": handle.event_id, "task_id": handle.task_id, **attempt},
            outcome="applied",
            handle=handle,
        )

    def alert(self, context: CapabilityContext, handle: object) -> Mapping[str, object]:
        return {
            "title": "数据回填任务进入队列",
            "symptoms": ["迁移排程的批量回填将按任务队列与限速推进，WAL 与 I/O 上升"],
            "severity": "info",
            "category": "scheduled_migration",
        }

    def cleanup(self, handle: object) -> None:
        handle = self._handle(handle)
        report = handle.worker.stop()
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "delivery_note": report.delivery_note,
            "rows_backfilled": report.rows_backfilled,
        }

    def assert_clean(self, handle: object) -> Mapping[str, object]:
        handle = self._handle(handle)
        connection = handle.source.connection(f"backfill-clean-{handle.event_id}")
        try:
            task = read_release_task(connection, handle.task_id)
        finally:
            connection.close()
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "clean": True,
            "task_status": task.status,
            "rows_done": task.rows_done,
        }

    def _handle(self, handle: object) -> _BackfillHandle:
        if not isinstance(handle, _BackfillHandle):
            raise ValueError(f"Unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


class PromoCampaignPeakCapability:
    """The marketing campaign opens: traffic switches to the promo tier and the
    campaign publishes its own VIP threshold override. One business act with two
    public effects — the traffic tier and the `ops.promo_campaign` caliber row
    the backfill resolves against. Trigger is silent: the campaign row itself is
    the discoverable evidence, no alert announces the mechanism."""

    capability_id = "promo_campaign_peak"
    _PARAMS = frozenset({"tier", "campaign_id"})

    def declaration(self, occurrence: EventOccurrence) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            ownership=(ResourceOwnership(
                resource_key=f"driver:traffic-tier:{occurrence.entity}",
                resource_kind="workload_plan",
            ),),
            max_activation_seconds=10.0,
        )

    def activate(self, context: CapabilityContext) -> EventActivationResult:
        context.occurrence.reject_unknown_params(self._PARAMS)
        tier = context.occurrence.require_str("tier")
        campaign_id = context.occurrence.require_str("campaign_id")
        driver = require_driver(context, self.capability_id)
        driver.apply_tier(tier)
        activated_at = context.clock.monotonic()
        connection = context.source.connection("promo-campaign-open")
        try:
            with connection.cursor() as cursor:
                cursor.execute(PROMO_CAMPAIGN_OPEN_SQL, {
                    "campaign_id": campaign_id, "activated_at": activated_at,
                })
                if cursor.rowcount != 1:
                    raise RuntimeError(
                        f"Promo campaign open must transition the scheduled row exactly once: "
                        f"campaign_id={campaign_id!r}, rowcount={cursor.rowcount}"
                    )
            connection.commit()
        finally:
            connection.close()
        return EventActivationResult(
            attempt={
                "tier": tier,
                "campaign_id": campaign_id,
                "campaign_state": "active",
                "activated_at": activated_at,
            },
            outcome="applied",
            handle={"tier": tier, "campaign_id": campaign_id},
        )

    def alert(self, context: CapabilityContext, handle: object) -> Mapping[str, object]:
        return {
            "title": "促销活动窗口开启",
            "symptoms": ["促销流量档位生效，订单与支付并发上升"],
            "severity": "info",
            "category": "planned_traffic_change",
        }

    def cleanup(self, handle: object) -> Mapping[str, object]:
        # The campaign stays open by design: its caliber must remain the live
        # config the delivery verifier recomputes against. Nothing to revert.
        return {"campaign_id": handle["campaign_id"], "state": "active"}

    def assert_clean(self, handle: object) -> Mapping[str, object]:
        return {"capability_id": self.capability_id, "clean": True}


CAPABILITY_REGISTRY = CapabilityRegistry((
    LegacyClientLongTxCapability(),
    ReleaseWorkerDdlCapability(),
    BackfillWorkerCapability(),
    PromoCampaignPeakCapability(),
))
