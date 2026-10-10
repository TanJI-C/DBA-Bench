# SCHEMATA table reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-schemata.md`
- Source Title: `SCHEMATA`
- Source Heading Path: `SCHEMATA`
- Source Line Ranges: `5-51`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `schemata`, `show-databases`, `database-metadata`, `character-set`, `collation`, `sql-path`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0405_d21fa1dc2f`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-schemata.md#schemata`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2a554c3910e302ece5d1ab56d1d99b45ccbf8a4a0c7f3aeecce4e2b5596fa44`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-schemata#schemata
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-schemata.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the `information_schema.SCHEMATA` table definition, its columns, or the statement equivalent to `SHOW DATABASES` for database metadata.
- Retrieval Keywords: SCHEMATA, information_schema, SHOW DATABASES, CATALOG_NAME, SCHEMA_NAME, DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME, SQL_PATH, database name, default character set, default collation, SQL_PATH always NULL
- Follow-up Guidance: The source shows `USE information_schema; DESC SCHEMATA;` and `SELECT * FROM SCHEMATA;` as example queries for this table.
- Classification Note: This is a reference entry because it defines the `SCHEMATA` table structure, sample output, and the meaning of each field.

## Official Source Content

# SCHEMATA

The `SCHEMATA` table provides information about databases. The table data is equivalent to the result of the [`SHOW DATABASES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-databases) statement.

```sql
USE information_schema;
desc SCHEMATA;
```

```
+----------------------------+--------------+------+------+---------+-------+
| Field                      | Type         | Null | Key  | Default | Extra |
+----------------------------+--------------+------+------+---------+-------+
| CATALOG_NAME               | varchar(512) | YES  |      | NULL    |       |
| SCHEMA_NAME                | varchar(64)  | YES  |      | NULL    |       |
| DEFAULT_CHARACTER_SET_NAME | varchar(64)  | YES  |      | NULL    |       |
| DEFAULT_COLLATION_NAME     | varchar(32)  | YES  |      | NULL    |       |
| SQL_PATH                   | varchar(512) | YES  |      | NULL    |       |
+----------------------------+--------------+------+------+---------+-------+
5 rows in set (0.00 sec)
```

```sql
SELECT * FROM SCHEMATA;
```

```
+--------------+--------------------+----------------------------+------------------------+----------+
| CATALOG_NAME | SCHEMA_NAME        | DEFAULT_CHARACTER_SET_NAME | DEFAULT_COLLATION_NAME | SQL_PATH |
+--------------+--------------------+----------------------------+------------------------+----------+
| def          | INFORMATION_SCHEMA | utf8mb4                    | utf8mb4_bin            | NULL     |
| def          | METRICS_SCHEMA     | utf8mb4                    | utf8mb4_bin            | NULL     |
| def          | mysql              | utf8mb4                    | utf8mb4_bin            | NULL     |
| def          | PERFORMANCE_SCHEMA | utf8mb4                    | utf8mb4_bin            | NULL     |
| def          | test               | utf8mb4                    | utf8mb4_bin            | NULL     |
+--------------+--------------------+----------------------------+------------------------+----------+
5 rows in set (0.00 sec)
```

Fields in the `SCHEMATA` table are described as follows:

* `CATALOG_NAME`: The catalog to which the database belongs.
* `SCHEMA_NAME`: The database name.
* `DEFAULT_CHARACTER_SET_NAME`: The default character set of the database.
* `DEFAULT_COLLATION_NAME`: The default collation of the database.
* `SQL_PATH`: The value of this item is always `NULL`.
