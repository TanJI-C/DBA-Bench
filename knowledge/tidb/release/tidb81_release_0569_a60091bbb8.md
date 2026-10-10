# TiDB bug fixes in 7.6.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.6.0.md`
- Source Title: `TiDB 7.6.0 Release Notes`
- Source Heading Path: `TiDB 7.6.0 Release Notes > Bug fixes`
- Source Line Ranges: `418-449`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `br`, `sql`, `tiflash`
- Topic Tags: `bug-fixes`, `ddl`, `statistics`, `optimizer`, `sql-compatibility`, `indexes`, `partitioned-tables`, `mpp`, `memory`, `foreign-keys`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0569_a60091bbb8`
- Source ID: `tidb-docs-8.1:releases/release-7.6.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e062c2114fa7f1ce8d2ec883091ccd0a502e724610f3d94429a2a89a2006f807`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.6.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.6.0 bug fixes related to DDL, statistics, optimizer behavior, SQL compatibility, indexes, partitioned tables, memory, BR import, MPP, or foreign keys.
- Retrieval Keywords: TiDB 7.6.0 bug fixes, ILIKE data race, #49677, STREAM_AGG() incorrectly handling CI, #49902, converting bytes to TIME encoding fails, #47346, CHECK constraint ENFORCED MySQL 8.0, #47567, #47631, DDL statements with the CHECK constraint are stuck, #47632, adding index fails out of memory, #47862, upgrade during ADD INDEX inconsistent indexes, #46306, ADMIN CHECK tidb_mem_quota_query ERROR 8175, #49258, ALTER TABLE foreign key DECIMAL precision error, #49836, ALTER TABLE foreign key INTEGER length reported as error by mistake, #47702, expression index divisor is 0, #50053, TiDB nodes OOM large number of tables, #50077, DDL stuck running state cluster rolling restart, #50073, global indexes partitioned tables PointGet BatchPointGet incorrect results, #47539, MPP plans generated columns visible indexes, #47766, LIMIT pushdown OR type Index Merge, #48588, mysql.bind_info duplicate built-in rows after BR import, #46527, statistics partitioned tables dropped partitions, #48182, concurrent merging of global statistics partitioned tables, #48713, LIKE index range scans PADDING SPACE incorrect results, #48821, generated columns data race, #44919, ANALYZE TABLE WITH 0 TOPN Top1 statistics, #49080, illegal optimizer hints valid hints ineffective, #49308, Hash partitioned tables statistics add drop reorganize TRUNCATE partitions, #48235, #48233, #48226, #48231, automatic statistics updates outside time window, #49552, partitioned table converted to non-partitioned old statistics not deleted, #49547, TRUNCATE TABLE old statistics not deleted, #49663, enforced sorting optimizer hints STREAM_AGG() IndexMerge, #49605, histogram boundary contains NULL readable strings, #49823, GROUP_CONCAT(ORDER BY) return errors, #49986, UPDATE DELETE INSERT overflow errors instead of warnings SQL_MODE not strict, #49137, composite index multi-valued indexes non-binary type strings insert fails, #49680
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a TiDB release-note bug-fix summary because it lists multiple issues fixed in TiDB 7.6.0 across TiDB-related components and SQL features.

## Official Source Content

- Fix the issue that the `ILIKE` function might cause data race in some scenarios [#49677](https://github.com/pingcap/tidb/issues/49677) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that query results are incorrect due to `STREAM_AGG()` incorrectly handling CI [#49902](https://github.com/pingcap/tidb/issues/49902) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that encoding fails when converting bytes to `TIME` [#47346](https://github.com/pingcap/tidb/issues/47346) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the behavior of the `ENFORCED` option in the `CHECK` constraint is inconsistent with MySQL 8.0 [#47567](https://github.com/pingcap/tidb/issues/47567) [#47631](https://github.com/pingcap/tidb/issues/47631) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that DDL statements with the `CHECK` constraint are stuck [#47632](https://github.com/pingcap/tidb/issues/47632) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that adding index fails for DDL statements due to out of memory [#47862](https://github.com/pingcap/tidb/issues/47862) @[GMHDBJD](https://github.com/GMHDBJD)
    - Fix the issue that upgrading the cluster during executing `ADD INDEX` might cause the data to be inconsistent with the indexes [#46306](https://github.com/pingcap/tidb/issues/46306) @[zimulala](https://github.com/zimulala)
    - Fix the issue that executing `ADMIN CHECK` after updating the `tidb_mem_quota_query` system variable returns `ERROR 8175` [#49258](https://github.com/pingcap/tidb/issues/49258) @[tangenta](https://github.com/tangenta)
    - Fix the issue that when `ALTER TABLE` modifies the type of a column referenced by a foreign key, the change in `DECIMAL` precision is not reported as an error [#49836](https://github.com/pingcap/tidb/issues/49836) @[yoshikipom](https://github.com/yoshikipom)
    - Fix the issue that when `ALTER TABLE` modifies the type of a column referenced by a foreign key, the change in `INTEGER` length is reported as an error by mistake [#47702](https://github.com/pingcap/tidb/issues/47702) @[yoshikipom](https://github.com/yoshikipom)
    - Fix the issue that in some scenarios the expression index does not detect that the divisor is 0 [#50053](https://github.com/pingcap/tidb/issues/50053) @[lcwangchao](https://github.com/lcwangchao)
    - Mitigate the issue that TiDB nodes might encounter OOM errors when dealing with a large number of tables [#50077](https://github.com/pingcap/tidb/issues/50077) @[zimulala](https://github.com/zimulala)
    - Fix the issue that DDL gets stuck in the running state during cluster rolling restart [#50073](https://github.com/pingcap/tidb/issues/50073) @[tangenta](https://github.com/tangenta)
    - Fix the issue that results might be incorrect when accessing global indexes of partitioned tables using `PointGet` or `BatchPointGet` operators [#47539](https://github.com/pingcap/tidb/issues/47539) @[L-maple](https://github.com/L-maple)
    - Fix the issue that MPP plans might not be selected when indexes on generated columns are set as visible [#47766](https://github.com/pingcap/tidb/issues/47766) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that `LIMIT` might not be pushed down to the `OR` type `Index Merge` [#48588](https://github.com/pingcap/tidb/issues/48588) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that duplicate built-in rows might exist in the `mysql.bind_info` table after BR import [#46527](https://github.com/pingcap/tidb/issues/46527) @[qw4990](https://github.com/qw4990)
    - Fix the issue that statistics for partitioned tables are not updated as expected after partitions are dropped [#48182](https://github.com/pingcap/tidb/issues/48182) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that errors might be returned during the concurrent merging of global statistics for partitioned tables [#48713](https://github.com/pingcap/tidb/issues/48713) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that query results might be incorrect when the `LIKE` operator is used for index range scans on a column with PADDING SPACE [#48821](https://github.com/pingcap/tidb/issues/48821) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that generated columns might trigger concurrent read and write on memory and result in data race [#44919](https://github.com/pingcap/tidb/issues/44919) @[tangenta](https://github.com/tangenta)
    - Fix the issue that `ANALYZE TABLE` might still collect Top1 statistics even when `WITH 0 TOPN` (indicating not collecting topN statistics) is specified [#49080](https://github.com/pingcap/tidb/issues/49080) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that illegal optimizer hints might cause valid hints to be ineffective [#49308](https://github.com/pingcap/tidb/issues/49308) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that statistics for Hash partitioned tables are not correspondingly updated when you add, drop, reorganize, or `TRUNCATE` partitions [#48235](https://github.com/pingcap/tidb/issues/48235) [#48233](https://github.com/pingcap/tidb/issues/48233) [#48226](https://github.com/pingcap/tidb/issues/48226) [#48231](https://github.com/pingcap/tidb/issues/48231) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that after the time window for automatic statistics updates is configured, statistics might still be updated outside that time window [#49552](https://github.com/pingcap/tidb/issues/49552) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that old statistics are not automatically deleted when a partitioned table is converted to a non-partitioned table [#49547](https://github.com/pingcap/tidb/issues/49547) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that old statistics are not automatically deleted when you clear data from a non-partitioned table using `TRUNCATE TABLE` [#49663](https://github.com/pingcap/tidb/issues/49663) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that enforced sorting might become ineffective when a query uses optimizer hints (such as `STREAM_AGG()`) that enforce sorting and its execution plan contains `IndexMerge` [#49605](https://github.com/pingcap/tidb/issues/49605) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that histogram statistics might not be parsed into readable strings when the histogram boundary contains `NULL` [#49823](https://github.com/pingcap/tidb/issues/49823) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that executing queries containing the `GROUP_CONCAT(ORDER BY)` syntax might return errors [#49986](https://github.com/pingcap/tidb/issues/49986) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that `UPDATE`, `DELETE`, and `INSERT` statements return overflow errors instead of warnings when the `SQL_MODE` is not strict [#49137](https://github.com/pingcap/tidb/issues/49137) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that data cannot be inserted when a table has a composite index consisting of multi-valued indexes and non-binary type strings [#49680](https://github.com/pingcap/tidb/issues/49680) @[YangKeao](https://github.com/YangKeao)
