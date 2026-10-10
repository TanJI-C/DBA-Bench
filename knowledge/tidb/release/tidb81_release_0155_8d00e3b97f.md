# Bug fixes for TiDB in RC.2

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.0-rc.2.md`
- Source Title: `TiDB 4.0 RC.2 Release Notes`
- Source Heading Path: `TiDB 4.0 RC.2 Release Notes > Bug Fixes`
- Source Line Ranges: `109-152`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`, `dashboard`
- Topic Tags: `bug-fixes`, `sql`, `planner`, `indexmerge`, `sequence`, `statement-summary`, `collation`, `plan-cache`, `gc`, `slow-log`, `grafana`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0155_8d00e3b97f`
- Source ID: `tidb-docs-8.1:releases/release-4.0.0-rc.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0f477d6cef870841f7683f0df3fa3947d6c25ef612c8b33e3aec447afe2f4b2c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.0-rc.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.0-rc.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB RC.2 bug fixes about SQL execution, planner hints, statement summary, plan cache, slow log, collation, GC, or Grafana display issues.
- Retrieval Keywords: TiDB 4.0 RC.2 Release Notes, Bug Fixes, IndexMerge hint, Statement Summary table, Plan Cache, @@LAST_PLAN_FROM_CACHE, SLOW_QUERY table, SELECT FOR UPDATE, green GC, Grafana TiDB Summary dashboard
- Follow-up Guidance: Review the listed pull requests for the exact fixes and affected components.
- Classification Note: This is the TiDB section of RC.2 bug fixes, covering SQL behavior, optimizer hints, logs, GC, and dashboard presentation issues.

## Official Source Content

## Bug Fixes

+ TiDB

    - Improve the logic that determines whether to use vectorization for expression execution in multiple operators [#16383](https://github.com/pingcap/tidb/pull/16383)
    - Fix the issue that the `IndexMerge` hint fails to check the database name correctly [#16932](https://github.com/pingcap/tidb/pull/16932)
    - Forbid truncating the sequence object [#17037](https://github.com/pingcap/tidb/pull/17037)
    - Fix the issue that the `INSERT`/`UPDATE`/`ANALYZE`/`DELETE` statements can be performed on a sequence object [#16957](https://github.com/pingcap/tidb/pull/16957)
    - Fix the issue that the internal SQL statements in the bootstrap phase are not correctly marked as internal queries in the Statement Summary table [#17062](https://github.com/pingcap/tidb/pull/17062)
    - Fix the error that occurs when a filter condition supported by TiFlash but not by TiKV is pushed down to the `IndexLookupJoin` operator [#17036](https://github.com/pingcap/tidb/pull/17036)
    - Fix the concurrency issue of the `LIKE` expression that might occur after the collation is enabled [#16997](https://github.com/pingcap/tidb/pull/16997)
    - Fix the issue that the `LIKE` function cannot correctly build the `Range` query index after the collation is enabled [#16783](https://github.com/pingcap/tidb/pull/16783)
    - Fix the issue that a wrong value is returned when executing `@@LAST_PLAN_FROM_CACHE` after the `Plan Cache` statement is triggered [#16831](https://github.com/pingcap/tidb/pull/16831)
    - Fix the issue that `TableFilter` on the index is missed when calculating candidate paths for `IndexMerge` [#16947](https://github.com/pingcap/tidb/pull/16947)
    - Fix the issue that a physical query plan cannot be generated when using the `MergeJoin` hint and the `TableDual` operator exists [#17016](https://github.com/pingcap/tidb/pull/17016)
    - Fix the wrong capitalization of the values in the `Stmt_Type` column of the Statement Summary table [#17018](https://github.com/pingcap/tidb/pull/17018)
    - Fix the issue that the `Permission Denied` error is reported because the service cannot be started when different users use the same `tmp-storage-path` [#16996](https://github.com/pingcap/tidb/pull/16996)
    - Fix the issue that the `NotNullFlag` result type is incorrectly set for an expression whose result type is determined by multiple input columns, such as `CASE WHEN` [#16995](https://github.com/pingcap/tidb/pull/16995)
    - Fix the issue that the green GC might leave unresolved locks when dirty stores exist [#16949](https://github.com/pingcap/tidb/pull/16949)
    - Fix the issue that the green GC might leave unresolved locks when encountering a single key with multiple different locks [#16948](https://github.com/pingcap/tidb/pull/16948)
    - Fix the issue of inserting a wrong value in the `INSERT VALUE` statement because a sub-query refers to a parent query column [#16952](https://github.com/pingcap/tidb/pull/16952)
    - Fix the issue of incorrect results when using the `AND` operator on the `Float` value [#16666](https://github.com/pingcap/tidb/pull/16666)
    - Fix the wrong information of the `WAIT_TIME` field in the expensive log [#16907](https://github.com/pingcap/tidb/pull/16907)
    - Fix the issue that the `SELECT FOR UPDATE` statement cannot be recorded in the slow log in the pessimistic transaction mode [#16897](https://github.com/pingcap/tidb/pull/16897)
    - Fix the wrong result that occurs when executing `SELECT DISTINCT` on a column of the `Enum` or `Set` type [#16892](https://github.com/pingcap/tidb/pull/16892)
    - Fix the display error of `auto_random_base` in the `SHOW CREATE TABLE` statement [#16864](https://github.com/pingcap/tidb/pull/16864)
    - Fix the incorrect value of `string_value` in the `WHERE` clause [#16559](https://github.com/pingcap/tidb/pull/16559)
    - Fix the issue that the error message of the `GROUP BY` window function is inconsistent with that of MySQL [#16165](https://github.com/pingcap/tidb/pull/16165)
    - Fix the issue that the `FLASH TABLE` statement fails to execute when the database name contains the uppercase letter [#17167](https://github.com/pingcap/tidb/pull/17167)
    - Fix the inaccurate memory tracing of the Projection executor [#17118](https://github.com/pingcap/tidb/pull/17118)
    - Fix the issue of incorrect time filtering of the `SLOW_QUERY` table in different time zones [#17164](https://github.com/pingcap/tidb/pull/17164)
    - Fix the panic issue that occurs when `IndexMerge` is used with the virtual generated column [#17126](https://github.com/pingcap/tidb/pull/17126)
    - Fix the capitalization issue of the `INSTR` and `LOCATE` function [#17068](https://github.com/pingcap/tidb/pull/17068)
    - Fix the issue that the `tikv server timeout` error is reported frequently after the `tidb_allow_batch_cop` configuration is enabled [#17161](https://github.com/pingcap/tidb/pull/17161)
    - Fix the issue that the result of performing `XOR` operation on the Float type is inconsistent with that of MySQL 8.0 [#16978](https://github.com/pingcap/tidb/pull/16978)
    - Fix the issue that no error is reported when the unsupported `ALTER TABLE REORGANIZE PARTITION` statement is executed [#17178](https://github.com/pingcap/tidb/pull/17178)
    - Fix the issue that an error is reported when `EXPLAIN FORMAT="dot"  FOR CONNECTION ID` encounters an unsupported plan [#17160](https://github.com/pingcap/tidb/pull/17160)
    - Fix the record issue of the prepared statement in the `EXEC_COUNT` column of the Statement Summary table [#17086](https://github.com/pingcap/tidb/pull/17086)
    - Fix the issue that the value is not validated when setting the Statement Summary system variable [#17129](https://github.com/pingcap/tidb/pull/17129)
    - Fix the issue that an error is reported if an overflow value is used to query the `UNSIGNED BIGINT` primary key when the plan cache is enabled [#17120](https://github.com/pingcap/tidb/pull/17120)
    - Fix the incorrect QPS display by the machine instance and request type on the Grafana **TiDB Summary** dashboard [#17105](https://github.com/pingcap/tidb/pull/17105)

+ TiKV
