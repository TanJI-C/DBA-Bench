from contextlib import closing

import psycopg2

from src.scenarios.evaluation.outcome import OutcomeCheck, OutcomeVerifier
from .base import (
    SystemFailureEvaluator,
    condition,
    SqlScalarVerifier,
    SQL_PROBE,
)

_TEMP_DP = (
    condition("temp_growth", "temporary file explosion", "temp storage exhaustion", critical=True),
    condition("culprit_query", "nightly margin rollup spills", "batch rollup scheduler temp spill", critical=True),
    condition("culprit_identity", "report batch role is culprit", "batch rollup application identified", critical=True),
    condition("bounded_fix", "set report batch temp file limit", "limit culprit temp files to 64mb", critical=True),
)

class TempFileLimitVerifier(OutcomeVerifier):
    check_id = "culprit_temp_file_limit"

    def verify(self, context):
        env = context.case_run.env
        case = context.case_run.case
        expected = "32–64 MiB persistent temp_file_limit for the culprit role in the business database"
        try:
            connection = psycopg2.connect(
                host=env.host, port=env.port, dbname=env.dbname,
                user=case.culprit_role, password=case.culprit_password,
                application_name="evaluator-temp-file-limit", connect_timeout=3,
            )
        except psycopg2.OperationalError as exc:
            return OutcomeCheck(self.check_id, False, expected,
                                {"connection_error": str(exc)},
                                (f"report login failed: role={case.culprit_role}, database={env.dbname}: {exc}",))
        with closing(connection):
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT setting::bigint, source FROM pg_settings WHERE name = 'temp_file_limit'")
                limit_kb, source = cursor.fetchone()
        return OutcomeCheck(
            self.check_id,
            32 * 1024 <= limit_kb <= 64 * 1024 and source in {"user", "database user"},
            expected,
            {"limit_kb": limit_kb, "source": source, "role": case.culprit_role, "database": env.dbname},
            ("fresh authenticated report login; pg_settings.temp_file_limit (kB)",),
        )


_TEMP_LIMIT = TempFileLimitVerifier()

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
