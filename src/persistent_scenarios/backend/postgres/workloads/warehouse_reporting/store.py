"""Instance-owned SQL adapters implementing the core `JobQueueStore` protocol.

The public `wh.report_queue` table is the real scheduling source: the core
`JobQueueRunner` claims rows through these adapters, and authorized agents may
legitimately rewrite job SQL, request single-attempt cancellation, or pause
services through `wh.queue_config` / `wh.ingest_control`. The trusted ledger
keeps every obligation, so deleting queued rows can only end as outstanding
loss, never as a completed delivery.
"""

from __future__ import annotations

import json
import re
import time

import psycopg2

from src.persistent_scenarios.backend.postgres.workloads.olap import JobControl, JobQueueStore, QueuedJob
from src.workloads.tpcds import get_tpcds_query

from .reports import (
    deliverable_cutoff,
    digest_row_count,
    report_contract,
    streaming_result_digest,
)
from .schema import STAGE_BATCHES

QUEUE_APP_PREFIX = "pg5r-olap-worker"
MAX_ATTEMPTS = 3
DEFAULT_BACKUP_PASS_COUNT = 4
DEFAULT_ATTEMPT_TIMEOUT_SECONDS = 900.0
HEARTBEAT_JOB_PREFIX = "bi_heartbeat_"
PREMATURE_COMPLETION_MARKER_NOTE = "premature completion marker published (upstream ETL race)"
PREMATURE_COMPLETION_MARKER_REASSERT_NOTE = "premature completion marker re-asserted (upstream ETL race)"
# The upstream maintenance pipeline's stated policy for its statistics rebuild
# window: in-flight attempts of the affected report are invalidated
# so they re-execute under the rebuilt statistics. The note states what the
# pipeline did, not why the delivery then dies — the retry-budget burn is the
# discoverable root cause, not a leaked one.
MAINTENANCE_INVALIDATION_NOTE = (
    "statistics rebuild window: in-flight report attempt invalidated for plan refresh "
    "(upstream maintenance pipeline)"
)

_STAGE_BY_BATCH = {spec.batch_id: spec for spec in STAGE_BATCHES}

INGEST_PRIORITY = 10
REQUIRED_REPORT_PRIORITY = 50
HEARTBEAT_PRIORITY = 100


def ingest_stage_spec(batch_id: int):
    spec = _STAGE_BY_BATCH.get(batch_id)
    if spec is None:
        raise KeyError(
            f"no staged batch is provisioned for ingest: batch_id={batch_id}, provisioned={sorted(_STAGE_BY_BATCH)!r}"
        )
    return spec


def ingest_sql(batch_id: int) -> str:
    spec = ingest_stage_spec(batch_id)
    return (
        "INSERT INTO wh.batch_sales (batch_id, line_id, sold_date_sk, item_sk, customer_sk, store_sk, "
        "channel, quantity, net_paid, net_profit) "
        f"SELECT {batch_id}, nextval('wh.batch_line_seq'), stage.sold_date_sk, stage.item_sk, stage.customer_sk, "
        "stage.store_sk, stage.channel, stage.quantity, stage.net_paid, stage.net_profit "
        f"FROM {spec.stage_table} AS stage;"
    )


def heartbeat_job_id(query_id: str, sequence: int) -> str:
    return f"{HEARTBEAT_JOB_PREFIX}{query_id}_{sequence:04d}"


def heartbeat_query_ids() -> tuple[str, ...]:
    return ("q3", "q42", "q52")


def heartbeat_sql(query_id: str) -> str:
    return get_tpcds_query(query_id)


def _wall_now() -> float:
    return time.monotonic()


# ---------------------------------------------------------------------------
# Raw SQL over the public warehouse control tables.
# ---------------------------------------------------------------------------


class QueueTables:
    def __init__(self, env) -> None:
        self._env = env

    def connect(self, role: str):
        return self._env.open_workload_connection(f"{QUEUE_APP_PREFIX}-{role}")

    @staticmethod
    def _fetchone(connection, sql: str, args: tuple = ()) -> tuple | None:
        with connection.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
        connection.rollback()
        return rows[0] if rows else None

    def config_row(self, connection) -> tuple[int, int, bool, bool]:
        row = self._fetchone(
            connection,
            "SELECT max_workers, work_mb, analytics_enabled, backup_enabled FROM wh.queue_config WHERE id = 1;",
        )
        if row is None:
            raise RuntimeError("wh.queue_config lost its single configuration row")
        return int(row[0]), int(row[1]), bool(row[2]), bool(row[3])

    def update_config(self, connection, at: float, **changes: object) -> dict[str, object]:
        allowed = {"max_workers", "work_mb", "analytics_enabled", "backup_enabled"}
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"unsupported queue config fields: {sorted(unknown)!r}")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT max_workers, work_mb, analytics_enabled, backup_enabled FROM wh.queue_config WHERE id = 1;"
            )
            old = cursor.fetchone()
            assignments = ", ".join(f"{name} = %s" for name in changes)
            cursor.execute(f"UPDATE wh.queue_config SET {assignments} WHERE id = 1;", tuple(changes.values()))
            cursor.execute(
                "SELECT max_workers, work_mb, analytics_enabled, backup_enabled FROM wh.queue_config WHERE id = 1;"
            )
            new = cursor.fetchone()
            cursor.execute(
                "INSERT INTO wh.config_audit (changed_at, table_name, old_row, new_row) VALUES (%s, %s, %s, %s);",
                (at, "wh.queue_config", json.dumps(old, default=str), json.dumps(new, default=str)),
            )
        connection.commit()
        return dict(zip(("max_workers", "work_mb", "analytics_enabled", "backup_enabled"), new))

    def update_ingest_control(self, connection, batch_id: int, analyze_after_ingest: bool, at: float) -> dict[str, object]:
        with connection.cursor() as cursor:
            cursor.execute("SELECT analyze_after_ingest FROM wh.ingest_control WHERE batch_id = %s;", (batch_id,))
            old = cursor.fetchone()
            cursor.execute(
                "UPDATE wh.ingest_control SET analyze_after_ingest = %s WHERE batch_id = %s;",
                (analyze_after_ingest, batch_id),
            )
            cursor.execute(
                "INSERT INTO wh.config_audit (changed_at, table_name, old_row, new_row) VALUES (%s, %s, %s, %s);",
                (at, "wh.ingest_control", json.dumps(old, default=str),
                 json.dumps({"batch_id": batch_id, "analyze_after_ingest": analyze_after_ingest})),
            )
        connection.commit()
        return {"batch_id": batch_id, "analyze_after_ingest": analyze_after_ingest}

    def execute_release_sql(self, connection, sql: str, audit_table: str, at: float) -> None:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            cursor.execute(
                "INSERT INTO wh.config_audit (changed_at, table_name, old_row, new_row) VALUES (%s, %s, %s, %s);",
                (at, audit_table, "", sql),
            )
        connection.commit()

    def database_guc_value(self, connection, guc_name: str) -> str:
        """Effective value on a FRESH session: the only probe that sees
        database/role-scoped settings (existing sessions keep their startup
        values, so the agent-facing surface decouples from the release)."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_setting(%s);", (guc_name,))
            row = cursor.fetchone()
        connection.rollback()
        return str(row[0])

    def audit_release(self, connection, at: float, audit_table: str, old_row: str, new_row: str) -> dict[str, object]:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO wh.config_audit (changed_at, table_name, old_row, new_row) VALUES (%s, %s, %s, %s) "
                "RETURNING audit_id;",
                (at, audit_table, old_row, new_row),
            )
            audit_id = int(cursor.fetchone()[0])
        connection.commit()
        return {"audit_id": audit_id, "table_name": audit_table, "old_row": old_row, "new_row": new_row}

    def enqueue_row(self, connection, job_id: str, job_type: str, report_id: str, batch_cutoff: int | None,
                    sql_text: str, submit_at: float, deadline: float, priority: int) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO wh.report_queue (job_id, job_type, report_id, batch_cutoff, sql_text, "
                "submit_at, deadline, status, attempts, cancel_requested, priority) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, 'queued', 0, false, %s);",
                (job_id, job_type, report_id, batch_cutoff, sql_text, submit_at, deadline, priority),
            )

    def claimed_row(self, connection, job_type: str, worker_id: str, pid: int,
                    report_id_prefix: str | None = None) -> tuple | None:
        if report_id_prefix is None:
            kind_filter = "job_type = %s"
            args: list = [job_type]
        elif report_id_prefix.startswith("!"):
            kind_filter = "job_type = %s AND report_id NOT LIKE %s"
            args = [job_type, f"{report_id_prefix[1:]}%"]
        else:
            kind_filter = "job_type = %s AND report_id LIKE %s"
            args = [job_type, f"{report_id_prefix}%"]
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE wh.report_queue SET status = 'running', claimed_by = %s, claim_pid = %s, attempts = attempts + 1 "
                "WHERE job_id = ("
                "  SELECT job_id FROM wh.report_queue"
                f"  WHERE {kind_filter} AND status = 'queued'"
                "  ORDER BY priority, job_id LIMIT 1 FOR UPDATE SKIP LOCKED"
                ") RETURNING job_id, report_id, batch_cutoff, sql_text, submit_at, deadline, attempts;",
                (worker_id, pid) + tuple(args),
            )
            rows = cursor.fetchall()
        return rows[0] if rows else None

    def job_state(self, connection, job_id: str) -> tuple[str, bool, int]:
        row = self._fetchone(
            connection,
            "SELECT sql_text, cancel_requested, attempts FROM wh.report_queue WHERE job_id = %s;",
            (job_id,),
        )
        if row is None:
            raise RuntimeError(f"claimed queue row disappeared during execution: job_id={job_id!r}")
        return str(row[0]), bool(row[1]), int(row[2])

    def job_status(self, connection, job_id: str) -> str:
        row = self._fetchone(
            connection,
            "SELECT status FROM wh.report_queue WHERE job_id = %s;",
            (job_id,),
        )
        if row is None:
            raise RuntimeError(f"claimed queue row disappeared during execution: job_id={job_id!r}")
        return str(row[0])

    def requeue_row(self, connection, job_id: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE wh.report_queue SET status = 'queued', claimed_by = NULL, claim_pid = NULL, "
                "cancel_requested = false WHERE job_id = %s;", (job_id,)
            )
        connection.commit()

    def fail_row(self, connection, job_id: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE wh.report_queue SET status = 'failed' WHERE job_id = %s;", (job_id,))
        connection.commit()

    def deliver_report_row(self, connection, job_id: str, report_id: str, batch_cutoff: int | None,
                           delivered_at: float, result_digest: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE wh.report_queue SET status = 'delivered' WHERE job_id = %s;", (job_id,))
            cursor.execute(
                "INSERT INTO wh.report_result (job_id, report_id, batch_cutoff, delivered_at, row_count, result_digest) "
                "VALUES (%s, %s, %s, %s, %s, %s);",
                (job_id, report_id, batch_cutoff, delivered_at, digest_row_count(result_digest), result_digest),
            )

    def mark_delivered(self, connection, job_id: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE wh.report_queue SET status = 'delivered' WHERE job_id = %s;", (job_id,))

    def deliver_backup_row(self, connection, job_id: str, delivered_at: float, payload: dict) -> None:
        with connection.cursor() as cursor:
            self.mark_delivered(connection, job_id)
            cursor.execute(
                "INSERT INTO wh.backup_result (job_id, passes, bytes_read, digest, finished_at) "
                "VALUES (%s, %s, %s, %s, %s);",
                (job_id, payload["passes"], payload["bytes_read"], payload["passes_digest"], delivered_at),
            )

    def cancel_requested_running(self, connection) -> tuple[tuple[str, int], ...]:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT job_id, claim_pid FROM wh.report_queue "
                "WHERE status = 'running' AND cancel_requested = true AND claim_pid IS NOT NULL;"
            )
            rows = cursor.fetchall()
        connection.rollback()
        return tuple((str(row[0]), int(row[1])) for row in rows)

    def cancel_backend(self, connection, pid: int) -> None:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_cancel_backend(%s);", (pid,))
        connection.rollback()

    def ingest_control_analyze(self, connection, batch_id: int) -> bool:
        row = self._fetchone(
            connection, "SELECT analyze_after_ingest FROM wh.ingest_control WHERE batch_id = %s;", (batch_id,)
        )
        if row is None:
            raise RuntimeError(f"wh.ingest_control must hold exactly one row per batch: batch_id={batch_id}, rows=0")
        return bool(row[0])

    def analyze_fact_table(self, connection) -> None:
        with connection.cursor() as cursor:
            cursor.execute("ANALYZE wh.batch_sales;")
        connection.commit()

    def record_batch_registry(self, connection, batch_id: int, started_at: float, finished_at: float,
                              analyzed_at: float | None, row_count: int) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE wh.batch_registry SET ingest_started_at = %s, ingest_finished_at = %s, "
                "analyzed_at = %s, row_count = %s WHERE batch_id = %s;",
                (started_at, finished_at, analyzed_at, row_count, batch_id),
            )
        connection.commit()

    def batch_registry_state(self, connection, batch_id: int) -> dict[str, object]:
        row = self._fetchone(
            connection,
            "SELECT ingest_started_at, ingest_finished_at, analyzed_at, row_count "
            "FROM wh.batch_registry WHERE batch_id = %s;",
            (batch_id,),
        )
        if row is None:
            raise RuntimeError(
                f"wh.batch_registry lost its declared staged-batch row: batch_id={batch_id}, rows=0"
            )
        return {
            "batch_id": batch_id,
            "ingest_started_at": row[0],
            "ingest_finished_at": row[1],
            "analyzed_at": row[2],
            "row_count": int(row[3]),
        }

    def batch_ingest_state(self, connection, batch_id: int, job_id: str) -> dict[str, object]:
        """Authoritative ingest-progress fact: queue row status plus registry truth.

        ``in_flight`` is the publish precondition of the premature completion
        marker: only a batch whose ingest row is still open AND whose registry
        still carries no completion can be lied about transiently — the real
        ``record_batch_registry`` at ingest completion overwrites the lie.
        """
        row = self._fetchone(
            connection, "SELECT status FROM wh.report_queue WHERE job_id = %s;", (job_id,)
        )
        if row is None:
            raise RuntimeError(
                f"ingest queue row missing while inspecting batch progress: job_id={job_id!r}"
            )
        status = str(row[0])
        registry = self.batch_registry_state(connection, batch_id)
        return {
            "job_id": job_id,
            "queue_status": status,
            **registry,
            "in_flight": status in ("queued", "running") and registry["ingest_finished_at"] is None,
        }

    def publish_premature_registry_marker(self, connection, batch_id: int, marker_at: float) -> dict[str, object] | None:
        """Upstream ETL race: publish completion into the registry before the ingest lands.

        Updates the declared timestamps to the marker instant and audits the lie
        into wh.config_audit. The UPDATE is guarded exactly like the re-assert:
        it only fires while the registry row carries no real ingest start (the
        real record_batch_registry writes ingest_started_at, the lie never does)
        and the ingest obligation is still open, so a true completion that lands
        between the capability's observation and this statement can never be
        overwritten. Returns the before/after facts, or None when the guard
        blocked the publish (race lost — the caller turns that into prevented
        evidence, never a synthesized lie).
        """
        before = self.batch_registry_state(connection, batch_id)
        updated = self._guarded_marker_update(connection, batch_id, marker_at)
        if not updated:
            connection.rollback()
            return None
        audit = self.audit_release(
            connection,
            marker_at,
            "wh.batch_registry",
            json.dumps(before, default=str),
            json.dumps(
                {
                    "note": PREMATURE_COMPLETION_MARKER_NOTE,
                    "batch_id": batch_id,
                    "ingest_finished_at": marker_at,
                    "analyzed_at": marker_at,
                },
                default=str,
            ),
        )
        return {"batch_id": batch_id, "marker_at": marker_at, "before": before, **audit}

    def reassert_premature_registry_marker(self, connection, batch_id: int, marker_at: float) -> bool:
        """Re-assert the premature lie one cadence step later, guarded.

        The transient lie must stay observable across inspection cycles for the
        whole trap window [marker publish, real ingest completion], so the
        upstream publisher re-stamps the completion while the ingest is still
        open. Each re-assert audits its own wh.config_audit row, which is what
        makes the window reproducible after the real completion overwrites the
        row. Returns False — without writing anything — once the truth landed
        (ingest_started_at set by the real ingest) or the ingest obligation is
        no longer open; the guard lives inside the UPDATE, so a re-assert over
        the true completion is impossible by construction.
        """
        if not self._guarded_marker_update(connection, batch_id, marker_at):
            connection.rollback()
            return False
        self.audit_release(
            connection,
            marker_at,
            "wh.batch_registry",
            "",
            json.dumps(
                {
                    "note": PREMATURE_COMPLETION_MARKER_REASSERT_NOTE,
                    "batch_id": batch_id,
                    "ingest_finished_at": marker_at,
                    "analyzed_at": marker_at,
                },
                default=str,
            ),
        )
        return True

    def _guarded_marker_update(self, connection, batch_id: int, marker_at: float) -> list:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE wh.batch_registry SET ingest_finished_at = %s, analyzed_at = %s "
                "WHERE batch_id = %s AND ingest_started_at IS NULL "
                "AND EXISTS (SELECT 1 FROM wh.report_queue WHERE job_id = %s "
                "            AND status IN ('queued', 'running')) "
                "RETURNING batch_id;",
                (marker_at, marker_at, batch_id, f"ingest_batch_{batch_id}"),
            )
            return cursor.fetchall()

    def maintenance_attempt_state(self, connection, job_id: str) -> dict[str, object] | None:
        """Public queue-row state of one report job (None when the row is absent)."""
        row = self._fetchone(
            connection,
            "SELECT status, cancel_requested, attempts FROM wh.report_queue WHERE job_id = %s;",
            (job_id,),
        )
        if row is None:
            return None
        return {"status": str(row[0]), "cancel_requested": bool(row[1]), "attempts": int(row[2])}

    def invalidate_running_attempt(self, connection, job_id: str, at: float) -> bool:
        """Maintenance-pipeline attempt invalidation: request cancellation of the
        attempt currently executing ``job_id`` and audit the write.

        The UPDATE is guarded on status='running' AND cancel_requested=false, so
        an already-flagged or already-terminal row is never double-counted.
        Returns False when nothing was invalidated.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE wh.report_queue SET cancel_requested = true "
                "WHERE job_id = %s AND status = 'running' AND cancel_requested = false "
                "RETURNING job_id;",
                (job_id,),
            )
            invalidated = cursor.fetchall()
        if not invalidated:
            connection.rollback()
            return False
        self.audit_release(
            connection,
            at,
            "wh.report_queue",
            "",
            json.dumps({"note": MAINTENANCE_INVALIDATION_NOTE, "job_id": job_id}, sort_keys=True),
        )
        return True


def _backend_pid(connection) -> int:
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_backend_pid();")
        pid = int(cursor.fetchone()[0])
    connection.commit()
    return pid


# ---------------------------------------------------------------------------
# Job bodies. They receive the connection the runner claimed with and own their
# commit boundaries; a raising body must leave the row consistent first.
# ---------------------------------------------------------------------------


def make_report_run(tables: QueueTables, *, attempt_timeout_seconds: float):
    """Report body: live queue-row SQL, control-table work_mem, declared digest."""

    def run(job: QueuedJob, connection) -> str:
        sql_text, _cancel_requested, _attempts = tables.job_state(connection, job.job_id)
        _max_workers, work_mb, _analytics, _backup = tables.config_row(connection)
        ordered = bool((job.input_snapshot or {}).get("ordered", True))
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SET LOCAL work_mem = '{work_mb}MB';")
                cursor.execute(f"SET LOCAL statement_timeout = '{int(attempt_timeout_seconds * 1000)}ms';")
                cursor.execute(sql_text)
                digest = streaming_result_digest(cursor, ordered=ordered)
        except psycopg2.errors.QueryCanceled:
            connection.rollback()
            _sql, cancel_requested, attempts = tables.job_state(connection, job.job_id)
            if cancel_requested and attempts < MAX_ATTEMPTS:
                tables.requeue_row(connection, job.job_id)
            else:
                tables.fail_row(connection, job.job_id)
            raise
        connection.rollback()
        return digest

    return run


def make_ingest_run(tables: QueueTables, job_id: str, batch_id: int, *, attempt_timeout_seconds: float):
    """Ingest body: staged batch load, optional statistics maintenance, registry fact."""

    def run(job: QueuedJob, connection) -> str:
        spec = ingest_stage_spec(batch_id)
        with connection.cursor() as cursor:
            cursor.execute(f"SET LOCAL statement_timeout = '{int(attempt_timeout_seconds * 1000)}ms';")
            cursor.execute(
                "INSERT INTO wh.batch_sales (batch_id, line_id, sold_date_sk, item_sk, customer_sk, store_sk, "
                "channel, quantity, net_paid, net_profit) "
                "SELECT %s, nextval('wh.batch_line_seq'), stage.sold_date_sk, stage.item_sk, stage.customer_sk, "
                "stage.store_sk, stage.channel, stage.quantity, stage.net_paid, stage.net_profit "
                f"FROM {spec.stage_table} AS stage;",
                (batch_id,),
            )
            inserted = cursor.rowcount
        connection.commit()
        analyze_requested = tables.ingest_control_analyze(connection, batch_id)
        analyzed_at = None
        if analyze_requested:
            tables.analyze_fact_table(connection)
            analyzed_at = _wall_now()
        tables.record_batch_registry(connection, batch_id, job.submitted_at_monotonic, _wall_now(),
                                     analyzed_at, int(inserted))
        tables.mark_delivered(connection, job_id)
        connection.commit()
        return f"ingest:{int(inserted)}"

    return run


