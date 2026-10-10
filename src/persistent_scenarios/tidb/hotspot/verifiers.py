"""Business-truth verifiers for the OLTP hotspot instance.

Call convention: ``verifier(port, connection, ledger_view, params) -> Mapping`` where
``connection`` is a trusted business-truth connection and ``port`` is the
``TiDBPersistentEnvironmentPort``. Every verifier returns a JSON-able fact
mapping with a boolean ``passed``; infrastructure failures raise.
"""

from __future__ import annotations

from typing import Any, Mapping

from src.persistent_scenarios.runtime.ledger import LedgerTerminal, LogicalTransactionRecord

from . import schema
from .business import PlaceOrderPayload  # noqa: F401  (re-exported for reference)

_ORDERS_SQL = (
    "SELECT order_id, sku, qty, amount_cents, status, idempotency_key FROM shop.orders"
)
_PAYMENTS_SQL = "SELECT order_id, amount_cents FROM shop.payments"
_INVENTORY_SQL = "SELECT sku, qty_available FROM shop.inventory"
_DUPLICATE_KEY_SQL = (
    "SELECT idempotency_key, COUNT(*) FROM shop.orders GROUP BY idempotency_key HAVING COUNT(*) > 1"
)


def _fetch_all(connection: Any, sql: str) -> tuple[tuple, ...]:
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    connection.commit()
    return rows


def _trusted_prefixes(params: Mapping[str, Any]) -> tuple[str, ...]:
    """Order-id prefixes of declared trusted out-of-ledger writers.

    Mechanism-evidence probes commit business rows the workload ledger does
    not plan. Their committed rows stay DB-verified (paid consistency, key
    consistency, uniqueness, inventory decrements); only the "explained by
    the ledger" expectation is scoped away. Empty by default: in a
    production run the driver is the only writer and every row must be
    explained by the ledger."""
    return tuple(str(prefix) for prefix in params.get("trusted_order_id_prefixes", ()))


def _committed_place_ops(ledger_view: Any) -> dict[str, Mapping[str, Any]]:
    places: dict[str, Mapping[str, Any]] = {}
    for record in ledger_view.logical_transactions():
        if record.tx_kind != "place_order" or record.terminal is not LedgerTerminal.COMPLETED:
            continue
        payload = _place_payload_from_record(record)
        if payload is not None:
            places[record.business_id] = payload
    return places


def _committed_pay_ops(ledger_view: Any) -> dict[str, Mapping[str, Any]]:
    pays: dict[str, Mapping[str, Any]] = {}
    for record in ledger_view.logical_transactions():
        if record.tx_kind != "pay_order" or record.terminal is not LedgerTerminal.COMPLETED:
            continue
        payload = _pay_payload_from_record(record)
        if payload is not None:
            pays[record.business_id] = payload
    return pays


def _place_payload_from_record(record: LogicalTransactionRecord) -> Mapping[str, Any] | None:
    for attempt in reversed(record.attempts):
        if "sku" in attempt.detail and "qty" in attempt.detail:
            return {
                "sku": str(attempt.detail["sku"]),
                "qty": int(attempt.detail["qty"]),
                "amount_cents": int(attempt.detail["amount_cents"]),
                "order_id": str(attempt.detail["order_id"]),
            }
    return None


def _pay_payload_from_record(record: LogicalTransactionRecord) -> Mapping[str, Any] | None:
    for attempt in reversed(record.attempts):
        if "order_id" in attempt.detail and "amount_cents" in attempt.detail:
            return {
                "order_id": str(attempt.detail["order_id"]),
                "amount_cents": int(attempt.detail["amount_cents"]),
            }
    return None


