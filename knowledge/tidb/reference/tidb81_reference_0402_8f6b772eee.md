# REFERENTIAL_CONSTRAINTS table schema and foreign key example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-referential-constraints.md`
- Source Title: `REFERENTIAL_CONSTRAINTS`
- Source Heading Path: `REFERENTIAL_CONSTRAINTS`
- Source Line Ranges: `5-69`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `referential_constraints`, `foreign_key`, `table_schema`, `constraint_metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0402_8f6b772eee`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-referential-constraints.md#referential-constraints`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f485808862e1173e8d545d9a5bc7be15c29dabd6b3f2669d53505b2559b67a82`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-referential-constraints#referential-constraints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-referential-constraints.md

## Retrieval Guidance

- Use When: Use this chunk when looking for INFORMATION_SCHEMA metadata about FOREIGN KEY relationships, including the REFERENTIAL_CONSTRAINTS table schema and an example showing update and delete rules.
- Retrieval Keywords: REFERENTIAL_CONSTRAINTS, INFORMATION_SCHEMA, FOREIGN KEY, CONSTRAINT_NAME, UNIQUE_CONSTRAINT_NAME, MATCH_OPTION, UPDATE_RULE, DELETE_RULE, TABLE_NAME, REFERENCED_TABLE_NAME, DESC REFERENTIAL_CONSTRAINTS, SELECT * FROM REFERENTIAL_CONSTRAINTS, fk_parent, ON UPDATE CASCADE, ON DELETE RESTRICT
- Follow-up Guidance: The source includes a SQL example that creates test.parent and test.child with CONSTRAINT fk_parent and then queries SELECT * FROM REFERENTIAL_CONSTRAINTS\G to show the resulting metadata.
- Classification Note: This is reference content because it defines the REFERENTIAL_CONSTRAINTS table columns and shows example output for foreign key constraint metadata in SQL.

## Official Source Content

# REFERENTIAL_CONSTRAINTS

The `REFERENTIAL_CONSTRAINTS` table provides information about [`FOREIGN KEY`](https://docs.pingcap.com/tidb/stable/foreign-key) relationships between tables.

```sql
USE INFORMATION_SCHEMA;
DESC REFERENTIAL_CONSTRAINTS;
```

The output is as follows:

```sql
+---------------------------+--------------+------+------+---------+-------+
| Field                     | Type         | Null | Key  | Default | Extra |
+---------------------------+--------------+------+------+---------+-------+
| CONSTRAINT_CATALOG        | varchar(512) | NO   |      | NULL    |       |
| CONSTRAINT_SCHEMA         | varchar(64)  | NO   |      | NULL    |       |
| CONSTRAINT_NAME           | varchar(64)  | NO   |      | NULL    |       |
| UNIQUE_CONSTRAINT_CATALOG | varchar(512) | NO   |      | NULL    |       |
| UNIQUE_CONSTRAINT_SCHEMA  | varchar(64)  | NO   |      | NULL    |       |
| UNIQUE_CONSTRAINT_NAME    | varchar(64)  | YES  |      | NULL    |       |
| MATCH_OPTION              | varchar(64)  | NO   |      | NULL    |       |
| UPDATE_RULE               | varchar(64)  | NO   |      | NULL    |       |
| DELETE_RULE               | varchar(64)  | NO   |      | NULL    |       |
| TABLE_NAME                | varchar(64)  | NO   |      | NULL    |       |
| REFERENCED_TABLE_NAME     | varchar(64)  | NO   |      | NULL    |       |
+---------------------------+--------------+------+------+---------+-------+
11 rows in set (0.00 sec)
```

```sql
CREATE TABLE test.parent (
  id INT NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (id)
);

CREATE TABLE test.child (
  id INT NOT NULL AUTO_INCREMENT,
  name varchar(255) NOT NULL,
  parent_id INT DEFAULT NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_parent FOREIGN KEY (parent_id) REFERENCES parent (id) ON UPDATE CASCADE ON DELETE RESTRICT
);

SELECT * FROM REFERENTIAL_CONSTRAINTS\G
```

The output is as follows:

```sql
*************************** 1. row ***************************
       CONSTRAINT_CATALOG: def
        CONSTRAINT_SCHEMA: test
          CONSTRAINT_NAME: fk_parent
UNIQUE_CONSTRAINT_CATALOG: def
 UNIQUE_CONSTRAINT_SCHEMA: test
   UNIQUE_CONSTRAINT_NAME: PRIMARY
             MATCH_OPTION: NONE
              UPDATE_RULE: CASCADE
              DELETE_RULE: RESTRICT
               TABLE_NAME: child
    REFERENCED_TABLE_NAME: parent
1 row in set (0.00 sec)
```
