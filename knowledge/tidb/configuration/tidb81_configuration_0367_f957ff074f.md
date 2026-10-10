# TiKV read pool configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > readpool.unified | TiKV Configuration File > readpool.unified > `min-thread-count` | TiKV Configuration File > readpool.unified > `max-thread-count` | TiKV Configuration File > readpool.unified > `stack-size` | TiKV Configuration File > readpool.unified > `max-tasks-per-worker` | TiKV Configuration File > readpool.unified > `auto-adjust-pool-size` <span class="version-mark">New in v6.3.0</span> | TiKV Configuration File > readpool.storage | TiKV Configuration File > readpool.storage > `use-unified-pool` | TiKV Configuration File > readpool.storage > `high-concurrency` | TiKV Configuration File > readpool.storage > `normal-concurrency` | TiKV Configuration File > readpool.storage > `low-concurrency` | TiKV Configuration File > readpool.storage > `max-tasks-per-worker-high` | TiKV Configuration File > readpool.storage > `max-tasks-per-worker-normal` | TiKV Configuration File > readpool.storage > `max-tasks-per-worker-low` | TiKV Configuration File > readpool.storage > `stack-size` | TiKV Configuration File > `readpool.coprocessor` | TiKV Configuration File > `readpool.coprocessor` > `use-unified-pool` | TiKV Configuration File > `readpool.coprocessor` > `high-concurrency` | TiKV Configuration File > `readpool.coprocessor` > `normal-concurrency` | TiKV Configuration File > `readpool.coprocessor` > `low-concurrency` | TiKV Configuration File > `readpool.coprocessor` > `max-tasks-per-worker-high` | TiKV Configuration File > `readpool.coprocessor` > `max-tasks-per-worker-normal` | TiKV Configuration File > `readpool.coprocessor` > `max-tasks-per-worker-low` | TiKV Configuration File > `readpool.coprocessor` > `stack-size``
- Source Line Ranges: `278-424`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `readpool`, `thread-pool`, `concurrency`, `coprocessor`, `storage-reads`, `server-is-busy`, `stack-size`, `cpu-tuning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0367_f957ff074f`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#readpool-unified`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fe57b60521b9826f952657e548eaa23c31e4de440f726d797ddb0d7708083213`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#readpool-unified
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiKV read pool configuration details for unified, storage, or coprocessor thread pools, including concurrency, stack size, task limits, and `Server Is Busy` conditions.
- Retrieval Keywords: readpool.unified, min-thread-count, max-thread-count, stack-size, max-tasks-per-worker, auto-adjust-pool-size, readpool.storage, use-unified-pool, high-concurrency, normal-concurrency, low-concurrency, max-tasks-per-worker-high, max-tasks-per-worker-normal, max-tasks-per-worker-low, readpool.coprocessor, UnifyReadPool, Server Is Busy, Performance tuning for TiKV thread pools
- Follow-up Guidance: The content also points to Performance tuning for TiKV thread pools when modifying unified read pool or scheduler-related thread pool sizes.
- Classification Note: This is configuration content because it defines TiKV read request thread pool parameters, defaults, ranges, and behavior for unified, storage, and coprocessor read pools.

## Official Source Content

## readpool.unified

Configuration items related to the single thread pool serving read requests. This thread pool supersedes the original storage thread pool and coprocessor thread pool since the 4.0 version.
### `min-thread-count`

+ The minimal working thread count of the unified read pool
+ Default value: `1`
### `max-thread-count`

+ The maximum working thread count of the unified read pool or the UnifyReadPool thread pool. When you modify the size of this thread pool, refer to [Performance tuning for TiKV thread pools](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools).
+ Value range: `[min-thread-count, MAX(4, CPU quota * 10)]`. `MAX(4, CPU quota * 10)` takes the greater value out of `4` and the `CPU quota * 10`.
+ Default value: MAX(4, CPU * 0.8)

> **Note:**
>
> Increasing the thread count will lead to more context switches, which might cause a performance decrease. It is not recommended to modify the value of this configuration item.
### `stack-size`

+ The stack size of the threads in the unified thread pool
+ Type: Integer + Unit
+ Default value: `"10MiB"`
+ Unit: KiB|MiB|GiB
+ Minimum value: `"2MiB"`
+ Maximum value: The number of Kbytes output in the result of the `ulimit -sH` command executed in the system.
### `max-tasks-per-worker`

+ The maximum number of tasks allowed for a single thread in the unified read pool. `Server Is Busy` is returned when the value is exceeded.
+ Default value: `2000`
+ Minimum value: `2`
### `auto-adjust-pool-size` New in v6.3.0

