# Enable distinct aggregate pushdown for TiFlash queries

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Push down aggregate functions to a position before `Join` or `Union` | Tune TiFlash Performance > Tune TiDB parameters > Enable `Distinct` optimization`
- Source Line Ranges: `167-203`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `mpp`, `aggregate-pushdown`, `distinct`, `coprocessor`, `query-optimization`, `system-variables`, `explain-analyze`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0256_36062ac093`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#push-down-aggregate-functions-to-a-position-before-join-or-union`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0e790450af54596fa42fac96e7c4b1d2b4a798edfb9e8c0ce3d31a1f9aeb6877`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#push-down-aggregate-functions-to-a-position-before-join-or-union
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiFlash query performance guidance for aggregate functions with DISTINCT, especially pushdown behavior controlled by a TiDB system variable.
- Retrieval Keywords: tidb_opt_distinct_agg_push_down, Enable Distinct optimization, Distinct aggregate pushdown, count(distinct a), sum(distinct a), Coprocessor, TiFlash, EXPLAIN ANALYZE, HashAgg_6, group by column test.t.a
- Follow-up Guidance: The example compares EXPLAIN ANALYZE output before and after setting @@tidb_opt_distinct_agg_push_down = ON and notes warnings indicating the aggregate function cannot be fully pushed down to TiFlash.
- Classification Note: This is classified as performance content because it describes enabling DISTINCT aggregate pushdown to TiFlash to improve query performance for slow queries.

## Official Source Content

### Enable `Distinct` optimization

TiFlash does not support some aggregate functions that accept the `Distinct` column, such as `Sum`. By default, the entire aggregate function is calculated in TiDB. By enabling the `Distinct` optimization, some operations can be pushed down to TiFlash, thereby improving query performance.

If the aggregate function with the `distinct` operation is slow in a query, you can enable the optimization operation of pushing down the aggregate function with `Distinct` (such as `select sum(distinct a) from t`) to Coprocessor by setting the value of the [`tidb_opt_distinct_agg_push_down`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_distinct_agg_push_down) variable to `ON`.

```sql
set @@tidb_opt_distinct_agg_push_down = ON;
```

The following example shows the query result before and after the `tidb_opt_distinct_agg_push_down` variable is enabled. Before this variable is enabled, TiDB needs to read all data from TiFlash and execute `distinct` in TiDB. After this variable is enabled, `distinct a` is pushed down to TiFlash, and a new `group by` column `test.t.a` is added in `HashAgg_6`. The two warnings in the query result indicate that the aggregate function cannot be fully pushed down to TiFlash.

Before `tidb_opt_distinct_agg_push_down` is enabled:

```sql
mysql> explain analyze select count(distinct a) from test.t;
+----------------------------+--------------+-----------+--------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------+----------+---------+
| id                         | estRows      | actRows   | task         | access object | execution info                                                                                                                                                                                                                                                                                                                                   | operator info                                          | memory   | disk    |
+----------------------------+--------------+-----------+--------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------+----------+---------+
| HashAgg_6                  | 1.00         | 1         | root         |               | time:2m23.2s, loops:2                                                                                                                                                                                                                                                                                                                            | funcs:sum(distinct Column#23)->Column#22               | 41.3 KB  | 0 Bytes |
| └─Projection_16            | 600000000.00 | 600000000 | root         |               | time:2.51s, loops:586548, Concurrency:5                                                                                                                                                                                                                                                                                                          | cast(test.t.a, decimal(10,0) BINARY)->Column#23        | 243.2 KB | N/A     |
|   └─TableReader_11         | 600000000.00 | 600000000 | root         |               | time:1.6s, loops:586548, cop_task: {num: 1173, max: 256.2ms, min: 25.1ms, avg: 46.9ms, p95: 63.5ms, rpc_num: 1173, rpc_time: 55s, copr_cache_hit_ratio: 0.00, distsql_concurrency: 15}                                                                                                                                                           | data:TableFullScan_10                                  | 70.2 MB  | N/A     |
|     └─TableFullScan_10     | 600000000.00 | 600000000 | cop[tiflash] | table:t       | tiflash_task:{proc max:9ms, min:531µs, avg: 4.49ms, p80:5.55ms, p95:6.74ms, iters:9390, tasks:1173, threads:1173}, tiflash_scan:{dtfile:{total_scanned_packs:73834, total_skipped_packs:1231, total_scanned_rows:600010914, total_skipped_rows:9988978, total_rs_index_load_time: 0ms, total_read_time: 16ms}, total_create_snapshot_time: 0ms}  | keep order:false                                       | N/A      | N/A     |
+----------------------------+--------------+-----------+--------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------+----------+---------+
4 rows in set, 2 warnings (2 min 23.21 sec)
```

Enable `tidb_opt_distinct_agg_push_down`:

```sql
mysql> set @@tidb_opt_distinct_agg_push_down = ON;
Query OK, 0 rows affected (0.00 sec)
```

After `tidb_opt_distinct_agg_push_down` is enabled:
