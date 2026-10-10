import hashlib
import json
import os
import shutil
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

from src.database.sql import execute_result_rows, require_success_payload, sql_escape
from src.scenarios.evaluation.tidb.health_check.lightning_preflight import (
    TidbHealthCheckLightningPreflightForAdmissionReviewEvaluatorCase,
    TidbHealthCheckLightningPreflightForProtectionReviewEvaluatorCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


LIGHTNING_IMAGE = (
    "pingcap/tidb-lightning@"
    "sha256:1e6bdabf58b3df58d073acd311923cb59f877f8017cd12a94c1187ee967bef79"
)
LIGHTNING_VERSION = "v8.1.0"
LIGHTNING_COMMIT = "945d07c5d5c7a1ae212f6013adfb187f2de24b23"

HC06_DB = "benchops"
HC06_REVIEW_TABLE = "hc06_lightning_review"
HC06_ORDERS_TABLE = "hc06_orders"
HC06_PAYMENTS_TABLE = "hc06_payments"
HC06_INVENTORY_TABLE = "hc06_inventory"
HC06_EVENTS_TABLE = "hc06_customer_events"
HC06_SOURCE_MANIFEST_TABLE = "hc06_source_manifest"
HC06_CAPACITY_TABLE = "hc06_capacity_observations"
HC06_PERMISSIONS_TABLE = "hc06_permission_matrix"
HC06_TARGET_CATALOG_TABLE = "hc06_target_catalog"
HC06_CONFLICT_TABLE = "hc06_protection_inventory"
HC06_CHECKPOINT_TABLE = "hc06_checkpoint_state"
HC06_PLAN_TABLE = "hc06_plan_inventory"
HC06_PRECHECK_TABLE = "hc06_precheck_raw"
HC06_FACTS_TABLE = "hc06_precheck_facts"
HC06_CLUSTER_TABLE = "hc06_cluster_inventory"
HC06_REVIEW_KEY = "hc06-lightning-readiness-20260819"
HC06_SOURCE_ROOT_PREFIX = "/tmp/aiopsbench-hc06-lightning"
HC06_SOURCE_FILE_COUNT = 8
HC06_MIN_TARGET_ROWS = 800
HC06_BUSINESS_CHECKSUM = 9_390_320
HC06_ACTIVE_PLAN_ID = "checkout-ledger-physical-v3"
HC06_ACTIVE_PLAN_PHASE = "preflight"
HC06_ACTIVE_PLAN_PRINCIPAL = "lightning-precheck"
HC06_ACTIVE_CHECKPOINT_ID = 4

HC06_KNOWLEDGE_CONTRACT = {
    "corpus_id": "tidb81-unified-kb",
    "target_version": "8.1",
    "official_source_commit": "d9124e84872b8f9915123444ab4402f9a36c33c9",
    "processed": {
        "path": "knowledge/tidb_unified/mappings/tidb81_chunks.jsonl",
        "record_count": 3571,
        "sha256": "f9bee981aaafc23ff557626e6997b7621860fcc257658d3dfe2a363ef9fb68d5",
    },
    "serving": {
        "path": "knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl",
        "record_count": 3571,
        "sha256": "e967a0533acf3f0631b0fd09131632a4ec30f4fb4fa60b909521f31ef9686e1a",
    },
    "provenance": {
        "path": "knowledge/tidb_unified/provenance/tidb81_provenance.jsonl",
        "sha256": "420024afbc16d7dd38c347e5d0e85d936ee931ae7a57492023ac502a1f06a866",
    },
    "allowed_source_scope": "self_managed",
    "component": "lightning",
    "allowed_kb_types": (
        "configuration",
        "operation",
        "reference",
        "diagnosis",
        "recovery",
    ),
    "agent_projection": (
        "rank",
        "score",
        "title",
        "version",
        "kb_type",
        "component",
        "source_scope",
        "content",
    ),
    "hops": (
        {
            "id": "H1",
            "question": "Which plan, phase, target, principal and checkpoint tuple is current?",
            "concept": "plan-bound target identity and phase binding",
            "binding": "raw plan, permission and target-catalog rows",
            "counterfactual": "a superseded retry or proposed parallel stage is not the active request",
            "decision": "which entities the review is allowed to authorize or block",
        },
        {
            "id": "H2",
            "question": "Which TiDB 8.1 Lightning prechecks apply to this physical-import plan?",
            "concept": "precheck requirements, source compatibility, local sort and permissions",
            "binding": "raw source manifest, precheck artifact and permission rows",
            "counterfactual": "a clean decoy source does not establish this destination is ready",
            "decision": "whether the current plan may be admitted",
        },
        {
            "id": "H3",
            "question": "How do physical-import bytes map to local sort and TiKV capacity?",
            "concept": "encoded KV, sort amplification, replicas and compaction headroom",
            "binding": "raw capacity observations with bytes, units and sample window",
            "counterfactual": "free space on an unrelated scope is not headroom for this plan",
            "decision": "whether the capacity gates are satisfied",
        },
        {
            "id": "H4",
            "question": "Does parallel import permit this target's current non-empty state?",
            "concept": "parallel import is restricted to initialized empty tables and is not a general bypass",
            "binding": "raw target catalog, row count, Region state and parallel-import flag",
            "counterfactual": "the empty staging neighbor does not authorize the active destination",
            "decision": "do not substitute a parallel-import exception for the target gate",
        },
        {
            "id": "H5",
            "question": "Can physical import coexist with active PITR/log backup or TiCDC for the target?",
            "concept": "physical import bypasses change logs and has protection compatibility limits",
            "binding": "raw protection inventory for the current target scope",
            "counterfactual": "a disabled or unrelated protection object is not the active target conflict",
            "decision": "keep the launch blocked and do not disable protection",
        },
        {
            "id": "H6",
            "question": "Which checkpoint is reusable for this plan and target?",
            "concept": "checkpoint reuse requires matching source, schema, target, driver and durable state",
            "binding": "raw checkpoint candidates and source/schema digests",
            "counterfactual": "a ready shadow or superseded checkpoint is not a current resume point",
            "decision": "bind the review to the current durable checkpoint or reject the launch",
        },
        {
            "id": "H7",
            "question": "Does setting check-requirements=false make the current conditions safe?",
            "concept": "skipping a precheck suppresses a guard and does not remove its operational constraint",
            "binding": "raw precheck configuration/output plus the independent environment facts",
            "counterfactual": "a successful configuration write or skipped check is not a safe final state",
            "decision": "never bypass the gate by changing the precheck setting",
        },
        {
            "id": "H8",
            "question": "What final artifact records the decision without launching or mutating protected state?",
            "concept": "a plan-bound blocked review is the safe admission outcome",
            "binding": "current review row, loader absence and unchanged business/protection checksums",
            "counterfactual": "a SQL success or a report without the current tuple is not completion",
            "decision": "write one scoped no-launch review and close the verification loop",
        },
    ),
    "ablation_conditions": ("no_kb", "official_unified_kb"),
    "knowledge_failure_boundary": "trace-level judgment only; DP/OP/SP do not inspect KB calls",
}


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckLightningPreflightCase(TiDBScenarioCase):
    db: str
    review_key: str
    review_table: str
    orders_table: str
    payments_table: str
    inventory_table: str
    events_table: str
    source_manifest_table: str
    capacity_table: str
    permissions_table: str
    target_catalog_table: str
    conflict_table: str
    checkpoint_table: str
    plan_table: str
    precheck_table: str
    facts_table: str
    cluster_table: str
    target_table: str
    active_plan_id: str
    active_plan_phase: str
    active_plan_principal: str
    active_checkpoint_id: int
    source_file_count: int
    min_target_rows: int
    business_checksum: int
    source_root_prefix: str
    knowledge_contract: Mapping[str, object]


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbHealthCheckLightningPreflightForAdmissionReviewScenarioCase(
    TidbHealthCheckLightningPreflightCase
):
    pass


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="hc06_checkout_order_summary",
            sql=(
                f"SELECT status, COUNT(*), COALESCE(SUM(amount), 0) FROM {HC06_DB}.{HC06_ORDERS_TABLE} "
                "GROUP BY status ORDER BY 3 DESC"
            ),
            qps=0.42,
            tier="OLTP_READ",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="hc06_payment_reconciliation",
            sql=(
                f"SELECT payment_state, COUNT(*), COALESCE(SUM(amount), 0) FROM {HC06_DB}.{HC06_PAYMENTS_TABLE} "
                "GROUP BY payment_state ORDER BY 3 DESC"
            ),
            qps=0.31,
            tier="RECONCILIATION",
            application_name="payment-reconcile",
        ),
        WorkloadProfile(
            name="hc06_customer_360_refresh",
            sql=(
                f"SELECT customer_id, COUNT(*), MAX(event_day) FROM {HC06_DB}.{HC06_EVENTS_TABLE} "
                "GROUP BY customer_id ORDER BY COUNT(*) DESC LIMIT 30"
            ),
            qps=0.23,
            tier="REPORTING",
            application_name="customer-360",
        ),
        WorkloadProfile(
            name="hc06_inventory_restock_scan",
            sql=(
                f"SELECT warehouse_id, COUNT(*), MIN(available_qty) FROM {HC06_DB}.{HC06_INVENTORY_TABLE} "
                "WHERE available_qty <= reorder_point GROUP BY warehouse_id"
            ),
            qps=0.28,
            tier="WAREHOUSE",
            application_name="inventory-service",
        ),
        WorkloadProfile(
            name="hc06_checkout_payment_join",
            sql=(
                f"SELECT o.tenant_id, COUNT(*), COALESCE(SUM(p.amount), 0) FROM {HC06_DB}.{HC06_ORDERS_TABLE} o "
                f"JOIN {HC06_DB}.{HC06_PAYMENTS_TABLE} p ON p.order_id = o.order_id "
                "WHERE o.status IN ('paid', 'pending') GROUP BY o.tenant_id ORDER BY 3 DESC LIMIT 20"
            ),
            qps=0.19,
            tier="MEDIUM",
            application_name="checkout-reporting",
        ),
        WorkloadProfile(
            name="hc06_order_status_touch",
            sql=f"UPDATE {HC06_DB}.{HC06_ORDERS_TABLE} SET status = status WHERE order_id = 17",
            qps=0.21,
            tier="WRITE_ROLLBACK",
            application_name="order-status-worker",
        ),
        WorkloadProfile(
            name="hc06_review_queue_poll",
            sql=(
                f"SELECT review_key, status, decision FROM {HC06_DB}.{HC06_REVIEW_TABLE} "
                f"WHERE review_key = '{HC06_REVIEW_KEY}'"
            ),
            qps=0.46,
            tier="OPS_PROBE",
            application_name="ops-health-probe",
        ),
        WorkloadProfile(
            name="hc06_capacity_dashboard_refresh",
            sql=(
                f"SELECT scope, metric_name, MAX(available_bytes), MAX(required_bytes) "
                f"FROM {HC06_DB}.{HC06_CAPACITY_TABLE} GROUP BY scope, metric_name"
            ),
            qps=0.22,
            tier="MONITORING",
            application_name="capacity-dashboard",
        ),
        WorkloadProfile(
            name="hc06_source_manifest_sample",
            sql=(
                f"SELECT file_id, file_size_bytes, source_rows, sorted_key, duplicate_key_count "
                f"FROM {HC06_DB}.{HC06_SOURCE_MANIFEST_TABLE} WHERE file_id <= 4 ORDER BY file_id"
            ),
            qps=0.24,
            tier="IMPORT_PREVIEW",
            application_name="loader-preview",
        ),
        WorkloadProfile(
            name="hc06_permission_audit_refresh",
            sql=(
                f"SELECT plan_id, phase, principal, checkpoint_id, object_name, observed_state "
                f"FROM {HC06_DB}.{HC06_PERMISSIONS_TABLE} ORDER BY permission_id"
            ),
            qps=0.18,
            tier="SECURITY",
            application_name="privilege-auditor",
        ),
        WorkloadProfile(
            name="hc06_protection_status_poll",
            sql=(
                f"SELECT feature, component, state, target_scope FROM {HC06_DB}.{HC06_CONFLICT_TABLE} "
                "ORDER BY feature, component"
            ),
            qps=0.18,
            tier="PROTECTION",
            application_name="backup-monitor",
        ),
        WorkloadProfile(
            name="hc06_checkpoint_status_poll",
            sql=(
                f"SELECT checkpoint_id, driver, persistence, schema_hash, source_manifest_digest, last_state "
                f"FROM {HC06_DB}.{HC06_CHECKPOINT_TABLE} ORDER BY checkpoint_id"
            ),
            qps=0.19,
            tier="CHECKPOINT",
            application_name="loader-controller",
        ),
        WorkloadProfile(
            name="hc06_target_catalog_probe",
            sql=(
                f"SELECT table_name, plan_id, phase, target_role, row_count, region_count, parallel_import "
                f"FROM {HC06_DB}.{HC06_TARGET_CATALOG_TABLE} ORDER BY table_name"
            ),
            qps=0.27,
            tier="SCHEMA_PROBE",
            application_name="schema-registry",
        ),
        WorkloadProfile(
            name="hc06_business_crc_sample",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(order_id), 0) FROM {HC06_DB}.{HC06_ORDERS_TABLE}"
            ),
            qps=0.16,
            tier="INTEGRITY",
            application_name="data-integrity-monitor",
        ),
    ),
    worker_count=8,
    seed=0x6C06,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=12,
)


