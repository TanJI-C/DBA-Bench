# Configure tiflash_fine_grained_shuffle_stream_count with EXPLAIN ANALYZE example

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Configure `tiflash_fine_grained_shuffle_stream_count``
- Source Line Ranges: `370-394`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `mpp`, `fine-grained-shuffle`, `stream-count`, `explain-analyze`, `window-function`, `sql-session-variable`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0265_d94724f106`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#configure-tiflash-fine-grained-shuffle-stream-count`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cfaa97288be1c384f5cd93a5047ee13e69ca9ade4505d79469399626a11a0afb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#configure-tiflash-fine-grained-shuffle-stream-count
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an EXPLAIN ANALYZE example that shows how the session variable `tiflash_fine_grained_shuffle_stream_count` appears in TiFlash MPP execution for a window function query.
- Retrieval Keywords: tiflash_fine_grained_shuffle_stream_count, EXPLAIN ANALYZE, row_number() over (partition by a), mpp[tiflash], fine-grained shuffle, stream_count: 8, set @@tiflash_fine_grained_shuffle_stream_count = 20, Window_22, Sort_13, ExchangeSender_11, ExchangeReceiver_12
- Follow-up Guidance: The chunk continues with the result after `tiflash_fine_grained_shuffle_stream_count` is set to `20`.
- Classification Note: This is classified as TiFlash performance tuning because the content demonstrates a TiDB session variable change and compares TiFlash MPP execution details such as `stream_count` in `EXPLAIN ANALYZE` output.

## Official Source Content

```sql
mysql> explain analyze select *, row_number() over (partition by a) from t;
+----------------------------------+--------------+-----------+--------------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+--------+------+
| id                               | estRows      | actRows   | task         | access object | execution info                                                                                                                                                                                                                                                                                                                                  | operator info                                                                                                        | memory | disk |
+----------------------------------+--------------+-----------+--------------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+--------+------+
| TableReader_24                   | 600000000.00 | 600000000 | root         |               | time:4m30.5s, loops:585941, cop_task: {num: 9163, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache_hit_ratio: 0.00}                                                                                                                                                                                                                               | data:ExchangeSender_23                                                                                               | N/A    | N/A  |
| └─ExchangeSender_23              | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:4m30.5s, min:3m4.8s, avg: 3m36.1s, p80:4m30.5s, p95:4m30.5s, iters:9160, tasks:3, threads:24}                                                                                                                                                                                                                            | ExchangeType: PassThrough                                                                                            | N/A    | N/A  |
|   └─Window_22                    | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:3m31.6s, min:2m26.2s, avg: 2m50.7s, p80:3m31.6s, p95:3m31.6s, iters:9160, tasks:3, threads:24}                                                                                                                                                                                                                           | row_number()->Column#23 over(partition by test.t.a rows between current row and current row), stream_count: 8        | N/A    | N/A  |
|     └─Sort_13                    | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:3m28.6s, min:2m24.2s, avg: 2m48.4s, p80:3m28.6s, p95:3m28.6s, iters:9160, tasks:3, threads:24}                                                                                                                                                                                                                           | test.t.a, stream_count: 8                                                                                            | N/A    | N/A  |
|       └─ExchangeReceiver_12      | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:32.4s, min:32s, avg: 32.1s, p80:32.4s, p95:32.4s, iters:49307, tasks:3, threads:24}                                                                                                                                                                                                                                      | stream_count: 8                                                                                                      | N/A    | N/A  |
|         └─ExchangeSender_11      | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:32s, min:0s, avg: 10.7s, p80:32s, p95:32s, iters:9386, tasks:3, threads:60}                                                                                                                                                                                                                                              | ExchangeType: HashPartition, Hash Cols: [name: test.t.a, collate: binary], stream_count: 8                           | N/A    | N/A  |
|           └─TableFullScan_10     | 600000000.00 | 600000000 | mpp[tiflash] | table:t       | tiflash_task:{proc max:113.9ms, min:0s, avg: 38ms, p80:113.9ms, p95:113.9ms, iters:9386, tasks:3, threads:60}, tiflash_scan:{dtfile:{total_scanned_packs:73834, total_skipped_packs:190, total_scanned_rows:600000000, total_skipped_rows:1536382, total_rs_index_load_time: 16ms, total_read_time: 166324ms}, total_create_snapshot_time: 0ms} | keep order:false                                                                                                     | N/A    | N/A  |
+----------------------------------+--------------+-----------+--------------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+--------+------+
7 rows in set (4 min 30.59 sec)
```

Set `tiflash_fine_grained_shuffle_stream_count` to `20`:

```sql
mysql> set @@tiflash_fine_grained_shuffle_stream_count = 20;
Query OK, 0 rows affected (0.00 sec)
```

After `tiflash_fine_grained_shuffle_stream_count` is set to `20`:
