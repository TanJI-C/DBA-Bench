# RaftDB log settings and Raft Engine configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > raftdb > `wal-bytes-per-sync` | TiKV Configuration File > raftdb > `info-log-max-size` | TiKV Configuration File > raftdb > `info-log-roll-time` | TiKV Configuration File > raftdb > `info-log-keep-log-file-num` | TiKV Configuration File > raftdb > `info-log-dir` | TiKV Configuration File > raftdb > `info-log-level` | TiKV Configuration File > raft-engine | TiKV Configuration File > raft-engine > `enable` | TiKV Configuration File > raft-engine > `dir` | TiKV Configuration File > raft-engine > `batch-compression-threshold` | TiKV Configuration File > raft-engine > `bytes-per-sync` | TiKV Configuration File > raft-engine > `target-file-size` | TiKV Configuration File > raft-engine > `purge-threshold` | TiKV Configuration File > raft-engine > `recovery-mode` | TiKV Configuration File > raft-engine > `recovery-read-block-size` | TiKV Configuration File > raft-engine > `recovery-threads` | TiKV Configuration File > raft-engine > `memory-limit` | TiKV Configuration File > raft-engine > `format-version` <span class="version-mark">New in v6.3.0</span> | TiKV Configuration File > raft-engine > `enable-log-recycle` <span class="version-mark">New in v6.3.0</span> | TiKV Configuration File > raft-engine > `prefill-for-recycle` <span class="version-mark">New in v7.0.0</span> | TiKV Configuration File > raft-engine > `compression-level` <span class="version-mark">New in v7.4.0</span>`
- Source Line Ranges: `1963-2126`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `raftdb`, `raft-engine`, `wal`, `logging`, `deprecation`, `recovery`, `downgrade`, `compression`, `storage-engine`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0380_92915271aa`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#wal-bytes-per-sync`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cb302eeaa388487ca75c974a14dc080b17ba2df3b694095f14ec7596a26323bb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#wal-bytes-per-sync
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiKV raftdb log settings or Raft Engine configuration such as deprecations, recovery behavior, log recycling, compression, startup migration, or downgrade notes.
- Retrieval Keywords: wal-bytes-per-sync, info-log-max-size, info-log-roll-time, info-log-keep-log-file-num, info-log-dir, info-log-level, raft-engine, enable, dir, batch-compression-threshold, bytes-per-sync, target-file-size, purge-threshold, recovery-mode, recovery-read-block-size, recovery-threads, memory-limit, format-version, enable-log-recycle, prefill-for-recycle, compression-level, log.file.max-size, log.file.max-backups, log.level, absolute-consistency, tolerate-tail-corruption, tolerate-any-corruption, storage.engine="raft-kv", storage.engine="partitioned-raft-kv"
- Follow-up Guidance: The content also states that enabling Raft Engine for the first time causes TiKV to transfer data from RocksDB to Raft Engine and that certain downgrade cases require disabling Raft Engine and restarting TiKV before the downgrade.
- Classification Note: This is classified as configuration for the TiKV component because the content defines TiKV configuration items under raftdb and raft-engine, including defaults, value options, deprecation warnings, and notes.

## Official Source Content

### `wal-bytes-per-sync`

+ The rate at which OS incrementally synchronizes WAL files to disk when the WAL files are being written
+ Default value: `"512KiB"`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `info-log-max-size`

