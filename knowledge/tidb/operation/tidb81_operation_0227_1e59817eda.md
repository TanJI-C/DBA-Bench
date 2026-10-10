# Statistics collection overview, automatic update, and manual ANALYZE

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics | Introduction to Statistics > Collect statistics | Introduction to Statistics > Collect statistics > Automatic update | Introduction to Statistics > Collect statistics > Manual collection`
- Source Line Ranges: `5-73`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `statistics`, `optimizer`, `auto-analyze`, `analyze-table`, `sampling`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0227_1e59817eda`
- Source ID: `tidb-docs-8.1:statistics.md#introduction-to-statistics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `01fa103bfef808664b93cc17e90055584d10222ee68a19602895944b92ee9891`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#introduction-to-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when you need the overview of TiDB statistics, automatic update behavior, or the `ANALYZE TABLE` manual collection syntax and related `tidb_auto_analyze%` variables.
- Retrieval Keywords: Introduction to Statistics, automatic update, manual collection, ANALYZE TABLE, ANALYZE TABLE tbl, tidb_enable_auto_analyze, tidb_auto_analyze_ratio, tidb_auto_analyze_start_time, tidb_auto_analyze_end_time, tidb_auto_analyze_partition_batch_size, tidb_enable_auto_analyze_priority_queue, SHOW STATS_META, WITH NUM BUCKETS, WITH NUM TOPN, WITH NUM CMSKETCH DEPTH, WITH NUM CMSKETCH WIDTH, WITH NUM SAMPLES, WITH FLOAT_NUM SAMPLERATE
- Follow-up Guidance: See Histograms, Top-N, and CMSketch for the related statistics types.
- Classification Note: This content is an operational introduction to how TiDB collects statistics automatically and manually for optimizer cost estimation.

## Official Source Content

# Introduction to Statistics

TiDB uses statistics as input to the optimizer to estimate the number of rows processed in each plan step for a SQL statement. The optimizer estimates the cost of each available plan choice, including [index accesses](https://docs.pingcap.com/tidb/stable/choose-index) and the sequence of table joins, and produces a cost for each available plan. The optimizer then picks the execution plan with the lowest overall cost.
## Collect statistics

This section describes two ways of collecting statistics: automatic update and manual collection.
### Automatic update

For the [`INSERT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert), [`DELETE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete), or [`UPDATE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update) statements, TiDB automatically updates the number of rows and modified rows in statistics.

TiDB persists the update information regularly and the update cycle is 20 * [`stats-lease`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#stats-lease). The default value of `stats-lease` is `3s`. If you specify the value as `0`, TiDB stops updating statistics automatically.

TiDB persists the update information every 60 seconds.

Based upon the number of changes to a table, TiDB will automatically schedule [`ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) to collect statistics on those tables. This is controlled by the [`tidb_enable_auto_analyze`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_auto_analyze-new-in-v610) system variable and the following `tidb_auto_analyze%` variables.

|  System Variable | Default Value | Description |
|---|---|---|
| [`tidb_enable_auto_analyze`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_auto_analyze-new-in-v610) | `ON` | Controls whether TiDB automatically executes `ANALYZE`. |
| [`tidb_auto_analyze_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_ratio) | `0.5` | The threshold value of automatic update. |
| [`tidb_auto_analyze_start_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_start_time) | `00:00 +0000` | The start time in a day when TiDB can perform automatic update. |
| [`tidb_auto_analyze_end_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_end_time)   | `23:59 +0000` | The end time in a day when TiDB can perform automatic update. |
| [`tidb_auto_analyze_partition_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_partition_batch_size-new-in-v640) | `128` | The number of partitions that TiDB automatically analyzes when analyzing a partitioned table (that is, when automatically updating statistics on a partitioned table). |
| [`tidb_enable_auto_analyze_priority_queue`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_auto_analyze_priority_queue-new-in-v800) | `ON` | Controls whether to enable the priority queue to schedule the tasks of automatically collecting statistics. When this variable is enabled, TiDB prioritizes collecting statistics for tables that are more valuable to collect, such as newly created indexes and partitioned tables with partition changes. Additionally, TiDB prioritizes tables with lower health scores, placing them at the front of the queue. |

When the ratio of the number of modified rows to the total number of rows of `tbl` in a table is greater than `tidb_auto_analyze_ratio`, and the current time is between `tidb_auto_analyze_start_time` and `tidb_auto_analyze_end_time`, TiDB executes the `ANALYZE TABLE tbl` statement in the background to automatically update the statistics on this table.

To avoid the situation that modifying data on a small table frequently triggers the automatic update, when a table has less than 1000 rows, modifications do not trigger the automatic update in TiDB. You can use the `SHOW STATS_META` statement to view the number of rows in a table.

> **Note:**
>
> Currently, the automatic update does not record the configuration items input at manual `ANALYZE`. Therefore, when you use the [`WITH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) syntax to control the collecting behavior of `ANALYZE`, you need to manually set scheduled tasks to collect statistics.
### Manual collection

Currently, TiDB collects statistics as a full collection. You can execute the `ANALYZE TABLE` statement to collect statistics.

You can perform full collection using the following syntax.

+ To collect statistics of all the tables in `TableNameList`:

    ```sql
    ANALYZE TABLE TableNameList [WITH NUM BUCKETS|TOPN|CMSKETCH DEPTH|CMSKETCH WIDTH]|[WITH NUM SAMPLES|WITH FLOATNUM SAMPLERATE];
    ```

+ `WITH NUM BUCKETS` specifies the maximum number of buckets in the generated histogram.
+ `WITH NUM TOPN` specifies the maximum number of the generated `TOPN`s.
+ `WITH NUM CMSKETCH DEPTH` specifies the depth of the CM Sketch.
+ `WITH NUM CMSKETCH WIDTH` specifies the width of the CM Sketch.
+ `WITH NUM SAMPLES` specifies the number of samples.
+ `WITH FLOAT_NUM SAMPLERATE` specifies the sampling rate.

`WITH NUM SAMPLES` and `WITH FLOAT_NUM SAMPLERATE` correspond to two different algorithms of collecting samples.

See [Histograms](#histogram), [Top-N](#top-n) and [CMSketch](#count-min-sketch) (Count-Min Sketch) for detailed explanations. For `SAMPLES`/`SAMPLERATE`, see [Improve collection performance](#improve-collection-performance).

For information on persisting the options for easier reuse, see [Persist `ANALYZE` configurations](#persist-analyze-configurations).
