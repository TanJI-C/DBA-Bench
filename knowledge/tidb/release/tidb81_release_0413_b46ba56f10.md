# 6.5.9 bug fixes across TiDB, TiKV, PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.9.md`
- Source Title: `TiDB 6.5.9 Release Notes`
- Source Heading Path: `TiDB 6.5.9 Release Notes > Bug fixes`
- Source Line Ranges: `83-137`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`
- Topic Tags: `bug-fixes`, `cte`, `panic`, `wal`, `timezone`, `metrics`, `json`, `transactions`, `scaling`, `data-race`, `deprecated-config`, `replica-migration`, `remote-read`, `chunk-encoding`, `backup`, `log-backup`, `gc-safepoint`, `changefeed`, `storage-sink`, `syncpoint`, `csv`, `azure`, `gcs`, `data-loss`, `file-scan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0413_b46ba56f10`
- Source ID: `tidb-docs-8.1:releases/release-6.5.9.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4dd90056e1e2271eda37efdcf481d9eef3b766fe55180edf91fd35e2f3a00e5e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.9#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.9.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 6.5.9 bug-fix list across TiDB, TiKV, PD, TiFlash, BR, TiCDC, DM, and TiDB Lightning for issues such as CTE panic, WAL corruption, timezone conversion, monitoring metrics, SHOW CONFIG output, replica migration panic, log backup, changefeed, storage sink, and file scanning.
- Retrieval Keywords: TiDB 6.5.9 bug fixes, executing queries containing CTEs causes TiDB to panic, #41688, inactive Write Ahead Logs WALs in RocksDB might corrupt data, #16705, TiKV converts the time zone incorrectly for Brazil and Egypt, #16220, tikv_unified_read_pool_thread_count has no data, #16629, JSON integers greater than INT64 but less than UINT64 parsed as FLOAT64, #16512, optimistic transaction atomicity broken resolving lock Async Commit 1PC, #16620, PD scaling progress is not correctly displayed, #7726, MergeLabels data race, #7535, learner-peer-count does not synchronize the old value after a leader switch, #7728, SHOW CONFIG includes deprecated configuration item trace-region-flow, #7917, TiFlash panic unstable network connections with PD during replica migration, #8323, TiFlash crash due to data race in remote reads, #8685, ENUM column crash during chunk encoding, #8674, TIME column precision modified queries might fail after Region migration split merge, #8601, BR removing a log backup task after it is paused does not immediately restore the GC safepoint, #52082, stopping a log backup task causes TiDB to crash, #50839, snapshot lost caused by GC not reported in time when resuming a changefeed, #10463, Syncpoint table might be incorrectly replicated, #10576, TiCDC cannot access Azure and GCS properly in storage sink scenarios, #10592, data is lost when the upstream primary key is of binary type, #10672, TiDB Lightning invalid symbolic link files during file scanning, #49423
- Follow-up Guidance: The source lists component-specific fixes for TiDB, TiKV, PD, TiFlash, BR, TiCDC, DM, and TiDB Lightning, each with the affected issue description and GitHub issue number.
- Classification Note: This chunk is classified as a release note because the official content is a consolidated TiDB 6.5.9 bug-fix summary grouped by component and tool.

## Official Source Content

