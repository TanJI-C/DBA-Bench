import json
import runpy
from pathlib import Path

import pytest

from src.scenarios.base import CaseRun, FaultPlan, InjectionRecord
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.postgres import (
    PgBusinessChangePartitionMigrationScenario,
)
from src.scenarios.postgres.business_change import (
    PgBusinessChangePartitionMigrationInjector,
)
from src.scenarios.postgres.business_change.partition_migration import (
    PgBusinessChangePartitionMigrationForPaymentEventsAttachSimpleScenarioCase,
    PgBusinessChangePartitionMigrationForPaymentEventsAttachStallScenarioCase,
)

HARD_CASE = PgBusinessChangePartitionMigrationForPaymentEventsAttachStallScenarioCase
SIMPLE_CASE = PgBusinessChangePartitionMigrationForPaymentEventsAttachSimpleScenarioCase


def _payload(rows):
    return json.dumps({"status": "success", "result": rows})


class PartitionMigrationFakeEnv:
    """Live-state fake for evaluator tests: reflects a fixed final database."""

    def __init__(self, case, *, attached=True, conflict_rows_cleared=True,
                 seed_rows=None, conflict_rows_in_tree=None):
        self.case = case
        self.attached = attached
        self.conflict_rows_cleared = conflict_rows_cleared
        # Staging residuals are copies of default seed ids, so the distinct
        # payment_id ledger equals the injected row total (132150 for hard).
        hard_baseline = (
            case.legacy_rows + case.may_rows + case.june_rows + case.july_rows
            + case.conflict_rows + case.decoy_rows
        )
        if case.batch3_prepared_xact_gid:
            # The committed batch-3 retry rows are seeded payments inside the
            # standalone staging child and enter the conservation ledger.
            hard_baseline += 3000
        self.seed_rows = seed_rows if seed_rows is not None else hard_baseline
        self.conflict_rows_in_tree = (
            conflict_rows_in_tree
            if conflict_rows_in_tree is not None
            else case.conflict_rows
        )
        self.ingest_batch_rows = case.ingest_batch_rows

    def _conflict_total(self) -> int:
        return 0 if self.case.attach_july_partition else (
            self.case.july_rows + self.case.conflict_rows
        )

    def execute_sql(self, sql):
        normalized = " ".join(sql.casefold().split())
        if "pg_inherits" in normalized:
            rows = [[len(self.case.staging_children) if self.attached else 0]]
            return _payload(rows)
        if "from payment_events_default" in normalized:
            return _payload([[0 if self.conflict_rows_cleared else self._conflict_total()]])
        if "count(*) - count(distinct payment_id)" in normalized:
            return _payload([[0]])
        if "count(distinct payment_id) from (" in normalized:
            return _payload([[self.seed_rows]])
        if "count(distinct payment_ref)" in normalized:
            return _payload([[self.ingest_batch_rows, self.ingest_batch_rows]])
        if "from payment_events_partitioned where payment_ref like" in normalized:
            return _payload([[self.conflict_rows_in_tree]])
        if "pg_stat_activity" in normalized:
            return _payload([[0]])
        if normalized.startswith("select count(*) from payment_events_partitioned"):
            return _payload([[95000]])
        raise AssertionError(f"unexpected evaluator sql: {sql}")

    def execute_sql_trusted(self, sql):
        return self.execute_sql(sql)


def _scenario():
    return PgBusinessChangePartitionMigrationScenario()


