"""GcMvccRecoveryEnv: Case-specific capabilities and mutable run state.

Generic TiDB execution remains in src.execution.environments.tidb.
"""

from src.execution.environments.tidb import TiDBEnv
from src.execution.tidb_cluster_control import TiDBClusterControl
from typing import Any, Dict


class GcMvccRecoveryControl(TiDBClusterControl):
    def _resolve_mvcc_lock(self, region_id, parameters):
        env = self.env
        if not env.mvcc_recovery_guard_active():
            return super()._resolve_mvcc_lock(region_id, parameters)
        if set(parameters) != {"inspection_id", "key", "lock_type", "start_ts"}:
            raise ValueError(
                "mvcc_lock resolve requires exactly parameters.inspection_id, "
                "key, lock_type, start_ts (key-level recovery; region-level "
                "recovery is unavailable while the Region holds in-flight "
                f"transaction locks): region_id={region_id}, "
                f"parameters={sorted(parameters)}"
            )
        result = env.deployment.mvcc.mvcc_lock_resolve_key(
            region_id,
            str(parameters["inspection_id"]),
            str(parameters["key"]),
            str(parameters["lock_type"]),
            parameters["start_ts"],
        )
        return result

    def _apply_storage_maintenance(self, region_id, preflight_id):
        if self.env.mvcc_recovery_guard_active():
            self.env.deployment.mvcc.mvcc_recovery_apply_interlock(region_id, preflight_id)
        return super()._apply_storage_maintenance(region_id, preflight_id)

class GcMvccRecoveryEnv(TiDBEnv):
    cluster_control_type = GcMvccRecoveryControl

    def __init__(self, *args, **kwargs):
        self._mvcc_recovery_guard = None
        super().__init__(*args, **kwargs)

    def configure_mvcc_recovery_guard(self, guard: Dict[str, Any]) -> None:
        if self._mvcc_recovery_guard is not None:
            raise RuntimeError(
                f"TiDB MVCC recovery guard is already configured: run_id={self.run_id!r}, "
                f"configured={self._mvcc_recovery_guard!r}"
            )
        self._mvcc_recovery_guard = dict(guard)

    def clear_mvcc_recovery_guard(self) -> None:
        if self._mvcc_recovery_guard is None:
            raise RuntimeError(
                f"TiDB MVCC recovery guard is not configured: run_id={self.run_id!r}"
            )
        self._mvcc_recovery_guard = None

    def mvcc_recovery_guard_active(self) -> bool:
        return self._mvcc_recovery_guard is not None