def make_backup_run(tables: QueueTables, job_id: str, *, backup_pass_count: int, attempt_timeout_seconds: float):
    """Backup body: repeated full-fact verification reads producing a checkable digest."""

    def run(job: QueuedJob, connection) -> str:
        pass_facts: list[list[tuple[str, int]]] = []
        with connection.cursor() as cursor:
            # A backup reads one stable snapshot: repeatable read pins one MVCC
            # snapshot for every pass, so a batch committing mid-backup cannot
            # split the artifact across two logical states.
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            cursor.execute(f"SET LOCAL statement_timeout = '{int(attempt_timeout_seconds * 1000)}ms';")
            for _ in range(backup_pass_count):
                cursor.execute("SELECT count(*), COALESCE(sum(hashtext(line_id::text)), 0) FROM wh.batch_sales;")
                row = cursor.fetchone()
                facts = [("fact_rows", int(row[0])), ("fact_digest", int(row[1]))]
                cursor.execute("SELECT pg_total_relation_size('wh.batch_sales');")
                facts.append(("fact_bytes", int(cursor.fetchone()[0])))
                pass_facts.append(facts)
        connection.rollback()
        payload = {
            "passes": backup_pass_count,
            "bytes_read": pass_facts[0][2][1],
            "passes_digest": json.dumps(pass_facts, sort_keys=True, default=str),
        }
        tables.deliver_backup_row(connection, job_id, _wall_now(), payload)
        connection.commit()
        return json.dumps(payload, sort_keys=True)

    return run


