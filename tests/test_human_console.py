"""Exercise browser transport through the real gateway and agent lifecycle."""
from functools import partial
from pathlib import Path
from threading import Thread
import json
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from src.agents.browser_human import BrowserHumanAgent
from src.scenarios.runtime.env_gateway import EnvGateway
from src.visualization.human_console import HumanConsole, SessionConflict
from src.visualization.server import ThreadedHTTPServer, VisualizationHandler

REPORT = {'diagnosis': {'conditions': []}, 'outcome': {'changes': [], 'verification': []}, 'summary': 'Verified health.'}
TOOLS = [{'type': 'function', 'function': {'name': name, 'description': name, 'parameters': {'type': 'object'}}} for name in ['execute_sql', 'submit', 'exit']]


def test_session_state_and_restart(tmp_path):
    console = HumanConsole(tmp_path)
    session = console.register({'tools': TOOLS, 'participant': 'p1', 'run_id': 'run1', 'scenario_id': 'demo', 'case_id': 'healthy'})
    sid = session['id']
    with pytest.raises(ValueError, match='未提供工具'):
        console.enqueue(sid, {'api': 'unknown', 'args': {}})
    with pytest.raises(ValueError, match='fields mismatch'):
        console.enqueue(sid, {'api': 'submit', 'args': {'report': {}}})
    action = console.enqueue(sid, {'api': 'execute_sql', 'args': {'sql_query': 'SELECT 1'}, 'thinking': ''})
    with pytest.raises(SessionConflict):
        console.enqueue(sid, action)
    assert console.next_action(sid, timeout=0)['id'] == action['id']
    console.result(sid, {'action_id': action['id'], 'result': {'status': 'error', 'error': 'SQL failed'}})
    assert console.get(sid)['state'] == 'ready'  # Tool errors remain visible, participant can correct SQL.
    restored = HumanConsole(tmp_path)
    assert restored.get(sid)['state'] == 'failed'
    assert restored.get(sid)['actions'][0]['result']['error'] == 'SQL failed'


def test_http_browser_agent_gateway_submit_and_cleanup_notification(tmp_path, monkeypatch):
    console = HumanConsole(tmp_path / 'sessions')
    handler = partial(VisualizationHandler, artifacts_dir=str(tmp_path / 'artifacts/experiments'), human_console=console)
    server = ThreadedHTTPServer(('127.0.0.1', 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True); thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    def post(path, body, origin=None):
        request = Request(base + '/api/human' + path, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', **({'Origin': origin} if origin else {})})
        with urlopen(request) as response:
            return json.load(response)
    for name, value in [('RUN_ID', 'run-1'), ('SCENARIO_ID', 'demo'), ('CASE_ID', 'healthy')]:
        monkeypatch.setenv('AIOPS_' + name, value)
    class Env:
        def execute_action(self, api, args):
            return json.dumps({'status': 'success', 'columns': ['value'], 'result': [[42]]})
    agent = BrowserHumanAgent(base, 'p1'); agent.set_tools(TOOLS); agent.set_user_prompt('Check health.')
    actions = []; agent.init_env_gateway(EnvGateway(Env(), actions))
    submitted = []
    worker = Thread(target=lambda: submitted.append(agent.solve()), daemon=True); worker.start()
    try:
        deadline = time.monotonic() + 5
        while not console.list_sessions() and time.monotonic() < deadline:
            time.sleep(.01)
        sid = console.list_sessions()[0]['id']
        with pytest.raises(HTTPError) as exc:
            post(f'/sessions/{sid}/actions', {'api': 'exit', 'args': {}}, 'http://other-site.example')
        assert exc.value.code == 403
        post(f'/sessions/{sid}/actions', {'api': 'execute_sql', 'args': {'sql_query': 'SELECT 42'}, 'thinking': 'Verify'})
        deadline = time.monotonic() + 5
        while console.get(sid)['state'] != 'ready' and time.monotonic() < deadline:
            time.sleep(.01)
        assert actions[0]['api'] == 'execute_sql'
        assert console.get(sid)['actions'][0]['result']['result'] == [[42]]
        post(f'/sessions/{sid}/actions', {'api': 'submit', 'args': {'report': REPORT}, 'thinking': ''})
        worker.join(timeout=5)
        assert submitted == [{'report': REPORT}]
        assert console.get(sid)['state'] == 'evaluating'
        agent.on_run_finished({'DiagnosisPass': None, 'OutcomePass': True, 'SafePass': True}, None)
        assert console.get(sid)['state'] == 'completed'
        assert len(actions) == 1  # Terminal submission never goes to the environment gateway.
    finally:
        server.shutdown(); server.server_close(); thread.join()


def test_all_registered_case_commands_accept_human_agent(tmp_path):
    import yaml
    from src.scenarios import SCENARIO_REGISTRY
    from src.benchmark.manifest import load_manifest
    from src.benchmark.planner import plan_runs
    from src.benchmark.adapters.scenario import build_scenario_command
    root = Path(__file__).resolve().parents[1]
    for registration in SCENARIO_REGISTRY:
        if registration.entrypoint is None:
            continue
        raw = {'experiment_id': 'human-contract',
               'benchmark': {'systems': [registration.system.value], 'categories': [registration.category.value], 'scenarios': [registration.scenario_id]},
               'agents': [{'id': 'p1', 'mode': 'human', 'settings': {'console_url': 'http://127.0.0.1:9235', 'participant': 'p1'}}],
               'runtime': {'port_base': 25000}}
        path = tmp_path / 'manifest.yaml'; path.write_text(yaml.safe_dump(raw))
        manifest = load_manifest(path)
        for spec in plan_runs(manifest):
            command = build_scenario_command(spec, manifest, root)
            assert command[command.index('--model') + 1] == 'human', command
            assert '--max-turns' not in command, command
            mode_flag = '--mode' if '--mode' in command else '--agent'
            assert command[command.index(mode_flag) + 1] == 'llm', command
            assert command[command.index('--case') + 1] == spec.case_id


def test_failed_child_does_not_wait_for_missing_container(monkeypatch):
    from types import SimpleNamespace
    from src.benchmark import runner
    monkeypatch.setattr(runner, '_docker_inspect', lambda _: None)
    result = runner._capture_runtime_evidence({'container_name': 'not-created'}, process=SimpleNamespace(poll=lambda: 1), timeout_seconds=600)
    assert result['status'] == 'incomplete'
    assert 'not-created' in result['error']


@pytest.mark.parametrize('cpuset', ['', '   ', ' 8-11,32-35 '])
def test_pg_launcher_freezes_worker_allocation_before_pinning(tmp_path, monkeypatch, cpuset):
    from types import SimpleNamespace
    import yaml
    from src.visualization import human_runs

    validations = []
    commands = []
    started = []

    def validate(manifest, specs):
        validations.append(manifest.runtime.isolation.cpuset_cpus)
        assert len(specs) == 1
        assert specs[0].case_id == 'product_category_prefix_simple'
        return (SimpleNamespace(cpuset_cpus='8,9,10,11,32,33,34,35'),)

    def dry_run(command, **kwargs):
        commands.append(command)
        assert command[:3] == ['taskset', '-c', '8,9,10,11,32,33,34,35']
        assert command[-1] == '--dry-run'
        return SimpleNamespace(returncode=0, stdout='validated', stderr='')

    monkeypatch.setattr(human_runs, 'validate_execution_plan', validate)
    monkeypatch.setattr(human_runs.subprocess, 'run', dry_run)
    monkeypatch.setattr(human_runs, 'Thread', lambda **kwargs: SimpleNamespace(start=lambda: started.append(kwargs)))
    runs = human_runs.HumanRuns(tmp_path, 'http://127.0.0.1:9235')
    job = runs.launch({'scenario_id': 'pg_query_perf_missing_index',
                       'case_id': 'product_category_prefix_simple', 'participant': 'p1',
                       'port_base': 25432, 'seed': 11, 'cpuset_cpus': cpuset})
    assert validations == [cpuset.strip() or None]
    manifest = yaml.safe_load(Path(job['manifest']).read_text())
    assert manifest['runtime']['isolation']['cpuset_cpus'] == commands[0][2]
    assert started[0]['args'][1] == commands[0][:-1]


def test_tidb_launcher_needs_no_pg_cpu_setting(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import yaml
    from src.visualization import human_runs

    commands = []
    monkeypatch.setattr(human_runs.subprocess, 'run', lambda command, **kwargs:
                        commands.append(command) or SimpleNamespace(returncode=0, stdout='validated', stderr=''))
    monkeypatch.setattr(human_runs, 'Thread', lambda **kwargs: SimpleNamespace(start=lambda: None))
    runs = human_runs.HumanRuns(tmp_path, 'http://127.0.0.1:9235')
    job = runs.launch({'scenario_id': 'tidb_resource_governance_sql_binding',
                       'case_id': 'channel_window_binding_approval', 'participant': 'p1',
                       'port_base': 24500, 'seed': 11, 'cpuset_cpus': ''})
    assert 'taskset' not in commands[0]
    assert 'isolation' not in yaml.safe_load(Path(job['manifest']).read_text())['runtime']


def test_human_sessions_enforce_tidb_runtime_tool_scope(tmp_path):
    from types import SimpleNamespace
    from src.execution.environments.tidb import TiDBEnv
    from src.scenarios.tidb.health_check.runtime.backup_recoverability import BackupRecoverabilityEnv

    deployment = SimpleNamespace(run_id='scope-test', primary_tidb_endpoint=('127.0.0.1', 4000))
    env = TiDBEnv(deployment=deployment)
    console = HumanConsole(tmp_path)
    common = console.register({'tools': env.get_tool_schemas(), 'participant': 'p1',
                               'run_id': 'common', 'scenario_id': 'sql-binding', 'case_id': 'approval'})
    for name in BackupRecoverabilityEnv.HC04_RESTORE_TOOLS:
        with pytest.raises(ValueError, match='会话未提供工具'):
            console.enqueue(common['id'], {'api': name, 'args': {}, 'thinking': ''})
    assert common['actions'] == []
    env = BackupRecoverabilityEnv(deployment=deployment)
    env.configure_hc04_restore_runtime({})
    restore = console.register({'tools': env.get_tool_schemas(), 'participant': 'p1',
                                'run_id': 'restore', 'scenario_id': 'hc04', 'case_id': 'repair'})
    action = console.enqueue(restore['id'], {'api': 'inspect_backup_archive',
                                             'args': {'backup_id': 'approved'}, 'thinking': ''})
    assert console.next_action(restore['id'], timeout=0)['id'] == action['id']
    env.clear_hc04_restore_runtime()
