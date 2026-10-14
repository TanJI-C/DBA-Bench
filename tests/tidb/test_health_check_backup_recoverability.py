import hashlib
import inspect
import json
import runpy

import pytest

from src.scenarios import TIDB_SCENARIO_REGISTRY
from src.scenarios.base import CaseRun, FaultLifecycleContext
from src.scenarios.evaluation.tidb.health_check.backup_recoverability import (
    TidbHealthCheckBackupRecoverabilityForBackupChainRepairEvaluatorCase,
    _archive_state_sql,
    _business_truth_sql,
    _restore_attempt_sql,
    _restore_checks_sql,
)
from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import (
    SemanticConditionJudgment,
    SemanticJudgment,
)
from src.scenarios.tidb.health_check.runtime.backup_recoverability import BackupRecoverabilityEnv
from src.scenarios.tidb.health_check.backup_recoverability import (
    TidbHealthCheckBackupRecoverabilityInjector,
)


def _scenario():
    return next(
        registration.scenario
        for registration in TIDB_SCENARIO_REGISTRY
        if registration.scenario_id == "tidb_health_check_backup_recoverability"
    )


def _report(text="complete", *, diagnosis=True):
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "archive_integrity_failure",
                    "factor": (
                        "the requested checkpoint cannot be reached because the active primary copies of log "
                        "segments A3, A4, A5, A7, and A8 are corrupted while their authorized replicas remain usable"
                    ),
                    "entity": "backup_chain_repair_and_restore",
                    "evidence": ["archive checksum and replica state"],
                },
                {
                    "type": "archive_availability_gap",
                    "factor": (
                        "segment A6 is absent from the replicated archive chain even though its bytes are "
                        "readable and an authorized copy exists, so restore continuity remains broken"
                    ),
                    "entity": "backup_chain_repair_and_restore",
                    "evidence": ["archive continuity and replication state"],
                },
            ]
            if diagnosis
            else [],
        },
        "outcome": {"changes": [text], "verification": [text]},
        "summary": text,
    }


