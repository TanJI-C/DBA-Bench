# RocksDB engine runtime, WAL, logging, and write path settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > rocksdb > `max-background-jobs` | TiKV Configuration File > rocksdb > `max-background-flushes` | TiKV Configuration File > rocksdb > `max-sub-compactions` | TiKV Configuration File > rocksdb > `max-open-files` | TiKV Configuration File > rocksdb > `max-manifest-file-size` | TiKV Configuration File > rocksdb > `create-if-missing` | TiKV Configuration File > rocksdb > `wal-recovery-mode` | TiKV Configuration File > rocksdb > `wal-dir` | TiKV Configuration File > rocksdb > `wal-ttl-seconds` | TiKV Configuration File > rocksdb > `wal-size-limit` | TiKV Configuration File > rocksdb > `max-total-wal-size` | TiKV Configuration File > rocksdb > `stats-dump-period` | TiKV Configuration File > rocksdb > `compaction-readahead-size` | TiKV Configuration File > rocksdb > `writable-file-max-buffer-size` | TiKV Configuration File > rocksdb > `use-direct-io-for-flush-and-compaction` | TiKV Configuration File > rocksdb > `rate-bytes-per-sec` | TiKV Configuration File > rocksdb > `rate-limiter-refill-period` | TiKV Configuration File > rocksdb > `rate-limiter-mode` | TiKV Configuration File > rocksdb > `rate-limiter-auto-tuned` <span class="version-mark">New in v5.0</span> | TiKV Configuration File > rocksdb > `enable-pipelined-write` | TiKV Configuration File > rocksdb > `bytes-per-sync` | TiKV Configuration File > rocksdb > `wal-bytes-per-sync` | TiKV Configuration File > rocksdb > `info-log-max-size` | TiKV Configuration File > rocksdb > `info-log-roll-time` | TiKV Configuration File > rocksdb > `info-log-keep-log-file-num` | TiKV Configuration File > rocksdb > `info-log-dir` | TiKV Configuration File > rocksdb > `info-log-level` | TiKV Configuration File > rocksdb > `write-buffer-flush-oldest-first` <span class="version-mark">New in v6.6.0</span> | TiKV Configuration File > rocksdb > `write-buffer-limit` <span class="version-mark">New in v6.6.0</span> | TiKV Configuration File > rocksdb > `track-and-verify-wals-in-manifest` <span class="version-mark">New in v6.5.9, v7.1.5, v7.5.2, and v8.0.0</span> | TiKV Configuration File > rocksdb > `enable-multi-batch-write` <span class="version-mark">New in v6.2.0</span>`
- Source Line Ranges: `1221-1452`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `rocksdb`, `wal`, `logging`, `compaction`, `io`, `rate-limiting`, `write-path`, `thread-pools`, `memtable`, `storage-engine`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0375_7f83cc8ccd`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#max-background-jobs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9a238b8f6d62d837db5be8550d7cc84982aca6a8ff7c83591e07b652f137ff38`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#max-background-jobs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV self-managed RocksDB configuration details for background jobs, WAL behavior, compaction I/O limiting, logging settings, memtable write-buffer controls, or write path options.
- Retrieval Keywords: rocksdb.max-background-jobs, rocksdb.max-background-flushes, rocksdb.max-sub-compactions, rocksdb.max-open-files, rocksdb.max-manifest-file-size, rocksdb.create-if-missing, rocksdb.wal-recovery-mode, rocksdb.wal-dir, rocksdb.wal-ttl-seconds, rocksdb.wal-size-limit, rocksdb.max-total-wal-size, rocksdb.stats-dump-period, rocksdb.compaction-readahead-size, rocksdb.writable-file-max-buffer-size, rocksdb.use-direct-io-for-flush-and-compaction, rocksdb.rate-bytes-per-sec, rocksdb.rate-limiter-refill-period, rocksdb.rate-limiter-mode, rocksdb.rate-limiter-auto-tuned, rocksdb.enable-pipelined-write, rocksdb.bytes-per-sync, rocksdb.wal-bytes-per-sync, rocksdb.info-log-max-size, rocksdb.info-log-roll-time, rocksdb.info-log-keep-log-file-num, rocksdb.info-log-dir, rocksdb.info-log-level, rocksdb.write-buffer-flush-oldest-first, rocksdb.write-buffer-limit, rocksdb.track-and-verify-wals-in-manifest, rocksdb.enable-multi-batch-write, WAL recovery mode, max total WAL size, compaction rate limiter, Track WAL in MANIFEST, Pipelined Write, memtable flush strategy
- Follow-up Guidance: The source points to Performance tuning for TiKV thread pools for RocksDB thread pool sizing and to TiKV logging settings such as log.file.max-size, log.file.max-backups, and log.level for deprecated RocksDB log options.
- Classification Note: This is a configuration chunk because it enumerates TiKV rocksdb configuration items, defaults, value options, minimum values, deprecation warnings, and version-marked settings.

## Official Source Content

### `max-background-jobs`

+ The number of background threads in RocksDB. When you modify the size of the RocksDB thread pool, refer to [Performance tuning for TiKV thread pools](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools).
+ Default value:
    + When the number of CPU cores is 10, the default value is `9`.
    + When the number of CPU cores is 8, the default value is `7`.
    + When the number of CPU cores is `N`, the default value is `max(2, min(N - 1, 9))`.
+ Minimum value: `2`
### `max-background-flushes`

+ The maximum number of concurrent background memtable flush jobs
+ Default value:
    + When the number of CPU cores is 10, the default value is `3`.
    + When the number of CPU cores is 8, the default value is `2`.
    + When the number of CPU cores is `N`, the default value is `[(max-background-jobs + 3) / 4]`.
+ Minimum value: `1`
### `max-sub-compactions`

+ The number of sub-compaction operations performed concurrently in RocksDB
+ Default value: `3`
+ Minimum value: `1`
### `max-open-files`

+ The total number of files that RocksDB can open
+ Default value: `40960`
+ Minimum value: `-1`
### `max-manifest-file-size`

+ The maximum size of a RocksDB Manifest file
+ Default value: `"128MiB"`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `create-if-missing`

+ Determines whether to automatically create a DB switch
+ Default value: `true`
### `wal-recovery-mode`

+ WAL recovery mode
+ Optional values:
    + `"tolerate-corrupted-tail-records"`: tolerates and discards the records that have incomplete trailing data on all logs
    + `"absolute-consistency"`: abandons recovery when corrupted logs are found
    + `"point-in-time"`: recovers logs sequentially until the first corrupted log is encountered
    + `"skip-any-corrupted-records"`: post-disaster recovery. The data is recovered as much as possible, and corrupted records are skipped.
+ Default value: `"point-in-time"`
### `wal-dir`

+ The directory in which WAL files are stored. If not specified, the WAL files will be stored in the same directory as the data.
+ Default value: `""`
### `wal-ttl-seconds`

+ The living time of the archived WAL files. When the value is exceeded, the system deletes these files.
+ Default value: `0`
+ Minimum value: `0`
+ unit: second
### `wal-size-limit`

+ The size limit of the archived WAL files. When the value is exceeded, the system deletes these files.
+ Default value: `0`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `max-total-wal-size`

+ The maximum RocksDB WAL size in total, which is the size of `*.log` files in the `data-dir`.
+ Default value:

    + When `storage.engine="raft-kv"`, the default value is `"4GiB"`.
    + When `storage.engine="partitioned-raft-kv"`, the default value is `1`.
### `stats-dump-period`

+ The interval at which statistics are output to the log.
+ Default value:

    + When `storage.engine="raft-kv"`, the default value is `"10m"`.
    + When `storage.engine="partitioned-raft-kv"`, the default value is `"0"`.
### `compaction-readahead-size`

+ Enables the readahead feature during RocksDB compaction and specifies the size of readahead data. If you are using mechanical disks, it is recommended to set the value to 2MiB at least.
+ Default value: `0`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `writable-file-max-buffer-size`

+ The maximum buffer size used in WritableFileWrite
+ Default value: `"1MiB"`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `use-direct-io-for-flush-and-compaction`

+ Determines whether to use `O_DIRECT` for both reads and writes in the background flush and compactions. The performance impact of this option: enabling `O_DIRECT` bypasses and prevents contamination of the OS buffer cache, but the subsequent file reads require re-reading the contents to the buffer cache.
+ Default value: `false`
### `rate-bytes-per-sec`

+ When Titan is disabled, this configuration item limits the I/O rate of RocksDB compaction to reduce the impact of RocksDB compaction on the foreground read and write performance during traffic peaks. When Titan is enabled, this configuration item limits the summed I/O rates of RocksDB compaction and Titan GC. If you find that the I/O or CPU consumption of RocksDB compaction and Titan GC is too large, set this configuration item to an appropriate value according the disk I/O bandwidth and the actual write traffic.
+ Default value: `10GiB`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `rate-limiter-refill-period`

+ Controls how often I/O tokens are refilled. A smaller value reduces I/O bursts but causes more CPU overhead.
+ Default value: `"100ms"`
### `rate-limiter-mode`

+ RocksDB's compaction rate limiter mode
+ Optional values: `"read-only"`, `"write-only"`, `"all-io"`
+ Default value: `"write-only"`
### `rate-limiter-auto-tuned` New in v5.0

+ Determines whether to automatically optimize the configuration of the RocksDB's compaction rate limiter based on recent workload. When this configuration is enabled, compaction pending bytes will be slightly higher than usual.
+ Default value: `true`
### `enable-pipelined-write`

+ Controls whether to enable Pipelined Write. When this configuration is enabled, the previous Pipelined Write is used. When this configuration is disabled, the new Pipelined Commit mechanism is used.
+ Default value: `false`
### `bytes-per-sync`

+ The rate at which OS incrementally synchronizes files to disk while these files are being written asynchronously
+ Default value: `"1MiB"`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `wal-bytes-per-sync`

+ The rate at which OS incrementally synchronizes WAL files to disk while the WAL files are being written
+ Default value: `"512KiB"`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `info-log-max-size`

> **Warning:**
>
> Starting from v5.4.0, RocksDB logs are managed by the logging module of TiKV. Therefore, this configuration item is deprecated, and its function is replaced by the configuration item [`log.file.max-size`](#max-size-new-in-v540).

+ The maximum size of Info log
+ Default value: `"1GiB"`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `info-log-roll-time`

> **Warning:**
>
> Starting from v5.4.0, RocksDB logs are managed by the logging module of TiKV. Therefore, this configuration item is deprecated. TiKV no longer supports automatic log splitting based on time. Instead, you can use the configuration item [`log.file.max-size`](#max-size-new-in-v540) to set the threshold for automatic log splitting based on file size.

+ The time interval at which Info logs are truncated. If the value is `0s`, logs are not truncated.
+ Default value: `"0s"`
### `info-log-keep-log-file-num`

> **Warning:**
>
> Starting from v5.4.0, RocksDB logs are managed by the logging module of TiKV. Therefore, this configuration item is deprecated, and its function is replaced by the configuration item [`log.file.max-backups`](#max-backups-new-in-v540).

+ The maximum number of kept log files
+ Default value: `10`
+ Minimum value: `0`
### `info-log-dir`

+ The directory in which logs are stored
+ Default value: `""`
### `info-log-level`

> **Warning:**
>
> Starting from v5.4.0, RocksDB logs are managed by the logging module of TiKV. Therefore, this configuration item is deprecated, and its function is replaced by the configuration item [`log.level`](#level-new-in-v540).

+ Log levels of RocksDB
+ Default value: `"info"`
### `write-buffer-flush-oldest-first` New in v6.6.0

> **Warning:**
>
> This feature is experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

+ Specifies the flush strategy used when the memory usage of `memtable` of the current RocksDB reaches the threshold.
+ Default value: `false`
+ Value options:

    + `false`: `memtable` with the largest data volume is flushed to SST files.
    + `true`: The earliest `memtable` is flushed to SST files. This strategy can clear the `memtable` of cold data, which is suitable for scenarios with obvious cold and hot data.
### `write-buffer-limit` New in v6.6.0

> **Warning:**
>
> This feature is experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

+ Specifies the total memory limit of `memtable` for all RocksDB instances in a single TiKV. `0` means no limit.
+ Default value:

    + When `storage.engine="raft-kv"`, the default value is `0`, which means no limit.
    + When `storage.engine="partitioned-raft-kv"`, the default value is 20% of the size of total system memory.

+ Unit: KiB|MiB|GiB
### `track-and-verify-wals-in-manifest` New in v6.5.9, v7.1.5, v7.5.2, and v8.0.0

+ Controls whether to record information about Write Ahead Log (WAL) files in the RocksDB MANIFEST file and whether to verify the integrity of WAL files during startup. For more information, see RocksDB [Track WAL in MANIFEST](https://github.com/facebook/rocksdb/wiki/Track-WAL-in-MANIFEST).
+ Default value: `true`
+ Value options:
    + `true`: records information about WAL files in the MANIFEST file and verifies the integrity of WAL files during startup.
    + `false`: does not record information about WAL files in the MANIFEST file and does not verify the integrity of WAL files during startup.
### `enable-multi-batch-write` New in v6.2.0

+ Controls whether to enable RocksDB write optimization, allowing the contents of WriteBatch to be written concurrently to the memtable, reducing write latency.
+ Default value: None. However, it is enabled by default unless explicitly set to `false` or if `rocksdb.enable-pipelined-write` or `rocksdb.enable-unordered-write` is enabled.
