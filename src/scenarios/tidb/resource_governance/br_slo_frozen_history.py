from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import threading
import time
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path

import pymysql

from src.database.sql import parse_json_object
from src.scenarios.evaluation.tidb.resource_governance.br_slo_frozen_history import (
    TidbResourceGovernanceBrSloFrozenHistoryEvaluatorCase,
    TidbResourceGovernanceBrSloHistoryInvestigationEvaluatorCase,
)
from src.execution.history.records import (
    HistoricalRecordSource,
)
from src.scenarios.frozen_history import (
    DecoyDirection,
    DecoyKind,
    HistoryDecoySpec,
    FrozenHistorySpec,
)
from src.scenarios.tidb.common import (
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)
from src.scenarios.tidb.resource_governance.br_slo import (
    TidbResourceGovernanceBrSloInjector,
    _RG03_ARTIFACT_ROOT,
    _RG03_BR_IMAGE,
    _RG03_EXPECTED_INTEGRITY,
    _RG03_ROW_COUNT,
    _rg03_workload,
)
from src.workloads.specs import BackgroundWorkloadStartPhase, WorkloadProfile

from ...base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


_DATABASE = "benchops_mf_rg03"
_BUSINESS_TABLE = "orders"
_JOB_TABLE = "maintenance_jobs"
_CONTROLLER_TABLE = "br_pause_controller"
_BASELINE_CONFIG_TABLE = "config_baseline"
_ARTIFACT_ROOT = f"{_RG03_ARTIFACT_ROOT}-frozen-history"
_BR_JOB_PREFIX = "mf-br"
_BR_PAYLOAD_TABLE = "br_payload"
_TARGET_CAPTURE_SECONDS = 600
_MINIMUM_BR_RUN_SECONDS = 30
_SLO_BREACH_SAMPLES = 1
_BR_PAYLOAD_DIGITS = 125
_BR_PAYLOAD_ROWS_PER_DIGIT = 10_000
_BR_PAYLOAD_DIGITS_PER_BATCH = 1
_BR_PAYLOAD_BYTES_PER_ROW = 1_024
_BR_PAYLOAD_DIGESTS_PER_ROW = _BR_PAYLOAD_BYTES_PER_ROW // 16
_BR_PAYLOAD_SEED_WORKERS = 8


def _frozen_history_workload():
    base = _rg03_workload()
    base_profiles = tuple(
        replace(
            profile,
            sql=profile.sql.replace("benchops.", f"{_DATABASE}.").replace(
                "FROM benchops ", f"FROM {_DATABASE} "
            ),
        )
        for profile in base.profiles
    )
    profiles = (
        WorkloadProfile(
            name="checkout_quote_range",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(CRC32(SHA2(payload, 512))), 0) "
                f"FROM {_DATABASE}.{_BUSINESS_TABLE} "
                "WHERE order_id BETWEEN MOD(CAST(UNIX_TIMESTAMP(NOW()) AS UNSIGNED), 95904) + 1 "
                "AND MOD(CAST(UNIX_TIMESTAMP(NOW()) AS UNSIGNED), 95904) + 4096"
            ),
            qps=60.0,
            tier="OLTP_CORE",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="checkout_recent_payload",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(CHAR_LENGTH(payload)), 0) "
                f"FROM {_DATABASE}.{_BUSINESS_TABLE} "
                "WHERE order_id BETWEEN 96001 AND 97024 AND status IN ('PAID', 'SHIPPED')"
            ),
            qps=1.1,
            tier="OLTP_CORE",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="br_controller_observer",
            sql=(
                f"SELECT job_id, requested_action, controller_state, resume_count, last_event "
                f"FROM {_DATABASE}.{_CONTROLLER_TABLE} ORDER BY last_event_at DESC, job_id LIMIT 8"
            ),
            qps=0.12,
            tier="OBSERVABILITY",
            application_name="backup-controller",
        ),
        WorkloadProfile(
            name="br_progress_observer",
            sql=(
                f"SELECT job_id, state, total_ranges, ranges_succeeded, ranges_failed, checksum_status, storage_path "
                f"FROM {_DATABASE}.{_JOB_TABLE} ORDER BY started_at DESC, job_id DESC LIMIT 12"
            ),
            qps=0.12,
            tier="OBSERVABILITY",
            application_name="backup-progress",
        ),
    )
    profiles += base_profiles
    return replace(
        base,
        profiles=profiles,
        seed=0xAF03,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        warmup_seconds=30,
    )


