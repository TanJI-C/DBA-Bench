# Agg pushdown explain analyze example and enable command

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Push down aggregate functions to a position before `Join` or `Union``
- Source Line Ranges: `110-140`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `mpp`, `aggregate-pushdown`, `hashagg`, `hashjoin`, `explain-analyze`, `execution-plan`, `session-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0254_c15be6bd1c`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#push-down-aggregate-functions-to-a-position-before-join-or-union`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7722a6aee01e4189e585e3b0148553d6de337642d5eb4c84a8e4b571b0e0e7e8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#push-down-aggregate-functions-to-a-position-before-join-or-union
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when searching for an `EXPLAIN ANALYZE` example that shows the TiFlash MPP execution plan before enabling `tidb_opt_agg_push_down` and the SQL command to enable it.
- Retrieval Keywords: explain analyze select count(*) from t1 join t2 where t1.a = t2.b group by t1.a, tidb_opt_agg_push_down, mysql> set @@tidb_opt_agg_push_down = ON, HashAgg_58, HashJoin_41, mpp[tiflash], ExchangeSender_65, TableReader_66, TableFullScan_19, TableFullScan_23
- Follow-up Guidance: The source continues with the query plan after `tidb_opt_agg_push_down` is enabled.
- Classification Note: This is classified as performance for TiFlash because it provides an execution-plan example used to observe aggregate pushdown behavior in TiFlash MPP queries.

## Official Source Content

```sql
mysql> explain analyze select count(*) from t1 join t2 where t1.a = t2.b group by t1.a;
+------------------------------------------+--------------+-----------+--------------+---------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+------+
| id                                       | estRows      | actRows   | task         | access object | execution info                                                                                                                                                                                                                                                                                                                                | operator info                                                                                      | memory | disk |
+------------------------------------------+--------------+-----------+--------------+---------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+------+
| TableReader_66                           | 100450000.00 | 20        | root         |               | time:2.13s, loops:2, cop_task: {num: 21, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache_hit_ratio: 0.00}                                                                                                                                                                                                                                      | data:ExchangeSender_65                                                                             | N/A    | N/A  |
| └─ExchangeSender_65                      | 100450000.00 | 20        | mpp[tiflash] |               | tiflash_task:{proc max:2.13s, min:2.08s, avg: 2.11s, p80:2.13s, p95:2.13s, iters:768, tasks:3, threads:60}                                                                                                                                                                                                                                    | ExchangeType: PassThrough                                                                          | N/A    | N/A  |
|   └─Projection_60                        | 100450000.00 | 20        | mpp[tiflash] |               | tiflash_task:{proc max:2.13s, min:2.08s, avg: 2.11s, p80:2.13s, p95:2.13s, iters:768, tasks:3, threads:60}                                                                                                                                                                                                                                    | Column#43                                                                                          | N/A    | N/A  |
|     └─HashAgg_58                         | 100450000.00 | 20        | mpp[tiflash] |               | tiflash_task:{proc max:2.13s, min:2.08s, avg: 2.11s, p80:2.13s, p95:2.13s, iters:768, tasks:3, threads:60}                                                                                                                                                                                                                                    | group by:test.t1.a, funcs:count(1)->Column#43                                                      | N/A    | N/A  |
|       └─HashJoin_41                      | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:1.77s, min:1.67s, avg: 1.73s, p80:1.77s, p95:1.77s, iters:10955, tasks:3, threads:60}                                                                                                                                                                                                                                  | inner join, equal:[eq(test.t1.a, test.t2.b)], stream_count: 20                                     | N/A    | N/A  |
|         ├─ExchangeReceiver_22(Build)     | 100450000.00 | 99980000  | mpp[tiflash] |               | tiflash_task:{proc max:171ms, min:127ms, avg: 154.5ms, p80:171ms, p95:171ms, iters:10440, tasks:3, threads:60}                                                                                                                                                                                                                                | stream_count: 20                                                                                   | N/A    | N/A  |
|         │ └─ExchangeSender_21            | 100450000.00 | 99980000  | mpp[tiflash] |               | tiflash_task:{proc max:498.7ms, min:0s, avg: 166.2ms, p80:498.7ms, p95:498.7ms, iters:1653, tasks:3, threads:60}                                                                                                                                                                                                                              | ExchangeType: HashPartition, Hash Cols: [name: test.t1.a, collate: binary], stream_count: 20       | N/A    | N/A  |
|         │   └─Selection_20               | 100450000.00 | 99980000  | mpp[tiflash] |               | tiflash_task:{proc max:83.7ms, min:0s, avg: 27.9ms, p80:83.7ms, p95:83.7ms, iters:1653, tasks:3, threads:60}                                                                                                                                                                                                                                  | not(isnull(test.t1.a))                                                                             | N/A    | N/A  |
|         │     └─TableFullScan_19         | 100450000.00 | 99980000  | mpp[tiflash] | table:t1      | tiflash_task:{proc max:41.7ms, min:0s, avg: 13.9ms, p80:41.7ms, p95:41.7ms, iters:1653, tasks:3, threads:60}, tiflash_scan:{dtfile:{total_scanned_packs:12336, total_skipped_packs:5759, total_scanned_rows:100083566, total_skipped_rows:46786721, total_rs_index_load_time: 5ms, total_read_time: 1105ms}, total_create_snapshot_time: 0ms} | keep order:false                                                                                   | N/A    | N/A  |
|         └─ExchangeReceiver_26(Probe)     | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:373ms, min:71ms, avg: 253.2ms, p80:373ms, p95:373ms, iters:28135, tasks:3, threads:60}                                                                                                                                                                                                                                 |                                                                                                    | N/A    | N/A  |
|           └─ExchangeSender_25            | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:2.07s, min:0s, avg: 689.6ms, p80:2.07s, p95:2.07s, iters:9388, tasks:3, threads:60}                                                                                                                                                                                                                                    | ExchangeType: HashPartition, Hash Cols: [name: test.t2.b, collate: binary]                         | N/A    | N/A  |
|             └─Selection_24               | 600000000.00 | 600000000 | mpp[tiflash] |               | tiflash_task:{proc max:146.9ms, min:0s, avg: 49ms, p80:146.9ms, p95:146.9ms, iters:9388, tasks:3, threads:60}                                                                                                                                                                                                                                 | not(isnull(test.t2.b))                                                                             | N/A    | N/A  |
|               └─TableFullScan_23         | 600000000.00 | 600000000 | mpp[tiflash] | table:t2      | tiflash_task:{proc max:63.8ms, min:0s, avg: 21.3ms, p80:63.8ms, p95:63.8ms, iters:9388, tasks:3, threads:60}, tiflash_scan:{dtfile:{total_scanned_packs:73834, total_skipped_packs:439, total_scanned_rows:600007458, total_skipped_rows:3553131, total_rs_index_load_time: 12ms, total_read_time: 270ms}, total_create_snapshot_time: 0ms}   | keep order:false                                                                                   | N/A    | N/A  |
+------------------------------------------+--------------+-----------+--------------+---------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+------+
13 rows in set (2.15 sec)
```
Enable `tidb_opt_agg_push_down`:

```sql
mysql> set @@tidb_opt_agg_push_down = ON;
Query OK, 0 rows affected (0.00 sec)
```

After `tidb_opt_agg_push_down` is enabled:
