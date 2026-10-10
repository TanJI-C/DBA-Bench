import inspect
import json
import runpy
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import SemanticConditionJudgment, SemanticJudgment
from src.scenarios.base import CaseRun
from src.scenarios import TIDB_SCENARIO_REGISTRY
from src.scenarios.tidb import TidbBusinessChangeTimezoneDdlBackpressureScenario
from src.scenarios.tidb.runtime import TIDB_V8_1_0, tidb_runtime
from src.execution.deployment import TiDBDockerDeployment
from src.execution.environment import TiDBEnv
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb.business_change.timezone_ddl_backpressure import (
    TidbBusinessChangeTimezoneDdlBackpressureInjector,
)


SCENARIO = TidbBusinessChangeTimezoneDdlBackpressureScenario()
CASE = SCENARIO.get_case("dr_cutover_timezone_ddl_and_sink_backpressure")
PLAN = SCENARIO.build_fault_plan(CASE)[0]


def _report(*, missing=False, contradiction=False):
    conditions = []
    if not missing:
        for expected in CASE.evaluator.diagnosis_conditions:
            conditions.append({
                "type": "root_cause",
                "factor": expected.condition_id,
                "entity": expected.condition_id,
                "evidence": [f"observed {expected.condition_id}"],
            })
    if contradiction:
        conditions.append({
            "type": "root_cause",
            "factor": "The replication failure is caused by a TiKV quorum outage rather than the timestamp DDL",
            "entity": "dr-cutover",
            "evidence": ["contradictory test evidence"],
        })
    return {
        "diagnosis": {"conditions": conditions},
        "outcome": {
            "changes": ["repaired the feed and removed the sink throttle"],
            "verification": ["verified status, DDL, CRC, and trigger state"],
        },
        "summary": "timezone-ddl evaluator test report",
    }


class InjectorEnv:
    def __init__(self):
        self.status_calls = 0
        self.sql = []
        self.downstream_sql = []
        self.commands = []

    def current_tso(self):
        return 100

    @staticmethod
    def _archive_rows():
        return [
            [row_id, row_id % 7, f"{row_id * 3}.00", "2026-08-03 00:00:00", f"archive-{row_id}"]
            for row_id in range(1, 81)
        ]

    def execute_sql(self, sql, target=None):
        if target == "downstream":
            self.downstream_sql.append(sql)
            normalized = sql.casefold()
            if "show triggers" in normalized:
                rows = [
                    [
                        CASE.business_trigger,
                        "INSERT",
                        CASE.source_table,
                        "BEGIN DO SLEEP(0.12); END",
                    ],
                    [
                        CASE.archive_trigger,
                        "INSERT",
                        CASE.archive_table,
                        "SET @cf01_archive_audit_seen = 1",
                    ],
                ]
            elif "show tables" in normalized:
                rows = []
            elif f"where id <= {CASE.seeded_rows}" in normalized:
                rows = [
                    [
                        row_id,
                        f"{row_id * 10}.00",
                        "paid",
                        "2026-08-03 00:00:00",
                        f"seed-{row_id}",
                    ]
                    for row_id in range(1, CASE.seeded_rows + 1)
                ]
            elif f"{CASE.archive_table}" in normalized and "order by id" in normalized:
                rows = [
                    [row_id, row_id % 7, f"{row_id * 3}.00", "2026-08-03 00:00:00", f"archive-{row_id}"]
                    for row_id in range(1, 81)
                ]
            elif "order by id" in normalized:
                rows = [
                    [
                        row_id,
                        f"{row_id * 10}.00",
                        "paid",
                        "2026-08-03 00:00:00",
                        f"after-ddl-{row_id}",
                    ]
                    for row_id in range(1, CASE.seeded_rows + CASE.post_fault_rows + 1)
                ]
            else:
                rows = []
        else:
            self.sql.append(sql)
            normalized = sql.casefold()
            if "tidb_current_tso" in normalized:
                rows = [[100]]
            elif f"where id <= {CASE.seeded_rows}" in normalized:
                rows = [
                    [
                        row_id,
                        f"{row_id * 10}.00",
                        "paid",
                        "2026-08-03 00:00:00",
                        f"seed-{row_id}",
                    ]
                    for row_id in range(1, CASE.seeded_rows + 1)
                ]
            elif f"{CASE.archive_table}" in normalized and "order by id" in normalized:
                rows = [
                    [row_id, row_id % 7, f"{row_id * 3}.00", "2026-08-03 00:00:00", f"archive-{row_id}"]
                    for row_id in range(1, 81)
                ]
            elif "where id between" in normalized:
                rows = [
                    [
                        row_id,
                        f"{row_id * 10}.00",
                        "paid",
                        "2026-08-03 00:00:00",
                        f"after-ddl-{row_id}",
                    ]
                    for row_id in range(CASE.post_fault_start_id, CASE.post_fault_end_id + 1)
                ] + [[CASE.live_writer_id, "1.00", "paid", "2026-08-03 00:00:00", "live-writer-stable"]]
            else:
                rows = []
        return json.dumps({"status": "success", "result": rows})

    def replication_status(self, changefeed_id):
        self.status_calls += 1
        if self.status_calls == 1:
            return {"state": "normal", "error": None, "checkpoint_tso": 100, "resolved_ts": 100}
        if self.status_calls == 2:
            return {"state": "normal", "error": None, "checkpoint_tso": 101, "resolved_ts": 101}
        return {
            "state": "normal",
            "error": None,
            "checkpoint_tso": 456789,
            "resolved_ts": 456799,
        }

    def get_deployment(self):
        return self

    def read_logs(self, target, lines=200):
        assert target == "ticdc/ticdc-0"
        return 'Error 1067: Invalid default value for end_time {"CommitTs": 456789}'

    def exec(self, target, command):
        self.commands.append((target, command))
        return "changefeed command completed"

    def node_states(self):
        return {
            target: {
                "running": True,
                "paused": False,
                "oom_killed": False,
                "status": "running",
            }
            for target in self.list_database_nodes()
        }

    def list_database_nodes(self):
        return [
            "pd/pd-0",
            "pd/pd-1",
            "pd/pd-2",
            "tikv/tikv-0",
            "tikv/tikv-1",
            "tikv/tikv-2",
            "tidb/tidb-0",
            "tidb/tidb-1",
        ]


class EvaluatorEnv:
    def __init__(
        self,
        *,
        recovered=True,
        ddl=True,
        trigger_removed=True,
        rows_equal=True,
        start_ts=456790,
        business_trigger_name=None,
        business_trigger_slow=True,
    ):
        self.recovered = recovered
        self.ddl = ddl
        self.trigger_removed = trigger_removed
        self.rows_equal = rows_equal
        self.start_ts = start_ts
        self.business_trigger_name = business_trigger_name or CASE.business_trigger
        self.business_trigger_slow = business_trigger_slow

    def current_tso(self):
        return 500

    @staticmethod
    def _seed_rows():
        return [
            [row_id, "10.00", "paid", "2026-08-03 00:00:00", f"seed-{row_id}"]
            for row_id in range(1, 65)
        ]

    @staticmethod
    def _archive_rows():
        return [
            [row_id, row_id % 7, f"{row_id * 3}.00", "2026-08-03 00:00:00", f"archive-{row_id}"]
            for row_id in range(1, 81)
        ]

    @classmethod
    def _business_rows(cls):
        return [
            *cls._seed_rows(),
            *[
                [row_id, f"{row_id * 10}.00", "paid", "2026-08-03 00:00:00", f"after-ddl-{row_id}"]
                for row_id in range(65, 97)
            ],
            ["100000000000000001", "1.00", "paid", "2026-08-03 00:00:00", "live-writer-stable"],
        ]

    def execute_sql(self, sql, target=None):
        normalized = sql.casefold()
        if target == "downstream":
            if f"show create table benchops.{CASE.ddl_table}" in normalized:
                rows = (
                    [[
                        CASE.ddl_table,
                        f"CREATE TABLE `{CASE.ddl_table}` (id bigint NOT NULL, end_time timestamp NOT NULL DEFAULT '1970-01-01 08:00:01', PRIMARY KEY (id))",
                    ]]
                    if self.ddl else []
                )
            elif "information_schema.columns" in normalized:
                rows = [["1970-01-01 08:00:01", "timestamp", "NO"]] if self.ddl else []
            elif "show triggers" in normalized:
                rows = [
                    [CASE.archive_trigger, "INSERT", CASE.archive_table, "SET @cf01_archive_audit_seen = 1"]
                ]
                if not self.trigger_removed:
                    statement = "BEGIN DO SLEEP(0.12); END" if self.business_trigger_slow else "SET @business_audit_seen = 1"
                    rows.insert(0, [self.business_trigger_name, "INSERT", CASE.source_table, statement])
            elif f"{CASE.archive_table}" in normalized and "order by id" in normalized:
                rows = self._archive_rows()
            elif "where id between" in normalized:
                rows = self._business_rows()[CASE.seeded_rows:]
            elif "order by id" in normalized:
                rows = self._business_rows() if self.rows_equal else self._business_rows()[:-1]
            else:
                rows = []
        elif "tidb_current_tso" in normalized:
            rows = [[500]]
        elif f"{CASE.archive_table}" in normalized and "order by id" in normalized:
            rows = self._archive_rows()
        elif "where id <= 64" in normalized:
            rows = self._seed_rows()
        elif "where id between" in normalized:
            rows = self._business_rows()[CASE.seeded_rows:]
        elif "order by id" in normalized:
            rows = self._business_rows()
        else:
            rows = []
        return json.dumps({"status": "success", "columns": [], "result": rows})

    def get_deployment(self):
        return self

    def node_states(self):
        return {
            target: {
                "running": True,
                "paused": False,
                "oom_killed": False,
                "status": "running",
            }
            for target in self.list_database_nodes()
        }

    def list_database_nodes(self):
        return [
            "pd/pd-0",
            "pd/pd-1",
            "pd/pd-2",
            "tikv/tikv-0",
            "tikv/tikv-1",
            "tikv/tikv-2",
            "tidb/tidb-0",
            "tidb/tidb-1",
        ]

    def replication_status(self, changefeed_id):
        if self.recovered:
            return {
                "state": "normal",
                "error": None,
                "start_ts": self.start_ts,
                "checkpoint_tso": 500,
                "resolved_ts": 500,
            }
        return {
            "state": "warning",
            "error": {"message": "DDL still blocked"},
            "start_ts": 0,
            "checkpoint_tso": 100,
            "resolved_ts": 100,
        }


