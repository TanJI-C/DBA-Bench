# Aggregation optimizer hints and MPP aggregation modes

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Hints that take effect in query blocks > HASH_AGG() | Optimizer Hints > Hints that take effect in query blocks > STREAM_AGG() | Optimizer Hints > Hints that take effect in query blocks > MPP_1PHASE_AGG() | Optimizer Hints > Hints that take effect in query blocks > MPP_2PHASE_AGG()`
- Source Line Ranges: `367-410`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tiflash`
- Topic Tags: `optimizer-hints`, `aggregation`, `hash-agg`, `stream-agg`, `mpp`, `tiflash`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0124_afc3167e8c`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#hash-agg`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `098d584a7b41b1df8de0fea18a54f1b74207ecde8fd981ee57c9f9656b51f658`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#hash-agg
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when looking for optimizer hints that control aggregation algorithms, including HASH_AGG(), STREAM_AGG(), MPP_1PHASE_AGG(), and MPP_2PHASE_AGG().
- Retrieval Keywords: HASH_AGG(), STREAM_AGG(), MPP_1PHASE_AGG(), MPP_2PHASE_AGG(), hash aggregation, stream aggregation, one-phase aggregation, two-phase aggregation, MPP mode, TiFlash MPP mode, aggregate functions, GROUP BY
- Follow-up Guidance: The source notes that MPP_1PHASE_AGG() and MPP_2PHASE_AGG() only take effect in MPP mode and refers to Use TiFlash MPP Mode for cluster support details.
- Classification Note: This is classified as performance content because it describes optimizer hints that select aggregation algorithms and MPP aggregation modes for query execution.

## Official Source Content

### HASH_AGG()

The `HASH_AGG()` hint tells the optimizer to use the hash aggregation algorithm in all the aggregate functions in the specified query block. This algorithm allows the query to be executed concurrently with multiple threads, which achieves a higher processing speed but consumes more memory. For example:

```sql
select /*+ HASH_AGG() */ count(*) from t1, t2 where t1.a > 10 group by t1.id;
```
### STREAM_AGG()

The `STREAM_AGG()` hint tells the optimizer to use the stream aggregation algorithm in all the aggregate functions in the specified query block. Generally, this algorithm consumes less memory but takes longer processing time. If there is a very large data volume or insufficient system memory, it is recommended to use this hint. For example:

```sql
select /*+ STREAM_AGG() */ count(*) from t1, t2 where t1.a > 10 group by t1.id;
```
### MPP_1PHASE_AGG()

`MPP_1PHASE_AGG()` tells the optimizer to use the one-phase aggregation algorithm for all aggregate functions in the specified query block. This hint only takes effect in the MPP mode. For example:

```sql
SELECT /*+ MPP_1PHASE_AGG() */ COUNT(*) FROM t1, t2 WHERE t1.a > 10 GROUP BY t1.id;
```

> **Note:**
>
> Before using this hint, make sure that the current TiDB cluster can support using TiFlash MPP mode in the query. For details, refer to [Use TiFlash MPP Mode](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode).
### MPP_2PHASE_AGG()

`MPP_2PHASE_AGG()` tells the optimizer to use the two-phase aggregation algorithm for all aggregate functions in the specified query block. This hint only takes effect in the MPP mode. For example:

```sql
SELECT /*+ MPP_2PHASE_AGG() */ COUNT(*) FROM t1, t2 WHERE t1.a > 10 GROUP BY t1.id;
```

> **Note:**
>
> Before using this hint, make sure that the current TiDB cluster can support using TiFlash MPP mode in the query. For details, refer to [Use TiFlash MPP Mode](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode).
