import json
import subprocess


class TiDBRollout:
    """Rollout operations and run state."""

    def __init__(self, deployment):
        self.deployment = deployment
        self._component_image_overrides: dict[str, str] = {}
        self._upgrade_audit: list[dict[str, object]] = []

    def _require_upgrade_release(self):
        if self.deployment.upgrade_release is None:
            raise RuntimeError(
                f"TiDB upgrade release is not configured: run_id={self.deployment.run_id!r}, "
                f"current_release={self.deployment.release.version!r}"
            )
        return self.deployment.upgrade_release


    def upgrade_precheck(self) -> dict[str, object]:
        self.deployment._check_pd()
        self.deployment._check_tikv()
        self.deployment._check_tidb()
        operators = self.deployment._pd_ctl("operator", "show")
        return {
            "pd_members": self.deployment.topology.pd_count,
            "tikv_up": self.deployment.topology.tikv_count,
            "tidb_endpoints": len(self.deployment.tidb_endpoints),
            "operators": operators,
            "current_version": self.deployment.release.version,
            "target_version": self._require_upgrade_release().version,
        }


    def wait_for_upgrade_precheck(self) -> dict[str, object]:
        observed: dict[str, object] = {}

        def check() -> None:
            observed.clear()
            observed.update(self.upgrade_precheck())

        self.deployment._wait("upgrade precheck", check, self.deployment.warm_tidb_readiness_timeout_sec)
        return dict(observed)


    def _upgrade_targets(self, node_type: str) -> tuple[str, ...]:
        if node_type not in {"pd", "tikv", "tidb"}:
            raise ValueError(f"TiDB rolling upgrade does not support node_type={node_type!r}")
        return tuple(f"{node_type}/{service}" for service in self.deployment.COMPONENTS[node_type])


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
            env=self.deployment._env,
        ).returncode != 0:
            raise RuntimeError(
                f"TiDB upgrade image is unavailable: run_id={self.deployment.run_id!r}, "
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
                for service in self.deployment.COMPONENTS[required_type]
                if service not in upgraded
            )
            for required_type in required_types
        }
        missing = {node_type: services for node_type, services in missing.items() if services}
        if missing:
            raise RuntimeError(
                f"TiDB rolling upgrade order is invalid: run_id={self.deployment.run_id!r}, "
                f"component={node_type!r}, missing_predecessors={missing!r}, "
                f"upgraded_services={sorted(upgraded)!r}"
            )


    def _wait_upgraded_component(self, target: str) -> None:
        node_type = target.split("/", 1)[0]
        if node_type == "pd":
            self.deployment._wait("rolling upgrade PD", self._check_pd_control_plane, 180)
        elif node_type == "tikv":
            self.deployment._wait("rolling upgrade TiKV", self.deployment._check_tikv, 240)
        elif node_type == "tidb":
            self.deployment._wait_tidb_target(target, self.deployment.tidb_readiness_timeout_sec)
        else:
            raise ValueError(f"Unsupported upgraded component target: target={target!r}")


    def _check_pd_control_plane(self) -> None:
        self.deployment._check_pd()
        self.deployment._pd_stores()


    def _set_tikv_leader_weight(
        self,
        store_id: int,
        leader_weight: object,
        region_weight: object,
    ) -> None:
        self.deployment._pd_ctl(
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
        self.deployment._pd_ctl(
            "scheduler",
            "add",
            "evict-leader-scheduler",
            str(store_id),
        )

        def leaders_evicted() -> None:
            current = self.deployment.stores._store_for_target(target)
            observed = int(current["status"].get("leader_count", 0))
            if observed != 0:
                raise RuntimeError(
                    f"TiKV leader evacuation is incomplete: run_id={self.deployment.run_id!r}, "
                    f"target={target!r}, store_id={store_id!r}, "
                    f"expected_leader_count=0, observed_leader_count={observed}, store={current!r}"
                )

        try:
            self.deployment._wait("TiKV leader transfer", leaders_evicted, 300)
        finally:
            self.deployment._pd_ctl("scheduler", "remove", scheduler_name)
        return leader_count_before


    def upgrade_component(self, target: str) -> dict[str, object]:
        if target not in self.deployment.NODES or target.startswith("monitoring/"):
            raise ValueError(
                f"TiDB rolling upgrade target must be a database node: target={target!r}, "
                f"expected={self.deployment.database_nodes!r}"
            )
        node_type, service = target.split("/", 1)
        self._upgrade_predecessors_ready(node_type)
        if service in self._component_image_overrides:
            raise RuntimeError(
                f"TiDB component was already upgraded: run_id={self.deployment.run_id!r}, target={target!r}, "
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
                store = self.deployment.stores._store_for_target(target)
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
            self.deployment._render_runtime_files()
            self.deployment._run(
                self.deployment._compose + ["up", "--detach", "--no-deps", "--force-recreate", service],
                target,
            )
            self.deployment._container_ids.clear()
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
            "from_version": self.deployment.release.version,
            "to_version": release.version,
            "leader_count_before": leader_count,
            "leader_count_after": leader_count_after,
            "leader_transfer_count": leader_transfer_count,
            "store_id": store_id,
        }
        self._upgrade_audit.append(event)
        return dict(event)


    def rollback_component(self, target: str) -> dict[str, object]:
        if target not in self.deployment.NODES or target.startswith("monitoring/"):
            raise ValueError(f"TiDB rollback target must be a database node: target={target!r}")
        service = self.deployment.NODES[target]
        if service not in self._component_image_overrides:
            raise RuntimeError(
                f"TiDB rollback target is not upgraded: run_id={self.deployment.run_id!r}, target={target!r}"
            )
        upgrades = [item for item in self._upgrade_audit if item["event"] == "component_upgrade"]
        if not upgrades or upgrades[-1]["target"] != target:
            raise RuntimeError(
                f"TiDB rollback must reverse the most recent component: run_id={self.deployment.run_id!r}, "
                f"target={target!r}, last_upgrade={upgrades[-1] if upgrades else None!r}"
            )
        self._component_image_overrides.pop(service)
        self.deployment._render_runtime_files()
        self.deployment._run(
            self.deployment._compose + ["up", "--detach", "--no-deps", "--force-recreate", service],
            target,
        )
        self.deployment._container_ids.clear()
        self._wait_upgraded_component(target)
        release = self._require_upgrade_release()
        event = {
            "event": "component_rollback",
            "target": target,
            "component": target.split("/", 1)[0],
            "from_version": release.version,
            "to_version": self.deployment.release.version,
        }
        self._upgrade_audit.append(event)
        return dict(event)


    def verify_monitoring_coverage(self) -> dict[str, object]:
        self.deployment._wait(
            "monitoring",
            self.deployment._check_prometheus,
            self.deployment._prometheus_readiness_timeout(),
        )
        from urllib.parse import urlencode
        from urllib.request import urlopen

        query = urlencode({"query": "up"})
        with urlopen(
            f"http://127.0.0.1:{self.deployment.prometheus_port}/api/v1/query?{query}", timeout=5
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
            "current_version": self.deployment.release.version,
            "target_version": self.deployment.upgrade_release.version if self.deployment.upgrade_release else None,
        }


    def upgrade_evaluation_state(self) -> dict[str, object]:
        return {
            "audit": [dict(item) for item in self._upgrade_audit],
            "component_images": dict(self._component_image_overrides),
            "current_version": self.deployment.release.version,
            "target_version": self.deployment.upgrade_release.version if self.deployment.upgrade_release else None,
        }
