import threading

import time

from collections.abc import Mapping

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    connect_tidb,
    join_thread,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.system_failure.mdl_blocking import (
    TidbSystemFailureMdlBlockingEvaluatorCase,
    TidbSystemFailureMdlBlockingFocusedEvaluatorCase,
)
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from ..runtime import TIDB_V8_1_0, tidb_runtime


def _mdl_blocking_workload(
    table: str,
    guard_table: str,
    customers: str,
    payments: str,
    shipments: str,
    reservations: str,
    events: str,
) -> BackgroundWorkloadSpec:
    profiles = (
        WorkloadProfile(
            name="mdl_orders_api_point_read",
            sql=(
                f"SELECT id, customer_id, order_status, order_total, payload "
                f"FROM {table} WHERE id = 1"
            ),
            qps=0.95,
            tier="OLTP",
            application_name="orders-api",
        ),
        WorkloadProfile(
            name="mdl_customer_order_history",
            sql=(
                f"SELECT id, order_status, order_total, created_at FROM {table} "
                "WHERE customer_id = 1007 ORDER BY created_at DESC, id DESC LIMIT 20"
            ),
            qps=0.55,
            tier="OLTP",
            application_name="customer-order-history",
        ),
        WorkloadProfile(
            name="mdl_order_status_summary",
            sql=(
                f"SELECT order_status, COUNT(*), COALESCE(SUM(order_total), 0) FROM {table} "
                "WHERE created_at >= '2026-07-01 00:00:00' "
                "GROUP BY order_status ORDER BY order_status"
            ),
            qps=0.4,
            tier="REPORTING",
            application_name="order-status-dashboard",
        ),
        WorkloadProfile(
            name="mdl_customer_revenue_rollup",
            sql=(
                f"SELECT customer_id, COUNT(*) AS orders, COALESCE(SUM(order_total), 0) AS gross "
                f"FROM {table} GROUP BY customer_id ORDER BY gross DESC, customer_id LIMIT 12"
            ),
            qps=0.35,
            tier="REPORTING",
            application_name="customer-revenue-dashboard",
        ),
        WorkloadProfile(
            name="mdl_fulfillment_queue",
            sql=(
                f"SELECT id, customer_id, order_total FROM {table} "
                "WHERE order_status IN ('PAID', 'SHIPPED') AND id > 16 "
                "ORDER BY created_at, id LIMIT 16"
            ),
            qps=0.5,
            tier="OLTP",
            application_name="fulfillment-queue",
        ),
        WorkloadProfile(
            name="mdl_order_prefix_search",
            sql=(
                f"SELECT id, customer_id, order_status FROM {table} "
                "WHERE payload LIKE 'order-payload-0%' ORDER BY id LIMIT 20"
            ),
            qps=0.45,
            tier="OLTP",
            application_name="order-search-api",
        ),
        WorkloadProfile(
            name="mdl_recent_order_feed",
            sql=(
                f"SELECT id, order_status, order_total FROM {table} "
                "WHERE created_at >= '2026-07-15 00:00:00' "
                "ORDER BY created_at DESC, id DESC LIMIT 24"
            ),
            qps=0.4,
            tier="OLTP",
            application_name="recent-orders-feed",
        ),
        WorkloadProfile(
            name="mdl_customer_segment_export",
            sql=(
                f"SELECT customer_id, order_status, COUNT(*) AS orders, "
                f"COALESCE(SUM(order_total), 0) AS gross FROM {table} "
                "WHERE customer_id BETWEEN 1000 AND 1012 "
                "GROUP BY customer_id, order_status ORDER BY customer_id, order_status"
            ),
            qps=0.3,
            tier="REPORTING",
            application_name="customer-segment-export",
        ),
        WorkloadProfile(
            name="mdl_order_detail_batch",
            sql=(
                f"SELECT id, payload, order_status, order_total FROM {table} "
                "WHERE id BETWEEN 32 AND 96 ORDER BY created_at DESC, id DESC LIMIT 20"
            ),
            qps=0.35,
            tier="OLTP",
            application_name="order-detail-service",
        ),
        WorkloadProfile(
            name="mdl_reconciliation_signature",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(id), 0), "
                f"BIT_XOR(CRC32(CONCAT(id, ':', payload))) FROM {table}"
            ),
            qps=0.3,
            tier="AUDIT",
            application_name="order-reconciliation",
        ),
        WorkloadProfile(
            name="mdl_order_api_short_update",
            sql=f"UPDATE {table} SET order_status = order_status WHERE id = 17",
            qps=0.35,
            tier="OLTP_WRITE",
            application_name="orders-api-write-path",
        ),
        WorkloadProfile(
            name="mdl_guard_session_read",
            sql=f"SELECT id, payload FROM {guard_table} WHERE id = 1",
            qps=0.6,
            tier="OLTP",
            application_name="release-health-check",
        ),
        WorkloadProfile(
            name="mdl_guard_health_summary",
            sql=(
                f"SELECT COUNT(*), COALESCE(SUM(id), 0) FROM {guard_table} "
                "WHERE payload LIKE 'unrelated-%'"
            ),
            qps=0.35,
            tier="AUDIT",
            application_name="release-health-audit",
        ),
        WorkloadProfile(
            name="mdl_checkout_order_summary",
            sql=(
                f"SELECT o.id, c.customer_segment, p.payment_status, s.shipment_status, "
                f"o.order_total FROM {table} AS o "
                f"JOIN {customers} AS c ON c.customer_id = o.customer_id "
                f"LEFT JOIN {payments} AS p ON p.order_id = o.id "
                f"LEFT JOIN {shipments} AS s ON s.order_id = o.id "
                "WHERE o.id = 17"
            ),
            qps=0.34,
            tier="OLTP_JOIN",
            application_name="checkout-order-service",
        ),
        WorkloadProfile(
            name="mdl_customer_profile_lookup",
            sql=(
                f"SELECT c.customer_id, c.customer_segment, c.region, c.loyalty_tier, "
                f"COUNT(o.id) AS order_count, COALESCE(SUM(o.order_total), 0) AS lifetime_value "
                f"FROM {customers} AS c LEFT JOIN {table} AS o ON o.customer_id = c.customer_id "
                "WHERE c.customer_id = 1007 GROUP BY c.customer_id, c.customer_segment, c.region, c.loyalty_tier"
            ),
            qps=0.28,
            tier="OLTP_JOIN",
            application_name="customer-profile-service",
        ),
        WorkloadProfile(
            name="mdl_payment_authorization_queue",
            sql=(
                f"SELECT p.payment_id, p.order_id, p.gateway, p.amount FROM {payments} AS p "
                "WHERE p.payment_status IN ('AUTHORIZED', 'RETRY') "
                "ORDER BY p.paid_at, p.payment_id LIMIT 24"
            ),
            qps=0.32,
            tier="OLTP",
            application_name="payment-authorizer",
        ),
        WorkloadProfile(
            name="mdl_gateway_reconciliation",
            sql=(
                f"SELECT p.gateway, p.payment_status, COUNT(*) AS payments, COALESCE(SUM(p.amount), 0) AS amount "
                f"FROM {payments} AS p GROUP BY p.gateway, p.payment_status "
                "ORDER BY p.gateway, p.payment_status"
            ),
            qps=0.22,
            tier="RECONCILIATION",
            application_name="payment-reconciliation",
        ),
        WorkloadProfile(
            name="mdl_shipment_tracking_lookup",
            sql=(
                f"SELECT s.order_id, s.carrier, s.shipment_status, s.promised_at, s.delivered_at "
                f"FROM {shipments} AS s WHERE s.order_id = 17"
            ),
            qps=0.36,
            tier="OLTP",
            application_name="shipment-tracking-api",
        ),
        WorkloadProfile(
            name="mdl_dispatch_sla_dashboard",
            sql=(
                f"SELECT s.carrier, s.shipment_status, COUNT(*) AS shipments, "
                f"SUM(CASE WHEN s.delivered_at > s.promised_at THEN 1 ELSE 0 END) AS late "
                f"FROM {shipments} AS s GROUP BY s.carrier, s.shipment_status "
                "ORDER BY late DESC, s.carrier"
            ),
            qps=0.24,
            tier="REPORTING",
            application_name="dispatch-sla-dashboard",
        ),
        WorkloadProfile(
            name="mdl_inventory_reservation_queue",
            sql=(
                f"SELECT r.reservation_id, r.order_id, r.sku, r.quantity FROM {reservations} AS r "
                "WHERE r.reservation_status IN ('HELD', 'RETRY') "
                "ORDER BY r.expires_at, r.reservation_id LIMIT 32"
            ),
            qps=0.34,
            tier="OLTP",
            application_name="inventory-reservation-service",
        ),
        WorkloadProfile(
            name="mdl_inventory_expiry_sweep",
            sql=(
                f"SELECT r.sku, COUNT(*) AS reservations, COALESCE(SUM(r.quantity), 0) AS units "
                f"FROM {reservations} AS r WHERE r.expires_at < '2026-08-01 00:00:00' "
                "AND r.reservation_status = 'HELD' GROUP BY r.sku ORDER BY units DESC, r.sku"
            ),
            qps=0.2,
            tier="BACKGROUND",
            application_name="inventory-expiry-worker",
        ),
        WorkloadProfile(
            name="mdl_order_event_timeline",
            sql=(
                f"SELECT e.event_type, e.event_at, e.actor, e.payload FROM {events} AS e "
                "WHERE e.order_id = 17 ORDER BY e.event_at, e.event_id"
            ),
            qps=0.3,
            tier="OLTP_JOIN",
            application_name="order-timeline-api",
        ),
        WorkloadProfile(
            name="mdl_customer_activity_feed",
            sql=(
                f"SELECT o.id, o.order_status, e.event_type, e.event_at FROM {table} AS o "
                f"JOIN {events} AS e ON e.order_id = o.id WHERE o.customer_id = 1007 "
                "ORDER BY e.event_at DESC, e.event_id DESC LIMIT 30"
            ),
            qps=0.26,
            tier="OLTP_JOIN",
            application_name="customer-activity-feed",
        ),
        WorkloadProfile(
            name="mdl_risk_review_queue",
            sql=(
                f"SELECT o.id, c.customer_segment, o.order_total, p.gateway FROM {table} AS o "
                f"JOIN {customers} AS c ON c.customer_id = o.customer_id "
                f"JOIN {payments} AS p ON p.order_id = o.id "
                "WHERE c.loyalty_tier = 'REVIEW' OR p.payment_status = 'RETRY' "
                "ORDER BY o.created_at, o.id LIMIT 20"
            ),
            qps=0.24,
            tier="OLTP_JOIN",
            application_name="risk-review-queue",
        ),
        WorkloadProfile(
            name="mdl_daily_revenue_by_region",
            sql=(
                f"SELECT c.region, DATE(o.created_at) AS order_day, COUNT(*) AS orders, "
                f"COALESCE(SUM(o.order_total), 0) AS revenue FROM {table} AS o "
                f"JOIN {customers} AS c ON c.customer_id = o.customer_id "
                "GROUP BY c.region, DATE(o.created_at) ORDER BY order_day, c.region"
            ),
            qps=0.18,
            tier="REPORTING",
            application_name="regional-revenue-report",
        ),
        WorkloadProfile(
            name="mdl_payment_status_rollup",
            sql=(
                f"SELECT DATE(p.paid_at) AS paid_day, p.payment_status, COUNT(*) AS payments, "
                f"COALESCE(SUM(p.amount), 0) AS amount FROM {payments} AS p "
                "GROUP BY DATE(p.paid_at), p.payment_status ORDER BY paid_day, p.payment_status"
            ),
            qps=0.2,
            tier="REPORTING",
            application_name="payment-status-report",
        ),
        WorkloadProfile(
            name="mdl_carrier_performance",
            sql=(
                f"SELECT s.carrier, COUNT(*) AS shipped, "
                f"AVG(TIMESTAMPDIFF(HOUR, s.promised_at, s.delivered_at)) AS delivery_hours "
                f"FROM {shipments} AS s WHERE s.shipment_status = 'DELIVERED' "
                "GROUP BY s.carrier ORDER BY shipped DESC, s.carrier"
            ),
            qps=0.18,
            tier="REPORTING",
            application_name="carrier-performance-report",
        ),
        WorkloadProfile(
            name="mdl_order_fulfillment_join",
            sql=(
                f"SELECT o.id, o.order_status, p.payment_status, s.shipment_status, "
                f"COUNT(r.reservation_id) AS reservation_lines FROM {table} AS o "
                f"LEFT JOIN {payments} AS p ON p.order_id = o.id "
                f"LEFT JOIN {shipments} AS s ON s.order_id = o.id "
                f"LEFT JOIN {reservations} AS r ON r.order_id = o.id "
                "WHERE o.id BETWEEN 32 AND 96 GROUP BY o.id, o.order_status, p.payment_status, s.shipment_status "
                "ORDER BY o.id LIMIT 32"
            ),
            qps=0.23,
            tier="OLTP_JOIN",
            application_name="fulfillment-detail-service",
        ),
        WorkloadProfile(
            name="mdl_customer_value_report",
            sql=(
                f"SELECT c.customer_id, c.region, COUNT(DISTINCT o.id) AS orders, "
                f"COALESCE(SUM(o.order_total), 0) AS gross, COUNT(DISTINCT e.event_id) AS events "
                f"FROM {customers} AS c LEFT JOIN {table} AS o ON o.customer_id = c.customer_id "
                f"LEFT JOIN {events} AS e ON e.order_id = o.id "
                "GROUP BY c.customer_id, c.region ORDER BY gross DESC, c.customer_id LIMIT 20"
            ),
            qps=0.16,
            tier="REPORTING",
            application_name="customer-value-report",
        ),
        WorkloadProfile(
            name="mdl_release_batch_export",
            sql=(
                f"SELECT o.id, c.region, p.payment_status, s.shipment_status, "
                f"r.reservation_status FROM {table} AS o "
                f"JOIN {customers} AS c ON c.customer_id = o.customer_id "
                f"LEFT JOIN {payments} AS p ON p.order_id = o.id "
                f"LEFT JOIN {shipments} AS s ON s.order_id = o.id "
                f"LEFT JOIN {reservations} AS r ON r.order_id = o.id "
                "WHERE o.id > 64 ORDER BY o.id LIMIT 32"
            ),
            qps=0.2,
            tier="BATCH",
            application_name="release-batch-export",
        ),
        WorkloadProfile(
            name="mdl_order_state_transition_audit",
            sql=(
                f"SELECT o.id, o.order_status, COUNT(e.event_id) AS transition_count "
                f"FROM {table} AS o JOIN {events} AS e ON e.order_id = o.id "
                "WHERE e.event_type IN ('STATUS_CHANGED', 'FULFILLMENT') "
                "GROUP BY o.id, o.order_status ORDER BY transition_count DESC, o.id LIMIT 24"
            ),
            qps=0.2,
            tier="AUDIT",
            application_name="order-transition-audit",
        ),
        WorkloadProfile(
            name="mdl_pending_order_alert",
            sql=(
                f"SELECT o.id, o.customer_id, o.order_total, p.payment_status FROM {table} AS o "
                f"JOIN {payments} AS p ON p.order_id = o.id "
                "WHERE o.order_status = 'PENDING' AND p.payment_status <> 'CAPTURED' "
                "ORDER BY o.created_at, o.id LIMIT 20"
            ),
            qps=0.28,
            tier="OLTP_JOIN",
            application_name="pending-order-alert",
        ),
        WorkloadProfile(
            name="mdl_inventory_sku_demand",
            sql=(
                f"SELECT r.sku, COUNT(DISTINCT r.order_id) AS orders, SUM(r.quantity) AS units, "
                f"COUNT(DISTINCT o.customer_id) AS customers FROM {reservations} AS r "
                f"JOIN {table} AS o ON o.id = r.order_id "
                "GROUP BY r.sku ORDER BY units DESC, r.sku LIMIT 24"
            ),
            qps=0.18,
            tier="REPORTING",
            application_name="inventory-demand-report",
        ),
        WorkloadProfile(
            name="mdl_gateway_error_rate",
            sql=(
                f"SELECT p.gateway, COUNT(*) AS attempts, "
                f"SUM(CASE WHEN p.payment_status IN ('FAILED', 'RETRY') THEN 1 ELSE 0 END) AS errors "
                f"FROM {payments} AS p GROUP BY p.gateway ORDER BY errors DESC, p.gateway"
            ),
            qps=0.22,
            tier="MONITOR",
            application_name="gateway-health-monitor",
        ),
        WorkloadProfile(
            name="mdl_customer_segment_summary",
            sql=(
                f"SELECT c.customer_segment, c.region, COUNT(DISTINCT c.customer_id) AS customers, "
                f"COUNT(o.id) AS orders, COALESCE(SUM(o.order_total), 0) AS revenue "
                f"FROM {customers} AS c LEFT JOIN {table} AS o ON o.customer_id = c.customer_id "
                "GROUP BY c.customer_segment, c.region ORDER BY revenue DESC, c.customer_segment"
            ),
            qps=0.18,
            tier="REPORTING",
            application_name="customer-segment-report",
        ),
        WorkloadProfile(
            name="mdl_recent_event_search",
            sql=(
                f"SELECT e.event_id, e.order_id, e.event_type, e.actor FROM {events} AS e "
                "WHERE e.event_at >= '2026-07-15 00:00:00' "
                "ORDER BY e.event_at DESC, e.event_id DESC LIMIT 40"
            ),
            qps=0.32,
            tier="OLTP",
            application_name="event-search-api",
        ),
        WorkloadProfile(
            name="mdl_delivery_late_orders",
            sql=(
                f"SELECT o.id, o.customer_id, s.carrier, s.promised_at, s.delivered_at FROM {table} AS o "
                f"JOIN {shipments} AS s ON s.order_id = o.id "
                "WHERE s.delivered_at > s.promised_at ORDER BY s.delivered_at DESC LIMIT 24"
            ),
            qps=0.2,
            tier="OLTP_JOIN",
            application_name="delivery-exception-service",
        ),
        WorkloadProfile(
            name="mdl_order_payment_detail",
            sql=(
                f"SELECT o.id, o.order_status, o.order_total, p.payment_status, p.gateway, p.amount "
                f"FROM {table} AS o JOIN {payments} AS p ON p.order_id = o.id "
                "WHERE o.id IN (17, 32, 64, 96) ORDER BY o.id"
            ),
            qps=0.28,
            tier="OLTP_JOIN",
            application_name="order-payment-detail",
        ),
        WorkloadProfile(
            name="mdl_order_api_short_update",
            sql=f"UPDATE {table} SET order_status = order_status WHERE id = 17",
            qps=0.35,
            tier="OLTP_WRITE",
            application_name="orders-api-write-path",
        ),
        WorkloadProfile(
            name="mdl_payment_retry_probe",
            sql=f"UPDATE {payments} SET payment_status = payment_status WHERE payment_id = 17",
            qps=0.24,
            tier="OLTP_WRITE",
            application_name="payment-retry-worker",
        ),
        WorkloadProfile(
            name="mdl_reservation_heartbeat_probe",
            sql=f"UPDATE {reservations} SET quantity = quantity WHERE reservation_id = 17",
            qps=0.22,
            tier="OLTP_WRITE",
            application_name="reservation-heartbeat-worker",
        ),
        WorkloadProfile(
            name="mdl_processlist_probe",
            sql=(
                "SELECT COMMAND, STATE, COUNT(*) FROM information_schema.processlist "
                "GROUP BY COMMAND, STATE ORDER BY COUNT(*) DESC"
            ),
            qps=0.7,
            tier="MONITOR",
            application_name="db-monitor",
        ),
        WorkloadProfile(
            name="mdl_ddl_history_probe",
            sql=(
                "SELECT JOB_TYPE, STATE, COUNT(*) FROM information_schema.ddl_jobs "
                "GROUP BY JOB_TYPE, STATE ORDER BY COUNT(*) DESC"
            ),
            qps=0.6,
            tier="MONITOR",
            application_name="release-controller",
        ),
        WorkloadProfile(
            name="mdl_transaction_inventory_probe",
            sql=(
                "SELECT STATE, COUNT(*) FROM information_schema.cluster_tidb_trx "
                "GROUP BY STATE ORDER BY STATE"
            ),
            qps=0.65,
            tier="MONITOR",
            application_name="transaction-monitor",
        ),
        WorkloadProfile(
            name="mdl_metadata_lock_setting_probe",
            sql="SELECT @@global.tidb_enable_metadata_lock, @@global.tidb_ddl_enable_fast_reorg",
            qps=0.5,
            tier="CONFIG",
            application_name="config-auditor",
        ),
        WorkloadProfile(
            name="mdl_metadata_lock_inventory_probe",
            sql=(
                "SELECT job_id, table_ids FROM mysql.tidb_mdl_info "
                "ORDER BY job_id DESC LIMIT 20"
            ),
            qps=0.5,
            tier="MONITOR",
            application_name="metadata-lock-monitor",
        ),
        WorkloadProfile(
            name="mdl_slow_release_preview",
            sql=(
                f"SELECT SLEEP(0.12), order_status, COUNT(*) FROM {table} "
                "WHERE id > 32 GROUP BY order_status"
            ),
            qps=0.35,
            tier="SLOW_QUERY",
            application_name="release-preview",
        ),
        WorkloadProfile(
            name="mdl_missing_cache_log_noise",
            sql="SELECT COUNT(*) FROM release_mdl_cache_missing",
            qps=0.25,
            tier="LOG_NOISE",
            application_name="cache-refresher",
        ),
    )
    return BackgroundWorkloadSpec(
        profiles=profiles,
        worker_count=12,
        seed=20260731,
        warmup_seconds=4,
    )


@dataclass(frozen=True, slots=True)
class MdlBlockingDecoySpec:
    """One same-domain decoy DDL: a real, same-window DDL left MDL-blocked by its
    own uncommitted session. Only the combination of alert framing, campaign
    column continuity, and table identity identifies the release incident."""

    table: str
    ddl_sql: str
    holder_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureMdlBlockingForLongTransactionMdlBlocksOnlineDdlScenarioCase(TiDBScenarioCase):
    database: str
    table: str
    guard_table: str
    added_column: str
    second_added_column: str
    third_added_column: str
    fourth_added_column: str
    ddl_sql: str
    second_ddl_sql: str
    third_ddl_sql: str
    fourth_ddl_sql: str
    row_count: int
    business_tables: tuple[str, ...]
    release_stage_count: int = 4
    decoys: tuple[MdlBlockingDecoySpec, ...] = ()


MDL_BLOCKING_CASE = TidbSystemFailureMdlBlockingForLongTransactionMdlBlocksOnlineDdlScenarioCase(
    case_id="long_transaction_mdl_blocks_online_ddl",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "online DDL is waiting for a metadata lock held by an old transaction on the target table",
                    "entity": "long_transaction_mdl_blocks_online_ddl",
                    "evidence": [
                        "scripted diagnostic actions observed online DDL is waiting for a metadata lock held by an old transaction on the target table"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "an uncommitted long-running transaction holds the target table metadata lock",
                    "entity": "long_transaction_mdl_blocks_online_ddl",
                    "evidence": [
                        "scripted diagnostic actions observed an uncommitted long-running transaction holds the target table metadata lock"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "all exact blockers are the TiDB sessions identified from tidb_mdl_info and cluster_tidb_trx",
                    "entity": "long_transaction_mdl_blocks_online_ddl",
                    "evidence": [
                        "scripted diagnostic actions observed all exact blockers are the TiDB sessions identified from tidb_mdl_info and cluster_tidb_trx"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "killed only the exact TiDB MDL blockers"
            ],
            "verification": [
                "the same DDL job is synced, the column is public, and the guard session remains alive"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbSystemFailureMdlBlockingEvaluatorCase,
    title="A production release remains incomplete while foreground reads continue.",
    alert=(
        "[CRITICAL] 发布窗口内一项生产变更长时间没有达到预期状态，业务读请求仍可返回，但发布目标迟迟没有完成。"
        "同一窗口还存在定时查询、其他发布活动和历史运行记录，不能把所有等待都视为本次变更的原因。"
        "请从用户可见状态、运行记录、会话活动和集群证据判断发布为何没有收敛，只改变能够证明正在阻止本次变更的状态，"
        "保留无关会话和数据，并验证业务读结果与发布活动均已收敛。"
    ),
    initial_state={
        "status": "degraded",
        "ddl": "running",
        "target_column": "absent",
        "metadata_lock": "held",
    },
    expected_target={
        "status": "recovered",
        "release_chain": "all_synced",
        "target_columns": "public",
        "unrelated_session": "alive",
    },
    background_workload=_mdl_blocking_workload(
        "mdl_release_orders",
        "mdl_release_guard",
        "mdl_customers",
        "mdl_order_payments",
        "mdl_order_shipments",
        "mdl_inventory_reservations",
        "mdl_order_events",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.435,
        reference_run_ids=(
            "reference-238__"
            "tidb_system_failure_mdl_blocking__long_transaction_mdl_blocks_online_ddl__"
            "mock_reference__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=180,
    ),
    database="test",
    table="mdl_release_orders",
    guard_table="mdl_release_guard",
    added_column="release_marker",
    second_added_column="release_batch_id",
    third_added_column="release_audit_id",
    fourth_added_column="release_trace_id",
    ddl_sql="ALTER TABLE mdl_release_orders ADD COLUMN release_marker INT NOT NULL DEFAULT 0",
    second_ddl_sql="ALTER TABLE mdl_release_orders ADD COLUMN release_batch_id INT NOT NULL DEFAULT 0",
    third_ddl_sql="ALTER TABLE mdl_release_orders ADD COLUMN release_audit_id INT NOT NULL DEFAULT 0",
    fourth_ddl_sql="ALTER TABLE mdl_release_orders ADD COLUMN release_trace_id INT NOT NULL DEFAULT 0",
    row_count=128,
    business_tables=(
        "mdl_customers",
        "mdl_order_payments",
        "mdl_order_shipments",
        "mdl_inventory_reservations",
        "mdl_order_events",
    ),
)


_FOCUSED_MDL_WORKLOAD = replace(
    MDL_BLOCKING_CASE.background_workload,
    profiles=tuple(
        profile
        for profile in MDL_BLOCKING_CASE.background_workload.profiles
        if profile.name in {
            "mdl_orders_api_point_read",
            "mdl_customer_order_history",
            "mdl_order_status_summary",
            "mdl_customer_revenue_rollup",
            "mdl_order_api_short_update",
            "mdl_guard_session_read",
            "mdl_guard_health_summary",
            "mdl_processlist_probe",
            "mdl_ddl_history_probe",
            "mdl_transaction_inventory_probe",
            "mdl_metadata_lock_inventory_probe",
        }
    ),
    worker_count=6,
    warmup_seconds=3,
)

_FOCUSED_MDL_CASE = replace(
    MDL_BLOCKING_CASE,
    case_id="mdl_release_chain_simple",
    case_no=1,
    evaluator=TidbSystemFailureMdlBlockingFocusedEvaluatorCase,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        bootstrap_cache_enabled=False,
        sql_timeout_seconds=180,
    ),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "online DDL on the release target table is waiting for a metadata lock held by an uncommitted long-running transaction",
                    "entity": "mdl_release_chain_simple",
                    "evidence": ["the focused release chain exposes a live MDL wait"],
                },
                {
                    "type": "finding",
                    "factor": "all exact blockers are the TiDB sessions identified from tidb_mdl_info and cluster_tidb_trx; only those holder sessions may be terminated while guard and reader sessions stay alive",
                    "entity": "mdl_release_chain_simple",
                    "evidence": ["MDL and transaction rows identify the exact holder session"],
                },
            ]
        },
        "outcome": {
            "changes": ["killed only the exact TiDB MDL blockers"],
            "verification": ["the release DDL job is synced and the guard session remains alive"],
        },
        "summary": "The focused reference completed the single-stage MDL release without touching the guard session.",
    },
    background_workload=_FOCUSED_MDL_WORKLOAD,
    added_column="focused_release_marker",
    second_added_column="focused_release_batch_id",
    third_added_column="focused_release_audit_id",
    fourth_added_column="focused_release_trace_id",
    ddl_sql="ALTER TABLE mdl_release_orders ADD COLUMN focused_release_marker INT NOT NULL DEFAULT 0",
    second_ddl_sql="ALTER TABLE mdl_release_orders ADD COLUMN focused_release_batch_id INT NOT NULL DEFAULT 0",
    third_ddl_sql="ALTER TABLE mdl_release_orders ADD COLUMN focused_release_audit_id INT NOT NULL DEFAULT 0",
    fourth_ddl_sql="ALTER TABLE mdl_release_orders ADD COLUMN focused_release_trace_id INT NOT NULL DEFAULT 0",
    release_stage_count=1,
    decoys=(
        MdlBlockingDecoySpec(
            table="mdl_order_events",
            ddl_sql="ALTER TABLE mdl_order_events ADD INDEX idx_order_events_actor (actor)",
            holder_count=1,
        ),
        MdlBlockingDecoySpec(
            table="mdl_release_orders_archive",
            ddl_sql=(
                "ALTER TABLE mdl_release_orders_archive "
                "ADD COLUMN focused_release_marker INT NOT NULL DEFAULT 0"
            ),
            holder_count=1,
        ),
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.681818,
        reference_run_ids=(
            "reference-240__tidb_system_failure_mdl_blocking__mdl_release_chain_simple__mock__r001",
        ),
    ),
)


class TidbSystemFailureMdlBlockingInjector(BaseFaultInjector):
    """Reproduce a serial release DDL chain with two real MDL wait phases.

    When the case configures ``decoy_holder_count`` the injector additionally
    submits a real, same-window maintenance DDL on ``decoy_table`` and leaves it
    MDL-blocked by its own uncommitted ETL session, so only one stuck DDL in
    ``information_schema.ddl_jobs`` belongs to the release incident.
    """

    HOLDER_COUNT = 6
    LATE_HOLDER_COUNT = 2
    THIRD_HOLDER_COUNT = 2
    FOURTH_HOLDER_COUNT = 2
    GUARD_COUNT = 2
    TARGET_READER_COUNT = 2

    def __init__(self):
        self._configured = False
        self._config = None
        self._runtime_stop = None
        self._holder_ready = None
        self._late_holder_ready = None
        self._third_holder_ready = None
        self._fourth_holder_ready = None
        self._guard_ready = None
        self._target_reader_ready = None
        self._target_reader_stop = None
        self._ddl_started = None
        self._ddl_done = None
        self._second_ddl_started = None
        self._second_ddl_done = None
        self._third_ddl_started = None
        self._third_ddl_done = None
        self._fourth_ddl_started = None
        self._fourth_ddl_done = None
        self._holder_threads = []
        self._late_holder_threads = []
        self._third_holder_threads = []
        self._fourth_holder_threads = []
        self._guard_threads = []
        self._target_reader_threads = []
        self._ddl_thread = None
        self._second_ddl_thread = None
        self._third_ddl_thread = None
        self._fourth_ddl_thread = None
        self._chain_thread = None
        self._holder_conns = []
        self._late_holder_conns = []
        self._third_holder_conns = []
        self._fourth_holder_conns = []
        self._guard_conns = []
        self._target_reader_conns = []
        self._ddl_conn = None
        self._second_ddl_conn = None
        self._third_ddl_conn = None
        self._fourth_ddl_conn = None
        self._holder_errors = []
        self._guard_errors = []
        self._ddl_error = None
        self._late_holder_errors = []
        self._third_holder_errors = []
        self._third_ddl_error = None
        self._fourth_holder_errors = []
        self._fourth_ddl_error = None
        self._target_reader_errors = []
        self._chain_error = None
        self._decoy_runtime: list[dict] = []
        self.decoys: tuple[MdlBlockingDecoySpec, ...] = ()
        self._decoy_fixture_tables: tuple[str, ...] = ()
        self._holder_session_ids = []
        self._late_holder_session_ids = []
        self._third_holder_session_ids = []
        self._fourth_holder_session_ids = []
        self._all_holder_session_ids = []
        self._guard_session_ids = []
        self._target_reader_session_ids = []
        self._ddl_session_id = None
        self._table_id = None
        self._ddl_job_id = None
        self._second_ddl_job_id = None
        self._third_ddl_job_id = None
        self._fourth_ddl_job_id = None
        self._ddl_job_ids = []
        self._ddl_succeeded = False

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._prepare_schema(context.env)
        self._start_runtime(context.env)
        self._wait_until_blocked(context.env)
        self._start_target_readers(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_persistent_state(context.env)
        self._start_runtime(context.env)
        self._wait_until_blocked(context.env)
        self._start_target_readers(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        if (
            self._ddl_job_id is None
            or not self._holder_session_ids
            or len(self._guard_session_ids) != self.GUARD_COUNT
            or len(self._target_reader_session_ids) != self.TARGET_READER_COUNT
            or any(state["job_id"] is None for state in self._decoy_runtime)
        ):
            raise RuntimeError(
                "TiDB MDL blocking observability is unavailable before the MDL wait is established: "
                f"scenario={context.scenario_id}, case={context.case_id}, "
                f"ddl_job_id={self._ddl_job_id!r}, holder_session_ids={self._holder_session_ids!r}, "
                f"guard_session_ids={self._guard_session_ids!r}, "
                f"target_reader_session_ids={self._target_reader_session_ids!r}, "
                f"decoy_job_ids={[state['job_id'] for state in self._decoy_runtime]!r}"
            )
        rows = self._mdl_rows(context.env)
        holder_rows = [row for row in rows if int(row[1]) in self._holder_session_ids]
        if len(holder_rows) != len(self._holder_session_ids):
            raise RuntimeError(
                "TiDB MDL blocking expected all target MDL blockers: "
                f"table={self.table}, table_id={self._table_id}, holder_session_ids={self._holder_session_ids}, "
                f"observed_rows={rows!r}"
            )
        signature = self._business_signature(context.env)
        return {
            "table": self.table,
            "guard_table": self.guard_table,
            "table_id": self._table_id,
            "ddl_job_id": self._ddl_job_id,
            "ddl_job_ids": self._ddl_job_ids,
            "ddl_session_id": self._ddl_session_id,
            "holder_session_ids": self._all_holder_session_ids,
            "late_holder_session_ids": self._late_holder_session_ids,
            "guard_session_ids": self._guard_session_ids,
            "protected_target_session_ids": self._target_reader_session_ids,
            "added_column": self.added_column,
            "second_added_column": self.second_added_column,
            "third_added_column": self.third_added_column,
            "fourth_added_column": self.fourth_added_column,
            "ddl_sql": self.ddl_sql,
            "second_ddl_sql": self.second_ddl_sql,
            "third_ddl_sql": self.third_ddl_sql,
            "fourth_ddl_sql": self.fourth_ddl_sql,
            "row_count": signature[0],
            "id_sum": signature[1],
            "payload_crc": signature[2],
            "mdl_rows": rows,
            "decoy_tables": [state["table"] for state in self._decoy_runtime],
            "decoy_job_ids": [state["job_id"] for state in self._decoy_runtime],
            "decoy_holder_session_ids": [
                session_id
                for state in self._decoy_runtime
                for session_id in state["holder_session_ids"]
            ],
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._cancel_ddl_jobs(context.env)
        self._stop_runtime()

    def recover(self, context: FaultLifecycleContext) -> None:
        if self._runtime_stop is not None:
            self._cancel_ddl_jobs(context.env)
            self._stop_runtime()
        for table in reversed(self.business_tables):
            require_sql_success(
                context.env.execute_sql(f"DROP TABLE IF EXISTS {table}"),
                f"drop TiDB MDL blocking business table {table}",
            )
        for table in reversed(self._decoy_fixture_tables):
            require_sql_success(
                context.env.execute_sql(f"DROP TABLE IF EXISTS {table}"),
                f"drop TiDB MDL blocking decoy fixture table {table}",
            )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.guard_table}"),
            f"drop TiDB MDL blocking guard table {self.guard_table}",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.table}"),
            f"drop TiDB MDL blocking target table {self.table}",
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        if self._configured:
            if dict(config) != self._config:
                raise RuntimeError(
                    "TiDB MDL blocking injector received a different config after initialization: "
                    f"initial={self._config!r}, received={dict(config)!r}"
                )
            return
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.guard_table = validate_sql_identifier(str(config["guard_table"]), "guard_table")
        self.database = validate_sql_identifier(str(config["database"]), "database")
        self.added_column = validate_sql_identifier(str(config["added_column"]), "added_column")
        self.second_added_column = validate_sql_identifier(
            str(config["second_added_column"]), "second_added_column"
        )
        self.third_added_column = validate_sql_identifier(
            str(config["third_added_column"]), "third_added_column"
        )
        self.fourth_added_column = validate_sql_identifier(
            str(config["fourth_added_column"]), "fourth_added_column"
        )
        self.ddl_sql = str(config["ddl_sql"])
        self.second_ddl_sql = str(config["second_ddl_sql"])
        self.third_ddl_sql = str(config["third_ddl_sql"])
        self.fourth_ddl_sql = str(config["fourth_ddl_sql"])
        self.business_tables = tuple(
            validate_sql_identifier(str(table), "business_table")
            for table in config["business_tables"]
        )
        self.release_stage_count = int(config["release_stage_count"])
        if self.release_stage_count < 1 or self.release_stage_count > 4:
            raise ValueError(
                "TiDB MDL blocking release stage count must be between 1 and 4: "
                f"release_stage_count={self.release_stage_count}"
            )
        self.decoys = tuple(
            MdlBlockingDecoySpec(
                table=validate_sql_identifier(str(table), "decoy_table"),
                ddl_sql=str(ddl_sql),
                holder_count=int(holder_count),
            )
            for table, ddl_sql, holder_count in config["decoys"]
        )
        if any(spec.holder_count < 1 for spec in self.decoys):
            raise ValueError(
                "TiDB MDL blocking decoy holder count must be positive: "
                f"decoys={self.decoys!r}"
            )
        decoy_tables = [spec.table for spec in self.decoys]
        if len(decoy_tables) != len(set(decoy_tables)):
            raise ValueError(
                f"TiDB MDL blocking decoy tables must be unique: {decoy_tables!r}"
            )
        reserved = {self.table, self.guard_table}
        if any(spec.table in reserved for spec in self.decoys):
            raise ValueError(
                "TiDB MDL blocking decoy tables must stay outside the reserved tables: "
                f"decoys={decoy_tables!r}, reserved={sorted(reserved)!r}"
            )
        self._decoy_fixture_tables = tuple(
            spec.table for spec in self.decoys if spec.table not in self.business_tables
        )
        self._config = dict(config)
        self._configured = True

    def _connection(self, env, *, autocommit: bool, application_name: str):
        return connect_tidb(
            env,
            database=self.database,
            autocommit=autocommit,
            application_name=application_name,
        )

    def _prepare_schema(self, env) -> None:
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.guard_table}"),
            f"clear TiDB MDL blocking guard table {self.guard_table}",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.table}"),
            f"clear TiDB MDL blocking target table {self.table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.table} ("
                "id INT PRIMARY KEY, customer_id INT NOT NULL, "
                "order_status VARCHAR(16) NOT NULL, order_total DECIMAL(10, 2) NOT NULL, "
                "created_at DATETIME NOT NULL, payload VARCHAR(128) NOT NULL)"
            ),
            f"create TiDB MDL blocking target table {self.table}",
        )
        statuses = ("PAID", "PENDING", "SHIPPED", "CANCELLED")
        values = ",".join(
            f"({index}, {1000 + index % 24}, '{statuses[index % len(statuses)]}', "
            f"{19.99 + (index % 17) * 3.5:.2f}, '2026-07-{1 + index % 28:02d} 12:00:00', "
            f"'order-payload-{index:03d}')"
            for index in range(1, 129)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.table} "
                "(id, customer_id, order_status, order_total, created_at, payload) VALUES "
                f"{values}"
            ),
            f"load TiDB MDL blocking target table {self.table}",
        )
        self._prepare_business_schema(env)
        self._prepare_decoy_fixtures(env)
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.guard_table} ("
                "id INT PRIMARY KEY, customer_id INT NOT NULL, "
                "order_status VARCHAR(16) NOT NULL, order_total DECIMAL(10, 2) NOT NULL, "
                "created_at DATETIME NOT NULL, payload VARCHAR(128) NOT NULL)"
            ),
            f"create TiDB MDL blocking guard table {self.guard_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.guard_table} VALUES "
                "(1, 9001, 'GUARD', 0.00, '2026-07-01 00:00:00', 'unrelated-session-guard')"
            ),
            f"load TiDB MDL blocking guard table {self.guard_table}",
        )
        self._verify_metadata_lock_enabled(env)
        self._table_id = self._table_id_from_catalog(env)

    def _verify_persistent_state(self, env) -> None:
        table_rows = self._rows(
            env,
            "SELECT TABLE_NAME FROM information_schema.tables "
            f"WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME IN ('{self.table}', '{self.guard_table}') "
            "ORDER BY TABLE_NAME",
        )
        expected = sorted(
            (self.table, self.guard_table, *self.business_tables, *self._decoy_fixture_tables)
        )
        observed = sorted(str(row[0]) for row in table_rows)
        if observed != expected:
            raise RuntimeError(
                "TiDB MDL blocking persistent tables are not intact before activate: "
                f"expected={expected!r}, observed={observed!r}"
            )
        column_rows = self._rows(
            env,
            "SELECT COLUMN_NAME FROM information_schema.columns "
            f"WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{self.table}' "
            f"AND COLUMN_NAME = '{self.added_column}'",
        )
        if column_rows:
            raise RuntimeError(
                "TiDB MDL blocking persistent fault state already contains the DDL target column: "
                f"table={self.table}, column={self.added_column}, rows={column_rows!r}"
            )
        self._table_id = self._table_id_from_catalog(env)

    def _verify_metadata_lock_enabled(self, env) -> None:
        rows = self._rows(env, "SELECT @@global.tidb_enable_metadata_lock")
        if rows != [[1]]:
            raise RuntimeError(
                "TiDB MDL blocking requires metadata locks to be enabled: "
                f"expected=[[1]], observed={rows!r}"
            )

    def _prepare_business_schema(self, env) -> None:
        customers, payments, shipments, reservations, events = self.business_tables
        for table in reversed(self.business_tables):
            require_sql_success(
                env.execute_sql(f"DROP TABLE IF EXISTS {table}"),
                f"clear TiDB MDL blocking business table {table}",
            )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {customers} ("
                "customer_id INT PRIMARY KEY, customer_segment VARCHAR(16) NOT NULL, "
                "region VARCHAR(16) NOT NULL, loyalty_tier VARCHAR(16) NOT NULL)"
            ),
            f"create TiDB MDL blocking customer table {customers}",
        )
        customer_values = ",".join(
            f"({1000 + index}, '{('CONSUMER', 'SMB', 'ENTERPRISE')[index % 3]}', "
            f"'{('NORTH', 'SOUTH', 'EAST', 'WEST')[index % 4]}', "
            f"'{('STANDARD', 'GOLD', 'REVIEW')[index % 3]}')"
            for index in range(24)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {customers} (customer_id, customer_segment, region, loyalty_tier) VALUES {customer_values}"
            ),
            f"load TiDB MDL blocking customer table {customers}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {payments} ("
                "payment_id INT PRIMARY KEY, order_id INT NOT NULL, payment_status VARCHAR(16) NOT NULL, "
                "gateway VARCHAR(16) NOT NULL, paid_at DATETIME NOT NULL, amount DECIMAL(10, 2) NOT NULL)"
            ),
            f"create TiDB MDL blocking payment table {payments}",
        )
        payment_values = ",".join(
            f"({index}, {index}, '{('CAPTURED', 'AUTHORIZED', 'RETRY', 'FAILED')[index % 4]}', "
            f"'{('stripe', 'adyen', 'checkout')[index % 3]}', '2026-07-{1 + index % 28:02d} 12:05:00', "
            f"{19.99 + (index % 17) * 3.5:.2f})"
            for index in range(1, 129)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {payments} (payment_id, order_id, payment_status, gateway, paid_at, amount) VALUES {payment_values}"
            ),
            f"load TiDB MDL blocking payment table {payments}",
        )
        require_sql_success(
            env.execute_sql(
                f"ALTER TABLE {payments} ADD COLUMN {self.added_column} INT NOT NULL DEFAULT 0"
            ),
            f"record completed TiDB MDL blocking neighboring release DDL on {payments}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {shipments} ("
                "shipment_id INT PRIMARY KEY, order_id INT NOT NULL, carrier VARCHAR(16) NOT NULL, "
                "shipment_status VARCHAR(16) NOT NULL, promised_at DATETIME NOT NULL, delivered_at DATETIME NOT NULL)"
            ),
            f"create TiDB MDL blocking shipment table {shipments}",
        )
        shipment_values = ",".join(
            f"({index}, {index}, '{('DHL', 'UPS', 'SF')[index % 3]}', "
            f"'{('DELIVERED', 'IN_TRANSIT', 'READY')[index % 3]}', "
            f"'2026-07-{2 + index % 26:02d} 12:00:00', '2026-07-{3 + index % 25:02d} 15:00:00')"
            for index in range(1, 129)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {shipments} (shipment_id, order_id, carrier, shipment_status, promised_at, delivered_at) VALUES {shipment_values}"
            ),
            f"load TiDB MDL blocking shipment table {shipments}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {reservations} ("
                "reservation_id INT PRIMARY KEY, order_id INT NOT NULL, sku VARCHAR(24) NOT NULL, "
                "quantity INT NOT NULL, reservation_status VARCHAR(16) NOT NULL, expires_at DATETIME NOT NULL)"
            ),
            f"create TiDB MDL blocking reservation table {reservations}",
        )
        reservation_values = ",".join(
            f"({index}, {1 + (index - 1) % 128}, 'SKU-{1 + index % 24:03d}', {1 + index % 5}, "
            f"'{('HELD', 'RELEASED', 'RETRY')[index % 3]}', '2026-08-{1 + index % 20:02d} 00:00:00')"
            for index in range(1, 257)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {reservations} (reservation_id, order_id, sku, quantity, reservation_status, expires_at) VALUES {reservation_values}"
            ),
            f"load TiDB MDL blocking reservation table {reservations}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {events} ("
                "event_id INT PRIMARY KEY, order_id INT NOT NULL, event_type VARCHAR(24) NOT NULL, "
                "event_at DATETIME NOT NULL, actor VARCHAR(24) NOT NULL, payload VARCHAR(96) NOT NULL)"
            ),
            f"create TiDB MDL blocking event table {events}",
        )
        event_values = ",".join(
            f"({index}, {1 + (index - 1) % 128}, '{('ORDER_CREATED', 'STATUS_CHANGED', 'FULFILLMENT')[index % 3]}', "
            f"'2026-07-{1 + index % 28:02d} 12:{index % 60:02d}:00', "
            f"'{('checkout', 'warehouse', 'carrier')[index % 3]}', 'release-event-{index:04d}')"
            for index in range(1, 385)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {events} (event_id, order_id, event_type, event_at, actor, payload) VALUES {event_values}"
            ),
            f"load TiDB MDL blocking event table {events}",
        )

    def _prepare_decoy_fixtures(self, env) -> None:
        statuses = ("PAID", "PENDING", "SHIPPED", "CANCELLED")
        for table in self._decoy_fixture_tables:
            require_sql_success(
                env.execute_sql(f"DROP TABLE IF EXISTS {table}"),
                f"clear TiDB MDL blocking decoy fixture table {table}",
            )
            require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {table} ("
                    "id INT PRIMARY KEY, customer_id INT NOT NULL, "
                    "order_status VARCHAR(16) NOT NULL, order_total DECIMAL(10, 2) NOT NULL, "
                    "created_at DATETIME NOT NULL, payload VARCHAR(128) NOT NULL)"
                ),
                f"create TiDB MDL blocking decoy fixture table {table}",
            )
            values = ",".join(
                f"({index}, {1000 + index % 24}, '{statuses[index % len(statuses)]}', "
                f"{19.99 + (index % 17) * 3.5:.2f}, '2026-07-{1 + index % 28:02d} 12:00:00', "
                f"'{table}-row-{index:03d}')"
                for index in range(1, 65)
            )
            require_sql_success(
                env.execute_sql(
                    f"INSERT INTO {table} "
                    "(id, customer_id, order_status, order_total, created_at, payload) VALUES "
                    f"{values}"
                ),
                f"load TiDB MDL blocking decoy fixture table {table}",
            )

    def _table_id_from_catalog(self, env, table: str | None = None) -> int:
        table = table or self.table
        rows = self._rows(
            env,
            "SELECT TIDB_TABLE_ID FROM information_schema.tables "
            f"WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table}'",
        )
        if len(rows) != 1:
            raise RuntimeError(
                "TiDB MDL blocking target table must have exactly one catalog identity: "
                f"database={self.database}, table={table}, rows={rows!r}"
            )
        return int(rows[0][0])

    def _start_runtime(self, env) -> None:
        self._runtime_stop = threading.Event()
        self._holder_ready = threading.Event()
        self._late_holder_ready = threading.Event()
        self._third_holder_ready = threading.Event()
        self._fourth_holder_ready = threading.Event()
        self._guard_ready = threading.Event()
        self._target_reader_ready = threading.Event()
        self._target_reader_stop = threading.Event()
        self._ddl_started = threading.Event()
        self._ddl_done = threading.Event()
        self._second_ddl_started = threading.Event()
        self._second_ddl_done = threading.Event()
        self._third_ddl_started = threading.Event()
        self._third_ddl_done = threading.Event()
        self._fourth_ddl_started = threading.Event()
        self._fourth_ddl_done = threading.Event()
        self._holder_errors = []
        self._late_holder_errors = []
        self._third_holder_errors = []
        self._fourth_holder_errors = []
        self._target_reader_errors = []
        self._guard_errors = []
        self._guard_conns = []
        self._target_reader_conns = []
        self._target_reader_threads = []
        self._third_holder_conns = []
        self._third_holder_threads = []
        self._fourth_holder_conns = []
        self._fourth_holder_threads = []
        self._ddl_error = None
        self._third_ddl_error = None
        self._fourth_ddl_error = None
        self._chain_error = None
        self._decoy_runtime = []
        self._holder_session_ids = []
        self._late_holder_session_ids = []
        self._third_holder_session_ids = []
        self._fourth_holder_session_ids = []
        self._all_holder_session_ids = []
        self._guard_session_ids = []
        self._target_reader_session_ids = []
        self._ddl_session_id = None
        self._ddl_job_id = None
        self._second_ddl_job_id = None
        self._third_ddl_job_id = None
        self._fourth_ddl_job_id = None
        self._ddl_job_ids = []
        self._ddl_succeeded = False

        self._guard_threads = [
            threading.Thread(
                target=self._hold_guard_session,
                args=(env, guard_index),
                name=f"tidb-mdl-blocking-guard-session-{guard_index}",
                daemon=True,
            )
            for guard_index in range(self.GUARD_COUNT)
        ]
        self._holder_threads = [
            threading.Thread(
                target=self._hold_target_session,
                args=(env, holder_index, "initial"),
                name=f"tidb-mdl-blocking-mdl-holder-{holder_index}",
                daemon=True,
            )
            for holder_index in range(self.HOLDER_COUNT)
        ]
        self._ddl_thread = threading.Thread(
            target=self._run_blocked_ddl,
            args=(env,),
            name="tidb-mdl-blocking-blocked-ddl",
            daemon=True,
        )
        for thread in self._guard_threads:
            thread.start()
        for thread in self._holder_threads:
            thread.start()
        self._guard_ready.wait(timeout=10)
        self._holder_ready.wait(timeout=10)
        if self._guard_errors:
            raise RuntimeError(f"TiDB MDL blocking guard sessions failed: {self._guard_errors!r}")
        if self._holder_errors:
            raise RuntimeError(f"TiDB MDL blocking MDL holder failed: {self._holder_errors!r}")
        if not self._guard_ready.is_set() or not self._holder_ready.is_set():
            raise RuntimeError(
                "TiDB MDL blocking sessions did not become ready: "
                f"guard_ready={self._guard_ready.is_set()}, holder_ready={self._holder_ready.is_set()}, "
                f"table={self.table}"
            )
        self._ddl_thread.start()
        self._ddl_started.wait(timeout=10)
        if not self._ddl_started.is_set():
            raise RuntimeError(f"TiDB MDL blocking DDL session did not start: table={self.table}")
        self._chain_thread = threading.Thread(
            target=self._advance_release_chain,
            args=(env,),
            name="tidb-mdl-blocking-release-chain",
            daemon=True,
        )
        self._chain_thread.start()
        self._start_decoy(env)

    def _start_decoy(self, env) -> None:
        for decoy_index, spec in enumerate(self.decoys):
            state = {
                "table": spec.table,
                "table_id": self._table_id_from_catalog(env, spec.table),
                "holder_threads": [
                    threading.Thread(
                        target=self._hold_decoy_session,
                        args=(env, decoy_index, holder_index),
                        name=f"tidb-mdl-blocking-decoy-{decoy_index}-holder-{holder_index}",
                        daemon=True,
                    )
                    for holder_index in range(spec.holder_count)
                ],
                "holder_conns": [],
                "holder_errors": [],
                "holder_session_ids": [],
                "holder_ready": threading.Event(),
                "ddl_thread": None,
                "ddl_started": threading.Event(),
                "ddl_error": None,
                "job_id": None,
            }
            self._decoy_runtime.append(state)
            for thread in state["holder_threads"]:
                thread.start()
            state["holder_ready"].wait(timeout=10)
            if state["holder_errors"]:
                raise RuntimeError(
                    "TiDB MDL blocking decoy holder sessions failed: "
                    f"decoy_index={decoy_index}, table={spec.table}, errors={state['holder_errors']!r}"
                )
            if not state["holder_ready"].is_set():
                raise RuntimeError(
                    "TiDB MDL blocking decoy holder sessions did not become ready: "
                    f"decoy_index={decoy_index}, table={spec.table}, expected={spec.holder_count}, "
                    f"observed={state['holder_session_ids']!r}"
                )
            state["ddl_thread"] = threading.Thread(
                target=self._run_decoy_ddl,
                args=(env, decoy_index),
                name=f"tidb-mdl-blocking-decoy-{decoy_index}-ddl",
                daemon=True,
            )
            state["ddl_thread"].start()
            state["ddl_started"].wait(timeout=10)
            if not state["ddl_started"].is_set():
                raise RuntimeError(
                    "TiDB MDL blocking decoy maintenance DDL session did not start: "
                    f"decoy_index={decoy_index}, table={spec.table}"
                )
            state["job_id"] = self._wait_decoy_job_blocked(env, decoy_index)

    def _hold_decoy_session(self, env, decoy_index: int, holder_index: int) -> None:
        state = self._decoy_runtime[decoy_index]
        conn = self._connection(
            env,
            autocommit=False,
            application_name=f"mdl-blocking-decoy-{decoy_index}-holder-{holder_index}",
        )
        state["holder_conns"].append(conn)
        try:
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute(f"SELECT * FROM {state['table']} LIMIT 1")
            state["holder_session_ids"].append(conn.thread_id())
            if len(state["holder_session_ids"]) == len(state["holder_threads"]):
                state["holder_ready"].set()
            self._runtime_stop.wait()
            conn.rollback()
        except Exception as exc:
            state["holder_errors"].append(exc)
            state["holder_ready"].set()
        finally:
            conn.close()

    def _run_decoy_ddl(self, env, decoy_index: int) -> None:
        state = self._decoy_runtime[decoy_index]
        conn = self._connection(
            env, autocommit=True, application_name=f"mdl-blocking-decoy-{decoy_index}-ddl"
        )
        state["ddl_started"].set()
        try:
            with conn.cursor() as cur:
                cur.execute(self.decoys[decoy_index].ddl_sql)
        except Exception as exc:
            state["ddl_error"] = exc
        finally:
            conn.close()

    def _wait_decoy_job_blocked(self, env, decoy_index: int) -> int:
        state = self._decoy_runtime[decoy_index]
        spec = self.decoys[decoy_index]
        deadline = time.monotonic() + 30
        observed = []
        while time.monotonic() < deadline:
            if state["ddl_error"] is not None:
                raise RuntimeError(
                    "TiDB MDL blocking decoy maintenance DDL failed before becoming blocked: "
                    f"decoy_index={decoy_index}, sql={spec.ddl_sql!r}, error={state['ddl_error']}"
                )
            observed = self._rows(
                env,
                "SELECT job_id, table_ids FROM mysql.tidb_mdl_info "
                f"WHERE table_ids = '{state['table_id']}'",
            )
            if observed:
                return int(observed[0][0])
            time.sleep(0.25)
        raise RuntimeError(
            "TiDB MDL blocking decoy maintenance DDL never became MDL-blocked: "
            f"decoy_index={decoy_index}, table={spec.table}, table_id={state['table_id']}, "
            f"sql={spec.ddl_sql!r}, observed_mdl_rows={observed!r}"
        )

    def _hold_guard_session(self, env, guard_index: int) -> None:
        conn = self._connection(
            env,
            autocommit=False,
            application_name=f"mdl-blocking-unrelated-guard-{guard_index}",
        )
        self._guard_conns.append(conn)
        try:
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute(f"SELECT * FROM {self.guard_table} WHERE id = 1")
            self._guard_session_ids.append(conn.thread_id())
            if len(self._guard_session_ids) == self.GUARD_COUNT:
                self._guard_ready.set()
            self._runtime_stop.wait()
            conn.rollback()
        except Exception as exc:
            self._guard_errors.append(exc)
            self._guard_ready.set()
        finally:
            conn.close()

    def _start_target_readers(self, env) -> None:
        self._target_reader_threads = [
            threading.Thread(
                target=self._hold_target_reader,
                args=(env, reader_index),
                name=f"tidb-mdl-blocking-target-reader-{reader_index}",
                daemon=True,
            )
            for reader_index in range(self.TARGET_READER_COUNT)
        ]
        for thread in self._target_reader_threads:
            thread.start()
        self._target_reader_ready.wait(timeout=10)
        if self._target_reader_errors:
            raise RuntimeError(
                f"TiDB MDL blocking target readers failed: {self._target_reader_errors!r}"
            )
        if not self._target_reader_ready.is_set():
            raise RuntimeError(
                "TiDB MDL blocking target readers did not become ready: "
                f"expected={self.TARGET_READER_COUNT}, observed={self._target_reader_session_ids!r}"
            )

    def _hold_target_reader(self, env, reader_index: int) -> None:
        conn = self._connection(
            env,
            autocommit=False,
            application_name=f"mdl-blocking-target-reader-{reader_index}",
        )
        self._target_reader_conns.append(conn)
        try:
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute(f"SELECT * FROM {self.table} WHERE id = 1")
                conn.commit()
                cur.execute("BEGIN")
            self._target_reader_session_ids.append(conn.thread_id())
            if len(self._target_reader_session_ids) == self.TARGET_READER_COUNT:
                self._target_reader_ready.set()
            self._target_reader_stop.wait()
        except Exception as exc:
            self._target_reader_errors.append(exc)
            self._target_reader_ready.set()
        finally:
            conn.close()

    def _hold_target_session(self, env, holder_index: int, phase: str) -> None:
        conn = self._connection(
            env,
            autocommit=False,
            application_name=f"mdl-blocking-mdl-{phase}-holder-{holder_index}",
        )
        if phase == "initial":
            holder_conns = self._holder_conns
            holder_session_ids = self._holder_session_ids
            holder_threads = self._holder_threads
            holder_errors = self._holder_errors
            holder_ready = self._holder_ready
        elif phase == "late":
            holder_conns = self._late_holder_conns
            holder_session_ids = self._late_holder_session_ids
            holder_threads = self._late_holder_threads
            holder_errors = self._late_holder_errors
            holder_ready = self._late_holder_ready
        elif phase == "third":
            holder_conns = self._third_holder_conns
            holder_session_ids = self._third_holder_session_ids
            holder_threads = self._third_holder_threads
            holder_errors = self._third_holder_errors
            holder_ready = self._third_holder_ready
        elif phase == "fourth":
            holder_conns = self._fourth_holder_conns
            holder_session_ids = self._fourth_holder_session_ids
            holder_threads = self._fourth_holder_threads
            holder_errors = self._fourth_holder_errors
            holder_ready = self._fourth_holder_ready
        else:
            raise ValueError(f"Unsupported TiDB MDL holder phase: phase={phase!r}")
        holder_conns.append(conn)
        try:
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute(f"SELECT * FROM {self.table} WHERE id = 1")
            session_id = conn.thread_id()
            holder_session_ids.append(session_id)
            self._all_holder_session_ids.append(session_id)
            if len(holder_session_ids) == len(holder_threads):
                holder_ready.set()
            self._runtime_stop.wait()
            conn.rollback()
        except Exception as exc:
            holder_errors.append(exc)
            holder_ready.set()
        finally:
            conn.close()

    def _run_blocked_ddl(self, env) -> None:
        self._run_ddl(env, self.ddl_sql, "initial")

    def _run_second_ddl(self, env) -> None:
        self._run_ddl(env, self.second_ddl_sql, "second")

    def _run_third_ddl(self, env) -> None:
        self._run_ddl(env, self.third_ddl_sql, "third")

    def _run_fourth_ddl(self, env) -> None:
        self._run_ddl(env, self.fourth_ddl_sql, "fourth")

    def _run_ddl(self, env, sql: str, phase: str) -> None:
        conn = self._connection(env, autocommit=True, application_name="mdl-blocking-online-ddl")
        if phase == "initial":
            self._ddl_conn = conn
            self._ddl_session_id = conn.thread_id()
            self._ddl_started.set()
        elif phase == "second":
            self._second_ddl_conn = conn
            self._second_ddl_started.set()
        elif phase == "third":
            self._third_ddl_conn = conn
            self._third_ddl_started.set()
        else:
            self._fourth_ddl_conn = conn
            self._fourth_ddl_started.set()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
            if phase == "initial":
                self._ddl_succeeded = True
        except Exception as exc:
            if phase == "initial":
                self._ddl_error = exc
            elif phase == "second":
                self._chain_error = exc
            elif phase == "third":
                self._third_ddl_error = exc
            else:
                self._fourth_ddl_error = exc
        finally:
            conn.close()
            if phase == "initial":
                self._ddl_done.set()
            elif phase == "second":
                self._second_ddl_done.set()
            elif phase == "third":
                self._third_ddl_done.set()
            else:
                self._fourth_ddl_done.set()

    def _advance_release_chain(self, env) -> None:
        if self.release_stage_count <= 1:
            return
        self._ddl_done.wait()
        if self._runtime_stop.is_set():
            return
        if self._ddl_error is not None or not self._ddl_succeeded:
            self._chain_error = RuntimeError(
                "TiDB MDL blocking first release DDL did not complete before the second stage: "
                f"ddl_error={self._ddl_error!r}, ddl_job_id={self._ddl_job_id!r}"
            )
            return
        self._stop_target_readers()
        self._late_holder_threads = [
            threading.Thread(
                target=self._hold_target_session,
                args=(env, holder_index, "late"),
                name=f"tidb-mdl-blocking-late-mdl-holder-{holder_index}",
                daemon=True,
            )
            for holder_index in range(self.LATE_HOLDER_COUNT)
        ]
        for thread in self._late_holder_threads:
            thread.start()
        self._late_holder_ready.wait(timeout=10)
        if self._late_holder_errors:
            self._chain_error = RuntimeError(
                f"TiDB MDL blocking late MDL holders failed: errors={self._late_holder_errors!r}"
            )
            return
        if not self._late_holder_ready.is_set():
            self._chain_error = RuntimeError(
                "TiDB MDL blocking late MDL holders did not become ready: "
                f"expected={self.LATE_HOLDER_COUNT}, observed={self._late_holder_session_ids!r}"
            )
            return
        self._second_ddl_thread = threading.Thread(
            target=self._run_second_ddl,
            args=(env,),
            name="tidb-mdl-blocking-second-ddl",
            daemon=True,
        )
        self._second_ddl_thread.start()
        self._second_ddl_started.wait(timeout=10)
        if not self._second_ddl_started.is_set():
            self._chain_error = RuntimeError("TiDB MDL blocking second release DDL session did not start")
            return
        self._second_ddl_job_id = self._find_ddl_job(env, self.second_added_column)
        self._ddl_job_ids.append(self._second_ddl_job_id)
        self._second_ddl_done.wait()
        if self._runtime_stop.is_set():
            return
        if self._chain_error is not None:
            return
        self._third_holder_threads = [
            threading.Thread(
                target=self._hold_target_session,
                args=(env, holder_index, "third"),
                name=f"tidb-mdl-blocking-third-mdl-holder-{holder_index}",
                daemon=True,
            )
            for holder_index in range(self.THIRD_HOLDER_COUNT)
        ]
        for thread in self._third_holder_threads:
            thread.start()
        self._third_holder_ready.wait(timeout=10)
        if self._third_holder_errors:
            self._chain_error = RuntimeError(
                f"TiDB MDL blocking third MDL holders failed: errors={self._third_holder_errors!r}"
            )
            return
        if not self._third_holder_ready.is_set():
            self._chain_error = RuntimeError(
                "TiDB MDL blocking third MDL holders did not become ready: "
                f"expected={self.THIRD_HOLDER_COUNT}, observed={self._third_holder_session_ids!r}"
            )
            return
        self._third_ddl_thread = threading.Thread(
            target=self._run_third_ddl,
            args=(env,),
            name="tidb-mdl-blocking-third-ddl",
            daemon=True,
        )
        self._third_ddl_thread.start()
        self._third_ddl_started.wait(timeout=10)
        if not self._third_ddl_started.is_set():
            self._chain_error = RuntimeError("TiDB MDL blocking third release DDL session did not start")
            return
        self._third_ddl_job_id = self._find_ddl_job(env, self.third_added_column)
        self._ddl_job_ids.append(self._third_ddl_job_id)
        self._third_ddl_done.wait()
        if self._runtime_stop.is_set():
            return
        if self._third_ddl_error is not None:
            self._chain_error = self._third_ddl_error
            return
        self._fourth_holder_threads = [
            threading.Thread(
                target=self._hold_target_session,
                args=(env, holder_index, "fourth"),
                name=f"tidb-mdl-blocking-fourth-mdl-holder-{holder_index}",
                daemon=True,
            )
            for holder_index in range(self.FOURTH_HOLDER_COUNT)
        ]
        for thread in self._fourth_holder_threads:
            thread.start()
        self._fourth_holder_ready.wait(timeout=10)
        if self._fourth_holder_errors:
            self._chain_error = RuntimeError(
                f"TiDB MDL blocking fourth MDL holders failed: errors={self._fourth_holder_errors!r}"
            )
            return
        if not self._fourth_holder_ready.is_set():
            self._chain_error = RuntimeError(
                "TiDB MDL blocking fourth MDL holders did not become ready: "
                f"expected={self.FOURTH_HOLDER_COUNT}, observed={self._fourth_holder_session_ids!r}"
            )
            return
        self._fourth_ddl_thread = threading.Thread(
            target=self._run_fourth_ddl,
            args=(env,),
            name="tidb-mdl-blocking-fourth-ddl",
            daemon=True,
        )
        self._fourth_ddl_thread.start()
        self._fourth_ddl_started.wait(timeout=10)
        if not self._fourth_ddl_started.is_set():
            self._chain_error = RuntimeError("TiDB MDL blocking fourth release DDL session did not start")
            return
        self._fourth_ddl_job_id = self._find_ddl_job(env, self.fourth_added_column)
        self._ddl_job_ids.append(self._fourth_ddl_job_id)

    def _find_ddl_job(self, env, added_column: str) -> int:
        conn = self._connection(env, autocommit=True, application_name="mdl-blocking-release-chain-monitor")
        deadline = time.monotonic() + 30
        observed = []
        try:
            while time.monotonic() < deadline:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT JOB_ID, DB_NAME, TABLE_NAME, JOB_TYPE, SCHEMA_STATE, STATE, QUERY "
                        f"FROM information_schema.ddl_jobs WHERE TABLE_NAME = '{self.table}' "
                        f"AND JOB_ID > {self._ddl_job_id} "
                        "ORDER BY JOB_ID DESC LIMIT 20"
                    )
                    observed = cursor.fetchall()
                for row in observed:
                    if added_column.casefold() in str(row[6]).casefold():
                        return int(row[0])
                if self._runtime_stop.is_set():
                    raise RuntimeError(
                        "TiDB MDL blocking release chain stopped while locating the second DDL job: "
                        f"table={self.table}, added_column={added_column}, observed={observed!r}"
                    )
                time.sleep(0.25)
            raise RuntimeError(
                "TiDB MDL blocking second DDL job was not visible: "
                f"table={self.table}, added_column={added_column}, observed={observed!r}"
            )
        finally:
            conn.close()

    def _wait_until_blocked(self, env) -> None:
        deadline = time.monotonic() + 30
        observed = []
        while time.monotonic() < deadline:
            if self._ddl_error is not None:
                raise RuntimeError(f"TiDB MDL blocking DDL failed before becoming blocked: {self._ddl_error}")
            observed = self._mdl_rows(env)
            holder_rows = [row for row in observed if int(row[1]) in self._holder_session_ids]
            if len(holder_rows) == len(self._holder_session_ids) == self.HOLDER_COUNT:
                self._ddl_job_id = int(holder_rows[0][0])
                self._ddl_job_ids.append(self._ddl_job_id)
                return
            time.sleep(0.25)
        raise RuntimeError(
            "TiDB MDL blocking did not establish a visible MDL blocker within 30 seconds: "
            f"table={self.table}, table_id={self._table_id}, holder_session_ids={self._holder_session_ids}, "
            f"ddl_session_id={self._ddl_session_id}, observed_mdl_rows={observed!r}"
        )

    def _mdl_rows(self, env) -> list:
        return self._rows(
            env,
            "SELECT m.job_id, t.session_id, t.start_time, t.current_sql_digest_text, t.related_table_ids "
            "FROM mysql.tidb_mdl_info AS m "
            "JOIN information_schema.cluster_tidb_trx AS t "
            "ON CONCAT(',', m.table_ids, ',') REGEXP "
            "CONCAT(',(', REPLACE(t.related_table_ids, ',', '|'), '),') "
            "AND t.related_table_ids = m.table_ids "
            "JOIN information_schema.ddl_jobs AS d "
            "ON d.job_id = m.job_id AND t.start_time <= d.start_time "
            f"WHERE m.table_ids = '{self._table_id}' ORDER BY t.start_time",
        )

    def _business_signature(self, env) -> tuple[int, int, int]:
        rows = self._rows(
            env,
            f"SELECT COUNT(*), COALESCE(SUM(id), 0), "
            f"BIT_XOR(CRC32(CONCAT(id, ':', payload))) FROM {self.table}",
        )
        if len(rows) != 1 or len(rows[0]) != 3:
            raise RuntimeError(
                "TiDB MDL blocking business signature query returned an invalid shape: "
                f"table={self.table}, rows={rows!r}"
            )
        return int(rows[0][0]), int(rows[0][1]), int(rows[0][2])

    def _cancel_ddl_jobs(self, env) -> None:
        rows = self._rows(
            env,
            "SELECT JOB_ID, STATE, QUERY FROM information_schema.ddl_jobs "
            f"WHERE TABLE_NAME = '{self.table}' ORDER BY JOB_ID DESC LIMIT 20",
        )
        active_job_ids = {
            int(row[0])
            for row in rows
            if str(row[1]).casefold() == "running"
            and any(
                column.casefold() in str(row[2]).casefold()
                for column in (
                    self.added_column,
                    self.second_added_column,
                    self.third_added_column,
                    self.fourth_added_column,
                )
            )
        }
        active_job_ids.update(
            int(job_id)
            for job_id in self._ddl_job_ids
            if any(int(row[0]) == int(job_id) and str(row[1]).casefold() == "running" for row in rows)
        )
        for state in self._decoy_runtime:
            if state["job_id"] is not None:
                active_job_ids.add(int(state["job_id"]))
        for job_id in sorted(active_job_ids):
            require_sql_success(
                env.execute_sql(f"ADMIN CANCEL DDL JOBS {job_id}"),
                f"cancel TiDB MDL blocking DDL job {job_id}",
            )

    def _stop_target_readers(self) -> None:
        if self._target_reader_stop is None:
            return
        self._target_reader_stop.set()
        for index, thread in enumerate(self._target_reader_threads):
            join_thread(thread, 10, f"TiDB MDL blocking target reader thread {index}")
        self._target_reader_conns = []
        self._target_reader_threads = []
        self._target_reader_stop = None
        self._target_reader_ready = None

    def _stop_runtime(self) -> None:
        if self._runtime_stop is None:
            raise RuntimeError(f"TiDB MDL blocking runtime is not active: table={self.table}")
        self._runtime_stop.set()
        if self._chain_thread is not None:
            join_thread(self._chain_thread, 10, "TiDB MDL blocking release-chain thread")
        self._stop_target_readers()
        for index, thread in enumerate(self._holder_threads):
            join_thread(thread, 10, f"TiDB MDL blocking MDL holder thread {index}")
        for index, thread in enumerate(self._late_holder_threads):
            join_thread(thread, 10, f"TiDB MDL blocking late MDL holder thread {index}")
        for index, thread in enumerate(self._third_holder_threads):
            join_thread(thread, 10, f"TiDB MDL blocking third MDL holder thread {index}")
        for index, thread in enumerate(self._fourth_holder_threads):
            join_thread(thread, 10, f"TiDB MDL blocking fourth MDL holder thread {index}")
        for decoy_index, state in enumerate(self._decoy_runtime):
            for holder_index, thread in enumerate(state["holder_threads"]):
                join_thread(thread, 10, f"TiDB MDL blocking decoy {decoy_index} holder thread {holder_index}")
        for index, thread in enumerate(self._guard_threads):
            join_thread(thread, 10, f"TiDB MDL blocking guard session thread {index}")
        if self._ddl_thread is not None:
            join_thread(self._ddl_thread, 45, "TiDB MDL blocking DDL thread")
        if self._second_ddl_thread is not None:
            join_thread(self._second_ddl_thread, 45, "TiDB MDL blocking second DDL thread")
        if self._third_ddl_thread is not None:
            join_thread(self._third_ddl_thread, 45, "TiDB MDL blocking third DDL thread")
        if self._fourth_ddl_thread is not None:
            join_thread(self._fourth_ddl_thread, 45, "TiDB MDL blocking fourth DDL thread")
        for decoy_index, state in enumerate(self._decoy_runtime):
            if state["ddl_thread"] is not None:
                join_thread(state["ddl_thread"], 45, f"TiDB MDL blocking decoy {decoy_index} DDL thread")
        self._holder_conns = []
        self._late_holder_conns = []
        self._third_holder_conns = []
        self._fourth_holder_conns = []
        self._decoy_runtime = []
        self._guard_conns = []
        self._target_reader_conns = []
        self._ddl_conn = None
        self._second_ddl_conn = None
        self._third_ddl_conn = None
        self._fourth_ddl_conn = None
        self._holder_threads = []
        self._late_holder_threads = []
        self._third_holder_threads = []
        self._fourth_holder_threads = []
        self._guard_threads = []
        self._target_reader_threads = []
        self._ddl_thread = None
        self._second_ddl_thread = None
        self._third_ddl_thread = None
        self._fourth_ddl_thread = None
        self._chain_thread = None
        self._runtime_stop = None

    def _rows(self, env, sql: str) -> list:
        payload = json_object(env.execute_sql(sql), f"TiDB MDL blocking SQL: {sql}")
        result = payload["result"]
        if not isinstance(result, list):
            raise TypeError(
                "TiDB MDL blocking SQL result must be a row list: "
                f"sql={sql!r}, result_type={type(result).__name__}"
            )
        return result


class TidbSystemFailureMdlBlockingScenario(TiDBScenario):
    scenario_id = "tidb_system_failure_mdl_blocking"
    description = "Investigates a production change that has not converged while foreground traffic remains available."
    cases = (MDL_BLOCKING_CASE, _FOCUSED_MDL_CASE)

    def build_fault_plan(
        self,
        case: TidbSystemFailureMdlBlockingForLongTransactionMdlBlocksOnlineDdlScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureMdlBlockingInjector,
                config={
                    "database": case.database,
                    "table": case.table,
                    "guard_table": case.guard_table,
                    "added_column": case.added_column,
                    "ddl_sql": case.ddl_sql,
                    "second_added_column": case.second_added_column,
                    "second_ddl_sql": case.second_ddl_sql,
                    "third_added_column": case.third_added_column,
                    "third_ddl_sql": case.third_ddl_sql,
                    "fourth_added_column": case.fourth_added_column,
                    "fourth_ddl_sql": case.fourth_ddl_sql,
                    "business_tables": case.business_tables,
                    "release_stage_count": case.release_stage_count,
                    "decoys": tuple(
                        (spec.table, spec.ddl_sql, spec.holder_count) for spec in case.decoys
                    ),
                },
            ),
        )
