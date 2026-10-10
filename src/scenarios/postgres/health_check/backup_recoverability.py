from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.health_check import (
    PgHealthCheckBackupRecoverabilityForMissingWalRecoveryGapEvaluatorCase,
    PgHealthCheckCapacityTrendForSalesEventStorageGrowthEvaluatorCase,
    PgHealthCheckConfigDriftForMemoryResizeConfigDriftEvaluatorCase,
    PgHealthCheckLongRunningTxForCheckoutPoolIdleTransactionEvaluatorCase,
    PgHealthCheckSequenceExhaustionForBillingCanaryInt4SequenceExhaustionEvaluatorCase,
    PgHealthCheckTableBloatForStoreReturnsTableIndexBloatEvaluatorCase,
    PgHealthCheckUnusedIndexesForCustomerRedundantIndexesEvaluatorCase,
    PgHealthCheckBackupRecoverabilityForSingleMissingWalGapSimpleEvaluatorCase,
    PgHealthCheckCapacityTrendForArchiveGrowthForecastSimpleEvaluatorCase,
    PgHealthCheckConfigDriftForCacheBaselineDriftSimpleEvaluatorCase,
    PgHealthCheckLongRunningTxForSingleIdleTransactionCleanupSimpleEvaluatorCase,
    PgHealthCheckSequenceExhaustionForBillingSequenceCapacityRiskSimpleEvaluatorCase,
    PgHealthCheckTableBloatForStoreReturnsBloatSimpleEvaluatorCase,
    PgHealthCheckUnusedIndexesForCustomerUnusedIndexSimpleEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from ...base import (
    DifficultyCalibration,
    PostgresCaseRuntime,
    PostgresScenario,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    CaseResourceSpec,
    PostgresScenarioCase,
)


POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)

CONFIG_DRIFT_POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=65536,
    container_cpu_limit=1.0,
    container_memory_mb=65536,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckBackupRecoverabilityCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    drill_batch_id: str
    recovery_window_label: str
    backup_id: str
    backup_path: str
    archive_dir: str
    requested_recovery_target_time: str
    latest_recoverable_time: str
    missing_wal_file: str
    missing_range: tuple[str, ...]
    chain_profile: str = "full"

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckBackupRecoverabilityForMissingWalRecoveryGapScenarioCase(PgHealthCheckBackupRecoverabilityCase):
    pass

@dataclass(frozen=True, slots=True, kw_only=True)
class PgHealthCheckBackupRecoverabilityForSingleMissingWalGapSimpleScenarioCase(PgHealthCheckBackupRecoverabilityCase):
    pass

