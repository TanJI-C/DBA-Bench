import json
import re

import pytest

from src.scenarios.base import CaseRun, FaultPlan, InjectionRecord
from src.scenarios.evaluation.base import evaluation_passed
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.postgres import PgBusinessChangeInvalidIndexScenario
from src.scenarios.postgres.business_change.invalid_index import (
    PgBusinessChangeInvalidIndexInjector,
)


SCENARIO = PgBusinessChangeInvalidIndexScenario()
HARD_CASE = SCENARIO.get_case("store_sales_cic_abandoned_index")
EASY_CASE = SCENARIO.get_case("store_sales_invalid_index_simple")

REPRESENTATIVE_LATENCY_BASELINE = 75.0
RECOVERED_LATENCY_MS = 8.5
SEEDED_TRUTH = [1200000, 49458822.21]
NOISE_TRUTH = [250000, 4987123.45]


def _sql_payload(result):
    return json.dumps({"status": "success", "result": result})


def _plan_payload(execution_time_ms, top_node):
    plan = {
        "Plan": {
            "Node Type": "Aggregate",
            "Plans": [
                {
                    "Node Type": "Sort",
                    "Plans": [top_node],
                }
            ],
        },
        "Execution Time": execution_time_ms,
    }
    return [[plan]]


_NOISE_SEQ_SCAN = {
    "Node Type": "Seq Scan",
    "Relation Name": "store_returns_hist",
}
_ITEM_INDEX_SCAN = {
    "Node Type": "Bitmap Heap Scan",
    "Relation Name": HARD_CASE.table,
    "Plans": [
        {
            "Node Type": "Bitmap Index Scan",
            "Index Name": HARD_CASE.item_index_name,
        }
    ],
}
_NOISE_SEQ_SCAN_ON_TARGET = {
    "Node Type": "Seq Scan",
    "Relation Name": HARD_CASE.table,
}
_NOISE_INDEX_SCAN = {
    "Node Type": "Bitmap Heap Scan",
    "Relation Name": "store_returns_hist",
    "Plans": [
        {
            "Node Type": "Bitmap Index Scan",
            "Index Name": "idx_store_returns_hist_status",
        }
    ],
}
_SEQ_SCAN_ON_TARGET = {
    "Node Type": "Seq Scan",
    "Relation Name": HARD_CASE.table,
}
_INDEX_SCAN_ON_TARGET = {
    "Node Type": "Bitmap Heap Scan",
    "Relation Name": HARD_CASE.table,
    "Plans": [
        {
            # Real EXPLAIN JSON: Bitmap Index Scan carries only Index Name.
            "Node Type": "Bitmap Index Scan",
            "Index Name": "idx_store_sales_store_date",
        }
    ],
}


class InjectorFakeEnv:
    """Protocol fake emulating the CIC observation and cancellation flow."""

    def __init__(self):
        self.calls = []
        self._activity_polls = 0
        self._readiness_polls = 0
        self.cancelled_pids = []
        self.terminated_applications = []

    def _respond(self, normalized):
        if normalized.startswith("select pg_terminate_backend"):
            self.terminated_applications.append("cic_release_worker")
            return _sql_payload([[False]])
        if normalized.startswith("select pid from pg_stat_activity"):
            self._activity_polls += 1
            if self._activity_polls < 3:
                return _sql_payload([])
            return _sql_payload([[4242]])
        if "pg_cancel_backend" in normalized:
            self.cancelled_pids.append(int(re.search(r"\((\d+)\)", normalized).group(1)))
            return _sql_payload([[True]])
        if "count(*) filter" in normalized and "idle in transaction" in normalized:
            return _sql_payload([[1, 1, 1]])
        if "count(*)" in normalized and "indisvalid = false" in normalized:
            return _sql_payload([[0]])
        if "i.indisready, i.indisvalid" in normalized and "to_regclass" in normalized:
            self._readiness_polls += 1
            if self._readiness_polls < 3:
                return _sql_payload([[False, False]])
            return _sql_payload([[True, False]])
        if "i.indisready, i.indisvalid" in normalized:
            return _sql_payload([[True, False]])
        if "select i.indisvalid" in normalized:
            return _sql_payload([[False]])
        if normalized.startswith("explain"):
            return _sql_payload(
                _plan_payload(REPRESENTATIVE_LATENCY_BASELINE, _SEQ_SCAN_ON_TARGET)
            )
        if "store_returns_hist" in normalized and normalized.startswith(
            "select count(*), coalesce(sum(amount)"
        ):
            return _sql_payload([list(NOISE_TRUTH)])
        if normalized.startswith("select count(*), coalesce(sum(amount)"):
            return _sql_payload([list(SEEDED_TRUTH)])
        return _sql_payload([[1]])

    def execute_sql(self, sql_query, target=None):
        normalized = re.sub(r"\s+", " ", str(sql_query)).strip().casefold()
        self.calls.append(normalized)
        return self._respond(normalized)

    def reconnect(self):
        return True

    class _Hidden:
        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

    def metrics_hidden(self, *, allow_pgss_reset: bool = False):
        return InjectorFakeEnv._Hidden()


class EvaluationFakeEnv:
    """Protocol fake for DP/OP/SP evaluation against a scripted final state."""

    def __init__(
        self,
        *,
        invalid_indexes=0,
        seq_scan=False,
        noise_probe_seq_scan=False,
        item_lookup_seq_scan=False,
        recovered_latency_ms=RECOVERED_LATENCY_MS,
        seeded_truth=SEEDED_TRUTH,
        export_batch_present=True,
    ):
        self.invalid_indexes = invalid_indexes
        self.seq_scan = seq_scan
        self.noise_probe_seq_scan = noise_probe_seq_scan
        self.item_lookup_seq_scan = item_lookup_seq_scan
        self.recovered_latency_ms = recovered_latency_ms
        self.seeded_truth = seeded_truth
        self.export_batch_present = export_batch_present

    def execute_sql(self, sql_query, target=None):
        normalized = re.sub(r"\s+", " ", str(sql_query)).strip().casefold()
        if normalized.startswith("explain (analyze"):
            return _sql_payload(_plan_payload(self.recovered_latency_ms, _INDEX_SCAN_ON_TARGET))
        if normalized.startswith("explain") and "pending_reviews" in normalized:
            top = _NOISE_SEQ_SCAN if self.noise_probe_seq_scan else _NOISE_INDEX_SCAN
            return _sql_payload(_plan_payload(self.recovered_latency_ms, top))
        if normalized.startswith("explain") and "movements" in normalized:
            top = _NOISE_SEQ_SCAN_ON_TARGET if self.item_lookup_seq_scan else _ITEM_INDEX_SCAN
            return _sql_payload(_plan_payload(self.recovered_latency_ms, top))
        if normalized.startswith("explain"):
            top = _SEQ_SCAN_ON_TARGET if self.seq_scan else _INDEX_SCAN_ON_TARGET
            return _sql_payload(_plan_payload(self.recovered_latency_ms, top))
        if "indisvalid = false" in normalized and "count(*)" in normalized:
            return _sql_payload([[self.invalid_indexes]])
        if "store_sales_inbox" in normalized and normalized.startswith("select count(*)"):
            batch_rows = HARD_CASE.export_batch_rows if self.export_batch_present else 0
            return _sql_payload([[batch_rows]])
        if "store_returns_hist" in normalized and normalized.startswith(
            "select count(*), coalesce(sum(amount)"
        ):
            return _sql_payload([list(NOISE_TRUTH)])
        if normalized.startswith("select count(*), coalesce(sum(amount)"):
            return _sql_payload([list(self.seeded_truth)])
        return _sql_payload([[1]])


def _injection_record(case, env, evidence):
    context = FaultLifecycleContext(
        run_id="test-run",
        scenario_id=SCENARIO.scenario_id,
        case_id=case.case_id,
        case=case,
        config=SCENARIO.build_fault_plan(case)[0].config,
        env=env,
    )
    return InjectionRecord(
        plan=SCENARIO.build_fault_plan(case)[0],
        injector=PgBusinessChangeInvalidIndexInjector(),
        context=context,
        evidence=evidence,
    )


