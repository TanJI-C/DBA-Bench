import ast
import json
import hashlib
import math
import os
import re
import shutil
import socket
import subprocess
import tempfile
import time
import shlex
import uuid
from datetime import datetime, timedelta, timezone
from copy import deepcopy
from collections.abc import Mapping
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any, List

import yaml


TIKV_STORAGE_MAINTENANCE_PROCEDURE = "recover-mvcc"


def lightning_network_alias(run_id: str) -> str:
    """Short in-network DNS name for the Case-owned Lightning container.

    The container name is ``{run_id}-lightning`` which easily exceeds the 63-byte
    DNS label limit, so Prometheus can never resolve it. Containers get this
    deterministic alias instead, and the Prometheus scrape target uses it.
    """
    return f"rg05-lg-{hashlib.sha1(run_id.encode('utf-8')).hexdigest()[:12]}"


def lightning_job_id(run_id: str) -> str:
    """Opaque run-scoped Lightning job id, uniform in shape with seeded decoy ids.

    Registry triage must not leak which job is the incident through naming:
    every job id — active or decoy — is ``lightning-job/`` plus a 12-hex token,
    so length, prefix clusters, and list order carry no signal. The frozen
    history series keys reuse this id so agents can bind a job to its history.
    """
    return f"lightning-job/{hashlib.sha256(run_id.encode('utf-8')).hexdigest()[:12]}"


def lightning_decoy_job_id(run_id: str, index: int) -> str:
    """Frozen-history job id for seeded batch decoy ``index`` (1-based).

    The controller's registry seeding and the history assembler must derive
    the same ids so every decoy job owns its frozen lightning series.
    """
    return lightning_job_id(f"{run_id}-batch{index:02d}")


class _TiDBReadinessFatalError(RuntimeError):
    pass


class PersistentBaselineIdentityMismatch(RuntimeError):
    """A persistent baseline was produced under a different cluster identity.

    The baseline is a cache of a Case's initial cluster state; a mismatching
    copy is a cache miss that the deployment rebuilds, not a hard failure.
    """


def canonical_pd_config(config: Mapping[str, object]) -> dict[str, object]:
    normalized = deepcopy(dict(config))
    for key in (
        "client-urls",
        "peer-urls",
        "advertise-client-urls",
        "advertise-peer-urls",
        "name",
    ):
        normalized.pop(key, None)
    metric = normalized.get("metric")
    if metric is not None:
        if not isinstance(metric, dict):
            raise TypeError(f"PD config metric must be an object: metric={metric!r}")
        metric.pop("job", None)
    return normalized


def _render_toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    raise TypeError(f"Unsupported TiKV config override value: value={value!r}")


def _render_toml_sections(sections: Mapping[str, Mapping[str, object]]) -> str:
    blocks = []
    for section, keys in sections.items():
        lines = [f"[{section}]"]
        lines.extend(f"{key} = {_render_toml_value(value)}" for key, value in keys.items())
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


class BaseDeployment(ABC):
    """
    部署层抽象。
    职责：承载底层服务的运行容器或集群，提供标准化的部署/销毁接口。
    """
    @abstractmethod
    def deploy(self):
        """部署服务"""
        pass

    @abstractmethod
    def teardown(self):
        """销毁服务"""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """检查服务是否就绪"""
        pass


