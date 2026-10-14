import json
from types import SimpleNamespace

from src.execution.environments.tidb import TiDBEnv
from src.scenarios.tidb.business_change.runtime.pitr_checkpoint_recovery import PitrCheckpointRecoveryEnv
from src.scenarios.tidb.health_check.runtime.backup_recoverability import BackupRecoverabilityEnv
from src.scenarios.tidb.system_failure.runtime.br_permission import BrPermissionEnv


def test_br_resource_dispatch_uses_domain_controller_and_preserves_redaction():
    env = object.__new__(BrPermissionEnv)
    env.inspect_br_backup_state = lambda: {
        "last_result": {"status": "success", "secret_key": "must-never-be-exposed"},
        "objects": ["backup-object"],
        "desired_binding": {"grant_id": 7},
    }

    result = json.loads(env.manage_cluster("job", "get"))

    assert result["status"] == "success"
    assert result["result"] == {
        "last_result": {"status": "success"},
        "objects": ["backup-object"],
        "desired_binding": {"grant_id": 7},
    }


def test_pitr_registers_restore_resource_only_in_its_domain_environment():
    generic = object.__new__(TiDBEnv)
    env = object.__new__(PitrCheckpointRecoveryEnv)
    env.run_id = "pitr-extension-test"
    env._k08_pitr_runtime = None
    calls = []
    env.configure_k08_pitr_runtime(SimpleNamespace(
        observe_agent_sql=lambda target, sql: None,
        restore_operation=lambda *args: calls.append(args) or {"checkpoint": "ready"},
    ))

    assert json.loads(generic.manage_cluster("restore", "get"))["status"] == "error"
    result = json.loads(env.manage_cluster("restore", "get", "checkpoint", {"tail": 5}))
    assert result["result"] == {"checkpoint": "ready"}
    assert calls == [("get", "checkpoint", {"tail": 5})]
    env.clear_k08_pitr_runtime()
    assert env.agent_sql_observers == ()


def test_backup_tools_are_owned_by_the_backup_environment():
    generic = object.__new__(TiDBEnv)
    backup = object.__new__(BackupRecoverabilityEnv)

    generic_specs = generic._collect_tool_specs()
    backup_specs = backup._collect_tool_specs()

    assert set(BackupRecoverabilityEnv.HC04_RESTORE_TOOLS).isdisjoint(generic_specs)
    assert set(BackupRecoverabilityEnv.HC04_RESTORE_TOOLS) <= backup_specs.keys()
