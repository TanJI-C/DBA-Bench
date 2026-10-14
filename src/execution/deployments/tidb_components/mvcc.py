import ast
import os
import re
import shlex
import subprocess
import uuid

import yaml


from src.execution.deployments.tidb_support import TIKV_STORAGE_MAINTENANCE_PROCEDURE


class TiDBMvcc:
    """Mvcc operations and run state."""

    def __init__(self, deployment):
        self.deployment = deployment
        self._mvcc_inspections: dict[str, dict[str, object]] = {}
        self._mvcc_tool_metadata_cache: dict[str, dict[str, str]] = {}

    _MVCC_DATA_PREFIX_HEX = "7A"


    _MVCC_DATA_MAX_HEX = "7B"


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

        region = self.deployment.pd_request("GET", f"/pd/api/v1/region/id/{region_id}")
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

        stores = self.deployment._pd_stores()
        store_by_target: dict[str, dict[str, object]] = {}
        for item in stores:
            store = item["store"]
            address = str(store["address"])
            service = address.rsplit(":", 1)[0]
            target = f"tikv/{service}"
            if target in self.deployment.NODES:
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
        if target not in self.deployment.NODES or not target.startswith("tikv/"):
            raise ValueError(
                f"MVCC operation requires a TiKV target: target={target!r}, "
                f"expected={[item for item in self.deployment.NODES if item.startswith('tikv/')]!r}"
            )
        return self.deployment.NODES[target]


    def _mvcc_tikv_mounts(self, service: str) -> tuple[str, str, str]:
        if self.deployment.compose_file is None:
            raise RuntimeError(f"TiDB Compose file is not configured: run_id={self.deployment.run_id!r}")
        with open(self.deployment.compose_file, encoding="utf-8") as handle:
            services = yaml.safe_load(handle)["services"]
        node = services[service]
        data_mount = None
        config_mount = None
        image = str(node["image"])
        for volume in node.get("volumes", []):
            parts = str(volume).split(":")
            if len(parts) < 2:
                raise ValueError(
                    f"TiKV Compose volume is not a host bind mount: run_id={self.deployment.run_id!r}, "
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
                f"run_id={self.deployment.run_id!r}, service={service!r}, volumes={node.get('volumes')!r}"
            )
        if not os.path.isdir(data_mount) or not os.path.isfile(config_mount):
            raise FileNotFoundError(
                "MVCC helper host mount does not exist: "
                f"run_id={self.deployment.run_id!r}, service={service!r}, data_dir={data_mount!r}, "
                f"config_path={config_mount!r}"
            )
        return data_mount, config_mount, image


    def _mvcc_tool_metadata(self, image: str) -> dict[str, str]:
        cached = self._mvcc_tool_metadata_cache.get(image)
        if cached is not None:
            return dict(cached)
        if "@sha256:" not in image:
            raise RuntimeError(
                f"MVCC helper requires a digest-pinned TiKV image: run_id={self.deployment.run_id!r}, image={image!r}"
            )
        if self.deployment.release is None:
            raise RuntimeError(f"TiDB release is not configured: run_id={self.deployment.run_id!r}")
        expected_version = self.deployment.release.version.removeprefix("v")
        version_command = [
            "docker", "run", "--rm", "--user", "0:0",
            "--entrypoint", "/tikv-ctl", image, "--version",
        ]
        version_result = subprocess.run(
            version_command, capture_output=True, text=True, env=self.deployment._env
        )
        if version_result.returncode != 0:
            raise RuntimeError(
                "TiKV trusted tool version command failed: "
                f"run_id={self.deployment.run_id!r}, image={image!r}, command={shlex.join(version_command)!r}, "
                f"exit_code={version_result.returncode}, stdout={version_result.stdout.strip()!r}, "
                f"stderr={version_result.stderr.strip()!r}"
            )
        version_match = re.search(r"Release Version:\s*([0-9][^\s]*)", version_result.stdout)
        commit_match = re.search(r"Git Commit Hash:\s*([0-9a-f]+)", version_result.stdout)
        if version_match is None or commit_match is None:
            raise RuntimeError(
                "TiKV trusted tool version output is incomplete: "
                f"run_id={self.deployment.run_id!r}, image={image!r}, stdout={version_result.stdout.strip()!r}"
            )
        observed_version = version_match.group(1)
        if observed_version != expected_version:
            raise RuntimeError(
                "TiKV trusted tool version mismatch: "
                f"run_id={self.deployment.run_id!r}, image={image!r}, expected_version={expected_version!r}, "
                f"observed_version={observed_version!r}, stdout={version_result.stdout.strip()!r}"
            )
        hash_command = [
            "docker", "run", "--rm", "--user", "0:0",
            "--entrypoint", "/bin/sh", image, "-c", "sha256sum /tikv-ctl",
        ]
        hash_result = subprocess.run(hash_command, capture_output=True, text=True, env=self.deployment._env)
        if hash_result.returncode != 0:
            raise RuntimeError(
                "TiKV trusted tool hash command failed: "
                f"run_id={self.deployment.run_id!r}, image={image!r}, command={shlex.join(hash_command)!r}, "
                f"exit_code={hash_result.returncode}, stdout={hash_result.stdout.strip()!r}, "
                f"stderr={hash_result.stderr.strip()!r}"
            )
        hash_match = re.fullmatch(r"\s*([0-9a-f]{64})\s+/tikv-ctl\s*", hash_result.stdout)
        if hash_match is None:
            raise RuntimeError(
                "TiKV trusted tool hash output is invalid: "
                f"run_id={self.deployment.run_id!r}, image={image!r}, stdout={hash_result.stdout.strip()!r}"
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
        pd_endpoints = [f"{service_name}:2379" for service_name in self.deployment.COMPONENTS["pd"]]
        command = [
            "docker", "run", "--rm", "--user", "0:0",
            "--network", self.deployment.network_name,
            "-v", f"{data_dir}:/data/tikv:rw",
            "-v", f"{config_path}:/tikv.toml:ro",
            "--entrypoint", metadata["binary_path"], image,
            "--data-dir=/data/tikv", "--config=/tikv.toml",
            *arguments,
        ]
        result = subprocess.run(command, capture_output=True, text=True, env=self.deployment._env)
        if result.returncode != 0:
            raise RuntimeError(
                "TiKV trusted command failed: "
                f"run_id={self.deployment.run_id!r}, release_version={metadata['release_version']!r}, "
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
        self.deployment._run(self.deployment._compose + ["stop", "--timeout", "120", service], target)
        command_error = None
        try:
            return callback(service)
        except Exception as exc:
            command_error = exc
            raise
        finally:
            try:
                self.deployment._run(self.deployment._compose + ["start", service], target)
                self.deployment._container_ids.clear()
                self.deployment._wait(
                    target,
                    lambda service=service: self.deployment._check_tikv_target(service),
                    self.deployment.warm_tidb_readiness_timeout_sec,
                )
                self.deployment.active_tikv_services.add(service)
            except Exception as start_error:
                if command_error is not None:
                    raise RuntimeError(
                        "TiKV offline helper failed during command and restart: "
                        f"run_id={self.deployment.run_id!r}, target={target!r}, operation={operation!r}, "
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
                f"TiKV offline helper requires at least one target: run_id={self.deployment.run_id!r}, operation={operation!r}"
            )
        services = tuple(self._mvcc_compose_service(target) for target in targets)
        if len(set(services)) != len(services):
            raise ValueError(
                "TiKV offline helper received duplicate services: "
                f"run_id={self.deployment.run_id!r}, operation={operation!r}, targets={targets!r}, services={services!r}"
            )
        command_error = None
        try:
            for target, service in zip(targets, services):
                self.deployment._run(self.deployment._compose + ["stop", "--timeout", "120", service], target)
            return callback(services)
        except Exception as exc:
            command_error = exc
            raise
        finally:
            try:
                self.deployment._run(self.deployment._compose + ["start", *services], targets[0])
                self.deployment._container_ids.clear()
                for target, service in zip(targets, services):
                    self.deployment._wait(
                        target,
                        lambda service=service: self.deployment._check_tikv_target(service),
                        self.deployment.warm_tidb_readiness_timeout_sec,
                    )
                    self.deployment.active_tikv_services.add(service)
            except Exception as start_error:
                if command_error is not None:
                    raise RuntimeError(
                        "TiKV multi-target offline helper failed during command and restart: "
                        f"run_id={self.deployment.run_id!r}, targets={targets!r}, operation={operation!r}, "
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
            key_hex = TiDBMvcc._mvcc_decode_memcomparable_key(encoded_key_hex, "lock_key")
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
                        "-p", f"{self.deployment.COMPONENTS['pd'][0]}:2379",
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
                        "-p", f"{self.deployment.COMPONENTS['pd'][0]}:2379",
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
