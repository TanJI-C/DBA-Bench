"""Real flock contention and descriptor inheritance, without a Docker daemon."""
import errno
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

import pytest

from src.execution import host_ports


@pytest.fixture(autouse=True)
def docker_inventory(monkeypatch):
    monkeypatch.setattr(host_ports, '_docker_port_owners', lambda: {})
    monkeypatch.delenv(host_ports.PORT_LEASE_ENV, raising=False)


def test_layout_stays_reserved_before_publish_and_during_rebuild(tmp_path):
    with host_ports.reserve_host_ports(59000, (0, 1, 5), owner='one', root=tmp_path) as first:
        # No listeners exist, including the later auxiliary service/rebuild window.
        with host_ports.reserve_host_ports(59000, (0, 1, 5), owner='two', root=tmp_path) as second:
            assert set(first.ports).isdisjoint(second.ports)
        with pytest.raises(RuntimeError, match='one'):
            host_ports.reserve_host_ports(59005, (0,), owner='three', root=tmp_path, attempts=1)
    with host_ports.reserve_host_ports(59000, (0, 1, 5), owner='next', root=tmp_path) as released:
        assert released.ports == (59000, 59001, 59005)


def test_external_listener_and_stopped_docker_mapping_are_excluded(monkeypatch, tmp_path):
    monkeypatch.setattr(host_ports, '_docker_port_owners', lambda: {59002: ['stopped']})
    with socket.socket() as listener:
        listener.bind(('0.0.0.0', 59000))
        listener.listen()
        with host_ports.reserve_host_ports(59000, (0, 1), owner='new', root=tmp_path) as lease:
            assert lease.ports == (59003, 59004)


def test_failed_partial_layout_does_not_leak_locks(tmp_path):
    with host_ports.reserve_host_ports(59002, (0,), owner='held', root=tmp_path):
        with pytest.raises(RuntimeError, match='59002'):
            host_ports.reserve_host_ports(59000, (0, 2), owner='failed', root=tmp_path, attempts=1)
        with host_ports.reserve_host_ports(59000, (0,), owner='free', root=tmp_path) as lease:
            assert lease.ports == (59000,)


def test_range_exhaustion_is_explicit(tmp_path):
    with host_ports.reserve_host_ports(59000, (0, 1), owner='held', root=tmp_path):
        with pytest.raises(RuntimeError, match='allowed_range'):
            host_ports.reserve_host_ports(59000, (0, 1), owner='fail', root=tmp_path, allowed_range=(59000, 59002))


def test_probe_does_not_hide_unexpected_error(monkeypatch):
    class BadSocket:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def bind(self, address): raise OSError(errno.EACCES, 'denied')
    monkeypatch.setattr(host_ports.socket, 'socket', lambda *args: BadSocket())
    with pytest.raises(RuntimeError, match='port=59000'):
        host_ports._bindable(59000)


def test_owned_container_mapping_can_be_reclaimed(monkeypatch, tmp_path):
    monkeypatch.setattr(host_ports, '_docker_port_owners', lambda: {59000: ['own']})
    with host_ports.reserve_host_ports(59000, (0,), owner='own', root=tmp_path, owned_containers=('own',)) as lease:
        assert lease.ports == (59000,)


def test_adoption_rejects_undeclared_ports(monkeypatch, tmp_path):
    with host_ports.reserve_host_ports(59000, (0,), owner='parent', root=tmp_path) as lease:
        monkeypatch.setenv(host_ports.PORT_LEASE_ENV, lease.process_environment)
        with pytest.raises(RuntimeError, match='missing=\\[59001\\]'):
            host_ports.claim_host_ports((59000, 59001), owner='child')


def test_child_keeps_lease_when_parent_releases(tmp_path):
    lease = host_ports.reserve_host_ports(59000, (0, 1), owner='parent', root=tmp_path)
    script = """
from src.execution.host_ports import claim_host_ports
with claim_host_ports((59000, 59001), owner='child') as lease:
    print('ready', flush=True)
    input()
"""
    child = subprocess.Popen([sys.executable, '-c', script], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, pass_fds=lease.pass_fds,
                             env={**os.environ, host_ports.PORT_LEASE_ENV: lease.process_environment})
    try:
        assert child.stdout.readline().strip() == 'ready'
        lease.close()
        with pytest.raises(RuntimeError, match='reservation failed'):
            host_ports.reserve_host_ports(59000, (0, 1), owner='contender', root=tmp_path, attempts=1)
        _, stderr = child.communicate('\n', timeout=10)
        assert child.returncode == 0, stderr
        with host_ports.reserve_host_ports(59000, (0, 1), owner='after', root=tmp_path):
            pass
    finally:
        lease.close()
        if child.poll() is None:
            child.kill()
            child.communicate()


def test_simultaneous_processes_choose_disjoint_layouts(tmp_path):
    script = """
import sys, json
from pathlib import Path
from src.execution import host_ports
host_ports._docker_port_owners = lambda: {}
input()
with host_ports.reserve_host_ports(59000, (0, 1, 5), owner=sys.argv[2], root=Path(sys.argv[1])) as lease:
    print(json.dumps(lease.ports), flush=True)
    input()
"""
    children = [subprocess.Popen([sys.executable, '-c', script, str(tmp_path), str(index)],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                for index in range(3)]
    try:
        for child in children:
            child.stdin.write('\n')
            child.stdin.flush()
        layouts = []
        for child in children:
            line = child.stdout.readline()
            assert line, child.stderr.read()
            layouts.append(set(json.loads(line)))
        assert len(set.union(*layouts)) == sum(map(len, layouts))
        for child in children:
            _, stderr = child.communicate('\n', timeout=10)
            assert child.returncode == 0, stderr
    finally:
        for child in children:
            if child.poll() is None:
                child.kill()
                child.communicate()


@pytest.mark.parametrize('stderr,code', [('Error: No such object: vanished\n', 1), ('', 0)])
def test_docker_inventory_handles_concurrent_removal(monkeypatch, stderr, code):
    responses = iter([
        subprocess.CompletedProcess([], 0, 'alive\nvanished\n', ''),
        subprocess.CompletedProcess([], code, json.dumps({'name': '/alive', 'ports': {'5432/tcp': [{'HostPort': '59000'}]}})+'\n', stderr),
    ])
    monkeypatch.undo()  # Exercise the actual inventory reader.
    monkeypatch.setattr(host_ports.subprocess, 'run', lambda *args, **kwargs: next(responses))
    assert host_ports._docker_port_owners() == {59000: ['alive']}


def test_docker_inventory_does_not_hide_daemon_failure(monkeypatch):
    monkeypatch.undo()
    responses = iter([subprocess.CompletedProcess([], 0, 'alive\n', ''),
                      subprocess.CompletedProcess([], 1, '', 'daemon disconnected')])
    monkeypatch.setattr(host_ports.subprocess, 'run', lambda *args, **kwargs: next(responses))
    with pytest.raises(RuntimeError, match='daemon disconnected'):
        host_ports._docker_port_owners()


@pytest.mark.skipif(not socket.has_ipv6, reason='IPv6 unavailable')
def test_ipv6_only_listener_is_excluded(tmp_path):
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        listener.bind(('::1', 59000))
        listener.listen()
        with host_ports.reserve_host_ports(59000, (0,), owner='new', root=tmp_path) as lease:
            assert lease.ports == (59001,)


def test_postgres_deployment_keeps_ports_until_teardown_and_can_claim_again(isolated_host_ports, monkeypatch, tmp_path):
    from src.execution.deployments.postgres import PGDockerDeployment
    deployment = PGDockerDeployment(container_name='lease-pg', port=59000)
    deployment.host_port_offsets = (0, 1, 2)
    deployment._claim_ports()
    with pytest.raises(RuntimeError, match='reservation failed'):
        host_ports.reserve_host_ports(59002, (0,), owner='other', attempts=1)
    monkeypatch.setattr('src.execution.deployments.postgres.subprocess.run',
                        lambda *args, **kwargs: subprocess.CompletedProcess([], 0, '', ''))
    deployment.teardown()
    assert deployment._port_lease is None
    deployment._claim_ports()
    assert deployment._port_lease.ports == (59000, 59001, 59002)
    deployment.teardown()


def test_tidb_lease_covers_rendered_ports_and_survives_startup(isolated_host_ports, monkeypatch, tmp_path):
    import yaml
    from src.execution.deployments.tidb import TiDBDockerDeployment
    from src.execution.tidb_runtime import tidb_runtime, TIDB_V8_1_0
    deployment = TiDBDockerDeployment(run_id='lease-tidb', port_base=59000)
    deployment.configure_runtime(tidb_runtime(release=TIDB_V8_1_0, pd_count=1, tikv_count=1, tidb_count=2,
                                               bootstrap_cache_enabled=False))
    document = yaml.safe_load(Path(deployment.compose_file).read_text())
    published = {int(mapping.split(':')[0]) for service in document['services'].values() for mapping in service.get('ports', ())}
    assert published == set(deployment._port_lease.ports)
    monkeypatch.setattr(deployment, 'preflight', lambda: None)
    monkeypatch.setattr(deployment, '_project_exists', lambda: False)
    monkeypatch.setattr(deployment.snapshots, '_prepare_persistent_state', lambda: None)
    def start():
        with pytest.raises(RuntimeError, match='reservation failed'):
            host_ports.reserve_host_ports(59004, (0,), owner='during-start', attempts=1)
    monkeypatch.setattr(deployment, '_start_cluster', start)
    deployment._env['DOCKER_ROOT_DIR'] = '/tmp'
    monkeypatch.setattr(deployment, '_run', lambda *args: '')
    deployment.deploy()
    deployment.force_teardown()
    assert deployment._port_lease is None
    with host_ports.reserve_host_ports(59000, (0, 1, 2, 3, 4), owner='after'):
        pass


def test_rpo_claims_custom_restore_endpoint(isolated_host_ports):
    from src.execution.backup_rpo import RpoPGEnv, RpoTopology
    from src.scenarios.postgres.health_check.backup_rpo_certification import PgHealthCheckBackupRpoCertificationScenario
    case = PgHealthCheckBackupRpoCertificationScenario().cases[0]
    env = RpoPGEnv(topology=RpoTopology.for_run(run_id='lease-rpo', case_id=case.case_id,
                                             primary_port=59000, restore_port=59009))
    env.configure_runtime(case.runtime)
    env.deployment._claim_ports()
    assert env.deployment._port_lease.ports == (59000, 59009)
    with pytest.raises(RuntimeError, match='reservation failed'):
        host_ports.reserve_host_ports(59009, (0,), owner='other', attempts=1)


def test_partition_entrypoint_moves_auxiliary_listeners_with_primary(monkeypatch):
    import runpy
    import sys
    entry = runpy.run_path('examples/run_pg_resource_governance_partition_cleanup_scenario.py')
    globals_ = entry['main'].__globals__
    observed = []
    monkeypatch.setattr(sys, 'argv', ['partition', '--case', 'filesystem_cleanup_pressure_simple', '--port', '59000'])
    monkeypatch.setitem(globals_, '_check_ports', lambda ports: observed.append(ports))
    monkeypatch.setitem(globals_, '_check_docker_names', lambda names: None)
    def run(args, scenario, case, *unused):
        assert scenario.build_fault_plan(case)[0].config['auxiliary_ports'] == (59001, 59002)
        return dict(DiagnosisPass=True, OutcomePass=True, SafePass=True)
    monkeypatch.setitem(globals_, 'run_mode', run)
    monkeypatch.setenv('AIOPS_PARTITION_CLEANUP_AUX_PORTS', '15862,15863')
    entry['main']()
    assert observed == [(59000, 59001, 59002)]


def test_pgbouncer_entrypoint_claims_custom_pooler_endpoint(monkeypatch, isolated_host_ports):
    import runpy
    from types import SimpleNamespace
    entry = runpy.run_path('examples/run_pg_resource_governance_pgbouncer_connection_budget_scenario.py')
    globals_ = entry['run_mode'].__globals__
    args = SimpleNamespace(seed=None, pgbouncer_port=59009, port=59000, container_name='lease-pooler',
                           fault_snapshot_mode='off', fault_snapshot_name=None, max_turns=5)
    class Orchestrator:
        def __init__(self, env, scenario, case, agent, **kwargs):
            env.configure_runtime(case.runtime)
            env.deployment._claim_ports()
            assert env.deployment._port_lease.ports == (59000, 59009)
        def run(self):
            return dict(DiagnosisPass=True, OutcomePass=True, SafePass=True)
    monkeypatch.setitem(globals_, 'Orchestrator', Orchestrator)
    entry['run_mode']('pool_partition_shortage_simple', 'mock', args)


def test_io_entrypoint_claims_custom_monitor_endpoint(monkeypatch, isolated_host_ports, tmp_path):
    import runpy
    from types import SimpleNamespace
    from src.scenarios.postgres.resource_governance.io_context_workload import PgResourceGovernanceIoContextWorkloadScenario
    entry = runpy.run_path('examples/run_pg_resource_governance_io_context_workload_scenario.py')
    init_sql = tmp_path / 'init.sql'
    init_sql.write_text('')
    workload = SimpleNamespace(data_dir=str(tmp_path), get_init_sql_path=lambda: str(init_sql))
    monkeypatch.setitem(entry['build_env'].__globals__, 'TPCDSWorkload', lambda **kwargs: workload)
    env, case, _, _ = entry['build_env'](PgResourceGovernanceIoContextWorkloadScenario().cases[0],
                                       59000, 59009, 'lease-io', 'mock')
    env.configure_runtime(case.runtime)
    env.deployment._claim_ports()
    assert env.deployment._port_lease.ports == (59000, 59009)
    assert case.monitoring_port == 59009


def test_partition_actual_http_endpoints_stay_reserved_during_restart(tmp_path):
    from types import SimpleNamespace
    from urllib.request import urlopen
    from src.scenarios.postgres.resource_governance.partition_cleanup import SIMPLE_CASE, _TelemetryServer
    with host_ports.reserve_host_ports(59000, SIMPLE_CASE.runtime.host_ports.offsets,
                                      owner='partition', root=tmp_path) as lease:
        port = lease.ports[1]
        provider = SimpleNamespace(snapshot=lambda: {'port': port})
        server = _TelemetryServer(provider, port, 'lease-proof')
        server.start()
        try:
            with urlopen(f'http://127.0.0.1:{port}/metrics', timeout=3) as response:
                assert json.load(response) == {'port': port}
        finally:
            server.stop()
        with pytest.raises(RuntimeError, match='reservation failed'):
            host_ports.reserve_host_ports(port, (0,), owner='during-restart', root=tmp_path, attempts=1)
        server = _TelemetryServer(provider, port, 'lease-proof-restart')
        server.start()
        try:
            with urlopen(f'http://127.0.0.1:{port}/metrics', timeout=3) as response:
                assert json.load(response) == {'port': port}
        finally:
            server.stop()
