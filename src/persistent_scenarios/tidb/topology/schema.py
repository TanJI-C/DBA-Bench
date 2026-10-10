"""Business schema for the online topology change instance.

Reuses the hotspot trade schema (same order/inventory service) and adds the
maintenance work-order control plane plus the placement-policy target table.
The ``maintenance_learner`` placement policy itself is published by the
change-plan capability (with its real-world label drift), not by DDL here.
"""

from __future__ import annotations

from ..hotspot.schema import DDL_STATEMENTS as TRADE_DDL_STATEMENTS
from ..hotspot.schema import (
    DATABASE,
    OPS_DATABASE,
    INITIAL_CLIENT_POLICY,
    initial_client_config_statement,
    price_cents_for_sku,
    seed_inventory_statements,
    seed_snapshot,
)

MAINTENANCE_ORDERS_DDL = """
CREATE TABLE IF NOT EXISTS ops.maintenance_orders (
    order_id VARCHAR(64) NOT NULL,
    deliverable_id VARCHAR(64) NOT NULL,
    kind VARCHAR(32) NOT NULL,
    target VARCHAR(64) NOT NULL,
    deadline_seconds INT NOT NULL,
    published_at_ms BIGINT NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'published',
    PRIMARY KEY (order_id, deliverable_id)
)
"""

MAINTENANCE_TRACKING_DDL = """
CREATE TABLE IF NOT EXISTS ops.maintenance_tracking (
    id INT PRIMARY KEY,
    note VARCHAR(128) NOT NULL
)
"""

DDL_STATEMENTS = TRADE_DDL_STATEMENTS + (MAINTENANCE_ORDERS_DDL, MAINTENANCE_TRACKING_DDL)

MAINTENANCE_TRACKING_SEED = "INSERT INTO ops.maintenance_tracking (id, note) VALUES (1, 'topology change tracking row')"

READ_MAINTENANCE_ORDERS_SQL = (
    "SELECT order_id, deliverable_id, kind, target, deadline_seconds, published_at_ms "
    "FROM ops.maintenance_orders WHERE status = 'published' ORDER BY published_at_ms, deliverable_id"
)

SHOW_PLACEMENT_SQL = "SHOW PLACEMENT FOR TABLE ops.maintenance_tracking"

__all__ = [
    "DATABASE",
    "OPS_DATABASE",
    "INITIAL_CLIENT_POLICY",
    "DDL_STATEMENTS",
    "MAINTENANCE_TRACKING_SEED",
    "READ_MAINTENANCE_ORDERS_SQL",
    "SHOW_PLACEMENT_SQL",
    "initial_client_config_statement",
    "price_cents_for_sku",
    "seed_inventory_statements",
    "seed_snapshot",
]
