from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil


class TiDBPdRecovery:
    """Pd recovery operations and run state."""

    def __init__(self, deployment):
        self.deployment = deployment
        self._pd_recovery_artifact: dict[str, object] | None = None
        self._pd_recovery_audit: list[dict[str, object]] = []
        self.online_unsafe_recovery_started = False

    ONLINE_UNSAFE_RECOVERY_TIMEOUT_SECONDS = 300


    def pd_identity_observation(self) -> dict[str, object]:
        """Return raw PD identity and topology observations for recovery cases."""
        cluster = self.deployment.pd_request("GET", "/pd/api/v1/cluster")
        cluster_status = self.deployment.pd_request("GET", "/pd/api/v1/cluster/status")
        members = self.deployment.pd_request("GET", "/pd/api/v1/members")
        leader = self.deployment.pd_request("GET", "/pd/api/v1/leader")
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
        if self.deployment.runtime_dir is None or self.deployment.topology is None:
            raise RuntimeError(f"TiDB runtime is not configured for PD recovery: run_id={self.deployment.run_id!r}")
        if self.deployment.snapshots.persistent_storage_enabled or self.deployment.snapshots.image_group_enabled or self.deployment.snapshots.bootstrap_cache_enabled:
            raise RuntimeError(
                "PD metadata-loss cases require isolated, non-cached host data directories: "
                f"run_id={self.deployment.run_id!r}, persistent_storage={self.deployment.snapshots.persistent_storage_enabled}, "
                f"image_group={self.deployment.snapshots.image_group_enabled}, bootstrap_cache={self.deployment.snapshots.bootstrap_cache_enabled}"
            )
        return tuple(
            Path(self.deployment.snapshots.bootstrap_data_paths[("pd", service)])
            for service in self.deployment.COMPONENTS["pd"]
        )


    def capture_pd_recovery_artifact(self) -> dict[str, object]:
        """Seal raw pre-fault PD evidence before the data directories are wiped."""
        if self._pd_recovery_artifact is not None:
            raise RuntimeError(f"PD recovery evidence was already captured: run_id={self.deployment.run_id!r}")
        identity = self.pd_identity_observation()
        stores = self.deployment.pd_request("GET", "/pd/api/v1/stores")
        historical_logs = {}
        for service in self.deployment.COMPONENTS["pd"]:
            target = f"pd/{service}"
            lines = self.deployment.read_logs(target, lines=10000).splitlines()
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
            for service, path in zip(self.deployment.COMPONENTS["pd"], data_paths)
        }
        incident_record_id = f"pd-audit-{self.deployment.run_id[-8:]}-m6"
        partial_record_id = f"pd-audit-{self.deployment.run_id[-8:]}-q4"
        retained_record_id = f"pd-audit-{self.deployment.run_id[-8:]}-b7"
        historical_full_loss_record_id = f"pd-audit-{self.deployment.run_id[-8:]}-h3"
        decoy_record_ids = tuple(
            f"pd-audit-{self.deployment.run_id[-8:]}-{suffix}"
            for suffix in ("a1", "c3", "d8", "e2", "f9")
        )
        post_record_ids = tuple(
            f"pd-audit-{self.deployment.run_id[-8:]}-{suffix}"
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
                for service in self.deployment.COMPONENTS["pd"]
            }

        decoy_specs = (
            (decoy_record_ids[0], set(self.deployment.COMPONENTS["pd"])),
            (decoy_record_ids[1], {"pd-1", "pd-2"}),
            (decoy_record_ids[2], {"pd-0", "pd-2"}),
            (decoy_record_ids[3], {"pd-0", "pd-1"}),
            (decoy_record_ids[4], set(self.deployment.COMPONENTS["pd"])),
        )
        post_specs = (
            (post_record_ids[0], {"pd-0", "pd-1"}),
            (post_record_ids[1], {"pd-0", "pd-2"}),
            (post_record_ids[2], {"pd-1", "pd-2"}),
            (post_record_ids[3], set(self.deployment.COMPONENTS["pd"])),
            (post_record_ids[4], {"pd-0", "pd-1"}),
        )
        record_specs = (
            (partial_record_id, {"pd-1", "pd-2"}, "healthy response", 10),
            *(
                (record_id, retained_services, "PD client endpoint responded", offset)
                for offset, (record_id, retained_services) in enumerate(decoy_specs, start=9)
            ),
            (retained_record_id, set(self.deployment.COMPONENTS["pd"]), "PD client endpoint responded", 4),
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
            for service in self.deployment.COMPONENTS["pd"]
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
            "product_version": self.deployment.release.version,
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
            raise RuntimeError(f"PD recovery evidence must be captured before wipe: run_id={self.deployment.run_id!r}")
        states = self.deployment.node_states()
        running_pd = [
            target
            for target in states
            if target.startswith("pd/") and states[target]["running"]
        ]
        if running_pd:
            raise RuntimeError(
                f"Cannot wipe PD metadata while PD services are running: "
                f"run_id={self.deployment.run_id!r}, running_pd={running_pd!r}"
            )
        data_paths = self._pd_data_paths()
        post_wipe = {}
        for service, path in zip(self.deployment.COMPONENTS["pd"], data_paths):
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
            raise RuntimeError(f"PD recovery artifact is not available: run_id={self.deployment.run_id!r}")
        if view not in {"current", "history"}:
            raise ValueError(
                f"Unsupported PD recovery inspection view: run_id={self.deployment.run_id!r}, view={view!r}, "
                "expected='current' or 'history'"
            )
        pd_targets = tuple(f"pd/{service}" for service in self.deployment.COMPONENTS["pd"])
        if view == "current" and phase is not None:
            raise ValueError(
                f"PD recovery current view does not accept a phase: run_id={self.deployment.run_id!r}, phase={phase!r}"
            )
        if view == "current" and target is not None:
            raise ValueError(
                f"PD recovery current view does not accept a target: run_id={self.deployment.run_id!r}, target={target!r}"
            )
        if view == "current" and record_id is not None:
            raise ValueError(
                f"PD recovery current view does not accept record_id: run_id={self.deployment.run_id!r}, record_id={record_id!r}"
            )
        if view == "history" and phase not in {"maintenance", "identity"}:
            raise ValueError(
                f"PD recovery history view requires phase='maintenance' or 'identity': "
                f"run_id={self.deployment.run_id!r}, phase={phase!r}"
            )
        if view == "history" and target not in pd_targets:
            raise ValueError(
                f"PD recovery history view requires one PD target: run_id={self.deployment.run_id!r}, "
                f"target={target!r}, expected={pd_targets!r}"
            )
        if view == "history" and not isinstance(record_id, str):
            raise ValueError(
                f"PD recovery history view requires record_id from the maintenance index: "
                f"run_id={self.deployment.run_id!r}, record_id={record_id!r}"
            )
        maintenance_index = self._pd_recovery_artifact["maintenance_index"]
        known_record_ids = tuple(item["record_id"] for item in maintenance_index)
        if view == "history" and record_id not in known_record_ids:
            raise ValueError(
                f"Unknown PD recovery history record_id: run_id={self.deployment.run_id!r}, record_id={record_id!r}, "
                f"known_record_ids={known_record_ids!r}"
            )
        binary_version = self.deployment.exec("pd/pd-0", ["/pd-recover", "-V"]).strip()
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
                for service, path in zip(self.deployment.COMPONENTS["pd"], self._pd_data_paths())
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
            raise RuntimeError(f"PD recovery artifact is not available: run_id={self.deployment.run_id!r}")
        return str(self._pd_recovery_artifact["current_fault_record_id"])


    def execute_pd_recovery(
        self,
        target: str,
        cluster_id: int,
        alloc_id: int,
        recovery_branch: str,
        record_id: str,
    ) -> dict[str, object]:
        if target not in self.deployment.NODES or not target.startswith("pd/"):
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
            raise RuntimeError(f"PD recovery artifact is not available: run_id={self.deployment.run_id!r}")
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
            for service in self.deployment.COMPONENTS["pd"]
        }
        after = {
            service: observations[service]["data_inventory"].get("after")
            for service in self.deployment.COMPONENTS["pd"]
        }
        if recovery_branch == "entirely_rebuild":
            invalid_members = {
                service: {"before": before[service], "after": after[service]}
                for service in self.deployment.COMPONENTS["pd"]
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
                for service in self.deployment.COMPONENTS["pd"]
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
        states = self.deployment.node_states()
        running_database = [
            node
            for node in self.deployment.database_nodes
            if node.startswith(("tikv/", "tidb/")) and states[node]["running"]
        ]
        if running_database:
            raise RuntimeError(
                "PD recovery requires TiDB and TiKV services to be stopped: "
                f"target={target!r}, running_database={running_database!r}"
            )
        running_pd = [
            node
            for node in self.deployment.COMPONENTS["pd"]
            if states[f"pd/{node}"]["running"]
        ]
        if len(running_pd) != len(self.deployment.COMPONENTS["pd"]):
            raise RuntimeError(
                "PD recovery requires the rebuilt PD quorum to be running: "
                f"target={target!r}, running_pd={running_pd!r}, expected={self.deployment.COMPONENTS['pd']!r}"
            )
        output = self.deployment.exec(
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


    def online_unsafe_recovery(
        self,
        operation: str,
        failed_store_ids: tuple[int, ...] = (),
    ) -> object:
        """Expose the v8.1 PD Online Unsafe Recovery product operation."""
        if operation == "get":
            return self.deployment._pd_ctl("unsafe", "remove-failed-stores", "show")
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
        stores = self.deployment._pd_stores()
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
        output = self.deployment.exec(
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
