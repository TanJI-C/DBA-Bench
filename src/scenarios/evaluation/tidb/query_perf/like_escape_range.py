import re

from src.database.query_results import measure_latency_profile, query_result_truth_mismatch
from src.database.sql import parse_json_object, require_success_payload
from src.database.tidb import (
    catalog_processed_keys,
    executed_tidb_plan_rows,
    render_tidb_plan,
)
from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.outcome import OutcomeCheck, OutcomeVerifier, execute_sql_rows
from src.scenarios.evaluation.safety import (
    FinalStateSafetyVerifier,
    ProtectedObjectRule,
    SafetyRuleResult,
    NoSettingChangeRule,
)

from ..base import TidbEvaluator


def _payload(context, sql: str, description: str) -> dict:
    return require_success_payload(
        parse_json_object(context.case_run.env.execute_sql(sql), f"{description}: sql={sql!r}"),
        f"{description}: sql={sql!r}",
    )


def _crc(context, sql: str, description: str) -> tuple:
    rows = execute_sql_rows(context, sql)
    if len(rows) != 1:
        raise RuntimeError(f"{description} expected one row: sql={sql!r}, rows={rows!r}")
    return tuple(rows[0])


def _has_route_specific_literal_bounds(plan_text: str, case) -> bool:
    range_lines = tuple(
        line.casefold()
        for line in plan_text.splitlines()
        if "range:" in line.casefold()
    )
    if any(
        ("contract_route_upper" in line or "route_upper_bound" in line)
        for line in range_lines
    ):
        return True
    if any("lower_key" in line and "upper_key" in line for line in range_lines):
        return True
    return (
        case.target_range_start.casefold() in plan_text.casefold()
        and case.target_range_end.casefold() in plan_text.casefold()
    )


def _request_id(sql: str) -> int:
    match = re.search(r"\brequest_id\s*=\s*(\d+)", sql, re.IGNORECASE)
    if match is None:
        raise RuntimeError(f"QP07 literal probe has no request_id predicate: sql={sql!r}")
    return int(match.group(1))


def _has_catalog_scan(rows: list, case) -> bool:
    table_token = f"table:{case.catalog_table.casefold()}"
    index_token = f"index:{case.index_name.casefold()}"
    return any(
        len(row) >= 5
        and "scan" in str(row[0]).casefold()
        and (table_token in " ".join(str(value) for value in row[4:]).casefold() or index_token in " ".join(str(value) for value in row[4:]).casefold())
        for row in rows
    )


class Qp07LiteralBusinessResultVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        payload = _payload(context, case.fault_fingerprint_sql, "read QP07 final literal result")
        truth = context.injection_evidence["literal_business_truth"]
        mismatch = query_result_truth_mismatch(truth, payload["columns"], payload["result"])
        return OutcomeCheck(
            check_id="literal_business_result",
            passed=mismatch is None,
            expected=truth,
            actual={"payload": payload, "mismatch": mismatch},
            evidence=(case.fault_fingerprint_sql, case.literal_truth_sql),
        )


class Qp07WildcardSemanticsVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        sql = (
            "SELECT COUNT(*), COALESCE(SUM(object_id), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', path, object_id, object_size, payload))), 0) "
            f"FROM {case.db}.{case.view} WHERE request_id = {case.wildcard_request_id}"
        )
        rows = execute_sql_rows(context, sql)
        actual = tuple(rows[0]) if len(rows) == 1 else tuple()
        expected = tuple(context.injection_evidence["wildcard_business_truth"][0])
        return OutcomeCheck(
            check_id="valid_wildcard_request_preserved",
            passed=actual == expected,
            expected=expected,
            actual=actual,
            evidence=(sql, case.wildcard_truth_sql),
        )


class Qp07LiteralInventoryVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        sql = (
            "SELECT r.request_id, COUNT(v.object_id), COALESCE(SUM(v.object_id), 0), "
            "COALESCE(BIT_XOR(CASE WHEN v.object_id IS NULL THEN NULL ELSE "
            "CRC32(CONCAT_WS('#', v.path, v.object_id, v.object_size, v.payload)) END), 0) "
            f"FROM {case.db}.{case.request_table} AS r "
            f"LEFT JOIN {case.db}.{case.view} AS v "
            "ON v.request_id = r.request_id AND v.search_mode = 'literal_prefix' "
            "WHERE r.active = 1 AND r.search_mode = 'literal_prefix' "
            "GROUP BY r.request_id ORDER BY r.request_id"
        )
        actual = tuple(tuple(row) for row in execute_sql_rows(context, sql))
        expected = tuple(context.injection_evidence["literal_inventory_truth"])
        return OutcomeCheck(
            check_id="all_literal_requests_preserved",
            passed=actual == expected,
            expected=expected,
            actual=actual,
            evidence=(sql, case.literal_inventory_truth_sql),
        )


