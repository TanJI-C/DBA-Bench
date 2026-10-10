# RaftDB storage engine configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > raftdb | TiKV Configuration File > raftdb > `max-background-jobs` | TiKV Configuration File > raftdb > `max-sub-compactions` | TiKV Configuration File > raftdb > `max-open-files` | TiKV Configuration File > raftdb > `max-manifest-file-size` | TiKV Configuration File > raftdb > `create-if-missing` | TiKV Configuration File > raftdb > `stats-dump-period` | TiKV Configuration File > raftdb > `wal-dir` | TiKV Configuration File > raftdb > `wal-ttl-seconds` | TiKV Configuration File > raftdb > `wal-size-limit` | TiKV Configuration File > raftdb > `max-total-wal-size` | TiKV Configuration File > raftdb > `compaction-readahead-size` | TiKV Configuration File > raftdb > `writable-file-max-buffer-size` | TiKV Configuration File > raftdb > `use-direct-io-for-flush-and-compaction` | TiKV Configuration File > raftdb > `enable-pipelined-write` | TiKV Configuration File > raftdb > `allow-concurrent-memtable-write` | TiKV Configuration File > raftdb > `bytes-per-sync``
- Source Line Ranges: `1859-1962`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `raftdb`, `rocksdb`, `wal`, `compaction`, `io`, `thread-pool`, `pipelined-write`, `sync`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0379_acd6d44149`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#raftdb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f271c0eff30c7207a9b9737687e0e9cf621dad6df7ddcaaf2bb6536a415d95c1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raftdb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for raftdb configuration items in TiKV, especially RocksDB thread, WAL, compaction, I/O, pipelined write, and sync related settings.
- Retrieval Keywords: raftdb, max-background-jobs, max-sub-compactions, max-open-files, max-manifest-file-size, create-if-missing, stats-dump-period, wal-dir, wal-ttl-seconds, wal-size-limit, max-total-wal-size, compaction-readahead-size, writable-file-max-buffer-size, use-direct-io-for-flush-and-compaction, enable-pipelined-write, allow-concurrent-memtable-write, bytes-per-sync, RocksDB WAL, O_DIRECT, Pipelined Write, Pipelined Commit
- Follow-up Guidance: The source includes a note that raftdb.wal-dir must not be set to the same value as rocksdb.wal-dir.
- Classification Note: This is classified as configuration because the content lists TiKV raftdb configuration parameters and their documented defaults, limits, and effects.

## Official Source Content

## raftdb

Configuration items related to `raftdb`
### `max-background-jobs`

+ The number of background threads in RocksDB. When you modify the size of the RocksDB thread pool, refer to [Performance tuning for TiKV thread pools](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance#performance-tuning-for-tikv-thread-pools).
+ Default value: `4`
+ Minimum value: `2`
### `max-sub-compactions`

+ The number of concurrent sub-compaction operations performed in RocksDB
+ Default value: `2`
+ Minimum value: `1`
### `max-open-files`

+ The total number of files that RocksDB can open
+ Default value: `40960`
+ Minimum value: `-1`
### `max-manifest-file-size`

+ The maximum size of a RocksDB Manifest file
+ Default value: `"20MiB"`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `create-if-missing`

+ If the value is `true`, the database will be created if it is missing
+ Default value: `true`
### `stats-dump-period`

+ The interval at which statistics are output to the log
+ Default value: `10m`
### `wal-dir`

+ The directory in which Raft RocksDB WAL files are stored, which is the absolute directory path for WAL. **Do not** set this configuration item to the same value as [`rocksdb.wal-dir`](#wal-dir).
+ If this configuration item is not set, the log files are stored in the same directory as data.
+ If there are two disks on the machine, storing RocksDB data and WAL logs on different disks can improve performance.
+ Default value: `""`
### `wal-ttl-seconds`

+ Specifies how long the archived WAL files are retained. When the value is exceeded, the system deletes these files.
+ Default value: `0`
+ Minimum value: `0`
+ Unit: second
### `wal-size-limit`

+ The size limit of the archived WAL files. When the value is exceeded, the system deletes these files.
+ Default value: `0`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
### `max-total-wal-size`

+ The maximum RocksDB WAL size in total
+ Default value:
    + When `storage.engine="raft-kv"`, the default value is `"4GiB"`.
    + When `storage.engine="partitioned-raft-kv"`, the default value is `1`.
### `compaction-readahead-size`

+ Controls whether to enable the readahead feature during RocksDB compaction and specify the size of readahead data.
+ If you use mechanical disks, it is recommended to set the value to `2MiB` at least.
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
### `enable-pipelined-write`

+ Controls whether to enable Pipelined Write. When this configuration is enabled, the previous Pipelined Write is used. When this configuration is disabled, the new Pipelined Commit mechanism is used.
+ Default value: `true`
### `allow-concurrent-memtable-write`

+ Controls whether to enable concurrent memtable write.
+ Default value: `true`
### `bytes-per-sync`

+ The rate at which OS incrementally synchronizes files to disk while these files are being written asynchronously
+ Default value: `"1MiB"`
+ Minimum value: `0`
+ Unit: B|KiB|MiB|GiB
