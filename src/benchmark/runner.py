from __future__ import annotations

import hashlib
import json
import os
import platform
import signal
import subprocess
import sys
import time
import threading
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from src.agent_language import AGENT_LANGUAGE_ENV
from .adapters.persistent_scenario import build_persistent_scenario_command
from .adapters.scenario import build_scenario_command, validate_scenario_target, assert_fault_snapshots_exist
from .commands import container_name
from .aggregate import aggregate, write_aggregate
from .isolation import (
    allocate_workers,
    derive_worker_demand,
    requires_host_exclusive,
)
from .host_resources import reserve_host_resources
from src.execution.host_ports import PORT_LEASE_ENV, PortLease, reserve_host_ports
from .manifest import ExperimentManifest
from .models import (
    BoundedScenarioRunSpec,
    PersistentScenarioRunSpec,
    RunRecord,
    ScenarioKind,
    WorkerAllocation,
)
from .store import ExperimentStore, atomic_write_json


# Run the entrypoint and capture the source state from the active checkout.
# Artifact roots remain shared through src.project_paths, but linked worktrees
# must not execute an older script from the main checkout.
# Linked worktrees share the Git common directory for artifacts, but commands
# must execute the entrypoint and source files from the active checkout.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _classify_process_failure(stdout_path: Path) -> tuple[str, str]:
    """Preserve known pre-agent admission failures as infrastructure events."""
    try:
        output = stdout_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "scenario_process", "Scenario process exited with a non-zero status"
    marker = "PG-RG-PC01 admission blocker:"
    if marker in output:
        summary = output.rsplit(marker, 1)[-1].splitlines()[0].strip()
        return "admission", f"{marker} {summary}"
    marker = "MODEL-LOOP-ABORT:"
    if marker in output:
        summary = output.rsplit(marker, 1)[-1].splitlines()[0].strip()
        return "model_failure", f"{marker} {summary}"
    marker = "PG-RG-MF01 replay infrastructure:"
    if marker in output:
        summary = output.rsplit(marker, 1)[-1].splitlines()[0].strip()
        return "evaluator", f"{marker} {summary}"
    marker = "LTX-FIXTURE-MISSING:"
    if marker in output:
        summary = output.rsplit(marker, 1)[-1].splitlines()[0].strip()
        return "fixture_missing", f"{marker} {summary}"
    if "LLM API 调用失败" in output:
        lines = [line.strip() for line in output.splitlines() if "LLM API 调用失败" in line or "413 Request Entity Too Large" in line]
        summary = " ".join(lines[-2:])
        return "provider", summary or "LLM API 调用失败"
    if "protocol error" in output.lower() or "malformed response" in output.lower():
        return "protocol", "Agent/provider protocol error or malformed response"
    # 只认供应商配额/限流的明确签名；裸 "quota"/"rate limit" 会命中场景工具
    # schema 描述（如 disk_quota_mb、storage.io-rate-limit），全是误报
    if ("insufficient_user_quota" in output or "AccountQuotaExceeded" in output
            or "error code: 429" in output or "Request too large" in output):
        return "quota", "Provider quota or rate limit exceeded"
    if "dsdgen not found" in output and "Cloning tpcds-kit repository" in output:
        return "workload_setup", "TPC-DS workload bootstrap failed while preparing tpcds-kit"
    if "Dataset init SQL hash differs from manifest" in output:
        return "workload_setup", "Dataset artifact hash does not match the frozen manifest"
    return "scenario_process", "Scenario process exited with a non-zero status"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _command_container_name(command: list[str]) -> str | None:
    if "--container-name" not in command:
        return None
    index = command.index("--container-name") + 1
    if index >= len(command) or not command[index]:
        raise ValueError(f"Scenario command has an empty container name: command={command!r}")
    return command[index]


def _command_published_port(command: list[str], flag: str) -> int | None:
    if flag not in command:
        return None
    index = command.index(flag) + 1
    if index >= len(command):
        raise ValueError(f"Scenario command has no value for {flag}: command={command!r}")
    return int(command[index])


def _discover_container_name(command: list[str]) -> str | None:
    port = _command_published_port(command, "--primary-port")
    if port is None:
        port = _command_published_port(command, "--port")
    if port is None:
        return None
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"publish={port}", "--format", "{{.Names}}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Docker primary-port discovery failed: port={port}, stderr={result.stderr.strip()!r}"
        )
    matches = sorted(line for line in result.stdout.splitlines() if line)
    return matches[0] if matches else None


