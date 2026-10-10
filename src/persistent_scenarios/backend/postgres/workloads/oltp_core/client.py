"""Logical transaction executors for the pg5 OLTP trade flows.

Every execution unit is a logical operation with a client-generated business
identity (`order_id`). A retry of the same logical operation reuses that
identity and is idempotent at the database level, so the SLO denominator
counts each logical operation once no matter how many attempts it needed.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any

import psycopg2

from .control import ClientConfig
from .schema import promo_tier_for_amount


class FlowFailure(RuntimeError):
    """A logical operation attempt failed in a way the driver records as such."""


class ConnectionFailure(FlowFailure):
    """The driver could not open or use its database connection."""


class AttemptKind(str, enum.Enum):
    COMMITTED = "committed"
    COMMITTED_REPLAY = "committed_replay"
    BUSINESS_REJECTED = "business_rejected"


@dataclass(frozen=True, slots=True)
class PlaceOrderPayload:
    order_id: str
    sku: str
    qty: int
    amount_cents: int
    created_at: float
    promo_tier: str | None = None


@dataclass(frozen=True, slots=True)
class PayOrderPayload:
    order_id: str
    amount_cents: int
    paid_at: float


PLACE_ORDER_SQL = (
    "INSERT INTO shop.orders (order_id, sku, qty, amount_cents, status, created_at) "
    "VALUES (%(order_id)s, %(sku)s, %(qty)s, %(amount_cents)s, 'pending', %(created_at)s) "
    "ON CONFLICT (order_id) DO NOTHING;"
)
PLACE_ORDER_V2_SQL = (
    "INSERT INTO shop.orders (order_id, sku, qty, amount_cents, status, created_at, promo_tier) "
    "VALUES (%(order_id)s, %(sku)s, %(qty)s, %(amount_cents)s, 'pending', %(created_at)s, %(promo_tier)s) "
    "ON CONFLICT (order_id) DO NOTHING;"
)
DECREMENT_INVENTORY_SQL = (
    "UPDATE shop.inventory SET qty_available = qty_available - %(qty)s "
    "WHERE sku = %(sku)s AND qty_available >= %(qty)s;"
)
ORDER_STATUS_SQL = "SELECT status FROM shop.orders WHERE order_id = %(order_id)s;"
PAY_ORDER_SQL = (
    "UPDATE shop.orders SET status = 'paid', paid_at = %(paid_at)s "
    "WHERE order_id = %(order_id)s AND status = 'pending';"
)
INSERT_PAYMENT_SQL = (
    "INSERT INTO shop.payments (payment_id, order_id, amount_cents) "
    "VALUES (%(payment_id)s, %(order_id)s, %(amount_cents)s) "
    "ON CONFLICT (order_id) DO NOTHING;"
)
STOCK_READ_SQL = "SELECT qty_available FROM shop.inventory WHERE sku = %(sku)s;"

_TIMEOUT_PGCODES = frozenset({"55P03", "57014"})


def set_attempt_timeouts(cursor: Any, policy: ClientConfig) -> None:
    cursor.execute(f"SET LOCAL statement_timeout = {int(policy.request_timeout_ms)};")
    cursor.execute(f"SET LOCAL lock_timeout = {int(policy.request_timeout_ms)};")


def classify_psycopg_error(exc: Exception) -> str:
    """Maps a database error to the driver's terminal/attempt outcome class."""

    if isinstance(exc, FlowFailure):
        raise AssertionError(f"FlowFailure must not reach classify_psycopg_error: {exc!r}")
    pgcode = getattr(exc, "pgcode", None)
    if pgcode in _TIMEOUT_PGCODES:
        return "timeout"
    if isinstance(exc, (psycopg2.OperationalError, psycopg2.InterfaceError)):
        return "connection_refused"
    return "error"


def place_order(connection: Any, payload: PlaceOrderPayload, policy: ClientConfig) -> AttemptKind:
    """One idempotent place_order attempt. Rolls back on business rejection."""

    with connection.cursor() as cursor:
        set_attempt_timeouts(cursor, policy)
        cursor.execute(
            PLACE_ORDER_V2_SQL if payload.promo_tier is not None else PLACE_ORDER_SQL,
            {
                "order_id": payload.order_id,
                "sku": payload.sku,
                "qty": payload.qty,
                "amount_cents": payload.amount_cents,
                "created_at": payload.created_at,
                "promo_tier": payload.promo_tier,
            },
        )
        inserted = cursor.rowcount
        if inserted == 0:
            cursor.execute(ORDER_STATUS_SQL, {"order_id": payload.order_id})
            row = cursor.fetchone()
            if row is None:
                raise FlowFailure(
                    "place_order replay found no existing order despite insert conflict: "
                    f"order_id={payload.order_id!r}"
                )
            connection.commit()
            return AttemptKind.COMMITTED_REPLAY
        cursor.execute(DECREMENT_INVENTORY_SQL, {"sku": payload.sku, "qty": payload.qty})
        if cursor.rowcount == 0:
            connection.rollback()
            return AttemptKind.BUSINESS_REJECTED
    connection.commit()
    return AttemptKind.COMMITTED


def pay_order(connection: Any, payload: PayOrderPayload, policy: ClientConfig) -> AttemptKind:
    """One idempotent pay_order attempt keyed by the order business identity."""

    with connection.cursor() as cursor:
        set_attempt_timeouts(cursor, policy)
        cursor.execute(PAY_ORDER_SQL, {"order_id": payload.order_id, "paid_at": payload.paid_at})
        paid_now = cursor.rowcount
        if paid_now == 0:
            cursor.execute(ORDER_STATUS_SQL, {"order_id": payload.order_id})
            row = cursor.fetchone()
            if row is None:
                connection.rollback()
                return AttemptKind.BUSINESS_REJECTED
            if str(row[0]) != "paid":
                connection.rollback()
                return AttemptKind.BUSINESS_REJECTED
            connection.commit()
            return AttemptKind.COMMITTED_REPLAY
        cursor.execute(
            INSERT_PAYMENT_SQL,
            {
                "payment_id": f"pay-{payload.order_id}",
                "order_id": payload.order_id,
                "amount_cents": payload.amount_cents,
            },
        )
    connection.commit()
    return AttemptKind.COMMITTED


def stock_read(connection: Any, sku: str, policy: ClientConfig) -> int:
    with connection.cursor() as cursor:
        set_attempt_timeouts(cursor, policy)
        cursor.execute(STOCK_READ_SQL, {"sku": sku})
        row = cursor.fetchone()
    if row is None:
        raise FlowFailure(f"stock_read found no inventory row: sku={sku!r}")
    connection.commit()
    return int(row[0])


def new_version_place_payload(payload: PlaceOrderPayload) -> PlaceOrderPayload:
    """Promotion-tier application writes the derived column from schema v2 on."""

    return PlaceOrderPayload(
        order_id=payload.order_id,
        sku=payload.sku,
        qty=payload.qty,
        amount_cents=payload.amount_cents,
        created_at=payload.created_at,
        promo_tier=promo_tier_for_amount(payload.amount_cents),
    )
