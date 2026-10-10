# TiKV storage section configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > storage | TiKV Configuration File > storage > `data-dir` | TiKV Configuration File > storage > `engine` <span class="version-mark">New in v6.6.0</span> | TiKV Configuration File > storage > `scheduler-concurrency` | TiKV Configuration File > storage > `scheduler-worker-pool-size` | TiKV Configuration File > storage > `scheduler-pending-write-threshold` | TiKV Configuration File > storage > `enable-async-apply-prewrite` | TiKV Configuration File > storage > `reserve-space``
- Source Line Ranges: `425-477`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `storage`, `data-dir`, `engine`, `scheduler`, `write-queue`, `async-commit`, `disk-space`, `reserve-space`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0368_46b17a40da`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#storage`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `702be5eb58465778be7421f37fc5322aa34525577afb21b036bde4d60d309a38`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#storage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiKV `storage` section configuration for `data-dir`, `engine`, scheduler settings, async prewrite apply behavior, write queue thresholds, or disk reserve space protection.
- Retrieval Keywords: storage, data-dir, engine, raft-kv, partitioned-raft-kv, scheduler-concurrency, scheduler-worker-pool-size, scheduler-pending-write-threshold, enable-async-apply-prewrite, reserve-space, space_placeholder_file, Server Is Busy, Async Commit
- Follow-up Guidance: The content notes that `engine` is experimental, can only be specified when creating a new cluster, and cannot be modified once specified.
- Classification Note: This is configuration content because it lists TiKV storage-related configuration items with their defaults, value ranges, and operational effects.

## Official Source Content

## storage

Configuration items related to storage.
### `data-dir`

+ The storage path of the RocksDB directory
+ Default value: `"./"`
### `engine` New in v6.6.0

> **Warning:**
>
> This feature is experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

+ Specifies the engine type. This configuration can only be specified when creating a new cluster and cannot be modified once being specified.
+ Default value: `"raft-kv"`
+ Value options:

    + `"raft-kv"`: The default engine type in versions earlier than TiDB v6.6.0.
    + `"partitioned-raft-kv"`: The new storage engine type introduced in TiDB v6.6.0.
### `scheduler-concurrency`

+ A built-in memory lock mechanism to prevent simultaneous operations on a key. Each key has a hash in a different slot.
+ Default value: `524288`
+ Minimum value: `1`
### `scheduler-worker-pool-size`

+ The number of threads in the Scheduler thread pool. Scheduler threads are mainly used for checking transaction consistency before data writing. If the number of CPU cores is greater than or equal to `16`, the default value is `8`; otherwise, the default value is `4`. When you modify the size of the Scheduler thread pool, refer to [Performance tuning for TiKV thread pools](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools).
+ Default value: `4`
+ Value range: `[1, MAX(4, CPU)]`. In `MAX(4, CPU)`, `CPU` means the number of your CPU cores. `MAX(4, CPU)` takes the greater value out of `4` and the `CPU`.
### `scheduler-pending-write-threshold`

+ The maximum size of the write queue. A `Server Is Busy` error is returned for a new write to TiKV when this value is exceeded.
+ Default value: `"100MiB"`
+ Unit: MiB|GiB
### `enable-async-apply-prewrite`

+ Determines whether Async Commit transactions respond to the TiKV client before applying prewrite requests. After enabling this configuration item, latency can be easily reduced when the apply duration is high, or the delay jitter can be reduced when the apply duration is not stable.
+ Default value: `false`
### `reserve-space`

+ When TiKV is started, some space is reserved on the disk as disk protection. When the remaining disk space is less than the reserved space, TiKV restricts some write operations. The reserved space is divided into two parts: 80% of the reserved space is used as the extra disk space required for operations when the disk space is insufficient, and the other 20% is used to store the temporary file. In the process of reclaiming space, if the storage is exhausted by using too much extra disk space, this temporary file serves as the last protection for restoring services.
+ The name of the temporary file is `space_placeholder_file`, located in the `storage.data-dir` directory. When TiKV goes offline because its disk space ran out, if you restart TiKV, the temporary file is automatically deleted and TiKV tries to reclaim the space.
+ When the remaining space is insufficient, TiKV does not create the temporary file. The effectiveness of the protection is related to the size of the reserved space. The size of the reserved space is the larger value between 5% of the disk capacity and this configuration value. If this configuration item is set to `0`, or to a zero value with any supported unit (for example, `0KiB`, `0MiB`, or `0GiB`), TiKV disables this disk protection feature.
+ Default value: `"5GiB"`
+ Unit: B|KB|KiB|MB|MiB|GB|GiB|TB|TiB|PB|PiB
