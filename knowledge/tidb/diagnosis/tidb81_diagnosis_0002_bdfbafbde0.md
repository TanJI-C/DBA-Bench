# Diagnose TiKV-side slow data processing

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/analyze-slow-queries.md`
- Source Title: `Analyze Slow Queries`
- Source Heading Path: `Analyze Slow Queries > Analyze system issues > TiKV is slow in data processing | Analyze Slow Queries > Analyze system issues > TiKV is slow in data processing > TiKV instance is busy | Analyze Slow Queries > Analyze system issues > TiKV is slow in data processing > Too many outdated keys`
- Source Line Ranges: `60-112`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`
- Topic Tags: `slow-queries`, `tikv-bottleneck`, `coprocessor`, `explain-analyze`, `slow-log`, `cop-wait`, `outdated-keys`, `processed-keys`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0002_bdfbafbde0`
- Source ID: `tidb-docs-8.1:analyze-slow-queries.md#tikv-is-slow-in-data-processing`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7c1efa76389d7b4b08ef436a66dc4496d93232d8acdb71343bceade95ac437b1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/analyze-slow-queries#tikv-is-slow-in-data-processing
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/analyze-slow-queries.md

## Retrieval Guidance

- Use When: Use this chunk when EXPLAIN ANALYZE or slow log fields indicate the bottleneck is on the TiKV side and you need the official signs for busy TiKV instances or too many outdated keys.
- Retrieval Keywords: TiKV is slow in data processing, cop[tikv], tikv-task, EXPLAIN ANALYZE, Cop_process, Cop_wait, TiKV instance is busy, Max_Addr, Total_keys, Processed_keys, Too many outdated keys, TableFullScan_15, StreamAgg_8
- Follow-up Guidance: After identifying TiKV as the bottleneck, the content says to use Cop_wait to see whether one TiKV instance is busy and to compare Total_keys with Processed_keys to see whether there are too many older-version keys.
- Classification Note: This is classified as diagnosis because the content explains how to recognize TiKV-side slow processing from EXPLAIN ANALYZE and slow log evidence and how to distinguish specific causes.

## Official Source Content

### TiKV is slow in data processing

If TiKV is slow in data processing, you can easily identify it in the result of `EXPLAIN ANALYZE`. In the following example, `StreamAgg_8` and `TableFullScan_15`, two `tikv-task`s (as indicated by `cop[tikv]` in the `task` column), take `170ms` to execute. After subtracting `170ms`, the execution time of TiDB operators account for a very small proportion of the total execution time. This indicates that the bottleneck is in TiKV.

```sql
+----------------------------+---------+---------+-----------+---------------+------------------------------------------------------------------------------+---------------------------------+-----------+------+
| id                         | estRows | actRows | task      | access object | execution info                                                               | operator info                   | memory    | disk |
+----------------------------+---------+---------+-----------+---------------+------------------------------------------------------------------------------+---------------------------------+-----------+------+
| StreamAgg_16               | 1.00    | 1       | root      |               | time:170.08572ms, loops:2                                                     | funcs:count(Column#5)->Column#3 | 372 Bytes | N/A  |
| └─TableReader_17           | 1.00    | 1       | root      |               | time:170.080369ms, loops:2, rpc num: 1, rpc time:17.023347ms, proc keys:28672 | data:StreamAgg_8                | 202 Bytes | N/A  |
|   └─StreamAgg_8            | 1.00    | 1       | cop[tikv] |               | time:170ms, loops:29                                                          | funcs:count(1)->Column#5        | N/A       | N/A  |
|     └─TableFullScan_15     | 7.00    | 28672   | cop[tikv] | table:t       | time:170ms, loops:29                                                          | keep order:false, stats:pseudo  | N/A       | N/A  |
+----------------------------+---------+---------+-----------+---------------+------------------------------------------------------------------------------+---------------------------------+-----------+------
```

In addition, the `Cop_process` and `Cop_wait` fields in the slow log can also help your analysis. In the following example, the total duration of the query is around `180.85ms`, and the largest `coptask` takes `171ms`. This indicates that the bottleneck of this query is on the TiKV side.

For the description of each field in the slow log, see [fields description](https://docs.pingcap.com/tidb/stable/identify-slow-queries#fields-description).

```log
# Query_time: 0.18085
...
# Num_cop_tasks: 1
# Cop_process: Avg_time: 170ms P90_time: 170ms Max_time: 170ms Max_addr: 10.6.131.78
# Cop_wait: Avg_time: 1ms P90_time: 1ms Max_time: 1ms Max_Addr: 10.6.131.78
```

After identifying that TiKV is the bottleneck, you can find out the cause as described in the following sections.
#### TiKV instance is busy

During the execution of a SQL statement, TiDB might fetch data from multiple TiKV instances. If one TiKV instance responds slowly, the overall SQL execution speed is slowed down.

The `Cop_wait` field in the slow log can help you determine this cause.

```log
# Cop_wait: Avg_time: 1ms P90_time: 2ms Max_time: 110ms Max_Addr: 10.6.131.78
```

The log above shows that a `cop-task` sent to the `10.6.131.78` instance waits `110ms` before being executed. It indicates that this instance is busy. You can check the CPU monitoring of that time to confirm the cause.
#### Too many outdated keys

A TiKV instance has much outdated data, which needs to be cleaned up for data scan. This impacts the processing speed.

Check `Total_keys` and `Processed_keys`. If they are greatly different, the TiKV instance has too many keys of the older versions.

```
...
# Total_keys: 2215187529 Processed_keys: 1108056368
...
```
