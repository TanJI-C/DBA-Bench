import os
import sys
from pathlib import Path
from types import SimpleNamespace

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.execution.deployment import PGDockerDeployment


def test_pg_deployment_adds_custom_network_once():
    deployment = PGDockerDeployment(
        container_name="test-custom-network",
        network_name="test-custom-network-net",
    )

    command = deployment._build_docker_run_command()

    assert command.count("--network") == 1
    assert command[command.index("--network") + 1] == "test-custom-network-net"


def test_pg_init_restarts_after_large_import_shutdown_timeout(monkeypatch, tmp_path):
    init_sql = Path(tmp_path) / "init.sql"
    init_sql.write_text("SELECT 1;", encoding="utf-8")
    deployment = PGDockerDeployment(
        container_name="test-init-restart",
        init_sql_path=str(init_sql),
        initialization_timeout_seconds=2,
    )
    sql_ready_checks = iter((False, True, True))
    calls = []
    logs = (
        "running /docker-entrypoint-initdb.d/init.sql\n"
        "pg_ctl: server does not shut down\n"
        "PostgreSQL Database directory appears to contain a database; Skipping initialization\n"
    )

    def fake_run(command, **kwargs):
        calls.append(command)
        if isinstance(command, str):
            return SimpleNamespace(stdout="", stderr="", returncode=0)
        if command[:3] == ["docker", "logs", deployment.container_name]:
            return SimpleNamespace(stdout=logs, stderr="", returncode=0)
        if command[:3] == ["docker", "inspect", "-f"]:
            return SimpleNamespace(stdout="false", stderr="", returncode=0)
        if command[:3] == ["docker", "exec", deployment.container_name]:
            if "pg_isready" in command or "SELECT 1" in command:
                return SimpleNamespace(
                    stdout="1\n" if next(sql_ready_checks) else "",
                    stderr="",
                    returncode=0,
                )
            if "psql" in command:
                return SimpleNamespace(stdout="", stderr="", returncode=0)
            return SimpleNamespace(stdout="", stderr="", returncode=0)
        if command[:3] == ["docker", "start", deployment.container_name]:
            return SimpleNamespace(stdout=deployment.container_name, stderr="", returncode=0)
        if command[:2] == ["docker", "rm"]:
            return SimpleNamespace(stdout="", stderr="", returncode=0)
        if command and command[0] == "docker":
            return SimpleNamespace(stdout="", stderr="", returncode=0)
        return SimpleNamespace(stdout="", stderr="", returncode=0)

    monkeypatch.setattr("src.execution.deployment.subprocess.run", fake_run)
    monkeypatch.setattr("src.execution.deployment.time.sleep", lambda _seconds: None)
    monkeypatch.setattr(
        deployment,
        "_build_docker_run_command",
        lambda for_init=False: ["docker", "run", "init"],
    )

    deployment.initialize_dataset_container()

    assert ["docker", "start", deployment.container_name] in calls



def _record_deploy_commands(monkeypatch, deployment):
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if command[:3] == ["docker", "image", "inspect"]:
            return SimpleNamespace(stdout="", stderr="no such image", returncode=1)
        return SimpleNamespace(stdout="", stderr="", returncode=0)

    monkeypatch.setattr("src.execution.deployment.subprocess.run", fake_run)
    monkeypatch.setattr(deployment, "initialize_dataset_container", lambda: None)
    monkeypatch.setattr(deployment, "_ensure_owned_resources", lambda: None)
    monkeypatch.setattr(deployment, "is_container_running", lambda: False)
    monkeypatch.setattr(deployment, "_build_docker_run_command", lambda for_init=False: ["docker", "run", "main"])
    return calls


def test_pg_deploy_builds_base_image_without_workload_data(monkeypatch):
    deployment = PGDockerDeployment(container_name="test-base-image")
    calls = _record_deploy_commands(monkeypatch, deployment)

    deployment.deploy()

    commit = next(command for command in calls if command[:2] == ["docker", "commit"])
    assert commit == ["docker", "commit", deployment.container_name, deployment.image_name]
    assert ["docker", "run", "main"] in calls


def test_pg_deploy_labels_dataset_image_with_workload_data(monkeypatch, tmp_path):
    deployment = PGDockerDeployment(container_name="test-dataset-image", workload_data_dir=str(tmp_path / "data"))
    calls = _record_deploy_commands(monkeypatch, deployment)
    monkeypatch.setattr(deployment, "_dataset_ready_label", lambda: "ready-123")

    deployment.deploy()

    commit = next(command for command in calls if command[:2] == ["docker", "commit"])
    assert commit == [
        "docker", "commit",
        "--change", "LABEL aiopsbench.dataset_ready=ready-123",
        deployment.container_name,
        deployment.image_name,
    ]

def main():
    print("="*60)
    print("PGDockerDeployment 测试")
    print("="*60)

    deployment = PGDockerDeployment(
        container_name="aiopsbench-pg-test",
        port=15432,
        resources={
            "cpus": 0.5,
            "memory_mb": 512,
            "shm_size": "128m"
        }
    )

    print("\n--- 1. 测试部署 ---")
    deployment.deploy()

    print("\n--- 2. 测试等待就绪 ---")
    if deployment.wait_for_ready(timeout=60):
        print("PostgreSQL 已就绪！")
    else:
        print("PostgreSQL 就绪超时！")
        return

    print("\n--- 3. 测试 is_ready ---")
    print(f"is_ready = {deployment.is_ready()}")

    print("\n--- 4. 测试胖镜像是否存在 ---")
    image_name = deployment.image_name
    result = os.popen(f"docker images -q {image_name}").read().strip()
    print(f"Fat image '{image_name}' exists = {bool(result)}")

    print("\n--- 5. 测试销毁 ---")
    deployment.teardown()

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()
