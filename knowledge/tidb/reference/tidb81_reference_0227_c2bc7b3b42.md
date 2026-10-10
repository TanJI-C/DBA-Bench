# DM ignorable precheck items

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-precheck.md`
- Source Title: `Migration Task Precheck`
- Source Heading Path: `Migration Task Precheck > Descriptions of check items > Ignorable check items`
- Source Line Ranges: `142-166`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `precheck`, `ignore-checking-items`, `risk`, `physical-import`, `privileges`, `binlog`, `schema-compatibility`, `sharding`, `online-ddl`, `region-distribution`, `free-space`, `version-compatibility`, `data-safety`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0227_c2bc7b3b42`
- Source ID: `tidb-docs-8.1:dm/dm-precheck.md#ignorable-check-items`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `89b1bc8ff86b73e8a9f7d33e817ea7109c6c694afe3ad9a39f1d225981a57b2c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-precheck#ignorable-check-items
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-precheck.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which DM precheck items can be skipped with `ignore-checking-items` and what each ignorable item checks.
- Retrieval Keywords: ignore-checking-items, Ignorable check items, dump_privilege, replication_privilege, version, server_id, binlog_enable, table_schema, schema_of_shard_tables, auto_increment_ID, online_ddl, empty_region, region_distribution, downstream_version, free_space, downstream_mutex_features, physical import, binlog_row_image, data safety
- Follow-up Guidance: The note states that since v6.0, DM does not allow ignoring some check items related to data safety, with `binlog_row_image` given as an example.
- Classification Note: This is reference content because it enumerates the ignorable precheck item identifiers and briefly defines each check from the official documentation.

## Official Source Content

### Ignorable check items

Prechecks can find potential risks in your environments. It is not recommended to ignore check items. If your data migration task has special needs, you can use the [`ignore-checking-items` configuration item](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced) to skip some check items.

| Check item  | Description   |
| :---------- | :------------ |
| `dump_privilege`         | Checks the dump privilege of the user in the upstream MySQL instance. |
| `replication_privilege` | Checks the replication privilege of the user in the upstream MySQL instance. |
| `version`               | Checks the version of the upstream database. |
| `server_id`             | Checks whether server_id is configured in the upstream database. |
| `binlog_enable`         | Checks whether binlog is enabled in the upstream database. |
| `table_schema`          | Checks the compatibility of the table schemas in the upstream MySQL tables. |
| `schema_of_shard_tables`| Checks the consistency of the table schemas in the upstream MySQL multi-instance shards. |
| `auto_increment_ID`     | Checks whether the auto-increment primary key conflicts in the upstream MySQL multi-instance shards. |
|`online_ddl`| Checks whether the upstream is in the process of [online-DDL](https://docs.pingcap.com/tidb/stable/dm/feature-online-ddl). |
| `empty_region` | Checks the number of empty Regions in the downstream database for physical import. |
| `region_distribution` | Checks the distribution of Regions in the downstream database for physical import. |
| `downstream_version` | Checks the versions of TiDB, PD, and TiKV in the downstream database. |
| `free_space` | Checks the free space of the downstream database. |
| `downstream_mutex_features` | Checks whether the downstream database is running tasks that are incompatible with physical import. |

> **Note:**
>
> More ignorable check items are supported in versions earlier than v6.0. Since v6.0, DM does not allow ignoring some check items related to data safety. For example, if you configure the `binlog_row_image` parameter incorrectly, data might be lost during the replication.
