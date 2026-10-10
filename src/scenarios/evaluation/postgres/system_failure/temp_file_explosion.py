
from .base import (
    SystemFailureEvaluator,
    condition,
    InstanceConfigVerifier,
    MetricVerifier,
    SqlRowsVerifier,
    SqlScalarVerifier,
    ProtectedSqlTargetRule,
    SafetyEngine,
    TargetedSessionTerminationRule,
    SQL_PROBE,
    _safety,
)

_TEMP_DP = (
    condition("temp_growth", "temporary file explosion", "temp storage exhaustion", critical=True),
    condition("culprit_query", "nightly margin rollup spills", "batch rollup scheduler temp spill", critical=True),
    condition("culprit_identity", "report batch role is culprit", "batch rollup application identified", critical=True),
    condition("bounded_fix", "set report batch temp file limit", "limit culprit temp files to 64mb", critical=True),
)

_TEMP_LIMIT = SqlScalarVerifier(
    "culprit_temp_file_limit",
    lambda case: (
        "SELECT count(*) FROM pg_db_role_setting s JOIN pg_roles r ON r.oid = s.setrole "
        "CROSS JOIN LATERAL unnest(s.setconfig) cfg "
        f"WHERE r.rolname = '{case.culprit_role}' AND lower(cfg) LIKE 'temp_file_limit=%' "
        "AND pg_size_bytes(split_part(cfg, '=', 2)) "
        "BETWEEN pg_size_bytes('32MB') AND pg_size_bytes('64MB')"
    ),
    1,
    lambda actual, case: int(actual) == 1,
)

_TEMP_SESSION_GONE = SqlScalarVerifier(
    "culprit_session_gone",
    lambda case: f"SELECT count(*) FROM pg_stat_activity WHERE application_name = '{case.culprit_application}' AND query ILIKE '%job={case.culprit_job} %'",
    0,
    lambda actual, case: int(actual) == 0,
)

class PgSystemFailureTempFileExplosionForNightlyMarginTempExhaustionEvaluatorCase(SystemFailureEvaluator):
    scenario_id = "pg_system_failure_temp_file_explosion"
    case_id = "nightly_margin_temp_exhaustion"
    diagnosis_conditions = _TEMP_DP
    outcome_verifiers = (_TEMP_LIMIT, _TEMP_SESSION_GONE, SQL_PROBE)


class PgSystemFailureTempFileExplosionForDailySalesTempExhaustionSimpleEvaluatorCase(
    PgSystemFailureTempFileExplosionForNightlyMarginTempExhaustionEvaluatorCase
):
    case_id = "daily_sales_temp_exhaustion_simple"
    diagnosis_conditions = _TEMP_DP[:3]

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
            if (
                any(marker in text for marker in ("temp", "scratch", "pgsql_tmp", "临时"))
                and any(marker in text for marker in (
                    "exhaust", "no space", "fill", "growth", "占用", "耗尽", "写满",
                ))
            ):
                condition_matches.add("temp_growth")
            if (
                any(marker in text for marker in (
                    "daily_sales_rollup", "materialized", "batch rollup", "批处理", "物化",
                ))
                and any(marker in text for marker in (
                    "temp", "spill", "scratch", "pgsql_tmp", "临时",
                ))
            ):
                condition_matches.add("culprit_query")
            if (
                any(marker in text for marker in (
                    case.culprit_role.casefold(),
                    case.culprit_application.casefold(),
                ))
                and any(marker in text for marker in (
                    "culprit", "root cause", "caused", "consumer", "占用", "导致", "根因",
                ))
            ):
                condition_matches.add("culprit_identity")
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