_REFERENCE_DIAGNOSIS = {
    "conditions": [
        {
            "type": "temporal_cause",
            "factor": "BR progress rises before TiKV shared I/O and CPU saturation, then historical checkout p99 crosses 35 ms; the live controller guard uses checkout p95 > 35 ms",
            "entity": "target historical window",
            "evidence": [
                "query_metrics history shows BR progress/job activity before the TiKV resource rise",
                "historical checkout p99 crosses the SLO after the shared resource rise, while the live controller records a p95 breach before pausing",
            ],
        },
        {
            "type": "target_identity",
            "factor": "the paused run-scoped BR job and storage path are the target historical episode",
            "entity": "the current PAUSED_FOR_REVIEW job",
            "evidence": [
                "the current job, controller state, range progress, and storage path agree",
                "historical catalog and recovery candidates do not own the current artifact",
            ],
        },
        {
            "type": "root_cause",
            "factor": "BR maintenance and foreground checkout share TiKV disk, network, and CPU resources",
            "entity": "tikv/tikv-0, tikv/tikv-1, tikv/tikv-2",
            "evidence": [
                "all three TiKV resource series rise while checkout demand does not rise first",
                "the same window contains BR progress and foreground latency degradation",
            ],
        },
        {
            "type": "root_cause",
            "factor": "backup auto-tune is disabled and the maintenance budget is too strong for the foreground SLO",
            "entity": "TiKV backup configuration and the target BR job",
            "evidence": [
                "SHOW CONFIG exposes backup.enable-auto-tune=false at the target episode",
                "the initial eight-thread maintenance budget with auto-tune disabled is not sustainable under checkout traffic",
            ],
        },
        {
            "type": "exclusion",
            "factor": "OLAP burst, compaction, off-peak small backup, and checkout QPS flash are excluded by timing or healthy SLO",
            "entity": "historical decoy windows",
            "evidence": [
                "OLAP and compaction windows have no matching target BR progress",
                "the off-peak small backup and checkout flash preserve the relevant SLO or have a different causal order",
            ],
        },
    ]
}


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceBrSloFrozenHistoryCase(TiDBScenarioCase):
    database: str
    business_table: str
    job_table: str
    controller_table: str
    baseline_config_table: str
    job_id_prefix: str
    row_count: int
    expected_business_integrity: tuple[int, int, int]
    business_query: str
    slo_p95_ms: float
    max_backup_bytes: int
    artifact_root: str
    br_image: str
    initial_br_concurrency: int
    initial_tikv_backup_threads: int
    target_capture_seconds: int
    minimum_br_run_seconds: int
    reference_path: tuple[str, ...]


