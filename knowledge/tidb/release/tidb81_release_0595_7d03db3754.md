# Compatibility parameter changes and deprecated features in 8.1.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.0.md`
- Source Title: `TiDB 8.1.0 Release Notes`
- Source Heading Path: `TiDB 8.1.0 Release Notes > Compatibility changes > Configuration file parameters | TiDB 8.1.0 Release Notes > Deprecated features`
- Source Line Ranges: `181-209`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `dashboard`, `lightning`, `tikv`, `ticdc`, `sql`
- Topic Tags: `compatibility-changes`, `configuration-parameters`, `deprecated-features`, `telemetry`, `system-variables`, `authentication`, `cdc-sink`, `lightning-conflicts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0595_7d03db3754`
- Source ID: `tidb-docs-8.1:releases/release-8.1.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3d67eda83f1419f44e9b2fffc821b576bcae2a326c611b159bba46dd9da172a7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when locating TiDB 8.1.0 compatibility changes, configuration parameter changes, or deprecated telemetry, TiCDC authentication, and TiDB Lightning conflict settings.
- Retrieval Keywords: TiDB 8.1.0 compatibility changes, Deprecated features, enable-telemetry, tidb_enable_telemetry, ADMIN SHOW TELEMETRY, TELEMETRY, TELEMETRY_ID, concurrently-init-stats, conflict.max-record-rows, conflict.threshold, raft-engine.batch-compression-threshold, memory.enable-thread-exclusive-arena, security.client-allowed-user, security.client-user-required, security.mtls, sink.debezium.output-old-value, sink.open.output-old-value, duplicate-resolution, conflict.strategy
- Follow-up Guidance: The chunk also identifies removed telemetry syntax and keywords, and notes planned or future deprecations for execution plan binding auto-evolution and TiDB Lightning conflict detection parameters.
- Classification Note: The official content is classified as a release-note compatibility and deprecation summary because it lists changed configuration parameters, removed telemetry-related items, and scheduled deprecations in TiDB 8.1.0.

## Official Source Content

### Configuration file parameters

| Configuration file | Configuration parameter | Change type | Description |
| -------- | -------- | -------- | -------- |
| TiDB| [`enable-telemetry`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-telemetry-new-in-v402-and-deprecated-in-v810) | Deprecated | Starting from v8.1.0, the telemetry feature in TiDB is removed, and this configuration item is no longer functional. It is retained solely for compatibility with earlier versions. |
| TiDB| [`concurrently-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#concurrently-init-stats-new-in-v810-and-v752) | Newly added | Controls whether to initialize statistics concurrently during TiDB startup. The default value is `false`. |
| PD | [`enable-telemetry`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-telemetry) | Deprecated | Starting from v8.1.0, the telemetry feature in TiDB Dashboard is removed, and this configuration item is no longer functional. It is retained solely for compatibility with earlier versions. |
| TiDB Lightning | [`conflict.max-record-rows`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-configuration) | Modified | Starting from v8.1.0, there is no need to configure `conflict.max-record-rows` manually, because TiDB Lightning automatically assigns the value of `conflict.max-record-rows` with the value of `conflict.threshold`, regardless of the user input. `conflict.max-record-rows` will be deprecated in a future release. |
| TiDB Lightning | [`conflict.threshold`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) | Modified | Changes the default value from `9223372036854775807` to `10000` to quickly interrupt abnormal tasks so that you can make corresponding adjustments as soon as possible. This saves time and computational resources by avoiding the scenario where a large amount of conflicting data is discovered after the import, caused by abnormal data sources or incorrect table schema definitions. |
| TiKV | [`raft-engine.batch-compression-threshold`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#batch-compression-threshold) | Modified | Changes the default value from `"8KiB"` to `"4KiB"` to reduce the IOPS overhead of writing Raft logs and improve the compression ratio. |
| TiKV | [`memory.enable-thread-exclusive-arena`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-thread-exclusive-arena-new-in-v810) | Newly added | Controls whether to display the memory allocation status at the TiKV thread level to track the memory usage of each TiKV thread. The default value is `true`. |
| TiCDC | [`security.client-allowed-user`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-server-config#cdc-server-configuration-file-parameters) | Newly added | Lists the usernames that are allowed for client authentication. Authentication requests with usernames not in this list will be rejected. The default value is null. |
| TiCDC | [`security.client-user-required`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-server-config#cdc-server-configuration-file-parameters) | Newly added | Controls whether to use username and password for client authentication. The default value is `false`. |
| TiCDC | [`security.mtls`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-server-config#cdc-server-configuration-file-parameters) | Newly added | Controls whether to enable the TLS client authentication. The default value is `false`. |
| TiCDC | [`sink.debezium.output-old-value`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | Controls whether to output the value before the row data changes. The default value is `true`. When it is disabled, the `UPDATE` event does not output the "before" field. |
| TiCDC | [`sink.open.output-old-value`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | Controls whether to output the value before the row data changes. The default value is `true`. When it is disabled, the `UPDATE` event does not output the "p" field. |
## Deprecated features

* Starting from v8.1.0, the telemetry feature in TiDB and TiDB Dashboard is removed:

    * The system variable [`tidb_enable_telemetry`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_telemetry-new-in-v402-and-deprecated-in-v810), the TiDB configuration item [`enable-telemetry`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-telemetry-new-in-v402-and-deprecated-in-v810), and the PD configuration item [`enable-telemetry`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-telemetry) are deprecated and no longer functional.
    * The `ADMIN SHOW TELEMETRY` syntax is removed.
    * The `TELEMETRY` and `TELEMETRY_ID` keywords are removed.

* It is planned to redesign [the auto-evolution of execution plan bindings](https://docs.pingcap.com/tidb/stable/sql-plan-management#baseline-evolution) in subsequent releases, and the related variables and behavior will change.
* The TiDB Lightning parameter [`conflict.max-record-rows`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) is scheduled for deprecation in a future release and will be subsequently removed. This parameter will be replaced by `conflict.threshold`, which means that the maximum number of conflicting records is consistent with the maximum number of conflicting records that can be tolerated in a single import task.
* Starting from v8.0.0, TiDB Lightning deprecates the [old version of conflict detection](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#the-old-version-of-conflict-detection-deprecated-in-v800) strategy for the physical import mode, and enables you to control the conflict detection strategy for both logical and physical import modes via the [`conflict.strategy`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) parameter. The [`duplicate-resolution`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) parameter for the old version of conflict detection will be removed in a future release.
