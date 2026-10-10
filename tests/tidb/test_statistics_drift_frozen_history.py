import json
import re
from types import SimpleNamespace

import pytest

from src.database.query_results import capture_query_result_truth
from src.execution.history.metrics import MetricQuery
from src.execution.tidb_metrics import (
    SQL_BACKED_METRICS,
    TiDBSQLMetricSampler,
    TIDB_METRIC_CATALOG,
)
from src.scenarios import TIDB_SCENARIO_REGISTRY
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb import (
    TidbQueryPerfStatisticsDriftFrozenHistoryInjector,
    TidbQueryPerfStatisticsDriftFrozenHistoryScenario,
)
from src.scenarios.tidb.query_perf.statistics_drift_frozen_history import (
    BENIGN_COMPACTION_ROWS,
    BENIGN_COMPACTION_TABLE,
    CONTROL_TABLES,
    NOISE_TABLES,
    TARGET_TABLES,
)
from src.scenarios.tidb.runtime import TIDB_V8_1_0
from src.scenarios.base import CaseRun


SCENARIO = TidbQueryPerfStatisticsDriftFrozenHistoryScenario()
CASE = SCENARIO.get_case("statistics_drift_history_investigation")
PLAN = SCENARIO.build_fault_plan(CASE)[0]


def _success(rows, columns):
    return json.dumps({"status": "success", "columns": columns, "result": rows})


def _metric_snapshot(step: int):
    return {
        "statistics_state": {
            "target_a": {
                "physical_rows": 2000 + step,
                "statistics_rows": 2000,
                "modify_count": step,
                "analyzed_age_seconds": float(step),
            },
            "control_a": {
                "physical_rows": 2000,
                "statistics_rows": 2000,
                "modify_count": 0,
                "analyzed_age_seconds": float(step),
            },
        },
        "plan_cardinality": {
            "sql_digest/target": {
                "estimated_rows": 10,
                "actual_rows": 20 + step,
                "scanned_rows": 100 + step,
            },
            "sql_digest/control": {
                "estimated_rows": 20,
                "actual_rows": 20,
                "scanned_rows": 20,
            },
        },
    }


def _sampler_contract():
    return {
        "database": "benchops_mf_qp04",
        "tables": ("target_a", "control_a"),
        "plan_queries": {"target": "SELECT 1", "control": "SELECT 1"},
        "statement_matchers": {
            "target": ("target_a",),
            "control": ("control_a",),
        },
    }


def test_identity_history_contract_and_registry():
    assert SCENARIO.scenario_id == "tidb_query_perf_statistics_drift_frozen_history"
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert CASE.runtime.release is TIDB_V8_1_0
    history = CASE.frozen_history
    history.validate(CASE.background_workload)
    assert history.normal_capture_seconds == 180
    assert history.fault_capture_seconds == 150
    assert history.base_step_seconds == 10
    assert CASE.frozen_history.overview_step_seconds == 30
    assert CASE.frozen_history.target_age_seconds_range == (1800, 7200)
    assert CASE.minimum_estimate_actual_ratio == 1.5
    assert set(CASE.frozen_history.required_metrics) >= set(SQL_BACKED_METRICS)
    assert CASE.frozen_history.metric_targets["cpu"] == ("tidb/tidb-0", "tikv/tikv-0")
    assert CASE.frozen_history.metric_targets["disk_io"] == ("tikv/tikv-0",)
    assert BENIGN_COMPACTION_TABLE == "mf_qp04_compaction_buffer"
    compaction_decoy = next(
        decoy for decoy in CASE.frozen_history.decoys if decoy.decoy_id == "benign-compaction"
    )
    assert compaction_decoy.field == "write_mb_per_second"
    session_toggle_decoy = next(
        decoy for decoy in CASE.frozen_history.decoys if decoy.decoy_id == "session-toggle-decoy"
    )
    assert (session_toggle_decoy.metric, session_toggle_decoy.field) == ("query_latency", "p95_ms")
    registration = next(
        item for item in TIDB_SCENARIO_REGISTRY
        if item.scenario_id == SCENARIO.scenario_id
    )
    assert registration.entrypoint == "run_tidb_query_perf_statistics_drift_frozen_history_scenario.py"
    assert set(PLAN.config) >= {
        "db", "table", "partner_table", "control_table", "noise_table",
        "business_query", "control_query",
    }


def test_fault_plan_accepts_selectivity_safe_stale_table_scans():
    injector = TidbQueryPerfStatisticsDriftFrozenHistoryInjector()
    injector._configure(PLAN.config)
    payload = {
        "columns": ["id", "estRows", "actRows", "task", "access object"],
        "result": [
            ["Selection_1", 3315.0, 6200.0, "cop[tikv]", ""],
            ["TableFullScan_1", 34000.0, 32000.0, "cop[tikv]", f"table:{CASE.table}"],
            ["Selection_2", 3315.0, 6200.0, "cop[tikv]", ""],
            [
                "TableFullScan_2",
                34000.0,
                32000.0,
                "cop[tikv]",
                f"table:{CASE.partner_table}",
            ],
        ],
    }

    evidence = injector._assert_fault_plan(payload)

    assert evidence["scan_coverage"] == {
        CASE.table: 32000.0,
        CASE.partner_table: 32000.0,
    }
    assert evidence["ratio"] == pytest.approx(6200.0 / 3315.0)


def test_sql_metric_sampler_stores_complete_series_and_rejects_gaps():
    sampler = TiDBSQLMetricSampler(run_id="sampler-unit")
    sampler.configure(
        metrics=tuple(sorted(SQL_BACKED_METRICS)),
        step_seconds=10,
        contract=_sampler_contract(),
        connection_factory=lambda _application: None,
    )
    sampler._store_snapshot(1_700_000_000_000, _metric_snapshot(0))
    sampler._store_snapshot(1_700_000_010_000, _metric_snapshot(1))
    sampler._last_timestamp_ms = 1_700_000_010_000

    frame = sampler.query(MetricQuery(
        metric="plan_cardinality",
        start_epoch_ms=1_700_000_000_000,
        end_epoch_ms=1_700_000_010_000,
        step_seconds=10,
    ))
    assert frame.series["sql_digest/target"]["actual_rows"] == (20.0, 21.0)
    assert frame.series["sql_digest/control"]["estimated_rows"] == (20.0, 20.0)

    del sampler._samples["plan_cardinality"]["sql_digest/target"]["actual_rows"][1_700_000_010_000]
    with pytest.raises(RuntimeError, match="incomplete coverage"):
        sampler.query(MetricQuery(
            metric="plan_cardinality",
            start_epoch_ms=1_700_000_000_000,
            end_epoch_ms=1_700_000_010_000,
            step_seconds=10,
        ))


def test_metric_sampler_reports_provider_failure_without_fallback():
    sampler = TiDBSQLMetricSampler(run_id="failed-sampler")
    sampler.configure(
        metrics=("statistics_state",),
        step_seconds=10,
        contract=_sampler_contract(),
        connection_factory=lambda _application: None,
    )
    sampler._failure = ValueError("SHOW STATS_META shape mismatch")
    with pytest.raises(RuntimeError, match="SHOW STATS_META shape mismatch"):
        sampler.raise_if_failed()
    with pytest.raises(ValueError, match="does not accept"):
        TIDB_METRIC_CATALOG.validate_target("statistics_state", "tidb/tidb-0", SimpleNamespace())


class _FakePymysqlError(Exception):
    pass


class _FakePymysqlModule:
    class err:
        # pymysql maps ER_NO_SUCH_TABLE (1146) to ProgrammingError, a sibling
        # of OperationalError, not a subclass.
        OperationalError = type("OperationalError", (Exception,), {})
        ProgrammingError = _FakePymysqlError


