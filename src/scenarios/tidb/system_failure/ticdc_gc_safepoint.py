import json
import re
import shlex
import time
from collections.abc import Mapping
from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.system_failure.ticdc_gc_safepoint import (
    TidbSystemFailureTiCdcGcSafepointEvaluatorCase,
    TidbSystemFailureTiCdcGcSafepointReducedBurstEvaluatorCase,
)
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    _compact_bytes,
    _table_row_key,
    _var_u64,
    connect_tidb,
    json_object,
    require_sql_success,
    run_sql_batches,
    validate_sql_identifier,
)
from src.scenarios.workloads import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase, WorkloadProfile

from ...base import DifficultyCalibration, FaultPlan, TiDBReplicationRuntime, TiDBScenario, TiDBScenarioCase
from ..runtime import MYSQL_8_4, TICDC_V8_1_0, TIDB_V8_1_0, tidb_runtime


SCENARIO_ID = "tidb_system_failure_ticdc_gc_safepoint"
CASE_ID = "ticdc_oom_leftover_lock_and_service_safepoint"
SOURCE_DB = "benchops"
TARGET_TABLE = "k02_orders"
ARCHIVE_TABLE = "k02_archive"
BACKUP_TABLE = "k02_backup"
ABANDONED_TABLE = "k02_abandoned"
TARGET_FEED = "k02-target"
HEALTHY_FEED = "k02-healthy"
BACKUP_FEED = "k02-backup"
ABANDONED_FEED = "k02-abandoned"
TARGET_CAPTURE = "ticdc/ticdc-0"
ABANDONED_CAPTURE = "ticdc/ticdc-1"
LIVE_WRITER_ID = 900000000000000001
K02_LOCK_TTL_MS = 3_600_000


def _encode_stale_lock(key: bytes) -> tuple[str, dict[str, int]]:
    start_ts = (int(time.time() * 1000) << 18) | (time.monotonic_ns() & ((1 << 18) - 1))
    min_commit_ts = start_ts - 1
    value = bytearray(b"P")
    value.extend(_compact_bytes(key))
    value.extend(_var_u64(start_ts))
    value.extend(_var_u64(K02_LOCK_TTL_MS))
    value.extend(b"c")
    value.extend(min_commit_ts.to_bytes(8, "big"))
    value.extend(b"a")
    value.extend(_var_u64(1))
    value.extend(_compact_bytes(key))
    return value.hex().upper(), {
        "start_ts": start_ts,
        "min_commit_ts": min_commit_ts,
    }


def _feed_profiles() -> tuple[WorkloadProfile, ...]:
    return (
        WorkloadProfile(
            name="k02_target_post_oom_writer",
            sql=(
                f"REPLACE INTO {SOURCE_DB}.{TARGET_TABLE} "
                f"(id, amount, note, payload) VALUES ({LIVE_WRITER_ID}, 7, 'post-oom-live', "
                "'post-oom-live-payload')"
            ),
            qps=0.25,
            tier="OLTP_CORE",
            commit=True,
            application_name="k02-order-writer",
        ),
        WorkloadProfile(
            name="k02_archive_health_writer",
            sql=(
                f"REPLACE INTO {SOURCE_DB}.{ARCHIVE_TABLE} "
                "(id, amount, note, payload) VALUES (900000000000000002, 11, "
                "'healthy-archive-live', 'healthy-archive-payload')"
            ),
            qps=0.20,
            tier="OLTP_CORE",
            commit=True,
            application_name="k02-archive-writer",
        ),
        WorkloadProfile(
            name="k02_orders_truth_probe",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(id), 0), "
                f"BIT_XOR(CRC32(CONCAT_WS('#', id, amount, note, payload))) "
                f"FROM {SOURCE_DB}.{TARGET_TABLE}"
            ),
            qps=0.40,
            tier="REPLICATION_OBSERVABILITY",
            application_name="k02-replication-audit",
        ),
        WorkloadProfile(
            name="k02_archive_truth_probe",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(id), 0), "
                f"BIT_XOR(CRC32(CONCAT_WS('#', id, amount, note, payload))) "
                f"FROM {SOURCE_DB}.{ARCHIVE_TABLE}"
            ),
            qps=0.35,
            tier="REPLICATION_OBSERVABILITY",
            application_name="k02-archive-audit",
        ),
        WorkloadProfile(
            name="k02_tso_probe",
            sql="SELECT TIDB_CURRENT_TSO()",
            qps=0.45,
            tier="REPLICATION_OBSERVABILITY",
            application_name="k02-tso-observer",
        ),
        WorkloadProfile(
            name="k02_region_probe",
            sql=(
                "SELECT REGION_ID, DB_NAME, TABLE_NAME FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
                f"WHERE DB_NAME = '{SOURCE_DB}' AND TABLE_NAME IN ('{TARGET_TABLE}', '{ARCHIVE_TABLE}') "
                "ORDER BY REGION_ID"
            ),
            qps=0.20,
            tier="REPLICATION_OBSERVABILITY",
            application_name="k02-region-observer",
        ),
        WorkloadProfile(
            name="k02_gc_sql_probe",
            sql=(
                "SELECT VARIABLE_NAME, VARIABLE_VALUE FROM mysql.tidb "
                "WHERE VARIABLE_NAME IN ('tikv_gc_safe_point', 'tikv_gc_last_run_time') "
                "ORDER BY VARIABLE_NAME"
            ),
            qps=0.18,
            tier="REPLICATION_OBSERVABILITY",
            application_name="k02-gc-observer",
        ),
        WorkloadProfile(
            name="k02_decoy_backup_probe",
            sql=f"SELECT COUNT(*), SUM(id) FROM {SOURCE_DB}.{BACKUP_TABLE}",
            qps=0.18,
            tier="BACKUP_MIGRATION",
            application_name="k02-backup-audit",
        ),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureTiCdcGcSafepointForTicdcOomLeftoverLockAndServiceSafepointScenarioCase(
    TiDBScenarioCase
):
    source_db: str
    target_table: str
    archive_table: str
    backup_table: str
    abandoned_table: str
    target_feed_id: str
    healthy_feed_id: str
    backup_feed_id: str
    abandoned_feed_id: str
    target_capture: str
    abandoned_capture: str
    target_writer_rate: float
    ticdc_oom_memory_mb: int
    catchup_window_seconds: int
    gc_owner_release_window_seconds: int
    gc_headroom_max_seconds: int
    disk_free_bytes: int
    compaction_pending_limit: int
    seeded_rows: int
    oom_burst_rows: int

    @property
    def target_truth_sql(self) -> str:
        return (
            f"SELECT COUNT(*), COALESCE(SUM(id), 0), "
            f"BIT_XOR(CRC32(CONCAT_WS('#', id, amount, note, payload))), "
            f"SUM(note LIKE 'post-oom%') FROM {self.source_db}.{self.target_table}"
        )

    @property
    def archive_truth_sql(self) -> str:
        return (
            f"SELECT COUNT(*), COALESCE(SUM(id), 0), "
            f"BIT_XOR(CRC32(CONCAT_WS('#', id, amount, note, payload))) "
            f"FROM {self.source_db}.{self.archive_table}"
        )


_CASE = TidbSystemFailureTiCdcGcSafepointForTicdcOomLeftoverLockAndServiceSafepointScenarioCase(
    case_id=CASE_ID,
    case_no=0,
    evaluator=TidbSystemFailureTiCdcGcSafepointEvaluatorCase,
    title="TiCDC OOM 后遗留 Region lock 与 abandoned service GC safepoint 复合故障",
    alert=(
        "[CRITICAL] k02_orders 的复制新鲜度越过告警窗口，目标 TiCDC capture 近期发生过内存异常，"
        "控制面可能仍显示 NORMAL；TiKV 旧版本、磁盘和 compaction 风险同时升高。请区分目标 feed、"
        "健康 archive/backup feed 和已经失联的 changefeed owner。公开目标 writer rate、TiCDC memory limit、"
        "catch-up window、GC owner release window、GC headroom、disk 与 compaction 阈值；不要删除业务数据、全局推进 GC、修改 GC lifetime、"
        "解析错误 Region/Store，或删除健康 owner。"
    ),
    initial_state={
        "target_feed": "post_oom_progress_or_lock_degraded",
        "abandoned_owner": "stale_service_safepoint_present",
        "gc": "effective_safepoint_pinned",
        "business": "target_freshness_behind",
    },
    expected_target={
        "target_feed": "normal_and_caught_up",
        "target_region": "healthy_without_target_lock",
        "abandoned_owner": "feed_removed_owner_released_to_gc_worker_boundary",
        "protected_owners": "active_healthy_backup_preserved",
        "gc": "advanced_with_headroom",
        "business": "source_downstream_equal",
    },
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "target TiCDC OOM/restart is associated with the target feed progress failure and a real Write CF/MVCC lock in the target Region",
                    "entity": "target_feed_region_lock_chain",
                    "evidence": ["OOMKilled capture state, target feed progress, bounded lock scan, and Region peer scope"],
                },
                {
                    "type": "root_cause",
                    "factor": "the target lock is an MVCC/Write CF condition in the observed Region rather than ordinary downstream sink lag",
                    "entity": "target_region_mvcc_lock",
                    "evidence": ["lock CF raw scan across every current peer Store and healthy-feed counterfactual"],
                },
                {
                    "type": "root_cause",
                    "factor": "an abandoned TiCDC service GC safepoint owner remains without a live runtime and pins the effective oldest safepoint",
                    "entity": "abandoned_service_gc_safepoint",
                    "evidence": ["PD service_gc_safe_points, exact changefeed ID, stopped capture, and stale owner mapping"],
                },
                {
                    "type": "scope",
                    "factor": "target, abandoned, healthy, and backup owner scopes are distinct",
                    "entity": "ticdc_owner_scope",
                    "evidence": ["capture diagnostics, service IDs, and preserved owner snapshots"],
                },
                {
                    "type": "scope_exclusion",
                    "factor": "changing tidb_gc_life_time, deleting all feeds, or resolving every Region is not a repair",
                    "entity": "unsafe_global_shortcuts",
                    "evidence": ["GC config, owner list, Region peer set, and safety boundaries"],
                },
                {
                    "type": "joint_recovery",
                    "factor": "repairing only the target feed/lock chain or only the abandoned safepoint chain leaves OutcomePass false",
                    "entity": "two_chain_joint_acceptance",
                    "evidence": ["partial final-state checks for progress/lock and GC/owner cleanup"],
                },
                {
                    "type": "joint_verification",
                    "factor": "progress, lock, Region health, GC headroom, disk, compaction, and source/downstream business truth must converge together",
                    "entity": "k02_final_invariants",
                    "evidence": ["trusted final-state verification over the declared catch-up and sampling windows"],
                },
            ]
        },
        "outcome": {
            "changes": [
                "resolved only the observed target Region lock scope through the versioned read-before-write path",
                "removed only the exact abandoned changefeed and waited for its cluster-level service safepoint to release to the gc_worker boundary",
            ],
            "verification": [
                "target progress, lock scope, Region peers, owner preservation, GC headroom, disk, compaction, and source/downstream truth converged",
            ],
        },
        "summary": "The two real TiCDC/GC chains were diagnosed and repaired without touching protected feeds, Regions, or business data.",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_feed_profiles(),
        worker_count=4,
        seed=20260819,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=12.0,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.625,
        reference_run_ids=("reference-282__tidb_system_failure_ticdc_gc_safepoint",),
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
            ticdc_count=2,
            ticdc_cluster_ids=("default", "k02-abandoned"),
        ),
    ),
    source_db=SOURCE_DB,
    target_table=TARGET_TABLE,
    archive_table=ARCHIVE_TABLE,
    backup_table=BACKUP_TABLE,
    abandoned_table=ABANDONED_TABLE,
    target_feed_id=TARGET_FEED,
    healthy_feed_id=HEALTHY_FEED,
    backup_feed_id=BACKUP_FEED,
    abandoned_feed_id=ABANDONED_FEED,
    target_capture=TARGET_CAPTURE,
    abandoned_capture=ABANDONED_CAPTURE,
    target_writer_rate=0.25,
    ticdc_oom_memory_mb=128,
    catchup_window_seconds=180,
    gc_owner_release_window_seconds=360,
    gc_headroom_max_seconds=3600,
    disk_free_bytes=512 * 1024 * 1024,
    compaction_pending_limit=32,
    seeded_rows=64,
    oom_burst_rows=8000,
)