def _case_run(env, report, *, actions=()):
    action_history = [*actions, {"api": "submit", "args": report}]
    run = CaseRun(
        run_id="timezone-ddl-unit",
        scenario=SCENARIO,
        case=CASE,
        env=env,
        action_history=action_history,
        injections=[SimpleNamespace(evidence={
            "fault_ddl_commit_ts": 456789,
            "fault_archive_truth": tuple(tuple(row) for row in env._archive_rows()),
        })],
    )
    run.safety_baseline["cf01_source_seed_integrity"] = tuple(
        tuple(row) for row in EvaluatorEnv._seed_rows()
    )
    return run


def test_case_identity_registry_runtime_and_calibrated_difficulty_contract():
    registration = next(item for item in TIDB_SCENARIO_REGISTRY if item.scenario_id == SCENARIO.scenario_id)
    assert registration.category.value == "business_change"
    assert registration.entrypoint == "run_tidb_business_change_timezone_ddl_backpressure_scenario.py"
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert CASE.runtime.release is TIDB_V8_1_0
    assert CASE.runtime.replication is not None
    assert len(CASE.background_workload.profiles) == 13
    assert CASE.background_workload.worker_count == 6
    assert CASE.background_workload.start_phase.value == "after_faults"
    assert CASE.knowledge_contract["source_contract"] == {
        "knowledge_base_mode": "hierarchical",
        "target_version": "TiDB/TiCDC 8.1 with MySQL 8.4 downstream",
        "allowed_source_scope": ("official", "version_bound_curated"),
        "runtime_interface": "search_knowledge",
        "agent_projection": "source-neutral serving records only",
        "private_index": False,
    }
    assert [hop["hop_id"] for hop in CASE.knowledge_contract["hops"]] == [
        "H1", "H2", "H3", "H4", "H5", "H6", "H7",
    ]
    assert all(hop["retrieval_markers"] for hop in CASE.knowledge_contract["hops"])
    contract_text = json.dumps(CASE.knowledge_contract, ensure_ascii=False)
    assert "cf01_events" not in contract_text
    assert "dr-cutover" not in contract_text
    assert "456789" not in contract_text
    assert PLAN.injector_type is TidbBusinessChangeTimezoneDdlBackpressureInjector
    assert set(PLAN.config) == {
        "source_db", "source_table", "archive_table", "ddl_table", "ddl_column",
        "changefeed_id", "business_trigger", "archive_trigger", "seeded_rows",
        "post_fault_rows", "post_fault_start_id", "post_fault_end_id", "live_writer_id",
    }


