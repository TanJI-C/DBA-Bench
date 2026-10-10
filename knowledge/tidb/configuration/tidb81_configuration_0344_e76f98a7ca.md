# Configure disk quota for physical import mode

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-physical-import-mode-usage.md`
- Source Title: `Use Physical Import Mode`
- Source Heading Path: `Use Physical Import Mode > Configure disk quota <span class="version-mark">New in v6.2.0</span>`
- Source Line Ranges: `279-300`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tikv`
- Topic Tags: `physical-import`, `disk-quota`, `temporary-files`, `local-backend`, `configuration`, `throttling`, `disk-space`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0344_e76f98a7ca`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-physical-import-mode-usage.md#configure-disk-quota-span-class-version-mark-new-in-v6-2-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ced61f8e827af29ce5212e4ebcb915ccc3e09868e0830cab30720ff92ba28ba3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#configure-disk-quota-span-class-version-mark-new-in-v6-2-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-physical-import-mode-usage.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB Lightning physical import mode controls local temporary file usage with disk quota and check intervals for the local backend.
- Retrieval Keywords: physical import mode, Configure disk quota, TiDB Lightning, temporary files, local disk space, write failure, [tikv-importer], disk-quota, backend = "local", [cron], check-disk-quota, MaxInt64, 9223372036854775807 bytes, pause reading source data, sorted key-value pairs, write to TiKV
- Follow-up Guidance: The source also states that checking disk quota acquires an exclusive lock that blocks all import threads, and that a larger `check-disk-quota` value can let disk usage exceed the configured quota.
- Classification Note: This is classified as configuration because the content defines the `tikv-importer.disk-quota`, `tikv-importer.backend`, and `cron.check-disk-quota` settings for TiDB Lightning physical import mode.

## Official Source Content

## Configure disk quota New in v6.2.0

When you import data in the physical import mode, TiDB Lightning creates a large number of temporary files on the local disk to encode, sort, and split the original data. When the local disk space is insufficient, TiDB Lightning reports an error and exits because of write failure.

To avoid this situation, you can configure disk quota for TiDB Lightning. When the size of the temporary files exceeds the disk quota, TiDB Lightning pauses the process of reading the source data and writing temporary files. TiDB Lightning prioritizes writing the sorted key-value pairs to TiKV. After deleting the local temporary files, TiDB Lightning continues the import process.

To enable disk quota, add the following configuration to your configuration file:

```toml
[tikv-importer]
# MaxInt64 by default, which is 9223372036854775807 bytes.
disk-quota = "10GB"
backend = "local"

[cron]
# The interval of checking disk quota. 60 seconds by default.
check-disk-quota = "30s"
```

`disk-quota` limits the storage space used by TiDB Lightning. The default value is MaxInt64, which is 9223372036854775807 bytes. This value is much larger than the disk space you might need for the import, so leaving it as the default value is equivalent to not setting the disk quota.

`check-disk-quota` is the interval of checking disk quota. The default value is 60 seconds. When TiDB Lightning checks the disk quota, it acquires an exclusive lock for the relevant data, which blocks all the import threads. Therefore, if TiDB Lightning checks the disk quota before every write, it significantly slows down the write efficiency (as slow as a single-thread write). To achieve efficient write, disk quota is not checked before every write; instead, TiDB Lightning pauses all the import threads and checks the disk quota every `check-disk-quota` interval. That is, if the value of `check-disk-quota` is set to a large value, the disk space used by TiDB Lightning might exceed the disk quota you set, which leaves the disk quota ineffective. Therefore, it is recommended to set the value of `check-disk-quota` to a small value. The specific value of this item is determined by the environment in which TiDB Lightning is running. In different environments, TiDB Lightning writes temporary files at different speeds. Theoretically, the faster the speed, the smaller the value of `check-disk-quota` should be.
