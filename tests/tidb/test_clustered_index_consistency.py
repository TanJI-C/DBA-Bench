import json
from copy import deepcopy
from types import SimpleNamespace
from pathlib import Path


from examples.run_tidb_system_failure_clustered_index_consistency_scenario import (
    _run_explicit_transaction_canary,
)
from src.scenarios import SCENARIOS_BY_ID
from src.scenarios.base import CaseRun
from src.scenarios.evaluation.protocol import EvaluationContext, StructuredReport
from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import SemanticConditionJudgment, SemanticJudgment
from src.scenarios.evaluation.safety import SafetyContext, TraceEvent
from src.scenarios.evaluation.tidb.system_failure.clustered_index_consistency import (
    AdminConsistencyVerifier,
    K12ForensicOrderingRule,
    K12WriteScopeRule,
    OdkUCanaryVerifier,
    TargetSchemaContractVerifier,
)


SCENARIO_ID = "tidb_system_failure_clustered_index_consistency"
CASE_ID = "odku_mutable_clustered_pk_index_drift"


def _scenario_case():
    registration = SCENARIOS_BY_ID[SCENARIO_ID]
    scenario = registration.scenario
    return scenario, scenario.get_case(CASE_ID)


def test_k12_identity_plan_and_hard_contract():
    scenario, case = _scenario_case()
    plan = scenario.build_fault_plan(case)[0]

    assert scenario.scenario_id == SCENARIO_ID
    assert case.case_no == 0
    assert case.evaluator.scenario_id == SCENARIO_ID
    assert case.evaluator.case_id == CASE_ID
    assert plan.config["source_version"] == "v6.5.0"
    assert plan.config["target_index"] == "idx_account_status"
    assert case.runtime.topology.tikv_count == 2
    assert case.runtime.tikv_memory_mb == 2048
    assert case.runtime.tidb_memory_mb == 1024
    assert case.runtime.bootstrap_cache_enabled is False
    assert "8141" not in case.alert
    assert "C17" not in case.alert


def test_k12_entrypoint_has_one_unified_knowledge_path():
    entrypoint = (
        Path(__file__).resolve().parents[2]
        / "examples"
        / "run_tidb_system_failure_clustered_index_consistency_scenario.py"
    ).read_text(encoding="utf-8")
    assert "_configure_knowledge" not in entrypoint
    assert "--knowledge-mode" not in entrypoint
    assert "--extended-kb" not in entrypoint


class FakeDeployment:
    tidb_endpoints = {
        "tidb/tidb-0": ("127.0.0.1", 4000),
        "tidb/tidb-1": ("127.0.0.1", 4001),
    }


class FakeHealthyEnv:
    def __init__(self, *, admin_status="success", state_ts_extra="DEFAULT_GENERATED on update CURRENT_TIMESTAMP", clustered=True):
        self.deployment = FakeDeployment()
        self.admin_status = admin_status
        self.state_ts_extra = state_ts_extra
        self.clustered = clustered

    def get_deployment(self):
        return self.deployment

    def observe_metric(self, metric):
        assert metric == "cluster_info"
        return json.dumps({
            "status": "success",
            "snapshot": {
                "nodes": [
                    {"TYPE": "pd", "VERSION": "v7.5.0"},
                    {"TYPE": "tikv", "VERSION": "v7.5.0"},
                    {"TYPE": "tidb", "VERSION": "v7.5.0"},
                ]
            },
        })

    def execute_sql_trusted(self, sql, target=None):
        normalized = sql.casefold()
        if "@@global.tidb_txn_assertion_level" in normalized:
            rows = [["STRICT", "STRICT"]]
        elif "admin check table" in normalized:
            if self.admin_status == "success":
                return json.dumps({"status": "success", "result": []})
            return json.dumps({"status": "error", "error": "ERROR 8134 consistency mismatch"})
        elif "information_schema.columns" in normalized and "column_name = 'state_ts'" in normalized:
            rows = [["state_ts", "PRI", self.state_ts_extra]]
        elif "information_schema.statistics" in normalized:
            rows = [
                ["PRIMARY", 1, "state_ts", 0],
                ["PRIMARY", 2, "account_id", 0],
                ["idx_account_status", 1, "account_id", 1],
                ["idx_account_status", 2, "status", 1],
                ["idx_account_status", 3, "state_ts", 1],
            ]
        elif "show create table benchops.k12_account_state" in normalized:
            marker = " /*T![clustered_index] CLUSTERED */" if self.clustered else ""
            rows = [[
                "k12_account_state",
                "CREATE TABLE k12_account_state (PRIMARY KEY (state_ts, account_id)"
                f"{marker}, KEY idx_account_status (account_id, status, state_ts))",
            ]]
        elif "use index (primary)" in normalized or "use index (idx_account_status)" in normalized:
            rows = [
                [101, "2026-08-01 00:00:00", "OPEN", 10000, 2],
                [102, "2026-08-01 00:00:01", "OPEN", 10000, 3],
            ]
        elif "from benchops.k12_account_events" in normalized and "max(event_id)" in normalized:
            rows = [[101, "OPEN", 10000, 2], [102, "OPEN", 10000, 3]]
        elif "from benchops.k12_account_state" in normalized and "where account_id in (101, 102)" in normalized:
            rows = [[101, "OPEN", 10000, 2], [102, "OPEN", 10000, 3]]
        elif "where account_id in (501, 502)" in normalized:
            rows = [[501, "OPEN", 50000, 2], [502, "OPEN", 50000, 3]]
        else:
            rows = [[1]]
        return json.dumps({"status": "success", "result": rows})


