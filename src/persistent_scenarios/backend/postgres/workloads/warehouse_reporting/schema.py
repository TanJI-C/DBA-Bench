"""Warehouse schema, batch skew payloads and provisioning for pg_warehouse_batch_reporting.

The fact model, skew parameters and control tables are frozen by the instance design;
the row counts and skew shapes are the calibrated batch scale.
"""

from __future__ import annotations

from dataclasses import dataclass


SCHEMA_NAME = "wh"
FACT_TABLE = "wh.batch_sales"
STAGE_A_TABLE = "wh.stage_batch_a"
STAGE_B_TABLE = "wh.stage_batch_b"
CONSUMER_SUMMARY_TABLE = "wh.consumer_batch_summary"

# The downstream consumer's hot-item band: the hot_item_range report
# consumes item_sk BETWEEN 101 AND 250, so the staging profile records how many
# distinct items each batch contributes to that band.
CONSUMER_HOT_BAND_LOW = 101
CONSUMER_HOT_BAND_HIGH = 250

HISTORY_BATCH_ID = 0
BATCH_A_ID = 1
BATCH_B_ID = 2

# Scale basis: the fact volume is sized for minutes-scale healthy report
# runtimes (band 1.5-8min). At smaller volumes (3 history copies, 3M-row
# batches) reports finish in 10-100s and no contract mechanism can bind
# against the 600-840s deadlines.
HISTORY_COPY_COUNT = 12
BATCH_ROW_COUNT = 12_000_000


@dataclass(frozen=True, slots=True)
class BatchStageSpec:
    """Deterministic staged batch payload with a baked-in single-dimension skew."""

    batch_id: int
    stage_table: str
    row_count: int
    dimension: str  # "item" | "customer"
    hot_row_modulus: int  # rows with g % modulus < hot_rows_per_group are hot
    hot_rows_per_group: int
    hot_value_base: int
    hot_value_span: int
    cold_value_base: int
    cold_value_span: int

    def __post_init__(self) -> None:
        if self.dimension not in {"item", "customer"}:
            raise ValueError(f"batch stage skew dimension must be item or customer: dimension={self.dimension!r}")
        if not 0 < self.hot_rows_per_group < self.hot_row_modulus:
            raise ValueError(
                "batch stage hot share must be inside (0, 1): "
                f"stage_table={self.stage_table!r}, hot_rows_per_group={self.hot_rows_per_group}, "
                f"hot_row_modulus={self.hot_row_modulus}"
            )

    @property
    def skew_kind(self) -> str:
        return f"{self.dimension}_skew"


BATCH_A_STAGE = BatchStageSpec(
    batch_id=BATCH_A_ID,
    stage_table=STAGE_A_TABLE,
    row_count=BATCH_ROW_COUNT,
    dimension="item",
    hot_row_modulus=3,
    hot_rows_per_group=2,
    hot_value_base=101,
    hot_value_span=150,
    cold_value_base=20001,
    cold_value_span=80000,
)

BATCH_B_STAGE = BatchStageSpec(
    batch_id=BATCH_B_ID,
    stage_table=STAGE_B_TABLE,
    row_count=BATCH_ROW_COUNT,
    dimension="customer",
    hot_row_modulus=10,
    hot_rows_per_group=6,
    hot_value_base=501,
    hot_value_span=50,
    cold_value_base=5001,
    cold_value_span=195000,
)

STAGE_BATCHES = (BATCH_A_STAGE, BATCH_B_STAGE)


def _skew_expression(spec: BatchStageSpec) -> str:
    return (
        f"CASE WHEN g % {spec.hot_row_modulus} < {spec.hot_rows_per_group} "
        f"THEN {spec.hot_value_base} + (g % {spec.hot_value_span}) "
        f"ELSE {spec.cold_value_base} + (g % {spec.cold_value_span}) END"
    )


def stage_build_sql(spec: BatchStageSpec) -> str:
    """Create one staged batch payload table; deterministic and re-runnable after TRUNCATE."""
    if spec.dimension == "item":
        item_expr = _skew_expression(spec)
        customer_expr = "1 + (g % 200000)"
    else:
        item_expr = "2001 + (g % 100000)"
        customer_expr = _skew_expression(spec)
    return (
        f"CREATE TABLE {spec.stage_table} AS\n"
        f"SELECT g AS stage_line_id,\n"
        f"       2451000 + (g % 730) AS sold_date_sk,\n"
        f"       {item_expr} AS item_sk,\n"
        f"       {customer_expr} AS customer_sk,\n"
        f"       1 + (g % 12) AS store_sk,\n"
        f"       'store'::text AS channel,\n"
        f"       1 + (g % 50) AS quantity,\n"
        f"       round(((g % 100000)::numeric / 100) + 1, 2) AS net_paid,\n"
        f"       round(((g % 50000)::numeric / 100), 2) AS net_profit\n"
        f"FROM generate_series(1, {spec.row_count}) AS g"
    )


def _consumer_profile_sql(batch_id: int, source_table: str) -> str:
    """Downstream consumer's staging payload profile for one batch.

    The consumer team profiles every staged payload at staging time and keeps the
    rollup in its own cache table: row count, channel mix, money/quantity totals
    and the hot-band item contribution. The profile is derived from the staged
    rows themselves (deterministic payloads), so it is canonical truth for the
    batch contribution and stays stable while the queue-side delivery cycle runs.
    """
    return (
        "INSERT INTO wh.consumer_batch_summary (batch_id, source_table, row_count, store_rows, "
        "catalog_rows, web_rows, total_quantity, total_net_paid, total_net_profit, "
        f"hot_band_item_count, profiled_at) SELECT {batch_id}, '{source_table}', count(*), "
        "count(*) FILTER (WHERE channel = 'store'), count(*) FILTER (WHERE channel = 'catalog'), "
        "count(*) FILTER (WHERE channel = 'web'), COALESCE(sum(quantity), 0), "
        "COALESCE(sum(net_paid), 0), COALESCE(sum(net_profit), 0), "
        f"count(DISTINCT item_sk) FILTER (WHERE item_sk BETWEEN {CONSUMER_HOT_BAND_LOW} "
        f"AND {CONSUMER_HOT_BAND_HIGH}), extract(epoch from now()) FROM {source_table}"
    )


# Statement stream that provisions the whole instance-private warehouse layer.
# Base TPC-DS relations already exist in the deployed image; this adds the batch
# fact model, the batch-0 history, the staged payloads and the public control plane.
def provision_statements() -> tuple[str, ...]:
    history_copy = (
        "INSERT INTO wh.batch_sales (batch_id, line_id, sold_date_sk, item_sk, customer_sk, store_sk, channel, quantity, net_paid, net_profit)\n"
        "SELECT 0, nextval('wh.batch_line_seq'), ss_sold_date_sk, ss_item_sk, ss_customer_sk, ss_store_sk, 'store', ss_quantity, ss_net_paid, ss_net_profit\n"
        f"FROM store_sales CROSS JOIN generate_series(1, {HISTORY_COPY_COUNT}) AS fiscal_copy"
    )
    catalog_copy = (
        "INSERT INTO wh.batch_sales (batch_id, line_id, sold_date_sk, item_sk, customer_sk, store_sk, channel, quantity, net_paid, net_profit)\n"
        "SELECT 0, nextval('wh.batch_line_seq'), cs_sold_date_sk, cs_item_sk, cs_bill_customer_sk, cs_call_center_sk, 'catalog', cs_quantity, cs_net_paid, cs_net_profit\n"
        f"FROM catalog_sales CROSS JOIN generate_series(1, {HISTORY_COPY_COUNT}) AS fiscal_copy"
    )
    web_copy = (
        "INSERT INTO wh.batch_sales (batch_id, line_id, sold_date_sk, item_sk, customer_sk, store_sk, channel, quantity, net_paid, net_profit)\n"
        "SELECT 0, nextval('wh.batch_line_seq'), ws_sold_date_sk, ws_item_sk, ws_bill_customer_sk, ws_web_site_sk, 'web', ws_quantity, ws_net_paid, ws_net_profit\n"
        f"FROM web_sales CROSS JOIN generate_series(1, {HISTORY_COPY_COUNT}) AS fiscal_copy"
    )
    ddl: list[str] = [
        "CREATE SCHEMA IF NOT EXISTS wh",
        (
            "CREATE TABLE IF NOT EXISTS wh.batch_sales (\n"
            "    batch_id int NOT NULL,\n"
            "    line_id bigint NOT NULL,\n"
            "    sold_date_sk int,\n"
            "    item_sk int,\n"
            "    customer_sk int,\n"
            "    store_sk int,\n"
            "    channel text NOT NULL,\n"
            "    quantity int,\n"
            "    net_paid numeric(9,2),\n"
            "    net_profit numeric(9,2)\n"
            ")"
        ),
        "CREATE SEQUENCE IF NOT EXISTS wh.batch_line_seq AS bigint",
        "CREATE INDEX IF NOT EXISTS idx_batch_sales_item ON wh.batch_sales(item_sk)",
        (
            "CREATE TABLE IF NOT EXISTS wh.batch_registry (\n"
            "    batch_id int PRIMARY KEY,\n"
            "    stage_table text NOT NULL,\n"
            "    row_count bigint NOT NULL,\n"
            "    ingest_started_at double precision,\n"
            "    ingest_finished_at double precision,\n"
            "    analyzed_at double precision\n"
            ")"
        ),
        (
            "CREATE TABLE IF NOT EXISTS wh.queue_config (\n"
            "    id int PRIMARY KEY CHECK (id = 1),\n"
            "    max_workers int NOT NULL,\n"
            "    work_mb int NOT NULL,\n"
            "    analytics_enabled boolean NOT NULL,\n"
            "    backup_enabled boolean NOT NULL\n"
            ")"
        ),
        (
            "CREATE TABLE IF NOT EXISTS wh.report_queue (\n"
            "    job_id text PRIMARY KEY,\n"
            "    job_type text NOT NULL CHECK (job_type IN ('report', 'ingest', 'backup')),\n"
            "    report_id text NOT NULL,\n"
            "    batch_cutoff int,\n"
            "    sql_text text NOT NULL,\n"
            "    submit_at double precision NOT NULL,\n"
            "    deadline double precision NOT NULL,\n"
            "    status text NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'delivered', 'failed', 'canceled')),\n"
            "    attempts int NOT NULL DEFAULT 0,\n"
            "    claimed_by text,\n"
            "    claim_pid int,\n"
            "    cancel_requested boolean NOT NULL DEFAULT false,\n"
            "    priority int NOT NULL DEFAULT 100\n"
            ")"
        ),
        (
            "CREATE TABLE IF NOT EXISTS wh.ingest_control (\n"
            "    batch_id int PRIMARY KEY,\n"
            "    analyze_after_ingest boolean NOT NULL\n"
            ")"
        ),
        (
            "CREATE TABLE IF NOT EXISTS wh.config_audit (\n"
            "    audit_id bigserial PRIMARY KEY,\n"
            "    changed_at double precision NOT NULL,\n"
            "    table_name text NOT NULL,\n"
            "    old_row text NOT NULL,\n"
            "    new_row text NOT NULL\n"
            ")"
        ),
        (
            "CREATE TABLE IF NOT EXISTS wh.report_result (\n"
            "    job_id text PRIMARY KEY,\n"
            "    report_id text NOT NULL,\n"
            "    batch_cutoff int,\n"
            "    delivered_at double precision NOT NULL,\n"
            "    row_count bigint NOT NULL,\n"
            "    result_digest text NOT NULL\n"
            ")"
        ),
        (
            "CREATE TABLE IF NOT EXISTS wh.backup_result (\n"
            "    job_id text PRIMARY KEY,\n"
            "    passes int NOT NULL,\n"
            "    bytes_read bigint NOT NULL,\n"
            "    digest text NOT NULL,\n"
            "    finished_at double precision NOT NULL\n"
            ")"
        ),
        history_copy,
        catalog_copy,
        web_copy,
        (
            "INSERT INTO wh.batch_registry (batch_id, stage_table, row_count)\n"
            f"SELECT 0, '', count(*) FROM wh.batch_sales WHERE batch_id = 0"
        ),
        # The upstream publisher registers every staged batch up front (declared
        # payload identity, no completion timestamps); the ingest worker later
        # overwrites the timestamps and the real row count (store.record_batch_registry).
        (
            "INSERT INTO wh.batch_registry (batch_id, stage_table, row_count) VALUES "
            f"({BATCH_A_ID}, '{STAGE_A_TABLE}', {BATCH_A_STAGE.row_count}), "
            f"({BATCH_B_ID}, '{STAGE_B_TABLE}', {BATCH_B_STAGE.row_count})"
        ),
        "ANALYZE wh.batch_sales",
        stage_build_sql(BATCH_A_STAGE),
        stage_build_sql(BATCH_B_STAGE),
        "ANALYZE wh.stage_batch_a",
        "ANALYZE wh.stage_batch_b",
        f"INSERT INTO wh.ingest_control (batch_id, analyze_after_ingest) VALUES ({BATCH_A_ID}, true), ({BATCH_B_ID}, true)",
        "INSERT INTO wh.queue_config (id, max_workers, work_mb, analytics_enabled, backup_enabled) VALUES (1, 2, 4, true, true)",
        # Downstream consumer cache: staging payload profiles for the
        # history batch and both staged batches. Baked at provision time — staging
        # profiling happens when the payload is staged, before any ingest — so the
        # scoring-window workload is untouched and the profile rows are stable,
        # harness-maintained contradiction evidence for the batch B definition drift.
        (
            f"CREATE TABLE IF NOT EXISTS {CONSUMER_SUMMARY_TABLE} (\n"
            "    batch_id int PRIMARY KEY,\n"
            "    source_table text NOT NULL,\n"
            "    row_count bigint NOT NULL,\n"
            "    store_rows bigint NOT NULL,\n"
            "    catalog_rows bigint NOT NULL,\n"
            "    web_rows bigint NOT NULL,\n"
            "    total_quantity bigint NOT NULL,\n"
            "    total_net_paid numeric NOT NULL,\n"
            "    total_net_profit numeric NOT NULL,\n"
            "    hot_band_item_count int NOT NULL,\n"
            "    profiled_at double precision NOT NULL\n"
            ")"
        ),
        _consumer_profile_sql(HISTORY_BATCH_ID, "wh.batch_sales WHERE batch_id = 0"),
        _consumer_profile_sql(BATCH_A_ID, STAGE_A_TABLE),
        _consumer_profile_sql(BATCH_B_ID, STAGE_B_TABLE),
    ]
    return tuple(ddl)
