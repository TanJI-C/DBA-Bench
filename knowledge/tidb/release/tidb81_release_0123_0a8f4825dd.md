# TiDB 3.0.5 release overview and TiDB changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.5.md`
- Source Title: `TiDB 3.0.5 Release Notes`
- Source Heading Path: `TiDB 3.0.5 Release Notes | TiDB 3.0.5 Release Notes > TiDB`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`, `tikv`
- Topic Tags: `release-notes`, `sql-optimizer`, `sql-execution`, `server`, `ddl`, `monitoring`, `window-functions`, `pessimistic-transactions`, `slow-log`, `partitioned-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0123_0a8f4825dd`
- Source ID: `tidb-docs-8.1:releases/release-3.0.5.md#tidb-3-0-5-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cd32fe51b05736aff0ebe5efa7ee95721188862c1f7673367f32920c5793effc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.5#tidb-3-0-5-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.5.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 3.0.5 release-note details about SQL optimizer, SQL execution engine, server, DDL, or monitor changes and fixes.
- Retrieval Keywords: TiDB 3.0.5 Release Notes, TiDB 3.0.5, SQL Optimizer, SQL Execution Engine, Server, DDL, Monitor, Window Functions, IndexJoin, partition table, ifnull, outer join Apply, UPDATE subquery where condition, AntiSemiJoin, str_to_date, from_unixtime, invalid list index, AutoIncrement, getGeneratedKeys(), HashAgg, transaction TTL, pessimistic transactions, tidb_max_delta_schema_count, kvrpc.Cleanup, information_schema.tables, region-cache-ttl, slow-log-plan, tidb_record_plan_in_slow_log, tidb_decode_plan, information_schema.processlist, INSERT IGNORE, BatchGet(), Add Index, Transaction OPS
- Follow-up Guidance: The source also includes TiKV, PD, Tools, and TiDB Ansible changes in the same 3.0.5 release notes.
- Classification Note: This chunk is classified as a TiDB release-notes section because the official content lists TiDB 3.0.5 changes across optimizer, execution, server, DDL, and monitoring areas.

## Official Source Content

# TiDB 3.0.5 Release Notes

Release date: October 25, 2019

TiDB version: 3.0.5

TiDB Ansible version: 3.0.5
## TiDB

