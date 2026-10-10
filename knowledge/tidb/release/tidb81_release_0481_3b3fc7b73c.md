# 7.1.6 bug fixes for SQL execution, optimizer, metadata, and restore behavior

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.6.md`
- Source Title: `TiDB 7.1.6 Release Notes`
- Source Heading Path: `TiDB 7.1.6 Release Notes > Bug fixes`
- Source Line Ranges: `72-109`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `bug-fixes`, `sql-execution`, `optimizer`, `statistics`, `ddl`, `dml`, `indexing`, `transactions`, `views`, `information-schema`, `warnings`, `panic`, `memory-usage`, `plan-cache`, `restore`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0481_3b3fc7b73c`
- Source ID: `tidb-docs-8.1:releases/release-7.1.6.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e2a0fcb97c0553cf0eedf4651d564bc8d85febf17371df5096d1d010c8ca8722`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.6 bug fixes affecting SQL execution, optimizer behavior, statistics, DDL or DML concurrency, warnings, panic cases, metadata tables, restore behavior, or monitoring metrics.
- Retrieval Keywords: TiDB 7.1.6 Bug fixes, #52914 concurrent DML adding unique index inconsistent data indexes, #54897 DXF network partition adding indexes inconsistent data indexes, YEAR type unsigned integer out of range incorrect results, #54688 INDEX_HASH_JOIN cannot exit properly abnormally interrupted, SHOW WARNINGS panic, #54324 INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY panic, memTracker HashJoin IndexLookUp Apply high memory usage, recursive CTE invalid pointers, empty projection TiDB panic, virtual columns transactions data modification incorrect query results, AUTO_ID_CACHE=1 auto_increment_increment auto_increment_offset incorrect auto-increment ID allocation, ALL function subqueries incorrect results, virtual columns UnionScan predicate pushdown, UPDATE list subqueries TiDB panic, GROUP BY indirect placeholder ? cannot find columns, Sort operator spills disk files not deleted after query error, SELECT ... FOR UPDATE wrong point get plans, max_execute_time settings interfere with each other, histogram and TopN primary key column statistics not loaded after restarting TiDB, TopN operator pushed down incorrectly, SELECT WHERE ORDER BY poor performance, closing the connection error in the log, DECIMAL(0,0) illegal column type can be created, information_schema.columns warning 1356 view definition subquery column definition, unique index column IS NULL row estimate 1, SELECT INTO OUTFILE clustered indexes predicates, Optimizer Hints incorrect WARNINGS information, Sync Load QPS monitoring metric incorrect, CREATE OR REPLACE VIEW concurrently table doesn't exist, RESTORE AUTO_ID_CACHE=1 Duplicate entry, INFORMATION_SCHEMA.STATISTICS SUB_PART NULL, Longlong type overflow in predicates, cached execution plans date types unix_timestamp incorrect results, LENGTH() condition unexpectedly removed utf8_bin utf8mb4_bin
- Follow-up Guidance: This chunk also helps when matching specific issue identifiers such as #52914, #54897, #54324, #52680, or operational phrases like `Duplicate entry`, `table doesn't exist`, and `warning 1356`.
- Classification Note: The official content is a TiDB 7.1.6 release-note bug-fix list covering multiple SQL, optimizer, metadata, restore, and monitoring issues under the TiDB component.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue of inconsistent data indexes caused by concurrent DML operations when adding a unique index [#52914](https://github.com/pingcap/tidb/issues/52914) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that comparing a column of `YEAR` type with an unsigned integer that is out of range causes incorrect results [#50235](https://github.com/pingcap/tidb/issues/50235) @[qw4990](https://github.com/qw4990)
    - Fix the issue that `INDEX_HASH_JOIN` cannot exit properly when SQL is abnormally interrupted [#54688](https://github.com/pingcap/tidb/issues/54688) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the network partition during adding indexes using the Distributed eXecution Framework (DXF) might cause inconsistent data indexes [#54897](https://github.com/pingcap/tidb/issues/54897) @[tangenta](https://github.com/tangenta)
    - Fix the issue that using `SHOW WARNINGS;` to obtain warnings might cause a panic [#48756](https://github.com/pingcap/tidb/issues/48756) @[xhebox](https://github.com/xhebox)
    - Fix the issue that querying the `INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY` table might cause TiDB to panic [#54324](https://github.com/pingcap/tidb/issues/54324) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue of abnormally high memory usage caused by `memTracker` not being detached when the `HashJoin` or `IndexLookUp` operator is the driven side sub-node of the `Apply` operator [#54005](https://github.com/pingcap/tidb/issues/54005) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that recursive CTE queries might result in invalid pointers [#54449](https://github.com/pingcap/tidb/issues/54449) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that an empty projection causes TiDB to panic [#49109](https://github.com/pingcap/tidb/issues/49109) @[winoros](https://github.com/winoros)
    - Fix the issue that TiDB might return incorrect query results when you query tables with virtual columns in transactions that involve data modification operations [#53951](https://github.com/pingcap/tidb/issues/53951) @[qw4990](https://github.com/qw4990)
    - Fix the issue that for tables containing auto-increment columns with `AUTO_ID_CACHE=1`, setting `auto_increment_increment` and `auto_increment_offset` system variables to non-default values might cause incorrect auto-increment ID allocation [#52622](https://github.com/pingcap/tidb/issues/52622) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that subqueries included in the `ALL` function might cause incorrect results [#52755](https://github.com/pingcap/tidb/issues/52755) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that predicates cannot be pushed down properly when the filter condition of a SQL query contains virtual columns and the execution condition contains `UnionScan` [#54870](https://github.com/pingcap/tidb/issues/54870) @[qw4990](https://github.com/qw4990)
    - Fix the issue that subqueries in an `UPDATE` list might cause TiDB to panic [#52687](https://github.com/pingcap/tidb/issues/52687) @[winoros](https://github.com/winoros)
    - Fix the issue that indirect placeholder `?` references in a `GROUP BY` statement cannot find columns [#53872](https://github.com/pingcap/tidb/issues/53872) @[qw4990](https://github.com/qw4990)
    - Fix the issue that disk files might not be deleted after the `Sort` operator spills and a query error occurs [#55061](https://github.com/pingcap/tidb/issues/55061) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue of reusing wrong point get plans for `SELECT ... FOR UPDATE` [#54652](https://github.com/pingcap/tidb/issues/54652) @[qw4990](https://github.com/qw4990)
    - Fix the issue that `max_execute_time` settings at multiple levels interfere with each other [#50914](https://github.com/pingcap/tidb/issues/50914) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that the histogram and TopN in the primary key column statistics are not loaded after restarting TiDB [#37548](https://github.com/pingcap/tidb/issues/37548) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the TopN operator might be pushed down incorrectly [#37986](https://github.com/pingcap/tidb/issues/37986) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the performance of the `SELECT ... WHERE ... ORDER BY ...` statement execution is poor in some cases [#54969](https://github.com/pingcap/tidb/issues/54969) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that TiDB reports an error in the log when closing the connection in some cases [#53689](https://github.com/pingcap/tidb/issues/53689) @[jackysp](https://github.com/jackysp)
    - Fix the issue that the illegal column type `DECIMAL(0,0)` can be created in some cases [#53779](https://github.com/pingcap/tidb/issues/53779) @[tangenta](https://github.com/tangenta)
    - Fix the issue that obtaining the column information using `information_schema.columns` returns warning 1356 when a subquery is used as a column definition in a view definition [#54343](https://github.com/pingcap/tidb/issues/54343) @[lance6716](https://github.com/lance6716)
    - Fix the issue that the optimizer incorrectly estimates the number of rows as 1 when accessing a unique index with the query condition `column IS NULL` [#56116](https://github.com/pingcap/tidb/issues/56116) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that `SELECT INTO OUTFILE` does not work when clustered indexes are used as predicates [#42093](https://github.com/pingcap/tidb/issues/42093) @[qw4990](https://github.com/qw4990)
    - Fix the issue of incorrect WARNINGS information when using Optimizer Hints [#53767](https://github.com/pingcap/tidb/issues/53767) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the Sync Load QPS monitoring metric is incorrect [#53558](https://github.com/pingcap/tidb/issues/53558) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that executing `CREATE OR REPLACE VIEW` concurrently might result in the `table doesn't exist` error [#53673](https://github.com/pingcap/tidb/issues/53673) @[tangenta](https://github.com/tangenta)
    - Fix the issue that restoring a table with `AUTO_ID_CACHE=1` using the `RESTORE` statement might cause a `Duplicate entry` error [#52680](https://github.com/pingcap/tidb/issues/52680) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the `SUB_PART` value in the `INFORMATION_SCHEMA.STATISTICS` table is `NULL` [#55812](https://github.com/pingcap/tidb/issues/55812) @[Defined2014](https://github.com/Defined2014)
    - Fix the overflow issue of the `Longlong` type in predicates [#45783](https://github.com/pingcap/tidb/issues/45783) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that incorrect results are returned when the cached execution plans contain the comparison between date types and `unix_timestamp` [#48165](https://github.com/pingcap/tidb/issues/48165) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the `LENGTH()` condition is unexpectedly removed when the collation is `utf8_bin` or `utf8mb4_bin` [#53730](https://github.com/pingcap/tidb/issues/53730) @[elsa0520](https://github.com/elsa0520)