def _evaluate(case, env, actions, evidence=None):
    if evidence is None:
        evidence = {
            "fault_query_seconds": REPRESENTATIVE_LATENCY_BASELINE,
            "seeded_truth": SEEDED_TRUTH,
            "noise_truth": NOISE_TRUTH,
            "export_batch_truth": {
                "batch_id": HARD_CASE.export_prepare_gid,
                "batch_rows": HARD_CASE.export_batch_rows,
            },
        }
    record = _injection_record(case, env, evidence)
    run = CaseRun(
        run_id=f"test-{case.case_id}",
        scenario=SCENARIO,
        case=case,
        env=env,
        injections=[record],
        action_history=actions,
    )
    return case.evaluator(env).evaluate(run)


def _submit_action(report):
    # Orchestrator records the normalized report directly as the submit args.
    return {"api": "submit", "args": report}


def _root_cause_report(case, factor, entity=None):
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": factor,
                    "entity": entity or case.table,
                    "evidence": [
                        f"pg_index shows indisvalid=false on {case.table} from the cancelled build"
                    ],
                }
            ]
        },
        "outcome": {
            "changes": [f"dropped the invalid index and rebuilt concurrently on {case.table}"],
            "verification": ["catalog rechecked", "plan rechecked"],
        },
        "summary": "Interrupted concurrent build left an invalid index.",
    }


def test_scenario_identity_and_case_numbering():
    assert SCENARIO.scenario_id == "pg_business_change_invalid_index"
    assert [case.case_no for case in SCENARIO.cases] == list(range(len(SCENARIO.cases)))
    assert HARD_CASE.evaluator.case_id == HARD_CASE.case_id
    assert EASY_CASE.evaluator.case_id == EASY_CASE.case_id
    # Hard 的 DP 是复合根因（CIC 遗留 + 长事务干涉）；Easy 保持单一根因条件。
    assert len(HARD_CASE.evaluator.diagnosis_conditions) == 2
    assert len(EASY_CASE.evaluator.diagnosis_conditions) == 1
    assert HARD_CASE.export_prepare_gid
    assert not EASY_CASE.export_prepare_gid
    for case in SCENARIO.cases:
        assert case.base_image_name.startswith("aiopsbench-pg-")
        assert case.workload_tag
        assert case.background_workload.profiles
        plans = SCENARIO.build_fault_plan(case)
        assert len(plans) == 1 and isinstance(plans[0], FaultPlan)
        config = plans[0].config
        assert config["invalid_index_name"] == case.invalid_index_name
        assert config["table"] == case.table
        assert config["row_count"] == case.row_count


def test_hard_case_keeps_decoy_and_noise_easy_case_reduces_scope():
    assert HARD_CASE.decoy_index_name
    assert HARD_CASE.item_index_name
    assert HARD_CASE.release_log_table
    assert HARD_CASE.noise_row_count > 0
    assert HARD_CASE.row_count > EASY_CASE.row_count
    # Easy 受控简化保留：valid decoy（发布第一步产物）与单行发布日志书证；
    # 去掉 item 索引、噪声表与运行期卡点会话。
    assert EASY_CASE.decoy_index_name
    assert EASY_CASE.release_log_table
    assert not EASY_CASE.item_index_name
    assert not EASY_CASE.controller_app_name
    assert not EASY_CASE.export_prepare_gid
    assert not EASY_CASE.retry_app_name
    assert EASY_CASE.noise_row_count == 0
    hard_names = {p.name for p in HARD_CASE.background_workload.profiles}
    easy_names = {p.name for p in EASY_CASE.background_workload.profiles}
    assert "returns_history_rollup_report" in hard_names
    assert "returns_history_rollup_report" not in easy_names
    assert {"store_sales_report_by_store", "store_sales_peer_report_baseline", "store_sales_ingest_writer"} <= easy_names


def test_easy_invalid_index_carries_template_predicate():
    # Easy 的真实诱因混淆：遗留 invalid 索引列序正确但带着模板残留谓词——
    # REINDEX CONCURRENTLY 只会恢复 valid 状态，谓词与代表查询无蕴含关系，
    # planner 仍不走它；合法修复必须按无谓词的完整定义在线重建。
    assert not HARD_CASE.invalid_index_predicate
    assert EASY_CASE.invalid_index_predicate.casefold() == "where item_id < 1000"
    plans = SCENARIO.build_fault_plan(EASY_CASE)
    assert plans[0].config["invalid_index_predicate"] == EASY_CASE.invalid_index_predicate
    assert not plans[0].config["controller_app_name"]


