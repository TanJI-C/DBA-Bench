# Performance improvements: async commit, optimizer stability, and jitter reduction

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0-rc.md`
- Source Title: `TiDB 5.0 RC Release Notes`
- Source Heading Path: `TiDB 5.0 RC Release Notes > Performance improvements | TiDB 5.0 RC Release Notes > Performance improvements > Support async commit (experimental) | TiDB 5.0 RC Release Notes > Performance improvements > Improve the optimizer's stability in index selection (experimental) | TiDB 5.0 RC Release Notes > Performance improvements > Optimize performance jitter caused by imperfect scheduling or imperfect I/O flow control`
- Source Line Ranges: `94-132`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `sql`
- Topic Tags: `performance`, `async-commit`, `external-consistency`, `optimizer`, `statistics`, `scheduling`, `io-flow-control`, `gc-compaction`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0146_f8cf7a3d5c`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0-rc.md#performance-improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cc2e7fbe4b5e9e52cec3e39b6fac73e2229f7cc23ef079af08622346c95c1ae0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0-rc#performance-improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0-rc.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 5.0.0-rc performance release notes about async commit, optimizer index-selection stability, or jitter reduction related to scheduling, compaction, GC, and TiFlash background I/O limits.
- Retrieval Keywords: TiDB 5.0.0-rc, Performance improvements, async commit, tidb_enable_async_commit, tidb_guarantee_external_consistency, external consistency, two-phase commit, Sysbench oltp-insert, optimizer stability in index selection, multi-column NDV, multi-column order dependency, multi-column function dependency, TopN, CMSKetch, histogram, performance jitter, region-score-formula-version = v2, store-limit, enable-cross-table-merge = true, empty Regions, rate-limiter-auto-tuned, GC Compaction Filter, gc.enable-compaction-filter = true, bg_task_io_rate_limit, TiFlash, I/O flow control, scheduling
- Follow-up Guidance: The chunk states that async commit returns results after the first phase of two-phase commit and notes that external consistency is guaranteed only when `tidb_guarantee_external_consistency = ON` is set.
- Classification Note: This is classified as a performance chunk because the official content focuses on latency reduction, optimizer stability, and reduced performance jitter through specific performance-related features and configurations.

## Official Source Content

## Performance improvements
### Support async commit (experimental)

Enabling the async commit feature can significantly reduce the latency of transactions. For example, with this feature enabled, the latency of transactions in the Sysbench oltp-insert test is 37.3% lower than that when this feature is disabled.

Previously without the async commit feature, the statements being written were only returned to the client after the two-phase transaction commit finished. Now the async commit feature supports returning the result to the client after the first phase of the two-phase commit finishes. The second phase is then performed asynchronously in the background, thus reducing the latency of transaction commit.

However, when async commit is enabled, the external consistency of transactions can be guaranteed **only** when `tidb_guarantee_external_consistency = ON` is set. With async commit enabled, the performance might drop.

Users can enable this feature by setting the global variable `tidb_enable_async_commit = ON`.

+ [User document](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_async_commit-new-in-v50)
+ Related issue: [#8316](https://github.com/tikv/tikv/issues/8316)
### Improve the optimizer's stability in index selection (experimental)

The optimizer's ability to always select a relatively suitable index greatly determines whether the latency of queries is stable. We have improved and refactored the statistics module to ensure that, for the same SQL statements, the optimizer does not select a different index from multiple candidate indexes each time due to missing or inaccurate statistics. The main improvements to help the optimizer select a relatively suitable index are as follows:

+ Add more information to the statistics module, such as the multi-column NDV, the multi-column order dependency, and the multi-column function dependency.
+ Refactor the statistics module.
    + Delete `TopN` values from `CMSKetch`.
    + Refactor the search logic of `TopN`.
    + Delete the `TopN` information from the histogram and create an index of the histogram for easy maintenance of Bucket NDV.

Related issue: [#18065](https://github.com/pingcap/tidb/issues/18065)
### Optimize performance jitter caused by imperfect scheduling or imperfect I/O flow control

The TiDB scheduling process occupies resources such as I/O, network, CPU, and memory. If TiDB does not control the scheduled tasks, QPS and delay might cause performance jitter due to resource preemption. After the following optimizations, in the 72-hour test, the standard deviation of Sysbench TPS jitter is reduced from 11.09% to 3.36%.

+ Reduce the redundant scheduling issues caused by fluctuations of node capacity (always near the waterline) and caused by PD's `store-limit` configuration value set too large. This is achieved by introducing a new set of scheduling calculation formulas enabled via the `region-score-formula-version = v2` configuration item. [#3269](https://github.com/tikv/pd/pull/3269)
+ Enable the cross-Region merge feature by modifying `enable-cross-table-merge = true` to reduce the number of empty Regions. [#3129](https://github.com/tikv/pd/pull/3129)
+ Data compaction in the TiKV background occupies a lot of I/O resources. The system automatically adjusts the compaction rate to balance the contention for I/O resources between background tasks and foreground reads and writes. After enabling this feature via the `rate-limiter-auto-tuned` configuration item, the delay jitter is greatly reduced. [#18011](https://github.com/pingcap/tidb/issues/18011)
+ When TiKV performs garbage collection (GC) and data compaction, partitions occupy CPU and I/O resources. Overlapping data exists during the execution of these two tasks. To reduce I/O usage, the GC Compaction Filter feature combines these two tasks into one and executes them in the same task. This feature is still experimental and you can enable it via `gc.enable-compaction-filter = true`. [#18009](https://github.com/pingcap/tidb/issues/18009)
+ When TiFlash compresses or sorts data, it occupies a lot of I/O resources. The system alleviates contention for resources by limiting the compression and data sorting's use of I/O resources. This feature is still experimental and you can enable it via `bg_task_io_rate_limit`.

Related issue: [#18005](https://github.com/pingcap/tidb/issues/18005)
