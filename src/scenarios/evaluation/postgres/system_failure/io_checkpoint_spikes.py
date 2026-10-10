
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

_CHECKPOINT_DP = (
    condition("latency_spikes", "periodic checkpoint latency spikes", "disk io checkpoint correlation", critical=True),
    condition("aggressive_config", "checkpoint settings too aggressive", "small wal size and short checkpoint timeout", critical=True),
    condition("checkpoint_evidence", "bgwriter checkpoint deltas", "checkpoint write spike evidence", critical=True),
    condition("tune_reload", "tune checkpoint settings and reload", "restore checkpoint parameters without restart", critical=True),
)

_CHECKPOINT_CONFIG = SqlRowsVerifier(
    "checkpoint_configuration",
    lambda case: (
        "SELECT EXTRACT(EPOCH FROM current_setting('checkpoint_timeout')::interval) "
        f">= EXTRACT(EPOCH FROM '{case.checkpoint_timeout_target}'::interval), "
        "pg_size_bytes(current_setting('max_wal_size')) "
        f">= pg_size_bytes('{case.max_wal_size_target}'), "
        "current_setting('checkpoint_completion_target')::float8 "
        f">= {case.checkpoint_completion_target_target}::float8"
    ),
    "checkpoint storm relieved: timeout, max_wal_size, and completion target at or beyond the case targets",
    lambda rows, case: len(rows) == 1 and all(bool(value) for value in rows[0]),
)


class PgSystemFailureIoCheckpointSpikesForCheckoutCheckpointSpikesEvaluatorCase(SystemFailureEvaluator):
    scenario_id = "pg_system_failure_io_checkpoint_spikes"
    case_id = "checkout_checkpoint_spikes"
    diagnosis_conditions = _CHECKPOINT_DP
    outcome_verifiers = (_CHECKPOINT_CONFIG, SQL_PROBE)


class PgSystemFailureIoCheckpointSpikesForSingleCheckoutCheckpointSpikeSimpleEvaluatorCase(SystemFailureEvaluator):
    scenario_id = "pg_system_failure_io_checkpoint_spikes"
    case_id = "single_checkout_checkpoint_spike_simple"
    diagnosis_conditions = _CHECKPOINT_DP[:3]
    outcome_verifiers = (_CHECKPOINT_CONFIG, SQL_PROBE)

    def DiagnosisPassFunc(self, context):
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
                "checkpoint" in text
                and any(marker in text for marker in (
                    "frequent", "频繁", "spike", "尖峰", "storm", "风暴",
                    "burst", "抖动", "stall", "周期",
                ))
            ):
                condition_matches.add("latency_spikes")
            if (
                all(marker in text for marker in (
                    "max_wal_size", "checkpoint_timeout", "checkpoint_completion_target",
                ))
                and any(marker in text for marker in (
                    "64mb", "90s", "0.3", "unsafe", "aggressive", "过小", "过短", "过低",
                ))
            ):
                condition_matches.add("aggressive_config")
            if (
                any(marker in text for marker in (
                    "pg_stat_bgwriter", "checkpoints_req", "checkpoint_write_time",
                    "checkpoint complete", "walwrite",
                ))
                and any(marker in text for marker in (
                    "checkpoint", "write", "i/o", "io", "写入", "刷",
                ))
            ):
                condition_matches.add("checkpoint_evidence")
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
