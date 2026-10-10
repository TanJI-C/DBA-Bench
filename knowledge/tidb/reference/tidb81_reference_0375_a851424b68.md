# CHECK_CONSTRAINTS table overview and fields

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-check-constraints.md`
- Source Title: `CHECK_CONSTRAINTS`
- Source Heading Path: `CHECK\_CONSTRAINTS`
- Source Line Ranges: `5-53`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `check_constraints`, `check`, `create table`, `schema metadata`, `constraint fields`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0375_a851424b68`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-check-constraints.md#check-constraints`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9d3072e8b8d5e1d56f2b56bb6d3b607e7fa0de089571fbd397e550ac8723b364`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-check-constraints#check-constraints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-check-constraints.md

## Retrieval Guidance

- Use When: Use this chunk when looking up what the INFORMATION_SCHEMA.CHECK_CONSTRAINTS table contains, how to inspect its columns, or what metadata is returned for CHECK constraints.
- Retrieval Keywords: CHECK_CONSTRAINTS, INFORMATION_SCHEMA, DESC CHECK_CONSTRAINTS, CHECK constraints, CONSTRAINT_CATALOG, CONSTRAINT_SCHEMA, CONSTRAINT_NAME, CHECK_CLAUSE, CREATE TABLE test.t1 (id INT PRIMARY KEY, CHECK (id%2 = 0)), SET GLOBAL tidb_enable_check_constraint = ON, SELECT * FROM CHECK_CONSTRAINTS, t1_chk_1, def
- Follow-up Guidance: The example shows enabling tidb_enable_check_constraint, creating a table with CHECK (id%2 = 0), and querying CHECK_CONSTRAINTS to return CONSTRAINT_CATALOG def, CONSTRAINT_SCHEMA test, CONSTRAINT_NAME t1_chk_1, and CHECK_CLAUSE (`id` % 2 = 0).
- Classification Note: This is reference content because it defines the CHECK_CONSTRAINTS information_schema table, lists its fields, and demonstrates the returned metadata for a CHECK constraint.

## Official Source Content

# CHECK\_CONSTRAINTS

The `CHECK_CONSTRAINTS` table provides information about [`CHECK` constraints](https://docs.pingcap.com/tidb/stable/constraints#check) on tables.

```sql
USE INFORMATION_SCHEMA;
DESC CHECK_CONSTRAINTS;
```

The output is as follows:

```sql
+--------------------+-------------+------+-----+---------+-------+
| Field              | Type        | Null | Key | Default | Extra |
+--------------------+-------------+------+-----+---------+-------+
| CONSTRAINT_CATALOG | varchar(64) | NO   |     | NULL    |       |
| CONSTRAINT_SCHEMA  | varchar(64) | NO   |     | NULL    |       |
| CONSTRAINT_NAME    | varchar(64) | NO   |     | NULL    |       |
| CHECK_CLAUSE       | longtext    | NO   |     | NULL    |       |
+--------------------+-------------+------+-----+---------+-------+
4 rows in set (0.00 sec)
```

The following example adds a `CHECK` constraint using the `CREATE TABLE` statement:

```sql
SET GLOBAL tidb_enable_check_constraint = ON;
CREATE TABLE test.t1 (id INT PRIMARY KEY, CHECK (id%2 = 0));
SELECT * FROM CHECK_CONSTRAINTS\G
```

The output is as follows:

```sql
*************************** 1. row ***************************
CONSTRAINT_CATALOG: def
 CONSTRAINT_SCHEMA: test
   CONSTRAINT_NAME: t1_chk_1
      CHECK_CLAUSE: (`id` % 2 = 0)
1 row in set (0.00 sec)
```

Fields in the `CHECK_CONSTRAINTS` table are described as follows:

* `CONSTRAINT_CATALOG`: The catalog of the constraint, which is always `def`.
* `CONSTRAINT_SCHEMA`: The schema of the constraint.
* `CONSTRAINT_NAME`: The name of the constraint.
* `CHECK_CLAUSE`: The clause of the check constraint.
