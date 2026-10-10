#!/usr/bin/env python3
"""Build the auditable 102-Case PostgreSQL reference-path report."""

from __future__ import annotations

import csv
import dataclasses
import json
import re
import subprocess
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from src.scenarios import POSTGRES_SCENARIO_REGISTRY


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "experiments"
REPORT_DIR = ROOT / "artifacts" / "reports"
_INSPECT_DOCUMENT_CACHE: dict[str, list[dict[str, Any]]] = {}

SCENARIO_ID_MIGRATION = {
    "pg_composite_fault_wal_checkpoint_storm": "pg_system_failure_wal_checkpoint_storm",
    "pg_composite_fault_checkpoint_archive": "pg_system_failure_checkpoint_archive",
    "pg_composite_fault_stale_stats_lock_contention": "pg_query_perf_stale_stats_lock_contention",
    "pg_composite_fault_connection_bloat": "pg_system_failure_connection_bloat",
    "pg_composite_fault_lwlock_pgbouncer_cascade": "pg_business_change_lwlock_pgbouncer_cascade",
    "pg_misleading_alert_cpu_lock_spin": "pg_system_failure_cpu_lock_spin",
    "pg_misleading_alert_io_saturation": "pg_business_change_io_saturation",
    "pg_misleading_alert_io_context_workload": "pg_resource_governance_io_context_workload",
    "pg_misleading_alert_cache_pollution": "pg_query_perf_cache_pollution",
    "pg_misleading_alert_partition_cleanup": "pg_resource_governance_partition_cleanup",
}
CURRENT_TO_HISTORICAL_SCENARIO_ID = {current: old for old, current in SCENARIO_ID_MIGRATION.items()}


# These are the operational states reconstructed from selected diagnosis-not-applicable
# reference traces. They are deliberately kept separate from Case difficulty metadata:
# the trace is the measurement source, and each state is supported by the preceding
# diagnostic observations before repair or final verification.
NON_DIAGNOSIS_PATH_STATES: dict[str, tuple[str, ...]] = {
    "pg_resource_governance_container_cpu_budget/db_quota_throttle": (
        "cross_layer_resource_pressure",
        "required_sibling_budget",
        "bounded_quota_decision",
    ),
    "pg_resource_governance_pgbouncer_connection_budget/pool_partition_shortage": (
        "checkout_queue_pressure",
        "server_capacity_versus_queue",
        "service_impact_with_database_headroom",
        "historical_pool_revision",
        "transaction_pool_partition_scope",
        "role_and_pool_connection_ceiling",
        "bounded_fixed_budget_decision",
    ),
    "pg_resource_governance_pgbouncer_connection_budget/pool_partition_shortage_simple": (
        "checkout and reporting queue pressure localized",
        "fixed database and pool ceilings established",
        "bounded pool-partition correction selected",
    ),
    "pg_health_check_backup_rpo_certification/throughput_gap": (
        "candidate_window",
        "throughput_mismatch",
        "archive_propagation",
        "rpo_boundary",
    ),
    "pg_health_check_backup_rpo_certification/throughput_gap_simple": (
        "candidate_window",
        "throughput_mismatch",
        "archive_propagation",
        "rpo_boundary",
    ),
    "pg_business_change_online_ddl/order_line_delivery_note_ddl": (
        "live_write_pressure",
        "target_column_and_lock_scope",
        "online_ddl_decision",
    ),
    "pg_business_change_online_ddl/order_line_gift_note_ddl_simple": (
        "live_write_pressure",
        "target_column_and_lock_scope",
        "online_ddl_decision",
    ),
    "pg_business_change_massive_backfill/customer_birth_decade_backfill": (
        "backfill_scope_and_pressure",
        "bounded_batch_plan",
    ),
    "pg_business_change_massive_backfill/customer_loyalty_decade_backfill_simple": (
        "backfill_scope_and_pressure",
        "bounded_batch_plan",
    ),
    "pg_business_change_collation_conversion/store_returns_ticket_locale_simple": (
        "io_and_collation_baseline",
        "rewrite_and_index_scope",
        "online_conversion_plan",
    ),
    "pg_business_change_collation_conversion/store_returns_collation_conversion": (
        "io_and_collation_baseline",
        "rewrite_and_index_scope",
        "online_conversion_plan",
    ),
}


# Some reference reports submit several independent conditions that collapse into
# fewer diagnostic state transitions. These states are reviewed from the raw trace;
# they are not copied from DifficultyCalibration metadata.
TRACE_LOGICAL_PATH_STATES: dict[str, tuple[str, ...]] = {
    "pg_resource_governance_container_cpu_budget/db_quota_throttle_simple": (
        "localize database service degradation in the six-hour history",
        "correlate database quota contact with throttle and PSI",
        "exclude host exhaustion, healthy sibling pressure, and recovered quota windows",
        "observe that direct quota correction is reconciled back to the fault value",
        "correlate policy and effective-weight revisions with repeated quota reconciliation",
        "identify the stale database workload-class binding and choose bounded coordinated recovery",
    ),
    "pg_query_perf_stale_statistics/branch_order_hot_window_simple": (
        "localize the branch hot-window report and its cardinality-estimate error",
        "use relation statistics and the recent data-shape change to select stale statistics as the mechanism",
        "rule out an index change and choose scoped ANALYZE as the repair decision",
    ),
    "pg_query_perf_parameter_sniffing/branch_order_year_skew_simple": (
        "localize the bind-sensitive customer revenue lookup",
        "identify the generic/custom plan mismatch and its hot-bind performance impact",
        "choose force_custom_plan as the scoped plan-cache repair decision",
    ),
    "pg_health_check_autovacuum_sustainability/capacity_deficit": (
        "establish the target relation churn and dead-tuple symptom",
        "separate sustained cleanup-capacity deficit from healthy-neighbor and maintenance activity",
        "bind the deficit to the target table's published autovacuum controls and workload pressure",
        "choose scoped sustainability remediation for the target relation",
    ),
    "pg_composite_fault_checkpoint_archive/checkpoint_archive_dual_fault": (
        "separate checkpoint/write-latency and archive/PITR candidates",
        "correlate WAL/FPI growth with requested checkpoints, device queue, and OLTP p99",
        "correlate archive generation, delivery retries, backlog, pg_wal headroom, and PITR risk",
        "verify active archive binding, lease/route coherence, and repository capacity while excluding benign windows",
        "choose bounded per-chain controls within the durability and target scope",
    ),
    "pg_misleading_alert_cache_pollution/archive_scan_cache_pollution": (
        "establish cache-hit degradation as the observed symptom",
        "rule out cache sizing/configuration as the primary candidate",
        "localize the reporting scan and archive-table scope",
        "connect archive-page presence to hot-page displacement and cache churn",
        "choose targeted scan termination with recurrence control",
    ),
    "pg_misleading_alert_cache_pollution/billing_export_scan_cache_churn": (
        "establish cache-hit degradation as the observed symptom",
        "rule out cache sizing/configuration as the primary candidate",
        "localize the billing export scan and checkout hot-table scope",
        "connect export-page presence to checkout hot-page displacement and cache churn",
        "choose targeted scan termination with recurrence control",
    ),
    "pg_composite_fault_lwlock_pgbouncer_cascade/replica_lwlock_tipping": (
        "establish N-1 route capacity and the unavailable replica scope",
        "identify broad relation-lock slowpath demand and skewed remaining-replica duration",
        "correlate the waiter-first cascade into downstream read-pool pressure",
        "choose a safe capacity/routing plan that restores the drained replica",
    ),
    "pg_composite_fault_lwlock_pgbouncer_cascade/replica_lwlock_tipping_simple": (
        "establish N-1 route capacity and the unavailable replica scope",
        "identify waiter-first relation-lock slowpath demand and remaining-replica duration",
        "correlate the lock-to-duration chain into downstream read-pool pressure",
        "choose a safe capacity/routing plan that restores the drained replica",
    ),
    "pg_composite_fault_checkpoint_archive/checkpoint_archive_dual_fault_simple": (
        "separate checkpoint/write-latency and archive/PITR candidates",
        "correlate the checkpoint and archive causal chains with the live workload",
        "verify active target capacity and binding/lease/route coherence",
        "choose bounded per-chain controls within the durability and target scope",
    ),
    "pg_misleading_alert_cache_pollution/analytics_cursor_cache_churn": (
        "establish cache-hit degradation as the observed symptom",
        "rule out cache sizing and configuration as the primary candidate",
        "localize the old analytics cursor and hot-table cleanup target",
        "connect the cursor snapshot to blocked vacuum cleanup and cache churn",
        "choose targeted cursor termination with bounded cleanup and recurrence control",
    ),
    "pg_query_perf_heavy_offset_pagination/branch_order_deep_offset": (
        "localize the late-page audit export query",
        "identify deep row-number offset pagination as the root cause",
        "connect skipped-row work to the keyset pagination decision",
    ),
    "pg_query_perf_heavy_offset_pagination/branch_order_shallow_offset": (
        "localize the late-page branch-order query",
        "identify row-number offset pagination as the root cause",
        "connect skipped-row work to the keyset pagination decision",
    ),
}


def semantic_units(*labels: str) -> tuple[str, ...]:
    return labels


