# TIDB_CHECK_CONSTRAINTS table structure and fields

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-tidb-check-constraints.md`
- Source Title: `TIDB_CHECK_CONSTRAINTS`
- Source Heading Path: `TIDB\_CHECK\_CONSTRAINTS`
- Source Line Ranges: `5-59`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `information_schema`, `check-constraints`, `metadata`, `schema`, `table-id`, `sql-reference`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0416_c2712be030`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-tidb-check-constraints.md#tidb-check-constraints`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `95a027468dbe860cefeda71e0b68917b5a8a7017fd1a734084b2b67cb0d454c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-check-constraints#tidb-check-constraints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-tidb-check-constraints.md

## Retrieval Guidance

- Use When: Use this content when looking up the INFORMATION_SCHEMA table that exposes CHECK constraint metadata together with the defining table name and table ID in TiDB.
- Retrieval Keywords: TIDB_CHECK_CONSTRAINTS, INFORMATION_SCHEMA, CHECK_CONSTRAINTS, CHECK constraints, TABLE_NAME, TABLE_ID, CONSTRAINT_CATALOG, CONSTRAINT_SCHEMA, CONSTRAINT_NAME, CHECK_CLAUSE, DESC TIDB_CHECK_CONSTRAINTS, SELECT * FROM TIDB_CHECK_CONSTRAINTS, tidb_enable_check_constraint, CREATE TABLE test.t1 (id INT PRIMARY KEY, CHECK (id%2 = 0))
- Follow-up Guidance: The source includes an example that enables tidb_enable_check_constraint, creates a table with a CHECK constraint, and queries TIDB_CHECK_CONSTRAINTS to show CONSTRAINT_NAME, CHECK_CLAUSE, TABLE_NAME, and TABLE_ID.
- Classification Note: This is reference content because it defines the TIDB_CHECK_CONSTRAINTS information schema table, lists its fields and meanings, and shows example SQL output.

## Official Source Content

# TIDB\_CHECK\_CONSTRAINTS

The `TIDB_CHECK_CONSTRAINTS` table provides information about [`CHECK` constraints](https://docs.pingcap.com/tidb/stable/constraints#check) on tables. In addition to the columns in [`CHECK_CONSTRAINTS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-check-constraints), `TIDB_CHECK_CONSTRAINTS` provides the name and ID of the table that defines the `CHECK` constraint.

```sql
USE INFORMATION_SCHEMA;
DESC TIDB_CHECK_CONSTRAINTS;
```

The output is as follows:

```sql
+--------------------+-------------+------+------+---------+-------+
| Field              | Type        | Null | Key  | Default | Extra |
+--------------------+-------------+------+------+---------+-------+
| CONSTRAINT_CATALOG | varchar(64) | NO   |      | NULL    |       |
| CONSTRAINT_SCHEMA  | varchar(64) | NO   |      | NULL    |       |
| CONSTRAINT_NAME    | varchar(64) | NO   |      | NULL    |       |
| CHECK_CLAUSE       | longtext    | NO   |      | NULL    |       |
| TABLE_NAME         | varchar(64) | YES  |      | NULL    |       |
| TABLE_ID           | bigint(21)  | YES  |      | NULL    |       |
+--------------------+-------------+------+------+---------+-------+
6 rows in set (0.00 sec)
```

The following example adds a `CHECK` constraint using the `CREATE TABLE` statement:

```sql
SET GLOBAL tidb_enable_check_constraint = ON;
CREATE TABLE test.t1 (id INT PRIMARY KEY, CHECK (id%2 = 0));
SELECT * FROM TIDB_CHECK_CONSTRAINTS\G
```

The output is as follows:

```sql
*************************** 1. row ***************************
CONSTRAINT_CATALOG: def
 CONSTRAINT_SCHEMA: test
   CONSTRAINT_NAME: t1_chk_1
      CHECK_CLAUSE: (`id` % 2 = 0)
        TABLE_NAME: t1
          TABLE_ID: 107
1 row in set (0.02 sec)
```

Fields in the `TIDB_CHECK_CONSTRAINTS` table are described as follows:

* `CONSTRAINT_CATALOG`: The catalog of the constraint, which is always `def`.
* `CONSTRAINT_SCHEMA`: The schema of the constraint.
* `CONSTRAINT_NAME`: The name of the constraint.
* `CHECK_CLAUSE`: The clause of the check constraint.
* `TABLE_NAME`: The name of the table where the constraint is located.
* `TABLE_ID`: The ID of the table where the constraint is located.
