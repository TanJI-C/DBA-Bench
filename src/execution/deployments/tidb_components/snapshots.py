import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Optional, Dict


from src.project_paths import SOURCE_ROOT
from src.execution.deployments.tidb_support import PersistentBaselineIdentityMismatch


class TiDBSnapshots:
    """Snapshots operations and run state."""

    def __init__(self, deployment, storage_key, storage_root, image_group_key):
        self.deployment = deployment
        self.storage_key = storage_key
        self.storage_root = Path(storage_root).resolve() if storage_root else None
        self.image_group_key = image_group_key
        self.image_group_disabled = False
        self.persistent_state_reused = False
        self._persistent_state_pending = False
        self._persistent_lock = None
        self._persistent_base_dir = None
        self._persistent_baseline_dir = None
        self._persistent_run_dir = None
        self.bootstrap_cache_root = deployment._env.get(
            "AIOPS_TIDB_BOOTSTRAP_CACHE_DIR",
            os.path.join(str(SOURCE_ROOT), "data", "tidb", "bootstrap-cache"),
        )
        self.bootstrap_cache_key = None
        self.bootstrap_cache_path = None
        self.bootstrap_cache_used = False
        self.bootstrap_cache_enabled = True
        self.bootstrap_data_paths = {}
        self.image_group_root = Path(
            deployment._env.get(
                "AIOPS_TIDB_IMAGE_GROUP_DIR",
                os.path.join(str(SOURCE_ROOT), "data", "tidb", "image-groups"),
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

    BOOTSTRAP_CACHE_VERSION = 1


    IMAGE_GROUP_VERSION = 1


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
        if self.deployment.topology is not None:
            if self.bootstrap_cache_path is None:
                self._configure_bootstrap_cache()
            self.deployment._render_runtime_files()


    def _image_group_base_metadata(self) -> dict[str, object]:
        if not self.image_group_enabled:
            raise RuntimeError(f"TiDB image group is not configured: run_id={self.deployment.run_id!r}")
        if self.deployment.release is None or self.deployment.topology is None:
            raise RuntimeError(f"TiDB runtime is not configured: run_id={self.deployment.run_id!r}")
        config_dir = os.path.dirname(self.deployment.compose_template)
        tikv_config_path = self.image_group_tikv_config_path
        if tikv_config_path is None:
            raise RuntimeError(
                f"TiDB image-group TiKV config is not prepared: run_id={self.deployment.run_id!r}"
            )
        return {
            "version": self.IMAGE_GROUP_VERSION,
            "image_group_key": self.image_group_key,
            "release_version": self.deployment.release.version,
            "images": list(self.deployment._release_images()),
            "topology": {
                "pd_count": self.deployment.topology.pd_count,
                "tikv_count": self.deployment.topology.tikv_count,
                "tidb_count": self.deployment.topology.tidb_count,
                "tiflash_count": self.deployment.topology.tiflash_count,
            },
            "config_digests": {
                "pd.toml": self._sha256_file(os.path.join(config_dir, "config", "pd.toml")),
                "tikv.toml": self._sha256_file(tikv_config_path),
            },
        }


    def _configure_image_group(self) -> None:
        config_dir = os.path.dirname(self.deployment.compose_template)
        self.image_group_tikv_config_path = os.path.join(self.deployment.runtime_dir, "tikv-image-group.toml")
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
            for service in (*self.deployment.COMPONENTS["pd"], *self.deployment.COMPONENTS["tikv"])
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
                f"TiDB image group is not configured: run_id={self.deployment.run_id!r}, snapshot={snapshot_name!r}"
            )
        if snapshot_name != self.image_group_name:
            raise RuntimeError(
                f"TiDB image group identity mismatch: run_id={self.deployment.run_id!r}, "
                f"expected={self.image_group_name!r}, actual={snapshot_name!r}"
            )
        if not self.image_group_metadata_path.is_file():
            return False
        actual = json.loads(self.image_group_metadata_path.read_text(encoding="utf-8"))
        if actual != self.image_group_metadata:
            raise RuntimeError(
                f"TiDB image group metadata mismatch: run_id={self.deployment.run_id!r}, "
                f"snapshot={snapshot_name!r}, expected={self.image_group_metadata!r}, actual={actual!r}"
            )
        missing = [
            image
            for image in self.image_group_images.values()
            if subprocess.run(
                ["docker", "image", "inspect", image],
                capture_output=True,
                env=self.deployment._env,
            ).returncode != 0
        ]
        if missing:
            raise RuntimeError(
                f"TiDB image group is incomplete: run_id={self.deployment.run_id!r}, "
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
                f"Cannot select missing TiDB image group: run_id={self.deployment.run_id!r}, "
                f"snapshot={snapshot_name!r}, base_snapshot={base_snapshot_name!r}"
            )
        self.image_group_selected = True
        self.image_group_reused = True
        self.deployment._render_runtime_files()


    def _acquire_image_group_lock(self) -> None:
        if not self.image_group_enabled:
            return
        if self._image_group_lock is not None:
            raise RuntimeError(f"TiDB image group lock is already held: run_id={self.deployment.run_id!r}")
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
                f"TiDB image group is not configured: run_id={self.deployment.run_id!r}, snapshot={snapshot_name!r}"
            )
        self._acquire_image_group_lock()
        try:
            if self._validate_image_group(snapshot_name):
                raise RuntimeError(
                    f"TiDB image group already exists: run_id={self.deployment.run_id!r}, snapshot={snapshot_name!r}"
                )
            database_services = [
                *self.deployment.COMPONENTS["tidb"],
                *self.deployment.COMPONENTS["tikv"],
                *self.deployment.COMPONENTS["pd"],
            ]
            self.deployment._run(
                self.deployment._compose + ["stop", "--timeout", "120", *database_services],
                "image-group",
            )
            for service in (*self.deployment.COMPONENTS["pd"], *self.deployment.COMPONENTS["tikv"]):
                container_id = self.deployment._service_container_id(service)
                image = self.image_group_images[service]
                self.deployment._run(
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
            self.deployment._render_runtime_files()
            self.deployment._container_ids.clear()
            self.deployment._start_database_services()
            print(
                f"[Deployment] TiDB image group saved: run_id={self.deployment.run_id!r}, "
                f"snapshot={self.image_group_name!r}"
            )
        finally:
            self.release_image_group_lock()


    def _persistent_metadata_path(self) -> Path:
        if self._persistent_baseline_dir is None:
            raise RuntimeError(f"TiDB persistent storage is not configured: run_id={self.deployment.run_id!r}")
        return self._persistent_baseline_dir / "metadata.json"


    def _persistent_metadata(self) -> dict[str, object]:
        if self.deployment.release is None:
            raise RuntimeError(f"TiDB release is not configured: run_id={self.deployment.run_id!r}")
        return {
            "version": 2,
            "storage_key": self.storage_key,
            "release": {
                "pd_image": self.deployment.release.pd_image,
                "tikv_image": self.deployment.release.tikv_image,
                "tidb_image": self.deployment.release.tidb_image,
            },
            "topology": {
                "pd": self.deployment.topology.pd_count,
                "tikv": self.deployment.topology.tikv_count,
                "tidb": self.deployment.topology.tidb_count,
            },
        }


    def _validate_persistent_metadata(self) -> None:
        metadata_path = self._persistent_metadata_path()
        if not metadata_path.is_file():
            raise RuntimeError(
                f"TiDB persistent baseline is incomplete: run_id={self.deployment.run_id!r}, "
                f"storage_key={self.storage_key!r}, missing={str(metadata_path)!r}"
            )
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        expected = self._persistent_metadata()
        if metadata != expected:
            raise PersistentBaselineIdentityMismatch(
                f"TiDB persistent baseline identity mismatch: run_id={self.deployment.run_id!r}, "
                f"storage_key={self.storage_key!r}, expected={expected!r}, actual={metadata!r}"
            )
        for service in (*self.deployment.COMPONENTS["pd"], *self.deployment.COMPONENTS["tikv"]):
            path = self._persistent_baseline_dir / service
            if not path.is_dir():
                raise RuntimeError(
                    f"TiDB persistent baseline is incomplete: run_id={self.deployment.run_id!r}, "
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
                f"TiDB persistent baseline is partially present: run_id={self.deployment.run_id!r}, "
                f"storage_key={self.storage_key!r}, baseline_exists={baseline_exists}, "
                f"metadata_exists={metadata_exists}"
            )
        if baseline_exists:
            try:
                self._validate_persistent_metadata()
            except PersistentBaselineIdentityMismatch as error:
                print(
                    f"[Deployment] TiDB persistent baseline identity mismatch; rebuilding from scratch: "
                    f"run_id={self.deployment.run_id!r}, storage_key={self.storage_key!r}, error={error!r}"
                )
                shutil.rmtree(self._persistent_baseline_dir)
                baseline_exists = False
            else:
                if self._persistent_run_dir.exists():
                    shutil.rmtree(self._persistent_run_dir)
                self._persistent_run_dir.mkdir(parents=True)
                for service in (*self.deployment.COMPONENTS["pd"], *self.deployment.COMPONENTS["tikv"]):
                    shutil.copytree(
                        self._persistent_baseline_dir / service,
                        self._persistent_run_dir / service,
                    )
                self.persistent_state_reused = True
                self.release_persistence_lock()
                print(
                    f"[Deployment] Reusing TiDB persistent baseline: storage_key={self.storage_key!r}, "
                    f"run_id={self.deployment.run_id!r}"
                )
                return
        if self._persistent_run_dir.exists():
            shutil.rmtree(self._persistent_run_dir)
        self._persistent_run_dir.mkdir(parents=True)
        for service in (*self.deployment.COMPONENTS["pd"], *self.deployment.COMPONENTS["tikv"]):
            (self._persistent_run_dir / service).mkdir()
        self._persistent_state_pending = True
        print(
            f"[Deployment] Creating TiDB persistent baseline: storage_key={self.storage_key!r}, "
            f"run_id={self.deployment.run_id!r}"
        )


    def _make_persistent_state_user_accessible(self) -> None:
        if self._persistent_run_dir is None:
            raise RuntimeError(f"TiDB persistent run directory is not configured: run_id={self.deployment.run_id!r}")
        if self.deployment.release is None:
            raise RuntimeError(f"TiDB release is not configured: run_id={self.deployment.run_id!r}")
        self._normalize_host_directory(
            self._persistent_run_dir,
            self.deployment.release.pd_image,
            f"persistent state for storage_key={self.storage_key!r}",
        )


    def _normalize_host_directory(self, path: Path | str, image: str, description: str) -> None:
        command = [
            "docker", "run", "--rm", "--user", "0:0", "--entrypoint", "/bin/sh",
            "-v", f"{path}:/state",
            image,
            "-c", "chmod -R a+rwX /state",
        ]
        result = subprocess.run(command, capture_output=True, text=True, env=self.deployment._env)
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
                f"TiDB persistent baseline lock is not held: run_id={self.deployment.run_id!r}, "
                f"storage_key={self.storage_key!r}"
            )
        self._make_persistent_state_user_accessible()
        self.deployment._run(
            self.deployment._compose + ["stop", "--timeout", "120", *self.deployment.COMPONENTS["tidb"]],
            "persistent-baseline",
        )
        self.deployment._run(
            self.deployment._compose + [
                "stop", "--timeout", "120",
                *self.deployment.COMPONENTS["tikv"], *self.deployment.COMPONENTS["pd"],
            ],
            "persistent-baseline",
        )
        if self._persistent_baseline_dir.exists():
            raise RuntimeError(
                f"TiDB persistent baseline appeared during initialization: run_id={self.deployment.run_id!r}, "
                f"storage_key={self.storage_key!r}"
            )
        self._persistent_baseline_dir.mkdir(parents=True)
        for service in (*self.deployment.COMPONENTS["pd"], *self.deployment.COMPONENTS["tikv"]):
            shutil.copytree(
                self._persistent_run_dir / service,
                self._persistent_baseline_dir / service,
            )
        metadata_path = self._persistent_metadata_path()
        metadata_path.write_text(
            json.dumps(self._persistent_metadata(), ensure_ascii=True, sort_keys=True),
            encoding="utf-8",
        )
        self.deployment._start_database_services()
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


    def _bootstrap_cache_metadata(self) -> dict:
        config_dir = os.path.dirname(self.deployment.compose_template)
        metadata = {
            "cache_version": self.BOOTSTRAP_CACHE_VERSION,
            "release_version": self.deployment.release.version,
            "images": list(self.deployment._release_images()),
            "topology": {
                "pd_count": self.deployment.topology.pd_count,
                "tikv_count": self.deployment.topology.tikv_count,
                "tidb_count": self.deployment.topology.tidb_count,
                "tiflash_count": self.deployment.topology.tiflash_count,
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
        if not self.bootstrap_cache_enabled or self.deployment.topology.deferred_tikv_count > 0:
            mode = "disabled" if not self.bootstrap_cache_enabled else "deferred-topology"
            for node_type, services in (("pd", self.deployment.COMPONENTS["pd"]), ("tikv", self.deployment.COMPONENTS["tikv"])):
                for service in services:
                    destination = os.path.join(self.deployment.runtime_dir, "data", node_type, service)
                    os.makedirs(destination)
                    self.bootstrap_data_paths[(node_type, service)] = destination
            print(
                f"[Deployment] TiDB bootstrap cache: run_id={self.deployment.run_id!r}, mode={mode!r}"
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
                f"TiDB bootstrap cache is incomplete: run_id={self.deployment.run_id!r}, "
                f"cache_path={self.bootstrap_cache_path!r}, marker={marker_path!r}"
            )
        if os.path.isfile(marker_path):
            with open(marker_path, encoding="utf-8") as handle:
                cached_metadata = json.load(handle)
            if cached_metadata != metadata:
                raise RuntimeError(
                    f"TiDB bootstrap cache metadata mismatch: run_id={self.deployment.run_id!r}, "
                    f"cache_path={self.bootstrap_cache_path!r}, expected={metadata!r}, "
                    f"actual={cached_metadata!r}"
                )
            self.bootstrap_cache_used = True

        for node_type, services in (("pd", self.deployment.COMPONENTS["pd"]), ("tikv", self.deployment.COMPONENTS["tikv"])):
            for service in services:
                source = os.path.join(self.bootstrap_cache_path, node_type, service)
                destination = os.path.join(self.deployment.runtime_dir, "data", node_type, service)
                os.makedirs(destination)
                if self.bootstrap_cache_used:
                    self._copy_tree(source, destination)
                self.bootstrap_data_paths[(node_type, service)] = destination
        print(
            f"[Deployment] TiDB bootstrap cache: run_id={self.deployment.run_id!r}, "
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
        container_id = self.deployment._service_container_id(service)
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
                f"TiDB bootstrap cache is disabled for this runtime: run_id={self.deployment.run_id!r}"
            )
        if self.bootstrap_cache_used:
            return
        if os.path.exists(self.bootstrap_cache_path):
            raise RuntimeError(
                f"TiDB bootstrap cache appeared during deployment: run_id={self.deployment.run_id!r}, "
                f"cache_path={self.bootstrap_cache_path!r}"
            )
        os.makedirs(self.bootstrap_cache_root, exist_ok=True)
        temporary_cache = tempfile.mkdtemp(
            prefix=f".{self.bootstrap_cache_key}-",
            dir=self.bootstrap_cache_root,
        )
        database_services = [
            *self.deployment.COMPONENTS["tidb"],
            *self.deployment.COMPONENTS["tikv"],
            *self.deployment.COMPONENTS["pd"],
        ]
        self.deployment._run(self.deployment._compose + ["stop", *database_services], "bootstrap-cache")
        self.deployment._container_ids.clear()
        for node_type, services in (("pd", self.deployment.COMPONENTS["pd"]), ("tikv", self.deployment.COMPONENTS["tikv"])):
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
        self.deployment._run(self.deployment._compose + ["start", *self.deployment.COMPONENTS["pd"]], "bootstrap-cache")
        self.deployment._container_ids.clear()
        self.deployment._wait("pd", self.deployment._check_pd, 120)
        self.deployment._start_tikv_services(("start",))
        for index, service in enumerate(self.deployment.COMPONENTS["tidb"]):
            target = f"tidb/{service}"
            self.deployment._run(self.deployment._compose + ["start", service], target)
            self.deployment._container_ids.clear()
            self.deployment._wait_tidb_target(target, self.deployment._tidb_readiness_timeout(index))
        self.deployment._wait(
            "prometheus",
            self.deployment._check_prometheus,
            self.deployment._prometheus_readiness_timeout(),
        )


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
