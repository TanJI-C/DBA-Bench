# Titan storage engine configuration overview and enablement

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > rocksdb.titan | TiKV Configuration File > rocksdb.titan > `enabled` | TiKV Configuration File > rocksdb.titan > `dirname``
- Source Line Ranges: `1453-1476`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `titan`, `storage-engine`, `blob-files`, `upgrade-behavior`, `version-specific`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0376_29032f6eb8`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#rocksdb-titan`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f6b748bfabfcd3ccb26cb8d16a0297715720062129b8531577b1c70dd08f95fe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#rocksdb-titan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV self-managed Titan configuration basics, including whether Titan is enabled, its default behavior after upgrades, and the Titan blob file directory.
- Retrieval Keywords: rocksdb.titan, rocksdb.titan.enabled, rocksdb.titan.dirname, Titan enabled, Titan Blob file directory, Disable Titan, min-blob-size, wide table and JSON data writing and point query
- Follow-up Guidance: The source includes a warning to refer to Disable Titan for the steps to disable Titan and notes upgrade-retained behavior for Titan and min-blob-size.
- Classification Note: This is a configuration chunk because it describes TiKV rocksdb.titan configuration items, including enablement, directory location, defaults, warnings, and upgrade-related notes from the official content.

## Official Source Content

## rocksdb.titan

Configuration items related to Titan.
### `enabled`

> **Warning**
>
> When disabling Titan for TiDB versions earlier than v8.5.0, it is not recommended to modify this configuration item to `false`, as this might cause TiKV to crash. To disable Titan, refer to the steps in [Disable Titan](https://docs.pingcap.com/tidb/stable/storage-engine/titan-configuration#disable-titan).

> **Note:**
>
> - To enhance the performance of wide table and JSON data writing and point query, starting from TiDB v7.6.0, the default value changes from `false` to `true`, which means that Titan is enabled by default.
> - Existing clusters upgraded to v7.6.0 or later versions retain the original configuration, which means that if Titan is not explicitly enabled, it still uses RocksDB.
> - If the cluster has enabled Titan before upgrading to TiDB v7.6.0 or later versions, Titan will be retained after the upgrade, and the [`min-blob-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-blob-size) configuration before the upgrade will be retained. If you do not explicitly configure the value before the upgrade, the default value of the previous version `1KiB` will be retained to ensure the stability of the cluster configuration after the upgrade.

+ Enables or disables Titan.
+ Default value: `true`
### `dirname`

+ The directory in which the Titan Blob file is stored
+ Default value: `"titandb"`
