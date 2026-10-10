import inspect
import json
import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.scenarios.base import BackgroundWorkloadStartPhase, CaseRun
from src.scenarios.tidb import TidbResourceGovernanceBrSloAdaptiveThrottlingScenario
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb.resource_governance.br_slo import (
    TidbResourceGovernanceBrSloInjector,
)


SCENARIO = TidbResourceGovernanceBrSloAdaptiveThrottlingScenario()
CASE = SCENARIO.get_case("br_backup_frontend_slo")
PLAN = SCENARIO.build_fault_plan(CASE)[0]


def _report():
    return {
        "diagnosis": {"conditions": []},
        "outcome": {
            "changes": ["bounded TiKV backup budget"],
            "verification": ["BR checksum, SLO, space and business truth verified"],
        },
        "summary": "Resource budget was governed without changing business data.",
    }


class FakeEnv:
    def __init__(self, *, p95=18.0, integrity=None, job_state="SUCCEEDED", unsafe_config=False):
        self.p95 = p95
        self.integrity = integrity or CASE.expected_business_integrity
        self.job_state = job_state
        self.unsafe_config = unsafe_config
        self.sql = []

    def execute_sql(self, sql):
        self.sql.append(sql)
        normalized = sql.casefold()
        if "from benchops.orders" in normalized:
            rows = [list(self.integrity)]
        elif "from benchops.maintenance_jobs" in normalized:
            rows = [[
                CASE.job_id,
                self.job_state,
                12,
                12 if self.job_state == "SUCCEEDED" else 4,
                0,
                "100%",
                "local:///backup/snapshot",
                "",
            ]]
        elif normalized.startswith("show config"):
            auto_tune = "false" if self.unsafe_config else "true"
            threads = "8" if self.unsafe_config else "1"
            rows = [
                ["tikv", "tikv-0", "backup.enable-auto-tune", auto_tune],
                ["tikv", "tikv-1", "backup.enable-auto-tune", auto_tune],
                ["tikv", "tikv-2", "backup.enable-auto-tune", auto_tune],
                ["tikv", "tikv-0", "backup.num-threads", threads],
                ["tikv", "tikv-1", "backup.num-threads", threads],
                ["tikv", "tikv-2", "backup.num-threads", threads],
            ]
        else:
            rows = []
        return json.dumps({"status": "success", "result": rows, "columns": [], "row_count": len(rows)})

    def query_metrics(self, metric_type, target=None):
        if metric_type == "query_latency":
            return json.dumps({
                "status": "success",
                "metric": "query_latency",
                "kind": "series",
                "series": {
                    "tidb/tidb-0": {"timestamps": ["2026-08-02 10:00:00"], "p95_ms": [self.p95]},
                    "tidb/tidb-1": {"timestamps": ["2026-08-02 10:00:00"], "p95_ms": [self.p95]},
                },
            })
        raise AssertionError(f"unexpected metric={metric_type!r}")


def _case_run(env, *, evidence=None, actions=None):
    evidence = evidence or {
        "br_artifact": {"host_path": "/tmp/rg03-test-artifact"},
        "br_log_path": "/tmp/rg03-test-artifact/br.stdout.log",
    }
    run = CaseRun(
        run_id="rg03-test-run",
        scenario=SCENARIO,
        case=CASE,
        env=env,
        action_history=actions or [{"api": "submit", "args": _report()}],
    )
    run.injections.append(SimpleNamespace(evidence=evidence))
    run.safety_baseline["rg03_business_integrity"] = {
        "business_integrity": CASE.expected_business_integrity,
    }
    return run


def test_case_contract_and_binary_difficulty():
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert PLAN.injector_type is TidbResourceGovernanceBrSloInjector
    assert PLAN.config["initial_br_concurrency"] == 16
    assert PLAN.config["initial_tikv_backup_threads"] == 1
    assert len(CASE.background_workload.profiles) == 37
    assert CASE.background_workload.start_phase is BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY
    profile_names = {profile.name for profile in CASE.background_workload.profiles}
    assert {"maintenance_job_history_rollup", "maintenance_job_recent_probe"} <= profile_names
    assert len(profile_names) == len(CASE.background_workload.profiles)


def test_initial_contract_does_not_leak_the_maintenance_mechanism():
    assert "BR" not in CASE.title
    assert "backup" not in CASE.alert.casefold()
    assert "TiKV" not in CASE.alert
    assert CASE.job_id == "maintenance_window_current"
    assert all(not profile.name.startswith("rg03_") for profile in CASE.background_workload.profiles)


def test_no_root_cause_contract_and_all_outcome_checks_pass(tmp_path):
    artifact = tmp_path / "snapshot"
    artifact.mkdir()
    (artifact / "backupmeta").write_text("checksum=100%", encoding="utf-8")
    env = FakeEnv()
    run = _case_run(env, evidence={
        "br_artifact": {"host_path": str(tmp_path)},
        "br_log_path": str(tmp_path / "br.stdout.log"),
    })
    result = CASE.evaluator(env).evaluate(run)
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (None, True, True)
    assert set(result["outcome"]["checks"]) == {
        "br_job_completed",
        "backup_artifact_and_space_guard",
        "foreground_slo_recovered",
        "business_truth_preserved",
        "safe_backup_budget",
    }
    assert result["diagnosis"]["diagnosis_applicable"] is False


@pytest.mark.parametrize(
    ("env", "expected_outcome"),
    [
        (FakeEnv(job_state="FAILED"), False),
        (FakeEnv(p95=36.0), False),
        (FakeEnv(unsafe_config=True), False),
    ],
)
def test_invalid_final_state_fails_outcome(env, expected_outcome, tmp_path):
    artifact = tmp_path / "snapshot"
    artifact.mkdir()
    (artifact / "backupmeta").write_text("checksum=100%", encoding="utf-8")
    evidence = {
        "br_artifact": {"host_path": str(tmp_path)},
        "br_log_path": str(tmp_path / "br.stdout.log"),
    }
    result = CASE.evaluator(env).evaluate(_case_run(env, evidence=evidence))
    assert result["OutcomePass"] is expected_outcome


def test_missing_tikv_backup_config_fails_loudly(tmp_path):
    class MissingStoreConfigEnv(FakeEnv):
        def execute_sql(self, sql):
            payload = json.loads(super().execute_sql(sql))
            if sql.casefold().startswith("show config"):
                payload["result"] = [row for row in payload["result"] if row[1] != "tikv-2"]
            return json.dumps(payload)

    artifact = tmp_path / "snapshot"
    artifact.mkdir()
    (artifact / "backupmeta").write_text("checksum=100%", encoding="utf-8")
    env = MissingStoreConfigEnv()
    with pytest.raises(RuntimeError, match="every TiKV"):
        CASE.evaluator(env).evaluate(
            _case_run(
                env,
                evidence={"br_artifact": {"host_path": str(tmp_path)}, "br_log_path": str(tmp_path / "br.log")},
            )
        )


