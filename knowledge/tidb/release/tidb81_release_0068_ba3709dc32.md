# TiDB 2.1.19 release notes for TiDB server, SQL, and DDL

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.19.md`
- Source Title: `TiDB 2.1.19 Release Notes`
- Source Heading Path: `TiDB 2.1.19 Release Notes | TiDB 2.1.19 Release Notes > TiDB`
- Source Line Ranges: `5-67`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `release-notes`, `sql-optimizer`, `sql-execution`, `slow-query`, `http-api`, `server-configuration`, `ddl`, `statistics`, `timezone`, `binlog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0068_ba3709dc32`
- Source ID: `tidb-docs-8.1:releases/release-2.1.19.md#tidb-2-1-19-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5ed7564d1ba6e7dd23c41a9a3d43f9635b9e9392b2a89a34d4fb42b86b94165d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.19#tidb-2-1-19-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.19.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 2.1.19 release-note changes in SQL Optimizer, SQL Execution Engine, Server, or DDL, including specific fixes, new slow_query fields, HTTP API updates, and configuration items.
- Retrieval Keywords: TiDB 2.1.19 Release Notes, SQL Optimizer, SQL Execution Engine, slow_query table, Prewrite_time, Commit_time, Get_commit_ts_time, Commit_backoff_time, Backoff_types, Resolve_lock_time, Local_latch_wait_time, Write_key, Write_size, Prewrite_region, Txn_retry, select max(_tidb_rowid) from t, PhysicalUnionScan, ANALYZE, ADMIN CHECK TABLE, partitioned tables, SHOW CREATE TABLE, information_schema.KEY_COLUMN_USAGE, Streaming, Invalid time format, daylight saving time, sum(distinct), KILL CONNECTION, info/all interface, HTTP API, server-version, plugin, COLLATE, BIT column, drop column, Drainer
- Follow-up Guidance: This chunk also points to related 2.1.19 changes in binlog status via the info/all HTTP API, the server-version configuration item, and DDL behavior affecting downstream Drainer.
- Classification Note: The official content is classified as a TiDB release-notes chunk because it lists TiDB 2.1.19 changes across optimizer, execution, server, and DDL areas.

## Official Source Content

# TiDB 2.1.19 Release Notes

Release date: December 27, 2019

TiDB version: 2.1.19

TiDB Ansible version: 2.1.19
## TiDB

