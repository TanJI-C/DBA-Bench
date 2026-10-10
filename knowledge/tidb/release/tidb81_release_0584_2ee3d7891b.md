# 8.0.0 improvements for TiDB and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Improvements`
- Source Line Ranges: `367-403`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `release-notes`, `improvements`, `ddl`, `import-into`, `spill-to-disk`, `index-join`, `index-merge`, `show-warnings`, `plan-cache`, `statistics`, `memory-tracker`, `system-tables`, `tso`, `pessimistic-locks`, `health-control`, `pd-client`, `raft`, `monitoring`, `slow-logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0584_2ee3d7891b`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0c8047dd1457184f054d37eb1c7dd9193cf3b7175bc7738a35b9c5e81388361f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 8.0.0 release-note improvements for TiDB, TiKV, or PD-related performance, observability, DDL, import, statistics, memory tracking, health control, TSO, Raft, or slow log changes.
- Retrieval Keywords: TiDB 8.0.0 Improvements, CREATE TABLE DDL performance 10 times linear scalability, IMPORT INTO ... FROM FILE 16 tasks simultaneously, spilling data to disk Sort operator, canceling queries during spilling data to disk, Index Join partial conditions multiple equal conditions, Index Merge sorting requirements, SHOW WARNINGS Apply operator blocks the concurrency, point get most optimal index, statistics synchronously loading high priority widespread timeouts, PREPARE statement execution plan cache SHOW WARNINGS, force-init-stats true HTTP servers monitoring, MemoryTracker IndexLookup, MemoryTracker MemTableReaderExec, loading Regions in batch from PD, INFORMATION_SCHEMA.TABLES INFORMATION_SCHEMA.STATISTICS INFORMATION_SCHEMA.KEY_COLUMN_USAGE INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS, TSO verification and detection, cleaning up pessimistic locks uncommitted transactions, tikv-client.enable-replica-selector-v2, PD client metadata storage interface, write cf stats scanning performance, Raft conf change latest heartbeat Region inaccessible, Pipelined DML Flush BufferBatchGet, cgroup CPU and memory limits monitoring and alerting, Region workers snapshot generation workers CPU monitoring, slow logs for peer and store messages
- Follow-up Guidance: The chunk also notes that unified health control for TiKV can be disabled by setting `tikv-client.enable-replica-selector-v2` to `false`.
- Classification Note: This is a self-managed release-notes improvements chunk covering shared TiDB and TiKV enhancements and exact feature identifiers introduced in the TiDB 8.0.0 release notes.

## Official Source Content

## Improvements

+ TiDB

    - Improve the performance of executing the `CREATE TABLE` DDL statement by 10 times and support linear scalability [#50052](https://github.com/pingcap/tidb/issues/50052) @[GMHDBJD](https://github.com/GMHDBJD)
    - Support submitting 16 `IMPORT INTO ... FROM FILE` tasks simultaneously, facilitating bulk data import into target tables and significantly improving the efficiency and performance of importing data files [#49008](https://github.com/pingcap/tidb/issues/49008) @[D3Hunter](https://github.com/D3Hunter)
    - Improve the performance of spilling data to disk for the `Sort` operator [#47733](https://github.com/pingcap/tidb/issues/47733) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Support canceling queries during spilling data to disk, which optimizes the exit mechanism of the data spill feature [#50511](https://github.com/pingcap/tidb/issues/50511) @[wshwsh12](https://github.com/wshwsh12)
    - Support using an index that matches partial conditions to construct Index Join when processing table join queries with multiple equal conditions [#47233](https://github.com/pingcap/tidb/issues/47233) @[winoros](https://github.com/winoros)
    - Enhance the capability of Index Merge to identify sorting requirements in queries and select indexes that meet the sorting requirements [#48359](https://github.com/pingcap/tidb/issues/48359) @[AilinKid](https://github.com/AilinKid)
    - When the `Apply` operator is not executed concurrently, TiDB enables you to view the name of the operator that blocks the concurrency by executing `SHOW WARNINGS` [#50256](https://github.com/pingcap/tidb/issues/50256) @[hawkingrei](https://github.com/hawkingrei)
    - Optimize the index selection for `point get` queries by selecting the most optimal index for queries when all indexes support `point get` queries [#50184](https://github.com/pingcap/tidb/issues/50184) @[elsa0520](https://github.com/elsa0520)
    - Temporarily adjust the priority of statistics synchronously loading tasks to high to avoid widespread timeouts during TiKV high loads, as these timeouts might result in statistics not being loaded [#50332](https://github.com/pingcap/tidb/issues/50332) @[winoros](https://github.com/winoros)
    - When the `PREPARE` statement fails to hit the execution plan cache, TiDB enables you to view the reason by executing `SHOW WARNINGS` [#50407](https://github.com/pingcap/tidb/issues/50407) @[hawkingrei](https://github.com/hawkingrei)
    - Improve the accuracy of query estimation information when the same row of data is updated multiple times [#47523](https://github.com/pingcap/tidb/issues/47523) @[terry1purcell](https://github.com/terry1purcell)
    - Index Merge supports embedding multi-value indexes and `OR` operators in `AND` predicates [#51778](https://github.com/pingcap/tidb/issues/51778) @[time-and-fate](https://github.com/time-and-fate)
    - When `force-init-stats` is set to `true`, TiDB waits for statistics initialization to finish before providing services during TiDB startup. This setting no longer blocks the startup of HTTP servers, which enables users to continue monitoring [#50854](https://github.com/pingcap/tidb/issues/50854) @[hawkingrei](https://github.com/hawkingrei)
    - MemoryTracker can track the memory usage of the `IndexLookup` operator [#45901](https://github.com/pingcap/tidb/issues/45901) @[solotzg](https://github.com/solotzg)
    - MemoryTracker can track the memory usage of the `MemTableReaderExec` operator [#51456](https://github.com/pingcap/tidb/issues/51456) @[wshwsh12](https://github.com/wshwsh12)
    - Support loading Regions in batch from PD to speed up the conversion process from the KV range to Regions when querying large tables [#51326](https://github.com/pingcap/tidb/issues/51326) @[SeaRise](https://github.com/SeaRise)
    - Optimize the query performance of the system tables `INFORMATION_SCHEMA.TABLES`, `INFORMATION_SCHEMA.STATISTICS`, `INFORMATION_SCHEMA.KEY_COLUMN_USAGE`, and `INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS`. Compared with earlier versions, the performance has been improved by up to 100 times. [#50305](https://github.com/pingcap/tidb/issues/50305) @[ywqzzy](https://github.com/ywqzzy)

+ TiKV

    - Enhance TSO verification and detection to improve the robustness of the cluster TSO when the configuration or operation is improper [#16545](https://github.com/tikv/tikv/issues/16545) @[cfzjywxk](https://github.com/cfzjywxk)
    - Optimize the logic of cleaning up pessimistic locks to improve the processing performance of uncommitted transactions [#16158](https://github.com/tikv/tikv/issues/16158) @[cfzjywxk](https://github.com/cfzjywxk)
    - Introduce unified health control for TiKV to reduce the impact of abnormal single TiKV node on cluster access performance. You can disable this optimization by setting [`tikv-client.enable-replica-selector-v2`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-replica-selector-v2-new-in-v800) to `false`. [#16297](https://github.com/tikv/tikv/issues/16297) [#1104](https://github.com/tikv/client-go/issues/1104) [#1167](https://github.com/tikv/client-go/issues/1167) @[MyonKeminta](https://github.com/MyonKeminta) @[zyguan](https://github.com/zyguan) @[crazycs520](https://github.com/crazycs520)
    - The PD client uses the metadata storage interface to replace the previous global configuration interface [#14484](https://github.com/tikv/tikv/issues/14484) @[HuSharp](https://github.com/HuSharp)
    - Enhance the scanning performance by determining the data loading behavior through write cf stats [#16245](https://github.com/tikv/tikv/issues/16245) @[Connor1996](https://github.com/Connor1996)
    - Check the latest heartbeat for nodes being deleted and voters being demoted during the Raft conf change process to ensure that this behavior does not make the Region inaccessible [#15799](https://github.com/tikv/tikv/issues/15799) @[tonyxuqqi](https://github.com/tonyxuqqi)
    - Add Flush and BufferBatchGet interfaces for Pipelined DML [#16291](https://github.com/tikv/tikv/issues/16291) @[ekexium](https://github.com/ekexium)
    - Add monitoring and alerting for cgroup CPU and memory limits [#16392](https://github.com/tikv/tikv/issues/16392) @[pingandb](https://github.com/pingandb)
    - Add CPU monitoring for Region workers and snapshot generation workers [#16562](https://github.com/tikv/tikv/issues/16562) @[Connor1996](https://github.com/Connor1996)
    - Add slow logs for peer and store messages [#16600](https://github.com/tikv/tikv/issues/16600) @[Connor1996](https://github.com/Connor1996)

+ PD
