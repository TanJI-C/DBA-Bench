from src.execution.deployments.tidb_components.snapshots import TiDBSnapshots
from src.execution.deployments.tidb_components.pd_recovery import TiDBPdRecovery
from src.execution.deployments.tidb_components.mvcc import TiDBMvcc
from src.execution.deployments.tidb_components.stores import TiDBStores
from src.execution.deployments.tidb_components.rollout import TiDBRollout
from src.execution.deployments.tidb_components.network import TiDBNetwork
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
import time
from typing import Optional, Dict, Any, List

import yaml

from src.execution.deployments.base import BaseDeployment
from src.execution.docker_network import create_tidb_network
from src.execution.host_ports import PORT_LEASE_ENV, claim_host_ports, reserve_host_ports
from src.project_paths import SOURCE_ROOT


from src.execution.deployments.tidb_support import _TiDBReadinessFatalError, _render_toml_sections


class TiDBDockerDeployment(BaseDeployment):
    """Run an isolated case-defined TiDB topology with Docker Compose."""
    MONITORING_IMAGES = (
        "prom/prometheus@sha256:f20d3127bf2876f4a1df76246fca576b41ddf1125ed1c546fbd8b16ea55117e6",
        "m.daocloud.io/gcr.io/cadvisor/cadvisor@sha256:f40e65878e25c2e78ea037f73a449527a0fb994e303dc3e34cb6b187b4b91435",
    )
    MIN_DISK_BYTES = 20 * 1024**3
    FIRST_TIDB_BOOTSTRAP_TIMEOUT = 900
    DEFAULT_FIRST_TIDB_READINESS_TIMEOUT = 300
    FOLLOWING_TIDB_READINESS_TIMEOUT = 300
    PROMETHEUS_READINESS_TIMEOUT = 120
    PROMETHEUS_READINESS_TARGET_BASELINE = 7
    PROMETHEUS_READINESS_SECONDS_PER_EXTRA_TARGET = 10
    PROMETHEUS_DISCOVERY_GRACE_SECONDS = 90
    GET_PROBE_RETRY_ATTEMPTS = 3
    GET_PROBE_RETRY_INTERVAL_SECONDS = 0.5

    def __init__(
        self,
        run_id: str,
        port_base: int = 4000,
        storage_key: Optional[str] = None,
        storage_root: Optional[str] = None,
        image_group_key: Optional[str] = None,
        tidb_readiness_timeout_sec: int = 1800,
        warm_tidb_readiness_timeout_sec: int = 300,
    ):
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", run_id):
            raise ValueError(f"Invalid TiDB run_id {run_id!r}; use lowercase letters, digits, '_' or '-'")
        self.run_id = run_id
        self.project_name = f"aiopsbench-{run_id}"
        self.network_subnet: str | None = None
        self._network_created = False
        self.port_base = port_base
        if storage_key is not None and not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", storage_key):
            raise ValueError(
                f"Invalid TiDB storage_key {storage_key!r}; use lowercase letters, digits, '_' or '-'"
            )
        if storage_key is not None and storage_root is None:
            raise ValueError(
                f"TiDB persistent storage requires storage_root: run_id={run_id!r}, storage_key={storage_key!r}"
            )
        if image_group_key is not None and not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", image_group_key):
            raise ValueError(
                f"Invalid TiDB image_group_key {image_group_key!r}; "
                "use lowercase letters, digits, '_' or '-'"
            )
        if storage_key is not None and image_group_key is not None:
            raise ValueError(
                f"TiDB storage_key and image_group_key are mutually exclusive: "
                f"run_id={run_id!r}, storage_key={storage_key!r}, image_group_key={image_group_key!r}"
            )
        if tidb_readiness_timeout_sec <= 0 or warm_tidb_readiness_timeout_sec <= 0:
            raise ValueError(
                "TiDB readiness timeouts must be positive: "
                f"cold={tidb_readiness_timeout_sec}, warm={warm_tidb_readiness_timeout_sec}"
            )
        self.tikv_shared_volume_root = None
        self.tidb_readiness_timeout_sec = tidb_readiness_timeout_sec
        self.warm_tidb_readiness_timeout_sec = warm_tidb_readiness_timeout_sec
        self._last_readiness_error = None
        root = str(SOURCE_ROOT)
        self.compose_template = os.path.join(
            root, "config", "docker", "tidb-docker", "docker-compose.yml"
        )
        self.topology = None
        self.release = None
        self.tikv_store_zones = ()
        self.pd_location_labels = ()
        self.tikv_config_writable = False
        self.tikv_io_rate_limit_strict = False
        self.pd_config_path = None
        self.replication_runtime = None
        self.upgrade_release = None
        self.pd_cpu_limit = 1.0
        self.NODES = {}
        self.COMPONENTS = {}
        self.database_nodes = ()
        self.active_tikv_services = set()
        self.tikv_memory_mb = 2048
        self.tidb_memory_mb = 1024
        self.node_cpu_limits = {}
        self.tidb_endpoints = {}
        self.prometheus_port = None
        self.lightning_scrape_target = None
        self._prometheus_shortfall_since: float | None = None
        self._deployment_reached_ready = False
        self.downstream_port = None
        self.ticdc_port = None
        self.ticdc_ports = {}
        self.runtime_dir = None
        self.compose_file = None
        self._container_ids = {}
        self._port_lease = None
        self._env = dict(os.environ)

        self.snapshots = TiDBSnapshots(self, storage_key, storage_root, image_group_key)
        self.pd_recovery = TiDBPdRecovery(self)
        self.mvcc = TiDBMvcc(self)
        self.stores = TiDBStores(self)
        self.rollout = TiDBRollout(self)
        self.network = TiDBNetwork(self)

    @property
    def primary_tidb_endpoint(self) -> tuple[str, int]:
        return "127.0.0.1", self.port_base

    @property
    def network_name(self) -> str:
        return f"{self.project_name}_default"

    def _port_block_span(self) -> int:
        span = self.topology.tidb_count * 2 + 1
        if self.replication_runtime is not None:
            span += 1 + self.replication_runtime.ticdc_count
        return span

    def _reserve_port_block(self) -> int:
        span = self._port_block_span()
        if PORT_LEASE_ENV in os.environ:
            self._port_lease = claim_host_ports(tuple(range(self.port_base, self.port_base + span)), owner=self.run_id)
        else:
            self._port_lease = reserve_host_ports(self.port_base, tuple(range(span)), owner=self.run_id,
                                                  step=span, owned_containers=())
        return min(self._port_lease.ports)

    def configure_runtime(self, runtime) -> None:
        if self.topology is not None:
            raise RuntimeError(f"TiDB runtime is already configured: run_id={self.run_id!r}")
        if runtime.image_group_key is not None:
            if self.snapshots.storage_key is not None:
                raise ValueError(
                    f"TiDB storage_key and runtime image_group_key are mutually exclusive: "
                    f"run_id={self.run_id!r}, storage_key={self.snapshots.storage_key!r}, "
                    f"image_group_key={runtime.image_group_key!r}"
                )
            if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", runtime.image_group_key):
                raise ValueError(
                    f"Invalid TiDB runtime image_group_key {runtime.image_group_key!r}; "
                    "use lowercase letters, digits, '_' or '-'"
                )
            if self.snapshots.image_group_key is not None and self.snapshots.image_group_key != runtime.image_group_key:
                raise ValueError(
                    f"TiDB image_group_key mismatch: run_id={self.run_id!r}, "
                    f"deployment={self.snapshots.image_group_key!r}, runtime={runtime.image_group_key!r}"
                )
            self.snapshots.image_group_key = runtime.image_group_key
        self.topology = runtime.topology
        if runtime.tikv_memory_mb <= 0:
            raise ValueError(
                f"TiKV memory limit must be positive: tikv_memory_mb={runtime.tikv_memory_mb}"
            )
        self.tikv_memory_mb = runtime.tikv_memory_mb
        self.release = runtime.release
        self.replication_runtime = runtime.replication
        self.tidb_memory_mb = runtime.tidb_memory_mb
        self.tikv_shared_volume_root = (
            Path(runtime.tikv_shared_volume_root).resolve()
            if runtime.tikv_shared_volume_root is not None
            else None
        )
        if self.tikv_shared_volume_root is not None:
            self.tikv_shared_volume_root.mkdir(parents=True, exist_ok=True)
        self.tikv_store_zones = tuple(runtime.tikv_store_zones)
        self.pd_location_labels = tuple(runtime.pd_location_labels)
        self.tikv_config_writable = runtime.tikv_config_writable
        self.tikv_io_rate_limit_strict = runtime.tikv_io_rate_limit_strict
        self.tikv_server_config_overrides = runtime.tikv_server_config_overrides
        if self.tikv_config_writable and self.snapshots.image_group_enabled:
            raise ValueError(
                "Writable TiKV config cannot use a shared image group config: "
                f"run_id={self.run_id!r}, image_group_key={self.snapshots.image_group_key!r}"
            )
        if self.tikv_store_zones and len(self.tikv_store_zones) != self.topology.tikv_count:
            raise ValueError(
                "TiDB runtime TikKV zone count must match topology: "
                f"run_id={self.run_id!r}, zones={self.tikv_store_zones!r}, "
                f"tikv_count={self.topology.tikv_count}"
            )
        if self.tikv_store_zones and self.snapshots.image_group_enabled:
            raise ValueError(
                "TiDB per-store labels cannot use an image group with one shared TiKV config: "
                f"run_id={self.run_id!r}, image_group_key={self.snapshots.image_group_key!r}"
            )
        self.snapshots.bootstrap_cache_enabled = runtime.bootstrap_cache_enabled
        self._container_ids.clear()
        if self.tidb_readiness_timeout_sec == 1800:
            self.tidb_readiness_timeout_sec = runtime.readiness_timeout_seconds
        self.upgrade_release = runtime.upgrade_release
        self.pd_cpu_limit = runtime.pd_cpu_limit
        self.port_base = self._reserve_port_block()
        topology = self.topology
        self.COMPONENTS = {
            node_type: tuple(f"{node_type}-{index}" for index in range(topology.count(node_type)))
            for node_type in ("pd", "tikv", "tidb", "tiflash")
        }
        self.COMPONENTS["monitoring"] = ("prometheus", "cadvisor")
        if self.replication_runtime is not None:
            self.COMPONENTS["ticdc"] = tuple(
                f"ticdc-{index}" for index in range(self.replication_runtime.ticdc_count)
            )
            self.COMPONENTS["downstream"] = ("mysql-0",)
        node_types = ["pd", "tikv", "tidb", "tiflash"]
        if self.replication_runtime is not None:
            node_types.extend(("ticdc", "downstream"))
        self.NODES = {
            f"{node_type}/{service}": service
            for node_type in node_types
            for service in self.COMPONENTS[node_type]
        }
        self.NODES.update({
            "monitoring/prometheus-0": "prometheus",
            "monitoring/cadvisor-0": "cadvisor",
        })
        self.database_nodes = tuple(
            target
            for node_type in ("pd", "tikv", "tidb", "tiflash")
            for target in (f"{node_type}/{service}" for service in self.COMPONENTS[node_type])
        )
        self.active_tikv_services = set(
            self.COMPONENTS["tikv"][:topology.initial_tikv_count]
        )
        self.tidb_endpoints = {
            f"tidb/tidb-{index}": ("127.0.0.1", self.port_base + index * 2)
            for index in range(topology.tidb_count)
        }
        self.prometheus_port = self.port_base + topology.tidb_count * 2
        if self.replication_runtime is not None:
            self.downstream_port = self.prometheus_port + 1
            self.ticdc_ports = {
                f"ticdc/{service}": self.prometheus_port + 2 + index
                for index, service in enumerate(self.COMPONENTS["ticdc"])
            }
            self.ticdc_port = self.ticdc_ports["ticdc/ticdc-0"]
        self.runtime_dir = tempfile.mkdtemp(prefix=f"aiopsbench-tidb-{self.run_id}-")
        self.compose_file = os.path.join(self.runtime_dir, "docker-compose.yml")
        if self.snapshots.image_group_enabled:
            self.snapshots._configure_image_group()
        else:
            self.snapshots._configure_bootstrap_cache()
        if self.snapshots.storage_key is not None:
            self.snapshots._persistent_base_dir = self.snapshots.storage_root / self.snapshots.storage_key
            self.snapshots._persistent_baseline_dir = self.snapshots._persistent_base_dir / "baseline"
            self.snapshots._persistent_run_dir = self.snapshots._persistent_base_dir / "runs" / self.run_id
            self.snapshots._persistent_run_dir.mkdir(parents=True, exist_ok=True)
        self.stores._maintenance_audit = []
        self._render_runtime_files()


    def _release_images(self) -> tuple[str, ...]:
        if self.release is None:
            raise RuntimeError(f"TiDB release is not configured: run_id={self.run_id!r}")
        images = (
            self.release.pd_image,
            self.release.tikv_image,
            self.release.tidb_image,
        )
        if self.topology.tiflash_count:
            return (*images, self.release.tiflash_image)
        return images

    def _upgrade_release_images(self) -> tuple[str, ...]:
        if self.upgrade_release is None:
            return ()
        images = (
            self.upgrade_release.pd_image,
            self.upgrade_release.tikv_image,
            self.upgrade_release.tidb_image,
        )
        if self.topology.tiflash_count:
            return (*images, self.upgrade_release.tiflash_image)
        return images

    def _runtime_database_images(self) -> tuple[str, ...]:
        if self.release is None:
            raise RuntimeError(f"TiDB release is not configured: run_id={self.run_id!r}")
        if self.snapshots.image_group_selected:
            images = (
                *(self.snapshots.image_group_images[service] for service in self.COMPONENTS["pd"]),
                *(self.snapshots.image_group_images[service] for service in self.COMPONENTS["tikv"]),
                self.release.tidb_image,
                *(([self.release.tiflash_image]) if self.topology.tiflash_count else []),
            )
        else:
            images = self._release_images()
        if self.replication_runtime is not None:
            images = (*images, self.replication_runtime.ticdc_image, self.replication_runtime.downstream_image)
        return images

    def _component_image(self, node_type: str, service: str) -> str:
        override = self.rollout._component_image_overrides.get(service)
        if override is not None:
            return override
        if self.snapshots.image_group_selected and node_type in {"pd", "tikv"}:
            return self.snapshots.image_group_images[service]
        return {
            "pd": self.release.pd_image,
            "tikv": self.release.tikv_image,
            "tidb": self.release.tidb_image,
            "tiflash": self.release.tiflash_image,
        }[node_type]


    @staticmethod
    def _absolute_volumes(volumes: list[str], config_dir: str) -> list[str]:
        return [
            f"{os.path.join(config_dir, volume[2:].split(':', 1)[0])}:{volume.split(':', 1)[1]}"
            if volume.startswith("./") else volume
            for volume in volumes
        ]

    def _worker_cpuset(self) -> tuple[str, str] | None:
        cpuset_cpus = self._env.get("AIOPS_CPUSET_CPUS")
        cpuset_mems = self._env.get("AIOPS_CPUSET_MEMS")
        if bool(cpuset_cpus) != bool(cpuset_mems):
            raise RuntimeError(
                "TiDB worker cpuset requires both resource variables: "
                f"run_id={self.run_id!r}, AIOPS_CPUSET_CPUS={cpuset_cpus!r}, "
                f"AIOPS_CPUSET_MEMS={cpuset_mems!r}"
            )
        return (cpuset_cpus, cpuset_mems) if cpuset_cpus else None

    def _apply_worker_numa_binding(self) -> None:
        worker_cpuset = self._worker_cpuset()
        if worker_cpuset is None:
            return
        _, cpuset_mems = worker_cpuset
        for service in sorted(set(self.NODES.values())):
            container_id = self._service_container_id(service)
            self._run(
                ["docker", "update", "--cpuset-mems", cpuset_mems, container_id],
                service,
            )

    def _render_runtime_files(self) -> None:
        with open(self.compose_template, encoding="utf-8") as handle:
            template = yaml.safe_load(handle)
        if self.release is None:
            raise RuntimeError(f"TiDB release is not configured: run_id={self.run_id!r}")
        template["x-pd"]["image"] = self.release.pd_image
        template["x-tikv"]["image"] = self.release.tikv_image
        template["x-tidb"]["image"] = self.release.tidb_image
        if self.release.tiflash_image is not None:
            template["x-tiflash"]["image"] = self.release.tiflash_image
        config_dir = os.path.dirname(self.compose_template)
        pd_addresses = ",".join(f"{service}:2379" for service in self.COMPONENTS["pd"])
        initial_cluster = ",".join(
            f"{service}=http://{service}:2380" for service in self.COMPONENTS["pd"]
        )
        services = {}
        volumes = {}

        self.pd_config_path = None
        if self.pd_location_labels:
            base_pd_config_path = os.path.join(config_dir, "config", "pd.toml")
            base_pd_config = Path(base_pd_config_path).read_text(encoding="utf-8")
            if "[replication]" not in base_pd_config or "location-labels" in base_pd_config:
                raise RuntimeError(
                    f"TiDB PD base config cannot receive runtime location labels: "
                    f"run_id={self.run_id!r}, path={base_pd_config_path!r}"
                )
            labels = ", ".join(json.dumps(label) for label in self.pd_location_labels)
            self.pd_config_path = os.path.join(self.runtime_dir, "pd.toml")
            Path(self.pd_config_path).write_text(
                base_pd_config.replace(
                    "[replication]\n",
                    f"[replication]\nlocation-labels = [{labels}]\n",
                    1,
                ),
                encoding="utf-8",
            )

        for service in self.COMPONENTS["pd"]:
            node = deepcopy(template["x-pd"])
            node["image"] = self._component_image("pd", service)
            node["cpus"] = self.pd_cpu_limit
            node["volumes"] = self._absolute_volumes(node["volumes"], config_dir)
            if self.pd_location_labels:
                node["volumes"] = [
                    (
                        f"{self.pd_config_path}:/pd.toml:ro"
                        if volume.split(":", 1)[1] == "/pd.toml:ro"
                        else volume
                    )
                    for volume in node["volumes"]
                ]
            # PD 的 /data/pd 一律落到真实数据目录：tmpfs 在容器重启后被清空，
            # SF01 等场景注入器的 PD stop/start 会因数据丢失而无法重新加入集群；
            # 构建期 commit 本就不会捕获 tmpfs 内容，改用 bind mount 不改变镜像语义。
            node.pop("tmpfs", None)
            if self.snapshots.persistent_storage_enabled:
                node["volumes"].append(f"{self.snapshots._persistent_run_dir / service}:/data/pd")
            elif not self.snapshots.image_group_enabled:
                pd_data_path = self.snapshots.bootstrap_data_paths[("pd", service)]
                node["volumes"].append(f"{pd_data_path}:/data/pd")
            # image group 构建/使用期 PD 数据留在容器可写层：bind mount 与 tmpfs
            # 都不会被 docker commit 捕获，group 镜像里的 PD 会以空数据重新
            # bootstrap 出新 cluster ID，与 TiKV 镜像层数据失配后拒绝启动。
            node["init"] = True
            # image group 构建/使用期 PD 以 root 运行：数据在容器可写层，不产生
            # 宿主目录属主问题；bind mount 路径（persistent/cache）仍以宿主用户
            # 运行，避免 runtime_dir 清理被 root 属主文件挡住。
            node["user"] = (
                "0:0"
                if self.snapshots.image_group_enabled
                else f"{os.getuid()}:{os.getgid()}"
            )
            node["command"] = [
                f"--name={service}", "--data-dir=/data/pd",
                "--client-urls=http://0.0.0.0:2379", "--peer-urls=http://0.0.0.0:2380",
                f"--advertise-client-urls=http://{service}:2379",
                f"--advertise-peer-urls=http://{service}:2380",
                f"--initial-cluster={initial_cluster}", "--config=/pd.toml", "--log-file=",
            ]
            services[service] = node

        if self.replication_runtime is not None:
            downstream = deepcopy(template["x-downstream"])
            downstream["image"] = self.replication_runtime.downstream_image
            downstream["ports"] = [f"{self.downstream_port}:3306"]
            downstream["environment"] = {"MYSQL_ALLOW_EMPTY_PASSWORD": "yes"}
            downstream["command"] = [
                "--default-time-zone=+08:00",
                "--character-set-server=utf8mb4",
                "--collation-server=utf8mb4_bin",
            ]
            services["mysql-0"] = downstream

            for index, service in enumerate(self.COMPONENTS["ticdc"]):
                target = f"ticdc/{service}"
                ticdc = deepcopy(template["x-ticdc"])
                ticdc["image"] = self.replication_runtime.ticdc_image
                ticdc["ports"] = [f"{self.ticdc_ports[target]}:8300"]
                ticdc["depends_on"] = [*self.COMPONENTS["pd"], *self.COMPONENTS["tidb"], "mysql-0"]
                ticdc["command"] = [
                    "/cdc",
                    "server",
                    "--addr=0.0.0.0:8300",
                    f"--advertise-addr={service}:8300",
                    f"--pd={','.join(f'http://{service}:2379' for service in self.COMPONENTS['pd'])}",
                    "--data-dir=/tmp/cdc",
                    "--gc-ttl=86400",
                    "--tz=Asia/Shanghai",
                    "--log-file=",
                ]
                if self.replication_runtime.ticdc_cluster_ids:
                    ticdc["command"].append(
                        f"--cluster-id={self.replication_runtime.ticdc_cluster_ids[index]}"
                    )
                services[service] = ticdc

        for service in self.COMPONENTS["tikv"]:
            node = deepcopy(template["x-tikv"])
            node["image"] = self._component_image("tikv", service)
            node["volumes"] = self._absolute_volumes(node["volumes"], config_dir)
            tikv_config_command_path = "/tikv.toml"
            if (
                self.tikv_config_writable
                or self.tikv_store_zones
                or self.tikv_io_rate_limit_strict
                or self.tikv_server_config_overrides
            ):
                tikv_config_dir = os.path.join(self.runtime_dir, f"{service}-config")
                Path(tikv_config_dir).mkdir(parents=True, exist_ok=True)
                tikv_config_path = os.path.join(tikv_config_dir, "tikv.toml")
                base_config = Path(os.path.join(config_dir, "config", "tikv.toml")).read_text(encoding="utf-8")
                if "[server]" in base_config:
                    raise RuntimeError(
                        f"TiKV base config already has a [server] section: run_id={self.run_id!r}, "
                        f"path={os.path.join(config_dir, 'config', 'tikv.toml')!r}"
                    )
                if self.tikv_io_rate_limit_strict:
                    marker = "[storage.io-rate-limit]\n"
                    if marker in base_config:
                        base_config = base_config.replace(
                            marker,
                            f"{marker}strict = true\n",
                            1,
                        )
                    else:
                        base_config = f"{base_config.rstrip()}\n\n{marker}strict = true\n"
                if self.tikv_store_zones:
                    zone = self.tikv_store_zones[self.COMPONENTS["tikv"].index(service)]
                    base_config = (
                        f'{base_config.rstrip()}\n\n[server]\nlabels = {{ zone = "{zone}", region = "{zone}" }}\n'
                    )
                if self.tikv_server_config_overrides:
                    base_config = base_config.rstrip() + "\n\n" + _render_toml_sections(
                        self.tikv_server_config_overrides
                    )
                Path(tikv_config_path).write_text(base_config, encoding="utf-8")
                node["volumes"] = [
                    (
                        (
                            f"{tikv_config_dir}:/tikv-config:rw"
                            if self.tikv_config_writable
                            else f"{tikv_config_path}:/tikv.toml:ro"
                        )
                        if volume.split(":", 1)[1] == "/tikv.toml:ro"
                        else volume
                    )
                    for volume in node["volumes"]
                ]
                if self.tikv_config_writable:
                    tikv_config_command_path = "/tikv-config/tikv.toml"
            if self.snapshots.image_group_enabled:
                node["volumes"] = [
                    (
                        f"{self.snapshots.image_group_tikv_config_path}:/tikv.toml:ro"
                        if volume.split(":", 1)[1] == "/tikv.toml:ro"
                        else volume
                    )
                    for volume in node["volumes"]
                ]
            if not self.snapshots.image_group_enabled:
                if self.snapshots.persistent_storage_enabled:
                    node["volumes"].append(f"{self.snapshots._persistent_run_dir / service}:/data/tikv")
                else:
                    tikv_data_path = self.snapshots.bootstrap_data_paths[("tikv", service)]
                    node["volumes"].append(f"{tikv_data_path}:/data/tikv")
            if self.tikv_shared_volume_root is not None:
                node["volumes"].append(f"{self.tikv_shared_volume_root}:/backup")
            node["mem_limit"] = f"{self.tikv_memory_mb}m"
            node["memswap_limit"] = f"{self.tikv_memory_mb}m"
            node["init"] = True
            node["user"] = "0:0" if self.snapshots.image_group_enabled else f"{os.getuid()}:{os.getgid()}"
            node["command"] = [
                "--addr=0.0.0.0:20160", f"--advertise-addr={service}:20160",
                "--status-addr=0.0.0.0:20180", f"--advertise-status-addr={service}:20180",
                f"--pd={pd_addresses}", "--data-dir=/data/tikv", f"--config={tikv_config_command_path}", "--log-file=",
            ]
            services[service] = node

        if self.COMPONENTS["tiflash"]:
            tiflash_config_path = os.path.join(self.runtime_dir, "tiflash.toml")
            tiflash_proxy_path = os.path.join(self.runtime_dir, "tiflash-proxy.toml")
            tiflash_name = self.COMPONENTS["tiflash"][0]
            with open(tiflash_proxy_path, "w", encoding="utf-8") as handle:
                handle.write(
                    "[security]\nca-path = \"\"\ncert-path = \"\"\nkey-path = \"\"\n\n"
                    "[storage]\nreserve-space = \"0\"\n\n"
                    "[raftstore]\ncapacity = \"8GB\"\n"
                )
            with open(tiflash_config_path, "w", encoding="utf-8") as handle:
                handle.write(
                    "tmp_path = \"/tmp/tiflash/data/tmp\"\n"
                    "path = \"/tmp/tiflash/data/db\"\n"
                    "capacity = \"8589934592\"\n"
                    "mark_cache_size = 268435456\nminmax_index_cache_size = 268435456\n"
                    "tcp_port = 9000\nhttp_port = 8123\n\n"
                    "[flash]\nservice_addr = \"0.0.0.0:3930\"\n"
                    "[flash.flash_cluster]\nupdate_rule_interval = 5\n"
                    "[flash.proxy]\naddr = \"0.0.0.0:20170\"\n"
                    f"advertise-addr = \"{tiflash_name}:20170\"\n"
                    "data-dir = \"/data/proxy\"\nconfig = \"/proxy.toml\"\nlog-file = \"\"\n"
                    f"engine-addr = \"{tiflash_name}:3930\"\nstatus-addr = \"0.0.0.0:20181\"\n"
                    f"advertise-status-addr = \"{tiflash_name}:20181\"\n\n"
                    "[logger]\ncount = 3\nerrorlog = \"\"\nlog = \"\"\nlevel = \"info\"\n\n"
                    "[application]\nrunAsDaemon = false\n\n"
                    f"[raft]\npd_addr = \"{pd_addresses}\"\nignore_databases = \"system,default\"\n\n"
                    "[profiles]\n[profiles.default]\n"
                )
            for service in self.COMPONENTS["tiflash"]:
                node = deepcopy(template["x-tiflash"])
                node["image"] = self.release.tiflash_image
                node["volumes"] = [
                    f"{tiflash_config_path}:/config.toml:ro",
                    f"{tiflash_proxy_path}:/proxy.toml:ro",
                ]
                node["depends_on"] = [*self.COMPONENTS["pd"], *self.COMPONENTS["tikv"]]
                services[service] = node

        for index, service in enumerate(self.COMPONENTS["tidb"]):
            node = deepcopy(template["x-tidb"])
            node["image"] = self._component_image("tidb", service)
            # 与 tidb_runtime 的 CPU 预算（tidb_count * 1）对齐：模板默认 2.0 会让
            # 大拓扑（如 5 TiDB 的滚动升级）超出 worker cpuset，CFS 限流把启动期
            # 的 PD/TiKV gRPC 打穿 deadline。
            node["cpus"] = 1.0
            node["init"] = True
            node["mem_limit"] = f"{self.tidb_memory_mb}m"
            node["memswap_limit"] = f"{self.tidb_memory_mb}m"
            node["volumes"] = self._absolute_volumes(
                ["./config/tidb.toml:/tidb.toml:ro"], config_dir
            )
            node["ports"] = [
                f"{self.port_base + index * 2}:4000",
                f"{self.port_base + index * 2 + 1}:10080",
            ]
            node["command"] = [
                "--config=/tidb.toml", "--store=tikv", f"--path={pd_addresses}", "--host=0.0.0.0",
                f"--advertise-address={service}", "--status=10080",
                *self.release.tidb_extra_args, "--log-file=",
            ]
            services[service] = node

        prometheus_config = {
            "global": {"scrape_interval": "2s", "evaluation_interval": "2s"},
            "scrape_configs": [
                {"job_name": "pd", "static_configs": [{"targets": [f"{node}:2379" for node in self.COMPONENTS["pd"]]}]},
                {"job_name": "tikv", "static_configs": [{"targets": [f"{node}:20180" for node in self.COMPONENTS["tikv"]]}]},
                {"job_name": "tidb", "static_configs": [{"targets": [f"{node}:10080" for node in self.COMPONENTS["tidb"]]}]},
                {"job_name": "cadvisor", "scrape_interval": "5s", "scrape_timeout": "4s", "static_configs": [{"targets": ["cadvisor:8080"]}]},
            ],
        }
        if self.COMPONENTS.get("ticdc"):
            prometheus_config["scrape_configs"].insert(
                3,
                {"job_name": "ticdc", "static_configs": [{"targets": [f"{node}:8300" for node in self.COMPONENTS["ticdc"]]}]},
            )
        if self.COMPONENTS["tiflash"]:
            prometheus_config["scrape_configs"].insert(
                3,
                {"job_name": "tiflash", "static_configs": [{"targets": [f"{node}:8234" for node in self.COMPONENTS["tiflash"]]}]},
            )
        if self.lightning_scrape_target:
            prometheus_config["scrape_configs"].append(
                {"job_name": "lightning", "static_configs": [{"targets": [self.lightning_scrape_target]}]}
            )
        prometheus_config_path = os.path.join(self.runtime_dir, "prometheus.yml")
        with open(prometheus_config_path, "w", encoding="utf-8") as handle:
            yaml.safe_dump(prometheus_config, handle, sort_keys=False)

        prometheus = deepcopy(template["services"]["prometheus"])
        prometheus["init"] = True
        prometheus["ports"] = [f"{self.prometheus_port}:9090"]
        prometheus["volumes"] = [f"{prometheus_config_path}:/etc/prometheus/prometheus.yml:ro"]
        services["prometheus"] = prometheus
        services["cadvisor"] = deepcopy(template["services"]["cadvisor"])
        services["cadvisor"]["init"] = True
        worker_cpuset = self._worker_cpuset()
        if worker_cpuset is not None:
            cpuset_cpus, cpuset_mems = worker_cpuset
            for service in services.values():
                service["cpuset"] = cpuset_cpus
        with open(self.compose_file, "w", encoding="utf-8") as handle:
            yaml.safe_dump(
                {
                    "services": services,
                    "volumes": volumes,
                    "networks": {
                        "default": {
                            "name": self.network_name,
                            "external": True,
                        }
                    },
                },
                handle,
                sort_keys=False,
            )

        self.node_cpu_limits = {
            target: float(services[service]["cpus"])
            for target, service in self.NODES.items()
        }

    @staticmethod
    def _memory_bytes(value: str) -> int:
        units = {"m": 1024**2, "g": 1024**3}
        return int(float(value[:-1]) * units[value[-1].lower()])

    def _required_resources(self) -> tuple[int, int]:
        with open(self.compose_file, encoding="utf-8") as handle:
            services = yaml.safe_load(handle)["services"]
        cpus = math.ceil(sum(float(service["cpus"]) for service in services.values()))
        memory = sum(self._memory_bytes(service["mem_limit"]) for service in services.values())
        return cpus, memory

    @property
    def _compose(self) -> List[str]:
        if "DOCKER_ROOT_DIR" not in self._env:
            self._docker_info()
        return [
            "docker", "compose", "--project-name", self.project_name,
            "--file", self.compose_file,
        ]

    def _run(self, cmd: List[str], component: str = "cluster") -> str:
        result = subprocess.run(cmd, capture_output=True, text=True, env=self._env)
        if result.returncode != 0:
            raise RuntimeError(
                f"TiDB command failed: run_id={self.run_id!r}, component={component!r}, "
                f"command={shlex.join(cmd)!r}, returncode={result.returncode}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )
        return result.stdout

    def _get_probe(self, cmd: List[str], component: str) -> str:
        """Retry a read-only container probe across transient 5xx windows.

        Readiness gates already tolerate the same conditions through _wait;
        a single-shot wget from scenario setup/verify/evaluation would
        otherwise turn a sub-second PD leader transition into an
        infrastructure_failure.
        """
        last_error = None
        for _ in range(self.GET_PROBE_RETRY_ATTEMPTS):
            try:
                return self._run(cmd, component)
            except RuntimeError as error:
                last_error = error
                time.sleep(self.GET_PROBE_RETRY_INTERVAL_SECONDS)
        raise last_error

    def preflight(self):
        if self.topology is None:
            raise RuntimeError(f"TiDB topology is not configured: run_id={self.run_id!r}")
        if not os.path.isfile(self.compose_file):
            raise FileNotFoundError(f"TiDB compose file not found: run_id={self.run_id!r}, path={self.compose_file!r}")
        self._run(["docker", "version"], "docker")
        self._run(["docker", "compose", "version"], "compose")
        required_images = (
            *self._runtime_database_images(),
            *self._upgrade_release_images(),
            *self.MONITORING_IMAGES,
        )
        missing = [
            image for image in required_images
            if subprocess.run(
                ["docker", "image", "inspect", image], capture_output=True, env=self._env
            ).returncode != 0
        ]
        if missing:
            raise RuntimeError(f"TiDB preflight missing images: run_id={self.run_id!r}, images={missing}")
        info = self._docker_info()
        cpus, memory_bytes, docker_root = int(info[0]), int(info[1]), info[2]
        disk_bytes = shutil.disk_usage(docker_root).free
        required_cpus, required_memory_bytes = self._required_resources()
        if cpus < required_cpus or memory_bytes < required_memory_bytes or disk_bytes < self.MIN_DISK_BYTES:
            raise RuntimeError(
                f"TiDB preflight resources insufficient: run_id={self.run_id!r}, "
                f"actual_cpus={cpus}, required_cpus={required_cpus}, "
                f"actual_memory_bytes={memory_bytes}, required_memory_bytes={required_memory_bytes}, "
                f"actual_disk_bytes={disk_bytes}, required_disk_bytes={self.MIN_DISK_BYTES}"
            )
        self._run(self._compose + ["config", "--quiet"], "compose")

    def _docker_info(self) -> List[str]:
        info = self._run(
            ["docker", "info", "--format", "{{.NCPU}} {{.MemTotal}} {{.DockerRootDir}}"],
            "docker",
        ).split()
        self._env["DOCKER_ROOT_DIR"] = info[2]
        return info

    def _project_exists(self) -> bool:
        return bool(self._run(self._compose + ["ps", "--all", "--quiet"], "compose").strip())

    def _ensure_network(self) -> None:
        if self._network_created:
            return
        self.network_subnet = create_tidb_network(self.network_name, env=self._env)
        self._network_created = True


    def _service_container_id(self, service: str) -> str:
        cached = self._container_ids.get(service)
        if cached is not None:
            return cached
        container_id = self._run(self._compose + ["ps", "--all", "--quiet", service], service).strip()
        if not container_id:
            raise RuntimeError(
                f"TiDB container not found: run_id={self.run_id!r}, component={service!r}"
            )
        self._container_ids[service] = container_id
        return container_id

    def current_pd_leader(self) -> str:
        pd0_container_id = self._service_container_id("pd-0")
        leader_payload = json.loads(
            self._get_probe(
                [
                    "docker", "exec", pd0_container_id, "wget", "-qO-", "-T", "5",
                    "http://127.0.0.1:2379/pd/api/v1/leader",
                ],
                "pd-0",
            )
        )
        leader_service = leader_payload["name"]
        if leader_service not in self.COMPONENTS["pd"]:
            raise RuntimeError(
                f"PD leader is outside the configured topology: run_id={self.run_id!r}, "
                f"leader={leader_service!r}, configured={self.COMPONENTS['pd']!r}"
            )
        return leader_service

    def transfer_pd_leader(self, destination_service: str) -> None:
        if destination_service not in self.COMPONENTS["pd"]:
            raise ValueError(
                f"Unknown PD leader transfer destination: destination_service={destination_service!r}, "
                f"configured={self.COMPONENTS['pd']!r}"
            )
        self.pd_request("POST", "/pd/api/v1/leader/transfer", {"name": destination_service})

    def pd_request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Any:
        if method not in {"GET", "POST", "DELETE"}:
            raise ValueError(f"Unsupported PD API method: method={method!r}, path={path!r}")
        if not path.startswith("/pd/api/v1/"):
            raise ValueError(f"PD API path must stay under /pd/api/v1/: path={path!r}")
        if method == "GET" and body is not None:
            raise ValueError(f"GET PD API request cannot contain a payload: path={path!r}")
        if method != "GET":
            leader_service = self.current_pd_leader()
            container_id = self._service_container_id(leader_service)
            command = ["docker", "exec", container_id, "wget", "-qO-", "-T", "5"]
            command.extend([f"--method={method}", "--header=Content-Type: application/json"])
            if body is not None:
                command.append(f"--body-data={json.dumps(body, separators=(',', ':'))}")
            command.append(f"http://127.0.0.1:2379{path}")
            output = self._run(command, leader_service)
            output = output.strip()
            if not output:
                raise RuntimeError(
                    f"PD API returned an empty response: run_id={self.run_id!r}, method={method!r}, path={path!r}"
                )
            return json.loads(output)
        # Observation-only GETs re-resolve the leader on every attempt so a
        # leadership transition inside the retry window cannot pin a stale node.
        last_error = None
        for _ in range(self.GET_PROBE_RETRY_ATTEMPTS):
            try:
                leader_service = self.current_pd_leader()
                container_id = self._service_container_id(leader_service)
                command = ["docker", "exec", container_id, "wget", "-qO-", "-T", "5"]
                command.append(f"http://127.0.0.1:2379{path}")
                output = self._get_probe(command, leader_service).strip()
                if not output:
                    raise RuntimeError(
                        f"PD API returned an empty response: run_id={self.run_id!r}, method={method!r}, path={path!r}"
                    )
                return json.loads(output)
            except (RuntimeError, json.JSONDecodeError) as error:
                last_error = error
                time.sleep(self.GET_PROBE_RETRY_INTERVAL_SECONDS)
        raise last_error

    def _pd_json(self, path: str) -> Any:
        return self.pd_request("GET", path)

    def gc_safepoint_list(self) -> dict[str, object]:
        payload = self.pd_request("GET", "/pd/api/v1/gc/safepoint")
        if not isinstance(payload, dict) or not isinstance(payload.get("service_gc_safe_points"), list):
            raise RuntimeError(
                "PD service GC safepoint response is malformed: "
                f"run_id={self.run_id!r}, payload={payload!r}"
            )
        if "gc_safe_point" not in payload:
            raise RuntimeError(
                "PD service GC safepoint response has no global safepoint: "
                f"run_id={self.run_id!r}, payload={payload!r}"
            )
        return payload

    def gc_safepoint_remove(self, service_id: str) -> dict[str, object]:
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", service_id) is None:
            raise ValueError(f"Invalid PD service GC safepoint id: service_id={service_id!r}")
        output = self.pd_request("DELETE", f"/pd/api/v1/gc/safepoint/{service_id}")
        return {"service_id": service_id, "output": output}

    def changefeed_diagnostics(
        self,
        capture_target: str,
        changefeed_id: str | None = None,
    ) -> dict[str, object]:
        if capture_target not in self.NODES or not capture_target.startswith("ticdc/"):
            raise ValueError(
                "TiCDC diagnostics requires a discovered capture target: "
                f"capture_target={capture_target!r}, expected={sorted(target for target in self.NODES if target.startswith('ticdc/'))!r}"
            )
        if changefeed_id is not None and re.fullmatch(r"[a-z0-9][a-z0-9_-]*", changefeed_id) is None:
            raise ValueError(f"Invalid TiCDC changefeed_id: changefeed_id={changefeed_id!r}")
        path = "/api/v1/changefeeds"
        if changefeed_id is not None:
            path += f"/{changefeed_id}"
        output = self._get_probe(
            self._exec_command(capture_target, ["wget", "-qO-", "-T", "5", f"http://127.0.0.1:8300{path}"]),
            capture_target,
        )
        payload = json.loads(output)
        if changefeed_id is None and not isinstance(payload, list):
            raise RuntimeError(
                "TiCDC changefeed list response is malformed: "
                f"run_id={self.run_id!r}, capture_target={capture_target!r}, payload={payload!r}"
            )
        if changefeed_id is not None and not isinstance(payload, dict):
            raise RuntimeError(
                "TiCDC changefeed response is malformed: "
                f"run_id={self.run_id!r}, capture_target={capture_target!r}, changefeed_id={changefeed_id!r}, payload={payload!r}"
            )
        return {"capture_target": capture_target, "changefeed_id": changefeed_id, "changefeeds": payload}

    def remove_changefeed(self, capture_target: str, changefeed_id: str) -> dict[str, object]:
        if capture_target not in self.NODES or not capture_target.startswith("ticdc/"):
            raise ValueError(
                "TiCDC cleanup requires a discovered capture target: "
                f"capture_target={capture_target!r}"
            )
        if re.fullmatch(r"[a-z0-9][a-z0-9_-]*", changefeed_id) is None:
            raise ValueError(f"Invalid TiCDC changefeed_id: changefeed_id={changefeed_id!r}")
        output = self.exec(
            capture_target,
            [
                "/cdc", "cli", "changefeed", "remove",
                "--server=http://127.0.0.1:8300",
                f"--changefeed-id={changefeed_id}",
            ],
        )
        return {"capture_target": capture_target, "changefeed_id": changefeed_id, "output": output.strip()}

    def set_ticdc_memory_limit(self, target: str, memory_mb: int) -> dict[str, object]:
        if target not in self.NODES or not target.startswith("ticdc/"):
            raise ValueError(
                f"TiCDC memory limit requires a TiCDC target: target={target!r}, "
                f"expected={tuple(item for item in self.NODES if item.startswith('ticdc/'))!r}"
            )
        if not isinstance(memory_mb, int) or isinstance(memory_mb, bool) or memory_mb <= 0:
            raise ValueError(f"TiCDC memory limit must be a positive integer: target={target!r}, memory_mb={memory_mb!r}")
        service = self.NODES[target]
        container = self._service_container_id(service)
        previous = subprocess.run(
            ["docker", "inspect", "--format", "{{.HostConfig.Memory}}", container],
            capture_output=True,
            text=True,
            env=self._env,
        )
        if previous.returncode != 0:
            raise RuntimeError(
                "TiCDC memory limit inspection failed: "
                f"run_id={self.run_id!r}, target={target!r}, container={container!r}, "
                f"stdout={previous.stdout.strip()!r}, stderr={previous.stderr.strip()!r}"
            )
        previous_bytes = int(previous.stdout.strip())
        requested_bytes = memory_mb * 1024 * 1024
        updated = subprocess.run(
            ["docker", "update", "--memory", str(requested_bytes), "--memory-swap", str(requested_bytes), container],
            capture_output=True,
            text=True,
            env=self._env,
        )
        if updated.returncode != 0:
            raise RuntimeError(
                "TiCDC memory limit update failed: "
                f"run_id={self.run_id!r}, target={target!r}, container={container!r}, memory_mb={memory_mb}, "
                f"stdout={updated.stdout.strip()!r}, stderr={updated.stderr.strip()!r}"
            )
        return {
            "target": target,
            "container": container,
            "previous_memory_bytes": previous_bytes,
            "memory_bytes": requested_bytes,
            "memory_mb": memory_mb,
        }


    def clock_status_observation(self) -> dict[str, object]:
        states = self.node_states()
        observations = []
        for target, state in states.items():
            if not target.startswith(("pd/", "tikv/", "tidb/")):
                continue
            if not state["running"]:
                observations.append({"target": target, "running": False})
                continue
            before_ms = time.time_ns() // 1_000_000
            observed_ms = int(self.exec(target, ["date", "+%s%3N"]).strip())
            after_ms = time.time_ns() // 1_000_000
            midpoint_ms = (before_ms + after_ms) // 2
            observations.append({
                "target": target,
                "running": True,
                "observed_epoch_ms": observed_ms,
                "host_midpoint_epoch_ms": midpoint_ms,
                "offset_ms": observed_ms - midpoint_ms,
            })
        running = [item for item in observations if item["running"]]
        if not running:
            raise RuntimeError(f"Clock observation found no running database service: run_id={self.run_id!r}")
        return {
            "clock_source": "container wall-clock sample compared with host midpoint",
            "observations": observations,
            "max_abs_offset_ms": max(abs(int(item["offset_ms"])) for item in running),
        }

    def _stage_services(self, label: str) -> tuple[str, ...]:
        if label == "tikv":
            # Deferred TiKV Stores are absent (or created-but-stopped) until a
            # Case starts them, so the stage guard must mirror _check_tikv's
            # active-service expectation instead of the full topology.
            return tuple(
                service
                for service in self.COMPONENTS["tikv"]
                if service in self.active_tikv_services
            )
        if label in {"pd", "tiflash", "tikv", "monitoring", "ticdc", "downstream"}:
            if label == "monitoring":
                return self.COMPONENTS["monitoring"]
            if label == "tikv":
                # Deferred TiKV services are only `compose create`d after the
                # active stores pass readiness; asserting them here would fail
                # every deployment of a deferred topology (SF02 tikv-3, BC05
                # tikv-4/tikv-5 "container not found").
                return tuple(
                    service
                    for service in self.COMPONENTS["tikv"]
                    if service in self.active_tikv_services
                )
            return self.COMPONENTS[label]
        if label == "upgrade precheck":
            return (
                *self.COMPONENTS["pd"],
                *self.COMPONENTS["tikv"],
                *self.COMPONENTS["tidb"],
            )
        if label == "rolling upgrade PD":
            return self.COMPONENTS["pd"]
        if label in {
            "rolling upgrade TiKV",
            "TiKV region leader metadata",
            "TiKV leader transfer",
            "TiKV leader eviction",
        }:
            return self.COMPONENTS["tikv"]
        if label.startswith("pd leader before "):
            return self.COMPONENTS["pd"]
        if "/" in label:
            return (label.rsplit("/", 1)[1],)
        return (label,)

    def _container_snapshot(self, service: str) -> dict[str, Any]:
        container_id = self._service_container_id(service)
        raw = self._run(
            ["docker", "inspect", "--format", "{{json .}}", container_id],
            service,
        )
        return json.loads(raw)

    def _assert_stage_running(self, label: str) -> None:
        for service in self._stage_services(label):
            snapshot = self._container_snapshot(service)
            state = snapshot["State"]
            if state["OOMKilled"] or state["Status"] != "running":
                diagnostics = self._readiness_diagnostics(label)
                raise RuntimeError(
                    f"TiDB service stopped during readiness: run_id={self.run_id!r}, "
                    f"stage={label!r}, service={service!r}, status={state['Status']!r}, "
                    f"oom_killed={state['OOMKilled']}, exit_code={state['ExitCode']}, "
                    f"restart_count={snapshot.get('RestartCount', 0)}, diagnostics={diagnostics}"
                )

    def _readiness_diagnostics(self, label: str) -> str:
        details = []
        for service in self._stage_services(label):
            ps = subprocess.run(
                self._compose + ["ps", "--all", service],
                capture_output=True,
                text=True,
                env=self._env,
            )
            logs = subprocess.run(
                self._compose + ["logs", "--no-color", "--timestamps", "--tail", "40", service],
                capture_output=True,
                text=True,
                env=self._env,
            )
            details.append(
                f"service={service!r}, ps_stdout={ps.stdout.strip()!r}, "
                f"ps_stderr={ps.stderr.strip()!r}, logs_stdout={logs.stdout.strip()!r}, "
                f"logs_stderr={logs.stderr.strip()!r}"
            )
        return " | ".join(details)

    def add_region_peer(self, region_id: int, store_id: int) -> str:
        if region_id <= 0 or store_id <= 0:
            raise ValueError(
                f"PD add-peer requires positive identifiers: region_id={region_id}, store_id={store_id}"
            )
        return self._pd_ctl(
            "operator", "add", "add-peer", str(region_id), str(store_id)
        )

    def remove_region_peer(self, region_id: int, store_id: int) -> str:
        if region_id <= 0 or store_id <= 0:
            raise ValueError(
                f"PD remove-peer requires positive identifiers: region_id={region_id}, store_id={store_id}"
            )
        return self._pd_ctl(
            "operator", "add", "remove-peer", str(region_id), str(store_id)
        )

    def transfer_region_leader(self, region_id: int, store_id: int) -> str:
        if region_id <= 0 or store_id <= 0:
            raise ValueError(
                f"PD transfer-leader requires positive identifiers: region_id={region_id}, store_id={store_id}"
            )
        return self._pd_ctl(
            "operator", "add", "transfer-leader", str(region_id), str(store_id)
        )


    def _pd_ctl(self, *args: str) -> Any:
        output = self.exec(
            "pd/pd-0",
            ["/pd-ctl", "-u", "http://127.0.0.1:2379", *args],
        )
        if args[:2] == ("operator", "add") or args[:2] in {
            ("store", "weight"),
            ("store", "delete"),
            ("store", "remove-tombstone"),
            ("scheduler", "add"),
            ("scheduler", "remove"),
        }:
            if "Usage:" in output:
                raise RuntimeError(
                    f"PD control command was rejected: run_id={self.run_id!r}, "
                    f"args={args!r}, output={output.strip()!r}"
                )
            return output.strip() or None
        if output.strip():
            try:
                return json.loads(output)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"PD control command returned non-JSON output: run_id={self.run_id!r}, "
                    f"args={args!r}, output={output.strip()!r}"
                ) from exc
        if args[:2] in {("scheduler", "add"), ("scheduler", "remove")}:
            return None
        raise RuntimeError(
            f"PD control command returned an empty response: run_id={self.run_id!r}, args={args!r}"
        )

    def pd_ctl_command(self, *args: str) -> str:
        """Run a bounded raw pd-ctl command for a scenario-owned control plane."""
        output = self.exec(
            "pd/pd-0",
            ["/pd-ctl", "-u", "http://127.0.0.1:2379", *args],
        ).strip()
        if not output:
            raise RuntimeError(
                f"PD control command returned an empty response: run_id={self.run_id!r}, args={args!r}"
            )
        if "Usage:" in output or output.casefold().startswith("failed"):
            raise RuntimeError(
                f"PD control command was rejected: run_id={self.run_id!r}, args={args!r}, output={output!r}"
            )
        return output

    def pd_ctl_command_with_json(
        self,
        args: tuple[str, ...],
        payload: object,
        *,
        container_path: str,
    ) -> str:
        """Run pd-ctl with JSON written inside the isolated PD container."""
        if not container_path.startswith("/tmp/aiopsbench-"):
            raise ValueError(
                f"K09 pd-ctl input path must stay under /tmp/aiopsbench-: path={container_path!r}"
            )
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        command = " ".join(
            shlex.quote(value)
            for value in ("/pd-ctl", "-u", "http://127.0.0.1:2379", *args)
        )
        script = (
            "set -eu; "
            f"printf '%s' {shlex.quote(encoded)} > {shlex.quote(container_path)}; "
            f"exec {command}"
        )
        output = self.exec("pd/pd-0", ["sh", "-ceu", script]).strip()
        if not output:
            raise RuntimeError(
                "PD control command with JSON returned an empty response: "
                f"run_id={self.run_id!r}, args={args!r}, container_path={container_path!r}"
            )
        if "Usage:" in output or output.casefold().startswith("failed"):
            raise RuntimeError(
                "PD control command with JSON was rejected: "
                f"run_id={self.run_id!r}, args={args!r}, output={output!r}"
            )
        return output

    def _pd_stores(self) -> list[dict[str, object]]:
        payload = self._pd_ctl("store")
        stores = payload["stores"]
        if not isinstance(stores, list):
            raise TypeError(f"PD store response has non-list stores: payload={payload!r}")
        return stores


    def _wait(self, label: str, check, timeout: int):
        if timeout <= 0:
            raise ValueError(f"TiDB readiness timeout must be positive: stage={label!r}, timeout={timeout}")
        deadline = time.monotonic() + timeout
        last_error = None
        last_report = -1
        while time.monotonic() < deadline:
            self._assert_stage_running(label)
            try:
                check()
                return
            except _TiDBReadinessFatalError:
                raise
            except Exception as exc:
                last_error = exc
                self._last_readiness_error = repr(exc)
                elapsed = int(timeout - max(0, deadline - time.monotonic()))
                report = elapsed // 15
                if report != last_report:
                    print(
                        f"[Deployment] TiDB readiness pending: run_id={self.run_id!r}, "
                        f"stage={label!r}, elapsed={elapsed}s/{timeout}s, error={exc!r}"
                    )
                    last_report = report
                time.sleep(1)
        diagnostics = self._readiness_diagnostics(label)
        raise RuntimeError(
            f"TiDB readiness timed out: run_id={self.run_id!r}, stage={label!r}, "
            f"timeout={timeout}, last_error={last_error!r}, diagnostics={diagnostics}"
        ) from last_error

    @staticmethod
    def _stable_check(check, required_successes: int):
        successful_checks = 0

        def check_stable():
            nonlocal successful_checks
            try:
                check()
            except Exception:
                successful_checks = 0
                raise
            successful_checks += 1
            if successful_checks < required_successes:
                raise RuntimeError(
                    f"readiness requires {required_successes} consecutive checks; "
                    f"observed={successful_checks}"
                )

        return check_stable

    def _check_pd(self):
        members = self._pd_json("/pd/api/v1/members").get("members", [])
        expected = self.topology.pd_count
        if len(members) != expected:
            raise RuntimeError(f"expected {expected} PD members, got {len(members)}: {members!r}")
        leader = self._pd_json("/pd/api/v1/leader")
        expected_leaders = set(self.COMPONENTS["pd"])
        if leader.get("name") not in expected_leaders:
            raise RuntimeError(
                f"PD has no valid leader: run_id={self.run_id!r}, "
                f"expected={sorted(expected_leaders)!r}, payload={leader!r}"
            )

    def _check_pd_leader(self):
        self._pd_json("/pd/api/v1/leader")

    def _check_tikv(self, expected_services=None):
        stores = self._pd_json("/pd/api/v1/stores").get("stores", [])
        expected_services = set(self.active_tikv_services if expected_services is None else expected_services)
        # PD's /stores API also lists TiFlash engines (address <service>:3930);
        # scope the comparison to TiKV store addresses so post-deploy readiness
        # does not count a registered TiFlash node as an unexpected TiKV service.
        up_services = {
            item["store"]["address"].split(":", 1)[0]
            for item in stores
            if item.get("store", {}).get("state_name") == "Up"
            and item["store"]["address"].endswith(":20160")
        }
        if up_services != expected_services:
            container_states = {}
            for service in sorted(expected_services):
                container_id = self._service_container_id(service)
                state = json.loads(
                    self._run(
                        ["docker", "inspect", "--format", "{{json .State}}", container_id],
                        service,
                    )
                )
                container_states[service] = {
                    "status": state["Status"],
                    "running": state["Running"],
                    "exit_code": state["ExitCode"],
                    "error": state["Error"],
                }
            stopped = {
                service: state
                for service, state in container_states.items()
                if not state["running"]
            }
            if stopped:
                logs = {
                    service: self._run(
                        ["docker", "logs", "--tail", "80", self._service_container_id(service)],
                        service,
                    )[-4000:]
                    for service in stopped
                }
                raise _TiDBReadinessFatalError(
                    f"TiKV container exited before readiness: run_id={self.run_id!r}, "
                    f"containers={stopped!r}, logs={logs!r}, stores={stores!r}"
                )
            raise RuntimeError(
                f"expected Up TiKV services={sorted(expected_services)!r}, "
                f"observed={sorted(up_services)!r}, container_states={container_states!r}, "
                f"stores={stores!r}"
            )

    def _start_tikv_services(self, command: tuple[str, ...]) -> None:
        started_tikv_services = set()
        for service in self.COMPONENTS["tikv"]:
            if service not in self.active_tikv_services:
                continue
            self._run(self._compose + [*command, service], service)
            started_tikv_services.add(service)
            self._wait(
                f"tikv/{service}",
                lambda expected_services=frozenset(started_tikv_services): self._check_tikv(expected_services),
                self.tidb_readiness_timeout_sec,
            )
        self._wait("tikv", self._check_tikv, self.tidb_readiness_timeout_sec)

    def _check_tiflash(self):
        for service in self.COMPONENTS["tiflash"]:
            container_id = self._service_container_id(service)
            self._run(
                ["docker", "exec", container_id, "wget", "-qO-", "http://127.0.0.1:8234/metrics"],
                service,
            )

    def _check_tikv_target(self, service: str):
        stores_payload = self._pd_json("/pd/api/v1/stores")
        stores = stores_payload.get("stores")
        if stores is None:
            raise RuntimeError(
                f"PD stores API returned no store list: run_id={self.run_id!r}, "
                f"payload={stores_payload!r}"
            )
        target_address = f"{service}:20160"
        matching = [
            item for item in stores
            if item.get("store", {}).get("address") == target_address
        ]
        if len(matching) != 1 or matching[0]["store"].get("state_name") != "Up":
            raise RuntimeError(
                f"TiKV store is not Up: run_id={self.run_id!r}, service={service!r}, "
                f"target_address={target_address!r}, stores={stores!r}"
            )

    def _check_tidb_target(self, target: str):
        service, = self._services(target)
        container_id = self._service_container_id(service)
        state = json.loads(
            self._run(
                ["docker", "inspect", "--format", "{{json .State}}", container_id],
                target,
            )
        )
        if not state["Running"]:
            logs = self._run(
                ["docker", "logs", "--tail", "80", container_id],
                target,
            )
            raise _TiDBReadinessFatalError(
                f"TiDB container exited before readiness: run_id={self.run_id!r}, "
                f"target={target!r}, status={state['Status']!r}, exit_code={state['ExitCode']}, "
                f"error={state['Error']!r}, logs={logs[-4000:]!r}"
            )
        import pymysql
        host, port = self.tidb_endpoints[target]
        try:
            with pymysql.connect(
                host=host, port=port, user="root", password="", connect_timeout=5,
                read_timeout=5, write_timeout=5, autocommit=True,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
        except Exception as exc:
            raise RuntimeError(
                f"TiDB SQL readiness probe failed: run_id={self.run_id!r}, target={target!r}, "
                f"endpoint={host}:{port}, error={exc!r}"
            ) from exc

    def _tidb_readiness_diagnostics(self, target: str) -> str:
        import urllib.error
        from urllib.request import urlopen

        service, = self._services(target)
        container_id = self._service_container_id(service)
        inspect = json.loads(
            self._run(
                ["docker", "inspect", "--format", "{{json .}}", container_id],
                target,
            )
        )
        state = inspect["State"]
        status_api = None
        status_api_error = None
        host, port = self.tidb_endpoints[target]
        try:
            with urlopen(f"http://{host}:{port + 1}/status", timeout=3) as response:
                status_api = {
                    "http_status": response.status,
                    "body": json.load(response),
                }
        except (OSError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            status_api_error = repr(exc)
        log_lines = self.read_logs(target, lines=120).splitlines()
        signal_lines = [
            line
            for line in log_lines
            if any(
                token in line.casefold()
                for token in ("bootstrap", "ddl", "schema", "tso", "timestamp", "ready", "error", "warn")
            )
        ][-20:]
        return (
            f"endpoint={host}:{port}, status_api={status_api!r}, status_api_error={status_api_error!r}, "
            f"container={{'id': {container_id!r}, 'status': {state['Status']!r}, "
            f"'running': {state['Running']!r}, 'oom_killed': {state['OOMKilled']!r}, "
            f"'restart_count': {inspect['RestartCount']!r}}}, "
            f"log_signals={signal_lines!r}"
        )

    def _wait_tidb_target(self, target: str, timeout: int):
        try:
            self._wait(target, lambda: self._check_tidb_target(target), timeout)
        except RuntimeError as exc:
            diagnostics = self._tidb_readiness_diagnostics(target)
            raise RuntimeError(f"{exc}; readiness_diagnostics={diagnostics}") from exc

    def _tidb_readiness_timeout(self, index: int) -> int:
        if index == 0 and self.topology.tikv_count >= 3:
            return self.FIRST_TIDB_BOOTSTRAP_TIMEOUT
        if index == 0:
            return self.DEFAULT_FIRST_TIDB_READINESS_TIMEOUT
        return self.FOLLOWING_TIDB_READINESS_TIMEOUT

    def _check_tidb(self):
        for target in self.tidb_endpoints:
            self._check_tidb_target(target)

    def _check_prometheus(self):
        from urllib.parse import urlencode
        from urllib.request import urlopen
        with urlopen(f"http://127.0.0.1:{self.prometheus_port}/-/ready", timeout=3) as response:
            if response.status != 200:
                raise RuntimeError(f"Prometheus readiness returned HTTP {response.status}")
        query = urlencode({"query": "up"})
        with urlopen(
            f"http://127.0.0.1:{self.prometheus_port}/api/v1/query?{query}", timeout=3
        ) as response:
            payload = json.load(response)
        targets = payload["data"]["result"]
        deferred_instances = {
            f"{service}:20180"
            for service in self.COMPONENTS["tikv"]
            if service not in self.active_tikv_services
        }
        if self.lightning_scrape_target:
            # The Case-owned Lightning container starts after deployment, so
            # its target stays down during readiness and must be deferred.
            deferred_instances.add(self.lightning_scrape_target)
        down = [
            item["metric"]
            for item in targets
            if item["value"][1] != "1"
            and item["metric"].get("instance") not in deferred_instances
        ]
        expected = self._prometheus_expected_target_count()
        if len(targets) != expected or down:
            # A shortfall with no down target means Prometheus has not yet run
            # its first scrape round for every static target; that lag is
            # bounded by the scrape interval, so tolerate it within a grace
            # window instead of spending the readiness budget on retries.
            if len(targets) < expected and not down:
                now = time.monotonic()
                if self._prometheus_shortfall_since is None:
                    self._prometheus_shortfall_since = now
                    print(
                        f"[Deployment] Prometheus service discovery lag: "
                        f"expected={expected}, actual={len(targets)}; allowing "
                        f"{self.PROMETHEUS_DISCOVERY_GRACE_SECONDS}s grace"
                    )
                    return
                if now - self._prometheus_shortfall_since < self.PROMETHEUS_DISCOVERY_GRACE_SECONDS:
                    return
            raise RuntimeError(
                f"Prometheus targets not ready: expected={expected}, actual={len(targets)}, down={down!r}"
            )
        self._prometheus_shortfall_since = None
        series_query = urlencode({
            "query": "sum by (container_label_com_docker_compose_service) "
                     f'(container_cpu_usage_seconds_total{{container_label_com_docker_compose_project="{self.project_name}"}})'
        })
        with urlopen(
            f"http://127.0.0.1:{self.prometheus_port}/api/v1/query?{series_query}", timeout=3
        ) as response:
            payload = json.load(response)
        observed_services = {
            item["metric"].get("container_label_com_docker_compose_service")
            for item in payload["data"]["result"]
        }
        expected_services = {
            *self.COMPONENTS["pd"],
            *self.active_tikv_services,
            *self.COMPONENTS["tidb"],
            *self.COMPONENTS["tiflash"],
        }
        missing_services = sorted(expected_services - observed_services)
        if missing_services:
            # cadvisor registers new containers between scrapes; the metric
            # collection layer requires every database service, so readiness
            # must not release the environment before their first samples land.
            raise RuntimeError(
                f"Prometheus has no container samples yet for TiDB services: "
                f"run_id={self.run_id!r}, missing={missing_services!r}"
            )

    def prometheus_services_fresh(self, window_seconds: int) -> bool:
        """True when every database and monitoring service has a fresh sample.

        The metric collection layer's rate queries need recent samples for every
        service; under host load cAdvisor scrapes can stall for whole windows
        even though the deployment readiness gate saw first samples earlier.
        The disk aggregates additionally need cAdvisor to be exporting
        filesystem stats at all: a freshly started cAdvisor reports cpu series
        while its machine filesystem detection has not produced any
        container_fs_* series yet, and rate queries over them return no series.
        """
        from urllib.parse import urlencode
        from urllib.request import urlopen

        def fresh_series(metric_selector: str) -> list:
            freshness_query = urlencode({
                "query": f'timestamp({metric_selector}'
                         f'{{container_label_com_docker_compose_project="{self.project_name}"}})'
                         f' > time() - {window_seconds}',
            })
            with urlopen(
                f"http://127.0.0.1:{self.prometheus_port}/api/v1/query?{freshness_query}",
                timeout=3,
            ) as response:
                payload = json.load(response)
            return payload["data"]["result"]

        expected_services = {
            *self.COMPONENTS["pd"],
            *self.active_tikv_services,
            *self.COMPONENTS["tidb"],
            *self.COMPONENTS["tiflash"],
            *self.COMPONENTS["monitoring"],
        }
        observed_services = {
            item["metric"].get("container_label_com_docker_compose_service")
            for item in fresh_series("container_cpu_usage_seconds_total")
        }
        if not expected_services <= observed_services:
            return False
        return bool(fresh_series("container_fs_reads_bytes_total"))

    def _check_downstream(self):
        import pymysql

        connection = pymysql.connect(
            host="127.0.0.1",
            port=self.downstream_port,
            user="root",
            password="",
            connect_timeout=3,
            read_timeout=3,
            write_timeout=3,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                if cursor.fetchone() != (1,):
                    raise RuntimeError(
                        f"TiDB downstream readiness returned an unexpected probe row: run_id={self.run_id!r}"
                    )
        finally:
            connection.close()

    def _check_ticdc(self, target=None):
        from urllib.request import urlopen

        targets = self.ticdc_ports if target is None else {target: self.ticdc_ports[target]}
        for capture_target, port in targets.items():
            with urlopen(f"http://127.0.0.1:{port}/status", timeout=3) as response:
                if response.status != 200:
                    raise RuntimeError(
                        "TiCDC readiness returned a non-200 response: "
                        f"run_id={self.run_id!r}, target={capture_target!r}, status={response.status}"
                    )

    def enable_lightning_scrape_target(self, target: str) -> None:
        """Declare the Case-owned Lightning container as a Prometheus target."""
        self.lightning_scrape_target = target

    def update_node_cpu_limit(self, target: str, cpu_limit: float) -> None:
        """Sync node cpu bookkeeping after an external docker cgroup resize."""
        self.node_cpu_limits[target] = float(cpu_limit)

    def _prometheus_expected_target_count(self) -> int:
        with open(os.path.join(self.runtime_dir, "prometheus.yml"), encoding="utf-8") as handle:
            prometheus = yaml.safe_load(handle)
        return sum(
            len(static_config["targets"])
            for config in prometheus["scrape_configs"]
            for static_config in config["static_configs"]
        )

    def _prometheus_readiness_timeout(self) -> int:
        # Derive the budget from the same rendered scrape configuration the
        # readiness check counts, so case-owned targets (ticdc, Lightning,
        # deferred TiKV) scale the timeout without a second counting formula.
        extra_targets = max(
            0,
            self._prometheus_expected_target_count() - self.PROMETHEUS_READINESS_TARGET_BASELINE,
        )
        return self.PROMETHEUS_READINESS_TIMEOUT + (
            extra_targets * self.PROMETHEUS_READINESS_SECONDS_PER_EXTRA_TARGET
        )

    def _tikv_readiness_timeout(self) -> int:
        if self.snapshots.persistent_state_reused or self.snapshots.image_group_reused:
            return self.warm_tidb_readiness_timeout_sec
        return self.tidb_readiness_timeout_sec

    def _start_database_services(self) -> None:
        self._container_ids.clear()
        self._run(self._compose + ["up", "--detach", *self.COMPONENTS["pd"]], "pd")
        self._wait("pd", self._check_pd, 120)
        started_tikv_services = set()
        for service in self.COMPONENTS["tikv"]:
            if service not in self.active_tikv_services:
                continue
            target = f"tikv/{service}"
            self._wait("pd leader before " + target, self._check_pd_leader, 120)
            self._run(self._compose + ["up", "--detach", service], target)
            started_tikv_services.add(service)
            self._wait(
                target,
                lambda expected_services=frozenset(started_tikv_services): self._check_tikv(expected_services),
                self._tikv_readiness_timeout(),
            )
        for service in self.COMPONENTS["tikv"]:
            if service in self.active_tikv_services:
                continue
            target = f"tikv/{service}"
            self._run(self._compose + ["create", service], target)
        if self.COMPONENTS["tiflash"]:
            self._run(self._compose + ["up", "--detach", *self.COMPONENTS["tiflash"]], "tiflash")
            self._wait("tiflash", self._check_tiflash, 300)
        for index, service in enumerate(self.COMPONENTS["tidb"]):
            target = f"tidb/{service}"
            self._wait("pd leader before " + target, self._check_pd_leader, 120)
            self._run(self._compose + ["up", "--detach", service], target)
            if self.snapshots.persistent_storage_enabled or self.snapshots.image_group_enabled:
                timeout = (
                    self.warm_tidb_readiness_timeout_sec
                    if self.snapshots.persistent_state_reused or self.snapshots.image_group_reused
                    else self.tidb_readiness_timeout_sec
                )
            else:
                timeout = self._tidb_readiness_timeout(index)
            self._wait_tidb_target(target, timeout)

    def _start_replication_services(self) -> None:
        if self.replication_runtime is None:
            return
        self._run(self._compose + ["up", "--detach", "mysql-0"], "downstream")
        self._wait("downstream", self._check_downstream, 180)
        for service in self.COMPONENTS["ticdc"]:
            target = f"ticdc/{service}"
            self._run(self._compose + ["up", "--detach", service], target)
            self._wait(target, lambda target=target: self._check_ticdc(target), 180)
        # TiCDC deliberately has no restart policy (the K02 fault kills it), so
        # a capture that lost its race with the tail of the cluster startup
        # would stay dead until fault injection. Revive it once now that
        # PD/TiKV are up, and require a stable /status answer.
        for service in self.COMPONENTS["ticdc"]:
            target = f"ticdc/{service}"
            try:
                self._check_ticdc(target)
            except (OSError, RuntimeError) as error:
                print(
                    f"[Deployment] TiCDC capture died during cluster startup; reviving: "
                    f"run_id={self.run_id!r}, target={target!r}, error={error!r}"
                )
                self._run(self._compose + ["up", "--detach", service], target)
                self._wait(target, lambda target=target: self._check_ticdc(target), 180)

    def deploy(self):
        if self._port_lease is None:
            self._port_lease = claim_host_ports(
                tuple(range(self.port_base, self.port_base + self._port_block_span())), owner=self.run_id,
                owned_containers=tuple(f"{self.project_name}-{service}-1" for services in self.COMPONENTS.values() for service in services),
            )
        self.preflight()
        if self._project_exists():
            if self.is_ready():
                self._deployment_reached_ready = True
                return
            raise RuntimeError(
                f"TiDB Compose project exists but is not ready: run_id={self.run_id!r}, "
                f"last_readiness_error={self._last_readiness_error!r}; run teardown() before creating a fresh environment"
            )
        self.snapshots._prepare_persistent_state()
        try:
            self._start_cluster()
        except Exception as error:
            self._retry_cluster_start(error)
        if (
            not self.snapshots.persistent_storage_enabled
            and not self.snapshots.image_group_enabled
            and self.snapshots.bootstrap_cache_enabled
            and self.topology.deferred_tikv_count == 0
        ):
            self.snapshots._save_bootstrap_cache()

    def _start_cluster(self) -> None:
        self._ensure_network()
        self._start_database_services()
        self._start_replication_services()
        self._run(self._compose + ["up", "--detach", *self.COMPONENTS["monitoring"]], "monitoring")
        self._apply_worker_numa_binding()
        self._wait("prometheus", self._check_prometheus, self._prometheus_readiness_timeout())
        self._deployment_reached_ready = True

    def _retry_cluster_start(self, first_error: Exception) -> None:
        """Reset the partially started compose project and start the cluster once more.

        Cluster-start failures under concurrent multi-cluster deployment are
        dominated by transient host contention (embedded-DNS resolution
        failures, TiKV heartbeat stalls, TiDB exiting before SQL readiness).
        A cache-seeded start that failed is treated as untrustworthy cache
        content: the retry drops the cache and cold-bootstraps, and the next
        successful deploy re-saves a fresh cache. Deterministic deployments
        (persistent storage, image group) do not retry — except a reused
        persistent baseline that cannot boot, which is a corrupt cache entry
        and is rebuilt once from a fresh bootstrap.
        """
        if self.snapshots.image_group_enabled:
            raise first_error
        if self.snapshots.persistent_storage_enabled:
            if not self.snapshots.persistent_state_reused:
                raise first_error
            print(
                f"[Deployment] TiDB persistent baseline failed to start; rebuilding it once: "
                f"run_id={self.run_id!r}, storage_key={self.snapshots.storage_key!r}, error={first_error!r}"
            )
            self._reset_partial_cluster()
            self.snapshots._discard_persistent_baseline()
            try:
                self._start_cluster()
            except Exception as retry_error:
                raise RuntimeError(
                    f"TiDB cluster start retry failed: run_id={self.run_id!r}, first_error={first_error!r}"
                ) from retry_error
            return
        print(
            f"[Deployment] TiDB cluster start failed; resetting containers and retrying once: "
            f"run_id={self.run_id!r}, error={first_error!r}"
        )
        self.snapshots._discard_bootstrap_cache()
        self._reset_partial_cluster()
        try:
            self._start_cluster()
        except Exception as retry_error:
            raise RuntimeError(
                f"TiDB cluster start retry failed: run_id={self.run_id!r}, first_error={first_error!r}"
            ) from retry_error


    def _reset_partial_cluster(self) -> None:
        self._run(self._compose + ["down", "--volumes", "--remove-orphans"], "deployment-retry")
        if self._network_created:
            self._run(["docker", "network", "rm", self.network_name], "deployment-retry network")
            self._network_created = False
        self._container_ids.clear()
        for (node_type, service), destination in self.snapshots.bootstrap_data_paths.items():
            shutil.rmtree(destination)
            os.makedirs(destination)
            if self.snapshots.bootstrap_cache_used:
                self.snapshots._copy_tree(
                    os.path.join(self.snapshots.bootstrap_cache_path, node_type, service), destination
                )

    def is_ready(self) -> bool:
        try:
            self._check_pd()
            self._check_tikv()
            self._check_tidb()
            if self.replication_runtime is not None:
                self._check_downstream()
                self._check_ticdc()
            self._check_prometheus()
            states = self.node_states()
            required_targets = {
                target
                for target in states
                if not target.startswith("tikv/")
                or self.NODES[target] in self.active_tikv_services
            }
            return all(states[target]["running"] for target in required_targets)
        except Exception as exc:
            self._last_readiness_error = repr(exc)
            return False

    def wait_for_ready(self, timeout: int = 180) -> bool:
        self._wait("cluster", self._check_cluster, timeout)
        return True

    def _check_cluster(self) -> None:
        if not self.is_ready():
            raise RuntimeError(
                f"TiDB cluster is not ready: run_id={self.run_id!r}, "
                f"last_readiness_error={self._last_readiness_error!r}"
            )

    def list_nodes(self) -> List[str]:
        return list(self.NODES)

    def list_database_nodes(self) -> List[str]:
        return list(self.database_nodes)

    def _services(self, target: str) -> tuple:
        if target in self.NODES:
            return (self.NODES[target],)
        if target in self.COMPONENTS:
            return self.COMPONENTS[target]
        raise ValueError(f"Unknown TiDB target {target!r}; expected one of {list(self.NODES)}")

    def _service_state(self, target: str) -> Dict[str, Any]:
        service = self.NODES[target]
        container_id = self._service_container_id(service)
        try:
            raw = self._run(
                ["docker", "inspect", "--format", "{{json .State}}", container_id], service
            )
        except RuntimeError as exc:
            # 外部清理删除已退出容器时 inspect 报 no such object：missing 是
            # restore 需要显式处理的合法状态；其余 inspect 失败照常抛出。
            if "no such object" not in str(exc):
                raise
            return {
                "container_id": container_id,
                "running": False,
                "paused": False,
                "oom_killed": False,
                "status": "missing",
                "missing": True,
            }
        state = json.loads(raw)
        return {
            "container_id": container_id,
            "running": state["Running"],
            "paused": state["Paused"],
            "oom_killed": state["OOMKilled"],
            "status": state["Status"],
            "missing": False,
        }

    def node_states(self) -> Dict[str, Dict[str, Any]]:
        states = {}
        for target, service in self.NODES.items():
            container_id = self._service_container_id(service)
            raw = self._run(
                ["docker", "inspect", "--format", "{{json .State}}", container_id], service
            )
            state = json.loads(raw)
            states[target] = {
                "container_id": container_id,
                "running": state["Running"],
                "paused": state["Paused"],
                "oom_killed": state["OOMKilled"],
                "status": state["Status"],
            }
        return states

    def _control(self, action: str, target: str):
        services = self._services(target)
        for service in services:
            self._run(self._compose + [action, service], f"{target}/{service}")
        self._container_ids.clear()

    def restart_component(self, target: str):
        self._control("restart", target)
        pd_targets = self.network._tidb_stale_egress_targets.get(target)
        if pd_targets:
            self.network.allow_pd_network_stale_egress(target, pd_targets)
        pd_targets = self.network._tidb_egress_shadow_targets.get(target)
        if pd_targets:
            self.network._run_network_namespace_tool(
                target,
                self.network._tidb_egress_shadow_rule_script(pd_targets),
            )
        addresses = self.network._tidb_pd_network_rehydration_addresses.get(target)
        if addresses:
            self.network._run_network_namespace_tool(
                target,
                self.network._pd_network_rehydration_rule_script(addresses),
            )

    def restart_pd_quorum(self) -> None:
        services = self.COMPONENTS["pd"]
        self._run(self._compose + ["restart", *services], "pd quorum restart")
        self._container_ids.clear()


    def stop_component(self, target: str):
        # An individually stopped TiCDC capture must flush its tables before
        # exit, so its stop is graceful; other components use compose defaults.
        stop_args = ["--timeout", "120"] if target.startswith("ticdc/") else []
        for service in self._services(target):
            self._run(
                self._compose + ["stop", *stop_args, service],
                target if target in self.NODES else f"{target}/{service}",
            )
        self._container_ids.clear()
        if target.startswith("tikv/"):
            self.active_tikv_services.remove(self.NODES[target])

    def start_component(self, target: str):
        services = self._services(target)
        for service in services:
            self._container_ids.clear()
            container_id = self._service_container_id(service)
            self._run(["docker", "start", container_id], f"{target}/{service}")
        if target.startswith("tikv/"):
            self.active_tikv_services.add(self.NODES[target])

    def read_logs(self, target: str, lines: int = 200) -> str:
        service, = self._services(target)
        return self._run(
            self._compose + ["logs", "--no-color", "--timestamps", "--tail", str(lines), service],
            target,
        )

    def read_logs_at_range(self, target: str, start_epoch_ms: int, end_epoch_ms: int) -> str:
        """Read only the Docker log interval used by a metric capture."""
        if start_epoch_ms >= end_epoch_ms:
            raise ValueError(
                f"TiDB log capture range must be positive: target={target!r}, "
                f"start_epoch_ms={start_epoch_ms}, end_epoch_ms={end_epoch_ms}"
            )
        service, = self._services(target)
        start = datetime.fromtimestamp(start_epoch_ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        end = datetime.fromtimestamp(end_epoch_ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        return self._run(
            self._compose + [
                "logs", "--no-color", "--timestamps", "--since", start, "--until", end, service,
            ],
            target,
        )

    def _exec_command(self, target: str, command: List[str]) -> List[str]:
        service, = self._services(target)
        return ["docker", "exec", self._service_container_id(service), *command]

    def exec(self, target: str, command: List[str]) -> str:
        return self._run(self._exec_command(target, command), target)


    def wait_for_target(self, target: str, timeout: int = 120) -> None:
        self._wait_tidb_target(target, timeout)

    def teardown(self):
        if self.compose_file is not None and os.path.isfile(self.compose_file):
            self._docker_info()
            runtime_audit_path = self._env.get("AIOPS_RUNTIME_AUDIT_PATH")
            runtime_audit_incomplete = False
            if runtime_audit_path:
                services = []
                missing_services = []
                inspect_errors = []
                for target, service in sorted(self.NODES.items()):
                    container_id = self._run(
                        self._compose + ["ps", "--all", "--quiet", service], service
                    ).strip()
                    if not container_id:
                        missing_services.append({"target": target, "service": service})
                        continue
                    inspected = subprocess.run(
                        ["docker", "inspect", container_id],
                        capture_output=True,
                        text=True,
                        env=self._env,
                    )
                    if inspected.returncode != 0:
                        inspect_errors.append(
                            {
                                "target": target,
                                "service": service,
                                "container_id": container_id,
                                "returncode": inspected.returncode,
                                "stderr": inspected.stderr.strip(),
                            }
                        )
                        continue
                    records = json.loads(inspected.stdout)
                    if len(records) != 1:
                        inspect_errors.append(
                            {
                                "target": target,
                                "service": service,
                                "container_id": container_id,
                                "error": "expected one docker inspect record",
                                "record_count": len(records),
                            }
                        )
                        continue
                    record = records[0]
                    host_config = record["HostConfig"]
                    state = record["State"]
                    services.append({
                        "target": target,
                        "service": service,
                        "container_id": record["Id"],
                        "name": record["Name"].lstrip("/"),
                        "state": {
                            "status": state["Status"],
                            "running": state["Running"],
                            "exit_code": state["ExitCode"],
                            "oom_killed": state["OOMKilled"],
                        },
                        "runtime": {
                            "cpuset_cpus": host_config["CpusetCpus"],
                            "cpuset_mems": host_config["CpusetMems"],
                            "nano_cpus": host_config["NanoCpus"],
                            "memory_bytes": host_config["Memory"],
                            "cpu_quota": host_config["CpuQuota"],
                            "cpu_period": host_config["CpuPeriod"],
                        },
                    })
                runtime_audit_incomplete = bool(missing_services or inspect_errors)
                Path(runtime_audit_path).write_text(
                    json.dumps(
                        {
                            "schema": "tidb_docker_runtime_v1",
                            "run_id": self.run_id,
                            "requested": {
                                "cpuset_cpus": self._env.get("AIOPS_CPUSET_CPUS"),
                                "cpuset_mems": self._env.get("AIOPS_CPUSET_MEMS"),
                                "cpu_limit": self._env.get("AIOPS_CPU_LIMIT"),
                                "memory_mb": self._env.get("AIOPS_MEMORY_MB"),
                            },
                            "expected_service_count": len(self.NODES),
                            "missing_services": missing_services,
                            "inspect_errors": inspect_errors,
                            "services": services,
                        },
                        ensure_ascii=True,
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
            if not self.snapshots.persistent_storage_enabled and not self.snapshots.image_group_enabled:
                for node_type, services in (("pd", self.COMPONENTS["pd"]), ("tikv", self.COMPONENTS["tikv"])):
                    for service in services:
                        container_id = self._run(
                            self._compose + ["ps", "--all", "--quiet", service], service
                        ).strip()
                        if container_id:
                            running = self._run(
                                ["docker", "inspect", "--format", "{{.State.Running}}", container_id],
                                service,
                            ).strip()
                            if running == "true":
                                self._run(
                                    [
                                        "docker",
                                        "exec",
                                        "--user",
                                        "0:0",
                                        container_id,
                                        "chmod",
                                        "-R",
                                        "a+rwX",
                                        f"/data/{node_type}",
                                    ],
                                    service,
                                )
                            elif running == "false":
                                if self.release is None:
                                    raise RuntimeError(
                                        f"TiDB release is not configured while normalizing stopped data: "
                                        f"run_id={self.run_id!r}, service={service!r}"
                                    )
                                self.snapshots._normalize_host_directory(
                                    self.snapshots.bootstrap_data_paths[(node_type, service)],
                                    self.release.pd_image,
                                    f"stopped {node_type} service={service!r}",
                                )
                            else:
                                raise RuntimeError(
                                    f"Unexpected Docker running state during TiDB teardown: "
                                    f"run_id={self.run_id!r}, service={service!r}, "
                                    f"container_id={container_id!r}, running={running!r}"
                                )
            down_args = ["down", "--remove-orphans"]
            if not self.snapshots.persistent_storage_enabled:
                down_args.insert(1, "--volumes")
            self._run(self._compose + down_args, "compose")
            remaining = self._run(self._compose + ["ps", "--all", "--quiet"], "compose").strip()
            cleanup_audit_path = self._env.get("AIOPS_CLEANUP_AUDIT_PATH")
            if cleanup_audit_path:
                Path(cleanup_audit_path).write_text(
                    json.dumps(
                        {
                            "schema": "tidb_cleanup_v1",
                            "run_id": self.run_id,
                            "official_teardown": True,
                            "compose_down": down_args,
                            "remaining_containers": remaining,
                            "network_created": self._network_created,
                        },
                        ensure_ascii=True,
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
            if remaining:
                raise RuntimeError(
                    f"TiDB teardown left containers behind: run_id={self.run_id!r}, containers={remaining!r}"
                )
            if self._network_created:
                self._run(["docker", "network", "rm", self.network_name], "network")
                self._network_created = False
            if runtime_audit_incomplete:
                if self._deployment_reached_ready:
                    raise RuntimeError(
                        "TiDB runtime audit was incomplete after official cleanup: "
                        f"run_id={self.run_id!r}, runtime_audit_path={runtime_audit_path!r}"
                    )
                # The environment never reached ready, so the expected runtime
                # state never existed; raising here would only bury the run's
                # original failure under an audit error.
                print(
                    f"[Deployment] TiDB runtime audit incomplete after a deployment that never "
                    f"became ready (ignored): run_id={self.run_id!r}, "
                    f"missing_services={missing_services!r}, inspect_errors={inspect_errors!r}"
                )
        if self.snapshots._persistent_run_dir is not None and self.snapshots._persistent_run_dir.exists():
            self.snapshots._make_persistent_state_user_accessible()
            shutil.rmtree(self.snapshots._persistent_run_dir)
        self.snapshots.release_persistence_lock()
        if self.runtime_dir is not None and os.path.isdir(self.runtime_dir):
            shutil.rmtree(self.runtime_dir)

        if self._port_lease is not None:
            self._port_lease.close()
            self._port_lease = None

    def force_teardown(self) -> None:
        """Immediately remove this run's containers, network, and volumes."""
        if self.compose_file is not None and os.path.isfile(self.compose_file):
            self._run(self._compose + ["down", "--volumes", "--remove-orphans", "--timeout", "5"], "force compose")
        if self._network_created:
            attached = json.loads(self._run(
                ["docker", "network", "inspect", self.network_name, "--format", "{{json .Containers}}"],
                "inspect force network",
            )) or {}
            for container_id in attached:
                removal = subprocess.run(
                    ["docker", "rm", "--force", container_id],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                # A concurrent removal (graceful teardown still draining) has
                # already accepted the rm; "already in progress" is the goal state.
                if removal.returncode != 0 and "is already in progress" not in removal.stderr:
                    raise RuntimeError(
                        f"TiDB command failed: run_id={self.run_id!r}, component='remove force-network container', "
                        f"command='docker rm --force {container_id}', returncode={removal.returncode}, "
                        f"stdout={removal.stdout!r}, stderr={removal.stderr!r}"
                    )
            self._run(["docker", "network", "rm", self.network_name], "force network")
            self._network_created = False
        if self.runtime_dir is not None and os.path.isdir(self.runtime_dir):
            shutil.rmtree(self.runtime_dir)
        self.snapshots.release_persistence_lock()

        if self._port_lease is not None:
            self._port_lease.close()
            self._port_lease = None

    def destroy(self):
        self.teardown()