> **Warning:**
>
> Starting from v5.4.0, RocksDB logs are managed by the logging module of TiKV. Therefore, this configuration item is deprecated, and its function is replaced by the configuration item [`log.file.max-size`](#max-size-new-in-v540).

+ The maximum size of Info logs
+ Default value: `"1GiB"`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `info-log-roll-time`

> **Warning:**
>
> Starting from v5.4.0, RocksDB logs are managed by the logging module of TiKV. Therefore, this configuration item is deprecated. TiKV no longer supports automatic log splitting based on time. Instead, you can use the configuration item [`log.file.max-size`](#max-size-new-in-v540) to set the threshold for automatic log splitting based on file size.

+ The interval at which Info logs are truncated. If the value is `0s`, logs are not truncated.
+ Default value: `"0s"` (which means logs are not truncated)
### `info-log-keep-log-file-num`

> **Warning:**
>
> Starting from v5.4.0, RocksDB logs are managed by the logging module of TiKV. Therefore, this configuration item is deprecated, and its function is replaced by the configuration item [`log.file.max-backups`](#max-backups-new-in-v540).

+ The maximum number of Info log files kept in RaftDB
+ Default value: `10`
+ Minimum value: `0`
### `info-log-dir`

+ The directory in which Info logs are stored
+ Default value: `""`
### `info-log-level`

> **Warning:**
>
> Starting from v5.4.0, RocksDB logs are managed by the logging module of TiKV. Therefore, this configuration item is deprecated, and its function is replaced by the configuration item [`log.level`](#level-new-in-v540).

+ Log levels of RaftDB
+ Default value: `"info"`
## raft-engine

Configuration items related to Raft Engine.

> **Note:**
>
> - When you enable Raft Engine for the first time, TiKV transfers its data from RocksDB to Raft Engine. Therefore, you need to wait extra tens of seconds for TiKV to start.
> - The data format of Raft Engine in TiDB v5.4.0 is not compatible with earlier TiDB versions. Therefore, if you need to downgrade a TiDB cluster from v5.4.0 to an earlier version, **before** downgrading, disable Raft Engine by setting `enable` to `false` and restart TiKV for the configuration to take effect.
### `enable`

+ Determines whether to use Raft Engine to store Raft logs. When it is enabled, configurations of `raftdb` are ignored.
+ Default value: `true`
### `dir`

+ The directory at which raft log files are stored. If the directory does not exist, it will be created when TiKV is started.
+ If this configuration item is not set, `{data-dir}/raft-engine` is used.
+ If there are multiple disks on your machine, it is recommended to store the data of Raft Engine on a different disk to improve TiKV performance.
+ Default value: `""`
### `batch-compression-threshold`

+ Specifies the threshold size of a log batch. A log batch larger than this configuration is compressed. If you set this configuration item to `0`, compression is disabled.
+ Default value: `"4KiB"`. Before v8.1.0, the default value is `"8KiB"`.
### `bytes-per-sync`

> **Warning:**
>
> Starting from v6.5.0, Raft Engine writes logs to disk directly without buffering. Therefore, this configuration item is deprecated and no longer functional.

+ Specifies the maximum accumulative size of buffered writes. When this configuration value is exceeded, buffered writes are flushed to the disk.
+ If you set this configuration item to `0`, incremental sync is disabled.
+ Before v6.5.0, the default value is `"4MiB"`.
### `target-file-size`

+ Specifies the maximum size of log files. When a log file is larger than this value, it is rotated.
+ Default value: `"128MiB"`
### `purge-threshold`

+ Specifies the threshold size of the main log queue. When this configuration value is exceeded, the main log queue is purged.
+ This configuration can be used to adjust the disk space usage of Raft Engine.
+ Default value: `"10GiB"`
### `recovery-mode`

+ Determines how to deal with file corruption during recovery.
+ Value options: `"absolute-consistency"`, `"tolerate-tail-corruption"`, `"tolerate-any-corruption"`
+ Default value: `"tolerate-tail-corruption"`
### `recovery-read-block-size`

+ The minimum I/O size for reading log files during recovery.
+ Default value: `"16KiB"`
+ Minimum value: `"512B"`
### `recovery-threads`

+ The number of threads used to scan and recover log files.
+ Default value: `4`
+ Minimum value: `1`
### `memory-limit`

+ Specifies the limit on the memory usage of Raft Engine.
+ When this configuration value is not set, 15% of the available system memory is used.
+ Default value: `Total machine memory * 15%`
### `format-version` New in v6.3.0

> **Note:**
>
> After `format-version` is set to `2`, if you need to downgrade a TiKV cluster from v6.3.0 to an earlier version, take the following steps **before** the downgrade:
>
> 1. Disable Raft Engine by setting [`enable`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-1) to `false` and restart TiKV to make the configuration take effect.
> 2. Set `format-version` to `1`.
> 3. Enable Raft Engine by setting `enable` to `true` and restart TiKV to make the configuration take effect.

+ Specifies the version of log files in Raft Engine.
+ Value Options:
    + `1`: Default log file version for TiKV earlier than v6.3.0. Can be read by TiKV >= v6.1.0.
    + `2`: Supports log recycling. Can be read by TiKV >= v6.3.0.
+ Default value:
    + When `storage.engine="raft-kv"`, the default value is `2`.
    + When `storage.engine="partitioned-raft-kv"`, the default value is `5`.
### `enable-log-recycle` New in v6.3.0

> **Note:**
>
> This configuration item is only available when [`format-version`](#format-version-new-in-v630) >= 2.

+ Determines whether to recycle stale log files in Raft Engine. When it is enabled, logically purged log files will be reserved for recycling. This reduces the long tail latency on write workloads.
+ Default value: `true`
### `prefill-for-recycle` New in v7.0.0

> **Note:**
>
> This configuration item only takes effect when [`enable-log-recycle`](#enable-log-recycle-new-in-v630) is set to `true`.

+ Determines whether to generate empty log files for log recycling in Raft Engine. When it is enabled, Raft Engine will automatically fill a batch of empty log files for log recycling during initialization, making log recycling effective immediately after initialization.
+ Default value: `false`
### `compression-level` New in v7.4.0

+ Sets the compression efficiency of the LZ4 algorithm used by Raft Engine when writing Raft log files. A lower value indicates faster compression speed but lower compression ratio.
+ Range: `[1, 16]`
+ Default value: `1`