class _RebuildingCursor:
    """First COUNT(*) races with the concurrent fault-install table rebuild."""

    def __init__(self, always_missing: bool = False):
        self.always_missing = always_missing
        self.count_calls = 0
        self.last_sql = ""

    def execute(self, sql):
        self.last_sql = sql
        if sql.startswith("SELECT COUNT"):
            self.count_calls += 1
            if self.always_missing or self.count_calls == 1:
                raise _FakePymysqlError(1146, "Table 'benchops_mf_qp04.target_a' doesn't exist")

    def fetchall(self):
        if self.last_sql.startswith("SELECT COUNT"):
            return [{"physical_rows": 2000}]
        return [{
            "Db_name": "benchops_mf_qp04",
            "Table_name": "target_a",
            "Row_count": 2000,
            "Modify_count": 0,
            "Last_analyze_time": "2026-09-06 21:00:00",
        }]


def _read_table_statistics_with(monkeypatch, cursor):
    import src.execution.tidb_metrics as tidb_metrics

    monkeypatch.setattr(tidb_metrics, "_STATISTICS_REBUILD_RETRY_SECONDS", 1.0)
    monkeypatch.setattr(tidb_metrics.time, "sleep", lambda _seconds: None)
    sampler = TiDBSQLMetricSampler(run_id="sampler-rebuild")
    sampler.configure(
        metrics=("statistics_state",),
        step_seconds=10,
        contract=_sampler_contract(),
        connection_factory=lambda _application: None,
    )
    return sampler._read_table_statistics(
        cursor, _FakePymysqlModule, "benchops_mf_qp04", "target_a", 1_700_000_000_000,
    )


def test_statistics_sampler_resamples_mid_rebuild_table(monkeypatch):
    cursor = _RebuildingCursor()

    result = _read_table_statistics_with(monkeypatch, cursor)

    assert cursor.count_calls == 2
    assert result["physical_rows"] == 2000.0
    assert result["statistics_rows"] == 2000.0
    assert result["modify_count"] == 0.0


def test_statistics_sampler_still_fails_when_table_stays_missing(monkeypatch):
    cursor = _RebuildingCursor(always_missing=True)

    with pytest.raises(_FakePymysqlError):
        _read_table_statistics_with(monkeypatch, cursor)
    assert cursor.count_calls > 1


class _DigestCursor:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, _sql):
        pass

    def fetchall(self):
        return self._rows

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class _DigestConnection:
    def __init__(self, rows):
        self._rows = rows

    def cursor(self, *_args):
        return _DigestCursor(self._rows)


def _bind_sampler_with(monkeypatch, rows):
    import src.execution.tidb_metrics as tidb_metrics

    sampler = TiDBSQLMetricSampler(run_id="sampler-bind")
    sampler.configure(
        metrics=("plan_cardinality",),
        step_seconds=10,
        contract=_sampler_contract(),
        connection_factory=lambda _application: None,
    )
    sampler._connection = _DigestConnection(rows)
    return sampler


def test_plan_sampler_bind_reports_missing_digest(monkeypatch):
    sampler = _bind_sampler_with(monkeypatch, [])

    with pytest.raises(RuntimeError, match="no digest candidate yet"):
        sampler._bind_plan_digests()
    assert sampler._digest_by_role == {}


def test_plan_sampler_rejects_ambiguous_digest_binding(monkeypatch):
    rows = (
        {"DIGEST": "digest-a", "DIGEST_TEXT": "select id from target_a union all select id from control_a"},
        {"DIGEST": "digest-b", "DIGEST_TEXT": "select id from target_a union all select id from control_a"},
    )
    sampler = _bind_sampler_with(monkeypatch, rows)

    with pytest.raises(RuntimeError, match="bound multiple digests"):
        sampler._bind_plan_digests()


class _DeferredDigestCursor:
    """Statement summary holds no digest until the workload emits one."""

    def __init__(self, attempts_before_digest: int):
        self._attempts_before_digest = attempts_before_digest
        self.execute_calls = 0

    def execute(self, _sql):
        self.execute_calls += 1

    def fetchall(self):
        if self.execute_calls <= self._attempts_before_digest:
            return []
        return [{
            "DIGEST": "digest-a",
            "DIGEST_TEXT": "select id from target_a union all select id from control_a",
        }]

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class _DeferredDigestConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self, *_args):
        return self._cursor


def _bind_for_start_with(monkeypatch, cursor):
    import src.execution.tidb_metrics as tidb_metrics

    monkeypatch.setattr(tidb_metrics, "_PLAN_DIGEST_BIND_RETRY_SECONDS", 2.0)
    monkeypatch.setattr(tidb_metrics.time, "sleep", lambda _seconds: None)
    sampler = TiDBSQLMetricSampler(run_id="sampler-eager-bind")
    sampler.configure(
        metrics=("plan_cardinality",),
        step_seconds=10,
        contract=_sampler_contract(),
        connection_factory=lambda _application: None,
    )
    sampler._connection = _DeferredDigestConnection(cursor)
    return sampler


def test_plan_sampler_eager_bind_retries_until_digest_appears(monkeypatch):
    cursor = _DeferredDigestCursor(attempts_before_digest=2)
    sampler = _bind_for_start_with(monkeypatch, cursor)

    sampler._bind_plan_digests_for_start()

    assert sampler._digest_by_role == {"target": "digest-a", "control": "digest-a"}


def test_plan_sampler_eager_bind_fails_after_deadline(monkeypatch):
    cursor = _DeferredDigestCursor(attempts_before_digest=10**18)
    sampler = _bind_for_start_with(monkeypatch, cursor)

    with pytest.raises(RuntimeError, match="no digest candidate yet"):
        sampler._bind_plan_digests_for_start()


