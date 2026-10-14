"""Host port leases held across container startup, restart and replacement."""

from contextlib import ExitStack
from dataclasses import dataclass
import errno
import fcntl
import json
import os
from pathlib import Path
import socket
import subprocess
from typing import IO


HOST_PORT_ROOT = Path('/tmp/aiopsbench-host-resources/ports')
PORT_LEASE_ENV = 'AIOPS_HOST_PORT_LEASE'


@dataclass
class PortLease:
    ports: tuple[int, ...]
    files: tuple[IO, ...]

    @property
    def pass_fds(self) -> tuple[int, ...]:
        return tuple(file.fileno() for file in self.files)

    @property
    def process_environment(self) -> str:
        return json.dumps(dict(zip(self.ports, self.pass_fds)))

    def close(self) -> None:
        for file in self.files:
            file.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def _docker_port_owners() -> dict[int, list[str]]:
    ids = subprocess.run(['docker', 'ps', '-aq'], capture_output=True, text=True, check=True).stdout.split()
    if not ids:
        return {}
    result = subprocess.run(
        ['docker', 'inspect', '--format', '{"name":{{json .Name}},"ports":{{json .HostConfig.PortBindings}}}', *ids],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        # Containers may disappear between ps and inspect during another run's teardown.
        vanished = {f"Error: No such object: {container_id}" for container_id in ids}
        if not result.stderr.strip() or any(line not in vanished for line in result.stderr.splitlines()):
            raise RuntimeError(f"Docker port inventory failed: ids={ids}, stderr={result.stderr!r}")
    owners: dict[int, list[str]] = {}
    for line in result.stdout.splitlines():
        container = json.loads(line)
        for bindings in (container['ports'] or {}).values():
            for binding in bindings or ():
                if binding['HostPort']:
                    owners.setdefault(int(binding['HostPort']), []).append(container['name'].removeprefix('/'))
    return owners


def _bindable(port: int) -> bool:
    addresses = [(socket.AF_INET, '0.0.0.0')]
    if socket.has_ipv6:
        addresses.append((socket.AF_INET6, '::'))
    for family, address in addresses:
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            if family == socket.AF_INET6:
                sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
            try:
                sock.bind((address, port))
            except OSError as exc:
                if exc.errno == errno.EADDRINUSE:
                    return False
                raise RuntimeError(f'Host port probe failed: address={address!r}, port={port}, error={exc!r}') from exc
    return True


def reserve_host_ports(
    base: int, offsets: tuple[int, ...], *, owner: str,
    root: Path = HOST_PORT_ROOT, attempts: int = 64, step: int = 1,
    allowed_range: tuple[int, int] = (1024, 65535),
    owned_containers: tuple[str, ...] = (),
) -> PortLease:
    """Atomically choose and lock a complete layout; Docker keeps actual sockets.

    Socket probes detect external listeners. Persistent per-port flock files
    prevent participating processes from selecting the same still-unpublished
    ports. Docker's declared mappings also exclude stopped/orphan containers.
    """
    root.mkdir(parents=True, exist_ok=True)
    rejected = []
    with (root / 'admission.lock').open('a+') as admission:
        fcntl.flock(admission, fcntl.LOCK_EX)
        docker_owners = _docker_port_owners()
        for candidate in range(base, base + attempts * step, step):
            ports = tuple(sorted({candidate + offset for offset in offsets}))
            if ports[0] < allowed_range[0] or ports[-1] > allowed_range[1]:
                break
            with ExitStack() as stack:
                files = []
                conflict = None
                for port in ports:
                    file = stack.enter_context((root / f'{port}.lock').open('a+'))
                    try:
                        fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        file.seek(0)
                        conflict = {'port': port, 'lease_owner': file.read()}
                        break
                    containers = [name for name in docker_owners.get(port, ()) if name not in owned_containers]
                    if containers or (not docker_owners.get(port) and not _bindable(port)):
                        conflict = {'port': port, 'containers': containers, 'external_listener': not containers}
                        break
                    files.append(file)
                if conflict is not None:
                    rejected.append(conflict)
                    continue
                for port, file in zip(ports, files):
                    file.seek(0)
                    file.truncate()
                    json.dump({'owner': owner, 'pid': os.getpid(), 'port': port}, file)
                    file.flush()
                stack.pop_all()
                return PortLease(ports, tuple(files))
    raise RuntimeError(
        f'Host port reservation failed: owner={owner!r}, base={base}, offsets={offsets}, '
        f'allowed_range={allowed_range}, attempted={len(rejected)}, conflicts={rejected}'
    )


def claim_host_ports(ports: tuple[int, ...], *, owner: str, owned_containers: tuple[str, ...] = ()) -> PortLease:
    """Adopt the runner's inherited locks, or claim exact standalone ports."""
    if PORT_LEASE_ENV in os.environ:
        inherited = {int(port): fd for port, fd in json.loads(os.environ[PORT_LEASE_ENV]).items()}
        missing = sorted(set(ports) - inherited.keys())
        if missing:
            raise RuntimeError(f'Undeclared host ports: owner={owner!r}, requested={ports}, missing={missing}, reserved={sorted(inherited)}')
        with ExitStack() as stack:
            files = tuple(stack.enter_context(os.fdopen(os.dup(inherited[port]), 'r+')) for port in ports)
            stack.pop_all()
            return PortLease(ports, files)
    base = min(ports)
    return reserve_host_ports(base, tuple(port - base for port in ports), owner=owner,
                              attempts=1, owned_containers=owned_containers)
