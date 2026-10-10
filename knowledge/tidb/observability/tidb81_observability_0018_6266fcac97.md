# Check Coprocessor Cache effect with EXPLAIN ANALYZE and Grafana

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/coprocessor-cache.md`
- Source Title: `Coprocessor Cache`
- Source Heading Path: `Coprocessor Cache > Check the cache effect | Coprocessor Cache > Check the cache effect > Use `EXPLAIN ANALYZE` | Coprocessor Cache > Check the cache effect > View the Grafana monitoring panel`
- Source Line Ranges: `46-70`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`, `tikv`
- Topic Tags: `cache-hit-rate`, `explain-analyze`, `grafana`, `monitoring`, `distsql`, `execution-info`, `copr-cache`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0018_6266fcac97`
- Source ID: `tidb-docs-8.1:coprocessor-cache.md#check-the-cache-effect`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9c0a96f039d7f8a2326722f7005f8158c072cc8c88099bc51f1454fe8675f07`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/coprocessor-cache#check-the-cache-effect
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/coprocessor-cache.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about how to observe Coprocessor Cache hit rate or cluster-wide cache hits, misses, and discards.
- Retrieval Keywords: EXPLAIN ANALYZE, execution info, copr_cache_hit_rate, copr_cache_hit_ratio, Operators for accessing tables, IndexLookUp_6, cop_task, Grafana, copr-cache panel, distsql subsystem, tidb namespace, hits misses cache discards
- Follow-up Guidance: The source gives an `EXPLAIN ANALYZE SELECT * FROM t USE INDEX(a);` example where `0.75` means the Coprocessor Cache hit rate is about 75%.
- Classification Note: This is classified as observability because the supplied content focuses on checking Coprocessor Cache effect through `EXPLAIN ANALYZE` output and Grafana monitoring panels.

## Official Source Content

## Check the cache effect

You can check the cache effect of Coprocessor by executing `EXPLAIN ANALYZE` or viewing the Grafana monitoring panel.
### Use `EXPLAIN ANALYZE`

You can view the cache hit rate in [Operators for accessing tables](https://docs.pingcap.com/tidb/stable/choose-index#operators-for-accessing-tables) by using the [`EXPLAIN ANALYZE` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze). See the following example:

```sql
EXPLAIN ANALYZE SELECT * FROM t USE INDEX(a);
+-------------------------------+-----------+---------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+-----------------------+------+
| id                            | estRows   | actRows | task      | access object          | execution info                                                                                                                                                                                                                                           | operator info                  | memory                | disk |
+-------------------------------+-----------+---------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+-----------------------+------+
| IndexLookUp_6                 | 262400.00 | 262400  | root      |                        | time:620.513742ms, loops:258, cop_task: {num: 4, max: 5.530817ms, min: 1.51829ms, avg: 2.70883ms, p95: 5.530817ms, max_proc_keys: 2480, p95_proc_keys: 2480, tot_proc: 1ms, tot_wait: 1ms, rpc_num: 4, rpc_time: 10.816328ms, copr_cache_hit_rate: 0.75} |                                | 6.685169219970703 MB  | N/A  |
| ├─IndexFullScan_4(Build)      | 262400.00 | 262400  | cop[tikv] | table:t, index:a(a, c) | proc max:93ms, min:1ms, p80:93ms, p95:93ms, iters:275, tasks:4                                                                                                                                                                                           | keep order:false, stats:pseudo | 1.7549400329589844 MB | N/A  |
| └─TableRowIDScan_5(Probe)     | 262400.00 | 0       | cop[tikv] | table:t                | time:0ns, loops:0                                                                                                                                                                                                                                        | keep order:false, stats:pseudo | N/A                   | N/A  |
+-------------------------------+-----------+---------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+-----------------------+------+
3 rows in set (0.62 sec)
```

The column `execution info` of the execution result gives the `copr_cache_hit_ratio` information, which indicates the hit rate of the Coprocessor Cache. The `0.75` in the above example means that the hit rate is about 75%.
### View the Grafana monitoring panel

In Grafana, you can see the **copr-cache** panel in the `distsql` subsystem under the `tidb` namespace. This panel monitors the number of hits, misses, and cache discards of the Coprocessor Cache in the entire cluster.