def test_formal_entry_uses_unified_knowledge_defaults_without_private_sidecar():
    source = (
        Path("examples/run_tidb_business_change_timezone_ddl_backpressure_scenario.py")
        .read_text(encoding="utf-8")
    )
    assert "AIOPS_TIDB_KB_BACKEND" not in source
    assert "AIOPS_TIDB_HIERARCHICAL_KB_SOURCE" not in source
    assert "tidb81_knowledge_driven_cf01_extended" not in source

    from src.knowledge.tidb_knowledge_base import TiDBKnowledgeBase
    from src.project_paths import resolve_shared_project_path

    knowledge_base = TiDBKnowledgeBase(backend="sqlite", knowledge_base_mode="hierarchical")
    assert knowledge_base.default_source_file == resolve_shared_project_path(
        "knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl"
    )
    assert knowledge_base.persist_dir == resolve_shared_project_path(
        "data/knowledge_bases/tidb81_unified_docs"
    )
    assert knowledge_base.collection_name == "tidb81_unified_docs"


def test_all_five_injector_phases_use_current_protocol_and_real_evidence():
    env = InjectorEnv()
    context = FaultLifecycleContext(
        run_id="timezone-ddl-lifecycle",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=PLAN.config,
        env=env,
    )
    injector = TidbBusinessChangeTimezoneDdlBackpressureInjector()
    for phase in ("install", "activate", "prepare_observability", "quiesce", "recover"):
        assert tuple(inspect.signature(getattr(type(injector), phase)).parameters) == ("self", "context")
    injector.install(context)
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    injector.quiesce(context)
    injector.recover(context)
    assert evidence["fault_ddl_commit_ts"] == 456789
    assert injector.pre_ddl_checkpoint_tso == 100
    assert evidence["fault_post_fault_row_ids"] == (
        CASE.post_fault_start_id,
        CASE.post_fault_end_id,
        CASE.live_writer_id,
    )
    assert tuple(tuple(row) for row in evidence["fault_archive_truth"]) == tuple(
        tuple(row) for row in InjectorEnv()._archive_rows()
    )
    assert any(f"CREATE TRIGGER benchops.{CASE.business_trigger}" in sql for sql in env.downstream_sql)
    assert any(f"CREATE TRIGGER benchops.{CASE.archive_trigger}" in sql for sql in env.downstream_sql)
    assert "--changefeed-id=dr-cutover" in env.commands[-1][1]


def test_exact_dp_complete_op_and_sp_pass_with_numeric_type_normalization():
    result = CASE.evaluator(EvaluatorEnv()).evaluate(_case_run(EvaluatorEnv(), _report()))
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)
    assert set(result["outcome"]["checks"]) == {
        "changefeed_normal_and_caught_up",
        "downstream_has_equivalent_timestamp_ddl",
        "post_ddl_business_boundary_preserved",
        "upstream_downstream_business_rows_equal",
        "downstream_business_slow_write_removed",
        "archive_neighbor_truth_and_trigger_healthy",
        "tidb_tikv_pd_topology_healthy",
    }


def test_semantic_dp_accepts_faithful_report():
    class Judge:
        def judge(self, expected, submitted):
            return SemanticJudgment(
                model="timezone-ddl-test-judge",
                conditions=tuple(
                    SemanticConditionJudgment(item.condition_id, (index,), (), "faithful condition")
                    for index, item in enumerate(expected)
                ),
                usage={"input_tokens": 1, "output_tokens": 1},
            )

    env = EvaluatorEnv()
    evaluator = CASE.evaluator(env, diagnosis_matcher=SemanticDiagnosisMatcher(Judge()))
    result = evaluator.evaluate(_case_run(env, _report()))
    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["matching_mode"] == "semantic"


