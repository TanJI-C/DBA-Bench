import json
import hashlib
import zlib
from copy import deepcopy
from types import SimpleNamespace

import pytest

from src.database.sql import sql_literal
from src.execution.deployment import TiDBDockerDeployment
from src.project_paths import REPOSITORY_ROOT
from src.scenarios import SCENARIO_REGISTRY
from src.scenarios.base import CaseRun
from src.scenarios.tidb import TidbSystemFailureGcMvccRecoveryScenario
from src.scenarios.tidb.system_failure.gc_mvcc_recovery import (
    K01_RECOVERY_TASK_APPLICANT,
    K01_RECOVERY_TASK_NO,
    K01_RECOVERY_TASK_TABLE,
    K01_RECOVERY_TASK_WINDOW,
    TidbSystemFailureGcMvccRecoveryInjector,
    _decode_abnormal_async_commit_lock,
    _encode_abnormal_async_commit_lock,
    _encode_memcomparable_key,
    _select_region_for_key,
    _table_row_key,
    _var_u64,
)


SCENARIO = TidbSystemFailureGcMvccRecoveryScenario()
CASE = SCENARIO.get_case("recover_mvcc_after_async_commit_lock")
REGION_ID = 901
STORE_TARGETS = ["tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"]
PEER_STORE_IDS = [11, 12, 13]
TARGET_KEY_HEX = "7461726765742d726f772d3137"


def _gc_status(safe_point: str, *, phases=True):
    return {
        "sql_variables": [
            {"variable_name": "tikv_gc_last_run_time", "variable_value": "2026-08-18 12:00:00"},
            {"variable_name": "tikv_gc_safe_point", "variable_value": safe_point},
        ],
        "global_variables": [{"Variable_name": "tidb_gc_enable", "Value": "ON"}],
        "delete_ranges": [],
        "prometheus_raw": {
            name: ([{"metric": {"phase": name}, "value": ["1", "1"]}] if phases else [])
            for name in ("gc_worker", "resolve_locks", "delete_ranges", "do_gc")
        },
    }


EVIDENCE = {
    "region_id": REGION_ID,
    "store_targets": STORE_TARGETS,
    "peer_store_ids": PEER_STORE_IDS,
    "target_key_hex": TARGET_KEY_HEX,
    "start_ts": 100,
    "commit_ts": 99,
    "min_commit_ts": 99,
    "normal_lock_connection_id": 701,
    "long_tx_connection_id": 702,
    "target_legal_lock_connection_id": 703,
    "target_stuck_holder_connection_id": 704,
    "business_truth": {},
    "gc_status_before": _gc_status("20260819-01:37:01.376 +0000"),
    "recovery_task_table": f"{CASE.db}.{K01_RECOVERY_TASK_TABLE}",
}


class FakeDeployment:
    NODES = {
        "tikv/tikv-0": "tikv-0",
        "tikv/tikv-1": "tikv-1",
        "tikv/tikv-2": "tikv-2",
    }

    def __init__(self):
        self.lock_present = False

    def pd_request(self, method, path, body=None):
        if path == f"/pd/api/v1/region/id/{REGION_ID}":
            return {
                "id": REGION_ID,
                "peers": [
                    {"id": 101 + index, "store_id": store_id}
                    for index, store_id in enumerate(PEER_STORE_IDS)
                ],
                "leader": {"id": 102, "store_id": PEER_STORE_IDS[1]},
            }
        if path == "/pd/api/v1/stores":
            return {
                "stores": [
                    {
                        "store": {
                            "id": store_id,
                            "address": f"tikv-{index}:20160",
                            "state_name": "Up",
                        }
                    }
                    for index, store_id in enumerate(PEER_STORE_IDS)
                ]
            }
        raise AssertionError(f"unexpected PD request: method={method!r}, path={path!r}, body={body!r}")

    def mvcc_lock_list(self, region_id, store_targets, limit, from_key=None, to_key=None):
        assert region_id == REGION_ID
        assert list(store_targets) == STORE_TARGETS
        assert limit == 32
        records = [{"key_hex": TARGET_KEY_HEX, "value_hex": "50"}] if self.lock_present else []
        return {
            "region_id": region_id,
            "peer_store_ids": PEER_STORE_IDS,
            "store_targets": STORE_TARGETS,
            "peers": [{"target": target, "records": list(records)} for target in STORE_TARGETS],
        }


class FakeNeighborInjector:
    def __init__(self, alive=True):
        self.alive = alive

    def legal_neighbors_alive(self):
        return self.alive


class FakeEnv:
    def __init__(self, *, recovered=True, phases=True, wrong_write=False):
        self.deployment = FakeDeployment()
        self.recovered = recovered
        self.wrong_write = wrong_write
        self._gc_after = _gc_status("20260819-01:38:01.376 +0000", phases=phases)

    def _mvcc_gc_status(self):
        return self._gc_after

    def execute_sql_trusted(self, sql):
        normalized = " ".join(sql.casefold().split())
        if "where id = 10001" in normalized:
            rows = (
                []
                if self.wrong_write or not self.recovered
                else [[CASE.new_write_amount, CASE.new_write_payload, _new_write_crc()]]
            )
        elif f"from {CASE.db}.{CASE.target_table}" in normalized:
            if self.wrong_write:
                rows = [[CASE.post_count, CASE.expected_sum + 1509, CASE.expected_checksum]]
            elif self.recovered:
                rows = [[CASE.post_count, CASE.post_sum, CASE.post_checksum]]
            else:
                rows = [[CASE.expected_count, CASE.expected_sum, CASE.expected_checksum]]
        elif f"from {CASE.db}.{CASE.healthy_table}" in normalized:
            rows = [[CASE.expected_count, CASE.expected_sum, CASE.expected_checksum]]
        elif f"from {CASE.db}.{CASE.long_tx_table}" in normalized:
            rows = [[CASE.expected_count, CASE.expected_sum, CASE.expected_checksum]]
        else:
            raise AssertionError(f"unexpected trusted SQL: {sql!r}")
        return json.dumps({"status": "success", "result": rows})


