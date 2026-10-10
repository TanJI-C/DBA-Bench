# 7.0.0 configuration parameter changes across components

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.0.0.md`
- Source Title: `TiDB 7.0.0 Release Notes`
- Source Heading Path: `TiDB 7.0.0 Release Notes > Compatibility changes > Configuration file parameters`
- Source Line Ranges: `351-383`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tiflash`, `lightning`, `ticdc`, `dm`
- Topic Tags: `configuration-parameters`, `compatibility-changes`, `default-values`, `renamed-parameters`, `newly-added-parameters`, `resource-control`, `tiflash-disaggregated-storage`, `s3`, `physical-import`, `changefeed`, `dm-task`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0437_ffa882d968`
- Source ID: `tidb-docs-8.1:releases/release-7.0.0.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3e52fe47420a7d3a3f926ef5b45b66446d7a050fd8a8d8ae20aff3f01ce981af`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.0.0#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.0.0 compatibility changes to configuration file parameters, including renamed, modified default, deleted, and newly added parameters across TiKV, PD, TiFlash, TiDB Lightning, TiCDC, and DM.
- Retrieval Keywords: TiDB 7.0.0 configuration file parameters, server.snap-max-write-bytes-per-sec, server.snap-io-max-bytes-per-sec, raft-engine.enable-log-recycle, resolved-ts.advance-ts-interval, resource-control.enabled, raft-engine.prefill-for-recycle, degraded-mode-wait-duration, read-base-cost, read-cost-per-byte, read-cpu-ms-cost, write-base-cost, write-cost-per-byte, mark_cache_size, minmax_index_cache_size, flash.disaggregated_mode, storage.s3.endpoint, storage.s3.bucket, storage.s3.root, storage.s3.access_key_id, storage.s3.secret_access_key, storage.remote.cache.dir, storage.remote.cache.capacity, add-index-by-sql, enable-table-across-nodes, region-threshold, analyze, range-concurrency, compress-kv-pairs, pd-addr, default value changes, renamed parameters, newly added parameters
- Follow-up Guidance: The source lists each affected component parameter together with its change type and description, including default values, rename targets, and feature-specific notes such as Resource Control, TiFlash disaggregated storage and S3, physical import mode, changefeed configuration, and DM task configuration.
- Classification Note: This chunk is classified as a release note because it is a TiDB 7.0.0 compatibility changes table summarizing configuration parameter changes across multiple components.

## Official Source Content

### Configuration file parameters

| Configuration file | Configuration parameter | Change type | Description |
| -------- | -------- | -------- | -------- |
| TiKV | `server.snap-max-write-bytes-per-sec` | Deleted | This parameter is renamed to [`server.snap-io-max-bytes-per-sec`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#snap-io-max-bytes-per-sec). |
| TiKV | [`raft-engine.enable-log-recycle`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-log-recycle-new-in-v630) | Modified | The default value changes from `false` to `true`. |
| TiKV | [`resolved-ts.advance-ts-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#advance-ts-interval) | Modified | The default value changes from `"1s"` to `"20s"`. This modification can increase the interval of the regular advancement of Resolved TS and reduce the traffic consumption between TiKV nodes. |
| TiKV | [`resource-control.enabled`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#resource-control) | Modified | The default value changes from `false` to `true`. |
| TiKV | [`raft-engine.prefill-for-recycle`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#prefill-for-recycle-new-in-v700) | Newly added | Controls whether to generate empty log files for log recycling in Raft Engine. The default value is `false`. |
| PD | [`degraded-mode-wait-duration`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#degraded-mode-wait-duration) | Newly added | A [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control)-related configuration item. It controls the waiting time for triggering the degraded mode. The default value is `0s`. |
| PD | [`read-base-cost`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#read-base-cost) | Newly added | A [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control)-related configuration item. It controls the basis factor for conversion from a read request to RU. The default value is `0.25`. |
| PD | [`read-cost-per-byte`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#read-cost-per-byte) | Newly added | A [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control)-related configuration item. It controls the basis factor for conversion from read flow to RU. The default value is `1/ (64 * 1024)`. |
| PD | [`read-cpu-ms-cost`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#read-cpu-ms-cost) | Newly added | A [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control)-related configuration item. It controls the basis factor for conversion from CPU to RU. The default value is `1/3`. |
| PD | [`write-base-cost`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#write-base-cost) | Newly added | A [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control)-related configuration item. It controls the basis factor for conversion from a write request to RU. The default value is `1`. |
| PD | [`write-cost-per-byte`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#write-cost-per-byte) | Newly added | A [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control)-related configuration item. It controls the basis factor for conversion from write flow to RU. The default value is `1/1024`. |
| TiFlash | [`mark_cache_size`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration) | Modified | Change the default cache limit of the metadata for a data block in TiFlash from `5368709120` to `1073741824` to reduce unnecessary memory usage. |
| TiFlash | [`minmax_index_cache_size`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration) | Modified | Change the default cache limit of the min-max index for a data block in TiFlash from `5368709120` to `1073741824` to reduce unnecessary memory usage. |
| TiFlash | [`flash.disaggregated_mode`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3) | Newly added | In the disaggregated architecture of TiFlash, it indicates whether this TiFlash node is a write node or a compute node. The value can be `tiflash_write` or `tiflash_compute`. |
| TiFlash | [`storage.s3.endpoint`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3) | Newly added | The endpoint to connect to S3. |
| TiFlash | [`storage.s3.bucket`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3) | Newly added | The bucket where TiFlash stores all data. |
| TiFlash | [`storage.s3.root`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3) | Newly added | The root directory of data storage in S3 bucket. |
| TiFlash | [`storage.s3.access_key_id`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3) | Newly added | `ACCESS_KEY_ID` for accessing S3. |
| TiFlash | [`storage.s3.secret_access_key`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3) | Newly added | `SECRET_ACCESS_KEY` for accessing S3. |
| TiFlash | [`storage.remote.cache.dir`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3) | Newly added | The local data cache directory of TiFlash compute node. |
| TiFlash | [`storage.remote.cache.capacity`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3) | Newly added | The size of the local data cache directory of TiFlash compute node. |
| TiDB Lightning | [`add-index-by-sql`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) | Newly added | Controls whether to use SQL to add indexes in physical import mode. The default value is `false`, which means that TiDB Lightning will encode both row data and index data into KV pairs and import them into TiKV together. The advantage of adding indexes using SQL is to separate the import of data and the import of indexes, which can quickly import data. Even if the index creation fails after the data is imported, the data consistency is not affected. |
| TiCDC | [`enable-table-across-nodes`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | Determines whether to divide a table into multiple sync ranges according to the number of Regions. These ranges can be replicated by multiple TiCDC nodes. |
| TiCDC      | [`region-threshold`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) | Newly added | When `enable-table-across-nodes` is enabled, this feature only takes effect on tables with more than `region-threshold` Regions.      |
| DM | [`analyze`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced)  | Newly added | Controls whether to execute the `ANALYZE TABLE <table>` operation on each table after CHECKSUM is completed. It can be configured as `"required"`/`"optional"`/`"off"`. The default value is `"optional"`. |
| DM | [`range-concurrency`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced)  | Newly added | Controls the concurrency of dm-worker writing KV data to TiKV. |
| DM | [`compress-kv-pairs`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced)  | Newly added | Controls whether to enable compression when dm-worker sends KV data to TiKV. Currently, only gzip is supported. The default value is empty, which means no compression. |
| DM | [`pd-addr`](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced)  | Newly added | Controls the address of the downstream PD server in the Physical Import mode. You can fill in either one or more PD servers. If this configuration item is empty, use the PD address information from the TiDB query by default. |
