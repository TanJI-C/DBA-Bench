import os
import shutil


class TiDBStores:
    """Stores operations and run state."""

    def __init__(self, deployment):
        self.deployment = deployment
        self._maintenance_audit: list[dict[str, object]] = []

    def _tikv_target(self, target: str) -> str:
        if target not in self.deployment.NODES or not target.startswith("tikv/"):
            raise ValueError(
                f"TiKV maintenance target must be a TiKV node: target={target!r}, "
                f"expected={[node for node in self.deployment.NODES if node.startswith('tikv/')]}"
            )
        return self.deployment.NODES[target]


    def _store_for_target(self, target: str) -> dict[str, object]:
        service = self._tikv_target(target)
        expected_address = f"{service}:20160"
        matches = [
            item
            for item in self.deployment._pd_stores()
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

        self.deployment._wait(target, check, timeout)
        return observed


    def _record_maintenance(self, event: str, **details: object) -> None:
        self._maintenance_audit.append({"event": event, **details})


    def maintenance_observation(self) -> dict[str, object]:
        return {
            "stores": self.deployment._pd_stores(),
            "operators": self.deployment._pd_ctl("operator", "show"),
            "audit": [dict(item) for item in self._maintenance_audit],
        }


    def scale_out_tikv(self, target: str) -> dict[str, object]:
        service = self._tikv_target(target)
        if any(
            item["store"]["address"] == f"{service}:20160"
            for item in self.deployment._pd_stores()
        ):
            raise RuntimeError(
                f"TiKV scale-out target already has a PD store: target={target!r}, service={service!r}"
            )
        state = self.deployment.node_states()[target]
        if state["running"]:
            raise RuntimeError(
                f"TiKV scale-out target container must be stopped before scale-out: "
                f"target={target!r}, state={state!r}"
            )
        self.deployment.start_component(target)
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
        self.deployment._pd_ctl("store", "delete", str(store_id))
        tombstone = self._wait_store_state(target, "Tombstone")
        self.deployment.stop_component(target)
        self.deployment._run(self.deployment._compose + ["rm", "--force", service], target)
        self.deployment._pd_ctl("store", "remove-tombstone")
        self.deployment._run(self.deployment._compose + ["create", service], target)
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
        self.deployment._pd_ctl("store", "delete", str(store_id))
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
            item for item in self.deployment._pd_stores()
            if str(item["store"]["state_name"]) == "Tombstone"
        ]
        if len(tombstones) != 1 or tombstones[0]["store"]["id"] != store["store"]["id"]:
            raise RuntimeError(
                f"TiKV disk replacement requires exactly the requested Tombstone store: "
                f"target={target!r}, target_store={store!r}, tombstones={tombstones!r}"
            )
        old_store_id = store["store"]["id"]
        service = self._tikv_target(target)
        self.deployment.stop_component(target)
        self.deployment._run(self.deployment._compose + ["rm", "--force", service], target)
        self.deployment._pd_ctl("store", "remove-tombstone")
        self.deployment._run(self.deployment._compose + ["create", service], target)
        self.deployment.start_component(target)
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
            if target not in self.deployment.NODES or not target.startswith("tikv/")
        )
        if unknown_targets:
            raise ValueError(
                "TiKV restore targets must be configured TiKV nodes: "
                f"targets={targets!r}, unknown_targets={unknown_targets!r}"
            )
        stores = self.deployment._pd_stores()
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
        restore_states = {target: self.deployment._service_state(target) for target in targets}
        for target in targets:
            if not restore_states[target]["missing"]:
                continue
            # 共享宿主机的外部清理可能删掉已退出的 Case 容器：原地重建容器
            # （数据目录仍在，TiKV 以原 Store 身份重新注册），让下方各分支
            # 与等待循环面对真实容器。
            service = self.deployment.NODES[target]
            self.deployment.active_tikv_services.discard(service)
            self.deployment._run(self.deployment._compose + ["create", service], target)
            self.deployment._container_ids.pop(service, None)
        for target in tombstone_targets:
            service = self.deployment.NODES[target]
            if restore_states[target]["running"]:
                self.deployment._control("stop", target)
            self.deployment.active_tikv_services.discard(service)
            self.deployment._run(self.deployment._compose + ["rm", "--force", service], target)
        if tombstone_targets:
            self.deployment._pd_ctl("store", "remove-tombstone")
            for target in tombstone_targets:
                self.deployment._run(self.deployment._compose + ["create", self.deployment.NODES[target]], target)
                self.deployment._container_ids.pop(self.deployment.NODES[target], None)
        removed_targets = tuple(target for target in targets if target not in by_target)
        for target in removed_targets:
            # PD 记录已被删除的 Store：旧容器带着本地数据重启必然被 PD 以
            # StoreTombstone 拒绝。清空数据目录并重建容器，让 TiKV 以全新
            # Store 身份重新注册，由健康副本回补数据。
            service = self.deployment.NODES[target]
            if restore_states[target]["running"]:
                self.deployment._control("stop", target)
            self.deployment.active_tikv_services.discard(service)
            self.deployment._run(self.deployment._compose + ["rm", "--force", service], target)
            data_dir = (
                self.deployment.snapshots._persistent_run_dir / service
                if self.deployment.snapshots.persistent_storage_enabled
                else self.deployment.snapshots.bootstrap_data_paths[("tikv", service)]
            )
            shutil.rmtree(data_dir, ignore_errors=True)
            os.makedirs(data_dir, exist_ok=True)
            self.deployment._run(self.deployment._compose + ["create", service], target)
            self.deployment._container_ids.pop(service, None)
        for target in targets:
            service = self.deployment.NODES[target]
            running = restore_states[target]["running"]
            store = by_target.get(target)
            if not running:
                self.deployment.start_component(target)
                continue
            if store is None or str(store["store"].get("state_name")) != "Up":
                self.deployment.restart_component(target)
                self.deployment.active_tikv_services.add(service)
        self.deployment._container_ids.clear()
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
                    if not self.deployment.node_states()[target]["running"]:
                        self.deployment.start_component(target)
            if last_error is not None:
                raise last_error


    def region_health_observation(self) -> dict[str, object]:
        return {
            "stores": self.deployment._pd_stores(),
            "operators": self.deployment._pd_ctl("operator", "show"),
        }