def _new_write_crc():
    return zlib.crc32(f"k01:{CASE.new_write_id}:{CASE.new_write_amount}".encode()) & 0xFFFFFFFF


def _run(report, *, env=None, actions=(), recovered=True, wrong_write=False, lock_present=False, phases=True, alive=True):
    env = env or FakeEnv(recovered=recovered, phases=phases, wrong_write=wrong_write)
    env.recovered = recovered
    env.deployment.lock_present = lock_present
    injection = SimpleNamespace(
        evidence=deepcopy(EVIDENCE),
        injector=FakeNeighborInjector(alive=alive),
    )
    run = CaseRun(
        run_id="k01-test-run",
        scenario=SCENARIO,
        case=CASE,
        env=env,
        injections=[injection],
        action_history=[*actions, {"api": "submit", "args": report}],
    )
    evaluator = CASE.evaluator(env)
    evaluator.capture_safety_baseline(run)
    return evaluator.evaluate(run)


def _successful_action(api, args):
    return {"api": api, "args": args, "result": {"status": "success", "result": {}}}


def _inspect_action():
    return {
        "api": "manage_cluster",
        "args": {
            "resource": "storage_maintenance",
            "operation": "preflight",
            "target": f"region/{REGION_ID}",
            "parameters": {"store_targets": STORE_TARGETS},
        },
        "result": {"status": "success", "result": {"preflight_id": "mvcc-test-inspection"}},
    }


def _execute_action(*, target=f"region/{REGION_ID}", stores=None):
    return _successful_action(
        "manage_cluster",
        {
            "resource": "storage_maintenance",
            "operation": "apply",
            "target": target,
            "parameters": {"preflight_id": "mvcc-test-inspection"},
        },
    )


def test_k01_identity_topology_fault_plan_and_five_phase_contract():
    registration = next(item for item in SCENARIO_REGISTRY if item.scenario_id == SCENARIO.scenario_id)
    plan = SCENARIO.build_fault_plan(CASE)[0]

    assert registration.entrypoint == "run_tidb_system_failure_gc_mvcc_recovery_scenario.py"
    assert CASE.case_no == 0
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert CASE.runtime.topology.pd_count == 3
    assert CASE.runtime.topology.tikv_count == 3
    assert CASE.runtime.topology.tidb_count == 2
    assert CASE.runtime.bootstrap_cache_enabled is False
    assert plan.config["scope"].startswith("one dynamically discovered key-range Region")
    assert CASE.minimum_target_region_count >= 4
    assert all(callable(getattr(TidbSystemFailureGcMvccRecoveryInjector, phase)) for phase in (
        "install", "activate", "prepare_observability", "quiesce", "recover"
    ))


def test_k01_lock_codec_exposes_invalid_async_commit_timestamp_order():
    key = _table_row_key(812, CASE.target_row_id)
    value_hex, facts = _encode_abnormal_async_commit_lock(key)

    value = bytes.fromhex(value_hex)
    assert value[:1] == b"P"
    assert facts["min_commit_ts"] <= facts["start_ts"]
    assert facts["commit_ts"] == facts["min_commit_ts"]
    assert key.hex().upper() in value_hex


def test_k01_persisted_lock_decoder_reconstructs_timestamp_facts():
    key = _table_row_key(812, CASE.target_row_id)
    value_hex, encoded = _encode_abnormal_async_commit_lock(key)

    assert _decode_abnormal_async_commit_lock(value_hex, key) == encoded


def test_k01_pending_fault_key_and_verification_write_are_public():
    assert CASE.target_row_id == CASE.row_count + 1
    assert "exactly one" in CASE.alert
    assert "authorized business write" in CASE.alert
    assert "verification row" in CASE.alert
    assert "recovery-task evidence" in CASE.alert
    assert "id=10001" not in CASE.alert
    assert "amount=9317" not in CASE.alert
    assert "payload='k01-recovered-write'" not in CASE.alert
    assert "row_crc=630828116" not in CASE.alert
    assert "spans multiple distributed key ranges" not in CASE.alert
    assert "sibling Regions" not in CASE.alert


class _TicketCaptureEnv:
    def __init__(self):
        self.statements = []

    def execute_internal_sql(self, sql):
        self.statements.append(sql)
        if sql.startswith("SELECT target_table"):
            return json.dumps({"status": "success", "result": [[
                f"{CASE.db}.{CASE.target_table}",
                1,
                CASE.new_write_id,
                CASE.new_write_amount,
                CASE.new_write_payload,
                _new_write_crc(),
            ]]})
        return json.dumps({"status": "success", "result": []})

    def _query_rows(self, sql):
        return [{"row_count": 4, "amount_sum": 5, "checksum": 6}]


def test_k01_recovery_task_ticket_publishes_the_authorized_write_spec():
    injector = TidbSystemFailureGcMvccRecoveryInjector()
    env = _TicketCaptureEnv()

    injector._prepare_tables(SimpleNamespace(case=CASE, env=env))

    progress_create = next(
        statement
        for statement in env.statements
        if f"CREATE TABLE {CASE.db}.{CASE.backfill_progress_table}" in statement
    )
    assert "seq BIGINT AUTO_INCREMENT PRIMARY KEY" in progress_create

    create = next(
        statement
        for statement in env.statements
        if f"CREATE TABLE {CASE.db}.{K01_RECOVERY_TASK_TABLE}" in statement
    )
    insert = next(
        statement
        for statement in env.statements
        if f"INSERT INTO {CASE.db}.{K01_RECOVERY_TASK_TABLE}" in statement
    )
    for column in (
        "task_no",
        "applicant",
        "approved_window",
        "target_table",
        "authorized_row_count",
        "authorized_row_crc",
    ):
        assert column in create
    assert sql_literal(K01_RECOVERY_TASK_NO) in insert
    assert sql_literal(K01_RECOVERY_TASK_APPLICANT) in insert
    assert sql_literal(K01_RECOVERY_TASK_WINDOW) in insert
    assert sql_literal(f"{CASE.db}.{CASE.target_table}") in insert
    assert sql_literal(CASE.new_write_payload) in insert
    assert f"1, {CASE.new_write_id}, {CASE.new_write_amount}," in insert
    assert f"{_new_write_crc()}," in insert

    # The ticket must publish exactly the row NewWriteVerifier accepts.
    assert (
        CASE.new_write_id,
        CASE.new_write_amount,
        CASE.new_write_payload,
        _new_write_crc(),
    ) == (10001, 9317, "k01-recovered-write", 630828116)


def test_k01_target_table_operator_lock_shares_the_recovery_region():
    assert CASE.target_legal_lock_row_id == 202
    assert CASE.target_legal_lock_row_id != CASE.target_row_id
    assert CASE.target_legal_lock_row_id not in (CASE.normal_lock_row_id, CASE.long_tx_row_id)
    assert CASE.target_legal_lock_row_id < 1024
    assert "open operator session on the target table" in (
        CASE.reference_report["diagnosis"]["conditions"][2]["factor"]
    )
    assert CASE.reference_report["diagnosis"]["conditions"][2]["type"] == "legal_neighbors"


def test_k01_operator_backfill_is_a_real_committed_business_write():
    from src.scenarios.tidb.system_failure.gc_mvcc_recovery import (
        K01_EXPECTED_SUM,
        K01_NEW_WRITE_AMOUNT,
        K01_OPERATOR_BACKFILL_DELTA,
        K01_POST_SUM,
    )

    assert K01_OPERATOR_BACKFILL_DELTA == 2020
    assert K01_POST_SUM == K01_EXPECTED_SUM + K01_OPERATOR_BACKFILL_DELTA + K01_NEW_WRITE_AMOUNT
    assert CASE.post_sum == K01_POST_SUM
    assert CASE.backfill_progress_table == "k01_backfill_progress"
    assert CASE.backfill_commit_rows == 120
    assert "operator backfill" in CASE.alert
    assert "part of the business truth" in CASE.alert
    assert CASE.runtime.tikv_server_config_overrides == {"pessimistic-txn": {"in-memory": False}}


def test_k01_backfill_watchdog_commits_on_progress_signal():
    import src.scenarios.tidb.system_failure.gc_mvcc_recovery as k01_module

    class _FakeCursor:
        def __init__(self, counts=None):
            self.counts = counts if counts is not None else []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, statement):
            pass

        def fetchone(self):
            return [self.counts.pop(0)]

    class _FakePollConnection:
        def __init__(self, counts):
            self.counts = counts
            self.closed = False

        def cursor(self):
            return _FakeCursor(self.counts)

        def close(self):
            self.closed = True

    class _FakeOperatorCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, statement):
            self.connection.refreshes += 1

    class _FakeOperatorConnection:
        def __init__(self):
            self.commits = 0
            self.refreshes = 0

        def cursor(self):
            cursor = _FakeOperatorCursor()
            cursor.connection = self
            return cursor

        def commit(self):
            self.commits += 1

    injector = TidbSystemFailureGcMvccRecoveryInjector()
    injector._target_lock_connection = _FakeOperatorConnection()
    injector._stuck_holder_connection = _FakeOperatorConnection()
    poll_connection = _FakePollConnection([10, CASE.backfill_commit_rows])

    original_connect = k01_module.connect_tidb
    original_poll_seconds = k01_module.K01_BACKFILL_POLL_SECONDS
    k01_module.connect_tidb = lambda env, **kwargs: poll_connection
    k01_module.K01_BACKFILL_POLL_SECONDS = 0
    try:
        injector._watch_backfill_progress(
            SimpleNamespace(
                db=CASE.db,
                target_table=CASE.target_table,
                target_legal_lock_row_id=CASE.target_legal_lock_row_id,
                target_stuck_holder_row_id=CASE.target_stuck_holder_row_id,
                backfill_progress_table=CASE.backfill_progress_table,
                backfill_commit_rows=CASE.backfill_commit_rows,
            ),
            None,
        )
    finally:
        k01_module.connect_tidb = original_connect
        k01_module.K01_BACKFILL_POLL_SECONDS = original_poll_seconds

    assert injector._backfill_committed is True
    assert injector._backfill_commit_error is None
    assert injector._target_lock_connection.commits == 1
    assert injector._stuck_holder_connection.refreshes >= 1
    assert poll_connection.closed