def _docker_inspect(container_name: str) -> dict[str, object] | None:
    names = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name=^{container_name}", "--format", "{{.Names}}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if names.returncode != 0:
        raise RuntimeError(
            f"Docker container namespace query failed: namespace={container_name!r}, stderr={names.stderr.strip()!r}"
        )
    matches = sorted(line for line in names.stdout.splitlines() if line)
    if not matches:
        return None
    primary = next((name for name in matches if name == container_name or name.endswith("-primary")), matches[0])
    result = subprocess.run(["docker", "inspect", primary], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"Docker inspect failed after namespace match: namespace={container_name!r}, container={primary!r}, stderr={result.stderr.strip()!r}"
        )
    payload = json.loads(result.stdout)
    if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
        raise RuntimeError(
            f"Docker inspect returned an invalid payload: container={primary!r}, output={result.stdout!r}"
        )
    return payload[0]


def _runtime_evidence_pending(worker: WorkerAllocation | None, resources: object | None, container_name: str | None) -> dict[str, object]:
    return {
        "status": "pending",
        "worker_id": worker.id if worker else None,
        "physical_cores": list(worker.physical_cores) if worker else [],
        "cpuset_cpus": worker.cpuset_cpus if worker else None,
        "cpuset_mems": worker.cpuset_mems if worker else None,
        "worker_cpu_capacity": worker.cpu_capacity if worker else None,
        "worker_memory_capacity_mb": worker.memory_capacity_mb if worker else None,
        "container_cpu_limit": getattr(resources, "container_cpu_limit", None),
        "container_memory_mb": getattr(resources, "container_memory_mb", None),
        "container_name": container_name,
    }


def _capture_runtime_evidence(
    pending: dict[str, object],
    *,
    process: subprocess.Popen,
    timeout_seconds: float = 60.0,
) -> dict[str, object]:
    container_name = pending["container_name"]
    if container_name is None:
        return {**pending, "status": "incomplete", "error": "Run command has no Docker container name", "captured_at": now_iso()}
    container_name = str(container_name)
    deadline = time.monotonic() + timeout_seconds
    inspect = None
    while time.monotonic() < deadline:
        try:
            inspect = _docker_inspect(container_name)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            return {**pending, "status": "incomplete", "error": f"Docker inspect failed: container={container_name!r}, error={exc}", "captured_at": now_iso()}
        if inspect is not None:
            break
        if process.poll() is not None:
            break
        time.sleep(0.25)
    if inspect is None:
        return {**pending, "status": "incomplete", "error": f"Docker inspect unavailable: container={container_name!r}", "captured_at": now_iso()}
    host = inspect.get("HostConfig")
    if not isinstance(host, dict):
        raise RuntimeError(f"Docker inspect has no HostConfig: container={container_name!r}")
    actual = {
        "docker_runtime": host.get("Runtime"),
        "cpuset_cpus": host.get("CpusetCpus"),
        "cpuset_mems": host.get("CpusetMems"),
        "nano_cpus": host.get("NanoCpus"),
        "memory_bytes": host.get("Memory"),
        "container_name": str(inspect.get("Name", "")).lstrip("/"),
    }
    if actual["cpuset_cpus"] != pending["cpuset_cpus"] or actual["cpuset_mems"] != pending["cpuset_mems"]:
        return {**pending, **actual, "status": "incomplete", "error": f"Docker cpuset mismatch: declared={pending['cpuset_cpus']!r}/{pending['cpuset_mems']!r}, actual={actual['cpuset_cpus']!r}/{actual['cpuset_mems']!r}", "captured_at": now_iso()}
    expected_nano = (
        int(float(pending["container_cpu_limit"]) * 1_000_000_000)
        if pending["container_cpu_limit"] is not None
        else None
    )
    expected_memory = (
        int(pending["container_memory_mb"]) * 1024 * 1024
        if pending["container_memory_mb"] is not None
        else None
    )
    if (
        (expected_nano is not None and actual["nano_cpus"] != expected_nano)
        or (expected_memory is not None and actual["memory_bytes"] != expected_memory)
    ):
        return {**pending, **actual, "status": "incomplete", "error": f"Docker resource mismatch: declared={expected_nano}/{expected_memory}, actual={actual['nano_cpus']!r}/{actual['memory_bytes']!r}", "captured_at": now_iso()}
    return {**pending, **actual, "status": "complete", "captured_at": now_iso()}


def _capture_cleanup_evidence(container_name: str | None) -> dict[str, object]:
    if container_name is None:
        return {"status": "incomplete", "error": "Run command has no Docker container name", "checked_at": now_iso()}
    def names(args: list[str]) -> list[str]:
        result = subprocess.run(["docker", *args], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"Docker cleanup query failed: command={args!r}, stderr={result.stderr.strip()!r}")
        return sorted(line for line in result.stdout.splitlines() if line)

    try:
        containers = names(["ps", "-a", "--filter", f"name=^{container_name}", "--format", "{{.Names}}"])
        volumes = [name for name in names(["volume", "ls", "--format", "{{.Name}}"]) if name.startswith(container_name)]
        networks = [name for name in names(["network", "ls", "--format", "{{.Name}}"]) if name.startswith(container_name)]
    except RuntimeError as exc:
        return {"status": "incomplete", "container_name": container_name, "error": str(exc), "checked_at": now_iso()}
    return {
        "status": "complete" if not (containers or volumes or networks) else "incomplete",
        "container_present": bool(containers),
        "remaining_task_containers": ",".join(containers),
        "remaining_task_volumes": ",".join(volumes),
        "remaining_task_networks": ",".join(networks),
        "checked_at": now_iso(),
    }


