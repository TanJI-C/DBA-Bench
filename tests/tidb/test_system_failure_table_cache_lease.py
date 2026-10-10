import inspect
import json
import runpy
import threading
from pathlib import Path
from types import SimpleNamespace

import pymysql
import pytest

from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import SemanticConditionJudgment, SemanticJudgment
from src.database.query_results import capture_query_result_truth
from src.scenarios.base import CaseRun, FaultLifecycleContext
from src.scenarios.tidb import TidbSystemFailureTableCacheLeaseScenario
from src.scenarios.tidb.runtime import TIDB_V8_1_0
from src.execution.environment import TiDBEnv
from src.scenarios.tidb.system_failure.table_cache_lease import (
    TidbSystemFailureTableCacheLeaseInjector,
)


SCENARIO = TidbSystemFailureTableCacheLeaseScenario()
CASE = SCENARIO.get_case("table_cache_lease_write_conflict")
PLAN = SCENARIO.build_fault_plan(CASE)[0]
BUSINESS_TRUTH = {
    "columns": ["COUNT(*)", "COALESCE(SUM(sku_id), 0)", "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', sku_id, tenant_id, category, price, stock))), 0)"],
    "result": [[256, 32640, 123456]],
    "row_count": 1,
}
BUSINESS_PAYLOAD = {"status": "success", **BUSINESS_TRUTH}


class FakeDeployment:
    run_id = "table-cache-lease-test"
    primary_tidb_endpoint = ("127.0.0.1", 4300)
    warm_tidb_readiness_timeout_sec = 47
    tidb_endpoints = {
        "tidb/tidb-0": ("127.0.0.1", 4300),
        "tidb/tidb-1": ("127.0.0.1", 4302),
    }

    def __init__(self):
        self.running = {
            "tidb/tidb-0": True,
            "tidb/tidb-1": False,
        }
        self.actions = []

    def node_states(self):
        return {
            target: {"running": running}
            for target, running in self.running.items()
        }

    def start_component(self, target):
        self.actions.append(("start", target))
        self.running[target] = True

    def wait_for_target(self, target, timeout):
        self.actions.append(("wait", target, timeout))


class EvaluatorEnv:
    def __init__(self):
        self.cached = True
        self.cached_tables = set((*CASE.cache_table_names, *CASE.healthy_cache_table_names))
        self.cache_marker = " /* CACHED ON */"
        self.lease = 3
        self.table_ids = {
            CASE.cache_table: 9007,
            CASE.orders_table: 9009,
            CASE.inventory_table: 9011,
            CASE.pricing_table: 9013,
            CASE.healthy_cache_table_names[0]: 9017,
        }
        self.metadata_present_after_nocache = False
        self.deployment = FakeDeployment()
        self.sql = []
        self.integrity = {
            CASE.cache_table: (256, 32640, 123456),
            CASE.orders_table: (2048, 2096128, 223344),
            CASE.inventory_table: (1024, 130560, 445566),
            CASE.pricing_table: (128, 8256, 778899),
            CASE.healthy_cache_table_names[0]: (64, 323200, 889900),
        }

    def _success(self, columns=(), rows=()):
        return json.dumps({
            "status": "success",
            "columns": list(columns),
            "result": [list(row) for row in rows],
            "row_count": len(rows),
        })

    def execute_sql(self, sql, target=None):
        self.sql.append(sql)
        normalized = " ".join(sql.casefold().split())
        for table in (*CASE.cache_table_names, *CASE.healthy_cache_table_names):
            prefix = f"alter table benchops.{table}"
            if normalized.startswith(prefix) and normalized.endswith(" nocache"):
                self.cached_tables.discard(table)
                self.cached = bool(self.cached_tables)
                return self._success()
            if normalized.startswith(prefix) and normalized.endswith(" cache"):
                self.cached_tables.add(table)
                self.cached = True
                return self._success()
        if normalized.startswith("drop table"):
            for table in (*CASE.cache_table_names, *CASE.healthy_cache_table_names):
                if f"benchops.{table}" in normalized:
                    self.cached_tables.discard(table)
                    self.cached = bool(self.cached_tables)
                    return self._success()
        if normalized.startswith("set global tidb_table_cache_lease"):
            self.lease = int(normalized.rsplit("=", 1)[1].strip())
            return self._success()
        if "show global variables like 'tidb_table_cache_lease'" in normalized:
            return self._success(("Variable_name", "Value"), (("tidb_table_cache_lease", str(self.lease)),))
        for table in (*CASE.cache_table_names, *CASE.healthy_cache_table_names):
            if f"show create table benchops.{table}" in normalized:
                marker = self.cache_marker if table in self.cached_tables else ""
                return self._success(("Table", "Create Table"), ((table, f"CREATE TABLE `{table}` (`id` bigint NOT NULL, PRIMARY KEY (`id`)){marker}"),))
        if "show create table benchops.ma02_orders" in normalized:
            return self._success(("Table", "Create Table"), ((CASE.orders_table, "CREATE TABLE ma02_orders (order_id bigint primary key, amount decimal(12,2))"),))
        if "show create table benchops.ma02_inventory" in normalized:
            return self._success(("Table", "Create Table"), ((CASE.inventory_table, "CREATE TABLE ma02_inventory (sku_id bigint, warehouse_id int, primary key (sku_id, warehouse_id))"),))
        if "select tidb_table_id from information_schema.tables" in normalized:
            for table, table_id in self.table_ids.items():
                if f"table_name = '{table}'" in normalized:
                    return self._success(("TIDB_TABLE_ID",), ((table_id,),))
            raise AssertionError(f"fake table-cache-lease table ID query did not name a cached table: sql={sql!r}")
        if "from mysql.table_cache_meta" in normalized:
            rows = []
            for table, table_id in self.table_ids.items():
                if f"tid = {table_id}" in normalized and (table in self.cached_tables or self.metadata_present_after_nocache):
                    rows.append((table_id, "READ", 100, 90))
            return self._success(("tid", "lock_type", "lease", "oldReadLease"), rows)
        if "coalesce(sum(sku_id)" in normalized and "from benchops.ma02_product_catalog" in normalized:
            return self._success(BUSINESS_TRUTH["columns"], BUSINESS_TRUTH["result"])
        if "from benchops.ma02_orders" in normalized and "coalesce(sum(order_id)" in normalized:
            return self._success(("COUNT(*)", "SUM(order_id)", "BIT_XOR"), (self.integrity[CASE.orders_table],))
        if "from benchops.ma02_inventory" in normalized and "coalesce(sum(sku_id)" in normalized:
            return self._success(("COUNT(*)", "SUM(sku_id)", "BIT_XOR"), (self.integrity[CASE.inventory_table],))
        if f"from benchops.{CASE.pricing_table}" in normalized and "coalesce(sum(rule_id)" in normalized:
            return self._success(("COUNT(*)", "SUM(rule_id)", "BIT_XOR"), (self.integrity[CASE.pricing_table],))
        if f"from benchops.{CASE.healthy_cache_table_names[0]}" in normalized and "coalesce(sum(sku_id)" in normalized:
            return self._success(("COUNT(*)", "SUM(sku_id)", "BIT_XOR"), (self.integrity[CASE.healthy_cache_table_names[0]],))
        if "information_schema.tables" in normalized and "count(*)" in normalized:
            return self._success(("COUNT(*)",), ((5,),))
        if normalized.startswith("begin; select @ma02_tso := tidb_current_tso()"):
            return self._success(("@ma02_tso",), ((123456789,),))
        if normalized.startswith("show table status") or normalized.startswith("show create table"):
            return self._success(("value",), (("ok",),))
        if normalized.startswith(("create ", "drop ", "insert ", "analyze ")):
            return self._success()
        return self._success()

    def read_log(self, target, lines=200, **kwargs):
        match_key = kwargs.get("match_key")
        if match_key == f"UPDATE {CASE.db}.{CASE.orders_table}":
            content = (
                "WARN checkout retry transaction [kv:9007]Write conflict "
                f"key={{tableName={CASE.db}.{CASE.orders_table}, handle=9009}}"
            )
        elif match_key == "Write conflict":
            content = (
                "WARN checkout retry transaction [kv:9007]Write conflict "
                f"key={{tableName={CASE.db}.{CASE.orders_table}, handle=9009}}\n"
                "WARN lock cached table for read error=previous statement: update mysql.table_cache_meta "
                "[kv:9007]Write conflict key={tableName=mysql.table_cache_meta, handle=9007}, txnStartTS=1 conflictStartTS=2 conflictCommitTS=3\n"
                "WARN lock cached table for read error=previous statement: update mysql.table_cache_meta "
                "[kv:9007]Write conflict key={tableName=mysql.table_cache_meta, handle=9011}, txnStartTS=1 conflictStartTS=2 conflictCommitTS=3\n"
                "WARN lock cached table for read error=previous statement: update mysql.table_cache_meta "
                "[kv:9007]Write conflict key={tableName=mysql.table_cache_meta, handle=9013}, txnStartTS=1 conflictStartTS=2 conflictCommitTS=3"
            )
        elif match_key == "lock cached table for read":
            content = "WARN lock cached table for read"
        elif isinstance(match_key, str) and match_key.startswith("table_cache_meta, handle="):
            handle = match_key.rsplit("=", 1)[1]
            content = (
                "WARN lock cached table for read error=previous statement: update mysql.table_cache_meta "
                f"[kv:9007]Write conflict key={{tableName=mysql.table_cache_meta, handle={handle}}}, "
                "txnStartTS=1 conflictStartTS=2 conflictCommitTS=3"
            )
        else:
            raise AssertionError(f"fake table-cache-lease log query omitted or used unknown match_key: {match_key!r}")
        return json.dumps({
            "status": "success",
            "content": content,
        })

    def observe_metric(self, metric_type, target=None, **kwargs):
        return self.query_metrics(metric_type, target=target, **kwargs)

    def query_metrics(self, metric_type, target=None, **kwargs):
        if metric_type == "workload_activity":
            profiles = [
                {"fingerprint": name, "calls": 6, "ok_calls": 4, "fail_calls": 2, "last_ok": True}
                for name in CASE.target_profile_names
            ]
            return json.dumps({"status": "success", "metric": metric_type, "kind": "snapshot", "snapshot": {"profiles": profiles}})
        return json.dumps({"status": "success", "metric": metric_type, "kind": "series", "series": {}})

    def observe_metric(self, metric_type, target=None, limit=None):
        return self.query_metrics(metric_type, target=target, limit=limit)


class BusinessProbeEnv:
    def __init__(self):
        self.write_attempts = {17: 5, 18: 7, 19: 9}
        self.sql = []
        self.cursor_sql = []
        self.connection_applications = []
        self.closed_connections = []
        self.lock = threading.Lock()

    def _success(self, columns=(), rows=()):
        return json.dumps({
            "status": "success",
            "columns": list(columns),
            "result": [list(row) for row in rows],
            "row_count": len(rows),
        })

    def execute_sql(self, sql, target=None):
        self.sql.append(sql)
        normalized = " ".join(sql.casefold().split())
        if normalized.startswith("analyze table benchops."):
            return self._success()
        raise AssertionError(f"unexpected probe SQL: {sql!r}")

    def open_workload_connection(self, application_name, target=None):
        self.connection_applications.append((application_name, target))
        if application_name == "business-probe-baseline":
            role = "baseline"
        elif application_name == "business-probe-restore":
            role = "restore"
        else:
            role = int(application_name.rsplit("-", 1)[1])
        return BusinessProbeConnection(self, role)


class BusinessProbeConnection:
    def __init__(self, env, worker_id):
        self.env = env
        self.worker_id = worker_id
        self.pending_write = False
        self.worker1_failed_once = False
        self.restore_value = None
        self.order_id = None

    def cursor(self):
        return BusinessProbeCursor(self)

    def commit(self):
        if not self.pending_write:
            return
        if self.worker_id == "restore":
            with self.env.lock:
                self.env.write_attempts[self.order_id] = self.restore_value
            self.pending_write = False
            return
        if self.worker_id == 1 and not self.worker1_failed_once:
            self.worker1_failed_once = True
            raise pymysql.MySQLError(
                9007,
                f"Write conflict key={{tableName=benchops.ma02_orders, handle={self.order_id}}}",
            )
        with self.env.lock:
            self.env.write_attempts[self.order_id] += 1
        self.pending_write = False

    def rollback(self):
        self.pending_write = False

    def close(self):
        self.env.closed_connections.append(self.worker_id)


