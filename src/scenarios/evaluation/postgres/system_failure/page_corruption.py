
from .base import (
    SystemFailureEvaluator,
    condition,
    SqlRowsVerifier,
    SqlScalarVerifier,
    SqlResponseVerifier,
)
from src.scenarios.evaluation.outcome import OutcomeCheck, OutcomeVerifier, execute_sql_rows

_CORRUPTION_DP = (
    condition("checksum_error", "invalid page checksum error", "physical page corruption", critical=True),
    condition("affected_relation", "order line audit relation affected", "corrupt relation identified", critical=True),
    condition("not_sql_repair", "ordinary sql cannot repair physical corruption", "rebuild from clean copy required", critical=True),
    condition("recovery_source", "restore from verified clean snapshot", "rebuild service from validated source", critical=True),
)
_HEALTHY_QUERY = SqlRowsVerifier(
    "unaffected_database_query_succeeds",
    lambda case: "SELECT count(*) FROM pg_class",
    "query succeeds",
    lambda rows, case: len(rows) == 1 and int(rows[0][0]) > 0,
)
_RECOVERED_QUERY = SqlResponseVerifier(
    "corruption_query_recovered",
    lambda case: f"SET statement_timeout = '5s'; {case.check_query}",
    "successful business read",
    lambda payload, case: payload.get("status") == "success",
)
_CORRUPT_EVIDENCE_PRESERVED = SqlScalarVerifier(
    "corrupt_evidence_relation_preserved",
    lambda case: (
        "SELECT count(*) FROM pg_class c JOIN page_corruption_recovery_manifest m "
        "ON c.relfilenode = m.original_relfilenode "
        f"WHERE m.service_relation = '{case.table}' AND c.relname <> m.service_relation"
    ),
    1,
    lambda actual, case: int(actual) == 1,
)
_SERVICE_INDEX_PRESERVED = SqlScalarVerifier(
    "service_business_index_present",
    lambda case: (
        "SELECT count(*) FROM pg_index i "
        "JOIN pg_class tbl ON tbl.oid = i.indrelid "
        "JOIN pg_class idx ON idx.oid = i.indexrelid "
        "JOIN pg_attribute a ON a.attrelid = tbl.oid AND a.attname = 'order_id' "
        f"WHERE tbl.relname = '{case.table}' AND idx.relkind = 'i' "
        "AND i.indisvalid AND i.indnkeyatts = 1 AND i.indkey[0] = a.attnum"
    ),
    "a valid single-column index on order_id exists on the service relation",
    lambda actual, case: int(actual) >= 1,
)
_RECOVERY_BUSINESS_CHECK = SqlScalarVerifier(
    "recovery_source_business_check",
    lambda case: f"SELECT count(*) FROM {case.table} WHERE order_id = 1 AND amount = (SELECT expected_amount FROM page_corruption_recovery_manifest WHERE service_relation = '{case.table}')",
    1,
    lambda actual, case: int(actual) == 1,
)


class _RecoverySumVerifier(OutcomeVerifier):
    """Verify the recovered service relation against the ledger's business checksum.

    A service relation that is still damaged cannot be full-scanned; the check
    fails cleanly with the probe error instead of raising a read failure.
    """

    check_id = "recovery_amount_sum_intact"

    def verify(self, context):
        import json

        case = context.case_run.case
        probe = context.case_run.env.execute_sql(
            f"SET statement_timeout = '5s'; {case.check_query}"
        )
        payload = probe if isinstance(probe, dict) else json.loads(probe)
        if payload.get("status") != "success":
            return OutcomeCheck(
                check_id=self.check_id,
                passed=False,
                expected="recovered service relation matches the ledger business checksum",
                actual={"readable": False, "error": str(payload.get("error", ""))[:200]},
                evidence=("business checksum over recovered service relation",),
            )
        sql = (
            "SELECT CASE WHEN (SELECT sum(amount) FROM "
            f"{case.table}) = (SELECT expected_amount_sum FROM page_corruption_recovery_manifest "
            f"WHERE service_relation = '{case.table}') THEN 1 ELSE 0 END"
        )
        actual = execute_sql_rows(context, sql)[0][0]
        return OutcomeCheck(
            check_id=self.check_id,
            passed=int(actual) == 1,
            expected="recovered service relation matches the ledger business checksum",
            actual={"readable": True, "checksum_matches": int(actual) == 1},
            evidence=(sql,),
        )


_RECOVERY_SUM_CHECK = _RecoverySumVerifier()
class _AuditBusinessTruthVerifier(OutcomeVerifier):
    """Result-type business truth for the order-detail audit case: the restored
    read path must match the pre-incident audit baseline. A read failure or a
    destroyed baseline is a diagnosable failed check, never a silent pass."""

    _BASELINE_TABLE = "order_detail_audit_baseline"

    def __init__(self, check_id: str, column: str, aggregate: str):
        self.check_id = check_id
        self.column = column
        self.aggregate = aggregate

    def verify(self, context):
        import json

        case = context.case_run.case
        probe = context.case_run.env.execute_sql(
            f"SET statement_timeout = '5s'; {case.check_query}"
        )
        payload = probe if isinstance(probe, dict) else json.loads(probe)
        if payload.get("status") != "success":
            return OutcomeCheck(
                check_id=self.check_id,
                passed=False,
                expected=self._expected(),
                actual={"readable": False, "error": str(payload.get("error", ""))[:200]},
                evidence=("audit baseline comparison over the restored read path",),
            )
        sql = (
            "SELECT CASE WHEN (SELECT " + self.aggregate + " FROM " + case.read_path_view + ") = "
            "(SELECT " + self.column + " FROM " + self._BASELINE_TABLE + ") THEN 1 ELSE 0 END"
        )
        raw = context.case_run.env.execute_sql(sql)
        payload = raw if isinstance(raw, dict) else json.loads(raw)
        if payload.get("status") != "success":
            return OutcomeCheck(
                check_id=self.check_id,
                passed=False,
                expected=self._expected(),
                actual={"readable": True, "baseline_error": str(payload.get("error", ""))[:200]},
                evidence=(sql,),
            )
        matches = int(payload["result"][0][0]) == 1
        return OutcomeCheck(
            check_id=self.check_id,
            passed=matches,
            expected=self._expected(),
            actual={"readable": True, "baseline_matches": matches},
            evidence=(sql,),
        )

    def _expected(self) -> str:
        return (
            f"restored audit dataset {self.aggregate} equals the audit baseline {self.column}"
        )


_AUDIT_ROW_COUNT_INTACT = _AuditBusinessTruthVerifier(
    "audit_row_count_intact", "expected_row_count", "count(*)"
)
_AUDIT_AMOUNT_SUM_INTACT = _AuditBusinessTruthVerifier(
    "audit_amount_sum_intact", "expected_amount_sum", "sum(amount)"
)
_AUDIT_WEIGHTED_SUM_INTACT = _AuditBusinessTruthVerifier(
    "audit_weighted_sum_intact", "expected_weighted_amount_sum", "sum(amount * order_id)"
)


class PgSystemFailurePageCorruptionForOrderLineAuditPageCorruptionEvaluatorCase(SystemFailureEvaluator):
    scenario_id = "pg_system_failure_page_corruption"
    case_id = "order_line_audit_page_corruption"
    diagnosis_conditions = _CORRUPTION_DP
    outcome_verifiers = (
        _RECOVERED_QUERY,
        _HEALTHY_QUERY,
        _AUDIT_ROW_COUNT_INTACT,
        _AUDIT_AMOUNT_SUM_INTACT,
        _AUDIT_WEIGHTED_SUM_INTACT,
    )


class PgSystemFailurePageCorruptionForInvoicePageCorruptionTriageSimpleEvaluatorCase(
    SystemFailureEvaluator
):
    scenario_id = "pg_system_failure_page_corruption"
    case_id = "invoice_page_corruption_triage_simple"
    diagnosis_conditions = (
        _CORRUPTION_DP[0],
        condition("affected_relation", "invoice page audit relation affected", "corrupt relation identified", critical=True),
    )
    outcome_verifiers = (_RECOVERED_QUERY, _HEALTHY_QUERY, _CORRUPT_EVIDENCE_PRESERVED, _SERVICE_INDEX_PRESERVED, _RECOVERY_BUSINESS_CHECK, _RECOVERY_SUM_CHECK)

    def DiagnosisPassFunc(self, context):
        expected = {item.condition_id: item for item in self.diagnosis_conditions}
        matched = set()
        extras = set()
        mappings = []
        case = context.case_run.case
        for index, submitted in enumerate(context.report.diagnosis.conditions):
            terms = {
                submitted.type.casefold(),
                submitted.factor.casefold(),
                submitted.entity.casefold(),
            }
            text = " ".join((*terms, *(item.casefold() for item in submitted.evidence)))
            condition_matches = {
                condition_id
                for condition_id, spec in expected.items()
                if spec.aliases & terms
            }
            if any(marker in text for marker in (
                "checksum mismatch", "page verification failed", "invalid page",
                "physical page corruption", "物理页损坏", "校验和",
            )):
                condition_matches.add("checksum_error")
            if (
                case.table.casefold() in text
                and any(marker in text for marker in (
                    "relation", "relfilenode", "block 1", "corrupt", "损坏", "关系",
                ))
            ):
                condition_matches.add("affected_relation")
            if (
                any(marker in text for marker in (
                    "physical", "checksum", "invalid page", "物理", "校验和",
                ))
                and any(marker in text for marker in (
                    "cannot repair", "not repairable", "ordinary sql", "preserve evidence",
                    "offline restore", "pitr", "restore from backup", "无法修复",
                    "证据保全", "离线恢复", "备份恢复",
                ))
            ):
                condition_matches.add("not_sql_repair")
            matched.update(condition_matches)
            if condition_matches:
                mappings.append({
                    "submitted_index": index,
                    "condition_ids": sorted(condition_matches),
                })
            else:
                extras.update(terms)

        missing = [
            item.condition_id for item in self.diagnosis_conditions
            if item.condition_id not in matched
        ]
        return {
            "DiagnosisPass": not missing,
            "diagnosis_applicable": True,
            "report_valid": True,
            "submitted_conditions": [
                {
                    "type": item.type,
                    "factor": item.factor,
                    "entity": item.entity,
                    "evidence": list(item.evidence),
                }
                for item in context.report.diagnosis.conditions
            ],
            "matched_conditions": [
                item.condition_id for item in self.diagnosis_conditions
                if item.condition_id in matched
            ],
            "missing_conditions": missing,
            "extra_conditions": sorted(extras),
            "critical_missing": missing,
            "contradictory_conditions": [],
            "condition_mappings": mappings,
            "evidence_references": [
                evidence
                for item in context.report.diagnosis.conditions
                for evidence in item.evidence
            ],
        }