+ SQL Optimizer
    - Support boundary checking on Window Functions [#12404](https://github.com/pingcap/tidb/pull/12404)
    - Fix the issue that `IndexJoin` on the partition table returns incorrect results [#12712](https://github.com/pingcap/tidb/pull/12712)
    - Fix the issue that the `ifnull` function on the top of the outer join `Apply` operator returns incorrect results [#12694](https://github.com/pingcap/tidb/pull/12694)
    - Fix the issue of update failure when a subquery was included in the `where` condition of `UPDATE` [#12597](https://github.com/pingcap/tidb/pull/12597)
    - Fix the issue that outer join was incorrectly converted to inner join when the `cast` function was included in the query conditions [#12790](https://github.com/pingcap/tidb/pull/12790)
    - Fix incorrect expression passing in the join condition of `AntiSemiJoin` [#12799](https://github.com/pingcap/tidb/pull/12799)
    - Fix the statistics error caused by shallow copy when initializing statistics [#12817](https://github.com/pingcap/tidb/pull/12817)
    - Fix the issue that the `str_to_date` function in TiDB returns a different result from MySQL when the date string and the format string do not match [#12725](https://github.com/pingcap/tidb/pull/12725)
+ SQL Execution Engine
    - Fix the panic issue when the `from_unixtime` function handles null [#12551](https://github.com/pingcap/tidb/pull/12551)
    - Fix the `invalid list index` error reported when canceling DDL jobs [#12671](https://github.com/pingcap/tidb/pull/12671)
    - Fix the issue that arrays were out of bounds when Window Functions are used [#12660](https://github.com/pingcap/tidb/pull/12660)
    - Improve the behavior of the `AutoIncrement` column when it is implicitly allocated, to keep it consistent with the default mode of MySQL auto-increment locking (["consecutive" lock mode](https://dev.mysql.com/doc/refman/5.7/en/innodb-auto-increment-handling.html)): for the implicit allocation of multiple `AutoIncrement` IDs in a single-line `Insert` statement, TiDB guarantees the continuity of the allocated values. This improvement ensures that the JDBC `getGeneratedKeys()` method will get the correct results in any scenario. [#12602](https://github.com/pingcap/tidb/pull/12602)
    - Fix the issue that the query is hanged when `HashAgg` serves as a child node of `Apply` [#12766](https://github.com/pingcap/tidb/pull/12766)
    - Fix the issue that the `AND` and `OR` logical expressions return incorrect results when it comes to type conversion [#12811](https://github.com/pingcap/tidb/pull/12811)
+ Server
    - Implement the interface function that modifies transaction TTL to help support large transactions later [#12397](https://github.com/pingcap/tidb/pull/12397)
    - Support extending the transaction TTL as needed (up to 10 minutes) to support pessimistic transactions [#12579](https://github.com/pingcap/tidb/pull/12579)
    - Adjust the number of times that TiDB caches schema changes and corresponding changed table information from 100 to 1024, and support modification by using the `tidb_max_delta_schema_count` system variable [#12502](https://github.com/pingcap/tidb/pull/12502)
    - Update the behavior of the `kvrpc.Cleanup` protocol to no longer clean locks of transactions that are not overtime [#12417](https://github.com/pingcap/tidb/pull/12417)
    - Support logging Partition table information to the `information_schema.tables` table [#12631](https://github.com/pingcap/tidb/pull/12631)
    - Support modifying the TTL of Region Cache by configuring `region-cache-ttl` [#12683](https://github.com/pingcap/tidb/pull/12683)
    - Support printing the execution plan compression-encoded information in the slow log. This feature is enabled by default and can be controlled by using the `slow-log-plan` configuration or the `tidb_record_plan_in_slow_log` variable. In addition, the `tidb_decode_plan` function can decode the execution plan column encoded information in the slow log into execution plan information. [#12808](https://github.com/pingcap/tidb/pull/12808)
    - Support displaying memory usage information in the `information_schema.processlist` table [#12801](https://github.com/pingcap/tidb/pull/12801)
    - Fix the issue that an error and an unexpected alarm might occur when the TiKV Client judges an idle connection [#12846](https://github.com/pingcap/tidb/pull/12846)
    - Fix the issue that the `INSERT IGNORE` statement performance is decreased because `tikvSnapshot` does not properly cache the KV results of `BatchGet()` [#12872](https://github.com/pingcap/tidb/pull/12872)
    - Fix the issue that the TiDB response speed was relatively low because of slow connection to some KV services [#12814](https://github.com/pingcap/tidb/pull/12814)
+ DDL
    - Fix the issue that the `Create Table` operation does not correctly set the Int type default value for the Set column [#12267](https://github.com/pingcap/tidb/pull/12267)
    - Support multiple `unique`s when creating a unique index in the `Create Table` statement [#12463](https://github.com/pingcap/tidb/pull/12463)
    - Fix the issue that populating the default value of this column for existing rows might cause an error when adding a Bit type column using `Alter Table` [#12489](https://github.com/pingcap/tidb/pull/12489)
    - Fix the failure of adding a partition when the Range partitioned table uses a Date or Datetime type column as the partitioning key [#12815](https://github.com/pingcap/tidb/pull/12815)
    - Support checking the consistency of the partition type and the partition key type when creating a table or adding a partition, for the Range partitioned table with the Date or Datetime type column as the partition key [#12792](https://github.com/pingcap/tidb/pull/12792)
    - Add a check that the Unique Key column set needs to be greater than or equal to the partitioned column set when creating a Range partitioned table [#12718](https://github.com/pingcap/tidb/pull/12718)
+ Monitor
    - Add the monitoring metrics of Commit and Rollback operations to the `Transaction OPS` dashboard [#12505](https://github.com/pingcap/tidb/pull/12505)
    - Add the monitoring metrics of `Add Index` operation progress [#12390](https://github.com/pingcap/tidb/pull/12390)
