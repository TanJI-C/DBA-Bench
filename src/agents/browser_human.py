"""A human participant drives the normal agent gateway from a browser."""
from __future__ import annotations

import json
import os
from urllib.request import Request, ProxyHandler, build_opener

from src.agents.agent import BaseAgent
from src.scenarios.evaluation.protocol import StructuredReport


class BrowserHumanAgent(BaseAgent):
    use_native_tools = True
    requires_tool_help = True

    def __init__(self, console_url: str, participant: str):
        super().__init__()
        self.console_url = console_url.rstrip('/')
        self.participant = participant
        self.session_id = None
        self.tools_schema = []
        self.tool_help = {}
        self.system_prompt = ''
        self.user_prompt = ''
        self._http = build_opener(ProxyHandler({}))

    def set_tools(self, tools):
        self.tools_schema = tools

    def set_tool_help(self, tool_help):
        self.tool_help = tool_help

    def set_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt

    def set_user_prompt(self, user_prompt):
        self.user_prompt = user_prompt

    def _request(self, path, body=None):
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode()
        request = Request(self.console_url + '/api/human' + path, data=data,
                          headers={'Content-Type': 'application/json'})
        with self._http.open(request, timeout=35) as response:
            return json.load(response)

    def solve(self):
        session = self._request('/sessions', {
            'participant': self.participant,
            'run_id': os.environ['AIOPS_RUN_ID'],
            'scenario_id': os.environ['AIOPS_SCENARIO_ID'],
            'case_id': os.environ['AIOPS_CASE_ID'],
            'system_prompt': self.system_prompt, 'user_prompt': self.user_prompt,
            'tools': self.tools_schema,
            'tool_help': self.tool_help,
        })
        self.session_id = session['id']
        while True:
            action = self._request(f'/sessions/{self.session_id}/next')['action']
            if action is None:  # Long-poll timeout, not an execution failure.
                continue
            api, args = action['api'], action['args']
            self.record_action(json.dumps(action, ensure_ascii=False), action)
            if api == 'exit':
                raise RuntimeError(f'Human participant cancelled run: session={self.session_id}')
            if api == 'submit':
                StructuredReport.from_mapping(args['report'])
                self._request(f'/sessions/{self.session_id}/result', {
                    'action_id': action['id'], 'result': {'status': 'success', 'message': '提交成功，正在评估与清理。'},
                })
                return args
            result = self.execute(api, args, thinking=action['thinking'], source='human', action_id=action['id'])
            self.action_history[-1]['result'] = result
            self._request(f'/sessions/{self.session_id}/result', {
                'action_id': action['id'], 'result': result,
            })

    def on_run_finished(self, evaluation, error):
        if self.session_id is not None:
            self._request(f'/sessions/{self.session_id}/finish', {'evaluation': evaluation, 'error': error})

    def _export_prompts(self):
        return {'system': self.system_prompt, 'user': self.user_prompt}
