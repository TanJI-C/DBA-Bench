from collections.abc import Mapping

from dataclasses import dataclass, field, replace

import json

import threading

import time

from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    connect_tidb,
    join_thread,
    json_object,
    require_sql_success,
    run_cleanup_steps,
    validate_sql_identifier,
)

from dataclasses import dataclass

from src.scenarios.evaluation.tidb.system_failure.lock_contention import (
    TidbSystemFailureLockContentionForAdmissionEventsRowLockDeadlockEvaluatorCase,
    TidbSystemFailureLockContentionFocusedEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureLockContentionCase(TiDBScenarioCase):
    database: str
    table: str
    decoy_tables: tuple[str, ...]
    same_table_decoy_routes: tuple[tuple[int, str], ...]
    lock_row_id: int
    expected_amount: str
    minimum_other_lock_waits: int


class TidbSystemFailureLockContentionForAdmissionEventsRowLockDeadlockScenarioCase(
    TidbSystemFailureLockContentionCase
):
    pass


_SF04_TARGET_EVENT_TYPES = "'checkout_pending','checkout_completed','checkout_committed','reconciliation_pending'"
_SF04_DECOY_EVENT_TYPES = "'shadow_pending','shadow_completed','checkout_committed'"


_CASE = TidbSystemFailureLockContentionForAdmissionEventsRowLockDeadlockScenarioCase(
    case_id="admission_events_row_lock_deadlock",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "The current checkout failure is a live pessimistic row lock wait, not a generic slow query; the affected target is benchops.admission_alt_events handle 1.",
                    "entity": "admission_events_row_lock_deadlock",
                    "evidence": [
                        "scripted diagnostic actions observed The current checkout failure is a live pessimistic row lock wait, not a generic slow query; the affected target is benchops.admission_alt_events handle 1."
                    ]
                },
                {
                    "type": "finding",
                    "factor": "The DATA_LOCK_WAITS chain identifies the active holding transaction and its session, and that session owns the target key lock.",
                    "entity": "admission_events_row_lock_deadlock",
                    "evidence": [
                        "scripted diagnostic actions observed The DATA_LOCK_WAITS chain identifies the active holding transaction and its session, and that session owns the target key lock."
                    ]
                },
                {
                    "type": "finding",
                    "factor": "The affected business object is benchops.admission_alt_events handle 1 in schema benchops; same-table checkout-like waits on handles 17, 23, 42, 77, and 91 plus same-name schemas, account, and audit lock chains are unrelated traffic and must be separated by route and session correlation.",
                    "entity": "admission_events_row_lock_deadlock",
                    "evidence": [
                        "scripted diagnostic actions observed The affected business object is benchops.admission_alt_events handle 1 in schema benchops; same-table checkout-like waits on handles 17, 23, 42, 77, and 91 plus same-name schemas, account, and audit lock chains are unrelated traffic and must be separated by route and session correlation."
                    ]
                },
                {
                    "type": "finding",
                    "factor": "DEADLOCKS history contains completed historical transactions and must be separated from the current live blocker and waiter chain.",
                    "entity": "admission_events_row_lock_deadlock",
                    "evidence": [
                        "scripted diagnostic actions observed DEADLOCKS history contains completed historical transactions and must be separated from the current live blocker and waiter chain."
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "applied the case-specific remediation"
            ],
            "verification": [
                "verified the case-specific final state"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbSystemFailureLockContentionForAdmissionEventsRowLockDeadlockEvaluatorCase,
    title="Checkout writes stall amid mixed transactional activity.",
    alert=(
        "[P1] checkout-api 的订单确认写入延迟持续升高，部分请求未完成，但读取和其他业务流量仍可继续服务。"
        "同一 TiDB 集群还存在账户、审计、回放/归档校验、报表和监控活动，当前窗口同时有会话/事务活动与历史错误记录。"
        "请从当前运行时证据判断影响 checkout 的主要原因，区分当前业务路径、无关活动、同名对象和历史记录，"
        "只改变为恢复该业务路径所必需的状态，避免终止或修改无关会话和数据，并验证新的 checkout 写入可以完成。"
    ),
    initial_state={"status": "degraded", "lock": "active checkout write dependency"},
    expected_target={
        "status": "recovered",
        "lock": "target waiter committed",
        "amount": "80.19",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="sf04_checkout_event_detail",
                sql=(
                    "SELECT event_id, account_id, amount, event_type FROM "
                    "benchops.admission_alt_events WHERE event_id BETWEEN 2 AND 120 "
                    "ORDER BY event_id LIMIT 30"
                ),
                qps=0.16,
                tier="CRITICAL",
            ),
            WorkloadProfile(
                name="sf04_checkout_account_total",
                sql=(
                    "SELECT account_id, COUNT(*), SUM(amount) FROM benchops.admission_alt_events "
                    "WHERE account_id IN (3, 7, 11, 17, 23) GROUP BY account_id ORDER BY account_id"
                ),
                qps=0.12,
                tier="CRITICAL",
            ),
            WorkloadProfile(
                name="sf04_checkout_status_summary",
                sql=(
                    "SELECT event_type, COUNT(*), SUM(amount) FROM benchops.admission_alt_events "
                    "GROUP BY event_type ORDER BY event_type"
                ),
                qps=0.1,
                tier="CRITICAL",
            ),
            WorkloadProfile(
                name="sf04_checkout_event_account_join",
                sql=(
                    "SELECT e.event_id, e.amount, a.tier, a.region FROM benchops.admission_alt_events e "
                    "JOIN benchops.admission_alt_accounts a ON a.account_id=e.account_id "
                    "WHERE e.event_id BETWEEN 2 AND 100 ORDER BY e.event_id LIMIT 30"
                ),
                qps=0.12,
                tier="CRITICAL",
            ),
            WorkloadProfile(
                name="sf04_checkout_pending_scan",
                sql=(
                    "SELECT event_id, account_id, amount FROM benchops.admission_alt_events "
                    "WHERE event_type IN ('checkout_pending','reconciliation_pending') "
                    "ORDER BY event_id LIMIT 30"
                ),
                qps=0.1,
                tier="CRITICAL",
            ),
            WorkloadProfile(
                name="sf04_checkout_recent_events",
                sql=(
                    "SELECT event_id, event_type, amount FROM benchops.admission_alt_events "
                    "WHERE event_id BETWEEN 80 AND 150 ORDER BY event_id DESC LIMIT 25"
                ),
                qps=0.1,
                tier="CRITICAL",
            ),
            WorkloadProfile(
                name="sf04_account_profile",
                sql=(
                    "SELECT account_id, tier, region FROM benchops.admission_alt_accounts "
                    "WHERE account_id BETWEEN 1 AND 80 ORDER BY account_id LIMIT 30"
                ),
                qps=0.14,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_account_balance_dashboard",
                sql=(
                    "SELECT region, COUNT(*), SUM(balance) FROM benchops.admission_alt_accounts "
                    "GROUP BY region ORDER BY region"
                ),
                qps=0.1,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_account_tier_mix",
                sql=(
                    "SELECT tier, region, COUNT(*), AVG(balance) FROM benchops.admission_alt_accounts "
                    "GROUP BY tier, region ORDER BY tier, region"
                ),
                qps=0.1,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_account_top_balances",
                sql=(
                    "SELECT account_id, balance FROM benchops.admission_alt_accounts "
                    "ORDER BY balance DESC, account_id LIMIT 25"
                ),
                qps=0.1,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_audit_reconciliation",
                sql=(
                    "SELECT action, COUNT(*), MAX(created_at) FROM benchops.admission_alt_audit "
                    "WHERE event_id BETWEEN 1 AND 160 GROUP BY action ORDER BY action"
                ),
                qps=0.12,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_audit_recent",
                sql=(
                    "SELECT event_id, action, actor FROM benchops.admission_alt_audit "
                    "ORDER BY created_at DESC, audit_id DESC LIMIT 35"
                ),
                qps=0.1,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_audit_event_join",
                sql=(
                    "SELECT a.audit_id, a.event_id, e.event_type, a.action FROM benchops.admission_alt_audit a "
                    "JOIN benchops.admission_alt_events e ON e.event_id=a.event_id "
                    "WHERE a.event_id BETWEEN 1 AND 120 ORDER BY a.audit_id LIMIT 35"
                ),
                qps=0.1,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_audit_actor_summary",
                sql=(
                    "SELECT actor, action, COUNT(*) FROM benchops.admission_alt_audit "
                    "GROUP BY actor, action ORDER BY actor, action"
                ),
                qps=0.08,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_shadow_business_read",
                sql=(
                    "SELECT event_id, account_id, amount, event_type FROM benchops_shadow.admission_alt_events "
                    "ORDER BY event_id LIMIT 6"
                ),
                qps=0.1,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_replay_business_read",
                sql=(
                    "SELECT event_id, account_id, amount, event_type FROM benchops_replay.admission_alt_events "
                    "ORDER BY event_id LIMIT 6"
                ),
                qps=0.1,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_archive_business_read",
                sql=(
                    "SELECT event_id, account_id, amount, event_type FROM benchops_archive.admission_alt_events "
                    "ORDER BY event_id LIMIT 6"
                ),
                qps=0.1,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_canary_business_read",
                sql=(
                    "SELECT event_id, account_id, amount, event_type FROM benchops_canary.admission_alt_events "
                    "ORDER BY event_id LIMIT 6"
                ),
                qps=0.1,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_lock_wait_inventory",
                sql=(
                    "SELECT TRX_ID, CURRENT_HOLDING_TRX_ID, KEY_INFO "
                    "FROM INFORMATION_SCHEMA.DATA_LOCK_WAITS"
                ),
                qps=0.14,
                tier="MONITOR",
            ),
            WorkloadProfile(
                name="sf04_lock_inventory_by_table",
                sql=(
                    "SELECT KEY_INFO, COUNT(*) FROM INFORMATION_SCHEMA.DATA_LOCK_WAITS "
                    "GROUP BY KEY_INFO ORDER BY COUNT(*) DESC"
                ),
                qps=0.1,
                tier="MONITOR",
            ),
            WorkloadProfile(
                name="sf04_transaction_inventory",
                sql=(
                    "SELECT SESSION_ID, STATE, START_TIME "
                    "FROM INFORMATION_SCHEMA.CLUSTER_TIDB_TRX "
                    "ORDER BY START_TIME LIMIT 60"
                ),
                qps=0.12,
                tier="MONITOR",
            ),
            WorkloadProfile(
                name="sf04_deadlock_history",
                sql=(
                    "SELECT DEADLOCK_ID, OCCUR_TIME, TRY_LOCK_TRX_ID, KEY_INFO, TRX_HOLDING_LOCK "
                    "FROM INFORMATION_SCHEMA.DEADLOCKS "
                    "ORDER BY OCCUR_TIME DESC LIMIT 30"
                ),
                qps=0.12,
                tier="MONITOR",
            ),
            WorkloadProfile(
                name="sf04_active_process_inventory",
                sql=(
                    "SELECT ID, DB, COMMAND, TIME, STATE, INFO FROM INFORMATION_SCHEMA.PROCESSLIST "
                    "WHERE INFO IS NOT NULL ORDER BY TIME DESC LIMIT 80"
                ),
                qps=0.12,
                tier="MONITOR",
            ),
            WorkloadProfile(
                name="sf04_lock_process_correlation",
                sql=(
                    "SELECT ID, DB, STATE, INFO FROM INFORMATION_SCHEMA.PROCESSLIST "
                    "WHERE INFO LIKE '%admission_alt_events%' ORDER BY ID"
                ),
                qps=0.1,
                tier="MONITOR",
            ),
            WorkloadProfile(
                name="sf04_table_catalog_inventory",
                sql=(
                    "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES "
                    "WHERE TABLE_NAME LIKE 'admission_alt_%' ORDER BY TABLE_SCHEMA, TABLE_NAME"
                ),
                qps=0.08,
                tier="MONITOR",
            ),
            WorkloadProfile(
                name="sf04_target_key_read",
                sql=(
                    "SELECT event_id, account_id, amount, event_type FROM benchops.admission_alt_events "
                    "WHERE event_id=1"
                ),
                qps=0.1,
                tier="CRITICAL",
            ),
            WorkloadProfile(
                name="sf04_target_neighbor_read",
                sql=(
                    "SELECT event_id, account_id, amount, event_type FROM benchops.admission_alt_events "
                    "WHERE event_id=17"
                ),
                qps=0.08,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="sf04_reconciliation_summary",
                sql=(
                    "SELECT COUNT(*), SUM(amount), MIN(event_id), MAX(event_id) "
                    "FROM benchops.admission_alt_events WHERE event_id BETWEEN 1 AND 240"
                ),
                qps=0.08,
                tier="LIGHT",
            ),
        ),
        worker_count=4,
        seed=20260731,
        warmup_seconds=12,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.842857,
        reference_run_ids=(
            "tidb_system_failure_lock_contention__admission_events_row_lock_deadlock__mock__r001",
        ),
    ),
    runtime=tidb_runtime(release=TIDB_V8_1_0, pd_count=3, tikv_count=3, tidb_count=2),
    database="benchops",
    table="benchops.admission_alt_events",
    decoy_tables=(
        "benchops.admission_alt_accounts",
        "benchops.admission_alt_audit",
        "benchops_shadow.admission_alt_events",
        "benchops_replay.admission_alt_events",
        "benchops_archive.admission_alt_events",
        "benchops_canary.admission_alt_events",
    ),
    same_table_decoy_routes=(
        (17, "app=checkout-api route=reconciliation"),
        (23, "app=checkout-api route=retry"),
        (42, "app=settlement-worker route=repair"),
        (77, "app=checkout-api route=shadow-confirm"),
        (91, "app=checkout-api route=retry-shadow"),
    ),
    lock_row_id=1,
    expected_amount="80.19",
    minimum_other_lock_waits=22,
)


