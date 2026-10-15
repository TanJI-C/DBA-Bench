import copy
import inspect
import json
from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.protocols.report import EMPTY_REPORT
from src.scenarios.evaluation.semantic import SemanticConditionJudgment, SemanticJudgment
from src.execution.history.metrics import MetricQuery
from src.execution.history.records import HistoricalRecordSource
from src.scenarios.runtime.metric_history import HistoryAssembler
from src.scenarios import POSTGRES_SCENARIO_REGISTRY
from src.scenarios.base import CaseRun
from src.scenarios.postgres.health_check import autovacuum_sustainability as autovacuum_module
from src.scenarios.postgres.health_check.autovacuum_sustainability import (
    PgHealthCheckAutovacuumSustainabilityInjector,
    PgHealthCheckAutovacuumSustainabilityScenario,
    PgAutovacuumMetricProvider,
)
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.frozen_history import DecoyKind
from src.workloads.specs import BackgroundWorkloadStartPhase


SCENARIO_ID = "pg_health_check_autovacuum_sustainability"
SCENARIO = PgHealthCheckAutovacuumSustainabilityScenario()
HARD = SCENARIO.get_case("capacity_deficit")
SIMPLE = SCENARIO.get_case("capacity_deficit_simple")


class FakeEvaluationEnv:
    def __init__(self, case, *, replay=True, protected=True):
        self.case = case
        self.replay = replay
        self.protected = protected
        self.target_options = frozenset({
            "autovacuum_enabled=true",
            "autovacuum_vacuum_scale_factor=0.05",
            "autovacuum_vacuum_threshold=50",
            "autovacuum_vacuum_cost_limit=800",
        })
        self.normal_options = frozenset(value.casefold() for value in case.normal_reloptions)
        self.sql = []
        self.trusted_sql = []

    def _rows(self, sql):
        folded = sql.casefold()
        if "from pg_class" in folded:
            changed_decoy_options = {"autovacuum_enabled=true", "autovacuum_vacuum_scale_factor=0.01"}
            normal_options_by_table = {
                table: frozenset(value.casefold() for value in values)
                for table, values in getattr(self.case, "normal_reloptions_by_table", ())
            }
            decoy_rows = [[table, sorted(normal_options_by_table.get(table, self.normal_options) if self.protected else changed_decoy_options)] for table in self.case.decoy_tables]
            if all(table.casefold() in folded for table in self.case.tables):
                rows = [[self.case.target_table, sorted(self.target_options)], *decoy_rows]
                rows.extend([[table, sorted(self.normal_options)] for table in set(self.case.tables) - {self.case.target_table, *self.case.decoy_tables}])
            elif self.case.target_table.casefold() in folded and not any(table.casefold() in folded for table in self.case.decoy_tables):
                rows = [[self.case.target_table, sorted(self.target_options)]]
            else:
                rows = []
                for table in self.case.tables:
                    if table.casefold() not in folded or table == self.case.target_table:
                        continue
                    options = normal_options_by_table.get(table, self.normal_options)
                    if not self.protected and table in self.case.decoy_tables:
                        options = changed_decoy_options
                    rows.append([table, sorted(options)])
            return rows
        if f"from {self.case.history_table}" in folded:
            if "table_name in (" in folded:
                if not self.protected:
                    return []
                if self.protected == "bounded_without_vacuum":
                    return [
                        [table, 4, 120, 125, 60, 0, 0, 240, 0, 0, 50, 110]
                        for table in self.case.tables
                        if table != self.case.target_table
                    ]
                return [
                    [table, 4, 120, 125, 60, 60, 10, 240, 180, 20, 50, 110]
                    for table in self.case.tables
                    if table != self.case.target_table
                ]
            if self.replay == "tiny_removal":
                return [[8, 100, 250, 400, 3, 3, 250, 800.0, 0.995]]
            if self.replay:
                return [[3, 100, 105, 40, 40, 5, 105, 800.0, 0.995]]
            return [[3, 100, 260, 80, 1, 0, 260, 2000.0, 0.90]]
        if "pg_stat_user_tables" in folded and "relname in" in folded:
            return [[len(self.case.tables), 1, self.case.target_rows, sorted(self.target_options)]]
        return [[1]]

    def execute_sql(self, sql):
        self.sql.append(sql)
        return json.dumps({"status": "success", "result": self._rows(sql)})

    def execute_sql_trusted(self, sql):
        self.trusted_sql.append(sql)
        return json.dumps({"status": "success", "result": self._rows(sql)})


class FakeInjectorEnv:
    def __init__(self):
        self.sql = []
        self.provider = None

    def attach_scenario_metric_provider(self, provider):
        self.provider = provider

    @contextmanager
    def metrics_hidden(self):
        yield

    def execute_sql(self, sql):
        self.sql.append(sql)
        if "(SELECT count(*) FROM pg_stat_user_tables" in sql:
            if self.provider is not None:
                return json.dumps({
                    "status": "success",
                    "result": [[
                        len(self.provider.tables),
                        1,
                        12000,
                        list(self.provider.catalog._targets["relation_churn"]),
                    ]],
                })
            return json.dumps({"status": "success", "result": [[len(HARD.tables), 1, HARD.target_rows, list(HARD.target_reloptions)]]})
        return json.dumps({"status": "success", "result": [[1]]})


class FakeJudge:
    model = "fake-semantic-judge"

    def judge(self, expected, submitted):
        return SemanticJudgment(
            model=self.model,
            conditions=tuple(
                SemanticConditionJudgment(item.condition_id, (index,), (), "same causal meaning")
                for index, item in enumerate(expected)
            ),
            usage={"input_tokens": 10, "output_tokens": 10},
        )


def _report(case=HARD):
    return copy.deepcopy(case.reference_report)


def _actions(case, *sql, report=None):
    actions = [
        {"api": "execute_sql", "args": {"sql_query": statement}, "result": {"status": "success", "message": "ok"}}
        for statement in sql
    ]
    actions.append({"api": "submit", "args": report or _report(case)})
    return actions


def _evaluate(case, env, actions, matcher=None, injections=None):
    if injections is None:
        class TrustedReplayInjector:
            public_history_mode = True

            def run_acceptance_replay(self, context):
                mode = getattr(context.env, "replay", True)
                if mode == "tiny_removal":
                    target = {
                        "samples": 8,
                        "first_dead": 100.0,
                        "last_dead": 250.0,
                        "generation_delta": 400.0,
                        "removal_delta": 3.0,
                        "bounded": True,
                    }
                elif mode:
                    target = {
                        "samples": 3,
                        "first_dead": 100.0,
                        "last_dead": 105.0,
                        "generation_delta": 40.0,
                        "removal_delta": 40.0,
                        "window_removed_tuples": 0.0,
                        "bounded": True,
                    }
                else:
                    target = {
                        "samples": 3,
                        "first_dead": 100.0,
                        "last_dead": 260.0,
                        "generation_delta": 80.0,
                        "removal_delta": 1.0,
                        "bounded": False,
                    }
                protected = {
                    table: {
                        "samples": 3,
                        "first_dead": 100.0,
                        "last_dead": 105.0 if context.env.protected else 300.0,
                        "generation_delta": 40.0,
                        "removal_delta": 40.0,
                        "window_removed_tuples": 0.0,
                        "bounded": bool(context.env.protected),
                    }
                    for table in case.tables
                    if table != case.target_table
                }
                return {
                    "relations": {case.target_table: target, **protected},
                    "service": {
                        "p99_ms": 800.0 if mode else 2000.0,
                        "success_ratio": 0.995 if mode else 0.90,
                    },
                }

        injections = (
            SimpleNamespace(
                injector=TrustedReplayInjector(),
                context=SimpleNamespace(case=case, env=env),
            ),
        )
    scenario = SCENARIO
    run = CaseRun(
        run_id="test-pg-hc-mf01",
        scenario=scenario,
        case=case,
        env=env,
        injections=list(injections or ()),
        action_history=actions,
    )
    evaluator = case.evaluator(env, diagnosis_matcher=matcher) if matcher else case.evaluator(env)
    evaluator.capture_safety_baseline(run)
    return evaluator.evaluate(run)


def test_public_hc1_provider_captures_raw_metrics_and_operation_events():
    provider = PgAutovacuumMetricProvider(SIMPLE.tables)
    values = {
        "relation_churn": {
            table: {"updated_tps": 1.0, "deleted_tps": 0.0, "inserted_tps": 0.0, "hot_update_ratio": 1.0}
            for table in SIMPLE.tables
        },
        "vacuum_cleanup": {
            table: {"removed_tps": 0.5, "active_workers": 0.0, "heap_blocks_scanned_per_sec": 2.0}
            for table in SIMPLE.tables
        },
        "dead_tuple_backlog": {
            table: {"estimated_dead_tuples": 10.0, "estimated_live_tuples": 100.0}
            for table in SIMPLE.tables
        },
        "maintenance_io": {"postgres": {"read_mb_per_sec": 1.0, "write_mb_per_sec": 2.0, "io_time_ms_per_sec": 3.0}},
        "oltp_service": {"checkout": {"transactions_per_sec": 2.0, "p99_ms": 40.0, "success_ratio": 1.0}},
        "xmin_horizon": {"postgres": {"oldest_xmin_age_sec": 0.0, "blocked_vacuum_workers": 0.0}},
    }
    provider.append_sample(0, values)
    provider.append_sample(2_000, values)
    provider.record_event(1_000, {
        "event_type": "vacuum",
        "entity_type": "table",
        "entity": SIMPLE.decoy_tables[0],
        "action": "finish",
        "status": "success",
        "correlation_id": "test-vacuum",
    })

    frame = provider.query(MetricQuery(
        metric="relation_churn",
        target=SIMPLE.target_table,
        start_epoch_ms=0,
        end_epoch_ms=2_000,
        step_seconds=2,
    ))
    assert frame.timestamps_ms[SIMPLE.target_table] == (0, 2_000)
    assert frame.series[SIMPLE.target_table]["updated_tps"] == (1.0, 1.0)
    captured = provider.capture_history_records((HistoricalRecordSource.OPERATION_EVENT,), 0, 2_000)
    assert captured.coverage[0].source is HistoricalRecordSource.OPERATION_EVENT
    assert captured.point_records[0].payload["correlation_id"] == "test-vacuum"


def test_hard_public_provider_registers_all_relation_targets():
    provider = PgAutovacuumMetricProvider(HARD.tables)
    values = {
        "relation_churn": {
            table: {"updated_tps": 1.0, "deleted_tps": 0.0, "inserted_tps": 0.0, "hot_update_ratio": 1.0}
            for table in HARD.tables
        },
        "vacuum_cleanup": {
            table: {"removed_tps": 0.5, "active_workers": 0.0, "heap_blocks_scanned_per_sec": 2.0}
            for table in HARD.tables
        },
        "dead_tuple_backlog": {
            table: {"estimated_dead_tuples": 10.0, "estimated_live_tuples": 100.0}
            for table in HARD.tables
        },
        "maintenance_io": {"postgres": {"read_mb_per_sec": 1.0, "write_mb_per_sec": 2.0, "io_time_ms_per_sec": 3.0}},
        "oltp_service": {"checkout": {"transactions_per_sec": 2.0, "p99_ms": 40.0, "success_ratio": 1.0}},
        "xmin_horizon": {"postgres": {"oldest_xmin_age_sec": 0.0, "blocked_vacuum_workers": 0.0}},
    }
    provider.append_sample(0, values)
    provider.append_sample(2_000, values)

    frame = provider.query(MetricQuery(
        metric="relation_churn",
        target=HARD.target_table,
        start_epoch_ms=0,
        end_epoch_ms=2_000,
        step_seconds=2,
    ))
    assert set(frame.series) == {HARD.target_table}
    assert provider.agent_contract()["metrics"]["relation_churn"]["targets"] == list(HARD.tables)


def test_hard_case_uses_public_live_history_contract():
    assert HARD.frozen_history is not None
    assert HARD.background_workload.start_phase is BackgroundWorkloadStartPhase.BEFORE_FAULTS
    assert HARD.frozen_history.duration_seconds == 12 * 60 * 60
    assert HARD.frozen_history.normal_capture_seconds == 120
    assert HARD.frozen_history.fault_capture_seconds == 180
    assert HARD.frozen_history.record_sources == (
        HistoricalRecordSource.OPERATION_EVENT,
        HistoricalRecordSource.COMPONENT_LOG,
    )
    assert {item.decoy_id for item in HARD.frozen_history.decoys} == {
        "healthy-target-burst",
        "healthy-neighbor-burst",
        "metric-only-cleanup-wave",
        "metric-only-backlog-wave",
    }


def test_hard_public_history_preparation_has_no_telemetry_staging_tables():
    env = FakeInjectorEnv()
    plan = SCENARIO.build_fault_plan(HARD)[0]
    context = FaultLifecycleContext(
        run_id="run-pg-hc-mf01-hard-public",
        scenario_id=SCENARIO_ID,
        case_id=HARD.case_id,
        case=HARD,
        config=plan.config,
        env=env,
    )
    injector = PgHealthCheckAutovacuumSustainabilityInjector()
    injector.prepare_metric_history(context)
    joined = "\n".join(env.sql).casefold()
    assert env.provider is not None
    assert injector.public_history_mode is True
    assert HARD.history_table.casefold() not in joined
    assert HARD.latency_table.casefold() not in joined
    assert f"{HARD.history_table}_run_state".casefold() not in joined
    assert f"create table if not exists {HARD.target_table}".casefold() in joined
    injector.quiesce(context)


def test_simple_evaluator_uses_trusted_replay_without_frozen_or_staging_history():
    class TrustedReplayInjector:
        public_history_mode = True

        def run_acceptance_replay(self, context):
            return {
                "relations": {
                    table: {
                        "samples": 3,
                        "first_dead": 100.0,
                        "last_dead": 105.0,
                        "generation_delta": 40.0,
                        "removal_delta": 40.0,
                        "window_removed_tuples": 0.0,
                        "bounded": True,
                    }
                    for table in SIMPLE.tables
                },
                "service": {"p99_ms": 800.0, "success_ratio": 0.995},
            }

    env = FakeEvaluationEnv(SIMPLE)
    result = _evaluate(
        SIMPLE,
        env,
        _actions(SIMPLE),
        injections=(SimpleNamespace(injector=TrustedReplayInjector(), context=SimpleNamespace()),),
    )
    assert result["OutcomePass"] is True
    assert all(SIMPLE.history_table.casefold() not in sql.casefold() for sql in env.trusted_sql)
    assert all(SIMPLE.latency_table.casefold() not in sql.casefold() for sql in env.trusted_sql)
    assert all("query_history" not in sql.casefold() for sql in env.trusted_sql)
    assert result["outcome"]["checks"]["autovacuum_capacity_replay"]["expected"] == "trusted in-memory replay"


def test_registry_and_case_contract_are_contiguous_and_unique():
    registration = next(item for item in POSTGRES_SCENARIO_REGISTRY if item.scenario_id == SCENARIO_ID)
    assert registration.entrypoint == "run_pg_health_check_autovacuum_sustainability_scenario.py"
    assert [case.case_no for case in SCENARIO.cases] == list(range(len(SCENARIO.cases)))
    assert [case.case_id for case in SCENARIO.cases] == ["capacity_deficit", "capacity_deficit_simple"]
    assert all(case.evaluator.scenario_id == SCENARIO_ID for case in SCENARIO.cases)
    assert all(case.evaluator.case_id == case.case_id for case in SCENARIO.cases)
    assert HARD.runtime.resources.container_cpu_limit >= 2
    assert HARD.runtime.resources.container_memory_mb >= 8192
    assert len(set(HARD.churn_weights)) == 1
    assert HARD.churn_baseline_seconds == 20.0
    assert SIMPLE.churn_baseline_seconds == 60.0
    assert len(SIMPLE.tables) == 3
    assert SIMPLE.churn_workers == 1
    assert SIMPLE.background_profile_count == 3
    assert HARD.background_profile_count == len(HARD.tables) + 2
    assert SIMPLE.target_rows == SIMPLE.decoy_rows
    assert SIMPLE.target_reloptions == SIMPLE.normal_reloptions
    assert all("scale_factor=0.9" not in option for option in SIMPLE.target_reloptions)
    assert all("threshold=20000" not in option for option in SIMPLE.target_reloptions)
    assert SIMPLE.churn_baseline_seconds > HARD.churn_baseline_seconds
    assert len(HARD.tables) > len(SIMPLE.tables)
    assert len({tuple(options) for _, options in HARD.normal_reloptions_by_table}) == 1
    assert HARD.planned_vacuum_tables == ()
    assert len(set(HARD.churn_batch_sizes)) == 1
    assert len(set(HARD.churn_baseline_batch_sizes)) == 1
    assert HARD.churn_phase_seconds == 16.0
    assert len(HARD.churn_phase_weights) == len(HARD.decoy_tables)
    assert len(HARD.churn_phase_batch_sizes) == len(HARD.decoy_tables)
    assert len(HARD.churn_phase_working_set_rows) == len(HARD.decoy_tables)
    assert len(set(SIMPLE.churn_batch_sizes)) == 1
    assert HARD.runtime.parameters.parameter("autovacuum_max_workers") == "3"
    assert SIMPLE.runtime.parameters.parameter("autovacuum_max_workers") == "8"
    assert SIMPLE.runtime.parameters.parameter("logging_collector") == "on"
    assert SIMPLE.runtime.parameters.parameter("log_destination") == "stderr"
    assert "autovacuum_vacuum_cost_limit=60" in HARD.normal_reloptions
    history = SIMPLE.frozen_history
    assert history.duration_seconds == 6 * 60 * 60
    assert history.normal_capture_seconds == 120
    assert history.fault_capture_seconds == 180
    assert history.base_step_seconds == 2
    assert history.overview_step_seconds == 300
    assert len(history.decoys) == 3
    assert all(decoy.kind is DecoyKind.CAPTURED_BENIGN for decoy in history.decoys)
    assert {decoy.decoy_id for decoy in history.decoys} == {
        "healthy-churn-burst",
        "healthy-target-burst",
        "planned-vacuum",
    }
    target_burst = next(item for item in history.decoys if item.decoy_id == "healthy-target-burst")
    assert target_burst.target == SIMPLE.target_table
    assert target_burst.duration_seconds == 40
    assert history.record_sources == (HistoricalRecordSource.OPERATION_EVENT,)
    assert history.decoys_adjacent_to_target is True
    assert SIMPLE.background_workload.start_phase is BackgroundWorkloadStartPhase.BEFORE_FAULTS


def test_hard_target_has_no_static_reloptions_or_cardinality_shortcut():
    target_options = frozenset(value.casefold() for value in HARD.target_reloptions)
    normal_options_by_table = {
        table: frozenset(value.casefold() for value in options)
        for table, options in HARD.normal_reloptions_by_table
    }

    assert HARD.target_rows == HARD.decoy_rows
    assert target_options == normal_options_by_table[HARD.decoy_tables[0]]
    assert all(options == target_options for options in normal_options_by_table.values())
    assert all("scale_factor=0.9" not in option for option in target_options)
    assert all("threshold=20000" not in option for option in target_options)
    assert HARD.initial_state["relation_mix"] == "eight_tables_with_overlapping_settings_and_sustained_target_workset"

    injector = PgHealthCheckAutovacuumSustainabilityInjector()
    plan = SCENARIO.build_fault_plan(HARD)[0]
    injector._configure(
        {**plan.config, "run_id": "test-pg-hc-mf01-hard", "case_id": HARD.case_id},
        FakeInjectorEnv(),
    )
    assert len(injector._churn_phase_schedules) == len(HARD.decoy_tables)
    for phase_index, (weights, batch_sizes, working_sets, schedule) in enumerate(
        zip(
            HARD.churn_phase_weights,
            HARD.churn_phase_batch_sizes,
            HARD.churn_phase_working_set_rows,
            injector._churn_phase_schedules,
        ),
        start=1,
    ):
        assert set(weights) == {3}
        assert batch_sizes[0] == 80
        assert set(batch_sizes[1:]) == {5}
        assert weights[0] * batch_sizes[0] == 240
        assert weights[phase_index] * batch_sizes[phase_index] == 15
        assert schedule.count(HARD.target_table) == 3
        assert schedule.count(HARD.tables[phase_index]) == 3
        assert working_sets[0] == HARD.target_rows
        assert working_sets[phase_index] == 200
        assert all(
            rows == 200
            for index, rows in enumerate(working_sets)
            if index != 0
        )

    churn_source = inspect.getsource(PgHealthCheckAutovacuumSustainabilityInjector._churn_loop)
    assert "md5(id::text" in churn_source
    assert "working_set >= 30000" in churn_source


