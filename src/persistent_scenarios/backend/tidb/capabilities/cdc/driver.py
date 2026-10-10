"""Persistent workload drivers for tidb_cdc_downstream_freshness.

Two services share one persistent topology:

- ``orders`` (upstream TiDB): continuously submitted paid-order transactions
  paced by a public traffic-control row; every commit is source evidence.
- ``fulfilment_visibility`` (downstream MySQL read model): every source
  commit becomes a visibility obligation - the committed (business key,
  version, marker) must be visible downstream before the deadline.

The downstream batch processor is a real fulfilment-side job whose schedule
lives in a public control table, so the agent can retune it durably. All
business truth goes to two append-only trusted ledgers outside the databases.
Transport failures on a live connection are reconnect-and-retry client facts;
they are recorded, and the first error of a fresh connection propagates.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Mapping

from src.persistent_scenarios.model.spec import OltpObjective, PersistentScenarioSpec
from src.persistent_scenarios.runtime.clock import Clock
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    LedgerTerminal,
    TransactionAttempt,
    TrustedLedger,
)

from .connections import CdcConnectionFactories, TRANSPORT_ERRORS
from .schema import (
    BATCH_CONTROL_TABLE,
    DOWNSTREAM_DATABASE,
    MAINTENANCE_LOG_TABLE,
    OPS_DATABASE,
    ORDERS_TABLE,
    STATE_PAID,
    TRAFFIC_CONTROL_TABLE,
    UPSTREAM_DATABASE,
    marker_for,
)

ORDERS_SERVICE_ID = "orders"
VISIBILITY_SERVICE_ID = "fulfilment_visibility"

_ORDERS_LEDGER_ID = "cdc_orders"
_VISIBILITY_LEDGER_ID = "cdc_visibility"

_POLL_INTERVAL_SECONDS = 0.5
_CONTROL_POLL_SECONDS = 2.0
_FULFILMENT_READ_INTERVAL_SECONDS = 1.0
_DRAIN_TIMEOUT_SECONDS = 120.0


@dataclass(slots=True)
class _PendingObligation:
    business_id: str
    order_id: int
    version: int
    marker: str
    planned_at: float
    deadline_at: float
    poll_count: int = 0


def _record_reconnect(log, label: str, error: Exception) -> None:
    log(f"{label} transport reconnect: {type(error).__name__}: {error}")


class _OrderWriter(threading.Thread):
    """Continuous upstream order submissions paced by the traffic-control row."""

    def __init__(self, *, factories, ledger, clock, orders_deadline_seconds: float,
                 confirm_fraction: float, first_order_id: int, log):
        super().__init__(name="cdc-order-writer", daemon=True)
        self._factories = factories
        self._ledger = ledger
        self._clock = clock
        self._orders_deadline = float(orders_deadline_seconds)
        self._confirm_fraction = float(confirm_fraction)
        self._next_order_id = int(first_order_id)
        self._log = log
        self._shutdown_event = threading.Event()
        self._no_new_requests = threading.Event()
        self._visibility_sink = None
        self.submitted = 0
        self.committed = 0
        self.aborted = 0
        self.client_retries = 0
        self.rate_samples: list[float] = []

    def attach_visibility_sink(self, sink) -> None:
        self._visibility_sink = sink

    def stop_new_requests(self) -> None:
        self._no_new_requests.set()

    def shutdown(self) -> None:
        self._shutdown_event.set()

    def run(self) -> None:
        conn = self._factories.upstream()
        cursor = conn.cursor()
        window_start = self._clock.monotonic()
        window_committed = 0
        while not self._shutdown_event.is_set():
            if self._no_new_requests.is_set():
                break
            try:
                target_rate = self._read_target_rate(cursor)
                if target_rate <= 0:
                    self._sleep(_CONTROL_POLL_SECONDS)
                    continue
                self._submit_one(cursor)
            except TRANSPORT_ERRORS as exc:
                _record_reconnect(self._log, "order-writer", exc)
                conn.close()
                conn = self._factories.upstream()
                cursor = conn.cursor()
                continue
            window_committed += 1
            elapsed = self._clock.monotonic() - window_start
            if elapsed >= 5.0:
                self.rate_samples.append(window_committed / elapsed)
                window_start = self._clock.monotonic()
                window_committed = 0
            self._sleep(1.0 / target_rate)
        conn.close()

    def _sleep(self, seconds: float) -> None:
        self._clock.wait_until(self._clock.monotonic() + seconds, self._shutdown_event)

    def _read_target_rate(self, cursor) -> float:
        cursor.execute(
            f"SELECT target_orders_per_sec FROM {OPS_DATABASE}.{TRAFFIC_CONTROL_TABLE} WHERE id = 1"
        )
        return float(cursor.fetchall()[0][0])

    def _submit_one(self, cursor) -> None:
        now = self._clock.monotonic()
        order_id = self._next_order_id
        self._next_order_id += 1
        self.submitted += 1
        marker = marker_for(order_id, 1, now)
        business_id = f"order-{order_id}"
        self._ledger.append_planned_transaction(
            business_id=business_id, service_id=ORDERS_SERVICE_ID,
            tx_kind="submit_order", planned_at_monotonic=now,
            deadline_at_monotonic=now + self._orders_deadline,
        )
        cursor.execute(
            f"INSERT INTO {UPSTREAM_DATABASE}.{ORDERS_TABLE} "
            "(order_id, version, state, amount, marker, updated_at) VALUES "
            f"({order_id}, 1, '{STATE_PAID}', {order_id % 500 + 1}.25, '{marker}', NOW(3))"
        )
        self._record_submit(business_id, now, order_id, marker, 1, STATE_PAID)
        if (order_id % 10) < int(self._confirm_fraction * 10):
            self._confirm_order(cursor, order_id)

    def _record_submit(self, business_id: str, started: float, order_id: int,
                       marker: str, version: int, state: str) -> None:
        completed = self._clock.monotonic()
        self._ledger.append_transaction_attempt(
            business_id=business_id,
            attempt=TransactionAttempt(attempt_index=1, started_at_monotonic=started,
                                       ended_at_monotonic=completed,
                                       outcome=AttemptOutcome.COMMITTED, detail={}),
        )
        self._ledger.append_transaction_terminal(
            business_id=business_id, terminal=LedgerTerminal.COMPLETED,
            completed_at_monotonic=completed, result_digest=f"{order_id}:{version}:{state}:{marker}",
        )
        self.committed += 1
        if self._visibility_sink is not None:
            self._visibility_sink(order_id, marker, completed)

    def _confirm_order(self, cursor, order_id: int) -> None:
        now = self._clock.monotonic()
        marker = marker_for(order_id, 2, now)
        business_id = f"order-{order_id}-confirm"
        self._ledger.append_planned_transaction(
            business_id=business_id, service_id=ORDERS_SERVICE_ID,
            tx_kind="confirm_order", planned_at_monotonic=now,
            deadline_at_monotonic=now + self._orders_deadline,
        )
        cursor.execute(
            f"UPDATE {UPSTREAM_DATABASE}.{ORDERS_TABLE} SET version = 2, state = 'shipped', "
            f"marker = '{marker}', updated_at = NOW(3) WHERE order_id = {order_id}"
        )
        self._record_submit(business_id, now, order_id, marker, 2, "shipped")

    def facts(self) -> Mapping[str, object]:
        return {
            "submitted": self.submitted,
            "committed": self.committed,
            "aborted": self.aborted,
            "client_retries": self.client_retries,
            "avg_orders_per_sec": (
                sum(self.rate_samples) / len(self.rate_samples) if self.rate_samples else 0.0
            ),
        }


class _FulfilmentService(threading.Thread):
    """Downstream fulfilment reads: resolves visibility obligations and serves paid-order reads."""

    def __init__(self, *, factories, ledger, clock, visibility_deadline_seconds: float, log):
        super().__init__(name="cdc-fulfilment-service", daemon=True)
        self._factories = factories
        self._ledger = ledger
        self._clock = clock
        self._deadline = float(visibility_deadline_seconds)
        self._log = log
        self._shutdown_event = threading.Event()
        self._lock = threading.Lock()
        self._pending: dict[str, _PendingObligation] = {}
        self.resolved: list[float] = []
        self.read_latencies: list[float] = []
        self.expired = 0

    def record_commit(self, order_id: int, marker: str, committed_at: float) -> None:
        """Sink called by the order writer for every upstream commit."""
        version = int(marker.split("-v")[1].split("-")[0])
        business_id = f"order-{order_id}:v{version}"
        with self._lock:
            self._pending[business_id] = _PendingObligation(
                business_id=business_id, order_id=order_id, version=version, marker=marker,
                planned_at=committed_at, deadline_at=committed_at + self._deadline,
            )
        self._ledger.append_planned_transaction(
            business_id=business_id, service_id=VISIBILITY_SERVICE_ID,
            tx_kind="order_visibility", planned_at_monotonic=committed_at,
            deadline_at_monotonic=committed_at + self._deadline,
        )

    def stop_new_requests(self) -> None:
        pass  # obligations follow upstream commits; nothing is planned here

    def shutdown(self) -> None:
        self._shutdown_event.set()

    def outstanding(self) -> int:
        with self._lock:
            return len(self._pending)

    def run(self) -> None:
        conn = self._factories.downstream()
        cursor = conn.cursor()
        next_read = self._clock.monotonic()
        while not self._shutdown_event.is_set():
            try:
                self._resolve_due(cursor)
                if self._clock.monotonic() >= next_read:
                    self._fulfilment_read(cursor)
                    next_read = self._clock.monotonic() + _FULFILMENT_READ_INTERVAL_SECONDS
            except TRANSPORT_ERRORS as exc:
                _record_reconnect(self._log, "fulfilment-service", exc)
                conn.close()
                conn = self._factories.downstream()
                cursor = conn.cursor()
                continue
            self._clock.wait_until(self._clock.monotonic() + _POLL_INTERVAL_SECONDS, self._shutdown_event)
        conn.close()

    def _resolve_due(self, cursor) -> None:
        now = self._clock.monotonic()
        with self._lock:
            candidates = list(self._pending.values())
        if not candidates:
            return
        # one batched poll per cycle: resolve everything already visible,
        # expire only what passed its deadline unseen
        ids = ",".join(str(item.order_id) for item in candidates)
        cursor.execute(
            f"SELECT order_id, version, marker FROM {DOWNSTREAM_DATABASE}.{ORDERS_TABLE} "
            f"WHERE order_id IN ({ids})"
        )
        observed = {int(row[0]): (int(row[1]), str(row[2])) for row in cursor.fetchall()}
        for obligation in candidates:
            down = observed.get(obligation.order_id)
            # the required (version, marker) is visible once the read model serves
            # that version or any later one (a newer version implies the older
            # commit was applied; its marker was then overwritten by the update)
            visible = down is not None and (
                down[0] > obligation.version
                or (down[0] == obligation.version and down[1] == obligation.marker)
            )
            past_deadline = now >= obligation.deadline_at
            if not visible and not past_deadline:
                with self._lock:
                    pending = self._pending.get(obligation.business_id)
                    if pending is not None:
                        pending.poll_count += 1
                continue
            observed_at = self._clock.monotonic()
            with self._lock:
                self._pending.pop(obligation.business_id, None)
            if visible:
                self.resolved.append(observed_at - obligation.planned_at)
                terminal, outcome = LedgerTerminal.COMPLETED, AttemptOutcome.COMMITTED
                digest = f"{obligation.order_id}:{obligation.version}:{obligation.marker}"
            else:
                self.expired += 1
                terminal, outcome = LedgerTerminal.INCOMPLETE_TIMEOUT, AttemptOutcome.TIMED_OUT
                digest = None
            self._ledger.append_transaction_attempt(
                business_id=obligation.business_id,
                attempt=TransactionAttempt(attempt_index=1, started_at_monotonic=obligation.planned_at,
                                           ended_at_monotonic=observed_at, outcome=outcome,
                                           detail={"poll_count": obligation.poll_count + 1,
                                                   "downstream_version": down[0] if down else None}),
            )
            self._ledger.append_transaction_terminal(
                business_id=obligation.business_id, terminal=terminal,
                completed_at_monotonic=observed_at if visible else None, result_digest=digest,
            )

    def _fulfilment_read(self, cursor) -> None:
        started = self._clock.monotonic()
        cursor.execute(
            f"SELECT order_id FROM {DOWNSTREAM_DATABASE}.{ORDERS_TABLE} "
            f"WHERE state = '{STATE_PAID}' ORDER BY order_id DESC LIMIT 20"
        )
        cursor.fetchall()
        self.read_latencies.append(self._clock.monotonic() - started)

    def facts(self) -> Mapping[str, object]:
        resolved = list(self.resolved)
        return {
            "resolved_count": len(resolved),
            "expired_count": self.expired,
            "outstanding": self.outstanding(),
            "visibility_p50_seconds": (sorted(resolved)[len(resolved) // 2] if resolved else None),
            "visibility_max_seconds": (max(resolved) if resolved else None),
            "fulfilment_read_p50_seconds": (
                sorted(self.read_latencies)[len(self.read_latencies) // 2]
                if self.read_latencies else None
            ),
        }


class DownstreamBatchWorker(threading.Thread):
    """Fulfilment-side batch processor; its schedule lives in a public control table.

    The worker re-reads ``batch_control`` every cycle, so durable operator
    retuning (rows/pause) takes effect without any code change and survives
    later campaign windows.
    """

    def __init__(self, *, factories, clock, log):
        super().__init__(name="cdc-batch-worker", daemon=True)
        self._factories = factories
        self._clock = clock
        self._log = log
        self._shutdown_event = threading.Event()
        self.rows_written = 0
        self.schedule_changes_observed = 0
        self.batches_run = 0

    def stop_new_requests(self) -> None:
        pass

    def shutdown(self) -> None:
        self._shutdown_event.set()

    def run(self) -> None:
        conn = self._factories.downstream()
        cursor = conn.cursor()
        schedule: tuple[int, int, float] = (0, 0, 0.0)
        next_control_read = 0.0
        next_batch_at = None
        payload = "x" * 512
        while not self._shutdown_event.is_set():
            now = self._clock.monotonic()
            try:
                if now >= next_control_read:
                    new_schedule = self._read_schedule(cursor)
                    if new_schedule != schedule:
                        self.schedule_changes_observed += 1
                        schedule = new_schedule
                    next_control_read = now + _CONTROL_POLL_SECONDS
                enabled, batch_rows, pause = schedule
                if not enabled:
                    next_batch_at = None
                    self._clock.wait_until(now + _CONTROL_POLL_SECONDS, self._shutdown_event)
                    continue
                if next_batch_at is None:
                    next_batch_at = now
                if now >= next_batch_at:
                    self._run_batch(cursor, batch_rows, payload)
                    next_batch_at = self._clock.monotonic() + pause
                    continue
                self._clock.wait_until(min(next_batch_at, now + _POLL_INTERVAL_SECONDS), self._shutdown_event)
            except TRANSPORT_ERRORS as exc:
                _record_reconnect(self._log, "batch-worker", exc)
                conn.close()
                conn = self._factories.downstream()
                cursor = conn.cursor()
        conn.close()

    def _read_schedule(self, cursor) -> tuple[int, int, float]:
        cursor.execute(
            f"SELECT enabled, batch_rows, batch_pause_seconds FROM "
            f"{DOWNSTREAM_DATABASE}.{BATCH_CONTROL_TABLE} WHERE id = 1"
        )
        row = cursor.fetchall()[0]
        return int(row[0]), int(row[1]), float(row[2])

    _BATCH_STATEMENT_CHUNK = 1000  # rows per INSERT statement; a batch may span chunks
    _LOCK_SCAN_ROWS = 200          # recent read-model orders locked per batch transaction

    def _run_batch(self, cursor, batch_rows: int, payload: str) -> None:
        # staging-table churn: write the new batch, then drop the previous one,
        # so sustained batch pressure never grows the read model without bound.
        # The whole batch runs inside one transaction that also locks the most
        # recent read-model orders for its verification scan, so the sink apply
        # queues behind real downstream row locks (sink backpressure).
        first = 6_000_000 + self.rows_written
        cursor.execute("BEGIN")
        cursor.execute(
            f"SELECT order_id FROM {DOWNSTREAM_DATABASE}.{ORDERS_TABLE} "
            f"ORDER BY order_id DESC LIMIT {self._LOCK_SCAN_ROWS} FOR UPDATE"
        )
        cursor.fetchall()
        for chunk_start in range(0, batch_rows, self._BATCH_STATEMENT_CHUNK):
            chunk = batch_rows - chunk_start if chunk_start + self._BATCH_STATEMENT_CHUNK > batch_rows \
                else self._BATCH_STATEMENT_CHUNK
            values = ",".join(
                f"({first + chunk_start + i}, {self.batches_run}, '{payload}', NOW(3))"
                for i in range(chunk)
            )
            cursor.execute(
                f"INSERT IGNORE INTO {DOWNSTREAM_DATABASE}.fulfilment_batches "
                f"(batch_id, batch_no, payload, created_at) VALUES {values}"
            )
        if self.batches_run > 0:
            cursor.execute(
                f"DELETE FROM {DOWNSTREAM_DATABASE}.fulfilment_batches WHERE batch_no = "
                f"{self.batches_run - 1}"
            )
        cursor.execute("COMMIT")
        self.rows_written += batch_rows
        self.batches_run += 1

    def facts(self) -> Mapping[str, object]:
        return {
            "batch_rows_written": self.rows_written,
            "batches_run": self.batches_run,
            "schedule_changes_observed": self.schedule_changes_observed,
        }


class UpstreamMaintenanceWorker(threading.Thread):
    """Upstream statistics maintenance: a real, recurring business task.

    The fulfilment pipeline refreshes the order-store optimizer statistics on
    a fixed cycle and records every run in the ``ops.maintenance_log`` audit
    table (start, end, duration, status). The passes are light and never
    touch business rows, but they are real upstream work: during any
    overlapping incident window they show up in the same tool results the
    agent reads (processlist, statement summaries, the maintenance audit) and
    must be excluded by cross-evidence, not by name.
    """

    _MAINTENANCE_TASK = "orders_stats_refresh"

    def __init__(self, *, factories, clock, log, cycle_seconds: float = 600.0):
        super().__init__(name="cdc-maintenance-worker", daemon=True)
        self._factories = factories
        self._clock = clock
        self._log = log
        self._cycle_seconds = float(cycle_seconds)
        self._shutdown_event = threading.Event()
        self.runs_completed = 0

    def stop_new_requests(self) -> None:
        pass

    def shutdown(self) -> None:
        self._shutdown_event.set()

    def run(self) -> None:
        conn = self._factories.upstream()
        cursor = conn.cursor()
        next_run = self._clock.monotonic()
        while not self._shutdown_event.is_set():
            now = self._clock.monotonic()
            if now < next_run:
                self._clock.wait_until(min(next_run, now + _POLL_INTERVAL_SECONDS), self._shutdown_event)
                continue
            try:
                self._run_pass(cursor, now)
            except TRANSPORT_ERRORS as exc:
                _record_reconnect(self._log, "maintenance-worker", exc)
                conn.close()
                conn = self._factories.upstream()
                cursor = conn.cursor()
            next_run = self._clock.monotonic() + self._cycle_seconds
        conn.close()

    def _run_pass(self, cursor, started_at: float) -> None:
        run_id = self.runs_completed + 1
        cursor.execute(
            f"INSERT INTO {OPS_DATABASE}.{MAINTENANCE_LOG_TABLE} "
            "(run_id, task, started_at, finished_at, duration_seconds, status) VALUES "
            f"({run_id}, '{self._MAINTENANCE_TASK}', NOW(3), NULL, NULL, 'running')"
        )
        cursor.execute(f"ANALYZE TABLE {UPSTREAM_DATABASE}.{ORDERS_TABLE}")
        finished_at = self._clock.monotonic()
        duration = finished_at - started_at
        cursor.execute(
            f"UPDATE {OPS_DATABASE}.{MAINTENANCE_LOG_TABLE} SET finished_at = NOW(3), "
            f"duration_seconds = {duration:.3f}, status = 'completed' WHERE run_id = {run_id}"
        )
        self.runs_completed += 1

    def facts(self) -> Mapping[str, object]:
        return {"maintenance_runs": self.runs_completed}


class CdcFreshnessWorkloadRuntime:
    """``PersistentWorkloadRuntime`` for the CDC freshness scenario."""

    def __init__(self, *, environment, spec: PersistentScenarioSpec, run_id: str, clock: Clock,
                 factories: CdcConnectionFactories, ledger_dir, log,
                 confirm_fraction: float = 0.3, first_order_id: int = 1_000_000):
        self._environment = environment
        self._spec = spec
        self._run_id = run_id
        self._clock = clock
        self._log = log
        orders = self._objective(ORDERS_SERVICE_ID)
        visibility = self._objective(VISIBILITY_SERVICE_ID)
        self._orders_ledger = TrustedLedger(
            _ORDERS_LEDGER_ID, ledger_dir / f"{run_id}-{_ORDERS_LEDGER_ID}.jsonl")
        self._visibility_ledger = TrustedLedger(
            _VISIBILITY_LEDGER_ID, ledger_dir / f"{run_id}-{_VISIBILITY_LEDGER_ID}.jsonl")
        self._writer = _OrderWriter(
            factories=factories, ledger=self._orders_ledger, clock=clock,
            orders_deadline_seconds=orders.deadline_seconds,
            confirm_fraction=confirm_fraction, first_order_id=first_order_id, log=log,
        )
        self._fulfilment = _FulfilmentService(
            factories=factories, ledger=self._visibility_ledger, clock=clock,
            visibility_deadline_seconds=visibility.deadline_seconds, log=log,
        )
        self._writer.attach_visibility_sink(self._fulfilment.record_commit)
        self._batch = DownstreamBatchWorker(factories=factories, clock=clock, log=log)
        self._maintenance = UpstreamMaintenanceWorker(factories=factories, clock=clock, log=log)

    def _objective(self, service_id: str) -> OltpObjective:
        for service in self._spec.services:
            if isinstance(service, OltpObjective) and service.service_id == service_id:
                return service
        raise ValueError(
            f"CDC freshness spec must declare an oltp objective for service_id={service_id!r}: "
            f"declared={[service.service_id for service in self._spec.services]!r}"
        )

    def start(self) -> None:
        self._writer.start()
        self._fulfilment.start()
        self._batch.start()
        self._maintenance.start()

    def wait_for_warmup(self) -> float:
        deadline = self._clock.monotonic() + 120.0
        while self._clock.monotonic() < deadline:
            if self._writer.committed >= 30:
                break
            self._clock.wait_until(self._clock.monotonic() + 0.5, threading.Event())
        return self._clock.monotonic()

    def stop_new_requests(self) -> None:
        self._writer.stop_new_requests()

    def drain(self) -> None:
        deadline = self._clock.monotonic() + _DRAIN_TIMEOUT_SECONDS
        while self._fulfilment.outstanding() > 0 and self._clock.monotonic() < deadline:
            self._clock.wait_until(self._clock.monotonic() + 0.5, threading.Event())

    def stop(self) -> None:
        self._writer.shutdown()
        self._fulfilment.shutdown()
        self._batch.shutdown()
        self._maintenance.shutdown()
        self._writer.join(timeout=30)
        self._fulfilment.join(timeout=30)
        self._batch.join(timeout=30)
        self._maintenance.join(timeout=30)

    def ledgers(self) -> Mapping[str, TrustedLedger]:
        return {"orders": self._orders_ledger, "visibility": self._visibility_ledger}

    def baseline_facts(self) -> Mapping[str, object]:
        return {
            "orders": self._writer.facts(),
            "visibility": self._fulfilment.facts(),
            "batch": self._batch.facts(),
            "maintenance": self._maintenance.facts(),
        }
