# STATISTICS information_schema table and index metadata fields

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-statistics.md`
- Source Title: `STATISTICS`
- Source Heading Path: `STATISTICS`
- Source Line Ranges: `5-74`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `statistics`, `indexes`, `index-metadata`, `show-index`, `schema-reference`, `expression-index`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0412_2d8fdc0182`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-statistics.md#statistics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `05039f1cf4275a63c65767b4eadadcb3db4b7cc5f7cdec01ae47a85cd3a853b3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-statistics#statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-statistics.md

## Retrieval Guidance

- Use When: Use this chunk when you need the field definitions or equivalent query forms for index metadata in INFORMATION_SCHEMA.STATISTICS or SHOW INDEX.
- Retrieval Keywords: STATISTICS, INFORMATION_SCHEMA.STATISTICS, SHOW INDEX, TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, NON_UNIQUE, INDEX_SCHEMA, INDEX_NAME, PRIMARY, SEQ_IN_INDEX, COLUMN_NAME, COLLATION, CARDINALITY, SUB_PART, PACKED, NULLABLE, INDEX_TYPE, COMMENT, INDEX_COMMENT, IS_VISIBLE, Expression, expression index, SELECT * FROM INFORMATION_SCHEMA.STATISTICS WHERE table_name = 'tbl_name' AND table_schema = 'db_name'
- Follow-up Guidance: The source states that selecting from INFORMATION_SCHEMA.STATISTICS with table_name and table_schema is equivalent to SHOW INDEX FROM tbl_name FROM db_name.
- Classification Note: This is reference content because it defines the STATISTICS information_schema table columns and explains the meaning of each index metadata field.

## Official Source Content

# STATISTICS

The `STATISTICS` table provides information about table indexes.

```sql
USE information_schema;
DESC statistics;
```

```sql
+---------------+---------------+------+------+---------+-------+
| Field         | Type          | Null | Key  | Default | Extra |
+---------------+---------------+------+------+---------+-------+
| TABLE_CATALOG | varchar(512)  | YES  |      | NULL    |       |
| TABLE_SCHEMA  | varchar(64)   | YES  |      | NULL    |       |
| TABLE_NAME    | varchar(64)   | YES  |      | NULL    |       |
| NON_UNIQUE    | varchar(1)    | YES  |      | NULL    |       |
| INDEX_SCHEMA  | varchar(64)   | YES  |      | NULL    |       |
| INDEX_NAME    | varchar(64)   | YES  |      | NULL    |       |
| SEQ_IN_INDEX  | bigint(2)     | YES  |      | NULL    |       |
| COLUMN_NAME   | varchar(21)   | YES  |      | NULL    |       |
| COLLATION     | varchar(1)    | YES  |      | NULL    |       |
| CARDINALITY   | bigint(21)    | YES  |      | NULL    |       |
| SUB_PART      | bigint(3)     | YES  |      | NULL    |       |
| PACKED        | varchar(10)   | YES  |      | NULL    |       |
| NULLABLE      | varchar(3)    | YES  |      | NULL    |       |
| INDEX_TYPE    | varchar(16)   | YES  |      | NULL    |       |
| COMMENT       | varchar(16)   | YES  |      | NULL    |       |
| INDEX_COMMENT | varchar(1024) | YES  |      | NULL    |       |
| IS_VISIBLE    | varchar(3)    | YES  |      | NULL    |       |
| Expression    | varchar(64)   | YES  |      | NULL    |       |
+---------------+---------------+------+------+---------+-------+
18 rows in set (0.00 sec)
```

Fields in the `STATISTICS` table are described as follows:

* `TABLE_CATALOG`: The name of the catalog to which the table containing the index belongs. This value is always `def`.
* `TABLE_SCHEMA`: The name of the database to which the table containing the index belongs.
* `TABLE_NAME`: The name of the table containing the index.
* `NON_UNIQUE`: If the index must not contain duplicate values, the value is `0`; if duplicate values are allowed in the index, the value is `1`.
* `INDEX_SCHEMA`: The name of the database to which the index belongs.
* `INDEX_NAME`: The name of the index. If the index is the primary key, then the value is always `PRIMARY`.
* `SEQ_IN_INDEX`: The column number in the index, starting from `1`.
* `COLUMN_NAME`: The column name. See the description of the `Expression` column.
* `COLLATION`: The sorting method of the columns in the index. The value can be `A` (ascending order), `D` (descending order) or `NULL` (unsorted).
* `CARDINALITY`: TiDB does not use this field. The field value is always `0`.
* `SUB_PART`: The prefix of the index. If only part of the prefix of the column is indexed, the value is the number of indexed characters; if the entire column is indexed, the value is `NULL`.
* `PACKED`: TiDB does not use this field. This value is always `NULL`.
* `NULLABLE`: If the column might contain a `NULL` value, the value is `YES`; if not, the value is `''`.
* `INDEX_TYPE`: The type of the index.
* `COMMENT`: Other information related to the index.
* `INDEX_COMMENT`: Any comment with comment attribute provided for the index when creating the index.
* `IS_VISIBLE`: Whether the optimizer can use this index.
* `Expression` For the index key of the non-expression part, this value is `NULL`; for the index key of the expression part, this value is the expression itself. Refer to [Expression Index](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#expression-index).

The following statements are equivalent:

```sql
SELECT * FROM INFORMATION_SCHEMA.STATISTICS
  WHERE table_name = 'tbl_name'
  AND table_schema = 'db_name'

SHOW INDEX
  FROM tbl_name
  FROM db_name
```
