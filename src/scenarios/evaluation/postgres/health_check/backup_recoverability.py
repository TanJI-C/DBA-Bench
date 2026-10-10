from .base import (
    HealthCheckEvaluator,
    condition,
    InstanceActionVerifier,
    OutcomeCheck,
    SqlRowsVerifier,
    SqlScalarVerifier,
    AllowedSqlTargetsRule,
    ProtectedSqlTargetRule,
    SafetyEngine,
    TargetedSessionTerminationRule,
    _safety,
    _sql_array,
)
from src.scenarios.evaluation.outcome import OutcomeVerifier, normalize_report_term, report_outcome_text

_BACKUP_DP = (
    condition("selected_backup", "selected checkout ledger backup chain", "target base backup identified", critical=True),
    condition("missing_wal", "missing wal segment a7", "archive continuity gap", critical=True),
    condition("latest_point", "latest recoverable point is 02:31", "requested target exceeds recoverable time by 14 minutes", critical=True),
    condition("noise_excluded", "standby seed and reporting clone are not approved recovery sources", "backup noise excluded", critical=True),
    condition("risk", "business rpo is violated", "repair archive gap before pitr", critical=True),
)
_BACKUP_SIMPLE_DP = (
    condition(
        "selected_backup",
        "selected ledger backup chain",
        "selected backup chain",
        "selected base backup",
        "selected recovery window base backup",
        "DR_READINESS_BLOCKER",
        "归档 WAL 不连续，导致所选业务恢复窗口不能签核",
        "target base backup identified",
        critical=True,
    ),
    condition(
        "missing_wal",
        "required wal segment is missing",
        "missing wal segment",
        "archive continuity gap",
        "archive gap",
        "WAL Segment Missing",
        "archive chain gap",
        "归档 WAL 不连续，导致所选业务恢复窗口不能签核",
        critical=True,
        contradictions=("archive chain is complete",),
    ),
    condition(
        "latest_point",
        "requested target exceeds latest recoverable point",
        "latest recoverable point calculated",
        "latest recovery point",
        "requested recovery point",
        "LATEST_SAFE_RECOVERY_POINT",
        "最新安全恢复点早于业务请求恢复点",
        "latest safe recovery point",
        critical=True,
    ),
)
_BACKUP_VALIDATION = InstanceActionVerifier(
    "backup_restore_validation", "validate_backup", lambda case: case.backup_path,
    "failed with the expected WAL gap",
    lambda payload, case: payload["validation_status"] == "failed"
    and payload["latest_recoverable_time"] == case.latest_recoverable_time
    and any(item["wal_file"] == case.missing_wal_file for item in payload["missing_wal_segments"]),
)
class _BackupRiskReportVerifier(OutcomeVerifier):
    check_id = "backup_risk_report"

    def verify(self, context):
        case = context.case_run.case
        text = report_outcome_text(context)
        case_evidence = all(normalize_report_term(term) in text for term in (
            case.missing_wal_file,
            str(case.latest_recoverable_time)[11:16],
            str(case.requested_recovery_target_time)[11:16],
        ))
        return OutcomeCheck(
            check_id=self.check_id,
            passed=case_evidence,
            expected="explicit WAL gap and latest/requested recovery points",
            actual={"matched_path": "case_evidence" if case_evidence else None},
            evidence=(*context.report.outcome.changes, *context.report.outcome.verification, context.report.summary),
        )


_BACKUP_REPORT = _BackupRiskReportVerifier()


class PgHealthCheckBackupRecoverabilityForMissingWalRecoveryGapEvaluatorCase(HealthCheckEvaluator):
    scenario_id = "pg_health_check_backup_recoverability"
    case_id = "missing_wal_recovery_gap"
    diagnosis_conditions = _BACKUP_DP
    outcome_verifiers = (_BACKUP_VALIDATION, _BACKUP_REPORT)


class PgHealthCheckBackupRecoverabilityForSingleMissingWalGapSimpleEvaluatorCase(HealthCheckEvaluator):
    scenario_id = "pg_health_check_backup_recoverability"
    case_id = "single_missing_wal_gap_simple"
    diagnosis_conditions = _BACKUP_SIMPLE_DP
    outcome_verifiers = (_BACKUP_VALIDATION, _BACKUP_REPORT)
