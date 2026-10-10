# TIDB_INDEXES table schema and index metadata fields

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-tidb-indexes.md`
- Source Title: `TIDB_INDEXES`
- Source Heading Path: `TIDB_INDEXES`
- Source Line Ranges: `5-66`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `information_schema`, `index-metadata`, `schema-inspection`, `slow-query-correlation`, `table-fields`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0420_6e0ce13843`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-tidb-indexes.md#tidb-indexes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f60311e73bc92536b995ceb3151b027acfa2d74eaf44aff2d6e87db67c9d9bdc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-indexes#tidb-indexes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-tidb-indexes.md

## Retrieval Guidance

- Use When: Use this content when you need the schema of information_schema.TIDB_INDEXES or need to map TABLE_ID and INDEX_ID from SLOW_QUERY or another table/API to specific index metadata.
- Retrieval Keywords: TIDB_INDEXES, information_schema.tidb_indexes, DESC tidb_indexes, INDEX_ID, TABLE_SCHEMA, TABLE_NAME, NON_UNIQUE, KEY_NAME, SEQ_IN_INDEX, COLUMN_NAME, SUB_PART, INDEX_COMMENT, Expression, IS_VISIBLE, CLUSTERED, SLOW_QUERY, TABLE_ID, tables.tidb_table_id, clustered index, PRIMARY
- Follow-up Guidance: The source includes an example SQL join using tidb_indexes and tables with tables.tidb_table_id and index_id to retrieve the specific index information.
- Classification Note: This is reference content because it defines the TIDB_INDEXES table schema and explains the meaning of each index metadata field, including INDEX_ID for joins.

## Official Source Content

# TIDB_INDEXES

The `TIDB_INDEXES` table provides the INDEX information of all tables.

```sql
USE information_schema;
DESC tidb_indexes;
```

```
+---------------+---------------+------+------+---------+-------+
| Field         | Type          | Null | Key  | Default | Extra |
+---------------+---------------+------+------+---------+-------+
| TABLE_SCHEMA  | varchar(64)   | YES  |      | NULL    |       |
| TABLE_NAME    | varchar(64)   | YES  |      | NULL    |       |
| NON_UNIQUE    | bigint(21)    | YES  |      | NULL    |       |
| KEY_NAME      | varchar(64)   | YES  |      | NULL    |       |
| SEQ_IN_INDEX  | bigint(21)    | YES  |      | NULL    |       |
| COLUMN_NAME   | varchar(64)   | YES  |      | NULL    |       |
| SUB_PART      | bigint(21)    | YES  |      | NULL    |       |
| INDEX_COMMENT | varchar(2048) | YES  |      | NULL    |       |
| Expression    | varchar(64)   | YES  |      | NULL    |       |
| INDEX_ID      | bigint(21)    | YES  |      | NULL    |       |
| IS_VISIBLE    | varchar(64)   | YES  |      | NULL    |       |
| CLUSTERED     | varchar(64)   | YES  |      | NULL    |       |
+---------------+---------------+------+------+---------+-------+
12 rows in set (0.00 sec)
```

`INDEX_ID` is the unique ID that TiDB allocates for each index. It can be used to do a join operation with `INDEX_ID` obtained from another table or API.

For example, you can obtain `TABLE_ID` and `INDEX_ID` that are involved in some slow query in the [`SLOW_QUERY` table](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-slow-query) and then obtain the specific index information using the following SQL statements:

```sql
SELECT
 tidb_indexes.*
FROM
 tidb_indexes,
 tables
WHERE
  tidb_indexes.table_schema = tables.table_schema
 AND tidb_indexes.table_name = tidb_indexes.table_name
 AND tables.tidb_table_id = ?
 AND index_id = ?
```

Fields in the `TIDB_INDEXES` table are described as follows:

* `TABLE_SCHEMA`: The name of the schema to which the index belongs.
* `TABLE_NAME`: The name of the table to which the index belongs.
* `NON_UNIQUE`: If the index is unique, the value is `0`; otherwise, the value is `1`.
* `KEY_NAME`: The index name. If the index is the primary key, the name is `PRIMARY`.
* `SEQ_IN_INDEX`: The sequential number of columns in the index, which starts from `1`.
* `COLUMN_NAME`: The name of the column where the index is located.
* `SUB_PART`: The prefix length of the index. If the column is partly indexed, the `SUB_PART` value is the count of the indexed characters; otherwise, the value is `NULL`.
* `INDEX_COMMENT`: The comment of the index, which is made when the index is created.
* `INDEX_ID`: The index ID.
* `IS_VISIBLE`: Whether the index is visible.
* `CLUSTERED`: Whether it is a [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes).
