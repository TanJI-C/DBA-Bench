from __future__ import annotations

import os
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .models import (
    IsolationDemandSpec,
    IsolationPolicySpec,
    BoundedScenarioRunSpec,
    PersistentScenarioRunSpec,
    WorkerAllocation,
)


HOST_EXCLUSIVE_SCENARIOS = frozenset({
    "pg_business_change_collation_conversion",
    "pg_business_change_massive_backfill",
    "pg_business_change_online_ddl",
    "pg_system_failure_wal_checkpoint_storm",
    "pg_health_check_backup_recoverability",
    "pg_health_check_capacity_trend",
    "pg_health_check_table_bloat",
    "pg_business_change_io_saturation",
    "pg_resource_governance_io_context_workload",
    "pg_resource_governance_audit_logging",
    "pg_resource_governance_resource_throttling",
    "pg_system_failure_oom",
    "pg_system_failure_temp_file_explosion",
    "pg_system_failure_wal_accumulation",
    "pg_system_failure_io_checkpoint_spikes",
    "pg_system_failure_page_corruption",
    "pg_system_failure_noisy_neighbor",
    "pg_system_failure_auto_analyze_storm",
})

@dataclass(frozen=True)
class PhysicalCore:
    socket_id: int
    core_id: int
    numa_node: int
    logical_cpus: tuple[int, ...]

    @property
    def id(self) -> str:
        return f"socket{self.socket_id}/core{self.core_id}"


def expand_linux_set(value: str, context: str) -> frozenset[int]:
    members: set[int] = set()
    for part in value.split(","):
        token = part.strip()
        if not token:
            raise ValueError(f"{context} contains an empty item: {value!r}")
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            if start > end:
                raise ValueError(f"{context} has a descending range {token!r}: {value!r}")
            members.update(range(start, end + 1))
        else:
            members.add(int(token))
    if not members or min(members) < 0:
        raise ValueError(f"{context} must contain non-negative Linux IDs: {value!r}")
    return frozenset(members)


def discover_physical_cores(
    sys_root: Path = Path("/sys"),
    allowed_cpus: set[int] | None = None,
) -> tuple[PhysicalCore, ...]:
    allowed = set(os.sched_getaffinity(0) if allowed_cpus is None else allowed_cpus)
    cores: dict[tuple[int, int], PhysicalCore] = {}
    for cpu in sorted(allowed):
        cpu_root = sys_root / f"devices/system/cpu/cpu{cpu}"
        topology_root = cpu_root / "topology"
        siblings = expand_linux_set(
            (topology_root / "thread_siblings_list").read_text(encoding="utf-8").strip(),
            f"CPU {cpu} thread siblings",
        )
        # Partial cores are allowed: a cpuset may carry only some SMT threads of
        # a core (the case demand is a container quota in logical-CPU units, so
        # scheduling is logical-CPU based, not whole-physical-core based). A
        # partially available core contributes only its allowed threads.
        available_siblings = siblings & allowed
        socket_id = int(
            (topology_root / "physical_package_id").read_text(encoding="utf-8").strip()
        )
        core_id = int((topology_root / "core_id").read_text(encoding="utf-8").strip())
        node_paths = sorted(cpu_root.glob("node[0-9]*"))
        if len(node_paths) != 1:
            raise RuntimeError(
                f"CPU {cpu} must belong to exactly one NUMA node, got "
                f"{[path.name for path in node_paths]}"
            )
        numa_node = int(node_paths[0].name.removeprefix("node"))
        core = PhysicalCore(
            socket_id=socket_id,
            core_id=core_id,
            numa_node=numa_node,
            logical_cpus=tuple(sorted(available_siblings)),
        )
        key = (socket_id, core_id)
        existing = cores.setdefault(key, core)
        if existing != core:
            raise RuntimeError(
                f"Inconsistent topology for physical core {key}: {existing} != {core}"
            )
    return tuple(sorted(
        cores.values(),
        key=lambda core: (core.numa_node, core.socket_id, core.core_id),
    ))


def _node_available_memory_kb(node: int, sys_root: Path) -> int:
    text = (sys_root / f"devices/system/node/node{node}/meminfo").read_text(
        encoding="utf-8"
    )
    values = {}
    for field in ("MemFree", "FilePages", "SReclaimable", "Shmem"):
        match = re.search(
            rf"^Node {node} {field}:\s+(\d+) kB$", text, re.MULTILINE
        )
        if not match:
            raise RuntimeError(
                f"NUMA node {node} meminfo does not contain {field}: text={text!r}"
            )
        values[field] = int(match.group(1))
    return (
        values["MemFree"]
        + values["FilePages"]
        + values["SReclaimable"]
        - values["Shmem"]
    )


def allocate_workers(
    demand: IsolationDemandSpec,
    worker_count: int,
    sys_root: Path = Path("/sys"),
    allowed_cpus: set[int] | None = None,
    cpuset_cpus: str | None = None,
) -> tuple[WorkerAllocation, ...]:
    cores_by_node: dict[int, list[PhysicalCore]] = defaultdict(list)
    for core in discover_physical_cores(sys_root=sys_root, allowed_cpus=allowed_cpus):
        cores_by_node[core.numa_node].append(core)
    pinned_cpus = expand_linux_set(cpuset_cpus, "worker cpuset") if cpuset_cpus else None
    if pinned_cpus is not None:
        host_cpus = set(os.sched_getaffinity(0) if allowed_cpus is None else allowed_cpus)
        unavailable = sorted(pinned_cpus - host_cpus)
        if unavailable:
            raise RuntimeError(
                f"Worker cpuset contains unavailable CPUs: cpuset_cpus={cpuset_cpus!r}, "
                f"unavailable={unavailable!r}"
            )
        for node in tuple(cores_by_node):
            cores_by_node[node] = [
                core
                for core in cores_by_node[node]
                if set(core.logical_cpus) & pinned_cpus
            ]
    node_available_memory_kb = {
        node: _node_available_memory_kb(node, sys_root)
        for node in cores_by_node
    }
    required_memory_kb = demand.memory_mb_per_worker * 1024
    if pinned_cpus is not None and worker_count == 1:
        # The explicit cpuset is the chunk's scheduling band, sized by the
        # launcher to the case's logical-CPU demand (physical_cores_per_worker
        # carries the container quota counted in logical CPUs). Pin the worker
        # to the whole band instead of requiring whole physical cores.
        band_cpus = sorted({
            cpu
            for cores in cores_by_node.values()
            for core in cores
            for cpu in core.logical_cpus
            if cpu in pinned_cpus
        })
        if len(band_cpus) < demand.physical_cores_per_worker:
            raise RuntimeError(
                f"Worker cpuset has fewer logical CPUs than the case demand: "
                f"cpuset_cpus={cpuset_cpus!r}, logical_cpus={len(band_cpus)}, "
                f"demand={demand.physical_cores_per_worker}"
            )
        band_nodes = tuple(sorted(
            node for node, cores in cores_by_node.items() if cores
        ))
        available_memory_kb = sum(node_available_memory_kb[node] for node in band_nodes)
        if available_memory_kb < required_memory_kb:
            raise RuntimeError(
                f"Worker cpuset NUMA nodes lack memory: cpuset_cpus={cpuset_cpus!r}, "
                f"available_memory_mb={available_memory_kb // 1024}, "
                f"required_mb={demand.memory_mb_per_worker}"
            )
        return (WorkerAllocation(
            id="worker-01",
            physical_cores=tuple(
                core.id
                for cores in cores_by_node.values()
                for core in cores
            ),
            cpuset_cpus=",".join(str(cpu) for cpu in band_cpus),
            cpuset_mems=",".join(str(node) for node in band_nodes),
            cpu_capacity=float(demand.physical_cores_per_worker),
            memory_capacity_mb=demand.memory_mb_per_worker,
        ),)
    used_nodes: set[int] = set()
    workers = []
    for index in range(worker_count):
        candidates = [
            node
            for node in sorted(cores_by_node)
            if len(cores_by_node[node]) >= demand.physical_cores_per_worker
            and node_available_memory_kb[node] >= required_memory_kb
            and (demand.numa_policy != "separate" or node not in used_nodes)
        ]
        if candidates:
            node = candidates[0]
            selected = tuple(cores_by_node[node][:demand.physical_cores_per_worker])
            del cores_by_node[node][:demand.physical_cores_per_worker]
            selected_nodes = (node,)
        elif worker_count == 1:
            available_cores = [
                (node, core)
                for node in sorted(cores_by_node)
                for core in cores_by_node[node]
            ]
            if (
                len(available_cores) < demand.physical_cores_per_worker
                or sum(node_available_memory_kb.values()) < required_memory_kb
            ):
                remaining = {
                    node: {
                        "physical_cores": len(cores),
                        "available_memory_mb": node_available_memory_kb[node] // 1024,
                    }
                    for node, cores in sorted(cores_by_node.items())
                }
                raise RuntimeError(
                    f"Cannot allocate benchmark worker {index + 1}/{worker_count}: "
                    f"physical_cores_per_worker={demand.physical_cores_per_worker}, "
                    f"memory_mb_per_worker={demand.memory_mb_per_worker}, "
                    f"numa_policy={demand.numa_policy!r}, remaining={remaining}"
                )
            selected_pairs = available_cores[:demand.physical_cores_per_worker]
            selected = tuple(core for _, core in selected_pairs)
            selected_nodes = tuple(sorted({node for node, _ in selected_pairs}))
            for selected_node in selected_nodes:
                selected_set = set(selected)
                cores_by_node[selected_node] = [
                    core for core in cores_by_node[selected_node]
                    if core not in selected_set
                ]
        else:
            remaining = {
                node: {
                    "physical_cores": len(cores),
                    "available_memory_mb": node_available_memory_kb[node] // 1024,
                }
                for node, cores in sorted(cores_by_node.items())
            }
            raise RuntimeError(
                f"Cannot allocate benchmark worker {index + 1}/{worker_count}: "
                f"physical_cores_per_worker={demand.physical_cores_per_worker}, "
                f"memory_mb_per_worker={demand.memory_mb_per_worker}, "
                f"numa_policy={demand.numa_policy!r}, remaining={remaining}"
            )
        for selected_node in selected_nodes:
            node_available_memory_kb[selected_node] = max(
                0,
                node_available_memory_kb[selected_node] - required_memory_kb,
            )
        used_nodes.update(selected_nodes)
        logical_cpus = sorted({
            cpu
            for core in selected
            for cpu in core.logical_cpus
            if pinned_cpus is None or cpu in pinned_cpus
        })
        workers.append(WorkerAllocation(
            id=f"worker-{index + 1:02d}",
            physical_cores=tuple(core.id for core in selected),
            cpuset_cpus=",".join(str(cpu) for cpu in logical_cpus),
            cpuset_mems=",".join(str(node) for node in selected_nodes),
            cpu_capacity=float(demand.physical_cores_per_worker),
            memory_capacity_mb=demand.memory_mb_per_worker,
        ))
    return tuple(workers)