+ SQL Optimizer
    - Optimize the scenario of `select max(_tidb_rowid) from t` to avoid full table scan [#13294](https://github.com/pingcap/tidb/pull/13294)
    - Fix the incorrect results caused by the incorrect value assigned to the user variable in the query and the push-down of predicates [#13230](https://github.com/pingcap/tidb/pull/13230)
    - Fix the issue that the statistics are not accurate because a data race occurs when statistics are updated [#13690](https://github.com/pingcap/tidb/pull/13690)
    - Fix the issue that the result is incorrect when the `UPDATE` statement contains both a sub-query and a stored generated column; fix the `UPDATE` statement execution error when this statement contains two same-named tables from different databases [#13357](https://github.com/pingcap/tidb/pull/13357)
    - Fix the issue that the query plan might be incorrectly selected because the `PhysicalUnionScan` operator incorrectly sets the statistics [#14134](https://github.com/pingcap/tidb/pull/14134)
    - Remove the `minAutoAnalyzeRatio` constraint to make the automatic `ANALYZE` more timely [#14013](https://github.com/pingcap/tidb/pull/14013)
    - Fix the issue that the estimated number of rows is greater than `1` when the `WHERE` clause contains an equal condition on the unique key [#13385](https://github.com/pingcap/tidb/pull/13385)
+ SQL Execution Engine
    - Fix the precision overflow when using `int64` as the intermediate result of `unit64` in `ConvertJSONToInt` [#13036](https://github.com/pingcap/tidb/pull/13036)
    - Fix the issue that when the `SLEEP` function is in a query (for example, `select 1 from (select sleep(1)) t;)`), column pruning causes `sleep(1)` in the query to be invalid [#13039](https://github.com/pingcap/tidb/pull/13039)
    - Reduce memory overhead by reusing `Chunk` in the `INSERT ON DUPLICATE UPDATE` statement [#12999](https://github.com/pingcap/tidb/pull/12999)
    - Add more transaction-related fields for the `slow_query` table [#13129](https://github.com/pingcap/tidb/pull/13129):
        - `Prewrite_time`
        - `Commit_time`
        - `Get_commit_ts_time`
        - `Commit_backoff_time`
        - `Backoff_types`
        - `Resolve_lock_time`
        - `Local_latch_wait_time`
        - `Write_key`
        - `Write_size`
        - `Prewrite_region`
        - `Txn_retry`
    - Fix the issue that a subquery contained in an `UPDATE` statement is incorrectly converted; fix the `UPDATE` execution failure when the `WHERE` clause contains a subquery [#13120](https://github.com/pingcap/tidb/pull/13120)
    - Support executing `ADMIN CHECK TABLE` on partitioned tables [#13143](https://github.com/pingcap/tidb/pull/13143)
    - Fix the issue that the precision of statements such as `SHOW CREATE TABLE` is incomplete when `ON UPDATE CURRENT_TIMESTAMP` is used as a column attribute and floating point precision is specified [#12462](https://github.com/pingcap/tidb/pull/12462)
    - Fix the panic occurred when executing the `SELECT * FROM information_schema.KEY_COLUMN_USAGE` statement because the foreign key is not checked when dropping, modifying or changing the column [#14162](https://github.com/pingcap/tidb/pull/14162)
    - Fix the issue that the returned data might be duplicated when `Streaming` is enabled in TiDB [#13255](https://github.com/pingcap/tidb/pull/13255)
    - Fix the `Invalid time format` error caused by daylight saving time [#13624](https://github.com/pingcap/tidb/pull/13624)
    - Fix the issue that data is incorrect because the precision is lost when an integer is converted to an unsigned floating point or decimal type [#13756](https://github.com/pingcap/tidb/pull/13756)
    - Fix the issue that an incorrect type of value is returned when the `Quote` function handles the `NULL` value [#13681](https://github.com/pingcap/tidb/pull/13681)
    - Fix the issue that the timezone is incorrect after parsing the date from strings using `gotime.Local` [#13792](https://github.com/pingcap/tidb/pull/13792)
    - Fix the issue that the result might be incorrect because the `binSearch` function does not return an error in the implementation of `builtinIntervalRealSig` [#13768](https://github.com/pingcap/tidb/pull/13768)
    - Fix the issue that an error might occur when converting the string type to the floating point type in the `INSERT` statement execution [#14009](https://github.com/pingcap/tidb/pull/14009)
    - Fix the incorrect result returned from the `sum(distinct)` function [#13041](https://github.com/pingcap/tidb/pull/13041)
    - Fix the issue that `data too long` is returned when `CAST` converting the data in `union` of the same location to the merged type because the returned type length of the `jsonUnquoteFunction` function is given an incorrect value [#13645](https://github.com/pingcap/tidb/pull/13645)
    - Fix the issue that the password cannot be set because the privilege check is too strict [#13805](https://github.com/pingcap/tidb/pull/13805)
+ Server
    - Fix the issue that `KILL CONNECTION` might cause the goroutine leak [#13252](https://github.com/pingcap/tidb/pull/13252)
    - Support getting the binlog status of all TiDB nodes via the `info/all` interface of the HTTP API [#13188](https://github.com/pingcap/tidb/pull/13188)
    - Fix the failure to build the TiDB project on Windows [#13650](https://github.com/pingcap/tidb/pull/13650)
    - Add the `server-version` configuration item to control and modify the version of TiDB server [#13904](https://github.com/pingcap/tidb/pull/13904)
    - Fix the issue that the binary `plugin` compiled with Go1.13 does not run normally [#13527](https://github.com/pingcap/tidb/pull/13527)
+ DDL
    - Use the table's `COLLATE` instead of the system's default charset in the column when a table is created and the table contains `COLLATE` [#13190](https://github.com/pingcap/tidb/pull/13190)
    - Limit the length of the index name when creating a table [#13311](https://github.com/pingcap/tidb/pull/13311)
    - Fix the issue that the length of the table name is not checked when renaming a table [#13345](https://github.com/pingcap/tidb/pull/13345)
    - Check the width range of the `BIT` column [#13511](https://github.com/pingcap/tidb/pull/13511)
    - Make the error information output from `change/modify column` more understandable [#13798](https://github.com/pingcap/tidb/pull/13798)
    - Fix the issue that when executing the `drop column` operation that has not yet been handled by the downstream Drainer, the downstream might receive DML operations without the affected column [#13974](https://github.com/pingcap/tidb/pull/13974)
