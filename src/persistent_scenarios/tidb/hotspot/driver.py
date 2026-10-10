"""Workload driver for ``tidb_oltp_hotspot_resilience``.

The driver is the production client system: a bounded worker pool of real
client connections executing externally scheduled logical trades (open loop),
a stock-read scheduler, a control-table poller adopting the published client
policy, and an integrity probe. Event capabilities drive it through
``apply_tier``; published configuration is adopted through the poller.
Nothing here knows event IDs.

Scheduling model: one trade scheduler plans paired checkout+payment logical
transactions (payment fires after its checkout commits; a rejected or lost
checkout terminates its payment as a business loss), and one read scheduler
plans stock reads. Every business identity is planned exactly once in the
core trusted ledger; client retries merge into the same identity and inherit
the original deadline. An unknown commit outcome is resolved through the
business idempotency key before any terminal decision.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import queue
import random
import threading
import time
from typing import Any, Mapping

from src.persistent_scenarios.runtime.clock import Clock
from src.persistent_scenarios.runtime.ledger import (
    AttemptOutcome,
    LedgerTerminal,
    TransactionAttempt,
    TrustedLedger,
)

from .business import (
    BusinessRejected,
    PayOrderPayload,
    PlaceOrderPayload,
    classify_pymysql_error,
    ledger_place_detail,
    pay_order,
    place_order,
    reconcile_order_committed,
    stock_read,
)
from .control import (
    _ORDER_ID_SUFFIX_LENGTH,
    ORDER_ID_COLUMN_LENGTH,
    ClientPolicy,
    validate_policy_transition,
)
from .schema import FLASH_SALE_SKU, price_cents_for_sku


@dataclass(frozen=True, slots=True)
class TrafficTier:
    name: str
    place_qps: float
    stock_read_qps: float
    promo_skus: tuple[str, ...]
    flash_sku: str | None = None
    flash_share: float = 0.0

    def __post_init__(self) -> None:
        if self.place_qps <= 0 or self.stock_read_qps <= 0:
            raise ValueError(
                f"traffic tier rates must be positive: name={self.name!r}, "
                f"place_qps={self.place_qps}, stock_read_qps={self.stock_read_qps}"
            )
        if not 0 <= self.flash_share <= 1:
            raise ValueError(f"flash_share must be in [0,1]: name={self.name!r}, value={self.flash_share}")
        if (self.flash_sku is None) != (self.flash_share == 0.0):
            raise ValueError(
                f"flash_sku and positive flash_share must be set together: name={self.name!r}"
            )


@dataclass(frozen=True, slots=True)
class TrafficPlan:
    tiers: tuple[TrafficTier, ...]

    def __post_init__(self) -> None:
        if not self.tiers:
            raise ValueError("traffic plan requires at least one tier")
        names = [tier.name for tier in self.tiers]
        if len(names) != len(set(names)):
            raise ValueError(f"traffic tier names must be unique: names={names!r}")

    def tier_by_name(self, name: str) -> TrafficTier:
        for tier in self.tiers:
            if tier.name == name:
                return tier
        raise ValueError(f"unknown traffic tier: name={name!r}, known={tuple(tier.name for tier in self.tiers)!r}")

    def as_mapping(self) -> Mapping[str, float]:
        return {tier.name: tier.place_qps for tier in self.tiers}


@dataclass(frozen=True, slots=True)
class DriverConfig:
    pool_size: int
    deadline_seconds: float
    control_poll_seconds: float = 2.0
    pay_lag_seconds: float = 0.5
    integrity_probe_interval_seconds: float = 30.0
    queue_capacity: int = 512
    seed: int = 20260918

    def __post_init__(self) -> None:
        if self.pool_size < 1:
            raise ValueError(f"pool_size must be at least 1: value={self.pool_size}")
        if self.deadline_seconds <= 0:
            raise ValueError(f"deadline_seconds must be positive: value={self.deadline_seconds}")
        for name in ("control_poll_seconds", "integrity_probe_interval_seconds"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive: value={getattr(self, name)}")
        if self.pay_lag_seconds < 0:
            raise ValueError(f"pay_lag_seconds must be non-negative: value={self.pay_lag_seconds}")
        if self.queue_capacity < 1:
            raise ValueError(f"queue_capacity must be at least 1: value={self.queue_capacity}")


@dataclass(frozen=True, slots=True)
class _WorkItem:
    op_id: str
    flow_id: str
    place_payload: PlaceOrderPayload | None
    pay_payload: PayOrderPayload | None
    sku: str
    scheduled_at: float
    deadline_at: float


class ClientConfigPoller:
    """Adopts the published client policy; rejects unsafe/stale publications."""

    def __init__(self, connection_source: Any, clock: Clock, poll_seconds: float) -> None:
        from .control import READ_CLIENT_POLICY_SQL

        self._source = connection_source
        self._clock = clock
        self._poll_seconds = poll_seconds
        self._read_sql = READ_CLIENT_POLICY_SQL
        self._lock = threading.Lock()
        self._policy: ClientPolicy | None = None
        self._applied_version = -1
        self._applied_versions: tuple[int, ...] = ()
        self._rejected: tuple[Mapping[str, str], ...] = ()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        policy = self._read_once()
        with self._lock:
            self._policy = policy
            self._applied_version = policy.config_version
            self._applied_versions = (policy.config_version,)
        self._thread = threading.Thread(target=self._loop, name="tidb5-oltp-client-config-poller", daemon=True)
        self._thread.start()

    def _read_once(self) -> ClientPolicy:
        connection = self._source.connect_control()
        try:
            with connection.cursor() as cursor:
                cursor.execute(self._read_sql)
                row = cursor.fetchone()
            connection.commit()
        finally:
            connection.close()
        if row is None:
            raise RuntimeError("ops.client_config has no policy row for id=1")
        return ClientPolicy.from_row(dict(zip(
            ("config_version", "request_timeout_ms", "max_retries", "retry_backoff_ms",
             "retry_jitter_ms", "max_connection_lifetime_seconds", "connect_bias",
             "lock_wait_timeout_seconds", "order_id_prefix", "settlement_paused"),
            row,
        )))

    def _loop(self) -> None:
        while not self._stop.wait(self._poll_seconds):
            try:
                candidate = self._read_once()
            except Exception:  # noqa: BLE001 - control read retries next cycle
                continue
            with self._lock:
                current = self._policy
                if current is not None and candidate.config_version <= current.config_version:
                    continue
            try:
                validate_policy_transition(current, candidate)
            except ValueError as exc:
                self._rejected = self._rejected + ({
                    "published_version": str(candidate.config_version),
                    "reason": str(exc),
                },)
                continue
            self._source.apply_policy(candidate)
            with self._lock:
                self._policy = candidate
                self._applied_version = candidate.config_version
                self._applied_versions = self._applied_versions + (candidate.config_version,)

    def active(self) -> ClientPolicy:
        with self._lock:
            if self._policy is None:
                raise RuntimeError("client config poller has not started")
            return self._policy

    def applied_version(self) -> int:
        with self._lock:
            return self._applied_version

    def applied_versions(self) -> tuple[int, ...]:
        with self._lock:
            return self._applied_versions

    def rejected_publications(self) -> tuple[Mapping[str, str], ...]:
        with self._lock:
            return self._rejected

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)


class HotspotWorkloadDriver:
    """Runs the externally planned trade workload against the TiDB shop."""

    def __init__(
        self,
        *,
        service_id: str,
        ledger: TrustedLedger,
        clock: Clock,
        connection_source: Any,
        plan: TrafficPlan,
        config: DriverConfig,
        run_id: str,
        scoring_origin: float,
        input_stop_seconds: float,
        normal_sku_count: int,
    ) -> None:
        if input_stop_seconds <= 0:
            raise ValueError(f"input_stop_seconds must be positive: value={input_stop_seconds}")
        self.service_id = service_id
        self.ledger = ledger
        self.clock = clock
        self.source = connection_source
        self.plan = plan
        self.config = config
        self.run_id = run_id
        self._scoring_origin = scoring_origin
        self._input_stop_seconds = input_stop_seconds
        self._input_stop = threading.Event()
        self._stop = threading.Event()
        self._poller = ClientConfigPoller(connection_source, clock, config.control_poll_seconds)
        self._work_queue: queue.Queue[_WorkItem] = queue.Queue(maxsize=config.queue_capacity)
        self._pending_pay: dict[str, _WorkItem] = {}
        self._threads: list[threading.Thread] = []
        self._sequence = 0
        self._sequence_lock = threading.Lock()
        self._rng = random.Random(config.seed)
        self._tier_lock = threading.Lock()
        self._current_tier = plan.tiers[0]
        self._tier_history: tuple[Mapping[str, Any], ...] = ()
        self._stock_reads: list[Mapping[str, Any]] = []
        self._probes: list[Mapping[str, Any]] = []
        self._attempt_counts: dict[str, int] = {}
        self._attempt_lock = threading.Lock()
        self._open: dict[str, _WorkItem] = {}
        self._open_lock = threading.Lock()
        self._thread_local = threading.local()
        self._probe_error: BaseException | None = None
        self._worker_error: BaseException | None = None
        self._finished = False
        self._normal_sku_count = normal_sku_count
        self._executor = ThreadPoolExecutor(
            max_workers=config.pool_size, thread_name_prefix=f"tidb5-oltp-{service_id}"
        )

    # -- PersistentWorkloadRuntime protocol ----------------------------------

    def start(self) -> None:
        if self._threads:
            raise RuntimeError(f"hotspot workload driver cannot start twice: run_id={self.run_id!r}")
        self._poller.start()
        for index in range(self.config.pool_size):
            self._executor.submit(self._worker_loop, index)
        for name, target in (
            ("trade", self._trade_scheduler_loop),
            ("stock_read", self._stock_scheduler_loop),
            ("integrity_probe", self._probe_loop),
        ):
            thread = threading.Thread(target=target, name=f"tidb5-oltp-{name}", daemon=True)
            thread.start()
            self._threads.append(thread)

    def wait_for_warmup(self) -> float:
        if not self.clock.wait_until(self._scoring_origin, self._stop):
            raise RuntimeError(f"hotspot workload driver stopped before warmup: run_id={self.run_id!r}")
        return self._scoring_origin

    def stop_new_requests(self) -> None:
        self._input_stop.set()

    def drain(self) -> None:
        deadline = time.monotonic() + _DRAIN_GRACE_SECONDS
        while time.monotonic() < deadline:
            with self._open_lock:
                open_count = len(self._open)
            if self._work_queue.empty() and open_count == 0:
                return
            time.sleep(0.02)

    def stop(self) -> Mapping[str, Any]:
        if self._finished:
            raise RuntimeError(f"hotspot workload driver already stopped: run_id={self.run_id!r}")
        self._finished = True
        # Stop the arrivals first and let the workers finish (or deadline-
        # terminate) everything already queued; a scheduler blocked on a full
        # queue can only exit once the queue drains, so _stop must come last.
        self._input_stop.set()
        self.drain()
        self._stop.set()
        for thread in self._threads:
            thread.join(timeout=30)
            if thread.is_alive():
                raise RuntimeError(
                    f"hotspot workload driver thread did not stop: run_id={self.run_id!r}, "
                    f"thread={thread.name!r}"
                )
        self._poller.stop()
        self._executor.shutdown(wait=True)
        if self._probe_error is not None:
            raise RuntimeError(
                f"hotspot workload integrity probe failed: run_id={self.run_id!r}"
            ) from self._probe_error
        if self._worker_error is not None:
            raise RuntimeError(
                f"hotspot workload worker failed: run_id={self.run_id!r}, op_in_flight_finalized_as_open_loss"
            ) from self._worker_error
        self._terminate_pending()
        return {
            "tier_history": self._tier_history,
            "applied_config_versions": self._poller.applied_versions(),
            "rejected_publications": self._poller.rejected_publications(),
            "stock_reads": tuple(self._stock_reads),
            "probes": tuple(self._probes),
        }

    def ledgers(self) -> Mapping[str, TrustedLedger]:
        return {"trade": self.ledger}

    def baseline_facts(self) -> Mapping[str, object]:
        return {
            "tier": self.current_tier(),
            "config_version": self._poller.applied_version(),
            "scoring_origin": self._scoring_origin,
            "pool_size": self.config.pool_size,
        }

    # -- capability control surface ------------------------------------------

    def apply_tier(self, tier_name: str) -> None:
        tier = self.plan.tier_by_name(tier_name)
        with self._tier_lock:
            self._current_tier = tier
        self._tier_history = self._tier_history + (
            {"tier": tier_name, "at_monotonic": self.clock.monotonic()},
        )

    def current_tier(self) -> str:
        with self._tier_lock:
            return self._current_tier.name

    def applied_config_version(self) -> int:
        return self._poller.applied_version()

    def rejected_publications(self) -> tuple[Mapping[str, str], ...]:
        return self._poller.rejected_publications()

    def backend_connection_counts(self) -> Mapping[str, int]:
        return self.source.connection_counts()

    # -- scheduling ------------------------------------------------------------

    def _trade_scheduler_loop(self) -> None:
        tier = self.plan.tiers[0]
        next_at = self._scoring_origin
        input_stop = self._scoring_origin + self._input_stop_seconds
        while not self._stop.is_set():
            if not self.clock.wait_until(next_at, self._stop):
                return
            if self._stop.is_set() or self._input_stop.is_set() or next_at >= input_stop:
                return
            self._plan_trade_arrival(next_at, self._current_tier_snapshot())
            next_at += 1.0 / self._current_tier_snapshot().place_qps

    def _stock_scheduler_loop(self) -> None:
        next_at = self._scoring_origin
        input_stop = self._scoring_origin + self._input_stop_seconds
        while not self._stop.is_set():
            if not self.clock.wait_until(next_at, self._stop):
                return
            if self._stop.is_set() or self._input_stop.is_set() or next_at >= input_stop:
                return
            self._plan_stock_read(next_at)
            next_at += 1.0 / self._current_tier_snapshot().stock_read_qps

    def _current_tier_snapshot(self) -> TrafficTier:
        with self._tier_lock:
            return self._current_tier

    def _next_sku(self, tier: TrafficTier) -> str:
        with self._sequence_lock:
            sequence = self._sequence + 1
        if sequence % 5 < 4 and tier.promo_skus:
            if tier.flash_sku is not None and self._rng.random() < tier.flash_share:
                return tier.flash_sku
            return tier.promo_skus[sequence % len(tier.promo_skus)]
        return f"SKU-{self._rng.randrange(self._normal_sku_count):04d}"

    def _plan_trade_arrival(self, scheduled_at: float, tier: TrafficTier) -> None:
        with self._sequence_lock:
            self._sequence += 1
            sequence = self._sequence
        sku = self._next_sku(tier)
        qty = self._rng.randint(1, 5)
        amount = price_cents_for_sku(sku) * qty
        order_id = order_identifier(self._poller.active(), self.run_id, sequence)
        place_payload = PlaceOrderPayload(
            order_id=order_id, sku=sku, qty=qty, amount_cents=amount,
            created_at_ms=int(scheduled_at * 1000),
        )
        pay_item = _WorkItem(
            op_id=f"{order_id}:pay",
            flow_id="pay_order",
            place_payload=None,
            pay_payload=PayOrderPayload(order_id=order_id, amount_cents=amount,
                                        paid_at_ms=int((scheduled_at + self.config.pay_lag_seconds) * 1000)),
            sku=sku,
            scheduled_at=scheduled_at + self.config.pay_lag_seconds,
            deadline_at=scheduled_at + self.config.pay_lag_seconds + self.config.deadline_seconds,
        )
        self._plan_item(order_id, "place_order", scheduled_at, {"sku": sku, "qty": qty, "amount_cents": amount})
        self._plan_item(pay_item.op_id, pay_item.flow_id, pay_item.scheduled_at,
                        {"order_id": order_id, "amount_cents": amount})
        self._pending_pay[order_id] = pay_item
        self._enqueue_trade(_WorkItem(
            op_id=order_id, flow_id="place_order", place_payload=place_payload, pay_payload=None,
            sku=sku, scheduled_at=scheduled_at, deadline_at=scheduled_at + self.config.deadline_seconds,
        ))

    def _plan_stock_read(self, scheduled_at: float) -> None:
        with self._sequence_lock:
            self._sequence += 1
            sequence = self._sequence
        with self._tier_lock:
            tier = self._current_tier
        sku = tier.promo_skus[sequence % len(tier.promo_skus)] if tier.promo_skus else (
            f"SKU-{self._rng.randrange(self._normal_sku_count):04d}"
        )
        self._enqueue_observation(_WorkItem(
            op_id=f"{self.run_id}-s{sequence:08d}", flow_id="stock_read", place_payload=None,
            pay_payload=None, sku=sku, scheduled_at=scheduled_at,
            deadline_at=scheduled_at + self.config.deadline_seconds,
        ))

    def _plan_item(self, op_id: str, flow_id: str, planned_at: float, payload: Mapping[str, Any]) -> None:
        with self._open_lock:
            if op_id in self._open:
                raise RuntimeError(f"logical transaction planned twice: op_id={op_id!r}")
        self.ledger.append_planned_transaction(
            business_id=op_id,
            service_id=self.service_id,
            tx_kind=flow_id,
            planned_at_monotonic=planned_at,
            deadline_at_monotonic=planned_at + self.config.deadline_seconds,
        )
        with self._open_lock:
            self._open[op_id] = _PLANNED  # sentinel until the item is enqueued

    # -- execution -------------------------------------------------------------

    def _enqueue_trade(self, item: _WorkItem) -> None:
        """Queue a ledger-planned business transaction.

        The open entry survives until a terminal decision; if the queue
        rejects the item after stop, stop() finalizes it as an explicit
        outstanding loss instead of shrinking the ledger denominator."""
        with self._open_lock:
            self._open[item.op_id] = item
        self._put(item)

    def _enqueue_observation(self, item: _WorkItem) -> None:
        """Queue a stock read. Observations carry no ledger identity: they are
        never planned and never receive terminals, so they must not enter the
        open-transaction view that drain() waits on and stop() finalizes."""
        self._put(item)

    def _put(self, item: _WorkItem) -> None:
        while True:
            try:
                self._work_queue.put(item, timeout=0.25)
                return
            except queue.Full:
                if self._stop.is_set():
                    # Workers are gone, the item can never execute. A traded
                    # item keeps its open entry and stop() finalizes it as an
                    # explicit outstanding loss; observations are dropped.
                    return

    def _worker_loop(self, index: int) -> None:
        while not self._stop.is_set():
            try:
                item = self._work_queue.get(timeout=0.05)
            except queue.Empty:
                continue
            try:
                if item.flow_id == "stock_read":
                    self._execute_stock_read(item)
                else:
                    self._execute_trade(item)
            except Exception as exc:  # noqa: BLE001 - surfaced through stop()
                if self._worker_error is None:
                    self._worker_error = exc
                self._stop.set()
                return
            finally:
                self._work_queue.task_done()

    def _thread_connection(self) -> Any:
        policy = self._poller.active()
        connection = getattr(self._thread_local, "connection", None)
        created_at = getattr(self._thread_local, "created_at", 0.0)
        policy_version = getattr(self._thread_local, "policy_version", -1)
        now = self.clock.monotonic()
        lifetime = policy.max_connection_lifetime_seconds
        if (
            connection is None
            or policy_version != policy.config_version
            or now - created_at > lifetime
        ):
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass
            connection = self.source.connect(policy)
            self._thread_local.connection = connection
            self._thread_local.created_at = now
            self._thread_local.policy_version = policy.config_version
        return connection

    def _execute_trade(self, item: _WorkItem) -> None:
        while True:
            now = self.clock.monotonic()
            if now >= item.deadline_at:
                self._record_terminal(item, LedgerTerminal.INCOMPLETE_TIMEOUT, None, None)
                if item.flow_id == "place_order":
                    self._release_pending_pay(item.op_id, committed=False)
                return
            policy = self._poller.active()
            started = self.clock.monotonic()
            outcome, ended, digest, detail = self._execute_attempt(item, policy)
            # Every attempt carries the business payload so the ledger alone
            # reconstructs conservation, including uncertain-commit attempts
            # whose terminal is resolved through the idempotency key.
            if item.flow_id == "place_order":
                detail = {**ledger_place_detail(item.place_payload), **detail}
            else:
                detail = {
                    "order_id": item.pay_payload.order_id,
                    "amount_cents": item.pay_payload.amount_cents,
                    **detail,
                }
            with self._attempt_lock:
                attempt_index = self._attempt_counts.get(item.op_id, 0)
                self._attempt_counts[item.op_id] = attempt_index + 1
            self.ledger.append_transaction_attempt(
                business_id=item.op_id,
                attempt=TransactionAttempt(
                    attempt_index=attempt_index,
                    started_at_monotonic=started,
                    ended_at_monotonic=ended,
                    outcome=outcome,
                    detail=detail,
                ),
            )
            if outcome is AttemptOutcome.COMMITTED:
                self._record_terminal(item, LedgerTerminal.COMPLETED, ended, digest)
                if item.flow_id == "place_order":
                    self._release_pending_pay(item.op_id, committed=True)
                return
            if detail.get("uncertain_commit"):
                resolved = self._reconcile(item)
                if resolved:
                    self._record_terminal(item, LedgerTerminal.COMPLETED, ended, self._digest_for(item))
                    if item.flow_id == "place_order":
                        self._release_pending_pay(item.op_id, committed=True)
                    return
            retryable = detail.get("retryable", False)
            attempts = self._attempt_counts.get(item.op_id, 0)
            if self.clock.monotonic() >= item.deadline_at:
                self._record_terminal(item, LedgerTerminal.INCOMPLETE_TIMEOUT, None, None)
                if item.flow_id == "place_order":
                    self._release_pending_pay(item.op_id, committed=False)
                return
            if not retryable or attempts > policy.max_retries:
                self._record_terminal(item, LedgerTerminal.INCOMPLETE_ERROR, None, None)
                if item.flow_id == "place_order":
                    self._release_pending_pay(item.op_id, committed=False)
                return
            backoff = (policy.retry_backoff_ms + self._rng.randrange(0, policy.retry_jitter_ms + 1)) / 1000.0
            if backoff > 0:
                self.clock.wait_until(self.clock.monotonic() + backoff, self._stop)

    def _execute_attempt(self, item: _WorkItem, policy: ClientPolicy) -> tuple[AttemptOutcome, float, str | None, dict]:
        connection = self._thread_connection()
        started = self.clock.monotonic()
        try:
            if item.flow_id == "place_order":
                digest = place_order(connection, item.place_payload)
                ended = self.clock.monotonic()
                return AttemptOutcome.COMMITTED, ended, digest, dict(ledger_place_detail(item.place_payload))
            digest = pay_order(connection, item.pay_payload)
            ended = self.clock.monotonic()
            return AttemptOutcome.COMMITTED, ended, digest, {"order_id": item.pay_payload.order_id}
        except BusinessRejected as exc:
            ended = self.clock.monotonic()
            self._drop_thread_connection()
            return AttemptOutcome.ABORTED, ended, None, {"error": str(exc), "retryable": False}
        except Exception as exc:  # pymysql errors and client-side read timeouts
            ended = self.clock.monotonic()
            outcome, retryable = classify_pymysql_error(exc)
            code = exc.args[0] if exc.args else type(exc).__name__
            # 1062 duplicate key on the idempotent INSERT means the earlier
            # uncertain attempt landed: resolve through the idempotency key.
            uncertain = outcome is AttemptOutcome.TIMED_OUT or code == 1062
            if not retryable or uncertain:
                self._drop_thread_connection()
            return outcome, ended, None, {
                "error": str(code),
                "retryable": retryable,
                "uncertain_commit": uncertain,
            }

    def _reconcile(self, item: _WorkItem) -> bool:
        """Resolve an unknown commit outcome through the idempotency key.

        A transient probe failure (connection refused, read timeout) leaves the
        outcome unresolved: the trade retry loop keeps the transaction open
        until its deadline, so a broken probe neither strands the transaction
        nor kills the worker. Non-transient probe errors propagate."""
        self._drop_thread_connection()
        connection = None
        try:
            connection = self.source.connect_reconcile()
            key = item.place_payload.idempotency_key if item.place_payload is not None else item.pay_payload.order_id
            return reconcile_order_committed(connection, key)
        except Exception as exc:
            _outcome, retryable = classify_pymysql_error(exc)
            if not retryable:
                raise
            return False
        finally:
            if connection is not None:
                connection.close()

    def _drop_thread_connection(self) -> None:
        connection = getattr(self._thread_local, "connection", None)
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass
            self._thread_local.connection = None

    def _digest_for(self, item: _WorkItem) -> str:
        if item.flow_id == "place_order":
            payload = item.place_payload
            return f"order:{payload.order_id}:{payload.sku}:{payload.qty}:{payload.amount_cents}"
        payload = item.pay_payload
        return f"payment:{payload.order_id}:{payload.amount_cents}"

    def _release_pending_pay(self, order_id: str, committed: bool) -> None:
        pay_item = self._pending_pay.pop(order_id, None)
        if pay_item is None:
            return
        if committed:
            self._enqueue_trade(pay_item)
        else:
            self._record_terminal(pay_item, LedgerTerminal.INCOMPLETE_ERROR, None, None)

    def _record_terminal(
        self,
        item: _WorkItem,
        terminal: LedgerTerminal,
        completed_at: float | None,
        digest: str | None,
    ) -> None:
        with self._open_lock:
            still_open = self._open.pop(item.op_id, _MISSING)
        if still_open is _MISSING:
            raise RuntimeError(
                f"logical transaction reached a second terminal decision: op_id={item.op_id!r}"
            )
        self.ledger.append_transaction_terminal(
            business_id=item.op_id, terminal=terminal, completed_at_monotonic=completed_at, result_digest=digest,
        )

    def _execute_stock_read(self, item: _WorkItem) -> None:
        started = self.clock.monotonic()
        try:
            connection = self._thread_connection()
            stock_read(connection, item.sku)
        except Exception:  # noqa: BLE001 - observation only, never a business terminal
            ended = self.clock.monotonic()
            self._stock_reads.append({"sku": item.sku, "latency_ms": (ended - started) * 1000, "outcome": "failed"})
            return
        ended = self.clock.monotonic()
        self._stock_reads.append({
            "sku": item.sku,
            "latency_ms": (ended - started) * 1000,
            "outcome": "ok" if ended <= item.deadline_at else "late",
        })

    # -- probe and close ---------------------------------------------------------

    def _probe_loop(self) -> None:
        # The probe is trusted harness telemetry. The throttle window is
        # DESIGNED to produce transient connection losses on the store that
        # carries the hot regions, so the probe reconnects and continues; only
        # persistent failure (consecutive budget exhausted) stops the workload
        # and surfaces through stop().
        failures = 0
        while not self._stop.is_set():
            try:
                connection = self.source.connect_control()
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(PAID_WITHOUT_PAYMENT_PROBE_SQL)
                        paid_without_payment = int(cursor.fetchone()[0])
                        cursor.execute(_NEGATIVE_INVENTORY_SQL)
                        negative_inventory = int(cursor.fetchone()[0])
                    connection.commit()
                finally:
                    connection.close()
                self._probes.append({
                    "checked_at_monotonic": self.clock.monotonic(),
                    "paid_without_payment": paid_without_payment,
                    "negative_inventory": negative_inventory,
                })
                failures = 0
                self.clock.wait_until(self.clock.monotonic() + self.config.integrity_probe_interval_seconds, self._stop)
            except BaseException as exc:  # noqa: BLE001 - surfaced through stop() once the budget is exhausted
                failures += 1
                if failures >= _PROBE_FAILURE_BUDGET:
                    self._probe_error = exc
                    self._stop.set()
                else:
                    self.clock.wait_until(self.clock.monotonic() + 5.0, self._stop)

    def _terminate_pending(self) -> None:
        now = self.clock.monotonic()
        with self._open_lock:
            open_ids = sorted(self._open)
        for op_id in open_ids:
            self.ledger.append_transaction_terminal(
                business_id=op_id, terminal=LedgerTerminal.INCOMPLETE_OUTSTANDING,
                completed_at_monotonic=None, result_digest=None,
            )
        with self._open_lock:
            self._open.clear()
        _ = now


_DRAIN_GRACE_SECONDS = 30.0
# Consecutive integrity-probe failures tolerated across transient connection
# losses (a designed consequence of the throttle window) before the probe
# failure stops the workload.
_PROBE_FAILURE_BUDGET = 10

_PLANNED = object()
_MISSING = object()


def order_identifier(policy: ClientPolicy, run_id: str, sequence: int) -> str:
    """Identity of one planned trade: "<prefix>-o" plus the 8-digit sequence.

    The prefix is the deployment's order-id scope. A published
    ``ops.client_config.order_id_prefix`` replaces the deployment identifier
    with the documented column-width-compatible prefix (the application honors
    the control-table publication; no code change is involved). The fallback
    deployment identifier is truncated to the ``shop.orders.order_id`` column
    width (the documented "truncated deployment identifier" semantic), so a
    long run identity can never push generated ids past the column.
    """
    prefix = policy.order_id_prefix or run_id
    max_prefix_length = ORDER_ID_COLUMN_LENGTH - _ORDER_ID_SUFFIX_LENGTH
    if len(prefix) > max_prefix_length:
        prefix = prefix[:max_prefix_length]
    return f"{prefix}-o{sequence:08d}"

PAID_WITHOUT_PAYMENT_PROBE_SQL = (
    "SELECT COUNT(*) FROM shop.orders o LEFT JOIN shop.payments p ON p.order_id = o.order_id "
    "WHERE o.status = 'paid' AND p.order_id IS NULL"
)
_NEGATIVE_INVENTORY_SQL = "SELECT COUNT(*) FROM shop.inventory WHERE qty_available < 0"
