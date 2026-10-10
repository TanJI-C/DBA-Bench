# Improvements across TiDB ecosystem components

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.6.md`
- Source Title: `TiDB 7.1.6 Release Notes`
- Source Heading Path: `TiDB 7.1.6 Release Notes > Improvements`
- Source Line Ranges: `24-71`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `br`, `ticdc`, `dm`
- Topic Tags: `improvements`, `optimizer`, `mpp`, `show-create-table`, `placement-rules`, `statistics-loading`, `slow-logs`, `rocksdb-compaction`, `restart-stability`, `memory-usage`, `function-execution`, `tls-certificates`, `join-cancel`, `short-query-performance`, `garbage-collection`, `log-backup`, `data-recovery`, `dns-retry`, `region-leader-retry`, `domain-loading`, `disk-space-check`, `alibaba-cloud-credentials`, `raw-events`, `redo-logs`, `add-index-ddl`, `mysql-8-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0480_b1204f08f1`
- Source ID: `tidb-docs-8.1:releases/release-7.1.6.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6ce62ae5015a32c0af7664c0a207965cd863e1f54684660cae0c40eacc55cbc4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.6#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 7.1.6 improvements across TiDB, TiKV, TiFlash, BR, TiCDC, or DM, including optimizer behavior, MPP balancing, SHOW CREATE TABLE compatibility, backup and restore retries, raw events, redo logs, and MySQL 8.0 password support.
- Retrieval Keywords: TiDB 7.1.6 Improvements, TiDB improvements, TiKV improvements, TiFlash improvements, BR improvements, TiCDC improvements, DM improvements, equality conditions, TopN, modified row count, MPP load balancing, SHOW CREATE TABLE, expression default values, TiFlash placement rules, TRUNCATE, DROP, partitioned tables, loading statistics, slow logs, peer and store messages, RocksDB compaction, disk space reclamation, restarting TiKV, memory usage, LENGTH(), ASCII(), TLS, certificates, JOIN operator, short query performance, clustered indexes, log backup, merge operations, empty SST files, DNS errors, absence of a leader in a Region, br log restore, domain, disk space, Alibaba Cloud access credentials, raw events, Message Queue, cloud storage, redo logs, ADD INDEX DDL, SUPER permission, go-mysql 1.9.1, MySQL server 8.0, passwords longer than 19 characters
- Follow-up Guidance: 
- Classification Note: This is a release-note improvements section listing component-specific enhancements in TiDB 7.1.6 for TiDB, TiKV, TiFlash, Backup & Restore, TiCDC, and TiDB Data Migration.

## Official Source Content

## Improvements

+ TiDB

    - Adjust estimation results from 0 to 1 for equality conditions that do not hit TopN when statistics are entirely composed of TopN and the modified row count in the corresponding table statistics is non-zero [#47400](https://github.com/pingcap/tidb/issues/47400) @[terry1purcell](https://github.com/terry1purcell)
    - Remove stores without Regions during MPP load balancing [#52313](https://github.com/pingcap/tidb/issues/52313) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Improve the MySQL compatibility of expression default values displayed in the output of `SHOW CREATE TABLE` [#52939](https://github.com/pingcap/tidb/issues/52939) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - By batch deleting TiFlash placement rules, improve the processing speed of data GC after performing the `TRUNCATE` or `DROP` operation on partitioned tables [#54068](https://github.com/pingcap/tidb/issues/54068) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Improve sync load performance to reduce latency in loading statistics [#52294](https://github.com/pingcap/tidb/issues/52294) [hawkingrei](https://github.com/hawkingrei)

+ TiKV

    - Add slow logs for peer and store messages [#16600](https://github.com/tikv/tikv/issues/16600) @[Connor1996](https://github.com/Connor1996)
    - Optimize the compaction trigger mechanism of RocksDB to accelerate disk space reclamation when handling a large number of DELETE versions [#17269](https://github.com/tikv/tikv/issues/17269) @[AndreMouche](https://github.com/AndreMouche)
    - Optimize the jittery access delay when restarting TiKV due to waiting for the log to be applied, improving the stability of TiKV [#15874](https://github.com/tikv/tikv/issues/15874) @[LykxSassinator](https://github.com/LykxSassinator)
    - Remove unnecessary async blocks to reduce memory usage [#16540](https://github.com/tikv/tikv/issues/16540) @[overvenus](https://github.com/overvenus)

+ TiFlash

    - Optimize the execution efficiency of `LENGTH()` and `ASCII()` functions [#9344](https://github.com/pingcap/tiflash/issues/9344) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Mitigate the issue that TiFlash might panic due to updating certificates after TLS is enabled [#8535](https://github.com/pingcap/tiflash/issues/8535) @[windtalker](https://github.com/windtalker)
    - Improve the cancel mechanism of the JOIN operator, so that the JOIN operator can respond to cancel requests in a timely manner [#9430](https://github.com/pingcap/tiflash/issues/9430) @[windtalker](https://github.com/windtalker)
    - Reduce lock conflicts under highly concurrent data read operations and optimize short query performance [#9125](https://github.com/pingcap/tiflash/issues/9125) @[JinheLin](https://github.com/JinheLin)
    - Improve the garbage collection speed of outdated data in the background for tables with clustered indexes [#9529](https://github.com/pingcap/tiflash/issues/9529) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Enhance the tolerance of log backup to merge operations. When encountering a reasonably long merge operation, log backup tasks are less likely to enter the error state [#16554](https://github.com/tikv/tikv/issues/16554) @[YuJuncen](https://github.com/YuJuncen)
        - BR cleans up empty SST files during data recovery [#16005](https://github.com/tikv/tikv/issues/16005) @[Leavrth](https://github.com/Leavrth)
        - Increase the number of retries for failures caused by DNS errors [#53029](https://github.com/pingcap/tidb/issues/53029) @[YuJuncen](https://github.com/YuJuncen)
        - Increase the number of retries for failures caused by the absence of a leader in a Region [#54017](https://github.com/pingcap/tidb/issues/54017) @[Leavrth](https://github.com/Leavrth)
        - Except for the `br log restore` subcommand, all other `br log` subcommands support skipping the loading of the TiDB `domain` data structure to reduce memory consumption [#52088](https://github.com/pingcap/tidb/issues/52088) @[Leavrth](https://github.com/Leavrth)
        - Support checking whether the disk space in TiKV is sufficient before TiKV downloads each SST file. If the space is insufficient, BR terminates the restore and returns an error [#17224](https://github.com/tikv/tikv/issues/17224) @[RidRisR](https://github.com/RidRisR)
        - Support setting Alibaba Cloud access credentials through environment variables [#45551](https://github.com/pingcap/tidb/issues/45551) @[RidRisR](https://github.com/RidRisR)
        - Reduce unnecessary log printing during backup [#55902](https://github.com/pingcap/tidb/issues/55902) @[Leavrth](https://github.com/Leavrth)

    + TiCDC

        - Support directly outputting raw events when the downstream is a Message Queue (MQ) or cloud storage [#11211](https://github.com/pingcap/tiflow/issues/11211) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Improve memory stability during data recovery using redo logs to reduce the probability of OOM [#10900](https://github.com/pingcap/tiflow/issues/10900) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - When the downstream is TiDB with the `SUPER` permission granted, TiCDC supports querying the execution status of `ADD INDEX DDL` from the downstream database to avoid data replication failure due to timeout in retrying executing the DDL statement in some cases [#10682](https://github.com/pingcap/tiflow/issues/10682) @[CharlesCheung96](https://github.com/CharlesCheung96)

    + TiDB Data Migration (DM)

        - Upgrade `go-mysql` to 1.9.1 to support connecting to MySQL server 8.0 using passwords longer than 19 characters [#11603](https://github.com/pingcap/tiflow/pull/11603) @[fishiu](https://github.com/fishiu)
