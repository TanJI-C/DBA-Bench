# Dynamic configuration overview and viewing instance configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dynamic-config.md`
- Source Title: `Modify Configuration Dynamically`
- Source Heading Path: `Modify Configuration Dynamically | Modify Configuration Dynamically > Common Operations | Modify Configuration Dynamically > Common Operations > View instance configuration`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `dynamic-configuration`, `show-config`, `instance-configuration`, `sql-statements`, `filtering`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0098_68346e201c`
- Source ID: `tidb-docs-8.1:dynamic-config.md#modify-configuration-dynamically`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `27d571c32c9e25090002759ac14a44f893267a2d40613a34956d91a6b010ee38`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dynamic-config#modify-configuration-dynamically
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dynamic-config.md

## Retrieval Guidance

- Use When: Use this when you need to view instance configuration across TiDB, TiKV, and PD or filter configuration output with the `show config` statement.
- Retrieval Keywords: show config, show config where type='tidb', show config where instance in (...), show config where name like '%log%', show config where type='tikv' and name='log.level', View instance configuration, dynamically modify configuration, TiDB Self-Managed
- Follow-up Guidance: The content also shows that `show config` results can be filtered by `type`, `instance`, and `name` fields.
- Classification Note: This is classified as shared configuration content because it describes SQL-based viewing of configuration for multiple components including TiDB, TiKV, and PD in TiDB Self-Managed.

## Official Source Content

# Modify Configuration Dynamically

This document describes how to dynamically modify the cluster configuration.

You can dynamically update the configuration of components (including TiDB, TiKV, and PD) using SQL statements, without restarting the cluster components. Currently, the method of changing TiDB instance configuration is different from that of changing configuration of other components (such as TiKV and PD).

> **Note:**
>
> This feature is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/). For TiDB Cloud, you need to contact [TiDB Cloud Support](https://docs.pingcap.com/tidbcloud/tidb-cloud-support) to modify the configurations.
## Common Operations

This section describes the common operations of dynamically modifying configuration.
### View instance configuration

To view the configuration of all instances in the cluster, use the `show config` statement. The result is as follows:

```sql
show config;
```

```sql
+------+-----------------+-----------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Type | Instance        | Name                                                      | Value                                                                                                                                                                                                                                                                            |
+------+-----------------+-----------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| tidb | 127.0.0.1:4001  | advertise-address                                         | 127.0.0.1                                                                                                                                                                                                                                                                        |
| tidb | 127.0.0.1:4001  | binlog.binlog-socket                                      |                                                                                                                                                                                                                                                                                  |
| tidb | 127.0.0.1:4001  | binlog.enable                                             | false                                                                                                                                                                                                                                                                            |
| tidb | 127.0.0.1:4001  | binlog.ignore-error                                       | false                                                                                                                                                                                                                                                                            |
| tidb | 127.0.0.1:4001  | binlog.strategy                                           | range                                                                                                                                                                                                                                                                            |
| tidb | 127.0.0.1:4001  | binlog.write-timeout                                      | 15s                                                                                                                                                                                                                                                                              |
| tidb | 127.0.0.1:4001  | check-mb4-value-in-utf8                                   | true                                                                                                                                                                                                                                                                             |

...
```

You can filter the result by fields. For example:

```sql
show config where type='tidb'
show config where instance in (...)
show config where name like '%log%'
show config where type='tikv' and name='log.level'
```