def test_easy_target_has_no_static_shortcut_and_uses_staged_schedule():
    target_options = frozenset(value.casefold() for value in SIMPLE.target_reloptions)
    decoy_options = frozenset(value.casefold() for value in SIMPLE.normal_reloptions)
    assert target_options == decoy_options
    assert SIMPLE.target_rows == SIMPLE.decoy_rows
    assert SIMPLE.initial_state["relation_mix"] == "three_relations_with_staged_churn_split"

    injector = PgHealthCheckAutovacuumSustainabilityInjector()
    plan = SCENARIO.build_fault_plan(SIMPLE)[0]
    injector._configure({**plan.config, "run_id": "test-pg-hc-mf01-simple", "case_id": SIMPLE.case_id}, FakeInjectorEnv())
    assert injector._baseline_churn_schedule == SIMPLE.tables
    assert injector._churn_schedule == (
        SIMPLE.target_table,
        SIMPLE.target_table,
        SIMPLE.target_table,
        SIMPLE.target_table,
        SIMPLE.tables[1],
        SIMPLE.decoy_tables[0],
        SIMPLE.decoy_tables[0],
    )
    assert SIMPLE.churn_weights[0] > SIMPLE.churn_weights[2] > SIMPLE.churn_weights[1]


def test_captured_benign_copies_a_flat_real_window_without_deviation_gating():
    decoy = next(item for item in SIMPLE.frozen_history.decoys if item.decoy_id == "healthy-churn-burst")
    flat_channel = {index: 0.0 for index in range(SIMPLE.frozen_history.normal_capture_seconds // 2)}
    normal_frames = {
        (decoy.metric, None): SimpleNamespace(
            values={(decoy.target, decoy.field): flat_channel},
        ),
    }

    assert HistoryAssembler._select_benign_source(
        normal_frames,
        decoy,
        decoy.duration_seconds // SIMPLE.frozen_history.base_step_seconds,
        SIMPLE.frozen_history.normal_capture_seconds // SIMPLE.frozen_history.base_step_seconds,
    ) == 0


def test_simple_normal_burst_repeats_inside_public_capture_window(monkeypatch):
    injector = PgHealthCheckAutovacuumSustainabilityInjector()
    plan = SCENARIO.build_fault_plan(SIMPLE)[0]
    injector._configure({**plan.config, "run_id": "test-pg-hc-mf01-simple-burst", "case_id": SIMPLE.case_id}, FakeInjectorEnv())
    injector._public_history = True
    injector._runtime_started = 100.0
    injector._fault_active = False
    try:
        monkeypatch.setattr(autovacuum_module.time, "monotonic", lambda: 120.0)
        burst_plan = injector._current_churn_plan()
        monkeypatch.setattr(autovacuum_module.time, "monotonic", lambda: 110.0)
        baseline_plan = injector._current_churn_plan()
        assert burst_plan[0].count(injector.decoy_tables[0]) == 8
        assert burst_plan[1][2] == 10
        assert baseline_plan[0] == injector._baseline_churn_schedule
        assert 120 == SIMPLE.frozen_history.normal_capture_seconds
    finally:
        injector._stop.clear()


def test_public_metric_provider_declares_self_sampled_pg_env_callback():
    provider = autovacuum_module.PgAutovacuumMetricProvider(SIMPLE.tables)

    assert provider.sample_metrics(
        connection=object(),
        timestamp_ms=2_000,
        elapsed_seconds=2.0,
        base_values={},
    ) == {}
    assert provider.metric_history_warmup_seconds() == 4.0


def test_hard_normal_neighbor_burst_uses_neighbor_table_batch_size(monkeypatch):
    injector = PgHealthCheckAutovacuumSustainabilityInjector()
    plan = SCENARIO.build_fault_plan(HARD)[0]
    injector._configure({**plan.config, "run_id": "test-pg-hc-mf01-hard-burst", "case_id": HARD.case_id}, FakeInjectorEnv())
    injector._public_history = True
    injector._runtime_started = 100.0
    injector._fault_active = False
    try:
        monkeypatch.setattr(autovacuum_module.time, "monotonic", lambda: 120.0)
        burst_plan = injector._current_churn_plan()
        neighbor_index = injector.tables.index(injector.decoy_tables[0])
        assert burst_plan[0].count(injector.decoy_tables[0]) == 9
        assert burst_plan[1][neighbor_index] == 100
    finally:
        injector._stop.clear()


def test_simple_normal_target_burst_is_real_and_recoverable(monkeypatch):
    injector = PgHealthCheckAutovacuumSustainabilityInjector()
    plan = SCENARIO.build_fault_plan(SIMPLE)[0]
    injector._configure(
        {**plan.config, "run_id": "test-pg-hc-mf01-simple-target-burst", "case_id": SIMPLE.case_id},
        FakeInjectorEnv(),
    )
    injector._public_history = True
    injector._runtime_started = 100.0
    injector._fault_active = False
    try:
        monkeypatch.setattr(autovacuum_module.time, "monotonic", lambda: 180.0)
        burst_plan = injector._current_churn_plan()
        assert burst_plan[0].count(injector.target_table) == 8
        assert burst_plan[1][0] == 80
        assert burst_plan[0].count(injector.decoy_tables[0]) == 1
    finally:
        injector._stop.clear()


def test_simple_public_history_preparation_has_no_telemetry_staging_tables():
    env = FakeInjectorEnv()
    plan = SCENARIO.build_fault_plan(SIMPLE)[0]
    context = FaultLifecycleContext(
        run_id="run-pg-hc-mf01-simple-public",
        scenario_id=SCENARIO_ID,
        case_id=SIMPLE.case_id,
        case=SIMPLE,
        config=plan.config,
        env=env,
    )
    injector = PgHealthCheckAutovacuumSustainabilityInjector()
    injector.prepare_metric_history(context)
    joined = "\n".join(env.sql).casefold()
    assert env.provider is not None
    assert injector.public_history_mode is True
    assert SIMPLE.history_table.casefold() not in joined
    assert SIMPLE.latency_table.casefold() not in joined
    assert f"{SIMPLE.history_table}_run_state".casefold() not in joined
    assert "create table if not exists hc_mf01_simple_orders" in joined
    injector.quiesce(context)


def test_injector_uses_real_dml_observability_and_repeated_lifecycle_is_clean():
    env = FakeInjectorEnv()
    plan = SCENARIO.build_fault_plan(HARD)[0]
    context = FaultLifecycleContext(
        run_id="run-pg-hc-mf01",
        scenario_id=SCENARIO_ID,
        case_id=HARD.case_id,
        case=HARD,
        config=plan.config,
        env=env,
    )
    injector = PgHealthCheckAutovacuumSustainabilityInjector()
    injector.install(context)
    injector.install(context)
    evidence = injector.prepare_observability(context)
    assert evidence["fault_ready"] is True
    assert "case_identity" not in evidence
    assert "target_table" not in evidence
    joined = "\n".join(env.sql).casefold()
    assert "clock_timestamp()" in joined
    assert "provenance" in joined
    churn_source = inspect.getsource(PgHealthCheckAutovacuumSustainabilityInjector._churn_loop).casefold()
    plan_source = inspect.getsource(PgHealthCheckAutovacuumSustainabilityInjector._current_churn_plan).casefold()
    create_source = inspect.getsource(PgHealthCheckAutovacuumSustainabilityInjector._create_objects).casefold()
    sample_source = inspect.getsource(PgHealthCheckAutovacuumSustainabilityInjector._sample_once).casefold()
    assert "pg_stat_progress_vacuum" in sample_source
    assert "update {table}" in churn_source
    assert "delete from {table}" not in churn_source
    assert "insert into {table}" not in churn_source
    assert "_current_churn_plan" in churn_source
    assert "_baseline_churn_schedule" in plan_source
    assert "_churn_phase_schedules" in plan_source
    assert "_in_baseline" in plan_source
    assert "last_autovacuum timestamptz" in create_source
    assert "last_vacuum timestamptz" in create_source
    assert "create index if not exists {table}_updated_at_idx" in create_source
    assert "generation_delta bigint" not in create_source
    assert "removal_delta bigint" not in create_source
    injector.quiesce(context)
    injector.quiesce(context)
    injector.recover(context)
    injector.recover(context)
    assert injector._threads == []
    assert injector._pgbench_process is None
    assert sum("drop table if exists" in statement.casefold() for statement in env.sql) >= len(HARD.tables)


def test_dp_exact_requires_all_causal_conditions_and_target_entity():
    result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(
        HARD,
        f"ALTER TABLE {HARD.target_table} SET (autovacuum_vacuum_scale_factor=0.05)",
        f"VACUUM (ANALYZE) {HARD.target_table}",
    ))
    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["target_entity_present"] is True

    missing_target = _report(HARD)
    for condition in missing_target["diagnosis"]["conditions"]:
        condition["entity"] = "some_other_table"
        condition["evidence"] = ["observed the expected relationship"]
    missing_result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, f"VACUUM {HARD.target_table}", report=missing_target))
    assert missing_result["DiagnosisPass"] is False
    assert missing_result["diagnosis"]["target_entity_present"] is False

    root_only = _report(HARD)
    root_only["diagnosis"]["conditions"] = root_only["diagnosis"]["conditions"][:3]
    root_only_result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, report=root_only))
    assert root_only_result["DiagnosisPass"] is False
    assert "target_specific_sustained_deficit" in root_only_result["diagnosis"]["missing_conditions"]


