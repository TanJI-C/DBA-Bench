# TiDB query execution and data consistency troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-troubleshooting-map.md`
- Source Title: `TiDB Troubleshooting Map`
- Source Heading Path: `TiDB Troubleshooting Map > 3. TiDB issues > 3.3 Wrong execution plan | TiDB Troubleshooting Map > 3. TiDB issues > 3.4 SQL execution error | TiDB Troubleshooting Map > 3. TiDB issues > 3.5 Slow query issues | TiDB Troubleshooting Map > 3. TiDB issues > 3.6 Hotspot issues | TiDB Troubleshooting Map > 3. TiDB issues > 3.7 High disk I/O usage | TiDB Troubleshooting Map > 3. TiDB issues > 3.8 Lock conflicts | TiDB Troubleshooting Map > 3. TiDB issues > 3.9 Inconsistency between data and indexes`
- Source Line Ranges: `143-208`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `execution-plan`, `statistics`, `sql-errors`, `slow-queries`, `hotspot`, `disk-io`, `lock-conflicts`, `data-index-consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0108_bb459f2c3e`
- Source ID: `tidb-docs-8.1:tidb-troubleshooting-map.md#3-3-wrong-execution-plan`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `21d8915c947dd25b25b4c440efe127689f938a3030831078e8e8ba96b105e2e0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-troubleshooting-map#3-3-wrong-execution-plan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-troubleshooting-map.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiDB issues involving wrong execution plans, SQL execution errors, slow queries, hotspots, high disk I/O usage, lock conflicts, or inconsistency between data and indexes.
- Retrieval Keywords: wrong execution plan, explain analyze {SQL}, select count(*), TableScan, IndexScan, Scan Keys, Join Order, SQL Bind, show stats_meta, modify count/row count, analyze table, auto analyze, tidb_auto_analyze_ratio, tidb_auto_analyze_start_time, tidb_auto_analyze_end_time, ERROR 1265(01000) Data Truncated, Cast(xx as decimal(a, b)), Identify slow queries, Analyze slow queries, Troubleshoot Hotspot Issues, Troubleshoot High Disk I/O Usage, Troubleshoot Lock Conflicts, ADMIN CHECK TABLE, ADMIN CHECK INDEX, inconsistency between data and indexes, data inconsistency error
- Follow-up Guidance: The content points to dedicated documents for Identify slow queries, Analyze slow queries, Troubleshoot Hotspot Issues, Troubleshoot High Disk I/O Usage, Troubleshoot Lock Conflicts, and Troubleshoot Inconsistency Between Data and Indexes.
- Classification Note: This chunk is classified as diagnosis because the official content lists symptoms, investigation methods, and related troubleshooting paths for multiple TiDB query execution and consistency problems.

## Official Source Content

### 3.3 Wrong execution plan

- 3.3.1 Symptom

    - SQL query execution time is much longer compared with that of previous executions, or the execution plan suddenly changes. If the execution plan is logged in the slow log, you can directly compare the execution plans.

    - SQL query execution time is much longer compared with that of other databases such as MySQL. Compare the execution plan with other databases to see the differences, such as `Join Order`.

    - In slow log, the number of SQL execution time `Scan Keys` is large.

- 3.3.2 Investigate the execution plan

    - `explain analyze {SQL}`. When the execution time is acceptable, compare `count` in the result of `explain analyze` and the number of `row` in `execution info`. If a large difference is found in the `TableScan/IndexScan` row, it is likely that the statistics is incorrect. If a large difference is found in other rows, the problem might not be in the statistics.

    - `select count(*)`. When the execution plan contains a `join` operation, `explain analyze` might take a long time. You can check whether the problem is in the statistics by executing `select count(*)` for the conditions on `TableScan/IndexScan` and comparing the `row count` information in the `explain` result.

- 3.3.3 Mitigation

    - For v3.0 and later versions, use the `SQL Bind` feature to bind the execution plan.

    - Update the statistics. If you are roughly sure that the problem is caused by the statistics, [dump the statistics](https://docs.pingcap.com/tidb/stable/statistics#export-statistics). If the cause is outdated statistics, such as the `modify count/row count` in `show stats_meta` is greater than a certain value (for example, 0.3), or the table has an index of time column, you can try recovering by using `analyze table`. If `auto analyze` is configured, check whether the `tidb_auto_analyze_ratio` system variable is too large (for example, greater than 0.3), and whether the current time is between `tidb_auto_analyze_start_time` and `tidb_auto_analyze_end_time`.

    - For other situations, [report a bug](https://github.com/pingcap/tidb/issues/new?labels=type%2Fbug&template=bug-report.md).
### 3.4 SQL execution error

- 3.4.1 The client reports the `ERROR 1265(01000) Data Truncated` error. This is because the way TiDB internally calculates the precision of `Decimal` type is incompatible with that of MySQL. This issue has been fixed in v3.0.10 ([#14438](https://github.com/pingcap/tidb/pull/14438)).

    - Cause:

        In MySQL, if two large-precision `Decimal` are divided and the result exceeds the maximum decimal precision (`30`), only `30` digits are reserved and no error is reported;

        In TiDB, the calculation result is the same as in MySQL, but inside the data structure that represents `Decimal`, a field for decimal precision still retains the actual precision.

        Take `(0.1^30) / 10` as an example. The results in TiDB and MySQL are both `0`, because the precision is `30` at most. However, in TiDB, the field for decimal precision is still `31`.

        After multiple `Decimal` divisions, even though the result is correct, this precision field could grow larger and larger, and eventually exceeds the threshold in TiDB (`72`), and the `Data Truncated` error is reported.

        The multiplication of `Decimal` does not have this issue, because the out-of-bounds is bypassed, and the precision is set to the maximum precision limit.

    - Solution: You can bypass this issue by manually adding `Cast(xx as decimal(a, b))`, in which `a` and `b` are the target precisions.
### 3.5 Slow query issues

To identify slow queries, see [Identify slow queries](https://docs.pingcap.com/tidb/stable/identify-slow-queries). To analyze and handle slow queries, see [Analyze slow queries](https://docs.pingcap.com/tidb/stable/analyze-slow-queries).
### 3.6 Hotspot issues

As a distributed database, TiDB has a load balancing mechanism to distribute the application loads as evenly as possible to different computing or storage nodes, to make better use of server resources. However, in certain scenarios, some application loads cannot be well distributed, which can affect the performance and form a single point of high load, also known as a hotspot.

TiDB provides a complete solution to troubleshooting, resolving or avoiding hotspots. By balancing load hotspots, overall performance can be improved, including improving QPS and reducing latency. For detailed solutions, see [Troubleshoot Hotspot Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues).
### 3.7 High disk I/O usage

If TiDB's response slows down after you have troubleshot the CPU bottleneck and the bottleneck caused by transaction conflicts, you need to check I/O metrics to help determine the current system bottleneck. For how to locate and handle the issue of high I/O usage in TiDB, see [Troubleshoot High Disk I/O Usage](https://docs.pingcap.com/tidb/stable/troubleshoot-high-disk-io).
### 3.8 Lock conflicts

TiDB supports complete distributed transactions. Starting from v3.0, TiDB provides optimistic transaction mode and pessimistic transaction mode. To learn how to troubleshoot lock-related issues and how to handle optimistic and pessimistic lock conflicts, see [Troubleshoot Lock Conflicts](https://docs.pingcap.com/tidb/stable/troubleshoot-lock-conflicts).
### 3.9 Inconsistency between data and indexes

TiDB checks consistency between data and indexes when it executes transactions or the [`ADMIN CHECK [TABLE|INDEX]`](/sql-statements/sql-statement-admin-check-table-index.md) statement. If the check finds that a record key-value and the corresponding index key-value are inconsistent, that is, a key-value pair storing row data and the corresponding key-value pair storing its index are inconsistent (for example, more indexes or missing indexes), TiDB reports a data inconsistency error and prints the related errors in error logs.

To learn more about the inconsistency error and how to bypass the check, see [Troubleshoot Inconsistency Between Data and Indexes](https://docs.pingcap.com/tidb/stable/troubleshoot-data-inconsistency-errors).
