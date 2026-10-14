from collections.abc import Mapping
from dataclasses import dataclass, replace
import hashlib
import json
import threading
import time
import zlib

import pymysql

from src.scenarios.evaluation.tidb.system_failure.slow_store_lock_ttl import (
    TidbSystemFailureSf02EvaluatorCase,
    TidbSystemFailureSf02FocusedEvaluatorCase,
)
from src.scenarios.tidb.common import (
    BaseFaultInjector,
    FaultLifecycleContext,
    connect_tidb,
    join_thread,
    json_object,
    require_sql_success,
    run_sql_batches,
    validate_sql_identifier,
)
from src.workloads.specs import BackgroundWorkloadStartPhase, WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime

SF02_TARGET_RETRY_PAYLOAD = "settled-after-storage-retry"


def sf02_order_amount(order_id: int) -> int:
    return 100 + (order_id * 17) % 900


def sf02_order_crc(order_id: int) -> int:
    return (order_id * 2654435761) & 0xFFFFFFFF


def sf02_retry_order_crc(order_id: int) -> int:
    return sf02_order_crc(order_id) ^ 0xC0FFEE42


def sf02_payload_value(table_index: int, event_id: int) -> str:
    return f"payload-{table_index}-{event_id:04d}"


def sf02_payload_crc(table_index: int, event_id: int, payload: str, state: str) -> int:
    return zlib.crc32(f"{table_index}:{event_id}:{payload}:{state}".encode())


def sf02_retry_payload_value(
    table_index: int,
    event_id: int,
    retry_payload: str = SF02_TARGET_RETRY_PAYLOAD,
) -> str:
    return f"{retry_payload}-{table_index}-{event_id:04d}"


def sf02_retry_payload_crc(
    table_index: int,
    event_id: int,
    retry_payload: str = SF02_TARGET_RETRY_PAYLOAD,
) -> int:
    return sf02_payload_crc(
        table_index,
        event_id,
        sf02_retry_payload_value(table_index, event_id, retry_payload),
        "applied",
    )


def sf02_expected_payload_checksum(
    table_index: int,
    workset_rows: int,
    retry_payload: str = SF02_TARGET_RETRY_PAYLOAD,
) -> tuple[int, int, int]:
    checksums = [
        sf02_retry_payload_crc(table_index, event_id, retry_payload)
        for event_id in range(1, workset_rows + 1)
    ]
    checksum = 0
    for value in checksums:
        checksum ^= value
    return len(checksums), sum(checksums), checksum


def sf02_primary_key_hash(table: str, event_id: int) -> str:
    return hashlib.sha256(f"{table}:event_id={event_id}".encode()).hexdigest()[:16]


def sf02_io_limiter_signature(config: Mapping[str, object]) -> dict[str, object]:
    return {key: config[key] for key in ("max-bytes-per-sec", "mode", "strict")}


def sf02_base_amount_sum(row_count: int) -> int:
    return sum(sf02_order_amount(order_id) for order_id in range(1, row_count + 1))


def sf02_base_checksum(row_count: int) -> int:
    checksum = 0
    for order_id in range(1, row_count + 1):
        checksum ^= sf02_order_crc(order_id)
    return checksum


SF02_ORDER_STATES = ("open", "settled")
SF02_SETTLEMENT_JOB_STATES = ("retry_required", "settled", "processing", "committed")
SF02_SETTLEMENT_LEDGER_STATES = ("applied",)
SF02_SETTLEMENT_PAYLOAD_STATES = ("ready", "processing", "applied")


def _sql_state_values(states: tuple[str, ...]) -> str:
    return ", ".join(f"'{state}'" for state in states)


class TidbSystemFailureSf02SlowStoreInjector(BaseFaultInjector):
    """Throttle one real TiKV Store and generate a real 2PC lock-loss commit failure."""

    _PAYLOAD_ROWS = tuple(range(1, 33))
    _TAIL_ROWS = tuple(range(33, 65))
    _PAYLOAD_B_ROWS = 4096
    _TAIL_CYCLES = 4
    _PRELOCK_MAX_BYTES = "1MiB"
    _FAULT_MAX_BYTES = "256KiB"
    _FAULT_MODE = "write-only"
    _LOCK_TTL_MS = 3000
    _TXN_COMMIT_WAIT_SECONDS = 240
    _TARGET_PREPARE_TIMEOUT_SECONDS = 180
    _LOCK_REAPER_START_DELAY_SECONDS = 1
    _NEAR_STORE_SETTLE_POLLS = 18
    _NEAR_STORE_SETTLE_POLL_SECONDS = 10
    _NEAR_STORE_SETTLE_STABLE_READS = 3
    _PEER_REPAIR_TIMEOUT_SECONDS = 240

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._setup_tables(context.env)
        self._resolve_target_store(context.env)
        self._start_store_throttle(context.env)
        self._run_target_transaction(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        state = self._state
        if state["target_node"] != self.target_node:
            raise RuntimeError(
                "SF02 activation target changed: "
                f"registered={state['target_node']!r}, resolved={self.target_node!r}"
            )
        self._verify_tables(context.env)
        observed = context.env.tikv_io_rate_limit(self.target_node)
        if sf02_io_limiter_signature(observed) == sf02_io_limiter_signature(state["baseline_io_config"]):
            raise RuntimeError(
                "SF02 activation expected the target TiKV I/O limit to remain active: "
                f"target={self.target_node!r}, baseline={state['baseline_io_config']!r}, "
                f"observed={observed!r}"
            )

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        state = self._state
        if not state["failure_observed"]:
            raise RuntimeError(
                "SF02 observability cannot be prepared before a real target commit failure: "
                f"target={state['target_node']!r}, transaction={state['transaction']!r}"
            )
        self._repair_contract_region_peers(context.env)
        stores = context.env.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
        primary_detail = self._pd_region(context.env, self.primary_region_id)
        peer_store_ids = tuple(sorted(int(peer["store_id"]) for peer in primary_detail["peers"]))
        order_detail = self._pd_region(context.env, self.order_region_id)
        order_peer_store_ids = tuple(sorted(int(peer["store_id"]) for peer in order_detail["peers"]))
        if len(peer_store_ids) != 3 or len(order_peer_store_ids) != 3:
            raise RuntimeError(
                "SF02 payload/order Regions must each have exactly three peers before observability: "
                f"primary_region_id={self.primary_region_id}, primary_peers={peer_store_ids!r}, "
                f"order_region_id={self.order_region_id}, order_peers={order_peer_store_ids!r}"
            )
        attempts = json_object(
            context.env.execute_sql(
                f"SELECT attempt_id, scope, order_id, error_code, start_ts, commit_ts, "
                f"elapsed_ms, lock_ttl_ms, primary_table, primary_key_value, primary_key_hash, "
                f"lock_heartbeat_ts, renewal_count, reaper_ts, phase, final_state FROM {self.attempt_table} "
                "ORDER BY attempt_id"
            ),
            "read SF02 transaction attempt evidence",
        )
        checksum = json_object(
            context.env.execute_sql(
                f"SELECT COUNT(*), SUM(amount), BIT_XOR(row_crc) FROM {self.business_table}"
            ),
            "read SF02 business checksum baseline",
        )
        target_address = f"{self.target_node.rsplit('/', 1)[1]}:20180"
        baseline = {
            int(row["store"]["id"]): {
                "address": row["store"]["address"],
                "state_name": row["store"]["state_name"],
                "leader_count": int(row["status"]["leader_count"]),
                "region_count": int(row["status"]["region_count"]),
            }
            for row in stores
        }
        state["baseline_stores"] = baseline
        state["baseline_business_checksum"] = tuple(int(value) for value in checksum["result"][0])
        return {
            "sf02_target_node": self.target_node,
            "sf02_target_store_id": self.target_store_id,
            "sf02_target_region_id": self.primary_region_id,
            "sf02_target_address": target_address,
            "sf02_target_peer_store_ids": peer_store_ids,
            "sf02_order_region_id": self.order_region_id,
            "sf02_order_peer_store_ids": order_peer_store_ids,
            "sf02_primary_table": self.primary_table,
            "sf02_primary_key_value": self.primary_event_id,
            "sf02_primary_key_hash": self.primary_key_hash,
            "sf02_secondary_table": self.secondary_table,
            "sf02_secondary_region_id": self.secondary_region_id,
            "sf02_secondary_store_id": self.secondary_store_id,
            "sf02_near_node": self.near_node,
            "sf02_near_store_id": self.near_store_id,
            "sf02_transaction_failure_attempts": len(attempts["result"]),
            "sf02_baseline_business_checksum": state["baseline_business_checksum"],
            "sf02_baseline_target_io_config": state["baseline_io_config"],
            "sf02_baseline_near_io_config": state["baseline_near_io_config"],
            "sf02_baseline_store_count": len(baseline),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._stop_store_throttle(context.env)
        self._stop_near_store_throttle(context.env)
        self._commit_ready.set()
        self._blocker_release.set()
        self._join_transaction_thread()

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        if getattr(self, "target_node", None) is not None:
            self._stop_store_throttle(context.env)
        if getattr(self, "near_node", None) is not None:
            self._stop_near_store_throttle(context.env)
        if getattr(self, "_commit_ready", None) is not None:
            self._commit_ready.set()
        if getattr(self, "_blocker_release", None) is not None:
            self._blocker_release.set()
        self._join_transaction_thread()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "db")
        self.business_table = validate_sql_identifier(str(config["business_table"]), "business_table")
        self.job_table = validate_sql_identifier(str(config["job_table"]), "job_table")
        self.retry_plan_table = validate_sql_identifier(str(config["retry_plan_table"]), "retry_plan_table")
        self.payload_tables = tuple(
            validate_sql_identifier(str(table), "payload_table")
            for table in config["payload_tables"]
        )
        self.attempt_table = validate_sql_identifier(str(config["attempt_table"]), "attempt_table")
        self.ledger_table = validate_sql_identifier(str(config["ledger_table"]), "ledger_table")
        self.decoy_tables = tuple(
            validate_sql_identifier(str(table), "decoy_table")
            for table in config["decoy_tables"]
        )
        self.row_count = int(config["row_count"])
        self.target_order_id = int(config["target_order_id"])
        self.target_job_id = str(config["target_job_id"])
        self.target_delta = int(config["target_delta"])
        self.target_retry_payload = str(config["target_retry_payload"])
        self.config_history_table = f"{self.db}.sf02_store_config_history"
        self.env = env

    def _setup_tables(self, env) -> None:
        order_states = _sql_state_values(SF02_ORDER_STATES)
        job_states = _sql_state_values(SF02_SETTLEMENT_JOB_STATES)
        ledger_states = _sql_state_values(SF02_SETTLEMENT_LEDGER_STATES)
        payload_states = _sql_state_values(SF02_SETTLEMENT_PAYLOAD_STATES)
        for table in (
            self.business_table,
            self.job_table,
            self.retry_plan_table,
            *self.payload_tables,
            self.attempt_table,
            self.ledger_table,
            self.config_history_table.rsplit(".", 1)[1],
            *self.decoy_tables,
        ):
            require_sql_success(
                env.execute_bootstrap_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"),
                f"drop stale SF02 table {self.db}.{table}",
            )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"CREATE TABLE {self.db}.{self.business_table} ("
                "order_id BIGINT PRIMARY KEY, customer_id BIGINT NOT NULL, "
                f"amount INT NOT NULL, status ENUM({order_states}) NOT NULL, "
                f"CONSTRAINT chk_sf02_business_order_status CHECK (status IN ({order_states})), "
                "row_crc BIGINT NOT NULL, payload VARCHAR(8192) NOT NULL, "
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            ),
            "create SF02 business table",
        )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"CREATE TABLE {self.db}.{self.job_table} ("
                "job_id VARCHAR(64) PRIMARY KEY, order_id BIGINT NOT NULL, "
                "requested_delta INT NOT NULL, workset_rows INT NOT NULL, "
                f"state ENUM({job_states}) NOT NULL, "
                f"CONSTRAINT chk_sf02_settlement_job_state CHECK (state IN ({job_states})), "
                "retry_strategy VARCHAR(64), "
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            ),
            "create SF02 settlement job table",
        )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"CREATE TABLE {self.db}.{self.retry_plan_table} ("
                "job_id VARCHAR(64) PRIMARY KEY, order_id BIGINT NOT NULL, "
                "requested_delta INT NOT NULL, workset_rows INT NOT NULL, "
                "payload_event_start BIGINT NOT NULL, payload_event_end BIGINT NOT NULL, "
                f"order_status ENUM({order_states}) NOT NULL, "
                f"CONSTRAINT chk_sf02_retry_order_status CHECK (order_status IN ({order_states})), "
                f"job_state ENUM({job_states}) NOT NULL, "
                f"CONSTRAINT chk_sf02_retry_job_state CHECK (job_state IN ({job_states})), "
                "order_payload VARCHAR(255) NOT NULL, payload_prefix VARCHAR(255) NOT NULL, "
                f"payload_state ENUM({payload_states}) NOT NULL, "
                f"CONSTRAINT chk_sf02_retry_payload_state CHECK (payload_state IN ({payload_states})), "
                "order_row_crc BIGINT NOT NULL, order_crc_rule VARCHAR(255) NOT NULL, "
                "payload_crc_rule VARCHAR(255) NOT NULL, "
                f"ledger_state ENUM({ledger_states}) NOT NULL, "
                f"CONSTRAINT chk_sf02_retry_ledger_state CHECK (ledger_state IN ({ledger_states})), "
                "retry_strategy VARCHAR(64) NOT NULL)"
            ),
            "create SF02 public settlement retry plan",
        )
        for table in self.payload_tables:
            require_sql_success(
                env.execute_bootstrap_sql(
                    f"CREATE TABLE {self.db}.{table} ("
                    "event_id BIGINT PRIMARY KEY, payload VARCHAR(8192) NOT NULL, "
                    f"state ENUM({payload_states}) NOT NULL, "
                    f"CONSTRAINT chk_sf02_payload_state CHECK (state IN ({payload_states})), "
                    "row_crc BIGINT NOT NULL, "
                    "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
                ),
                f"create SF02 settlement payload table {table}",
            )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"CREATE TABLE {self.db}.{self.attempt_table} ("
                "attempt_id BIGINT AUTO_INCREMENT PRIMARY KEY, scope ENUM('target','lock_reaper','noise') NOT NULL, "
                "job_id VARCHAR(64) NOT NULL, order_id BIGINT NOT NULL, "
                "error_code VARCHAR(128) NOT NULL, error_text VARCHAR(512) NOT NULL, "
                "start_ts BIGINT NOT NULL, commit_ts BIGINT NOT NULL, elapsed_ms BIGINT NOT NULL, "
                "lock_ttl_ms BIGINT NOT NULL, primary_table VARCHAR(128) NOT NULL, "
                "primary_key_value BIGINT NOT NULL, primary_key_hash VARCHAR(64) NOT NULL, "
                "lock_heartbeat_ts BIGINT NOT NULL, renewal_count BIGINT NOT NULL, "
                "reaper_ts BIGINT NOT NULL, phase ENUM('historical','reaper_after_ttl',"
                "'unexpected_commit','commit_failed_after_ttl') NOT NULL, "
                "final_state ENUM('committed','observed_noise','committed_after_ttl',"
                "'unexpected_commit','commit_failed') NOT NULL, "
                "observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            ),
            "create SF02 transaction attempt table",
        )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"CREATE TABLE {self.config_history_table} ("
                "history_id BIGINT AUTO_INCREMENT PRIMARY KEY, store_node VARCHAR(128) NOT NULL, "
                "store_id BIGINT NOT NULL, "
                "max_bytes_per_sec VARCHAR(32) NOT NULL, mode VARCHAR(32) NOT NULL, "
                "strict_mode BOOLEAN NOT NULL, observed_ts_ms BIGINT NOT NULL)"
            ),
            "create SF02 Store config history",
        )
        require_sql_success(
            env.execute_bootstrap_sql(
                f"CREATE TABLE {self.db}.{self.ledger_table} ("
                "ledger_id BIGINT AUTO_INCREMENT PRIMARY KEY, job_id VARCHAR(64) NOT NULL, "
                f"order_id BIGINT NOT NULL, delta INT NOT NULL, state ENUM({ledger_states}) NOT NULL, "
                f"CONSTRAINT chk_sf02_ledger_state CHECK (state IN ({ledger_states})), "
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            ),
            "create SF02 settlement ledger table",
        )
        for table in self.decoy_tables:
            require_sql_success(
                env.execute_bootstrap_sql(
                f"CREATE TABLE {self.db}.{table} ("
                "event_id BIGINT PRIMARY KEY, account_id BIGINT NOT NULL, "
                "amount INT NOT NULL, state ENUM('open') NOT NULL, payload VARCHAR(255) NOT NULL)"
                ),
                f"create SF02 decoy table {table}",
            )
        self._seed_business_rows(env)
        self._seed_jobs(env)
        self._seed_retry_plan(env)
        self._seed_payload_rows(env)
        require_sql_success(
            env.execute_bootstrap_sql(
                f"SPLIT TABLE {self.db}.{self.payload_tables[1]} BETWEEN (0) AND "
                f"({self._PAYLOAD_B_ROWS + 1}) REGIONS 4"
            ),
            "split SF02 payload_b into deterministic key-range Regions",
        )
        self._wait_for_table_regions(env, self.payload_tables[1], 4)
        self._seed_attempt_noise(env)
        self._seed_decoy_rows(env)

    def _seed_business_rows(self, env) -> None:
        values = []
        for order_id in range(1, self.row_count + 1):
            values.append(
                f"({order_id},{10000 + order_id % 37},{sf02_order_amount(order_id)},'open',"
                f"{sf02_order_crc(order_id)},'baseline-order-{order_id:04d}')"
            )
        run_sql_batches(
            lambda sql: env.execute_bootstrap_sql(sql),
            f"INSERT INTO {self.db}.{self.business_table} "
            "(order_id, customer_id, amount, status, row_crc, payload) VALUES ",
            values,
            64,
            "seed SF02 business rows",
        )

    def _seed_jobs(self, env) -> None:
        values = [
            f"('{self.target_job_id}',{self.target_order_id},{self.target_delta},{len(self._PAYLOAD_ROWS)},'retry_required',NULL)",
        ]
        for index in range(1, 25):
            values.append(
                f"('sf02-decoy-job-{index:03d}',{100 + index},{index % 11 + 1},"
                f"{index % 8 + 1},'{'settled' if index % 3 else 'retry_required'}',NULL)"
            )
        run_sql_batches(
            lambda sql: env.execute_bootstrap_sql(sql),
            f"INSERT INTO {self.db}.{self.job_table} "
            "(job_id, order_id, requested_delta, workset_rows, state, retry_strategy) VALUES ",
            values,
            32,
            "seed SF02 settlement jobs",
        )

    def _seed_retry_plan(self, env) -> None:
        require_sql_success(
            env.execute_bootstrap_sql(
                f"INSERT INTO {self.db}.{self.retry_plan_table} ("
                "job_id, order_id, requested_delta, workset_rows, payload_event_start, payload_event_end, "
                "order_status, job_state, order_payload, payload_prefix, payload_state, order_row_crc, "
                "order_crc_rule, payload_crc_rule, ledger_state, retry_strategy) VALUES ("
                f"'{self.target_job_id}',{self.target_order_id},{self.target_delta},{len(self._PAYLOAD_ROWS)},"
                f"{self._PAYLOAD_ROWS[0]},{self._PAYLOAD_ROWS[-1]},'settled','committed',"
                f"'{self.target_retry_payload}','{self.target_retry_payload}','applied',"
                f"{sf02_retry_order_crc(self.target_order_id)},"
                "'((order_id * 2654435761) & 4294967295) XOR 0xC0FFEE42',"
                "'CRC32(table_index:event_id:payload:state), with state=applied',"
                "'applied','targeted_store_retry')"
            ),
            "seed SF02 public settlement retry plan",
        )

    def _seed_payload_rows(self, env) -> None:
        for table_index, table in enumerate(self.payload_tables, start=1):
            row_limit = self._PAYLOAD_B_ROWS if table_index == 2 else 64
            values = [
                f"({event_id},'{sf02_payload_value(table_index, event_id)}','ready',"
                f"{sf02_payload_crc(table_index, event_id, sf02_payload_value(table_index, event_id), 'ready')})"
                for event_id in range(1, row_limit + 1)
            ]
            run_sql_batches(
                lambda sql: env.execute_bootstrap_sql(sql),
                f"INSERT INTO {self.db}.{table} (event_id, payload, state, row_crc) VALUES ",
                values,
                128 if table_index == 2 else 32,
                f"seed SF02 settlement payload rows {table}",
            )

    def _seed_attempt_noise(self, env) -> None:
        errors = ("ERROR 8022", "LOCK_WAIT_TIMEOUT", "ERROR 9007", "server is busy", "OK")
        values = []
        for index in range(1, 121):
            error = errors[index % len(errors)]
            state = "committed" if error == "OK" else "observed_noise"
            values.append(
                f"('noise','sf02-decoy-job-{((index - 1) % 24) + 1:03d}',{100 + index % 24},"
                f"'{error}','same-domain decoy transaction',"
                f"{900000000000 + index},{900000000100 + index},{index % 900 + 10},3000,"
                f"'{self.payload_tables[1]}',{1 + index % 32},"
                f"'{sf02_primary_key_hash(self.payload_tables[1], 1)}',0,0,0,'historical','{state}')"
            )
            run_sql_batches(
                lambda sql: env.execute_bootstrap_sql(sql),
                f"INSERT INTO {self.db}.{self.attempt_table} "
                "(scope, job_id, order_id, error_code, error_text, start_ts, commit_ts, elapsed_ms, lock_ttl_ms, "
                "primary_table, primary_key_value, primary_key_hash, lock_heartbeat_ts, renewal_count, reaper_ts, phase, final_state) VALUES ",
                values,
            40,
            "seed SF02 transaction noise",
        )

    def _seed_decoy_rows(self, env) -> None:
        for table_index, table in enumerate(self.decoy_tables, start=1):
            values = [
                f"({event_id},{table_index * 1000 + event_id},{50 + event_id},'open','sf02-decoy-{table_index}-{event_id}')"
                for event_id in range(1, 25)
            ]
            run_sql_batches(
                lambda sql: env.execute_bootstrap_sql(sql),
                f"INSERT INTO {self.db}.{table} (event_id, account_id, amount, state, payload) VALUES ",
                values,
                32,
                f"seed SF02 decoy rows {table}",
            )

    def _store_row(self, env, store_id: int) -> dict:
        stores = env.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
        return next(item for item in stores if int(item["store"]["id"]) == store_id)

    def _contract_peer_store_ids(self, env, region_id: int) -> set[int]:
        return {
            int(peer["store_id"])
            for peer in self._pd_region(env, region_id)["peers"]
        }

    def _settle_near_store(self, env) -> None:
        """Wait out the replica-balance fill wave triggered by the deferred Store.

        PD pours Regions onto the freshly registered empty near Store; a peer
        migration that lands on a contract Region after baseline capture would
        invalidate `target_region_has_three_healthy_replicas`. The wait ends
        once the near Store region count stops changing, so the baseline is
        captured against settled placement.
        """
        last_region_count = None
        stable_reads = 0
        for attempt in range(self._NEAR_STORE_SETTLE_POLLS):
            region_count = int(self._store_row(env, self.near_store_id)["status"]["region_count"])
            stable_reads = stable_reads + 1 if region_count == last_region_count else 0
            last_region_count = region_count
            if stable_reads >= self._NEAR_STORE_SETTLE_STABLE_READS:
                return
            if attempt < self._NEAR_STORE_SETTLE_POLLS - 1:
                time.sleep(self._NEAR_STORE_SETTLE_POLL_SECONDS)

    def _repair_contract_region_peers(self, env) -> None:
        """Restore the contract Region peer sets if the near Store grabbed a peer.

        PD holds at most one operator per Region: while a balance-wave, merge,
        or repair operator is installed on the contract Region, a new pd-ctl
        issue is rejected or cancels the installed operator, which froze the
        peer set until the deadline in production. The repair therefore waits
        out the installed operator before issuing, records every pd-ctl
        verdict, and logs each stall so the blocking operator stays visible in
        the run stdout.
        """
        stores = env.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
        baseline_store_ids = sorted(
            int(item["store"]["id"])
            for item in stores
            if item["store"]["state_name"] == "Up"
            and int(item["store"]["id"]) != self.near_store_id
        )
        for region_id in (self.primary_region_id, self.order_region_id):
            if self.near_store_id not in self._contract_peer_store_ids(env, region_id):
                continue
            deadline = time.monotonic() + self._PEER_REPAIR_TIMEOUT_SECONDS
            last_response = None
            last_operator = None
            next_log_at = 0.0
            while True:
                peer_store_ids = self._contract_peer_store_ids(env, region_id)
                missing_store_ids = [
                    store_id for store_id in baseline_store_ids if store_id not in peer_store_ids
                ]
                if self.near_store_id not in peer_store_ids and not missing_store_ids:
                    return
                if time.monotonic() >= deadline:
                    raise RuntimeError(
                        "SF02 contract Region peer repair did not converge: "
                        f"region_id={region_id}, "
                        f"peers={sorted(self._contract_peer_store_ids(env, region_id))!r}, "
                        f"near_store_id={self.near_store_id}, "
                        f"last_operator={last_operator!r}, last_pdctl={last_response!r}"
                    )
                # PD keeps one operator per Region: never issue while one is
                # installed, or the issue is rejected or cancels the operator
                # in flight and the peer set freezes until the deadline.
                last_operator = self._pd_region_operator(env, region_id)
                if last_operator is None:
                    if self.near_store_id in peer_store_ids:
                        last_response = env.deployment.remove_region_peer(
                            region_id, self.near_store_id
                        )
                    elif missing_store_ids:
                        last_response = env.deployment.add_region_peer(
                            region_id, missing_store_ids[0]
                        )
                if time.monotonic() >= next_log_at:
                    print(
                        f"[SF02] peer repair: region_id={region_id}, "
                        f"peers={sorted(peer_store_ids)!r}, missing={missing_store_ids!r}, "
                        f"operator={last_operator!r}, pdctl={last_response!r}"
                    )
                    next_log_at = time.monotonic() + 30
                time.sleep(2)

    def _pd_region_operator(self, env, region_id: int) -> object | None:
        """Return the operator PD currently holds on the Region, or None.

        GET /pd/api/v1/operators answers with the active operator list, either
        as a bare JSON array or wrapped under an "operators" key.
        """
        payload = env.deployment.pd_request("GET", "/pd/api/v1/operators")
        if isinstance(payload, list):
            entries = payload
        elif isinstance(payload, Mapping) and isinstance(payload.get("operators"), list):
            entries = payload["operators"]
        else:
            raise TypeError(
                "SF02 PD operators response has no operator list: "
                f"region_id={region_id}, payload={payload!r}"
            )
        for entry in entries:
            if int(entry["region_id"]) == region_id:
                return entry
        return None

    def _resolve_target_store(self, env) -> None:
        topology = env.deployment.topology
        if topology.deferred_tikv_count != 1:
            raise RuntimeError(
                "SF02 requires exactly one deferred maintenance TiKV Store: "
                f"tikv_count={topology.tikv_count}, deferred_tikv_count={topology.deferred_tikv_count}"
            )
        deferred_service = env.deployment.COMPONENTS["tikv"][-1]
        self.near_node = f"tikv/{deferred_service}"
        env.deployment.start_component(self.near_node)
        near_store = self._wait_for_store_registration(env, deferred_service)
        self.near_store_id = int(near_store["store"]["id"])
        self._settle_near_store(env)

        def table_regions(table: str, description: str) -> tuple[tuple[int, int], ...]:
            payload = json_object(
                env.execute_bootstrap_sql(f"SHOW TABLE {self.db}.{table} REGIONS"),
                description,
            )
            rows = payload["result"]
            if not rows:
                raise RuntimeError(
                    "SF02 table has no observable Regions for deterministic key placement: "
                    f"table={table!r}, rows={rows!r}"
                )
            return tuple((int(row[0]), int(row[4])) for row in rows)

        def table_region(table: str, description: str) -> tuple[int, int]:
            regions = table_regions(table, description)
            if len(regions) != 1:
                raise RuntimeError(
                    "SF02 table must remain one Region for deterministic key placement: "
                    f"table={table!r}, regions={regions!r}"
                )
            return regions[0]

        self.primary_table = self.payload_tables[1]
        self.primary_event_id = 1
        primary_regions = table_regions(
            self.primary_table,
            "resolve SF02 payload_b primary Region candidates",
        )
        if len(primary_regions) != 4:
            raise RuntimeError(
                "SF02 payload_b must expose exactly four key-range Regions: "
                f"table={self.primary_table!r}, regions={primary_regions!r}"
            )
        self.primary_region_ids = tuple(region_id for region_id, _ in primary_regions)
        self.primary_region_id, self.target_store_id = primary_regions[0]
        self.primary_key_hash = sf02_primary_key_hash(self.primary_table, self.primary_event_id)
        self.target_region_id = self.primary_region_id
        self.order_region_id, self.order_store_id = table_region(
            self.business_table,
            "resolve SF02 orders Region leader",
        )
        stores = env.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
        up_store_ids = tuple(
            int(item["store"]["id"])
            for item in stores
            if item["store"]["state_name"] == "Up"
        )
        if self.target_store_id == self.near_store_id:
            destination_store_id = next(
                store_id
                for store_id in up_store_ids
                if store_id != self.near_store_id
            )
            env.deployment.transfer_region_leader(self.primary_region_id, destination_store_id)
            self._wait_for_region_leader(env, self.primary_region_id, destination_store_id)
            primary_regions = table_regions(
                self.primary_table,
                "re-resolve SF02 payload_b primary Region leader after near-store exclusion",
            )
            self.primary_region_id, self.target_store_id = primary_regions[0]
            self.target_region_id = self.primary_region_id
        if self.order_store_id == self.target_store_id:
            order_peers = {
                int(peer["store_id"])
                for peer in self._pd_region(env, self.order_region_id)["peers"]
            }
            order_destination = next(
                store_id
                for store_id in sorted(order_peers & set(up_store_ids))
                if store_id not in {self.target_store_id, self.near_store_id}
            )
            env.deployment.transfer_region_leader(self.order_region_id, order_destination)
            self._wait_for_region_leader(env, self.order_region_id, order_destination)
            self.order_region_id, self.order_store_id = table_region(
                self.business_table,
                "re-resolve SF02 orders Region leader after transfer",
            )
        if self.order_store_id == self.target_store_id:
            raise RuntimeError(
                "SF02 orders Region leader must be a healthy sibling of the payload_b primary leader: "
                f"orders_region_id={self.order_region_id}, target_store_id={self.target_store_id}, "
                f"order_store_id={self.order_store_id}"
            )

        payload_regions = tuple(
            (table, *table_region(table, f"resolve SF02 payload Region table={table}"))
            for table in self.payload_tables
            if table != self.primary_table
        )
        secondary_candidates = tuple(
            candidate
            for candidate in payload_regions
            if candidate[0] != self.primary_table and candidate[2] != self.target_store_id
        )
        leader_transfer = None
        if not secondary_candidates:
            table, region_id, current_store_id = next(
                candidate for candidate in payload_regions if candidate[0] != self.primary_table
            )
            peer_store_ids = {
                int(peer["store_id"])
                for peer in self._pd_region(env, region_id)["peers"]
            }
            destination_store_id = next(
                store_id
                for store_id in sorted(peer_store_ids & set(up_store_ids))
                if store_id not in {self.target_store_id, self.near_store_id}
            )
            self._transfer_region_leader(env, region_id, destination_store_id)
            self._wait_for_region_leader(env, region_id, destination_store_id)
            secondary_candidates = ((table, region_id, destination_store_id),)
            leader_transfer = {
                "region_id": region_id,
                "from_store_id": current_store_id,
                "to_store_id": destination_store_id,
            }
        if not secondary_candidates:
            raise RuntimeError(
                "SF02 could not find a secondary payload Region on a different Store from the primary: "
                f"primary_store_id={self.target_store_id}, candidates={secondary_candidates!r}"
            )
        self.secondary_table, self.secondary_region_id, self.secondary_store_id = secondary_candidates[0]
        attempt_region = json_object(
            env.execute_bootstrap_sql(f"SHOW TABLE {self.db}.{self.attempt_table} REGIONS"),
            "resolve SF02 transaction-attempt audit Region leader",
        )
        attempt_rows = attempt_region["result"]
        if len(attempt_rows) != 1:
            raise RuntimeError(
                "SF02 transaction-attempt audit table must remain one Region: "
                f"table={self.attempt_table!r}, rows={attempt_rows!r}"
            )
        self.attempt_region_id = int(attempt_rows[0][0])
        self.attempt_store_id = int(attempt_rows[0][4])
        attempt_leader_transfer = None
        if self.attempt_store_id == self.target_store_id:
            attempt_peer_store_ids = {
                int(peer["store_id"])
                for peer in self._pd_region(env, self.attempt_region_id)["peers"]
            }
            destination_store_id = next(
                store_id
                for store_id in sorted(attempt_peer_store_ids & set(up_store_ids))
                if store_id != self.target_store_id
            )
            self._transfer_region_leader(env, self.attempt_region_id, destination_store_id)
            self._wait_for_region_leader(env, self.attempt_region_id, destination_store_id)
            attempt_leader_transfer = {
                "region_id": self.attempt_region_id,
                "from_store_id": self.attempt_store_id,
                "to_store_id": destination_store_id,
            }
            self.attempt_store_id = destination_store_id
        target_matches = [
            item for item in stores if int(item["store"]["id"]) == self.target_store_id
        ]
        if len(target_matches) != 1:
            raise RuntimeError(
                "SF02 payload_b primary leader Store was not found in PD Store inventory: "
                f"region_id={self.primary_region_id}, target_store_id={self.target_store_id}, stores={stores!r}"
            )
        target_service = str(target_matches[0]["store"]["address"]).split(":", 1)[0]
        self.target_node = f"tikv/{target_service}"
        baseline_io_config = env.tikv_io_rate_limit(self.target_node)
        baseline_near_io_config = env.tikv_io_rate_limit(self.near_node)
        for node, config in (
            (self.target_node, baseline_io_config),
            (self.near_node, baseline_near_io_config),
        ):
            if not config["strict"] or config["mode"] != self._FAULT_MODE:
                raise RuntimeError(
                    "SF02 requires strict write-only Store I/O limiters before fault injection: "
                    f"node={node!r}, config={config!r}"
                )
        self.order_peer_store_ids = tuple(
            sorted(int(peer["store_id"]) for peer in self._pd_region(env, self.order_region_id)["peers"])
        )
        self._state = {
            "case": {
                "db": self.db,
                "business_table": self.business_table,
                "job_table": self.job_table,
                "retry_plan_table": self.retry_plan_table,
                "payload_tables": self.payload_tables,
                "primary_table": self.primary_table,
                "secondary_table": self.secondary_table,
                "attempt_table": self.attempt_table,
                "ledger_table": self.ledger_table,
            },
            "target_node": self.target_node,
            "target_store_id": self.target_store_id,
            "target_region_id": self.primary_region_id,
            "primary_key_hash": self.primary_key_hash,
            "order_region_id": self.order_region_id,
            "order_store_id": self.order_store_id,
            "secondary_region_id": self.secondary_region_id,
            "secondary_store_id": self.secondary_store_id,
            "secondary_leader_transfer": leader_transfer,
            "attempt_region_id": self.attempt_region_id,
            "attempt_store_id": self.attempt_store_id,
            "attempt_leader_transfer": attempt_leader_transfer,
            "near_node": self.near_node,
            "near_store_id": self.near_store_id,
            "baseline_io_config": baseline_io_config,
            "baseline_near_io_config": baseline_near_io_config,
            "fault_active": False,
            "failure_observed": False,
            "transaction": {},
        }
        self._record_all_store_config_samples(env)
        self._configure_near_store(env)

    def _pd_region(self, env, region_id: int) -> dict:
        payload = env.deployment.pd_request("GET", f"/pd/api/v1/region/id/{region_id}")
        if not isinstance(payload, dict) or not isinstance(payload.get("peers"), list):
            raise RuntimeError(
                "SF02 PD Region response has no peer list: "
                f"region_id={region_id}, payload={payload!r}"
            )
        return payload

    def _wait_for_table_regions(self, env, table: str, expected_count: int) -> None:
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            payload = json_object(
                env.execute_bootstrap_sql(f"SHOW TABLE {self.db}.{table} REGIONS"),
                f"wait for SF02 table Regions table={table}",
            )
            rows = payload["result"]
            if len(rows) == expected_count:
                return
            time.sleep(1)
        raise RuntimeError(
            "SF02 table Region split did not converge: "
            f"table={table!r}, expected_count={expected_count}, observed_rows={rows!r}"
        )

    def _wait_for_store_registration(self, env, service: str) -> dict:
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            stores = env.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
            matches = [
                item for item in stores
                if item["store"]["address"] == f"{service}:20160"
                and item["store"]["state_name"] == "Up"
            ]
            if len(matches) == 1:
                return matches[0]
            time.sleep(1)
        raise RuntimeError(
            "SF02 deferred maintenance Store did not join PD as Up: "
            f"service={service!r}, observed_stores={stores!r}"
        )

    def _wait_for_region_leader(self, env, region_id: int, store_id: int) -> None:
        # PD runs one operator per Region at a time; re-issue the transfer
        # operator while waiting so a balance-queue conflict cannot silently
        # drop it.
        deadline = time.monotonic() + 240
        next_issue_at = 0.0
        last_response = None
        while time.monotonic() < deadline:
            payload = env.deployment.pd_request("GET", f"/pd/api/v1/region/id/{region_id}")
            leader = payload.get("leader")
            if leader is not None and int(leader["store_id"]) == store_id:
                if last_response is not None:
                    print(
                        f"[SF02] leader transfer converged: region_id={region_id}, "
                        f"store_id={store_id}, attempts_issued={last_response!r}"
                    )
                return
            if time.monotonic() >= next_issue_at:
                last_response = env.deployment.transfer_region_leader(region_id, store_id)
                print(
                    f"[SF02] transfer-leader operator: region_id={region_id}, "
                    f"dest_store={store_id}, current_leader={leader!r}, pdctl={last_response!r}"
                )
                next_issue_at = time.monotonic() + 5
            time.sleep(1)
        raise RuntimeError(
            "SF02 secondary Region leader transfer did not converge: "
            f"region_id={region_id}, expected_store_id={store_id}, "
            f"last_pdctl={last_response!r}, observed={payload!r}"
        )

    def _record_config_sample(
        self,
        node: str,
        store_id: int,
        config: Mapping[str, object],
    ) -> None:
        signature = sf02_io_limiter_signature(config)
        require_sql_success(
            self.env.execute_bootstrap_sql(
                f"INSERT INTO {self.config_history_table} "
                "(store_node, store_id, max_bytes_per_sec, mode, strict_mode, observed_ts_ms) "
                f"VALUES ('{node}',{store_id},"
                f"'{signature['max-bytes-per-sec']}','{signature['mode']}',"
                f"{str(bool(signature['strict'])).upper()},{int(time.time() * 1000)})"
            ),
            f"record SF02 raw Store config sample node={node} store_id={store_id}",
        )

    def _record_all_store_config_samples(self, env) -> None:
        stores = env.deployment.pd_request("GET", "/pd/api/v1/stores")["stores"]
        for item in sorted(stores, key=lambda value: int(value["store"]["id"])):
            store = item["store"]
            node = f"tikv/{str(store['address']).split(':', 1)[0]}"
            self._record_config_sample(
                node,
                int(store["id"]),
                env.tikv_io_rate_limit(node),
            )

    def _configure_near_store(self, env) -> None:
        state = self._state
        observed = env.set_tikv_io_rate_limit(self.near_node, self._FAULT_MAX_BYTES)
        expected = {
            "max-bytes-per-sec": self._FAULT_MAX_BYTES,
            "mode": state["baseline_near_io_config"]["mode"],
            "strict": state["baseline_near_io_config"]["strict"],
        }
        if sf02_io_limiter_signature(observed) != expected:
            raise RuntimeError(
                "SF02 near Store decoy I/O cap did not persist: "
                f"near={self.near_node!r}, expected={expected!r}, observed={observed!r}"
            )
        state["near_fault_io_config"] = observed
        self._record_all_store_config_samples(env)


    def _transfer_region_leader(self, env, region_id: int, store_id: int) -> None:
        payload = env.deployment.pd_request("GET", f"/pd/api/v1/region/id/{region_id}")
        peer_store_ids = {int(peer["store_id"]) for peer in payload["peers"]}
        if store_id not in peer_store_ids:
            env.deployment.add_region_peer(region_id, store_id)
            deadline = time.monotonic() + 90
            while time.monotonic() < deadline:
                payload = env.deployment.pd_request("GET", f"/pd/api/v1/region/id/{region_id}")
                if store_id in {int(peer["store_id"]) for peer in payload["peers"]}:
                    break
                time.sleep(1)
            else:
                raise RuntimeError(
                    "SF02 Region leader transfer destination did not become a peer: "
                    f"region_id={region_id}, destination_store_id={store_id}, observed={payload!r}"
                )
        env.deployment.transfer_region_leader(region_id, store_id)

    def _start_store_throttle(self, env) -> None:
        baseline = self._state["baseline_io_config"]
        if not baseline["strict"] or baseline["mode"] != self._FAULT_MODE:
            raise RuntimeError(
                "SF02 requires the target Store's baseline I/O limiter to use strict write-only mode: "
                f"target={self.target_node!r}, baseline={baseline!r}"
            )
        fault_config = {
            "max-bytes-per-sec": self._PRELOCK_MAX_BYTES,
            "mode": self._FAULT_MODE,
            "strict": baseline["strict"],
        }
        current = env.set_tikv_io_rate_limit(
            self.target_node,
            self._PRELOCK_MAX_BYTES,
        )
        state = self._state
        state["fault_active"] = True
        state["fault_io_config"] = current
        state["prelock_io_config"] = current
        state["final_fault_io_config"] = {
            "max-bytes-per-sec": self._FAULT_MAX_BYTES,
            "mode": self._FAULT_MODE,
            "strict": baseline["strict"],
        }
        if sf02_io_limiter_signature(current) != fault_config:
            raise RuntimeError(
                "SF02 TiKV I/O throttle did not persist: "
                f"target={self.target_node!r}, expected={fault_config!r}, observed={current!r}"
            )
        self._record_all_store_config_samples(env)

    def _stop_store_throttle(self, env) -> None:
        state = self._state
        current = env.tikv_io_rate_limit(self.target_node)
        if current != state["baseline_io_config"]:
            current = env.set_tikv_io_rate_limit(
                self.target_node,
                state["baseline_io_config"]["max-bytes-per-sec"],
            )
            if current != state["baseline_io_config"]:
                raise RuntimeError(
                    "SF02 TiKV I/O throttle recovery did not restore the baseline: "
                    f"target={self.target_node!r}, expected={state['baseline_io_config']!r}, "
                    f"observed={current!r}"
                )
        state["fault_active"] = False

    def _stop_near_store_throttle(self, env) -> None:
        state = self._state
        current = env.tikv_io_rate_limit(self.near_node)
        if current != state["baseline_near_io_config"]:
            restored = env.set_tikv_io_rate_limit(
                self.near_node,
                state["baseline_near_io_config"]["max-bytes-per-sec"],
            )
            if restored != state["baseline_near_io_config"]:
                raise RuntimeError(
                    "SF02 near Store I/O decoy recovery did not restore the baseline: "
                    f"near={self.near_node!r}, expected={state['baseline_near_io_config']!r}, "
                    f"observed={restored!r}"
                )
            self._record_all_store_config_samples(env)
        env.deployment.stop_component(self.near_node)

    def _run_target_transaction(self, env) -> None:
        self._transaction_error = None
        self._transaction_exception = None
        self._lock_reaper_error = None
        self._lock_reaper_succeeded = False
        self._blocker_error = None
        self._blocker_succeeded = False
        self._tail_error = None
        self._tail_completed = threading.Event()
        self._reaper_ts_ms = 0
        self._heartbeat_missed_ts_ms = 0
        self._blocker_ready = threading.Event()
        self._blocker_release = threading.Event()
        self._target_lock_ready = threading.Event()
        self._commit_ready = threading.Event()
        self._lock_reaper_thread = None
        self._blocker_thread = threading.Thread(
            target=self._lock_blocker_worker,
            args=(env,),
            name="sf02-secondary-lock-blocker",
            daemon=True,
        )
        self._blocker_thread.start()
        if not self._blocker_ready.wait(timeout=30):
            raise RuntimeError(
                "SF02 secondary lock blocker did not acquire its business lock: "
                f"table={self.secondary_table!r}, event_id=7, error={self._blocker_error!r}"
            )
        if self._blocker_error is not None:
            raise self._blocker_error
        self._transaction_thread = threading.Thread(
            target=self._target_transaction_worker,
            args=(env,),
            name="sf02-target-lock-ttl-transaction",
            daemon=True,
        )
        self._transaction_thread.start()
        if not self._target_lock_ready.wait(timeout=self._TARGET_PREPARE_TIMEOUT_SECONDS):
            if self._transaction_exception is not None:
                raise self._transaction_exception
            raise RuntimeError(
                "SF02 target transaction did not prepare its mutations before the slow Store window: "
                f"target={self.target_node!r}, order_id={self.target_order_id}"
            )
        state = self._state
        final_fault_config = {
            "max-bytes-per-sec": self._FAULT_MAX_BYTES,
            "mode": self._FAULT_MODE,
            "strict": state["baseline_io_config"]["strict"],
        }
        observed = self.env.set_tikv_io_rate_limit(
            self.target_node,
            self._FAULT_MAX_BYTES,
        )
        if sf02_io_limiter_signature(observed) != final_fault_config:
            raise RuntimeError(
                "SF02 final TiKV I/O throttle did not reach the target Store: "
                f"target={self.target_node!r}, expected={final_fault_config!r}, "
                f"observed={observed!r}"
            )
        state["fault_io_config"] = observed
        state["slow_window_started_at_ms"] = int(time.time() * 1000)
        self._heartbeat_missed_ts_ms = state["slow_window_started_at_ms"]
        self._record_all_store_config_samples(env)
        self._tail_thread = threading.Thread(
            target=self._persistence_tail_worker,
            args=(env,),
            name="sf02-target-persistence-tail",
            daemon=True,
        )
        self._tail_thread.start()
        self._commit_ready.set()
        time.sleep(self._LOCK_REAPER_START_DELAY_SECONDS)
        self._lock_reaper_thread = threading.Thread(
            target=self._lock_reaper_worker,
            args=(env,),
            name="sf02-expired-lock-reaper",
            daemon=True,
        )
        self._lock_reaper_thread.start()
        join_thread(self._lock_reaper_thread, self._TXN_COMMIT_WAIT_SECONDS, "SF02 expired-lock reaper")
        if self._lock_reaper_error is not None:
            self._blocker_release.set()
            join_thread(self._blocker_thread, 30, "SF02 secondary lock blocker cleanup")
            raise self._lock_reaper_error
        self._blocker_release.set()
        join_thread(self._blocker_thread, self._TXN_COMMIT_WAIT_SECONDS, "SF02 secondary lock blocker")
        if self._blocker_error is not None:
            raise self._blocker_error
        if not self._blocker_succeeded:
            raise RuntimeError(
                "SF02 secondary lock blocker did not commit after the reaper completed: "
                f"table={self.secondary_table!r}, error={self._blocker_error!r}"
            )
        join_thread(self._transaction_thread, self._TXN_COMMIT_WAIT_SECONDS, "SF02 target transaction")
        join_thread(self._tail_thread, self._TXN_COMMIT_WAIT_SECONDS, "SF02 target persistence tail")
        if self._tail_error is not None:
            raise self._tail_error
        if not self._tail_completed.is_set():
            raise RuntimeError(
                "SF02 target persistence tail did not complete its fixed workload: "
                f"target={self.target_node!r}, cycles={self._TAIL_CYCLES}, error={self._tail_error!r}"
            )
        if self._transaction_exception is not None:
            raise self._transaction_exception
        if self._transaction_error is None:
            raise RuntimeError(
                "SF02 target transaction unexpectedly committed under the injected Store I/O limit: "
                f"target={self.target_node!r}, region_id={self.target_region_id}, "
                f"max_bytes_per_sec={self._FAULT_MAX_BYTES!r}"
            )
        if not self._lock_reaper_succeeded:
            raise RuntimeError(
                "SF02 expired-lock reaper did not commit after waiting for the target lock: "
                f"target={self.target_node!r}, order_id={self.target_order_id}, "
                f"error={self._lock_reaper_error!r}"
            )
        normalized = self._transaction_error.casefold()
        if not any(
            token in normalized
            for token in ("txnlocknotfound", "lock not found", "8022")
        ):
            raise RuntimeError(
                "SF02 target transaction failed for an unexpected reason: "
                f"target={self.target_node!r}, error={self._transaction_error!r}"
            )
        state = self._state
        state["failure_observed"] = True
        self._update_target_attempt_timeline(env)
        state["transaction"] = {
            "error": self._transaction_error,
            "target_order_id": self.target_order_id,
            "target_region_id": self.target_region_id,
            "target_store_id": self.target_store_id,
            "primary_table": self.primary_table,
            "primary_region_id": self.primary_region_id,
            "lock_reaper": "committed_after_lock_ttl_expiry",
            "secondary_table": self.secondary_table,
            "secondary_region_id": self.secondary_region_id,
            "secondary_store_id": self.secondary_store_id,
        }

    def _target_transaction_worker(self, env) -> None:
        connection = None
        try:
            connection = connect_tidb(
                env,
                database=self.db,
                autocommit=False,
                application_name="sf02-target-settlement-worker",
                read_timeout=self._TXN_COMMIT_WAIT_SECONDS,
                write_timeout=self._TXN_COMMIT_WAIT_SECONDS,
            )
            self._target_transaction_body(env, connection)
        except Exception as exc:
            self._transaction_exception = exc
            self._target_lock_ready.set()
        finally:
            if connection is not None:
                connection.close()

    def _persistence_tail_worker(self, env) -> None:
        connection = None
        try:
            connection = connect_tidb(
                env,
                database=self.db,
                autocommit=False,
                application_name="sf02-target-persistence-tail",
                read_timeout=self._TXN_COMMIT_WAIT_SECONDS,
                write_timeout=self._TXN_COMMIT_WAIT_SECONDS,
            )
            for _ in range(self._TAIL_CYCLES):
                with connection.cursor() as cursor:
                    cursor.execute("BEGIN OPTIMISTIC")
                    cursor.execute(
                        f"UPDATE {self.primary_table} SET payload = RPAD(payload, 8192, 't') "
                        f"WHERE event_id BETWEEN {self._TAIL_ROWS[0]} AND {self._TAIL_ROWS[-1]}"
                    )
                    connection.commit()
                with connection.cursor() as cursor:
                    cursor.execute("BEGIN OPTIMISTIC")
                    for event_id in self._TAIL_ROWS:
                        payload = sf02_payload_value(2, event_id)
                        crc = sf02_payload_crc(2, event_id, payload, "ready")
                        cursor.execute(
                            f"UPDATE {self.primary_table} SET payload = '{payload}', row_crc = {crc}, state = 'ready' "
                            f"WHERE event_id = {event_id}"
                        )
                    connection.commit()
            self._tail_completed.set()
        except Exception as exc:
            self._tail_error = exc
            if connection is not None:
                connection.rollback()
            self._tail_completed.set()
        finally:
            if connection is not None:
                connection.close()

    def _lock_blocker_worker(self, env) -> None:
        connection = None
        try:
            connection = connect_tidb(
                env,
                database=self.db,
                autocommit=False,
                application_name="sf02-secondary-lock-blocker",
                read_timeout=self._TXN_COMMIT_WAIT_SECONDS,
                write_timeout=self._TXN_COMMIT_WAIT_SECONDS,
            )
            with connection.cursor() as cursor:
                cursor.execute("SET SESSION tidb_txn_mode = 'pessimistic'")
                cursor.execute("SET SESSION innodb_lock_wait_timeout = 180")
                cursor.execute("BEGIN PESSIMISTIC")
                cursor.execute(
                    f"UPDATE {self.secondary_table} SET payload = payload "
                    "WHERE event_id = 7"
                )
            self._blocker_ready.set()
            with connection.cursor() as cursor:
                deadline = time.monotonic() + self._TXN_COMMIT_WAIT_SECONDS
                while not self._blocker_release.wait(timeout=0.5):
                    if time.monotonic() >= deadline:
                        raise RuntimeError(
                            "SF02 secondary lock blocker was not released: "
                            f"table={self.secondary_table!r}, event_id=7"
                        )
                    cursor.execute(
                        f"SELECT event_id FROM {self.secondary_table} "
                        "WHERE event_id = 7 FOR UPDATE"
                    )
            connection.rollback()
            self._blocker_succeeded = True
        except Exception as exc:
            self._blocker_error = exc
            self._blocker_ready.set()
            if connection is not None:
                connection.rollback()
        finally:
            if connection is not None:
                connection.close()

    def _lock_reaper_worker(self, env) -> None:
        connection = None
        started = time.monotonic()
        try:
            connection = connect_tidb(
                env,
                database=self.db,
                autocommit=False,
                application_name="sf02-expired-lock-reaper",
                read_timeout=self._TXN_COMMIT_WAIT_SECONDS,
                write_timeout=self._TXN_COMMIT_WAIT_SECONDS,
            )
            with connection.cursor() as cursor:
                cursor.execute("SET SESSION tidb_txn_mode = 'pessimistic'")
                cursor.execute("SET SESSION innodb_lock_wait_timeout = 180")
                cursor.execute("BEGIN PESSIMISTIC")
                cursor.execute(
                    f"SELECT event_id FROM {self.primary_table} "
                    f"WHERE event_id = {self.primary_event_id} FOR UPDATE"
                )
                start_ts = self._current_tso(env)
                connection.commit()
            self._lock_reaper_succeeded = True
            self._reaper_ts_ms = int(time.time() * 1000)
            self._record_attempt(
                env,
                scope="lock_reaper",
                error_code="LOCK_REAPED",
                error_text="business lock acquired after the target lock TTL expired",
                start_ts=start_ts,
                commit_ts=self._current_tso(env),
                elapsed_ms=int((time.monotonic() - started) * 1000),
                final_state="committed_after_ttl",
                phase="reaper_after_ttl",
                lock_heartbeat_ts=self._heartbeat_missed_ts_ms,
                reaper_ts=self._reaper_ts_ms,
            )
        except Exception as exc:
            self._lock_reaper_error = exc
            if connection is not None:
                connection.rollback()
        finally:
            if connection is not None:
                connection.close()

    def _target_transaction_body(self, env, connection) -> None:
        start_ts = 0
        started = time.monotonic()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET SESSION tidb_txn_mode = 'optimistic'")
                cursor.execute("SET SESSION innodb_lock_wait_timeout = 180")
                cursor.execute("SET SESSION tidb_retry_limit = 0")
                cursor.execute("SET SESSION tidb_enable_async_commit = 0")
                cursor.execute("SET SESSION tidb_enable_1pc = 0")
                cursor.execute("SELECT @@tidb_txn_mode")
                txn_mode = str(cursor.fetchone()[0])
                self._observed_txn_mode = txn_mode
                if txn_mode.casefold() != "optimistic":
                    raise RuntimeError(
                        "SF02 target transaction did not enter optimistic mode: "
                        f"observed_txn_mode={txn_mode!r}"
                    )
                cursor.execute("SELECT @@tidb_current_ts")
                start_ts = int(cursor.fetchone()[0])
                cursor.execute("BEGIN OPTIMISTIC")
                self._target_begin_ts_ms = int(time.time() * 1000)
                for table in (self.primary_table, *self.payload_tables[:1], *self.payload_tables[2:]):
                    for event_id in self._PAYLOAD_ROWS:
                        cursor.execute(
                            f"UPDATE {table} SET payload = RPAD(payload, 8192, 'x'), state = 'processing' "
                            f"WHERE event_id = {event_id}"
                        )
                cursor.execute(
                    f"UPDATE {self.business_table} SET amount = amount + {self.target_delta}, "
                    f"status = 'settled', payload = '{self.target_retry_payload}' "
                    f"WHERE order_id = {self.target_order_id}"
                )
                cursor.execute(
                    f"UPDATE {self.job_table} SET state = 'settled', "
                    f"updated_at = CURRENT_TIMESTAMP WHERE job_id = '{self.target_job_id}'"
                )
                self._target_lock_ready.set()
                if not self._commit_ready.wait(timeout=self._TXN_COMMIT_WAIT_SECONDS):
                    raise RuntimeError(
                        "SF02 target transaction was not released after the target Store restart: "
                        f"target={self.target_node!r}, wait_seconds={self._TXN_COMMIT_WAIT_SECONDS}"
                    )
                cursor.execute("SELECT @@tidb_current_ts")
                commit_ts = int(cursor.fetchone()[0])
                connection.commit()
                self._record_attempt(
                    env,
                    scope="target",
                    error_code="UNEXPECTED_COMMIT",
                    error_text="target transaction committed while the SF02 fault was active",
                    start_ts=start_ts,
                    commit_ts=commit_ts,
                    elapsed_ms=int((time.monotonic() - started) * 1000),
                    final_state="unexpected_commit",
                    phase="unexpected_commit",
                    lock_heartbeat_ts=self._heartbeat_missed_ts_ms,
                    reaper_ts=self._reaper_ts_ms,
                )
                self._transaction_error = "UNEXPECTED_COMMIT"
        except pymysql.MySQLError as exc:
            error_text = str(exc)
            commit_ts = self._current_tso(env)
            self._transaction_error = error_text
            self._record_attempt(
                env,
                scope="target",
                error_code=(
                    "TxnLockNotFound"
                    if "txnlocknotfound" in error_text.casefold() or "8022" in error_text
                    else "TRANSACTION_ERROR"
                ),
                error_text=error_text,
                start_ts=start_ts,
                commit_ts=commit_ts,
                elapsed_ms=int((time.monotonic() - started) * 1000),
                final_state="commit_failed",
                phase="commit_failed_after_ttl",
                lock_heartbeat_ts=self._heartbeat_missed_ts_ms,
                reaper_ts=self._reaper_ts_ms,
            )
            connection.rollback()

    def _current_tso(self, env) -> int:
        connection = connect_tidb(
            env,
            database=self.db,
            autocommit=True,
            application_name="sf02-target-tso-probe",
            read_timeout=30,
            write_timeout=30,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT @@tidb_current_ts")
                return int(cursor.fetchone()[0])
        finally:
            connection.close()

    def _record_attempt(
        self,
        env,
        *,
        scope: str,
        error_code: str,
        error_text: str,
        start_ts: int,
        commit_ts: int,
        elapsed_ms: int,
        final_state: str,
        phase: str,
        lock_heartbeat_ts: int,
        reaper_ts: int,
    ) -> None:
        connection = connect_tidb(
            env,
            database=self.db,
            autocommit=True,
            application_name="sf02-attempt-audit",
            read_timeout=30,
            write_timeout=30,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"INSERT INTO {self.attempt_table} "
                    "(scope, job_id, order_id, error_code, error_text, start_ts, commit_ts, elapsed_ms, lock_ttl_ms, "
                    "primary_table, primary_key_value, primary_key_hash, lock_heartbeat_ts, renewal_count, reaper_ts, phase, final_state) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        scope,
                        self.target_job_id,
                        self.target_order_id,
                        error_code,
                        error_text[:512],
                        start_ts,
                        commit_ts,
                        elapsed_ms,
                        self._LOCK_TTL_MS,
                        self.primary_table,
                        self.primary_event_id,
                        self.primary_key_hash,
                        lock_heartbeat_ts,
                        0,
                        reaper_ts,
                        phase,
                        final_state,
                    ),
                )
        finally:
            connection.close()

    def _update_target_attempt_timeline(self, env) -> None:
        require_sql_success(
            env.execute_bootstrap_sql(
                f"UPDATE {self.db}.{self.attempt_table} SET reaper_ts={self._reaper_ts_ms}, "
                f"phase='commit_failed_after_ttl' WHERE scope='target' "
                f"AND job_id='{self.target_job_id}' AND final_state='commit_failed' "
                "ORDER BY attempt_id DESC LIMIT 1"
            ),
            "complete SF02 target TTL timeline",
        )

    def _join_transaction_thread(self) -> None:
        transaction_thread = getattr(self, "_transaction_thread", None)
        if transaction_thread is not None:
            join_thread(transaction_thread, 30, "SF02 target transaction cleanup")
        reaper_thread = getattr(self, "_lock_reaper_thread", None)
        if reaper_thread is not None:
            join_thread(reaper_thread, 30, "SF02 expired-lock reaper cleanup")
        tail_thread = getattr(self, "_tail_thread", None)
        if tail_thread is not None:
            join_thread(tail_thread, 30, "SF02 target persistence tail cleanup")
        blocker_thread = getattr(self, "_blocker_thread", None)
        if blocker_thread is not None:
            join_thread(blocker_thread, 30, "SF02 secondary lock blocker cleanup")

    def _verify_tables(self, env) -> None:
        payload = json_object(
            env.execute_sql(
                f"SELECT (SELECT COUNT(*) FROM {self.db}.{self.business_table}), "
                f"(SELECT COUNT(*) FROM {self.db}.{self.job_table}), "
                f"(SELECT COUNT(*) FROM {self.db}.{self.decoy_tables[0]})"
            ),
            "verify SF02 persistent tables",
        )
        rows = payload["result"]
        if rows != [[self.row_count, 25, 24]]:
            raise RuntimeError(
                "SF02 persistent tables changed before activation: "
                f"expected={[self.row_count, 25, 24]!r}, observed={rows!r}"
            )
