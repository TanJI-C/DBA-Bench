# Broadcast hash join threshold tuning example

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Replace Shuffled Hash Join with Broadcast Hash Join`
- Source Line Ranges: `250-278`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `mpp`, `hash-join`, `broadcast-join`, `execution-plan`, `explain-analyze`, `session-variables`, `thresholds`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0259_176934e01d`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#replace-shuffled-hash-join-with-broadcast-hash-join`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2bcd1fb2790b71e80167338fffa2af2203f4cf1253af84d0e907716ca79671bb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#replace-shuffled-hash-join-with-broadcast-hash-join
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an example of changing an MPP hash join plan from a shuffled hash join to a broadcast hash join by tuning a TiDB session variable and inspecting the result with EXPLAIN ANALYZE.
- Retrieval Keywords: Replace Shuffled Hash Join with Broadcast Hash Join, tidb_broadcast_join_threshold_size, set @@tidb_broadcast_join_threshold_size = 10000000, explain analyze, HashJoin_44, mpp[tiflash], ExchangeType: HashPartition, Broadcast hash join threshold tuning example, supplier lineitem s_suppkey l_suppkey
- Follow-up Guidance: The chunk continues with the state after tidb_broadcast_join_threshold_size is set to 10000000.
- Classification Note: This is classified as TiFlash performance tuning because the official content shows an MPP TiFlash execution plan for a hash join and a TiDB parameter adjustment that affects join distribution behavior.

## Official Source Content

