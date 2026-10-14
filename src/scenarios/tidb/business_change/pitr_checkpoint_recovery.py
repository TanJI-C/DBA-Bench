from __future__ import annotations

import hashlib
import os
import re
import selectors
import shlex
import subprocess
import time
from dataclasses import dataclass, replace
from datetime import datetime

import pymysql

from src.database.sql import sql_literal
from src.protocols.report import structured_reference_report
from src.scenarios.evaluation.tidb.business_change.pitr_checkpoint_recovery import (
    TidbBusinessChangePitrCheckpointRecoveryEvaluatorCase,
    TidbBusinessChangePitrCheckpointRecoverySingleInterruptionEvaluatorCase,
)
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    run_sql_batches,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.specs import TiDBCaseRuntime
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbBusinessChangePitrCheckpointRecoveryForResumeFailedPitrWithoutBreakingChainScenarioCase(
    TiDBScenarioCase
):
    business_database: str
    control_database: str
    orders_table: str
    order_items_table: str
    payments_table: str
    marker_table: str
    attempt_table: str
    backup_table: str
    object_table: str
    operator_touch_target_table: str
    request_id: str
    selected_attempt_id: str
    target_marker: str
    post_target_marker: str
    expected_orders: int
    expected_order_id_sum: int
    expected_amount_sum: int
    expected_order_items: int
    expected_item_id_sum: int
    expected_payments: int
    expected_payment_id_sum: int
    expected_source_orders: int
    expected_source_order_id_sum: int
    expected_source_order_items: int
    expected_source_payments: int
    target_runtime: TiDBCaseRuntime
    br_image: str
    minio_image: str
    mc_image: str


class _K08CommandError(RuntimeError):
    pass


def _background_workload() -> BackgroundWorkloadSpec:
    business_database = "benchops"
    control_database = "benchops_k08"
    orders_table = "k08_orders"
    marker_table = "k08_markers"
    backup_table = "k08_backup_requests"
    attempt_table = "k08_restore_attempts"
    return BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="k08_source_order_summary",
                sql=(
                    f"SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
                    f"COALESCE(SUM(amount_cents), 0) FROM {business_database}.{orders_table}"
                ),
                qps=0.45,
                tier="BUSINESS_READ",
                application_name="checkout-api",
            ),
            WorkloadProfile(
                name="k08_marker_progress_watch",
                sql=(
                    f"SELECT marker, committed_tso FROM {business_database}.{marker_table} "
                    "ORDER BY committed_tso DESC"
                ),
                qps=0.34,
                tier="RECOVERY_OBSERVABILITY",
                application_name="recovery-dashboard",
            ),
            WorkloadProfile(
                name="k08_backup_request_watch",
                sql=(
                    f"SELECT request_id, snapshot_status, log_status, log_checkpoint_ts, "
                    f"continuity_status FROM {control_database}.{backup_table}"
                ),
                qps=0.30,
                tier="RECOVERY_OBSERVABILITY",
                application_name="backup-monitor",
            ),
            WorkloadProfile(
                name="k08_restore_attempt_history",
                sql=(
                    f"SELECT attempt_id, phase, status, checkpoint_status, log_continuity "
                    f"FROM {control_database}.{attempt_table} ORDER BY attempt_id DESC LIMIT 12"
                ),
                qps=0.28,
                tier="RECOVERY_OBSERVABILITY",
                application_name="restore-orchestrator",
            ),
            WorkloadProfile(
                name="k08_historical_backup_decoy",
                sql=(
                    f"SELECT request_id, snapshot_backup_ts, requested_target_ts, continuity_status "
                    f"FROM {control_database}.{backup_table} "
                    "WHERE request_id <> 'k08-historical-request' ORDER BY snapshot_backup_ts"
                ),
                qps=0.22,
                tier="DECOY_READ",
                application_name="backup-audit",
            ),
        ),
        worker_count=5,
        seed=0xC008,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=2.0,
    )


_CASE = TidbBusinessChangePitrCheckpointRecoveryForResumeFailedPitrWithoutBreakingChainScenarioCase(
    case_id="resume_failed_pitr_without_breaking_chain",
    case_no=0,
    evaluator=TidbBusinessChangePitrCheckpointRecoveryEvaluatorCase,
    title="Resume an interrupted isolated PITR without breaking the backup chain.",
    alert=(
        "隔离恢复集群上的一次业务 PITR 任务中断，source 集群仍在持续提供订单服务。请先从当前 "
        "restore task、备份存储、集群状态和业务数据判断恢复任务处于什么阶段，再决定是否可以安全继续。"
        "目标是把恢复推进到公开的目标时间点，并证明 snapshot、log backup、checkpoint 和 target "
        "业务结果连续；不能在 source/production 上重试，不能删除或改写 backup objects，不能用更晚的 "
        "时间点掩盖日志缺口；恢复窗口内 partial target 可能经历过外部操作，不能在未证明兼容性前写入、删表或盲目重试。"
    ),
    initial_state={
        "source_service": "healthy_and_writing",
        "restore_task": "interrupted",
        "target": "isolated_partial_state_requires_compatibility_check",
        "backup_chain": "requires_verification",
        "checkpoint": "persisted_but_unclassified",
    },
    expected_target={
        "restore_task": "completed",
        "target": "isolated_and_consistent",
        "time_boundary": "target_marker_present_post_target_absent",
        "source": "unchanged",
        "backup_objects": "unchanged",
    },
        background_workload=_background_workload(),
    reference_report=structured_reference_report(
        case_id="resume_failed_pitr_without_breaking_chain",
        factors=(
            "the isolated PITR restore failed during log restore after a partial target and checkpoint were persisted",
            "the checkpoint is bound to the same upstream cluster, snapshot BackupTS, log start-ts, restored-ts, target TSO, and isolated target as the failed attempt",
            "the BR and target version support checkpoint restore and the observed checkpoint location is the version-correct external log-backup prefix rather than an unrelated candidate prefix",
            "the snapshot and log backup chain is continuous and retention still reaches the requested target without a missing or corrupt segment",
            "the partial target table identity or downstream ID mapping changed after checkpoint persistence even though the business schema and data still look equivalent, so the checkpoint is not safe to resume on that target even though cluster identity matches; the safe decision is an explicitly isolated clean restart",
        ),
        changes=("isolated the touched partial target and completed a clean PITR restart with unchanged time boundaries",),
        verification=(
            "the isolated target reached terminal completion",
            "target marker is present and post-target marker is absent",
            "target business truth and source protection were verified",
        ),
        summary="The reference path rejected exact resume on a touched partial target, used a new isolated target, and proved chain and business continuity.",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.627451,
        reference_run_ids=("reference-266__tidb_business_change_pitr_checkpoint_recovery__resume_failed_pitr_without_breaking_chain__mock__r001",),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=1,
        sql_timeout_seconds=180,
        tikv_memory_mb=2048,
        tidb_memory_mb=1024,
        readiness_timeout_seconds=1800,
    ),
    business_database="benchops",
    control_database="benchops_k08",
    orders_table="k08_orders",
    order_items_table="k08_order_items",
    payments_table="k08_payments",
    marker_table="k08_markers",
    attempt_table="k08_restore_attempts",
    backup_table="k08_backup_requests",
    object_table="k08_backup_objects",
    operator_touch_target_table="k08_orders",
    request_id="k08-pitr-orders-20260818",
    selected_attempt_id="k08-pitr-orders-20260818-attempt-001",
    target_marker="target-window-b",
    post_target_marker="post-target-c",
    expected_orders=2000,
    expected_order_id_sum=2_001_000,
    expected_amount_sum=1_199_000,
    expected_order_items=4000,
    expected_item_id_sum=8_002_000,
    expected_payments=2000,
    expected_payment_id_sum=2_001_000,
    expected_source_orders=2000,
    expected_source_order_id_sum=2_001_000,
    expected_source_order_items=4000,
    expected_source_payments=2000,
    target_runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=3,
        tidb_count=1,
        sql_timeout_seconds=180,
        tikv_memory_mb=2048,
        tidb_memory_mb=1024,
        bootstrap_cache_enabled=False,
        readiness_timeout_seconds=1800,
    ),
    br_image="docker.m.daocloud.io/pingcap/br:v8.1.0",
    minio_image="docker.m.daocloud.io/minio/minio:RELEASE.2024-06-13T22-53-53Z",
    mc_image="docker.m.daocloud.io/minio/mc:latest",
)

