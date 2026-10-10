# KEY_COLUMN_USAGE table schema, query example, and column descriptions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-key-column-usage.md`
- Source Title: `KEY_COLUMN_USAGE`
- Source Heading Path: `KEY_COLUMN_USAGE`
- Source Line Ranges: `5-86`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `key constraints`, `primary key`, `foreign key`, `table schema`, `column reference`, `sql query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0393_df45e8094e`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-key-column-usage.md#key-column-usage`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9af4fdf65a7f619554fe308af212215f0485f1e7608365439f5a1074be32f7a1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-key-column-usage#key-column-usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-key-column-usage.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the INFORMATION_SCHEMA.KEY_COLUMN_USAGE table schema, an example query against key_column_usage, or the meaning of columns that describe primary key or foreign key constraints.
- Retrieval Keywords: KEY_COLUMN_USAGE, information_schema, DESC key_column_usage, SELECT * FROM key_column_usage WHERE table_schema='mysql' and table_name='user', CONSTRAINT_CATALOG, CONSTRAINT_SCHEMA, CONSTRAINT_NAME, TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, ORDINAL_POSITION, POSITION_IN_UNIQUE_CONSTRAINT, REFERENCED_TABLE_SCHEMA, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME, primary key constraint, foreign key constraint
- Follow-up Guidance: The source includes a query example for table_schema='mysql' and table_name='user' that returns two PRIMARY constraint rows for the Host and User columns.
- Classification Note: This is reference content because it defines the KEY_COLUMN_USAGE table structure, shows a SQL query example, and describes each column in the table.

## Official Source Content

# KEY_COLUMN_USAGE

The `KEY_COLUMN_USAGE` table describes the key constraints of the columns, such as the primary key constraint.

```sql
USE information_schema;
DESC key_column_usage;
```

```
+-------------------------------+--------------+------+------+---------+-------+
| Field                         | Type         | Null | Key  | Default | Extra |
+-------------------------------+--------------+------+------+---------+-------+
| CONSTRAINT_CATALOG            | varchar(512) | NO   |      | NULL    |       |
| CONSTRAINT_SCHEMA             | varchar(64)  | NO   |      | NULL    |       |
| CONSTRAINT_NAME               | varchar(64)  | NO   |      | NULL    |       |
| TABLE_CATALOG                 | varchar(512) | NO   |      | NULL    |       |
| TABLE_SCHEMA                  | varchar(64)  | NO   |      | NULL    |       |
| TABLE_NAME                    | varchar(64)  | NO   |      | NULL    |       |
| COLUMN_NAME                   | varchar(64)  | NO   |      | NULL    |       |
| ORDINAL_POSITION              | bigint(10)   | NO   |      | NULL    |       |
| POSITION_IN_UNIQUE_CONSTRAINT | bigint(10)   | YES  |      | NULL    |       |
| REFERENCED_TABLE_SCHEMA       | varchar(64)  | YES  |      | NULL    |       |
| REFERENCED_TABLE_NAME         | varchar(64)  | YES  |      | NULL    |       |
| REFERENCED_COLUMN_NAME        | varchar(64)  | YES  |      | NULL    |       |
+-------------------------------+--------------+------+------+---------+-------+
12 rows in set (0.00 sec)
```

```sql
SELECT * FROM key_column_usage WHERE table_schema='mysql' and table_name='user';
```

```
*************************** 1. row ***************************
           CONSTRAINT_CATALOG: def
            CONSTRAINT_SCHEMA: mysql
              CONSTRAINT_NAME: PRIMARY
                TABLE_CATALOG: def
                 TABLE_SCHEMA: mysql
                   TABLE_NAME: user
                  COLUMN_NAME: Host
             ORDINAL_POSITION: 1
POSITION_IN_UNIQUE_CONSTRAINT: NULL
      REFERENCED_TABLE_SCHEMA: NULL
        REFERENCED_TABLE_NAME: NULL
       REFERENCED_COLUMN_NAME: NULL
*************************** 2. row ***************************
           CONSTRAINT_CATALOG: def
            CONSTRAINT_SCHEMA: mysql
              CONSTRAINT_NAME: PRIMARY
                TABLE_CATALOG: def
                 TABLE_SCHEMA: mysql
                   TABLE_NAME: user
                  COLUMN_NAME: User
             ORDINAL_POSITION: 2
POSITION_IN_UNIQUE_CONSTRAINT: NULL
      REFERENCED_TABLE_SCHEMA: NULL
        REFERENCED_TABLE_NAME: NULL
       REFERENCED_COLUMN_NAME: NULL
2 rows in set (0.00 sec)
```

The description of columns in the `KEY_COLUMN_USAGE` table is as follows:

* `CONSTRAINT_CATALOG`: The name of the catalog to which the constraint belongs. The value is always `def`.
* `CONSTRAINT_SCHEMA`: The name of the schema to which the constraint belongs.
* `CONSTRAINT_NAME`: The name of the constraint.
* `TABLE_CATALOG`: The name of the catalog to which the table belongs. The value is always `def`.
* `TABLE_SCHEMA`: The name of the schema to which the table belongs.
* `TABLE_NAME`: The name of the table with constraints.
* `COLUMN_NAME`: The name of the column with constraints.
* `ORDINAL_POSITION`: The position of the column in the constraint, rather than in the table. The position number starts from `1`.
* `POSITION_IN_UNIQUE_CONSTRAINT`: The unique constraint and the primary key constraint are empty. For foreign key constraints, this column is the position of the referenced table's key.
* `REFERENCED_TABLE_SCHEMA`: The name of the schema referenced by the constraint. Currently in TiDB, the value of this column in all constraints is `nil`, except for the foreign key constraint.
* `REFERENCED_TABLE_NAME`: The name of the table referenced by the constraint. Currently in TiDB, the value of this column in all constraints is `nil`, except for the foreign key constraint.
* `REFERENCED_COLUMN_NAME`: The name of the column referenced by the constraint. Currently in TiDB, the value of this column in all constraints is `nil`, except for the foreign key constraint.