class FakeRecoverabilityEnv:
    def __init__(
        self,
        case,
        *,
        front_archive_repaired=True,
        early_archive_repaired=True,
        late_archive_repaired=True,
        archive_repaired=True,
        secondary_archive_repaired=True,
        continuity_archive_repaired=True,
        restore_status="success",
        production_valid=True,
    ):
        self.case = case
        self.front_archive_repaired = front_archive_repaired
        self.early_archive_repaired = early_archive_repaired
        self.late_archive_repaired = late_archive_repaired
        self.archive_repaired = archive_repaired
        self.secondary_archive_repaired = secondary_archive_repaired
        self.continuity_archive_repaired = continuity_archive_repaired
        self.restore_status = restore_status
        self.production_valid = production_valid

    def execute_sql(self, sql):
        normalized = " ".join(sql.casefold().split())
        if normalized == " ".join(_archive_state_sql(self.case).casefold().split()):
            rows = (
                [
                [
                    self.case.front_segment,
                    1 if self.front_archive_repaired else 0,
                    "OK" if self.front_archive_repaired else "CORRUPT",
                    "READABLE" if self.front_archive_repaired else "READABLE_BUT_INVALID",
                    19,
                    "AVAILABLE" if self.front_archive_repaired else "CORRUPT",
                    1,
                    1 if self.front_archive_repaired else 0,
                ],
                [
                    self.case.early_segment,
                    1 if self.early_archive_repaired else 0,
                    "OK" if self.early_archive_repaired else "CORRUPT",
                    "READABLE" if self.early_archive_repaired else "READABLE_BUT_INVALID",
                    13,
                    "AVAILABLE" if self.early_archive_repaired else "CORRUPT",
                    1,
                    1 if self.early_archive_repaired else 0,
                ],
                [
                    self.case.late_segment,
                    1 if self.late_archive_repaired else 0,
                    "OK" if self.late_archive_repaired else "CORRUPT",
                    "READABLE" if self.late_archive_repaired else "READABLE_BUT_INVALID",
                    15,
                    "AVAILABLE" if self.late_archive_repaired else "CORRUPT",
                    1,
                    1 if self.late_archive_repaired else 0,
                ],
                [
                    self.case.continuity_segment,
                    1 if self.continuity_archive_repaired else 0,
                    "OK",
                    "READABLE",
                    9,
                    "AVAILABLE",
                    1,
                    1 if self.continuity_archive_repaired else 0,
                ],
                [
                    self.case.missing_segment,
                        1 if self.archive_repaired else 0,
                        "OK" if self.archive_repaired else "CORRUPT",
                        "READABLE" if self.archive_repaired else "READABLE_BUT_INVALID",
                        1,
                        "AVAILABLE" if self.archive_repaired else "CORRUPT",
                        1,
                        1 if self.archive_repaired else 0,
                    ],
                [
                    self.case.secondary_segment,
                        1 if self.secondary_archive_repaired else 0,
                        "OK" if self.secondary_archive_repaired else "CORRUPT",
                        "READABLE" if self.secondary_archive_repaired else "READABLE_BUT_INVALID",
                        5,
                        "AVAILABLE" if self.secondary_archive_repaired else "CORRUPT",
                        1,
                        1 if self.secondary_archive_repaired else 0,
                ],
                ]
            )
        elif normalized == " ".join(_restore_attempt_sql(self.case).casefold().split()):
            rows = (
                [[
                    f"{self.case.selected_drill_id}-attempt-002",
                    "SUCCESS",
                    1,
                    "COMPLETE",
                    "MATCH",
                    "NONE",
                ]]
                if self.restore_status == "success"
                else [[
                    f"{self.case.selected_drill_id}-attempt-001",
                    self.restore_status.upper(),
                    1,
                    "GAP",
                    "NOT_VERIFIED",
                    "CHECKPOINT_NOT_REACHED",
                ]]
            )
        elif normalized == " ".join(_restore_checks_sql(self.case).casefold().split()):
            rows = (
                [
                    [self.case.inventory_table, self.case.source_inventory, self.case.source_inventory, 2428920, 2428920, "MATCH"],
                    [self.case.order_lines_table, self.case.source_order_lines, self.case.source_order_lines, 6481800, 6481800, "MATCH"],
                    [self.case.orders_table, self.case.source_orders, self.case.source_orders, 1620900, 1620900, "MATCH"],
                    [self.case.payments_table, self.case.source_payments, self.case.source_payments, 1620900, 1620900, "MATCH"],
                ]
                if self.restore_status == "success"
                else []
            )
        elif normalized == " ".join(_business_truth_sql(self.case).casefold().split()):
            rows = [
                [self.case.inventory_table, self.case.source_inventory, 2428920],
                [self.case.order_lines_table, self.case.source_order_lines, 6481800],
                [self.case.orders_table, self.case.source_orders, 1620900],
                [self.case.payments_table, self.case.source_payments, 1620900],
            ]
            if not self.production_valid:
                rows[2][1] -= 1
        elif "restore_sandbox_orders" in normalized:
            rows = [[self.case.source_orders, 1620900]] if self.restore_status == "success" else [[0, 0]]
        elif "restore_sandbox_order_lines" in normalized:
            rows = [[self.case.source_order_lines, 6481800]] if self.restore_status == "success" else [[0, 0]]
        elif "restore_sandbox_payments" in normalized:
            rows = [[self.case.source_payments, 1620900]] if self.restore_status == "success" else [[0, 0]]
        elif "restore_sandbox_inventory" in normalized:
            rows = [[self.case.source_inventory, 2428920]] if self.restore_status == "success" else [[0, 0]]
        else:
            raise AssertionError(f"unexpected evaluator SQL: {sql}")
        return json.dumps({"status": "success", "result": rows})


def _case_run(case, env, actions):
    return CaseRun(
        run_id="hc04-test-run",
        scenario=_scenario(),
        case=case,
        env=env,
        action_history=actions,
    )


