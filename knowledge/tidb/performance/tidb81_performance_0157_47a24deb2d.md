# Runtime Filter performance comparison and best practices

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/runtime-filter.md`
- Source Title: `Runtime Filter`
- Source Heading Path: `Runtime Filter > Use Runtime Filter > Step 4. Performance comparison | Runtime Filter > Use Runtime Filter > Best practices`
- Source Line Ranges: `203-233`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `runtime filter`, `mpp`, `hash join`, `table scan`, `io reduction`, `query performance`, `fact table`, `dimension table`, `best practices`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0157_47a24deb2d`
- Source ID: `tidb-docs-8.1:runtime-filter.md#step-4-performance-comparison`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ca21631024d9c8254affa7599e06f37f871e3f1aa328fa58f1c966642b77a176`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/runtime-filter#step-4-performance-comparison
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/runtime-filter.md

## Retrieval Guidance

- Use When: Use this chunk when looking for Runtime Filter performance effects in TiFlash MPP hash join plans and the documented best-practice scenario for fact table and dimension table joins.
- Retrieval Keywords: Runtime Filter performance comparison, EXPLAIN ANALYZE, HashJoin_48, runtime filter:0[IN], TableFullScan total_scanned_rows, IO reduction, HashJoin execution duration reduced from 376.1 ms to 157.6 ms, mpp[tiflash], catalog_sales, date_dim, fact table and dimension table join, TPC-DS Sales table and date_dim table
- Follow-up Guidance: The source says Runtime Filter is applicable when a large table and a small table are joined and the dimension table has a small amount of hit data, which helps the fact table filter out more nonmatching data and improve query performance.
- Classification Note: This is classified as performance because the official content compares EXPLAIN ANALYZE execution information, including total_scanned_rows and HashJoin duration, and summarizes best practices for improving query performance.

## Official Source Content

```sql
EXPLAIN ANALYZE SELECT cs_ship_date_sk FROM catalog_sales, date_dim
    -> WHERE d_date = '2002-2-01' AND
    ->      cs_ship_date_sk = d_date_sk;
+----------------------------------------+-------------+---------+--------------+---------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+---------+------+
| id                                     | estRows     | actRows | task         | access object       | execution info                                                                                                                                                                                                                                                                                                                                                                                       | operator info                                                                                                                                 | memory  | disk |
+----------------------------------------+-------------+---------+--------------+---------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+---------+------+
| TableReader_53                         | 37343.19    | 59574   | root         |                     | time:162.1ms, loops:82, RU:0.000000, cop_task: {num: 47, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache_hit_ratio: 0.00}                                                                                                                                                                                                                                                                             | MppVersion: 1, data:ExchangeSender_52                                                                                                         | 12.7 KB | N/A  |
| └─ExchangeSender_52                    | 37343.19    | 59574   | mpp[tiflash] |                     | tiflash_task:{proc max:160.8ms, min:154.3ms, avg: 157.6ms, p80:160.8ms, p95:160.8ms, iters:86, tasks:2, threads:16}                                                                                                                                                                                                                                                                                  | ExchangeType: PassThrough                                                                                                                     | N/A     | N/A  |
|   └─Projection_51                      | 37343.19    | 59574   | mpp[tiflash] |                     | tiflash_task:{proc max:160.8ms, min:154.3ms, avg: 157.6ms, p80:160.8ms, p95:160.8ms, iters:86, tasks:2, threads:16}                                                                                                                                                                                                                                                                                  | tpcds50.catalog_sales.cs_ship_date_sk                                                                                                         | N/A     | N/A  |
|     └─HashJoin_48                      | 37343.19    | 59574   | mpp[tiflash] |                     | tiflash_task:{proc max:160.8ms, min:154.3ms, avg: 157.6ms, p80:160.8ms, p95:160.8ms, iters:86, tasks:2, threads:16}                                                                                                                                                                                                                                                                                  | inner join, equal:[eq(tpcds50.date_dim.d_date_sk, tpcds50.catalog_sales.cs_ship_date_sk)], runtime filter:0[IN] <- tpcds50.date_dim.d_date_sk | N/A     | N/A  |
|       ├─ExchangeReceiver_29(Build)     | 1.00        | 2       | mpp[tiflash] |                     | tiflash_task:{proc max:132.3ms, min:130.8ms, avg: 131.6ms, p80:132.3ms, p95:132.3ms, iters:2, tasks:2, threads:16}                                                                                                                                                                                                                                                                                   |                                                                                                                                               | N/A     | N/A  |
|       │ └─ExchangeSender_28            | 1.00        | 1       | mpp[tiflash] |                     | tiflash_task:{proc max:131ms, min:0s, avg: 65.5ms, p80:131ms, p95:131ms, iters:1, tasks:2, threads:1}                                                                                                                                                                                                                                                                                                | ExchangeType: Broadcast, Compression: FAST                                                                                                    | N/A     | N/A  |
|       │   └─TableFullScan_26           | 1.00        | 1       | mpp[tiflash] | table:date_dim      | tiflash_task:{proc max:3.01ms, min:0s, avg: 1.51ms, p80:3.01ms, p95:3.01ms, iters:1, tasks:2, threads:1}, tiflash_scan:{dtfile:{total_scanned_packs:2, total_skipped_packs:12, total_scanned_rows:16384, total_skipped_rows:97625, total_rs_index_load_time: 0ms, total_read_time: 0ms}, total_create_snapshot_time: 0ms, total_local_region_num: 1, total_remote_region_num: 0}                     | pushed down filter:eq(tpcds50.date_dim.d_date, 2002-02-01 00:00:00.000000), keep order:false                                                  | N/A     | N/A  |
|       └─Selection_31(Probe)            | 71638034.00 | 5308995 | mpp[tiflash] |                     | tiflash_task:{proc max:39.8ms, min:24.3ms, avg: 32.1ms, p80:39.8ms, p95:39.8ms, iters:86, tasks:2, threads:16}                                                                                                                                                                                                                                                                                       | not(isnull(tpcds50.catalog_sales.cs_ship_date_sk))                                                                                            | N/A     | N/A  |
|         └─TableFullScan_30             | 71997669.00 | 5335549 | mpp[tiflash] | table:catalog_sales | tiflash_task:{proc max:36.8ms, min:23.3ms, avg: 30.1ms, p80:36.8ms, p95:36.8ms, iters:86, tasks:2, threads:16}, tiflash_scan:{dtfile:{total_scanned_packs:660, total_skipped_packs:12451, total_scanned_rows:5335549, total_skipped_rows:100905778, total_rs_index_load_time: 2ms, total_read_time: 47ms}, total_create_snapshot_time: 0ms, total_local_region_num: 194, total_remote_region_num: 0} | pushed down filter:empty, keep order:false, runtime filter:0[IN] -> tpcds50.catalog_sales.cs_ship_date_sk                                     | N/A     | N/A  |
+----------------------------------------+-------------+---------+--------------+---------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------+---------+------+
9 rows in set (0.17 sec)
```
By comparing the execution information of the two queries, you can find the following improvements:

* IO reduction: by comparing the `total_scanned_rows` of the TableFullScan operator, you can see that the scan volume of `TableFullScan` is reduced by 2/3 after Runtime Filter is enabled.
* Hash join performance improvement: the execution duration of the `HashJoin` operator is reduced from 376.1 ms to 157.6 ms.
### Best practices

Runtime Filter is applicable to the scenario where a large table and a small table are joined, such as a join query of a fact table and a dimension table. When the dimension table has a small amount of hit data, it means that the filter has fewer values, so the fact table can filter out the data that does not meet the conditions more effectively. Compared with the default scenario where the entire fact table is scanned, this significantly improves the query performance.

The join operation of the `Sales` table and the `date_dim` table in TPC-DS is a typical example.