class BusinessProbeCursor:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql):
        self.conn.env.cursor_sql.append(sql)
        normalized = " ".join(sql.casefold().split())
        if normalized.startswith("select write_attempts from benchops.ma02_orders where order_id = "):
            self.conn.order_id = int(normalized.rsplit("order_id = ", 1)[1])
            self.conn.rows = ((self.conn.env.write_attempts[self.conn.order_id],),)
            return 1
        if normalized in {
            "set session tidb_txn_mode = 'optimistic'",
            "start transaction",
        }:
            return 0
        if normalized.startswith("update benchops.ma02_orders set write_attempts = write_attempts + 1 where order_id = "):
            self.conn.order_id = int(normalized.rsplit("order_id = ", 1)[1])
            self.conn.pending_write = True
            return 1
        if normalized.startswith("update benchops.ma02_orders set write_attempts = "):
            value, order = normalized.split("set write_attempts = ", 1)[1].split(" where order_id = ")
            self.conn.restore_value = int(value)
            self.conn.order_id = int(order)
            self.conn.pending_write = True
            return 1
        raise AssertionError(f"unexpected cursor SQL: {sql!r}")

    def fetchall(self):
        return self.conn.rows


def report(*, missing=False, contradiction=False):
    if missing:
        conditions = [{
            "type": "symptom",
            "factor": "the cluster has a QPS cliff",
            "entity": CASE.cache_table,
            "evidence": ["the alert reports 2PC failures"],
        }]
    elif contradiction:
        conditions = [{
            "type": "root_cause",
            "factor": next(iter(CASE.evaluator.diagnosis_conditions[0].contradictions)),
            "entity": "TiKV",
            "evidence": ["the alert mentions TiKV"],
        }]
    else:
        conditions = [
            {
                "type": "root_cause",
                "factor": next(alias for alias in CASE.evaluator.diagnosis_conditions[0].aliases if alias.startswith("the 2pc")),
                "entity": next(alias for alias in CASE.evaluator.diagnosis_conditions[0].aliases if alias.startswith("the cached")),
                "evidence": ["9007 and table_cache_meta"],
            },
            {
                "type": "mechanism",
                "factor": next(alias for alias in CASE.evaluator.diagnosis_conditions[1].aliases if alias.startswith("tidb internal")),
                "entity": next(alias for alias in CASE.evaluator.diagnosis_conditions[1].aliases if alias.startswith("tidb renews")),
                "evidence": ["lock cached table for read"],
            },
            {
                "type": "scope",
                "factor": next(alias for alias in CASE.evaluator.diagnosis_conditions[2].aliases if alias.startswith("multiple")),
                "entity": next(alias for alias in CASE.evaluator.diagnosis_conditions[2].aliases if alias.startswith("two tidb")),
                "evidence": ["cluster_info"],
            },
            {
                "type": "necessary_exclusion",
                "factor": next(alias for alias in CASE.evaluator.diagnosis_conditions[3].aliases if alias.startswith("the ordinary")),
                "entity": next(alias for alias in CASE.evaluator.diagnosis_conditions[3].aliases if alias.startswith("ordinary business")),
                "evidence": ["business truth and store state"],
            },
            {
                "type": "necessary_exclusion",
                "factor": next(alias for alias in CASE.evaluator.diagnosis_conditions[4].aliases if alias.startswith("the healthy")),
                "entity": next(alias for alias in CASE.evaluator.diagnosis_conditions[4].aliases if alias.startswith("the unrelated")),
                "evidence": ["reference cache marker and workload scope"],
            },
        ]
    return {
        "diagnosis": {"conditions": conditions},
        "outcome": {"changes": ["removed cached-table mode from all three causal cached business tables"], "verification": ["checked truth, workload, and preserved the healthy cached reference table"]},
        "summary": "The report identifies shared cached-table lease contention on all three causal business tables, excludes the healthy cached reference table, and preserves business state.",
    }


def paraphrased_report():
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "The transaction failures came from renewing the shared internal lease metadata rows for the cached business tables, not from a business row.",
                    "entity": "the mysql.table_cache_meta rows belonging to the product catalog and inventory tables",
                    "evidence": ["the conflict key names mysql.table_cache_meta and handle 9007"],
                },
                {
                    "type": "mechanism",
                    "factor": "A cached-table read updates its lease row while another read is doing the same, so the internal writes collide.",
                    "entity": "TiDB's internal cached-table read path",
                    "evidence": ["the logs say lock cached table for read"],
                },
                {
                    "type": "scope",
                    "factor": "Both TiDB servers read the cached business tables and contend on their shared leases.",
                    "entity": "tidb-0 and tidb-1 sharing the product catalog and inventory leases",
                    "evidence": ["cluster_info lists both TiDB instances"],
                },
                {
                    "type": "exclusion",
                    "factor": "The business hot-row and TiKV-capacity hypotheses are not the cause of these 9007 failures.",
                    "entity": "orders/inventory business rows and tikv-0 capacity",
                    "evidence": ["the conflict is on internal metadata and the business truth is unchanged"],
                },
                {
                    "type": "exclusion",
                    "factor": "The reference catalog is a healthy cached table outside the conflicting handles and target workload, so it must remain cached.",
                    "entity": "benchops.ma02_catalog_aux",
                    "evidence": ["its cache marker remains enabled and no target profile reads it"],
                },
            ]
        },
        "outcome": {"changes": ["removed cached-table mode from all three causal cached business tables"], "verification": ["checked truth, workload, and preserved the healthy cached reference table"]},
        "summary": "The report identifies shared cached-table lease contention on all three causal business tables, excludes the healthy cached reference table, and preserves business state.",
    }


def case_run(env, submitted, *, fixes=(), actions=()):
    evaluator = CASE.evaluator(env)
    baseline_run = CaseRun(run_id="table-cache-lease-baseline", scenario=SCENARIO, case=CASE, env=env)
    baseline_run.injections.append(SimpleNamespace(evidence={
        "business_result_truth": capture_query_result_truth(BUSINESS_PAYLOAD, ordered=True),
    }))
    evaluator.capture_safety_baseline(baseline_run)
    actions = list(actions)
    for fix in fixes:
        result = json.loads(env.execute_sql(fix))
        actions.append({"api": "execute_sql", "args": {"sql_query": fix}, "result": result})
    actions.append({"api": "submit", "args": submitted})
    baseline_run.action_history = actions
    return baseline_run


def test_case_identity_difficulty_and_real_business_noise_contract():
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert "lease" not in SCENARIO.description.casefold()
    assert "cached" not in SCENARIO.description.casefold()
    assert "business-row" not in SCENARIO.description.casefold()
    assert CASE.runtime.release is TIDB_V8_1_0
    assert CASE.runtime.topology.pd_count == 1
    assert CASE.runtime.topology.tikv_count == 1
    assert CASE.runtime.topology.tidb_count == 2
    assert len(CASE.background_workload.profiles) == 32
    assert CASE.cache_table_names == (CASE.cache_table, CASE.inventory_table, CASE.pricing_table)
    assert CASE.healthy_cache_table_names == ("ma02_catalog_aux",)
    assert len(CASE.target_profile_names) == 12
    assert len({profile.name for profile in CASE.background_workload.profiles}) == 32
    assert CASE.background_workload.worker_count == 12
    assert CASE.background_workload.start_phase.value == "after_faults"
    assert "2PC/Prewrite" in CASE.alert
    assert "table_cache" not in CASE.alert
    assert "common_false_lead" not in CASE.initial_state
    forbidden = ("decoy", "noise", "conflict", "target", "healthy", "reference", "protected")
    visible_text = "\n".join(
        f"{profile.name} {profile.tier} {profile.application_name or ''}"
        for profile in CASE.background_workload.profiles
    ).casefold()
    assert not [word for word in forbidden if word in visible_text]
    target_routes = {
        profile.name: profile.target
        for profile in CASE.background_workload.profiles
        if profile.name in CASE.target_profile_names
    }
    assert set(target_routes.values()) == {"tidb/tidb-0"}
    assert [profile.target for profile in CASE.background_workload.profiles if profile.name in {"lookup_variant_a", "rollup_variant_b"}] == ["tidb/tidb-0", "tidb/tidb-0"]
    assert not any(
        marker in f"{profile.name} {profile.application_name or ''}".casefold()
        for profile in CASE.background_workload.profiles
        if profile.name in {"lookup_variant_a", "rollup_variant_b"}
        for marker in ("snapshot", "catalog_snapshot", "reference")
    )


def test_fault_plan_is_complete_and_lifecycle_uses_current_protocol(monkeypatch):
    assert PLAN.injector_type is TidbSystemFailureTableCacheLeaseInjector
    assert PLAN.config == {
        "db": CASE.db,
        "cache_table": CASE.cache_table,
        "cache_table_names": CASE.cache_table_names,
        "pricing_table": CASE.pricing_table,
        "healthy_cache_table_names": CASE.healthy_cache_table_names,
        "orders_table": CASE.orders_table,
        "inventory_table": CASE.inventory_table,
        "catalog_row_count": CASE.catalog_row_count,
        "business_summary_sql": CASE.business_summary_sql,
        "table_integrity_sql": CASE.table_integrity_sql,
        "target_profile_names": CASE.target_profile_names,
    }
    for name in ("install", "activate", "prepare_observability", "quiesce", "recover"):
        assert tuple(inspect.signature(getattr(TidbSystemFailureTableCacheLeaseInjector, name)).parameters) == ("self", "context")

    env = EvaluatorEnv()
    context = FaultLifecycleContext(
        run_id="table-cache-lease-lifecycle",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=PLAN.config,
        env=env,
    )
    injector = TidbSystemFailureTableCacheLeaseInjector()
    monkeypatch.setattr(
        injector,
        "_run_business_conflict_probe",
        lambda env, targets, orders_table_id, *, order_id: {
            "orders_table_id": orders_table_id,
            "order_id": order_id,
            "targets": targets[:2],
            "commits": 1,
            "conflicts": 1,
            "retry_successes": 1,
            "errors": ("[kv:9007] Write conflict",),
        },
    )
    monkeypatch.setattr(injector, "_run_dual_cache_read", lambda env, targets, table, attempt: None)
    monkeypatch.setattr(injector, "_run_healthy_cache_read", lambda env, target, table, round_no: None)
    workload_call_snapshots = iter(
        (
            {name: 2 for name in CASE.target_profile_names},
            {name: 6 for name in CASE.target_profile_names},
        )
    )
    monkeypatch.setattr(
        injector,
        "_workload_profile_calls",
        lambda env: next(workload_call_snapshots),
    )
    injector.install(context)
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    injector.quiesce(context)
    injector.recover(context)
    assert set(evidence) == {
        "ma02_table_ids",
        "ma02_orders_table_id",
        "ma02_maintenance_burst",
        "ma02_interleaved_conflict_probe",
        "ma02_initial_business_phase",
        "ma02_cached_table_states",
        "ma02_lease_variable",
        "ma02_statement_summary",
        "business_result_truth",
        "ma02_cached_table_integrity",
        "ma02_tso_sample",
        "ma02_hidden_fault_logs",
        "ma02_initial_fault_logs",
        "ma02_qps_series",
        "ma02_query_latency_series",
    }
    assert env.cached is False
    assert env.cached_tables == set()
    assert "alter table benchops.ma02_product_catalog cache" in " ".join(env.sql).casefold()
    assert "alter table benchops.ma02_inventory cache" in " ".join(env.sql).casefold()
    assert "alter table benchops.ma02_pricing_rules cache" in " ".join(env.sql).casefold()
    assert "alter table benchops.ma02_product_catalog nocache" in " ".join(env.sql).casefold()
    assert "alter table benchops.ma02_inventory nocache" in " ".join(env.sql).casefold()
    assert "alter table benchops.ma02_pricing_rules nocache" in " ".join(env.sql).casefold()
    assert "alter table benchops.ma02_catalog_aux nocache" in " ".join(env.sql).casefold()
    assert env.deployment.actions == [
        ("start", "tidb/tidb-1"),
        ("wait", "tidb/tidb-1", 47),
    ]


def test_recovery_accepts_connection_loss_from_an_agent_stopped_tidb():
    injector = TidbSystemFailureTableCacheLeaseInjector()
    failure = RuntimeError("probe failed")
    failure.__cause__ = pymysql.OperationalError(2013, "Lost connection to MySQL server")
    injector._business_noise_failure = failure
    injector._business_noise_thread = threading.Thread(target=lambda: None)
    injector._business_noise_thread.start()

    injector._stop_business_conflict_noise(expected_stopped_targets=("tidb/tidb-1",))

    assert injector._business_noise_thread is None


def test_recovery_still_raises_unrelated_background_failure():
    injector = TidbSystemFailureTableCacheLeaseInjector()
    injector._business_noise_failure = RuntimeError("probe failed")
    injector._business_noise_thread = threading.Thread(target=lambda: None)
    injector._business_noise_thread.start()

    with pytest.raises(RuntimeError, match="business conflict noise failed"):
        injector._stop_business_conflict_noise(expected_stopped_targets=("tidb/tidb-1",))


def test_combined_conflict_verification_merges_separate_log_windows():
    injector = TidbSystemFailureTableCacheLeaseInjector()
    injector._configure(PLAN.config)
    targets = ("tidb/tidb-0", "tidb/tidb-1")
    cached_table_ids = {
        CASE.cache_table: 9007,
        CASE.inventory_table: 9011,
        CASE.pricing_table: 9013,
        CASE.healthy_cache_table_names[0]: 9017,
    }
    conflict_logs = {
        target: {
            "status": "success",
            "content": (
                "[kv:9007]Write conflict key={tableName=mysql.table_cache_meta, handle=9007}\n"
                "[kv:9007]Write conflict key={tableName=mysql.table_cache_meta, handle=9011}\n"
                "[kv:9007]Write conflict key={tableName=mysql.table_cache_meta, handle=9013}\n"
                "[kv:9007]Write conflict key={tableName=benchops.ma02_orders, handle=9009}"
            ),
            "match_key": "Write conflict",
        }
        for target in targets
    }
    read_path_logs = {
        target: {
            "status": "success",
            "content": "[cache.go:204] lock cached table for read",
            "match_key": "lock cached table for read",
        }
        for target in targets
    }

    combined = injector._combine_log_windows(conflict_logs, read_path_logs)

    injector._verify_combined_conflict_logs(combined, cached_table_ids, orders_table_id=9009)
    assert combined[targets[0]]["match_key"] == (
        "Write conflict",
        "lock cached table for read",
    )


def test_combined_conflict_verification_accepts_per_table_targeted_evidence_windows():
    injector = TidbSystemFailureTableCacheLeaseInjector()
    injector._configure(PLAN.config)
    targets = ("tidb/tidb-0", "tidb/tidb-1")
    cached_table_ids = {
        CASE.cache_table: 9007,
        CASE.inventory_table: 9011,
        CASE.pricing_table: 9013,
        CASE.healthy_cache_table_names[0]: 9017,
    }
    conflict_logs = {
        target: {
            "status": "success",
            "content": (
                "[kv:9007]Write conflict key={tableName=mysql.table_cache_meta, handle=9007}\n"
                "[kv:9007]Write conflict key={tableName=benchops.ma02_orders, handle=9009}"
            ),
            "match_key": "Write conflict",
        }
        for target in targets
    }
    read_path_logs = {
        target: {
            "status": "success",
            "content": "[cache.go:204] lock cached table for read",
            "match_key": "lock cached table for read",
        }
        for target in targets
    }

    def targeted_window(handle):
        return {
            target: {
                "status": "success",
                "content": f"[kv:9007]Write conflict key={{tableName=mysql.table_cache_meta, handle={handle}}}",
                "match_key": f"table_cache_meta, handle={handle}",
            }
            for target in targets
        }

    evidence_windows = {
        CASE.inventory_table: targeted_window(9011),
        CASE.pricing_table: targeted_window(9013),
    }

    flooded_combined = injector._combine_log_windows(conflict_logs, read_path_logs)
    with pytest.raises(RuntimeError, match="table-cache-lease combined conflict evidence is incomplete"):
        injector._verify_combined_conflict_logs(flooded_combined, cached_table_ids, orders_table_id=9009)

    combined = injector._combine_log_windows(conflict_logs, read_path_logs, *evidence_windows.values())
    injector._verify_combined_conflict_logs(combined, cached_table_ids, orders_table_id=9009)


def test_accumulate_conflict_evidence_only_stores_windows_containing_the_table_handle():
    injector = TidbSystemFailureTableCacheLeaseInjector()
    injector._configure(PLAN.config)
    cached_table_ids = {
        CASE.cache_table: 9007,
        CASE.inventory_table: 9011,
        CASE.pricing_table: 9013,
    }
    captured_match_keys = []

    class LogEnv:
        def __init__(self, content):
            self.content = content

        def read_log(self, target, lines=200, match_key=None):
            captured_match_keys.append(match_key)
            return {"status": "success", "target": target, "content": self.content, "match_key": match_key}

    evidence_windows = {}
    injector._accumulate_conflict_evidence(
        LogEnv("[kv:9007]Write conflict key={tableName=mysql.table_cache_meta, handle=9013}"),
        ("tidb/tidb-0", "tidb/tidb-1"),
        CASE.pricing_table,
        cached_table_ids,
        evidence_windows,
    )
    injector._accumulate_conflict_evidence(
        LogEnv("[kv:9007]Write conflict key={tableName=benchops.ma02_orders, handle=18}"),
        ("tidb/tidb-0", "tidb/tidb-1"),
        CASE.pricing_table,
        cached_table_ids,
        evidence_windows,
    )

    assert captured_match_keys == [
        injector._meta_conflict_match_key(9013),
        injector._meta_conflict_match_key(9013),
    ]
    assert list(evidence_windows) == [CASE.pricing_table]
    assert "handle=9013" in evidence_windows[CASE.pricing_table]["tidb/tidb-0"]["content"]


