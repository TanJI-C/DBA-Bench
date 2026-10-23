"""Deterministic unit-test DP and opt-in host admission isolation."""
import pytest

from src.execution import host_ports


@pytest.fixture(autouse=True)
def deterministic_diagnosis_matching(monkeypatch):
    """Unit tests select exact DP explicitly; semantic tests override this setting."""
    monkeypatch.setenv("AIOPS_DP_MATCH_MODE", "exact")


@pytest.fixture
def isolated_host_ports(monkeypatch, tmp_path):
    leases = []
    reserve = host_ports.reserve_host_ports

    def isolated_reserve(*args, **kwargs):
        kwargs['root'] = tmp_path / 'ports'
        lease = reserve(*args, **kwargs)
        leases.append(lease)
        return lease

    monkeypatch.delenv(host_ports.PORT_LEASE_ENV, raising=False)
    monkeypatch.setattr(host_ports, '_docker_port_owners', lambda: {})
    monkeypatch.setattr(host_ports, '_bindable', lambda port: True)
    monkeypatch.setattr(host_ports, 'reserve_host_ports', isolated_reserve)
    monkeypatch.setattr('src.execution.deployments.tidb.reserve_host_ports', isolated_reserve)
    yield
    for lease in leases:
        lease.close()
