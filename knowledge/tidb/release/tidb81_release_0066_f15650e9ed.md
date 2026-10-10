# TiDB 2.1.18 release overview and TiDB fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.18.md`
- Source Title: `TiDB 2.1.18 Release Notes`
- Source Heading Path: `TiDB 2.1.18 Release Notes | TiDB 2.1.18 Release Notes > TiDB`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `release-notes`, `sql-optimizer`, `sql-engine`, `server`, `ddl`, `monitoring`, `bug-fixes`, `performance`, `system-variables`, `slow-query-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0066_f15650e9ed`
- Source ID: `tidb-docs-8.1:releases/release-2.1.18.md#tidb-2-1-18-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `10057d7d893e6a5aa3a1d6e58a7833a8d99de0cd476e841db9085d73bf22b36d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.18#tidb-2-1-18-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.18.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 2.1.18 release-note fixes or behavior changes for SQL Optimizer, SQL Engine, Server, DDL, Monitor, slow query logs, AutoIncrement, or related system variables.
- Retrieval Keywords: TiDB 2.1.18 Release Notes, SQL Optimizer, SQL Engine, Server, DDL, Monitor, invalid query ranges split by feedback, point get plan privilege check, select ... limit ... offset, IndexLookUpReader, parameters in ORDER BY GROUP BY LIMIT OFFSET, IndexJoin partition table incorrect results, str_to_date, outer join incorrectly converted to inner join, AntiSemiJoin, rounding of time, PREPARE statement monitoring record sql_type, from_unixtime handles null panic, YEAR type NULL instead of 0000, AutoIncrement getGeneratedKeys(), HashAgg child node of Apply, AND OR type conversion incorrect results, SLEEP(), KILL TIDB QUERY, slow query logs log level ERROR, tidb_max_delta_schema_count, set session autocommit, SessionVars, Prev_stmt, COMMIT fails in an explicitly committed transaction, FLUSH PRIVILEGES, skip-grant-table=true, COM_STMT_FETCH, write conflicts error code, tidb_allow_remove_auto_inc, ADMIN CANCEL DDL JOBS invalid list index, backoff monitoring, Add Index operation progress
- Follow-up Guidance: The content also points to the `tidb_allow_remove_auto_inc` system variable details in the System Variables documentation.
- Classification Note: This is a release-notes chunk for the TiDB component because it lists TiDB 2.1.18 fixes and changes across optimizer, engine, server, DDL, and monitoring.

## Official Source Content

# TiDB 2.1.18 Release Notes

Release date: November 4, 2019

TiDB version: 2.1.18

TiDB Ansible version: 2.1.18
## TiDB

