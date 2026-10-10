# Compatibility changes for configuration parameters and system tables

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.6.0.md`
- Source Title: `TiDB 7.6.0 Release Notes`
- Source Heading Path: `TiDB 7.6.0 Release Notes > Compatibility changes > Configuration file parameters | TiDB 7.6.0 Release Notes > Compatibility changes > System tables`
- Source Line Ranges: `280-310`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `lightning`, `pd`, `sql`, `ticdc`, `tidb`, `tiflash`, `tikv`
- Topic Tags: `compatibility`, `configuration`, `system-tables`, `tls`, `compression`, `gc`, `compaction`, `resolved-ts`, `resource-control`, `keywords`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0565_1a8e4b3070`
- Source ID: `tidb-docs-8.1:releases/release-7.6.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b5f2ff613af305803ac3741495f3d02fa2c932a4a226677defd4e476b44e7a78`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.6.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.6.0 compatibility changes for configuration parameters or system table fields across TiDB, TiKV, TiFlash, TiDB Lightning, BR, and TiCDC.
- Retrieval Keywords: TiDB 7.6.0 compatibility changes, tls-version, TLS1.2 or higher, raftstore.report-min-resolved-ts-interval, raftstore.pd-report-min-resolved-ts-interval, blob-file-compression, zstd, rocksdb.defaultcf.titan.min-blob-size, rocksdb.titan.enabled, cdc.incremental-scan-concurrency-limit, gc.num-threads, raftstore.periodic-full-compact-start-times, raftstore.periodic-full-compact-start-max-cpu, zstd-dict-size, logger.level, tidb.pd-addr, multiple PD addresses, block-size, backend='local', BR --granularity, coarse-grained Region scatter, TiCDC compression, sink.cloud-storage-config, INFORMATION_SCHEMA.KEYWORDS, INFORMATION_SCHEMA.SLOW_QUERY, Resource_group, Request_unit_read, Request_unit_write, Time_queued_by_rc
- Follow-up Guidance: The source also states that INFORMATION_SCHEMA.SLOW_QUERY adds Resource_group, Request_unit_read, Request_unit_write, and Time_queued_by_rc fields, and that INFORMATION_SCHEMA.KEYWORDS is newly added.
- Classification Note: This is a release-note compatibility summary because the official content lists modified, renamed, and newly added configuration items plus system table changes in TiDB 7.6.0.

## Official Source Content

### Configuration file parameters

| Configuration file | Configuration parameter | Change type | Description |
| -------- | -------- | -------- | -------- |
| TiDB | [`tls-version`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tls-version) | Modified | The default value is "". The default supported TLS versions of TiDB are changed from `TLS1.1` or higher to `TLS1.2` or higher. |
| TiKV | [`raftstore.report-min-resolved-ts-interval`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file/#report-min-resolved-ts-interval-new-in-v600) | Renamed | To make the name more accurate, this configuration item is renamed to [`raftstore.pd-report-min-resolved-ts-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#pd-report-min-resolved-ts-interval-new-in-v760). `raftstore.report-min-resolved-ts-interval` is no longer effective. |
| TiKV | [`blob-file-compression`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#blob-file-compression) | Modified | The algorithm used for compressing values in Titan, which takes value as the unit. Starting from TiDB v7.6.0, the default compression algorithm is `zstd`. |
| TiKV | [`rocksdb.defaultcf.titan.min-blob-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-blob-size) | Modified   | Starting from TiDB v7.6.0, the default value for new clusters is `32KB`. For existing clusters upgrading to v7.6.0, the default value `1KB` remains unchanged. |
| TiKV | [`rocksdb.titan.enabled`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enabled) | Modified  |  Enables or disables Titan. For v7.5.0 and earlier versions, the default value is `false`. Starting from v7.6.0, the default value is `true` for only new clusters. Existing clusters upgraded to v7.6.0 or later versions will retain the original configuration. |
| TiKV | [`cdc.incremental-scan-concurrency-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#incremental-scan-concurrency-limit-new-in-v760) | Newly added | Sets the maximum queue length for the tasks of incrementally scanning historical data waiting to be executed. The default value is `10000`, which means that at most 10000 tasks can be queued for execution. |
| TiKV | [`gc.num-threads`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#num-threads-new-in-v658-v714-v751-and-v760) | Newly added | When `enable-compaction-filter` is set to `false`, this parameter controls the number of GC threads. The default value is `1`. |
| TiKV | [`raftstore.periodic-full-compact-start-times`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#periodic-full-compact-start-times-new-in-v760) | Newly added | Sets the specific times that TiKV initiates periodic full compaction. The default value `[]` means periodic full compaction is disabled. |
| TiKV | [`raftstore.periodic-full-compact-start-max-cpu`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#periodic-full-compact-start-max-cpu-new-in-v760) | Newly added | Limits the maximum CPU usage rate for TiKV periodic full compaction. The default value is `0.1`. |
| TiKV | [`raftstore.pd-report-min-resolved-ts-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#pd-report-min-resolved-ts-interval-new-in-v760) | Newly added | Renamed from [`raftstore.report-min-resolved-ts-interval`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file#report-min-resolved-ts-interval-new-in-v600). It specifies the minimum interval for TiKV to report Resolved TS to the PD leader. The default value is `"1s"`. |
| TiKV | [`zstd-dict-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#zstd-dict-size) |  Newly added | Specifies the `zstd` dictionary compression size. The default value is `"0KB"`, which means to disable the `zstd` dictionary compression. |
| TiFlash | [`logger.level`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) | Modified | Changes the default value from `"debug"` to `"INFO"` to reduce the cost of logging. |
| TiDB Lightning| [`tidb.pd-addr`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) | Modified  | Configures the addresses of the PD Servers. Starting from v7.6.0, TiDB supports setting multiple PD addresses. |
| TiDB Lightning | [`block-size`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) | Newly added | Controls the I/O block size for sorting local files in Physical Import Mode (`backend='local'`). The default value is `16KiB`. When the disk IOPS is a bottleneck, you can increase this value to improve performance. |
| BR | [`--granularity`](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide#performance-and-impact-of-snapshot-restore) | Newly added | Uses the coarse-grained Region scatter algorithm (experimental) by specifying `--granularity="coarse-grained"`. This accelerates restore speed in large-scale Region scenarios. |
| TiCDC | [`compression`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Newly added | Controls the behavior to compress redo log files. |
| TiCDC | [`sink.cloud-storage-config`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Newly added | Sets the automatic cleanup of historical data when replicating data to object storage. |
### System tables

- Add a new system table [`INFORMATION_SCHEMA.KEYWORDS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-keywords) to display the information of all keywords supported by TiDB.
- In the system table [`INFORMATION_SCHEMA.SLOW_QUERY`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-slow-query), add the following fields related to Resource Control:
    - `Resource_group`: the resource group that the statement is bound to.
    - `Request_unit_read`: the total read RUs consumed by the statement.
    - `Request_unit_write`: the total write RUs consumed by the statement.
    - `Time_queued_by_rc`: the total time that the statement waits for available resources.
