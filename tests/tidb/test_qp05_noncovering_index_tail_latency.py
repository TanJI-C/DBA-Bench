import inspect
import json
import runpy
import time
from contextlib import contextmanager
from dataclasses import replace
from types import SimpleNamespace

import pytest

from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.protocol import StructuredReport
from src.scenarios.evaluation.semantic import (
    SemanticConditionJudgment,
    SemanticJudgment,
)
from src.scenarios import TIDB_SCENARIO_REGISTRY
from src.scenarios.base import CaseRun
from src.database.query_results import capture_query_result_truth
from src.database.tidb import tidb_plan_metrics
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb.query_perf.noncovering_index_tail_latency import (
    TidbQueryPerfNoncoveringIndexTailLatencyInjector,
)


SCENARIO_ID = "tidb_query_perf_noncovering_index_tail_latency"
CASE_ID = "noncovering_index_tail_latency"


def _scenario():
    return next(item.scenario for item in TIDB_SCENARIO_REGISTRY if item.scenario_id == SCENARIO_ID)


SCENARIO = _scenario()
CASE = SCENARIO.get_case(CASE_ID)
PLAN = SCENARIO.build_fault_plan(CASE)[0]
TARGET_COLUMNS = [
    "event_id",
    "tenant_id",
    "event_time",
    "order_state",
    "order_total",
    "currency",
    "fulfillment_zone",
]
TARGET_ROWS = [
    [index, 42, f"2025-01-{(index % 28) + 1:02d} 00:00:00", "READY", "42.00", "USD", 0]
    for index in range(1, 101)
]
TARGET_PAYLOAD = {
    "status": "success",
    "columns": TARGET_COLUMNS,
    "result": TARGET_ROWS,
    "row_count": len(TARGET_ROWS),
}
TABLE_TRUTH = [[1_000_000, 500000500000, 123456789]]
PAGE_CONTEXT_TRUTH = [
    ["checkout-history-legacy", 42, "READY", 1, "2024-10-01", "2025-01-01"],
    ["checkout-history-ops", 42, "SHIPPED", 3, "2025-01-01", "2025-07-01"],
    ["checkout-history-page", 42, "READY", 0, "2025-01-01", "2025-07-01"],
    ["checkout-history-page-mobile", 42, "READY", 0, "2025-01-01", "2025-04-01"],
    ["checkout-history-replay", 177, "READY", 2, "2025-01-01", "2025-07-01"],
    ["checkout-history-export", 42, "READY", 1, "2024-07-01", "2025-01-01"],
    ["customer-support-page", 318, "READY", 5, "2024-10-01", "2025-01-01"],
    ["fraud-review-page", 260, "READY", 7, "2025-04-01", "2025-07-01"],
    ["merchant-settlement-export", 205, "READY", 4, "2024-10-01", "2025-01-01"],
    ["merchant-settlement-page", 205, "READY", 4, "2025-01-01", "2025-04-01"],
    ["warehouse-replay-export", 177, "SHIPPED", 6, "2024-07-01", "2025-01-01"],
    ["warehouse-replay-page", 177, "SHIPPED", 6, "2024-07-01", "2025-01-01"],
]
ROUTE_REGISTRY_TRUTH = [list(row) for row in CASE.route_registry_rows]
_FAULT_INDEX_COLUMNS = (
    ("event_time", "tenant_id", "order_state", "event_id"),
    ("order_state", "event_time", "tenant_id", "event_id"),
    ("event_time", "tenant_id", "order_state", "event_id", "order_total", "currency", "fulfillment_zone", "event_note"),
    ("event_time", "tenant_id", "order_state", "event_id", "order_total", "currency", "fulfillment_zone", "merchant_id", "event_note"),
    ("order_state", "event_time", "tenant_id", "event_id", "order_total", "currency", "fulfillment_zone", "merchant_id", "event_note"),
    ("event_time", "tenant_id", "order_state", "event_id", "order_total", "currency", "fulfillment_zone", "merchant_id", "customer_ref", "last_modified", "event_note"),
    ("order_state", "event_time", "tenant_id", "event_id", "order_total", "currency", "fulfillment_zone", "merchant_id", "customer_ref", "last_modified", "event_note"),
    ("event_time", "fulfillment_zone", "tenant_id", "order_state", "event_id", "order_total", "currency", "merchant_id", "customer_ref", "last_modified", "event_note"),
)
BASE_INDEX_CATALOG = [
    [CASE.table, 0, "PRIMARY", 1, "event_id"],
    *[
        [CASE.table, 1, index_name, position, column]
        for index_name, columns in zip(
            CASE.fault_index_names,
            _FAULT_INDEX_COLUMNS,
        )
        for position, column in enumerate(columns, 1)
    ],
    [CASE.table, 1, "qp05_merchant_recent", 1, "merchant_id"],
    [CASE.table, 1, "qp05_merchant_recent", 2, "last_modified"],
    [CASE.table, 1, "qp05_customer_time", 1, "customer_ref"],
    [CASE.table, 1, "qp05_customer_time", 2, "event_time"],
    [CASE.table, 1, "qp05_zone_state_modified", 1, "fulfillment_zone"],
    [CASE.table, 1, "qp05_zone_state_modified", 2, "order_state"],
    [CASE.table, 1, "qp05_zone_state_modified", 3, "last_modified"],
    [CASE.table, 1, "qp05_currency_state_modified", 1, "currency"],
    [CASE.table, 1, "qp05_currency_state_modified", 2, "order_state"],
    [CASE.table, 1, "qp05_currency_state_modified", 3, "last_modified"],
    [CASE.table, 1, "qp05_note_time", 1, "event_note"],
    [CASE.table, 1, "qp05_note_time", 2, "event_time"],
    [CASE.table, 1, "qp05_history_tenant_window", 1, "tenant_id"],
    [CASE.table, 1, "qp05_history_tenant_window", 2, "event_time"],
    [CASE.table, 1, "qp05_history_tenant_window", 3, "order_state"],
    [CASE.table, 1, "qp05_history_tenant_window", 4, "fulfillment_zone"],
    [CASE.table, 1, "qp05_history_tenant_window", 5, "event_id"],
    [CASE.table, 1, "qp05_history_tenant_window", 6, "order_total"],
    [CASE.table, 1, "qp05_history_tenant_window", 7, "currency"],
    [CASE.table, 1, "qp05_history_state_window", 1, "order_state"],
    [CASE.table, 1, "qp05_history_state_window", 2, "event_time"],
    [CASE.table, 1, "qp05_history_state_window", 3, "tenant_id"],
    [CASE.table, 1, "qp05_history_state_window", 4, "fulfillment_zone"],
    [CASE.table, 1, "qp05_history_state_window", 5, "event_id"],
    [CASE.table, 1, "qp05_history_state_window", 6, "order_total"],
    [CASE.table, 1, "qp05_history_state_window", 7, "currency"],
]
FULL_INDEX_CATALOG = [
    *[
        row
        for row in BASE_INDEX_CATALOG
        if row[2] not in CASE.replaceable_fault_index_names
    ],
    [CASE.table, 1, "agent_covering", 1, "tenant_id"],
    [CASE.table, 1, "agent_covering", 2, "order_state"],
    [CASE.table, 1, "agent_covering", 3, "event_time"],
    [CASE.table, 1, "agent_covering", 4, "event_id"],
    [CASE.table, 1, "agent_covering", 5, "order_total"],
    [CASE.table, 1, "agent_covering", 6, "currency"],
    [CASE.table, 1, "agent_covering", 7, "fulfillment_zone"],
]
ADDED_INDEX_CATALOG = [
    *BASE_INDEX_CATALOG,
    *FULL_INDEX_CATALOG[-7:],
]
PARTIAL_INDEX_CATALOG = [
    *BASE_INDEX_CATALOG,
    [CASE.table, 1, "only_order", 1, "tenant_id"],
    [CASE.table, 1, "only_order", 2, "order_state"],
    [CASE.table, 1, "only_order", 3, "event_time"],
    [CASE.table, 1, "only_order", 4, "event_id"],
]
WRONG_RANGE_INDEX_CATALOG = [
    *BASE_INDEX_CATALOG,
    [CASE.table, 1, "covering_wrong_order", 1, "event_time"],
    [CASE.table, 1, "covering_wrong_order", 2, "tenant_id"],
    [CASE.table, 1, "covering_wrong_order", 3, "order_state"],
    [CASE.table, 1, "covering_wrong_order", 4, "event_id"],
    [CASE.table, 1, "covering_wrong_order", 5, "order_total"],
    [CASE.table, 1, "covering_wrong_order", 6, "currency"],
    [CASE.table, 1, "covering_wrong_order", 7, "fulfillment_zone"],
]


def _success(rows=None, columns=None):
    rows = [] if rows is None else rows
    return json.dumps(
        {
            "status": "success",
            "columns": columns or [],
            "result": rows,
            "row_count": len(rows),
        }
    )


def _report(*, complete=True):
    factors = [
        sorted(alias for alias in condition.aliases if alias != condition.condition_id)[0]
        for condition in CASE.evaluator.diagnosis_conditions
    ]
    if not complete:
        factors = factors[:2]
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause" if index < len(factors) - 1 else "necessary_exclusion",
                    "factor": factor,
                    "entity": f"{CASE.db}.{CASE.table}" if index < len(factors) - 1 else "TiDB/TiKV cluster",
                    "evidence": ["EXPLAIN ANALYZE, index catalog, and node health"],
                }
                for index, factor in enumerate(factors)
            ]
        },
        "outcome": {
            "changes": ["created an equivalent safe composite covering access path"],
            "verification": ["verified canonical EXPLAIN ANALYZE, p95, target result, CRC, and table check"],
        },
        "summary": "The report identifies both access-path faults and excludes a component outage.",
    }


class FakeTiDBEnv:
    def __init__(
        self,
        *,
        state="full",
        table_changed=False,
        target_changed=False,
        remove_existing_index=False,
        page_context_changed=False,
        route_registry_changed=False,
        ddl_states=None,
        stats_visible=True,
    ):
        self.state = state
        self.table_changed = table_changed
        self.target_changed = target_changed
        self.remove_existing_index = remove_existing_index
        self.page_context_changed = page_context_changed
        self.route_registry_changed = route_registry_changed
        self.ddl_states = tuple(
            ddl_states
            if ddl_states is not None
            else ("running",)
            if state == "unrepaired"
            else ("synced",)
        )
        self.stats_visible = stats_visible
        self.sql = []
        self.bootstrap_sql = []
        self.show_index_calls = 0
        self.auto_analyze_disabled = False
        self.connection_routers = None
        self.router_reset_count = 0

    @contextmanager
    def metrics_hidden(self):
        yield

    def _plan_rows(self):
        if self.state in {"full", "replaced", "added"}:
            scan_volume = 8218
            index_name = "agent_covering"
            return [
                ["IndexReader_1", "120.00", "100", "root", f"table:{CASE.table}"],
                [
                    "IndexRangeScan_2",
                    "120.00",
                    str(scan_volume),
                    "cop[tikv]",
                    f"table:{CASE.table}, index:{index_name}(tenant_id,order_state,event_time,event_id,order_total,currency,fulfillment_zone), range:(42,READY,2025-01-01,2025-07-01], total_process_keys: {scan_volume}",
                ],
            ]
        if self.state == "wrong_range":
            return [
                ["IndexReader_1", "120.00", "100", "root", f"table:{CASE.table}"],
                [
                    "IndexRangeScan_2",
                    "120.00",
                    "200000",
                    "cop[tikv]",
                    f"table:{CASE.table}, index:covering_wrong_order(event_time,tenant_id,order_state,event_id,order_total,currency,fulfillment_zone), range:(2025-01-01,2025-07-01], total_process_keys: 200000",
                ],
            ]
        if self.state == "partial":
            return [
                ["IndexLookUp_1", "120.00", "100", "root", f"table:{CASE.table}"],
                [
                    "IndexRangeScan_2",
                    "120.00",
                    "8218",
                    "cop[tikv]",
                    f"table:{CASE.table}, index:only_order(tenant_id,order_state,event_time,event_id), range:(42,READY,2025-01-01,2025-07-01], total_process_keys: 8218",
                ],
                ["TableRowIDScan_3", "120.00", "100", "cop[tikv]", f"table:{CASE.table}"],
            ]
        return [
            ["IndexLookUp_1", "120.00", "13149", "root", f"table:{CASE.table}"],
            [
                "IndexRangeScan_2",
                "13149.00",
                "13149",
                "cop[tikv]",
                f"table:{CASE.table}, index:{CASE.fault_index_names[0]}(event_time,tenant_id,order_state,event_id), range:(2025-01-01,2025-07-01], total_process_keys: 13149",
            ],
            ["TableRowIDScan_3", "120.00", "13149", "cop[tikv]", f"table:{CASE.table}"],
        ]

    def execute_sql(self, sql):
        self.sql.append(sql)
        normalized = " ".join(sql.casefold().split())
        if normalized.startswith("explain analyze"):
            return _success(
                self._plan_rows(),
                ["id", "estRows", "actRows", "task", "access object"],
            )
        if normalized.startswith("with page_scope as") and f"from {CASE.db}.{CASE.table} as e" in normalized:
            if self.state == "partial":
                time.sleep(0.1)
            rows = [list(row) for row in TARGET_ROWS]
            if self.target_changed:
                rows[0][1] = 177
            return _success(rows, TARGET_COLUMNS)
        if normalized.startswith("select count(*), sum(event_id)"):
            return _success(TABLE_TRUTH if not self.table_changed else [[999999, 499999500001, 987654321]])
        if "from benchops.qp05_page_context" in normalized and "order by route_key" in normalized:
            rows = PAGE_CONTEXT_TRUTH
            if self.page_context_changed:
                rows = PAGE_CONTEXT_TRUTH[:-1]
            return _success(rows, ["route_key", "tenant_id", "order_state", "window_start", "window_end"])
        if "from benchops.qp05_route_registry" in normalized and "order by fingerprint" in normalized:
            rows = ROUTE_REGISTRY_TRUTH
            if self.route_registry_changed:
                rows = ROUTE_REGISTRY_TRUTH[:-1]
            return _success(
                rows,
                ["fingerprint", "route_key", "route_version", "is_current", "surface", "projection_class", "slo_ms"],
            )
        if normalized.startswith("select count(*) from benchops.qp05_page_context"):
            return _success([[12]], ["COUNT(*)"])
        if normalized.startswith("select count(*) from benchops.qp05_route_registry"):
            return _success([[CASE.route_registry_row_count]], ["COUNT(*)"])
        if normalized.startswith("select count(*) from"):
            return _success([[CASE.row_count]], ["COUNT(*)"])
        if normalized.startswith("select @@global.tidb_auto_analyze_ratio"):
            if self.auto_analyze_disabled:
                return _success(
                    [["0.000010", "00:00 +0000", "00:01 +0000"]],
                    ["@@GLOBAL.tidb_auto_analyze_ratio", "start_time", "end_time"],
                )
            return _success(
                [["0.5", "00:00 +0000", "23:59 +0000"]],
                ["@@GLOBAL.tidb_auto_analyze_ratio", "start_time", "end_time"],
            )
        if normalized.startswith("select date_format"):
            return _success([["00:00 +0000", "00:01 +0000"]])
        if normalized.startswith("show index"):
            self.show_index_calls += 1
            rows = BASE_INDEX_CATALOG
            if self.show_index_calls > 1:
                rows = {
                    "full": FULL_INDEX_CATALOG,
                    "replaced": FULL_INDEX_CATALOG,
                    "added": ADDED_INDEX_CATALOG,
                    "partial": PARTIAL_INDEX_CATALOG,
                    "wrong_range": WRONG_RANGE_INDEX_CATALOG,
                }.get(self.state, BASE_INDEX_CATALOG)
            if self.remove_existing_index and self.show_index_calls > 1:
                rows = BASE_INDEX_CATALOG[1:]
            return _success(rows, ["Table", "Non_unique", "Key_name", "Seq_in_index", "Column_name"])
        if normalized.startswith("admin check table"):
            return _success([[CASE.table, "OK"]], ["Table", "Msg_text"])
        if normalized.startswith("show stats_meta"):
            rows = [["benchops", CASE.table, 1, 0]] if self.stats_visible else []
            return _success(rows, ["Db_name", "Table_name", "Version", "Modify_count"])
        if "information_schema.tables" in normalized and "index_length" in normalized:
            index_growth = 0
            return _success(
                [[1_000_000, 50_000_000, 100_000_000 + index_growth]],
                ["TABLE_ROWS", "DATA_LENGTH", "INDEX_LENGTH"],
            )
        if normalized.startswith("create database") or normalized.startswith("create table"):
            return _success()
        if normalized.startswith("drop table") or normalized.startswith("insert"):
            return _success()
        if normalized.startswith("analyze table") or normalized.startswith("create index"):
            return _success()
        if normalized.startswith("set global tidb_auto_analyze_ratio="):
            self.auto_analyze_disabled = "0.000010" in normalized
            return _success()
        if normalized.startswith("alter table") or normalized.startswith("set global"):
            return _success()
        if normalized.startswith("admin show ddl jobs"):
            return _success(
                [[index + 1, state] for index, state in enumerate(self.ddl_states)],
                ["JOB_ID", "STATE"],
            )
        if normalized.startswith("drop index") or normalized.startswith("delete"):
            return _success()
        return _success()

    def execute_bootstrap_sql(self, sql):
        self.bootstrap_sql.append(sql)
        return _success()

    def execute_sql_full_result(self, sql):
        return self.execute_sql(sql)

    def query_metrics(self, metric_type, target=None):
        return _success([], [])

    def observe_metric(self, metric_type, target=None, limit=None):
        return _success([], [])

    def manage_cluster(self, resource, operation, target=None, parameters=None):
        assert (resource, operation, target) == ("service", "list", None)
        return json.dumps(
            {
                "status": "success",
                "resource": resource,
                "operation": operation,
                "target": target,
                "result": {
                    "nodes": {
                        "pd/pd-0": {"state": "Up"},
                        "tidb/tidb-0": {"state": "Up"},
                        "tikv/tikv-0": {"state": "Up"},
                        "tikv/tikv-1": {"state": "Up"},
                        "tikv/tikv-2": {"state": "Up"},
                    },
                    "sql_endpoints": ["tidb/tidb-0"],
                },
            }
        )

    def initialize_connection_routers(self, routers):
        self.connection_routers = routers

    def reset_connection_routers(self):
        self.connection_routers = None
        self.router_reset_count += 1

    def read_log(self, target, lines=200, start_line=None, end_line=None, match_key=None):
        return _success([], [])

    def execute_sql_trusted(self, sql):
        return self.execute_sql(sql)


