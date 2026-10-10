# Encrypt DM source database password

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-manage-source.md`
- Source Title: `Manage Data Source Configurations in TiDB Data Migration`
- Source Heading Path: `Manage Data Source Configurations in TiDB Data Migration | Manage Data Source Configurations in TiDB Data Migration > Encrypt the database password`
- Source Line Ranges: `5-27`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `password-encryption`, `dmctl`, `secret-key-path`, `source-configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0076_c8027d9399`
- Source ID: `tidb-docs-8.1:dm/dm-manage-source.md#manage-data-source-configurations-in-tidb-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9d3e3c0e83dd15588b84966cd43d2109b00c5fc78eb98c06f32c771431947fa6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#manage-data-source-configurations-in-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-manage-source.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how to encrypt a DM source database password with dmctl or the requirement related to secret-key-path before running the encryption command.
- Retrieval Keywords: Encrypt the database password, dmctl encrypt, secret-key-path, DM-master, encrypted password, source configuration, ./dmctl encrypt 'abc!@#123'
- Follow-up Guidance: The source notes that starting from v8.0.0, you must configure secret-key-path for DM-master before using the dmctl encrypt command.
- Classification Note: This is classified as configuration because it covers password handling in DM configuration files and the prerequisite DM-master secret-key-path setting.

## Official Source Content

# Manage Data Source Configurations in TiDB Data Migration

This document introduces how to manage data source configurations, including encrypting the MySQL password, operating the data source, and changing the bindings between upstream MySQL instances and DM-workers using [dmctl](https://docs.pingcap.com/tidb/stable/dm/dmctl-introduction).
## Encrypt the database password

In DM configuration files, it is recommended to use the password encrypted with dmctl. For one original password, the encrypted password is different after each encryption.

> **Note:**
>
> Starting from v8.0.0, you must configure [`secret-key-path`](https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file) for DM-master before using the `dmctl encrypt` command.

```bash
./dmctl encrypt 'abc!@#123'
```

```
MKxn0Qo3m3XOyjCnhEMtsUCm83EhGQDZ/T4=
```
