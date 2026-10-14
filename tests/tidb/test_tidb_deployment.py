from src.execution.deployments.tidb_components.snapshots import TiDBSnapshots
import os
import json
import shutil
import time
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.usefixtures("isolated_host_ports")
import yaml

from src.scenarios.tidb import TidbQueryPerfIndexMergeSelectionFailureScenario
from src.execution.specs import TiDBReplicationRuntime, TiDBTopologySpec
from src.execution.tidb_runtime import MYSQL_8_4, TICDC_V8_1_0, TIDB_V5_4_3, TIDB_V8_1_0, tidb_runtime
from src.execution.deployments.tidb import TiDBDockerDeployment
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.evaluation.safety import _parse_sql, TraceEvent
from src.scenarios.runtime.orchestrator import Orchestrator


class FakeAgent:
    required_tool_profile = None
    use_native_tools = False


def _runtime(
    pd_count: int,
    tikv_count: int,
    tidb_count: int,
    tiflash_count: int = 0,
    bootstrap_cache_enabled: bool = True,
    tikv_config_writable: bool = False,
    tikv_io_rate_limit_strict: bool = False,
    pd_cpu_limit: float = 1.0,
    deferred_tikv_count: int = 0,
    tikv_memory_mb: int = 2048,
    sql_timeout_seconds: int = 35,
    replication=None,
):
    return tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=pd_count,
        tikv_count=tikv_count,
        tidb_count=tidb_count,
        tiflash_count=tiflash_count,
        bootstrap_cache_enabled=bootstrap_cache_enabled,
        tikv_config_writable=tikv_config_writable,
        tikv_io_rate_limit_strict=tikv_io_rate_limit_strict,
        pd_cpu_limit=pd_cpu_limit,
        deferred_tikv_count=deferred_tikv_count,
        tikv_memory_mb=tikv_memory_mb,
        sql_timeout_seconds=sql_timeout_seconds,
        replication=replication,
    )


def test_run_identity_ports_and_targets():
    deployment = TiDBDockerDeployment(run_id="case-17", port_base=4400)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=2, tidb_count=3))

    try:
        assert deployment.project_name == "aiopsbench-case-17"
        assert deployment.tidb_endpoints == {
            "tidb/tidb-0": ("127.0.0.1", 4400),
            "tidb/tidb-1": ("127.0.0.1", 4402),
            "tidb/tidb-2": ("127.0.0.1", 4404),
        }
        assert deployment.prometheus_port == 4406
        assert deployment._services("tikv/tikv-1") == ("tikv-1",)
        assert deployment._services("pd") == ("pd-0",)
        assert deployment.list_database_nodes() == [
            "pd/pd-0",
            "tikv/tikv-0",
            "tikv/tikv-1",
            "tidb/tidb-0",
            "tidb/tidb-1",
            "tidb/tidb-2",
        ]

        with pytest.raises(ValueError, match="Unknown TiDB target"):
            deployment._services("tikv-1")
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_online_unsafe_recovery_accepts_pd_registration_text(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="unsafe-recovery-registration", port_base=4410)
    monkeypatch.setattr(
        deployment,
        "_pd_stores",
        lambda: [
            {"store": {"id": 11, "state_name": "Disconnected"}},
            {"store": {"id": 12, "state_name": "Disconnected"}},
        ],
    )
    monkeypatch.setattr(
        deployment,
        "exec",
        lambda target, command: 'Success! Request has been accepted."',
    )

    result = deployment.pd_recovery.online_unsafe_recovery("start", (11, 12))

    assert result["state"] == "accepted"
    assert result["failed_store_ids"] == [11, 12]
    assert deployment.pd_recovery.online_unsafe_recovery_started is True