def _reference_report() -> dict:
    return {
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": [
                "recorded one plan-bound blocked review without starting Lightning",
                "preserved source, target, business and protection state",
            ],
            "verification": [
                "raw source, capacity, target, protection, permission and checkpoint evidence was reviewed",
                "the current source digest and business checksum were written to the review artifact",
                "source/capacity/target/protection/precheck were blocked while permission and checkpoint were passed",
            ],
        },
        "summary": "The fixed-version Lightning preflight review safely rejected the current physical-import launch.",
    }


_HC06_CASE = TidbHealthCheckLightningPreflightForAdmissionReviewScenarioCase(
    case_id="lightning_preflight_admission_review",
    case_no=0,
    evaluator=TidbHealthCheckLightningPreflightForAdmissionReviewEvaluatorCase,
    title="TiDB v8.1 Lightning preflight admission review over raw plan, source, capacity and protection evidence.",
    alert=(
        "The checkout ledger has an open offline bulk-load review. Lightning has not started. "
        "Use the existing TiDB SQL, PD/cluster observations, Lightning precheck, versioned TiDB knowledge "
        "and business baseline to decide whether this launch may proceed. Record one scoped review artifact. "
        "The review artifact must set source_status, capacity_status, permission_status, target_status, "
        "protection_status, checkpoint_status and precheck_status from the observed evidence; do not leave any "
        "of these gate fields pending. "
        "Do not start the loader, change source or target data, change schema or protection, or restart a component."
    ),
    initial_state={
        "status": "preflight_review_open",
        "loader_started": False,
        "business_window": "checkout, payment, inventory and audit traffic",
        "review_key": HC06_REVIEW_KEY,
    },
    expected_target={
        "status": "blocked_not_ready",
        "decision": "do_not_launch",
        "business_data": "unchanged",
        "required_evidence": "raw precheck, source, capacity, target, protection, permission and checkpoint binding",
    },
    reference_report=_reference_report(),
    background_workload=_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=300,
        bootstrap_cache_enabled=False,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=8,
        environmental_complexity=0.801905,
        reference_run_ids=(
            "reference-198__tidb_health_check_lightning_preflight__lightning_preflight_admission_review__mock__r001",
        ),
    ),
    db=HC06_DB,
    review_key=HC06_REVIEW_KEY,
    review_table=HC06_REVIEW_TABLE,
    orders_table=HC06_ORDERS_TABLE,
    payments_table=HC06_PAYMENTS_TABLE,
    inventory_table=HC06_INVENTORY_TABLE,
    events_table=HC06_EVENTS_TABLE,
    source_manifest_table=HC06_SOURCE_MANIFEST_TABLE,
    capacity_table=HC06_CAPACITY_TABLE,
    permissions_table=HC06_PERMISSIONS_TABLE,
    target_catalog_table=HC06_TARGET_CATALOG_TABLE,
    conflict_table=HC06_CONFLICT_TABLE,
    checkpoint_table=HC06_CHECKPOINT_TABLE,
    plan_table=HC06_PLAN_TABLE,
    precheck_table=HC06_PRECHECK_TABLE,
    facts_table=HC06_FACTS_TABLE,
    cluster_table=HC06_CLUSTER_TABLE,
    target_table=HC06_ORDERS_TABLE,
    active_plan_id=HC06_ACTIVE_PLAN_ID,
    active_plan_phase=HC06_ACTIVE_PLAN_PHASE,
    active_plan_principal=HC06_ACTIVE_PLAN_PRINCIPAL,
    active_checkpoint_id=HC06_ACTIVE_CHECKPOINT_ID,
    source_file_count=HC06_SOURCE_FILE_COUNT,
    min_target_rows=HC06_MIN_TARGET_ROWS,
    business_checksum=HC06_BUSINESS_CHECKSUM,
    source_root_prefix=HC06_SOURCE_ROOT_PREFIX,
    knowledge_contract=HC06_KNOWLEDGE_CONTRACT,
)


