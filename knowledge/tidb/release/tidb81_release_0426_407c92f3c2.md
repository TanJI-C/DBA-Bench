# Bug fixes across TiDB, TiKV, PD, TiFlash, BR, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Bug fixes`
- Source Line Ranges: `543-594`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`
- Topic Tags: `bug-fixes`, `scalability`, `performance`, `reliability`, `availability`, `sql`, `backup-restore`, `pitr`, `changefeed`, `network-traffic`, `memory-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0426_407c92f3c2`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0243efd68b65cec7d49794a97e1c661c98ab78a987d0891df1a47fce5e2b68e1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.6.0 bug fixes across TiDB, TiKV, PD, TiFlash, BR, or TiCDC related to specific errors, performance problems, memory usage, network traffic, PITR, restore, or changefeed behavior.
- Retrieval Keywords: TiDB 6.6.0 bug fixes, can't find proper physical plan, virtual columns, auto analyze graceful shutdown, IndexMerge memory limiting behaviors, SELECT * FROM table_name LIMIT 1 partitioned tables slow, const Enum cast, Resolved TS higher network traffic, failed pessimistic DML data inconsistency, Region Scatter redundant replicas, Online Unsafe Recovery auto-detect stuck, replace-down-peer slows down, ReportMinResolvedTS PD OOM, TiFlash system tables get stuck, semi-joins excessive memory Cartesian products, DECIMAL division not rounded, start_ts cannot uniquely identify an MPP query, BR restoring log backup hot Regions fail, PITR CA-bundles, PITR backup progress not to advance, resolve lock frequency too high, transaction_atomicity and protocol cannot be updated via the configuration file, redo log S3 storage failure, changefeed might get stuck, pull-based sink CPU usage memory control throughput
- Follow-up Guidance: The chunk groups fixes by component: TiDB, TiKV, PD, TiFlash, Backup & Restore (BR), and TiCDC.
- Classification Note: This is a release-notes bug-fix summary covering multiple shared components in TiDB 6.6.0 for self-managed deployments.

## Official Source Content

- Fix the issue that data race might occur when an index is added [#40879](https://github.com/pingcap/tidb/issues/40879) @[tangenta](https://github.com/tangenta)
    - Fix the `can't find proper physical plan` issue caused by virtual columns [#41014](https://github.com/pingcap/tidb/issues/41014) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that TiDB cannot restart after global bindings are created for partition tables in dynamic trimming mode [#40368](https://github.com/pingcap/tidb/issues/40368) @[Yisaer](https://github.com/Yisaer)
    - Fix the issue that `auto analyze` causes graceful shutdown to take a long time [#40038](https://github.com/pingcap/tidb/issues/40038) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the panic of the TiDB server when the IndexMerge operator triggers memory limiting behaviors [#41036](https://github.com/pingcap/tidb/pull/41036) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the `SELECT * FROM table_name LIMIT 1` query on partitioned tables is slow [#40741](https://github.com/pingcap/tidb/pull/40741) @[solotzg](https://github.com/solotzg)

+ TiKV

    - Fix an error that occurs when casting the `const Enum` type to other types [#14156](https://github.com/tikv/tikv/issues/14156) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that Resolved TS causes higher network traffic [#14092](https://github.com/tikv/tikv/issues/14092) @[overvenus](https://github.com/overvenus)
    - Fix the data inconsistency issue caused by network failure between TiDB and TiKV during the execution of a DML after a failed pessimistic DML [#14038](https://github.com/tikv/tikv/issues/14038) @[MyonKeminta](https://github.com/MyonKeminta)

+ PD

    - Fix the issue that the Region Scatter task generates redundant replicas unexpectedly [#5909](https://github.com/tikv/pd/issues/5909) @[HundunDM](https://github.com/HunDunDM)
    - Fix the issue that the Online Unsafe Recovery feature would get stuck and time out in `auto-detect` mode [#5753](https://github.com/tikv/pd/issues/5753) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that the execution `replace-down-peer` slows down under certain conditions [#5788](https://github.com/tikv/pd/issues/5788) @[HundunDM](https://github.com/HunDunDM)
    - Fix the PD OOM issue that occurs when the calls of `ReportMinResolvedTS` are too frequent [#5965](https://github.com/tikv/pd/issues/5965) @[HundunDM](https://github.com/HunDunDM)

+ TiFlash

    - Fix the issue that querying TiFlash-related system tables might get stuck [#6745](https://github.com/pingcap/tiflash/pull/6745) @[lidezhu](https://github.com/lidezhu)
    - Fix the issue that semi-joins use excessive memory when calculating Cartesian products [#6730](https://github.com/pingcap/tiflash/issues/6730) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that the result of the division operation on the DECIMAL data type is not rounded [#6393](https://github.com/pingcap/tiflash/issues/6393) @[LittleFall](https://github.com/LittleFall)
    - Fix the issue that `start_ts` cannot uniquely identify an MPP query in TiFlash queries, which might cause an MPP query to be incorrectly canceled [#43426](https://github.com/pingcap/tidb/issues/43426) @[hehechen](https://github.com/hehechen)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that when restoring log backup, hot Regions cause the restore to fail [#37207](https://github.com/pingcap/tidb/issues/37207) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that restoring data to a cluster on which the log backup is running causes the log backup file to be unrecoverable [#40797](https://github.com/pingcap/tidb/issues/40797) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that the PITR feature does not support CA-bundles [#38775](https://github.com/pingcap/tidb/issues/38775) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the panic issue caused by duplicate temporary tables during recovery [#40797](https://github.com/pingcap/tidb/issues/40797) @[joccau](https://github.com/joccau)
        - Fix the issue that PITR does not support configuration changes for PD clusters [#14165](https://github.com/tikv/tikv/issues/14165) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that the connection failure between PD and tidb-server causes PITR backup progress not to advance [#41082](https://github.com/pingcap/tidb/issues/41082) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that TiKV cannot listen to PITR tasks due to the connection failure between PD and TiKV [#14159](https://github.com/tikv/tikv/issues/14159) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that the frequency of `resolve lock` is too high when there is no PITR backup task in the TiDB cluster [#40759](https://github.com/pingcap/tidb/issues/40759) @[joccau](https://github.com/joccau)
        - Fix the issue that when a PITR backup task is deleted, the residual backup data causes data inconsistency in new tasks [#40403](https://github.com/pingcap/tidb/issues/40403) @[joccau](https://github.com/joccau)

    + TiCDC

        - Fix the issue that `transaction_atomicity` and `protocol` cannot be updated via the configuration file [#7935](https://github.com/pingcap/tiflow/issues/7935) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that precheck is not performed on the storage path of redo log [#6335](https://github.com/pingcap/tiflow/issues/6335) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue of insufficient duration that redo log can tolerate for S3 storage failure [#8089](https://github.com/pingcap/tiflow/issues/8089) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that changefeed might get stuck in special scenarios such as when scaling in or scaling out TiKV or TiCDC nodes [#8174](https://github.com/pingcap/tiflow/issues/8174) @[hicqu](https://github.com/hicqu)
        - Fix the issue of too high traffic among TiKV nodes [#14092](https://github.com/tikv/tikv/issues/14092) @[overvenus](https://github.com/overvenus)
        - Fix the performance issues of TiCDC in terms of CPU usage, memory control, and throughput when the pull-based sink is enabled [#8142](https://github.com/pingcap/tiflow/issues/8142) [#8157](https://github.com/pingcap/tiflow/issues/8157) [#8001](https://github.com/pingcap/tiflow/issues/8001) [#5928](https://github.com/pingcap/tiflow/issues/5928) @[hicqu](https://github.com/hicqu) @[hi-rustin](https://github.com/Rustin170506)

    + TiDB Data Migration (DM)
