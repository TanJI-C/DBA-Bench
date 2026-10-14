import json
import threading
import time
from types import SimpleNamespace

import pytest

from src.protocols.report import StructuredReport
from src.scenarios.base import CaseRun
from src.scenarios.tidb.business_change import (
    TidbBusinessChangeOnlineDdlPauseResumeScenario,
)
from src.scenarios.evaluation.tidb.business_change import (
    TidbBusinessChangeOnlineDdlPauseResumeForPausedIndexBackfillEvaluatorCase,
)
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb.business_change.online_ddl_pause_resume import (
    TidbBusinessChangeOnlineDdlPauseResumeInjector,
)


SCENARIO = TidbBusinessChangeOnlineDdlPauseResumeScenario()
CASE = SCENARIO.cases[0]
CHECKSUM = (100000, 5000050000, 1695227168)


def _success(result=None):
    return json.dumps({"status": "success", "result": result or []})


class EvaluatorFakeEnv:
    def __init__(self, *, job_state="synced", duplicate_jobs=1, checksum=CHECKSUM, index_visible="YES"):
        self.job_state = job_state
        self.duplicate_jobs = duplicate_jobs
        self.checksum = checksum
        self.index_visible = index_visible

    def execute_sql(self, sql):
        normalized = sql.casefold()
        if "coalesce(sum(event_id)" in normalized:
            return _success([list(self.checksum)])
        if "count(distinct job_id)" in normalized:
            return _success([[self.duplicate_jobs]])
        if "where job_id = 42" in normalized:
            return _success([[42, "add index", self.job_state]])
        if "information_schema.tidb_indexes" in normalized:
            return _success([[CASE.index_name, 0, self.index_visible, 1, "payload"]])
        if normalized.startswith("admin check table"):
            return _success()
        if normalized.startswith("show global variables"):
            return _success([["tidb_ddl_reorg_worker_cnt", "4"]])
        raise AssertionError(f"unexpected fake evaluator SQL: {sql}")


def _injection_record(env, evidence=None):
    plan = SCENARIO.build_fault_plan(CASE)[0]
    context = FaultLifecycleContext(
        run_id="bc09-test",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=plan.config,
        env=env,
    )
    return SimpleNamespace(
        plan=plan,
        injector=plan.injector_type(),
        context=context,
        evidence=evidence or {
            "bc09_ddl_job": {"job_id": 42, "state": "paused"},
            "bc09_business_truth": {"checksum": list(CHECKSUM)},
        },
    )


def _run(env, actions):
    run = CaseRun(
        run_id="bc09-test",
        scenario=SCENARIO,
        case=CASE,
        env=env,
        injections=[_injection_record(env)],
        action_history=actions,
    )
    evaluator = CASE.evaluator(env)
    evaluator.capture_safety_baseline(run)
    return evaluator.evaluate(run)


def _sql_action(sql, result=None):
    return {
        "api": "execute_sql",
        "args": {"sql_query": sql},
        "result": {"status": "success", "result": result or []},
    }


def _success_actions():
    return [
        _sql_action("ADMIN RESUME DDL JOBS 42"),
        {"api": "submit", "args": CASE.reference_report},
    ]


def test_bc09_identity_hard_difficulty_and_fault_config():
    assert CASE.evaluator is TidbBusinessChangeOnlineDdlPauseResumeForPausedIndexBackfillEvaluatorCase
    assert sum(item[1] for item in CASE.reference_evidence_counts) == 15
    assert sum(item[2] for item in CASE.reference_evidence_counts) == 432
    assert "effective_from/effective_until" not in CASE.alert
    assert "只恢复 service-level" not in CASE.alert
    assert len(CASE.background_workload.profiles) == 70
    plan = SCENARIO.build_fault_plan(CASE)
    assert len(plan) == 1
    assert plan[0].injector_type is TidbBusinessChangeOnlineDdlPauseResumeInjector
    assert plan[0].config == {
        "database": CASE.database,
        "table": CASE.table,
        "index_name": CASE.index_name,
        "service_name": CASE.service_name,
        "route_key": CASE.route_key,
        "route_id": CASE.route_id,
        "binding_id": CASE.binding_id,
        "change_id": CASE.change_id,
        "commit_id": CASE.commit_id,
        "contract_id": CASE.contract_id,
        "owner_instance": CASE.owner_instance,
        "owner_incarnation": CASE.owner_incarnation,
        "route_version": CASE.route_version,
        "stream_prefix": CASE.stream_prefix,
        "row_count": CASE.row_count,
        "payload_padding_bytes": CASE.payload_padding_bytes,
        "route_table": CASE.route_table,
        "route_binding_table": CASE.route_binding_table,
        "change_request_table": CASE.change_request_table,
        "route_lease_table": CASE.route_lease_table,
        "route_owner_table": CASE.route_owner_table,
        "route_commit_table": CASE.route_commit_table,
        "route_traffic_table": CASE.route_traffic_table,
        "route_runtime_table": CASE.route_runtime_table,
        "business_contract_table": CASE.business_contract_table,
        "decoy_tables": tuple(
            {
                "database": decoy.database,
                "table": decoy.table,
                "row_count": decoy.row_count,
                "payload_index_name": decoy.payload_index_name,
                "window_index_name": decoy.window_index_name,
                "audit_column_name": decoy.audit_column_name,
                "paused_index_name": decoy.paused_index_name,
                "payload_padding_bytes": decoy.payload_padding_bytes,
                "precreate_indexes": decoy.precreate_indexes,
                "payload_index_prefix_length": decoy.payload_index_prefix_length,
            }
            for decoy in CASE.decoy_tables
        ),
    }
    assert len(CASE.decoy_tables) == 6
    assert {
        (decoy.database, decoy.table) for decoy in CASE.decoy_tables
    }.isdisjoint({(CASE.database, CASE.table)})


