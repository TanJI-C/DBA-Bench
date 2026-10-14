from collections.abc import Mapping

import time

from src.database.query_results import nearest_rank_percentile

from src.database.query_results import capture_query_result_truth

from src.database.sql import parse_json_object, require_success_payload

from src.scenarios.tidb.common import BaseFaultInjector, FaultLifecycleContext, validate_sql_identifier

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.query_perf.case_when_in_cartesian_semi_join import (
    TidbQueryPerfCaseWhenInCartesianSemiJoinEvaluatorCase,
    TidbQueryPerfCaseWhenInCartesianSemiJoinSimpleEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import BackgroundWorkloadSpec, BackgroundWorkloadStartPhase
from src.scenarios.base import DifficultyCalibration, FaultPlan, TiDBScenario, TiDBScenarioCase
from src.execution.tidb_runtime import TIDB_V8_1_0, tidb_runtime


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfCaseWhenInCartesianSemiJoinCase(TiDBScenarioCase):
    db: str
    outer_table: str
    rule_table: str
    gate_table: str
    region_table: str
    view: str
    business_query: str
    performance_query: str
    outer_rows: int
    rule_rows: int
    gate_rows: int
    region_rows: int
    candidate_matches: int
    region_expected_matches: int
    expected_region_null_rows: int
    expected_matches: int
    expected_null_outer_rows: int
    expected_null_result_rows: int
    expected_zero_result_rows: int
    performance_ratio: float


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbQueryPerfCaseWhenInCartesianSemiJoinForOrderRiskReportScenarioCase(
    TidbQueryPerfCaseWhenInCartesianSemiJoinCase
):
    pass


_BUSINESS_QUERY = (
    "SELECT id, matched "
    "FROM benchops.qp06_case_result ORDER BY id"
)

_PERFORMANCE_QUERY = (
    "SELECT SUM(matched) AS matched_rows, COUNT(*) AS probe_rows "
    "FROM benchops.qp06_case_result"
)


_CASE = TidbQueryPerfCaseWhenInCartesianSemiJoinForOrderRiskReportScenarioCase(
    case_id="case_when_in_cartesian_semi_join",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "The affected order-risk report uses four scalar CASE WHEN value IN subquery expressions, including a scope_c and scope_d region IN expression tested with IS NULL, and each subquery applies a scope-dependent LIKE correlation over nullable keys, so TiDB must preserve four membership expressions plus the different three-valued NULL semantics of scope_c versus scope_d",
                    "entity": "case_when_in_cartesian_semi_join",
                    "evidence": [
                        "scripted diagnostic actions observed The affected order-risk report uses four scalar CASE WHEN value IN subquery expressions, including a scope_c and scope_d region IN expression tested with IS NULL, and each subquery applies a scope-dependent LIKE correlation over nullable keys, so TiDB must preserve four membership expressions plus the different three-valued NULL semantics of scope_c versus scope_d"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "The nullable scalar IN expressions are planned as four Cartesian left outer semi joins with non-equality other-conditions, multiplying the 10001-row report probe through 3001-row, 1801-row, and 2301-row gates and re-evaluating the region membership for the scope_c/scope_d NULL branch",
                    "entity": "case_when_in_cartesian_semi_join",
                    "evidence": [
                        "scripted diagnostic actions observed The nullable scalar IN expressions are planned as four Cartesian left outer semi joins with non-equality other-conditions, multiplying the 10001-row report probe through 3001-row, 1801-row, and 2301-row gates and re-evaluating the region membership for the scope_c/scope_d NULL branch"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "The root cause is confined to the order-risk CASE/IN report endpoint; cluster health, the point-lookup workloads, and ordinary reads of both gate tables are not the cause of the latency regression",
                    "entity": "case_when_in_cartesian_semi_join",
                    "evidence": [
                        "scripted diagnostic actions observed The root cause is confined to the order-risk CASE/IN report endpoint; cluster health, the point-lookup workloads, and ordinary reads of both gate tables are not the cause of the latency regression"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "applied the case-specific remediation"
            ],
            "verification": [
                "verified the case-specific final state"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbQueryPerfCaseWhenInCartesianSemiJoinEvaluatorCase,
    title="Four nullable scalar IN expressions expand into Cartesian semi joins over non-unique memberships.",
    alert=(
        "[CRITICAL] [TiDB/Order-Risk-Report] 风险规则报表的 P95 从 20ms 上升到数秒，"
        "同一报表指纹的处理量和 TiDB root CPU 同步增加；集群成员、存储副本和其它点查没有明显异常。"
        "请定位这个报表查询的执行退化原因，在保持命中结果、scope_c/scope_d 差异化 NULL 语义不变的前提下恢复性能。"
    ),
    initial_state={
        "status": "degraded",
        "report": "order-risk-rule-report",
        "endpoint": "benchops.qp06_case_result",
    },
    expected_target={
        "status": "recovered",
        "result_consistent": True,
        "null_semantics_preserved": True,
        "cartesian_join_removed": True,
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="qp06_order_risk_report",
                sql=_PERFORMANCE_QUERY,
                qps=0.08,
                tier="OLAP_BURST",
                application_name="qp06-order-risk-report",
            ),
            WorkloadProfile(
                name="qp06_rule_point_lookup",
                sql=(
                    "SELECT rule_key FROM benchops.qp06_product_risk_rule "
                    "WHERE rule_key IN (17, 29, 311)"
                ),
                qps=1.2,
                tier="OLTP_CORE",
                application_name="qp06-rule-point-lookup",
            ),
            WorkloadProfile(
                name="qp06_gate_point_lookup",
                sql=(
                "SELECT gate_key FROM benchops.qp06_shipping_risk_gate "
                    "WHERE gate_key IN (17, 29, 311)"
                ),
                qps=1.0,
                tier="OLTP_CORE",
                application_name="qp06-gate-point-lookup",
            ),
            WorkloadProfile(
                name="qp06_region_point_lookup",
                sql=(
                    "SELECT region_key FROM benchops.qp06_region_risk_gate "
                    "WHERE region_key IN (17, 29, 311)"
                ),
                qps=0.9,
                tier="OLTP_CORE",
                application_name="qp06-region-point-lookup",
            ),
            WorkloadProfile(
                name="qp06_case_point_probe",
                sql=(
                    "SELECT id, lookup_key FROM benchops.qp06_case_outer "
                    "WHERE risk_scope='scope_b' AND id IN (5001, 7001, 9001, 9999)"
                ),
                qps=1.0,
                tier="OLTP_CORE",
                application_name="qp06-case-point-probe",
            ),
            WorkloadProfile(
                name="qp06_schema_inventory",
                sql=(
                    "SELECT TABLE_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES "
                    "WHERE TABLE_SCHEMA='benchops' ORDER BY TABLE_NAME"
                ),
                qps=0.35,
                tier="DDL_MAINTENANCE_OBSERVABILITY",
                application_name="qp06-schema-inventory",
            ),
            WorkloadProfile(
                name="qp06_equivalent_join_decoy",
                sql=(
                    "SELECT COUNT(*) FROM benchops.qp06_case_outer AS o "
                    "JOIN (SELECT DISTINCT rule_key FROM benchops.qp06_product_risk_rule "
                    "WHERE rule_key IS NOT NULL) AS r ON r.rule_key=o.lookup_key"
                ),
                qps=0.12,
                tier="OLAP_BURST",
                application_name="qp06-equivalent-join-decoy",
            ),
        ),
        worker_count=3,
        seed=20260731,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=5,
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        sql_timeout_seconds=300,
        image_group_key="qp06-case-in-cartesian-semi-join",
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.865672,
        reference_run_ids=(
            "reference-109__tidb_query_perf_case_when_in_cartesian_semi_join__case_when_in_cartesian_semi_join__mock__r001",
        ),
    ),
    db="benchops",
    outer_table="qp06_case_outer",
    rule_table="qp06_product_risk_rule",
    gate_table="qp06_shipping_risk_gate",
    region_table="qp06_region_risk_gate",
    view="qp06_case_result",
    business_query=_BUSINESS_QUERY,
    performance_query=_PERFORMANCE_QUERY,
    outer_rows=10001,
    rule_rows=3001,
    gate_rows=1801,
    region_rows=2301,
    candidate_matches=1500,
    region_expected_matches=1200,
    expected_region_null_rows=2,
    expected_matches=1200,
    expected_null_outer_rows=1,
    expected_null_result_rows=4301,
    expected_zero_result_rows=4500,
    performance_ratio=0.35,
)

_QP06_REDUCED_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(
        WorkloadProfile(
            name="qp06_order_risk_report",
            sql=_PERFORMANCE_QUERY,
            qps=0.08,
            tier="OLAP_BURST",
            application_name="qp06-order-risk-report",
        ),
        WorkloadProfile(
            name="qp06_rule_point_lookup",
            sql=(
                "SELECT rule_key FROM benchops.qp06_product_risk_rule "
                "WHERE rule_key IN (17, 29, 311)"
            ),
            qps=1.2,
            tier="OLTP_CORE",
            application_name="qp06-rule-point-lookup",
        ),
        WorkloadProfile(
            name="qp06_gate_point_lookup",
            sql=(
                "SELECT gate_key FROM benchops.qp06_shipping_risk_gate "
                "WHERE gate_key IN (17, 29, 311)"
            ),
            qps=1.0,
            tier="OLTP_CORE",
            application_name="qp06-gate-point-lookup",
        ),
        WorkloadProfile(
            name="qp06_region_point_lookup",
            sql=(
                "SELECT region_key FROM benchops.qp06_region_risk_gate "
                "WHERE region_key IN (17, 29, 311)"
            ),
            qps=0.9,
            tier="OLTP_CORE",
            application_name="qp06-region-point-lookup",
        ),
    ),
    worker_count=2,
    seed=20260731,
    start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    warmup_seconds=5,
)

_CASE_REDUCED = replace(
    _CASE,
    case_id="case_when_in_cartesian_semi_join_simple",
    case_no=1,
    evaluator=TidbQueryPerfCaseWhenInCartesianSemiJoinSimpleEvaluatorCase,
    runtime=replace(_CASE.runtime, sql_timeout_seconds=300),
    title="Four nullable scalar IN expressions expand into Cartesian semi joins over non-unique memberships.",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": (
                        "The affected order-risk report uses four scalar CASE WHEN value IN subquery expressions, "
                        "including a scope_c and scope_d region IN expression tested with IS NULL, and each subquery "
                        "applies a scope-dependent LIKE correlation over nullable keys, so TiDB must preserve four "
                        "membership expressions plus the different three-valued NULL semantics of scope_c versus scope_d"
                    ),
                    "entity": "case_when_in_cartesian_semi_join_simple",
                    "evidence": [
                        (
                            "The nullable scalar IN expressions are planned as four Cartesian left outer semi joins "
                            "with non-equality other-conditions, multiplying the 10001-row report probe through "
                            "3001-row, 1801-row, and 2301-row gates and re-evaluating the region membership for the "
                            "scope_c/scope_d NULL branch"
                        ),
                        (
                            "one evidence round read the view definition and the EXPLAIN plan: the degenerate view "
                            "correlates the rule, gate, and region membership subqueries by scope-dependent LIKE "
                            "and the plan expands them into four Cartesian left outer semi joins"
                        ),
                    ],
                },
                {
                    "type": "necessary_exclusion",
                    "factor": (
                        "The root cause is confined to the order-risk CASE/IN report endpoint; cluster health, "
                        "the point-lookup workloads, and ordinary reads of both gate tables are not the cause "
                        "of the latency regression"
                    ),
                    "entity": "case_when_in_cartesian_semi_join_simple",
                    "evidence": [
                        (
                            "only the report fingerprint regresses while the point-lookup probes and ordinary "
                            "gate-table reads keep their latency, so the rewrite must stay scoped to the report "
                            "endpoint view"
                        ),
                    ],
                },
            ]
        },
        "outcome": {
            "changes": [
                "rewrote the endpoint view with equality-based scope joins and deduplicated memberships, preserving the scope_c/scope_d NULL branch"
            ],
            "verification": [
                "rechecked the final plan, business truth, NULL semantics, and report latency after the scoped rewrite"
            ],
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification.",
    },
    alert=(
        "[CRITICAL] [TiDB/Order-Risk-Report] 风险规则报表的 P95 从 20ms 上升到数秒，"
        "同一报表指纹的处理量和 TiDB root CPU 同步增加；集群成员、存储副本和其它点查没有明显异常。"
        "请从报表指纹、view 定义和执行计划中定位这个报表查询的执行退化原因，"
        "在保持命中结果、scope_c/scope_d 差异化 NULL 语义和风险规则数据不变的前提下恢复性能，"
        "并把修复范围限定在报表端点本身。"
    ),
    background_workload=_QP06_REDUCED_BACKGROUND_WORKLOAD,
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.279863,
        reference_run_ids=(
            "tidb-cs-close-a-20260908__tidb_query_perf_case_when_in_cartesian_semi_join__"
            "case_when_in_cartesian_semi_join_simplified__mock__r001",
        ),
    ),
)