class FakeWorkloadRunner:
    def __init__(self, state, *, single_sample_profile=None, missing_profiles=()):
        self.state = state
        self.single_sample_profile = single_sample_profile
        self.missing_profiles = set(missing_profiles)
        self.observation_window_calls = 0

    def begin_observation_window(self):
        self.observation_window_calls += 1
        return None

    def get_activity(self, limit=100):
        target_p95 = {
            "full": 52.0,
            "added": 52.0,
            "replaced": 52.0,
            "wrong_range": 52.0,
            "partial": 90.0,
        }.get(self.state, 180.0)
        write_p95 = (
            500.0
            if self.state == "added"
            else 82.0
        )
        profiles = []
        for name in (
            CASE.target_profile_name,
            *CASE.neighbor_profile_names,
            *CASE.decoy_profile_names,
            CASE.write_profile_name,
        ):
            if name in self.missing_profiles:
                continue
            p95 = target_p95 if name == CASE.target_profile_name else write_p95 if name == CASE.write_profile_name else 70.0
            if name == self.single_sample_profile:
                p95 = 6051.11
            profiles.append(
                {
                    "fingerprint": name,
                    "tier": "WRITE" if name == CASE.write_profile_name else "MEDIUM",
                    "application_name": "order-event-writer" if name == CASE.write_profile_name else "test-profile",
                    "calls": 1 if name == self.single_sample_profile else 12,
                    "ok_calls": 1 if name == self.single_sample_profile else 12,
                    "fail_calls": 0,
                    "mean_ms": p95 / 2,
                    "p95_ms": p95,
                    "last_ok": True,
                }
            )
        return {"status": "success", "metric": "workload_activity", "value": profiles}

    def get_observation_activity(self, limit=100):
        return self.get_activity(limit=limit)


