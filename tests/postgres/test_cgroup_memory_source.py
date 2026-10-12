import subprocess
from types import SimpleNamespace

import pytest

import src.execution.environment as environment
from src.execution.environment import PGEnv

CONTAINER_ID = "3f2a9c" + "0" * 58


@pytest.fixture
def host(tmp_path, monkeypatch):
    """A host /proc and cgroup v2 tree, and a Docker CLI that answers for one container."""
    proc = tmp_path / "proc"
    cgroup = tmp_path / "cgroup"
    monkeypatch.setattr(environment, "HOST_PROC_ROOT", str(proc))
    monkeypatch.setattr(environment, "HOST_CGROUP_ROOT", str(cgroup))

    # The root cgroup of a v2 host: memory.stat for the whole machine, no memory.current or memory.max.
    cgroup.mkdir()
    (cgroup / "memory.stat").write_text("anon 1\ninactive_file 2500000000\n")
    container_dir = cgroup / "docker" / CONTAINER_ID
    container_dir.mkdir(parents=True)
    (container_dir / "memory.current").write_text("300000000\n")
    (container_dir / "memory.max").write_text("536870912\n")
    (container_dir / "memory.stat").write_text("anon 1\ninactive_file 100000000\n")

    inside = {
        "/sys/fs/cgroup/cgroup.controllers": "cpu memory\n",
        "/sys/fs/cgroup/memory.current": "60000000\n",
        "/sys/fs/cgroup/memory.max": "536870912\n",
        "/sys/fs/cgroup/memory.stat": "anon 1\ninactive_file 20000000\n",
    }
    reported_pid = {"value": "4242"}

    def run(cmd, *args, **kwargs):
        if cmd[:2] == ["docker", "inspect"]:
            return subprocess.CompletedProcess(cmd, 0, stdout=f"{CONTAINER_ID} {reported_pid['value']}\n", stderr="")
        if cmd[:2] == ["docker", "exec"]:
            return subprocess.CompletedProcess(cmd, 0, stdout=inside[cmd[-1]], stderr="")
        raise AssertionError(f"unexpected command {cmd!r}")

    monkeypatch.setattr(subprocess, "run", run)

    def process(pid, cgroup_path):
        (proc / pid).mkdir(parents=True)
        (proc / pid / "cgroup").write_text(f"0::{cgroup_path}\n")
        reported_pid["value"] = pid

    return SimpleNamespace(process=process)


def make_env():
    env = PGEnv.__new__(PGEnv)
    env.deployment = SimpleNamespace(container_name="pg")
    env._host_cgroup_base = None
    env._cgroup_v2 = None
    return env


def test_reads_the_container_cgroup_on_the_host_when_the_pid_is_the_container(host):
    host.process("4242", f"/docker/{CONTAINER_ID}")
    env = make_env()

    # (300000000 - 100000000) / 536870912
    assert env._sample_memory() == 37.3
    assert env._host_cgroup_base.endswith(f"docker/{CONTAINER_ID}")


def test_a_host_process_in_the_root_cgroup_with_the_container_pid_is_not_read(host):
    # Docker Desktop reports the PID from its own VM; here a host process carries the same number.
    host.process("4242", "/")
    env = make_env()

    # Every counter comes from inside the container: (60000000 - 20000000) / 536870912.
    assert env._sample_memory() == 7.5
    assert env._host_cgroup_base is None


def test_a_host_process_in_another_cgroup_with_the_container_pid_is_not_read(host, tmp_path):
    other = tmp_path / "cgroup" / "init.scope"
    other.mkdir()
    (other / "memory.current").write_text("7000000\n")
    (other / "memory.max").write_text("max\n")
    (other / "memory.stat").write_text("anon 1\ninactive_file 400000\n")
    host.process("4242", "/init.scope")
    env = make_env()

    assert env._sample_memory() == 7.5
    assert env._host_cgroup_base is None
