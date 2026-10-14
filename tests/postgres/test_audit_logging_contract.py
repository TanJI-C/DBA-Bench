import json
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.execution.deployments.postgres import PGDockerDeployment
from src.scenarios.evaluation.postgres.resource_governance import audit_logging as evaluation
from src.scenarios.postgres.resource_governance.audit_logging import (
    PgResourceGovernanceAuditLoggingInjector,
    PgResourceGovernanceAuditLoggingScenario,
)
from examples.run_pg_resource_governance_audit_logging_scenario import build_full_score_mock_responses


def audit_records(*commands, read_log=None):
    records = [{"message": f"AUDIT: SESSION,1,1,{category},{command},TABLE,public.audit_probe,<not logged>,<not logged>"}
               for category, command in commands]
    if read_log is not None:
        records.append({"message": read_log})
    return records


REQUIRED_COMMANDS = (("WRITE", "INSERT"), ("WRITE", "UPDATE"), ("WRITE", "DELETE"),
                     ("DDL", "CREATE TABLE"), ("ROLE", "CREATE ROLE"))


@pytest.mark.parametrize('extra_log,passed', [
    (None, True),  # native none
    ("statement: UPDATE public.audit_orders SET amount = amount + 1 WHERE id = 42", True),  # native mod
    ("statement: CREATE TEMP TABLE audit_probe (id integer)", True),  # native ddl
    ("statement: SELECT amount FROM public.audit_orders WHERE id = 42", False),
    ("duration: 1.0 ms  statement: SELECT amount FROM public.audit_orders WHERE id = 42", False),
    ("AUDIT: OBJECT,1,1,READ,SELECT,TABLE,public.audit_orders,<not logged>,<not logged>", False),
    ("AUDIT: SESSION,1,1,READ,SELECT,,,<not logged>,<not logged>", False),
    ("AUDIT: SESSION,1,1,MISC_SET,SET,,,SET work_mem = '1MB',<not logged>", True),
])
def test_outcome_accepts_redundant_write_logs_but_rejects_actual_read_logs(monkeypatch, extra_log, passed):
    records = audit_records(*REQUIRED_COMMANDS, read_log=extra_log)
    monkeypatch.setattr(evaluation, '_audit_probe', lambda context: (
        "SELECT amount FROM public.audit_orders WHERE id = 42", [(1,)], [(42,)], records,
    ))
    check = evaluation._AUDIT_BEHAVIOR.verify(None)
    assert check.passed is passed
    assert check.actual['checkout_read_log_count'] == (0 if passed else 1)


@pytest.mark.parametrize('missing', REQUIRED_COMMANDS)
def test_each_required_audit_operation_must_produce_a_real_record(monkeypatch, missing):
    records = audit_records(*(command for command in REQUIRED_COMMANDS if command != missing))
    monkeypatch.setattr(evaluation, '_audit_probe', lambda context: ('SELECT amount', [(1,)], [(42,)], records))
    assert not evaluation._AUDIT_BEHAVIOR.verify(None).passed


def test_ddl_audit_must_identify_the_created_object(monkeypatch):
    records = audit_records(*REQUIRED_COMMANDS)
    for record in records:
        if ',DDL,CREATE TABLE,' in record['message']:
            record['message'] = 'AUDIT: SESSION,1,1,DDL,CREATE TABLE,,,CREATE TEMP TABLE probe (id int),<not logged>'
    monkeypatch.setattr(evaluation, '_audit_probe', lambda context: ('SELECT amount', [(1,)], [(42,)], records))
    assert not evaluation._AUDIT_BEHAVIOR.verify(None).passed


def test_native_logs_and_placeholder_settings_cannot_replace_audit_records(monkeypatch):
    records = [{"message": "statement: UPDATE audit_orders SET amount = amount + 1"}]
    monkeypatch.setattr(evaluation, '_audit_probe', lambda context: ('SELECT amount', [(1,)], [(42,)], records))
    assert not evaluation._AUDIT_BEHAVIOR.verify(None).passed


@pytest.mark.parametrize('read_rows,write_rows', [([], [(42,)]), ([(None,)], [(42,)]), ([(1,)], [])])
def test_business_read_and_write_must_succeed(monkeypatch, read_rows, write_rows):
    monkeypatch.setattr(evaluation, '_audit_probe', lambda context: (
        'SELECT amount', read_rows, write_rows, audit_records(*REQUIRED_COMMANDS),
    ))
    assert not evaluation._AUDIT_BEHAVIOR.verify(None).passed


@pytest.mark.parametrize('delayed', [False, True])
def test_probe_rolls_back_and_isolates_logs_by_backend(delayed):
    env = MagicMock()
    observer, conn = MagicMock(), MagicMock()
    env.open_workload_connection.side_effect = [observer, conn]
    conn.get_backend_pid.return_value = 73
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchall.side_effect = [[(1,)], [(42,)]]
    log_cur = observer.cursor.return_value.__enter__.return_value
    reads = 0
    def fetchone():
        nonlocal reads
        if 'pg_read_file' not in log_cur.execute.call_args.args[0]:
            return (0,)
        reads += 1
        if delayed and reads == 1:
            return ('2026-10-14 19:35:34.822 UTC [99] LOG:  unrelated\n',)
        marker = cur.execute.call_args.args[0].split("RAISE LOG '")[1].split("'")[0]
        return (
            "2026-10-14 19:35:34.822 UTC [99] LOG:  statement: SELECT amount FROM audit_orders\n"
            f"2026-10-14 19:35:34.822 UTC [73] LOG:  {marker}\n",
        )
    log_cur.fetchone.side_effect = fetchone
    context = SimpleNamespace(case_run=SimpleNamespace(case=SimpleNamespace(table='audit_orders'), env=env))
    _, _, _, records = evaluation._audit_probe(context)
    assert len(records) == 1 and records[0]['pid'] == 73
    conn.rollback.assert_called_once()
    conn.close.assert_called_once()
    observer.close.assert_called_once()
    conn.commit.assert_not_called()
    env.execute_sql.assert_not_called()
    assert reads == (2 if delayed else 1)
    statements = [call.args[0] for call in cur.execute.call_args_list]
    assert any(sql.startswith('INSERT INTO public.audit_orders') for sql in statements)
    assert any(sql.startswith('DELETE FROM public.audit_orders') for sql in statements)
    assert any(sql.startswith('CREATE TEMP TABLE') for sql in statements)
    assert any(sql.startswith('CREATE ROLE') for sql in statements)


def test_probe_rolls_back_on_sql_failure():
    env = MagicMock()
    observer, conn = MagicMock(), MagicMock()
    env.open_workload_connection.side_effect = [observer, conn]
    observer.cursor.return_value.__enter__.return_value.fetchone.return_value = (0,)
    cur = conn.cursor.return_value.__enter__.return_value
    cur.execute.side_effect = RuntimeError('probe SQL failed')
    context = SimpleNamespace(case_run=SimpleNamespace(case=SimpleNamespace(table='audit_orders'), env=env))
    with pytest.raises(RuntimeError, match='probe SQL failed'):
        evaluation._audit_probe(context)
    conn.rollback.assert_called_once()
    conn.close.assert_called_once()
    observer.close.assert_called_once()


@pytest.mark.parametrize('case', PgResourceGovernanceAuditLoggingScenario().cases, ids=lambda case: case.case_id)
def test_mock_repair_removes_read_grants_and_retains_pgaudit(case):
    responses = build_full_score_mock_responses(case)
    text = json.dumps(responses)
    assert "ALTER SYSTEM SET log_statement = 'none'" in text
    assert "ALTER SYSTEM SET pgaudit.log = 'write, ddl, role'" in text
    assert f'REVOKE SELECT ON {case.table} FROM {case.audit_role}' in text
    assert dict(case.runtime.parameters.parameters)['shared_preload_libraries'] == 'pg_stat_statements,pgaudit'
    plan = PgResourceGovernanceAuditLoggingScenario().build_fault_plan(case)[0]
    assert plan.config['audit_role'] == case.audit_role


def test_extension_install_precedes_enabling_audit(monkeypatch):
    injector = PgResourceGovernanceAuditLoggingInjector()
    env = MagicMock()
    env.metrics_hidden.return_value = nullcontext()
    env.execute_sql.return_value = {'status': 'success', 'result': []}
    for method in ('_setup_table_and_role', '_verify_persistent_state', '_scrub_agent_visible_history', '_start_runtime'):
        monkeypatch.setattr(injector, method, lambda: None)
    context = SimpleNamespace(config={'table': 'audit_orders', 'audit_role': 'auditor', 'worker_count': 1}, env=env)
    injector.install(context)
    statements = [call.args[0] for call in env.execute_sql.call_args_list]
    assert statements.index('CREATE EXTENSION pgaudit;') < statements.index("ALTER SYSTEM SET pgaudit.log = 'all';")


def test_deployment_initializes_from_extension_image():
    deployment = PGDockerDeployment(initialization_image='aiopsbench-pg-audit-base:pg16')
    command = deployment._build_docker_run_command(for_init=True)
    assert 'aiopsbench-pg-audit-base:pg16' in command
    assert 'postgres:16' not in command
