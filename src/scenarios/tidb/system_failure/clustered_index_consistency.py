import json
from collections.abc import Mapping
from dataclasses import dataclass, replace

from src.scenarios.base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)
from src.scenarios.evaluation.tidb.system_failure.clustered_index_consistency import (
    TidbSystemFailureClusteredIndexConsistencyEvaluatorCase,
    TidbSystemFailureClusteredIndexConsistencyRecoveryEvaluatorCase,
)
from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.tidb.common import (
    connect_tidb,
    json_object,
    require_sql_success,
    validate_sql_identifier,
)
from src.scenarios.tidb.runtime import (
    TIDB_V6_5_0,
    TIDB_V7_5_0,
    canonical_tidb_version,
    tidb_runtime,
)
from src.scenarios.workloads import WorkloadProfile


_DATABASE = "benchops"
_TARGET_TABLE = "k12_account_state"
_LEDGER_TABLE = "k12_account_events"
_HEALTHY_NONCLUSTERED_TABLE = "k12_healthy_nonclustered"
_HEALTHY_NO_ODKU_TABLE = "k12_healthy_no_odku"
_CANARY_PLAN_TABLE = "k12_canary_plan"
_TARGET_INDEX = "idx_account_status"
_TARGET_ACCOUNT_IDS = (101, 102)
_AUTOCOMMIT_CANARY_ACCOUNT_ID = 501
_EXPLICIT_CANARY_ACCOUNT_ID = 502
_AUTOCOMMIT_CANARY_TIMESTAMP = "2026-08-02 00:00:00"
_EXPLICIT_CANARY_TIMESTAMP = "2026-08-03 00:00:00"
_SEED_STATUS = "OPEN"
_SEED_BALANCE_CENTS = 10000
_CANARY_BALANCE_CENTS = 50000


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureClusteredIndexConsistencyForOdkuMutableClusteredPkIndexDriftScenarioCase(TiDBScenarioCase):
    database: str
    target_table: str
    ledger_table: str
    healthy_nonclustered_table: str
    healthy_no_odku_table: str
    canary_plan_table: str
    target_index: str
    target_account_ids: tuple[int, ...]
    autocommit_canary_account_id: int
    explicit_canary_account_id: int
    autocommit_canary_timestamp: str
    explicit_canary_timestamp: str
    seed_status: str
    seed_balance_cents: int
    canary_balance_cents: int
    source_version: str
    target_version: str


def _workload_profiles(
    *,
    database: str = _DATABASE,
    target_table: str = _TARGET_TABLE,
    ledger_table: str = _LEDGER_TABLE,
    healthy_nonclustered_table: str = _HEALTHY_NONCLUSTERED_TABLE,
    healthy_no_odku_table: str = _HEALTHY_NO_ODKU_TABLE,
) -> tuple[WorkloadProfile, ...]:
    target = f"{database}.{target_table}"
    ledger = f"{database}.{ledger_table}"
    healthy_nonclustered = f"{database}.{healthy_nonclustered_table}"
    healthy_no_odku = f"{database}.{healthy_no_odku_table}"
    return (
        WorkloadProfile(
            name="k12_target_primary_probe",
            sql=(
                f"SELECT account_id, status, balance_cents, version FROM {target} "
                "ORDER BY account_id, state_ts"
            ),
            qps=0.45,
            tier="K12_TARGET_READ",
            application_name="account-state-api",
        ),
        WorkloadProfile(
            name="k12_target_secondary_probe",
            sql=(
                f"SELECT account_id, status, balance_cents, version FROM {target} "
                f"USE INDEX ({_TARGET_INDEX}) ORDER BY account_id, state_ts"
            ),
            qps=0.35,
            tier="K12_TARGET_INDEX_READ",
            application_name="account-index-reader",
        ),
        WorkloadProfile(
            name="k12_ledger_audit",
            sql=(
                f"SELECT account_id, event_state, version FROM {ledger} "
                "ORDER BY event_id"
            ),
            qps=0.30,
            tier="K12_LEDGER",
            application_name="account-ledger-audit",
        ),
        WorkloadProfile(
            name="k12_nonclustered_health_probe",
            sql=(
                f"SELECT account_id, state_ts, version FROM {healthy_nonclustered} "
                "ORDER BY account_id"
            ),
            qps=0.25,
            tier="K12_HEALTHY_NEIGHBOR",
            application_name="account-health-monitor",
        ),
        WorkloadProfile(
            name="k12_no_odku_health_probe",
            sql=(
                f"SELECT account_id, state_ts, version FROM {healthy_no_odku} "
                "ORDER BY account_id"
            ),
            qps=0.25,
            tier="K12_HEALTHY_NEIGHBOR",
            application_name="account-reconciliation",
        ),
    )


