"""Business schema and seed data for the OLTP hotspot instance.

TiDB dialect (v8.1.0). All monetary and timestamp values are integers so the
conservation verifiers compare exact business truth without timezone or
decimal parsing. ``idempotency_key`` carries the client retry identity: an
uncertain commit is reconciled through it, never inferred from a timeout.
"""

from __future__ import annotations

from typing import Mapping

DATABASE = "shop"
OPS_DATABASE = "ops"

PROMO_GROUP_A = tuple(f"SKU-{index:04d}" for index in range(0, 5))
PROMO_GROUP_B = tuple(f"SKU-{index:04d}" for index in range(10, 15))
FLASH_SALE_SKU = "SKU-0000"
NORMAL_SKU_COUNT = 20
SEED_INVENTORY_PER_SKU = 2000
SEED_PRICE_CENTS = {f"SKU-{index:04d}": 1000 + index * 250 for index in range(NORMAL_SKU_COUNT)}

INITIAL_CLIENT_POLICY = {
    "id": 1,
    "config_version": 1,
    "request_timeout_ms": 3000,
    "max_retries": 3,
    "retry_backoff_ms": 100,
    "retry_jitter_ms": 50,
    "max_connection_lifetime_seconds": 60,
    "connect_bias": None,
    "lock_wait_timeout_seconds": 8,
    "order_id_prefix": None,
    "settlement_paused": 0,
}

ORDERS_DDL = """
CREATE TABLE IF NOT EXISTS shop.orders (
    order_id VARCHAR(64) PRIMARY KEY,
    sku VARCHAR(16) NOT NULL,
    qty INT NOT NULL,
    amount_cents INT NOT NULL,
    status ENUM('placed','paid') NOT NULL DEFAULT 'placed',
    idempotency_key VARCHAR(64) NOT NULL,
    created_at_ms BIGINT NOT NULL
)
"""

PAYMENTS_DDL = """
CREATE TABLE IF NOT EXISTS shop.payments (
    order_id VARCHAR(64) PRIMARY KEY,
    amount_cents INT NOT NULL,
    paid_at_ms BIGINT NOT NULL
)
"""

INVENTORY_DDL = """
CREATE TABLE IF NOT EXISTS shop.inventory (
    sku VARCHAR(16) PRIMARY KEY,
    qty_available INT NOT NULL
)
"""

CLIENT_CONFIG_DDL = """
CREATE TABLE IF NOT EXISTS ops.client_config (
    id INT PRIMARY KEY,
    config_version INT NOT NULL,
    request_timeout_ms INT NOT NULL,
    max_retries INT NOT NULL,
    retry_backoff_ms INT NOT NULL,
    retry_jitter_ms INT NOT NULL,
    max_connection_lifetime_seconds INT NOT NULL,
    connect_bias VARCHAR(32) NULL,
    lock_wait_timeout_seconds INT NOT NULL,
    order_id_prefix VARCHAR(16) NULL COMMENT '部署前缀：客户端以其截断部署标识生成订单号（前缀-o+8位序号）；为空=使用完整部署标识。发布新 config_version 后生效',
    settlement_paused TINYINT NOT NULL DEFAULT 0 COMMENT '结算批处理暂停标志：1=当前结算事务结束后不再开始新事务；0=继续批处理队列。结算客户端在每个结算项开始前读取'
)
"""

DDL_STATEMENTS = (ORDERS_DDL, PAYMENTS_DDL, INVENTORY_DDL, CLIENT_CONFIG_DDL)


def seed_inventory_statements() -> tuple[str, ...]:
    return tuple(
        f"INSERT INTO shop.inventory (sku, qty_available) VALUES ('{sku}', {SEED_INVENTORY_PER_SKU})"
        for sku in sorted(SEED_PRICE_CENTS)
    )


def initial_client_config_statement() -> str:
    policy = INITIAL_CLIENT_POLICY
    bias = "NULL" if policy["connect_bias"] is None else f"'{policy['connect_bias']}'"
    prefix = "NULL" if policy["order_id_prefix"] is None else f"'{policy['order_id_prefix']}'"
    return (
        f"INSERT INTO ops.client_config (id, config_version, request_timeout_ms, max_retries, "
        f"retry_backoff_ms, retry_jitter_ms, max_connection_lifetime_seconds, connect_bias, "
        f"lock_wait_timeout_seconds, order_id_prefix, settlement_paused) "
        f"VALUES ({policy['id']}, {policy['config_version']}, {policy['request_timeout_ms']}, "
        f"{policy['max_retries']}, {policy['retry_backoff_ms']}, {policy['retry_jitter_ms']}, "
        f"{policy['max_connection_lifetime_seconds']}, {bias}, "
        f"{policy['lock_wait_timeout_seconds']}, {prefix}, {policy['settlement_paused']})"
    )


def price_cents_for_sku(sku: str) -> int:
    if sku not in SEED_PRICE_CENTS:
        raise ValueError(f"unknown SKU has no seeded price: sku={sku!r}, known={sorted(SEED_PRICE_CENTS)!r}")
    return SEED_PRICE_CENTS[sku]


def seed_snapshot() -> Mapping[str, int]:
    return {sku: SEED_INVENTORY_PER_SKU for sku in sorted(SEED_PRICE_CENTS)}