def commerce_ledger_conservation(
    port: Any, connection: Any, ledger_view: Any, params: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Order/payment/inventory truth against the trusted transaction ledger."""
    places = _committed_place_ops(ledger_view)
    pays = _committed_pay_ops(ledger_view)

    orders = {
        str(row[0]): {"sku": str(row[1]), "qty": int(row[2]), "amount_cents": int(row[3]), "status": str(row[4])}
        for row in _fetch_all(connection, _ORDERS_SQL)
    }
    payments = {str(row[0]): int(row[1]) for row in _fetch_all(connection, _PAYMENTS_SQL)}
    inventory = {str(row[0]): int(row[1]) for row in _fetch_all(connection, _INVENTORY_SQL)}

    failures: list[str] = []
    prefixes = _trusted_prefixes(params)
    placed_order_ids = {str(payload["order_id"]) for payload in places.values()}
    trusted_order_ids = {order_id for order_id in orders if order_id.startswith(prefixes)}

    unexpected = set(orders) - placed_order_ids - trusted_order_ids
    if unexpected:
        failures.append(
            f"database holds orders the ledger never committed: order_ids={sorted(unexpected)[:10]!r}, "
            f"count={len(unexpected)}"
        )
    for op_id, payload in places.items():
        order_id = str(payload["order_id"])
        row = orders.get(order_id)
        if row is None:
            failures.append(f"committed place_order missing from database: op_id={op_id!r}, order_id={order_id!r}")
            continue
        if (
            row["sku"] != payload["sku"]
            or row["qty"] != payload["qty"]
            or row["amount_cents"] != payload["amount_cents"]
        ):
            failures.append(
                f"order row diverges from committed ledger payload: order_id={order_id!r}, row={row!r}, "
                f"payload={payload!r}"
            )

    paid_from_ledger = {str(payload["order_id"]) for payload in pays.values()}
    for order_id, row in orders.items():
        if row["status"] == "paid" and order_id not in paid_from_ledger:
            failures.append(f"paid order without a committed payment transaction: order_id={order_id!r}")
        if row["status"] != "paid" and order_id in payments:
            failures.append(f"payment exists for a non-paid order: order_id={order_id!r}")
    for op_id, payload in pays.items():
        order_id = str(payload["order_id"])
        row = orders.get(order_id)
        if row is None or row["status"] != "paid":
            failures.append(f"committed pay_order but order is not paid: op_id={op_id!r}, order_id={order_id!r}")
            continue
        payment = payments.get(order_id)
        if payment is None:
            failures.append(f"committed pay_order has no payment row: op_id={op_id!r}, order_id={order_id!r}")
        elif payment != row["amount_cents"]:
            failures.append(
                f"payment amount diverges from order amount: order_id={order_id!r}, "
                f"payment={payment}, order={row['amount_cents']}"
            )
        if payment is not None and payment != int(payload["amount_cents"]):
            failures.append(
                f"payment amount diverges from ledger payload: order_id={order_id!r}, payment={payment}, "
                f"payload={payload['amount_cents']}"
            )

    decrements: dict[str, int] = {}
    for payload in places.values():
        sku = str(payload["sku"])
        decrements[sku] = decrements.get(sku, 0) + int(payload["qty"])
    for order_id in trusted_order_ids:
        sku = orders[order_id]["sku"]
        decrements[sku] = decrements.get(sku, 0) + int(orders[order_id]["qty"])
    seed_inventory = schema.seed_snapshot()
    for sku, initial in seed_inventory.items():
        expected = initial - decrements.get(sku, 0)
        actual = inventory.get(sku)
        if actual is None:
            failures.append(f"seeded inventory row missing: sku={sku!r}")
        elif actual != expected:
            failures.append(
                f"inventory conservation violated: sku={sku!r}, initial={initial}, "
                f"committed_decrements={decrements.get(sku, 0)}, actual={actual}, expected={expected}"
            )
    for sku in inventory:
        if sku not in seed_inventory:
            failures.append(f"unknown inventory row appeared: sku={sku!r}")

    return {
        "passed": not failures,
        "failures": failures[:20],
        "failure_count": len(failures),
        "committed_place_ops": len(places),
        "committed_pay_ops": len(pays),
        "db_orders": len(orders),
    }


def orders_idempotency_uniqueness(
    port: Any, connection: Any, ledger_view: Any, params: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Every business identity appears at most once; retries never duplicate rows."""
    duplicates = [(str(row[0]), int(row[1])) for row in _fetch_all(connection, _DUPLICATE_KEY_SQL)]
    orders = {
        str(row[0]): str(row[5])
        for row in _fetch_all(connection, _ORDERS_SQL)
    }
    ledger_place_ids = set()
    for record in ledger_view.logical_transactions():
        if record.tx_kind == "place_order":
            ledger_place_ids.add(record.business_id)
    trusted_order_ids = {order_id for order_id in orders if order_id.startswith(_trusted_prefixes(params))}
    orphan_orders = sorted(set(orders) - ledger_place_ids - trusted_order_ids)
    key_mismatches = sorted(
        order_id for order_id, key in orders.items() if key != order_id
    )
    failures = []
    if duplicates:
        failures.append(f"idempotency keys map to multiple orders: duplicates={duplicates[:10]!r}")
    if orphan_orders:
        failures.append(f"orders with no ledger transaction: order_ids={orphan_orders[:10]!r}")
    if key_mismatches:
        failures.append(f"order_id and idempotency_key diverged: order_ids={key_mismatches[:10]!r}")
    return {
        "passed": not failures,
        "failures": failures,
        "duplicate_keys": len(duplicates),
        "order_count": len(orders),
    }


def unknown_commit_dedup(
    port: Any, connection: Any, ledger_view: Any, params: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Uncertain commits resolved through the idempotency key never duplicate."""
    orders = {str(row[0]) for row in _fetch_all(connection, _ORDERS_SQL)}
    failures: list[str] = []
    reconciled_committed = 0
    for record in ledger_view.logical_transactions():
        uncertain = any(bool(attempt.detail.get("uncertain_commit")) for attempt in record.attempts)
        if record.tx_kind == "place_order":
            order_id = record.business_id
            if uncertain and record.terminal is LedgerTerminal.COMPLETED:
                reconciled_committed += 1
            if uncertain and record.terminal is not LedgerTerminal.COMPLETED and order_id in orders:
                failures.append(
                    f"order row exists though the ledger resolved the unknown commit as not committed: "
                    f"order_id={order_id!r}, terminal={record.terminal.value}"
                )
            if record.terminal is LedgerTerminal.COMPLETED and order_id not in orders:
                failures.append(f"completed place_order has no order row: order_id={order_id!r}")
            if record.terminal is not LedgerTerminal.COMPLETED and order_id in orders:
                failures.append(
                    f"order row exists for a transaction the ledger did not complete: "
                    f"order_id={order_id!r}, terminal={record.terminal.value}"
                )
    return {
        "passed": not failures,
        "failures": failures[:20],
        "failure_count": len(failures),
        "uncertain_commits_resolved_committed": reconciled_committed,
    }


VERIFIERS: dict[str, Any] = {
    "commerce_ledger_conservation": commerce_ledger_conservation,
    "orders_idempotency_uniqueness": orders_idempotency_uniqueness,
    "unknown_commit_dedup": unknown_commit_dedup,
}