_PGHEALTHCHECKBACKUPRECOVERABILITYSCENARIO_CASE = PgHealthCheckBackupRecoverabilityForMissingWalRecoveryGapScenarioCase(
    case_id='missing_wal_recovery_gap',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "selected checkout ledger backup chain",
                    "entity": "missing_wal_recovery_gap",
                    "evidence": [
                        "scripted diagnostic actions observed selected checkout ledger backup chain"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "missing wal segment a7",
                    "entity": "missing_wal_recovery_gap",
                    "evidence": [
                        "scripted diagnostic actions observed missing wal segment a7"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "latest recoverable point is 02:31",
                    "entity": "missing_wal_recovery_gap",
                    "evidence": [
                        "scripted diagnostic actions observed latest recoverable point is 02:31"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "standby seed and reporting clone are not approved recovery sources",
                    "entity": "missing_wal_recovery_gap",
                    "evidence": [
                        "scripted diagnostic actions observed standby seed and reporting clone are not approved recovery sources"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "business rpo is violated",
                    "entity": "missing_wal_recovery_gap",
                    "evidence": [
                        "scripted diagnostic actions observed business rpo is violated"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "missing WAL creates a 14 minutes business RPO gap"
            ],
            "verification": [
                "sandbox restore validation confirmed the gap"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgHealthCheckBackupRecoverabilityForMissingWalRecoveryGapEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Production DR readiness audit with multiple backup chains and one selected unrecoverable recovery window.',
    alert='[DR Readiness Audit] The scheduled recoverability audit for a production recovery window needs manual evidence review. Validate the selected backup chain, restore-drill evidence, archive continuity, and the most recent recoverable point for the business recovery target. Several historical drills and monitoring events are present in the catalog, so separate current-window evidence from operational noise before submitting.',
    initial_state={'status': 'needs_dr_validation',
 'business_service': 'checkout-ledger',
 'audit_batch_id': 'dr-readiness-20260709-am',
 'recovery_window_label': 'checkout-ledger closeout 02:45Z',
 'requested_recovery_target_time': '2026-07-08 02:45:00+00'},
    expected_target={'status': 'audited',
 'backup_id': 'base_20260708_020000_tli2',
 'archive_gap_detected': True,
 'missing_wal_file': '0000000200000000000000A7',
 'latest_recoverable_time': '2026-07-08 02:31:00+00',
 'business_rpo_risk': 'requested target is 14 minutes beyond the latest recoverable point'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    drill_batch_id='dr-readiness-20260709-am',
    recovery_window_label='checkout-ledger closeout 02:45Z',
    backup_id='base_20260708_020000_tli2',
    backup_path='/tmp/ops_dr_backup/pg-primary/base_20260708_020000_tli2',
    archive_dir='/tmp/ops_dr_archive/pg-primary/timeline_00000002',
    requested_recovery_target_time='2026-07-08 02:45:00+00',
    latest_recoverable_time='2026-07-08 02:31:00+00',
    missing_wal_file='0000000200000000000000A7',
    missing_range=('2026-07-08 02:31:00+00', '2026-07-08 02:38:00+00'),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.666667,
        reference_run_ids=('run_pg_health_check_backup_recoverability_missing_wal_recovery_gap_MockLLMAgent',),
    ),
)

_PGHEALTHCHECKBACKUPRECOVERABILITY_SIMPLE_CASE = PgHealthCheckBackupRecoverabilityForSingleMissingWalGapSimpleScenarioCase(
    case_id='single_missing_wal_gap_simple',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "selected ledger backup chain",
                    "entity": "single_missing_wal_gap_simple",
                    "evidence": [
                        "scripted diagnostic actions observed selected ledger backup chain"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "required wal segment is missing",
                    "entity": "single_missing_wal_gap_simple",
                    "evidence": [
                        "scripted diagnostic actions observed required wal segment is missing"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "requested target exceeds latest recoverable point",
                    "entity": "single_missing_wal_gap_simple",
                    "evidence": [
                        "scripted diagnostic actions observed requested target exceeds latest recoverable point"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "business rpo is violated",
                    "entity": "single_missing_wal_gap_simple",
                    "evidence": [
                        "scripted diagnostic actions observed business rpo is violated"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "missing WAL creates a 14 minutes business RPO gap"
            ],
            "verification": [
                "sandbox restore validation confirmed the gap"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=1,
    evaluator=PgHealthCheckBackupRecoverabilityForSingleMissingWalGapSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='A focused DR audit with one selected chain, one healthy comparison chain, and a single missing WAL segment.',
    alert='[DR Readiness Review] The selected business recovery window has not been signed off. Verify the chosen backup, archive continuity, sandbox restore evidence, and the latest safe recovery point. A prior healthy chain remains visible for comparison.',
    initial_state={'status': 'needs_dr_validation', 'business_service': 'checkout-ledger', 'audit_batch_id': 'dr-simple-20260729'},
    expected_target={'status': 'audited', 'archive_gap_detected': True, 'business_rpo_risk': 'requested target exceeds latest recoverable point'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    drill_batch_id='dr-simple-20260729',
    recovery_window_label='checkout-ledger closeout 02:45Z',
    backup_id='base_20260708_020000_tli2',
    backup_path='/tmp/ops_dr_backup/pg-primary/base_20260708_020000_tli2',
    archive_dir='/tmp/ops_dr_archive/pg-primary/timeline_00000002',
    requested_recovery_target_time='2026-07-08 02:45:00+00',
    latest_recoverable_time='2026-07-08 02:31:00+00',
    missing_wal_file='0000000200000000000000A7',
    missing_range=('2026-07-08 02:31:00+00', '2026-07-08 02:38:00+00'),
    chain_profile='simple',
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.2,
        reference_run_ids=('run_pg_health_check_backup_recoverability_single_missing_wal_gap_simple_MockLLMAgent',),
    ),
)


import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import (
    PgQueryPerfFaultFingerprintProbe,
    _cancel_open_connection,
    _join_thread,
    _json_object,
    _json_response,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)

class PgHealthCheckBackupRecoverabilityInjector(BaseFaultInjector):
    """
    模拟生产灾备巡检：多条备份链和运维噪声并存，只有当前审计窗口
    的 timeline 2 物理备份链缺少一个必需归档 WAL 段。
    """

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print("[FaultInjector:PgHealthCheckBackupRecoverabilityInjector] Preparing backup chain assets...")
        self.chains = self._backup_chains()
        self._create_backup_files()
        self._create_metadata()
        self._assert_fault_observable()
        print("[FaultInjector:PgHealthCheckBackupRecoverabilityInjector] Fault injection complete.")

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.backup_id = config['backup_id']
        self.backup_path = config['backup_path']
        self.archive_dir = config['archive_dir']
        self.drill_batch_id = config['drill_batch_id']
        self.recovery_window_label = config['recovery_window_label']
        self.requested_recovery_target_time = config['requested_recovery_target_time']
        self.latest_recoverable_time = config['latest_recoverable_time']
        self.missing_wal_file = config['missing_wal_file']
        self.missing_range = tuple(config['missing_range'])
        self.chain_profile = str(config.get('chain_profile', 'full'))

    def _sql_literal(self, value) -> str:
        return "'" + str(value).replace("'", "''") + "'"

    def _backup_chains(self):
        chains = [
            self._chain(
                backup_id="base_20260706_020000_tli1",
                backup_path="/tmp/ops_dr_backup/pg-primary/base_20260706_020000_tli1",
                archive_dir="/tmp/ops_dr_archive/pg-primary/timeline_00000001",
                timeline=1,
                started_at="2026-07-06 02:00:00+00",
                completed_at="2026-07-06 02:12:00+00",
                requested_target="2026-07-06 02:45:00+00",
                latest_recoverable="2026-07-06 02:45:00+00",
                status="validated_success",
                is_audit_target=False,
                label="prior nightly ledger closeout",
                note="successful drill from previous nightly run",
                wal_specs=[
                    ("000000010000000000000090", 144, "2026-07-06 02:00:00+00", "2026-07-06 02:12:00+00", True),
                    ("000000010000000000000091", 145, "2026-07-06 02:12:00+00", "2026-07-06 02:24:00+00", True),
                    ("000000010000000000000092", 146, "2026-07-06 02:24:00+00", "2026-07-06 02:36:00+00", True),
                    ("000000010000000000000093", 147, "2026-07-06 02:36:00+00", "2026-07-06 02:50:00+00", True),
                ],
            ),
            self._chain(
                backup_id=self.backup_id,
                backup_path=self.backup_path,
                archive_dir=self.archive_dir,
                timeline=2,
                started_at="2026-07-08 02:00:00+00",
                completed_at="2026-07-08 02:11:00+00",
                requested_target=self.requested_recovery_target_time,
                latest_recoverable=self.latest_recoverable_time,
                status="available_for_dr_audit",
                is_audit_target=True,
                label=self.recovery_window_label,
                note="current audit target after standby promotion to timeline 2",
                wal_specs=[
                    ("0000000200000000000000A4", 164, "2026-07-08 02:00:00+00", "2026-07-08 02:12:00+00", True),
                    ("0000000200000000000000A5", 165, "2026-07-08 02:12:00+00", "2026-07-08 02:22:00+00", True),
                    ("0000000200000000000000A6", 166, "2026-07-08 02:22:00+00", self.latest_recoverable_time, True),
                    (self.missing_wal_file, 167, self.missing_range[0], self.missing_range[1], False),
                    ("0000000200000000000000A8", 168, "2026-07-08 02:38:00+00", "2026-07-08 02:50:00+00", True),
                ],
            ),
            self._chain(
                backup_id="base_20260708_021500_standby_tli2",
                backup_path="/tmp/ops_dr_backup/pg-standby/base_20260708_021500_standby_tli2",
                archive_dir="/tmp/ops_dr_archive/pg-standby/timeline_00000002",
                timeline=2,
                started_at="2026-07-08 02:15:00+00",
                completed_at="2026-07-08 02:27:00+00",
                requested_target="2026-07-08 02:45:00+00",
                latest_recoverable="2026-07-08 02:45:00+00",
                status="standby_validation_success",
                is_audit_target=False,
                label="standby seeding after promotion",
                note="same-day standby seed after promotion",
                wal_specs=[
                    ("0000000200000000000000A9", 169, "2026-07-08 02:15:00+00", "2026-07-08 02:25:00+00", True),
                    ("0000000200000000000000AA", 170, "2026-07-08 02:25:00+00", "2026-07-08 02:35:00+00", True),
                    ("0000000200000000000000AB", 171, "2026-07-08 02:35:00+00", "2026-07-08 02:45:00+00", True),
                ],
            ),
            self._chain(
                backup_id="base_20260708_030000_reporting_clone_tli2",
                backup_path="/tmp/ops_dr_backup/reporting-clone/base_20260708_030000_reporting_clone_tli2",
                archive_dir="/tmp/ops_dr_archive/reporting-clone/timeline_00000002",
                timeline=2,
                started_at="2026-07-08 03:00:00+00",
                completed_at="2026-07-08 03:09:00+00",
                requested_target="2026-07-08 03:30:00+00",
                latest_recoverable="2026-07-08 03:20:00+00",
                status="reporting_clone_failed_validation",
                is_audit_target=False,
                label="reporting clone refresh",
                note="BI clone refresh restore attempt",
                wal_specs=[
                    ("0000000200000000000000B0", 176, "2026-07-08 03:00:00+00", "2026-07-08 03:10:00+00", True),
                    ("0000000200000000000000B1", 177, "2026-07-08 03:10:00+00", "2026-07-08 03:20:00+00", True),
                    ("0000000200000000000000B2", 178, "2026-07-08 03:20:00+00", "2026-07-08 03:30:00+00", False),
                ],
            ),
            self._chain(
                backup_id="base_20260629_020000_tli1",
                backup_path="/tmp/ops_dr_backup/pg-primary/base_20260629_020000_tli1",
                archive_dir="/tmp/ops_dr_archive/pg-primary/timeline_00000001_retired",
                timeline=1,
                started_at="2026-06-29 02:00:00+00",
                completed_at="2026-06-29 02:13:00+00",
                requested_target="2026-06-29 03:00:00+00",
                latest_recoverable="2026-06-29 02:24:00+00",
                status="expired_by_retention",
                is_audit_target=False,
                label="expired weekly chain",
                note="normal retention cleanup on retired timeline",
                wal_specs=[
                    ("000000010000000000000070", 112, "2026-06-29 02:00:00+00", "2026-06-29 02:12:00+00", True),
                    ("000000010000000000000071", 113, "2026-06-29 02:12:00+00", "2026-06-29 02:24:00+00", True),
                    ("000000010000000000000072", 114, "2026-06-29 02:24:00+00", "2026-06-29 02:36:00+00", False),
                ],
            ),
        ]
        if self.chain_profile == "simple":
            return [chain for chain in chains if chain["is_audit_target"] or chain["backup_id"] == "base_20260706_020000_tli1"]
        return chains

    def _chain(self, **kwargs):
        base_files = {
            "backup_label": (
                f"START WAL LOCATION: 0/{kwargs['timeline']}000000 "
                f"(file {kwargs['wal_specs'][0][0]})\n"
                f"BACKUP FROM: primary\nSTART TIME: {kwargs['started_at']}\n"
            ),
            "global/pg_control": f"pg_control snapshot for {kwargs['backup_id']}\n",
            "base/16384/2600": f"heap fork sample block 2600 for {kwargs['backup_id']}\n",
            "base/16384/2601": f"heap fork sample block 2601 for {kwargs['backup_id']}\n",
        }
        wal_segments = [
            {
                "wal_file": wal_file,
                "sequence": sequence,
                "start_time": start_time,
                "end_time": end_time,
                "present": present,
                "size_bytes": 0,
            }
            for wal_file, sequence, start_time, end_time, present in kwargs.pop("wal_specs")
        ]
        kwargs["base_files"] = base_files
        kwargs["wal_segments"] = wal_segments
        return kwargs

    def _create_backup_files(self):
        import json as _json
        import posixpath
        import shlex
        import subprocess

        commands = [
            "rm -rf /tmp/ops_dr_backup /tmp/ops_dr_archive /tmp/pg_restore_sandbox",
            "mkdir -p /tmp/ops_dr_backup /tmp/ops_dr_archive",
        ]
        for chain in self.chains:
            commands.append(f"mkdir -p {shlex.quote(chain['backup_path'])} {shlex.quote(chain['archive_dir'])}")
            for rel_path, content in chain["base_files"].items():
                full_path = posixpath.join(chain["backup_path"], rel_path)
                commands.append(f"mkdir -p {shlex.quote(posixpath.dirname(full_path))}")
                commands.append(f"printf %s {shlex.quote(content)} > {shlex.quote(full_path)}")
            for item in chain["wal_segments"]:
                if not item["present"]:
                    continue
                wal_path = posixpath.join(chain["archive_dir"], item["wal_file"])
                content = f"WAL {item['wal_file']} records from {item['start_time']} to {item['end_time']}\n"
                commands.append(f"printf %s {shlex.quote(content)} > {shlex.quote(wal_path)}")
                item["size_bytes"] = len(content.encode("utf-8"))
            manifest = {
                "backup_id": chain["backup_id"],
                "base_backup_path": chain["backup_path"],
                "archive_dir": chain["archive_dir"],
                "backup_start_time": chain["started_at"],
                "backup_stop_time": chain["completed_at"],
                "requested_recovery_target_time": chain["requested_target"],
                "files": [
                    {"path": rel_path, "size_bytes": len(content.encode("utf-8"))}
                    for rel_path, content in chain["base_files"].items()
                ],
                "wal_chain": [
                    {
                        "wal_file": item["wal_file"],
                        "sequence": item["sequence"],
                        "start_time": item["start_time"],
                        "end_time": item["end_time"],
                        "required": True,
                    }
                    for item in chain["wal_segments"]
                ],
            }
            manifest_json = _json.dumps(manifest, ensure_ascii=False, indent=2)
            commands.append(
                f"cat > {shlex.quote(posixpath.join(chain['backup_path'], 'backup_manifest.json'))} <<'JSON'\n"
                f"{manifest_json}\nJSON"
            )
        result = subprocess.run(
            ["docker", "exec", self.env.deployment.container_name, "bash", "-lc", "\n".join(commands)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())

    def _create_metadata(self):
        import posixpath

        self.env.execute_sql("DROP SCHEMA IF EXISTS ops_dr CASCADE;")
        self.env.execute_sql("CREATE SCHEMA ops_dr;")
        self.env.execute_sql("""
            CREATE TABLE ops_dr.backup_sets (
                backup_id text PRIMARY KEY,
                backup_path text NOT NULL,
                manifest_path text NOT NULL,
                archive_dir text NOT NULL,
                started_at timestamptz NOT NULL,
                completed_at timestamptz NOT NULL,
                requested_recovery_target_time timestamptz NOT NULL,
                status text NOT NULL,
                timeline integer NOT NULL,
                drill_batch_id text NOT NULL,
                recovery_window_label text NOT NULL,
                is_audit_target boolean NOT NULL,
                notes text NOT NULL
            );
            CREATE TABLE ops_dr.audit_requests (
                audit_batch_id text PRIMARY KEY,
                business_service text NOT NULL,
                recovery_window_label text NOT NULL,
                requested_recovery_target_time timestamptz NOT NULL,
                selected_backup_id text NOT NULL,
                priority text NOT NULL,
                review_reason text NOT NULL
            );
            CREATE TABLE ops_dr.backup_files (
                backup_id text NOT NULL,
                relative_path text NOT NULL,
                size_bytes bigint NOT NULL,
                checksum_status text NOT NULL
            );
            CREATE TABLE ops_dr.archive_segments (
                backup_id text NOT NULL,
                timeline integer NOT NULL,
                segment_no integer NOT NULL,
                wal_file text NOT NULL,
                first_record_time timestamptz NOT NULL,
                last_record_time timestamptz NOT NULL,
                present boolean NOT NULL,
                file_path text NOT NULL,
                size_bytes bigint NOT NULL,
                retention_state text NOT NULL
            );
            CREATE TABLE ops_dr.restore_drill_runs (
                run_id text PRIMARY KEY,
                backup_id text NOT NULL,
                target_time timestamptz NOT NULL,
                run_started_at timestamptz NOT NULL,
                result text NOT NULL,
                failure_class text NOT NULL,
                log_excerpt text NOT NULL
            );
            CREATE TABLE ops_dr.archive_retention_events (
                event_id text PRIMARY KEY,
                event_time timestamptz NOT NULL,
                timeline integer NOT NULL,
                cutoff_time timestamptz NOT NULL,
                action text NOT NULL,
                notes text NOT NULL
            );
            CREATE TABLE ops_dr.monitoring_events (
                event_time timestamptz NOT NULL,
                source text NOT NULL,
                severity text NOT NULL,
                related_backup_id text,
                message text NOT NULL
            );
            CREATE TABLE ops_dr.archive_object_inventory (
                object_key text PRIMARY KEY,
                backup_id text NOT NULL,
                wal_file text NOT NULL,
                bucket text NOT NULL,
                region text NOT NULL,
                storage_class text NOT NULL,
                lifecycle_state text NOT NULL,
                legal_hold boolean NOT NULL,
                replication_status text NOT NULL,
                usable_for_recovery boolean NOT NULL,
                notes text NOT NULL
            );
            CREATE TABLE ops_dr.recovery_runbook_approvals (
                work_order_id text PRIMARY KEY,
                audit_batch_id text NOT NULL,
                business_service text NOT NULL,
                recovery_window_label text NOT NULL,
                selected_backup_id text NOT NULL,
                approved_source_role text NOT NULL,
                approval_state text NOT NULL,
                approved_at timestamptz,
                approval_notes text NOT NULL
            );
            CREATE TABLE ops_dr.timeline_promotion_history (
                timeline integer PRIMARY KEY,
                predecessor_timeline integer,
                promoted_at timestamptz NOT NULL,
                promoted_host text NOT NULL,
                promotion_lsn text NOT NULL,
                promotion_reason text NOT NULL
            );
            CREATE TABLE ops_dr.backup_label_chain (
                backup_id text PRIMARY KEY,
                source_role text NOT NULL,
                timeline integer NOT NULL,
                start_wal_file text NOT NULL,
                stop_wal_file text NOT NULL,
                upstream_timeline integer,
                label_summary text NOT NULL
            );
            CREATE TABLE ops_dr.archive_replica_checksums (
                backup_id text NOT NULL,
                wal_file text NOT NULL,
                local_checksum_status text NOT NULL,
                object_checksum_status text NOT NULL,
                replica_region text NOT NULL,
                replica_status text NOT NULL,
                usable_for_restore boolean NOT NULL,
                verified_at timestamptz NOT NULL,
                notes text NOT NULL
            );
            CREATE TABLE ops_dr.restore_drill_artifacts (
                artifact_id text PRIMARY KEY,
                run_id text NOT NULL,
                backup_id text NOT NULL,
                target_time timestamptz NOT NULL,
                artifact_path text NOT NULL,
                artifact_status text NOT NULL,
                signed_by text NOT NULL,
                notes text NOT NULL
            );
        """)
        backup_rows = []
        file_rows = []
        archive_rows = []
        for chain in self.chains:
            backup_rows.append(
                f"({self._sql_literal(chain['backup_id'])}, "
                f"{self._sql_literal(chain['backup_path'])}, "
                f"{self._sql_literal(posixpath.join(chain['backup_path'], 'backup_manifest.json'))}, "
                f"{self._sql_literal(chain['archive_dir'])}, "
                f"{self._sql_literal(chain['started_at'])}, {self._sql_literal(chain['completed_at'])}, "
                f"{self._sql_literal(chain['requested_target'])}, "
                f"{self._sql_literal(chain['status'])}, {chain['timeline']}, "
                f"{self._sql_literal(self.drill_batch_id)}, {self._sql_literal(chain['label'])}, "
                f"{'true' if chain['is_audit_target'] else 'false'}, {self._sql_literal(chain['note'])})"
            )
            for rel_path, content in chain["base_files"].items():
                file_rows.append(
                    f"({self._sql_literal(chain['backup_id'])}, {self._sql_literal(rel_path)}, "
                    f"{len(content.encode('utf-8'))}, 'ok')"
                )
            for item in chain["wal_segments"]:
                retention_state = "retained"
                if not item["present"] and chain["status"] == "expired_by_retention":
                    retention_state = "expired_by_policy"
                elif not item["present"]:
                    retention_state = "unexpected_missing"
                archive_rows.append(
                    f"({self._sql_literal(chain['backup_id'])}, {chain['timeline']}, {item['sequence']}, "
                    f"{self._sql_literal(item['wal_file'])}, "
                    f"{self._sql_literal(item['start_time'])}, "
                    f"{self._sql_literal(item['end_time'])}, "
                    f"{'true' if item['present'] else 'false'}, "
                    f"{self._sql_literal(posixpath.join(chain['archive_dir'], item['wal_file']))}, "
                    f"{int(item.get('size_bytes') or 0)}, {self._sql_literal(retention_state)})"
                )
        self.env.execute_sql("INSERT INTO ops_dr.backup_sets VALUES " + ", ".join(backup_rows) + ";")
        self.env.execute_sql(f"""
            INSERT INTO ops_dr.audit_requests VALUES (
                {self._sql_literal(self.drill_batch_id)},
                'checkout-ledger',
                {self._sql_literal(self.recovery_window_label)},
                {self._sql_literal(self.requested_recovery_target_time)},
                {self._sql_literal(self.backup_id)},
                'p1',
                'quarter-close recovery objective selected after timeline-2 promotion'
            );
        """)
        self.env.execute_sql("INSERT INTO ops_dr.backup_files VALUES " + ", ".join(file_rows) + ";")
        self.env.execute_sql("INSERT INTO ops_dr.archive_segments VALUES " + ", ".join(archive_rows) + ";")
        self.env.execute_sql(f"""
            INSERT INTO ops_dr.restore_drill_runs VALUES
            ('drill_20260706_success', 'base_20260706_020000_tli1', '2026-07-06 02:45:00+00',
             '2026-07-06 04:05:00+00', 'success', 'none',
             'sandbox replay completed through target on timeline 1'),
            ('drill_20260708_old_failure', 'base_20260706_020000_tli1', '2026-07-06 02:45:00+00',
             '2026-07-08 11:40:00+00', 'failed', 'sandbox_config',
             'retired sandbox had stale tablespace mapping; backup chain later revalidated successfully'),
            ('drill_20260709_pending', {self._sql_literal(self.backup_id)}, {self._sql_literal(self.requested_recovery_target_time)},
             '2026-07-09 06:00:00+00', 'pending_manual_review', 'unknown',
             'automated audit selected this chain after timeline switch'),
            ('drill_20260708_standby_success', 'base_20260708_021500_standby_tli2', '2026-07-08 02:45:00+00',
             '2026-07-08 05:10:00+00', 'success', 'none',
             'standby seed replay completed through the requested target'),
            ('drill_20260708_reporting_clone_failure', 'base_20260708_030000_reporting_clone_tli2', '2026-07-08 03:30:00+00',
             '2026-07-08 06:20:00+00', 'failed', 'clone_copy_aborted',
             'reporting clone restore stopped after a BI refresh copy abort'),
            ('drill_20260709_standby_pending', 'base_20260708_021500_standby_tli2', '2026-07-08 02:45:00+00',
             '2026-07-09 06:05:00+00', 'pending_manual_review', 'unknown',
             'standby seed audit requested by capacity planning team');
            INSERT INTO ops_dr.archive_retention_events VALUES
            ('ret_20260708_tli1', '2026-07-08 00:30:00+00', 1, '2026-06-30 00:00:00+00',
             'expire_archives', 'normal 7 day WAL retention on retired timeline'),
            ('ret_20260709_tli2', '2026-07-09 00:30:00+00', 2, '2026-07-02 00:00:00+00',
             'keep_current_window', 'current audit window explicitly excluded from cleanup');
            INSERT INTO ops_dr.monitoring_events VALUES
            ('2026-07-08 01:58:00+00', 'backup-mailer', 'info', {self._sql_literal(self.backup_id)},
             'base backup completed and success mail delivered'),
            ('2026-07-08 02:29:00+00', 'archive-lag-probe', 'info', NULL,
             'archiver reported segment 0000000200000000000000A6 archived successfully'),
            ('2026-07-08 02:33:00+00', 'archive-lag-probe', 'warning', NULL,
             'standby archive lag briefly exceeded 180s during report ETL burst'),
            ('2026-07-08 02:36:00+00', 'archive-lag-probe', 'info', NULL,
             'archive retry job reported pending queue drained after earlier lag warning'),
            ('2026-07-08 02:41:00+00', 'bi-reporting', 'info', NULL,
             'daily ledger extract ran slow SQL against reporting replica'),
            ('2026-07-08 02:52:00+00', 'archive-lag-probe', 'warning', NULL,
             'object listing showed upload backlog on the primary archive bucket during nightly sweep'),
            ('2026-07-09 06:00:00+00', 'dr-audit', 'warning', {self._sql_literal(self.backup_id)},
             'recoverability audit requested manual evidence review for selected business window');
            INSERT INTO ops_dr.archive_object_inventory VALUES
            ('s3://ledger-dr-primary/timeline_00000002/0000000200000000000000A6', {self._sql_literal(self.backup_id)}, '0000000200000000000000A6',
             'ledger-dr-primary', 'us-east-1', 'STANDARD', 'active', true, 'replicated', true,
             'selected primary chain WAL replicated and legal-hold protected'),
            ('s3://ledger-dr-primary/timeline_00000002/0000000200000000000000A7', {self._sql_literal(self.backup_id)}, {self._sql_literal(self.missing_wal_file)},
             'ledger-dr-primary', 'us-east-1', 'STANDARD', 'restore_required', false, 'replica_missing', false,
             'catalog entry registered by the nightly object audit'),
            ('s3://ledger-dr-primary/timeline_00000002/0000000200000000000000A8', {self._sql_literal(self.backup_id)}, '0000000200000000000000A8',
             'ledger-dr-primary', 'us-east-1', 'STANDARD', 'active', true, 'replicated', true,
             'later WAL segment on the same timeline'),
            ('s3://ledger-dr-standby/timeline_00000002/0000000200000000000000AB', 'base_20260708_021500_standby_tli2', '0000000200000000000000AB',
             'ledger-dr-standby', 'us-west-2', 'STANDARD', 'active', true, 'replicated', true,
             'standby seed archive replicated in the west bucket'),
            ('s3://ledger-bi-clone/timeline_00000002/0000000200000000000000B2', 'base_20260708_030000_reporting_clone_tli2', '0000000200000000000000B2',
             'ledger-bi-clone', 'us-east-2', 'STANDARD_IA', 'expired_by_lifecycle', false, 'not_replicated', false,
             'BI clone bucket applies STANDARD_IA lifecycle rules');
            INSERT INTO ops_dr.recovery_runbook_approvals VALUES
            ('wo-dr-20260709-0442', {self._sql_literal(self.drill_batch_id)}, 'checkout-ledger', {self._sql_literal(self.recovery_window_label)},
             {self._sql_literal(self.backup_id)}, 'pg-primary', 'approved_primary_only', '2026-07-09 05:55:00+00',
             'runbook authorizes pg-primary selected_backup_id only; standby seed requires separate promotion approval'),
            ('wo-dr-20260708-standby-seed', 'dr-readiness-20260708-standby', 'checkout-ledger', 'standby seed smoke test 02:45Z',
             'base_20260708_021500_standby_tli2', 'pg-standby', 'smoke_test_only', '2026-07-08 05:05:00+00',
             'technical restore evidence only; not approved as the current checkout-ledger recovery objective'),
            ('wo-bi-20260708-clone', 'bi-clone-20260708', 'ledger-reporting', 'reporting clone refresh 03:30Z',
             'base_20260708_030000_reporting_clone_tli2', 'reporting-clone', 'not_production_dr', NULL,
             'BI clone work order is outside production DR runbook');
            INSERT INTO ops_dr.timeline_promotion_history VALUES
            (1, NULL, '2026-06-29 00:00:00+00', 'pg-primary-a', '0/7000000', 'original production timeline'),
            (2, 1, '2026-07-08 01:52:00+00', 'pg-standby-b', '0/A400000', 'planned promotion before checkout-ledger closeout DR audit');
            INSERT INTO ops_dr.backup_label_chain VALUES
            ('base_20260706_020000_tli1', 'pg-primary', 1, '000000010000000000000090', '000000010000000000000093', NULL,
             'prior primary backup on retired timeline 1'),
            ({self._sql_literal(self.backup_id)}, 'pg-primary', 2, '0000000200000000000000A4', '0000000200000000000000A8', 1,
             'selected primary backup after timeline-2 promotion'),
            ('base_20260708_021500_standby_tli2', 'pg-standby-seed', 2, '0000000200000000000000A9', '0000000200000000000000AB', 1,
             'same-day standby seed chain starts after selected primary backup and is not runbook-approved'),
            ('base_20260708_030000_reporting_clone_tli2', 'reporting-clone', 2, '0000000200000000000000B0', '0000000200000000000000B2', 1,
             'BI clone label chain belongs to reporting refresh workflow');
            INSERT INTO ops_dr.archive_replica_checksums VALUES
            ({self._sql_literal(self.backup_id)}, '0000000200000000000000A6', 'ok', 'ok', 'us-west-2', 'replicated', true, '2026-07-08 02:32:00+00',
             'verified during the nightly cross-region sweep'),
            ({self._sql_literal(self.backup_id)}, {self._sql_literal(self.missing_wal_file)}, 'missing_local', 'missing_object', 'us-west-2', 'replica_missing', false, '2026-07-08 02:39:00+00',
             'nightly cross-region sweep record'),
            ('base_20260708_021500_standby_tli2', '0000000200000000000000AB', 'ok', 'ok', 'us-west-2', 'replicated', true, '2026-07-08 02:46:00+00',
             'standby seed checksum verified during the nightly cross-region sweep'),
            ('base_20260708_030000_reporting_clone_tli2', '0000000200000000000000B2', 'missing_local', 'expired_object', 'us-east-2', 'expired_by_lifecycle', false, '2026-07-08 03:31:00+00',
             'reporting clone WAL expired by lifecycle');
            INSERT INTO ops_dr.restore_drill_artifacts VALUES
            ('artifact-dr-20260709-primary-pending', 'drill_20260709_pending', {self._sql_literal(self.backup_id)}, {self._sql_literal(self.requested_recovery_target_time)},
             '/srv/dr-artifacts/checkout-ledger/20260709/primary_restore.log', 'incomplete_missing_wal', 'dr-automation',
             'audit artifact generated for the pending validation run'),
            ('artifact-dr-20260708-standby-smoke', 'drill_20260708_standby_success', 'base_20260708_021500_standby_tli2', '2026-07-08 02:45:00+00',
             '/srv/dr-artifacts/checkout-ledger/20260708/standby_seed_smoke.log', 'passed_smoke_only', 'standby-ops',
             'standby smoke artifact from capacity-team validation'),
            ('artifact-bi-20260708-clone', 'drill_20260708_reporting_clone_failure', 'base_20260708_030000_reporting_clone_tli2', '2026-07-08 03:30:00+00',
             '/srv/dr-artifacts/reporting/20260708/clone_restore.log', 'failed_clone_copy', 'bi-ops',
             'artifact belongs to reporting clone workflow');
        """)

    def _assert_fault_observable(self):
        import json as _json

        meta = self.env.execute_sql("""
            SET statement_timeout = '5s';
            SELECT backup_id, backup_path, manifest_path, archive_dir,
                   requested_recovery_target_time
            FROM ops_dr.backup_sets;
        """)
        if _json.loads(meta).get("status") != "success":
            raise RuntimeError(f"Backup metadata is not queryable: {meta}")
        validate = self.env.manage_instance("validate_backup", self.backup_path)
        payload = _json.loads(validate)
        if payload.get("status") != "success" or payload.get("archive_chain_ok") is not False:
            raise RuntimeError(f"Backup validation did not expose archive gap: {validate}")
        missing = payload.get("missing_wal_segments") or []
        if not missing or missing[0].get("wal_file") != self.missing_wal_file:
            raise RuntimeError(f"Missing WAL segment not identified: {validate}")

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {}

    def quiesce(self, context: FaultLifecycleContext):
        """No background threads or runtime resources to clean up."""
        pass

    def recover(self, context: FaultLifecycleContext):
        import shlex
        import subprocess

        print("[FaultInjector:PgHealthCheckBackupRecoverabilityInjector] Recovering...")
        _require_sql_success(
            self.env.execute_sql("DROP SCHEMA IF EXISTS ops_dr CASCADE;"),
            "drop backup-recoverability metadata",
        )
        paths = [
            "/tmp/ops_dr_backup",
            "/tmp/ops_dr_archive",
            "/tmp/pg_restore_sandbox",
        ]
        result = subprocess.run(
            [
                "docker", "exec", self.env.deployment.container_name,
                "bash", "-lc", "rm -rf " + " ".join(shlex.quote(path) for path in paths),
            ],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to remove backup-recoverability files: "
                f"{(result.stderr or result.stdout).strip()}"
            )

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._assert_fault_observable()


class PgHealthCheckBackupRecoverabilityScenario(PostgresScenario):
    scenario_id = 'pg_health_check_backup_recoverability'
    description = 'Simulates a DR health check where a physical backup cannot recover to the requested target because an archived WAL segment is missing.'
    cases = (_PGHEALTHCHECKBACKUPRECOVERABILITYSCENARIO_CASE, _PGHEALTHCHECKBACKUPRECOVERABILITY_SIMPLE_CASE)

    def build_fault_plan(self, case: PgHealthCheckBackupRecoverabilityCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgHealthCheckBackupRecoverabilityInjector,
                config={
                    'backup_id': case.backup_id,
                    'backup_path': case.backup_path,
                    'archive_dir': case.archive_dir,
                    'drill_batch_id': case.drill_batch_id,
                    'recovery_window_label': case.recovery_window_label,
                    'requested_recovery_target_time': case.requested_recovery_target_time,
                    'latest_recoverable_time': case.latest_recoverable_time,
                    'missing_wal_file': case.missing_wal_file,
                    'missing_range': case.missing_range,
                    'chain_profile': case.chain_profile,
                },
            ),
        )