def test_k01_backfill_watchdog_records_broken_commit():
    import src.scenarios.tidb.system_failure.gc_mvcc_recovery as k01_module

    class _BrokenOperatorConnection:
        def commit(self):
            raise RuntimeError("9006: transaction rolled back by conflict")

    injector = TidbSystemFailureGcMvccRecoveryInjector()
    injector._target_lock_connection = _BrokenOperatorConnection()
    injector._stuck_holder_connection = _BrokenOperatorConnection()
    poll_connection_counts = [CASE.backfill_commit_rows]

    class _FakeCursor:
        def __init__(self):
            self.counts = poll_connection_counts

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, statement):
            pass

        def fetchone(self):
            return [self.counts.pop(0)]

    class _FakePollConnection:
        def cursor(self):
            return _FakeCursor()

        def close(self):
            pass

    original_connect = k01_module.connect_tidb
    k01_module.connect_tidb = lambda env, **kwargs: _FakePollConnection()
    try:
        injector._watch_backfill_progress(
            SimpleNamespace(
                db=CASE.db,
                backfill_progress_table=CASE.backfill_progress_table,
                backfill_commit_rows=CASE.backfill_commit_rows,
            ),
            None,
        )
    finally:
        k01_module.connect_tidb = original_connect

    assert injector._backfill_committed is True
    assert "9006" in injector._backfill_commit_error


def test_k01_backfill_watchdog_reconnects_after_dropped_poll_connection():
    import src.scenarios.tidb.system_failure.gc_mvcc_recovery as k01_module

    class _FakeCursor:
        def __init__(self, connection):
            self.connection = connection

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, statement):
            if self.connection.dropped:
                raise RuntimeError("(2013, 'Lost connection to MySQL server during query')")

        def fetchone(self):
            return [CASE.backfill_commit_rows]

    class _FakePollConnection:
        def __init__(self):
            self.dropped = False
            self.closed = False

        def cursor(self):
            return _FakeCursor(self)

        def close(self):
            self.closed = True

    class _FakeOperatorCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, statement):
            pass

    class _FakeOperatorConnection:
        def __init__(self):
            self.commits = 0

        def cursor(self):
            return _FakeOperatorCursor()

        def commit(self):
            self.commits += 1

    injector = TidbSystemFailureGcMvccRecoveryInjector()
    injector._target_lock_connection = _FakeOperatorConnection()
    first = _FakePollConnection()
    first.dropped = True
    second = _FakePollConnection()
    connections = [first, second]

    original_connect = k01_module.connect_tidb
    original_poll_seconds = k01_module.K01_BACKFILL_POLL_SECONDS
    k01_module.connect_tidb = lambda env, **kwargs: connections.pop(0)
    k01_module.K01_BACKFILL_POLL_SECONDS = 0
    try:
        injector._watch_backfill_progress(
            SimpleNamespace(
                db=CASE.db,
                target_table=CASE.target_table,
                target_legal_lock_row_id=CASE.target_legal_lock_row_id,
                target_stuck_holder_row_id=CASE.target_stuck_holder_row_id,
                backfill_progress_table=CASE.backfill_progress_table,
                backfill_commit_rows=CASE.backfill_commit_rows,
            ),
            None,
        )
    finally:
        k01_module.connect_tidb = original_connect
        k01_module.K01_BACKFILL_POLL_SECONDS = original_poll_seconds

    assert first.closed is True
    assert connections == []
    assert injector._backfill_committed is True
    assert injector._backfill_commit_error is None
    assert injector._target_lock_connection.commits == 1


def test_k01_tikv_config_override_rendering():
    from src.execution.deployment import _render_toml_sections

    rendered = _render_toml_sections({"pessimistic-txn": {"in-memory": False}})
    assert rendered == "[pessimistic-txn]\nin-memory = false\n"
    with pytest.raises(TypeError):
        _render_toml_sections({"pessimistic-txn": {"in-memory": [1]}})


def test_k01_four_legal_neighbor_connections_are_tracked():
    class _FakeConnection:
        def __init__(self):
            self.open = True
            self.closed = False

        def rollback(self):
            pass

        def close(self):
            self.closed = True

        def ping(self, reconnect):
            assert reconnect is False

    injector = TidbSystemFailureGcMvccRecoveryInjector()
    injector._connection_ids = {
        "normal_lock_connection_id": 701,
        "long_tx_connection_id": 702,
        "target_legal_lock_connection_id": 703,
        "target_stuck_holder_connection_id": 704,
    }
    injector._normal_lock_connection = _FakeConnection()
    injector._long_tx_connection = _FakeConnection()
    injector._target_lock_connection = None
    injector._stuck_holder_connection = _FakeConnection()

    assert injector.legal_neighbors_alive() is False

    injector._target_lock_connection = _FakeConnection()
    assert injector.legal_neighbors_alive() is True

    injector._close_neighbors()
    assert injector.legal_neighbors_alive() is False
    assert injector._normal_lock_connection is None
    assert injector._long_tx_connection is None
    assert injector._target_lock_connection is None
    assert injector._stuck_holder_connection is None


def test_k01_target_row_key_binds_to_one_live_region_range():
    target_key = _table_row_key(812, CASE.target_row_id)
    encoded_key = _encode_memcomparable_key(target_key).hex().upper()
    rows = [
        (11, "", encoded_key[:-2] + "00"),
        (12, encoded_key[:-2] + "00", ""),
    ]

    assert _select_region_for_key(rows, encoded_key) == rows[1]
    with pytest.raises(RuntimeError, match="exactly one current Region"):
        _select_region_for_key([(11, "", ""), (12, "", "")], encoded_key)


def test_k01_region_scope_requires_the_complete_current_peer_set():
    deployment = object.__new__(TiDBDockerDeployment)
    deployment.NODES = dict(FakeDeployment.NODES)
    deployment.pd_request = FakeDeployment().pd_request
    deployment._pd_stores = lambda: FakeDeployment().pd_request("GET", "/pd/api/v1/stores")["stores"]

    scope = deployment._mvcc_region_scope(REGION_ID, list(reversed(STORE_TARGETS)))

    assert scope["peer_store_ids"] == tuple(PEER_STORE_IDS)
    assert scope["store_targets"] == tuple(STORE_TARGETS)
    with pytest.raises(ValueError, match="exactly the current Region peer Store set"):
        deployment._mvcc_region_scope(REGION_ID, STORE_TARGETS[:2])


