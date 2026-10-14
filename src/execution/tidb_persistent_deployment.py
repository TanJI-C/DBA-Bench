"""Docker Compose deployment for TiDB Persistent Scenario topologies.

This module owns only Docker control: compose rendering, network/port/data-dir
management, readiness waiting and service lifecycle. Node/role semantics,
images and NodeSpec expansion live in
``src/persistent_scenarios/backend/tidb/topology.py``.

Resource lease (tidb5-portfolio batch):
- run_id must start with ``tidb5-backend-`` and the remainder must match the
  docker compose project-name charset ``[a-z0-9][a-z0-9_-]*`` (lowercase
  letter/digit first, then lowercase letters, digits, dashes, underscores),
  which the benchmark planner's ``__``-joined run_ids satisfy;
- host ports must stay inside 26000-26499;
- data directories live under ``<repo>/data/tidb5-backend/<run_id>`` and are
  removed through a root-privileged one-shot container so bind mounts owned by
  container-internal users (MySQL) stay removable.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import socket
import subprocess
import time
from typing import Any, Mapping

import pymysql
import yaml

from src.execution.tidb_runtime import TIDB_V8_1_0, TiDBReleaseSpec
from src.execution.docker_network import create_tidb_network
from src.execution.host_ports import claim_host_ports

_NETWORK_TOOL_IMAGE = (
    "docker.m.daocloud.io/nicolaka/netshoot@"
    "sha256:b09d9b21381f47a79b3cbcb30da25266dc17186ea00ae65e99fdc51396f48e70"
)
_MONITORING_IMAGES = (
    "prom/prometheus@sha256:f20d3127bf2876f4a1df76246fca576b41ddf1125ed1c546fbd8b16ea55117e6",
    "m.daocloud.io/gcr.io/cadvisor/cadvisor@sha256:3cde6faf0791ebf7b41d6f8ae7145466fed712ea6f252c935294d2608b1af388",
)
TICDC_IMAGE = "pingcap/ticdc@sha256:7832063b5215b3107d33b7280b2653a79667e9ba54e4b0596ed1092b4a486015"
MYSQL_IMAGE = "mysql@sha256:43bd9764df60666fb2ba2cf8217dd17b3d2414c150005d2fdd07a0cd73d3b7f5"

RUN_ID_PREFIX = "tidb5-backend-"
PORT_RANGE = (26000, 26499)
_REPO_ROOT = Path(__file__).resolve().parents[2]
_COMPOSE_TEMPLATE_DIR = _REPO_ROOT / "config" / "docker" / "tidb-docker"
DATA_ROOT = _REPO_ROOT / "data" / "tidb5-backend"

_ROLES = ("pd", "tikv", "tidb", "tiflash", "ticdc", "downstream")
_ROLE_IMAGES = {
    "pd": lambda release: release.pd_image,
    "tikv": lambda release: release.tikv_image,
    "tidb": lambda release: release.tidb_image,
    "tiflash": lambda release: release.tiflash_image,
    "ticdc": lambda release: TICDC_IMAGE,
    "downstream": lambda release: MYSQL_IMAGE,
}


class TiDBPersistentDeploymentError(RuntimeError):
    """Deployment failure with diagnosable context (ports, compose, readiness)."""


class TiDBReadinessFatalError(TiDBPersistentDeploymentError):
    """A topology container exited before readiness; retrying cannot succeed."""


@dataclass(frozen=True)
class PersistentTiDBNodePlan:
    """One docker-compose service expanded from a NodeSpec."""

    service: str
    role: str
    node_id: str
    image: str
    cpus: float
    memory_mb: int
    cap_add: tuple[str, ...] = ()
    volumes: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.role not in _ROLES:
            raise ValueError(
                f"Unknown TiDB persistent node role: role={self.role!r}, expected={_ROLES!r}"
            )
        if self.cpus <= 0 or self.memory_mb <= 0:
            raise ValueError(
                f"Node resources must be positive: service={self.service!r}, "
                f"cpus={self.cpus!r}, memory_mb={self.memory_mb!r}"
            )


@dataclass(frozen=True)
class PersistentTiDBTopologyPlan:
    """Expanded multi-node plan consumed by ``TiDBPersistentDeployment``."""

    nodes: tuple[PersistentTiDBNodePlan, ...]

    def __post_init__(self) -> None:
        services = [node.service for node in self.nodes]
        if len(services) != len(set(services)):
            raise ValueError(f"TiDB persistent services must be unique: services={services!r}")

    def role_services(self, role: str) -> tuple[str, ...]:
        return tuple(node.service for node in self.nodes if node.role == role)

    def service(self, name: str) -> PersistentTiDBNodePlan:
        for node in self.nodes:
            if node.service == name:
                return node
        raise ValueError(f"Unknown TiDB persistent service: services={[node.service for node in self.nodes]!r}, name={name!r}")

    @property
    def tidb_count(self) -> int:
        return len(self.role_services("tidb"))

    @property
    def allocated_port_count(self) -> int:
        return port_allocation_count(self, enable_monitoring=True)


def port_allocation_count(topology: PersistentTiDBTopologyPlan, *, enable_monitoring: bool = True) -> int:
    """Number of host ports the deployment allocates from its port_base."""
    count = (
        2 * len(topology.role_services("tidb"))
        + len(topology.role_services("downstream"))
        + len(topology.role_services("ticdc"))
    )
    if enable_monitoring:
        count += 1  # prometheus
    return count


@dataclass(frozen=True)
class PersistentTiDBPortPlan:
    tidb_sql: dict[str, int]
    tidb_status: dict[str, int]
    prometheus: int | None  # None when monitoring is disabled
    downstream: dict[str, int]
    ticdc: dict[str, int]

    @property
    def host_ports(self) -> tuple[int, ...]:
        ports = [*self.tidb_sql.values(), *self.tidb_status.values(), *self.downstream.values(), *self.ticdc.values()]
        if self.prometheus is not None:
            ports.append(self.prometheus)
        return tuple(sorted(ports))


def build_port_plan(topology: PersistentTiDBTopologyPlan, port_base: int, *, enable_monitoring: bool = True) -> PersistentTiDBPortPlan:
    """Allocate host ports from the TiDB SQL port_base upward.

    Each TiDB node takes a consecutive port pair (SQL 4000, status 10080);
    the remaining single-port services follow in fixed order: prometheus,
    downstream, ticdc. With ``enable_monitoring=False`` the prometheus port is
    not allocated (metric scraping is unavailable).
    """
    tidb_services = topology.role_services("tidb")
    tidb_sql = {service: port_base + 2 * index for index, service in enumerate(tidb_services)}
    tidb_status = {service: port_base + 2 * index + 1 for index, service in enumerate(tidb_services)}
    cursor = port_base + 2 * len(tidb_services)

    def take() -> int:
        nonlocal cursor
        value = cursor
        cursor += 1
        return value

    prometheus = take() if enable_monitoring else None
    downstream = {service: take() for service in topology.role_services("downstream")}
    ticdc = {service: take() for service in topology.role_services("ticdc")}
    return PersistentTiDBPortPlan(
        tidb_sql=tidb_sql,
        tidb_status=tidb_status,
        prometheus=prometheus,
        downstream=downstream,
        ticdc=ticdc,
    )


class TiDBPersistentDeployment:
    """One persistent TiDB topology deployed with docker compose."""

    def __init__(
        self,
        *,
        run_id: str,
        port_base: int,
        topology: PersistentTiDBTopologyPlan,
        data_root: os.PathLike[str] | str = DATA_ROOT,
        release: TiDBReleaseSpec = TIDB_V8_1_0,
        readiness_timeout_seconds: int = 1800,
        first_tidb_readiness_timeout_seconds: int = 900,
        enable_monitoring: bool = True,
    ):
        if not run_id.startswith(RUN_ID_PREFIX):
            raise ValueError(f"TiDB persistent run_id must use the batch lease prefix {RUN_ID_PREFIX!r}: run_id={run_id!r}")
        if re.fullmatch(r"[a-z0-9][a-z0-9_-]*", run_id[len(RUN_ID_PREFIX):]) is None:
            raise ValueError(
                f"TiDB persistent run_id must use the docker compose project-name charset after the prefix "
                f"({RUN_ID_PREFIX!r} + [a-z0-9][a-z0-9_-]*): run_id={run_id!r}"
            )
        port_count = port_allocation_count(topology, enable_monitoring=enable_monitoring)
        if not PORT_RANGE[0] <= port_base <= PORT_RANGE[1] or port_base + port_count - 1 > PORT_RANGE[1]:
            raise ValueError(
                f"TiDB persistent port_base violates the lease range {PORT_RANGE!r}: "
                f"port_base={port_base}, required_ports={port_count}"
            )
        if readiness_timeout_seconds <= 0 or first_tidb_readiness_timeout_seconds <= 0:
            raise ValueError(
                f"Readiness timeouts must be positive: readiness={readiness_timeout_seconds}, "
                f"first_tidb={first_tidb_readiness_timeout_seconds}"
            )
        for role in ("pd", "tikv", "tidb"):
            if not topology.role_services(role):
                raise ValueError(f"TiDB persistent topology requires at least one {role} node: topology={topology!r}")
        for role in ("tiflash", "ticdc", "downstream"):
            for service in topology.role_services(role):
                image = topology.service(service).image
                expected = _ROLE_IMAGES[role](release)
                if image != expected:
                    raise ValueError(
                        f"TiDB persistent service image does not match the release: "
                        f"service={service!r}, role={role!r}, image={image!r}, expected={expected!r}"
                    )
        self.run_id = run_id
        self.port_base = port_base
        self.topology = topology
        self.release = release
        self.readiness_timeout_seconds = readiness_timeout_seconds
        self.first_tidb_readiness_timeout_seconds = first_tidb_readiness_timeout_seconds
        self.data_root = Path(data_root).resolve()
        self.data_dir = self.data_root / run_id
        self.project_name = f"aiopsbench-{run_id}"
        self.network_name = f"{self.project_name}-network"
        self.network_subnet: str | None = None
        self._network_created = False
        self.enable_monitoring = enable_monitoring
        self.ports = build_port_plan(topology, port_base, enable_monitoring=enable_monitoring)
        self.tidb_endpoints = {
            f"tidb/{service}": ("127.0.0.1", self.ports.tidb_sql[service])
            for service in topology.role_services("tidb")
        }
        self.NODES = {
            f"{node.role}/{node.service}": node.service for node in topology.nodes
        }
        if enable_monitoring:
            self.NODES.update({"monitoring/prometheus-0": "prometheus", "monitoring/cadvisor-0": "cadvisor"})
        self.prometheus_port = self.ports.prometheus
        self.database_nodes = tuple(
            f"{node.role}/{node.service}" for node in topology.nodes if node.role in ("pd", "tikv", "tidb", "tiflash")
        )
        self.node_cpu_limits = {
            **{f"{node.role}/{node.service}": node.cpus for node in topology.nodes},
            **({"monitoring/prometheus-0": 0.5, "monitoring/cadvisor-0": 2.0} if enable_monitoring else {}),
        }
        self.runtime_dir = self.data_dir / "runtime"
        self.compose_file = self.runtime_dir / "docker-compose.yml"
        self._env: dict[str, str] = dict(os.environ)
        self._deployed = False
        self._port_lease = None

    # -- basic properties -----------------------------------------------------

    @property
    def project_ports(self) -> tuple[int, ...]:
        return self.ports.host_ports

    def tidb_sql_endpoint(self, service: str) -> tuple[str, int]:
        return "127.0.0.1", self.ports.tidb_sql[service]

    def downstream_sql_endpoint(self, service: str | None = None) -> tuple[str, int]:
        services = self.topology.role_services("downstream")
        if service is None:
            if not services:
                raise TiDBPersistentDeploymentError(
                    f"Topology has no downstream MySQL node: run_id={self.run_id!r}"
                )
            service = services[0]
        if service not in self.ports.downstream:
            raise ValueError(
                f"Unknown downstream service: run_id={self.run_id!r}, service={service!r}, "
                f"known={services!r}"
            )
        return "127.0.0.1", self.ports.downstream[service]

    # -- docker helpers ---------------------------------------------------------

    def _run(self, cmd: list[str], *, component: str = "cluster", timeout: int | None = None) -> str:
        result = subprocess.run(cmd, capture_output=True, text=True, env=self._env, timeout=timeout)
        if result.returncode != 0:
            raise TiDBPersistentDeploymentError(
                f"TiDB persistent docker command failed: run_id={self.run_id!r}, component={component!r}, "
                f"command={shlex.join(cmd)!r}, returncode={result.returncode}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        return result.stdout

    @property
    def _compose(self) -> list[str]:
        if self.enable_monitoring and "DOCKER_ROOT_DIR" not in self._env:
            self._load_docker_root()
        return ["docker", "compose", "--project-name", self.project_name, "--file", str(self.compose_file)]

    def _load_docker_root(self) -> None:
        info = self._run(
            ["docker", "info", "--format", "{{.DockerRootDir}}"], component="docker"
        ).strip()
        self._env["DOCKER_ROOT_DIR"] = info

    def run_compose(self, *args: str, timeout: int = 120) -> str:
        """Run one ``docker compose`` subcommand through the deployment env.

        The single compose execution path for assembly-side lifecycle commands
        (deferred TiKV store rm/create/start): ``self._compose`` lazily loads
        ``DOCKER_ROOT_DIR`` into ``self._env`` when monitoring is enabled and
        the child always runs with ``env=self._env``, so the cadvisor
        ``${DOCKER_ROOT_DIR:?...}`` volume interpolation cannot fail on a
        command that never went through the main deploy path first.
        """
        command = self._compose + list(args)
        result = subprocess.run(command, capture_output=True, text=True, env=self._env, timeout=timeout)
        if result.returncode != 0:
            raise TiDBPersistentDeploymentError(
                f"compose command failed: args={args!r}, project={self.project_name!r}, "
                f"stderr={result.stderr.strip()[-400:]!r}"
            )
        return result.stdout

    def service_container_id(self, service: str) -> str:
        known = {*(node.service for node in self.topology.nodes), *self.NODES.values()}
        if service not in known:
            raise ValueError(f"Unknown TiDB persistent service: services={sorted(known)!r}, name={service!r}")
        container_id = self._run(self._compose + ["ps", "--all", "--quiet", service], component=service).strip()
        if not container_id:
            raise TiDBPersistentDeploymentError(
                f"TiDB persistent container not found: run_id={self.run_id!r}, service={service!r}"
            )
        return container_id

    def service_state(self, service: str) -> dict[str, Any]:
        container_id = self.service_container_id(service)
        payload = self._run(
            ["docker", "inspect", "--format", "{{json .State}}", container_id], component=service
        )
        return json.loads(payload)

    def service_logs(self, service: str, *, tail: int = 200) -> str:
        if tail <= 0:
            raise ValueError(f"Log tail must be positive: service={service!r}, tail={tail}")
        return self._run(
            ["docker", "logs", "--tail", str(tail), self.service_container_id(service)],
            component=service,
        )

    def exec_command(self, service: str, command: list[str], *, timeout: int = 30) -> str:
        return self._run(
            ["docker", "exec", self.service_container_id(service), *command],
            component=service,
            timeout=timeout,
        )

    def pd_request(self, method: str, path: str, body: Mapping[str, Any] | None = None) -> Any:
        """Issue a PD HTTP API request through the pd-0 container (busybox wget)."""
        if not path.startswith("/pd/api/v1/"):
            raise ValueError(f"PD API path must stay under /pd/api/v1/: path={path!r}")
        command = ["wget", "-qO-", "-T", "5"]
        if method != "GET":
            command.extend([f"--method={method}", "--header=Content-Type: application/json"])
            if body is not None:
                command.append(f"--body-data={json.dumps(dict(body), separators=(',', ':'))}")
        command.append(f"http://127.0.0.1:2379{path}")
        output = self.exec_command(self.topology.role_services("pd")[0], command)
        output = output.strip()
        if not output:
            raise TiDBPersistentDeploymentError(
                f"PD API returned an empty response: run_id={self.run_id!r}, method={method!r}, path={path!r}"
            )
        return json.loads(output)

    # -- compose rendering -------------------------------------------------------

    def render_compose_spec(self) -> dict[str, Any]:
        """Build the compose mapping (pure; no docker side effects)."""
        config_dir = _COMPOSE_TEMPLATE_DIR / "config"
        pd_addresses = ",".join(f"{service}:2379" for service in self.topology.role_services("pd"))
        initial_cluster = ",".join(
            f"{service}=http://{service}:2380" for service in self.topology.role_services("pd")
        )
        services: dict[str, Any] = {}
        host_uid_gid = f"{os.getuid()}:{os.getgid()}"

        for service in self.topology.role_services("pd"):
            node = self.topology.service(service)
            services[service] = {
                "image": node.image,
                "cpus": node.cpus,
                "mem_limit": f"{node.memory_mb}m",
                "memswap_limit": f"{node.memory_mb}m",
                "storage_opt": {"size": "2G"},
                "volumes": [
                    *(f"{host}:{container}" for host, container in node.volumes),
                    str(config_dir / "pd.toml") + ":/pd.toml:ro",
                    str(self.data_dir / "pd" / service) + ":/data/pd",
                ],
                "init": True,
                "user": host_uid_gid,
                "restart": "no",
                "command": [
                    f"--name={service}", "--data-dir=/data/pd",
                    "--client-urls=http://0.0.0.0:2379", "--peer-urls=http://0.0.0.0:2380",
                    f"--advertise-client-urls=http://{service}:2379",
                    f"--advertise-peer-urls=http://{service}:2380",
                    f"--initial-cluster={initial_cluster}", "--config=/pd.toml", "--log-file=",
                ],
            }
            if node.cap_add:
                services[service]["cap_add"] = list(node.cap_add)

        for service in self.topology.role_services("tikv"):
            node = self.topology.service(service)
            services[service] = {
                "image": node.image,
                "cpus": node.cpus,
                "mem_limit": f"{node.memory_mb}m",
                "memswap_limit": f"{node.memory_mb}m",
                "storage_opt": {"size": "8G"},
                "volumes": [
                    *(f"{host}:{container}" for host, container in node.volumes),
                    # Dynamic config changes (the hotspot throttle/release
                    # primitives persist back to the TiKV config file) need a
                    # writable config: the shared template is staged per run
                    # (deploy) and mounted rw — the bounded deployment's
                    # tikv_config_writable pattern.
                    str(self.runtime_dir / f"{service}-config") + ":/tikv-config:rw",
                    str(self.data_dir / "tikv" / service) + ":/data/tikv",
                ],
                "init": True,
                "user": host_uid_gid,
                "restart": "no",
                "command": [
                    "--addr=0.0.0.0:20160", f"--advertise-addr={service}:20160",
                    "--status-addr=0.0.0.0:20180", f"--advertise-status-addr={service}:20180",
                    f"--pd={pd_addresses}", "--data-dir=/data/tikv",
                    "--config=/tikv-config/tikv.toml", "--log-file=",
                ],
            }
            if node.cap_add:
                services[service]["cap_add"] = list(node.cap_add)

        for index, service in enumerate(self.topology.role_services("tidb")):
            node = self.topology.service(service)
            services[service] = {
                "image": node.image,
                "cpus": node.cpus,
                "mem_limit": f"{node.memory_mb}m",
                "memswap_limit": f"{node.memory_mb}m",
                "storage_opt": {"size": "2G"},
                "tmpfs": ["/tmp/tidb:size=512M"],
                "volumes": [
                    *(f"{host}:{container}" for host, container in node.volumes),
                    str(config_dir / "tidb.toml") + ":/tidb.toml:ro",
                ],
                "init": True,
                "restart": "no",
                "ports": [
                    f"{self.ports.tidb_sql[service]}:4000",
                    f"{self.ports.tidb_status[service]}:10080",
                ],
                "command": [
                    "--config=/tidb.toml", "--store=tikv", f"--path={pd_addresses}", "--host=0.0.0.0",
                    f"--advertise-address={service}", "--status=10080",
                    *self.release.tidb_extra_args, "--log-file=",
                ],
            }
            if node.cap_add:
                services[service]["cap_add"] = list(node.cap_add)

        for service in self.topology.role_services("tiflash"):
            node = self.topology.service(service)
            tiflash_config = self._render_tiflash_configs(service, pd_addresses)
            services[service] = {
                "image": node.image,
                "cpus": node.cpus,
                "mem_limit": f"{node.memory_mb}m",
                "memswap_limit": f"{node.memory_mb}m",
                "storage_opt": {"size": "10G"},
                "security_opt": ["seccomp:unconfined"],
                "volumes": [
                    *(f"{host}:{container}" for host, container in node.volumes),
                    str(tiflash_config) + ":/config.toml:ro",
                    str(tiflash_config.with_name(f"{service}-proxy.toml")) + ":/proxy.toml:ro",
                    str(self.data_dir / "tiflash" / service) + ":/data",
                ],
                "entrypoint": ["/tiflash/tiflash", "server", "--config-file", "/config.toml"],
                "depends_on": [*self.topology.role_services("pd"), *self.topology.role_services("tikv")],
                "restart": "no",
            }
            if node.cap_add:
                services[service]["cap_add"] = list(node.cap_add)

        for service in self.topology.role_services("downstream"):
            node = self.topology.service(service)
            services[service] = {
                "image": node.image,
                "cpus": node.cpus,
                "mem_limit": f"{node.memory_mb}m",
                "memswap_limit": f"{node.memory_mb}m",
                "environment": {"MYSQL_ALLOW_EMPTY_PASSWORD": "yes"},
                "volumes": [
                    *(f"{host}:{container}" for host, container in node.volumes),
                    str(self.data_dir / "downstream" / service) + ":/var/lib/mysql",
                ],
                "ports": [f"{self.ports.downstream[service]}:3306"],
                "command": [
                    "--default-time-zone=+08:00",
                    "--character-set-server=utf8mb4",
                    "--collation-server=utf8mb4_bin",
                ],
                "init": True,
                "restart": "no",
            }
            if node.cap_add:
                services[service]["cap_add"] = list(node.cap_add)

        for service in self.topology.role_services("ticdc"):
            node = self.topology.service(service)
            services[service] = {
                "image": node.image,
                "cpus": node.cpus,
                "mem_limit": f"{node.memory_mb}m",
                "memswap_limit": f"{node.memory_mb}m",
                "volumes": [
                    *(f"{host}:{container}" for host, container in node.volumes),
                    str(self.data_dir / "ticdc" / service) + ":/data",
                ],
                "depends_on": [*self.topology.role_services("pd"), *self.topology.role_services("tidb")],
                "ports": [f"{self.ports.ticdc[service]}:8300"],
                "command": [
                    "/cdc", "server",
                    "--addr=0.0.0.0:8300",
                    f"--advertise-addr={service}:8300",
                    f"--pd={','.join(f'http://{pd}:2379' for pd in self.topology.role_services('pd'))}",
                    "--data-dir=/data/cdc",
                    # Freshness-critical fail-fast GC pin release: on this
                    # ticdc build the GC manager takes its TTL from the server
                    # config (pkg/txnutil/gc/gc_manager.go gcTTL: serverConfig.GcTTL),
                    # and a changefeed whose checkpoint stalls longer than the
                    # TTL gives up its GC pin. 600s mirrors the schema_release
                    # payload fact gc_pin_release_seconds=600 (the cdc capability
                    # constant PIN_RELEASE_STALL_SECONDS; pinned by test).
                    "--gc-ttl=600",
                    "--tz=Asia/Shanghai",
                    "--log-file=",
                ],
                "restart": "no",
            }
            if node.cap_add:
                services[service]["cap_add"] = list(node.cap_add)

        prometheus_config = {
            "global": {"scrape_interval": "2s", "evaluation_interval": "2s"},
            "scrape_configs": [
                {"job_name": "pd", "static_configs": [{"targets": [f"{node}:2379" for node in self.topology.role_services("pd")]}]},
                {"job_name": "tikv", "static_configs": [{"targets": [f"{node}:20180" for node in self.topology.role_services("tikv")]}]},
                {"job_name": "tidb", "static_configs": [{"targets": [f"{node}:10080" for node in self.topology.role_services("tidb")]}]},
            ],
        }
        if self.topology.role_services("tiflash"):
            prometheus_config["scrape_configs"].append(
                {"job_name": "tiflash", "static_configs": [{"targets": [f"{node}:8234" for node in self.topology.role_services("tiflash")]}]}
            )
        if self.topology.role_services("ticdc"):
            prometheus_config["scrape_configs"].append(
                {"job_name": "ticdc", "static_configs": [{"targets": [f"{node}:8300" for node in self.topology.role_services("ticdc")]}]}
            )
        prometheus_config["scrape_configs"].append(
            {"job_name": "cadvisor", "scrape_interval": "5s", "scrape_timeout": "4s", "static_configs": [{"targets": ["cadvisor:8080"]}]}
        )
        prometheus_config_path = self.runtime_dir / "prometheus.yml"
        if self.enable_monitoring:
            prometheus_config_path.parent.mkdir(parents=True, exist_ok=True)
            with prometheus_config_path.open("w", encoding="utf-8") as handle:
                yaml.safe_dump(prometheus_config, handle, sort_keys=False)

            services["prometheus"] = {
                "image": _MONITORING_IMAGES[0],
                "user": "0:0",
                "cpus": 0.5,
                "mem_limit": "2g",
                "memswap_limit": "2g",
                "storage_opt": {"size": "4G"},
                "init": True,
                "restart": "no",
                "ports": [f"{self.ports.prometheus}:9090"],
                "volumes": [str(prometheus_config_path) + ":/etc/prometheus/prometheus.yml:ro"],
            }
            services["cadvisor"] = {
                "image": _MONITORING_IMAGES[1],
                "cpus": 2.0,
                "mem_limit": "2g",
                "memswap_limit": "2g",
                "command": [
                    "--docker_only=true",
                    "--housekeeping_interval=2s",
                    "--global_housekeeping_interval=2s",
                    "--store_container_labels=true",
                ],
                "privileged": True,
                "devices": ["/dev/kmsg:/dev/kmsg"],
                "volumes": [
                    "/:/rootfs:ro",
                    "/var/run:/var/run:ro",
                    "/sys:/sys:ro",
                    "${DOCKER_ROOT_DIR:?DOCKER_ROOT_DIR is required}:/var/lib/docker:ro",
                    "/dev/disk:/dev/disk:ro",
                ],
                "init": True,
                "restart": "no",
            }
        return {
            "services": services,
            "volumes": {},
            "networks": {"default": {"name": self.network_name, "external": True}},
        }

    def _render_tiflash_configs(self, service: str, pd_addresses: str) -> Path:
        config_path = self.runtime_dir / f"{service}.toml"
        proxy_path = self.runtime_dir / f"{service}-proxy.toml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        proxy_path.write_text(
            "[security]\nca-path = \"\"\ncert-path = \"\"\nkey-path = \"\"\n\n"
            "[storage]\nreserve-space = \"0\"\n\n"
            "[raftstore]\ncapacity = \"8GB\"\n",
            encoding="utf-8",
        )
        config_path.write_text(
            "tmp_path = \"/data/tmp\"\n"
            "path = \"/data/db\"\n"
            "capacity = \"8589934592\"\n"
            "mark_cache_size = 268435456\nminmax_index_cache_size = 268435456\n"
            "tcp_port = 9000\nhttp_port = 8123\n\n"
            "[flash]\nservice_addr = \"0.0.0.0:3930\"\n"
            "[flash.flash_cluster]\nupdate_rule_interval = 5\n"
            "[flash.proxy]\naddr = \"0.0.0.0:20170\"\n"
            f"advertise-addr = \"{service}:20170\"\n"
            "data-dir = \"/data/proxy\"\nconfig = \"/proxy.toml\"\nlog-file = \"\"\n"
            f"engine-addr = \"{service}:3930\"\nstatus-addr = \"0.0.0.0:20181\"\n"
            f"advertise-status-addr = \"{service}:20181\"\n\n"
            "[logger]\ncount = 3\nerrorlog = \"\"\nlog = \"\"\nlevel = \"info\"\n\n"
            "[application]\nrunAsDaemon = false\n\n"
            f"[raft]\npd_addr = \"{pd_addresses}\"\nignore_databases = \"system,default\"\n\n"
            "[profiles]\n[profiles.default]\n",
            encoding="utf-8",
        )
        return config_path

    # -- deploy / readiness / teardown --------------------------------------------

    def deploy(self) -> None:
        if self._deployed:
            raise TiDBPersistentDeploymentError(f"TiDB persistent deployment already deployed: run_id={self.run_id!r}")
        self._preflight()
        self._ensure_network()
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        # Per-run writable TiKV config (see render_compose_spec): the dynamic
        # config change primitives persist back to the config file.
        for service in self.topology.role_services("tikv"):
            config_target = self.runtime_dir / f"{service}-config"
            config_target.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(_COMPOSE_TEMPLATE_DIR / "config" / "tikv.toml", config_target / "tikv.toml")
        for role, mount in (("pd", "/data/pd"), ("tikv", "/data/tikv"), ("ticdc", "/data/cdc"), ("downstream", "/var/lib/mysql")):
            for service in self.topology.role_services(role):
                (self.data_dir / role / service).mkdir(parents=True, exist_ok=True)
        for service in self.topology.role_services("tiflash"):
            (self.data_dir / "tiflash" / service).mkdir(parents=True, exist_ok=True)
        spec = self.render_compose_spec()
        with self.compose_file.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(spec, handle, sort_keys=False)
        # Staged start (TiUP order): PD must have a leader and TiKV stores must be
        # Up before TiDB/TiFlash/TiCDC boot, otherwise TiDB FATAL-exits at startup
        # with "get TSO failed, tso client is nil" instead of retrying.
        pd_services = self.topology.role_services("pd")
        tikv_services = self.topology.role_services("tikv")
        tail_services = [
            *(node.service for node in self.topology.nodes if node.role not in ("pd", "tikv")),
            *(("prometheus", "cadvisor") if self.enable_monitoring else ()),
        ]
        for services, label, check in (
            (pd_services, "pd", self._check_pd),
            (tikv_services, "tikv", self._check_tikv),
        ):
            self._run(self._compose + ["up", "--detach", "--no-deps", *services], component="cluster", timeout=600)
            self._wait(label, check, self.readiness_timeout_seconds, services)
        if tail_services:
            self._run(self._compose + ["up", "--detach", "--no-deps", *tail_services], component="cluster", timeout=600)
        self._deployed = True
        self._wait_ready()

    def deploy_stage_commands(self) -> tuple[list[str], ...]:
        """The exact staged `docker compose up` commands deploy() issues."""
        pd_services = self.topology.role_services("pd")
        tikv_services = self.topology.role_services("tikv")
        tail_services = [
            *(node.service for node in self.topology.nodes if node.role not in ("pd", "tikv")),
            *(("prometheus", "cadvisor") if self.enable_monitoring else ()),
        ]
        stages = []
        for services in (pd_services, tikv_services, tail_services):
            if services:
                stages.append([*"docker", "compose", "--project-name", self.project_name,
                               "--file", str(self.compose_file), "up", "--detach", "--no-deps", *services])
        return tuple(stages)

    def _preflight(self) -> None:
        if self._port_lease is None:
            self._port_lease = claim_host_ports(self.ports.host_ports, owner=self.run_id)
        self._run(["docker", "version"], component="docker")
        self._run(["docker", "compose", "version"], component="docker")
        monitoring_images = _MONITORING_IMAGES if self.enable_monitoring else ()
        required_images = (
            *(node.image for node in self.topology.nodes),
            *monitoring_images,
        )
        missing = [
            image for image in required_images
            if subprocess.run(["docker", "image", "inspect", image], capture_output=True, env=self._env).returncode != 0
        ]
        if missing:
            raise TiDBPersistentDeploymentError(
                f"TiDB persistent preflight missing images: run_id={self.run_id!r}, images={missing!r}"
            )
        disk_bytes = shutil.disk_usage(self._load_docker_root() if "DOCKER_ROOT_DIR" in self._env else self._docker_root()).free
        if disk_bytes < 20 * 1024**3:
            raise TiDBPersistentDeploymentError(
                f"TiDB persistent preflight disk insufficient: run_id={self.run_id!r}, free_bytes={disk_bytes}"
            )
        self._load_docker_root()
        for port in self.ports.host_ports:
            with socket.socket() as sock:
                try:
                    sock.bind(("127.0.0.1", port))
                except OSError as exc:
                    raise TiDBPersistentDeploymentError(
                        f"TiDB persistent preflight port unavailable: run_id={self.run_id!r}, port={port}, error={exc!r}"
                    ) from exc

    def _docker_root(self) -> str:
        return self._run(["docker", "info", "--format", "{{.DockerRootDir}}"], component="docker").strip()

    def _ensure_network(self) -> None:
        if self._network_created:
            return
        self.network_subnet = create_tidb_network(self.network_name, env=self._env)
        self._network_created = True

    def _wait_ready(self) -> None:
        if self.enable_monitoring:
            self._wait(
                "prometheus",
                lambda: self.exec_command("prometheus", ["wget", "-qO-", "http://127.0.0.1:9090/-/ready"]),
                self.readiness_timeout_seconds,
                ["prometheus"],
            )
        for service in self.topology.role_services("tiflash"):
            self._wait(
                f"tiflash/{service}",
                lambda service=service: self.exec_command(service, ["wget", "-qO-", "http://127.0.0.1:8234/metrics"]),
                self.readiness_timeout_seconds,
                [service],
            )
        for service in self.topology.role_services("tidb"):
            timeout = self.first_tidb_readiness_timeout_seconds
            self._wait(
                f"tidb/{service}",
                lambda service=service: self._check_tidb_sql(service),
                timeout,
                [service],
            )
        for service in self.topology.role_services("ticdc"):
            self._wait(
                f"ticdc/{service}",
                lambda service=service: self.exec_command(service, ["wget", "-qO-", "http://127.0.0.1:8300/status"]),
                self.readiness_timeout_seconds,
                [service],
            )
        for service in self.topology.role_services("downstream"):
            self._wait(
                f"downstream/{service}",
                lambda service=service: self._check_downstream_sql(service),
                self.readiness_timeout_seconds,
                [service],
            )

    def _readiness_diagnostics(self, label: str) -> dict[str, Any]:
        diagnostics: dict[str, Any] = {"label": label, "containers": {}, "log_tails": {}}
        for node in self.topology.nodes:
            try:
                state = self.service_state(node.service)
                diagnostics["containers"][node.service] = {
                    "status": state.get("Status"),
                    "running": state.get("Running"),
                    "exit_code": state.get("ExitCode"),
                    "error": state.get("Error"),
                }
                if not state.get("Running"):
                    diagnostics["log_tails"][node.service] = self.service_logs(node.service, tail=80)[-4000:]
            except Exception as exc:
                diagnostics["containers"][node.service] = f"inspection failed: {exc!r}"
        return diagnostics

    def _wait(self, label: str, check, timeout: int, scanned_services: list[str]) -> None:
        deadline = time.monotonic() + timeout
        last_error: Exception | None = None
        reported = -1
        last_fatal_scan = 0.0
        while time.monotonic() < deadline:
            if time.monotonic() - last_fatal_scan >= 5.0:
                self._fatal_container_scan(scanned_services)
                last_fatal_scan = time.monotonic()
            try:
                check()
                return
            except Exception as exc:
                last_error = exc
                elapsed = int(timeout - max(0.0, deadline - time.monotonic()))
                if elapsed // 30 != reported:
                    reported = elapsed // 30
                    print(
                        f"[TiDBPersistentDeployment] readiness pending: run_id={self.run_id!r}, "
                        f"stage={label!r}, elapsed={elapsed}s/{timeout}s, error={exc!r}",
                        flush=True,
                    )
                time.sleep(1)
        diagnostics = self._readiness_diagnostics(label)
        raise TiDBPersistentDeploymentError(
            f"TiDB persistent readiness timed out: run_id={self.run_id!r}, stage={label!r}, "
            f"timeout={timeout}, last_error={last_error!r}, diagnostics={diagnostics}"
        ) from last_error

    def _fatal_container_scan(self, services: list[str]) -> None:
        """Raise as soon as any started container exits before readiness.

        TiDB components FATAL-exit when they cannot join the cluster at boot
        (e.g. a transient docker embedded-DNS failure); waiting for readiness
        after that can never succeed, so fail fast with the container's log.
        Only services started by the current stage are scanned; later-stage
        containers do not exist yet.
        """
        for service in services:
            state = self.service_state(service)
            if not state.get("Running"):
                tail = self.service_logs(service, tail=80)[-2000:]
                raise TiDBReadinessFatalError(
                    f"TiDB persistent container exited before readiness: run_id={self.run_id!r}, "
                    f"service={service!r}, state={state!r}, log_tail={tail!r}"
                )

    def _check_pd(self) -> None:
        members = self.pd_request("GET", "/pd/api/v1/members").get("members", [])
        expected = self.topology.role_services("pd")
        if len(members) != len(expected):
            raise RuntimeError(f"expected {len(expected)} PD members, got {len(members)}: {members!r}")
        leader = self.pd_request("GET", "/pd/api/v1/leader")
        if leader.get("name") not in expected:
            raise RuntimeError(f"PD has no valid leader: run_id={self.run_id!r}, leader={leader!r}, expected={expected!r}")

    def _check_tikv(self) -> None:
        stores = self.pd_request("GET", "/pd/api/v1/stores").get("stores", [])
        expected = set(f"{service}:20160" for service in self.topology.role_services("tikv"))
        up = {
            item["store"]["address"]
            for item in stores
            if item.get("store", {}).get("state_name") == "Up"
        }
        if up != expected:
            raise RuntimeError(
                f"expected Up TiKV stores={sorted(expected)!r}, observed={sorted(up)!r}, stores={stores!r}"
            )

    def _check_tidb_sql(self, service: str) -> None:
        host, port = self.tidb_sql_endpoint(service)
        connection = pymysql.connect(
            host=host, port=port, user="root", password="", database="test",
            connect_timeout=5, read_timeout=10, write_timeout=10,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchall()
        finally:
            connection.close()

    def _check_downstream_sql(self, service: str) -> None:
        host, port = self.downstream_sql_endpoint(service)
        connection = pymysql.connect(
            host=host, port=port, user="root", password="",
            connect_timeout=5, read_timeout=10, write_timeout=10,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchall()
        finally:
            connection.close()

    # -- lifecycle control ---------------------------------------------------------

    def manage_service(self, action: str, service: str) -> None:
        """stop / start / restart one compose service (returns after compose, not cluster readiness)."""
        self.topology.service(service)
        if action not in ("stop", "start", "restart"):
            raise ValueError(f"Unsupported TiDB persistent service action: action={action!r}, service={service!r}")
        self._run(self._compose + [action, service], component=service, timeout=300)

    # -- reversible node resource limits -------------------------------------------

    def _observe_container_cpu_limit(self, service: str, container_id: str) -> dict[str, Any]:
        payload = self._run(
            [
                "docker", "inspect", container_id,
                "--format", "{{.HostConfig.NanoCpus}} {{.HostConfig.CpuQuota}} {{.HostConfig.CpuPeriod}}",
            ],
            component=service,
        )
        nano_cpus, cpu_quota, cpu_period = (int(value) for value in payload.split())
        return {
            "nano_cpus": nano_cpus,
            "cpus": nano_cpus / 1_000_000_000,
            "cpu_quota": cpu_quota,
            "cpu_period": cpu_period,
        }

    def _apply_container_cpu_limit(self, service: str, container_id: str, cpus: float) -> dict[str, Any]:
        self._run(["docker", "update", "--cpus", repr(cpus), container_id], component=service)
        observed = self._observe_container_cpu_limit(service, container_id)
        if abs(observed["cpus"] - cpus) > 1e-9:
            raise TiDBPersistentDeploymentError(
                f"TiDB persistent container CPU limit did not take effect: run_id={self.run_id!r}, "
                f"service={service!r}, requested_cpus={cpus!r}, observed={observed!r}"
            )
        return observed

    def _node_limit_evidence(
        self, node: PersistentTiDBNodePlan, action: str, observed: Mapping[str, Any], **changes: float
    ) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "action": action,
            "target": f"{node.role}/{node.service}",
            "service": node.service,
            "spec_cpus": node.cpus,
            **changes,
            **observed,
        }

    def set_node_cpu_limit(self, service: str, cpus: float) -> dict[str, Any]:
        """Apply a reversible container CPU limit to one topology node.

        The cgroup limit is verified against the container's live HostConfig and
        mirrored into ``node_cpu_limits`` so ``query_metrics("cpu", ...)`` percent
        normalization observes the throttled budget. Evidence is returned
        trace-shaped; ``clear_node_cpu_limit`` restores the compose-declared value.
        """
        if cpus <= 0:
            raise ValueError(f"TiDB persistent node CPU limit must be positive: service={service!r}, cpus={cpus!r}")
        node = self.topology.service(service)
        observed = self._apply_container_cpu_limit(service, self.service_container_id(service), cpus)
        self.node_cpu_limits[f"{node.role}/{service}"] = cpus
        return self._node_limit_evidence(node, "applied", observed, requested_cpus=cpus)

    def node_cpu_limit(self, service: str) -> dict[str, Any]:
        """Observe the current container CPU limit of one topology node."""
        node = self.topology.service(service)
        observed = self._observe_container_cpu_limit(service, self.service_container_id(service))
        return self._node_limit_evidence(node, "observed", observed)

    def clear_node_cpu_limit(self, service: str) -> dict[str, Any]:
        """Release an applied limit by restoring the compose-declared spec cpus."""
        node = self.topology.service(service)
        observed = self._apply_container_cpu_limit(service, self.service_container_id(service), node.cpus)
        self.node_cpu_limits[f"{node.role}/{service}"] = node.cpus
        return self._node_limit_evidence(node, "released", observed, restored_cpus=node.cpus)

    def teardown(self) -> None:
        """compose down -v, remove the run network, delete the run data dir."""
        errors: list[str] = []
        if self.compose_file.exists():
            try:
                self._run(self._compose + ["down", "--volumes", "--remove-orphans"], component="cluster", timeout=600)
            except Exception as exc:
                errors.append(f"compose down failed: {exc!r}")
        if self._network_created:
            try:
                self._run(["docker", "network", "rm", self.network_name], component="network")
                self._network_created = False
            except Exception as exc:
                errors.append(f"network removal failed: {exc!r}")
        self._deployed = False
        if self.data_dir.exists():
            try:
                self.remove_data()
            except Exception as exc:
                errors.append(f"data removal failed: {exc!r}")
        if errors:
            raise TiDBPersistentDeploymentError(
                f"TiDB persistent teardown reported errors: run_id={self.run_id!r}, errors={errors!r}"
            )
        if self._port_lease is not None:
            self._port_lease.close()
            self._port_lease = None

    def remove_data(self) -> None:
        """Remove the run data dir through a root one-shot container.

        Bind-mount data written by container-internal users (MySQL uid 999,
        TiFlash) is not host-user owned, so direct rmtree cannot remove it.
        """
        if not self.data_dir.exists():
            return
        self._run(
            [
                "docker", "run", "--rm",
                "-v", f"{self.data_dir}:/data",
                _NETWORK_TOOL_IMAGE,
                "sh", "-c", "rm -rf /data/* /data/..?* /data/.[!.]*",
            ],
            component="cleanup",
            timeout=600,
        )
        self.data_dir.rmdir()

    # -- module repr ---------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"TiDBPersistentDeployment(run_id={self.run_id!r}, port_base={self.port_base!r}, "
            f"roles={ {role: len(self.topology.role_services(role)) for role in _ROLES if self.topology.role_services(role)}!r} )"
        )
