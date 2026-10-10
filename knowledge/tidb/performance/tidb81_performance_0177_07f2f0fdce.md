# Identify bottlenecks in execution plans

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > Understand execution plans > Identify bottlenecks in execution plans`
- Source Line Ranges: `489-538`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `execution-plans`, `actrows`, `estrows`, `statistics`, `optimizer`, `join-order`, `memory-usage`, `disk-usage`, `hash-join`, `table-scan`, `index-scan`, `query-performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0177_07f2f0fdce`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#identify-bottlenecks-in-execution-plans`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b9fa4c3acc1e098b18775068499c76848ffc1fb9fc59e31de5a03fb239829e06`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#identify-bottlenecks-in-execution-plans
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing a slow query by reading an execution plan and comparing `actRows`, `estRows`, execution time, and `memory` or `disk` usage to find bottleneck operators or incorrect join order.
- Retrieval Keywords: Identify bottlenecks in execution plans, actRows, estRows, execution info, memory, disk, TableFullScan, HashJoin, IndexReader_76, IndexRangeScan_75, HashJoin_69, index_orders_on_adjustment_id(adjustment_id), orders table, incorrect join order, outdated statistics, query termination due to resource constraints
- Follow-up Guidance: The source continues with an example where updated statistics on the `orders` table make `estRows` closer to `actRows`, change the join order, remove excessive memory and disk usage, and reduce execution time from 5 minutes 51 seconds to 1.96 seconds.
- Classification Note: This chunk is classified as performance for SQL because it explains how to analyze TiDB execution plans and TiKV coprocessor operators to identify estimation errors, resource pressure, and inefficient join order that cause slow queries.

## Official Source Content

#### Identify bottlenecks in execution plans

When analyzing execution plans, compare `actRows` (actual rows) with `estRows` (estimated rows) to evaluate the accuracy of the optimizer's estimations. A significant difference between these values might indicate outdated or inaccurate statistics, which can lead to suboptimal query plans.

To identify bottlenecks in a slow query, perform the following steps:

1. Review the `execution info` section from top to bottom, focusing on operators with high execution time.
2. For the first child operator that consumes significant time:
    - Compare `actRows` with `estRows` to assess estimation accuracy.
    - Analyze detailed metrics in `execution info`, such as high execution time or other metrics.
    - Check `memory` and `disk` usage for potential resource constraints.
3. Correlate these factors to determine the root cause of the performance issue. For example, if a `TableFullScan` operation has a high `actRows` count and long execution time in `execution info`, consider creating an index. If a `HashJoin` operation shows high memory usage and execution time, consider optimizing the join order or using an alternative join method.

In the following execution plan, the query runs for 5 minutes and 51 seconds before being canceled. The key issues include:

1. Severe underestimation: The first leaf node `IndexReader_76` reads data from the `index_orders_on_adjustment_id(adjustment_id)` index. The actual number of rows (`actRows`) is 256,811,189, which is significantly higher than the estimated 1 row (`estRows`).
2. Memory overflow: This underestimation causes the hash join operator `HashJoin_69` to build a hash table with far more data than expected, consuming excessive memory (22.6 GB) and disk space (7.65 GB).
3. Query termination: The `actRows` value of `0` for `HashJoin_69` and operators above it indicate either no matching rows or query termination due to resource constraints. In this case, the hash join consumes too much memory, triggering memory control mechanisms to terminate the query.
4. Incorrect join order: The root cause of this inefficient plan is the severe underestimation of `estRows` for `IndexRangeScan_75`, leading the optimizer to choose an incorrect join order.

To address these issues, ensure that table statistics are up to date, particularly for the `orders` table and the `index_orders_on_adjustment_id` index.

```
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------...----------------------+
| id                                 | estRows   | estCost      | actRows   | task      | access object                                                                          | execution info ...| memory   | disk     |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------...----------------------+
| TopN_19                            | 1.01      | 461374372.63 | 0         | root      |                                                                                        | time:5m51.1s, l...| 0 Bytes  | 0 Bytes  |
| └─IndexJoin_32                     | 1.01      | 460915067.45 | 0         | root      |                                                                                        | time:5m51.1s, l...| 0 Bytes  | N/A      |
|   ├─HashJoin_69(Build)             | 1.01      | 460913065.41 | 0         | root      |                                                                                        | time:5m51.1s, l...| 21.6 GB  | 7.65 GB  |
|   │ ├─IndexReader_76(Build)        | 1.00      | 18.80        | 256805045 | root      |                                                                                        | time:1m4.1s, lo...| 12.4 MB  | N/A      |
|   │ │ └─IndexRangeScan_75          | 1.00      | 186.74       | 256811189 | cop[tikv] | table:orders, index:index_orders_on_adjustment_id(adjustment_id)                       | tikv_task:{proc...| N/A      | N/A      |
|   │ └─Projection_74(Probe)         | 30652.93  | 460299612.60 | 1024      | root      |                                                                                        | time:1.08s, loo...| 413.4 KB | N/A      |
|   │   └─IndexLookUp_73             | 30652.93  | 460287375.95 | 6144      | root      | partition:all                                                                          | time:1.08s, loo...| 107.8 MB | N/A      |
|   │     ├─IndexRangeScan_70(Build) | 234759.64 | 53362737.50  | 390699    | cop[tikv] | table:rates, index:index_rates_on_label_id(label_id)                                   | time:29.6ms, lo...| N/A      | N/A      |
|   │     └─Selection_72(Probe)      | 30652.93  | 110373973.91 | 187070    | cop[tikv] |                                                                                        | time:36.8s, loo...| N/A      | N/A      |
|   │       └─TableRowIDScan_71      | 234759.64 | 86944962.10  | 390699    | cop[tikv] | table:rates                                                                            | tikv_task:{proc...| N/A      | N/A      |
|   └─TableReader_28(Probe)          | 0.00      | 43.64        | 0         | root      |                                                                                        |                ...| N/A      | N/A      |
|     └─Selection_27                 | 0.00      | 653.96       | 0         | cop[tikv] |                                                                                        |                ...| N/A      | N/A      |
|       └─TableRangeScan_26          | 1.01      | 454.36       | 0         | cop[tikv] | table:labels                                                                           |                ...| N/A      | N/A      |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------...----------------------+
```

The following execution plan shows the expected results after fixing the incorrect estimation on the `orders` table. The query now takes 1.96 seconds to run, which is a significant improvement from the previous 5 minutes and 51 seconds:

- Accurate estimation: The `estRows` values now closely match the `actRows`, indicating that the statistics are updated and more accurate.
- Efficient join order: The query now starts with a `TableReader` on the `labels` table, followed by an `IndexJoin` with the `rates` table, and another `IndexJoin` with the `orders` table. This join order works more efficiently with the actual data distribution.
- No memory overflow: Unlike the previous plan, this execution shows no signs of excessive memory or disk usage, indicating that the query runs within expected resource limits.

This optimized plan demonstrates the importance of accurate statistics and proper join order in query performance. The execution time reduction (from 351 seconds to 1.96 seconds) shows the impact of addressing estimation errors.
