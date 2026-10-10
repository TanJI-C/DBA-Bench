"""Order-domain schema, roles and authorization control tables for the
shared-resource HTAP instance (pg_htap_shared_resource_isolation).

Business truth lives entirely in these tables; the deployment base image may
carry any auxiliary dataset. All statements are idempotent per fresh database
and fail loudly on conflict.
"""

from __future__ import annotations

from dataclasses import dataclass

ROLE_OLTP = "htap_oltp"
ROLE_DASHBOARD = "htap_dashboard"
ROLE_ANALYST = "htap_analyst"

APP_OLTP = "pg5r-htap3-oltp"
# The steady dashboard pool runs the audited stable release; the retry-storm
# cohort (capability) runs v2.4.1-rc3, so pg_stat_activity carries the release
# contrast the attribution hops on.
APP_DASHBOARD = "dashboard-edge/v2.3.9"
APP_ANALYSIS_WORKER = "pg5r-htap3-analysis-worker"
APP_EXPORT_WORKER = "pg5r-htap3-export-worker"
APP_WATERMARK = "pg5r-htap3-watermark"
APP_TRUSTED = "pg5r-htap3-trusted"

CONTROL_DEFAULTS = {
    "analyst_max_concurrency": "2",
    "analyst_statement_timeout_ms": "120000",
    "export_rows_per_second": "8000",
    "dashboard_max_concurrency": "4",
}

CONTROL_KEYS = tuple(CONTROL_DEFAULTS)


@dataclass(frozen=True, slots=True)
class HtapDatasetScale:
    order_rows: int = 1_200_000
    line_multiplier: int = 3
    sku_rows: int = 3_000
    hot_skus: int = 24


# Compressed-timeline calibration scale used by the three-path calibration.
SMOKE_SCALE = HtapDatasetScale(order_rows=40_000, line_multiplier=3, sku_rows=500, hot_skus=24)


def bootstrap(open_connection, scale: HtapDatasetScale) -> None:
    connection = open_connection("pg5r-htap3-bootstrap", "primary")
    try:
        with connection.cursor() as cursor:
            _create_roles(cursor)
            _create_tables(cursor, scale)
            _seed(cursor, scale)
            _grant(cursor)
        connection.commit()
    finally:
        connection.close()


def _create_roles(cursor) -> None:
    cursor.execute(
        f"DO $$ BEGIN"
        f" IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{ROLE_OLTP}') THEN"
        f" CREATE ROLE {ROLE_OLTP} LOGIN PASSWORD 'htap3_oltp'; END IF;"
        f" IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{ROLE_DASHBOARD}') THEN"
        f" CREATE ROLE {ROLE_DASHBOARD} LOGIN PASSWORD 'htap3_dashboard'; END IF;"
        f" IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{ROLE_ANALYST}') THEN"
        f" CREATE ROLE {ROLE_ANALYST} LOGIN PASSWORD 'htap3_analyst'; END IF;"
        f" END $$;"
    )


