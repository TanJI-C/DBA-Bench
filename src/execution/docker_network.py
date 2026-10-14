"""Allocate TiDB bridge subnets through Docker's atomic IPAM reservation.

Docker owns the lease: successful network creation reserves a /24 until that
network is removed. Processes and worktrees need no shared lock or lease file.
Only IPAM overlap means contention; all other Docker failures are terminal.
"""

import hashlib
from ipaddress import IPv4Network
import re
import subprocess
from typing import Mapping


TIDB_NETWORK_POOL = IPv4Network("10.252.0.0/16")


def create_tidb_network(name: str, *, env: Mapping[str, str]) -> str:
    """Create an exclusively owned bridge and return its allocated subnet.

    Hashing chooses the first candidate, not the allocation. Docker serializes
    reservations, including requests from callers that do not use this module.
    A conflicting network identity is never adopted or removed.
    """
    listed = subprocess.run(
        ["docker", "network", "ls", "--filter", f"name=^{re.escape(name)}$", "--quiet"],
        capture_output=True, text=True, env=env,
    )
    if listed.returncode:
        raise RuntimeError(
            f"Docker network listing failed: network={name!r}, "
            f"returncode={listed.returncode}, stdout={listed.stdout.strip()!r}, "
            f"stderr={listed.stderr.strip()!r}"
        )
    if listed.stdout.strip():
        raise RuntimeError(
            f"Docker network identity already exists: network={name!r}, "
            f"network_ids={listed.stdout.strip()!r}"
        )

    subnets = tuple(TIDB_NETWORK_POOL.subnets(new_prefix=24))
    start = int(hashlib.sha256(name.encode()).hexdigest()[:2], 16)
    for offset in range(len(subnets)):
        subnet = str(subnets[(start + offset) % len(subnets)])
        created = subprocess.run(
            ["docker", "network", "create", "--driver", "bridge", "--subnet", subnet, name],
            capture_output=True, text=True, env=env,
        )
        if created.returncode == 0:
            return subnet
        if "Pool overlaps with other one on this address space" not in created.stderr:
            raise RuntimeError(
                f"Docker network creation failed: network={name!r}, subnet={subnet!r}, "
                f"returncode={created.returncode}, stdout={created.stdout.strip()!r}, "
                f"stderr={created.stderr.strip()!r}"
            )
    raise RuntimeError(
        f"Docker subnet pool exhausted: network={name!r}, pool={str(TIDB_NETWORK_POOL)!r}, "
        f"prefix=24, attempted_subnets={len(subnets)}"
    )
