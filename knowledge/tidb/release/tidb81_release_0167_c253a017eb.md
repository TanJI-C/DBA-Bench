# TiDB 4.0.13 bug fixes for TiDB

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.13.md`
- Source Title: `TiDB 4.0.13 Release Notes`
- Source Heading Path: `TiDB 4.0.13 Release Notes > Bug Fixes`
- Source Line Ranges: `54-103`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`, `shared`
- Topic Tags: `release-notes`, `bug-fixes`, `query-results`, `panic`, `ddl`, `collation`, `privileges`, `optimizer`, `tiflash`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0167_c253a017eb`
- Source ID: `tidb-docs-8.1:releases/release-4.0.13.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `15fa7a149745c50adb15708b28317da983476ae7c74314ce5e097ca9dd5b2aad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.13#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.13.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 4.0.13 bug fixes related to wrong query results, panic, DDL, collation, privileges, optimizer behavior, or TiFlash selection in TiDB.
- Retrieval Keywords: TiDB 4.0.13 bug fixes, UPDATE statement with a subquery updates the generated column, duplicate query results multi-column index, BIT type constant as the divisor in the DIV expression, NO_ZERO_IN_DATE, insert ignore on duplicate, Audit plugin causes TiDB panic, HashJoin collation, batch_point_get, tidb_row_format_version, enable_new_collation, approx_percent, TiKV server timeout, IndexJoin prefix column index, group_concat_max_len, USE_INDEX_MERGE hint does not take effect, ANALYZE with enable_new_collation enabled, cancelling DDL jobs gets stuck, show table status, REPLACE operation privileges, RANGE partitions, tidb_enable_table_partition, Coprocessor Cache panel of Grafana does not work, statistic cache
- Follow-up Guidance: The chunk enumerates many individual TiDB bug fixes, each identified by the affected SQL statement, function, variable, operator, or error behavior.
- Classification Note: The content is classified as TiDB bug fixes because it is the Bug Fixes section and every listed item describes a corrected TiDB issue in 4.0.13.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix the panic issue that occurs when the `UPDATE` statement with a subquery updates the generated column [#24658](https://github.com/pingcap/tidb/pull/24658)
    - Fix the issue that causes duplicate query results when using the multi-column index for data reads [#24634](https://github.com/pingcap/tidb/pull/24634)
    - Fix the issue that causes wrong query result when using the `BIT` type constant as the divisor in the DIV expression [#24266](https://github.com/pingcap/tidb/pull/24266)
    - Fix the issue that the `NO_ZERO_IN_DATE` SQL mode does not take effect for the default column value set in DDL statements [#24185](https://github.com/pingcap/tidb/pull/24185)
    - Fix an issue which causes wrong query results when using `UNION` between a `BIT` type column and an `INTEGER` type column [#24026](https://github.com/pingcap/tidb/pull/24026)
    - Fix the issue that the `TableDual` plans are mistakenly created when comparing the `BINARY` type and the `CHAR` type [#23917](https://github.com/pingcap/tidb/pull/23917)
    - Fix the issue that the `insert ignore on duplicate` statement might unexpectedly delete table records [#23825](https://github.com/pingcap/tidb/pull/23825)
    - Fix the issue that the Audit plugin causes TiDB panic [#23819](https://github.com/pingcap/tidb/pull/23819)
    - Fix the issue that the `HashJoin` operator incorrectly processes the collation [#23812](https://github.com/pingcap/tidb/pull/23812)
    - Fix the issue of disconnection that occurs when `batch_point_get` incorrectly handles abnormal values in the pessimistic transaction [#23778](https://github.com/pingcap/tidb/pull/23778)
    - Fix the issue of inconsistent indexes that occurs when the `tidb_row_format_version` configuration value is set to `1` and the `enable_new_collation` value is set to `true` [#23772](https://github.com/pingcap/tidb/pull/23772)
    - Fix a bug that occurs when comparing the `INTEGER` type column with the `STRING` constant value [#23705](https://github.com/pingcap/tidb/pull/23705)
    - Fix the error that occurs when the `BIT` type column is passed into the `approx_percent` function [#23702](https://github.com/pingcap/tidb/pull/23702)
    - Fix a bug that causes TiDB to mistakenly report the `TiKV server timeout` error when executing TiFlash batch requests [#23700](https://github.com/pingcap/tidb/pull/23700)
    - Fix the issue that the `IndexJoin` operator returns wrong results on the prefix column index [#23691](https://github.com/pingcap/tidb/pull/23691)
    - Fix the issue which causes wrong query results because the collation on the `BINARY` type column is not properly handled [#23598](https://github.com/pingcap/tidb/pull/23598)
    - Fix the issue of query panic that occurs when the `UPDATE` statement contains the join query with the `HAVING` clause [#23575](https://github.com/pingcap/tidb/pull/23575)
    - Fix the issue that causes TiFlash to return wrong results when using the `NULL` constant in the comparison expression [#23474](https://github.com/pingcap/tidb/pull/23474)
    - Fix the issue of wrong results when comparing the `YEAR` type column with the `STRING` constant [#23335](https://github.com/pingcap/tidb/pull/23335)
    - Fix the issue that `group_concat` panics when `session.group_concat_max_len` is set too small [#23257](https://github.com/pingcap/tidb/pull/23257)
    - Fix the issue of wrong query results that occurs when using the `BETWEEN` expression for the `TIME` type column [#23233](https://github.com/pingcap/tidb/pull/23233)
    - Fix the issue of privilege check in the `DELETE` statements [#23215](https://github.com/pingcap/tidb/pull/23215)
    - Fix the issue that no error is reported when inserting invalid strings to the `DECIMAL` type column [#23196](https://github.com/pingcap/tidb/pull/23196)
    - Fix the issue of parsing error occurred when inserting data to the `DECIMAL` type columns [#23152](https://github.com/pingcap/tidb/pull/23152)
    - Fix the issue that the `USE_INDEX_MERGE` hint does not take effect [#22924](https://github.com/pingcap/tidb/pull/22924)
    - Fix a bug that the query returns wrong results when using `ENUM` or `SET` columns in the `WHERE` clause as an filter [#22814](https://github.com/pingcap/tidb/pull/22814)
    - Fix a bug that the query returns wrong results when using the clustered index and the new collation at the same time [#21408](https://github.com/pingcap/tidb/pull/21408)
    - Fix the panic that occurs when executing `ANALYZE` with `enable_new_collation` enabled [#21299](https://github.com/pingcap/tidb/pull/21299)
    - Fix the issue that SQL views does not correctly handle the default roles associated with the SQL DEFINER [#24531](https://github.com/pingcap/tidb/pull/24531)
    - Fix the issue that cancelling DDL jobs gets stuck [#24445](https://github.com/pingcap/tidb/pull/24445)
    - Fix the issue that the `concat` function incorrectly handles the collation [#24300](https://github.com/pingcap/tidb/pull/24300)
    - Fix a bug that the query returns wrong results when the `SELECT` field has an `IN` subquery and the subquery's outer side contains `NULL` tuples [#24022](https://github.com/pingcap/tidb/pull/24022)
    - Fix a bug that TiFlash is chosen wrongly by the optimizer when `TableScan` is in descending order [#23974](https://github.com/pingcap/tidb/pull/23974)
    - Fix a bug that the `point_get` plan returns the column name that is inconsistent with that of MySQL [#23970](https://github.com/pingcap/tidb/pull/23970)
    - Fix the issue that executing the `show table status` statement on a database with a upper-cased name returns wrong results [#23958](https://github.com/pingcap/tidb/pull/23958)
    - Fix a bug that the users who do not have the `INSERT` and `DELETE` privileges on a table at the same time can perform the `REPLACE` operation [#23938](https://github.com/pingcap/tidb/pull/23938)
    - Fix the issue that the results of the `concat`/`make_set`/`insert` expressions are wrong because the collation is incorrectly handled [#23878](https://github.com/pingcap/tidb/pull/23878)
    - Fix the panic that occurs when executing a query on the table that has `RANGE` partitions [#23689](https://github.com/pingcap/tidb/pull/23689)
    - Fix the issue: In the cluster of an earlier version, if the `tidb_enable_table_partition` variable is set to `false`, the tables that contain partitions are handled as non-partitioned tables. Executing `batch point get` queries on this table, when the cluster is upgraded to a later version, causes connection panic. [#23682](https://github.com/pingcap/tidb/pull/23682)
    - Fix the issue that when TiDB is configured to listen on TCP and UNIX sockets, the remote hosts over the TCP connection are not correctly validated for connection [#23513](https://github.com/pingcap/tidb/pull/23513)
    - Fix a bug that the non-default collation causes wrong query results [#22923](https://github.com/pingcap/tidb/pull/22923)
    - Fix a bug that the **Coprocessor Cache** panel of Grafana does not work [#22617](https://github.com/pingcap/tidb/pull/22617)
    - Fix the error that occurs when the optimizer accesses the statistic cache [#22565](https://github.com/pingcap/tidb/pull/22565)

+ TiKV
