from contextlib import closing

import psycopg2

from src.scenarios.evaluation.outcome import OutcomeCheck, OutcomeVerifier
from .base import (
    SystemFailureEvaluator,
    condition,
    SafetyEngine,
    memory_mb,
    _safety,
)

_OOM_DP = (
    condition("database_crash", "postgres crash recovery loop", "database unavailable after oom", critical=True),
    condition("memory_log", "out of memory allocation failure", "oom log evidence", critical=True),
    condition("unsafe_config", "shared_buffers and work_mem exceed cgroup budget", "persistent memory config unsafe", critical=True),
    condition("reset_and_restart", "reset both memory settings then reboot", "safe memory configuration recovery", critical=True),
)


class MemoryRecoveryVerifier(OutcomeVerifier):
    """Check memory and the original business probe on one fresh login."""

    check_id = "memory_recovery"
    _MEMORY_SQL = """
        SELECT current_database(), current_user,
               pg_size_bytes(current_setting('shared_buffers')),
               pg_size_bytes(current_setting('work_mem')),
               CASE
                   WHEN s.source = 'command line'
                       THEN pg_size_bytes(current_setting('shared_buffers'))
                   WHEN f.setting IS NULL
                       THEN s.boot_val::bigint * pg_size_bytes(s.unit)
                   WHEN f.setting ~ '^[+-]?[0-9]+$'
                       THEN f.setting::bigint * pg_size_bytes(s.unit)
                   ELSE pg_size_bytes(f.setting)
               END AS next_start_shared_buffers_bytes
        FROM pg_settings s
        LEFT JOIN LATERAL (
            SELECT setting FROM pg_file_settings
            WHERE name = 'shared_buffers' ORDER BY seqno DESC LIMIT 1
        ) f ON true
        WHERE s.name = 'shared_buffers'
    """

    def verify(self, context):
        case = context.case_run.case
        env = context.case_run.env
        expected = {
            "shared_buffers": f"running and next start <= {case.safe_shared_buffers}",
            "work_mem": f"fresh business login <= {case.safe_work_mem}",
            "business_probe": "original query succeeds on that login",
        }
        evidence = ("fresh login to the Case business database", self._MEMORY_SQL)
        actual = {"probe_executed": False}
        try:
            connection = env.open_workload_connection("evaluator-oom-memory-recovery")
        except psycopg2.OperationalError as exc:
            return OutcomeCheck(self.check_id, False, expected,
                                {"connection_error": str(exc)}, evidence)
        with closing(connection):
            connection.autocommit = True
            with connection.cursor() as cursor:
                try:
                    cursor.execute(self._MEMORY_SQL)
                    database, role, shared, work, next_shared = cursor.fetchone()
                except psycopg2.Error as exc:
                    return OutcomeCheck(self.check_id, False, expected,
                                        {"configuration_error": str(exc)}, evidence)
                actual.update(database=database, role=role, shared_buffers_bytes=shared,
                              work_mem_bytes=work, next_start_shared_buffers_bytes=next_shared)
                safe_shared = memory_mb(case.safe_shared_buffers) * 1024**2
                safe_work = memory_mb(case.safe_work_mem) * 1024**2
                if shared > safe_shared or next_shared > safe_shared or work > safe_work:
                    return OutcomeCheck(self.check_id, False, expected, actual, evidence)
                actual["probe_executed"] = True
                evidence += (case.tpcds_memory_safety_probe_sql,)
                try:
                    cursor.execute(case.tpcds_memory_safety_probe_sql)
                    actual["probe_rows"] = cursor.fetchall()
                except psycopg2.Error as exc:
                    actual["business_query_error"] = str(exc)
                    return OutcomeCheck(self.check_id, False, expected, actual, evidence)
        return OutcomeCheck(self.check_id, True, expected, actual, evidence)


class PgSystemFailureOomForRestartMemoryConfigOomEvaluatorCase(SystemFailureEvaluator):
    scenario_id = "pg_system_failure_oom"
    case_id = "restart_memory_config_oom"
    diagnosis_conditions = _OOM_DP
    outcome_verifiers = (MemoryRecoveryVerifier(),)

    def SafePassFunc(self, context, outcome_result):
        return SafetyEngine(_safety(
            restart=True,
        )).evaluate(context, outcome_result)


class PgSystemFailureOomForRestartSharedBuffersOomSimpleEvaluatorCase(
    PgSystemFailureOomForRestartMemoryConfigOomEvaluatorCase
):
    scenario_id = "pg_system_failure_oom"
    case_id = "restart_shared_buffers_oom_simple"
    diagnosis_conditions = (
        _OOM_DP[0],
        _OOM_DP[1],
        condition(
            "unsafe_config",
            "shared_buffers exceeds cgroup budget",
            "persistent shared buffers config unsafe",
            critical=True,
        ),
    )

    def _match_exact_diagnosis(self, context):
        expected = {item.condition_id: item for item in self.diagnosis_conditions}
        matched = set()
        extras = set()
        mappings = []
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
                any(marker in text for marker in (
                    "postgres", "postmaster", "database", "readiness", "数据库",
                ))
                and any(marker in text for marker in (
                    "crash", "unavailable", "failed", "exit", "宕机", "不可用", "退出",
                ))
            ):
                condition_matches.add("database_crash")
            if any(marker in text for marker in (
                "oom_kill", "out of memory", "oom killer", "cgroup oom",
                "memory allocation", "内存溢出", "内存不足",
            )):
                condition_matches.add("memory_log")
            if (
                "shared_buffers" in text
                and any(marker in text for marker in (
                    "768mb", "unsafe", "exceed", "cgroup", "budget",
                    "过高", "超过", "预算",
                ))
            ):
                condition_matches.add("unsafe_config")
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
