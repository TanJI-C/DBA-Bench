# TiDB 6.1.7 release notes improvements and bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.7.md`
- Source Title: `TiDB 6.1.7 Release Notes`
- Source Heading Path: `TiDB 6.1.7 Release Notes | TiDB 6.1.7 Release Notes > Improvements | TiDB 6.1.7 Release Notes > Bug fixes`
- Source Line Ranges: `5-67`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `ticdc`, `lightning`, `pd`, `tiflash`
- Topic Tags: `release-notes`, `improvements`, `bug-fixes`, `transactions`, `replication`, `import`, `cte`, `partitioned-tables`, `memory-usage`, `placement-rules`, `region-split`, `gc`, `ddl`, `statistics`, `query-correctness`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0320_2c9dbf1825`
- Source ID: `tidb-docs-8.1:releases/release-6.1.7.md#tidb-6-1-7-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `94208c64105de0719be4ad020d3ead8f0dfbd0e59be6f8a1e7064b52e92377ec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.7#tidb-6-1-7-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.7.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 6.1.7 release notes for improvements and bug fixes across TiDB, TiCDC, TiDB Lightning, PD-related lock timing behavior, partitioned tables, CTEs, memory usage, GC, DDL, and TiFlash.
- Retrieval Keywords: TiDB 6.1.7 Release Notes, 6.1.7 improvements, 6.1.7 bug fixes, pessimistic transactions internal transaction retry, TiCDC batch UPDATE DML statements, TiDB Lightning verify checksum through SQL after the import, resolve lock might hang when there is a sudden change in PD time, Common Table Expressions CTE insufficient disk space, CTEs and correlated subqueries incorrect query results or panic, SELECT CAST(n AS CHAR) negative number incorrect, partitioned tables Region split errors, tidb_opt_agg_push_down incorrect results, residual pessimistic locks affect data correctness when GC resolves locks, TiCDC lose some row changes during table renaming, tidb_scatter_region Region does not automatically split after a partition is truncated, TRUNCATE TABLE partitioned tables many partitions TiFlash replicas write conflict, window functions to TiFlash incorrect execution plans, memTracker with cursor fetch memory leaks, INFORMATION_SCHEMA.DDL_JOBS QUERY column exceed column definition, SHOW PROCESSLIST TxnStart long subquery time, ADMIN SHOW DDL JOBS missing table names DROP TABLE, AES_DECRYPT runtime error index out of range, query with CTE causes TiDB to hang
- Follow-up Guidance: The source groups the changes into Improvements for TiDB, TiCDC, and TiDB Lightning, and Bug fixes primarily for TiDB including one TiCDC-related fix.
- Classification Note: This chunk is classified as a self-managed release-notes summary because the official content is the TiDB 6.1.7 release notes listing product improvements and bug fixes for multiple components.

## Official Source Content

# TiDB 6.1.7 Release Notes

Release date: July 12, 2023

TiDB version: 6.1.7

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.1/production-deployment-using-tiup)
## Improvements

+ TiDB

    - Use pessimistic transactions in internal transaction retry to avoid retry failure and reduce time consumption [#38136](https://github.com/pingcap/tidb/issues/38136) @[jackysp](https://github.com/jackysp)

+ Tools

    + TiCDC

        - Support batch `UPDATE` DML statements to improve TiCDC replication performance [#8084](https://github.com/pingcap/tiflow/issues/8084) @[amyangfei](https://github.com/amyangfei)

    + TiDB Lightning

        - Verify checksum through SQL after the import to improve stability of verification [#41941](https://github.com/pingcap/tidb/issues/41941) @[GMHDBJD](https://github.com/GMHDBJD)
## Bug fixes

+ TiDB

    - Fix the panic issue caused by empty `processInfo` [#43829](https://github.com/pingcap/tidb/issues/43829) @[zimulala](https://github.com/zimulala)
    - Fix the issue that `resolve lock` might hang when there is a sudden change in PD time [#44822](https://github.com/pingcap/tidb/issues/44822) @[zyguan](https://github.com/zyguan)
    - Fix the issue that queries containing Common Table Expressions (CTEs) might cause insufficient disk space [#44477](https://github.com/pingcap/tidb/issues/44477) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that using CTEs and correlated subqueries simultaneously might result in incorrect query results or panic [#44649](https://github.com/pingcap/tidb/issues/44649) [#38170](https://github.com/pingcap/tidb/issues/38170) [#44774](https://github.com/pingcap/tidb/issues/44774) @[winoros](https://github.com/winoros) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the query result of the `SELECT CAST(n AS CHAR)` statement is incorrect when `n` in the statement is a negative number [#44786](https://github.com/pingcap/tidb/issues/44786) @[xhebox](https://github.com/xhebox)
    - Fix the query panic issue of TiDB in certain cases [#40857](https://github.com/pingcap/tidb/issues/40857) @[Dousir9](https://github.com/Dousir9)
    - Fix the issue that SQL compile error logs are not redacted [#41831](https://github.com/pingcap/tidb/issues/41831) @[lance6716](https://github.com/lance6716)
    - Fix the issue that the `SELECT` statement returns an error for a partitioned table if the table partition definition uses the `FLOOR()` function to round a partitioned column [#42323](https://github.com/pingcap/tidb/issues/42323) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that querying partitioned tables might cause errors during Region split [#43144](https://github.com/pingcap/tidb/issues/43144) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue of unnecessary memory usage during reading statistical information [#42052](https://github.com/pingcap/tidb/issues/42052) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the issue of excessive memory usage after creating a large number of empty partitioned tables [#44308](https://github.com/pingcap/tidb/issues/44308) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that queries might return incorrect results when `tidb_opt_agg_push_down` is enabled [#44795](https://github.com/pingcap/tidb/issues/44795) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that the join result of common table expressions might be wrong [#38170](https://github.com/pingcap/tidb/issues/38170) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that in some rare cases, residual pessimistic locks of pessimistic transactions might affect data correctness when GC resolves locks [#43243](https://github.com/pingcap/tidb/issues/43243) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that after a new column is added in the cache table, the value is `NULL` instead of the default value of the column [#42928](https://github.com/pingcap/tidb/issues/42928) @[lqs](https://github.com/lqs)
    - Fix the issue that TiDB returns an error when the corresponding rows in partitioned tables cannot be found in the probe phase of index join [#43686](https://github.com/pingcap/tidb/issues/43686) @[AilinKid](https://github.com/AilinKid) @[mjonss](https://github.com/mjonss)
    - Fix the issue that dropping a database causes slow GC progress [#33069](https://github.com/pingcap/tidb/issues/33069) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that data and indexes are inconsistent when the `ON UPDATE` statement does not correctly update the primary key [#44565](https://github.com/pingcap/tidb/issues/44565) @[zyguan](https://github.com/zyguan)
    - Fix the issue that TiCDC might lose some row changes during table renaming [#43338](https://github.com/pingcap/tidb/issues/43338) @[tangenta](https://github.com/tangenta)
    - Fix the behavior issue of Placement Rules in partitioned tables, so that the Placement Rules in deleted partitions can be correctly set and recycled [#44116](https://github.com/pingcap/tidb/issues/44116) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that when `tidb_scatter_region` is enabled, Region does not automatically split after a partition is truncated [#43174](https://github.com/pingcap/tidb/issues/43174) [#43028](https://github.com/pingcap/tidb/issues/43028)
    - Fix the issue of DDL retry caused by write conflict when executing `TRUNCATE TABLE` for partitioned tables with many partitions and TiFlash replicas [#42940](https://github.com/pingcap/tidb/issues/42940) @[mjonss](https://github.com/mjonss)
    - Fix the issue of incorrect execution plans when pushing down window functions to TiFlash [#43922](https://github.com/pingcap/tidb/issues/43922) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that incorrect results might be returned when using a common table expression (CTE) in statements with non-correlated subqueries [#44051](https://github.com/pingcap/tidb/issues/44051) @[winoros](https://github.com/winoros)
    - Fix the issue that using `memTracker` with cursor fetch causes memory leaks [#44254](https://github.com/pingcap/tidb/issues/44254) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the data length in the `QUERY` column of the `INFORMATION_SCHEMA.DDL_JOBS` table might exceed the column definition [#42440](https://github.com/pingcap/tidb/issues/42440) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the `min, max` query result is incorrect [#43805](https://github.com/pingcap/tidb/issues/43805) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that TiDB reports syntax errors when analyzing tables [#43392](https://github.com/pingcap/tidb/issues/43392) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the `SHOW PROCESSLIST` statement cannot display the TxnStart of the transaction of the statement with a long subquery time [#40851](https://github.com/pingcap/tidb/issues/40851) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue of missing table names in the `ADMIN SHOW DDL JOBS` result when a `DROP TABLE` operation is being executed [#42268](https://github.com/pingcap/tidb/issues/42268) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue of displaying the incorrect TiDB address in IPv6 environment [#43260](https://github.com/pingcap/tidb/issues/43260) @[nexustar](https://github.com/nexustar)
    - Fix the issue that the SQL statement reports the `runtime error: index out of range` error when using the `AES_DECRYPT` expression [#43063](https://github.com/pingcap/tidb/issues/43063) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that there is no warning when using `SUBPARTITION` to create partitioned tables [#41198](https://github.com/pingcap/tidb/issues/41198) [#41200](https://github.com/pingcap/tidb/issues/41200) @[mjonss](https://github.com/mjonss)
    - Fix the issue that the query with CTE causes TiDB to hang [#43749](https://github.com/pingcap/tidb/issues/43749) [#36896](https://github.com/pingcap/tidb/issues/36896) @[guo-shaoge](https://github.com/guo-shaoge)
