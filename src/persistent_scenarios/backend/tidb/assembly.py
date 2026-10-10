"""TiDB Persistent Scenario backend assembly (integration-owned).

``build_tidb_backend`` is the TiDB mirror of ``api.build_postgres_backend``:
``api.py`` stays PG-only as the public entry, so the TiDB assembly lives in
``backend/tidb`` (integration: TiDB 装配（backend/tidb 内装配模块）).

    from src.persistent_scenarios.backend.tidb.assembly import (
        TiDBAssemblyEnvironmentProvider, build_tidb_backend,
    )

    provider = TiDBAssemblyEnvironmentProvider(data_root=...)
    backend = build_tidb_backend(spec, environment_provider=provider)
    engine = PersistentScenarioEngine(spec, backend, agent_factory, run_id=..., port=..., ...)

The engine consumes the ``PersistentScenarioBackend`` protocol
(``backend/contracts.py``): environment / events / workload / telemetry /
safety / state_facts / action_classifier + ``validate_spec``.

Reconciliation decisions registered for the coordinator:

- Instance capability packages consume ``run.env`` through the
  ``TiDBPersistentEnvironmentPort`` face while the backend environment ships
  the agent tool face; ``TiDBAssemblyEnvironment`` is the composite, so no
  package file changes.
- Instance specs declare the portfolio-contract action-class vocabulary while
  the backend classifier emits the TiDB SQL vocabulary. The classifier
  implementation lives with integration: the assembly ships the
  explicit per-instance translation (``_ACTION_CLASS_TRANSLATION``) and routes
  the vocabulary unification upstream.
- Instance 5's ``tikv-reserve`` node is a deferred (created-not-started)
  store; the NodeSpec deployment has no reserve concept. The assembly renders
  the node as ``tikv`` and implements the bounded ``scale_out_tikv`` semantics
  over public deployment attributes (``DeferredTiKVStore``); the backend REQ
  is routed.
"""

from __future__ import annotations

import csv
import io
import json
import re
import shutil
import threading
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping

import pymysql

from src.execution.tidb_persistent_deployment import (
    MYSQL_IMAGE,
    TICDC_IMAGE,
    TiDBPersistentDeployment,
    TiDBPersistentDeploymentError,
)
from src.persistent_scenarios.backend.contracts import (
    ActionClassifier,
    EventCapabilityRegistry,
    EnvironmentProvider,
    SafetyProvider,
    StateFactProvider,
    TelemetryProvider,
    WorkloadProvider,
)
from src.persistent_scenarios.backend.tidb.capabilities.cdc.verifiers import VERIFIERS as _CDC_VERIFIERS
from src.persistent_scenarios.backend.tidb.classifier import (
    ACTION_CLASS_ADMIN,
    ACTION_CLASS_COMPONENT_CONFIG,
    ACTION_CLASS_CDC_ADMIN,
    ACTION_CLASS_DDL,
    ACTION_CLASS_DML_WRITE,
    ACTION_CLASS_INSTANCE_MANAGE,
    ACTION_CLASS_KILL_SESSION,
    ACTION_CLASS_LOG_READ,
    ACTION_CLASS_METRIC_READ,
    ACTION_CLASS_READ_ONLY,
    ACTION_CLASS_STORE_MAINTENANCE,
    ACTION_CLASS_UNKNOWN,
    ACTION_CLASS_VARIABLE_SET,
    TiDBActionClassifier,
)
from src.persistent_scenarios.backend.tidb.environment import PersistentTiDBEnvironment
from src.persistent_scenarios.backend.tidb.topology import expand_topology
from src.persistent_scenarios.model.enums import DatabaseSystem, RequiredStateKind
from src.persistent_scenarios.model.spec import PersistentScenarioSpec
from src.persistent_scenarios.runtime.lifecycle import (
    ActionClassification,
    EvidenceStatus,
    IntegrityFact,
    IntegrityStatus,
    RequiredStateEvidence,
)
from src.persistent_scenarios.runtime.ledger import LedgerTerminal, LedgerView
from src.persistent_scenarios.runtime.telemetry import TelemetryRuntime
from src.persistent_scenarios.tidb.port_adapter import DeploymentPort
from src.scenarios.tidb.runtime import TIDB_V8_1_0, TiDBReleaseSpec

__all__ = [
    "DeferredTiKVStore",
    "InstanceBinding",
    "TiDBAssemblyEnvironment",
    "TiDBAssemblyEnvironmentProvider",
    "TiDBPersistentScenarioBackend",
    "build_tidb_backend",
    "register_instance_binding",
]


# ---------------------------------------------------------------------------
# Environment: agent face (backend) + trusted port face (instance packages)
# ---------------------------------------------------------------------------


class _DeploymentExecShim:
    """Adapts ``TiDBPersistentDeployment`` to the deployment names the oltp
    ``DeploymentPort`` expects: ``exec`` (-> ``exec_command``) and
    ``scale_out_tikv`` (-> the assembly's deferred-store start)."""

    def __init__(self, deployment: TiDBPersistentDeployment, deferred: "DeferredTiKVStore"):
        self._deployment = deployment
        self._deferred = deferred

    def __getattr__(self, name: str):
        return getattr(self._deployment, name)

    def exec(self, service: str, command: list[str], *, timeout: int = 30) -> str:
        # The port adapter addresses nodes by their "role/service" target form
        # (the bounded deployment face it was calibrated against); the
        # persistent deployment takes bare compose service names.
        return self._deployment.exec_command(_service_of(service), command, timeout=timeout)

    def scale_out_tikv(self, target: str) -> dict[str, Any]:
        return self._deferred.start(target)


class DeferredTiKVStore:
    """Deferred (created-not-started) TiKV store over the persistent deployment.

    Mirrors the bounded-deployment semantics the oltp package calibrated
    against: after deploy the store is removed from PD (Tombstone), its
    container is recreated but not started, and ``start`` brings it online as a
    NEW PD store.
    """

    _TOMBSTONE_TIMEOUT_SECONDS = 300.0
    _UP_TIMEOUT_SECONDS = 600.0

    def __init__(self, deployment: TiDBPersistentDeployment):
        self._deployment = deployment
        self._prepared: set[str] = set()
        self._lock = threading.Lock()

    def compose(self, *args: str, timeout: int = 120) -> str:
        return self._deployment.run_compose(*args, timeout=timeout)

    def _store_for_service(self, service: str) -> dict[str, Any] | None:
        payload = self._deployment.pd_request("GET", "/pd/api/v1/stores")
        address = f"{service}:20160"
        for store in payload.get("stores", ()):
            if store.get("store", {}).get("address") == address:
                return store
        return None

    def _wait_store_state(self, service: str, state_name: str, timeout: float) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            store = self._store_for_service(service)
            if store is not None and store.get("store", {}).get("state_name") == state_name:
                return store
            time.sleep(2.0)
        raise TiDBPersistentDeploymentError(
            f"deferred TiKV store did not reach state {state_name!r}: "
            f"service={service!r}, project={self._deployment.project_name!r}, timeout={timeout}"
        )

    def _wait_store_tombstoned(self, service: str, timeout: float) -> None:
        """Wait until the store is fully removed from PD. Tombstone-equivalent
        is disjunctive: PD reports the state as Tombstone, or drops the
        tombstoned store from the default store list entirely."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            store = self._store_for_service(service)
            if store is None or store.get("store", {}).get("state_name") == "Tombstone":
                return
            time.sleep(2.0)
        raise TiDBPersistentDeploymentError(
            f"deferred TiKV store did not reach state 'Tombstone': "
            f"service={service!r}, project={self._deployment.project_name!r}, timeout={timeout}"
        )

    def prepare(self, service: str) -> Mapping[str, Any]:
        """Take the Up store offline and recreate its container without starting it."""
        with self._lock:
            store = self._store_for_service(service)
            if store is None:
                raise TiDBPersistentDeploymentError(
                    f"deferred-store prepare found no PD store: service={service!r}, "
                    f"project={self._deployment.project_name!r}"
                )
            store_id = int(store["store"]["id"])
            self._deployment.pd_request("DELETE", f"/pd/api/v1/store/{store_id}")
            self._wait_store_tombstoned(service, self._TOMBSTONE_TIMEOUT_SECONDS)
            self._deployment.manage_service("stop", service)
            self.compose("rm", "--force", service)
            # Purge the tombstone record so PD forgets the old store identity and
            # the recreated container can register as a NEW store (the bounded
            # prepare_scale_out_slot semantics this deferred store mirrors).
            self._deployment.exec_command(
                "pd-0",
                ["/pd-ctl", "-u", "http://127.0.0.1:2379", "store", "remove-tombstone"],
                timeout=30,
            )
            self.compose("create", service)
            self._prepared.add(service)
            return {"service": service, "old_store_id": store_id, "state": "deferred"}

    def _wait_store_registered(self, service: str, timeout: float) -> dict[str, Any]:
        """Wait until the started container's store registers in PD. A freshly
        booted TiKV heartbeats its store into PD asynchronously; labeling it
        before that registration is a race (lost under host load)."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            store = self._store_for_service(service)
            if store is not None:
                return store
            time.sleep(2.0)
        raise TiDBPersistentDeploymentError(
            f"deferred TiKV store never registered in PD: service={service!r}, "
            f"project={self._deployment.project_name!r}, timeout={timeout}"
        )

    def start(self, target: str) -> dict[str, Any]:
        """Bring the deferred store online as a NEW PD store (port ``start_tikv``).

        Idempotent: the agent may lawfully start the reserved service first
        through its own instance-manage surface (the work order names the
        scale-out), in which case the store registers without this path's
        zone label — the arrival event reuses the live store, re-applies the
        label, and waits for Up instead of failing the event.
        """
        service = target.rsplit("/", 1)[-1]
        with self._lock:
            if service not in self._prepared:
                raise TiDBPersistentDeploymentError(
                    f"deferred-store start on a service that was never prepared: service={service!r}, "
                    f"prepared={sorted(self._prepared)!r}"
                )
            if self._store_for_service(service) is None:
                self.compose("start", service, timeout=300)
                self._wait_store_registered(service, self._UP_TIMEOUT_SECONDS)
            _label_tikv_store(self._deployment, service)
            store = self._wait_store_state(service, "Up", self._UP_TIMEOUT_SECONDS)
            return {"target": target, "state": "Up", "store_id": int(store["store"]["id"])}


