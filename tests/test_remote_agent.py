"""Exercise the remote-agent HTTP relay through the real gateway and lifecycle."""
from http.server import BaseHTTPRequestHandler
import json
from threading import Thread

import pytest
import yaml

from src.agents.factory import build_benchmark_agent
from src.agents.remote_agent import RemoteAgent
from src.benchmark.manifest import load_manifest
from src.scenarios.runtime.env_gateway import EnvGateway
from src.visualization.server import ThreadedHTTPServer

REPORT = {'diagnosis': {'conditions': []}, 'outcome': {'changes': [], 'verification': []}, 'summary': 'Verified health.'}
TOOLS = [{'type': 'function', 'function': {'name': name, 'description': name, 'parameters': {'type': 'object'}}} for name in ['execute_sql', 'submit', 'exit']]
USAGE = {'provider': 'openai', 'model': 'agent-model', 'input_tokens': 120, 'output_tokens': 30, 'cached_input_tokens': 100}


class ScriptedRemote:
    """A remote agent server that replays a fixed list of actions."""

    def __init__(self, actions):
        self.actions = list(actions)
        self.sessions = []
        self.results = []
        self.finished = []

    def handler(self):
        remote = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def _reply(self, body):
                data = json.dumps(body).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _body(self):
                return json.loads(self.rfile.read(int(self.headers['Content-Length'])))

            def do_POST(self):
                body = self._body()
                if self.path == '/agent/sessions':
                    remote.sessions.append(body)
                    self._reply({'id': 's1'})
                elif self.path == '/agent/sessions/s1/result':
                    remote.results.append(body)
                    self._reply({})
                elif self.path == '/agent/sessions/s1/finish':
                    remote.finished.append(body)
                    self._reply({})
                else:
                    self.send_error(404)

            def do_GET(self):
                if self.path != '/agent/sessions/s1/next':
                    self.send_error(404)
                    return
                self._reply({'action': remote.actions.pop(0) if remote.actions else None})

        return Handler


class Env:
    def __init__(self):
        self.calls = []

    def execute_action(self, api, args):
        self.calls.append((api, args))
        return json.dumps({'status': 'success', 'columns': ['value'], 'result': [[len(self.calls)]]})


@pytest.fixture
def relay(monkeypatch):
    servers = []
    for name, value in [('RUN_ID', 'run-1'), ('SCENARIO_ID', 'demo'), ('CASE_ID', 'healthy'), ('AGENT_ID', 'external-1')]:
        monkeypatch.setenv('AIOPS_' + name, value)

    def start(actions, max_turns=30):
        remote = ScriptedRemote(actions)
        server = ThreadedHTTPServer(('127.0.0.1', 0), remote.handler())
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        servers.append((server, thread))
        agent = RemoteAgent(f'http://127.0.0.1:{server.server_port}/agent/')
        agent.set_tools(TOOLS)
        agent.set_system_prompt('You are a DBA.')
        agent.set_user_prompt('Check health.')
        agent.max_turns = max_turns
        env, history = Env(), []
        agent.init_env_gateway(EnvGateway(env, history))
        return remote, agent, env, history

    yield start
    for server, thread in servers:
        server.shutdown()
        server.server_close()
        thread.join()


def sql(action_id, query, **extra):
    return {'id': action_id, 'api': 'execute_sql', 'args': {'sql_query': query}, **extra}


def test_relays_actions_through_gateway_and_returns_submission(relay):
    remote, agent, env, history = relay([
        sql('a1', 'SELECT 1', thinking='Look', turn_id='t1', usage=[USAGE]),
        sql('a2', 'SELECT 2', turn_id='t1'),
        sql('a3', 'SELECT 3'),
        {'id': 'a4', 'api': 'submit', 'args': {'report': REPORT}},
    ], max_turns=5)

    assert agent.solve() == {'report': REPORT}

    session = remote.sessions[0]
    assert session['run_id'] == 'run-1' and session['agent_id'] == 'external-1'
    assert session['max_turns'] == 5
    assert session['system_prompt'] == 'You are a DBA.' and session['user_prompt'] == 'Check health.'
    assert [call[1]['sql_query'] for call in env.calls] == ['SELECT 1', 'SELECT 2', 'SELECT 3']
    assert [entry['api'] for entry in history] == ['execute_sql'] * 3  # submit never reaches the gateway
    assert [(r['action_id'], r['turns_used']) for r in remote.results] == [('a1', 1), ('a2', 1), ('a3', 2)]
    assert remote.results[0]['result']['result'] == [[1]]
    assert agent.model_usage_history == [{
        'provider': 'openai', 'model': 'agent-model',
        'input_tokens': 120, 'cache_input_tokens': 100, 'output_tokens': 30,
    }]
    trace = agent.export_diagnostic_trace()
    assert trace['agent_type'] == 'RemoteAgent'
    assert trace['llm_usage'][0]['cached_input_tokens'] == 100
    assert trace['llm_usage'][0]['cache_write_input_tokens'] == 0

    agent.on_run_finished({'OutcomePass': True}, None)
    assert remote.finished == [{'evaluation': {'OutcomePass': True}, 'error': None}]


def test_tool_turn_after_max_turns_fails_without_executing(relay):
    _, agent, env, _ = relay([sql('a1', 'SELECT 1'), sql('a2', 'SELECT 2')], max_turns=1)

    with pytest.raises(RuntimeError, match='after max_turns=1'):
        agent.solve()

    assert [call[1]['sql_query'] for call in env.calls] == ['SELECT 1']


def test_submit_after_max_turns_is_accepted(relay):
    _, agent, _, _ = relay([
        sql('a1', 'SELECT 1'),
        {'id': 'a2', 'api': 'submit', 'args': {'report': REPORT}},
    ], max_turns=1)

    assert agent.solve() == {'report': REPORT}


def test_exit_fails_the_run(relay):
    _, agent, env, _ = relay([{'id': 'a1', 'api': 'exit', 'args': {}}])

    with pytest.raises(RuntimeError, match='exited without submitting'):
        agent.solve()
    assert env.calls == []


@pytest.mark.parametrize('usage', [
    {'provider': 'openai', 'model': 'm', 'input_tokens': 1, 'output_tokens': 1},
    [{'provider': 'openai', 'model': 'm', 'input_tokens': -1, 'output_tokens': 1}],
    [{'provider': 'openai', 'model': 'm', 'input_tokens': '10', 'output_tokens': 1}],
    [{'model': 'm', 'input_tokens': 1, 'output_tokens': 1}],
])
def test_malformed_usage_fails_before_execution(relay, usage):
    _, agent, env, _ = relay([sql('a1', 'SELECT 1', usage=usage)])

    with pytest.raises(ValueError, match='usage'):
        agent.solve()
    assert env.calls == []


@pytest.mark.parametrize('endpoint', ['', 'localhost:9000', 'ftp://host/agent', None])
def test_rejects_non_http_endpoint(endpoint):
    with pytest.raises(ValueError, match='endpoint'):
        RemoteAgent(endpoint)


def test_factory_builds_remote_agent_from_exact_settings():
    agent = build_benchmark_agent('remote', model='remote', config_path='unused', settings={'endpoint': 'http://127.0.0.1:9000'}, seed=11)
    assert isinstance(agent, RemoteAgent)
    with pytest.raises(ValueError, match='exactly'):
        build_benchmark_agent('remote', model='remote', config_path='unused', settings={'endpoint': 'http://127.0.0.1:9000', 'participant': 'p1'}, seed=11)


def _manifest(tmp_path, agent, scenario_kind=None):
    raw = {
        'experiment_id': 'remote-contract',
        'benchmark': {'systems': ['postgresql'], 'categories': ['query_perf'], 'scenarios': ['pg_query_perf_missing_index']},
        'agents': [agent],
    }
    if scenario_kind:
        raw['benchmark']['scenario_kind'] = scenario_kind
    path = tmp_path / 'manifest.yaml'
    path.write_text(yaml.safe_dump(raw))
    return load_manifest(path)


def test_manifest_accepts_remote_agent(tmp_path):
    manifest = _manifest(tmp_path, {'id': 'external-1', 'mode': 'remote', 'max_turns': 25, 'settings': {'endpoint': 'http://127.0.0.1:9000/agent'}})
    agent = manifest.agents[0]
    assert (agent.mode, agent.max_turns, agent.settings) == ('remote', 25, {'endpoint': 'http://127.0.0.1:9000/agent'})


@pytest.mark.parametrize('agent, message', [
    ({'id': 'r', 'mode': 'remote', 'settings': {}}, 'exactly'),
    ({'id': 'r', 'mode': 'remote', 'settings': {'endpoint': 'http://h', 'extra': 1}}, 'exactly'),
    ({'id': 'r', 'mode': 'remote', 'settings': {'endpoint': 'h:9000'}}, 'endpoint'),
    ({'id': 'r', 'mode': 'remote', 'max_output_tokens': 100, 'settings': {'endpoint': 'http://h'}}, 'max_output_tokens'),
])
def test_manifest_rejects_invalid_remote_agent(tmp_path, agent, message):
    with pytest.raises(ValueError, match=message):
        _manifest(tmp_path, agent)
