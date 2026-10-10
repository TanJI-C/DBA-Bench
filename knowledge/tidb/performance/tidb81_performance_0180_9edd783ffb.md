# Composite index tuning for ORDER BY queries

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > Index strategy in TiDB > SQL tuning with a composite index involving sorting`
- Source Line Ranges: `693-753`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `sql-tuning`, `composite-index`, `order-by`, `sorting`, `execution-plan`, `explain-analyze`, `indexlookup`, `topn`, `limit`, `analyze-table`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0180_9edd783ffb`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#sql-tuning-with-a-composite-index-involving-sorting`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ceabbbdea87e084ff272b88eb78cbf5b96b2af90a5e0b9efa5555b94f1447bb1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#sql-tuning-with-a-composite-index-involving-sorting
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB SQL tuning guidance for an ORDER BY ... LIMIT query where EXPLAIN ANALYZE shows IndexLookUp, TopN, and sorting because the existing composite index does not preserve id order.
- Retrieval Keywords: ORDER BY, LIMIT, EXPLAIN ANALYZE, composite index, sorting, TopN_10, Limit_14, IndexLookUp_23, IndexLookUp_35, IndexRangeScan_20, IndexRangeScan_33, keep order:false, keep order:true, test_idx(snapshot_id, user_id, status), test_new(snapshot_id), CREATE INDEX test_new ON test(snapshot_id), ANALYZE TABLE test INDEX test_new, snapshot_id = 459840, test.id > 998464, ORDER BY test.id ASC
- Follow-up Guidance: The content also shows the original and optimized execution plans, including the change from TopN to Limit and the keep order property on IndexRangeScan.
- Classification Note: This chunk is classified as performance for the SQL component because it explains how a composite index choice affects execution-plan operators, row ordering, and query latency for ORDER BY queries.

## Official Source Content

#### SQL tuning with a composite index involving sorting

You can optimize queries with `ORDER BY` clauses by creating composite indexes that include both filtering and sorting columns. This approach helps TiDB access data efficiently while maintaining the desired order.

For example, consider the following query that retrieves data from `test` based on specific conditions:

```sql
EXPLAIN ANALYZE SELECT  
test.*
FROM
  test
WHERE
  test.snapshot_id = 459840
  AND test.id > 998464
ORDER BY
  test.id ASC
LIMIT
  1000
```

The execution plan shows a duration of 170 ms. TiDB uses the `test_index` to perform an `IndexRangeScan_20` with the filter `snapshot_id = 459840`. It then retrieves all columns from the table, returning 5,715 rows to TiDB after `IndexLookUp_23`. TiDB sorts these rows and returns 1,000 rows.

The `id` column is the primary key, which means it is implicitly included in the `test_idx` index. However, `IndexRangeScan_20` does not guarantee order because `test_idx` includes two additional columns (`user_id` and `status`) after the index prefix column `snapshot_id`. As a result, the ordering of `id` is not preserved.

The original plan is as follows:

```
+------------------------------+---------+---------+-----------+----------------------------------------------------------+-----------------------------------------------+--------------------------------------------+
| id                           | estRows | actRows | task      | access object                                            | execution info                                | operator info                              | 
+------------------------------+---------+---------+-----------+----------------------------------------------------------+-----------------------------------------------+--------------------------------------------+
| id                           | estRows | actRows | task      | access object                                            | execution info                             ...| test.id, offset:0, count:1000              | 
| TopN_10                      | 19.98   | 1000    | root      |                                                          | time:170.6ms, loops:2                      ...|                                            |
| └─IndexLookUp_23             | 19.98   | 5715    | root      |                                                          | time:166.6ms, loops:7                      ...|                                            | 
|   ├─Selection_22(Build)      | 19.98   | 5715    | cop[tikv] |                                                          | time:18.6ms, loops:9, cop_task: {num: 3,   ...| gt(test.id, 998464)                        | 
|   │ └─IndexRangeScan_20      | 433.47  | 7715    | cop[tikv] | table:test, index:test_idx(snapshot_id, user_id, status) | tikv_task:{proc max:4ms, min:4ms, avg: 4ms ...| range:[459840,459840], keep order:false    |
|   └─TableRowIDScan_21(Probe) | 19.98   | 5715    | cop[tikv] | table:test                                               | time:301.6ms, loops:10, cop_task: {num: 3, ...| keep order:false                           | 
+------------------------------+---------+---------+-----------+----------------------------------------------------------+-----------------------------------------------+--------------------------------------------+
```

To optimize the query, you can create a new index on `(snapshot_id)`. This ensures that `id` is sorted within each `snapshot_id` group. With this index, execution time drops to 96 ms. The `keep order` property becomes `true` for `IndexRangeScan_33`, and `TopN` is replaced with `Limit`. As a result, `IndexLookUp_35` returns only 1,000 rows to TiDB, eliminating the need for additional sorting operations.

The following is the query statement with the optimized index:

```sql
CREATE INDEX test_new ON test(snapshot_id);
ANALYZE TABLE test INDEX test_new;
```

The new plan is as follows:

```
+----------------------------------+---------+---------+-----------+----------------------------------------------+----------------------------------------------+----------------------------------------------------+
| id                               | estRows | actRows | task      | access object                                | execution info                               | operator info                                      |
+----------------------------------+---------+---------+-----------+----------------------------------------------+----------------------------------------------+----------------------------------------------------+
| Limit_14                         | 17.59   | 1000    | root      |                                              | time:96.1ms, loops:2, RU:92.300155           | offset:0, count:1000                               |
| └─IndexLookUp_35                 | 17.59   | 1000    | root      |                                              | time:96.1ms, loops:1, index_task:         ...|                                                    |
|   ├─IndexRangeScan_33(Build)     | 17.59   | 5715    | cop[tikv] | table:test, index:test_new(snapshot_id)      | time:7.25ms, loops:8, cop_task: {num: 3,  ...| range:(459840 998464,459840 +inf], keep order:true |
|   └─TableRowIDScan_34(Probe)     | 17.59   | 5715    | cop[tikv] | table:test                                   | time:232.9ms, loops:9, cop_task: {num: 3, ...| keep order:false                                   |
+----------------------------------+---------+---------+-----------+----------------------------------------------+----------------------------------------------+----------------------------------------------------+
```