_CASE = TidbSystemFailureClusteredIndexConsistencyForOdkuMutableClusteredPkIndexDriftScenarioCase(
    case_id="odku_mutable_clustered_pk_index_drift",
    case_no=0,
    evaluator=TidbSystemFailureClusteredIndexConsistencyEvaluatorCase,
    title="Account state writes fail while clustered and secondary index paths disagree.",
    alert=(
        "告警：账户状态服务在一次批量状态写入后出现间歇性写入失败，部分读取路径返回的状态不能互相解释，"
        "但 PD、TiKV、TiDB 服务仍可用。请先在 benchops.k12_account_state 事故边界内止写并保留取证，"
        "区分当前故障与 k12_healthy_nonclustered、k12_healthy_no_odku 两个健康近邻；"
        "k12_account_events 是只追加的业务账本，不能修改或删除。"
        "只有完成取证、版本处置和数据修复后，才允许使用 k12_canary_plan 中声明的 account_id 501（autocommit）"
        "和 502（显式事务）执行新的 ODKU canary；不要重启组件、删除 TiKV key、或对全库做无界重建。"
    ),
    initial_state={
        "reported_service": "account state API",
        "target": f"{_DATABASE}.{_TARGET_TABLE}",
        "symptom": "ODKU writes report an assertion failure and index-backed reads are not self-consistent",
        "cluster_surface": "PD, TiKV and TiDB remain reachable",
        "protected_truth": f"{_DATABASE}.{_LEDGER_TABLE} is append-only",
        "authorized_recovery_writes": "only the two canaries declared by k12_canary_plan after repair",
    },
    expected_target={
        "source_version": "v6.5.0",
        "target_version": "v7.5.0",
        "assertion_level": "STRICT",
        "canonical_source": f"{_DATABASE}.{_LEDGER_TABLE}",
        "consistency_check": "ADMIN CHECK TABLE succeeds",
        "canaries": "one autocommit and one explicit-transaction ODKU path succeed",
        "healthy_neighbors_preserved": True,
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=_workload_profiles(),
        worker_count=4,
        seed=0x51205,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=4.0,
    ),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "k12_mutable_clustered_pk_index_drift",
                    "entity": f"{_DATABASE}.{_TARGET_TABLE}",
                    "evidence": [
                        "repeated ODKU omits the ON UPDATE clustered handle column and the vulnerable release returns 8141",
                        "ADMIN CHECK TABLE reports a mismatch between the clustered record and idx_account_status",
                    ],
                },
                {
                    "type": "finding",
                    "factor": "historical_drift_and_future_write_risk",
                    "entity": f"{_DATABASE}.{_TARGET_TABLE}",
                    "evidence": [
                        "existing drift remains after setting assertion level and new ODKU writes must be stopped until repair",
                    ],
                },
                {
                    "type": "finding",
                    "factor": "assertion_level_scope",
                    "entity": "all TiDB SQL endpoints",
                    "evidence": [
                        "global and session tidb_txn_assertion_level must be checked on every endpoint",
                    ],
                },
                {
                    "type": "finding",
                    "factor": "vulnerable_fixed_release",
                    "entity": "TiDB cluster",
                    "evidence": [
                        "the reproducible v6.5.0 image is vulnerable and the v7.5.0 image contains the handleChanged fix",
                    ],
                },
                {
                    "type": "finding",
                    "factor": "canonical_ledger_truth",
                    "entity": f"{_DATABASE}.{_LEDGER_TABLE}",
                    "evidence": [
                        "append-only applied ledger events are the business truth used to decide which row values to preserve",
                    ],
                },
                {
                    "type": "finding",
                    "factor": "repair_strategy_selection",
                    "entity": f"{_DATABASE}.{_TARGET_TABLE}",
                    "evidence": [
                        "the trusted clustered record permits rebuilding all secondary indexes; an untrusted handle requires logical reconstruction from the ledger",
                    ],
                },
                {
                    "type": "finding",
                    "factor": "closed_loop_consistency_acceptance",
                    "entity": f"{_DATABASE}.{_TARGET_TABLE}",
                    "evidence": [
                        "ADMIN CHECK, forced primary and secondary paths, ledger truth, both ODKU canaries and healthy neighbors all pass",
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "Stopped target ODKU writes, preserved the ledger and forensic index-path evidence, and upgraded every database component from v6.5.0 to v7.5.0.",
                "Set tidb_txn_assertion_level to STRICT on the cluster and rebuilt the affected secondary index from the trusted clustered records.",
                "Ran the authorized autocommit and explicit-transaction ODKU canaries only after repair.",
            ],
            "verification": [
                "All TiDB endpoints report the fixed release and both global and session assertion levels are STRICT.",
                "ADMIN CHECK TABLE, forced index paths, ledger truth, healthy neighbors and both new canaries pass.",
            ],
        },
        "summary": "The clustered primary-key and secondary-index inconsistency was diagnosed from raw SQL evidence and closed with trusted final-state checks.",
    },
    runtime=tidb_runtime(
        release=TIDB_V6_5_0,
        upgrade_release=TIDB_V7_5_0,
        pd_count=1,
        tikv_count=2,
        tidb_count=1,
        sql_timeout_seconds=300,
        tikv_memory_mb=2048,
        tidb_memory_mb=1024,
        bootstrap_cache_enabled=False,
        readiness_timeout_seconds=900,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.611111,
        reference_run_ids=(
            "reference-279__tidb_system_failure_clustered_index_consistency__odku_mutable_clustered_pk_index_drift__mock__r001",
        ),
    ),
    database=_DATABASE,
    target_table=_TARGET_TABLE,
    ledger_table=_LEDGER_TABLE,
    healthy_nonclustered_table=_HEALTHY_NONCLUSTERED_TABLE,
    healthy_no_odku_table=_HEALTHY_NO_ODKU_TABLE,
    canary_plan_table=_CANARY_PLAN_TABLE,
    target_index=_TARGET_INDEX,
    target_account_ids=_TARGET_ACCOUNT_IDS,
    autocommit_canary_account_id=_AUTOCOMMIT_CANARY_ACCOUNT_ID,
    explicit_canary_account_id=_EXPLICIT_CANARY_ACCOUNT_ID,
    autocommit_canary_timestamp=_AUTOCOMMIT_CANARY_TIMESTAMP,
    explicit_canary_timestamp=_EXPLICIT_CANARY_TIMESTAMP,
    seed_status=_SEED_STATUS,
    seed_balance_cents=_SEED_BALANCE_CENTS,
    canary_balance_cents=_CANARY_BALANCE_CENTS,
    source_version="v6.5.0",
    target_version="v7.5.0",
)


class TidbSystemFailureClusteredIndexConsistencyInjector(BaseFaultInjector):
    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._create_schema()
        self._seed_ledger_and_health()
        self._set_vulnerable_assertion_level()
        self._trigger_autocommit_drift()
        self._trigger_explicit_transaction_drift()
        self._verify_fault()

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_vulnerable_release()
        self._verify_fault()

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        target = f"{self.database}.{self.target_table}"
        ledger = f"{self.database}.{self.ledger_table}"
        healthy_nonclustered = f"{self.database}.{self.healthy_nonclustered_table}"
        healthy_no_odku = f"{self.database}.{self.healthy_no_odku_table}"
        admin_check = self._read_json(
            self.env.execute_sql(f"ADMIN CHECK TABLE {target}"),
            "K12 prepare ADMIN CHECK TABLE",
        )
        healthy_truth = json_object(
            self.env.execute_sql(
                f"SELECT account_id, state_ts, version FROM {healthy_nonclustered} ORDER BY account_id"
            ),
            "K12 capture healthy nonclustered truth",
        )
        healthy_no_odku_truth = json_object(
            self.env.execute_sql(
                f"SELECT account_id, state_ts, version FROM {healthy_no_odku} ORDER BY account_id"
            ),
            "K12 capture healthy no-ODKU truth",
        )
        ledger_truth = json_object(
            self.env.execute_sql(
                f"SELECT event_id, account_id, event_state, status, balance_cents, version "
                f"FROM {ledger} ORDER BY event_id"
            ),
            "K12 capture append-only ledger truth",
        )
        primary_rows = json_object(
            self.env.execute_sql(
                f"SELECT account_id, state_ts, status, balance_cents, version FROM {target} "
                "USE INDEX (PRIMARY) ORDER BY account_id, state_ts"
            ),
            "K12 capture clustered primary path",
        )
        secondary_rows = json_object(
            self.env.execute_sql(
                f"SELECT account_id, state_ts, status, balance_cents, version FROM {target} "
                f"USE INDEX ({self.target_index}) ORDER BY account_id, state_ts"
            ),
            "K12 capture secondary index path",
        )
        return {
            "k12_admin_check_status": admin_check["status"],
            "k12_admin_check_error": str(admin_check.get("error", "")),
            "k12_target_primary_rows": primary_rows["result"],
            "k12_target_secondary_rows": secondary_rows["result"],
            "k12_ledger_rows": ledger_truth["result"],
            "k12_healthy_nonclustered_truth": healthy_truth["result"],
            "k12_healthy_no_odku_truth": healthy_no_odku_truth["result"],
            "k12_source_version": self.source_version,
            "k12_autocommit_error_code": 8141,
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        require_sql_success(
            self.env.execute_sql(f"DROP DATABASE IF EXISTS {self.database}"),
            f"drop K12 database {self.database}",
        )

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.database = validate_sql_identifier(str(config["database"]), "database")
        self.target_table = validate_sql_identifier(str(config["target_table"]), "target_table")
        self.ledger_table = validate_sql_identifier(str(config["ledger_table"]), "ledger_table")
        self.healthy_nonclustered_table = validate_sql_identifier(
            str(config["healthy_nonclustered_table"]), "healthy_nonclustered_table"
        )
        self.healthy_no_odku_table = validate_sql_identifier(
            str(config["healthy_no_odku_table"]), "healthy_no_odku_table"
        )
        self.canary_plan_table = validate_sql_identifier(
            str(config["canary_plan_table"]), "canary_plan_table"
        )
        self.target_index = validate_sql_identifier(str(config["target_index"]), "target_index")
        self.target_account_ids = tuple(int(value) for value in config["target_account_ids"])
        self.autocommit_canary_account_id = int(config["autocommit_canary_account_id"])
        self.explicit_canary_account_id = int(config["explicit_canary_account_id"])
        self.autocommit_canary_timestamp = str(config["autocommit_canary_timestamp"])
        self.explicit_canary_timestamp = str(config["explicit_canary_timestamp"])
        self.seed_status = str(config["seed_status"])
        self.seed_balance_cents = int(config["seed_balance_cents"])
        self.canary_balance_cents = int(config["canary_balance_cents"])
        self.source_version = str(config["source_version"])

    def _create_schema(self) -> None:
        database = self.database
        target = f"{database}.{self.target_table}"
        ledger = f"{database}.{self.ledger_table}"
        healthy_nonclustered = f"{database}.{self.healthy_nonclustered_table}"
        healthy_no_odku = f"{database}.{self.healthy_no_odku_table}"
        canary_plan = f"{database}.{self.canary_plan_table}"
        statements = (
            f"DROP DATABASE IF EXISTS {database}",
            f"CREATE DATABASE {database}",
            f"CREATE TABLE {target} ("
            "account_id BIGINT NOT NULL, "
            "state_ts TIMESTAMP(0) NOT NULL ON UPDATE CURRENT_TIMESTAMP(0), "
            "status VARCHAR(32) NOT NULL, "
            "balance_cents BIGINT NOT NULL, "
            "version BIGINT NOT NULL, "
            "PRIMARY KEY (state_ts, account_id) CLUSTERED, "
            f"KEY {self.target_index} (account_id, status, state_ts)"
            ")",
            f"CREATE TABLE {healthy_nonclustered} ("
            "account_id BIGINT NOT NULL, "
            "state_ts TIMESTAMP(0) NOT NULL ON UPDATE CURRENT_TIMESTAMP(0), "
            "status VARCHAR(32) NOT NULL, balance_cents BIGINT NOT NULL, version BIGINT NOT NULL, "
            "PRIMARY KEY (account_id) NONCLUSTERED, "
            f"KEY {self.target_index} (account_id, status, state_ts)"
            ")",
            f"CREATE TABLE {healthy_no_odku} ("
            "account_id BIGINT NOT NULL, "
            "state_ts TIMESTAMP(0) NOT NULL ON UPDATE CURRENT_TIMESTAMP(0), "
            "status VARCHAR(32) NOT NULL, balance_cents BIGINT NOT NULL, version BIGINT NOT NULL, "
            "PRIMARY KEY (state_ts, account_id) CLUSTERED, "
            f"KEY {self.target_index} (account_id, status, state_ts)"
            ")",
            f"CREATE TABLE {ledger} ("
            "event_id BIGINT PRIMARY KEY, account_id BIGINT NOT NULL, "
            "event_state VARCHAR(16) NOT NULL, event_kind VARCHAR(32) NOT NULL, "
            "status VARCHAR(32) NOT NULL, balance_cents BIGINT NOT NULL, version BIGINT NOT NULL, "
            "state_ts TIMESTAMP(0) NOT NULL, written_at TIMESTAMP(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0), "
            "KEY idx_ledger_account (account_id, event_id)"
            ")",
            f"CREATE TABLE {canary_plan} ("
            "canary_id VARCHAR(32) PRIMARY KEY, account_id BIGINT NOT NULL, "
            "execution_path VARCHAR(32) NOT NULL, seed_state_ts TIMESTAMP(0) NOT NULL, "
            "repeat_count INT NOT NULL, expected_version BIGINT NOT NULL, "
            "status VARCHAR(32) NOT NULL, balance_cents BIGINT NOT NULL"
            ")",
        )
        for statement in statements:
            require_sql_success(self.env.execute_sql(statement), f"K12 schema statement: {statement}")

    def _seed_ledger_and_health(self) -> None:
        database = self.database
        target = f"{database}.{self.target_table}"
        ledger = f"{database}.{self.ledger_table}"
        healthy_nonclustered = f"{database}.{self.healthy_nonclustered_table}"
        healthy_no_odku = f"{database}.{self.healthy_no_odku_table}"
        canary_plan = f"{database}.{self.canary_plan_table}"
        for account_id, timestamp in zip(self.target_account_ids, ("2026-08-01 00:00:00", "2026-08-01 00:00:01")):
            event_state, event_kind = {
                self.target_account_ids[0]: ("attempted", "odku_failed"),
                self.target_account_ids[1]: ("applied", "odku_committed"),
            }[account_id]
            require_sql_success(
                self.env.execute_sql(
                    f"INSERT INTO {ledger} "
                    "(event_id, account_id, event_state, event_kind, status, balance_cents, version, state_ts) "
                    f"VALUES ({account_id}00, {account_id}, 'applied', 'initial', "
                    f"'{self.seed_status}', {self.seed_balance_cents}, 1, '{timestamp}'), "
                    f"({account_id}01, {account_id}, 'applied', 'odku_applied', "
                    f"'{self.seed_status}', {self.seed_balance_cents}, 2, '{timestamp}'), "
                    f"({account_id}02, {account_id}, '{event_state}', '{event_kind}', "
                    f"'{self.seed_status}', {self.seed_balance_cents}, 3, '{timestamp}')"
                ),
                f"seed K12 ledger account {account_id}",
            )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {healthy_nonclustered} "
                "(account_id, state_ts, status, balance_cents, version) VALUES "
                f"(201, '2026-08-01 00:00:00', '{self.seed_status}', {self.seed_balance_cents}, 1), "
                f"(202, '2026-08-01 00:00:01', '{self.seed_status}', {self.seed_balance_cents}, 1)"
            ),
            "seed K12 healthy nonclustered table",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {healthy_no_odku} "
                "(account_id, state_ts, status, balance_cents, version) VALUES "
                f"(301, '2026-08-01 00:00:00', '{self.seed_status}', {self.seed_balance_cents}, 1), "
                f"(302, '2026-08-01 00:00:01', '{self.seed_status}', {self.seed_balance_cents}, 1)"
            ),
            "seed K12 healthy no-ODKU table",
        )
        require_sql_success(
            self.env.execute_sql(
                f"INSERT INTO {canary_plan} "
                "(canary_id, account_id, execution_path, seed_state_ts, repeat_count, expected_version, status, balance_cents) VALUES "
                f"('autocommit', {self.autocommit_canary_account_id}, 'autocommit', '{self.autocommit_canary_timestamp}', 2, 2, "
                f"'{self.seed_status}', {self.canary_balance_cents}), "
                f"('explicit_txn', {self.explicit_canary_account_id}, 'explicit_transaction', '{self.explicit_canary_timestamp}', 3, 3, "
                f"'{self.seed_status}', {self.canary_balance_cents})"
            ),
            "seed K12 canary plan",
        )
        target_rows = json_object(
            self.env.execute_sql(f"SELECT COUNT(*) FROM {target}"),
            "verify K12 target starts empty",
        )
        if target_rows["result"] != [[0]]:
            raise RuntimeError(f"K12 target table was not empty before fault injection: rows={target_rows!r}")

    def _set_vulnerable_assertion_level(self) -> None:
        require_sql_success(
            self.env.execute_sql("SET GLOBAL tidb_txn_assertion_level = 'FAST'"),
            "set K12 vulnerable assertion level",
        )

    def _odku_statement(self, account_id: int, timestamp: str, version: int) -> str:
        return (
            f"INSERT INTO {self.database}.{self.target_table} "
            "(account_id, state_ts, status, balance_cents, version) "
            f"VALUES ({account_id}, '{timestamp}', '{self.seed_status}', {self.seed_balance_cents}, {version}) "
            "ON DUPLICATE KEY UPDATE "
            "status = VALUES(status), balance_cents = VALUES(balance_cents), version = VALUES(version)"
        )

    def _trigger_autocommit_drift(self) -> None:
        account_id = self.target_account_ids[0]
        timestamp = "2026-08-01 00:00:00"
        for version in (1, 2):
            require_sql_success(
                self.env.execute_sql(self._odku_statement(account_id, timestamp, version)),
                f"K12 autocommit ODKU version {version}",
            )
        self._expect_8141(
            self.env.execute_sql(self._odku_statement(account_id, timestamp, 3)),
            "K12 autocommit third ODKU",
        )

    def _trigger_explicit_transaction_drift(self) -> None:
        account_id = self.target_account_ids[1]
        timestamp = "2026-08-01 00:00:01"
        with connect_tidb(self.env, database=self.database, autocommit=False) as connection:
            with connection.cursor() as cursor:
                for version in (1, 2, 3):
                    cursor.execute(self._odku_statement(account_id, timestamp, version))
            connection.commit()

    def _verify_fault(self) -> None:
        target = f"{self.database}.{self.target_table}"
        self._verify_vulnerable_release()
        admin_check = self._read_json(
            self.env.execute_sql(f"ADMIN CHECK TABLE {target}"),
            "verify K12 ADMIN CHECK TABLE fault",
        )
        if admin_check["status"] != "error" or "8134" not in str(admin_check.get("error", "")):
            raise RuntimeError(
                "K12 fault did not produce the expected consistency-check error: "
                f"target={target!r}, response={admin_check!r}"
            )

    def _verify_vulnerable_release(self) -> None:
        payload = self._read_json(self.env.observe_metric("cluster_info"), "read K12 cluster version")
        versions = {
            canonical_tidb_version(row["VERSION"])
            for row in payload["snapshot"]["nodes"]
        }
        expected_version = canonical_tidb_version(self.source_version)
        if versions != {expected_version}:
            raise RuntimeError(
                "K12 injector requires the vulnerable release on every component: "
                f"expected={self.source_version!r}, observed={sorted(versions)!r}"
            )

    @staticmethod
    def _read_json(result: object, context: str) -> dict:
        if not isinstance(result, str):
            raise TypeError(f"{context} expected a JSON string, got {type(result).__name__}")
        payload = json.loads(result)
        if not isinstance(payload, dict):
            raise TypeError(f"{context} expected a JSON object, got {type(payload).__name__}")
        return payload

    @staticmethod
    def _expect_8141(result: object, context: str) -> None:
        if not isinstance(result, str):
            raise TypeError(f"{context} expected a JSON string, got {type(result).__name__}")
        payload = json.loads(result)
        if not isinstance(payload, dict) or payload.get("status") != "error" or "8141" not in str(payload.get("error", "")):
            raise RuntimeError(f"{context} did not return TiDB ERROR 8141: response={payload!r}")


