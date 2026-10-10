# Raftstore batching, merge, inspection, and compaction settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > raftstore > `snap-apply-batch-size` | TiKV Configuration File > raftstore > `consistency-check-interval` | TiKV Configuration File > raftstore > `raft-store-max-leader-lease` | TiKV Configuration File > raftstore > `right-derive-when-split` | TiKV Configuration File > raftstore > `merge-max-log-gap` | TiKV Configuration File > raftstore > `merge-check-tick-interval` | TiKV Configuration File > raftstore > `use-delete-range` | TiKV Configuration File > raftstore > `cleanup-import-sst-interval` | TiKV Configuration File > raftstore > `local-read-batch-size` | TiKV Configuration File > raftstore > `apply-yield-write-size` <span class="version-mark">New in v6.4.0</span> | TiKV Configuration File > raftstore > `apply-max-batch-size` | TiKV Configuration File > raftstore > `apply-pool-size` | TiKV Configuration File > raftstore > `store-max-batch-size` | TiKV Configuration File > raftstore > `store-pool-size` | TiKV Configuration File > raftstore > `store-io-pool-size` <span class="version-mark">New in v5.3.0</span> | TiKV Configuration File > raftstore > `future-poll-size` | TiKV Configuration File > raftstore > `cmd-batch` | TiKV Configuration File > raftstore > `inspect-interval` | TiKV Configuration File > raftstore > `raft-write-size-limit` <span class="version-mark">New in v5.3.0</span> | TiKV Configuration File > raftstore > `evict-cache-on-memory-ratio` <span class="version-mark">New in v7.5.0</span> | TiKV Configuration File > raftstore > `periodic-full-compact-start-times` <span class="version-mark">New in v7.6.0</span> | TiKV Configuration File > raftstore > `periodic-full-compact-start-max-cpu` <span class="version-mark">New in v7.6.0</span> | TiKV Configuration File > raftstore > `follower-read-max-log-gap` <span class="version-mark">New in v7.4.0</span> | TiKV Configuration File > raftstore > `inspect-cpu-util-thd` <span class="version-mark">New in v7.6.0</span> | TiKV Configuration File > raftstore > `inspect-kvdb-interval` <span class="version-mark">New in v8.1.2</span> | TiKV Configuration File > raftstore > `min-pending-apply-region-count` <span class="version-mark">New in v8.0.0</span> | TiKV Configuration File > raftstore > `request-voter-replicated-index-interval` <span class="version-mark">New in v6.6.0</span> | TiKV Configuration File > raftstore > `slow-trend-unsensitive-cause` <span class="version-mark">New in v6.6.0</span> | TiKV Configuration File > raftstore > `slow-trend-unsensitive-result` <span class="version-mark">New in v6.6.0</span>`
- Source Line Ranges: `966-1145`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `raftstore`, `batching`, `thread-pools`, `merge`, `snapshots`, `consistency-check`, `compaction`, `slow-node-detection`, `memory`, `leader-lease`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0373_510ca72683`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#snap-apply-batch-size`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66c372927ee07f2ed0c92d371df3b85549a979741d454dbcd969a6f2e0544fb6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#snap-apply-batch-size
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiKV raftstore configuration items for batching, merge checks, snapshot apply memory, slow node detection, full compaction scheduling, follower read lag, or thread pool sizing.
- Retrieval Keywords: raftstore, snap-apply-batch-size, consistency-check-interval, raft-store-max-leader-lease, right-derive-when-split, merge-max-log-gap, merge-check-tick-interval, use-delete-range, cleanup-import-sst-interval, local-read-batch-size, apply-yield-write-size, apply-max-batch-size, apply-pool-size, store-max-batch-size, store-pool-size, store-io-pool-size, future-poll-size, cmd-batch, inspect-interval, raft-write-size-limit, evict-cache-on-memory-ratio, periodic-full-compact-start-times, periodic-full-compact-start-max-cpu, follower-read-max-log-gap, inspect-cpu-util-thd, inspect-kvdb-interval, min-pending-apply-region-count, request-voter-replicated-index-interval, slow-trend-unsensitive-cause, slow-trend-unsensitive-result, Raftstore thread pool, StoreWriter thread pool, slow node detection, periodic full compaction
- Follow-up Guidance: The source also points readers who modify `apply-pool-size`, `store-pool-size`, or `store-io-pool-size` to the TiKV thread pool performance tuning documentation.
- Classification Note: This chunk is classified as TiKV self-managed configuration because it defines raftstore configuration parameters, defaults, limits, warnings, and version-marked options in the TiKV configuration file.

## Official Source Content

### `snap-apply-batch-size`

+ The memory cache size required when the imported snapshot file is written into the disk
+ Default value: `"10MiB"`
+ Minimum value: `0`
+ Unit: MiB
### `consistency-check-interval`

> **Warning:**
>
> It is **NOT** recommended to enable the consistency check in production environments, because it affects cluster performance and is incompatible with the garbage collection in TiDB.

+ The time interval at which the consistency check is triggered. `0` means that this feature is disabled.
+ Default value: `"0s"`
+ Minimum value: `0`
### `raft-store-max-leader-lease`

+ The longest trusted period of a Raft leader
+ Default value: `"9s"`
+ Minimum value: `0`
### `right-derive-when-split`

+ Specifies the start key of the new Region when a Region is split. When this configuration item is set to `true`, the start key is the maximum split key. When this configuration item is set to `false`, the start key is the original Region's start key.
+ Default value: `true`
### `merge-max-log-gap`

+ The maximum number of missing logs allowed when `merge` is performed
+ Default value: `10`
+ Minimum value: greater than `raft-log-gc-count-limit`
### `merge-check-tick-interval`

+ The time interval at which TiKV checks whether a Region needs merge
+ Default value: `"2s"`
+ Minimum value: greater than `0`
### `use-delete-range`

+ Determines whether to delete data from the `rocksdb delete_range` interface
+ Default value: `false`
### `cleanup-import-sst-interval`

+ The time interval at which the expired SST file is checked. `0` means that this feature is disabled.
+ Default value: `"10m"`
+ Minimum value: `0`
### `local-read-batch-size`

+ The maximum number of read requests processed in one batch
+ Default value: `1024`
+ Minimum value: greater than `0`
### `apply-yield-write-size` New in v6.4.0

+ The maximum number of bytes that the Apply thread can write for one FSM (Finite-state Machine) in one round of poll. This is a soft limit.
+ Default value: `"32KiB"`
+ Minimum value: greater than `0`
+ Unit: KiB|MiB|GiB
### `apply-max-batch-size`

+ Raft state machines process data write requests in batches by the BatchSystem. This configuration item specifies the maximum number of Raft state machines that can process the requests in one batch.
+ Default value: `256`
+ Minimum value: greater than `0`
+ Maximum value: `10240`
### `apply-pool-size`

+ The allowable number of threads in the pool that flushes data to the disk, which is the size of the Apply thread pool. When you modify the size of this thread pool, refer to [Performance tuning for TiKV thread pools](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools).
+ Default value: `2`
+ Value ranges: `[1, CPU * 10]`. `CPU` means the number of your CPU cores.
### `store-max-batch-size`

+ Raft state machines process requests for flushing logs into the disk in batches by the BatchSystem. This configuration item specifies the maximum number of Raft state machines that can process the requests in one batch.
+ If `hibernate-regions` is enabled, the default value is `256`. If `hibernate-regions` is disabled, the default value is `1024`.
+ Minimum value: greater than `0`
+ Maximum value: `10240`
### `store-pool-size`

+ The allowable number of threads in the pool that processes Raft, which is the size of the Raftstore thread pool. When you modify the size of this thread pool, refer to [Performance tuning for TiKV thread pools](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools).
+ Default value: `2`
+ Value ranges: `[1, CPU * 10]`. `CPU` means the number of your CPU cores.
### `store-io-pool-size` New in v5.3.0

+ The allowable number of threads that process Raft I/O tasks, which is the size of the StoreWriter thread pool. When you modify the size of this thread pool, refer to [Performance tuning for TiKV thread pools](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools).
+ Default value: `1` (Before v8.0.0, the default value is `0`)
+ Minimum value: `0`
### `future-poll-size`

+ The allowable number of threads that drive `future`
+ Default value: `1`
+ Minimum value: greater than `0`
### `cmd-batch`

+ Controls whether to enable batch processing of the requests. When it is enabled, the write performance is significantly improved.
+ Default value: `true`
### `inspect-interval`

+ At a certain interval, TiKV inspects the latency of the Raftstore component. This parameter specifies the interval of the inspection. If the latency exceeds this value, this inspection is marked as timeout.
+ Judges whether the TiKV node is slow based on the ratio of timeout inspection.
+ Default value: `"100ms"`
+ Minimum value: `"1ms"`
### `raft-write-size-limit` New in v5.3.0

+ Determines the threshold at which Raft data is written into the disk. If the data size is larger than the value of this configuration item, the data is written to the disk. When the value of `store-io-pool-size` is `0`, this configuration item does not take effect.
+ Default value: `1MiB`
+ Minimum value: `0`
### `evict-cache-on-memory-ratio` New in v7.5.0

+ When the memory usage of TiKV exceeds 90% of the system available memory, and the memory occupied by Raft entry cache exceeds the used memory * `evict-cache-on-memory-ratio`, TiKV evicts the Raft entry cache.
+ If this value is set to `0`, it means that this feature is disabled.
+ Default value: `0.1`
+ Minimum value: `0`
### `periodic-full-compact-start-times` New in v7.6.0

> **Warning:**
>
> Periodic full compaction is experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

+ Set the specific times that TiKV initiates periodic full compaction. You can specify multiple time schedules in an array. For example:
    + `periodic-full-compact-start-times = ["03:00", "23:00"]` indicates that TiKV performs full compaction daily at 03:00 AM and 11:00 PM, based on the local time zone of the TiKV node.
    + `periodic-full-compact-start-times = ["03:00 +0000", "23:00 +0000"]` indicates that TiKV performs full compaction daily at 03:00 AM and 11:00 PM in UTC timezone.
    + `periodic-full-compact-start-times = ["03:00 +0800", "23:00 +0800"]` indicates that TiKV performs full compaction daily at 03:00 AM and 11:00 PM in UTC+08:00 timezone.
+ Default value: `[]`, which means periodic full compaction is disabled by default.
### `periodic-full-compact-start-max-cpu` New in v7.6.0

+ Limits the maximum CPU usage rate for TiKV periodic full compaction.
+ Default value: `0.1`, which means that the maximum CPU usage for periodic compaction processes is 10%.
### `follower-read-max-log-gap` New in v7.4.0

+ The maximum number of logs a follower is allowed to lag behind when processing read requests. If this limit is exceeded, the read request is rejected.
+ Default value: `100`
### `inspect-cpu-util-thd` New in v7.6.0

+ The CPU utilization threshold for determining whether a TiKV node is busy during slow node detection.
+ Value range: `[0, 1]`
+ Default value: `0.4`, which means `40%`.
### `inspect-kvdb-interval` New in v8.1.2

+ The interval and timeout for checking the KV disk during slow node detection in TiKV. If KVDB and RaftDB share the same mount path, this value is overridden by `0` (no detection).
+ Default value: `2s`
### `min-pending-apply-region-count` New in v8.0.0

+ The maximum number of Regions in the busy state of applying Raft logs when TiKV starts. Raftstore accepts leader transfers only when the number of such Regions is below this value, reducing availability degradation during rolling restarts.
+ Default value: `10`
### `request-voter-replicated-index-interval` New in v6.6.0

+ Controls the interval at which the Witness node periodically retrieves the replicated Raft log position from voter nodes.
+ Default value: `5m`, which means 5 minutes.
### `slow-trend-unsensitive-cause` New in v6.6.0

+ When TiKV uses the SlowTrend detection algorithm, this configuration item controls the sensitivity of latency detection. A higher value indicates lower sensitivity.
+ Default value: `10`
### `slow-trend-unsensitive-result` New in v6.6.0

+ When TiKV uses the SlowTrend detection algorithm, this configuration item controls the sensitivity of QPS detection. A higher value indicates lower sensitivity.
+ Default value: `0.5`
