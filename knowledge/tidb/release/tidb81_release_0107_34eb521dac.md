# Bug fixes for TiDB and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.14.md`
- Source Title: `TiDB 3.0.14 Release Notes`
- Source Heading Path: `TiDB 3.0.14 Release Notes > Bug Fixes`
- Source Line Ranges: `66-113`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`
- Topic Tags: `release-notes`, `bug-fixes`, `mysql-compatibility`, `drop-index`, `statement-summary`, `plan-cache`, `functions`, `mergejoin`, `privilege-check`, `load-data`, `partition-pruning`, `concurrent-ddl`, `views`, `time-parsing`, `collation`, `stalecommand`, `audit-plugin`, `fast-analyze`, `processlist`, `oom`, `partitions`, `mvcc`, `union`, `indexlookupjoin`, `only-full-group-by`, `isolation-recovery`, `data-loss`, `learner`, `raw-kv`, `raft`, `grpc`, `region-merge`, `transactions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0107_34eb521dac`
- Source ID: `tidb-docs-8.1:releases/release-3.0.14.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2b9f3bd8f2bb6a0adba976849a288ea684b62ec889496450e65b7f08a7ea9c8c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.14#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.14.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the detailed TiDB 3.0.14 bug fixes for SQL compatibility, planner behavior, views, partitions, processlist, MVCC HTTP API, and TiKV reliability issues.
- Retrieval Keywords: TiDB 3.0.14 Bug Fixes, WEEKEND ALLOW_INVALID_DATES, DROP INDEX auto-increment primary key, Statement Summary TABLE_NAMES, plan cache incorrect results, not istrue isfalse incorrect result, MergeJoin redundant indexes panic, CURRENT_ROLE SET ROLE, LOAD DATA encounters \\, database visibility incompatible with MySQL, SET DEFAULT ROLE ALL privilege check, partition pruning failure caused by the plan cache, schema change during transaction commit concurrent DDL, Unknown column using a view not in the current schema, parsing time strings incompatible with MySQL, StaleCommand no error message returned, audit plugin port probing panic, fast analyze indices only panic, SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST panic, TiDB OOM large number of partitions, information_schema.tidb_hot_table partitioned tables, MVCC HTTP API partitioned tables, UNION error handling consistent with SELECT, IndexLookupJoin incorrect range, only_full_group_by brackets, view_name.col_name from view_name, TiKV isolation recovery, Region Merge data loss during network isolation, learner cannot be removed correctly, raw key-value pairs out of order, Raft messages too large reconnection, gRPC thread deadlock empty request, cleanup of lock atomicity of the transaction
- Follow-up Guidance: The chunk separates bug fixes into TiDB and TiKV lists, so retrieval can be narrowed further by component-specific identifiers such as `Statement Summary`, `INFORMATION_SCHEMA.PROCESSLIST`, `MVCC`, `Region Merge`, or `StaleCommand`.
- Classification Note: The official content is classified as bug fixes because every item describes a corrected failure, panic, incompatibility, or reliability problem in TiDB or TiKV.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix the issue that `WEEKEND` function is not compatible with MySQL when the SQL mode is `ALLOW_INVALID_DATES` [#16170](https://github.com/pingcap/tidb/pull/16170)
    - Fix the issue that the `DROP INDEX` statement fails to execute when the index column contains the auto-increment primary key [#16008](https://github.com/pingcap/tidb/pull/16008)
    - Fix the issue of incorrect values of the `TABLE_NAMES` column in the Statement Summary [#15231](https://github.com/pingcap/tidb/pull/15231)
    - Fix the issue that some expressions have incorrect results when the plan cache is enabled [#16184](https://github.com/pingcap/tidb/pull/16184)
    - Fix the issue that the result of the `not`/`istrue`/`isfalse` function is incorrect [#15916](https://github.com/pingcap/tidb/pull/15916)
    - Fix the panic caused by the `MergeJoin` operation on tables with redundant indexes [#15919](https://github.com/pingcap/tidb/pull/15919)
    - Fix the issue caused by incorrectly simplifying the link when the predicate only refers to the outer table [#16492](https://github.com/pingcap/tidb/pull/16492)
    - Fix the issue that the `CURRENT_ROLE` function reports an error caused by the `SET ROLE` statement [#15569](https://github.com/pingcap/tidb/pull/15569)
    - Fix the issue that the result of the `LOAD DATA` statement is incompatible with MySQL when this statement encounters `\` [#16633](https://github.com/pingcap/tidb/pull/16633)
    - Fix the issue that the database visibility is incompatible with MySQL [#14939](https://github.com/pingcap/tidb/pull/14939)
    - Fix the issue of incorrect privilege check for the `SET DEFAULT ROLE ALL` statement [#15585](https://github.com/pingcap/tidb/pull/15585)
    - Fix the issue of partition pruning failure caused by the plan cache [#15818](https://github.com/pingcap/tidb/pull/15818)
    - Fix the issue that `schema change` is reported during the transaction commit when concurrent DDL operations are performed on a table and blocking exists, because the transaction does not lock the related table [#15707](https://github.com/pingcap/tidb/pull/15707)
    - Fix the incorrect behavior of `IF(not_int, *, *)` [#15356](https://github.com/pingcap/tidb/pull/15356)
    - Fix the incorrect behavior of `CASE WHEN (not_int)` [#15359](https://github.com/pingcap/tidb/pull/15359)
    - Fix the issue that the `Unknown column` error message is returned when using a `view` that is not in the current schema [#15866](https://github.com/pingcap/tidb/pull/15866)
    - Fix the issue that the result of parsing time strings is incompatible with MySQL [#16242](https://github.com/pingcap/tidb/pull/16242)
    - Fix the possible panic of the collation operator in `left join` when a `null` column exists in the right child node [#16528](https://github.com/pingcap/tidb/pull/16528)
    - Fix the issue that no error message is returned even though the SQL execution is blocked when TiKV keeps returning the `StaleCommand` error message [#16528](https://github.com/pingcap/tidb/pull/16528)
    - Fix the possible panic caused by the port probing when the audit plugin is enabled [#15967](https://github.com/pingcap/tidb/pull/15967)
    - Fix the panic caused when `fast analyze` works on indices only [#15967](https://github.com/pingcap/tidb/pull/15967)
    - Fix the possible panic of the `SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST` statement execution in some cases [#16309](https://github.com/pingcap/tidb/pull/16309)
    - Fix the issue of TiDB OOM caused by specifying a large number of partitions (for example, `9999999999999`) when the hash partition table is created without checking the number of partitions before allocating memory [#16218](https://github.com/pingcap/tidb/pull/16218)
    - Fix the issue of incorrect information of partitioned tables in `information_schema.tidb_hot_table` [#16726](https://github.com/pingcap/tidb/pull/16726)
    - Fix the issue that the partition selection algorithm does not take effect on the hash partitioned table [#16070](https://github.com/pingcap/tidb/pull/16070)
    - Fix the issue that the HTTP API of the MVCC series does not support partitioned tables [#16191](https://github.com/pingcap/tidb/pull/16191)
    - Keep the error handling of the `UNION` statement consistent with that of the `SELECT` statement [#16137](https://github.com/pingcap/tidb/pull/16137)
    - Fix the issue of incorrect behavior when the parameter type of the `VALUES` function is `bit(n)` [#15486](https://github.com/pingcap/tidb/pull/15486)
    - Fix the issue that the processing logic of TiDB is inconsistent with MySQL when the `view` column name is too long. In this case, the system automatically generates a short column name. [#14873](https://github.com/pingcap/tidb/pull/14873 )
    - Fix the issue that `(not not col)` is incorrectly optimized as `col` [#16094](https://github.com/pingcap/tidb/pull/16094)
    - Fix the issue of incorrect `range` of the inner table built by `IndexLookupJoin` plans [#15753](https://github.com/pingcap/tidb/pull/15753)
    - Fix the issue that `only_full_group_by` fails to correctly check expressions with brackets [#16012](https://github.com/pingcap/tidb/pull/16012)
    - Fix the issue that an error is returned when the `select view_name.col_name from view_name` statement is executed [#15572](https://github.com/pingcap/tidb/pull/15572)

+ TiKV

    - Fix the issue that the node cannot be deleted correctly after the isolation recovery in some cases [#7703](https://github.com/tikv/tikv/pull/7703)
    - Fix the issue of data loss during network isolation caused by the Region Merge operation [#7679](https://github.com/tikv/tikv/pull/7679)
    - Fix the issue that learner cannot be removed correctly in some cases [#7598](https://github.com/tikv/tikv/pull/7598)
    - Fix the issue that the scanning result of raw key-value pairs might be out of order [#7597](https://github.com/tikv/tikv/pull/7597)
    - Fix the issue of reconnection when the batch of Raft messages is too large [#7542](https://github.com/tikv/tikv/pull/7542)
    - Fix the issue of gRPC thread deadlock caused by the empty request [#7538](https://github.com/tikv/tikv/pull/7538)
    - Fix the issue that the processing logic of restarting the learner is incorrect during the merge process [#7457](https://github.com/tikv/tikv/pull/7457)
    - Fix the issue that repeated requests on the cleanup of lock might destroy the atomicity of the transaction [#7388](https://github.com/tikv/tikv/pull/7388)