class TidbSystemFailureClusteredIndexConsistencyScenario(TiDBScenario):
    scenario_id = "tidb_system_failure_clustered_index_consistency"
    description = (
        "Repair a real TiDB clustered-primary-key and secondary-index consistency fault caused by vulnerable ODKU handling."
    )
    cases = (_CASE, replace(_CASE, case_id="clustered_index_consistency_recovery", case_no=1,
                            evaluator=TidbSystemFailureClusteredIndexConsistencyRecoveryEvaluatorCase,
                            difficulty=DifficultyCalibration(
                                diagnostic_depth=6,
                                environmental_complexity=0.5,
                                reference_run_ids=('reference-80__tidb_system_failure_clustered_index_consistency__clustered_index_consistency_recovery__mock__r001',),
                                protocol_version='difficulty-v2',
                            ),
                            background_workload=replace(_CASE.background_workload, worker_count=2, seed=0x51206)))

    def build_fault_plan(
        self,
        case: TidbSystemFailureClusteredIndexConsistencyForOdkuMutableClusteredPkIndexDriftScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureClusteredIndexConsistencyInjector,
                config={
                    "database": case.database,
                    "target_table": case.target_table,
                    "ledger_table": case.ledger_table,
                    "healthy_nonclustered_table": case.healthy_nonclustered_table,
                    "healthy_no_odku_table": case.healthy_no_odku_table,
                    "canary_plan_table": case.canary_plan_table,
                    "target_index": case.target_index,
                    "target_account_ids": case.target_account_ids,
                    "autocommit_canary_account_id": case.autocommit_canary_account_id,
                    "explicit_canary_account_id": case.explicit_canary_account_id,
                    "autocommit_canary_timestamp": case.autocommit_canary_timestamp,
                    "explicit_canary_timestamp": case.explicit_canary_timestamp,
                    "seed_status": case.seed_status,
                    "seed_balance_cents": case.seed_balance_cents,
                    "canary_balance_cents": case.canary_balance_cents,
                    "source_version": case.source_version,
                },
            ),
        )


__all__ = (
    "TidbSystemFailureClusteredIndexConsistencyForOdkuMutableClusteredPkIndexDriftScenarioCase",
    "TidbSystemFailureClusteredIndexConsistencyInjector",
    "TidbSystemFailureClusteredIndexConsistencyScenario",
)
