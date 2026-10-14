"""Frozen-history TiCDC timezone-DDL and downstream backpressure Case."""

from __future__ import annotations

import re
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass, replace
from urllib.error import HTTPError

from src.scenarios.evaluation.tidb.business_change.timezone_ddl_backpressure_frozen_history import (
    TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryEvaluatorCase,
    TidbBusinessChangeTimezoneDdlBackpressureReducedHistoryEvaluatorCase,
)
from src.execution.history.records import HistoricalRecordSource
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    require_sql_success,
    validate_sql_identifier,
)
from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase, WorkloadProfile

from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.specs import TiDBReplicationRuntime
from src.execution.tidb_runtime import MYSQL_8_4, TICDC_V8_1_0, TIDB_V8_1_0, tidb_runtime


SCENARIO_ID = "tidb_business_change_timezone_ddl_backpressure_frozen_history"
SOURCE_DB = "benchops_mf_cf01"
SOURCE_TABLE = "mf_cf01_events"
DDL_TABLE = "mf_cf01_order_cutover"
DECOY_TABLE = "mf_cf01_archive_events"
SCHEMA_ROLLOUT_TABLES = (
    "mf_cf01_cutover_shadow",
    "mf_cf01_archive_rollup",
)
CHANGEFEED_ID = "mf-dr-cutover"
BUSINESS_TRIGGER = "mf_cf01_order_audit"
ARCHIVE_TRIGGER = "mf_cf01_archive_audit"
LIVE_WRITER_ID = 100_000_000_000_000_001
SEEDED_ROWS = 64
POST_FAULT_ROWS = 32


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryForHistoryInvestigationScenarioCase(TiDBScenarioCase):
    source_db: str
    source_table: str
    ddl_table: str
    decoy_table: str
    schema_rollout_tables: tuple[str, ...]
    changefeed_id: str
    business_trigger: str
    archive_trigger: str
    live_writer_id: int
    seeded_rows: int
    post_fault_rows: int
    ddl_delay_seconds: float


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="mf_cf01_business_summary",
            sql=(
                f"SELECT state, COUNT(*), COALESCE(SUM(amount), 0) "
                f"FROM {SOURCE_DB}.{SOURCE_TABLE} GROUP BY state ORDER BY state"
            ),
            qps=0.55,
            tier="OLTP_CORE",
            application_name="cutover-order-api",
        ),
        WorkloadProfile(
            name="mf_cf01_recent_events",
            sql=(
                f"SELECT COUNT(*), MIN(id), MAX(id) FROM {SOURCE_DB}.{SOURCE_TABLE} "
                "WHERE updated_at >= NOW() - INTERVAL 1 HOUR"
            ),
            qps=0.70,
            tier="OLTP_CORE",
            application_name="cutover-order-api",
        ),
        WorkloadProfile(
            name="mf_cf01_archive_report",
            sql=(
                f"SELECT tenant_id, COUNT(*), COALESCE(SUM(amount), 0) "
                f"FROM {SOURCE_DB}.{DECOY_TABLE} GROUP BY tenant_id ORDER BY tenant_id"
            ),
            qps=0.65,
            tier="OLAP_BURST",
            application_name="archive-reporting",
        ),
        WorkloadProfile(
            name="mf_cf01_schema_probe",
            sql=f"SHOW CREATE TABLE {SOURCE_DB}.{SOURCE_TABLE}",
            qps=0.45,
            tier="DDL_MAINTENANCE_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="mf_cf01_ddl_history_probe",
            sql="ADMIN SHOW DDL JOBS 10",
            qps=0.25,
            tier="DDL_MAINTENANCE_OBSERVABILITY",
            application_name="schema-observer",
        ),
        WorkloadProfile(
            name="mf_cf01_tso_probe",
            sql="SELECT TIDB_CURRENT_TSO(), NOW(), @@session.time_zone",
            qps=0.90,
            tier="REPLICATION_OBSERVABILITY",
            application_name="cutover-controller",
        ),
        WorkloadProfile(
            name="mf_cf01_live_writer",
            sql=(
                f"REPLACE INTO {SOURCE_DB}.{SOURCE_TABLE} "
                "(id, amount, state, updated_at, note) VALUES "
                f"({LIVE_WRITER_ID}, 1.00, 'paid', '2026-08-16 00:00:00', 'live-writer-stable')"
            ),
            qps=0.20,
            tier="OLTP_CORE",
            commit=True,
            application_name="cutover-order-writer",
        ),
    ),
    worker_count=2,
    seed=20260816,
    start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    warmup_seconds=180,
)


_FROZEN_HISTORY_HISTORY = FrozenHistorySpec(
    schema_version=1,
    duration_seconds=12 * 60 * 60,
    normal_capture_seconds=600,
    fault_capture_seconds=600,
    base_step_seconds=120,
    overview_step_seconds=120,
    block_min_seconds=120,
    block_max_seconds=120,
    transition_seconds=120,
    target_age_seconds_range=(2400, 7200),
    required_metrics=("qps", "query_latency"),
    record_sources=(
        HistoricalRecordSource.COMPONENT_LOG,
        HistoricalRecordSource.TOPSQL,
        HistoricalRecordSource.SLOW_QUERIES,
    ),
    decoys=(
        HistoryDecoySpec(
            decoy_id="source-latency-catchup",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=2,
            duration_seconds=120,
            minimum_deviation_mad=0.5,
        ),
        HistoryDecoySpec(
            decoy_id="archive-report-latency",
            kind=DecoyKind.CAPTURED_BENIGN,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=2,
            duration_seconds=120,
            minimum_deviation_mad=0.5,
        ),
        HistoryDecoySpec(
            decoy_id="clean-ddl-latency",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=1,
            duration_seconds=120,
            amplitude_mad=1.5,
        ),
        HistoryDecoySpec(
            decoy_id="owner-handoff-latency-dip",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.DIP,
            count=2,
            duration_seconds=120,
            amplitude_mad=2.0,
        ),
        HistoryDecoySpec(
            decoy_id="archive-report-latency-spike",
            kind=DecoyKind.METRIC_ONLY,
            metric="query_latency",
            field="p95_ms",
            target=None,
            direction=DecoyDirection.SPIKE,
            count=2,
            duration_seconds=120,
            amplitude_mad=1.8,
        ),
    ),
    max_points_per_series=7200,
    max_scalar_samples_per_response=12000,
    max_history_records_per_response=240,
)


_REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "root_cause",
                "factor": "historical_target_window",
                "entity": CHANGEFEED_ID,
                "evidence": ["The bounded historical window shows the target episode rather than only the current snapshot."],
            },
            {
                "type": "root_cause",
                "factor": "pre_ddl_sink_backpressure",
                "entity": f"{DECOY_TABLE} excluded; {SOURCE_TABLE} downstream sink",
                "evidence": ["A real SLEEP trigger on the business table reduces sink capacity before the DDL failure."],
            },
            {
                "type": "root_cause",
                "factor": "timezone_sensitive_ddl",
                "entity": f"{CHANGEFEED_ID}/{DDL_TABLE}",
                "evidence": ["TiCDC history contains Error 1067 and the unique failed CommitTs for the UTC timestamp DDL."],
            },
            {
                "type": "root_cause",
                "factor": "ddl_checkpoint_block",
                "entity": CHANGEFEED_ID,
                "evidence": ["Checkpoint stops at the failed TSO while resolved progress continues and the REST state can remain NORMAL."],
            },
            {
                "type": "root_cause",
                "factor": "temporal_cascade",
                "entity": f"{CHANGEFEED_ID}/{SOURCE_TABLE}",
                "evidence": ["The sink deficit precedes the timezone DDL failure; later source writes remain in the backlog."],
            },
            {
                "type": "root_cause",
                "factor": "scope_exclusion",
                "entity": "healthy TiDB topology and archive trigger",
                "evidence": ["Cluster health and the non-sleep archive trigger exclude unrelated components and the archive table."],
            },
            {
                "type": "root_cause",
                "factor": "post_ddl_dml_preservation",
                "entity": SOURCE_TABLE,
                "evidence": ["The source and downstream row truth includes seeded, post-DDL, and live-writer rows."],
            },
        ]
    },
    "outcome": {
        "changes": [
            "created an equivalent downstream TIMESTAMP definition using the downstream timezone representation",
            "recreated the target changefeed from failed CommitTs plus one",
            "removed only the business-table slow-write trigger",
        ],
        "verification": [
            "the target changefeed is NORMAL with no error and has caught up",
            "source and downstream business rows, including the live-writer row, are equal",
            "the protected archive trigger remains present and has no sleep delay",
        ],
    },
    "summary": "The historical evidence links sink backpressure before a timezone-sensitive DDL failure; recovery preserves the cutover-window rows and the unrelated archive trigger.",
}


class TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryInjector(BaseFaultInjector):

    retain_workload_after_metric_history = True

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""
    """Create the target tables and schedule the real fault inside the capture window."""

    def __init__(self) -> None:
        self.source_db = ""
        self.source_table = ""
        self.ddl_table = ""
        self.decoy_table = ""
        self.schema_rollout_tables: tuple[str, ...] = ()
        self.changefeed_id = ""
        self.business_trigger = ""
        self.archive_trigger = ""
        self.seeded_rows = 0
        self.post_fault_rows = 0
        self.ddl_delay_seconds = 0.0
        self.ddl_commit_ts: int | None = None
        self._configured = False
        self._episode_thread: threading.Thread | None = None
        self._episode_error: BaseException | None = None
        self._stop_event = threading.Event()
        self._evidence: dict[str, object] = {}

    def _configure(self, config: Mapping[str, object]) -> None:
        self.source_db = validate_sql_identifier(str(config["source_db"]), "source_db")
        self.source_table = validate_sql_identifier(str(config["source_table"]), "source_table")
        self.ddl_table = validate_sql_identifier(str(config["ddl_table"]), "ddl_table")
        self.decoy_table = validate_sql_identifier(str(config["decoy_table"]), "decoy_table")
        self.schema_rollout_tables = tuple(
            validate_sql_identifier(str(table), "schema_rollout_table")
            for table in config["schema_rollout_tables"]
        )
        self.changefeed_id = str(config["changefeed_id"])
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", self.changefeed_id):
            raise ValueError(f"Invalid TiCDC changefeed_id: changefeed_id={self.changefeed_id!r}")
        self.business_trigger = validate_sql_identifier(str(config["business_trigger"]), "business_trigger")
        self.archive_trigger = validate_sql_identifier(str(config["archive_trigger"]), "archive_trigger")
        self.seeded_rows = int(config["seeded_rows"])
        self.post_fault_rows = int(config["post_fault_rows"])
        self.ddl_delay_seconds = float(config["ddl_delay_seconds"])
        if self.ddl_delay_seconds <= 0:
            raise ValueError(f"DDL delay must be positive: delay_seconds={self.ddl_delay_seconds!r}")

    @staticmethod
    def _values(start: int, end: int, prefix: str) -> str:
        return ",".join(
            f"({row_id}, {row_id * 10}.00, 'paid', '2026-08-16 00:00:00', '{prefix}-{row_id}')"
            for row_id in range(start, end + 1)
        )

    @staticmethod
    def _run_ticdc_cli(env, arguments: list[str]) -> str:
        return env.get_deployment().exec("ticdc/ticdc-0", ["/cdc", "cli", "changefeed", *arguments])

    @staticmethod
    def _wait_for_status(env, changefeed_id: str, predicate, label: str, timeout: float = 120) -> dict:
        deadline = time.monotonic() + timeout
        last_status = None
        while time.monotonic() < deadline:
            try:
                last_status = env.replication_status(changefeed_id)
            except HTTPError as exc:
                if exc.code == 404:
                    time.sleep(1)
                    continue
                if exc.code == 400:
                    body = exc.read().decode("utf-8", errors="replace")
                    if "CDC:ErrChangeFeedNotExists" in body:
                        time.sleep(1)
                        continue
                    raise RuntimeError(
                        f"TiCDC status request failed: changefeed_id={changefeed_id!r}, http_status={exc.code}, body={body!r}"
                    ) from exc
                body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"TiCDC status request failed: changefeed_id={changefeed_id!r}, http_status={exc.code}, body={body!r}"
                ) from exc
            if predicate(last_status):
                return last_status
            time.sleep(1)
        raise RuntimeError(
            f"TiCDC status did not reach {label}: changefeed_id={changefeed_id!r}, last_status={last_status!r}"
        )

    def _setup_upstream(self, env) -> None:
        require_sql_success(env.execute_sql(f"DROP DATABASE IF EXISTS {self.source_db}"), "clear frozen-history source schema")
        require_sql_success(env.execute_sql(f"CREATE DATABASE {self.source_db}"), "create frozen-history source schema")
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.source_db}.{self.source_table} ("
                "id BIGINT PRIMARY KEY, amount DECIMAL(12,2) NOT NULL, state VARCHAR(16) NOT NULL, "
                "updated_at DATETIME NOT NULL, note VARCHAR(255) NOT NULL)"
            ),
            "create frozen-history business table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.source_db}.{self.decoy_table} ("
                "id BIGINT PRIMARY KEY, tenant_id BIGINT NOT NULL, amount DECIMAL(12,2) NOT NULL, "
                "updated_at DATETIME NOT NULL, note VARCHAR(255) NOT NULL)"
            ),
            "create frozen-history archive table",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.source_db}.{self.source_table} "
                f"(id, amount, state, updated_at, note) VALUES {self._values(1, self.seeded_rows, 'seed')}"
            ),
            "seed frozen-history business rows",
        )
        archive_values = ",".join(
            f"({row_id}, {row_id % 7}, {row_id * 3}.00, '2026-08-16 00:00:00', 'archive-{row_id}')"
            for row_id in range(1, 81)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.source_db}.{self.decoy_table} "
                f"(id, tenant_id, amount, updated_at, note) VALUES {archive_values}"
            ),
            "seed frozen-history archive rows",
        )

    def _setup_downstream(self, env) -> None:
        require_sql_success(
            env.execute_sql(f"DROP DATABASE IF EXISTS {self.source_db}", target="downstream"),
            "clear frozen-history downstream schema",
        )
        require_sql_success(
            env.execute_sql(f"CREATE DATABASE {self.source_db}", target="downstream"),
            "create frozen-history downstream schema",
        )
        require_sql_success(
            env.execute_sql(
                f"SET GLOBAL time_zone = '+08:00'; "
                f"CREATE TABLE {self.source_db}.{self.source_table} ("
                "id BIGINT PRIMARY KEY, amount DECIMAL(12,2) NOT NULL, state VARCHAR(16) NOT NULL, "
                "updated_at DATETIME NOT NULL, note VARCHAR(255) NOT NULL)",
                target="downstream",
            ),
            "create frozen-history downstream business table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.source_db}.{self.decoy_table} ("
                "id BIGINT PRIMARY KEY, tenant_id BIGINT NOT NULL, amount DECIMAL(12,2) NOT NULL, "
                "updated_at DATETIME NOT NULL, note VARCHAR(255) NOT NULL)",
                target="downstream",
            ),
            "create frozen-history downstream archive table",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.source_db}.{self.source_table} "
                f"(id, amount, state, updated_at, note) VALUES {self._values(1, self.seeded_rows, 'seed')}",
                target="downstream",
            ),
            "seed frozen-history downstream business rows",
        )
        archive_values = ",".join(
            f"({row_id}, {row_id % 7}, {row_id * 3}.00, '2026-08-16 00:00:00', 'archive-{row_id}')"
            for row_id in range(1, 81)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.source_db}.{self.decoy_table} "
                f"(id, tenant_id, amount, updated_at, note) VALUES {archive_values}",
                target="downstream",
            ),
            "seed frozen-history downstream archive rows",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TRIGGER {self.source_db}.{self.business_trigger} "
                f"BEFORE INSERT ON {self.source_db}.{self.source_table} "
                "FOR EACH ROW BEGIN DO SLEEP(0.12); END",
                target="downstream",
            ),
            "create frozen-history business slow trigger",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TRIGGER {self.source_db}.{self.archive_trigger} "
                f"AFTER INSERT ON {self.source_db}.{self.decoy_table} "
                "FOR EACH ROW SET @mf_cf01_archive_audit_seen = 1",
                target="downstream",
            ),
            "create frozen-history protected archive trigger",
        )

    def _create_changefeed(self, env) -> None:
        self._run_ticdc_cli(
            env,
            [
                "create",
                "--server=http://127.0.0.1:8300",
                "--sink-uri=mysql://root@mysql-0:3306/",
                f"--changefeed-id={self.changefeed_id}",
                "--no-confirm",
            ],
        )
        self._wait_for_status(
            env,
            self.changefeed_id,
            lambda status: str(status.get("state", "")).casefold() == "normal" and not status.get("error"),
            "NORMAL before the target episode",
        )

    def _inject_timezone_ddl(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"SET SESSION time_zone = '+00:00'; "
                f"CREATE TABLE {self.source_db}.{self.ddl_table} ("
                "id BIGINT PRIMARY KEY, end_time TIMESTAMP NOT NULL DEFAULT '1970-01-01 00:00:01'); "
                "SET SESSION time_zone = '+08:00'"
            ),
            "execute frozen-history UTC timestamp DDL",
        )

    def _read_ddl_commit_ts(self, env, log: str | None = None) -> int:
        log = log if log is not None else env.get_deployment().read_logs("ticdc/ticdc-0", lines=10000)
        if "1067" not in log or "Invalid default" not in log:
            raise RuntimeError(
                f"TiCDC log lacks the frozen-history timezone DDL failure: changefeed_id={self.changefeed_id!r}, log_tail={log[-4000:]!r}"
            )
        matches = sorted(set(re.findall(r"(?:\\?\"CommitTs\\?\"\s*:\s*|commitTs=)(\d+)", log, re.IGNORECASE)))
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected one failed DDL CommitTs: changefeed_id={self.changefeed_id!r}, matches={matches!r}"
            )
        return int(matches[0])

    def _wait_for_ddl_failure(self, env) -> int:
        deadline = time.monotonic() + 120
        last_status = None
        while time.monotonic() < deadline:
            log = env.get_deployment().read_logs("ticdc/ticdc-0", lines=10000)
            if "1067" in log and "Invalid default" in log:
                commit_ts = self._read_ddl_commit_ts(env, log)
                last_status = env.replication_status(self.changefeed_id)
                checkpoint = int(last_status.get("checkpoint_tso", 0))
                resolved = int(last_status.get("resolved_ts", 0))
                if checkpoint == commit_ts and resolved >= checkpoint:
                    return commit_ts
            time.sleep(1)
        raise RuntimeError(
            f"TiCDC did not expose the failed DDL checkpoint: changefeed_id={self.changefeed_id!r}, last_status={last_status!r}"
        )

    def _inject_post_fault_rows(self, env) -> None:
        start = self.seeded_rows + 1
        end = self.seeded_rows + self.post_fault_rows
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.source_db}.{self.source_table} "
                f"(id, amount, state, updated_at, note) VALUES {self._values(start, end, 'after-ddl')}"
            ),
            "create frozen-history post-DDL source rows",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.source_db}.{self.source_table} "
                f"(id, amount, state, updated_at, note) VALUES "
                f"({LIVE_WRITER_ID}, 1.00, 'paid', '2026-08-16 00:00:00', 'live-writer-stable') "
                "ON DUPLICATE KEY UPDATE amount=VALUES(amount), state=VALUES(state), "
                "updated_at=VALUES(updated_at), note=VALUES(note)"
            ),
            "preserve frozen-history live-writer row",
        )

    def _inject_schema_rollout_noise(self, env) -> None:
        for table in self.schema_rollout_tables:
            require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {self.source_db}.{table} ("
                    "id BIGINT PRIMARY KEY, "
                    "end_time TIMESTAMP NOT NULL DEFAULT '1970-01-01 08:00:01')"
                ),
                f"create frozen-history post-failure schema rollout table: table={table!r}",
            )

    def _run_target_episode(self, env) -> None:
        try:
            if self._stop_event.wait(self.ddl_delay_seconds):
                return
            self._inject_timezone_ddl(env)
            self.ddl_commit_ts = self._wait_for_ddl_failure(env)
            self._evidence["fault_ddl_commit_ts"] = self.ddl_commit_ts
            self._inject_schema_rollout_noise(env)
            self._inject_post_fault_rows(env)
        except BaseException as exc:
            self._episode_error = exc

    def _join_episode(self, context: str) -> None:
        thread = self._episode_thread
        if thread is None:
            return
        thread.join(timeout=150)
        if thread.is_alive():
            self._stop_event.set()
            raise RuntimeError(f"{context} target episode thread did not stop: thread={thread.name!r}")
        if self._episode_error is not None:
            raise RuntimeError(f"{context} target episode failed: changefeed_id={self.changefeed_id!r}") from self._episode_error

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._setup_upstream(context.env)
        self._setup_downstream(context.env)
        self._create_changefeed(context.env)
        self._configured = True

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        if not self._configured:
            raise RuntimeError("Frozen-history timezone-ddl activate requires a completed install")
        self._wait_for_status(
            context.env,
            self.changefeed_id,
            lambda status: str(status.get("state", "")).casefold() == "normal",
            "NORMAL during activation",
        )

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        if not self._configured:
            raise RuntimeError("Frozen-history timezone-ddl observability requested before install")
        self._evidence = {
            "fault_ddl_commit_ts": None,
            "fault_changefeed_id": self.changefeed_id,
            "fault_business_trigger": self.business_trigger,
            "fault_archive_trigger": self.archive_trigger,
            "fault_seeded_rows": self.seeded_rows,
            "fault_post_fault_rows": self.post_fault_rows,
            "history_contract": {
                "duration_seconds": _FROZEN_HISTORY_HISTORY.duration_seconds,
                "target_age_seconds_range": _FROZEN_HISTORY_HISTORY.target_age_seconds_range,
                "record_sources": [source.value for source in _FROZEN_HISTORY_HISTORY.record_sources],
            },
        }
        self._stop_event.clear()
        self._episode_error = None
        self._episode_thread = threading.Thread(
            target=self._run_target_episode,
            args=(context.env,),
            name=f"mf-dr-cutover-target-episode-{context.run_id}",
        )
        self._episode_thread.start()
        return self._evidence

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_event.set()
        self._join_episode("Frozen-history timezone-ddl quiesce")

    def recover(self, context: FaultLifecycleContext) -> None:
        self._stop_event.set()
        self._join_episode("Frozen-history timezone-ddl recovery")
        env = context.env
        require_sql_success(
            env.execute_sql(f"DROP TRIGGER IF EXISTS {self.source_db}.{self.business_trigger}", target="downstream"),
            "remove frozen-history business slow trigger",
        )
        require_sql_success(
            env.execute_sql(f"DROP TRIGGER IF EXISTS {self.source_db}.{self.archive_trigger}", target="downstream"),
            "remove frozen-history archive trigger",
        )
        try:
            env.replication_status(self.changefeed_id)
        except HTTPError as exc:
            if exc.code != 404:
                raise
        else:
            self._run_ticdc_cli(
                env,
                [
                    "remove",
                    "--server=http://127.0.0.1:8300",
                    f"--changefeed-id={self.changefeed_id}",
                ],
            )
        require_sql_success(
            env.execute_sql(f"DROP DATABASE IF EXISTS {self.source_db}", target="downstream"),
            "drop frozen-history downstream schema",
        )
        require_sql_success(
            env.execute_sql(f"DROP DATABASE IF EXISTS {self.source_db}"),
            "drop frozen-history source schema",
        )


_CASE = TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryForHistoryInvestigationScenarioCase(
    case_id="timezone_ddl_backpressure_history_investigation",
    case_no=0,
    evaluator=TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryEvaluatorCase,
    title="容灾切换窗口内 TiCDC 时区 DDL 与下游 sink 背压的历史调查",
    alert=(
        "[CRITICAL] 容灾切换后的复制新鲜度在一段历史窗口内持续恶化；当前控制面可能仍显示 NORMAL，"
        "业务写入没有停止，归档报表和集群节点看起来也正常。请使用可用的历史指标和记录定位完整根因，"
        "恢复给定业务复制路径并保留切换窗口内已提交的数据。允许在目标业务范围内执行必要的 schema 修复、"
        "目标 changefeed 恢复和受限业务写入；不得修改全局时区、业务数据、归档对象或无关组件。"
    ),
    initial_state={
        "status": "historical_replication_degradation",
        "control_plane": "may_be_normal",
        "business_writes": "continue",
        "archive_neighbor": "healthy",
    },
    expected_target={
        "status": "recovered",
        "changefeed": "normal_and_caught_up",
        "business_rows": "source_equals_downstream",
        "scope": "business_trigger_only; archive_trigger_preserved",
    },
    background_workload=_BACKGROUND_WORKLOAD,
    frozen_history=_FROZEN_HISTORY_HISTORY,
    difficulty=DifficultyCalibration(
        diagnostic_depth=8,
        environmental_complexity=0.936733,
        reference_run_ids=("pending:tidb-frozen-history-timezone-ddl",),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=180,
        bootstrap_cache_enabled=False,
        replication=TiDBReplicationRuntime(
            ticdc_image=TICDC_V8_1_0,
            downstream_image=MYSQL_8_4,
            ticdc_cpu_limit=1.0,
            ticdc_memory_mb=1024,
            downstream_cpu_limit=0.5,
            downstream_memory_mb=1024,
        ),
    ),
    reference_report=_REFERENCE_REPORT,
    source_db=SOURCE_DB,
    source_table=SOURCE_TABLE,
    ddl_table=DDL_TABLE,
    decoy_table=DECOY_TABLE,
    schema_rollout_tables=SCHEMA_ROLLOUT_TABLES,
    changefeed_id=CHANGEFEED_ID,
    business_trigger=BUSINESS_TRIGGER,
    archive_trigger=ARCHIVE_TRIGGER,
    live_writer_id=LIVE_WRITER_ID,
    seeded_rows=SEEDED_ROWS,
    post_fault_rows=POST_FAULT_ROWS,
    ddl_delay_seconds=180.0,
)