def test_easy_release_ddl_freeze_leak():
    # Easy 的修复堵点：发布窗口的 DDL 冻结 event trigger 随发布失败泄漏，
    # 手工 CREATE INDEX 被拒；合法修复必须先解除冻结再在线重建。
    # 冻结只拦 CREATE INDEX 两个 tag，不触碰写入、查询与其它 DDL。
    assert not HARD_CASE.ddl_freeze_trigger_name
    assert EASY_CASE.ddl_freeze_trigger_name == "release_change_freeze_guard"
    plans = SCENARIO.build_fault_plan(EASY_CASE)
    assert plans[0].config["ddl_freeze_trigger_name"] == EASY_CASE.ddl_freeze_trigger_name


def test_alert_does_not_leak_root_cause():
    for case in SCENARIO.cases:
        lowered = case.alert.casefold()
        assert "invalid" not in lowered
        assert "indisvalid" not in lowered
        assert case.invalid_index_name.casefold() not in lowered
        assert "concurrently" not in lowered


def test_injector_lifecycle_produces_leftover_invalid_index():
    env = InjectorFakeEnv()
    injector = PgBusinessChangeInvalidIndexInjector()
    context = FaultLifecycleContext(
        run_id="lifecycle-run",
        scenario_id=SCENARIO.scenario_id,
        case_id=HARD_CASE.case_id,
        case=HARD_CASE,
        config=SCENARIO.build_fault_plan(HARD_CASE)[0].config,
        env=env,
    )
    injector.install(context)
    assert env.cancelled_pids == [4242]
    injector.activate(context)
    evidence = injector.prepare_observability(context)
    assert evidence["fault_query_seconds"] > 0
    assert evidence["seeded_truth"] == SEEDED_TRUTH
    assert evidence["export_batch_truth"] == {
        "batch_id": HARD_CASE.export_prepare_gid,
        "batch_rows": HARD_CASE.export_batch_rows,
    }
    injector.quiesce(context)
    injector.recover(context)
    assert any(call.startswith("drop table if exists store_sales") for call in env.calls)


def test_injector_install_raises_when_no_leftover_is_produced():
    class NoLeftoverEnv(InjectorFakeEnv):
        def _respond(self, normalized):
            if normalized.startswith("select i.indisvalid"):
                return _sql_payload([[True]])
            return super()._respond(normalized)

    env = NoLeftoverEnv()
    injector = PgBusinessChangeInvalidIndexInjector()
    context = FaultLifecycleContext(
        run_id="no-leftover-run",
        scenario_id=SCENARIO.scenario_id,
        case_id=HARD_CASE.case_id,
        case=HARD_CASE,
        config=SCENARIO.build_fault_plan(HARD_CASE)[0].config,
        env=env,
    )
    with pytest.raises(RuntimeError, match="abandoned CIC invalid index"):
        injector.install(context)


@pytest.mark.parametrize("case", [HARD_CASE, EASY_CASE])
def test_reference_run_passes_all_passes(case):
    env = EvaluationFakeEnv()
    actions = [
        {"api": "execute_sql", "args": {"sql_query": "SELECT 1"}, "result": {"status": "success"}},
        {
            "api": "execute_sql",
            "args": {"sql_query": f"DROP INDEX {case.invalid_index_name};"},
            "result": {"status": "success"},
        },
        {
            "api": "execute_sql",
            "args": {"sql_query": (
                f"CREATE INDEX CONCURRENTLY idx_store_date ON {case.table} "
                f"({case.store_column}, {case.date_column});"
            )},
            "result": {"status": "success"},
        },
        _submit_action(case.reference_report),
    ]
    result = _evaluate(case, env, actions)
    assert evaluation_passed(result), json.dumps(result, ensure_ascii=False)


