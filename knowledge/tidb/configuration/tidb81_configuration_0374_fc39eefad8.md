# Coprocessor region split and plugin configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > coprocessor | TiKV Configuration File > coprocessor > `split-region-on-table` | TiKV Configuration File > coprocessor > `batch-split-limit` | TiKV Configuration File > coprocessor > `region-max-size` | TiKV Configuration File > coprocessor > `region-split-size` | TiKV Configuration File > coprocessor > `region-max-keys` | TiKV Configuration File > coprocessor > `region-split-keys` | TiKV Configuration File > coprocessor > `consistency-check-method` | TiKV Configuration File > coprocessor-v2 | TiKV Configuration File > coprocessor-v2 > `coprocessor-plugin-directory` | TiKV Configuration File > coprocessor-v2 > `enable-region-bucket` <span class="version-mark">New in v6.1.0</span> | TiKV Configuration File > coprocessor-v2 > `region-bucket-size` <span class="version-mark">New in v6.1.0</span> | TiKV Configuration File > rocksdb`
- Source Line Ranges: `1146-1220`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`
- Topic Tags: `coprocessor`, `region-split`, `region-size`, `region-keys`, `consistency-check`, `plugins`, `region-bucket`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0374_fc39eefad8`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#coprocessor`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1411bc2c6e87d2113b03b895b55a1d283238fb8bc71b03e85895b435ab828d25`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#coprocessor
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiKV coprocessor configuration for Region split thresholds, consistency check method, coprocessor plugin loading, or experimental region bucket settings.
- Retrieval Keywords: coprocessor, split-region-on-table, batch-split-limit, region-max-size, region-split-size, region-max-keys, region-split-keys, consistency-check-method, coprocessor-v2, coprocessor-plugin-directory, enable-region-bucket, region-bucket-size, Region split, mvcc, raw, compiled coprocessor plugins, bucket, Dynamic size Region
- Follow-up Guidance: The source notes that `enable-region-bucket` makes sense only when `region-split-size` is twice of `region-bucket-size` or above, and links to the Dynamic size Region design document for bucket details.
- Classification Note: This chunk is classified as TiKV self-managed configuration because it documents coprocessor and coprocessor-v2 configuration items, including Region split parameters, consistency check mode, plugin directory, and experimental bucket options.

## Official Source Content

## coprocessor

Configuration items related to Coprocessor.
### `split-region-on-table`

+ Determines whether to split Region by table. It is recommended for you to use the feature only in TiDB mode.
+ Default value: `false`
### `batch-split-limit`

+ The threshold of Region split in batches. Increasing this value speeds up Region split.
+ Default value: `10`
+ Minimum value: `1`
### `region-max-size`

+ The maximum size of a Region. When the value is exceeded, the Region splits into many.
+ Default value: `region-split-size / 2 * 3`
+ Unit: KiB|MiB|GiB
### `region-split-size`

+ The size of the newly split Region. This value is an estimate.
+ Default value: `"96MiB"`
+ Unit: KiB|MiB|GiB
### `region-max-keys`

+ The maximum allowable number of keys in a Region. When this value is exceeded, the Region splits into many.
+ Default value: `region-split-keys / 2 * 3`
### `region-split-keys`

+ The number of keys in the newly split Region. This value is an estimate.
+ Default value: `960000`
### `consistency-check-method`

+ Specifies the method of data consistency check
+ For the consistency check of MVCC data, set the value to `"mvcc"`. For the consistency check of raw data, set the value to `"raw"`.
+ Default value: `"mvcc"`
## coprocessor-v2
### `coprocessor-plugin-directory`

+ The path of the directory where compiled coprocessor plugins are located. Plugins in this directory are automatically loaded by TiKV.
+ If this configuration item is not set, the coprocessor plugin is disabled.
+ Default value: `"./coprocessors"`
### `enable-region-bucket` New in v6.1.0

+ Determines whether to divide a Region into smaller ranges called buckets. The bucket is used as the unit of the concurrent query to improve the scan concurrency. For more about the design of the bucket, refer to [Dynamic size Region](https://github.com/tikv/rfcs/blob/master/text/0082-dynamic-size-region.md).
+ Default value: false

> **Warning:**
>
> - `enable-region-bucket` is an experimental feature introduced in TiDB v6.1.0. It is not recommended that you use it in production environments.
> - This configuration makes sense only when `region-split-size` is twice of `region-bucket-size` or above; otherwise, no bucket is actually generated.
> - Adjusting `region-split-size` to a larger value might have the risk of performance regression and slow scheduling.
### `region-bucket-size` New in v6.1.0

+ The size of a bucket when `enable-region-bucket` is true.
+ Default value: Starting from v7.3.0, the default value is changed from `96MiB` to `50MiB`.

> **Warning:**
>
> `region-bucket-size` is an experimental feature introduced in TiDB v6.1.0. It is not recommended that you use it in production environments.
## rocksdb

Configuration items related to RocksDB
