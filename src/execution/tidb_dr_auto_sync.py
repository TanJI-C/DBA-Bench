"""Scenario-owned TiDB DR Auto-Sync control for K09."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from typing import Any

from src.database.sql import parse_json_object, require_success_payload


class K09FinalStateUnavailable(RuntimeError):
    """A trusted K09 endpoint returned a structured final-state read error."""

    def __init__(self, context: str, response: object):
        self.context = context
        self.response = response
        super().__init__(f"{context} final state is unavailable: response={response!r}")


class TiDBDrAutoSyncControl:
    """Drive the documented v8.1 DR Auto-Sync controls for one disposable run."""

    def __init__(self, env: object, case: object):
        self.env = env
        self.case = case
        self.deployment = env.deployment
        self._original_bundle: list[dict[str, Any]] | None = None
        self._original_placement_rules_enabled = False
        self._transition: dict[str, Any] | None = None
        self._primary_store_ids: tuple[int, ...] = ()
        self._sealed_observation: Mapping[str, object] | None = None
        self._sealed_business_truth: dict[str, object] | None = None

    def install(self) -> None:
        self._original_bundle = self._placement_bundle()
        original_config = self._json_pd_ctl("config", "show", "all")
        replication_config = original_config.get("replication", {})
        if not isinstance(replication_config, Mapping):
            raise TypeError(
                f"K09 PD config has an invalid replication section: config={original_config!r}"
            )
        self._original_placement_rules_enabled = str(
            replication_config.get("enable-placement-rules", "false")
        ).casefold() == "true"
        original_mode = self._original_replication_mode(original_config)
        if original_mode not in {"", "majority"}:
            raise RuntimeError(
                "K09 requires a fresh majority-mode TiDB cluster before installing DR Auto-Sync: "
                f"run_id={self.deployment.run_id!r}, original_mode={original_mode!r}, "
                f"config={original_config!r}"
            )
        self.deployment.pd_ctl_command("config", "placement-rules", "enable")
        self._set_rules(self._autosync_bundle(self.case.primary_zone, self.case.dr_zone))
        self._set_replication_mode(self.case.primary_zone, self.case.dr_zone)
        self._primary_store_ids = self._store_ids_for_zone(self.case.primary_zone)
        if len(self._primary_store_ids) != self.case.primary_store_count:
            raise RuntimeError(
                "K09 primary Store topology is incomplete: "
                f"run_id={self.deployment.run_id!r}, expected={self.case.primary_store_count}, "
                f"store_ids={self._primary_store_ids!r}, stores={self._stores()!r}"
            )

    def activate(self) -> None:
        status = self._replication_status()
        if str(status["mode"]).casefold() != "dr-auto-sync":
            raise RuntimeError(
                "K09 activation found an unexpected replication mode: "
                f"run_id={self.deployment.run_id!r}, status={status!r}"
            )

    def seal_business_truth(self) -> None:
        if self._sealed_business_truth is not None:
            raise RuntimeError(
                "K09 business truth was already sealed: "
                f"run_id={self.deployment.run_id!r}, truth={self._sealed_business_truth!r}"
            )
        self._sealed_business_truth = self._business_truth()

    def prepare_observability(self) -> Mapping[str, object]:
        if self._sealed_business_truth is None:
            raise RuntimeError(
                "K09 observability requires pre-fault business truth: "
                f"run_id={self.deployment.run_id!r}"
            )
        observation = self.snapshot()
        self._sealed_observation = observation
        return {
            "k09_initial_replication": observation["replication"],
            "k09_initial_stores": observation["stores"],
            "k09_initial_regions": observation["regions"],
            "k09_initial_business": self._sealed_business_truth,
        }

    def fence_get(self) -> dict[str, object]:
        routers = self.env.connection_router_statuses()
        services = self.deployment.node_states()
        endpoint_targets = {
            self.case.primary_endpoint,
            self.case.dr_endpoint,
        }
        return {
            "routers": routers,
            "services": {
                target: services[target]
                for target in sorted(services)
                if target in endpoint_targets
            },
        }

    def fence_apply(self, target: str) -> dict[str, object]:
        if target != self.case.primary_endpoint:
            raise ValueError(
                "K09 fence target must be the current primary endpoint: "
                f"target={target!r}, primary_endpoint={self.case.primary_endpoint!r}"
            )
        fence = self.fence_get()
        service = fence["services"][target]
        if service["running"]:
            raise RuntimeError(
                "K09 unplanned fence requires the primary SQL endpoint to be stopped: "
                f"target={target!r}, service={service!r}"
            )
        routers = fence["routers"]
        if any(status["policy"] not in {"round_robin", "least_connections"} for status in routers.values()):
            raise RuntimeError(
                "K09 unplanned fence requires a distributing router policy: "
                f"routers={routers!r}"
            )
        if any(target not in status["draining"] for status in routers.values()):
            updated = self.env.drain_connection_routers(target)
        else:
            updated = routers
        self.env.invalidate_workload_connections()
        return {
            "status": "accepted",
            "target": target,
            "router": updated,
            "services": self.fence_get()["services"],
        }

    def transition(
        self,
        mode: str,
        *,
        failed_store_ids: object = None,
        timeout_seconds: int = 120,
    ) -> dict[str, object]:
        if mode not in {"planned", "unplanned"}:
            raise ValueError(f"K09 transition mode is invalid: mode={mode!r}")
        if self._transition is not None:
            raise RuntimeError(
                "K09 transition was already submitted: "
                f"run_id={self.deployment.run_id!r}, transition={self._transition!r}"
            )
        self._require_fenced_router()
        if mode == "planned":
            if failed_store_ids is not None:
                raise ValueError("K09 planned transition does not accept failed_store_ids")
            self._set_rules(self._autosync_bundle(self.case.dr_zone, self.case.primary_zone))
            self._set_replication_mode(self.case.dr_zone, self.case.primary_zone)
            self._transition = {
                "mode": "planned",
                "status": "accepted",
                "target_primary_zone": self.case.dr_zone,
            }
            return {
                **self._transition,
                "replication": self._replication_status(),
                "placement": self._placement_bundle(),
            }

        ids = self._require_failed_store_ids(failed_store_ids)
        if timeout_seconds < 30 or timeout_seconds > 600:
            raise ValueError(
                f"K09 unsafe recovery timeout is outside 30..600 seconds: timeout_seconds={timeout_seconds}"
            )
        current_stores = {int(store["id"]): store for store in self._stores()}
        up_ids = sorted(
            store_id
            for store_id in ids
            if str(current_stores[store_id]["state_name"]).casefold() in {"up", "serving"}
        )
        if up_ids:
            raise RuntimeError(
                "K09 unsafe recovery received Store IDs that are still connected: "
                f"store_ids={up_ids!r}, stores={self._stores()!r}"
            )
        command_output = self.deployment.pd_ctl_command(
            "unsafe",
            "remove-failed-stores",
            ",".join(str(store_id) for store_id in ids),
            "--timeout",
            str(timeout_seconds),
        )
        self._transition = {
            "mode": "unplanned",
            "status": "accepted",
            "target_primary_zone": self.case.dr_zone,
            "failed_store_ids": list(ids),
            "request_output": command_output,
            "timeout_seconds": timeout_seconds,
        }
        return {
            **self._transition,
            "replication": self._replication_status(),
            "stores": self._stores_payload(),
        }

    def wait(self, mode: str, timeout_seconds: int = 120) -> dict[str, object]:
        if mode not in {"planned", "unplanned"}:
            raise ValueError(f"K09 wait mode is invalid: mode={mode!r}")
        if self._transition is None or self._transition["mode"] != mode:
            raise RuntimeError(
                "K09 wait requires a matching accepted transition: "
                f"run_id={self.deployment.run_id!r}, mode={mode!r}, transition={self._transition!r}"
            )
        if timeout_seconds <= 0 or timeout_seconds > 600:
            raise ValueError(
                f"K09 wait timeout is outside 1..600 seconds: timeout_seconds={timeout_seconds}"
            )
        deadline = time.monotonic() + timeout_seconds
        last = self.snapshot()
        while True:
            if mode == "planned":
                terminal = self._planned_terminal(last)
            else:
                terminal = self._unplanned_terminal(last)
            if terminal:
                self._transition["status"] = "terminal"
                last = self.snapshot()
                return {
                    "status": "terminal",
                    "mode": mode,
                    "transition": dict(self._transition),
                    "snapshot": last,
                }
            if time.monotonic() >= deadline:
                return {
                    "status": "running",
                    "mode": mode,
                    "transition": dict(self._transition),
                    "snapshot": last,
                }
            time.sleep(2.0)
            last = self.snapshot()

    def snapshot(self) -> dict[str, object]:
        recovery = None
        if self._transition is not None and self._transition["mode"] == "unplanned":
            recovery = self.deployment.pd_ctl_command(
                "unsafe", "remove-failed-stores", "show"
            )
        return {
            "replication": self._replication_status(),
            "pd_config": self._json_pd_ctl("config", "show", "all"),
            "placement": self._placement_bundle(),
            "stores": self._stores_payload(),
            "regions": self._region_replication_rows(),
            "fence": self.fence_get(),
            "recovery": recovery,
            "transition": dict(self._transition) if self._transition is not None else None,
        }

    def business_truth(self) -> dict[str, object]:
        return self._business_truth()

    def handoff_receipts(self) -> list[dict[str, object]]:
        rows = self._trusted_rows(
            (
                "SELECT handoff_id, failover_mode, endpoint_name, "
                "acknowledged_marker_count, acknowledged_amount_sum, "
                "acknowledged_crc, fence_generation, created_at "
                f"FROM {self.case.database}.{self.case.handoff_table} "
                "ORDER BY handoff_id"
            ),
            "K09 DR failover handoff receipts",
        )
        result = []
        for row in rows:
            if len(row) != 8:
                raise ValueError(
                    "K09 DR failover handoff receipt has an invalid row shape: "
                    f"run_id={self.deployment.run_id!r}, row={row!r}"
                )
            result.append({
                "handoff_id": int(row[0]),
                "failover_mode": str(row[1]),
                "endpoint_name": str(row[2]),
                "acknowledged_marker_count": int(row[3]),
                "acknowledged_amount_sum": int(row[4]),
                "acknowledged_crc": int(row[5]),
                "fence_generation": int(row[6]),
                "created_at": str(row[7]),
            })
        return result

    def recover(self) -> None:
        if self._original_bundle is None:
            raise RuntimeError(
                f"K09 cannot recover before install: run_id={self.deployment.run_id!r}"
            )
        if self._transition is not None and self._transition["mode"] == "unplanned":
            if self._transition["status"] == "accepted":
                self.wait("unplanned", 600)
            if self._transition["status"] != "terminal":
                raise RuntimeError(
                    "K09 unplanned recovery did not reach terminal state before cleanup: "
                    f"run_id={self.deployment.run_id!r}, transition={self._transition!r}"
                )
        self.deployment.pd_ctl_command_with_json(
            (
                "config",
                "placement-rules",
                "rule-bundle",
                "save",
                "--in=/tmp/aiopsbench-k09-original.json",
            ),
            self._original_bundle,
            container_path="/tmp/aiopsbench-k09-original.json",
        )
        self.deployment.pd_ctl_command("config", "set", "replication-mode", "majority")
        self.deployment.pd_ctl_command(
            "config",
            "placement-rules",
            "enable" if self._original_placement_rules_enabled else "disable",
        )
        self.env.reset_connection_routers()

    def _planned_terminal(self, snapshot: Mapping[str, object]) -> bool:
        replication = snapshot["replication"]
        placement = snapshot["placement"]
        return (
            str(replication["dr-auto-sync"]["state"]).casefold() == "sync"
            and self._bundle_matches(
                placement,
                self._autosync_bundle(self.case.dr_zone, self.case.primary_zone),
            )
            and self._region_replication_terminal(snapshot["regions"])
        )

    def _unplanned_terminal(self, snapshot: Mapping[str, object]) -> bool:
        recovery = str(snapshot["recovery"] or "").casefold()
        if "unsafe recovery failed" in recovery:
            raise RuntimeError(
                "K09 unsafe recovery reached a failed terminal state: "
                f"run_id={self.deployment.run_id!r}, recovery={snapshot['recovery']!r}"
            )
        if "unsafe recovery finished" not in recovery:
            return False
        if not self._bundle_matches(
            snapshot["placement"],
            self._unplanned_bundle(self.case.dr_zone),
        ):
            self._set_rules(self._unplanned_bundle(self.case.dr_zone))
            self._set_replication_mode(self.case.dr_zone, self.case.primary_zone)
            return False
        return all(
            str(store["state_name"]).casefold() == "tombstone"
            for store in snapshot["stores"]
            if int(store["id"]) in self._transition["failed_store_ids"]
        ) and self._region_replication_terminal(snapshot["regions"])

    @staticmethod
    def _region_replication_terminal(regions: object) -> bool:
        if not isinstance(regions, list):
            raise TypeError(f"K09 Region replication evidence is not a list: regions={regions!r}")
        return bool(regions) and all(
            str(row[2]).casefold() in {"integrity_over_label", "simple_majority"}
            for row in regions
        )

    def _require_fenced_router(self) -> None:
        fence = self.fence_get()
        for name, status in fence["routers"].items():
            if self.case.primary_endpoint not in status["draining"]:
                raise RuntimeError(
                    "K09 transition requires the current primary endpoint to be drained: "
                    f"router={name!r}, status={status!r}"
                )
            if status["active_connections"].get(self.case.primary_endpoint, 0) != 0:
                raise RuntimeError(
                    "K09 transition requires zero active connections on the drained primary endpoint: "
                    f"router={name!r}, status={status!r}"
                )

    def _require_failed_store_ids(self, value: object) -> tuple[int, ...]:
        if not isinstance(value, list) or not value or any(isinstance(item, bool) for item in value):
            raise ValueError(
                "K09 unplanned transition requires failed_store_ids as a non-empty integer list: "
                f"value={value!r}"
            )
        ids = tuple(sorted({int(item) for item in value}))
        if len(ids) != len(value) or any(item <= 0 for item in ids):
            raise ValueError(f"K09 failed_store_ids must be unique positive IDs: value={value!r}")
        if ids != self._primary_store_ids:
            raise ValueError(
                "K09 failed_store_ids must exactly match all primary-AZ Stores observed at setup: "
                f"expected={self._primary_store_ids!r}, actual={ids!r}"
            )
        return ids

    def _stores_payload(self) -> list[dict[str, object]]:
        return self._stores()

    def _stores(self) -> list[dict[str, object]]:
        payload = self.deployment.pd_request("GET", "/pd/api/v1/stores")
        stores = payload["stores"]
        if not isinstance(stores, list):
            raise TypeError(f"K09 PD stores response has non-list stores: payload={payload!r}")
        result = [self._store_record(item["store"]) for item in stores]
        if self._transition is not None and self._transition["mode"] == "unplanned":
            observed_ids = {int(store["id"]) for store in result}
            for store_id in self._transition["failed_store_ids"]:
                if int(store_id) in observed_ids:
                    continue
                terminal = self.deployment.pd_request(
                    "GET", f"/pd/api/v1/store/{int(store_id)}"
                )
                result.append(self._store_record(terminal["store"]))
        return sorted(result, key=lambda item: int(item["id"]))

    @staticmethod
    def _store_record(store: Mapping[str, object]) -> dict[str, object]:
        labels = {
            str(label["key"]): str(label["value"])
            for label in store.get("labels", [])
        }
        return {
            "id": int(store["id"]),
            "address": str(store["address"]),
            "state_name": str(store["state_name"]),
            "labels": labels,
            "version": str(store.get("version", "")),
        }

    def _store_ids_for_zone(self, zone: str) -> tuple[int, ...]:
        return tuple(
            int(store["id"])
            for store in self._stores()
            if store["labels"].get(self.case.zone_label) == zone
        )

    def _replication_status(self) -> dict[str, object]:
        return self.deployment.pd_request(
            "GET", "/pd/api/v1/replication_mode/status"
        )

    def _placement_bundle(self) -> list[dict[str, object]]:
        output = self.deployment.exec(
            "pd/pd-0",
            [
                "sh",
                "-ceu",
                (
                    "set -eu; "
                    "/pd-ctl -u http://127.0.0.1:2379 config placement-rules "
                    "rule-bundle load --out=/tmp/aiopsbench-k09-observed.json >/dev/null; "
                    "cat /tmp/aiopsbench-k09-observed.json"
                ),
            ],
        ).strip()
        try:
            payload = json.loads(output)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "K09 placement rule load did not return JSON: "
                f"run_id={self.deployment.run_id!r}, output={output!r}"
            ) from exc
        if not isinstance(payload, list):
            raise TypeError(
                "K09 placement rule bundle must be a JSON array: "
                f"run_id={self.deployment.run_id!r}, payload={payload!r}"
            )
        return payload

    def _region_replication_rows(self) -> list:
        sql = (
            "SELECT DB_NAME, TABLE_NAME, REPLICATIONSTATUS_STATE, COUNT(*) "
            "FROM information_schema.TIKV_REGION_STATUS "
            f"WHERE DB_NAME = '{self.case.database}' AND TABLE_NAME = '{self.case.table}' "
            "GROUP BY DB_NAME, TABLE_NAME, REPLICATIONSTATUS_STATE "
            "ORDER BY REPLICATIONSTATUS_STATE"
        )
        raw = self.env.execute_sql_trusted(sql, target=self.case.dr_endpoint)
        payload = parse_json_object(raw, "K09 Region replication status")
        if payload.get("status") != "success":
            raise K09FinalStateUnavailable("K09 Region replication status", payload)
        rows = payload.get("result")
        if not isinstance(rows, list):
            raise TypeError(
                f"K09 Region replication status returned invalid rows: response={payload!r}"
            )
        return rows

    def _business_truth(self) -> dict[str, object]:
        all_sql = (
            "SELECT COUNT(*), COALESCE(SUM(amount_cents), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', marker_id, amount_cents, payload, commit_tso, origin))), 0), "
            "COALESCE(MIN(commit_tso), 0), COALESCE(MAX(commit_tso), 0) "
            f"FROM {self.case.database}.{self.case.table}"
        )
        seed_sql = (
            "SELECT COUNT(*), COALESCE(SUM(amount_cents), 0), "
            "COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', marker_id, amount_cents, payload, commit_tso, origin))), 0) "
            f"FROM {self.case.database}.{self.case.table} WHERE marker_id LIKE 'seed-%'"
        )
        all_rows = self._trusted_rows(all_sql, "K09 business truth")
        seed_rows = self._trusted_rows(seed_sql, "K09 seed business truth")
        if len(all_rows) != 1 or len(all_rows[0]) != 5:
            raise ValueError(f"K09 business truth returned an invalid row: rows={all_rows!r}")
        if len(seed_rows) != 1 or len(seed_rows[0]) != 3:
            raise ValueError(f"K09 seed business truth returned an invalid row: rows={seed_rows!r}")
        return {
            "all": {
                "count": int(all_rows[0][0]),
                "amount_sum": int(all_rows[0][1]),
                "crc": int(all_rows[0][2]),
                "min_commit_tso": int(all_rows[0][3]),
                "max_commit_tso": int(all_rows[0][4]),
            },
            "seed": {
                "count": int(seed_rows[0][0]),
                "amount_sum": int(seed_rows[0][1]),
                "crc": int(seed_rows[0][2]),
            },
            "canary": self._canary_truth(),
        }

    def _canary_truth(self) -> dict[str, int]:
        rows = self._trusted_rows(
            (
                "SELECT endpoint_name, COUNT(*) "
                f"FROM {self.case.database}.{self.case.canary_table} "
                "GROUP BY endpoint_name ORDER BY endpoint_name"
            ),
            "K09 endpoint fence canary truth",
        )
        return {str(row[0]): int(row[1]) for row in rows}

    def _trusted_rows(self, sql: str, context: str) -> list:
        payload = parse_json_object(
            self.env.execute_sql_trusted(sql, target=self.case.dr_endpoint),
            context,
        )
        if payload.get("status") != "success":
            raise K09FinalStateUnavailable(context, payload)
        rows = payload.get("result")
        if not isinstance(rows, list):
            raise TypeError(f"{context} returned invalid rows: response={payload!r}")
        return rows

    def _write_endpoint_canary(self) -> None:
        require_success_payload(
            self.env.execute_sql_trusted(
                (
                    f"INSERT INTO {self.case.database}.{self.case.canary_table} "
                    "(endpoint_name, token) VALUES "
                    f"('{self.case.dr_endpoint}', UUID())"
                ),
                target=self.case.dr_endpoint,
            ),
            "K09 DR endpoint canary write",
        )

    def _set_rules(self, bundle: list[dict[str, object]]) -> None:
        self.deployment.pd_ctl_command_with_json(
            (
                "config",
                "placement-rules",
                "rule-bundle",
                "save",
                "--in=/tmp/aiopsbench-k09-rules.json",
            ),
            bundle,
            container_path="/tmp/aiopsbench-k09-rules.json",
        )

    def _set_replication_mode(self, primary: str, dr: str) -> None:
        commands = (
            ("config", "set", "replication-mode", "dr-auto-sync"),
            ("config", "set", "replication-mode", "dr-auto-sync", "label-key", self.case.zone_label),
            ("config", "set", "replication-mode", "dr-auto-sync", "primary", primary),
            ("config", "set", "replication-mode", "dr-auto-sync", "dr", dr),
            ("config", "set", "replication-mode", "dr-auto-sync", "primary-replicas", str(self.case.primary_store_count)),
            ("config", "set", "replication-mode", "dr-auto-sync", "dr-replicas", str(self.case.dr_voter_count)),
            ("config", "set", "replication-mode", "dr-auto-sync", "wait-store-timeout", self.case.wait_store_timeout),
            ("config", "set", "replication-mode", "dr-auto-sync", "wait-recover-timeout", self.case.wait_recover_timeout),
            ("config", "set", "replication-mode", "dr-auto-sync", "pause-region-split", "true"),
        )
        for command in commands:
            self.deployment.pd_ctl_command(*command)

    def _json_pd_ctl(self, *args: str) -> dict[str, object]:
        output = self.deployment.pd_ctl_command(*args)
        try:
            payload = json.loads(output)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"K09 pd-ctl command did not return JSON: run_id={self.deployment.run_id!r}, args={args!r}, output={output!r}"
            ) from exc
        if not isinstance(payload, dict):
            raise TypeError(
                f"K09 pd-ctl command returned a non-object JSON payload: args={args!r}, payload={payload!r}"
            )
        return payload

    @staticmethod
    def _original_replication_mode(config: Mapping[str, object]) -> str:
        value = config.get("replication-mode", {})
        if isinstance(value, Mapping):
            return str(value.get("replication-mode", "")).casefold()
        return str(value).casefold()

    def _autosync_bundle(self, primary: str, dr: str) -> list[dict[str, object]]:
        return [{
            "group_id": "pd",
            "group_index": 0,
            "group_override": False,
            "rules": [
                self._rule("primary-voters", "voter", self.case.primary_store_count, primary),
                self._rule("dr-voters", "voter", self.case.dr_voter_count, dr),
                self._rule("dr-learner", "learner", self.case.dr_learner_count, dr),
            ],
        }]

    def _unplanned_bundle(self, primary: str) -> list[dict[str, object]]:
        return [{
            "group_id": "pd",
            "group_index": 0,
            "group_override": False,
            "rules": [
                self._rule("recovered-primary-voters", "voter", self.case.total_dr_store_count, primary),
            ],
        }]

    def _rule(self, rule_id: str, role: str, count: int, zone: str) -> dict[str, object]:
        return {
            "group_id": "pd",
            "id": rule_id,
            "start_key": "",
            "end_key": "",
            "role": role,
            "count": count,
            "label_constraints": [{
                "key": self.case.zone_label,
                "op": "in",
                "values": [zone],
            }],
            "location_labels": [self.case.zone_label],
        }

    @staticmethod
    def _bundle_matches(actual: object, expected: object) -> bool:
        def rules(bundle: object) -> list[Mapping[str, object]]:
            if not isinstance(bundle, list):
                raise TypeError(f"K09 placement bundle must be a JSON array: bundle={bundle!r}")
            result = []
            for group in bundle:
                if not isinstance(group, Mapping) or not isinstance(group.get("rules"), list):
                    raise TypeError(f"K09 placement bundle group is invalid: group={group!r}")
                result.extend(group["rules"])
            return result

        actual_rules = rules(actual)
        expected_rules = rules(expected)
        if not actual_rules or not expected_rules:
            raise TypeError(
                f"K09 placement bundle rules must be non-empty lists: actual={actual!r}, expected={expected!r}"
            )
        def signature(rule: Mapping[str, object]) -> tuple:
            constraints = rule["label_constraints"]
            if not isinstance(constraints, list) or len(constraints) != 1:
                raise ValueError(f"K09 placement rule has an invalid label constraint: rule={rule!r}")
            constraint = constraints[0]
            return (
                str(rule["id"]),
                str(rule["role"]),
                int(rule["count"]),
                str(constraint["key"]),
                tuple(str(item) for item in constraint["values"]),
            )
        return sorted(signature(rule) for rule in actual_rules) == sorted(
            signature(rule) for rule in expected_rules
        )