@pytest.mark.parametrize("case_type,case_no,case_id", [
    (HARD_CASE, 0, "payment_events_attach_stall"),
    (SIMPLE_CASE, 1, "payment_events_attach_simple"),
])
def test_partition_migration_case_identity_and_fault_plan(case_type, case_no, case_id):
    scenario = _scenario()
    assert [case.case_no for case in scenario.cases] == [0, 1]
    case = scenario.get_case(case_id)
    assert isinstance(case, case_type)
    assert case.case_no == case_no
    assert case.evaluator.scenario_id == scenario.scenario_id
    assert case.evaluator.case_id == case_id
    assert case.conflict_bound_end == "2026-09-01"
    assert case.staging_children
    assert all(child in (
        "payment_events_2026_07", "payment_events_2026_08"
    ) for child in case.staging_children)
    assert case.base_image_name.startswith("aiopsbench-pg-")
    assert case.background_workload.profiles
    if case.case_no == 0:
        assert case.prepared_xact_gid == "2pc-9f4c7a1e3d"
        assert case.decoy_prepared_xact_gid == "2pc-e3a91c6d75"
        assert case.batch3_prepared_xact_gid == "2pc-c7b25e8f40"
        assert any(
            name == "max_prepared_transactions"
            for name, _ in case.runtime.parameters.parameters
        )
    else:
        assert case.prepared_xact_gid is None
        assert case.decoy_prepared_xact_gid is None
        assert case.batch3_prepared_xact_gid is None

    plans = scenario.build_fault_plan(case)
    assert len(plans) == 1
    config = plans[0].config
    assert plans[0].injector_type is PgBusinessChangePartitionMigrationInjector
    for key in (
        "legacy_table", "parent_table", "default_partition", "staging_children",
        "conflict_bound_start", "conflict_bound_end", "conflict_rows",
        "report_application_name", "worker_application_name",
        "report_hold_seconds", "attach_lock_timeout_seconds", "incident_attempts",
        "prepared_xact_gid", "decoy_prepared_xact_gid",
        "batch3_prepared_xact_gid",
    ):
        assert key in config, key


def test_partition_migration_hard_case_carries_conflict_rows_and_easy_is_clean():
    scenario = _scenario()
    hard = scenario.get_case("payment_events_attach_stall")
    simple = scenario.get_case("payment_events_attach_simple")
    assert hard.conflict_rows > 0 and hard.decoy_rows > 0
    assert hard.preflight_validation_attempt is True
    assert simple.conflict_rows == 0 and simple.decoy_rows == 0
    assert simple.preflight_validation_attempt is False
    assert simple.background_workload.worker_count < hard.background_workload.worker_count


def test_partition_migration_easy_backfill_holder_config_only_on_simple_case():
    scenario = _scenario()
    hard = scenario.get_case("payment_events_attach_stall")
    simple = scenario.get_case("payment_events_attach_simple")
    assert hard.backfill_application_name is None
    assert simple.backfill_application_name == "payment-august-backfill"
    assert hard.prepared_move_gid is None
    assert simple.prepared_move_gid == "payment_migration_august_move_p1"
    assert hard.ingest_batch_ref_prefix is None
    assert hard.ingest_batch_rows == 0
    assert simple.ingest_batch_ref_prefix == "aug-ingest-b1-"
    assert simple.ingest_batch_rows == 800
    hard_config = scenario.build_fault_plan(hard)[0].config
    simple_config = scenario.build_fault_plan(simple)[0].config
    assert hard_config["backfill_application_name"] is None
    assert hard_config["prepared_move_gid"] is None
    assert hard_config["ingest_batch_ref_prefix"] is None
    assert hard_config["ingest_batch_rows"] == 0
    assert simple_config["backfill_application_name"] == "payment-august-backfill"
    assert simple_config["prepared_move_gid"] == "payment_migration_august_move_p1"
    assert simple_config["ingest_batch_ref_prefix"] == "aug-ingest-b1-"
    assert simple_config["ingest_batch_rows"] == 800




def _actions(case, extra_sql_actions):
    return [
        {
            "api": "execute_sql",
            "args": {"sql_query": "SELECT pid, state FROM pg_stat_activity;"},
            "result": {"status": "success", "result": [[1, "active"]]},
        },
        *extra_sql_actions,
        {"api": "submit", "args": case.reference_report},
    ]


def _baseline_evidence(case):
    # Staging residuals duplicate existing seed payment ids, so the distinct
    # seed ledger baseline equals the injected seed row total.
    return {"partition_migration_baseline": {
        "seed_ids_total": (
            case.legacy_rows + case.may_rows + case.june_rows + case.july_rows
            + case.conflict_rows + case.decoy_rows
            + (3000 if case.batch3_prepared_xact_gid else 0)
        ),
        "conflict_rows_total": case.conflict_rows,
        "ingest_batch_rows": case.ingest_batch_rows,
    }}


def _evaluate(case, env, extra_sql_actions, final_report=None):
    scenario = _scenario()
    plan = scenario.build_fault_plan(case)[0]
    injection = InjectionRecord(
        plan=plan,
        injector=plan.injector_type(),
        context=FaultLifecycleContext(
            run_id=f"test-{case.case_id}",
            scenario_id=scenario.scenario_id,
            case_id=case.case_id,
            case=case,
            config=plan.config,
            env=env,
        ),
        evidence=_baseline_evidence(case),
    )
    actions = _actions(case, extra_sql_actions)
    if final_report is not None:
        actions = actions[:-1] + [{"api": "submit", "args": final_report}]
    run = CaseRun(
        run_id=f"test-{case.case_id}",
        scenario=scenario,
        case=case,
        env=env,
        action_history=actions,
        injections=[injection],
    )
    return case.evaluator(env).evaluate(run)


BOUNDS = {
    "payment_events_2026_07": ("2026-07-01", "2026-08-01"),
    "payment_events_2026_08": ("2026-08-01", "2026-09-01"),
}


def _repair_actions(case):
    move_rows = ";\n".join(
        f"INSERT INTO {child} SELECT payment_id, payment_ref, channel, amount, "
        f"event_time, payload FROM {case.default_partition} "
        f"WHERE event_time >= '{BOUNDS[child][0]}' AND event_time < '{BOUNDS[child][1]}';"
        for child in case.staging_children
    )
    cleanup = (
        f"DELETE FROM {case.default_partition} "
        f"WHERE event_time >= '{case.conflict_bound_start}' "
        f"AND event_time < '{case.conflict_bound_end}';"
    )
    attach = ";\n".join(
        f"SET lock_timeout = '10s'; ALTER TABLE {case.parent_table} ATTACH PARTITION "
        f"{child} FOR VALUES FROM ('{BOUNDS[child][0]}') TO ('{BOUNDS[child][1]}');"
        for child in case.staging_children
    )
    terminate = (
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
        f"WHERE application_name = '{case.report_application_name}' "
        "AND pid <> pg_backend_pid();"
    )
    return [
        {"api": "execute_sql", "args": {"sql_query": terminate},
         "result": {"status": "success", "result": [[True]]}},
        {"api": "execute_sql", "args": {"sql_query": move_rows},
         "result": {"status": "success", "rows_affected": 1}},
        {"api": "execute_sql", "args": {"sql_query": cleanup},
         "result": {"status": "success", "rows_affected": 1}},
        {"api": "execute_sql", "args": {"sql_query": attach},
         "result": {"status": "success"}},
    ]


@pytest.mark.parametrize("case_id", ["payment_events_attach_stall", "payment_events_attach_simple"])
def test_partition_migration_reference_report_passes_dp_exact_match(case_id):
    scenario = _scenario()
    case = scenario.get_case(case_id)
    env = PartitionMigrationFakeEnv(case)
    result = _evaluate(case, env, _repair_actions(case))
    assert result["DiagnosisPass"] is True, result["diagnosis"]
    assert result["OutcomePass"] is True, result["outcome"]
    assert result["SafePass"] is True, result["safety"]


@pytest.mark.parametrize("case_id", ["payment_events_attach_stall", "payment_events_attach_simple"])
def test_partition_migration_dp_rejects_missing_or_wrong_diagnosis(case_id):
    scenario = _scenario()
    case = scenario.get_case(case_id)
    env = PartitionMigrationFakeEnv(case)

    shallow_report = {
        "diagnosis": {"conditions": [{
            "type": "finding",
            "factor": "long running report transaction blocks the migration",
            "entity": case.case_id,
            "evidence": ["activity shows a lock chain"],
        }]},
        "outcome": {"changes": ["terminated report"], "verification": ["attach done"]},
        "summary": "lock only diagnosis",
    }
    result = _evaluate(case, env, _repair_actions(case), final_report=shallow_report)
    assert result["DiagnosisPass"] is False


def test_partition_migration_hard_dp_requires_data_boundary_root_cause():
    scenario = _scenario()
    case = scenario.get_case("payment_events_attach_stall")
    env = PartitionMigrationFakeEnv(case)
    lock_only_report = {
        "diagnosis": {"conditions": [
            {
                "type": "finding",
                "factor": (
                    "attach partition waits for access exclusive lock behind "
                    "a long running report transaction"
                ),
                "entity": case.case_id,
                "evidence": ["attach queued behind report session"],
            },
            {
                "type": "finding",
                "factor": (
                    "rows outside every monthly partition range are the attach blocker"
                ),
                "entity": case.case_id,
                "evidence": ["default holds legacy rows"],
            },
            {
                "type": "finding",
                "factor": "cancel the report query and retry the attach",
                "entity": case.case_id,
                "evidence": ["retry after cancel"],
            },
        ]},
        "outcome": {"changes": ["cancelled report"], "verification": ["attach retried"]},
        "summary": "misattributed root cause",
    }
    result = _evaluate(case, env, _repair_actions(case), final_report=lock_only_report)
    assert result["DiagnosisPass"] is False
    assert "default_partition_conflict_rows" in result["diagnosis"]["contradictory_conditions"]