class TidbResourceGovernanceBrSloFrozenHistoryInjector(TidbResourceGovernanceBrSloInjector):

    retain_workload_after_metric_history = True
    """Run and audit one real BR process that is paused and resumed in place."""

    def __init__(self):
        super().__init__()
        self.controller_table = None
        self.target_capture_seconds = None
        self.slo_p95_ms = None
        self.minimum_br_run_seconds = None
        self._container_name = None
        self._controller_stop = None
        self._controller_thread = None
        self._controller_error = None
        self._container_paused = False
        self._pause_not_before = None
        self._slo_breach_samples = 0
        self._br_progress_percent = 0.0
        self._history_prepared = False

    def prepare_metric_history(self, context: FaultLifecycleContext) -> None:
        stage_clock = time.monotonic()

        def _timing(stage: str) -> None:
            print(f">>> [RG03-mf timing] prepare.{stage}: {time.monotonic() - stage_clock:.3f}s")

        self._configure(context.config, context.run_id)
        self._create_schema(context.env)
        _timing("create_schema_and_seed")
        self._capture_baseline_config(context.env)
        _timing("capture_baseline_config")
        self._history_prepared = True

    def install(self, context: FaultLifecycleContext) -> None:
        if not self._history_prepared:
            raise RuntimeError(
                "Frozen-history BR install requires prepare_metric_history to complete first: "
                f"run_id={context.run_id!r}"
            )
        stage_clock = time.monotonic()

        def _timing(stage: str) -> None:
            print(f">>> [RG03-mf timing] install.{stage}: {time.monotonic() - stage_clock:.3f}s")

        self._verify_business_integrity(context.env)
        _timing("verify_business_integrity")
        self._prepare_artifact_directory()
        self._insert_job(context.env, "STARTING")
        self._set_backup_config(context.env, auto_tune="false", threads=self.initial_tikv_backup_threads)
        _timing("job_and_config")
        self._start_br(context)
        _timing("start_br")

    def activate(self, context: FaultLifecycleContext) -> None:
        stage_clock = time.monotonic()

        def _timing(stage: str) -> None:
            print(f">>> [RG03-mf timing] activate.{stage}: {time.monotonic() - stage_clock:.3f}s")

        self._configure(context.config, context.run_id)
        self._load_baseline_config(context.env)
        self._verify_business_integrity(context.env)
        _timing("verify_business_integrity")
        self._prepare_artifact_directory()
        self._insert_job(context.env, "STARTING")
        self._set_backup_config(context.env, auto_tune="false", threads=self.initial_tikv_backup_threads)
        _timing("job_and_config")
        self._start_br(context)
        _timing("start_br")

    def _configure(self, config: Mapping[str, object], run_id: str) -> None:
        config = dict(config)
        prefix = str(config["job_id_prefix"])
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", prefix) is None:
            raise ValueError(f"Invalid run-scoped BR job ID prefix: prefix={prefix!r}")
        config["job_id"] = f"{prefix}-{hashlib.sha256(run_id.encode()).hexdigest()[:20]}"
        super()._configure(config, run_id)
        self.controller_table = validate_sql_identifier(str(config["controller_table"]), "controller_table")
        self.target_capture_seconds = int(config["target_capture_seconds"])
        self.slo_p95_ms = float(config["slo_p95_ms"])
        self.minimum_br_run_seconds = int(config["minimum_br_run_seconds"])
        if (
            self.target_capture_seconds <= self.minimum_br_run_seconds
            or self.minimum_br_run_seconds <= 0
            or self.slo_p95_ms <= 0
        ):
            raise ValueError(
                "Frozen-history BR controller minimum run must be positive and shorter than the target capture: "
                f"target_capture_seconds={self.target_capture_seconds}, minimum_br_run_seconds={self.minimum_br_run_seconds}, "
                f"slo_p95_ms={self.slo_p95_ms}"
            )

    def _create_schema(self, env) -> None:
        super()._create_schema(env)
        require_sql_success(
            env.execute_sql(
                f"ALTER TABLE {self.database}.{self.job_table} "
                "ADD COLUMN progress_percent DECIMAL(6,2) NOT NULL DEFAULT 0"
            ),
            "frozen-history add BR progress column",
        )
        # Keep the real BR process alive through the target window without changing business truth.
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.database}.{_BR_PAYLOAD_TABLE}"),
            "frozen-history clear BR payload table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{_BR_PAYLOAD_TABLE} ("
                f"payload_id BIGINT PRIMARY KEY, payload VARBINARY({_BR_PAYLOAD_BYTES_PER_ROW}) NOT NULL"
                ") ENGINE=InnoDB"
            ),
            "frozen-history create BR payload table",
        )
        def _load_digit_batch(digit_start: int) -> None:
            digits = " UNION ALL ".join(
                f"SELECT {digit} AS digit"
                for digit in range(digit_start, digit_start + _BR_PAYLOAD_DIGITS_PER_BATCH)
            )
            digest_expression = "CONCAT(" + ", ".join(
                f"MD5(CONCAT(n, '-{part}'))"
                for part in range(_BR_PAYLOAD_DIGESTS_PER_ROW)
            ) + ")"
            payload_expression = f"UNHEX({digest_expression})"
            require_sql_success(
                env.execute_internal_sql(
                    f"INSERT INTO {self.database}.{_BR_PAYLOAD_TABLE} (payload_id, payload) "
                    f"SELECT n + 100000 * digit, {payload_expression} "
                    f"FROM {self.database}.numbers "
                    f"CROSS JOIN ({digits}) AS digits "
                    f"WHERE n BETWEEN 1 AND {_BR_PAYLOAD_ROWS_PER_DIGIT}"
                ),
                f"frozen-history load BR payload digit batch {digit_start}.."
                f"{digit_start + _BR_PAYLOAD_DIGITS_PER_BATCH - 1}",
            )

        batch_starts = list(range(0, _BR_PAYLOAD_DIGITS, _BR_PAYLOAD_DIGITS_PER_BATCH))
        with ThreadPoolExecutor(max_workers=min(_BR_PAYLOAD_SEED_WORKERS, len(batch_starts))) as pool:
            for _ in pool.map(_load_digit_batch, batch_starts):
                pass
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.database}.{self.controller_table} ("
                "job_id VARCHAR(64) PRIMARY KEY, "
                "requested_action VARCHAR(16) NOT NULL, "
                "controller_state VARCHAR(24) NOT NULL, "
                "resume_count INT NOT NULL, "
                "last_event VARCHAR(16) NOT NULL, "
                "storage_path VARCHAR(255) NOT NULL, "
                "last_event_at DATETIME(6) NULL, "
                "last_error VARCHAR(1000) NOT NULL, "
                "CONSTRAINT chk_mf_rg03_requested_action CHECK "
                "(requested_action IN ('AUTO_PAUSE', 'RESUME', 'NONE')), "
                "CONSTRAINT chk_mf_rg03_controller_state CHECK "
                "(controller_state IN ('RUNNING', 'PAUSED_FOR_REVIEW', 'SUCCEEDED'))"
                ") ENGINE=InnoDB"
            ),
            "frozen-history create BR pause controller",
        )

    def _insert_job(self, env, state: str) -> None:
        super()._insert_job(env, state)
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.database}.{self.controller_table} "
                "(job_id, requested_action, controller_state, resume_count, last_event, storage_path, last_event_at, last_error) "
                f"VALUES ('{self.job_id}', 'AUTO_PAUSE', 'RUNNING', 0, 'START', '{self._storage_uri}', NOW(6), '')"
            ),
            "frozen-history insert BR pause controller",
        )

    def _reset_job(self, env) -> None:
        super()._reset_job(env)
        require_sql_success(
            env.execute_sql(
                f"UPDATE {self.database}.{self.job_table} SET progress_percent=0 "
                f"WHERE job_id='{self.job_id}'"
            ),
            "frozen-history reset BR progress",
        )
        require_sql_success(
            env.execute_sql(
                f"UPDATE {self.database}.{self.controller_table} SET requested_action='AUTO_PAUSE', "
                "controller_state='RUNNING', resume_count=0, last_event='START', "
                f"storage_path='{self._storage_uri}', last_event_at=NOW(6), last_error='' WHERE job_id='{self.job_id}'"
            ),
            "frozen-history reset BR pause controller",
        )

    def _start_br(self, context: FaultLifecycleContext) -> None:
        if self._br_process is not None and self._br_process.poll() is None:
            raise RuntimeError(f"Frozen-history BR process is already running: run_id={context.run_id!r}")
        deployment = context.env.deployment
        network = f"{deployment.project_name}_default"
        self._container_name = f"{deployment.project_name}-mf-br"
        self._br_log_handle = self._br_log_path.open("w", encoding="utf-8")
        self._br_progress_percent = 0.0
        br_detail_log_path = f"/backup/{self.artifact_root.name}/br.detail.log"
        command = [
            "docker", "run", "--rm", "--name", self._container_name,
            "--network", network,
            "--user", f"{os.getuid()}:{os.getgid()}",
            "-v", f"{self.artifact_root.parent}:/backup",
            "--entrypoint", "/br", self.br_image,
            "--log-file", br_detail_log_path,
            "backup", "db",
            "--pd", "http://pd-0:2379",
            "--db", self.database,
            "--storage", self._storage_uri,
            "--concurrency", str(self.initial_br_concurrency),
            "--checksum",
        ]
        require_sql_success(
            context.env.execute_sql(
                f"UPDATE {self.database}.{self.job_table} SET state='RUNNING', started_at=NOW(6) "
                f"WHERE job_id='{self.job_id}'"
            ),
            "frozen-history mark BR job running",
        )
        self._br_process = subprocess.Popen(
            command,
            stdout=self._br_log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self._br_stop = threading.Event()
        self._monitor_error = None
        self._br_thread = threading.Thread(
            target=self._monitor_br,
            args=(context.env,),
            name=f"frozen-history-br-monitor-{context.run_id}",
            daemon=True,
        )
        self._br_thread.start()
    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        evidence = dict(super().prepare_observability(context))
        self._start_controller(context.env)
        evidence.update({
            "target_job": {
                "job_id": self.job_id,
                "storage_uri": self._storage_uri,
                "controller_table": f"{self.database}.{self.controller_table}",
            },
            "controller_table": f"{self.database}.{self.controller_table}",
            "br_detail_log_path": str(self._br_log_path.with_name("br.detail.log")),
            "pause_semantics": "docker pause/unpause on the same BR process with an audited controller row",
        })
        return evidence

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_controller()
        self._unpause_container(context.env)
        super().quiesce(context)

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Retain the paused BR and controller so Agent review can request resume."""
        if self._container_name is None or self._br_process is None:
            raise RuntimeError(
                "Frozen-history history settle requires the original BR container and process: "
                f"run_id={context.run_id!r}, job_id={self.job_id!r}, "
                f"container={self._container_name!r}, process_present={self._br_process is not None}"
            )
        if not self._container_paused or self._br_process.poll() is not None:
            raise RuntimeError(
                "Frozen-history history settle requires the original BR process to remain paused and alive: "
                f"run_id={context.run_id!r}, job_id={self.job_id!r}, "
                f"container={self._container_name!r}, paused_flag={self._container_paused!r}, "
                f"process_returncode={self._br_process.poll()!r}"
            )
        inspect_result = subprocess.run(
            ["docker", "inspect", "--format", "{{json .State}}", self._container_name],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if inspect_result.returncode != 0:
            raise RuntimeError(
                "Frozen-history history settle could not inspect the original BR container: "
                f"run_id={context.run_id!r}, job_id={self.job_id!r}, container={self._container_name!r}, "
                f"stdout={inspect_result.stdout.strip()!r}, stderr={inspect_result.stderr.strip()!r}"
            )
        try:
            container_state = json.loads(inspect_result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Frozen-history history settle received invalid BR container state: "
                f"run_id={context.run_id!r}, job_id={self.job_id!r}, container={self._container_name!r}, "
                f"stdout={inspect_result.stdout.strip()!r}"
            ) from exc
        if (
            container_state.get("Status") != "paused"
            or container_state.get("Running") is not True
            or container_state.get("Paused") is not True
        ):
            raise RuntimeError(
                "Frozen-history history settle found the BR container is not still paused and alive: "
                f"run_id={context.run_id!r}, job_id={self.job_id!r}, container={self._container_name!r}, "
                f"state={container_state!r}"
            )
        job = self._job(context.env)
        if job["job_id"] != self.job_id or job["state"] != "PAUSED_FOR_REVIEW":
            raise RuntimeError(
                "Frozen-history history settle found an invalid current target job: "
                f"run_id={context.run_id!r}, expected_job_id={self.job_id!r}, job={job!r}"
            )

    def recover(self, context: FaultLifecycleContext) -> None:
        self._stop_controller()
        self._unpause_container(context.env)
        super().recover(context)

    def _job(self, env) -> dict[str, object]:
        # The controller and monitor threads poll from the background; a fresh
        # connection per read keeps them off the shared primary connection that
        # the main thread uses concurrently during evaluation and teardown.
        payload = json_object(
            env.execute_internal_sql(
                f"SELECT job_id, state, total_ranges, ranges_succeeded, ranges_failed, checksum_status, storage_path, last_error "
                f"FROM {self.database}.{self.job_table} WHERE job_id='{self.job_id}'"
            ),
            "RG03 read BR job record",
        )
        rows = payload["result"]
        if len(rows) != 1:
            raise RuntimeError(f"RG03 BR job record must contain one row: rows={rows!r}")
        row = rows[0]
        return {
            "job_id": str(row[0]),
            "state": str(row[1]).upper(),
            "total_ranges": int(row[2]),
            "ranges_succeeded": int(row[3]),
            "ranges_failed": int(row[4]),
            "checksum_status": str(row[5]),
            "storage_path": str(row[6]),
            "last_error": str(row[7] or ""),
        }

    def _monitor_br(self, env) -> None:
        try:
            while self._br_process.poll() is None:
                self._refresh_br_progress(env)
                if self._br_stop.is_set():
                    return
                self._br_stop.wait(1.0)
            self._refresh_br_progress(env)
            if self._br_stop.is_set():
                return
            returncode = self._br_process.returncode
            log_text = self._br_log_path.read_text(encoding="utf-8", errors="replace")
            if returncode != 0:
                self._update_job(
                    env,
                    state="FAILED",
                    total_ranges=0,
                    ranges_succeeded=0,
                    ranges_failed=1,
                    checksum_status="FAILED",
                    last_error=log_text[-1800:],
                )
                return
            summary = self._parse_br_summary(log_text)
            self._br_progress_percent = 100.0
            self._update_job(env, state="SUCCEEDED", **summary, last_error="")
            self._update_controller(
                env,
                controller_state="SUCCEEDED",
                requested_action="NONE",
                last_error="",
                keep_last_event=True,
            )
        except Exception as exc:
            self._monitor_error = exc

    def _refresh_br_progress(self, env) -> None:
        log_text = self._br_log_path.read_text(encoding="utf-8", errors="replace")
        progress = self._parse_br_progress_percent(log_text)
        if progress is None:
            return
        if progress <= self._br_progress_percent:
            return
        self._br_progress_percent = progress
        connection = pymysql.connect(
            host=env.host,
            port=env.port,
            user=env.user,
            password=env.password,
            database=env.dbname,
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=5,
            read_timeout=10,
            write_timeout=10,
        )
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {self.database}.{self.job_table} SET progress_percent=%s "
                "WHERE job_id=%s AND state='RUNNING'",
                (progress, self.job_id),
            )
        connection.close()

    @staticmethod
    def _parse_br_progress_percent(log_text: str) -> float | None:
        values = re.findall(r"Database Backup <[^>]*>\s*(\d+(?:\.\d+)?)%", log_text)
        if not values:
            return None
        progress = max(float(value) for value in values)
        if not 0.0 <= progress <= 100.0:
            raise RuntimeError(f"Frozen-history BR progress is outside 0..100 percent: progress={progress!r}")
        return progress

    def _start_controller(self, env) -> None:
        if self._controller_thread is not None:
            raise RuntimeError(f"Frozen-history BR controller is already running: job_id={self.job_id!r}")
        self._controller_stop = threading.Event()
        self._controller_error = None
        self._pause_not_before = time.monotonic() + self.minimum_br_run_seconds
        self._slo_breach_samples = 0
        self._controller_thread = threading.Thread(
            target=self._controller_loop,
            args=(env,),
            name=f"frozen-history-br-controller-{self.job_id}",
            daemon=True,
        )
        self._controller_thread.start()

    def _stop_controller(self) -> None:
        if self._controller_stop is not None:
            self._controller_stop.set()
        if self._controller_thread is not None:
            self._controller_thread.join(timeout=10)
            if self._controller_thread.is_alive():
                raise RuntimeError(f"Frozen-history BR controller did not stop: job_id={self.job_id!r}")
        self._controller_thread = None
        self._controller_stop = None
        if self._controller_error is not None:
            error = self._controller_error
            self._controller_error = None
            raise RuntimeError(f"Frozen-history BR controller failed: job_id={self.job_id!r}, error={error!r}") from error

    def _controller_loop(self, env) -> None:
        try:
            while not self._controller_stop.is_set():
                controller = self._controller(env)
                if controller["controller_state"] == "SUCCEEDED":
                    return
                if not self._container_paused and controller["controller_state"] == "RUNNING":
                    job = self._job(env)
                    p95_ms = self._current_checkout_p95(env)
                    if p95_ms > self.slo_p95_ms:
                        self._slo_breach_samples += 1
                    else:
                        self._slo_breach_samples = 0
                    if (
                        self._pause_not_before is not None
                        and time.monotonic() >= self._pause_not_before
                        and job["state"] == "RUNNING"
                        and self._br_progress_percent > 0.0
                        and self._slo_breach_samples >= _SLO_BREACH_SAMPLES
                    ):
                        self._pause_container(env, guard_p95_ms=p95_ms)
                elif self._container_paused and controller["requested_action"] == "RESUME":
                    self._resume_container(env)
                self._controller_stop.wait(1.0)
        except Exception as exc:
            if self._controller_stop is not None and self._controller_stop.is_set():
                return
            self._controller_error = exc

    def _current_checkout_p95(self, env) -> float:
        payload = parse_json_object(
            env.observe_metric("query_latency"),
            "frozen-history BR controller checkout latency",
        )
        if payload.get("status") != "success":
            raise RuntimeError(
                "Frozen-history BR controller checkout latency returned an error: "
                f"payload={payload!r}"
            )
        series = payload.get("series")
        if not isinstance(series, dict) or not series:
            raise RuntimeError(
                "Frozen-history BR controller checkout latency has no series: "
                f"payload={payload!r}"
            )
        latest = []
        for target, values in series.items():
            if not isinstance(values, dict) or not values.get("p95_ms"):
                raise RuntimeError(
                    "Frozen-history BR controller checkout latency has no p95 samples: "
                    f"target={target!r}, values={values!r}"
                )
            latest.append(float(values["p95_ms"][-1]))
        return max(latest)

    def _controller(self, env) -> dict[str, object]:
        connection = pymysql.connect(
            host=env.host,
            port=env.port,
            user=env.user,
            password=env.password,
            database=env.dbname,
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=5,
            read_timeout=10,
            write_timeout=10,
        )
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT requested_action, controller_state, resume_count FROM {self.database}.{self.controller_table} "
                "WHERE job_id=%s",
                (self.job_id,),
            )
            rows = cursor.fetchall()
        connection.close()
        if len(rows) != 1:
            raise RuntimeError(
                "Frozen-history BR controller target row is not unique: "
                f"job_id={self.job_id!r}, rows={rows!r}"
            )
        return {
            "requested_action": str(rows[0][0]).upper(),
            "controller_state": str(rows[0][1]).upper(),
            "resume_count": int(rows[0][2]),
        }

    def _pause_container(self, env, *, guard_p95_ms: float) -> None:
        if self._container_name is None or self._br_process is None or self._br_process.poll() is not None:
            raise RuntimeError(
                "Frozen-history BR cannot pause a missing or exited process: "
                f"job_id={self.job_id!r}, container={self._container_name!r}"
            )
        print(
            ">>> [RG03-mf timing] pause: "
            f"progress_percent={self._br_progress_percent!r}, guard_p95_ms={guard_p95_ms!r}"
        )
        completed = subprocess.run(
            ["docker", "pause", self._container_name],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if completed.returncode != 0:
            if (
                "is not running" in completed.stderr
                and self._br_process.poll() is not None
                and self._br_thread is not None
            ):
                self._br_thread.join(timeout=2)
                job = self._job(env)
                if job["state"] == "SUCCEEDED":
                    return
            raise RuntimeError(
                "Frozen-history BR pause failed: "
                f"job_id={self.job_id!r}, container={self._container_name!r}, "
                f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
            )
        self._container_paused = True
        self._pause_not_before = None
        self._update_controller(
            env,
            controller_state="PAUSED_FOR_REVIEW",
            requested_action="NONE",
            last_event="AUTO_PAUSE",
            last_error="",
        )
        require_sql_success(
            env.execute_internal_sql(
                f"UPDATE {self.database}.{self.job_table} SET state='PAUSED_FOR_REVIEW', finished_at=NULL "
                f"WHERE job_id='{self.job_id}'"
            ),
            "frozen-history mark BR job paused",
        )

    def _resume_container(self, env) -> None:
        if self._container_name is None or not self._container_paused:
            raise RuntimeError(
                "Frozen-history BR resume requires the same paused container: "
                f"job_id={self.job_id!r}, container={self._container_name!r}, paused={self._container_paused!r}"
            )
        if not self._backup_budget_is_resumable(env):
            self._update_controller(
                env,
                controller_state="PAUSED_FOR_REVIEW",
                requested_action="NONE",
                last_event="RESUME_BLOCKED",
                last_error="resume request rejected: current maintenance state is not eligible for resume",
            )
            return
        completed = subprocess.run(
            ["docker", "unpause", self._container_name],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "Frozen-history BR resume failed: "
                f"job_id={self.job_id!r}, container={self._container_name!r}, "
                f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
            )
        self._container_paused = False
        self._update_controller(
            env,
            controller_state="RUNNING",
            requested_action="NONE",
            last_event="RESUME",
            last_error="",
            increment_resume=True,
        )
        require_sql_success(
            env.execute_internal_sql(
                f"UPDATE {self.database}.{self.job_table} SET state='RUNNING', finished_at=NULL "
                f"WHERE job_id='{self.job_id}'"
            ),
            "frozen-history mark BR job resumed",
        )

    def _backup_budget_is_resumable(self, env) -> bool:
        rows = self._config_rows(env)
        settings = {
            "backup.enable-auto-tune": {},
            "backup.num-threads": {},
        }
        for row in rows:
            name = str(row[2])
            if name not in settings:
                continue
            instance = str(row[1]).split(":", 1)[0]
            if instance in settings[name]:
                raise RuntimeError(
                    "Frozen-history BR resume saw duplicate TiKV backup configuration: "
                    f"setting={name!r}, instance={instance!r}, rows={rows!r}"
                )
            settings[name][instance] = str(row[3])
        instances = set(settings["backup.enable-auto-tune"])
        expected_instances = {"tikv-0", "tikv-1", "tikv-2"}
        if instances != expected_instances or instances != set(settings["backup.num-threads"]):
            raise RuntimeError(
                "Frozen-history BR resume saw inconsistent TiKV backup configuration coverage: "
                f"expected_instances={sorted(expected_instances)!r}, "
                f"auto_tune_instances={sorted(instances)!r}, "
                f"thread_instances={sorted(settings['backup.num-threads'])!r}, rows={rows!r}"
            )
        return all(
            settings["backup.enable-auto-tune"][instance].casefold() == "true"
            and float(settings["backup.num-threads"][instance]) in {1.0, 2.0}
            for instance in sorted(instances)
        )

    def _unpause_container(self, env) -> None:
        if not self._container_paused:
            return
        if self._container_name is None:
            raise RuntimeError(f"Frozen-history BR has paused state without a container: job_id={self.job_id!r}")
        completed = subprocess.run(
            ["docker", "unpause", self._container_name],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "Frozen-history BR teardown unpause failed: "
                f"job_id={self.job_id!r}, container={self._container_name!r}, "
                f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
            )
        self._container_paused = False

    def _update_controller(
        self,
        env,
        *,
        controller_state: str,
        requested_action: str,
        last_error: str,
        last_event: str | None = None,
        increment_resume: bool = False,
        keep_last_event: bool = False,
    ) -> None:
        if keep_last_event and last_event is not None:
            raise ValueError("Frozen-history controller update cannot keep and replace last_event")
        connection = pymysql.connect(
            host=env.host,
            port=env.port,
            user=env.user,
            password=env.password,
            database=env.dbname,
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=5,
            read_timeout=10,
            write_timeout=10,
        )
        with connection.cursor() as cursor:
            if keep_last_event:
                cursor.execute(
                    f"UPDATE {self.database}.{self.controller_table} SET requested_action=%s, controller_state=%s, "
                    "last_event_at=NOW(6), last_error=%s WHERE job_id=%s",
                    (requested_action, controller_state, last_error, self.job_id),
                )
            else:
                cursor.execute(
                    f"UPDATE {self.database}.{self.controller_table} SET requested_action=%s, controller_state=%s, "
                    "resume_count=resume_count + %s, last_event=%s, last_event_at=NOW(6), last_error=%s WHERE job_id=%s",
                    (
                        requested_action,
                        controller_state,
                        1 if increment_resume else 0,
                        last_event,
                        last_error,
                        self.job_id,
                    ),
                )
        connection.close()


_CASE = TidbResourceGovernanceBrSloFrozenHistoryCase(
    case_id="br_slo_history_calibration",
    case_no=0,
    evaluator=TidbResourceGovernanceBrSloFrozenHistoryEvaluatorCase,
    title="Reconstruct a paused BR SLO incident from a frozen 12-hour TiDB history and continue it safely.",
    alert=(
        "P1 data-protection SLO review: a run-scoped BR job was automatically paused for review after the "
        "checkout latency guard was crossed. The foreground is currently healthy and the maintenance pressure "
        "is no longer live. Reconstruct the 12-hour history, identify the target job and the resource cause, "
        "then use the authorized bounded TiKV backup budget and the same-job pause/resume controller to finish "
        "the existing artifact. Do not change business data, write historical observations, start a replacement "
        "job, disable space protection, or restart the cluster. The published contracts are checkout p95 <= 35 ms, "
        "artifact <= 8 GiB, all ranges with checksum 100%, unchanged orders truth, and auto-tune enabled with "
        "1..2 backup threads per TiKV."
    ),
    initial_state={
        "status": "br_paused_for_review",
        "foreground_slo": "recovered_after_guard_pause",
        "history": "12h_frozen_frozen_history",
        "target_job": "run_scoped_and_currently_paused",
    },
    expected_target={
        "status": "br_succeeded_on_same_job",
        "foreground_slo": "checkout_p95<=35ms",
        "artifact": "non_empty_backupmeta_and_checksum_100_percent",
        "configuration": "auto_tune=true_threads=1..2_on_every_tikv",
        "business_integrity": "orders_unchanged",
    },
    background_workload=_frozen_history_workload(),
    frozen_history=FrozenHistorySpec(
        schema_version=1,
        duration_seconds=12 * 60 * 60,
        normal_capture_seconds=300,
        fault_capture_seconds=_TARGET_CAPTURE_SECONDS,
        base_step_seconds=60,
        overview_step_seconds=60,
        block_min_seconds=60,
        block_max_seconds=300,
        transition_seconds=60,
        target_age_seconds_range=(1200, 1800),
        required_metrics=(
            "query_latency",
            "qps",
            "cpu",
            "disk_io",
            "disk_usage",
            "network_io",
            "active_connections",
        ),
        record_sources=(
            HistoricalRecordSource.COMPONENT_LOG,
            HistoricalRecordSource.TOPSQL,
            HistoricalRecordSource.SLOW_QUERIES,
        ),
        decoys=(
            HistoryDecoySpec(
                decoy_id="olap-query-burst",
                kind=DecoyKind.METRIC_ONLY,
                metric="query_latency",
                field="p99_ms",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=120,
                amplitude_mad=1.0,
            ),
            HistoryDecoySpec(
                decoy_id="tikv-compaction",
                kind=DecoyKind.METRIC_ONLY,
                metric="cpu",
                field="percent",
                target="tikv/tikv-0",
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=120,
                amplitude_mad=1.0,
            ),
            HistoryDecoySpec(
                decoy_id="small-backup-offpeak",
                kind=DecoyKind.METRIC_ONLY,
                metric="cpu",
                field="percent",
                target="tikv/tikv-1",
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=120,
                amplitude_mad=1.0,
            ),
            HistoryDecoySpec(
                decoy_id="checkout-flash-peak",
                kind=DecoyKind.METRIC_ONLY,
                metric="qps",
                field="queries_per_second",
                target=None,
                direction=DecoyDirection.SPIKE,
                count=1,
                duration_seconds=120,
                amplitude_mad=1.0,
            ),
        ),
        max_points_per_series=6000,
        max_scalar_samples_per_response=30000,
        max_history_records_per_response=400,
        metric_targets={
            "query_latency": (None,),
            "qps": (None,),
            "cpu": ("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
            "disk_io": ("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
            "disk_usage": (None,),
            "network_io": ("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
            "active_connections": (None,),
        },
        metric_rate_windows={
            "query_latency": 30,
            "qps": 30,
            "cpu": 30,
            "disk_io": 30,
            "network_io": 30,
        },
    ),
    reference_report={
        "diagnosis": _REFERENCE_DIAGNOSIS,
        "outcome": {
            "changes": [
                "enabled the bounded TiKV backup budget and resumed the existing BR job through its controller",
            ],
            "verification": [
                "the same run-scoped job completed all ranges with checksum 100%",
                "the original artifact and checkout SLO are healthy",
                "the orders business truth is unchanged",
            ],
        },
        "summary": "The historical BR resource incident was identified and the existing job was safely continued without changing business data.",
    },
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=1,
        sql_timeout_seconds=600,
        tikv_shared_volume_root=_ARTIFACT_ROOT,
        tikv_memory_mb=4_096,
        tidb_memory_mb=2_048,
        bootstrap_cache_enabled=False,
    ),
    database=_DATABASE,
    business_table=_BUSINESS_TABLE,
    job_table=_JOB_TABLE,
    controller_table=_CONTROLLER_TABLE,
    baseline_config_table=_BASELINE_CONFIG_TABLE,
    job_id_prefix=_BR_JOB_PREFIX,
    row_count=_RG03_ROW_COUNT,
    expected_business_integrity=_RG03_EXPECTED_INTEGRITY,
    business_query=(
        f"SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
        f"COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, tenant_id, status, amount, payload))), 0) "
        f"FROM {_DATABASE}.{_BUSINESS_TABLE}"
    ),
    slo_p95_ms=35.0,
    max_backup_bytes=8 * 1024 * 1024 * 1024,
    artifact_root=_ARTIFACT_ROOT,
    br_image=_RG03_BR_IMAGE,
    initial_br_concurrency=4,
    initial_tikv_backup_threads=8,
    target_capture_seconds=_TARGET_CAPTURE_SECONDS,
    minimum_br_run_seconds=_MINIMUM_BR_RUN_SECONDS,
    reference_path=(
        "current checkout SLO is healthy only after an automatic pause, while the BR job is incomplete",
        "the historical window shows BR progress before TiKV I/O/CPU and checkout p99 degradation, with a live p95 guard breach",
        "the historical window maps to one run-scoped job, storage path, and range progress; its current controller state explains why it is paused",
        "the shared TiKV resource chain is caused by the disabled auto-tune and an unsustainable maintenance budget",
        "OLAP, compaction, off-peak backup and checkout QPS flash are competing explanations but fail the timing/identity test",
        "the safe decision is to adjust the bounded budget and resume the same job, then verify all final invariants",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.850198,
        reference_run_ids=(
            "tidb-mf-rg02-reference-mock-r106-20260828__"
            "tidb_resource_governance_br_slo_adaptive_throttling_frozen_history__"
            "br_slo_history_calibration__mock__r001",
        ),
    ),
)

_INVESTIGATION_WORKLOAD = replace(
    _CASE.background_workload,
    profiles=_CASE.background_workload.profiles[:5],
    worker_count=4,
    seed=20260904,
)
_INVESTIGATION_CASE = replace(
    _CASE,
    case_id="br_slo_history_investigation",
    case_no=1,
    evaluator=TidbResourceGovernanceBrSloHistoryInvestigationEvaluatorCase,
    title="Investigate a bounded BR/checkout contention window and continue the same artifact.",
    alert=(
        "P2 backup review: a smaller BR job was paused after checkout crossed its 35 ms guard. Reconstruct the six-hour history, "
        "exclude a single OLAP burst, and resume the same artifact with auto-tune and 1..2 backup threads per TiKV. "
        "Business data, history, space protection, replacement jobs, and cluster restarts remain out of scope."
    ),
    background_workload=_INVESTIGATION_WORKLOAD,
    frozen_history=replace(
        _CASE.frozen_history,
        duration_seconds=21_600,
        base_step_seconds=20,
        normal_capture_seconds=120,
        fault_capture_seconds=120,
        block_min_seconds=60,
        block_max_seconds=60,
        target_age_seconds_range=(900, 2_400),
        decoys=_CASE.frozen_history.decoys[:2],
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.5,
        reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
        protocol_version='difficulty-v2',
    ),
    row_count=_CASE.row_count // 2,
    initial_br_concurrency=3,
    initial_tikv_backup_threads=6,
    target_capture_seconds=180,
    minimum_br_run_seconds=max(30, _CASE.minimum_br_run_seconds // 2),
)


class TidbResourceGovernanceBrSloAdaptiveThrottlingFrozenHistoryScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_br_slo_adaptive_throttling_frozen_history"
    description = "Frozen-history historical reconstruction of a BR foreground-SLO resource incident."
    cases = (_CASE, _INVESTIGATION_CASE)

    def build_fault_plan(self, case: TidbResourceGovernanceBrSloFrozenHistoryCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernanceBrSloFrozenHistoryInjector,
                config={
                    "database": case.database,
                    "business_table": case.business_table,
                    "job_table": case.job_table,
                    "controller_table": case.controller_table,
                    "baseline_config_table": case.baseline_config_table,
                    "job_id_prefix": case.job_id_prefix,
                    "row_count": case.row_count,
                    "expected_business_integrity": case.expected_business_integrity,
                    "artifact_root": case.artifact_root,
                    "br_image": case.br_image,
                    "initial_br_concurrency": case.initial_br_concurrency,
                    "initial_tikv_backup_threads": case.initial_tikv_backup_threads,
                    "target_capture_seconds": case.target_capture_seconds,
                    "slo_p95_ms": case.slo_p95_ms,
                    "minimum_br_run_seconds": case.minimum_br_run_seconds,
                },
            ),
        )


__all__ = (
    "TidbResourceGovernanceBrSloAdaptiveThrottlingFrozenHistoryScenario",
    "TidbResourceGovernanceBrSloFrozenHistoryCase",
    "TidbResourceGovernanceBrSloFrozenHistoryInjector",
)