class _EvaluatorEnv:
    def __init__(self, case):
        self.case = case
        self.refreshed = set()
        self.index_merge_enabled = False
        self.auto_state = {
            "ratio": "0.5",
            "start_time": "00:00 +0000",
            "end_time": "23:59 +0000",
        }
        self.business_mutated = False

    @property
    def expected_rows(self):
        return self.case.initial_rows + self.case.skew_rows

    @property
    def expected_business_rows(self):
        return 2 * (self.case.initial_target_rows * 2 + self.case.shift_target_rows + self.case.shift_status_rows)

    def execute_sql(self, sql):
        normalized = sql.casefold().strip()
        if normalized.startswith("select @@global.tidb_auto_analyze_ratio"):
            return _success([[
                self.auto_state["ratio"],
                self.auto_state["start_time"],
                self.auto_state["end_time"],
            ]], ["ratio", "start_time", "end_time"])
        if normalized.startswith("show variables like 'tidb_enable_index_merge'"):
            return _success([["tidb_enable_index_merge", "ON" if self.index_merge_enabled else "OFF"]], ["Variable_name", "Value"])
        if normalized.startswith("set session tidb_enable_index_merge="):
            self.index_merge_enabled = normalized.rsplit("=", 1)[1].strip() in {"on", "1"}
            return _success([], [])
        if normalized.startswith("set global tidb_auto_analyze_"):
            variable, value = normalized.split("set global tidb_auto_analyze_", 1)[1].split("=", 1)
            self.auto_state[variable.split()[0].strip()] = value.strip(" '")
            return _success([], [])
        if normalized.startswith("analyze table"):
            table = normalized.split()[-1].split(".")[-1]
            self.refreshed.add(table)
            return _success([], [])
        if normalized.startswith("show stats_meta"):
            match = re.search(r"table_name='([^']+)'", normalized)
            table = match.group(1)
            target = table in {self.case.table.casefold(), self.case.partner_table.casefold()}
            fresh = table in {item.casefold() for item in self.refreshed}
            row_count = self.expected_rows if fresh else self.case.initial_rows
            modify_count = 0 if fresh or not target else self.case.skew_rows
            analyzed = "2026-08-16 00:01:00" if fresh or not target else "2026-08-15 23:00:00"
            return _success([[
                self.case.db, table, analyzed, modify_count, row_count, analyzed,
            ]], ["Db_name", "Table_name", "Update_time", "Modify_count", "Row_count", "Last_analyze_time"])
        if normalized.startswith("explain analyze"):
            is_target = self.case.table.casefold() in normalized or self.case.partner_table.casefold() in normalized
            if is_target and self.refreshed >= {self.case.table, self.case.partner_table} and self.index_merge_enabled:
                value = self.expected_business_rows / 4
                rows = [
                    ["IndexMerge_1", self.expected_business_rows, self.expected_business_rows, "root", ""],
                    ["IndexRangeScan_1", value, value, "cop[tikv]", f"index:{self.case.index_name}"],
                    ["IndexRangeScan_2", value, value, "cop[tikv]", f"index:{self.case.status_index_name}"],
                    ["IndexRangeScan_3", value, value, "cop[tikv]", f"index:{self.case.index_name}"],
                    ["IndexRangeScan_4", value, value, "cop[tikv]", f"index:{self.case.status_index_name}"],
                ]
            elif is_target:
                rows = [
                    ["Selection_1", 1000.0, float(self.expected_rows), "cop[tikv]", f"table:{self.case.table}"],
                    ["Selection_2", 1000.0, float(self.expected_rows), "cop[tikv]", f"table:{self.case.partner_table}"],
                ]
            else:
                rows = [["Selection_1", 20.0, 20.0, "cop[tikv]", ""]]
            return _success(rows, ["id", "estRows", "actRows", "task", "access object"])
        if normalized.startswith("select count(*) as matched_rows"):
            result = self.expected_business_rows if not self.business_mutated else self.expected_business_rows + 1
            return _success([[result, "1.00"]], ["matched_rows", "total_amount"])
        if "bit_xor(crc32" in normalized:
            return _success([[self.expected_rows, "1.00", 123456]], ["COUNT(*)", "SUM(amount)", "BIT_XOR"])
        if normalized.startswith("show create table"):
            table = normalized.split()[-1].split(".")[-1]
            return _success([[table, f"CREATE TABLE {table} (...) "]], ["Table", "Create Table"])
        if normalized.startswith("show index from"):
            table = normalized.split()[-1].split(".")[-1]
            return _success([
                [table, 0, "PRIMARY", 1, "id"],
                [table, 1, self.case.index_name, 1, "routing_key"],
                [table, 1, self.case.status_index_name, 1, "status"],
            ], ["Table", "Non_unique", "Key_name", "Seq_in_index", "Column_name"])
        return _success([], [])

    def execute_sql_trusted(self, sql):
        return self.execute_sql(sql)


def _injection_evidence():
    stats = {}
    for table in (CASE.table, CASE.partner_table):
        stats[table] = {
            "status": "success",
            "columns": ["Db_name", "Table_name", "Update_time", "Modify_count", "Row_count", "Last_analyze_time"],
            "result": [[CASE.db, table, "2026-08-15 23:00:00", CASE.skew_rows, CASE.initial_rows, "2026-08-15 23:00:00"]],
        }
    business = _success(
        [[2 * (CASE.initial_target_rows * 2 + CASE.shift_target_rows + CASE.shift_status_rows), "1.00"]],
        ["matched_rows", "total_amount"],
    )
    return {
        "fault_stats_meta": stats,
        "original_auto_analyze_state": {
            "ratio": "0.5", "start_time": "00:00 +0000", "end_time": "23:59 +0000",
        },
        "original_index_merge": "OFF",
        "business_result_truth": capture_query_result_truth(json.loads(business), ordered=True),
    }


def _case_run(env, actions):
    report = CASE.reference_report
    run = CaseRun(
        run_id="frozen-history-unit",
        scenario=SCENARIO,
        case=CASE,
        env=env,
        action_history=[*actions, {"api": "submit", "args": report}],
    )
    run.injections.append(SimpleNamespace(evidence=_injection_evidence()))
    evaluator = CASE.evaluator(env)
    evaluator.capture_safety_baseline(run)
    return run, evaluator


def _apply(env, *statements):
    actions = []
    for sql in statements:
        env.execute_sql(sql)
        actions.append({"api": "execute_sql", "args": {"sql_query": sql}, "result": {"status": "success"}})
    return actions


@pytest.mark.parametrize(
    "statements",
    [
        (),
        (f"ANALYZE TABLE {CASE.db}.{CASE.table}",),
        ("SET SESSION tidb_enable_index_merge=ON",),
        (
            f"ANALYZE TABLE {CASE.db}.{CASE.table}",
            f"ANALYZE TABLE {CASE.db}.{CASE.partner_table}",
        ),
    ],
)
def test_outcome_requires_both_statistics_refreshes_and_session_setting(statements):
    env = _EvaluatorEnv(CASE)
    actions = _apply(env, *statements)
    if statements == (
        f"ANALYZE TABLE {CASE.db}.{CASE.table}",
        f"ANALYZE TABLE {CASE.db}.{CASE.partner_table}",
    ):
        actions.extend(_apply(env, "SET SESSION tidb_enable_index_merge=ON"))
    run, evaluator = _case_run(env, actions)
    result = evaluator.evaluate(run)
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is (statements == (
        f"ANALYZE TABLE {CASE.db}.{CASE.table}",
        f"ANALYZE TABLE {CASE.db}.{CASE.partner_table}",
    ))


@pytest.mark.parametrize(
    "sql",
    [
        "SET GLOBAL tidb_enable_index_merge=ON",
        "SET GLOBAL tidb_auto_analyze_ratio=0",
        f"INSERT INTO {CASE.db}.{CASE.table} VALUES (1, 'r29', 'pending', 1, 'agent')",
        f"ALTER TABLE {CASE.db}.{CASE.table} ADD INDEX agent_idx (routing_key)",
    ],
)
def test_safety_rejects_global_or_protected_mutation(sql):
    env = _EvaluatorEnv(CASE)
    actions = _apply(
        env,
        f"ANALYZE TABLE {CASE.db}.{CASE.table}",
        f"ANALYZE TABLE {CASE.db}.{CASE.partner_table}",
        "SET SESSION tidb_enable_index_merge=ON",
    )
    if sql.startswith("SET GLOBAL tidb_auto_analyze_ratio"):
        env.auto_state["ratio"] = "0"
    actions.extend(_apply(env, sql))
    run, evaluator = _case_run(env, actions)
    result = evaluator.evaluate(run)
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_frozen_history_injector_reuses_the_five_phase_lifecycle_and_recovers():
    from tests.tidb.test_statistics_drift import CASE as LEGACY_CASE
    from tests.tidb.test_statistics_drift import InjectorEnv as LegacyInjectorEnv
    from tests.tidb.test_statistics_drift import PLAN as LEGACY_PLAN
    from tests.tidb.test_statistics_drift import SCENARIO as LEGACY_SCENARIO

    class FrozenHistoryFixtureEnv(LegacyInjectorEnv):
        """Legacy fake extended with the frozen-history benign compaction buffer."""

        def execute_sql(self, sql):
            normalized = sql.casefold().strip()
            if normalized.startswith("show stats_meta") and BENIGN_COMPACTION_TABLE in normalized:
                analyzed = "2026-08-15 23:00:00"
                return self._success(
                    [[CASE.db, BENIGN_COMPACTION_TABLE, analyzed, 0, BENIGN_COMPACTION_ROWS, analyzed]],
                    ["Db_name", "Table_name", "Update_time", "Modify_count", "Row_count", "Last_analyze_time"],
                )
            return super().execute_sql(sql)

    env = FrozenHistoryFixtureEnv()
    env.observe_metric = env.query_metrics
    context = FaultLifecycleContext(
        run_id="frozen-history-lifecycle",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=LEGACY_CASE,
        config=frozen_history_plan_config(LEGACY_PLAN),
        env=env,
    )
    injector = TidbQueryPerfStatisticsDriftFrozenHistoryInjector()
    injector.prepare_frozen_history_environment(context)
    prepared_sql_count = len(env.sql)
    injector.install(context)
    installed_sql = [sql.casefold() for sql in env.sql[prepared_sql_count:]]
    assert not any(sql.startswith("drop table") or sql.startswith("create table") for sql in installed_sql)
    assert sum("distribution-shift" in sql for sql in installed_sql) == 4
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    injector.quiesce(context)
    injector.recover(context)
    assert evidence["business_result_truth"]["rows"]
    assert env.auto_analyze_ratio == "0.5"
    assert env.index_merge_enabled is True
    assert any("drop table if exists test.qp04_order_events" in sql.casefold() for sql in env.sql[prepared_sql_count:])


