# Bug fixes in TiDB 8.1.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.0.md`
- Source Title: `TiDB 8.1.0 Release Notes`
- Source Heading Path: `TiDB 8.1.0 Release Notes > Bug fixes`
- Source Line Ranges: `252-297`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`
- Topic Tags: `bug fixes`, `statistics`, `ddl`, `indexing`, `query execution`, `dashboard`, `tikv`, `pd`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0597_f703b40b4c`
- Source ID: `tidb-docs-8.1:releases/release-8.1.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c3b169ad8621b7794565435d9059caec8d79612287eec94ee66a392cd2b8b176`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.1.0 bug fixes related to statistics, DDL and index creation, query execution correctness, Dashboard metrics, TiKV, or PD release-note issues.
- Retrieval Keywords: TiDB 8.1.0 bug fixes, Can't find a proper physical plan for this query, multi-valued indexes, automatic statistics collection gets stuck after an OOM error occurs, BR restore table has no statistics statistics health 100%, TiDB creates statistics for system tables during upgrade, tidb_mem_quota_analyze, fail to get stats version for this histogram, INFORMATION_SCHEMA.TIKV_REGION_STATUS, adding indexes in the ingest mode might cause inconsistent data index, adding indexes fails when the TiDB network is isolated, Distributed eXecution Framework DXF adding indexes to large tables fails, adding indexes concurrently no such file or directory, IMPORT INTO operation gets stuck when importing a large amount of data, IndexHashJoin outputs redundant data, TopN operator in correlated subqueries incorrect result, TABLESAMPLE static partition pruning tidb_partition_prune_mode='static', TiDB Dashboard Monitoring Connection Count incorrect, EXPLAIN ANALYZE max_remote_stream incorrect, TIDB_HOT_REGIONS INFORMATION_SCHEMA, IFNULL function inconsistent with MySQL, resolve-ts is blocked when a stale Region peer ignores the GC message, inactive Write Ahead Logs WALs in RocksDB might corrupt data
- Follow-up Guidance: The chunk lists specific fixed issues for TiDB and TiKV in TiDB 8.1.0, with issue identifiers such as #49438, #51993, #52884, #52923, #16504, and #16705.
- Classification Note: This is a release-notes bug-fix section for TiDB 8.1.0 covering fixes across TiDB and TiKV, including statistics, DDL, indexing, query execution, monitoring, and storage-layer issues.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that executing SQL statements containing tables with multi-valued indexes might return the `Can't find a proper physical plan for this query` error [#49438](https://github.com/pingcap/tidb/issues/49438) @[qw4990](https://github.com/qw4990)
    - Fix the issue that automatic statistics collection gets stuck after an OOM error occurs [#51993](https://github.com/pingcap/tidb/issues/51993) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that after using BR to restore a table that has no statistics, the statistics health of that table is still 100% [#29769](https://github.com/pingcap/tidb/issues/29769) @[winoros](https://github.com/winoros)
    - Fix the issue that TiDB creates statistics for system tables during upgrade [#52040](https://github.com/pingcap/tidb/issues/52040) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that automatic statistics collection is triggered before the initialization of statistics finishes [#52346](https://github.com/pingcap/tidb/issues/52346) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that TiDB might crash when `tidb_mem_quota_analyze` is enabled and the memory used by updating statistics exceeds the limit [#52601](https://github.com/pingcap/tidb/issues/52601) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the TiDB synchronously loading statistics mechanism retries to load empty statistics indefinitely and prints the `fail to get stats version for this histogram` log [#52657](https://github.com/pingcap/tidb/issues/52657) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that expressions containing different collations might cause the query to panic when the new framework for collations is disabled [#52772](https://github.com/pingcap/tidb/issues/52772) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the `CPS by type` metric displays incorrect values [#52605](https://github.com/pingcap/tidb/issues/52605) @[nolouch](https://github.com/nolouch)
    - Fix the issue that the nil pointer error occurs when you query `INFORMATION_SCHEMA.TIKV_REGION_STATUS` [#52013](https://github.com/pingcap/tidb/issues/52013) @[JmPotato](https://github.com/JmPotato)
    - Fix the incorrect error message displayed when an invalid default value is specified for a column [#51592](https://github.com/pingcap/tidb/issues/51592) @[danqixu](https://github.com/danqixu)
    - Fix the issue that adding indexes in the ingest mode might cause inconsistent data index in some corner cases [#51954](https://github.com/pingcap/tidb/issues/51954) @[lance6716](https://github.com/lance6716)
    - Fix the issue that DDL operations get stuck when restoring a table with the foreign key [#51838](https://github.com/pingcap/tidb/issues/51838) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that adding indexes fails when the TiDB network is isolated [#51846](https://github.com/pingcap/tidb/issues/51846) @[ywqzzy](https://github.com/ywqzzy)
    - Fix the issue that adding an index with the same name after renaming an index causes an error [#51431](https://github.com/pingcap/tidb/issues/51431) @[lance6716](https://github.com/lance6716)
    - Fix the issue of inconsistent data indexes caused by cluster upgrade during adding indexes [#52411](https://github.com/pingcap/tidb/issues/52411) @[tangenta](https://github.com/tangenta)
    - Fix the issue that adding indexes to large tables fails after enabling the Distributed eXecution Framework (DXF) [#52640](https://github.com/pingcap/tidb/issues/52640) @[tangenta](https://github.com/tangenta)
    - Fix the issue that adding indexes concurrently reports the error `no such file or directory` [#52475](https://github.com/pingcap/tidb/issues/52475) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the temporary data cannot be cleaned up after adding indexes fails [#52639](https://github.com/pingcap/tidb/issues/52639) @[lance6716](https://github.com/lance6716)
    - Fix the issue that the metadata lock fails to prevent DDL operations from executing in the plan cache scenario [#51407](https://github.com/pingcap/tidb/issues/51407) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the `IMPORT INTO` operation gets stuck when importing a large amount of data [#52884](https://github.com/pingcap/tidb/issues/52884) @[lance6716](https://github.com/lance6716)
    - Fix the issue that TiDB unexpectedly restarts when logging gRPC errors [#51301](https://github.com/pingcap/tidb/issues/51301) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that IndexHashJoin outputs redundant data when calculating Anti Left Outer Semi Join [#52923](https://github.com/pingcap/tidb/issues/52923) @[yibin87](https://github.com/yibin87)
    - Fix the incorrect result of the TopN operator in correlated subqueries [#52777](https://github.com/pingcap/tidb/issues/52777) @[yibin87](https://github.com/yibin87)
    - Fix the inaccurate execution time statistics of HashJoin probe [#52222](https://github.com/pingcap/tidb/issues/52222) @[windtalker](https://github.com/windtalker)
    - Fix the issue that using `TABLESAMPLE` returns incorrect results in static partition pruning mode (`tidb_partition_prune_mode='static'`) [#52282](https://github.com/pingcap/tidb/issues/52282) @[tangenta](https://github.com/tangenta)
    - Fix the issue that TTL is deviated by 1 hour in daylight saving time [#51675](https://github.com/pingcap/tidb/issues/51675) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the incorrect calculation and display of the number of connections (Connection Count) on the TiDB Dashboard Monitoring page [#51889](https://github.com/pingcap/tidb/issues/51889) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the status gets stuck when rolling back the partition DDL tasks [#51090](https://github.com/pingcap/tidb/issues/51090) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that the value of `max_remote_stream` is incorrect when executing `EXPLAIN ANALYZE` [#52646](https://github.com/pingcap/tidb/issues/52646) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that querying the `TIDB_HOT_REGIONS` table might incorrectly return `INFORMATION_SCHEMA` tables [#50810](https://github.com/pingcap/tidb/issues/50810) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the `EXPLAIN` statement might display incorrect column IDs in the result when statistics for certain columns are not fully loaded [#52207](https://github.com/pingcap/tidb/issues/52207) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that the type returned by the `IFNULL` function is inconsistent with MySQL [#51765](https://github.com/pingcap/tidb/issues/51765) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that adding a unique index might cause TiDB to panic [#52312](https://github.com/pingcap/tidb/issues/52312) @[wjhuang2016](https://github.com/wjhuang2016)

+ TiKV

    - Fix the issue that resolve-ts is blocked when a stale Region peer ignores the GC message [#16504](https://github.com/tikv/tikv/issues/16504) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that inactive Write Ahead Logs (WALs) in RocksDB might corrupt data [#16705](https://github.com/tikv/tikv/issues/16705) @[Connor1996](https://github.com/Connor1996)

+ PD
