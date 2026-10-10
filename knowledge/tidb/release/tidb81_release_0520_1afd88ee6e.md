# 7.5.0 compatibility, offline package, and deprecations

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.0.md`
- Source Title: `TiDB 7.5.0 Release Notes`
- Source Heading Path: `TiDB 7.5.0 Release Notes > Compatibility changes > Configuration file parameters | TiDB 7.5.0 Release Notes > Offline package changes | TiDB 7.5.0 Release Notes > Deprecated features`
- Source Line Ranges: `170-211`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `dumpling`, `lightning`, `ticdc`, `tidb`, `tikv`
- Topic Tags: `compatibility`, `configuration`, `offline-packages`, `deprecation`, `system-variables`, `backup`, `cdc`, `import`, `statistics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0520_1afd88ee6e`
- Source ID: `tidb-docs-8.1:releases/release-7.5.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `77e5bbf06484ea39c5063cabfc2667ea1bf911dd0e8ed21c4a29fb71377cfaae`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.0 compatibility changes, newly added or modified configuration parameters, offline package removals, or deprecated features across TiDB, TiKV, BR, TiCDC, TiDB Lightning, and statistics.
- Retrieval Keywords: TiDB 7.5.0 compatibility changes, tikv-client.copr-req-timeout, raftstore.inspect-interval, raftstore.region-compact-min-redundant-rows, raftstore.region-compact-redundant-rows-percent, raftstore.evict-cache-on-memory-ratio, memory.enable-heap-profiling, memory.profiling-sample-per-bytes, --ignore-stats, case-sensitive, sink.dispatchers.partition, changefeed-error-stuck-duration, encoding-worker-num, flush-worker-num, sink.column-selectors, sql-mode, TiDB Lightning --importer deleted, TiDB-community-toolkit removed contents, tikv-importer-{version}-linux-{arch}.tar.gz, mydumper deprecated, TiKV-importer deprecated, TiDB Binlog technical support no longer provided, Fast Analyze deprecated, incremental collection deprecated
- Follow-up Guidance: The chunk also points to alternatives such as Dumpling for Mydumper, the Physical Import Mode of TiDB Lightning for TiKV-importer, TiCDC for data replication, and PITR for data recovery.
- Classification Note: This is a release-notes compatibility and deprecation section because the content lists configuration file parameter changes, offline package changes, and deprecated features introduced in TiDB 7.5.0.

## Official Source Content

### Configuration file parameters

| Configuration file | Configuration parameter | Change type | Description |
| -------- | -------- | -------- | -------- |
| TiDB | [`tikv-client.copr-req-timeout`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#copr-req-timeout-new-in-v750) | Newly added | Sets the timeout of a single Coprocessor request. |
| TiKV | [`raftstore.inspect-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#inspect-interval) | Modified | Changes the default value from `500ms` to `100ms` after optimizing the algorithm to improve the sensitivity of slow node detection. |
| TiKV | [`raftstore.region-compact-min-redundant-rows`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-compact-min-redundant-rows-new-in-v710) | Modified | Sets the number of redundant MVCC rows required to trigger RocksDB compaction. Starting from v7.5.0, this configuration item takes effect for the `"raft-kv"` storage engine. |
| TiKV | [`raftstore.region-compact-redundant-rows-percent`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-compact-redundant-rows-percent-new-in-v710) | Modified | Sets the percentage of redundant MVCC rows required to trigger RocksDB compaction. Starting from v7.5.0, this configuration item takes effect for the `"raft-kv"` storage engine. |
| TiKV | [`raftstore.evict-cache-on-memory-ratio`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#evict-cache-on-memory-ratio-new-in-v750) | Newly added | When the memory usage of TiKV exceeds 90% of the system available memory, and the memory occupied by Raft entry cache exceeds the `evict-cache-on-memory-ratio` of used memory, TiKV evicts the Raft entry cache. |
| TiKV | [`memory.enable-heap-profiling`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-heap-profiling-new-in-v750) | Newly added | Controls whether to enable Heap Profiling to track the memory usage of TiKV. |
| TiKV | [`memory.profiling-sample-per-bytes`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#profiling-sample-per-bytes-new-in-v750) | Newly added | Specifies the amount of data sampled by Heap Profiling each time, rounding up to the nearest power of 2. |
| BR | [`--ignore-stats`](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-statistics) | Newly added | Controls whether to back up and restore database statistics. When you set this parameter to `false`, the br command-line tool supports backing up and restoring statistics of columns, indexes, and tables. |
| TiCDC | [`case-sensitive`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Modified | Changes the default value from `true` to `false` after further tests, which means that the table names and database names in the TiCDC configuration file are case-insensitive by default. |
| TiCDC | [`sink.dispatchers.partition`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Modified | Controls how TiCDC dispatches incremental data to Kafka partitions. v7.5.0 introduces a new value option `columns`, which uses the explicitly specified column values to calculate the partition number. |
| TiCDC | [`changefeed-error-stuck-duration`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Newly added | Controls the duration for which the changefeed is allowed to automatically retry when internal errors or exceptions occur. |
| TiCDC | [`encoding-worker-num`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Newly added | Controls the number of encoding and decoding workers in the redo module. |
| TiCDC | [`flush-worker-num`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Newly added | Controls the number of flushing workers in the redo module. |
| TiCDC | [`sink.column-selectors`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Newly added | Controls the specified columns of data change events that TiCDC sends to Kafka when dispatching incremental data. |
| TiCDC | [`sql-mode`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Newly added | Specifies the SQL mode used by TiCDC when parsing DDL statements. The default value is the same as the default SQL mode of TiDB. |
| TiDB Lightning | `--importer` | Deleted | Specifies the address of TiKV-importer, which is deprecated in v7.5.0. |
## Offline package changes

Starting from v7.5.0, the following contents are removed from the `TiDB-community-toolkit` [binary package](https://docs.pingcap.com/tidb/stable/binary-package):

- `tikv-importer-{version}-linux-{arch}.tar.gz`
- `mydumper`
- `spark-{version}-any-any.tar.gz`
- `tispark-{version}-any-any.tar.gz`
## Deprecated features

* [Mydumper](https://docs.pingcap.com/tidb/v4.0/mydumper-overview) is deprecated in v7.5.0 and most of its features have been replaced by [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview). It is strongly recommended that you use Dumpling instead of Mydumper.

* TiKV-importer is deprecated in v7.5.0. It is strongly recommended that you use the [Physical Import Mode of TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode) as an alternative.

* Starting from TiDB v7.5.0, technical support for the data replication feature of [TiDB Binlog](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview) is no longer provided. It is strongly recommended to use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) as an alternative solution for data replication. Although TiDB Binlog v7.5.0 still supports the Point-in-Time Recovery (PITR) scenario, this component will be completely deprecated in future versions. It is recommended to use [PITR](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) as an alternative solution for data recovery.

* The [`Fast Analyze`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_fast_analyze) feature (experimental) for statistics is deprecated in v7.5.0.

* The [incremental collection](https://docs.pingcap.com/tidb/v7.4/statistics#incremental-collection) feature (experimental) for statistics is deprecated in v7.5.0.
