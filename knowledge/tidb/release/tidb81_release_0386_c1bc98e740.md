# TiDB 6.5.12 bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.12.md`
- Source Title: `TiDB 6.5.12 Release Notes`
- Source Heading Path: `TiDB 6.5.12 Release Notes > Bug fixes`
- Source Line Ranges: `47-85`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`
- Topic Tags: `release-notes`, `bug-fixes`, `sql`, `optimizer`, `cte`, `index-merge`, `stale-read`, `consistency`, `memory-leak`, `ddl-owner`, `add-index`, `slow-query`, `information-schema`, `prepare-protocol`, `temporary-tables`, `partitioned-tables`, `views`, `type-conversion`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0386_c1bc98e740`
- Source ID: `tidb-docs-8.1:releases/release-6.5.12.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f00721f06ae8ea87262dd9ae632453fc1267e6d2eaade1bc6252504eddd5aab1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.12#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.12.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.12 bug fixes affecting SQL behavior, optimizer, DDL, stale read, slow query tables, CTEs, views, and type handling.
- Retrieval Keywords: TiDB 6.5.12 bug fixes, NATURAL JOIN, USING clause, CAST character set, LOAD DATA ... REPLACE INTO, data inconsistency, ADD INDEX, index length limitation, Common Table Expression, CTE, IndexMerge, BIT to CHAR, TiKV panics, CREATE VIEW, variables or parameters, memory leaks, PD member, distributed execution framework, cluster_slow_query, ORDER BY, stale read, TSO, INFORMATION_SCHEMA.columns, INSERT ... ON DUPLICATE KEY, mysql_insert_id, unique index, column IS NULL, IndexLookUp, read_from_storage hint, DELETE statement with aliases, INDEX_HASH_JOIN, DDL Owners, information_schema.cluster_slow_query, duplicate entry, type conversion errors, VIEW, ENUM, Incorrect date value: '0000-00-00', Prepare protocol, non-UTF8 character set, temporary tables, ONLY_FULL_GROUP_BY, partitioned tables, IN condition, slow logs, RADIANS(), BIT column, ORDER BY LIMIT SELECT DISTINCT
- Follow-up Guidance: 
- Classification Note: This is a release-notes bug-fix chunk because the official content is a list of TiDB issues fixed in 6.5.12, each tied to specific SQL statements, tables, hints, or error behaviors.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that using subqueries after the `NATURAL JOIN` or `USING` clause might result in errors [#53766](https://github.com/pingcap/tidb/issues/53766) @[dash12653](https://github.com/dash12653)
    - Fix the issue that the `CAST` function does not support explicitly setting the character set [#55677](https://github.com/pingcap/tidb/issues/55677) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that the `LOAD DATA ... REPLACE INTO` operation causes data inconsistency [#56408](https://github.com/pingcap/tidb/issues/56408) @[fzzf678](https://github.com/fzzf678)
    - Fix the issue that TiDB does not check the index length limitation when executing `ADD INDEX` [#56930](https://github.com/pingcap/tidb/issues/56930) @[fzzf678](https://github.com/fzzf678)
    - Fix the issue of illegal memory access that might occur when a Common Table Expression (CTE) has multiple data consumers and one consumer exits without reading any data [#55881](https://github.com/pingcap/tidb/issues/55881) @[windtalker](https://github.com/windtalker)
    - Fix the issue that some predicates might be lost when constructing `IndexMerge` [#58476](https://github.com/pingcap/tidb/issues/58476) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that converting data from the `BIT` type to the `CHAR` type might cause TiKV panics [#56494](https://github.com/pingcap/tidb/issues/56494) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that using variables or parameters in the `CREATE VIEW` statement does not report errors [#53176](https://github.com/pingcap/tidb/issues/53176) @[mjonss](https://github.com/mjonss)
    - Fix the issue that unreleased session resources might lead to memory leaks [#56271](https://github.com/pingcap/tidb/issues/56271) @[lance6716](https://github.com/lance6716)
    - Fix the issue that executing `ADD INDEX` might fail after modifying the PD member in the distributed execution framework [#48680](https://github.com/pingcap/tidb/issues/48680) @[lance6716](https://github.com/lance6716)
    - Fix the issue that using `ORDER BY` when querying `cluster_slow_query table` might generate unordered results [#51723](https://github.com/pingcap/tidb/issues/51723) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that stale read does not strictly verify the timestamp of the read operation, resulting in a small probability of affecting the consistency of the transaction when an offset exists between the TSO and the real physical time [#56809](https://github.com/pingcap/tidb/issues/56809) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that the performance of querying `INFORMATION_SCHEMA.columns` degrades [#58184](https://github.com/pingcap/tidb/issues/58184) @[lance6716](https://github.com/lance6716)
    - Fix the issue that the `INSERT ... ON DUPLICATE KEY` statement is not compatible with `mysql_insert_id` [#55965](https://github.com/pingcap/tidb/issues/55965) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the optimizer incorrectly estimates the number of rows as 1 when accessing a unique index with the query condition `column IS NULL` [#56116](https://github.com/pingcap/tidb/issues/56116) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that part of the memory of the `IndexLookUp` operator is not tracked [#56440](https://github.com/pingcap/tidb/issues/56440) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the potential data race issue that might occur in TiDB's internal coroutine [#57798](https://github.com/pingcap/tidb/issues/57798) [#56053](https://github.com/pingcap/tidb/issues/56053) @[fishiu](https://github.com/fishiu) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the `read_from_storage` hint might not take effect when the query has an available Index Merge execution plan [#56217](https://github.com/pingcap/tidb/issues/56217) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that execution plan bindings cannot be created for the multi-table `DELETE` statement with aliases [#56726](https://github.com/pingcap/tidb/issues/56726) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that `INDEX_HASH_JOIN` might hang during an abnormal exit [#54055](https://github.com/pingcap/tidb/issues/54055) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that two DDL Owners might exist at the same time [#54689](https://github.com/pingcap/tidb/issues/54689) @[joccau](https://github.com/joccau)
    - Fix the issue that when querying the `information_schema.cluster_slow_query` table, if the time filter is not added, only the latest slow log file is queried [#56100](https://github.com/pingcap/tidb/issues/56100) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that `duplicate entry` might occur when adding unique indexes [#56161](https://github.com/pingcap/tidb/issues/56161) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the error message is incorrect in certain type conversion errors [#41730](https://github.com/pingcap/tidb/issues/41730) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the CTE defined in `VIEW` is incorrectly inlined [#56582](https://github.com/pingcap/tidb/issues/56582) @[elsa0520](https://github.com/elsa0520)
    - Fix the issue that the `UPDATE` statement incorrectly updates values of the `ENUM` type [#56832](https://github.com/pingcap/tidb/issues/56832) @[xhebox](https://github.com/xhebox)
    - Fix the issue that executing the `UPDATE` statement after adding a `DATE` column results in the error `Incorrect date value: '0000-00-00'` in some cases [#59047](https://github.com/pingcap/tidb/issues/59047) @[mjonss](https://github.com/mjonss)
    - Fix the issue that in the Prepare protocol, an error occurs when the client uses a non-UTF8 character set [#58870](https://github.com/pingcap/tidb/issues/58870) @[xhebox](https://github.com/xhebox)
    - Fix the issue that querying temporary tables might trigger unexpected TiKV requests in some cases [#58875](https://github.com/pingcap/tidb/issues/58875) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that the `ONLY_FULL_GROUP_BY` setting does not take effect on statements in views [#53175](https://github.com/pingcap/tidb/issues/53175) @[mjonss](https://github.com/mjonss)
    - Fix the issue that querying partitioned tables using an `IN` condition containing a mismatched value type and a type conversion error leads to incorrect query results [#54746](https://github.com/pingcap/tidb/issues/54746) @[mjonss](https://github.com/mjonss)
    - Fix the issue that querying slow logs might fail when certain fields contain empty values [#58147](https://github.com/pingcap/tidb/issues/58147) @[yibin87](https://github.com/yibin87)
    - Fix the issue that the `RADIANS()` function computes values in an incorrect order [#57671](https://github.com/pingcap/tidb/issues/57671) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that the default value of the `BIT` column is incorrect [#57301](https://github.com/pingcap/tidb/issues/57301) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that an inline error might occur if a CTE contains `ORDER BY`, `LIMIT`, or `SELECT DISTINCT` clauses and is referenced by the recursive part of another CTE [#56603](https://github.com/pingcap/tidb/issues/56603) @[elsa0520](https://github.com/elsa0520)
