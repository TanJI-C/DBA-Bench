from __future__ import annotations

import threading
import time
import zlib
from collections.abc import Mapping
from dataclasses import dataclass, replace

from src.database.sql import sql_literal
from src.scenarios.evaluation.tidb.system_failure.gc_mvcc_recovery import (
    TidbSystemFailureGcMvccRecoveryEvaluatorCase,
    TidbSystemFailureGcMvccRecoveryCaseEvaluator,
)
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    _compact_bytes,
    _table_row_key,
    _var_u64,
    connect_tidb,
    json_object,
    validate_sql_identifier,
)
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


K01_DB = "bench_k01"
K01_TARGET_TABLE = "k01_target_orders"
K01_HEALTHY_TABLE = "k01_healthy_orders"
K01_LONG_TX_TABLE = "k01_long_tx_orders"
K01_ROW_COUNT = 256
# Pre-split the target table so the affected row must be bound to one live key-range Region.
K01_TARGET_REGION_SPLIT_MAX_ROW_ID = 4096
K01_MIN_TARGET_REGION_COUNT = 4
# Keep the malformed lock on a pending key so ordinary seeded-row truth reads remain readable.
K01_TARGET_ROW_ID = 257
K01_NORMAL_LOCK_ROW_ID = 23
K01_LONG_TX_ROW_ID = 41
# Legal pessimistic operator lock inside the target table's key range: its real lock CF record
# (visible because the case disables TiKV in-memory pessimistic locks) shares the recovery Region
# with the malformed async-commit lock and must be discriminated from it.
K01_TARGET_LEGAL_LOCK_ROW_ID = 202
# Second protected live pessimistic lock holder inside the same recovery Region (investigator
# session): it never commits during the episode, so the recovery Region always contains an
# in-flight 'S' lock record and region-level maintenance stays interlocked.
K01_TARGET_STUCK_HOLDER_ROW_ID = 300
K01_OPERATOR_BACKFILL_DELTA = 2020
K01_BACKFILL_PROGRESS_TABLE = "k01_backfill_progress"
K01_BACKFILL_COMMIT_ROWS = 120
K01_BACKFILL_POLL_SECONDS = 2
K01_NEW_WRITE_ID = 10001
K01_NEW_WRITE_AMOUNT = 9317
K01_NEW_WRITE_PAYLOAD = "k01-recovered-write"
K01_LOCK_TTL_MS = 3_600_000
K01_RECOVERY_TASK_TABLE = "k01_recovery_tasks"
K01_RECOVERY_TASK_NO = "K01-RCV-20260915-001"
K01_RECOVERY_TASK_TITLE = "authorized recovery acceptance write for the stalled orders table"
K01_RECOVERY_TASK_APPLICANT = "dba-oncall"
K01_RECOVERY_TASK_WINDOW = "current incident resolution window"
K01_RECOVERY_TASK_STATUS = "approved"


def k01_amount(row_id: int) -> int:
    return 1000 + (row_id * 37) % 9000


def k01_crc(row_id: int, amount: int) -> int:
    return zlib.crc32(f"k01:{row_id}:{amount}".encode()) & 0xFFFFFFFF


def _business_truth(row_count: int) -> tuple[int, int, int]:
    rows = [(row_id, k01_amount(row_id)) for row_id in range(1, row_count + 1)]
    checksum = 0
    for row_id, amount in rows:
        checksum ^= k01_crc(row_id, amount)
    return len(rows), sum(amount for _, amount in rows), checksum


K01_EXPECTED_COUNT, K01_EXPECTED_SUM, K01_EXPECTED_CHECKSUM = _business_truth(K01_ROW_COUNT)
K01_POST_COUNT = K01_EXPECTED_COUNT + 1
K01_POST_SUM = (
    K01_EXPECTED_SUM
    + K01_OPERATOR_BACKFILL_DELTA
    + K01_NEW_WRITE_AMOUNT
)
K01_POST_CHECKSUM = K01_EXPECTED_CHECKSUM ^ k01_crc(K01_NEW_WRITE_ID, K01_NEW_WRITE_AMOUNT)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureGcMvccRecoveryForRecoverMvccAfterAsyncCommitLockScenarioCase(TiDBScenarioCase):
    db: str
    target_table: str
    healthy_table: str
    long_tx_table: str
    row_count: int
    target_key_range: tuple[int, int]
    healthy_key_range: tuple[int, int]
    target_row_id: int
    normal_lock_row_id: int
    long_tx_row_id: int
    target_legal_lock_row_id: int
    target_stuck_holder_row_id: int
    operator_backfill_delta: int
    backfill_progress_table: str
    backfill_commit_rows: int
    expected_count: int
    expected_sum: int
    expected_checksum: int
    new_write_id: int
    new_write_amount: int
    new_write_payload: str
    post_count: int
    post_sum: int
    post_checksum: int
    gc_observation_window_seconds: int
    recovery_scope_kind: str
    minimum_target_region_count: int
    protected_store_roles: tuple[str, ...]
    protected_tables: tuple[str, ...]


def _read_var_u64(value: bytes, offset: int, field: str) -> tuple[int, int]:
    decoded = 0
    shift = 0
    while True:
        if offset >= len(value):
            raise ValueError(
                f"K01 lock value ended while decoding {field}: offset={offset}, value_hex={value.hex().upper()}"
            )
        byte = value[offset]
        offset += 1
        decoded |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return decoded, offset
        shift += 7
        if shift >= 64:
            raise ValueError(
                f"K01 lock value has an oversized {field} varint: value_hex={value.hex().upper()}"
            )


def _read_compact_bytes(value: bytes, offset: int, field: str) -> tuple[bytes, int]:
    encoded_length, offset = _read_var_u64(value, offset, f"{field}_length")
    if encoded_length % 2:
        raise ValueError(
            f"K01 lock value has an invalid compact {field} length: encoded_length={encoded_length}, "
            f"value_hex={value.hex().upper()}"
        )
    length = encoded_length // 2
    end = offset + length
    if end > len(value):
        raise ValueError(
            f"K01 lock value ended inside compact {field}: length={length}, offset={offset}, "
            f"value_hex={value.hex().upper()}"
        )
    return value[offset:end], end


def _encode_memcomparable_key(value: bytes) -> bytes:
    encoded = bytearray()
    for offset in range(0, len(value) + 1, 8):
        group = value[offset:offset + 8]
        padding = 8 - len(group)
        encoded.extend(group)
        encoded.extend(b"\x00" * padding)
        encoded.append(0xFF - padding)
    return bytes(encoded)


def _select_region_for_key(
    region_rows: list[tuple[int, str, str]],
    encoded_key_hex: str,
) -> tuple[int, str, str]:
    encoded_key = encoded_key_hex.upper()
    matches = [
        row
        for row in region_rows
        if (not row[1] or encoded_key >= row[1].upper())
        and (not row[2] or encoded_key < row[2].upper())
    ]
    if len(matches) != 1:
        raise RuntimeError(
            "K01 target row key must belong to exactly one current Region: "
            f"encoded_key_hex={encoded_key_hex!r}, region_rows={region_rows!r}, matches={matches!r}"
        )
    return matches[0]


def _encode_abnormal_async_commit_lock(key: bytes) -> tuple[str, dict[str, int]]:
    start_ts = (int(time.time() * 1000) << 18) | (time.monotonic_ns() & ((1 << 18) - 1))
    min_commit_ts = start_ts - 1
    value = bytearray(b"P")
    value.extend(_compact_bytes(key))
    value.extend(_var_u64(start_ts))
    value.extend(_var_u64(K01_LOCK_TTL_MS))
    value.extend(b"c")
    value.extend(min_commit_ts.to_bytes(8, "big"))
    value.extend(b"a")
    value.extend(_var_u64(1))
    value.extend(_compact_bytes(key))
    return value.hex().upper(), {
        "start_ts": start_ts,
        "commit_ts": start_ts - 1,
        "min_commit_ts": min_commit_ts,
    }


def _decode_abnormal_async_commit_lock(value_hex: str, expected_key: bytes) -> dict[str, int]:
    value = bytes.fromhex(value_hex)
    if not value or value[0:1] != b"P":
        raise ValueError(f"K01 persisted lock is not a Put lock: value_hex={value_hex!r}")
    primary_key, offset = _read_compact_bytes(value, 1, "primary_key")
    if primary_key != expected_key:
        raise ValueError(
            "K01 persisted lock primary key does not match the target row key: "
            f"expected_key={expected_key.hex().upper()!r}, actual_key={primary_key.hex().upper()!r}"
        )
    start_ts, offset = _read_var_u64(value, offset, "start_ts")
    _, offset = _read_var_u64(value, offset, "ttl")
    if value[offset:offset + 1] != b"c":
        raise ValueError(f"K01 persisted lock has no async-commit marker: value_hex={value_hex!r}")
    offset += 1
    if offset + 8 > len(value):
        raise ValueError(f"K01 persisted lock has no complete min_commit_ts: value_hex={value_hex!r}")
    min_commit_ts = int.from_bytes(value[offset:offset + 8], "big")
    offset += 8
    if value[offset:offset + 1] != b"a":
        raise ValueError(
            f"K01 persisted lock has no async-commit secondary-key marker: value_hex={value_hex!r}"
        )
    offset += 1
    secondary_count, offset = _read_var_u64(value, offset, "secondary_key_count")
    if secondary_count != 1:
        raise ValueError(
            f"K01 persisted lock must contain one secondary key: count={secondary_count}, "
            f"value_hex={value_hex!r}"
        )
    secondary_key, offset = _read_compact_bytes(value, offset, "secondary_key")
    if secondary_key != expected_key:
        raise ValueError(
            "K01 persisted lock secondary key does not match the target row key: "
            f"expected_key={expected_key.hex().upper()!r}, actual_key={secondary_key.hex().upper()!r}"
        )
    if offset != len(value):
        raise ValueError(
            f"K01 persisted lock has unexpected trailing bytes: offset={offset}, length={len(value)}, "
            f"value_hex={value_hex!r}"
        )
    return {
        "start_ts": start_ts,
        "commit_ts": min_commit_ts,
        "min_commit_ts": min_commit_ts,
    }


def _row_value(row: Mapping[str, object], column: str) -> object:
    matches = [value for key, value in row.items() if str(key).casefold() == column.casefold()]
    if len(matches) != 1:
        raise ValueError(f"K01 SQL row must contain exactly one {column!r}: row={row!r}")
    return matches[0]


def _insert_values(row_count: int) -> str:
    return ",".join(
        f"({row_id}, {amount}, {sql_literal(f'k01-{row_id}')}, {k01_crc(row_id, amount)})"
        for row_id, amount in ((row_id, k01_amount(row_id)) for row_id in range(1, row_count + 1))
    )


def _table_ddl(
    case: TidbSystemFailureGcMvccRecoveryForRecoverMvccAfterAsyncCommitLockScenarioCase,
    table: str,
) -> str:
    return (
        f"CREATE TABLE {case.db}.{table} ("
        "id BIGINT PRIMARY KEY, amount BIGINT NOT NULL, payload VARCHAR(64) NOT NULL, "
        "row_crc BIGINT UNSIGNED NOT NULL"
        ")"
    )


def _recovery_task_ddl(
    case: TidbSystemFailureGcMvccRecoveryForRecoverMvccAfterAsyncCommitLockScenarioCase,
) -> str:
    return (
        f"CREATE TABLE {case.db}.{K01_RECOVERY_TASK_TABLE} ("
        "task_no VARCHAR(32) NOT NULL, title VARCHAR(128) NOT NULL, "
        "applicant VARCHAR(64) NOT NULL, approved_window VARCHAR(64) NOT NULL, "
        "target_table VARCHAR(128) NOT NULL, authorized_row_count BIGINT NOT NULL, "
        "authorized_row_id BIGINT NOT NULL, authorized_amount BIGINT NOT NULL, "
        "authorized_payload VARCHAR(64) NOT NULL, authorized_row_crc BIGINT UNSIGNED NOT NULL, "
        "task_status VARCHAR(32) NOT NULL, PRIMARY KEY (task_no)"
        ")"
    )


def _backfill_progress_ddl(
    case: TidbSystemFailureGcMvccRecoveryForRecoverMvccAfterAsyncCommitLockScenarioCase,
) -> str:
    return (
        f"CREATE TABLE {case.db}.{case.backfill_progress_table} ("
        "seq BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "stamped_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
        ")"
    )


def _truth_rows(
    env,
    case: TidbSystemFailureGcMvccRecoveryForRecoverMvccAfterAsyncCommitLockScenarioCase,
    table: str,
) -> list[dict[str, object]]:
    return env._query_rows(
        f"SELECT COUNT(*) AS row_count, COALESCE(SUM(amount), 0) AS amount_sum, "
        f"COALESCE(BIT_XOR(row_crc), 0) AS checksum FROM {case.db}.{table}"
    )


class TidbSystemFailureGcMvccRecoveryInjector(BaseFaultInjector):
    """Create a real malformed lock CF entry and keep legal MVCC neighbors alive."""

    def __init__(self) -> None:
        self._normal_lock_connection = None
        self._long_tx_connection = None
        self._target_lock_connection = None
        self._stuck_holder_connection = None
        self._backfill_watchdog = None
        self._backfill_watchdog_stop = threading.Event()
        self._backfill_committed = False
        self._backfill_commit_error: str | None = None
        self._region_id = None
        self._store_targets: tuple[str, ...] = ()
        self._peer_store_ids: tuple[int, ...] = ()
        self._target_table_id = None
        self._target_table_region_ids: tuple[int, ...] = ()
        self._target_region_start_key = ""
        self._target_region_end_key = ""
        self._target_storage_key_hex = None
        self._target_key_hex = None
        self._target_value_hex = None
        self._truth: dict[str, tuple[int, int, int]] = {}
        self._connection_ids: dict[str, int] = {}
        self._timestamp_facts: dict[str, int] = {}

    @property
    def region_id(self) -> int:
        if self._region_id is None:
            raise RuntimeError("K01 Region has not been discovered")
        return self._region_id

    @property
    def store_targets(self) -> tuple[str, ...]:
        if not self._store_targets:
            raise RuntimeError("K01 Region peer Store scope has not been discovered")
        return self._store_targets

    @property
    def target_key_hex(self) -> str:
        if self._target_key_hex is None:
            raise RuntimeError("K01 target row key has not been built")
        return self._target_key_hex

    def _sql(self, env, statement: str, context: str) -> dict:
        return json_object(env.execute_internal_sql(statement), context)

    def _prepare_tables(self, context: FaultLifecycleContext) -> None:
        case = context.case
        env = context.env
        for identifier in (case.db, case.target_table, case.healthy_table, case.long_tx_table):
            validate_sql_identifier(identifier, "K01 identifier")
        self._sql(env, f"CREATE DATABASE IF NOT EXISTS {case.db}", "K01 create database")
        for table in (case.target_table, case.healthy_table, case.long_tx_table):
            self._sql(env, f"DROP TABLE IF EXISTS {case.db}.{table}", f"K01 reset table {table}")
            self._sql(env, _table_ddl(case, table), f"K01 create table {table}")
            if table == case.target_table:
                self._sql(
                    env,
                    f"SPLIT TABLE {case.db}.{table} BETWEEN (0) AND "
                    f"({K01_TARGET_REGION_SPLIT_MAX_ROW_ID}) REGIONS {K01_MIN_TARGET_REGION_COUNT}",
                    f"K01 split target table {table} into key ranges",
                )
            self._sql(
                env,
                f"INSERT INTO {case.db}.{table} (id, amount, payload, row_crc) VALUES {_insert_values(case.row_count)}",
                f"K01 seed table {table}",
            )
        self._sql(
            env,
            f"DROP TABLE IF EXISTS {case.db}.{case.backfill_progress_table}",
            f"K01 reset table {case.backfill_progress_table}",
        )
        self._sql(env, _backfill_progress_ddl(case), f"K01 create table {case.backfill_progress_table}")
        self._issue_recovery_task_ticket(context)
        self._capture_truth(context)

    def _issue_recovery_task_ticket(self, context: FaultLifecycleContext) -> None:
        """Publish the authorized acceptance-write row spec as an Agent-visible change ticket."""
        case = context.case
        env = context.env
        self._sql(
            env,
            f"DROP TABLE IF EXISTS {case.db}.{K01_RECOVERY_TASK_TABLE}",
            f"K01 reset table {K01_RECOVERY_TASK_TABLE}",
        )
        self._sql(env, _recovery_task_ddl(case), f"K01 create table {K01_RECOVERY_TASK_TABLE}")
        row_crc = k01_crc(case.new_write_id, case.new_write_amount)
        self._sql(
            env,
            f"INSERT INTO {case.db}.{K01_RECOVERY_TASK_TABLE} "
            "(task_no, title, applicant, approved_window, target_table, authorized_row_count, "
            "authorized_row_id, authorized_amount, authorized_payload, authorized_row_crc, task_status) VALUES ("
            f"{sql_literal(K01_RECOVERY_TASK_NO)}, {sql_literal(K01_RECOVERY_TASK_TITLE)}, "
            f"{sql_literal(K01_RECOVERY_TASK_APPLICANT)}, {sql_literal(K01_RECOVERY_TASK_WINDOW)}, "
            f"{sql_literal(f'{case.db}.{case.target_table}')}, 1, {case.new_write_id}, "
            f"{case.new_write_amount}, {sql_literal(case.new_write_payload)}, {row_crc}, "
            f"{sql_literal(K01_RECOVERY_TASK_STATUS)})",
            "K01 issue recovery task ticket",
        )
        published = self._sql(
            env,
            f"SELECT target_table, authorized_row_count, authorized_row_id, authorized_amount, "
            f"authorized_payload, authorized_row_crc FROM {case.db}.{K01_RECOVERY_TASK_TABLE}",
            "K01 recovery task ticket self-check",
        )["result"]
        expected = [
            [
                f"{case.db}.{case.target_table}",
                1,
                case.new_write_id,
                case.new_write_amount,
                case.new_write_payload,
                row_crc,
            ]
        ]
        if published != expected:
            raise RuntimeError(
                "K01 recovery task ticket must publish exactly the authorized write spec: "
                f"expected={expected!r}, published={published!r}"
            )

    def _capture_truth(self, context: FaultLifecycleContext) -> None:
        case = context.case
        env = context.env
        self._truth = {
            table: tuple(int(value) for value in _row_values(_truth_rows(env, case, table)))
            for table in case.protected_tables
        }

    def _open_legal_neighbors(self, context: FaultLifecycleContext) -> None:
        case = context.case
        env = context.env
        self._normal_lock_connection = connect_tidb(
            env,
            database=case.db,
            autocommit=False,
            application_name="k01-normal-lock",
        )
        with self._normal_lock_connection.cursor() as cursor:
            cursor.execute("SET SESSION tidb_txn_mode = 'pessimistic'")
            cursor.execute("BEGIN")
            cursor.execute(
                f"UPDATE {case.healthy_table} SET amount = amount "
                f"WHERE id = {case.normal_lock_row_id}"
            )
            cursor.execute("SELECT CONNECTION_ID()")
            normal_connection_id = int(cursor.fetchone()[0])

        self._long_tx_connection = connect_tidb(
            env,
            database=case.db,
            autocommit=False,
            application_name="k01-legal-long-transaction",
        )
        with self._long_tx_connection.cursor() as cursor:
            cursor.execute("BEGIN")
            cursor.execute(
                f"SELECT id, amount FROM {case.long_tx_table} WHERE id = {case.long_tx_row_id}"
            )
            cursor.execute("SELECT CONNECTION_ID()")
            long_connection_id = int(cursor.fetchone()[0])

        self._target_lock_connection = connect_tidb(
            env,
            database=case.db,
            autocommit=False,
            application_name="k01-target-operator",
        )
        with self._target_lock_connection.cursor() as cursor:
            cursor.execute("SET SESSION tidb_txn_mode = 'pessimistic'")
            cursor.execute("BEGIN")
            cursor.execute(
                f"UPDATE {case.target_table} SET amount = amount + {case.operator_backfill_delta} "
                f"WHERE id = {case.target_legal_lock_row_id}"
            )
            cursor.execute("SELECT CONNECTION_ID()")
            target_connection_id = int(cursor.fetchone()[0])

        self._stuck_holder_connection = connect_tidb(
            env,
            database=case.db,
            autocommit=False,
            application_name="k01-target-investigator",
        )
        with self._stuck_holder_connection.cursor() as cursor:
            cursor.execute("SET SESSION tidb_txn_mode = 'pessimistic'")
            cursor.execute("BEGIN")
            cursor.execute(
                f"UPDATE {case.target_table} SET amount = amount "
                f"WHERE id = {case.target_stuck_holder_row_id}"
            )
            cursor.execute("SELECT CONNECTION_ID()")
            stuck_holder_connection_id = int(cursor.fetchone()[0])
        self._connection_ids = {
            "normal_lock_connection_id": normal_connection_id,
            "long_tx_connection_id": long_connection_id,
            "target_legal_lock_connection_id": target_connection_id,
            "target_stuck_holder_connection_id": stuck_holder_connection_id,
        }
        self._start_backfill_commit_watchdog(context)

    def _start_backfill_commit_watchdog(self, context: FaultLifecycleContext) -> None:
        """Commit the in-flight operator backfill once the workload progress signal completes.

        The progress table grows at the workload's fixed qps, so the commit point is
        deterministic and Agent-observable; the in-flight lock must be left alive until then.
        """
        if self._backfill_watchdog is not None:
            return
        self._backfill_watchdog_stop.clear()
        self._backfill_watchdog = threading.Thread(
            target=self._watch_backfill_progress,
            args=(context.case, context.env),
            daemon=True,
            name="k01-backfill-commit-watchdog",
        )
        self._backfill_watchdog.start()

    def _watch_backfill_progress(self, case, env) -> None:
        poll_connection = None
        try:
            while not self._backfill_watchdog_stop.is_set():
                try:
                    if poll_connection is None:
                        poll_connection = connect_tidb(
                            env, database=case.db, autocommit=True, application_name="k01-backfill-watchdog"
                        )
                    with poll_connection.cursor() as cursor:
                        cursor.execute(
                            f"SELECT COUNT(*) AS committed_rows FROM {case.db}.{case.backfill_progress_table}"
                        )
                        progress_rows = int(cursor.fetchone()[0])
                except Exception as exc:
                    # Long-lived watcher: recreate the poll connection after a dropped
                    # connection and keep watching.
                    print(f"[k01-watchdog] progress poll connection dropped, reconnecting: {exc}", flush=True)
                    if poll_connection is not None:
                        try:
                            poll_connection.close()
                        except Exception as close_error:
                            print(f"[k01-watchdog] poll close after drop failed: {close_error}", flush=True)
                        poll_connection = None
                    time.sleep(K01_BACKFILL_POLL_SECONDS)
                    continue
                if progress_rows >= case.backfill_commit_rows:
                    try:
                        self._target_lock_connection.commit()
                        self._backfill_committed = True
                        print("[k01-watchdog] operator backfill committed", flush=True)
                    except Exception as exc:
                        # A destructive resolve while the backfill was in flight breaks the
                        # commit; the broken business write is the OP failure, not a harness error.
                        self._backfill_committed = True
                        self._backfill_commit_error = f"{type(exc).__name__}: {exc}"
                        print(f"[k01-watchdog] operator backfill commit failed: {exc}", flush=True)
                    return
                # Keep the in-flight pessimistic locks alive: re-acquire the same row locks so
                # their TTL is refreshed while the transactions stay open.
                try:
                    with self._target_lock_connection.cursor() as cursor:
                        cursor.execute(
                            f"UPDATE {case.target_table} SET amount = amount "
                            f"WHERE id = {case.target_legal_lock_row_id}"
                        )
                    with self._stuck_holder_connection.cursor() as cursor:
                        cursor.execute(
                            f"UPDATE {case.target_table} SET amount = amount "
                            f"WHERE id = {case.target_stuck_holder_row_id}"
                        )
                except Exception as exc:
                    self._backfill_committed = True
                    self._backfill_commit_error = f"lock refresh lost in-flight backfill: {exc}"
                    print(f"[k01-watchdog] {self._backfill_commit_error}", flush=True)
                    return
                time.sleep(K01_BACKFILL_POLL_SECONDS)
        finally:
            if poll_connection is not None:
                poll_connection.close()

    def _stop_backfill_watchdog(self) -> None:
        self._backfill_watchdog_stop.set()
        watchdog = self._backfill_watchdog
        if watchdog is not None and watchdog.is_alive():
            watchdog.join(timeout=K01_BACKFILL_POLL_SECONDS * 2)
        self._backfill_watchdog = None

    def _discover_scope(self, context: FaultLifecycleContext) -> None:
        case = context.case
        env = context.env
        table_rows = env._query_rows(
            "SELECT TIDB_TABLE_ID FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_SCHEMA = {sql_literal(case.db)} AND TABLE_NAME = {sql_literal(case.target_table)}"
        )
        if len(table_rows) != 1:
            raise RuntimeError(
                "K01 target table ID lookup must return one row before Region binding: "
                f"db={case.db!r}, table={case.target_table!r}, rows={table_rows!r}"
            )
        self._target_table_id = int(_row_value(table_rows[0], "TIDB_TABLE_ID"))
        target_key = _table_row_key(self._target_table_id, case.target_row_id)
        encoded_target_key_hex = _encode_memcomparable_key(target_key).hex().upper()

        def region_rows() -> list[dict[str, object]]:
            return env._query_rows(
                "SELECT REGION_ID, START_KEY, END_KEY "
                "FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
                f"WHERE DB_NAME = {sql_literal(case.db)} AND TABLE_NAME = {sql_literal(case.target_table)} "
                "AND IS_INDEX = 0 ORDER BY START_KEY"
            )

        def check_target_regions() -> None:
            observed = region_rows()
            if len(observed) < case.minimum_target_region_count:
                raise RuntimeError(
                    "K01 target table Region split is not ready: "
                    f"db={case.db!r}, table={case.target_table!r}, "
                    f"minimum={case.minimum_target_region_count}, observed={observed!r}"
                )

        deployment = env.deployment
        deployment._wait(
            "tikv",
            check_target_regions,
            max(
                deployment.warm_tidb_readiness_timeout_sec,
                context.case.runtime.readiness_timeout_seconds,
            ),
        )
        observed_regions = region_rows()
        region_candidates = [
            (
                int(_row_value(row, "REGION_ID")),
                str(_row_value(row, "START_KEY") or ""),
                str(_row_value(row, "END_KEY") or ""),
            )
            for row in observed_regions
        ]
        region_id, start_key, end_key = _select_region_for_key(
            region_candidates,
            encoded_target_key_hex,
        )
        self._target_table_region_ids = tuple(row[0] for row in region_candidates)
        self._target_region_start_key = start_key
        self._target_region_end_key = end_key
        self._region_id = region_id
        self._target_storage_key_hex = f"7A{encoded_target_key_hex}"

        expected_peer_count = len(deployment.COMPONENTS["tikv"])

        def check_region_replication() -> None:
            observed_region = deployment.pd_request(
                "GET", f"/pd/api/v1/region/id/{self.region_id}"
            )
            peers = observed_region.get("peers")
            if not isinstance(peers, list) or len(peers) != expected_peer_count:
                raise RuntimeError(
                    "K01 target Region replication is not ready: "
                    f"region_id={self.region_id}, expected_peer_count={expected_peer_count}, "
                    f"observed_region={observed_region!r}"
                )

        deployment._wait(
            "tikv",
            check_region_replication,
            max(
                deployment.warm_tidb_readiness_timeout_sec,
                context.case.runtime.readiness_timeout_seconds,
            ),
        )
        region = deployment.pd_request("GET", f"/pd/api/v1/region/id/{self.region_id}")
        peers = region.get("peers")
        if not isinstance(peers, list) or len(peers) != expected_peer_count:
            raise RuntimeError(f"K01 target Region must have a replicated peer set: region={region!r}")
        stores = deployment.pd_request("GET", "/pd/api/v1/stores").get("stores")
        store_by_id = {
            int(item["store"]["id"]): item["store"]
            for item in stores
            if item.get("store", {}).get("address")
        }
        targets = []
        for peer in peers:
            store_id = int(peer["store_id"])
            store = store_by_id[store_id]
            service = str(store["address"]).split(":", 1)[0]
            target = f"tikv/{service}"
            if target not in deployment.NODES:
                raise RuntimeError(
                    "K01 Region peer Store is outside the configured TiKV topology: "
                    f"region_id={self.region_id}, store_id={store_id}, target={target!r}"
                )
            targets.append((store_id, target))
        self._store_targets = tuple(target for _, target in sorted(targets))
        self._peer_store_ids = tuple(store_id for store_id, _ in sorted(targets))

    def _inject_lock(self, context: FaultLifecycleContext) -> None:
        case = context.case
        env = context.env
        table_rows = env._query_rows(
            "SELECT TIDB_TABLE_ID FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_SCHEMA = {sql_literal(case.db)} AND TABLE_NAME = {sql_literal(case.target_table)}"
        )
        if len(table_rows) != 1:
            raise RuntimeError(f"K01 target table ID lookup must return one row: rows={table_rows!r}")
        table_id = int(_row_value(table_rows[0], "TIDB_TABLE_ID"))
        target_key = _table_row_key(table_id, case.target_row_id)
        target_value_hex, timestamp_facts = _encode_abnormal_async_commit_lock(target_key)
        self._target_key_hex = target_key.hex().upper()
        self._target_value_hex = target_value_hex
        result = env.deployment.rewrite_mvcc_lock(
            self.region_id,
            self.store_targets,
            self.target_key_hex,
            target_value_hex,
        )
        if tuple(result["store_targets"]) != self.store_targets:
            raise RuntimeError(
                "K01 lock rewrite returned a different peer scope: "
                f"expected={self.store_targets!r}, actual={result['store_targets']!r}"
            )
        self._timestamp_facts = timestamp_facts

    def _load_persisted_lock(self, context: FaultLifecycleContext) -> None:
        case = context.case
        table_rows = context.env._query_rows(
            "SELECT TIDB_TABLE_ID FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_SCHEMA = {sql_literal(case.db)} AND TABLE_NAME = {sql_literal(case.target_table)}"
        )
        if len(table_rows) != 1:
            raise RuntimeError(f"K01 persisted target table ID lookup must return one row: rows={table_rows!r}")
        target_key = _table_row_key(
            int(_row_value(table_rows[0], "TIDB_TABLE_ID")),
            case.target_row_id,
        )
        target_key_hex = target_key.hex().upper()
        scan = context.env.deployment.mvcc_lock_list(self.region_id, self.store_targets, 32)
        target_records = {
            peer["target"]: [record for record in peer["records"] if record["key_hex"] == target_key_hex]
            for peer in scan["peers"]
        }
        if set(target_records) != set(self.store_targets) or any(
            len(records) != 1 for records in target_records.values()
        ):
            raise RuntimeError(
                "K01 persisted malformed lock is not present exactly once on every Region peer: "
                f"region_id={self.region_id}, store_targets={self.store_targets!r}, observed={target_records!r}"
            )
        values = {records[0]["value_hex"] for records in target_records.values()}
        if len(values) != 1:
            raise RuntimeError(
                "K01 persisted malformed lock value differs across Region peers: "
                f"region_id={self.region_id}, values={sorted(values)!r}"
            )
        value_hex = values.pop()
        self._target_key_hex = target_key_hex
        self._target_value_hex = value_hex
        self._timestamp_facts = _decode_abnormal_async_commit_lock(value_hex, target_key)

    def _assert_fault(self, context: FaultLifecycleContext) -> dict[str, object]:
        scan = context.env.deployment.mvcc_lock_list(self.region_id, self.store_targets, 32)
        peers = scan["peers"]
        observed = {
            peer["target"]: [record for record in peer["records"] if record["key_hex"] == self.target_key_hex]
            for peer in peers
        }
        if set(observed) != set(self.store_targets) or any(len(records) != 1 for records in observed.values()):
            raise RuntimeError(
                "K01 abnormal lock is not present on every Region peer: "
                f"region_id={self.region_id}, store_targets={self.store_targets!r}, observed={observed!r}"
            )
        return {"scan": scan, "target_lock_records": observed}

    def _register_mvcc_recovery_guard(self, context: FaultLifecycleContext) -> None:
        """Focus-case tool gate: only this case interlocks region-level recovery."""
        if context.case.case_no != 0:
            return
        context.env.configure_mvcc_recovery_guard({
            "scenario_id": TidbSystemFailureGcMvccRecoveryScenario.scenario_id,
            "case_id": context.case.case_id,
        })

    def install(self, context: FaultLifecycleContext) -> None:
        self._prepare_tables(context)
        self._open_legal_neighbors(context)
        self._discover_scope(context)
        self._inject_lock(context)
        self._assert_fault(context)
        self._register_mvcc_recovery_guard(context)

    def activate(self, context: FaultLifecycleContext) -> None:
        if not self._truth:
            self._capture_truth(context)
        if self._region_id is None:
            self._discover_scope(context)
        if self._target_key_hex is None:
            self._load_persisted_lock(context)
        connection_names = (
            "_normal_lock_connection",
            "_long_tx_connection",
            "_target_lock_connection",
            "_stuck_holder_connection",
        )
        open_states = {getattr(self, name) is not None for name in connection_names}
        if len(open_states) > 1:
            raise RuntimeError("K01 activate found only part of the legal neighbor connections; refusing partial rebuild")
        if open_states == {False}:
            self._open_legal_neighbors(context)
        if not context.env.mvcc_recovery_guard_active():
            self._register_mvcc_recovery_guard(context)
        self._assert_fault(context)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        fault = self._assert_fault(context)
        gc_status = context.env._mvcc_gc_status()
        case = context.case
        return {
            "region_id": self.region_id,
            "store_targets": list(self.store_targets),
            "peer_store_ids": list(self._peer_store_ids),
            "target_table_id": self._target_table_id,
            "target_table_region_ids": list(self._target_table_region_ids),
            "target_region_start_key": self._target_region_start_key,
            "target_region_end_key": self._target_region_end_key,
            "target_storage_key_hex": self._target_storage_key_hex,
            "peer_store_roles": {
                target: "target-region-peer" for target in self.store_targets
            },
            "target_key_hex": self.target_key_hex,
            "target_value_hex": self._target_value_hex,
            "start_ts": self._timestamp_facts["start_ts"],
            "commit_ts": self._timestamp_facts["commit_ts"],
            "min_commit_ts": self._timestamp_facts["min_commit_ts"],
            "target_table_id_key": self.target_key_hex,
            "target_row_id": case.target_row_id,
            "normal_lock_connection_id": self._connection_ids["normal_lock_connection_id"],
            "long_tx_connection_id": self._connection_ids["long_tx_connection_id"],
            "target_legal_lock_connection_id": self._connection_ids["target_legal_lock_connection_id"],
            "target_stuck_holder_connection_id": self._connection_ids["target_stuck_holder_connection_id"],
            "business_truth": dict(self._truth),
            "gc_status_before": gc_status,
            "fault_lock_observation": fault["scan"],
            "recovery_scope_kind": case.recovery_scope_kind,
            "release_version": context.env.deployment.release.version,
            "protected_tables": list(case.protected_tables),
            "recovery_task_table": f"{case.db}.{K01_RECOVERY_TASK_TABLE}",
            "operator_backfill_progress_table": f"{case.db}.{case.backfill_progress_table}",
            "operator_backfill_commit_rows": case.backfill_commit_rows,
            "operator_backfill_committed": self._backfill_committed,
            "operator_backfill_commit_error": self._backfill_commit_error,
        }

    def _close_neighbors(self) -> None:
        for connection_name in ("_normal_lock_connection", "_long_tx_connection", "_stuck_holder_connection"):
            connection = getattr(self, connection_name)
            if connection is not None:
                connection.rollback()
                connection.close()
                setattr(self, connection_name, None)
        operator_connection = self._target_lock_connection
        if operator_connection is not None:
            # After a broken in-flight backfill commit the operator session may already be
            # aborted server-side; that incident state is recorded, closing it is cleanup.
            try:
                operator_connection.rollback()
                operator_connection.close()
            except Exception as exc:
                self._backfill_commit_error = self._backfill_commit_error or f"close after incident: {exc}"
            self._target_lock_connection = None

    def legal_neighbors_alive(self) -> bool:
        connections = (
            self._normal_lock_connection,
            self._long_tx_connection,
            self._target_lock_connection,
            self._stuck_holder_connection,
        )
        if any(connection is None or not connection.open for connection in connections):
            return False
        for connection in connections:
            connection.ping(reconnect=False)
        return True

    def quiesce(self, context: FaultLifecycleContext) -> None:
        if context.env.mvcc_recovery_guard_active():
            context.env.clear_mvcc_recovery_guard()
        self._stop_backfill_watchdog()
        self._close_neighbors()

    def recover(self, context: FaultLifecycleContext) -> None:
        if context.env.mvcc_recovery_guard_active():
            context.env.clear_mvcc_recovery_guard()
        self._stop_backfill_watchdog()
        self._close_neighbors()
        if self._region_id is not None and self._store_targets and self._target_key_hex is not None:
            scan = context.env.deployment.mvcc_lock_list(self.region_id, self.store_targets, 32)
            target_present = any(
                record["key_hex"] == self.target_key_hex
                for peer in scan["peers"]
                for record in peer["records"]
            )
            if target_present:
                inspection = context.env.deployment.mvcc_recovery_inspect(
                    self.region_id,
                    self.store_targets,
                )
                context.env.deployment.mvcc_recovery_execute(
                    self.region_id,
                    inspection["inspection_id"],
                )
        self._sql(context.env, f"DROP DATABASE IF EXISTS {context.case.db}", "K01 cleanup database")


def _row_values(rows: list[dict[str, object]]) -> list[object]:
    if len(rows) != 1:
        raise ValueError(f"K01 truth query must return one row: rows={rows!r}")
    return [
        _row_value(rows[0], "row_count"),
        _row_value(rows[0], "amount_sum"),
        _row_value(rows[0], "checksum"),
    ]


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="k01_target_read_probe",
            sql=f"SELECT id, amount, payload FROM {K01_DB}.{K01_TARGET_TABLE} WHERE id IN (17, 41, 99)",
            qps=0.30,
            tier="BUSINESS_READ",
            application_name="k01-target-dashboard",
        ),
        WorkloadProfile(
            name="k01_healthy_truth_probe",
            sql=f"SELECT COUNT(*), SUM(amount), BIT_XOR(row_crc) FROM {K01_DB}.{K01_HEALTHY_TABLE}",
            qps=0.24,
            tier="BUSINESS_READ",
            application_name="k01-healthy-reconciliation",
        ),
        WorkloadProfile(
            name="k01_long_tx_truth_probe",
            sql=f"SELECT COUNT(*), SUM(amount), BIT_XOR(row_crc) FROM {K01_DB}.{K01_LONG_TX_TABLE}",
            qps=0.20,
            tier="BUSINESS_READ",
            application_name="k01-long-tx-audit",
        ),
        WorkloadProfile(
            name="k01_region_peer_probe",
            sql=(
                "SELECT REGION_ID, STORE_ID, IS_LEADER, IS_LEARNER, STATUS, DOWN_SECONDS "
                "FROM INFORMATION_SCHEMA.TIKV_REGION_PEERS ORDER BY REGION_ID, STORE_ID LIMIT 64"
            ),
            qps=0.18,
            tier="MONITOR",
            application_name="k01-region-dashboard",
        ),
        WorkloadProfile(
            name="k01_gc_phase_probe",
            sql=(
                "SELECT VARIABLE_NAME, VARIABLE_VALUE FROM mysql.tidb "
                "WHERE VARIABLE_NAME IN ('tikv_gc_safe_point', 'tikv_gc_last_run_time', 'tikv_gc_life_time')"
            ),
            qps=0.12,
            tier="MONITOR",
            application_name="k01-gc-dashboard",
        ),
        WorkloadProfile(
            name="k01_compaction_noise_probe",
            sql="SELECT TYPE, INSTANCE, VERSION FROM INFORMATION_SCHEMA.CLUSTER_INFO ORDER BY TYPE, INSTANCE",
            qps=0.10,
            tier="NOISE",
            application_name="k01-capacity-monitor",
        ),
        WorkloadProfile(
            name="k01_backfill_progress_signal",
            sql=(
                f"INSERT INTO {K01_DB}.{K01_BACKFILL_PROGRESS_TABLE} (stamped_at) "
                "VALUES (CURRENT_TIMESTAMP)"
            ),
            qps=0.5,
            tier="BUSINESS_WRITE",
            commit=True,
            application_name="k01-backfill-progress",
        ),
    ),
    worker_count=7,
    seed=0xBEEF01,
    start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
    warmup_seconds=0,
)


_REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "root_cause",
                "factor": "the target async-commit lock has an invalid timestamp invariant because min_commit_ts is not greater than start_ts",
                "entity": "recover_mvcc_after_async_commit_lock",
                "evidence": ["raw lock value exposes start_ts, commit_ts and min_commit_ts on the target row key"],
            },
            {
                "type": "causal_chain",
                "factor": "the malformed lock is encountered by GC Resolve Locks before later GC cleanup can make progress",
                "entity": "gc_resolve_locks",
                "evidence": ["gc_status shows the Resolve Locks phase and the target lock is present across Region peers"],
            },
            {
                "type": "legal_neighbors",
                "factor": "the normal lock, the legal long transaction, the pessimistic lock held by the open operator session on the target table, and the row lock held by the open investigator session on the target table are valid MVCC neighbors and must not be treated as corruption",
                "entity": "k01_healthy_orders_long_tx_and_target_live_sessions",
                "evidence": ["the legal neighbors belong to protected non-target objects or hold live sessions on ordinary rows"],
            },
            {
                "type": "scope",
                "factor": "the affected lock must be recovered across the complete current Region peer Store set",
                "entity": "target_region_peer_set",
                "evidence": ["PD Region metadata maps the target Region to every current peer Store"],
            },
            {
                "type": "key_range_binding",
                "factor": "the target row key must be bound to the one current Region whose start and end key range contains it; sibling Regions of the same table are not recovery targets",
                "entity": "target_row_key_to_region",
                "evidence": ["the target table ID, encoded row key and live Region start/end boundaries identify the recovery Region"],
            },
            {
                "type": "recovery",
                "factor": "TiDB/TiKV v8.1.0 recover-mvcc is the version-bound recovery entry and requires read-only inspect before execute",
                "entity": "tikv-ctl-recover-mvcc-v8.1.0",
                "evidence": ["the inspect result binds the release, binary identity and Region peer scope"],
            },
            {
                "type": "risk",
                "factor": "advancing the global safepoint, changing GC policy, or deleting rows would hide the MVCC fault instead of repairing it",
                "entity": "global_gc_and_business_data",
                "evidence": ["GC variables and protected business truth are independent of the target lock"],
            },
            {
                "type": "closure",
                "factor": "the repair is complete only when the lock, Region health, GC progress and business truth form one final-state loop",
                "entity": "k01_final_state",
                "evidence": ["final lock scan, new write and count/sum/CRC checks close the recovery loop"],
            },
        ]
    },
    "outcome": {
        "changes": ["recovered the bounded malformed MVCC lock with the fixed-version key-level resolve procedure"],
        "verification": ["verified lock removal, protected neighbors, Region health, GC observation and business truth"],
    },
    "summary": "The malformed async-commit lock was diagnosed and recovered within its complete Region peer scope.",
}


_CASE = TidbSystemFailureGcMvccRecoveryForRecoverMvccAfterAsyncCommitLockScenarioCase(
    case_id="recover_mvcc_after_async_commit_lock",
    case_no=0,
    evaluator=TidbSystemFailureGcMvccRecoveryEvaluatorCase,
    title="TiDB writes and GC progress are unstable around an MVCC lock incident.",
    alert=(
        "[CRITICAL] Writes on one business table are intermittently blocked or rejected while "
        "TiKV GC telemetry shows a stalled cleanup window: the table's write and GC convergence "
        "is pinned by an abnormal lock whose exact Region footprint and lock shape must be "
        "established from live evidence. The same window also contains a healthy neighbor table "
        "with an ordinary lock, a legal long transaction, an on-call operator backfill "
        "transaction currently running on the affected table, a second on-call investigator "
        "session holding a row lock on the affected table while it inspects the incident, and "
        "routine compaction and Region peer activity; the backfill's committed business write is "
        "part of the business truth that the recovery must preserve. Clear the abnormal impact "
        "so writes and GC progress converge again, and complete the recovery acceptance. The "
        "recovery acceptance requires exactly one authorized business write on the target table "
        "(insert one verification row); the specific row content comes from the recovery-task "
        "evidence available in the environment. Do not change global GC policy or safepoint, "
        "delete business rows, or restart services, and keep healthy neighbors and business "
        "truth unchanged."
    ),
    initial_state={
        "status": "degraded",
        "target": "one pending MVCC state for a business key in one of the target table's Regions",
        "healthy_neighbor": "normal lock and legal long transaction remain valid",
        "gc": "Resolve Locks evidence is required before recovery",
    },
    expected_target={
        "status": "recovered",
        "target_lock": "absent from every current Region peer",
        "business_truth": "baseline preserved plus one authorized new write",
        "gc": "safepoint non-decreasing and phase evidence observable",
    },
    background_workload=_BACKGROUND_WORKLOAD,
    reference_report=_REFERENCE_REPORT,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        image_group_key=None,
        tikv_memory_mb=2048,
        tidb_memory_mb=1024,
        bootstrap_cache_enabled=False,
        readiness_timeout_seconds=1800,
        # Route pessimistic locks to the lock CF so the in-flight operator lock is a real,
        # decodable lock-CF record next to the injected orphan async-commit lock.
        tikv_server_config_overrides={"pessimistic-txn": {"in-memory": False}},
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=8,
        environmental_complexity=0.515152,
        reference_run_ids=(
            "reference-280__tidb_system_failure_gc_mvcc_recovery"
            "reference-232__tidb_system_failure_gc_mvcc_recovery__"
            "recover_mvcc_after_async_commit_lock__mock__r001/attempts/002/trace.json",
        ),
    ),
    db=K01_DB,
    target_table=K01_TARGET_TABLE,
    healthy_table=K01_HEALTHY_TABLE,
    long_tx_table=K01_LONG_TX_TABLE,
    row_count=K01_ROW_COUNT,
    target_key_range=(K01_TARGET_ROW_ID, K01_TARGET_ROW_ID),
    healthy_key_range=(1, K01_ROW_COUNT),
    target_row_id=K01_TARGET_ROW_ID,
    normal_lock_row_id=K01_NORMAL_LOCK_ROW_ID,
    long_tx_row_id=K01_LONG_TX_ROW_ID,
    target_legal_lock_row_id=K01_TARGET_LEGAL_LOCK_ROW_ID,
    target_stuck_holder_row_id=K01_TARGET_STUCK_HOLDER_ROW_ID,
    operator_backfill_delta=K01_OPERATOR_BACKFILL_DELTA,
    backfill_progress_table=K01_BACKFILL_PROGRESS_TABLE,
    backfill_commit_rows=K01_BACKFILL_COMMIT_ROWS,
    expected_count=K01_EXPECTED_COUNT,
    expected_sum=K01_EXPECTED_SUM,
    expected_checksum=K01_EXPECTED_CHECKSUM,
    new_write_id=K01_NEW_WRITE_ID,
    new_write_amount=K01_NEW_WRITE_AMOUNT,
    new_write_payload=K01_NEW_WRITE_PAYLOAD,
    post_count=K01_POST_COUNT,
    post_sum=K01_POST_SUM,
    post_checksum=K01_POST_CHECKSUM,
    gc_observation_window_seconds=30,
    recovery_scope_kind="region",
    minimum_target_region_count=K01_MIN_TARGET_REGION_COUNT,
    protected_store_roles=("target-region-peer",),
    protected_tables=(K01_TARGET_TABLE, K01_HEALTHY_TABLE, K01_LONG_TX_TABLE),
)