_REDUCED_HISTORY_CASE = replace(
    _CASE,
    case_id="timezone_ddl_backpressure_reduced_history_investigation",
    case_no=1,
    evaluator=TidbBusinessChangeTimezoneDdlBackpressureReducedHistoryEvaluatorCase,
    title="较短 DDL 延迟和较小写入批次下的 TiCDC 历史复合故障调查",
    seeded_rows=48,
    post_fault_rows=16,
    ddl_delay_seconds=90.0,
    background_workload=replace(_CASE.background_workload, worker_count=4),
    frozen_history=replace(_CASE.frozen_history, decoys=tuple(d for d in _CASE.frozen_history.decoys if d.decoy_id != "source-latency-catchup")),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.716667,
        reference_run_ids=('pending:tidb-frozen-history-timezone-ddl',),
        protocol_version='difficulty-v2',
    ),
)


class TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryScenario(TiDBScenario):
    scenario_id = SCENARIO_ID
    description = "Frozen-history historical investigation of a timezone-sensitive TiCDC DDL failure compounded by sink backpressure."
    cases = (_CASE, _REDUCED_HISTORY_CASE)

    def build_fault_plan(
        self,
        case: TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryForHistoryInvestigationScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryInjector,
                config={
                    "source_db": case.source_db,
                    "source_table": case.source_table,
                    "ddl_table": case.ddl_table,
                    "decoy_table": case.decoy_table,
                    "schema_rollout_tables": case.schema_rollout_tables,
                    "changefeed_id": case.changefeed_id,
                    "business_trigger": case.business_trigger,
                    "archive_trigger": case.archive_trigger,
                    "seeded_rows": case.seeded_rows,
                    "post_fault_rows": case.post_fault_rows,
                    "ddl_delay_seconds": case.ddl_delay_seconds,
                },
            ),
        )


__all__ = (
    "TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryForHistoryInvestigationScenarioCase",
    "TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryInjector",
    "TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryScenario",
)
