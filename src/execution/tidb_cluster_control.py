"""TiDB cluster observation and maintenance dispatcher."""

import json
import re
from typing import Any, Dict, Optional


class TiDBClusterControl:
    def __init__(self, env):
        self.env = env

    def execute(self, resource: str, operation: str, target: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Run a resource-neutral observation or maintenance operation."""
        parameters = {} if parameters is None else parameters
        try:
            resource = str(resource).casefold()
            operation = str(operation).casefold()
            result: Any
            handler = self.resource_handlers().get(resource)
            if handler is None:
                raise ValueError(f"Unknown manage_cluster resource: resource={resource!r}")
            result = handler(operation, target, parameters)
            return json.dumps(
                {
                    "status": "success",
                    "resource": resource,
                    "operation": operation,
                    "target": target,
                    "result": result,
                },
                ensure_ascii=False,
                default=str,
            )
        except (ValueError, RuntimeError, OSError, KeyError, json.JSONDecodeError) as exc:
            return json.dumps(
                {
                    "status": "error",
                    "resource": resource,
                    "operation": operation,
                    "target": target,
                    "error": str(exc),
                },
                ensure_ascii=False,
            )

    def _service(self, operation, target, parameters):
        env = self.env
        if operation == "list":
            result = {
                "nodes": env._service_states(),
                "sql_endpoints": sorted(env.deployment.tidb_endpoints),
            }
        elif operation == "get":
            if target is None:
                raise ValueError("manage_cluster service get requires target")
            external = env._replication_endpoint
            if external is not None and target == external["target"]:
                result = {
                    "target": target,
                    "cpu_limit": env._replication_cpu_limit(),
                }
            elif external is not None and target == "downstream/mysql-0":
                result = {
                    "target": target,
                    "cpu_limit": env._replication_downstream_cpu_limit(),
                }
            else:
                states = env._service_states()
                if target == "cluster":
                    result = {"nodes": states}
                else:
                    if target not in states:
                        raise ValueError(
                            f"Unknown service target: target={target!r}, expected={sorted(states)}"
                        )
                    result = {"target": target, "state": states[target]}
        elif operation in {"start", "stop", "restart"}:
            if target is None:
                raise ValueError(
                    f"manage_cluster service {operation} requires target"
                )
            result = env._control_service(operation, target)
        elif operation in {"scale_out", "scale_in", "replace_disk"}:
            if target is None:
                raise ValueError(
                    f"manage_cluster service {operation} requires target"
                )
            method = {
                "scale_out": env.deployment.stores.scale_out_tikv,
                "scale_in": env.deployment.stores.scale_in_tikv,
                "replace_disk": env.deployment.stores.replace_tikv_disk,
            }[operation]
            result = method(target)
        elif operation in {"upgrade", "rollback"}:
            if target is None:
                raise ValueError(
                    f"manage_cluster service {operation} requires target"
                )
            method = (
                env.deployment.rollout.upgrade_component
                if operation == "upgrade"
                else env.deployment.rollout.rollback_component
            )
            result = self._agent_component_change_result(method(target))
        elif operation == "resize":
            if target is None or "cpu_limit" not in parameters:
                raise ValueError(
                    "manage_cluster service resize requires target and parameters.cpu_limit"
                )
            result = env._resize_service(target, float(parameters["cpu_limit"]))
        else:
            raise ValueError(
                f"Unsupported service operation: operation={operation!r}"
            )
        return result

    def _store(self, operation, target, parameters):
        env = self.env
        if operation == "list":
            payload = env.deployment.pd_request("GET", "/pd/api/v1/stores")
            env._remember_pd_stores(payload)
            result = payload
        elif operation == "get":
            if target is None:
                raise ValueError("manage_cluster store get requires target")
            result = env._pd_store(target)
        elif operation == "update":
            if target is None:
                raise ValueError("manage_cluster store update requires target")
            store = env._pd_store(target)
            if "state" in parameters:
                state = str(parameters["state"])
                if state not in {"Offline", "Up"}:
                    raise ValueError(
                        f"Unsupported Store state: target={target!r}, state={state!r}"
                    )
                result = env.deployment.pd_request(
                    "POST",
                    f"/pd/api/v1/store/{store['id']}/state?state={state}",
                )
            elif "rate" in parameters:
                rate = int(parameters["rate"])
                if rate <= 0:
                    raise ValueError(
                        f"Store operator rate must be positive: target={target!r}, rate={rate}"
                    )
                result = env.deployment.pd_request(
                    "POST",
                    f"/pd/api/v1/store/{store['id']}/limit",
                    {"rate": rate},
                )
            else:
                raise ValueError(
                    "manage_cluster store update requires parameters.state or parameters.rate"
                )
        else:
            raise ValueError(
                f"Unsupported store operation: operation={operation!r}"
            )
        return result

    def _region(self, operation, target, parameters):
        env = self.env
        if operation == "list":
            if target is None:
                raise ValueError("manage_cluster region list requires a Store target")
            store = env._pd_store(target)
            result = env.deployment.pd_request(
                "GET", f"/pd/api/v1/regions/store/{store['id']}"
            )
            env._observed_region_ids.setdefault(target, set()).update(
                int(region["id"]) for region in result["regions"]
            )
        elif operation == "get":
            if "region_id" not in parameters:
                raise ValueError("manage_cluster region get requires parameters.region_id")
            region_id = int(parameters["region_id"])
            if region_id <= 0:
                raise ValueError(f"Region ID must be positive: region_id={region_id}")
            result = env.deployment.pd_request(
                "GET", f"/pd/api/v1/region/id/{region_id}"
            )
            if target is not None:
                env._observed_region_ids.setdefault(target, set()).add(region_id)
        elif operation == "remove":
            if target is None or "region_id" not in parameters:
                raise ValueError(
                    "manage_cluster region remove requires target and parameters.region_id"
                )
            region_id = int(parameters["region_id"])
            store = env._pd_store(target)
            if region_id not in env._observed_region_ids.get(target, set()):
                raise ValueError(
                    f"Region must be observed before removal: target={target!r}, region_id={region_id}"
                )
            if store.get("state_name") != "Offline":
                raise ValueError(
                    f"Region removal requires an Offline Store: target={target!r}, store={store!r}"
                )
            region = env.deployment.pd_request(
                "GET", f"/pd/api/v1/region/id/{region_id}"
            )
            peer_store_ids = {int(peer["store_id"]) for peer in region.get("peers") or ()}
            if int(store["id"]) not in peer_store_ids:
                raise ValueError(
                    f"Region target Store is not a peer: target={target!r}, region_id={region_id}"
                )
            if len(peer_store_ids) < 3:
                raise ValueError(
                    f"Region removal requires at least three peers: region_id={region_id}, peers={sorted(peer_store_ids)}"
                )
            result = env.deployment.remove_region_peer(region_id, int(store["id"]))
        else:
            raise ValueError(
                f"Unsupported region operation: operation={operation!r}"
            )
        return result

    def _mvcc_lock(self, operation, target, parameters):
        env = self.env
        if operation not in {"list", "resolve"}:
            raise ValueError(
                f"Unsupported mvcc_lock operation: operation={operation!r}"
            )
        if target is None:
            raise ValueError("manage_cluster mvcc_lock list requires a Region target")
        region_id = env._mvcc_region_id(target)
        if operation == "list":
            if set(parameters) != {"store_targets"}:
                raise ValueError(
                    "mvcc_lock list requires exactly parameters.store_targets; "
                    f"region_id={region_id}, parameters={sorted(parameters)}"
                )
            store_targets = parameters["store_targets"]
            if not isinstance(store_targets, list):
                raise ValueError(
                    "mvcc_lock list requires parameters.store_targets as a list: "
                    f"region_id={region_id}, store_targets={store_targets!r}"
                )
            result = env.deployment.mvcc.mvcc_lock_list(
                region_id,
                store_targets,
                128,
            )
        else:
            result = self._resolve_mvcc_lock(region_id, parameters)
        return result

    def _changefeed_diagnostics(self, operation, target, parameters):
        env = self.env
        if operation == "list":
            if target is None:
                raise ValueError("changefeed_diagnostics list requires a capture target")
            result = env._changefeed_diagnostics("list", target)
        elif operation == "get":
            if target is None or "capture_target" not in parameters:
                raise ValueError(
                    "changefeed_diagnostics get requires target=changefeed_id and parameters.capture_target"
                )
            result = env._changefeed_diagnostics(
                "get",
                str(parameters["capture_target"]),
                target,
            )
        else:
            raise ValueError(
                f"Unsupported changefeed_diagnostics operation: operation={operation!r}"
            )
        return result

    def _gc_safepoint(self, operation, target, parameters):
        env = self.env
        if operation == "list":
            result = env._gc_safepoint_list()
        elif operation == "remove":
            if target is None:
                raise ValueError(
                    "manage_cluster gc_safepoint remove requires target=service_id"
                )
            result = env._gc_safepoint_remove(target, parameters)
        else:
            raise ValueError(
                f"Unsupported gc_safepoint operation: operation={operation!r}"
            )
        return result

    def _gc_status(self, operation, target, parameters):
        env = self.env
        if operation != "get":
            raise ValueError(
                f"Unsupported gc_status operation: operation={operation!r}"
            )
        result = env._mvcc_gc_status()
        # prometheus_raw is a ~270KB metrics dump that would otherwise
        # persist in the agent conversation for the rest of the run;
        # K01 evaluation still reads it via the direct _mvcc_gc_status path.
        result.pop("prometheus_raw")
        return result

    def _storage_maintenance(self, operation, target, parameters):
        env = self.env
        if operation not in {"preflight", "apply"}:
            raise ValueError(
                f"Unsupported storage_maintenance operation: operation={operation!r}"
            )
        if target is None:
            raise ValueError(
                f"manage_cluster storage_maintenance {operation} requires a Region target"
            )
        region_id = env._mvcc_region_id(target)
        if operation == "preflight" and set(parameters) != {"store_targets"}:
            raise ValueError(
                "storage_maintenance preflight requires exactly parameters.store_targets: "
                f"region_id={region_id}, parameters={sorted(parameters)}"
            )
        if operation == "preflight":
            store_targets = parameters["store_targets"]
            if not isinstance(store_targets, list):
                raise ValueError(
                    "storage_maintenance preflight requires parameters.store_targets as a list: "
                    f"region_id={region_id}, store_targets={store_targets!r}"
                )
            result = env.deployment.mvcc.mvcc_recovery_inspect(region_id, store_targets)
            result = dict(result)
            preflight_id = result.pop("inspection_id")
            result["preflight_id"] = preflight_id
        else:
            if set(parameters) != {"preflight_id"}:
                raise ValueError(
                    "storage_maintenance apply requires exactly parameters.preflight_id: "
                    f"region_id={region_id}, parameters={sorted(parameters)}"
                )
            result = self._apply_storage_maintenance(region_id, str(parameters["preflight_id"]))
            result = dict(result)
            preflight_id = result.pop("inspection_id")
            result["preflight_id"] = preflight_id
        return result

    def _unsafe_recovery(self, operation, target, parameters):
        env = self.env
        if target is not None:
            raise ValueError(
                "manage_cluster unsafe_recovery does not accept target: "
                f"target={target!r}"
            )
        if operation == "get":
            result = {
                "state": "observed",
                "output": env.deployment.pd_recovery.online_unsafe_recovery("get"),
            }
        elif operation == "start":
            if set(parameters) != {"failed_store_ids"}:
                raise ValueError(
                    "manage_cluster unsafe_recovery start requires exactly parameters.failed_store_ids: "
                    f"parameters={sorted(parameters)!r}"
                )
            raw_ids = parameters["failed_store_ids"]
            if (
                not isinstance(raw_ids, list)
                or not raw_ids
                or any(isinstance(store_id, bool) for store_id in raw_ids)
            ):
                raise ValueError(
                    "manage_cluster unsafe_recovery start requires a non-empty integer list: "
                    f"failed_store_ids={raw_ids!r}"
                )
            failed_store_ids = tuple(sorted(int(store_id) for store_id in raw_ids))
            if len(failed_store_ids) != len(raw_ids) or any(
                store_id <= 0 for store_id in failed_store_ids
            ):
                raise ValueError(
                    "manage_cluster unsafe_recovery failed_store_ids must be unique positive integers: "
                    f"failed_store_ids={raw_ids!r}"
                )
            result = env.deployment.pd_recovery.online_unsafe_recovery(
                "start",
                failed_store_ids,
            )
        else:
            raise ValueError(
                f"Unsupported unsafe_recovery operation: operation={operation!r}"
            )
        return result

    def _pd_identity(self, operation, target, parameters):
        env = self.env
        if operation != "get":
            raise ValueError(
                f"Unsupported pd_identity operation: operation={operation!r}"
            )
        result = env.deployment.pd_recovery.pd_identity_observation()
        return result

    def _pd_recovery(self, operation, target, parameters):
        env = self.env
        if operation == "inspect":
            view = parameters.get("view", "current")
            if not isinstance(view, str):
                raise ValueError(
                    "manage_cluster pd_recovery inspect view must be a string: "
                    f"view={view!r}"
                )
            phase = parameters.get("phase")
            if phase is not None and not isinstance(phase, str):
                raise ValueError(
                    "manage_cluster pd_recovery inspect phase must be a string: "
                    f"phase={phase!r}"
                )
            record_id = parameters.get("record_id")
            if record_id is not None and not isinstance(record_id, str):
                raise ValueError(
                    "manage_cluster pd_recovery inspect record_id must be a string: "
                    f"record_id={record_id!r}"
                )
            result = env.deployment.pd_recovery.pd_recovery_inspection(view, phase, target, record_id)
        elif operation == "execute":
            if target is None:
                raise ValueError("manage_cluster pd_recovery execute requires a PD target")
            if not env._clock_status_observed:
                raise RuntimeError(
                    "manage_cluster pd_recovery execute requires a successful clock_status/list observation: "
                    f"target={target!r}"
                )
            required = {"cluster_id", "alloc_id", "recovery_branch", "record_id"}
            if set(parameters) != required:
                raise ValueError(
                    "manage_cluster pd_recovery execute requires exactly the evidence-bound parameters: "
                    f"target={target!r}, expected={sorted(required)!r}, parameters={sorted(parameters)!r}"
                )
            result = env.deployment.pd_recovery.execute_pd_recovery(
                target,
                int(parameters["cluster_id"]),
                int(parameters["alloc_id"]),
                parameters["recovery_branch"],
                parameters["record_id"],
            )
        else:
            raise ValueError(
                f"Unsupported pd_recovery operation: operation={operation!r}"
            )
        return result

    def _clock_status(self, operation, target, parameters):
        env = self.env
        if operation != "list":
            raise ValueError(
                f"Unsupported clock_status operation: operation={operation!r}"
            )
        result = env.deployment.clock_status_observation()
        env._clock_status_observed = True
        return result



    def _operator(self, operation, target, parameters):
        env = self.env
        if operation not in {"list", "get"}:
            raise ValueError(
                f"Unsupported operator operation: operation={operation!r}"
            )
        result = env.deployment.pd_request("GET", "/pd/api/v1/operators")
        return result

    def _scheduler(self, operation, target, parameters):
        env = self.env
        if operation in {"list", "get"}:
            result = env.deployment.pd_request("GET", "/pd/api/v1/schedulers")
        elif operation == "remove":
            scheduler_type = str(parameters.get("type", ""))
            store_id = parameters.get("store_id")
            if target and store_id is None:
                match = re.fullmatch(
                    r"(evict-leader-scheduler)[/-]([0-9]+)", target
                )
                if match:
                    scheduler_type, store_id = match.group(1), int(match.group(2))
            if scheduler_type != "evict-leader-scheduler" or store_id is None:
                raise ValueError(
                    "scheduler remove requires the observed scheduler type and store_id"
                )
            leader = env.deployment.pd_request("GET", "/pd/api/v1/leader")
            result = env.deployment.exec(
                f"pd/{leader['name']}",
                [
                    "curl", "-fsS", "-X", "DELETE",
                    "http://127.0.0.1:2379/pd/api/v1/scheduler-config/"
                    f"evict-leader-scheduler/delete/{int(store_id)}",
                ],
            )
        else:
            raise ValueError(
                f"Unsupported scheduler operation: operation={operation!r}"
            )
        return result

    def _config(self, operation, target, parameters):
        env = self.env
        config_target = target or "pd"
        if operation == "get":
            if config_target == "pd":
                result = env.deployment.pd_request("GET", "/pd/api/v1/config")
            elif config_target.startswith("tikv/"):
                result = env._read_tikv_runtime_config(config_target)
            else:
                raise ValueError(
                    f"Unsupported config target: target={config_target!r}"
                )
        elif operation == "update":
            if config_target == "pd":
                key = parameters.get("key")
                value = parameters.get("value")
                if key is None or value is None:
                    raise ValueError(
                        "PD config update requires parameters.key and parameters.value"
                    )
                if not isinstance(key, str) or not key.startswith("schedule."):
                    raise ValueError(
                        f"PD config updates must target schedule.*: key={key!r}"
                    )
                normalized = str(value).casefold()
                if normalized in {"true", "false"}:
                    parsed_value: object = normalized
                else:
                    try:
                        parsed_value = int(value)
                    except ValueError:
                        parsed_value = str(value)
                result = env.deployment.pd_request(
                    "POST", "/pd/api/v1/config", {key: parsed_value}
                )
            elif config_target.startswith("tikv/"):
                key = parameters.get("key")
                value = parameters.get("value")
                if key != "storage.io-rate-limit.max-bytes-per-sec" or value is None:
                    raise ValueError(
                        "TiKV config update requires key=storage.io-rate-limit.max-bytes-per-sec and value"
                    )
                observed = env.set_tikv_io_rate_limit(config_target, int(value))
                result = {"storage": {"io_rate_limit": observed}}
            else:
                raise ValueError(
                    f"Unsupported config target: target={config_target!r}"
                )
        else:
            raise ValueError(
                f"Unsupported config operation: operation={operation!r}"
            )
        return result

    def _network(self, operation, target, parameters):
        env = self.env
        if target is None:
            raise ValueError("manage_cluster network operation requires target")
        if operation == "get":
            result = env.deployment.network.inspect_pd_network(target)
        elif operation == "update":
            access = parameters.get("access")
            if access != "allow":
                raise ValueError(
                    f"Unsupported network access state: target={target!r}, access={access!r}"
                )
            env.deployment.network.allow_pd_network(target)
            result = env.deployment.network.inspect_pd_network(target)
        else:
            raise ValueError(
                f"Unsupported network operation: operation={operation!r}"
            )
        return result

    def _router(self, operation, target, parameters):
        env = self.env
        if operation == "get":
            result = env.connection_router_statuses()
        elif operation == "update":
            if target is None or "policy" not in parameters:
                raise ValueError(
                    "router update requires target and parameters.policy"
                )
            result = env.set_connection_router_policy(
                target, str(parameters["policy"])
            )
        elif operation == "drain":
            if target is None:
                raise ValueError("router drain requires a TiDB target")
            result = env.drain_connection_routers(target)
        else:
            raise ValueError(
                f"Unsupported router operation: operation={operation!r}"
            )
        return result

    def _changefeed(self, operation, target, parameters):
        env = self.env
        if target is None:
            raise ValueError("manage_cluster changefeed operation requires target")
        if operation == "list":
            result = env.deployment.changefeed_diagnostics(target)
        elif operation == "get":
            result = env._changefeed_state(target)
        elif operation == "update":
            result = env._update_replication_sink_config(target, parameters)
        elif operation in {"pause", "resume"}:
            result = env._changefeed_lifecycle(operation, target)
        elif operation == "recreate":
            start_ts = int(parameters.get("start_ts", 0))
            result = env._recreate_changefeed(target, start_ts)
        else:
            raise ValueError(
                f"Unsupported changefeed operation: operation={operation!r}"
            )
        return result

    def _job(self, operation, target, parameters):
        env = self.env
        if operation == "get":
            if env._import_controller is not None:
                result = env._agent_import_status(env.import_controller.status())
            else:
                raise RuntimeError(f"No managed external job is configured: run_id={env.run_id!r}")
        elif operation == "check":
            status = env.import_controller.precheck()
            result = {
                "target_rows": status["target_rows"],
                "output_tail": status["output_tail"],
            }
        elif operation == "update":
            required = (
                "region_concurrency", "disk_quota_mb", "store_write_bwlimit_mib"
            )
            missing = [name for name in required if name not in parameters]
            if missing:
                raise ValueError(
                    f"job update is missing parameters: missing={missing!r}"
                )
            status = env.import_controller.apply_budget(
                region_concurrency=parameters["region_concurrency"],
                disk_quota_mb=parameters["disk_quota_mb"],
                store_write_bwlimit_mib=parameters["store_write_bwlimit_mib"],
                job_id=parameters.get("job_id"),
            )
            result = {"state": status["import_state"]}
        elif operation == "wait":
            timeout_seconds = int(parameters.get("timeout_seconds", 120))
            result = env._agent_import_status(
                env.import_controller.wait(timeout_seconds)
            )
        else:
            raise ValueError(
                f"Unsupported job operation: operation={operation!r}"
            )
        return result



    def _resolve_mvcc_lock(self, region_id, parameters):
        env = self.env
        if set(parameters) != {"inspection_id"}:
            raise ValueError(
                "mvcc_lock resolve requires exactly parameters.inspection_id: "
                f"region_id={region_id}, parameters={sorted(parameters)}"
            )
        result = env.deployment.mvcc.mvcc_recovery_execute(
            region_id,
            str(parameters["inspection_id"]),
        )
        return result

    def _apply_storage_maintenance(self, region_id, preflight_id):
        return self.env.deployment.mvcc.mvcc_recovery_execute(region_id, preflight_id)

    @staticmethod
    def _agent_component_change_result(details):
        return {
            "target": details["target"],
            "component": details["component"],
            "from_version": details["from_version"],
            "to_version": details["to_version"],
        }

    def _release(self, operation, target, parameters):
        rollout = self.env.deployment.rollout
        if operation == "get":
            return rollout.upgrade_agent_observation()
        if operation not in {"upgrade", "rollback"}:
            raise ValueError(f"Unsupported release operation: operation={operation!r}")
        if target is None:
            raise ValueError(f"release {operation} requires a component target")
        method = rollout.upgrade_component if operation == "upgrade" else rollout.rollback_component
        return self._agent_component_change_result(method(target))

    def _monitoring(self, operation, target, parameters):
        if operation != "get":
            raise ValueError(f"Unsupported monitoring operation: operation={operation!r}")
        details = self.env.deployment.rollout.verify_monitoring_coverage()
        return {"targets": details["targets"]}

    def resource_handlers(self):
        """Built-in resources; domain controllers extend or override these handlers."""
        return {
            "service": self._service,
            "store": self._store,
            "region": self._region,
            "mvcc_lock": self._mvcc_lock,
            "changefeed_diagnostics": self._changefeed_diagnostics,
            "gc_safepoint": self._gc_safepoint,
            "gc_status": self._gc_status,
            "storage_maintenance": self._storage_maintenance,
            "unsafe_recovery": self._unsafe_recovery,
            "pd_identity": self._pd_identity,
            "pd_recovery": self._pd_recovery,
            "clock_status": self._clock_status,
            "operator": self._operator,
            "scheduler": self._scheduler,
            "config": self._config,
            "network": self._network,
            "router": self._router,
            "changefeed": self._changefeed,
            "job": self._job,
            "release": self._release,
            "monitoring": self._monitoring,
        }
