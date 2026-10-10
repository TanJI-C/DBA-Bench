"""Instance 1 (business priority) transaction-leak mechanism.

The leak opens a pool-external session with the application role, updates one
promotion hot-row and then idles inside the open transaction, holding the row
lock against every concurrent inventory decrement on that SKU. The session is
bounded by `hold_seconds` (the client's own timeout that finally rolls it
back) or by effective role protection, whichever comes first.

`application_name` lets an occurrence masquerade as a scheduled maintenance
job (tx_leak_2): the session still connects with the application role's write
grants, but announces a maintenance-looking application name and self-
registers into `ops.maintenance_registry`, so only the audit trajectory,
transaction age and last-query attributes separate it from real maintenance.
"""

from __future__ import annotations

from ..oltp_core.held_session import HeldSession, HeldSessionObservation
from ..oltp_core.ports import Clock, ConnectionSource

LEAK_APPLICATION_NAME = "shop_app"

LEAK_HOT_ROW_UPDATE_SQL = (
    "UPDATE shop.inventory SET qty_available = qty_available - 1 WHERE sku = %(sku)s;"
)


def hot_row_opener(sku: str) -> object:
    def opener(connection: object) -> None:
        with connection.cursor() as cursor:  # type: ignore[attr-defined]
            cursor.execute(LEAK_HOT_ROW_UPDATE_SQL, {"sku": sku})
        # No commit, no rollback: idling inside the transaction is the leak.

    return opener


def run_tx_leak(
    *,
    source: ConnectionSource,
    clock: Clock,
    sku: str,
    hold_seconds: float,
    stop,
    application_name: str = LEAK_APPLICATION_NAME,
) -> HeldSessionObservation:
    session = HeldSession(
        source=source,
        clock=clock,
        application_name=application_name,
        opener=hot_row_opener(sku),
    )
    return session.run(hold_seconds=hold_seconds, stop=stop)
