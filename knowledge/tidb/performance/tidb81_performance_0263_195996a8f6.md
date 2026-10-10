# Execution concurrency EXPLAIN ANALYZE example output

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Set a greater execution concurrency`
- Source Line Ranges: `338-355`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `mpp`, `execution-concurrency`, `explain-analyze`, `hashagg`, `exchange`, `stream-count`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0263_195996a8f6`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#set-a-greater-execution-concurrency`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6c29190da9c3557483eb494a3cd9887927876a940b91b0308656516d2796022c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#set-a-greater-execution-concurrency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting EXPLAIN ANALYZE output for a TiFlash MPP aggregation query and checking execution concurrency through stream_count, tasks, and threads fields.
- Retrieval Keywords: EXPLAIN ANALYZE select a, count(*) from t group by a, HashAgg_40, ExchangeSender_41, ExchangeReceiver_42, stream_count: 20, mpp[tiflash], threads:60, tasks:3, TableFullScan_26, ExchangeType: HashPartition
- Follow-up Guidance: The example shows stream_count: 20 in HashAgg_40, ExchangeReceiver_42, and ExchangeSender_41, together with tiflash_task details such as tasks:3 and threads:60.
- Classification Note: This is classified as performance for TiFlash because the official content is an EXPLAIN ANALYZE example used to observe MPP execution concurrency indicators in query operators.

## Official Source Content

```sql
mysql> explain analyze select a, count(*) from t group by a;
+--------------------------------------+--------------+-----------+--------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+------+
| id                                   | estRows      | actRows   | task         | access object | execution info                                                                                                                                                                                                                                                                                                                             | operator info                                                                                                                 | memory | disk |
+--------------------------------------+--------------+-----------+--------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+------+
| TableReader_44                       | 20.00        | 20        | root         |               | time:357.7ms, loops:2, cop_task: {num: 19, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache_hit_ratio: 0.00}                                                                                                                                                                                                                                 | data:ExchangeSender_43                                                                                                        | N/A    | N/A  |
| └─ExchangeSender_43                  | 20.00        | 20        | mpp[tiflash] |               | tiflash_task:{proc max:355.3ms, min:354.6ms, avg: 355ms, p80:355.3ms, p95:355.3ms, iters:16, tasks:3, threads:60}                                                                                                                                                                                                                          | ExchangeType: PassThrough                                                                                                     | N/A    | N/A  |
|   └─Projection_5                     | 20.00        | 20        | mpp[tiflash] |               | tiflash_task:{proc max:354.3ms, min:353.6ms, avg: 354ms, p80:354.3ms, p95:354.3ms, iters:16, tasks:3, threads:60}                                                                                                                                                                                                                          | test.t.a, Column#22                                                                                                           | N/A    | N/A  |
|     └─Projection_39                  | 20.00        | 20        | mpp[tiflash] |               | tiflash_task:{proc max:354.3ms, min:353.6ms, avg: 354ms, p80:354.3ms, p95:354.3ms, iters:16, tasks:3, threads:60}                                                                                                                                                                                                                          | Column#22, test.t.a                                                                                                           | N/A    | N/A  |
|       └─HashAgg_40                   | 20.00        | 20        | mpp[tiflash] |               | tiflash_task:{proc max:354.3ms, min:353.6ms, avg: 354ms, p80:354.3ms, p95:354.3ms, iters:16, tasks:3, threads:60}                                                                                                                                                                                                                          | group by:test.t.a, funcs:sum(Column#29)->Column#22, funcs:firstrow(test.t.a)->test.t.a, stream_count: 20                      | N/A    | N/A  |
|         └─ExchangeReceiver_42        | 20.00        | 60        | mpp[tiflash] |               | tiflash_task:{proc max:354.3ms, min:353.6ms, avg: 354ms, p80:354.3ms, p95:354.3ms, iters:16, tasks:3, threads:60}                                                                                                                                                                                                                          | stream_count: 20                                                                                                              | N/A    | N/A  |
|           └─ExchangeSender_41        | 20.00        | 60        | mpp[tiflash] |               | tiflash_task:{proc max:349.6ms, min:0s, avg: 116.5ms, p80:349.6ms, p95:349.6ms, iters:3, tasks:3, threads:60}                                                                                                                                                                                                                              | ExchangeType: HashPartition, Hash Cols: [name: test.t.a, collate: binary], stream_count: 20                                   | N/A    | N/A  |
|             └─HashAgg_37             | 20.00        | 60        | mpp[tiflash] |               | tiflash_task:{proc max:347.6ms, min:0s, avg: 115.9ms, p80:347.6ms, p95:347.6ms, iters:3, tasks:3, threads:60}                                                                                                                                                                                                                              | group by:test.t.a, funcs:count(1)->Column#29                                                                                  | N/A    | N/A  |
|               └─TableFullScan_26     | 600000000.00 | 600000000 | mpp[tiflash] | table:t       | tiflash_task:{proc max:36.6ms, min:0s, avg: 12.2ms, p80:36.6ms, p95:36.6ms, iters:9389, tasks:3, threads:60}, tiflash_scan:{dtfile:{total_scanned_packs:73833, total_skipped_packs:418, total_scanned_rows:600001386, total_skipped_rows:3381854, total_rs_index_load_time: 10ms, total_read_time: 61ms}, total_create_snapshot_time: 0ms} | keep order:false                                                                                                              | N/A    | N/A  |
+--------------------------------------+--------------+-----------+--------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+------+
9 rows in set (0.37 sec)
```
