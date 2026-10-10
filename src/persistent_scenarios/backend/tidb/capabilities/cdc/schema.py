"""Business data construction for tidb_cdc_downstream_freshness.

The upstream TiDB order store receives a continuous paid-order stream; the
independent downstream MySQL read model serves the fulfilment service. Every
order carries an end-to-end business marker so source commits and downstream
visibility can be paired by (business key, version) without trusting
changefeed checkpoints. Schema DDL is version-fixed and executed by the
trusted driver/capability surface only.
"""

from __future__ import annotations

from dataclasses import dataclass

UPSTREAM_DATABASE = "fulfil"
DOWNSTREAM_DATABASE = "fulfil"
OPS_DATABASE = "ops"
ORDERS_TABLE = "orders"
BATCH_TABLE = "fulfilment_batches"
BATCH_CONTROL_TABLE = "batch_control"
TRAFFIC_CONTROL_TABLE = "cdc_traffic_control"
MAINTENANCE_LOG_TABLE = "maintenance_log"

ORDERS_COLUMNS = (
    "order_id BIGINT PRIMARY KEY,"
    " version INT NOT NULL,"
    " state VARCHAR(16) NOT NULL,"
    " amount DECIMAL(12,2) NOT NULL,"
    " marker VARCHAR(64) NOT NULL,"
    " updated_at DATETIME(3) NOT NULL"
)

STATE_CREATED = "created"
STATE_PAID = "paid"


@dataclass(frozen=True, slots=True)
class CdcSchemaStatements:
    """Ordered DDL for one side of the CDC topology."""

    upstream: tuple[str, ...]
    downstream: tuple[str, ...]


def create_database_statement(database: str) -> str:
    return f"CREATE DATABASE IF NOT EXISTS {database}"


def schema_statements() -> CdcSchemaStatements:
    upstream = (
        create_database_statement(OPS_DATABASE),
        create_database_statement(UPSTREAM_DATABASE),
        f"CREATE TABLE IF NOT EXISTS {UPSTREAM_DATABASE}.{ORDERS_TABLE} ({ORDERS_COLUMNS})",
        f"CREATE TABLE IF NOT EXISTS {OPS_DATABASE}.{TRAFFIC_CONTROL_TABLE} ("
        "id INT PRIMARY KEY,"
        " target_orders_per_sec DOUBLE NOT NULL,"
        " note VARCHAR(255) NOT NULL,"
        " updated_at DATETIME(3) NOT NULL)",
        f"INSERT INTO {OPS_DATABASE}.{TRAFFIC_CONTROL_TABLE} "
        "(id, target_orders_per_sec, note, updated_at) VALUES "
        "(1, 4.0, 'baseline arrival', NOW(3))",
        f"CREATE TABLE IF NOT EXISTS {OPS_DATABASE}.{MAINTENANCE_LOG_TABLE} ("
        "run_id BIGINT PRIMARY KEY,"
        " task VARCHAR(64) NOT NULL,"
        " started_at DATETIME(3) NOT NULL,"
        " finished_at DATETIME(3) NULL,"
        " duration_seconds DOUBLE NULL,"
        " status VARCHAR(16) NOT NULL)",  # the nightly upstream maintenance audit trail
    )
    downstream = (
        create_database_statement(DOWNSTREAM_DATABASE),
        # The feed replicates every upstream database, so the downstream
        # mirror needs the ops control-plane schema (traffic control +
        # maintenance audit) that the upstream statements create before the
        # feed exists; without it the resumed backlog fails with
        # "Unknown database 'ops'" and the checkpoint freezes again.
        create_database_statement(OPS_DATABASE),
        f"CREATE TABLE IF NOT EXISTS {OPS_DATABASE}.{TRAFFIC_CONTROL_TABLE} ("
        "id INT PRIMARY KEY,"
        " target_orders_per_sec DOUBLE NOT NULL,"
        " note VARCHAR(255) NOT NULL,"
        " updated_at DATETIME(3) NOT NULL)",
        f"CREATE TABLE IF NOT EXISTS {OPS_DATABASE}.{MAINTENANCE_LOG_TABLE} ("
        "run_id BIGINT PRIMARY KEY,"
        " task VARCHAR(64) NOT NULL,"
        " started_at DATETIME(3) NOT NULL,"
        " finished_at DATETIME(3) NULL,"
        " duration_seconds DOUBLE NULL,"
        " status VARCHAR(16) NOT NULL)",
        f"CREATE TABLE IF NOT EXISTS {DOWNSTREAM_DATABASE}.{ORDERS_TABLE} ({ORDERS_COLUMNS})",
        f"CREATE TABLE IF NOT EXISTS {DOWNSTREAM_DATABASE}.{BATCH_TABLE} ("
        "batch_id BIGINT PRIMARY KEY,"
        " batch_no INT NOT NULL,"
        " payload VARBINARY(2048) NOT NULL,"
        " created_at DATETIME(3) NOT NULL)",
        f"CREATE TABLE IF NOT EXISTS {DOWNSTREAM_DATABASE}.{BATCH_CONTROL_TABLE} ("
        "id INT PRIMARY KEY,"
        " enabled TINYINT NOT NULL,"
        " batch_rows INT NOT NULL,"
        " batch_pause_seconds DOUBLE NOT NULL,"
        " note VARCHAR(255) NOT NULL,"
        " updated_at DATETIME(3) NOT NULL)",
        f"INSERT INTO {DOWNSTREAM_DATABASE}.{BATCH_CONTROL_TABLE} "
        "(id, enabled, batch_rows, batch_pause_seconds, note, updated_at) VALUES "
        "(1, 0, 2000, 5.0, 'batch window closed', NOW(3))",
    )
    return CdcSchemaStatements(upstream=upstream, downstream=downstream)


def seed_order_rows(count: int, *, start_order_id: int = 1) -> str:
    """Seed historical paid orders on both sides (initial state, not replicated)."""
    values = ",".join(
        f"({order_id}, 2, '{STATE_PAID}', {order_id % 500 + 1}.25, "
        f"'seed-{order_id:08d}', NOW(3))"
        for order_id in range(start_order_id, start_order_id + count)
    )
    return (
        f"INSERT INTO {UPSTREAM_DATABASE}.{ORDERS_TABLE} "
        "(order_id, version, state, amount, marker, updated_at) VALUES "
    ) + values


def marker_for(order_id: int, version: int, committed_at_monotonic: float) -> str:
    """Deterministic per-commit business marker (ledger-independent)."""
    return f"m{order_id:09d}-v{version:03d}-{int(committed_at_monotonic * 1000):013d}"


def order_row_digest(order_id: int, version: int, state: str, amount: str, marker: str) -> str:
    """Stable digest of one business row used for pairing and hole checks."""
    return f"{order_id}:{version}:{state}:{amount}:{marker}"