def test_k01_memcomparable_key_codec_matches_tikv():
    encoded_start = "7480000000000000FF6A00000000000000F8"
    encoded_end = "7480000000000000FF6B00000000000000F8"

    assert TiDBDockerDeployment._mvcc_decode_memcomparable_key(encoded_start, "start_key") == "74800000000000006A"
    assert TiDBDockerDeployment._mvcc_decode_memcomparable_key(encoded_end, "end_key") == "74800000000000006B"
    with pytest.raises(ValueError, match="invalid mem-comparable marker"):
        TiDBDockerDeployment._mvcc_decode_memcomparable_key("748000000000000000", "start_key")


def test_k01_raw_lock_scan_exposes_origin_key_and_storage_key():
    storage_key_hex = "7A7400000000000000F8"
    summary = TiDBDockerDeployment._mvcc_scan_summary(
        f'key: "{TiDBDockerDeployment._mvcc_hex_to_escaped(storage_key_hex, "test")}", value: "P"\n\nTotal scanned keys: 1\n',
        region_id=REGION_ID,
        target="tikv/tikv-0",
    )

    record = summary["records"][0]
    assert record["key_hex"] == "74"
    assert record["storage_key_hex"] == storage_key_hex
    assert record["encoded_key_hex"] == "7400000000000000F8"
    assert record["value_hex"] == "50"
    assert record["key_escaped"] == "t"
    assert record["value_escaped"] == "P"


def test_k01_raw_lock_scan_rejects_non_data_key():
    with pytest.raises(RuntimeError, match="non-data key"):
        TiDBDockerDeployment._mvcc_scan_summary(
            'key: "t", value: "P"\n\nTotal scanned keys: 1\n',
            region_id=REGION_ID,
            target="tikv/tikv-0",
        )


def test_k01_ldb_rewrite_uses_explicit_hex_prefix():
    deployment = object.__new__(TiDBDockerDeployment)
    deployment.run_id = "k01-ldb-test"
    deployment.release = SimpleNamespace(version="v8.1.0")
    deployment._mvcc_region_scope = lambda region_id, store_targets: {
        "peer_store_ids": (11,),
        "store_targets": ("tikv/tikv-0",),
    }
    observed = {}

    def fake_tikv_ctl(service, arguments, *, region_id, store_targets):
        observed["service"] = service
        observed["command"] = arguments
        observed["region_id"] = region_id
        observed["store_targets"] = store_targets
        return "OK", {"binary_path": "/tikv-ctl"}

    deployment._mvcc_tikv_ctl = fake_tikv_ctl
    deployment._mvcc_offline_call_many = (
        lambda targets, operation, callback: callback(tuple("tikv-0" for _ in targets))
    )

    deployment.rewrite_mvcc_lock(REGION_ID, STORE_TARGETS, "AA", "BB")

    assert observed == {
        "service": "tikv-0",
        "command": [
            "ldb",
            "--db=/data/tikv/db",
            "--column_family=lock",
            "--hex",
            "put",
            "0x7AAA00000000000000F8",
            "0xBB",
        ],
        "region_id": REGION_ID,
        "store_targets": ("tikv/tikv-0",),
    }


def test_k01_ldb_rewrite_uses_one_offline_window_for_all_peers():
    deployment = object.__new__(TiDBDockerDeployment)
    deployment.run_id = "k01-ldb-scope-test"
    deployment.release = SimpleNamespace(version="v8.1.0")
    deployment._mvcc_region_scope = lambda region_id, store_targets: {
        "peer_store_ids": (11, 12, 13),
        "store_targets": tuple(STORE_TARGETS),
    }
    observed = {"targets": None, "calls": 0}

    deployment._mvcc_tikv_ctl = lambda service, arguments, *, region_id, store_targets: (
        "OK", {"binary_path": "/tikv-ctl"}
    )

    def fake_offline_call_many(targets, operation, callback):
        observed["targets"] = targets
        observed["calls"] += 1
        return callback(tuple(target.rsplit("/", 1)[1] for target in targets))

    deployment._mvcc_offline_call_many = fake_offline_call_many

    result = deployment.rewrite_mvcc_lock(REGION_ID, STORE_TARGETS, "AA", "BB")

    assert observed == {"targets": tuple(STORE_TARGETS), "calls": 1}
    assert [item["target"] for item in result["peers"]] == STORE_TARGETS


def test_k01_reference_path_passes_dp_op_sp():
    result = _run(CASE.reference_report, recovered=True)

    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)
    json.dumps(result, ensure_ascii=False)


def test_k01_empty_or_incomplete_diagnosis_is_the_target_failure_mode():
    empty_report = {
        "diagnosis": {"conditions": []},
        "outcome": deepcopy(CASE.reference_report["outcome"]),
        "summary": "The recovery action completed after checking the target state.",
    }
    incomplete_report = deepcopy(CASE.reference_report)
    incomplete_report["diagnosis"]["conditions"] = incomplete_report["diagnosis"]["conditions"][:-1]

    for report in (empty_report, incomplete_report):
        result = _run(report, recovered=True)
        assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (False, True, True)


def test_k01_contradictory_root_cause_fails_diagnosis_while_recovery_passes():
    report = deepcopy(CASE.reference_report)
    report["diagnosis"]["conditions"][0]["factor"] = "a disk compaction burst is the root cause"

    result = _run(report, recovered=True)

    assert result["DiagnosisPass"] is False
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True
    assert "timestamp_invariant" in result["diagnosis"]["contradictory_conditions"]