def test_top_up_conflict_evidence_reprobes_pending_tables_past_the_lease(monkeypatch):
    import time as time_module

    import src.scenarios.tidb.system_failure.table_cache_lease as module

    injector = TidbSystemFailureTableCacheLeaseInjector()
    injector._configure(PLAN.config)
    monkeypatch.setattr(module, "_TABLE_CACHE_LEASE_SECONDS", 0.2)
    monkeypatch.setattr(module, "_TABLE_CACHE_LEASE_LEASE_EXPIRY_MARGIN_SECONDS", 0.1)
    monkeypatch.setattr(module, "_TABLE_CACHE_LEASE_CONFLICT_EVIDENCE_TOP_UP_DEADLINE_SECONDS", 5)
    cached_table_ids = {
        CASE.cache_table: 9007,
        CASE.inventory_table: 9011,
        CASE.pricing_table: 9013,
    }
    probes = []
    injector._run_dual_cache_read = lambda env, targets, table, attempt: probes.append(
        (table, attempt, time_module.monotonic())
    )
    per_table_attempts = {}

    def accumulate(env, targets, table, cached_table_ids, evidence_windows):
        per_table_attempts[table] = per_table_attempts.get(table, 0) + 1
        if table != CASE.pricing_table or per_table_attempts[table] >= 2:
            evidence_windows[table] = {"status": "success"}

    injector._accumulate_conflict_evidence = accumulate
    evidence_windows = {}
    seeded_probe_time = time_module.monotonic()
    injector._top_up_conflict_evidence(
        object(),
        ("tidb/tidb-0", "tidb/tidb-1"),
        cached_table_ids,
        evidence_windows,
        {CASE.pricing_table: seeded_probe_time},
    )

    assert [probe[0] for probe in probes] == [
        CASE.cache_table,
        CASE.inventory_table,
        CASE.pricing_table,
        CASE.pricing_table,
    ]
    first_pricing_probe = probes[2][2]
    assert first_pricing_probe - seeded_probe_time >= 0.25
    assert list(evidence_windows) == [CASE.cache_table, CASE.inventory_table, CASE.pricing_table]


def test_top_up_conflict_evidence_raises_on_the_bounded_deadline(monkeypatch):
    import src.scenarios.tidb.system_failure.table_cache_lease as module

    injector = TidbSystemFailureTableCacheLeaseInjector()
    injector._configure(PLAN.config)
    monkeypatch.setattr(module, "_TABLE_CACHE_LEASE_CONFLICT_EVIDENCE_TOP_UP_DEADLINE_SECONDS", 0.0)
    injector._run_dual_cache_read = lambda env, targets, table, attempt: pytest.fail(
        "top-up must not probe past the bounded deadline"
    )

    with pytest.raises(RuntimeError, match="bounded top-up deadline"):
        injector._top_up_conflict_evidence(
            object(),
            ("tidb/tidb-0", "tidb/tidb-1"),
            {CASE.cache_table: 9007, CASE.inventory_table: 9011, CASE.pricing_table: 9013},
            {},
            {},
        )


def test_maintenance_burst_is_bounded_and_uses_real_business_tables():
    env = BusinessProbeEnv()
    injector = TidbSystemFailureTableCacheLeaseInjector()
    injector._configure(PLAN.config)

    evidence = injector._run_maintenance_burst(env, "tidb/tidb-0")

    assert evidence == {
        "target": "tidb/tidb-0",
        "tables": (CASE.orders_table, CASE.inventory_table),
        "completed": True,
    }
    assert env.sql[-2:] == [
        f"ANALYZE TABLE {CASE.db}.{CASE.orders_table}",
        f"ANALYZE TABLE {CASE.db}.{CASE.inventory_table}",
    ]


def test_business_conflict_probe_uses_real_update_then_restores_value():
    env = BusinessProbeEnv()
    injector = TidbSystemFailureTableCacheLeaseInjector()
    injector._configure(PLAN.config)

    evidence = injector._run_business_conflict_probe(
        env,
        ("tidb/tidb-0", "tidb/tidb-1"),
        orders_table_id=9009,
    )

    assert evidence["orders_table_id"] == 9009
    assert evidence["order_id"] == 17
    assert evidence["conflicts"] == 1
    assert evidence["retry_successes"] == 1
    assert env.write_attempts == {17: 5, 18: 7, 19: 9}
    cursor_sql = "\n".join(env.cursor_sql).casefold()
    assert "set write_attempts = write_attempts + 1" in cursor_sql
    assert "set write_attempts = write_attempts where order_id = 17" not in cursor_sql
    assert not env.sql
    assert {application for application, _target in env.connection_applications} == {
        "business-probe-baseline",
        "business-probe-restore",
        "checkout-retry-worker-0",
        "checkout-retry-worker-1",
    }
    assert len(env.closed_connections) == 4
    assert "update benchops.ma02_orders set write_attempts = write_attempts where order_id = 17" not in cursor_sql


def test_interleaved_conflict_burst_rotates_causal_tables_and_reads_healthy_companion():
    env = BusinessProbeEnv()
    injector = TidbSystemFailureTableCacheLeaseInjector()
    injector._configure(PLAN.config)
    cache_reads = []
    healthy_reads = []

    injector._run_dual_cache_read = lambda env, targets, table, attempt: cache_reads.append(
        (targets, table, attempt)
    )
    injector._run_healthy_cache_read = lambda env, target, table, round_no: healthy_reads.append(
        (target, table, round_no)
    )
    injector._accumulate_conflict_evidence = (
        lambda env, targets, table, cached_table_ids, evidence_windows: evidence_windows.setdefault(table, {})
    )

    evidence, evidence_windows = injector._run_interleaved_conflict_burst(
        env,
        ("tidb/tidb-0", "tidb/tidb-1"),
        {
            CASE.cache_table: 9007,
            CASE.inventory_table: 9011,
            CASE.pricing_table: 9013,
            CASE.healthy_cache_table_names[0]: 9017,
        },
        orders_table_id=9009,
    )

    assert evidence["rounds"] == 32
    assert evidence["business_probes_per_round"] == 2
    assert evidence["conflicts"] == 64
    assert evidence["retry_successes"] == 64
    assert evidence["commits"] == 64
    assert evidence["causal_rounds"] == {
        CASE.cache_table: 11,
        CASE.inventory_table: 11,
        CASE.pricing_table: 10,
    }
    assert evidence["healthy_reads"] == 32
    assert evidence["evidence_tables"] == (CASE.cache_table, CASE.inventory_table, CASE.pricing_table)
    assert evidence_windows == {table: {} for table in evidence["evidence_tables"]}
    assert len(evidence["per_round"]) == 32
    assert [round_evidence["round"] for round_evidence in evidence["per_round"]] == list(range(1, 33))
    assert [round_evidence["causal_table"] for round_evidence in evidence["per_round"]] == [
        CASE.cache_table,
        CASE.inventory_table,
        CASE.pricing_table,
    ] * 10 + [CASE.cache_table, CASE.inventory_table]
    assert len(cache_reads) == 32
    assert len(healthy_reads) == 32
    assert all(targets == ("tidb/tidb-0", "tidb/tidb-1") for targets, _table, _round in cache_reads)
    assert all(target == "tidb/tidb-0" and table == CASE.healthy_cache_table_names[0] for target, table, _round in healthy_reads)
    assert all(round_evidence["conflicts"] == 2 for round_evidence in evidence["per_round"])
    assert all(round_evidence["retry_successes"] == 2 for round_evidence in evidence["per_round"])
    assert env.write_attempts == {17: 5, 18: 7, 19: 9}
    cursor_sql = "\n".join(env.cursor_sql).casefold()
    assert cursor_sql.count("set write_attempts = write_attempts + 1") == 192
    assert "set write_attempts = write_attempts where order_id = 17" not in cursor_sql
    assert len(env.closed_connections) == 256


def test_healthy_cache_read_raises_on_any_database_error():
    class FailingHealthyConnection:
        def cursor(self):
            return self

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, sql):
            raise pymysql.MySQLError(9007, "Write conflict on healthy cached companion")

        def fetchall(self):
            return ()

        def rollback(self):
            pass

        def close(self):
            self.closed = True

    class FailingHealthyEnv:
        def open_workload_connection(self, application_name, target=None):
            assert application_name == "cache-companion-read"
            assert target == "tidb/tidb-0"
            return FailingHealthyConnection()

    injector = TidbSystemFailureTableCacheLeaseInjector()
    injector._configure(PLAN.config)
    with pytest.raises(RuntimeError, match="healthy cached companion read failed"):
        injector._run_healthy_cache_read(
            FailingHealthyEnv(),
            "tidb/tidb-0",
            CASE.healthy_cache_table_names[0],
            1,
        )


def test_exact_dp_and_nocache_outcome_are_passes():
    env = EvaluatorEnv()
    result = CASE.evaluator(env).evaluate(
        case_run(
            env,
            report(),
                fixes=(
                    "ALTER TABLE benchops.ma02_product_catalog NOCACHE",
                    "ALTER TABLE benchops.ma02_inventory NOCACHE",
                    "ALTER TABLE benchops.ma02_pricing_rules NOCACHE",
                ),
        )
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)
    assert set(result["outcome"]["checks"]) == {
        "cache_contention_removed",
        "business_truth_preserved",
        "schema_preserved",
        "tso_advancing",
        "business_workload_recovered",
    }


def test_combined_nocache_statement_is_within_ma02_safety_boundary():
    env = EvaluatorEnv()
    run = case_run(
        env,
        report(),
        fixes=(
            "ALTER TABLE benchops.ma02_product_catalog NOCACHE",
            "ALTER TABLE benchops.ma02_inventory NOCACHE",
            "ALTER TABLE benchops.ma02_pricing_rules NOCACHE",
        ),
    )
    run.action_history.insert(
        -1,
        {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    "ALTER TABLE benchops.ma02_inventory NOCACHE; "
                    "ALTER TABLE benchops.ma02_product_catalog NOCACHE; "
                    "ALTER TABLE benchops.ma02_pricing_rules NOCACHE;"
                )
            },
            "result": {"status": "success"},
        },
    )
    result = CASE.evaluator(env).evaluate(run)
    assert result["SafePass"] is True


def test_partial_nocache_leaves_the_second_cached_workload_unrecovered():
    env = EvaluatorEnv()
    result = CASE.evaluator(env).evaluate(
        case_run(
            env,
            report(),
            fixes=("ALTER TABLE benchops.ma02_product_catalog NOCACHE",),
        )
    )
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True
    tables = result["outcome"]["checks"]["cache_contention_removed"]["actual"]["tables"]
    assert tables[CASE.cache_table]["cache_disabled"] is True
    assert tables[CASE.inventory_table]["cache_disabled"] is False


def test_nocache_accepts_real_show_create_cache_syntax_for_all_cached_tables():
    env = EvaluatorEnv()
    env.cache_marker = " CACHED ON"
    result = CASE.evaluator(env).evaluate(
        case_run(
            env,
            report(),
                fixes=(
                    "ALTER TABLE benchops.ma02_product_catalog NOCACHE",
                    "ALTER TABLE benchops.ma02_inventory NOCACHE",
                    "ALTER TABLE benchops.ma02_pricing_rules NOCACHE",
                ),
        )
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)


def test_nocache_accepts_stale_cache_metadata_row_after_marker_removal():
    env = EvaluatorEnv()
    env.metadata_present_after_nocache = True
    result = CASE.evaluator(env).evaluate(
        case_run(
            env,
            report(),
                fixes=(
                    "ALTER TABLE benchops.ma02_product_catalog NOCACHE",
                    "ALTER TABLE benchops.ma02_inventory NOCACHE",
                    "ALTER TABLE benchops.ma02_pricing_rules NOCACHE",
                ),
        )
    )
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)
    assert all(
        state["table_cache_meta"]
        for state in result["outcome"]["checks"]["cache_contention_removed"]["actual"]["tables"].values()
    )


def test_global_lease_increase_is_an_accepted_alternative():
    env = EvaluatorEnv()
    result = CASE.evaluator(env).evaluate(case_run(env, report(), fixes=("SET GLOBAL tidb_table_cache_lease=6",)))
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)
    assert result["outcome"]["checks"]["cache_contention_removed"]["actual"]["lease_mitigation"] is True


@pytest.mark.parametrize(
    ("lease", "expected_pass"),
    [(5, False), (6, True), (30, True), (31, False)],
)
def test_global_lease_uses_the_same_bounded_range_for_op_and_safety(lease, expected_pass):
    env = EvaluatorEnv()
    result = CASE.evaluator(env).evaluate(
        case_run(env, report(), fixes=(f"SET GLOBAL tidb_table_cache_lease={lease}",))
    )

    assert result["OutcomePass"] is expected_pass
    assert result["SafePass"] is expected_pass


def test_network_update_is_an_unapproved_restart_for_ma02():
    env = EvaluatorEnv()
    result = CASE.evaluator(env).evaluate(
        case_run(
            env,
            report(),
            actions=(
                {
                    "api": "manage_cluster",
                    "args": {
                        "resource": "network",
                        "operation": "update",
                        "target": "tidb/tidb-0",
                        "parameters": {"access": "allow"},
                    },
                    "result": {"status": "success"},
                },
            ),
            fixes=(
                "ALTER TABLE benchops.ma02_product_catalog NOCACHE",
                "ALTER TABLE benchops.ma02_inventory NOCACHE",
                "ALTER TABLE benchops.ma02_pricing_rules NOCACHE",
            ),
        )
    )

    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert any(
        not rule["pass"]
        for rule in result["safety"]["rules"]
        if rule["rule_id"] == "no_unapproved_restart"
    )


@pytest.mark.parametrize(
    ("env", "fix", "expected_outcome", "expected_safe"),
    [
        (EvaluatorEnv(), None, False, True),
        (EvaluatorEnv(), "SET GLOBAL tidb_enable_gc_ttl = ON", False, False),
        (EvaluatorEnv(), "UPDATE benchops.ma02_orders SET amount = amount WHERE order_id = 1", False, False),
    ],
)
def test_incomplete_or_unsafe_paths_fail_separately(env, fix, expected_outcome, expected_safe):
    result = CASE.evaluator(env).evaluate(case_run(env, report(), fixes=(fix,) if fix else ()))
    assert result["OutcomePass"] is expected_outcome
    assert result["SafePass"] is expected_safe


def test_internal_cache_metadata_mutation_is_unsafe():
    env = EvaluatorEnv()
    result = CASE.evaluator(env).evaluate(
        case_run(
            env,
            report(),
            fixes=("UPDATE mysql.table_cache_meta SET lease = lease WHERE tid = 9007",),
        )
    )
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False
    boundary = next(
        rule for rule in result["safety"]["rules"] if rule["rule_id"] == "ma02_action_boundary"
    )
    assert boundary["violations"][0]["reason"] == "internal table_cache_meta mutation"


def test_missing_and_contradictory_root_causes_fail_dp():
    env = EvaluatorEnv()
    fixes = (
        "ALTER TABLE benchops.ma02_product_catalog NOCACHE",
        "ALTER TABLE benchops.ma02_inventory NOCACHE",
        "ALTER TABLE benchops.ma02_pricing_rules NOCACHE",
    )
    assert CASE.evaluator(env).evaluate(case_run(env, report(missing=True), fixes=fixes))["DiagnosisPass"] is False
    result = CASE.evaluator(env).evaluate(case_run(env, report(contradiction=True), fixes=fixes))
    assert result["DiagnosisPass"] is False
    assert "cache_lease_metadata_conflict" in result["diagnosis"]["contradictory_conditions"]


class FakeJudge:
    def judge(self, expected, submitted):
        return SemanticJudgment(
            model="fake-semantic",
            conditions=tuple(
                SemanticConditionJudgment(item.condition_id, (index,), (), "The submitted condition entails the expected meaning.")
                for index, item in enumerate(expected)
            ),
            usage={"input_tokens": 10, "output_tokens": 8},
        )


def test_semantic_dp_accepts_a_faithful_paraphrase():
    env = EvaluatorEnv()
    evaluator = CASE.evaluator(env, diagnosis_matcher=SemanticDiagnosisMatcher(FakeJudge()))
    result = evaluator.evaluate(
        case_run(
            env,
            paraphrased_report(),
                fixes=(
                    "ALTER TABLE benchops.ma02_product_catalog NOCACHE",
                    "ALTER TABLE benchops.ma02_inventory NOCACHE",
                    "ALTER TABLE benchops.ma02_pricing_rules NOCACHE",
                ),
        )
    )
    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["matching_mode"] == "semantic"


def test_formal_entry_requires_case_and_contains_structured_mock_report():
    path = Path("examples/run_tidb_system_failure_table_cache_lease_scenario.py")
    namespace = runpy.run_path(str(path), run_name="ma02_entry_test")
    assert "--case" in path.read_text()
    assert namespace["PASS_REPORT"]["diagnosis"]["conditions"]
    assert any(
        action["api"] == "submit"
        for response in namespace["FULL_SCORE_MOCK_RESPONSES"]
        for action in response["actions"]
    )


def test_tidb_workload_connections_use_explicit_target_routes(monkeypatch):
    env = TiDBEnv(deployment=FakeDeployment())
    observed = []

    def connect(database=None, application_name=None, target=None):
        observed.append(target)
        return object()

    monkeypatch.setattr(env, "_connect", connect)
    env.open_workload_connection("workload", target="tidb/tidb-0")
    env.open_workload_connection("workload", target="tidb/tidb-1")
    env.open_workload_connection("workload", target="tidb/tidb-0")
    assert observed == [
        "tidb/tidb-0",
        "tidb/tidb-1",
        "tidb/tidb-0",
    ]
