"""Warehouse business schema and batch contracts for tidb_olap_warehouse_delivery.

The `wh.*` schema is the business surface of the periodic warehouse delivery service:
order facts land in `wh.orders` per batch, report jobs run from the public queue table
`wh.warehouse_jobs`, and the scheduler releases configuration through
`wh.warehouse_config` (audited in `wh.config_audit`). All values follow the
three-path difficulty calibration.
"""

from __future__ import annotations

from dataclasses import dataclass

SCHEMA = "wh"
FACT_TABLE = "wh.orders"
BATCH_REGISTRY = "wh.batch_registry"
QUEUE_TABLE = "wh.warehouse_jobs"
CONFIG_TABLE = "wh.warehouse_config"
CONFIG_AUDIT = "wh.config_audit"
REPORT_RESULT = "wh.report_result"

HISTORY_BATCH_ID = 0
BATCH_A_ID = 1
BATCH_B_ID = 2

# Row counts: tuned against measured INSERT SELECT
# throughput on the v8.1.0 experiment cluster so one batch ingests well inside
# its candidate 600s deadline while still saturating TiKV resources.
HISTORY_ROW_COUNT = 1_000_000
BATCH_ROW_COUNT = 400_000

# Region skew: batch A concentrates on the low-numbered regions (t=15),
# batch B shifts the skew onto a different region group (t=60).
BATCH_A_SKEW_REGIONS = (1, 2, 3)
BATCH_A_SKEW_SHARE = 0.66
BATCH_B_SKEW_REGIONS = (8, 9, 10)
BATCH_B_SKEW_SHARE = 0.60

# Correction wave (t=26): the upstream re-delivers a corrected
# window covering both staged batches. The correction rewrites unit_price /
# unit_cost / amount on a deterministic subset of each stage table and atomically
# re-publishes batch A into the fact table, so batch-A report truth changes
# mid-run and report deliveries over superseded inputs are honestly incomplete.
CORRECTION_PRICE_FACTOR = 1.06
CORRECTION_COST_FACTOR = 0.97
CORRECTION_ROW_MODULUS = 8  # corrected subset: order_id % 8 == 0

REGION_COUNT = 12
WAREHOUSE_COUNT = 40
ITEM_COUNT = 400
CHANNELS = ("app", "web", "pos")

STAGE_BATCHES = (
    ("1", "wh.stage_batch_a"),
    ("2", "wh.stage_batch_b"),
)


@dataclass(frozen=True, slots=True)
class BatchSpec:
    batch_id: int
    stage_table: str
    row_count: int
    skew_regions: tuple[int, ...]
    skew_share: float
    note: str


BATCH_SPECS = (
    BatchSpec(BATCH_A_ID, "wh.stage_batch_a", BATCH_ROW_COUNT, BATCH_A_SKEW_REGIONS, BATCH_A_SKEW_SHARE, "region_skew_east"),
    BatchSpec(BATCH_B_ID, "wh.stage_batch_b", BATCH_ROW_COUNT, BATCH_B_SKEW_REGIONS, BATCH_B_SKEW_SHARE, "region_skew_south"),
)


def stage_spec(batch_id: int) -> BatchSpec:
    for spec in BATCH_SPECS:
        if spec.batch_id == batch_id:
            return spec
    raise KeyError(f"no staged batch is provisioned for ingest: batch_id={batch_id}, provisioned={[s.batch_id for s in BATCH_SPECS]!r}")


def provision_statements() -> tuple[str, ...]:
    """Idempotent business schema: facts, dimensions, staging, control tables."""
    fact_columns = (
        "order_id BIGINT NOT NULL, batch_id INT NOT NULL, region_id INT NOT NULL, "
        "warehouse_id INT NOT NULL, item_id INT NOT NULL, channel VARCHAR(8) NOT NULL, "
        "quantity INT NOT NULL, unit_price DECIMAL(10,2) NOT NULL, unit_cost DECIMAL(10,2) NOT NULL, "
        "amount DECIMAL(12,2) NOT NULL, order_ts DATETIME NOT NULL"
    )
    return (
        "CREATE DATABASE IF NOT EXISTS wh;",
        "CREATE TABLE IF NOT EXISTS wh.dim_region ("
        "region_id INT PRIMARY KEY, region_name VARCHAR(64) NOT NULL, group_name VARCHAR(32) NOT NULL);",
        "CREATE TABLE IF NOT EXISTS wh.dim_warehouse ("
        "warehouse_id INT PRIMARY KEY, region_id INT NOT NULL, name VARCHAR(64) NOT NULL);",
        f"CREATE TABLE IF NOT EXISTS {FACT_TABLE} ({fact_columns}, PRIMARY KEY (order_id));",
        "CREATE TABLE IF NOT EXISTS wh.stage_batch_a ("
        f"{fact_columns.replace('order_id BIGINT NOT NULL', 'order_id BIGINT')});",
        "CREATE TABLE IF NOT EXISTS wh.stage_batch_b ("
        f"{fact_columns.replace('order_id BIGINT NOT NULL', 'order_id BIGINT')});",
        f"""CREATE TABLE IF NOT EXISTS {QUEUE_TABLE} (
  job_id VARCHAR(64) PRIMARY KEY,
  job_type VARCHAR(16) NOT NULL,
  report_id VARCHAR(64) NULL,
  batch_cutoff INT NULL,
  sql_text TEXT,
  submit_at DOUBLE NOT NULL,
  deadline DOUBLE NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'queued',
  attempts INT NOT NULL DEFAULT 0,
  claimed_by VARCHAR(64) NULL,
  claim_conn_id BIGINT NULL,
  claim_started_at DOUBLE NULL,
  cancel_requested BOOLEAN NOT NULL DEFAULT FALSE,
  priority INT NOT NULL DEFAULT 50,
  result_digest VARCHAR(128) NULL
);""",
        f"""CREATE TABLE IF NOT EXISTS {CONFIG_TABLE} (
  id INT PRIMARY KEY,
  max_workers INT NOT NULL,
  report_memory_quota_mb INT NOT NULL,
  analytics_enabled BOOLEAN NOT NULL,
  ingest_enabled BOOLEAN NOT NULL
);""",
        f"""CREATE TABLE IF NOT EXISTS {CONFIG_AUDIT} (
  audit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  changed_at DOUBLE NOT NULL,
  table_name VARCHAR(64) NOT NULL,
  old_row TEXT NOT NULL,
  new_row TEXT NOT NULL
);""",
        f"""CREATE TABLE IF NOT EXISTS {BATCH_REGISTRY} (
  batch_id INT PRIMARY KEY,
  skew_note VARCHAR(64) NOT NULL,
  analyze_after_ingest BOOLEAN NOT NULL DEFAULT TRUE,
  reports_held BOOLEAN NOT NULL DEFAULT FALSE,
  republished_at DOUBLE NULL,
  ingest_started_at DOUBLE NULL,
  ingest_finished_at DOUBLE NULL,
  analyzed_at DOUBLE NULL,
  row_count BIGINT NULL
);""",
        f"""CREATE TABLE IF NOT EXISTS {REPORT_RESULT} (
  job_id VARCHAR(64) PRIMARY KEY,
  report_id VARCHAR(64) NOT NULL,
  batch_cutoff INT NOT NULL,
  delivered_at DOUBLE NOT NULL,
  row_count INT NOT NULL,
  result_digest VARCHAR(128) NOT NULL
);""",
        f"INSERT INTO {CONFIG_TABLE} (id, max_workers, report_memory_quota_mb, analytics_enabled, ingest_enabled) "
        "SELECT 1, 2, 512, TRUE, TRUE FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM " + CONFIG_TABLE + " WHERE id = 1);",
        # Report hold: batch A ships with its report deliveries
        # gated - the upstream correction wave is announced for its window, so the
        # scheduler holds the batch's report class until an operator releases it.
        f"UPDATE {BATCH_REGISTRY} SET reports_held = TRUE WHERE batch_id = {BATCH_A_ID};",
    )
