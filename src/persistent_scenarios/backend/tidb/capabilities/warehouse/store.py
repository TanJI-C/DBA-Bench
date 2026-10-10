"""Instance-owned SQL adapters over the public warehouse control tables (pymysql).

The public `wh.warehouse_jobs` table is the real scheduling source: workers claim rows
through these adapters, and authorized agents may legitimately rewrite job SQL, request
cancellation, or pause/widen services through `wh.warehouse_config` (audited in
`wh.config_audit`). The trusted ledger keeps every obligation, so deleting queued rows
or cancelling attempts can only end as outstanding loss, never a completed delivery.
"""

from __future__ import annotations

import json
import re
import time

from .reports import streaming_result_digest
from .schema import (
    BATCH_REGISTRY,
    CONFIG_AUDIT,
    CONFIG_TABLE,
    CORRECTION_COST_FACTOR,
    CORRECTION_PRICE_FACTOR,
    CORRECTION_ROW_MODULUS,
    FACT_TABLE,
    QUEUE_TABLE,
    REPORT_RESULT,
    stage_spec,
)

QUEUE_APP_PREFIX = "tidb5-olap-worker"
MAX_ATTEMPTS = 3
DEFAULT_ATTEMPT_TIMEOUT_SECONDS = 900.0
HEARTBEAT_JOB_PREFIX = "bi_heartbeat_"

INGEST_PRIORITY = 10
REQUIRED_REPORT_PRIORITY = 50
HEARTBEAT_PRIORITY = 100


def heartbeat_job_id(query_id: str, sequence: int) -> str:
    return f"{HEARTBEAT_JOB_PREFIX}{query_id}_{sequence:04d}"


def heartbeat_query_ids() -> tuple[str, ...]:
    return ("region_recent", "channel_recent", "item_recent")


def heartbeat_sql(query_id: str, batch_cutoff: int, since_ts: str) -> str:
    """Light BI heartbeat queries over recent history (frozen task class)."""
    catalog = {
        "region_recent": (
            "SELECT region_id, SUM(quantity) FROM wh.orders "
            f"WHERE batch_id <= {int(batch_cutoff)} AND order_ts >= '{since_ts}' GROUP BY region_id"
        ),
        "channel_recent": (
            "SELECT channel, COUNT(*) FROM wh.orders "
            f"WHERE batch_id <= {int(batch_cutoff)} AND order_ts >= '{since_ts}' GROUP BY channel"
        ),
        "item_recent": (
            "SELECT item_id, SUM(amount) FROM wh.orders "
            f"WHERE batch_id <= {int(batch_cutoff)} AND order_ts >= '{since_ts}' "
            "GROUP BY item_id ORDER BY 2 DESC LIMIT 20"
        ),
    }
    return catalog[query_id]


def _wall_now() -> float:
    return time.monotonic()


def fetchone(connection, sql: str, args: tuple = ()) -> tuple | None:
    with connection.cursor() as cursor:
        cursor.execute(sql, args)
        rows = cursor.fetchall()
    connection.rollback()
    return rows[0] if rows else None


