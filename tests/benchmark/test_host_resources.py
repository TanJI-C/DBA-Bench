"""Exercise kernel leases with independent processes, not mocked locks."""
import json
import subprocess
import sys

import pytest

from src.benchmark.host_resources import reserve_host_resources
from src.benchmark.models import AgentSpec, BoundedScenarioRunSpec, IsolationPolicySpec
from src.database.system import DatabaseSystem
from src.execution.specs import CaseResourceSpec


def _topology(root):
    for cpu in range(2):
        path = root / f'devices/system/cpu/cpu{cpu}'
        (path / 'topology').mkdir(parents=True)
        for name, value in {'physical_package_id': '0', 'core_id': str(cpu), 'thread_siblings_list': str(cpu)}.items():
            (path / 'topology' / name).write_text(value)
        (path / 'node0').mkdir()
    path = root / 'devices/system/node/node0'
    path.mkdir(parents=True)
    (path / 'meminfo').write_text('Node 0 MemFree: 1048576 kB\nNode 0 FilePages: 0 kB\nNode 0 SReclaimable: 0 kB\nNode 0 Shmem: 0 kB\n')
    return root


def _spec(memory=128, scenario='pg_system_failure_deadlock'):
    return BoundedScenarioRunSpec(
        experiment_id='lease-test', run_id='lease-run', system=DatabaseSystem.POSTGRESQL,
        scenario_id=scenario, script='scenario.py', category='system_failure', case_id='test',
        agent=AgentSpec(id='mock', mode='mock'), repetition=1, seed=11, port=19000,
        resources=CaseResourceSpec(worker_physical_cores=1, worker_memory_mb=memory,
                                   container_cpu_limit=0.5, container_memory_mb=memory),
    )


def _reserve(tmp_path, spec=None, policy=IsolationPolicySpec('local')):
    return reserve_host_resources('lease-test', [spec or _spec()], policy, 1,
                                  root=tmp_path / 'leases', sys_root=tmp_path / 'sys', allowed_cpus={0, 1})


CHILD = '''
import json, sys
from pathlib import Path
from src.benchmark.host_resources import reserve_host_resources
from src.benchmark.models import IsolationPolicySpec
from tests.benchmark.test_host_resources import _spec
root = Path(sys.argv[1])
try:
    with reserve_host_resources('child', [_spec(int(sys.argv[2]))], IsolationPolicySpec('local'), 1,
                               root=root/'leases', sys_root=root/'sys', allowed_cpus={0,1}) as lease:
        print(json.dumps(lease.evidence), flush=True)
        sys.stdin.readline()
except RuntimeError as exc:
    print(str(exc), flush=True)
    sys.exit(7)
'''


def _child(tmp_path, memory=128):
    return subprocess.Popen([sys.executable, '-u', '-c', CHILD, str(tmp_path), str(memory)],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def test_independent_processes_get_disjoint_cores_and_reuse_released_capacity(tmp_path):
    _topology(tmp_path / 'sys')
    with _reserve(tmp_path) as first:
        child = _child(tmp_path)
        try:
            second = json.loads(child.stdout.readline())
            assert set(first.workers[0].physical_cores).isdisjoint(second['workers'][0]['physical_cores'])
            with pytest.raises(RuntimeError, match='active_reservations'):
                with _reserve(tmp_path):
                    pytest.fail('All physical cores are already reserved')
        finally:
            child.communicate('\n', timeout=10)
        assert child.returncode == 0
        with _reserve(tmp_path) as reused:
            assert reused.workers[0].physical_cores == tuple(second['workers'][0]['physical_cores'])


def test_memory_reservations_prevent_cross_process_overcommit(tmp_path):
    _topology(tmp_path / 'sys')
    with _reserve(tmp_path, _spec(768)):
        child = _child(tmp_path, 512)
        output, error = child.communicate(timeout=10)
        assert child.returncode == 7, error
        assert 'required' in output or 'memory_mb_per_worker=512' in output


@pytest.mark.parametrize('policy,spec', [(None, _spec()), (IsolationPolicySpec('local'), _spec(scenario='pg_system_failure_oom'))])
def test_unpinned_and_host_exclusive_experiments_block_other_processes(tmp_path, policy, spec):
    _topology(tmp_path / 'sys')
    with _reserve(tmp_path, spec, policy):
        child = _child(tmp_path)
        output, error = child.communicate(timeout=10)
        assert child.returncode == 7, error
        assert 'Host admission denied' in output


def test_shared_lease_prevents_exclusive_admission_and_explicit_cpuset_overlap(tmp_path):
    _topology(tmp_path / 'sys')
    with _reserve(tmp_path):
        with pytest.raises(RuntimeError, match='Host admission denied'):
            with _reserve(tmp_path, policy=None):
                pytest.fail('Exclusive admission must fail')
        with pytest.raises(RuntimeError, match='overlaps reserved'):
            with _reserve(tmp_path, policy=IsolationPolicySpec('local', '0')):
                pytest.fail('Explicit CPU band is already occupied')


def test_lease_survives_owner_exit_until_inherited_child_exits(tmp_path):
    _topology(tmp_path / 'sys')
    # The owner exits without closing its context. Its child retains both FDs.
    owner_code = '''
import os, subprocess, sys
from pathlib import Path
from tests.benchmark.test_host_resources import _reserve
context = _reserve(Path(sys.argv[1]), policy=None)
lease = context.__enter__()
child = subprocess.Popen([sys.executable, '-c', 'import sys; sys.stdin.readline()'],
                         stdin=sys.stdin, pass_fds=lease.pass_fds)
print(child.pid, flush=True)
os._exit(0)
'''
    owner = subprocess.Popen([sys.executable, '-u', '-c', owner_code, str(tmp_path)],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert int(owner.stdout.readline()) > 0
    owner.wait(timeout=10)
    try:
        with pytest.raises(RuntimeError, match='Host admission denied'):
            with _reserve(tmp_path):
                pytest.fail('Inherited child still owns lease')
    finally:
        owner.stdin.write('\n')
        owner.stdin.flush()
        owner.stdin.close()
        owner.stdout.read()  # EOF proves the child has exited and closed its inherited descriptors.
    with _reserve(tmp_path) as released:
        assert released.workers


def test_exception_releases_reservation(tmp_path):
    _topology(tmp_path / 'sys')
    with pytest.raises(ValueError, match='execution failed'):
        with _reserve(tmp_path, policy=None):
            raise ValueError('execution failed')
    with _reserve(tmp_path) as released:
        assert released.workers[0].cpuset_cpus == '0'


def test_abandoned_docker_resources_block_reuse_until_cleanup(tmp_path, monkeypatch):
    _topology(tmp_path / 'sys')
    record = tmp_path / 'run.json'
    record.write_text(json.dumps({'run_id': 'orphan-run',
                                 'command': ['python', 'demo.py', '--container-name', 'orphan-cluster'],
                                 'runtime_evidence': {}}))
    with reserve_host_resources('orphan', [_spec()], None, 1,
                               root=tmp_path / 'leases', run_records=(record,)):
        pass
    from types import SimpleNamespace
    names = ['aiopsbench-orphan-cluster-tidb-0-1']
    monkeypatch.setattr('src.benchmark.host_resources.subprocess.run',
                        lambda *args, **kwargs: SimpleNamespace(stdout='\n'.join(names)))
    with pytest.raises(RuntimeError, match='still owns Docker containers'):
        with _reserve(tmp_path):
            pytest.fail('Orphan container must keep admission blocked')
    names.clear()
    with _reserve(tmp_path) as released:
        assert released.workers
