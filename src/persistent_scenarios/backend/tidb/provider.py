"""EnvironmentProvider implementation for TiDB persistent scenarios.

Construction shape for the integration assembly (the documented constructor):

    provider = TiDBEnvironmentProvider(data_root=<batch data dir>)
    environment = provider.create(spec, run_id="tidb5-backend-<name>", port=<port_base>)
    provider.deploy(environment)
    ...
    provider.teardown(environment)

``port`` is the host port_base; the deployment derives every service port from
it inside the lease range 26000-26499 (validated by the deployment module).
The run_id must carry the batch lease prefix ``tidb5-backend-``.
"""

from __future__ import annotations

import os
from pathlib import Path

from src.execution.tidb_persistent_deployment import (
    DATA_ROOT,
    MYSQL_IMAGE,
    RUN_ID_PREFIX,
    TICDC_IMAGE,
    TiDBPersistentDeployment,
    PORT_RANGE,
    port_allocation_count,
)
from src.execution.specs import HostPortLayout
from src.execution.tidb_runtime import TIDB_V8_1_0, TiDBReleaseSpec

from .environment import PersistentTiDBEnvironment
from .topology import expand_topology


class TiDBEnvironmentProvider:
    """``EnvironmentProvider`` over ``TiDBPersistentDeployment``."""

    def __init__(
        self,
        *,
        data_root: os.PathLike[str] | str = DATA_ROOT,
        release: TiDBReleaseSpec = TIDB_V8_1_0,
        readiness_timeout_seconds: int = 1800,
    ):
        self.data_root = data_root
        self.release = release
        self.readiness_timeout_seconds = readiness_timeout_seconds

    def _release_images(self) -> dict[str, str]:
        if self.release.tiflash_image is None:
            raise ValueError(
                f"TiDB release has no TiFlash image, persistent deployments require one: "
                f"version={self.release.version!r}"
            )
        return {
            "pd": self.release.pd_image,
            "tikv": self.release.tikv_image,
            "tidb": self.release.tidb_image,
            "tiflash": self.release.tiflash_image,
            "ticdc": TICDC_IMAGE,
            "downstream": MYSQL_IMAGE,
        }

    def host_ports(self, spec) -> HostPortLayout:
        topology = expand_topology(spec, release_images=self._release_images(), data_dir=str(self.data_root))
        return HostPortLayout(offsets=tuple(range(port_allocation_count(topology, enable_monitoring=True))),
                              allowed_range=PORT_RANGE)

    def create(self, spec, run_id: str, port: int) -> PersistentTiDBEnvironment:
        if not run_id.startswith(RUN_ID_PREFIX):
            raise ValueError(
                f"TiDB persistent run_id must use the batch lease prefix {RUN_ID_PREFIX!r}: run_id={run_id!r}"
            )
        data_dir = Path(self.data_root).resolve() / run_id
        topology = expand_topology(spec, release_images=self._release_images(), data_dir=str(data_dir))
        deployment = TiDBPersistentDeployment(
            run_id=run_id,
            port_base=port,
            topology=topology,
            data_root=self.data_root,
            release=self.release,
            readiness_timeout_seconds=self.readiness_timeout_seconds,
        )
        return PersistentTiDBEnvironment(deployment=deployment)

    def deploy(self, environment: PersistentTiDBEnvironment) -> None:
        environment.deploy()

    def teardown(self, environment: PersistentTiDBEnvironment) -> None:
        environment.teardown()
