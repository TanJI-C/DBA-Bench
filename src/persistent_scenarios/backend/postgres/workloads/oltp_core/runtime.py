"""Workload driver for the pg5 OLTP instances.

The driver is the production client system: a bounded pool of application
worker threads (each owning one real pooled database connection, recycled by
age) executing externally scheduled logical trade operations, an integrity
probe, and a control-table poller. Event capabilities drive it through
`apply_tier` and read it through `telemetry`; nothing here knows event IDs.

Scheduling model: one trade scheduler plans paired checkout+payment logical
operations (payment fires only after its checkout commits; a rejected or lost
checkout terminates its payment as a business loss), and one read scheduler
plans stock reads. Operations still queued when the run closes terminate as
`pending_at_close`, so nothing disappears from the denominator.
"""

from __future__ import annotations

import queue
import random
import threading
import time
from dataclasses import dataclass
from typing import Mapping

import psycopg2

from . import client
from .client import AttemptKind, FlowFailure, PlaceOrderPayload, PayOrderPayload
from .control import ClientConfig, ClientConfigPoller, column_exists
from .ledger import AttemptOutcome, BusinessLedger, OpKind
from .ports import Clock, ConnectionSource, DBConnection, EvidenceLedgerFile
from .schema import PROMO_SKUS, price_cents_for_sku
from .traffic import TrafficPlan, TrafficTier


@dataclass(frozen=True, slots=True)
class DriverConfig:
    pool_size: int
    control_poll_seconds: float = 5.0
    connection_max_lifetime_seconds: float = 60.0
    pay_lag_seconds: float = 0.5
    integrity_probe_interval_seconds: float = 60.0
    seed: int = 20260918

    def __post_init__(self) -> None:
        if self.pool_size <= 0:
            raise ValueError(f"pool_size must be positive: value={self.pool_size!r}")
        for name in ("control_poll_seconds", "connection_max_lifetime_seconds", "integrity_probe_interval_seconds"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive: value={getattr(self, name)!r}")
        if self.pay_lag_seconds < 0:
            raise ValueError(f"pay_lag_seconds must be non-negative: value={self.pay_lag_seconds!r}")


NEW_VERSION_CHECK_INTERVAL_SECONDS = 5.0
_DRAIN_GRACE_SECONDS = 30.0

PAID_WITHOUT_PAYMENT_PROBE_SQL = (
    "SELECT count(*) FROM shop.orders o LEFT JOIN shop.payments p ON p.order_id = o.order_id "
    "WHERE o.status = 'paid' AND p.order_id IS NULL AND o.order_id NOT LIKE 'hist-%';"
)
NEGATIVE_INVENTORY_PROBE_SQL = "SELECT count(*) FROM shop.inventory WHERE qty_available < 0;"


@dataclass(frozen=True, slots=True)
class _WorkItem:
    op_id: str
    flow_id: str
    place_payload: PlaceOrderPayload | None
    pay_payload: PayOrderPayload | None
    sku: str
    scheduled_at: float
    deadline_at: float


@dataclass(frozen=True, slots=True)
class StockReadObservation:
    scheduled_at: float
    ended_at: float
    latency_ms: float
    outcome: str


@dataclass(frozen=True, slots=True)
class ProbeObservation:
    checked_at: float
    paid_without_payment: int
    negative_inventory: int


@dataclass(frozen=True, slots=True)
class DriverRunSummary:
    tier_schedule: Mapping[str, float]
    applied_config_versions: tuple[int, ...]
    stock_reads: tuple[StockReadObservation, ...]
    probes: tuple[ProbeObservation, ...]


class OltpWorkloadDriver:
    """Runs the externally planned trade workload against one PostgreSQL."""

    def __init__(
        self,
        *,
        source: ConnectionSource,
        clock: Clock,
        evidence: EvidenceLedgerFile,
        plan: TrafficPlan,
        config: DriverConfig,
        run_id: str,
        scoring_origin: float,
        horizon_seconds: float,
        input_stop_seconds: float,
        warmup_seconds: float = 0.0,
        new_version_column: str | None = None,
    ) -> None:
        if input_stop_seconds >= horizon_seconds:
            raise ValueError(
                "Business input must stop before the horizon: "
                f"input_stop_seconds={input_stop_seconds}, horizon_seconds={horizon_seconds}"
            )
        self.source = source
        self.clock = clock
        self.evidence = evidence
        self.plan = plan
        self.config = config
        self.control_poll_seconds = config.control_poll_seconds
        self.run_id = run_id
        self._scoring_origin = scoring_origin
        self._warmup_seconds = warmup_seconds
        self._input_stop_seconds = input_stop_seconds
        self._input_stop = threading.Event()
        self._new_version_column = new_version_column
        self.ledger = BusinessLedger(evidence)
        self._poller = ClientConfigPoller(source, clock, poll_seconds=config.control_poll_seconds)
        self._work_queue: queue.Queue[_WorkItem] = queue.Queue()
        self._pending_pay: dict[str, _WorkItem] = {}
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        self._sequence = 0
        self._sequence_lock = threading.Lock()
        self._rng = random.Random(config.seed)
        self._tier_lock = threading.Lock()
        self._current_tier = plan.tiers[0]
        self._stock_reads: list[StockReadObservation] = []
        self._probes: list[ProbeObservation] = []
        self._config_versions: list[int] = []
        self._thread_local = threading.local()
        self._worker_busy = [0] * config.pool_size
        self._probe_error: BaseException | None = None
        self._finished = False

    # -- lifecycle: PersistentWorkloadRuntime protocol ------------------------

    def start(self) -> None:
        if self._threads:
            raise RuntimeError("OltpWorkloadDriver cannot start twice")
        self._poller.start()
        self._config_versions.append(self._poller.applied_version())
        for index in range(self.config.pool_size):
            thread = threading.Thread(
                target=self._worker_loop, args=(index,), name=f"pg5-oltp-worker-{index}", daemon=True
            )
            thread.start()
            self._threads.append(thread)
        for name, target in (
            ("trade", self._trade_scheduler_loop),
            ("stock_read", self._stock_scheduler_loop),
            ("integrity_probe", self._probe_loop),
        ):
            thread = threading.Thread(target=target, name=f"pg5-oltp-{name}", daemon=True)
            thread.start()
            self._threads.append(thread)

    def wait_for_warmup(self) -> float:
        """Blocks through the real warmup phase and returns the scoring start.

        The warmup window is real time: business arrivals
        scheduled inside it stay out of the engine's scoring window, which
        begins at the returned instant.
        """

        scoring_start = self._scoring_origin + self._warmup_seconds
        if not self.clock.wait_until(scoring_start, self._stop):
            raise RuntimeError(f"pg5 OLTP driver stopped before warmup completed: run_id={self.run_id!r}")
        # Return the actual clock at return time, never a nominal deadline in
        # the past: the engine appends timeline entries after this point and
        # its canonical timeline forbids moving backwards.
        return self.clock.monotonic()

    def stop_new_requests(self) -> None:
        """Stops the arrival schedulers; queued operations keep executing."""

        self._input_stop.set()

    def drain(self) -> None:
        """Waits out the operational grace period for in-flight work to land.

        The grace bound is wall-clock on purpose: drain is the harness's
        operational shutdown allowance, while all business timing (deadlines,
        latencies) stays on the injected monotonic clock.
        """

        deadline = time.monotonic() + _DRAIN_GRACE_SECONDS
        while time.monotonic() < deadline:
            if self._work_queue.empty() and not any(self._worker_busy) and not self._pending_pay:
                return
            time.sleep(0.02)

    def stop(self) -> DriverRunSummary:
        if self._finished:
            raise RuntimeError("OltpWorkloadDriver has already been drained")
        self._finished = True
        self._stop.set()
        for thread in self._threads:
            thread.join(timeout=30)
            if thread.is_alive():
                raise RuntimeError(
                    f"pg5 OLTP driver thread did not stop within its join timeout: thread={thread.name!r}"
                )
        self._poller.stop()
        if self._probe_error is not None:
            raise RuntimeError(
                f"pg5 OLTP integrity probe failed during the run: error={self._probe_error!r}"
            ) from self._probe_error
        self._terminate_pending_operations()
        return DriverRunSummary(
            tier_schedule=self.plan.as_mapping(),
            applied_config_versions=tuple(self._config_versions),
            stock_reads=tuple(self._stock_reads),
            probes=tuple(self._probes),
        )

    def stop_and_drain(self) -> DriverRunSummary:
        self.stop_new_requests()
        self.drain()
        return self.stop()

    def ledgers(self) -> Mapping[str, BusinessLedger]:
        """The trusted business ledgers keyed by ledger name."""

        return {"commerce": self.ledger}

    def baseline_facts(self) -> Mapping[str, object]:
        """Warmup-derived baseline facts for the health admission gate."""

        return {
            "tier": self.current_tier(),
            "config_version": self._config_versions[-1] if self._config_versions else None,
            "scoring_origin": self._scoring_origin,
            "pool_size": self.config.pool_size,
        }

    # -- capability control surface ---------------------------------------

    @property
    def scoring_origin(self) -> float:
        return self._scoring_origin

    def apply_tier(self, tier_name: str) -> None:
        tier = self.plan.tier_by_name(tier_name)
        with self._tier_lock:
            self._current_tier = tier
        self.evidence.append({"kind": "traffic_tier", "tier": tier_name, "at": self.clock.monotonic()})

    def current_tier(self) -> str:
        with self._tier_lock:
            return self._current_tier.name

    def applied_config_version(self) -> int:
        return self._poller.applied_version()

    def telemetry(self) -> Mapping[str, object]:
        return {
            "tier": self.current_tier(),
            "config_version": self._config_versions[-1],
            "queue_depth": self._work_queue.qsize(),
            "busy_workers": sum(self._worker_busy),
            "pool_size": self.config.pool_size,
        }

    # -- scheduling --------------------------------------------------------

    def _arrival_window(self) -> tuple[float, float]:
        """Business arrivals live inside the scoring window: they start at the
        warmup barrier (warmup arrivals stay out of
        scoring) and stop at the compressed input stop, both measured from the
        scoring start like every other engine boundary."""
        start = self._scoring_origin + self._warmup_seconds
        return start, start + self._input_stop_seconds

    def _trade_scheduler_loop(self) -> None:
        interval = 1.0 / self.plan.tiers[0].place_order_qps
        next_at, input_stop = self._arrival_window()
        while not self._stop.is_set():
            if not self.clock.wait_until(next_at, self._stop):
                return
            if self._stop.is_set() or self._input_stop.is_set() or next_at >= input_stop:
                return
            self._plan_trade_arrival(next_at, self._tier_at(next_at))
            interval = 1.0 / self._tier_at(next_at).place_order_qps
            next_at += interval

    def _stock_scheduler_loop(self) -> None:
        interval = 1.0 / self.plan.tiers[0].stock_read_qps
        next_at, input_stop = self._arrival_window()
        while not self._stop.is_set():
            if not self.clock.wait_until(next_at, self._stop):
                return
            if self._stop.is_set() or self._input_stop.is_set() or next_at >= input_stop:
                return
            self._plan_stock_read(next_at, self._tier_at(next_at))
            interval = 1.0 / self._tier_at(next_at).stock_read_qps
            next_at += interval

    def _tier_at(self, absolute_monotonic: float) -> TrafficTier:
        with self._tier_lock:
            return self._current_tier

    def _plan_trade_arrival(self, scheduled_at: float, tier: TrafficTier) -> None:
        with self._sequence_lock:
            self._sequence += 1
            sequence = self._sequence
        if sequence % 5 < 4:
            sku = PROMO_SKUS[sequence % len(PROMO_SKUS)]
        else:
            sku = f"SKU-{self._rng.randrange(20):04d}"
        qty = self._rng.randint(1, 5)
        amount = price_cents_for_sku(sku) * qty
        order_id = f"{self.run_id}-o{sequence:08d}"
        place_payload = PlaceOrderPayload(
            order_id=order_id, sku=sku, qty=qty, amount_cents=amount, created_at=scheduled_at,
        )
        pay_deadline = scheduled_at + self.config.pay_lag_seconds + tier.op_deadline_ms / 1000.0
        pay_item = _WorkItem(
            op_id=f"{order_id}:pay",
            flow_id=OpKind.PAY_ORDER.value,
            place_payload=None,
            pay_payload=PayOrderPayload(order_id=order_id, amount_cents=amount, paid_at=scheduled_at),
            sku=sku,
            scheduled_at=scheduled_at + self.config.pay_lag_seconds,
            deadline_at=pay_deadline,
        )
        self.ledger.plan(
            order_id, OpKind.PLACE_ORDER.value, scheduled_at, scheduled_at + tier.op_deadline_ms / 1000.0,
            {"sku": sku, "qty": qty, "amount_cents": amount},
        )
        self.ledger.plan(
            f"{order_id}:pay", OpKind.PAY_ORDER.value, pay_item.scheduled_at, pay_deadline,
            {"order_id": order_id, "amount_cents": amount},
        )
        self._pending_pay[order_id] = pay_item
        self._work_queue.put(_WorkItem(
            op_id=order_id,
            flow_id=OpKind.PLACE_ORDER.value,
            place_payload=place_payload,
            pay_payload=None,
            sku=sku,
            scheduled_at=scheduled_at,
            deadline_at=scheduled_at + tier.op_deadline_ms / 1000.0,
        ))

    def _plan_stock_read(self, scheduled_at: float, tier: TrafficTier) -> None:
        sku = PROMO_SKUS[self._rng.randrange(len(PROMO_SKUS))]
        self._work_queue.put(_WorkItem(
            op_id=f"{self.run_id}-s{sequence_label(scheduled_at)}",
            flow_id="stock_read",
            place_payload=None,
            pay_payload=None,
            sku=sku,
            scheduled_at=scheduled_at,
            deadline_at=scheduled_at + tier.op_deadline_ms / 1000.0,
        ))

    # -- execution ---------------------------------------------------------

    def _worker_loop(self, index: int) -> None:
        while not self._stop.is_set():
            try:
                item = self._work_queue.get(timeout=0.05)
            except queue.Empty:
                continue
            self._worker_busy[index] = 1
            try:
                self._execute(item)
            finally:
                self._worker_busy[index] = 0
                self._work_queue.task_done()

    def _execute(self, item: _WorkItem) -> None:
        if item.flow_id == "stock_read":
            self._execute_stock_read(item)
            return
        self._execute_with_retries(item)

    def _execute_with_retries(self, item: _WorkItem) -> None:
        while True:
            policy = self._poller.active()
            now = self.clock.monotonic()
            if now >= item.deadline_at:
                self.ledger.terminal(item.op_id, AttemptOutcome.TIMEOUT, now, "business_deadline_exceeded")
                if item.flow_id == OpKind.PLACE_ORDER.value:
                    self._on_place_terminal(item.op_id, AttemptOutcome.TIMEOUT)
                return
            started = self.clock.monotonic()
            try:
                connection = self._thread_connection()
                if item.flow_id == OpKind.PLACE_ORDER.value:
                    payload = item.place_payload
                    if self._new_version_active():
                        payload = client.new_version_place_payload(payload)
                    result = client.place_order(connection, payload, policy)
                else:
                    result = client.pay_order(connection, item.pay_payload, policy)
            except psycopg2.Error as exc:
                outcome = AttemptOutcome(client.classify_psycopg_error(exc))
                self.ledger.attempt(
                    item.op_id, started, self.clock.monotonic(), outcome,
                    f"pgcode={getattr(exc, 'pgcode', None)!r}",
                )
            except FlowFailure as exc:
                self.ledger.attempt(
                    item.op_id, started, self.clock.monotonic(), AttemptOutcome.ERROR, str(exc)
                )
            else:
                outcome = (
                    AttemptOutcome.BUSINESS_REJECTED
                    if result is AttemptKind.BUSINESS_REJECTED
                    else AttemptOutcome.COMMITTED
                )
                self.ledger.attempt(item.op_id, started, self.clock.monotonic(), outcome, result.value)
                self.ledger.terminal(item.op_id, outcome, self.clock.monotonic(), result.value)
                if item.flow_id == OpKind.PLACE_ORDER.value:
                    self._on_place_terminal(item.op_id, outcome)
                return
            attempts = self.ledger.attempt_count(item.op_id)
            retryable = self.ledger.retryable(item.op_id)
            deadline_passed = self.clock.monotonic() >= item.deadline_at
            if deadline_passed or not retryable or attempts > policy.max_retries:
                final = self.ledger.last_attempt_outcome(item.op_id) if attempts else AttemptOutcome.TIMEOUT
                self.ledger.terminal(item.op_id, final, self.clock.monotonic(), "retry_budget_exhausted_or_deadline")
                if item.flow_id == OpKind.PLACE_ORDER.value:
                    self._on_place_terminal(item.op_id, final)
                return
            backoff = (policy.retry_backoff_ms + self._jitter(policy)) / 1000.0
            if backoff > 0:
                self.clock.wait_until(self.clock.monotonic() + backoff, self._stop)

    def _on_place_terminal(self, order_id: str, outcome: AttemptOutcome) -> None:
        """Releases the paired payment once the checkout reached a terminal state."""

        pay_item = self._pending_pay.pop(order_id, None)
        if pay_item is None:
            return
        if outcome is AttemptOutcome.COMMITTED:
            self._work_queue.put(pay_item)
        else:
            self.ledger.terminal(
                pay_item.op_id, AttemptOutcome.BUSINESS_REJECTED, self.clock.monotonic(), "order_was_not_placed"
            )

    def _jitter(self, policy: ClientConfig) -> int:
        if policy.retry_jitter_ms == 0:
            return 0
        return self._rng.randrange(0, policy.retry_jitter_ms + 1)

    def _execute_stock_read(self, item: _WorkItem) -> None:
        started = self.clock.monotonic()
        try:
            connection = self._thread_connection()
            client.stock_read(connection, item.sku, self._poller.active())
        except psycopg2.Error:
            ended = self.clock.monotonic()
            self._stock_reads.append(StockReadObservation(item.scheduled_at, ended, (ended - started) * 1000, "failed"))
            return
        ended = self.clock.monotonic()
        outcome = "ok" if ended <= item.deadline_at else "late"
        self._stock_reads.append(StockReadObservation(item.scheduled_at, ended, (ended - started) * 1000, outcome))

    # -- connections -------------------------------------------------------

    def _thread_connection(self) -> DBConnection:
        connection = getattr(self._thread_local, "connection", None)
        created = getattr(self._thread_local, "created_at", None)
        now = self.clock.monotonic()
        if connection is not None and created is not None and now - created > self.config.connection_max_lifetime_seconds:
            connection.close()
            self._thread_local.connection = None
            self._thread_local.new_version_cache = None
            connection = None
        if connection is None:
            connection = self.source.connection("shop_app")
            self._thread_local.connection = connection
            self._thread_local.created_at = now
            self._thread_local.new_version_cache = None
        return connection

    def _new_version_active(self) -> bool:
        if self._new_version_column is None:
            return False
        cache = getattr(self._thread_local, "new_version_cache", None)
        now = self.clock.monotonic()
        if cache is not None and now - cache[1] < NEW_VERSION_CHECK_INTERVAL_SECONDS:
            return cache[0]
        active = column_exists(self._thread_connection(), "shop.orders", self._new_version_column)
        self._thread_local.new_version_cache = (active, now)
        return active

    # -- probe and close ---------------------------------------------------

    def _probe_loop(self) -> None:
        connection = self.source.connection("shop_auditor")
        try:
            while not self._stop.is_set():
                with connection.cursor() as cursor:
                    cursor.execute(PAID_WITHOUT_PAYMENT_PROBE_SQL)
                    paid_without_payment = int(cursor.fetchone()[0])
                    cursor.execute(NEGATIVE_INVENTORY_PROBE_SQL)
                    negative_inventory = int(cursor.fetchone()[0])
                connection.commit()
                self._probes.append(ProbeObservation(self.clock.monotonic(), paid_without_payment, negative_inventory))
                self.clock.wait_until(self.clock.monotonic() + self.config.integrity_probe_interval_seconds, self._stop)
        except BaseException as exc:  # noqa: BLE001 - surfaced through stop()
            self._probe_error = exc
            self._stop.set()
        finally:
            connection.close()

    def _terminate_pending_operations(self) -> None:
        now = self.clock.monotonic()
        for op_id in self.ledger.unfinished_op_ids():
            self.ledger.terminal(op_id, AttemptOutcome.PENDING_AT_CLOSE, now, "run_closed_before_terminal_outcome")


def sequence_label(scheduled_at: float) -> str:
    return f"{scheduled_at:.6f}"
