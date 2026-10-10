"""Browser session transport; environment access remains in BrowserHumanAgent."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from queue import Empty, Queue
from threading import RLock
import time
from uuid import uuid4

from src.scenarios.evaluation.protocol import StructuredReport


class SessionConflict(ValueError):
    pass


class HumanConsole:
    def __init__(self, storage: Path):
        self.storage = storage
        self.sessions = {}
        self.queues = {}
        self.lock = RLock()
        if storage.exists():
            for path in storage.glob('*.json'):
                session = json.loads(path.read_text())
                if session['state'] in {'ready', 'busy', 'evaluating'}:
                    session['state'] = 'failed'
                    session['error'] = '控制台服务已重启；此会话不能恢复，请新建运行。'
                    self._save(session)
                self.sessions[session['id']] = session

    def _save(self, session):
        session['revision'] += 1
        self.storage.mkdir(parents=True, exist_ok=True)
        path = self.storage / (session['id'] + '.json')
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(session, ensure_ascii=False, indent=2))
        temporary.replace(path)

    def list_sessions(self):
        with self.lock:
            return [{k: s[k] for k in ('id', 'participant', 'run_id', 'scenario_id', 'case_id', 'state', 'created', 'revision')}
                    for s in reversed(list(self.sessions.values()))]

    def get(self, session_id):
        with self.lock:
            return deepcopy(self.sessions[session_id])

    def register(self, body):
        with self.lock:
            session_id = uuid4().hex
            session = dict(body, id=session_id, state='ready', created=time.time(), actions=[], evaluation=None, error=None, revision=0)
            self.sessions[session_id] = session
            self.queues[session_id] = Queue()
            self._save(session)
            return self.get(session_id)

    def enqueue(self, session_id, body):
        with self.lock:
            session = self.sessions[session_id]
            if session['state'] != 'ready':
                raise SessionConflict(f"会话不能执行工具：state={session['state']}, session={session_id}")
            tools = {t['function']['name'] for t in session['tools']}
            if body['api'] not in tools:
                raise ValueError(f"会话未提供工具 {body['api']!r}")
            if body['api'] == 'submit':
                StructuredReport.from_mapping(body['args']['report'])
            action = dict(body, id=uuid4().hex, started=time.time(), result=None)
            session['actions'].append(action)
            session['state'] = 'busy'
            self._save(session)
            self.queues[session_id].put(action)
            return action

    def next_action(self, session_id, timeout=25):
        with self.lock:
            queue = self.queues[session_id]
        try:
            return queue.get(timeout=timeout)
        except Empty:
            return None

    def result(self, session_id, body):
        with self.lock:
            session = self.sessions[session_id]
            action = session['actions'][-1]
            if action['id'] != body['action_id'] or session['state'] != 'busy':
                raise SessionConflict(f"结果与待执行动作不匹配：session={session_id}")
            action.update(result=body['result'], finished=time.time())
            session['state'] = 'evaluating' if action['api'] == 'submit' else 'ready'
            self._save(session)
            return {'ok': True}

    def finish(self, session_id, body):
        with self.lock:
            session = self.sessions[session_id]
            if session['state'] == 'busy' and body['error']:
                session['actions'][-1].update(result={'status': 'error', 'error': body['error']}, finished=time.time())
            session.update(body, state='failed' if body['error'] else 'completed')
            self._save(session)
            return {'ok': True}