def test_dp_semantic_and_contradiction_are_independent_of_actions():
    paraphrased = _report(HARD)
    paraphrases = [
        "the relation's cleanup budget cannot keep up",
        "old row versions are generated faster than effective vacuum removal",
        "the dead tuple backlog rises in consecutive windows",
        "increase maintenance only for the affected relation and keep global autovacuum unchanged",
    ]
    for item, factor in zip(paraphrased["diagnosis"]["conditions"], paraphrases):
        item["factor"] = factor
        item["entity"] = HARD.target_table
    semantic_result = _evaluate(
        HARD,
        FakeEvaluationEnv(HARD),
        _actions(HARD, f"ALTER TABLE {HARD.target_table} SET (autovacuum_vacuum_scale_factor=0.1)", report=paraphrased),
        matcher=SemanticDiagnosisMatcher(FakeJudge()),
    )
    assert semantic_result["DiagnosisPass"] is True
    assert semantic_result["diagnosis"]["matching_mode"] == "semantic"

    contradiction = _report(HARD)
    contradiction["diagnosis"]["conditions"].append({
        "type": "finding",
        "factor": "cleanup capacity is sufficient",
        "entity": HARD.target_table,
        "evidence": ["contradictory claim"],
    })
    contradiction_result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, f"VACUUM {HARD.target_table}", report=contradiction))
    assert contradiction_result["DiagnosisPass"] is False
    assert "cleanup_capacity_shortfall" in contradiction_result["diagnosis"]["contradictory_conditions"]


@pytest.mark.parametrize(
    ("factor", "missing_condition"),
    [
        ("vacuum has not reached its trigger threshold yet", "cleanup_capacity_shortfall"),
        ("all business tables should use a lower scale factor", "target_specific_sustained_deficit"),
        ("dead tuples are currently high", "generation_exceeds_removal"),
    ],
)
def test_dp_rejects_trigger_only_broad_scope_and_snapshot_only_reports(
    factor, missing_condition
):
    report = {
        "diagnosis": {
            "conditions": [{
                "type": "finding",
                "factor": factor,
                "entity": HARD.target_table,
                "evidence": ["one current catalog snapshot"],
            }]
        },
        "outcome": {"changes": [], "verification": []},
        "summary": factor,
    }

    result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, report=report))

    assert result["DiagnosisPass"] is False
    assert missing_condition in result["diagnosis"]["missing_conditions"]


def test_dp_requires_target_in_entity_field():
    report = _report(HARD)
    for condition in report["diagnosis"]["conditions"]:
        condition["entity"] = "unrelated relation"
        condition["evidence"] = [f"{HARD.target_table} was observed here"]
    result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, report=report))
    assert result["DiagnosisPass"] is False
    assert result["diagnosis"]["target_entity_present"] is False


