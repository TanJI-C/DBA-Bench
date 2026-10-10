"""Order/report schema, roles and control tables for pg_htap_replica_freshness.

Primary is the only writable node; the standby serves report reads and receives
the same schema through streaming replication.
"""

from __future__ import annotations

from dataclasses import dataclass

ROLE_OLTP = "frs_oltp"
ROLE_REPORT = "frs_report"

APP_OLTP = "pg5r-htap4-oltp"
APP_REPORT_WORKER = "pg5r-htap4-report-worker"
APP_WATERMARK = "pg5r-htap4-watermark"
APP_TRUSTED = "pg5r-htap4-trusted"

# Every control row has a real consumer: the report worker
# reads report_statement_timeout_ms per claim; the runtime's LinkPolicyGovernor
# applies replication_link_rate_kbit (0 = full rate, >0 = tc tbf kbit) to the
# replication link. Agent repairs go through these rows with updated_by='dba'.
CONTROL_DEFAULTS = {
    "report_statement_timeout_ms": "30000",
    "replication_link_rate_kbit": "0",
}

CONTROL_KEYS = tuple(CONTROL_DEFAULTS)


@dataclass(frozen=True, slots=True)
class FreshnessDatasetScale:
    order_rows: int = 200_000
    event_rows: int = 800_000


# Compressed-timeline calibration scale used by the three-path calibration.
SMOKE_SCALE = FreshnessDatasetScale(order_rows=20_000, event_rows=80_000)


def bootstrap(open_connection, scale: FreshnessDatasetScale) -> None:
    connection = open_connection("pg5r-htap4-bootstrap", "primary")
    try:
        with connection.cursor() as cursor:
            _create_roles(cursor)
            _create_tables(cursor)
            _seed(cursor, scale)
            _grant(cursor)
        connection.commit()
    finally:
        connection.close()


def _create_roles(cursor) -> None:
    cursor.execute(
        "DO $$ BEGIN"
        f" IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{ROLE_OLTP}') THEN"
        f" CREATE ROLE {ROLE_OLTP} LOGIN PASSWORD 'frs_oltp'; END IF;"
        f" IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{ROLE_REPORT}') THEN"
        f" CREATE ROLE {ROLE_REPORT} LOGIN PASSWORD 'frs_report'; END IF;"
        " END $$;"
    )


def _create_tables(cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS frs_orders (
            order_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            status text NOT NULL CHECK (status IN ('created', 'paid', 'shipped')),
            amount numeric(12, 2) NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE IF NOT EXISTS frs_payments (
            payment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            order_id bigint NOT NULL UNIQUE REFERENCES frs_orders(order_id),
            amount numeric(12, 2) NOT NULL,
            paid_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE IF NOT EXISTS frs_order_events (
            event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            order_id bigint NOT NULL,
            kind text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE IF NOT EXISTS frs_commit_watermark (
            watermark_seq bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            commit_lsn pg_lsn NOT NULL,
            committed_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE IF NOT EXISTS frs_report_jobs (
            job_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            ref text UNIQUE,
            report_kind text NOT NULL,
            freshness_budget_seconds int NOT NULL,
            state text NOT NULL DEFAULT 'queued' CHECK (state IN ('queued', 'running', 'delivered', 'deadline_missed', 'cancelled')),
            deadline_at timestamptz NOT NULL,
            submitted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            delivered_at timestamptz,
            visible_watermark_seq bigint,
            replay_lsn pg_lsn,
            result_digest text
        );
        CREATE TABLE IF NOT EXISTS frs_work_control (
            control_key text PRIMARY KEY,
            control_value text NOT NULL,
            updated_by text NOT NULL DEFAULT 'workload',
            updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        """
    )


def _seed(cursor, scale: FreshnessDatasetScale) -> None:
    cursor.execute(
        "INSERT INTO frs_orders (status, amount) "
        "SELECT CASE g %% 5 WHEN 0 THEN 'created' WHEN 1 THEN 'shipped' ELSE 'paid' END, "
        "((g * 17) %% 80000) / 100.0 + 4 FROM generate_series(1, %s) g ON CONFLICT DO NOTHING;",
        (scale.order_rows,),
    )
    cursor.execute(
        "INSERT INTO frs_payments (order_id, amount) SELECT order_id, amount FROM frs_orders "
        "WHERE status = 'paid' ON CONFLICT DO NOTHING;"
    )
    cursor.execute(
        "INSERT INTO frs_order_events (order_id, kind) SELECT (g %% %s) + 1, 'e' || (g %% 8) "
        "FROM generate_series(1, %s) g ON CONFLICT DO NOTHING;",
        (scale.order_rows, scale.event_rows),
    )
    rows_sql = " UNION ALL ".join(f"SELECT '{key}', '{value}'" for key, value in CONTROL_DEFAULTS.items())
    cursor.execute(
        f"INSERT INTO frs_work_control (control_key, control_value) {rows_sql} "
        "ON CONFLICT (control_key) DO NOTHING;"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS frs_events_created_idx ON frs_order_events (created_at);"
        "CREATE INDEX IF NOT EXISTS frs_orders_status_idx ON frs_orders (status, order_id);"
    )


def _grant(cursor) -> None:
    cursor.execute(
        f"GRANT SELECT, INSERT, UPDATE ON frs_orders, frs_payments, frs_order_events, frs_commit_watermark TO {ROLE_OLTP};"
        f"GRANT SELECT ON frs_orders, frs_order_events, frs_payments, frs_commit_watermark TO {ROLE_REPORT};"
        f"GRANT SELECT, UPDATE, INSERT ON frs_report_jobs TO {ROLE_REPORT};"
        f"GRANT SELECT, UPDATE ON frs_work_control TO {ROLE_REPORT};"
        f"GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO {ROLE_OLTP}, {ROLE_REPORT};"
    )
