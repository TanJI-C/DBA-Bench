import hashlib

import json

import shlex

import subprocess

import time

from collections.abc import Mapping

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.system_failure.br_permission import (
    TidbSystemFailureBrPermissionEvaluatorCase,
    TidbSystemFailureBrPermissionFocusedEvaluatorCase,
)
from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.workloads.specs import WorkloadProfile

from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


_DATABASE = "benchops"
_TABLE = "admission_events"
_CREDENTIALS_TABLE = "backup_credentials"
_CREDENTIAL_GRANTS_TABLE = "backup_credential_scope_grants"
_AUTHORITY_LEASES_TABLE = "backup_authority_grant_leases"
_HISTORY_TABLE = "backup_job_history"
_BINDINGS_TABLE = "backup_runtime_bindings"
_WORKER_LEASES_TABLE = "backup_worker_leases"
_STORAGE_AUDIT_TABLE = "backup_storage_audit"
_WORKER_REGISTRY_TABLE = "backup_worker_registry"
_WORKER_MATERIALS_TABLE = "backup_worker_materials"
_JOB_DISPATCHES_TABLE = "backup_job_dispatches"
_DISPATCH_ROUTES_TABLE = "backup_dispatch_routes"
_REQUEST_CACHE_TABLE = "backup_request_material_cache"
_REQUEST_ATTEMPTS_TABLE = "backup_storage_request_attempts"

_TARGET_LEASE_TOKEN = "lt-4f7c9d2a"
_HEALTHY_LEASE_TOKEN = "lt-b91e6f40"
_REHEARSAL_LEASE_TOKEN = "lt-82a1e5c7"
_STALE_SIBLING_LEASE_TOKEN = "lt-3d6b8f11"
_REPORTING_LEASE_TOKEN = "lt-c0e4a712"
_ARCHIVE_LEASE_TOKEN = "lt-5a8d2f93"
_POST_HANDOFF_LEASE_TOKEN = "lt-e17b6c04"
_TARGET_AUTHORITY_EPOCH = "ep-4b8e2f19"
_TARGET_CHANGE_REF = "br-watch-20260801-2330-a1"
_AUTHORITY_HANDOFF_EPOCH = "ep-93d1c7a0"
_GENERATION_SHADOW_EPOCH = "ep-6c2a8f51"
_HEALTHY_AUTHORITY_EPOCH = "ep-7a2c1e60"
_REHEARSAL_AUTHORITY_EPOCH = "ep-1d8f4a62"
_STALE_SIBLING_AUTHORITY_EPOCH = "ep-5e9b3c74"
_REPORTING_AUTHORITY_EPOCH = "ep-2f6a8d03"
_ARCHIVE_AUTHORITY_EPOCH = "ep-8c1e5b47"
_POST_HANDOFF_AUTHORITY_EPOCH = "ep-a4d7c920"
_SUPERSEDED_AUTHORITY_EPOCH = "ep-b6f1d834"
_LATE_HANDOFF_AUTHORITY_EPOCH = "ep-c9e2f745"
_REQUEST_ROUTE_TOKEN = "rt-5e7c9b3a1d04"
_REQUEST_ASSIGNMENT_REPLAY_ROUTE_TOKEN = "rt-b37c8d12"
_REQUEST_CACHE_TOKEN = "c-7b4d9e1a2f60"
_FAILOVER_CACHE_TOKEN = "c-19d7a4e2"
_REQUEST_ASSIGNMENT_REPLAY_CACHE_TOKEN = "c-b37c8d12"
_PREFLIGHT_ATTEMPT_ID = "att-91d2e6b4"
_PREFLIGHT_LEASE_TOKEN = "lt-91d2e6b4"
_PREFLIGHT_AUTHORITY_LEASE_ID = 30
_PREFLIGHT_AUTHORITY_EPOCH = "ep-91d2e6b4"
_TARGET_ASSIGNMENT_ID = 10
_RETRY_ATTEMPT_ID = "att-b37c8d12"
_HEDGED_ATTEMPT_ID = "att-6e2a9f40"
_SECOND_CANDIDATE_ATTEMPT_ID = "att-8c4d1e73"
_FAILED_REQUEST_ATTEMPT_ID = "att-4a7f1c9e"
_HEDGED_ROUTE_TOKEN = "rt-6e2a9f40"
_HEDGED_CACHE_TOKEN = "c-6e2a9f40"
_HEDGED_LEASE_TOKEN = "lt-6e2a9f40"
_HEDGED_WORKER_HANDLE = "wh-7c2e9a41"
_HEDGED_EXECUTOR_HANDLE = "writer-slot-a"
_HEDGED_MATERIAL_HANDLE = "mh-6e2a9f40"
_HEDGED_AUTHORITY_LEASE_ID = 24
_HEDGED_AUTHORITY_EPOCH = "ep-6e2a9f40"
_HEDGED_CHANGE_REF = _TARGET_CHANGE_REF
_SECOND_CANDIDATE_ROUTE_TOKEN = "rt-8c4d1e73"
_SECOND_CANDIDATE_CACHE_TOKEN = "c-8c4d1e73"
_SECOND_CANDIDATE_LEASE_TOKEN = "lt-8c4d1e73"
_SECOND_CANDIDATE_WORKER_HANDLE = "wh-7c2e9a41"
_SECOND_CANDIDATE_EXECUTOR_HANDLE = "writer-slot-a"
_SECOND_CANDIDATE_MATERIAL_HANDLE = "mh-8c4d1e73"
_SECOND_CANDIDATE_AUTHORITY_LEASE_ID = 25
_SECOND_CANDIDATE_AUTHORITY_EPOCH = "ep-8c4d1e73"
_SECOND_CANDIDATE_CHANGE_REF = _TARGET_CHANGE_REF
_TARGET_WORKER_HANDLE = "wh-7c2e9a41"
_SHADOW_WORKER_HANDLE = "wh-3f8b1d70"
_TARGET_CACHE_AFFINITY = "ca-8f4d2a71"
_SHADOW_CACHE_AFFINITY = "ca-2b7e9c40"
_TARGET_MATERIAL_HANDLE = "mh-92dd7c4a"
_PRODUCTION_MATERIAL_HANDLE = "mh-6a6ba702"
_REHEARSAL_MATERIAL_HANDLE = "mh-d6rehearsal"
_REPORTING_MATERIAL_HANDLE = "mh-c0reporting"
_ARCHIVE_MATERIAL_HANDLE = "mh-5aarchive"
_EXTRA_CANDIDATE_1_ATTEMPT_ID = "att-9d5f2b60"
_EXTRA_CANDIDATE_1_ROUTE_TOKEN = "rt-9d5f2b60"
_EXTRA_CANDIDATE_1_CACHE_TOKEN = "c-9d5f2b60"
_EXTRA_CANDIDATE_1_LEASE_TOKEN = "lt-9d5f2b60"
_EXTRA_CANDIDATE_1_AUTHORITY_LEASE_ID = 26
_EXTRA_CANDIDATE_1_AUTHORITY_EPOCH = _TARGET_AUTHORITY_EPOCH
_EXTRA_CANDIDATE_1_MATERIAL_HANDLE = _TARGET_MATERIAL_HANDLE
_EXTRA_CANDIDATE_2_ATTEMPT_ID = "att-a1c7e3f5"
_EXTRA_CANDIDATE_2_ROUTE_TOKEN = "rt-a1c7e3f5"
_EXTRA_CANDIDATE_2_CACHE_TOKEN = "c-a1c7e3f5"
_EXTRA_CANDIDATE_2_LEASE_TOKEN = "lt-a1c7e3f5"
_EXTRA_CANDIDATE_2_AUTHORITY_LEASE_ID = 27
_EXTRA_CANDIDATE_2_AUTHORITY_EPOCH = "ep-a1c7e3f5"
_EXTRA_CANDIDATE_2_MATERIAL_HANDLE = _HEDGED_MATERIAL_HANDLE
_EXTRA_CANDIDATE_3_ATTEMPT_ID = "att-b2d8f4a6"
_EXTRA_CANDIDATE_3_ROUTE_TOKEN = "rt-b2d8f4a6"
_EXTRA_CANDIDATE_3_CACHE_TOKEN = "c-b2d8f4a6"
_EXTRA_CANDIDATE_3_LEASE_TOKEN = "lt-b2d8f4a6"
_EXTRA_CANDIDATE_3_AUTHORITY_LEASE_ID = 28
_EXTRA_CANDIDATE_3_AUTHORITY_EPOCH = _TARGET_AUTHORITY_EPOCH
_EXTRA_CANDIDATE_3_MATERIAL_HANDLE = _TARGET_MATERIAL_HANDLE
_EXTRA_CANDIDATE_4_ATTEMPT_ID = "att-c3e9a5b7"
_EXTRA_CANDIDATE_4_ROUTE_TOKEN = "rt-c3e9a5b7"
_EXTRA_CANDIDATE_4_CACHE_TOKEN = "c-c3e9a5b7"
_EXTRA_CANDIDATE_4_LEASE_TOKEN = "lt-c3e9a5b7"
_EXTRA_CANDIDATE_4_AUTHORITY_LEASE_ID = 29
_EXTRA_CANDIDATE_4_AUTHORITY_EPOCH = "ep-c3e9a5b7"
_EXTRA_CANDIDATE_4_MATERIAL_HANDLE = _SECOND_CANDIDATE_MATERIAL_HANDLE
_R61_CANDIDATE_1_ATTEMPT_ID = "att-d4f0a6c8"
_R61_CANDIDATE_1_ROUTE_TOKEN = "rt-d4f0a6c8"
_R61_CANDIDATE_1_CACHE_TOKEN = "c-d4f0a6c8"
_R61_CANDIDATE_1_LEASE_TOKEN = "lt-d4f0a6c8"
_R61_CANDIDATE_1_AUTHORITY_LEASE_ID = 31
_R61_CANDIDATE_1_AUTHORITY_EPOCH = "ep-d4f0a6c8"
_R61_CANDIDATE_1_MATERIAL_HANDLE = _TARGET_MATERIAL_HANDLE
_R61_CANDIDATE_2_ATTEMPT_ID = "att-e5a1b7d9"
_R61_CANDIDATE_2_ROUTE_TOKEN = "rt-e5a1b7d9"
_R61_CANDIDATE_2_CACHE_TOKEN = "c-e5a1b7d9"
_R61_CANDIDATE_2_LEASE_TOKEN = "lt-e5a1b7d9"
_R61_CANDIDATE_2_AUTHORITY_LEASE_ID = 32
_R61_CANDIDATE_2_AUTHORITY_EPOCH = "ep-e5a1b7d9"
_R61_CANDIDATE_2_MATERIAL_HANDLE = _HEDGED_MATERIAL_HANDLE
_R61_CANDIDATE_3_ATTEMPT_ID = "att-f6b2c8e0"
_R61_CANDIDATE_3_ROUTE_TOKEN = "rt-f6b2c8e0"
_R61_CANDIDATE_3_CACHE_TOKEN = "c-f6b2c8e0"
_R61_CANDIDATE_3_LEASE_TOKEN = "lt-f6b2c8e0"
_R61_CANDIDATE_3_AUTHORITY_LEASE_ID = 33
_R61_CANDIDATE_3_AUTHORITY_EPOCH = "ep-f6b2c8e0"
_R61_CANDIDATE_3_MATERIAL_HANDLE = _TARGET_MATERIAL_HANDLE
_R61_CANDIDATE_4_ATTEMPT_ID = "att-a7c3d9f1"
_R61_CANDIDATE_4_ROUTE_TOKEN = "rt-a7c3d9f1"
_R61_CANDIDATE_4_CACHE_TOKEN = "c-a7c3d9f1"
_R61_CANDIDATE_4_LEASE_TOKEN = "lt-a7c3d9f1"
_R61_CANDIDATE_4_AUTHORITY_LEASE_ID = 34
_R61_CANDIDATE_4_AUTHORITY_EPOCH = "ep-a7c3d9f1"
# r8: rotation-watch canary workers for the admission scope. They converged
# onto the production material after the rotation like the healthy sibling,
# so "which worker is currently serving what" requires revision/window
# discrimination across several converged chains before the failed request's
# worker can be pinned.
_WATCH4_LEASE_TOKEN = "lt-b4d81c20"
_WATCH5_LEASE_TOKEN = "lt-c95e2f37"
_WATCH4_AUTHORITY_EPOCH = "ep-b4d81c20"
_WATCH5_AUTHORITY_EPOCH = "ep-c95e2f37"
_WATCH4_ROUTE_TOKEN = "rt-b4d81c20"
_WATCH5_ROUTE_TOKEN = "rt-c95e2f37"
# r9: the rotation controller completed the epoch promotion after the lease
# tables were last written, so the paper trail keeps the pre-promotion epoch
# while the live epoch is only observable on the controller's event stream.
_LIVE_AUTHORITY_EPOCH = "ep-9f3ac7d1"
# r9: repeated denied writes on the backup prefix trip the bucket's automated
# denial-rate guard; the prefix stays quarantined until an operator releases
# the guard with the quarantine identity from the controller event stream.
_PREFIX_QUARANTINE_REF = "qg-7c2f81e9"
_QUARANTINE_TICKETS_TABLE = "backup_storage_quarantine_tickets"
_R61_CANDIDATE_4_MATERIAL_HANDLE = _SECOND_CANDIDATE_MATERIAL_HANDLE
_DECOY_CREDENTIAL_V5_ID = 230
_DECOY_CREDENTIAL_V6_ID = 231
_DECOY_CREDENTIAL_V4_SHADOW_ID = 232
_DECOY_V5_ACCESS_KEY = "admission-v5"
_DECOY_V6_ACCESS_KEY = "admission-v6"
_DECOY_V4_SHADOW_ACCESS_KEY = "admission-v4-shadow"
_DECOY_V5_MATERIAL_HANDLE = "mh-230shadow"
_DECOY_V6_MATERIAL_HANDLE = "mh-231shadow"
_DECOY_V4_SHADOW_MATERIAL_HANDLE = "mh-232shadow"
_DECOY_AUTHORITY_SHADOW_EPOCH = "ep-7d3a9b21"
_TARGET_ASSIGNMENT_FENCE = "af-target-sf06-2330"
_WATCH_REPLAY_ASSIGNMENT_FENCE = "af-2c7e9b41"
# The replay is inside the same scheduler fence; request_context_token is the
# request identity shared by the two execution attempts.
_REQUEST_ASSIGNMENT_REPLAY_FENCE = _TARGET_ASSIGNMENT_FENCE
_RETRY_ASSIGNMENT_FENCE = "af-retry-sf06-2359"
_TARGET_REQUEST_CONTEXT = "ctx-target-sf06-request"
_REQUEST_ASSIGNMENT_REPLAY_CONTEXT = _TARGET_REQUEST_CONTEXT
_WATCH_REPLAY_REQUEST_CONTEXT = "ctx-2c7e9b41"
_RETRY_REQUEST_CONTEXT = "ctx-retry-sf06-request"
_TARGET_REQUEST_STAGE = "backup_upload"
_TARGET_EXECUTION_PHASE = "dispatch_window"
_TARGET_EXECUTION_REASON = "storage-write"
_HANDOFF_EXECUTION_PHASE = _TARGET_EXECUTION_PHASE
_HANDOFF_EXECUTION_REASON = _TARGET_EXECUTION_REASON
_REPLAY_EXECUTION_PHASE = _TARGET_EXECUTION_PHASE
_REPLAY_EXECUTION_REASON = _TARGET_EXECUTION_REASON
_PREFLIGHT_ROUTE_TOKEN = "rt-91d2e6b4"
_PREFLIGHT_CACHE_TOKEN = "c-91d2e6b4"


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureBrPermissionForS3CredentialsDeniedScenarioCase(TiDBScenarioCase):
    database: str
    table: str
    credentials_table: str
    credential_grants_table: str
    authority_leases_table: str
    history_table: str
    bindings_table: str
    worker_leases_table: str
    storage_audit_table: str
    worker_registry_table: str
    worker_materials_table: str
    job_dispatches_table: str
    dispatch_routes_table: str
    request_cache_table: str
    request_attempts_table: str
    row_count: int
    expected_ranges: int
    effective_binding_id: int
    candidate_binding_id: int
    fault_credential_id: int
    correct_credential_id: int
    target_worker: str
    healthy_worker: str
    target_authority_lease_id: int
    target_authority_epoch: str
    desired_revision: int
    observed_revision: int
    entity_decoys: bool = False
    # r4: the focused authority model does not materialize the desired grant on
    # lease rows (sentinel 0); the refresh validator derives the unique
    # request-time-valid production grant from the grants window instead.
    derive_desired_from_grants: bool = False
    # r6: the focused authority broker answers every refresh identity-check
    # failure with one uniform rejection, so the passing combination cannot be
    # probed dimension by dimension through error feedback.
    uniform_refresh_rejection: bool = False
    # r9: the refresh validator verifies the authority epoch against the
    # controller's live promoted epoch (observable only on the job observe
    # event stream) instead of the stale lease-table epoch columns.
    epoch_from_observation: bool = False
    # r9: repeated denied writes trip the storage denial-rate guard; the
    # backup prefix stays quarantined until a bounded release presents the
    # quarantine identity. r11: the controller stream only announces the
    # quarantine itself; the guard issues the release ticket into its ticket
    # table on the first denied write, so the release identity cannot be
    # observed before the agent has attempted the denied write.
    storage_prefix_quarantine: bool = False
    live_authority_epoch: str | None = None
    prefix_quarantine_ref: str | None = None
    quarantine_tickets_table: str = _QUARANTINE_TICKETS_TABLE


_SF06_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="ledger_event_lookup",
            sql=(
                f"SELECT event_id, amount FROM {_DATABASE}.{_TABLE} "
                "WHERE tenant_id = 7 ORDER BY event_id DESC LIMIT 20"
            ),
            qps=0.55,
            tier="LIGHT",
            application_name="ledger-api",
        ),
        WorkloadProfile(
            name="ledger_dashboard_rollup",
            sql=(
                f"SELECT event_type, COUNT(*), SUM(amount) FROM {_DATABASE}.{_TABLE} "
                "GROUP BY event_type ORDER BY event_type"
            ),
            qps=0.28,
            tier="MEDIUM",
            application_name="ledger-dashboard",
        ),
        WorkloadProfile(
            name="ledger_reconciliation_rollup",
            sql=(
                f"SELECT tenant_id, COUNT(*), SUM(amount) FROM {_DATABASE}.{_TABLE} "
                "GROUP BY tenant_id ORDER BY tenant_id LIMIT 32"
            ),
            qps=0.22,
            tier="MEDIUM",
            application_name="reconciliation-worker",
        ),
        WorkloadProfile(
            name="backup_history_audit",
            sql=(
                f"SELECT job_id, status, ranges_failed, checksum_percent "
                f"FROM {_DATABASE}.{_HISTORY_TABLE} ORDER BY started_at DESC LIMIT 20"
            ),
            qps=0.42,
            tier="LIGHT",
            application_name="backup-audit",
        ),
        WorkloadProfile(
            name="ledger_payload_risk_probe",
            sql=(
                f"SELECT COUNT(*) FROM {_DATABASE}.{_TABLE} "
                "WHERE payload LIKE '%risk-7%'"
            ),
            qps=0.35,
            tier="LIGHT",
            application_name="risk-monitor",
        ),
        WorkloadProfile(
           name="backup_credential_inventory_audit",
           sql=(
               f"SELECT status, COUNT(*) FROM {_DATABASE}.{_CREDENTIALS_TABLE} "
               "GROUP BY status ORDER BY status"
           ),
           qps=0.24,
           tier="LIGHT",
           application_name="platform-audit",
       ),
        WorkloadProfile(
            name="ledger_recent_event_window",
            sql=(
                f"SELECT event_id, tenant_id, event_type, amount FROM {_DATABASE}.{_TABLE} "
                "WHERE event_id >= 700 ORDER BY event_id DESC LIMIT 50"
            ),
            qps=0.24,
            tier="LIGHT",
            application_name="ledger-api",
        ),
        WorkloadProfile(
            name="ledger_amount_bucket_rollup",
            sql=(
                f"SELECT CASE WHEN amount < 100 THEN 'small' "
                "WHEN amount < 500 THEN 'medium' ELSE 'large' END AS amount_bucket, "
                "COUNT(*), SUM(amount) "
                f"FROM {_DATABASE}.{_TABLE} GROUP BY amount_bucket ORDER BY amount_bucket"
            ),
            qps=0.18,
            tier="MEDIUM",
            application_name="ledger-dashboard",
        ),
        WorkloadProfile(
            name="ledger_payload_prefix_scan",
            sql=(
                f"SELECT LEFT(payload, 10), COUNT(*) FROM {_DATABASE}.{_TABLE} "
                "GROUP BY LEFT(payload, 10) ORDER BY COUNT(*) DESC LIMIT 20"
            ),
            qps=0.16,
            tier="MEDIUM",
            application_name="risk-monitor",
        ),
        WorkloadProfile(
            name="ledger_backup_join_reconciliation",
            sql=(
                f"SELECT e.event_type, h.status, COUNT(*) "
                f"FROM {_DATABASE}.{_TABLE} e JOIN {_DATABASE}.{_HISTORY_TABLE} h "
                "ON h.table_name = 'admission_events' "
                "WHERE h.job_id LIKE 'historical-br-%' "
                "GROUP BY e.event_type, h.status ORDER BY e.event_type, h.status"
            ),
            qps=0.12,
            tier="HEAVY",
            application_name="reconciliation-worker",
        ),
        WorkloadProfile(
            name="backup_history_failure_rollup",
            sql=(
                f"SELECT database_name, table_name, status, COUNT(*) "
                f"FROM {_DATABASE}.{_HISTORY_TABLE} "
                "GROUP BY database_name, table_name, status "
                "ORDER BY database_name, table_name, status"
            ),
            qps=0.24,
            tier="MEDIUM",
            application_name="backup-audit",
        ),
        WorkloadProfile(
            name="backup_history_object_prefix_sweep",
            sql=(
                f"SELECT storage_uri, COUNT(*), MAX(started_at) "
                f"FROM {_DATABASE}.{_HISTORY_TABLE} "
                "GROUP BY storage_uri ORDER BY MAX(started_at) DESC LIMIT 25"
            ),
            qps=0.18,
            tier="MEDIUM",
            application_name="backup-audit",
        ),
        WorkloadProfile(
            name="backup_recent_error_triage",
            sql=(
                f"SELECT job_id, storage_uri, error_text FROM {_DATABASE}.{_HISTORY_TABLE} "
                "WHERE status = 'error' ORDER BY started_at DESC LIMIT 20"
            ),
            qps=0.22,
            tier="LIGHT",
            application_name="backup-oncall",
        ),
        WorkloadProfile(
            name="backup_credential_rotation_audit",
            sql=(
                f"SELECT owner, status, COUNT(*), MAX(last_rotated) "
                f"FROM {_DATABASE}.{_CREDENTIALS_TABLE} "
                "GROUP BY owner, status ORDER BY owner, status"
            ),
            qps=0.20,
            tier="LIGHT",
            application_name="platform-audit",
        ),
        WorkloadProfile(
            name="backup_credential_scope_rollup",
            sql=(
                f"SELECT scope, status, COUNT(*) FROM {_DATABASE}.{_CREDENTIALS_TABLE} "
                "GROUP BY scope, status ORDER BY scope, status"
            ),
            qps=0.20,
            tier="MEDIUM",
            application_name="platform-audit",
        ),
        WorkloadProfile(
            name="backup_target_candidate_audit",
            sql=(
                f"SELECT c.credential_id, c.profile_name, c.status, c.last_rotated, "
                f"b.binding_state, b.role, b.effective_from "
                f"FROM {_DATABASE}.{_CREDENTIALS_TABLE} c "
                f"JOIN {_DATABASE}.{_BINDINGS_TABLE} b ON b.credential_id = c.credential_id "
                "WHERE b.target_scope = 'benchops.admission_events' "
                "ORDER BY b.effective_from DESC, c.last_rotated DESC LIMIT 20"
            ),
            qps=0.24,
            tier="LIGHT",
            application_name="ledger-platform",
        ),
        WorkloadProfile(
            name="ledger_tenant_amount_reconciliation",
            sql=(
                f"SELECT tenant_id, MIN(amount), MAX(amount), AVG(amount), COUNT(*) "
                f"FROM {_DATABASE}.{_TABLE} "
                "GROUP BY tenant_id ORDER BY tenant_id LIMIT 32"
            ),
            qps=0.18,
            tier="MEDIUM",
            application_name="reconciliation-worker",
        ),
        WorkloadProfile(
            name="backup_runtime_binding_watch",
            sql=(
                f"SELECT target_scope, binding_state, role, COUNT(*), MAX(effective_from) "
                f"FROM {_DATABASE}.{_BINDINGS_TABLE} "
                "GROUP BY target_scope, binding_state, role ORDER BY target_scope, binding_state, role"
            ),
            qps=0.30,
            tier="MEDIUM",
            application_name="backup-control-plane",
        ),
        WorkloadProfile(
            name="backup_effective_binding_lookup",
            sql=(
                f"SELECT b.binding_id, b.credential_id, b.role, b.binding_state, c.access_key "
                f"FROM {_DATABASE}.{_BINDINGS_TABLE} b "
                f"JOIN {_DATABASE}.{_CREDENTIALS_TABLE} c ON c.credential_id = b.credential_id "
                "WHERE b.target_scope = 'benchops.admission_events' AND b.binding_state IN ('effective', 'canary') "
                "ORDER BY b.effective_from DESC LIMIT 10"
            ),
            qps=0.28,
            tier="LIGHT",
            application_name="backup-control-plane",
        ),
        WorkloadProfile(
            name="backup_binding_propagation_audit",
            sql=(
                f"SELECT role, binding_state, COUNT(*), MIN(effective_from), MAX(effective_from) "
                f"FROM {_DATABASE}.{_BINDINGS_TABLE} "
                "WHERE target_scope = 'benchops.admission_events' "
                "GROUP BY role, binding_state ORDER BY role, binding_state"
            ),
            qps=0.25,
            tier="LIGHT",
            application_name="platform-audit",
        ),
        WorkloadProfile(
            name="backup_current_job_binding_join",
            sql=(
                f"SELECT h.job_id, h.status, c.profile_name, b.role, b.binding_state "
                f"FROM {_DATABASE}.{_HISTORY_TABLE} h "
                f"JOIN {_DATABASE}.{_BINDINGS_TABLE} b ON b.target_scope = CONCAT(h.database_name, '.', h.table_name) "
                f"JOIN {_DATABASE}.{_CREDENTIALS_TABLE} c ON c.credential_id = b.credential_id "
                "WHERE h.job_id LIKE 'sf06-br-%' ORDER BY h.started_at DESC LIMIT 10"
            ),
            qps=0.20,
            tier="MEDIUM",
            application_name="backup-oncall",
        ),
        WorkloadProfile(
            name="ledger_customer_segment_rollup",
            sql=(
                f"SELECT tenant_id, event_type, COUNT(*), AVG(amount) "
                f"FROM {_DATABASE}.{_TABLE} WHERE tenant_id BETWEEN 1 AND 16 "
                "GROUP BY tenant_id, event_type ORDER BY tenant_id, event_type"
            ),
            qps=0.24,
            tier="MEDIUM",
            application_name="customer-insights",
        ),
        WorkloadProfile(
            name="ledger_duplicate_risk_scan",
            sql=(
                f"SELECT payload, COUNT(*), SUM(amount) FROM {_DATABASE}.{_TABLE} "
                "GROUP BY payload HAVING COUNT(*) > 1 ORDER BY COUNT(*) DESC LIMIT 50"
            ),
            qps=0.18,
            tier="HEAVY",
            application_name="risk-monitor",
        ),
        WorkloadProfile(
            name="ledger_hourly_amount_window",
            sql=(
                f"SELECT event_type, SUM(amount), COUNT(*) FROM {_DATABASE}.{_TABLE} "
                "WHERE event_id BETWEEN 100 AND 900 GROUP BY event_type ORDER BY SUM(amount) DESC"
            ),
            qps=0.22,
            tier="MEDIUM",
            application_name="ledger-dashboard",
        ),
        WorkloadProfile(
            name="backup_history_actor_matrix",
            sql=(
                f"SELECT actor, status, COUNT(*), AVG(ranges_failed) FROM {_DATABASE}.{_HISTORY_TABLE} "
                "GROUP BY actor, status ORDER BY actor, status"
            ),
            qps=0.26,
            tier="MEDIUM",
            application_name="backup-audit",
        ),
        WorkloadProfile(
            name="backup_storage_error_prefix_search",
            sql=(
                f"SELECT storage_uri, COUNT(*), MAX(error_text) FROM {_DATABASE}.{_HISTORY_TABLE} "
                "WHERE error_text <> '' GROUP BY storage_uri ORDER BY COUNT(*) DESC LIMIT 30"
            ),
            qps=0.24,
            tier="MEDIUM",
            application_name="backup-oncall",
        ),
        WorkloadProfile(
            name="backup_credential_owner_matrix",
            sql=(
                f"SELECT owner, scope, status, COUNT(*) FROM {_DATABASE}.{_CREDENTIALS_TABLE} "
                "GROUP BY owner, scope, status ORDER BY owner, scope, status"
            ),
            qps=0.26,
            tier="MEDIUM",
            application_name="platform-audit",
        ),
        WorkloadProfile(
            name="backup_binding_role_matrix",
            sql=(
                f"SELECT role, target_scope, binding_state, COUNT(*) FROM {_DATABASE}.{_BINDINGS_TABLE} "
                "GROUP BY role, target_scope, binding_state ORDER BY role, target_scope, binding_state"
            ),
            qps=0.22,
            tier="MEDIUM",
            application_name="backup-control-plane",
        ),
    ),
    worker_count=10,
    seed=606060,
    start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
    warmup_seconds=15,
)


TidbSystemFailureBrPermissionCase = TidbSystemFailureBrPermissionForS3CredentialsDeniedScenarioCase


_SF06_CASE = TidbSystemFailureBrPermissionForS3CredentialsDeniedScenarioCase(
    case_id="br_s3_credentials_denied",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "the failed BR operation is a table snapshot backup of benchops.admission_events, not a foreground SQL slowdown or an unrelated historical backup",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions observed the failed BR operation is a table snapshot backup of benchops.admission_events, not a foreground SQL slowdown or an unrelated historical backup"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the current BR table backup fails because the target worker's object-storage write receives HTTP 403 Forbidden while the source table and object-storage service remain available",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions observed the current BR table backup fails because the target worker's object-storage write receives HTTP 403 Forbidden while the source table and object-storage service remain available"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the target control-plane binding and current worker lease appear converged on the active production material, but the failed request's time-scoped data-plane cache snapshot resolves to a different opaque material",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions correlated the failed request start with a request-time cache snapshot different from the converged current worker lease"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the failed scheduler dispatch has eleven same-scope route assignments for the same public event second; all failed writes share the production worker/executor identity, the assignment windows overlap the BR request start, and each write remains a distinct opaque request candidate",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions correlated the failed dispatch and request start with eleven same-scope route assignments, compared overlapping valid windows and handoff ownership, and retained every failed-write candidate"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the current dispatch record resolves the production request to the generation-3001 dispatch-window route, registry assignment, and target lease; a same-generation competing assignment also covers request start, so route lifecycle, change_ref, material, and production URI must be compared before selecting the production lease",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions joined the current dispatch generation and request-start window to the generation-3001 routes, then compared lifecycle, change_ref, authority, material, and URI ownership across the overlapping route and registry assignments"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the failed request cache snapshot's worker handle and target scope match the same production worker identity used by all candidates; the production cache and a competing cache both cover request start, so route identity, lifecycle, change_ref, material, and URI ownership must be compared before selecting the causal snapshot",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions joined request cache route identity, lifecycle, change_ref, material, ownership, and time window to the generation-3001 production assignment and excluded the competing cache despite its same-worker request-start coverage"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the failed request's target-worker cache snapshot is the cause of the current 403: its opaque material handle carries production request context but selects a different active credential_id than the healthy sibling's production material, while the healthy sibling uses the active production material for the requested URI and the object-storage policy is available",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions resolved the request-time cache material handle, joined its credential_id to the credential inventory, and excluded the healthy sibling and object-storage policy"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the failed storage audit access-key fingerprint identifies an access-key alias shared by all eleven same-window failed-write material candidates, so fingerprint alone cannot select the causal request material",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions matched backup_storage_audit.access_key_fingerprint to all eleven failed-write material_digest rows and retained each candidate until cross-layer lifecycle correlation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the failed request cache, target worker lease, target authority lease, and competing failed-write assignments share one rotation change_ref, so the watch identity narrows the request to the same rotation wave but cannot select the production assignment without route, registry, authority, material, grant URI, and lifecycle closure",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions joined change_ref across backup_request_material_cache, backup_worker_leases, and backup_authority_grant_leases and retained all same-watch failed-write assignments until the full route, registry, authority, material, grant URI, and lifecycle chain selected the production request"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the failed storage request's opaque request_assignment_fence matches all eleven failed-write attempts, so the request-level boundary is established but does not distinguish the scheduler lifecycle that issued the production 403",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions aligned request_assignment_fence and request_context_token across backup_storage_audit, backup_dispatch_routes, backup_request_material_cache, backup_worker_leases, and backup_authority_grant_leases and retained all eleven same-context candidates for lifecycle disambiguation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the failed storage request's opaque request_context_token is shared by all eleven failed-write route/cache/worker/authority records, so it identifies the request but not one actual execution attempt; assignment generation and cross-table identity resolve the 403 executor",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions observed the same request_context_token on all failed-write candidates and used dispatch generation, route window, registry lifecycle, cache identity, and grant URI to distinguish the production execution"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the failed storage audit request stage and request start/event time align with eleven same-second write candidates carrying the same dispatch-window/storage-write labels; the later follow-up starts after the failed event, so route, registry, cache, lease, grant, lifecycle, and change_ref identities together resolve the production executor",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions aligned backup_storage_audit request stage and request start/event time with all eleven failed put_backup_chunk rows, excluded the later follow-up, compared the symmetric competing candidates using cross-layer lifecycle and ownership evidence, and then resolved production ownership"
                    ]
                },
                    {
                        "type": "finding",
                        "factor": "the storage audit dispatch and event time resolve to all eleven same-second failed put_backup_chunk rows in backup_storage_request_attempts; the completed precheck precedes them and the later follow-up starts after the 403",
                        "entity": "br_s3_credentials_denied",
                        "evidence": [
                        "scripted diagnostic actions joined backup_storage_audit.dispatch_id and event_time to all eleven failed-write rows, then excluded the completed non-write precheck and later follow-up by operation/state/window"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "same dispatch failed attempt competition is causal: the storage audit has no attempt_id and the ledger contains eleven failed put_backup_chunk writes with the same dispatch, request context, assignment fence, second-level event time, access-key fingerprint, assignment generation, common dispatch-window/storage-write labels, worker/executor identity, and rotation change_ref; only the production route/cache/worker/authority/material chain closes on the current dispatch request-start lifecycle, active binding, authority epoch, and production grant URI, while the other ten same-worker candidates must not be refreshed",
                        "entity": "br_s3_credentials_denied",
                        "evidence": [
                        "scripted diagnostic actions compared the opaque attempt identities, route/cache/worker/authority/material identity, assignment generation, registry window, grant scope, and request URI for all eleven failed writes before selecting the production target"
                        ]
                    },
                {
                    "type": "finding",
                    "factor": "the failed request material credential_id resolves to an active scope grant that covers only the rehearsal URI, despite the credential inventory row presenting production request context, while the effective production credential has an active grant covering the requested production URI",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions joined the failed material credential_id to backup_credential_scope_grants and compared grant_scope/grant_uri with the failed production request"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the failed production request route's lease token and generation resolve to a stale target authority lease: its observed rehearsal grant and lower revision lag the desired production grant during the request window, while the other failed-write authority leases are different assignments",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions joined the request route lease_token and route_generation to backup_authority_grant_leases assignment_generation, then compared observed/desired grant ids, revisions, lease_state, and request time window with the other failed-write authority leases"
                    ]
                },
                {
                    "type": "finding",
                        "factor": "the worker lease and authority lease for the failed request share opaque authority epoch ep-4b8e2f19; the same lease token and generation also have a different competing epoch, so only the epoch-aligned stale grant, change_ref, lifecycle, and URI state is causal",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions joined the request route lease token and generation through backup_worker_leases and backup_authority_grant_leases, then matched authority_epoch, change_ref, grant revisions, stale state, and the failed request time window while excluding the competing epoch"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the current dispatch's generation-3001 route and registry assignment are valid at request start and through the storage event; one same-generation competing candidate also covers request start with the same worker/executor identity, so lifecycle, change_ref, authority, material, and production URI evidence rather than a phase label identifies the production dispatch",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions joined request_started_at and event_time to the current dispatch generation, compared the overlapping lifecycle windows and symmetric labels, then resolved the target worker lease, authority epoch, change_ref, and production URI"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the source benchops.admission_events table is intact and the incident is an object-storage authorization failure rather than data loss or table corruption",
                    "entity": "br_s3_credentials_denied",
                    "evidence": [
                        "scripted diagnostic actions observed the source benchops.admission_events table is intact and the incident is an object-storage authorization failure rather than data loss or table corruption"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "reconciled the target worker binding for the approved table scope and reran the table backup without a secret override"
            ],
            "verification": [
                "BR completed all ranges with checksum 100%, backupmeta exists, and the source table CRC is unchanged"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbSystemFailureBrPermissionEvaluatorCase,
    title="Nightly table backup SLO is breached while foreground data remains available.",
    alert=(
        "[CRITICAL] The nightly table-backup SLO has been breached repeatedly. The source ledger remains "
        "readable and foreground requests are serving, but the latest backup attempt is not usable. "
        "Separate source-data integrity, database/backup execution, job history, and remote-storage evidence; "
        "identify the failed stage, restore a verified backup, and keep source data and unrelated backup-control "
        "records unchanged."
    ),
    initial_state={"status": "degraded", "backup": "failed", "source_table": "read_write"},
    expected_target={
        "status": "recovered",
        "backup": "3/3 ranges with checksum 100%",
        "objects": "backupmeta present",
        "source_table": "crc unchanged",
    },
    background_workload=_SF06_BACKGROUND_WORKLOAD,
    difficulty=DifficultyCalibration(
        diagnostic_depth=24,
        environmental_complexity=0.539315,
        reference_run_ids=(
            "reference-237__tidb_system_failure_br_permission__br_s3_credentials_denied__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        readiness_timeout_seconds=2400,
    ),
    database=_DATABASE,
    table=_TABLE,
    credentials_table=_CREDENTIALS_TABLE,
    credential_grants_table=_CREDENTIAL_GRANTS_TABLE,
    authority_leases_table=_AUTHORITY_LEASES_TABLE,
    history_table=_HISTORY_TABLE,
    bindings_table=_BINDINGS_TABLE,
    worker_leases_table=_WORKER_LEASES_TABLE,
    storage_audit_table=_STORAGE_AUDIT_TABLE,
    worker_registry_table=_WORKER_REGISTRY_TABLE,
    worker_materials_table=_WORKER_MATERIALS_TABLE,
    job_dispatches_table=_JOB_DISPATCHES_TABLE,
    dispatch_routes_table=_DISPATCH_ROUTES_TABLE,
    request_cache_table=_REQUEST_CACHE_TABLE,
    request_attempts_table=_REQUEST_ATTEMPTS_TABLE,
    row_count=1000,
    expected_ranges=3,
    effective_binding_id=900,
    candidate_binding_id=901,
    fault_credential_id=902,
    correct_credential_id=901,
    target_worker="br-worker-0",
    healthy_worker="br-worker-1",
    target_authority_lease_id=17,
    target_authority_epoch=_TARGET_AUTHORITY_EPOCH,
    desired_revision=18,
    observed_revision=18,
)


_FOCUSED_SF06_WORKLOAD = replace(
    _SF06_BACKGROUND_WORKLOAD,
    profiles=tuple(
        profile
        for profile in _SF06_BACKGROUND_WORKLOAD.profiles
        if profile.name in {
            "ledger_event_lookup",
            "backup_history_audit",
            "backup_credential_inventory_audit",
            "backup_target_candidate_audit",
            "backup_runtime_binding_watch",
            "backup_effective_binding_lookup",
            "backup_binding_propagation_audit",
            "backup_current_job_binding_join",
            "platform_change_event_matrix",
            "platform_change_event_window",
        }
    ),
    worker_count=5,
    warmup_seconds=8,
)

_FOCUSED_SF06_CASE = replace(
    _SF06_CASE,
    case_id="br_s3_binding_focus",
    case_no=1,
    evaluator=TidbSystemFailureBrPermissionFocusedEvaluatorCase,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": (
                        "the failed BR operation is a table snapshot backup of benchops.admission_events, and the "
                        "current BR table backup fails because the target worker's object-storage write receives "
                        "HTTP 403 Forbidden: the failed request's time-scoped data-plane cache snapshot resolves to "
                        "an opaque material whose credential has no active grant covering the requested production "
                        "URI, while the source table and object-storage service remain available"
                    ),
                    "entity": "br_s3_binding_focus",
                    "evidence": [
                        "the request-time cache material handle resolves to a credential whose active scope grant "
                        "covers only the rehearsal URI; the desired authority grant is not materialized on any "
                        "lease row and is derived as the unique request-time-valid production grant of the "
                        "control-plane credential from the grants window"
                    ],
                },
                {
                    "type": "finding",
                    "factor": (
                        "the source benchops.admission_events table is intact and the incident is an object-storage "
                        "authorization failure rather than data loss or table corruption; only the target worker "
                        "binding for the approved table scope must be reconciled onto the active production material "
                        "and the backup rerun, while the healthy sibling and the other same-window failed-write "
                        "candidates must not be refreshed"
                    ),
                    "entity": "br_s3_binding_focus",
                    "evidence": [
                        "source-table truth is unchanged and the healthy sibling worker stays converged on the "
                        "active production material"
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "reconciled the target worker binding for the approved table scope and reran the table backup without a secret override"
            ],
            "verification": [
                "BR completed all ranges with checksum 100%, backupmeta exists, and the source table CRC is unchanged"
            ],
        },
        "summary": "The focused scripted mock reconciled the target worker binding and verified the rerun backup.",
    },
    background_workload=_FOCUSED_SF06_WORKLOAD,
    effective_binding_id=1900,
    candidate_binding_id=1901,
    fault_credential_id=1902,
    correct_credential_id=1901,
    entity_decoys=True,
    derive_desired_from_grants=True,
    uniform_refresh_rejection=True,
    epoch_from_observation=True,
    storage_prefix_quarantine=True,
    live_authority_epoch=_LIVE_AUTHORITY_EPOCH,
    prefix_quarantine_ref=_PREFIX_QUARANTINE_REF,
    target_authority_lease_id=46,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.466527,
        reference_run_ids=(
            "reference-233__"
            "tidb_system_failure_br_permission__br_s3_binding_focus__mock__r001",
        ),
    ),
)


class TidbSystemFailureBrPermissionInjector(BaseFaultInjector):
    """Run a real BR table backup against an isolated S3-compatible store."""

    def __init__(self):
        self._runtime_registered = False
        self._minio_container = None
        self._minio_running = False

    def install(self, context: FaultLifecycleContext):
        self._configure(context.config, context)
        self._start_minio()
        self._create_fixture(context.env)
        self._register_runtime(context.env)
        self._verify_fixture(context.env)

    def activate(self, context: FaultLifecycleContext):
        self._configure(context.config, context)
        self._ensure_minio_running()
        if not self._runtime_registered:
            self._register_runtime(context.env)
        self._verify_fixture(context.env)

    def prepare_observability(self, context: FaultLifecycleContext):
        source_truth = context.env.capture_br_source_truth(context.case)
        failed_attempt = json.loads(
            context.env.manage_cluster(
                resource="job",
                operation="start",
                parameters={
                    "database": self.database,
                    "table": self.table,
                },
            )
        )
        if failed_attempt["status"] == "success":
            failed_attempt = failed_attempt["result"]
        if failed_attempt["status"] == "success":
            raise RuntimeError(
                "SF06 stale-worker BR backup unexpectedly succeeded: "
                f"run_id={context.run_id!r}, database={self.database!r}, table={self.table!r}, "
                f"attempt={failed_attempt!r}"
            )
        failure_text = str(failed_attempt.get("error", failed_attempt.get("output", ""))).casefold()
        if "403" not in failure_text and "forbidden" not in failure_text:
            raise RuntimeError(
                "SF06 stale-worker BR backup failed without the required 403/Forbidden evidence: "
                f"run_id={context.run_id!r}, attempt={failed_attempt!r}"
            )
        return {
            "sf06_source_truth_before": source_truth,
            "sf06_failed_br_attempt": failed_attempt,
            "sf06_reference_unit_counts": {
                "backup_job_history": {"causal": 2, "noise": 59},
                "backup_credentials": {"causal": 8, "noise": 91},
                "backup_runtime_bindings": {"causal": 8, "noise": 88},
                "backup_authority_grant_leases": {"causal": 26, "noise": 3},
                "backup_worker_leases": {"causal": 8, "noise": 14},
                "backup_worker_registry": {"causal": 8, "noise": 15},
                "backup_job_dispatches": {"causal": 6, "noise": 41},
                "backup_dispatch_routes": {"causal": 10, "noise": 50},
                "backup_worker_materials": {"causal": 7, "noise": 4},
                "backup_request_material_cache": {"causal": 8, "noise": 14},
                "backup_storage_audit": {"causal": 3, "noise": 15},
                "backup_storage_request_attempts": {"causal": 11, "noise": 2},
                "request_attempt_ledger_is_causal": {"causal": 1, "noise": 0},
            },
        }

    def quiesce(self, context: FaultLifecycleContext):
        if not self._minio_running:
            raise RuntimeError(
                "SF06 cannot quiesce an inactive MinIO runtime: "
                f"run_id={context.run_id!r}, container={self._minio_container!r}"
            )
        completed = subprocess.run(
            ["docker", "stop", self._minio_container],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "SF06 MinIO quiesce failed: "
                f"run_id={context.run_id!r}, container={self._minio_container!r}, "
                f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
            )
        self._minio_running = False

    def recover(self, context: FaultLifecycleContext):
        if self._minio_container is None:
            raise RuntimeError(
                "SF06 recovery has no MinIO container identity: "
                f"run_id={context.run_id!r}"
            )
        completed = subprocess.run(
            ["docker", "rm", "--force", self._minio_container],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "SF06 MinIO recovery failed: "
                f"run_id={context.run_id!r}, container={self._minio_container!r}, "
                f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
            )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.history_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR history table {self.history_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.credentials_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR credential table {self.credentials_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.credential_grants_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR credential grant table {self.credential_grants_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.authority_leases_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR authority lease table {self.authority_leases_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.bindings_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR runtime binding table {self.bindings_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.worker_leases_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR worker lease table {self.worker_leases_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.storage_audit_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR storage audit table {self.storage_audit_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.worker_registry_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR worker registry table {self.worker_registry_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.worker_materials_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR worker material table {self.worker_materials_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.job_dispatches_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR job dispatch table {self.job_dispatches_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.dispatch_routes_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR dispatch route table {self.dispatch_routes_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.request_cache_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR request cache table {self.request_cache_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.request_attempts_relation}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR request attempts table {self.request_attempts_relation}",
        )
        require_sql_success(
            context.env.execute_sql_with_timeout(
                f"DROP TABLE IF EXISTS {self.database}.{self.table}",
                timeout_seconds=300,
            ),
            f"drop SF06 BR source table {self.database}.{self.table}",
        )
        if self._runtime_registered:
            context.env.clear_br_backup_runtime()
        self._minio_running = False
        self._runtime_registered = False

    def _configure(self, config: Mapping[str, object], context: FaultLifecycleContext) -> None:
        self.database = validate_sql_identifier(str(config["database"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.credentials_table = validate_sql_identifier(str(config["credentials_table"]), "credentials_table")
        self.credential_grants_table = validate_sql_identifier(str(config["credential_grants_table"]), "credential_grants_table")
        self.authority_leases_table = validate_sql_identifier(str(config["authority_leases_table"]), "authority_leases_table")
        self.history_table = validate_sql_identifier(str(config["history_table"]), "history_table")
        self.bindings_table = validate_sql_identifier(str(config["bindings_table"]), "bindings_table")
        self.worker_leases_table = validate_sql_identifier(str(config["worker_leases_table"]), "worker_leases_table")
        self.storage_audit_table = validate_sql_identifier(str(config["storage_audit_table"]), "storage_audit_table")
        self.worker_registry_table = validate_sql_identifier(str(config["worker_registry_table"]), "worker_registry_table")
        self.worker_materials_table = validate_sql_identifier(str(config["worker_materials_table"]), "worker_materials_table")
        self.job_dispatches_table = validate_sql_identifier(str(config["job_dispatches_table"]), "job_dispatches_table")
        self.dispatch_routes_table = validate_sql_identifier(str(config["dispatch_routes_table"]), "dispatch_routes_table")
        self.request_cache_table = validate_sql_identifier(str(config["request_cache_table"]), "request_cache_table")
        self.request_attempts_table = validate_sql_identifier(str(config["request_attempts_table"]), "request_attempts_table")
        self.quarantine_tickets_table = validate_sql_identifier(str(config["quarantine_tickets_table"]), "quarantine_tickets_table")
        self.credentials_relation = f"{self.database}.{self.credentials_table}"
        self.credential_grants_relation = f"{self.database}.{self.credential_grants_table}"
        self.authority_leases_relation = f"{self.database}.{self.authority_leases_table}"
        self.history_relation = f"{self.database}.{self.history_table}"
        self.bindings_relation = f"{self.database}.{self.bindings_table}"
        self.worker_leases_relation = f"{self.database}.{self.worker_leases_table}"
        self.storage_audit_relation = f"{self.database}.{self.storage_audit_table}"
        self.worker_registry_relation = f"{self.database}.{self.worker_registry_table}"
        self.worker_materials_relation = f"{self.database}.{self.worker_materials_table}"
        self.job_dispatches_relation = f"{self.database}.{self.job_dispatches_table}"
        self.dispatch_routes_relation = f"{self.database}.{self.dispatch_routes_table}"
        self.request_cache_relation = f"{self.database}.{self.request_cache_table}"
        self.request_attempts_relation = f"{self.database}.{self.request_attempts_table}"
        self.quarantine_tickets_relation = f"{self.database}.{self.quarantine_tickets_table}"
        self.row_count = int(config["row_count"])
        self.expected_ranges = int(config["expected_ranges"])
        self.effective_binding_id = int(config["effective_binding_id"])
        self.candidate_binding_id = int(config["candidate_binding_id"])
        self.fault_credential_id = int(config["fault_credential_id"])
        self.correct_credential_id = int(config["correct_credential_id"])
        self.target_worker = str(config["target_worker"])
        self.healthy_worker = str(config["healthy_worker"])
        self.target_authority_lease_id = int(config["target_authority_lease_id"])
        self.target_authority_epoch = str(config["target_authority_epoch"])
        self.target_executor_handle = str(config["target_executor_handle"])
        self.desired_revision = int(config["desired_revision"])
        self.observed_revision = int(config["observed_revision"])
        self.entity_decoys = bool(config["entity_decoys"])
        self.derive_desired_from_grants = bool(config["derive_desired_from_grants"])
        self.uniform_refresh_rejection = bool(config["uniform_refresh_rejection"])
        self.epoch_from_observation = bool(config["epoch_from_observation"])
        self.storage_prefix_quarantine = bool(config["storage_prefix_quarantine"])
        self.live_authority_epoch = str(config["live_authority_epoch"])
        self.prefix_quarantine_ref = str(config["prefix_quarantine_ref"])
        self.minio_image = str(config["minio_image"])
        self.mc_image = str(config["mc_image"])
        self.br_image = str(config["br_image"])
        self.minio_container = f"{config['minio_container_prefix']}-{hashlib.sha256(context.run_id.encode()).hexdigest()[:12]}"
        self.bucket = str(config["bucket"])
        self.object_prefix = str(config["object_prefix"])
        self.correct_access_key = str(config["correct_access_key"])
        self.correct_secret_key = str(config["correct_secret_key"])
        self.fault_access_key = str(config["fault_access_key"])
        self.fault_secret_key = str(config["fault_secret_key"])
        self._observed_access_key = self.fault_access_key
        self._observed_secret_key = self.fault_secret_key
        self.timeout_seconds = int(config["timeout_seconds"])
        self.network_name = context.env.deployment.network_name
        self.endpoint = f"http://{self.minio_container}:9000"
        self.storage = self._storage_for(self.object_prefix)

    def _storage_for(self, object_prefix: str) -> str:
        return f"s3://{self.bucket}/{object_prefix}?endpoint={self.endpoint}&force-path-style=true"

    def _register_runtime(self, env) -> None:
        env.configure_br_backup_runtime({
            "database": self.database,
            "table": self.table,
            "credentials_relation": self.credentials_relation,
            "credential_grants_table": self.credential_grants_relation,
            "authority_leases_table": self.authority_leases_relation,
            "history_table": self.history_relation,
            "bindings_relation": self.bindings_relation,
            "worker_leases_table": self.worker_leases_relation,
            "storage_audit_table": self.storage_audit_relation,
            "worker_registry_table": self.worker_registry_relation,
            "worker_materials_table": self.worker_materials_relation,
            "job_dispatches_table": self.job_dispatches_relation,
            "dispatch_routes_table": self.dispatch_routes_relation,
            "request_cache_table": self.request_cache_relation,
            "request_attempts_table": self.request_attempts_relation,
            "quarantine_tickets_table": self.quarantine_tickets_relation,
            "target_executor_handle": self.target_executor_handle,
            "derive_desired_from_grants": self.derive_desired_from_grants,
            "uniform_refresh_rejection": self.uniform_refresh_rejection,
            "epoch_from_observation": self.epoch_from_observation,
            "live_authority_epoch": self.live_authority_epoch,
            "storage_prefix_quarantine": self.storage_prefix_quarantine,
            "prefix_quarantine_active": self.storage_prefix_quarantine,
            "prefix_quarantine_ref": self.prefix_quarantine_ref,
            "controller_events": self._controller_event_stream(),
            "target_worker_handle": _TARGET_WORKER_HANDLE,
            "target_authority_lease_id": str(self.target_authority_lease_id),
            "authority_lease_id": str(self.target_authority_lease_id),
        "failed_request_attempt_id": "att-4a7f1c9e",
        "failed_request_attempt_sequence": "4",
            "target_authority_epoch": self.target_authority_epoch,
            "target_change_ref": _TARGET_CHANGE_REF,
            "target_scope": f"{self.database}.{self.table}",
            "target_lease_id": "8",
            "target_lease_token": _TARGET_LEASE_TOKEN,
            "target_assignment_generation": "3001",
            "post_handoff_lease_token": _POST_HANDOFF_LEASE_TOKEN,
            "request_route_token": _REQUEST_ROUTE_TOKEN,
            "request_cache_token": _REQUEST_CACHE_TOKEN,
            "retry_cache_token": "cache-sf06-br-002",
            "target_assignment_fence": _TARGET_ASSIGNMENT_FENCE,
            "request_assignment_replay_fence": _REQUEST_ASSIGNMENT_REPLAY_FENCE,
            "retry_assignment_fence": _RETRY_ASSIGNMENT_FENCE,
            "target_request_context": _TARGET_REQUEST_CONTEXT,
            "request_assignment_replay_context": _REQUEST_ASSIGNMENT_REPLAY_CONTEXT,
            "retry_request_context": _RETRY_REQUEST_CONTEXT,
            "target_request_stage": _TARGET_REQUEST_STAGE,
            "target_execution_phase": _TARGET_EXECUTION_PHASE,
            "target_execution_reason": _TARGET_EXECUTION_REASON,
            "replay_request_stage": "post_failure_replay",
            "replay_execution_phase": _REPLAY_EXECUTION_PHASE,
            "replay_execution_reason": _REPLAY_EXECUTION_REASON,
            "target_material_handle": _TARGET_MATERIAL_HANDLE,
            "correct_material_handle": _PRODUCTION_MATERIAL_HANDLE,
            "desired_binding_id": str(self.effective_binding_id),
            "desired_credential_id": str(self.correct_credential_id),
            "desired_revision": str(self.desired_revision),
            "observed_binding_id": str(self.effective_binding_id),
            "observed_revision": str(self.observed_revision),
            "observed_material_handle": _TARGET_MATERIAL_HANDLE,
            "request_cache_material_handle": _TARGET_MATERIAL_HANDLE,
            "target_worker": self.target_worker,
            "healthy_worker": self.healthy_worker,
            "storage": self.storage,
            "network_name": self.network_name,
            "minio_container": self.minio_container,
            "bucket": self.bucket,
            "object_prefix": self.object_prefix,
            "correct_access_key": self.correct_access_key,
            "correct_secret_key": self.correct_secret_key,
            "observed_access_key": self._observed_access_key,
            "observed_secret_key": self._observed_secret_key,
            "last_forbidden_access_key": self._observed_access_key,
            "mc_image": self.mc_image,
            "br_image": self.br_image,
            "pd_endpoint": "pd-0:2379",
            "run_prefix": "sf06-br",
            "timeout_seconds": str(self.timeout_seconds),
        })
        self._runtime_registered = True

    def _controller_event_stream(self) -> tuple[dict, ...]:
        # r9: the rotation controller's recent event stream. Under
        # epoch_from_observation the epoch promotion is the live control-plane
        # fact the lease-table paper trail cannot show; under
        # storage_prefix_quarantine the denial-rate guard entry announces the
        # quarantine. r11: the stream carries no release ticket — the guard
        # issues the release ticket into its ticket table on the first denied
        # write, so the release identity only exists after the denied attempt.
        # The remaining rows are routine heartbeats from healthy workers and
        # unrelated scopes.
        target_scope = f"{self.database}.{self.table}"
        healthy_epoch = (
            self.live_authority_epoch
            if self.epoch_from_observation
            else self.target_authority_epoch
        )
        events: list[dict] = [
            {
                "event": "worker_serving_heartbeat",
                "worker": "br-worker-1",
                "scope": target_scope,
                "material_fingerprint": "6a6ba702490a3747",
                "authority_epoch": healthy_epoch,
                "at": "2026-08-01 23:59:31",
            },
            {
                "event": "worker_serving_heartbeat",
                "worker": "br-worker-0",
                "scope": target_scope,
                "material_fingerprint": "21d7434db5b737f2",
                "authority_epoch": self.target_authority_epoch,
                "at": "2026-08-01 23:59:12",
            },
            {
                "event": "rehearsal_lease_heartbeat",
                "scope": f"{target_scope}/rehearsal",
                "authority_epoch": _REHEARSAL_AUTHORITY_EPOCH,
                "at": "2026-08-01 23:59:03",
            },
            {
                "event": "reporting_scope_epoch_refresh",
                "scope": "reporting.admission_events",
                "current_epoch": _REPORTING_AUTHORITY_EPOCH,
                "at": "2026-08-01 23:59:18",
            },
        ]
        if self.epoch_from_observation:
            events.extend((
                {
                    "event": "authority_epoch_promoted",
                    "scope": target_scope,
                    "previous_epoch": self.target_authority_epoch,
                    "current_epoch": self.live_authority_epoch,
                    "promotion_source": "rotation-controller",
                    "at": "2026-08-01 23:59:05",
                },
                {
                    "event": "worker_serving_heartbeat",
                    "worker": "br-worker-4",
                    "scope": target_scope,
                    "material_fingerprint": "6a6ba702490a3747",
                    "authority_epoch": self.live_authority_epoch,
                    "at": "2026-08-01 23:59:44",
                },
                {
                    "event": "worker_serving_heartbeat",
                    "worker": "br-worker-5",
                    "scope": target_scope,
                    "material_fingerprint": "6a6ba702490a3747",
                    "authority_epoch": self.live_authority_epoch,
                    "at": "2026-08-01 23:59:47",
                },
            ))
        if self.storage_prefix_quarantine:
            events.append({
                "event": "storage_prefix_quarantined",
                "prefix": self.object_prefix,
                "bucket": self.bucket,
                "guard": "bucket-denial-rate-guard",
                "trigger": "repeated-denied-writes",
                "at": "2026-08-01 23:59:50",
            })
        # r10: routine heartbeats keep arriving after the incident window, so
        # the observe default window (most recent events) shows only steady
        # serving noise; the promotion and quarantine entries must be read
        # back through the explicit time-window parameters.
        for worker, at in (
            ("br-worker-1", "2026-08-01 23:59:51"),
            ("br-worker-4", "2026-08-01 23:59:55"),
            ("br-worker-1", "2026-08-01 23:59:58"),
            ("br-worker-5", "2026-08-02 00:00:12"),
            ("br-worker-1", "2026-08-02 00:00:34"),
            ("br-worker-4", "2026-08-02 00:00:56"),
            ("br-worker-5", "2026-08-02 00:01:18"),
            ("br-worker-1", "2026-08-02 00:01:40"),
        ):
            events.append({
                "event": "worker_serving_heartbeat",
                "worker": worker,
                "scope": target_scope,
                "material_fingerprint": "6a6ba702490a3747",
                "authority_epoch": healthy_epoch,
                "at": at,
            })
        return tuple(sorted(events, key=lambda item: item["at"], reverse=True))

    def _create_fixture(self, env) -> None:
        require_sql_success(
            self._fixture_sql(env, "CREATE DATABASE IF NOT EXISTS benchops"),
            "create SF06 benchops database",
        )
        require_sql_success(
            self._fixture_sql(env, f"DROP TABLE IF EXISTS {self.history_relation}"),
            f"clear SF06 BR history table {self.history_relation}",
        )
        require_sql_success(
            self._fixture_sql(env, f"DROP TABLE IF EXISTS {self.credentials_relation}"),
            f"clear SF06 BR credential table {self.credentials_relation}",
        )
        require_sql_success(
            self._fixture_sql(env, f"DROP TABLE IF EXISTS {self.credential_grants_relation}"),
            f"clear SF06 BR credential grant table {self.credential_grants_relation}",
        )
        require_sql_success(
            self._fixture_sql(env, f"DROP TABLE IF EXISTS {self.authority_leases_relation}"),
            f"clear SF06 BR authority lease table {self.authority_leases_relation}",
        )
        require_sql_success(
            self._fixture_sql(env, f"DROP TABLE IF EXISTS {self.bindings_relation}"),
            f"clear SF06 BR runtime binding table {self.bindings_relation}",
        )
        require_sql_success(
            self._fixture_sql(env, f"DROP TABLE IF EXISTS {self.job_dispatches_relation}"),
            f"clear SF06 BR job dispatch table {self.job_dispatches_relation}",
        )
        require_sql_success(
            self._fixture_sql(env, f"DROP TABLE IF EXISTS {self.dispatch_routes_relation}"),
            f"clear SF06 BR dispatch route table {self.dispatch_routes_relation}",
        )
        require_sql_success(
            self._fixture_sql(env, f"DROP TABLE IF EXISTS {self.request_cache_relation}"),
            f"clear SF06 BR request cache table {self.request_cache_relation}",
        )
        require_sql_success(
            self._fixture_sql(env, f"DROP TABLE IF EXISTS {self.request_attempts_relation}"),
            f"clear SF06 BR request attempts table {self.request_attempts_relation}",
        )
        require_sql_success(
            self._fixture_sql(env, f"DROP TABLE IF EXISTS {self.worker_materials_relation}"),
            f"clear SF06 BR worker material table {self.worker_materials_relation}",
        )
        require_sql_success(
            self._fixture_sql(env, f"DROP TABLE IF EXISTS {self.database}.{self.table}"),
            f"clear SF06 BR source table {self.database}.{self.table}",
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.database}.{self.table} ("
                "event_id BIGINT PRIMARY KEY, tenant_id INT NOT NULL, "
                "event_type VARCHAR(32) NOT NULL, amount DECIMAL(12, 2) NOT NULL, "
                "payload VARCHAR(128) NOT NULL, KEY idx_tenant_type (tenant_id, event_type), "
                "KEY idx_event_type (event_type))"
            ),
            f"create SF06 BR source table {self.database}.{self.table}",
        )
        self._insert_source_rows(env)
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.credentials_relation} ("
                "credential_id INT PRIMARY KEY, profile_name VARCHAR(64) NOT NULL, "
                "scope VARCHAR(128) NOT NULL, storage_uri VARCHAR(255) NOT NULL, "
                "access_key VARCHAR(128) NOT NULL, access_key_fingerprint VARCHAR(32) NOT NULL, "
                "secret_key VARCHAR(128) NOT NULL, "
                "status VARCHAR(16) NOT NULL, owner VARCHAR(64) NOT NULL, "
                "last_rotated DATETIME NOT NULL)"
            ),
            f"create SF06 BR credential table {self.credentials_relation}",
        )
        self._insert_credentials(env)
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.credential_grants_relation} ("
                "grant_id INT PRIMARY KEY, credential_id INT NOT NULL, grant_scope VARCHAR(128) NOT NULL, "
                "grant_uri VARCHAR(255) NOT NULL, grant_state VARCHAR(16) NOT NULL, valid_from DATETIME NOT NULL, "
                "valid_to DATETIME NULL, grant_source VARCHAR(64) NOT NULL, "
                "KEY idx_grant_credential_time (credential_id, valid_from, valid_to), "
                "KEY idx_grant_scope (grant_scope, grant_state))"
            ),
            f"create SF06 BR credential grant table {self.credential_grants_relation}",
        )
        self._insert_credential_grants(env)
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.authority_leases_relation} ("
                "lease_id INT PRIMARY KEY, lease_token VARCHAR(64) NOT NULL, assignment_generation INT NOT NULL, "
                "authority_epoch VARCHAR(64) NOT NULL, "
                "target_scope VARCHAR(128) NOT NULL, observed_grant_id INT NOT NULL, desired_grant_id INT NOT NULL, observed_revision INT NOT NULL, "
                "desired_revision INT NOT NULL, lease_state VARCHAR(16) NOT NULL, valid_from DATETIME NOT NULL, "
                "valid_to DATETIME NULL, change_ref VARCHAR(64) NOT NULL, request_assignment_fence VARCHAR(64) NOT NULL, "
                "request_context_token VARCHAR(64) NOT NULL, execution_phase VARCHAR(32) NOT NULL, "
                "execution_reason VARCHAR(64) NOT NULL, "
                "KEY idx_authority_identity (lease_token, assignment_generation, authority_epoch, target_scope, valid_from, valid_to), "
                "KEY idx_authority_scope_state (target_scope, lease_state))"
            ),
            f"create SF06 BR authority lease table {self.authority_leases_relation}",
        )
        self._insert_authority_leases(env)
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.bindings_relation} ("
                "binding_id INT PRIMARY KEY, target_scope VARCHAR(128) NOT NULL, "
                "credential_id INT NOT NULL, role VARCHAR(32) NOT NULL, "
                "binding_state VARCHAR(16) NOT NULL, effective_from DATETIME NOT NULL, "
                "effective_to DATETIME NULL, change_ticket VARCHAR(64) NOT NULL, "
                "KEY idx_binding_target (target_scope, binding_state, effective_from), "
                "KEY idx_binding_credential (credential_id))"
            ),
            f"create SF06 BR runtime binding table {self.bindings_relation}",
        )
        self._insert_bindings(env)
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.worker_registry_relation} ("
                "assignment_id INT PRIMARY KEY, executor_handle VARCHAR(64) NOT NULL, "
                "lease_token VARCHAR(64) NOT NULL, assignment_generation INT NOT NULL, "
                "worker_handle VARCHAR(64) NOT NULL, "
                "target_scope VARCHAR(128) NOT NULL, "
                "valid_from DATETIME NOT NULL, valid_to DATETIME NULL, "
                "assignment_state VARCHAR(16) NOT NULL, "
                "KEY idx_handle_time (executor_handle, valid_from, valid_to), "
                "KEY idx_lease_identity (lease_token, assignment_generation, target_scope), "
                "KEY idx_scope_worker (target_scope, worker_handle))"
            ),
            f"create SF06 BR worker registry table {self.worker_registry_relation}",
        )
        self._insert_worker_registry(env)
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.worker_materials_relation} ("
                "material_handle VARCHAR(64) PRIMARY KEY, credential_id INT NOT NULL, "
                "target_scope VARCHAR(128) NOT NULL, storage_uri VARCHAR(255) NOT NULL, "
                "material_digest VARCHAR(32) NOT NULL, material_status VARCHAR(16) NOT NULL, "
                "valid_from DATETIME NOT NULL, valid_to DATETIME NULL, rotation_source VARCHAR(64) NOT NULL, "
                "KEY idx_material_credential (credential_id), KEY idx_material_scope_time (target_scope, valid_from, valid_to))"
            ),
            f"create SF06 BR worker material table {self.worker_materials_relation}",
        )
        self._insert_worker_materials(env)
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.dispatch_routes_relation} ("
                "route_token VARCHAR(64) PRIMARY KEY, dispatch_id VARCHAR(64) NOT NULL, "
                "target_scope VARCHAR(128) NOT NULL, executor_handle VARCHAR(64) NOT NULL, "
                "lease_token VARCHAR(64) NOT NULL, "
                "route_generation INT NOT NULL, valid_from DATETIME NOT NULL, valid_to DATETIME NULL, "
                "route_state VARCHAR(16) NOT NULL, assignment_phase VARCHAR(32) NOT NULL, "
                "route_reason VARCHAR(64) NOT NULL, request_assignment_fence VARCHAR(64) NOT NULL, "
                "request_context_token VARCHAR(64) NOT NULL, "
                "KEY idx_route_dispatch (dispatch_id), "
                "KEY idx_route_scope_time (target_scope, valid_from, valid_to))"
            ),
            f"create SF06 BR dispatch route table {self.dispatch_routes_relation}",
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.job_dispatches_relation} ("
                "dispatch_id VARCHAR(64) PRIMARY KEY, job_id VARCHAR(64) NOT NULL, "
                "target_scope VARCHAR(128) NOT NULL, storage_uri VARCHAR(255) NOT NULL, "
                "dispatch_generation INT NOT NULL, "
                "dispatched_at DATETIME NOT NULL, released_at DATETIME NULL, "
                "dispatch_state VARCHAR(16) NOT NULL, assignment_phase VARCHAR(32) NOT NULL, "
                "assignment_reason VARCHAR(64) NOT NULL, request_assignment_fence VARCHAR(64) NOT NULL, "
                "request_context_token VARCHAR(64) NOT NULL, "
                "KEY idx_dispatch_job_time (job_id, dispatched_at), "
                "KEY idx_dispatch_scope_time (target_scope, dispatched_at))"
            ),
            f"create SF06 BR job dispatch table {self.job_dispatches_relation}",
        )
        self._insert_job_dispatch_noise(env)
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.request_cache_relation} ("
                "cache_token VARCHAR(64) PRIMARY KEY, route_token VARCHAR(64) NOT NULL, "
                "target_scope VARCHAR(128) NOT NULL, "
                "worker_handle VARCHAR(64) NOT NULL, "
                "material_handle VARCHAR(64) NOT NULL, cache_phase VARCHAR(32) NOT NULL, "
                "valid_from DATETIME NOT NULL, valid_to DATETIME NULL, cache_state VARCHAR(16) NOT NULL, "
                "change_ref VARCHAR(64) NOT NULL, request_assignment_fence VARCHAR(64) NOT NULL, "
                "request_context_token VARCHAR(64) NOT NULL, "
                "KEY idx_cache_route (route_token), KEY idx_cache_worker_time (worker_handle, valid_from, valid_to), "
                "KEY idx_cache_scope_time (target_scope, valid_from, valid_to))"
            ),
            f"create SF06 BR request cache table {self.request_cache_relation}",
        )
        self._insert_request_material_cache(env)
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.request_attempts_relation} ("
                "attempt_id VARCHAR(64) PRIMARY KEY, dispatch_id VARCHAR(64) NOT NULL, "
                "target_scope VARCHAR(128) NOT NULL, request_context_token VARCHAR(64) NOT NULL, "
                "request_assignment_fence VARCHAR(64) NOT NULL, request_started_at DATETIME NOT NULL, "
                "event_time DATETIME NOT NULL, request_stage VARCHAR(32) NOT NULL, "
                "execution_phase VARCHAR(32) NOT NULL, execution_reason VARCHAR(64) NOT NULL, "
                "attempt_sequence INT NOT NULL, operation_name VARCHAR(64) NOT NULL, "
                "attempt_state VARCHAR(16) NOT NULL, access_key_fingerprint VARCHAR(32) NOT NULL, "
                "http_status INT NOT NULL, "
                "KEY idx_attempt_dispatch_time (dispatch_id, event_time), "
                "KEY idx_attempt_identity (request_context_token, request_assignment_fence, attempt_sequence))"
            ),
            f"create SF06 BR request attempts table {self.request_attempts_relation}",
        )
        self._insert_request_attempts(env)
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.worker_leases_relation} ("
                "lease_id INT PRIMARY KEY, lease_token VARCHAR(64) NOT NULL, assignment_generation INT NOT NULL, "
                "authority_epoch VARCHAR(64) NOT NULL, "
                "worker_id VARCHAR(64) NOT NULL, target_scope VARCHAR(128) NOT NULL, "
                "storage_uri VARCHAR(255) NOT NULL, "
                "desired_binding_id INT NOT NULL, desired_revision INT NOT NULL, "
                "observed_binding_id INT NOT NULL, observed_revision INT NOT NULL, "
                "observed_material_handle VARCHAR(64) NOT NULL, lease_state VARCHAR(16) NOT NULL, "
                "valid_from DATETIME NOT NULL, valid_to DATETIME NULL, "
                "last_heartbeat DATETIME NOT NULL, change_ref VARCHAR(64) NOT NULL, request_assignment_fence VARCHAR(64) NOT NULL, "
                "request_context_token VARCHAR(64) NOT NULL, execution_phase VARCHAR(32) NOT NULL, "
                "execution_reason VARCHAR(64) NOT NULL, "
                "KEY idx_lease_identity (lease_token, assignment_generation, authority_epoch, worker_id, target_scope), "
                "KEY idx_scope_state (target_scope, lease_state))"
            ),
            f"create SF06 BR worker lease table {self.worker_leases_relation}",
        )
        self._insert_worker_leases(env)
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.storage_audit_relation} ("
                "job_id VARCHAR(64) PRIMARY KEY, target_scope VARCHAR(128) NOT NULL, "
                "storage_uri VARCHAR(255) NOT NULL, dispatch_id VARCHAR(64) NOT NULL, "
                "http_status INT NOT NULL, access_key_fingerprint VARCHAR(32) NOT NULL, "
                "policy_decision VARCHAR(16) NOT NULL, request_stage VARCHAR(32) NOT NULL, "
                "request_started_at DATETIME NOT NULL, event_time DATETIME NOT NULL, request_assignment_fence VARCHAR(64) NOT NULL, "
                "request_context_token VARCHAR(64) NOT NULL, "
                "KEY idx_audit_scope_time (target_scope, event_time))"
            ),
            f"create SF06 BR storage audit table {self.storage_audit_relation}",
        )
        self._insert_storage_audit_noise(env)
        if self.storage_prefix_quarantine:
            # r11: the storage guard keeps its own quarantine release tickets.
            # The table starts empty; the first denied write under the active
            # quarantine issues the release ticket row at runtime.
            require_sql_success(
                self._fixture_sql(
                    env,
                    f"CREATE TABLE {self.quarantine_tickets_relation} ("
                    "ticket_ref VARCHAR(64) PRIMARY KEY, prefix VARCHAR(128) NOT NULL, "
                    "bucket VARCHAR(128) NOT NULL, guard VARCHAR(64) NOT NULL, "
                    "triggering_change_ref VARCHAR(64) NOT NULL, "
                    "issued_at DATETIME NOT NULL, ticket_state VARCHAR(16) NOT NULL, "
                    "KEY idx_ticket_prefix (prefix, ticket_state))"
                ),
                f"create SF06 BR quarantine tickets table {self.quarantine_tickets_relation}",
            )
        require_sql_success(
            self._fixture_sql(
                env,
                f"CREATE TABLE {self.history_relation} ("
                "job_id VARCHAR(64) PRIMARY KEY, storage_uri VARCHAR(255) NOT NULL, "
                "database_name VARCHAR(64) NOT NULL, table_name VARCHAR(64) NOT NULL, "
                "status VARCHAR(16) NOT NULL, error_text VARCHAR(2048) NOT NULL, "
                "ranges_total INT NULL, ranges_succeed INT NULL, ranges_failed INT NULL, "
                "checksum_percent DECIMAL(5, 2) NULL, actor VARCHAR(32) NOT NULL, "
                "started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            ),
            f"create SF06 BR history table {self.history_relation}",
        )
        self._insert_history_noise(env)

    @staticmethod
    def _fixture_sql(env, sql: str) -> str:
        return env.execute_sql_with_timeout(sql, timeout_seconds=300)

    @staticmethod
    def _literal(value: object) -> str:
        return "'" + str(value).replace("'", "''") + "'"

    def _insert_source_rows(self, env) -> None:
        event_types = ("PAYMENT", "TRANSFER", "REFUND", "SETTLEMENT")
        for start in range(1, self.row_count + 1, 100):
            values = []
            for event_id in range(start, min(start + 100, self.row_count + 1)):
                values.append(
                    "(" + ", ".join((
                        str(event_id),
                        str((event_id % 32) + 1),
                        self._literal(event_types[event_id % len(event_types)]),
                        f"{(event_id * 17 % 100000) / 100:.2f}",
                        self._literal(f"acct-{event_id:04d}-risk-{event_id % 19}"),
                    )) + ")"
                )
            require_sql_success(
                self._fixture_sql(
                    env,
                    f"INSERT INTO {self.database}.{self.table} "
                    "(event_id, tenant_id, event_type, amount, payload) VALUES "
                    + ",".join(values)
                ),
                f"insert SF06 BR source rows starting at event_id={start}",
            )

    def _insert_credentials(self, env) -> None:
        rows = [
            (self.correct_credential_id, "br-prod-primary-v4", f"{self.database}.{self.table}", self.storage, self.correct_access_key, self.correct_secret_key, "active", "ledger-platform", "2026-07-30 02:00:00"),
            (self.fault_credential_id, "br-prod-primary-v3", f"{self.database}.{self.table}", self.storage, "retired-production-v3", "retired-production-v3-secret", "retired", "ledger-platform", "2026-07-15 02:00:00"),
            (903, "br-dr-rehearsal-v2", "dr-rehearsal", self._storage_for("dr-rehearsal"), "dr-access", "dr-secret", "active", "platform-dr", "2026-07-29 01:00:00"),
            (904, "br-analytics-v8", "analytics", self._storage_for("analytics"), "analytics-access", "analytics-secret", "active", "analytics", "2026-07-28 01:00:00"),
            (905, "br-ledger-archive-v7", "archive", self._storage_for("ledger-archive"), "archive-access", "archive-secret", "expired", "compliance", "2026-06-30 00:00:00"),
        ]
        # r4: the focused fixture trims background credential volume; its
        # difficulty comes from the derivation chain, not data size.
        credential_background = 80 if self.entity_decoys else 220
        rows.extend(
            (
                index,
                f"br-prod-overlap-v{index:03d}",
                f"{self.database}.{self.table}",
                self.storage,
                f"rotation-access-{index:03d}",
                f"rotation-secret-{index:03d}",
                "retired" if index % 7 == 0 else "active",
                "ledger-platform",
                f"2026-08-01 {(index % 23):02d}:00:00",
            )
            for index in range(1, credential_background + 1)
        )
        tenant_decoys = 8 if self.entity_decoys else 20
        rows.extend(
            (
                1000 + index,
                f"br-decoy-{index:03d}",
                f"tenant-{index:03d}",
                self._storage_for(f"decoy-{index:03d}"),
                f"decoy-access-{index:03d}",
                f"decoy-secret-{index:03d}",
                "active" if index % 2 else "retired",
                "service-catalog",
                f"2026-07-{(index % 28) + 1:02d} 03:00:00",
            )
            for index in range(1, tenant_decoys + 1)
        )
        rows.extend((
            (221, "credential-profile-7f2a", f"{self.database}.{self.table}", self.storage,
             "sf06-key-8f2a1c", "sf06-secret-4b7e", "active", "ledger-platform", "2026-08-01 23:00:00"),
            (222, "credential-profile-4c91", f"{self.database}.{self.table}", self.storage,
             "sf06-key-8f2a1c", "sf06-shadow-secret", "active", "ledger-platform", "2026-08-01 22:00:00"),
            (223, "br-prod-primary-v4-rehearsal", f"{self.database}.{self.table}/rehearsal", self._storage_for("br-permission/rehearsal"),
             "admission-rehearsal", "admission-rehearsal-secret", "active", "ledger-platform", "2026-08-01 21:00:00"),
        ))
        if self.entity_decoys:
            rows.extend((
                (_DECOY_CREDENTIAL_V5_ID, "br-prod-primary-v5", f"{self.database}.{self.table}", self.storage,
                 _DECOY_V5_ACCESS_KEY, "admission-v5-secret", "active", "ledger-platform", "2026-08-01 23:45:00"),
                (_DECOY_CREDENTIAL_V6_ID, "br-prod-primary-v6-canary", f"{self.database}.{self.table}", self.storage,
                 _DECOY_V6_ACCESS_KEY, "admission-v6-secret", "active", "ledger-platform", "2026-08-01 23:50:00"),
                (_DECOY_CREDENTIAL_V4_SHADOW_ID, "br-prod-primary-v4-shadow", f"{self.database}.{self.table}", self.storage,
                 _DECOY_V4_SHADOW_ACCESS_KEY, "admission-v4-shadow-secret", "active", "ledger-platform", "2026-07-31 02:00:00"),
            ))
        target_fingerprint = hashlib.sha256(self.fault_access_key.encode("utf-8")).hexdigest()[:16]
        values = ",".join(
            "(" + ", ".join(
                (
                    str(row[0]),
                    *(
                        self._literal(value)
                        for value in (
                            *row[1:5],
                            target_fingerprint if row[0] in {221, 222} else hashlib.sha256(str(row[4]).encode("utf-8")).hexdigest()[:16],
                            *row[5:],
                        )
                    ),
                )
            ) + ")"
            for row in sorted(rows, key=lambda row: row[0])
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.credentials_relation} "
                "(credential_id, profile_name, scope, storage_uri, access_key, access_key_fingerprint, "
                "secret_key, status, owner, last_rotated) "
                "VALUES " + values
            ),
            f"insert SF06 BR credentials into {self.credentials_relation}",
        )

    def _insert_credential_grants(self, env) -> None:
        target_scope = f"{self.database}.{self.table}"
        rows = (
            (1, self.correct_credential_id, target_scope, self.storage, "active", "2026-08-01 23:30:00", None, f"grant-set-{self.correct_credential_id}"),
            (2, 221, f"{target_scope}/rehearsal", self._storage_for("br-permission/rehearsal"), "active", "2026-08-01 23:00:00", None, "grant-set-221"),
            (3, 222, f"{target_scope}/rehearsal", self._storage_for("br-permission/rehearsal"), "active", "2026-08-01 22:00:00", None, "grant-set-4c91"),
            (4, 223, f"{target_scope}/rehearsal", self._storage_for("br-permission/rehearsal"), "active", "2026-08-01 21:00:00", None, "grant-set-223"),
            (5, 903, "dr-rehearsal", self._storage_for("dr-rehearsal"), "active", "2026-07-29 01:00:00", None, "grant-set-903"),
            (6, 904, "analytics", self._storage_for("analytics"), "active", "2026-07-28 01:00:00", None, "grant-set-904"),
            (7, 905, "archive", self._storage_for("ledger-archive"), "expired", "2026-06-30 01:00:00", None, "grant-set-905"),
            (8, self.fault_credential_id, f"{target_scope}/rehearsal", self._storage_for("br-permission/rehearsal"), "active", "2026-07-15 02:00:00", None, f"grant-set-{self.fault_credential_id}"),
        )
        if self.entity_decoys:
            rows = rows + (
                # Expired/closed rotation-wave production grants: they cover the
                # production URI but their validity ended before the failed
                # request started, so only grant-set-{correct} remains valid.
                (10, _DECOY_CREDENTIAL_V5_ID, target_scope, self.storage, "active", "2026-07-30 10:00:00", "2026-08-01 23:30:00", "grant-set-230-rotation"),
                (11, _DECOY_CREDENTIAL_V6_ID, target_scope, self.storage, "active", "2026-08-01 22:00:00", "2026-08-01 23:45:00", "grant-set-231-rotation"),
                (12, _DECOY_CREDENTIAL_V4_SHADOW_ID, f"{target_scope}/rehearsal", self._storage_for("br-permission/rehearsal"), "active", "2026-07-31 02:00:00", None, "grant-set-232-shadow"),
                (13, 221, target_scope, self.storage, "expired", "2026-07-25 02:00:00", None, "grant-set-221-revoked"),
                (14, 222, target_scope, self.storage, "active", "2026-07-20 02:00:00", "2026-07-28 02:00:00", "grant-set-222-historical"),
                (15, 903, target_scope, self.storage, "active", "2026-08-01 23:00:00", "2026-08-01 23:40:00", "grant-set-903-dr-window"),
                (16, 904, f"{target_scope}/rehearsal", self._storage_for("br-permission/rehearsal"), "active", "2026-07-28 01:00:00", None, "grant-set-904-audit"),
                (17, 1, target_scope, self.storage, "active", "2026-07-15 02:00:00", "2026-08-01 23:15:00", "grant-set-001-rotation"),
                # Same-credential previous-wave production grant: credential and
                # URI checks pass but the window closed before request start, so
                # only the lease whose desired grant is window-valid can refresh.
                (18, self.correct_credential_id, target_scope, self.storage, "active", "2026-07-01 02:00:00", "2026-08-01 23:40:00", f"grant-set-{self.correct_credential_id}-previous-wave"),
                (19, self.fault_credential_id, f"{target_scope}/rehearsal-2", self._storage_for("br-permission/rehearsal-2"), "active", "2026-07-20 02:00:00", None, f"grant-set-{self.fault_credential_id}-rehearsal-2"),
                (20, self.correct_credential_id, f"{target_scope}/rehearsal", self._storage_for("br-permission/rehearsal"), "active", "2026-07-25 02:00:00", None, f"grant-set-{self.correct_credential_id}-rehearsal"),
                # r5: shadow-rotation production grant for the v4-shadow decoy
                # credential with an OPEN window covering the failed request.
                # "active + production URI + request-time window" now matches
                # grants 1 and 21 across two candidate credentials, so the
                # causal credential must be pinned by the control-plane binding
                # candidate and the healthy worker's serving material instead
                # of a grants-table-only filter.
                (21, _DECOY_CREDENTIAL_V4_SHADOW_ID, target_scope, self.storage, "active", "2026-07-15 02:00:00", None, "grant-set-232-shadow-rotation"),
                # r7: the whole in-flight wave-2 canary set carries open-window
                # production grants, not just the v4-shadow credential. The
                # newer canary bindings (224/225/226) make every wave-2
                # credential look like the promotion target, so recency and
                # window filtering both point away from the causal credential;
                # only the serving currency of the healthy worker pins the
                # credential whose production grant is the reconcile target.
                (22, _DECOY_CREDENTIAL_V5_ID, target_scope, self.storage, "active", "2026-07-18 02:00:00", None, "grant-set-230-wave2"),
                (23, _DECOY_CREDENTIAL_V6_ID, target_scope, self.storage, "active", "2026-07-21 02:00:00", None, "grant-set-231-wave2"),
                # r8: the causal credential also holds an open-window grant on
                # a sibling table's production URI, so the desired-grant
                # derivation must check grant_scope and grant_uri together;
                # a URI-only or credential-only filter is ambiguous.
                (24, self.correct_credential_id, "benchops.settlement_events", self._storage_for("settlement"), "active", "2026-07-20 02:00:00", None, "grant-set-1901-settlement"),
            )
            # r5: grant_source carries no credential or wave semantics in the
            # focused authority model; ownership lives in the credential_id
            # column and wave timing in valid_from/valid_to, so grant selection
            # requires the window comparison instead of label reading.
            opaque_sources = {
                1: "igt-4b2a91", 2: "igt-9c1d70", 3: "igt-2e6f48", 4: "igt-7a30c5",
                5: "igt-c84d12", 6: "igt-51b9e7", 7: "igt-d2a660", 8: "igt-e97f03",
                10: "igt-16c8a4", 11: "igt-83f52b", 12: "igt-60d917", 13: "igt-2b47ce",
                14: "igt-a51093", 15: "igt-4e8d26", 16: "igt-f73b58", 17: "igt-19a640",
                18: "igt-95c2de", 19: "igt-7d40ab", 20: "igt-36e1fc", 21: "igt-b8a207",
                22: "igt-c3d94e", 23: "igt-5f81b6", 24: "igt-8e2a75",
            }
            rows = tuple(row[:7] + (opaque_sources[row[0]],) for row in rows)
        values = ",".join(
            "(" + ", ".join(
                "NULL" if value is None else self._literal(value)
                for value in row
            ) + ")"
            for row in rows
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.credential_grants_relation} "
                "(grant_id, credential_id, grant_scope, grant_uri, grant_state, valid_from, valid_to, grant_source) VALUES "
                + values,
            ),
            f"insert SF06 credential grants into {self.credential_grants_relation}",
        )

    def _insert_authority_leases(self, env) -> None:
        target_scope = f"{self.database}.{self.table}"
        rows = (
            (2, _HEALTHY_LEASE_TOKEN, 105, _HEALTHY_AUTHORITY_EPOCH, target_scope, 1, 1, 18, 18, "converged", "2026-08-01 23:30:00", None, "grant-watch-20260801-2330"),
            (3, _TARGET_LEASE_TOKEN, 3002, _GENERATION_SHADOW_EPOCH, target_scope, 3, 1, 16, 18, "stale", "2026-08-01 23:58:41", "2026-08-01 23:59:00", "grant-watch-20260801-2358-handoff"),
            (4, _REHEARSAL_LEASE_TOKEN, 104, _REHEARSAL_AUTHORITY_EPOCH, f"{target_scope}/rehearsal", 4, 4, 12, 12, "converged", "2026-08-01 22:00:00", None, "grant-watch-20260801-2250"),
            (5, _REPORTING_LEASE_TOKEN, 106, _REPORTING_AUTHORITY_EPOCH, "reporting.admission_events", 6, 6, 9, 9, "converged", "2026-08-01 23:30:00", None, "grant-watch-20260801-2320"),
            (6, _ARCHIVE_LEASE_TOKEN, 100, _ARCHIVE_AUTHORITY_EPOCH, "benchops.settlement_events", 7, 7, 20, 20, "expired", "2026-08-01 22:00:00", None, "grant-watch-20260801-2310"),
            (9, _STALE_SIBLING_LEASE_TOKEN, 103, _STALE_SIBLING_AUTHORITY_EPOCH, target_scope, 2, 1, 16, 18, "stale", "2026-08-01 23:30:00", "2026-08-01 23:58:30", "grant-watch-20260801-2330"),
            (_PREFLIGHT_AUTHORITY_LEASE_ID, _PREFLIGHT_LEASE_TOKEN, 3001, _PREFLIGHT_AUTHORITY_EPOCH, target_scope, 1, 1, 18, 18, "converged", "2026-08-01 23:58:39", "2026-08-01 23:58:41", _TARGET_CHANGE_REF),
            (17, _TARGET_LEASE_TOKEN, 3001, _TARGET_AUTHORITY_EPOCH, target_scope, 8, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
            (22, _TARGET_LEASE_TOKEN, 3001, _TARGET_AUTHORITY_EPOCH, target_scope, 3, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "watch-20260801-2358-a"),
            (18, _POST_HANDOFF_LEASE_TOKEN, 4001, _POST_HANDOFF_AUTHORITY_EPOCH, target_scope, 1, 1, 18, 18, "converged", "2026-08-01 23:59:00", None, "grant-watch-20260801-2359-handoff"),
            (19, _TARGET_LEASE_TOKEN, 3001, _AUTHORITY_HANDOFF_EPOCH, target_scope, 2, 1, 17, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "grant-watch-20260801-2358-epoch-shadow"),
            (20, _HEALTHY_LEASE_TOKEN, 3003, _SUPERSEDED_AUTHORITY_EPOCH, target_scope, 1, 1, 18, 18, "converged", "2026-08-01 23:58:45", "2026-08-01 23:58:46", "grant-watch-20260801-2358-superseded"),
            (21, _HEALTHY_LEASE_TOKEN, 3004, _LATE_HANDOFF_AUTHORITY_EPOCH, target_scope, 1, 1, 18, 18, "converged", "2026-08-01 23:58:46", "2026-08-01 23:58:48", "grant-watch-20260801-2358-late-handoff"),
            (23, _TARGET_LEASE_TOKEN, 3001, _TARGET_AUTHORITY_EPOCH, target_scope, 3, 1, 16, 18, "stale", "2026-08-01 23:58:48", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
            (_HEDGED_AUTHORITY_LEASE_ID, _HEDGED_LEASE_TOKEN, 3001, _HEDGED_AUTHORITY_EPOCH, target_scope, 3, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _HEDGED_CHANGE_REF),
            (_SECOND_CANDIDATE_AUTHORITY_LEASE_ID, _SECOND_CANDIDATE_LEASE_TOKEN, 3001, _SECOND_CANDIDATE_AUTHORITY_EPOCH, target_scope, 3, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _SECOND_CANDIDATE_CHANGE_REF),
            (_EXTRA_CANDIDATE_1_AUTHORITY_LEASE_ID, _EXTRA_CANDIDATE_1_LEASE_TOKEN, 3001, _EXTRA_CANDIDATE_1_AUTHORITY_EPOCH, target_scope, 2, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
            (_EXTRA_CANDIDATE_2_AUTHORITY_LEASE_ID, _EXTRA_CANDIDATE_2_LEASE_TOKEN, 3001, _EXTRA_CANDIDATE_2_AUTHORITY_EPOCH, target_scope, 3, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
            (_EXTRA_CANDIDATE_3_AUTHORITY_LEASE_ID, _EXTRA_CANDIDATE_3_LEASE_TOKEN, 3001, _EXTRA_CANDIDATE_3_AUTHORITY_EPOCH, target_scope, 2, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
            (_EXTRA_CANDIDATE_4_AUTHORITY_LEASE_ID, _EXTRA_CANDIDATE_4_LEASE_TOKEN, 3001, _EXTRA_CANDIDATE_4_AUTHORITY_EPOCH, target_scope, 3, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
            (_R61_CANDIDATE_1_AUTHORITY_LEASE_ID, _R61_CANDIDATE_1_LEASE_TOKEN, 3001, _R61_CANDIDATE_1_AUTHORITY_EPOCH, target_scope, 2, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
            (_R61_CANDIDATE_2_AUTHORITY_LEASE_ID, _R61_CANDIDATE_2_LEASE_TOKEN, 3001, _R61_CANDIDATE_2_AUTHORITY_EPOCH, target_scope, 3, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
            (_R61_CANDIDATE_3_AUTHORITY_LEASE_ID, _R61_CANDIDATE_3_LEASE_TOKEN, 3001, _R61_CANDIDATE_3_AUTHORITY_EPOCH, target_scope, 2, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
            (_R61_CANDIDATE_4_AUTHORITY_LEASE_ID, _R61_CANDIDATE_4_LEASE_TOKEN, 3001, _R61_CANDIDATE_4_AUTHORITY_EPOCH, target_scope, 3, 1, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
        )
        if self.entity_decoys:
            # r4: the focused authority model does not materialize the desired
            # grant on lease rows. Every focused lease row carries the sentinel
            # desired_grant_id=0 ("derive at reconcile time"), so no single
            # lease row or lease-table scan can read the repair pair.
            #
            # Shadow leases keep the target identity family but their observed
            # grants belong to other credentials, expired states, or the shadow
            # epoch, so each one fails no-state at the observed-material,
            # window, or epoch validation. Rows sharing observed grant 8 with
            # the full target identity would refresh successfully under the
            # sentinel model, so none may exist besides the causal lease 46.
            rows = rows + (
                (35, _TARGET_LEASE_TOKEN, 3001, _TARGET_AUTHORITY_EPOCH, target_scope, 12, 0, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
                (36, _TARGET_LEASE_TOKEN, 3001, _DECOY_AUTHORITY_SHADOW_EPOCH, target_scope, 10, 0, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
                (40, _TARGET_LEASE_TOKEN, 3001, _TARGET_AUTHORITY_EPOCH, target_scope, 13, 0, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
                (42, _TARGET_LEASE_TOKEN, 3001, _TARGET_AUTHORITY_EPOCH, target_scope, 15, 0, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
                (43, _TARGET_LEASE_TOKEN, 3001, _TARGET_AUTHORITY_EPOCH, target_scope, 14, 0, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
            )
            # The causal lease shadow family carries a lease id above every
            # decoy so no id-order heuristic selects it; the base causal row 17
            # is absent from this focused fixture. With the sentinel semantics,
            # its passing (observed, desired) pair is no longer readable: the
            # desired grant must be derived from the grants window.
            rows = tuple(row for row in rows if row[0] != 17) + (
                (46, _TARGET_LEASE_TOKEN, 3001, _TARGET_AUTHORITY_EPOCH, target_scope, 8, 0, 16, 18, "stale", "2026-08-01 23:58:40", "2026-08-01 23:59:00", _TARGET_CHANGE_REF),
                # r8: the rotation-watch canary workers' own authority chains
                # converged after the rotation (observed=desired=grant 1), so
                # "which chain still needs reconciling" requires the request
                # identity join rather than a scan for stale production rows.
                (47, _WATCH4_LEASE_TOKEN, 105, _WATCH4_AUTHORITY_EPOCH, target_scope, 1, 1, 18, 18, "converged", "2026-08-01 23:58:45", None, "br-rotation-watch-20260801-2358-handoff"),
                (48, _WATCH5_LEASE_TOKEN, 105, _WATCH5_AUTHORITY_EPOCH, target_scope, 1, 1, 18, 18, "converged", "2026-08-01 23:58:46", None, "br-rotation-watch-20260801-2358-handoff"),
            )
            rows = tuple(row[:6] + (0,) + row[7:] for row in rows)
        def assignment_fence(row) -> str:
            if row[0] == _PREFLIGHT_AUTHORITY_LEASE_ID:
                return _TARGET_ASSIGNMENT_FENCE
            if row[0] == 17:
                return _TARGET_ASSIGNMENT_FENCE
            if row[0] == 23:
                return _REQUEST_ASSIGNMENT_REPLAY_FENCE
            if row[0] == 22:
                return _WATCH_REPLAY_ASSIGNMENT_FENCE
            if row[0] == _HEDGED_AUTHORITY_LEASE_ID:
                return _TARGET_ASSIGNMENT_FENCE
            if row[0] == _SECOND_CANDIDATE_AUTHORITY_LEASE_ID:
                return _TARGET_ASSIGNMENT_FENCE
            if row[0] in {
                _EXTRA_CANDIDATE_1_AUTHORITY_LEASE_ID,
                _EXTRA_CANDIDATE_2_AUTHORITY_LEASE_ID,
                _EXTRA_CANDIDATE_3_AUTHORITY_LEASE_ID,
                _EXTRA_CANDIDATE_4_AUTHORITY_LEASE_ID,
                _R61_CANDIDATE_1_AUTHORITY_LEASE_ID,
                _R61_CANDIDATE_2_AUTHORITY_LEASE_ID,
                _R61_CANDIDATE_3_AUTHORITY_LEASE_ID,
                _R61_CANDIDATE_4_AUTHORITY_LEASE_ID,
                35,
                36,
                40,
                42,
                43,
                46,
            }:
                return _TARGET_ASSIGNMENT_FENCE
            return f"af-authority-{row[0]}"

        def request_context(row) -> str:
            return {
                _PREFLIGHT_AUTHORITY_LEASE_ID: _TARGET_REQUEST_CONTEXT,
                17: _TARGET_REQUEST_CONTEXT,
                23: _REQUEST_ASSIGNMENT_REPLAY_CONTEXT,
                22: _WATCH_REPLAY_REQUEST_CONTEXT,
                _HEDGED_AUTHORITY_LEASE_ID: _TARGET_REQUEST_CONTEXT,
                _SECOND_CANDIDATE_AUTHORITY_LEASE_ID: _TARGET_REQUEST_CONTEXT,
                _EXTRA_CANDIDATE_1_AUTHORITY_LEASE_ID: _TARGET_REQUEST_CONTEXT,
                _EXTRA_CANDIDATE_2_AUTHORITY_LEASE_ID: _TARGET_REQUEST_CONTEXT,
                _EXTRA_CANDIDATE_3_AUTHORITY_LEASE_ID: _TARGET_REQUEST_CONTEXT,
                _EXTRA_CANDIDATE_4_AUTHORITY_LEASE_ID: _TARGET_REQUEST_CONTEXT,
                _R61_CANDIDATE_1_AUTHORITY_LEASE_ID: _TARGET_REQUEST_CONTEXT,
                _R61_CANDIDATE_2_AUTHORITY_LEASE_ID: _TARGET_REQUEST_CONTEXT,
                _R61_CANDIDATE_3_AUTHORITY_LEASE_ID: _TARGET_REQUEST_CONTEXT,
                _R61_CANDIDATE_4_AUTHORITY_LEASE_ID: _TARGET_REQUEST_CONTEXT,
                35: _TARGET_REQUEST_CONTEXT,
                36: _TARGET_REQUEST_CONTEXT,
                40: _TARGET_REQUEST_CONTEXT,
                42: _TARGET_REQUEST_CONTEXT,
                43: _TARGET_REQUEST_CONTEXT,
                46: _TARGET_REQUEST_CONTEXT,
            }.get(row[0], f"ctx-authority-{row[0]}")

        def execution_phase(row) -> str:
            return {
                _PREFLIGHT_AUTHORITY_LEASE_ID: _TARGET_EXECUTION_PHASE,
                17: _TARGET_EXECUTION_PHASE,
                23: _REPLAY_EXECUTION_PHASE,
                22: _REPLAY_EXECUTION_PHASE,
                _HEDGED_AUTHORITY_LEASE_ID: _HANDOFF_EXECUTION_PHASE,
                _SECOND_CANDIDATE_AUTHORITY_LEASE_ID: _TARGET_EXECUTION_PHASE,
                _EXTRA_CANDIDATE_1_AUTHORITY_LEASE_ID: _TARGET_EXECUTION_PHASE,
                _EXTRA_CANDIDATE_2_AUTHORITY_LEASE_ID: _HANDOFF_EXECUTION_PHASE,
                _EXTRA_CANDIDATE_3_AUTHORITY_LEASE_ID: _TARGET_EXECUTION_PHASE,
                _EXTRA_CANDIDATE_4_AUTHORITY_LEASE_ID: _HANDOFF_EXECUTION_PHASE,
                _R61_CANDIDATE_1_AUTHORITY_LEASE_ID: _TARGET_EXECUTION_PHASE,
                _R61_CANDIDATE_2_AUTHORITY_LEASE_ID: _HANDOFF_EXECUTION_PHASE,
                _R61_CANDIDATE_3_AUTHORITY_LEASE_ID: _TARGET_EXECUTION_PHASE,
                _R61_CANDIDATE_4_AUTHORITY_LEASE_ID: _HANDOFF_EXECUTION_PHASE,
                35: _TARGET_EXECUTION_PHASE,
                36: _TARGET_EXECUTION_PHASE,
                40: _TARGET_EXECUTION_PHASE,
                42: _TARGET_EXECUTION_PHASE,
                43: _TARGET_EXECUTION_PHASE,
                46: _TARGET_EXECUTION_PHASE,
            }.get(row[0], "control_plane")

        def execution_reason(row) -> str:
            return {
                _PREFLIGHT_AUTHORITY_LEASE_ID: "read-before-write",
                17: _TARGET_EXECUTION_REASON,
                23: _REPLAY_EXECUTION_REASON,
                22: _TARGET_EXECUTION_REASON,
                _HEDGED_AUTHORITY_LEASE_ID: _HANDOFF_EXECUTION_REASON,
                _SECOND_CANDIDATE_AUTHORITY_LEASE_ID: _TARGET_EXECUTION_REASON,
                _EXTRA_CANDIDATE_1_AUTHORITY_LEASE_ID: _TARGET_EXECUTION_REASON,
                _EXTRA_CANDIDATE_2_AUTHORITY_LEASE_ID: _HANDOFF_EXECUTION_REASON,
                _EXTRA_CANDIDATE_3_AUTHORITY_LEASE_ID: _TARGET_EXECUTION_REASON,
                _EXTRA_CANDIDATE_4_AUTHORITY_LEASE_ID: _HANDOFF_EXECUTION_REASON,
                _R61_CANDIDATE_1_AUTHORITY_LEASE_ID: _TARGET_EXECUTION_REASON,
                _R61_CANDIDATE_2_AUTHORITY_LEASE_ID: _HANDOFF_EXECUTION_REASON,
                _R61_CANDIDATE_3_AUTHORITY_LEASE_ID: _TARGET_EXECUTION_REASON,
                _R61_CANDIDATE_4_AUTHORITY_LEASE_ID: _HANDOFF_EXECUTION_REASON,
                35: _TARGET_EXECUTION_REASON,
                36: _TARGET_EXECUTION_REASON,
                40: _TARGET_EXECUTION_REASON,
                42: _TARGET_EXECUTION_REASON,
                43: _TARGET_EXECUTION_REASON,
                46: _TARGET_EXECUTION_REASON,
            }.get(row[0], "authority-lease-observation")

        values = ",".join(
            "(" + ", ".join(
                "NULL" if value is None else self._literal(value)
                for value in (
                    *row,
                    assignment_fence(row),
                    request_context(row),
                    execution_phase(row),
                    execution_reason(row),
                )
            ) + ")"
            for row in rows
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.authority_leases_relation} "
                "(lease_id, lease_token, assignment_generation, authority_epoch, target_scope, observed_grant_id, desired_grant_id, observed_revision, "
                "desired_revision, lease_state, valid_from, valid_to, change_ref, request_assignment_fence, request_context_token, execution_phase, execution_reason) VALUES " + values,
            ),
            f"insert SF06 authority grant leases into {self.authority_leases_relation}",
        )

    def _insert_bindings(self, env) -> None:
        rows = [
            (self.effective_binding_id, f"{self.database}.{self.table}", self.fault_credential_id, "primary", "effective", "2026-07-30 02:00:00", None, "chg-bind-0730"),
            (self.candidate_binding_id, f"{self.database}.{self.table}", self.correct_credential_id, "primary", "canary", "2026-08-07 00:09:00", None, "chg-bind-0809"),
        ]
        # r4: the focused fixture trims background binding volume to match the
        # trimmed credential inventory; sibling volume is unchanged.
        binding_background = 80 if self.entity_decoys else 219
        rows.extend(
            (
                index,
                f"{self.database}.{self.table}",
                index,
                "canary" if index % 3 == 0 else "primary",
                "pending" if index % 4 else "rolled_back",
                f"2026-08-01 {(index % 23):02d}:00:00",
                None,
                f"IAM-2026-08-{(index % 28) + 1:02d}-{index:03d}",
            )
            for index in range(1, binding_background + 1)
        )
        tenant_decoys = 8 if self.entity_decoys else 20
        rows.extend(
            (
                2000 + index,
                f"tenant-{index:03d}",
                1000 + index,
                "secondary",
                "effective" if index % 2 else "retired",
                f"2026-07-{(index % 28) + 1:02d} 04:00:00",
                None,
                f"IAM-OTHER-{index:03d}",
            )
            for index in range(1, tenant_decoys + 1)
        )
        rows.extend((
            (221, f"{self.database}.{self.table}", 221, "primary", "canary", "2026-08-01 23:00:00", None, "IAM-2026-0801-PRIMARY-V5-CANARY"),
            (222, f"{self.database}.{self.table}", 222, "primary", "canary", "2026-08-01 22:00:00", None, "IAM-2026-0801-ROTATE-47-CANARY"),
            (223, f"{self.database}.{self.table}", 223, "primary", "canary", "2026-08-01 21:00:00", None, "IAM-2026-0801-PRIMARY-V4-REHEARSAL"),
        ))
        if self.entity_decoys:
            # Newer production-scope canary bindings than the true candidate:
            # recency and profile naming alone cannot select the repair target,
            # only the active production-URI grant chain can.
            # r8: the whole wave-2 stage was rolled back mid-flight while its
            # pre-authorization grants stay window-open, and the true
            # candidate's own wave-1 canary had a rolled-back false start, so
            # neither "newest binding" nor "any canary binding of the correct
            # credential" selects the reconcile target by itself.
            rows.extend((
                (224, f"{self.database}.{self.table}", _DECOY_CREDENTIAL_V5_ID, "primary", "rolled_back", "2026-08-08 09:00:00", "2026-08-09 21:00:00", "IAM-2026-0808-PRIMARY-V5-CANARY"),
                (225, f"{self.database}.{self.table}", _DECOY_CREDENTIAL_V6_ID, "primary", "rolled_back", "2026-08-09 10:00:00", "2026-08-09 21:00:00", "IAM-2026-0809-PRIMARY-V6-CANARY"),
                (226, f"{self.database}.{self.table}", _DECOY_CREDENTIAL_V4_SHADOW_ID, "primary", "rolled_back", "2026-08-10 11:00:00", "2026-08-10 21:00:00", "IAM-2026-0810-PRIMARY-V4-SHADOW-CANARY"),
                (227, f"{self.database}.{self.table}", self.correct_credential_id, "primary", "rolled_back", "2026-07-28 02:00:00", "2026-07-29 18:00:00", "IAM-2026-0728-PRIMARY-V4-FALSE-START"),
            ))
        values = ",".join(
            "(" + ", ".join((str(row[0]), self._literal(row[1]), str(row[2]), self._literal(row[3]), self._literal(row[4]), self._literal(row[5]), "NULL" if row[6] is None else self._literal(row[6]), self._literal(row[7]))) + ")"
            for row in sorted(rows, key=lambda row: row[0])
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.bindings_relation} "
                "(binding_id, target_scope, credential_id, role, binding_state, effective_from, effective_to, change_ticket) VALUES "
                + values
            ),
            f"insert SF06 BR runtime bindings into {self.bindings_relation}",
        )

    def _insert_worker_materials(self, env) -> None:
        target_scope = f"{self.database}.{self.table}"
        rows = (
            (
                _PRODUCTION_MATERIAL_HANDLE,
                self.correct_credential_id,
                target_scope,
                self.storage,
                hashlib.sha256(self.correct_access_key.encode()).hexdigest()[:16],
                "active",
                "2026-08-01 23:30:00",
                None,
                "IAM-2026-0801-PRIMARY-ROTATION",
            ),
            (
                _TARGET_MATERIAL_HANDLE,
                self.fault_credential_id,
                target_scope,
                self.storage,
                hashlib.sha256(self.fault_access_key.encode()).hexdigest()[:16],
                "active",
                "2026-08-01 23:00:00",
                None,
                "IAM-2026-0801-ROTATE-47",
            ),
            (
                _REHEARSAL_MATERIAL_HANDLE,
                223,
                f"{target_scope}/rehearsal",
                self._storage_for("br-permission/rehearsal"),
                "165dace3924038be",
                "active",
                "2026-08-01 21:00:00",
                None,
                "IAM-2026-0801-PRIMARY-V4-REHEARSAL",
            ),
            (
                _REPORTING_MATERIAL_HANDLE,
                904,
                "reporting.admission_events",
                self._storage_for("reporting-admission"),
                "analytics-fp",
                "active",
                "2026-08-01 23:30:00",
                None,
                "REPORTING-2026-0801",
            ),
            (
                _ARCHIVE_MATERIAL_HANDLE,
                905,
                "benchops.settlement_events",
                self._storage_for("settlement"),
                "archive-fp",
                "expired",
                "2026-08-01 22:00:00",
                None,
                "ARCHIVE-2026-0801",
            ),
            (
                "mh-retired-9021",
                self.fault_credential_id,
                target_scope,
                self.storage,
                hashlib.sha256("retired-production-v3".encode()).hexdigest()[:16],
                "retired",
                "2026-07-15 02:00:00",
                "2026-08-01 23:30:00",
                "IAM-2026-0801-PRIMARY-ROTATION",
            ),
            (
                _HEDGED_MATERIAL_HANDLE,
                self.fault_credential_id,
                target_scope,
                self.storage,
                hashlib.sha256(self.fault_access_key.encode("utf-8")).hexdigest()[:16],
                "active",
                "2026-08-01 22:00:00",
                None,
                "IAM-2026-0801-ROTATE-47-CANARY",
            ),
            (
                _SECOND_CANDIDATE_MATERIAL_HANDLE,
                222,
                target_scope,
                self.storage,
                hashlib.sha256(self.fault_access_key.encode("utf-8")).hexdigest()[:16],
                "active",
                "2026-08-01 23:00:00",
                None,
                "IAM-2026-0801-ROTATE-47-CANARY-SHADOW",
            ),
        )
        if self.entity_decoys:
            rows = rows + (
                (
                    _DECOY_V5_MATERIAL_HANDLE,
                    _DECOY_CREDENTIAL_V5_ID,
                    target_scope,
                    self.storage,
                    hashlib.sha256(_DECOY_V5_ACCESS_KEY.encode("utf-8")).hexdigest()[:16],
                    "active",
                    "2026-08-01 23:45:00",
                    None,
                    "IAM-2026-0808-PRIMARY-V5-CANARY",
                ),
                (
                    _DECOY_V6_MATERIAL_HANDLE,
                    _DECOY_CREDENTIAL_V6_ID,
                    target_scope,
                    self.storage,
                    hashlib.sha256(_DECOY_V6_ACCESS_KEY.encode("utf-8")).hexdigest()[:16],
                    "active",
                    "2026-08-01 23:50:00",
                    None,
                    "IAM-2026-0809-PRIMARY-V6-CANARY",
                ),
                (
                    _DECOY_V4_SHADOW_MATERIAL_HANDLE,
                    _DECOY_CREDENTIAL_V4_SHADOW_ID,
                    target_scope,
                    self.storage,
                    hashlib.sha256(_DECOY_V4_SHADOW_ACCESS_KEY.encode("utf-8")).hexdigest()[:16],
                    "active",
                    "2026-07-31 02:00:00",
                    None,
                    "IAM-2026-0810-PRIMARY-V4-SHADOW-CANARY",
                ),
            )
        values = ",".join(
            "(" + ", ".join(
                (self._literal(value) if value is not None else "NULL")
                for value in row
            ) + ")"
            for row in rows
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.worker_materials_relation} "
                "(material_handle, credential_id, target_scope, storage_uri, material_digest, material_status, "
                "valid_from, valid_to, rotation_source) VALUES " + values,
            ),
            f"insert SF06 BR worker materials into {self.worker_materials_relation}",
        )

    def _insert_worker_leases(self, env) -> None:
        rows = [
            (
                1,
                _TARGET_LEASE_TOKEN,
                3002,
                _GENERATION_SHADOW_EPOCH,
                "br-worker-2",
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                self.observed_revision,
                _PRODUCTION_MATERIAL_HANDLE,
                "converged",
                "2026-08-01 23:58:31",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:41",
                _TARGET_CHANGE_REF,
            ),
            (
                18,
                _PREFLIGHT_LEASE_TOKEN,
                3001,
                _PREFLIGHT_AUTHORITY_EPOCH,
                "br-worker-0",
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                self.desired_revision,
                _PRODUCTION_MATERIAL_HANDLE,
                "converged",
                "2026-08-01 23:58:39",
                "2026-08-01 23:58:41",
                "2026-08-01 23:58:40",
                _TARGET_CHANGE_REF,
            ),
            (
                2,
                _HEALTHY_LEASE_TOKEN,
                105,
                _HEALTHY_AUTHORITY_EPOCH,
                "br-worker-1",
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                self.desired_revision,
                _PRODUCTION_MATERIAL_HANDLE,
                "converged",
                "2026-08-01 23:30:00",
                None,
                "2026-08-01 23:59:59",
                "br-rotation-watch-20260801-2330",
            ),
            (
                3,
                _REHEARSAL_LEASE_TOKEN,
                104,
                _REHEARSAL_AUTHORITY_EPOCH,
                "br-worker-0",
                f"{self.database}.{self.table}/rehearsal",
                self._storage_for("br-permission/rehearsal"),
                901,
                12,
                901,
                12,
                _REHEARSAL_MATERIAL_HANDLE,
                "converged",
                "2026-08-01 22:00:00",
                None,
                "2026-08-01 23:55:08",
                "br-rehearsal-20260801-2250",
            ),
            (
                4,
                _STALE_SIBLING_LEASE_TOKEN,
                103,
                _STALE_SIBLING_AUTHORITY_EPOCH,
                "br-worker-2",
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _TARGET_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:31",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:45",
                "br-rotation-watch-20260801-2330",
            ),
            (
                5,
                _REPORTING_LEASE_TOKEN,
                106,
                _REPORTING_AUTHORITY_EPOCH,
                "br-worker-2",
                "reporting.admission_events",
                self._storage_for("reporting-admission"),
                930,
                8,
                930,
                8,
                _REPORTING_MATERIAL_HANDLE,
                "converged",
                "2026-08-01 23:30:00",
                None,
                "2026-08-01 23:59:12",
                "reporting-watch-20260801-2320",
            ),
            (
                6,
                _ARCHIVE_LEASE_TOKEN,
                100,
                _ARCHIVE_AUTHORITY_EPOCH,
                "br-worker-3",
                "benchops.settlement_events",
                self._storage_for("settlement"),
                940,
                21,
                940,
                20,
                _ARCHIVE_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 22:00:00",
                None,
                "2026-08-01 23:56:48",
                "archive-watch-20260801-2310",
            ),
            (
                7,
                _POST_HANDOFF_LEASE_TOKEN,
                4001,
                _POST_HANDOFF_AUTHORITY_EPOCH,
                "br-worker-0",
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                self.desired_revision,
                _PRODUCTION_MATERIAL_HANDLE,
                "converged",
                "2026-08-01 23:59:00",
                None,
                "2026-08-01 23:59:58",
                "br-rotation-watch-20260801-2359-handoff",
            ),
            (
                8,
                _TARGET_LEASE_TOKEN,
                3001,
                _TARGET_AUTHORITY_EPOCH,
                "br-worker-0",
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _TARGET_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:47",
                _TARGET_CHANGE_REF,
            ),
            (
                9,
                _HEALTHY_LEASE_TOKEN,
                3001,
                _SUPERSEDED_AUTHORITY_EPOCH,
                "br-worker-1",
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                self.desired_revision,
                _PRODUCTION_MATERIAL_HANDLE,
                "converged",
                "2026-08-01 23:58:45",
                "2026-08-01 23:58:46",
                "2026-08-01 23:58:46",
                "br-rotation-watch-20260801-2358-superseded",
            ),
            (
                10,
                _HEALTHY_LEASE_TOKEN,
                3004,
                _LATE_HANDOFF_AUTHORITY_EPOCH,
                "br-worker-1",
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                self.desired_revision,
                _PRODUCTION_MATERIAL_HANDLE,
                "converged",
                "2026-08-01 23:58:46",
                "2026-08-01 23:58:48",
                "2026-08-01 23:58:47",
                "br-rotation-watch-20260801-2358-late-handoff",
            ),
            (
                11,
                _TARGET_LEASE_TOKEN,
                3001,
                _TARGET_AUTHORITY_EPOCH,
                "br-worker-0",
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _HEDGED_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:48",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:48",
                _TARGET_CHANGE_REF,
            ),
            (
                12,
                _HEDGED_LEASE_TOKEN,
                3001,
                _HEDGED_AUTHORITY_EPOCH,
                self.target_worker,
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _HEDGED_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:47",
                _HEDGED_CHANGE_REF,
            ),
            (
                13,
                _SECOND_CANDIDATE_LEASE_TOKEN,
                3001,
                _SECOND_CANDIDATE_AUTHORITY_EPOCH,
                self.target_worker,
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _SECOND_CANDIDATE_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:47",
                _SECOND_CANDIDATE_CHANGE_REF,
            ),
            (
                14,
                _EXTRA_CANDIDATE_1_LEASE_TOKEN,
                3001,
                _EXTRA_CANDIDATE_1_AUTHORITY_EPOCH,
                self.target_worker,
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _EXTRA_CANDIDATE_1_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:47",
                _TARGET_CHANGE_REF,
            ),
            (
                15,
                _EXTRA_CANDIDATE_2_LEASE_TOKEN,
                3001,
                _EXTRA_CANDIDATE_2_AUTHORITY_EPOCH,
                self.target_worker,
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _EXTRA_CANDIDATE_2_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:47",
                _TARGET_CHANGE_REF,
            ),
            (
                16,
                _EXTRA_CANDIDATE_3_LEASE_TOKEN,
                3001,
                _EXTRA_CANDIDATE_3_AUTHORITY_EPOCH,
                self.target_worker,
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _EXTRA_CANDIDATE_3_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:47",
                _TARGET_CHANGE_REF,
            ),
            (
                17,
                _EXTRA_CANDIDATE_4_LEASE_TOKEN,
                3001,
                _EXTRA_CANDIDATE_4_AUTHORITY_EPOCH,
                self.target_worker,
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _EXTRA_CANDIDATE_4_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:47",
                _TARGET_CHANGE_REF,
            ),
            (
                19,
                _R61_CANDIDATE_1_LEASE_TOKEN,
                3001,
                _R61_CANDIDATE_1_AUTHORITY_EPOCH,
                self.target_worker,
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _R61_CANDIDATE_1_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:47",
                _TARGET_CHANGE_REF,
            ),
            (
                20,
                _R61_CANDIDATE_2_LEASE_TOKEN,
                3001,
                _R61_CANDIDATE_2_AUTHORITY_EPOCH,
                self.target_worker,
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _R61_CANDIDATE_2_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:47",
                _TARGET_CHANGE_REF,
            ),
            (
                21,
                _R61_CANDIDATE_3_LEASE_TOKEN,
                3001,
                _R61_CANDIDATE_3_AUTHORITY_EPOCH,
                self.target_worker,
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _R61_CANDIDATE_3_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:47",
                _TARGET_CHANGE_REF,
            ),
            (
                22,
                _R61_CANDIDATE_4_LEASE_TOKEN,
                3001,
                _R61_CANDIDATE_4_AUTHORITY_EPOCH,
                self.target_worker,
                f"{self.database}.{self.table}",
                self.storage,
                900,
                self.desired_revision,
                900,
                16,
                _R61_CANDIDATE_4_MATERIAL_HANDLE,
                "stale",
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "2026-08-01 23:58:47",
                _TARGET_CHANGE_REF,
            ),
        ]
        if self.entity_decoys:
            # r8: the healthy sibling's own serving history is time-phased —
            # until 23:58:45 it served the same stale production-credential
            # material as the incident worker, and the rotation-watch canary
            # workers converged onto the production material after the
            # rotation. "What is currently serving what" therefore requires
            # revision/window discrimination across several converged rows
            # instead of a single healthy-peer lookup.
            rows = rows + [
                (
                    23,
                    _HEALTHY_LEASE_TOKEN,
                    104,
                    _SUPERSEDED_AUTHORITY_EPOCH,
                    "br-worker-1",
                    f"{self.database}.{self.table}",
                    self.storage,
                    900,
                    16,
                    900,
                    16,
                    _TARGET_MATERIAL_HANDLE,
                    "converged",
                    "2026-08-01 23:30:00",
                    "2026-08-01 23:58:45",
                    "2026-08-01 23:58:45",
                    "br-rotation-watch-20260801-2330",
                ),
                (
                    24,
                    _WATCH4_LEASE_TOKEN,
                    105,
                    _WATCH4_AUTHORITY_EPOCH,
                    "br-worker-4",
                    f"{self.database}.{self.table}",
                    self.storage,
                    900,
                    self.desired_revision,
                    900,
                    self.desired_revision,
                    _PRODUCTION_MATERIAL_HANDLE,
                    "converged",
                    "2026-08-01 23:58:45",
                    None,
                    "2026-08-01 23:59:52",
                    "br-rotation-watch-20260801-2358-handoff",
                ),
                (
                    25,
                    _WATCH5_LEASE_TOKEN,
                    105,
                    _WATCH5_AUTHORITY_EPOCH,
                    "br-worker-5",
                    f"{self.database}.{self.table}",
                    self.storage,
                    900,
                    self.desired_revision,
                    900,
                    self.desired_revision,
                    _PRODUCTION_MATERIAL_HANDLE,
                    "converged",
                    "2026-08-01 23:58:46",
                    None,
                    "2026-08-01 23:59:55",
                    "br-rotation-watch-20260801-2358-handoff",
                ),
            ]
        def assignment_fence(row) -> str:
            return {
                18: _TARGET_ASSIGNMENT_FENCE,
                8: _TARGET_ASSIGNMENT_FENCE,
                11: _REQUEST_ASSIGNMENT_REPLAY_FENCE,
                12: _TARGET_ASSIGNMENT_FENCE,
                13: _TARGET_ASSIGNMENT_FENCE,
                14: _TARGET_ASSIGNMENT_FENCE,
                15: _TARGET_ASSIGNMENT_FENCE,
                16: _TARGET_ASSIGNMENT_FENCE,
                17: _TARGET_ASSIGNMENT_FENCE,
                19: _TARGET_ASSIGNMENT_FENCE,
                20: _TARGET_ASSIGNMENT_FENCE,
                21: _TARGET_ASSIGNMENT_FENCE,
                22: _TARGET_ASSIGNMENT_FENCE,
            }.get(row[0], f"af-worker-{row[0]}")

        def request_context(row) -> str:
            return {
                18: _TARGET_REQUEST_CONTEXT,
                8: _TARGET_REQUEST_CONTEXT,
                11: _REQUEST_ASSIGNMENT_REPLAY_CONTEXT,
                12: _TARGET_REQUEST_CONTEXT,
                13: _TARGET_REQUEST_CONTEXT,
                14: _TARGET_REQUEST_CONTEXT,
                15: _TARGET_REQUEST_CONTEXT,
                16: _TARGET_REQUEST_CONTEXT,
                17: _TARGET_REQUEST_CONTEXT,
                19: _TARGET_REQUEST_CONTEXT,
                20: _TARGET_REQUEST_CONTEXT,
                21: _TARGET_REQUEST_CONTEXT,
                22: _TARGET_REQUEST_CONTEXT,
            }.get(row[0], f"ctx-worker-{row[0]}")

        def execution_phase(row) -> str:
            return {
                18: _TARGET_EXECUTION_PHASE,
                8: _TARGET_EXECUTION_PHASE,
                11: _REPLAY_EXECUTION_PHASE,
                12: _HANDOFF_EXECUTION_PHASE,
                13: _TARGET_EXECUTION_PHASE,
                14: _TARGET_EXECUTION_PHASE,
                15: _HANDOFF_EXECUTION_PHASE,
                16: _TARGET_EXECUTION_PHASE,
                17: _HANDOFF_EXECUTION_PHASE,
                19: _TARGET_EXECUTION_PHASE,
                20: _HANDOFF_EXECUTION_PHASE,
                21: _TARGET_EXECUTION_PHASE,
                22: _HANDOFF_EXECUTION_PHASE,
            }.get(row[0], "control_plane")

        def execution_reason(row) -> str:
            return {
                18: "read-before-write",
                8: _TARGET_EXECUTION_REASON,
                11: _REPLAY_EXECUTION_REASON,
                12: _HANDOFF_EXECUTION_REASON,
                13: _TARGET_EXECUTION_REASON,
                14: _TARGET_EXECUTION_REASON,
                15: _HANDOFF_EXECUTION_REASON,
                16: _TARGET_EXECUTION_REASON,
                17: _HANDOFF_EXECUTION_REASON,
                19: _TARGET_EXECUTION_REASON,
                20: _HANDOFF_EXECUTION_REASON,
                21: _TARGET_EXECUTION_REASON,
                22: _HANDOFF_EXECUTION_REASON,
            }.get(row[0], "worker-lease-observation")

        values = ",".join(
            "(" + ", ".join(
                (str(row[0]), *(
                    "NULL" if value is None else self._literal(value)
                    for value in (
                        *row[1:],
                        assignment_fence(row),
                        request_context(row),
                        execution_phase(row),
                        execution_reason(row),
                    )
                ))
            ) + ")"
            for row in rows
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.worker_leases_relation} "
                "(lease_id, lease_token, assignment_generation, authority_epoch, worker_id, target_scope, storage_uri, desired_binding_id, desired_revision, "
                "observed_binding_id, observed_revision, observed_material_handle, lease_state, "
                "valid_from, valid_to, last_heartbeat, change_ref, request_assignment_fence, request_context_token, execution_phase, execution_reason) VALUES "
                + values,
            ),
            f"insert SF06 BR worker leases into {self.worker_leases_relation}",
        )

    def _insert_worker_registry(self, env) -> None:
        rows = [
            (10, self.target_executor_handle, _TARGET_LEASE_TOKEN, 3001, _TARGET_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "active"),
            (19, self.target_executor_handle, _PREFLIGHT_LEASE_TOKEN, 3001, _TARGET_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:39", "2026-08-01 23:58:41", "released"),
            (2, self.target_executor_handle, _STALE_SIBLING_LEASE_TOKEN, 102, "wh-91d4c6a2", f"{self.database}.{self.table}", "2026-07-01 00:00:00", "2026-08-01 23:29:59", "retired"),
            (3, "writer-slot-b", _HEALTHY_LEASE_TOKEN, 105, "wh-5a0e7b19", f"{self.database}.{self.table}", "2026-08-01 23:30:00", None, "active"),
            (4, "rehearsal-slot", _REHEARSAL_LEASE_TOKEN, 104, "wh-c8e2a630", f"{self.database}.{self.table}/rehearsal", "2026-08-01 22:00:00", None, "active"),
            (5, "writer-slot-c", _REPORTING_LEASE_TOKEN, 106, "wh-4b7d1f82", "reporting.admission_events", "2026-08-01 23:30:00", None, "active"),
            (6, "archive-slot", _ARCHIVE_LEASE_TOKEN, 100, "wh-a6c3e905", "benchops.settlement_events", "2026-08-01 22:00:00", None, "active"),
            (7, "writer-slot-b", _POST_HANDOFF_LEASE_TOKEN, 102, "wh-2d9f6b40", f"{self.database}.{self.table}", "2026-07-01 00:00:00", "2026-08-01 23:29:59", "retired"),
            (8, "writer-slot-c", _REPORTING_LEASE_TOKEN, 106, "wh-e1a5c7d3", "reporting.admission_events", "2026-07-01 00:00:00", "2026-08-01 23:29:59", "retired"),
            (9, self.target_executor_handle, _STALE_SIBLING_LEASE_TOKEN, 103, "wh-6b0f2a84", f"{self.database}.{self.table}", "2026-08-01 23:30:00", "2026-08-01 23:58:30", "active"),
            (1, self.target_executor_handle, _TARGET_LEASE_TOKEN, 3002, _SHADOW_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:31", "2026-08-02 00:30:00", "active"),
            (11, "writer-slot-b", _HEALTHY_LEASE_TOKEN, 3003, "wh-5a0e7b19", f"{self.database}.{self.table}", "2026-08-01 23:58:45", "2026-08-01 23:58:46", "released"),
            (12, "writer-slot-b", _HEALTHY_LEASE_TOKEN, 3004, "wh-5a0e7b19", f"{self.database}.{self.table}", "2026-08-01 23:58:46", "2026-08-01 23:58:48", "released"),
            (13, _HEDGED_EXECUTOR_HANDLE, _HEDGED_LEASE_TOKEN, 3001, _HEDGED_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "active"),
            (14, _SECOND_CANDIDATE_EXECUTOR_HANDLE, _SECOND_CANDIDATE_LEASE_TOKEN, 3001, _SECOND_CANDIDATE_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "active"),
            (15, self.target_executor_handle, _EXTRA_CANDIDATE_1_LEASE_TOKEN, 3001, _TARGET_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "active"),
            (16, self.target_executor_handle, _EXTRA_CANDIDATE_2_LEASE_TOKEN, 3001, _TARGET_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "active"),
            (17, self.target_executor_handle, _EXTRA_CANDIDATE_3_LEASE_TOKEN, 3001, _TARGET_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "active"),
            (18, self.target_executor_handle, _EXTRA_CANDIDATE_4_LEASE_TOKEN, 3001, _TARGET_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "active"),
            (20, self.target_executor_handle, _R61_CANDIDATE_1_LEASE_TOKEN, 3001, _TARGET_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "active"),
            (21, self.target_executor_handle, _R61_CANDIDATE_2_LEASE_TOKEN, 3001, _TARGET_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "active"),
            (22, self.target_executor_handle, _R61_CANDIDATE_3_LEASE_TOKEN, 3001, _TARGET_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "active"),
            (23, self.target_executor_handle, _R61_CANDIDATE_4_LEASE_TOKEN, 3001, _TARGET_WORKER_HANDLE, f"{self.database}.{self.table}", "2026-08-01 23:58:40", "2026-08-01 23:59:00", "active"),
        ]
        if self.entity_decoys:
            # r8: the rotation-watch canary workers hold active same-scope
            # assignments on their own lease chains, widening the set of
            # plausible refresh targets that only the request-identity join
            # can exclude.
            rows = rows + [
                (24, "writer-slot-d", _WATCH4_LEASE_TOKEN, 105, "wh-b4d81c20", f"{self.database}.{self.table}", "2026-08-01 23:58:45", None, "active"),
                (25, "writer-slot-e", _WATCH5_LEASE_TOKEN, 105, "wh-c95e2f37", f"{self.database}.{self.table}", "2026-08-01 23:58:46", None, "active"),
            ]
        values = ",".join(
            "(" + ", ".join(
                (str(row[0]), *(
                    "NULL" if value is None else self._literal(value)
                    for value in row[1:]
                ))
            ) + ")"
            for row in rows
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.worker_registry_relation} "
                "(assignment_id, executor_handle, lease_token, assignment_generation, worker_handle, target_scope, valid_from, valid_to, assignment_state) VALUES "
                + values,
            ),
            f"insert SF06 BR worker registry into {self.worker_registry_relation}",
        )

    def _insert_job_dispatch_noise(self, env) -> None:
        target_scope = f"{self.database}.{self.table}"
        rows = [
            ("dispatch-history-01", "historical-br-01", target_scope, self.storage, "writer-slot-a", 101, "2026-08-01 22:10:00", "2026-08-01 22:25:00", "released", "scheduled", "scheduled-backup"),
            ("dispatch-history-02", "historical-br-02", target_scope, self.storage, "writer-slot-a", 102, "2026-08-01 23:10:00", "2026-08-01 23:29:59", "released", "handoff", "lease-handoff"),
            ("dispatch-history-03", "historical-br-03", target_scope, self.storage, "writer-slot-a", 103, "2026-08-01 23:31:00", "2026-08-01 23:40:00", "released", "scheduled", "scheduled-backup"),
            ("dispatch-history-04", "historical-br-04", f"{target_scope}/rehearsal", self._storage_for("br-permission/rehearsal"), "rehearsal-slot", 104, "2026-08-01 23:45:00", None, "active", "rehearsal", "rehearsal"),
            ("dispatch-history-05", "historical-br-05", target_scope, self.storage, "writer-slot-b", 105, "2026-08-01 23:50:00", None, "active", "sibling", "healthy-sibling"),
            ("sf06-br-001-superseded-dispatch", "sf06-br-001", target_scope, self.storage, "writer-slot-b", 3003, "2026-08-01 23:58:45", "2026-08-01 23:58:46", "released", _TARGET_EXECUTION_PHASE, _TARGET_EXECUTION_REASON),
            ("sf06-br-001-late-handoff-dispatch", "sf06-br-001", target_scope, self.storage, "writer-slot-b", 3004, "2026-08-01 23:58:46", "2026-08-01 23:58:48", "released", _TARGET_EXECUTION_PHASE, _TARGET_EXECUTION_REASON),
        ]
        rows.extend(
            (
                f"dispatch-history-{index:02d}",
                f"historical-br-{index:02d}",
                f"reporting.table_{index:02d}" if index % 2 else target_scope,
                self._storage_for(f"history-{index:02d}"),
                "writer-slot-c" if index % 2 else "writer-slot-a",
                100 + index,
                f"2026-08-01 22:{(index + 10):02d}:00",
                f"2026-08-01 22:{(index + 20):02d}:00",
                "released",
                "history_replay" if index % 2 else "handoff",
                "history-replay" if index % 2 else "lease-handoff",
            )
            for index in range(6, 13)
        )
        rows.extend(
            (
                f"dispatch-post-handoff-{index:02d}",
                f"historical-br-post-handoff-{index:02d}",
                target_scope,
                self.storage,
                "writer-slot-b",
                4000 + index,
                f"2026-08-02 00:{index:02d}:00",
                None,
                "active",
                "post_handoff",
                "post-handoff-scheduled",
            )
            for index in range(1, 33)
        )
        watch_route_rows: list[tuple] = []
        if self.entity_decoys:
            # r8: the rotation-watch canary workers run their own active
            # same-scope dispatches, so the routes table carries additional
            # request-time-valid same-scope chains that only the route ->
            # lease-token -> authority-lease join can exclude.
            rows = rows + [
                (
                    "sf06-br-001-watch4-dispatch",
                    "sf06-br-001",
                    target_scope,
                    self.storage,
                    "writer-slot-d",
                    105,
                    "2026-08-01 23:58:45",
                    None,
                    "active",
                    _TARGET_EXECUTION_PHASE,
                    "rotation-watch",
                ),
                (
                    "sf06-br-001-watch5-dispatch",
                    "sf06-br-001",
                    target_scope,
                    self.storage,
                    "writer-slot-e",
                    105,
                    "2026-08-01 23:58:46",
                    None,
                    "active",
                    _TARGET_EXECUTION_PHASE,
                    "rotation-watch",
                ),
            ]
            watch_route_rows = [
                (
                    _WATCH4_ROUTE_TOKEN,
                    "sf06-br-001-watch4-dispatch",
                    target_scope,
                    self.storage,
                    "writer-slot-d",
                    105,
                    "2026-08-01 23:58:45",
                    None,
                    "active",
                    _TARGET_EXECUTION_PHASE,
                    "rotation-watch",
                ),
                (
                    _WATCH5_ROUTE_TOKEN,
                    "sf06-br-001-watch5-dispatch",
                    target_scope,
                    self.storage,
                    "writer-slot-e",
                    105,
                    "2026-08-01 23:58:46",
                    None,
                    "active",
                    _TARGET_EXECUTION_PHASE,
                    "rotation-watch",
                ),
            ]
        route_rows = rows + [
            (
                _PREFLIGHT_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                self.target_executor_handle,
                3001,
                "2026-08-01 23:58:39",
                "2026-08-01 23:58:41",
                "released",
                _TARGET_EXECUTION_PHASE,
                "read-before-write",
            ),
            (
                "rt-8c13d7e4a0b2",
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                self.target_executor_handle,
                3002,
                "2026-08-01 23:58:41",
                "2026-08-01 23:59:00",
                "active",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
            ),
            (
                _SECOND_CANDIDATE_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                _SECOND_CANDIDATE_EXECUTOR_HANDLE,
                3001,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "released",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
            ),
            (
                _REQUEST_ASSIGNMENT_REPLAY_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                self.target_executor_handle,
                3001,
                "2026-08-01 23:58:48",
                "2026-08-01 23:59:00",
                "released",
                _REPLAY_EXECUTION_PHASE,
                _REPLAY_EXECUTION_REASON,
            ),
            (
                _HEDGED_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                _HEDGED_EXECUTOR_HANDLE,
                3001,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "released",
                _HANDOFF_EXECUTION_PHASE,
                _HANDOFF_EXECUTION_REASON,
            ),
            (
                _EXTRA_CANDIDATE_1_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                self.target_executor_handle,
                3001,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "released",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
            ),
            (
                _EXTRA_CANDIDATE_2_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                self.target_executor_handle,
                3001,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "released",
                _HANDOFF_EXECUTION_PHASE,
                _HANDOFF_EXECUTION_REASON,
            ),
            (
                _EXTRA_CANDIDATE_3_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                self.target_executor_handle,
                3001,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "released",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
            ),
            (
                _EXTRA_CANDIDATE_4_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                self.target_executor_handle,
                3001,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "released",
                _HANDOFF_EXECUTION_PHASE,
                _HANDOFF_EXECUTION_REASON,
            ),
            (
                _R61_CANDIDATE_1_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                self.target_executor_handle,
                3001,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "released",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
            ),
            (
                _R61_CANDIDATE_2_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                self.target_executor_handle,
                3001,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "released",
                _HANDOFF_EXECUTION_PHASE,
                _HANDOFF_EXECUTION_REASON,
            ),
            (
                _R61_CANDIDATE_3_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                self.target_executor_handle,
                3001,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "released",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
            ),
            (
                _R61_CANDIDATE_4_ROUTE_TOKEN,
                "sf06-br-001-dispatch",
                target_scope,
                self.storage,
                self.target_executor_handle,
                3001,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "released",
                _HANDOFF_EXECUTION_PHASE,
                _HANDOFF_EXECUTION_REASON,
            ),
        ] + watch_route_rows

        def route_lease_token(row) -> str:
            if row[0] == _PREFLIGHT_ROUTE_TOKEN:
                return _PREFLIGHT_LEASE_TOKEN
            if row[0] in {_REQUEST_ROUTE_TOKEN, "rt-8c13d7e4a0b2", _REQUEST_ASSIGNMENT_REPLAY_ROUTE_TOKEN}:
                return _TARGET_LEASE_TOKEN
            if row[0] == _HEDGED_ROUTE_TOKEN:
                return _HEDGED_LEASE_TOKEN
            if row[0] == _SECOND_CANDIDATE_ROUTE_TOKEN:
                return _SECOND_CANDIDATE_LEASE_TOKEN
            if row[0] == _EXTRA_CANDIDATE_1_ROUTE_TOKEN:
                return _EXTRA_CANDIDATE_1_LEASE_TOKEN
            if row[0] == _EXTRA_CANDIDATE_2_ROUTE_TOKEN:
                return _EXTRA_CANDIDATE_2_LEASE_TOKEN
            if row[0] == _EXTRA_CANDIDATE_3_ROUTE_TOKEN:
                return _EXTRA_CANDIDATE_3_LEASE_TOKEN
            if row[0] == _EXTRA_CANDIDATE_4_ROUTE_TOKEN:
                return _EXTRA_CANDIDATE_4_LEASE_TOKEN
            if row[0] == _R61_CANDIDATE_1_ROUTE_TOKEN:
                return _R61_CANDIDATE_1_LEASE_TOKEN
            if row[0] == _R61_CANDIDATE_2_ROUTE_TOKEN:
                return _R61_CANDIDATE_2_LEASE_TOKEN
            if row[0] == _R61_CANDIDATE_3_ROUTE_TOKEN:
                return _R61_CANDIDATE_3_LEASE_TOKEN
            if row[0] == _R61_CANDIDATE_4_ROUTE_TOKEN:
                return _R61_CANDIDATE_4_LEASE_TOKEN
            if row[0] == _WATCH4_ROUTE_TOKEN:
                return _WATCH4_LEASE_TOKEN
            if row[0] == _WATCH5_ROUTE_TOKEN:
                return _WATCH5_LEASE_TOKEN
            return {
                "writer-slot-a": _STALE_SIBLING_LEASE_TOKEN,
                "writer-slot-b": _HEALTHY_LEASE_TOKEN,
                "rehearsal-slot": _REHEARSAL_LEASE_TOKEN,
                "writer-slot-c": _REPORTING_LEASE_TOKEN,
                "archive-slot": _ARCHIVE_LEASE_TOKEN,
                "writer-slot-d": _WATCH4_LEASE_TOKEN,
                "writer-slot-e": _WATCH5_LEASE_TOKEN,
            }[row[4]]

        def route_token(row) -> str:
            return row[0] if row[0].startswith("rt-") else f"route-{row[0]}"

        def route_dispatch_id(row) -> str:
            return row[1] if row[0].startswith("rt-") else row[0]

        def assignment_fence(row) -> str:
            if row[0] == _PREFLIGHT_ROUTE_TOKEN:
                return _TARGET_ASSIGNMENT_FENCE
            if row[0] == "rt-8c13d7e4a0b2":
                return _WATCH_REPLAY_ASSIGNMENT_FENCE
            if row[0] == _REQUEST_ASSIGNMENT_REPLAY_ROUTE_TOKEN:
                return _REQUEST_ASSIGNMENT_REPLAY_FENCE
            if row[0] == _HEDGED_ROUTE_TOKEN:
                return _TARGET_ASSIGNMENT_FENCE
            if row[0] == _SECOND_CANDIDATE_ROUTE_TOKEN:
                return _TARGET_ASSIGNMENT_FENCE
            if row[0] in {
                _EXTRA_CANDIDATE_1_ROUTE_TOKEN,
                _EXTRA_CANDIDATE_2_ROUTE_TOKEN,
                _EXTRA_CANDIDATE_3_ROUTE_TOKEN,
                _EXTRA_CANDIDATE_4_ROUTE_TOKEN,
                _R61_CANDIDATE_1_ROUTE_TOKEN,
                _R61_CANDIDATE_2_ROUTE_TOKEN,
                _R61_CANDIDATE_3_ROUTE_TOKEN,
                _R61_CANDIDATE_4_ROUTE_TOKEN,
            }:
                return _TARGET_ASSIGNMENT_FENCE
            if row[0] == _REQUEST_ROUTE_TOKEN:
                return _TARGET_ASSIGNMENT_FENCE
            return f"af-route-{row[0]}"

        def request_context(row) -> str:
            if row[0] == _PREFLIGHT_ROUTE_TOKEN:
                return _TARGET_REQUEST_CONTEXT
            if row[0] == _REQUEST_ROUTE_TOKEN:
                return _TARGET_REQUEST_CONTEXT
            if row[0] == _REQUEST_ASSIGNMENT_REPLAY_ROUTE_TOKEN:
                return _REQUEST_ASSIGNMENT_REPLAY_CONTEXT
            if row[0] == _HEDGED_ROUTE_TOKEN:
                return _TARGET_REQUEST_CONTEXT
            if row[0] == _SECOND_CANDIDATE_ROUTE_TOKEN:
                return _TARGET_REQUEST_CONTEXT
            if row[0] in {
                _EXTRA_CANDIDATE_1_ROUTE_TOKEN,
                _EXTRA_CANDIDATE_2_ROUTE_TOKEN,
                _EXTRA_CANDIDATE_3_ROUTE_TOKEN,
                _EXTRA_CANDIDATE_4_ROUTE_TOKEN,
                _R61_CANDIDATE_1_ROUTE_TOKEN,
                _R61_CANDIDATE_2_ROUTE_TOKEN,
                _R61_CANDIDATE_3_ROUTE_TOKEN,
                _R61_CANDIDATE_4_ROUTE_TOKEN,
            }:
                return _TARGET_REQUEST_CONTEXT
            if row[0] == "rt-8c13d7e4a0b2":
                return _WATCH_REPLAY_REQUEST_CONTEXT
            return f"ctx-route-{row[0]}"

        route_values = ",".join(
            "(" + ", ".join(
                "NULL" if value is None else self._literal(value)
                for value in (
                    route_token(row),
                    route_dispatch_id(row),
                    row[2],
                    row[4],
                    route_lease_token(row),
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                    row[9],
                    row[10],
                    assignment_fence(row),
                    request_context(row),
                )
            ) + ")"
            for row in route_rows
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.dispatch_routes_relation} "
                "(route_token, dispatch_id, target_scope, executor_handle, lease_token, route_generation, valid_from, "
                "valid_to, route_state, assignment_phase, route_reason, request_assignment_fence, request_context_token) VALUES "
                + route_values,
            ),
            f"insert SF06 BR dispatch route noise into {self.dispatch_routes_relation}",
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.job_dispatches_relation} "
                "(dispatch_id, job_id, target_scope, storage_uri, dispatch_generation, "
                "dispatched_at, released_at, dispatch_state, assignment_phase, assignment_reason, request_assignment_fence, request_context_token) VALUES "
                + ",".join(
                    "(" + ", ".join(
                        "NULL" if value is None else self._literal(value)
                        for value in (*row[:4], *row[5:], assignment_fence(row), request_context(row))
                    ) + ")"
                    for row in rows
                ),
            ),
            f"insert SF06 BR job dispatch noise into {self.job_dispatches_relation}",
        )

    def _insert_request_material_cache(self, env) -> None:
        target_scope = f"{self.database}.{self.table}"
        rows = [
            (
                "cache-history-01",
                "route-dispatch-history-01",
                target_scope,
                "wh-history-01",
                "mh-retired-9021",
                "scheduled",
                "2026-08-01 22:10:00",
                "2026-08-01 22:25:00",
                "serving",
                "br-history-20260801-2210",
            ),
            (
                "cache-history-02",
                "route-dispatch-history-02",
                target_scope,
                "wh-history-02",
                _PRODUCTION_MATERIAL_HANDLE,
                "handoff",
                "2026-08-01 23:10:00",
                "2026-08-01 23:29:59",
                "serving",
                "br-history-20260801-2310",
            ),
            (
                "cache-rehearsal-04",
                "route-dispatch-history-04",
                f"{target_scope}/rehearsal",
                "wh-c8e2a630",
                _REHEARSAL_MATERIAL_HANDLE,
                "rehearsal",
                "2026-08-01 23:45:00",
                None,
                "serving",
                "br-rehearsal-20260801-2345",
            ),
            (
                "cache-healthy-05",
                "route-dispatch-history-05",
                target_scope,
                "wh-5a0e7b19",
                _PRODUCTION_MATERIAL_HANDLE,
                "sibling",
                "2026-08-01 23:50:00",
                None,
                "serving",
                "br-healthy-sibling-20260801-2350",
            ),
            (
                _PREFLIGHT_CACHE_TOKEN,
                _PREFLIGHT_ROUTE_TOKEN,
                target_scope,
                _TARGET_WORKER_HANDLE,
                _PRODUCTION_MATERIAL_HANDLE,
                _TARGET_EXECUTION_PHASE,
                "2026-08-01 23:58:39",
                "2026-08-01 23:58:41",
                "serving",
                _TARGET_CHANGE_REF,
            ),
            (
                _REQUEST_CACHE_TOKEN,
                _REQUEST_ROUTE_TOKEN,
                target_scope,
                _TARGET_WORKER_HANDLE,
                _TARGET_MATERIAL_HANDLE,
                _TARGET_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                _TARGET_CHANGE_REF,
            ),
            (
                "c-4e8a1d6f2b90",
                _SHADOW_CACHE_AFFINITY,
                target_scope,
                _SHADOW_WORKER_HANDLE,
                _HEDGED_MATERIAL_HANDLE,
                _TARGET_EXECUTION_PHASE,
                "2026-08-01 23:58:39",
                "2026-08-01 23:59:00",
                "serving",
                "br-rotation-watch-20260801-2358-handoff",
            ),
            (
                _FAILOVER_CACHE_TOKEN,
                "ca-failover-sf06-73dc",
                target_scope,
                _TARGET_WORKER_HANDLE,
                _HEDGED_MATERIAL_HANDLE,
                _TARGET_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                "br-rotation-watch-20260801-2358-failover-replay",
            ),
            (
                _HEDGED_CACHE_TOKEN,
                _HEDGED_ROUTE_TOKEN,
                target_scope,
                _HEDGED_WORKER_HANDLE,
                _HEDGED_MATERIAL_HANDLE,
                _TARGET_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                _HEDGED_CHANGE_REF,
            ),
            (
                _REQUEST_ASSIGNMENT_REPLAY_CACHE_TOKEN,
                _REQUEST_ASSIGNMENT_REPLAY_ROUTE_TOKEN,
                target_scope,
                _TARGET_WORKER_HANDLE,
                _HEDGED_MATERIAL_HANDLE,
                _REPLAY_EXECUTION_PHASE,
                "2026-08-01 23:58:48",
                "2026-08-01 23:59:00",
                "serving",
                _TARGET_CHANGE_REF,
            ),
            (
                _SECOND_CANDIDATE_CACHE_TOKEN,
                _SECOND_CANDIDATE_ROUTE_TOKEN,
                target_scope,
                _SECOND_CANDIDATE_WORKER_HANDLE,
                _SECOND_CANDIDATE_MATERIAL_HANDLE,
                _TARGET_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                _SECOND_CANDIDATE_CHANGE_REF,
            ),
            (
                _EXTRA_CANDIDATE_1_CACHE_TOKEN,
                _EXTRA_CANDIDATE_1_ROUTE_TOKEN,
                target_scope,
                _TARGET_WORKER_HANDLE,
                _EXTRA_CANDIDATE_1_MATERIAL_HANDLE,
                _TARGET_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                _TARGET_CHANGE_REF,
            ),
            (
                _EXTRA_CANDIDATE_2_CACHE_TOKEN,
                _EXTRA_CANDIDATE_2_ROUTE_TOKEN,
                target_scope,
                _TARGET_WORKER_HANDLE,
                _EXTRA_CANDIDATE_2_MATERIAL_HANDLE,
                _HANDOFF_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                _TARGET_CHANGE_REF,
            ),
            (
                _EXTRA_CANDIDATE_3_CACHE_TOKEN,
                _EXTRA_CANDIDATE_3_ROUTE_TOKEN,
                target_scope,
                _TARGET_WORKER_HANDLE,
                _EXTRA_CANDIDATE_3_MATERIAL_HANDLE,
                _TARGET_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                _TARGET_CHANGE_REF,
            ),
            (
                _EXTRA_CANDIDATE_4_CACHE_TOKEN,
                _EXTRA_CANDIDATE_4_ROUTE_TOKEN,
                target_scope,
                _TARGET_WORKER_HANDLE,
                _EXTRA_CANDIDATE_4_MATERIAL_HANDLE,
                _HANDOFF_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                _TARGET_CHANGE_REF,
            ),
            (
                _R61_CANDIDATE_1_CACHE_TOKEN,
                _R61_CANDIDATE_1_ROUTE_TOKEN,
                target_scope,
                _TARGET_WORKER_HANDLE,
                _R61_CANDIDATE_1_MATERIAL_HANDLE,
                _TARGET_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                _TARGET_CHANGE_REF,
            ),
            (
                _R61_CANDIDATE_2_CACHE_TOKEN,
                _R61_CANDIDATE_2_ROUTE_TOKEN,
                target_scope,
                _TARGET_WORKER_HANDLE,
                _R61_CANDIDATE_2_MATERIAL_HANDLE,
                _HANDOFF_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                _TARGET_CHANGE_REF,
            ),
            (
                _R61_CANDIDATE_3_CACHE_TOKEN,
                _R61_CANDIDATE_3_ROUTE_TOKEN,
                target_scope,
                _TARGET_WORKER_HANDLE,
                _R61_CANDIDATE_3_MATERIAL_HANDLE,
                _TARGET_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                _TARGET_CHANGE_REF,
            ),
            (
                _R61_CANDIDATE_4_CACHE_TOKEN,
                _R61_CANDIDATE_4_ROUTE_TOKEN,
                target_scope,
                _TARGET_WORKER_HANDLE,
                _R61_CANDIDATE_4_MATERIAL_HANDLE,
                _HANDOFF_EXECUTION_PHASE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:59:00",
                "serving",
                _TARGET_CHANGE_REF,
            ),
            (
                "c-late-sf06-br-001-handoff",
                "ca-late-4d7e2f81",
                target_scope,
                "wh-5a0e7b19",
                _PRODUCTION_MATERIAL_HANDLE,
                _TARGET_EXECUTION_PHASE,
                "2026-08-01 23:58:46",
                "2026-08-01 23:58:48",
                "serving",
                "br-rotation-watch-20260801-2358-late-handoff",
            ),
            (
                "cache-sf06-br-002",
                "rt-1a6d4c8e2f90",
                target_scope,
                "wh-post-handoff",
                _PRODUCTION_MATERIAL_HANDLE,
                "retry_data_plane",
                "2026-08-01 23:59:40",
                None,
                "standby",
                "br-rotation-watch-20260801-2359-handoff",
            ),
            (
                "cache-post-handoff-01",
                "route-dispatch-post-handoff-01",
                target_scope,
                "wh-post-handoff",
                _PRODUCTION_MATERIAL_HANDLE,
                "post_handoff",
                "2026-08-02 00:01:00",
                None,
                "serving",
                "br-post-handoff-20260802-0001",
            ),
        ]
        def assignment_fence(row) -> str:
            return {
                _PREFLIGHT_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
                _REQUEST_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
                _FAILOVER_CACHE_TOKEN: _WATCH_REPLAY_ASSIGNMENT_FENCE,
                _REQUEST_ASSIGNMENT_REPLAY_CACHE_TOKEN: _REQUEST_ASSIGNMENT_REPLAY_FENCE,
                _SECOND_CANDIDATE_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
                _HEDGED_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
                _EXTRA_CANDIDATE_1_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
                _EXTRA_CANDIDATE_2_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
                _EXTRA_CANDIDATE_3_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
                _EXTRA_CANDIDATE_4_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
                _R61_CANDIDATE_1_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
                _R61_CANDIDATE_2_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
                _R61_CANDIDATE_3_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
                _R61_CANDIDATE_4_CACHE_TOKEN: _TARGET_ASSIGNMENT_FENCE,
            }.get(row[0], f"af-cache-{row[0]}")

        def request_context(row) -> str:
            return {
                _PREFLIGHT_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
                _REQUEST_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
                _REQUEST_ASSIGNMENT_REPLAY_CACHE_TOKEN: _REQUEST_ASSIGNMENT_REPLAY_CONTEXT,
                _FAILOVER_CACHE_TOKEN: _WATCH_REPLAY_REQUEST_CONTEXT,
                _SECOND_CANDIDATE_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
                _HEDGED_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
                _EXTRA_CANDIDATE_1_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
                _EXTRA_CANDIDATE_2_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
                _EXTRA_CANDIDATE_3_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
                _EXTRA_CANDIDATE_4_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
                _R61_CANDIDATE_1_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
                _R61_CANDIDATE_2_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
                _R61_CANDIDATE_3_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
                _R61_CANDIDATE_4_CACHE_TOKEN: _TARGET_REQUEST_CONTEXT,
            }.get(row[0], f"ctx-cache-{row[0]}")

        def cache_phase(row) -> str:
            if row[0] == _REQUEST_ASSIGNMENT_REPLAY_CACHE_TOKEN:
                return _REPLAY_EXECUTION_PHASE
            if row[0] == _HEDGED_CACHE_TOKEN:
                return _HANDOFF_EXECUTION_PHASE
            return str(row[5])

        values = ",".join(
            "(" + ", ".join(
                "NULL" if value is None else self._literal(value)
                for value in (*row[:5], cache_phase(row), *row[6:], assignment_fence(row), request_context(row))
            ) + ")"
            for row in rows
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.request_cache_relation} "
                "(cache_token, route_token, target_scope, worker_handle, material_handle, cache_phase, "
                "valid_from, valid_to, cache_state, change_ref, request_assignment_fence, request_context_token) VALUES " + values,
            ),
            f"insert SF06 BR request material cache into {self.request_cache_relation}",
        )

    def _insert_storage_audit_noise(self, env) -> None:
        rows = []
        for index in range(1, 18):
            same_scope = index % 3 == 0
            event_time = f"2026-08-01 23:{(index + 20) % 60:02d}:00"
            rows.append(
                (
                    f"storage-audit-{index:02d}",
                    f"{self.database}.{self.table}" if same_scope else f"reporting.table_{index:02d}",
                    self._storage_for(
                        "br-permission/rehearsal" if same_scope else f"history-{index:02d}"
                    ),
                    f"dispatch-history-{index:02d}",
                    200 if index % 5 else 403,
                    hashlib.sha256(f"sf06-noise-access-{index}".encode("utf-8")).hexdigest()[:16],
                    "allow" if index % 5 else "deny",
                    "backup_upload" if index % 2 else "bucket_region",
                    event_time,
                    event_time,
                    f"af-storage-{index:02d}",
                    f"ctx-storage-{index:02d}",
                )
            )
        values = ",".join(
            "(" + ", ".join(
                "NULL" if value is None else self._literal(value)
                for value in row
            ) + ")"
            for row in rows
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.storage_audit_relation} "
                "(job_id, target_scope, storage_uri, dispatch_id, http_status, access_key_fingerprint, "
                "policy_decision, request_stage, request_started_at, event_time, request_assignment_fence, request_context_token) VALUES "
                + values,
            ),
            f"insert SF06 BR storage audit noise into {self.storage_audit_relation}",
        )

    def _insert_request_attempts(self, env) -> None:
        target_scope = f"{self.database}.{self.table}"
        rows = (
            (
                _PREFLIGHT_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:39",
                "2026-08-01 23:58:40",
                "backup_upload",
                _TARGET_EXECUTION_PHASE,
                "read-before-write",
                1,
                "get_bucket_region",
                "completed",
                hashlib.sha256(self.correct_access_key.encode()).hexdigest()[:16],
                200,
            ),
            (
                _RETRY_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:48",
                "2026-08-01 23:58:49",
                "backup_upload",
                _REPLAY_EXECUTION_PHASE,
                _REPLAY_EXECUTION_REASON,
                5,
                "put_backup_chunk_followup",
                "aborted",
                hashlib.sha256(self.fault_access_key.encode()).hexdigest()[:16],
                0,
            ),
            (
                _HEDGED_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:58:47",
                "backup_upload",
                _HANDOFF_EXECUTION_PHASE,
                _HANDOFF_EXECUTION_REASON,
                2,
                "put_backup_chunk",
                "failed",
                hashlib.sha256(self.fault_access_key.encode()).hexdigest()[:16],
                403,
            ),
            (
                _SECOND_CANDIDATE_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:58:47",
                "backup_upload",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
                3,
                "put_backup_chunk",
                "failed",
                hashlib.sha256(self.fault_access_key.encode()).hexdigest()[:16],
                403,
            ),
            (
                _FAILED_REQUEST_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:58:47",
                "backup_upload",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
                4,
                "put_backup_chunk",
                "failed",
                hashlib.sha256(self.fault_access_key.encode()).hexdigest()[:16],
                403,
            ),
            (
                _EXTRA_CANDIDATE_1_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:58:47",
                "backup_upload",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
                6,
                "put_backup_chunk",
                "failed",
                hashlib.sha256(self.fault_access_key.encode("utf-8")).hexdigest()[:16],
                403,
            ),
            (
                _EXTRA_CANDIDATE_2_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:58:47",
                "backup_upload",
                _HANDOFF_EXECUTION_PHASE,
                _HANDOFF_EXECUTION_REASON,
                7,
                "put_backup_chunk",
                "failed",
                hashlib.sha256(self.fault_access_key.encode("utf-8")).hexdigest()[:16],
                403,
            ),
            (
                _EXTRA_CANDIDATE_3_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:58:47",
                "backup_upload",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
                8,
                "put_backup_chunk",
                "failed",
                hashlib.sha256(self.fault_access_key.encode("utf-8")).hexdigest()[:16],
                403,
            ),
            (
                _EXTRA_CANDIDATE_4_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:58:47",
                "backup_upload",
                _HANDOFF_EXECUTION_PHASE,
                _HANDOFF_EXECUTION_REASON,
                9,
                "put_backup_chunk",
                "failed",
                hashlib.sha256(self.fault_access_key.encode("utf-8")).hexdigest()[:16],
                403,
            ),
            (
                _R61_CANDIDATE_1_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:58:47",
                "backup_upload",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
                10,
                "put_backup_chunk",
                "failed",
                hashlib.sha256(self.fault_access_key.encode("utf-8")).hexdigest()[:16],
                403,
            ),
            (
                _R61_CANDIDATE_2_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:58:47",
                "backup_upload",
                _HANDOFF_EXECUTION_PHASE,
                _HANDOFF_EXECUTION_REASON,
                11,
                "put_backup_chunk",
                "failed",
                hashlib.sha256(self.fault_access_key.encode("utf-8")).hexdigest()[:16],
                403,
            ),
            (
                _R61_CANDIDATE_3_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:58:47",
                "backup_upload",
                _TARGET_EXECUTION_PHASE,
                _TARGET_EXECUTION_REASON,
                12,
                "put_backup_chunk",
                "failed",
                hashlib.sha256(self.fault_access_key.encode("utf-8")).hexdigest()[:16],
                403,
            ),
            (
                _R61_CANDIDATE_4_ATTEMPT_ID,
                "sf06-br-001-dispatch",
                target_scope,
                _TARGET_REQUEST_CONTEXT,
                _TARGET_ASSIGNMENT_FENCE,
                "2026-08-01 23:58:40",
                "2026-08-01 23:58:47",
                "backup_upload",
                _HANDOFF_EXECUTION_PHASE,
                _HANDOFF_EXECUTION_REASON,
                13,
                "put_backup_chunk",
                "failed",
                hashlib.sha256(self.fault_access_key.encode("utf-8")).hexdigest()[:16],
                403,
            ),
        )
        values = ",".join(
            "(" + ", ".join(
                "NULL" if value is None else self._literal(value)
                for value in row
            ) + ")"
            for row in rows
        )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.request_attempts_relation} "
                "(attempt_id, dispatch_id, target_scope, request_context_token, request_assignment_fence, "
                "request_started_at, event_time, request_stage, execution_phase, execution_reason, attempt_sequence, "
                "operation_name, attempt_state, access_key_fingerprint, http_status) VALUES " + values,
            ),
            f"insert SF06 BR request attempts into {self.request_attempts_relation}",
        )

    def _insert_history_noise(self, env) -> None:
        rows = []
        for index in range(1, 61):
            status = "error" if index % 5 == 0 or index % 11 == 0 else "success"
            error_text = (
                "Forbidden: rotated credential policy denied the object-storage request"
                if index % 11 == 0
                else "timeout while waiting for a remote worker" if index % 5 == 0 else ""
            )
            ranges_succeed = "0" if index % 11 == 0 else "3" if index % 5 == 0 else "4"
            ranges_failed = "4" if index % 11 == 0 else "1" if index % 5 == 0 else "0"
            checksum_percent = "0.00" if index % 11 == 0 else "75.00" if index % 5 == 0 else "100.00"
            rows.append(
                "(" + ", ".join((
                    self._literal(f"historical-br-{index:02d}"),
                    self._literal(self._storage_for(f"history-{index:02d}")),
                    self._literal("benchops" if index % 3 else "reporting"),
                    self._literal(self.table if index % 4 else "settlement_events"),
                    self._literal(status),
                    self._literal(error_text),
                    "4",
                    ranges_succeed,
                    ranges_failed,
                    checksum_percent,
                    self._literal("scheduled-history"),
                )) + ")"
            )
        require_sql_success(
            self._fixture_sql(
                env,
                f"INSERT INTO {self.history_relation} "
                "(job_id, storage_uri, database_name, table_name, status, error_text, "
                "ranges_total, ranges_succeed, ranges_failed, checksum_percent, actor) VALUES "
                + ",".join(rows)
            ),
            f"insert SF06 BR history noise into {self.history_relation}",
        )

    def _verify_fixture(self, env) -> None:
        payload = json_object(
            self._fixture_sql(env, f"SELECT COUNT(*) FROM {self.database}.{self.table}"),
            f"verify SF06 BR source row count for {self.database}.{self.table}",
        )
        observed = int(payload["result"][0][0])
        if observed != self.row_count:
            raise RuntimeError(
                "SF06 BR source row count mismatch: "
                f"database={self.database!r}, table={self.table!r}, "
                f"expected={self.row_count}, observed={observed}"
            )
        if self.entity_decoys:
            # r4 focused profile: trimmed background inventory, grants with the
            # shadow-rotation grant 21, sentinel-desired leases with the pruned
            # shadow family, and the causal lease at id 46.
            # r7/r8: wave-2 open-window production grants (21/22/23), the
            # settlement-scope grant 24, rolled-back wave-2 bindings plus the
            # candidate's false start, and the rotation-watch worker chains.
            expected_counts = (
                (self.credentials_relation, 99),
                (self.credential_grants_relation, 23),
                (self.authority_leases_relation, 31),
                (self.bindings_relation, 97),
                (self.worker_registry_relation, 25),
                (self.worker_materials_relation, 11),
                (self.job_dispatches_relation, 48),
                (self.dispatch_routes_relation, 63),
                (self.request_cache_relation, 22),
                (self.request_attempts_relation, 13),
                (self.worker_leases_relation, 25),
                (self.storage_audit_relation, 17),
                (self.history_relation, 60),
            )
        else:
            expected_counts = (
                (self.credentials_relation, 248),
                (self.credential_grants_relation, 8),
                (self.authority_leases_relation, 24),
                (self.bindings_relation, 244),
                (self.worker_registry_relation, 23),
                (self.worker_materials_relation, 8),
                (self.job_dispatches_relation, 46),
                (self.dispatch_routes_relation, 59),
                (self.request_cache_relation, 22),
                (self.request_attempts_relation, 13),
                (self.worker_leases_relation, 22),
                (self.storage_audit_relation, 17),
                (self.history_relation, 60),
            )
        for table, expected in expected_counts:
            payload = json_object(
                self._fixture_sql(env, f"SELECT COUNT(*) FROM {table}"),
                f"verify SF06 BR fixture row count for {table}",
            )
            observed = int(payload["result"][0][0])
            if observed != expected:
                raise RuntimeError(
                    "SF06 BR fixture row count mismatch: "
                    f"table={table!r}, expected={expected}, observed={observed}"
                )

    def _start_minio(self) -> None:
        self._minio_container = self.minio_container
        completed = subprocess.run(
            [
                "docker", "run", "--detach", "--name", self.minio_container,
                "--network", self.network_name,
                "-e", f"MINIO_ROOT_USER={self.correct_access_key}",
                "-e", f"MINIO_ROOT_PASSWORD={self.correct_secret_key}",
                self.minio_image, "server", "/data", "--address", ":9000",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "SF06 MinIO install failed: "
                f"container={self.minio_container!r}, network={self.network_name!r}, "
                f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
            )
        self._minio_running = True
        last = None
        for _ in range(30):
            last = self._mc(("ls",))
            if last.returncode == 0:
                bucket = self._mc(("mb", f"admission/{self.bucket}"))
                if bucket.returncode != 0:
                    raise RuntimeError(
                        "SF06 MinIO bucket creation failed: "
                        f"container={self.minio_container!r}, bucket={self.bucket!r}, "
                        f"stdout={bucket.stdout.strip()!r}, stderr={bucket.stderr.strip()!r}"
                    )
                return
            time.sleep(1)
        raise RuntimeError(
            "SF06 MinIO did not become ready: "
            f"container={self.minio_container!r}, stdout={last.stdout.strip()!r}, "
            f"stderr={last.stderr.strip()!r}"
        )

    def _ensure_minio_running(self) -> None:
        completed = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Running}}", self.minio_container],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "SF06 MinIO activation cannot find the persistent container: "
                f"container={self.minio_container!r}, stderr={completed.stderr.strip()!r}"
            )
        if completed.stdout.strip() != "true":
            started = subprocess.run(
                ["docker", "start", self.minio_container],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if started.returncode != 0:
                raise RuntimeError(
                    "SF06 MinIO activation failed to start the container: "
                    f"container={self.minio_container!r}, stderr={started.stderr.strip()!r}"
                )
        self._minio_container = self.minio_container
        self._minio_running = True
        ready = self._mc(("ls",))
        if ready.returncode != 0:
            raise RuntimeError(
                "SF06 MinIO activation found a running container but the API is not ready: "
                f"container={self.minio_container!r}, stderr={ready.stderr.strip()!r}"
            )

    def _mc(self, args: tuple[str, ...]):
        script = (
            "mc alias set admission http://"
            f"{self.minio_container}:9000 {self.correct_access_key} {self.correct_secret_key} >/dev/null && "
            f"mc {shlex.join(args)}"
        )
        return subprocess.run(
            [
                "docker", "run", "--rm", "--network", self.network_name,
                "--entrypoint", "/bin/sh", self.mc_image, "-c", script,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )


class TidbSystemFailureBrPermissionScenario(TiDBScenario):
    scenario_id = "tidb_system_failure_br_permission"
    description = "Diagnoses a failed table-backup path and produces a verified backup."
    cases = (_SF06_CASE, _FOCUSED_SF06_CASE)

    def build_fault_plan(self, case: TidbSystemFailureBrPermissionCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureBrPermissionInjector,
                config={
                    "database": case.database,
                    "table": case.table,
                    "credentials_table": case.credentials_table,
                    "credential_grants_table": case.credential_grants_table,
                    "authority_leases_table": case.authority_leases_table,
                    "history_table": case.history_table,
                    "bindings_table": case.bindings_table,
                    "worker_leases_table": case.worker_leases_table,
                    "storage_audit_table": case.storage_audit_table,
                    "worker_registry_table": case.worker_registry_table,
                    "worker_materials_table": case.worker_materials_table,
                    "job_dispatches_table": case.job_dispatches_table,
                    "dispatch_routes_table": case.dispatch_routes_table,
                    "request_cache_table": case.request_cache_table,
                    "request_attempts_table": case.request_attempts_table,
                    "quarantine_tickets_table": case.quarantine_tickets_table,
                    "target_executor_handle": "writer-slot-a",
                    "row_count": case.row_count,
                    "expected_ranges": case.expected_ranges,
                    "effective_binding_id": case.effective_binding_id,
                    "candidate_binding_id": case.candidate_binding_id,
                    "fault_credential_id": case.fault_credential_id,
                    "correct_credential_id": case.correct_credential_id,
                    "entity_decoys": case.entity_decoys,
                    "derive_desired_from_grants": case.derive_desired_from_grants,
                    "uniform_refresh_rejection": case.uniform_refresh_rejection,
                    "epoch_from_observation": case.epoch_from_observation,
                    "storage_prefix_quarantine": case.storage_prefix_quarantine,
                    "live_authority_epoch": case.live_authority_epoch,
                    "prefix_quarantine_ref": case.prefix_quarantine_ref,
                    "target_authority_lease_id": case.target_authority_lease_id,
                    "target_authority_epoch": case.target_authority_epoch,
                    "minio_image": "docker.m.daocloud.io/minio/minio:RELEASE.2024-06-13T22-53-53Z",
                    "mc_image": "docker.m.daocloud.io/minio/mc:latest",
                    "br_image": "docker.m.daocloud.io/pingcap/br:v8.1.0",
                    "minio_container_prefix": "aiopsbench-sf06-br-minio",
                    "bucket": "admission",
                    "object_prefix": "br-permission",
                    "correct_access_key": "admission",
                    "correct_secret_key": "admission-secret",
                    "target_worker": case.target_worker,
                    "healthy_worker": case.healthy_worker,
                    "desired_revision": case.desired_revision,
                    "observed_revision": case.observed_revision,
                    "fault_access_key": "sf06-key-8f2a1c",
                    "fault_secret_key": "sf06-secret-4b7e",
                    "timeout_seconds": 180,
                },
            ),
        )