def test_case_topology_renders_compose_and_prometheus_targets():
    deployment = TiDBDockerDeployment(run_id="rendered-topology", port_base=4600)
    runtime = _runtime(pd_count=1, tikv_count=2, tidb_count=1)
    deployment.configure_runtime(runtime)

    try:
        with open(deployment.compose_file, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle)
        assert compose["networks"]["default"] == {
            "name": deployment.network_name,
            "external": True,
        }
        assert deployment.network_subnet is None  # Allocated when Docker creates the network.
        assert set(compose["services"]) == {
            "pd-0", "tikv-0", "tikv-1", "tidb-0", "prometheus", "cadvisor",
        }
        assert compose["services"]["pd-0"]["image"] == runtime.release.pd_image
        assert compose["services"]["tikv-0"]["image"] == runtime.release.tikv_image
        assert compose["services"]["tikv-0"]["mem_limit"] == "2048m"
        assert compose["services"]["tikv-0"]["memswap_limit"] == "2048m"
        assert compose["services"]["tidb-0"]["image"] == runtime.release.tidb_image
        assert compose["services"]["pd-0"]["cpus"] == 1.0
        assert compose["services"]["pd-0"]["mem_limit"] == "4g"
        assert compose["services"]["tidb-0"]["mem_limit"] == "1024m"
        assert compose["services"]["tidb-0"]["memswap_limit"] == "1024m"
        assert any(
            volume.endswith("/data/pd")
            for volume in compose["services"]["pd-0"]["volumes"]
        )
        pd_config_volume = next(
            volume for volume in compose["services"]["pd-0"]["volumes"] if volume.endswith(":/pd.toml:ro")
        )
        pd_config_path = pd_config_volume.split(":", 1)[0]
        with open(pd_config_path, encoding="utf-8") as handle:
            pd_config = handle.read()
        assert "lease = 10" in pd_config
        assert 'tick-interval = "1s"' in pd_config
        assert 'election-interval = "30s"' in pd_config
        tidb = compose["services"]["tidb-0"]
        assert "--config=/tidb.toml" in tidb["command"]
        tidb_config_volume = next(
            volume for volume in tidb["volumes"] if volume.endswith(":/tidb.toml:ro")
        )
        tidb_config_path = tidb_config_volume.split(":", 1)[0]
        assert tidb_config_path.endswith("/config/tidb.toml")
        with open(tidb_config_path, encoding="utf-8") as handle:
            assert "pd-server-timeout = 60" in handle.read()
        prometheus_volume = compose["services"]["prometheus"]["volumes"][0]
        prometheus_path = prometheus_volume.split(":", 1)[0]
        assert os.path.isfile(prometheus_path)
        assert compose["services"]["pd-0"]["user"] == f"{os.getuid()}:{os.getgid()}"
        assert compose["services"]["tikv-0"]["user"] == f"{os.getuid()}:{os.getgid()}"
        assert any(volume.endswith(":/data/pd") for volume in compose["services"]["pd-0"]["volumes"])
        assert any(volume.endswith(":/data/tikv") for volume in compose["services"]["tikv-0"]["volumes"])
        with open(prometheus_path, encoding="utf-8") as handle:
            scrape_configs = yaml.safe_load(handle)["scrape_configs"]
        targets = {
            config["job_name"]: config["static_configs"][0]["targets"]
            for config in scrape_configs
        }
        assert targets == {
            "pd": ["pd-0:2379"],
            "tikv": ["tikv-0:20180", "tikv-1:20180"],
            "tidb": ["tidb-0:10080"],
            "cadvisor": ["cadvisor:8080"],
        }
        expected_tikv_volume = f"{deployment.snapshots.bootstrap_data_paths[('tikv', 'tikv-0')]}:/data/tikv"
        assert compose["services"]["tikv-0"]["volumes"][-1] == expected_tikv_volume
        assert compose["services"]["tidb-0"]["command"][0] == "--config=/tidb.toml"
        assert compose["services"]["tidb-0"]["volumes"][0].endswith("/config/tidb.toml:/tidb.toml:ro")
        assert compose["services"]["prometheus"]["mem_limit"] == "2g"
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_worker_cpuset_is_rendered_for_every_tidb_service(monkeypatch):
    monkeypatch.setenv("AIOPS_CPUSET_CPUS", "24-47")
    monkeypatch.setenv("AIOPS_CPUSET_MEMS", "0,1")
    monkeypatch.setenv("AIOPS_CPU_LIMIT", "12")
    monkeypatch.setenv("AIOPS_MEMORY_MB", "21504")
    deployment = TiDBDockerDeployment(run_id="worker-cpuset", port_base=4630)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=2, tidb_count=1))

    try:
        with open(deployment.compose_file, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle)
        assert {service["cpuset"] for service in compose["services"].values()} == {"24-47"}
        assert all("cpuset_mems" not in service for service in compose["services"].values())
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_replication_topology_renders_each_ticdc_capture_with_its_own_port():
    deployment = TiDBDockerDeployment(run_id="two-captures", port_base=4640)
    runtime = _runtime(
        pd_count=1,
        tikv_count=2,
        tidb_count=1,
        replication=TiDBReplicationRuntime(
            ticdc_image=TICDC_V8_1_0,
            downstream_image=MYSQL_8_4,
            ticdc_cpu_limit=1.0,
            ticdc_memory_mb=1024,
            downstream_cpu_limit=0.5,
            downstream_memory_mb=1024,
            ticdc_count=2,
            ticdc_cluster_ids=("default", "k02-abandoned"),
        ),
    )
    try:
        deployment.configure_runtime(runtime)
        with open(deployment.compose_file, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle)

        assert deployment.COMPONENTS["ticdc"] == ("ticdc-0", "ticdc-1")
        assert deployment.NODES["ticdc/ticdc-0"] == "ticdc-0"
        assert deployment.NODES["ticdc/ticdc-1"] == "ticdc-1"
        assert deployment.ticdc_ports == {
            "ticdc/ticdc-0": 4644,
            "ticdc/ticdc-1": 4645,
        }
        assert deployment.ticdc_port == 4644

        for index in range(2):
            service = f"ticdc-{index}"
            target = f"ticdc/{service}"
            node = compose["services"][service]
            assert node["ports"] == [f"{deployment.ticdc_ports[target]}:8300"]
            assert f"--advertise-addr={service}:8300" in node["command"]
            assert "--gc-ttl=86400" in node["command"]
            assert f"--cluster-id={runtime.replication.ticdc_cluster_ids[index]}" in node["command"]
            assert set(node["depends_on"]) == {"pd-0", "tidb-0", "mysql-0"}
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tidb_network_is_created_with_an_explicit_run_subnet(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="network-capacity-contract", port_base=4620)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    calls = []

    def allocate(name, *, env):
        calls.append((name, env))
        return "10.252.42.0/24"

    monkeypatch.setattr("src.execution.deployments.tidb.create_tidb_network", allocate)

    try:
        deployment._ensure_network()
        deployment._ensure_network()
        assert deployment._network_created is True
        assert deployment.network_subnet == "10.252.42.0/24"
        assert calls == [(deployment.network_name, deployment._env)]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tidb_network_identity_conflict_is_not_reused(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="network-identity-conflict", port_base=4630)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(
        "src.execution.docker_network.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="existing-id", stderr=""),
    )

    try:
        with pytest.raises(RuntimeError, match="network identity already exists"):
            deployment._ensure_network()
        assert deployment._network_created is False
        assert deployment.network_subnet is None
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_writable_tikv_config_uses_run_local_rw_copy():
    deployment = TiDBDockerDeployment(run_id="writable-tikv-config", port_base=4610)
    deployment.configure_runtime(
        _runtime(
            pd_count=1,
            tikv_count=1,
            tidb_count=1,
            tikv_config_writable=True,
            tikv_io_rate_limit_strict=True,
        )
    )

    try:
        with open(deployment.compose_file, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle)
        volume = next(
            volume
            for volume in compose["services"]["tikv-0"]["volumes"]
            if volume.endswith(":/tikv-config:rw")
        )
        source = volume.split(":", 1)[0]
        assert source.startswith(deployment.runtime_dir)
        with open(os.path.join(source, "tikv.toml"), encoding="utf-8") as handle:
            config = handle.read()
        assert "[storage.io-rate-limit]" in config
        assert "strict = true" in config
        assert "--config=/tikv-config/tikv.toml" in compose["services"]["tikv-0"]["command"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_case_specific_tikv_memory_is_rendered_and_reserved():
    deployment = TiDBDockerDeployment(run_id="tikv-memory-contract", port_base=4690)
    runtime = tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=2,
        tidb_count=1,
        tikv_memory_mb=4096,
    )
    deployment.configure_runtime(runtime)

    try:
        with open(deployment.compose_file, encoding="utf-8") as handle:
            services = yaml.safe_load(handle)["services"]
        assert services["tikv-0"]["mem_limit"] == "4096m"
        assert services["tikv-1"]["mem_limit"] == "4096m"
        assert services["tikv-0"]["memswap_limit"] == "4096m"
        assert services["tikv-1"]["memswap_limit"] == "4096m"
        assert runtime.resources.container_memory_mb == 17_408
        assert deployment._required_resources()[1] == 17_408 * 1024**2
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_case_specific_tidb_memory_is_rendered_and_reserved():
    deployment = TiDBDockerDeployment(run_id="tidb-memory-contract", port_base=4696)
    runtime = tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=2,
        tidb_memory_mb=4096,
    )
    deployment.configure_runtime(runtime)

    try:
        with open(deployment.compose_file, encoding="utf-8") as handle:
            services = yaml.safe_load(handle)["services"]
        for service in ("tidb-0", "tidb-1"):
            assert services[service]["mem_limit"] == "4096m"
            assert services[service]["memswap_limit"] == "4096m"
        assert runtime.resources.container_memory_mb == 18_432
        assert deployment._required_resources()[1] == 18_432 * 1024**2
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tidb_readiness_waits_for_system_schema_initialization(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="tidb-system-schema-ready", port_base=4700)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    statements = []

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, statement):
            statements.append(statement)

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.close()
            return False

        def cursor(self):
            return Cursor()

        def close(self):
            statements.append("CLOSE")

    try:
        monkeypatch.setattr(deployment, "_service_container_id", lambda service: "tidb-container")
        monkeypatch.setattr(
            deployment,
            "_run",
            lambda command, component: '{"Running":true}' if command[1] == "inspect" else "",
        )
        monkeypatch.setattr("pymysql.connect", lambda **kwargs: Connection())
        deployment._check_tidb_target("tidb/tidb-0")
        assert statements == [
            "SELECT 1",
            "CLOSE",
        ]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tikv_shared_volume_is_mounted_for_pushdown_backup(tmp_path):
    shared_root = tmp_path / "rg03-artifacts"
    deployment = TiDBDockerDeployment(
        run_id="shared-backup-render",
        port_base=4610,
    )
    deployment.configure_runtime(
        tidb_runtime(
            release=TIDB_V8_1_0,
            pd_count=1,
            tikv_count=2,
            tidb_count=1,
            tikv_shared_volume_root=str(shared_root),
        )
    )
    try:
        with open(deployment.compose_file, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle)
        expected = f"{shared_root.resolve()}:/backup"
        assert expected in compose["services"]["tikv-0"]["volumes"]
        assert expected in compose["services"]["tikv-1"]["volumes"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_case_tikv_memory_limit_renders_in_compose():
    deployment = TiDBDockerDeployment(run_id="large-tikv-memory", port_base=4650)
    deployment.configure_runtime(
        _runtime(pd_count=1, tikv_count=2, tidb_count=1, tikv_memory_mb=4096)
    )

    try:
        with open(deployment.compose_file, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle)
        assert compose["services"]["tikv-0"]["mem_limit"] == "4096m"
        assert compose["services"]["tikv-0"]["memswap_limit"] == "4096m"
        assert compose["services"]["pd-0"]["mem_limit"] == "4g"
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_release_contract_renders_pinned_images_and_version_specific_tidb_args():
    deployments = []
    try:
        for release in (TIDB_V8_1_0, TIDB_V5_4_3):
            deployment = TiDBDockerDeployment(
                run_id=f"release-{release.version[1:].replace('.', '-')}",
                port_base=4700,
            )
            deployments.append(deployment)
            runtime = tidb_runtime(
                release=release,
                pd_count=1,
                tikv_count=1,
                tidb_count=1,
            )
            deployment.configure_runtime(runtime)
            with open(deployment.compose_file, encoding="utf-8") as handle:
                services = yaml.safe_load(handle)["services"]
            assert services["pd-0"]["image"] == release.pd_image
            assert services["tikv-0"]["image"] == release.tikv_image
            assert services["tidb-0"]["image"] == release.tidb_image
            command = services["tidb-0"]["command"]
            assert ("--temp-dir=/tmp/tidb" in command) is (release is TIDB_V8_1_0)
    finally:
        for deployment in deployments:
            shutil.rmtree(deployment.runtime_dir)


def test_persistent_topology_mounts_run_specific_pd_and_tikv_directories(tmp_path):
    deployment = TiDBDockerDeployment(
        run_id="persistent-render",
        port_base=4650,
        storage_key="qp07-baseline",
        storage_root=str(tmp_path),
        tidb_readiness_timeout_sec=901,
        warm_tidb_readiness_timeout_sec=301,
    )
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))

    try:
        with open(deployment.compose_file, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle)
        assert f"{tmp_path}/qp07-baseline/runs/persistent-render/pd-0:/data/pd" in compose["services"]["pd-0"]["volumes"]
        assert f"{tmp_path}/qp07-baseline/runs/persistent-render/tikv-0:/data/tikv" in compose["services"]["tikv-0"]["volumes"]
        assert deployment.tidb_readiness_timeout_sec == 901
        assert deployment.warm_tidb_readiness_timeout_sec == 301
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_persistent_baseline_is_saved_then_cloned_into_a_new_run(tmp_path, monkeypatch):
    first = TiDBDockerDeployment(
        run_id="baseline-source",
        port_base=4660,
        storage_key="qp07-baseline",
        storage_root=str(tmp_path),
    )
    first.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    first.snapshots._prepare_persistent_state()
    first._env["DOCKER_ROOT_DIR"] = "/tmp"
    monkeypatch.setattr(first.snapshots, "_make_persistent_state_user_accessible", lambda: None)
    for service in ("pd-0", "tikv-0"):
        (first.snapshots._persistent_run_dir / service / "initialized.marker").write_text(service, encoding="utf-8")
    monkeypatch.setattr(first, "_run", lambda command, component="cluster": "")
    monkeypatch.setattr(first, "_wait", lambda label, check, timeout: None)
    first.snapshots.persist_initial_state()
    first.snapshots.release_persistence_lock()

    metadata = json.loads(
        (tmp_path / "qp07-baseline" / "baseline" / "metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["topology"] == {"pd": 1, "tikv": 1, "tidb": 1}

    second = TiDBDockerDeployment(
        run_id="baseline-consumer",
        port_base=4670,
        storage_key="qp07-baseline",
        storage_root=str(tmp_path),
    )
    second.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    second.snapshots._prepare_persistent_state()
    try:
        assert second.snapshots.persistent_state_reused is True
        assert (second.snapshots._persistent_run_dir / "pd-0" / "initialized.marker").read_text(encoding="utf-8") == "pd-0"
        assert (second.snapshots._persistent_run_dir / "tikv-0" / "initialized.marker").read_text(encoding="utf-8") == "tikv-0"
    finally:
        second.snapshots.release_persistence_lock()
        shutil.rmtree(first.runtime_dir)
        shutil.rmtree(second.runtime_dir)


def test_readiness_timeout_preserves_last_error_and_service_diagnostics(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="readiness-diagnostics")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    clock_calls = {"count": 0}

    def clock():
        clock_calls["count"] += 1
        return 0.0 if clock_calls["count"] < 3 else 2.0

    monkeypatch.setattr("src.execution.deployments.tidb.time.monotonic", clock)
    monkeypatch.setattr("src.execution.deployments.tidb.time.sleep", lambda seconds: None)
    monkeypatch.setattr(deployment, "_assert_stage_running", lambda label: None)
    monkeypatch.setattr(
        deployment,
        "_readiness_diagnostics",
        lambda label: "service='tidb-0', logs_stdout='bootstrap pending'",
    )

    def fail_check():
        raise RuntimeError("PD metadata is still bootstrapping")

    try:
        with pytest.raises(RuntimeError, match="bootstrap pending") as error:
            deployment._wait("tidb/tidb-0", fail_check, 1)
        assert "PD metadata is still bootstrapping" in str(error.value)
        assert "stage='tidb/tidb-0'" in str(error.value)
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_upgrade_precheck_wait_retries_until_cluster_is_ready(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="upgrade-precheck-readiness")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    calls = []
    assert deployment._stage_services("upgrade precheck") == ("pd-0", "tikv-0", "tidb-0")

    def upgrade_precheck():
        calls.append("precheck")
        if len(calls) == 1:
            raise RuntimeError("TiKV store is still converging")
        return {"tikv_up": 1, "current_version": "v6.5.0"}

    real_wait = deployment._wait

    def wait(label, check, timeout):
        assert label == "upgrade precheck"
        assert timeout == deployment.warm_tidb_readiness_timeout_sec
        monkeypatch.setattr("src.execution.deployments.tidb.time.monotonic", lambda: 0.0)
        monkeypatch.setattr("src.execution.deployments.tidb.time.sleep", lambda seconds: None)
        monkeypatch.setattr(deployment, "_assert_stage_running", lambda stage: None)
        real_wait(label, check, timeout)

    monkeypatch.setattr(deployment.rollout, "upgrade_precheck", upgrade_precheck)
    monkeypatch.setattr(deployment, "_wait", wait)
    try:
        assert deployment.rollout.wait_for_upgrade_precheck() == {
            "tikv_up": 1,
            "current_version": "v6.5.0",
        }
        assert calls == ["precheck", "precheck"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tikv_readiness_check_ignores_registered_tiflash_stores(monkeypatch):
    """PD lists TiFlash engines alongside TiKV stores; only :20160 counts.

    Regression: after the tiflash stage registers its store,
    is_ready()/wait_for_ready() must match the Up store service names against
    the full topology, not the TiKV topology alone — otherwise the TiFlash
    node reads as an unexpected TiKV service and readiness never passes.
    """
    deployment = TiDBDockerDeployment(run_id="tikv-check-tiflash-store")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1, tiflash_count=1))
    stores_payload = {
        "stores": [
            {"store": {"address": "tikv-0:20160", "state_name": "Up"}},
            {"store": {
                "address": "tiflash-0:3930",
                "state_name": "Up",
                "labels": [{"key": "engine", "value": "tiflash"}],
            }},
        ],
    }
    monkeypatch.setattr(deployment, "_pd_json", lambda path: stores_payload)
    try:
        deployment._check_tikv()
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tiflash_readiness_stage_guard_targets_rendered_services(monkeypatch):
    """The tiflash stage guard must inspect the rendered tiflash-<n> services.

    Regression: resolving the literal label "tiflash" as a service name makes
    every TiFlash deployment fail with
    "TiDB container not found: component='tiflash'" regardless of the stores'
    real state.
    """
    deployment = TiDBDockerDeployment(run_id="tiflash-stage-guard")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1, tiflash_count=1))
    assert deployment._stage_services("tiflash") == ("tiflash-0",)
    inspected = []
    monkeypatch.setattr(
        deployment,
        "_container_snapshot",
        lambda service: inspected.append(service)
        or {
            "State": {"OOMKilled": False, "Status": "running", "ExitCode": 0},
            "RestartCount": 0,
        },
    )
    try:
        deployment._assert_stage_running("tiflash")
        assert inspected == ["tiflash-0"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_stopped_service_error_includes_recent_service_diagnostics(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="stopped-service-diagnostics")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(
        deployment,
        "_container_snapshot",
        lambda service: {
            "State": {
                "OOMKilled": False,
                "Status": "exited",
                "ExitCode": 1,
            },
            "RestartCount": 0,
        },
    )
    monkeypatch.setattr(
        deployment,
        "_readiness_diagnostics",
        lambda label: "service='tikv-0', logs_stdout='PD connection failed'",
    )

    try:
        with pytest.raises(RuntimeError, match="PD connection failed") as error:
            deployment._assert_stage_running("tikv")
        assert "service='tikv-0'" in str(error.value)
        assert "exit_code=1" in str(error.value)
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_command_error_contains_run_component_and_output(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="failed-run")
    monkeypatch.setattr(
        "src.execution.deployments.tidb.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=7,
            stdout="partial output",
            stderr="compose exploded",
        ),
    )

    with pytest.raises(RuntimeError) as error:
        deployment._run(["docker", "compose", "up"], "tikv-2")

    message = str(error.value)
    assert "run_id='failed-run'" in message
    assert "component='tikv-2'" in message
    assert "returncode=7" in message
    assert "partial output" in message
    assert "compose exploded" in message