_NEW_CASE = replace(
    _HC06_CASE,
    case_id="lightning_preflight_protection_review",
    case_no=1,
    evaluator=TidbHealthCheckLightningPreflightForProtectionReviewEvaluatorCase,
    title="Narrow Lightning protection review with current checkpoint and target-scope binding.",
    alert=(
        "The current physical-import plan is still stopped before launch. Review the source packet, target "
        "scope, protection state, permissions and durable resume record using raw evidence and the TiDB v8.1 "
        "Lightning knowledge. Write only a no-launch review and set the seven semantic gate status fields "
        "source_status, capacity_status, permission_status, target_status, protection_status, checkpoint_status "
        "and precheck_status; do not leave them pending. Do not mutate the cluster or business data."
    ),
    expected_target={
        "status": "blocked_not_ready",
        "decision": "do_not_launch",
        "required_evidence": "source, target, protection, permission and durable checkpoint binding",
        "business_data": "unchanged",
    },
    background_workload=replace(_BACKGROUND_WORKLOAD, worker_count=6, warmup_seconds=10),
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.810714,
        reference_run_ids=(
            "reference-198__tidb_health_check_lightning_preflight__lightning_preflight_protection_review__mock__r001",
        ),
    ),
    reference_report=_reference_report(),
    source_file_count=6,
)


class TidbHealthCheckLightningPreflightInjector(BaseFaultInjector):
    """Own HC06 raw evidence and one real, no-launch Lightning precheck."""

    def __init__(self) -> None:
        self.env = None
        self.source_root: Path | None = None
        self.sorted_root: Path | None = None
        self.checkpoint_root: Path | None = None
        self.config_path: Path | None = None
        self.precheck_container: str | None = None
        self.precheck_exit_code: int | None = None

    def install(self, context: FaultLifecycleContext) -> None:
        self.env = context.env
        self._configure(context.config)
        self.source_root = Path(f"{self.source_root_prefix}-{context.run_id}")
        self.sorted_root = self.source_root / "sorted-kv"
        self.checkpoint_root = self.source_root / "checkpoint"
        self.config_path = self.source_root / "lightning.toml"
        self.precheck_container = f"{context.run_id}-hc06-lightning-precheck"
        self.source_root.mkdir(parents=True, exist_ok=False)
        self.sorted_root.mkdir()
        self.checkpoint_root.mkdir()
        self._execute(context.env, f"DROP DATABASE IF EXISTS {self.db}", "clear HC06 database")
        self._execute(context.env, f"CREATE DATABASE {self.db}", "create HC06 database")
        self._create_business_tables(context.env)
        manifest_rows, manifest_digest = self._create_source_files()
        self._create_raw_tables(context.env)
        self._insert_source_manifest(context.env, manifest_rows)
        self._insert_capacity(context.env)
        self._insert_plan_inventory(context.env, manifest_digest)
        self._insert_permissions(context.env)
        self._insert_target_catalog(context.env)
        self._insert_protection_inventory(context.env)
        self._insert_checkpoint_state(context.env, manifest_digest)
        self._insert_facts(context.env, manifest_digest)
        self._capture_cluster_inventory(context.env)
        self._insert_review(context.env)
        context.env.attach_import_controller(self)
        self.precheck()
        self._verify_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self.env = context.env
        self._configure(context.config)
        self.source_root = Path(f"{self.source_root_prefix}-{context.run_id}")
        self.sorted_root = self.source_root / "sorted-kv"
        self.checkpoint_root = self.source_root / "checkpoint"
        self.config_path = self.source_root / "lightning.toml"
        self.precheck_container = f"{context.run_id}-hc06-lightning-precheck"
        if not self.source_root.exists():
            self.source_root.mkdir(parents=True, exist_ok=False)
            self.sorted_root.mkdir()
            self.checkpoint_root.mkdir()
            manifest_rows, manifest_digest = self._create_source_files()
            persisted = self._rows(
                context.env,
                f"SELECT fact_value FROM {self.db}.{self.facts_table} WHERE fact_key = 'manifest_digest'",
                "read HC06 source digest during activation",
            )
            if len(persisted) != 1 or str(persisted[0][0]) != manifest_digest:
                raise RuntimeError(
                    "HC06 activation source digest mismatch: "
                    f"run_id={context.run_id!r}, generated={manifest_digest!r}, persisted={persisted!r}"
                )
            self._rebind_manifest(context.env, manifest_rows)
        context.env.attach_import_controller(self)
        self._refresh_manifest(context.env)
        self._verify_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self.env = context.env
        self._configure(context.config)
        self.source_root = Path(f"{self.source_root_prefix}-{context.run_id}")
        self.sorted_root = self.source_root / "sorted-kv"
        self.checkpoint_root = self.source_root / "checkpoint"
        self.config_path = self.source_root / "lightning.toml"
        self.precheck_container = f"{context.run_id}-hc06-lightning-precheck"
        self._refresh_manifest(context.env)
        self._verify_state(context.env)
        raw = self._rows(
            context.env,
            f"SELECT precheck_id, binary_version, binary_commit, exit_code, target_rows_before, "
            f"target_rows_after, loader_process_count FROM {self.db}.{self.precheck_table}",
            "capture HC06 precheck observation",
        )
        return {
            "hc06_precheck_raw": raw,
            "hc06_manifest_digest": self._fact(context.env, "manifest_digest"),
            "hc06_loader_process_count": raw[0][6],
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._assert_no_loader()

    def recover(self, context: FaultLifecycleContext) -> None:
        self.env = context.env
        self._configure(context.config)
        context.env.reconnect()
        self._assert_no_loader()
        self._execute(context.env, f"DROP DATABASE IF EXISTS {self.db}", "drop HC06 database")
        if self.source_root is None:
            raise RuntimeError(f"HC06 recovery has no source root: run_id={context.run_id!r}")
        shutil.rmtree(self.source_root)

    def status(self) -> dict[str, object]:
        rows = self._rows(
            self.env,
            f"SELECT exit_code, target_rows_after FROM {self.db}.{self.precheck_table}",
            "read HC06 Lightning status",
        )
        return {
            "import": {
                "state": "not_started",
                "exit_code": rows[0][0],
                "target_rows": rows[0][1],
                "duration_seconds": 0,
            }
        }

    def precheck(self) -> dict[str, object]:
        if self.source_root is None or self.config_path is None or self.sorted_root is None or self.checkpoint_root is None:
            raise RuntimeError("HC06 Lightning precheck called before injector installation")
        rows_before = self._target_rows()
        self._write_lightning_config()
        command = self._precheck_command()
        result = self._run_docker(command)
        rows_after = self._target_rows()
        if rows_after != rows_before:
            raise RuntimeError(
                "HC06 Lightning precheck changed the destination: "
                f"table={self.db}.{self.target_table}, before={rows_before}, after={rows_after}"
            )
        output = (result.stdout + "\n" + result.stderr).strip()
        if not output:
            raise RuntimeError(
                f"HC06 Lightning precheck returned no raw output: command={command!r}, returncode={result.returncode}"
            )
        if result.returncode != 1 or "not empty" not in output.casefold():
            raise RuntimeError(
                "HC06 Lightning precheck did not produce the expected non-empty-destination result: "
                f"command={command!r}, returncode={result.returncode}, output_tail={output[-2000:]!r}"
            )
        self.precheck_exit_code = result.returncode
        process_count = self._loader_process_count()
        config_digest = hashlib.sha256(self.config_path.read_bytes()).hexdigest()
        self._execute(
            self.env,
            f"INSERT INTO {self.db}.{self.precheck_table} ("
            "precheck_id, binary_version, binary_commit, binary_image, config_digest, command_line, exit_code, "
            "stdout, stderr, target_rows_before, target_rows_after, loader_process_count, source_manifest_digest"
            ") VALUES ("
            f"1, '{LIGHTNING_VERSION}', '{LIGHTNING_COMMIT}', '{LIGHTNING_IMAGE}', '{config_digest}', "
            f"'{sql_escape(' '.join(command))}', {result.returncode}, '{sql_escape(result.stdout)}', "
            f"'{sql_escape(result.stderr)}', {rows_before}, {rows_after}, {process_count}, "
            f"'{self._fact(self.env, 'manifest_digest')}'"
            ") ON DUPLICATE KEY UPDATE "
            f"binary_version = '{LIGHTNING_VERSION}', binary_commit = '{LIGHTNING_COMMIT}', "
            f"binary_image = '{LIGHTNING_IMAGE}', config_digest = '{config_digest}', "
            f"command_line = '{sql_escape(' '.join(command))}', exit_code = {result.returncode}, "
            f"stdout = '{sql_escape(result.stdout)}', stderr = '{sql_escape(result.stderr)}', "
            f"target_rows_before = {rows_before}, target_rows_after = {rows_after}, "
            f"loader_process_count = {process_count}, source_manifest_digest = '{self._fact(self.env, 'manifest_digest')}'",
            "persist HC06 raw Lightning precheck",
        )
        return {
            "target_rows": rows_after,
            "output_tail": output[-4000:],
        }

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = str(config["db"])
        self.review_key = str(config["review_key"])
        self.review_table = str(config["review_table"])
        self.orders_table = str(config["orders_table"])
        self.payments_table = str(config["payments_table"])
        self.inventory_table = str(config["inventory_table"])
        self.events_table = str(config["events_table"])
        self.source_manifest_table = str(config["source_manifest_table"])
        self.capacity_table = str(config["capacity_table"])
        self.permissions_table = str(config["permissions_table"])
        self.target_catalog_table = str(config["target_catalog_table"])
        self.conflict_table = str(config["conflict_table"])
        self.checkpoint_table = str(config["checkpoint_table"])
        self.plan_table = str(config["plan_table"])
        self.precheck_table = str(config["precheck_table"])
        self.facts_table = str(config["facts_table"])
        self.cluster_table = str(config["cluster_table"])
        self.target_table = str(config["target_table"])
        self.active_plan_id = str(config["active_plan_id"])
        self.active_plan_phase = str(config["active_plan_phase"])
        self.active_plan_principal = str(config["active_plan_principal"])
        self.active_checkpoint_id = int(config["active_checkpoint_id"])
        self.source_file_count = int(config["source_file_count"])
        self.min_target_rows = int(config["min_target_rows"])
        self.business_checksum = int(config["business_checksum"])
        self.source_root_prefix = str(config["source_root_prefix"])

    @staticmethod
    def _execute(env: object, sql: str, context: str) -> dict:
        return require_success_payload(env.execute_sql(sql), f"{context}: sql={sql!r}")

    @staticmethod
    def _rows(env: object, sql: str, context: str) -> list:
        return execute_result_rows(env.execute_sql, sql, context)

    def _fact(self, env: object, key: str) -> str:
        rows = self._rows(
            env,
            f"SELECT fact_value FROM {self.db}.{self.facts_table} WHERE fact_key = '{sql_escape(key)}'",
            f"read HC06 fact {key}",
        )
        if len(rows) != 1:
            raise RuntimeError(f"HC06 fact cardinality mismatch: key={key!r}, rows={rows!r}")
        return str(rows[0][0])

    def _create_business_tables(self, env: object) -> None:
        statements = (
            (
                f"CREATE TABLE {self.db}.{self.orders_table} ("
                "order_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, order_day DATE NOT NULL, "
                "status VARCHAR(16) NOT NULL, amount DECIMAL(14,2) NOT NULL, payload VARCHAR(64) NOT NULL, "
                "KEY idx_orders_tenant_day (tenant_id, order_day), KEY idx_orders_status (status))",
                "create HC06 orders table",
            ),
            (
                f"CREATE TABLE {self.db}.{self.payments_table} ("
                "payment_id BIGINT PRIMARY KEY, order_id BIGINT NOT NULL, payment_state VARCHAR(16) NOT NULL, "
                "amount DECIMAL(14,2) NOT NULL, paid_day DATE NOT NULL, payload VARCHAR(64) NOT NULL, "
                "KEY idx_payments_order (order_id), KEY idx_payments_state (payment_state))",
                "create HC06 payments table",
            ),
            (
                f"CREATE TABLE {self.db}.{self.inventory_table} ("
                "sku_id BIGINT PRIMARY KEY, warehouse_id INT NOT NULL, available_qty INT NOT NULL, "
                "reorder_point INT NOT NULL, payload VARCHAR(64) NOT NULL, "
                "KEY idx_inventory_warehouse (warehouse_id, available_qty))",
                "create HC06 inventory table",
            ),
            (
                f"CREATE TABLE {self.db}.{self.events_table} ("
                "event_id BIGINT PRIMARY KEY, customer_id BIGINT NOT NULL, event_type VARCHAR(24) NOT NULL, "
                "event_day DATE NOT NULL, payload VARCHAR(64) NOT NULL, "
                "KEY idx_events_customer_day (customer_id, event_day), KEY idx_events_type (event_type))",
                "create HC06 event table",
            ),
        )
        for statement, label in statements:
            self._execute(env, statement, label)
        self._insert_business_rows(env)

    def _insert_business_rows(self, env: object) -> None:
        values = [
            f"({order_id}, {1 + order_id % 47}, DATE('2026-07-{1 + order_id % 28:02d}'), "
            f"'{('paid', 'pending', 'review', 'cancelled')[order_id % 4]}', "
            f"{100 + order_id % 997}.00, 'hc06-checkout-order')"
            for order_id in range(1, 801)
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.orders_table} (order_id, tenant_id, order_day, status, amount, payload) VALUES ",
            values,
            "load HC06 orders",
        )
        values = [
            f"({10_000 + order_id}, {order_id}, '{('settled', 'pending', 'refunded')[order_id % 3]}', "
            f"{80 + order_id % 431}.00, DATE('2026-07-{1 + order_id % 28:02d}'), 'hc06-payment-ledger')"
            for order_id in range(1, 801)
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.payments_table} (payment_id, order_id, payment_state, amount, paid_day, payload) VALUES ",
            values,
            "load HC06 payments",
        )
        values = [
            f"({sku_id}, {1 + sku_id % 12}, {20 + sku_id % 180}, {30 + sku_id % 45}, 'hc06-inventory-snapshot')"
            for sku_id in range(1, 241)
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.inventory_table} (sku_id, warehouse_id, available_qty, reorder_point, payload) VALUES ",
            values,
            "load HC06 inventory",
        )
        values = [
            f"({event_id}, {1 + event_id % 370}, '{('checkout', 'login', 'refund', 'shipment', 'support')[event_id % 5]}', "
            f"DATE('2026-07-{1 + event_id % 28:02d}'), 'hc06-customer-event')"
            for event_id in range(1, 1201)
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.events_table} (event_id, customer_id, event_type, event_day, payload) VALUES ",
            values,
            "load HC06 events",
        )

    def _insert_batches(self, env: object, prefix: str, values: list[str], context: str) -> None:
        for start in range(0, len(values), 200):
            batch = values[start:start + 200]
            self._execute(env, prefix + ",".join(batch), f"{context} rows {start + 1}-{start + len(batch)}")

    def _create_source_files(self) -> tuple[list[tuple], str]:
        if self.source_root is None:
            raise RuntimeError("HC06 source root is not initialized")
        columns = "order_id,tenant_id,order_day,amount,status,payload"
        rows = []
        all_ids: set[int] = set()
        for file_id in range(1, self.source_file_count + 1):
            order_ids = list(range(1 + (file_id - 1) * 400, 1 + file_id * 400))
            if file_id == 4:
                order_ids[0] = 1200
            if file_id == 6:
                order_ids[0], order_ids[1] = order_ids[1], order_ids[0]
            path = self.source_root / f"{self.db}.{self.target_table}.{file_id:03d}.csv"
            path.write_text(
                "\n".join(
                    [
                        columns,
                        *(
                            f"{order_id},{1 + order_id % 47},2026-07-{1 + order_id % 28:02d},"
                            f"{100 + order_id % 997}.00,{('paid', 'pending', 'review')[order_id % 3]},hc06-source"
                            for order_id in order_ids
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            overlap = len(all_ids.intersection(order_ids))
            all_ids.update(order_ids)
            rows.append(
                (
                    file_id,
                    str(path),
                    digest,
                    digest,
                    path.stat().st_size,
                    len(order_ids),
                    "utf-8",
                    "csv",
                    int(order_ids == sorted(order_ids)),
                    overlap,
                    columns,
                    "source_filesystem",
                )
            )
        digest = hashlib.sha256(
            "\n".join(f"{row[0]}:{row[2]}" for row in rows).encode("utf-8")
        ).hexdigest()
        return rows, digest

    def _create_raw_tables(self, env: object) -> None:
        statements = (
            (
                f"CREATE TABLE {self.db}.{self.source_manifest_table} ("
                "file_id INT PRIMARY KEY, file_path VARCHAR(255) NOT NULL, sha256 CHAR(64) NOT NULL, "
                "observed_sha256 CHAR(64) NOT NULL, file_size_bytes BIGINT NOT NULL, source_rows INT NOT NULL, "
                "file_charset VARCHAR(32) NOT NULL, file_format VARCHAR(32) NOT NULL, sorted_key TINYINT NOT NULL, "
                "duplicate_key_count INT NOT NULL, columns_signature VARCHAR(255) NOT NULL, source VARCHAR(128) NOT NULL)",
                "create HC06 raw source manifest",
            ),
            (
                f"CREATE TABLE {self.db}.{self.capacity_table} ("
                "observation_id INT PRIMARY KEY, scope VARCHAR(64) NOT NULL, metric_name VARCHAR(64) NOT NULL, "
                "raw_size_bytes BIGINT NOT NULL, encoded_kv_bytes BIGINT NOT NULL, sort_amplification DECIMAL(8,3) NOT NULL, "
                "temp_headroom_bytes BIGINT NOT NULL, replica_factor INT NOT NULL, compaction_headroom_bytes BIGINT NOT NULL, "
                "available_bytes BIGINT NOT NULL, required_bytes BIGINT NOT NULL, unit VARCHAR(16) NOT NULL, "
                "sample_window VARCHAR(64) NOT NULL, source VARCHAR(128) NOT NULL)",
                "create HC06 raw capacity inventory",
            ),
            (
                f"CREATE TABLE {self.db}.{self.permissions_table} ("
                "permission_id INT PRIMARY KEY, plan_id VARCHAR(96) NOT NULL, phase VARCHAR(32) NOT NULL, "
                "principal VARCHAR(64) NOT NULL, checkpoint_id INT NOT NULL, object_name VARCHAR(128) NOT NULL, "
                "privilege_name VARCHAR(64) NOT NULL, observed_state VARCHAR(64) NOT NULL, source VARCHAR(128) NOT NULL)",
                "create HC06 raw permission inventory",
            ),
            (
                f"CREATE TABLE {self.db}.{self.target_catalog_table} ("
                "catalog_id INT PRIMARY KEY, table_name VARCHAR(128) NOT NULL, plan_id VARCHAR(96) NOT NULL, "
                "phase VARCHAR(32) NOT NULL, target_role VARCHAR(32) NOT NULL, row_count BIGINT NOT NULL, "
                "region_count INT NOT NULL, region_state VARCHAR(64) NOT NULL, parallel_import TINYINT NOT NULL, "
                "column_signature VARCHAR(255) NOT NULL, pk_signature VARCHAR(128) NOT NULL, source VARCHAR(128) NOT NULL)",
                "create HC06 raw target catalog",
            ),
            (
                f"CREATE TABLE {self.db}.{self.conflict_table} ("
                "inventory_id INT PRIMARY KEY, feature VARCHAR(32) NOT NULL, component VARCHAR(96) NOT NULL, "
                "state VARCHAR(64) NOT NULL, mode VARCHAR(64) NOT NULL, target_scope VARCHAR(128) NOT NULL, "
                "observed_at VARCHAR(64) NOT NULL, source VARCHAR(128) NOT NULL)",
                "create HC06 raw protection inventory",
            ),
            (
                f"CREATE TABLE {self.db}.{self.checkpoint_table} ("
                "checkpoint_id INT PRIMARY KEY, checkpoint_name VARCHAR(96) NOT NULL, plan_id VARCHAR(96) NOT NULL, "
                "phase VARCHAR(32) NOT NULL, target_table VARCHAR(128) NOT NULL, driver VARCHAR(32) NOT NULL, "
                "persistence VARCHAR(32) NOT NULL, container_ephemeral TINYINT NOT NULL, schema_hash CHAR(64) NOT NULL, "
                "source_manifest_digest CHAR(64) NOT NULL, last_state VARCHAR(32) NOT NULL, resume_safe TINYINT NOT NULL, "
                "source VARCHAR(128) NOT NULL)",
                "create HC06 raw checkpoint inventory",
            ),
            (
                f"CREATE TABLE {self.db}.{self.plan_table} ("
                "plan_id VARCHAR(96) PRIMARY KEY, review_key VARCHAR(96) NOT NULL, phase VARCHAR(32) NOT NULL, "
                "plan_state VARCHAR(32) NOT NULL, request_id VARCHAR(96) NOT NULL, source_manifest_digest CHAR(64) NOT NULL, "
                "created_at VARCHAR(64) NOT NULL, source VARCHAR(128) NOT NULL)",
                "create HC06 raw plan inventory",
            ),
            (
                f"CREATE TABLE {self.db}.{self.precheck_table} ("
                "precheck_id INT PRIMARY KEY, binary_version VARCHAR(32) NOT NULL, binary_commit CHAR(40) NOT NULL, "
                "binary_image VARCHAR(255) NOT NULL, config_digest CHAR(64) NOT NULL, command_line TEXT NOT NULL, "
                "exit_code INT NOT NULL, stdout LONGTEXT NOT NULL, stderr LONGTEXT NOT NULL, target_rows_before BIGINT NOT NULL, "
                "target_rows_after BIGINT NOT NULL, loader_process_count INT NOT NULL, source_manifest_digest CHAR(64) NOT NULL)",
                "create HC06 raw Lightning precheck table",
            ),
            (
                f"CREATE TABLE {self.db}.{self.facts_table} ("
                "fact_key VARCHAR(64) PRIMARY KEY, fact_value VARCHAR(255) NOT NULL, source VARCHAR(128) NOT NULL)",
                "create HC06 raw fact table",
            ),
            (
                f"CREATE TABLE {self.db}.{self.cluster_table} ("
                "inventory_id INT PRIMARY KEY, component VARCHAR(32) NOT NULL, identity_name VARCHAR(128) NOT NULL, "
                "state VARCHAR(64) NOT NULL, region_count INT NOT NULL, leader_count INT NOT NULL, raw_payload LONGTEXT NOT NULL, "
                "source VARCHAR(128) NOT NULL)",
                "create HC06 raw PD inventory",
            ),
            (
                f"CREATE TABLE {self.db}.{self.review_table} ("
                "review_key VARCHAR(96) PRIMARY KEY, status VARCHAR(32) NOT NULL, decision VARCHAR(32) NOT NULL, "
                "plan_id VARCHAR(96) NOT NULL, phase VARCHAR(32) NOT NULL, principal VARCHAR(64) NOT NULL, checkpoint_id INT NOT NULL, "
                "target_table VARCHAR(128) NOT NULL, target_row_count BIGINT NOT NULL, source_manifest_digest CHAR(64) NOT NULL, "
                "source_file_count INT NOT NULL, business_checksum BIGINT NOT NULL, evidence_refs TEXT NOT NULL, "
                "safety_boundary TEXT NOT NULL, verification TEXT NOT NULL, "
                "source_status VARCHAR(32) NOT NULL, capacity_status VARCHAR(32) NOT NULL, "
                "permission_status VARCHAR(32) NOT NULL, target_status VARCHAR(32) NOT NULL, "
                "protection_status VARCHAR(32) NOT NULL, checkpoint_status VARCHAR(32) NOT NULL, "
                "precheck_status VARCHAR(32) NOT NULL, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
                "create HC06 review artifact table",
            ),
        )
        for statement, label in statements:
            self._execute(env, statement, label)

    def _insert_source_manifest(self, env: object, rows: list[tuple]) -> None:
        values = [
            "(%d, '%s', '%s', '%s', %d, %d, '%s', '%s', %d, %d, '%s', '%s')"
            % tuple(sql_escape(value) if isinstance(value, str) else value for value in row)
            for row in rows
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.source_manifest_table} "
            "(file_id, file_path, sha256, observed_sha256, file_size_bytes, source_rows, file_charset, file_format, "
            "sorted_key, duplicate_key_count, columns_signature, source) VALUES ",
            values,
            "insert HC06 raw source manifest",
        )

    def _insert_capacity(self, env: object) -> None:
        raw_size = sum(path.stat().st_size for path in self.source_root.glob(f"{self.db}.{self.target_table}.*.csv"))
        rows = [
            (1, "lightning_local_sort", "filesystem_free", raw_size, raw_size * 2, 1.5, 2**30, 1, 0, 18 * 2**30, 24 * 2**30, "bytes", "preflight-window", "capacity-plan"),
            (2, "tikv_cluster", "replicated_free", raw_size, raw_size * 2, 1.0, 0, 3, 20 * 2**30, 89 * 2**30, 120 * 2**30, "bytes", "preflight-window", "pd-store-capacity-snapshot"),
            (3, "tikv/store-0", "free", raw_size, raw_size * 2, 1.0, 0, 3, 0, 31 * 2**30, 40 * 2**30, "bytes", "preflight-window", "pd-store-capacity-snapshot"),
            (4, "tikv/store-1", "free", raw_size, raw_size * 2, 1.0, 0, 3, 0, 30 * 2**30, 40 * 2**30, "bytes", "preflight-window", "pd-store-capacity-snapshot"),
            (5, "tikv/store-2", "free", raw_size, raw_size * 2, 1.0, 0, 3, 0, 28 * 2**30, 40 * 2**30, "bytes", "preflight-window", "pd-store-capacity-snapshot"),
            (6, "tidb_sql", "filesystem_free", raw_size, raw_size, 1.0, 0, 1, 0, 8 * 2**30, 4 * 2**30, "bytes", "preflight-window", "node-filesystem-snapshot"),
            (7, "pd_metadata", "filesystem_free", raw_size, raw_size, 1.0, 0, 1, 0, 12 * 2**30, 2 * 2**30, "bytes", "preflight-window", "node-filesystem-snapshot"),
            (8, "backup_staging", "filesystem_free", raw_size, raw_size, 1.0, 0, 1, 0, 55 * 2**30, 20 * 2**30, "bytes", "preflight-window", "backup-snapshot"),
        ]
        values = [
            "(%d, '%s', '%s', %d, %d, %.3f, %d, %d, %d, %d, %d, '%s', '%s', '%s')"
            % row
            for row in rows
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.capacity_table} "
            "(observation_id, scope, metric_name, raw_size_bytes, encoded_kv_bytes, sort_amplification, temp_headroom_bytes, "
            "replica_factor, compaction_headroom_bytes, available_bytes, required_bytes, unit, sample_window, source) VALUES ",
            values,
            "insert HC06 raw capacity inventory",
        )

    def _insert_plan_inventory(self, env: object, manifest_digest: str) -> None:
        rows = [
            (self.active_plan_id, self.review_key, self.active_plan_phase, "scheduled", "hc06-request-current", manifest_digest, "2026-08-19T10:00:00Z", "change-control"),
            ("checkout-ledger-physical-v2", self.review_key, "retry", "superseded", "hc06-request-retry", "old-manifest-digest", "2026-08-18T10:00:00Z", "change-control"),
            ("checkout-ledger-parallel-stage-v1", self.review_key, "exception-review", "proposed", "hc06-request-parallel", manifest_digest, "2026-08-19T09:00:00Z", "change-control"),
        ]
        values = [
            "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
            % tuple(sql_escape(value) for value in row)
            for row in rows
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.plan_table} (plan_id, review_key, phase, plan_state, request_id, source_manifest_digest, created_at, source) VALUES ",
            values,
            "insert HC06 raw plan inventory",
        )

    def _insert_permissions(self, env: object) -> None:
        rows = [
            (1, self.active_plan_id, self.active_plan_phase, self.active_plan_principal, self.active_checkpoint_id, f"{self.db}.{self.source_manifest_table}", "SELECT", "granted", "grant-audit"),
            (2, self.active_plan_id, self.active_plan_phase, self.active_plan_principal, self.active_checkpoint_id, f"{self.db}.{self.target_table}", "SELECT", "granted", "grant-audit"),
            (3, self.active_plan_id, self.active_plan_phase, self.active_plan_principal, self.active_checkpoint_id, f"{self.db}.{self.checkpoint_table}", "SELECT,INSERT,UPDATE", "granted", "grant-audit"),
            (4, self.active_plan_id, self.active_plan_phase, self.active_plan_principal, self.active_checkpoint_id, "local-sort-directory", "FILE", "read_only", "driver-policy"),
            (5, self.active_plan_id, self.active_plan_phase, self.active_plan_principal, self.active_checkpoint_id, "pd-admin-api", "ADMIN", "read_only_token", "service-policy"),
            (6, self.active_plan_id, self.active_plan_phase, self.active_plan_principal, 1, f"{self.db}.{self.target_table}", "SELECT", "granted", "grant-audit"),
            (7, self.active_plan_id, self.active_plan_phase, self.active_plan_principal, 1, f"{self.db}.{self.checkpoint_table}", "SELECT,INSERT,UPDATE", "granted", "grant-audit"),
            (8, self.active_plan_id, self.active_plan_phase, self.active_plan_principal, 2, f"{self.db}.{self.target_table}", "SELECT", "denied", "driver-policy"),
            (9, self.active_plan_id, self.active_plan_phase, self.active_plan_principal, 3, f"{self.db}.{self.target_table}", "SELECT", "denied", "driver-policy"),
            (10, self.active_plan_id, "retry", "loader-old-shadow", 1, f"{self.db}.{self.target_table}", "SELECT", "expired", "grant-audit"),
            (11, "checkout-ledger-parallel-stage-v1", "exception-review", self.active_plan_principal, 2, f"{self.db}.hc06_orders_shadow", "SELECT", "granted", "grant-audit"),
            (12, "warehouse-replay-logical-v1", "logical", "reporting-readonly", 0, f"{self.db}.{self.inventory_table}", "SELECT", "granted", "grant-audit"),
            (13, "warehouse-replay-logical-v1", "logical", "analytics-changefeed", 0, f"{self.db}.{self.events_table}", "SELECT", "granted", "grant-audit"),
        ]
        values = [
            "(%d, '%s', '%s', '%s', %d, '%s', '%s', '%s', '%s')"
            % tuple(sql_escape(value) if isinstance(value, str) else value for value in row)
            for row in rows
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.permissions_table} (permission_id, plan_id, phase, principal, checkpoint_id, object_name, privilege_name, observed_state, source) VALUES ",
            values,
            "insert HC06 raw permission inventory",
        )

    def _insert_target_catalog(self, env: object) -> None:
        order_signature = "order_id:BIGINT|tenant_id:INT|order_day:DATE|status:VARCHAR|amount:DECIMAL|payload:VARCHAR"
        rows = [
            (1, self.target_table, self.active_plan_id, self.active_plan_phase, "destination", 800, 9, "normal", 0, order_signature, "PRIMARY(order_id)", "target-catalog"),
            (2, f"{self.target_table}_stage", self.active_plan_id, self.active_plan_phase, "staging", 0, 1, "normal", 1, "order_id:BIGINT|payload:VARCHAR", "PRIMARY(order_id)", "target-catalog"),
            (3, self.target_table, "checkout-ledger-physical-v2", "retry", "destination", 0, 0, "not-created", 0, order_signature, "PRIMARY(order_id)", "target-catalog"),
            (4, "hc06_orders_shadow", "checkout-ledger-parallel-stage-v1", "exception-review", "destination", 0, 1, "normal", 1, "order_id:BIGINT|payload:VARCHAR", "PRIMARY(order_id)", "target-catalog"),
            (5, self.payments_table, "business-ledger-steady-v1", "steady", "protected_business", 800, 9, "normal", 0, "payment_id:BIGINT|order_id:BIGINT|payment_state:VARCHAR|amount:DECIMAL|paid_day:DATE|payload:VARCHAR", "PRIMARY(payment_id)", "target-catalog"),
            (6, self.inventory_table, "business-ledger-steady-v1", "steady", "protected_business", 240, 9, "normal", 0, "sku_id:BIGINT|warehouse_id:INT|available_qty:INT|reorder_point:INT|payload:VARCHAR", "PRIMARY(sku_id)", "target-catalog"),
            (7, self.events_table, "business-ledger-steady-v1", "steady", "protected_business", 1200, 9, "normal", 0, "event_id:BIGINT|customer_id:BIGINT|event_type:VARCHAR|event_day:DATE|payload:VARCHAR", "PRIMARY(event_id)", "target-catalog"),
        ]
        values = [
            "(%d, '%s', '%s', '%s', '%s', %d, %d, '%s', %d, '%s', '%s', '%s')"
            % tuple(sql_escape(value) if isinstance(value, str) else value for value in row)
            for row in rows
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.target_catalog_table} (catalog_id, table_name, plan_id, phase, target_role, row_count, region_count, region_state, parallel_import, column_signature, pk_signature, source) VALUES ",
            values,
            "insert HC06 raw target catalog",
        )

    def _insert_protection_inventory(self, env: object) -> None:
        rows = [
            (1, "PITR", "pitr-service", "enabled", "log-backup-retention", self.target_table, "2026-08-19T10:00:00Z", "pitr-controller"),
            (2, "TiCDC", "changefeed-analytics", "normal", "running", self.target_table, "2026-08-19T10:00:00Z", "changefeed-controller"),
            (3, "BR", "nightly-backup", "idle", "last-success", "cluster", "2026-08-19T09:30:00Z", "br-controller"),
            (4, "GC", "gc-safepoint", "healthy", "headroom-41m", "cluster", "2026-08-19T10:00:00Z", "gc-status"),
            (5, "TiCDC", "changefeed-shadow", "stopped", "not-selected", "cluster", "2026-08-19T10:00:00Z", "changefeed-controller"),
            (6, "PITR", "archive-shadow", "disabled", "not-selected", "cluster", "2026-08-19T10:00:00Z", "pitr-controller"),
            (7, "DDL", "schema-owner", "idle", "no-active-job", self.target_table, "2026-08-19T10:00:00Z", "ddl-history"),
            (8, "Scheduler", "store-balance", "normal", "no-pending-operator", "cluster", "2026-08-19T10:00:00Z", "pd-status"),
        ]
        values = [
            "(%d, '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
            % tuple(sql_escape(value) if isinstance(value, str) else value for value in row)
            for row in rows
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.conflict_table} (inventory_id, feature, component, state, mode, target_scope, observed_at, source) VALUES ",
            values,
            "insert HC06 raw protection inventory",
        )

    def _insert_checkpoint_state(self, env: object, manifest_digest: str) -> None:
        schema_hash = hashlib.sha256(b"hc06-lightning-schema-v1").hexdigest()
        rows = [
            (1, "hc06-precheck-mysql-retry", "checkout-ledger-physical-v2", "retry", self.target_table, "mysql", "durable", 0, hashlib.sha256(b"hc06-lightning-schema-v0").hexdigest(), "old-manifest-digest", "ready", 1, "checkpoint-inventory"),
            (2, "hc06-precheck-file-shadow", self.active_plan_id, self.active_plan_phase, self.target_table, "file", "ephemeral", 1, schema_hash, manifest_digest, "stale", 0, "checkpoint-inventory"),
            (3, "hc06-precheck-s3-shadow", self.active_plan_id, self.active_plan_phase, self.target_table, "s3", "durable", 0, hashlib.sha256(b"hc06-lightning-schema-v0").hexdigest(), "old-manifest-digest", "stale", 0, "checkpoint-inventory"),
            (self.active_checkpoint_id, "hc06-precheck-mysql", self.active_plan_id, self.active_plan_phase, self.target_table, "mysql", "durable", 0, schema_hash, manifest_digest, "ready", 1, "checkpoint-inventory"),
        ]
        values = [
            "(%d, '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%s', %d, '%s')"
            % tuple(sql_escape(value) if isinstance(value, str) else value for value in row)
            for row in rows
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.checkpoint_table} (checkpoint_id, checkpoint_name, plan_id, phase, target_table, driver, persistence, container_ephemeral, schema_hash, source_manifest_digest, last_state, resume_safe, source) VALUES ",
            values,
            "insert HC06 raw checkpoint inventory",
        )

    def _insert_facts(self, env: object, manifest_digest: str) -> None:
        schema_hash = hashlib.sha256(b"hc06-lightning-schema-v1").hexdigest()
        rows = [
            ("manifest_digest", manifest_digest, "source-manifest"),
            ("schema_hash", schema_hash, "schema-catalog"),
            ("source_file_count", str(self.source_file_count), "source-manifest"),
            ("business_checksum", str(self.business_checksum), "business-crc"),
            ("source_root", str(self.source_root), "source-filesystem"),
        ]
        values = [
            "('%s', '%s', '%s')" % tuple(sql_escape(value) for value in row)
            for row in rows
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.facts_table} (fact_key, fact_value, source) VALUES ",
            values,
            "insert HC06 raw facts",
        )

    def _capture_cluster_inventory(self, env: object) -> None:
        stores = env.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
        rows = []
        for index, store in enumerate(stores, start=1):
            store_record = store["store"]
            store_id = int(store_record["id"])
            regions = env.deployment.pd_request("GET", f"/pd/api/v1/regions/store/{store_id}")["regions"]
            leaders = sum(1 for region in regions if int(region["leader"]["store_id"]) == store_id)
            payload = json.dumps({"store": store, "regions": regions}, sort_keys=True)
            rows.append(
                (
                    index,
                    "tikv",
                    f"store-{store_id}",
                    str(store_record["state_name"]),
                    len(regions),
                    leaders,
                    payload,
                    "pd-api-v1",
                )
            )
        values = [
            "(%d, '%s', '%s', '%s', %d, %d, '%s', '%s')"
            % tuple(sql_escape(value) if isinstance(value, str) else value for value in row)
            for row in rows
        ]
        self._insert_batches(
            env,
            f"INSERT INTO {self.db}.{self.cluster_table} (inventory_id, component, identity_name, state, region_count, leader_count, raw_payload, source) VALUES ",
            values,
            "insert HC06 raw PD inventory",
        )

    def _insert_review(self, env: object) -> None:
        self._execute(
            env,
            f"INSERT INTO {self.db}.{self.review_table} (review_key, status, decision, plan_id, phase, principal, checkpoint_id, target_table, target_row_count, source_manifest_digest, source_file_count, business_checksum, evidence_refs, safety_boundary, verification, source_status, capacity_status, permission_status, target_status, protection_status, checkpoint_status, precheck_status) VALUES ("
            f"'{self.review_key}', 'open', 'pending', '', '', '', 0, '{self.target_table}', 0, '', 0, 0, '', '', '', 'pending', 'pending', 'pending', 'pending', 'pending', 'pending', 'pending')",
            "insert HC06 open review",
        )

    def _refresh_manifest(self, env: object) -> None:
        rows = self._rows(
            env,
            f"SELECT file_id, file_path, sha256 FROM {self.db}.{self.source_manifest_table} ORDER BY file_id",
            "read HC06 source manifest",
        )
        if len(rows) != self.source_file_count:
            raise RuntimeError(
                f"HC06 source manifest row count mismatch: expected={self.source_file_count}, actual={len(rows)}"
            )
        for file_id, file_path, expected_digest in rows:
            observed_digest = hashlib.sha256(Path(str(file_path)).read_bytes()).hexdigest()
            self._execute(
                env,
                f"UPDATE {self.db}.{self.source_manifest_table} SET observed_sha256 = '{observed_digest}' "
                f"WHERE file_id = {int(file_id)}",
                f"refresh HC06 source digest {file_id}",
            )

    def _rebind_manifest(self, env: object, rows: list[tuple]) -> None:
        for file_id, file_path, digest, *_ in rows:
            self._execute(
                env,
                f"UPDATE {self.db}.{self.source_manifest_table} SET file_path = '{sql_escape(file_path)}', "
                f"sha256 = '{digest}', observed_sha256 = '{digest}' WHERE file_id = {int(file_id)}",
                f"rebind HC06 source file {file_id}",
            )

    def _write_lightning_config(self) -> None:
        if self.config_path is None or self.sorted_root is None or self.checkpoint_root is None:
            raise RuntimeError("HC06 Lightning paths are not initialized")
        self.config_path.write_text(
            "\n".join(
                (
                    "[lightning]",
                    'level = "info"',
                    "check-requirements = true",
                    "region-concurrency = 2",
                    "",
                    "[checkpoint]",
                    "enable = true",
                    'driver = "file"',
                    f'dsn = "/var/lib/lightning/checkpoint/checkpoint.pb"',
                    "",
                    "[tidb]",
                    'host = "tidb-0"',
                    "port = 4000",
                    "status-port = 10080",
                    'user = "root"',
                    'password = ""',
                    'pd-addr = "pd-0:2379,pd-1:2379,pd-2:2379"',
                    "",
                    "[mydumper]",
                    'data-source-dir = "/var/lib/lightning/source"',
                    "strict-format = true",
                    "no-schema = true",
                    "",
                    "[mydumper.csv]",
                    "header = true",
                    'separator = ","',
                    "",
                    "[tikv-importer]",
                    'backend = "local"',
                    'sorted-kv-dir = "/var/lib/lightning/sorted-kv"',
                    "parallel-import = false",
                    "",
                    "[post-restore]",
                    'checksum = "off"',
                    'analyze = "off"',
                )
            )
            + "\n",
            encoding="ascii",
        )

    def _precheck_command(self) -> list[str]:
        if self.config_path is None or self.source_root is None or self.sorted_root is None or self.checkpoint_root is None:
            raise RuntimeError("HC06 Lightning paths are not initialized")
        network = self.env.deployment.network_name
        return [
            "run",
            "--name", self.precheck_container,
            "--network", network,
            "--user", f"{os.getuid()}:{os.getgid()}",
            "--cpus", "1.0",
            "--memory", "1g",
            "-v", f"{self.config_path}:/var/lib/lightning/lightning.toml:ro",
            "-v", f"{self.source_root}:/var/lib/lightning/source:ro",
            "-v", f"{self.sorted_root}:/var/lib/lightning/sorted-kv",
            "-v", f"{self.checkpoint_root}:/var/lib/lightning/checkpoint",
            "--rm",
            LIGHTNING_IMAGE,
            "/tidb-lightning",
            "--config", "/var/lib/lightning/lightning.toml",
            "--log-file", "-",
            "--d", "/var/lib/lightning/source",
            "--no-schema",
            "--pd-urls", "pd-0:2379,pd-1:2379,pd-2:2379",
            "--tidb-host", "tidb-0",
            "--tidb-port", "4000",
            "--tidb-status", "10080",
            "--tidb-user", "root",
            "--backend", "local",
            "--sorted-kv-dir", "/var/lib/lightning/sorted-kv",
            "--enable-checkpoint",
            "--checksum", "off",
            "--analyze", "off",
        ]

    @staticmethod
    def _run_docker(command: list[str]) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(
                ["docker", *command],
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"HC06 Lightning precheck timed out: command={command!r}") from exc
        except OSError as exc:
            raise RuntimeError(f"HC06 cannot execute Docker for Lightning precheck: command={command!r}") from exc
        return result

    def _loader_process_count(self) -> int:
        if self.precheck_container is None:
            raise RuntimeError("HC06 precheck container name is not initialized")
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={self.precheck_container}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return len([line for line in result.stdout.splitlines() if line.strip()])

    def _assert_no_loader(self) -> None:
        if self._loader_process_count() != 0:
            raise RuntimeError(f"HC06 loader process is still running: container={self.precheck_container!r}")

    def _target_rows(self) -> int:
        rows = self._rows(
            self.env,
            f"SELECT COUNT(*) FROM {self.db}.{self.target_table}",
            "read HC06 target row count",
        )
        if len(rows) != 1:
            raise RuntimeError(f"HC06 target row count cardinality mismatch: rows={rows!r}")
        return int(rows[0][0])

    def _verify_state(self, env: object) -> None:
        expected = {
            self.orders_table: 800,
            self.payments_table: 800,
            self.inventory_table: 240,
            self.events_table: 1200,
            self.source_manifest_table: self.source_file_count,
            self.capacity_table: 8,
            self.plan_table: 3,
            self.permissions_table: 13,
            self.target_catalog_table: 7,
            self.conflict_table: 8,
            self.checkpoint_table: 4,
            self.facts_table: 5,
            self.cluster_table: len(env.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]),
            self.precheck_table: 1,
            self.review_table: 1,
        }
        for table, count in expected.items():
            rows = self._rows(env, f"SELECT COUNT(*) FROM {self.db}.{table}", f"verify HC06 raw table {table}")
            if len(rows) != 1 or int(rows[0][0]) != count:
                raise RuntimeError(
                    f"HC06 raw table state mismatch: table={table!r}, expected={count}, rows={rows!r}"
                )


class TidbHealthCheckLightningPreflightScenario(TiDBScenario):
    scenario_id = "tidb_health_check_lightning_preflight"
    description = (
        "TiDB v8.1 Lightning preflight review that joins raw plan, source, capacity, PD, protection, "
        "permission and checkpoint evidence before a physical import."
    )
    cases = (_HC06_CASE, _NEW_CASE)

    def build_fault_plan(self, case: TidbHealthCheckLightningPreflightCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbHealthCheckLightningPreflightInjector,
                config={
                    "db": case.db,
                    "review_key": case.review_key,
                    "review_table": case.review_table,
                    "orders_table": case.orders_table,
                    "payments_table": case.payments_table,
                    "inventory_table": case.inventory_table,
                    "events_table": case.events_table,
                    "source_manifest_table": case.source_manifest_table,
                    "capacity_table": case.capacity_table,
                    "permissions_table": case.permissions_table,
                    "target_catalog_table": case.target_catalog_table,
                    "conflict_table": case.conflict_table,
                    "checkpoint_table": case.checkpoint_table,
                    "plan_table": case.plan_table,
                    "precheck_table": case.precheck_table,
                    "facts_table": case.facts_table,
                    "cluster_table": case.cluster_table,
                    "target_table": case.target_table,
                    "active_plan_id": case.active_plan_id,
                    "active_plan_phase": case.active_plan_phase,
                    "active_plan_principal": case.active_plan_principal,
                    "active_checkpoint_id": case.active_checkpoint_id,
                    "source_file_count": case.source_file_count,
                    "min_target_rows": case.min_target_rows,
                    "business_checksum": case.business_checksum,
                    "source_root_prefix": case.source_root_prefix,
                },
            ),
        )