class TidbQueryPerfCaseWhenInCartesianSemiJoinInjector(BaseFaultInjector):
    """Create the dual nullable CASE/IN view and preserve rewrite evidence."""
    INSERT_BATCH_SIZE = 1000
    DUPLICATE_MEMBERSHIP_ROWS = 100
    # MySQL client connection-class errors (pymysql code, TiDB server code) that
    # a loaded TiDB node returns while the evidence reads below are in flight.
    TRANSIENT_CONNECTION_ERROR_TOKENS = ("(2003,", "(2006,", "(2013,", "(2055,", "(9001,")
    TRANSIENT_CAPTURE_ATTEMPTS = 3
    TRANSIENT_CAPTURE_RETRY_WAIT_SECONDS = 10

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_fixture(context.env)
        self._verify_fault_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        self._verify_fault_state(context.env)
        version = self._capture_payload(context.env, "SELECT VERSION()", "capture QP06 TiDB version")
        view_definition = self._capture_payload(
            context.env,
            f"SHOW CREATE VIEW {self.db}.{self.view}",
            "capture QP06 faulty view definition",
        )
        fault_plan = self._capture_payload(
            context.env,
            f"EXPLAIN {self.business_query}",
            "capture QP06 Cartesian plan",
        )
        fault_result = self._capture_payload(
            context.env,
            self.business_query,
            "capture QP06 business result truth",
        )
        fault_performance = self._measure(context.env)
        topsql = parse_json_object(
            context.env.observe_metric("topsql", None),
            "capture QP06 TopSQL evidence",
        )
        query_latency = parse_json_object(
            context.env.query_metrics("query_latency", None),
            "capture QP06 query-latency evidence",
        )
        self._assert_fault_plan(fault_plan)
        return {
            "tidb_version": version,
            "fault_view_definition": view_definition,
            "fault_plan": fault_plan,
            "fault_business_result_truth": capture_query_result_truth(
                fault_result,
                ordered=True,
            ),
            "fault_performance": fault_performance,
            "fault_p95_seconds": fault_performance["p95_seconds"],
            "topsql": topsql,
            "query_latency": query_latency,
            "fixture_contract": {
                "outer_rows": self.outer_rows,
                "rule_rows": self.rule_rows,
                "gate_rows": self.gate_rows,
                "region_rows": self.region_rows,
                "expected_matches": self.expected_matches,
                "expected_null_outer_rows": self.expected_null_outer_rows,
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_fault_state(context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._require_success(
            context.env.execute_sql(f"DROP VIEW IF EXISTS {self.db}.{self.view}"),
            f"drop QP06 view {self.db}.{self.view}",
        )
        self._require_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.rule_table}"),
            f"drop QP06 rule table {self.db}.{self.rule_table}",
        )
        self._require_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.gate_table}"),
            f"drop QP06 gate table {self.db}.{self.gate_table}",
        )
        self._require_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.region_table}"),
            f"drop QP06 region table {self.db}.{self.region_table}",
        )
        self._require_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.outer_table}"),
            f"drop QP06 outer table {self.db}.{self.outer_table}",
        )
        remaining = self._payload(
            context.env,
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            f"WHERE TABLE_SCHEMA='{self.db}' AND TABLE_NAME IN "
            f"('{self.outer_table}', '{self.rule_table}', '{self.gate_table}', '{self.region_table}', '{self.view}')",
            "verify QP06 fixture recovery",
        )
        if remaining["result"]:
            raise RuntimeError(
                "QP06 recovery left owned objects behind: "
                f"objects={remaining['result']!r}"
            )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.outer_table = validate_sql_identifier(str(config["outer_table"]), "outer table")
        self.rule_table = validate_sql_identifier(str(config["rule_table"]), "rule table")
        self.gate_table = validate_sql_identifier(str(config["gate_table"]), "gate table")
        self.region_table = validate_sql_identifier(str(config["region_table"]), "region table")
        self.view = validate_sql_identifier(str(config["view"]), "view")
        self.business_query = str(config["business_query"])
        self.performance_query = str(config["performance_query"])
        self.outer_rows = int(config["outer_rows"])
        self.rule_rows = int(config["rule_rows"])
        self.gate_rows = int(config["gate_rows"])
        self.region_rows = int(config["region_rows"])
        self.candidate_matches = int(config["candidate_matches"])
        self.region_expected_matches = int(config["region_expected_matches"])
        self.expected_region_null_rows = int(config["expected_region_null_rows"])
        self.expected_matches = int(config["expected_matches"])
        self.expected_null_outer_rows = int(config["expected_null_outer_rows"])
        self.expected_zero_result_rows = int(config["expected_zero_result_rows"])
        self.sql_timeout_seconds = int(config["sql_timeout_seconds"])

    def _payload(self, env, sql: str, description: str) -> dict:
        return require_success_payload(
            env.execute_sql_with_timeout(sql, self.sql_timeout_seconds),
            f"{description}: sql={sql!r}",
        )

    def _capture_payload(self, env, sql: str, description: str) -> dict:
        """Capture evidence-critical reads with bounded retries.

        These heavy fault-evidence reads share the TiDB node with the running
        background workload; under host load TiDB may drop the client
        connection mid-query (MySQL client error 2013). Each attempt re-runs
        the read from scratch; non-transient failures still raise immediately.
        """
        for attempt in range(1, self.TRANSIENT_CAPTURE_ATTEMPTS + 1):
            try:
                return self._payload(env, sql, description)
            except RuntimeError as exc:
                if attempt == self.TRANSIENT_CAPTURE_ATTEMPTS or not self._is_transient(exc):
                    raise
                print(
                    f"[FaultInjector:QP06] Transient TiDB connection failure while capturing "
                    f"evidence; retrying in {self.TRANSIENT_CAPTURE_RETRY_WAIT_SECONDS}s "
                    f"(attempt {attempt}/{self.TRANSIENT_CAPTURE_ATTEMPTS - 1} retries): {exc}"
                )
                time.sleep(self.TRANSIENT_CAPTURE_RETRY_WAIT_SECONDS)

    @classmethod
    def _is_transient(cls, exc: Exception) -> bool:
        message = str(exc)
        return any(token in message for token in cls.TRANSIENT_CONNECTION_ERROR_TOKENS)

    def _require_success(self, raw, description: str) -> dict:
        return require_success_payload(raw, description)

    def _create_fixture(self, env) -> None:
        self._require_success(
            env.execute_sql(f"CREATE DATABASE IF NOT EXISTS {self.db}"),
            f"create QP06 database {self.db}",
        )
        self._require_success(
            env.execute_sql(f"DROP VIEW IF EXISTS {self.db}.{self.view}"),
            f"clear QP06 view {self.db}.{self.view}",
        )
        self._require_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.rule_table}"),
            f"clear QP06 rule table {self.db}.{self.rule_table}",
        )
        self._require_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.gate_table}"),
            f"clear QP06 gate table {self.db}.{self.gate_table}",
        )
        self._require_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.region_table}"),
            f"clear QP06 region table {self.db}.{self.region_table}",
        )
        self._require_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.outer_table}"),
            f"clear QP06 outer table {self.db}.{self.outer_table}",
        )
        self._require_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.outer_table} ("
                "id BIGINT PRIMARY KEY, lookup_key BIGINT NULL, "
                "risk_scope VARCHAR(16) NOT NULL, payload VARCHAR(32) NOT NULL)"
            ),
            f"create QP06 outer table {self.db}.{self.outer_table}",
        )
        self._require_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.rule_table} ("
                "rule_id BIGINT PRIMARY KEY, rule_key BIGINT NULL, rule_scope VARCHAR(16) NOT NULL, "
                "rule_name VARCHAR(32) NOT NULL)"
            ),
            f"create QP06 rule table {self.db}.{self.rule_table}",
        )
        self._require_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.gate_table} ("
                "gate_id BIGINT PRIMARY KEY, gate_key BIGINT NULL, gate_scope VARCHAR(16) NOT NULL, "
                "gate_name VARCHAR(32) NOT NULL)"
            ),
            f"create QP06 gate table {self.db}.{self.gate_table}",
        )
        self._require_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.region_table} ("
                "region_id BIGINT PRIMARY KEY, region_key BIGINT NULL, region_scope VARCHAR(16) NOT NULL, "
                "region_name VARCHAR(32) NOT NULL)"
            ),
            f"create QP06 region table {self.db}.{self.region_table}",
        )
        outer_rows = [
            (
                n,
                n if n <= self.candidate_matches else None if n == self.outer_rows else n + 100000,
                (
                    "scope_a" if n <= 4000 or n == self.outer_rows
                    else "scope_b" if n <= 7000
                    else "scope_c" if n <= 8500
                    else "scope_d"
                ),
                f"probe-{n}",
            )
            for n in range(1, self.outer_rows + 1)
        ]
        self._insert_batches(
            env,
            f"{self.db}.{self.outer_table}",
            "id, lookup_key, risk_scope, payload",
            outer_rows,
            f"load QP06 outer rows={self.outer_rows}",
        )
        rule_rows = [
            (
                n,
                (
                    n if n <= self.candidate_matches
                    else None if n == self.candidate_matches + 1
                    else n - self.candidate_matches - 1
                    if n <= self.candidate_matches + self.DUPLICATE_MEMBERSHIP_ROWS + 1
                    else n + 200000
                ),
                "scope_a" if n <= 2000 else "scope_b" if n <= 2500 else "scope_c" if n <= 2750 else "scope_d",
                f"rule-{n}",
            )
            for n in range(1, self.rule_rows + 1)
        ]
        self._insert_batches(
            env,
            f"{self.db}.{self.rule_table}",
            "rule_id, rule_key, rule_scope, rule_name",
            rule_rows,
            f"load QP06 rule rows={self.rule_rows}",
        )
        gate_rows = [
            (
                n,
                (
                    n if n <= self.candidate_matches
                    else None if n == self.candidate_matches + 1
                    else n - self.candidate_matches - 1
                    if n <= self.candidate_matches + self.DUPLICATE_MEMBERSHIP_ROWS + 1
                    else n + 300000
                ),
                "scope_a" if n <= 1800 else "scope_b" if n <= 1801 else "scope_c",
                f"gate-{n}",
            )
            for n in range(1, self.gate_rows + 1)
        ]
        self._insert_batches(
            env,
            f"{self.db}.{self.gate_table}",
            "gate_id, gate_key, gate_scope, gate_name",
            gate_rows,
            f"load QP06 gate rows={self.gate_rows}",
        )
        region_rows = [
            (
                n,
                (
                    n if n <= self.region_expected_matches
                    else None if n in (self.region_expected_matches + 1, 2251)
                    else n - self.region_expected_matches - 1
                    if n <= self.region_expected_matches + self.DUPLICATE_MEMBERSHIP_ROWS + 1
                    else n + 400000
                ),
                "scope_a" if n <= 2200 else "scope_b" if n <= 2250 else "scope_c" if n == 2251 else "scope_d",
                f"region-{n}",
            )
            for n in range(1, self.region_rows + 1)
        ]
        self._insert_batches(
            env,
            f"{self.db}.{self.region_table}",
            "region_id, region_key, region_scope, region_name",
            region_rows,
            f"load QP06 region rows={self.region_rows}",
        )
        self._require_success(
            env.execute_sql(
                f"CREATE VIEW {self.db}.{self.view} AS "
                f"SELECT o.id, CASE WHEN (o.lookup_key IN "
                f"(SELECT r.rule_key FROM {self.db}.{self.rule_table} AS r WHERE r.rule_scope LIKE CONCAT(o.risk_scope, '')) "
                f"AND o.lookup_key IN (SELECT g.gate_key FROM {self.db}.{self.gate_table} AS g WHERE g.gate_scope LIKE CONCAT(o.risk_scope, '')) "
                f"AND o.lookup_key IN (SELECT x.region_key FROM {self.db}.{self.region_table} AS x WHERE x.region_scope LIKE CONCAT(o.risk_scope, ''))) THEN 1 "
                f"WHEN o.risk_scope IN ('scope_c', 'scope_d') AND (o.lookup_key IN (SELECT x.region_key FROM {self.db}.{self.region_table} AS x WHERE x.region_scope LIKE CONCAT(o.risk_scope, ''))) IS NULL THEN NULL "
                "WHEN o.risk_scope IN ('scope_b', 'scope_c', 'scope_d') THEN 0 "
                "ELSE NULL END AS matched "
                f"FROM {self.db}.{self.outer_table} AS o"
            ),
            f"create QP06 faulty view {self.db}.{self.view}",
        )
        self._require_success(
            env.execute_sql(f"ANALYZE TABLE {self.db}.{self.outer_table}"),
            f"analyze QP06 outer table {self.db}.{self.outer_table}",
        )
        self._require_success(
            env.execute_sql(f"ANALYZE TABLE {self.db}.{self.rule_table}"),
            f"analyze QP06 rule table {self.db}.{self.rule_table}",
        )
        self._require_success(
            env.execute_sql(f"ANALYZE TABLE {self.db}.{self.gate_table}"),
            f"analyze QP06 gate table {self.db}.{self.gate_table}",
        )
        self._require_success(
            env.execute_sql(f"ANALYZE TABLE {self.db}.{self.region_table}"),
            f"analyze QP06 region table {self.db}.{self.region_table}",
        )

    def _insert_batches(
        self,
        env,
        table: str,
        columns: str,
        rows: list[tuple[int, int | None, str, str]],
        description: str,
    ) -> None:
        for batch_index, start in enumerate(range(0, len(rows), self.INSERT_BATCH_SIZE), start=1):
            batch = rows[start:start + self.INSERT_BATCH_SIZE]
            values = ",".join(
                f"({row_id},{'NULL' if lookup_key is None else lookup_key},'{scope}','{label}')"
                for row_id, lookup_key, scope, label in batch
            )
            self._require_success(
                env.execute_sql(f"INSERT INTO {table} ({columns}) VALUES {values}"),
                f"{description} batch={batch_index}",
            )

    def _verify_fault_state(self, env) -> None:
        outer_count = self._payload(
            env,
            f"SELECT COUNT(*) FROM {self.db}.{self.outer_table}",
            "verify QP06 outer row count",
        )
        if int(outer_count["result"][0][0]) != self.outer_rows:
            raise RuntimeError(
                "QP06 outer fixture row count mismatch: "
                f"expected={self.outer_rows}, observed={outer_count['result'][0][0]}"
            )
        rule_count = self._payload(
            env,
            f"SELECT COUNT(*) FROM {self.db}.{self.rule_table}",
            "verify QP06 rule row count",
        )
        if int(rule_count["result"][0][0]) != self.rule_rows:
            raise RuntimeError(
                "QP06 rule fixture row count mismatch: "
                f"expected={self.rule_rows}, observed={rule_count['result'][0][0]}"
            )
        null_count = self._payload(
            env,
            f"SELECT COUNT(*) FROM {self.db}.{self.rule_table} WHERE rule_key IS NULL",
            "verify QP06 nullable rule key",
        )
        if int(null_count["result"][0][0]) != 1:
            raise RuntimeError(
                "QP06 rule fixture must contain exactly one NULL rule key: "
                f"observed={null_count['result'][0][0]}"
            )
        gate_count = self._payload(
            env,
            f"SELECT COUNT(*) FROM {self.db}.{self.gate_table}",
            "verify QP06 gate row count",
        )
        if int(gate_count["result"][0][0]) != self.gate_rows:
            raise RuntimeError(
                "QP06 gate fixture row count mismatch: "
                f"expected={self.gate_rows}, observed={gate_count['result'][0][0]}"
            )
        gate_null_count = self._payload(
            env,
            f"SELECT COUNT(*) FROM {self.db}.{self.gate_table} WHERE gate_key IS NULL",
            "verify QP06 nullable gate key",
        )
        if int(gate_null_count["result"][0][0]) != 1:
            raise RuntimeError(
                "QP06 gate fixture must contain exactly one NULL gate key: "
                f"observed={gate_null_count['result'][0][0]}"
            )
        region_count = self._payload(
            env,
            f"SELECT COUNT(*) FROM {self.db}.{self.region_table}",
            "verify QP06 region row count",
        )
        if int(region_count["result"][0][0]) != self.region_rows:
            raise RuntimeError(
                "QP06 region fixture row count mismatch: "
                f"expected={self.region_rows}, observed={region_count['result'][0][0]}"
            )
        region_null_count = self._payload(
            env,
            f"SELECT COUNT(*) FROM {self.db}.{self.region_table} WHERE region_key IS NULL",
            "verify QP06 nullable region key",
        )
        if int(region_null_count["result"][0][0]) != self.expected_region_null_rows:
            raise RuntimeError(
                "QP06 region fixture NULL key count mismatch: "
                f"expected={self.expected_region_null_rows}, observed={region_null_count['result'][0][0]}"
            )
        view = self._payload(
            env,
            f"SHOW CREATE VIEW {self.db}.{self.view}",
            "verify QP06 faulty view",
        )
        self._assert_fault_plan(
            self._payload(env, f"EXPLAIN {self.business_query}", "verify QP06 faulty plan")
        )
        view_text = str(view["result"])
        if view_text.casefold().count(" in (select") != 4 or "case" not in view_text.casefold():
            raise RuntimeError(
                "QP06 fault view must retain four scalar CASE IN expressions: "
                f"definition={view_text!r}"
            )

    def _assert_fault_plan(self, payload: dict) -> None:
        plan_text = str(payload["result"]).casefold()
        if plan_text.count("cartesian") != 4 or "semi join" not in plan_text:
            raise RuntimeError(
                "QP06 fault plan must contain four Cartesian semi joins: "
                f"plan={payload['result']!r}"
            )

    def _measure(self, env) -> dict[str, object]:
        warmup = self._capture_payload(env, self.performance_query, "warm up QP06 performance query")
        if len(warmup["result"]) != 1:
            raise RuntimeError(f"QP06 performance warmup returned unexpected rows: {warmup!r}")
        samples = []
        for _ in range(3):
            started = time.perf_counter()
            payload = self._capture_payload(env, self.performance_query, "measure QP06 performance query")
            elapsed = time.perf_counter() - started
            row = payload["result"]
            if len(row) != 1 or int(row[0][0]) != self.expected_matches or int(row[0][1]) != self.outer_rows:
                raise RuntimeError(
                    "QP06 performance query returned wrong truth: "
                    f"expected={[self.expected_matches, self.outer_rows]!r}, observed={row!r}"
                )
            samples.append(elapsed)
        p95 = nearest_rank_percentile(samples, 0.95)
        return {
            "samples_seconds": [round(value, 6) for value in samples],
            "p95_seconds": p95,
            "min_seconds": min(samples),
            "max_seconds": max(samples),
        }


class TidbQueryPerfCaseWhenInCartesianSemiJoinScenario(TiDBScenario):
    scenario_id = "tidb_query_perf_case_when_in_cartesian_semi_join"
    description = "Four nullable CASE IN subqueries expand into Cartesian semi joins over non-unique memberships in TiDB."
    cases = (_CASE, _CASE_REDUCED)

    def build_fault_plan(
        self,
        case: TidbQueryPerfCaseWhenInCartesianSemiJoinCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbQueryPerfCaseWhenInCartesianSemiJoinInjector,
                config={
                    "db": case.db,
                    "outer_table": case.outer_table,
                    "rule_table": case.rule_table,
                    "gate_table": case.gate_table,
                    "region_table": case.region_table,
                    "view": case.view,
                    "business_query": case.business_query,
                    "performance_query": case.performance_query,
                    "outer_rows": case.outer_rows,
                    "rule_rows": case.rule_rows,
                    "gate_rows": case.gate_rows,
                    "region_rows": case.region_rows,
                    "candidate_matches": case.candidate_matches,
                    "region_expected_matches": case.region_expected_matches,
                    "expected_region_null_rows": case.expected_region_null_rows,
                    "expected_matches": case.expected_matches,
                    "expected_null_outer_rows": case.expected_null_outer_rows,
                    "expected_zero_result_rows": case.expected_zero_result_rows,
                    "sql_timeout_seconds": case.runtime.sql_timeout_seconds,
                },
            ),
        )
