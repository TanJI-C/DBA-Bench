# TiDB parameter tuning for TiFlash MPP mode

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters | Tune TiFlash Performance > Tune TiDB parameters > Forcibly enable the MPP mode`
- Source Line Ranges: `14-39`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`, `sql`
- Topic Tags: `mpp`, `session-variables`, `optimizer`, `query-execution`, `join-pushdown`, `aggregation-pushdown`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0359_8fee10dcf6`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#tune-tidb-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2e400e9b55a40bb3b738016e7c7fb2d8ddde127c9b2dee450a1c5ebabe6d0c85`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#tune-tidb-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when asking how TiDB parameters affect TiFlash MPP execution plans, including forcibly enabling MPP mode and related TiFlash tuning topics.
- Retrieval Keywords: Tune TiDB parameters, Forcibly enable the MPP mode, MPP execution plans, tidb_enforce_mpp, set @@tidb_enforce_mpp = ON;, Join, Aggregation, Push down aggregate functions to a position before Join or Union, Enable Distinct optimization, ALTER TABLE ... COMPACT, Replace Shuffled Hash Join with Broadcast Hash Join, Set a greater execution concurrency, tiflash_fine_grained_shuffle_stream_count
- Follow-up Guidance: This source states that enabling `tidb_enforce_mpp` can force the optimizer to generate MPP execution plans and push `Join` and `Aggregation` down to TiFlash when the optimizer does not generate an MPP plan.
- Classification Note: The classification is configuration for the TiDB component because the content centers on tuning TiDB parameters and session variables that influence TiFlash query execution behavior.

## Official Source Content

## Tune TiDB parameters

This section describes how to improve TiFlash performance by tuning TiDB parameters, including:

- [Forcibly enable the MPP mode](#forcibly-enable-the-mpp-mode)
- [Push down aggregate functions to a position before `Join` or `Union`](#push-down-aggregate-functions-to-a-position-before-join-or-union)
- [Enable `Distinct` optimization](#enable-distinct-optimization)
- [Compact data using the `ALTER TABLE ... COMPACT` statement](#compact-data-using-the-alter-table--compact-statement)
- [Replace Shuffled Hash Join with Broadcast Hash Join](#replace-shuffled-hash-join-with-broadcast-hash-join)
- [Set a greater execution concurrency](#set-a-greater-execution-concurrency)
- [Configure `tiflash_fine_grained_shuffle_stream_count`](#configure-tiflash_fine_grained_shuffle_stream_count)
### Forcibly enable the MPP mode

MPP execution plans can fully utilize distributed computing resources, thereby significantly improving the efficiency of batch data queries. When the optimizer does not generate an MPP execution plan for a query, you can forcibly enable the MPP mode:

The variable [`tidb_enforce_mpp`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enforce_mpp-new-in-v51) controls whether to ignore the optimizer's cost estimation and to forcibly use TiFlash's MPP mode for query execution. To enable MPP mode forcibly, run the following command:

```sql
set @@tidb_enforce_mpp = ON;
```

The following example shows the query result before and after `tidb_enforce_mpp` is enabled. Before this variable is enabled, TiDB needs to read data from TiKV and execute `Join` and `Aggregation` in TiDB. After `tidb_enforce_mpp` is enabled, `Join` and `Aggregation` are pushed down to TiFlash. In addition, because the optimizer does not necessarily generate MPP execution plans, by enabling `tidb_enforce_mpp`, you can force the optimizer to generate MPP execution plans.

Before MPP mode is enabled:
