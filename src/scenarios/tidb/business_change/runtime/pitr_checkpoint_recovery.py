"""PitrCheckpointRecoveryEnv: Case-specific capabilities and mutable run state.

Generic TiDB execution remains in src.execution.environments.tidb.
"""

from src.execution.environments.tidb import TiDBEnv
from src.execution.tidb_cluster_control import TiDBClusterControl


class PitrCheckpointRecoveryControl(TiDBClusterControl):
    def resource_handlers(self):
        return {**super().resource_handlers(), "restore": self._restore}

    def _restore(self, operation, target, parameters):
        env = self.env
        result = env._require_k08_pitr_runtime().restore_operation(
            operation, target, parameters
        )
        return result

class PitrCheckpointRecoveryEnv(TiDBEnv):
    cluster_control_type = PitrCheckpointRecoveryControl

    additional_log_sources = ("br/snapshot", "br/log-backup", "br/restore")

    def __init__(self, *args, **kwargs):
        self._k08_pitr_runtime = None
        self.agent_sql_observers = ()
        super().__init__(*args, **kwargs)

    def configure_k08_pitr_runtime(self, controller: object) -> None:
        if self._k08_pitr_runtime is not None:
            raise RuntimeError(f"TiDB K08 PITR runtime is already configured: run_id={self.run_id!r}")
        self._k08_pitr_runtime = controller
        self.agent_sql_observers = (controller.observe_agent_sql,)

    def owns_k08_pitr_runtime(self, controller: object) -> bool:
        return self._k08_pitr_runtime is controller

    def clear_k08_pitr_runtime(self) -> None:
        if self._k08_pitr_runtime is None:
            raise RuntimeError(f"TiDB K08 PITR runtime is not configured: run_id={self.run_id!r}")
        self._k08_pitr_runtime = None
        self.agent_sql_observers = ()

    def _require_k08_pitr_runtime(self):
        if self._k08_pitr_runtime is None:
            raise RuntimeError(f"TiDB K08 PITR runtime is not configured: run_id={self.run_id!r}")
        return self._k08_pitr_runtime

    def read_additional_log(self, target: str) -> str:
        return self._require_k08_pitr_runtime().read_log(target)