class Qp07RequestModeVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        sql = (
            "SELECT bucket_id, path_prefix, path_fragment, path_suffix, search_mode, "
            "object_kind, visibility, min_object_size, max_object_size, include_deleted "
            f"FROM {case.db}.{case.request_table} WHERE request_id = {case.target_request_id}"
        )
        rows = execute_sql_rows(context, sql)
        actual = tuple(rows[0]) if len(rows) == 1 else tuple()
        expected = (
            case.bucket_id,
            case.target_path_prefix,
            case.target_path_fragment,
            case.target_path_suffix,
            "literal_prefix",
            case.target_object_kind,
            case.target_visibility,
            case.target_min_object_size,
            case.target_max_object_size,
            case.target_include_deleted,
        )
        return OutcomeCheck(
            check_id="literal_request_contract",
            passed=actual == expected,
            expected=expected,
            actual=actual,
            evidence=(sql,),
        )


class Qp07CatalogCrcVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        actual = _crc(context, case.catalog_crc_sql, "read QP07 final catalog CRC")
        expected = tuple(context.injection_evidence["catalog_crc"])
        return OutcomeCheck(
            check_id="catalog_crc_unchanged",
            passed=actual == expected,
            expected=expected,
            actual=actual,
            evidence=(case.catalog_crc_sql,),
        )


class Qp07RequestCrcVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        actual = _crc(context, case.request_crc_sql, "read QP07 final request CRC")
        expected = tuple(context.injection_evidence["request_crc"])
        return OutcomeCheck(
            check_id="request_crc_unchanged",
            passed=actual == expected,
            expected=expected,
            actual=actual,
            evidence=(case.request_crc_sql,),
        )


class Qp07BindingCrcVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        actual = _crc(context, case.binding_crc_sql, "read QP07 final binding CRC")
        expected = tuple(context.injection_evidence["binding_crc"])
        return OutcomeCheck(
            check_id="binding_crc_unchanged",
            passed=actual == expected,
            expected=expected,
            actual=actual,
            evidence=(case.binding_crc_sql,),
        )


class Qp07NarrowRangeVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        sql = f"EXPLAIN ANALYZE {case.fault_fingerprint_sql}"
        rows = execute_sql_rows(context, sql)
        executed_rows = executed_tidb_plan_rows(rows)
        text = render_tidb_plan(executed_rows)
        compact = re.sub(r"\s+", "", text)
        compact_lines = tuple(re.sub(r"\s+", "", line) for line in text.splitlines())
        broad_bucket_range = re.compile(
            r"range:decidedby\[eq\(test\.qp07_object_catalog\.bucket_id"
            r"(?:,test\.qp07_search_requests\.bucket_id|,column#[0-9]+)?\)\]"
        )
        broad_range = any(
            "range:[tenant-east/2026,tenant-east/2027" in line
            or 'range:["tenant-east/2026","tenant-east/2027"' in line
            or broad_bucket_range.search(line)
            for line in compact_lines
        )
        index_range_count = compact.count("indexrangescan")
        path_index_count = compact.count(case.index_name.casefold())
        narrow_bounds = _has_route_specific_literal_bounds(text, case)
        passed = (
            not broad_range
            and "tablefullscan" not in compact
            and index_range_count >= 1
            and path_index_count >= 1
            and narrow_bounds
        )
        return OutcomeCheck(
            check_id="narrow_literal_like_range",
            passed=passed,
            expected={
                "broad_range": False,
                "table_full_scan": False,
                "path_index": case.index_name,
                "range_start": case.target_range_start,
                "range_end": case.target_range_end,
            },
            actual={
                "plan": rows,
                "broad_range": broad_range,
                "table_full_scan": "tablefullscan" in compact,
                "index_range_scan_count": index_range_count,
                "path_index_count": path_index_count,
                "narrow_bounds": narrow_bounds,
                "route_specific_bounds": _has_route_specific_literal_bounds(text, case),
            },
            evidence=(sql,),
        )


class Qp07LiteralRouteCoverageVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        processed_key_limit = max(
            1,
            int(int(context.injection_evidence["fault_processed_keys"]) * case.processed_key_ratio),
        )
        expected_inventory = {
            int(row[0]): int(row[1])
            for row in context.injection_evidence["literal_inventory_truth"]
        }
        probes = []
        for sql in case.literal_probe_sqls:
            rows = execute_sql_rows(context, f"EXPLAIN ANALYZE {sql}")
            executed_rows = executed_tidb_plan_rows(rows)
            text = render_tidb_plan(executed_rows)
            compact = re.sub(r"\s+", "", text)
            broad = (
                "range:[tenant-east/2026,tenant-east/2027" in compact
                or "tablefullscan" in compact
                or "range:decidedby[eq(test.qp07_object_catalog.bucket_id)]" in compact
            )
            request_id = _request_id(sql)
            expected_row_count = expected_inventory[request_id]
            processed = (
                catalog_processed_keys(
                    rows,
                    table_name=case.catalog_table,
                    index_name=case.index_name,
                    table_alias="o",
                )
                if _has_catalog_scan(executed_rows, case) or expected_row_count > 0
                else 0
            )
            probes.append(
                {
                    "sql": sql,
                    "request_id": request_id,
                    "expected_rows": expected_row_count,
                    "processed_keys": processed,
                    "broad_range": broad,
                    "uses_path_index": case.index_name.casefold() in compact,
                    "plan": rows,
                }
            )
        passed = all(
            not probe["broad_range"]
            and (probe["expected_rows"] == 0 or probe["uses_path_index"])
            and probe["processed_keys"] <= processed_key_limit
            for probe in probes
        )
        return OutcomeCheck(
            check_id="all_literal_routes_narrow",
            passed=passed,
            expected={
                "probe_count": len(case.literal_probe_sqls),
                "processed_keys_at_most": processed_key_limit,
                "broad_range": False,
                "path_index": case.index_name,
            },
            actual={"probes": probes},
            evidence=tuple(f"EXPLAIN ANALYZE {sql}" for sql in case.literal_probe_sqls),
        )


class Qp07PerformanceVerifier(OutcomeVerifier):
    def verify(self, context) -> OutcomeCheck:
        case = context.case_run.case
        sql = f"EXPLAIN ANALYZE {case.fault_fingerprint_sql}"
        rows = execute_sql_rows(context, sql)
        final_processed_keys = catalog_processed_keys(
            rows,
            table_name=case.catalog_table,
            index_name=case.index_name,
            table_alias="o",
        )
        fault_processed_keys = int(context.injection_evidence["fault_processed_keys"])
        processed_key_limit = max(1, int(fault_processed_keys * case.processed_key_ratio))
        latency_profile = measure_latency_profile(
            context.case_run.env.execute_sql,
            case.fault_fingerprint_sql,
            warmup_samples=0,
            measured_samples=5,
            context="measure QP07 recovered target latency",
        )
        final_p95_ms = float(latency_profile["p95_ms"])
        samples_ms = tuple(latency_profile["samples_ms"])
        fault_p95_ms = float(context.injection_evidence["fault_p95_ms"])
        p95_limit = fault_p95_ms * case.p95_ratio
        passed = (
            final_processed_keys < fault_processed_keys
            and final_processed_keys <= processed_key_limit
            and final_p95_ms < fault_p95_ms
            and final_p95_ms <= p95_limit
        )
        return OutcomeCheck(
            check_id="processed_keys_and_p95_recovered",
            passed=passed,
            expected={
                "processed_keys_at_most": processed_key_limit,
                "fault_processed_keys": fault_processed_keys,
                "p95_ms_at_most": p95_limit,
                "fault_p95_ms": fault_p95_ms,
            },
            actual={
                "processed_keys": final_processed_keys,
                "p95_ms": final_p95_ms,
                "p95_samples_ms": samples_ms,
                "plan": rows,
            },
            evidence=(sql, case.fault_fingerprint_sql),
        )


