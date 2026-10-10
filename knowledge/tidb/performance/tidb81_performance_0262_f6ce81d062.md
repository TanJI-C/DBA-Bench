# Set greater execution concurrency example and thread setting

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Set a greater execution concurrency`
- Source Line Ranges: `311-337`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `execution-concurrency`, `mpp`, `explain-analyze`, `session-variables`, `thread-tuning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0262_f6ce81d062`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#set-a-greater-execution-concurrency`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9691d7b4583a2ed71fdcd19b018579c7a671ba327c82889af8e44340cea5b784`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#set-a-greater-execution-concurrency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an example of increasing TiFlash execution concurrency with the session variable `tidb_max_tiflash_threads` and checking `EXPLAIN ANALYZE` MPP operator thread counts.
- Retrieval Keywords: tidb_max_tiflash_threads, set @@tidb_max_tiflash_threads = 20, EXPLAIN ANALYZE, mpp[tiflash], tiflash_task, threads:24, stream_count: 8, HashAgg_40, ExchangeSender_41, TableFullScan_26, select a, count(*) from t group by a
- Follow-up Guidance: After `tidb_max_tiflash_threads` is set to `20`, the source continues with the post-change example output.
- Classification Note: This is classified as TiFlash performance tuning because the official content shows a TiDB session variable used to tune TiFlash execution concurrency and observes thread-related execution details in an MPP query plan.

## Official Source Content

```sql
mysql> explain analyze select a, count(*) from t group by a;
+--------------------------------------+--------------+-----------+--------------+---------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------+--------+------+
| id                                   | estRows      | actRows   | task         | access object | execution info                                                                                                                                                                                                                                                                                                                     | operator info                                                                                                                | memory | disk |
+--------------------------------------+--------------+-----------+--------------+---------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------+--------+------+
| TableReader_44                       | 20.00        | 20        | root         |               | time:655.9ms, loops:2, cop_task: {num: 14, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache_hit_ratio: 0.00}                                                                                                                                                                                                                         | data:ExchangeSender_43                                                                                                       | N/A    | N/A  |
| └─ExchangeSender_43                  | 20.00        | 20        | mpp[tiflash] |               | tiflash_task:{proc max:654.6ms, min:652.4ms, avg: 653.8ms, p80:654.6ms, p95:654.6ms, iters:11, tasks:3, threads:24}                                                                                                                                                                                                                | ExchangeType: PassThrough                                                                                                    | N/A    | N/A  |
|   └─Projection_5                     | 20.00        | 20        | mpp[tiflash] |               | tiflash_task:{proc max:654.3ms, min:651.4ms, avg: 653.1ms, p80:654.3ms, p95:654.3ms, iters:11, tasks:3, threads:24}                                                                                                                                                                                                                | test.t.a, Column#22                                                                                                          | N/A    | N/A  |
|     └─Projection_39                  | 20.00        | 20        | mpp[tiflash] |               | tiflash_task:{proc max:654.3ms, min:651.4ms, avg: 653.1ms, p80:654.3ms, p95:654.3ms, iters:11, tasks:3, threads:24}                                                                                                                                                                                                                | Column#22, test.t.a                                                                                                          | N/A    | N/A  |
|       └─HashAgg_40                   | 20.00        | 20        | mpp[tiflash] |               | tiflash_task:{proc max:654.3ms, min:651.4ms, avg: 653.1ms, p80:654.3ms, p95:654.3ms, iters:11, tasks:3, threads:24}                                                                                                                                                                                                                | group by:test.t.a, funcs:sum(Column#29)->Column#22, funcs:firstrow(test.t.a)->test.t.a, stream_count: 8                      | N/A    | N/A  |
|         └─ExchangeReceiver_42        | 20.00        | 60        | mpp[tiflash] |               | tiflash_task:{proc max:654.3ms, min:651.4ms, avg: 653.1ms, p80:654.3ms, p95:654.3ms, iters:11, tasks:3, threads:24}                                                                                                                                                                                                                | stream_count: 8                                                                                                              | N/A    | N/A  |
|           └─ExchangeSender_41        | 20.00        | 60        | mpp[tiflash] |               | tiflash_task:{proc max:649ms, min:0s, avg: 216.3ms, p80:649ms, p95:649ms, iters:3, tasks:3, threads:24}                                                                                                                                                                                                                            | ExchangeType: HashPartition, Hash Cols: [name: test.t.a, collate: binary], stream_count: 8                                   | N/A    | N/A  |
|             └─HashAgg_37             | 20.00        | 60        | mpp[tiflash] |               | tiflash_task:{proc max:649ms, min:0s, avg: 216.3ms, p80:649ms, p95:649ms, iters:3, tasks:3, threads:24}                                                                                                                                                                                                                            | group by:test.t.a, funcs:count(1)->Column#29                                                                                 | N/A    | N/A  |
|               └─TableFullScan_26     | 600000000.00 | 600000000 | mpp[tiflash] | table:t       | tiflash_task:{proc max:40ms, min:0s, avg: 13.3ms, p80:40ms, p95:40ms, iters:9386, tasks:3, threads:24}, tiflash_scan:{dtfile:{total_scanned_packs:73833, total_skipped_packs:174, total_scanned_rows:600000000, total_skipped_rows:1402537, total_rs_index_load_time: 0ms, total_read_time: 4ms}, total_create_snapshot_time: 0ms} | keep order:false                                                                                                             | N/A    | N/A  |
+--------------------------------------+--------------+-----------+--------------+---------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------+--------+------+
9 rows in set (0.67 sec)
```
Set `tidb_max_tiflash_threads` to `20`:

```sql
mysql> set @@tidb_max_tiflash_threads = 20;
Query OK, 0 rows affected (0.00 sec)
```

After `tidb_max_tiflash_threads` is set to `20`:
