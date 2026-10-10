# TiDB 5.2.4 TiDB bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.2.4.md`
- Source Title: `TiDB 5.2.4 Release Notes`
- Source Heading Path: `TiDB 5.2.4 Release Notes > Bug fixes`
- Source Line Ranges: `56-99`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`
- Topic Tags: `release-notes`, `bug-fixes`, `sql`, `joins`, `window-functions`, `enum`, `set`, `logging`, `slow-query-log`, `partitioned-tables`, `transactions`, `tiflash`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0248_817dcd27b5`
- Source ID: `tidb-docs-8.1:releases/release-5.2.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b657be3ed378eb33c83692240c6002f3324f0fefe434ec74ec66b136283a6426`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.2.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.2.4.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 5.2.4 bug fixes for SQL wrong results, join and window-function issues, ENUM or SET handling, slow query log problems, partitioned-table index usage, or TiFlash query errors.
- Retrieval Keywords: TiDB 5.2.4 bug fixes, INDEX HASH JOIN send on closed channel, Column 'col_name' in field list is ambiguous, natural join, NATURAL JOIN unexpected columns, window functions different results when using a transaction or not, window function causes TiDB to panic instead of reporting an error, GREATEST inconsistent results tidb_enable_vectorized_expression, microsecond function in vectorized expressions, Merge Join operator gets wrong results, correlated subquery returns a constant, wrong encoding of the ENUM or SET column, MAX or MIN on the ENUM or SET column, CASE WHEN function on the ENUM data type, JOIN on ENUM type columns, partitioned tables cannot fully use indexes to scan data, slow query log does not take effect on the slow query log, slow query log cannot output log normally and might consume too much memory, max_allowed_packet does not take effect, INSERT ... SELECT ... ON DUPLICATE KEY UPDATE panic, REPLACE statement incorrectly changes other rows, ORDER BY and LIMIT prefix-column index wrong results, TiDB may dispatch duplicate tasks to TiFlash, MPP task list empty error, TiFlash empty range
- Follow-up Guidance: The chunk groups many TiDB fixes, covering join operators, TiFlash execution, transaction behavior, logging, and SQL function correctness.
- Classification Note: The official content is classified as bug fixes because it enumerates resolved TiDB issues in 5.2.4, mostly involving incorrect query results, panics, logging problems, and execution errors.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix wrong range calculation results for Nulleq function on Enum values [#32428](https://github.com/pingcap/tidb/issues/32428)
    - Fix the issue that INDEX HASH JOIN returns the `send on closed channel` error [#31129](https://github.com/pingcap/tidb/issues/31129)
    - Fix the issue that concurrent column type change causes inconsistency between the schema and the data [#31048](https://github.com/pingcap/tidb/issues/31048)
    - Fix the issue of potential data index inconsistency in optimistic transaction mode [#30410](https://github.com/pingcap/tidb/issues/30410)
    - Fix the issue that a SQL operation is canceled when its JSON type column joins its `CHAR` type column [#29401](https://github.com/pingcap/tidb/issues/29401)
    - Fix the issue that window functions might return different results when using a transaction or not [#29947](https://github.com/pingcap/tidb/issues/29947)
    - Fix the issue that the `Column 'col_name' in field list is ambiguous` error is reported unexpectedly when a SQL statement contains natural join [#25041](https://github.com/pingcap/tidb/issues/25041)
    - Fix the issue that the length information is wrong when casting `Decimal` to `String` [#29417](https://github.com/pingcap/tidb/issues/29417)
    - Fix the issue that the `GREATEST` function returns inconsistent results due to different values of `tidb_enable_vectorized_expression` (set to `on` or `off`) [#29434](https://github.com/pingcap/tidb/issues/29434)
    - Fix wrong results of deleting data of multiple tables using `left join` [#31321](https://github.com/pingcap/tidb/issues/31321)
    - Fix a bug that TiDB may dispatch duplicate tasks to TiFlash [#32814](https://github.com/pingcap/tidb/issues/32814)
    - Fix the MPP task list empty error when executing a query [#31636](https://github.com/pingcap/tidb/issues/31636)
    - Fix wrong results of index join caused by an innerWorker panic [#31494](https://github.com/pingcap/tidb/issues/31494)
    - Fix the issue that executing the `INSERT ... SELECT ... ON DUPLICATE KEY UPDATE` statement gets panic [#28078](https://github.com/pingcap/tidb/issues/28078)
    - Fix wrong query results due to the optimization of `Order By` [#30271](https://github.com/pingcap/tidb/issues/30271)
    - Fix the wrong result that might occur when performing `JOIN` on `ENUM` type columns [#27831](https://github.com/pingcap/tidb/issues/27831)
    - Fix the panic when using the `CASE WHEN` function on the `ENUM` data type [#29357](https://github.com/pingcap/tidb/issues/29357)
    - Fix wrong results of the `microsecond` function in vectorized expressions [#29244](https://github.com/pingcap/tidb/issues/29244)
    - Fix the issue that the window function causes TiDB to panic instead of reporting an error [#30326](https://github.com/pingcap/tidb/issues/30326)
    - Fix the issue that the Merge Join operator gets wrong results in certain cases [#33042](https://github.com/pingcap/tidb/issues/33042)
    - Fix the issue that TiDB gets a wrong result when a correlated subquery returns a constant  [#32089](https://github.com/pingcap/tidb/issues/32089)
    - Fix the issue that TiDB writes wrong data due to the wrong encoding of the `ENUM` or `SET` column [#32302](https://github.com/pingcap/tidb/issues/32302)
    - Fix the issue that the `MAX` or `MIN` function on the `ENUM` or `SET` column returns a wrong result when the new collation is enabled in TiDB [#31638](https://github.com/pingcap/tidb/issues/31638)
    - Fix the issue that the IndexHashJoin operator does not exit successfully [#31062](https://github.com/pingcap/tidb/issues/31062)
    - Fix the issue that TiDB might read wrong data when a table has a virtual column [#30965](https://github.com/pingcap/tidb/issues/30965)
    - Fix the issue that the setting of the log level does not take effect on the slow query log [#30309](https://github.com/pingcap/tidb/issues/30309)
    - Fix the issue that partitioned tables cannot fully use indexes to scan data in some cases [#33966](https://github.com/pingcap/tidb/issues/33966)
    - Fix the issue that the background HTTP service of TiDB might not exit successfully and makes the cluster in an abnormal state [#30571](https://github.com/pingcap/tidb/issues/30571)
    - Fix the issue that TiDB might unexpectedly output many logs of failed authentication [#29709](https://github.com/pingcap/tidb/issues/29709)
    - Fix the issue that the system variable `max_allowed_packet` does not take effect [#31422](https://github.com/pingcap/tidb/issues/31422)
    - Fix the issue that the `REPLACE` statement incorrectly changes other rows when the auto ID is out of range [#29483](https://github.com/pingcap/tidb/issues/29483)
    - Fix the issue that the slow query log cannot output log normally and might consume too much memory [#32656](https://github.com/pingcap/tidb/issues/32656)
    - Fix the issue that the result of NATURAL JOIN might include unexpected columns [#29481](https://github.com/pingcap/tidb/issues/29481)
    - Fix the issue that using `ORDER BY` and `LIMIT` together in one statement might output wrong results if a prefix-column index is used to query data [#29711](https://github.com/pingcap/tidb/issues/29711)
    - Fix the issue that the DOUBLE type auto-increment column might be changed when the optimistic transaction retries [#29892](https://github.com/pingcap/tidb/issues/29892)
    - Fix the issue that the STR_TO_DATE function cannot handle the preceding zero of the microsecond part correctly [#30078](https://github.com/pingcap/tidb/issues/30078)
    - Fix the issue that TiDB gets the wrong result when using TiFlash to scan tables with empty range although TiFlash does not support reading tables with empty range yet [#33083](https://github.com/pingcap/tidb/issues/33083)

+ TiKV
