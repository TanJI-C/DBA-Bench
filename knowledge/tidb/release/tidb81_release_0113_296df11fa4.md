# TiDB 3.0.2 release notes and TiDB fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.2.md`
- Source Title: `TiDB 3.0.2 Release Notes`
- Source Heading Path: `TiDB 3.0.2 Release Notes | TiDB 3.0.2 Release Notes > TiDB`
- Source Line Ranges: `5-53`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `release-notes`, `sql-optimizer`, `sql-execution`, `bug-fixes`, `query-plans`, `query-results`, `window-functions`, `explain-analyze`, `statistics`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0113_296df11fa4`
- Source ID: `tidb-docs-8.1:releases/release-3.0.2.md#tidb-3-0-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f35076534f93d03331a8c43d17da2c91e7b286bdc5e0057e2e9c241365724854`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.2#tidb-3-0-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.0.2 fixes or behavior changes in SQL optimizer and SQL execution, especially around wrong query plans, wrong query results, MySQL compatibility, window functions, EXPLAIN output, and statistics.
- Retrieval Keywords: TiDB 3.0.2 Release Notes, TiDB 3.0.2, SQL Optimizer, SQL Execution Engine, Can't find column in schema, same table occurs multiple times in a query, TIDB_INLJ hint, explain select /*+ TIDB_INLJ(t1) */, SELECT IF(1,c,c) FROM t, SELECT 0 LIKE 'a string', SHOW COLUMNS FROM tbl WHERE FIELDS IN (SELECT 'a'), outerJoinElimination, window function, UNBOUNDED PRECEDING, ERROR 3593 (HY000): You cannot use the window function FUNCTION_NAME in this context, IGNORE NULLS, time equal conditions, Top-N statistics, INSERT function contains NULL in parameters, ADMIN CHECKSUM, partitioned table, INDEX JOIN uses the prefix index, DATE_ADD, DATE_SUB, INTERVAL, microseconds, Mod(%), Multiple(*), Minus(-), max_allowed_packet, CONCAT, CONCAT_WS, SUBTIME, ADDTIME, CONVERT_TZ, EXPLAIN ANALYZE, MEMORY column, EXPLAIN, CARTESIAN Join, auto-increment columns, float and double types, pseudo statistics are dumped, CASE WHEN ELSE NULL, constant folding optimization, floatStrToIntStr, +999.9999e2, REGEXP BINARY, GRANT ROLE, CURRENT_ROLE, REVOKE ROLE, mysql.default_role, Incorrect datetime value, SELECT ADDDATE('2008-01-34', -1), constant overflows float, constant overflows bigint, JSON data converted to an integer, FLOAT DOUBLE DECIMAL column parameters, Index Lookup Join contains the prefix index, Ranger, NAME_CONST, Incorrect arguments to NAME_CONST
- Follow-up Guidance: The source lists specific corrected examples and phrases for these TiDB 3.0.2 fixes, including `EXPLAIN ANALYZE` with the `MEMORY` column and `EXPLAIN` with `CARTESIAN` Join.
- Classification Note: This is a self-managed TiDB release-notes chunk for version 3.0.2 focused on TiDB SQL optimizer and execution bug fixes, compatibility fixes, and query plan or result changes.

## Official Source Content

# TiDB 3.0.2 Release Notes

Release date: August 7, 2019

TiDB version: 3.0.2

TiDB Ansible version: 3.0.2
## TiDB

+ SQL Optimizer
    - Fix the issue that the "Can't find column in schema" message is reported when the same table occurs multiple times in a query and logically the query result is always empty [#11247](https://github.com/pingcap/tidb/pull/11247)
    - Fix the issue that the query plan does not meet the expectation caused by the `TIDB_INLJ` hint not working correctly in some cases (like `explain select /*+ TIDB_INLJ(t1) */ t1.b, t2.a from t t1, t t2 where t1.b = t2.a`) [#11362](https://github.com/pingcap/tidb/pull/11362)
    - Fix the issue that the column name in the query result is wrong in some cases (like `SELECT IF(1,c,c) FROM t`) [#11379](https://github.com/pingcap/tidb/pull/11379)
    - Fix the issue that some queries like `SELECT 0 LIKE 'a string'` return `TRUE` because the `LIKE` expression is implicitly converted to 0 in some cases [#11411](https://github.com/pingcap/tidb/pull/11411)
    - Support sub-queries in the `SHOW` statement, like `SHOW COLUMNS FROM tbl WHERE FIELDS IN (SELECT 'a')` [#11459](https://github.com/pingcap/tidb/pull/11459)
    - Fix the issue that the related column of the aggregate function cannot be found and an error is reported caused by the `outerJoinElimination` optimizing rule not correctly handling the column alias; improve alias parsing in the optimizing process to make optimization cover more query types [#11377](https://github.com/pingcap/tidb/pull/11377)
    - Fix the issue that no error is reported when the syntax restriction is violated in the Window function (for example, `UNBOUNDED PRECEDING` is not allowed to appear at the end of the Frame definition) [#11543](https://github.com/pingcap/tidb/pull/11543)
    - Fix the issue that `FUNCTION_NAME` is in uppercase in the `ERROR 3593 (HY000): You cannot use the window function FUNCTION_NAME in this context` error message, which causes incompatibility with MySQL [#11535](https://github.com/pingcap/tidb/pull/11535)
    - Fix the issue that the unimplemented `IGNORE NULLS` syntax in the Window function is used but no error is reported [#11593](https://github.com/pingcap/tidb/pull/11593)
    - Fix the issue that the Optimizer does not correctly estimate time equal conditions [#11512](https://github.com/pingcap/tidb/pull/11512)
    - Support updating the Top-N statistics based on the feedback information [#11507](https://github.com/pingcap/tidb/pull/11507)
+ SQL Execution Engine
    - Fix the issue that the returned value is not `NULL` when the `INSERT` function contains `NULL` in parameters [#11248](https://github.com/pingcap/tidb/pull/11248)
    - Fix the issue that the computing result might be wrong when the partitioned table is checked by the `ADMIN CHECKSUM` operation [#11266](https://github.com/pingcap/tidb/pull/11266)
    - Fix the issue that the result might be wrong when INDEX JOIN uses the prefix index [#11246](https://github.com/pingcap/tidb/pull/11246)
    - Fix the issue that result might be wrong caused by incorrectly aligning fractions when the `DATE_ADD` function does subtraction on date numbers involving microseconds [#11288](https://github.com/pingcap/tidb/pull/11288)
    - Fix the wrong result caused by the `DATE_ADD` function incorrectly processing the negative numbers in `INTERVAL` [#11325](https://github.com/pingcap/tidb/pull/11325)
    - Fix the issue that the number of fractional digits returned by `Mod(%)`, `Multiple(*)` or `Minus(-)` is different from that in MySQL when `Mod(%)`, `Multiple(*)` or `Minus(-)` returns 0 and the number of fractional digits is large (like `select 0.000 % 0.11234500000000000000`) [#11251](https://github.com/pingcap/tidb/pull/11251)
    - Fix the issue that `NULL` with a warning is incorrectly returned when the length of the result returned by `CONCAT` and `CONCAT_WS` functions exceeds `max_allowed_packet` [#11275](https://github.com/pingcap/tidb/pull/11275)
    - Fix the issue that `NULL` with a warning is incorrectly returned when parameters in the `SUBTIME` and `ADDTIME` functions are invalid [#11337](https://github.com/pingcap/tidb/pull/11337)
    - Fix the issue that `NULL` is incorrectly returned when parameters in the `CONVERT_TZ` function are invalid [#11359](https://github.com/pingcap/tidb/pull/11359)
    - Add the `MEMORY` column to the result returned by `EXPLAIN ANALYZE` to show the memory usage of this query [#11418](https://github.com/pingcap/tidb/pull/11418)
    - Add `CARTESIAN` Join to the result of `EXPLAIN` [#11429](https://github.com/pingcap/tidb/pull/11429)
    - Fix the incorrect data of auto-increment columns of the float and double types [#11385](https://github.com/pingcap/tidb/pull/11385)
    - Fix the panic issue caused by some `nil` information when pseudo statistics are dumped [#11460](https://github.com/pingcap/tidb/pull/11460)
    - Fix the incorrect query result of `SELECT … CASE WHEN … ELSE NULL ...` caused by constant folding optimization [#11441](https://github.com/pingcap/tidb/pull/11441)
    - Fix the issue that `floatStrToIntStr` does not correctly parse the input such as `+999.9999e2` [#11473](https://github.com/pingcap/tidb/pull/11473)
    - Fix the issue that `NULL` is not returned in some cases when the result of the `DATE_ADD` and `DATE_SUB` function overflows [#11476](https://github.com/pingcap/tidb/pull/11476)
    - Fix the issue that the conversion result is different from that in MySQL if the string contains an invalid character when a long string is converted to an integer [#11469](https://github.com/pingcap/tidb/pull/11469)
    - Fix the issue that the result of the `REGEXP BINARY` function is incompatible with MySQL caused by case sensitiveness of this function [#11504](https://github.com/pingcap/tidb/pull/11504)
    - Fix the issue that an error is reported when the `GRANT ROLE` statement receives `CURRENT_ROLE`; fix the issue that the `REVOKE ROLE` statement does not correctly revoke the `mysql.default_role` privilege [#11356](https://github.com/pingcap/tidb/pull/11356)
    - Fix the display format issue of the `Incorrect datetime value` warning information when executing statements like `SELECT ADDDATE('2008-01-34', -1)` [#11447](https://github.com/pingcap/tidb/pull/11447)
    - Fix the issue that the error message reports `constant … overflows float` rather than `constant … overflows bigint` if the result overflows when a float field of the JSON data is converted to an integer [#11534](https://github.com/pingcap/tidb/pull/11534)
    - Fix the issue that the result might be wrong caused by incorrect type conversion when the `DATE_ADD` function receives `FLOAT`, `DOUBLE` and `DECIMAL` column parameters [#11527](https://github.com/pingcap/tidb/pull/11527)
    - Fix the wrong result caused by incorrectly processing the sign of the INTERVAL fraction in the `DATE_ADD` function [#11615](https://github.com/pingcap/tidb/pull/11615)
    - Fix the incorrect query result when Index Lookup Join contains the prefix index caused by `Ranger` not correctly handling the prefix index [#11565](https://github.com/pingcap/tidb/pull/11565)
    - Fix the issue that the "Incorrect arguments to NAME_CONST" message is reported if the `NAME_CONST` function is executed when the second parameter of `NAME_CONST` is a negative number [#11268](https://github.com/pingcap/tidb/pull/11268)