class QueueTables:
    """Raw SQL over wh.warehouse_jobs / wh.warehouse_config and the batch registry."""

    def config_row(self, connection) -> tuple[int, int, bool, bool]:
        row = fetchone(
            connection,
            f"SELECT max_workers, report_memory_quota_mb, analytics_enabled, ingest_enabled "
            f"FROM {CONFIG_TABLE} WHERE id = 1;",
        )
        if row is None:
            raise RuntimeError(f"{CONFIG_TABLE} lost its single configuration row")
        return int(row[0]), int(row[1]), bool(row[2]), bool(row[3])

    def update_config(self, connection, at: float, **changes: object) -> dict[str, object]:
        allowed = {"max_workers", "report_memory_quota_mb", "analytics_enabled", "ingest_enabled"}
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"unsupported warehouse config fields: {sorted(unknown)!r}")
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT max_workers, report_memory_quota_mb, analytics_enabled, ingest_enabled "
                f"FROM {CONFIG_TABLE} WHERE id = 1;"
            )
            old = cursor.fetchone()
            assignments = ", ".join(f"{name} = %s" for name in changes)
            cursor.execute(f"UPDATE {CONFIG_TABLE} SET {assignments} WHERE id = 1;", tuple(changes.values()))
            cursor.execute(
                f"SELECT max_workers, report_memory_quota_mb, analytics_enabled, ingest_enabled "
                f"FROM {CONFIG_TABLE} WHERE id = 1;"
            )
            new = cursor.fetchone()
            cursor.execute(
                f"INSERT INTO {CONFIG_AUDIT} (changed_at, table_name, old_row, new_row) VALUES (%s, %s, %s, %s);",
                (at, CONFIG_TABLE, json.dumps(old, default=str), json.dumps(new, default=str)),
            )
        connection.commit()
        return dict(zip(("max_workers", "report_memory_quota_mb", "analytics_enabled", "ingest_enabled"), new))

    def enqueue_row(self, connection, job_id: str, job_type: str, report_id: str | None, batch_cutoff: int | None,
                    sql_text: str, submit_at: float, deadline: float, priority: int) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {QUEUE_TABLE} (job_id, job_type, report_id, batch_cutoff, sql_text, "
                f"submit_at, deadline, status, attempts, cancel_requested, priority) "
                f"VALUES (%s, %s, %s, %s, %s, %s, %s, 'queued', 0, FALSE, %s);",
                (job_id, job_type, report_id, batch_cutoff, sql_text, submit_at, deadline, priority),
            )
        connection.commit()

    def claim_row(self, connection, job_type: str, worker_id: str, report_id_prefix: str | None = None,
                  respect_report_hold: bool = False) -> tuple | None:
        """Pessimistic claim via SELECT ... FOR UPDATE SKIP LOCKED (TiDB v6.2+).

        `respect_report_hold` applies the scheduler's per-batch report hold: report
        jobs whose batch registry row carries reports_held=TRUE stay queued (the
        upstream correction wave gates the batch's report class until an operator
        releases it).
        """
        if report_id_prefix is None:
            kind_filter = f"job_type = %s"
            args: list = [job_type]
        elif report_id_prefix.startswith("!"):
            kind_filter = "job_type = %s AND (report_id NOT LIKE %s OR report_id IS NULL)"
            args = [job_type, f"{report_id_prefix[1:]}%"]
        else:
            kind_filter = "job_type = %s AND report_id LIKE %s"
            args = [job_type, f"{report_id_prefix}%"]
        hold_filter = ""
        if respect_report_hold:
            hold_filter = (
                f" AND NOT EXISTS (SELECT 1 FROM {BATCH_REGISTRY} held "
                f"WHERE held.batch_id = {QUEUE_TABLE}.batch_cutoff AND held.reports_held = TRUE)"
            )
        with connection.cursor() as cursor:
            cursor.execute("BEGIN PESSIMISTIC;")
            cursor.execute(
                f"SELECT job_id FROM {QUEUE_TABLE} WHERE {kind_filter}{hold_filter} AND status = 'queued' "
                f"ORDER BY priority, job_id LIMIT 1 FOR UPDATE SKIP LOCKED;",
                tuple(args),
            )
            picked = cursor.fetchone()
            if picked is None:
                cursor.execute("ROLLBACK;")
                return None
            cursor.execute(
                f"UPDATE {QUEUE_TABLE} SET status = 'running', claimed_by = %s, claim_conn_id = CONNECTION_ID(), "
                f"claim_started_at = %s, attempts = attempts + 1 WHERE job_id = %s AND status = 'queued';",
                (worker_id, _wall_now(), picked[0]),
            )
            if cursor.rowcount != 1:
                # Measured on the real-clock zero path (6-way release): TiDB
                # v8.1 SKIP LOCKED can hand the same queued row to concurrent waiters whose
                # own lock request was still pending when the skip decision ran, so several
                # workers executed one delivery. The conditional UPDATE collapses every
                # duplicate claim to the single winner; the losers re-poll.
                cursor.execute("ROLLBACK;")
                return None
            cursor.execute(
                f"SELECT job_id, report_id, batch_cutoff, sql_text, submit_at, deadline, attempts "
                f"FROM {QUEUE_TABLE} WHERE job_id = %s;",
                (picked[0],),
            )
            row = cursor.fetchone()
            cursor.execute("COMMIT;")
        return row if row else None

    def job_state(self, connection, job_id: str) -> tuple[str, bool, int]:
        row = fetchone(
            connection,
            f"SELECT sql_text, cancel_requested, attempts FROM {QUEUE_TABLE} WHERE job_id = %s;",
            (job_id,),
        )
        if row is None:
            raise RuntimeError(f"claimed queue row disappeared during execution: job_id={job_id!r}")
        return str(row[0]), bool(row[1]), int(row[2])

    def requeue_row(self, connection, job_id: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {QUEUE_TABLE} SET status = 'queued', claimed_by = NULL, claim_conn_id = NULL, "
                f"claim_started_at = NULL, cancel_requested = FALSE WHERE job_id = %s;",
                (job_id,),
            )
        connection.commit()

    def fail_row(self, connection, job_id: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE {QUEUE_TABLE} SET status = 'failed' WHERE job_id = %s;", (job_id,))
        connection.commit()

    def mark_delivered(self, connection, job_id: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE {QUEUE_TABLE} SET status = 'delivered' WHERE job_id = %s;", (job_id,))
        connection.commit()

    def deliver_report_row(self, connection, job_id: str, report_id: str, batch_cutoff: int,
                           delivered_at: float, result_digest: str, row_count: int) -> None:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE {QUEUE_TABLE} SET status = 'delivered', result_digest = %s WHERE job_id = %s;",
                           (result_digest, job_id))
            cursor.execute(
                f"INSERT INTO {REPORT_RESULT} (job_id, report_id, batch_cutoff, delivered_at, row_count, result_digest) "
                f"VALUES (%s, %s, %s, %s, %s, %s);",
                (job_id, report_id, batch_cutoff, delivered_at, row_count, result_digest),
            )
        connection.commit()

    def cancel_requested_running(self, connection) -> tuple[tuple[str, int], ...]:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT job_id, claim_conn_id FROM {QUEUE_TABLE} "
                f"WHERE status = 'running' AND cancel_requested = TRUE AND claim_conn_id IS NOT NULL;"
            )
            rows = cursor.fetchall()
        connection.rollback()
        return tuple((str(row[0]), int(row[1])) for row in rows)

    def kill_connection(self, connection, conn_id: int) -> None:
        with connection.cursor() as cursor:
            cursor.execute(f"KILL TIDB {int(conn_id)};")
        connection.commit()

    def set_analyze_after_ingest(self, connection, batch_id: int, analyze_after_ingest: bool, at: float) -> dict:
        """Registry flag: whether ingest workers run ANALYZE after publishing a batch."""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT skew_note, analyze_after_ingest FROM {BATCH_REGISTRY} WHERE batch_id = %s;", (batch_id,))
            old = cursor.fetchone()
            if old is None:
                raise RuntimeError(f"{BATCH_REGISTRY} must hold one row per planned batch: batch_id={batch_id}")
            cursor.execute(
                f"UPDATE {BATCH_REGISTRY} SET analyze_after_ingest = %s WHERE batch_id = %s;",
                (analyze_after_ingest, batch_id),
            )
            cursor.execute(
                f"INSERT INTO {CONFIG_AUDIT} (changed_at, table_name, old_row, new_row) VALUES (%s, %s, %s, %s);",
                (at, BATCH_REGISTRY, json.dumps(old, default=str),
                 json.dumps({"batch_id": batch_id, "analyze_after_ingest": analyze_after_ingest}, default=str)),
            )
        connection.commit()
        return {"batch_id": batch_id, "analyze_after_ingest": analyze_after_ingest}

    def registry_row(self, connection, batch_id: int) -> tuple[str, bool, bool, float | None, float | None, float | None, float | None, int | None]:
        row = fetchone(
            connection,
            f"SELECT skew_note, analyze_after_ingest, reports_held, republished_at, ingest_started_at, "
            f"ingest_finished_at, analyzed_at, row_count "
            f"FROM {BATCH_REGISTRY} WHERE batch_id = %s;",
            (batch_id,),
        )
        if row is None:
            raise RuntimeError(f"{BATCH_REGISTRY} must hold one row per planned batch: batch_id={batch_id}")
        return row

    def record_batch_registry(self, connection, batch_id: int, started_at: float, finished_at: float,
                              analyzed_at: float | None, row_count: int) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {BATCH_REGISTRY} SET ingest_started_at = %s, ingest_finished_at = %s, "
                f"analyzed_at = COALESCE(analyzed_at, %s), row_count = %s WHERE batch_id = %s;",
                (started_at, finished_at, analyzed_at, row_count, batch_id),
            )
        connection.commit()

    def audit_registry_change(self, connection, at: float, table_name: str, old_row: dict, new_row: dict) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {CONFIG_AUDIT} (changed_at, table_name, old_row, new_row) VALUES (%s, %s, %s, %s);",
                (at, table_name, json.dumps(old_row, default=str), json.dumps(new_row, default=str)),
            )
        connection.commit()

    # ---------------------------------------------------------------------------
    # Correction wave: real upstream re-delivery over the stage
    # tables and one atomic re-publication of batch A.
    # ---------------------------------------------------------------------------

    def rewrite_stage_with_correction(self, connection, stage_table: str, at: float, batch_id: int) -> dict:
        """Deterministic upstream correction over one stage table: pricing/cost
        corrections on the order_id % 8 subset, amount kept consistent."""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {stage_table};")
            staged_rows = int(cursor.fetchone()[0])
            cursor.execute(
                f"UPDATE {stage_table} SET "
                f"unit_price = ROUND(unit_price * {CORRECTION_PRICE_FACTOR}, 2), "
                f"unit_cost = ROUND(unit_cost * {CORRECTION_COST_FACTOR}, 2), "
                f"amount = ROUND(quantity * ROUND(unit_price * {CORRECTION_PRICE_FACTOR}, 2), 2) "
                f"WHERE order_id % {CORRECTION_ROW_MODULUS} = 0;",
            )
            corrected_rows = int(cursor.rowcount)
        connection.commit()
        self.audit_registry_change(
            connection, at, stage_table,
            {"batch_id": batch_id, "stage_rows": staged_rows},
            {"batch_id": batch_id, "corrected_rows": corrected_rows,
             "price_factor": CORRECTION_PRICE_FACTOR, "cost_factor": CORRECTION_COST_FACTOR},
        )
        return {"stage_table": stage_table, "stage_rows": staged_rows, "corrected_rows": corrected_rows}

    def republish_batch(self, connection, batch_id: int, at: float) -> dict:
        """Atomic batch re-publication: the corrected stage payload replaces the
        published batch in ONE transaction (upstream ingest atomicity),
        the registry carries the republish marker, and the wave is audited."""
        spec = stage_spec(batch_id)
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {FACT_TABLE} WHERE batch_id = %s;", (batch_id,))
            published_before = int(cursor.fetchone()[0])
            started = _wall_now()
            cursor.execute(f"DELETE FROM {FACT_TABLE} WHERE batch_id = %s;", (batch_id,))
            cursor.execute(
                f"INSERT INTO {FACT_TABLE} (order_id, batch_id, region_id, warehouse_id, item_id, channel, "
                f"quantity, unit_price, unit_cost, amount, order_ts) "
                f"SELECT order_id, %s, region_id, warehouse_id, item_id, channel, quantity, unit_price, "
                f"unit_cost, amount, order_ts FROM {spec.stage_table};",
                (batch_id,),
            )
            republished_rows = int(cursor.rowcount)
            cursor.execute(
                f"UPDATE {BATCH_REGISTRY} SET ingest_started_at = %s, ingest_finished_at = %s, "
                f"republished_at = %s, row_count = %s WHERE batch_id = %s;",
                (started, _wall_now(), at, republished_rows, batch_id),
            )
            cursor.execute(
                f"INSERT INTO {CONFIG_AUDIT} (changed_at, table_name, old_row, new_row) VALUES (%s, %s, %s, %s);",
                (at, BATCH_REGISTRY,
                 json.dumps({"batch_id": batch_id, "published_rows": published_before, "republished_at": None}),
                 json.dumps({"batch_id": batch_id, "republished_rows": republished_rows})),
            )
        connection.commit()
        return {"batch_id": batch_id, "republished_rows": republished_rows, "republished_at": at}

    def set_reports_held(self, connection, batch_id: int, held: bool, at: float) -> dict:
        """Scheduler-side hold transition (the wave arms it; the operator release is a
        direct authorized registry UPDATE by the agent and does not go through here)."""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT reports_held FROM {BATCH_REGISTRY} WHERE batch_id = %s;", (batch_id,))
            old = cursor.fetchone()
            if old is None:
                raise RuntimeError(f"{BATCH_REGISTRY} must hold one row per planned batch: batch_id={batch_id}")
            cursor.execute(f"UPDATE {BATCH_REGISTRY} SET reports_held = %s WHERE batch_id = %s;", (held, batch_id))
        connection.commit()
        self.audit_registry_change(
            connection, at, BATCH_REGISTRY,
            {"batch_id": batch_id, "reports_held": bool(old[0])},
            {"batch_id": batch_id, "reports_held": held},
        )
        return {"batch_id": batch_id, "reports_held": held}

    def record_maintenance_analyze(self, connection, at: float, table_name: str, phase: str) -> None:
        """Maintenance-session audit row for one ANALYZE phase (started/finished)."""
        self.audit_registry_change(
            connection, at, "maintenance_analyze", {"table": table_name, "phase": phase}, {},
        )


