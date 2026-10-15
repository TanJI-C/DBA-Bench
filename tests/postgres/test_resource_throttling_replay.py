"""Behavioral OP regression. Live PostgreSQL checks are opt-in (about 4 minutes)."""
import json
import os
import socket
import subprocess
import threading
import time
import uuid
from contextlib import closing
from types import SimpleNamespace

import psycopg2
import pytest

from src.database.query_results import capture_query_result_truth
from src.execution.environments.postgres import PGEnv
from src.execution.host_ports import reserve_host_ports
from src.scenarios.evaluation.postgres.resource_governance import resource_throttling as op
from src.scenarios.postgres.resource_governance.resource_throttling import (
    PgResourceGovernanceResourceThrottlingInjector,
    PgResourceGovernanceResourceThrottlingScenario,
)
from src.scenarios.runtime.workload_runner import WorkloadRunner


def test_op_budget_bounds_a_server_that_never_completes_login(monkeypatch):
    # A real TCP socket accepts the connection but sends no PostgreSQL handshake.
    with closing(socket.socket()) as server:
        server.bind(('127.0.0.1', 0))
        server.listen()
        monkeypatch.setattr(op, 'OP_BUDGET_SECONDS', 5.05)  # 5s is reserved for cleanup.
        env = SimpleNamespace(host='127.0.0.1', port=server.getsockname()[1],
                              dbname='testdb', user='postgres', password='test')
        context = SimpleNamespace(case_run=SimpleNamespace(env=env, case=None),
                                  injection_evidence={'resource_throttling_business_truth': {}})
        started = time.monotonic()
        result = op.ReportReplayVerifier().verify(context)
    assert not result.passed
    assert 'deadline exceeded' in result.actual['failure']
    assert time.monotonic() - started < 0.5


def test_report_client_uses_case_query_without_overriding_role_settings(monkeypatch):
    from unittest.mock import MagicMock
    case = PgResourceGovernanceResourceThrottlingScenario().cases[0]
    injector = PgResourceGovernanceResourceThrottlingInjector()
    injector._configure(PgResourceGovernanceResourceThrottlingScenario().build_fault_plan(case)[0].config,
                        SimpleNamespace(host='localhost', port=5432, dbname='testdb'))
    conn = MagicMock()
    monkeypatch.setattr(psycopg2, 'connect', lambda **kwargs: conn)
    injector._run_report_query()
    conn.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(case.report_query)
    conn.close.assert_called_once()


@pytest.fixture(scope='module')
def live_env():
    if os.environ.get('DBA_BENCH_LIVE_RESOURCE_OP') != '1':
        pytest.skip('set DBA_BENCH_LIVE_RESOURCE_OP=1 to run real PostgreSQL replay checks')
    name = 'dba-resource-op-test-' + uuid.uuid4().hex[:8]
    with reserve_host_ports(16430, (0,), owner=name) as lease:
        port = lease.ports[0]
        subprocess.run([
            'docker', 'run', '-d', '--name', name, '--cpus=1', '--memory=512m',
            '--memory-swap=512m', '-e', 'POSTGRES_INITDB_ARGS=--no-sync', '-e', 'POSTGRES_PASSWORD=password', '-e', 'POSTGRES_DB=testdb',
            '-p', f'127.0.0.1:{port}:5432', 'postgres:16',
        ], check=True, capture_output=True)
        try:
            for _ in range(360):
                ready = subprocess.run(['docker', 'exec', name, 'pg_isready', '-h', '127.0.0.1',
                                        '-U', 'postgres', '-d', 'testdb'], capture_output=True, timeout=5)
                if ready.returncode == 0:
                    break
                time.sleep(0.5)
            else:
                raise RuntimeError(f'PostgreSQL did not start: container={name}')
            env = PGEnv(host='127.0.0.1', port=port, tool_profile='no_knowledge')
            yield env
        finally:
            subprocess.run(['docker', 'rm', '-f', name], check=True, capture_output=True)


@pytest.fixture(scope='module', params=(0, 1))
def live_case(request, live_env):
    case = PgResourceGovernanceResourceThrottlingScenario().cases[request.param]
    injector = PgResourceGovernanceResourceThrottlingInjector()
    injector._configure(PgResourceGovernanceResourceThrottlingScenario().build_fault_plan(case)[0].config,
                        live_env)
    injector._setup_roles_and_data()
    truth = capture_query_result_truth(live_env.execute_sql(case.business_truth_sql), ordered=True)
    workload = WorkloadRunner(live_env, profiles=list(case.background_workload.profiles),
                              worker_count=case.background_workload.worker_count,
                              seed=case.background_workload.seed)
    workload.start()
    injector._stop_event = threading.Event()
    maintenance = threading.Thread(target=injector._run_maintenance_decoy)
    maintenance.start()
    try:
        yield case, truth
    finally:
        injector._stop_event.set()
        maintenance.join(timeout=8)
        assert not maintenance.is_alive()
        workload.stop()


@pytest.mark.parametrize('repair, passed', [
    ('role_timeout', True), ('database_role_timeout', True), ('boundary_timeout', True),
    ('short_timeout', True),
    ('kill_only', False), ('connection_limit_only', False), ('agent_session_only', False),
    ('wrong_role', False), ('nologin', False), ('no_select', False), ('deleted_rows', False),
    ('changed_amount', False), ('external_cancel', False), ('original_still_active', False),
])
def test_live_replay_accepts_effective_repairs_and_rejects_bypasses(live_env, live_case, repair, passed):
    case, truth = live_case
    def execute(sql):
        payload = json.loads(live_env.execute_sql(sql))
        assert payload['status'] == 'success', payload
        return payload
    execute(f'ALTER ROLE {case.report_role} RESET ALL; '
            f'ALTER ROLE {case.report_role} IN DATABASE testdb RESET ALL; '
            f'ALTER ROLE {case.report_role} LOGIN CONNECTION LIMIT -1; '
            f'GRANT SELECT ON {case.table} TO {case.report_role}; '
            f'ALTER ROLE {case.noise_roles[0]} RESET ALL; RESET statement_timeout;')
    if repair in ('role_timeout', 'boundary_timeout', 'short_timeout', 'changed_amount', 'deleted_rows'):
        timeout = '30s' if repair == 'boundary_timeout' else '100ms' if repair == 'short_timeout' else '1s'
        execute(f"ALTER ROLE {case.report_role} SET statement_timeout='{timeout}';")
    if repair == 'database_role_timeout':
        # Both catalog rows exist: this was the original Issue #28 false negative.
        execute(f"ALTER ROLE {case.report_role} SET work_mem='4MB'; "
                f"ALTER ROLE {case.report_role} IN DATABASE testdb SET statement_timeout='1s';")
    if repair == 'connection_limit_only':
        execute(f'ALTER ROLE {case.report_role} CONNECTION LIMIT 2;')
    if repair == 'agent_session_only':
        execute("SET statement_timeout='1s';")
    if repair == 'wrong_role':
        execute(f"ALTER ROLE {case.noise_roles[0]} SET statement_timeout='1s';")
    if repair == 'nologin':
        execute(f'ALTER ROLE {case.report_role} NOLOGIN;')
    if repair == 'no_select':
        execute(f'REVOKE SELECT ON {case.table} FROM {case.report_role};')
    if repair == 'deleted_rows':
        execute(f'CREATE TEMP TABLE deleted_order AS SELECT * FROM {case.table} WHERE id=42; '
                f'DELETE FROM {case.table} WHERE id=42;')
    if repair == 'changed_amount':
        execute(f'UPDATE {case.table} SET amount=amount+1 WHERE id=42;')
    context = SimpleNamespace(case_run=SimpleNamespace(case=case, env=live_env),
                              injection_evidence={'resource_throttling_business_truth': truth})
    stop = threading.Event()
    conn = None
    if repair == 'original_still_active':
        conn = psycopg2.connect(host=live_env.host, port=live_env.port, dbname=live_env.dbname,
                                user=case.report_role, password=case.role_password,
                                application_name=case.root_application_name, async_=True)
        op._wait(conn, time.monotonic()+5)
        conn.cursor().execute(case.report_query)
        time.sleep(0.1)
    def cancel_replay():
        # Independent external cancellation must not be mistaken for a DB timeout.
        with closing(psycopg2.connect(host=live_env.host, port=live_env.port, dbname=live_env.dbname,
                                     user=live_env.user, password=live_env.password)) as admin:
            admin.autocommit = True
            while not stop.wait(0.05):
                with admin.cursor() as cur:
                    cur.execute("SELECT pg_cancel_backend(pid) FROM pg_stat_activity "
                                "WHERE application_name='dba-bench-resource-op' "
                                "AND state='active' AND query LIKE 'SELECT sum((a.amount%'")
    canceller = threading.Thread(target=cancel_replay) if repair == 'external_cancel' else None
    if canceller:
        canceller.start()
    try:
        result = op.ReportReplayVerifier().verify(context)
        print(json.dumps({'case': case.case_id, 'repair': repair, **result.as_dict()}, default=str), flush=True)
        assert result.passed is passed, result
        assert result.actual['elapsed_s'] < op.OP_BUDGET_SECONDS
        assert execute("SELECT count(*) FROM pg_stat_activity "
                       "WHERE application_name='dba-bench-resource-op'")['result'] == [[0]]
    finally:
        stop.set()
        if canceller:
            canceller.join(timeout=5)
            assert not canceller.is_alive()
        if conn:
            execute(f'SELECT pg_terminate_backend({conn.get_backend_pid()},1000);')
            conn.close()
        if repair == 'deleted_rows':
            execute(f'INSERT INTO {case.table} SELECT * FROM deleted_order; DROP TABLE deleted_order;')
        if repair == 'changed_amount':
            execute(f'UPDATE {case.table} SET amount=amount-1 WHERE id=42;')
