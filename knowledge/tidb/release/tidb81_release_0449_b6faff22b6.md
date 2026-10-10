# 7.1.0 configuration file parameter changes across components

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.0.md`
- Source Title: `TiDB 7.1.0 Release Notes`
- Source Heading Path: `TiDB 7.1.0 Release Notes > Compatibility changes > Configuration file parameters`
- Source Line Ranges: `344-369`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `lightning`, `ticdc`
- Topic Tags: `compatibility`, `configuration-parameters`, `defaults`, `new-parameters`, `modified-parameters`, `deleted-parameters`, `startup-statistics`, `logging`, `region-split`, `compaction`, `scheduler`, `tls`, `integrity-check`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0449_b6faff22b6`
- Source ID: `tidb-docs-8.1:releases/release-7.1.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `947f0d8049d84a6cdeafc7b95a0540c5b51943e863c36ffa0af4c9728863509c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB 7.1.0 configuration file parameter additions, modifications, or deletions across TiDB, TiKV, PD, TiFlash, TiDB Lightning, and TiCDC.
- Retrieval Keywords: TiDB 7.1.0 configuration file parameters, performance.force-init-stats, performance.lite-init-stats, log.timeout, region-compact-min-redundant-rows, region-compact-redundant-rows-percent, split.byte-threshold, split.qps-threshold, split.region-cpu-overload-threshold-ratio, region-compact-check-step, store-limit-version, schedule.enable-diagnostic, TiFlash http_port deleted, tikv-importer.pause-pd-scheduler-scope, tikv-importer.region-check-backoff-limit, tikv-importer.region-split-batch-size, tikv-importer.region-split-concurrency, insecure-skip-verify, integrity.corruption-handle-level, integrity.integrity-check-level, sink.only-output-updated-columns, sink.enable-partition-separator
- Follow-up Guidance: The chunk also states default values, value options, and conditions for some parameters such as region-split-size greater than or equal to 4 GB, storage.engine="partitioned-raft-kv", and TiCDC replication to Kafka.
- Classification Note: This is a release-note compatibility summary because the official content lists newly added, modified, and deleted configuration parameters and their behavior changes by component.

## Official Source Content

### Configuration file parameters

| Configuration file | Configuration parameter | Change type | Description |
| -------- | -------- | -------- | -------- |
| TiDB | [`performance.force-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#force-init-stats-new-in-v657-and-v710) | Newly added | Controls whether to wait for statistics initialization to finish before providing services during TiDB startup. |
| TiDB | [`performance.lite-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#lite-init-stats-new-in-v710) | Newly added | Controls whether to use lightweight statistics initialization during TiDB startup. |
| TiDB | [`log.timeout`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#timeout-new-in-v710) | Newly added | Sets the timeout for log-writing operations in TiDB. In case of a disk failure that prevents logs from being written, this configuration item can trigger the TiDB process to panic instead of hang. The default value is `0`, which means no timeout is set. |
| TiKV | [`region-compact-min-redundant-rows`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-compact-min-redundant-rows-new-in-v710) | Newly added | Sets the number of redundant MVCC rows required to trigger RocksDB compaction. The default value is `50000`. |
| TiKV | [`region-compact-redundant-rows-percent`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-compact-redundant-rows-percent-new-in-v710) | Newly added | Sets the percentage of redundant MVCC rows required to trigger RocksDB compaction. The default value is `20`. |
| TiKV | [`split.byte-threshold`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#byte-threshold-new-in-v50) | Modified | Changes the default value from `30MiB` to `100MiB` when [`region-split-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-split-size) is greater than or equal to 4 GB. |
| TiKV | [`split.qps-threshold`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#qps-threshold) | Modified | Changes the default value from `3000` to `7000` when [`region-split-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-split-size) is greater than or equal to 4 GB. |
| TiKV | [`split.region-cpu-overload-threshold-ratio`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-cpu-overload-threshold-ratio-new-in-v620) | Modified | Changes the default value from `0.25` to `0.75` when [`region-split-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-split-size) is greater than or equal to 4 GB. |
| TiKV | [`region-compact-check-step`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-compact-check-step) | Modified | Changes the default value from `100` to `5` when Partitioned Raft KV is enabled (`storage.engine="partitioned-raft-kv"`). |
| PD | [`store-limit-version`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#store-limit-version-new-in-v710) | Newly added | Controls the mode of store limit. Value options are `"v1"` and `"v2"`. |
| PD | [`schedule.enable-diagnostic`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-diagnostic-new-in-v630) | Modified | Changes the default value from `false` to `true`, meaning that the diagnostic feature of scheduler is enabled by default. |
| TiFlash | `http_port` | Deleted | Deprecates the HTTP service port (default `8123`). |
| TiDB Lightning | [`tikv-importer.pause-pd-scheduler-scope`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) | Newly added | Controls the scope in which TiDB Lightning pauses PD scheduling. The default value is `"table"` and value options are `"global"` and `"table"`. |
| TiDB Lightning | [`tikv-importer.region-check-backoff-limit`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) | Newly added | Controls the number of retries to wait for the Region to come online after the split and scatter operations. The default value is `1800`. The maximum retry interval is two seconds. The number of retries is not increased if any Region becomes online between retries.|
| TiDB Lightning | [`tikv-importer.region-split-batch-size`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) | Newly added | Controls the number of Regions when splitting Regions in a batch. The default value is `4096`. |
| TiDB Lightning | [`tikv-importer.region-split-concurrency`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) | Newly added | Controls the concurrency when splitting Regions. The default value is the number of CPU cores. |
| TiCDC | [`insecure-skip-verify`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka) | Newly added | Controls whether the authentication algorithm is set when TLS is enabled in the scenario of replicating data to Kafka. |
| TiCDC | [`integrity.corruption-handle-level`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#cli-and-configuration-parameters-of-ticdc-changefeeds) | Newly added | Specifies the log level of the Changefeed when the checksum validation for single-row data fails. The default value is `"warn"`. Value options are `"warn"` and `"error"`. |
| TiCDC | [`integrity.integrity-check-level`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#cli-and-configuration-parameters-of-ticdc-changefeeds) | Newly added | Controls whether to enable the checksum validation for single-row data. The default value is `"none"`, which means to disable the feature. |
| TiCDC | [`sink.only-output-updated-columns`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#cli-and-configuration-parameters-of-ticdc-changefeeds) | Newly added | Controls whether to only output the updated columns. The default value is `false`. |
| TiCDC | [`sink.enable-partition-separator`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#cli-and-configuration-parameters-of-ticdc-changefeeds) | Modified | Changes the default value from `false` to `true` after further tests, meaning that partitions in a table are stored in separate directories by default. It is recommended that you keep the value as `true` to avoid the potential issue of data loss during replication of partitioned tables to storage services. |