# ---------------------------------------------------------------------------
# Job bodies: each receives the claim connection and owns its commit boundaries.
# ---------------------------------------------------------------------------


def make_report_run(tables: QueueTables, *, attempt_timeout_seconds: float):
    """Report body: live queue-row SQL, session memory quota from the control table."""

    def run(job, connection) -> str:
        sql_text, _cancel_requested, _attempts = tables.job_state(connection, job.job_id)
        _max_workers, quota_mb, _analytics, _ingest = tables.config_row(connection)
        ordered = bool((job.input_snapshot or {}).get("ordered", True))
        report_id = str((job.input_snapshot or {}).get("report_id", ""))
        cutoff = int((job.input_snapshot or {}).get("batch_cutoff", 0))
        with connection.cursor() as cursor:
            cursor.execute(f"SET SESSION tidb_mem_quota_query = {int(quota_mb) * 1024 * 1024};")
            cursor.execute(f"SET SESSION max_execution_time = {int(attempt_timeout_seconds * 1000)};")
            cursor.execute(sql_text)
            digest, row_count = streaming_result_digest(cursor, ordered=ordered)
        connection.rollback()
        tables.deliver_report_row(connection, job.job_id, report_id, cutoff, _wall_now(), digest, row_count)
        return digest

    return run


def make_ingest_run(tables: QueueTables, job_id: str, batch_id: int, *, attempt_timeout_seconds: float):
    """Ingest body: validate the staged batch, publish it in one transaction, register facts.

    The staged batch is verified (row count matches the plan) before publication; the
    publication itself is a single INSERT ... SELECT transaction, so a failure midway
    leaves wh.orders untouched (batch atomicity).
    """

    def run(job, connection) -> str:
        spec = stage_spec(batch_id)
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {spec.stage_table};")
            staged_rows = int(cursor.fetchone()[0])
            if staged_rows != spec.row_count:
                raise RuntimeError(
                    f"staged batch validation failed: batch_id={batch_id}, stage_table={spec.stage_table}, "
                    f"expected_rows={spec.row_count}, staged_rows={staged_rows}"
                )
            started = _wall_now()
            cursor.execute(
                f"INSERT INTO {FACT_TABLE} (order_id, batch_id, region_id, warehouse_id, item_id, channel, "
                f"quantity, unit_price, unit_cost, amount, order_ts) "
                f"SELECT order_id, %s, region_id, warehouse_id, item_id, channel, quantity, unit_price, "
                f"unit_cost, amount, order_ts FROM {spec.stage_table};",
                (batch_id,),
            )
            published = cursor.rowcount
        connection.commit()
        analyzed_at = None
        registry = tables.registry_row(connection, batch_id)
        _note, analyze_after_ingest = registry[0], registry[1]
        if analyze_after_ingest:
            # the calibrated maintenance form (driver YAML statistics_maintenance):
            # a full ANALYZE right after a publish wave was killed by
            # tidb_server_memory_limit (8176) on the 2GB TiDB / 4GB TiKV cluster,
            # the 0.05 SAMPLERATE form completes in 7-16s (measured)
            with connection.cursor() as cursor:
                cursor.execute(f"ANALYZE TABLE {FACT_TABLE} WITH 0.05 SAMPLERATE;")
            analyzed_at = _wall_now()
        tables.record_batch_registry(connection, batch_id, started, _wall_now(), analyzed_at, int(published))
        tables.mark_delivered(connection, job_id)
        return f"ingest:{int(published)}"

    return run
