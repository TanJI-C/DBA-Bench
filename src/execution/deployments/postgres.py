from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import time
from typing import Optional, Dict, Any

from src.execution.deployments.base import BaseDeployment
from src.execution.host_ports import claim_host_ports
from src.project_paths import SOURCE_ROOT


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
        self.host_port_offsets = (0,)
        self._port_lease = None
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

        project_root = str(SOURCE_ROOT)
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

            # harness 鲁棒性（非难度变更）：fat 镜像 entrypoint 装载完成后用
            # pg_ctl 关闭临时 server，默认 60s 等待窗口（PGCTLTIMEOUT）在宿主机
            # IO 争用下会被 shutdown checkpoint 超过（2026-09-15 实测容器
            # exit 1，数据装载本身已完成）；放宽等待只影响初始化时长。
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

    def _claim_ports(self) -> None:
        if self._port_lease is None:
            self._port_lease = claim_host_ports(tuple(self.port + offset for offset in self.host_port_offsets),
                                               owner=self.container_name, owned_containers=(self.container_name,))

    def initialize_dataset_container(self):
        self._claim_ports()
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
        self._claim_ports()
        if not self._is_initialized():
            self.initialize_dataset_container()
            subprocess.run(
                ["docker", "stop", "-t", "30", self.container_name],
                check=True,
                capture_output=True,
            )
            # Only workload images have a dataset whose readiness can be labelled.
            label = (
                []
                if self.workload_data_dir is None
                else ["--change", f"LABEL aiopsbench.dataset_ready={self._dataset_ready_label()}"]
            )
            result = subprocess.run(
                ["docker", "commit", *label, self.container_name, self.image_name],
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
        if self._port_lease is not None:
            self._port_lease.close()
            self._port_lease = None

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