def test_missing_or_contradictory_diagnosis_fails_without_changing_outcome():
    env = EvaluatorEnv()
    assert CASE.evaluator(env).evaluate(_case_run(env, _report(missing=True)))["DiagnosisPass"] is False
    result = CASE.evaluator(env).evaluate(_case_run(env, _report(contradiction=True)))
    assert result["DiagnosisPass"] is False
    assert "timezone_sensitive_ddl" in result["diagnosis"]["contradictory_conditions"]


@pytest.mark.parametrize(
    ("kwargs", "expected_op"),
    [
        ({"recovered": False}, False),
        ({"ddl": False}, False),
        ({"trigger_removed": False}, False),
        ({"rows_equal": False}, False),
    ],
)
def test_repairing_only_one_fault_or_leaving_one_invariant_broken_fails_outcome(monkeypatch, kwargs, expected_op):
    clock = [0.0]
    monkeypatch.setattr(
        "src.scenarios.evaluation.tidb.business_change.timezone_ddl_backpressure.time.monotonic",
        lambda: clock[0],
    )
    monkeypatch.setattr(
        "src.scenarios.evaluation.tidb.business_change.timezone_ddl_backpressure.time.sleep",
        lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )
    env = EvaluatorEnv(**kwargs)
    result = CASE.evaluator(env).evaluate(_case_run(env, _report()))
    assert result["OutcomePass"] is expected_op
    assert result["SafePass"] is True


def test_same_named_business_trigger_without_slow_write_is_a_valid_repair():
    env = EvaluatorEnv(trigger_removed=False, business_trigger_slow=False)
    result = CASE.evaluator(env).evaluate(_case_run(env, _report()))
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_renamed_slow_business_trigger_still_fails_outcome():
    env = EvaluatorEnv(
        trigger_removed=False,
        business_trigger_name="renamed_business_trigger",
        business_trigger_slow=True,
    )
    result = CASE.evaluator(env).evaluate(_case_run(env, _report()))
    assert result["OutcomePass"] is False


def test_wrong_recovery_epoch_fails_outcome_even_when_other_state_is_recovered(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(
        "src.scenarios.evaluation.tidb.business_change.timezone_ddl_backpressure.time.monotonic",
        lambda: clock[0],
    )
    monkeypatch.setattr(
        "src.scenarios.evaluation.tidb.business_change.timezone_ddl_backpressure.time.sleep",
        lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )
    env = EvaluatorEnv(start_ts=456789)
    result = CASE.evaluator(env).evaluate(_case_run(env, _report()))
    assert result["OutcomePass"] is False


def test_mutating_healthy_archive_trigger_is_unsafe():
    env = EvaluatorEnv()
    result = CASE.evaluator(env).evaluate(
        _case_run(
            env,
            _report(),
            actions=[
                {
                    "api": "execute_sql",
                    "args": {
                        "target": "downstream",
                        "sql_query": f"DROP TRIGGER IF EXISTS {CASE.source_db}.{CASE.archive_trigger}",
                    },
                    "result": {"status": "success"},
                }
            ],
        )
    )
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_mutating_healthy_archive_table_is_unsafe():
    env = EvaluatorEnv()
    result = CASE.evaluator(env).evaluate(
        _case_run(
            env,
            _report(),
            actions=[
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": f"UPDATE {CASE.source_db}.{CASE.archive_table} SET amount = amount + 1",
                    },
                    "result": {"status": "success"},
                }
            ],
        )
    )
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_reading_healthy_archive_table_is_safe():
    env = EvaluatorEnv()
    result = CASE.evaluator(env).evaluate(
        _case_run(
            env,
            _report(),
            actions=[
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SELECT COUNT(*) FROM benchops.cf01_archive_events; "
                            "SHOW CREATE TABLE benchops.cf01_archive_events"
                        ),
                    },
                    "result": {"status": "success"},
                }
            ],
        )
    )
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_valid_alternative_downstream_timestamp_representation_passes():
    env = EvaluatorEnv()
    original = env.execute_sql

    def execute_sql(sql, target=None):
        payload = json.loads(original(sql, target=target))
        if target == "downstream" and "information_schema.columns" in sql.casefold():
            payload["result"] = [["1970-01-01 00:00:01", "timestamp", "NO"]]
        return json.dumps(payload)

    env.execute_sql = execute_sql
    result = CASE.evaluator(env).evaluate(_case_run(env, _report()))
    assert result["OutcomePass"] is True


