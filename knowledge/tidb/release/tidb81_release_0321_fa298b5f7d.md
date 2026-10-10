# Bug fixes across TiDB, TiKV, PD, BR, TiCDC, Lightning, and TiDB Binlog

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.7.md`
- Source Title: `TiDB 6.1.7 Release Notes`
- Source Heading Path: `TiDB 6.1.7 Release Notes > Bug fixes`
- Source Line Ranges: `68-108`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `br`, `ticdc`, `lightning`, `ecosystem`
- Topic Tags: `bug-fixes`, `partitioned-tables`, `cte`, `transactions`, `placement-rules`, `encryption`, `continuous-profiling`, `grpc`, `backup`, `changefeed`, `kafka`, `pd-failover`, `logical-import`, `disk-quota`, `oom`, `binlog`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0321_fa298b5f7d`
- Source ID: `tidb-docs-8.1:releases/release-6.1.7.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c8f1d35af98f4d5d8ea2d7415d90ce8d4fa112c2911244f50cff450c699f07ba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.7#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.7.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.1.7 bug fixes across TiDB, TiKV, PD, BR, TiCDC, TiDB Lightning, or TiDB Binlog for issues involving partitioned tables, CTE predicate pushdown, auto-commit transaction behavior, encryption key ID conflict, Continuous Profiling, gRPC error format, backup slowdown, changefeed creation or recovery, Kafka downstream workload, Logical Import Mode metadata, disk quota accuracy, OOM, or failed DDL statements.
- Retrieval Keywords: TiDB 6.1.7 bug fixes, truncating a partition placement rule invalid, CTE results are incorrect when pushing down predicates, auto-commit change affects transaction commit behaviours, TiDB Lightning SST file leakage, encryption key ID conflict old keys deletion, file handle leakage in Continuous Profiling, PD gRPC returns errors with unexpected formats, resolved lock timeout falsely reported, backup slowdown when a TiKV node crashes, TiCDC cannot create a changefeed with a downstream Kafka-on-Pulsar, TiCDC cannot automatically recover when PD address or leader fails, TiCDC queries the downstream metadata too frequently, TiCDC gets stuck when PD fails, Logical Import Mode metadata not updated in time, disk quota might be inaccurate due to competing conditions, write to tikv with no leader returned, unclosed delimiter OOM, wide table OOM, etcd client does not automatically synchronize the latest node information, Drainer panic old TiKV client version, unfiltered failed DDL statements cause task errors
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release note because it lists bug fixes included in TiDB 6.1.7 across multiple components and tools.

## Official Source Content

- Fix the issue that truncating a partition of a partitioned table might cause the Placement Rule of the partition to become invalid [#44031](https://github.com/pingcap/tidb/issues/44031) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that CTE results are incorrect when pushing down predicates [#43645](https://github.com/pingcap/tidb/issues/43645) @[winoros](https://github.com/winoros)
    - Fix the issue that `auto-commit` change affects transaction commit behaviours [#36581](https://github.com/pingcap/tidb/issues/36581) @[cfzjywxk](https://github.com/cfzjywxk)

+ TiKV

    - Fix the issue that TiDB Lightning might cause SST file leakage [#14745](https://github.com/tikv/tikv/issues/14745) @[YuJuncen](https://github.com/YuJuncen)
    - Fix the issue that encryption key ID conflict might cause the deletion of the old keys [#14585](https://github.com/tikv/tikv/issues/14585) @[tabokie](https://github.com/tabokie)
    - Fix the issue of file handle leakage in Continuous Profiling [#14224](https://github.com/tikv/tikv/issues/14224) @[tabokie](https://github.com/tabokie)

+ PD

    - Fix the issue that gRPC returns errors with unexpected formats [#5161](https://github.com/tikv/pd/issues/5161) @[HuSharp](https://github.com/HuSharp)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that `resolved lock timeout` is falsely reported in some cases [#43236](https://github.com/pingcap/tidb/issues/43236) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue of backup slowdown when a TiKV node crashes in a cluster [#42973](https://github.com/pingcap/tidb/issues/42973) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC

        - Fix the issue that TiCDC cannot create a changefeed with a downstream Kafka-on-Pulsar [#8892](https://github.com/pingcap/tiflow/issues/8892) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the issue that TiCDC cannot automatically recover when PD address or leader fails [#8812](https://github.com/pingcap/tiflow/issues/8812) [#8877](https://github.com/pingcap/tiflow/issues/8877) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that when the downstream is Kafka, TiCDC queries the downstream metadata too frequently and causes excessive workload in the downstream [#8957](https://github.com/pingcap/tiflow/issues/8957) [#8959](https://github.com/pingcap/tiflow/issues/8959) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the issue that TiCDC gets stuck when PD fails such as network isolation or PD Owner node reboot [#8808](https://github.com/pingcap/tiflow/issues/8808) [#8812](https://github.com/pingcap/tiflow/issues/8812) [#8877](https://github.com/pingcap/tiflow/issues/8877) @[asddongmen](https://github.com/asddongmen)

    + TiDB Lightning

        - Fix the issue that in Logical Import Mode, deleting tables downstream during import might cause TiDB Lightning metadata not to be updated in time [#44614](https://github.com/pingcap/tidb/issues/44614) @[dsdashun](https://github.com/dsdashun)
        - Fix the issue that disk quota might be inaccurate due to competing conditions [#44867](https://github.com/pingcap/tidb/issues/44867) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue of `write to tikv with no leader returned` when importing a large amount of data [#43055](https://github.com/pingcap/tidb/issues/43055) @[lance6716](https://github.com/lance6716)
        - Fix a possible OOM problem when there is an unclosed delimiter in the data file [#40400](https://github.com/pingcap/tidb/issues/40400) @[buchuitoudegou](https://github.com/buchuitoudegou)
        - Fix the issue that OOM might occur when importing a wide table [#43728](https://github.com/pingcap/tidb/issues/43728) @[D3Hunter](https://github.com/D3Hunter)

    + TiDB Binlog

        - Fix the issue that the etcd client does not automatically synchronize the latest node information during initialization [#1236](https://github.com/pingcap/tidb-binlog/issues/1236) @[lichunzhu](https://github.com/lichunzhu)
        - Fix the panic issue of Drainer due to an old TiKV client version by upgrading the TiKV client [#1170](https://github.com/pingcap/tidb-binlog/issues/1170) @[lichunzhu](https://github.com/lichunzhu)
        - Fix the issue that unfiltered failed DDL statements cause task errors [#1228](https://github.com/pingcap/tidb-binlog/issues/1228) @[lichunzhu](https://github.com/lichunzhu)