def _actions(report, *, unsafe=False):
    actions = []
    if unsafe:
        actions.append({
            "api": "execute_sql",
            "args": {"sql_query": "UPDATE benchops.hc04_orders SET status = 'lost' WHERE order_id = 1"},
            "result": {"status": "success", "result": []},
        })
    actions.append({"api": "submit", "args": report})
    return actions


def _evaluate(env, report=None, *, unsafe=False):
    return env.case.evaluator(env).evaluate(
        _case_run(env.case, env, _actions(report or _report(), unsafe=unsafe))
    )


def test_hc04_identity_difficulty_fault_plan_and_lifecycle_contract():
    scenario = _scenario()
    case = scenario.get_case("backup_chain_repair_and_restore")
    assert case.evaluator is TidbHealthCheckBackupRecoverabilityForBackupChainRepairEvaluatorCase
    assert "checksum-invalid" not in case.alert
    assert "continuity gap" not in case.alert
    assert "comparison evidence only" not in case.alert
    assert "archive_chain" not in case.initial_state
    for phase in ("install", "activate", "prepare_observability", "quiesce", "recover"):
        assert list(inspect.signature(getattr(TidbHealthCheckBackupRecoverabilityInjector, phase)).parameters) == ["self", "context"]
    plan = scenario.build_fault_plan(case)[0]
    assert plan.config["selected_backup_id"] == case.selected_backup_id
    assert plan.config["rpo_target_seconds"] == case.rpo_target_seconds
    assert plan.config["rto_target_seconds"] == case.rto_target_seconds


def test_hc04_full_repair_passes_all_three_flags():
    result = _evaluate(FakeRecoverabilityEnv(_scenario().cases[0]))
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)
    assert set(result["outcome"]["checks"]) == {
        "hc04_archive_fault_repaired",
        "hc04_isolated_restore_succeeded",
        "hc04_critical_restore_checks_match",
        "hc04_sandbox_orders_match",
        "hc04_sandbox_order_lines_match",
        "hc04_sandbox_payments_match",
        "hc04_sandbox_inventory_match",
        "hc04_production_business_truth_unchanged",
    }


def test_hc04_agent_that_does_not_find_the_archive_fault_fails_diagnosis():
    result = _evaluate(
        FakeRecoverabilityEnv(
            _scenario().cases[0],
            archive_repaired=False,
            secondary_archive_repaired=False,
            continuity_archive_repaired=False,
            restore_status="not_run",
        ),
        _report("no finding", diagnosis=False),
    )
    assert result["DiagnosisPass"] is False
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_hc04_semantic_dp_accepts_a_faithful_paraphrase():
    class FakeJudge:
        model = "fake-semantic"

        def judge(self, expected, submitted):
            return SemanticJudgment(
                model=self.model,
                conditions=(
                    SemanticConditionJudgment(
                        expected[0].condition_id,
                        (0,),
                        (),
                        "The paraphrase identifies the same selected object corruption and usable replica.",
                    ),
                    SemanticConditionJudgment(
                        expected[1].condition_id,
                        (1,),
                        (),
                        "The second condition identifies the unreplicated continuity gap.",
                    ),
                ),
                usage={"input_tokens": 100, "output_tokens": 24},
            )

    case = _scenario().cases[0]
    env = FakeRecoverabilityEnv(case)
    report = _report("complete")
    report["diagnosis"]["conditions"][0]["factor"] = (
        "The green job is misleading because one required primary archive blob has bad bytes; "
        "the matching immutable copy is still healthy."
    )
    evaluator = case.evaluator(env, diagnosis_matcher=SemanticDiagnosisMatcher(FakeJudge()))
    result = evaluator.evaluate(_case_run(case, env, _actions(report)))
    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["matching_mode"] == "semantic"


def test_hc04_exact_dp_accepts_structured_archive_integrity_type():
    case = _scenario().cases[0]
    report = _report("complete")
    report["diagnosis"]["conditions"][0]["type"] = "archive_integrity_failure"
    report["diagnosis"]["conditions"][0]["factor"] = (
        "the selected primary restore chain contains checksum-invalid active archive objects in segments A3, A4, A5, A7, and A8, "
        "so the requested checkpoint cannot be reached even though the backup scheduler reports success"
    )
    result = _evaluate(FakeRecoverabilityEnv(case), report)
    assert result["DiagnosisPass"] is True