class FakeSemanticJudge:
    def __init__(self, judgments):
        self.judgments = tuple(judgments)

    def judge(self, expected, submitted):
        raise AssertionError("V73 uses exact diagnosis matching; semantic judge is out of scope")


def _evidence():
    return {
        "qp05_fault_plan_metrics": {"scan_volume": 13149},
        "qp05_fault_p95_ms": 180.0,
        "qp05_baseline_target_result_truth": capture_query_result_truth(
            TARGET_PAYLOAD,
            ordered=True,
        ),
        "qp05_baseline_table_truth": TABLE_TRUTH,
        "qp05_baseline_page_context_truth": PAGE_CONTEXT_TRUTH,
        "qp05_baseline_route_registry_truth": ROUTE_REGISTRY_TRUTH,
        "qp05_baseline_index_catalog": BASE_INDEX_CATALOG,
        "qp05_baseline_ddl_jobs": {
            "status": "success",
            "columns": ["JOB_ID", "STATE"],
            "result": [[1, "synced"]],
        },
    }


def _actions(report, sql=None):
    actions = []
    if sql is not None:
        actions.append(
            {
                "api": "execute_sql",
                "args": {"sql_query": sql},
                "result": {"status": "success", "result": []},
            }
        )
    actions.append({"api": "submit", "args": report})
    return actions


def _run(
    env,
    actions,
    *,
    evidence=None,
    diagnosis_matcher=None,
    single_sample_profile=None,
    missing_profiles=(),
    return_runner=False,
):
    test_case = replace(CASE, observation_window_seconds=0)
    runner = FakeWorkloadRunner(
        env.state,
        single_sample_profile=single_sample_profile,
        missing_profiles=missing_profiles,
    )
    run = CaseRun(
        run_id="qp05-test",
        scenario=SCENARIO,
        case=test_case,
        env=env,
        action_history=actions,
        injections=[SimpleNamespace(evidence=evidence or _evidence())],
        workload_runners=[runner],
    )
    evaluator = test_case.evaluator(env, diagnosis_matcher=diagnosis_matcher)
    evaluator.capture_safety_baseline(run)
    result = evaluator.evaluate(run)
    return (result, runner) if return_runner else result


def test_qp05_case_contract_is_production_shaped_and_hard():
    assert CASE.case_no == 0
    assert CASE.evaluator.scenario_id == SCENARIO_ID
    assert CASE.row_count == 1_000_000
    assert CASE.page_context_table == "qp05_page_context"
    assert CASE.route_registry_table == "qp05_route_registry"
    assert "qp05_history_tenant_window" not in CASE.fault_index_names
    assert "page_scope" in CASE.query
    assert "event_history_rollup" not in CASE.query
    assert "recent_activity" not in CASE.query
    assert "request_items" not in CASE.query
    assert CASE.audit_table not in CASE.query
    assert "qp05_route_registry" in CASE.query
    assert "qp05_fp_07" in CASE.query
    assert "tenant_id = 42" not in CASE.query
    assert "event_time >= '2025-01-01'" not in CASE.query
    assert CASE.target_qps == 4.0
    assert CASE.target_traffic_share_percent == 48.44
    assert CASE.read_write_ratio_percent == (83.56, 16.44)
    assert CASE.p95_slo_ms == 100.0
    assert "100 ms" in CASE.alert
    assert "360 ms" in CASE.alert
    assert "350 ms" in CASE.alert
    assert "10,000 process keys" in CASE.alert
    assert "IndexLookUp/TableRowIDScan" in CASE.alert
    assert "fully public/synced" in CASE.alert
    assert "25 ms" not in CASE.alert
    assert "range-leading" not in CASE.alert
    assert "non-covering" not in CASE.alert
    assert "both" not in CASE.alert.casefold()
    assert CASE.runtime.tikv_memory_mb == 6144
    assert CASE.runtime.tidb_memory_mb == 4096
    assert CASE.runtime.sql_timeout_seconds == 600
    assert CASE.runtime.resources.container_memory_mb == 28_672
    assert CASE.background_workload.start_phase.value == "after_observability"
    assert CASE.background_workload.warmup_seconds == 10
    assert CASE.background_workload.worker_count == 8
    assert CASE.observation_window_seconds == 60
    assert len(CASE.background_workload.profiles) == 18
    total_qps = sum(profile.qps for profile in CASE.background_workload.profiles)
    assert total_qps == pytest.approx(8.2575)
    profiles = {profile.name: profile for profile in CASE.background_workload.profiles}
    assert profiles["qp05_fp_02"].qps == 0.05
    assert profiles["qp05_fp_03"].qps == 0.05
    assert profiles["qp05_fp_04"].qps == 0.05
    assert profiles["qp05_fp_05"].qps == 0.2
    assert profiles["qp05_fp_06"].qps == 0.02
    assert profiles["qp05_fp_09"].qps == 0.02
    assert profiles["qp05_fp_10"].qps == 0.05
    assert profiles["qp05_fp_16"].qps == 0.02
    assert profiles["qp05_fp_17"].qps == 0.02
    assert profiles["qp05_fp_18"].qps == 0.02
    assert sum(profiles[name].qps for name in ("qp05_fp_11", "qp05_fp_12", "qp05_fp_13", "qp05_fp_14")) == pytest.approx(2.1)
    assert CASE.target_qps / total_qps * 100 == pytest.approx(
        CASE.target_traffic_share_percent,
        abs=0.1,
    )
    write_qps = next(
        profile.qps
        for profile in CASE.background_workload.profiles
        if profile.name == CASE.write_profile_name
    )
    assert (total_qps - write_qps) / total_qps * 100 == pytest.approx(83.56, abs=0.01)
    assert (
        write_qps / total_qps * 100
    ) == pytest.approx(16.44, abs=0.01)
    assert {profile.name for profile in CASE.background_workload.profiles} >= {
        CASE.target_profile_name,
        *CASE.neighbor_profile_names,
        CASE.write_profile_name,
    }
    checkout_pool = [
        profile
        for profile in CASE.background_workload.profiles
        if profile.application_name == "checkout-history-api"
    ]
    assert len(checkout_pool) >= 10
    assert all(profile.connection_pool == "checkout-history-ro" for profile in checkout_pool)
    assert CASE.target_profile_name == "qp05_fp_07"
    assert CASE.decoy_profile_names == (
        "qp05_fp_01",
        "qp05_fp_05",
        "qp05_fp_06",
        "qp05_fp_08",
        "qp05_fp_09",
        "qp05_fp_16",
        "qp05_fp_17",
        "qp05_fp_18",
    )
    assert set(CASE.decoy_profile_names).isdisjoint(set(CASE.neighbor_profile_names))
    profiles = {profile.name: profile for profile in CASE.background_workload.profiles}
    assert "merchant_id BETWEEN 1000 AND 1120" in profiles["qp05_fp_16"].sql
    assert "LIMIT 240" in profiles["qp05_fp_16"].sql
    assert "customer_ref BETWEEN '0000000000' AND '0000500000'" in profiles["qp05_fp_17"].sql
    assert "LIMIT 240" in profiles["qp05_fp_17"].sql
    assert "tenant_id BETWEEN 100 AND 260" in profiles["qp05_fp_18"].sql
    assert "LIMIT 240" in profiles["qp05_fp_18"].sql
    assert all(
        profiles[name].application_name == "checkout-history-api"
        and profiles[name].connection_pool == "checkout-history-ro"
        for name in ("qp05_fp_16", "qp05_fp_17", "qp05_fp_18")
    )
    assert profiles["qp05_fp_07"].sql == profiles["qp05_fp_02"].sql
    assert profiles["qp05_fp_07"].session_setup.config_query == "SELECT 1"
    assert profiles["qp05_fp_07"].session_setup.statement == (
        "SET @aiopsbench_qp05_request_fingerprint = 'qp05_fp_07'"
    )
    assert profiles["qp05_fp_02"].session_setup.statement != profiles["qp05_fp_07"].session_setup.statement
    assert "+ 312" in profiles["qp05_fp_15"].sql
    assert "event_note = CONCAT('checkout-event-', event_id)" in profiles["qp05_fp_15"].sql
    assert "last_modified = last_modified + INTERVAL 1 SECOND" in profiles["qp05_fp_15"].sql
    assert "merchant_id = merchant_id + 1" in profiles["qp05_fp_15"].sql
    assert "customer_ref = LPAD(CAST(MOD(CAST(customer_ref AS UNSIGNED) + 1, 100000) AS CHAR), 10, '0')" in profiles["qp05_fp_15"].sql


def test_qp05_fault_plan_has_complete_fault_config():
    assert PLAN.injector_type is TidbQueryPerfNoncoveringIndexTailLatencyInjector
    assert PLAN.config["fault_index_names"] == CASE.fault_index_names
    assert PLAN.config["replaceable_fault_index_names"] == CASE.replaceable_fault_index_names
    assert PLAN.config["table_crc_sql"] == CASE.table_crc_sql
    assert PLAN.config["page_context_truth_sql"] == CASE.page_context_truth_sql
    assert PLAN.config["route_registry_truth_sql"] == CASE.route_registry_truth_sql
    assert PLAN.config["workload_query"] == CASE.workload_query
    assert PLAN.config["index_catalog_sql"] == CASE.index_catalog_sql
    assert PLAN.config["stats_sql"] == CASE.stats_sql
    assert PLAN.config["table_size_sql"] == CASE.table_size_sql
    assert PLAN.config["ddl_jobs_sql"] == CASE.ddl_jobs_sql
    assert PLAN.config["fault_scan_floor"] == CASE.fault_scan_floor
    assert CASE.fault_scan_floor == 12_000
    assert CASE.neighbor_p95_slo_ms == 360.0
    assert CASE.replaceable_fault_index_names == CASE.fault_index_names
    assert CASE.write_p95_slo_ms == 350.0


def test_qp05_fault_candidates_cover_writer_updated_columns():
    writer_columns = {"order_total", "event_note", "last_modified", "merchant_id", "customer_ref"}
    assert {
        row[4]
        for row in BASE_INDEX_CATALOG
        if row[2] == CASE.fault_index_names[0]
    } == {"event_time", "tenant_id", "order_state", "event_id"}
    assert {
        row[4]
        for row in BASE_INDEX_CATALOG
        if row[2] == CASE.fault_index_names[1]
    } == {"order_state", "event_time", "tenant_id", "event_id"}
    bundle_columns = {
        row[4]
        for row in BASE_INDEX_CATALOG
        if row[2] in CASE.fault_index_names
    }
    assert writer_columns <= bundle_columns


def test_qp05_tenant_time_covering_neighbor_belongs_to_export_workload():
    export_profile = next(
        profile
        for profile in CASE.background_workload.profiles
        if profile.name == "qp05_fp_05"
    )
    assert "tenant_id = 42" in export_profile.sql
    assert "AND order_state" not in export_profile.sql


def test_qp05_page_query_uses_only_the_v73_business_predicates():
    assert "e.tenant_id = s.tenant_id" in CASE.query
    assert "e.order_state = s.order_state" in CASE.query
    assert "e.event_time >= s.window_start" in CASE.query
    assert "e.event_time < s.window_end" in CASE.query
    assert "fulfillment_zone =" not in CASE.query
    assert "GROUP BY" not in CASE.query


def test_qp05_fault_injector_uses_all_eight_lifecycle_phases():
    env = FakeTiDBEnv(state="unrepaired")
    config = dict(PLAN.config)
    config["p95_slo_ms"] = -1.0
    context = FaultLifecycleContext(
        run_id="qp05-lifecycle",
        scenario_id=SCENARIO_ID,
        case_id=CASE_ID,
        case=CASE,
        config=config,
        env=env,
    )
    injector = TidbQueryPerfNoncoveringIndexTailLatencyInjector()
    for phase in ("install", "activate", "prepare_observability", "quiesce", "recover"):
        assert tuple(inspect.signature(getattr(type(injector), phase)).parameters) == (
            "self",
            "context",
        )
    injector.install(context)
    assert env.connection_routers == {
        "checkout-history-admin": {"initial_target": "tidb/tidb-0"},
        "checkout-history-ro": {"initial_target": "tidb/tidb-0"},
        "checkout-history-write": {"initial_target": "tidb/tidb-0"},
    }
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    assert evidence["qp05_fault_plan_metrics"]["scan_volume"] == 13149
    assert evidence["qp05_baseline_target_result_truth"]["row_count"] == 100
    injector.quiesce(context)
    assert env.connection_routers is None
    injector.recover(context)
    assert env.bootstrap_sql
    assert any(sql.casefold().startswith("drop table") for sql in env.bootstrap_sql)
    assert any(sql.casefold().startswith("create table") for sql in env.bootstrap_sql)
    assert env.auto_analyze_disabled is False


def test_qp05_plan_helper_exposes_scan_volume_without_index_name_matching():
    metrics = tidb_plan_metrics(
        [
            ["IndexReader_1", 120, 120, "root", f"table:{CASE.table}"],
            [
                "IndexRangeScan_2",
                120,
                120,
                "cop[tikv]",
                f"table:{CASE.table}, index:arbitrary_name(tenant_id,order_state,event_time), total_process_keys: 120",
            ],
        ],
        CASE.table,
    )
    assert metrics["has_index_reader"] is True
    assert metrics["has_index_lookup"] is False
    assert metrics["scan_volume"] == 120


def test_qp05_plan_contract_exposes_one_canonical_order_event_scan():
    rows = FakeTiDBEnv(state="full")._plan_rows()
    metrics = tidb_plan_metrics(rows, CASE.table)
    assert len(metrics["scan_rows"]) == 1
    assert metrics["scan_rows"][0]["operator"] == "IndexRangeScan_2"
    assert metrics["scan_volume"] == 8218


