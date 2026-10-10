# Improvements across TiDB cluster components and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Improvements`
- Source Line Ranges: `427-502`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`, `dumpling`, `ecosystem`
- Topic Tags: `improvements`, `ttl`, `add-index`, `plan-cache`, `partitioned-tables`, `flashback-cluster`, `raftstore`, `block-cache`, `memory-threshold`, `gc-tuner`, `keyspace`, `mvcc`, `pitr`, `replication`, `alerts`, `relay`, `import`, `csv`, `foreign-keys`, `consistency-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0424_b3d666ebe4`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84f9af7106e6a86c6a4caebf473ca54daa35e44b05a6d395d00d1db49532f1f5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 6.6.0 improvements summary across cluster components and tools such as TiDB, TiKV, PD, TiFlash, BR, TiCDC, DM, Lightning, Dumpling, and sync-diff-inspector.
- Retrieval Keywords: TiDB 6.6.0 Improvements, TTL background cleaning tasks, distributed data backfill for ADD INDEX, CURDATE() as the default value of a column, partial order prop push down LIST-type partitioned tables, optimizer hints and execution plan bindings, plan cache strategy, region cache memory leak, MODIFY COLUMN is not supported on partitioned tables, FLASHBACK CLUSTER retries min-resolved-ts, storage.block-cache.capacity, region-split-size, enable-region-bucket, Raftstore asynchronous writes priority scheduling, evict-slow-trend-scheduler, global memory threshold, GC Tuner, keyspace manager, independent MVCC bitmap filter, PITR recovery, batch UPDATE DML statements, MQ sink and MySQL sink asynchronous mode, DM alert rules automatically recoverable errors, async/batch relay writer, lightning.max-error, CSV data files with BOM headers, foreign keys during import, skip-non-existing-table
- Follow-up Guidance: The source groups the improvements by component and tool, including TiDB, TiKV, PD, TiFlash, BR, TiCDC, DM, TiDB Lightning, Dumpling, and sync-diff-inspector.
- Classification Note: This is classified as a release improvements chunk because it enumerates new optimizations and feature enhancements introduced in TiDB 6.6.0 across multiple components and tools.

## Official Source Content

## Improvements

+ TiDB

    - Improve the scheduling mechanism of TTL background cleaning tasks to allow the cleaning task of a single table to be split into several sub-tasks and scheduled to run on multiple TiDB nodes simultaneously [#40361](https://github.com/pingcap/tidb/issues/40361) @[YangKeao](https://github.com/YangKeao)
    - Optimize the column name display of the result returned by running multi-statements after setting a non-default delimiter [#39662](https://github.com/pingcap/tidb/issues/39662) @[mjonss](https://github.com/mjonss)
    - Optimize the execution efficiency of statements after warning messages are generated [#39702](https://github.com/pingcap/tidb/issues/39702) @[tiancaiamao](https://github.com/tiancaiamao)
    - Support distributed data backfill for `ADD INDEX` (experimental) [#37119](https://github.com/pingcap/tidb/issues/37119) @[zimulala](https://github.com/zimulala)
    - Support using `CURDATE()` as the default value of a column [#38356](https://github.com/pingcap/tidb/issues/38356) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - `partial order prop push down` now supports the LIST-type partitioned tables [#40273](https://github.com/pingcap/tidb/issues/40273) @[winoros](https://github.com/winoros)
    - Add error messages for conflicts between optimizer hints and execution plan bindings [#40910](https://github.com/pingcap/tidb/issues/40910) @[Reminiscent](https://github.com/Reminiscent)
    - Optimize the plan cache strategy to avoid non-optimal plans when using plan cache in some scenarios [#40312](https://github.com/pingcap/tidb/pull/40312) [#40218](https://github.com/pingcap/tidb/pull/40218) [#40280](https://github.com/pingcap/tidb/pull/40280) [#41136](https://github.com/pingcap/tidb/pull/41136) [#40686](https://github.com/pingcap/tidb/pull/40686) @[qw4990](https://github.com/qw4990)
    - Clear expired region cache regularly to avoid memory leak and performance degradation [#40461](https://github.com/pingcap/tidb/issues/40461) @[sticnarf](https://github.com/sticnarf)
    - `MODIFY COLUMN` is not supported on partitioned tables [#39915](https://github.com/pingcap/tidb/issues/39915) @[wjhuang2016](https://github.com/wjhuang2016)
    - Disable renaming of columns that partition tables depend on [#40150](https://github.com/pingcap/tidb/issues/40150) @[mjonss](https://github.com/mjonss)
    - Refine the error message reported when a column that a partitioned table depends on is deleted [#38739](https://github.com/pingcap/tidb/issues/38739) @[jiyfhust](https://github.com/jiyfhust)
    - Add a mechanism that `FLASHBACK CLUSTER` retries when it fails to check the `min-resolved-ts` [#39836](https://github.com/pingcap/tidb/issues/39836) @[Defined2014](https://github.com/Defined2014)

+ TiKV

    - Optimize the default values of some parameters in partitioned-raft-kv mode: the default value of the TiKV configuration item `storage.block-cache.capacity` is adjusted from 45% to 30%, and the default value of `region-split-size` is adjusted from `96MiB` adjusted to `10GiB`. When using raft-kv mode and `enable-region-bucket` is `true`, `region-split-size` is adjusted to 1 GiB by default. [#12842](https://github.com/tikv/tikv/issues/12842) @[tonyxuqqi](https://github.com/tonyxuqqi)
    - Support priority scheduling in Raftstore asynchronous writes [#13730](https://github.com/tikv/tikv/issues/13730) @[Connor1996](https://github.com/Connor1996)
    - Support starting TiKV on a CPU with less than 1 core [#13586](https://github.com/tikv/tikv/issues/13586) [#13752](https://github.com/tikv/tikv/issues/13752) [#14017](https://github.com/tikv/tikv/issues/14017) @[andreid-db](https://github.com/andreid-db)
    - Optimize the new detection mechanism of Raftstore slow score and add `evict-slow-trend-scheduler` [#14131](https://github.com/tikv/tikv/issues/14131) @[innerr](https://github.com/innerr)
    - Force the block cache of RocksDB to be shared and no longer support setting the block cache separately according to CF [#12936](https://github.com/tikv/tikv/issues/12936) @[busyjay](https://github.com/busyjay)

+ PD

    - Support managing the global memory threshold to alleviate the OOM problem (experimental) [#5827](https://github.com/tikv/pd/issues/5827) @[hnes](https://github.com/hnes)
    - Add the GC Tuner to alleviate the GC pressure (experimental) [#5827](https://github.com/tikv/pd/issues/5827) @[hnes](https://github.com/hnes)
    - Add the `evict-slow-trend-scheduler` scheduler to detect and schedule abnormal nodes [#5808](https://github.com/tikv/pd/pull/5808) @[innerr](https://github.com/innerr)
    - Add the keyspace manager to manage keyspace [#5293](https://github.com/tikv/pd/issues/5293) @[AmoebaProtozoa](https://github.com/AmoebaProtozoa)

+ TiFlash

    - Support an independent MVCC bitmap filter that decouples the MVCC filtering operations in the TiFlash data scanning process, which provides the foundation for future optimization of the data scanning process [#6296](https://github.com/pingcap/tiflash/issues/6296) @[JinheLin](https://github.com/JinheLin)
    - Reduce the memory usage of TiFlash by up to 30% when there is no query [#6589](https://github.com/pingcap/tiflash/pull/6589) @[hongyunyan](https://github.com/hongyunyan)

+ Tools

    + Backup & Restore (BR)

        - Optimize the concurrency of downloading log backup files on the TiKV side to improve the performance of PITR recovery in regular scenarios [#14206](https://github.com/tikv/tikv/issues/14206) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC

        - Support batch `UPDATE` DML statements to improve TiCDC replication performance [#8084](https://github.com/pingcap/tiflow/issues/8084) @[amyangfei](https://github.com/amyangfei)
        - Implement MQ sink and MySQL sink in the asynchronous mode to improve the sink throughput [#5928](https://github.com/pingcap/tiflow/issues/5928) @[hicqu](https://github.com/hicqu) @[hi-rustin](https://github.com/Rustin170506)

    + TiDB Data Migration (DM)

        - Optimize DM alert rules and content [#7376](https://github.com/pingcap/tiflow/issues/7376) @[D3Hunter](https://github.com/D3Hunter)

             Previously, alerts similar to "DM_XXX_process_exits_with_error" were raised whenever a related error occurred. But some alerts are caused by idle database connections, which can be recovered after reconnecting. To reduce these kinds of alerts, DM divides errors into two types: automatically recoverable errors and unrecoverable errors:

            - For an error that is automatically recoverable, DM reports the alert only if the error occurs more than 3 times within 2 minutes.
            - For an error that is not automatically recoverable, DM maintains the original behavior and reports the alert immediately.

        - Optimize relay performance by adding the async/batch relay writer [#4287](https://github.com/pingcap/tiflow/issues/4287) @[GMHDBJD](https://github.com/GMHDBJD)

    + TiDB Lightning
        - Physical Import Mode supports keyspace [#40531](https://github.com/pingcap/tidb/issues/40531) @[iosmanthus](https://github.com/iosmanthus)
        - Support setting the maximum number of conflicts by `lightning.max-error` [#40743](https://github.com/pingcap/tidb/issues/40743) @[dsdashun](https://github.com/dsdashun)
        - Support importing CSV data files with BOM headers [#40744](https://github.com/pingcap/tidb/issues/40744) @[dsdashun](https://github.com/dsdashun)
        - Optimize the processing logic when encountering TiKV flow-limiting errors and try other available regions instead [#40205](https://github.com/pingcap/tidb/issues/40205) @[lance6716](https://github.com/lance6716)
        - Disable checking the table foreign keys during import [#40027](https://github.com/pingcap/tidb/issues/40027) @[sleepymole](https://github.com/sleepymole)

    + Dumpling

        - Support exporting settings for foreign keys [#39913](https://github.com/pingcap/tidb/issues/39913) @[lichunzhu](https://github.com/lichunzhu)

    + sync-diff-inspector

        - Add a new parameter `skip-non-existing-table` to control whether to skip checking upstream and downstream data consistency when tables in the downstream do not exist in the upstream [#692](https://github.com/pingcap/tidb-tools/issues/692) @[lichunzhu](https://github.com/lichunzhu) @[liumengya94](https://github.com/liumengya94)
