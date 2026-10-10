from collections.abc import Mapping
from dataclasses import dataclass, replace
import threading

from src.scenarios.evaluation.tidb.system_failure.deadlock import (
    TidbSystemFailureDeadlockForWalletPairReverseOrderDeadlockEvaluatorCase,
    TidbSystemFailureDeadlockFocusedEvaluatorCase,
)
from src.scenarios.base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
)
from src.scenarios.workloads import WorkloadProfile
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.tidb.common import (
    connect_tidb,
    join_thread,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)

from ...base import FaultPlan, TiDBScenario, TiDBScenarioCase
from ..runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureDeadlockCase(TiDBScenarioCase):
    account_table: str
    job_table: str
    attempt_table: str
    receipt_table: str
    reconciliation_table: str
    dispatch_table: str
    ledger_table: str
    batch_id: str
    from_account_id: int
    to_account_id: int
    amount: int
    from_initial_balance: int
    to_initial_balance: int
    decoy_account_ids: tuple[int, ...]
    decoy_job_count: int
    deadlock_decoy_specs: tuple[tuple[str, int, int, str, int], ...]
    slow_queries: tuple[str, ...]
    from_expected_balance: int
    to_expected_balance: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureDeadlockForWalletPairReverseOrderDeadlockScenarioCase(TidbSystemFailureDeadlockCase):
    pass


ACCOUNT_TABLE = "sf05_accounts"
JOB_TABLE = "sf05_transfer_jobs"
ATTEMPT_TABLE = "sf05_transfer_attempts"
RECONCILIATION_TABLE = "sf05_settlement_reconciliation"
DISPATCH_TABLE = "sf05_settlement_dispatch"
LEDGER_TABLE = "sf05_settlement_ledger"
DECOY_SEED_JOB_COUNT = 24
COMPETING_BATCH_ID = "settlement-20260808-045"
COMPETING_FROM_ACCOUNT_ID = 101
COMPETING_TO_ACCOUNT_ID = 202
COMPETING_AMOUNT = 30
DEADLOCK_DECOY_SPECS = (
    ("settlement-20260808-001", 301, 302, "needs_retry", 7),
    ("settlement-20260808-003", 401, 402, "manual_review", 7),
    ("settlement-20260808-005", 501, 502, "settled", 7),
    ("settlement-20260808-025", 101, 202, "settled", 2),
    ("settlement-20260808-026", 202, 101, "manual_review", 1),
    ("settlement-20260808-027", 101, 202, "needs_retry", 55),
    ("settlement-20260808-043", 101, 202, "needs_retry", 2),
    ("settlement-20260808-044", 202, 101, "needs_retry", 1),
)


def build_tidb_deadlock_noise_profiles(
    *,
    account_table: str = ACCOUNT_TABLE,
    job_table: str = JOB_TABLE,
    attempt_table: str = ATTEMPT_TABLE,
) -> list[WorkloadProfile]:
    return [
        WorkloadProfile(
            name="sf05_wallet_pool_rollup",
            sql=(
                "SELECT lock_group, count(*) AS accounts, sum(balance) AS total_balance "
                f"FROM {account_table} "
                "GROUP BY lock_group "
                "ORDER BY total_balance DESC, lock_group"
            ),
            qps=0.70,
            tier="TIDB_SF05_ROLLUP",
            application_name="wallet-dashboard-rollup",
        ),
        WorkloadProfile(
            name="sf05_retry_queue_status_probe",
            sql=(
                "SELECT status, count(*) AS jobs, max(updated_at) AS newest_job "
                f"FROM {job_table} "
                "GROUP BY status "
                "ORDER BY jobs DESC, status"
            ),
            qps=0.65,
            tier="TIDB_SF05_QUEUE",
            application_name="settlement-retry-monitor",
        ),
        WorkloadProfile(
            name="sf05_attempt_error_digest_rollup",
            sql=(
                "SELECT left(error_code, 8) AS error_prefix, count(*) AS attempts "
                f"FROM {attempt_table} "
                "GROUP BY error_prefix "
                "ORDER BY attempts DESC, error_prefix"
            ),
            qps=0.55,
            tier="TIDB_SF05_ATTEMPTS",
            application_name="attempt-digest-exporter",
        ),
        WorkloadProfile(
            name="sf05_same_domain_pair_touch",
            sql=(
                f"UPDATE {account_table} "
                "SET balance = balance "
                "WHERE account_id IN (301, 302)"
            ),
            qps=0.55,
            tier="TIDB_SF05_DML_NOISE",
            commit=False,
            application_name="wallet-api-ledger-touch",
        ),
        WorkloadProfile(
            name="sf05_slow_receipt_probe",
            sql=(
                "SELECT SLEEP(0.35), count(*) AS pending_receipts "
                f"FROM {job_table} "
                "WHERE status IN ('needs_retry', 'manual_review')"
            ),
            qps=0.40,
            tier="TIDB_SF05_SLOW_NOISE",
            application_name="receipt-latency-probe",
        ),
        WorkloadProfile(
            name="sf05_missing_cache_probe",
            sql="SELECT count(*) FROM settlement_cache_missing",
            qps=0.25,
            tier="TIDB_SF05_LOG_NOISE",
            application_name="settlement-cache-refresh",
        ),
    ]


_TIDB_SYSTEM_FAILURE_DEADLOCK_CASE = TidbSystemFailureDeadlockForWalletPairReverseOrderDeadlockScenarioCase(
    case_id="wallet_pair_reverse_order_deadlock",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "tidb pessimistic transaction deadlock",
                    "entity": "settlement-20260808-042",
                    "evidence": [
                        "deadlock history contains a mutual lock cycle with TiDB error 1213"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "current retry candidate is settlement-20260808-042 for wallet accounts 101 and 202",
                    "entity": "settlement-20260808-042",
                    "evidence": [
                        "the current needs_retry job and current attempt rows map the business batch to accounts 101 and 202"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "target pair has current ERROR 1213 attempts while older 9007 and LOCK_WAIT_TIMEOUT rows are historical",
                    "entity": "settlement-20260808-042",
                    "evidence": [
                        "attempt timestamps and job status separate the current 1213 from older target-pair failures"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the settlement workload has multiple current retry batches for the 101-to-202 wallet pair, but settlement-20260808-042 is the incomplete 70-unit customer incident rather than the separate 30-unit replay",
                    "entity": "settlement-20260808-042",
                    "evidence": [
                        "job, account pair, amount, receipt and observed_at values distinguish the 70-unit customer incident from the newer 30-unit retry event"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the pending 70-unit settlement receipt links the current wallet incident to settlement-20260808-042, while the separate 30-unit 045 receipt belongs to a replay candidate",
                    "entity": "settlement-20260808-042",
                    "evidence": [
                        "receipt state, account pair, amount and batch_id distinguish the customer incident from the newer replay event"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the settlement reconciliation control marks settlement-20260808-042 open and the separate current batch settlement-20260808-045 duplicate_hold",
                    "entity": "settlement-20260808-042",
                    "evidence": [
                        "the control record joins the alert's open reconciliation item to the 101-to-202 job, receipt, and attempt rows"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the settlement dispatch queue assigns settlement-20260808-042 to the active customer incident and marks settlement-20260808-045 as a suppressed replay",
                    "entity": "settlement-20260808-042",
                    "evidence": [
                        "dispatch state, incident key, account pair, amount and batch_id associate the alert with 042 rather than the newer 30-unit suppressed replay"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "the target settlement ledger has an applied debit for account 101 and a pending credit for account 202, so recovery must not repeat the debit",
                    "entity": "settlement-20260808-042",
                    "evidence": [
                        "ledger entry state and account balance show that only the 202 credit leg remains pending"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "two settlement transactions lock wallet accounts in opposite primary-key order",
                    "entity": "settlement-20260808-042",
                    "evidence": [
                        "the two current attempt rows show 101-to-202 and 202-to-101 acquisition order"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "deadlock transactions are already rolled back; no persistent blocker or TiKV outage",
                    "entity": "settlement-20260808-042",
                    "evidence": [
                        "data_lock_waits is empty after the victim rollback and cluster health remains available"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "completed the pending credit leg for settlement batch settlement-20260808-042 with accounts locked in ascending primary-key order without repeating the applied debit"
            ],
            "verification": [
                "verified both wallet balances, target ledger completion, retry queue status, and remaining noise jobs"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbSystemFailureDeadlockForWalletPairReverseOrderDeadlockEvaluatorCase,
    title="A settlement batch remains incomplete amid concurrent wallet activity.",
    alert=(
        "告警：一批 settlement 业务操作未完成，部分账户状态和处理进度没有达到预期，但钱包查询仍可用。"
        "现场同时有 retry、manual-review、receipt-delivery、dispatch/replay、dashboard 和其他账户操作，部分结算回执延迟，历史事务错误也仍然可见。"
        "请从当前批次的事务、会话、业务表和组件证据判断是并发冲突、数据状态问题还是组件异常，"
        "完整恢复目标业务并避免重复或遗漏账户更新。不要删除或跳过业务更新，不要重启 TiDB，"
        "不要终止无关业务会话。"
    ),
    initial_state={
        "reported_service": "wallet settlement",
        "symptom": "an incomplete settlement while wallet queries remain available",
        "visible_activity": "same-domain retry, receipt, reconciliation, dispatch, transaction, dashboard, and account activity",
    },
    expected_target={
        "account_101_balance": 9930,
        "account_202_balance": 10070,
        "target_status": "completed",
        "decoy_jobs_preserved": True,
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(
            build_tidb_deadlock_noise_profiles(
                account_table=ACCOUNT_TABLE,
                job_table=JOB_TABLE,
                attempt_table=ATTEMPT_TABLE,
            )
        ),
        worker_count=6,
        seed=0x5F05,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=6.0,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.608831,
        reference_run_ids=(
            "reference-227__"
            "tidb_system_failure_deadlock__wallet_pair_reverse_order_deadlock__mock__r001",
        ),
    ),
    runtime=tidb_runtime(release=TIDB_V8_1_0, pd_count=3, tikv_count=3, tidb_count=2),
    account_table=ACCOUNT_TABLE,
    job_table=JOB_TABLE,
    attempt_table=ATTEMPT_TABLE,
    batch_id="settlement-20260808-042",
    from_account_id=101,
    to_account_id=202,
    amount=70,
    from_initial_balance=9930,
    to_initial_balance=10000,
    from_expected_balance=9930,
    to_expected_balance=10070,
    decoy_account_ids=(301, 302, 401, 402, 501, 502, 601, 602),
    decoy_job_count=30,
    receipt_table="sf05_settlement_receipts",
    reconciliation_table=RECONCILIATION_TABLE,
    dispatch_table=DISPATCH_TABLE,
    ledger_table=LEDGER_TABLE,
    deadlock_decoy_specs=DEADLOCK_DECOY_SPECS,
    slow_queries=(
        "SELECT status, count(*) AS jobs FROM sf05_transfer_jobs GROUP BY status",
        "SELECT SLEEP(0.35), count(*) FROM sf05_transfer_jobs WHERE status IN ('needs_retry', 'manual_review')",
        "UPDATE sf05_accounts SET balance = balance WHERE account_id IN (301, 302)",
    ),
)


_FOCUSED_DEADLOCK_WORKLOAD = replace(
    _TIDB_SYSTEM_FAILURE_DEADLOCK_CASE.background_workload,
    profiles=tuple(build_tidb_deadlock_noise_profiles()[:5]),
    worker_count=4,
    warmup_seconds=4.0,
)

_FOCUSED_DEADLOCK_CASE = replace(
    _TIDB_SYSTEM_FAILURE_DEADLOCK_CASE,
    case_id="wallet_pair_deadlock_simple",
    case_no=1,
    evaluator=TidbSystemFailureDeadlockFocusedEvaluatorCase,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": (
                        "current retry candidate is settlement-20260808-042 for wallet accounts 101 and 202: its "
                        "two settlement transactions lock the wallet rows in opposite primary-key order and form a "
                        "TiDB error 1213 pessimistic deadlock cycle that already rolled back the victim, so no "
                        "persistent blocker or TiKV outage remains"
                    ),
                    "entity": "wallet_pair_deadlock_simple",
                    "evidence": [
                        "information_schema.deadlocks shows the 101/202 AB-BA cycle and data_lock_waits is empty "
                        "after the victim rollback"
                    ],
                },
                {
                    "type": "finding",
                    "factor": (
                        "the target pair's older 9007 and LOCK_WAIT_TIMEOUT rows and the separate newer 30-unit "
                        "settlement-20260808-045 replay are not the repair target: only settlement-20260808-042's "
                        "ledger has an applied debit for account 101 and a pending credit for account 202, so "
                        "recovery must complete just the pending credit leg in ascending primary-key order without "
                        "repeating the debit"
                    ),
                    "entity": "wallet_pair_deadlock_simple",
                    "evidence": [
                        "target ledger rows show the 101 debit applied and only the 202 credit pending for batch 042"
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "completed the pending credit leg for settlement batch settlement-20260808-042 with accounts locked in ascending primary-key order without repeating the applied debit"
            ],
            "verification": [
                "verified both wallet balances, target ledger completion, retry queue status, and remaining noise jobs"
            ]
        },
        "summary": "The focused scripted mock completed the target wallet deadlock diagnosis and verification.",
    },
    background_workload=_FOCUSED_DEADLOCK_WORKLOAD,
    deadlock_decoy_specs=DEADLOCK_DECOY_SPECS[:4],
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.9453,
        reference_run_ids=(
            "tidb-reference-9__"
            "tidb_system_failure_deadlock__wallet_pair_deadlock_simple__mock__r001",
        ),
    ),
)


class TidbSystemFailureDeadlockInjector(BaseFaultInjector):
    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        print(f"[FaultInjector:TidbSystemFailureDeadlockInjector] Building SF05 tables in {context.run_id}...")
        self._setup_tables(context.env)
        self._create_real_deadlock(context.env)
        self._record_target_attempts(context.env)
        self._create_decoy_deadlocks(context.env)
        self._create_competing_deadlock(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_tables(context.env)
        self._create_real_deadlock(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        env = context.env
        deadlocks = json_object(
            env.execute_sql("SELECT * FROM information_schema.deadlocks ORDER BY occur_time DESC LIMIT 10"),
            "read TiDB deadlock history for SF05",
        )
        workload = json_object(
            env.observe_metric("workload_activity"),
            "read SF05 workload activity",
        )
        attempts = json_object(
            env.execute_sql(
                f"SELECT error_code, count(*) FROM {self.attempt_table} "
                "GROUP BY error_code ORDER BY count(*) DESC, error_code"
            ),
            "read SF05 attempt noise",
        )
        return {
            "sf05_deadlock_history_rows": len(deadlocks["result"]),
            "sf05_workload_profiles": workload["snapshot"]["active_profiles"],
            "sf05_attempt_error_groups": len(attempts["result"]),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        return None

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        for table in (
            self.ledger_table,
            self.dispatch_table,
            self.reconciliation_table,
            self.receipt_table,
            self.attempt_table,
            self.job_table,
            self.account_table,
        ):
            require_sql_success(
                context.env.execute_sql(f"DROP TABLE IF EXISTS {table}"),
                f"drop SF05 table {table}",
            )

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.account_table = validate_sql_identifier(str(config["account_table"]), "account_table")
        self.job_table = validate_sql_identifier(str(config["job_table"]), "job_table")
        self.attempt_table = validate_sql_identifier(str(config["attempt_table"]), "attempt_table")
        self.receipt_table = validate_sql_identifier(str(config["receipt_table"]), "receipt_table")
        self.reconciliation_table = validate_sql_identifier(
            str(config["reconciliation_table"]), "reconciliation_table"
        )
        self.dispatch_table = validate_sql_identifier(str(config["dispatch_table"]), "dispatch_table")
        self.ledger_table = validate_sql_identifier(str(config["ledger_table"]), "ledger_table")
        self.batch_id = str(config["batch_id"])
        self.from_account_id = int(config["from_account_id"])
        self.to_account_id = int(config["to_account_id"])
        self.amount = int(config["amount"])
        self.from_initial_balance = int(config["from_initial_balance"])
        self.to_initial_balance = int(config["to_initial_balance"])
        self.decoy_account_ids = tuple(int(value) for value in config["decoy_account_ids"])
        self.decoy_job_count = int(config["decoy_job_count"])
        self.deadlock_decoy_specs = tuple(
            (str(batch_id), int(first_id), int(second_id), str(status), int(age_minutes))
            for batch_id, first_id, second_id, status, age_minutes in config["deadlock_decoy_specs"]
        )
        self.env = env

    def _connection(self, env):
        return connect_tidb(
            env,
            autocommit=False,
        )

    def _setup_tables(self, env) -> None:
        for table in (
            self.ledger_table,
            self.dispatch_table,
            self.reconciliation_table,
            self.receipt_table,
            self.attempt_table,
            self.job_table,
            self.account_table,
        ):
            require_sql_success(env.execute_sql(f"DROP TABLE IF EXISTS {table}"), f"drop stale SF05 table {table}")
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.account_table} ("
                "account_id INT PRIMARY KEY, "
                "customer_id INT NOT NULL, "
                "lock_group VARCHAR(32) NOT NULL, "
                "balance INT NOT NULL, "
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            ),
            "create SF05 accounts table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.job_table} ("
                "batch_id VARCHAR(64) PRIMARY KEY, "
                "from_account_id INT NOT NULL, "
                "to_account_id INT NOT NULL, "
                "amount INT NOT NULL, "
                "status VARCHAR(32) NOT NULL, "
                "lock_order VARCHAR(64) NOT NULL, "
                "retry_strategy VARCHAR(64), "
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            ),
            "create SF05 jobs table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.attempt_table} ("
                "attempt_id INT AUTO_INCREMENT PRIMARY KEY, "
                "batch_id VARCHAR(64) NOT NULL, "
                "worker_id VARCHAR(64) NOT NULL, "
                "first_account_id INT NOT NULL, "
                "second_account_id INT NOT NULL, "
                "error_code VARCHAR(64) NOT NULL, "
                "final_state VARCHAR(64) NOT NULL, "
                "note VARCHAR(255), "
                "observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            ),
            "create SF05 attempts table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.receipt_table} ("
                "receipt_id VARCHAR(64) PRIMARY KEY, "
                "batch_id VARCHAR(64) NOT NULL, "
                "from_account_id INT NOT NULL, "
                "to_account_id INT NOT NULL, "
                "amount INT NOT NULL, "
                "receipt_state VARCHAR(32) NOT NULL, "
                "observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            ),
            "create SF05 settlement receipts table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.reconciliation_table} ("
                "reconciliation_id VARCHAR(64) PRIMARY KEY, "
                "batch_id VARCHAR(64) NOT NULL, "
                "from_account_id INT NOT NULL, "
                "to_account_id INT NOT NULL, "
                "amount INT NOT NULL, "
                "control_state VARCHAR(32) NOT NULL, "
                "source VARCHAR(64) NOT NULL, "
                "observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            ),
            "create SF05 settlement reconciliation table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.dispatch_table} ("
                "dispatch_id VARCHAR(64) PRIMARY KEY, "
                "incident_key VARCHAR(64) NOT NULL, "
                "batch_id VARCHAR(64) NOT NULL, "
                "from_account_id INT NOT NULL, "
                "to_account_id INT NOT NULL, "
                "amount INT NOT NULL, "
                "dispatch_state VARCHAR(32) NOT NULL, "
                "route VARCHAR(64) NOT NULL, "
                "observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            ),
            "create SF05 settlement dispatch table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.ledger_table} ("
                "ledger_entry_id VARCHAR(64) PRIMARY KEY, "
                "batch_id VARCHAR(64) NOT NULL, "
                "account_id INT NOT NULL, "
                "leg_type VARCHAR(16) NOT NULL, "
                "amount INT NOT NULL, "
                "entry_state VARCHAR(32) NOT NULL, "
                "ledger_reference VARCHAR(64) NOT NULL, "
                "observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            ),
            "create SF05 settlement ledger table",
        )
        self._seed_accounts(env)
        self._seed_jobs(env)
        self._seed_receipts(env)
        self._seed_reconciliation(env)
        self._seed_dispatch(env)
        self._seed_ledger(env)
        self._seed_attempt_noise(env)

    def _seed_accounts(self, env) -> None:
        rows = [
            (self.from_account_id, 7001, "target_wallet_pair", self.from_initial_balance),
            (self.to_account_id, 7002, "target_wallet_pair", self.to_initial_balance),
            (301, 7101, "receipt_decoy_pair", 5000),
            (302, 7102, "receipt_decoy_pair", 5100),
            (401, 7201, "manual_review_pair", 6100),
            (402, 7202, "manual_review_pair", 6200),
            (501, 7301, "dashboard_pair", 7300),
            (502, 7302, "dashboard_pair", 7400),
            (601, 7401, "replay_shadow_pair", 9000),
            (602, 7402, "replay_shadow_pair", 9100),
        ]
        values = ",".join(f"({account_id},{customer_id},'{lock_group}',{balance})" for account_id, customer_id, lock_group, balance in rows)
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.account_table} "
                "(account_id, customer_id, lock_group, balance) VALUES "
                f"{values}"
            ),
            "seed SF05 accounts",
        )

    def _seed_jobs(self, env) -> None:
        decoy_statuses = {batch_id: status for batch_id, _, _, status, _ in self.deadlock_decoy_specs}
        rows = [
            (
                self.batch_id,
                self.from_account_id,
                self.to_account_id,
                self.amount,
                "needs_retry",
                "reverse_observed",
                "none",
            )
        ]
        for index in range(1, DECOY_SEED_JOB_COUNT + 1):
            source = self.decoy_account_ids[(index - 1) % len(self.decoy_account_ids)]
            target = self.decoy_account_ids[index % len(self.decoy_account_ids)]
            batch_id = f"settlement-20260808-{index:03d}"
            status = decoy_statuses.get(
                batch_id,
                ("manual_review", "settled", "needs_receipt", "queued")[index % 4],
            )
            rows.append((batch_id, source, target, 3 + index, status, "mixed", "none"))
        existing_batch_ids = {row[0] for row in rows}
        for batch_id, first_id, second_id, status, _ in self.deadlock_decoy_specs:
            if batch_id not in existing_batch_ids:
                rows.append((batch_id, first_id, second_id, 20 + len(rows), status, "mixed", "none"))
        rows.append(
            (
                COMPETING_BATCH_ID,
                COMPETING_FROM_ACCOUNT_ID,
                COMPETING_TO_ACCOUNT_ID,
                COMPETING_AMOUNT,
                "needs_retry",
                "reverse_observed",
                "none",
            )
        )
        values = ",".join(
            "('" + batch_id + f"',{source},{target},{amount},'{status}','{lock_order}','{retry_strategy}',"
            f"{self._job_updated_at_sql(batch_id)})"
            for batch_id, source, target, amount, status, lock_order, retry_strategy in rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.job_table} "
                "(batch_id, from_account_id, to_account_id, amount, status, lock_order, retry_strategy, updated_at) "
                f"VALUES {values}"
            ),
            "seed SF05 transfer jobs",
        )

    def _job_updated_at_sql(self, batch_id: str) -> str:
        if batch_id == self.batch_id:
            return "CURRENT_TIMESTAMP - INTERVAL 8 MINUTE"
        if batch_id == COMPETING_BATCH_ID:
            return "CURRENT_TIMESTAMP - INTERVAL 1 MINUTE"
        for spec_batch_id, _, _, _, age_minutes in self.deadlock_decoy_specs:
            if batch_id == spec_batch_id:
                return f"CURRENT_TIMESTAMP - INTERVAL {age_minutes} MINUTE"
        return "CURRENT_TIMESTAMP - INTERVAL 2 HOUR"

    def _seed_attempt_noise(self, env) -> None:
        rows = []
        errors = ("LOCK_WAIT_TIMEOUT", "ERROR 9007", "OK", "RECEIPT_TIMEOUT", "MANUAL_REVIEW")
        for index in range(1, 73):
            source = self.decoy_account_ids[(index - 1) % len(self.decoy_account_ids)]
            target = self.decoy_account_ids[index % len(self.decoy_account_ids)]
            rows.append(
                (
                    f"settlement-20260808-{((index - 1) % DECOY_SEED_JOB_COUNT) + 1:03d}",
                    f"noise-worker-{index % 9}",
                    source,
                    target,
                    errors[index % len(errors)],
                    "noise_only",
                    "same-domain transfer activity",
                )
            )
        values = ",".join(
            f"('{batch_id}','{worker_id}',{first_id},{second_id},'{error_code}','{state}','{note}')"
            for batch_id, worker_id, first_id, second_id, error_code, state, note in rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.attempt_table} "
                "(batch_id, worker_id, first_account_id, second_account_id, error_code, final_state, note) "
                f"VALUES {values}"
            ),
            "seed SF05 attempt noise",
        )

    def _seed_receipts(self, env) -> None:
        rows = (
            ("receipt-20260808-042", self.batch_id, self.from_account_id, self.to_account_id, self.amount, "pending", 1),
            ("receipt-20260808-045", COMPETING_BATCH_ID, COMPETING_FROM_ACCOUNT_ID, COMPETING_TO_ACCOUNT_ID, COMPETING_AMOUNT, "pending", 1),
            ("receipt-20260808-025", "settlement-20260808-025", 101, 202, 35, "delivered", 2),
            ("receipt-20260808-026", "settlement-20260808-026", 202, 101, 25, "manual_review", 1),
            ("receipt-20260808-027", "settlement-20260808-027", 101, 202, 15, "delivered", 55),
            ("receipt-20260808-043", "settlement-20260808-043", 101, 202, 70, "delivered", 2),
            ("receipt-20260808-044", "settlement-20260808-044", 202, 101, 70, "manual_review", 1),
        )
        values = ",".join(
            f"('{receipt_id}','{batch_id}',{from_id},{to_id},{amount},'{state}',"
            f"CURRENT_TIMESTAMP - INTERVAL {age_minutes} MINUTE)"
            for receipt_id, batch_id, from_id, to_id, amount, state, age_minutes in rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.receipt_table} "
                "(receipt_id, batch_id, from_account_id, to_account_id, amount, receipt_state, observed_at) "
                f"VALUES {values}"
            ),
            "seed SF05 settlement receipts",
        )

    def _seed_reconciliation(self, env) -> None:
        rows = (
            ("reconcile-20260808-9001", self.batch_id, self.from_account_id, self.to_account_id, self.amount, "open", "settlement-api", 8),
            ("reconcile-20260808-9002", COMPETING_BATCH_ID, COMPETING_FROM_ACCOUNT_ID, COMPETING_TO_ACCOUNT_ID, COMPETING_AMOUNT, "duplicate_hold", "replay-guard", 1),
            ("reconcile-20260808-9003", "settlement-20260808-043", 101, 202, 70, "closed", "settlement-api", 2),
            ("reconcile-20260808-9004", "settlement-20260808-044", 202, 101, 70, "manual_review", "risk-queue", 1),
            ("reconcile-20260808-9005", "settlement-20260808-027", 101, 202, 15, "closed", "settlement-api", 55),
        )
        values = ",".join(
            f"('{reconciliation_id}','{batch_id}',{from_id},{to_id},{amount},'{control_state}','{source}',"
            f"CURRENT_TIMESTAMP - INTERVAL {age_minutes} MINUTE)"
            for reconciliation_id, batch_id, from_id, to_id, amount, control_state, source, age_minutes in rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.reconciliation_table} "
                "(reconciliation_id, batch_id, from_account_id, to_account_id, amount, control_state, source, observed_at) "
                f"VALUES {values}"
            ),
            "seed SF05 settlement reconciliation records",
        )

    def _seed_dispatch(self, env) -> None:
        rows = (
            ("dispatch-20260808-042", "wallet-alert-081", self.batch_id, self.from_account_id, self.to_account_id, self.amount, "active_customer_incident", "customer-settlement", 8),
            ("dispatch-20260808-045", "wallet-alert-081", COMPETING_BATCH_ID, COMPETING_FROM_ACCOUNT_ID, COMPETING_TO_ACCOUNT_ID, COMPETING_AMOUNT, "suppressed_replay", "replay-guard", 1),
            ("dispatch-20260808-043", "wallet-alert-079", "settlement-20260808-043", 101, 202, 70, "closed", "customer-settlement", 2),
            ("dispatch-20260808-044", "wallet-alert-080", "settlement-20260808-044", 202, 101, 70, "manual_review", "risk-queue", 1),
            ("dispatch-20260808-027", "wallet-alert-061", "settlement-20260808-027", 101, 202, 15, "closed", "customer-settlement", 55),
        )
        values = ",".join(
            f"('{dispatch_id}','{incident_key}','{batch_id}',{from_id},{to_id},{amount},'{dispatch_state}','{route}',"
            f"CURRENT_TIMESTAMP - INTERVAL {age_minutes} MINUTE)"
            for dispatch_id, incident_key, batch_id, from_id, to_id, amount, dispatch_state, route, age_minutes in rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.dispatch_table} "
                "(dispatch_id, incident_key, batch_id, from_account_id, to_account_id, amount, dispatch_state, route, observed_at) "
                f"VALUES {values}"
            ),
            "seed SF05 settlement dispatch records",
        )

    def _seed_ledger(self, env) -> None:
        rows = (
            ("ledger-20260808-042-debit", self.batch_id, self.from_account_id, "debit", self.amount, "applied", "txn-042-debit", 8),
            ("ledger-20260808-042-credit", self.batch_id, self.to_account_id, "credit", self.amount, "pending", "txn-042-credit", 0),
            ("ledger-20260808-045-debit", COMPETING_BATCH_ID, COMPETING_FROM_ACCOUNT_ID, "debit", COMPETING_AMOUNT, "blocked", "txn-045-debit", 1),
            ("ledger-20260808-045-credit", COMPETING_BATCH_ID, COMPETING_TO_ACCOUNT_ID, "credit", COMPETING_AMOUNT, "blocked", "txn-045-credit", 1),
            ("ledger-20260808-043-credit", "settlement-20260808-043", 202, "credit", 70, "applied", "txn-043-credit", 2),
        )
        values = ",".join(
            f"('{entry_id}','{batch_id}',{account_id},'{leg_type}',{amount},'{entry_state}','{ledger_reference}',"
            f"CURRENT_TIMESTAMP - INTERVAL {age_minutes} MINUTE)"
            for entry_id, batch_id, account_id, leg_type, amount, entry_state, ledger_reference, age_minutes in rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.ledger_table} "
                "(ledger_entry_id, batch_id, account_id, leg_type, amount, entry_state, ledger_reference, observed_at) "
                f"VALUES {values}"
            ),
            "seed SF05 settlement ledger entries",
        )

    def _record_target_attempts(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.attempt_table} "
                "(batch_id, worker_id, first_account_id, second_account_id, error_code, final_state, note, observed_at) "
                "VALUES "
                f"('{self.batch_id}','historical-worker-a',{self.from_account_id},{self.to_account_id},"
                "'ERROR 9007','rolled_back','older transaction conflict record',"
                "CURRENT_TIMESTAMP - INTERVAL 2 HOUR),"
                f"('{self.batch_id}','historical-worker-b',{self.to_account_id},{self.from_account_id},"
                "'LOCK_WAIT_TIMEOUT','rolled_back','older transaction conflict record',"
                "CURRENT_TIMESTAMP - INTERVAL 90 MINUTE),"
                f"('{self.batch_id}','settlement-worker-a',{self.from_account_id},{self.to_account_id},"
                "'ERROR 1213','rolled_back','current transaction conflict record',CURRENT_TIMESTAMP),"
                f"('{self.batch_id}','settlement-worker-b',{self.to_account_id},{self.from_account_id},"
                "'ERROR 1213','rolled_back','current transaction conflict record',CURRENT_TIMESTAMP)"
            ),
            "record SF05 target deadlock attempts",
        )

    def _create_decoy_deadlocks(self, env) -> None:
        for batch_id, first_id, second_id, _, age_minutes in self.deadlock_decoy_specs:
            self._create_deadlock_for_pair(
                env,
                first_id=first_id,
                second_id=second_id,
                worker_a=f"{batch_id}-worker-a",
                worker_b=f"{batch_id}-worker-b",
            )
            self._record_decoy_deadlock_attempts(env, batch_id, first_id, second_id, age_minutes)

    def _create_competing_deadlock(self, env) -> None:
        self._create_deadlock_for_pair(
            env,
            first_id=COMPETING_FROM_ACCOUNT_ID,
            second_id=COMPETING_TO_ACCOUNT_ID,
            worker_a="replay-worker-a",
            worker_b="replay-worker-b",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.attempt_table} "
                "(batch_id, worker_id, first_account_id, second_account_id, error_code, final_state, note, observed_at) "
                "VALUES "
                f"('{COMPETING_BATCH_ID}','replay-worker-a',{COMPETING_FROM_ACCOUNT_ID},{COMPETING_TO_ACCOUNT_ID},"
                "'ERROR 1213','rolled_back','duplicate-hold transaction conflict',CURRENT_TIMESTAMP),"
                f"('{COMPETING_BATCH_ID}','replay-worker-b',{COMPETING_TO_ACCOUNT_ID},{COMPETING_FROM_ACCOUNT_ID},"
                "'ERROR 1213','rolled_back','duplicate-hold transaction conflict',CURRENT_TIMESTAMP)"
            ),
            f"record SF05 competing deadlock attempts for {COMPETING_BATCH_ID}",
        )

    def _record_decoy_deadlock_attempts(
        self,
        env,
        batch_id: str,
        first_id: int,
        second_id: int,
        age_minutes: int,
    ) -> None:
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.attempt_table} "
                "(batch_id, worker_id, first_account_id, second_account_id, error_code, final_state, note, observed_at) "
                "VALUES "
                f"('{batch_id}','deadlock-worker-a',{first_id},{second_id},"
                f"'ERROR 1213','rolled_back','same-domain transaction conflict',CURRENT_TIMESTAMP - INTERVAL {age_minutes} MINUTE),"
                f"('{batch_id}','deadlock-worker-b',{second_id},{first_id},"
                f"'ERROR 1213','rolled_back','same-domain transaction conflict',CURRENT_TIMESTAMP - INTERVAL {age_minutes} MINUTE)"
            ),
            f"record SF05 decoy deadlock attempts for {batch_id}",
        )

    def _verify_tables(self, env) -> None:
        payload = json_object(
            env.execute_sql(
                f"SELECT "
                f"(SELECT count(*) FROM {self.account_table}), "
                f"(SELECT count(*) FROM {self.job_table}), "
                f"(SELECT count(*) FROM {self.attempt_table}), "
                f"(SELECT count(*) FROM {self.receipt_table}), "
                f"(SELECT count(*) FROM {self.reconciliation_table}), "
                f"(SELECT count(*) FROM {self.dispatch_table}), "
                f"(SELECT count(*) FROM {self.ledger_table})"
            ),
            "verify SF05 table state",
        )
        accounts, jobs, attempts, receipts, reconciliations, dispatches, ledger_entries = payload["result"][0]
        expected_attempts = 72 + 4 + (2 * len(self.deadlock_decoy_specs)) + 2
        if (
            accounts < 10
            or jobs < self.decoy_job_count + 1
            or attempts < expected_attempts
            or receipts < 7
            or reconciliations < 5
            or dispatches < 5
            or ledger_entries < 5
        ):
            raise RuntimeError(
                "SF05 persistent state is incomplete: "
                f"accounts={accounts}, jobs={jobs}, attempts={attempts}, receipts={receipts}, "
                f"reconciliations={reconciliations}, dispatches={dispatches}, ledger_entries={ledger_entries}, "
                f"decoy_job_count={self.decoy_job_count}, expected_attempts={expected_attempts}"
            )

    def _create_real_deadlock(self, env) -> None:
        self._create_deadlock_for_pair(
            env,
            first_id=self.from_account_id,
            second_id=self.to_account_id,
            worker_a="settlement-worker-a",
            worker_b="settlement-worker-b",
        )

    def _create_deadlock_for_pair(
        self,
        env,
        *,
        first_id: int,
        second_id: int,
        worker_a: str,
        worker_b: str,
    ) -> None:
        barrier = threading.Barrier(2, timeout=12)
        errors = []

        def transact(name: str, first_id: int, second_id: int) -> None:
            conn = self._connection(env)
            try:
                conn.autocommit = False
                with conn.cursor() as cur:
                    cur.execute("SET innodb_lock_wait_timeout=30")
                    cur.execute("BEGIN PESSIMISTIC")
                    cur.execute(f"UPDATE {self.account_table} SET balance = balance WHERE account_id = {first_id}")
                    barrier.wait()
                    cur.execute(f"UPDATE {self.account_table} SET balance = balance WHERE account_id = {second_id}")
            except Exception as exc:
                errors.append((name, str(exc)))
            finally:
                conn.rollback()
                conn.close()

        first = threading.Thread(
            target=transact,
            args=(worker_a, first_id, second_id),
            daemon=True,
        )
        second = threading.Thread(
            target=transact,
            args=(worker_b, second_id, first_id),
            daemon=True,
        )
        first.start()
        second.start()
        join_thread(first, 35, "SF05 deadlock transaction A")
        join_thread(second, 35, "SF05 deadlock transaction B")
        if not any("1213" in message or "Deadlock" in message for _, message in errors):
            raise RuntimeError(
                "SF05 did not observe a TiDB deadlock error: "
                f"first_id={first_id}, second_id={second_id}, errors={errors!r}"
            )


class TidbSystemFailureDeadlockScenario(TiDBScenario):
    scenario_id = "tidb_system_failure_deadlock"
    description = "Investigates an incomplete settlement batch amid concurrent wallet activity."
    cases = (_TIDB_SYSTEM_FAILURE_DEADLOCK_CASE, _FOCUSED_DEADLOCK_CASE)

    def build_fault_plan(self, case: TidbSystemFailureDeadlockCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureDeadlockInjector,
                config={
                    "account_table": case.account_table,
                    "job_table": case.job_table,
                    "attempt_table": case.attempt_table,
                    "receipt_table": case.receipt_table,
                    "reconciliation_table": case.reconciliation_table,
                    "dispatch_table": case.dispatch_table,
                    "ledger_table": case.ledger_table,
                    "batch_id": case.batch_id,
                    "from_account_id": case.from_account_id,
                    "to_account_id": case.to_account_id,
                    "amount": case.amount,
                    "from_initial_balance": case.from_initial_balance,
                    "to_initial_balance": case.to_initial_balance,
                    "decoy_account_ids": case.decoy_account_ids,
                    "decoy_job_count": case.decoy_job_count,
                    "deadlock_decoy_specs": case.deadlock_decoy_specs,
                },
            ),
        )