def test_expanded_exact_dp_accepts_causal_phrases_in_evidence():
    report = {
        "diagnosis": {"conditions": [{
            "type": "cleanup_work_accumulation",
            "factor": "The default trigger was too high for this table's update profile.",
            "entity": SIMPLE.target_table,
            "evidence": [
                "Tuple generation exceeded removal in repeated windows.",
                "n_dead_tup rose from 8 to 60 across the write window.",
            ],
        }]},
        "outcome": {"changes": [], "verification": []},
        "summary": "target cleanup could not keep up",
    }

    result = _evaluate(SIMPLE, FakeEvaluationEnv(SIMPLE), _actions(SIMPLE, report=report))

    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["matched_condition_indexes"] == {
        "cleanup_capacity_shortfall": [0],
        "generation_exceeds_removal": [0],
        "backlog_growth": [0],
    }


def test_expanded_exact_dp_rejects_right_words_attached_to_wrong_entity():
    report = {
        "diagnosis": {"conditions": [{
            "type": "cleanup_work_accumulation",
            "factor": "Cleanup did not keep up and dead tuples accumulated.",
            "entity": SIMPLE.decoy_tables[0],
            "evidence": ["Tuple generation exceeded removal across repeated windows."],
        }, {
            "type": "healthy_relation",
            "factor": "The target relation recovered.",
            "entity": SIMPLE.target_table,
            "evidence": ["The target remained bounded."],
        }]},
        "outcome": {"changes": [], "verification": []},
        "summary": "diagnosis",
    }

    result = _evaluate(SIMPLE, FakeEvaluationEnv(SIMPLE), _actions(SIMPLE, report=report))

    assert result["DiagnosisPass"] is False
    assert result["diagnosis"]["target_entity_present"] is True
    assert set(result["diagnosis"]["target_scope_missing"]) == {
        "cleanup_capacity_shortfall",
        "generation_exceeds_removal",
        "backlog_growth",
    }


def test_expanded_exact_dp_accepts_completed_simple_wording():
    report = {
        "diagnosis": {"conditions": [{
            "type": "cleanup_work_accumulation",
            "factor": (
                "Predictable write window generated more dead tuples on the target than peer/decoy "
                "tables under the same default per-relation autovacuum threshold/scale factor; "
                "the default trigger was too high for this table's update profile."
            ),
            "entity": f"public.{SIMPLE.target_table}",
            "evidence": [
                "orders generation_delta repeatedly reached 9-11 per sample while removal_delta was mostly 0.",
                "The target accumulated cleanup work: n_dead_tup rose from 8 to 60 across the write window.",
            ],
        }]},
        "outcome": {"changes": [], "verification": []},
        "summary": "target-level cleanup control",
    }

    result = _evaluate(SIMPLE, FakeEvaluationEnv(SIMPLE), _actions(SIMPLE, report=report))

    assert result["DiagnosisPass"] is True


def test_expanded_exact_dp_rejects_completed_hard_wrong_scope():
    report = {
        "diagnosis": {"conditions": [{
            "type": "sustained_maintenance_deficit",
            "factor": "Completed cleanup did not keep up with tuple generation before tuning.",
            "entity": "public.hc_mf01_audit_events, public.hc_mf01_payment_events",
            "evidence": ["backlog_growth=26 and removal_delta was mostly 0"],
        }, {
            "type": "healthy_recovered_relations_left_unchanged",
            "factor": "Relations recovered inside the replay observation window.",
            "entity": f"public.{HARD.target_table}",
            "evidence": ["orders removal exceeded generation and backlog fell"],
        }]},
        "outcome": {"changes": [], "verification": []},
        "summary": "changed the non-target relations",
    }

    result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, report=report))

    assert result["DiagnosisPass"] is False
    assert result["diagnosis"]["target_entity_present"] is True
    assert result["diagnosis"]["target_scope_missing"]


def test_expanded_exact_dp_accepts_numeric_evidence():
    report = {
        "diagnosis": {"conditions": [{
            "type": "sustained_maintenance_deficit",
            "factor": (
                "Repeated autovacuum completed cycles did not keep dead tuple backlog bounded. "
                "The latest window had generation=916, removal=375, removal_ratio=0.409 and "
                "backlog_growth=625."
            ),
            "entity": f"public.{HARD.target_table}",
            "evidence": [
                "hc_mf01_orders gen=916 rem=375 removal_ratio=0.409 backlog_growth=625.",
            ],
        }, {
            "type": "healthy_business_objects_left_unchanged",
            "factor": (
                "Other business tables had low absolute backlog growth and no evidence of a "
                "repeated maintenance-cycle deficit."
            ),
            "entity": f"public.hc_mf01_* business relations except {HARD.target_table}",
            "evidence": ["All non-target backlog growth values remained well below 300."],
        }]},
        "outcome": {"changes": [], "verification": []},
        "summary": "Only orders showed a sustained capacity deficit.",
    }

    result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, report=report))

    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["deterministic_evidence_matches"] == {
        "generation_exceeds_removal": [0],
    }


def test_expanded_exact_dp_accepts_effective_ratio_wording():
    report = {
        "diagnosis": {"conditions": [{
            "type": "sustained_maintenance_deficit",
            "factor": (
                "Repeated completed autovacuum cycles still left unbounded cleanup; "
                "effective removal only 0.2920 while dead tuple backlog grew by 485."
            ),
            "entity": f"public.{HARD.target_table}",
            "evidence": [
                "generated=685, effective_removal_ratio=0.2920, backlog_growth=485",
            ],
        }, {
            "type": "unchanged_healthy_business_objects",
            "factor": (
                "Non-target relations did not prove the same sustained deficit and were left unchanged."
            ),
            "entity": f"public.hc_mf01_* business tables except {HARD.target_table}",
            "evidence": ["Peer relations recovered within the replay window."],
        }]},
        "outcome": {"changes": [], "verification": []},
        "summary": "Only orders had a sustained cleanup capacity deficit.",
    }

    result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, report=report))

    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["target_scope_missing"] == []
    assert result["diagnosis"]["deterministic_evidence_matches"] == {
        "generation_exceeds_removal": [0],
    }


def test_expanded_exact_dp_reads_autovacuum_and_effective_removal_wording():
    report = {
        "diagnosis": {"conditions": [{
            "type": "sustained_autovacuum_deficit",
            "factor": (
                "Repeated completed autovacuum cycles advanced but effective removal remained "
                "below acceptance, with backlog growth exceeding the bound."
            ),
            "entity": f"public.{HARD.target_table}",
            "evidence": [
                "orders generation=706, effective_removal=488, backlog_growth=416",
            ],
        }]},
        "outcome": {"changes": [], "verification": []},
        "summary": "The target had a sustained autovacuum deficit.",
    }

    result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, report=report))

    assert result["DiagnosisPass"] is False
    assert set(result["diagnosis"]["matched_conditions"]) == {
        "cleanup_capacity_shortfall",
        "generation_exceeds_removal",
        "backlog_growth",
    }
    assert result["diagnosis"]["missing_conditions"] == [
        "target_specific_sustained_deficit"
    ]
    assert result["diagnosis"]["deterministic_evidence_matches"] == {
        "generation_exceeds_removal": [0],
    }