def _tikv_zone(deployment: TiDBPersistentDeployment, service: str) -> str:
    """The fault-domain zone of one TiKV store: node order maps to zone names,
    matching the bounded-deployment topology the oltp package calibrated. The
    deferred reserve store (role ``tikv-reserve``) continues the same numbering,
    so the first reserve store lands in zone4 as the placement story expects."""
    services = deployment.topology.role_services("tikv")
    if service in services:
        index = services.index(service)
    else:
        reserve = deployment.topology.role_services("tikv-reserve")
        index = len(services) + reserve.index(service)
    return f"zone{index + 1}"


def _tikv_store_id(deployment: TiDBPersistentDeployment, service: str) -> int | None:
    address = f"{service}:20160"
    for store in deployment.pd_request("GET", "/pd/api/v1/stores").get("stores", ()):
        record = store.get("store", {})
        if record.get("address") == address:
            return int(record["id"])
    return None


def _store_zone_labels(deployment: TiDBPersistentDeployment, store_id: int) -> dict[str, str]:
    for store in deployment.pd_request("GET", "/pd/api/v1/stores").get("stores", ()):
        record = store.get("store", {})
        if int(record.get("id", -1)) == store_id:
            return {
                str(item.get("key")): str(item.get("value"))
                for item in record.get("labels", ())
            }
    raise TiDBPersistentDeploymentError(
        f"PD has no store: store_id={store_id!r}, project={deployment.project_name!r}"
    )


def _label_tikv_store(deployment: TiDBPersistentDeployment, service: str) -> None:
    """Label one TiKV store with its fault-domain zone. The persistent
    deployment renders no store labels while the oltp calibration depends on
    them: the reserve-zone story, the ``[+zone=zone4]`` placement policies and
    the hot-table leader pin."""
    store_id = _tikv_store_id(deployment, service)
    if store_id is None:
        raise TiDBPersistentDeploymentError(
            f"PD has no store to label for the service: service={service!r}, "
            f"project={deployment.project_name!r}"
        )
    zone = _tikv_zone(deployment, service)
    deployment.pd_request(
        "POST", f"/pd/api/v1/store/{store_id}/label", {"zone": zone}
    )
    labeled = _store_zone_labels(deployment, store_id)
    if labeled.get("zone") != zone:
        raise TiDBPersistentDeploymentError(
            f"TiKV store zone label did not take effect: service={service!r}, "
            f"zone={zone!r}, labels={labeled!r}"
        )


def _label_online_tikv_stores(deployment: TiDBPersistentDeployment) -> None:
    """Label every online TiKV store with its fault-domain zone; deferred
    reserve stores carry no PD store yet and are labeled when
    ``DeferredTiKVStore.start`` brings them online."""
    for service in deployment.topology.role_services("tikv"):
        if _tikv_store_id(deployment, service) is not None:
            _label_tikv_store(deployment, service)


class TiDBAssemblyEnvironment(PersistentTiDBEnvironment):
    """``PersistentTiDBEnvironment`` (agent face) plus the
    ``TiDBPersistentEnvironmentPort`` face consumed by instance capabilities,
    drivers and verifiers through ``run.env``."""

    def __init__(self, *, deployment: TiDBPersistentDeployment, deferred: DeferredTiKVStore):
        super().__init__(deployment=deployment)
        self.deferred = deferred
        self.reserve_services: tuple[str, ...] = ()
        # No default database: instance schemas differ (shop/wh/htap) and
        # every port SQL is fully qualified.
        self._port = DeploymentPort(_DeploymentExecShim(deployment, deferred), sql_port=0, database=None)

    def attach_driver(self, driver: Any) -> None:
        self._port.attach_driver(driver)

    def workload(self) -> Any:
        return self._port.workload()

    # -- cdc capability connection surface -------------------------------------

    def upstream(self):
        # The cdc capability surfaces observe live state with repeated reads on
        # one connection, so these factories must not pin a REPEATABLE-READ
        # snapshot: autocommit matches the calibrated PymysqlCdcConnections.
        return self.connect(autocommit=True)

    def downstream(self):
        return self.connect_downstream(autocommit=True)

    def control_connection(self) -> Any:
        return self._port.control_connection()

    def pd_stores(self) -> tuple[Mapping[str, Any], ...]:
        return self._port.pd_stores()

    def set_tikv_io_rate_limit(self, target: str, max_bytes_per_sec: int) -> Mapping[str, Any]:
        """Apply the TiKV I/O ceiling and verify the effective value.

        The persistent deployment mounts tikv.toml read-only, so TiKV applies
        the change to its runtime config but fails to persist it back to the
        config file and answers the write with an error status ("config
        changed, but failed to persist change"). The mechanism requires the
        effective value inside the run (the store never restarts mid-run), so
        the contract here is the GET read-back, not the write status.
        """
        body = json.dumps(
            {"storage.io-rate-limit.max-bytes-per-sec": str(int(max_bytes_per_sec))},
            separators=(",", ":"),
        )
        post = self.deployment.exec_command(
            _service_of(target),
            [
                "wget", "-qO-", "--timeout=5", "--content-on-error",
                "--method=POST", "--header=Content-Type: application/json",
                f"--body-data={body}", "http://127.0.0.1:20180/config",
            ],
            timeout=30,
        )
        observed = self.tikv_io_rate_limit(target)
        if int(observed["max-bytes-per-sec"]) != int(max_bytes_per_sec):
            raise RuntimeError(
                f"TiKV I/O limit did not take effect: target={target!r}, "
                f"requested={max_bytes_per_sec!r}, observed={observed!r}, "
                f"post_output={post.strip()[-200:]!r}"
            )
        return {"target": target, **observed}

    def tikv_io_rate_limit(self, target: str) -> Mapping[str, Any]:
        return self._port.tikv_io_rate_limit(target)

    def set_tikv_container_cpu_limit(self, target: str, cpus: float) -> Mapping[str, Any]:
        observed = self.deployment.set_node_cpu_limit(_service_of(target), cpus)
        return {"target": target, **dict(observed)}

    def tikv_container_cpu_limit(self, target: str) -> Mapping[str, Any]:
        observed = self.deployment.node_cpu_limit(_service_of(target))
        return {"target": target, **dict(observed)}

    def start_tikv(self, target: str) -> Mapping[str, Any]:
        return self.deferred.start(target)

    def pd_regions_check(self, kind: str) -> tuple[Mapping[str, Any], ...]:
        return self._port.pd_regions_check(kind)

    def table_leader_distribution(self, table: str) -> Mapping[str, int]:
        return self._port.table_leader_distribution(table)

    def backend_connection_counts(self) -> Mapping[str, int]:
        return self._port.backend_connection_counts()

    def drain_backend(self, target: str) -> Mapping[str, Any]:
        return self._port.drain_backend(target)


def _service_of(target: str) -> str:
    return target.rsplit("/", 1)[-1]


# ---------------------------------------------------------------------------
# Environment provider (integration lease; direct deployment composition)
# ---------------------------------------------------------------------------