# ---------------------------------------------------------------------------
# Core JobQueueStore adapters, one per service runner.
# ---------------------------------------------------------------------------


class ReportQueueStore(JobQueueStore):
    """Report + heartbeat service: concurrency and pause come from `wh.queue_config`."""

    def __init__(self, tables: QueueTables, *, attempt_timeout_seconds: float = DEFAULT_ATTEMPT_TIMEOUT_SECONDS) -> None:
        self._tables = tables
        self._attempt_timeout_seconds = attempt_timeout_seconds

    def enqueue(self, job: QueuedJob, connection) -> None:
        snapshot = dict(job.input_snapshot or {})
        report_id = re.sub(r"_batch\d+$", "", job.job_id)
        cutoff = deliverable_cutoff(job.job_id) if re.search(r"_batch\d+$", job.job_id) else None
        priority = HEARTBEAT_PRIORITY if job.job_kind == "heartbeat" else REQUIRED_REPORT_PRIORITY
        self._tables.enqueue_row(
            connection, job.job_id, "report", report_id, cutoff,
            snapshot.get("sql", ""), job.submitted_at_monotonic, job.deadline_at_monotonic, priority,
        )

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        row = self._tables.claimed_row(connection, "report", worker_id, _backend_pid(connection),
                                       report_id_prefix=f"!{HEARTBEAT_JOB_PREFIX}")
        if row is None:
            return None
        job_id, _report_id, _cutoff, _sql, submit_at, deadline, _attempts = row
        ordered = report_contract(str(_report_id)).ordered if not str(job_id).startswith(HEARTBEAT_JOB_PREFIX) else True
        return QueuedJob(
            job_id=str(job_id),
            job_kind="report",
            submitted_at_monotonic=float(submit_at),
            deadline_at_monotonic=float(deadline),
            run=make_report_run(self._tables, attempt_timeout_seconds=self._attempt_timeout_seconds),
            batch_version=None,
            input_snapshot={"ordered": ordered},
        )

    def record_result(self, job_id: str, result_digest: str, connection) -> None:
        row = self._tables._fetchone(
            connection, "SELECT report_id, batch_cutoff FROM wh.report_queue WHERE job_id = %s;", (job_id,)
        )
        if row is None:
            raise RuntimeError(f"cannot record a result for an unknown job: job_id={job_id!r}")
        self._tables.deliver_report_row(
            connection, job_id, str(row[0]), row[1], _wall_now(), result_digest
        )
        connection.commit()

    def read_control(self, connection) -> JobControl:
        max_workers, _work_mb, analytics_enabled, _backup = self._tables.config_row(connection)
        return JobControl(max_concurrency=max_workers, paused=not analytics_enabled)

    def failure_disposition(self, connection, job: QueuedJob) -> str:
        # Only the report body requeues (authorized single-attempt cancellation):
        # a row back at 'queued' will be retried, anything else is final.
        return "retry" if self._tables.job_status(connection, job.job_id) == "queued" else "final"


