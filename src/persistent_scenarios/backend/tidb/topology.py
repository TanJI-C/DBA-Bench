"""NodeSpec expansion into a TiDB persistent topology plan.

Role vocabulary (TiDB backend, documented for integration assembly):

- ``pd``        - placement driver nodes (at least 1; the portfolio contract
                  topologies use 3);
- ``tikv``      - TiKV storage nodes;
- ``tidb``      - TiDB SQL nodes;
- ``tiflash``   - TiFlash columnar replica nodes (0 or more);
- ``ticdc``     - TiCDC capture nodes (0 or more);
- ``downstream``- independent MySQL downstream for CDC replication (0 or 1).

Prometheus and cAdvisor are deployment infrastructure added by the deployment
module; they are never part of ``nodes``. NodeSpec ``docker_caps`` becomes
compose ``cap_add``; NodeSpec ``volumes`` become node-scoped bind mounts under
the run data dir (host path ``<data_dir>/volumes/<name>`` -> the given
``mount_path``).
"""

from __future__ import annotations

from src.execution.tidb_persistent_deployment import (
    PersistentTiDBNodePlan,
    PersistentTiDBTopologyPlan,
)

from ...model.spec import PersistentScenarioSpec

TIDB_NODE_ROLES = ("pd", "tikv", "tidb", "tiflash", "ticdc", "downstream")
_DOWNSTREAM_COUNT_LIMIT = 1
# tidb_htap_tiflash_isolation candidate topology: the candidate topology carries
# two TiFlash stores; anything beyond the candidate must not silently deploy.
_TIFLASH_COUNT_LIMIT = 2


def expand_topology(
    spec: PersistentScenarioSpec,
    *,
    release_images: dict[str, str],
    data_dir: str,
) -> PersistentTiDBTopologyPlan:
    """Expand ``spec.environment.nodes`` into the deployment topology plan.

    ``release_images`` maps role -> digest-pinned image for the release chosen
    by the caller (see ``provider.py``); ``data_dir`` is the run data root the
    deployment module derived from the run_id.
    """
    plans: list[PersistentTiDBNodePlan] = []
    role_counts: dict[str, int] = {}
    for node in spec.environment.nodes:
        if node.role not in TIDB_NODE_ROLES:
            raise ValueError(
                f"Unknown TiDB persistent NodeSpec role: node_id={node.node_id!r}, role={node.role!r}, "
                f"expected={TIDB_NODE_ROLES!r}"
            )
        index = role_counts.get(node.role, 0)
        role_counts[node.role] = index + 1
        service = f"{node.role}-{index}"
        if node.role not in release_images:
            raise ValueError(
                f"No pinned image registered for TiDB persistent role: role={node.role!r}, "
                f"available={sorted(release_images)!r}"
            )
        plans.append(PersistentTiDBNodePlan(
            service=service,
            role=node.role,
            node_id=node.node_id,
            image=release_images[node.role],
            cpus=node.resources.container_cpu_limit,
            memory_mb=node.resources.container_memory_mb,
            cap_add=tuple(node.docker_caps),
            volumes=tuple(
                (f"{data_dir}/volumes/{volume.name}", volume.mount_path)
                for volume in node.volumes
            ),
        ))
    for role in ("pd", "tikv", "tidb"):
        if role_counts.get(role, 0) < 1:
            raise ValueError(
                f"TiDB persistent topology requires at least one {role} node: "
                f"node_role_counts={ {role: role_counts.get(role, 0) for role in TIDB_NODE_ROLES}!r}"
            )
    if role_counts.get("downstream", 0) > _DOWNSTREAM_COUNT_LIMIT:
        raise ValueError(
            f"TiDB persistent topology supports at most {_DOWNSTREAM_COUNT_LIMIT} downstream node: "
            f"downstream_count={role_counts.get('downstream', 0)}"
        )
    if role_counts.get("tiflash", 0) > _TIFLASH_COUNT_LIMIT:
        raise ValueError(
            f"TiDB persistent topology supports at most {_TIFLASH_COUNT_LIMIT} TiFlash nodes: "
            f"tiflash_count={role_counts.get('tiflash', 0)}"
        )
    return PersistentTiDBTopologyPlan(nodes=tuple(plans))