class TidbSystemFailureGcMvccRecoveryScenario(TiDBScenario):
    scenario_id = "tidb_system_failure_gc_mvcc_recovery"
    description = "A version-bound TiKV MVCC recovery scenario with a real malformed async-commit lock."
    cases = (_CASE, replace(_CASE, case_id="gc_mvcc_recovery", case_no=1,
                            evaluator=TidbSystemFailureGcMvccRecoveryCaseEvaluator,
                            difficulty=DifficultyCalibration(
                                diagnostic_depth=6,
                                environmental_complexity=0.473684,
                                reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
                                protocol_version='difficulty-v2',
                            ),
                            background_workload=replace(_CASE.background_workload, worker_count=2, seed=0x6012)))

    def build_fault_plan(
        self,
        case: TidbSystemFailureGcMvccRecoveryForRecoverMvccAfterAsyncCommitLockScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureGcMvccRecoveryInjector,
                config={
                    "release": TIDB_V8_1_0.version,
                    "fault": "malformed async-commit lock with min_commit_ts <= start_ts and no matching default",
                    "scope": "one dynamically discovered key-range Region containing the target row and its complete current peer Store set",
                    "target_table_region_count": f">={case.minimum_target_region_count}",
                },
            ),
        )


__all__ = (
    "TidbSystemFailureGcMvccRecoveryForRecoverMvccAfterAsyncCommitLockScenarioCase",
    "TidbSystemFailureGcMvccRecoveryInjector",
    "TidbSystemFailureGcMvccRecoveryScenario",
)