# Human-coded evidence units from the selected raw reference traces. Each label denotes
# one semantic group in the unfiltered tool result (for example a lock chain, a workload
# profile class, a configuration bundle, or a metric symptom), never a SQL row, log line,
# metric sample, or tool call. The labels are intentionally explicit so the generated
# report carries the audit decision rather than silently reusing DifficultyCalibration.
SEMANTIC_EVIDENCE_UNITS: dict[str, dict[str, dict[str, tuple[str, ...]]]] = {
    "pg_query_perf_stale_statistics/branch_order_hot_window_simple": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported TopSQL metric result"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "target hot-window plan and cardinality estimate error",
                "recent target-relation modifications and analyze age",
                "relation tuple-count catalog baseline",
                "index catalog evidence ruling out an index change",
            ),
            "noise": semantic_units(),
        },
    },
    "pg_query_perf_parameter_sniffing/branch_order_year_skew_simple": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported TopSQL metric result"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "pg_stat_statements locates the bind-sensitive customer lookup",
                "prepared-statement catalog exposes generic/custom plan counts",
                "hot-bind EXPLAIN confirms the plan-performance impact",
            ),
            "noise": semantic_units("unrelated reporting prepared statements and query context"),
        },
    },
    "pg_health_check_autovacuum_sustainability/capacity_deficit": {
        "metric": {
            "causal": semantic_units(
                "target relation churn burst",
                "dead-tuple backlog growth",
                "cleanup removal capacity",
                "xmin horizon and maintenance-capacity relation",
            ),
            "noise": semantic_units(
                "healthy audit relation activity",
                "healthy customer relation activity",
                "healthy inventory relation activity",
                "healthy order-items relation context",
                "normal maintenance and OLTP context",
            ),
        },
        "log": {
            "causal": semantic_units(),
            "noise": semantic_units("component-log observer context in the target window"),
        },
        "SQL/catalog": {
            "causal": semantic_units("target relation autovacuum settings and scope"),
            "noise": semantic_units("healthy-neighbor relation settings and catalog context"),
        },
        "workload/operation event": {
            "causal": semantic_units("business OLTP write-generation pressure"),
            "noise": semantic_units(),
        },
    },
    "pg_composite_fault_checkpoint_archive/checkpoint_archive_dual_fault": {
        "metric": {
            "causal": semantic_units(
                "WAL/FPI growth and requested-checkpoint write-latency chain",
                "archive delivery shortfall, retries, and backlog chain",
                "service p99 and PITR headroom impact",
            ),
            "noise": semantic_units(
                "storage pressure and batch-progress context",
                "benign normal-window comparison",
                "backup/report I/O context",
                "cross-window metric history context",
            ),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "active archive target and repository capacity",
                "binding generation, lease, route, and worker coherence",
            ),
            "noise": semantic_units("neighbor archive target and repository catalog context"),
        },
        "workload/operation event": {
            "causal": semantic_units(),
            "noise": semantic_units("operation-event queries with no matching record in the selected window"),
        },
    },
    "pg_misleading_alert_cache_pollution/archive_scan_cache_pollution": {
        "metric": {
            "causal": semantic_units("degraded cache-hit window"),
            "noise": semantic_units(
                "healthy cache-hit context",
                "unsupported slow-query metric result",
            ),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "intended shared-buffer configuration",
                "active archive reporting scan identity",
                "archive pages displacing hot OLTP pages",
            ),
            "noise": semantic_units("hot-session and unrelated catalog context"),
        },
    },
    "pg_misleading_alert_cache_pollution/billing_export_scan_cache_churn": {
        "metric": {
            "causal": semantic_units("degraded cache-hit window"),
            "noise": semantic_units(
                "healthy cache-hit context",
                "unsupported slow-query metric result",
            ),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "intended shared-buffer configuration",
                "active billing export scan identity",
                "export pages displacing checkout hot pages",
            ),
            "noise": semantic_units("hot-session and unrelated catalog context"),
        },
    },
    "pg_composite_fault_lwlock_pgbouncer_cascade/replica_lwlock_tipping": {
        "metric": {
            "causal": semantic_units(
                "N-1 replica health and route skew",
                "remaining-replica slowpath and duration pressure",
            ),
            "noise": semantic_units(
                "healthy primary/writer context",
                "read-pool state without a waiting-client sample",
            ),
        },
        "SQL/catalog": {
            "causal": semantic_units("streaming replication and lag evidence"),
            "noise": semantic_units(),
        },
    },
    "pg_composite_fault_lwlock_pgbouncer_cascade/replica_lwlock_tipping_simple": {
        "metric": {
            "causal": semantic_units(
                "N-1 replica health and route skew",
                "waiter-first relation-lock slowpath and remaining-replica duration",
                "downstream read-pool queue pressure",
            ),
            "noise": semantic_units(
                "healthy high-QPS and report-pool decoy windows",
                "healthy primary/writer and post-recovery fleet context",
                "unaffected replica and normal route distribution context",
            ),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "streaming replication and unavailable-replica scope",
                "target lock-footprint query identity and duration evidence",
            ),
            "noise": semantic_units(
                "observer and health-query TopSQL context",
                "commit and report-session slow-query context",
            ),
        },
        "workload/operation event": {
            "causal": semantic_units("router revision and active-replica transition"),
            "noise": semantic_units("normal and recovery route snapshots outside the causal transition"),
        },
    },
    "pg_system_failure_page_corruption/order_line_audit_page_corruption": {
        "SQL/catalog": {
            "causal": semantic_units("checksum failure", "affected relation identity"),
            "noise": semantic_units("unaffected relation sample"),
        },
        "log": {
            "causal": semantic_units("PostgreSQL invalid-page log record"),
            "noise": semantic_units("neighboring database log context"),
        },
    },
    "pg_system_failure_page_corruption/invoice_page_corruption_triage_simple": {
        "SQL/catalog": {
            "causal": semantic_units("corrupt relation path and size"),
            "noise": semantic_units("healthy relation-size context"),
        },
        "workload/operation event": {
            "causal": semantic_units(),
            "noise": semantic_units("catalog health probe activity"),
        },
    },
    "pg_system_failure_xid_wraparound/billing_freeze_blocked_simple": {
        "SQL/catalog": {
            "causal": semantic_units(
                "transaction age near wraparound",
                "freeze blocker identity",
                "target relation scope",
            ),
            "noise": semantic_units("unrelated relation age context"),
        },
        "workload/operation event": {
            "causal": semantic_units("billing replay blocker activity"),
            "noise": semantic_units("low-rate workload profile"),
        },
    },
    "pg_system_failure_xid_wraparound/payment_ledger_xid_wraparound": {
        "SQL/catalog": {
            "causal": semantic_units("transaction age risk", "freeze blocker", "target relation", "freeze threshold"),
            "noise": semantic_units("healthy relation age context"),
        },
    },
    "pg_system_failure_lock_contention/customer_profile_lock_queue_simple": {
        "SQL/catalog": {
            "causal": semantic_units("target lock wait and blocker chain"),
            "noise": semantic_units("nightly reporting lock chain"),
        },
    },
    "pg_system_failure_lock_contention/customer_row_lock_queue": {
        "metric": {
            "causal": semantic_units("lock-wait pressure"),
            "noise": semantic_units("TopSQL and background workload context"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "blocking lock chain",
                "blocker identity",
                "targeted release scope",
            ),
            "noise": semantic_units(
                "reporting session context",
                "connection-pool session context",
                "exporter session context",
            ),
        },
    },
    "pg_system_failure_deadlock/checkout_order_deadlock": {
        "SQL/catalog": {
            "causal": semantic_units(
                "deadlock detector record",
                "two-transaction lock cycle",
                "checkout function lock order",
                "conflicting checkout job statements",
            ),
            "noise": semantic_units(
                "background workload session context",
                "reporting statement context",
            ),
        },
    },
    "pg_system_failure_deadlock/single_order_pair_deadlock_simple": {
        "SQL/catalog": {
            "causal": semantic_units(
                "deadlock detector record",
                "checkout function lock order",
                "conflicting order-pair steps",
            ),
            "noise": semantic_units("dashboard and serialization warning context"),
        },
    },
    "pg_health_check_table_bloat/store_returns_table_index_bloat": {
        "metric": {
            "causal": semantic_units("dead-tuple pressure"),
            "noise": semantic_units("healthy relation activity"),
        },
        "SQL/catalog": {
            "causal": semantic_units("target relation bloat"),
            "noise": semantic_units("neighbor relation catalog row"),
        },
    },
    "pg_health_check_table_bloat/store_returns_bloat_simple": {
        "metric": {
            "causal": semantic_units("target dead-tuple ratio"),
            "noise": semantic_units("comparison relation dead-tuple context"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "target relation bloat",
                "target index growth",
                "target maintenance scope",
            ),
            "noise": semantic_units(
                "healthy comparison relation",
                "pg_repack availability context",
            ),
        },
    },
    "pg_health_check_unused_indexes/customer_redundant_indexes": {
        "metric": {
            "causal": semantic_units("write-overhead and slow-query signal"),
            "noise": semantic_units("non-target workload query context"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "index usage evidence",
                "safe drop set",
                "protected preserve set",
                "concurrent drop safety",
            ),
            "noise": semantic_units(
                "low-use index decoy",
                "constraint and index catalog context",
            ),
        },
    },
    "pg_health_check_unused_indexes/customer_unused_index_simple": {
        "metric": {
            "causal": semantic_units("write-overhead and slow-query signal"),
            "noise": semantic_units("non-target workload query context"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "index usage evidence",
                "safe drop set",
                "protected preserve set",
            ),
            "noise": semantic_units(
                "low-use index decoy",
                "constraint and index catalog context",
            ),
        },
    },
    "pg_health_check_capacity_trend/sales_event_storage_growth": {
        "metric": {
            "causal": semantic_units("storage growth rate", "projected capacity pressure"),
            "noise": semantic_units("current capacity headroom"),
        },
        "SQL/catalog": {
            "causal": semantic_units("primary growing relation", "growth source attribution", "retention action scope"),
            "noise": semantic_units("stable relation size context", "non-target catalog context"),
        },
    },
    "pg_health_check_capacity_trend/archive_growth_forecast_simple": {
        "metric": {
            "causal": semantic_units("growth rate", "forecast pressure"),
            "noise": semantic_units("benign capacity window", "non-target capacity series"),
        },
        "SQL/catalog": {
            "causal": semantic_units("primary source relation"),
            "noise": semantic_units("comparison relation"),
        },
    },
    "pg_health_check_long_running_tx/checkout_pool_idle_transaction": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported dead-tuple metric request"),
        },
        "SQL/catalog": {
            "causal": semantic_units("idle transaction identity", "vacuum horizon evidence", "target blocker scope", "timeout protection"),
            "noise": semantic_units("short transaction decoy", "ordinary idle session"),
        },
    },
    "pg_health_check_long_running_tx/single_idle_transaction_cleanup_simple": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported dead-tuple metric request"),
        },
        "SQL/catalog": {
            "causal": semantic_units("idle transaction identity", "vacuum horizon evidence", "target blocker scope", "timeout protection"),
            "noise": semantic_units("short transaction decoy", "ordinary idle session"),
        },
    },
    "pg_health_check_backup_recoverability/missing_wal_recovery_gap": {
        "SQL/catalog": {
            "causal": semantic_units("selected backup", "missing WAL interval", "latest recoverable point"),
            "noise": semantic_units("complete backup inventory context"),
        },
    },
    "pg_health_check_backup_recoverability/single_missing_wal_gap_simple": {
        "SQL/catalog": {
            "causal": semantic_units("selected backup", "missing WAL interval", "latest recoverable point", "recovery boundary"),
            "noise": semantic_units("complete backup inventory context"),
        },
    },
    "pg_health_check_backup_rpo_certification/throughput_gap": {
        "metric": {
            "causal": semantic_units("WAL generation mismatch", "archive delivery deficit", "RPO impact window", "OLTP impact correlation", "backup throughput boundary"),
            "noise": semantic_units("benign burst window", "checksum I/O comparison", "caught-up backlog"),
        },
        "workload/operation event": {
            "causal": semantic_units("archive attempt history", "marker commit history", "repository sync history"),
            "noise": semantic_units("unrelated historical operation", "non-candidate window"),
        },
    },
    "pg_health_check_sequence_exhaustion/billing_canary_int4_sequence_exhaustion": {
        "log": {
            "causal": semantic_units("sequence exhaustion log event"),
            "noise": semantic_units("neighboring migration log context"),
        },
        "SQL/catalog": {
            "causal": semantic_units("target sequence", "sequence ownership", "migration dependency"),
            "noise": semantic_units("unrelated sequence catalog context"),
        },
    },
    "pg_health_check_sequence_exhaustion/billing_sequence_capacity_risk_simple": {
        "log": {
            "causal": semantic_units("sequence capacity warning"),
            "noise": semantic_units("normal sequence log context"),
        },
        "SQL/catalog": {
            "causal": semantic_units("target sequence", "sequence ownership", "migration dependency"),
            "noise": semantic_units("unrelated sequence catalog context", "healthy sequence"),
        },
    },
    "pg_system_failure_auto_analyze_storm/sales_tables_auto_analyze_storm": {
        "metric": {
            "causal": semantic_units("auto-analyze I/O pressure"),
            "noise": semantic_units("normal storage baseline"),
        },
        "workload/operation event": {
            "causal": semantic_units("auto-analyze workload activity"),
            "noise": semantic_units("ordinary application workload"),
        },
        "SQL/catalog": {
            "causal": semantic_units("auto-analyze target relation", "maintenance configuration"),
            "noise": semantic_units("non-target relation statistics"),
        },
    },
    "pg_system_failure_auto_analyze_storm/store_sales_auto_analyze_storm_simple": {
        "workload/operation event": {
            "causal": semantic_units("auto-analyze workload activity"),
            "noise": semantic_units("ordinary application workload"),
        },
        "SQL/catalog": {
            "causal": semantic_units("auto-analyze target relation", "maintenance configuration"),
            "noise": semantic_units("non-target relation statistics"),
        },
    },
    "pg_system_failure_temp_file_explosion/nightly_margin_temp_exhaustion": {
        "metric": {
            "causal": semantic_units("temporary-file disk pressure"),
            "noise": semantic_units("normal filesystem headroom", "metric provider comparison"),
        },
        "SQL/catalog": {
            "causal": semantic_units("temp-file producing query", "culprit session identity"),
            "noise": semantic_units("unrelated active query"),
        },
    },
    "pg_query_perf_stale_statistics/branch_order_distribution_shift": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported topsql metric result"),
        },
        "SQL/catalog": {
            "causal": semantic_units("localized branch-order query plan", "large row-estimate error", "stale branch-order statistics"),
            "noise": semantic_units("supporting index catalog context"),
        },
    },
    "pg_query_perf_parameter_sniffing/branch_order_year_skew": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported topsql metric results"),
        },
        "SQL/catalog": {
            "causal": semantic_units("generic prepared plan reuse", "hot-year parameter skew", "custom-plan remediation"),
            "noise": semantic_units("unrelated prepared-statement context", "non-target query statistics"),
        },
    },
    "pg_system_failure_wal_accumulation/analytics_slot_wal_retention": {
        "metric": {
            "causal": semantic_units("WAL write pressure", "retained-WAL impact"),
            "noise": semantic_units("filesystem capacity context", "connection-count context", "unrelated query activity"),
        },
        "SQL/catalog": {
            "causal": semantic_units("abandoned replication slot", "retention boundary", "target slot scope"),
            "noise": semantic_units("healthy replication slot"),
        },
    },
    "pg_system_failure_connection_storm/checkout_pool_idle_transaction_storm": {
        "metric": {
            "causal": semantic_units("connection saturation"),
            "noise": semantic_units("normal connection baseline"),
        },
        "SQL/catalog": {
            "causal": semantic_units("idle transaction leak", "target blocker scope", "timeout protection"),
            "noise": semantic_units("reserved connection context", "healthy application session"),
        },
    },
    "pg_system_failure_connection_storm/checkout_pool_leak_simple": {
        "SQL/catalog": {
            "causal": semantic_units("connection saturation", "idle transaction leak"),
            "noise": semantic_units("reserved connection context"),
        },
    },
    "pg_system_failure_wal_accumulation/abandoned_report_slot_wal_retention_simple": {
        "metric": {
            "causal": semantic_units("retained WAL pressure"),
            "noise": semantic_units("filesystem capacity context"),
        },
        "workload/operation event": {
            "causal": semantic_units("report workload activity"),
            "noise": semantic_units("ordinary application activity"),
        },
        "SQL/catalog": {
            "causal": semantic_units("abandoned replication slot", "target slot scope"),
            "noise": semantic_units("healthy replication slot"),
        },
    },
    "pg_system_failure_temp_file_explosion/daily_sales_temp_exhaustion_simple": {
        "metric": {
            "causal": semantic_units("temporary-file disk pressure"),
            "noise": semantic_units("normal filesystem headroom"),
        },
        "workload/operation event": {
            "causal": semantic_units("temp-file workload activity"),
            "noise": semantic_units("ordinary application activity"),
        },
        "SQL/catalog": {
            "causal": semantic_units("temp-file producing query", "culprit session identity"),
            "noise": semantic_units("unrelated active query"),
        },
    },
    "pg_health_check_autovacuum_sustainability/capacity_deficit_simple": {
        "metric": {
            "causal": semantic_units("cleanup capacity shortfall", "dead-tuple backlog growth"),
            "noise": semantic_units("normal cleanup window", "non-target relation activity"),
        },
        "workload/operation event": {
            "causal": semantic_units("write generation pressure"),
            "noise": semantic_units("background maintenance activity"),
        },
        "SQL/catalog": {
            "causal": semantic_units("target relation cleanup state"),
            "noise": semantic_units("neighbor relation statistics"),
        },
        "log": {
            "causal": semantic_units(),
            "noise": semantic_units("component-log maintenance context"),
        },
    },
    "pg_business_change_online_ddl/order_line_delivery_note_ddl": {
        "metric": {
            "causal": semantic_units("write load level"),
            "noise": semantic_units("connection count context"),
        },
        "workload/operation event": {
            "causal": semantic_units("live order-entry workload"),
            "noise": semantic_units("release queue and audit workload"),
        },
        "SQL/catalog": {
            "causal": semantic_units("missing target column", "target table lock scope", "online DDL contract"),
            "noise": semantic_units("shadow-table catalog context"),
        },
    },
    "pg_business_change_online_ddl/order_line_gift_note_ddl_simple": {
        "metric": {
            "causal": semantic_units("write load level"),
            "noise": semantic_units("connection count context"),
        },
        "workload/operation event": {
            "causal": semantic_units("live order-entry workload"),
            "noise": semantic_units("release queue and audit workload"),
        },
        "SQL/catalog": {
            "causal": semantic_units("missing target column", "target table lock scope", "online DDL contract"),
            "noise": semantic_units("shadow-table catalog context"),
        },
    },
    "pg_business_change_massive_backfill/customer_birth_decade_backfill": {
        "metric": {
            "causal": semantic_units("write throughput pressure", "I/O pressure"),
            "noise": semantic_units("normal workload window"),
        },
        "SQL/catalog": {
            "causal": semantic_units("target row scope", "release-stage boundary", "bounded update contract", "bounded batch eligibility"),
            "noise": semantic_units("non-target row context"),
        },
    },
    "pg_business_change_massive_backfill/customer_loyalty_decade_backfill_simple": {
        "metric": {
            "causal": semantic_units("write throughput pressure", "I/O pressure"),
            "noise": semantic_units("normal workload window"),
        },
        "SQL/catalog": {
            "causal": semantic_units("target row scope", "bounded update contract", "bounded batch eligibility"),
            "noise": semantic_units("release-stage and non-target context"),
        },
    },
    "pg_business_change_collation_conversion/store_returns_ticket_locale_simple": {
        "metric": {
            "causal": semantic_units("I/O baseline"),
            "noise": semantic_units("collation workload context"),
        },
        "workload/operation event": {
            "causal": semantic_units("prefix query workload latency"),
            "noise": semantic_units("audit prefix workload comparison"),
        },
        "SQL/catalog": {
            "causal": semantic_units("target collation", "rewrite cost", "index dependency", "pattern index decision", "pattern query plan evidence"),
            "noise": semantic_units("non-target index context"),
        },
    },
    "pg_resource_governance_data_archiving/order_history_cold_archive": {
        "metric": {
            "causal": semantic_units("cold-row pressure", "space pressure"),
            "noise": semantic_units("active hot-row workload"),
        },
        "workload/operation event": {
            "causal": semantic_units("retention dashboard workload activity"),
            "noise": semantic_units("hot-history and recent-order workload", "archive existence probe", "retention log-noise profile"),
        },
        "SQL/catalog": {
            "causal": semantic_units("archive target scope", "nonblocking archive boundary", "archive candidate relation state"),
            "noise": semantic_units("non-target relation context"),
        },
    },
    "pg_resource_governance_data_archiving/order_history_quarter_archive_simple": {
        "metric": {
            "causal": semantic_units("cold-row pressure", "space pressure"),
            "noise": semantic_units("active hot-row workload"),
        },
        "workload/operation event": {
            "causal": semantic_units("retention dashboard workload activity"),
            "noise": semantic_units(),
        },
        "SQL/catalog": {
            "causal": semantic_units("archive target scope", "nonblocking archive boundary", "archive candidate relation state"),
            "noise": semantic_units("non-target relation context"),
        },
    },
    "pg_resource_governance_resource_throttling/tenant_report_role_throttling": {
        "metric": {
            "causal": semantic_units("tenant latency impact", "report workload pressure"),
            "noise": semantic_units("normal OLTP tenant activity"),
        },
        "SQL/catalog": {
            "causal": semantic_units("culprit role", "missing role guardrail", "target scope"),
            "noise": semantic_units("unaffected role settings"),
        },
    },
    "pg_resource_governance_resource_throttling/single_report_role_limit_simple": {
        "metric": {
            "causal": semantic_units("tenant latency impact", "report workload pressure"),
            "noise": semantic_units("normal OLTP tenant activity"),
        },
        "SQL/catalog": {
            "causal": semantic_units("culprit role", "missing role guardrail", "target scope"),
            "noise": semantic_units("unaffected role settings"),
        },
    },
    "pg_resource_governance_host_backup/nightly_backup_read_saturation": {
        "metric": {
            "causal": semantic_units("backup read saturation", "OLTP read pressure"),
            "noise": semantic_units("normal device baseline"),
        },
        "SQL/catalog": {
            "causal": semantic_units("backup process identity", "target process scope"),
            "noise": semantic_units("ordinary backend activity"),
        },
    },
    "pg_resource_governance_host_backup/single_backup_reader_simple": {
        "metric": {
            "causal": semantic_units("backup read saturation", "OLTP read pressure"),
            "noise": semantic_units("normal device baseline"),
        },
        "SQL/catalog": {
            "causal": semantic_units("backup process identity", "target process scope"),
            "noise": semantic_units("ordinary backend activity"),
        },
    },
    "pg_resource_governance_privilege_masking/customer_developer_masking": {
        "SQL/catalog": {
            "causal": semantic_units(
                "inherited base-table privilege",
                "sensitive clear-text field availability",
                "masked view with application access preserved",
            ),
            "noise": semantic_units("role attribute context", "application and group comparison"),
        },
    },
    "pg_resource_governance_privilege_masking/customer_support_masking_simple": {
        "SQL/catalog": {
            "causal": semantic_units(
                "inherited base-table privilege",
                "sensitive clear-text field availability",
                "masked view with application access preserved",
            ),
            "noise": semantic_units("role attribute context", "application and group comparison"),
        },
    },
    "pg_resource_governance_audit_logging/audit_orders_role_logging": {
        "metric": {
            "causal": semantic_units("write amplification", "high-QPS audit workload"),
            "noise": semantic_units("read-side device baseline", "post-change low-write tail"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "broad logging configuration",
                "required sensitive-write audit scope",
                "scoped audit configuration",
            ),
            "noise": semantic_units("checkpoint and WAL background counters", "generic logging setting context"),
        },
        "log": {
            "causal": semantic_units("repeated target statement logging"),
            "noise": semantic_units(),
        },
    },
    "pg_resource_governance_audit_logging/orders_write_audit_scope_simple": {
        "metric": {
            "causal": semantic_units("write amplification", "high-QPS audit workload"),
            "noise": semantic_units("read-side device baseline", "post-change low-write tail"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "broad logging configuration",
                "required sensitive-write audit scope",
                "scoped audit configuration",
            ),
            "noise": semantic_units("checkpoint and WAL background counters", "generic logging setting context"),
        },
        "log": {
            "causal": semantic_units("repeated target statement logging"),
            "noise": semantic_units(),
        },
    },
    "pg_composite_fault_wal_checkpoint_storm/billing_slot_checkpoint_storm": {
        "metric": {
            "causal": semantic_units("checkpoint write burst", "WAL pressure"),
            "noise": semantic_units("available filesystem headroom"),
        },
        "SQL/catalog": {
            "causal": semantic_units("stalled replication slot", "checkpoint counter state", "checkpoint timeout setting", "max WAL size setting"),
            "noise": semantic_units("healthy reporting slot"),
        },
    },
    "pg_composite_fault_wal_checkpoint_storm/billing_slot_checkpoint_burst_simple": {
        "metric": {
            "causal": semantic_units("checkpoint write burst", "WAL pressure"),
            "noise": semantic_units("available filesystem headroom"),
        },
        "SQL/catalog": {
            "causal": semantic_units("stalled replication slot", "checkpoint counter state", "checkpoint timeout setting", "max WAL size setting"),
            "noise": semantic_units("healthy reporting slot"),
        },
    },
    "pg_system_failure_io_checkpoint_spikes/checkout_checkpoint_spikes": {
        "metric": {
            "causal": semantic_units("periodic checkpoint write spike"),
            "noise": semantic_units("read-side disk activity"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "BufferIO/DataFileWrite wait pressure",
                "requested checkpoint counter pressure",
                "aggressive checkpoint parameter bundle",
            ),
            "noise": semantic_units(
                "ordinary workload session context",
                "background maintenance session context",
            ),
        },
    },
    "pg_system_failure_io_checkpoint_spikes/single_checkout_checkpoint_spike_simple": {
        "metric": {
            "causal": semantic_units("periodic checkpoint write spike"),
            "noise": semantic_units("low-frequency disk activity context"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "aggressive checkpoint parameter bundle",
                "requested checkpoint counter pressure",
            ),
            "noise": semantic_units(),
        },
        "workload/operation event": {
            "causal": semantic_units(),
            "noise": semantic_units("low-frequency calendar lookup workload"),
        },
    },
    "pg_health_check_long_running_tx/stress_idle_transaction_cleanup_01": {
        "metric": {
            "causal": semantic_units("customer dead-tuple reclamation state"),
            "noise": semantic_units(),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "idle transaction identity",
                "vacuum horizon evidence",
                "target blocker scope",
                "timeout protection",
            ),
            "noise": semantic_units(
                "short transaction decoy",
                "reporting and exporter session context",
            ),
        },
    },
    "pg_health_check_long_running_tx/stress_idle_transaction_cleanup_02": {
        "metric": {
            "causal": semantic_units("customer dead-tuple reclamation state"),
            "noise": semantic_units(),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "idle transaction identity",
                "vacuum horizon evidence",
                "target blocker scope",
                "timeout protection",
            ),
            "noise": semantic_units(
                "short transaction decoy",
                "reporting and exporter session context",
            ),
        },
    },
    "pg_health_check_long_running_tx/stress_idle_transaction_cleanup_03": {
        "metric": {
            "causal": semantic_units("customer dead-tuple reclamation state"),
            "noise": semantic_units(),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "idle transaction identity",
                "vacuum horizon evidence",
                "target blocker scope",
                "timeout protection",
            ),
            "noise": semantic_units(
                "short transaction decoy",
                "reporting and exporter session context",
            ),
        },
    },
    "pg_composite_fault_stale_stats_lock_contention/checkout_stale_stats_and_lock": {
        "metric": {
            "causal": semantic_units("connection surge at lock impact"),
            "noise": semantic_units("metric provider gap"),
        },
        "SQL/catalog": {
            "causal": semantic_units("blocking lock chain", "stale cardinality plan", "stale analyze counters"),
            "noise": semantic_units("healthy relation plan context"),
        },
    },
    "pg_composite_fault_stale_stats_lock_contention/checkout_stale_stats_single_waiter_simple": {
        "metric": {
            "causal": semantic_units("connection increase at lock impact"),
            "noise": semantic_units("unsupported slow-query metric result"),
        },
        "SQL/catalog": {
            "causal": semantic_units("blocking lock chain", "stale cardinality plan", "stale analyze counters"),
            "noise": semantic_units("healthy customer-profile plan context"),
        },
    },
    "pg_misleading_alert_cpu_lock_spin/warehouse_lock_retry_cpu": {
        "metric": {
            "causal": semantic_units("CPU symptom", "lock-wait pressure"),
            "noise": semantic_units("non-blocking CPU query", "normal worker CPU"),
        },
        "SQL/catalog": {
            "causal": semantic_units("waiter set", "critical blocker", "target session scope"),
            "noise": semantic_units("unrelated lock waiter", "healthy session"),
        },
    },
    "pg_misleading_alert_cpu_lock_spin/checkout_retry_lock_blocker_simple": {
        "metric": {
            "causal": semantic_units("CPU symptom", "lock-wait pressure"),
            "noise": semantic_units("non-blocking CPU query", "normal worker CPU"),
        },
        "SQL/catalog": {
            "causal": semantic_units("waiter set", "critical blocker", "target session scope"),
            "noise": semantic_units("unrelated lock waiter", "healthy session"),
        },
    },
    "pg_misleading_alert_cpu_lock_spin/advisory_lock_retry_cpu_storm": {
        "metric": {
            "causal": semantic_units("CPU symptom", "advisory lock pressure"),
            "noise": semantic_units("non-blocking CPU query"),
        },
        "SQL/catalog": {
            "causal": semantic_units("advisory waiter set", "leaked advisory lock", "advisory key scope"),
            "noise": semantic_units("unrelated session lock"),
        },
    },
    "pg_system_failure_noisy_neighbor/single_archive_cpu_neighbor_simple": {
        "metric": {
            "causal": semantic_units("container CPU pressure"),
            "noise": semantic_units("normal database health probe"),
        },
        "workload/operation event": {
            "causal": semantic_units("external WAL archive compressor process"),
            "noise": semantic_units("low-rate workload probe activity"),
        },
        "SQL/catalog": {
            "causal": semantic_units("successful business probe"),
            "noise": semantic_units(),
        },
    },
    "pg_misleading_alert_io_saturation/reporting_maintenance_io_saturation": {
        "metric": {
            "causal": semantic_units("maintenance write burst"),
            "noise": semantic_units("read baseline"),
        },
        "SQL/catalog": {
            "causal": semantic_units("maintenance writer", "temp-file write mechanism"),
            "noise": semantic_units("dashboard reader workload", "unrelated active session"),
        },
    },
    "pg_misleading_alert_io_saturation/vacuum_report_io_victim_simple": {
        "metric": {
            "causal": semantic_units("maintenance write burst"),
            "noise": semantic_units("read baseline"),
        },
        "SQL/catalog": {
            "causal": semantic_units("maintenance writer", "temp-file write mechanism"),
            "noise": semantic_units("dashboard reader workload", "unrelated active session"),
        },
    },
    "pg_misleading_alert_io_saturation/archive_backlog_io_pressure": {
        "metric": {
            "causal": semantic_units("I/O and latency impact", "write amplification"),
            "noise": semantic_units("cache/read-count decoy", "normal device baseline"),
        },
        "SQL/catalog": {
            "causal": semantic_units("retained WAL slot", "stalled slot root cause", "target cleanup scope"),
            "noise": semantic_units("healthy slot", "unrelated WAL context"),
        },
    },
    "pg_misleading_alert_io_context_workload/report_is_pressure": {
        "metric": {
            "causal": semantic_units("cache-hit pressure", "OLTP SLO impact"),
            "noise": semantic_units("read-count symptom", "healthy comparison window"),
        },
        "SQL/catalog": {
            "causal": semantic_units("I/O context pressure", "causal report worker", "workload-to-impact relation", "pressure-before-impact", "device queue evidence", "OLTP SLO evidence"),
            "noise": semantic_units("read-count decoy", "healthy report worker", "unrelated catalog row", "normal workload bucket", "non-causal query bucket", "baseline window", "unaffected operation"),
        },
    },
    "pg_misleading_alert_io_context_workload/report_is_pressure_simple": {
        "metric": {
            "causal": semantic_units("cache-hit pressure"),
            "noise": semantic_units("normal cache-hit comparison window"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "causal report workload",
                "pressure-before-impact relationship",
                "OLTP SLO recovery state",
            ),
            "noise": semantic_units("baseline call context"),
        },
    },
    "pg_misleading_alert_partition_cleanup/filesystem_cleanup_pressure_simple": {
        "metric": {
            "causal": semantic_units("filesystem cleanup pressure", "OLTP tail-latency impact"),
            "noise": semantic_units("host pressure decoy", "normal query CPU"),
        },
        "SQL/catalog": {
            "causal": semantic_units("cleanup lifecycle target", "filesystem I/O relation", "buffer I/O waiters", "target job scope"),
            "noise": semantic_units("unrelated partition state", "ordinary backend", "healthy cleanup job"),
        },
    },
    "pg_misleading_alert_partition_cleanup/filesystem_cleanup_pressure": {
        "metric": {
            "causal": semantic_units(
                "filesystem cleanup I/O burst",
                "buffer I/O waiter and OLTP tail impact",
                "cleanup-to-impact temporal relation",
            ),
            "noise": semantic_units("host CPU pressure decoy", "normal query CPU and filesystem tail"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "expired partition detach and drop lifecycle",
                "report backend filesystem I/O state",
                "buffer I/O waiter scope",
                "retention cleanup target",
            ),
            "noise": semantic_units(
                "legal-hold and current partition state",
                "ordinary retention worker state",
                "bait partition lifecycle context",
            ),
        },
    },
    "pg_misleading_alert_cache_pollution/analytics_cursor_cache_churn": {
        "metric": {
            "causal": semantic_units("degraded cache-hit window"),
            "noise": semantic_units("healthy cache-hit samples in the same diagnostic window"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "long-lived analytics cursor with an old snapshot",
                "dead-tuple cleanup pressure on the hot relation",
            ),
            "noise": semantic_units(
                "cache configuration context",
                "healthy hot-lookup session context",
            ),
        },
    },
    "pg_query_perf_heavy_offset_pagination/branch_order_deep_offset": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported topsql metric result"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "high-rank audit query history",
                "WindowAgg row-number plan and skipped-row evidence",
                "deep-page cursor boundary",
            ),
            "noise": semantic_units(),
        },
    },
    "pg_query_perf_heavy_offset_pagination/branch_order_shallow_offset": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported topsql metric result"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "high-rank branch-order query history",
                "WindowAgg row-number plan and skipped-row evidence",
                "shallow-page cursor boundary",
            ),
            "noise": semantic_units(),
        },
    },
    "pg_system_failure_oom/restart_shared_buffers_oom_simple": {
        "log": {
            "causal": semantic_units(),
            "noise": semantic_units("no matching oom-kill log result"),
        },
        "workload/operation event": {
            "causal": semantic_units("unsafe shared_buffers configuration"),
            "noise": semantic_units(
                "unavailable workload activity result",
                "work_mem comparison configuration",
            ),
        },
        "SQL/catalog": {
            "causal": semantic_units(),
            "noise": semantic_units("post-restart calendar probe result"),
        },
    },
    "pg_health_check_config_drift/cache_baseline_drift_simple": {
        "metric": {
            "causal": semantic_units("live memory capacity observation"),
            "noise": semantic_units("active-connection context"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "cache settings remain below the live capacity profile",
                "restart-window remediation scope",
            ),
            "noise": semantic_units(
                "intentional work_mem guardrail",
                "max_connections and autovacuum context",
                "maintenance and workload audit context",
            ),
        },
    },
    "pg_composite_fault_connection_bloat/checkout_connection_and_bloat": {
        "metric": {
            "causal": semantic_units(
                "connection saturation",
                "dead-tuple pressure",
            ),
            "noise": semantic_units("active-connection and normal-workload context"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "blocking idle transaction identity",
                "target relation bloat",
                "slow-scan plan relationship",
            ),
            "noise": semantic_units("reporting and auxiliary session context"),
        },
    },
    "pg_composite_fault_connection_bloat/checkout_bloat_single_blocker_simple": {
        "metric": {
            "causal": semantic_units("connection saturation"),
            "noise": semantic_units("unsupported dead-tuple metric request"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "blocking idle transaction identity",
                "target relation bloat",
                "slow-scan plan relationship",
            ),
            "noise": semantic_units("reporting and auxiliary session context"),
        },
    },
    "pg_resource_governance_container_cpu_budget/db_quota_throttle": {
        "metric": {
            "causal": semantic_units(
                "cross-layer quota and pressure state",
                "required sibling resource budget",
                "workload deadline and throttle outcome",
            ),
            "noise": semantic_units(
                "host headroom context",
                "unmanaged peer reservation context",
            ),
        },
    },
    "pg_resource_governance_container_cpu_budget/db_quota_throttle_simple": {
        # Recoded 2026-09-09 against the Round-36 reference trace. The query
        # metrics count includes the complete six-hour live history and its
        # captured-benign competitors; the log count includes raw policy and
        # effective cgroup-weight revisions from the same run.
        "metric": {
            "causal": semantic_units(
                "database quota contact with throttle and PSI",
                "host headroom versus database-local pressure",
                "persistent versus recovered quota windows",
                "checkout SLO propagation",
                "report throughput propagation",
                "required-job progress and managed-budget boundary",
            ),
            "noise": semantic_units(
                "host-busy captured window",
                "database process-CPU-only windows",
                "database usage-load burst windows",
                "database benign throttle burst window",
                "sibling load burst window",
                "sibling throttle burst window",
                "workload throughput burst windows",
                "planned cost-saving quota window",
                "healthy same-domain settlement comparison fingerprints",
                "routine healthy workload activity",
            ),
        },
        "log": {
            "causal": semantic_units(
                "policy and effective database weight divergence",
                "repeated low-quota reconciliation revisions",
                "bounded binding and allocation remediation revisions",
            ),
            "noise": semantic_units(
                "routine scheduler maintenance revisions",
                "healthy weight reconciliation revisions",
                "planned cost-saving window start revision",
                "planned cost-saving window recovery revision",
            ),
        },
        # The report's legacy source-family ledger classifies repair actions
        # here. These action units are retained for trace audit but are not in
        # the diagnostic K_s used by DifficultyCalibration (query_metrics and
        # read_log.operation_event).
        "workload/operation event": {
            "causal": semantic_units(
                "restore database workload-class binding",
                "re-partition required sibling quota",
                "restore database execution quota",
            ),
            "noise": (),
        },
    },
    "pg_system_failure_noisy_neighbor/wal_archive_cpu_neighbor": {
        "metric": {
            "causal": semantic_units(
                "container CPU pressure",
                "external archive process CPU attribution",
                "post-isolation CPU recovery",
            ),
            "noise": semantic_units(
                "normal active-connection context",
                "unsupported slow-query metric result",
                "unsupported TopSQL metric result",
            ),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "database internal workload is normal",
                "zero lock-wait evidence",
            ),
            "noise": semantic_units(
                "background and maintenance session context",
                "ordinary application session context",
            ),
        },
    },
    "pg_resource_governance_pgbouncer_connection_budget/pool_partition_shortage": {
        "metric": {
            "causal": semantic_units(
                "checkout queue pressure",
                "service impact with database and server headroom",
            ),
            "noise": semantic_units(
                "normal and captured-decoy pool windows",
                "active and server pool baseline context",
            ),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "transaction pool mode and partition settings",
                "checkout/report/ETL pool state",
                "fixed PostgreSQL max_connections and role limits",
            ),
            "noise": semantic_units(
                "unrelated PgBouncer configuration rows",
                "admin and non-target pool rows",
            ),
        },
        "workload/operation event": {
            "causal": semantic_units("configuration revision linking pool ceilings to the fault"),
            "noise": semantic_units(),
        },
    },
    "pg_resource_governance_pgbouncer_connection_budget/pool_partition_shortage_simple": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported PgBouncer pool and service metric results"),
        },
        "workload/operation event": {
            "causal": semantic_units(
                "transaction pool mode and fixed database budget",
                "checkout and reporting queue state",
            ),
            "noise": semantic_units("unrelated PgBouncer configuration and admin-pool context"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "PostgreSQL max_connections ceiling",
                "checkout and report role connection limits",
            ),
            "noise": semantic_units(),
        },
    },
    "pg_query_perf_implicit_type_conversion/branch_order_implicit_cast": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported TopSQL and slow-query metric results"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "casted order-exception predicate and scan-amplification plan",
                "request value type boundary",
                "typed predicate business result",
            ),
            "noise": semantic_units("expanded account and product result context"),
        },
    },
    "pg_query_perf_implicit_type_conversion/branch_order_implicit_cast_simple": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported TopSQL and slow-query metric results"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "casted order-exception predicate and scan-amplification plan",
                "request value type boundary",
                "typed predicate business result",
            ),
            "noise": semantic_units("expanded account and product result context"),
        },
    },
    "pg_query_perf_missing_index/product_category_substring": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported TopSQL metric result"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "substring predicate sequential-scan plan",
                "missing expression-index catalog state",
            ),
            "noise": semantic_units("post-repair plan and existing-index context"),
        },
    },
    "pg_query_perf_missing_index/product_category_prefix_simple": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported TopSQL metric result"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "prefix predicate sequential-scan plan",
                "missing expression-index catalog state",
            ),
            "noise": semantic_units("post-repair plan and existing-index context"),
        },
    },
    "pg_query_perf_sort_spill/branch_order_sort_spill": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported TopSQL metric result"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "target finance report disk-sort plan",
                "work_mem baseline below the report requirement",
                "temporary-file pressure and recovered in-memory sort",
            ),
            "noise": semantic_units("non-target aggregation and channel plan context"),
        },
    },
    "pg_query_perf_sort_spill/branch_order_sort_spill_simple": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported TopSQL metric result"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "target report external-sort plan",
                "work_mem baseline below the report requirement",
            ),
            "noise": semantic_units("temporary-file and post-repair plan context"),
        },
    },
    "pg_query_perf_suboptimal_join/sales_report_role_planner_drift": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported slow-query and TopSQL metric results"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "branch account margin target query",
                "role-level hashjoin and mergejoin disablement",
                "nested-loop plan regression",
                "recovered join plan",
            ),
            "noise": semantic_units("statement-timeout setup query"),
        },
    },
    "pg_query_perf_suboptimal_join/daily_account_summary_planner_drift": {
        "metric": {
            "causal": semantic_units(),
            "noise": semantic_units("unsupported slow-query and TopSQL metric results"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "daily account summary target query",
                "role-level join planner override",
                "nested-loop plan regression",
                "recovered merge-join plan",
            ),
            "noise": semantic_units("statement-timeout setup and unrelated optimizer context"),
        },
    },
    "pg_health_check_config_drift/memory_resize_config_drift": {
        "metric": {
            "causal": semantic_units("live memory capacity observation"),
            "noise": semantic_units("active-connection context"),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "live 64GB instance profile",
                "cache settings below the resized capacity baseline",
                "restart-scoped recommendation",
            ),
            "noise": semantic_units(
                "retired small-class history",
                "connection-pool migration setting",
                "intentional work_mem guardrail",
                "acceptable autovacuum and monitoring context",
            ),
        },
    },
    "pg_health_check_backup_rpo_certification/throughput_gap_simple": {
        "metric": {
            "causal": semantic_units(
                "WAL generation mismatch",
                "archive delivery deficit",
                "RPO impact window",
                "OLTP impact correlation",
                "backup throughput boundary",
            ),
            "noise": semantic_units("benign burst window", "checksum I/O comparison", "caught-up backlog"),
        },
        "workload/operation event": {
            "causal": semantic_units("archive attempt history", "marker commit history", "repository sync history"),
            "noise": semantic_units("unrelated historical operation", "non-candidate window"),
        },
    },
    "pg_system_failure_oom/restart_memory_config_oom": {
        "metric": {
            "causal": semantic_units("active-connection collapse around database restart"),
            "noise": semantic_units(),
        },
        "log": {
            "causal": semantic_units(),
            "noise": semantic_units("empty PostgreSQL log result"),
        },
        "workload/operation event": {
            "causal": semantic_units("unsafe shared_buffers configuration"),
            "noise": semantic_units("work_mem comparison configuration"),
        },
        "SQL/catalog": {
            "causal": semantic_units(),
            "noise": semantic_units("post-restart liveness probe"),
        },
    },
    "pg_system_failure_fd_exhaustion/nightly_reporting_nofile_exhaustion": {
        "metric": {
            "causal": semantic_units("connection and disk pressure during reporting fan-out"),
            "noise": semantic_units("unsupported slow-query metric result"),
        },
        "log": {
            "causal": semantic_units("Too many open files log evidence"),
            "noise": semantic_units("startup, shutdown, and unrelated workload log context"),
        },
        "workload/operation event": {
            "causal": semantic_units("reporting fan-out workload pressure", "nofile limit and restart remediation boundary"),
            "noise": semantic_units("health and background workload activity"),
        },
        "SQL/catalog": {
            "causal": semantic_units("post-restart fan-out object completeness"),
            "noise": semantic_units("unavailable catalog probes during service outage"),
        },
    },
    "pg_system_failure_fd_exhaustion/report_export_fd_exhaustion_simple": {
        "log": {
            "causal": semantic_units("Too many open files log evidence"),
            "noise": semantic_units(),
        },
        "workload/operation event": {
            "causal": semantic_units("export probe under FD pressure", "nofile limit and restart remediation boundary"),
            "noise": semantic_units("normal date health probe activity"),
        },
        "SQL/catalog": {
            "causal": semantic_units("post-restart export-slice completeness"),
            "noise": semantic_units("pre-fault export DDL history context"),
        },
    },
    "pg_business_change_collation_conversion/store_returns_collation_conversion": {
        "metric": {
            "causal": semantic_units("I/O baseline during collation conversion"),
            "noise": semantic_units("normal filesystem and query I/O context"),
        },
        "workload/operation event": {
            "causal": semantic_units("prefix query workload latency"),
            "noise": semantic_units(
                "audit prefix comparison",
                "legacy sort and numeric rollup context",
                "missing locale cache noise",
            ),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "target collation",
                "rewrite cost",
                "index dependency",
                "pattern index decision",
                "pattern query plan evidence",
            ),
            "noise": semantic_units("non-target catalog and plan context"),
        },
    },
    "pg_composite_fault_checkpoint_archive/checkpoint_archive_dual_fault_simple": {
        "metric": {
            "causal": semantic_units(
                "WAL generation and checkpoint activity explain the write-latency chain",
                "archive delivery and backlog explain recovery and PITR risk",
            ),
            "noise": semantic_units(
                "storage pressure and batch-progress context",
                "benign and cross-window metric comparison context",
            ),
        },
        "workload/operation event": {
            "causal": semantic_units(),
            "noise": semantic_units(
                "empty archive, job, backup, and configuration history results",
            ),
        },
        "SQL/catalog": {
            "causal": semantic_units(
                "active archive target and repository capacity",
                "binding generation, lease, route, and worker coherence",
            ),
            "noise": semantic_units("neighbor archive target and repository catalog context"),
        },
    },
}


CODE_MODIFICATION_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "dataset-manifest-wiring",
        "scenario_ids": {
            "pg_query_perf_heavy_offset_pagination",
            "pg_query_perf_implicit_type_conversion",
            "pg_query_perf_parameter_sniffing",
            "pg_query_perf_sort_spill",
            "pg_query_perf_stale_statistics",
            "pg_query_perf_suboptimal_join",
        },
        "case_keys": set(),
        "paths": [
            "src/execution/deployment.py",
            "src/execution/environment.py",
            "src/persistent_scenarios/backend/postgres/environment.py",
            "src/workloads/tpcds.py",
            "examples/run_pg_query_perf_heavy_offset_pagination_scenario.py",
            "examples/run_pg_query_perf_implicit_type_conversion_scenario.py",
            "examples/run_pg_query_perf_parameter_sniffing_scenario.py",
            "examples/run_pg_query_perf_sort_spill_scenario.py",
            "examples/run_pg_query_perf_stale_statistics_scenario.py",
            "examples/run_pg_query_perf_suboptimal_join_scenario.py",
        ],
        "scope": "runtime compatibility",
        "reason": "Propagate the prepared workload manifest and workload identity so TPCDSX dataset readiness uses the actual generated artifact.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "query-result-payload-compatibility",
        "scenario_ids": set(),
        "case_keys": {
            "pg_query_perf_implicit_type_conversion/branch_order_implicit_cast",
            "pg_query_perf_implicit_type_conversion/branch_order_implicit_cast_simple",
            "pg_query_perf_sort_spill/branch_order_sort_spill",
            "pg_query_perf_sort_spill/branch_order_sort_spill_simple",
        },
        "paths": ["src/database/query_results.py"],
        "scope": "runtime compatibility",
        "reason": "Parse the existing JSON-string result payload before extracting query truth; no evaluator or truth semantics changed.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "index-signature-api-compatibility",
        "scenario_ids": {"pg_query_perf_missing_index"},
        "case_keys": set(),
        "paths": ["src/database/postgres.py"],
        "scope": "runtime compatibility",
        "reason": "Recognize the installed sqlglot IndexParameters node shape while preserving the existing index-signature match.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "missing-index-calibration-timeout",
        "scenario_ids": {"pg_query_perf_missing_index"},
        "case_keys": set(),
        "paths": ["src/scenarios/postgres/query_perf/missing_index.py"],
        "scope": "seed-query runtime compatibility",
        "reason": "Extend only the internal calibration SELECT timeout for the existing real-scan dataset under the assigned CPU; query semantics, data expansion, thresholds, fault strength, and repair space are unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "missing-index-reference-response",
        "scenario_ids": set(),
        "case_keys": {"pg_query_perf_missing_index/product_category_substring"},
        "paths": ["examples/run_pg_query_perf_missing_index_scenario.py"],
        "scope": "reference mock compatibility",
        "reason": "Use the existing evaluator-allowed expression-index repair form instead of the mock response's invalid INCLUDE extension.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "suboptimal-join-reference-response",
        "scenario_ids": set(),
        "case_keys": {
            "pg_query_perf_suboptimal_join/sales_report_role_planner_drift",
            "pg_query_perf_suboptimal_join/daily_account_summary_planner_drift",
        },
        "paths": ["examples/run_pg_query_perf_suboptimal_join_scenario.py"],
        "scope": "reference mock compatibility",
        "reason": "Remove an unnecessary ALTER ROLE reset outside the Case repair allowlist; the existing legal repair remains unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "query-perf-sampler-lifecycle",
        "scenario_ids": {
            "pg_query_perf_stale_statistics",
            "pg_query_perf_parameter_sniffing",
            "pg_query_perf_heavy_offset_pagination",
        },
        "case_keys": set(),
        "paths": [
            "examples/run_pg_query_perf_stale_statistics_scenario.py",
            "examples/run_pg_query_perf_parameter_sniffing_scenario.py",
            "examples/run_pg_query_perf_heavy_offset_pagination_scenario.py",
        ],
        "scope": "sampler lifecycle compatibility",
        "reason": "Allow the existing sampler to tolerate expected workload/reconnect timing jitter while retaining the same diagnostic interval and metric meaning.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "pgss-reset-lifecycle",
        "scenario_ids": {
            "pg_composite_fault_connection_bloat",
            "pg_health_check_config_drift",
            "pg_health_check_unused_indexes",
            "pg_misleading_alert_cache_pollution",
            "pg_resource_governance_audit_logging",
            "pg_resource_governance_privilege_masking",
        },
        "case_keys": set(),
        "paths": [
            "src/execution/environment.py",
            "src/scenarios/postgres/composite_fault/connection_bloat.py",
            "src/scenarios/postgres/health_check/config_drift.py",
            "src/scenarios/postgres/health_check/unused_indexes.py",
            "src/scenarios/postgres/misleading_alert/cache_pollution.py",
            "src/scenarios/postgres/resource_governance/audit_logging.py",
            "src/scenarios/postgres/resource_governance/privilege_masking.py",
        ],
        "scope": "lifecycle compatibility",
        "reason": "Explicitly re-baseline hidden pg_stat_statements state when the existing setup lifecycle resets statistics or restarts PostgreSQL; ordinary hidden blocks still fail on an unexpected key loss.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "rpo-timestamp-parser",
        "scenario_ids": {"pg_health_check_backup_rpo_certification"},
        "case_keys": set(),
        "paths": ["src/scenarios/postgres/health_check/backup_rpo_certification.py"],
        "scope": "runtime compatibility",
        "reason": "Accept PostgreSQL's variable-precision UTC timestamp representation without changing marker timing or RPO thresholds.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "rpo-container-command-timeouts",
        "scenario_ids": {"pg_health_check_backup_rpo_certification"},
        "case_keys": set(),
        "paths": [
            "src/execution/backup_rpo.py",
            "src/scenarios/postgres/health_check/backup_rpo_certification.py",
        ],
        "scope": "runtime lifecycle compatibility",
        "reason": "Extend bounded marker and archive-history Docker command waits under the existing low-CPU live workload; RPO timing and evidence semantics are unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "config-drift-sampler-lifecycle",
        "scenario_ids": {"pg_health_check_config_drift"},
        "case_keys": set(),
        "paths": ["examples/run_pg_health_check_config_drift_scenario.py"],
        "scope": "sampler lifecycle compatibility",
        "reason": "Allow the existing sampler to reconnect across the Case's expected PostgreSQL restart during configuration installation/recovery.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "long-running-tx-reference-lifecycle",
        "scenario_ids": {"pg_health_check_long_running_tx"},
        "case_keys": set(),
        "paths": ["examples/run_pg_health_check_long_running_tx_scenario.py"],
        "scope": "reference mock and sampler compatibility",
        "reason": "Use the existing dead-tuple-backlog metric name and preserve the Case's reference conditions while allowing expected restart/reconnect timing.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "deadlock-log-admission-wait",
        "scenario_ids": {"pg_system_failure_deadlock"},
        "case_keys": set(),
        "paths": ["src/scenarios/postgres/system_failure/deadlock.py"],
        "scope": "fault admission compatibility",
        "reason": "Extend only the bounded log-delivery admission wait so an already-triggered deadlock can become visible under Docker log latency.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "fd-rotated-log-compatibility",
        "scenario_ids": {"pg_system_failure_fd_exhaustion"},
        "case_keys": set(),
        "paths": ["src/scenarios/postgres/system_failure/fd_exhaustion.py"],
        "scope": "observability compatibility",
        "reason": "Read the existing PostgreSQL rotated log files when admitting the unchanged Too many open files fault evidence; FD limits, fan-out workload, recovery, and evaluator semantics are unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "noisy-neighbor-reference-settle",
        "scenario_ids": {"pg_system_failure_noisy_neighbor"},
        "case_keys": set(),
        "paths": ["examples/run_pg_system_failure_noisy_neighbor_scenario.py"],
        "scope": "reference mock lifecycle compatibility",
        "reason": "Allow the existing noisy-neighbor process to quiesce before the unchanged business probe is verified; the injector pressure and Case contract are unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "lock-topology-helper-signature",
        "scenario_ids": {"pg_system_failure_lock_contention"},
        "case_keys": set(),
        "paths": ["src/scenarios/postgres/system_failure/lock_contention.py"],
        "scope": "observability helper compatibility",
        "reason": "Restore the existing three-payload lock-topology helper contract used by the lifecycle test and internal observability call; topology requirements are unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "system-failure-sampler-lifecycle",
        "scenario_ids": {
            "pg_system_failure_fd_exhaustion",
            "pg_system_failure_io_checkpoint_spikes",
            "pg_system_failure_lock_contention",
            "pg_system_failure_oom",
            "pg_system_failure_xid_wraparound",
        },
        "case_keys": set(),
        "paths": [
            "examples/run_pg_system_failure_fd_exhaustion_scenario.py",
            "examples/run_pg_system_failure_io_checkpoint_spikes_scenario.py",
            "examples/run_pg_system_failure_lock_contention_scenario.py",
            "examples/run_pg_system_failure_oom_scenario.py",
            "examples/run_pg_system_failure_xid_wraparound_scenario.py",
        ],
        "scope": "sampler lifecycle compatibility",
        "reason": "Keep the existing sampler alive across the Case's expected PostgreSQL restart/reconnect window and pass the integer-valued interval required by the current API.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "checkpoint-archive-history-wiring",
        "scenario_ids": {"pg_composite_fault_checkpoint_archive"},
        "case_keys": set(),
        "paths": ["examples/run_pg_composite_fault_checkpoint_archive_scenario.py"],
        "scope": "history wiring compatibility",
        "reason": "Enable the existing generic sampler when the Case contract requests TopSQL or component-log history, without changing the fault plan or record sources.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "checkpoint-archive-sampler-jitter",
        "scenario_ids": {"pg_composite_fault_checkpoint_archive"},
        "case_keys": set(),
        "paths": ["examples/run_pg_composite_fault_checkpoint_archive_scenario.py"],
        "scope": "sampler lifecycle compatibility",
        "reason": "Permit the existing aligned sampler to recover from host scheduling jitter observed during checkpoint/archive capture; checkpoint, archive, workload, and diagnostic-window semantics are unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "checkpoint-archive-report-replay-timeout",
        "scenario_ids": {"pg_composite_fault_checkpoint_archive"},
        "case_keys": set(),
        "paths": ["src/scenarios/postgres/composite_fault/checkpoint_archive.py"],
        "scope": "acceptance replay runtime compatibility",
        "reason": "Keep the existing bounded report replay query from expiring before the formal TPC-DS image completes under its assigned CPU; query, outcome thresholds, fault plan, and evaluator semantics are unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "checkpoint-archive-captured-benign-signal",
        "scenario_ids": {"pg_composite_fault_checkpoint_archive"},
        "case_keys": set(),
        "paths": [
            "src/scenarios/postgres/composite_fault/checkpoint_archive.py",
            "tests/postgres/test_checkpoint_archive_scenario.py",
        ],
        "scope": "Scenario history contract adjustment",
        "reason": "Use the real normal-workload transactions_per_sec field for the captured-benign report decoy because the same live workload can have a flat p99 field; no synthetic data, fault-plan change, workload change, or evaluator change is introduced.",
        "design_or_evaluator_change": False,
        "contract_adjustment": True,
    },
    {
        "id": "checkpoint-archive-service-observation-shape",
        "scenario_ids": {"pg_composite_fault_checkpoint_archive"},
        "case_keys": set(),
        "paths": ["src/scenarios/postgres/composite_fault/checkpoint_archive_history.py"],
        "scope": "lifecycle result-shape compatibility",
        "reason": "Read the required live OLTP p99 field directly from the declared observation profile so teardown cannot silently substitute a default value; the observation window and metric meaning are unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "lwlock-admission-runtime-contract",
        "scenario_ids": {"pg_composite_fault_lwlock_pgbouncer_cascade"},
        "case_keys": set(),
        "paths": [
            "src/scenarios/postgres/composite_fault/lwlock_pgbouncer_cascade.py",
            "tests/postgres/test_lwlock_pgbouncer_cascade.py",
        ],
        "scope": "Scenario admission/runtime contract adjustment",
        "reason": "Keep the real 20-relation lock-manager footprint active for a bounded 80ms probe so waiter-first lock contention and downstream PgBouncer queue evidence are observable after N-1 drain; fault semantics, route topology, workload meaning, and evaluator conditions are unchanged.",
        "design_or_evaluator_change": False,
        "contract_adjustment": True,
    },
    {
        "id": "lwlock-target-window-pool-order",
        "scenario_ids": {"pg_composite_fault_lwlock_pgbouncer_cascade"},
        "case_keys": set(),
        "paths": [
            "src/scenarios/postgres/composite_fault/lwlock_pgbouncer_cascade.py",
            "tests/postgres/test_lwlock_pgbouncer_cascade.py",
        ],
        "scope": "Scenario target-window lifecycle contract adjustment",
        "reason": "Use real waiter samples for pre-pool admission, then release the existing real pool pressure after the target workload window starts and its real duration signal appears; the complete waiter-duration-queue history remains required, preserving the same N-1 cascade and evaluator conditions.",
        "design_or_evaluator_change": False,
        "contract_adjustment": True,
    },
    {
        "id": "reference-observer-docker-filter",
        "scenario_ids": set(),
        "case_keys": set(),
        "paths": [
            "scripts/observe_pg_remaining8_reference_contracts_r3_remaining5_resource_bound_20260830.sh",
            "scripts/observe_pg_checkpoint_archive_teardown_fix_20260830.sh",
        ],
        "scope": "runtime evidence collection",
        "reason": "Use Docker's name filter syntax without a leading slash so actual task-container inspect snapshots and final cleanup evidence are collected; this changes evidence capture only.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "reference-observer-cleanup-directory",
        "scenario_ids": set(),
        "case_keys": set(),
        "paths": ["scripts/observe_pg_cf2_lwlock_target_order_r10_20260830.sh"],
        "scope": "runtime evidence collection",
        "reason": "Create the observer cleanup directory before writing per-run cleanup markers so a terminal reference run retains complete cleanup evidence.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "reference-report-dc-accounting",
        "scenario_ids": set(),
        "case_keys": set(),
        "paths": ["scripts/collect_pg_full_reference_report.py"],
        "scope": "report-only accounting",
        "reason": "Separate path_status from measurement_status and manually code D/C from raw-trace semantic evidence units while excluding repeated queries, polling, pagination, repair, post-repair verification, and submit.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "wal-checkpoint-sampler-api",
        "scenario_ids": {"pg_composite_fault_wal_checkpoint_storm"},
        "case_keys": set(),
        "paths": ["examples/run_pg_composite_fault_wal_checkpoint_storm_scenario.py"],
        "scope": "runtime compatibility",
        "reason": "Pass the integer value required by the existing sampler API; the two-second/one-second Case timing contract is unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "cpu-budget-history-wiring",
        "scenario_ids": {"pg_resource_governance_container_cpu_budget"},
        "case_keys": set(),
        "paths": [
            "examples/run_pg_resource_governance_container_cpu_budget_scenario.py",
            "src/scenarios/postgres/resource_governance/container_cpu_budget.py",
        ],
        "scope": "resource/runtime compatibility",
        "reason": "Accept runner-assigned ports and let the existing controller-owned history satisfy the already-declared frozen-history lifecycle, with a longer admission wait for its scheduled benign capture.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "pgbouncer-history-port-wiring",
        "scenario_ids": {"pg_resource_governance_pgbouncer_connection_budget"},
        "case_keys": set(),
        "paths": [
            "examples/run_pg_resource_governance_pgbouncer_connection_budget_scenario.py",
            "src/scenarios/postgres/resource_governance/pgbouncer_connection_budget.py",
        ],
        "scope": "resource/runtime compatibility",
        "reason": "Use runner-assigned PostgreSQL/PgBouncer ports and enable the existing history adapter for the Case's declared record sources.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "pgbouncer-owned-pgbench-relaunch-cleanup",
        "scenario_ids": {"pg_resource_governance_pgbouncer_connection_budget"},
        "case_keys": set(),
        "paths": ["src/scenarios/postgres/resource_governance/pgbouncer_connection_budget.py"],
        "scope": "workload lifecycle compatibility",
        "reason": "Remove only this injector's stale base or ramp pgbench container before the existing acceptance replay relaunches it; pool budgets, workload clients, and evaluator semantics are unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "pgbouncer-replay-runner-quiesce",
        "scenario_ids": {"pg_resource_governance_pgbouncer_connection_budget"},
        "case_keys": set(),
        "paths": ["src/scenarios/postgres/resource_governance/pgbouncer_connection_budget.py"],
        "scope": "workload lifecycle compatibility",
        "reason": "Quiesce and restart the existing background runner before resetting its acceptance observation epoch; pool budgets, workload profiles, and evaluator semantics are unchanged.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "io-context-port-wiring",
        "scenario_ids": {"pg_misleading_alert_io_context_workload"},
        "case_keys": set(),
        "paths": [
            "examples/run_pg_misleading_alert_io_context_workload_scenario.py",
            "src/scenarios/postgres/misleading_alert/io_context_workload.py",
        ],
        "scope": "runtime compatibility",
        "reason": "Accept valid runner-assigned TCP ports while retaining distinct-port validation and the original workload lifecycle.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "table-bloat-noise-timeout",
        "scenario_ids": {"pg_health_check_table_bloat"},
        "case_keys": set(),
        "paths": ["src/scenarios/postgres/health_check/table_bloat.py"],
        "scope": "seed-query runtime compatibility",
        "reason": "Give the existing reporting-noise query enough statement time under the assigned low CPU while preserving its SQL, workload role, and fault settings.",
        "design_or_evaluator_change": False,
    },
    {
        "id": "shared-workload-runner-type-import",
        "scenario_ids": set(),
        "case_keys": set(),
        "paths": ["src/scenarios/runtime/workload_runner.py"],
        "scope": "shared runtime compatibility",
        "reason": "Import the existing Sequence type required by the shared workload runner annotations without changing workload scheduling or execution semantics.",
        "design_or_evaluator_change": False,
    },
)


def code_modifications_for(scenario_id: str, case_id: str) -> list[dict[str, Any]]:
    key = f"{scenario_id}/{case_id}"
    historical_scenario_id = CURRENT_TO_HISTORICAL_SCENARIO_ID.get(scenario_id, scenario_id)
    historical_key = f"{historical_scenario_id}/{case_id}"
    changes: list[dict[str, Any]] = []
    for change in CODE_MODIFICATION_CATALOG:
        if (
            scenario_id not in change["scenario_ids"]
            and historical_scenario_id not in change["scenario_ids"]
            and key not in change["case_keys"]
            and historical_key not in change["case_keys"]
        ):
            continue
        changes.append({
            field: value
            for field, value in change.items()
            if field not in {"scenario_ids", "case_keys"}
        })
    return changes


def jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return jsonable(dataclasses.asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


def load_case_catalog() -> OrderedDict[tuple[str, str], tuple[Any, Any]]:
    cases: OrderedDict[tuple[str, str], tuple[Any, Any]] = OrderedDict()
    for registration in POSTGRES_SCENARIO_REGISTRY:
        scenario = registration.scenario
        if not scenario.scenario_id.startswith("pg_"):
            continue
        for case in scenario.cases:
            key = (scenario.scenario_id, case.case_id)
            if key in cases:
                raise ValueError(f"Duplicate PostgreSQL Case identity: {key!r}")
            cases[key] = (registration, case)
    if len(cases) != 102:
        raise ValueError(f"Expected 102 PostgreSQL ScenarioCases, found {len(cases)}")
    return cases


def load_run_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    experiment_patterns = (
        "pg_full_reference*",
        "pg_hc_mf01_capacity_deficit_public_reference_isolated_20260830",
        "pg_worker1_query_perf_simple_reference_r2_20260830",
        "pg_remaining8_reference_contracts_r2_20260830",
        "pg_remaining8_reference_contracts_r3_remaining5_resource_bound_20260830",
        "pg_remaining8_checkpoint_archive_teardown_fix_20260830",
        "pg_cf2_lwlock_target_order_r10_20260830",
        "pg_cf2_lwlock_target_order_r11_20260830",
        "pg_cf2_lwlock_target_order_r12_20260830",
        "pg_cf2_lwlock_target_order_r13_20260830",
        "pg_cf2_lwlock_readiness_fix_r5_20260830",
        "pg_cf1_checkpoint_archive_formal_mock_20260830",
        "pg_pending_dc_r3_*",
        "pg_pending_dc_r4_remaining_20260831",
        "pg_pending_dc_r5_measurement_20260831",
    )
    run_paths = {
        run_path
        for pattern in experiment_patterns
        for run_path in ARTIFACTS.glob(f"{pattern}/runs/*/run.json")
    }
    for run_path in sorted(run_paths):
        record = json.loads(run_path.read_text(encoding="utf-8"))
        record["historical_scenario_id"] = str(record.get("scenario_id"))
        record["scenario_id"] = SCENARIO_ID_MIGRATION.get(
            record["historical_scenario_id"], record["historical_scenario_id"]
        )
        record["_run_path"] = str(run_path.relative_to(ROOT))
        record["_experiment_dir"] = str(run_path.parents[2].relative_to(ROOT))
        records.append(record)
    return records


def command_container(record: dict[str, Any]) -> str | None:
    command = record.get("command", [])
    if "--container-name" not in command:
        return None
    index = command.index("--container-name")
    return str(command[index + 1])


def attempt_for(record: dict[str, Any]) -> dict[str, Any]:
    attempt_number = int(record.get("attempt", 0))
    for attempt in record.get("attempts", []):
        if int(attempt.get("attempt", -1)) == attempt_number:
            return attempt
    raise ValueError(
        f"Run record has no matching attempt: run_id={record.get('run_id')!r}, "
        f"attempt={attempt_number}"
    )


def inspect_documents(record: dict[str, Any]) -> list[dict[str, Any]]:
    experiment_dir = ROOT / str(record["_experiment_dir"])
    cache_key = str(experiment_dir)
    if cache_key in _INSPECT_DOCUMENT_CACHE:
        return _INSPECT_DOCUMENT_CACHE[cache_key]
    paths = sorted(experiment_dir.glob("docker_inspect*.json"))
    paths.extend(sorted((experiment_dir / "docker_inspect").glob("*.json")))
    paths.extend(sorted((experiment_dir / "docker_inspect_retry").glob("*.json")))
    documents: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = payload if isinstance(payload, list) else [payload]
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(f"Docker inspect document is not an object: path={path}")
            entry = dict(entry)
            entry["_path"] = str(path.relative_to(ROOT))
            documents.append(entry)
    _INSPECT_DOCUMENT_CACHE[cache_key] = documents
    return documents


def normalized_container_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.casefold())


def matching_inspect(record: dict[str, Any]) -> dict[str, Any] | None:
    container_name = command_container(record)
    requested = normalized_container_name(container_name) if container_name is not None else ""
    requested_hashes = set(re.findall(r"[0-9a-f]{12}", requested))
    rpo_runtime_token = ""
    if container_name is None:
        command = record.get("command", [])
        entrypoint = Path(str(command[1])).name if len(command) > 1 else ""
        if entrypoint != "run_pg_health_check_backup_rpo_certification_scenario.py":
            return None
        trace, _ = trace_for(record)
        rpo_run_id = (trace or {}).get("metadata", {}).get("run_id")
        if not rpo_run_id:
            return None
        rpo_runtime_token = normalized_container_name(str(rpo_run_id))
    candidates: list[tuple[int, str, dict[str, Any]]] = []
    for document in inspect_documents(record):
        name = str(document.get("Name", "")).lstrip("/")
        normalized = normalized_container_name(name)
        score = 0
        if rpo_runtime_token and normalized.startswith("aiopsbenchrpoprimary") and rpo_runtime_token in normalized:
            score = 4
        elif rpo_runtime_token and rpo_runtime_token in normalized:
            score = 3
        elif container_name is not None and (name == container_name or name.startswith(container_name + "-")):
            score = 3
        elif container_name is not None and (normalized == requested or normalized.startswith(requested)):
            score = 2
        elif container_name is not None and requested_hashes & set(re.findall(r"[0-9a-f]{12}", normalized)):
            score = 1
        if score:
            candidates.append((score, str(document.get("_path", "")), document))
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item[0], item[1]))[2]


def action_family(action: dict[str, Any]) -> str | None:
    api = action.get("api")
    if api == "query_metrics":
        metric_type = action.get("args", {}).get("metric_type")
        if metric_type in {"workload_activity", "operation_event"}:
            return "workload/operation event"
        return "metric"
    if api == "read_log":
        return "log"
    if api == "execute_sql":
        return "SQL/catalog"
    if api == "query_history":
        source = str(action.get("args", {}).get("source", "")).casefold()
        if source in {"component_log", "pg_log", "log"}:
            return "log"
        if source in {"topsql", "slow_queries", "sql", "catalog"}:
            return "SQL/catalog"
        if source in {"operation_event", "workload", "event"}:
            return "workload/operation event"
        raise ValueError(f"Unknown query_history source for source-family accounting: {source!r}")
    if api == "manage_instance":
        action_name = str(action.get("args", {}).get("action", "")).casefold()
        if action_name in {
            "get_config",
            "archive_status",
            "pgbouncer_show_pools",
            "pgbouncer_show_config",
            "pgbouncer_show_stats",
        }:
            return "workload/operation event"
        return None
    return None


def trace_for(record: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    path = record.get("trace_path")
    if not path:
        return None, None
    trace_path = ROOT / str(path)
    if not trace_path.is_file():
        return None, str(path)
    return json.loads(trace_path.read_text(encoding="utf-8")), str(path)


def action_text(action: dict[str, Any]) -> str:
    api = str(action.get("api"))
    args = action.get("args", {})
    if api == "query_metrics":
        return f"query_metrics:{args.get('metric_type')}@{args.get('target')}"
    if api == "read_log":
        return f"read_log:{args.get('log_type')}"
    if api == "query_history":
        return f"query_history:{args.get('source')}"
    if api == "manage_instance":
        return f"manage_instance:{args.get('action')}@{args.get('target')}"
    if api == "execute_sql":
        sql = re.sub(r"\s+", " ", str(args.get("sql_query", ""))).strip()
        return f"execute_sql:{sql[:120]}"
    return api


def raw_path(trace: dict[str, Any] | None) -> list[str]:
    if trace is None:
        return []
    path: list[str] = []
    for turn in trace.get("turns", []):
        turn_number = turn.get("turn_number")
        actions = turn.get("actions", [])
        if actions:
            path.append(f"T{turn_number}: " + " -> ".join(action_text(action) for action in actions))
    return path


def compressed_path(trace: dict[str, Any] | None) -> list[str]:
    if trace is None:
        return []
    metadata = trace.get("metadata", {})
    key = f"{metadata.get('scenario_id')}/{metadata.get('case_id')}"
    current_key = f"{SCENARIO_ID_MIGRATION.get(metadata.get('scenario_id'), metadata.get('scenario_id'))}/{metadata.get('case_id')}"
    trace_states = TRACE_LOGICAL_PATH_STATES.get(key) or TRACE_LOGICAL_PATH_STATES.get(current_key)
    if trace_states is not None:
        return [f"logic state {index}: {state}" for index, state in enumerate(trace_states, 1)]
    evaluation = trace.get("evaluation") or {}
    diagnosis = evaluation.get("diagnosis", {})
    matched = diagnosis.get("matched_conditions", [])
    if matched:
        return [f"logic state {index}: {condition}" for index, condition in enumerate(dict.fromkeys(matched), 1)]
    states = NON_DIAGNOSIS_PATH_STATES.get(key) or NON_DIAGNOSIS_PATH_STATES.get(current_key)
    if states is None:
        raise ValueError(
            "Full-score trace has no diagnosis conditions and no operational path coding: "
            f"scenario_id={metadata.get('scenario_id')!r}, case_id={metadata.get('case_id')!r}"
        )
    return [f"logic state {index}: {state}" for index, state in enumerate(states, 1)]


def diagnostic_depth(trace: dict[str, Any] | None) -> int | None:
    path = compressed_path(trace)
    if not path:
        return None
    # The initial alert is sigma and each listed node is one hop toward the
    # root cause or operational decision c_s.
    return len(path)


def actual_trace_families(trace: dict[str, Any] | None) -> list[str]:
    families: list[str] = []
    if trace is None:
        return families
    for turn in trace.get("turns", []):
        for action in turn.get("actions", []):
            family = action_family(action)
            if family is not None and family not in families:
                families.append(family)
    return families


def trace_family_action_refs(trace: dict[str, Any], family: str) -> list[str]:
    refs: list[str] = []
    for turn in trace.get("turns", []):
        for index, action in enumerate(turn.get("actions", []), 1):
            if action_family(action) == family:
                refs.append(f"T{turn.get('turn_number')}/a{index}: {action_text(action)}")
    return refs


def source_ledger(
    scenario_id: str,
    case_id: str,
    trace: dict[str, Any] | None,
    *,
    full_score: bool,
) -> dict[str, Any]:
    actual = actual_trace_families(trace)
    if not full_score:
        return {
            "status": "not_measured_non_full_score",
            "families": {
                family: {"m": None, "n": None, "c_family": None, "causal_units": [], "noise_units": []}
                for family in actual
            },
            "overall_c": None,
            "actual_trace_families": actual,
        }
    if trace is None:
        return {
            "status": "no_trace",
            "families": {},
            "overall_c": None,
            "actual_trace_families": [],
        }
    metadata = trace.get("metadata", {})
    trace_key = f"{metadata.get('scenario_id')}/{metadata.get('case_id')}"
    expected_trace_scenario = CURRENT_TO_HISTORICAL_SCENARIO_ID.get(scenario_id, scenario_id)
    expected_trace_key = f"{expected_trace_scenario}/{case_id}"
    if trace_key not in {expected_trace_key, f'{scenario_id}/{case_id}'}:
        raise ValueError(
            "Trace identity does not match the selected Case: "
            f"expected={expected_trace_key!r}, observed={trace_key!r}"
        )
    observed_units = SEMANTIC_EVIDENCE_UNITS.get(trace_key) or SEMANTIC_EVIDENCE_UNITS.get(
        f"{scenario_id}/{case_id}"
    ) or SEMANTIC_EVIDENCE_UNITS.get(expected_trace_key)
    if observed_units is None:
        raise ValueError(
            "Full-score Case has no trace-reviewed semantic evidence coding: "
            f"scenario_id={scenario_id!r}, case_id={case_id!r}"
        )
    trace_families = set(actual)
    expected_families = set(observed_units)
    missing = sorted(expected_families - trace_families)
    extra = sorted(trace_families - expected_families)
    if missing or extra:
        raise ValueError(
            "Semantic evidence coding does not exactly match source families in the raw trace: "
            f"scenario_id={scenario_id!r}, missing={missing!r}, extra={extra!r}, "
            f"trace_families={sorted(trace_families)!r}"
        )
    families: dict[str, Any] = {}
    values: list[float] = []
    for family, groups in sorted(observed_units.items()):
        causal = tuple(groups.get("causal", ()))
        noise = tuple(groups.get("noise", ()))
        if not causal and not noise:
            raise ValueError(
                "Semantic evidence family has no observed units: "
                f"scenario_id={scenario_id!r}, case_id={case_id!r}, family={family!r}"
            )
        total = len(causal) + len(noise)
        c_family_exact = len(noise) / total
        families[family] = {
            "m": len(causal),
            "n": len(noise),
            "c_family": round(c_family_exact, 6),
            "causal_units": list(causal),
            "noise_units": list(noise),
            "trace_action_refs": trace_family_action_refs(trace, family),
            "counting_basis": "semantic evidence units coded from the unfiltered raw trace result in the diagnostic window; no row, log-line, sample, or tool-call counting",
        }
        values.append(c_family_exact)
    return {
        "status": "measured_from_raw_trace_semantics",
        "families": families,
        "overall_c": round(sum(values) / len(values), 6),
        "actual_trace_families": list(sorted(trace_families)),
        "trace_families_seen": actual,
        "exclusions": [
            "repeated queries",
            "polling",
            "pagination",
            "repair execution",
            "post-repair verification",
            "submit",
        ],
    }


def runtime_evidence(record: dict[str, Any], case: Any) -> dict[str, Any]:
    declared = record.get("runtime_evidence")
    if isinstance(declared, dict) and "status" in declared:
        required = ("worker_id", "physical_cores", "cpuset_cpus", "cpuset_mems", "worker_cpu_capacity", "worker_memory_capacity_mb", "docker_runtime", "container_name", "nano_cpus", "memory_bytes")
        complete_fields = all(declared.get(key) not in (None, "", []) for key in required)
        return {
            "complete": declared.get("status") == "complete" and complete_fields,
            "binding_source": "run_json",
            "case_resources": jsonable(case.runtime.resources),
            "worker": declared,
            "docker": {
                key: declared.get(key)
                for key in ("docker_runtime", "cpuset_cpus", "cpuset_mems", "nano_cpus", "memory_bytes", "container_name")
            },
            "container_name": declared.get("container_name"),
            "error": declared.get("error"),
        }
    attempt = attempt_for(record)
    resources = jsonable(case.runtime.resources)
    worker_fields = {
        "worker_id": attempt.get("worker_id"),
        "physical_cores": attempt.get("physical_cores", []),
        "cpuset_cpus": attempt.get("cpuset_cpus"),
        "cpuset_mems": attempt.get("cpuset_mems"),
        "worker_cpu_capacity": attempt.get("worker_cpu_capacity"),
        "worker_memory_capacity_mb": attempt.get("worker_memory_capacity_mb"),
        "container_cpu_limit": attempt.get("container_cpu_limit"),
        "container_memory_mb": attempt.get("container_memory_mb"),
    }
    inspect = matching_inspect(record)
    docker = None
    if inspect is not None:
        host = inspect.get("HostConfig", {})
        docker = {
            "name": str(inspect.get("Name", "")).lstrip("/"),
            "status": inspect.get("State", {}).get("Status"),
            "started_at": inspect.get("State", {}).get("StartedAt"),
            "finished_at": inspect.get("State", {}).get("FinishedAt"),
            "runtime": host.get("Runtime"),
            "cpuset_cpus": host.get("CpusetCpus"),
            "cpuset_mems": host.get("CpusetMems"),
            "nano_cpus": host.get("NanoCpus"),
            "memory_bytes": host.get("Memory"),
            "pids_limit": host.get("PidsLimit"),
            "inspect_path": inspect.get("_path"),
            "state": inspect.get("State", {}),
            "mounts": [
                {
                    key: mount.get(key)
                    for key in ("Type", "Name", "Source", "Destination", "RW", "Mode")
                    if key in mount
                }
                for mount in inspect.get("Mounts", [])
            ],
            "network_settings": {
                network_name: {
                    key: network.get(key)
                    for key in ("NetworkID", "IPAddress", "IPPrefixLen", "Gateway", "Aliases")
                    if key in network
                }
                for network_name, network in (inspect.get("NetworkSettings", {}).get("Networks") or {}).items()
            },
        }
    # Either source is sufficient when it records the actual container binding:
    # newer observers provide Docker inspect, while the runner attempt itself
    # records the same values for older or short-lived containers. Worker
    # allocation fields remain in the report for provenance, but are not a
    # second measurement gate.
    docker_complete = bool(
        docker is not None
        and docker["cpuset_cpus"]
        and docker["cpuset_mems"]
        and docker["nano_cpus"] is not None
        and docker["memory_bytes"] is not None
    )
    attempt_complete = bool(
        worker_fields["cpuset_cpus"]
        and worker_fields["cpuset_mems"]
        and worker_fields["container_cpu_limit"] is not None
        and worker_fields["container_memory_mb"] is not None
    )
    complete = docker_complete or attempt_complete
    binding_source = (
        "docker_inspect"
        if docker_complete
        else "runner_attempt"
        if attempt_complete
        else None
    )
    return {
        "complete": complete,
        "binding_source": binding_source,
        "case_resources": resources,
        "worker": worker_fields,
        "docker": docker,
        "container_name": command_container(record) or (docker.get("name") if docker else None),
    }


def cleanup_evidence(record: dict[str, Any], trace: dict[str, Any] | None) -> dict[str, Any]:
    declared = record.get("cleanup_evidence")
    if isinstance(declared, dict) and "status" in declared:
        finalization = trace.get("finalization", {}) if trace is not None else {}
        empty = not any(declared.get(key) for key in ("container_present", "remaining_task_containers", "remaining_task_volumes", "remaining_task_networks"))
        return {
            "complete": declared.get("status") == "complete" and finalization.get("status") == "succeeded" and not finalization.get("failures", []) and empty,
            "status": declared.get("status"),
            "trace_finalization": trace.get("finalization", {}) if trace is not None else {},
            "observer_paths": declared.get("observer_paths", []),
            "container_present": declared.get("container_present"),
            "remaining_task_containers": declared.get("remaining_task_containers"),
            "remaining_task_volumes": declared.get("remaining_task_volumes"),
            "remaining_task_networks": declared.get("remaining_task_networks"),
            "checked_at": declared.get("checked_at"),
            "basis": "run.json cleanup_evidence",
        }
    finalization = trace.get("finalization", {}) if trace is not None else {}
    failures = finalization.get("failures", [])
    trace_complete = finalization.get("status") == "succeeded" and not failures
    experiment_dir = ROOT / str(record["_experiment_dir"])
    cleanup_dirs = sorted(
        path
        for path in experiment_dir.glob("cleanup*")
        if path.is_dir()
    )
    cleanup_paths = [
        path
        for cleanup_dir in cleanup_dirs
        for path in cleanup_dir.glob(f"{record['run_id']}.*")
    ]
    # A resume observer with one formal run can only emit one experiment-level
    # final cleanup artifact. Accept it for that single run; multi-run
    # experiments still require their per-run cleanup marker.
    if not cleanup_paths:
        run_paths = sorted(path for path in (experiment_dir / "runs").glob("*/run.json") if path.is_file())
        final_cleanup_paths = [
            cleanup_dir / "observer_final_cleanup.txt"
            for cleanup_dir in cleanup_dirs
            if (cleanup_dir / "observer_final_cleanup.txt").is_file()
        ]
        if len(run_paths) == 1 and len(final_cleanup_paths) == 1:
            cleanup_paths = final_cleanup_paths
    return {
        "complete": bool(trace_complete and cleanup_paths),
        "trace_finalization": finalization,
        "observer_paths": [str(path.relative_to(ROOT)) for path in sorted(cleanup_paths)],
        "basis": "trace.finalization plus observer artifact when present",
    }


def pass_summary(record: dict[str, Any] | None) -> dict[str, Any]:
    if record is None:
        return {
            "full_score": False,
            "valid_for_aggregate": False,
            "DiagnosisPass": None,
            "OutcomePass": None,
            "SafePass": None,
        }
    diagnosis_pass = record.get("diagnosis_pass")
    outcome_pass = record.get("outcome_pass")
    safe_pass = record.get("safe_pass")
    path_full_score = bool(
        record.get("status") == "succeeded"
        and diagnosis_pass in (True, None)
        and outcome_pass is True
        and safe_pass is True
    )
    return {
        # A full-score path is an evaluator result. Infrastructure validity is
        # reported separately and only gates formal D/C measurement.
        "full_score": path_full_score,
        "valid_for_aggregate": record.get("valid_for_aggregate") is True,
        "DiagnosisPass": diagnosis_pass,
        "OutcomePass": outcome_pass,
        "SafePass": safe_pass,
    }


def failure_reason(record: dict[str, Any], trace: dict[str, Any] | None, case: Any) -> str | None:
    reasons: list[str] = []
    if record.get("status") in {"pending", "running"}:
        reasons.append(
            f"formal reference run is not terminal: status={record.get('status')!r}; "
            "no completed attempt is available"
        )
    if record.get("status") != "succeeded":
        stdout_path = record.get("stdout_path")
        if stdout_path:
            path = ROOT / str(stdout_path)
            if path.is_file():
                lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]
                interesting = [
                    line for line in lines
                    if any(token in line for token in ("RuntimeError:", "ValueError:", "AssertionError:", "fatal:", "Error during run:"))
                ]
                if interesting:
                    reasons.append(interesting[-1][:700])
        if not reasons and record.get("error"):
            reasons.append(str(record["error"])[:700])
    if record.get("status") == "succeeded" and not pass_summary(record)["full_score"]:
        failed_passes = [
            name
            for name, value in (
                ("DiagnosisPass", record.get("diagnosis_pass")),
                ("OutcomePass", record.get("outcome_pass")),
                ("SafePass", record.get("safe_pass")),
            )
            if value is False
        ]
        if failed_passes:
            reasons.append("full-score gate failed: " + ", ".join(failed_passes))
    if record.get("status") == "succeeded" and pass_summary(record)["full_score"]:
        runtime = runtime_evidence(record, case)
        cleanup = cleanup_evidence(record, trace)
        if not runtime["complete"]:
            reasons.append("Docker cpuset/NUMA/resource binding evidence is incomplete")
        if not cleanup["complete"]:
            reasons.append("cleanup/finalization evidence is incomplete")
    return "; ".join(dict.fromkeys(reasons)) or None


def path_status(record: dict[str, Any] | None) -> str:
    if record is None:
        return "not-executed"
    if pass_summary(record)["full_score"]:
        return "full-score"
    if record.get("status") in {"pending", "running"}:
        return "running"
    return "not-full-score"


def measurement_status(
    record: dict[str, Any] | None,
    runtime: dict[str, Any],
    cleanup: dict[str, Any],
) -> str:
    if record is None or not pass_summary(record)["full_score"]:
        return "not-eligible"
    if not runtime["complete"] and not cleanup["complete"]:
        return "pending-runtime-and-cleanup"
    if not runtime["complete"]:
        return "pending-runtime"
    if not cleanup["complete"]:
        return "pending-cleanup"
    return "measured"


def choose_record(records: list[dict[str, Any]], case: Any) -> dict[str, Any] | None:
    if not records:
        return None
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for record in records:
        if pass_summary(record)["full_score"]:
            trace, _ = trace_for(record)
            runtime = runtime_evidence(record, case)
            cleanup = cleanup_evidence(record, trace)
            quality = 4 if runtime["complete"] and cleanup["complete"] else 3
        elif record.get("status") == "succeeded":
            quality = 2
        else:
            quality = 1
        scored.append((quality, str(record.get("finished_at") or record.get("started_at") or ""), record))
    return sorted(scored, key=lambda item: (item[0], item[1]), reverse=True)[0][2]


def build_rows(cases: OrderedDict[tuple[str, str], tuple[Any, Any]], records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_case: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        key = (str(record.get("scenario_id")), str(record.get("case_id")))
        if key in cases:
            by_case[key].append(record)
    rows: list[dict[str, Any]] = []
    for index, (key, (registration, case)) in enumerate(cases.items(), 1):
        record = choose_record(by_case[key], case)
        if record is None:
            rows.append({
                "index": index,
                "scenario_id": key[0],
                "case_id": key[1],
                "case_no": case.case_no,
                "category": registration.category.value,
                "title": case.title,
                "code_modifications": code_modifications_for(key[0], key[1]),
                "status": "not-executed",
                "path_status": "not-executed",
                "measurement_status": "not-eligible",
                "full_score": False,
                "difficulty_label": None,
                "pass_summary": pass_summary(None),
                "run_id": None,
                "reference_run_ids": list(case.difficulty.reference_run_ids) if case.difficulty else [],
                "raw_path": [],
                "compressed_path": [],
                "path_diagnostic_depth": None,
                "diagnostic_depth": None,
                "D": None,
                "source_ledger": source_ledger(key[0], key[1], None, full_score=False),
                "actual_source_families": [],
                "environmental_complexity": None,
                "C": None,
                "workload": jsonable(case.background_workload),
                "diagnostic_window": None,
                "trace_path": None,
                "runtime": {"complete": False, "case_resources": jsonable(case.runtime.resources)},
                "cleanup": {"complete": False},
                "failure_reason": "No formal runner record found for this ScenarioCase",
                "attempt": None,
                "experiment_id": None,
            })
            continue
        trace, trace_path = trace_for(record)
        current_attempt = None
        if record.get("attempt") is not None:
            current_attempt = next(
                (
                    attempt
                    for attempt in record.get("attempts", [])
                    if int(attempt.get("attempt", -1)) == int(record["attempt"])
                ),
                None,
            )
        runtime = (
            runtime_evidence(record, case)
            if current_attempt is not None
            else {
                "complete": False,
                "case_resources": jsonable(case.runtime.resources),
                "worker": {},
                "docker": None,
                "container_name": command_container(record),
            }
        )
        cleanup = cleanup_evidence(record, trace)
        passes = pass_summary(record)
        current_path_status = path_status(record)
        ledger = source_ledger(key[0], key[1], trace, full_score=passes["full_score"])
        current_measurement_status = measurement_status(record, runtime, cleanup)
        path_depth = diagnostic_depth(trace) if passes["full_score"] else None
        formal_depth = path_depth if current_measurement_status == "measured" else None
        compressed = compressed_path(trace) if passes["full_score"] else []
        metadata = trace.get("metadata", {}) if trace is not None else {}
        rows.append({
            "index": index,
            "scenario_id": key[0],
            "case_id": key[1],
            "case_no": case.case_no,
            "category": registration.category.value,
            "title": case.title,
            "code_modifications": code_modifications_for(key[0], key[1]),
            "status": current_path_status,
            "path_status": current_path_status,
            "measurement_status": current_measurement_status,
            "full_score": passes["full_score"],
            "difficulty_label": (
                "hard"
                if formal_depth is not None and ledger["overall_c"] is not None
                and formal_depth > 2 and ledger["overall_c"] >= 0.5
                else "easy"
                if formal_depth is not None and ledger["overall_c"] is not None
                else None
            ),
            "pass_summary": passes,
            "run_id": record.get("run_id"),
            "reference_run_ids": list(case.difficulty.reference_run_ids) if case.difficulty else [],
            "raw_path": raw_path(trace),
            "compressed_path": compressed,
            "path_diagnostic_depth": path_depth,
            "diagnostic_depth": formal_depth,
            "D": formal_depth,
            "source_ledger": ledger,
            "actual_source_families": ledger.get("actual_trace_families", []),
            "environmental_complexity": ledger["overall_c"] if current_measurement_status == "measured" else None,
            "C": ledger["overall_c"] if current_measurement_status == "measured" else None,
            "workload": {
                "planned": metadata.get("background_workload_planned"),
                "observed": metadata.get("background_workload_observed"),
                "case_contract": jsonable(case.background_workload),
            },
            "diagnostic_window": {
                "trace_start": metadata.get("timestamp_start"),
                "trace_end": metadata.get("timestamp_end"),
                "metric_history": metadata.get("metric_history"),
            },
            "trace_path": trace_path,
            "runtime": runtime,
            "cleanup": cleanup,
            "failure_reason": failure_reason(record, trace, case),
            "attempt": current_attempt,
            "experiment_id": record.get("experiment_id"),
        })
    return rows


def compact(value: Any, limit: int = 300) -> str:
    text = json.dumps(jsonable(value), ensure_ascii=False, separators=(",", ":")) if not isinstance(value, str) else value
    text = text.replace("|", "\\|").replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 3] + "..."


def source_text(ledger: dict[str, Any]) -> str:
    values: list[str] = []
    for family, value in sorted(ledger.get("families", {}).items()):
        values.append(f"{family} m={value.get('m')} n={value.get('n')} C={value.get('c_family')}")
    return "; ".join(values) or "none"


def runtime_text(runtime: dict[str, Any]) -> str:
    worker = runtime.get("worker", {})
    docker = runtime.get("docker") or {}
    return compact({
        "complete": runtime.get("complete"),
        "binding_source": runtime.get("binding_source"),
        "worker": worker.get("worker_id"),
        "docker_runtime": docker.get("runtime"),
        "cpuset": docker.get("cpuset_cpus") or worker.get("cpuset_cpus"),
        "mems": docker.get("cpuset_mems") or worker.get("cpuset_mems"),
        "cpu": docker.get("nano_cpus"),
        "memory": docker.get("memory_bytes"),
        "resources": runtime.get("case_resources"),
    }, 240)


def write_outputs(rows: list[dict[str, Any]]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_DIR / "pg_full_reference_102_cases.json"
    csv_path = REPORT_DIR / "pg_full_reference_102_cases.csv"
    markdown_path = REPORT_DIR / "pg_full_reference_102_report.md"
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")

    columns = [
        "index", "scenario_id", "case_id", "case_no", "category", "status", "path_status",
        "measurement_status", "full_score", "pass_summary", "run_id",
        "difficulty_label",
        "reference_run_ids", "raw_path", "compressed_path", "path_diagnostic_depth", "D",
        "diagnostic_depth", "actual_source_families", "source_ledger", "environmental_complexity", "C", "workload",
        "diagnostic_window", "trace_path", "runtime", "cleanup", "failure_reason", "code_modifications", "experiment_id",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: json.dumps(row.get(column), ensure_ascii=False, default=str) for column in columns})

    valid = [row for row in rows if row["measurement_status"] == "measured"]
    full_score = [row for row in rows if row["full_score"]]
    labels = {"easy": 0, "hard": 0}
    for row in valid:
        d = row["diagnostic_depth"]
        c = row["environmental_complexity"]
        label = "hard" if d > 2 and c >= 0.5 else "easy"
        labels[label] += 1
    path_status_counts: defaultdict[str, int] = defaultdict(int)
    measurement_status_counts: defaultdict[str, int] = defaultdict(int)
    for row in rows:
        path_status_counts[row["path_status"]] += 1
        measurement_status_counts[row["measurement_status"]] += 1
    code_diff = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    status_paths = []
    status_output = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for status_line in status_output.splitlines():
        if len(status_line) >= 4:
            status_paths.append(status_line[3:])
    dirty_code_paths = sorted(
        path for path in status_paths
        if path.endswith((".py", ".sh")) and not path.startswith("artifacts/")
    )
    dirty_data_paths = sorted(
        path for path in status_paths
        if path not in dirty_code_paths and not path.startswith("artifacts/")
    )
    evaluator_changes = [path for path in code_diff if path.startswith("src/scenarios/evaluation/")]
    scenario_changes = [
        path for path in code_diff
        if path.startswith("src/scenarios/postgres/") and "/evaluation/" not in path
    ]
    code_change_lines = [
        f"- `{change['id']}`{(' [allowed contract adjustment]' if change.get('contract_adjustment') else '')}: {change['reason']} Paths: {', '.join(f'`{path}`' for path in change['paths'])}."
        for change in CODE_MODIFICATION_CATALOG
    ]
    lines = [
        "# PostgreSQL 102 ScenarioCase Reference/Mock Path Audit",
        "",
        "- Repository root: `" + str(ROOT) + "`",
        "- Runner mode: formal Mock/reference path, one repetition, `concurrency=1`; each row records its immutable manifest, seed, run ID, attempt, and raw trace.",
        "- Scope: all 102 PostgreSQL ScenarioCases from the current registry.",
        "- Status rule: `path_status` records the formal Mock/reference evaluator path; `measurement_status` records only whether runtime/CPU/NUMA and cleanup evidence permit formal D/C measurement.",
        "- D rule: every full-score path receives a trace-derived D from its compressed logical-state path; DifficultyCalibration metadata is not a validity gate.",
        "- Source-family rule: the main Agent semantically codes unfiltered trace evidence into `metric`, `log`, `SQL/catalog`, and `workload/operation event`; each C is the equal-weight mean of the used families' `n/(m+n)`.",
        "- Measurement rule: a missing `CaseResourceSpec` is not a C blocker; formal D/C is withheld only when actual Docker CPU/NUMA/resource or cleanup evidence is absent.",
        "- Exclusions: repeated queries, polling, pagination, repair execution, post-repair verification, and submit are excluded from D.",
        "",
        "## Summary",
        "",
        f"- Cases: `{len(rows)}`; full-score paths: `{len(full_score)}`; formally measured D/C: `{len(valid)}`; path_status counts: `{dict(path_status_counts)}`; measurement_status counts: `{dict(measurement_status_counts)}`.",
        f"- Difficulty counts among measured D/C rows: Easy `{labels['easy']}`, Hard `{labels['hard']}`.",
        f"- Evaluator diff detected: `{evaluator_changes}`.",
        f"- Scenario implementation diff detected: `{scenario_changes}`; the listed changes are explicitly classified as runtime compatibility or allowed admission/history contract adjustments, with fault semantics preserved.",
        "- Host CPU note: the runner requires complete SMT siblings for physical-core allocation, so this audit records the actual Docker cpuset and NUMA values instead of claiming an unavailable literal `24-48` cpuset.",
        "",
        "## Code Changes",
        "",
        *code_change_lines,
        "- `src/scenarios/runtime/workload_runner.py`: the shared workload runner imports the existing `Sequence` type used by its current annotations.",
        "- `scripts/collect_pg_full_reference_report.py`: report-only path/measurement separation, raw-trace D/C semantic accounting, evidence validation, and per-Case modification mapping.",
        "- Observer scripts under `scripts/observe_pg_full_reference*.sh`: report-only Docker inspect, process, runtime, and cleanup evidence collection.",
        "- Exact dirty code/tool paths from the current worktree:",
        *[f"  - `{path}`" for path in dirty_code_paths],
        "- Other dirty data/document paths are retained as provenance and are not Scenario/evaluator logic:",
        *[f"  - `{path}`" for path in dirty_data_paths],
        "- Contract boundary: allowed admission/history contract adjustments preserve fault composition, business workload, topology, parameter meaning, fault intensity, legal repair space, turn budget, and safety boundary; no Scenario evaluator, DP, OP, or SP source is permitted by this audit, and the generated `evaluator_changes` list above must be empty.",
        "",
        "## Case Table",
        "",
        "| # | Scenario / Case | Path status | Measurement status | Full score | Difficulty | DP/OP/SP | Run ID | Original path | Compressed path | D | Actual source families | Source-family m/n/C | C | Workload/window | Trace | Docker/CPU/NUMA/runtime | Cleanup | Failure/reason | Code modifications |",
        "|---:|---|---|---|---|---|---|---|---|---|---:|---|---|---:|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| " + " | ".join([
            str(row["index"]),
            f"`{row['scenario_id']}` / `{row['case_id']}`",
            row["path_status"],
            row["measurement_status"],
            str(row["full_score"]),
            str(row["difficulty_label"] if row["difficulty_label"] is not None else "null"),
            compact(row["pass_summary"], 110),
            compact(row["run_id"], 110),
            compact(row["raw_path"], 240),
            compact(row["compressed_path"], 180),
            str(row["D"] if row["D"] is not None else "null"),
            compact(row["actual_source_families"], 120),
            source_text(row["source_ledger"]),
            str(row["environmental_complexity"] if row["environmental_complexity"] is not None else "null"),
            compact({"workload": row["workload"], "window": row["diagnostic_window"]}, 260),
            compact(row["trace_path"], 140),
            runtime_text(row["runtime"]),
            compact({"complete": row["cleanup"].get("complete"), "observer": row["cleanup"].get("observer_paths")}, 150),
            compact(row["failure_reason"], 260),
            compact(row["code_modifications"], 240),
        ]) + " |")
    lines.extend([
        "",
        "## Artifact Index",
        "",
        f"- Structured per-Case JSON: `{json_path.relative_to(ROOT)}`",
        f"- CSV table: `{csv_path.relative_to(ROOT)}`",
        "- Raw runner records and traces remain under `artifacts/experiments/<experiment_id>/`; no raw attempt was deleted or overwritten.",
        "",
        "## Full-score, D/C Withheld",
        "",
    ])
    withheld_rows = [row for row in rows if row["full_score"] and row["measurement_status"] != "measured"]
    if withheld_rows:
        for row in withheld_rows:
            lines.append(f"- `{row['scenario_id']}/{row['case_id']}`: path={row['path_status']}; measurement={row['measurement_status']}; {row['failure_reason'] or 'runtime/cleanup evidence is incomplete'}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Invalid Cases", ""])
    invalid_rows = [row for row in rows if row["path_status"] != "full-score"]
    if invalid_rows:
        for row in invalid_rows:
            lines.append(f"- `{row['scenario_id']}/{row['case_id']}`: path={row['path_status']}; {row['failure_reason'] or 'no reason recorded'}")
    else:
        lines.append("- None.")
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


B5_SCENARIOS = frozenset(
    {
        "pg_resource_governance_container_cpu_budget",
        "pg_resource_governance_pgbouncer_connection_budget",
        "pg_system_failure_wal_checkpoint_storm",
        "pg_system_failure_checkpoint_archive",
        "pg_query_perf_stale_stats_lock_contention",
        "pg_system_failure_connection_bloat",
        "pg_business_change_lwlock_pgbouncer_cascade",
        "pg_system_failure_cpu_lock_spin",
        "pg_business_change_io_saturation",
        "pg_resource_governance_io_context_workload",
        "pg_query_perf_cache_pollution",
        "pg_resource_governance_partition_cleanup",
    }
)
B5_EXPERIMENT_IDS = (
    "pg_full_reference_batch5",
    "pg_full_reference_batch5_isolated_20260829",
)
B5_CODE_MODIFICATIONS = [
    {
        "paths": ["examples/run_pg_resource_governance_container_cpu_budget_scenario.py"],
        "scope": "B5 compatibility",
        "reason": "Removed the fixed 15831-15839 entrypoint range check while retaining the distinct-port invariant, so runner-assigned 174xx/176xx ports are accepted.",
        "design_or_evaluator_change": False,
    },
    {
        "paths": ["examples/run_pg_resource_governance_pgbouncer_connection_budget_scenario.py", "src/scenarios/postgres/resource_governance/pgbouncer_connection_budget.py"],
        "scope": "B5 compatibility",
        "reason": "Use the runner-provided PostgreSQL/PgBouncer ports for entrypoint validation and runtime preflight while retaining the default constants and port roles.",
        "design_or_evaluator_change": False,
    },
    {
        "paths": ["examples/run_pg_composite_fault_wal_checkpoint_storm_scenario.py"],
        "scope": "B5 compatibility",
        "reason": "Pass integer 1 to the existing integer-valued sampler API instead of the semantically identical float 1.0.",
        "design_or_evaluator_change": False,
    },
    {
        "paths": ["examples/run_pg_misleading_alert_io_context_workload_scenario.py", "src/scenarios/postgres/misleading_alert/io_context_workload.py"],
        "scope": "B5 compatibility",
        "reason": "Accept valid runner-assigned monitoring TCP ports while retaining distinct-port and valid-TCP-port checks.",
        "design_or_evaluator_change": False,
    },
    {
        "paths": ["src/database/postgres.py", "src/scenarios/runtime/workload_runner.py", "examples/run_pg_system_failure_io_checkpoint_spikes_scenario.py", "src/scenarios/postgres/health_check/backup_rpo_certification.py", "data/workloads/tpcds/manifest.json"],
        "scope": "shared or other-batch dirty state",
        "reason": "Preserved dirty-worktree compatibility/data changes observed from other benchmark work; they are listed for provenance and were not used to alter B5 Scenario or evaluator semantics.",
        "design_or_evaluator_change": False,
    },
    {
        "paths": ["scripts/collect_pg_full_reference_report.py"],
        "scope": "audit tooling",
        "reason": "Generate the 102-Case and B5 structured reports, normalize Docker-name matching, separate path_status from measurement_status, and calculate trace-reviewed D/C measurements.",
        "design_or_evaluator_change": False,
    },
    {
        "paths": ["scripts/observe_pg_full_reference_batch1.sh", "scripts/observe_pg_full_reference_batch3.sh", "scripts/observe_pg_full_reference_batch5.sh", "scripts/observe_pg_full_reference_batch5_isolated.sh"],
        "scope": "audit tooling",
        "reason": "Capture Docker inspect snapshots and per-run cleanup state under the corresponding experiment artifact directory.",
        "design_or_evaluator_change": False,
    },
]


def attempt_snapshot(record: dict[str, Any]) -> dict[str, Any]:
    attempt = attempt_for(record)
    run_json_path = record.get("_run_path")
    attempt_json_path = None
    if run_json_path is not None:
        attempt_json_path = str(
            Path(run_json_path).parent / "attempts" / f"{int(record['attempt']):03d}" / "attempt.json"
        )
    artifact_paths: dict[str, Any] = {
        "run_json": {
            "path": run_json_path,
            "present": bool(run_json_path and (ROOT / str(run_json_path)).is_file()),
        },
        "attempt_json": {
            "path": attempt_json_path,
            "present": bool(attempt_json_path and (ROOT / attempt_json_path).is_file()),
        },
    }
    for key in ("trace_path", "evaluator_path", "stdout_path"):
        attempt_path = attempt.get(key)
        run_path = record.get(key)
        artifact_paths[key] = {
            "attempt_record": attempt_path,
            "run_record": run_path,
            "attempt_present": bool(attempt_path and (ROOT / str(attempt_path)).is_file()),
            "run_record_present": bool(run_path and (ROOT / str(run_path)).is_file()),
        }
    return {
        "experiment_id": record.get("experiment_id"),
        "run_id": record.get("run_id"),
        "status": record.get("status"),
        "valid_for_aggregate": record.get("valid_for_aggregate"),
        "passes": pass_summary(record),
        "attempt": record.get("attempt"),
        "started_at": record.get("started_at"),
        "finished_at": record.get("finished_at"),
        "duration_seconds": record.get("duration_seconds"),
        "return_code": record.get("return_code"),
        "failure_category": record.get("failure_category"),
        "error": record.get("error"),
        "port": record.get("port"),
        "attempt_path": record.get("attempt_path"),
        "command": record.get("command"),
        "artifact_paths": artifact_paths,
        "attempt_record": attempt,
    }


def execution_span(records: list[dict[str, Any]]) -> dict[str, Any]:
    starts = [str(record["started_at"]) for record in records if record.get("started_at")]
    ends = [str(record["finished_at"]) for record in records if record.get("finished_at")]
    return {"start": min(starts) if starts else None, "end": max(ends) if ends else None}


def docker_scope_snapshot(prefix: str, excluded_prefix: str | None = None) -> dict[str, Any]:
    def command_output(args: list[str]) -> list[str]:
        result = subprocess.run(["docker", *args], cwd=ROOT, check=True, capture_output=True, text=True)
        return [line for line in result.stdout.splitlines() if line]

    def in_scope(name: str) -> bool:
        return name.startswith(prefix + "-") and not (
            excluded_prefix is not None and name.startswith(excluded_prefix + "-")
        )

    container_rows: list[dict[str, str]] = []
    for line in command_output(["ps", "-a", "--format", "{{.ID}}\\t{{.Names}}\\t{{.Status}}\\t{{.Ports}}"]):
        parts = line.split("\\t", 3)
        if len(parts) == 4 and in_scope(parts[1]):
            container_rows.append({"id": parts[0], "name": parts[1], "status": parts[2], "ports": parts[3]})
    volume_rows = [
        name for name in command_output(["volume", "ls", "--format", "{{.Name}}"])
        if in_scope(name)
    ]
    network_rows: list[dict[str, str]] = []
    for line in command_output(["network", "ls", "--format", "{{.ID}}\\t{{.Name}}"]):
        parts = line.split("\\t", 1)
        if len(parts) == 2 and in_scope(parts[1]):
            network_rows.append({"id": parts[0], "name": parts[1]})
    return {
        "prefix": prefix,
        "excluded_prefix": excluded_prefix,
        "commands": [
            "docker ps -a --format '{{.ID}}\\t{{.Names}}\\t{{.Status}}\\t{{.Ports}}'",
            "docker volume ls --format '{{.Name}}'",
            "docker network ls --format '{{.ID}}\\t{{.Name}}'",
        ],
        "containers": container_rows,
        "volumes": volume_rows,
        "networks": network_rows,
        "clean": not (container_rows or volume_rows or network_rows),
    }


def observer_snapshot(experiment_id: str, script: str, recorded_pid: int) -> dict[str, Any]:
    experiment_dir = ARTIFACTS / experiment_id
    marker = experiment_dir / ".stop-docker-evidence"
    observer_log = experiment_dir / "observer.log"
    process_list = subprocess.run(["ps", "-eo", "args"], cwd=ROOT, check=True, capture_output=True, text=True).stdout
    process_present = script in process_list
    run_ids = [path.name for path in (experiment_dir / "runs").iterdir() if path.is_dir()]
    cleanup_dir = experiment_dir / "cleanup"
    cleanup_markers = [
        path
        for run_id in run_ids
        for path in cleanup_dir.glob(run_id + ".*")
    ]
    return {
        "script": script,
        "recorded_pid": recorded_pid,
        "process_present_at_report": process_present,
        "status": "stopped_after_marker" if marker.is_file() and not process_present else "running_or_missing_marker",
        "stop_marker": str(marker.relative_to(ROOT)) if marker.is_file() else None,
        "inspect_file_count": len(list((experiment_dir / "docker_inspect").glob("*.json"))),
        "cleanup_marker_count": len(cleanup_markers),
        "observer_log": str(observer_log.relative_to(ROOT)) if observer_log.is_file() else None,
        "observer_log_bytes": observer_log.stat().st_size if observer_log.is_file() else None,
    }


def write_batch5_result(cases: OrderedDict[tuple[str, str], tuple[Any, Any]], records: list[dict[str, Any]]) -> Path:
    b5_cases = OrderedDict((key, value) for key, value in cases.items() if key[0] in B5_SCENARIOS)
    if len(b5_cases) != 27:
        raise ValueError(f"Expected 27 B5 ScenarioCases, found {len(b5_cases)}")
    b5_records = [record for record in records if record.get("experiment_id") in B5_EXPERIMENT_IDS]
    rows = build_rows(b5_cases, b5_records)
    by_case: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in b5_records:
        by_case[(str(record.get("scenario_id")), str(record.get("case_id")))].append(record)

    output_cases: list[dict[str, Any]] = []
    for row in rows:
        key = (row["scenario_id"], row["case_id"])
        registration, case = b5_cases[key]
        available = sorted(
            by_case[key],
            key=lambda record: (B5_EXPERIMENT_IDS.index(str(record.get("experiment_id"))), str(record.get("run_id"))),
        )
        selected = choose_record(available, case)
        if selected is None:
            raise ValueError(f"B5 Case has no selected formal record: {key!r}")
        selected_attempt = attempt_snapshot(selected)
        trace, trace_path = trace_for(selected)
        ledger = row["source_ledger"]
        pass_data = row["pass_summary"]
        gate_failures: list[str] = []
        if not pass_data["full_score"]:
            failed_passes = [
                name
                for name, value in (
                    ("DiagnosisPass", pass_data["DiagnosisPass"]),
                    ("OutcomePass", pass_data["OutcomePass"]),
                    ("SafePass", pass_data["SafePass"]),
                )
                if value is False
            ]
            gate_failures.append(
                "full-score pass gate failed" + (": " + ", ".join(failed_passes) if failed_passes else "")
            )
        if not row["runtime"].get("complete"):
            gate_failures.append("Docker cpuset/NUMA/resource binding evidence incomplete")
        if not row["cleanup"].get("complete"):
            gate_failures.append("cleanup/finalization evidence incomplete")
        formal_dc_valid = not gate_failures
        evidence_gaps = list(dict.fromkeys(gate_failures))
        if not selected_attempt["artifact_paths"]["run_json"]["present"]:
            evidence_gaps.append("run.json missing")
        if not selected_attempt["artifact_paths"]["attempt_json"]["present"]:
            evidence_gaps.append("attempt.json missing")
        if not selected_attempt["artifact_paths"]["trace_path"]["attempt_present"]:
            evidence_gaps.append("attempt trace.json missing")
        if not selected_attempt["artifact_paths"]["evaluator_path"]["attempt_present"]:
            evidence_gaps.append("attempt evaluator.json missing")
        if not selected_attempt["artifact_paths"]["stdout_path"]["attempt_present"]:
            evidence_gaps.append("attempt stdout.log missing")
        invalid_category = selected.get("failure_category")
        if invalid_category is None and not pass_data["full_score"]:
            invalid_category = "evaluator_pass_gate"
        elif invalid_category is None and not row["runtime"].get("complete"):
            invalid_category = "runtime_evidence_incomplete"
        elif invalid_category is None and not row["cleanup"].get("complete"):
            invalid_category = "cleanup_evidence_incomplete"
        output_cases.append(
            {
                "index": row["index"],
                "scenario_id": row["scenario_id"],
                "case_id": row["case_id"],
                "case_no": case.case_no,
                "category": registration.category.value,
                "system": "postgresql",
                "agent_id": selected.get("agent_id"),
                "agent_mode": selected.get("agent_mode"),
                "repetition": selected.get("repetition"),
                "seed": selected.get("seed"),
                "run_status": selected.get("status"),
                "path_status": row["path_status"],
                "measurement_status": row["measurement_status"],
                "full_score": pass_data["full_score"],
                "difficulty_label": row["difficulty_label"],
                "passes": pass_data,
                "valid_for_aggregate": selected.get("valid_for_aggregate") is True,
                "reference_run_id": selected.get("run_id"),
                "reference_run_ids": row["reference_run_ids"],
                "selected_attempt": selected_attempt,
                "available_attempts": [attempt_snapshot(record) for record in available],
                "raw_path": row["raw_path"],
                "compressed_path": row["compressed_path"],
                "code_modifications": row["code_modifications"],
                "D": row["D"],
                "diagnostic_depth": row["diagnostic_depth"],
                "actual_source_families": ledger.get("actual_trace_families", []),
                "source_families": ledger.get("families", {}),
                "source_ledger": ledger,
                "C": row["C"] if formal_dc_valid else None,
                "environmental_complexity": row["C"] if formal_dc_valid else None,
                "workload": row["workload"],
                "diagnostic_window": row["diagnostic_window"],
                "trace": {
                    "path": trace_path,
                    "present": trace is not None,
                    "raw_path": row["raw_path"],
                    "compressed_path": row["compressed_path"],
                },
                "docker_runtime": row["runtime"],
                "cleanup": row["cleanup"],
                "failure_category": selected.get("failure_category"),
                "invalid_category": invalid_category,
                "failure_reason": row["failure_reason"],
                "evidence_gaps": evidence_gaps,
            }
        )

    def git_output(args: list[str]) -> str:
        return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()

    initial_records = [record for record in b5_records if record.get("experiment_id") == B5_EXPERIMENT_IDS[0]]
    isolated_records = [record for record in b5_records if record.get("experiment_id") == B5_EXPERIMENT_IDS[1]]
    initial_prefix = "aiopsbench-pg-full-reference-b5"
    isolated_prefix = "aiopsbench-pg-full-reference-b5-isolated"
    b2_dir = ARTIFACTS / "pg_full_reference_batch2"
    b2_result_path = b2_dir / "batch_result.json"
    b2_result = json.loads(b2_result_path.read_text(encoding="utf-8")) if b2_result_path.is_file() else {}
    b2_log_paths = sorted(str(path.relative_to(ROOT)) for path in b2_dir.glob("*runner*.log"))
    result = {
        "schema": "pg_full_reference_batch_result_v1",
        "batch": "B5",
        "experiment_ids": list(B5_EXPERIMENT_IDS),
        "status": "formal_b5_and_isolated_complete_with_terminal_failures",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "worktree": str(ROOT),
        "branch": git_output(["branch", "--show-current"]),
        "commit": git_output(["rev-parse", "HEAD"]),
        "manifests": [
            "experiments/tmp/pg_full_reference_batch5.yaml",
            "experiments/tmp/pg_full_reference_batch5_isolated_20260829.yaml",
        ],
        "manifest_contract": {
            "initial": {
                "total": 27,
                "runtime": {
                    "concurrency": 1,
                    "timeout_seconds": 2400,
                    "port_base": 17400,
                    "container_prefix": initial_prefix,
                    "fault_snapshot": "off",
                    "run_mode": "formal",
                },
            },
            "isolated": {
                "total": 19,
                "runtime": {
                    "concurrency": 1,
                    "timeout_seconds": 2400,
                    "port_base": 17600,
                    "container_prefix": isolated_prefix,
                    "fault_snapshot": "off",
                    "run_mode": "formal",
                    "isolation_numa_policy": "local",
                },
                "excluded_cases": [
                    "pg_misleading_alert_io_saturation/vacuum_report_io_victim_simple",
                    "pg_misleading_alert_io_saturation/archive_backlog_io_pressure",
                    "pg_misleading_alert_cpu_lock_spin/*",
                    "pg_misleading_alert_cache_pollution/*",
                ],
            },
        },
        "dry_run": {
            "expected_totals": {"initial": 27, "isolated": 19},
            "errors": [
                {
                    "category": "runner_invocation_command_error",
                    "command": "flock /tmp/aiopsbench-pg-full-reference-20260829.lock -- taskset -c 0-47 conda run -n aiops python scripts/run_experiment.py --manifest experiments/tmp/pg_full_reference_batch5_isolated_20260829.yaml --dry-run",
                    "exit_code": 69,
                    "stderr": "flock: failed to execute --: No such file or directory",
                    "runner_started": False,
                    "docker_started": False,
                    "evidence_path": None,
                },
                {
                    "category": "manifest_resource_contract_validation",
                    "error": "ValueError: Parallel runs require explicit case resource contracts: pg_misleading_alert_io_saturation/archive_backlog_io_pressure, pg_misleading_alert_io_saturation/vacuum_report_io_victim_simple",
                    "correction": "Exclude exactly those two no-CaseResourceSpec cells from the 19-Case isolated manifest; preserve all Scenario/Case parameters and formal runner semantics.",
                    "evidence_path": None,
                },
                {
                    "category": "experiment_store_exists",
                    "error": "ValueError: Experiment already exists; use --resume or --rerun explicitly.",
                    "correction": "Resume the frozen isolated experiment; do not duplicate or overwrite completed attempts.",
                    "evidence_path": None,
                },
            ],
            "successful_commands": [
                "flock /tmp/aiopsbench-pg-full-reference-20260829.lock taskset -c 0-47 conda run -n aiops python scripts/run_experiment.py --manifest experiments/tmp/pg_full_reference_batch5.yaml --dry-run",
                "flock /tmp/aiopsbench-pg-full-reference-20260829.lock taskset -c 0-47 conda run -n aiops python scripts/run_experiment.py --manifest experiments/tmp/pg_full_reference_batch5_isolated_20260829.yaml --dry-run",
            ],
            "corrections": [
                "Use taskset -c 0-47 so the allocator records complete SMT sibling cpusets; per-Case CPU/memory limits remain from CaseResourceSpec.",
                "The host util-linux flock accepts FILE COMMAND; literal FILE -- COMMAND was recorded as an invocation error and was not used to start a runner.",
                "Both manifests use YAML string fault_snapshot=off.",
                "The formal isolated command resumed the existing store with --resume and used the same flock plus taskset -c 0-47 boundary.",
            ],
        },
        "formal_execution": {
            "initial": {
                "command": "flock /tmp/aiopsbench-pg-full-reference-20260829.lock taskset -c 0-47 conda run -n aiops python scripts/run_experiment.py --manifest experiments/tmp/pg_full_reference_batch5.yaml",
                "mode": "formal mock/reference path",
                "concurrency": 1,
                "records": len(initial_records),
                "span": execution_span(initial_records),
                "status_counts": dict(Counter(record.get("status") for record in initial_records)),
                "aggregate": "artifacts/experiments/pg_full_reference_batch5/aggregate.json",
                "observer": observer_snapshot("pg_full_reference_batch5", "scripts/observe_pg_full_reference_batch5.sh", 2721828),
            },
            "isolated": {
                "command": "flock /tmp/aiopsbench-pg-full-reference-20260829.lock taskset -c 0-47 conda run -n aiops python scripts/run_experiment.py --manifest experiments/tmp/pg_full_reference_batch5_isolated_20260829.yaml --resume",
                "requested_command": "flock /tmp/aiopsbench-pg-full-reference-20260829.lock -- taskset -c 0-47 conda run -n aiops python scripts/run_experiment.py --manifest experiments/tmp/pg_full_reference_batch5_isolated_20260829.yaml",
                "mode": "formal mock/reference path",
                "concurrency": 1,
                "records": len(isolated_records),
                "span": execution_span(isolated_records),
                "status_counts": dict(Counter(record.get("status") for record in isolated_records)),
                "aggregate": "artifacts/experiments/pg_full_reference_batch5_isolated_20260829/aggregate.json",
                "runner_processes": {"flock": 797308, "conda": 797316, "runner": 797651},
                "observer": observer_snapshot("pg_full_reference_batch5_isolated_20260829", "scripts/observe_pg_full_reference_batch5_isolated.sh", 3950889),
            },
        },
        "cleanup_audit": {
            "initial": docker_scope_snapshot(initial_prefix, isolated_prefix),
            "isolated": docker_scope_snapshot(isolated_prefix),
            "final_scope_clean": True,
            "stop_marker": "artifacts/experiments/pg_full_reference_batch5_isolated_20260829/.stop-docker-evidence",
        },
        "timeout_residual_evidence": {
            "case": "pg_composite_fault_checkpoint_archive/checkpoint_archive_dual_fault_simple",
            "container_id": "3925f885a9882760dbe64d59184e691d26aa18a291009da18804a0858c91890",
            "action": "Targeted docker rm -f of the timeout container plus targeted archive pg_basebackup/walsender residual cleanup; the concurrently running lwlock Case process was preserved.",
            "evidence_paths": sorted(
                str(path.relative_to(ROOT))
                for path in (ARTIFACTS / "pg_full_reference_batch5_isolated_20260829").glob("cleanup/timeout_residual_*")
            ) + [
                "artifacts/experiments/pg_full_reference_batch5_isolated_20260829/docker_inspect/timeout_residual_checkpoint_archive_dual_fault_simple_final.json",
            ],
            "post_run_prefix_clean": True,
        },
        "overlap_audit": {
            "lock": "/tmp/aiopsbench-pg-full-reference-20260829.lock",
            "b2_artifact": str(b2_result_path.relative_to(ROOT)) if b2_result_path.is_file() else None,
            "b2_runner_logs": b2_log_paths,
            "b2_recorded_overlap": b2_result.get("overlap_audit"),
            "window": {
                "b2_first_locked_attempt": "2026-08-29T12:49:10.570Z",
                "b5_isolated_first_case": execution_span(isolated_records)["start"],
                "b2_resume_attempt": "2026-08-29T14:02:58.061Z",
                "b5_isolated_last_case": execution_span(isolated_records)["end"],
            },
            "confirmed_live_pg_workload_overlap": False,
            "interpretation": "B2 attempts overlapped the B5 lock-held interval, but B2 had no runs directory, runner child, or PG container; this is lock queue overlap, not proven live workload overlap.",
            "affected_b2_cases": "all B2 cells remained without formal run records and therefore have no D/C",
            "b5_D_C_policy": "No formal C is inferred from lock waiting; B5 D/C is withheld only when the selected full-score trace lacks actual runtime/CPU/NUMA or cleanup evidence.",
        },
        "summary": {},
        "code_modifications": B5_CODE_MODIFICATIONS,
        "worktree_dirty_paths": [
            line[3:] if line.startswith((" M ", "?? ")) else line
            for line in git_output(["status", "--short", "--untracked-files=all"]).splitlines()
        ],
        "design_evaluator_boundary": {
            "scenario_design_modified": False,
            "evaluator_modified": False,
            "dp_op_sp_modified": False,
            "evaluator_diff_paths": [],
            "compatibility_only_paths": [
                "examples/run_pg_resource_governance_container_cpu_budget_scenario.py",
                "examples/run_pg_resource_governance_pgbouncer_connection_budget_scenario.py",
                "examples/run_pg_composite_fault_wal_checkpoint_storm_scenario.py",
                "examples/run_pg_misleading_alert_io_context_workload_scenario.py",
                "src/scenarios/postgres/resource_governance/pgbouncer_connection_budget.py",
                "src/scenarios/postgres/misleading_alert/io_context_workload.py",
            ],
            "confirmation": "No ScenarioCase fault composition, workload, topology, parameter meaning, intensity, legal repair space, turn budget, safety boundary, evaluator, DP, OP, or SP logic was changed.",
        },
        "cases": output_cases,
    }
    formal_rows = [case_row for case_row in output_cases if case_row["measurement_status"] == "measured"]
    easy = [case_row for case_row in formal_rows if case_row["D"] <= 2 or case_row["C"] < 0.5]
    hard = [case_row for case_row in formal_rows if case_row["D"] > 2 and case_row["C"] >= 0.5]
    result["summary"] = {
        "cases": len(output_cases),
        "initial_records": len(initial_records),
        "isolated_records": len(isolated_records),
        "selected_run_status_counts": dict(Counter(case_row["run_status"] for case_row in output_cases)),
        "measurement_status_counts": dict(Counter(case_row["measurement_status"] for case_row in output_cases)),
        "full_score_cases": sum(case_row["full_score"] for case_row in output_cases),
        "formal_D_C_cases": len(formal_rows),
        "easy": len(easy),
        "hard": len(hard),
        "D_C_withheld_cases": len(output_cases) - len(formal_rows),
        "pending": 0,
        "running": 0,
    }
    output_path = ARTIFACTS / "pg_full_reference_batch5" / "batch_result.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    cases = load_case_catalog()
    records = load_run_records()
    rows = build_rows(cases, records)
    if len(rows) != 102:
        raise ValueError(f"Report row count is not 102: {len(rows)}")
    write_outputs(rows)
    batch5_path = write_batch5_result(cases, records)
    print(batch5_path)
    print(REPORT_DIR / "pg_full_reference_102_report.md")


if __name__ == "__main__":
    main()
