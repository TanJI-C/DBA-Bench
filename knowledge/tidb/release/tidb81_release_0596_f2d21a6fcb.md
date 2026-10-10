# 8.1.0 improvements across TiDB, TiKV, PD, TiFlash, BR, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.0.md`
- Source Title: `TiDB 8.1.0 Release Notes`
- Source Heading Path: `TiDB 8.1.0 Release Notes > Improvements`
- Source Line Ranges: `210-251`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dashboard`, `sql`
- Topic Tags: `improvements`, `mysql-compatibility`, `indexes`, `dxf`, `optimizer`, `metrics`, `ldap`, `stability`, `pitr`, `redo-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0596_f2d21a6fcb`
- Source ID: `tidb-docs-8.1:releases/release-8.1.0.md#improvements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8b4514e3ec7d0ea7bd21ca4719fb10eba642b0283c802320b3f9ee850682097d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 8.1.0 improvements list across TiDB, TiKV, PD, TiFlash, BR, and TiCDC.
- Retrieval Keywords: TiDB 8.1.0 Improvements, SHOW CREATE TABLE foreign keys, SHOW CREATE TABLE expression default values, adding multiple indexes concurrently in the ingest mode, tidb_service_scope, Distributed eXecution Framework, DXF, DNF items always false, Optimizer Fix Controls, Index Merge, total_kv_read_wall_time, execution info, RU (max), Resource Control dashboard, LDAP authentication timeout, snapshot files in Raftstore threads, shutdown speed of TiKV, metrics for memory usage per thread, OperatorController, competition locks, TiFlash updating certificates after TLS is enabled, PITR, log backup, adding index acceleration, empty SST files, redo logs, OOM, transaction conflict scenarios
- Follow-up Guidance: The chunk groups improvements by component, including TiDB, TiKV, PD, TiFlash, BR, and TiCDC, with specific feature and stability enhancements for each.
- Classification Note: The official content is classified as an improvements section because it enumerates feature, compatibility, performance, observability, and stability enhancements introduced in TiDB 8.1.0.

## Official Source Content

## Improvements

+ TiDB

    - Improve the MySQL compatibility of foreign keys displayed in the output of `SHOW CREATE TABLE` [#51837](https://github.com/pingcap/tidb/issues/51837) @[negachov](https://github.com/negachov)
    - Improve the MySQL compatibility of expression default values displayed in the output of `SHOW CREATE TABLE` [#52939](https://github.com/pingcap/tidb/issues/52939) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Support adding multiple indexes concurrently in the ingest mode [#52596](https://github.com/pingcap/tidb/issues/52596) @[lance6716](https://github.com/lance6716)
    - Support configuring the system variable `tidb_service_scope` with various values, enhancing the utilization of the Distributed eXecution Framework (DXF) [#52441](https://github.com/pingcap/tidb/issues/52441) @[ywqzzy](https://github.com/ywqzzy)
    - Enhance the handling of DNF items that are always `false` by directly ignoring such filter conditions, thus avoiding unnecessary full table scans [#40997](https://github.com/pingcap/tidb/issues/40997) @[hi-rustin](https://github.com/Rustin170506)
    - Support using Optimizer Fix Controls to remove the limitation that the optimizer does not automatically choose Index Merge for a query when the optimizer can choose the single index scan method (other than full table scan) for the query [#52869](https://github.com/pingcap/tidb/issues/52869) @[time-and-fate](https://github.com/time-and-fate)
    - Add the `total_kv_read_wall_time` metric to the column `execution info` of Coprocessor operators [#28937](https://github.com/pingcap/tidb/issues/28937) @[cfzjywxk](https://github.com/cfzjywxk)
    - Add the `RU (max)` metric on the Resource Control dashboard [#49318](https://github.com/pingcap/tidb/issues/49318) @[nolouch](https://github.com/nolouch)
    - Add a timeout mechanism for LDAP authentication to avoid the issue of resource lock (RLock) not being released in time [#51883](https://github.com/pingcap/tidb/issues/51883) @[YangKeao](https://github.com/YangKeao)

+ TiKV

    - Avoid performing IO operations on snapshot files in Raftstore threads to improve TiKV stability [#16564](https://github.com/tikv/tikv/issues/16564) @[Connor1996](https://github.com/Connor1996)
    - Accelerate the shutdown speed of TiKV [#16680](https://github.com/tikv/tikv/issues/16680) @[LykxSassinator](https://github.com/LykxSassinator)
    - Add metrics for memory usage per thread [#15927](https://github.com/tikv/tikv/issues/15927) @[Connor1996](https://github.com/Connor1996)

+ PD

    - Optimize the logic for `OperatorController` to reduce the overhead of competition locks [#7897](https://github.com/tikv/pd/issues/7897) @[nolouch](https://github.com/nolouch)

+ TiFlash

    - Mitigate the issue that TiFlash might panic due to updating certificates after TLS is enabled [#8535](https://github.com/pingcap/tiflash/issues/8535) @[windtalker](https://github.com/windtalker)

+ Tools

    + Backup & Restore (BR)

        - Add PITR integration test cases to cover compatibility testing for log backup and adding index acceleration [#51987](https://github.com/pingcap/tidb/issues/51987) @[Leavrth](https://github.com/Leavrth)
        - Remove the invalid verification for active DDL jobs when log backup starts [#52733](https://github.com/pingcap/tidb/issues/52733) @[Leavrth](https://github.com/Leavrth)
        - Add test cases to test compatibility between PITR and the acceleration of adding indexes feature [#51988](https://github.com/pingcap/tidb/issues/51988) @[Leavrth](https://github.com/Leavrth)
        - BR cleans up empty SST files during data recovery [#16005](https://github.com/tikv/tikv/issues/16005) @[Leavrth](https://github.com/Leavrth)

    + TiCDC

        - Improve memory stability during data recovery using redo logs to reduce the probability of OOM [#10900](https://github.com/pingcap/tiflow/issues/10900) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Significantly improve the stability of data replication in transaction conflict scenarios, with up to 10 times performance improvement [#10896](https://github.com/pingcap/tiflow/issues/10896) @[CharlesCheung96](https://github.com/CharlesCheung96)