_SINGLE_INTERRUPTION_CASE = replace(
    _CASE,
    case_id="resume_single_interruption_pitr_checkpoint",
    case_no=1,
    evaluator=TidbBusinessChangePitrCheckpointRecoverySingleInterruptionEvaluatorCase,
    title="Resume one isolated PITR interruption while preserving the backup chain.",
    background_workload=replace(_CASE.background_workload, worker_count=3),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.5,
        reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
        protocol_version='difficulty-v2',
    ),
)


class TidbBusinessChangePitrCheckpointRecoveryInjector(BaseFaultInjector):

    retain_workload_after_metric_history = True

    def settle_after_history_capture(self, context: FaultLifecycleContext) -> None:
        """Keep the fault state active through the Agent phase."""
    def __init__(self):
        self.env = None
        self.case = None
        self.context_run_id = None
        self.source_network = None
        self.target_deployment = None
        self._retired_target_deployments = []
        self.target_network = None
        self.target_host = "127.0.0.1"
        self.target_port = None
        self.minio_container = None
        self.log_container = None
        self.restore_container = None
        self.minio_running = False
        self.log_started = False
        self.restore_started = False
        self._observed_attempts: set[str] = set()
        self._schema_audit_surfaces: set[str] = set()
        self._table_identity_audit_surfaces: set[str] = set()
        self._attempt_output: dict[str, str] = {}
        self._checkpoint_table_id_maps: dict[int, dict[str, int]] = {}
        self._checkpoint_abandoned = False
        self._snapshot_output = ""
        self._attempt_counter = 1
        self.snapshot_storage = None
        self.log_storage = None
        self.checkpoint_storage_root = None
        self.checkpoint_storage_suffix = None
        self.checkpoint_storage = None
        self.checkpoint_prefix = None
        self._checkpoint_object_cache: dict[int, list[str]] = {}
        self.upstream_cluster_id = None
        self.target_cluster_id = None
        self.snapshot_backup_ts = None
        self.log_start_ts = None
        self.target_tso = None

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self._create_source_schema()
        self._start_target_cluster()
        self._start_minio()
        self._start_log_backup()
        self._run_snapshot_backup()
        self._write_log_markers()
        self._run_failed_restore()
        self._create_control_plane()
        self._register_runtime()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context)
        self._ensure_minio()
        if self.target_deployment is None:
            raise RuntimeError(f"K08 target deployment is missing during activate: run_id={context.run_id!r}")
        if not self.target_deployment.is_ready():
            self.target_deployment.wait_for_ready(300)
        self._register_runtime()
        self._verify_failed_state()

    def prepare_observability(self, context: FaultLifecycleContext) -> dict[str, object]:
        self._verify_failed_state()
        source_truth = self._source_rows(
            f"SELECT "
            f"(SELECT COUNT(*) FROM {self.case.business_database}.{self.case.orders_table}), "
            f"(SELECT COALESCE(SUM(order_id), 0) FROM {self.case.business_database}.{self.case.orders_table}), "
            f"(SELECT COALESCE(SUM(amount_cents), 0) FROM {self.case.business_database}.{self.case.orders_table}), "
            f"(SELECT COUNT(*) FROM {self.case.business_database}.{self.case.order_items_table}), "
            f"(SELECT COALESCE(SUM(item_id), 0) FROM {self.case.business_database}.{self.case.order_items_table}), "
            f"(SELECT COUNT(*) FROM {self.case.business_database}.{self.case.payments_table}), "
            f"(SELECT COALESCE(SUM(payment_id), 0) FROM {self.case.business_database}.{self.case.payments_table}), "
            f"(SELECT COUNT(*) FROM {self.case.business_database}.{self.case.marker_table} "
            f"WHERE marker = {sql_literal(self.case.post_target_marker)})"
        )
        if len(source_truth) != 1 or len(source_truth[0]) != 8:
            raise RuntimeError(f"K08 source truth must have one eight-column row: rows={source_truth!r}")
        objects = self._source_rows(
            f"SELECT object_id, storage_prefix, object_status, checksum_status, protected "
            f"FROM {self.case.control_database}.{self.case.object_table} ORDER BY object_id"
        )
        return {
            "k08_runtime": {
                "upstream_cluster_id": self.upstream_cluster_id,
                "target_cluster_id": self.target_cluster_id,
                "snapshot_backup_ts": self.snapshot_backup_ts,
                "log_start_ts": self.log_start_ts,
                "start_ts": self.snapshot_backup_ts,
                "restored_ts": self.target_tso,
                "requested_target_ts": self.target_tso,
            },
            "k08_target_truth": tuple(source_truth[0][:7]),
            "k08_source_truth": tuple(source_truth[0][0:2] + source_truth[0][3:4] + source_truth[0][5:6] + source_truth[0][7:8]),
            "k08_backup_objects": objects,
            "k08_reference_unit_counts": {
                "knowledge_chunks": {"causal": 7, "noise": 8},
                "backup_restore_rows": {"causal": 8, "noise": 12},
                "sql_rows": {"causal": 6, "noise": 10},
                "component_log_lines": {"causal": 3, "noise": 6},
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_restore_container()
        self._stop_log_backup()
        if self.target_deployment is not None:
            for target in self.target_deployment.COMPONENTS["tikv"]:
                component = f"tikv/{target}"
                states = self.target_deployment.node_states()
                if states[component]["running"]:
                    self.target_deployment.stop_component(component)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._stop_restore_container()
        self._stop_log_backup()
        if self.restore_started:
            self._docker(["rm", "--force", self.restore_container], "remove K08 restore controller")
        self.restore_started = False
        self.restore_container = None
        if self.target_deployment is not None:
            self._detach_minio(self.target_deployment)
            self.target_deployment.teardown()
            self.target_deployment = None
        for deployment in self._retired_target_deployments:
            self._detach_minio(deployment)
            deployment.teardown()
        self._retired_target_deployments.clear()
        if self.minio_running:
            self._docker(["rm", "--force", self.minio_container], "remove K08 MinIO")
        self.minio_running = False
        self.minio_container = None
        if self.env is not None:
            self.env.clear_secondary_endpoint()
            if self.env.owns_k08_pitr_runtime(self):
                self.env.clear_k08_pitr_runtime()
        self._drop_source_schema()

    def restore_operation(self, operation: str, target: str | None, parameters: dict[str, object]) -> dict[str, object]:
        if operation == "list":
            if target is not None or parameters:
                raise ValueError("K08 restore list accepts no target or parameters")
            return {"attempts": self._attempt_rows()}
        if operation == "get":
            if target is None or parameters:
                raise ValueError("K08 restore get requires only an attempt target")
            self._require_attempt(target)
            self._observed_attempts.add(target)
            return {
                "attempt": self._attempt_payload(target),
                "target": self._target_observation(),
            }
        if operation == "resume":
            if target is None or parameters:
                raise ValueError("K08 restore resume requires only an attempt target")
            self._resume(target)
            return {
                "attempt": self._attempt_payload(target),
                "target": self._target_observation(),
            }
        if operation == "abandon":
            if target is None or parameters:
                raise ValueError("K08 restore abandon requires only an attempt target")
            self._abandon(target)
            return {
                "attempt": self._attempt_payload(target),
                "target": self._target_observation(),
            }
        if operation == "restart":
            if target is None or parameters:
                raise ValueError("K08 restore restart requires only the failed attempt target")
            self._restart(target)
            return {
                "attempts": self._attempt_rows(),
                "target": self._target_observation(),
            }
        if operation == "wait":
            if parameters:
                raise ValueError(f"K08 restore wait accepts no parameters: parameters={parameters!r}")
            if target is not None:
                self._require_attempt(target)
            return self._wait_restore(target, 120)
        raise ValueError(f"Unsupported K08 restore operation: operation={operation!r}")

    def observe_agent_sql(self, target: str, sql_query: str) -> None:
        normalized = sql_query.replace("`", "").casefold()
        if target not in {"primary", "replica"}:
            return
        if any(re.search(rf"\b{keyword}\b", normalized) for keyword in (
            "alter", "drop", "insert", "update", "delete", "replace", "merge", "call", "grant", "revoke",
        )):
            return
        table_ref = f"{self.case.business_database}.{self.case.operator_touch_target_table}".casefold()
        table_scope = (
            table_ref in normalized
            or (
                re.search(rf"\b{re.escape(self.case.business_database.casefold())}\b", normalized)
                and re.search(rf"\b{re.escape(self.case.operator_touch_target_table.casefold())}\b", normalized)
            )
        )
        catalog_read = (
            "information_schema.statistics" in normalized
            or "information_schema.columns" in normalized
            or "information_schema.tables" in normalized
            or re.search(r"\bshow\s+(?:index|keys)\b", normalized) is not None
            or re.search(r"\bshow\s+create\s+table\b", normalized) is not None
            or re.search(r"\bshow\s+table\s+status\b", normalized) is not None
        )
        table_identity_read = (
            "information_schema.tables" in normalized
            and "tidb_table_id" in normalized
        )
        if catalog_read and table_scope:
            self._schema_audit_surfaces.add(target)
        if table_identity_read and table_scope:
            self._table_identity_audit_surfaces.add(target)

    def _configure(self, context: FaultLifecycleContext) -> None:
        self.env = context.env
        self.case = context.case
        self.context_run_id = context.run_id
        self.source_network = context.env.deployment.network_name
        # Reserve a distinct port block for the isolated target cluster.
        self.target_port = context.env.port + 1000
        self.minio_container = self.minio_container or (
            f"aiopsbench-k08-minio-{hashlib.sha256(context.run_id.encode()).hexdigest()[:12]}"
        )

    def _create_source_schema(self) -> None:
        case = self.case
        statements = (
            f"CREATE DATABASE IF NOT EXISTS {case.business_database}",
            f"CREATE DATABASE IF NOT EXISTS {case.control_database}",
            f"DROP TABLE IF EXISTS {case.business_database}.{case.orders_table}",
            f"DROP TABLE IF EXISTS {case.business_database}.{case.order_items_table}",
            f"DROP TABLE IF EXISTS {case.business_database}.{case.payments_table}",
            f"DROP TABLE IF EXISTS {case.business_database}.{case.marker_table}",
            f"CREATE TABLE {case.business_database}.{case.orders_table} (order_id BIGINT PRIMARY KEY, amount_cents BIGINT NOT NULL, order_status VARCHAR(24) NOT NULL)",
            f"CREATE TABLE {case.business_database}.{case.order_items_table} (item_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, quantity INT NOT NULL)",
            f"CREATE TABLE {case.business_database}.{case.payments_table} (payment_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, amount_cents BIGINT NOT NULL)",
            f"CREATE TABLE {case.business_database}.{case.marker_table} (marker VARCHAR(64) PRIMARY KEY, committed_tso BIGINT NOT NULL, payload VARCHAR(128) NOT NULL)",
        )
        for statement in statements:
            require_sql_success(self.env.execute_internal_sql(statement), f"K08 source SQL: {statement}")
        order_rows = [
            f"({index}, {100 + index % 1000}, 'created')"
            for index in range(1, case.expected_orders + 1)
        ]
        item_rows = [
            f"({index}, {1 + (index - 1) % case.expected_orders}, {1 + index % 4})"
            for index in range(1, case.expected_order_items + 1)
        ]
        payment_rows = [
            f"({index}, {index}, {100 + index % 1000})"
            for index in range(1, case.expected_payments + 1)
        ]
        run_sql_batches(
            self.env.execute_internal_sql,
            f"INSERT INTO {case.business_database}.{case.orders_table} (order_id, amount_cents, order_status) VALUES ",
            order_rows,
            250,
            "K08 source orders",
        )
        run_sql_batches(
            self.env.execute_internal_sql,
            f"INSERT INTO {case.business_database}.{case.order_items_table} (item_id, order_id, quantity) VALUES ",
            item_rows,
            250,
            "K08 source order items",
        )
        run_sql_batches(
            self.env.execute_internal_sql,
            f"INSERT INTO {case.business_database}.{case.payments_table} (payment_id, order_id, amount_cents) VALUES ",
            payment_rows,
            250,
            "K08 source payments",
        )
        require_sql_success(
            self.env.execute_internal_sql(
                f"INSERT INTO {case.business_database}.{case.marker_table} (marker, committed_tso, payload) "
                f"VALUES ('snapshot-baseline', {self.env.current_tso()}, 'snapshot baseline')"
            ),
            "K08 snapshot marker",
        )

    def _start_target_cluster(self) -> None:
        target_run_id = f"{self.context_run_id}-k08-target"
        self.target_deployment = self.env.deployment.__class__(
            run_id=target_run_id,
            port_base=self.target_port,
        )
        self.target_deployment.configure_runtime(self.case.target_runtime)
        self.target_deployment.deploy()
        self._wait_for(
            lambda: self.target_deployment.is_ready(),
            300,
            "K08 initial target deployment readiness",
        )
        self.target_network = self.target_deployment.network_name
        self.target_host, self.target_port = self.target_deployment.primary_tidb_endpoint
        self.target_cluster_id = self._cluster_id(self.target_deployment)
        self.env.configure_secondary_endpoint(self.target_host, self.target_port, "")

    def _start_minio(self) -> None:
        case = self.case
        self._docker([
            "run", "--detach", "--name", self.minio_container, "--network", self.source_network,
            "-e", "MINIO_ROOT_USER=k08", "-e", "MINIO_ROOT_PASSWORD=k08-secret",
            case.minio_image, "server", "/data", "--address", ":9000",
        ], "start K08 MinIO")
        self.minio_running = True
        self._wait_for(lambda: self._mc(("ls", "minio")).returncode == 0, 120, "K08 MinIO readiness")
        result = self._mc(("mb", "--ignore-existing", "minio/k08"))
        if result.returncode != 0:
            raise _K08CommandError(
                "K08 MinIO bucket creation failed: bucket='k08', "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        self._docker(["network", "connect", self.target_network, self.minio_container], "connect MinIO to K08 target network")
        prefix = f"pitr/{self.context_run_id}"
        self.checkpoint_prefix = f"k08/checkpoints/{self.context_run_id}"
        suffix = "?access-key=k08&secret-access-key=k08-secret&endpoint=http://%s:9000&force-path-style=true" % self.minio_container
        self.snapshot_storage = f"s3://k08/{prefix}/snapshot{suffix}"
        self.log_storage = f"s3://k08/{prefix}/log{suffix}"
        self.checkpoint_storage_root = f"s3://k08/{prefix}/log/checkpoints"
        self.checkpoint_storage_suffix = suffix
        self.checkpoint_storage = self._checkpoint_storage_for(self.target_cluster_id)

    def _run_snapshot_backup(self) -> None:
        output = self._run_br(
            self.source_network,
            ["backup", "full", "--pd=pd-0:2379", f"--storage={self.snapshot_storage}", "--log-file="],
            "K08 snapshot backup",
        )
        self._snapshot_output = output
        match = re.search(r"BackupTS=(\d+)", output)
        if match is None:
            raise _K08CommandError(f"K08 snapshot backup output has no BackupTS: output={output!r}")
        self.snapshot_backup_ts = int(match.group(1))
        self.upstream_cluster_id = self._cluster_id(self.env.deployment)

    def _start_log_backup(self) -> None:
        self.log_container = self._container_name("log", self._attempt_counter)
        self._docker([
            "run", "--detach", "--name", self.log_container, "--network", self.source_network,
            "--entrypoint", "/br", self.case.br_image,
            "log", "start", "--task-name=k08-pitr", "--pd=pd-0:2379",
            f"--storage={self.log_storage}", "--log-file=",
        ], "start K08 log backup")
        self.log_started = True
        self.log_start_ts = self.env.current_tso()
        self._wait_for(
            lambda: self._run_br(self.source_network, ["log", "status", "--task-name=k08-pitr", "--pd=pd-0:2379"], "K08 log status probe", allow_failure=True).find("NORMAL") >= 0,
            180,
            "K08 log backup normal state",
        )

    def _write_log_markers(self) -> None:
        case = self.case
        for marker in ("phase-a", case.target_marker):
            tso = self.env.current_tso()
            require_sql_success(
                self.env.execute_internal_sql(
                    f"INSERT INTO {case.business_database}.{case.marker_table} (marker, committed_tso, payload) "
                    f"VALUES ({sql_literal(marker)}, {tso}, {sql_literal('live log marker ' + marker)})"
                ),
                f"K08 log marker {marker}",
            )
            if marker == case.target_marker:
                self.target_tso = self.env.current_tso()
        if self.target_tso is None:
            raise RuntimeError("K08 target marker did not produce a target TSO")
        require_sql_success(
            self.env.execute_internal_sql(
                f"INSERT INTO {case.business_database}.{case.marker_table} (marker, committed_tso, payload) "
                f"VALUES ({sql_literal(case.post_target_marker)}, {self.env.current_tso()}, 'must not appear in target')"
            ),
            "K08 post-target marker",
        )
        self._wait_for_log_checkpoint(180)

    def _wait_for_log_checkpoint(self, timeout: int) -> None:
        target_physical_ms = int(self.target_tso) >> 18

        def checkpoint_reached() -> bool:
            output = self._run_br(
                self.source_network,
                ["log", "status", "--task-name=k08-pitr", "--pd=pd-0:2379"],
                "K08 log checkpoint status probe",
            )
            if "NORMAL" not in output:
                raise _K08CommandError(
                    "K08 log backup is not NORMAL while waiting for requested target: "
                    f"target_tso={self.target_tso}, output_tail={output[-4000:]!r}"
                )
            match = re.search(
                r"checkpoint\[global\]:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)? [+-]\d{4})\s*;",
                output,
            )
            if match is None:
                raise _K08CommandError(
                    "K08 log status has no documented checkpoint[global] field: "
                    f"target_tso={self.target_tso}, output_tail={output[-4000:]!r}"
                )
            checkpoint_text = match.group(1)
            checkpoint_format = (
                "%Y-%m-%d %H:%M:%S.%f %z"
                if "." in checkpoint_text
                else "%Y-%m-%d %H:%M:%S %z"
            )
            checkpoint_ms = int(datetime.strptime(checkpoint_text, checkpoint_format).timestamp() * 1000)
            return checkpoint_ms >= target_physical_ms

        self._wait_for(checkpoint_reached, timeout, "K08 log backup checkpoint coverage")

    def _run_failed_restore(self) -> None:
        self.restore_container = self._container_name("restore", self._attempt_counter)
        checkpoint_watcher = self._start_checkpoint_watcher()
        try:
            self._docker([
                "run", "--detach", "--name", self.restore_container, "--network", self.target_network,
                "--entrypoint", "/br", self.case.br_image,
                "restore", "point", "--pd=pd-0:2379", f"--storage={self.log_storage}",
                f"--full-backup-storage={self.snapshot_storage}",
                f"--restored-ts={self.target_tso}", "--log-file=",
            ], "start K08 interrupted PITR")
            self.restore_started = True
            self._wait_for_restore_checkpoint(300, checkpoint_watcher)
        finally:
            if checkpoint_watcher.poll() is None:
                checkpoint_watcher.kill()
            checkpoint_watcher.wait()
        output = self._wait_container(self.restore_container, 300)
        self._attempt_output[self.case.selected_attempt_id] = output
        if not self._target_has_checkpoint():
            raise RuntimeError("K08 injected failure lost the target log checkpoint")
        self._wait_for(
            self._partial_target_schema_is_ready,
            300,
            "K08 partial target business schema restoration",
        )
        self._capture_checkpoint_table_id_map()
        self._touch_partial_target()

    def _create_control_plane(self) -> None:
        case = self.case
        statements = (
            f"DROP TABLE IF EXISTS {case.control_database}.{case.attempt_table}",
            f"DROP TABLE IF EXISTS {case.control_database}.{case.backup_table}",
            f"DROP TABLE IF EXISTS {case.control_database}.{case.object_table}",
            f"CREATE TABLE {case.control_database}.{case.attempt_table} ("
            "request_id VARCHAR(96), attempt_id VARCHAR(128) PRIMARY KEY, phase VARCHAR(32), status VARCHAR(32), "
            "upstream_cluster_id BIGINT, target_cluster_id BIGINT, start_ts BIGINT, restored_ts BIGINT, "
            "requested_target_ts BIGINT, checkpoint_status VARCHAR(32), log_continuity VARCHAR(32), error_text VARCHAR(512))",
            f"CREATE TABLE {case.control_database}.{case.backup_table} ("
            "request_id VARCHAR(96) PRIMARY KEY, snapshot_status VARCHAR(32), log_status VARCHAR(32), "
            "snapshot_backup_ts BIGINT, log_start_ts BIGINT, log_checkpoint_ts BIGINT, requested_target_ts BIGINT, "
            "continuity_status VARCHAR(32), object_hash_status VARCHAR(32), upstream_cluster_id BIGINT, "
            "target_cluster_id BIGINT, release_version VARCHAR(32), retention_start_ts BIGINT, "
            "retention_end_ts BIGINT, segment_count INT)",
            f"CREATE TABLE {case.control_database}.{case.object_table} ("
            "object_id BIGINT PRIMARY KEY, storage_prefix VARCHAR(1024), object_status VARCHAR(32), "
            "checksum_status VARCHAR(32), protected TINYINT)",
        )
        for statement in statements:
            require_sql_success(self.env.execute_internal_sql(statement), f"K08 control SQL: {statement}")
        values = (
            sql_literal(case.request_id),
            sql_literal(case.selected_attempt_id),
            sql_literal("UNKNOWN"),
            sql_literal("FAILED"),
            str(self.upstream_cluster_id),
            str(self.target_cluster_id),
            str(self.snapshot_backup_ts),
            str(self.target_tso),
            str(self.target_tso),
            sql_literal("PERSISTED"),
            sql_literal("UNVERIFIED"),
            sql_literal("restore controller exited unexpectedly"),
        )
        require_sql_success(
            self.env.execute_internal_sql(
                f"INSERT INTO {case.control_database}.{case.attempt_table} "
                "(request_id, attempt_id, phase, status, upstream_cluster_id, target_cluster_id, start_ts, restored_ts, requested_target_ts, checkpoint_status, log_continuity, error_text) "
                f"VALUES ({', '.join(values)})"
            ),
            "K08 failed attempt record",
        )
        require_sql_success(
            self.env.execute_internal_sql(
                f"INSERT INTO {case.control_database}.{case.attempt_table} VALUES "
                f"({sql_literal(case.request_id)}, {sql_literal(case.selected_attempt_id + '-history')}, 'SNAPSHOT_RESTORE', 'ABANDONED', "
                f"{self.upstream_cluster_id}, {self.target_cluster_id + 100}, {self.snapshot_backup_ts - 2000}, {self.snapshot_backup_ts - 1500}, {self.snapshot_backup_ts - 1500}, 'COMPLETE', 'CONTIGUOUS', 'historical attempt for the same request')"
            ),
            "K08 historical restore attempt record",
        )
        require_sql_success(
            self.env.execute_internal_sql(
                f"INSERT INTO {case.control_database}.{case.backup_table} "
                "(request_id, snapshot_status, log_status, snapshot_backup_ts, log_start_ts, log_checkpoint_ts, requested_target_ts, continuity_status, object_hash_status, upstream_cluster_id, target_cluster_id, release_version, retention_start_ts, retention_end_ts, segment_count) "
                f"VALUES "
                f"({sql_literal(case.request_id)}, 'COMPLETE', 'RUNNING', {self.snapshot_backup_ts}, {self.log_start_ts}, {self.target_tso}, {self.target_tso}, 'UNVERIFIED', 'UNCHANGED', {self.upstream_cluster_id}, {self.target_cluster_id}, 'v8.1.0', {self.snapshot_backup_ts}, {self.target_tso + 1000}, 3), "
                f"('k08-historical-request', 'COMPLETE', 'STOPPED', {self.snapshot_backup_ts - 2000}, {self.snapshot_backup_ts - 1800}, {self.snapshot_backup_ts - 1200}, {self.snapshot_backup_ts - 1000}, 'CONTIGUOUS', 'UNCHANGED', {self.upstream_cluster_id}, {self.target_cluster_id + 100}, 'v8.1.0', {self.snapshot_backup_ts - 2000}, {self.target_tso - 500}, 2), "
                f"('k08-gap-request', 'COMPLETE', 'FAILED', {self.snapshot_backup_ts - 1000}, {self.snapshot_backup_ts - 900}, {self.snapshot_backup_ts - 400}, {self.target_tso}, 'GAP', 'MISSING', {self.upstream_cluster_id}, {self.target_cluster_id + 200}, 'v8.1.0', {self.snapshot_backup_ts - 1000}, {self.snapshot_backup_ts - 400}, 1), "
                f"('k08-cross-version-request', 'COMPLETE', 'STOPPED', {self.snapshot_backup_ts - 3000}, {self.snapshot_backup_ts - 2900}, {self.snapshot_backup_ts - 2500}, {self.target_tso}, 'CONTIGUOUS', 'UNCHANGED', {self.upstream_cluster_id + 1}, {self.target_cluster_id + 300}, 'v7.5.0', {self.snapshot_backup_ts - 3000}, {self.target_tso}, 4), "
                f"('k08-same-upstream-retry', 'COMPLETE', 'RUNNING', {self.snapshot_backup_ts + 200}, {self.log_start_ts + 200}, {self.target_tso + 200}, {self.target_tso + 200}, 'CONTIGUOUS', 'UNCHANGED', {self.upstream_cluster_id}, {self.target_cluster_id + 400}, 'v8.1.0', {self.snapshot_backup_ts + 200}, {self.target_tso + 500}, 5), "
                f"('k08-retention-edge', 'COMPLETE', 'STOPPED', {self.snapshot_backup_ts - 5000}, {self.log_start_ts - 5000}, {self.target_tso - 100}, {self.target_tso}, 'CONTIGUOUS', 'UNCHANGED', {self.upstream_cluster_id}, {self.target_cluster_id + 500}, 'v8.1.0', {self.snapshot_backup_ts - 5000}, {self.target_tso - 50}, 1), "
                f"('k08-same-target-old-window', 'COMPLETE', 'STOPPED', {self.snapshot_backup_ts - 4000}, {self.log_start_ts - 4000}, {self.target_tso - 1200}, {self.target_tso - 1000}, 'CONTIGUOUS', 'UNCHANGED', {self.upstream_cluster_id}, {self.target_cluster_id}, 'v8.1.0', {self.snapshot_backup_ts - 4000}, {self.target_tso - 900}, 2)"
            ),
            "K08 backup request record",
        )
        require_sql_success(
            self.env.execute_internal_sql(
                f"INSERT INTO {case.control_database}.{case.object_table} VALUES "
                f"(1, {sql_literal(self.snapshot_storage)}, 'AVAILABLE', 'UNCHANGED', 1), "
                f"(2, {sql_literal(self.log_storage)}, 'AVAILABLE', 'UNCHANGED', 1), "
                f"(3, {sql_literal('s3://k08/' + self.checkpoint_prefix + '/same-upstream-old-attempt')}, 'CANDIDATE', 'UNSELECTED', 1), "
                f"(4, {sql_literal('s3://k08/' + self.checkpoint_prefix + '/cross-version')}, 'CANDIDATE', 'UNSELECTED', 1), "
                f"(5, {sql_literal('s3://k08/' + self.checkpoint_prefix + '/same-upstream-retry')}, 'CANDIDATE', 'UNSELECTED', 1), "
                f"(6, {sql_literal('s3://k08/' + self.checkpoint_prefix + '/retention-edge')}, 'CANDIDATE', 'UNSELECTED', 1), "
                f"(7, {sql_literal('s3://k08/' + self.checkpoint_prefix + '/same-target-old-window')}, 'CANDIDATE', 'UNSELECTED', 1), "
                f"(8, {sql_literal('s3://k08/' + self.checkpoint_prefix + '/stale-log-prefix')}, 'CANDIDATE', 'UNSELECTED', 1)"
            ),
            "K08 backup object inventory",
        )

    def _register_runtime(self) -> None:
        if not self.env.owns_k08_pitr_runtime(self):
            self.env.configure_k08_pitr_runtime(self)

    def _verify_failed_state(self) -> None:
        rows = self._attempt_rows(self.case.selected_attempt_id)
        checkpoint_present = self._target_has_checkpoint()
        partial_target_modified = self._partial_target_is_modified()
        if (
            len(rows) != 1
            or rows[0][1] != "FAILED"
            or not checkpoint_present
            or not partial_target_modified
        ):
            raise RuntimeError(
                "K08 failed checkpoint state is not reproducible: "
                f"rows={rows!r}, checkpoint_present={checkpoint_present}, "
                f"partial_target_modified={partial_target_modified}"
            )

    def _resume(self, attempt_id: str) -> None:
        self._require_attempt(attempt_id)
        if attempt_id not in self._observed_attempts:
            raise ValueError(f"K08 restore resume requires restore/get first: attempt_id={attempt_id!r}")
        expected = {
            "upstream_cluster_id": int(self.upstream_cluster_id),
            "start_ts": int(self.snapshot_backup_ts),
            "restored_ts": int(self.target_tso),
            "requested_target_ts": int(self.target_tso),
            "target_cluster_id": int(self.target_cluster_id),
        }
        row = self._attempt_rows(attempt_id)[0]
        actual = {
            "upstream_cluster_id": int(row[3]),
            "start_ts": int(row[5]),
            "restored_ts": int(row[6]),
            "requested_target_ts": int(row[7]),
            "target_cluster_id": int(row[4]),
        }
        if actual != expected:
            raise ValueError(f"K08 resume identity/time binding mismatch: attempt_id={attempt_id!r}, expected={expected!r}, actual={actual!r}")
        if self._partial_target_is_modified():
            raise ValueError(
                "K08 exact resume rejected because the current target/checkpoint state did not satisfy resume "
                f"preconditions: target_cluster_id={self.target_cluster_id}, requested_target_ts={self.target_tso}; "
                "no target state was modified"
            )
        self._run_restore_foreground(attempt_id, self.target_network, self.target_deployment)

    def _restart(self, attempt_id: str) -> None:
        self._require_attempt(attempt_id)
        if attempt_id not in self._observed_attempts:
            raise ValueError(f"K08 clean restart requires restore/get first: attempt_id={attempt_id!r}")
        row = self._attempt_rows(attempt_id)[0]
        if int(row[4]) != int(self.target_cluster_id) or int(row[7]) != int(self.target_tso):
            raise ValueError(
                "K08 clean restart identity/time binding mismatch: "
                f"attempt_id={attempt_id!r}, expected_target_cluster_id={self.target_cluster_id!r}, "
                f"actual_target_cluster_id={row[4]!r}, expected_requested_target_ts={self.target_tso!r}, "
                f"actual_requested_target_ts={row[7]!r}"
            )
        if self.checkpoint_storage_root is None:
            raise RuntimeError(
                "K08 clean restart cannot validate the checkpoint scope because the current log-backup root is missing: "
                f"attempt_id={attempt_id!r}"
            )
        if not self._checkpoint_abandoned:
            raise ValueError(
                "K08 clean restart is blocked because the incompatible partial checkpoint was not explicitly "
                "abandoned; no new target was created"
            )
        old_target = self.target_cluster_id
        old_deployment = self.target_deployment
        clean_deployment = self.env.deployment.__class__(
            run_id=f"{self.context_run_id}-k08-clean",
            port_base=self.target_port + 20,
        )
        try:
            clean_deployment.configure_runtime(self.case.target_runtime)
            clean_deployment.deploy()
            self._wait_for(
                lambda: clean_deployment.is_ready(),
                300,
                "K08 clean target deployment readiness",
            )
            clean_network = clean_deployment.network_name
            clean_host, clean_port = clean_deployment.primary_tidb_endpoint
            clean_cluster_id = self._cluster_id(clean_deployment)
            if old_target == clean_cluster_id:
                raise RuntimeError(
                    f"K08 clean restart did not create a new target cluster: cluster_id={old_target}"
                )
            self._docker(
                ["network", "connect", clean_network, self.minio_container],
                "connect MinIO to clean K08 target network",
            )
        except Exception as error:
            try:
                clean_deployment.teardown()
            except Exception as cleanup_error:
                error.add_note(
                    "K08 clean target preflight cleanup failed: "
                    f"run_id={self.context_run_id!r}, cleanup_error={cleanup_error!r}"
                )
            raise

        self.env.configure_secondary_endpoint(clean_host, clean_port, "")
        self._retired_target_deployments.append(old_deployment)
        self.target_deployment = clean_deployment
        self.target_network = clean_network
        self.target_host = clean_host
        self.target_port = clean_port
        self.target_cluster_id = clean_cluster_id
        self.checkpoint_storage = self._checkpoint_storage_for(clean_cluster_id)
        clean_attempt = f"{attempt_id}-clean-001"
        self._run_restore_foreground(clean_attempt, self.target_network, self.target_deployment)
        require_sql_success(
            self.env.execute_internal_sql(
                f"UPDATE {self.case.control_database}.{self.case.attempt_table} SET phase='LOG_RESTORE', status='ABANDONED', log_continuity='CONTIGUOUS', error_text={sql_literal('superseded by explicit isolated clean restart')} WHERE attempt_id={sql_literal(attempt_id)}"
            ),
            "K08 mark old target abandoned",
        )

    def _abandon(self, attempt_id: str) -> None:
        self._require_attempt(attempt_id)
        if attempt_id not in self._observed_attempts:
            raise ValueError(f"K08 restore abandon requires restore/get first: attempt_id={attempt_id!r}")
        row = self._attempt_rows(attempt_id)[0]
        if int(row[4]) != int(self.target_cluster_id) or int(row[7]) != int(self.target_tso):
            raise ValueError(
                "K08 abandon identity/time binding mismatch: "
                f"attempt_id={attempt_id!r}, expected_target_cluster_id={self.target_cluster_id!r}, "
                f"actual_target_cluster_id={row[4]!r}, expected_requested_target_ts={self.target_tso!r}, "
                f"actual_requested_target_ts={row[7]!r}"
            )
        if not self._partial_target_is_modified():
            raise ValueError(
                "K08 abandon is not allowed because the partial target touch evidence is absent: "
                f"attempt_id={attempt_id!r}"
            )
        if not {"primary", "replica"}.issubset(self._schema_audit_surfaces):
            raise ValueError(
                "K08 abandon requires a successful source/partial-target compatibility audit before checkpoint "
                f"abandonment: observed_surfaces={sorted(self._schema_audit_surfaces)!r}, "
                "read the same business table catalog on primary and replica"
            )
        if "replica" not in self._table_identity_audit_surfaces:
            raise ValueError(
                "K08 abandon precondition failed because the required checkpoint/partial-target compatibility "
                "evidence was not observed: "
                f"attempt_id={attempt_id!r}, observed_schema_surfaces={sorted(self._schema_audit_surfaces)!r}; "
                "no state was modified; re-read the current attempt and establish the missing compatibility evidence "
                "before retrying"
            )
        self._checkpoint_abandoned = True
        require_sql_success(
            self.env.execute_internal_sql(
                f"UPDATE {self.case.control_database}.{self.case.attempt_table} "
                f"SET phase='LOG_RESTORE', status='ABANDONED', error_text={sql_literal('incompatible checkpoint explicitly abandoned')} "
                f"WHERE attempt_id={sql_literal(attempt_id)}"
            ),
            "K08 explicitly abandon incompatible checkpoint",
        )

    def _run_restore_foreground(self, attempt_id: str, network: str, deployment) -> None:
        output = self._run_br(
            network,
            ["restore", "point", "--pd=pd-0:2379", f"--storage={self.log_storage}",
             f"--full-backup-storage={self.snapshot_storage}",
             f"--restored-ts={self.target_tso}", "--log-file="],
            f"K08 PITR restore attempt={attempt_id}",
        )
        self._attempt_output[attempt_id] = output
        target_rows = self._target_rows(
            f"SELECT marker, COUNT(*) FROM {self.case.business_database}.{self.case.marker_table} "
            f"WHERE marker IN ('{self.case.target_marker}', '{self.case.post_target_marker}') GROUP BY marker ORDER BY marker"
        )
        if target_rows != [[self.case.target_marker, 1]]:
            self._record_attempt(attempt_id, "FAILED", "BUSINESS_TRUTH_MISMATCH", "CONTIGUOUS", "restore output completed but target marker boundary was not proven")
            raise _K08CommandError(f"K08 restore target truth mismatch: attempt_id={attempt_id!r}, rows={target_rows!r}")
        self._checkpoint_table_id_maps[int(self.target_cluster_id)] = self._target_table_id_map()
        self._mark_backup_chain_proven()
        self._record_attempt(attempt_id, "COMPLETED", "COMPLETE", "CONTIGUOUS", "")

    def _mark_backup_chain_proven(self) -> None:
        require_sql_success(
            self.env.execute_internal_sql(
                f"UPDATE {self.case.control_database}.{self.case.backup_table} "
                f"SET log_status='RUNNING', continuity_status='CONTIGUOUS' "
                f"WHERE request_id={sql_literal(self.case.request_id)}"
            ),
            "K08 mark backup chain proven",
        )

    def _record_attempt(self, attempt_id: str, status: str, checkpoint_status: str, continuity: str, error: str) -> None:
        case = self.case
        exists = self._source_rows(
            f"SELECT attempt_id FROM {case.control_database}.{case.attempt_table} WHERE attempt_id={sql_literal(attempt_id)}"
        )
        if exists:
            require_sql_success(
                self.env.execute_internal_sql(
                    f"UPDATE {case.control_database}.{case.attempt_table} SET phase='LOG_RESTORE', status={sql_literal(status)}, checkpoint_status={sql_literal(checkpoint_status)}, log_continuity={sql_literal(continuity)}, error_text={sql_literal(error)} WHERE attempt_id={sql_literal(attempt_id)}"
                ),
                f"K08 update attempt {attempt_id}",
            )
            return
        require_sql_success(
            self.env.execute_internal_sql(
                f"INSERT INTO {case.control_database}.{case.attempt_table} VALUES ({sql_literal(case.request_id)}, {sql_literal(attempt_id)}, 'LOG_RESTORE', {sql_literal(status)}, {self.upstream_cluster_id}, {self.target_cluster_id}, {self.snapshot_backup_ts}, {self.target_tso}, {self.target_tso}, {sql_literal(checkpoint_status)}, {sql_literal(continuity)}, {sql_literal(error)})"
            ),
            f"K08 insert attempt {attempt_id}",
        )

    def _attempt_payload(self, attempt_id: str) -> dict[str, object]:
        rows = self._attempt_rows(attempt_id)
        if len(rows) != 1:
            raise RuntimeError(f"K08 attempt payload requires one row: attempt_id={attempt_id!r}, rows={rows!r}")
        output_tail = self._attempt_output.get(attempt_id, "")
        row = rows[0]
        checkpoint = {
            "storage": "external",
            "prefix": self._checkpoint_storage_for(int(row[4])),
            "target_cluster_id": row[4],
            "objects": self._checkpoint_objects(int(row[4])),
        }
        return {
            "row": row,
            "raw_args": {
                "upstream_cluster_id": row[3],
                "start_ts": row[5],
                "restored_ts": row[6],
                "requested_target_ts": row[7],
                "target_cluster_id": row[4],
                "full_backup_storage": self.snapshot_storage,
                "log_storage": self.log_storage,
            },
            "checkpoint": checkpoint,
            "error_output_tail": output_tail[-4000:],
        }

    def _target_observation(self) -> dict[str, object]:
        business_tables = self._target_rows(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_SCHEMA={sql_literal(self.case.business_database)} ORDER BY TABLE_NAME"
        )
        markers = []
        if [self.case.marker_table] in business_tables:
            markers = self._target_rows(
                f"SELECT marker, committed_tso FROM {self.case.business_database}.{self.case.marker_table} ORDER BY committed_tso"
            )
        return {
            "cluster_id": self.target_cluster_id,
            "endpoint": f"{self.target_host}:{self.target_port}",
            "checkpoint_storage": self.checkpoint_storage,
            "checkpoint_objects": self._checkpoint_objects(),
            "business_tables": business_tables,
            "markers": markers,
        }

    def _wait_restore(self, attempt_id: str | None, timeout: int) -> dict[str, object]:
        if self.restore_started:
            state = self._container_state(self.restore_container)
            if state == "running":
                self._wait_container(self.restore_container, timeout)
        return {
            "attempt": self._attempt_rows(attempt_id) if attempt_id else self._attempt_rows(),
            "output_tail": self._attempt_output.get(attempt_id or self.case.selected_attempt_id, "")[-4000:],
        }

    def _attempt_rows(self, attempt_id: str | None = None) -> list[list[object]]:
        where = f" WHERE request_id={sql_literal(self.case.request_id)}"
        if attempt_id is not None:
            where += f" AND attempt_id={sql_literal(attempt_id)}"
        return self._source_rows(
            f"SELECT attempt_id, status, phase, upstream_cluster_id, target_cluster_id, start_ts, restored_ts, requested_target_ts, checkpoint_status, log_continuity, error_text FROM {self.case.control_database}.{self.case.attempt_table}{where} ORDER BY attempt_id"
        )

    def _require_attempt(self, attempt_id: str) -> None:
        if len(self._attempt_rows(attempt_id)) != 1:
            raise ValueError(f"K08 restore attempt is not in current request: attempt_id={attempt_id!r}")

    def _touch_partial_target(self) -> None:
        case = self.case
        rows = self._target_rows(
            f"SELECT order_id, amount_cents, order_status "
            f"FROM {case.business_database}.{case.operator_touch_target_table} ORDER BY order_id"
        )
        if len(rows) != case.expected_orders:
            raise RuntimeError(
                "K08 partial target recreation requires the restored order table row count before the external change: "
                f"expected={case.expected_orders}, actual={len(rows)}"
            )
        conn = pymysql.connect(
            host=self.target_host,
            port=self.target_port,
            user="root",
            password="",
            autocommit=True,
            connect_timeout=5,
            read_timeout=180,
            write_timeout=180,
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"DROP TABLE {case.business_database}.{case.operator_touch_target_table}"
                )
                cursor.execute(
                    f"CREATE TABLE {case.business_database}.{case.operator_touch_target_table} "
                    "(order_id BIGINT PRIMARY KEY, amount_cents BIGINT NOT NULL, "
                    "order_status VARCHAR(24) NOT NULL)"
                )
                cursor.executemany(
                    f"INSERT INTO {case.business_database}.{case.operator_touch_target_table} "
                    "(order_id, amount_cents, order_status) VALUES (%s, %s, %s)",
                    rows,
                )
        finally:
            conn.close()

    def _partial_target_schema_is_ready(self) -> bool:
        case = self.case
        expected = [[table] for table in sorted((
            case.orders_table,
            case.order_items_table,
            case.payments_table,
            case.marker_table,
        ))]
        rows = self._target_rows(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_SCHEMA={sql_literal(case.business_database)} "
            f"AND TABLE_NAME IN ({', '.join(sql_literal(table) for table in (case.orders_table, case.order_items_table, case.payments_table, case.marker_table))}) "
            "ORDER BY TABLE_NAME"
        )
        return rows == expected

    def _partial_target_is_modified(self) -> bool:
        target_cluster_id = int(self.target_cluster_id)
        expected = self._checkpoint_table_id_maps.get(target_cluster_id)
        if expected is None:
            raise RuntimeError(
                "K08 partial target identity baseline is missing: "
                f"target_cluster_id={target_cluster_id}, known_targets={sorted(self._checkpoint_table_id_maps)}"
            )
        return self._target_table_id_map() != expected

    def _capture_checkpoint_table_id_map(self) -> None:
        target_cluster_id = int(self.target_cluster_id)
        self._checkpoint_table_id_maps[target_cluster_id] = self._target_table_id_map()

    def _target_table_id_map(self) -> dict[str, int]:
        rows = self._target_rows(
            "SELECT TABLE_NAME, TIDB_TABLE_ID FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_SCHEMA={sql_literal(self.case.business_database)} "
            f"AND TABLE_NAME={sql_literal(self.case.operator_touch_target_table)}"
        )
        if len(rows) != 1 or len(rows[0]) != 2:
            raise RuntimeError(
                "K08 target table identity query must return one TABLE_NAME/TIDB_TABLE_ID row: "
                f"table={self.case.operator_touch_target_table!r}, rows={rows!r}"
            )
        return {str(rows[0][0]): int(rows[0][1])}

    def _target_has_checkpoint(self) -> bool:
        return bool(self._checkpoint_objects())

    def _checkpoint_storage_for(self, target_cluster_id: int) -> str:
        if self.checkpoint_storage_root is None or self.checkpoint_storage_suffix is None:
            raise RuntimeError(
                "K08 checkpoint storage identity is unavailable: "
                f"root={self.checkpoint_storage_root!r}, suffix={self.checkpoint_storage_suffix!r}, target_cluster_id={target_cluster_id!r}"
            )
        return f"{self.checkpoint_storage_root}/restore-{int(target_cluster_id)}{self.checkpoint_storage_suffix}"

    def _checkpoint_objects(self, target_cluster_id: int | None = None) -> list[str]:
        target_cluster_id = int(self.target_cluster_id if target_cluster_id is None else target_cluster_id)
        if target_cluster_id in self._checkpoint_object_cache:
            return self._checkpoint_object_cache[target_cluster_id]
        result = self._mc(("ls", "--recursive", self._checkpoint_root(target_cluster_id)))
        if result.returncode != 0:
            output = f"{result.stdout}\n{result.stderr}".casefold()
            if "does not exist" in output:
                return []
            raise _K08CommandError(
                "K08 checkpoint storage listing failed: "
                f"root={self._checkpoint_root(target_cluster_id)!r}, returncode={result.returncode}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        objects = [line for line in result.stdout.splitlines() if line.strip()]
        self._checkpoint_object_cache[target_cluster_id] = objects
        return objects

    def _checkpoint_root(self, target_cluster_id: int | None = None) -> str:
        target_cluster_id = int(self.target_cluster_id if target_cluster_id is None else target_cluster_id)
        return f"minio/k08/pitr/{self.context_run_id}/log/checkpoints/restore-{target_cluster_id}"

    def _start_checkpoint_watcher(self):
        script = (
            f"mc alias set minio http://{self.minio_container}:9000 k08 k08-secret >/dev/null && "
            f"mc watch --json --recursive {self._checkpoint_root()}"
        )
        return subprocess.Popen(
            [
                "docker", "run", "--rm", "--network", self.source_network,
                "--entrypoint", "/bin/sh", self.case.mc_image, "-c", script,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
        )

    def _source_rows(self, sql: str) -> list[list[object]]:
        return json_object(self.env.execute_internal_sql(sql), f"K08 source query: {sql}")["result"]

    def _target_rows(self, sql: str) -> list[list[object]]:
        conn = pymysql.connect(host=self.target_host, port=self.target_port, user="root", password="", autocommit=True, connect_timeout=5, read_timeout=180, write_timeout=180)
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                return [list(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def _cluster_id(deployment) -> int:
        payload = deployment.pd_request("GET", "/pd/api/v1/cluster")
        value = payload["id"]
        if not isinstance(value, int) or value <= 0:
            raise RuntimeError(f"K08 PD cluster ID must be a positive integer: payload={payload!r}")
        return value

    def _ensure_minio(self) -> None:
        if self.minio_container is None:
            raise RuntimeError("K08 MinIO container identity is missing")
        state = self._container_state(self.minio_container)
        if state != "running":
            self._docker(["start", self.minio_container], "start K08 MinIO during activate")
        self._wait_for(lambda: self._mc(("ls", "minio/k08")).returncode == 0, 120, "K08 MinIO activation readiness")
        self.minio_running = True

    def _stop_restore_container(self) -> None:
        if not self.restore_started:
            return
        state = self._container_state(self.restore_container)
        if state == "running":
            self._docker(["stop", "--time", "10", self.restore_container], "stop K08 restore controller")

    def _stop_log_backup(self) -> None:
        if not self.log_started:
            return
        self._docker(["rm", "--force", self.log_container], "stop K08 log backup")
        self.log_started = False
        self.log_container = None

    def _detach_minio(self, deployment) -> None:
        if not self.minio_running:
            return
        self._docker(
            ["network", "disconnect", "--force", deployment.network_name, self.minio_container],
            f"disconnect K08 MinIO from target network={deployment.network_name!r}",
        )

    def _drop_source_schema(self) -> None:
        if self.env is None or self.case is None:
            return
        case = self.case
        for relation in (case.attempt_table, case.backup_table, case.object_table):
            require_sql_success(
                self.env.execute_internal_sql(f"DROP TABLE IF EXISTS {case.control_database}.{relation}"),
                f"drop K08 control table {relation}",
            )
        for relation in (case.orders_table, case.order_items_table, case.payments_table, case.marker_table):
            require_sql_success(
                self.env.execute_internal_sql(f"DROP TABLE IF EXISTS {case.business_database}.{relation}"),
                f"drop K08 business table {relation}",
            )
        require_sql_success(self.env.execute_internal_sql(f"DROP DATABASE IF EXISTS {case.control_database}"), "drop K08 control database")

    def _mc(
        self,
        args: tuple[str, ...],
        *,
        input_text: str | None = None,
    ):
        command = ["mc", *args]
        script = (
            f"mc alias set minio http://{self.minio_container}:9000 k08 k08-secret >/dev/null && "
            f"{shlex.join(command)}"
        )
        return subprocess.run(
            ["docker", "run", "--rm", "--network", self.source_network, "--entrypoint", "/bin/sh", self.case.mc_image, "-c", script],
            capture_output=True,
            text=True,
            input=input_text,
            timeout=300,
        )

    def _run_br(self, network: str, args: list[str], context: str, *, allow_failure: bool = False) -> str:
        completed = subprocess.run(
            ["docker", "run", "--rm", "--network", network, "--entrypoint", "/br", self.case.br_image, *args],
            capture_output=True,
            text=True,
            timeout=600,
        )
        output = completed.stdout + completed.stderr
        if completed.returncode != 0 and not allow_failure:
            raise _K08CommandError(
                f"{context} failed: returncode={completed.returncode}, output={output.strip()!r}"
            )
        return output

    def _wait_for_restore_checkpoint(self, timeout: int, checkpoint_watcher=None) -> None:
        deadline = time.monotonic() + timeout
        follower = subprocess.Popen(
            ["docker", "logs", "--follow", "--tail", "20", self.restore_container],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
        )
        selector = selectors.DefaultSelector()
        selector.register(follower.stdout, selectors.EVENT_READ, "restore-log")
        if checkpoint_watcher is not None:
            selector.register(checkpoint_watcher.stdout, selectors.EVENT_READ, "checkpoint-event")
        captured = bytearray()
        checkpoint_logged = False
        checkpoint_phase_logged = False
        checkpoint_event_logged = False
        next_checkpoint_probe = 0.0
        try:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError(
                        "K08 log restore checkpoint phase did not reach its phase gate: "
                        f"timeout_seconds={timeout}, container={self.restore_container!r}"
                    )
                for key, _ in selector.select(min(0.2, remaining)):
                    chunk = os.read(key.fd, 65536)
                    if chunk:
                        if key.data == "checkpoint-event":
                            checkpoint_event_logged = True
                        else:
                            captured.extend(chunk)
                            checkpoint_logged = b"save checkpoint task info" in captured
                            checkpoint_phase_logged = b"InLogRestoreAndIdMapPersist" in captured
                    else:
                        selector.unregister(key.fileobj)

                now = time.monotonic()
                checkpoint_present = checkpoint_event_logged
                if checkpoint_watcher is None and now >= next_checkpoint_probe:
                    checkpoint_present = self._target_has_checkpoint()
                    next_checkpoint_probe = now + 0.5

                state = self._container_state(self.restore_container)
                checkpoint_phase_ready = checkpoint_present and checkpoint_phase_logged
                if checkpoint_phase_ready:
                    if state != "running":
                        exit_code = self._container_exit_code(self.restore_container)
                        output = self._restore_logs()
                        self._attempt_output[self.case.selected_attempt_id] = output
                        raise _K08CommandError(
                            "K08 restore controller completed before the checkpoint interruption could be injected: "
                            f"container={self.restore_container!r}, state={state!r}, exit_code={exit_code}, "
                            f"checkpoint_logged={checkpoint_logged}, checkpoint_phase_logged={checkpoint_phase_logged}, "
                            f"checkpoint_event_logged={checkpoint_event_logged}, checkpoint_present={checkpoint_present}, "
                            f"output_tail={output[-4000:]!r}"
                        )
                    try:
                        self._docker(["kill", self.restore_container], "interrupt K08 restore controller")
                    except RuntimeError as exc:
                        state = self._container_state(self.restore_container)
                        output = self._restore_logs()
                        self._attempt_output[self.case.selected_attempt_id] = output
                        raise _K08CommandError(
                            "K08 restore controller exited during checkpoint interruption: "
                            f"container={self.restore_container!r}, state={state!r}, "
                            f"checkpoint_logged={checkpoint_logged}, checkpoint_phase_logged={checkpoint_phase_logged}, "
                            f"checkpoint_event_logged={checkpoint_event_logged}, checkpoint_present={checkpoint_present}, "
                            f"output_tail={output[-4000:]!r}"
                        ) from exc
                    return
                if state in {"exited", "dead"}:
                    exit_code = self._container_exit_code(self.restore_container)
                    output = self._restore_logs()
                    self._attempt_output[self.case.selected_attempt_id] = output
                    raise _K08CommandError(
                        "K08 restore controller stopped before target checkpoint: "
                        f"container={self.restore_container!r}, state={state!r}, exit_code={exit_code}, "
                        f"checkpoint_logged={checkpoint_logged}, checkpoint_phase_logged={checkpoint_phase_logged}, "
                        f"checkpoint_event_logged={checkpoint_event_logged}, checkpoint_present={checkpoint_present}, "
                        f"output_tail={output[-4000:]!r}"
                    )
                if state != "running":
                    raise RuntimeError(
                        "K08 restore controller entered an invalid checkpoint-wait state: "
                        f"container={self.restore_container!r}, state={state!r}"
                    )
                follower_exit_code = follower.poll()
                if follower_exit_code is not None:
                    raise _K08CommandError(
                        "K08 restore log follower stopped before target checkpoint: "
                        f"container={self.restore_container!r}, follower_exit_code={follower_exit_code}, "
                        f"output_tail={bytes(captured)[-4000:]!r}"
                    )
                if checkpoint_watcher is not None and checkpoint_watcher.poll() is not None and not checkpoint_event_logged:
                    raise _K08CommandError(
                        "K08 checkpoint object watcher stopped before a put event: "
                        f"watcher_exit_code={checkpoint_watcher.poll()}, "
                        f"container={self.restore_container!r}"
                    )
        finally:
            selector.close()
            if follower.poll() is None:
                follower.kill()
            follower.wait()

    def _restore_logs(self, *, tail: int | None = None) -> str:
        command = ["docker", "logs"]
        if tail is not None:
            command.extend(["--tail", str(tail)])
        command.append(self.restore_container)
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(
                "K08 restore controller logs could not be read: "
                f"container={self.restore_container!r}, returncode={result.returncode}, "
                f"stderr={result.stderr.strip()!r}"
            )
        return result.stdout + result.stderr

    def _wait_container(self, container: str, timeout: int) -> str:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            state = self._container_state(container)
            if state == "exited":
                result = subprocess.run(["docker", "logs", container], capture_output=True, text=True, timeout=120)
                if result.returncode != 0:
                    raise RuntimeError(f"K08 cannot read stopped container logs: container={container!r}, stderr={result.stderr.strip()!r}")
                return result.stdout + result.stderr
            if state != "running":
                raise RuntimeError(f"K08 restore container entered unexpected state: container={container!r}, state={state!r}")
            time.sleep(1)
        raise TimeoutError(f"K08 container did not exit within timeout: container={container!r}, timeout_seconds={timeout}")

    @staticmethod
    def _container_exit_code(container: str) -> int:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.ExitCode}}", container],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"K08 container exit-code lookup failed: container={container!r}, "
                f"stderr={result.stderr.strip()!r}"
            )
        return int(result.stdout.strip())

    def _wait_for(self, predicate, timeout: int, context: str) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(1)
        raise TimeoutError(f"{context} did not reach its phase gate: timeout_seconds={timeout}")

    def _container_state(self, container: str) -> str:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", container],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"K08 container state lookup failed: container={container!r}, stderr={result.stderr.strip()!r}")
        state = result.stdout.strip()
        if state not in {"created", "running", "paused", "restarting", "removing", "exited", "dead"}:
            raise RuntimeError(f"K08 container state is invalid: container={container!r}, state={state!r}")
        return state

    def read_log(self, target: str) -> str:
        if target == "br/snapshot":
            return self._snapshot_output
        if target == "br/log-backup":
            if self.log_container is None:
                raise RuntimeError(f"K08 log-backup container is unavailable: run_id={self.context_run_id!r}")
            result = subprocess.run(
                ["docker", "logs", "--timestamps", self.log_container],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"K08 log-backup log read failed: container={self.log_container!r}, "
                    f"stderr={result.stderr.strip()!r}"
                )
            return result.stdout + result.stderr
        if target == "br/restore":
            if self.restore_container is None:
                raise RuntimeError(f"K08 restore container is unavailable: run_id={self.context_run_id!r}")
            result = subprocess.run(
                ["docker", "logs", "--timestamps", self.restore_container],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"K08 restore log read failed: container={self.restore_container!r}, "
                    f"stderr={result.stderr.strip()!r}"
                )
            return result.stdout + result.stderr
        raise ValueError(
            f"Unsupported K08 external log target: target={target!r}, "
            "expected='br/snapshot', 'br/log-backup' or 'br/restore'"
        )

    def _container_name(self, kind: str, attempt: int) -> str:
        digest = hashlib.sha256(self.context_run_id.encode()).hexdigest()[:12]
        return f"aiopsbench-k08-{digest}-{kind}-{attempt:03d}"

    @staticmethod
    def _docker(command: list[str], context: str) -> str:
        docker_command = ["docker", *command]
        result = subprocess.run(docker_command, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            raise RuntimeError(
                f"{context} failed: command={shlex.join(docker_command)!r}, returncode={result.returncode}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        return result.stdout.strip()


class TidbBusinessChangePitrCheckpointRecoveryScenario(TiDBScenario):
    scenario_id = "tidb_business_change_pitr_checkpoint_recovery"
    description = (
        "Runs an isolated TiDB PITR restore with a real snapshot/log chain, a persisted checkpoint, "
        "a deterministic log-phase interruption, and a source-protection proof."
    )
    cases = (_CASE, _SINGLE_INTERRUPTION_CASE)

    def build_fault_plan(
        self,
        case: TidbBusinessChangePitrCheckpointRecoveryForResumeFailedPitrWithoutBreakingChainScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbBusinessChangePitrCheckpointRecoveryInjector,
                config={
                    "request_id": case.request_id,
                    "selected_attempt_id": case.selected_attempt_id,
                    "business_database": case.business_database,
                    "control_database": case.control_database,
                    "br_image": case.br_image,
                    "minio_image": case.minio_image,
                    "mc_image": case.mc_image,
                    "target_runtime": case.target_runtime,
                },
            ),
        )


__all__ = (
    "TidbBusinessChangePitrCheckpointRecoveryForResumeFailedPitrWithoutBreakingChainScenarioCase",
    "TidbBusinessChangePitrCheckpointRecoveryInjector",
    "TidbBusinessChangePitrCheckpointRecoveryScenario",
)
