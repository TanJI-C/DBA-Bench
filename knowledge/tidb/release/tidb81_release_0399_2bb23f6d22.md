# TiDB 6.5.4 bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.4.md`
- Source Title: `TiDB 6.5.4 Release Notes`
- Source Heading Path: `TiDB 6.5.4 Release Notes > Bug fixes`
- Source Line Ranges: `74-111`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `br`, `pd`, `tikv`, `tiflash`
- Topic Tags: `bug-fixes`, `query-execution`, `partitioning`, `stale-read`, `prepared-statements`, `statistics`, `gc`, `memory-usage`, `ddl`, `mpp`, `permissions`, `region-metadata`, `restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0399_2bb23f6d22`
- Source ID: `tidb-docs-8.1:releases/release-6.5.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `feade1f0717ddd55b064d29d0b4d446f2a494d45c6caa767c862e3490a665dfe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.4.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.5.4 bug fix information for query execution, partitioning, stale reads, prepared statements, statistics, GC, DDL, MPP, permissions, region metadata, or BR restore issues.
- Retrieval Keywords: TiDB 6.5.4 bug fixes, index out of range STREAM_AGG(), CREATE TABLE sub-partition definitions non-partitioned table, stale_read_ts PREPARE stmt, ActivateTxn data race, batch client does not reconnect timely, SQL compile error logs are not redacted, CTEs correlated subqueries incorrect query results panic, TTL tasks statistics updates, GC Resolve Locks pessimistic locks, binary protocol PREPARE EXECUTE memory leaks, INFORMATION_SCHEMA.DDL_JOBS QUERY column, PD OOM large number of Regions Prepare Execute virtual tables, statistics auto-collection partitioned table new index, statistics SQL execution details excessive memory consumption, batch coprocessor retry incorrect Region information, indexMerge killed hang-up, INFORMATION_SCHEMA.TIKV_REGION_STATUS incorrect results, MPP mode tidb_enable_parallel_apply incorrect results, tidb_opt_agg_push_down incorrect results, virtual columns proper physical plan, empty processInfo panic, SELECT CAST(n AS CHAR) negative number, MySQL Cursor Fetch protocol tidb_mem_quota_query, BR restore AUTO_ID_CACHE=1 duplicate entry, partitioned table FLOOR() function SELECT returns an error, concurrent view DDL operations blocked, statistics collection task incorrect datetime value, DDL statements stuck after PD node replaced, resolve lock hang sudden change in PD time, index scan data race, FormatSQL() extremely long SQL statements, INFORMATION_SCHEMA.TIFLASH_REPLICA without permissions, DATETIME TIMESTAMP column compared with a number constant, Index Join query stuck
- Follow-up Guidance: The source enumerates individual TiDB 6.5.4 fixes across TiDB, including exact SQL statements, system tables, variables, and error phrases for targeted lookup.
- Classification Note: This chunk is classified as a release note because it is the Bug fixes section of the TiDB 6.5.4 Release Notes and lists resolved issues in TiDB and related components.

## Official Source Content

## Bug fixes

+ TiDB 

    - Fix the issue that the `index out of range` error might be reported when pushing down the `STREAM_AGG()` operator [#40857](https://github.com/pingcap/tidb/issues/40857) @[Dousir9](https://github.com/Dousir9)
    - Fix the issue that TiDB ignores all partition information and creates a non-partitioned table when the `CREATE TABLE` statement contains sub-partition definitions [#41198](https://github.com/pingcap/tidb/issues/41198) [#41200](https://github.com/pingcap/tidb/issues/41200) @[mjonss](https://github.com/mjonss)
    - Fix the issue that incorrect `stale_read_ts` setting might cause `PREPARE stmt` to read data incorrectly [#43044](https://github.com/pingcap/tidb/issues/43044) @[you06](https://github.com/you06) 
    - Fix the issue of possible data race in ActivateTxn [#42092](https://github.com/pingcap/tidb/issues/42092) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that a batch client does not reconnect timely [#44431](https://github.com/pingcap/tidb/issues/44431) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that SQL compile error logs are not redacted [#41831](https://github.com/pingcap/tidb/issues/41831) @[lance6716](https://github.com/lance6716)
    - Fix the issue that using CTEs and correlated subqueries simultaneously might result in incorrect query results or panic [#44649](https://github.com/pingcap/tidb/issues/44649) [#38170](https://github.com/pingcap/tidb/issues/38170) [#44774](https://github.com/pingcap/tidb/issues/44774) @[winoros](https://github.com/winoros) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that TTL tasks cannot trigger statistics updates in time [#40109](https://github.com/pingcap/tidb/issues/40109) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the GC Resolve Locks step might miss some pessimistic locks [#45134](https://github.com/pingcap/tidb/issues/45134) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that memory leaks and duration continues to increase when connecting to TiDB using the binary protocol and executing a large number of `PREPARE` and `EXECUTE` statements [#44612](https://github.com/pingcap/tidb/issues/44612) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the data length in the `QUERY` column of the `INFORMATION_SCHEMA.DDL_JOBS` table might exceed the column definition [#42440](https://github.com/pingcap/tidb/issues/42440) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the PD OOM issue when there is a large number of Regions but the table ID cannot be pushed down when querying some virtual tables using `Prepare` or `Execute` [#39605](https://github.com/pingcap/tidb/issues/39605) @[djshow832](https://github.com/djshow832)
    - Fix the issue that statistics auto-collection might not trigger correctly on a partitioned table after adding a new index to the partitioned table [#41638](https://github.com/pingcap/tidb/issues/41638) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the issue that excessive memory consumption of SQL execution details in statistics causes TiDB OOM in extreme cases [#44047](https://github.com/pingcap/tidb/issues/44047) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that batch coprocessor retry might generate incorrect Region information that causes query failure [#44622](https://github.com/pingcap/tidb/issues/44622) @[windtalker](https://github.com/windtalker)
    - Fix the hang-up issue that occurs when queries with `indexMerge` are killed [#45279](https://github.com/pingcap/tidb/issues/45279) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that querying the system table `INFORMATION_SCHEMA.TIKV_REGION_STATUS` returns incorrect results in some cases [#45531](https://github.com/pingcap/tidb/issues/45531) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that query results in MPP mode are incorrect when `tidb_enable_parallel_apply` is enabled [#45299](https://github.com/pingcap/tidb/issues/45299) @[windtalker](https://github.com/windtalker)
    - Fix the issue that queries might return incorrect results when `tidb_opt_agg_push_down` is enabled [#44795](https://github.com/pingcap/tidb/issues/44795) @[AilinKid](https://github.com/AilinKid)
    - Fix the can't find proper physical plan issue caused by virtual columns [#41014](https://github.com/pingcap/tidb/issues/41014) @[AilinKid](https://github.com/AilinKid)
    - Fix the panic issue caused by empty `processInfo` [#43829](https://github.com/pingcap/tidb/issues/43829) @[zimulala](https://github.com/zimulala)
    - Fix the issue that the query result of the `SELECT CAST(n AS CHAR)` statement is incorrect when `n` in the statement is a negative number [#44786](https://github.com/pingcap/tidb/issues/44786) @[xhebox](https://github.com/xhebox)
    - Fix the issue that when the MySQL Cursor Fetch protocol is used, the memory consumption of result sets might exceed the `tidb_mem_quota_query` limit and causes TiDB OOM. After the fix, TiDB will automatically write result sets to the disk to release memory [#43233](https://github.com/pingcap/tidb/issues/43233) @[YangKeao](https://github.com/YangKeao)
    - Fix the `duplicate entry` error that occurs when restoring a table with `AUTO_ID_CACHE=1` using BR [#44716](https://github.com/pingcap/tidb/issues/44716) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the `SELECT` statement returns an error for a partitioned table if the table partition definition uses the `FLOOR()` function to round a partitioned column [#42323](https://github.com/pingcap/tidb/issues/42323) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that concurrent view might cause DDL operations to be blocked [#40352](https://github.com/pingcap/tidb/issues/40352) @[zeminzhou](https://github.com/zeminzhou)
    - Fix the issue that a statistics collection task fails due to an incorrect `datetime` value [#39336](https://github.com/pingcap/tidb/issues/39336) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the issue that some DDL statements might be stuck for a period after the PD node of a cluster is replaced [#33908](https://github.com/pingcap/tidb/issues/33908)
    - Fix the issue that `resolve lock` might hang when there is a sudden change in PD time [#44822](https://github.com/pingcap/tidb/issues/44822) @[zyguan](https://github.com/zyguan)
    - Fix the potential data race issue in index scan [#45126](https://github.com/pingcap/tidb/issues/45126) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the `FormatSQL()` method cannot properly truncate extremely long SQL statements in input [#44542](https://github.com/pingcap/tidb/issues/44542) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that users can view information in the `INFORMATION_SCHEMA.TIFLASH_REPLICA` table even without permissions [#45320](https://github.com/pingcap/tidb/issues/45320) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that the behavior is inconsistent with MySQL when comparing a `DATETIME` or `TIMESTAMP` column with a number constant [#38361](https://github.com/pingcap/tidb/issues/38361) @[yibin87](https://github.com/yibin87)
    - Fix the issue that an error in Index Join might cause the query to get stuck [#45716](https://github.com/pingcap/tidb/issues/45716) @[wshwsh12](https://github.com/wshwsh12)
