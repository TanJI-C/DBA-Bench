# TiDB 3.0.1 release notes and TiDB changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.1.md`
- Source Title: `TiDB 3.0.1 Release Notes`
- Source Heading Path: `TiDB 3.0.1 Release Notes | TiDB 3.0.1 Release Notes > TiDB`
- Source Line Ranges: `5-51`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `pd`, `tikv`
- Topic Tags: `release-notes`, `sql-features`, `session-variables`, `region-split`, `auto-increment`, `plugins`, `audit`, `plan-cache`, `generated-columns`, `arm64`, `collation`, `bug-fixes`, `processlist`, `fast-analyze`, `pessimistic-locking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0098_95f9edeaa4`
- Source ID: `tidb-docs-8.1:releases/release-3.0.1.md#tidb-3-0-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b18c3e939d8b925896dd8f5c3ebe1a99844db20b60f1bcaa8ac6e84d8c58343c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.1#tidb-3-0-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.0.1 release-note details about new SQL features, session variables, plugin management, generated column restrictions, ARM64 support, collation changes, or specific TiDB bug fixes and pessimistic locking changes.
- Retrieval Keywords: TiDB 3.0.1 Release Notes, MAX_EXECUTION_TIME, tidb_wait_split_region_finish_backoff, ADMIN PLUGINS ENABLE, ADMIN PLUGINS DISABLE, Audit plugin session connection information, Prepare Plan Cache window functions, stored generated columns, virtual generated columns, ARM64 architecture, modify collation UTF-8 utf8mb4, SHOW PROCESSLIST, FAST ANALYZE, FLUSH PRIVILEGES, skip-grant-table, oom-action="cancel", UPDATE … SELECT, INSERT … ON DUPLICATE, SELECT … FOR UPDATE, pessimistic locking
- Follow-up Guidance: The chunk also includes multiple TiDB 3.0.1 fixes for query correctness, memory usage reporting, DDL panic, TiKV client connectivity, and experimental pessimistic locking behavior.
- Classification Note: This is classified as a TiDB release-notes chunk because the official content lists TiDB 3.0.1 feature additions, behavior changes, and bug fixes under the TiDB section.

## Official Source Content

# TiDB 3.0.1 Release Notes

Release date: July 16, 2019

TiDB version: 3.0.1

TiDB Ansible version: 3.0.1
## TiDB

+ Add support for the `MAX_EXECUTION_TIME` feature [#11026](https://github.com/pingcap/tidb/pull/11026)
+ Add the `tidb_wait_split_region_finish_backoff` session variable to control the backoff time of splitting Regions [#11166](https://github.com/pingcap/tidb/pull/11166)
+ Support automatically adjusting the incremental gap allocated by auto-increment IDs based on the load, and the auto-adjustment scope of the incremental gap is 1000~2000000 [#11006](https://github.com/pingcap/tidb/pull/11006)
+ Add the `ADMIN PLUGINS ENABLE`/`ADMIN PLUGINS DISABLE` SQL statement to dynamically enable or disable plugins [#11157](https://github.com/pingcap/tidb/pull/11157)
+ Add the session connection information in the Audit plugin [#11013](https://github.com/pingcap/tidb/pull/11013)
+ Change the default behavior during the period of splitting Regions to wait for PD to finish scheduling [#11166](https://github.com/pingcap/tidb/pull/11166)
+ Prohibit Window Functions from being cached in Prepare Plan Cache to avoid incorrect results in some cases [#11048](https://github.com/pingcap/tidb/pull/11048)
+ Prohibit `ALTER` statements from modifying the definition of stored generated columns [#11068](https://github.com/pingcap/tidb/pull/11068)
+ Disallow changing virtual generated columns to stored generated columns [#11068](https://github.com/pingcap/tidb/pull/11068)
+ Disallow changing the generated column expression with indexes [#11068](https://github.com/pingcap/tidb/pull/11068)
+ Support compiling TiDB on the ARM64 architecture [#11150](https://github.com/pingcap/tidb/pull/11150)
+ Support modifying the collation of a database or a table, but the character set of the database/table has to be UTF-8 or utf8mb4 [#11086](https://github.com/pingcap/tidb/pull/11086)
+ Fix the issue that an error is reported when the `SELECT` subquery in the `UPDATE … SELECT` statement fails to parse the column in the `UPDATE` expression and the column is wrongly pruned [#11252](https://github.com/pingcap/tidb/pull/11252)
+ Fix the panic issue that happens when a column is queried on multiple times and the returned result is NULL during point queries [#11226](https://github.com/pingcap/tidb/pull/11226)
+ Fix the data race issue caused by non-thread safe `rand.Rand` when using the `RAND` function [#11169](https://github.com/pingcap/tidb/pull/11169)
+ Fix the bug that the memory usage of a SQL statement exceeds the threshold but the execution of this statement is not canceled in some cases when `oom-action="cancel"` is configured, and the returned result is incorrect [#11004](https://github.com/pingcap/tidb/pull/11004)
+ Fix the issue that `SHOW PROCESSLIST` shows that the memory usage is not `0` because the memory usage of MemTracker was not correctly cleaned [#10970](https://github.com/pingcap/tidb/pull/10970)
+ Fix the bug that the result of comparing integers and non-integers is not correct in some cases [#11194](https://github.com/pingcap/tidb/pull/11194)
+ Fix the bug that the query result is not correct when the query on table partitions contains a predicate in explicit transactions [#11196](https://github.com/pingcap/tidb/pull/11196)
+ Fix the DDL job panic issue because `infoHandle` might be `NULL` [#11022](https://github.com/pingcap/tidb/pull/11022)
+ Fix the issue that the query result is not correct because the queried column is not referenced in the subquery and is then wrongly pruned when running a nested aggregation query [#11020](https://github.com/pingcap/tidb/pull/11020)
+ Fix the issue that the `Sleep` function does not respond to the `KILL` statement in time [#11028](https://github.com/pingcap/tidb/pull/11028)
+ Fix the issue that the `DB` and `INFO` columns shown by the `SHOW PROCESSLIST` command are incompatible with MySQL [#11003](https://github.com/pingcap/tidb/pull/11003)
+ Fix the system panic issue caused by the `FLUSH PRIVILEGES` statement when `skip-grant-table=true` is configured [#11027](https://github.com/pingcap/tidb/pull/11027)
+ Fix the issue that the primary key statistics collected by `FAST ANALYZE` are not correct when the table primary key is an `UNSIGNED` integer [#11099](https://github.com/pingcap/tidb/pull/11099)
+ Fix the issue that the "invalid key" error is reported by the `FAST ANALYZE` statement in some cases [#11098](https://github.com/pingcap/tidb/pull/11098)
+ Fix the issue that the precision shown by the `SHOW CREATE TABLE` statement is incomplete when `CURRENT_TIMESTAMP` is used as the default value of the column and the float precision is specified [#11088](https://github.com/pingcap/tidb/pull/11088)
+ Fix the issue that the function name is not in lowercase when window functions report an error to make it compatible with MySQL [#11118](https://github.com/pingcap/tidb/pull/11118)
+ Fix the issue that TiDB fails to connect to TiKV and thus cannot provide service after the background thread of TiKV Client Batch gRPC panics [#11101](https://github.com/pingcap/tidb/pull/11101)
+ Fix the issue that the variable is set incorrectly by `SetVar` because of the shallow copy of the string [#11044](https://github.com/pingcap/tidb/pull/11044)
+ Fix the issue that the execution fails and an error is reported when the `INSERT … ON DUPLICATE` statement is applied on table partitions [#11231](https://github.com/pingcap/tidb/pull/11231)
+ Pessimistic locking (experimental feature)
    - Fix the issue that an incorrect result is returned because of the invalid lock on the row when point queries are run using the pessimistic locking and the returned data is empty [#10976](https://github.com/pingcap/tidb/pull/10976)
    - Fix the issue that the query result is not correct because `SELECT … FOR UPDATE` does not use the correct TSO when using the pessimistic locking in the query [#11015](https://github.com/pingcap/tidb/pull/11015)
    - Change the detection behavior from immediate conflict detection to waiting when an optimistic transaction meets a pessimistic lock to avoid worsening the lock conflict [#11051](https://github.com/pingcap/tidb/pull/11051)