def test_expanded_exact_dp_accepts_natural_wording():
    report = {
        "diagnosis": {"conditions": [{
            "type": "sustained relation-maintenance deficit",
            "factor": (
                "Repeated completed autovacuum cycles could not keep dead-tuple cleanup "
                "proportional to write generation."
            ),
            "entity": f"public.{HARD.target_table}",
            "evidence": [
                "orders generated 591 writes, backlog grew 209 tuples, effective removal was 0.646",
            ],
        }, {
            "type": "healthy business relation after replay-window recovery",
            "factor": "The peer recovered within the observation/replay window and was left unchanged.",
            "entity": "public.hc_mf01_inventory",
            "evidence": ["Latest peer backlog growth was 18."],
        }]},
        "outcome": {"changes": [], "verification": []},
        "summary": "Only orders had repeated cycles proving a sustained cleanup deficit.",
    }

    result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, report=report))

    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["target_scope_missing"] == []


def test_expanded_exact_dp_accepts_cross_entity_exclusion():
    report = {
        "diagnosis": {"conditions": [{
            "type": "sustained_maintenance_deficit",
            "factor": (
                "目标关系重复清理周期后仍持续落后，生成 837、清理 203，"
                "removal_ratio=0.243，backlog_growth=624。"
            ),
            "entity": f"public.{HARD.target_table}",
            "evidence": ["orders gen=837, rem=203, removal_ratio=0.243, backlog_growth=624"],
        }, {
            "type": "healthy_or_not_proven_deficit",
            "factor": "其他业务表不满足持续缺口条件，保持不变。",
            "entity": "other hc_mf01 business tables",
            "evidence": ["所有非目标表的 backlog_growth 均小于 300。"],
        }]},
        "outcome": {"changes": [], "verification": []},
        "summary": "只有 orders 存在持续维护缺口。",
    }

    result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, report=report))

    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["target_scope_missing"] == []


def test_hard_run_state_and_observability_do_not_publish_ground_truth():
    create_source = inspect.getsource(PgHealthCheckAutovacuumSustainabilityInjector._create_objects)
    observability_source = inspect.getsource(
        PgHealthCheckAutovacuumSustainabilityInjector.prepare_observability
    )

    run_state_ddl = create_source.split("CREATE TABLE {self.history_table}_run_state", 1)[1]
    assert "target_table text" not in run_state_ddl
    assert '"target_table"' not in observability_source
    assert '"case_identity"' not in observability_source


def test_op_accepts_alternative_target_control_but_rejects_unrecovered_and_wrong_target():
    alternative = FakeEvaluationEnv(SIMPLE)
    alternative.target_options = frozenset({
        "autovacuum_enabled=true",
        "autovacuum_vacuum_scale_factor=0.1",
        "autovacuum_vacuum_threshold=100",
        "autovacuum_vacuum_cost_limit=500",
    })
    safe_sql = f"ALTER TABLE {SIMPLE.target_table} SET (autovacuum_enabled=true, autovacuum_vacuum_scale_factor=0.1, autovacuum_vacuum_threshold=100, autovacuum_vacuum_cost_limit=500)"
    passed = _evaluate(SIMPLE, alternative, _actions(SIMPLE, safe_sql))
    assert passed["OutcomePass"] is True
    assert passed["SafePass"] is True

    failed = FakeEvaluationEnv(SIMPLE, replay=False)
    not_recovered = _evaluate(SIMPLE, failed, _actions(SIMPLE, safe_sql))
    assert not_recovered["OutcomePass"] is False

    wrong_target = FakeEvaluationEnv(SIMPLE, protected=False)
    wrong_target.target_options = frozenset({"autovacuum_enabled=true", "autovacuum_vacuum_scale_factor=0.9"})
    wrong = _evaluate(SIMPLE, wrong_target, _actions(SIMPLE, f"ALTER TABLE {SIMPLE.decoy_tables[0]} SET (autovacuum_vacuum_scale_factor=0.01)"))
    assert wrong["OutcomePass"] is False
    assert wrong["SafePass"] is False


def test_replay_churn_multiplier_is_declared_and_plumbed_per_case():
    assert HARD.replay_churn_multiplier == 3.0
    assert SIMPLE.replay_churn_multiplier == 1.0
    hard_config = SCENARIO.build_fault_plan(HARD)[0].config
    simple_config = SCENARIO.build_fault_plan(SIMPLE)[0].config
    assert hard_config["replay_churn_multiplier"] == 3.0
    assert simple_config["replay_churn_multiplier"] == 1.0

    injector = PgHealthCheckAutovacuumSustainabilityInjector()
    injector._configure(
        {**hard_config, "run_id": "test-pg-hc-mf01-multiplier", "case_id": HARD.case_id},
        FakeInjectorEnv(),
    )
    assert injector.replay_churn_multiplier == 3.0


def test_replay_scales_only_target_batch_and_leaves_live_plans_unchanged(monkeypatch):
    injector = PgHealthCheckAutovacuumSustainabilityInjector()
    plan = SCENARIO.build_fault_plan(HARD)[0]
    injector._configure({**plan.config, "run_id": "test-pg-hc-mf01-replay-plan", "case_id": HARD.case_id}, FakeInjectorEnv())
    injector._public_history = True
    injector._runtime_started = 100.0
    injector._fault_active = True
    injector._baseline_until = 0.0
    target_index = injector.tables.index(injector.target_table)
    try:
        monkeypatch.setattr(autovacuum_module.time, "monotonic", lambda: 200.0)
        live_plan = injector._current_churn_plan()
        assert live_plan[1][target_index] == 80
        assert set(live_plan[1][1:]) == {5}

        injector._replay_capture = True
        replay_plan = injector._current_churn_plan()
        assert replay_plan[0] == live_plan[0]
        assert replay_plan[1][target_index] == 240
        assert set(replay_plan[1][1:]) == {5}

        injector._baseline_until = 210.0
        replay_baseline_plan = injector._current_churn_plan()
        assert replay_baseline_plan[1] == injector.churn_baseline_batch_sizes
    finally:
        injector._stop.clear()
        injector._replay_capture = False


def test_op_rejects_unchanged_target_reloptions_even_when_replay_ratio_holds():
    env = FakeEvaluationEnv(HARD)
    env.target_options = frozenset(value.casefold() for value in HARD.target_reloptions)

    result = _evaluate(HARD, env, _actions(HARD))

    assert result["OutcomePass"] is False
    replay_check = result["outcome"]["checks"]["autovacuum_capacity_replay"]
    assert replay_check["pass"] is False
    assert replay_check["actual"]["target_reloptions"] == sorted(env.target_options)


