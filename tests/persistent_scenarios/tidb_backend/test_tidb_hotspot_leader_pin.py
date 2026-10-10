"""Unit tests for the hotspot leader-pin bootstrap convergence loop."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.execution.tidb_persistent_deployment import TiDBPersistentDeploymentError
from src.persistent_scenarios.backend.tidb import assembly


def _spec():
    return SimpleNamespace(events=[
        SimpleNamespace(
            capability_id="tikv_slow_throttle",
            payload={"target": "tikv/tikv-3", "table": "shop.orders"},
        ),
    ])


class _FakeDeployment:
    def __init__(self, post_results):
        self.post_results = list(post_results)
        self.posts = []

    def pd_request(self, method, path, body=None):
        if method == "DELETE" and path == "/pd/api/v1/schedulers/balance-leader-scheduler":
            return {}
        if method == "GET" and path == "/pd/api/v1/stores":
            return {"stores": [{"store": {"address": "tikv-3:20160", "id": 4}}]}
        if method == "GET" and path.startswith("/pd/api/v1/region/id/"):
            return {"leader": {"store_id": 1}}
        if method == "POST" and path == "/pd/api/v1/operators":
            self.posts.append(dict(body))
            outcome = self.post_results.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome
        raise AssertionError(f"unexpected PD request: {method} {path}")


class _FakeEnvironment:
    def __init__(self, deployment, distributions):
        self.deployment = deployment
        self._port = SimpleNamespace(table_region_ids=lambda table: [100])
        self._distributions = list(distributions)

    def table_leader_distribution(self, table):
        return self._distributions.pop(0)


def _run(monkeypatch, environment, *, monotonic_step=None):
    sleeps: list[float] = []
    monkeypatch.setattr(assembly.time, "sleep", sleeps.append)
    if monotonic_step is not None:
        clock = {"now": 0.0}

        def monotonic():
            clock["now"] += monotonic_step
            return clock["now"]

        monkeypatch.setattr(assembly.time, "monotonic", monotonic)
    assembly._pin_orders_leaders(environment, _spec())
    return sleeps


def test_pin_tolerates_pd_rejecting_a_pending_transfer_repost(monkeypatch):
    deployment = _FakeDeployment(post_results=[{}, TiDBPersistentDeploymentError("returncode=8")])
    environment = _FakeEnvironment(deployment, distributions=[{}, {}, {"tikv/tikv-3": 2}])

    _run(monkeypatch, environment)

    assert deployment.posts == [
        {"name": "transfer-leader", "region_id": 100, "to_store_id": 4},
        {"name": "transfer-leader", "region_id": 100, "to_store_id": 4},
    ]


def test_pin_still_fails_loudly_when_the_pin_never_converges(monkeypatch):
    deployment = _FakeDeployment(post_results=[TiDBPersistentDeploymentError("returncode=8")])
    environment = _FakeEnvironment(deployment, distributions=[{} for _ in range(10)])

    with pytest.raises(TiDBPersistentDeploymentError, match="did not reach"):
        _run(monkeypatch, environment, monotonic_step=61.0)
    assert deployment.posts


def test_pin_returns_without_posting_when_target_already_holds_leaders(monkeypatch):
    deployment = _FakeDeployment(post_results=[AssertionError("must not post")])
    environment = _FakeEnvironment(deployment, distributions=[{"tikv/tikv-3": 3}])

    _run(monkeypatch, environment)
    assert deployment.posts == []
