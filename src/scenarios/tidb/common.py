import re
from collections.abc import Callable, Iterable

import pymysql

from src.database.sql import require_success_payload
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext


_SQL_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_sql_identifier(value: str, name: str) -> str:
    if not _SQL_IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid SQL identifier for {name}: {value!r}")
    return value


def _var_u64(value: int) -> bytes:
    if value < 0:
        raise ValueError(f"TiDB varint value must be non-negative: value={value}")
    encoded = bytearray()
    while value >= 0x80:
        encoded.append((value & 0x7F) | 0x80)
        value >>= 7
    encoded.append(value)
    return bytes(encoded)


def _compact_bytes(value: bytes) -> bytes:
    return _var_u64(len(value) << 1) + value


def _table_row_key(table_id: int, handle: int) -> bytes:
    if table_id <= 0 or handle <= 0:
        raise ValueError(
            f"TiDB row key IDs must be positive: table_id={table_id}, handle={handle}"
        )
    encoded_table = (table_id + (1 << 63)).to_bytes(8, "big")
    encoded_handle = (handle + (1 << 63)).to_bytes(8, "big")
    return b"t" + encoded_table + b"_r" + encoded_handle


def connect_tidb(
    env,
    *,
    database: str | None = None,
    autocommit: bool,
    application_name: str | None = None,
    read_timeout: int = 180,
    write_timeout: int = 180,
):
    connection = pymysql.connect(
        host=env.host,
        port=env.port,
        user=env.user,
        password=env.password,
        database=env.dbname if database is None else database,
        charset="utf8mb4",
        autocommit=autocommit,
        connect_timeout=5,
        read_timeout=read_timeout,
        write_timeout=write_timeout,
    )
    if application_name is not None:
        with connection.cursor() as cursor:
            cursor.execute("SET @aiopsbench_application_name = %s", (application_name,))
    return connection


def require_sql_success(result, context: str):
    require_success_payload(result, context)
    return result


def sequence_row_source(rows: int) -> str:
    """Deterministic subquery producing n = 1..rows as column `n`.

    Two-level recursion keeps each CTE under TiDB's default cte_max_recursion_depth
    (1000) and avoids catalog cross joins whose intermediate result TiDB cancels
    with memory error 8176.
    """
    if rows <= 0:
        raise ValueError(f"sequence row count must be positive: rows={rows}")
    tail = 200
    head = (rows + tail - 1) // tail
    return (
        "SELECT n "
        "FROM (WITH RECURSIVE head(h) AS (SELECT 1 UNION ALL SELECT h + 1 FROM head WHERE h < {head}), "
        "tail(t) AS (SELECT 1 UNION ALL SELECT t + 1 FROM tail WHERE t < {tail}) "
        "SELECT (head.h - 1) * 200 + tail.t AS n FROM head CROSS JOIN tail "
        "WHERE (head.h - 1) * 200 + tail.t <= {rows}) source"
    ).format(head=head, tail=tail, rows=rows)


def json_object(result, context: str) -> dict:
    return require_success_payload(result, context)


def run_sql_batches(
    execute_sql: Callable[[str], object],
    prefix: str,
    values: Iterable[str],
    batch_size: int,
    context: str,
) -> None:
    values = tuple(values)
    for start in range(0, len(values), batch_size):
        batch = values[start : start + batch_size]
        require_sql_success(
            execute_sql(prefix + ",".join(batch)),
            f"{context} rows {start}-{start + len(batch) - 1}",
        )


def join_thread(thread, timeout: float, context: str) -> None:
    thread.join(timeout=timeout)
    if thread.is_alive():
        raise RuntimeError(f"{context} did not stop within {timeout} seconds")


def run_cleanup_steps(context: str, steps: Iterable[tuple[str, Callable[[], object]]]) -> None:
    failures = []
    for operation, step in steps:
        try:
            step()
        except Exception as exc:
            failures.append((operation, exc))
    if failures:
        details = "; ".join(
            f"{operation}: {type(exc).__name__}: {exc}"
            for operation, exc in failures
        )
        raise RuntimeError(f"{context} failed: {details}") from failures[0][1]
