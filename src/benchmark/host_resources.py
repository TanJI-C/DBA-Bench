"""Host-wide admission shared by benchmark processes and Git worktrees.

Locks are owned by open file descriptions. Children inherit the lease so a
parent's death cannot admit another experiment while its run is still alive.
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
from dataclasses import asdict, dataclass
import fcntl
import json
import os
from pathlib import Path
import subprocess
from typing import Iterator
import uuid

from .isolation import allocate_workers, derive_worker_demand, expand_linux_set, requires_host_exclusive
from .models import BoundedScenarioRunSpec, IsolationPolicySpec, PersistentScenarioRunSpec, WorkerAllocation


HOST_RESOURCE_ROOT = Path('/tmp/aiopsbench-host-resources')


@dataclass(frozen=True)
class HostReservation:
    workers: tuple[WorkerAllocation, ...]
    pass_fds: tuple[int, ...]
    evidence: dict


def _live_reservations(root: Path) -> list[dict]:
    live = []
    for path in sorted(root.glob('lease-*.json')):
        with path.open('r+') as lease:
            try:
                fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                live.append(json.load(lease))
            else:
                evidence = json.load(lease)
                records = [Path(record) for record in evidence['run_records']]
                namespaces = set()
                for record_path in records:
                    record = json.loads(record_path.read_text())
                    namespaces.add(record['run_id'])
                    command = record['command']
                    for flag in ('--container-name', '--run-id'):
                        if flag in command:
                            namespaces.add(command[command.index(flag) + 1])
                    observed = record['runtime_evidence'].get('container_name')
                    if observed:
                        namespaces.add(observed)
                if namespaces:
                    result = subprocess.run(
                        ['docker', 'ps', '-a', '--format', '{{.Names}}'],
                        capture_output=True, text=True, check=True,
                    )
                    prefixes = namespaces | {'aiopsbench-' + name for name in namespaces}
                    remaining = [name for name in result.stdout.splitlines()
                                 if any(name == prefix or name.startswith(prefix + '-') for prefix in prefixes)]
                    if remaining:
                        raise RuntimeError(
                            f"Abandoned host reservation still owns Docker containers: "
                            f"experiment_id={evidence['experiment_id']!r}, containers={remaining}, lease={path}; "
                            "complete the experiment cleanup before admitting another experiment"
                        )
                path.unlink()
    return live


@contextmanager
def reserve_host_resources(
    experiment_id: str,
    specs: list[BoundedScenarioRunSpec | PersistentScenarioRunSpec],
    policy: IsolationPolicySpec | None,
    concurrency: int,
    *,
    root: Path = HOST_RESOURCE_ROOT,
    sys_root: Path = Path('/sys'),
    allowed_cpus: set[int] | None = None,
    run_records: tuple[Path, ...] = (),
) -> Iterator[HostReservation]:
    root.mkdir(parents=True, exist_ok=True)
    exclusive = policy is None or any(requires_host_exclusive(spec) for spec in specs)
    with ExitStack() as stack:
        gate = stack.enter_context((root / 'host.lock').open('a+'))
        try:
            fcntl.flock(gate, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(
                f'Host admission denied: experiment_id={experiment_id!r}, '
                f'exclusive={exclusive}, another benchmark holds an incompatible host lock; root={root}'
            ) from exc
        with (root / 'admission.lock').open('a+') as admission:
            fcntl.flock(admission, fcntl.LOCK_EX)
            live = _live_reservations(root)
            reserved_cores = frozenset(core for item in live for worker in item['workers'] for core in worker['physical_cores'])
            memory: dict[int, int] = {}
            for item in live:
                for worker in item['workers']:
                    for node in expand_linux_set(worker['cpuset_mems'], 'reserved NUMA nodes'):
                        memory[node] = memory.get(node, 0) + worker['memory_capacity_mb'] * 1024
            workers = ()
            if policy is not None:
                demand = derive_worker_demand(specs, policy, allow_missing_resources=concurrency == 1)
                try:
                    workers = allocate_workers(
                        demand, concurrency, sys_root=sys_root, allowed_cpus=allowed_cpus,
                        cpuset_cpus=policy.cpuset_cpus, reserved_cores=reserved_cores,
                        reserved_memory_kb=memory,
                    )
                except RuntimeError as exc:
                    raise RuntimeError(
                        f'Host resource reservation failed: experiment_id={experiment_id!r}, '
                        f'active_reservations={live!r}; {exc}'
                    ) from exc
            evidence = {
                'experiment_id': experiment_id, 'pid': os.getpid(),
                'exclusive': exclusive, 'workers': [asdict(worker) for worker in workers],
                'run_records': [str(path.resolve()) for path in run_records],
            }
            lease = stack.enter_context((root / f'lease-{uuid.uuid4().hex}.json').open('x+'))
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            json.dump(evidence, lease)
            lease.flush()
        yield HostReservation(workers, (gate.fileno(), lease.fileno()), evidence)