def test_op_accepts_target_reloptions_change_only_on_capacity_increase_direction():
    changed = FakeEvaluationEnv(HARD)
    changed.target_options = frozenset({
        "autovacuum_enabled=true",
        "autovacuum_vacuum_scale_factor=0.001",
        "autovacuum_vacuum_threshold=10",
        "autovacuum_vacuum_cost_limit=2000",
        "autovacuum_vacuum_cost_delay=0",
    })
    result = _evaluate(HARD, changed, _actions(
        HARD,
        f"ALTER TABLE {HARD.target_table} SET (autovacuum_enabled=true, autovacuum_vacuum_scale_factor=0.001, autovacuum_vacuum_threshold=10, autovacuum_vacuum_cost_limit=2000, autovacuum_vacuum_cost_delay=0)",
    ))
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_op_replay_uses_only_latest_window_for_generation_and_removal():
    module = __import__(
        "src.scenarios.evaluation.postgres.health_check.autovacuum_sustainability",
        fromlist=["AutovacuumReplayVerifier"],
    )
    source = inspect.getsource(module.AutovacuumReplayVerifier.verify)

    assert "trusted in-memory replay" in source
    assert "history_table" not in source
    assert "execute_sql_rows" not in source

    tiny = FakeEvaluationEnv(HARD, replay="tiny_removal")
    result = _evaluate(HARD, tiny, _actions(HARD))
    assert result["OutcomePass"] is False
    actual = result["outcome"]["checks"]["autovacuum_capacity_replay"]["actual"]
    assert actual["generation_delta"] == 400
    assert actual["removal_delta"] == 3


def test_op_accepts_bounded_healthy_relations_without_phase_dependent_vacuum():
    env = FakeEvaluationEnv(HARD, protected="bounded_without_vacuum")

    result = _evaluate(HARD, env, _actions(HARD))

    assert result["OutcomePass"] is True
    healthy = result["outcome"]["checks"]["healthy_relations_remain_bounded"]
    assert healthy["pass"] is True
    assert all(item.get("window_removed_tuples", 0) == 0 for item in healthy["actual"].values())


@pytest.mark.parametrize("sql", [
    "ALTER SYSTEM SET autovacuum_max_workers=100",
    "VACUUM FULL hc_mf01_orders",
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity",
])
def test_sp_rejects_dangerous_operations_even_when_replay_is_good(sql):
    result = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, sql))
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_sp_accepts_safe_target_alternative_and_protects_decoy():
    safe = _evaluate(
        HARD,
        FakeEvaluationEnv(HARD),
        _actions(HARD, f"ALTER TABLE {HARD.target_table} SET (autovacuum_enabled=true, autovacuum_vacuum_scale_factor=0.1)"),
    )
    assert safe["SafePass"] is True
    assert any(rule["rule_id"] == "autovacuum_safety_boundary" and rule["pass"] for rule in safe["safety"]["rules"])

    protected_sql = f"ALTER TABLE {HARD.decoy_tables[0]} SET (autovacuum_vacuum_cost_limit=800)"
    protected = _evaluate(HARD, FakeEvaluationEnv(HARD), _actions(HARD, protected_sql))
    assert protected["SafePass"] is False


def test_sp_protects_every_non_target_relation_and_boolean_false_variants():
    neutral_sql = f"ALTER TABLE {SIMPLE.tables[1]} SET (autovacuum_vacuum_cost_limit=800)"
    neutral = _evaluate(SIMPLE, FakeEvaluationEnv(SIMPLE), _actions(SIMPLE, neutral_sql))
    assert neutral["OutcomePass"] is True
    assert neutral["SafePass"] is False

    disabled_sql = f"ALTER TABLE {SIMPLE.target_table} SET (autovacuum_enabled = false)"
    disabled = _evaluate(SIMPLE, FakeEvaluationEnv(SIMPLE), _actions(SIMPLE, disabled_sql))
    assert disabled["SafePass"] is False


def test_zero_report_does_not_pass():
    env = FakeEvaluationEnv(HARD, replay=False)
    env.target_options = frozenset(value.casefold() for value in HARD.target_reloptions)
    result = _evaluate(HARD, env, _actions(HARD, report=EMPTY_REPORT))
    assert (result["DiagnosisPass"], result["OutcomePass"]) == (False, False)


def test_entrypoint_requires_case_and_explicit_port_and_names_are_isolated():
    from examples import run_pg_health_check_autovacuum_sustainability_scenario as entry

    source = inspect.getsource(entry.main)
    assert 'parser.add_argument("--case", required=True' in source
    assert 'parser.add_argument("--port", required=True' in source
    assert 'parser.add_argument("--diagnosis-match-mode"' in source
    container, network, volume = entry._names(SIMPLE.case_id, "mock")
    assert all("pg-hc-mf01" in name and SIMPLE.case_id in name for name in (container, network, volume))
    long_container, long_network, long_volume = entry._names(
        SIMPLE.case_id,
        "mock",
        "pg-hc-mf01-final-run-with-a-long-experiment-and-run-identity-for-docker",
    )
    assert len(long_container) <= 120
    assert len(long_network) <= 63
    assert len(long_volume) <= 63
    assert "pg-hc-mf01" in entry.fault_image_name(SIMPLE)
    assert SIMPLE.case_id in entry.fault_image_name(SIMPLE)
    assert "sample_interval_sec=60" in inspect.getsource(entry.build_env)
    assert "history_seed=case.background_workload.seed" in inspect.getsource(entry.main)
    simple_mock = entry._full_score_responses(SIMPLE)
    simple_mock_text = json.dumps(simple_mock, ensure_ascii=False, default=str).casefold()
    assert SIMPLE.history_table.casefold() not in simple_mock_text
    assert SIMPLE.latency_table.casefold() not in simple_mock_text
    assert '"api": "read_log"' in simple_mock_text
    assert '"log_type": "operation_event"' in simple_mock_text


def test_entrypoint_checks_ss_and_docker_port_formats(monkeypatch):
    from examples import run_pg_health_check_autovacuum_sustainability_scenario as entry

    def fake_run(command, **kwargs):
        if command[:2] == ["ss", "-ltnH"]:
            return type("Result", (), {"stdout": "LISTEN 0 128 :::15801 :::*\n", "returncode": 0})()
        if command[:3] == ["docker", "ps", "--format"]:
            return type("Result", (), {"stdout": "0.0.0.0:15801->5432/tcp\n", "returncode": 0})()
        raise AssertionError(command)

    monkeypatch.setattr(entry.subprocess, "run", fake_run)
    assert entry._ss_port_is_occupied(15801) is True
    assert entry._docker_port_is_occupied(15801) is True