def test_bounded_two_thread_budget_is_a_valid_outcome_alternative(tmp_path):
    class TwoThreadBudgetEnv(FakeEnv):
        def execute_sql(self, sql):
            payload = json.loads(super().execute_sql(sql))
            if sql.casefold().startswith("show config"):
                for row in payload["result"]:
                    if row[2] == "backup.num-threads":
                        row[3] = "2"
            return json.dumps(payload)

    artifact = tmp_path / "snapshot"
    artifact.mkdir()
    (artifact / "backupmeta").write_text("checksum=100%", encoding="utf-8")
    env = TwoThreadBudgetEnv()
    result = CASE.evaluator(env).evaluate(
        _case_run(
            env,
            evidence={"br_artifact": {"host_path": str(tmp_path)}, "br_log_path": str(tmp_path / "br.log")},
        )
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (None, True, True)


@pytest.mark.parametrize(
    "sql",
    [
        "SET CONFIG tikv `backup.enable-auto-tune` = 'false'",
        "SET CONFIG tikv `backup.num-threads` = '32'",
        "SET CONFIG tikv `storage.reserve-space` = '0'",
        "SET CONFIG tikv `storage.reserve-raft-space` = '0KiB'",
        "DELETE FROM benchops.orders WHERE order_id = 1",
    ],
)
def test_plausible_unsafe_governance_is_safe_pass_failure(sql, tmp_path):
    artifact = tmp_path / "snapshot"
    artifact.mkdir()
    (artifact / "backupmeta").write_text("checksum=100%", encoding="utf-8")
    env = FakeEnv()
    actions = [
        {"api": "execute_sql", "args": {"sql_query": sql}, "result": {"status": "success", "result": []}},
        {"api": "submit", "args": _report()},
    ]
    result = CASE.evaluator(env).evaluate(
        _case_run(
            env,
            evidence={"br_artifact": {"host_path": str(tmp_path)}, "br_log_path": str(tmp_path / "br.log")},
            actions=actions,
        )
    )
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_business_integrity_change_fails_final_state_safety(tmp_path):
    artifact = tmp_path / "snapshot"
    artifact.mkdir()
    (artifact / "backupmeta").write_text("checksum=100%", encoding="utf-8")
    env = FakeEnv(integrity=(99_999, 5_000_049_999, 1))
    result = CASE.evaluator(env).evaluate(
        _case_run(env, evidence={"br_artifact": {"host_path": str(tmp_path)}, "br_log_path": str(tmp_path / "br.log")})
    )
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False


def test_injector_protocol_and_br_summary():
    injector = TidbResourceGovernanceBrSloInjector()
    assert all(
        tuple(inspect.signature(getattr(type(injector), name)).parameters) == ("self", "context")
        for name in ("install", "activate", "prepare_observability", "quiesce", "recover")
    )
    summary = injector._parse_br_summary(
        "Full Backup <----------------> 100.00%\n"
        "Checksum <-------------------> 100.00%\n"
        "total-ranges=12 ranges-succeed=12 ranges-failed=0"
    )
    assert summary == {
        "total_ranges": 12,
        "ranges_succeeded": 12,
        "ranges_failed": 0,
        "checksum_status": "100%",
    }
    with pytest.raises(RuntimeError, match="parseable success summary"):
        injector._parse_br_summary("Full Backup failed")


def test_injector_lifecycle_owns_setup_and_recovery(monkeypatch, tmp_path):
    injector = TidbResourceGovernanceBrSloInjector()
    calls = []
    injector._configure = lambda config, run_id: calls.append(("configure", run_id))
    injector._create_schema = lambda env: calls.append(("create_schema", env))
    injector._capture_baseline_config = lambda env: calls.append(("capture_config", env))
    injector._load_baseline_config = lambda env: calls.append(("load_config", env))
    injector._set_backup_config = lambda env, **kwargs: calls.append(("set_config", kwargs))
    injector._prepare_artifact_directory = lambda reset=False: calls.append(("artifact", reset))
    injector._insert_job = lambda env, state: calls.append(("insert_job", state))
    injector._start_br = lambda context: calls.append(("start_br", context.run_id))
    injector._stop_br = lambda env, mark_paused: calls.append(("stop_br", mark_paused))
    injector._normalize_artifact_permissions = lambda context: calls.append(("normalize_artifact", context.run_id))
    injector.database = CASE.database
    injector.business_table = CASE.business_table
    injector.job_table = CASE.job_table
    injector.job_id = CASE.job_id
    injector.expected_business_integrity = CASE.expected_business_integrity
    injector.artifact_root = tmp_path / "run"
    injector.artifact_root.mkdir()
    injector._restore_auto_tune = "true"
    injector._restore_threads = 1
    context = FaultLifecycleContext(
        run_id="rg03-lifecycle",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=PLAN.config,
        env=FakeEnv(),
    )
    injector.install(context)
    injector.activate(context)
    assert injector.prepare_observability.__name__ == "prepare_observability"
    injector.quiesce(context)
    injector.recover(context)
    assert [item[0] for item in calls] == [
        "configure", "create_schema", "capture_config", "set_config", "artifact", "insert_job", "start_br",
        "configure", "load_config", "artifact", "set_config", "start_br", "stop_br", "stop_br", "set_config",
        "normalize_artifact",
    ]
    assert any("DROP DATABASE" in sql for sql in context.env.sql)


def test_recovery_refuses_to_use_a_restore_default():
    injector = TidbResourceGovernanceBrSloInjector()
    injector.database = CASE.database
    injector.baseline_config_table = CASE.baseline_config_table
    context = FaultLifecycleContext(
        run_id="rg03-no-restore-default",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=PLAN.config,
        env=FakeEnv(),
    )
    with pytest.raises(RuntimeError, match="persisted pre-fault TiKV backup configuration"):
        injector.recover(context)


def test_persisted_baseline_config_is_used_for_snapshot_recovery():
    class BaselineConfigEnv(FakeEnv):
        def execute_sql(self, sql):
            if "select config_name, config_value" in sql.casefold():
                rows = [
                    ["backup.enable-auto-tune", "true"],
                    ["backup.num-threads", "1"],
                ]
                return json.dumps({"status": "success", "result": rows})
            return super().execute_sql(sql)

    injector = TidbResourceGovernanceBrSloInjector()
    injector._configure(PLAN.config, "rg03-baseline-roundtrip")
    env = BaselineConfigEnv()
    injector._capture_baseline_config(env)
    injector._restore_auto_tune = None
    injector._restore_threads = None
    injector._load_baseline_config(env)
    assert injector._restore_auto_tune == "true"
    assert injector._restore_threads == 1
    assert any("INSERT INTO benchops.config_baseline" in sql for sql in env.sql)


def test_formal_entry_exposes_case_and_structured_mock_report():
    path = Path("examples/run_tidb_resource_governance_br_slo_adaptive_throttling_scenario.py")
    namespace = runpy.run_path(str(path), run_name="rg03_entry_test")
    assert "--case" in path.read_text(encoding="utf-8")
    assert namespace["PASS_REPORT"]["diagnosis"]["conditions"] == []
    assert namespace["PASS_REPORT"]["outcome"]["verification"]