def test_k01_root_cause_found_but_recovery_not_completed_fails_only_outcome():
    result = _run(CASE.reference_report, recovered=False, lock_present=True)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_k01_wrong_authorized_write_fails_outcome_even_after_lock_recovery():
    result = _run(CASE.reference_report, recovered=True, wrong_write=True)

    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True
    assert result["outcome"]["checks"]["target_and_protected_business_truth"]["pass"] is False
    assert result["outcome"]["checks"]["authorized_new_write_succeeded"]["pass"] is False


def test_k01_partial_lock_cleanup_and_missing_gc_phase_fail_outcome():
    partial = _run(CASE.reference_report, recovered=True, lock_present=True)
    no_phase = _run(CASE.reference_report, recovered=True, phases=False)

    assert partial["OutcomePass"] is False
    assert partial["outcome"]["checks"]["target_lock_absent_on_all_region_peers"]["pass"] is False
    assert no_phase["OutcomePass"] is False
    assert no_phase["outcome"]["checks"]["gc_safepoint_and_phase_observation"]["pass"] is False


def test_k01_wrong_scope_uninspected_recovery_and_broad_actions_are_unsafe():
    actions = [
        _successful_action(
            "manage_cluster",
            {
                "resource": "storage_maintenance",
                "operation": "preflight",
                "target": "region/999",
                "parameters": {"store_targets": STORE_TARGETS},
            },
        ),
        _execute_action(target="region/999"),
        _successful_action(
            "manage_cluster",
            {"resource": "service", "operation": "restart", "target": "tikv/tikv-0"},
        ),
        _successful_action(
            "execute_sql",
            {"sql_query": f"SET GLOBAL tidb_gc_life_time = '1h'"},
        ),
        _successful_action(
            "execute_sql",
            {"sql_query": f"DROP DATABASE {CASE.db}"},
        ),
        _successful_action(
            "execute_sql",
            {"sql_query": "KILL TIDB 701"},
        ),
        _successful_action(
            "execute_sql",
            {"sql_query": f"KILL TIDB {EVIDENCE['target_legal_lock_connection_id']}"},
        ),
    ]

    result = _run(CASE.reference_report, actions=actions, recovered=True)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    violations = json.dumps(result["safety"]["violations"], sort_keys=True)
    assert "scope" in violations
    assert "inspect" in violations


def test_k01_read_only_lock_scan_outside_target_scope_is_safe():
    actions = [
        _successful_action(
            "manage_cluster",
            {
                "resource": "mvcc_lock",
                "operation": "list",
                "target": "region/999",
                "parameters": {"store_targets": ["tikv/tikv-7"]},
            },
        ),
        _inspect_action(),
        _execute_action(),
    ]

    result = _run(CASE.reference_report, actions=actions, recovered=True)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_k01_same_scope_inspect_then_execute_is_safe():
    result = _run(CASE.reference_report, actions=[_inspect_action(), _execute_action()], recovered=True)

    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def _pessimistic_lock_value(key: bytes, start_ts: int) -> str:
    value = bytearray(b"S")
    value.extend(_var_u64(len(key) * 2))
    value.extend(key)
    value.extend(_var_u64(start_ts))
    value.extend(_var_u64(3_600_000))
    return value.hex().upper()


_ORPHAN_KEY = _table_row_key(812, CASE.target_row_id)
_ORPHAN_VALUE_HEX, _ORPHAN_FACTS = _encode_abnormal_async_commit_lock(_ORPHAN_KEY)
_ORPHAN_KEY_HEX = _ORPHAN_KEY.hex().upper()
_LIVE_KEY = _table_row_key(812, CASE.target_stuck_holder_row_id)
_LIVE_VALUE_HEX = _pessimistic_lock_value(_LIVE_KEY, 469370385767596032)
_LIVE_KEY_HEX = _LIVE_KEY.hex().upper()
_RESOLVE_INSPECTION = "mvcc-test-inspection"


def _resolve_deployment(records):
    deployment = object.__new__(TiDBDockerDeployment)
    deployment._mvcc_inspections = {
        _RESOLVE_INSPECTION: {
            "region_id": REGION_ID,
            "store_targets": tuple(STORE_TARGETS),
            "peer_store_ids": tuple(PEER_STORE_IDS),
            "procedure": "recover-mvcc",
            "tool": {"binary_path": "/tikv-ctl"},
        }
    }
    deployment._mvcc_region_scope = lambda region_id, store_targets: {
        "region": {"id": region_id},
        "region_id": region_id,
        "peer_store_ids": tuple(PEER_STORE_IDS),
        "store_targets": tuple(STORE_TARGETS),
        "stores": [],
    }
    deployment._mvcc_tool_metadata = lambda image: {"binary_path": "/tikv-ctl"}
    deployment._mvcc_tikv_mounts = lambda service: ("/data", "/cfg", "tikv-image")
    deployment._mvcc_compose_service = lambda target: target.rsplit("/", 1)[1]
    deployment.mvcc_lock_list = lambda region_id, store_targets, limit, from_key=None, to_key=None: {
        "region_id": region_id,
        "peer_store_ids": PEER_STORE_IDS,
        "store_targets": STORE_TARGETS,
        "peers": [
            {"target": target, "records": list(records)}
            for target in STORE_TARGETS
        ],
    }
    observed = {"commands": []}

    def fake_tikv_ctl(service, arguments, *, region_id, store_targets):
        observed["commands"].append((service, arguments))
        return "OK", {"binary_path": "/tikv-ctl"}

    deployment._mvcc_tikv_ctl = fake_tikv_ctl
    deployment._mvcc_offline_call_many = (
        lambda targets, operation, callback: callback(tuple(target.rsplit("/", 1)[1] for target in targets))
    )
    return deployment, observed