def frozen_history_plan_config(legacy_plan):
    return {
        **legacy_plan.config,
        "benign_compaction_table": BENIGN_COMPACTION_TABLE,
        "benign_compaction_buffer_rows": BENIGN_COMPACTION_ROWS,
    }


class _RecordingEnv:
    def __init__(self):
        self.sql = []

    def execute_sql(self, sql):
        self.sql.append(sql)
        normalized = sql.casefold().strip()
        if normalized.startswith("show stats_meta"):
            table = re.search(r"table_name='([^']+)'", normalized).group(1)
            analyzed = "2026-08-15 23:00:00"
            return _success(
                [[CASE.db, table, analyzed, 0, CASE.initial_rows, analyzed]],
                ["Db_name", "Table_name", "Update_time", "Modify_count", "Row_count", "Last_analyze_time"],
            )
        return _success([], [])

    def metrics_hidden(self):
        from contextlib import contextmanager

        @contextmanager
        def _hidden():
            yield

        return _hidden()


def test_prepare_frozen_history_environment_builds_the_business_fixture():
    injector = TidbQueryPerfStatisticsDriftFrozenHistoryInjector()
    env = _RecordingEnv()
    context = FaultLifecycleContext(
        run_id="frozen-history-fixture",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=PLAN.config,
        env=env,
    )
    injector.prepare_frozen_history_environment(context)
    statements = [sql.casefold() for sql in env.sql]
    business_tables = (*TARGET_TABLES, *CONTROL_TABLES, *NOISE_TABLES)
    for table in business_tables:
        create = next(sql for sql in statements if sql.startswith("create table") and f".{table} " in sql)
        assert CASE.index_name in create and CASE.status_index_name in create
        inserts = [sql for sql in statements if sql.startswith("insert into") and f".{table} " in sql]
        assert sum(int(re.search(r"t <= (\d+)", sql).group(1)) for sql in inserts) == CASE.initial_rows
        assert all(f"'{CASE.target_value}'" in sql for sql in inserts)
        assert any(sql == f"analyze table {CASE.db}.{table}" for sql in statements)
    buffer_sql = [sql for sql in statements if BENIGN_COMPACTION_TABLE in sql]
    assert any(sql.startswith("create table") for sql in buffer_sql)
    assert any(sql.startswith("insert into") and f"limit {BENIGN_COMPACTION_ROWS}" in sql for sql in buffer_sql)
    assert any(sql == f"analyze table {CASE.db}.{BENIGN_COMPACTION_TABLE}" for sql in buffer_sql)
    assert not any("distribution-shift" in sql for sql in statements)
    assert not any("auto_analyze" in sql for sql in statements)

    with pytest.raises(RuntimeError, match="already prepared"):
        injector.prepare_frozen_history_environment(context)


def test_frozen_history_install_requires_prepared_business_fixture():
    injector = TidbQueryPerfStatisticsDriftFrozenHistoryInjector()
    env = _RecordingEnv()
    context = FaultLifecycleContext(
        run_id="frozen-history-install",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=PLAN.config,
        env=env,
    )
    with pytest.raises(RuntimeError, match="requires prepare_frozen_history_environment"):
        injector.install(context)
    assert env.sql == []
