# Assess performance with EXPLAIN ANALYZE and statistics health

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-walkthrough.md`
- Source Title: `EXPLAIN Walkthrough`
- Source Heading Path: ``EXPLAIN` Walkthrough > Assess the current performance`
- Source Line Ranges: `87-120`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain-analyze`, `execution-plan`, `statistics`, `analyze-table`, `show-stats-healthy`, `row-estimation`, `table-scan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0039_f929b25585`
- Source ID: `tidb-docs-8.1:explain-walkthrough.md#assess-the-current-performance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2b38f7e137e256833ad29ea2fd1166d13de54de088cb89b46c69e9cc5222c212`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-walkthrough#assess-the-current-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-walkthrough.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing a query with EXPLAIN ANALYZE where actual rows differ from estimated rows and you need to check whether outdated statistics are affecting the plan.
- Retrieval Keywords: EXPLAIN ANALYZE, ANALYZE TABLE, SHOW STATS_HEALTHY, tidb_auto_analyze_ratio, estRows, actRows, TableFullScan_18, Selection_19, statistics health, outdated statistics, row estimation
- Follow-up Guidance: The source also points to SHOW STATS_HEALTHY to see how close TiDB is to the tidb_auto_analyze_ratio threshold after ANALYZE TABLE or automatic statistics regeneration.
- Classification Note: This is classified as diagnosis because the content explains how to assess current query performance and verify whether inaccurate statistics are causing sub-optimal plans.

## Official Source Content

```sql
Query OK, 0 rows affected (10.22 sec)

+------------------------------+-------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------+-----------+------+
| id                           | estRows     | actRows  | task      | access object | execution info                                                                                                                                                                                                                                   | operator info                                                                                                          | memory    | disk |
+------------------------------+-------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------+-----------+------+
| StreamAgg_20                 | 1.00        | 1        | root      |               | time:926.393612ms, loops:2                                                                                                                                                                                                                       | funcs:count(Column#13)->Column#11                                                                                      | 632 Bytes | N/A  |
| └─TableReader_21             | 1.00        | 56       | root      |               | time:926.384792ms, loops:2, cop_task: {num: 56, max: 850.94424ms, min: 6.042079ms, avg: 234.987725ms, p95: 495.474806ms, max_proc_keys: 910371, p95_proc_keys: 704775, tot_proc: 10.656s, tot_wait: 904ms, rpc_num: 56, rpc_time: 13.158911952s} | data:StreamAgg_9                                                                                                       | 328 Bytes | N/A  |
|   └─StreamAgg_9              | 1.00        | 56       | cop[tikv] |               | proc max:592ms, min:4ms, p80:244ms, p95:480ms, iters:18695, tasks:56                                                                                                                                                                             | funcs:count(1)->Column#13                                                                                              | N/A       | N/A  |
|     └─Selection_19           | 432.89      | 11409    | cop[tikv] |               | proc max:592ms, min:4ms, p80:244ms, p95:480ms, iters:18695, tasks:56                                                                                                                                                                             | ge(bikeshare.trips.start_date, 2017-07-01 00:00:00.000000), le(bikeshare.trips.start_date, 2017-07-01 23:59:59.000000) | N/A       | N/A  |
|       └─TableFullScan_18     | 19117643.00 | 19117643 | cop[tikv] | table:trips   | proc max:564ms, min:4ms, p80:228ms, p95:456ms, iters:18695, tasks:56                                                                                                                                                                             | keep order:false                                                                                                       | N/A       | N/A  |
+------------------------------+-------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------+-----------+------+
5 rows in set (0.93 sec)
```

After `ANALYZE TABLE` is executed, you can see that the estimated rows for the `└─TableFullScan_18` operator is accurate and the estimate for `└─Selection_19` is now also much closer. In the two cases above, although the execution plan (the set of operators TiDB uses to execute this query) has not changed, quite frequently sub-optimal plans are caused by outdated statistics.

In addition to `ANALYZE TABLE`, TiDB automatically regenerates statistics as a background operation after the threshold of [`tidb_auto_analyze_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_ratio) is reached. You can see how close TiDB is to this threshold (how healthy TiDB considers the statistics to be) by executing the [`SHOW STATS_HEALTHY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-healthy) statement:

```sql
SHOW STATS_HEALTHY;
```

```sql
+-----------+------------+----------------+---------+
| Db_name   | Table_name | Partition_name | Healthy |
+-----------+------------+----------------+---------+
| bikeshare | trips      |                |     100 |
+-----------+------------+----------------+---------+
1 row in set (0.00 sec)
```
