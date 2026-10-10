"""External trusted business ledger and conservation verification.

The ledger lives in the driver process (plus its hash-chained host file), so a
database-superuser Agent cannot rewrite business truth. One logical operation
identity spans every client retry attempt; retries never widen the SLO
denominator and never disappear from the ledger.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Sequence

from .ports import EvidenceLedgerFile


class OpKind(str, Enum):
    PLACE_ORDER = "place_order"
    PAY_ORDER = "pay_order"


class AttemptOutcome(str, Enum):
    COMMITTED = "committed"
    BUSINESS_REJECTED = "business_rejected"
    TIMEOUT = "timeout"
    CONNECTION_REFUSED = "connection_refused"
    ERROR = "error"
    PENDING_AT_CLOSE = "pending_at_close"


_RETRYABLE_OUTCOMES = frozenset({AttemptOutcome.TIMEOUT, AttemptOutcome.CONNECTION_REFUSED})


@dataclass(frozen=True, slots=True)
class AttemptRecord:
    index: int
    started_at: float
    ended_at: float
    outcome: AttemptOutcome
    detail: str


@dataclass(frozen=True, slots=True)
class LogicalOp:
    op_id: str
    flow_id: str
    scheduled_at: float
    deadline_at: float
    payload: Mapping[str, object]
    attempts: tuple[AttemptRecord, ...]
    terminal: AttemptRecord

    @property
    def good(self) -> bool:
        return self.terminal.outcome is AttemptOutcome.COMMITTED and self.terminal.ended_at <= self.deadline_at


def good_fraction(ops: Sequence[LogicalOp], flow_ids: Sequence[str]) -> float:
    flows = set(flow_ids)
    selected = [op for op in ops if op.flow_id in flows]
    if not selected:
        raise ValueError(
            "good_fraction needs at least one ledger operation: "
            f"flow_ids={tuple(flow_ids)!r}, ledger_flows={sorted({op.flow_id for op in ops})!r}"
        )
    return sum(1 for op in selected if op.good) / len(selected)


@dataclass(frozen=True, slots=True)
class _OpState:
    op_id: str
    flow_id: str
    scheduled_at: float
    deadline_at: float
    payload: Mapping[str, object]
    attempts: tuple[AttemptRecord, ...] = ()
    terminal: AttemptRecord | None = None

    def frozen(self) -> LogicalOp:
        if self.terminal is None:
            raise ValueError(f"Logical operation has no terminal outcome yet: op_id={self.op_id!r}")
        return LogicalOp(
            self.op_id, self.flow_id, self.scheduled_at, self.deadline_at, self.payload,
            self.attempts, self.terminal,
        )


class BusinessLedger:
    """Append-only ledger of planned logical operations, attempts and terminals."""

    def __init__(self, evidence: EvidenceLedgerFile) -> None:
        self._evidence = evidence
        self._lock = threading.Lock()
        self._states: dict[str, _OpState] = {}
        self._order: list[str] = []

    def ops(self) -> tuple[LogicalOp, ...]:
        with self._lock:
            return tuple(self._states[op_id].frozen() for op_id in self._order if self._states[op_id].terminal is not None)

    def plan(self, op_id: str, flow_id: str, scheduled_at: float, deadline_at: float, payload: Mapping[str, object]) -> None:
        with self._lock:
            if op_id in self._states:
                raise ValueError(f"Logical operation planned twice: op_id={op_id!r}")
            if deadline_at <= scheduled_at:
                raise ValueError(
                    f"Logical operation deadline must follow its schedule: op_id={op_id!r}, "
                    f"scheduled_at={scheduled_at}, deadline_at={deadline_at}"
                )
            self._states[op_id] = _OpState(op_id, flow_id, scheduled_at, deadline_at, dict(payload))
            self._order.append(op_id)
        self._evidence.append({
            "kind": "plan",
            "op_id": op_id,
            "flow_id": flow_id,
            "scheduled_at": scheduled_at,
            "deadline_at": deadline_at,
            "payload": dict(payload),
        })

    def attempt(self, op_id: str, started_at: float, ended_at: float, outcome: AttemptOutcome, detail: str) -> None:
        with self._lock:
            state = self._require(op_id)
            if state.terminal is not None:
                raise ValueError(
                    f"Attempt recorded after terminal outcome: op_id={op_id!r}, terminal={state.terminal!r}"
                )
            if outcome is AttemptOutcome.PENDING_AT_CLOSE:
                raise ValueError(
                    f"pending_at_close is a terminal outcome, not an attempt outcome: op_id={op_id!r}"
                )
            record = AttemptRecord(len(state.attempts), started_at, ended_at, outcome, detail)
            self._states[op_id] = _OpState(
                state.op_id, state.flow_id, state.scheduled_at, state.deadline_at, state.payload,
                (*state.attempts, record), None,
            )
            attempt_number = len(state.attempts) + 1
        self._evidence.append({
            "kind": "attempt",
            "op_id": op_id,
            "attempt": attempt_number,
            "started_at": started_at,
            "ended_at": ended_at,
            "outcome": outcome.value,
            "detail": detail,
        })

    def terminal(self, op_id: str, outcome: AttemptOutcome, ended_at: float, detail: str) -> None:
        with self._lock:
            state = self._require(op_id)
            if state.terminal is not None:
                raise ValueError(
                    f"Logical operation already has a terminal outcome: op_id={op_id!r}, "
                    f"terminal={state.terminal!r}, rejected_outcome={outcome!r}"
                )
            if outcome is AttemptOutcome.PENDING_AT_CLOSE and state.attempts:
                last = state.attempts[-1]
                if last.outcome not in _RETRYABLE_OUTCOMES:
                    raise ValueError(
                        f"pending_at_close recorded over a non-retryable attempt: op_id={op_id!r}, last={last!r}"
                    )
            self._states[op_id] = _OpState(
                state.op_id, state.flow_id, state.scheduled_at, state.deadline_at, state.payload,
                state.attempts,
                AttemptRecord(len(state.attempts), state.scheduled_at, ended_at, outcome, detail),
            )
        self._evidence.append({
            "kind": "terminal",
            "op_id": op_id,
            "outcome": outcome.value,
            "ended_at": ended_at,
            "detail": detail,
        })

    def retryable(self, op_id: str) -> bool:
        with self._lock:
            state = self._require(op_id)
            if state.terminal is not None:
                return False
            if state.attempts:
                return state.attempts[-1].outcome in _RETRYABLE_OUTCOMES
            return True

    def attempt_count(self, op_id: str) -> int:
        with self._lock:
            return len(self._require(op_id).attempts)

    def last_attempt_outcome(self, op_id: str) -> AttemptOutcome:
        with self._lock:
            state = self._require(op_id)
            if not state.attempts:
                raise ValueError(f"Operation has no attempts: op_id={op_id!r}")
            return state.attempts[-1].outcome

    def unfinished_op_ids(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(op_id for op_id, state in self._states.items() if state.terminal is None)

    def _require(self, op_id: str) -> _OpState:
        state = self._states.get(op_id)
        if state is None:
            raise ValueError(f"Unknown logical operation: op_id={op_id!r}, known={len(self._states)}")
        return state


@dataclass(frozen=True, slots=True)
class OrderRow:
    order_id: str
    sku: str
    qty: int
    amount_cents: int
    status: str
    created_at: float
    promo_tier: str | None


@dataclass(frozen=True, slots=True)
class OrderBookSnapshot:
    """Trusted terminal database state gathered by the verifier connection."""

    orders: Mapping[str, OrderRow]
    archived_orders: Mapping[str, OrderRow]
    payments: Mapping[str, int]
    inventory: Mapping[str, int]
    initial_inventory: Mapping[str, int]
    seed_order_ids: frozenset[str]
    promo_tier_present: bool = False


@dataclass(frozen=True, slots=True)
class ConservationReport:
    denominator_ops: int
    committed_ops: int
    good_ops: int
    failures: tuple[str, ...] = field(default_factory=tuple)
    incorrect_business_ids: tuple[str, ...] = field(default_factory=tuple)

    @property
    def conserved(self) -> bool:
        return not self.failures


def verify_conservation(ops: Sequence[LogicalOp], snapshot: OrderBookSnapshot) -> ConservationReport:
    """Cross-checks ledger truth against the terminal database snapshot."""

    failures: list[str] = []
    incorrect_ids: set[str] = set()
    committed: dict[str, LogicalOp] = {}
    for op in ops:
        if op.terminal.outcome is AttemptOutcome.COMMITTED:
            if op.op_id in committed:
                failures.append(f"operation committed twice: op_id={op.op_id!r}")
            committed[op.op_id] = op

    place_ops = {op_id: op for op_id, op in committed.items() if op.flow_id == OpKind.PLACE_ORDER.value}
    pay_ops = {op_id: op for op_id, op in committed.items() if op.flow_id == OpKind.PAY_ORDER.value}

    all_orders = dict(snapshot.orders)
    for order_id, row in snapshot.archived_orders.items():
        if order_id in all_orders:
            failures.append(f"order present in both live and archive tables: order_id={order_id!r}")
        all_orders[order_id] = row

    non_seed = set(all_orders) - snapshot.seed_order_ids
    unexpected = non_seed - set(place_ops)
    if unexpected:
        failures.append(
            f"database holds orders the ledger never committed: order_ids={sorted(unexpected)[:10]!r}, "
            f"count={len(unexpected)}"
        )

    for op_id, op in place_ops.items():
        row = all_orders.get(op_id)
        if row is None:
            failures.append(f"committed place_order missing from database: op_id={op_id!r}")
            incorrect_ids.add(op_id)
            continue
        if (
            row.sku != op.payload["sku"]
            or row.qty != op.payload["qty"]
            or row.amount_cents != op.payload["amount_cents"]
        ):
            failures.append(
                f"order row diverges from committed ledger payload: op_id={op_id!r}, row={row!r}, "
                f"payload={op.payload!r}"
            )
            incorrect_ids.add(op_id)

    for op_id, op in pay_ops.items():
        order_id = str(op.payload["order_id"])
        order_row = all_orders.get(order_id)
        if order_row is None or order_row.status != "paid":
            failures.append(f"committed pay_order but order is not paid: op_id={op_id!r}, row={order_row!r}")
            incorrect_ids.add(order_id)
        payment = snapshot.payments.get(order_id)
        if payment is None:
            failures.append(f"committed pay_order has no payment row: op_id={op_id!r}")
            incorrect_ids.add(order_id)
        elif order_row is not None and payment != order_row.amount_cents:
            failures.append(
                f"payment amount diverges from order amount: op_id={op_id!r}, "
                f"payment={payment}, order={order_row.amount_cents}"
            )
            incorrect_ids.add(order_id)

    paid_from_pay_ops = {str(op.payload["order_id"]) for op in pay_ops.values()}
    for order_id, row in all_orders.items():
        if order_id in snapshot.seed_order_ids:
            continue
        if row.status == "paid" and order_id not in paid_from_pay_ops:
            failures.append(f"paid order without a committed payment operation: order_id={order_id!r}")
        if row.status != "paid" and order_id in snapshot.payments:
            failures.append(f"payment exists for a non-paid order: order_id={order_id!r}")

    decrements: dict[str, int] = {}
    for op in place_ops.values():
        sku = str(op.payload["sku"])
        decrements[sku] = decrements.get(sku, 0) + int(op.payload["qty"])
    for sku, initial in snapshot.initial_inventory.items():
        expected = initial - decrements.get(sku, 0)
        actual = snapshot.inventory.get(sku)
        if actual != expected:
            failures.append(
                f"inventory conservation violated: sku={sku!r}, initial={initial}, "
                f"committed_decrements={decrements.get(sku, 0)}, actual={actual}, expected={expected}"
            )
    for sku in snapshot.inventory:
        if sku not in snapshot.initial_inventory:
            failures.append(f"unknown inventory row appeared: sku={sku!r}")

    return ConservationReport(
        denominator_ops=len(ops),
        committed_ops=len(committed),
        good_ops=sum(1 for op in ops if op.good),
        failures=tuple(failures),
        incorrect_business_ids=tuple(sorted(incorrect_ids)),
    )


SNAPSHOT_ORDERS_SQL = (
    "SELECT order_id, sku, qty, amount_cents, status, created_at FROM shop.orders ORDER BY order_id;"
)
SNAPSHOT_ARCHIVE_SQL = (
    "SELECT order_id, sku, qty, amount_cents, status, created_at FROM shop.orders_archive ORDER BY order_id;"
)
SNAPSHOT_PAYMENTS_SQL = "SELECT order_id, amount_cents FROM shop.payments;"
SNAPSHOT_INVENTORY_SQL = "SELECT sku, qty_available FROM shop.inventory;"


def load_order_book_snapshot(
    connection,
    *,
    initial_inventory: Mapping[str, int],
    seed_order_prefix: str = "hist-",
) -> OrderBookSnapshot:
    """Reads the terminal database state for `verify_conservation`."""

    from .control import column_exists

    def _orders(sql: str) -> dict[str, OrderRow]:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        return {
            str(row[0]): OrderRow(str(row[0]), str(row[1]), int(row[2]), int(row[3]), str(row[4]), float(row[5]), None)
            for row in rows
        }

    orders = _orders(SNAPSHOT_ORDERS_SQL)
    archived = _orders(SNAPSHOT_ARCHIVE_SQL)
    with connection.cursor() as cursor:
        cursor.execute(SNAPSHOT_PAYMENTS_SQL)
        payments = {str(row[0]): int(row[1]) for row in cursor.fetchall()}
        cursor.execute(SNAPSHOT_INVENTORY_SQL)
        inventory = {str(row[0]): int(row[1]) for row in cursor.fetchall()}
    connection.commit()
    promo_tier_present = column_exists(connection, "shop.orders", "promo_tier")
    if promo_tier_present:
        with connection.cursor() as cursor:
            cursor.execute("SELECT order_id, promo_tier FROM shop.orders;")
            tiers = {str(row[0]): (None if row[1] is None else str(row[1])) for row in cursor.fetchall()}
        connection.commit()
        orders = {
            order_id: OrderRow(
                row.order_id, row.sku, row.qty, row.amount_cents, row.status, row.created_at,
                tiers.get(order_id),
            )
            for order_id, row in orders.items()
        }
    return OrderBookSnapshot(
        orders=orders,
        archived_orders=archived,
        payments=payments,
        inventory=inventory,
        initial_inventory=dict(initial_inventory),
        # Seed baseline spans both tables: once the archive job has migrated
        # the history orders, the live table no longer names them.
        seed_order_ids=frozenset(
            order_id
            for order_id in (*orders.keys(), *archived.keys())
            if order_id.startswith(seed_order_prefix)
        ),
        promo_tier_present=promo_tier_present,
    )