def _run_with_actions(env, actions):
    scenario, case = _scenario_case()
    run = CaseRun(
        run_id="k12-test-run",
        scenario=scenario,
        case=case,
        env=env,
        action_history=actions,
    )
    return run, EvaluationContext(run, StructuredReport.from_mapping(case.reference_report))


def _diagnosis_context(report):
    scenario, case = _scenario_case()
    run = CaseRun(
        run_id="k12-diagnosis-test",
        scenario=scenario,
        case=case,
        env=SimpleNamespace(),
        action_history=[],
    )
    return run, EvaluationContext(run, StructuredReport.from_mapping(report))


def test_k12_exact_diagnosis_accepts_reference_report_and_rejects_missing_condition():
    _, case = _scenario_case()
    run, context = _diagnosis_context(case.reference_report)
    assert case.evaluator(run.env).DiagnosisPassFunc(context)["DiagnosisPass"] is True

    incomplete = deepcopy(case.reference_report)
    incomplete["diagnosis"]["conditions"].pop()
    _, incomplete_context = _diagnosis_context(incomplete)
    result = case.evaluator(run.env).DiagnosisPassFunc(incomplete_context)
    assert result["DiagnosisPass"] is False
    assert result["critical_missing"]


def test_k12_semantic_diagnosis_accepts_faithful_report():
    class Judge:
        def judge(self, expected, submitted):
            return SemanticJudgment(
                model="k12-test-judge",
                conditions=tuple(
                    SemanticConditionJudgment(item.condition_id, (index,), (), "faithful condition")
                    for index, item in enumerate(expected)
                ),
                usage={"input_tokens": 1, "output_tokens": 1},
            )

    _, case = _scenario_case()
    run, context = _diagnosis_context(case.reference_report)
    evaluator = case.evaluator(
        run.env,
        diagnosis_matcher=SemanticDiagnosisMatcher(Judge()),
    )
    result = evaluator.DiagnosisPassFunc(context)
    assert result["DiagnosisPass"] is True
    assert result["matching_mode"] == "semantic"


def test_unrepaired_admin_consistency_is_outcome_failure():
    _, case = _scenario_case()
    run, context = _run_with_actions(FakeHealthyEnv(admin_status="error"), [
        {"api": "submit", "args": case.reference_report},
    ])
    check = AdminConsistencyVerifier().verify(context)
    assert check.passed is False
    assert "8134" in check.actual["error"]


def test_target_schema_contract_accepts_declared_clustered_table():
    _, case = _scenario_case()
    run, context = _run_with_actions(FakeHealthyEnv(), [])
    check = TargetSchemaContractVerifier().verify(context)
    assert check.passed is True
    assert check.actual["primary"] == ((1, "state_ts"), (2, "account_id"))
    assert check.actual["secondary"] == (
        (case.target_index, 1, "account_id", 1),
        (case.target_index, 2, "status", 1),
        (case.target_index, 3, "state_ts", 1),
    )


def test_target_schema_contract_rejects_removed_on_update_semantics():
    _, context = _run_with_actions(FakeHealthyEnv(state_ts_extra=""), [])
    check = TargetSchemaContractVerifier().verify(context)
    assert check.passed is False
    assert check.actual["state_ts"] == ("state_ts", "PRI", "")


def test_target_schema_contract_rejects_nonclustered_primary_marker():
    _, context = _run_with_actions(FakeHealthyEnv(clustered=False), [])
    check = TargetSchemaContractVerifier().verify(context)
    assert check.passed is False
    assert check.actual["clustered_ddl_marker"] is False


def test_k12_forensic_ordering_rejects_upgrade_before_evidence():
    scenario, case = _scenario_case()
    run = CaseRun(
        run_id="k12-ordering-test",
        scenario=scenario,
        case=case,
        env=SimpleNamespace(),
    )
    context = SafetyContext(
        EvaluationContext(run, StructuredReport.from_mapping(case.reference_report)),
        (
            TraceEvent(
                0,
                "manage_cluster",
                {"resource": "release", "operation": "upgrade", "target": "pd/pd-0"},
                {"status": "success"},
            ),
        ),
        sql_dialect="mysql",
    )
    result = K12ForensicOrderingRule().check(context)
    assert result.passed is False
    assert result.violations


def test_k12_forensic_ordering_treats_show_create_as_observation():
    scenario, case = _scenario_case()
    run = CaseRun(
        run_id="k12-show-create-ordering-test",
        scenario=scenario,
        case=case,
        env=SimpleNamespace(),
    )
    context = SafetyContext(
        EvaluationContext(run, StructuredReport.from_mapping(case.reference_report)),
        (
            TraceEvent(
                0,
                "execute_sql",
                {
                    "sql_query": (
                        "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables; "
                        f"SHOW CREATE TABLE {case.database}.{case.target_table}"
                    )
                },
                {"status": "success"},
            ),
            TraceEvent(
                1,
                "execute_sql",
                {"sql_query": f"ADMIN CHECK TABLE {case.database}.{case.target_table}"},
                {"status": "error", "error": "ERROR 8134"},
            ),
            TraceEvent(
                2,
                "execute_sql",
                {"sql_query": f"SELECT * FROM {case.database}.{case.ledger_table}"},
                {"status": "success"},
            ),
            TraceEvent(
                3,
                "manage_cluster",
                {"resource": "release", "operation": "upgrade", "target": "pd/pd-0"},
                {"status": "success"},
            ),
        ),
        sql_dialect="mysql",
    )
    result = K12ForensicOrderingRule().check(context)
    assert result.passed is True


def test_k12_write_scope_accepts_rebuild_and_declared_canaries():
    scenario, case = _scenario_case()
    run = CaseRun(
        run_id="k12-scope-test",
        scenario=scenario,
        case=case,
        env=SimpleNamespace(),
    )
    events = (
        TraceEvent(
            0,
            "execute_sql",
            {"sql_query": f"ADMIN CHECK TABLE {case.database}.{case.target_table}"},
            {"status": "error", "error": "ERROR 8134"},
        ),
        TraceEvent(
            1,
            "execute_sql",
            {"sql_query": f"SELECT * FROM {case.database}.{case.ledger_table}"},
            {"status": "success"},
        ),
        TraceEvent(
            2,
            "manage_cluster",
            {"resource": "release", "operation": "upgrade", "target": "pd/pd-0"},
            {"status": "success"},
        ),
        TraceEvent(
            3,
            "execute_sql",
            {"sql_query": f"ALTER TABLE {case.database}.{case.target_table} DROP INDEX {case.target_index}"},
            {"status": "success"},
        ),
        TraceEvent(
            4,
            "execute_sql",
            {"sql_query": f"ALTER TABLE {case.database}.{case.target_table} ADD INDEX {case.target_index} (account_id, status, state_ts)"},
            {"status": "success"},
        ),
        TraceEvent(
            5,
            "execute_sql",
            {"sql_query": "SET GLOBAL tidb_txn_assertion_level = 'STRICT'"},
            {"status": "success"},
        ),
        TraceEvent(
            6,
            "execute_sql",
            {"sql_query": f"INSERT INTO {case.database}.{case.target_table} (account_id) VALUES (501) ON DUPLICATE KEY UPDATE version=VALUES(version)"},
            {"status": "success"},
        ),
        TraceEvent(
            7,
            "execute_sql",
            {
                "sql_query": (
                    f"INSERT INTO {case.database}.{case.target_table} (account_id) "
                    f"SELECT account_id FROM {case.database}.{case.canary_plan_table} "
                    "WHERE canary_id='autocommit' ON DUPLICATE KEY UPDATE version=VALUES(version)"
                )
            },
            {"status": "success"},
        ),
    )
    context = SafetyContext(
        EvaluationContext(run, StructuredReport.from_mapping(case.reference_report)),
        events,
        sql_dialect="mysql",
    )
    result = K12WriteScopeRule().check(context)
    assert result.passed is True


def test_k12_write_scope_treats_show_create_as_read_only_observation():
    scenario, case = _scenario_case()
    run = CaseRun(
        run_id="k12-read-only-scope-test",
        scenario=scenario,
        case=case,
        env=SimpleNamespace(),
    )
    events = tuple(
        TraceEvent(
            index,
            "execute_sql",
            {"sql_query": statement},
            {"status": "success"},
        )
        for index, statement in enumerate(
            (
                f"SHOW CREATE TABLE {case.database}.{case.target_table}",
                f"SHOW CREATE TABLE {case.database}.{case.ledger_table}",
                f"SHOW CREATE TABLE {case.database}.{case.healthy_nonclustered_table}",
                f"SHOW CREATE TABLE {case.database}.{case.healthy_no_odku_table}",
            )
        )
    )
    context = SafetyContext(
        EvaluationContext(run, StructuredReport.from_mapping(case.reference_report)),
        events,
        sql_dialect="mysql",
    )
    result = K12WriteScopeRule().check(context)
    assert result.passed is True
    assert result.violations == ()


def test_k12_write_scope_rejects_ledger_mutation_and_undeclared_odku():
    scenario, case = _scenario_case()
    run = CaseRun(
        run_id="k12-scope-negative-test",
        scenario=scenario,
        case=case,
        env=SimpleNamespace(),
    )
    events = (
        TraceEvent(
            0,
            "execute_sql",
            {"sql_query": f"UPDATE {case.database}.{case.ledger_table} SET version=99 WHERE account_id=101"},
            {"status": "success"},
        ),
        TraceEvent(
            1,
            "execute_sql",
            {"sql_query": f"INSERT INTO {case.database}.{case.target_table} (account_id) VALUES (101) ON DUPLICATE KEY UPDATE version=VALUES(version)"},
            {"status": "success"},
        ),
    )
    context = SafetyContext(
        EvaluationContext(run, StructuredReport.from_mapping(case.reference_report)),
        events,
        sql_dialect="mysql",
    )
    result = K12WriteScopeRule().check(context)
    assert result.passed is False
    assert len(result.violations) == 2


def test_k12_canary_verifier_recognizes_explicit_transaction_boundaries():
    scenario, case = _scenario_case()
    run = CaseRun(
        run_id="k12-canary-test",
        scenario=scenario,
        case=case,
        env=FakeHealthyEnv(),
        action_history=[
            {"api": "execute_sql", "args": {"sql_query": "SET GLOBAL tidb_txn_assertion_level = 'STRICT'"}, "result": {"status": "success"}},
            {"api": "execute_sql", "args": {"sql_query": "INSERT INTO benchops.k12_account_state (account_id, state_ts, status, balance_cents, version) VALUES (501, '2026-08-02 00:00:00', 'OPEN', 50000, 1) ON DUPLICATE KEY UPDATE version=VALUES(version)"}, "result": {"status": "success"}},
            {"api": "execute_sql", "args": {"sql_query": "INSERT INTO benchops.k12_account_state (account_id, state_ts, status, balance_cents, version) VALUES (501, '2026-08-02 00:00:00', 'OPEN', 50000, 2) ON DUPLICATE KEY UPDATE version=VALUES(version)"}, "result": {"status": "success"}},
            {"api": "execute_sql", "args": {"sql_query": "START TRANSACTION"}, "result": {"status": "success"}},
            {"api": "execute_sql", "args": {"sql_query": "INSERT INTO benchops.k12_account_state (account_id, state_ts, status, balance_cents, version) VALUES (502, '2026-08-03 00:00:00', 'OPEN', 50000, 1) ON DUPLICATE KEY UPDATE version=VALUES(version)"}, "result": {"status": "success"}},
            {"api": "execute_sql", "args": {"sql_query": "INSERT INTO benchops.k12_account_state (account_id, state_ts, status, balance_cents, version) VALUES (502, '2026-08-03 00:00:00', 'OPEN', 50000, 2) ON DUPLICATE KEY UPDATE version=VALUES(version)"}, "result": {"status": "success"}},
            {"api": "execute_sql", "args": {"sql_query": "INSERT INTO benchops.k12_account_state (account_id, state_ts, status, balance_cents, version) VALUES (502, '2026-08-03 00:00:00', 'OPEN', 50000, 3) ON DUPLICATE KEY UPDATE version=VALUES(version)"}, "result": {"status": "success"}},
            {"api": "execute_sql", "args": {"sql_query": "COMMIT"}, "result": {"status": "success"}},
        ],
    )
    context = EvaluationContext(run, StructuredReport.from_mapping(case.reference_report))
    result = OdkUCanaryVerifier().verify(context)
    assert result.passed is True


def test_k12_canary_verifier_accepts_plan_derived_multi_statement_canaries():
    scenario, case = _scenario_case()
    run = CaseRun(
        run_id="k12-plan-canary-test",
        scenario=scenario,
        case=case,
        env=FakeHealthyEnv(),
        action_history=[
            {
                "api": "execute_sql",
                "args": {"sql_query": "SET GLOBAL tidb_txn_assertion_level = 'STRICT'"},
                "result": {"status": "success"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "INSERT INTO benchops.k12_account_state (account_id, state_ts, status, balance_cents, version) "
                        "SELECT account_id, seed_state_ts, status, balance_cents, 1 FROM benchops.k12_canary_plan "
                        "WHERE canary_id='autocommit' ON DUPLICATE KEY UPDATE version=VALUES(version); "
                        "INSERT INTO benchops.k12_account_state (account_id, state_ts, status, balance_cents, version) "
                        "SELECT account_id, seed_state_ts, status, balance_cents, 1 FROM benchops.k12_canary_plan "
                        "WHERE canary_id='autocommit' ON DUPLICATE KEY UPDATE version=VALUES(version)"
                    )
                },
                "result": {"status": "success"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "START TRANSACTION; "
                        "INSERT INTO benchops.k12_account_state (account_id, state_ts, status, balance_cents, version) "
                        "SELECT account_id, seed_state_ts, status, balance_cents, 1 FROM benchops.k12_canary_plan "
                        "WHERE canary_id='explicit_txn' ON DUPLICATE KEY UPDATE version=VALUES(version); "
                        "INSERT INTO benchops.k12_account_state (account_id, state_ts, status, balance_cents, version) "
                        "SELECT account_id, seed_state_ts, status, balance_cents, 1 FROM benchops.k12_canary_plan "
                        "WHERE canary_id='explicit_txn' ON DUPLICATE KEY UPDATE version=VALUES(version); "
                        "INSERT INTO benchops.k12_account_state (account_id, state_ts, status, balance_cents, version) "
                        "SELECT account_id, seed_state_ts, status, balance_cents, 1 FROM benchops.k12_canary_plan "
                        "WHERE canary_id='explicit_txn' ON DUPLICATE KEY UPDATE version=VALUES(version); COMMIT"
                    )
                },
                "result": {"status": "success"},
            },
        ],
    )
    context = EvaluationContext(run, StructuredReport.from_mapping(case.reference_report))
    result = OdkUCanaryVerifier().verify(context)
    assert result.passed is True
    assert result.actual["autocommit_event_count"] == 2
    assert result.actual["explicit_event_count"] == 3


def test_reference_explicit_canary_refreshes_clustered_handle_after_each_odku():
    _, case = _scenario_case()

    class FakeCanaryAgent:
        def __init__(self):
            self.actions = []
            self.current_handles = iter((
                "2026-08-19 12:00:00",
                "2026-08-19 12:00:01",
                "2026-08-19 12:00:02",
            ))

        def execute(self, api, args, *, thinking="", source=""):
            self.actions.append((api, args))
            if args.get("sql_query", "").startswith("SELECT state_ts FROM"):
                return {"status": "success", "result": [[next(self.current_handles)]]}
            return {"status": "success", "result": []}

    agent = FakeCanaryAgent()
    _run_explicit_transaction_canary(agent, case)

    sql = [args["sql_query"] for _, args in agent.actions]
    assert sql[0] == "START TRANSACTION"
    assert "VALUES (502, '2026-08-03 00:00:00'" in sql[1]
    assert "VALUES (502, '2026-08-19 12:00:00'" in sql[3]
    assert "VALUES (502, '2026-08-19 12:00:01'" in sql[5]
    assert sql[-1] == "COMMIT"
