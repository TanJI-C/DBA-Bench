"""Held-session mechanics shared by leak and long-transaction capabilities.

A held session opens one pool-external connection, runs its opener statements
inside a transaction and then idles. The session is bounded: it either holds
until `hold_seconds` elapses (applied) or disappears earlier because effective
role/session protection terminated it (prevented). Evidence records which
happened; the injector never re-opens to force the fault.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

import psycopg2

from .control import effective_guc
from .ports import Clock, ConnectionSource

_PROTECTION_PGCODES = frozenset({"55P03", "57014", "57P05"})


_OPENER_MECHANISMS = {
    "55P03": "lock_timeout",
    "57014": "statement_timeout",
    "57P05": "idle_in_transaction_session_timeout",
}


@dataclass(frozen=True, slots=True)
class HeldSessionObservation:
    outcome: str  # "applied" or "prevented"
    held_seconds: float
    detail: str
    protection_gucs: Mapping[str, str]
    mechanism: str = "none"  # which protection fired when prevented

    @property
    def prevented(self) -> bool:
        return self.outcome == "prevented"

    @staticmethod
    def prevented_mechanism(detail: str, protection_gucs: Mapping[str, str]) -> str:
        for pgcode, mechanism in _OPENER_MECHANISMS.items():
            if pgcode in detail:
                return mechanism
        idle_timeout = protection_gucs.get("idle_in_transaction_session_timeout", "0")
        if idle_timeout not in {"", "0"}:
            return "idle_in_transaction_session_timeout"
        return "session_terminated_externally"


class HeldSession:
    def __init__(
        self,
        *,
        source: ConnectionSource,
        clock: Clock,
        application_name: str,
        opener: Callable[[object], None],
        protection_gucs: Sequence[str] = (
            "idle_in_transaction_session_timeout",
            "lock_timeout",
            "statement_timeout",
        ),
    ) -> None:
        self._source = source
        self._clock = clock
        self._application_name = application_name
        self._opener = opener
        self._protection_gucs = tuple(protection_gucs)

    def run(
        self,
        *,
        hold_seconds: float,
        stop: threading.Event,
        probe_interval_seconds: float = 2.0,
    ) -> HeldSessionObservation:
        started = self._clock.monotonic()
        connection = self._source.connection(self._application_name)
        try:
            try:
                self._opener(connection)
            except psycopg2.Error as exc:
                pgcode = getattr(exc, "pgcode", None)
                if pgcode in _PROTECTION_PGCODES:
                    protection_gucs = self._capture_protection_gucs()
                    return HeldSessionObservation(
                        outcome="prevented",
                        held_seconds=self._clock.monotonic() - started,
                        detail=f"opener_aborted_by_protection:pgcode={pgcode!r}",
                        protection_gucs=protection_gucs,
                        mechanism=HeldSessionObservation.prevented_mechanism(
                            f"pgcode={pgcode!r}", protection_gucs
                        ),
                    )
                raise
            while not stop.is_set():
                if self._clock.monotonic() - started >= hold_seconds:
                    break
                if not self._clock.wait_until(
                    min(self._clock.monotonic() + probe_interval_seconds, started + hold_seconds),
                    stop,
                ):
                    break
                if self._clock.monotonic() - started >= hold_seconds:
                    break
                if not self._connection_alive(connection):
                    protection_gucs = self._capture_protection_gucs()
                    return HeldSessionObservation(
                        outcome="prevented",
                        held_seconds=self._clock.monotonic() - started,
                        detail="session_terminated_while_idle",
                        protection_gucs=protection_gucs,
                        mechanism=HeldSessionObservation.prevented_mechanism(
                            "session_terminated_while_idle", protection_gucs
                        ),
                    )
        finally:
            self._close_quietly(connection)
        detail = (
            "released_at_injector_stop"
            if stop.is_set() and self._clock.monotonic() - started < hold_seconds
            else "held_until_hold_deadline_then_released"
        )
        return HeldSessionObservation(
            outcome="applied",
            held_seconds=self._clock.monotonic() - started,
            detail=detail,
            protection_gucs=self._capture_protection_gucs(),
        )

    def _connection_alive(self, connection: object) -> bool:
        try:
            with connection.cursor() as cursor:  # type: ignore[attr-defined]
                # SELECT 1 inside the open transaction: it must not commit,
                # commit is exactly what would release the held locks.
                cursor.execute("SELECT 1;")
                cursor.fetchall()
            return True
        except psycopg2.Error:
            return False

    def _capture_protection_gucs(self) -> dict[str, str]:
        connection = self._source.connection(f"{self._application_name}-probe")
        try:
            return {guc: effective_guc(connection, guc) for guc in self._protection_gucs}
        finally:
            connection.close()

    def _close_quietly(self, connection: object) -> None:
        """Releases the session the way a client-side timeout would.

        A rollback failure on an already-terminated session is the terminated
        case itself and is reported by the caller's liveness probe, so the
        close path only ignores that specific breakage.
        """

        try:
            connection.rollback()  # type: ignore[attr-defined]
        except psycopg2.Error:
            pass
        connection.close()  # type: ignore[attr-defined]
