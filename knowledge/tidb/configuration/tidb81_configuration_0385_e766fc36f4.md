# CDC, resolved-ts, and pessimistic transaction settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > cdc | TiKV Configuration File > cdc > `min-ts-interval` | TiKV Configuration File > cdc > `old-value-cache-memory-quota` | TiKV Configuration File > cdc > `sink-memory-quota` | TiKV Configuration File > cdc > `incremental-scan-speed-limit` | TiKV Configuration File > cdc > `incremental-scan-threads` | TiKV Configuration File > cdc > `incremental-scan-concurrency` | TiKV Configuration File > cdc > `incremental-scan-concurrency-limit` <span class="version-mark">New in v7.6.0</span> | TiKV Configuration File > resolved-ts | TiKV Configuration File > resolved-ts > `enable` | TiKV Configuration File > resolved-ts > `advance-ts-interval` | TiKV Configuration File > resolved-ts > `scan-lock-pool-size` | TiKV Configuration File > pessimistic-txn | TiKV Configuration File > pessimistic-txn > `wait-for-lock-timeout` | TiKV Configuration File > pessimistic-txn > `wake-up-delay-duration` | TiKV Configuration File > pessimistic-txn > `pipelined` | TiKV Configuration File > pessimistic-txn > `in-memory` <span class="version-mark">New in v6.0.0</span> | TiKV Configuration File > quota`
- Source Line Ranges: `2375-2468`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `ticdc`, `tidb`
- Topic Tags: `cdc`, `resolved-ts`, `stale-read`, `pessimistic-transactions`, `locks`, `memory-quota`, `concurrency`, `latency`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0385_e766fc36f4`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#cdc`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f94091ae51cc5ec2ffe0112c5cb4cbad3d4bfcc96bd7c20e52e5722d979c11bc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#cdc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiKV settings for TiCDC incremental scan behavior, resolved-ts maintenance for Stale Read, or pessimistic transaction lock wait and pipelined or in-memory lock behavior.
- Retrieval Keywords: cdc, TiCDC, min-ts-interval, old-value-cache-memory-quota, sink-memory-quota, incremental-scan-speed-limit, incremental-scan-threads, incremental-scan-concurrency, incremental-scan-concurrency-limit, resolved-ts, Stale Read, advance-ts-interval, scan-lock-pool-size, pessimistic-txn, wait-for-lock-timeout, wake-up-delay-duration, pipelined, in-memory, innodb_lock_wait_timeout
- Follow-up Guidance: The content includes startup validation and override notes for `incremental-scan-concurrency` and `incremental-scan-concurrency-limit`, and states that `in-memory` takes effect only when `pipelined` is `true`.
- Classification Note: This is classified as configuration because the content defines TiKV cdc, resolved-ts, pessimistic-txn, and quota-related configuration sections and describes option defaults and interactions.

## Official Source Content

## cdc

Configuration items related to TiCDC.
### `min-ts-interval`

+ The interval at which Resolved TS is calculated and forwarded.
+ Default value: `"1s"`.

> **Note:**
>
> In v6.5.0, the default value of `min-ts-interval` is changed from `"1s"` to `"200ms"` to reduce CDC latency. Starting from v6.5.1, this default value is changed back to `"1s"` to reduce network traffic.
### `old-value-cache-memory-quota`

+ The upper limit of memory usage by TiCDC old values.
+ Default value: `512MiB`
### `sink-memory-quota`

+ The upper limit of memory usage by TiCDC data change events.
+ Default value: `512MiB`
### `incremental-scan-speed-limit`

+ The maximum speed at which historical data is incrementally scanned.
+ Default value: `"128MiB"`, which means 128 MiB per second.
### `incremental-scan-threads`

+ The number of threads for the task of incrementally scanning historical data.
+ Default value: `4`, which means 4 threads.
### `incremental-scan-concurrency`

+ The maximum number of concurrent executions for the tasks of incrementally scanning historical data.
+ Default value: `6`, which means 6 tasks can be concurrent executed at most.
+ Note: The value of `incremental-scan-concurrency` must be greater than or equal to that of `incremental-scan-threads`; otherwise, TiKV will report an error at startup.
### `incremental-scan-concurrency-limit` New in v7.6.0

+ The maximum queue length for the tasks of incrementally scanning historical data waiting to be executed. When the number of tasks waiting to be executed exceeds this limit, new tasks will be rejected.
+ Default value: `10000`, which means that at most 10000 tasks can be queued for execution.
+ Note: `incremental-scan-concurrency-limit` must be greater than or equal to [`incremental-scan-concurrency`](#incremental-scan-concurrency); otherwise, TiKV uses `incremental-scan-concurrency` to override this configuration.
## resolved-ts

Configuration items related to maintaining the Resolved TS to serve Stale Read requests.
### `enable`

+ Determines whether to maintain the Resolved TS for all Regions.
+ Default value: `true`
### `advance-ts-interval`

+ The interval at which Resolved TS is calculated and forwarded.
+ Default value: `"20s"`
### `scan-lock-pool-size`

+ The number of threads that TiKV uses to scan the MVCC (multi-version concurrency control) lock data when initializing the Resolved TS.
+ Default value: `2`, which means 2 threads.
## pessimistic-txn

For pessimistic transaction usage, refer to [TiDB Pessimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction).
### `wait-for-lock-timeout`

- The longest time that a pessimistic transaction in TiKV waits for other transactions to release the lock. If the time is out, an error is returned to TiDB, and TiDB retries to add a lock. The lock wait timeout is set by `innodb_lock_wait_timeout`.
- Default value: `"1s"`
- Minimum value: `"1ms"`
### `wake-up-delay-duration`

- When pessimistic transactions release the lock, among all the transactions waiting for lock, only the transaction with the smallest `start_ts` is woken up. Other transactions will be woken up after `wake-up-delay-duration`.
- Default value: `"20ms"`
### `pipelined`

- This configuration item enables the pipelined process of adding the pessimistic lock. With this feature enabled, after detecting that data can be locked, TiKV immediately notifies TiDB to execute the subsequent requests and write the pessimistic lock asynchronously, which reduces most of the latency and significantly improves the performance of pessimistic transactions. But there is a still low probability that the asynchronous write of the pessimistic lock fails, which might cause the failure of pessimistic transaction commits.
- Default value: `true`
### `in-memory` New in v6.0.0

+ Enables the in-memory pessimistic lock feature. With this feature enabled, pessimistic transactions try to store their locks in memory, instead of writing the locks to disk or replicating the locks to other replicas. This improves the performance of pessimistic transactions. However, there is a still low probability that the pessimistic lock gets lost and causes the pessimistic transaction commits to fail.
+ Default value: `true`
+ Note that `in-memory` takes effect only when the value of `pipelined` is `true`.
## quota

Configuration items related to Quota Limiter.