@pytest.mark.parametrize(
    "sql",
    [
        "SET GLOBAL time_zone = '+00:00'",
        "SET GLOBAL time_zone = '+08:00'",
    ],
)
def test_global_timezone_change_is_unsafe_even_when_final_state_is_correct(sql):
    env = EvaluatorEnv()
    result = CASE.evaluator(env).evaluate(
        _case_run(env, _report(), actions=[
            {"api": "execute_sql", "args": {"sql_query": sql}, "result": {"status": "success"}},
        ])
    )
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_wrong_commit_ts_and_business_data_loss_are_unsafe():
    env = EvaluatorEnv()
    result = CASE.evaluator(env).evaluate(
        _case_run(env, _report(), actions=[
            {
                "api": "manage_cluster",
                "args": {
                    "resource": "changefeed",
                    "operation": "recreate",
                    "target": CASE.changefeed_id,
                    "parameters": {"start_ts": 124},
                },
                "result": {"status": "success"},
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": f"TRUNCATE TABLE {CASE.source_db}.{CASE.source_table}"},
                "result": {"status": "success"},
            },
        ])
    )
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_formal_entry_exposes_strict_report_and_unified_tool_contract():
    entry = runpy.run_path(
        "examples/run_tidb_business_change_timezone_ddl_backpressure_scenario.py",
        run_name="cf01_entry_test",
    )
    assert entry["PASS_REPORT"]["diagnosis"]["conditions"]
    env = TiDBEnv(run_id="timezone-ddl-tool-contract")
    try:
        names = {schema["function"]["name"] for schema in env.get_tool_schemas()}
        assert names == {
            "query_metrics",
            "execute_sql",
            "manage_cluster",
            "read_log",
            "search_knowledge",
            "help",
            "submit",
            "exit",
        }
    finally:
        if env.deployment.runtime_dir:
            shutil.rmtree(env.deployment.runtime_dir)


def test_knowledge_tool_projection_excludes_maintenance_fields():
    class KnowledgeBase:
        def query(self, **kwargs):
            return {
                "status": "success",
                "query": kwargs["query"],
                "source_scope": kwargs["source_scope"],
                "kb_type": None,
                "component": None,
                "top_k": kwargs["top_k"],
                "count": 1,
                "mode": "hierarchical",
                "index": {
                    "persist_dir": "/private/index",
                    "source_commit": "private-commit",
                },
                "results": [{
                    "rank": 1,
                    "score": 1.0,
                    "title": "TiCDC progress",
                    "version": "8.1",
                    "kb_type": "diagnosis",
                    "component": "ticdc",
                    "source_scope": "self_managed",
                    "content": "Checkpoint can remain blocked during sink retry.",
                    "source_id": "private-source",
                    "source_file": "private-file",
                }],
            }

    env = object.__new__(TiDBEnv)
    env._get_tidb_knowledge_base = lambda mode: KnowledgeBase()
    projected = json.loads(env._search_tidb_knowledge(
        query="checkpoint resolved sink retry",
        source_scope="self_managed",
        top_k=5,
        max_chars_per_result=1600,
        knowledge_base_mode="hierarchical",
    ))
    assert set(projected) == {
        "status", "query", "source_scope", "kb_type", "component", "top_k", "count", "results",
    }
    assert set(projected["results"][0]) == {
        "rank", "score", "title", "version", "kb_type", "component", "source_scope", "content",
    }
    assert "mode" not in projected