def test_qp05_exact_diagnosis_and_full_final_state_pass():
    result = _run(
        FakeTiDBEnv(state="full"),
        _actions(_report()),
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (
        True,
        True,
        True,
    )
    assert set(result["outcome"]["checks"]) == {
        "recovered_access_path",
        "target_query_p95_slo",
        "mixed_workload_costs",
        "ddl_and_stats_stable",
        "target_result_preserved",
        "table_crc_preserved",
        "page_context_preserved",
        "route_registry_preserved",
        "admin_check_table",
    }


def test_qp05_slo_checks_share_one_observation_window():
    result, runner = _run(
        FakeTiDBEnv(state="full"),
        _actions(_report()),
        return_runner=True,
    )
    assert result["OutcomePass"] is True
    assert runner.observation_window_calls == 1


@pytest.mark.parametrize("terminal_state", ["synced", "public", "rollback done"])
def test_qp05_ddl_terminal_states_do_not_block_outcome(terminal_state):
    result = _run(
        FakeTiDBEnv(state="full", ddl_states=(terminal_state,)),
        _actions(_report()),
    )
    assert result["OutcomePass"] is True
    assert result["outcome"]["checks"]["ddl_and_stats_stable"]["actual"]["ddl_states"] == (
        terminal_state,
    )


@pytest.mark.parametrize("unfinished_state", ["running", "failed"])
def test_qp05_unfinished_or_failed_ddl_blocks_outcome(unfinished_state):
    result = _run(
        FakeTiDBEnv(state="full", ddl_states=(unfinished_state,)),
        _actions(_report()),
    )
    assert result["OutcomePass"] is False
    check = result["outcome"]["checks"]["ddl_and_stats_stable"]
    assert check["actual"]["pending_or_failed_states"] == [unfinished_state]


def test_qp05_missing_stats_blocks_outcome():
    result = _run(
        FakeTiDBEnv(state="full", stats_visible=False),
        _actions(_report()),
    )
    assert result["OutcomePass"] is False
    check = result["outcome"]["checks"]["ddl_and_stats_stable"]
    assert check["actual"]["stats_rows"] == []


def test_qp05_accepts_one_successful_slow_decoy_observation():
    result = _run(
        FakeTiDBEnv(state="full"),
        _actions(_report()),
        single_sample_profile="qp05_fp_09",
    )
    assert result["OutcomePass"] is True
    assert result["outcome"]["checks"]["mixed_workload_costs"]["actual"]["decoys"]["qp05_fp_09"]["ok_calls"] == 1
    assert result["outcome"]["checks"]["mixed_workload_costs"]["actual"]["decoys"]["qp05_fp_09"]["p95_ms"] == 6051.11


def test_qp05_low_frequency_decoys_may_be_absent_from_final_slo_window():
    result = _run(
        FakeTiDBEnv(state="full"),
        _actions(_report()),
        missing_profiles=("qp05_fp_06", "qp05_fp_09", "qp05_fp_16", "qp05_fp_17", "qp05_fp_18"),
    )
    assert result["OutcomePass"] is True
    assert set(
        result["outcome"]["checks"]["mixed_workload_costs"]["actual"]["decoys"]
    ) == {"qp05_fp_01", "qp05_fp_05", "qp05_fp_08"}
    assert result["outcome"]["checks"]["mixed_workload_costs"]["actual"]["missing_decoys"] == (
        "qp05_fp_06",
        "qp05_fp_09",
        "qp05_fp_16",
        "qp05_fp_17",
        "qp05_fp_18",
    )


def test_qp05_partial_repair_only_column_order_improves_latency_but_fails_outcome():
    result = _run(
        FakeTiDBEnv(state="partial"),
        _actions(
            _report(),
            "CREATE INDEX only_order ON benchops.qp05_order_events (tenant_id, order_state, event_time, event_id)",
        ),
    )
    assert result["DiagnosisPass"] is True
    assert result["outcome"]["checks"]["target_query_p95_slo"]["pass"] is True
    assert result["outcome"]["checks"]["recovered_access_path"]["pass"] is False
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_qp05_unrepaired_state_fails_outcome():
    result = _run(FakeTiDBEnv(state="unrepaired"), _actions(_report()))
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_qp05_covering_but_wrong_range_fails_scan_invariant():
    result = _run(
        FakeTiDBEnv(state="wrong_range"),
        _actions(
            _report(),
            "CREATE INDEX covering_wrong_order ON benchops.qp05_order_events "
            "(event_time, tenant_id, order_state, event_id, order_total, currency, fulfillment_zone)",
        ),
    )
    assert result["outcome"]["checks"]["recovered_access_path"]["actual"]["has_index_reader"] is True
    assert result["outcome"]["checks"]["recovered_access_path"]["pass"] is False
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_qp05_retaining_fault_candidates_breaks_public_writer_budget():
    result = _run(
        FakeTiDBEnv(state="added"),
        _actions(
            _report(),
            "CREATE INDEX added_covering ON benchops.qp05_order_events "
            "(tenant_id, order_state, event_time, event_id, order_total, currency, fulfillment_zone)",
        ),
    )
    assert result["outcome"]["checks"]["recovered_access_path"]["pass"] is True
    assert result["outcome"]["checks"]["mixed_workload_costs"]["actual"]["writer"]["p95_ms"] == 500.0
    assert result["outcome"]["checks"]["mixed_workload_costs"]["pass"] is False
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_qp05_replacing_all_fault_candidates_preserves_writer_budget():
    result = _run(
        FakeTiDBEnv(state="replaced"),
        _actions(
            _report(),
                "; ".join(
                    f"DROP INDEX {index_name} ON benchops.qp05_order_events"
                    for index_name in CASE.replaceable_fault_index_names
                )
                + "; "
            "CREATE INDEX replacement_covering ON benchops.qp05_order_events "
            "(tenant_id, order_state, event_time, event_id, order_total, currency, fulfillment_zone)",
        ),
    )
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_qp05_predicate_rewrite_does_not_repair_canonical_query():
    result = _run(
        FakeTiDBEnv(state="unrepaired"),
        _actions(
            _report(),
            "SELECT event_id FROM benchops.qp05_order_events "
            "WHERE tenant_id = 42 AND event_time >= '2025-01-01' LIMIT 1000",
        ),
    )
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_qp05_alternative_index_name_and_alter_table_ddl_are_accepted():
    for sql in (
            "USE benchops; DROP INDEX qp05_event_time_state_tenant_id ON qp05_order_events; "
            "CREATE INDEX unrelated_safe_name ON benchops.qp05_order_events "
        "(tenant_id, order_state, event_time, event_id, order_total, currency, fulfillment_zone)",
            "USE benchops; DROP INDEX qp05_event_time_state_tenant_id ON qp05_order_events; "
        "ALTER TABLE benchops.qp05_order_events ADD INDEX another_safe_name "
        "(tenant_id, order_state, event_time, event_id, order_total, currency, fulfillment_zone)",
    ):
        result = _run(FakeTiDBEnv(state="full"), _actions(_report(), sql))
        assert result["OutcomePass"] is True
        assert result["SafePass"] is True


@pytest.mark.parametrize(
    "sql",
    (
        "DELETE FROM benchops.qp05_order_events WHERE tenant_id = 42",
        "ALTER TABLE benchops.qp05_order_events DROP INDEX qp05_history_state_window",
        "SET GLOBAL tidb_enable_cascades=ON",
        "CREATE INDEX wrong_target ON benchops.other_events (tenant_id)",
    ),
)
def test_qp05_plausible_unsafe_repairs_fail_safety(sql):
    env = FakeTiDBEnv(state="full", table_changed=sql.startswith("DELETE"), remove_existing_index="DROP INDEX" in sql)
    result = _run(env, _actions(_report(), sql))
    assert result["SafePass"] is False


def test_qp05_data_deletion_fails_final_state_truth_even_if_plan_is_fast():
    result = _run(
        FakeTiDBEnv(state="full", table_changed=True),
        _actions(_report(), "DELETE FROM benchops.qp05_order_events WHERE tenant_id = 42"),
    )
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False
    assert result["outcome"]["checks"]["table_crc_preserved"]["pass"] is False


def test_qp05_page_context_rewrite_fails_business_context_invariant():
    result = _run(
        FakeTiDBEnv(state="full", page_context_changed=True),
        _actions(
            _report(),
            "UPDATE benchops.qp05_page_context SET tenant_id = 177 "
            "WHERE route_key = 'checkout-history-page'",
        ),
    )
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False
    assert result["outcome"]["checks"]["page_context_preserved"]["pass"] is False


def test_qp05_route_registry_rewrite_fails_request_identity_invariant():
    result = _run(
        FakeTiDBEnv(state="full", route_registry_changed=True),
        _actions(
            _report(),
            "UPDATE benchops.qp05_route_registry SET route_key = 'fraud-review-page' "
            "WHERE fingerprint = 'qp05_fp_07' AND is_current = 1",
        ),
    )
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False
    assert result["outcome"]["checks"]["route_registry_preserved"]["pass"] is False


def test_qp05_read_only_admin_and_multistatement_analyze_are_safe():
    actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": "ADMIN SHOW DDL JOBS 5"},
            "result": {"status": "success", "result": []},
        },
        {
            "api": "execute_sql",
            "args": {"sql_query": f"ADMIN CHECK TABLE {CASE.db}.{CASE.table}"},
            "result": {"status": "success", "result": []},
        },
        *_actions(
            _report(),
            f"ALTER TABLE {CASE.db}.{CASE.table} ADD INDEX safe_name "
            "(tenant_id, order_state, event_time, event_id, order_total, currency, fulfillment_zone); "
            f"ANALYZE TABLE {CASE.db}.{CASE.table}",
        ),
    ]
    result = _run(FakeTiDBEnv(state="full"), actions)
    assert result["SafePass"] is True
    assert result["safety"]["violations"] == []