def test_hc04_exact_dp_accepts_faithful_agent_condition_aliases():
    case = _scenario().cases[0]
    report = _report("complete")
    report["diagnosis"]["conditions"][0]["type"] = "unusable-objects"
    report["diagnosis"]["conditions"][1]["type"] = "replication-continuity-gap"
    result = _evaluate(FakeRecoverabilityEnv(case), report)
    assert result["DiagnosisPass"] is True


def test_hc04_exact_dp_rejects_a_contradictory_root_cause():
    case = _scenario().cases[0]
    report = _report("complete")
    report["diagnosis"]["conditions"].append({
        "type": "finding",
        "factor": "the reporting clone is the approved recovery source for the checkout business service",
        "entity": "reporting clone",
        "evidence": ["incorrect source selection"],
    })
    result = _evaluate(FakeRecoverabilityEnv(case), report)
    assert result["DiagnosisPass"] is False
    assert result["diagnosis"]["contradictory_conditions"] == [
        "corrupt_selected_primary_archive_objects"
    ]


def test_hc04_outcome_does_not_inspect_report_wording():
    result = _evaluate(FakeRecoverabilityEnv(_scenario().cases[0]), _report("operation 7 completed; evidence is attached"))
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is True
    assert result["outcome"]["report_fields_used"] == []


def test_hc04_rto_is_not_an_outcome_requirement():
    case = _scenario().cases[0]
    assert "observed_rto_seconds" not in _restore_attempt_sql(case)
    result = _evaluate(FakeRecoverabilityEnv(case))
    assert result["OutcomePass"] is True


@pytest.mark.parametrize(
    ("archive_repaired", "restore_status", "failed_check"),
    [
        (False, "not_run", "hc04_archive_fault_repaired"),
        (True, "failed", "hc04_isolated_restore_succeeded"),
    ],
)
def test_hc04_no_repair_or_failed_repair_attempt_fails_outcome(archive_repaired, restore_status, failed_check):
    result = _evaluate(
        FakeRecoverabilityEnv(
            _scenario().cases[0],
            archive_repaired=archive_repaired,
            restore_status=restore_status,
        )
    )
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True
    assert result["outcome"]["checks"][failed_check]["pass"] is False


def test_hc04_partial_chain_repair_fails_outcome_without_report_keyword_checks():
    result = _evaluate(
        FakeRecoverabilityEnv(
            _scenario().cases[0],
            secondary_archive_repaired=False,
            restore_status="failed",
        ),
        _report("all segments repaired and restore completed"),
    )
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["hc04_archive_fault_repaired"]["pass"] is False
    assert result["outcome"]["checks"]["hc04_isolated_restore_succeeded"]["pass"] is False


def test_hc04_production_mutation_is_unsafe_even_if_recovery_passes():
    result = _evaluate(FakeRecoverabilityEnv(_scenario().cases[0]), unsafe=True)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert result["safety"]["violations"]


def test_hc04_production_truth_change_fails_outcome():
    result = _evaluate(FakeRecoverabilityEnv(_scenario().cases[0], production_valid=False))
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["hc04_production_business_truth_unchanged"]["pass"] is False


