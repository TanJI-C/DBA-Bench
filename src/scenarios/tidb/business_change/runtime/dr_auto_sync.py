"""DR Auto-Sync environment capability and Agent control."""
from src.execution.environments.tidb import TiDBEnv
from src.execution.tidb_cluster_control import TiDBClusterControl
from .dr_auto_sync_control import TiDBDrAutoSyncControl


class DrAutoSyncClusterControl(TiDBClusterControl):
    def resource_handlers(self):
        return {**super().resource_handlers(), "dr_replication": self._dr_replication}

    def _dr_replication(self, operation, target, parameters):
        env = self.env
        control = env.dr_replication_control()
        if operation == "get":
            result = control.snapshot()
        elif operation == "topology":
            snapshot = control.snapshot()
            result = {
                "pd_leader": env.deployment.current_pd_leader(),
                "stores": snapshot["stores"],
                "placement": snapshot["placement"],
                "regions": snapshot["regions"],
            }
        elif operation == "fence_get":
            result = control.fence_get()
        elif operation == "fence_apply":
            if target is None or parameters:
                raise ValueError(
                    "dr_replication fence_apply requires target and no parameters"
                )
            result = control.fence_apply(target)
        elif operation == "transition":
            if "mode" not in parameters:
                raise ValueError(
                    "dr_replication transition requires parameters.mode"
                )
            if set(parameters) - {"mode", "failed_store_ids"}:
                raise ValueError(
                    "dr_replication transition accepts only mode and failed_store_ids: "
                    f"parameters={sorted(parameters)}"
                )
            result = control.transition(
                str(parameters["mode"]),
                failed_store_ids=parameters.get("failed_store_ids"),
            )
        elif operation == "wait":
            if set(parameters) != {"mode"}:
                raise ValueError(
                    "dr_replication wait requires exactly parameters.mode"
                )
            result = control.wait(
                str(parameters["mode"]),
            )
        else:
            raise ValueError(
                f"Unsupported dr_replication operation: operation={operation!r}"
            )
        return result


class DrAutoSyncEnv(TiDBEnv):
    cluster_control_type = DrAutoSyncClusterControl

    def __init__(self, *args, **kwargs):
        self._dr_auto_sync_control = None
        super().__init__(*args, **kwargs)

    def configure_dr_auto_sync(self, case) -> TiDBDrAutoSyncControl:
        """Register the K09-owned DR Auto-Sync control plane for this Case."""
        if self._dr_auto_sync_control is not None:
            raise RuntimeError(
                f"TiDB DR Auto-Sync control is already configured: run_id={self.run_id!r}"
            )
        self.initialize_connection_routers({
            "k09-business-router": {"initial_target": case.primary_endpoint},
        })
        self._dr_auto_sync_control = TiDBDrAutoSyncControl(self, case)
        return self._dr_auto_sync_control


    def dr_replication_control(self) -> TiDBDrAutoSyncControl:
        if self._dr_auto_sync_control is None:
            raise RuntimeError(
                f"K09 DR Auto-Sync control is not configured: run_id={self.run_id!r}"
            )
        return self._dr_auto_sync_control