SF02_DB = "test"
SF02_BUSINESS_TABLE = "sf02_orders"
SF02_JOB_TABLE = "sf02_settlement_jobs"
SF02_RETRY_PLAN_TABLE = "sf02_settlement_retry_plan"
SF02_PAYLOAD_TABLES = (
    "sf02_settlement_payload_a",
    "sf02_settlement_payload_b",
    "sf02_settlement_payload_c",
)
SF02_ATTEMPT_TABLE = "sf02_transaction_attempts"
SF02_LEDGER_TABLE = "sf02_settlement_ledger"
SF02_DECOY_TABLES = (
    "sf02_payment_events",
    "sf02_inventory_reservations",
    "sf02_order_audit",
    "sf02_shipping_events",
    "sf02_report_cache",
)
SF02_ROWS = 256
SF02_TARGET_ORDER_ID = 42
SF02_TARGET_JOB_ID = "sf02-settlement-042"
SF02_TARGET_DELTA = 37
SF02_BASE_SUM = sf02_base_amount_sum(SF02_ROWS)
SF02_BASE_CHECKSUM = sf02_base_checksum(SF02_ROWS)
SF02_TARGET_OLD_CRC = sf02_order_crc(SF02_TARGET_ORDER_ID)
SF02_TARGET_NEW_CRC = sf02_retry_order_crc(SF02_TARGET_ORDER_ID)
SF02_POST_CHECKSUM = SF02_BASE_CHECKSUM ^ SF02_TARGET_OLD_CRC ^ SF02_TARGET_NEW_CRC
SF02_EXPECTED_PAYLOAD_CHECKSUMS = tuple(
    sf02_expected_payload_checksum(table_index, 32)
    for table_index in range(1, 4)
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureSf02Case(TiDBScenarioCase):
    db: str
    business_table: str
    job_table: str
    retry_plan_table: str
    payload_tables: tuple[str, ...]
    attempt_table: str
    ledger_table: str
    decoy_tables: tuple[str, ...]
    row_count: int
    target_order_id: int
    target_job_id: str
    target_delta: int
    target_retry_payload: str
    target_initial_amount: int
    expected_target_row_crc: int
    expected_base_amount_sum: int
    expected_base_checksum: int
    expected_post_amount_sum: int
    expected_post_checksum: int
    expected_workset_rows: int
    expected_payload_checksums: tuple[tuple[int, int, int], ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbSystemFailureSf02ForSlowStoreLockTtlScenarioCase(TidbSystemFailureSf02Case):
    pass


_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="sf02_checkout_order_lookup",
            sql=f"SELECT order_id, customer_id, amount, status FROM {SF02_DB}.{SF02_BUSINESS_TABLE} WHERE order_id BETWEEN 1 AND 96 ORDER BY order_id LIMIT 24",
            qps=0.55,
            tier="BUSINESS_READ",
            application_name="checkout-api",
        ),
        WorkloadProfile(
            name="sf02_settlement_retry_queue",
            sql=f"SELECT job_id, order_id, requested_delta, workset_rows, state FROM {SF02_DB}.{SF02_JOB_TABLE} WHERE state <> 'committed' ORDER BY updated_at, job_id LIMIT 24",
            qps=0.38,
            tier="BUSINESS_READ",
            application_name="settlement-worker",
        ),
        WorkloadProfile(
            name="sf02_settlement_payload_probe",
            sql=f"SELECT event_id, payload FROM {SF02_DB}.{SF02_PAYLOAD_TABLES[0]} WHERE event_id BETWEEN 1 AND 24 ORDER BY event_id LIMIT 24",
            qps=0.24,
            tier="BUSINESS_READ",
            application_name="settlement-payload-reader",
        ),
        WorkloadProfile(
            name="sf02_order_checksum_probe",
            sql=f"SELECT COUNT(*), SUM(amount), BIT_XOR(row_crc) FROM {SF02_DB}.{SF02_BUSINESS_TABLE} WHERE order_id BETWEEN 1 AND 256",
            qps=0.16,
            tier="BUSINESS_READ",
            application_name="reconciliation-monitor",
        ),
        WorkloadProfile(
            name="sf02_target_row_touch_noise",
            sql=f"UPDATE {SF02_DB}.{SF02_BUSINESS_TABLE} SET payload = payload WHERE order_id IN (7,19,77,133)",
            qps=0.22,
            tier="BUSINESS_WRITE_NOISE",
            application_name="order-status-writer",
        ),
        WorkloadProfile(
            name="sf02_payment_rollup",
            sql=f"SELECT state, COUNT(*), SUM(amount) FROM {SF02_DB}.sf02_payment_events GROUP BY state ORDER BY state",
            qps=0.32,
            tier="BUSINESS_NOISE",
            application_name="payment-ledger",
        ),
        WorkloadProfile(
            name="sf02_inventory_reservation_scan",
            sql=f"SELECT account_id, SUM(amount), COUNT(*) FROM {SF02_DB}.sf02_inventory_reservations GROUP BY account_id ORDER BY account_id LIMIT 20",
            qps=0.28,
            tier="BUSINESS_NOISE",
            application_name="inventory-service",
        ),
        WorkloadProfile(
            name="sf02_audit_window",
            sql=f"SELECT state, COUNT(*) FROM {SF02_DB}.sf02_order_audit WHERE event_id BETWEEN 1 AND 20 GROUP BY state",
            qps=0.30,
            tier="BUSINESS_NOISE",
            application_name="risk-audit",
        ),
        WorkloadProfile(
            name="sf02_shipping_summary",
            sql=f"SELECT state, SUM(amount), COUNT(*) FROM {SF02_DB}.sf02_shipping_events GROUP BY state",
            qps=0.25,
            tier="BUSINESS_NOISE",
            application_name="shipping-planner",
        ),
        WorkloadProfile(
            name="sf02_report_cache_probe",
            sql=f"SELECT event_id, payload FROM {SF02_DB}.sf02_report_cache WHERE event_id BETWEEN 1 AND 18 ORDER BY event_id",
            qps=0.24,
            tier="REPORTING_NOISE",
            application_name="reporting-dashboard",
        ),
        WorkloadProfile(
            name="sf02_region_status_monitor",
            sql=(
                "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE "
                "FROM INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_SCHEMA='test' ORDER BY TABLE_NAME LIMIT 80"
            ),
            qps=0.18,
            tier="MONITOR",
            application_name="region-dashboard",
        ),
        WorkloadProfile(
            name="sf02_region_peer_monitor",
            sql="SELECT REGION_ID, STORE_ID, IS_LEADER, STATUS, DOWN_SECONDS FROM INFORMATION_SCHEMA.TIKV_REGION_PEERS ORDER BY DOWN_SECONDS DESC LIMIT 80",
            qps=0.18,
            tier="MONITOR",
            application_name="replication-dashboard",
        ),
        WorkloadProfile(
            name="sf02_cluster_store_monitor",
            sql="SELECT STORE_ID, STORE_STATE_NAME, LEADER_COUNT, REGION_COUNT, AVAILABLE FROM INFORMATION_SCHEMA.TIKV_STORE_STATUS ORDER BY STORE_ID",
            qps=0.22,
            tier="MONITOR",
            application_name="pd-dashboard",
        ),
        WorkloadProfile(
            name="sf02_attempt_history_noise",
            sql=f"SELECT scope, error_code, final_state, COUNT(*) FROM {SF02_DB}.{SF02_ATTEMPT_TABLE} GROUP BY scope, error_code, final_state ORDER BY COUNT(*) DESC, scope LIMIT 40",
            qps=0.24,
            tier="MONITOR",
            application_name="settlement-observability",
        ),
        WorkloadProfile(
            name="sf02_payload_b_scan",
            sql=f"SELECT event_id, state, LENGTH(payload) FROM {SF02_DB}.{SF02_PAYLOAD_TABLES[1]} WHERE event_id BETWEEN 1 AND 40 ORDER BY event_id LIMIT 32",
            qps=0.26,
            tier="BUSINESS_NOISE",
            application_name="settlement-payload-b-reader",
        ),
        WorkloadProfile(
            name="sf02_payload_c_scan",
            sql=f"SELECT event_id, state, LENGTH(payload) FROM {SF02_DB}.{SF02_PAYLOAD_TABLES[2]} WHERE event_id BETWEEN 9 AND 48 ORDER BY event_id LIMIT 32",
            qps=0.26,
            tier="BUSINESS_NOISE",
            application_name="settlement-payload-c-reader",
        ),
        WorkloadProfile(
            name="sf02_payment_inventory_join",
            sql=f"SELECT p.event_id, p.account_id, p.amount, i.amount FROM {SF02_DB}.sf02_payment_events p JOIN {SF02_DB}.sf02_inventory_reservations i ON i.event_id=p.event_id WHERE p.event_id BETWEEN 1 AND 24 ORDER BY p.event_id LIMIT 24",
            qps=0.24,
            tier="BUSINESS_NOISE",
            application_name="payment-inventory-reconciliation",
        ),
        WorkloadProfile(
            name="sf02_audit_shipping_join",
            sql=f"SELECT a.event_id, a.account_id, s.amount, a.state FROM {SF02_DB}.sf02_order_audit a JOIN {SF02_DB}.sf02_shipping_events s ON s.event_id=a.event_id WHERE a.event_id BETWEEN 1 AND 24 ORDER BY a.event_id LIMIT 24",
            qps=0.22,
            tier="BUSINESS_NOISE",
            application_name="audit-shipping-reconciliation",
        ),
        WorkloadProfile(
            name="sf02_customer_amount_summary",
            sql=f"SELECT customer_id, COUNT(*), SUM(amount) FROM {SF02_DB}.{SF02_BUSINESS_TABLE} GROUP BY customer_id ORDER BY SUM(amount) DESC LIMIT 37",
            qps=0.22,
            tier="BUSINESS_NOISE",
            application_name="customer-balance-dashboard",
        ),
    ),
    worker_count=12,
    seed=0x5F02,
    start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
    warmup_seconds=6,
)


_CASE = TidbSystemFailureSf02ForSlowStoreLockTtlScenarioCase(
    case_id="slow_store_lock_ttl_commit_failure",
    case_no=0,
    evaluator=TidbSystemFailureSf02EvaluatorCase,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": factor,
                    "entity": "slow_store_lock_ttl_commit_failure",
                    "evidence": [f"reference evidence: {factor}"],
                }
                for factor in (
                    "The target settlement transaction failed at commit with TiDB error 8022 / TxnLockNotFound after its ordinary 2PC lock TTL window, rather than being an ordinary lock wait or deadlock.",
                    "Exactly one TiKV Store in the target incident had a low storage.io-rate-limit write budget while the other Stores remained healthy; the I/O fault was Store-scoped, not cluster-wide.",
                    "The target business table Region carrying the settlement key had the degraded Store as its leader or peer, linking the Store fault to this transaction's key range.",
                    "The same transaction window showed a write, Raft, or apply persistence tail on the affected Store, so its foreground transaction path could not persist and acknowledge work within the normal latency envelope.",
                    "The Store I/O tail delayed ordinary 2PC lock TTL renewal until the lock expired and another transaction cleaned it, which caused the target commit to return TxnLockNotFound.",
                    "The failed attempt was the named settlement job for the target order, its writes rolled back, and recovery requires one targeted retry after the Store path is restored rather than deleting or skipping the business update.",
                )
            ]
        },
        "outcome": {
            "changes": [
                "restored the original storage.io-rate-limit on the exact degraded TiKV Store",
                "retried the named settlement job for the target order with the requested delta",
                "recorded one applied settlement ledger entry",
            ],
            "verification": [
                "the target Store configuration exactly matches its pre-fault configuration",
                "the business Region has three Up peers and a valid leader",
                "the target order, job, ledger, decoy objects, and business checksum match the expected final state",
            ],
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification.",
    },
    title="A TiDB settlement path is incomplete while the cluster remains partially available.",
    alert=(
        "[CRITICAL] One class of settlement writes is not completing within its normal window, while reads "
        "and unrelated writes continue to serve. The incident window contains transaction attempts, lock/"
        "timeout history, component latency and storage telemetry, Region placement data, and TiDB/TiKV logs; "
        "same-domain retries and historical failures are also present. Trace the affected operation across "
        "SQL, transaction, Region, Store, and component evidence, distinguish a local data-path problem "
        "from ordinary contention or an old error, and restore the business operation without changing "
        "unrelated Store settings or data. Verify the affected and decoy business records afterward. "
        "After confirming the exact target Store and sf02-settlement-042, read the public retry plan in "
        "test.sf02_settlement_retry_plan and the SHOW CREATE TABLE constraints before composing the retry. "
        "You may restore that Store's I/O configuration, retry the named job, and submit the necessary "
        "order/payload/ledger business writes using the plan's public workset, payload template, legal states, "
        "and CRC rules; "
        "do not modify decoys, historical attempts, non-target Stores, or delete data."
    ),
    initial_state={
        "status": "degraded_transaction_commit",
        "business_reads": "available",
        "target_job": SF02_TARGET_JOB_ID,
        "target_transaction": "commit failed after lock TTL window",
        "cluster": "three active TiKV replicas and one deferred maintenance Store",
    },
    expected_target={
        "status": "recovered",
        "target_store": "all-io throttle removed and Store healthy",
        "target_job": "committed",
        "target_order": f"amount + {SF02_TARGET_DELTA}, settled",
        "target_ledger": "one applied entry",
        "business_checksum": f"({SF02_ROWS},{SF02_BASE_SUM + SF02_TARGET_DELTA},{SF02_POST_CHECKSUM})",
        "decoys": "unchanged",
    },
    background_workload=_BACKGROUND_WORKLOAD,
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.930288,
        reference_run_ids=(
            "reference-226__"
            "tidb_system_failure_sf02__slow_store_lock_ttl_commit_failure__mock__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=4,
        tidb_count=2,
        sql_timeout_seconds=120,
        tikv_config_writable=True,
        tikv_io_rate_limit_strict=True,
        deferred_tikv_count=1,
        readiness_timeout_seconds=1800,
    ),
    db=SF02_DB,
    business_table=SF02_BUSINESS_TABLE,
    job_table=SF02_JOB_TABLE,
    retry_plan_table=SF02_RETRY_PLAN_TABLE,
    payload_tables=SF02_PAYLOAD_TABLES,
    attempt_table=SF02_ATTEMPT_TABLE,
    ledger_table=SF02_LEDGER_TABLE,
    decoy_tables=SF02_DECOY_TABLES,
    row_count=SF02_ROWS,
    target_order_id=SF02_TARGET_ORDER_ID,
    target_job_id=SF02_TARGET_JOB_ID,
    target_initial_amount=sf02_order_amount(SF02_TARGET_ORDER_ID),
    expected_target_row_crc=SF02_TARGET_NEW_CRC,
    target_delta=SF02_TARGET_DELTA,
    target_retry_payload=SF02_TARGET_RETRY_PAYLOAD,
    expected_base_amount_sum=SF02_BASE_SUM,
    expected_base_checksum=SF02_BASE_CHECKSUM,
    expected_post_amount_sum=SF02_BASE_SUM + SF02_TARGET_DELTA,
    expected_post_checksum=SF02_POST_CHECKSUM,
    expected_workset_rows=32,
    expected_payload_checksums=SF02_EXPECTED_PAYLOAD_CHECKSUMS,
)