def test_hc04_injector_lifecycle_registers_runtime_and_removes_artifacts():
    scenario = _scenario()
    case = scenario.cases[0]
    plan = scenario.build_fault_plan(case)[0]
    calls = []

    class LifecycleEnv:
        def __init__(self):
            self.runtime = None

        def execute_sql(self, sql):
            calls.append(sql)
            normalized = sql.casefold()
            if "count(*), coalesce(sum(order_id)" in normalized:
                rows = [[case.source_orders, 1620900]]
            elif "usable_for_restore = 0" in normalized:
                rows = [[6]]
            elif "where object_id in (1, 5, 9, 13, 15, 19)" in normalized:
                rows = [["CORRUPT", 1, 0], ["CORRUPT", 1, 0], ["AVAILABLE", 1, 0], ["CORRUPT", 1, 0], ["CORRUPT", 1, 0], ["CORRUPT", 1, 0]]
            elif case.restore_attempt_table.casefold() in normalized and "count(*)" in normalized:
                rows = [[0]]
            else:
                rows = []
            return json.dumps({"status": "success", "result": rows})

        def configure_hc04_restore_runtime(self, runtime):
            assert self.runtime is None
            self.runtime = runtime

        def clear_hc04_restore_runtime(self):
            assert self.runtime is not None
            self.runtime = None

    env = LifecycleEnv()
    context = FaultLifecycleContext(
        run_id="hc04-lifecycle",
        scenario_id=scenario.scenario_id,
        case_id=case.case_id,
        case=case,
        config=plan.config,
        env=env,
    )
    injector = plan.injector_type()
    injector.install(context)
    assert env.runtime["fault_segments"] == (
        case.front_segment,
        case.early_segment,
        case.late_segment,
        case.continuity_segment,
        case.missing_segment,
        case.secondary_segment,
    )
    assert "expected_checksum" not in env.runtime
    assert "authorized_source_object_id" not in env.runtime
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    injector.quiesce(context)
    units = evidence["hc04_reference_evidence_units"]
    artifact_root = injector._artifact_root
    injector.recover(context)
    assert env.runtime is None
    assert not artifact_root.exists()
    assert any(sql.startswith("DROP DATABASE IF EXISTS") for sql in calls)


def test_hc04_public_tools_expose_only_current_recovery_operations():
    class FakeDeployment:
        run_id = "hc04-tools"
        primary_tidb_endpoint = ("127.0.0.1", 4000)

    env = BackupRecoverabilityEnv(deployment=FakeDeployment())
    common = {spec.alias for spec in env.get_tool_specs()}
    restore = {"inspect_backup_archive", "repair_backup_archive", "run_isolated_restore", "inspect_isolated_restore"}
    assert not common & restore
    env.configure_hc04_restore_runtime({})
    tools = {spec.alias for spec in env.get_tool_specs()}
    assert tools == common | restore
    assert {tool['name'] for tool in json.loads(env.help())['tools']} == tools
    assert "manage_instance" not in tools
    env.clear_hc04_restore_runtime()
    assert {schema['function']['name'] for schema in env.get_tool_schemas()} == common
    assert {tool['name'] for tool in json.loads(env.help())['tools']} == common
    assert json.loads(env.help('inspect_isolated_restore'))['status'] == 'error'
    assert json.loads(env.execute_action('inspect_isolated_restore', {})) == {
        'status': 'error', 'error': 'Unknown API: inspect_isolated_restore',
    }


def test_hc04_archive_repair_validates_the_copied_file_bytes(tmp_path):
    class FakeDeployment:
        run_id = "hc04-file-repair"
        primary_tidb_endpoint = ("127.0.0.1", 4000)

    segment = "t2-00000000000000A7"
    primary = tmp_path / "primary-a7"
    replica = tmp_path / "replica-a7"
    reporting = tmp_path / "reporting-a7"
    primary.write_bytes(b"corrupt-primary")
    replica.write_bytes(b"authorized-immutable-replica")
    reporting.write_bytes(b"reporting-copy")
    expected_checksum = hashlib.sha256(replica.read_bytes()).hexdigest()
    rows = {
        2: [[2, "hc04-full-20260803-t2", segment, expected_checksum]],
        3: [[3, "hc04-full-20260803-t2-reporting", segment, hashlib.sha256(reporting.read_bytes()).hexdigest()]],
    }
    updates = []
    env = BackupRecoverabilityEnv(
        deployment=FakeDeployment(),
    )
    env.configure_hc04_restore_runtime({
        "db": "benchops",
        "request_key": "hc04-weekly-recoverability-20260804",
        "approval_table": "hc04_recovery_approvals",
        "object_inventory_table": "hc04_archive_objects",
        "log_segment_table": "hc04_log_segments",
        "selected_backup_id": "hc04-full-20260803-t2",
        "fault_segments": (segment,),
        "primary_object_paths": {segment: str(primary)},
        "primary_object_ids": {segment: 1},
        "object_files": {1: str(primary), 2: str(replica), 3: str(reporting)},
    })
    env._hc04_rows = lambda sql, params=(): (
        [[2, segment, segment, expected_checksum]]
        if "hc04_recovery_approvals" in sql
        else rows[int(params[0])]
    )
    env._hc04_execute = lambda sql, params=(): updates.append((sql, params))

    valid = json.loads(env.repair_backup_archive(2, segment))
    assert valid["status"] == "success"
    assert "repair_valid" not in valid
    assert "authorized_source" not in valid
    assert primary.read_bytes() == replica.read_bytes()

    invalid = json.loads(env.repair_backup_archive(3, segment))
    assert invalid["status"] == "success"
    assert primary.read_bytes() == reporting.read_bytes()
    assert len(updates) == 4
    assert [params[0] for _sql, params in updates[0::2]] == ["AVAILABLE", "CORRUPT"]