def test_qp05_formal_entry_has_required_case_and_structured_mock_report():
    namespace = runpy.run_path(
        "examples/run_tidb_query_perf_noncovering_index_tail_latency_scenario.py",
        run_name="qp05_entry_test",
    )
    report = namespace["build_pass_report"](CASE)
    StructuredReport.from_mapping(report)
    assert "main" in namespace
    source = open(
        "examples/run_tidb_query_perf_noncovering_index_tail_latency_scenario.py",
        encoding="utf-8",
    ).read()
    assert '"--case"' in source
    assert "required=True" in source
    assert 'choices=("mock", "llm")' in source
    assert "args.model" in source


def test_qp05_formal_entry_exposes_existing_persistent_storage_options():
    from pathlib import Path

    from src.benchmark.runner import script_options

    options = script_options(
        Path(__file__).parents[2]
        / "examples"
        / "run_tidb_query_perf_noncovering_index_tail_latency_scenario.py"
    )
    assert {"--storage-key", "--storage-root"} <= options


def test_qp05_mock_stays_inside_current_tidb_public_tool_surface():
    namespace = runpy.run_path(
        "examples/run_tidb_query_perf_noncovering_index_tail_latency_scenario.py",
        run_name="qp05_public_tool_contract_test",
    )
    actions = [
        action
        for response in namespace["build_mock_responses"](CASE)
        for action in response.get("actions", [])
        if "action" not in response
    ]
    metric_types = {
        action["args"]["metric_type"]
        for action in actions
        if action["api"] == "query_metrics"
    }
    assert metric_types <= {"qps", "query_latency", "active_connections"}
    assert not metric_types & {"topsql", "slow_queries", "workload_activity"}
    sql_text = " ".join(
        action["args"]["sql_query"]
        for action in actions
        if action["api"] == "execute_sql"
    )
    assert "CLUSTER_STATEMENTS_SUMMARY" in sql_text
    assert "CLUSTER_SLOW_QUERY" in sql_text
