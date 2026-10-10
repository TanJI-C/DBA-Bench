import threading
from collections.abc import Mapping
from dataclasses import dataclass, replace

import pymysql

from src.scenarios.evaluation.tidb.query_perf.optimistic_write_conflict import (
    TidbQueryPerfOptimisticWriteConflictForSettlementEvaluatorCase,
    TidbQueryPerfOptimisticWriteConflictForSettlementReducedEvaluatorCase,
)
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    join_thread,
    json_object,
    require_sql_success,
    run_cleanup_steps,
    validate_sql_identifier,
)

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

class TidbQueryPerfOptimisticWriteConflictInjector(BaseFaultInjector):
    """Build a real multi-table settlement retry path with commit-time collisions."""

    def __init__(self):
        self._threads: tuple[threading.Thread, ...] = ()
        self._target_probe: tuple[int, int, tuple[str, ...]] = (0, 0, ())
        self._decoy_probes: tuple[tuple[int, int, tuple[str, ...]], ...] = ()
        self._record_lock = threading.Lock()

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_schema(context.env)
        self._run_all_probes(context.env)
        self._verify_incomplete_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_incomplete_state(context.env)
        self._run_all_probes(context.env)
        self._verify_incomplete_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_incomplete_state(context.env)
        require_sql_success(
            context.env.execute_sql("SET SESSION tidb_txn_mode = 'OPTIMISTIC'"),
            "expose QP02 transaction mode for diagnostic inspection",
        )
        mode = json_object(
            context.env.execute_sql("SELECT @@tidb_txn_mode"),
            "capture QP02 transaction mode",
        )
        retry = json_object(
            context.env.execute_sql("SHOW VARIABLES LIKE 'tidb_retry_limit'"),
            "capture QP02 retry limit",
        )
        txn_rows = json_object(
            context.env.execute_sql(
                f"SELECT txn_id, merchant_id, account_id, settlement_day, amount_cents, currency, "
                f"status, retry_count, last_error FROM {self.db}.{self.txn_table} "
                f"WHERE txn_id IN ({self._quoted_txns()}) ORDER BY txn_id"
            ),
            "capture QP02 settlement items",
        )
        line_rows = json_object(
            context.env.execute_sql(
                f"SELECT txn_id, line_no, gross_cents, fee_cents, net_cents, state "
                f"FROM {self.db}.{self.line_table} WHERE txn_id IN ({self._quoted_txns()}) "
                "ORDER BY txn_id, line_no"
            ),
            "capture QP02 settlement lines",
        )
        account_rows = json_object(
            context.env.execute_sql(
                f"SELECT account_id, merchant_id, available_cents, pending_cents, version, touch_count "
                f"FROM {self.db}.{self.account_table} WHERE account_id IN ({self._account_ids()}) "
                "ORDER BY account_id"
            ),
            "capture QP02 account state",
        )
        position_rows = json_object(
            context.env.execute_sql(
                f"SELECT merchant_id, settlement_day, settled_cents, txn_count, version "
                f"FROM {self.db}.{self.position_table} "
                "WHERE settlement_day BETWEEN DATE('2026-08-03') AND DATE('2026-08-05') "
                "ORDER BY merchant_id, settlement_day"
            ),
            "capture QP02 merchant-day state",
        )
        attempt_rollup = json_object(
            context.env.execute_sql(
                f"SELECT txn_id, error_code, stage, merchant_id, settlement_day, relation_name, COUNT(*) AS attempts "
                f"FROM {self.db}.{self.attempt_table} "
                "GROUP BY txn_id, error_code, stage, merchant_id, settlement_day, relation_name "
                "ORDER BY attempts DESC, txn_id, error_code LIMIT 120"
            ),
            "capture QP02 attempt rollup",
        )
        target_account = self._one_row(
            account_rows["result"],
            lambda row: int(row[0]) == self.target_account_id,
            "target account baseline",
        )
        target_position = self._one_row(
            position_rows["result"],
            lambda row: int(row[0]) == self.target_merchant_id
            and str(row[1]) == self.target_settlement_day,
            "target merchant-day baseline",
        )
        return {
            "fault_target_txn_id": self.target_txn_id,
            "fault_target_resource": f"merchant={self.target_merchant_id},day={self.target_settlement_day}",
            "fault_target_probe": self._target_probe,
            "fault_decoy_probes": self._decoy_probes,
            "fault_retry_limit": int(retry["result"][0][1]),
            "fault_transaction_mode": mode["result"],
            "fault_txn_rows": txn_rows["result"],
            "fault_line_rows": line_rows["result"],
            "fault_account_rows": account_rows["result"],
            "fault_position_rows": position_rows["result"],
            "fault_attempt_rollup": attempt_rollup["result"],
            "fault_target_account_baseline": tuple(target_account),
            "fault_target_position_baseline": tuple(target_position),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime(context)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._stop_runtime(context)
        self._configure(context.config)
        require_sql_success(
            context.env.execute_sql(f"DROP DATABASE IF EXISTS {self.db}"),
            f"drop QP02 settlement database {self.db}",
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.txn_table = validate_sql_identifier(str(config["txn_table"]), "transaction table")
        self.line_table = validate_sql_identifier(str(config["line_table"]), "line table")
        self.account_table = validate_sql_identifier(str(config["account_table"]), "account table")
        self.position_table = validate_sql_identifier(str(config["position_table"]), "position table")
        self.reservation_table = validate_sql_identifier(str(config["reservation_table"]), "reservation table")
        self.queue_table = validate_sql_identifier(str(config["queue_table"]), "queue table")
        self.attempt_table = validate_sql_identifier(str(config["attempt_table"]), "attempt table")
        self.ledger_table = validate_sql_identifier(str(config["ledger_table"]), "ledger table")
        self.audit_table = validate_sql_identifier(str(config["audit_table"]), "audit table")
        self.outbox_table = validate_sql_identifier(str(config["outbox_table"]), "outbox table")
        self.target_txn_id = str(config["target_txn_id"])
        self.target_idempotency_key = str(config["target_idempotency_key"])
        self.target_merchant_id = int(config["target_merchant_id"])
        self.target_account_id = int(config["target_account_id"])
        self.target_settlement_day = str(config["target_settlement_day"])
        self.target_amount_cents = int(config["target_amount_cents"])
        self.target_currency = str(config["target_currency"])
        self.target_line_ids = tuple(int(value) for value in config["target_line_ids"])
        self.decoy_specs = tuple(
            (str(row[0]), int(row[1]), int(row[2]), str(row[3]))
            for row in config["decoy_specs"]
        )
        self.conflict_rounds = int(config["conflict_rounds"])
        self.minimum_conflicts = int(config["minimum_conflicts"])
        self.decoy_rounds = int(config["decoy_rounds"])
        self.decoy_minimum_conflicts = int(config["decoy_minimum_conflicts"])
        self.retry_limit = int(config["retry_limit"])

    def _create_schema(self, env) -> None:
        require_sql_success(
            env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {self.db}"),
            f"create QP02 database {self.db}",
        )
        for table in (
            self.outbox_table,
            self.audit_table,
            self.ledger_table,
            self.attempt_table,
            self.queue_table,
            self.reservation_table,
            self.position_table,
            self.account_table,
            self.line_table,
            self.txn_table,
        ):
            require_sql_success(
                env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"),
                f"drop stale QP02 table {self.db}.{table}",
            )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.txn_table} ("
                "txn_id VARCHAR(48) PRIMARY KEY, merchant_id BIGINT NOT NULL, account_id BIGINT NOT NULL, "
                "settlement_day DATE NOT NULL, amount_cents BIGINT NOT NULL, currency CHAR(3) NOT NULL, "
                "status VARCHAR(32) NOT NULL, idempotency_key VARCHAR(64) NOT NULL, retry_count INT NOT NULL, "
                "last_error VARCHAR(255) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE KEY uk_txn_idempotency (idempotency_key), "
                "KEY idx_txn_window (merchant_id, settlement_day, status))"
            ),
            "create QP02 settlement transaction table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.line_table} ("
                "line_id BIGINT PRIMARY KEY, txn_id VARCHAR(48) NOT NULL, line_no INT NOT NULL, "
                "line_kind VARCHAR(32) NOT NULL, gross_cents BIGINT NOT NULL, fee_cents BIGINT NOT NULL, "
                "net_cents BIGINT NOT NULL, state VARCHAR(32) NOT NULL, "
                "UNIQUE KEY uk_line_txn_no (txn_id, line_no), KEY idx_line_txn (txn_id))"
            ),
            "create QP02 settlement line table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.account_table} ("
                "account_id BIGINT PRIMARY KEY, merchant_id BIGINT NOT NULL, available_cents BIGINT NOT NULL, "
                "pending_cents BIGINT NOT NULL, version BIGINT NOT NULL, touch_count BIGINT NOT NULL, "
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE KEY uk_account_merchant (merchant_id, account_id))"
            ),
            "create QP02 merchant account table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.position_table} ("
                "merchant_id BIGINT NOT NULL, settlement_day DATE NOT NULL, settled_cents BIGINT NOT NULL, "
                "txn_count BIGINT NOT NULL, version BIGINT NOT NULL, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                "PRIMARY KEY (merchant_id, settlement_day))"
            ),
            "create QP02 merchant-day position table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.reservation_table} ("
                "reservation_id BIGINT PRIMARY KEY, txn_id VARCHAR(48) NOT NULL, account_id BIGINT NOT NULL, "
                "reserved_cents BIGINT NOT NULL, state VARCHAR(32) NOT NULL, touch_count BIGINT NOT NULL, "
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE KEY uk_reservation_txn (txn_id))"
            ),
            "create QP02 reservation table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.queue_table} ("
                "queue_id BIGINT PRIMARY KEY, txn_id VARCHAR(48) NOT NULL, queue_state VARCHAR(32) NOT NULL, "
                "attempts INT NOT NULL, visible_at TIMESTAMP NOT NULL, UNIQUE KEY uk_queue_txn (txn_id))"
            ),
            "create QP02 settlement queue table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.attempt_table} ("
                "attempt_id BIGINT PRIMARY KEY AUTO_INCREMENT, txn_id VARCHAR(48) NOT NULL, attempt_no INT NOT NULL, "
                "worker_name VARCHAR(64) NOT NULL, stage VARCHAR(32) NOT NULL, error_code VARCHAR(32) NOT NULL, "
                "merchant_id BIGINT NOT NULL, settlement_day DATE NOT NULL, relation_name VARCHAR(64) NOT NULL, "
                "detail VARCHAR(255) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                "KEY idx_attempt_lookup (txn_id, error_code, merchant_id, settlement_day))"
            ),
            "create QP02 settlement attempt table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.ledger_table} ("
                "ledger_id VARCHAR(64) PRIMARY KEY, txn_id VARCHAR(48) NOT NULL, merchant_id BIGINT NOT NULL, "
                "account_id BIGINT NOT NULL, debit_cents BIGINT NOT NULL, credit_cents BIGINT NOT NULL, "
                "currency CHAR(3) NOT NULL, status VARCHAR(32) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                "UNIQUE KEY uk_ledger_txn (txn_id))"
            ),
            "create QP02 settlement ledger table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.audit_table} ("
                "audit_id BIGINT PRIMARY KEY AUTO_INCREMENT, txn_id VARCHAR(48) NOT NULL, event_type VARCHAR(48) NOT NULL, "
                "actor VARCHAR(64) NOT NULL, detail VARCHAR(255) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                "UNIQUE KEY uk_audit_event (txn_id, event_type), KEY idx_audit_txn (txn_id))"
            ),
            "create QP02 settlement audit table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.outbox_table} ("
                "event_id VARCHAR(64) PRIMARY KEY, txn_id VARCHAR(48) NOT NULL, topic VARCHAR(64) NOT NULL, "
                "payload VARCHAR(255) NOT NULL, status VARCHAR(32) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                "UNIQUE KEY uk_outbox_txn_topic (txn_id, topic))"
            ),
            "create QP02 settlement outbox table",
        )
        self._seed_business_rows(env)
        self._seed_attempt_rows(env)

    def _seed_business_rows(self, env) -> None:
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.account_table} "
                "(account_id, merchant_id, available_cents, pending_cents, version, touch_count) VALUES "
                "(7001701, 42017, 5000000, 725500, 10, 0),"
                "(7001702, 42017, 1200000, 150000, 4, 0),"
                "(7001801, 42018, 2400000, 350000, 6, 0),"
                "(7001901, 42019, 1800000, 90000, 2, 0)"
            ),
            "seed QP02 merchant accounts",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.position_table} "
                "(merchant_id, settlement_day, settled_cents, txn_count, version) VALUES "
                "(42017, DATE('2026-08-03'), 980000, 7, 3),"
                "(42017, DATE('2026-08-04'), 3450000, 17, 10),"
                "(42018, DATE('2026-08-04'), 2080000, 11, 5),"
                "(42019, DATE('2026-08-04'), 840000, 5, 2)"
            ),
            "seed QP02 merchant-day positions",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.txn_table} "
                "(txn_id, merchant_id, account_id, settlement_day, amount_cents, currency, status, idempotency_key, retry_count, last_error) VALUES "
                f"('{self.target_txn_id}', {self.target_merchant_id}, {self.target_account_id}, DATE('{self.target_settlement_day}'), {self.target_amount_cents}, '{self.target_currency}', 'NEEDS_RETRY', '{self.target_idempotency_key}', 6, 'commit stage did not complete'),"
                "('SETTLE-20260805-004219', 42017, 7001702, DATE('2026-08-04'), 66000, 'USD', 'NEEDS_RETRY', 'idem-004219', 5, 'shared day position still pending'),"
                "('SETTLE-20260805-004218', 42018, 7001801, DATE('2026-08-04'), 87500, 'USD', 'NEEDS_RETRY', 'idem-004218', 4, 'partner acknowledgement pending'),"
                "('SETTLE-20260805-004231', 42019, 7001901, DATE('2026-08-04'), 33500, 'USD', 'MANUAL_REVIEW', 'idem-004231', 2, 'receipt projection unavailable'),"
                "('SETTLE-20260804-004217', 42017, 7001702, DATE('2026-08-03'), 64000, 'USD', 'NEEDS_RETRY', 'idem-prev-004217', 3, 'previous window acknowledgement pending'),"
                "('SETTLE-20260805-004245', 42017, 7001701, DATE('2026-08-04'), 45000, 'USD', 'READY', 'idem-004245', 0, ''),"
                "('SETTLE-20260805-004246', 42018, 7001801, DATE('2026-08-04'), 29000, 'USD', 'READY', 'idem-004246', 0, '')"
            ),
            "seed QP02 settlement items",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.line_table} "
                "(line_id, txn_id, line_no, line_kind, gross_cents, fee_cents, net_cents, state) VALUES "
                "(91042171, 'SETTLE-20260805-004217', 1, 'principal', 100000, 2000, 98000, 'PENDING'),"
                "(91042172, 'SETTLE-20260805-004217', 2, 'adjustment', 27500, 0, 27500, 'PENDING'),"
                "(91042191, 'SETTLE-20260805-004219', 1, 'principal', 66000, 0, 66000, 'PENDING'),"
                "(91042181, 'SETTLE-20260805-004218', 1, 'principal', 87500, 0, 87500, 'PENDING'),"
                "(91042311, 'SETTLE-20260805-004231', 1, 'principal', 33500, 0, 33500, 'PENDING'),"
                "(91042173, 'SETTLE-20260804-004217', 1, 'principal', 64000, 0, 64000, 'PENDING'),"
                "(91042451, 'SETTLE-20260805-004245', 1, 'principal', 45000, 0, 45000, 'PENDING'),"
                "(91042461, 'SETTLE-20260805-004246', 1, 'principal', 29000, 0, 29000, 'PENDING')"
            ),
            "seed QP02 settlement lines",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.reservation_table} "
                "(reservation_id, txn_id, account_id, reserved_cents, state, touch_count) VALUES "
                "(8204217, 'SETTLE-20260805-004217', 7001701, 125500, 'HELD', 0),"
                "(82042191, 'SETTLE-20260805-004219', 7001702, 66000, 'HELD', 0),"
                "(8204218, 'SETTLE-20260805-004218', 7001801, 87500, 'HELD', 0),"
                "(8204231, 'SETTLE-20260805-004231', 7001901, 33500, 'HELD', 0),"
                "(8204219, 'SETTLE-20260804-004217', 7001702, 64000, 'HELD', 0),"
                "(8204245, 'SETTLE-20260805-004245', 7001701, 45000, 'HELD', 0),"
                "(8204246, 'SETTLE-20260805-004246', 7001801, 29000, 'HELD', 0)"
            ),
            "seed QP02 reservations",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.queue_table} "
                "(queue_id, txn_id, queue_state, attempts, visible_at) VALUES "
                "(7204217, 'SETTLE-20260805-004217', 'READY', 6, CURRENT_TIMESTAMP - INTERVAL 42 MINUTE),"
                "(72042191, 'SETTLE-20260805-004219', 'RETRY', 5, CURRENT_TIMESTAMP - INTERVAL 37 MINUTE),"
                "(7204218, 'SETTLE-20260805-004218', 'RETRY', 4, CURRENT_TIMESTAMP - INTERVAL 31 MINUTE),"
                "(7204231, 'SETTLE-20260805-004231', 'REVIEW', 2, CURRENT_TIMESTAMP - INTERVAL 28 MINUTE),"
                "(7204219, 'SETTLE-20260804-004217', 'RETRY', 3, CURRENT_TIMESTAMP - INTERVAL 71 MINUTE),"
                "(7204245, 'SETTLE-20260805-004245', 'READY', 0, CURRENT_TIMESTAMP - INTERVAL 3 MINUTE),"
                "(7204246, 'SETTLE-20260805-004246', 'READY', 0, CURRENT_TIMESTAMP - INTERVAL 4 MINUTE)"
            ),
            "seed QP02 settlement queue",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.audit_table} "
                "(txn_id, event_type, actor, detail) VALUES "
                "('SETTLE-20260805-004219', 'shared_day_retry', 'settlement-worker-e', 'same merchant day remains pending'),"
                "('SETTLE-20260805-004218', 'retry_seen', 'retry-worker-b', 'nearby item remains pending'),"
                "('SETTLE-20260805-004231', 'manual_review', 'risk-gate', 'receipt projection unavailable'),"
                "('SETTLE-20260804-004217', 'partner_wait', 'settlement-batch', 'previous window acknowledgement pending')"
            ),
            "seed QP02 audit noise",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.outbox_table} "
                "(event_id, txn_id, topic, payload, status) VALUES "
                "('evt-004219-retry', 'SETTLE-20260805-004219', 'settlement.retry', '{\"status\":\"pending\"}', 'READY'),"
                "('evt-004218-retry', 'SETTLE-20260805-004218', 'settlement.retry', '{\"status\":\"pending\"}', 'READY'),"
                "('evt-004231-review', 'SETTLE-20260805-004231', 'settlement.review', '{\"status\":\"manual\"}', 'READY')"
            ),
            "seed QP02 outbox noise",
        )

    def _seed_attempt_rows(self, env) -> None:
        values = (
            "('SETTLE-20260805-004217', 1, 'settlement-worker-a', 'prewrite', 'OK', 42017, DATE('2026-08-04'), 'merchant_daily_position', 'write set prepared'),",
            "('SETTLE-20260805-004217', 2, 'settlement-worker-b', 'commit', '9007', 42017, DATE('2026-08-04'), 'merchant_daily_position', 'commit did not finish'),",
            "('SETTLE-20260805-004219', 1, 'settlement-worker-e', 'commit', '9007', 42017, DATE('2026-08-04'), 'merchant_daily_position', 'same merchant day commit did not finish'),",
            "('SETTLE-20260805-004218', 1, 'settlement-worker-c', 'commit', '9007', 42018, DATE('2026-08-04'), 'merchant_daily_position', 'nearby item commit did not finish'),",
            "('SETTLE-20260805-004231', 1, 'receipt-worker', 'notify', 'CACHE_MISS', 42019, DATE('2026-08-04'), 'settlement_outbox', 'receipt projection unavailable'),",
            "('SETTLE-20260804-004217', 1, 'partner-reconcile', 'ack', 'TIMEOUT', 42017, DATE('2026-08-03'), 'settlement_queue', 'previous window acknowledgement pending'),",
            "('SETTLE-20260805-004245', 1, 'settlement-worker-a', 'precheck', 'OK', 42017, DATE('2026-08-04'), 'merchant_daily_position', 'queued for later processing'),",
            "('SETTLE-20260805-004246', 1, 'settlement-worker-d', 'precheck', 'OK', 42018, DATE('2026-08-04'), 'merchant_daily_position', 'queued for later processing')",
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.attempt_table} "
                "(txn_id, attempt_no, worker_name, stage, error_code, merchant_id, settlement_day, relation_name, detail) VALUES "
                + "".join(values)
            ),
            "seed QP02 attempt evidence",
        )

    def _connection(self, env, *, autocommit: bool):
        return pymysql.connect(
            host=env.host,
            port=env.port,
            user=env.user,
            password=env.password,
            database=self.db,
            charset="utf8mb4",
            autocommit=autocommit,
            connect_timeout=5,
            read_timeout=90,
            write_timeout=90,
        )

    def _run_all_probes(self, env) -> None:
        self._target_probe = self._run_probe(
            env,
            txn_id=self.target_txn_id,
            merchant_id=self.target_merchant_id,
            account_id=self.target_account_id,
            settlement_day=self.target_settlement_day,
            rounds=self.conflict_rounds,
            minimum_conflicts=self.minimum_conflicts,
            label="settlement-target",
        )
        self._decoy_probes = tuple(
            self._run_probe(
                env,
                txn_id=txn_id,
                merchant_id=merchant_id,
                account_id=account_id,
                settlement_day=settlement_day,
                rounds=self.decoy_rounds,
                minimum_conflicts=self.decoy_minimum_conflicts,
                label=f"settlement-neighbor-{merchant_id}",
            )
            for txn_id, merchant_id, account_id, settlement_day in self.decoy_specs
        )

    def _run_probe(
        self,
        env,
        *,
        txn_id: str,
        merchant_id: int,
        account_id: int,
        settlement_day: str,
        rounds: int,
        minimum_conflicts: int,
        label: str,
    ) -> tuple[int, int, tuple[str, ...]]:
        barrier = threading.Barrier(2, timeout=30)
        conflict_count = 0
        commit_count = 0
        errors: list[str] = []
        counters_lock = threading.Lock()
        failures: list[Exception] = []
        failures_lock = threading.Lock()

        def worker(worker_id: int) -> None:
            nonlocal conflict_count, commit_count
            connection = None
            try:
                connection = self._connection(env, autocommit=False)
                with connection.cursor() as cursor:
                    cursor.execute("SET SESSION tidb_txn_mode = 'OPTIMISTIC'")
                    for round_no in range(rounds):
                        cursor.execute("START TRANSACTION")
                        try:
                            cursor.execute(
                                f"SELECT t.status, COUNT(l.line_id), COALESCE(SUM(l.net_cents), 0) "
                                f"FROM {self.txn_table} AS t "
                                f"JOIN {self.line_table} AS l ON l.txn_id = t.txn_id "
                                "WHERE t.txn_id = %s GROUP BY t.status",
                                (txn_id,),
                            )
                            cursor.execute(
                                f"UPDATE {self.position_table} SET version = version + 1, updated_at = CURRENT_TIMESTAMP "
                                "WHERE merchant_id = %s AND settlement_day = DATE(%s)",
                                (merchant_id, settlement_day),
                            )
                            cursor.execute(
                                f"UPDATE {self.account_table} SET version = version + 1, touch_count = touch_count + 1, "
                                "updated_at = CURRENT_TIMESTAMP WHERE account_id = %s",
                                (account_id,),
                            )
                            cursor.execute(
                                f"UPDATE {self.reservation_table} SET touch_count = touch_count + 1, "
                                "updated_at = CURRENT_TIMESTAMP WHERE txn_id = %s AND state = 'HELD'",
                                (txn_id,),
                            )
                            cursor.execute(
                                f"UPDATE {self.queue_table} SET attempts = attempts + 1 "
                                "WHERE txn_id = %s AND queue_state IN ('READY', 'RETRY')",
                                (txn_id,),
                            )
                            cursor.execute(
                                f"UPDATE {self.txn_table} SET retry_count = retry_count + 1, "
                                "last_error = 'commit stage still pending', updated_at = CURRENT_TIMESTAMP "
                                "WHERE txn_id = %s AND status IN ('NEEDS_RETRY', 'READY', 'MANUAL_REVIEW')",
                                (txn_id,),
                            )
                            barrier.wait()
                            connection.commit()
                        except pymysql.MySQLError as exc:
                            code = exc.args[0] if exc.args else None
                            if code != 9007:
                                raise RuntimeError(
                                    "QP02 probe returned an unexpected TiDB error: "
                                    f"txn_id={txn_id!r}, worker={worker_id}, round={round_no}, "
                                    f"code={code!r}, error={exc}"
                                ) from exc
                            connection.rollback()
                            with counters_lock:
                                conflict_count += 1
                                errors.append(str(exc))
                            self._record_attempt(
                                env,
                                txn_id=txn_id,
                                attempt_no=round_no + worker_id * 10000,
                                worker_name=f"{label}-{worker_id}",
                                stage="commit",
                                error_code="9007",
                                merchant_id=merchant_id,
                                settlement_day=settlement_day,
                                relation_name=self.position_table,
                                detail=str(exc)[:220],
                            )
                        else:
                            with counters_lock:
                                commit_count += 1
                            self._record_attempt(
                                env,
                                txn_id=txn_id,
                                attempt_no=round_no + worker_id * 10000,
                                worker_name=f"{label}-{worker_id}",
                                stage="commit",
                                error_code="OK",
                                merchant_id=merchant_id,
                                settlement_day=settlement_day,
                                relation_name=self.position_table,
                                detail="one retry attempt committed its operational marker",
                            )
            except Exception as exc:
                with failures_lock:
                    failures.append(exc)
                barrier.abort()
            finally:
                if connection is not None:
                    connection.close()

        self._threads = tuple(
            threading.Thread(
                target=worker,
                args=(worker_id,),
                name=f"qp02-settlement-{label}-{worker_id}",
                daemon=True,
            )
            for worker_id in (0, 1)
        )
        for thread in self._threads:
            thread.start()
        for thread in self._threads:
            join_thread(thread, 90, f"QP02 probe worker {thread.name}")
        self._threads = ()
        if failures:
            raise RuntimeError(
                f"QP02 probe failed: txn_id={txn_id!r}, label={label!r}, failures={failures!r}"
            ) from failures[0]
        if conflict_count < minimum_conflicts:
            raise RuntimeError(
                f"QP02 probe did not produce the required real commit conflicts: txn_id={txn_id!r}, "
                f"label={label!r}, required={minimum_conflicts}, conflicts={conflict_count}, "
                f"commits={commit_count}, errors={errors!r}"
            )
        return conflict_count, commit_count, tuple(errors)

    def _record_attempt(
        self,
        env,
        *,
        txn_id: str,
        attempt_no: int,
        worker_name: str,
        stage: str,
        error_code: str,
        merchant_id: int,
        settlement_day: str,
        relation_name: str,
        detail: str,
    ) -> None:
        with self._record_lock:
            connection = self._connection(env, autocommit=True)
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO {self.db}.{self.attempt_table} "
                        "(txn_id, attempt_no, worker_name, stage, error_code, merchant_id, settlement_day, relation_name, detail) "
                        "VALUES (%s, %s, %s, %s, %s, %s, DATE(%s), %s, %s)",
                        (
                            txn_id,
                            attempt_no,
                            worker_name,
                            stage,
                            error_code,
                            merchant_id,
                            settlement_day,
                            relation_name,
                            detail,
                        ),
                    )
            finally:
                connection.close()

    def _verify_incomplete_state(self, env) -> None:
        txn_rows = json_object(
            env.execute_sql(
                f"SELECT txn_id, status, amount_cents FROM {self.db}.{self.txn_table} "
                f"WHERE txn_id = '{self.target_txn_id}'"
            ),
            "verify QP02 target item remains incomplete",
        )["result"]
        line_rows = json_object(
            env.execute_sql(
                f"SELECT COUNT(*), COALESCE(SUM(CASE WHEN state = 'SETTLED' THEN 1 ELSE 0 END), 0) "
                f"FROM {self.db}.{self.line_table} WHERE txn_id = '{self.target_txn_id}'"
            ),
            "verify QP02 target lines remain pending",
        )["result"]
        ledger_rows = json_object(
            env.execute_sql(
                f"SELECT COUNT(*) FROM {self.db}.{self.ledger_table} "
                f"WHERE txn_id = '{self.target_txn_id}'"
            ),
            "verify QP02 target ledger is absent",
        )["result"]
        reservation_rows = json_object(
            env.execute_sql(
                f"SELECT state FROM {self.db}.{self.reservation_table} "
                f"WHERE txn_id = '{self.target_txn_id}'"
            ),
            "verify QP02 target reservation is held",
        )["result"]
        queue_rows = json_object(
            env.execute_sql(
                f"SELECT queue_state FROM {self.db}.{self.queue_table} "
                f"WHERE txn_id = '{self.target_txn_id}'"
            ),
            "verify QP02 target queue state",
        )["result"]
        if (
            len(txn_rows) != 1
            or str(txn_rows[0][1]) == "APPLIED"
            or int(txn_rows[0][2]) != self.target_amount_cents
            or len(line_rows) != 1
            or int(line_rows[0][0]) != len(self.target_line_ids)
            or int(line_rows[0][1]) != 0
            or len(ledger_rows) != 1
            or int(ledger_rows[0][0]) != 0
            or len(reservation_rows) != 1
            or str(reservation_rows[0][0]) != "HELD"
            or len(queue_rows) != 1
            or str(queue_rows[0][0]) not in {"READY", "RETRY"}
        ):
            raise RuntimeError(
                "QP02 fault image is not in the expected incomplete state: "
                f"target_txn_id={self.target_txn_id!r}, txn={txn_rows!r}, lines={line_rows!r}, "
                f"ledger={ledger_rows!r}, reservation={reservation_rows!r}, queue={queue_rows!r}"
            )

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        steps = tuple(
            (
                "join QP02 settlement probe worker",
                lambda thread=thread: join_thread(thread, 5, f"QP02 worker {thread.name}"),
            )
            for thread in self._threads
        )
        run_cleanup_steps(
            f"QP02 settlement cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._threads = ()

    def _quoted_txns(self) -> str:
        return ", ".join(
            f"'{txn_id}'" for txn_id in (self.target_txn_id, *(row[0] for row in self.decoy_specs))
        )

    def _account_ids(self) -> str:
        return ", ".join(
            str(account_id)
            for account_id in (self.target_account_id, *(row[2] for row in self.decoy_specs))
        )

    @staticmethod
    def _one_row(rows: list, predicate, context: str):
        matches = [row for row in rows if predicate(row)]
        if len(matches) != 1:
            raise RuntimeError(f"QP02 expected exactly one {context}: rows={rows!r}")
        return matches[0]


_DB = "settleops_qp02"
_TXN_TABLE = "settlement_txn"
_LINE_TABLE = "settlement_line"
_ACCOUNT_TABLE = "merchant_account"
_POSITION_TABLE = "merchant_daily_position"
_RESERVATION_TABLE = "settlement_reservation"
_QUEUE_TABLE = "settlement_queue"
_ATTEMPT_TABLE = "settlement_attempts"
_LEDGER_TABLE = "settlement_ledger"
_AUDIT_TABLE = "settlement_audit"
_OUTBOX_TABLE = "settlement_outbox"

_TARGET_TXN_ID = "SETTLE-20260805-004217"
_TARGET_IDEMPOTENCY_KEY = "idem-004217"
_TARGET_MERCHANT_ID = 42017
_TARGET_ACCOUNT_ID = 7001701
_TARGET_SETTLEMENT_DAY = "2026-08-04"
_TARGET_AMOUNT_CENTS = 125_500
_TARGET_CURRENCY = "USD"
_TARGET_LINE_IDS = (91042171, 91042172)
_DECOY_SPECS = (
    ("SETTLE-20260805-004218", 42018, 7001801, "2026-08-04"),
    ("SETTLE-20260805-004231", 42019, 7001901, "2026-08-04"),
    ("SETTLE-20260804-004217", 42017, 7001702, "2026-08-03"),
    ("SETTLE-20260805-004219", 42017, 7001702, "2026-08-04"),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfOptimisticWriteConflictCase(TiDBScenarioCase):
    db: str
    txn_table: str
    line_table: str
    account_table: str
    position_table: str
    reservation_table: str
    queue_table: str
    attempt_table: str
    ledger_table: str
    audit_table: str
    outbox_table: str
    target_txn_id: str
    target_idempotency_key: str
    target_merchant_id: int
    target_account_id: int
    target_settlement_day: str
    target_amount_cents: int
    target_currency: str
    target_line_ids: tuple[int, ...]
    decoy_specs: tuple[tuple[str, int, int, str], ...]
    conflict_rounds: int
    minimum_conflicts: int
    decoy_rounds: int
    decoy_minimum_conflicts: int
    retry_limit: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfOptimisticWriteConflictForSettlementScenarioCase(
    TidbQueryPerfOptimisticWriteConflictCase
):
    pass


_TARGET_AND_NEIGHBOR_TXNS = ", ".join(
    f"'{txn_id}'" for txn_id in (_TARGET_TXN_ID, *(row[0] for row in _DECOY_SPECS))
)
_DECOY_TXNS = ", ".join(f"'{row[0]}'" for row in _DECOY_SPECS)

_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="settlement_window_summary",
            sql=(
                f"SELECT t.merchant_id, t.settlement_day, t.status, COUNT(*) AS item_count, "
                f"COALESCE(SUM(l.net_cents), 0) AS net_cents "
                f"FROM {_DB}.{_TXN_TABLE} AS t "
                f"JOIN {_DB}.{_LINE_TABLE} AS l ON l.txn_id = t.txn_id "
                "WHERE t.settlement_day BETWEEN DATE('2026-08-03') AND DATE('2026-08-05') "
                "GROUP BY t.merchant_id, t.settlement_day, t.status "
                "ORDER BY net_cents DESC, t.merchant_id LIMIT 30"
            ),
            qps=0.35,
            tier="SETTLEMENT_READ",
            application_name="settlement-window-api",
        ),
        WorkloadProfile(
            name="queue_status_age",
            sql=(
                f"SELECT q.queue_state, t.status, COUNT(*) AS item_count, "
                f"MAX(TIMESTAMPDIFF(MINUTE, q.visible_at, NOW())) AS oldest_minutes "
                f"FROM {_DB}.{_QUEUE_TABLE} AS q "
                f"JOIN {_DB}.{_TXN_TABLE} AS t ON t.txn_id = q.txn_id "
                "GROUP BY q.queue_state, t.status ORDER BY oldest_minutes DESC"
            ),
            qps=0.45,
            tier="QUEUE_READ",
            application_name="settlement-queue-monitor",
        ),
        WorkloadProfile(
            name="account_position_dashboard",
            sql=(
                f"SELECT a.merchant_id, a.account_id, a.available_cents, a.pending_cents, "
                f"p.settlement_day, p.settled_cents, p.txn_count "
                f"FROM {_DB}.{_ACCOUNT_TABLE} AS a "
                f"JOIN {_DB}.{_POSITION_TABLE} AS p ON p.merchant_id = a.merchant_id "
                "WHERE a.account_id IN (7001701, 7001702, 7001801, 7001901) "
                "ORDER BY a.merchant_id, p.settlement_day"
            ),
            qps=0.35,
            tier="SETTLEMENT_READ",
            application_name="merchant-balance-console",
        ),
        WorkloadProfile(
            name="ledger_delivery_summary",
            sql=(
                f"SELECT l.status AS ledger_state, o.status AS delivery_state, COUNT(*) AS item_count "
                f"FROM {_DB}.{_LEDGER_TABLE} AS l "
                f"LEFT JOIN {_DB}.{_OUTBOX_TABLE} AS o ON o.txn_id = l.txn_id "
                "GROUP BY l.status, o.status ORDER BY item_count DESC"
            ),
            qps=0.30,
            tier="DELIVERY_READ",
            application_name="settlement-delivery-monitor",
        ),
        WorkloadProfile(
            name="authorization_trace_slice",
            sql=(
                f"SELECT t.txn_id, t.merchant_id, t.account_id, t.settlement_day, t.status, "
                f"t.retry_count, r.state AS reservation_state, q.queue_state "
                f"FROM {_DB}.{_TXN_TABLE} AS t "
                f"LEFT JOIN {_DB}.{_RESERVATION_TABLE} AS r ON r.txn_id = t.txn_id "
                f"LEFT JOIN {_DB}.{_QUEUE_TABLE} AS q ON q.txn_id = t.txn_id "
                f"WHERE t.txn_id IN ({_TARGET_AND_NEIGHBOR_TXNS}) ORDER BY t.txn_id"
            ),
            qps=0.35,
            tier="SETTLEMENT_READ",
            application_name="settlement-case-review",
        ),
        WorkloadProfile(
            name="attempt_code_rollup",
            sql=(
                f"SELECT error_code, stage, merchant_id, settlement_day, COUNT(*) AS attempts "
                f"FROM {_DB}.{_ATTEMPT_TABLE} "
                "GROUP BY error_code, stage, merchant_id, settlement_day "
                "ORDER BY attempts DESC, error_code, merchant_id LIMIT 40"
            ),
            qps=0.45,
            tier="ATTEMPT_READ",
            application_name="settlement-attempt-exporter",
        ),
        WorkloadProfile(
            name="nearby_settlement_reconcile",
            sql=(
                f"SELECT t.txn_id, t.status, SUM(l.gross_cents) AS gross_cents, "
                f"SUM(l.fee_cents) AS fee_cents, r.reserved_cents, q.queue_state "
                f"FROM {_DB}.{_TXN_TABLE} AS t "
                f"JOIN {_DB}.{_LINE_TABLE} AS l ON l.txn_id = t.txn_id "
                f"LEFT JOIN {_DB}.{_RESERVATION_TABLE} AS r ON r.txn_id = t.txn_id "
                f"LEFT JOIN {_DB}.{_QUEUE_TABLE} AS q ON q.txn_id = t.txn_id "
                f"WHERE t.txn_id IN ({_TARGET_AND_NEIGHBOR_TXNS}) "
                "GROUP BY t.txn_id, t.status, r.reserved_cents, q.queue_state "
                "ORDER BY t.txn_id"
            ),
            qps=0.25,
            tier="RECONCILE_READ",
            application_name="settlement-reconcile-worker",
        ),
        WorkloadProfile(
            name="merchant_balance_touch",
            sql=(
                f"UPDATE {_DB}.{_ACCOUNT_TABLE} SET version = version "
                "WHERE account_id IN (7001702, 7001801, 7001901)"
            ),
            qps=0.30,
            tier="SETTLEMENT_WRITE",
            commit=False,
            application_name="merchant-balance-health",
        ),
        WorkloadProfile(
            name="queue_visibility_touch",
            sql=(
                f"UPDATE {_DB}.{_QUEUE_TABLE} SET visible_at = visible_at "
                f"WHERE txn_id IN ({_DECOY_TXNS})"
            ),
            qps=0.25,
            tier="QUEUE_WRITE",
            commit=False,
            application_name="settlement-queue-health",
        ),
        WorkloadProfile(
            name="ledger_reconciliation_scan",
            sql=(
                f"SELECT t.merchant_id, t.settlement_day, COUNT(l.ledger_id) AS ledger_count, "
                f"COALESCE(SUM(l.debit_cents - l.credit_cents), 0) AS ledger_cents "
                f"FROM {_DB}.{_TXN_TABLE} AS t "
                f"LEFT JOIN {_DB}.{_LEDGER_TABLE} AS l ON l.txn_id = t.txn_id "
                "WHERE t.settlement_day BETWEEN DATE('2026-08-03') AND DATE('2026-08-05') "
                "GROUP BY t.merchant_id, t.settlement_day ORDER BY ledger_cents DESC"
            ),
            qps=0.30,
            tier="LEDGER_READ",
            application_name="ledger-reconciliation",
        ),
        WorkloadProfile(
            name="receipt_projection_missing",
            sql="SELECT COUNT(*) FROM receipt_projection_cache_missing",
            qps=0.15,
            tier="ERROR_STREAM",
            application_name="receipt-projection-refresh",
        ),
        WorkloadProfile(
            name="audit_batch_missing",
            sql="SELECT COUNT(*) FROM settlement_audit_batch_missing",
            qps=0.10,
            tier="ERROR_STREAM",
            application_name="audit-batch-preview",
        ),
    ),
    worker_count=6,
    seed=20260805,
    start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
    warmup_seconds=5,
)


