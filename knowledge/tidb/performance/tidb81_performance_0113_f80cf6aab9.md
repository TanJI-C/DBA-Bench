# EXPLAIN optimization result with index and coprocessor cache note

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-walkthrough.md`
- Source Title: `EXPLAIN Walkthrough`
- Source Heading Path: ``EXPLAIN` Walkthrough > Identify optimizations`
- Source Line Ranges: `200-217`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tikv`
- Topic Tags: `explain`, `query-optimization`, `index-scan`, `stream-aggregation`, `coprocessor-cache`, `execution-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0113_f80cf6aab9`
- Source ID: `tidb-docs-8.1:explain-walkthrough.md#identify-optimizations`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e3736c97436d20de680ede51775fbdff6e4aa980bde34c3bcd49d60716192895`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-walkthrough#identify-optimizations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-walkthrough.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting an EXPLAIN plan that shows StreamAgg, IndexReader, and IndexRangeScan on table `trips` with index `start_date(start_date)`, or when looking for the coprocessor cache note tied to expensive `TableFullScan` and `Selection` operators.
- Retrieval Keywords: EXPLAIN Walkthrough Identify optimizations, StreamAgg_17, IndexReader_18, StreamAgg_9, IndexRangeScan_16, table:trips, index:start_date(start_date), range:[2017-07-01 00:00:00,2017-07-01 23:59:59], cop[tikv], cop_task, coprocessor cache, TableFullScan, Selection
- Follow-up Guidance: The note says that if the Region has not been modified since the operator was last executed, TiKV returns the value from the coprocessor cache, which helps reduce much of the cost of expensive `TableFullScan` and `Selection` operators.
- Classification Note: This is classified as performance because the official content explains an optimized EXPLAIN result with index access and a coprocessor cache note that reduces query time and scan cost.

## Official Source Content

```sql
+-----------------------------+---------+---------+-----------+-------------------------------------------+------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+-----------+------+
| id                          | estRows | actRows | task      | access object                             | execution info                                                                                                   | operator info                                                     | memory    | disk |
+-----------------------------+---------+---------+-----------+-------------------------------------------+------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+-----------+------+
| StreamAgg_17                | 1.00    | 1       | root      |                                           | time:4.516728ms, loops:2                                                                                         | funcs:count(Column#13)->Column#11                                 | 372 Bytes | N/A  |
| └─IndexReader_18            | 1.00    | 1       | root      |                                           | time:4.514278ms, loops:2, cop_task: {num: 1, max:4.462288ms, proc_keys: 11409, rpc_num: 1, rpc_time: 4.457148ms} | index:StreamAgg_9                                                 | 238 Bytes | N/A  |
|   └─StreamAgg_9             | 1.00    | 1       | cop[tikv] |                                           | time:4ms, loops:12                                                                                               | funcs:count(1)->Column#13                                         | N/A       | N/A  |
|     └─IndexRangeScan_16     | 8471.88 | 11409   | cop[tikv] | table:trips, index:start_date(start_date) | time:4ms, loops:12                                                                                               | range:[2017-07-01 00:00:00,2017-07-01 23:59:59], keep order:false | N/A       | N/A  |
+-----------------------------+---------+---------+-----------+-------------------------------------------+------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------+-----------+------+
4 rows in set (0.00 sec)
```

From the result above, the query time has reduced from 1.03 seconds to 0.0 seconds.

> **Note:**
>
> Another optimization that applies here is the coprocessor cache. If you are unable to add indexes, consider enabling the [coprocessor cache](https://docs.pingcap.com/tidb/stable/coprocessor-cache). When it is enabled, as long as the Region has not been modified since the operator is last executed, TiKV will return the value from the cache. This will also help reduce much of the cost of the expensive `TableFullScan` and `Selection` operators.