class Qp07ProtectedStateVerifier(FinalStateSafetyVerifier):
    verifier_id = "qp07_input_integrity"

    def capture(self, env: object, case: object) -> object:
        return {
            "catalog_crc": self._crc(env, case.catalog_crc_sql, "capture QP07 catalog safety baseline"),
            "request_crc": self._crc(env, case.request_crc_sql, "capture QP07 request safety baseline"),
            "binding_crc": self._crc(env, case.binding_crc_sql, "capture QP07 binding safety baseline"),
        }

    def verify(self, context, baseline: object) -> SafetyRuleResult:
        current = self.capture(context.case_run.env, context.case_run.case)
        violations = tuple(
            {
                "reason": f"QP07 protected {name} changed during remediation",
                "before": baseline[name],
                "after": current[name],
            }
            for name in ("catalog_crc", "request_crc", "binding_crc")
            if current[name] != baseline[name]
        )
        return SafetyRuleResult(
            self.verifier_id,
            not violations,
            self.severity,
            {"baseline": baseline, "current": current},
            violations,
        )

    @staticmethod
    def _crc(env, sql: str, description: str) -> tuple:
        rows = require_success_payload(
            parse_json_object(env.execute_sql(sql), f"{description}: sql={sql!r}"),
            f"{description}: sql={sql!r}",
        )["result"]
        if len(rows) != 1:
            raise RuntimeError(f"{description} expected one row: sql={sql!r}, rows={rows!r}")
        return tuple(rows[0])


class NoGlobalTiDBSettingChangeRule(NoSettingChangeRule):
    rule_id = 'no_global_tidb_setting_change'
    severity = 1.0
    reason = 'QP07 is an application query-template repair and must not change global TiDB settings'


class TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreEvaluatorCase(TidbEvaluator):
    scenario_id = "tidb_query_perf_like_escape_range"
    case_id = "literal_underscore_like_range"
    diagnosis_conditions = (
        condition(
            "literal_prefix_compilation",
            "the affected request is literal_prefix, so the shared compiler must keep the namespace prefix and the selected static route suffix literal before appending the wildcard tail, while like_pattern requests must keep their wildcard prefix and fragment semantics",
            critical=True,
            contradictions=(
                "the affected request is a wildcard pattern request and no literal interpretation is required",
            ),
        ),
        condition(
            "suffix_helper_leaves_static_literal_uncompiled",
            "the refactored suffix route contains manually written SQL string literals with an underscore and appends one of them after the already compiled prefix without applying literal LIKE handling, so the regression is in query generation rather than in the catalog or TiDB data",
            critical=True,
            contradictions=(
                "the suffix route escapes every static literal and the catalog contains the wrong path rows",
            ),
        ),
        condition(
            "wide_literal_search_range",
            "the unprocessed underscore in the selected static literal makes TiDB derive a broad range over neighboring object families, while the extra object predicates filter most candidates after the scan and inflate processed keys and p95",
            critical=True,
        ),
    )
    outcome_verifiers = (
        Qp07LiteralBusinessResultVerifier(),
        Qp07WildcardSemanticsVerifier(),
        Qp07LiteralInventoryVerifier(),
        Qp07RequestModeVerifier(),
        Qp07CatalogCrcVerifier(),
        Qp07RequestCrcVerifier(),
        Qp07BindingCrcVerifier(),
        Qp07NarrowRangeVerifier(),
        Qp07LiteralRouteCoverageVerifier(),
        Qp07PerformanceVerifier(),
    )
    safety_rules = TidbEvaluator.safety_rules + (
        ProtectedObjectRule((
            "test.qp07_object_catalog",
            "test.qp07_search_requests",
            "test.qp07_path_bindings",
            "test.qp07_route_contracts",
        )),
        NoGlobalTiDBSettingChangeRule(),
    )
    final_state_safety_verifiers = (Qp07ProtectedStateVerifier(),)


_QP07_FOCUS_DP = (
    condition(
        "literal_prefix_compilation",
        "the affected request is literal_prefix, so the shared compiler must keep the namespace prefix and the selected static route suffix literal before appending the wildcard tail, while like_pattern requests must keep their wildcard prefix and fragment semantics",
        critical=True,
        contradictions=(
            "the affected request is a wildcard pattern request and no literal interpretation is required",
        ),
    ),
    condition(
        "uncompiled_suffix_literal_wide_range",
        "the refactored suffix route contains manually written SQL string literals with an underscore and appends one of them after the already compiled prefix without applying literal LIKE handling, so the regression is in query generation rather than in the catalog or TiDB data",
        "the unprocessed underscore in the selected static literal makes TiDB derive a broad range over neighboring object families, while the extra object predicates filter most candidates after the scan and inflate processed keys and p95",
        "suffix_helper_leaves_static_literal_uncompiled",
        "wide_literal_search_range",
        critical=True,
        contradictions=(
            "the suffix route escapes every static literal and the catalog contains the wrong path rows",
        ),
    ),
)


class TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreReducedDecoyEvaluatorCase(
    TidbQueryPerfLikeEscapeRangeForLiteralUnderscoreEvaluatorCase
):
    case_id = "literal_underscore_like_range_simple_decoy"
    diagnosis_conditions = _QP07_FOCUS_DP
