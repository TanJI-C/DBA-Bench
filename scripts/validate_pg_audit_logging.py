"""Validate pgAudit logging and measure reference evidence on real Docker PostgreSQL.

Usage: conda run -n aiops python scripts/validate_pg_audit_logging.py CASE_ID
Outputs a reference trace and logs/calibration/pg-audit-reference-CASE_ID.json.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import time
from contextlib import closing
from datetime import datetime, timezone
from src.agents.agent import MockLLMAgent
from src.scenarios.evaluation.base import evaluation_passed
from src.scenarios.evaluation.postgres.resource_governance.audit_logging import _AUDIT_BEHAVIOR
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.postgres.resource_governance.audit_logging import PgResourceGovernanceAuditLoggingScenario
from examples.run_pg_resource_governance_audit_logging_scenario import build_env, build_full_score_mock_responses
from types import SimpleNamespace

case_id = sys.argv[1]
scenario = PgResourceGovernanceAuditLoggingScenario()
case = scenario.get_case(case_id)
env = build_env(case, 15972 if case.case_no == 0 else 15973, f'dba-issue13-pgaudit-reference-{case.case_no}')
artifact = {'case_id': case_id, 'version': 'real-pgaudit-outcome-v2', 'workload': {'worker_count': case.worker_count, 'background_profiles': [p.name for p in case.background_workload.profiles]}}

def sql_rows(query, args=None):
    with closing(env.open_workload_connection('audit-logging-reference-validation')) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(query, args)
            return cur.fetchall() if cur.description else []

class ReferenceAgent(MockLLMAgent):
    def solve(self):
        settings = sql_rows('SELECT name, setting, source FROM pg_settings ORDER BY name')
        grants = sql_rows('SELECT table_schema, table_name, grantee, privilege_type FROM information_schema.role_table_grants ORDER BY 1,2,3,4')
        start = sql_rows("SELECT (pg_stat_file('/var/log/postgresql/postgresql.log')).size")[0][0]
        artifact['sampling_start'] = datetime.now(timezone.utc).isoformat()
        time.sleep(3)
        size = sql_rows("SELECT (pg_stat_file('/var/log/postgresql/postgresql.log')).size")[0][0]
        text = sql_rows("SELECT pg_read_file('/var/log/postgresql/postgresql.log', %s, %s)", (start, size-start))[0][0]
        artifact['sampling_end'] = datetime.now(timezone.utc).isoformat()
        artifact['settings'] = settings
        artifact['role_grants'] = grants
        artifact['log_lines'] = text.splitlines()
        settings_keys = {'shared_preload_libraries', 'pgaudit.log', 'pgaudit.role', 'log_statement', 'log_min_duration_statement'}
        m_settings = sum(row[0] in settings_keys for row in settings)
        m_grants = sum(row[1] == case.table and row[2] == case.audit_role for row in grants)
        m_logs = sum(case.table in line and ('AUDIT:' in line or 'statement:' in line) for line in artifact['log_lines'])
        artifact['tool_evidence'] = {
            'execute_sql.pg_settings': {'m': m_settings, 'n': len(settings)-m_settings},
            'execute_sql.role_table_grants': {'m': m_grants, 'n': len(grants)-m_grants},
            'read_log.pg_log': {'m': m_logs, 'n': len(artifact['log_lines'])-m_logs},
        }
        report = super().solve()
        # Native logger off: pgAudit must still produce real WRITE/DDL/ROLE records.
        offset = sql_rows("SELECT (pg_stat_file('/var/log/postgresql/postgresql.log')).size")[0][0]
        marker = f'issue13_pgaudit_proof_{case.case_no}'
        sql_rows(f'UPDATE {case.table} SET amount=amount WHERE id=42 /* {marker}_write */')
        sql_rows(f'CREATE TABLE {marker} (id integer)')
        sql_rows(f'CREATE ROLE {marker}_role')
        sql_rows(f'SELECT amount FROM {case.table} WHERE id=42 /* {marker}_read */')
        sql_rows(f'DROP ROLE {marker}_role')
        sql_rows(f'DROP TABLE {marker}')
        end = sql_rows("SELECT (pg_stat_file('/var/log/postgresql/postgresql.log')).size")[0][0]
        proof = sql_rows("SELECT pg_read_file('/var/log/postgresql/postgresql.log', %s, %s)", (offset, end-offset))[0][0]
        assert ',WRITE,UPDATE,' in proof and marker+'_write' in proof, proof
        assert ',DDL,CREATE TABLE,' in proof and marker in proof, proof
        assert ',ROLE,CREATE ROLE,' in proof and marker+'_role' in proof, proof
        assert marker+'_read' not in proof, proof
        check_context = SimpleNamespace(case_run=SimpleNamespace(case=case, env=env))
        assert _AUDIT_BEHAVIOR.verify(check_context).passed
        artifact['native_logging_alternatives'] = {}
        for setting in ('none', 'mod', 'ddl'):
            sql_rows('ALTER SYSTEM SET log_statement = %s', (setting,))
            sql_rows('SELECT pg_reload_conf()')
            env.reconnect()
            check = _AUDIT_BEHAVIOR.verify(check_context)
            assert check.passed, check.as_dict()
            artifact['native_logging_alternatives'][setting] = check.as_dict()
        sql_rows("ALTER SYSTEM SET log_statement = 'all'")
        sql_rows('SELECT pg_reload_conf()')
        env.reconnect()
        assert not _AUDIT_BEHAVIOR.verify(check_context).passed, 'native read logging must fail OP'
        sql_rows("ALTER SYSTEM SET log_statement = 'none'")
        sql_rows('SELECT pg_reload_conf()')
        env.reconnect()
        sql_rows(f'GRANT SELECT ON {case.table} TO {case.audit_role}')
        assert not _AUDIT_BEHAVIOR.verify(check_context).passed, 'object SELECT grant must fail OP'
        sql_rows(f'REVOKE SELECT ON {case.table} FROM {case.audit_role}')
        assert _AUDIT_BEHAVIOR.verify(check_context).passed
        sql_rows(f'GRANT SELECT (amount) ON {case.table} TO {case.audit_role}')
        assert not _AUDIT_BEHAVIOR.verify(check_context).passed, 'column SELECT grant must fail OP'
        sql_rows(f'REVOKE SELECT (amount) ON {case.table} FROM {case.audit_role}')
        assert _AUDIT_BEHAVIOR.verify(check_context).passed
        # Session WRITE covers the business table even without an object audit role.
        sql_rows("ALTER SYSTEM SET pgaudit.role = ''")
        sql_rows('SELECT pg_reload_conf()')
        env.reconnect()
        assert _AUDIT_BEHAVIOR.verify(check_context).passed
        # PostgreSQL accepts subtractive audit masks as an equivalent configuration.
        sql_rows("ALTER SYSTEM SET pgaudit.log = 'all,-read,-function,-misc,-misc_set'")
        sql_rows('SELECT pg_reload_conf()')
        env.reconnect()
        assert _AUDIT_BEHAVIOR.verify(check_context).passed
        sql_rows('ALTER SYSTEM SET pgaudit.role = %s', (case.audit_role,))
        sql_rows("ALTER SYSTEM SET pgaudit.log = 'write,ddl,role'")
        sql_rows('SELECT pg_reload_conf()')
        env.reconnect()
        artifact['audit_proof_log'] = proof.splitlines()
        artifact['audit_proof_passed'] = True
        return report

agent = ReferenceAgent(url='mock', api_key='mock', system_prompt='You are a DBA agent.', use_native_tools=False)
agent.set_mock_responses(build_full_score_mock_responses(case))
orchestrator = Orchestrator(env=env, scenario=scenario, case=case, agent=agent, max_turns=10, run_config=OrchestratorRunConfig(fault_snapshot_mode='off'))
result = orchestrator.run()
assert evaluation_passed(result), result
artifact['evaluation'] = result
artifact['reference_run_id'] = orchestrator.case_run.run_id
# Use the same initial metric outputs the reference agent actually observed.
for event in [event for turn in orchestrator.turn_history for event in turn['results'] if event['api'] == 'query_metrics']:
    data = event['data']
    metric = data['metric']
    if f'query_metrics.{metric}' in artifact['tool_evidence']:
        continue
    if metric == 'disk_io':
        m = sum(len(series['write_mb_per_second']) for series in data['series'].values())
        n = sum(len(series['read_mb_per_second']) for series in data['series'].values())
    elif metric == 'qps':
        m = data['counts']['scalar_samples']
        n = 0
    else:
        continue
    artifact['tool_evidence'][f'query_metrics.{metric}'] = {'m': m, 'n': n}
    artifact[f'metric_{metric}'] = data
m = sum(row['m'] for row in artifact['tool_evidence'].values())
n = sum(row['n'] for row in artifact['tool_evidence'].values())
artifact['diagnostic_path'] = ['excessive log writes under active checkout traffic', 'server log contains repetitive checkout statements without corresponding WAL/table growth', 'both native and pgAudit session/object READ logging exceed required write/DDL/role coverage']
artifact['diagnostic_depth'] = 2
artifact['environmental_complexity'] = n/(m+n)
path = Path('logs/calibration') / f'pg-audit-reference-{case.case_id}.json'
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, default=str)+'\n')
print('PGAUDIT REFERENCE PASS', case_id, artifact['reference_run_id'], artifact['tool_evidence'], 'D=2', 'C=', artifact['environmental_complexity'], flush=True)
