"""The runner leases implicit service ports and moves explicit ports together."""
import pytest
from types import SimpleNamespace

from src.benchmark.runner import ExperimentRunner
from src.execution import host_ports
from src.execution.specs import HostPortLayout


def test_runner_moves_entire_layout_and_passes_live_lease(monkeypatch, tmp_path):
    monkeypatch.setattr(host_ports, '_docker_port_owners', lambda: {})
    monkeypatch.setattr(host_ports, '_bindable', lambda port: True)
    command = ['python', 'scenario.py', '--primary-port', '59000', '--restore-port', '59002']
    monkeypatch.setattr('src.benchmark.runner.build_command', lambda spec, manifest: command.copy())
    reserve = host_ports.reserve_host_ports
    monkeypatch.setattr('src.benchmark.runner.reserve_host_ports', lambda *args, **kwargs: reserve(*args, root=tmp_path, **kwargs))
    spec = SimpleNamespace(run_id='run', host_ports=HostPortLayout(offsets=(0, 1, 2, 3)))
    runner = ExperimentRunner.__new__(ExperimentRunner)
    runner.manifest = object()
    runner.stopping = False

    def execute(spec, worker, actual, lease):
        assert actual[actual.index('--primary-port') + 1] == '59004'
        assert actual[actual.index('--restore-port') + 1] == '59006'
        assert lease.ports == (59004, 59005, 59006, 59007)
        with pytest.raises(RuntimeError, match='reservation failed'):
            reserve(59007, (0,), owner='other', root=tmp_path, attempts=1)
        return 'executed'

    runner._execute_reserved = execute
    with reserve(59003, (0,), owner='implicit-monitoring', root=tmp_path):
        assert runner._execute(spec) == 'executed'
    with reserve(59004, (0, 1, 2, 3), owner='after', root=tmp_path):
        pass