def environment_snapshot(
    manifest: ExperimentManifest,
    workers: tuple[WorkerAllocation, ...],
) -> dict:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True
    ).strip()
    git_status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=PROJECT_ROOT, text=True
    ).splitlines()
    diff = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=PROJECT_ROOT)
    docker_version = subprocess.check_output(
        ["docker", "version", "--format", "{{.Server.Version}}"],
        cwd=PROJECT_ROOT,
        text=True,
    ).strip()
    dependencies = subprocess.check_output(
        [sys.executable, "-m", "pip", "freeze"],
        cwd=PROJECT_ROOT,
        text=True,
    ).splitlines()
    configured_llm_path = Path(manifest.runtime.llm_config)
    llm_config = (
        configured_llm_path
        if configured_llm_path.is_absolute()
        else (PROJECT_ROOT / configured_llm_path).resolve()
    )
    return {
        "git_commit": commit,
        "git_dirty": bool(git_status),
        "git_status": git_status,
        "git_diff_sha256": hashlib.sha256(diff).hexdigest(),
        "manifest_sha256": _sha256(manifest.source_path),
        "llm_config_path": str(configured_llm_path),
        "llm_config_sha256": (
            _sha256(llm_config)
            if any(agent.mode in {"llm", "v-expel", "dbot", "dbaiops"} for agent in manifest.agents)
            else None
        ),
        "docker_server_version": docker_version,
        "python": sys.version,
        "dependencies": dependencies,
        "platform": platform.platform(),
        "workers": [asdict(worker) for worker in workers],
        "captured_at": now_iso(),
    }


def build_command(
    spec: BoundedScenarioRunSpec | PersistentScenarioRunSpec,
    manifest: ExperimentManifest,
    *,
    attempt: int | None = None,
) -> list[str]:
    if isinstance(spec, PersistentScenarioRunSpec):
        return build_persistent_scenario_command(spec, manifest, PROJECT_ROOT)
    return build_scenario_command(spec, manifest, PROJECT_ROOT, attempt=attempt)


def _isolate_scenario_attempt(
    command: list[str],
    spec: BoundedScenarioRunSpec | PersistentScenarioRunSpec,
    manifest: ExperimentManifest,
    attempt: int,
) -> list[str]:
    if attempt <= 1 or isinstance(spec, PersistentScenarioRunSpec) or "--container-name" not in command:
        return command
    index = command.index("--container-name") + 1
    isolated = list(command)
    isolated[index] = container_name(
        manifest.runtime.container_prefix,
        f"{spec.run_id}-a{attempt:03d}",
    )
    return isolated


_PORT_FLAGS = (
    "--port",
    "--primary-port",
    "--restore-port",
    "--pgbouncer-port",
    "--aux-port",
    "--monitoring-port",
)


def validate_execution_plan(
    manifest: ExperimentManifest,
    specs: list[BoundedScenarioRunSpec | PersistentScenarioRunSpec],
) -> tuple[WorkerAllocation, ...]:
    for spec in specs:
        build_command(spec, manifest)
        if isinstance(spec, BoundedScenarioRunSpec):
            validate_scenario_target(spec, manifest)
    if manifest.benchmark.scenario_kind is ScenarioKind.PERSISTENT:
        if manifest.runtime.concurrency != 1:
            raise ValueError("Persistent Scenario experiment execution requires runtime.concurrency=1")
        if manifest.runtime.isolation is None:
            return ()
        demand = derive_worker_demand(specs, manifest.runtime.isolation)
        return allocate_workers(
            demand,
            manifest.runtime.concurrency,
            cpuset_cpus=manifest.runtime.isolation.cpuset_cpus,
        )
    if manifest.runtime.fault_snapshot == "use":
        assert_fault_snapshots_exist(specs)
    if manifest.runtime.isolation is None:
        return ()
    demand = derive_worker_demand(
        specs,
        manifest.runtime.isolation,
        allow_missing_resources=manifest.runtime.concurrency == 1,
    )
    return allocate_workers(
        demand,
        manifest.runtime.concurrency,
        cpuset_cpus=manifest.runtime.isolation.cpuset_cpus,
    )






class ExperimentRunner:
    def __init__(
        self,
        manifest: ExperimentManifest,
        store: ExperimentStore,
        workers: tuple[WorkerAllocation, ...] = (),
    ):
        self.manifest = manifest
        self.store = store
        self.workers = workers
        if manifest.runtime.isolation is None and workers:
            raise ValueError("Benchmark workers require manifest.runtime.isolation")
        if manifest.runtime.isolation is not None and len(workers) != manifest.runtime.concurrency:
            raise ValueError(
                "Benchmark worker count must equal runtime.concurrency: "
                f"workers={len(workers)}, concurrency={manifest.runtime.concurrency}"
            )
        self.stopping = False
        self._processes: dict[str, subprocess.Popen] = {}
        self._process_lock = threading.Lock()
        self._reservation_fds: tuple[int, ...] = ()

    def initialize(self, specs: list[BoundedScenarioRunSpec | PersistentScenarioRunSpec]) -> None:
        self.store.initialize(
            self.manifest.raw,
            environment_snapshot(self.manifest, self.workers),
        )
        for spec in specs:
            record = self.store.load(spec.run_id)
            if record is None:
                self.store.save(RunRecord.from_spec(spec))
            elif record.status == "running":
                record.status = "interrupted"
                record.finished_at = now_iso()
                record.failure_category = "interrupted"
                record.error = "Previous process ended before recording a terminal status"
                self.store.save(record)

    def run(self, specs: list[BoundedScenarioRunSpec | PersistentScenarioRunSpec], rerun: set[str]) -> int:
        selected = []
        for spec in specs:
            record = self.store.load(spec.run_id)
            assert record is not None
            measurement_incomplete = (
                record.runtime_evidence.get("status") != "complete"
                or record.cleanup_evidence.get("status") != "complete"
            )
            if (
                record.status == "pending"
                or record.status in rerun
                or ("measurement" in rerun and measurement_incomplete)
            ):
                selected.append(spec)
        if not selected:
            print(f"Experiment {self.manifest.experiment_id}: no runs selected")
            return 0

        previous_handlers = {}
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, self._request_stop)
        try:
            with reserve_host_resources(
                self.manifest.experiment_id, selected, self.manifest.runtime.isolation,
                self.manifest.runtime.concurrency,
                run_records=tuple(self.store.record_path(spec.run_id) for spec in selected),
            ) as reservation:
                self.workers = reservation.workers
                self._reservation_fds = reservation.pass_fds
                atomic_write_json(self.store.root / "host-reservation.json", reservation.evidence)
                environment_path = self.store.root / "environment.json"
                environment = json.loads(environment_path.read_text())
                environment["workers"] = [asdict(worker) for worker in self.workers]
                atomic_write_json(environment_path, environment)
                try:
                    failures = self._run_selected(selected)
                finally:
                    self._reservation_fds = ()
        finally:
            for signum, handler in previous_handlers.items():
                signal.signal(signum, handler)
            write_aggregate(self.store.root, aggregate(self.store.records()))
        return 1 if failures else 0

    def _request_stop(self, signum, frame) -> None:
        self.stopping = True
        print(f"Received signal {signum}; no new runs will start", file=sys.stderr)
        with self._process_lock:
            processes = list(self._processes.values())
        for process in processes:
            try:
                # Allow the child to enter its finally block and tear down resources.
                os.killpg(process.pid, signal.SIGINT)
            except ProcessLookupError:
                continue

    @staticmethod
    def _terminate_process_group(process: subprocess.Popen, grace_seconds: float = 10.0) -> None:
        try:
            os.killpg(process.pid, signal.SIGINT)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=grace_seconds)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=5.0)

    def _run_selected(self, specs: list[BoundedScenarioRunSpec | PersistentScenarioRunSpec]) -> int:
        parallel = self.manifest.runtime.concurrency > 1
        failures = 0
        pending_by_scenario: dict[str, deque[BoundedScenarioRunSpec | PersistentScenarioRunSpec]] = {}
        for spec in specs:
            queue_key = spec.scenario_id if isinstance(spec, BoundedScenarioRunSpec) else f"persistent_scenario:{spec.scenario_id}"
            pending_by_scenario.setdefault(queue_key, deque()).append(spec)
        ready_scenarios = deque(pending_by_scenario)
        available_workers: deque[WorkerAllocation | None] = deque(
            self.workers or (None,)
        )

        with ThreadPoolExecutor(max_workers=self.manifest.runtime.concurrency) as executor:
            futures = {}

            def next_compatible_spec() -> BoundedScenarioRunSpec | PersistentScenarioRunSpec | None:
                for offset, scenario_id in enumerate(ready_scenarios):
                    spec = pending_by_scenario[scenario_id][0]
                    if futures and parallel and requires_host_exclusive(spec):
                        continue
                    ready_scenarios.rotate(-offset)
                    ready_scenarios.popleft()
                    ready_scenarios.rotate(offset)
                    return pending_by_scenario[scenario_id].popleft()
                return None

            def submit_ready() -> None:
                while (
                    ready_scenarios
                    and available_workers
                    and not self.stopping
                ):
                    spec = next_compatible_spec()
                    if spec is None:
                        return
                    host_exclusive = parallel and requires_host_exclusive(spec)
                    worker = available_workers.popleft()
                    futures[executor.submit(self._execute, spec, worker)] = (spec, worker)
                    if host_exclusive:
                        return

            submit_ready()
            while futures:
                completed, _ = wait(futures, return_when=FIRST_COMPLETED)
                for future in completed:
                    spec, worker = futures.pop(future)
                    record = future.result()
                    if record.status != "succeeded":
                        failures += 1
                    available_workers.append(worker)
                    queue_key = spec.scenario_id if isinstance(spec, BoundedScenarioRunSpec) else f"persistent_scenario:{spec.scenario_id}"
                    if pending_by_scenario[queue_key]:
                        ready_scenarios.append(queue_key)
                submit_ready()
        return failures

    def _execute(
        self,
        spec: BoundedScenarioRunSpec | PersistentScenarioRunSpec,
        worker: WorkerAllocation | None = None,
    ) -> RunRecord:
        if self.stopping:
            record = self.store.load(spec.run_id)
            assert record is not None
            return record
        command = build_command(spec, self.manifest)
        base_flag = '--primary-port' if '--primary-port' in command else '--port'
        base = int(command[command.index(base_flag) + 1])
        flags = {flag: int(command[command.index(flag) + 1]) - base for flag in _PORT_FLAGS if flag in command}
        offsets = tuple(sorted(set(spec.host_ports.offsets) | set(flags.values())))
        with reserve_host_ports(base, offsets, owner=spec.run_id,
                                allowed_range=spec.host_ports.allowed_range) as ports:
            shift = min(ports.ports) - base - min(offsets)
            for flag in flags:
                command[command.index(flag) + 1] = str(base + shift + flags[flag])
            return self._execute_reserved(spec, worker, command, ports)

    def _execute_reserved(
        self,
        spec: BoundedScenarioRunSpec | PersistentScenarioRunSpec,
        worker: WorkerAllocation | None,
        command: list[str],
        ports: PortLease,
    ) -> RunRecord:
        record = self.store.load(spec.run_id)
        assert record is not None
        if self.stopping:
            return record
        record.attempt += 1
        attempt = record.attempt
        attempt_dir = self.store.attempt_dir(spec.run_id, attempt)
        stdout_path = attempt_dir / "stdout.log"
        trace_path = attempt_dir / ("persistent_scenario_trace.json" if isinstance(spec, PersistentScenarioRunSpec) else "trace.json")
        evaluator_path = attempt_dir / ("persistent_scenario_evaluation.json" if isinstance(spec, PersistentScenarioRunSpec) else "evaluator.json")
        command = _isolate_scenario_attempt(
            command,
            spec,
            self.manifest,
            attempt,
        )
        base_flag = '--primary-port' if '--primary-port' in command else '--port'
        record.port = int(command[command.index(base_flag) + 1])
        atomic_write_json(attempt_dir / 'port-reservation.json', {'ports': ports.ports})

        record.status = "running"
        record.run_status = "pending"
        record.timeout_seconds = self.manifest.runtime.timeout_seconds
        record.started_at = now_iso()
        record.finished_at = None
        record.failure_category = None
        record.error = None
        record.diagnosis_pass = None
        record.outcome_pass = None
        record.safe_pass = None
        record.evaluator = None
        record.case_no = None
        record.valid_for_aggregate = False
        record.evaluation = {}
        record.service_objectives_pass = None
        record.data_integrity_pass = None
        record.required_state_pass = None
        record.command = command
        container_name = _command_container_name(command)
        record.worker_id = worker.id if worker else None
        record.physical_cores = worker.physical_cores if worker else ()
        record.cpuset_cpus = worker.cpuset_cpus if worker else None
        record.cpuset_mems = worker.cpuset_mems if worker else None
        record.worker_cpu_capacity = worker.cpu_capacity if worker else None
        record.worker_memory_capacity_mb = worker.memory_capacity_mb if worker else None
        resources = spec.resources
        if worker and resources is None and self.manifest.runtime.concurrency != 1:
            raise ValueError(
                "Parallel benchmark worker execution requires an explicit case resource contract: "
                f"scenario_id={spec.scenario_id!r}, case_id={spec.case_id!r}"
            )
        container_cpu_limit = resources.container_cpu_limit if resources else 0.5
        container_memory_mb = resources.container_memory_mb if resources else 256
        record.container_cpu_limit = container_cpu_limit
        record.container_memory_mb = container_memory_mb
        record.runtime_evidence = _runtime_evidence_pending(worker, resources, container_name)
        record.cleanup_evidence = {"status": "pending", "container_name": container_name}
        record.stdout_path = os.path.relpath(stdout_path, PROJECT_ROOT)
        record.trace_path = os.path.relpath(trace_path, PROJECT_ROOT)
        record.evaluator_path = os.path.relpath(evaluator_path, PROJECT_ROOT)
        record.attempt_path = os.path.relpath(self.store.attempt_path(spec.run_id, attempt), PROJECT_ROOT)
        record.process_runtime_path = os.path.relpath(
            attempt_dir / "process-runtime.json", PROJECT_ROOT
        )
        record.runtime_audit_path = os.path.relpath(
            attempt_dir / "docker-runtime.json", PROJECT_ROOT
        )
        record.cleanup_audit_path = os.path.relpath(
            attempt_dir / "cleanup.json", PROJECT_ROOT
        )
        self.store.save(record)

        env = os.environ.copy()
        for key in (
            "AIOPS_WORKER_ID",
            "AIOPS_CPUSET_CPUS",
            "AIOPS_CPUSET_MEMS",
            "AIOPS_CPU_LIMIT",
            "AIOPS_MEMORY_MB",
            "AIOPS_REASONING_EFFORT",
        ):
            env.pop(key, None)
        env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        env.update({
            "AIOPS_DP_MATCH_MODE": self.manifest.runtime.diagnosis_match_mode,
            "AIOPS_DP_SEMANTIC_MODEL": self.manifest.runtime.diagnosis_semantic_model,
            "AIOPS_DP_SEMANTIC_CONFIG": self.manifest.runtime.llm_config,
            "AIOPS_EXPERIMENT_ID": spec.experiment_id,
            "AIOPS_RUN_ID": spec.run_id,
            "AIOPS_AGENT_ID": spec.agent.id,
            "AIOPS_AGENT_MODE": spec.agent.mode,
            "AIOPS_AGENT_SETTINGS": json.dumps(
                spec.agent.settings, ensure_ascii=True, sort_keys=True
            ),
            "AIOPS_RUN_TIMEOUT_SECONDS": str(self.manifest.runtime.timeout_seconds),
            AGENT_LANGUAGE_ENV: self.manifest.runtime.agent_language,
            "AIOPS_REPETITION": str(spec.repetition),
            "AIOPS_SEED": str(spec.seed),
            "AIOPS_TRACE_OUTPUT_DIR": str(attempt_dir),
            "AIOPS_TRACE_FILENAME": trace_path.name,
            "AIOPS_SCENARIO_KIND": (
                ScenarioKind.PERSISTENT.value
                if isinstance(spec, PersistentScenarioRunSpec)
                else ScenarioKind.BOUNDED.value
            ),
            "AIOPS_PROCESS_RUNTIME_PATH": str(attempt_dir / "process-runtime.json"),
            "AIOPS_RUNTIME_AUDIT_PATH": str(attempt_dir / "docker-runtime.json"),
            "AIOPS_CLEANUP_AUDIT_PATH": str(attempt_dir / "cleanup.json"),
        })
        if spec.agent.reasoning_effort is not None:
            env["AIOPS_REASONING_EFFORT"] = spec.agent.reasoning_effort
        env["AIOPS_LLM_USAGE_LOG"] = str(attempt_dir / "llm_usage_live.jsonl")
        if self.manifest.runtime.postgres_storage_root is not None:
            env["AIOPS_POSTGRES_STORAGE_ROOT"] = self.manifest.runtime.postgres_storage_root
        if isinstance(spec, PersistentScenarioRunSpec):
            env["AIOPS_SCENARIO_ID"] = spec.scenario_id
        else:
            env.update({
                "AIOPS_SCENARIO_ID": spec.scenario_id,
                "AIOPS_CASE_ID": spec.case_id,
            })
        if worker:
            env.update({
                "AIOPS_WORKER_ID": worker.id,
                "AIOPS_CPUSET_CPUS": worker.cpuset_cpus,
                "AIOPS_CPUSET_MEMS": worker.cpuset_mems,
                "AIOPS_CPU_LIMIT": str(container_cpu_limit),
                "AIOPS_MEMORY_MB": str(container_memory_mb),
            })
            command = [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "exec_bound_process.py"),
                "--cpuset-cpus",
                worker.cpuset_cpus,
                "--audit-path",
                str(attempt_dir / "process-runtime.json"),
                "--",
                *command,
            ]
        env[PORT_LEASE_ENV] = ports.process_environment
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        start = time.monotonic()
        with stdout_path.open("w", encoding="utf-8") as log:
            try:
                process = subprocess.Popen(
                    command,
                    cwd=PROJECT_ROOT,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    start_new_session=True,
                    pass_fds=self._reservation_fds + ports.pass_fds,
                )
            except OSError as exc:
                return self._finish_failed_start(record, attempt, start, exc)
            with self._process_lock:
                self._processes[spec.run_id] = process
            has_published_port = (
                _command_published_port(command, "--primary-port") is not None
                or _command_published_port(command, "--port") is not None
            )
            discovered_container_name = _discover_container_name(command)
            if discovered_container_name is not None:
                container_name = discovered_container_name
            elif has_published_port:
                container_name = None
                deadline = time.monotonic() + float(self.manifest.runtime.postgres_cold_start_timeout_sec)
                while container_name is None and process.poll() is None and time.monotonic() < deadline:
                    container_name = _discover_container_name(command)
                    if container_name is None:
                        time.sleep(0.25)
            record.runtime_evidence["container_name"] = container_name
            record.cleanup_evidence["container_name"] = container_name
            if container_name is not None:
                record.runtime_evidence = _capture_runtime_evidence(
                    record.runtime_evidence,
                    process=process,
                    timeout_seconds=float(self.manifest.runtime.postgres_cold_start_timeout_sec),
                )
            else:
                record.runtime_evidence = {
                    **record.runtime_evidence,
                    "status": "incomplete",
                    "error": "Run command has no Docker container name",
                    "captured_at": now_iso(),
                }
            self.store.save(record)
            try:
                return_code = process.wait(timeout=self.manifest.runtime.timeout_seconds)
                if self.stopping:
                    status = "interrupted"
                    category = "interrupted"
                    error = "Run was interrupted by SIGINT or SIGTERM"
                else:
                    status = "succeeded" if return_code == 0 else "failed"
                    if return_code == 0:
                        category = None
                        error = None
                    else:
                        category, error = _classify_process_failure(stdout_path)
                        error = f"{error} (exit code {return_code})"
            except subprocess.TimeoutExpired:
                self._terminate_process_group(process)
                return_code = process.returncode
                status = "timed_out"
                category = "timeout"
                error = f"Run exceeded timeout_seconds={self.manifest.runtime.timeout_seconds}"
            finally:
                with self._process_lock:
                    self._processes.pop(spec.run_id, None)

        record.cleanup_evidence = _capture_cleanup_evidence(container_name)

        evaluation = None
        can_read_persistent_scenario_trace = isinstance(spec, PersistentScenarioRunSpec) and status in {"succeeded", "failed"}
        if status == "succeeded" or can_read_persistent_scenario_trace:
            if not trace_path.is_file():
                if status == "succeeded":
                    status = "failed"
                    category = "trace_export"
                    error = f"Run completed but expected trace was not written: {trace_path}"
            else:
                try:
                    trace = json.loads(trace_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    if status == "succeeded":
                        status = "failed"
                        category = "trace_export"
                        error = f"Trace is invalid JSON at line {exc.lineno}, column {exc.colno}: {trace_path}"
                else:
                    metadata = trace.get("metadata", {})
                    record.provider = metadata.get("provider")
                    record.retry_count = sum(
                        1 for call in trace.get("llm_calls", [])
                        if call.get("status") == "error"
                    )
                    record.timeout_seconds = self.manifest.runtime.timeout_seconds
                    if isinstance(spec, PersistentScenarioRunSpec) and trace.get("$schema") != "persistent_scenario_trace_v2":
                        status = "failed"
                        category = "trace_schema"
                        error = (
                            "Persistent Scenario runner only accepts persistent_scenario_trace_v2: "
                            f"run_id={spec.run_id!r}, schema={trace.get('$schema')!r}, trace={trace_path}"
                        )
                        evaluation = None
                    else:
                        evaluation = trace.get("persistent_scenario_evaluation" if isinstance(spec, PersistentScenarioRunSpec) else "evaluation")
                    if not isinstance(evaluation, dict):
                        if status == "succeeded":
                            status = "failed"
                            category = "evaluator"
                            error = f"Trace does not contain an evaluation object: {trace_path}"
                    else:
                        if isinstance(spec, PersistentScenarioRunSpec):
                            if (
                                evaluation.get("$schema") != "persistent_scenario_evaluation_v2"
                                or evaluation.get("schema_version") != 2
                            ):
                                status = "failed"
                                category = "trace_schema"
                                error = (
                                    "Persistent Scenario runner requires persistent_scenario_evaluation_v2 (schema_version=2): "
                                    f"run_id={spec.run_id!r}, schema={evaluation.get('$schema')!r}, trace={trace_path}"
                                )
                                evaluation = None
                            else:
                                evaluation_valid = evaluation.get("valid") is True
                                if evaluation_valid and evaluation.get("model_failure") is True:
                                    status = "succeeded"
                                    category = "model_failure"
                                    error = None
                                elif evaluation_valid and status == "failed":
                                    category = "persistent_scenario_process"
                                    error = (
                                        "Persistent Scenario process exited with a non-zero code after "
                                        f"producing a valid evaluation: return_code={return_code}, "
                                        f"model_failure={evaluation.get('model_failure')!r}, trace={trace_path}"
                                    )
                                elif evaluation_valid:
                                    category = None
                                    error = None
                                elif evaluation.get("valid") is False:
                                    status = "failed"
                                    category = evaluation.get("failure_classification") or "infrastructure"
                                    error = str(evaluation.get("failure") or "Persistent Scenario run was invalid")
                        if evaluation is not None:
                            atomic_write_json(evaluator_path, evaluation)

        record.status = status
        record.finished_at = now_iso()
        record.duration_seconds = round(time.monotonic() - start, 3)
        record.return_code = return_code
        record.failure_category = category
        record.error = error
        if evaluation is not None:
            if isinstance(spec, PersistentScenarioRunSpec):
                record.diagnosis_pass = evaluation["DiagnosisPass"]
                record.outcome_pass = evaluation["OutcomePass"]
                record.safe_pass = evaluation["SafePass"]
                record.service_objectives_pass = evaluation["ServiceObjectivesPass"]
                record.data_integrity_pass = evaluation["DataIntegrityPass"]
                record.required_state_pass = evaluation["RequiredStatePass"]
                record.evaluation = evaluation
            else:
                record.diagnosis_pass = evaluation["DiagnosisPass"]
                record.outcome_pass = evaluation["OutcomePass"]
                record.safe_pass = evaluation["SafePass"]
                record.evaluator = evaluation["evaluator"]
                record.case_no = evaluation["case_no"]
                record.evaluation = evaluation
        record.valid_for_aggregate = (
            status == "succeeded"
            and isinstance(evaluation, dict)
            and (
                not isinstance(spec, PersistentScenarioRunSpec)
                or (
                    evaluation.get("valid") is True
                )
            )
        )
        if category == "model_failure" or (isinstance(evaluation, dict) and evaluation.get("model_failure") is True):
            record.run_status = "model_failure"
        elif status == "succeeded" and record.valid_for_aggregate:
            record.run_status = "completed"
        elif category in {
            "admission", "process_start", "trace_export", "trace_schema", "evaluator",
            "timeout", "interrupted", "provider", "protocol", "quota", "infrastructure",
            "workload_setup", "database_startup",
        }:
            record.run_status = "infrastructure_failure"
        else:
            record.run_status = "invalid"
        record.attempts.append({
            "attempt": attempt,
            "status": status,
            "started_at": record.started_at,
            "finished_at": record.finished_at,
            "duration_seconds": record.duration_seconds,
            "return_code": return_code,
            "failure_category": category,
            "run_status": record.run_status,
            "error": error,
            "trace_path": record.trace_path,
            "evaluator_path": record.evaluator_path if evaluation is not None else None,
            "stdout_path": record.stdout_path,
            "worker_id": record.worker_id,
            "physical_cores": record.physical_cores,
            "cpuset_cpus": record.cpuset_cpus,
            "cpuset_mems": record.cpuset_mems,
            "worker_cpu_capacity": record.worker_cpu_capacity,
            "worker_memory_capacity_mb": record.worker_memory_capacity_mb,
            "container_cpu_limit": record.container_cpu_limit,
            "container_memory_mb": record.container_memory_mb,
            "runtime_evidence": record.runtime_evidence,
            "cleanup_evidence": record.cleanup_evidence,
            "process_runtime_path": record.process_runtime_path,
            "runtime_audit_path": record.runtime_audit_path,
            "cleanup_audit_path": record.cleanup_audit_path,
        })
        self.store.save_attempt(record)
        self.store.save(record)
        print(f"[{status}] {spec.run_id} ({record.duration_seconds:.1f}s)")
        return record

    def _finish_failed_start(
        self,
        record: RunRecord,
        attempt: int,
        start: float,
        exc: OSError,
    ) -> RunRecord:
        record.status = "failed"
        record.run_status = "infrastructure_failure"
        record.finished_at = now_iso()
        record.duration_seconds = round(time.monotonic() - start, 3)
        record.failure_category = "process_start"
        record.error = f"Failed to start scenario process: {exc}"
        record.valid_for_aggregate = False
        record.attempts.append({
            "attempt": attempt,
            "status": record.status,
            "started_at": record.started_at,
            "finished_at": record.finished_at,
            "duration_seconds": record.duration_seconds,
            "return_code": None,
            "failure_category": record.failure_category,
            "run_status": record.run_status,
            "error": record.error,
            "trace_path": None,
            "evaluator_path": None,
            "stdout_path": record.stdout_path,
            "worker_id": record.worker_id,
            "physical_cores": record.physical_cores,
            "cpuset_cpus": record.cpuset_cpus,
            "cpuset_mems": record.cpuset_mems,
            "worker_cpu_capacity": record.worker_cpu_capacity,
            "worker_memory_capacity_mb": record.worker_memory_capacity_mb,
            "container_cpu_limit": record.container_cpu_limit,
            "container_memory_mb": record.container_memory_mb,
            "runtime_evidence": record.runtime_evidence,
            "cleanup_evidence": record.cleanup_evidence,
        })
        self.store.save_attempt(record)
        self.store.save(record)
        print(f"[failed] {record.run_id}: {record.error}")
        return record