class IngestQueueStore(JobQueueStore):
    """Batch ingest service: one worker; never paused by the analytics switch."""

    def __init__(self, tables: QueueTables, *, attempt_timeout_seconds: float = DEFAULT_ATTEMPT_TIMEOUT_SECONDS) -> None:
        self._tables = tables
        self._attempt_timeout_seconds = attempt_timeout_seconds

    def enqueue(self, job: QueuedJob, connection) -> None:
        batch_id = int(job.batch_version)
        self._tables.enqueue_row(
            connection, job.job_id, "ingest", f"ingest_batch_{batch_id}", batch_id,
            ingest_sql(batch_id), job.submitted_at_monotonic, job.deadline_at_monotonic, INGEST_PRIORITY,
        )

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        row = self._tables.claimed_row(connection, "ingest", worker_id, _backend_pid(connection))
        if row is None:
            return None
        job_id, _report_id, batch_cutoff, _sql, submit_at, deadline, _attempts = row
        batch_id = int(batch_cutoff)
        spec = ingest_stage_spec(batch_id)
        return QueuedJob(
            job_id=str(job_id),
            job_kind="ingest",
            submitted_at_monotonic=float(submit_at),
            deadline_at_monotonic=float(deadline),
            run=make_ingest_run(self._tables, str(job_id), batch_id,
                                attempt_timeout_seconds=self._attempt_timeout_seconds),
            batch_version=str(batch_id),
            input_snapshot={"stage_table": spec.stage_table, "expected_rows": spec.row_count},
        )

    def record_result(self, job_id: str, result_digest: str, connection) -> None:
        self._tables.mark_delivered(connection, job_id)
        connection.commit()

    def read_control(self, connection) -> JobControl:
        return JobControl(max_concurrency=1, paused=False)


