# Distinct optimization explain analyze example

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Enable `Distinct` optimization`
- Source Line Ranges: `204-217`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `distinct`, `explain-analyze`, `hashagg`, `batchcop`, `query-plan`, `aggregation`, `mpp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0257_7472941ba4`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#enable-distinct-optimization`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9aea4ccd1e43bf7606992892a717a144e055fe7e47a4d41025d1f14b4a3efa8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#enable-distinct-optimization
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving an EXPLAIN ANALYZE example for DISTINCT optimization on TiFlash, especially for count(distinct a) with HashAgg and batchCop[tiflash] operators.
- Retrieval Keywords: explain analyze select count(distinct a) from test.t, Enable Distinct optimization, HashAgg_10, HashAgg_6, batchCop[tiflash], TableReader_11, TableFullScan_9, funcs:sum(distinct Column#23)->Column#22, group by:test.t.a, tiflash_task, tiflash_scan
- Follow-up Guidance: 
- Classification Note: This chunk is classified as TiFlash performance content because it shows a query plan and execution metrics for DISTINCT aggregation executed with TiFlash batch coprocessor operators.

## Official Source Content

```sql
mysql> explain analyze select count(distinct a) from test.t;
+-----------------------------+--------------+-----------+-------------------+---------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------+-----------+---------+
| id                          | estRows      | actRows   | task              | access object | execution info                                                                                                                                                                                                                                                                                                                                | operator info                                          | memory    | disk    |
+-----------------------------+--------------+-----------+-------------------+---------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------+-----------+---------+
| HashAgg_10                  | 1.00         | 1         | root              |               | time:233.8ms, loops:2                                                                                                                                                                                                                                                                                                                         | funcs:sum(distinct Column#23)->Column#22               | 2.42 KB   | 0 Bytes |
| └─Projection_12             | 1.00         | 3         | root              |               | time:233.7ms, loops:2, Concurrency:OFF                                                                                                                                                                                                                                                                                                        | cast(test.c.a, decimal(10,0) BINARY)->Column#23        | 380 Bytes | N/A     |
|   └─TableReader_11          | 1.00         | 3         | root              |               | time:233.7ms, loops:2, cop_task: {num: 6, max: 0s, min: 0s, avg: 0s, p95: 0s, copr_cache_hit_ratio: 0.00, distsql_concurrency: 15}                                                                                                                                                                                                            | data:HashAgg_6                                         | 100 Bytes | N/A     |
|     └─HashAgg_6             | 1.00         | 3         | batchCop[tiflash] |               | tiflash_task:{proc max:225.8ms, min:210.7ms, avg: 216.9ms, p80:225.8ms, p95:225.8ms, iters:3, tasks:3, threads:60}                                                                                                                                                                                                                            | group by:test.t.a,                                     | N/A       | N/A     |
|       └─TableFullScan_9     | 600000000.00 | 600000000 | batchCop[tiflash] | table:t       | tiflash_task:{proc max:50.3ms, min:33.7ms, avg: 44.6ms, p80:50.3ms, p95:50.3ms, iters:9387, tasks:3, threads:60}, tiflash_scan:{dtfile:{total_scanned_packs:73833, total_skipped_packs:475, total_scanned_rows:600000000, total_skipped_rows:3852098, total_rs_index_load_time: 0ms, total_read_time: 84ms}, total_create_snapshot_time: 0ms} | keep order:false                                       | N/A       | N/A     |
+-----------------------------+--------------+-----------+-------------------+---------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------+-----------+---------+
5 rows in set, 2 warnings (0.24 sec)
```