_REDUCED_BURST_CASE = replace(
    _CASE,
    case_id="ticdc_gc_safepoint_reduced_oom_burst",
    case_no=1,
    evaluator=TidbSystemFailureTiCdcGcSafepointReducedBurstEvaluatorCase,
    title="较小 OOM 写入突发下的 TiCDC Region lock 与 abandoned GC safepoint 复合故障",
    oom_burst_rows=3200,
    target_writer_rate=4.0,
    background_workload=replace(_CASE.background_workload, worker_count=3),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.473684,
        reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
        protocol_version='difficulty-v2',
    ),
)


class TidbSystemFailureTiCdcGcSafepointInjector(BaseFaultInjector):

    retain_workload_after_metric_history = True

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""
    """Create the real target OOM/lock chain and the independent stale safepoint owner."""

    def __init__(self) -> None:
        self._configured = False
        self._lock_connection = None
        self._evidence: dict[str, object] = {}
        self._created_changefeeds: list[tuple[str, str]] = []
        self._ticdc_memory_limit_changed = False

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_schema(context.env)
        self._seed_schema(context.env)
        self._create_changefeeds(context.env)
        self._record_region_scope(context.env)
        self._hold_target_lock(context.env)
        self._trigger_target_oom(context.env)
        self._verify_fault_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_fault_state(context.env)
        deployment = context.env.get_deployment()
        lock_observation = deployment.mvcc_lock_list(
            int(self._evidence["target_region_id"]),
            tuple(self._evidence["target_store_targets"]),
            32,
        )
        if not any(peer["records"] for peer in lock_observation["peers"]):
            raise RuntimeError(
                "K02 prepare_observability found no target lock after OOM: "
                f"run_id={context.run_id!r}, lock_observation={lock_observation!r}"
            )
        self._evidence["target_lock_observation"] = lock_observation
        self._evidence["gc_safepoint_before_agent"] = deployment.gc_safepoint_list()
        self._evidence["target_node_state_before_agent"] = deployment.node_states()[self.target_capture]
        self._evidence["target_memory_restore_before_agent"] = deployment.set_ticdc_memory_limit(
            self.target_capture,
            context.case.runtime.replication.ticdc_memory_mb,
        )
        self._ticdc_memory_limit_changed = False
        return dict(self._evidence)

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        if self._lock_connection is not None:
            self._lock_connection.close()
            self._lock_connection = None

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        deployment = context.env.get_deployment()
        if self._lock_connection is not None:
            self._lock_connection.close()
            self._lock_connection = None
        if self._ticdc_memory_limit_changed:
            deployment.set_ticdc_memory_limit(self.target_capture, 1024)
            self._ticdc_memory_limit_changed = False
        if self._created_changefeeds:
            for target in (self.target_capture, self.abandoned_capture):
                state = deployment.node_states()[target]
                if not state["running"]:
                    deployment.start_component(target)
            deployment._wait("ticdc", deployment._check_ticdc, 180)
            remove_deadline = time.monotonic() + 120
            for capture, feed_id in self._created_changefeeds:
                while True:
                    try:
                        deployment.remove_changefeed(capture, feed_id)
                        break
                    except RuntimeError as error:
                        # A freshly restarted capture answers /status but its
                        # CLI rejects mutations until the owner session is
                        # re-established; retry while the window is open.
                        if "ErrServerIsNotReady" not in str(error) or time.monotonic() >= remove_deadline:
                            raise
                        time.sleep(2)
            self._created_changefeeds.clear()
        require_sql_success(
            context.env.execute_internal_sql(f"DROP DATABASE IF EXISTS {self.source_db}"),
            "drop K02 source database",
        )
        require_sql_success(
            context.env.execute_sql_trusted(f"DROP DATABASE IF EXISTS {self.source_db}", target="downstream"),
            "drop K02 downstream database",
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        if self._configured:
            return
        self.source_db = validate_sql_identifier(str(config["source_db"]), "source_db")
        self.target_table = validate_sql_identifier(str(config["target_table"]), "target_table")
        self.archive_table = validate_sql_identifier(str(config["archive_table"]), "archive_table")
        self.backup_table = validate_sql_identifier(str(config["backup_table"]), "backup_table")
        self.abandoned_table = validate_sql_identifier(str(config["abandoned_table"]), "abandoned_table")
        self.target_feed_id = str(config["target_feed_id"])
        self.healthy_feed_id = str(config["healthy_feed_id"])
        self.backup_feed_id = str(config["backup_feed_id"])
        self.abandoned_feed_id = str(config["abandoned_feed_id"])
        self.target_capture = str(config["target_capture"])
        self.abandoned_capture = str(config["abandoned_capture"])
        self.target_cluster_id = str(config["target_cluster_id"])
        self.abandoned_cluster_id = str(config["abandoned_cluster_id"])
        for name in ("target_feed_id", "healthy_feed_id", "backup_feed_id", "abandoned_feed_id"):
            if re.fullmatch(r"[a-z0-9][a-z0-9_-]*", getattr(self, name)) is None:
                raise ValueError(f"Invalid K02 changefeed ID: field={name!r}, value={getattr(self, name)!r}")
        self.ticdc_oom_memory_mb = int(config["ticdc_oom_memory_mb"])
        self.oom_burst_rows = int(config["oom_burst_rows"])
        self.seeded_rows = int(config["seeded_rows"])
        self._configured = True

    @property
    def _tables(self) -> tuple[str, ...]:
        return (self.target_table, self.archive_table, self.backup_table, self.abandoned_table)

    def _create_schema(self, env) -> None:
        require_sql_success(env.execute_internal_sql(f"DROP DATABASE IF EXISTS {self.source_db}"), "clear K02 source database")
        require_sql_success(env.execute_internal_sql(f"CREATE DATABASE {self.source_db}"), "create K02 source database")
        for table in self._tables:
            require_sql_success(
                env.execute_internal_sql(
                    f"CREATE TABLE {self.source_db}.{table} ("
                    "id BIGINT PRIMARY KEY, amount BIGINT NOT NULL, note VARCHAR(128) NOT NULL, "
                    "payload VARCHAR(4096) NOT NULL)"
                ),
                f"create K02 source table {table}",
            )
        require_sql_success(
            env.execute_sql_trusted(f"DROP DATABASE IF EXISTS {self.source_db}", target="downstream"),
            "clear K02 downstream database",
        )
        require_sql_success(
            env.execute_sql_trusted(f"CREATE DATABASE {self.source_db}", target="downstream"),
            "create K02 downstream database",
        )
        for table in self._tables:
            require_sql_success(
                env.execute_sql_trusted(
                    f"CREATE TABLE {self.source_db}.{table} ("
                    "id BIGINT PRIMARY KEY, amount BIGINT NOT NULL, note VARCHAR(128) NOT NULL, "
                    "payload VARCHAR(4096) NOT NULL)",
                    target="downstream",
                ),
                f"create K02 downstream table {table}",
            )

    def _seed_schema(self, env) -> None:
        # A freshly created table races TiDB's schema-lease sync on a loaded
        # host; the first statement can fail with 8027 until the lease lands.
        schema_deadline = time.monotonic() + 90
        while True:
            try:
                env.execute_internal_sql(
                    f"SELECT 1 FROM {self.source_db}.{self.target_table} LIMIT 1"
                )
                break
            except Exception as exc:
                if time.monotonic() >= schema_deadline or "8027" not in repr(exc):
                    raise
                time.sleep(2)
        values = tuple(
            f"({row_id}, {row_id * 3}, 'seed-{row_id}', 'seed-payload-{row_id}')"
            for row_id in range(1, self.seeded_rows + 1)
        )
        run_sql_batches(
            env.execute_internal_sql,
            f"INSERT INTO {self.source_db}.{self.target_table} (id, amount, note, payload) VALUES ",
            values,
            32,
            "seed K02 target rows",
        )
        for table, prefix in (
            (self.archive_table, "archive"),
            (self.backup_table, "backup"),
            (self.abandoned_table, "abandoned"),
        ):
            require_sql_success(
                env.execute_internal_sql(
                    f"INSERT INTO {self.source_db}.{table} (id, amount, note, payload) "
                    f"VALUES (1, 1, '{prefix}-seed', '{prefix}-payload')"
                ),
                f"seed K02 protected table {table}",
            )
        run_sql_batches(
            lambda sql: env.execute_sql_trusted(sql, target="downstream"),
            f"INSERT INTO {self.source_db}.{self.target_table} (id, amount, note, payload) VALUES ",
            values,
            32,
            "seed K02 downstream target rows",
        )
        for table, prefix in (
            (self.archive_table, "archive"),
            (self.backup_table, "backup"),
            (self.abandoned_table, "abandoned"),
        ):
            require_sql_success(
                env.execute_sql_trusted(
                    f"INSERT INTO {self.source_db}.{table} (id, amount, note, payload) "
                    f"VALUES (1, 1, '{prefix}-seed', '{prefix}-payload')",
                    target="downstream",
                ),
                f"seed K02 downstream protected table {table}",
            )

    def _write_feed_config(
        self,
        deployment,
        capture: str,
        feed_id: str,
        table: str,
    ) -> str:
        config_path = f"/tmp/k02-{feed_id}.toml"
        content = f"[filter]\nrules = ['{self.source_db}.{table}']\n"
        deployment.exec(
            capture,
            ["sh", "-lc", f"printf %s {shlex.quote(content)} > {shlex.quote(config_path)}"],
        )
        return config_path

    def _create_changefeed(
        self,
        deployment,
        capture: str,
        feed_id: str,
        table: str,
        start_ts: int,
    ) -> None:
        config_path = self._write_feed_config(deployment, capture, feed_id, table)
        sink_uri = (
            f"mysql://root@mysql-0:3306/{self.source_db}"
            "?worker-count=4&max-txn-row=256&batch-dml-enable=true"
        )
        command = [
            "/cdc", "cli", "changefeed", "create",
            "--server=http://127.0.0.1:8300",
            f"--sink-uri={sink_uri}",
            f"--changefeed-id={feed_id}",
            f"--start-ts={start_ts}",
            f"--config={config_path}",
            "--no-confirm",
        ]
        deployment.exec(capture, command)
        self._created_changefeeds.append((capture, feed_id))

    def _capture_status(self, deployment, capture: str, feed_id: str) -> dict[str, object]:
        payload = json.loads(
            deployment.exec(capture, ["wget", "-qO-", "-T", "5", f"http://127.0.0.1:8300/api/v1/changefeeds/{feed_id}"])
        )
        if not isinstance(payload, dict):
            raise TypeError(f"K02 TiCDC status must be an object: capture={capture!r}, feed_id={feed_id!r}, payload={payload!r}")
        return payload

    def _wait_feed(self, deployment, capture: str, feed_id: str) -> dict[str, object]:
        deadline = time.monotonic() + 180
        last: dict[str, object] | None = None
        while time.monotonic() < deadline:
            try:
                last = self._capture_status(deployment, capture, feed_id)
            except RuntimeError as error:
                # A settling TiCDC briefly answers its API with 4xx/5xx while
                # feeds initialize; treat that as not-yet-converged instead of
                # letting a single transport error kill the run.
                last = {"state": "transient_error", "error": str(error)}
            if str(last.get("state", "")).casefold() == "normal" and not last.get("error"):
                return last
            time.sleep(2)
        raise RuntimeError(f"K02 changefeed did not become normal: capture={capture!r}, feed_id={feed_id!r}, last={last!r}")

    def _reconcile_target_capture(self, deployment) -> None:
        deployment.stop_component(self.target_capture)
        deployment.start_component(self.target_capture)
        deployment._wait(
            self.target_capture,
            lambda: deployment.changefeed_diagnostics(self.target_capture),
            180,
        )
        for feed_id in (self.target_feed_id, self.healthy_feed_id, self.backup_feed_id):
            self._wait_feed(deployment, self.target_capture, feed_id)

        deadline = time.monotonic() + 180
        last = None
        initializing_prefix = f"ticdc-{self.target_cluster_id}-initializing-"
        while time.monotonic() < deadline:
            last = deployment.gc_safepoint_list()
            initializing = [
                owner
                for owner in last["service_gc_safe_points"]
                if str(owner.get("service_id", "")).startswith(initializing_prefix)
            ]
            if not initializing:
                return
            time.sleep(2)
        raise RuntimeError(
            "K02 target TiCDC feed bootstrap left initializing service safepoint owners after reconcile: "
            f"capture={self.target_capture!r}, owners={initializing!r}, safepoint={last!r}"
        )

    def _create_changefeeds(self, env) -> None:
        deployment = env.get_deployment()
        start_ts = env.current_tso()
        safepoint = deployment.gc_safepoint_list()
        gc_workers = [
            owner
            for owner in safepoint["service_gc_safe_points"]
            if isinstance(owner, dict) and owner.get("service_id") == "gc_worker"
        ]
        if len(gc_workers) != 1:
            raise RuntimeError(
                "K02 requires exactly one gc_worker safepoint before creating feeds: "
                f"gc_workers={gc_workers!r}, safepoint={safepoint!r}"
            )
        abandoned_start_ts = int(gc_workers[0]["safe_point"]) + 1
        if abandoned_start_ts >= start_ts:
            raise RuntimeError(
                "K02 abandoned feed start-ts must be after the current gc_worker boundary and before current TSO: "
                f"abandoned_start_ts={abandoned_start_ts}, current_start_ts={start_ts}, gc_worker={gc_workers[0]!r}"
            )
        self._create_changefeed(
            deployment,
            self.abandoned_capture,
            self.abandoned_feed_id,
            self.abandoned_table,
            abandoned_start_ts,
        )
        self._stop_abandoned_capture(env)
        self._create_changefeed(deployment, self.target_capture, self.target_feed_id, self.target_table, start_ts)
        self._create_changefeed(deployment, self.target_capture, self.healthy_feed_id, self.archive_table, start_ts)
        self._create_changefeed(deployment, self.target_capture, self.backup_feed_id, self.backup_table, start_ts)
        for feed_id in (self.target_feed_id, self.healthy_feed_id, self.backup_feed_id):
            self._wait_feed(deployment, self.target_capture, feed_id)
        self._reconcile_target_capture(deployment)
        self._evidence["feed_start_ts"] = start_ts
        self._evidence["abandoned_start_ts"] = abandoned_start_ts
        self._evidence["target_feed_before_oom"] = self._capture_status(deployment, self.target_capture, self.target_feed_id)

    def _record_region_scope(self, env) -> None:
        deployment = env.get_deployment()
        expected_peer_count = len(deployment.COMPONENTS["tikv"])
        deadline = time.monotonic() + 180
        last_observation = None
        requested_peer_store_ids: set[int] = set()
        while time.monotonic() < deadline:
            payload = json_object(
                env.execute_internal_sql(
                    "SELECT REGION_ID FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
                    f"WHERE DB_NAME = '{self.source_db}' AND TABLE_NAME = '{self.target_table}' AND IS_INDEX = 0 "
                    "ORDER BY REGION_ID"
                ),
                "locate K02 target Region",
            )
            region_ids = tuple(int(row[0]) for row in payload["result"])
            if len(region_ids) != 1:
                raise RuntimeError(
                    "K02 target table must occupy exactly one Region before fault injection: "
                    f"region_ids={region_ids!r}"
                )
            region = deployment.pd_request("GET", f"/pd/api/v1/region/id/{region_ids[0]}")
            stores = deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
            address_to_target = {
                str(item["store"]["address"]): f"tikv/{str(item['store']['address']).rsplit(':', 1)[0]}"
                for item in stores
            }
            peers = tuple(sorted(int(peer["store_id"]) for peer in region["peers"]))
            store_targets = tuple(
                address_to_target[str(item["store"]["address"])]
                for item in stores
                if int(item["store"]["id"]) in peers
            )
            last_observation = {
                "region": region,
                "stores": stores,
                "peers": peers,
                "store_targets": store_targets,
            }
            requested_peer_store_ids.difference_update(peers)
            if len(store_targets) == expected_peer_count and len(peers) == expected_peer_count:
                self._evidence.update({
                    "target_region_id": region_ids[0],
                    "target_store_targets": store_targets,
                    "target_peer_store_ids": peers,
                    "target_region_before_fault": region,
                })
                return
            if len(peers) > expected_peer_count:
                raise RuntimeError(
                    "K02 target Region has more peers than the configured TiKV topology: "
                    f"expected_peer_count={expected_peer_count}, last_observation={last_observation!r}"
                )
            if len(peers) < expected_peer_count:
                candidate_store_id = next(
                    (
                        int(item["store"]["id"])
                        for item in stores
                        if str(item["store"].get("state_name", "")) == "Up"
                        and int(item["store"]["id"]) not in peers
                        and int(item["store"]["id"]) not in requested_peer_store_ids
                    ),
                    None,
                )
                if candidate_store_id is not None:
                    deployment.add_region_peer(region_ids[0], candidate_store_id)
                    requested_peer_store_ids.add(candidate_store_id)
            time.sleep(2)
        raise RuntimeError(
            "K02 target Region did not converge to the complete TiKV peer set: "
            f"expected_peer_count={expected_peer_count}, last_observation={last_observation!r}"
        )

    def _hold_target_lock(self, env) -> None:
        self._lock_connection = connect_tidb(env, database=self.source_db, autocommit=False, application_name="k02-abandoned-lock")
        with self._lock_connection.cursor() as cursor:
            cursor.execute("SET SESSION tidb_txn_mode = 'pessimistic'")
            cursor.execute("BEGIN PESSIMISTIC")
            cursor.execute(f"SELECT id FROM {self.target_table} WHERE id = 1 FOR UPDATE")
            if cursor.fetchone() != (1,):
                raise RuntimeError("K02 lock transaction did not lock target row id=1")
            cursor.execute(
                "SELECT TIDB_TABLE_ID FROM INFORMATION_SCHEMA.TABLES "
                f"WHERE TABLE_SCHEMA = '{self.source_db}' AND TABLE_NAME = '{self.target_table}'"
            )
            table_row = cursor.fetchone()
        if table_row is None:
            raise RuntimeError(
                "K02 target table ID lookup returned no row after acquiring the target lock: "
                f"database={self.source_db!r}, table={self.target_table!r}"
            )
        target_key = _table_row_key(int(table_row[0]), 1)
        stale_value, timestamp_facts = _encode_stale_lock(target_key)
        self._lock_connection.close()
        self._lock_connection = None
        rewritten = env.get_deployment().rewrite_mvcc_lock(
            int(self._evidence["target_region_id"]),
            tuple(self._evidence["target_store_targets"]),
            target_key.hex().upper(),
            stale_value,
        )
        if tuple(sorted(rewritten["store_targets"])) != tuple(sorted(self._evidence["target_store_targets"])):
            raise RuntimeError(
                "K02 stale lock rewrite returned a different Region peer scope: "
                f"expected={self._evidence['target_store_targets']!r}, rewritten={rewritten!r}"
            )
        self._evidence["lock_key_hint"] = f"{self.source_db}.{self.target_table}.id=1"
        self._evidence["lock_key_hex"] = target_key.hex().upper()
        self._evidence["lock_timestamp_facts"] = timestamp_facts

    def _trigger_target_oom(self, env) -> None:
        deployment = env.get_deployment()
        deployment.set_ticdc_memory_limit(self.target_capture, self.ticdc_oom_memory_mb)
        self._ticdc_memory_limit_changed = True
        values = tuple(
            f"({1000000000000 + row_id}, {row_id}, 'post-oom-burst-{row_id}', '{'x' * 3500}')"
            for row_id in range(1, self.oom_burst_rows + 1)
        )
        run_sql_batches(
            env.execute_internal_sql,
            f"INSERT INTO {self.source_db}.{self.target_table} (id, amount, note, payload) VALUES ",
            values,
            64,
            "create K02 target OOM burst",
        )
        deadline = time.monotonic() + 180
        state = None
        while time.monotonic() < deadline:
            state = deployment.node_states()[self.target_capture]
            if state["oom_killed"]:
                self._evidence["target_oom_state"] = state
                return
            time.sleep(2)
        raise RuntimeError(
            "K02 target TiCDC did not reach Docker OOMKilled state: "
            f"target={self.target_capture!r}, memory_mb={self.ticdc_oom_memory_mb}, state={state!r}"
        )

    def _stop_abandoned_capture(self, env) -> None:
        deployment = env.get_deployment()
        before = deployment.gc_safepoint_list()
        cluster_prefix = f"ticdc-{self.abandoned_cluster_id}-"
        candidates = [
            owner
            for owner in before["service_gc_safe_points"]
            if isinstance(owner, dict)
            and str(owner.get("service_id", "")).startswith(cluster_prefix)
            and "-initializing-" not in str(owner.get("service_id", ""))
            and "-creating-" not in str(owner.get("service_id", ""))
        ]
        if len(candidates) != 1:
            raise RuntimeError(
                "K02 requires exactly one real abandoned service owner before stopping its capture: "
                f"feed_id={self.abandoned_feed_id!r}, candidates={candidates!r}, safepoint={before!r}"
            )
        deployment.stop_component(self.abandoned_capture)
        deadline = time.monotonic() + 60
        after = None
        while time.monotonic() < deadline:
            after = deployment.gc_safepoint_list()
            if any(
                isinstance(owner, dict)
                and str(owner.get("service_id", "")) == candidates[0]["service_id"]
                for owner in after["service_gc_safe_points"]
            ):
                break
            time.sleep(2)
        else:
            raise RuntimeError(
                "K02 abandoned capture did not leave an observable service safepoint owner: "
                f"capture={self.abandoned_capture!r}, before={before!r}, after={after!r}"
            )
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            after = deployment.gc_safepoint_list()
            matches = [
                owner
                for owner in after["service_gc_safe_points"]
                if isinstance(owner, dict) and owner.get("service_id") == candidates[0]["service_id"]
            ]
            if len(matches) == 1:
                break
            time.sleep(1)
        else:
            raise RuntimeError(
                "K02 stopped abandoned capture did not retain its cluster-level service owner: "
                f"service_id={candidates[0]['service_id']!r}, after={after!r}"
            )
        self._evidence["gc_safepoint_after_abandon"] = after

    def _verify_fault_state(self, env) -> None:
        deployment = env.get_deployment()
        state = deployment.node_states()[self.target_capture]
        if not state["oom_killed"]:
            raise RuntimeError(f"K02 target capture is not OOMKilled: target={self.target_capture!r}, state={state!r}")
        safepoint = deployment.gc_safepoint_list()
        abandoned_prefix = f"ticdc-{self.abandoned_cluster_id}-"
        candidates = [
            owner for owner in safepoint["service_gc_safe_points"]
            if isinstance(owner, dict)
            and str(owner.get("service_id", "")).startswith(abandoned_prefix)
            and "-initializing-" not in str(owner.get("service_id", ""))
            and "-creating-" not in str(owner.get("service_id", ""))
        ]
        if len(candidates) != 1:
            raise RuntimeError(
                "K02 abandoned owner mapping is not exact: "
                f"feed_id={self.abandoned_feed_id!r}, candidates={candidates!r}, safepoint={safepoint!r}"
            )
        gc_workers = [
            owner
            for owner in safepoint["service_gc_safe_points"]
            if isinstance(owner, dict) and owner.get("service_id") == "gc_worker"
        ]
        if len(gc_workers) != 1 or int(candidates[0]["safe_point"]) > int(gc_workers[0]["safe_point"]):
            raise RuntimeError(
                "K02 abandoned owner is not pinning at or below the effective gc_worker safepoint: "
                f"abandoned={candidates[0]!r}, gc_workers={gc_workers!r}, safepoint={safepoint!r}"
            )
        self._evidence["gc_worker_safe_point"] = int(gc_workers[0]["safe_point"])
        self._evidence["abandoned_service_id"] = str(candidates[0]["service_id"])
        target_prefix = f"ticdc-{self.target_cluster_id}-"
        target_owners = [
            owner
            for owner in safepoint["service_gc_safe_points"]
            if isinstance(owner, dict)
            and str(owner.get("service_id", "")).startswith(target_prefix)
            and "-initializing-" not in str(owner.get("service_id", ""))
            and "-creating-" not in str(owner.get("service_id", ""))
        ]
        if len(target_owners) != 1:
            raise RuntimeError(
                "K02 target TiCDC cluster owner mapping is not exact: "
                f"cluster_id={self.target_cluster_id!r}, owners={target_owners!r}, safepoint={safepoint!r}"
            )
        service_ids = {
            "target": str(target_owners[0]["service_id"]),
            "healthy": str(target_owners[0]["service_id"]),
            "backup": str(target_owners[0]["service_id"]),
            "abandoned": str(candidates[0]["service_id"]),
        }
        self._evidence["service_ids"] = service_ids
        self._evidence["gc_safepoint_fault"] = safepoint


class TidbSystemFailureTiCdcGcSafepointScenario(TiDBScenario):
    scenario_id = SCENARIO_ID
    description = "TiCDC OOM/restart leaves a target MVCC lock while an abandoned service safepoint pins GC."
    cases = (_CASE, _REDUCED_BURST_CASE)

    def build_fault_plan(
        self,
        case: TidbSystemFailureTiCdcGcSafepointForTicdcOomLeftoverLockAndServiceSafepointScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureTiCdcGcSafepointInjector,
                config={
                    "source_db": case.source_db,
                    "target_table": case.target_table,
                    "archive_table": case.archive_table,
                    "backup_table": case.backup_table,
                    "abandoned_table": case.abandoned_table,
                    "target_feed_id": case.target_feed_id,
                    "healthy_feed_id": case.healthy_feed_id,
                    "backup_feed_id": case.backup_feed_id,
                    "abandoned_feed_id": case.abandoned_feed_id,
                    "target_capture": case.target_capture,
                    "abandoned_capture": case.abandoned_capture,
                    "target_cluster_id": case.runtime.replication.ticdc_cluster_ids[0],
                    "abandoned_cluster_id": case.runtime.replication.ticdc_cluster_ids[1],
                    "ticdc_oom_memory_mb": case.ticdc_oom_memory_mb,
                    "seeded_rows": case.seeded_rows,
                    "oom_burst_rows": case.oom_burst_rows,
                },
            ),
        )
