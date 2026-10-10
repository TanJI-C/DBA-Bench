# Configure fine-grained shuffle stream count for window functions

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Configure `tiflash_fine_grained_shuffle_stream_count``
- Source Line Ranges: `356-369`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `fine-grained-shuffle`, `window-functions`, `stream-count`, `system-variables`, `concurrency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0264_89b5bb424e`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#configure-tiflash-fine-grained-shuffle-stream-count`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `58a5c31ea883cf62b0cd01f4e939ac923d19ece123e2da885029daaa3f641d35`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#configure-tiflash-fine-grained-shuffle-stream-count
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB system variable that controls Fine Grained Shuffle concurrency for TiFlash window function execution and changes stream_count in query plans.
- Retrieval Keywords: tiflash_fine_grained_shuffle_stream_count, Fine Grained Shuffle, window functions, stream_count, set @@tiflash_fine_grained_shuffle_stream_count = 20, ExchangeSender_11, ExchangeReceiver_12, Sort_13, Window_22, threads
- Follow-up Guidance: The official example states that before re-configuration the stream_count of [ExchangeSender_11, ExchangeReceiver_12, Sort_13, Window_22] is 8, and after setting @@tiflash_fine_grained_shuffle_stream_count = 20 it becomes 20.
- Classification Note: This is classified as performance for TiFlash because the official content describes a system variable that increases concurrency for pushed-down window function execution in TiFlash.

## Official Source Content

### Configure `tiflash_fine_grained_shuffle_stream_count`

You can increase the concurrency for executing window functions by configuring [`tiflash_fine_grained_shuffle_stream_count`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_fine_grained_shuffle_stream_count-new-in-v620) of the Fine Grained Shuffle feature. In this way, the execution of window functions can occupy more system resources, which improves query performance.

When a window function is pushed down to TiFlash for execution, you can use this variable to control the concurrency level of the window function execution. The unit is threads.

```sql
set @@tiflash_fine_grained_shuffle_stream_count = 20;
```

The following example shows the query result before and after the `tiflash_fine_grained_shuffle_stream_count` variable is re-configured. Before the re-configuration, the `stream_count` of `[ExchangeSender_11, ExchangeReceiver_12, Sort_13, Window_22]` is 8. After the re-configuration, the `stream_count` becomes 20.

Before `tiflash_fine_grained_shuffle_stream_count` is re-configured:
