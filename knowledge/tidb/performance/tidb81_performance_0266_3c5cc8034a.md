# EXPLAIN ANALYZE output for fine-grained shuffle stream count

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Configure `tiflash_fine_grained_shuffle_stream_count``
- Source Line Ranges: `395-409`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `mpp`, `explain-analyze`, `window-functions`, `shuffle`, `stream-count`, `query-execution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0266_3c5cc8034a`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#configure-tiflash-fine-grained-shuffle-stream-count`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a2cc9fc55a8395a910e02757bf9dbcfb40752c6a25fc1ee4905afc663c4840dd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#configure-tiflash-fine-grained-shuffle-stream-count
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when identifying how EXPLAIN ANALYZE displays fine-grained shuffle stream count in a TiFlash MPP query with a window function.
- Retrieval Keywords: EXPLAIN ANALYZE, row_number() over (partition by a), tiflash_fine_grained_shuffle_stream_count, stream_count: 20, mpp[tiflash], Window_22, Sort_13, ExchangeReceiver_12, ExchangeSender_11, ExchangeType: HashPartition, TableFullScan_10
- Follow-up Guidance: The EXPLAIN ANALYZE output shows stream_count: 20 in the Window, Sort, ExchangeReceiver, and HashPartition ExchangeSender operators for the query select *, row_number() over (partition by a) from t.
- Classification Note: This is classified as performance for TiFlash because the official content is an EXPLAIN ANALYZE example used to inspect MPP query execution details related to fine-grained shuffle stream count.

## Official Source Content

```sql
mysql> explain analyze select *, row_number() over (partition by a) from t;
+----------------------------------+--------------+-----------+--------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------+--------+------+
| id                               | estRows      | actRows   | task         | access object | execution info                                                                                                                                                                                                                                                                                                                                    | operator info                                                                                                         | memory | disk |
+----------------------------------+--------------+-----------+--------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------+--------+------+
| TableReader_24                   | 600000000.00 | 600000000 | root         |               | time:2m55s, loops:585941, cop_task: {num: 9163, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache_hit_ratio: 0.00}                                                                                                                                                                                                                                   | data:ExchangeSender_23                                                                                                | N/A    | N/A  |
| └─ExchangeSender_23              | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:2m55s, min:1m37s, avg: 2m28.7s, p80:2m55s, p95:2m55s, iters:9160, tasks:3, threads:60}                                                                                                                                                                                                                                     | ExchangeType: PassThrough                                                                                             | N/A    | N/A  |
|   └─Window_22                    | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:2m12.9s, min:1m17s, avg: 1m54.2s, p80:2m12.9s, p95:2m12.9s, iters:9160, tasks:3, threads:60}                                                                                                                                                                                                                               | row_number()->Column#23 over(partition by test.t.a rows between current row and current row), stream_count: 20        | N/A    | N/A  |
|     └─Sort_13                    | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:2m10.9s, min:1m16s, avg: 1m52.5s, p80:2m10.9s, p95:2m10.9s, iters:9160, tasks:3, threads:60}                                                                                                                                                                                                                               | test.t.a, stream_count: 20                                                                                            | N/A    | N/A  |
|       └─ExchangeReceiver_12      | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:27.2s, min:25.5s, avg: 26.6s, p80:27.2s, p95:27.2s, iters:49602, tasks:3, threads:60}                                                                                                                                                                                                                                      | stream_count: 20                                                                                                      | N/A    | N/A  |
|         └─ExchangeSender_11      | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:25.5s, min:0s, avg: 8.51s, p80:25.5s, p95:25.5s, iters:9388, tasks:3, threads:60}                                                                                                                                                                                                                                          | ExchangeType: HashPartition, Hash Cols: [name: test.t.a, collate: binary], stream_count: 20                           | N/A    | N/A  |
|           └─TableFullScan_10     | 600000000.00 | 600000000 | mpp[tiflash] | table:t       | tiflash_task:{proc max:167.3ms, min:0s, avg: 55.8ms, p80:167.3ms, p95:167.3ms, iters:9388, tasks:3, threads:60}, tiflash_scan:{dtfile:{total_scanned_packs:73834, total_skipped_packs:408, total_scanned_rows:600002896, total_skipped_rows:3307316, total_rs_index_load_time: 20ms, total_read_time: 179431ms}, total_create_snapshot_time: 0ms} | keep order:false                                                                                                      | N/A    | N/A  |
+----------------------------------+--------------+-----------+--------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------+--------+------+
7 rows in set (2 min 55.09 sec)
```