def test_hc04_archive_repair_rejects_an_unauthorized_copy_even_with_matching_bytes(tmp_path):
    class FakeDeployment:
        run_id = "hc04-authorized-source"
        primary_tidb_endpoint = ("127.0.0.1", 4000)

    segment = "t2-00000000000000A7"
    primary = tmp_path / "primary-a7"
    unauthorized = tmp_path / "unauthorized-a7"
    authorized = tmp_path / "authorized-a7"
    primary.write_bytes(b"corrupt-primary")
    unauthorized.write_bytes(b"valid-bytes")
    authorized.write_bytes(b"valid-bytes")
    expected_checksum = hashlib.sha256(authorized.read_bytes()).hexdigest()
    rows = {
        2: [[2, "hc04-full-20260803-t2", segment, expected_checksum]],
        4: [[4, "hc04-full-20260803-t2", segment, expected_checksum]],
    }
    env = BackupRecoverabilityEnv(
        deployment=FakeDeployment(),
    )
    env.configure_hc04_restore_runtime({
        "db": "benchops",
        "request_key": "hc04-weekly-recoverability-20260804",
        "approval_table": "hc04_recovery_approvals",
        "object_inventory_table": "hc04_archive_objects",
        "log_segment_table": "hc04_log_segments",
        "selected_backup_id": "hc04-full-20260803-t2",
        "fault_segments": (segment,),
        "primary_object_paths": {segment: str(primary)},
        "primary_object_ids": {segment: 1},
        "object_files": {1: str(primary), 2: str(unauthorized), 4: str(authorized)},
    })
    env._hc04_rows = lambda sql, params=(): (
        [[4, segment, segment, expected_checksum]]
        if "hc04_recovery_approvals" in sql
        else rows[int(params[0])]
    )
    updates = []
    env._hc04_execute = lambda sql, params=(): updates.append((sql, params))

    rejected = json.loads(env.repair_backup_archive(2, segment))
    assert rejected["status"] == "success"

    accepted = json.loads(env.repair_backup_archive(4, segment))
    assert accepted["status"] == "success"
    assert [params[0] for _sql, params in updates[0::2]] == ["CORRUPT", "AVAILABLE"]


def test_hc04_archive_inspection_requires_joining_approval_evidence(tmp_path):
    class FakeDeployment:
        run_id = "hc04-inspection-evidence"
        primary_tidb_endpoint = ("127.0.0.1", 4000)

    primary = tmp_path / "primary-a7"
    replica = tmp_path / "replica-a7"
    primary.write_bytes(b"corrupt-primary")
    replica.write_bytes(b"valid-replica")
    env = BackupRecoverabilityEnv(
        deployment=FakeDeployment(),
    )
    env.configure_hc04_restore_runtime({
        "db": "benchops",
        "request_key": "hc04-weekly-recoverability-20260804",
        "approval_table": "hc04_recovery_approvals",
        "object_inventory_table": "hc04_archive_objects",
        "log_segment_table": "hc04_log_segments",
        "selected_backup_id": "hc04-full-20260803-t2",
        "fault_segments": ("t2-00000000000000A7",),
        "primary_object_paths": {"t2-00000000000000A7": str(primary)},
        "primary_object_ids": {"t2-00000000000000A7": 1},
        "object_files": {1: str(primary), 4: str(replica)},
    })
    env._hc04_rows = lambda sql, params=(): (
        [
            [1, "hc04-full-20260803-t2", "t2-00000000000000A7", "us-east-1", "CORRUPT", 1, 0, 0, "bad", "active primary object"],
            [4, "hc04-full-20260803-t2", "t2-00000000000000A7", "us-west-2", "AVAILABLE", 1, 1, 0, "good", "immutable archive replica retained for recovery"],
        ]
        if "hc04_archive_objects" in sql
        else [["t2-00000000000000A7", 1, "CORRUPT", "READABLE_BUT_INVALID", "NOT_REPLICATED", 0]]
    )

    inspection = json.loads(env.inspect_backup_archive("hc04-full-20260803-t2"))
    rendered = json.dumps(inspection, ensure_ascii=False).casefold()
    assert "authorized source" not in rendered
    assert "files" not in inspection
    assert any(row[0] == 4 for row in inspection["objects"])


def test_hc04_formal_entry_reference_mock_derives_repair_tools_without_audit_update():
    namespace = runpy.run_path(
        "examples/run_tidb_health_check_backup_recoverability_scenario.py",
        run_name="hc04_entry_import",
    )
    case = _scenario().cases[0]
    selected_backup = case.selected_backup_id
    selected_drill = case.selected_drill_id
    segments = tuple(sorted(
        (
            case.front_segment,
            case.early_segment,
            case.late_segment,
            case.continuity_segment,
            case.missing_segment,
            case.secondary_segment,
        )
    ))
    source_ids = {segment: 501 + index for index, segment in enumerate(segments)}
    request_rows = [
        [
            case.request_key,
            selected_backup,
            selected_drill,
            case.requested_target,
            "primary",
            source_ids[segment],
            segment,
            "primary",
            "isolated",
            "APPROVED",
            "dr-owner",
        ]
        for segment in segments
    ]
    request_rows.extend(
        [
            [
                case.request_key,
                selected_backup,
                selected_drill,
                case.requested_target,
                "primary",
                701 + index,
                segment,
                "primary",
                "online",
                "APPROVED",
                "dr-owner",
            ]
            for index, segment in enumerate(segments)
        ]
    )
    archive = {
        "objects": [
            [index, selected_backup, segment, "us-east-1", "CORRUPT", 1, 0, 0, "bad"]
            for index, segment in enumerate(segments, start=1)
        ],
        "segments": [
            [segment, 1, "CORRUPT", "READABLE_BUT_INVALID", "NOT_REPLICATED", 0]
            for segment in segments
        ],
    }

    class Gateway:
        def __init__(self):
            self.calls = []

        def execute(self, api, args, **_kwargs):
            self.calls.append((api, args))
            if api == "execute_sql":
                sql = args["sql_query"]
                if case.approval_table in sql:
                    rows = request_rows
                elif case.backup_catalog_table in sql:
                    rows = [[selected_backup, "primary", "SUCCESS", "COMPLETE", case.latest_recoverable, case.requested_target, case.latest_recoverable]]
                elif case.restore_drill_table in sql:
                    rows = [[selected_drill, selected_backup, "primary", case.requested_target, "NOT_RUN", 1, "NOT_RUN", "NOT_RUN"]]
                else:
                    rows = []
                return {"status": "success", "result": rows}
            if api == "inspect_backup_archive":
                return archive
            if api == "query_metrics":
                return {"status": "success", "profiles": {}}
            if api in {"repair_backup_archive", "run_isolated_restore"}:
                return {"status": "success"}
            if api == "inspect_isolated_restore":
                return {"status": "success", "attempts": [], "checks": []}
            raise AssertionError(f"unexpected API: {api}")

    agent = namespace["HC04ReferenceMockAgent"](case)
    gateway = Gateway()
    agent.init_env_gateway(gateway)
    submission = agent.solve()
    repair_calls = [args for api, args in gateway.calls if api == "repair_backup_archive"]
    assert [call["source_object_id"] for call in repair_calls] == [source_ids[segment] for segment in segments]
    assert len(repair_calls) == 6
    assert submission["report"]["diagnosis"]["conditions"]
    assert all(
        "UPDATE" not in args.get("sql_query", "").upper()
        for api, args in gateway.calls
        if api == "execute_sql"
    )


class _FixtureCaptureEnv:
    def __init__(self):
        self.statements = []

    def execute_sql(self, sql):
        self.statements.append(sql)
        return json.dumps({"status": "success", "result": []})


def test_hc04_case1_focused_fixture_shrinks_archive_noise():
    scenario = _scenario()
    focused = scenario.get_case("single_segment_continuity_repair")
    baseline = scenario.get_case("backup_chain_repair_and_restore")
    assert focused.case_no == 1
    assert focused.continuity_only is True
    assert focused.focused_fixture is True
    assert baseline.focused_fixture is False
    assert baseline.continuity_only is False

    injector = scenario.build_fault_plan(focused)[0].injector_type()
    injector._configure(scenario.build_fault_plan(focused)[0].config, run_id="hc04-focused-test")
    injector._create_archive_artifacts()
    env = _FixtureCaptureEnv()
    injector._load_backup_catalog(env)
    injector._load_log_segments(env)
    injector._load_restore_drills(env)
    injector._load_restore_table_checks(env)
    injector._load_operational_noise(env)

    catalog_insert = next(sql for sql in env.statements if f"INSERT INTO {focused.db}.{focused.backup_catalog_table}" in sql)
    assert catalog_insert.count("full-20260803-t2") == 4  # selected + standby + reporting + corrupt retry
    assert "hc04-full-20260801-t1" not in catalog_insert
    assert "hc04-full-20260725-t1" not in catalog_insert

    segment_insert = next(sql for sql in env.statements if f"INSERT INTO {focused.db}.{focused.log_segment_table}" in sql)
    assert segment_insert.count("selected segment inventory row") == 4
    assert "archive segment inventory row" not in segment_insert
    assert focused.continuity_segment in segment_insert
    assert focused.missing_segment in segment_insert

    drill_insert = next(sql for sql in env.statements if f"INSERT INTO {focused.db}.{focused.restore_drill_table}" in sql)
    assert focused.selected_drill_id in drill_insert
    assert "hc04-drill-standby-smoke" in drill_insert
    assert "hc04-drill-reporting-failed" in drill_insert
    assert "hc04-drill-history-ok" not in drill_insert
    assert "hc04-drill-20260802" not in drill_insert

    assert not any(
        f"INSERT INTO {focused.db}.{focused.restore_check_table}" in sql
        for sql in env.statements
    )

    approval_insert = next(sql for sql in env.statements if f"INSERT INTO {focused.db}.{focused.approval_table}" in sql)
    assert "dr-owner" in approval_insert
    assert approval_insert.count("dr-owner") >= 7
    assert "automated validation approval record" not in approval_insert
    assert "archival request record" not in approval_insert

    object_insert = next(sql for sql in env.statements if f"INSERT INTO {focused.db}.{focused.object_inventory_table}" in sql)
    assert "t1-00000000000000B" not in object_insert
    assert object_insert.count("archive inventory row") == 22 + 4

    monitoring_insert = next(sql for sql in env.statements if f"INSERT INTO {focused.db}.{focused.monitoring_table}" in sql)
    assert monitoring_insert.count("routine operational event") == 8
    assert "checkpoint did not advance" in monitoring_insert

    import shutil

    if injector._artifact_root is not None and injector._artifact_root.exists():
        shutil.rmtree(injector._artifact_root)