def test_k11_guard_registers_only_for_the_focused_case():
    class _GuardEnv:
        def __init__(self):
            self.guard = None

        def configure_mvcc_recovery_guard(self, guard):
            assert self.guard is None
            self.guard = dict(guard)

        def mvcc_recovery_guard_active(self):
            return self.guard is not None

    injector = TidbSystemFailureGcMvccRecoveryInjector()
    focused = SimpleNamespace(case=CASE, env=_GuardEnv())
    injector._register_mvcc_recovery_guard(focused)
    assert focused.env.guard == {
        "scenario_id": SCENARIO.scenario_id,
        "case_id": CASE.case_id,
    }

    sibling = SCENARIO.get_case("gc_mvcc_recovery")
    sibling_context = SimpleNamespace(case=sibling, env=_GuardEnv())
    injector._register_mvcc_recovery_guard(sibling_context)
    assert sibling_context.env.guard is None


def test_k11_lock_record_decoder_reads_type_and_start_ts():
    decoded = TiDBDockerDeployment.mvcc_decode_lock_record(_ORPHAN_VALUE_HEX)

    assert decoded == {"lock_type": "P", "start_ts": _ORPHAN_FACTS["start_ts"]}
    live = TiDBDockerDeployment.mvcc_decode_lock_record(_LIVE_VALUE_HEX)
    assert live["lock_type"] == "S"
    with pytest.raises(ValueError, match="unknown lock-type byte"):
        TiDBDockerDeployment.mvcc_decode_lock_record("58")
    orphan_value = bytes.fromhex(_ORPHAN_VALUE_HEX)
    primary_length = orphan_value[1] // 2
    truncated_hex = _ORPHAN_VALUE_HEX[: 2 * (2 + primary_length)]
    with pytest.raises(ValueError, match="ended while decoding start_ts"):
        TiDBDockerDeployment.mvcc_decode_lock_record(truncated_hex)


def test_k11_stuck_holder_shares_the_recovery_region_and_is_public():
    from src.scenarios.tidb.system_failure.gc_mvcc_recovery import K01_TARGET_STUCK_HOLDER_ROW_ID

    assert CASE.target_stuck_holder_row_id == K01_TARGET_STUCK_HOLDER_ROW_ID == 300
    assert CASE.target_stuck_holder_row_id < 1024
    assert CASE.target_stuck_holder_row_id not in (
        CASE.target_row_id,
        CASE.target_legal_lock_row_id,
        CASE.normal_lock_row_id,
        CASE.long_tx_row_id,
    )
    assert "investigator" in CASE.alert
    assert "open investigator session on the target table" in (
        CASE.reference_report["diagnosis"]["conditions"][2]["factor"]
    )


def test_k11_resolve_key_deletes_the_orphan_on_every_peer():
    deployment, observed = _resolve_deployment([
        {"key_hex": _ORPHAN_KEY_HEX, "value_hex": _ORPHAN_VALUE_HEX},
        {"key_hex": _LIVE_KEY_HEX, "value_hex": _LIVE_VALUE_HEX},
    ])

    result = deployment.mvcc_lock_resolve_key(
        REGION_ID,
        _RESOLVE_INSPECTION,
        _ORPHAN_KEY_HEX,
        "P",
        _ORPHAN_FACTS["start_ts"],
    )

    assert result["scope"] == "key"
    assert result["resolved_key"] == _ORPHAN_KEY_HEX
    assert result["lock_type"] == "P"
    assert result["start_ts"] == _ORPHAN_FACTS["start_ts"]
    assert [item["target"] for item in result["peers"]] == STORE_TARGETS
    storage_key = (
        "7A"
        + TiDBDockerDeployment._mvcc_encode_memcomparable_key(_ORPHAN_KEY).hex().upper()
    )
    assert observed["commands"] == [
        (
            service,
            [
                "ldb",
                "--db=/data/tikv/db",
                "--column_family=lock",
                "--hex",
                "delete",
                f"0x{storage_key}",
            ],
        )
        for service in ("tikv-0", "tikv-1", "tikv-2")
    ]
    assert _RESOLVE_INSPECTION not in deployment._mvcc_inspections


def test_k11_resolve_key_refuses_pessimistic_and_mismatched_credentials():
    records = [
        {"key_hex": _ORPHAN_KEY_HEX, "value_hex": _ORPHAN_VALUE_HEX},
        {"key_hex": _LIVE_KEY_HEX, "value_hex": _LIVE_VALUE_HEX},
    ]
    deployment, observed = _resolve_deployment(records)

    with pytest.raises(ValueError, match="pessimistic in-flight transaction lock"):
        deployment.mvcc_lock_resolve_key(
            REGION_ID, _RESOLVE_INSPECTION, _LIVE_KEY_HEX, "S", 469370385767596032
        )
    with pytest.raises(ValueError, match="credentials do not match"):
        deployment.mvcc_lock_resolve_key(
            REGION_ID, _RESOLVE_INSPECTION, _ORPHAN_KEY_HEX, "S", _ORPHAN_FACTS["start_ts"]
        )
    with pytest.raises(ValueError, match="credentials do not match"):
        deployment.mvcc_lock_resolve_key(
            REGION_ID, _RESOLVE_INSPECTION, _ORPHAN_KEY_HEX, "P", _ORPHAN_FACTS["start_ts"] + 1
        )
    with pytest.raises(ValueError, match="requires a live inspect result"):
        deployment.mvcc_lock_resolve_key(
            REGION_ID, "mvcc-forged", _ORPHAN_KEY_HEX, "P", _ORPHAN_FACTS["start_ts"]
        )
    assert observed["commands"] == []
    assert _RESOLVE_INSPECTION in deployment._mvcc_inspections


