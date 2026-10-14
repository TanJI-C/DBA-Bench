from unittest.mock import MagicMock

from src.scenarios.evaluation.diagnosis import ExactDiagnosisMatcher
from src.protocols.report import StructuredReport
from src.scenarios import ALL_SCENARIOS
from src.scenarios.postgres.resource_governance.audit_logging import PgResourceGovernanceAuditLoggingInjector
from src.scenarios.postgres.resource_governance.resource_throttling import PgResourceGovernanceResourceThrottlingInjector
from src.scenarios.postgres.resource_governance.resource_throttling import PgResourceGovernanceResourceThrottlingScenario
from src.scenarios.postgres.resource_governance.resource_throttling import build_resource_throttling_noise_profiles


def test_audit_logging_configuration_uses_reloadable_alter_system_settings():
    injector = PgResourceGovernanceAuditLoggingInjector()
    injector.env = MagicMock()
    injector.env.execute_sql.return_value = {"status": "success", "result": []}

    injector._set_config("pgaudit.log", "all")
    injector._reset_config("pgaudit.log")

    assert [call.args[0] for call in injector.env.execute_sql.call_args_list] == [
        "ALTER SYSTEM SET pgaudit.log = 'all';",
        "ALTER SYSTEM RESET pgaudit.log;",
    ]
    injector.env.manage_instance.assert_not_called()


def test_resource_throttling_sets_admin_statement_timeout():
    injector = PgResourceGovernanceResourceThrottlingInjector()
    injector.env = MagicMock()
    injector.env.execute_sql.return_value = {"status": "success", "result": []}

    injector._set_admin_statement_timeout()

    injector.env.execute_sql.assert_called_once_with(
        "ALTER ROLE postgres SET statement_timeout = '30s'; "
        "SET statement_timeout = '30s';"
    )


def test_single_report_role_limit_simple_keeps_same_domain_noise_profiles():
    profiles = build_resource_throttling_noise_profiles("tenant_orders_simple")[:4]
    assert len(profiles) == 4
    assert {profile.application_name for profile in profiles} >= {
        "bi-dashboard-refresh",
        "tenant-revenue-export-preview",
        "etl-ledger-backfill",
    }


def test_single_report_role_limit_simple_alert_keeps_symptom_only_contract():
    case = PgResourceGovernanceResourceThrottlingScenario().cases[1]
    assert case.case_id == "single_report_role_limit_simple"
    alert = case.alert.casefold()
    for leaked in ("report", "export", "role", "isolation", "limit", "work_mem", "connection limit"):
        assert leaked not in alert, f"alert leaks fix direction or culprit class: {leaked}"
    assert "without restarting the instance" in alert
    assert "reduce the risk of recurrence" in alert


def test_resource_governance_scripted_reports_have_applicable_diagnosis():
    scenario_ids = {
        "pg_resource_governance_data_archiving",
        "pg_resource_governance_resource_throttling",
        "pg_resource_governance_audit_logging",
        "pg_resource_governance_privilege_masking",
        "pg_resource_governance_host_backup",
    }
    scenarios = {
        scenario.scenario_id: scenario
        for scenario in ALL_SCENARIOS
        if scenario.scenario_id in scenario_ids
    }

    for scenario in scenarios.values():
        for case in scenario.cases:
            evaluator = case.evaluator(None)
            report = StructuredReport.from_mapping(case.reference_report)
            result = ExactDiagnosisMatcher().match(
                evaluator.diagnosis_conditions,
                report,
                applicable=evaluator.diagnosis_applicable,
            )
            assert result["DiagnosisPass"] is True, case.case_id
