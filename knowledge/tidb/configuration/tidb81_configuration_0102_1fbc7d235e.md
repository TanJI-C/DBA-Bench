# Enable disk spill encryption

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/enable-disk-spill-encrypt.md`
- Source Title: `Enable Encryption for Disk Spill`
- Source Heading Path: `Enable Encryption for Disk Spill | Enable Encryption for Disk Spill > Configure`
- Source Line Ranges: `5-21`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `disk spill`, `encryption`, `temporary files`, `memory quota`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0102_1fbc7d235e`
- Source ID: `tidb-docs-8.1:enable-disk-spill-encrypt.md#enable-encryption-for-disk-spill`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b0deb6bbd36fe010a740d28cd15ff0223e63d9a1068dfb98153db4cbc1b97e1b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/enable-disk-spill-encrypt#enable-encryption-for-disk-spill
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/enable-disk-spill-encrypt.md

## Retrieval Guidance

- Use When: Use this chunk when asking how TiDB encrypts temporary disk spill files created when a query exceeds tidb_mem_quota_query and tidb_enable_tmp_storage_on_oom is ON.
- Retrieval Keywords: Enable disk spill encryption, tidb_enable_tmp_storage_on_oom, tidb_mem_quota_query, temporary files, disk spill, spilled-file-encryption-method, [security], aes128-ctr, plaintext, TiDB configuration file
- Follow-up Guidance: The source states that spilled-file-encryption-method is configured in the [security] section, with value options aes128-ctr and plaintext, and plaintext is the default meaning encryption is disabled.
- Classification Note: This is classified as TiDB configuration content because it defines the [security].spilled-file-encryption-method setting and its behavior for disk spill temporary files.

## Official Source Content

# Enable Encryption for Disk Spill

When the system variable [`tidb_enable_tmp_storage_on_oom`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tmp_storage_on_oom) is set to `ON`, if the memory usage of a single SQL statement exceeds the limit of the system variable [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query), some operators can save the intermediate results during execution as a temporary file to the disk and delete the file after the query is completed.

You can enable encryption for disk spill to prevent attackers from accessing data by reading these temporary files.
## Configure

To enable encryption for the disk spill files, you can configure the item [`spilled-file-encryption-method`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#spilled-file-encryption-method) in the `[security]` section of the TiDB configuration file.

```toml
[security]
spilled-file-encryption-method = "aes128-ctr"
```

Value options for `spilled-file-encryption-method` are `aes128-ctr` and `plaintext`. The default value is `plaintext`, which means that encryption is disabled.