def _create_tables(cursor, scale: HtapDatasetScale) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS htap_orders (
            order_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            region integer NOT NULL,
            status text NOT NULL CHECK (status IN ('paid', 'shipped', 'cancelled')),
            amount numeric(12, 2) NOT NULL CHECK (amount >= 0),
            sku integer NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE IF NOT EXISTS htap_payments (
            payment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            order_id bigint NOT NULL UNIQUE REFERENCES htap_orders(order_id),
            amount numeric(12, 2) NOT NULL,
            paid_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE IF NOT EXISTS htap_order_lines (
            line_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            order_id bigint NOT NULL,
            sku integer NOT NULL,
            qty integer NOT NULL CHECK (qty > 0),
            price numeric(10, 2) NOT NULL,
            region integer NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE IF NOT EXISTS htap_inventory (
            sku integer PRIMARY KEY,
            on_hand integer NOT NULL CHECK (on_hand >= 0),
            reserved integer NOT NULL DEFAULT 0 CHECK (reserved >= 0)
        );
        CREATE TABLE IF NOT EXISTS htap_commit_watermark (
            watermark_seq bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            commit_lsn pg_lsn NOT NULL,
            committed_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE IF NOT EXISTS htap_analysis_jobs (
            job_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            ref text UNIQUE,
            tenant text NOT NULL,
            kind text NOT NULL CHECK (kind IN ('scan', 'export')),
            range_start bigint NOT NULL DEFAULT 0,
            range_end bigint NOT NULL,
            binding text,
            state text NOT NULL DEFAULT 'queued' CHECK (state IN ('queued', 'running', 'done', 'cancelled', 'deadline_missed')),
            deadline_at timestamptz NOT NULL,
            submitted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            finished_at timestamptz
        );
        CREATE TABLE IF NOT EXISTS htap_export_checkpoints (
            export_id text NOT NULL,
            watermark_seq bigint NOT NULL,
            last_line_id bigint NOT NULL,
            page_digest text NOT NULL,
            page_rows bigint NOT NULL,
            updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            PRIMARY KEY (export_id, last_line_id)
        );
        CREATE TABLE IF NOT EXISTS htap_work_control (
            control_key text PRIMARY KEY,
            control_value text NOT NULL,
            updated_by text NOT NULL DEFAULT 'workload',
            updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE IF NOT EXISTS htap_release_audit (
            audit_id bigserial PRIMARY KEY,
            changed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            component text NOT NULL,
            release_tag text NOT NULL,
            old_config text NOT NULL,
            new_config text NOT NULL,
            UNIQUE (component, release_tag)
        );
        CREATE TABLE IF NOT EXISTS htap_tenant_quota (
            tenant text PRIMARY KEY,
            tier text NOT NULL,
            max_concurrency int
        );
        CREATE TABLE IF NOT EXISTS htap_control_probe (id integer PRIMARY KEY, value integer NOT NULL);
        """
    )
    # Hot-table vacuum tuning: autovacuum genuinely cycles on the order
    # tables during a run, so "maintenance is running" is a visible but
    # non-discriminating signal — with a pinned xmin it advances nothing.
    cursor.execute(
        "ALTER TABLE htap_orders SET (autovacuum_vacuum_scale_factor = 0.01, autovacuum_vacuum_threshold = 200);"
        "ALTER TABLE htap_inventory SET (autovacuum_vacuum_scale_factor = 0.01, autovacuum_vacuum_threshold = 200);"
        "ALTER TABLE htap_payments SET (autovacuum_vacuum_scale_factor = 0.01, autovacuum_vacuum_threshold = 200);"
    )


def _seed(cursor, scale: HtapDatasetScale) -> None:
    cursor.execute(
        "INSERT INTO htap_inventory (sku, on_hand) SELECT s, 10000 + (s * 37) %% 5000 "
        "FROM generate_series(1, %s) s ON CONFLICT DO NOTHING;",
        (scale.sku_rows,),
    )
    cursor.execute("INSERT INTO htap_control_probe VALUES (1, 1) ON CONFLICT DO NOTHING;")
    cursor.execute(
        "INSERT INTO htap_orders (region, status, amount, sku, created_at) "
        "SELECT g %% 32, CASE g %% 7 WHEN 0 THEN 'cancelled' WHEN 1 THEN 'shipped' ELSE 'paid' END, "
        "((g * 13) %% 90000) / 100.0 + 5, (g %% %s) + 1, clock_timestamp() - (g %% 5400) * interval '1 second' "
        "FROM generate_series(1, %s) g ON CONFLICT DO NOTHING;",
        (scale.sku_rows, scale.order_rows),
    )
    cursor.execute(
        "INSERT INTO htap_payments (order_id, amount) SELECT order_id, amount FROM htap_orders "
        "WHERE status = 'paid' ON CONFLICT DO NOTHING;"
    )
    cursor.execute(
        "INSERT INTO htap_order_lines (order_id, sku, qty, price, region) "
        "SELECT (g %% %s) + 1, (g %% %s) + 1, (g %% 4) + 1, ((g * 7) %% 5000) / 100.0 + 1, g %% 32 "
        "FROM generate_series(1, %s) g ON CONFLICT DO NOTHING;",
        (scale.order_rows, scale.sku_rows, scale.order_rows * scale.line_multiplier),
    )
    rows_sql = " UNION ALL ".join(
        f"SELECT '{key}', '{value}'" for key, value in CONTROL_DEFAULTS.items()
    )
    cursor.execute(
        f"INSERT INTO htap_work_control (control_key, control_value) {rows_sql} "
        "ON CONFLICT (control_key) DO NOTHING;"
    )
    # Historical dashboard_edge client releases: the audit trail the retry-storm
    # attribution must find. The steady pool runs v2.3.9 (its application_name).
    cursor.execute(
        "INSERT INTO htap_release_audit (component, release_tag, old_config, new_config) VALUES "
        "('dashboard_edge', 'v2.3.7', '{\"retry_max\": 0}', '{\"retry_max\": 1, \"retry_backoff_ms\": 2000}'), "
        "('dashboard_edge', 'v2.3.9', '{\"retry_max\": 1, \"retry_backoff_ms\": 2000}', "
        "'{\"retry_max\": 1, \"retry_backoff_ms\": 1000}') "
        "ON CONFLICT (component, release_tag) DO NOTHING;"
    )
    # The competing tenants are declared with their business priority tier but
    # without per-tenant admission: the missing isolation decision the agent
    # must make. A NULL max_concurrency means the tenant is only governed by
    # the global analyst_max_concurrency budget.
    cursor.execute(
        "INSERT INTO htap_tenant_quota (tenant, tier, max_concurrency) VALUES "
        "('tenant_alpha', 'platinum', NULL), ('tenant_beta', 'standard', NULL) "
        "ON CONFLICT (tenant) DO NOTHING;"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS htap_orders_created_idx ON htap_orders (created_at);"
        "CREATE INDEX IF NOT EXISTS htap_orders_status_idx ON htap_orders (status, order_id);"
        "CREATE INDEX IF NOT EXISTS htap_lines_order_idx ON htap_order_lines (order_id);"
        "CREATE INDEX IF NOT EXISTS htap_lines_region_id_idx ON htap_order_lines (region, line_id);"
    )


def _grant(cursor) -> None:
    cursor.execute(
        f"GRANT SELECT, INSERT, UPDATE ON htap_orders, htap_payments, htap_inventory, htap_commit_watermark TO {ROLE_OLTP};"
        f"GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO {ROLE_OLTP};"
        f"GRANT SELECT ON htap_orders, htap_order_lines, htap_payments TO {ROLE_DASHBOARD};"
        f"GRANT SELECT, INSERT, UPDATE ON htap_analysis_jobs, htap_export_checkpoints TO {ROLE_ANALYST};"
        f"GRANT SELECT ON htap_order_lines, htap_orders, htap_commit_watermark TO {ROLE_ANALYST};"
        f"GRANT SELECT, UPDATE ON htap_work_control TO {ROLE_ANALYST}, {ROLE_DASHBOARD};"
        f"GRANT SELECT, UPDATE ON htap_tenant_quota TO {ROLE_ANALYST}, {ROLE_DASHBOARD};"
        f"GRANT SELECT ON htap_release_audit TO {ROLE_OLTP}, {ROLE_ANALYST}, {ROLE_DASHBOARD};"
        f"GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO {ROLE_ANALYST};"
    )


def read_control(open_connection, key: str) -> str:
    connection = open_connection("pg5r-htap3-trusted-control", "primary")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT control_value FROM htap_work_control WHERE control_key = %s;", (key,))
            row = cursor.fetchone()
        connection.rollback()
    finally:
        connection.close()
    if row is None:
        raise ValueError(f"Unknown htap_work_control key: key={key!r}, known={CONTROL_KEYS!r}")
    return str(row[0])
