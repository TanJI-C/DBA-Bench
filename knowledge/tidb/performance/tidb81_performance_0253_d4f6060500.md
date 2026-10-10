# Agg pushdown overview and setting before explain example

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Forcibly enable the MPP mode | Tune TiFlash Performance > Tune TiDB parameters > Push down aggregate functions to a position before `Join` or `Union``
- Source Line Ranges: `95-109`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `mpp`, `aggregate-pushdown`, `join`, `union`, `optimizer`, `session-variables`, `explain-analyze`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0253_d4f6060500`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#forcibly-enable-the-mpp-mode`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a367675b9f53447821b5b548977ca80a9b0db1f0f271967d0e92551bb8d941b6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#forcibly-enable-the-mpp-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB session variable that controls pushing aggregate functions before `Join` or `Union` in TiFlash MPP queries and why that can improve performance.
- Retrieval Keywords: tidb_opt_agg_push_down, Push down aggregate functions to a position before `Join` or `Union`, set @@tidb_opt_agg_push_down = ON, aggregate pushdown before Join or Union, HashAgg before HashJoin, MPP mode, optimizer executes the optimization operation
- Follow-up Guidance: The source continues with an example comparing the query plan before and after `tidb_opt_agg_push_down` is enabled.
- Classification Note: This is classified as performance for TiFlash because the content describes an optimizer setting that reduces data processed by `Join` or `Union` to improve query performance.

## Official Source Content

### Push down aggregate functions to a position before `Join` or `Union`

By pushing down aggregate operations to the position before `Join` or `Union`, you can reduce the data to be processed in the `Join` or `Union` operation, thereby improving performance.

The variable [`tidb_opt_agg_push_down`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_agg_push_down) controls whether the optimizer executes the optimization operation of pushing down the aggregate function to the position before `Join` or `Union`. When the aggregate operations are quite slow in the query, you can set this variable to `ON`.

```sql
set @@tidb_opt_agg_push_down = ON;
```

The following example shows the query result before and after the `tidb_opt_agg_push_down` variable is enabled. Before this variable is enabled, the `HashAgg_58` operation is executed following the `HashJoin_41` operation. After this variable is enabled, newly generated `HashAgg_21` and `HashAgg_32` operations are executed before the `HashJoin_76` operation. This significantly reduces the data to be processed by the `Join` operation.

Before `tidb_opt_agg_push_down` is enabled:
