"""Launch registered cases through the benchmark runner, with a human subject."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from threading import RLock, Thread
from uuid import uuid4

import yaml

from src.benchmark.api import load_manifest, plan_runs, validate_execution_plan
from src.scenarios import SCENARIO_REGISTRY
from src.visualization.human_console import SessionConflict


class HumanRuns:
    def __init__(self, root: Path, console_url: str):
        self.root = root
        self.console_url = console_url
        self.jobs = {}
        self.processes = {}
        self.lock = RLock()

    def catalog(self):
        return [{'scenario_id': r.scenario_id, 'system': r.system.value,
                 'category': r.category.value,
                 'cases': [{'case_id': c.case_id, 'title': c.title} for c in r.scenario.cases]}
                for r in SCENARIO_REGISTRY if r.entrypoint is not None]

    def list_jobs(self):
        with self.lock:
            return [dict(job) for job in self.jobs.values()]

    def cancel(self, job_id):
        with self.lock:
            process = self.processes[job_id]
            if process.poll() is not None:
                raise SessionConflict(f'运行已退出：job={job_id}')
            process.terminate()
            return {'ok': True}

    def launch(self, body):
        with self.lock:
            if any(j['state'] == 'running' for j in self.jobs.values()):
                raise SessionConflict('已有题目正在运行，请完成或终止当前运行后再开始。')
            r = next(r for r in SCENARIO_REGISTRY if r.scenario_id == body['scenario_id'] and r.entrypoint)
            r.scenario.get_case(body['case_id'])
            participant = body['participant'].strip()
            if not participant:
                raise ValueError('请输入参与者编号')
            experiment_id = 'human-' + uuid4().hex[:12]
            runtime = {'concurrency': 1, 'timeout_seconds': 14400,
                       'port_base': int(body['port_base']), 'container_prefix': experiment_id,
                       'fault_snapshot': 'off'}
            if r.system.value == 'postgresql':
                runtime['isolation'] = {'numa_policy': 'separate'}
                cpuset_cpus = body['cpuset_cpus'].strip()
                if cpuset_cpus:
                    runtime['isolation']['cpuset_cpus'] = cpuset_cpus
            manifest = {'experiment_id': experiment_id,
                        'benchmark': {'systems': [r.system.value], 'categories': [r.category.value],
                                      'scenarios': [r.scenario_id]},
                        'agents': [{'id': 'human', 'mode': 'human', 'max_turns': 1000,
                                    'settings': {'console_url': self.console_url, 'participant': participant}}],
                        'repetitions': 1, 'seeds': [int(body['seed'])], 'runtime': runtime,
                        'exclude_cells': [{'scenario': r.scenario_id, 'case': c.case_id, 'agent': 'human'}
                                          for c in r.scenario.cases if c.case_id != body['case_id']]}
            path = self.root / 'experiments/tmp' / (experiment_id + '.yaml')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False))
            command = [sys.executable, 'scripts/run_experiment.py', '--manifest', str(path)]
            if r.system.value == 'postgresql':
                plan = load_manifest(path)
                worker, = validate_execution_plan(plan, plan_runs(plan))
                runtime['isolation']['cpuset_cpus'] = worker.cpuset_cpus
                path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False))
                command = ['taskset', '-c', worker.cpuset_cpus, *command]
            checked = subprocess.run([*command, '--dry-run'], cwd=self.root, capture_output=True, text=True)
            if checked.returncode:
                raise ValueError('运行计划校验失败：' + checked.stdout + checked.stderr)
            job = {'id': experiment_id, 'state': 'running', 'scenario_id': r.scenario_id,
                   'case_id': body['case_id'], 'participant': participant, 'error': None,
                   'manifest': str(path), 'validation': checked.stdout}
            self.jobs[experiment_id] = job
            Thread(target=self._run, args=(job, command), daemon=True).start()
            return dict(job)

    def _run(self, job, command):
        log = self.root / 'artifacts/human-console' / (job['id'] + '.log')
        log.parent.mkdir(parents=True, exist_ok=True)
        try:
            with log.open('w') as handle:
                process = subprocess.Popen(command, cwd=self.root, stdout=handle, stderr=subprocess.STDOUT,
                                           env={**os.environ, 'PYTHONUNBUFFERED': '1'})
                with self.lock:
                    self.processes[job['id']] = process
                returncode = process.wait()
            with self.lock:
                job['state'] = 'completed' if returncode == 0 else 'failed'
                if returncode == 0:
                    job['error'] = None
                else:
                    details = [log.read_text()[-4000:]]
                    runs = self.root / 'artifacts/experiments' / job['id'] / 'runs'
                    details.extend(path.read_text()[-8000:] for path in runs.glob('*/attempts/*/stdout.log'))
                    job['error'] = '\n'.join(details)
        except OSError as exc:
            with self.lock:
                job.update(state='failed', error=f'无法启动 benchmark: {exc}')
