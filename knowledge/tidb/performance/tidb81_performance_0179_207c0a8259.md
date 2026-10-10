# Covering index tuning example

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > Index strategy in TiDB > SQL tuning with a covering index`
- Source Line Ranges: `630-692`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `covering-index`, `index-lookup`, `execution-plan`, `analyze-table`, `statistics`, `cop-task`, `query-performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0179_207c0a8259`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#sql-tuning-with-a-covering-index`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b661e55ffb24a56a23aac99c09b5c5920c3cf0a58d5768ce8353bbda0fa1712e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#sql-tuning-with-a-covering-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an example of improving a TiDB query by replacing an IndexLookUp with a covering index and comparing the execution plans before and after.
- Retrieval Keywords: covering index, IndexLookUp_19, IndexRangeScan_11, TableRowIDScan_12, logs_idx(snapshot_id, user_id, status), CREATE INDEX logs_covered ON logs(snapshot_id, user_id, status, source_type, target_type, amount), ANALYZE TABLE logs INDEX logs_covered, IndexReader_14, cop_task: {num: 1}, SUM(logs.amount), source_type, target_type, amount, statistics, execution plan
- Follow-up Guidance: The source also states that after creating `logs_covered`, executing `ANALYZE TABLE logs INDEX logs_covered;` collects statistics so the optimizer can select the new index.
- Classification Note: This chunk is classified as performance for SQL because it shows a query-performance tuning example in TiDB using a covering index, execution-plan changes, and updated statistics with work executed in TiKV cop tasks.

## Official Source Content

#### SQL tuning with a covering index

A covering index includes all columns referenced in the `WHERE` and `SELECT` clauses. Using a covering index can eliminate the need for additional index lookups, significantly improving query performance.

The following query requires an index lookup of 2,597,411 rows and takes 46.4 seconds to execute. TiDB dispatches 67 cop tasks for the index range scan on `logs_idx` (`IndexRangeScan_11`) and 301 cop tasks for table access (`TableRowIDScan_12`).

```sql
SELECT
  SUM(`logs`.`amount`)
FROM
  `logs`
WHERE
  `logs`.`user_id` = 1111
  AND `logs`.`snapshot_id` IS NULL
  AND `logs`.`status` IN ('complete', 'failure')
  AND `logs`.`source_type` != 'online'
  AND (
    `logs`.`source_type` IN ('user', 'payment')
    OR `logs`.`source_type` IN (
      'bank_account',
    )
    AND `logs`.`target_type` IN ('bank_account')
  );
```

The original execution plan is as follows:

```
+-------------------------------+------------+---------+-----------+--------------------------------------------------------------------------+------------------------------------------------------------+
| id                            | estRows    | actRows | task      | access object                                                            | execution info                                             | 
+-------------------------------+------------+---------+-----------+--------------------------------------------------------------------------+------------------------------------------------------------+
| HashAgg_18                   | 1.00       | 2571625.22 | 1       | root      |                                                              | time:46.4s, loops:2, partial_worker:{wall_time:46.37,   ...|
| └─IndexLookUp_19             | 1.00       | 2570096.68 | 301     | root      |                                                              | time:46.4s, loops:2, index_task: {total_time: 45.8s,    ...|
|   ├─IndexRangeScan_11(Build) | 1309.50    | 317033.98  | 2597411 | cop[tikv] | table:logs, index:logs_idx(snapshot_id, user_id, status)     | time:228ms, loops:2547, cop_task: {num: 67, max: 2.17s, ...|
|   └─HashAgg_7(Probe)         | 1.00       | 588434.48  | 301     | cop[tikv] |                                                              | time:3m46.7s, loops:260, cop_task: {num: 301,           ...|
|     └─Selection_13           | 1271.37    | 561549.27  | 2566562 | cop[tikv] |                                                              | tikv_task:{proc max:10s, min:0s, avg: 915.3ms,          ...|
|       └─TableRowIDScan_12    | 1309.50    | 430861.31  | 2597411 | cop[tikv] | table:logs                                                   | tikv_task:{proc max:10s, min:0s, avg: 908.7ms,          ...|
+-------------------------------+------------+---------+-----------+--------------------------------------------------------------------------+------------------------------------------------------------+
```

To improve query performance, you can create a covering index that includes `source_type`, `target_type`, and `amount` columns. This optimization eliminates the need for additional table lookups, reducing execution time to 90 milliseconds, and TiDB only needs to send one cop task to TiKV for data scanning.

After creating the index, execute the `ANALYZE TABLE` statement to collect statistics. In TiDB, index creation does not automatically update statistics, so analyzing the table ensures that the optimizer selects the new index.

```sql
CREATE INDEX logs_covered ON logs(snapshot_id, user_id, status, source_type, target_type, amount); 
ANALYZE TABLE logs INDEX logs_covered;
```

The new execution plan is as follows:

```
+-------------------------------+------------+---------+-----------+---------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------+
| id                            | estRows    | actRows | task      | access object                                                                                                                   | execution info                              |
+-------------------------------+------------+---------+-----------+---------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------+
| HashAgg_13                    | 1.00       | 1       | root      |                                                                                                                                 | time:90ms, loops:2, RU:158.885311,       ...|
| └─IndexReader_14              | 1.00       | 1       | root      |                                                                                                                                 | time:89.8ms, loops:2, cop_task: {num: 1, ...|
|   └─HashAgg_6                 | 1.00       | 1       | cop[tikv] |                                                                                                                                 | tikv_task:{time:88ms, loops:52},         ...|
|     └─Selection_12            | 5245632.33 | 52863   | cop[tikv] |                                                                                                                                 | tikv_task:{time:80ms, loops:52}          ...|
|       └─IndexRangeScan_11     | 5245632.33 | 52863   | cop[tikv] | table:logs, index:logs_covered(snapshot_id, user_id, status, source_type, target_type, amount)                                  | tikv_task:{time:60ms, loops:52}          ...|
+-------------------------------+------------+---------+-----------+---------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------+
```
