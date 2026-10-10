# View ANALYZE status and statistics metadata

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > View statistics | Introduction to Statistics > View statistics > `ANALYZE` state | Introduction to Statistics > View statistics > Metadata of tables | Introduction to Statistics > View statistics > Health state of tables | Introduction to Statistics > View statistics > Metadata of columns | Introduction to Statistics > View statistics > Buckets of histogram | Introduction to Statistics > View statistics > Top-N information`
- Source Line Ranges: `422-466`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `statistics`, `analyze`, `status`, `metadata`, `health`, `histogram`, `topn`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0080_95daed67c8`
- Source ID: `tidb-docs-8.1:statistics.md#view-statistics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `17c6bd64b2e9f917db10038a4fd823860295699f43aac228a94f9e1a3ae0d52d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#view-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when you need to view ANALYZE status or inspect statistics metadata, health, histograms, buckets, or Top-N information in TiDB.
- Retrieval Keywords: SHOW ANALYZE STATUS, mysql.analyze_jobs, tidb_mem_quota_analyze, tidb_max_auto_analyze_time, SHOW STATS_META, SHOW STATS_HEALTHY, modify_count, row_count, SHOW STATS_HISTOGRAMS, SHOW STATS_BUCKETS, SHOW STATS_TOPN, analyze panic due to memory quota exceeds, cluster-level tasks, history tasks within the last 7 days
- Follow-up Guidance: The source notes that SHOW ANALYZE STATUS shows only the most recent task records, while mysql.analyze_jobs can be used to view history tasks within the last 7 days.
- Classification Note: This is classified as an observability chunk because the official content is about viewing ANALYZE state and inspecting statistics-related metadata and health through SHOW statements and a system table.

## Official Source Content

## View statistics

You can view the `ANALYZE` status and statistics information using the following statements.
### `ANALYZE` state

When executing the `ANALYZE` statement, you can view the current state of `ANALYZE` using [`SHOW ANALYZE STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-analyze-status).

Starting from TiDB v6.1.0, the `SHOW ANALYZE STATUS` statement supports showing cluster-level tasks. Even after a TiDB restart, you can still view task records before the restart using this statement. Before TiDB v6.1.0, the `SHOW ANALYZE STATUS` statement can only show instance-level tasks, and task records are cleared after a TiDB restart.

`SHOW ANALYZE STATUS` shows the most recent task records only. Starting from TiDB v6.1.0, you can view the history tasks within the last 7 days through the system table `mysql.analyze_jobs`.

When [`tidb_mem_quota_analyze`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_analyze-new-in-v610) is set and an automatic `ANALYZE` task running in the TiDB background uses more memory than this threshold, the task will be retried. You can see failed and retried tasks in the output of the `SHOW ANALYZE STATUS` statement.

When [`tidb_max_auto_analyze_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_auto_analyze_time-new-in-v610) is greater than 0 and an automatic `ANALYZE` task running in the TiDB background takes more time than this threshold, the task will be terminated.

```sql
mysql> SHOW ANALYZE STATUS [ShowLikeOrWhere];
+--------------+------------+----------------+-------------------------------------------------------------------------------------------+----------------+---------------------+---------------------+----------+-------------------------------------------------------------------------------|
| Table_schema | Table_name | Partition_name | Job_info                                                                                  | Processed_rows | Start_time          | End_time            | State    | Fail_reason                                                                   |
+--------------+------------+----------------+-------------------------------------------------------------------------------------------+----------------+---------------------+---------------------+----------+-------------------------------------------------------------------------------|
| test         | sbtest1    |                | retry auto analyze table all columns with 100 topn, 0.055 samplerate                      |        2000000 | 2022-05-07 16:41:09 | 2022-05-07 16:41:20 | finished | NULL                                                                          |
| test         | sbtest1    |                | auto analyze table all columns with 100 topn, 0.5 samplerate                              |              0 | 2022-05-07 16:40:50 | 2022-05-07 16:41:09 | failed   | analyze panic due to memory quota exceeds, please try with smaller samplerate |
```
### Metadata of tables

You can use the [`SHOW STATS_META`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-meta) statement to view the total number of rows and the number of updated rows.
### Health state of tables

You can use the [`SHOW STATS_HEALTHY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-healthy) statement to check the health state of tables and roughly estimate the accuracy of the statistics. When `modify_count` >= `row_count`, the health state is 0; when `modify_count` < `row_count`, the health state is (1 - `modify_count`/`row_count`) * 100.
### Metadata of columns

You can use the [`SHOW STATS_HISTOGRAMS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-histograms) statement to view the number of different values and the number of `NULL` in all the columns.
### Buckets of histogram

You can use the [`SHOW STATS_BUCKETS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-buckets) statement to view each bucket of the histogram.
### Top-N information

You can use the [`SHOW STATS_TOPN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-topn) statement to view the Top-N information currently collected by TiDB.