```sql
mysql> explain analyze select max(l_shipdate), max(l_commitdate), max(l_receiptdate) from supplier,lineitem where s_suppkey = l_suppkey;
+------------------------------------------+--------------+-----------+--------------+----------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------+------+
| id                                       | estRows      | actRows   | task         | access object  | execution info                                                                                                                                                                                                                                                                                                                                               | operator info                                                                                                                                                   | memory  | disk |
+------------------------------------------+--------------+-----------+--------------+----------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------+------+
| HashAgg_45                               | 1.00         | 1         | root         |                | time:3.8s, loops:2, partial_worker:{wall_time:3.798284809s, concurrency:5, task_num:1, tot_wait:18.99079929s, tot_exec:8.193µs, tot_time:18.990819019s, max:3.798181723s, p95:3.798181723s}, final_worker:{wall_time:0s, concurrency:5, task_num:1, tot_wait:18.991291379s, tot_exec:197.45µs, tot_time:18.991494363s, max:3.798334972s, p95:3.798334972s}   | funcs:max(Column#28)->Column#25, funcs:max(Column#29)->Column#26, funcs:max(Column#30)->Column#27                                                               | 17.3 KB | N/A  |
| └─TableReader_47                         | 1.00         | 3         | root         |                | time:3.8s, loops:2, cop_task: {num: 6, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache_hit_ratio: 0.00}                                                                                                                                                                                                                                                       | data:ExchangeSender_46                                                                                                                                          | N/A     | N/A  |
|   └─ExchangeSender_46                    | 1.00         | 3         | mpp[tiflash] |                | tiflash_task:{proc max:3.79s, min:3.78s, avg: 3.78s, p80:3.79s, p95:3.79s, iters:3, tasks:3, threads:60}                                                                                                                                                                                                                                                     | ExchangeType: PassThrough                                                                                                                                       | N/A     | N/A  |
|     └─HashAgg_13                         | 1.00         | 3         | mpp[tiflash] |                | tiflash_task:{proc max:3.79s, min:3.78s, avg: 3.78s, p80:3.79s, p95:3.79s, iters:3, tasks:3, threads:60}                                                                                                                                                                                                                                                     | funcs:max(tpch_100.lineitem.l_shipdate)->Column#28, funcs:max(tpch_100.lineitem.l_commitdate)->Column#29, funcs:max(tpch_100.lineitem.l_receiptdate)->Column#30 | N/A     | N/A  |
|       └─HashJoin_44                      | 600845438.27 | 600037902 | mpp[tiflash] |                | tiflash_task:{proc max:3.17s, min:3.12s, avg: 3.14s, p80:3.17s, p95:3.17s, iters:11143, tasks:3, threads:60}                                                                                                                                                                                                                                                 | inner join, equal:[eq(tpch_100.supplier.s_suppkey, tpch_100.lineitem.l_suppkey)], stream_count: 20                                                              | N/A     | N/A  |
|         ├─ExchangeReceiver_30(Build)     | 1000000.00   | 1000000   | mpp[tiflash] |                | tiflash_task:{proc max:23.3ms, min:21ms, avg: 22.5ms, p80:23.3ms, p95:23.3ms, iters:120, tasks:3, threads:60}                                                                                                                                                                                                                                                | stream_count: 20                                                                                                                                                | N/A     | N/A  |
|         │ └─ExchangeSender_29            | 1000000.00   | 1000000   | mpp[tiflash] |                | tiflash_task:{proc max:22.7ms, min:0s, avg: 7.57ms, p80:22.7ms, p95:22.7ms, iters:16, tasks:3, threads:2}                                                                                                                                                                                                                                                    | ExchangeType: HashPartition, Hash Cols: [name: tpch_100.supplier.s_suppkey, collate: binary], stream_count: 20                                                  | N/A     | N/A  |
|         │   └─TableFullScan_28           | 1000000.00   | 1000000   | mpp[tiflash] | table:supplier | tiflash_task:{proc max:9.71ms, min:0s, avg: 3.24ms, p80:9.71ms, p95:9.71ms, iters:16, tasks:3, threads:2}, tiflash_scan:{dtfile:{total_scanned_packs:123, total_skipped_packs:0, total_scanned_rows:1000000, total_skipped_rows:0, total_rs_index_load_time: 0ms, total_read_time: 2ms}, total_create_snapshot_time: 0ms}                                    | keep order:false                                                                                                                                                | N/A     | N/A  |
|         └─ExchangeReceiver_33(Probe)     | 600037902.00 | 600037902 | mpp[tiflash] |                | tiflash_task:{proc max:564.3ms, min:340ms, avg: 438.5ms, p80:564.3ms, p95:564.3ms, iters:27583, tasks:3, threads:60}                                                                                                                                                                                                                                         |                                                                                                                                                                 | N/A     | N/A  |
|           └─ExchangeSender_32            | 600037902.00 | 600037902 | mpp[tiflash] |                | tiflash_task:{proc max:3.69s, min:0s, avg: 1.23s, p80:3.69s, p95:3.69s, iters:9298, tasks:3, threads:60}                                                                                                                                                                                                                                                     | ExchangeType: HashPartition, Hash Cols: [name: tpch_100.lineitem.l_suppkey, collate: binary]                                                                    | N/A     | N/A  |
|             └─TableFullScan_31           | 600037902.00 | 600037902 | mpp[tiflash] | table:lineitem | tiflash_task:{proc max:62.8ms, min:0s, avg: 20.9ms, p80:62.8ms, p95:62.8ms, iters:9298, tasks:3, threads:60}, tiflash_scan:{dtfile:{total_scanned_packs:73465, total_skipped_packs:13060, total_scanned_rows:600168663, total_skipped_rows:106699256, total_rs_index_load_time: 16ms, total_read_time: 27979ms}, total_create_snapshot_time: 0ms}            | keep order:false                                                                                                                                                | N/A     | N/A  |
+------------------------------------------+--------------+-----------+--------------+----------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------+------+
11 rows in set (3.83 sec)
```
Set `tidb_broadcast_join_threshold_size` to `10000000`:

```sql
mysql> set @@tidb_broadcast_join_threshold_size = 10000000;
Query OK, 0 rows affected (0.00 sec)
```

After `tidb_broadcast_join_threshold_size` is set to `10000000`:
