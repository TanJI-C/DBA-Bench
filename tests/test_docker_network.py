"""Docker is the allocator and lease store; no process-local reservations."""

import hashlib
from types import SimpleNamespace

import pytest

from src.execution.docker_network import create_tidb_network


OVERLAP = "Error response from daemon: invalid pool request: Pool overlaps with other one on this address space"


def _docker(monkeypatch, *, occupied=(), create_error=None, list_error=None, existing=""):
    calls = []
    occupied = set(occupied)

    def run(command, **kwargs):
        calls.append(command)
        assert kwargs["env"] == {"DOCKER_HOST": "unix:///test/docker.sock"}
        if command[2] == "ls":
            return SimpleNamespace(returncode=bool(list_error), stdout=existing, stderr=list_error or "")
        subnet = command[command.index("--subnet") + 1]
        error = create_error or (OVERLAP if subnet in occupied else "")
        if not error:
            occupied.add(subnet)
        return SimpleNamespace(returncode=bool(error), stdout="" if error else "network-id", stderr=error)

    monkeypatch.setattr("src.execution.docker_network.subprocess.run", run)
    return calls


ENV = {"DOCKER_HOST": "unix:///test/docker.sock"}


def test_colliding_networks_claim_different_subnets(monkeypatch):
    names = {}
    for index in range(257):
        name = f"network-{index}"
        first = hashlib.sha256(name.encode()).hexdigest()[:2]
        if first in names:
            pair = (names[first], name)
            break
        names[first] = name
    calls = _docker(monkeypatch)
    first_subnet = create_tidb_network(pair[0], env=ENV)
    second_subnet = create_tidb_network(pair[1], env=ENV)
    assert first_subnet != second_subnet
    assert len([call for call in calls if call[2] == "create"]) == 3


def test_candidate_scan_wraps_and_uses_all_256_slots(monkeypatch):
    free = "10.252.0.0/24"
    calls = _docker(monkeypatch, occupied=[f"10.252.{i}.0/24" for i in range(1, 256)])
    assert create_tidb_network("wrap-test", env=ENV) == free
    candidates = [call[call.index("--subnet") + 1] for call in calls if call[2] == "create"]
    assert len(candidates) == len(set(candidates))
    assert candidates[-2] == "10.252.255.0/24"
    assert candidates[-1] == free


def test_pool_exhaustion_is_explicit(monkeypatch):
    calls = _docker(monkeypatch, create_error=OVERLAP)
    with pytest.raises(RuntimeError, match=r"pool exhausted:.*pool='10.252.0.0/16'.*attempted_subnets=256"):
        create_tidb_network("full", env=ENV)
    candidates = [call[call.index("--subnet") + 1] for call in calls if call[2] == "create"]
    assert len(set(candidates)) == 256


@pytest.mark.parametrize("error", ["permission denied", "Cannot connect to the Docker daemon", "network with name exists", "invalid subnet"])
def test_non_contention_errors_fail_immediately(monkeypatch, error):
    calls = _docker(monkeypatch, create_error=error)
    with pytest.raises(RuntimeError, match="creation failed: network='failure'.*subnet=") as raised:
        create_tidb_network("failure", env=ENV)
    assert error in str(raised.value)
    assert len(calls) == 2


def test_listing_failure_never_attempts_creation(monkeypatch):
    calls = _docker(monkeypatch, list_error="permission denied")
    with pytest.raises(RuntimeError, match="listing failed: network='failure'"):
        create_tidb_network("failure", env=ENV)
    assert len(calls) == 1


def test_existing_identity_is_not_adopted(monkeypatch):
    calls = _docker(monkeypatch, existing="owned-by-other-process")
    with pytest.raises(RuntimeError, match="identity already exists"):
        create_tidb_network("same-name", env=ENV)
    assert len(calls) == 1


def test_network_name_filter_matches_literal_identity(monkeypatch):
    calls = _docker(monkeypatch)
    create_tidb_network("network.1", env=ENV)
    assert calls[0][calls[0].index("--filter") + 1] == r"name=^network\.1$"