def test_wait_store_state_uses_tikv_target_as_readiness_stage(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="store-state-readiness-stage")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=4, tidb_count=1))
    labels = []
    monkeypatch.setattr(deployment.stores, "_store_for_target", lambda target: {
        "store": {"id": 4, "state_name": "Up", "address": "tikv-3:20160"},
        "status": {"leader_count": 0, "region_count": 0},
    })
    monkeypatch.setattr(
        deployment,
        "_wait",
        lambda label, check, timeout: (labels.append((label, timeout)), check()),
    )

    try:
        observed = deployment.stores._wait_store_state("tikv/tikv-3", "Up", timeout=17)
        assert observed["store"]["state_name"] == "Up"
        assert labels == [("tikv/tikv-3", 17)]
        assert deployment._stage_services(labels[0][0]) == ("tikv-3",)
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_group_component_control_runs_services_sequentially(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="sequential-control")
    deployment.configure_runtime(_runtime(pd_count=3, tikv_count=2, tidb_count=1))
    commands = []
    deployment._env["DOCKER_ROOT_DIR"] = "/srv/docker-xfs"
    monkeypatch.setattr(
        deployment,
        "_service_container_id",
        lambda service: f"container-{service}",
    )
    monkeypatch.setattr(deployment, "_run", lambda command, component: commands.append((command, component)) or "")

    try:
        deployment.start_component("pd")
        assert [item[0] for item in commands] == [
            ["docker", "start", "container-pd-0"],
            ["docker", "start", "container-pd-1"],
            ["docker", "start", "container-pd-2"],
        ]
        assert [item[1] for item in commands] == ["pd/pd-0", "pd/pd-1", "pd/pd-2"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_component_control_reloads_container_id_after_stop(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="reload-container-id")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    commands = []
    deployment._env["DOCKER_ROOT_DIR"] = "/srv/docker-xfs"

    def fake_run(command, component):
        commands.append((command, component))
        if command[-4:] == ["ps", "--all", "--quiet", "pd-0"]:
            return "new-pd-container\n"
        return ""

    monkeypatch.setattr(deployment, "_run", fake_run)
    deployment._container_ids["pd-0"] = "old-pd-container"

    try:
        deployment.stop_component("pd")
        deployment.start_component("pd")
        assert commands == [
            ([*deployment._compose, "stop", "pd-0"], "pd/pd-0"),
            ([*deployment._compose, "ps", "--all", "--quiet", "pd-0"], "pd-0"),
            (["docker", "start", "new-pd-container"], "pd/pd-0"),
        ]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_individual_ticdc_stop_allows_graceful_capture_shutdown(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="graceful-ticdc-stop")
    deployment.configure_runtime(
        _runtime(
            pd_count=1,
            tikv_count=1,
            tidb_count=1,
            replication=TiDBReplicationRuntime(
                ticdc_image=TICDC_V8_1_0,
                downstream_image=MYSQL_8_4,
                ticdc_cpu_limit=1.0,
                ticdc_memory_mb=1024,
                downstream_cpu_limit=0.5,
                downstream_memory_mb=1024,
                ticdc_count=2,
            ),
        )
    )
    commands = []
    deployment._env["DOCKER_ROOT_DIR"] = "/srv/docker-xfs"
    monkeypatch.setattr(deployment, "_run", lambda command, component: commands.append((command, component)) or "")

    try:
        deployment.stop_component("ticdc/ticdc-1")
        assert commands == [
            ([*deployment._compose, "stop", "--timeout", "120", "ticdc-1"], "ticdc/ticdc-1"),
        ]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_pd_readiness_requires_members_and_leader_but_not_store_api(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-quorum-readiness")
    deployment.configure_runtime(_runtime(pd_count=3, tikv_count=3, tidb_count=1))
    paths = []
    deployment._env["DOCKER_ROOT_DIR"] = "/srv/docker-xfs"
    monkeypatch.setattr(
        deployment,
        "_service_container_id",
        lambda service: f"container-{service}",
    )
    monkeypatch.setattr(
        deployment,
        "_run",
        lambda command, component: '{"Running":true,"Status":"running",'
        '"ExitCode":0,"OOMKilled":false}',
    )

    def pd_json(path):
        paths.append(path)
        if path.endswith("/members"):
            return {"members": [{"name": "pd-0"}, {"name": "pd-1"}, {"name": "pd-2"}]}
        if path.endswith("/leader"):
            return {"name": "pd-1"}
        raise AssertionError(path)

    monkeypatch.setattr(deployment, "_pd_json", pd_json)

    try:
        deployment._check_pd()
        assert paths == ["/pd/api/v1/members", "/pd/api/v1/leader"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_stable_readiness_requires_consecutive_successes():
    calls = []

    def check():
        calls.append("check")

    stable_check = TiDBDockerDeployment._stable_check(check, required_successes=3)

    with pytest.raises(RuntimeError, match="observed=1"):
        stable_check()
    with pytest.raises(RuntimeError, match="observed=2"):
        stable_check()
    stable_check()

    assert calls == ["check", "check", "check"]


def test_tidb_admin_check_table_is_safe_known_sql_command():
    statements = _parse_sql(
        TraceEvent(
            3,
            "execute_sql",
            {"sql_query": "ADMIN CHECK TABLE test.sf01_business_events"},
            {"status": "success"},
        ),
        dialect="mysql",
    )

    assert len(statements) == 1
    assert statements[0].operation is None
    assert statements[0].parse_error is None
    assert statements[0].targets == frozenset({"test.sf01_business_events"})


def test_tidb_mysql_upsert_is_parsed_for_safety_rules():
    statements = _parse_sql(
        TraceEvent(
            4,
            "execute_sql",
            {
                "sql_query": (
                    "CREATE DATABASE IF NOT EXISTS recovery_verify; "
                    "CREATE TABLE IF NOT EXISTS recovery_verify.pd_recovery_check "
                    "(id INT PRIMARY KEY, marker VARCHAR(64)); "
                    "INSERT INTO recovery_verify.pd_recovery_check VALUES (1, 'pd-recovery-ok') "
                    "ON DUPLICATE KEY UPDATE marker=VALUES(marker); "
                    "SELECT id, marker FROM recovery_verify.pd_recovery_check WHERE id=1;"
                )
            },
            {"status": "success"},
        ),
        dialect="mysql",
    )

    assert [statement.parse_error for statement in statements] == [None, None, None, None]
    assert [statement.operation for statement in statements] == ["CREATE", "CREATE", "INSERT", None]
    assert "recovery_verify.pd_recovery_check" in statements[2].targets


def test_invalid_run_id_is_rejected():
    with pytest.raises(ValueError, match="Invalid TiDB run_id"):
        TiDBDockerDeployment(run_id="Mixed Case")


@pytest.mark.parametrize(
    "topology",
    [
        TiDBTopologySpec(pd_count=1, tikv_count=1, tidb_count=1),
        TiDBTopologySpec(pd_count=3, tikv_count=5, tidb_count=2),
    ],
)
def test_topology_node_counts_are_configurable(topology):
    deployment = TiDBDockerDeployment(run_id=f"topology-{topology.tikv_count}")
    deployment.configure_runtime(
        _runtime(
            pd_count=topology.pd_count,
            tikv_count=topology.tikv_count,
            tidb_count=topology.tidb_count,
        )
    )
    try:
        assert len(deployment.COMPONENTS["pd"]) == topology.pd_count
        assert len(deployment.COMPONENTS["tikv"]) == topology.tikv_count
        assert len(deployment.COMPONENTS["tidb"]) == topology.tidb_count
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_orchestrator_applies_case_topology_before_deploy():
    scenario = TidbQueryPerfIndexMergeSelectionFailureScenario()
    case = scenario.get_case("dual_single_column_index_or_predicate")
    env = TiDBEnv(run_id="case-contract", port_base=4800)
    orchestrator = Orchestrator(env, scenario, case, FakeAgent())

    orchestrator._apply_case_environment_contract()

    try:
        assert env.deployment.topology == case.runtime.topology
        assert env.sql_timeout_seconds == case.runtime.sql_timeout_seconds
        assert len(env.deployment.database_nodes) == 3
    finally:
        shutil.rmtree(env.deployment.runtime_dir)


def test_pd_json_parses_command_output(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-probe")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    commands = []
    try:
        monkeypatch.setattr(deployment, "_service_container_id", lambda service: "pd-container")
        monkeypatch.setattr(
            deployment,
            "_run",
            lambda command, component: commands.append((command, component)) or (
                '{"name": "pd-0"}'
                if command[-1].endswith("/pd/api/v1/leader")
                else '{"members": [{"name": "pd-0"}]}'
            ),
        )

        assert deployment._pd_json("/pd/api/v1/members") == {
            "members": [{"name": "pd-0"}],
        }
        assert commands[0][0][5:7] == ["-T", "5"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_pd_readiness_requires_elected_leader(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-leader")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    responses = {
        "/pd/api/v1/members": {"members": [{"name": "pd-0"}]},
        "/pd/api/v1/leader": {"name": "pd-0"},
    }
    try:
        monkeypatch.setattr(deployment, "_pd_json", lambda path: responses[path])
        deployment._check_pd()

        responses["/pd/api/v1/leader"] = {}
        with pytest.raises(RuntimeError, match="PD has no valid leader"):
            deployment._check_pd()
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_pd_request_keeps_http_error_body_visible(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-error-body")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    commands = []

    try:
        monkeypatch.setattr(deployment, "_service_container_id", lambda service: "pd-container")
        monkeypatch.setattr(deployment, "current_pd_leader", lambda: "pd-0")
        monkeypatch.setattr(
            deployment,
            "_run",
            lambda command, component: commands.append((command, component)) or "{}",
        )

        assert deployment.pd_request("POST", "/pd/api/v1/store/1012/limit", {"rate": 0}) == {}
        assert commands[0][0][5:7] == ["-T", "5"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_deploy_starts_tikv_as_one_stage(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="serial-tikv", port_base=4900)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=2, tidb_count=1))
    commands = []
    waits = []

    def allocate(name, *, env):
        commands.append((["allocate", name], "network"))
        return "10.252.42.0/24"

    monkeypatch.setattr("src.execution.deployments.tidb.create_tidb_network", allocate)

    try:
        monkeypatch.setattr(deployment, "preflight", lambda: None)
        monkeypatch.setattr(deployment, "_project_exists", lambda: False)
        monkeypatch.setattr(deployment.snapshots, "_save_bootstrap_cache", lambda: None)
        deployment._env["DOCKER_ROOT_DIR"] = "/srv/docker-xfs"
        monkeypatch.setattr(
            deployment,
            "_run",
            lambda command, component: commands.append((command, component)) or "",
        )
        monkeypatch.setattr(
            deployment,
            "_wait",
            lambda label, check, timeout: waits.append((label, timeout)),
        )
        monkeypatch.setattr(deployment.snapshots, "_save_bootstrap_cache", lambda: None)

        deployment.deploy()

        assert [component for _, component in commands] == [
            "network",
            "pd",
            "tikv/tikv-0",
            "tikv/tikv-1",
            "tidb/tidb-0",
            "monitoring",
        ]
        assert [label for label, _ in waits] == [
            "pd",
            "pd leader before tikv/tikv-0",
            "tikv/tikv-0",
            "pd leader before tikv/tikv-1",
            "tikv/tikv-1",
            "pd leader before tidb/tidb-0",
            "tidb/tidb-0",
            "prometheus",
        ]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_pd_request_supports_json_get_and_post(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-request")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    commands = []
    try:
        monkeypatch.setattr(deployment, "_service_container_id", lambda service: "pd-container")
        monkeypatch.setattr(deployment, "current_pd_leader", lambda: "pd-0")
        monkeypatch.setattr(
            deployment,
            "_run",
            lambda command, component: commands.append((command, component)) or "{}",
        )

        assert deployment.pd_request("GET", "/pd/api/v1/config") == {}
        assert deployment.pd_request(
            "POST",
            "/pd/api/v1/config",
            {"schedule": {"merge-schedule-limit": 8}},
        ) == {}
        assert commands == [
            (
                [
                    "docker",
                    "exec",
                    "pd-container",
                    "wget",
                    "-qO-",
                    "-T",
                    "5",
                    "http://127.0.0.1:2379/pd/api/v1/config",
                ],
                "pd-0",
            ),
            (
                [
                    "docker",
                    "exec",
                    "pd-container",
                    "wget",
                    "-qO-",
                    "-T",
                    "5",
                    "--method=POST",
                    "--header=Content-Type: application/json",
                    '--body-data={"schedule":{"merge-schedule-limit":8}}',
                    "http://127.0.0.1:2379/pd/api/v1/config",
                ],
                "pd-0",
            ),
        ]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_pd_request_get_retries_transient_pd_5xx(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-get-retry")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    urls = []

    def flaky_run(command, component):
        urls.append(command[-1])
        if len(urls) <= 2:
            raise RuntimeError(
                "TiDB command failed: run_id='pd-get-retry', "
                f"component={component!r}, command={command!r}, returncode=8, stdout='', stderr=''"
            )
        return '{"name":"pd-0"}'

    monkeypatch.setattr("time.sleep", lambda seconds: None)
    monkeypatch.setattr(deployment, "_service_container_id", lambda service: "pd-container")
    monkeypatch.setattr(deployment, "_run", flaky_run)
    try:
        assert deployment.pd_request("GET", "/pd/api/v1/stores") == {"name": "pd-0"}
        # Two failed leader probes recover inside the retry window; the fetch
        # itself succeeds on the first attempt.
        assert len(urls) == 4
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_pd_request_post_does_not_retry_the_mutation(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-post-fail-fast")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    mutations = []

    def flaky_run(command, component):
        if "--method=POST" in command:
            mutations.append(command)
            raise RuntimeError(
                "TiDB command failed: run_id='pd-post-fail-fast', "
                f"component={component!r}, command={command!r}, returncode=8, stdout='', stderr=''"
            )
        return '{"name":"pd-0"}'

    monkeypatch.setattr("time.sleep", lambda seconds: None)
    monkeypatch.setattr(deployment, "_service_container_id", lambda service: "pd-container")
    monkeypatch.setattr(deployment, "_run", flaky_run)
    try:
        with pytest.raises(RuntimeError, match="returncode=8"):
            deployment.pd_request("POST", "/pd/api/v1/store/1012/limit", {"rate": 0})
        assert len(mutations) == 1
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_pd_ctl_accepts_empty_operator_add_response_only(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-ctl-empty-response")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(deployment, "exec", lambda target, command: "")

    try:
        assert deployment._pd_ctl("operator", "add", "transfer-leader", "1", "2") is None
        with pytest.raises(RuntimeError, match="empty response"):
            deployment._pd_ctl("operator", "show")
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_pd_ctl_accepts_success_text_for_store_lifecycle_commands(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-ctl-store-lifecycle")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(deployment, "exec", lambda target, command: "Success!\n")

    try:
        assert deployment._pd_ctl("store", "delete", "292") == "Success!"
        assert deployment._pd_ctl("store", "remove-tombstone") == "Success!"
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_pd_ctl_accepts_text_operator_peer_creation_response(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-ctl-peer-create-response")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(
        deployment,
        "exec",
        lambda target, command: "Success! The operator is created.\"",
    )

    try:
        assert deployment._pd_ctl("operator", "add", "remove-peer", "11", "2") == (
            "Success! The operator is created.\""
        )
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_upgrade_readiness_labels_map_to_database_services():
    deployment = TiDBDockerDeployment(run_id="upgrade-readiness-labels")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))

    try:
        assert deployment._stage_services("rolling upgrade PD") == ("pd-0",)
        assert deployment._stage_services("rolling upgrade TiKV") == ("tikv-0",)
        assert deployment._stage_services("TiKV region leader metadata") == ("tikv-0",)
        assert deployment._stage_services("TiKV leader eviction") == ("tikv-0",)
        assert deployment._stage_services("pd leader before tikv/tikv-0") == ("pd-0",)
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_pd_control_plane_readiness_requires_pd_ctl_store(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-control-plane-readiness")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    checks = []
    monkeypatch.setattr(deployment, "_check_pd", lambda: checks.append("members"))
    monkeypatch.setattr(deployment, "_pd_stores", lambda: checks.append("stores"))

    try:
        deployment.rollout._check_pd_control_plane()
        assert checks == ["members", "stores"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tikv_leader_transfer_waits_for_pd_to_evacuate_all_leaders(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="leader-transfer-plan")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=3, tidb_count=1))
    target_store = {
        "store": {"id": 1, "address": "tikv-0:20160", "state_name": "Up"},
        "status": {"leader_count": 2},
    }
    waits = []
    pd_commands = []

    def wait(label, check, timeout):
        waits.append((label, timeout))
        target_store["status"]["leader_count"] = 0
        check()

    monkeypatch.setattr(deployment.stores, "_store_for_target", lambda target: target_store)
    monkeypatch.setattr(deployment, "_pd_ctl", lambda *args: pd_commands.append(args))
    monkeypatch.setattr(deployment, "_wait", wait)

    try:
        assert deployment.rollout._transfer_tikv_leaders("tikv/tikv-0", 1, 2) == 2
        assert waits == [("TiKV leader transfer", 300)]
        assert pd_commands == [
            ("scheduler", "add", "evict-leader-scheduler", "1"),
            ("scheduler", "remove", "evict-leader-scheduler-1"),
        ]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tikv_leader_transfer_fails_when_pd_does_not_evacuate_leaders(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="leader-transfer-timeout")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=3, tidb_count=1))
    target_store = {
        "store": {"id": 1, "address": "tikv-0:20160", "state_name": "Up"},
        "status": {"leader_count": 1},
    }
    pd_commands = []
    monkeypatch.setattr(deployment.stores, "_store_for_target", lambda target: target_store)
    monkeypatch.setattr(deployment, "_pd_ctl", lambda *args: pd_commands.append(args))
    monkeypatch.setattr(deployment, "_wait", lambda label, check, timeout: check())

    try:
        with pytest.raises(RuntimeError, match="leader evacuation is incomplete"):
            deployment.rollout._transfer_tikv_leaders("tikv/tikv-0", 1, 1)
        assert pd_commands == [
            ("scheduler", "add", "evict-leader-scheduler", "1"),
            ("scheduler", "remove", "evict-leader-scheduler-1"),
        ]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tidb_bootstrap_timeout_is_longer_for_the_first_sql_node():
    deployment = TiDBDockerDeployment(run_id="bootstrap-timeout")
    deployment.configure_runtime(_runtime(pd_count=3, tikv_count=3, tidb_count=2))

    try:
        assert deployment.FIRST_TIDB_BOOTSTRAP_TIMEOUT == 900
        assert deployment._tidb_readiness_timeout(0) == 900
        assert deployment.FOLLOWING_TIDB_READINESS_TIMEOUT == 300
        assert deployment._tidb_readiness_timeout(1) == 300
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_small_tidb_topology_keeps_the_default_first_node_timeout():
    deployment = TiDBDockerDeployment(run_id="small-bootstrap-timeout")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))

    try:
        assert deployment._tidb_readiness_timeout(0) == 300
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_reused_tidb_storage_uses_warm_tikv_readiness_timeout():
    deployment = TiDBDockerDeployment(
        run_id="warm-tikv-readiness",
        warm_tidb_readiness_timeout_sec=601,
    )
    deployment.snapshots.persistent_state_reused = True
    assert deployment._tikv_readiness_timeout() == 601


def test_cold_tidb_storage_uses_the_configured_tikv_readiness_timeout():
    deployment = TiDBDockerDeployment(run_id="cold-tikv-readiness")
    assert deployment._tikv_readiness_timeout() == 1800


def test_prometheus_readiness_timeout_scales_with_target_count():
    small = TiDBDockerDeployment(run_id="small-prometheus-timeout")
    small.configure_runtime(_runtime(pd_count=1, tikv_count=2, tidb_count=3))
    expanded = TiDBDockerDeployment(run_id="expanded-prometheus-timeout")
    expanded.configure_runtime(_runtime(pd_count=4, tikv_count=9, tidb_count=5))

    try:
        assert small._prometheus_readiness_timeout() == 120
        assert expanded._prometheus_readiness_timeout() == 240
    finally:
        shutil.rmtree(small.runtime_dir)
        shutil.rmtree(expanded.runtime_dir)


def test_expanded_topology_resource_contract_accounts_for_pd_memory():
    runtime = _runtime(pd_count=4, tikv_count=9, tidb_count=5)

    assert runtime.resources.worker_physical_cores == 19
    assert runtime.resources.worker_memory_mb == 44032
    assert runtime.resources.container_cpu_limit == 19.0
    assert runtime.resources.container_memory_mb == 44032


def test_pd_cpu_limit_is_rendered_and_included_in_resource_contract():
    runtime = _runtime(pd_count=4, tikv_count=9, tidb_count=5, pd_cpu_limit=2.0)
    deployment = TiDBDockerDeployment(
        run_id="pd-cpu-contract",
        port_base=4850,
        storage_key=None,
    )
    deployment.configure_runtime(runtime)
    with open(deployment.compose_file, encoding="utf-8") as handle:
        compose = yaml.safe_load(handle)
    assert compose["services"]["pd-0"]["cpus"] == 2.0
    assert compose["services"]["tikv-0"]["cpus"] == 1.0
    assert runtime.resources.worker_physical_cores == 23
    assert runtime.resources.container_cpu_limit == 23.0
    shutil.rmtree(deployment.runtime_dir)


def test_tidb_readiness_timeout_preserves_diagnostics(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="readiness-diagnostics")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(
        deployment,
        "_wait",
        lambda *args: (_ for _ in ()).throw(RuntimeError("last SQL error")),
    )
    monkeypatch.setattr(
        deployment,
        "_tidb_readiness_diagnostics",
        lambda target: f"target={target}, bootstrap=still-running",
    )

    try:
        with pytest.raises(RuntimeError, match="last SQL error; readiness_diagnostics=target=tidb/tidb-0"):
            deployment._wait_tidb_target("tidb/tidb-0", 900)
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tidb_bootstrap_cache_uses_distinct_runtime_data_dirs(monkeypatch, tmp_path):
    monkeypatch.setenv("AIOPS_TIDB_BOOTSTRAP_CACHE_DIR", str(tmp_path / "cache"))
    cold = TiDBDockerDeployment(run_id="cache-cold", port_base=4900)
    cold.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    cached_path = cold.snapshots.bootstrap_cache_path
    metadata = cold.snapshots._bootstrap_cache_metadata()
    for node_type, service in (("pd", "pd-0"), ("tikv", "tikv-0")):
        source = os.path.join(cached_path, node_type, service)
        os.makedirs(source)
        with open(os.path.join(source, "bootstrap.marker"), "w", encoding="utf-8") as handle:
            handle.write(node_type)
    with open(os.path.join(cached_path, "metadata.json"), "w", encoding="utf-8") as handle:
        json.dump(metadata, handle)

    warm = TiDBDockerDeployment(run_id="cache-warm", port_base=4920)
    warm.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))

    try:
        assert warm.snapshots.bootstrap_cache_used is True
        assert warm.snapshots.bootstrap_cache_path == cached_path
        assert warm.snapshots.bootstrap_data_paths != cold.snapshots.bootstrap_data_paths
        for node_type, service in (("pd", "pd-0"), ("tikv", "tikv-0")):
            runtime_marker = os.path.join(
                warm.snapshots.bootstrap_data_paths[(node_type, service)], "bootstrap.marker"
            )
            with open(runtime_marker, encoding="utf-8") as handle:
                assert handle.read() == node_type
        with open(warm.compose_file, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle)
        assert any(
            warm.snapshots.bootstrap_data_paths[("pd", "pd-0")] in volume
            for volume in compose["services"]["pd-0"]["volumes"]
        )
    finally:
        shutil.rmtree(cold.runtime_dir)
        shutil.rmtree(warm.runtime_dir)


def test_tidb_bootstrap_cache_can_be_disabled_for_a_fresh_topology(monkeypatch, tmp_path):
    cache_root = tmp_path / "cache"
    cache_root.mkdir()
    monkeypatch.setenv("AIOPS_TIDB_BOOTSTRAP_CACHE_DIR", str(cache_root))
    deployment = TiDBDockerDeployment(run_id="cache-disabled", port_base=4930)
    deployment.configure_runtime(
        _runtime(
            pd_count=3,
            tikv_count=5,
            tidb_count=2,
            bootstrap_cache_enabled=False,
        )
    )

    try:
        assert deployment.snapshots.bootstrap_cache_enabled is False
        assert deployment.snapshots.bootstrap_cache_used is False
        assert deployment.snapshots.bootstrap_cache_key is None
        assert deployment.snapshots.bootstrap_cache_path is None
        assert set(deployment.snapshots.bootstrap_data_paths) == {
            *(('pd', f'pd-{index}') for index in range(3)),
            *(('tikv', f'tikv-{index}') for index in range(5)),
        }
        assert not list(cache_root.iterdir())
        with pytest.raises(RuntimeError, match="bootstrap cache is disabled"):
            deployment.snapshots._save_bootstrap_cache()
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tidb_bootstrap_cache_is_saved_after_a_cold_deploy(monkeypatch, tmp_path):
    monkeypatch.setenv("AIOPS_TIDB_BOOTSTRAP_CACHE_DIR", str(tmp_path / "cache"))
    deployment = TiDBDockerDeployment(run_id="cache-save", port_base=4940)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    deployment._env["DOCKER_ROOT_DIR"] = "/var/lib/docker"
    commands = []
    monkeypatch.setattr(deployment, "_run", lambda command, component: commands.append((command, component)) or "")
    monkeypatch.setattr(deployment, "_wait", lambda *args: None)

    def snapshot_component_data(service, node_type, destination):
        with open(os.path.join(destination, "bootstrap.marker"), "w", encoding="utf-8") as handle:
            handle.write(node_type)

    monkeypatch.setattr(
        deployment.snapshots,
        "_snapshot_component_data",
        snapshot_component_data,
    )

    try:
        deployment.snapshots._save_bootstrap_cache()
        assert deployment.snapshots.bootstrap_cache_used is True
        assert os.path.isfile(os.path.join(deployment.snapshots.bootstrap_cache_path, "metadata.json"))
        assert ["stop" in command[0] for command in commands] == [True, False, False, False]
        assert ["start" in command[0] for command in commands] == [False, True, True, True]

    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tidb_bootstrap_cache_is_never_loaded_for_a_deferred_topology(monkeypatch, tmp_path):
    monkeypatch.setenv("AIOPS_TIDB_BOOTSTRAP_CACHE_DIR", str(tmp_path / "cache"))
    full = TiDBDockerDeployment(run_id="cache-full-topology", port_base=4950)
    full.configure_runtime(_runtime(pd_count=3, tikv_count=6, tidb_count=2))
    cached_path = full.snapshots.bootstrap_cache_path
    metadata = full.snapshots._bootstrap_cache_metadata()
    for node_type, service in (("pd", "pd-0"), ("tikv", "tikv-4")):
        source = os.path.join(cached_path, node_type, service)
        os.makedirs(source)
        with open(os.path.join(source, "bootstrap.marker"), "w", encoding="utf-8") as handle:
            handle.write(node_type)
    with open(os.path.join(cached_path, "metadata.json"), "w", encoding="utf-8") as handle:
        json.dump(metadata, handle)

    deferred = TiDBDockerDeployment(run_id="cache-deferred-topology", port_base=4970)
    deferred.configure_runtime(
        _runtime(pd_count=3, tikv_count=6, tidb_count=2, deferred_tikv_count=2)
    )

    try:
        assert deferred.snapshots.bootstrap_cache_used is False
        assert deferred.snapshots.bootstrap_cache_key is None
        assert deferred.snapshots.bootstrap_cache_path is None
        assert os.path.isdir(cached_path)
        for node_type, service in (("pd", "pd-0"), ("tikv", "tikv-4")):
            assert os.listdir(deferred.snapshots.bootstrap_data_paths[(node_type, service)]) == []
    finally:
        shutil.rmtree(full.runtime_dir)
        shutil.rmtree(deferred.runtime_dir)


def test_tidb_retry_after_cache_seeded_failure_discards_the_cache(monkeypatch, tmp_path):
    monkeypatch.setenv("AIOPS_TIDB_BOOTSTRAP_CACHE_DIR", str(tmp_path / "cache"))
    deployment = TiDBDockerDeployment(run_id="cache-retry-discard", port_base=4990)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    deployment._env["DOCKER_ROOT_DIR"] = "/var/lib/docker"
    cached_path = deployment.snapshots.bootstrap_cache_path
    metadata = deployment.snapshots._bootstrap_cache_metadata()
    for node_type, service in (("pd", "pd-0"), ("tikv", "tikv-0")):
        source = os.path.join(cached_path, node_type, service)
        os.makedirs(source)
        with open(os.path.join(source, "bootstrap.marker"), "w", encoding="utf-8") as handle:
            handle.write(node_type)
        shutil.copytree(
            source, deployment.snapshots.bootstrap_data_paths[(node_type, service)], dirs_exist_ok=True
        )
    with open(os.path.join(cached_path, "metadata.json"), "w", encoding="utf-8") as handle:
        json.dump(metadata, handle)
    deployment.snapshots.bootstrap_cache_used = True
    monkeypatch.setattr(deployment, "_run", lambda command, component: "")
    monkeypatch.setattr(deployment, "_start_cluster", lambda: None)

    try:
        deployment._retry_cluster_start(RuntimeError("first cluster start failed"))

        assert deployment.snapshots.bootstrap_cache_used is False
        assert not os.path.exists(cached_path)
        for node_type, service in (("pd", "pd-0"), ("tikv", "tikv-0")):
            runtime_dir = deployment.snapshots.bootstrap_data_paths[(node_type, service)]
            assert os.listdir(runtime_dir) == []
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_pd_json_queries_the_current_pd_leader(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-leader-probe")
    deployment.configure_runtime(_runtime(pd_count=3, tikv_count=1, tidb_count=1))
    commands = []

    try:
        monkeypatch.setattr(
            deployment,
            "_service_container_id",
            lambda service: f"{service}-container",
        )

        def run(command, component):
            commands.append((command, component))
            if command[-1].endswith("/pd/api/v1/leader"):
                return '{"name": "pd-2"}'
            return '{"stores": []}'

        monkeypatch.setattr(deployment, "_run", run)

        assert deployment._pd_json("/pd/api/v1/stores") == {"stores": []}
        assert commands[-1][0][1] == "exec"
        assert commands[-1][0][2] == "pd-2-container"
        assert commands[-1][1] == "pd-2"
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tikv_readiness_can_validate_only_started_services(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="partial-tikv")
    deployment.configure_runtime(
        _runtime(pd_count=1, tikv_count=2, tidb_count=1, deferred_tikv_count=1)
    )

    try:
        monkeypatch.setattr(
            deployment,
            "_pd_json",
            lambda path: {
                "stores": [
                    {"store": {"address": "tikv-0:20160", "state_name": "Up"}},
                ]
            },
        )
        deployment._check_tikv({"tikv-0"})
        deployment._check_tikv()
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tikv_readiness_reports_exited_container_immediately(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="exited-tikv")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))

    try:
        monkeypatch.setattr(
            deployment,
            "_pd_json",
            lambda path: {
                "stores": [
                    {"store": {"address": "tikv-0:20160", "state_name": "Down"}},
                ]
            },
        )
        monkeypatch.setattr(deployment, "_service_container_id", lambda service: "tikv-container")
        monkeypatch.setattr(
            deployment,
            "_run",
            lambda command, component: (
                '{"Status":"exited","Running":false,"ExitCode":1,"Error":"pd unavailable"}'
            ),
        )

        with pytest.raises(RuntimeError, match="TiKV container exited before readiness"):
            deployment._check_tikv()
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tidb_readiness_reports_exited_container_immediately(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="exited-tidb")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))

    try:
        monkeypatch.setattr(deployment, "_service_container_id", lambda service: "tidb-container")
        monkeypatch.setattr(
            deployment,
            "_run",
            lambda command, component: (
                '{"Status":"exited","Running":false,"ExitCode":1,"Error":"pd unavailable"}'
                if command[1] == "inspect"
                else "fatal TiDB startup log"
            ),
        )

        with pytest.raises(RuntimeError, match="TiDB container exited before readiness"):
            deployment._check_tidb_target("tidb/tidb-0")
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_deferred_tikv_is_created_without_starting(monkeypatch):
    monkeypatch.setattr(
        "src.execution.deployments.tidb.create_tidb_network",
        lambda name, *, env: "10.252.42.0/24",
    )
    deployment = TiDBDockerDeployment(run_id="deferred-tikv", port_base=4950)
    deployment.configure_runtime(
        _runtime(pd_count=1, tikv_count=2, tidb_count=1, deferred_tikv_count=1)
    )
    commands = []

    try:
        deployment._env["DOCKER_ROOT_DIR"] = "/tmp"
        monkeypatch.setattr(deployment, "preflight", lambda: None)
        monkeypatch.setattr(deployment, "_project_exists", lambda: False)
        monkeypatch.setattr(
            deployment,
            "_run",
            lambda command, component: commands.append((command, component)) or "",
        )
        monkeypatch.setattr(deployment, "_wait", lambda label, check, timeout: None)

        deployment.deploy()

        deferred = next(command for command, component in commands if component == "tikv/tikv-1")
        assert deferred[-2:] == ["create", "tikv-1"]
        assert "--no-start" not in deferred
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tikv_stage_wait_ignores_not_yet_created_deferred_container(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="deferred-stage-wait")
    deployment.configure_runtime(
        _runtime(pd_count=1, tikv_count=4, tidb_count=1, deferred_tikv_count=1)
    )
    inspected = []

    def container_id(service):
        if service not in deployment.active_tikv_services:
            raise RuntimeError(
                f"TiDB container not found: run_id={deployment.run_id!r}, component={service!r}"
            )
        inspected.append(service)
        return "container"

    try:
        monkeypatch.setattr(deployment, "_service_container_id", container_id)
        monkeypatch.setattr(
            deployment,
            "_run",
            lambda command, component: json.dumps(
                {"State": {"Status": "running", "Running": True, "OOMKilled": False, "ExitCode": 0}}
            ),
        )
        monkeypatch.setattr(
            deployment,
            "_pd_json",
            lambda path: {
                "stores": [
                    {"store": {"address": f"tikv-{index}:20160", "state_name": "Up"}}
                    for index in range(3)
                ]
            },
        )

        deployment._wait("tikv", deployment._check_tikv, 5)

        assert inspected == ["tikv-0", "tikv-1", "tikv-2"]
        assert deployment._stage_services("tikv") == ("tikv-0", "tikv-1", "tikv-2")
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tikv_stage_wait_still_fails_when_active_container_stopped(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="deferred-stage-stopped")
    deployment.configure_runtime(
        _runtime(pd_count=1, tikv_count=4, tidb_count=1, deferred_tikv_count=1)
    )

    try:
        monkeypatch.setattr(
            deployment, "_service_container_id", lambda service: "container"
        )
        monkeypatch.setattr(
            deployment,
            "_run",
            lambda command, component: json.dumps(
                {"State": {"Status": "created", "Running": False, "OOMKilled": False, "ExitCode": 0}}
            ),
        )
        monkeypatch.setattr(
            deployment, "_readiness_diagnostics", lambda label: ""
        )

        with pytest.raises(RuntimeError, match="TiDB service stopped during readiness"):
            deployment._wait("tikv", deployment._check_tikv, 5)
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_image_group_cold_render_keeps_pd_and_tikv_data_inside_container(monkeypatch, tmp_path):
    monkeypatch.setenv("AIOPS_TIDB_IMAGE_GROUP_DIR", str(tmp_path / "groups"))
    deployment = TiDBDockerDeployment(
        run_id="image-group-cold",
        port_base=4960,
        image_group_key="qp01-object-listing",
    )
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))

    try:
        assert deployment.tidb_readiness_timeout_sec == 1800
        with open(deployment.compose_file, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle)
        assert compose["services"]["pd-0"]["image"] == TIDB_V8_1_0.pd_image
        assert compose["services"]["tikv-0"]["image"] == TIDB_V8_1_0.tikv_image
        assert compose["services"]["pd-0"]["user"] == "0:0"
        assert compose["services"]["tikv-0"]["user"] == "0:0"
        assert "tmpfs" not in compose["services"]["pd-0"]
        # PD 数据必须留在容器可写层：bind mount/tmpfs 都不会被 docker commit
        # 捕获，group 镜像里的 PD 会以空数据重新 bootstrap 出新的 cluster ID，
        # 与 TiKV 镜像层数据失配后拒绝启动。
        assert all(
            not volume.endswith(":/data/pd")
            for volume in compose["services"]["pd-0"]["volumes"]
        )
        assert all(
            "/data/tikv" not in volume
            for volume in compose["services"]["tikv-0"]["volumes"]
        )
        assert compose["services"]["tikv-0"]["user"] == "0:0"
        tikv_config = next(
            volume.split(":", 1)[0]
            for volume in compose["services"]["tikv-0"]["volumes"]
            if volume.endswith(":/tikv.toml:ro")
        )
        assert tikv_config == deployment.snapshots.image_group_tikv_config_path
        with open(tikv_config, encoding="utf-8") as handle:
            assert 'capacity = "8GB"' in handle.read()
        assert deployment.snapshots.image_group_snapshot_name().startswith(
            "aiopsbench-tidb-group-qp01-object-listing-"
        )
        assert deployment.snapshots.image_group_exists(deployment.snapshots.image_group_name) is False
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_image_group_identity_changes_with_topology_and_reuses_only_matching_images(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("AIOPS_TIDB_IMAGE_GROUP_DIR", str(tmp_path / "groups"))
    first = TiDBDockerDeployment(
        run_id="image-group-one",
        port_base=4980,
        image_group_key="qp01-object-listing",
    )
    first.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    second = TiDBDockerDeployment(
        run_id="image-group-three-tikv",
        port_base=4990,
        image_group_key="qp01-object-listing",
    )
    second.configure_runtime(_runtime(pd_count=1, tikv_count=3, tidb_count=1))

    try:
        assert first.snapshots.image_group_name != second.snapshots.image_group_name
        first.snapshots.image_group_metadata_path.parent.mkdir(parents=True)
        first.snapshots.image_group_metadata_path.write_text(
            json.dumps(first.snapshots.image_group_metadata),
            encoding="utf-8",
        )
        monkeypatch.setattr(
            "src.execution.deployments.tidb.subprocess.run",
            lambda *args, **kwargs: SimpleNamespace(returncode=0),
        )
        assert first.snapshots.image_group_exists(first.snapshots.image_group_name) is True
        first.snapshots.select_image_group(first.snapshots.image_group_name, first.snapshots.base_image_snapshot_name())
        with open(first.compose_file, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle)
        assert compose["services"]["pd-0"]["image"] == first.snapshots.image_group_images["pd-0"]
        assert compose["services"]["tikv-0"]["image"] == first.snapshots.image_group_images["tikv-0"]
        assert all(
            "/data/" not in volume
            for service in ("pd-0", "tikv-0")
            for volume in compose["services"][service]["volumes"]
        )
    finally:
        shutil.rmtree(first.runtime_dir)
        shutil.rmtree(second.runtime_dir)


def test_image_group_save_commits_each_database_storage_container(monkeypatch, tmp_path):
    monkeypatch.setenv("AIOPS_TIDB_IMAGE_GROUP_DIR", str(tmp_path / "groups"))
    deployment = TiDBDockerDeployment(
        run_id="image-group-save",
        port_base=5000,
        image_group_key="qp01-object-listing",
    )
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    deployment._env["DOCKER_ROOT_DIR"] = str(tmp_path)
    commands = []
    monkeypatch.setattr(
        deployment,
        "_run",
        lambda command, component="cluster": commands.append((command, component)) or "",
    )
    monkeypatch.setattr(
        deployment,
        "_service_container_id",
        lambda service: f"container-{service}",
    )
    monkeypatch.setattr(deployment, "_start_database_services", lambda: None)
    deployment._container_ids.update({"pd-0": "stale-pd", "tikv-0": "stale-tikv"})

    try:
        deployment.snapshots.save_image_group(deployment.snapshots.image_group_name, {"case": "qp01"})
        assert deployment.snapshots.image_group_metadata_path.is_file()
        commit_commands = [
            command
            for command, component in commands
            if command[:2] == ["docker", "commit"]
        ]
        assert len(commit_commands) == 2
        assert {command[-2] for command in commit_commands} == {
            "container-pd-0",
            "container-tikv-0",
        }
        assert {command[-1] for command in commit_commands} == {
            deployment.snapshots.image_group_images["pd-0"],
            deployment.snapshots.image_group_images["tikv-0"],
        }
        assert all("/data/pd" not in " ".join(command) for command in commit_commands)
        assert all("/data/tikv" not in " ".join(command) for command in commit_commands)
        assert deployment.snapshots.image_group_selected is True
        assert deployment.snapshots.image_group_reused is True
        assert deployment._container_ids == {}
        with open(deployment.compose_file, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle)
        assert compose["services"]["pd-0"]["image"] == deployment.snapshots.image_group_images["pd-0"]
        assert compose["services"]["tikv-0"]["image"] == deployment.snapshots.image_group_images["tikv-0"]
    finally:
        deployment.snapshots.release_image_group_lock()
        shutil.rmtree(deployment.runtime_dir)


def test_start_database_services_clears_stale_container_ids(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="start-clears-cache", port_base=5010)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    commands = []
    deployment._container_ids["pd-0"] = "stale-pd-container"

    try:
        def fake_run(command, component="cluster"):
            if command[:3] == ["docker", "info", "--format"]:
                return "16 34359738368 /tmp"
            commands.append((command, component))
            return ""

        monkeypatch.setattr(deployment, "_run", fake_run)
        monkeypatch.setattr(deployment, "_wait", lambda label, check, timeout: None)

        deployment._start_database_services()

        assert deployment._container_ids == {}
        assert commands[0][0] == deployment._compose + ["up", "--detach", "pd-0"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_cold_tikv_readiness_uses_case_runtime_timeout():
    deployment = TiDBDockerDeployment(
        run_id="cold-tikv-timeout",
        tidb_readiness_timeout_sec=777,
    )
    assert deployment._tikv_readiness_timeout() == 777


def test_image_group_deploy_does_not_save_bootstrap_cache(monkeypatch):
    monkeypatch.setattr(
        "src.execution.deployments.tidb.create_tidb_network",
        lambda name, *, env: "10.252.42.0/24",
    )
    deployment = TiDBDockerDeployment(
        run_id="image-group-no-bootstrap-cache",
        image_group_key="qp01-object-listing",
    )
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    saved = []
    deployment._env["DOCKER_ROOT_DIR"] = "/tmp"
    monkeypatch.setattr(deployment, "preflight", lambda: None)
    monkeypatch.setattr(deployment, "_project_exists", lambda: False)
    monkeypatch.setattr(deployment.snapshots, "_prepare_persistent_state", lambda: None)
    monkeypatch.setattr(deployment, "_start_database_services", lambda: None)
    monkeypatch.setattr(deployment, "_run", lambda *args: "")
    monkeypatch.setattr(deployment, "_wait", lambda *args: None)
    monkeypatch.setattr(deployment.snapshots, "_save_bootstrap_cache", lambda: saved.append(True))

    try:
        deployment.deploy()
        assert saved == []
    finally:
        shutil.rmtree(deployment.runtime_dir)
def test_teardown_normalizes_data_for_stopped_containers(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="stopped-teardown", port_base=4950)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    commands = []
    helper_calls = []

    def fake_run(command, component):
        commands.append((command, component))
        if command[-4:] == ["ps", "--all", "--quiet", "pd-0"]:
            return "pd-container\n"
        if command[-4:] == ["ps", "--all", "--quiet", "tikv-0"]:
            return "tikv-container\n"
        if command[:3] == ["docker", "inspect", "--format"]:
            return "false\n"
        return ""

    def fake_subprocess_run(command, **kwargs):
        helper_calls.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(deployment, "_run", fake_run)
    monkeypatch.setattr(deployment, "_docker_info", lambda: None)
    monkeypatch.setattr("src.execution.deployments.tidb.subprocess.run", fake_subprocess_run)
    deployment.teardown()

    assert len(helper_calls) == 2
    assert all(command[:2] == ["docker", "run"] for command in helper_calls)
    assert all("--format" not in command for command in helper_calls)
    assert not any(command[0][0:2] == ["docker", "exec"] for command in commands)


def _teardown_with_incomplete_runtime_audit(monkeypatch, tmp_path):
    deployment = TiDBDockerDeployment(run_id="audit-teardown", port_base=4950)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(deployment, "_run", lambda command, component: "")
    monkeypatch.setattr(deployment, "_docker_info", lambda: None)
    monkeypatch.setattr(
        "src.execution.deployments.tidb.subprocess.run",
        lambda command, **kwargs: SimpleNamespace(returncode=0, stdout="[]", stderr=""),
    )
    deployment._env["AIOPS_RUNTIME_AUDIT_PATH"] = str(tmp_path / "docker-runtime.json")
    return deployment


def test_teardown_degrades_runtime_audit_when_deployment_never_became_ready(monkeypatch, tmp_path, capsys):
    deployment = _teardown_with_incomplete_runtime_audit(monkeypatch, tmp_path)
    deployment.teardown()

    assert "runtime audit incomplete" in capsys.readouterr().out


def test_teardown_keeps_strong_runtime_audit_after_ready_deployment(monkeypatch, tmp_path):
    deployment = _teardown_with_incomplete_runtime_audit(monkeypatch, tmp_path)
    deployment._deployment_reached_ready = True

    with pytest.raises(RuntimeError, match="runtime audit was incomplete"):
        deployment.teardown()


def test_pd_readiness_requires_an_elected_leader(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="pd-leader-readiness")
    deployment.configure_runtime(_runtime(pd_count=3, tikv_count=1, tidb_count=1))
    try:
        responses = {
            "/pd/api/v1/members": {"members": [{"name": "pd-0"}, {"name": "pd-1"}, {"name": "pd-2"}]},
            "/pd/api/v1/leader": {},
        }
        monkeypatch.setattr(deployment, "_pd_json", lambda path: responses[path])
        with pytest.raises(RuntimeError, match="PD has no valid leader"):
            deployment._check_pd()
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_region_health_observation_reads_current_pd_state(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="region-health-observation")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(deployment, "_pd_stores", lambda: [{"store": {"id": 1, "state_name": "Up"}}])
    monkeypatch.setattr(deployment, "_pd_ctl", lambda *args: [{"kind": "operator"}])

    try:
        assert deployment.stores.region_health_observation() == {
            "stores": [{"store": {"id": 1, "state_name": "Up"}}],
            "operators": [{"kind": "operator"}],
        }
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_tikv_stage_running_assert_skips_deferred_services(monkeypatch):
    """Deferred TiKV services have no container until the stage wait passes.

    The stage-level running assert must cover exactly the active TiKV services
    (SF02 tikv_count=4 deferred=1, BC05 deferred=2/3), matching the default
    expectation of _check_tikv; iterating every configured TiKV service fails
    deferred deployments with
    "TiDB container not found: component='tikv-3'/'tikv-4'/'tikv-5'".
    """
    deployment = TiDBDockerDeployment(run_id="deferred-tikv-stage-assert", port_base=4650)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=4, tidb_count=1, deferred_tikv_count=1))

    try:
        assert deployment.active_tikv_services == {"tikv-0", "tikv-1", "tikv-2"}
        assert deployment._stage_services("tikv") == ("tikv-0", "tikv-1", "tikv-2")
        # Upgrade stages still assert every configured TiKV service.
        assert deployment._stage_services("rolling upgrade TiKV") == (
            "tikv-0", "tikv-1", "tikv-2", "tikv-3",
        )

        snapshot_services = []

        def fake_snapshot(service):
            snapshot_services.append(service)
            return {"State": {"Status": "running", "OOMKilled": False, "ExitCode": 0}}

        monkeypatch.setattr(deployment, "_container_snapshot", fake_snapshot)
        deployment._assert_stage_running("tikv")
        assert snapshot_services == ["tikv-0", "tikv-1", "tikv-2"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_port_block_stays_on_free_planned_ports(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="port-block-free", port_base=4400)
    monkeypatch.setattr("src.execution.host_ports._bindable", lambda port: True)
    try:
        deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
        assert deployment.port_base == 4400
        assert deployment.tidb_endpoints == {"tidb/tidb-0": ("127.0.0.1", 4400)}
        assert deployment.prometheus_port == 4402
    finally:
        deployment._port_lease.close()
        shutil.rmtree(deployment.runtime_dir)


def test_port_block_shifts_past_occupied_ports(monkeypatch):
    """Chunk manifests reuse port segments across concurrent experiments; the
    block must shift to the next fully bindable span instead of failing at
    preflight after planning."""
    deployment = TiDBDockerDeployment(run_id="port-block-shift", port_base=4400)
    monkeypatch.setattr(
        "src.execution.host_ports._bindable", lambda port: port >= 4403,
    )
    try:
        deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
        assert deployment.port_base == 4403
        assert deployment.tidb_endpoints == {"tidb/tidb-0": ("127.0.0.1", 4403)}
        assert deployment.prometheus_port == 4405
    finally:
        deployment._port_lease.close()
        shutil.rmtree(deployment.runtime_dir)


def test_port_block_selection_exhaustion_raises(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="port-block-exhausted", port_base=4400)
    monkeypatch.setattr("src.execution.host_ports._bindable", lambda port: False)
    with pytest.raises(RuntimeError, match="Host port reservation failed"):
        deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))


