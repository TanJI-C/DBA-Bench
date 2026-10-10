import json
import threading
from dataclasses import replace
from types import SimpleNamespace

from src.execution.environment import PGEnv
from src.execution.postgres_metrics import (
    POSTGRES_METRIC_CATALOG,
    PostgresScenarioMetricCatalog,
    postgres_query_metrics_tool_definition,
)
import src.scenarios.postgres.resource_governance.pgbouncer_connection_budget as rg1
from src.execution.history.records import (
    CapturedRecords,
    FrozenHistoricalRecordStore,
    HistoricalCoverage,
    HistoricalPointRecord,
    HistoricalRecordSource,
)
from src.scenarios.postgres.resource_governance.pgbouncer_connection_budget import (
    PgBouncerMetricHistoryProvider,
    PgResourceGovernancePgbouncerConnectionBudgetScenario,
)


BASE_MS = 1_700_000_000_000


def _provider():
    case = PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case("pool_partition_shortage")
    env = SimpleNamespace()
    provider = PgBouncerMetricHistoryProvider(env, case)
    provider._samples[("pgbouncer_pool_clients", "testdb/checkout_user")] = [
        (BASE_MS, {"cl_active": 1.0, "cl_waiting": 0.0, "maxwait_sec": 0.0}),
        (BASE_MS + 2_000, {"cl_active": 2.0, "cl_waiting": 3.0, "maxwait_sec": 1.5}),
    ]
    return case, provider


def test_rg1_case_uses_frozen_history_without_root_cause_leak():
    case, provider = _provider()

    assert case.evaluator.diagnosis_applicable is False
    assert case.public_sql_protected_relations == (
        "rg_pgbouncer_etl_stage",
        "rg_pgbouncer_etl_target",
    )
    assert "root_cause" not in case.initial_state
    assert case.background_workload.start_phase.value == "before_faults"
    assert case.frozen_history is not None
    assert set(case.frozen_history.required_metrics) == set(provider.metric_names)
    assert HistoricalRecordSource.OPERATION_EVENT in case.frozen_history.record_sources
    assert {decoy.kind.value for decoy in case.frozen_history.decoys} == {"captured_benign"}
    assert case.frozen_history.decoys_adjacent_to_target is True
    assert {
        decoy.decoy_id for decoy in case.frozen_history.decoys
    } >= {"short-checkout-queue-burst", "short-reporting-queue-burst"}
    checkout_decoy = next(
        decoy for decoy in case.frozen_history.decoys
        if decoy.decoy_id == "short-checkout-queue-burst"
    )
    assert checkout_decoy.duration_seconds == 60
    assert checkout_decoy.count == 3
    reporting_decoy = next(
        decoy for decoy in case.frozen_history.decoys
        if decoy.decoy_id == "short-reporting-queue-burst"
    )
    assert reporting_decoy.target == "testdb/report_user"
    assert reporting_decoy.count == 2
    assert reporting_decoy.duration_seconds == 30
    assert next(
        decoy for decoy in case.frozen_history.decoys
        if decoy.decoy_id == "short-connection-churn"
    ).minimum_deviation_mad == 0.1
    assert provider.target_variants("pgbouncer_pool_rates") == (None,)


def test_rg1_catalog_exposes_dynamic_targets_to_shared_metric_tool_contract():
    _case, provider = _provider()
    catalog = PostgresScenarioMetricCatalog(provider, POSTGRES_METRIC_CATALOG)

    definition = postgres_query_metrics_tool_definition(catalog)
    metrics = {item["metric_name"]: item for item in definition["metric_definitions"]}

    assert metrics["pgbouncer_pool_clients"]["target_scope"]["series_target"] == "scenario_target"
    assert catalog.series_target("database_capacity") == "postgres"


def test_rg1_provider_serves_latest_window_without_explicit_timestamps():
    _case, provider = _provider()

    payload = json.loads(provider.query("pgbouncer_pool_clients", "testdb/checkout_user", None, None))

    assert payload["status"] == "success"
    assert payload["series"]["testdb/checkout_user"]["cl_waiting"] == [0.0, 3.0]
    assert payload["window"]["step_seconds"] == 2


def test_rg1_provider_resets_sampling_baselines_without_erasing_history():
    _case, provider = _provider()
    provider._previous_stats[("testdb/checkout_user", "checkout_user")] = (10, 20, 3.0)
    provider._previous_sample_time = 12.0

    provider.reset_sampling_baselines()

    assert provider._samples[("pgbouncer_pool_clients", "testdb/checkout_user")]
    assert provider._previous_stats == {}
    assert provider._previous_sample_time is None


def test_rg1_provider_primes_target_baselines_from_live_counters():
    case = PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case("pool_partition_shortage")

    class _Runner:
        def get_live_activity_counts(self):
            return {
                "report_tpcds": {"calls": 9, "ok_calls": 8},
                "report_probe": {"calls": 4, "ok_calls": 4},
            }

    class _Injector:
        def __init__(self):
            self._etl_lock = threading.Lock()
            self._etl_rows_updated = 12

        def churn_counts(self):
            return 30, 29

    injector = _Injector()
    provider = PgBouncerMetricHistoryProvider(
        SimpleNamespace(_workload_runner=_Runner()),
        case,
        injector,
    )
    provider.reset_sampling_baselines()

    assert provider._previous_profile_counts["report"] == (13, 12)
    assert provider._previous_etl_rows == 12
    assert provider._previous_churn_counts == (30, 29)
    assert provider._previous_sample_time is not None


def test_rg1_maxwait_prefers_microseconds_and_keeps_legacy_seconds():
    _case, provider = _provider()

    assert provider._maxwait_seconds({"maxwait": 0, "maxwait_us": 1250000}) == 1.25
    assert provider._maxwait_seconds({"maxwait": 2, "maxwait_us": 0}) == 2.0
    assert provider._maxwait_seconds({"maxwait": None, "maxwait_us": "bad"}) == 0.0


def test_rg1_pool_client_aggregate_uses_worst_pool_wait_not_sum():
    values = {
        ("pgbouncer_pool_clients", "testdb/checkout_user"): {
            "cl_active": 2.0, "cl_waiting": 4.0, "maxwait_sec": 1.25,
        },
        ("pgbouncer_pool_clients", "testdb/report_user"): {
            "cl_active": 1.0, "cl_waiting": 2.0, "maxwait_sec": 3.5,
        },
    }

    aggregate = rg1.PgBouncerMetricHistoryProvider._aggregate(
        values,
        "pgbouncer_pool_clients",
        ("cl_active", "cl_waiting", "maxwait_sec"),
        max_fields=frozenset({"maxwait_sec"}),
    )

    assert aggregate == {"cl_active": 3.0, "cl_waiting": 6.0, "maxwait_sec": 3.5}


def test_rg1_service_ratio_is_bounded_and_progress_is_interval_delta():
    case = PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case("pool_partition_shortage")

    class _Runner:
        def get_live_activity_counts(self):
            return {"report_tpcds": {"calls": 10, "ok_calls": 12}, "report_probe": {"calls": 0, "ok_calls": 0}}

        def get_activity(self, **_kwargs):
            return {"value": []}

    provider = PgBouncerMetricHistoryProvider(SimpleNamespace(_workload_runner=_Runner()), case)
    provider._previous_sample_time = 10.0
    provider._previous_profile_counts = {"report": (0, 0), "checkout": (0, 0)}
    services = provider._service_values(2.0)

    assert services["report"]["success_ratio"] == 1.0
    assert services["report"]["progress_units"] == 12.0


def test_rg1_target_pgbench_ramp_tracks_all_containers_for_teardown(monkeypatch):
    case = PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case("pool_partition_shortage")
    injector = rg1.PgBouncerConnectionBudgetInjector()
    injector.pgbench_container = "rg1-pgbench"
    injector.network = "rg1-network"
    injector._checkout_script = "/tmp/checkout.sql"
    docker_calls = []

    def fake_docker(*args, **kwargs):
        docker_calls.append(args)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(rg1, "_docker", fake_docker)
    injector._pgbench_ramp_loop(case, ((0, 1), (0, 1), (0, 4)), 2)
    injector._stop_pgbench()

    started = [args[args.index("--name") + 1] for args in docker_calls if args[:3] == ("run", "-d", "--name")]
    removed = [args[-1] for args in docker_calls if args[:2] == ("rm", "-f")]
    assert started == ["rg1-pgbench-ramp-1", "rg1-pgbench-ramp-2", "rg1-pgbench-ramp-3"]
    assert removed == started
    assert injector._pgbench_containers == []


def test_rg1_normal_auxiliary_burst_uses_explicit_health_window_concurrency(monkeypatch):
    case = PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case("pool_partition_shortage")
    injector = rg1.PgBouncerConnectionBudgetInjector()
    thread_args = []

    class _Thread:
        def __init__(self, *, target, args, name, daemon):
            thread_args.append((target, args, name, daemon))

        def start(self):
            return None

        def join(self, **_kwargs):
            return None

    monkeypatch.setattr(rg1.threading, "Thread", _Thread)

    injector._start_staged_auxiliary_read(case, burst_workers=8, record_schedule=True)

    assert len(thread_args) == 1
    assert thread_args[0][1] == (case, 8)
    assert thread_args[0][2] == "pg-rg-pgbouncer-staged-checkout-auxiliary"


def test_rg1_reporting_burst_is_captured_in_normal_and_target_phases(monkeypatch):
    case = PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case("pool_partition_shortage")
    injector = rg1.PgBouncerConnectionBudgetInjector()
    thread_args = []
    events = []

    class _Thread:
        def __init__(self, *, target, args, name, daemon):
            thread_args.append((target, args, name, daemon))

        def start(self):
            return None

    monkeypatch.setattr(rg1.threading, "Thread", _Thread)
    injector._record_event = lambda **event: events.append(event)

    injector._start_capture_report_noise(case, target_budget=False)
    assert thread_args[0][1] == (case, 4)
    assert events[0]["details"]["capture_phase"] == "normal"

    injector._target_report_noise_thread = None
    injector._start_capture_report_noise(case, target_budget=True)
    assert thread_args[1][1] == (case, 2)
    assert events[1]["details"]["capture_phase"] == "target"


def test_rg1_provider_records_target_revision_inside_public_sample_window():
    case = PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case("pool_partition_shortage")
    injector = SimpleNamespace(run_id="run-1")
    provider = PgBouncerMetricHistoryProvider(SimpleNamespace(), case, injector)
    provider.env = SimpleNamespace(
        manage_instance=lambda **_kwargs: {"status": "success"},
        pgbouncer_admin_query=lambda _query: {"status": "success"},
    )
    provider._pool_rows = lambda _payload: {}
    provider._stats_rows = lambda _payload: {}
    provider._client_values = lambda _payload, _elapsed: {
        f"{case.dbname}/{user}": {"connects_per_sec": 0.0, "disconnects_per_sec": 0.0}
        for user in case.pool_users
    }
    provider._capacity_values = lambda: {"active_connections": 5.0, "cpu_percent": 10.0}
    provider._service_values = lambda _elapsed: {
        "checkout": {"throughput_per_sec": 1.0, "p99_ms": 10.0, "success_ratio": 1.0, "progress_units": 1.0},
        "report": {"throughput_per_sec": 1.0, "p99_ms": 10.0, "success_ratio": 1.0, "progress_units": 1.0},
        "etl": {"throughput_per_sec": 1.0, "p99_ms": 0.0, "success_ratio": 1.0, "progress_units": 1.0},
    }

    provider._sample(BASE_MS)
    provider._sample(BASE_MS + 2_000)
    captured = provider.capture_history_records(
        (HistoricalRecordSource.OPERATION_EVENT,),
        BASE_MS,
        BASE_MS + 2_000,
    )

    assert len(captured.point_records) == 1
    assert captured.point_records[0].timestamp_ms == BASE_MS + 2_000
    assert captured.point_records[0].payload["details"]["new_max_db_connections"] == case.max_database_connections


def test_rg1_target_revision_ignores_retained_normal_samples():
    case = PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case("pool_partition_shortage")

    class _Injector:
        run_id = "run-1"

        def __init__(self):
            self._etl_lock = threading.Lock()
            self._etl_rows_updated = 0

        def churn_counts(self):
            return 0, 0

    injector = _Injector()
    provider = PgBouncerMetricHistoryProvider(SimpleNamespace(), case, injector)
    provider.env = SimpleNamespace(
        manage_instance=lambda **_kwargs: {"status": "success"},
        pgbouncer_admin_query=lambda _query: {"status": "success"},
    )
    provider._pool_rows = lambda _payload: {}
    provider._stats_rows = lambda _payload: {}
    provider._client_values = lambda _payload, _elapsed: {
        f"{case.dbname}/{user}": {"connects_per_sec": 0.0, "disconnects_per_sec": 0.0}
        for user in case.pool_users
    }
    provider._capacity_values = lambda: {"active_connections": 5.0, "cpu_percent": 10.0}
    provider._service_values = lambda _elapsed: {
        "checkout": {"throughput_per_sec": 1.0, "p99_ms": 10.0, "success_ratio": 1.0, "progress_units": 1.0},
        "report": {"throughput_per_sec": 1.0, "p99_ms": 10.0, "success_ratio": 1.0, "progress_units": 1.0},
        "etl": {"throughput_per_sec": 1.0, "p99_ms": 0.0, "success_ratio": 1.0, "progress_units": 1.0},
    }

    provider._sample(BASE_MS)
    provider._sample(BASE_MS + 2_000)
    provider._events.clear()
    provider.reset_sampling_baselines()
    provider._sample(BASE_MS + 4_000)
    assert provider._events == []
    provider._sample(BASE_MS + 6_000)
    assert len(provider._events) == 1


def test_rg1_history_contract_contains_only_observed_capacity_and_churn_fields():
    _case, provider = _provider()

    assert provider.metric_definitions()["database_capacity"].value_fields == (
        "active_connections",
        "cpu_percent",
    )
    assert provider.metric_definitions()["connection_churn"].value_fields == (
        "connects_per_sec",
        "disconnects_per_sec",
    )
    assert provider.target_variants("service_slo") == ("checkout", "report", "etl")
    semantics = provider.agent_contract()["metric_semantics"]
    assert "client backend sessions" in semantics["database_capacity.active_connections"]
    assert "background checkout probe" in semantics["service_slo.checkout"]
    assert "joint replay artifact" in semantics["service_slo.checkout"]


def test_rg1_pool_rates_keep_database_scope_when_stats_has_no_user_dimension():
    _case, provider = _provider()

    rows = provider._stats_rows({
        "columns": ["database", "total_xact_count", "total_query_count", "avg_query_time"],
        "result": [["testdb", 12, 18, 2500]],
    })

    assert set(rows) == {"testdb"}
    assert rows["testdb"]["avg_query_ms"] == 2.5


def test_rg1_connection_churn_uses_workload_lifecycle_counts():
    case = PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case("pool_partition_shortage")

    class _Churn:
        counts = (0, 0)

        def churn_counts(self):
            return self.counts

    churn = _Churn()
    provider = PgBouncerMetricHistoryProvider(SimpleNamespace(), case, churn)
    payload = {"columns": ["database", "user"], "result": []}

    provider._client_values(payload, 2.0)
    churn.counts = (60, 60)
    burst = provider._client_values(payload, 2.0)
    churn.counts = (67, 67)
    baseline = provider._client_values(payload, 2.0)

    assert burst["testdb/checkout_user"]["connects_per_sec"] == 30.0
    assert baseline["testdb/checkout_user"]["connects_per_sec"] == 3.5
    assert burst["testdb/report_user"]["connects_per_sec"] == 0.0


def test_rg1_invalid_pool_mode_returns_evaluator_readable_failure_artifact(monkeypatch):
    case = PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case("pool_partition_shortage")

    class _Env:
        def manage_instance(self, *, action):
            if action == "pgbouncer_show_config":
                return {
                    "status": "success",
                    "columns": ["key", "value"],
                    "result": [["pool_mode", "statement"], ["default_pool_size", "3"]],
                }
            if action == "pgbouncer_show_pools":
                return {
                    "status": "success",
                    "columns": ["database", "user", "cl_waiting"],
                    "result": [[case.dbname, case.checkout_user, 2]],
                }
            raise AssertionError(f"unexpected action: {action}")

    injector = rg1.PgBouncerConnectionBudgetInjector()
    injector.env = _Env()

    def _replay_must_not_start(_case):
        raise AssertionError("invalid pool mode should be classified before replay startup")

    monkeypatch.setattr(injector, "_start_replay_runtime", _replay_must_not_start)

    artifact = injector.run_acceptance_replay(case)

    assert artifact["replay_status"] == "skipped_invalid_pool_mode"
    assert artifact["policy_failure"]["pool_mode"] == "statement"
    assert artifact["checkout"]["attempts"] == 0
    assert artifact["report"]["completed"] == 0
    assert artifact["etl"]["rows_updated"] == 0
    assert artifact["queue_converged"] is False
    assert artifact["final_cl_waiting"] == 2
    assert injector._acceptance_artifact == artifact


def test_pg_env_routes_frozen_history_provider_through_public_query_metrics():
    _case, provider = _provider()
    env = PGEnv(deployment=SimpleNamespace(container_name="pg-rg-mf-test", resources={}))
    env.attach_scenario_metric_provider(provider)

    payload = json.loads(env.query_metrics("pgbouncer_pool_clients", target="testdb/checkout_user"))

    assert payload["status"] == "success"
    assert payload["metric"] == "pgbouncer_pool_clients"


def test_pg_env_registers_rg1_staging_relations_with_public_history_guard():
    case = PgResourceGovernancePgbouncerConnectionBudgetScenario().get_case("pool_partition_shortage")
    case = replace(case, frozen_history=None)
    env = PGEnv(deployment=SimpleNamespace(container_name="pg-rg-mf-guard-test", resources={}))

    env.configure_case(case)

    assert env._history_protected_relations == frozenset(case.public_sql_protected_relations)


def test_rg1_provider_implements_public_history_capture_contract():
    _case, provider = _provider()
    samples = [
        (BASE_MS, {"cl_active": 1.0, "cl_waiting": 0.0, "maxwait_sec": 0.0}),
        (BASE_MS + 2_000, {"cl_active": 2.0, "cl_waiting": 3.0, "maxwait_sec": 1.5}),
    ]
    for target in provider.target_variants("pgbouncer_pool_clients"):
        provider._samples[("pgbouncer_pool_clients", target)] = list(samples)

    frames = provider.capture_history(
        ("pgbouncer_pool_clients",),
        BASE_MS,
        BASE_MS + 2_000,
        2,
    )

    assert [frame.metric for frame in frames] == ["pgbouncer_pool_clients"]
    assert set(frames[0].series) == {"postgres", "testdb/checkout_user", "testdb/report_user", "testdb/etl_user"}
    assert all(
        len(timestamps) == 2
        for timestamps in frames[0].timestamps_ms.values()
    )


def test_pg_env_public_capture_aggregates_rg1_targets_per_metric():
    _case, provider = _provider()
    samples = []
    for index in range(2):
        samples.append((
            BASE_MS + index * 2_000,
            {
                field: float(index)
                for field in provider.metric_definitions()["pgbouncer_pool_clients"].value_fields
            },
        ))
    for metric in provider.metric_names:
        definition = provider.metric_definitions()[metric]
        for target in provider.target_variants(metric):
            provider._samples[(metric, target)] = [
                (
                    timestamp,
                    {field: float(index) for field in definition.value_fields},
                )
                for index, (timestamp, _values) in enumerate(samples)
            ]
    provider._last_timestamp_ms = BASE_MS + 2_000

    env = PGEnv(deployment=SimpleNamespace(container_name="pg-rg-mf-capture-test", resources={}))
    env.attach_scenario_metric_provider(provider)
    frames = env.capture_metric_history(
        tuple(sorted(provider.metric_names)),
        BASE_MS,
        BASE_MS + 2_000,
        2,
    )

    assert tuple(frame.metric for frame in frames) == tuple(sorted(provider.metric_names))
    assert all(frame.query_target is None for frame in frames)
    assert all(len(frame.series) == len(provider.target_variants(frame.metric)) for frame in frames)


def test_operation_event_history_filters_are_public_and_targetable():
    event = HistoricalPointRecord(
        source=HistoricalRecordSource.OPERATION_EVENT,
        target="testdb/checkout_user",
        timestamp_ms=BASE_MS,
        payload={
            "event_type": "config_revision",
            "entity_type": "pooler_config",
            "entity": "pgbouncer",
            "action": "apply",
            "status": "success",
            "correlation_id": "run-1",
            "details": {"old_max_db_connections": 20, "new_max_db_connections": 6},
        },
    )
    store = FrozenHistoricalRecordStore.from_captured(CapturedRecords(
        point_records=(event,),
        coverage=(HistoricalCoverage(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target=None,
            start_ms=BASE_MS,
            end_ms=BASE_MS + 2_000,
        ),),
    ))

    result = store.query(
        source=HistoricalRecordSource.OPERATION_EVENT,
        start_ms=BASE_MS,
        end_ms=BASE_MS + 2_000,
        target="testdb/checkout_user",
        filters={"event_type": "config_revision", "contains": "new_max_db_connections"},
        limit=10,
        max_window_seconds=60,
    )

    assert result["matched_records"] == 1
    assert result["records"][0]["details"]["new_max_db_connections"] == 6