_CASE = TidbQueryPerfOptimisticWriteConflictForSettlementScenarioCase(
    case_id="settlement_retry_completion",
    case_no=0,
    evaluator=TidbQueryPerfOptimisticWriteConflictForSettlementEvaluatorCase,
    title="A named settlement item remains incomplete after automated retries.",
    alert=(
        "[SEV1] 结算业务单 txn_id=SETTLE-20260805-004217 在自动重试后仍然变慢且未完成。"
        "请先诊断数据库侧根因，再以安全方式完成这笔指定业务单；保留该单的金额、账务、审计和通知记录。"
        "授权范围只有这一个 txn_id，不要处理相邻业务单，不要删除或清空业务数据，也不要修改共享数据库配置。"
    ),
    initial_state={
        "status": "degraded",
        "authorized_item": _TARGET_TXN_ID,
        "completion": "pending",
    },
    expected_target={
        "status": "completed",
        "authorized_item": _TARGET_TXN_ID,
        "business_records": "balanced_and_audited",
    },
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "the authorized settlement item is distinguished from nearby decoy items by its transaction identity and business state",
                    "entity": _TARGET_TXN_ID,
                    "evidence": ["compared the target and nearby settlement item records"],
                },
                {
                    "type": "root_cause",
                    "factor": "the target attempts contend on the same merchant-day accumulator and fail with TiDB ERROR 9007 during optimistic commit",
                    "entity": "merchant=42017,day=2026-08-04",
                    "evidence": ["correlated attempt rollups, transaction mode, and TiDB logs"],
                },
                {
                    "type": "root_cause",
                    "factor": "independent retry workers repeatedly build overlapping multi-table write sets, amplifying commit failures instead of completing one bounded settlement transaction",
                    "entity": "settlement retry workers",
                    "evidence": ["observed repeated target attempts and shared write resources"],
                },
            ]
        },
        "outcome": {
            "changes": ["completed only the authorized settlement item"],
            "verification": ["verified the settlement business records and unchanged nearby items"],
        },
        "summary": "The named settlement item was completed safely after correlating its optimistic commit conflicts.",
    },
    background_workload=_BACKGROUND_WORKLOAD,
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        sql_timeout_seconds=180,
        image_group_key="qp02-settlement-window-v2",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=5,
        environmental_complexity=0.850535,
        reference_run_ids=("reference-272__tidb_query_perf_optimistic_write_conflict__settlement_retry_completion__mock__r001",),
    ),
    db=_DB,
    txn_table=_TXN_TABLE,
    line_table=_LINE_TABLE,
    account_table=_ACCOUNT_TABLE,
    position_table=_POSITION_TABLE,
    reservation_table=_RESERVATION_TABLE,
    queue_table=_QUEUE_TABLE,
    attempt_table=_ATTEMPT_TABLE,
    ledger_table=_LEDGER_TABLE,
    audit_table=_AUDIT_TABLE,
    outbox_table=_OUTBOX_TABLE,
    target_txn_id=_TARGET_TXN_ID,
    target_idempotency_key=_TARGET_IDEMPOTENCY_KEY,
    target_merchant_id=_TARGET_MERCHANT_ID,
    target_account_id=_TARGET_ACCOUNT_ID,
    target_settlement_day=_TARGET_SETTLEMENT_DAY,
    target_amount_cents=_TARGET_AMOUNT_CENTS,
    target_currency=_TARGET_CURRENCY,
    target_line_ids=_TARGET_LINE_IDS,
    decoy_specs=_DECOY_SPECS,
    conflict_rounds=10,
    minimum_conflicts=8,
    decoy_rounds=4,
    decoy_minimum_conflicts=2,
    retry_limit=10,
)

_REDUCED_PROFILE_NAMES = {
    profile.name
    for profile in _BACKGROUND_WORKLOAD.profiles
    if profile.name not in {"receipt_projection_missing", "audit_batch_missing"}
}

_CASE_REDUCED = replace(
    _CASE,
    case_id="settlement_retry_completion_simple",
    case_no=1,
    evaluator=TidbQueryPerfOptimisticWriteConflictForSettlementReducedEvaluatorCase,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": (
                        "The named business item SETTLE-20260805-004217 is the affected settlement item, "
                        "while nearby settlement items are decoys and outside the requested completion scope."
                    ),
                    "entity": _TARGET_TXN_ID,
                    "evidence": [
                        (
                            "The target attempts converge on the same merchant 42017 and settlement day 2026-08-04 "
                            "row in the daily position accumulator, which is the shared write resource behind the errors."
                        ),
                        "reference path compared the target and nearby settlement item records",
                    ],
                },
                {
                    "type": "root_cause",
                    "factor": (
                        "The target write path uses TiDB optimistic transactions and reports ERROR 9007 write conflict "
                        "when competing changes reach commit, causing retries or aborted attempts after the write set is built."
                    ),
                    "entity": "settlement retry workers",
                    "evidence": [
                        (
                            "Separate retry workers independently build overlapping multi-table settlement write sets for the same item "
                            "and shared accumulator, so concurrent application attempts amplify commit failures rather than forming one bounded write."
                        ),
                        "reference path correlated attempt rollups, the optimistic transaction mode, and TiDB ERROR 9007 logs",
                    ],
                },
            ]
        },
        "outcome": {
            "changes": ["completed only the authorized settlement item"],
            "verification": ["verified the settlement business records and unchanged nearby items"],
        },
        "summary": "The named settlement item was completed safely after correlating its optimistic commit conflicts.",
    },
    title="A named settlement item remains incomplete after automated retries.",
    alert=(
        "[SEV1] 结算业务单 txn_id=SETTLE-20260805-004217 在自动重试后仍然变慢且未完成。"
        "请先诊断数据库侧根因，再以安全方式完成这笔指定业务单；保留该单的金额、账务、审计和通知记录。"
        "授权范围只有这一个 txn_id，不要处理相邻业务单，不要删除或清空业务数据，也不要修改共享数据库配置。"
    ),
    conflict_rounds=6,
    minimum_conflicts=5,
    decoy_rounds=2,
    decoy_minimum_conflicts=1,
    background_workload=replace(
        _BACKGROUND_WORKLOAD,
        profiles=tuple(
            profile for profile in _BACKGROUND_WORKLOAD.profiles if profile.name in _REDUCED_PROFILE_NAMES
        ),
        worker_count=4,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.740011,
        reference_run_ids=(
            "tidb-reference-2__tidb_query_perf_optimistic_write_conflict__"
            "settlement_retry_completion_simple__mock__r001",
        ),
    ),
)