class TiDBAssemblyEnvironmentProvider(EnvironmentProvider):
    """Creates the composite environment on the integration resource lease.

    Unlike the backend ``TiDBEnvironmentProvider`` this provider keeps run
    data under its own data root and turns instance-5 ``tikv-reserve`` nodes
    into deferred stores prepared right after deploy. The run-id prefix is the
    one the frozen ``TiDBPersistentDeployment`` module enforces
    (``tidb5-backend-``); integration runs identify themselves through the
    ``-int-`` segment (``tidb5-backend-int-...``) and their separate data root.
    """

    _RESERVE_ROLE = "tikv-reserve"
    RUN_ID_PREFIX = "tidb5-backend-"

    def __init__(
        self,
        *,
        data_root: str | Path,
        release: TiDBReleaseSpec = TIDB_V8_1_0,
        readiness_timeout_seconds: int = 1800,
        enable_monitoring: bool = False,
    ):
        self.data_root = Path(data_root)
        self.release = release
        self.readiness_timeout_seconds = readiness_timeout_seconds
        self.enable_monitoring = enable_monitoring

    def _release_images(self) -> dict[str, str]:
        if self.release.tiflash_image is None:
            raise ValueError(
                f"TiDB release has no TiFlash image, persistent deployments require one: "
                f"version={self.release.version!r}"
            )
        return {
            "pd": self.release.pd_image,
            "tikv": self.release.tikv_image,
            "tidb": self.release.tidb_image,
            "tiflash": self.release.tiflash_image,
            "ticdc": TICDC_IMAGE,
            "downstream": MYSQL_IMAGE,
        }

    def create(self, spec: PersistentScenarioSpec, run_id: str, port: int, *, time_scale: float = 1.0) -> TiDBAssemblyEnvironment:
        # The engine compresses the spec timeline itself (development_compressed);
        # the environment assembles whatever spec it is handed.
        if not run_id.startswith(self.RUN_ID_PREFIX):
            raise ValueError(
                f"TiDB integration run_id must use the lease prefix {self.RUN_ID_PREFIX!r}: "
                f"run_id={run_id!r}"
            )
        reserve_services = tuple(
            node.node_id for node in spec.environment.nodes if node.role == self._RESERVE_ROLE
        )
        if reserve_services:
            spec = self._translate_reserve_nodes(spec)
        spec = self._apply_smoke_resources(spec)
        data_dir = self.data_root / run_id
        ledgers_dir = self.data_root / "ledgers" / run_id
        for stale in (data_dir, ledgers_dir):
            if stale.exists():
                # Redeploying the same run_id is a rerun: trusted ledgers are
                # hash-chained from genesis and can never be appended to, so
                # the previous attempt's data roots are stale garbage by
                # definition (the ledger dir lives beside the deployment data
                # dirs, under <data_root>/ledgers/<run_id>).
                shutil.rmtree(stale)
        topology = expand_topology(spec, release_images=self._release_images(), data_dir=str(data_dir))
        deployment = TiDBPersistentDeployment(
            run_id=run_id,
            port_base=port,
            topology=topology,
            data_root=str(self.data_root),
            release=self.release,
            readiness_timeout_seconds=self.readiness_timeout_seconds,
            enable_monitoring=self.enable_monitoring,
        )
        environment = TiDBAssemblyEnvironment(
            deployment=deployment, deferred=DeferredTiKVStore(deployment)
        )
        environment.reserve_services = reserve_services
        return environment

    def deploy(self, environment: TiDBAssemblyEnvironment) -> None:
        environment.deploy()
        for service in environment.reserve_services:
            environment.deferred.prepare(service)

    def teardown(self, environment: TiDBAssemblyEnvironment) -> None:
        environment.teardown()

    def _translate_reserve_nodes(self, spec):
        """Map ``tikv-reserve`` nodes onto the ``tikv`` role for topology
        expansion; the node_id (hence the compose service name) is preserved
        and the deferred semantics restored by ``deploy`` + ``start_tikv``."""
        nodes = tuple(
            replace(node, role="tikv") if node.role == self._RESERVE_ROLE else node
            for node in spec.environment.nodes
        )
        return replace(spec, environment=replace(spec.environment, nodes=nodes))

    def _apply_smoke_resources(self, spec):
        """Raise TiKV/TiDB container memory to the olap-calibrated smoke
        binding (TiKV 8GB, TiDB 4GB; calibration measured the batch-load
        write storm at TiKV 4.4GB/8GB). The 2GB/1GB YAML limits fail the
        1M-row bootstrap load with TiDB v8.1 9005 "Region is unavailable",
        so this smoke profile overrides them and routes through the
        difficulty-calibration stage."""
        nodes = tuple(
            replace(
                node,
                resources=replace(
                    node.resources,
                    container_memory_mb=new_memory,
                    worker_memory_mb=max(node.resources.worker_memory_mb, new_memory),
                ),
            )
            if (new_memory := {"tikv": 8192, "tidb": 4096}.get(node.role)) is not None
            else node
            for node in spec.environment.nodes
        )
        return replace(spec, environment=replace(spec.environment, nodes=nodes))


# ---------------------------------------------------------------------------
# Action-class vocabulary translation (integration classifier wiring)
# ---------------------------------------------------------------------------

# Per-scenario translation: backend classifier action_class -> the instance
# spec's ``safety_policy.allowed_action_classes`` vocabulary. Classes absent
# from a table stay untranslated (the instance list decides authorization).
# Instance 1's control-vs-business write split follows the statement objects:
# ``ops.*`` tables are the control plane.
_ACTION_CLASS_TRANSLATION: dict[str, dict[str, str]] = {
    "tidb_oltp_hotspot_resilience": {
        ACTION_CLASS_READ_ONLY: "sql_read",
        ACTION_CLASS_VARIABLE_SET: "config_change",
        ACTION_CLASS_COMPONENT_CONFIG: "config_change",
        ACTION_CLASS_KILL_SESSION: "terminate_workload_session",
        ACTION_CLASS_DML_WRITE: "sql_write_business",
        ACTION_CLASS_DDL: "sql_write_business",
        ACTION_CLASS_ADMIN: "service_maintenance",
        ACTION_CLASS_INSTANCE_MANAGE: "service_maintenance",
        ACTION_CLASS_STORE_MAINTENANCE: "store_maintenance",
        ACTION_CLASS_LOG_READ: "sql_read",
        ACTION_CLASS_METRIC_READ: "sql_read",
    },
    "tidb_oltp_online_topology_change": {
        ACTION_CLASS_READ_ONLY: "sql_read",
        ACTION_CLASS_VARIABLE_SET: "config_change",
        ACTION_CLASS_COMPONENT_CONFIG: "config_change",
        ACTION_CLASS_KILL_SESSION: "terminate_workload_session",
        ACTION_CLASS_DML_WRITE: "sql_write_control_table",
        ACTION_CLASS_DDL: "placement_maintenance",
        ACTION_CLASS_ADMIN: "store_maintenance",
        ACTION_CLASS_INSTANCE_MANAGE: "service_maintenance",
        ACTION_CLASS_STORE_MAINTENANCE: "store_maintenance",
        ACTION_CLASS_LOG_READ: "sql_read",
        ACTION_CLASS_METRIC_READ: "sql_read",
    },
    "tidb_olap_warehouse_delivery": {
        ACTION_CLASS_READ_ONLY: "read",
        ACTION_CLASS_VARIABLE_SET: "session_control",
        ACTION_CLASS_COMPONENT_CONFIG: "maintenance",
        ACTION_CLASS_KILL_SESSION: "cancel_attempt",
        ACTION_CLASS_DML_WRITE: "queue_control",
        ACTION_CLASS_DDL: "maintenance",
        ACTION_CLASS_ADMIN: "maintenance",
        ACTION_CLASS_INSTANCE_MANAGE: "maintenance",
        ACTION_CLASS_LOG_READ: "read",
        ACTION_CLASS_METRIC_READ: "read",
    },
    "tidb_htap_tiflash_isolation": {
        ACTION_CLASS_READ_ONLY: "read",
        ACTION_CLASS_VARIABLE_SET: "session_control",
        ACTION_CLASS_COMPONENT_CONFIG: "config_control",
        ACTION_CLASS_KILL_SESSION: "cancel_attempt",
        ACTION_CLASS_DML_WRITE: "maintenance",
        ACTION_CLASS_DDL: "maintenance",
        ACTION_CLASS_ADMIN: "maintenance",
        ACTION_CLASS_INSTANCE_MANAGE: "maintenance",
        ACTION_CLASS_LOG_READ: "read",
        ACTION_CLASS_METRIC_READ: "read",
    },
    "tidb_cdc_downstream_freshness": {
        ACTION_CLASS_READ_ONLY: "sql_read",
        ACTION_CLASS_VARIABLE_SET: "sql_write",
        ACTION_CLASS_COMPONENT_CONFIG: "sql_write",
        ACTION_CLASS_KILL_SESSION: "sql_write",
        ACTION_CLASS_DML_WRITE: "sql_write",
        ACTION_CLASS_DDL: "sql_ddl",
        ACTION_CLASS_ADMIN: "sql_write",
        ACTION_CLASS_INSTANCE_MANAGE: "instance_manage",
        ACTION_CLASS_CDC_ADMIN: "changefeed_manage",
        ACTION_CLASS_LOG_READ: "sql_read",
        ACTION_CLASS_METRIC_READ: "sql_read",
    },
}

_CONTROL_VS_BUSINESS_WRITE_CLASSES = frozenset({"sql_write_control_table", "sql_write_business"})


