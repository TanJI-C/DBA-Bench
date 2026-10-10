# Bug fixes for Dashboard, TiFlash, BR, TiCDC, Dumpling, and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.9.md`
- Source Title: `TiDB 4.0.9 Release Notes`
- Source Heading Path: `TiDB 4.0.9 Release Notes > Bug Fixes`
- Source Line Ranges: `185-225`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `tiflash`, `br`, `ticdc`, `dumpling`, `lightning`, `tikv`, `pd`, `tidb`
- Topic Tags: `bug-fixes`, `ui`, `memory-usage`, `backup-restore`, `changefeed`, `etcd`, `kafka`, `import`, `gc-ttl`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0196_68fed3a32e`
- Source ID: `tidb-docs-8.1:releases/release-4.0.9.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9bc9e769142283e2583560ebaaad12b6bc4114e6100928730e889f1b29e275c7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.9#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.9.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.9 bug fixes for TiDB Dashboard, TiFlash, BR, TiCDC, Dumpling, or TiDB Lightning, especially issues with UI display, memory usage, changefeed replication, Kafka retry behavior, etcd watch memory, S3 secret access keys, blocked dumps, or GC life time TTL.
- Retrieval Keywords: TiDB 4.0.9 Bug Fixes, TiDB Dashboard display issue of time Chinese language, browser compatibility notice does not work, transaction start_ts incorrectly displayed, SQL texts incorrectly formatted, INFORMATION_SCHEMA.CLUSTER_HARDWARE disks not in use, Delta Cache memory usage estimate smaller than actual, thread information statistics memory leak, BR special characters in S3 secret access keys, TiCDC multiple owners owner campaign key deleted, TiCDC fail to continue replicating data when TiKV node crashes or recovers from crash, metadata repeatedly flushed to etcd before a table is initialized, replication interruption early GC latency updating TableInfo, schema storage costs too much memory when DDL operations are frequent, goroutine leak when a changefeed is paused or stopped, maximum retry timeout 600 seconds Kafka producer, Kafka batch size does not take effect, row change might be lost when network between TiCDC and PD has jitter, TiCDC process might exit when network between TiCDC and PD is not stable, singleton PD client replication block, etcd watch client too much memory, Dumpling connection to the MySQL database server is closed blocked, TiDB Lightning wrong field information, GC life time TTL does not take effect, Local-backend mode panic when manually stops running TiDB Lightning
- Follow-up Guidance: 
- Classification Note: This is a release-notes bug-fix chunk for self-managed tools and components, continuing the TiDB 4.0.9 Bug Fixes section beyond TiDB, TiKV, and PD.

## Official Source Content

- Fix a display issue of time in the Chinese language [#755](https://github.com/pingcap/tidb-dashboard/pull/755)
    - Fix a bug that the browser compatibility notice does not work [#776](https://github.com/pingcap/tidb-dashboard/pull/776)
    - Fix the issue that the transaction `start_ts` is incorrectly displayed in some scenarios [#793](https://github.com/pingcap/tidb-dashboard/pull/793)
    - Fix the issue that some SQL texts are incorrectly formatted [#805](https://github.com/pingcap/tidb-dashboard/pull/805)

+ TiFlash

    - Fix the issue that `INFORMATION_SCHEMA.CLUSTER_HARDWARE` might contain the information of disks that are not in use
    - Fix the issue that the estimate on memory usage of Delta Cache is smaller than the actual usage
    - Fix the memory leak caused by thread information statistics

+ Tools

    + Backup & Restore (BR)

        - Fix the failure caused by special characters in S3 secret access keys [#617](https://github.com/pingcap/br/pull/617)

    + TiCDC

        - Fix the issue that multiple owners might exist when the owner campaign key is deleted [#1104](https://github.com/pingcap/tiflow/pull/1104)
        - Fix a bug that TiCDC might fail to continue replicating data when a TiKV node crashes or recovers from a crash. This bug only exists in v4.0.8. [#1198](https://github.com/pingcap/tiflow/pull/1198)
        - Fix the issue that the metadata is repeatedly flushed to etcd before a table is initialized [#1191](https://github.com/pingcap/tiflow/pull/1191)
        - Fix an issue of replication interruption caused by early GC or the latency of updating `TableInfo` when the schema storage caches TiDB tables [#1114](https://github.com/pingcap/tiflow/pull/1114)
        - Fix the issue that the schema storage costs too much memory when DDL operations are frequent [#1127](https://github.com/pingcap/tiflow/pull/1127)
        - Fix the goroutine leak when a changefeed is paused or stopped [#1075](https://github.com/pingcap/tiflow/pull/1075)
        - Increase the maximum retry timeout to 600 seconds in Kafka producer to prevent replication interruption caused by the service or network jitter in the downstream Kafka [#1118](https://github.com/pingcap/tiflow/pull/1118)
        - Fix a bug that the Kafka batch size does not take effect [#1112](https://github.com/pingcap/tiflow/pull/1112)
        - Fix a bug that some tables' row change might be lost when the network between TiCDC and PD has jitter and when there are paused changefeeds being resumed at the same time [#1213](https://github.com/pingcap/tiflow/pull/1213)
        - Fix a bug that the TiCDC process might exit when the network between TiCDC and PD is not stable [#1218](https://github.com/pingcap/tiflow/pull/1218)
        - Use a singleton PD client in TiCDC and fix a bug that TiCDC closes PD client by accident which causes replication block [#1217](https://github.com/pingcap/tiflow/pull/1217)
        - Fix a bug that the TiCDC owner might consume too much memory in the etcd watch client [#1224](https://github.com/pingcap/tiflow/pull/1224)

    + Dumpling

        - Fix the issue that Dumpling might get blocked when its connection to the MySQL database server is closed [#190](https://github.com/pingcap/dumpling/pull/190)

    + TiDB Lightning

        - Fix the issue that keys are encoded using the wrong field information [#437](https://github.com/pingcap/tidb-lightning/pull/437)
        - Fix the issue that GC life time TTL does not take effect [#448](https://github.com/pingcap/tidb-lightning/pull/448)
        - Fix the issue that causes panic when manually stops the running TiDB Lightning in the Local-backend mode [#484](https://github.com/pingcap/tidb-lightning/pull/484)