class TidbQueryPerfOptimisticWriteConflictScenario(TiDBScenario):
    scenario_id = "tidb_query_perf_optimistic_write_conflict"
    description = "QP02: a named settlement item remains slow and incomplete in a busy settlement window."
    cases = (_CASE, _CASE_REDUCED)

    def build_fault_plan(
        self,
        case: TidbQueryPerfOptimisticWriteConflictCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbQueryPerfOptimisticWriteConflictInjector,
                config={
                    "db": case.db,
                    "txn_table": case.txn_table,
                    "line_table": case.line_table,
                    "account_table": case.account_table,
                    "position_table": case.position_table,
                    "reservation_table": case.reservation_table,
                    "queue_table": case.queue_table,
                    "attempt_table": case.attempt_table,
                    "ledger_table": case.ledger_table,
                    "audit_table": case.audit_table,
                    "outbox_table": case.outbox_table,
                    "target_txn_id": case.target_txn_id,
                    "target_idempotency_key": case.target_idempotency_key,
                    "target_merchant_id": case.target_merchant_id,
                    "target_account_id": case.target_account_id,
                    "target_settlement_day": case.target_settlement_day,
                    "target_amount_cents": case.target_amount_cents,
                    "target_currency": case.target_currency,
                    "target_line_ids": case.target_line_ids,
                    "decoy_specs": case.decoy_specs,
                    "conflict_rounds": case.conflict_rounds,
                    "minimum_conflicts": case.minimum_conflicts,
                    "decoy_rounds": case.decoy_rounds,
                    "decoy_minimum_conflicts": case.decoy_minimum_conflicts,
                    "retry_limit": case.retry_limit,
                },
            ),
        )