- Fix the issue that executing queries containing CTEs causes TiDB to panic [#41688](https://github.com/pingcap/tidb/issues/41688) @[srstack](https://github.com/srstack)

+ TiKV

    - Fix the issue that after the process of destroying Peer is interrupted by applying snapshots, it does not resume even after applying snapshots is complete [#16561](https://github.com/tikv/tikv/issues/16561) @[tonyxuqqi](https://github.com/tonyxuqqi)
    - Fix the issue that inactive Write Ahead Logs (WALs) in RocksDB might corrupt data [#16705](https://github.com/tikv/tikv/issues/16705) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that TiKV converts the time zone incorrectly for Brazil and Egypt [#16220](https://github.com/tikv/tikv/issues/16220) @[overvenus](https://github.com/overvenus)
    - Fix the issue that the monitoring metric `tikv_unified_read_pool_thread_count` has no data in some cases [#16629](https://github.com/tikv/tikv/issues/16629) @[YuJuncen](https://github.com/YuJuncen)
    - Fix the issue that JSON integers greater than the maximum `INT64` value but less than the maximum `UINT64` value are parsed as `FLOAT64` by TiKV, resulting in inconsistency with TiDB [#16512](https://github.com/tikv/tikv/issues/16512) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that during the execution of an optimistic transaction, if other transactions initiate the resolving lock operation on it, there is a small chance that the atomicity of the transaction might be broken if the transaction's primary key has data that was previously committed in Async Commit or 1PC mode [#16620](https://github.com/tikv/tikv/issues/16620) @[MyonKeminta](https://github.com/MyonKeminta)

+ PD

    - Fix the issue that the scaling progress is not correctly displayed [#7726](https://github.com/tikv/pd/issues/7726) @[CabinfeverB](https://github.com/CabinfeverB)
    - Fix the issue that data race occurs when the `MergeLabels` function is called [#7535](https://github.com/tikv/pd/issues/7535) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that the PD monitoring item `learner-peer-count` does not synchronize the old value after a leader switch [#7728](https://github.com/tikv/pd/issues/7728) @[CabinfeverB](https://github.com/CabinfeverB)
    - Fix the issue that the query result of `SHOW CONFIG` includes the deprecated configuration item `trace-region-flow` [#7917](https://github.com/tikv/pd/issues/7917) @[rleungx](https://github.com/rleungx)

+ TiFlash

    - Fix the issue that TiFlash might panic due to unstable network connections with PD during replica migration [#8323](https://github.com/pingcap/tiflash/issues/8323) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash might crash due to data race in case of remote reads [#8685](https://github.com/pingcap/tiflash/issues/8685) @[solotzg](https://github.com/solotzg)
    - Fix the issue that the `ENUM` column might cause TiFlash to crash during chunk encoding [#8674](https://github.com/pingcap/tiflash/issues/8674) @[yibin87](https://github.com/yibin87)
    - Fix the issue that TiFlash might panic when you insert data to columns with invalid default values in non-strict `sql_mode` [#8803](https://github.com/pingcap/tiflash/issues/8803) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that if Region migration, split, or merge occurs after the precision of a `TIME` column is modified, queries might fail [#8601](https://github.com/pingcap/tiflash/issues/8601) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that too many logs are printed when a full backup fails [#51572](https://github.com/pingcap/tidb/issues/51572) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that removing a log backup task after it is paused does not immediately restore the GC safepoint [#52082](https://github.com/pingcap/tidb/issues/52082) @[3pointer](https://github.com/3pointer)
        - Fix the issue that BR could not back up the `AUTO_RANDOM` ID allocation progress in a union clustered index that contains an `AUTO_RANDOM` column [#52255](https://github.com/pingcap/tidb/issues/52255) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that stopping a log backup task causes TiDB to crash [#50839](https://github.com/pingcap/tidb/issues/50839) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that TiKV panics when a full backup fails to find a peer in some extreme cases [#16394](https://github.com/tikv/tikv/issues/16394) @[Leavrth](https://github.com/Leavrth)

    + TiCDC

        - Fix the issue that `snapshot lost caused by GC` is not reported in time when resuming a changefeed and the `checkpoint-ts` of the changefeed is smaller than the GC safepoint of TiDB [#10463](https://github.com/pingcap/tiflow/issues/10463) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that data is written to a wrong CSV file due to wrong BarrierTS in scenarios where DDL statements are executed frequently [#10668](https://github.com/pingcap/tiflow/issues/10668) @[lidezhu](https://github.com/lidezhu)
        - Fix the issue that the Syncpoint table might be incorrectly replicated [#10576](https://github.com/pingcap/tiflow/issues/10576) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue TiCDC panics when scheduling table replication tasks [#10613](https://github.com/pingcap/tiflow/issues/10613) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that data race in the KV client causes TiCDC to panic [#10718](https://github.com/pingcap/tiflow/issues/10718) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the file sequence number generated by the storage service might not increment correctly when using the storage sink [#10352](https://github.com/pingcap/tiflow/issues/10352) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that TiCDC cannot access Azure and GCS properly in storage sink scenarios [#10592](https://github.com/pingcap/tiflow/issues/10592) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that the old value part of `open-protocol` incorrectly outputs the default value according to the `STRING` type instead of its actual type [#10803](https://github.com/pingcap/tiflow/issues/10803) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that a changefeed with eventual consistency enabled might fail when the object storage sink encounters a temporary failure [#10710](https://github.com/pingcap/tiflow/issues/10710) @[CharlesCheung96](https://github.com/CharlesCheung96)

    + TiDB Data Migration (DM)

        - Fix the issue that data is lost when the upstream primary key is of binary type [#10672](https://github.com/pingcap/tiflow/issues/10672) @[GMHDBJD](https://github.com/GMHDBJD)

    + TiDB Lightning

        - Fix the issue that TiDB Lightning reports an error when encountering invalid symbolic link files during file scanning [#49423](https://github.com/pingcap/tidb/issues/49423) @[lance6716](https://github.com/lance6716)
