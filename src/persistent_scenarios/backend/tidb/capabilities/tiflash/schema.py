"""HTAP isolation business schema for tidb_htap_tiflash_isolation.

Trading and analytics share `htap.orders`; analytics is intended to run on the TiFlash
replica. The public control plane is `htap.analytics_config` (per-connection engine
preference released by the scheduler and audited), `htap.analytics_jobs` (the analysis
queue) and `htap.analytics_result` (delivered analysis artifacts). All values
follow the three-path difficulty calibration.
"""

from __future__ import annotations

HTAP_SCHEMA = "htap"
ORDERS_TABLE = "htap.orders"
TENANT_TABLE = "htap.tenant_orders"
CONFIG_TABLE = "htap.analytics_config"
QUEUE_TABLE = "htap.analytics_jobs"
RESULT_TABLE = "htap.analytics_result"
TRADE_AUDIT = "htap.trade_audit"

HISTORY_ROW_COUNT = 800_000

ENGINE_PREFERENCES = ("auto", "tikv_only", "tiflash_preferred")
# Routing-continuity acceptance set: the published analytics
# template must keep the column-store replica reachable; `tikv_only` is the known-bad
# scheduler release. Both routing-healthy values of the public ENUM are accepted.
ROUTING_HEALTHY_PREFERENCES = ("auto", "tiflash_preferred")
TENANT_TEMPLATE_CONFIG_KEY = "tenant_engine_preference"

# Tenant slice (t=58): the tenant's initial data is a real,
# deterministic slice of the shared orders; the table is created with
# CREATE TABLE LIKE, which does NOT inherit the TiFlash replica, and the onboarding
# pipeline defers the replica attachment while the node is under maintenance.
TENANT_SLICE_MODULUS = 20


def provision_statements() -> tuple[str, ...]:
    return (
        "CREATE DATABASE IF NOT EXISTS htap;",
        f"""CREATE TABLE IF NOT EXISTS {ORDERS_TABLE} (
  order_id BIGINT NOT NULL,
  user_id INT NOT NULL,
  item_id INT NOT NULL,
  region_id INT NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  status VARCHAR(16) NOT NULL,
  created_at DATETIME NOT NULL,
  PRIMARY KEY (order_id)
);""",
        f"""CREATE TABLE IF NOT EXISTS {CONFIG_TABLE} (
  config_key VARCHAR(32) PRIMARY KEY,
  config_value VARCHAR(64) NOT NULL
);""",
        f"""CREATE TABLE IF NOT EXISTS {QUEUE_TABLE} (
  job_id VARCHAR(64) PRIMARY KEY,
  job_kind VARCHAR(16) NOT NULL,
  report_id VARCHAR(64) NULL,
  snapshot_marker BIGINT NULL,
  sql_text TEXT,
  submit_at DOUBLE NOT NULL,
  deadline DOUBLE NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'queued',
  attempts INT NOT NULL DEFAULT 0,
  claimed_by VARCHAR(64) NULL,
  claim_conn_id BIGINT NULL,
  cancel_requested BOOLEAN NOT NULL DEFAULT FALSE,
  not_before DOUBLE NULL,
  priority INT NOT NULL DEFAULT 50,
  result_digest VARCHAR(128) NULL
);""",
        f"""CREATE TABLE IF NOT EXISTS {RESULT_TABLE} (
  job_id VARCHAR(64) PRIMARY KEY,
  report_id VARCHAR(64) NOT NULL,
  snapshot_marker BIGINT NOT NULL,
  delivered_at DOUBLE NOT NULL,
  row_count INT NOT NULL,
  engine_used VARCHAR(32) NOT NULL,
  result_digest VARCHAR(128) NOT NULL
);""",
        f"""CREATE TABLE IF NOT EXISTS {TRADE_AUDIT} (
  audit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  at_monotonic DOUBLE NOT NULL,
  config_key VARCHAR(32) NOT NULL,
  old_value VARCHAR(64) NOT NULL,
  new_value VARCHAR(64) NOT NULL
);""",
        f"INSERT INTO {CONFIG_TABLE} (config_key, config_value) "
        "SELECT 'engine_preference', 'auto' FROM DUAL WHERE NOT EXISTS "
        "(SELECT 1 FROM htap.analytics_config WHERE config_key = 'engine_preference');",
        f"INSERT INTO {CONFIG_TABLE} (config_key, config_value) "
        "SELECT 'dashboard_enabled', 'true' FROM DUAL WHERE NOT EXISTS "
        "(SELECT 1 FROM htap.analytics_config WHERE config_key = 'dashboard_enabled');",
        f"INSERT INTO {CONFIG_TABLE} (config_key, config_value) "
        "SELECT 'analysis_enabled', 'true' FROM DUAL WHERE NOT EXISTS "
        "(SELECT 1 FROM htap.analytics_config WHERE config_key = 'analysis_enabled');",
    )


ANALYSIS_REPORT_SQL = (
    "SELECT region_id, DATE(created_at) AS day, SUM(amount) AS amount, COUNT(*) AS orders "
    "FROM htap.orders GROUP BY region_id, DATE(created_at) ORDER BY region_id, day"
)


def analysis_report_sql(max_order_id: int) -> str:
    """Snapshot-bound analysis truth (results bind to their declared
    snapshot). `max_order_id` is the declared snapshot marker (order count at submit;
    ids are contiguous: history 1..N, trades insert MAX(order_id)+1)."""
    max_order_id = int(max_order_id)
    if max_order_id < 0:
        raise ValueError(f"snapshot marker must be non-negative: max_order_id={max_order_id}")
    return ANALYSIS_REPORT_SQL.replace(
        "FROM htap.orders ", f"FROM htap.orders WHERE order_id <= {max_order_id} ", 1
    )


TENANT_ANALYSIS_SQL = (
    "SELECT region_id, DATE(created_at) AS day, SUM(amount) AS amount, COUNT(*) AS orders "
    "FROM htap.tenant_orders GROUP BY region_id, DATE(created_at) ORDER BY region_id, day"
)


def tenant_analysis_sql(max_order_id: int) -> str:
    """Snapshot-bound tenant analysis truth over the tenant's own table (the tenant
    template pins reads to the column-store replica, so this query is the recurrence
    surface for a missing placement attachment)."""
    max_order_id = int(max_order_id)
    if max_order_id < 0:
        raise ValueError(f"snapshot marker must be non-negative: max_order_id={max_order_id}")
    return TENANT_ANALYSIS_SQL.replace(
        "FROM htap.tenant_orders ", f"FROM htap.tenant_orders WHERE order_id <= {max_order_id} ", 1
    )


DASHBOARD_SQL_TEMPLATE = (
    "SELECT region_id, COUNT(*) AS orders, SUM(amount) AS amount FROM htap.orders "
    "WHERE created_at >= '{{since_ts}}' GROUP BY region_id ORDER BY region_id"
)