class TranslatingActionClassifier:
    """Backend TiDB classifier plus the assembly-owned per-instance
    translation into the spec's authorized action classes.

    GRANT/REVOKE (DCL) are missing from the backend classifier vocabulary
    (routed upstream); the assembly classifies them from the statement text
    before translating, so a legitimate user-admin repair is not misread as
    ``unknown``.
    """

    _DCL_RE = None  # compiled lazily below

    def __init__(self, scenario_id: str):
        try:
            self._table = _ACTION_CLASS_TRANSLATION[scenario_id]
        except KeyError:
            raise ValueError(
                f"No action-class translation registered for the scenario: "
                f"scenario_id={scenario_id!r}, known={sorted(_ACTION_CLASS_TRANSLATION)!r}"
            ) from None
        self._classifier = TiDBActionClassifier()
        self._dcl_target = {
            "tidb_cdc_downstream_freshness": "user_admin",
        }.get(scenario_id)

    def __call__(self, api: str, args: Mapping[str, object], result: object) -> ActionClassification:
        classification = self._classifier(api, args, result)
        action_class = classification.action_class
        if action_class == ACTION_CLASS_UNKNOWN and self._dcl_target is not None:
            if self._is_dcl(classification.details):
                return ActionClassification(
                    action_class=self._dcl_target,
                    objects=classification.objects,
                    details=classification.details,
                )
        if action_class == ACTION_CLASS_UNKNOWN:
            return classification
        translated = self._table.get(action_class)
        if translated is None:
            return classification
        if translated in _CONTROL_VS_BUSINESS_WRITE_CLASSES:
            objects = tuple(str(obj) for obj in classification.objects)
            translated = (
                "sql_write_control_table"
                if any(obj.startswith("ops.") for obj in objects)
                else "sql_write_business"
            )
        return ActionClassification(
            action_class=translated,
            objects=classification.objects,
            guc_name=classification.guc_name,
            guc_value=classification.guc_value,
            details=classification.details,
        )

    @staticmethod
    def _is_dcl(details: Mapping[str, object]) -> bool:
        statements = [str(details.get("statement", ""))]
        statements.extend(str(item) for item in details.get("statements", ()) or ())
        return any(
            re.match(r"(GRANT|REVOKE)\b", statement, re.IGNORECASE) for statement in statements if statement
        )


# ---------------------------------------------------------------------------
# Event capability registry (explicit per-workload import maps)
# ---------------------------------------------------------------------------


class LazyRuntimeProvider:
    """Resolves the workload runtime the warehouse/htap capabilities share;
    the workload provider creates the runtime before any event fires."""

    def __init__(self) -> None:
        self._runtime: Any = None
        self._lock = threading.Lock()

    def attach(self, runtime: Any) -> None:
        with self._lock:
            if self._runtime is not None:
                raise RuntimeError("LazyRuntimeProvider already resolved a workload runtime")
            self._runtime = runtime

    def __call__(self) -> Any:
        if self._runtime is None:
            raise RuntimeError("workload runtime requested before the workload provider created it")
        return self._runtime


class InstanceEventRegistry(EventCapabilityRegistry):
    """``capability(capability_id)`` over one instance's registration map plus
    the core ``EventProvider`` handle services (agent_alert / cleanup /
    assert_clean delegated back to the owning capability).

    Instance packages ship two registration shapes: plain capability-instance
    tuples (hotspot/topology/cdc) and id-string tuples plus a registry class
    bound to a runtime provider (warehouse/htap). This registry normalizes
    both onto the core protocol; a thin tracking wrapper records the owning
    capability and activation context for each provider handle.
    """

    def __init__(
        self,
        capabilities: tuple = (),
        *,
        registry_factory: Callable[[Callable[[], Any]], Any] | None = None,
        runtime_provider: LazyRuntimeProvider | None = None,
    ):
        self._activation: dict[int, tuple[Any, Any]] = {}
        if registry_factory is not None:
            if runtime_provider is None:
                raise ValueError(
                    f"{registry_factory.__name__} requires the assembly runtime provider"
                )
            self._registry = registry_factory(runtime_provider)
            self._capabilities: dict[str, Any] = {}
        else:
            self._registry = None
            self._capabilities = {capability.capability_id: capability for capability in capabilities}
            if not self._capabilities:
                raise ValueError("InstanceEventRegistry requires at least one capability")

    def _track(self, capability):
        registry = self

        class _TrackedCapability:
            capability_id = capability.capability_id

            def declaration(self, event):
                return capability.declaration(event)

            def activate(self, context):
                result = capability.activate(context)
                registry._activation[id(result.handle)] = (capability, context)
                return result

            def alert(self, context, handle):
                return capability.alert(context, handle)

            def cleanup(self, handle):
                capability.cleanup(handle)

            def assert_clean(self, handle):
                return capability.assert_clean(handle)

        return _TrackedCapability()

    def _owner(self, handle):
        entry = self._activation.get(id(handle))
        if entry is None:
            raise KeyError(
                f"event provider handle was not activated through the assembly registry: "
                f"handle_type={type(handle).__name__}"
            )
        return entry

    def capability(self, capability_id: str):
        if self._registry is not None:
            return self._track(self._registry.capability(capability_id))
        try:
            return self._track(self._capabilities[capability_id])
        except KeyError:
            raise KeyError(
                f"unknown instance capability: capability_id={capability_id!r}"
            ) from None

    def agent_alert(self, handle):
        capability, context = self._owner(handle)
        return capability.alert(context, handle)

    def cleanup(self, handle) -> None:
        capability, _ = self._owner(handle)
        capability.cleanup(handle)

    def assert_clean(self, handle) -> Mapping[str, object]:
        capability, _ = self._owner(handle)
        return capability.assert_clean(handle)


# ---------------------------------------------------------------------------
# Workload provider (per-instance runtime construction)
# ---------------------------------------------------------------------------


class TiDBWorkloadProvider(WorkloadProvider):
    """Runs the instance bootstrap (business schema + seed at calibrated
    volumes), constructs the instance workload runtime and attaches it as the
    capability control surface."""

    def __init__(self, binding: "InstanceBinding", runtime_provider: LazyRuntimeProvider):
        self._binding = binding
        self._runtime_provider = runtime_provider

    def create_runtime(
        self, environment, spec, run_id, clock, *, persistent_scenario_started: float
    ):
        self._binding.bootstrap(environment, spec)
        runtime = self._binding.make_workload_entry(
            environment, spec, run_id, clock, persistent_scenario_started
        )
        environment.attach_driver(runtime)
        self._runtime_provider.attach(runtime)
        return runtime


# ---------------------------------------------------------------------------
# Telemetry / safety / state facts
# ---------------------------------------------------------------------------


class TiDBTelemetryProvider(TelemetryProvider):
    """Trusted telemetry: per-backend connection counts."""

    _INTERVAL_SECONDS = 5.0

    def create_runtime(self, environment, spec, run_id, clock, *, persistent_scenario_started: float):
        def sample() -> Mapping[str, object]:
            return {"backend_connection_counts": dict(environment.backend_connection_counts())}

        return TelemetryRuntime(
            sample=sample, interval_seconds=self._INTERVAL_SECONDS, clock=clock
        )


class TiDBSafetyProvider(SafetyProvider):
    """Safety checkpoints: ledger tamper facts (the trusted ledger reports no
    tamper through this port) plus the effective GUC snapshot consumed by the
    evaluator's durability-floor rule."""

    def capture_baseline(self, environment, spec) -> Mapping[str, object]:
        return {"guc_effective": self._effective_guc_values(environment, spec)}

    def evaluate(self, environment, baseline, action_history, checkpoint) -> Mapping[str, object]:
        return {
            "ledger_tamper_attempts": (),
            "guc_effective": dict(baseline["guc_effective"]),
        }

    @staticmethod
    def _effective_guc_values(environment, spec) -> dict[str, str]:
        names = sorted(set(spec.safety_policy.guc_floor))
        if not names:
            return {}
        connection = environment.connect()
        try:
            with connection.cursor() as cursor:
                values = {}
                for name in names:
                    cursor.execute("SHOW GLOBAL VARIABLES LIKE %s", (name,))
                    row = cursor.fetchone()
                    if row is not None:
                        values[name] = str(row[1])
                return values
        finally:
            connection.close()


def verifier_verdict_failed(result: Mapping[str, Any]) -> bool:
    """Translate one instance verifier's result onto the evaluation verdict.

    The instance packages return their verdict under the convention their
    contract states: a ``failures`` list (hotspot/topology), a top-level
    ``passed`` bool (cdc), a ``satisfied`` bool (control-plane checks), or the
    ``incorrect_business_ids``/``incorrect_job_ids`` verdict-id lists the SLO
    evaluator consumes from FAILED result-truth facts (warehouse/tiflash).
    The assembly reads all of them at the top level so a verifier can never
    fail silently because its convention was not the one sampled.
    """
    return bool(
        result.get("failures")
        or result.get("incorrect_business_ids")
        or result.get("incorrect_job_ids")
        or result.get("passed") is False
        or result.get("satisfied") is False
    )


@dataclass(frozen=True)
class VerifierBinding:
    """One instance verifier normalized onto the assembly call convention
    ``call(environment, connection, views, params)``; ``views`` are the
    ``LedgerView``s of ``ledger_ids`` in the runtime ledger mapping."""

    ledger_ids: tuple[str, ...]
    call: Callable[[Any, Any, tuple, Mapping], Mapping[str, Any]]


class TiDBStateFactProvider(StateFactProvider):
    """Final-horizon trusted sampling: executes the instance-registered
    integrity and required-state verifiers over fresh trusted connections and
    the sealed workload ledgers."""

    def __init__(self, binding: "InstanceBinding", runtime_provider: LazyRuntimeProvider):
        self._binding = binding
        self._runtime_provider = runtime_provider

    def capture_integrity_facts(
        self, environment, spec: PersistentScenarioSpec, *, scoring_start_epoch: float | None = None
    ) -> tuple[IntegrityFact, ...]:
        ledgers = self._runtime_provider().ledgers()
        facts: list[IntegrityFact] = []
        for check in spec.integrity_checks:
            binding = self._binding.integrity_binding(check.verifier_id)
            result = self._run_verifier(binding, environment, ledgers, check.params)
            facts.append(IntegrityFact(
                check_id=check.check_id,
                kind=check.verifier_id,
                status=IntegrityStatus.FAILED if verifier_verdict_failed(result) else IntegrityStatus.PASSED,
                details=result,
            ))
        return tuple(facts)

    def capture_required_state_evidence(
        self, environment, spec: PersistentScenarioSpec, *, scoring_start_epoch: float | None = None
    ) -> tuple[RequiredStateEvidence, ...]:
        ledgers = self._runtime_provider().ledgers()
        captured_at = time.monotonic()
        evidence: list[RequiredStateEvidence] = []
        for check in spec.required_state:
            if check.kind is RequiredStateKind.CONTINUITY:
                facts = self._continuity_facts(ledgers, check.service_id, float(check.window_seconds))
            elif check.kind is RequiredStateKind.VERIFIER:
                binding = self._binding.required_state_binding(check.verifier_id)
                result = self._run_verifier(binding, environment, ledgers, check.params)
                facts = {"passed": not verifier_verdict_failed(result), **result}
            elif check.kind is RequiredStateKind.GUC_EFFECTIVE:
                facts = self._guc_effective_facts(environment, check)
            else:
                raise ValueError(
                    f"TiDB state facts cannot sample the required-state kind: "
                    f"check_id={check.check_id!r}, kind={check.kind!r}"
                )
            evidence.append(RequiredStateEvidence(
                check_id=check.check_id,
                status=EvidenceStatus.CAPTURED,
                facts=facts,
                captured_at_monotonic=captured_at,
            ))
        return tuple(evidence)

    @staticmethod
    def _run_verifier(binding: VerifierBinding, environment, ledgers, params) -> Mapping[str, Any]:
        views = tuple(LedgerView(ledgers[ledger_id]) for ledger_id in binding.ledger_ids)
        connection = environment.control_connection()
        try:
            return dict(binding.call(environment, connection, views, params))
        finally:
            connection.close()

    @staticmethod
    def _continuity_facts(ledgers, service_id: str, window_seconds: float) -> dict[str, object]:
        """Business continuation over the final window on the trusted ledger.

        The window ends at the service's last planned transaction - the last
        window that actually contains planned input - because the drain tail
        between the frozen input cutoff and the scoring end plans nothing.
        The denominator counts every transaction planned inside the window and
        the numerator counts how many of them completed, so lost work lowers
        the fraction instead of shrinking the denominator.
        """
        records = []
        for ledger_id, ledger in ledgers.items():
            for record in LedgerView(ledger).logical_transactions():
                if record.service_id == service_id:
                    records.append(record)
        if not records:
            raise ValueError(
                f"continuity check found no ledger transactions for the service: "
                f"service_id={service_id!r}, ledgers={sorted(ledgers)!r}"
            )
        window_start = max(record.planned_at_monotonic for record in records) - window_seconds
        planned = [record for record in records if record.planned_at_monotonic >= window_start]
        completed = sum(1 for record in planned if record.terminal is LedgerTerminal.COMPLETED)
        return {"completed": completed, "denominator": len(planned)}

    @staticmethod
    def _guc_effective_facts(environment, check) -> dict[str, object]:
        """Fresh-connection observation of the declared scope (REQ-001 shape);
        TiDB has no pending-restart concept."""
        connection = environment.connect()
        try:
            with connection.cursor() as cursor:
                if check.scope == "global":
                    cursor.execute("SHOW GLOBAL VARIABLES LIKE %s", (check.guc_name,))
                else:
                    cursor.execute("SHOW VARIABLES LIKE %s", (check.guc_name,))
                rows = cursor.fetchall()
        finally:
            connection.close()
        if not rows:
            raise ValueError(
                f"guc_effective check observed no variable: check_id={check.check_id!r}, "
                f"guc_name={check.guc_name!r}, scope={check.scope!r}"
            )
        return {
            "value": str(rows[0][1]),
            "fresh_connection": True,
            "scope": check.scope,
            **({"scope_name": check.scope_name} if check.scope_name is not None else {}),
            "pending_restart": False,
        }


# ---------------------------------------------------------------------------
# Backend bundle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TiDBPersistentScenarioBackend:
    """The ``PersistentScenarioBackend`` bundle for one TiDB instance spec."""

    system: DatabaseSystem
    environment: EnvironmentProvider
    events: EventCapabilityRegistry
    workload: WorkloadProvider
    telemetry: TelemetryProvider
    safety: SafetyProvider
    state_facts: StateFactProvider
    action_classifier: ActionClassifier
    _registered_scenario_ids: tuple[str, ...]

    def validate_spec(self, spec: PersistentScenarioSpec) -> None:
        if spec.system is not DatabaseSystem.TIDB:
            raise ValueError(
                f"TiDB backend requires a tidb spec: scenario_id={spec.scenario_id!r}, "
                f"system={spec.system!r}"
            )
        if spec.scenario_id not in self._registered_scenario_ids:
            raise ValueError(
                f"TiDB backend assembly has no instance binding for the scenario: "
                f"scenario_id={spec.scenario_id!r}, known={sorted(self._registered_scenario_ids)!r}"
            )
        policy_classes = set(spec.safety_policy.allowed_action_classes)
        translated = set(_ACTION_CLASS_TRANSLATION[spec.scenario_id].values())
        unmatched = translated - policy_classes
        if unmatched:
            raise ValueError(
                f"action-class translation targets classes the spec does not authorize: "
                f"scenario_id={spec.scenario_id!r}, unmatched={sorted(unmatched)!r}"
            )
        for event in spec.events:
            self.events.capability(event.capability_id)  # KeyError on an unknown id


# ---------------------------------------------------------------------------
# Instance bindings (explicit per-workload registration maps)
# ---------------------------------------------------------------------------


def _hotspot_connection_source(environment):
    class _Source:
        def connect(self, policy):
            return environment._port.connect_sql(None, read_timeout_ms=policy.request_timeout_ms)

        def connect_control(self):
            return environment._port.connect_sql(None, read_timeout_ms=10000)

        def connect_reconcile(self):
            return environment._port.connect_sql(None, read_timeout_ms=10000)

        def connection_counts(self):
            return environment.backend_connection_counts()

        def apply_policy(self, policy):
            return None

    return _Source()


def _make_hotspot_workload(environment, spec, run_id, clock, scoring_origin, ledgers_dir: Path):
    from src.persistent_scenarios.runtime.ledger import TrustedLedger
    from src.persistent_scenarios.tidb.hotspot.driver import (
        DriverConfig,
        HotspotWorkloadDriver,
        TrafficPlan,
        TrafficTier,
    )
    from src.persistent_scenarios.tidb.hotspot.schema import FLASH_SALE_SKU, PROMO_GROUP_A, PROMO_GROUP_B

    objective = next(service for service in spec.services if service.service_id == "trade")
    return HotspotWorkloadDriver(
        service_id="trade",
        ledger=TrustedLedger("trade", ledgers_dir / f"{run_id}-trade.jsonl"),
        clock=clock,
        connection_source=_hotspot_connection_source(environment),
        plan=TrafficPlan(tiers=(
            TrafficTier("normal", 2.0, 3.0, PROMO_GROUP_A, FLASH_SALE_SKU, 0.5),
            TrafficTier("promo_a", 8.0, 4.0, PROMO_GROUP_A, FLASH_SALE_SKU, 0.5),
            TrafficTier("promo_b", 8.0, 4.0, PROMO_GROUP_B, None, 0.0),
        )),
        config=DriverConfig(
            pool_size=6,
            deadline_seconds=objective.deadline_seconds,
            control_poll_seconds=1.0,
            integrity_probe_interval_seconds=20.0,
        ),
        run_id=run_id,
        scoring_origin=scoring_origin + spec.warmup_seconds,
        input_stop_seconds=float(spec.input_stop_seconds),
        normal_sku_count=20,
    )


def _make_topology_workload(environment, spec, run_id, clock, scoring_origin, ledgers_dir: Path):
    from src.persistent_scenarios.runtime.ledger import TrustedLedger
    from src.persistent_scenarios.tidb.hotspot.driver import DriverConfig, TrafficPlan, TrafficTier
    from src.persistent_scenarios.tidb.hotspot.schema import FLASH_SALE_SKU, PROMO_GROUP_A
    from src.persistent_scenarios.tidb.topology.driver import TopologyWorkloadDriver

    objective = next(service for service in spec.services if service.service_id == "trade")
    return TopologyWorkloadDriver(
        maintenance_ledger=TrustedLedger("maintenance", ledgers_dir / f"{run_id}-maintenance.jsonl"),
        maintenance_service_id="maintenance",
        environment_port=environment,
        service_id="trade",
        ledger=TrustedLedger("trade", ledgers_dir / f"{run_id}-trade.jsonl"),
        clock=clock,
        connection_source=_hotspot_connection_source(environment),
        plan=TrafficPlan(tiers=(
            TrafficTier("normal", 2.0, 3.0, PROMO_GROUP_A, FLASH_SALE_SKU, 0.5),
            TrafficTier("promo_peak", 6.0, 4.0, PROMO_GROUP_A, FLASH_SALE_SKU, 0.5),
        )),
        config=DriverConfig(
            pool_size=6,
            deadline_seconds=objective.deadline_seconds,
            control_poll_seconds=1.0,
            integrity_probe_interval_seconds=20.0,
        ),
        run_id=run_id,
        scoring_origin=scoring_origin + spec.warmup_seconds,
        input_stop_seconds=float(spec.input_stop_seconds),
        normal_sku_count=20,
    )