+ SQL Optimizer
    - Fix the issue that invalid query ranges might appear when split by feedback [#12172](https://github.com/pingcap/tidb/pull/12172)
    - Fix the issue that the privilege check is incorrect in point get plan [#12341](https://github.com/pingcap/tidb/pull/12341)
    - Optimize execution performance of the `select ... limit ... offset …` statement by pushing the Limit operator down to the `IndexLookUpReader` execution logic [#12380](https://github.com/pingcap/tidb/pull/12380)
    - Support using parameters in `ORDER BY`, `GROUP BY` and `LIMIT OFFSET` [#12514](https://github.com/pingcap/tidb/pull/12514)
    - Fix the issue that `IndexJoin` on the partition table returns incorrect results [#12713](https://github.com/pingcap/tidb/pull/12713)
    - Fix the issue that the `str_to_date` function in TiDB returns a different result from MySQL when the date string and the format string do not match [#12757](https://github.com/pingcap/tidb/pull/12757)
    - Fix the issue that outer join is incorrectly converted to inner join when the `cast` function is included in the query conditions [#12791](https://github.com/pingcap/tidb/pull/12791)
    - Fix incorrect expression passing in the join condition of `AntiSemiJoin` [#12800](https://github.com/pingcap/tidb/pull/12800)
+ SQL Engine
    - Fix the incorrectly rounding of time (for example, `2019-09-11 11:17:47.999999666` should be rounded to `2019-09-11 11:17:48`) [#12259](https://github.com/pingcap/tidb/pull/12259)
    - Fix the issue that the duration by `sql_type` for the `PREPARE` statement is not shown in the monitoring record [#12329](https://github.com/pingcap/tidb/pull/12329)
    - Fix the panic issue when the `from_unixtime` function handles null [#12572](https://github.com/pingcap/tidb/pull/12572)
    - Fix the compatibility issue that when an invalid value is inserted as the `YEAR` type, the result is `NULL` instead of `0000` [#12744](https://github.com/pingcap/tidb/pull/12744)
    - Improve the behavior of the `AutoIncrement` column when it is implicitly allocated, to keep it consistent with the default mode of MySQL auto-increment locking (["consecutive" lock mode](https://dev.mysql.com/doc/refman/5.7/en/innodb-auto-increment-handling.html)): for the implicit allocation of multiple `AutoIncrement` IDs in a single-line `Insert` statement, TiDB guarantees the continuity of the allocated values. This improvement ensures that the JDBC `getGeneratedKeys()` method will get the correct results in any scenario [#12619](https://github.com/pingcap/tidb/pull/12619)
    - Fix the issue that the query is hanged when `HashAgg` serves as a child node of `Apply` [#12769](https://github.com/pingcap/tidb/pull/12769)
    - Fix the issue that the `AND` and `OR` logical expressions return incorrect results when it comes to type conversion [#12813](https://github.com/pingcap/tidb/pull/12813)
+ Server
    - Fix the issue that the `SLEEP()` function is invalid for the `KILL TIDB QUERY` statements [#12159](https://github.com/pingcap/tidb/pull/12159)
    - Fix the issue that no error is reported when `AUTO_INCREMENT` incorrectly allocates `MAX int64` and `MAX uint64` [#12210](https://github.com/pingcap/tidb/pull/12210)
    - Fix the issue that the slow query logs are not recorded when the log level is `ERROR` [#12373](https://github.com/pingcap/tidb/pull/12373)
    - Adjust the number of times that TiDB caches schema changes and corresponding changed table information from 100 to 1024, and support modification by using the `tidb_max_delta_schema_count` system variable [#12515](https://github.com/pingcap/tidb/pull/12515)
    - Change the query start time from the point of "starting to execute" to "starting to compile" to make SQL statistics more accurate [#12638](https://github.com/pingcap/tidb/pull/12638)
    - Add the record of `set session autocommit` in TiDB logs [#12568](https://github.com/pingcap/tidb/pull/12568)
    - Record SQL query start time in `SessionVars` to prevent it from being reset during plan execution [#12676](https://github.com/pingcap/tidb/pull/12676)
    - Support `?` placeholder in `ORDER BY`, `GROUP BY` and `LIMIT OFFSET` [#12514](https://github.com/pingcap/tidb/pull/12514)
    - Add the `Prev_stmt` field in slow query logs to output the previous statement when the last statement is `COMMIT` [#12724](https://github.com/pingcap/tidb/pull/12724)
    - Record the last statement before `COMMIT` into the log when the `COMMIT` fails in an explicitly committed transaction [#12747](https://github.com/pingcap/tidb/pull/12747)
    - Optimize the saving method of the previous statement when the TiDB server executes a SQL statement to improve performance [#12751](https://github.com/pingcap/tidb/pull/12751)
    - Fix the panic issue caused by `FLUSH PRIVILEGES` statements under the `skip-grant-table=true` configuration [#12816](https://github.com/pingcap/tidb/pull/12816)
    - Increase the default minimum step of applying AutoID from `1000` to `30000` to avoid performance bottleneck when there are many write requests in a short time [#12891](https://github.com/pingcap/tidb/pull/12891)
    - Fix the issue that the failed `Prepared` statement is not print in the error log when TiDB panics [#12954](https://github.com/pingcap/tidb/pull/12954)
    - Fix the issue that the `COM_STMT_FETCH` time record in slow query logs is inconsistent with that in MySQL [#12953](https://github.com/pingcap/tidb/pull/12953)
    - Add an error code in the error message for write conflicts to quickly locate the cause [#12878](https://github.com/pingcap/tidb/pull/12878)
+ DDL
    - Disallow dropping the `AUTO INCREMENT` attribute of a column by default. Modify the value of the `tidb_allow_remove_auto_inc` variable if you do need to drop this attribute. See [System Variables](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_remove_auto_inc-new-in-v2118-and-v304) for more details. [#12146](https://github.com/pingcap/tidb/pull/12146)
    - Support multiple `unique`s when creating a unique index in the `Create Table` statement [#12469](https://github.com/pingcap/tidb/pull/12469)
    - Fix a compatibility issue that if the foreign key constraint in `CREATE TABLE` statement has no schema, schema of the created table should be used instead of returning a `No Database selected` error [#12678](https://github.com/pingcap/tidb/pull/12678)
    - Fix the issue that the `invalid list index` error is reported when executing `ADMIN CANCEL DDL JOBS` [#12681](https://github.com/pingcap/tidb/pull/12681)
+ Monitor
    - Add types for backoff monitoring and supplement the backoff time that is not recorded before, such as the backoff time when committing [#12326](https://github.com/pingcap/tidb/pull/12326)
    - Add a new metric to monitor `Add Index` operation progress [#12389](https://github.com/pingcap/tidb/pull/12389)
