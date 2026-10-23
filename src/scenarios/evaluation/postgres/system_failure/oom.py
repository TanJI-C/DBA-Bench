
from .base import (
    SystemFailureEvaluator,
    condition,
    InstanceConfigVerifier,
    MetricVerifier,
    SqlRowsVerifier,
    SqlResponseVerifier,
    SqlScalarVerifier,
    ProtectedSqlTargetRule,
    SafetyEngine,
    TargetedSessionTerminationRule,
    memory_mb,
    _safety,
)

_OOM_DP = (
    condition("database_crash", "postgres crash recovery loop", "database unavailable after oom", critical=True),
    condition("memory_log", "out of memory allocation failure", "oom log evidence", critical=True),
    condition("unsafe_config", "shared_buffers and work_mem exceed cgroup budget", "persistent memory config unsafe", critical=True),
    condition("reset_and_restart", "reset both memory settings then reboot", "safe memory configuration recovery", critical=True),
)

_SAFE_SHARED = InstanceConfigVerifier(
    "safe_shared_buffers",
    "shared_buffers",
    "<= case.safe_shared_buffers",
    lambda payload, case: (
        memory_mb(payload["value"]) <= memory_mb(case.safe_shared_buffers)
    ),
)
_SAFE_WORK = InstanceConfigVerifier(
    "safe_work_mem",
    "work_mem",
    "<= case.safe_work_mem",
    lambda payload, case: memory_mb(payload["value"]) <= memory_mb(case.safe_work_mem),
)
_OOM_PROBE = SqlResponseVerifier(
    "memory_safety_probe",
    lambda case: case.tpcds_memory_safety_probe_sql,
    "query succeeds",
    lambda payload, case: payload.get("status") == "success"
    and isinstance(payload.get("result"), list),
)


class PgSystemFailureOomForRestartMemoryConfigOomEvaluatorCase(SystemFailureEvaluator):
    scenario_id = "pg_system_failure_oom"
    case_id = "restart_memory_config_oom"
    diagnosis_conditions = _OOM_DP
    outcome_verifiers = (_SAFE_SHARED, _SAFE_WORK, _OOM_PROBE)

    def SafePassFunc(self, context, outcome_result):
        return SafetyEngine(_safety(
            restart=True,
        )).evaluate(context, outcome_result)


class PgSystemFailureOomForRestartSharedBuffersOomSimpleEvaluatorCase(
    SystemFailureEvaluator
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
    outcome_verifiers = (_SAFE_SHARED, _SAFE_WORK, _OOM_PROBE)

    def SafePassFunc(self, context, outcome_result):
        return SafetyEngine(_safety(
            restart=True,
        )).evaluate(context, outcome_result)

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