_FOCUSED_SF02_WORKLOAD = replace(
    _BACKGROUND_WORKLOAD,
    profiles=tuple(
        profile
        for profile in _BACKGROUND_WORKLOAD.profiles
        if profile.name in {
            "sf02_checkout_order_lookup",
            "sf02_settlement_retry_queue",
            "sf02_settlement_payload_probe",
            "sf02_order_checksum_probe",
            "sf02_region_status_monitor",
            "sf02_region_peer_monitor",
            "sf02_cluster_store_monitor",
            "sf02_attempt_history_noise",
        }
    ),
    worker_count=6,
    warmup_seconds=4,
)

_FOCUSED_SF02_ORDER_ID = 43
_FOCUSED_SF02_DELTA = 29
_FOCUSED_SF02_JOB_ID = "sf02-settlement-043-focused"
_FOCUSED_SF02_NEW_CHECKSUM = sf02_retry_order_crc(_FOCUSED_SF02_ORDER_ID)
_FOCUSED_SF02_POST_CHECKSUM = (
    SF02_BASE_CHECKSUM
    ^ sf02_order_crc(_FOCUSED_SF02_ORDER_ID)
    ^ _FOCUSED_SF02_NEW_CHECKSUM
)
_FOCUSED_SF02_RETRY_PAYLOAD = "settled-after-focused-store-retry"
_FOCUSED_SF02_EXPECTED_PAYLOAD_CHECKSUMS = tuple(
    sf02_expected_payload_checksum(table_index, 32, _FOCUSED_SF02_RETRY_PAYLOAD)
    for table_index in range(1, 4)
)

_FOCUSED_SF02_CASE = replace(
    _CASE,
    case_id="slow_store_lock_ttl_simple",
    case_no=1,
    evaluator=TidbSystemFailureSf02FocusedEvaluatorCase,
    background_workload=_FOCUSED_SF02_WORKLOAD,
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": (
                        "The named target settlement transaction committed after its ordinary 2PC lock TTL window "
                        "and returned TiDB error 8022 / TxnLockNotFound because the target Store has a Store-scoped "
                        "storage I/O limiter and persistence tail in the target transaction window: its write, "
                        "Raft, or apply persistence tail begins before the 3 second TTL renewal deadline and "
                        "overlaps the target primary transaction, so the primary lock heartbeat was not renewed "
                        "before TTL expiry and the lock reaper acquired the same payload_b primary key and "
                        "committed before the target commit returned 8022."
                    ),
                    "entity": "slow_store_lock_ttl_simple",
                    "evidence": [
                        "the target attempt is scope=target and final_state=commit_failed while the target Store "
                        "config history and disk/log telemetry overlap the transaction window before lock_ttl_ms=3000"
                    ],
                },
                {
                    "type": "finding",
                    "factor": (
                        "The failed transaction's primary table and key are in sf02_settlement_payload_b whose "
                        "primary Region leader or peer set intersects the degraded Store while the orders Region is "
                        "a healthy sibling and cannot identify the target by itself; the failed named settlement "
                        "attempt rolled back its order, payload, and job writes, so recovery requires restoring the "
                        "exact Store path and retrying only the target settlement business transaction, not "
                        "manually writing attempt or ledger rows or skipping the update."
                    ),
                    "entity": "slow_store_lock_ttl_simple",
                    "evidence": [
                        "region peers map the payload_b primary key to the degraded Store and the target job is "
                        "the only scope=target commit_failed row"
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "restored the original storage.io-rate-limit on the exact degraded TiKV Store",
                "retried the named settlement job for the target order with the requested delta",
                "recorded one applied settlement ledger entry",
            ],
            "verification": [
                "the target Store configuration exactly matches its pre-fault configuration",
                "the business Region has three Up peers and a valid leader",
                "the target order, job, ledger, decoy objects, and business checksum match the expected final state",
            ],
        },
        "summary": "The focused scripted mock restored the Store path and verified the retried settlement.",
    },
    target_order_id=_FOCUSED_SF02_ORDER_ID,
    target_job_id=_FOCUSED_SF02_JOB_ID,
    target_delta=_FOCUSED_SF02_DELTA,
    target_retry_payload=_FOCUSED_SF02_RETRY_PAYLOAD,
    target_initial_amount=sf02_order_amount(_FOCUSED_SF02_ORDER_ID),
    expected_target_row_crc=_FOCUSED_SF02_NEW_CHECKSUM,
    expected_post_amount_sum=SF02_BASE_SUM + _FOCUSED_SF02_DELTA,
    expected_post_checksum=_FOCUSED_SF02_POST_CHECKSUM,
    expected_payload_checksums=_FOCUSED_SF02_EXPECTED_PAYLOAD_CHECKSUMS,
    initial_state={
        **_CASE.initial_state,
        "target_job": _FOCUSED_SF02_JOB_ID,
    },
    expected_target={
        **_CASE.expected_target,
        "target_job": "committed",
        "target_order": f"amount + {_FOCUSED_SF02_DELTA}, settled",
        "business_checksum": f"({SF02_ROWS},{SF02_BASE_SUM + _FOCUSED_SF02_DELTA},{_FOCUSED_SF02_POST_CHECKSUM})",
    },
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.919141,
        reference_run_ids=(
            "reference-81__"
            "tidb_system_failure_sf02__slow_store_lock_ttl_simple__mock__r001",
        ),
    ),
)


class TidbSystemFailureSf02Scenario(TiDBScenario):
    scenario_id = "tidb_system_failure_sf02"
    description = "Investigates an incomplete TiDB settlement path and restores the affected business operation safely."
    cases = (_CASE, _FOCUSED_SF02_CASE)

    def build_fault_plan(self, case: TidbSystemFailureSf02Case) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbSystemFailureSf02SlowStoreInjector,
                config={
                    "db": case.db,
                    "business_table": case.business_table,
                    "job_table": case.job_table,
                    "retry_plan_table": case.retry_plan_table,
                    "payload_tables": case.payload_tables,
                    "attempt_table": case.attempt_table,
                    "ledger_table": case.ledger_table,
                    "decoy_tables": case.decoy_tables,
                    "row_count": case.row_count,
                    "target_order_id": case.target_order_id,
                    "target_job_id": case.target_job_id,
                    "target_delta": case.target_delta,
                    "target_retry_payload": case.target_retry_payload,
                },
            ),
        )
