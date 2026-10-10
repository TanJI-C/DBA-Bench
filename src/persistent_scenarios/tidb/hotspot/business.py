"""Business transaction bodies and outcome classification for the OLTP instance.

One attempt is one full client attempt: begin -> SQL -> commit, with the
client-side read timeout imposed by the connection. A lost connection or read
timeout after commit was *sent* leaves the commit outcome unknown; the caller
resolves it through the idempotency key (``reconcile_order_committed``) and
never treats a client timeout as a rollback.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from src.persistent_scenarios.runtime.ledger import AttemptOutcome

# MySQL/TiDB error codes that mean "rolled back, conflict-style, retryable".
CONFLICT_RETRYABLE_CODES = frozenset({1205, 1213, 9007, 9001, 9004, 9005})
CONNECTION_LOST_CODES = frozenset({2006, 2013})
# TiDB commit-result-unknown surface: the commit RPC may have landed on TiKV.
COMMIT_UNKNOWN_CODES = frozenset({2013, 2006, 8022, 9001})


class BusinessRejected(Exception):
    """A committed-none business rejection (e.g. insufficient inventory)."""


@dataclass(frozen=True, slots=True)
class PlaceOrderPayload:
    order_id: str
    sku: str
    qty: int
    amount_cents: int
    created_at_ms: int

    @property
    def idempotency_key(self) -> str:
        return self.order_id


@dataclass(frozen=True, slots=True)
class PayOrderPayload:
    order_id: str
    amount_cents: int
    paid_at_ms: int


PLACE_ORDER_SQL = (
    "INSERT INTO shop.orders (order_id, sku, qty, amount_cents, status, idempotency_key, created_at_ms) "
    "VALUES (%s, %s, %s, %s, 'placed', %s, %s)"
)
DECREMENT_INVENTORY_SQL = (
    "UPDATE shop.inventory SET qty_available = qty_available - %s WHERE sku = %s AND qty_available >= %s"
)
PAY_ORDER_SQL = "UPDATE shop.orders SET status = 'paid' WHERE order_id = %s AND status = 'placed'"
INSERT_PAYMENT_SQL = "INSERT INTO shop.payments (order_id, amount_cents, paid_at_ms) VALUES (%s, %s, %s)"
STOCK_READ_SQL = "SELECT qty_available FROM shop.inventory WHERE sku = %s"
RECONCILE_ORDER_SQL = "SELECT COUNT(*) FROM shop.orders WHERE idempotency_key = %s"


def classify_pymysql_error(exc: Exception) -> tuple[AttemptOutcome, bool]:
    """Map a pymysql failure to (core ledger outcome, client-retryable)."""
    code = exc.args[0] if exc.args else None
    if isinstance(code, int):
        if code in COMMIT_UNKNOWN_CODES:
            # The commit result is unknown; only idempotency-key reconciliation
            # may decide the terminal outcome.
            return AttemptOutcome.TIMED_OUT, True
        if code in CONNECTION_LOST_CODES:
            return AttemptOutcome.CONNECTION_REFUSED, True
        if code in CONFLICT_RETRYABLE_CODES:
            return AttemptOutcome.ABORTED, True
        return AttemptOutcome.ABORTED, False
    if type(exc).__name__ in {"InterfaceError", "OperationalError"}:
        return AttemptOutcome.CONNECTION_REFUSED, True
    return AttemptOutcome.ABORTED, False


def _release_failed_transaction(connection: Any) -> None:
    """Roll back the open transaction after a failed attempt.

    A read timeout or KILL leaves the connection dead, so the rollback itself
    raises; that must never mask the original attempt error, which is the sole
    input for the caller's outcome classification."""
    try:
        connection.rollback()
    except Exception:
        pass


def place_order(connection: Any, payload: PlaceOrderPayload) -> str:
    """One checkout attempt. Returns the committed result digest."""
    connection.begin()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                PLACE_ORDER_SQL,
                (payload.order_id, payload.sku, payload.qty, payload.amount_cents,
                 payload.idempotency_key, payload.created_at_ms),
            )
            cursor.execute(DECREMENT_INVENTORY_SQL, (payload.qty, payload.sku, payload.qty))
            if cursor.rowcount != 1:
                raise BusinessRejected(
                    f"insufficient inventory: sku={payload.sku!r}, requested={payload.qty}, "
                    f"order_id={payload.order_id!r}"
                )
    except Exception:
        _release_failed_transaction(connection)
        raise
    connection.commit()
    return f"order:{payload.order_id}:{payload.sku}:{payload.qty}:{payload.amount_cents}"


def pay_order(connection: Any, payload: PayOrderPayload) -> str:
    connection.begin()
    try:
        with connection.cursor() as cursor:
            cursor.execute(PAY_ORDER_SQL, (payload.order_id,))
            if cursor.rowcount != 1:
                raise BusinessRejected(
                    f"order not in payable state: order_id={payload.order_id!r}"
                )
            cursor.execute(INSERT_PAYMENT_SQL, (payload.order_id, payload.amount_cents, payload.paid_at_ms))
    except Exception:
        _release_failed_transaction(connection)
        raise
    connection.commit()
    return f"payment:{payload.order_id}:{payload.amount_cents}"


def stock_read(connection: Any, sku: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(STOCK_READ_SQL, (sku,))
        row = cursor.fetchone()
    if row is None:
        raise ValueError(f"stock read found no inventory row: sku={sku!r}")
    connection.commit()
    return int(row[0])


def reconcile_order_committed(connection: Any, idempotency_key: str) -> bool:
    """Resolve an unknown commit outcome through the business idempotency key."""
    with connection.cursor() as cursor:
        cursor.execute(RECONCILE_ORDER_SQL, (idempotency_key,))
        row = cursor.fetchone()
    connection.commit()
    return int(row[0]) > 0


def settlement_touch(connection: Any, sku: str) -> None:
    """One settlement-batch row touch: takes the inventory row write lock and
    keeps the transaction open (long-transaction capability body)."""
    connection.begin()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT qty_available FROM shop.inventory WHERE sku = %s FOR UPDATE", (sku,)
        )
        row = cursor.fetchone()
    if row is None:
        connection.rollback()
        raise ValueError(f"settlement touch found no inventory row: sku={sku!r}")


def ledger_place_detail(payload: PlaceOrderPayload) -> Mapping[str, Any]:
    return {
        "order_id": payload.order_id,
        "sku": payload.sku,
        "qty": payload.qty,
        "amount_cents": payload.amount_cents,
        "idempotency_key": payload.idempotency_key,
    }
