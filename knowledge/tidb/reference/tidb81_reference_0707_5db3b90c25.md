# schema_unused_indexes view definition and manual creation

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sys-schema/sys-schema-unused-indexes.md`
- Source Title: `schema_unused_indexes`
- Source Heading Path: ``schema_unused_indexes` | `schema_unused_indexes` > Manually create the `schema_unused_indexes` view | `schema_unused_indexes` > Read more`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `sys-schema`, `unused-indexes`, `index-usage`, `view-definition`, `manual-creation`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0707_5db3b90c25`
- Source ID: `tidb-docs-8.1:sys-schema/sys-schema-unused-indexes.md#schema-unused-indexes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4fa81eb0a79bf38a1f8282d08f449886b57f46c4914d3fefbc0675c6178e5430`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sys-schema/sys-schema-unused-indexes#schema-unused-indexes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sys-schema/sys-schema-unused-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the definition, columns, or manual creation SQL of the `sys.schema_unused_indexes` view that records indexes not used since the last start of TiDB.
- Retrieval Keywords: schema_unused_indexes, sys.schema_unused_indexes, schema_unused_indexes view, unused indexes since the last start of TiDB, OBJECT_SCHEMA, OBJECT_NAME, INDEX_NAME, USE SYS; DESC SCHEMA_UNUSED_INDEXES;, CREATE OR REPLACE VIEW sys.schema_unused_indexes, information_schema.cluster_tidb_index_usage, sum(last_access_time) is null, index_name != 'PRIMARY', table_schema not in ('sys', 'mysql', 'INFORMATION_SCHEMA', 'PERFORMANCE_SCHEMA'), clusters upgraded from versions earlier than v8.0.0, manually create the sys schema views
- Follow-up Guidance: The source also points to `INFORMATION_SCHEMA.TIDB_INDEX_USAGE` for more information.
- Classification Note: This is reference content because it defines the `schema_unused_indexes` view, lists its columns, and provides the exact SQL used to create it manually.

## Official Source Content

# `schema_unused_indexes`

`schema_unused_indexes` records indexes that have not been used since the last start of TiDB. It includes the following columns:

- `OBJECT_SCHEMA`: The name of the database to which the table containing the index belongs.
- `OBJECT_NAME`: The name of the table containing the index.
- `INDEX_NAME`: The name of the index.

```sql
USE SYS;
DESC SCHEMA_UNUSED_INDEXES;
```

The output is as follows:

```sql
+---------------+-------------+------+------+---------+-------+
| Field         | Type        | Null | Key  | Default | Extra |
+---------------+-------------+------+------+---------+-------+
| object_schema | varchar(64) | YES  |      | NULL    |       |
| object_name   | varchar(64) | YES  |      | NULL    |       |
| index_name    | varchar(64) | YES  |      | NULL    |       |
+---------------+-------------+------+------+---------+-------+
3 rows in set (0.00 sec)
```
## Manually create the `schema_unused_indexes` view

For clusters upgraded from versions earlier than v8.0.0, the `sys` schema and the views in it are not created automatically. You can manually create them using the following SQL statements:

```sql
CREATE DATABASE IF NOT EXISTS sys;
CREATE OR REPLACE VIEW sys.schema_unused_indexes AS
  SELECT
    table_schema as object_schema,
    table_name as object_name,
    index_name
  FROM information_schema.cluster_tidb_index_usage
  WHERE
    table_schema not in ('sys', 'mysql', 'INFORMATION_SCHEMA', 'PERFORMANCE_SCHEMA') and
    index_name != 'PRIMARY'
  GROUP BY table_schema, table_name, index_name
  HAVING
    sum(last_access_time) is null;
```
## Read more

- [`INFORMATION_SCHEMA.TIDB_INDEX_USAGE`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-index-usage)
