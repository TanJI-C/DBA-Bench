"""Instance 5 (online change) legacy client long-transaction mechanism.

An old reporting client opens a REPEATABLE READ transaction over the order
book and then idles because of a client defect, holding the relation
AccessShare lock and an xmin snapshot. That open transaction is the natural
DDL blocker for the release and, in the second occurrence, the repeat pattern
that scoped role protection should prevent.
"""

from __future__ import annotations

from ..oltp_core.held_session import HeldSession, HeldSessionObservation
from ..oltp_core.ports import Clock, ConnectionSource

LONG_TX_APPLICATION_NAME = "report_client"

LONG_TX_SNAPSHOT_SQL = (
    "SELECT count(*) FROM shop.orders WHERE created_at < %(cutoff)s;"
)


def repeatable_read_snapshot_opener(cutoff_created_at: float) -> object:
    def opener(connection: object) -> None:
        with connection.cursor() as cursor:  # type: ignore[attr-defined]
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            cursor.execute(LONG_TX_SNAPSHOT_SQL, {"cutoff": cutoff_created_at})
            cursor.fetchall()
        # No commit: the defect is idling inside the open snapshot transaction.

    return opener


def run_legacy_long_tx(
    *,
    source: ConnectionSource,
    clock: Clock,
    cutoff_created_at: float,
    hold_seconds: float,
    stop,
) -> HeldSessionObservation:
    session = HeldSession(
        source=source,
        clock=clock,
        application_name=LONG_TX_APPLICATION_NAME,
        opener=repeatable_read_snapshot_opener(cutoff_created_at),
        protection_gucs=(
            "idle_in_transaction_session_timeout",
            "statement_timeout",
        ),
    )
    # The liveness probe must idle LONGER than the protections it is meant to
    # trip: each probe statement resets idle_in_transaction_session_timeout,
    # so a 2s probe makes any role-set idle protection unable to ever fire and
    # the scoped-prevention path (contract t=52) impossible. 15s lets a 10s
    # role timeout abort the session and be recorded as prevented.
    return session.run(hold_seconds=hold_seconds, stop=stop, probe_interval_seconds=15.0)
