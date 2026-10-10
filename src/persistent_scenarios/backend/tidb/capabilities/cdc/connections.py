"""Connection factories for the CDC freshness workload drivers.

The persistent backend owns the real environment; the driver only needs two
DBAPI connection surfaces (upstream TiDB, downstream MySQL). Integration
injects the factories; experiments use the pymysql adapter below.
"""

from __future__ import annotations

from typing import Protocol

import pymysql


class CdcConnectionFactories(Protocol):
    """Returns a fresh PEP-249 connection per call (caller owns and closes it)."""

    def upstream(self) -> object: ...

    def downstream(self) -> object: ...


class PymysqlCdcConnections:
    """Pymysql adapter over the deployed topology endpoints."""

    def __init__(self, *, upstream_host: str, upstream_port: int,
                 downstream_host: str, downstream_port: int,
                 user: str = "root", password: str = "",
                 connect_timeout: int = 10, read_timeout: int = 60):
        self._upstream = (upstream_host, upstream_port)
        self._downstream = (downstream_host, downstream_port)
        self._user = user
        self._password = password
        self._connect_timeout = connect_timeout
        self._read_timeout = read_timeout

    def upstream(self) -> pymysql.connections.Connection:
        return self._connect(self._upstream)

    def downstream(self) -> pymysql.connections.Connection:
        return self._connect(self._downstream)

    def _connect(self, endpoint: tuple[str, int]) -> pymysql.connections.Connection:
        return pymysql.connect(
            host=endpoint[0], port=endpoint[1], user=self._user, password=self._password,
            database=None, connect_timeout=self._connect_timeout,
            read_timeout=self._read_timeout, autocommit=True,
        )


TRANSPORT_ERRORS = (pymysql.err.InterfaceError, pymysql.err.OperationalError)


def is_transport_error(exc: Exception) -> bool:
    """A broken client socket/timeout is a transport fact; anything else is business."""
    if isinstance(exc, pymysql.err.OperationalError):
        code = exc.args[0] if exc.args else None
        return code in (2002, 2003, 2006, 2013, 2055, 4031)
    return isinstance(exc, pymysql.err.InterfaceError)
