# Broadcast Hash Join explain analyze example

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Replace Shuffled Hash Join with Broadcast Hash Join`
- Source Line Ranges: `279-296`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `mpp`, `hash-join`, `broadcast-join`, `explain-analyze`, `query-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0260_0e5d1c5e12`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#replace-shuffled-hash-join-with-broadcast-hash-join`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `51823bbf35ad119e92754fb8a90c20a20ccd18c91fcb478903b39496a16bbffb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#replace-shuffled-hash-join-with-broadcast-hash-join
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving an EXPLAIN ANALYZE example that shows a TiFlash MPP Broadcast Hash Join plan and its operator details.
- Retrieval Keywords: EXPLAIN ANALYZE, Broadcast Hash Join, Shuffled Hash Join, HashJoin_42, ExchangeType: Broadcast, ExchangeSender_29, ExchangeReceiver_30(Build), mpp[tiflash], supplier, lineitem, s_suppkey, l_suppkey, query plan
- Follow-up Guidance: The example shows the build side using ExchangeType: Broadcast for supplier and the probe side scanning lineitem in an mpp[tiflash] plan.
- Classification Note: This is classified as performance content because the official content is an EXPLAIN ANALYZE query-plan example under replacing Shuffled Hash Join with Broadcast Hash Join in TiFlash.

## Official Source Content

```sql
mysql> explain analyze select max(l_shipdate), max(l_commitdate), max(l_receiptdate) from supplier,lineitem where s_suppkey = l_suppkey;
+------------------------------------------+--------------+-----------+--------------+----------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------+------+
| id                                       | estRows      | actRows   | task         | access object  | execution info                                                                                                                                                                                                                                                                                                                                                         | operator info                                                                                                                                                   | memory  | disk |
+------------------------------------------+--------------+-----------+--------------+----------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------+------+
| HashAgg_43                               | 1.00         | 1         | root         |                | time:2.75s, loops:2, partial_worker:{wall_time:2.748445779s, concurrency:5, task_num:1, tot_wait:13.74202679s, tot_exec:8.012µs, tot_time:13.742045721s, max:2.748414915s, p95:2.748414915s}, final_worker:{wall_time:2.74848039s, concurrency:5, task_num:1, tot_wait:13.742157526s, tot_exec:53.191µs, tot_time:13.742214417s, max:2.748462393s, p95:2.748462393s}   | funcs:max(Column#28)->Column#25, funcs:max(Column#29)->Column#26, funcs:max(Column#30)->Column#27                                                               | 17.3 KB | N/A  |
| └─TableReader_45                         | 1.00         | 3         | root         |                | time:2.75s, loops:2, cop_task: {num: 6, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache_hit_ratio: 0.00}                                                                                                                                                                                                                                                                | data:ExchangeSender_44                                                                                                                                          | N/A     | N/A  |
|   └─ExchangeSender_44                    | 1.00         | 3         | mpp[tiflash] |                | tiflash_task:{proc max:2.74s, min:2.65s, avg: 2.7s, p80:2.74s, p95:2.74s, iters:3, tasks:3, threads:60}                                                                                                                                                                                                                                                                | ExchangeType: PassThrough                                                                                                                                       | N/A     | N/A  |
|     └─HashAgg_13                         | 1.00         | 3         | mpp[tiflash] |                | tiflash_task:{proc max:2.74s, min:2.65s, avg: 2.7s, p80:2.74s, p95:2.74s, iters:3, tasks:3, threads:60}                                                                                                                                                                                                                                                                | funcs:max(tpch_100.lineitem.l_shipdate)->Column#28, funcs:max(tpch_100.lineitem.l_commitdate)->Column#29, funcs:max(tpch_100.lineitem.l_receiptdate)->Column#30 | N/A     | N/A  |
|       └─HashJoin_42                      | 600845438.27 | 600037902 | mpp[tiflash] |                | tiflash_task:{proc max:2.15s, min:2.06s, avg: 2.11s, p80:2.15s, p95:2.15s, iters:9286, tasks:3, threads:60}                                                                                                                                                                                                                                                            | inner join, equal:[eq(tpch_100.supplier.s_suppkey, tpch_100.lineitem.l_suppkey)]                                                                                | N/A     | N/A  |
|         ├─ExchangeReceiver_30(Build)     | 1000000.00   | 3000000   | mpp[tiflash] |                | tiflash_task:{proc max:28.1ms, min:24.9ms, avg: 27ms, p80:28.1ms, p95:28.1ms, iters:48, tasks:3, threads:60}                                                                                                                                                                                                                                                           |                                                                                                                                                                 | N/A     | N/A  |
|         │ └─ExchangeSender_29            | 1000000.00   | 1000000   | mpp[tiflash] |                | tiflash_task:{proc max:14ms, min:0s, avg: 4.67ms, p80:14ms, p95:14ms, iters:16, tasks:3, threads:2}                                                                                                                                                                                                                                                                    | ExchangeType: Broadcast                                                                                                                                         | N/A     | N/A  |
|         │   └─TableFullScan_28           | 1000000.00   | 1000000   | mpp[tiflash] | table:supplier | tiflash_task:{proc max:9ms, min:0s, avg: 3ms, p80:9ms, p95:9ms, iters:16, tasks:3, threads:2}, tiflash_scan:{dtfile:{total_scanned_packs:123, total_skipped_packs:0, total_scanned_rows:1000000, total_skipped_rows:0, total_rs_index_load_time: 0ms, total_read_time: 2ms}, total_create_snapshot_time: 0ms}                                                          | keep order:false                                                                                                                                                | N/A     | N/A  |
|         └─TableFullScan_31(Probe)        | 600037902.00 | 600037902 | mpp[tiflash] | table:lineitem | tiflash_task:{proc max:57.9ms, min:42.9ms, avg: 51.3ms, p80:57.9ms, p95:57.9ms, iters:9297, tasks:3, threads:60}, tiflash_scan:{dtfile:{total_scanned_packs:73464, total_skipped_packs:12985, total_scanned_rows:600169085, total_skipped_rows:106014866, total_rs_index_load_time: 23ms, total_read_time: 21667ms}, total_create_snapshot_time: 0ms}                  | keep order:false                                                                                                                                                | N/A     | N/A  |
+------------------------------------------+--------------+-----------+--------------+----------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------+------+
9 rows in set (2.76 sec)
```