+ Controls whether to automatically adjust the thread pool size. When it is enabled, the read performance of TiKV is optimized by automatically adjusting the UnifyReadPool thread pool size based on the current CPU usage. The possible range of the thread pool is `[max-thread-count, MAX(4, CPU)]`. The maximum value is the same as the one of [`max-thread-count`](#max-thread-count).
+ Default value: `false`
## readpool.storage

Configuration items related to storage thread pool.
### `use-unified-pool`

+ Determines whether to use the unified thread pool (configured in [`readpool.unified`](#readpoolunified)) for storage requests. If the value of this parameter is `false`, a separate thread pool is used, which is configured through the rest parameters in this section (`readpool.storage`).
+ Default value: If this section (`readpool.storage`) has no other configurations, the default value is `true`. Otherwise, for the backward compatibility, the default value is `false`. Change the configuration in [`readpool.unified`](#readpoolunified) as needed before enabling this option.
### `high-concurrency`

+ The allowable number of concurrent threads that handle high-priority `read` requests
+ When `8` ≤ `cpu num` ≤ `16`, the default value is `cpu_num * 0.5`; when `cpu num` is smaller than `8`, the default value is `4`; when `cpu num` is greater than `16`, the default value is `8`.
+ Minimum value: `1`
### `normal-concurrency`

+ The allowable number of concurrent threads that handle normal-priority `read` requests
+ When `8` ≤ `cpu num` ≤ `16`, the default value is `cpu_num * 0.5`; when `cpu num` is smaller than `8`, the default value is `4`; when `cpu num` is greater than `16`, the default value is `8`.
+ Minimum value: `1`
### `low-concurrency`

+ The allowable number of concurrent threads that handle low-priority `read` requests
+ When `8` ≤ `cpu num` ≤ `16`, the default value is `cpu_num * 0.5`; when `cpu num` is smaller than `8`, the default value is `4`; when `cpu num` is greater than `16`, the default value is `8`.
+ Minimum value: `1`
### `max-tasks-per-worker-high`

+ The maximum number of tasks allowed for a single thread in a high-priority thread pool. `Server Is Busy` is returned when the value is exceeded.
+ Default value: `2000`
+ Minimum value: `2`
### `max-tasks-per-worker-normal`

+ The maximum number of tasks allowed for a single thread in a normal-priority thread pool. `Server Is Busy` is returned when the value is exceeded.
+ Default value: `2000`
+ Minimum value: `2`
### `max-tasks-per-worker-low`

+ The maximum number of tasks allowed for a single thread in a low-priority thread pool. `Server Is Busy` is returned when the value is exceeded.
+ Default value: `2000`
+ Minimum value: `2`
### `stack-size`

+ The stack size of threads in the Storage read thread pool
+ Type: Integer + Unit
+ Default value: `"10MiB"`
+ Unit: KiB|MiB|GiB
+ Minimum value: `"2MiB"`
+ Maximum value: The number of Kbytes output in the result of the `ulimit -sH` command executed in the system.
## `readpool.coprocessor`

Configuration items related to the Coprocessor thread pool.
### `use-unified-pool`

+ Determines whether to use the unified thread pool (configured in [`readpool.unified`](#readpoolunified)) for coprocessor requests. If the value of this parameter is `false`, a separate thread pool is used, which is configured through the rest parameters in this section (`readpool.coprocessor`).
+ Default value: If none of the parameters in this section (`readpool.coprocessor`) are set, the default value is `true`. Otherwise, the default value is `false` for the backward compatibility. Adjust the configuration items in [`readpool.unified`](#readpoolunified) before enabling this parameter.
### `high-concurrency`

+ The allowable number of concurrent threads that handle high-priority Coprocessor requests, such as checkpoints
+ Default value: `CPU * 0.8`
+ Minimum value: `1`
### `normal-concurrency`

+ The allowable number of concurrent threads that handle normal-priority Coprocessor requests
+ Default value: `CPU * 0.8`
+ Minimum value: `1`
### `low-concurrency`

+ The allowable number of concurrent threads that handle low-priority Coprocessor requests, such as table scan
+ Default value: `CPU * 0.8`
+ Minimum value: `1`
### `max-tasks-per-worker-high`

+ The number of tasks allowed for a single thread in a high-priority thread pool. When this number is exceeded, `Server Is Busy` is returned.
+ Default value: `2000`
+ Minimum value: `2`
### `max-tasks-per-worker-normal`

+ The number of tasks allowed for a single thread in a normal-priority thread pool. When this number is exceeded, `Server Is Busy` is returned.
+ Default value: `2000`
+ Minimum value: `2`
### `max-tasks-per-worker-low`

+ The number of tasks allowed for a single thread in a low-priority thread pool. When this number is exceeded, `Server Is Busy` is returned.
+ Default value: `2000`
+ Minimum value: `2`
### `stack-size`

+ The stack size of the thread in the Coprocessor thread pool
+ Type: Integer + Unit
+ Default value: `"10MiB"`
+ Unit: KiB|MiB|GiB
+ Minimum value: `"2MiB"`
+ Maximum value: The number of Kbytes output in the result of the `ulimit -sH` command executed in the system.
