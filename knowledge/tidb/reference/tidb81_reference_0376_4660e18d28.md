# CLUSTER_CONFIG table overview and query example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-cluster-config.md`
- Source Title: `CLUSTER_CONFIG`
- Source Heading Path: `CLUSTER_CONFIG`
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `information_schema`, `cluster_config`, `configuration`, `sql-query`, `schema`, `instance-metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0376_4660e18d28`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-cluster-config.md#cluster-config`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `430db9501ed6323e824440f62830ffb14e56f600b08162e38e892a9ae4e33477`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-config#cluster-config
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-cluster-config.md

## Retrieval Guidance

- Use When: Use this chunk when you need the SQL reference for viewing current configuration values of all server components through `information_schema.CLUSTER_CONFIG`, including its schema and a sample filter on TiKV `coprocessor` settings.
- Retrieval Keywords: CLUSTER_CONFIG, information_schema, DESC cluster_config, TYPE, INSTANCE, KEY, VALUE, SELECT * FROM cluster_config WHERE type='tikv' AND `key` LIKE 'coprocessor%';, tidb, pd, tikv, cluster configuration table, current configuration of all server components, coprocessor.batch-split-limit, coprocessor.region-max-keys, coprocessor.region-max-size, coprocessor.region-split-keys, coprocessor.region-split-size, coprocessor.split-region-on-table
- Follow-up Guidance: The source includes a query example that filters `CLUSTER_CONFIG` rows by `type='tikv'` and `key` values starting with `coprocessor`.
- Classification Note: This is classified as a reference chunk because it defines the `CLUSTER_CONFIG` table, lists its columns and meanings, and shows exact SQL query examples for retrieving configuration data.

## Official Source Content

# CLUSTER_CONFIG

You can use the `CLUSTER_CONFIG` cluster configuration table to get the current configuration of all server components in the cluster. This simplifies the usage over earlier releases of TiDB, where obtaining similar information would require accessing the HTTP API endpoints of each instance.

> **Note:**
>
> This table is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).

```sql
USE information_schema;
DESC cluster_config;
```

```sql
+----------+--------------+------+------+---------+-------+
| Field    | Type         | Null | Key  | Default | Extra |
+----------+--------------+------+------+---------+-------+
| TYPE     | varchar(64)  | YES  |      | NULL    |       |
| INSTANCE | varchar(64)  | YES  |      | NULL    |       |
| KEY      | varchar(256) | YES  |      | NULL    |       |
| VALUE    | varchar(128) | YES  |      | NULL    |       |
+----------+--------------+------+------+---------+-------+
```

Field description:

* `TYPE`: The instance type. The optional values are `tidb`, `pd`, and `tikv`.
* `INSTANCE`: The service address of the instance.
* `KEY`: The configuration item name.
* `VALUE`: The configuration item value.

The following example shows how to query the `coprocessor` configuration on the TiKV instance using the `CLUSTER_CONFIG` table:

```sql
SELECT * FROM cluster_config WHERE type='tikv' AND `key` LIKE 'coprocessor%';
```

```sql
+------+-----------------+-----------------------------------+---------+
| TYPE | INSTANCE        | KEY                               | VALUE   |
+------+-----------------+-----------------------------------+---------+
| tikv | 127.0.0.1:20165 | coprocessor.batch-split-limit     | 10      |
| tikv | 127.0.0.1:20165 | coprocessor.region-max-keys       | 1440000 |
| tikv | 127.0.0.1:20165 | coprocessor.region-max-size       | 144MiB  |
| tikv | 127.0.0.1:20165 | coprocessor.region-split-keys     | 960000  |
| tikv | 127.0.0.1:20165 | coprocessor.region-split-size     | 96MiB   |
| tikv | 127.0.0.1:20165 | coprocessor.split-region-on-table | false   |
+------+-----------------+-----------------------------------+---------+
6 rows in set (0.00 sec)
```
