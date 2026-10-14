import math
from typing import Mapping

from src.execution.specs import (
    CaseResourceSpec,
    TiDBCaseRuntime,
    TiDBReleaseSpec,
    TiDBReplicationRuntime,
    TiDBTopologySpec,
)


def canonical_tidb_version(version: object) -> str:
    return str(version).strip().casefold().removeprefix("v")


TIDB_V8_1_0 = TiDBReleaseSpec(
    version="v8.1.0",
    pd_image="pingcap/pd@sha256:78f5de9dc59abd02c99056294fb51f29da39ed932eb92cb2570ad57fe0774e80",
    tikv_image="pingcap/tikv@sha256:0b9d00f2b4f60cd3f91b55720a737136643e17bfb4de82a3c30ca532430374a5",
    tidb_image="pingcap/tidb@sha256:ee98d7d09ea2dcdc76dd683de3c3cdd63f052b33a91f5645ab75609df3648501",
    tiflash_image="docker.m.daocloud.io/pingcap/tiflash@sha256:251e3e2b76482fe2f5c2b82311c9cce24f240a1ad66f1eeda3438e66da3a18ec",
    tidb_extra_args=("--temp-dir=/tmp/tidb",),
)

TIDB_V5_4_3 = TiDBReleaseSpec(
    version="v5.4.3",
    pd_image="pingcap/pd@sha256:821dc62050bb9c8ecbf86ea0003b0fe618bea0f4e14e57a4dea5e4f207b65cc7",
    tikv_image="pingcap/tikv@sha256:da2aacf38452a992d23f72a02300feeb0dd2381f58520a518bead5f8d55bccef",
    tidb_image="pingcap/tidb@sha256:eecea206c5e6d11f6a2be7ebb8a05e2f6235083a8caa3655c95bd6c2485fa073",
    tiflash_image=None,
    tidb_extra_args=(),
)

TICDC_V8_1_0 = "pingcap/ticdc@sha256:7832063b5215b3107d33b7280b2653a79667e9ba54e4b0596ed1092b4a486015"
MYSQL_8_4 = "mysql@sha256:43bd9764df60666fb2ba2cf8217dd17b3d2414c150005d2fdd07a0cd73d3b7f5"

TIDB_V6_5_0 = TiDBReleaseSpec(
    version="v6.5.0",
    pd_image="pingcap/pd@sha256:3fbd27b24675e67354f7c17a4bf289983a1071b8dc6f2d7c711fd7a64b5def98",
    tikv_image="pingcap/tikv@sha256:344dd6ac91922f71f8736ae7669f5a0b7e9be186ed2322e19042ebbba9c262a1",
    tidb_image="pingcap/tidb@sha256:64db0e93a911bf27518dd3d82b46dc3bea01e89140a9a71fd324c3cd06e89c6c",
    tiflash_image=None,
    tidb_extra_args=("--temp-dir=/tmp/tidb",),
)

TIDB_V7_5_0 = TiDBReleaseSpec(
    version="v7.5.0",
    pd_image="pingcap/pd@sha256:926a2565a4113aa8127840610f1e3419eab227aaf7a87310bb2cfe28d59d28ce",
    tikv_image="pingcap/tikv@sha256:d2adb67c75e9d25dda8c8c367c1db269e079dfd2f8427c8aff0ff44ec1c1be09",
    tidb_image="pingcap/tidb@sha256:4a0f3070b27a5acf9734e16c725050ae95b4a07b58ac08693c596ce237045a1f",
    tiflash_image=None,
    tidb_extra_args=("--temp-dir=/tmp/tidb",),
)


def tidb_runtime(
    *,
    release: TiDBReleaseSpec,
    pd_count: int,
    tikv_count: int,
    tidb_count: int,
    tiflash_count: int = 0,
    # 多实验并发时 TiDB 启动后的 SQL settle 窗口可达 60-100s(共享 docker data-root
    # IO 争用加剧);默认值取 120s 以覆盖 setup 首批 SQL,避免 2013 超时。
    sql_timeout_seconds: int = 120,
    image_group_key: str | None = None,
    tikv_shared_volume_root: str | None = None,
    tikv_store_zones: tuple[str, ...] = (),
    pd_location_labels: tuple[str, ...] = (),
    deferred_tikv_count: int = 0,
    tikv_memory_mb: int = 2048,
    tidb_memory_mb: int = 1024,
    bootstrap_cache_enabled: bool = True,
    tikv_config_writable: bool = False,
    tikv_io_rate_limit_strict: bool = False,
    tikv_server_config_overrides: Mapping[str, Mapping[str, object]] | None = None,
    readiness_timeout_seconds: int = 1800,
    replication: TiDBReplicationRuntime | None = None,
    upgrade_release: TiDBReleaseSpec | None = None,
    pd_cpu_limit: float = 1.0,
) -> TiDBCaseRuntime:
    topology = TiDBTopologySpec(
        pd_count=pd_count,
        tikv_count=tikv_count,
        tidb_count=tidb_count,
        tiflash_count=tiflash_count,
        deferred_tikv_count=deferred_tikv_count,
    )
    if tiflash_count and release.tiflash_image is None:
        raise ValueError(
            f"TiDB release has no TiFlash image: version={release.version!r}, tiflash_count={tiflash_count}"
        )
    replication_cpu = (
        replication.ticdc_count * replication.ticdc_cpu_limit + replication.downstream_cpu_limit
        if replication is not None
        else 0.0
    )
    if pd_cpu_limit <= 0:
        raise ValueError(f"TiDB PD CPU limit must be positive: pd_cpu_limit={pd_cpu_limit!r}")
    cpu_limit = (
        pd_count * pd_cpu_limit
        + tikv_count
        + tidb_count
        + tiflash_count * 2.0
        + 1.0
        + replication_cpu
    )
    memory_mb = (
        pd_count * 4096
        + tikv_count * tikv_memory_mb
        + tidb_count * tidb_memory_mb
        + tiflash_count * 4096
        + 4096
        + (
            replication.ticdc_count * replication.ticdc_memory_mb + replication.downstream_memory_mb
            if replication is not None
            else 0
        )
    )
    return TiDBCaseRuntime(
        topology=topology,
        resources=CaseResourceSpec(
            worker_physical_cores=math.ceil(cpu_limit),
            worker_memory_mb=memory_mb,
            container_cpu_limit=cpu_limit,
            container_memory_mb=memory_mb,
        ),
        release=release,
        upgrade_release=upgrade_release,
        sql_timeout_seconds=sql_timeout_seconds,
        tikv_memory_mb=tikv_memory_mb,
        tidb_memory_mb=tidb_memory_mb,
        image_group_key=image_group_key,
        tikv_shared_volume_root=tikv_shared_volume_root,
        tikv_store_zones=tikv_store_zones,
        pd_location_labels=pd_location_labels,
        bootstrap_cache_enabled=bootstrap_cache_enabled,
        tikv_config_writable=tikv_config_writable,
        tikv_io_rate_limit_strict=tikv_io_rate_limit_strict,
        tikv_server_config_overrides=tikv_server_config_overrides,
        readiness_timeout_seconds=readiness_timeout_seconds,
        replication=replication,
        pd_cpu_limit=pd_cpu_limit,
    )
