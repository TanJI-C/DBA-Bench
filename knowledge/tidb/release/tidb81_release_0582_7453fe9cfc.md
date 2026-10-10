# Compatibility changes for configuration parameters and system tables

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Compatibility changes > Configuration file parameters | TiDB 8.0.0 Release Notes > Compatibility changes > System tables`
- Source Line Ranges: `327-359`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `lightning`, `dm`, `ticdc`
- Topic Tags: `compatibility`, `configuration-parameters`, `system-tables`, `index-usage`, `tls`, `deprecation`, `release-notes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0582_7453fe9cfc`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d582f1ae03bd35d8a3151b583be9669bdddfafd5d209d13ba0950c73092fa95e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.0.0 compatibility changes to configuration parameters or newly added system tables and views related to index usage, TLS, logging, TiKV, PD, Lightning, DM, or TiCDC settings.
- Retrieval Keywords: TiDB 8.0.0 compatibility changes, instance.tidb_enable_collect_execution_info, INFORMATION_SCHEMA.TIDB_INDEX_USAGE, INFORMATION_SCHEMA.CLUSTER_TIDB_INDEX_USAGE, sys.schema_unused_indexes, sys schema, tls-version TLSv1.2 TLSv1.3, log.file.compression, log.general-log-file, tikv-client.enable-replica-selector-v2, log-backup.initial-scan-rate-limit, raftstore.store-io-pool-size, rocksdb.defaultcf.titan.blob-cache-size, rocksdb.defaultcf.titan.shared-blob-cache, rocksdb.titan.max-background-gc, security.encryption.master-key.vendor gcp, security.encryption.master-key.gcp.credential-file-path, storage.block-cache.low-pri-pool-ratio, schedule.enable-heartbeat-breakdown-metrics, schedule.enable-heartbeat-concurrent-runner, tikv-importer.duplicate-resolution, conflict.precheck-conflict-before-import, logical-import-batch-rows, logical-import-batch-size, secret-key-path, debezium-disable-schema, tls-certificate-file, tls-key-file-path
- Follow-up Guidance: The source also states that TiDB 8.0.0 adds INFORMATION_SCHEMA.TIDB_INDEX_USAGE, INFORMATION_SCHEMA.CLUSTER_TIDB_INDEX_USAGE, the sys schema, and the sys.schema_unused_indexes view.
- Classification Note: This is classified as a release compatibility chunk because the official content enumerates modified, newly added, and deprecated configuration parameters plus added system tables and views in TiDB 8.0.0.

## Official Source Content

### Configuration file parameters

| Configuration file | Configuration parameter | Change type | Description |
| -------- | -------- | -------- | -------- |
| TiDB | [`instance.tidb_enable_collect_execution_info`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_enable_collect_execution_info) | Modified | Adds a control to whether to record the [usage statistics of indexes](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-index-usage). The default value is `true`. |
| TiDB | [`tls-version`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tls-version) | Modified | This parameter no longer supports `"TLSv1.0"` and `"TLSv1.1"`. Now it only supports `"TLSv1.2"` and `"TLSv1.3"`. |
| TiDB  | [`log.file.compression`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#compression-new-in-v800) | Newly added | Specifies the compression format of the polling log. The default value is null, which means that the polling log is not compressed. |
| TiDB  | [`log.general-log-file`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#general-log-file-new-in-v800) | Newly added | Specifies the file to save the general log to. The default is null, which means that the general log will be written to the instance file. |
| TiDB | [`tikv-client.enable-replica-selector-v2`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-replica-selector-v2-new-in-v800) | Newly added | Controls whether to use the new version of the Region replica selector when sending RPC requests to TiKV. The default value is `true`. |
| TiKV | [`log-backup.initial-scan-rate-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#initial-scan-rate-limit-new-in-v620) | Modified | Adds a limit of `1MiB` as the minimum value. |
| TiKV | [`raftstore.store-io-pool-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#store-io-pool-size-new-in-v530) | Modified | Changes the default value from `0` to `1` to improve TiKV performance, meaning that the size of the StoreWriter thread pool now defaults to `1`. |
| TiKV | [`rocksdb.defaultcf.titan.blob-cache-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#blob-cache-size) | Modified | Starting from v8.0.0, TiKV introduces the `shared-blob-cache` configuration item and enables it by default, so there is no need to set `blob-cache-size` separately. The configuration of `blob-cache-size` only takes effect when `shared-blob-cache` is set to `false`. |
| TiKV | [`rocksdb.titan.max-background-gc`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#max-background-gc) | Modified | Changes the default value from `4` to `1` to reduce the occupation of thread resources by the Titan GC process. |
| TiKV | [`security.encryption.master-key.vendor`](https://docs.pingcap.com/tidb/stable/encryption-at-rest#specify-a-master-key-via-kms) | Modified | Adds `gcp` as an available type for the service provider. |
| TiKV | [`storage.block-cache.low-pri-pool-ratio`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#low-pri-pool-ratio-new-in-v800) | Newly added | Specifies the proportion of the entire block cache that the Titan component can use. The default value is `0.2`. |
| TiKV | [`rocksdb.defaultcf.titan.shared-blob-cache`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#shared-blob-cache-new-in-v800) | Newly added | Controls whether to enable the shared cache for Titan blob files and RocksDB block files. The default value is `true`. |
| TiKV | [`security.encryption.master-key.gcp.credential-file-path`](https://docs.pingcap.com/tidb/stable/encryption-at-rest#specify-a-master-key-via-kms) | Newly added | Specifies the path to the Google Cloud authentication credentials file when `security.encryption.master-key.vendor` is `gcp`. |
| PD | [`schedule.enable-heartbeat-breakdown-metrics`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-heartbeat-breakdown-metrics-new-in-v800) | Newly added | Controls whether to enable breakdown metrics for Region heartbeats. These metrics measure the time consumed in each stage of Region heartbeat processing, facilitating analysis through monitoring. The default value is `true`. |
| PD | [`schedule.enable-heartbeat-concurrent-runner`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-heartbeat-concurrent-runner-new-in-v800) | Newly added | Controls whether to enable asynchronous concurrent processing for Region heartbeats. When enabled, an independent executor handles Region heartbeat requests asynchronously and concurrently, which can improve heartbeat processing throughput and reduce latency. The default value is `true`. |
| TiDB Lightning  | [`tikv-importer.duplicate-resolution`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#the-old-version-of-conflict-detection-deprecated-in-v800)  | Deprecated | Controls whether to detect and resolve unique key conflicts in physical import mode. Starting from v8.0.0, it is replaced by [`conflict.strategy`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task). |
| TiDB Lightning  | [`conflict.precheck-conflict-before-import`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task)  | Newly added | Controls whether to enable preprocess conflict detection, which checks conflicts in data before importing it to TiDB. The default value of this parameter is `false`, which means that TiDB Lightning only checks conflicts after the data import. This parameter can be used only in the physical import mode (`tikv-importer.backend = "local"`).  |
| TiDB Lightning  | [`logical-import-batch-rows`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) | Newly added | Controls the maximum number of rows inserted per transaction in the logical import mode. The default value is `65536` rows. |
| TiDB Lightning  | [`logical-import-batch-size`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) | Newly added | Controls the maximum size of each SQL query executed on the downstream TiDB server in the logical import mode. The default value is `"96KiB"`. The unit can be KB, KiB, MB, or MiB. |
| Data Migration  |  [`secret-key-path`](https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file) | Newly added | Specifies the file path of the secret key, which is used to encrypt and decrypt upstream and downstream passwords. The file must contain a 64-character hexadecimal AES-256 secret key. |
| TiCDC | [`debezium-disable-schema`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config) | Newly added | Controls whether to disable the output of schema information. This parameter only takes effect when the sink type is MQ and the output protocol is Debezium. |
| TiCDC | [`tls-certificate-file`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-pulsar) | Newly added | Specifies the path to the encrypted certificate file on the client, which is required when Pulsar enables TLS encrypted transmission. |
| TiCDC | [`tls-key-file-path`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-pulsar) | Newly added | Specifies the path to the encrypted private key on the client, which is required when Pulsar enables TLS encrypted transmission. |
### System tables

* Add new system tables [`INFORMATION_SCHEMA.TIDB_INDEX_USAGE`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-index-usage) and [`INFORMATION_SCHEMA.CLUSTER_TIDB_INDEX_USAGE`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-index-usage#cluster_tidb_index_usage) to record index usage statistics on TiDB nodes.
* Add a new system schema [`sys`](https://docs.pingcap.com/tidb/stable/sys-schema/sys-schema) and a new view [`sys.schema_unused_indexes`](https://docs.pingcap.com/tidb/stable/sys-schema/sys-schema-unused-indexes), which records indexes that have not been used since the last start of TiDB.