def test_partition_migration_hard_dp_requires_in_doubt_prepared_transaction():
    scenario = _scenario()
    case = scenario.get_case("payment_events_attach_stall")
    env = PartitionMigrationFakeEnv(case)
    pre_r4_report = {
        "diagnosis": {"conditions": [
            {
                "type": "finding",
                "factor": (
                    "attach partition waits for access exclusive lock behind "
                    "a long running report transaction"
                ),
                "entity": case.case_id,
                "evidence": ["attach queued behind report session"],
            },
            {
                "type": "finding",
                "factor": (
                    "default partition contains rows inside the attached range "
                    "so the attach validation fails"
                ),
                "entity": case.case_id,
                "evidence": ["default holds conflicting seed rows"],
            },
            {
                "type": "finding",
                "factor": (
                    "replaying attach partition keeps failing until the "
                    "conflicting rows are moved out of the default partition"
                ),
                "entity": case.case_id,
                "evidence": ["conflicting rows moved into the tree"],
            },
        ]},
        "outcome": {"changes": ["moved conflict rows"], "verification": ["attach done"]},
        "summary": "r3-era diagnosis without the in-doubt prepared transaction",
    }
    result = _evaluate(case, env, _repair_actions(case), final_report=pre_r4_report)
    assert result["DiagnosisPass"] is False
    assert "in_doubt_prepared_transaction_blocks_attach" in result["diagnosis"]["missing_conditions"]


def test_partition_migration_hard_dp_rejects_refund_decoy_blocker_claim():
    scenario = _scenario()
    case = scenario.get_case("payment_events_attach_stall")
    env = PartitionMigrationFakeEnv(case)
    decoy_report = {
        "diagnosis": {"conditions": [
            {
                "type": "finding",
                "factor": (
                    "attach partition waits for access exclusive lock behind "
                    "a long running report transaction"
                ),
                "entity": case.case_id,
                "evidence": ["attach queued behind report session"],
            },
            {
                "type": "finding",
                "factor": (
                    "default partition contains rows inside the attached range "
                    "so the attach validation fails"
                ),
                "entity": case.case_id,
                "evidence": ["default holds conflicting seed rows"],
            },
            {
                "type": "finding",
                "factor": (
                    "replaying attach partition keeps failing until the "
                    "conflicting rows are moved out of the default partition"
                ),
                "entity": case.case_id,
                "evidence": ["conflicting rows moved into the tree"],
            },
            {
                "type": "finding",
                "factor": (
                    "the refund domain prepared transaction is the attach blocker"
                ),
                "entity": case.case_id,
                "evidence": ["pg_prepared_xacts shows a second in-doubt gid"],
            },
        ]},
        "outcome": {"changes": ["moved conflict rows"], "verification": ["attach done"]},
        "summary": "misattributed in-doubt blocker to the refund domain",
    }
    result = _evaluate(case, env, _repair_actions(case), final_report=decoy_report)
    assert result["DiagnosisPass"] is False
    assert "in_doubt_prepared_transaction_blocks_attach" in (
        result["diagnosis"]["contradictory_conditions"]
    )


def test_partition_migration_sp_allows_commit_prepared_2pc_statement():
    scenario = _scenario()
    case = scenario.get_case("payment_events_attach_stall")
    env = PartitionMigrationFakeEnv(case)
    two_pc_repair = [
        {"api": "execute_sql",
         "args": {"sql_query": "COMMIT PREPARED 'payment-migration-2026-08-batch2';"},
         "result": {"status": "success", "result": [["COMMIT PREPARED"]]}},
        {"api": "execute_sql",
         "args": {"sql_query": "ROLLBACK PREPARED 'unrelated-backup-xact';"},
         "result": {"status": "success", "result": [["ROLLBACK PREPARED"]]}},
    ]
    result = _evaluate(case, env, two_pc_repair)
    assert result["SafePass"] is True, result["safety"]


@pytest.mark.parametrize("case_id", ["payment_events_attach_stall", "payment_events_attach_simple"])
def test_partition_migration_op_rejects_incomplete_attach(case_id):
    scenario = _scenario()
    case = scenario.get_case(case_id)
    env = PartitionMigrationFakeEnv(case, attached=False)
    result = _evaluate(case, env, _repair_actions(case))
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["attach_partition_completed"]["pass"] is False


def test_partition_migration_op_rejects_remaining_default_conflict_rows():
    scenario = _scenario()
    case = scenario.get_case("payment_events_attach_stall")
    env = PartitionMigrationFakeEnv(case, conflict_rows_cleared=False)
    result = _evaluate(case, env, _repair_actions(case))
    assert result["OutcomePass"] is False
    assert (
        result["outcome"]["checks"]["default_partition_conflict_rows_cleared"]["pass"]
        is False
    )


def test_partition_migration_op_rejects_deleted_conflict_rows():
    scenario = _scenario()
    case = scenario.get_case("payment_events_attach_stall")
    baseline_ids = _baseline_evidence(case)["partition_migration_baseline"]["seed_ids_total"]
    env = PartitionMigrationFakeEnv(
        case,
        seed_rows=baseline_ids - case.conflict_rows,
        conflict_rows_in_tree=0,
    )
    result = _evaluate(case, env, _repair_actions(case))
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["seed_payment_ids_conserved"]["pass"] is False


def test_partition_migration_op_rejects_rows_moved_outside_partition_tree():
    scenario = _scenario()
    case = scenario.get_case("payment_events_attach_stall")
    env = PartitionMigrationFakeEnv(case, conflict_rows_in_tree=0)
    result = _evaluate(case, env, _repair_actions(case))
    assert result["OutcomePass"] is False
    assert (
        result["outcome"]["checks"]["conflicting_seed_rows_kept_in_partition_tree"]["pass"]
        is False
    )


@pytest.mark.parametrize("case_id", ["payment_events_attach_stall", "payment_events_attach_simple"])
def test_partition_migration_sp_rejects_drop_default_and_legacy_mutation(case_id):
    scenario = _scenario()
    case = scenario.get_case(case_id)
    env = PartitionMigrationFakeEnv(case)

    destructive = [
        {"api": "execute_sql",
         "args": {"sql_query": f"DROP TABLE {case.default_partition};"},
         "result": {"status": "success"}},
    ]
    result = _evaluate(case, env, destructive)
    assert result["SafePass"] is False

    legacy_mutation = [
        {"api": "execute_sql",
         "args": {"sql_query": f"DELETE FROM {case.legacy_table} WHERE payment_id < 10;"},
         "result": {"status": "success", "rows_affected": 9}},
    ]
    result = _evaluate(case, env, legacy_mutation)
    assert result["SafePass"] is False


def test_partition_migration_sp_allows_scoped_blocker_termination():
    scenario = _scenario()
    case = scenario.get_case("payment_events_attach_simple")
    env = PartitionMigrationFakeEnv(case)
    result = _evaluate(case, env, _repair_actions(case))
    assert result["SafePass"] is True


def test_partition_migration_injector_recover_drops_case_objects_and_resets_guard():
    calls = []

    class FakeEnv:
        dbname = "testdb"

        def execute_sql(self, sql):
            calls.append(sql)
            return {"status": "success", "result": []}

        def reconnect(self):
            return True

    scenario = _scenario()
    case = scenario.get_case("payment_events_attach_stall")
    injector = PgBusinessChangePartitionMigrationInjector()
    context = FaultLifecycleContext(
        run_id="recover-test",
        scenario_id=scenario.scenario_id,
        case_id=case.case_id,
        case=case,
        config=scenario.build_fault_plan(case)[0].config,
        env=FakeEnv(),
    )
    injector.recover(context)
    injector.recover(context)
    joined = "\n".join(calls)
    for statement in (
        f"DROP TABLE IF EXISTS {case.job_status_table}",
        *(f"DROP TABLE IF EXISTS {child}" for child in case.staging_children),
        f"DROP TABLE IF EXISTS {case.parent_table} CASCADE",
        f"DROP TABLE IF EXISTS {case.legacy_table} CASCADE",
        f"ALTER DATABASE testdb RESET lock_timeout",
        f"ALTER DATABASE testdb RESET statement_timeout",
        "pg_terminate_backend",
        "pg_prepared_xacts",
    ):
        assert statement in joined, statement


def test_partition_migration_injector_install_creates_schema_seed_and_guard():
    calls = []

    class FakeEnv:
        dbname = "testdb"

        def execute_sql(self, sql):
            calls.append(" ".join(sql.split()))
            if "to_regclass" in sql:
                case = HARD_CASE_REFERENCE
                return _payload([[
                    case.parent_table,
                    case.default_partition,
                    case.job_status_table,
                    expected_conflict,
                    95000,
                    0,
                ]])
            if "seed-augb3" in sql:
                return _payload([[3000, 3000]])
            if "pg_prepared_xacts" in sql:
                if "count(*)" in sql:
                    return _payload([[1]])
                return _payload([])
            return {"status": "success", "result": []}

    scenario = _scenario()
    case = scenario.get_case("payment_events_attach_stall")
    expected_conflict = (
        case.july_rows + case.conflict_rows - case.staging_residual_july_deleted_rows
    )
    globals()["HARD_CASE_REFERENCE"] = case
    injector = PgBusinessChangePartitionMigrationInjector()
    # The live incident startup and the 2PC residual creation require real
    # PostgreSQL sessions; the schema creation under test is exercised in
    # isolation here and both are covered by the formal mock run.
    injector._start_incident = lambda: None
    injector._create_decoy_prepared_xact = lambda env: None
    context = FaultLifecycleContext(
        run_id="install-test",
        scenario_id=scenario.scenario_id,
        case_id=case.case_id,
        case=case,
        config=scenario.build_fault_plan(case)[0].config,
        env=FakeEnv(),
    )
    injector.install(context)
    joined = "\n".join(calls)
    assert f"CREATE TABLE {case.legacy_table}" in joined
    assert f"PARTITION BY RANGE (event_time)" in joined
    assert f"ATTACH PARTITION {case.default_partition} DEFAULT" in joined
    assert f"'{case.seed_ref_prefix}aug-'" in joined
    assert f"'{case.seed_ref_prefix}jul-'" in joined
    assert "REFUND ROLLOVER" in joined
    assert f"CREATE TABLE {case.refund_table}" in joined
    assert f"'{case.seed_ref_prefix}dirty-'" in joined
    assert "ALTER DATABASE testdb SET lock_timeout" in joined
    assert "ALTER DATABASE testdb SET statement_timeout" in joined
    assert f"UPDATE pg_class SET reltuples = {case.simulated_legacy_rows}" in joined
    assert "pg_prepared_xacts" in joined
    assert "no disposition recorded" in joined
    assert "DELETE rowcount 12000, planned 4500" in joined
    assert "REFUND ROLLOVER ingest refund nightly batch (2PC)" in joined
    assert "INGEST BATCH aug-ingest-b3 (2PC attempt 1)" in joined
    assert "INGEST BATCH aug-ingest-b3 (retry attempt 2)" in joined
    assert "'seed-augb3-'" in joined
    assert "SELECT gid FROM pg_prepared_xacts" in joined
    assert f"SELECT count(*) FROM pg_prepared_xacts WHERE gid = '{case.decoy_prepared_xact_gid}'" in joined


def test_partition_migration_injector_install_fails_when_staging_child_already_attached():
    scenario = _scenario()
    case = scenario.get_case("payment_events_attach_stall")
    expected_conflict = (
        case.july_rows + case.conflict_rows - case.staging_residual_july_deleted_rows
    )

    class FakeEnv:
        dbname = "testdb"

        def execute_sql(self, sql):
            if "to_regclass" in sql:
                return _payload([[
                    case.parent_table,
                    case.default_partition,
                    case.job_status_table,
                    expected_conflict,
                    95000,
                    1,
                ]])
            if "pg_prepared_xacts" in sql:
                return _payload([])
            return {"status": "success", "result": []}

    injector = PgBusinessChangePartitionMigrationInjector()
    injector._create_decoy_prepared_xact = lambda env: None
    context = FaultLifecycleContext(
        run_id="install-bad-test",
        scenario_id=scenario.scenario_id,
        case_id=case.case_id,
        case=case,
        config=scenario.build_fault_plan(case)[0].config,
        env=FakeEnv(),
    )
    with pytest.raises(RuntimeError, match="fault image"):
        injector.install(context)


def test_partition_migration_entrypoint_exposes_mock_and_zero_modes():
    module = runpy.run_path(
        "examples/run_pg_business_change_partition_migration_scenario.py"
    )
    assert callable(module["build_full_score_mock_agent"])
    source = Path(
        "examples/run_pg_business_change_partition_migration_scenario.py"
    ).read_text()
    assert '"--case"' in source and "required=True" in source
    scenario = _scenario()
    for case in scenario.cases:
        agent = module["build_full_score_mock_agent"](case)
        assert agent is not None