def test_replication_port_block_span_covers_downstream_and_ticdc(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="port-block-replication", port_base=4400)
    replication = TiDBReplicationRuntime(
        ticdc_image=TICDC_V8_1_0,
        downstream_image=MYSQL_8_4,
        ticdc_cpu_limit=1.0,
        ticdc_memory_mb=1024,
        downstream_cpu_limit=0.5,
        downstream_memory_mb=1024,
        ticdc_count=2,
    )
    monkeypatch.setattr(
        "src.execution.host_ports._bindable", lambda port: port >= 4407,
    )
    try:
        deployment.configure_runtime(
            _runtime(pd_count=1, tikv_count=1, tidb_count=1, replication=replication)
        )
        assert deployment.port_base == 4412
        assert deployment.prometheus_port == 4414
        assert deployment.downstream_port == 4415
        assert deployment.ticdc_ports == {"ticdc/ticdc-0": 4416, "ticdc/ticdc-1": 4417}
    finally:
        deployment._port_lease.close()
        shutil.rmtree(deployment.runtime_dir)


def test_cluster_start_retry_resets_partial_deployment(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="cluster-start-retry", port_base=4500)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    deployment._env["DOCKER_ROOT_DIR"] = "/tmp/docker-root"
    commands = []
    database_start_attempts = {"count": 0}

    def flaky_start_database_services():
        database_start_attempts["count"] += 1
        if database_start_attempts["count"] == 1:
            raise RuntimeError("TiDB service stopped during readiness: stage='pd', service='pd-0'")

    monkeypatch.setattr(deployment, "_start_database_services", flaky_start_database_services)
    monkeypatch.setattr(deployment, "_start_replication_services", lambda: None)
    monkeypatch.setattr(deployment, "_apply_worker_numa_binding", lambda: None)
    monkeypatch.setattr(deployment, "_wait", lambda label, check, timeout: None)
    monkeypatch.setattr(
        deployment,
        "_run",
        lambda cmd, component="cluster": commands.append((tuple(cmd), component)) or "",
    )
    deployment._network_created = True
    ensure_calls = []
    monkeypatch.setattr(deployment, "_ensure_network", lambda: ensure_calls.append(True))
    try:
        try:
            deployment._start_cluster()
        except RuntimeError as first_error:
            deployment._retry_cluster_start(first_error)
        assert database_start_attempts["count"] == 2
        # Each start (initial and retry) ensures the network; the reset removed it.
        assert ensure_calls == [True, True]
        assert any(
            cmd[-3:] == ("down", "--volumes", "--remove-orphans") and component == "deployment-retry"
            for cmd, component in commands
        )
        # A bootstrap-cache miss wipes the dirty data directories for a fresh bootstrap.
        for destination in deployment.snapshots.bootstrap_data_paths.values():
            assert os.path.isdir(destination) and not os.listdir(destination)
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_cluster_start_retry_failure_wraps_first_error(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="cluster-start-retry-failed", port_base=4500)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    deployment._env["DOCKER_ROOT_DIR"] = "/tmp/docker-root"

    def always_fail():
        raise RuntimeError("TiKV store heartbeat stalled again")

    monkeypatch.setattr(deployment, "_start_cluster", always_fail)
    monkeypatch.setattr(deployment, "_run", lambda cmd, component="cluster": "")
    try:
        with pytest.raises(RuntimeError, match="cluster start retry failed") as error:
            deployment._retry_cluster_start(RuntimeError("first: DNS server misbehaving"))
        assert "first: DNS server misbehaving" in str(error.value)
        assert "TiKV store heartbeat stalled again" in str(error.value.__cause__)
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_cluster_start_retry_skipped_for_persistent_storage(monkeypatch):
    deployment = TiDBDockerDeployment(
        run_id="cluster-start-retry-persistent", port_base=4500,
        storage_key="retry-key", storage_root="/tmp/aiopsbench-retry-storage",
    )
    monkeypatch.setattr(
        TiDBSnapshots,
        "persistent_storage_enabled",
        property(lambda self: True),
    )
    first_error = RuntimeError("readiness timeout")
    with pytest.raises(RuntimeError) as error:
        deployment._retry_cluster_start(first_error)
    assert error.value is first_error


def test_cluster_start_reset_restores_bootstrap_cache_data(tmp_path, monkeypatch):
    deployment = TiDBDockerDeployment(run_id="cluster-start-reset-cache", port_base=4600)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    deployment._env["DOCKER_ROOT_DIR"] = "/tmp/docker-root"
    cache_dir = tmp_path / "cache"
    for node_type, service in deployment.snapshots.bootstrap_data_paths:
        blob = cache_dir / node_type / service
        blob.mkdir(parents=True)
        (blob / "payload").write_text("cached")
    monkeypatch.setattr(deployment.snapshots, "bootstrap_cache_used", True)
    monkeypatch.setattr(deployment.snapshots, "bootstrap_cache_path", str(cache_dir))
    monkeypatch.setattr(deployment, "_run", lambda cmd, component="cluster": "")
    dirty_destination = next(iter(deployment.snapshots.bootstrap_data_paths.values()))
    with open(os.path.join(dirty_destination, "stale"), "w", encoding="utf-8") as handle:
        handle.write("dirty")
    try:
        deployment._reset_partial_cluster()
        for destination in deployment.snapshots.bootstrap_data_paths.values():
            assert sorted(os.listdir(destination)) == ["payload"]
    finally:
        shutil.rmtree(deployment.runtime_dir)


class _FakeHttpResponse:
    def __init__(self, body: bytes):
        self.status = 200
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


def test_prometheus_readiness_requires_database_service_samples(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="prometheus-sample-gate", port_base=4700)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(deployment, "_prometheus_expected_target_count", lambda: 2)

    def fake_urlopen(url, timeout):
        if "/-/ready" in url:
            return _FakeHttpResponse(b"")
        if "query=up" in url:
            targets = {"data": {"result": [
                {"metric": {"instance": "pd-0:2379"}, "value": [0, "1"]},
                {"metric": {"instance": "cadvisor-0:8080"}, "value": [0, "1"]},
            ]}}
            return _FakeHttpResponse(json.dumps(targets).encode())
        return _FakeHttpResponse(json.dumps({"data": {"result": []}}).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    try:
        with pytest.raises(RuntimeError, match="no container samples yet") as error:
            deployment._check_prometheus()
        assert "'pd-0'" in str(error.value)
        assert "'tikv-0'" in str(error.value)
        assert "'tidb-0'" in str(error.value)
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_prometheus_readiness_passes_once_service_samples_exist(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="prometheus-sample-ok", port_base=4700)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(deployment, "_prometheus_expected_target_count", lambda: 2)

    def fake_urlopen(url, timeout):
        if "/-/ready" in url:
            return _FakeHttpResponse(b"")
        if "query=up" in url:
            targets = {"data": {"result": [
                {"metric": {"instance": "pd-0:2379"}, "value": [0, "1"]},
                {"metric": {"instance": "cadvisor-0:8080"}, "value": [0, "1"]},
            ]}}
            return _FakeHttpResponse(json.dumps(targets).encode())
        series = {"data": {"result": [
            {"metric": {"container_label_com_docker_compose_service": service}, "value": [0, "1"]}
            for service in ("pd-0", "tikv-0", "tidb-0")
        ]}}
        return _FakeHttpResponse(json.dumps(series).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    try:
        deployment._check_prometheus()
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_prometheus_readiness_tolerates_discovery_lag_within_grace(monkeypatch, capsys):
    deployment = TiDBDockerDeployment(run_id="prometheus-discovery-lag", port_base=4700)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(deployment, "_prometheus_expected_target_count", lambda: 3)

    def fake_urlopen(url, timeout):
        if "/-/ready" in url:
            return _FakeHttpResponse(b"")
        if "query=up" in url:
            targets = {"data": {"result": [
                {"metric": {"instance": "pd-0:2379"}, "value": [0, "1"]},
                {"metric": {"instance": "cadvisor-0:8080"}, "value": [0, "1"]},
            ]}}
            return _FakeHttpResponse(json.dumps(targets).encode())
        return _FakeHttpResponse(json.dumps({"data": {"result": []}}).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    try:
        # First observation starts the grace window instead of failing.
        deployment._check_prometheus()
        assert deployment._prometheus_shortfall_since is not None
        assert "service discovery lag" in capsys.readouterr().out

        # A shortfall that outlives the grace window still surfaces.
        deployment._prometheus_shortfall_since = time.monotonic() - (
            deployment.PROMETHEUS_DISCOVERY_GRACE_SECONDS + 1
        )
        with pytest.raises(RuntimeError, match="Prometheus targets not ready: expected=3, actual=2"):
            deployment._check_prometheus()
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_prometheus_readiness_clears_discovery_grace_when_targets_match(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="prometheus-discovery-recovered", port_base=4700)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    monkeypatch.setattr(deployment, "_prometheus_expected_target_count", lambda: 2)

    def fake_urlopen(url, timeout):
        if "/-/ready" in url:
            return _FakeHttpResponse(b"")
        if "query=up" in url:
            targets = {"data": {"result": [
                {"metric": {"instance": "pd-0:2379"}, "value": [0, "1"]},
                {"metric": {"instance": "cadvisor-0:8080"}, "value": [0, "1"]},
            ]}}
            return _FakeHttpResponse(json.dumps(targets).encode())
        series = {"data": {"result": [
            {"metric": {"container_label_com_docker_compose_service": service}, "value": [0, "1"]}
            for service in ("pd-0", "tikv-0", "tidb-0")
        ]}}
        return _FakeHttpResponse(json.dumps(series).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    deployment._prometheus_shortfall_since = time.monotonic()
    try:
        deployment._check_prometheus()
        assert deployment._prometheus_shortfall_since is None
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_prometheus_readiness_timeout_counts_case_owned_targets():
    deployment = TiDBDockerDeployment(run_id="case-owned-prometheus-timeout", port_base=4700)
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=2, tidb_count=3))
    try:
        assert deployment._prometheus_readiness_timeout() == 120
        deployment.enable_lightning_scrape_target("lightning-case-owned:8287")
        deployment._render_runtime_files()
        # The Lightning job lands in the same rendered scrape configuration
        # the readiness check counts, so the budget scales with it.
        assert deployment._prometheus_readiness_timeout() == 130
    finally:
        shutil.rmtree(deployment.runtime_dir)


def test_prometheus_services_fresh_requires_monitoring_and_filesystem_samples(monkeypatch):
    import io
    import urllib.parse

    deployment = TiDBDockerDeployment(run_id="fresh-monitoring-services")
    deployment.configure_runtime(_runtime(pd_count=1, tikv_count=1, tidb_count=1))
    deployment.prometheus_port = 41290

    def install(monkeypatch, *, monitoring, filesystem):
        def fake_urlopen(url, timeout):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["query"][0]
            if "container_fs_reads_bytes_total" in query:
                services = ["pd-0"] if filesystem else []
            else:
                services = ["pd-0", "tikv-0", "tidb-0"]
                services += ["prometheus", "cadvisor"] if monitoring else []
            payload = json.dumps({"data": {"result": [
                {"metric": {"container_label_com_docker_compose_service": service}, "value": [0, "1"]}
                for service in services
            ]}}).encode()
            return io.BytesIO(payload)

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    try:
        install(monkeypatch, monitoring=False, filesystem=True)
        assert deployment.prometheus_services_fresh(30) is False

        install(monkeypatch, monitoring=True, filesystem=False)
        assert deployment.prometheus_services_fresh(30) is False

        install(monkeypatch, monitoring=True, filesystem=True)
        assert deployment.prometheus_services_fresh(30) is True
    finally:
        shutil.rmtree(deployment.runtime_dir)