def derive_worker_demand(
    specs: list[BoundedScenarioRunSpec | PersistentScenarioRunSpec],
    policy: IsolationPolicySpec,
    *,
    allow_missing_resources: bool = False,
) -> IsolationDemandSpec:
    missing = sorted({
        (
            f"{spec.scenario_id}/{spec.case_id}"
            if isinstance(spec, BoundedScenarioRunSpec)
            else spec.scenario_id
        )
        for spec in specs
        if spec.resources is None
    })
    if missing and not allow_missing_resources:
        raise ValueError(
            "Parallel runs require explicit case resource contracts: "
            + ", ".join(missing)
        )
    resources = [spec.resources for spec in specs if spec.resources is not None]
    if not resources:
        return IsolationDemandSpec(
            physical_cores_per_worker=1,
            memory_mb_per_worker=512,
            numa_policy=policy.numa_policy,
        )
    return IsolationDemandSpec(
        physical_cores_per_worker=max(
            resource.worker_physical_cores for resource in resources
        ),
        memory_mb_per_worker=max(
            resource.worker_memory_mb for resource in resources
        ),
        numa_policy=policy.numa_policy,
    )


def requires_host_exclusive(spec: BoundedScenarioRunSpec) -> bool:
    return spec.scenario_id in HOST_EXCLUSIVE_SCENARIOS


def assert_fault_snapshots_exist(specs: list[BoundedScenarioRunSpec]) -> dict[str, str]:
    from src.scenarios import DatabaseSystem, SCENARIOS_BY_ID
    from src.execution.environment import PGEnv, TiDBEnv

    snapshots = {}
    snapshot_environments = {}
    for scenario_id, case_id in sorted({
        (spec.scenario_id, spec.case_id)
        for spec in specs
    }):
        registration = SCENARIOS_BY_ID[scenario_id]
        scenario = registration.scenario
        case = scenario.get_case(case_id)
        if registration.system is DatabaseSystem.POSTGRESQL:
            env = PGEnv()
        elif registration.system is DatabaseSystem.TIDB:
            image_group_key = case.runtime.image_group_key
            if image_group_key is None:
                raise ValueError(
                    f"TiDB fault snapshot requires an image_group_key: "
                    f"scenario={scenario_id!r}, case={case_id!r}"
                )
            env = TiDBEnv(
                run_id=f"snapshot-check-{scenario_id}-{case_id}",
                image_group_key=image_group_key,
            )
            env.configure_case(case)
        else:
            raise ValueError(
                f"Fault snapshots are unavailable for system={registration.system.value!r}, "
                f"scenario={scenario_id!r}, case={case_id!r}"
            )
        snapshot_name = env.snapshot_name(scenario_id, case)
        if snapshot_name is None:
            raise ValueError(
                f"Fault snapshot identity is unavailable: scenario={scenario_id!r}, case={case_id!r}"
            )
        key = f"{scenario_id}/{case_id}"
        snapshots[key] = snapshot_name
        snapshot_environments[key] = env
    missing = {
        scenario_id: snapshot_name
        for scenario_id, snapshot_name in snapshots.items()
        if not snapshot_environments[scenario_id].snapshot_exists(snapshot_name)
    }
    if missing:
        details = ", ".join(
            f"{scenario_id}={snapshot_name}"
            for scenario_id, snapshot_name in missing.items()
        )
        raise RuntimeError(
            "fault_snapshot='use' requires every fault snapshot to exist before execution; "
            f"missing: {details}"
        )
    return snapshots