class PGDockerDeployment(BaseDeployment):
    """
    PostgreSQL Docker 部署器。
    """

    DATASET_INIT_TIMEOUT_SECONDS = 600
    POSTGRES_HISTORY_PATH_TIMEOUT_SECONDS = 60
    POSTGRES_HISTORY_READ_TIMEOUT_SECONDS = 120
    POSTGRES_COMPATIBILITY_LOG_PATH = "/var/log/postgresql/postgresql.log"

    DEFAULT_RESOURCES = {
        # 512MB/1CPU 是"小公司 staging PG"的真实规格：Light TPC-DS 能在 30s timeout 内跑完，
        # 同时保留故障触发空间（Heavy 仍 spill）。
        # disk_quota 8192 与 TPCDSWorkload 默认一致——校准负载的 temp 写入在更小配额下会爆盘；
        # docker --storage-opt 配额在 run 时注入，不动 fault image。
        "cpus": 1.0,
        "memory_mb": 512,
        "shm_size": "256m",
        "disk_quota_mb": 8192,
    }

    WORKLOAD_DISK_QUOTA = {
        "tpcds": 8192,
        "tpcdsx": 8192,
        "default": 2048,
        "demo": 2048,
    }

    def __init__(self,
                 container_name: str = "aiopsbench-pg",
                 resources: Optional[Dict[str, Any]] = None,
                 postgres_user: str = "postgres",
                 postgres_password: str = "password",
                 postgres_db: str = "testdb",
                 port: int = 5432,
                 init_sql_path: Optional[str] = None,
                 workload_data_dir: Optional[str] = None,
                 dataset_manifest_path: Optional[str] = None,
                 image_name: Optional[str] = None,
                 postgres_runtime_options: Optional[str] = None,
                 data_volume_name: Optional[str] = None,
                 data_volume_root: Optional[str] = None,
                 network_name: Optional[str] = None,
                 volume_name: Optional[str] = None,
                 initialization_timeout_seconds: int = 600):
        self.container_name = container_name
        self.resources = resources or self.DEFAULT_RESOURCES.copy()
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password
        self.postgres_db = postgres_db
        self.port = port
        self.workload_data_dir = workload_data_dir
        if dataset_manifest_path is None and workload_data_dir is not None:
            dataset_manifest_path = str(Path(workload_data_dir).parent / "manifest.json")
        self.dataset_manifest_path = dataset_manifest_path
        self.image_name = image_name or "aiopsbench-pg-initialized:latest"
        self.postgres_runtime_options = postgres_runtime_options
        self.data_volume_name = data_volume_name
        self.data_volume_root = os.path.abspath(data_volume_root) if data_volume_root else None
        self.network_name = network_name
        self._owned_data_volume = False
        self.volume_name = volume_name
        # 大数据集 COPY 初始化在高负载共享主机上可能超过默认 600s；允许运行侧通过
        # 环境变量放宽初始化等待，不改变任何默认行为。
        self.initialization_timeout_seconds = int(
            os.environ.get(
                "AIOPS_INITIALIZATION_TIMEOUT_SECONDS", initialization_timeout_seconds
            )
        )
        self._owned_network = False
        self._owned_volume = False
        self.pgdata = "/var/lib/postgresql/data_fat"

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if init_sql_path is None:
            init_sql_path = os.path.join(project_root, "scripts", "init.sql")
        self.init_sql_path = init_sql_path
        self.entrypoint_path = os.path.join(project_root, "config", "docker", "pg-entrypoint.sh")

    def _is_initialized(self) -> bool:
        result = subprocess.run(
            ["docker", "image", "inspect", self.image_name],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return False
        if self.workload_data_dir is None:
            return True
        image = json.loads(result.stdout)[0]
        labels = image.get("Config", {}).get("Labels") or {}
        return labels.get("aiopsbench.dataset_ready") == self._dataset_ready_label()

    def _dataset_ready_label(self) -> str:
        if self.workload_data_dir is None:
            raise RuntimeError(
                "Dataset readiness label requested without workload data: "
                f"image_name={self.image_name!r}"
            )
        manifest_path = Path(self.dataset_manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        required = {
            "workload_name", "scale", "required_tables", "data_files", "init_sql_sha256", "schema_sha256",
            "schema_source", "dataset_fingerprint",
        }
        if set(manifest) < required:
            raise ValueError(
                "Dataset manifest is incomplete: "
                f"path={manifest_path}, missing={sorted(required - set(manifest))}"
            )
        if not isinstance(manifest["scale"], int) or manifest["scale"] <= 0:
            raise ValueError(f"Dataset manifest scale is invalid: path={manifest_path}, scale={manifest['scale']!r}")
        required_tables = manifest["required_tables"]
        data_files = manifest["data_files"]
        if not isinstance(required_tables, list) or not required_tables or not isinstance(data_files, dict):
            raise ValueError(
                "Dataset manifest table contract is invalid: "
                f"path={manifest_path}, required_tables={required_tables!r}, data_files={data_files!r}"
            )
        expected_files = {f"{table}.dat" for table in required_tables}
        if set(data_files) != expected_files:
            raise ValueError(
                "Dataset manifest file set does not match required tables: "
                f"path={manifest_path}, expected={sorted(expected_files)}, actual={sorted(data_files)}"
            )
        for filename, metadata in data_files.items():
            data_path = Path(self.workload_data_dir) / filename
            if not data_path.is_file():
                raise FileNotFoundError(
                    "Dataset manifest references a missing data file: "
                    f"manifest={manifest_path}, filename={filename!r}, path={data_path}"
                )
            if data_path.stat().st_size != metadata["size_bytes"]:
                raise RuntimeError(
                    "Dataset data file size differs from manifest: "
                    f"filename={filename!r}, expected={metadata['size_bytes']}, actual={data_path.stat().st_size}"
                )
            digest = hashlib.sha256(data_path.read_bytes()).hexdigest()
            if digest != metadata["sha256"]:
                raise RuntimeError(
                    "Dataset data file hash differs from manifest: "
                    f"filename={filename!r}, expected={metadata['sha256']!r}, actual={digest!r}"
                )
        init_path = Path(self.init_sql_path)
        init_digest = hashlib.sha256(init_path.read_bytes()).hexdigest()
        if init_digest != manifest["init_sql_sha256"]:
            raise RuntimeError(
                "Dataset init SQL hash differs from manifest: "
                f"path={init_path}, expected={manifest['init_sql_sha256']!r}, actual={init_digest!r}"
            )
        schema_path = Path(self.workload_data_dir).parent / "tpcds-kit" / "tools" / "tpcds.sql"
        if manifest["schema_source"] == "tpcds.sql":
            if not schema_path.is_file():
                raise FileNotFoundError(
                    "Dataset manifest requires the TPC-DS schema source, but it is missing: "
                    f"manifest={manifest_path}, path={schema_path}"
                )
            schema_digest = hashlib.sha256(schema_path.read_bytes()).hexdigest()
        elif manifest["schema_source"] == "init.sql":
            schema_digest = init_digest
        else:
            raise ValueError(
                "Dataset manifest has an unsupported schema source: "
                f"manifest={manifest_path}, schema_source={manifest['schema_source']!r}"
            )
        if schema_digest != manifest["schema_sha256"]:
            raise RuntimeError(
                "Dataset schema hash differs from manifest: "
                f"manifest={manifest_path}, expected={manifest['schema_sha256']!r}, actual={schema_digest!r}"
            )
        fingerprint_payload = {key: value for key, value in manifest.items() if key != "dataset_fingerprint"}
        computed_fingerprint = hashlib.sha256(
            json.dumps(fingerprint_payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
        ).hexdigest()
        if computed_fingerprint != manifest["dataset_fingerprint"]:
            raise RuntimeError(
                "Dataset manifest fingerprint is inconsistent: "
                f"path={manifest_path}, expected={manifest['dataset_fingerprint']!r}, actual={computed_fingerprint!r}"
            )
        fingerprint = manifest["dataset_fingerprint"]
        if not isinstance(fingerprint, str) or len(fingerprint) != 64:
            raise ValueError(
                "Dataset manifest fingerprint is invalid: "
                f"path={manifest_path}, fingerprint={fingerprint!r}"
            )
        return f"{manifest['workload_name']}-ready-v3-{fingerprint[:16]}"

    @staticmethod
    def image_exists(image_name: str) -> bool:
        result = subprocess.run(
            ["docker", "image", "inspect", image_name],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _build_docker_run_command(self, for_init: bool = False) -> list:
        cmd = [
            "docker", "run", "-d",
            "--name", self.container_name,
            "-e", f"POSTGRES_USER={self.postgres_user}",
            "-e", f"POSTGRES_PASSWORD={self.postgres_password}",
            "-e", f"POSTGRES_DB={self.postgres_db}",
            "-e", f"PGDATA={self.pgdata}",
            "-p", f"{self.port}:5432",
        ]
        if self.network_name:
            cmd.extend(["--network", self.network_name])
        if self.volume_name:
            # Keep the benchmark-owned volume outside PGDATA so snapshots remain
            # image-based while the resource itself still has an explicit owner.
            cmd.extend(["--mount", f"type=volume,source={self.volume_name},target=/aiopsbench_runtime"])
        if self.postgres_runtime_options:
            cmd.extend(["-e", f"POSTGRES_RUNTIME_OPTIONS={self.postgres_runtime_options}"])
        pg_nofile_limit = self.resources.get("pg_nofile_limit")
        if pg_nofile_limit:
            cmd.extend(["-e", f"PG_NOFILE_LIMIT={pg_nofile_limit}"])

        if for_init:
            if self.workload_data_dir:
                abs_workload_data = os.path.abspath(self.workload_data_dir)
                cmd.extend(["-v", f"{abs_workload_data}:/workload_data"])

            if os.path.exists(self.init_sql_path):
                abs_init_sql = os.path.abspath(self.init_sql_path)
                cmd.extend(["-v", f"{abs_init_sql}:/docker-entrypoint-initdb.d/init.sql"])

            # harness 鲁棒性：fat 镜像 entrypoint 装载完成后用 pg_ctl 关闭
            # 临时 server，默认 60s 等待窗口（PGCTLTIMEOUT）在宿主机 IO 争用下
            # 会被 shutdown checkpoint 超过（实测容器 exit 1，数据装载本身
            # 已完成）；放宽等待只影响初始化时长。
            cmd.extend(["-e", "PGCTLTIMEOUT=600"])
            cmd.append("postgres:16")
            cmd.extend(["-c", "shared_buffers=1GB", "-c", "work_mem=64MB", "-c", "shared_preload_libraries=pg_stat_statements"])
        else:
            if self.data_volume_name:
                # Mount by volume name so both root-backed bind volumes and
                # plain named volumes resolve through the same Docker path.
                cmd.extend(["-v", f"{self.data_volume_name}:{self.pgdata}"])
            cmd.insert(3, "--init")
            isolation_values = {
                "AIOPS_CPUSET_CPUS": os.environ.get("AIOPS_CPUSET_CPUS"),
                "AIOPS_CPUSET_MEMS": os.environ.get("AIOPS_CPUSET_MEMS"),
                "AIOPS_CPU_LIMIT": os.environ.get("AIOPS_CPU_LIMIT"),
                "AIOPS_MEMORY_MB": os.environ.get("AIOPS_MEMORY_MB"),
            }
            if any(isolation_values.values()) and not all(isolation_values.values()):
                raise RuntimeError(
                    "PostgreSQL worker isolation requires all resource variables: "
                    f"{isolation_values}"
                )
            cpus = (
                float(isolation_values["AIOPS_CPU_LIMIT"])
                if isolation_values["AIOPS_CPU_LIMIT"]
                else self.resources.get("cpus", 0.5)
            )
            cmd.extend(["--cpus", str(cpus)])
            mem_mb = (
                int(isolation_values["AIOPS_MEMORY_MB"])
                if isolation_values["AIOPS_MEMORY_MB"]
                else self.resources.get("memory_mb", 256)
            )
            cmd.extend(["--memory", f"{mem_mb}m"])
            cmd.extend(["--memory-swap", f"{mem_mb}m"])
            shm_size = self.resources.get("shm_size", "64m")
            cmd.extend(["--shm-size", str(shm_size)])

            cpuset_cpus = isolation_values["AIOPS_CPUSET_CPUS"]
            cpuset_mems = isolation_values["AIOPS_CPUSET_MEMS"]
            if cpuset_cpus:
                cmd.extend(["--cpuset-cpus", cpuset_cpus])
                cmd.extend(["--cpuset-mems", cpuset_mems])

            # 磁盘配额：--storage-opt size 限制容器可写层大小，df 原生显示配额。
            disk_quota_mb = self.resources.get("disk_quota_mb")
            if disk_quota_mb:
                cmd.extend(["--storage-opt", f"size={disk_quota_mb}m"])

            tmpfs_mounts = self.resources.get("tmpfs_mounts", [])
            if isinstance(tmpfs_mounts, str):
                tmpfs_mounts = [tmpfs_mounts]
            for tmpfs_mount in tmpfs_mounts:
                cmd.extend(["--tmpfs", str(tmpfs_mount)])

            if os.path.exists(self.entrypoint_path):
                cmd.extend(["-v", f"{os.path.abspath(self.entrypoint_path)}:/pg-entrypoint.sh:ro"])

            for capability in self.resources.get("cap_add", []):
                cmd.extend(["--cap-add", str(capability)])

            cmd.append(self.image_name)
            cmd.extend(["bash", "/pg-entrypoint.sh"])

        return cmd

    def _ensure_owned_docker_resource(self, resource_type: str, resource_name: str, owner: str) -> None:
        """Create or validate one explicitly assigned per-run Docker resource."""
        if not resource_name:
            return
        inspected = subprocess.run(
            ["docker", resource_type, "inspect", resource_name],
            capture_output=True,
            text=True,
        )
        if inspected.returncode != 0:
            subprocess.run(
                [
                    "docker", resource_type, "create",
                    "--label", f"aiopsbench.owner={owner}", resource_name,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            return
        try:
            labels = (json.loads(inspected.stdout)[0] or {}).get("Labels") or {}
        except (ValueError, IndexError, TypeError):
            labels = {}
        if labels.get("aiopsbench.owner") != owner:
            raise RuntimeError(
                f"Refusing to reuse unowned Docker {resource_type}: {resource_name!r}"
            )

    def _ensure_owned_resources(self) -> None:
        """Create or validate the named resources owned by this deployment."""
        network_owner = "partition-cleanup" if self.data_volume_name else "pg-hc-mf01"
        if self.network_name:
            self._ensure_owned_docker_resource("network", self.network_name, network_owner)
            self._owned_network = True
        if self.data_volume_name:
            if self.data_volume_root:
                # The PGDATA volume must be a named local volume backed by the
                # host path: Docker populates an empty named volume from the
                # image on first use, while a plain bind mount would shadow the
                # image's initialized cluster with an empty directory.
                host_path = os.path.join(self.data_volume_root, self.data_volume_name)
                os.makedirs(host_path, mode=0o770, exist_ok=True)
                inspected = subprocess.run(
                    ["docker", "volume", "inspect", self.data_volume_name],
                    capture_output=True,
                    text=True,
                )
                if inspected.returncode != 0:
                    subprocess.run(
                        [
                            "docker", "volume", "create",
                            "--driver", "local",
                            "--opt", "type=none",
                            "--opt", f"device={host_path}",
                            "--opt", "o=bind",
                            "--label", "aiopsbench.owner=partition-cleanup",
                            self.data_volume_name,
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                else:
                    try:
                        volume = json.loads(inspected.stdout)[0]
                    except (ValueError, IndexError, TypeError) as exc:
                        raise RuntimeError(
                            f"Cannot inspect PostgreSQL data volume: volume={self.data_volume_name!r}"
                        ) from exc
                    labels = volume.get("Labels") or {}
                    options = volume.get("Options") or {}
                    expected = {"type": "none", "device": host_path, "o": "bind"}
                    if labels.get("aiopsbench.owner") != "partition-cleanup" or options != expected:
                        raise RuntimeError(
                            "Refusing to reuse PostgreSQL data volume with a different owner or storage path: "
                            f"volume={self.data_volume_name!r}, options={options!r}, expected={expected!r}"
                        )
            else:
                self._ensure_owned_docker_resource("volume", self.data_volume_name, "partition-cleanup")
            self._owned_data_volume = True
        if self.volume_name:
            self._ensure_owned_docker_resource("volume", self.volume_name, "pg-hc-mf01")
            self._owned_volume = True

    def _prepare_dataset_image_contents(self):
        """准备进程级管理所需的文件。"""
        subprocess.run([
            "docker", "exec", self.container_name,
            "bash", "-c", "mkdir -p /var/log/postgresql && chown postgres:postgres /var/log/postgresql"
        ], capture_output=True)

        # 将权威 entrypoint 拷入容器，使随后提交的数据集镜像自包含。
        # 与运行时 -v 挂载同源（config/docker/pg-entrypoint.sh），避免两份副本漂移。
        if os.path.exists(self.entrypoint_path):
            subprocess.run([
                "docker", "cp", self.entrypoint_path,
                f"{self.container_name}:/pg-entrypoint.sh"
            ], capture_output=True)
            subprocess.run([
                "docker", "exec", self.container_name,
                "chmod", "+x", "/pg-entrypoint.sh"
            ], capture_output=True)
        else:
            print(f"[Deployment] Warning: entrypoint not found at {self.entrypoint_path}; "
                  f"image will rely on runtime mount.")

    def _sql_ready(self) -> bool:
        """Check readiness with a real SQL round trip, not only pg_isready."""
        try:
            result = subprocess.run(
                [
                    "docker", "exec", self.container_name,
                    "psql", "-U", self.postgres_user, "-d", self.postgres_db,
                    "-v", "ON_ERROR_STOP=1", "-Atqc", "SELECT 1",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0 and result.stdout.strip() == "1"
        except (OSError, subprocess.SubprocessError):
            return False

    def initialize_dataset_container(self):
        print(f"[Deployment] Initializing PostgreSQL dataset container for image '{self.image_name}'...")
        self._ensure_owned_resources()
        subprocess.run(["docker", "rm", "-f", self.container_name], capture_output=True)
        if os.path.exists(self.init_sql_path):
            os.chmod(self.init_sql_path, 0o644)

        cmd = self._build_docker_run_command(for_init=True)
        print(f"[Deployment] Starting init container... CMD: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"[Deployment] Error: {e.stderr.decode() if e.stderr else str(e)}")
            raise

        print(f"[Deployment] Waiting for initialization to complete...")
        start_time = time.time()
        while time.time() - start_time < self.initialization_timeout_seconds:
            res = subprocess.run(
                f"docker logs {self.container_name} 2>&1 | grep 'PostgreSQL init process complete; ready for start up.'",
                shell=True, capture_output=True, text=True
            )
            if res.stdout.strip():
                break
            # A large COPY workload can finish successfully but exceed the
            # image entrypoint's graceful-shutdown window.  In that case the
            # restart policy re-enters the existing data directory and emits
            # the skip-initialization marker instead of the normal completion
            # marker.  Accept that recovery path only after a clean log and a
            # ready server; an init.sql error must still fail the deployment.
            logs = subprocess.run(
                ["docker", "logs", self.container_name],
                capture_output=True,
                text=True,
            ).stdout
            lowered_logs = logs.casefold()
            if "psql:" in lowered_logs and (
                "error:" in lowered_logs
                or "error " in lowered_logs
                or "permission denied" in lowered_logs
            ):
                raise RuntimeError(
                    "PostgreSQL workload initialization failed: "
                    f"{logs[-4000:]}"
                )
            if (
                "PostgreSQL Database directory appears to contain a database; Skipping initialization" in logs
                and self._sql_ready()
            ):
                print("[Deployment] Initialization recovered from a completed data directory restart.")
                break
            # The stock postgres entrypoint can finish a large init.sql but
            # return after its shutdown checkpoint exceeds the stop window.
            # Restart that same task-owned container so the existing recovery
            # branch can verify SQL readiness without treating a clean import
            # as an initialization timeout.
            if "pg_ctl: server does not shut down" in logs and not self.is_container_running():
                restarted = subprocess.run(
                    ["docker", "start", self.container_name],
                    capture_output=True,
                    text=True,
                )
                if restarted.returncode != 0:
                    raise RuntimeError(
                        "PostgreSQL initialization container could not be restarted after "
                        f"a completed import: container={self.container_name!r}, "
                        f"error={restarted.stderr.strip()}"
                    )
                print("[Deployment] Restarted the completed initialization container for SQL readiness.")
            time.sleep(5)
        else:
            raise RuntimeError(
                "Timeout waiting for initialization to complete: "
                f"timeout_seconds={self.initialization_timeout_seconds}"
            )

        ready_deadline = time.time() + min(max(self.initialization_timeout_seconds, 60), 300)
        while time.time() < ready_deadline:
            if self._sql_ready():
                break
            time.sleep(2)
        else:
            raise RuntimeError("PostgreSQL initialization completed but SQL is not ready")

        print(f"[Deployment] Initialization complete. Installing pg_stat_statements extension...")
        result = subprocess.run([
            "docker", "exec", self.container_name,
            "psql", "-U", self.postgres_user, "-d", self.postgres_db,
            "-c", "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"
        ], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to install pg_stat_statements in container {self.container_name} "
                f"for dataset image {self.image_name}: {result.stderr.strip()}"
            )

        self._prepare_dataset_image_contents()

    def deploy(self):
        if not self._is_initialized():
            self.initialize_dataset_container()
            subprocess.run(
                ["docker", "stop", "-t", "30", self.container_name],
                check=True,
                capture_output=True,
            )
            result = subprocess.run(
                [
                    "docker", "commit",
                    "--change", f"LABEL aiopsbench.dataset_ready={self._dataset_ready_label()}",
                    self.container_name,
                    self.image_name,
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"docker commit failed for dataset image {self.image_name}: {result.stderr.strip()}"
                )
            subprocess.run(
                ["docker", "rm", "-f", self.container_name],
                check=True,
                capture_output=True,
            )
        print(f"[Deployment] Image '{self.image_name}' exists, starting container")

        self._ensure_owned_resources()

        if self.is_container_running():
            if self.is_ready():
                print(f"[Deployment] Container already running and PG ready")
                return
            else:
                print(f"[Deployment] Container running but PG not ready, starting PG...")
                self.start_pg()
                return

        subprocess.run(["docker", "rm", "-f", self.container_name], capture_output=True)

        cmd = self._build_docker_run_command(for_init=False)
        print(f"[Deployment] Starting container... CMD: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"[Deployment] Error starting container: {e.stderr.decode() if e.stderr else str(e)}")
            raise

        print(f"[Deployment] Container {self.container_name} started")

    def is_ready(self) -> bool:
        try:
            result = subprocess.run(
                ["docker", "exec", self.container_name,
                 "pg_isready", "-h", "localhost", "-p", "5432", "-U", self.postgres_user],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def wait_for_ready(self, timeout: int = 60) -> bool:
        print(f"[Deployment] Waiting for PostgreSQL to be ready (timeout={timeout}s)...")
        start = time.time()
        while time.time() - start < timeout:
            # pg_isready can succeed while the configured application
            # database is still unavailable; require the same SQL round trip
            # PGEnv will use before declaring deployment ready.
            if self.is_ready() and self._sql_ready():
                elapsed = int(time.time() - start)
                print(f"[Deployment] PostgreSQL ready in {elapsed}s")
                time.sleep(1)
                return True
            time.sleep(1)
        print(f"[Deployment] Timeout waiting for PostgreSQL")
        return False

    def read_logs(self, lines: int = 200) -> str:
        """Read the bounded PostgreSQL log stream exposed by the container."""
        if not isinstance(lines, int) or isinstance(lines, bool) or lines <= 0:
            raise ValueError(f"PostgreSQL log line limit must be positive: lines={lines!r}")
        result = subprocess.run(
            ["docker", "logs", "--timestamps", "--tail", str(lines), self.container_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"PostgreSQL Docker log read failed: container={self.container_name!r}, "
                f"returncode={result.returncode}, stderr={result.stderr.strip()!r}"
            )
        return result.stdout + result.stderr

    def _postgres_log_paths(self) -> tuple[str, ...]:
        result = subprocess.run(
            [
                "docker", "exec", self.container_name,
                "sh", "-c",
                "find /var/log/postgresql -maxdepth 1 -type f -name 'postgresql*.log' -print | sort",
            ],
            capture_output=True,
            text=True,
            timeout=self.POSTGRES_HISTORY_PATH_TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"PostgreSQL log file enumeration failed: container={self.container_name!r}, "
                f"returncode={result.returncode}, stderr={result.stderr.strip()!r}"
            )
        paths = tuple(path for path in result.stdout.splitlines() if path)
        if not paths:
            raise RuntimeError(
                f"PostgreSQL log file enumeration returned no files: container={self.container_name!r}, "
                f"directory='/var/log/postgresql'"
            )
        return paths

    def _postgres_log_sizes_for_paths(self, paths: tuple[str, ...]) -> dict[str, int]:
        result = subprocess.run(
            [
                "docker", "exec", self.container_name,
                "sh", "-c",
                'for path do printf "%s\\t" "$path"; wc -c < "$path"; done',
                "sh",
                *paths,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"PostgreSQL log size read failed: container={self.container_name!r}, "
                f"files={paths!r}, returncode={result.returncode}, stderr={result.stderr.strip()!r}"
            )
        sizes: dict[str, int] = {}
        for line in result.stdout.splitlines():
            path, raw_size = line.split("\t", 1)
            if path not in paths or path in sizes or not raw_size.strip().isdigit():
                raise RuntimeError(
                    f"PostgreSQL log size output is invalid: container={self.container_name!r}, "
                    f"files={paths!r}, line={line!r}"
                )
            sizes[path] = int(raw_size.strip())
        if tuple(sorted(sizes)) != tuple(sorted(paths)):
            raise RuntimeError(
                f"PostgreSQL log size output is incomplete: container={self.container_name!r}, "
                f"files={paths!r}, sizes={sizes!r}"
            )
        return sizes

    def postgres_log_sizes(self) -> dict[str, int]:
        """Return the current byte size of every PostgreSQL log file."""
        paths = self._postgres_log_paths()
        return self._postgres_log_sizes_for_paths(paths)

    def read_postgres_logs_after(self, offsets: dict[str, int]) -> tuple[str, dict[str, int]]:
        """Read bytes appended after a per-file PostgreSQL log snapshot."""
        paths = self._postgres_log_paths()
        sizes = self._postgres_log_sizes_for_paths(paths)
        missing = tuple(sorted(set(offsets) - set(sizes)))
        if missing:
            raise RuntimeError(
                f"PostgreSQL log file disappeared since the visible snapshot: "
                f"container={self.container_name!r}, missing_files={missing!r}, offsets={offsets!r}"
            )
        shrinking = {
            path: (offsets[path], sizes[path])
            for path in offsets
            if path in sizes and sizes[path] < offsets[path]
        }
        if shrinking:
            raise RuntimeError(
                f"PostgreSQL log file shrank since the visible snapshot: "
                f"container={self.container_name!r}, files={shrinking!r}"
            )
        chunks = []
        for path in paths:
            offset = offsets.get(path, 0)
            if offset < 0:
                raise ValueError(
                    f"PostgreSQL log offset must be non-negative: container={self.container_name!r}, "
                    f"path={path!r}, offset={offset}"
                )
            if sizes[path] == offset:
                continue
            result = subprocess.run(
                ["docker", "exec", self.container_name, "tail", "-c", f"+{offset + 1}", path],
                capture_output=True,
                text=True,
                timeout=self.POSTGRES_HISTORY_READ_TIMEOUT_SECONDS,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"PostgreSQL visible log read failed: container={self.container_name!r}, "
                    f"path={path!r}, offset={offset}, returncode={result.returncode}, "
                    f"stderr={result.stderr.strip()!r}"
                )
            chunks.append(result.stdout)
        return "".join(chunks), sizes

    def publish_postgres_log_compatibility_snapshot(self, content: str) -> dict[str, int]:
        """Expose an unfiltered real log interval through the legacy fixed path."""
        if not isinstance(content, str) or not content:
            raise ValueError(
                "PostgreSQL compatibility log snapshot content must be non-empty text: "
                f"container={self.container_name!r}, content_type={type(content).__name__}, "
                f"content_length={len(content) if isinstance(content, str) else None}"
            )
        result = subprocess.run(
            [
                "docker", "exec", "-i", self.container_name,
                "sh", "-c",
                f"cat > {self.POSTGRES_COMPATIBILITY_LOG_PATH}",
            ],
            input=content,
            capture_output=True,
            text=True,
            timeout=self.POSTGRES_HISTORY_READ_TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "PostgreSQL compatibility log snapshot failed: "
                f"container={self.container_name!r}, content_length={len(content)}, "
                f"returncode={result.returncode}, stderr={result.stderr.strip()!r}"
            )
        return self.postgres_log_sizes()

    def read_logs_at_range(self, start_epoch_ms: int, end_epoch_ms: int) -> str:
        """Read and merge PostgreSQL log files for the exact capture interval."""
        if not isinstance(start_epoch_ms, int) or isinstance(start_epoch_ms, bool):
            raise TypeError(f"PostgreSQL log start must be an epoch millisecond integer: start_epoch_ms={start_epoch_ms!r}")
        if not isinstance(end_epoch_ms, int) or isinstance(end_epoch_ms, bool):
            raise TypeError(f"PostgreSQL log end must be an epoch millisecond integer: end_epoch_ms={end_epoch_ms!r}")
        if start_epoch_ms >= end_epoch_ms:
            raise ValueError(
                f"PostgreSQL log capture range must be positive: container={self.container_name!r}, "
                f"start_epoch_ms={start_epoch_ms}, end_epoch_ms={end_epoch_ms}"
            )
        start = datetime.fromtimestamp(start_epoch_ms / 1000, tz=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        end = datetime.fromtimestamp(end_epoch_ms / 1000, tz=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        result = subprocess.run(
            [
                "docker", "logs", "--timestamps",
                "--since", start,
                "--until", end,
                self.container_name,
            ],
            capture_output=True,
            text=True,
            timeout=self.POSTGRES_HISTORY_READ_TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"PostgreSQL Docker log range read failed: container={self.container_name!r}, "
                f"start_epoch_ms={start_epoch_ms}, end_epoch_ms={end_epoch_ms}, "
                f"returncode={result.returncode}, stderr={result.stderr.strip()!r}"
            )
        docker_stream = result.stdout + result.stderr
        paths = self._postgres_log_paths()
        merged = subprocess.run(
            ["docker", "exec", self.container_name, "cat", *paths],
            capture_output=True,
            text=True,
            timeout=self.POSTGRES_HISTORY_READ_TIMEOUT_SECONDS,
        )
        if merged.returncode != 0:
            raise RuntimeError(
                f"PostgreSQL log file read failed: container={self.container_name!r}, files={paths!r}, "
                f"returncode={merged.returncode}, stderr={merged.stderr.strip()!r}"
            )
        return docker_stream + merged.stdout

    def teardown(self):
        print(f"[Deployment] Tearing down {self.container_name}...")
        data_volume_path = None
        if self.data_volume_name and self._owned_data_volume and self.data_volume_root:
            data_volume_path = os.path.join(self.data_volume_root, self.data_volume_name)
            if os.path.exists(data_volume_path):
                subprocess.run(
                    ["docker", "exec", self.container_name, "bash", "-c", f"chmod -R a+rwX -- {shlex.quote(self.pgdata)}"],
                    capture_output=True,
                    text=True,
                )
        subprocess.run(["docker", "rm", "-f", self.container_name], capture_output=True)
        if self.data_volume_name and self._owned_data_volume:
            subprocess.run(["docker", "volume", "rm", "-f", self.data_volume_name], capture_output=True)
        if self.volume_name and self._owned_volume:
            subprocess.run(["docker", "volume", "rm", "-f", self.volume_name], capture_output=True)
        if self.network_name and self._owned_network:
            subprocess.run(["docker", "network", "rm", self.network_name], capture_output=True)
        if data_volume_path:
            shutil.rmtree(data_volume_path, ignore_errors=True)
            if os.path.exists(data_volume_path):
                raise RuntimeError(
                    "PostgreSQL deployment cleanup left its host data directory: "
                    f"container={self.container_name!r}, path={data_volume_path!r}"
                )
        print(f"[Deployment] Container removed (image preserved)")

    def force_teardown(self):
        """Orchestrator timed-out-cleanup fallback; remove the same resource set as teardown()."""
        self.teardown()

    def _pg_ctl_cmd(self, action_args: str) -> list:
        """构造 pg_ctl 命令，自动探测容器内 PG 版本路径。"""
        detect = "PG_BIN=$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1)"
        apply_nofile = (
            "PG_NOFILE_RUNTIME=${PG_NOFILE_LIMIT:-}; "
            "if [ -f /etc/aiopsbench_pg_nofile_limit ]; then "
            "PG_NOFILE_RUNTIME=$(cat /etc/aiopsbench_pg_nofile_limit); "
            "fi; "
            "PG_CTL_PREFIX=''; "
            "if [ -n \"$PG_NOFILE_RUNTIME\" ]; then "
            "PG_CTL_PREFIX=\"ulimit -n $PG_NOFILE_RUNTIME && \"; "
            "fi"
        )
        return [
            "docker", "exec", self.container_name,
            "bash", "-c",
            f'{detect} && {apply_nofile} && su - postgres -c "$PG_CTL_PREFIX$PG_BIN/pg_ctl {action_args}"'
        ]

    def _pg_start_args(self) -> str:
        return (
            f"start -D {self.pgdata} "
            f"-l /var/log/postgresql/postgresql.log "
            f"-o {shlex.quote(self._pg_runtime_options())}"
        )

    def _pg_runtime_options(self) -> str:
        # 512MB/1CPU 容器下的 PG 内参。work_mem 8MB 让中等排序/hash 直接 spill
        # → 30s timeout 也跑不完；提到 16MB 让 Light/Medium TPC-DS 不 spill 跑通，
        # 但 Heavy（5+ 表 join / 大 sort）仍 spill → 故障仍触发。
        return self.postgres_runtime_options or (
            "-c shared_buffers=128MB -c work_mem=16MB "
            "-c shared_preload_libraries=pg_stat_statements "
            "-c logging_collector=on -c log_destination=stderr "
            "-c log_directory=/var/log/postgresql "
            "-c log_filename=postgresql-%Y-%m-%d_%H%M%S.log "
            "-c log_rotation_age=1d -c log_rotation_size=100MB"
        )

    def set_pg_nofile_limit(self, value: int) -> bool:
        """Persist the PostgreSQL process nofile soft limit for future start/restart."""
        result = subprocess.run(
            [
                "docker", "exec", self.container_name,
                "bash", "-c",
                f"printf '%s\\n' {int(value)} > /etc/aiopsbench_pg_nofile_limit",
            ],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0

    def reset_pg_nofile_limit(self) -> bool:
        result = subprocess.run(
            ["docker", "exec", self.container_name, "rm", "-f", "/etc/aiopsbench_pg_nofile_limit"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0

    def apply_pg_nofile_limit_runtime(self, value: int) -> bool:
        """Apply a nofile soft limit to the currently running postmaster."""
        result = subprocess.run(
            [
                "docker", "exec", self.container_name,
                "bash", "-c",
                (
                    f"PID=$(head -1 {self.pgdata}/postmaster.pid 2>/dev/null || true); "
                    "test -n \"$PID\" || exit 1; "
                    "HARD=$(awk '/Max open files/ {print $5}' /proc/$PID/limits); "
                    "if [ -z \"$HARD\" ] || [ \"$HARD\" = unlimited ]; then HARD=1048576; fi; "
                    f"prlimit --pid \"$PID\" --nofile={int(value)}:$HARD"
                ),
            ],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            print(f"[Deployment] Failed to apply runtime nofile limit: {result.stderr.strip()}")
        return result.returncode == 0

    def get_pg_nofile_limit(self) -> Dict[str, Any]:
        """Return configured and currently running PostgreSQL nofile limits."""
        result = subprocess.run(
            [
                "docker", "exec", self.container_name,
                "bash", "-c",
                (
                    "CONFIG=''; "
                    "if [ -f /etc/aiopsbench_pg_nofile_limit ]; then CONFIG=$(cat /etc/aiopsbench_pg_nofile_limit); fi; "
                    f"PID=$(head -1 {self.pgdata}/postmaster.pid 2>/dev/null || true); "
                    "SOFT=''; HARD=''; "
                    "if [ -n \"$PID\" ] && [ -r \"/proc/$PID/limits\" ]; then "
                    "read _ _ _ SOFT HARD _ < <(grep 'Max open files' /proc/$PID/limits); "
                    "fi; "
                    "printf '%s|%s|%s\\n' \"$CONFIG\" \"$SOFT\" \"$HARD\""
                ),
            ],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return {"status": "error", "error": result.stderr.strip()}
        parts = (result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "||").split("|")
        while len(parts) < 3:
            parts.append("")
        return {
            "status": "success",
            "configured": parts[0] or "(default)",
            "running_soft": parts[1] or "(unknown)",
            "running_hard": parts[2] or "(unknown)",
        }

    def stop_pg(self) -> bool:
        """停止容器内的 PG 进程（容器保持运行）"""
        try:
            result = subprocess.run(
                self._pg_ctl_cmd(f"stop -D {self.pgdata} -m fast"),
                capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("[Deployment] pg_ctl fast stop timed out.")
            return False

    def start_pg(self) -> bool:
        """启动容器内的 PG 进程"""
        timeout = int(self.resources.get("pg_ctl_start_timeout_sec", 30))
        result = subprocess.run(
            self._pg_ctl_cmd(self._pg_start_args()),
            capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0

    def restart_pg(self) -> bool:
        """重启容器内的 PG 进程"""
        timeout = int(self.resources.get("pg_ctl_restart_timeout_sec", 120))
        try:
            result = subprocess.run(
                self._pg_ctl_cmd(
                    f"restart -D {self.pgdata} -m fast "
                    f"-l /var/log/postgresql/postgresql.log "
                    f"-o {shlex.quote(self._pg_runtime_options())}"
                ),
                capture_output=True, text=True, timeout=timeout
            )
            if result.returncode == 0:
                return True
            print(f"[Deployment] pg_ctl fast restart failed; falling back to immediate process restart: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print("[Deployment] pg_ctl fast restart timed out; falling back to immediate process restart.")

        recovery_wait = int(self.resources.get("pg_ctl_recovery_wait_sec", 0))
        if recovery_wait > 0 and self.wait_for_ready(timeout=recovery_wait):
            return True

        # OOM/crash-recovery 场景中 fast shutdown 可能长时间等待 fsync。
        # 这里仍然只重启 PostgreSQL 进程，不重启 Docker 容器。
        try:
            subprocess.run(
                self._pg_ctl_cmd(f"stop -D {self.pgdata} -m immediate"),
                capture_output=True, text=True, timeout=30
            )
        except subprocess.TimeoutExpired:
            print("[Deployment] pg_ctl immediate stop timed out.")

        try:
            start_timeout = int(self.resources.get("pg_ctl_start_timeout_sec", 30))
            result = subprocess.run(
                self._pg_ctl_cmd(self._pg_start_args()),
                capture_output=True, text=True, timeout=start_timeout
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("[Deployment] pg_ctl start timed out after immediate stop.")
            return False

    def is_container_running(self) -> bool:
        """检查容器是否在运行（不关心 PG 状态）"""
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", self.container_name],
            capture_output=True, text=True
        )
        return result.stdout.strip() == "true"

    def reboot_machine(self) -> bool:
        """模拟机器重启：docker stop + docker start（保留文件系统）"""
        subprocess.run(["docker", "stop", "-t", "10", self.container_name],
                       capture_output=True)
        result = subprocess.run(["docker", "start", self.container_name],
                                capture_output=True)
        return result.returncode == 0


class TiDBDockerDeployment(BaseDeployment):
    """Run an isolated case-defined TiDB topology with Docker Compose."""
    ONLINE_UNSAFE_RECOVERY_TIMEOUT_SECONDS = 300
    _MVCC_DATA_PREFIX_HEX = "7A"
    _MVCC_DATA_MAX_HEX = "7B"
    BOOTSTRAP_CACHE_VERSION = 1
    IMAGE_GROUP_VERSION = 1
    NETWORK_SUBNET_PREFIX = "10.252"
    NETWORK_TOOL_IMAGE = (
        "docker.m.daocloud.io/nicolaka/netshoot@"
        "sha256:b09d9b21381f47a79b3cbcb30da25266dc17186ea00ae65e99fdc51396f48e70"
    )
    MONITORING_IMAGES = (
        "prom/prometheus@sha256:f20d3127bf2876f4a1df76246fca576b41ddf1125ed1c546fbd8b16ea55117e6",
        "m.daocloud.io/gcr.io/cadvisor/cadvisor@sha256:f40e65878e25c2e78ea037f73a449527a0fb994e303dc3e34cb6b187b4b91435",
    )
    MIN_DISK_BYTES = 20 * 1024**3
    PORT_BLOCK_PROBE_LIMIT = 64
    _MAX_HOST_PORT = 65535
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
        self.network_subnet = self._network_subnet(run_id)
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
        self.storage_key = storage_key
        self.storage_root = Path(storage_root).resolve() if storage_root else None
        self.tikv_shared_volume_root = None
        self.image_group_key = image_group_key
        self.image_group_disabled = False
        self.tidb_readiness_timeout_sec = tidb_readiness_timeout_sec
        self.warm_tidb_readiness_timeout_sec = warm_tidb_readiness_timeout_sec
        self.persistent_state_reused = False
        self._persistent_state_pending = False
        self._persistent_lock = None
        self._persistent_base_dir = None
        self._persistent_baseline_dir = None
        self._persistent_run_dir = None
        self._last_readiness_error = None
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        self._component_image_overrides: dict[str, str] = {}
        self._upgrade_audit: list[dict[str, object]] = []
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
        self._port_hold_sockets: list[socket.socket] = []
        self._env = dict(os.environ)
        self.bootstrap_cache_root = self._env.get(
            "AIOPS_TIDB_BOOTSTRAP_CACHE_DIR",
            os.path.join(root, "data", "tidb", "bootstrap-cache"),
        )
        self.bootstrap_cache_key = None
        self.bootstrap_cache_path = None
        self.bootstrap_cache_used = False
        self.bootstrap_cache_enabled = True
        self.bootstrap_data_paths = {}
        self.image_group_root = Path(
            self._env.get(
                "AIOPS_TIDB_IMAGE_GROUP_DIR",
                os.path.join(root, "data", "tidb", "image-groups"),
            )
        ).resolve()
        self.image_group_fingerprint = None
        self.image_group_name = None
        self.image_group_dir = None
        self.image_group_metadata_path = None
        self.image_group_metadata = None
        self.image_group_images = {}
        self.image_group_tikv_config_path = None
        self.image_group_selected = False
        self.image_group_reused = False
        self._image_group_lock = None
        self._maintenance_audit: list[dict[str, object]] = []
        self._pd_recovery_artifact: dict[str, object] | None = None
        self._pd_recovery_audit: list[dict[str, object]] = []
        self.online_unsafe_recovery_started = False
        self._pd_ingress_sources: dict[str, set[str]] = {}
        self._pd_response_egress_targets: dict[str, set[str]] = {}
        self._pd_response_egress_shadow_targets: dict[str, set[str]] = {}
        self._tidb_stale_egress_targets: dict[str, tuple[str, ...]] = {}
        self._tidb_egress_shadow_targets: dict[str, tuple[str, ...]] = {}
        self._tidb_pd_network_rehydration_targets: dict[str, tuple[str, ...]] = {}
        self._tidb_pd_network_rehydration_addresses: dict[str, tuple[str, ...]] = {}
        self._mvcc_inspections: dict[str, dict[str, object]] = {}
        self._mvcc_tool_metadata_cache: dict[str, dict[str, str]] = {}

    @property
    def primary_tidb_endpoint(self) -> tuple[str, int]:
        return "127.0.0.1", self.port_base

    @property
    def network_name(self) -> str:
        return f"{self.project_name}_default"

    @classmethod
    def _network_subnet(cls, run_id: str) -> str:
        subnet_octet = int(hashlib.sha256(run_id.encode()).hexdigest()[:2], 16)
        return f"{cls.NETWORK_SUBNET_PREFIX}.{subnet_octet}.0/24"

    def _port_block_span(self) -> int:
        span = self.topology.tidb_count * 2 + 1
        if self.replication_runtime is not None:
            span += 1 + self.replication_runtime.ticdc_count
        return span

    @staticmethod
    def _port_bindable(port: int) -> bool:
        with socket.socket() as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                return False
        return True

    def _select_free_port_block(self) -> int:
        """Shift the planned host port block forward until its full span is bindable.

        Chunk manifests reuse static port segments across concurrently running
        experiments, so the planned base can already be bound by another run's
        cluster. Host port publication is not part of the scenario contract; the
        endpoints re-derive from the selected block before compose rendering.
        The selected block stays bound by held sockets until the cluster start
        releases them right before compose up, closing the window in which a
        concurrent experiment could claim the same ports.
        """
        span = self._port_block_span()
        blocked_attempts: list[tuple[int, tuple[int, ...]]] = []
        start = self.port_base
        for _ in range(self.PORT_BLOCK_PROBE_LIMIT):
            if start + span - 1 > self._MAX_HOST_PORT:
                break
            conflicts = tuple(
                port for port in range(start, start + span) if not self._port_bindable(port)
            )
            if not conflicts:
                holds = []
                try:
                    for port in range(start, start + span):
                        sock = socket.socket()
                        sock.bind(("127.0.0.1", port))
                        holds.append(sock)
                except OSError:
                    for held in holds:
                        held.close()
                    blocked_attempts.append((start, ("lost during hold",)))
                    start += span
                    continue
                self._port_hold_sockets = holds
                if start != self.port_base:
                    print(
                        f"[Deployment] TiDB port block shifted: run_id={self.run_id!r}, "
                        f"planned={self.port_base}, selected={start}, span={span}"
                    )
                return start
            blocked_attempts.append((start, conflicts))
            start += span
        raise RuntimeError(
            f"TiDB port block selection exhausted: run_id={self.run_id!r}, "
            f"planned={self.port_base!r}, span={span}, blocked_attempts={blocked_attempts!r}"
        )

    def _release_port_holds(self) -> None:
        while self._port_hold_sockets:
            self._port_hold_sockets.pop().close()

    def configure_runtime(self, runtime) -> None:
        if self.topology is not None:
            raise RuntimeError(f"TiDB runtime is already configured: run_id={self.run_id!r}")
        if runtime.image_group_key is not None:
            if self.storage_key is not None:
                raise ValueError(
                    f"TiDB storage_key and runtime image_group_key are mutually exclusive: "
                    f"run_id={self.run_id!r}, storage_key={self.storage_key!r}, "
                    f"image_group_key={runtime.image_group_key!r}"
                )
            if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", runtime.image_group_key):
                raise ValueError(
                    f"Invalid TiDB runtime image_group_key {runtime.image_group_key!r}; "
                    "use lowercase letters, digits, '_' or '-'"
                )
            if self.image_group_key is not None and self.image_group_key != runtime.image_group_key:
                raise ValueError(
                    f"TiDB image_group_key mismatch: run_id={self.run_id!r}, "
                    f"deployment={self.image_group_key!r}, runtime={runtime.image_group_key!r}"
                )
            self.image_group_key = runtime.image_group_key
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
        if self.tikv_config_writable and self.image_group_enabled:
            raise ValueError(
                "Writable TiKV config cannot use a shared image group config: "
                f"run_id={self.run_id!r}, image_group_key={self.image_group_key!r}"
            )
        if self.tikv_store_zones and len(self.tikv_store_zones) != self.topology.tikv_count:
            raise ValueError(
                "TiDB runtime TikKV zone count must match topology: "
                f"run_id={self.run_id!r}, zones={self.tikv_store_zones!r}, "
                f"tikv_count={self.topology.tikv_count}"
            )
        if self.tikv_store_zones and self.image_group_enabled:
            raise ValueError(
                "TiDB per-store labels cannot use an image group with one shared TiKV config: "
                f"run_id={self.run_id!r}, image_group_key={self.image_group_key!r}"
            )
        self.bootstrap_cache_enabled = runtime.bootstrap_cache_enabled
        self._container_ids.clear()
        if self.tidb_readiness_timeout_sec == 1800:
            self.tidb_readiness_timeout_sec = runtime.readiness_timeout_seconds
        self.upgrade_release = runtime.upgrade_release
        self.pd_cpu_limit = runtime.pd_cpu_limit
        self.port_base = self._select_free_port_block()
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
        if self.image_group_enabled:
            self._configure_image_group()
        else:
            self._configure_bootstrap_cache()
        if self.storage_key is not None:
            self._persistent_base_dir = self.storage_root / self.storage_key
            self._persistent_baseline_dir = self._persistent_base_dir / "baseline"
            self._persistent_run_dir = self._persistent_base_dir / "runs" / self.run_id
            self._persistent_run_dir.mkdir(parents=True, exist_ok=True)
        self._maintenance_audit = []
        self._render_runtime_files()

    @property
    def persistent_storage_enabled(self) -> bool:
        return self.storage_key is not None

    @property
    def image_group_enabled(self) -> bool:
        return self.image_group_key is not None and not self.image_group_disabled

    def disable_image_group(self) -> None:
        """停用 image group：部署回落 bootstrap cache 体系。

        orchestrator 在 fault_snapshot=off 时调用（off 模式不会 select/save
        故障镜像）。用独立标志而非清 key——configure_runtime 会从 case runtime
        重新采纳 image_group_key，清 key 会被覆盖。已 configure 的部署在停用后
        重新走 bootstrap 分支并重渲染 compose。
        """
        self.image_group_disabled = True
        if self.topology is not None:
            if self.bootstrap_cache_path is None:
                self._configure_bootstrap_cache()
            self._render_runtime_files()

    def _image_group_base_metadata(self) -> dict[str, object]:
        if not self.image_group_enabled:
            raise RuntimeError(f"TiDB image group is not configured: run_id={self.run_id!r}")
        if self.release is None or self.topology is None:
            raise RuntimeError(f"TiDB runtime is not configured: run_id={self.run_id!r}")
        config_dir = os.path.dirname(self.compose_template)
        tikv_config_path = self.image_group_tikv_config_path
        if tikv_config_path is None:
            raise RuntimeError(
                f"TiDB image-group TiKV config is not prepared: run_id={self.run_id!r}"
            )
        return {
            "version": self.IMAGE_GROUP_VERSION,
            "image_group_key": self.image_group_key,
            "release_version": self.release.version,
            "images": list(self._release_images()),
            "topology": {
                "pd_count": self.topology.pd_count,
                "tikv_count": self.topology.tikv_count,
                "tidb_count": self.topology.tidb_count,
                "tiflash_count": self.topology.tiflash_count,
            },
            "config_digests": {
                "pd.toml": self._sha256_file(os.path.join(config_dir, "config", "pd.toml")),
                "tikv.toml": self._sha256_file(tikv_config_path),
            },
        }

    def _configure_image_group(self) -> None:
        config_dir = os.path.dirname(self.compose_template)
        self.image_group_tikv_config_path = os.path.join(self.runtime_dir, "tikv-image-group.toml")
        tikv_config = Path(os.path.join(config_dir, "config", "tikv.toml")).read_text(encoding="utf-8")
        Path(self.image_group_tikv_config_path).write_text(
            f'{tikv_config.rstrip()}\n\n[raftstore]\ncapacity = "8GB"\n',
            encoding="utf-8",
        )
        metadata = self._image_group_base_metadata()
        encoded = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode()
        self.image_group_fingerprint = hashlib.sha256(encoded).hexdigest()[:24]
        self.image_group_dir = (
            self.image_group_root / self.image_group_key / self.image_group_fingerprint
        )
        self.image_group_metadata_path = self.image_group_dir / "metadata.json"
        repository = f"aiopsbench-tidb-group-{self.image_group_key}-{self.image_group_fingerprint}"
        self.image_group_name = f"{repository}:latest"
        self.image_group_images = {
            service: f"{repository}-{service}:latest"
            for service in (*self.COMPONENTS["pd"], *self.COMPONENTS["tikv"])
        }
        self.image_group_metadata = {
            **metadata,
            "fingerprint": self.image_group_fingerprint,
            "snapshot_name": self.image_group_name,
            "component_images": self.image_group_images,
        }

    def _validate_image_group(self, snapshot_name: str) -> bool:
        if not self.image_group_enabled:
            raise RuntimeError(
                f"TiDB image group is not configured: run_id={self.run_id!r}, snapshot={snapshot_name!r}"
            )
        if snapshot_name != self.image_group_name:
            raise RuntimeError(
                f"TiDB image group identity mismatch: run_id={self.run_id!r}, "
                f"expected={self.image_group_name!r}, actual={snapshot_name!r}"
            )
        if not self.image_group_metadata_path.is_file():
            return False
        actual = json.loads(self.image_group_metadata_path.read_text(encoding="utf-8"))
        if actual != self.image_group_metadata:
            raise RuntimeError(
                f"TiDB image group metadata mismatch: run_id={self.run_id!r}, "
                f"snapshot={snapshot_name!r}, expected={self.image_group_metadata!r}, actual={actual!r}"
            )
        missing = [
            image
            for image in self.image_group_images.values()
            if subprocess.run(
                ["docker", "image", "inspect", image],
                capture_output=True,
                env=self._env,
            ).returncode != 0
        ]
        if missing:
            raise RuntimeError(
                f"TiDB image group is incomplete: run_id={self.run_id!r}, "
                f"snapshot={snapshot_name!r}, missing_images={missing!r}"
            )
        return True

    def image_group_snapshot_name(self) -> Optional[str]:
        return self.image_group_name if self.image_group_enabled else None

    def base_image_snapshot_name(self) -> Optional[str]:
        if not self.image_group_enabled:
            return None
        return f"{self.image_group_name}-base"

    def image_group_exists(self, snapshot_name: str) -> bool:
        return self._validate_image_group(snapshot_name)

    def select_image_group(self, snapshot_name: str, base_snapshot_name: str) -> None:
        if not self._validate_image_group(snapshot_name):
            raise RuntimeError(
                f"Cannot select missing TiDB image group: run_id={self.run_id!r}, "
                f"snapshot={snapshot_name!r}, base_snapshot={base_snapshot_name!r}"
            )
        self.image_group_selected = True
        self.image_group_reused = True
        self._render_runtime_files()

    def _acquire_image_group_lock(self) -> None:
        if not self.image_group_enabled:
            return
        if self._image_group_lock is not None:
            raise RuntimeError(f"TiDB image group lock is already held: run_id={self.run_id!r}")
        import fcntl

        self.image_group_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self.image_group_dir / ".lock"
        self._image_group_lock = lock_path.open("a+", encoding="utf-8")
        fcntl.flock(self._image_group_lock.fileno(), fcntl.LOCK_EX)

    def release_image_group_lock(self) -> None:
        if self._image_group_lock is None:
            return
        import fcntl

        fcntl.flock(self._image_group_lock.fileno(), fcntl.LOCK_UN)
        self._image_group_lock.close()
        self._image_group_lock = None

    def save_image_group(self, snapshot_name: str, _labels: Dict[str, str]) -> None:
        if not self.image_group_enabled:
            raise RuntimeError(
                f"TiDB image group is not configured: run_id={self.run_id!r}, snapshot={snapshot_name!r}"
            )
        self._acquire_image_group_lock()
        try:
            if self._validate_image_group(snapshot_name):
                raise RuntimeError(
                    f"TiDB image group already exists: run_id={self.run_id!r}, snapshot={snapshot_name!r}"
                )
            database_services = [
                *self.COMPONENTS["tidb"],
                *self.COMPONENTS["tikv"],
                *self.COMPONENTS["pd"],
            ]
            self._run(
                self._compose + ["stop", "--timeout", "120", *database_services],
                "image-group",
            )
            for service in (*self.COMPONENTS["pd"], *self.COMPONENTS["tikv"]):
                container_id = self._service_container_id(service)
                image = self.image_group_images[service]
                self._run(
                    [
                        "docker", "commit",
                        "--change", f"LABEL aiopsbench.tidb.image_group={self.image_group_name}",
                        container_id,
                        image,
                    ],
                    service,
                )
            self.image_group_dir.mkdir(parents=True, exist_ok=True)
            self.image_group_metadata_path.write_text(
                json.dumps(self.image_group_metadata, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            self.image_group_selected = True
            self.image_group_reused = True
            self._render_runtime_files()
            self._container_ids.clear()
            self._start_database_services()
            print(
                f"[Deployment] TiDB image group saved: run_id={self.run_id!r}, "
                f"snapshot={self.image_group_name!r}"
            )
        finally:
            self.release_image_group_lock()

    def _persistent_metadata_path(self) -> Path:
        if self._persistent_baseline_dir is None:
            raise RuntimeError(f"TiDB persistent storage is not configured: run_id={self.run_id!r}")
        return self._persistent_baseline_dir / "metadata.json"

    def _persistent_metadata(self) -> dict[str, object]:
        if self.release is None:
            raise RuntimeError(f"TiDB release is not configured: run_id={self.run_id!r}")
        return {
            "version": 2,
            "storage_key": self.storage_key,
            "release": {
                "pd_image": self.release.pd_image,
                "tikv_image": self.release.tikv_image,
                "tidb_image": self.release.tidb_image,
            },
            "topology": {
                "pd": self.topology.pd_count,
                "tikv": self.topology.tikv_count,
                "tidb": self.topology.tidb_count,
            },
        }

    def _validate_persistent_metadata(self) -> None:
        metadata_path = self._persistent_metadata_path()
        if not metadata_path.is_file():
            raise RuntimeError(
                f"TiDB persistent baseline is incomplete: run_id={self.run_id!r}, "
                f"storage_key={self.storage_key!r}, missing={str(metadata_path)!r}"
            )
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        expected = self._persistent_metadata()
        if metadata != expected:
            raise PersistentBaselineIdentityMismatch(
                f"TiDB persistent baseline identity mismatch: run_id={self.run_id!r}, "
                f"storage_key={self.storage_key!r}, expected={expected!r}, actual={metadata!r}"
            )
        for service in (*self.COMPONENTS["pd"], *self.COMPONENTS["tikv"]):
            path = self._persistent_baseline_dir / service
            if not path.is_dir():
                raise RuntimeError(
                    f"TiDB persistent baseline is incomplete: run_id={self.run_id!r}, "
                    f"storage_key={self.storage_key!r}, service={service!r}, path={str(path)!r}"
                )

    def _acquire_persistent_lock(self) -> None:
        if not self.persistent_storage_enabled:
            return
        import fcntl

        lock_path = self._persistent_base_dir / ".lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._persistent_lock = lock_path.open("a+", encoding="utf-8")
        fcntl.flock(self._persistent_lock.fileno(), fcntl.LOCK_EX)

    def release_persistence_lock(self) -> None:
        if self._persistent_lock is None:
            return
        import fcntl

        fcntl.flock(self._persistent_lock.fileno(), fcntl.LOCK_UN)
        self._persistent_lock.close()
        self._persistent_lock = None

    def _prepare_persistent_state(self) -> None:
        if not self.persistent_storage_enabled:
            return
        self._acquire_persistent_lock()
        baseline_exists = self._persistent_baseline_dir.exists()
        metadata_exists = self._persistent_metadata_path().exists()
        if baseline_exists != metadata_exists:
            raise RuntimeError(
                f"TiDB persistent baseline is partially present: run_id={self.run_id!r}, "
                f"storage_key={self.storage_key!r}, baseline_exists={baseline_exists}, "
                f"metadata_exists={metadata_exists}"
            )
        if baseline_exists:
            try:
                self._validate_persistent_metadata()
            except PersistentBaselineIdentityMismatch as error:
                print(
                    f"[Deployment] TiDB persistent baseline identity mismatch; rebuilding from scratch: "
                    f"run_id={self.run_id!r}, storage_key={self.storage_key!r}, error={error!r}"
                )
                shutil.rmtree(self._persistent_baseline_dir)
                baseline_exists = False
            else:
                if self._persistent_run_dir.exists():
                    shutil.rmtree(self._persistent_run_dir)
                self._persistent_run_dir.mkdir(parents=True)
                for service in (*self.COMPONENTS["pd"], *self.COMPONENTS["tikv"]):
                    shutil.copytree(
                        self._persistent_baseline_dir / service,
                        self._persistent_run_dir / service,
                    )
                self.persistent_state_reused = True
                self.release_persistence_lock()
                print(
                    f"[Deployment] Reusing TiDB persistent baseline: storage_key={self.storage_key!r}, "
                    f"run_id={self.run_id!r}"
                )
                return
        if self._persistent_run_dir.exists():
            shutil.rmtree(self._persistent_run_dir)
        self._persistent_run_dir.mkdir(parents=True)
        for service in (*self.COMPONENTS["pd"], *self.COMPONENTS["tikv"]):
            (self._persistent_run_dir / service).mkdir()
        self._persistent_state_pending = True
        print(
            f"[Deployment] Creating TiDB persistent baseline: storage_key={self.storage_key!r}, "
            f"run_id={self.run_id!r}"
        )

    def _make_persistent_state_user_accessible(self) -> None:
        if self._persistent_run_dir is None:
            raise RuntimeError(f"TiDB persistent run directory is not configured: run_id={self.run_id!r}")
        if self.release is None:
            raise RuntimeError(f"TiDB release is not configured: run_id={self.run_id!r}")
        self._normalize_host_directory(
            self._persistent_run_dir,
            self.release.pd_image,
            f"persistent state for storage_key={self.storage_key!r}",
        )

    def _normalize_host_directory(self, path: Path | str, image: str, description: str) -> None:
        command = [
            "docker", "run", "--rm", "--user", "0:0", "--entrypoint", "/bin/sh",
            "-v", f"{path}:/state",
            image,
            "-c", "chmod -R a+rwX /state",
        ]
        result = subprocess.run(command, capture_output=True, text=True, env=self._env)
        if result.returncode != 0:
            raise RuntimeError(
                f"TiDB host directory permission normalization failed: description={description!r}, "
                f"path={str(path)!r}, returncode={result.returncode}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )

    def persist_initial_state(self) -> None:
        if not self._persistent_state_pending:
            return
        if self._persistent_lock is None:
            raise RuntimeError(
                f"TiDB persistent baseline lock is not held: run_id={self.run_id!r}, "
                f"storage_key={self.storage_key!r}"
            )
        self._make_persistent_state_user_accessible()
        self._run(
            self._compose + ["stop", "--timeout", "120", *self.COMPONENTS["tidb"]],
            "persistent-baseline",
        )
        self._run(
            self._compose + [
                "stop", "--timeout", "120",
                *self.COMPONENTS["tikv"], *self.COMPONENTS["pd"],
            ],
            "persistent-baseline",
        )
        if self._persistent_baseline_dir.exists():
            raise RuntimeError(
                f"TiDB persistent baseline appeared during initialization: run_id={self.run_id!r}, "
                f"storage_key={self.storage_key!r}"
            )
        self._persistent_baseline_dir.mkdir(parents=True)
        for service in (*self.COMPONENTS["pd"], *self.COMPONENTS["tikv"]):
            shutil.copytree(
                self._persistent_run_dir / service,
                self._persistent_baseline_dir / service,
            )
        metadata_path = self._persistent_metadata_path()
        metadata_path.write_text(
            json.dumps(self._persistent_metadata(), ensure_ascii=True, sort_keys=True),
            encoding="utf-8",
        )
        self._start_database_services()
        self._persistent_state_pending = False
        print(
            f"[Deployment] TiDB persistent baseline saved: storage_key={self.storage_key!r}, "
            f"path={str(self._persistent_baseline_dir)!r}"
        )

    @staticmethod
    def _sha256_file(path: str) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

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
        if self.image_group_selected:
            images = (
                *(self.image_group_images[service] for service in self.COMPONENTS["pd"]),
                *(self.image_group_images[service] for service in self.COMPONENTS["tikv"]),
                self.release.tidb_image,
                *(([self.release.tiflash_image]) if self.topology.tiflash_count else []),
            )
        else:
            images = self._release_images()
        if self.replication_runtime is not None:
            images = (*images, self.replication_runtime.ticdc_image, self.replication_runtime.downstream_image)
        return images

    def _component_image(self, node_type: str, service: str) -> str:
        override = self._component_image_overrides.get(service)
        if override is not None:
            return override
        if self.image_group_selected and node_type in {"pd", "tikv"}:
            return self.image_group_images[service]
        return {
            "pd": self.release.pd_image,
            "tikv": self.release.tikv_image,
            "tidb": self.release.tidb_image,
            "tiflash": self.release.tiflash_image,
        }[node_type]

    def _bootstrap_cache_metadata(self) -> dict:
        config_dir = os.path.dirname(self.compose_template)
        metadata = {
            "cache_version": self.BOOTSTRAP_CACHE_VERSION,
            "release_version": self.release.version,
            "images": list(self._release_images()),
            "topology": {
                "pd_count": self.topology.pd_count,
                "tikv_count": self.topology.tikv_count,
                "tidb_count": self.topology.tidb_count,
                "tiflash_count": self.topology.tiflash_count,
            },
            "config_digests": {
                "pd.toml": self._sha256_file(os.path.join(config_dir, "config", "pd.toml")),
                "tikv.toml": self._sha256_file(os.path.join(config_dir, "config", "tikv.toml")),
            },
        }
        encoded = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode()
        metadata["cache_key"] = hashlib.sha256(encoded).hexdigest()[:24]
        return metadata

    def _configure_bootstrap_cache(self) -> None:
        # Deferred topologies never boot the full TiKV set, so a cache saved by
        # a same-shape full topology would seed PD with stores that can never
        # come up: system regions lose quorum and tidb-server FATALs on start.
        # They therefore cold-start unconditionally, exactly like a disabled cache.
        if not self.bootstrap_cache_enabled or self.topology.deferred_tikv_count > 0:
            mode = "disabled" if not self.bootstrap_cache_enabled else "deferred-topology"
            for node_type, services in (("pd", self.COMPONENTS["pd"]), ("tikv", self.COMPONENTS["tikv"])):
                for service in services:
                    destination = os.path.join(self.runtime_dir, "data", node_type, service)
                    os.makedirs(destination)
                    self.bootstrap_data_paths[(node_type, service)] = destination
            print(
                f"[Deployment] TiDB bootstrap cache: run_id={self.run_id!r}, mode={mode!r}"
            )
            return
        metadata = self._bootstrap_cache_metadata()
        self.bootstrap_cache_key = metadata["cache_key"]
        self.bootstrap_cache_path = os.path.join(
            self.bootstrap_cache_root,
            self.bootstrap_cache_key,
        )
        marker_path = os.path.join(self.bootstrap_cache_path, "metadata.json")
        if os.path.exists(self.bootstrap_cache_path) and not os.path.isfile(marker_path):
            raise RuntimeError(
                f"TiDB bootstrap cache is incomplete: run_id={self.run_id!r}, "
                f"cache_path={self.bootstrap_cache_path!r}, marker={marker_path!r}"
            )
        if os.path.isfile(marker_path):
            with open(marker_path, encoding="utf-8") as handle:
                cached_metadata = json.load(handle)
            if cached_metadata != metadata:
                raise RuntimeError(
                    f"TiDB bootstrap cache metadata mismatch: run_id={self.run_id!r}, "
                    f"cache_path={self.bootstrap_cache_path!r}, expected={metadata!r}, "
                    f"actual={cached_metadata!r}"
                )
            self.bootstrap_cache_used = True

        for node_type, services in (("pd", self.COMPONENTS["pd"]), ("tikv", self.COMPONENTS["tikv"])):
            for service in services:
                source = os.path.join(self.bootstrap_cache_path, node_type, service)
                destination = os.path.join(self.runtime_dir, "data", node_type, service)
                os.makedirs(destination)
                if self.bootstrap_cache_used:
                    self._copy_tree(source, destination)
                self.bootstrap_data_paths[(node_type, service)] = destination
        print(
            f"[Deployment] TiDB bootstrap cache: run_id={self.run_id!r}, "
            f"mode={'hit' if self.bootstrap_cache_used else 'miss'}, key={self.bootstrap_cache_key!r}, "
            f"path={self.bootstrap_cache_path!r}"
        )

    @staticmethod
    def _copy_tree(source: str, destination: str) -> None:
        result = subprocess.run(
            ["cp", "-a", "--reflink=auto", f"{source}/.", destination],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"TiDB bootstrap data copy failed: source={source!r}, destination={destination!r}, "
                f"returncode={result.returncode}, stdout={result.stdout.strip()!r}, "
                f"stderr={result.stderr.strip()!r}"
            )

    def _snapshot_component_data(self, service: str, node_type: str, destination: str) -> None:
        container_id = self._service_container_id(service)
        archive_path = os.path.join(os.path.dirname(destination), f".{service}.tar")
        with open(archive_path, "wb") as archive:
            result = subprocess.run(
                ["docker", "cp", f"{container_id}:/data/{node_type}/.", "-"],
                stdout=archive,
                stderr=subprocess.PIPE,
            )
        if result.returncode != 0:
            raise RuntimeError(
                f"TiDB bootstrap data snapshot failed: service={service!r}, node_type={node_type!r}, "
                f"container_id={container_id!r}, returncode={result.returncode}, "
                f"stderr={result.stderr.decode(errors='replace').strip()!r}"
            )
        result = subprocess.run(
            ["tar", "--no-same-owner", "-xf", archive_path, "-C", destination],
            capture_output=True,
            text=True,
        )
        os.remove(archive_path)
        if result.returncode != 0:
            raise RuntimeError(
                f"TiDB bootstrap data snapshot extraction failed: service={service!r}, "
                f"node_type={node_type!r}, destination={destination!r}, returncode={result.returncode}, "
                f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
            )

    def _save_bootstrap_cache(self) -> None:
        if not self.bootstrap_cache_enabled:
            raise RuntimeError(
                f"TiDB bootstrap cache is disabled for this runtime: run_id={self.run_id!r}"
            )
        if self.bootstrap_cache_used:
            return
        if os.path.exists(self.bootstrap_cache_path):
            raise RuntimeError(
                f"TiDB bootstrap cache appeared during deployment: run_id={self.run_id!r}, "
                f"cache_path={self.bootstrap_cache_path!r}"
            )
        os.makedirs(self.bootstrap_cache_root, exist_ok=True)
        temporary_cache = tempfile.mkdtemp(
            prefix=f".{self.bootstrap_cache_key}-",
            dir=self.bootstrap_cache_root,
        )
        database_services = [
            *self.COMPONENTS["tidb"],
            *self.COMPONENTS["tikv"],
            *self.COMPONENTS["pd"],
        ]
        self._run(self._compose + ["stop", *database_services], "bootstrap-cache")
        self._container_ids.clear()
        for node_type, services in (("pd", self.COMPONENTS["pd"]), ("tikv", self.COMPONENTS["tikv"])):
            for service in services:
                destination = os.path.join(temporary_cache, node_type, service)
                os.makedirs(destination)
                self._snapshot_component_data(service, node_type, destination)
        metadata = self._bootstrap_cache_metadata()
        with open(os.path.join(temporary_cache, "metadata.json"), "w", encoding="utf-8") as handle:
            json.dump(metadata, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary_cache, self.bootstrap_cache_path)
        self.bootstrap_cache_used = True
        self._run(self._compose + ["start", *self.COMPONENTS["pd"]], "bootstrap-cache")
        self._container_ids.clear()
        self._wait("pd", self._check_pd, 120)
        self._start_tikv_services(("start",))
        for index, service in enumerate(self.COMPONENTS["tidb"]):
            target = f"tidb/{service}"
            self._run(self._compose + ["start", service], target)
            self._container_ids.clear()
            self._wait_tidb_target(target, self._tidb_readiness_timeout(index))
        self._wait(
            "prometheus",
            self._check_prometheus,
            self._prometheus_readiness_timeout(),
        )

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
            if self.persistent_storage_enabled:
                node["volumes"].append(f"{self._persistent_run_dir / service}:/data/pd")
            elif not self.image_group_enabled:
                pd_data_path = self.bootstrap_data_paths[("pd", service)]
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
                if self.image_group_enabled
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
            if self.image_group_enabled:
                node["volumes"] = [
                    (
                        f"{self.image_group_tikv_config_path}:/tikv.toml:ro"
                        if volume.split(":", 1)[1] == "/tikv.toml:ro"
                        else volume
                    )
                    for volume in node["volumes"]
                ]
            if not self.image_group_enabled:
                if self.persistent_storage_enabled:
                    node["volumes"].append(f"{self._persistent_run_dir / service}:/data/tikv")
                else:
                    tikv_data_path = self.bootstrap_data_paths[("tikv", service)]
                    node["volumes"].append(f"{tikv_data_path}:/data/tikv")
            if self.tikv_shared_volume_root is not None:
                node["volumes"].append(f"{self.tikv_shared_volume_root}:/backup")
            node["mem_limit"] = f"{self.tikv_memory_mb}m"
            node["memswap_limit"] = f"{self.tikv_memory_mb}m"
            node["init"] = True
            node["user"] = "0:0" if self.image_group_enabled else f"{os.getuid()}:{os.getgid()}"
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
        inspected = subprocess.run(
            ["docker", "network", "inspect", self.network_name],
            capture_output=True,
            text=True,
            env=self._env,
        )
        if inspected.returncode == 0:
            raise RuntimeError(
                f"TiDB network identity already exists: run_id={self.run_id!r}, "
                f"network={self.network_name!r}, subnet={self.network_subnet!r}"
            )
        if inspected.returncode != 1:
            raise RuntimeError(
                f"TiDB network inspection failed: run_id={self.run_id!r}, "
                f"network={self.network_name!r}, returncode={inspected.returncode}, "
                f"stdout={inspected.stdout.strip()!r}, stderr={inspected.stderr.strip()!r}"
            )
        self._run(
            [
                "docker",
                "network",
                "create",
                "--driver",
                "bridge",
                "--subnet",
                self.network_subnet,
                self.network_name,
            ],
            "network",
        )
        self._network_created = True

    def _readiness_diagnostics(self, label: str) -> dict:
        if label == "pd":
            services = self.COMPONENTS["pd"]
        elif label == "tikv":
            services = self.COMPONENTS["pd"] + self.COMPONENTS["tikv"]
        elif label.startswith("tidb/"):
            services = (label.split("/", 1)[1],)
        elif label == "prometheus":
            services = self.COMPONENTS["monitoring"]
        else:
            services = tuple(self.NODES.values())
        diagnostics = {}
        for service in services:
            container_id = self._service_container_id(service)
            state = json.loads(
                self._run(
                    ["docker", "inspect", "--format", "{{json .State}}", container_id],
                    service,
                )
            )
            logs = self._run(
                self._compose + ["logs", "--no-color", "--timestamps", "--tail", "30", service],
                service,
            )
            diagnostics[service] = {
                "status": state["Status"],
                "running": state["Running"],
                "exit_code": state["ExitCode"],
                "oom_killed": state["OOMKilled"],
                "logs_tail": logs,
            }
        return diagnostics

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

    def pd_identity_observation(self) -> dict[str, object]:
        """Return raw PD identity and topology observations for recovery cases."""
        cluster = self.pd_request("GET", "/pd/api/v1/cluster")
        cluster_status = self.pd_request("GET", "/pd/api/v1/cluster/status")
        members = self.pd_request("GET", "/pd/api/v1/members")
        leader = self.pd_request("GET", "/pd/api/v1/leader")
        return {
            "cluster": cluster,
            "cluster_status": cluster_status,
            "members": members,
            "leader": leader,
        }

    @staticmethod
    def _directory_inventory(path: Path) -> dict[str, int]:
        if not path.is_dir():
            raise RuntimeError(f"TiDB data directory is missing: path={path}")
        files = [item for item in path.rglob("*") if item.is_file()]
        return {
            "file_count": len(files),
            "bytes": sum(item.stat().st_size for item in files),
        }

    def _pd_data_paths(self) -> tuple[Path, ...]:
        if self.runtime_dir is None or self.topology is None:
            raise RuntimeError(f"TiDB runtime is not configured for PD recovery: run_id={self.run_id!r}")
        if self.persistent_storage_enabled or self.image_group_enabled or self.bootstrap_cache_enabled:
            raise RuntimeError(
                "PD metadata-loss cases require isolated, non-cached host data directories: "
                f"run_id={self.run_id!r}, persistent_storage={self.persistent_storage_enabled}, "
                f"image_group={self.image_group_enabled}, bootstrap_cache={self.bootstrap_cache_enabled}"
            )
        return tuple(
            Path(self.bootstrap_data_paths[("pd", service)])
            for service in self.COMPONENTS["pd"]
        )

    def capture_pd_recovery_artifact(self) -> dict[str, object]:
        """Seal raw pre-fault PD evidence before the data directories are wiped."""
        if self._pd_recovery_artifact is not None:
            raise RuntimeError(f"PD recovery evidence was already captured: run_id={self.run_id!r}")
        identity = self.pd_identity_observation()
        stores = self.pd_request("GET", "/pd/api/v1/stores")
        historical_logs = {}
        for service in self.COMPONENTS["pd"]:
            target = f"pd/{service}"
            lines = self.read_logs(target, lines=10000).splitlines()
            historical_logs[target] = [
                line
                for line in lines
                if any(
                    marker in line
                    for marker in (
                        "init cluster id",
                        "idAllocator allocates a new id",
                        "cluster-id",
                    )
                )
            ]
        data_paths = self._pd_data_paths()
        pre_wipe_data = {
            service: self._directory_inventory(path)
            for service, path in zip(self.COMPONENTS["pd"], data_paths)
        }
        incident_record_id = f"pd-audit-{self.run_id[-8:]}-m6"
        partial_record_id = f"pd-audit-{self.run_id[-8:]}-q4"
        retained_record_id = f"pd-audit-{self.run_id[-8:]}-b7"
        historical_full_loss_record_id = f"pd-audit-{self.run_id[-8:]}-h3"
        decoy_record_ids = tuple(
            f"pd-audit-{self.run_id[-8:]}-{suffix}"
            for suffix in ("a1", "c3", "d8", "e2", "f9")
        )
        post_record_ids = tuple(
            f"pd-audit-{self.run_id[-8:]}-{suffix}"
            for suffix in ("r2", "s5", "t8", "u1", "v4")
        )
        incident_time = datetime.now(timezone.utc)
        empty_inventory = {"file_count": 0, "bytes": 0}

        def build_maintenance_observation(
            retained_services: set[str],
            probe_result: str,
        ) -> dict[str, object]:
            return {
                service: {
                    "data_inventory": {
                        "before": dict(pre_wipe_data[service]),
                        "after": (
                            dict(pre_wipe_data[service])
                            if service in retained_services
                            else dict(empty_inventory)
                        ),
                    },
                    "probe_result": probe_result,
                }
                for service in self.COMPONENTS["pd"]
            }

        decoy_specs = (
            (decoy_record_ids[0], set(self.COMPONENTS["pd"])),
            (decoy_record_ids[1], {"pd-1", "pd-2"}),
            (decoy_record_ids[2], {"pd-0", "pd-2"}),
            (decoy_record_ids[3], {"pd-0", "pd-1"}),
            (decoy_record_ids[4], set(self.COMPONENTS["pd"])),
        )
        post_specs = (
            (post_record_ids[0], {"pd-0", "pd-1"}),
            (post_record_ids[1], {"pd-0", "pd-2"}),
            (post_record_ids[2], {"pd-1", "pd-2"}),
            (post_record_ids[3], set(self.COMPONENTS["pd"])),
            (post_record_ids[4], {"pd-0", "pd-1"}),
        )
        record_specs = (
            (partial_record_id, {"pd-1", "pd-2"}, "healthy response", 10),
            *(
                (record_id, retained_services, "PD client endpoint responded", offset)
                for offset, (record_id, retained_services) in enumerate(decoy_specs, start=9)
            ),
            (retained_record_id, set(self.COMPONENTS["pd"]), "PD client endpoint responded", 4),
            (historical_full_loss_record_id, set(), "PD client endpoint responded", 3),
            (incident_record_id, set(), "PD client endpoint responded", 0),
            *(
                (record_id, retained_services, "PD client endpoint responded", offset)
                for offset, (record_id, retained_services) in enumerate(post_specs, start=1)
            ),
        )
        maintenance_index = [
            {
                "record_id": record_id,
                "observed_at": (incident_time - timedelta(minutes=offset)).isoformat(),
                "probe_result": probe_result,
            }
            for record_id, retained_services, probe_result, offset in record_specs
        ]
        maintenance_observations = {
            record_id: build_maintenance_observation(retained_services, probe_result)
            for record_id, retained_services, probe_result, _ in record_specs
            if record_id != incident_record_id
        }
        maintenance_observations[incident_record_id] = {
            service: {
                "data_inventory": {"before": dict(pre_wipe_data[service])},
                "probe_result": "PD client endpoint responded",
            }
            for service in self.COMPONENTS["pd"]
        }
        original_cluster_id = int(identity["cluster"]["id"])
        partial_cluster_id = original_cluster_id + 4_000_000_003
        historical_cluster_id = original_cluster_id + 9_000_000_007
        identity_logs_by_record = {
            record_id: {
                target: [
                    f'{target.rsplit("/", 1)[1]} | ["bootstrap cluster ok"] [cluster-id={original_cluster_id}]',
                    f'{target.rsplit("/", 1)[1]} | ["idAllocator allocates a new id"] [new-end=1000] [new-base=0]',
                ]
                for target in historical_logs
            }
            for record_id in maintenance_observations
        }
        identity_logs_by_record[partial_record_id] = {
            target: [
                f'{target.rsplit("/", 1)[1]} | ["bootstrap cluster ok"] [cluster-id={partial_cluster_id}]',
                f'{target.rsplit("/", 1)[1]} | ["idAllocator allocates a new id"] [new-end=5000] [new-base=4000]',
            ]
            for target in historical_logs
        }
        identity_logs_by_record[historical_full_loss_record_id] = {
            target: [
                f'{target.rsplit("/", 1)[1]} | ["bootstrap cluster ok"] [cluster-id={historical_cluster_id}]',
                f'{target.rsplit("/", 1)[1]} | ["idAllocator allocates a new id"] [new-end=7000] [new-base=6000]',
            ]
            for target in historical_logs
        }
        active_allocator_high_water_by_target = {
            "pd/pd-0": (100_000, 99_000),
            "pd/pd-1": (900_000, 899_000),
            "pd/pd-2": (850_000, 849_000),
        }
        for target, lines in historical_logs.items():
            active_allocator_high_water, active_allocator_base = active_allocator_high_water_by_target[target]
            lines.append(
                f'{target.rsplit("/", 1)[1]} | ["idAllocator allocates a new id"] '
                f'[new-end={active_allocator_high_water}] [new-base={active_allocator_base}]'
            )
        identity_logs_by_record[incident_record_id] = historical_logs
        self._pd_recovery_artifact = {
            "product_version": self.release.version,
            "binary": "/pd-recover",
            "pre_wipe_data": pre_wipe_data,
            "historical_pd_logs": historical_logs,
            "historical_identity": identity,
            "historical_stores": stores,
            "maintenance_index": maintenance_index,
            "maintenance_observations": maintenance_observations,
            "historical_identity_logs_by_record": identity_logs_by_record,
            "current_fault_record_id": incident_record_id,
            "historical_full_loss_record_id": historical_full_loss_record_id,
        }
        return self._pd_recovery_artifact

    def wipe_pd_metadata(self) -> dict[str, object]:
        if self._pd_recovery_artifact is None:
            raise RuntimeError(f"PD recovery evidence must be captured before wipe: run_id={self.run_id!r}")
        states = self.node_states()
        running_pd = [
            target
            for target in states
            if target.startswith("pd/") and states[target]["running"]
        ]
        if running_pd:
            raise RuntimeError(
                f"Cannot wipe PD metadata while PD services are running: "
                f"run_id={self.run_id!r}, running_pd={running_pd!r}"
            )
        data_paths = self._pd_data_paths()
        post_wipe = {}
        for service, path in zip(self.COMPONENTS["pd"], data_paths):
            if not path.is_dir():
                raise RuntimeError(f"PD data directory is missing before wipe: service={service!r}, path={path}")
            for child in path.iterdir():
                if child.is_dir() and not child.is_symlink():
                    shutil.rmtree(child)
                else:
                    child.unlink()
            post_wipe[service] = self._directory_inventory(path)
        self._pd_recovery_artifact["post_wipe_data"] = post_wipe
        incident_record_id = self._pd_recovery_artifact["current_fault_record_id"]
        for service, snapshot in post_wipe.items():
            self._pd_recovery_artifact["maintenance_observations"][incident_record_id][service][
                "data_inventory"
            ]["after"] = dict(snapshot)
        return post_wipe

    def pd_recovery_inspection(
        self,
        view: str = "current",
        phase: str | None = None,
        target: str | None = None,
        record_id: str | None = None,
    ) -> dict[str, object]:
        if self._pd_recovery_artifact is None:
            raise RuntimeError(f"PD recovery artifact is not available: run_id={self.run_id!r}")
        if view not in {"current", "history"}:
            raise ValueError(
                f"Unsupported PD recovery inspection view: run_id={self.run_id!r}, view={view!r}, "
                "expected='current' or 'history'"
            )
        pd_targets = tuple(f"pd/{service}" for service in self.COMPONENTS["pd"])
        if view == "current" and phase is not None:
            raise ValueError(
                f"PD recovery current view does not accept a phase: run_id={self.run_id!r}, phase={phase!r}"
            )
        if view == "current" and target is not None:
            raise ValueError(
                f"PD recovery current view does not accept a target: run_id={self.run_id!r}, target={target!r}"
            )
        if view == "current" and record_id is not None:
            raise ValueError(
                f"PD recovery current view does not accept record_id: run_id={self.run_id!r}, record_id={record_id!r}"
            )
        if view == "history" and phase not in {"maintenance", "identity"}:
            raise ValueError(
                f"PD recovery history view requires phase='maintenance' or 'identity': "
                f"run_id={self.run_id!r}, phase={phase!r}"
            )
        if view == "history" and target not in pd_targets:
            raise ValueError(
                f"PD recovery history view requires one PD target: run_id={self.run_id!r}, "
                f"target={target!r}, expected={pd_targets!r}"
            )
        if view == "history" and not isinstance(record_id, str):
            raise ValueError(
                f"PD recovery history view requires record_id from the maintenance index: "
                f"run_id={self.run_id!r}, record_id={record_id!r}"
            )
        maintenance_index = self._pd_recovery_artifact["maintenance_index"]
        known_record_ids = tuple(item["record_id"] for item in maintenance_index)
        if view == "history" and record_id not in known_record_ids:
            raise ValueError(
                f"Unknown PD recovery history record_id: run_id={self.run_id!r}, record_id={record_id!r}, "
                f"known_record_ids={known_record_ids!r}"
            )
        binary_version = self.exec("pd/pd-0", ["/pd-recover", "-V"]).strip()
        raw_logs_by_record = (
            self._pd_recovery_artifact["historical_identity_logs_by_record"][record_id]
            if view == "history"
            else self._pd_recovery_artifact["historical_pd_logs"]
        )
        agent_pd_logs = {
            target: [line for line in raw_lines if '["init cluster id"]' not in line]
            for target, raw_lines in (
                raw_logs_by_record.items()
            )
        }
        result = {
            "product_version": self._pd_recovery_artifact["product_version"],
            "pd_recover_version": binary_version,
            "historical_evidence": {},
        }
        if view == "current":
            result["historical_evidence"]["maintenance_index"] = list(maintenance_index)
            current_data = {
                service: self._directory_inventory(path)
                for service, path in zip(self.COMPONENTS["pd"], self._pd_data_paths())
            }
            result["data_inventory"] = {"current": current_data}
        elif phase == "maintenance":
            service = target.rsplit("/", 1)[1]
            observation = self._pd_recovery_artifact["maintenance_observations"][record_id][service]
            result["historical_evidence"]["maintenance_record"] = {
                "record_id": record_id,
                "target": target,
                "observation": observation,
            }
            if "data_inventory" in observation:
                result["data_inventory"] = dict(observation["data_inventory"])
        else:
            observation = self._pd_recovery_artifact["maintenance_observations"][record_id][
                target.rsplit("/", 1)[1]
            ]
            result["historical_evidence"]["identity_record"] = {
                "record_id": record_id,
                "target": target,
                "observation": {"probe_result": observation["probe_result"]},
            }
            result["historical_evidence"]["pd_logs"] = {target: agent_pd_logs[target]}
            result["historical_evidence"]["allocator_log_evidence"] = {
                "record_id": record_id,
                "logs_by_member": {
                    member_target: [
                        line
                        for line in member_lines
                        if '["idAllocator allocates a new id"]' in line
                    ]
                    for member_target, member_lines in agent_pd_logs.items()
                },
            }
        return result

    def pd_recovery_current_record_id(self) -> str:
        if self._pd_recovery_artifact is None:
            raise RuntimeError(f"PD recovery artifact is not available: run_id={self.run_id!r}")
        return str(self._pd_recovery_artifact["current_fault_record_id"])

    def execute_pd_recovery(
        self,
        target: str,
        cluster_id: int,
        alloc_id: int,
        recovery_branch: str,
        record_id: str,
    ) -> dict[str, object]:
        if target not in self.NODES or not target.startswith("pd/"):
            raise ValueError(f"PD recovery target must be a configured PD service: target={target!r}")
        if not isinstance(cluster_id, int) or cluster_id <= 0:
            raise ValueError(f"PD recovery cluster_id must be a positive integer: cluster_id={cluster_id!r}")
        if not isinstance(alloc_id, int) or alloc_id <= 0:
            raise ValueError(f"PD recovery alloc_id must be a positive integer: alloc_id={alloc_id!r}")
        if recovery_branch not in {"surviving_member", "entirely_rebuild"}:
            raise ValueError(
                "PD recovery requires one supported recovery_branch from "
                "['surviving_member', 'entirely_rebuild']: "
                f"target={target!r}, recovery_branch={recovery_branch!r}"
            )
        if not isinstance(record_id, str) or not record_id:
            raise ValueError(
                "PD recovery requires a non-empty maintenance record_id: "
                f"target={target!r}, record_id={record_id!r}"
            )
        if self._pd_recovery_artifact is None:
            raise RuntimeError(f"PD recovery artifact is not available: run_id={self.run_id!r}")
        known_record_ids = tuple(
            item["record_id"] for item in self._pd_recovery_artifact["maintenance_index"]
        )
        if record_id not in known_record_ids:
            raise ValueError(
                "PD recovery record_id is not present in the maintenance index: "
                f"target={target!r}, record_id={record_id!r}, known_record_ids={known_record_ids!r}"
            )
        observations = self._pd_recovery_artifact["maintenance_observations"][record_id]
        before = {
            service: observations[service]["data_inventory"]["before"]
            for service in self.COMPONENTS["pd"]
        }
        after = {
            service: observations[service]["data_inventory"].get("after")
            for service in self.COMPONENTS["pd"]
        }
        if recovery_branch == "entirely_rebuild":
            invalid_members = {
                service: {"before": before[service], "after": after[service]}
                for service in self.COMPONENTS["pd"]
                if int(before[service]["file_count"]) <= 0
                or after[service] is None
                or int(after[service]["file_count"]) != 0
            }
            if invalid_members:
                raise ValueError(
                    "PD entirely_rebuild branch requires one record proving all PD members were wiped: "
                    f"target={target!r}, record_id={record_id!r}, invalid_members={invalid_members!r}"
                )
            current_record_id = str(self._pd_recovery_artifact["current_fault_record_id"])
            if record_id != current_record_id:
                observed_at = next(
                    item["observed_at"]
                    for item in self._pd_recovery_artifact["maintenance_index"]
                    if item["record_id"] == record_id
                )
                current_observed_at = next(
                    item["observed_at"]
                    for item in self._pd_recovery_artifact["maintenance_index"]
                    if item["record_id"] == current_record_id
                )
                raise ValueError(
                    "PD entirely_rebuild branch must bind the active maintenance window before /pd-recover: "
                    f"target={target!r}, selected_record_id={record_id!r}, selected_observed_at={observed_at!r}, "
                    f"current_record_id={current_record_id!r}, current_observed_at={current_observed_at!r}"
                )
        else:
            surviving_members = {
                service: after[service]
                for service in self.COMPONENTS["pd"]
                if after[service] is not None and int(after[service]["file_count"]) > 0
            }
            if record_id != str(self._pd_recovery_artifact["current_fault_record_id"]):
                raise ValueError(
                    "PD surviving_member branch is not authorized for the selected maintenance record: "
                    f"target={target!r}, record_id={record_id!r}, observed_surviving_members={surviving_members!r}"
                )
            current_after = self._pd_recovery_artifact.get("post_wipe_data")
            if not isinstance(current_after, dict) or not any(
                int(snapshot["file_count"]) > 0 for snapshot in current_after.values()
            ):
                raise ValueError(
                    "PD surviving_member branch is invalid for the selected current maintenance record because "
                    "its observed members have no surviving PD data: "
                    f"target={target!r}, record_id={record_id!r}, observed_surviving_members={surviving_members!r}"
                )
        states = self.node_states()
        running_database = [
            node
            for node in self.database_nodes
            if node.startswith(("tikv/", "tidb/")) and states[node]["running"]
        ]
        if running_database:
            raise RuntimeError(
                "PD recovery requires TiDB and TiKV services to be stopped: "
                f"target={target!r}, running_database={running_database!r}"
            )
        running_pd = [
            node
            for node in self.COMPONENTS["pd"]
            if states[f"pd/{node}"]["running"]
        ]
        if len(running_pd) != len(self.COMPONENTS["pd"]):
            raise RuntimeError(
                "PD recovery requires the rebuilt PD quorum to be running: "
                f"target={target!r}, running_pd={running_pd!r}, expected={self.COMPONENTS['pd']!r}"
            )
        output = self.exec(
            target,
            [
                "/pd-recover",
                "--endpoints=http://127.0.0.1:2379",
                f"--cluster-id={cluster_id}",
                f"--alloc-id={alloc_id}",
            ],
        )
        audit = {
            "target": target,
            "cluster_id": cluster_id,
            "alloc_id": alloc_id,
            "recovery_branch": recovery_branch,
            "record_id": record_id,
            "binary": "/pd-recover",
            "stdout": output,
        }
        self._pd_recovery_audit.append(audit)
        return {"status": "recovered_metadata", **audit}

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

    def online_unsafe_recovery(
        self,
        operation: str,
        failed_store_ids: tuple[int, ...] = (),
    ) -> object:
        """Expose the v8.1 PD Online Unsafe Recovery product operation."""
        if operation == "get":
            return self._pd_ctl("unsafe", "remove-failed-stores", "show")
        if operation != "start":
            raise ValueError(
                f"Unsupported Online Unsafe Recovery operation: operation={operation!r}"
            )
        if not failed_store_ids:
            raise ValueError(
                "Online Unsafe Recovery requires every permanently failed Store ID: "
                f"failed_store_ids={failed_store_ids!r}"
            )
        normalized_ids = tuple(sorted(int(store_id) for store_id in failed_store_ids))
        if len(normalized_ids) != len(failed_store_ids) or any(store_id <= 0 for store_id in normalized_ids):
            raise ValueError(
                "Online Unsafe Recovery Store IDs must be unique positive integers: "
                f"failed_store_ids={failed_store_ids!r}"
            )
        stores = self._pd_stores()
        stores_by_id = {
            int(item["store"]["id"]): item
            for item in stores
        }
        missing_ids = sorted(set(normalized_ids) - set(stores_by_id))
        if missing_ids:
            raise ValueError(
                "Online Unsafe Recovery received Store IDs absent from the current PD Store inventory: "
                f"missing_store_ids={missing_ids!r}, observed_store_ids={sorted(stores_by_id)!r}"
            )
        connected_ids = [
            store_id
            for store_id in normalized_ids
            if str(stores_by_id[store_id]["store"].get("state_name", "")).casefold()
            in {"up", "serving"}
        ]
        if connected_ids:
            raise RuntimeError(
                "Online Unsafe Recovery rejected connected Stores; only permanently failed Stores are allowed: "
                f"connected_store_ids={connected_ids!r}, requested_store_ids={list(normalized_ids)!r}"
            )
        output = self.exec(
            "pd/pd-0",
            [
                "/pd-ctl",
                "-u",
                "http://127.0.0.1:2379",
                "unsafe",
                "remove-failed-stores",
                ",".join(str(store_id) for store_id in normalized_ids),
                "--timeout",
                str(self.ONLINE_UNSAFE_RECOVERY_TIMEOUT_SECONDS),
            ],
        ).strip()
        if output == "Success" or output.startswith("Success!"):
            self.online_unsafe_recovery_started = True
            return {
                "state": "accepted",
                "failed_store_ids": list(normalized_ids),
                "raw_output": output,
            }
        if output.startswith("Failed"):
            raise RuntimeError(
                "PD rejected Online Unsafe Recovery registration: "
                f"failed_store_ids={list(normalized_ids)!r}, output={output!r}"
            )
        raise RuntimeError(
            "PD Online Unsafe Recovery returned an unexpected registration response: "
            f"failed_store_ids={list(normalized_ids)!r}, output={output!r}"
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

    def _mvcc_region_scope(
        self,
        region_id: int,
        store_targets: list[str] | tuple[str, ...],
    ) -> dict[str, object]:
        if region_id <= 0:
            raise ValueError(f"MVCC Region ID must be positive: region_id={region_id}")
        if not isinstance(store_targets, (list, tuple)) or not store_targets:
            raise ValueError(
                "MVCC operation requires an explicit non-empty store_targets list: "
                f"region_id={region_id}, store_targets={store_targets!r}"
            )
        if any(not isinstance(target, str) for target in store_targets):
            raise TypeError(f"MVCC store_targets must contain strings: store_targets={store_targets!r}")
        if len(set(store_targets)) != len(store_targets):
            raise ValueError(f"MVCC store_targets must not contain duplicates: store_targets={store_targets!r}")

        region = self.pd_request("GET", f"/pd/api/v1/region/id/{region_id}")
        if int(region["id"]) != region_id:
            raise RuntimeError(
                f"PD returned a different Region: requested={region_id}, observed={region!r}"
            )
        peers = region.get("peers")
        if not isinstance(peers, list) or not peers:
            raise RuntimeError(f"PD Region has no peer list: region_id={region_id}, region={region!r}")
        peer_store_ids = tuple(sorted(int(peer["store_id"]) for peer in peers))
        if len(set(peer_store_ids)) != len(peer_store_ids):
            raise RuntimeError(
                f"PD Region has duplicate peer Store IDs: region_id={region_id}, peers={peers!r}"
            )

        stores = self._pd_stores()
        store_by_target: dict[str, dict[str, object]] = {}
        for item in stores:
            store = item["store"]
            address = str(store["address"])
            service = address.rsplit(":", 1)[0]
            target = f"tikv/{service}"
            if target in self.NODES:
                store_by_target[target] = {
                    "store_id": int(store["id"]),
                    "target": target,
                    "address": address,
                    "state": str(store.get("state_name", "")),
                }
        unknown_targets = sorted(set(store_targets) - set(store_by_target))
        if unknown_targets:
            raise ValueError(
                "MVCC store_targets are not current TiKV Store identities: "
                f"region_id={region_id}, unknown_targets={unknown_targets!r}, "
                f"known_targets={sorted(store_by_target)!r}"
            )
        selected_store_ids = tuple(sorted(store_by_target[target]["store_id"] for target in store_targets))
        if selected_store_ids != peer_store_ids:
            raise ValueError(
                "MVCC operation must cover exactly the current Region peer Store set: "
                f"region_id={region_id}, requested_targets={tuple(store_targets)!r}, "
                f"requested_store_ids={selected_store_ids!r}, peer_store_ids={peer_store_ids!r}"
            )
        peer_targets = tuple(
            target
            for _, target in sorted(
                (int(store_by_target[target]["store_id"]), target)
                for target in store_targets
            )
        )
        return {
            "region": region,
            "region_id": region_id,
            "peer_store_ids": peer_store_ids,
            "store_targets": peer_targets,
            "stores": [store_by_target[target] for target in peer_targets],
        }

    @staticmethod
    def _mvcc_region_target(region_id: int) -> str:
        return f"region/{region_id}"

    def _mvcc_compose_service(self, target: str) -> str:
        if target not in self.NODES or not target.startswith("tikv/"):
            raise ValueError(
                f"MVCC operation requires a TiKV target: target={target!r}, "
                f"expected={[item for item in self.NODES if item.startswith('tikv/')]!r}"
            )
        return self.NODES[target]

    def _mvcc_tikv_mounts(self, service: str) -> tuple[str, str, str]:
        if self.compose_file is None:
            raise RuntimeError(f"TiDB Compose file is not configured: run_id={self.run_id!r}")
        with open(self.compose_file, encoding="utf-8") as handle:
            services = yaml.safe_load(handle)["services"]
        node = services[service]
        data_mount = None
        config_mount = None
        image = str(node["image"])
        for volume in node.get("volumes", []):
            parts = str(volume).split(":")
            if len(parts) < 2:
                raise ValueError(
                    f"TiKV Compose volume is not a host bind mount: run_id={self.run_id!r}, "
                    f"service={service!r}, volume={volume!r}"
                )
            source, destination = parts[0], parts[1]
            if destination == "/data/tikv":
                data_mount = source
            elif destination == "/tikv.toml":
                config_mount = source
        if data_mount is None or config_mount is None:
            raise RuntimeError(
                "MVCC helper requires host-mounted TiKV data and config paths: "
                f"run_id={self.run_id!r}, service={service!r}, volumes={node.get('volumes')!r}"
            )
        if not os.path.isdir(data_mount) or not os.path.isfile(config_mount):
            raise FileNotFoundError(
                "MVCC helper host mount does not exist: "
                f"run_id={self.run_id!r}, service={service!r}, data_dir={data_mount!r}, "
                f"config_path={config_mount!r}"
            )
        return data_mount, config_mount, image

    def _mvcc_tool_metadata(self, image: str) -> dict[str, str]:
        cached = self._mvcc_tool_metadata_cache.get(image)
        if cached is not None:
            return dict(cached)
        if "@sha256:" not in image:
            raise RuntimeError(
                f"MVCC helper requires a digest-pinned TiKV image: run_id={self.run_id!r}, image={image!r}"
            )
        if self.release is None:
            raise RuntimeError(f"TiDB release is not configured: run_id={self.run_id!r}")
        expected_version = self.release.version.removeprefix("v")
        version_command = [
            "docker", "run", "--rm", "--user", "0:0",
            "--entrypoint", "/tikv-ctl", image, "--version",
        ]
        version_result = subprocess.run(
            version_command, capture_output=True, text=True, env=self._env
        )
        if version_result.returncode != 0:
            raise RuntimeError(
                "TiKV trusted tool version command failed: "
                f"run_id={self.run_id!r}, image={image!r}, command={shlex.join(version_command)!r}, "
                f"exit_code={version_result.returncode}, stdout={version_result.stdout.strip()!r}, "
                f"stderr={version_result.stderr.strip()!r}"
            )
        version_match = re.search(r"Release Version:\s*([0-9][^\s]*)", version_result.stdout)
        commit_match = re.search(r"Git Commit Hash:\s*([0-9a-f]+)", version_result.stdout)
        if version_match is None or commit_match is None:
            raise RuntimeError(
                "TiKV trusted tool version output is incomplete: "
                f"run_id={self.run_id!r}, image={image!r}, stdout={version_result.stdout.strip()!r}"
            )
        observed_version = version_match.group(1)
        if observed_version != expected_version:
            raise RuntimeError(
                "TiKV trusted tool version mismatch: "
                f"run_id={self.run_id!r}, image={image!r}, expected_version={expected_version!r}, "
                f"observed_version={observed_version!r}, stdout={version_result.stdout.strip()!r}"
            )
        hash_command = [
            "docker", "run", "--rm", "--user", "0:0",
            "--entrypoint", "/bin/sh", image, "-c", "sha256sum /tikv-ctl",
        ]
        hash_result = subprocess.run(hash_command, capture_output=True, text=True, env=self._env)
        if hash_result.returncode != 0:
            raise RuntimeError(
                "TiKV trusted tool hash command failed: "
                f"run_id={self.run_id!r}, image={image!r}, command={shlex.join(hash_command)!r}, "
                f"exit_code={hash_result.returncode}, stdout={hash_result.stdout.strip()!r}, "
                f"stderr={hash_result.stderr.strip()!r}"
            )
        hash_match = re.fullmatch(r"\s*([0-9a-f]{64})\s+/tikv-ctl\s*", hash_result.stdout)
        if hash_match is None:
            raise RuntimeError(
                "TiKV trusted tool hash output is invalid: "
                f"run_id={self.run_id!r}, image={image!r}, stdout={hash_result.stdout.strip()!r}"
            )
        metadata = {
            "release_version": f"v{observed_version}",
            "image": image,
            "binary_path": "/tikv-ctl",
            "binary_sha256": hash_match.group(1),
            "git_commit_hash": commit_match.group(1),
        }
        self._mvcc_tool_metadata_cache[image] = metadata
        return dict(metadata)

    @staticmethod
    def _mvcc_hex_to_escaped(value: str, field: str) -> str:
        if not isinstance(value, str) or len(value) % 2 or re.fullmatch(r"[0-9A-Fa-f]*", value) is None:
            raise ValueError(f"MVCC {field} must be an even-length hexadecimal string: value={value!r}")
        escaped = []
        for byte in bytes.fromhex(value):
            if 0x20 <= byte <= 0x7E and byte not in {0x5C}:
                escaped.append(chr(byte))
            else:
                escaped.append(f"\\{byte:03o}")
        return "".join(escaped)

    @staticmethod
    def _mvcc_decode_memcomparable_key(value: str, field: str) -> str:
        if not isinstance(value, str) or len(value) % 2 or re.fullmatch(r"[0-9A-Fa-f]*", value) is None:
            raise ValueError(f"MVCC {field} must be an even-length hexadecimal string: value={value!r}")
        encoded = bytes.fromhex(value)
        decoded = bytearray()
        offset = 0
        while offset < len(encoded):
            if len(encoded) - offset < 9:
                raise ValueError(
                    f"MVCC {field} has an incomplete mem-comparable group: value={value!r}, offset={offset}"
                )
            group = encoded[offset:offset + 8]
            marker = encoded[offset + 8]
            padding = 0xFF - marker
            if padding < 0 or padding > 8:
                raise ValueError(
                    f"MVCC {field} has an invalid mem-comparable marker: value={value!r}, marker={marker:#x}"
                )
            if padding and any(group[-padding:]):
                raise ValueError(
                    f"MVCC {field} has non-zero mem-comparable padding: value={value!r}, offset={offset}"
                )
            decoded.extend(group[:8 - padding])
            offset += 9
            if padding:
                if offset != len(encoded):
                    raise ValueError(
                        f"MVCC {field} has bytes after its terminal mem-comparable group: value={value!r}"
                    )
                break
        return bytes(decoded).hex().upper()

    @staticmethod
    def _mvcc_encode_memcomparable_key(value: bytes) -> bytes:
        encoded = bytearray()
        for offset in range(0, len(value) + 1, 8):
            group = value[offset:offset + 8]
            padding = 8 - len(group)
            encoded.extend(group)
            encoded.extend(b"\x00" * padding)
            encoded.append(0xFF - padding)
        return bytes(encoded)

    def _mvcc_tikv_ctl(
        self,
        service: str,
        arguments: list[str],
        *,
        region_id: int,
        store_targets: tuple[str, ...],
    ) -> tuple[str, dict[str, str]]:
        data_dir, config_path, image = self._mvcc_tikv_mounts(service)
        metadata = self._mvcc_tool_metadata(image)
        pd_endpoints = [f"{service_name}:2379" for service_name in self.COMPONENTS["pd"]]
        command = [
            "docker", "run", "--rm", "--user", "0:0",
            "--network", self.network_name,
            "-v", f"{data_dir}:/data/tikv:rw",
            "-v", f"{config_path}:/tikv.toml:ro",
            "--entrypoint", metadata["binary_path"], image,
            "--data-dir=/data/tikv", "--config=/tikv.toml",
            *arguments,
        ]
        result = subprocess.run(command, capture_output=True, text=True, env=self._env)
        if result.returncode != 0:
            raise RuntimeError(
                "TiKV trusted command failed: "
                f"run_id={self.run_id!r}, release_version={metadata['release_version']!r}, "
                f"binary_sha256={metadata['binary_sha256']!r}, image={image!r}, "
                f"region_id={region_id}, store_targets={store_targets!r}, "
                f"pd_endpoints={pd_endpoints!r}, command={shlex.join(command)!r}, "
                f"exit_code={result.returncode}, stdout={result.stdout.strip()!r}, "
                f"stderr={result.stderr.strip()!r}"
            )
        return result.stdout, metadata

    def _mvcc_offline_call(
        self,
        target: str,
        operation: str,
        callback,
    ):
        service = self._mvcc_compose_service(target)
        self._run(self._compose + ["stop", "--timeout", "120", service], target)
        command_error = None
        try:
            return callback(service)
        except Exception as exc:
            command_error = exc
            raise
        finally:
            try:
                self._run(self._compose + ["start", service], target)
                self._container_ids.clear()
                self._wait(
                    target,
                    lambda service=service: self._check_tikv_target(service),
                    self.warm_tidb_readiness_timeout_sec,
                )
                self.active_tikv_services.add(service)
            except Exception as start_error:
                if command_error is not None:
                    raise RuntimeError(
                        "TiKV offline helper failed during command and restart: "
                        f"run_id={self.run_id!r}, target={target!r}, operation={operation!r}, "
                        f"command_error={command_error!r}, restart_error={start_error!r}"
                    ) from start_error
                raise

    def _mvcc_offline_call_many(
        self,
        targets: tuple[str, ...],
        operation: str,
        callback,
    ):
        if not targets:
            raise ValueError(
                f"TiKV offline helper requires at least one target: run_id={self.run_id!r}, operation={operation!r}"
            )
        services = tuple(self._mvcc_compose_service(target) for target in targets)
        if len(set(services)) != len(services):
            raise ValueError(
                "TiKV offline helper received duplicate services: "
                f"run_id={self.run_id!r}, operation={operation!r}, targets={targets!r}, services={services!r}"
            )
        command_error = None
        try:
            for target, service in zip(targets, services):
                self._run(self._compose + ["stop", "--timeout", "120", service], target)
            return callback(services)
        except Exception as exc:
            command_error = exc
            raise
        finally:
            try:
                self._run(self._compose + ["start", *services], targets[0])
                self._container_ids.clear()
                for target, service in zip(targets, services):
                    self._wait(
                        target,
                        lambda service=service: self._check_tikv_target(service),
                        self.warm_tidb_readiness_timeout_sec,
                    )
                    self.active_tikv_services.add(service)
            except Exception as start_error:
                if command_error is not None:
                    raise RuntimeError(
                        "TiKV multi-target offline helper failed during command and restart: "
                        f"run_id={self.run_id!r}, targets={targets!r}, operation={operation!r}, "
                        f"command_error={command_error!r}, restart_error={start_error!r}"
                    ) from start_error
                raise

    @staticmethod
    def _mvcc_scan_summary(output: str, *, region_id: int, target: str) -> dict[str, object]:
        total_match = re.search(r"Total scanned keys:\s*(\d+)", output)
        if total_match is None:
            raise RuntimeError(
                "TiKV raw-scan output is missing its total: "
                f"region_id={region_id}, target={target!r}, output={output!r}"
            )
        records = []
        for line in output.splitlines():
            if not line.startswith("key: "):
                continue
            match = re.fullmatch(r"key: (\".*\"), value: (\".*\")", line)
            if match is None:
                raise RuntimeError(
                    "TiKV raw-scan record is not parseable: "
                    f"region_id={region_id}, target={target!r}, line={line!r}"
                )
            key = ast.literal_eval(match.group(1))
            value = ast.literal_eval(match.group(2))
            if not isinstance(key, str) or not isinstance(value, str):
                raise TypeError(
                    "TiKV raw-scan record did not decode to strings: "
                    f"region_id={region_id}, target={target!r}, line={line!r}"
                )
            storage_key_bytes = key.encode("latin1")
            if not storage_key_bytes.startswith(b"z"):
                raise RuntimeError(
                    "TiKV lock CF raw-scan returned a non-data key: "
                    f"region_id={region_id}, target={target!r}, key_hex={storage_key_bytes.hex().upper()!r}"
                )
            encoded_key_hex = storage_key_bytes[1:].hex().upper()
            key_hex = TiDBDockerDeployment._mvcc_decode_memcomparable_key(encoded_key_hex, "lock_key")
            key_bytes = bytes.fromhex(key_hex)
            value_bytes = value.encode("latin1")
            records.append({
                "key_hex": key_hex,
                "storage_key_hex": storage_key_bytes.hex().upper(),
                "encoded_key_hex": encoded_key_hex,
                "value_hex": value_bytes.hex().upper(),
                "key_escaped": key_bytes.decode("latin1"),
                "storage_key_escaped": key,
                "value_escaped": value,
            })
        return {
            "target": target,
            "scanned_keys": int(total_match.group(1)),
            "raw_output": output,
            "records": records,
        }

    def mvcc_lock_list(
        self,
        region_id: int,
        store_targets: list[str] | tuple[str, ...],
        limit: int,
        from_key: str | None = None,
        to_key: str | None = None,
    ) -> dict[str, object]:
        if limit <= 0 or limit > 128:
            raise ValueError(f"MVCC lock scan limit must be in 1..128: region_id={region_id}, limit={limit}")
        scope = self._mvcc_region_scope(region_id, store_targets)
        region = scope["region"]
        region_start_hex = str(region.get("start_key", ""))
        region_end_hex = str(region.get("end_key", ""))
        start_hex = (
            f"{self._MVCC_DATA_PREFIX_HEX}{region_start_hex}"
            if from_key is None and region_start_hex
            else (self._MVCC_DATA_PREFIX_HEX if from_key is None else from_key)
        )
        end_hex = (
            f"{self._MVCC_DATA_PREFIX_HEX}{region_end_hex}"
            if to_key is None and region_end_hex
            else (self._MVCC_DATA_MAX_HEX if to_key is None else to_key)
        )
        start = self._mvcc_hex_to_escaped(start_hex, "from_key")
        end = self._mvcc_hex_to_escaped(end_hex, "to_key")
        if start and end and start_hex.casefold() >= end_hex.casefold():
            raise ValueError(
                f"MVCC lock scan range must be ordered: region_id={region_id}, from_key={start_hex!r}, to_key={end_hex!r}"
            )
        arguments = ["raw-scan", "--cf=lock", f"--limit={limit}"]
        if start:
            arguments.append(f"--from={start}")
        if end:
            arguments.append(f"--to={end}")

        def scan_peers(services):
            peers = []
            for target, service in zip(scope["store_targets"], services):
                output, metadata = self._mvcc_tikv_ctl(
                    service,
                    arguments,
                    region_id=region_id,
                    store_targets=scope["store_targets"],
                )
                summary = self._mvcc_scan_summary(output, region_id=region_id, target=target)
                summary["store_id"] = next(
                    int(store["store_id"]) for store in scope["stores"] if store["target"] == target
                )
                summary["tool"] = metadata
                peers.append(summary)
            return peers

        peers = self._mvcc_offline_call_many(
            tuple(scope["store_targets"]),
            "mvcc_lock/list",
            scan_peers,
        )
        return {
            "region_id": region_id,
            "peer_store_ids": list(scope["peer_store_ids"]),
            "store_targets": list(scope["store_targets"]),
            "region_start_key": region_start_hex,
            "region_end_key": region_end_hex,
            "from_key": start_hex,
            "to_key": end_hex,
            "limit": limit,
            "peers": peers,
        }

    def mvcc_recovery_inspect(
        self,
        region_id: int,
        store_targets: list[str] | tuple[str, ...],
    ) -> dict[str, object]:
        procedure = TIKV_STORAGE_MAINTENANCE_PROCEDURE
        scope = self._mvcc_region_scope(region_id, store_targets)
        def inspect_peers(services):
            peer_results = []
            for target, service in zip(scope["store_targets"], services):
                output, metadata = self._mvcc_tikv_ctl(
                    service,
                    [
                        "recover-mvcc", "--read-only", "-r", str(region_id),
                        "-p", f"{self.COMPONENTS['pd'][0]}:2379",
                    ],
                    region_id=region_id,
                    store_targets=scope["store_targets"],
                )
                peer_results.append({
                    "target": target,
                    "store_id": next(
                        int(store["store_id"]) for store in scope["stores"] if store["target"] == target
                    ),
                    "raw_output": output,
                    "tool": metadata,
                })
            return peer_results

        peer_results = self._mvcc_offline_call_many(
            tuple(scope["store_targets"]),
            "mvcc_recovery/inspect",
            inspect_peers,
        )
        inspection_id = f"mvcc-{uuid.uuid4().hex}"
        self._mvcc_inspections[inspection_id] = {
            "region_id": region_id,
            "store_targets": tuple(scope["store_targets"]),
            "peer_store_ids": tuple(scope["peer_store_ids"]),
            "procedure": procedure,
            "tool": dict(peer_results[0]["tool"]),
        }
        return {
            "inspection_id": inspection_id,
            "procedure": procedure,
            "region_id": region_id,
            "peer_store_ids": list(scope["peer_store_ids"]),
            "store_targets": list(scope["store_targets"]),
            "supported_scope": "region",
            "read_only": True,
            "peers": peer_results,
        }

    def mvcc_recovery_execute(
        self,
        region_id: int,
        inspection_id: str,
    ) -> dict[str, object]:
        if not isinstance(inspection_id, str) or not inspection_id:
            raise ValueError(f"MVCC recovery execute requires inspection_id: value={inspection_id!r}")
        inspection = self._mvcc_inspections.get(inspection_id)
        if inspection is None:
            raise ValueError(
                f"MVCC recovery execute requires a live inspect result: inspection_id={inspection_id!r}, "
                f"known={sorted(self._mvcc_inspections)!r}"
            )
        procedure = TIKV_STORAGE_MAINTENANCE_PROCEDURE
        if procedure != inspection["procedure"]:
            raise RuntimeError(
                "TiKV storage maintenance procedure changed in the runtime: "
                f"inspection_id={inspection_id!r}, inspected_procedure={inspection['procedure']!r}, "
                f"runtime_procedure={procedure!r}"
            )
        scope = self._mvcc_region_scope(region_id, inspection["store_targets"])
        if tuple(scope["store_targets"]) != tuple(inspection["store_targets"]):
            raise ValueError(
                "MVCC recovery scope changed after inspect: "
                f"inspection_id={inspection_id!r}, inspected_targets={inspection['store_targets']!r}, "
                f"requested_targets={scope['store_targets']!r}"
            )
        current_tool = self._mvcc_tool_metadata(
            self._mvcc_tikv_mounts(self._mvcc_compose_service(scope["store_targets"][0]))[2]
        )
        if current_tool != inspection["tool"]:
            raise RuntimeError(
                "TiKV trusted tool identity changed after inspect: "
                f"inspection_id={inspection_id!r}, inspected_tool={inspection['tool']!r}, current_tool={current_tool!r}"
            )
        def execute_peers(services):
            peer_results = []
            for target, service in zip(scope["store_targets"], services):
                output, metadata = self._mvcc_tikv_ctl(
                    service,
                    [
                        "recover-mvcc", "-r", str(region_id),
                        "-p", f"{self.COMPONENTS['pd'][0]}:2379",
                    ],
                    region_id=region_id,
                    store_targets=scope["store_targets"],
                )
                peer_results.append({
                    "target": target,
                    "store_id": next(
                        int(store["store_id"]) for store in scope["stores"] if store["target"] == target
                    ),
                    "raw_output": output,
                    "tool": metadata,
                })
            return peer_results

        peer_results = self._mvcc_offline_call_many(
            tuple(scope["store_targets"]),
            "mvcc_recovery/execute",
            execute_peers,
        )
        del self._mvcc_inspections[inspection_id]
        return {
            "inspection_id": inspection_id,
            "procedure": procedure,
            "region_id": region_id,
            "peer_store_ids": list(scope["peer_store_ids"]),
            "store_targets": list(scope["store_targets"]),
            "scope": "region",
            "read_only": False,
            "peers": peer_results,
        }

    _MVCC_LOCK_TYPE_CHARACTERS = ("P", "D", "L", "S")

    @staticmethod
    def _mvcc_read_var_u64(value: bytes, offset: int, field: str) -> tuple[int, int]:
        decoded = 0
        shift = 0
        while True:
            if offset >= len(value):
                raise ValueError(
                    f"MVCC lock record ended while decoding {field}: offset={offset}, "
                    f"value_hex={value.hex().upper()}"
                )
            byte = value[offset]
            offset += 1
            decoded |= (byte & 0x7F) << shift
            if not byte & 0x80:
                return decoded, offset
            shift += 7
            if shift >= 64:
                raise ValueError(
                    f"MVCC lock record has an oversized {field} varint: value_hex={value.hex().upper()}"
                )

    @classmethod
    def mvcc_decode_lock_record(cls, value_hex: str) -> dict[str, object]:
        """Decode the lock-CF record fields that bound a key-level resolve.

        TiKV serializes every lock CF value as: lock-type byte, compact primary
        key, varint start_ts, varint ttl, ... The type byte and start_ts are the
        identity a destructive key-level maintenance caller must state.
        """
        if not isinstance(value_hex, str) or len(value_hex) % 2:
            raise ValueError(f"MVCC lock record value must be even-length hex: value_hex={value_hex!r}")
        value = bytes.fromhex(value_hex)
        if not value:
            raise ValueError("MVCC lock record value is empty")
        lock_type = chr(value[0])
        if lock_type not in cls._MVCC_LOCK_TYPE_CHARACTERS:
            raise ValueError(
                "MVCC lock record has an unknown lock-type byte: "
                f"type_byte={value[0]:02X}, value_hex={value.hex().upper()}"
            )
        encoded_length, offset = cls._mvcc_read_var_u64(value, 1, "primary_key_length")
        if encoded_length % 2:
            raise ValueError(
                "MVCC lock record has an invalid compact primary key length: "
                f"encoded_length={encoded_length}, value_hex={value.hex().upper()}"
            )
        offset += encoded_length // 2
        start_ts, _ = cls._mvcc_read_var_u64(value, offset, "start_ts")
        return {"lock_type": lock_type, "start_ts": start_ts}

    def delete_mvcc_lock(
        self,
        region_id: int,
        store_targets: list[str] | tuple[str, ...],
        key_hex: str,
    ) -> dict[str, object]:
        if re.fullmatch(r"[0-9A-Fa-f]+", key_hex or "") is None or len(key_hex) % 2:
            raise ValueError(f"MVCC key delete requires an even-length hex key: key_hex={key_hex!r}")
        scope = self._mvcc_region_scope(region_id, store_targets)
        storage_key_hex = (
            f"{self._MVCC_DATA_PREFIX_HEX}"
            f"{self._mvcc_encode_memcomparable_key(bytes.fromhex(key_hex)).hex().upper()}"
        )

        def delete(services):
            peer_results = []
            for target, service in zip(scope["store_targets"], services):
                output, metadata = self._mvcc_tikv_ctl(
                    service,
                    [
                        "ldb",
                        "--db=/data/tikv/db",
                        "--column_family=lock",
                        "--hex",
                        "delete",
                        f"0x{storage_key_hex}",
                    ],
                    region_id=region_id,
                    store_targets=scope["store_targets"],
                )
                peer_results.append({"target": target, "output": output, "tool": metadata})
            return peer_results

        results = self._mvcc_offline_call_many(
            tuple(scope["store_targets"]),
            "mvcc_lock_resolve_key",
            delete,
        )
        return {
            "region_id": region_id,
            "peer_store_ids": list(scope["peer_store_ids"]),
            "store_targets": list(scope["store_targets"]),
            "key_hex": key_hex.upper(),
            "storage_key_hex": storage_key_hex,
            "scope": "key",
            "peers": results,
        }

    def mvcc_recovery_apply_interlock(
        self,
        region_id: int,
        inspection_id: str,
    ) -> dict[str, object]:
        """Refuse region-level recover-mvcc while the Region holds live pessimistic locks."""
        inspection = self._mvcc_inspections.get(inspection_id)
        if inspection is None:
            raise ValueError(
                "MVCC recovery interlock requires a live inspect result: "
                f"inspection_id={inspection_id!r}, known={sorted(self._mvcc_inspections)!r}"
            )
        if int(inspection["region_id"]) != int(region_id):
            raise ValueError(
                "MVCC recovery interlock Region does not match the inspect result: "
                f"inspection_id={inspection_id!r}, inspected_region={inspection['region_id']!r}, "
                f"requested_region={region_id!r}"
            )
        scan = self.mvcc_lock_list(region_id, inspection["store_targets"], 128)
        live_keys = {}
        checked_keys = set()
        for peer in scan["peers"]:
            for record in peer["records"]:
                checked_keys.add(str(record["key_hex"]).upper())
                decoded = self.mvcc_decode_lock_record(record["value_hex"])
                if decoded["lock_type"] == "S":
                    live_keys[str(record["key_hex"]).upper()] = decoded["start_ts"]
        if live_keys:
            first_key = sorted(live_keys)[0]
            raise ValueError(
                f"region-level recover-mvcc refused: Region {region_id} lock CF still holds "
                f"{len(live_keys)} in-flight pessimistic transaction lock(s) "
                f"(first key={first_key!r}); region-level maintenance requires a Region "
                f"with no live lock holders"
            )
        return {
            "region_id": region_id,
            "inspection_id": inspection_id,
            "live_lock_count": 0,
            "checked_keys": sorted(checked_keys),
        }

    def mvcc_lock_resolve_key(
        self,
        region_id: int,
        inspection_id: str,
        key_hex: str,
        lock_type: str,
        start_ts: object,
    ) -> dict[str, object]:
        if not isinstance(inspection_id, str) or not inspection_id:
            raise ValueError(f"MVCC key-level resolve requires inspection_id: value={inspection_id!r}")
        if not isinstance(key_hex, str) or re.fullmatch(r"[0-9A-Fa-f]+", key_hex) is None or not key_hex:
            raise ValueError(
                f"MVCC key-level resolve requires a non-empty even-length hex key: key={key_hex!r}"
            )
        if lock_type not in self._MVCC_LOCK_TYPE_CHARACTERS:
            raise ValueError(
                "MVCC key-level resolve requires lock_type as the decoded lock-type character "
                f"({'/'.join(self._MVCC_LOCK_TYPE_CHARACTERS)}): lock_type={lock_type!r}"
            )
        if not isinstance(start_ts, int) or isinstance(start_ts, bool) or start_ts <= 0:
            raise ValueError(
                "MVCC key-level resolve requires the decoded integer start_ts of the lock record: "
                f"start_ts={start_ts!r}"
            )
        inspection = self._mvcc_inspections.get(inspection_id)
        if inspection is None:
            raise ValueError(
                f"MVCC key-level resolve requires a live inspect result: inspection_id={inspection_id!r}, "
                f"known={sorted(self._mvcc_inspections)!r}"
            )
        procedure = TIKV_STORAGE_MAINTENANCE_PROCEDURE
        if procedure != inspection["procedure"]:
            raise RuntimeError(
                "TiKV storage maintenance procedure changed in the runtime: "
                f"inspection_id={inspection_id!r}, inspected_procedure={inspection['procedure']!r}, "
                f"runtime_procedure={procedure!r}"
            )
        scope = self._mvcc_region_scope(region_id, inspection["store_targets"])
        if tuple(scope["store_targets"]) != tuple(inspection["store_targets"]):
            raise ValueError(
                "MVCC key-level resolve scope changed after inspect: "
                f"inspection_id={inspection_id!r}, inspected_targets={inspection['store_targets']!r}, "
                f"requested_targets={scope['store_targets']!r}"
            )
        current_tool = self._mvcc_tool_metadata(
            self._mvcc_tikv_mounts(self._mvcc_compose_service(scope["store_targets"][0]))[2]
        )
        if current_tool != inspection["tool"]:
            raise RuntimeError(
                "TiKV trusted tool identity changed after inspect: "
                f"inspection_id={inspection_id!r}, inspected_tool={inspection['tool']!r}, "
                f"current_tool={current_tool!r}"
            )
        normalized_key = key_hex.upper()
        scan = self.mvcc_lock_list(region_id, scope["store_targets"], 128)
        per_peer = {
            str(peer["target"]): [
                record for record in peer["records"]
                if str(record["key_hex"]).upper() == normalized_key
            ]
            for peer in scan["peers"]
        }
        absent = sorted(target for target, records in per_peer.items() if len(records) != 1)
        if absent:
            record_counts = {target: len(records) for target, records in per_peer.items()}
            raise ValueError(
                "MVCC key-level resolve requires exactly one lock record for the key on every "
                f"Region peer: key={normalized_key!r}, region_id={region_id}, "
                f"records_per_peer={record_counts!r}, absent_peers={absent!r}"
            )
        decoded_by_peer = {
            target: self.mvcc_decode_lock_record(records[0]["value_hex"])
            for target, records in per_peer.items()
        }
        observed_types = {decoded["lock_type"] for decoded in decoded_by_peer.values()}
        observed_starts = {decoded["start_ts"] for decoded in decoded_by_peer.values()}
        if len(observed_types) != 1 or len(observed_starts) != 1:
            raise ValueError(
                "MVCC key-level resolve observed an inconsistent lock record across Region peers: "
                f"key={normalized_key!r}, decoded={decoded_by_peer!r}"
            )
        actual_type = next(iter(observed_types))
        actual_start = next(iter(observed_starts))
        if actual_type != lock_type or actual_start != int(start_ts):
            raise ValueError(
                "MVCC key-level resolve credentials do not match the stored lock record: "
                f"key={normalized_key!r}, stated=(lock_type={lock_type!r}, start_ts={start_ts!r}), "
                f"actual=(lock_type={actual_type!r}, start_ts={actual_start!r})"
            )
        if actual_type == "S":
            raise ValueError(
                f"MVCC key-level resolve refused: key {normalized_key!r} holds a pessimistic "
                f"in-flight transaction lock (start_ts={actual_start!r}); a live transaction lock "
                f"must not be resolved by storage maintenance"
            )
        result = self.delete_mvcc_lock(region_id, scope["store_targets"], normalized_key)
        del self._mvcc_inspections[inspection_id]
        return {
            "inspection_id": inspection_id,
            "procedure": procedure,
            "region_id": region_id,
            "peer_store_ids": list(scope["peer_store_ids"]),
            "store_targets": list(scope["store_targets"]),
            "resolved_key": normalized_key,
            "lock_type": actual_type,
            "start_ts": actual_start,
            "scope": "key",
            "read_only": False,
            "peers": result["peers"],
        }

    def rewrite_mvcc_lock(
        self,
        region_id: int,
        store_targets: list[str] | tuple[str, ...],
        key_hex: str,
        value_hex: str,
    ) -> dict[str, object]:
        if re.fullmatch(r"[0-9A-Fa-f]+", key_hex or "") is None or len(key_hex) % 2:
            raise ValueError(f"K01 lock rewrite key must be non-empty even-length hex: key_hex={key_hex!r}")
        if re.fullmatch(r"[0-9A-Fa-f]+", value_hex or "") is None or len(value_hex) % 2:
            raise ValueError(f"K01 lock rewrite value must be non-empty even-length hex: value_hex={value_hex!r}")
        scope = self._mvcc_region_scope(region_id, store_targets)
        storage_key_hex = (
            f"{self._MVCC_DATA_PREFIX_HEX}"
            f"{self._mvcc_encode_memcomparable_key(bytes.fromhex(key_hex)).hex().upper()}"
        )

        def rewrite(services):
            peer_results = []
            for target, service in zip(scope["store_targets"], services):
                output, metadata = self._mvcc_tikv_ctl(
                    service,
                    [
                        "ldb",
                        "--db=/data/tikv/db",
                        "--column_family=lock",
                        "--hex",
                        "put",
                        f"0x{storage_key_hex}",
                        f"0x{value_hex}",
                    ],
                    region_id=region_id,
                    store_targets=scope["store_targets"],
                )
                peer_results.append({"target": target, "output": output, "tool": metadata})
            return peer_results

        results = self._mvcc_offline_call_many(
            tuple(scope["store_targets"]),
            "trusted_lock_rewrite",
            rewrite,
        )
        return {
            "region_id": region_id,
            "peer_store_ids": list(scope["peer_store_ids"]),
            "store_targets": list(scope["store_targets"]),
            "key_hex": key_hex,
            "storage_key_hex": storage_key_hex,
            "peers": results,
        }

    def _tikv_target(self, target: str) -> str:
        if target not in self.NODES or not target.startswith("tikv/"):
            raise ValueError(
                f"TiKV maintenance target must be a TiKV node: target={target!r}, "
                f"expected={[node for node in self.NODES if node.startswith('tikv/')]}"
            )
        return self.NODES[target]

    def _store_for_target(self, target: str) -> dict[str, object]:
        service = self._tikv_target(target)
        expected_address = f"{service}:20160"
        matches = [
            item
            for item in self._pd_stores()
            if item["store"]["address"] == expected_address
        ]
        if len(matches) != 1:
            raise RuntimeError(
                f"PD must expose exactly one store for TiKV target: target={target!r}, "
                f"address={expected_address!r}, matches={matches!r}"
            )
        return matches[0]

    def _store_state(self, target: str) -> str:
        return str(self._store_for_target(target)["store"]["state_name"])

    def _wait_store_state(self, target: str, expected: str, timeout: int = 180) -> dict[str, object]:
        observed: dict[str, object] = {}

        def check() -> None:
            nonlocal observed
            observed = self._store_for_target(target)
            actual = str(observed["store"]["state_name"])
            if actual != expected:
                raise RuntimeError(
                    f"TiKV store state has not reached target: target={target!r}, "
                    f"expected={expected!r}, observed={actual!r}, store={observed!r}"
                )

        self._wait(target, check, timeout)
        return observed

    def _record_maintenance(self, event: str, **details: object) -> None:
        self._maintenance_audit.append({"event": event, **details})

    def maintenance_observation(self) -> dict[str, object]:
        return {
            "stores": self._pd_stores(),
            "operators": self._pd_ctl("operator", "show"),
            "audit": [dict(item) for item in self._maintenance_audit],
        }

    def scale_out_tikv(self, target: str) -> dict[str, object]:
        service = self._tikv_target(target)
        if any(
            item["store"]["address"] == f"{service}:20160"
            for item in self._pd_stores()
        ):
            raise RuntimeError(
                f"TiKV scale-out target already has a PD store: target={target!r}, service={service!r}"
            )
        state = self.node_states()[target]
        if state["running"]:
            raise RuntimeError(
                f"TiKV scale-out target container must be stopped before scale-out: "
                f"target={target!r}, state={state!r}"
            )
        self.start_component(target)
        store = self._wait_store_state(target, "Up")
        store_id = store["store"]["id"]
        self._record_maintenance("scale_out", target=target, store_id=store_id)
        return {"target": target, "state": "Up", "store_id": store_id}

    def prepare_scale_out_slot(self, target: str) -> None:
        service = self._tikv_target(target)
        store = self._store_for_target(target)
        state = str(store["store"]["state_name"])
        if state != "Up":
            raise RuntimeError(
                f"Scale-out slot preparation requires an Up store: target={target!r}, "
                f"state={state!r}, store={store!r}"
            )
        store_id = store["store"]["id"]
        self._pd_ctl("store", "delete", str(store_id))
        tombstone = self._wait_store_state(target, "Tombstone")
        self.stop_component(target)
        self._run(self._compose + ["rm", "--force", service], target)
        self._pd_ctl("store", "remove-tombstone")
        self._run(self._compose + ["create", service], target)
        self._record_maintenance(
            "scale_out_slot_prepared",
            target=target,
            old_store_id=store_id,
            tombstone_observed=tombstone["store"]["state_name"] == "Tombstone",
        )

    def scale_in_tikv(self, target: str) -> dict[str, object]:
        store = self._store_for_target(target)
        state = str(store["store"]["state_name"])
        if state != "Up":
            raise RuntimeError(
                f"TiKV scale-in requires an Up store: target={target!r}, state={state!r}, store={store!r}"
            )
        store_id = store["store"]["id"]
        self._pd_ctl("store", "delete", str(store_id))
        self._record_maintenance(
            "scale_in_started",
            target=target,
            store_id=store_id,
            state_before=state,
        )
        return {"target": target, "state": "Offline", "store_id": store_id}

    def replace_tikv_disk(self, target: str) -> dict[str, object]:
        store = self._store_for_target(target)
        state = str(store["store"]["state_name"])
        if state != "Tombstone":
            raise RuntimeError(
                f"TiKV disk replacement requires a Tombstone store after scale-in: "
                f"target={target!r}, state={state!r}, store={store!r}"
            )
        tombstones = [
            item for item in self._pd_stores()
            if str(item["store"]["state_name"]) == "Tombstone"
        ]
        if len(tombstones) != 1 or tombstones[0]["store"]["id"] != store["store"]["id"]:
            raise RuntimeError(
                f"TiKV disk replacement requires exactly the requested Tombstone store: "
                f"target={target!r}, target_store={store!r}, tombstones={tombstones!r}"
            )
        old_store_id = store["store"]["id"]
        service = self._tikv_target(target)
        self.stop_component(target)
        self._run(self._compose + ["rm", "--force", service], target)
        self._pd_ctl("store", "remove-tombstone")
        self._run(self._compose + ["create", service], target)
        self.start_component(target)
        new_store = self._wait_store_state(target, "Up")
        new_store_id = new_store["store"]["id"]
        self._record_maintenance(
            "disk_replaced",
            target=target,
            old_store_id=old_store_id,
            new_store_id=new_store_id,
            tombstone_observed=True,
        )
        return {
            "target": target,
            "state": "Up",
            "old_store_id": old_store_id,
            "new_store_id": new_store_id,
            "tombstone_observed": True,
        }

    def restore_tikv_stores(self, targets: tuple[str, ...]) -> None:
        """Restore only the isolated TiKV slots owned by a fault injector."""
        if not targets:
            raise ValueError("TiKV restore requires at least one target")
        if len(set(targets)) != len(targets):
            raise ValueError(f"TiKV restore targets must be unique: targets={targets!r}")
        unknown_targets = tuple(
            target
            for target in targets
            if target not in self.NODES or not target.startswith("tikv/")
        )
        if unknown_targets:
            raise ValueError(
                "TiKV restore targets must be configured TiKV nodes: "
                f"targets={targets!r}, unknown_targets={unknown_targets!r}"
            )
        stores = self._pd_stores()
        by_target = {}
        for item in stores:
            target = f"tikv/{str(item['store']['address']).split(':', 1)[0]}"
            if target in by_target:
                raise RuntimeError(
                    "PD returned duplicate TiKV target mappings during restore: "
                    f"target={target!r}, stores={by_target[target]!r}, duplicate={item!r}"
                )
            by_target[target] = item
        tombstone_targets = tuple(
            target
            for target in targets
            if target in by_target
            and str(by_target[target]["store"].get("state_name")) == "Tombstone"
        )
        unexpected_tombstones = tuple(
            target
            for target, item in by_target.items()
            if str(item["store"].get("state_name")) == "Tombstone" and target not in targets
        )
        if unexpected_tombstones:
            raise RuntimeError(
                "TiKV restore found a Tombstone outside the Case-owned targets: "
                f"targets={targets!r}, unexpected_tombstones={unexpected_tombstones!r}"
            )
        restore_states = {target: self._service_state(target) for target in targets}
        for target in targets:
            if not restore_states[target]["missing"]:
                continue
            # 共享宿主机的外部清理可能删掉已退出的 Case 容器：原地重建容器
            # （数据目录仍在，TiKV 以原 Store 身份重新注册），让下方各分支
            # 与等待循环面对真实容器。
            service = self.NODES[target]
            self.active_tikv_services.discard(service)
            self._run(self._compose + ["create", service], target)
            self._container_ids.pop(service, None)
        for target in tombstone_targets:
            service = self.NODES[target]
            if restore_states[target]["running"]:
                self._control("stop", target)
            self.active_tikv_services.discard(service)
            self._run(self._compose + ["rm", "--force", service], target)
        if tombstone_targets:
            self._pd_ctl("store", "remove-tombstone")
            for target in tombstone_targets:
                self._run(self._compose + ["create", self.NODES[target]], target)
                self._container_ids.pop(self.NODES[target], None)
        removed_targets = tuple(target for target in targets if target not in by_target)
        for target in removed_targets:
            # PD 记录已被删除的 Store：旧容器带着本地数据重启必然被 PD 以
            # StoreTombstone 拒绝。清空数据目录并重建容器，让 TiKV 以全新
            # Store 身份重新注册，由健康副本回补数据。
            service = self.NODES[target]
            if restore_states[target]["running"]:
                self._control("stop", target)
            self.active_tikv_services.discard(service)
            self._run(self._compose + ["rm", "--force", service], target)
            data_dir = (
                self._persistent_run_dir / service
                if self.persistent_storage_enabled
                else self.bootstrap_data_paths[("tikv", service)]
            )
            shutil.rmtree(data_dir, ignore_errors=True)
            os.makedirs(data_dir, exist_ok=True)
            self._run(self._compose + ["create", service], target)
            self._container_ids.pop(service, None)
        for target in targets:
            service = self.NODES[target]
            running = restore_states[target]["running"]
            store = by_target.get(target)
            if not running:
                self.start_component(target)
                continue
            if store is None or str(store["store"].get("state_name")) != "Up":
                self.restart_component(target)
                self.active_tikv_services.add(service)
        self._container_ids.clear()
        for target in targets:
            last_error: RuntimeError | None = None
            for attempt in range(3):
                try:
                    self._wait_store_state(target, "Up", timeout=300)
                    last_error = None
                    break
                except RuntimeError as exc:
                    last_error = exc
                    # 恢复目标 TiKV 偶发撞上启动期 gRPC deadline 而退出（exit 1）；
                    # 重启容器再等一轮，仍失败则把最后一次错误抛出。
                    if not self.node_states()[target]["running"]:
                        self.start_component(target)
            if last_error is not None:
                raise last_error

    def region_health_observation(self) -> dict[str, object]:
        return {
            "stores": self._pd_stores(),
            "operators": self._pd_ctl("operator", "show"),
        }

    def _require_upgrade_release(self):
        if self.upgrade_release is None:
            raise RuntimeError(
                f"TiDB upgrade release is not configured: run_id={self.run_id!r}, "
                f"current_release={self.release.version!r}"
            )
        return self.upgrade_release

    def upgrade_precheck(self) -> dict[str, object]:
        self._check_pd()
        self._check_tikv()
        self._check_tidb()
        operators = self._pd_ctl("operator", "show")
        return {
            "pd_members": self.topology.pd_count,
            "tikv_up": self.topology.tikv_count,
            "tidb_endpoints": len(self.tidb_endpoints),
            "operators": operators,
            "current_version": self.release.version,
            "target_version": self._require_upgrade_release().version,
        }

    def wait_for_upgrade_precheck(self) -> dict[str, object]:
        observed: dict[str, object] = {}

        def check() -> None:
            observed.clear()
            observed.update(self.upgrade_precheck())

        self._wait("upgrade precheck", check, self.warm_tidb_readiness_timeout_sec)
        return dict(observed)

    def _upgrade_targets(self, node_type: str) -> tuple[str, ...]:
        if node_type not in {"pd", "tikv", "tidb"}:
            raise ValueError(f"TiDB rolling upgrade does not support node_type={node_type!r}")
        return tuple(f"{node_type}/{service}" for service in self.COMPONENTS[node_type])

    def _upgrade_image_for_target(self, target: str) -> str:
        release = self._require_upgrade_release()
        node_type, service = target.split("/", 1)
        if node_type == "pd":
            image = release.pd_image
        elif node_type == "tikv":
            image = release.tikv_image
        elif node_type == "tidb":
            image = release.tidb_image
        else:
            raise ValueError(f"TiDB rolling upgrade target must be database component: target={target!r}")
        if subprocess.run(
            ["docker", "image", "inspect", image],
            capture_output=True,
            env=self._env,
        ).returncode != 0:
            raise RuntimeError(
                f"TiDB upgrade image is unavailable: run_id={self.run_id!r}, "
                f"target={target!r}, image={image!r}, target_version={release.version!r}"
            )
        return image

    def _upgrade_predecessors_ready(self, node_type: str) -> None:
        required_types = {
            "pd": (),
            "tikv": ("pd",),
            "tidb": ("pd", "tikv"),
        }[node_type]
        upgraded = set(self._component_image_overrides)
        missing = {
            required_type: sorted(
                service
                for service in self.COMPONENTS[required_type]
                if service not in upgraded
            )
            for required_type in required_types
        }
        missing = {node_type: services for node_type, services in missing.items() if services}
        if missing:
            raise RuntimeError(
                f"TiDB rolling upgrade order is invalid: run_id={self.run_id!r}, "
                f"component={node_type!r}, missing_predecessors={missing!r}, "
                f"upgraded_services={sorted(upgraded)!r}"
            )

    def _wait_upgraded_component(self, target: str) -> None:
        node_type = target.split("/", 1)[0]
        if node_type == "pd":
            self._wait("rolling upgrade PD", self._check_pd_control_plane, 180)
        elif node_type == "tikv":
            self._wait("rolling upgrade TiKV", self._check_tikv, 240)
        elif node_type == "tidb":
            self._wait_tidb_target(target, self.tidb_readiness_timeout_sec)
        else:
            raise ValueError(f"Unsupported upgraded component target: target={target!r}")

    def _check_pd_control_plane(self) -> None:
        self._check_pd()
        self._pd_stores()

    def _set_tikv_leader_weight(
        self,
        store_id: int,
        leader_weight: object,
        region_weight: object,
    ) -> None:
        self._pd_ctl(
            "store",
            "weight",
            str(store_id),
            str(leader_weight),
            str(region_weight),
        )

    def _transfer_tikv_leaders(
        self,
        target: str,
        store_id: int,
        leader_count_before: int,
    ) -> int:
        if leader_count_before == 0:
            return 0

        scheduler_name = f"evict-leader-scheduler-{store_id}"
        self._pd_ctl(
            "scheduler",
            "add",
            "evict-leader-scheduler",
            str(store_id),
        )

        def leaders_evicted() -> None:
            current = self._store_for_target(target)
            observed = int(current["status"].get("leader_count", 0))
            if observed != 0:
                raise RuntimeError(
                    f"TiKV leader evacuation is incomplete: run_id={self.run_id!r}, "
                    f"target={target!r}, store_id={store_id!r}, "
                    f"expected_leader_count=0, observed_leader_count={observed}, store={current!r}"
                )

        try:
            self._wait("TiKV leader transfer", leaders_evicted, 300)
        finally:
            self._pd_ctl("scheduler", "remove", scheduler_name)
        return leader_count_before

    def upgrade_component(self, target: str) -> dict[str, object]:
        if target not in self.NODES or target.startswith("monitoring/"):
            raise ValueError(
                f"TiDB rolling upgrade target must be a database node: target={target!r}, "
                f"expected={self.database_nodes!r}"
            )
        node_type, service = target.split("/", 1)
        self._upgrade_predecessors_ready(node_type)
        if service in self._component_image_overrides:
            raise RuntimeError(
                f"TiDB component was already upgraded: run_id={self.run_id!r}, target={target!r}, "
                f"overrides={self._component_image_overrides!r}"
            )
        image = self._upgrade_image_for_target(target)
        leader_count = None
        leader_count_after = None
        leader_transfer_count = None
        store_id = None
        original_leader_weight = None
        original_region_weight = None
        try:
            if node_type == "tikv":
                store = self._store_for_target(target)
                store_id = int(store["store"]["id"])
                original_leader_weight = store["status"]["leader_weight"]
                original_region_weight = store["status"]["region_weight"]
                leader_count = int(store["status"].get("leader_count", 0))
                self._set_tikv_leader_weight(store_id, 0, 0)
                if leader_count:
                    leader_transfer_count = self._transfer_tikv_leaders(
                        target,
                        store_id,
                        leader_count,
                    )
                else:
                    leader_transfer_count = 0
                leader_count_after = 0
            self._component_image_overrides[service] = image
            self._render_runtime_files()
            self._run(
                self._compose + ["up", "--detach", "--no-deps", "--force-recreate", service],
                target,
            )
            self._container_ids.clear()
            self._wait_upgraded_component(target)
        finally:
            if original_leader_weight is not None:
                self._set_tikv_leader_weight(
                    int(store_id),
                    original_leader_weight,
                    original_region_weight,
                )
        release = self._require_upgrade_release()
        event = {
            "event": "component_upgrade",
            "target": target,
            "component": node_type,
            "service": service,
            "from_version": self.release.version,
            "to_version": release.version,
            "leader_count_before": leader_count,
            "leader_count_after": leader_count_after,
            "leader_transfer_count": leader_transfer_count,
            "store_id": store_id,
        }
        self._upgrade_audit.append(event)
        return dict(event)

    def rollback_component(self, target: str) -> dict[str, object]:
        if target not in self.NODES or target.startswith("monitoring/"):
            raise ValueError(f"TiDB rollback target must be a database node: target={target!r}")
        service = self.NODES[target]
        if service not in self._component_image_overrides:
            raise RuntimeError(
                f"TiDB rollback target is not upgraded: run_id={self.run_id!r}, target={target!r}"
            )
        upgrades = [item for item in self._upgrade_audit if item["event"] == "component_upgrade"]
        if not upgrades or upgrades[-1]["target"] != target:
            raise RuntimeError(
                f"TiDB rollback must reverse the most recent component: run_id={self.run_id!r}, "
                f"target={target!r}, last_upgrade={upgrades[-1] if upgrades else None!r}"
            )
        self._component_image_overrides.pop(service)
        self._render_runtime_files()
        self._run(
            self._compose + ["up", "--detach", "--no-deps", "--force-recreate", service],
            target,
        )
        self._container_ids.clear()
        self._wait_upgraded_component(target)
        release = self._require_upgrade_release()
        event = {
            "event": "component_rollback",
            "target": target,
            "component": target.split("/", 1)[0],
            "from_version": release.version,
            "to_version": self.release.version,
        }
        self._upgrade_audit.append(event)
        return dict(event)

    def verify_monitoring_coverage(self) -> dict[str, object]:
        self._wait(
            "monitoring",
            self._check_prometheus,
            self._prometheus_readiness_timeout(),
        )
        from urllib.parse import urlencode
        from urllib.request import urlopen

        query = urlencode({"query": "up"})
        with urlopen(
            f"http://127.0.0.1:{self.prometheus_port}/api/v1/query?{query}", timeout=5
        ) as response:
            payload = json.load(response)
        targets = payload["data"]["result"]
        observed = [
            {
                "job": item["metric"].get("job"),
                "instance": item["metric"].get("instance"),
                "value": item["value"][1],
            }
            for item in targets
        ]
        event = {
            "event": "monitoring_verified",
            "target_count": len(observed),
            "targets": observed,
        }
        self._upgrade_audit.append(event)
        return dict(event)

    def record_upgrade_event(self, event: str, **details: object) -> dict[str, object]:
        if not event:
            raise ValueError("TiDB upgrade audit event must be non-empty")
        record = {"event": event, **details}
        self._upgrade_audit.append(record)
        return dict(record)

    def upgrade_agent_observation(self) -> dict[str, object]:
        return {
            "current_version": self.release.version,
            "target_version": self.upgrade_release.version if self.upgrade_release else None,
        }

    def upgrade_evaluation_state(self) -> dict[str, object]:
        return {
            "audit": [dict(item) for item in self._upgrade_audit],
            "component_images": dict(self._component_image_overrides),
            "current_version": self.release.version,
            "target_version": self.upgrade_release.version if self.upgrade_release else None,
        }

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
        if self.persistent_state_reused or self.image_group_reused:
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
            if self.persistent_storage_enabled or self.image_group_enabled:
                timeout = (
                    self.warm_tidb_readiness_timeout_sec
                    if self.persistent_state_reused or self.image_group_reused
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
        self.preflight()
        if self._project_exists():
            self._release_port_holds()
            if self.is_ready():
                self._deployment_reached_ready = True
                return
            raise RuntimeError(
                f"TiDB Compose project exists but is not ready: run_id={self.run_id!r}, "
                f"last_readiness_error={self._last_readiness_error!r}; run teardown() before creating a fresh environment"
            )
        self._prepare_persistent_state()
        try:
            self._start_cluster()
        except Exception as error:
            self._retry_cluster_start(error)
        if (
            not self.persistent_storage_enabled
            and not self.image_group_enabled
            and self.bootstrap_cache_enabled
            and self.topology.deferred_tikv_count == 0
        ):
            self._save_bootstrap_cache()

    def _start_cluster(self) -> None:
        self._release_port_holds()
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
        if self.image_group_enabled:
            raise first_error
        if self.persistent_storage_enabled:
            if not self.persistent_state_reused:
                raise first_error
            print(
                f"[Deployment] TiDB persistent baseline failed to start; rebuilding it once: "
                f"run_id={self.run_id!r}, storage_key={self.storage_key!r}, error={first_error!r}"
            )
            self._reset_partial_cluster()
            self._discard_persistent_baseline()
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
        self._discard_bootstrap_cache()
        self._reset_partial_cluster()
        try:
            self._start_cluster()
        except Exception as retry_error:
            raise RuntimeError(
                f"TiDB cluster start retry failed: run_id={self.run_id!r}, first_error={first_error!r}"
            ) from retry_error

    def _discard_bootstrap_cache(self) -> None:
        """Drop a cache-seeded start that cannot boot; the next success re-saves it."""
        if not self.bootstrap_cache_used:
            return
        shutil.rmtree(self.bootstrap_cache_path)
        self.bootstrap_cache_used = False

    def _discard_persistent_baseline(self) -> None:
        """Drop a reused baseline that cannot boot; the next successful start re-persists it."""
        self.persistent_state_reused = False
        self._acquire_persistent_lock()
        try:
            shutil.rmtree(self._persistent_baseline_dir)
        finally:
            self.release_persistence_lock()
        self._persistent_state_pending = True

    def _reset_partial_cluster(self) -> None:
        self._run(self._compose + ["down", "--volumes", "--remove-orphans"], "deployment-retry")
        if self._network_created:
            self._run(["docker", "network", "rm", self.network_name], "deployment-retry network")
            self._network_created = False
        self._container_ids.clear()
        for (node_type, service), destination in self.bootstrap_data_paths.items():
            shutil.rmtree(destination)
            os.makedirs(destination)
            if self.bootstrap_cache_used:
                self._copy_tree(
                    os.path.join(self.bootstrap_cache_path, node_type, service), destination
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
        pd_targets = self._tidb_stale_egress_targets.get(target)
        if pd_targets:
            self.allow_pd_network_stale_egress(target, pd_targets)
        pd_targets = self._tidb_egress_shadow_targets.get(target)
        if pd_targets:
            self._run_network_namespace_tool(
                target,
                self._tidb_egress_shadow_rule_script(pd_targets),
            )
        addresses = self._tidb_pd_network_rehydration_addresses.get(target)
        if addresses:
            self._run_network_namespace_tool(
                target,
                self._pd_network_rehydration_rule_script(addresses),
            )

    def restart_pd_quorum(self) -> None:
        services = self.COMPONENTS["pd"]
        self._run(self._compose + ["restart", *services], "pd quorum restart")
        self._container_ids.clear()

    def arm_pd_network_rehydration(
        self,
        target: str,
        pd_targets: tuple[str, ...],
    ) -> None:
        if target not in self.NODES or not target.startswith("tidb/"):
            raise ValueError(f"Unknown TiDB rehydration target: target={target!r}")
        unknown_pd_targets = tuple(
            pd_target
            for pd_target in pd_targets
            if pd_target not in self.NODES or not pd_target.startswith("pd/")
        )
        if unknown_pd_targets:
            raise ValueError(
                f"Unknown PD rehydration targets: target={target!r}, pd_targets={unknown_pd_targets!r}"
            )
        hosts = " ".join(shlex.quote(self.NODES[pd_target]) for pd_target in pd_targets)
        output = self._run_network_namespace_tool(
            target,
            "set -eu; "
            f"for host in {hosts}; do "
            "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}'); "
            "test -n \"$ip\"; printf '%s\\n' \"$ip\"; "
            "done",
        )
        addresses = tuple(output.splitlines())
        if len(addresses) != len(pd_targets) or any(not address for address in addresses):
            raise RuntimeError(
                "TiDB PD network rehydration address resolution is invalid: "
                f"target={target!r}, pd_targets={pd_targets!r}, addresses={addresses!r}, output={output!r}"
            )
        self._tidb_pd_network_rehydration_targets[target] = tuple(pd_targets)
        self._tidb_pd_network_rehydration_addresses[target] = addresses

    def disarm_pd_network_rehydration(self, target: str) -> None:
        self._tidb_pd_network_rehydration_targets.pop(target, None)
        self._tidb_pd_network_rehydration_addresses.pop(target, None)

    def _pd_network_rehydration_rule_script(self, addresses: tuple[str, ...]) -> str:
        commands = ["set -eu"]
        commands.extend(
            "iptables -A OUTPUT -p tcp -d "
            f"{shlex.quote(address)} --dport 2379 -j REJECT --reject-with tcp-reset"
            for address in addresses
        )
        commands.append("iptables -S OUTPUT")
        return "; ".join(commands)

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

    def _run_network_namespace_tool(self, target: str, script: str) -> str:
        service, = self._services(target)
        container_id = self._service_container_id(service)
        self._run(
            ["docker", "image", "inspect", self.NETWORK_TOOL_IMAGE],
            "network-helper-image",
        )
        return self._run(
            [
                "docker", "run", "--rm",
                "--network", f"container:{container_id}",
                "--cap-add", "NET_ADMIN",
                "--entrypoint", "/bin/sh",
                self.NETWORK_TOOL_IMAGE,
                "-ceu", script,
            ],
            target,
        )

    def _pd_network_rule_script(
        self,
        operation: str,
        pd_targets: tuple[str, ...] | None = None,
    ) -> str:
        if operation not in {"-A", "-D"}:
            raise ValueError(f"Unsupported PD network rule operation: {operation!r}")
        pd_hosts = " ".join(
            shlex.quote(service)
            for service in (self.COMPONENTS["pd"] if pd_targets is None else pd_targets)
        )
        if operation == "-A":
            body = (
                "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}'); "
                "test -n \"$ip\"; "
                "iptables -A OUTPUT -p tcp -d \"$ip\" --dport 2379 "
                "-j REJECT --reject-with tcp-reset; "
            )
        else:
            body = (
                "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}') || true; "
                'if [ -n "$ip" ]; then '
                'rule="OUTPUT -p tcp -d $ip --dport 2379 -j REJECT --reject-with tcp-reset"; '
                'if iptables -C $rule; then iptables -D $rule; else status=$?; test "$status" -eq 1; fi; '
                'fi; '
            )
        return (
            "set -eu; "
            f"for host in {pd_hosts}; do "
            + body
            + "done; "
            "iptables -S OUTPUT"
        )

    def block_pd_network(self, target: str) -> str:
        return self._run_network_namespace_tool(
            target,
            self._pd_network_rule_script("-A"),
        )

    def _pd_response_egress_rule_script(
        self,
        operation: str,
        destination_targets: tuple[str, ...],
    ) -> str:
        if operation not in {"-A", "-D"}:
            raise ValueError(f"Unsupported PD response egress operation: {operation!r}")
        commands = [
            "set -eu",
            "source_ip=$(ip -4 -o addr show scope global | "
            "awk 'NR == 1 {split($4, parts, \"/\"); print parts[1]}')",
            'test -n "$source_ip"',
        ]
        for target in destination_targets:
            host = shlex.quote(self.NODES[target])
            if operation == "-A":
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}')",
                    'test -n "$ip"',
                ])
            else:
                commands.append(
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}') || true"
                )
            rule = (
                'OUTPUT -p tcp -s "$source_ip" --sport 2379 -d "$ip" '
                "-m comment --comment pd-response-policy -j REJECT --reject-with tcp-reset"
            )
            if operation == "-A":
                commands.append(f"iptables -A {rule}")
            else:
                commands.append(
                    f'if [ -n "$ip" ] && iptables -C {rule}; then iptables -D {rule}; '
                    'else status=$?; test "$status" -eq 1; fi'
                )
        commands.extend(["iptables -S INPUT", "iptables -S OUTPUT"])
        return "; ".join(commands)

    def block_pd_network_response(
        self,
        pd_targets: tuple[str, ...],
        destination_target: str,
    ) -> str:
        unknown_pd_targets = tuple(
            target for target in pd_targets
            if target not in self.NODES or not target.startswith("pd/")
        )
        if unknown_pd_targets:
            raise ValueError(
                f"Unknown PD response egress sources: pd_targets={unknown_pd_targets!r}"
            )
        if destination_target not in self.NODES or not destination_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown PD response egress destination: destination_target={destination_target!r}"
            )
        output = ""
        for pd_target in pd_targets:
            self._pd_response_egress_targets.setdefault(pd_target, set()).add(destination_target)
            output = self._run_network_namespace_tool(
                pd_target,
                self._pd_response_egress_rule_script("-A", (destination_target,)),
            )
        return output

    def allow_pd_network_response(
        self,
        pd_target: str,
        destination_target: str,
    ) -> str:
        if pd_target not in self.NODES or not pd_target.startswith("pd/"):
            raise ValueError(f"Unknown PD response egress source: pd_target={pd_target!r}")
        if destination_target not in self.NODES or not destination_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown PD response egress destination: destination_target={destination_target!r}"
            )
        output = self._run_network_namespace_tool(
            pd_target,
            self._pd_response_egress_rule_script("-D", (destination_target,)),
        )
        destinations = self._pd_response_egress_targets.get(pd_target)
        if destinations is not None:
            destinations.discard(destination_target)
            if not destinations:
                self._pd_response_egress_targets.pop(pd_target)
        return output

    def _pd_response_egress_shadow_rule_script(
        self,
        operation: str,
        destination_targets: tuple[str, ...],
    ) -> str:
        if operation not in {"-A", "-D"}:
            raise ValueError(f"Unsupported PD response egress shadow operation: {operation!r}")
        commands = [
            "set -eu",
            "source_ip=$(ip -4 -o addr show scope global | "
            "awk 'NR == 1 {split($4, parts, \"/\"); print parts[1]}')",
            'test -n "$source_ip"',
        ]
        for target in destination_targets:
            host = shlex.quote(self.NODES[target])
            if operation == "-A":
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}')",
                    'test -n "$ip"',
                ])
            else:
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}') || true",
                ])
            accept_suffix = (
                '-p tcp -s "$source_ip" --sport 2379 -d "$ip" '
                '-j ACCEPT'
            )
            accept_rule = (
                f"OUTPUT {accept_suffix}"
            )
            reject_rule = (
                'OUTPUT -p tcp -s "$source_ip" --sport 2379 -d "$ip" '
                "-m comment --comment pd-response-shadow-policy -j REJECT "
                "--reject-with tcp-reset"
            )
            if operation == "-A":
                commands.extend([
                    f"iptables -I OUTPUT 1 {accept_suffix}",
                    f"iptables -A {reject_rule}",
                ])
            else:
                removals = "; ".join(
                    f"if iptables -C {rule}; then iptables -D {rule}; "
                    'else status=$?; test "$status" -eq 1; fi'
                    for rule in (reject_rule, accept_rule)
                )
                commands.append(f'if [ -n "$ip" ]; then {removals}; fi')
        commands.extend(["iptables -S INPUT", "iptables -S OUTPUT"])
        return "; ".join(commands)

    def block_pd_network_response_shadow(
        self,
        pd_targets: tuple[str, ...],
        destination_targets: tuple[str, ...],
    ) -> str:
        unknown_pd_targets = tuple(
            target for target in pd_targets
            if target not in self.NODES or not target.startswith("pd/")
        )
        if unknown_pd_targets:
            raise ValueError(
                f"Unknown PD response egress shadow sources: pd_targets={unknown_pd_targets!r}"
            )
        unknown_destinations = tuple(
            target for target in destination_targets
            if target not in self.NODES or not target.startswith("tidb/")
        )
        if unknown_destinations:
            raise ValueError(
                "Unknown PD response egress shadow destinations: "
                f"destination_targets={unknown_destinations!r}"
            )
        output = ""
        for pd_target in pd_targets:
            output = self._run_network_namespace_tool(
                pd_target,
                self._pd_response_egress_shadow_rule_script("-A", destination_targets),
            )
            self._pd_response_egress_shadow_targets[pd_target] = set(destination_targets)
        return output

    def allow_pd_network_response_shadow(
        self,
        pd_target: str,
        destination_targets: tuple[str, ...],
    ) -> str:
        if pd_target not in self.NODES or not pd_target.startswith("pd/"):
            raise ValueError(f"Unknown PD response egress shadow source: pd_target={pd_target!r}")
        unknown_destinations = tuple(
            target for target in destination_targets
            if target not in self.NODES or not target.startswith("tidb/")
        )
        if unknown_destinations:
            raise ValueError(
                "Unknown PD response egress shadow destinations: "
                f"destination_targets={unknown_destinations!r}"
            )
        output = self._run_network_namespace_tool(
            pd_target,
            self._pd_response_egress_shadow_rule_script("-D", destination_targets),
        )
        self._pd_response_egress_shadow_targets.pop(pd_target, None)
        return output

    def block_pd_network_egress_shadow(
        self,
        target: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        if target not in self.NODES or not target.startswith("tidb/"):
            raise ValueError(f"Unknown TiDB egress shadow target: target={target!r}")
        unknown_pd_targets = tuple(
            pd_target for pd_target in pd_targets
            if pd_target not in self.NODES or not pd_target.startswith("pd/")
        )
        if unknown_pd_targets:
            raise ValueError(
                f"Unknown TiDB egress shadow PD targets: target={target!r}, "
                f"pd_targets={unknown_pd_targets!r}"
            )
        output = self._run_network_namespace_tool(
            target,
            self._tidb_egress_shadow_rule_script(pd_targets),
        )
        self._tidb_egress_shadow_targets[target] = tuple(pd_targets)
        return output

    def _tidb_egress_shadow_rule_script(
        self,
        pd_targets: tuple[str, ...],
    ) -> str:
        pd_hosts = " ".join(shlex.quote(self.NODES[pd_target]) for pd_target in pd_targets)
        return (
            "set -eu; "
            f"for host in {pd_hosts}; do "
            "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}'); "
            'test -n "$ip"; '
            'iptables -I OUTPUT 1 -p tcp -d "$ip" --dport 2379 -j ACCEPT; '
            'iptables -A OUTPUT -p tcp -d "$ip" --dport 2379 '
            '-m comment --comment pd-client-policy -j REJECT --reject-with tcp-reset; '
            "done; iptables -S INPUT; iptables -S OUTPUT"
        )

    def allow_pd_network_egress_shadow(
        self,
        target: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        if target not in self.NODES or not target.startswith("tidb/"):
            raise ValueError(f"Unknown TiDB egress shadow target: target={target!r}")
        pd_hosts = " ".join(shlex.quote(self.NODES[pd_target]) for pd_target in pd_targets)
        output = self._run_network_namespace_tool(
            target,
            "set -eu; "
            f"for host in {pd_hosts}; do "
            "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}') || true; "
            'if [ -n "$ip" ]; then '
            'reject="OUTPUT -p tcp -d $ip --dport 2379 -m comment --comment pd-client-policy '
            '-j REJECT --reject-with tcp-reset"; '
            'accept="OUTPUT -p tcp -d $ip --dport 2379 -j ACCEPT"; '
            'if iptables -C $reject; then iptables -D $reject; else status=$?; test "$status" -eq 1; fi; '
            'if iptables -C $accept; then iptables -D $accept; else status=$?; test "$status" -eq 1; fi; '
            'fi; '
            "done; iptables -S INPUT; iptables -S OUTPUT",
        )
        self._tidb_egress_shadow_targets.pop(target, None)
        return output

    def _tidb_stale_egress_rule_script(
        self,
        operation: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        if operation not in {"-I", "-D"}:
            raise ValueError(f"Unsupported TiDB stale egress operation: {operation!r}")
        commands = ["set -eu"]
        for pd_target in pd_targets:
            host = shlex.quote(self.NODES[pd_target])
            rule = (
                '-p tcp -d "$ip" --dport 2379 '
                "-m comment --comment pd-client-stale-policy -j REJECT "
                "--reject-with tcp-reset"
            )
            if operation == "-I":
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}')",
                    'test -n "$ip"',
                    f"iptables -I OUTPUT 1 {rule}",
                ])
            else:
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}') || true",
                    f'if [ -n "$ip" ] && iptables -C OUTPUT {rule}; then iptables -D OUTPUT {rule}; '
                    'else status=$?; test "$status" -eq 1; fi',
                ])
        commands.extend(["iptables -S INPUT", "iptables -S OUTPUT"])
        return "; ".join(commands)

    def block_pd_network_stale_egress(
        self,
        target: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        if target not in self.NODES or not target.startswith("tidb/"):
            raise ValueError(f"Unknown TiDB stale egress target: target={target!r}")
        unknown_pd_targets = tuple(
            pd_target
            for pd_target in pd_targets
            if pd_target not in self.NODES or not pd_target.startswith("pd/")
        )
        if unknown_pd_targets:
            raise ValueError(
                f"Unknown TiDB stale egress PD targets: target={target!r}, "
                f"pd_targets={unknown_pd_targets!r}"
            )
        output = self._run_network_namespace_tool(
            target,
            self._tidb_stale_egress_rule_script("-I", pd_targets),
        )
        self._tidb_stale_egress_targets[target] = tuple(pd_targets)
        return output

    def allow_pd_network_stale_egress(
        self,
        target: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        output = self._run_network_namespace_tool(
            target,
            self._tidb_stale_egress_rule_script("-D", pd_targets),
        )
        self._tidb_stale_egress_targets.pop(target, None)
        return output

    def block_pd_network_endpoint(self, target: str, pd_target: str) -> str:
        if pd_target not in self.NODES or not pd_target.startswith("pd/"):
            raise ValueError(
                f"Unknown PD network endpoint: target={target!r}, pd_target={pd_target!r}, "
                f"expected={tuple(f'pd/{service}' for service in self.COMPONENTS['pd'])!r}"
            )
        return self._run_network_namespace_tool(
            target,
            self._pd_network_rule_script("-A", (self.NODES[pd_target],)),
        )

    def block_pd_network_address(self, target: str, address: str) -> str:
        return self._run_network_namespace_tool(
            target,
            "set -eu; "
            "source_ip=$(ip -4 -o addr show scope global | "
            "awk 'NR == 1 {split($4, parts, \"/\"); print parts[1]}'); "
            "test -n \"$source_ip\"; "
            f"iptables -A OUTPUT -s \"$source_ip\" -p tcp -d {shlex.quote(address)} --dport 2379 "
            "-j REJECT --reject-with tcp-reset; "
            "iptables -S INPUT; iptables -S OUTPUT",
        )

    def _pd_ingress_rule_script(
        self,
        operation: str,
        source_targets: tuple[str, ...],
    ) -> str:
        if operation not in {"-A", "-D"}:
            raise ValueError(f"Unsupported PD ingress rule operation: {operation!r}")
        commands = [
            "set -eu",
        ]
        for target in source_targets:
            host = shlex.quote(self.NODES[target])
            marker = shlex.quote("pd-client-policy")
            rule = (
                f"INPUT -p tcp -s \"$ip\" --dport 2379 "
                f"-m comment --comment {marker} -j REJECT --reject-with tcp-reset"
            )
            if operation == "-A":
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}')",
                    'test -n "$ip"',
                    f"iptables -A {rule}",
                ])
            else:
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}') || true",
                    f'if [ -n "$ip" ] && iptables -C {rule}; then iptables -D {rule}; '
                    'else status=$?; test "$status" -eq 1; fi',
                ])
        commands.extend([
            "iptables -S INPUT",
            "iptables -S OUTPUT",
        ])
        return "; ".join(commands)

    def block_pd_network_ingress(
        self,
        source_target: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        if source_target not in self.NODES or not source_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown TiDB PD ingress source: source_target={source_target!r}, "
                f"expected={tuple(f'tidb/{service}' for service in self.COMPONENTS['tidb'])!r}"
            )
        unknown_targets = tuple(target for target in pd_targets if target not in self.NODES or not target.startswith("pd/"))
        if unknown_targets:
            raise ValueError(
                f"Unknown PD ingress targets: source_target={source_target!r}, "
                f"pd_targets={unknown_targets!r}"
            )
        output = ""
        for pd_target in pd_targets:
            self._pd_ingress_sources.setdefault(pd_target, set()).add(source_target)
            output = self._run_network_namespace_tool(
                pd_target,
                self._pd_ingress_rule_script("-A", (source_target,)),
            )
        return output

    def block_pd_network_ingress_decoy(self, source_target: str, pd_target: str) -> str:
        if source_target not in self.NODES or not source_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown TiDB PD ingress decoy source: source_target={source_target!r}, "
                f"expected={tuple(f'tidb/{service}' for service in self.COMPONENTS['tidb'])!r}"
            )
        if pd_target not in self.NODES or not pd_target.startswith("pd/"):
            raise ValueError(
                f"Unknown PD ingress decoy target: source_target={source_target!r}, "
                f"pd_target={pd_target!r}, expected={tuple(f'pd/{service}' for service in self.COMPONENTS['pd'])!r}"
            )
        return self._run_network_namespace_tool(
            pd_target,
            self._pd_ingress_rule_script("-A", (source_target,)),
        )

    def allow_pd_network_ingress_decoy(self, source_target: str, pd_target: str) -> str:
        return self._run_network_namespace_tool(
            pd_target,
            self._pd_ingress_rule_script("-D", (source_target,)),
        )

    def block_pd_network_ingress_shadow(self, source_target: str, pd_target: str) -> str:
        if source_target not in self.NODES or not source_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown TiDB PD ingress shadow source: source_target={source_target!r}, "
                f"expected={tuple(f'tidb/{service}' for service in self.COMPONENTS['tidb'])!r}"
            )
        if pd_target not in self.NODES or not pd_target.startswith("pd/"):
            raise ValueError(
                f"Unknown PD ingress shadow target: source_target={source_target!r}, "
                f"pd_target={pd_target!r}, expected={tuple(f'pd/{service}' for service in self.COMPONENTS['pd'])!r}"
            )
        host = shlex.quote(self.NODES[source_target])
        marker = shlex.quote("pd-client-policy")
        return self._run_network_namespace_tool(
            pd_target,
            "set -eu; "
            f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}'); "
            'test -n "$ip"; '
            'iptables -I INPUT 1 -p tcp -s "$ip" --dport 2379 -j ACCEPT; '
            f"iptables -A INPUT -p tcp -s \"$ip\" --dport 2379 -m comment --comment {marker} "
            "-j REJECT --reject-with tcp-reset; "
            "iptables -S INPUT; iptables -S OUTPUT",
        )

    def allow_pd_network_ingress_shadow(self, source_target: str, pd_target: str) -> str:
        if source_target not in self.NODES or not source_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown TiDB PD ingress shadow source: source_target={source_target!r}, "
                f"expected={tuple(f'tidb/{service}' for service in self.COMPONENTS['tidb'])!r}"
            )
        if pd_target not in self.NODES or not pd_target.startswith("pd/"):
            raise ValueError(
                f"Unknown PD ingress shadow target: source_target={source_target!r}, "
                f"pd_target={pd_target!r}, expected={tuple(f'pd/{service}' for service in self.COMPONENTS['pd'])!r}"
            )
        host = shlex.quote(self.NODES[source_target])
        marker = shlex.quote("pd-client-policy")
        reject_rule = (
            f"INPUT -p tcp -s \"$ip\" --dport 2379 -m comment --comment {marker} "
            "-j REJECT --reject-with tcp-reset"
        )
        accept_rule = 'INPUT -p tcp -s "$ip" --dport 2379 -j ACCEPT'
        return self._run_network_namespace_tool(
            pd_target,
            "set -eu; "
            f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}') || true; "
            'if [ -n "$ip" ]; then '
            f"if iptables -C {reject_rule}; then iptables -D {reject_rule}; "
            'else status=$?; test "$status" -eq 1; fi; '
            f"if iptables -C {accept_rule}; then iptables -D {accept_rule}; "
            'else status=$?; test "$status" -eq 1; fi; '
            'fi; '
            "iptables -S INPUT; iptables -S OUTPUT",
        )

    def inspect_pd_network(self, target: str) -> str:
        return self._run_network_namespace_tool(
            target,
            "set -eu; iptables -S INPUT; iptables -S OUTPUT",
        )

    def allow_pd_network(self, target: str) -> str:
        if target.startswith("pd/"):
            source_targets = tuple(sorted(self._pd_ingress_sources.get(target, ())))
            response_targets = tuple(sorted(self._pd_response_egress_targets.get(target, ())))
            if not source_targets and not response_targets:
                return self.inspect_pd_network(target)
            output = ""
            if source_targets:
                output = self._run_network_namespace_tool(
                    target,
                    self._pd_ingress_rule_script("-D", source_targets),
                )
            for destination_target in response_targets:
                output = self.allow_pd_network_response(target, destination_target)
            return output
        pd_hosts = " ".join(shlex.quote(service) for service in self.COMPONENTS["pd"])
        script = (
            "set -eu; "
            f"for host in {pd_hosts}; do "
            "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}'); "
            "test -n \"$ip\"; "
            "if iptables -C OUTPUT -p tcp -d \"$ip\" --dport 2379 "
            "-j REJECT --reject-with tcp-reset; then "
            "iptables -D OUTPUT -p tcp -d \"$ip\" --dport 2379 "
            "-j REJECT --reject-with tcp-reset; "
            "else status=$?; test \"$status\" -eq 1; fi; "
            "done; "
            "iptables -S INPUT; iptables -S OUTPUT"
        )
        return self._run_network_namespace_tool(target, script)

    def allow_pd_network_address(self, target: str, address: str) -> str:
        script = (
            "set -eu; "
            "source_ip=$(ip -4 -o addr show scope global | "
            "awk 'NR == 1 {split($4, parts, \"/\"); print parts[1]}'); "
            "test -n \"$source_ip\"; "
            f"if iptables -C OUTPUT -s \"$source_ip\" -p tcp -d {shlex.quote(address)} --dport 2379 "
            "-j REJECT --reject-with tcp-reset; then "
            f"iptables -D OUTPUT -s \"$source_ip\" -p tcp -d {shlex.quote(address)} --dport 2379 "
            "-j REJECT --reject-with tcp-reset; "
            "else status=$?; test \"$status\" -eq 1; fi; "
            "iptables -S INPUT; iptables -S OUTPUT"
        )
        return self._run_network_namespace_tool(target, script)

    def wait_for_target(self, target: str, timeout: int = 120) -> None:
        self._wait_tidb_target(target, timeout)

    def teardown(self):
        self._release_port_holds()
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
            if not self.persistent_storage_enabled and not self.image_group_enabled:
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
                                self._normalize_host_directory(
                                    self.bootstrap_data_paths[(node_type, service)],
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
            if not self.persistent_storage_enabled:
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
        if self._persistent_run_dir is not None and self._persistent_run_dir.exists():
            self._make_persistent_state_user_accessible()
            shutil.rmtree(self._persistent_run_dir)
        self.release_persistence_lock()
        if self.runtime_dir is not None and os.path.isdir(self.runtime_dir):
            shutil.rmtree(self.runtime_dir)

    def force_teardown(self) -> None:
        """Immediately remove this run's containers, network, and volumes."""
        self._release_port_holds()
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
        self.release_persistence_lock()

    def destroy(self):
        self.teardown()