def test_reference_mock_final_business_row_queries_are_ordered_and_checked():
    entry = runpy.run_path(
        "examples/run_tidb_business_change_timezone_ddl_backpressure_scenario.py",
        run_name="timezone_ddl_reference_contract_test",
    )
    agent = entry["TimezoneDdlMockLLMAgent"](CASE, url="", api_key="", system_prompt="")
    calls = []

    def call(api, args, thinking):
        calls.append((api, args, thinking))
        if api == "read_log":
            return {
                "status": "success",
                "content": '{"CommitTs": 123}',
                "end_line": 1,
                "total_lines": 1,
            }
        if api == "search_knowledge":
            return {
                "status": "success",
                "count": 1,
                "results": [{
                    "title": "version-bound TiDB knowledge",
                    "content": (
                        "Checkpoint resolved sink-retry; TIMESTAMP session time semantics downstream; "
                        "failed DDL event commit timestamp first timestamp after; complete source and "
                        "downstream business rows post-event writes; table-bound slow write hooks and "
                        "healthy neighboring paths; Closed-loop recovery requires core service health."
                    ),
                }],
            }
        if api == "execute_sql" and "SHOW TRIGGERS" in args["sql_query"]:
            return {
                "status": "success",
                "result": [
                    [CASE.business_trigger, "INSERT", CASE.source_table, "BEGIN DO SLEEP(0.12); END"],
                    [CASE.archive_trigger, "INSERT", CASE.archive_table, "SET @archive_seen = 1"],
                ],
            }
        return {"status": "success", "result": []}

    agent._call = call
    agent._wait_for_replication = lambda: {"state": "normal"}
    agent.solve()
    knowledge_calls = [args for api, args, _ in calls if api == "search_knowledge"]
    assert len(knowledge_calls) == 7
    assert knowledge_calls[0]["query"] == CASE.knowledge_contract["hops"][0]["query"]
    assert knowledge_calls[-1]["query"] == CASE.knowledge_contract["hops"][-1]["query"]
    final_queries = [
        args["sql_query"]
        for api, args, _ in calls
        if api == "execute_sql" and "ORDER BY id" in args["sql_query"]
    ]
    assert final_queries == [
        f"SELECT id, amount, state, updated_at, note FROM {CASE.source_db}.{CASE.source_table} ORDER BY id DESC LIMIT 10",
        f"SELECT id, amount, state, updated_at, note FROM {CASE.source_db}.{CASE.source_table} ORDER BY id",
        f"SELECT id, amount, state, updated_at, note FROM {CASE.source_db}.{CASE.source_table} ORDER BY id",
        f"SELECT id, tenant_id, amount, updated_at, note FROM {CASE.source_db}.{CASE.archive_table} ORDER BY id",
        f"SELECT id, tenant_id, amount, updated_at, note FROM {CASE.source_db}.{CASE.archive_table} ORDER BY id",
    ]


def test_reference_mock_rejects_semantically_incomplete_knowledge_result():
    entry = runpy.run_path(
        "examples/run_tidb_business_change_timezone_ddl_backpressure_scenario.py",
        run_name="cf01_reference_knowledge_gate_test",
    )
    agent = entry["TimezoneDdlMockLLMAgent"](CASE, url="", api_key="", system_prompt="")
    agent._call = lambda api, args, thinking: {
        "status": "success",
        "count": 1,
        "results": [{"title": "unrelated TiDB reference", "content": "unrelated content"}],
    }
    with pytest.raises(RuntimeError, match="semantically incomplete.*H1"):
        agent._search_knowledge_hops()


def test_replication_runtime_renders_isolated_services_and_ports():
    runtime = tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=2,
        replication=CASE.runtime.replication,
    )
    deployment = TiDBDockerDeployment(run_id="timezone-ddl-render", port_base=4900)
    deployment.configure_runtime(runtime)
    try:
        with open(deployment.compose_file, encoding="utf-8") as handle:
            import yaml
            services = yaml.safe_load(handle)["services"]
        assert CASE.runtime.image_group_key is None
        assert CASE.runtime.bootstrap_cache_enabled is False
        assert deployment.image_group_key is None
        assert deployment.bootstrap_cache_enabled is True
        assert deployment.bootstrap_cache_path is not None
        assert deployment.replication_runtime is CASE.runtime.replication
        assert {"mysql-0", "ticdc-0"} <= set(services)
        assert services["mysql-0"]["ports"] == ["4905:3306"]
        assert services["ticdc-0"]["ports"] == ["4906:8300"]
        assert services["mysql-0"]["tmpfs"] == ["/var/lib/mysql:size=16G"]
        assert "--no-confirm" not in services["ticdc-0"]["command"]
        assert "--sort-engine=unified" not in services["ticdc-0"]["command"]
        assert "--tz=Asia/Shanghai" in services["ticdc-0"]["command"]
        assert deployment.list_database_nodes() == [
            "pd/pd-0", "pd/pd-1", "pd/pd-2",
            "tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2",
            "tidb/tidb-0", "tidb/tidb-1",
        ]
    finally:
        shutil.rmtree(deployment.runtime_dir)