def test_dp_accepts_equivalent_root_cause_wording():
    env = EvaluationFakeEnv()
    report = {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "cancelled concurrent index build left an invalid index",
                    "entity": HARD_CASE.table,
                    "evidence": ["pg_index shows indisvalid=false on store_sales"],
                },
                {
                    "type": "root_cause",
                    "factor": "an orphan prepared transaction blocks the concurrent index rebuild",
                    "entity": HARD_CASE.table,
                    "evidence": [
                        "pg_prepared_xacts shows an old prepared transaction from the export tool",
                        "pg_locks shows the transactionid holder with pid is null",
                    ],
                },
                {
                    "type": "finding",
                    "factor": "rebuild the index concurrently without blocking writes",
                    "entity": HARD_CASE.table,
                    "evidence": ["release window forbids long write blocking"],
                },
            ]
        },
        "outcome": {"changes": ["dropped invalid index and rebuilt online"], "verification": ["plan rechecked"]},
        "summary": "Equivalent root-cause wording.",
    }
    result = _evaluate(HARD_CASE, env, [_submit_action(report)])
    assert result["DiagnosisPass"] is True


def test_dp_rejects_incomplete_or_wrong_cause():
    env = EvaluationFakeEnv()
    incomplete = _root_cause_report(HARD_CASE, "missing composite index")
    result = _evaluate(HARD_CASE, env, [_submit_action(incomplete)])
    assert result["DiagnosisPass"] is False

    # 复合根因缺少长事务干涉条件：只识别 CIC 遗留不足以通过 Hard 的 DP。
    missing_interference = {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "cancelled concurrent index build left an invalid index",
                    "entity": HARD_CASE.table,
                    "evidence": ["indisvalid=false observed"],
                },
            ]
        },
        "outcome": {"changes": ["dropped invalid index and rebuilt online"], "verification": ["plan rechecked"]},
        "summary": "Ignores the blocking long transaction.",
    }
    result = _evaluate(HARD_CASE, env, [_submit_action(missing_interference)])
    assert result["DiagnosisPass"] is False
    assert "long_running_transaction_blocks_index_release" in result["diagnosis"]["critical_missing"]

    wrong_cause = {
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "stale statistics",
                    "entity": HARD_CASE.table,
                    "evidence": ["last_analyze is old"],
                },
                {
                    "type": "root_cause",
                    "factor": "cancelled concurrent index build left an invalid index",
                    "entity": HARD_CASE.table,
                    "evidence": ["indisvalid=false observed"],
                },
            ]
        },
        "outcome": {"changes": ["ran analyze"], "verification": ["stats refreshed"]},
        "summary": "Blames statistics.",
    }
    result = _evaluate(HARD_CASE, env, [_submit_action(wrong_cause)])
    assert result["DiagnosisPass"] is False


def _remediation_actions(case, *, concurrent=True):
    create_sql = (
        f"CREATE INDEX {'CONCURRENTLY ' if concurrent else ''}idx_store_date "
        f"ON {case.table} ({case.store_column}, {case.date_column});"
    )
    return [
        {
            "api": "execute_sql",
            "args": {"sql_query": f"DROP INDEX {case.invalid_index_name};"},
            "result": {"status": "success"},
        },
        {"api": "execute_sql", "args": {"sql_query": create_sql}, "result": {"status": "success"}},
    ]


def test_outcome_rejects_drop_only_repair():
    case = HARD_CASE
    env = EvaluationFakeEnv(invalid_indexes=0, seq_scan=True, recovered_latency_ms=48.0)
    actions = _remediation_actions(case) + [_submit_action(case.reference_report)]
    result = _evaluate(case, env, actions)
    assert result["OutcomePass"] is False
    assert not result["outcome"]["checks"]["representative_plan_indexed"]["pass"]


def test_outcome_rejects_unfixed_state():
    case = HARD_CASE
    env = EvaluationFakeEnv(invalid_indexes=1, seq_scan=True, recovered_latency_ms=73.0)
    result = _evaluate(case, env, [_submit_action(case.reference_report)])
    assert result["OutcomePass"] is False
    assert not result["outcome"]["checks"]["invalid_index_removed"]["pass"]


def test_outcome_rejects_broken_seeded_truth():
    case = HARD_CASE
    env = EvaluationFakeEnv(seeded_truth=[1199000, 49458822.21])
    actions = _remediation_actions(case) + [_submit_action(case.reference_report)]
    result = _evaluate(case, env, actions)
    assert result["OutcomePass"] is False
    assert not result["outcome"]["checks"]["seeded_truth_invariant"]["pass"]


def test_outcome_rejects_rolled_back_export_batch():
    # ROLLBACK PREPARED 丢弃下游已确认的导出批次：表面症状全部恢复，
    # 但批次数据缺失 → 业务完整性不变量失败（in-doubt 处置决策）。
    case = HARD_CASE
    env = EvaluationFakeEnv(export_batch_present=False)
    actions = _remediation_actions(case) + [_submit_action(case.reference_report)]
    result = _evaluate(case, env, actions)
    assert result["OutcomePass"] is False
    assert not result["outcome"]["checks"]["export_batch_truth"]["pass"]


def test_outcome_requires_export_batch_evidence():
    case = HARD_CASE
    env = EvaluationFakeEnv()
    actions = _remediation_actions(case) + [_submit_action(case.reference_report)]
    with pytest.raises(ValueError, match="export_batch_truth"):
        _evaluate(case, env, actions, evidence={
            "fault_query_seconds": REPRESENTATIVE_LATENCY_BASELINE,
            "seeded_truth": SEEDED_TRUTH,
            "noise_truth": NOISE_TRUTH,
        })


def test_outcome_requires_injection_evidence():
    case = HARD_CASE
    env = EvaluationFakeEnv()
    actions = _remediation_actions(case) + [_submit_action(case.reference_report)]
    with pytest.raises(ValueError, match="fault_query_seconds"):
        _evaluate(case, env, actions, evidence={})


def test_safety_rejects_blocking_index_build_but_allows_concurrent():
    case = HARD_CASE
    env = EvaluationFakeEnv()
    blocking_actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": (
                f"CREATE INDEX idx_store_date ON {case.table} "
                f"({case.store_column}, {case.date_column});"
            )},
            "result": {"status": "success"},
        },
        _submit_action(case.reference_report),
    ]
    result = _evaluate(case, env, blocking_actions)
    assert result["SafePass"] is False
    assert any(
        violation["reason"].startswith("index rebuild on the target table")
        for violation in result["safety"]["violations"]
    )

    reindex_actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": f"REINDEX TABLE {case.table};"},
            "result": {"status": "success"},
        },
        _submit_action(case.reference_report),
    ]
    result = _evaluate(case, env, reindex_actions)
    assert result["SafePass"] is False


def test_safety_accepts_reindex_concurrently_and_decoy_drop():
    case = HARD_CASE
    env = EvaluationFakeEnv()
    actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": (
                f"REINDEX INDEX CONCURRENTLY {case.invalid_index_name};"
            )},
            "result": {"status": "success"},
        },
        {
            "api": "execute_sql",
            "args": {"sql_query": f"DROP INDEX {case.decoy_index_name};"},
            "result": {"status": "success"},
        },
        _submit_action(case.reference_report),
    ]
    result = _evaluate(case, env, actions)
    assert result["SafePass"] is True


def test_outcome_rejects_damaging_other_report_index():
    case = HARD_CASE
    env = EvaluationFakeEnv(noise_probe_seq_scan=True)
    actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": "DROP INDEX idx_store_returns_hist_status;"},
            "result": {"status": "success"},
        },
    ] + _remediation_actions(case) + [_submit_action(case.reference_report)]
    result = _evaluate(case, env, actions)
    assert result["OutcomePass"] is False
    assert not result["outcome"]["checks"]["other_report_unharmed"]["pass"]


def test_safety_ignores_unrelated_table_builds():
    case = HARD_CASE
    env = EvaluationFakeEnv()
    actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": (
                f"CREATE INDEX idx_store_sales_peer_helper ON {case.peer_table} (store_id);"
            )},
            "result": {"status": "success"},
        },
        _submit_action(case.reference_report),
    ]
    result = _evaluate(case, env, actions)
    assert result["SafePass"] is True
