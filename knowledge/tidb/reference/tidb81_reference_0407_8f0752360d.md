# SESSION_VARIABLES table overview and columns

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-session-variables.md`
- Source Title: `SESSION_VARIABLES`
- Source Heading Path: `SESSION_VARIABLES`
- Source Line Ranges: `5-56`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `session variables`, `show variables`, `table schema`, `sql query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0407_8f0752360d`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-session-variables.md#session-variables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cfc48dd79db2f873a42945ad7aa6426c9abfd86dfd92cc2ee4085ded95791600`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-session-variables#session-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-session-variables.md

## Retrieval Guidance

- Use When: Use this chunk when asking about the INFORMATION_SCHEMA.SESSION_VARIABLES table, its columns, or how it relates to SHOW SESSION VARIABLES in TiDB.
- Retrieval Keywords: SESSION_VARIABLES, INFORMATION_SCHEMA, SHOW SESSION VARIABLES, VARIABLE_NAME, VARIABLE_VALUE, DESC SESSION_VARIABLES, SELECT * FROM SESSION_VARIABLES ORDER BY variable_name LIMIT 10, session variables table schema
- Follow-up Guidance: The content also shows example SQL for DESC SESSION_VARIABLES and querying the first 10 rows from SESSION_VARIABLES ordered by variable_name.
- Classification Note: This is reference content because it defines the SESSION_VARIABLES table, lists its schema columns, and shows example queries and output.

## Official Source Content

# SESSION_VARIABLES

The `SESSION_VARIABLES` table provides information about session variables. The table data is similar to the result of the [`SHOW SESSION VARIABLES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-variables) statement.

```sql
USE INFORMATION_SCHEMA;
DESC SESSION_VARIABLES;
```

The output is as follows:

```sql
+----------------+---------------+------+------+---------+-------+
| Field          | Type          | Null | Key  | Default | Extra |
+----------------+---------------+------+------+---------+-------+
| VARIABLE_NAME  | varchar(64)   | YES  |      | NULL    |       |
| VARIABLE_VALUE | varchar(1024) | YES  |      | NULL    |       |
+----------------+---------------+------+------+---------+-------+
2 rows in set (0.00 sec)
```

Query the first 10 rows of the `SESSION_VARIABLES` table:

```sql
SELECT * FROM SESSION_VARIABLES ORDER BY variable_name LIMIT 10;
```

The output is as follows:

```sql
+-----------------------------------+------------------+
| VARIABLE_NAME                     | VARIABLE_VALUE   |
+-----------------------------------+------------------+
| allow_auto_random_explicit_insert | OFF              |
| auto_increment_increment          | 1                |
| auto_increment_offset             | 1                |
| autocommit                        | ON               |
| automatic_sp_privileges           | 1                |
| avoid_temporal_upgrade            | OFF              |
| back_log                          | 80               |
| basedir                           | /usr/local/mysql |
| big_tables                        | OFF              |
| bind_address                      | *                |
+-----------------------------------+------------------+
10 rows in set (0.00 sec)
```

The description of columns in the `SESSION_VARIABLES` table is as follows:

* `VARIABLE_NAME`: The name of the session-level variable in the database.
* `VARIABLE_VALUE`: The value of the session-level variable in the database.