def _make_warehouse_workload(environment, spec, run_id, clock, scoring_origin, ledgers_dir: Path):
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.runtime import (
        SERVICE_IDS,
        WarehouseDeliveryRuntime,
    )
    from src.persistent_scenarios.runtime.ledger import TrustedLedger

    ledgers = {
        service_id: TrustedLedger(f"{run_id}:{service_id}", ledgers_dir / f"{run_id}-{service_id}.jsonl")
        for service_id in SERVICE_IDS
    }
    return WarehouseDeliveryRuntime(
        connection_factory=lambda _name=None: environment.connect(),
        clock=clock,
        run_id=run_id,
        ledgers=ledgers,
        input_end_monotonic=scoring_origin + spec.warmup_seconds + float(spec.input_stop_seconds),
    )


def _make_htap_workload(environment, spec, run_id, clock, scoring_origin, ledgers_dir: Path):
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime import (
        SERVICE_IDS,
        HtapIsolationRuntime,
    )
    from src.persistent_scenarios.runtime.ledger import TrustedLedger

    ledgers = {
        service_id: TrustedLedger(f"{run_id}:{service_id}", ledgers_dir / f"{run_id}-{service_id}.jsonl")
        for service_id in SERVICE_IDS
    }
    return HtapIsolationRuntime(
        connection_factory=lambda _name=None: environment.connect(),
        clock=clock,
        run_id=run_id,
        ledgers=ledgers,
        input_end_monotonic=scoring_origin + spec.warmup_seconds + float(spec.input_stop_seconds),
        tiflash_container=environment.deployment.service_container_id(
            environment.deployment.topology.role_services("tiflash")[0]
        ),
    )


def _make_cdc_workload(environment, spec, run_id, clock, scoring_origin, ledgers_dir: Path):
    from src.persistent_scenarios.backend.tidb.capabilities.cdc.connections import PymysqlCdcConnections
    from src.persistent_scenarios.backend.tidb.capabilities.cdc.driver import CdcFreshnessWorkloadRuntime

    upstream_port = environment.deployment.ports.tidb_sql[
        environment.deployment.topology.role_services("tidb")[0]
    ]
    downstream_service = environment.deployment.topology.role_services("downstream")[0]
    downstream_host, downstream_port = environment.deployment.downstream_sql_endpoint(downstream_service)
    return CdcFreshnessWorkloadRuntime(
        environment=environment,
        spec=spec,
        run_id=run_id,
        clock=clock,
        factories=PymysqlCdcConnections(
            upstream_host="127.0.0.1", upstream_port=upstream_port,
            downstream_host=downstream_host, downstream_port=downstream_port,
        ),
        ledger_dir=ledgers_dir,
        log=lambda message: print(f"[{run_id}] cdc-driver: {message}", flush=True),
    )


def _bootstrap_sql(environment, statements, *, autocommit_connection: bool = False):
    connection = environment.connect()
    try:
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
        connection.commit()
    finally:
        connection.close()


def _load_data_csv(environment, csv_path: Path, table: str, columns: str) -> None:
    port = environment.deployment.ports.tidb_sql[
        environment.deployment.topology.role_services("tidb")[0]
    ]
    connection = pymysql.connect(
        host="127.0.0.1", port=port, user="root", password="", database="test",
        autocommit=False, local_infile=True, connect_timeout=10,
        read_timeout=1800, write_timeout=1800,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"LOAD DATA LOCAL INFILE '{csv_path}' INTO TABLE {table} "
                f"FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\n' ({columns})"
            )
        connection.commit()
    finally:
        connection.close()


def _bootstrap_hotspot(environment, spec) -> None:
    from src.persistent_scenarios.tidb.hotspot.schema import (
        DDL_STATEMENTS,
        initial_client_config_statement,
        seed_inventory_statements,
    )

    connection = environment.connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS shop")
            cursor.execute("CREATE DATABASE IF NOT EXISTS ops")
            for statement in DDL_STATEMENTS:
                cursor.execute(statement)
            cursor.execute("SELECT COUNT(*) FROM shop.inventory")
            if cursor.fetchone()[0] == 0:
                for statement in seed_inventory_statements():
                    cursor.execute(statement)
                cursor.execute(initial_client_config_statement())
            # The timeline's throttle event declares its store target
            # statically and the capability proves the target carries leader
            # regions of the hot table before slowing it. Split the orders
            # row-key space so the table spans regions from the start; at
            # compressed scale the run is shorter than the PD idle window
            # that would otherwise merge empty regions back, so the merge
            # checker is disabled to keep that precondition stable
            # (disclosed smoke-scale deviation, reversed at teardown with
            # the cluster).
            cursor.execute(
                "SPLIT TABLE shop.orders BETWEEN ('a') AND ('zzzzzzzz') REGIONS 9"
            )
        connection.commit()
    finally:
        connection.close()
    environment.deployment.pd_request(
        "POST", "/pd/api/v1/config",
        {"max-merge-region-size": 0, "max-merge-region-keys": 0},
    )
    schedule = environment.deployment.pd_request("GET", "/pd/api/v1/config")["schedule"]
    if schedule["max-merge-region-size"] != 0 or schedule["max-merge-region-keys"] != 0:
        raise TiDBPersistentDeploymentError(
            f"PD region merge could not be disabled: "
            f"max-merge-region-size={schedule['max-merge-region-size']!r}, "
            f"max-merge-region-keys={schedule['max-merge-region-keys']!r}"
        )
    _label_online_tikv_stores(environment.deployment)
    _pin_orders_leaders(environment, spec)


def _throttle_target(spec) -> str | None:
    """The store target the timeline's tikv_slow_throttle event declares
    (None when the instance declares no such event)."""
    for event in spec.events:
        if event.capability_id == "tikv_slow_throttle":
            return str(event.payload["target"])
    return None


def _pin_orders_leaders(environment, spec) -> None:
    """Deterministically place one leader region of the hot table on the store
    the declared throttle event targets.

    PD leader balance drifts leaders between bootstrap and the event (the
    precondition was observed lost twice at compressed scale), so the run
    pins one region with a one-shot PD transfer-leader operator and holds the
    placement by disabling the balance-leader scheduler for the run — both
    disclosed smoke-scale stabilizations; the cluster is torn down after the
    run. The PD placement-rules engine was evaluated and rejected: rule
    convergence latency is unbounded and its operator gate contradicts the
    declared rule.
    """
    target = _throttle_target(spec)
    if target is None:
        return
    table = str(next(
        event.payload["table"] for event in spec.events
        if event.capability_id == "tikv_slow_throttle"
    ))
    deployment = environment.deployment
    service = _service_of(target)
    store_id = _tikv_store_id(deployment, service)
    if store_id is None:
        raise TiDBPersistentDeploymentError(
            f"throttle target store is not registered in PD: target={target!r}, "
            f"table={table!r}"
        )
    deployment.pd_request("DELETE", "/pd/api/v1/schedulers/balance-leader-scheduler")
    deadline = time.monotonic() + 120.0
    distribution: Mapping[str, int] = {}
    while time.monotonic() < deadline:
        distribution = environment.table_leader_distribution(table)
        if int(distribution.get(target, 0)) > 0:
            return
        for region_id in environment._port.table_region_ids(table):
            record = deployment.pd_request("GET", f"/pd/api/v1/region/id/{region_id}")
            leader_store = record.get("leader", {}).get("store_id")
            if leader_store is not None and int(leader_store) != store_id:
                try:
                    deployment.pd_request("POST", "/pd/api/v1/operators", {
                        "name": "transfer-leader",
                        "region_id": int(region_id),
                        "to_store_id": int(store_id),
                    })
                except TiDBPersistentDeploymentError:
                    # PD rejects a re-POST while the previous transfer operator is
                    # still pending (the leader move can outlast one loop tick);
                    # the deadline loop keeps sampling the real distribution and
                    # still fails loudly if the pin never converges.
                    pass
                break
        time.sleep(2.0)
    raise TiDBPersistentDeploymentError(
        f"hot-table leaders did not reach the declared throttle target before "
        f"the bootstrap deadline: target={target!r}, table={table!r}, "
        f"distribution={dict(distribution)!r}"
    )


def _bootstrap_topology(environment, spec) -> None:
    from src.persistent_scenarios.tidb.topology.schema import (
        DDL_STATEMENTS,
        MAINTENANCE_TRACKING_SEED,
    )

    _bootstrap_hotspot(environment, spec)
    _bootstrap_sql(environment, (*DDL_STATEMENTS, MAINTENANCE_TRACKING_SEED))


def _seed_warehouse_registry(cursor) -> None:
    """Insert the batch registry rows and apply the report hold.

    The hold preset ships inside the schema's provision_statements, which run
    BEFORE this seed inserts the registry rows, so the batch-A gate
    (batch A ships with its report deliveries gated) is applied
    here against the rows that now exist - the deployed hold must be real, not
    a no-op against an empty table.
    """
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.schema import (
        BATCH_A_ID,
        BATCH_REGISTRY,
    )

    cursor.execute(
        "INSERT INTO wh.batch_registry (batch_id, skew_note, analyze_after_ingest) "
        "VALUES (1, 'region_skew_east', TRUE), (2, 'region_skew_south', TRUE), "
        "(3, 'backfill_wave_overlap', TRUE)"
    )
    cursor.execute(f"UPDATE {BATCH_REGISTRY} SET reports_held = TRUE WHERE batch_id = {BATCH_A_ID};")


def _bootstrap_warehouse(environment, spec) -> None:
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.datagen import generate_rows
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.schema import (
        HISTORY_BATCH_ID,
        provision_statements,
    )

    dimension_statements = [
        "INSERT IGNORE INTO wh.dim_region VALUES (%s, %s, %s)"
    ]
    connection = environment.connect()
    try:
        with connection.cursor() as cursor:
            for statement in provision_statements():
                cursor.execute(statement)
            for region_id in range(1, 13):
                group = "east" if region_id <= 4 else ("south" if region_id <= 8 else "north")
                cursor.execute(
                    dimension_statements[0], (region_id, f"region-{region_id:02d}", group)
                )
            # No smoke-reset here: the assembly deploys a fresh cluster, so
            # the tables hold nothing to reset, and an immediate TRUNCATE
            # after CREATE only adds DDL churn ahead of the bulk load
            # (observed TiDB v8.1 9005 "Region is unavailable" in that
            # window).
            _seed_warehouse_registry(cursor)
        connection.commit()
    finally:
        connection.close()
    columns = ("order_id, batch_id, region_id, warehouse_id, item_id, channel, quantity, "
               "unit_price, unit_cost, amount, order_ts")
    history_csv = _write_rows_csv(environment, generate_rows(HISTORY_BATCH_ID), "history")
    _load_data_csv(environment, history_csv, "wh.orders", columns)
    for batch_id, stage_table in ((1, "wh.stage_batch_a"), (2, "wh.stage_batch_b")):
        stage_csv = _write_rows_csv(environment, generate_rows(batch_id), f"stage_{batch_id}")
        _load_data_csv(environment, stage_csv, stage_table, columns)


def _write_rows_csv(environment, rows, name: str) -> Path:
    csv_path = Path(environment.deployment.data_dir) / f"{name}.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        # The LOAD statements declare LINES TERMINATED BY '\n'; csv.writer's
        # default \r\n terminator would corrupt the trailing field.
        writer = csv.writer(handle, lineterminator="\n")
        for row in rows:
            writer.writerow(row)
    return csv_path


def _bootstrap_htap(environment, spec) -> None:
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash.schema import (
        HISTORY_ROW_COUNT,
        ORDERS_TABLE,
        provision_statements,
    )

    _bootstrap_sql(environment, provision_statements())
    csv_path = Path(environment.deployment.data_dir) / "htap_history.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for order_id in range(1, HISTORY_ROW_COUNT + 1):
            writer.writerow((
                order_id, order_id % 10_000, order_id % 500, (order_id % 8) + 1,
                "100.00", "paid", "2026-01-01 00:00:00",
            ))
    _load_data_csv(
        environment, csv_path, ORDERS_TABLE,
        "order_id, user_id, item_id, region_id, amount, status, created_at",
    )
    _bootstrap_sql(environment, (f"ALTER TABLE {ORDERS_TABLE} SET TIFLASH REPLICA 1",))
    # The replica must be queryable before the scoring window opens: dashboard and
    # analysis SQL route reads through tiflash isolation, which fails with planner
    # error 1815 while the replica is still syncing.
    deadline = time.monotonic() + 600.0
    while True:
        connection = environment.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT AVAILABLE FROM information_schema.tiflash_replica "
                    "WHERE TABLE_SCHEMA = 'htap' AND TABLE_NAME = 'orders';"
                )
                row = cursor.fetchone()
            connection.rollback()
        finally:
            connection.close()
        if row is not None and int(row[0]) == 1:
            break
        if time.monotonic() > deadline:
            raise RuntimeError(
                "TiFlash replica for htap.orders did not become available within 600s: "
                f"row={row!r}, run_id={environment.deployment.run_id!r}"
            )
        time.sleep(5)


def _bootstrap_cdc(environment, spec) -> None:
    from src.persistent_scenarios.backend.tidb.capabilities.cdc.safepoint import (
        GC_LIFE_TIME_BASELINE_SECONDS,
        format_gc_duration,
    )
    from src.persistent_scenarios.backend.tidb.capabilities.cdc.schema import schema_statements

    # The sink account name is the frozen contract value shared by the spec's
    # agent repair action and the schema-release capability's REVOKE
    # (cdc capabilities.py keeps it private as _SINK_USER).
    SINK_USER = "cdc_sink"

    statements = schema_statements()
    _bootstrap_sql(environment, statements.upstream)
    # GC retention baseline (composite factor B): the deployed upstream must
    # carry the schema_release payload fact upstream_gc_life_time="30m0s"
    # (GC_LIFE_TIME_BASELINE_SECONDS) so the pinned-checkpoint stall develops
    # inside the recovery window instead of living on the TiDB default. The
    # changefeed pin-release analogue (gc_pin_release_seconds=600) is mirrored
    # on the deployment side as the ticdc server --gc-ttl in
    # TiDBPersistentDeployment.render_compose_spec.
    _bootstrap_sql(environment, (
        f"SET GLOBAL tidb_gc_life_time = '{format_gc_duration(GC_LIFE_TIME_BASELINE_SECONDS)}'",
    ))
    downstream = environment.connect_downstream()
    try:
        with downstream.cursor() as cursor:
            for statement in statements.downstream:
                cursor.execute(statement)
            cursor.execute(f"CREATE USER IF NOT EXISTS '{SINK_USER}'@'%' IDENTIFIED BY ''")
            cursor.execute(
                f"GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX, REFERENCES "
                f"ON *.* TO '{SINK_USER}'@'%'"
            )
        downstream.commit()
    finally:
        downstream.close()
    admin = environment.changefeed_admin()
    # The feed dials the sink from inside the ticdc container: the compose
    # service name and the container port, not the host-mapped endpoint.
    downstream_service = environment.deployment.topology.role_services("downstream")[0]
    # start_ts omitted: the cdc cli pins the feed to the current TSO at creation,
    # which is the bootstrap contract (replicate changes from now on).
    admin.create("cdc-freshness", f"mysql://{SINK_USER}@{downstream_service}:3306/")
    _wait_changefeed_normal(admin, "cdc-freshness")


def _wait_changefeed_normal(admin, feed_id: str, timeout: float = 120.0) -> Mapping[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        state = admin.query(feed_id)
        if state.get("state") == "normal":
            return state
        time.sleep(2.0)
    raise TiDBPersistentDeploymentError(
        f"cdc bootstrap changefeed did not reach state=normal: feed_id={feed_id!r}, "
        f"state={state!r}"
    )


@dataclass(frozen=True)
class InstanceBinding:
    """One instance's assembly contract: bootstrap, workload factory,
    capability registry and the normalized verifier maps."""

    scenario_id: str
    bootstrap: Callable[[Any, Any], None]
    make_workload: Callable
    registry: Callable[[LazyRuntimeProvider], InstanceEventRegistry]
    integrity: Mapping[str, VerifierBinding]
    required_state: Mapping[str, VerifierBinding]

    def make_workload_entry(self, environment, spec, run_id, clock, scoring_origin):
        # Run artifacts live OUTSIDE the deployment data dir: the environment
        # teardown deletes the cluster data dir, while the trusted ledgers must
        # survive it for the trace export and the state-fact sampling.
        ledgers_dir = Path(environment.deployment.data_dir).parent / "ledgers" / run_id
        ledgers_dir.mkdir(parents=True, exist_ok=True)
        return self.make_workload(environment, spec, run_id, clock, scoring_origin, ledgers_dir)

    def integrity_binding(self, verifier_id: str) -> VerifierBinding:
        try:
            return self.integrity[verifier_id]
        except KeyError:
            raise KeyError(
                f"instance registers no integrity verifier: scenario_id={self.scenario_id!r}, "
                f"verifier_id={verifier_id!r}, known={sorted(self.integrity)!r}"
            ) from None

    def required_state_binding(self, verifier_id: str) -> VerifierBinding:
        try:
            return self.required_state[verifier_id]
        except KeyError:
            raise KeyError(
                f"instance registers no required-state verifier: scenario_id={self.scenario_id!r}, "
                f"verifier_id={verifier_id!r}, known={sorted(self.required_state)!r}"
            ) from None


_INSTANCE_BINDINGS: dict[str, InstanceBinding] = {}


def register_instance_binding(binding: InstanceBinding) -> None:
    """Explicit per-workload registration (no auto discovery)."""
    _INSTANCE_BINDINGS[binding.scenario_id] = binding


def _binding(scenario_id: str) -> InstanceBinding:
    try:
        return _INSTANCE_BINDINGS[scenario_id]
    except KeyError:
        raise ValueError(
            f"No TiDB assembly binding registered for the scenario: scenario_id={scenario_id!r}, "
            f"known={sorted(_INSTANCE_BINDINGS)!r}"
        ) from None


def _oltp_integrity_bindings() -> dict[str, VerifierBinding]:
    from src.persistent_scenarios.tidb.hotspot.verifiers import (
        commerce_ledger_conservation,
        orders_idempotency_uniqueness,
        unknown_commit_dedup,
    )

    def _drop_port(call):
        return lambda environment, connection, views, params: call(
            None, connection, views[0], params
        )

    return {
        "commerce_ledger_conservation": VerifierBinding(("trade",), _drop_port(commerce_ledger_conservation)),
        "orders_idempotency_uniqueness": VerifierBinding(("trade",), _drop_port(orders_idempotency_uniqueness)),
        "unknown_commit_dedup": VerifierBinding(("trade",), _drop_port(unknown_commit_dedup)),
    }


def _topology_required_state_bindings() -> dict[str, VerifierBinding]:
    from src.persistent_scenarios.tidb.topology.verifiers import (
        maintenance_final_state,
        replica_safety_after_change,
    )

    def _pass_environment(call):
        return lambda environment, connection, views, params: call(
            environment, connection, views[0], params
        )

    return {
        "maintenance_final_state": VerifierBinding(("maintenance",), _pass_environment(maintenance_final_state)),
        "replica_safety_after_change": VerifierBinding(("maintenance",), _pass_environment(replica_safety_after_change)),
    }


def _warehouse_verifier_bindings() -> dict[str, VerifierBinding]:
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.runtime import (
        SERVICE_INGEST,
        SERVICE_REPORT,
    )
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse.verifiers import VERIFIERS

    ledger_choice = {
        "wh_report_result_truth": SERVICE_REPORT,
        "wh_fact_table_batch_invariant": SERVICE_INGEST,
        "wh_staging_tables_present": SERVICE_INGEST,
        "wh_analytics_continuity": SERVICE_REPORT,
        "wh_statistics_current": SERVICE_INGEST,
    }
    def _adapt(call):
        # warehouse verifiers consume the single-ledger face, not the
        # normalized assembly convention (environment, connection, views, params).
        return lambda environment, connection, views, params: call(connection, views[0], params)

    return {
        verifier_id: VerifierBinding((ledger_choice[verifier_id],), _adapt(call))
        for verifier_id, call in VERIFIERS.items()
    }


class _CompositeLedgerView:
    """Composition of several runtime ledgers for verifiers that must span
    services: the htap truth check sees the shared analysis pool AND the
    tenant service, because the tenant heavy analysis is a separate delivery
    duty whose job record lives in its own ledger."""

    def __init__(self, views: tuple) -> None:
        self._views = views

    def jobs(self):
        return tuple(job for view in self._views for job in view.jobs())

    def logical_transactions(self):
        return tuple(tx for view in self._views for tx in view.logical_transactions())


def _htap_verifier_bindings() -> dict[str, VerifierBinding]:
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash.runtime import (
        SERVICE_ANALYSIS,
        SERVICE_TENANT,
        SERVICE_TRADE,
    )
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash.verifiers import VERIFIERS

    ledger_choice = {
        "htap_trade_orders_conserved": (SERVICE_TRADE,),
        # The truth check spans both delivery duties: the shared analysis pool
        # and the tenant service (tenant_region_heavy_analysis).
        "htap_analysis_result_truth": (SERVICE_ANALYSIS, SERVICE_TENANT),
        "htap_analytics_config_continuity": (SERVICE_TRADE,),
        "htap_tiflash_replica_present": (SERVICE_TRADE,),
        # Dual-residue verifier (olap package): the trade-side tenant tables
        # onboarded during the run; pure catalog observation, ledger view unused.
        "htap_tenant_replica_attached": (SERVICE_TRADE,),
    }
    def _adapt(call):
        # htap verifiers consume the composite-ledger face, not the
        # normalized assembly convention (environment, connection, views, params).
        return lambda environment, connection, views, params: call(connection, _CompositeLedgerView(views), params)

    return {
        verifier_id: VerifierBinding(ledger_choice[verifier_id], _adapt(call))
        for verifier_id, call in VERIFIERS.items()
    }


def _cdc_verifier_bindings() -> dict[str, VerifierBinding]:
    def _keyword_call(instance):
        def call(environment, connection, views, params):
            return instance(
                params,
                upstream=environment.connect(),
                downstream=environment.connect_downstream(),
                ledger_view=views[0],
            )

        return call

    # Keys follow CdcFreshnessWorkloadRuntime.ledgers(): the runtime ledger
    # mapping exposes the two cdc ledgers as "orders" and "visibility".
    ledger_choice = {
        "cdc_marker_pairing": "visibility",
        "cdc_upstream_ledger_conservation": "orders",
        "cdc_downstream_caught_up": "visibility",
        "cdc_visibility_deadline": "visibility",
    }
    return {
        instance.verifier_id: VerifierBinding((ledger_choice[instance.verifier_id],), _keyword_call(instance))
        for instance in _CDC_VERIFIERS
    }


def _register_default_bindings() -> None:
    from src.persistent_scenarios.backend.tidb.capabilities.cdc import CAPABILITIES as _CDC_CAPABILITIES
    from src.persistent_scenarios.backend.tidb.capabilities.tiflash import (
        HtapCapabilityRegistry,
    )
    from src.persistent_scenarios.backend.tidb.capabilities.warehouse import (
        WarehouseCapabilityRegistry,
    )
    from src.persistent_scenarios.backend.tidb.capabilities.hotspot import CAPABILITIES as _HOTSPOT
    from src.persistent_scenarios.backend.tidb.capabilities.topology import CAPABILITIES as _TOPOLOGY

    def _plain_registry(capabilities):
        return lambda runtime_provider: InstanceEventRegistry(capabilities)

    def _provider_registry(registry_class):
        return lambda runtime_provider: InstanceEventRegistry(
            (), registry_factory=registry_class, runtime_provider=runtime_provider
        )

    defaults = (
        InstanceBinding(
            scenario_id="tidb_oltp_hotspot_resilience",
            bootstrap=_bootstrap_hotspot,
            make_workload=_make_hotspot_workload,
            registry=_plain_registry(_HOTSPOT),
            integrity=_oltp_integrity_bindings(),
            required_state={},
        ),
        InstanceBinding(
            scenario_id="tidb_oltp_online_topology_change",
            bootstrap=_bootstrap_topology,
            make_workload=_make_topology_workload,
            registry=_plain_registry(_TOPOLOGY),
            integrity=_oltp_integrity_bindings(),
            required_state=_topology_required_state_bindings(),
        ),
        InstanceBinding(
            scenario_id="tidb_olap_warehouse_delivery",
            bootstrap=_bootstrap_warehouse,
            make_workload=_make_warehouse_workload,
            registry=_provider_registry(WarehouseCapabilityRegistry),
            integrity=_warehouse_verifier_bindings(),
            required_state={
                "wh_analytics_continuity": _warehouse_verifier_bindings()["wh_analytics_continuity"],
                "wh_statistics_current": _warehouse_verifier_bindings()["wh_statistics_current"],
            },
        ),
        InstanceBinding(
            scenario_id="tidb_htap_tiflash_isolation",
            bootstrap=_bootstrap_htap,
            make_workload=_make_htap_workload,
            registry=_provider_registry(HtapCapabilityRegistry),
            integrity=_htap_verifier_bindings(),
            required_state={
                "htap_analytics_config_continuity":
                    _htap_verifier_bindings()["htap_analytics_config_continuity"],
                "htap_tiflash_replica_present": _htap_verifier_bindings()["htap_tiflash_replica_present"],
                # Dual-residue required state (olap package):
                # the tenant tables onboarded inside the maintenance window must
                # carry their placement at seal time.
                "htap_tenant_replica_attached":
                    _htap_verifier_bindings()["htap_tenant_replica_attached"],
            },
        ),
        InstanceBinding(
            scenario_id="tidb_cdc_downstream_freshness",
            bootstrap=_bootstrap_cdc,
            make_workload=_make_cdc_workload,
            registry=_plain_registry(_CDC_CAPABILITIES),
            integrity={
                "cdc_marker_pairing": _cdc_verifier_bindings()["cdc_marker_pairing"],
                "cdc_upstream_ledger_conservation":
                    _cdc_verifier_bindings()["cdc_upstream_ledger_conservation"],
            },
            required_state={
                "cdc_downstream_caught_up": _cdc_verifier_bindings()["cdc_downstream_caught_up"],
            },
        ),
    )
    for binding in defaults:
        register_instance_binding(binding)


_register_default_bindings()


# ---------------------------------------------------------------------------
# Public build entry (REQ-002 shape)
# ---------------------------------------------------------------------------


def build_tidb_backend(
    spec: PersistentScenarioSpec,
    *,
    environment_provider: TiDBAssemblyEnvironmentProvider,
) -> TiDBPersistentScenarioBackend:
    """Assemble the TiDB backend bundle for one instance spec."""
    binding = _binding(spec.scenario_id)
    runtime_provider = LazyRuntimeProvider()
    backend = TiDBPersistentScenarioBackend(
        system=DatabaseSystem.TIDB,
        environment=environment_provider,
        events=binding.registry(runtime_provider),
        workload=TiDBWorkloadProvider(binding, runtime_provider),
        telemetry=TiDBTelemetryProvider(),
        safety=TiDBSafetyProvider(),
        state_facts=TiDBStateFactProvider(binding, runtime_provider),
        action_classifier=TranslatingActionClassifier(spec.scenario_id),
        _registered_scenario_ids=tuple(sorted(_INSTANCE_BINDINGS)),
    )
    backend.validate_spec(spec)
    return backend