class BackupQueueStore(JobQueueStore):
    """Backup verification service: paused through `backup_enabled`."""

    def __init__(self, tables: QueueTables, *, backup_pass_count: int = DEFAULT_BACKUP_PASS_COUNT,
                 attempt_timeout_seconds: float = DEFAULT_ATTEMPT_TIMEOUT_SECONDS) -> None:
        self._tables = tables
        self._backup_pass_count = backup_pass_count
        self._attempt_timeout_seconds = attempt_timeout_seconds

    def enqueue(self, job: QueuedJob, connection) -> None:
        self._tables.enqueue_row(
            connection, job.job_id, "backup", "routine_backup_read", None,
            "multi_pass_verification_read", job.submitted_at_monotonic, job.deadline_at_monotonic, INGEST_PRIORITY,
        )

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        row = self._tables.claimed_row(connection, "backup", worker_id, _backend_pid(connection))
        if row is None:
            return None
        job_id, _report_id, _cutoff, _sql, submit_at, deadline, _attempts = row
        return QueuedJob(
            job_id=str(job_id),
            job_kind="backup",
            submitted_at_monotonic=float(submit_at),
            deadline_at_monotonic=float(deadline),
            run=make_backup_run(self._tables, str(job_id), backup_pass_count=self._backup_pass_count,
                                attempt_timeout_seconds=self._attempt_timeout_seconds),
            batch_version=None,
            input_snapshot={"passes": self._backup_pass_count},
        )

    def record_result(self, job_id: str, result_digest: str, connection) -> None:
        # The backup body already inserted wh.backup_result and committed its
        # delivery; a second INSERT here violates the pkey and kills the worker.
        # Ingest-style idempotent mark only.
        self._tables.mark_delivered(connection, job_id)
        connection.commit()

    def read_control(self, connection) -> JobControl:
        _max_workers, _work_mb, _analytics, backup_enabled = self._tables.config_row(connection)
        return JobControl(max_concurrency=1, paused=not backup_enabled)


class HeartbeatQueueStore(JobQueueStore):
    """BI heartbeat service: only the `bi_heartbeat_*` rows; paused with analytics."""

    def __init__(self, tables: QueueTables, *, attempt_timeout_seconds: float = DEFAULT_ATTEMPT_TIMEOUT_SECONDS) -> None:
        self._tables = tables
        self._attempt_timeout_seconds = attempt_timeout_seconds

    def enqueue(self, job: QueuedJob, connection) -> None:
        snapshot = dict(job.input_snapshot or {})
        self._tables.enqueue_row(
            connection, job.job_id, "report", job.job_id, None,
            snapshot.get("sql", ""), job.submitted_at_monotonic, job.deadline_at_monotonic, HEARTBEAT_PRIORITY,
        )

    def claim(self, worker_id: str, connection) -> QueuedJob | None:
        row = self._tables.claimed_row(connection, "report", worker_id, _backend_pid(connection),
                                       report_id_prefix=HEARTBEAT_JOB_PREFIX)
        if row is None:
            return None
        job_id, _report_id, _cutoff, _sql, submit_at, deadline, _attempts = row
        return QueuedJob(
            job_id=str(job_id),
            job_kind="heartbeat",
            submitted_at_monotonic=float(submit_at),
            deadline_at_monotonic=float(deadline),
            run=make_report_run(self._tables, attempt_timeout_seconds=self._attempt_timeout_seconds),
            batch_version=None,
            input_snapshot={"ordered": True},
        )

    def record_result(self, job_id: str, result_digest: str, connection) -> None:
        row = self._tables._fetchone(
            connection, "SELECT report_id, batch_cutoff FROM wh.report_queue WHERE job_id = %s;", (job_id,)
        )
        if row is None:
            raise RuntimeError(f"cannot record a result for an unknown job: job_id={job_id!r}")
        self._tables.deliver_report_row(
            connection, job_id, str(row[0]), row[1], _wall_now(), result_digest
        )
        connection.commit()

    def read_control(self, connection) -> JobControl:
        _max_workers, _work_mb, analytics_enabled, _backup = self._tables.config_row(connection)
        return JobControl(max_concurrency=1, paused=not analytics_enabled)
