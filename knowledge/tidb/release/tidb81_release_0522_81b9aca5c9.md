# Bug fixes across TiDB, TiKV, PD, TiFlash, BR, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.0.md`
- Source Title: `TiDB 7.5.0 Release Notes`
- Source Heading Path: `TiDB 7.5.0 Release Notes > Bug fixes`
- Source Line Ranges: `236-295`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`, `tiflash`, `br`, `ticdc`
- Topic Tags: `bug-fixes`, `sql`, `transactions`, `placement-rules`, `dr-auto-sync`, `monitoring`, `trace`, `pitr`, `log-backup`, `replication`, `kafka`, `nfs`, `redo-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0522_81b9aca5c9`
- Source ID: `tidb-docs-8.1:releases/release-7.5.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `60b63974fede12cfb12cf871ecbfad8c0593352366ff27b5483fdf7d96c3e961`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.5.0 bug fix details across TiDB, TiKV, PD, TiFlash, BR, or TiCDC for a specific issue, error phrase, function, scheduler, or feature name mentioned in the release notes.
- Retrieval Keywords: TiDB 7.5.0 bug fixes, Can't find column GROUP_CONCAT, Sort operator crash during the spill process, non-integer clustered indexes split table, encoding time fields incorrect timezone information, INDEX_LOOKUP_HASH_JOIN incorrect memory usage estimation, UPDATE statements with subqueries incorrectly converted to PointGet, cached execution plans date types unix_timestamp incorrect results, recursive CTEs aggregate functions window functions, MySQL compression protocol large loads of data >=16M, cgroup resource limits systemd, TiKV pessimistic transaction mode prewrite requests data inconsistency, evict-leader-scheduler lose configuration, canSync hasMajority DR Auto-Sync Placement Rules, rule checker does not add Learners, TiDB Dashboard cannot read PD trace data correctly, available_stores DR Auto-Sync, UPPER LOWER inconsistent results between TiDB and TiFlash, PITR skip restoring CREATE INDEX DDL statement, log backup stuck large wide tables, TiCDC replicating data to Kafka stuck, kv-client.enable-multiplexing replication tasks get stuck, claim-check storage path misspelled, redo log enabled owner node gets stuck due to NFS failure
- Follow-up Guidance: The chunk enumerates component-specific fixes for TiDB, TiKV, PD, TiFlash, BR, and TiCDC in the TiDB 7.5.0 release notes.
- Classification Note: The classification is release/shared because the content is a release-note bug-fix summary spanning multiple components rather than a single feature document.

## Official Source Content

## Bug fixes

+ TiDB

    - Prohibit split table operations on non-integer clustered indexes [#47350](https://github.com/pingcap/tidb/issues/47350) @[tangenta](https://github.com/tangenta)
    - Fix the issue of encoding time fields with incorrect timezone information [#46033](https://github.com/pingcap/tidb/issues/46033) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the Sort operator might cause TiDB to crash during the spill process [#47538](https://github.com/pingcap/tidb/issues/47538) @[windtalker](https://github.com/windtalker)
    - Fix the issue that TiDB returns `Can't find column` for queries with `GROUP_CONCAT` [#41957](https://github.com/pingcap/tidb/issues/41957) @[AilinKid](https://github.com/AilinKid)
    - Fix the panic issue of `batch-client` in `client-go` [#47691](https://github.com/pingcap/tidb/issues/47691) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue of incorrect memory usage estimation in `INDEX_LOOKUP_HASH_JOIN` [#47788](https://github.com/pingcap/tidb/issues/47788) @[SeaRise](https://github.com/SeaRise)
    - Fix the issue of uneven workload caused by the rejoining of a TiFlash node that has been offline for a long time [#35418](https://github.com/pingcap/tidb/issues/35418) @[windtalker](https://github.com/windtalker)
    - Fix the issue that the chunk cannot be reused when the HashJoin operator performs probe [#48082](https://github.com/pingcap/tidb/issues/48082) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the `COALESCE()` function returns incorrect result type for `DATE` type parameters [#46475](https://github.com/pingcap/tidb/issues/46475) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that `UPDATE` statements with subqueries are incorrectly converted to PointGet [#48171](https://github.com/pingcap/tidb/issues/48171) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that incorrect results are returned when the cached execution plans contain the comparison between date types and `unix_timestamp` [#48165](https://github.com/pingcap/tidb/issues/48165) @[qw4990](https://github.com/qw4990)
    - Fix the issue that an error is reported when default inline common table expressions (CTEs) with aggregate functions or window functions are referenced by recursive CTEs [#47881](https://github.com/pingcap/tidb/issues/47881) @[elsa0520](https://github.com/elsa0520)
    - Fix the issue that the optimizer mistakenly selects IndexFullScan to reduce sort introduced by window functions [#46177](https://github.com/pingcap/tidb/issues/46177) @[qw4990](https://github.com/qw4990)
    - Fix the issue that multiple references to CTEs result in incorrect results due to condition pushdown of CTEs [#47881](https://github.com/pingcap/tidb/issues/47881) @[winoros](https://github.com/winoros)
    - Fix the issue that the MySQL compression protocol cannot handle large loads of data (>=16M) [#47152](https://github.com/pingcap/tidb/issues/47152) [#47157](https://github.com/pingcap/tidb/issues/47157) [#47161](https://github.com/pingcap/tidb/issues/47161) @[dveeden](https://github.com/dveeden)
    - Fix the issue that TiDB does not read `cgroup` resource limits when it is started with `systemd` [#47442](https://github.com/pingcap/tidb/issues/47442) @[hawkingrei](https://github.com/hawkingrei)

+ TiKV

    - Fix the issue that retrying prewrite requests in the pessimistic transaction mode might cause the risk of data inconsistency in rare cases [#11187](https://github.com/tikv/tikv/issues/11187) @[MyonKeminta](https://github.com/MyonKeminta)

+ PD

    - Fix the issue that `evict-leader-scheduler` might lose configuration [#6897](https://github.com/tikv/pd/issues/6897) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that after a store goes offline, the monitoring metric of its statistics is not deleted [#7180](https://github.com/tikv/pd/issues/7180) @[rleungx](https://github.com/rleungx)
    - Fix the issue that `canSync` and `hasMajority` might be calculated incorrectly for clusters adopting the Data Replication Auto Synchronous (DR Auto-Sync) mode when the configuration of Placement Rules is complex [#7201](https://github.com/tikv/pd/issues/7201) @[disksing](https://github.com/disksing)
    - Fix the issue that the rule checker does not add Learners according to the configuration of Placement Rules [#7185](https://github.com/tikv/pd/issues/7185) @[nolouch](https://github.com/nolouch)
    - Fix the issue that TiDB Dashboard cannot read PD `trace` data correctly [#7253](https://github.com/tikv/pd/issues/7253) @[nolouch](https://github.com/nolouch)
    - Fix the issue that PD might panic due to empty Regions obtained internally [#7261](https://github.com/tikv/pd/issues/7261) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that `available_stores` is calculated incorrectly for clusters adopting the Data Replication Auto Synchronous (DR Auto-Sync) mode [#7221](https://github.com/tikv/pd/issues/7221) @[disksing](https://github.com/disksing)
    - Fix the issue that PD might delete normal Peers when TiKV nodes are unavailable [#7249](https://github.com/tikv/pd/issues/7249) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that adding multiple TiKV nodes to a large cluster might cause TiKV heartbeat reporting to become slow or stuck [#7248](https://github.com/tikv/pd/issues/7248) @[rleungx](https://github.com/rleungx)

+ TiFlash

    - Fix the issue that the `UPPER()` and `LOWER()` functions return inconsistent results between TiDB and TiFlash [#7695](https://github.com/pingcap/tiflash/issues/7695) @[windtalker](https://github.com/windtalker)
    - Fix the issue that executing queries on empty partitions causes query failure [#8220](https://github.com/pingcap/tiflash/issues/8220) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the panic issue caused by table creation failure when replicating TiFlash replicas [#8217](https://github.com/pingcap/tiflash/issues/8217) @[hongyunyan](https://github.com/hongyunyan)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that PITR might skip restoring the `CREATE INDEX` DDL statement [#47482](https://github.com/pingcap/tidb/issues/47482) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that the log backup might get stuck in some scenarios when backing up large wide tables [#15714](https://github.com/tikv/tikv/issues/15714) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC
        - Fix the performance issue caused by accessing NFS directories when replicating data to an object store sink [#10041](https://github.com/pingcap/tiflow/issues/10041) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that the storage path is misspelled when `claim-check` is enabled [#10036](https://github.com/pingcap/tiflow/issues/10036) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that TiCDC scheduling is not balanced in some cases [#9845](https://github.com/pingcap/tiflow/issues/9845) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that TiCDC might get stuck when replicating data to Kafka [#9855](https://github.com/pingcap/tiflow/issues/9855) @[hicqu](https://github.com/hicqu)
        - Fix the issue that the TiCDC processor might panic in some cases [#9849](https://github.com/pingcap/tiflow/issues/9849) [#9915](https://github.com/pingcap/tiflow/issues/9915) @[hicqu](https://github.com/hicqu) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that enabling `kv-client.enable-multiplexing` causes replication tasks to get stuck [#9673](https://github.com/pingcap/tiflow/issues/9673) @[fubinzh](https://github.com/fubinzh)
        - Fix the issue that an owner node gets stuck due to NFS failure when the redo log is enabled [#9886](https://github.com/pingcap/tiflow/issues/9886) @[3AceShowHand](https://github.com/3AceShowHand)
