# Storage format, TTL, block cache, flow control, and I/O rate limit

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > storage > `enable-ttl` | TiKV Configuration File > storage > `ttl-check-poll-interval` | TiKV Configuration File > storage > `background-error-recovery-window` <span class="version-mark">New in v6.1.0</span> | TiKV Configuration File > storage > `api-version` <span class="version-mark">New in v6.1.0</span> | TiKV Configuration File > `txn-status-cache-capacity` <span class="version-mark">New in v7.6.0</span> | TiKV Configuration File > storage.block-cache | TiKV Configuration File > storage.block-cache > `capacity` | TiKV Configuration File > storage.block-cache > `low-pri-pool-ratio` <span class="version-mark">New in v8.0.0</span> | TiKV Configuration File > storage.flow-control | TiKV Configuration File > storage.flow-control > `enable` | TiKV Configuration File > storage.flow-control > `memtables-threshold` | TiKV Configuration File > storage.flow-control > `l0-files-threshold` | TiKV Configuration File > storage.flow-control > `soft-pending-compaction-bytes-limit` | TiKV Configuration File > storage.flow-control > `hard-pending-compaction-bytes-limit` | TiKV Configuration File > storage.io-rate-limit | TiKV Configuration File > storage.io-rate-limit > `max-bytes-per-sec` | TiKV Configuration File > storage.io-rate-limit > `mode``
- Source Line Ranges: `478-587`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `tidb`
- Topic Tags: `storage`, `ttl`, `api-version`, `block-cache`, `flow-control`, `io-rate-limit`, `rawkv`, `mvcc`, `background-recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0369_3290ad5e91`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#enable-ttl`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c413345166d602bf33edb5861aed26678912554470df658459f714c4021fa0c0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-ttl
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV configuration details about storage TTL, RawKV `api-version`, block cache sharing, flow control thresholds, `ServerIsBusy` write rejection, background SST error recovery, or I/O rate limiting.
- Retrieval Keywords: storage.enable-ttl, ttl-check-poll-interval, background-error-recovery-window, storage.api-version, API V1, API V2, RawKV, MVCC, PD TSO, can't enable TTL on a non-ttl, txn-status-cache-capacity, storage.block-cache, capacity, low-pri-pool-ratio, storage.flow-control, memtables-threshold, l0-files-threshold, soft-pending-compaction-bytes-limit, hard-pending-compaction-bytes-limit, ServerIsBusy, storage.io-rate-limit, max-bytes-per-sec, mode, write-only
- Follow-up Guidance: The content also points to TTL, MVCC glossary, RawKV Backup & Restore, and RawKV CDC references when the question expands beyond the configuration items themselves.
- Classification Note: This is classified as configuration content because it defines TiKV configuration items, defaults, value options, warnings, and behavior for storage, cache, flow control, and I/O limiting.

## Official Source Content

### `enable-ttl`

> **Warning:**
>
> - Set `enable-ttl` to `true` or `false` **ONLY WHEN** deploying a new TiKV cluster. **DO NOT** modify the value of this configuration item in an existing TiKV cluster. TiKV clusters with different `enable-ttl` values use different data formats. Therefore, if you modify the value of this item in an existing TiKV cluster, the cluster will store data in different formats, which causes the "can't enable TTL on a non-ttl" error when you restart the TiKV cluster.
> - Use `enable-ttl` **ONLY IN** a TiKV cluster. **DO NOT** use this configuration item in a cluster that has TiDB nodes (which means setting `enable-ttl` to `true` in such clusters) unless `storage.api-version = 2` is configured. Otherwise, critical issues such as data corruption and the upgrade failure of TiDB clusters will occur.

+ [TTL](https://docs.pingcap.com/tidb/stable/time-to-live) is short for "Time to live". If this item is enabled, TiKV automatically deletes data that reaches its TTL. To set the value of TTL, you need to specify it in the requests when writing data via the client. If the TTL is not specified, it means that TiKV does not automatically delete the corresponding data.
+ Default value: `false`
### `ttl-check-poll-interval`

+ The interval of checking data to reclaim physical spaces. If data reaches its TTL, TiKV forcibly reclaims its physical space during the check.
+ Default value: `"12h"`
+ Minimum value: `"0s"`
### `background-error-recovery-window` New in v6.1.0

+ The maximum allowable time for TiKV to recover after RocksDB detects a recoverable background error. If some background SST files are damaged, RocksDB will report to PD via heartbeat after locating the Peer to which the damaged SST files belong. PD then performs scheduling operations to remove this Peer. Finally, the damaged SST files are deleted directly, and the TiKV background will work as normal again.
+ The damaged SST files still exist before the recovery finishes. During such a period, RocksDB can continue writing data, but an error will be reported when the damaged part of the data is read.
+ If the recovery fails to finish within this time window, TiKV will panic.
+ Default value: 1h
### `api-version` New in v6.1.0

+ The storage format and interface version used by TiKV when TiKV serves as the RawKV store.
+ Value options:
    + `1`: Uses API V1, does not encode the data passed from the client, and stores data as it is. In versions earlier than v6.1.0, TiKV uses API V1 by default.
    + `2`: Uses API V2:
        + The data is stored in the [Multi-Version Concurrency Control (MVCC)](https://docs.pingcap.com/tidb/stable/glossary#multi-version-concurrency-control-mvcc) format, where the timestamp is obtained from PD (which is TSO) by tikv-server.
        + Data is scoped according to different usage and API V2 supports co-existence of TiDB, Transactional KV, and RawKV applications in a single cluster.
        + When API V2 is used, you are expected to set `storage.enable-ttl = true` at the same time. Because API V2 supports the TTL feature, you must turn on [`enable-ttl`](#enable-ttl) explicitly. Otherwise, it will be in conflict because `storage.enable-ttl` defaults to `false`.
        + When API V2 is enabled, you need to deploy at least one tidb-server instance to reclaim obsolete data. This tidb-server instance can provide read and write services at the same time. To ensure high availability, you can deploy multiple tidb-server instances.
        + Client support is required for API V2. For details, see the corresponding instruction of the client for the API V2.
        + Since v6.2.0, Change Data Capture (CDC) for RawKV is supported. Refer to [RawKV CDC](https://tikv.org/docs/latest/concepts/explore-tikv-features/cdc/cdc).
+ Default value: `1`

> **Warning:**

> - API V1 and API V2 are different from each other in the storage format. You can enable or disable API V2 directly **only** when TiKV contains only TiDB data. In other scenarios, you need to deploy a new cluster, and migrate data using [RawKV Backup & Restore](https://tikv.org/docs/latest/concepts/explore-tikv-features/backup-restore/).
> - After API V2 is enabled, you **cannot** downgrade the TiKV cluster to a version earlier than v6.1.0. Otherwise, data corruption might occur.
## `txn-status-cache-capacity` New in v7.6.0

+ Sets the capacity of the transaction status cache in TiKV. Do not modify this parameter.
+ Default value: `5120000`
## storage.block-cache

Configuration items related to the sharing of block cache among multiple RocksDB Column Families (CF).
### `capacity`

+ The size of the shared block cache.
+ Default value:

    + When `storage.engine="raft-kv"`, the default value is 45% of the size of total system memory.
    + When `storage.engine="partitioned-raft-kv"`, the default value is 30% of the size of total system memory.

+ Unit: KiB|MiB|GiB
### `low-pri-pool-ratio` New in v8.0.0

+ Controls the proportion of the entire block cache that the Titan component can use.
+ Default value: `0.2`
## storage.flow-control

Configuration items related to the flow control mechanism in TiKV. This mechanism replaces the write stall mechanism in RocksDB and controls flow at the scheduler layer, which avoids secondary disasters caused by the stuck Raftstore or Apply threads.
### `enable`

+ Determines whether to enable the flow control mechanism. After it is enabled, TiKV automatically disables the write stall mechanism of KvDB and the write stall mechanism of RaftDB (excluding memtable).
+ Default value: `true`
### `memtables-threshold`

+ When the number of kvDB memtables reaches this threshold, the flow control mechanism starts to work. When `enable` is set to `true`, this configuration item overrides `rocksdb.(defaultcf|writecf|lockcf).max-write-buffer-number`.
+ Default value: `5`
### `l0-files-threshold`

+ When the number of kvDB L0 files reaches this threshold, the flow control mechanism starts to work. When `enable` is set to `true`, this configuration item overrides `rocksdb.(defaultcf|writecf|lockcf).level0-slowdown-writes-trigger`.
+ Default value: `20`
### `soft-pending-compaction-bytes-limit`

+ When the pending compaction bytes in KvDB reach this threshold, the flow control mechanism starts to reject some write requests and reports the `ServerIsBusy` error. When `enable` is set to `true`, this configuration item overrides `rocksdb.(defaultcf|writecf|lockcf).soft-pending-compaction-bytes-limit`.
+ Default value: `"192GiB"`
### `hard-pending-compaction-bytes-limit`

+ When the pending compaction bytes in KvDB reach this threshold, the flow control mechanism rejects all write requests and reports the `ServerIsBusy` error. When `enable` is set to `true`, this configuration item overrides `rocksdb.(defaultcf|writecf|lockcf).hard-pending-compaction-bytes-limit`.
+ Default value: `"1024GiB"`
## storage.io-rate-limit

Configuration items related to the I/O rate limiter.
### `max-bytes-per-sec`

+ Limits the maximum I/O bytes that a server can write to or read from the disk (determined by the `mode` configuration item below) in one second. When this limit is reached, TiKV prefers throttling background operations over foreground ones. The value of this configuration item should be set to the disk's optimal I/O bandwidth, for example, the maximum I/O bandwidth specified by your cloud disk vendor. When this configuration value is set to zero, disk I/O operations are not limited.
+ Default value: `"0MiB"`
### `mode`

+ Determines which types of I/O operations are counted and restrained below the `max-bytes-per-sec` threshold. Currently, only the write-only mode is supported.
+ Value options: `"read-only"`, `"write-only"`, and `"all-io"`
+ Default value: `"write-only"`