_FOCUSED_LOCK_WORKLOAD = replace(
    _CASE.background_workload,
    profiles=tuple(
        profile
        for profile in _CASE.background_workload.profiles
        if profile.name in {
            "sf04_checkout_event_detail",
            "sf04_checkout_pending_scan",
            "sf04_shadow_business_read",
            "sf04_replay_business_read",
            "sf04_archive_business_read",
            "sf04_canary_business_read",
            "sf04_lock_wait_inventory",
            "sf04_transaction_inventory",
            "sf04_deadlock_history",
            "sf04_active_process_inventory",
            "sf04_lock_process_correlation",
            "sf04_target_key_read",
            "sf04_target_neighbor_read",
        }
    ),
    worker_count=3,
    warmup_seconds=8,
)

_FOCUSED_CASE = replace(
    _CASE,
    case_id="checkout_row_lock_simple",
    case_no=1,
    evaluator=TidbSystemFailureLockContentionFocusedEvaluatorCase,
    alert=(
        "[P1] checkout-api 的订单确认写入延迟持续升高，部分请求未完成，但读取和其他业务流量仍可继续服务。"
        "同一 TiDB 集群还存在账户、审计、回放/归档校验、报表和监控活动，当前窗口同时有会话/事务活动与历史错误记录。"
        "请从当前运行时证据判断影响 checkout 的主要原因，区分当前业务路径、无关活动、同名对象和历史记录，"
        "只释放为恢复目标 checkout waiter 所必需的 holder，并用只读查询验证后台已有 waiter 的提交结果。"
        "不要执行额外的 INSERT、UPDATE、DELETE 或修改任何业务行；无关会话和数据必须保持不变。"
    ),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "The current checkout failure is a live pessimistic row lock wait, not a generic slow query; the affected target is benchops.admission_alt_events handle 1, and the DATA_LOCK_WAITS chain identifies the active holding transaction and its session that owns the target key lock.",
                    "entity": "checkout_row_lock_simple",
                    "evidence": ["current live DATA_LOCK_WAITS identifies the checkout target and its holder session"],
                },
                {
                    "type": "finding",
                    "factor": "Only the benchops checkout event handle 1 is in scope: same-table checkout-like waits on handles 17, 23, and 42 plus same-name schemas, account, and audit lock chains are unrelated traffic, and DEADLOCKS history contains completed historical transactions that must be separated from the current live blocker.",
                    "entity": "checkout_row_lock_simple",
                    "evidence": ["business rows, process routes, and deadlock history separate the target from focused decoys"],
                },
            ]
        },
        "outcome": {
            "changes": ["released only the holding transaction for the target business key"],
            "verification": [
                "the target waiter committed",
                "focused non-target lock waits and same-name decoys remain untouched",
            ],
        },
        "summary": "The focused reference released the exact checkout blocker and preserved unrelated lock chains.",
    },
    background_workload=_FOCUSED_LOCK_WORKLOAD,
    minimum_other_lock_waits=18,
    same_table_decoy_routes=(
        (17, "app=checkout-api route=reconciliation"),
        (23, "app=checkout-api route=retry"),
        (42, "app=settlement-worker route=repair"),
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.910256,
        reference_run_ids=(
            "reference-81__"
            "tidb_system_failure_lock_contention__checkout_row_lock_simple__mock__r001",
        ),
    ),
)


@dataclass(slots=True)
class _LockPair:
    table: str
    row_id: int
    holder_thread: threading.Thread | None = None
    waiter_thread: threading.Thread | None = None
    holder_conn: object | None = None
    waiter_conn: object | None = None
    holder_session_id: int | None = None
    waiter_session_id: int | None = None
    holder_error: Exception | None = None
    waiter_error: Exception | None = None
    holder_ready: threading.Event = field(default_factory=threading.Event)
    waiter_started: threading.Event = field(default_factory=threading.Event)

class TidbSystemFailureLockContentionInjector(BaseFaultInjector):
    """Hold several real business lock chains while one checkout chain is actionable."""

    def __init__(self):
        self.env = None
        self.database = None
        self.table = None
        self.decoy_tables = ()
        self.same_table_decoy_routes = ()
        self.lock_row_id = None
        self.expected_amount = None
        self._stop_event = None
        self._target_pair = None
        self._shadow_pair = None
        self._pairs = []
        self._deadlock_errors = ()

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._setup_business_tables()
        self._deadlock_errors = ()
        self._create_deadlock_record(self.table, 3, 4)
        self._create_deadlock_record(self.decoy_tables[3], 2, 3)
        self._start_runtime_pairs()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_business_tables()
        self._deadlock_errors = ()
        self._create_deadlock_record(self.table, 3, 4)
        self._create_deadlock_record(self.decoy_tables[3], 2, 3)
        self._start_runtime_pairs()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        waits = self._wait_rows()
        target_waits = [
            row for row in waits
            if self._matches_key_info(row, self.database, self._table_name(self.table))
        ]
        shadow_waits = [
            row for row in waits
            if self._matches_key_info(row, "benchops_shadow", "admission_alt_events")
        ]
        if not target_waits or len(shadow_waits) < 1 or len(waits) < len(self._pairs):
            raise RuntimeError(
                f"SF04 lock waits were not fully observable: target={target_waits!r}, "
                f"shadow={shadow_waits!r}, pair_count={len(self._pairs)}, waits={waits!r}"
            )
        return {
            "database": self.database,
            "target_table": self.table,
            "decoy_tables": list(self.decoy_tables),
            "target_row_id": self.lock_row_id,
            "expected_amount": self.expected_amount,
            "holder_session_id": self._target_pair.holder_session_id,
            "waiter_session_id": self._target_pair.waiter_session_id,
            "shadow_holder_session_id": self._shadow_pair.holder_session_id,
            "shadow_waiter_session_id": self._shadow_pair.waiter_session_id,
            "observed_wait_count": len(waits),
            "target_wait_count": len(target_waits),
            "shadow_wait_count": len(shadow_waits),
            "live_pair_count": len(self._pairs),
            "other_wait_count": len(waits) - len(target_waits),
            "decoy_holder_session_ids": [
                pair.holder_session_id
                for pair in self._pairs[1:]
            ],
            "deadlock_noise_count": len(self._deadlock_errors),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime(context)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime(context)

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.database = validate_sql_identifier(str(config["database"]), "database")
        self.table = str(config["table"])
        self.decoy_tables = tuple(str(item) for item in config["decoy_tables"])
        self.same_table_decoy_routes = tuple(
            (int(item[0]), str(item[1]))
            for item in config["same_table_decoy_routes"]
        )
        self.lock_row_id = int(config["lock_row_id"])
        self.expected_amount = str(config["expected_amount"])

    def _setup_business_tables(self) -> None:
        qualified_tables = (self.table, *self.decoy_tables)
        schemas = tuple(dict.fromkeys(
            validate_sql_identifier(table.split(".", 1)[0], "table schema")
            for table in qualified_tables
        ))
        for schema in schemas:
            require_sql_success(
                self.env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {schema}"),
                f"create SF04 database {schema}",
            )
        for table in qualified_tables:
            require_sql_success(
                self.env.execute_sql(f"DROP TABLE IF EXISTS {table}"),
                f"clear SF04 table {table}",
            )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {self.table} ("
                "event_id BIGINT PRIMARY KEY, account_id BIGINT NOT NULL, "
                f"amount DECIMAL(10,2) NOT NULL, event_type ENUM({_SF04_TARGET_EVENT_TYPES}) NOT NULL, "
                "payload VARCHAR(128) NOT NULL)"
            ),
            f"create SF04 target table {self.table}",
        )
        values = ",".join(
            f"({event_id},{event_id % 17},{'79.19' if event_id == 1 else '12.50'},"
            f"'{'checkout_pending' if event_id == 1 else 'checkout_completed'}',"
            f"'sf04-event-{event_id}')"
            for event_id in range(1, 241)
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {self.table} "
                "(event_id,account_id,amount,event_type,payload) VALUES "
                f"{values}"
            ),
            f"load SF04 target table {self.table}",
        )
        accounts, audit, shadow, replay, archive, canary = self.decoy_tables
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {accounts} (account_id BIGINT PRIMARY KEY, tier VARCHAR(16) NOT NULL, "
                "region VARCHAR(16) NOT NULL, balance DECIMAL(12,2) NOT NULL)"
            ),
            f"create SF04 account table {accounts}",
        )
        account_values = ",".join(
            f"({account_id},'{'gold' if account_id % 3 == 0 else 'standard'}',"
            f"'region-{account_id % 5}',{account_id * 19}.25)"
            for account_id in range(1, 161)
        )
        require_sql_success(
            self.env.execute_sql(f"INSERT INTO {accounts} VALUES {account_values}"),
            f"load SF04 account table {accounts}",
        )
        require_sql_success(
            self.env.execute_sql(
                f"CREATE TABLE {audit} (audit_id BIGINT PRIMARY KEY, event_id BIGINT NOT NULL, "
                "action VARCHAR(32) NOT NULL, actor VARCHAR(32) NOT NULL, created_at DATETIME NOT NULL)"
            ),
            f"create SF04 audit table {audit}",
        )
        audit_values = ",".join(
            f"({audit_id},{audit_id % 120 + 1},'{'settled' if audit_id % 2 else 'reviewed'}',"
            f"'worker-{audit_id % 7}','2026-07-31 00:{audit_id // 60:02d}:{audit_id % 60:02d}')"
            for audit_id in range(1, 361)
        )
        require_sql_success(
            self.env.execute_sql(f"INSERT INTO {audit} VALUES {audit_values}"),
            f"load SF04 audit table {audit}",
        )
        for index, table in enumerate((shadow, replay, archive, canary), start=1):
            require_sql_success(
                self.env.execute_sql(
                    f"CREATE TABLE {table} ("
                    "event_id BIGINT PRIMARY KEY, account_id BIGINT NOT NULL, "
                    f"amount DECIMAL(10,2) NOT NULL, event_type ENUM({_SF04_DECOY_EVENT_TYPES}) NOT NULL, "
                    "payload VARCHAR(128) NOT NULL)"
                ),
                f"create SF04 decoy event table {table}",
            )
            values = ",".join(
                f"({event_id},{index * 1000 + event_id},{40 + index + event_id / 100:.2f},"
                f"'{'shadow_pending' if event_id == 1 else 'shadow_completed'}',"
                f"'sf04-decoy-{index}-{event_id}')"
                for event_id in range(1, 7)
            )
            require_sql_success(
                self.env.execute_sql(
                    f"INSERT INTO {table} "
                    "(event_id,account_id,amount,event_type,payload) VALUES "
                    f"{values}"
                ),
                f"load SF04 decoy event table {table}",
            )

    def _verify_business_tables(self) -> None:
        for table, expected_rows in (
            (self.table, 240),
            *((table, 6) for table in self.decoy_tables[2:]),
        ):
            payload = json_object(
                self.env.execute_sql(f"SELECT COUNT(*) FROM {table}"),
                f"verify SF04 table {table}",
            )
            if payload["result"] != [[expected_rows]]:
                raise RuntimeError(
                    f"SF04 table row count changed before activate: table={table!r}, "
                    f"expected_rows={expected_rows}, result={payload['result']!r}"
                )

    def _connection(self):
        return connect_tidb(
            self.env,
            autocommit=False,
            read_timeout=960,
            write_timeout=960,
        )

    def _start_runtime_pairs(self) -> None:
        self._stop_event = threading.Event()
        accounts, audit, shadow, replay, archive, canary = self.decoy_tables
        self._pairs = [
            self._start_lock_pair(
                self.table,
                self.lock_row_id,
                f"UPDATE /* app=checkout-api route=confirm */ {self.table} "
                "SET amount=amount+1.00, event_type='checkout_committed' "
                f"WHERE event_id={self.lock_row_id}",
                "sf04-target-lock-holder",
                "sf04-target-lock-waiter",
                process_tag="app=checkout-api route=confirm",
            ),
            *(
                self._start_lock_pair(
                    self.table,
                    row_id,
                    f"UPDATE /* {route} */ {self.table} "
                    "SET amount=amount+0.07, event_type='checkout_committed' "
                    f"WHERE event_id={row_id}",
                    f"sf04-same-table-{row_id}-holder",
                    f"sf04-same-table-{row_id}-waiter",
                    process_tag=route,
                )
                for row_id, route in self.same_table_decoy_routes
            ),
            self._start_lock_pair(
                accounts,
                3,
                f"UPDATE {accounts} SET balance=balance+0.01 WHERE account_id=3",
                "sf04-account-holder",
                "sf04-account-waiter",
                key_column="account_id",
                process_tag="app=account-service route=balance",
            ),
            self._start_lock_pair(
                audit,
                1,
                f"UPDATE {audit} SET action='reviewed' WHERE audit_id=1",
                "sf04-audit-holder",
                "sf04-audit-waiter",
                key_column="audit_id",
                process_tag="app=audit-worker route=reconcile",
            ),
            self._start_lock_pair(
                shadow,
                self.lock_row_id,
                f"UPDATE {shadow} SET amount=amount WHERE event_id={self.lock_row_id}",
                "sf04-shadow-lock-holder",
                "sf04-shadow-lock-waiter",
                process_tag="app=shadow-service route=confirm",
            ),
            self._start_lock_pair(
                replay,
                self.lock_row_id,
                f"UPDATE {replay} SET amount=amount+1.00, event_type='checkout_committed' "
                f"WHERE event_id={self.lock_row_id}",
                "sf04-replay-lock-holder",
                "sf04-replay-lock-waiter",
                process_tag="app=replay-service route=confirm",
            ),
            self._start_lock_pair(
                archive,
                self.lock_row_id,
                f"UPDATE {archive} SET amount=amount+1.00, event_type='checkout_committed' "
                f"WHERE event_id={self.lock_row_id}",
                "sf04-archive-lock-holder",
                "sf04-archive-lock-waiter",
                process_tag="app=archive-service route=confirm",
            ),
            self._start_lock_pair(
                canary,
                self.lock_row_id,
                f"UPDATE {canary} SET amount=amount+1.00, event_type='checkout_committed' "
                f"WHERE event_id={self.lock_row_id}",
                "sf04-canary-lock-holder",
                "sf04-canary-lock-waiter",
                process_tag="app=canary-service route=confirm",
            ),
        ]
        self._target_pair = self._pairs[0]
        self._shadow_pair = next(pair for pair in self._pairs if pair.table == shadow)

    def _start_lock_pair(
        self,
        table: str,
        row_id: int,
        waiter_sql: str,
        holder_name: str,
        waiter_name: str,
        *,
        key_column: str = "event_id",
        process_tag: str,
    ) -> _LockPair:
        pair = _LockPair(table=table, row_id=row_id)

        def hold() -> None:
            conn = None
            try:
                conn = self._connection()
                pair.holder_conn = conn
                pair.holder_session_id = conn.thread_id()
                with conn.cursor() as cur:
                    cur.execute("BEGIN PESSIMISTIC")
                    cur.execute(
                        f"UPDATE /* {process_tag} */ {table} "
                        f"SET {key_column}={key_column} WHERE {key_column}={row_id}"
                    )
                pair.holder_ready.set()
                while not self._stop_event.wait(1):
                    with conn.cursor() as cur:
                        cur.execute(f"SELECT /* {process_tag} */ SLEEP(2)")
            except Exception as exc:
                pair.holder_error = exc
                pair.holder_ready.set()
            finally:
                if conn is not None:
                    conn.close()
                pair.holder_conn = None

        def wait_for_lock() -> None:
            conn = None
            try:
                pair.holder_ready.wait(10)
                conn = self._connection()
                pair.waiter_conn = conn
                pair.waiter_session_id = conn.thread_id()
                pair.waiter_started.set()
                with conn.cursor() as cur:
                    cur.execute("SET SESSION innodb_lock_wait_timeout=900")
                    cur.execute("BEGIN PESSIMISTIC")
                    cur.execute(waiter_sql)
                conn.commit()
            except Exception as exc:
                pair.waiter_error = exc
                pair.waiter_started.set()
            finally:
                if conn is not None:
                    conn.close()
                pair.waiter_conn = None

        pair.holder_thread = threading.Thread(target=hold, name=holder_name, daemon=True)
        pair.waiter_thread = threading.Thread(target=wait_for_lock, name=waiter_name, daemon=True)
        pair.holder_thread.start()
        pair.holder_ready.wait(10)
        if pair.holder_error is not None:
            raise RuntimeError(
                f"SF04 failed to acquire lock: table={table!r}, row_id={row_id}, "
                f"error={pair.holder_error!r}"
            )
        pair.waiter_thread.start()
        pair.waiter_started.wait(10)
        if pair.waiter_error is not None:
            raise RuntimeError(
                f"SF04 failed to start waiter: table={table!r}, row_id={row_id}, "
                f"error={pair.waiter_error!r}"
            )
        return pair

    @staticmethod
    def _table_name(qualified_table: str) -> str:
        return qualified_table.split(".", 1)[1]

    def _matches_key_info(self, row: list, database: str, table: str) -> bool:
        if len(row) < 2:
            raise ValueError(f"SF04 DATA_LOCK_WAITS row lacks KEY_INFO: row={row!r}")
        info = json.loads(row[1])
        if not isinstance(info, dict):
            raise TypeError(f"SF04 KEY_INFO must decode to an object: key_info={row[1]!r}")
        return (
            info["db_name"] == database
            and info["table_name"] == table
            and info["handle_value"] == str(self.lock_row_id)
        )

    def _wait_rows(self) -> list:
        deadline = time.monotonic() + 15
        last_rows = []
        while time.monotonic() < deadline:
            payload = json_object(
                self.env.execute_sql("SELECT * FROM INFORMATION_SCHEMA.DATA_LOCK_WAITS"),
                "observe SF04 lock waits",
            )
            last_rows = payload["result"]
            if last_rows:
                return last_rows
            time.sleep(0.25)
        return last_rows

    def _create_deadlock_record(self, table: str, first_id: int, second_id: int) -> None:
        barrier = threading.Barrier(2, timeout=15)
        errors = []

        def transact(first_id: int, second_id: int) -> None:
            conn = None
            try:
                conn = self._connection()
                with conn.cursor() as cur:
                    cur.execute("SET SESSION innodb_lock_wait_timeout=15")
                    cur.execute("BEGIN PESSIMISTIC")
                    cur.execute(f"UPDATE {table} SET amount=amount+0.01 WHERE event_id={first_id}")
                    barrier.wait()
                    cur.execute(f"UPDATE {table} SET amount=amount+0.01 WHERE event_id={second_id}")
                    conn.commit()
            except Exception as exc:
                errors.append(str(exc))
                if conn is not None:
                    conn.rollback()
            finally:
                if conn is not None:
                    conn.close()

        first = threading.Thread(target=transact, args=(3, 4), name="sf04-deadlock-a", daemon=True)
        second = threading.Thread(target=transact, args=(4, 3), name="sf04-deadlock-b", daemon=True)
        first.start()
        second.start()
        join_thread(first, 35, "SF04 deadlock transaction A")
        join_thread(second, 35, "SF04 deadlock transaction B")
        if not errors:
            raise RuntimeError(
                f"SF04 deadlock noise did not produce a transaction error: "
                f"table={table!r}, first_id={first_id}, second_id={second_id}"
            )
        self._deadlock_errors += tuple(errors)

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
        steps = []
        for pair in self._pairs:
            if pair.waiter_thread is not None and pair.waiter_thread.is_alive():
                steps.append(
                    (
                        f"terminate SF04 {pair.table}#{pair.row_id} lock waiter",
                        lambda pair=pair: require_sql_success(
                            self.env.execute_sql(f"KILL TIDB {pair.waiter_session_id}"),
                            f"terminate SF04 lock waiter session {pair.waiter_session_id} "
                            f"for {pair.table}#{pair.row_id}",
                        ),
                    )
                )
        for pair in self._pairs:
            if pair.holder_thread is not None:
                steps.append(
                    (
                        f"join SF04 {pair.table}#{pair.row_id} lock holder",
                        lambda pair=pair: join_thread(
                            pair.holder_thread, 5, f"SF04 lock holder {pair.table}#{pair.row_id}"
                        ),
                    )
                )
            if pair.waiter_thread is not None:
                steps.append(
                    (
                        f"join SF04 {pair.table}#{pair.row_id} lock waiter",
                        lambda pair=pair: join_thread(
                            pair.waiter_thread, 5, f"SF04 lock waiter {pair.table}#{pair.row_id}"
                        ),
                    )
                )
        run_cleanup_steps(f"SF04 lock contention cleanup for {context.run_id}", steps)
        self._target_pair = None
        self._shadow_pair = None
        self._pairs = []
        self._stop_event = None


class TidbSystemFailureLockContentionScenario(TiDBScenario):
    scenario_id = "tidb_system_failure_lock_contention"
    description = "Investigates a TiDB checkout write-path incident amid mixed transactional activity."
    cases = (_CASE, _FOCUSED_CASE)

    def build_fault_plan(
        self, case: TidbSystemFailureLockContentionCase
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureLockContentionInjector,
                config={
                    "database": case.database,
                    "table": case.table,
                    "decoy_tables": case.decoy_tables,
                    "same_table_decoy_routes": case.same_table_decoy_routes,
                    "lock_row_id": case.lock_row_id,
                    "expected_amount": case.expected_amount,
                },
            ),
        )