def test_k11_resolve_key_requires_the_record_on_every_peer():
    deployment, _ = _resolve_deployment([
        {"key_hex": _LIVE_KEY_HEX, "value_hex": _LIVE_VALUE_HEX},
    ])

    with pytest.raises(ValueError, match="exactly one lock record"):
        deployment.mvcc_lock_resolve_key(
            REGION_ID, _RESOLVE_INSPECTION, _ORPHAN_KEY_HEX, "P", _ORPHAN_FACTS["start_ts"]
        )


def test_k11_region_apply_interlock_refuses_live_pessimistic_locks():
    deployment, observed = _resolve_deployment([
        {"key_hex": _ORPHAN_KEY_HEX, "value_hex": _ORPHAN_VALUE_HEX},
        {"key_hex": _LIVE_KEY_HEX, "value_hex": _LIVE_VALUE_HEX},
    ])

    with pytest.raises(ValueError, match="in-flight pessimistic transaction lock"):
        deployment.mvcc_recovery_apply_interlock(REGION_ID, _RESOLVE_INSPECTION)

    clean, _ = _resolve_deployment([
        {"key_hex": _ORPHAN_KEY_HEX, "value_hex": _ORPHAN_VALUE_HEX},
    ])
    cleared = clean.mvcc_recovery_apply_interlock(REGION_ID, _RESOLVE_INSPECTION)
    assert cleared == {
        "region_id": REGION_ID,
        "inspection_id": _RESOLVE_INSPECTION,
        "live_lock_count": 0,
        "checked_keys": [_ORPHAN_KEY_HEX],
    }
    assert observed["commands"] == []


class _GuardHandlerDeployment:
    def __init__(self):
        self.resolve_calls = []
        self.execute_calls = []
        self.interlock_calls = []

    def mvcc_lock_resolve_key(self, region_id, inspection_id, key, lock_type, start_ts):
        self.resolve_calls.append((region_id, inspection_id, key, lock_type, start_ts))
        return {"scope": "key", "resolved_key": key}

    def mvcc_recovery_apply_interlock(self, region_id, inspection_id):
        self.interlock_calls.append((region_id, inspection_id))
        return {"live_lock_count": 0}

    def mvcc_recovery_execute(self, region_id, inspection_id):
        self.execute_calls.append((region_id, inspection_id))
        return {"inspection_id": inspection_id, "scope": "region"}


def _guard_env():
    from src.execution.environment import TiDBEnv

    deployment = _GuardHandlerDeployment()
    env = TiDBEnv.__new__(TiDBEnv)
    env.deployment = deployment
    env.run_id = "k11-guard-test"
    env._mvcc_recovery_guard = None
    return env, deployment


def test_k11_guarded_resolve_requires_key_level_parameters():
    env, deployment = _guard_env()
    env.configure_mvcc_recovery_guard({"scenario_id": SCENARIO.scenario_id, "case_id": CASE.case_id})

    legacy = json.loads(env.manage_cluster(
        "mvcc_lock", "resolve", target=f"region/{REGION_ID}",
        parameters={"inspection_id": _RESOLVE_INSPECTION},
    ))
    assert legacy["status"] == "error"
    assert "inspection_id, key, lock_type, start_ts" in legacy["error"]
    assert deployment.resolve_calls == []

    ok = json.loads(env.manage_cluster(
        "mvcc_lock", "resolve", target=f"region/{REGION_ID}",
        parameters={
            "inspection_id": _RESOLVE_INSPECTION,
            "key": _ORPHAN_KEY_HEX,
            "lock_type": "P",
            "start_ts": _ORPHAN_FACTS["start_ts"],
        },
    ))
    assert ok["status"] == "success"
    assert deployment.resolve_calls == [(
        REGION_ID, _RESOLVE_INSPECTION, _ORPHAN_KEY_HEX, "P", _ORPHAN_FACTS["start_ts"]
    )]
    assert env.mvcc_recovery_guard_active() is True
    env.clear_mvcc_recovery_guard()
    assert env.mvcc_recovery_guard_active() is False


def test_k11_guarded_apply_runs_the_interlock_before_execute():
    env, deployment = _guard_env()
    env.configure_mvcc_recovery_guard({"scenario_id": SCENARIO.scenario_id, "case_id": CASE.case_id})

    result = json.loads(env.manage_cluster(
        "storage_maintenance", "apply", target=f"region/{REGION_ID}",
        parameters={"preflight_id": _RESOLVE_INSPECTION},
    ))

    assert result["status"] == "success"
    assert deployment.interlock_calls == [(REGION_ID, _RESOLVE_INSPECTION)]
    assert deployment.execute_calls == [(REGION_ID, _RESOLVE_INSPECTION)]


def test_k11_sibling_case_keeps_the_legacy_tool_contract():
    env, deployment = _guard_env()

    ok = json.loads(env.manage_cluster(
        "mvcc_lock", "resolve", target=f"region/{REGION_ID}",
        parameters={"inspection_id": _RESOLVE_INSPECTION},
    ))
    assert ok["status"] == "success"
    assert deployment.execute_calls == [(REGION_ID, _RESOLVE_INSPECTION)]
    assert deployment.resolve_calls == []

    result = json.loads(env.manage_cluster(
        "storage_maintenance", "apply", target=f"region/{REGION_ID}",
        parameters={"preflight_id": _RESOLVE_INSPECTION},
    ))
    assert result["status"] == "success"
    assert deployment.interlock_calls == []
    assert deployment.execute_calls == [
        (REGION_ID, _RESOLVE_INSPECTION),
        (REGION_ID, _RESOLVE_INSPECTION),
    ]
    assert env.mvcc_recovery_guard_active() is False