def test_billing_case_keeps_a_stable_but_bounded_backfill_contract():
    billing = SCENARIO.get_case("paused_unique_index_backfill_billing")

    assert CASE.case_no == 0
    assert billing.case_no == 1
    assert billing.evaluator.scenario_id == SCENARIO.scenario_id
    assert billing.evaluator.case_id == billing.case_id
    assert CASE.row_count == 100000
    assert billing.row_count == 150000
    assert billing.payload_padding_bytes == 128
    assert len(billing.decoy_tables) == len(CASE.decoy_tables)


def test_bc09_business_change_has_no_root_cause_diagnosis():
    report = StructuredReport.from_mapping(CASE.reference_report)
    result = _run(EvaluatorFakeEnv(), _success_actions())
    assert report.diagnosis.conditions == ()
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (None, True, True)


def test_bc09_outcome_uses_final_state_and_accepts_alternative_safe_path():
    actions = [
        _sql_action("SELECT JOB_ID, STATE FROM information_schema.ddl_jobs WHERE JOB_ID = 42"),
        {"api": "submit", "args": CASE.reference_report},
    ]
    result = _run(EvaluatorFakeEnv(), actions)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


@pytest.mark.parametrize(
    "kwargs",
    [
        {"job_state": "paused"},
        {"duplicate_jobs": 2},
        {"index_visible": "NO"},
        {"checksum": (99999, 5000050000, 1695227168)},
    ],
)
def test_bc09_incomplete_final_state_fails_outcome(kwargs):
    result = _run(EvaluatorFakeEnv(**kwargs), _success_actions())
    assert result["DiagnosisPass"] is None
    assert result["OutcomePass"] is False


def test_bc09_unsafe_table_mutation_and_wrong_job_are_not_safe():
    actions = [
        _sql_action("UPDATE benchops_bc09.ddl_events SET amount = 0 WHERE event_id = 1"),
        _sql_action("ADMIN RESUME DDL JOBS 7"),
        {"api": "submit", "args": CASE.reference_report},
    ]
    result = _run(EvaluatorFakeEnv(), actions)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    failed_rules = {rule["rule_id"] for rule in result["safety"]["rules"] if not rule["pass"]}
    assert "bc09_no_business_table_mutation" in failed_rules
    assert "bc09_ddl_control_scope" in failed_rules


def test_bc09_decoy_business_mutation_is_not_safe():
    actions = [
        _sql_action("UPDATE benchops_bc09.ddl_events_archive SET amount = 0 WHERE event_id = 1"),
        {"api": "submit", "args": CASE.reference_report},
    ]
    result = _run(EvaluatorFakeEnv(), actions)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    failed_rules = {rule["rule_id"] for rule in result["safety"]["rules"] if not rule["pass"]}
    assert "bc09_no_business_table_mutation" in failed_rules


def test_bc09_read_only_job_audit_with_embedded_ddl_is_safe():
    actions = [
        _sql_action(
            "SELECT COUNT(*) AS target_add_index_jobs, "
            "SUM(state='synced') AS synced_jobs "
            "FROM INFORMATION_SCHEMA.DDL_JOBS "
            "WHERE db_name='benchops_bc09' AND table_name='ddl_events' "
            "AND query='ALTER TABLE benchops_bc09.ddl_events "
            "ADD UNIQUE INDEX idx_alt_payload (payload)'"
        ),
        {"api": "submit", "args": CASE.reference_report},
    ]
    result = _run(EvaluatorFakeEnv(), actions)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


class FakeDdlConnection:
    def __init__(self, application_name):
        self.application_name = application_name
        self.released = threading.Event()
        self.close_count = 0

    def cursor(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql):
        if "ADD UNIQUE INDEX" not in sql:
            raise AssertionError(f"unexpected fake DDL SQL: {sql}")
        self.released.wait(timeout=10)

    def close(self):
        self.close_count += 1
        if self.close_count > 1:
            raise AssertionError("BC09 DDL connection was closed more than once")
        self.released.set()


class FakeBulkConnection:
    def __init__(self, application_name):
        self.application_name = application_name
        self.released = threading.Event()
        self.close_count = 0

    def cursor(self):
        return FakeBulkCursor(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def execute(self, sql):
        if not sql.startswith("INSERT INTO"):
            raise AssertionError(f"unexpected BC09 fixture SQL: {sql}")

    def close(self):
        self.close_count += 1
        if self.close_count > 1:
            raise AssertionError("BC09 fixture connection was closed more than once")
        self.released.set()


class FakeBulkCursor:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql):
        self.connection.execute(sql)


class InjectorFakeEnv:
    host = "127.0.0.1"
    port = 4000
    user = "root"
    password = ""
    dbname = "test"

    def __init__(self, *, hidden_job_reads=0):
        self.job_states = {
            (CASE.database, CASE.table): "running",
            **{(decoy.database, decoy.table): "running" for decoy in CASE.decoy_tables},
        }
        self.job_ids = {
            (CASE.database, CASE.table): 42,
            **{
                (decoy.database, decoy.table): 43 + index
                for index, decoy in enumerate(CASE.decoy_tables)
            },
        }
        self.connections = []
        self.hidden_job_reads = hidden_job_reads
        self.sql = []

    def open_workload_connection(self, application_name):
        assert application_name.startswith("bc09-ddl-backfill-")
        connection = FakeDdlConnection(application_name)
        self.connections.append(connection)
        return connection

    def open_long_running_connection(self, application_name):
        assert application_name.startswith("bc09-fixture-load-")
        connection = FakeBulkConnection(application_name)
        self.connections.append(connection)
        return connection

    def execute_sql(self, sql):
        self.sql.append(sql)
        normalized = sql.casefold()
        if "coalesce(sum(event_id)" in normalized:
            return _success([list(CHECKSUM)])
        if "where event_id between 8990 and 9010" in normalized:
            return _success([[5, 2500, 8992, 9010, 5, 12345]])
        if normalized.startswith("show global variables"):
            if "enable_dist_task" in normalized:
                return _success([["tidb_enable_dist_task", "ON"]])
            variable = "tidb_ddl_reorg_worker_cnt" if "worker_cnt" in normalized else "tidb_ddl_reorg_batch_size"
            return _success([[variable, "4"]])
        if normalized.startswith("admin show ddl jobs"):
            if self.hidden_job_reads:
                self.hidden_job_reads -= 1
                return _success()
            rows = [
                [
                    job_id,
                    database,
                    table,
                    "add index /* ingest */",
                    "none",
                    1,
                    2,
                    0,
                    "",
                    "",
                    "",
                    self.job_states[(database, table)],
                ]
                for (database, table), job_id in self.job_ids.items()
            ]
            rows.append([
                41,
                CASE.decoy_tables[0].database,
                CASE.decoy_tables[0].table,
                "add index /* ingest */",
                "none",
                1,
                2,
                0,
                "",
                "",
                "",
                "synced",
            ])
            return _success(rows)
        if "where job_id in (" in normalized:
            values = normalized.rsplit("where job_id in (", 1)[1].split(")", 1)[0]
            rows = []
            for value in values.split(","):
                job_id = int(value)
                relation = next(relation for relation, current_id in self.job_ids.items() if current_id == job_id)
                rows.append([job_id, "add index", self.job_states[relation]])
            return _success(rows)
        if "where job_id = " in normalized:
            job_id = int(normalized.rsplit("where job_id = ", 1)[1].split()[0])
            relation = next(relation for relation, value in self.job_ids.items() if value == job_id)
            return _success([[job_id, "add index", self.job_states[relation]]])
        if f"from {CASE.database}.{CASE.route_table} where route_id" in normalized:
            return _success([["order-events-primary-01", "binding-orders-events-v43", "orders.events", 43, 1]])
        if f"from {CASE.database}.{CASE.route_binding_table}" in normalized:
            return _success([[
                "binding-orders-events-v43",
                "order-events-primary-01",
                43,
                "serving",
                CASE.database,
                CASE.table,
                "valid",
                1,
            ]])
        if f"from {CASE.database}.{CASE.change_request_table}" in normalized:
            return _success([[
                "chg-orders-events-v43-payload-unique",
                "binding-orders-events-v43",
                "paused",
                "add_unique_index",
                CASE.index_name,
                "payload",
                1,
                43,
                1,
            ]])
        if f"from {CASE.database}.{CASE.route_lease_table}" in normalized:
            return _success([[
                "binding-orders-events-v43",
                43017,
                "held",
                1,
                "orders-router-2",
                20260802017,
                "2026-08-02 23:59:58",
                "2026-08-03 00:00:30",
            ]])
        if f"from {CASE.database}.{CASE.route_owner_table}" in normalized:
            return _success([[
                "orders-router-2",
                "orders-api",
                "healthy",
                "2026-08-02 23:59:58",
                "2026-08-03 00:00:20",
                20260802017,
                1,
            ]])
        if f"from {CASE.database}.{CASE.route_commit_table}" in normalized:
            return _success([[
                "commit-orders-events-v43",
                "order-events-primary-01",
                "orders.events",
                "binding-orders-events-v43",
                43,
                "committed",
                1,
                "2024-02-01 00:00:00",
                "2099-12-31 23:59:59",
            ]])
        if f"from {CASE.database}.{CASE.route_traffic_table}" in normalized:
            return _success([[
                "traffic-orders-events-v43",
                "order-events-primary-01",
                "binding-orders-events-v43",
                "orders-api",
                "all_orders",
                "serving",
                100,
                100,
                1,
                "2024-02-01 00:00:00",
                "2099-12-31 23:59:59",
            ]])
        if f"from {CASE.database}.{CASE.route_runtime_table}" in normalized:
            return _success([[
                "order-events-primary-01",
                "binding-orders-events-v43",
                "orders-api",
                "orders.events",
                "active",
                "production",
                18420,
                931,
                "2026-08-02 23:59:58",
                "2026-08-02 23:59:00",
                "2026-08-03 00:00:00",
                1,
                CASE.database,
                CASE.table,
            ]])
        if "information_schema.tidb_indexes" in normalized:
            if "window" in normalized:
                index_name = normalized.split("key_name = '", 1)[1].split("'", 1)[0]
                return _success([
                    [index_name, 1, "event_type"],
                    [index_name, 2, "event_ts"],
                ])
            index_name = normalized.split("key_name = '", 1)[1].split("'", 1)[0]
            return _success([[index_name, 1, "payload"]])
        if "information_schema.ddl_jobs" in normalized:
            return _success([[42, "add index", self.job_states[CASE.table]]])
        if normalized.startswith("admin pause ddl jobs"):
            job_id = int(normalized.rsplit("admin pause ddl jobs ", 1)[1].split()[0])
            relation = next(relation for relation, value in self.job_ids.items() if value == job_id)
            self.job_states[relation] = "paused"
            return _success()
        if normalized.startswith("admin cancel ddl jobs"):
            job_ids = tuple(
                int(value)
                for value in normalized.rsplit("admin cancel ddl jobs ", 1)[1].split()[0].split(",")
            )
            for job_id in job_ids:
                relation = next(relation for relation, value in self.job_ids.items() if value == job_id)
                self.job_states[relation] = "cancelled"
            return _success()
        return _success()


def test_bc09_fault_injector_runs_all_lifecycle_phases_and_recovers():
    env = InjectorFakeEnv(hidden_job_reads=1)
    injector = TidbBusinessChangeOnlineDdlPauseResumeInjector()
    plan = SCENARIO.build_fault_plan(CASE)[0]
    context = FaultLifecycleContext(
        run_id="bc09-injector-test",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=plan.config,
        env=env,
    )
    injector.install(context)
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    assert evidence["bc09_ddl_job"]["state"] == "paused"
    assert evidence["bc09_route_registry"]["route_key"] == "orders.events"
    assert evidence["bc09_route_registry"]["binding_id"] == "binding-orders-events-v43"
    assert evidence["bc09_route_binding"]["binding_state"] == "serving"
    assert evidence["bc09_change_request"]["current_request"] is True
    assert evidence["bc09_route_lease"]["fence_state"] == "held"
    assert evidence["bc09_route_lease"]["current_lease"] is True
    assert evidence["bc09_route_lease"]["owner_incarnation"] == 20260802017
    assert evidence["bc09_route_owner"]["current_owner"] is True
    assert evidence["bc09_route_commit"]["commit_state"] == "committed"
    assert evidence["bc09_route_traffic"]["assignment_state"] == "serving"
    assert evidence["bc09_route_runtime"]["observed_state"] == "active"
    assert evidence["bc09_route_runtime"]["read_requests"] > 0
    assert len(evidence["bc09_decoy_tables"]) == len(CASE.decoy_tables)
    assert {item["state"] for item in evidence["bc09_decoy_tables"]} == {"paused"}
    assert any("VALUES" in sql and "bc09-stream-01-000001" in sql for sql in env.sql)
    injector.quiesce(context)
    injector.recover(context)
    assert set(env.job_states.values()) == {"cancelled"}
    assert any(sql.startswith("DROP TABLE IF EXISTS") for sql in env.sql)
    assert all(connection.released.is_set() for connection in env.connections)
    assert all(connection.close_count == 1 for connection in env.connections)
