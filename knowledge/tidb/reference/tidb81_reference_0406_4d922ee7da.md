# INFORMATION_SCHEMA SEQUENCES table and related sequence statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-sequences.md`
- Source Title: `SEQUENCES`
- Source Heading Path: `SEQUENCES | SEQUENCES > See also`
- Source Line Ranges: `5-85`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `information_schema`, `sequences`, `schema-metadata`, `sql-reference`, `create-sequence`, `alter-sequence`, `drop-sequence`, `show-create-sequence`, `sequence-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0406_4d922ee7da`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-sequences.md#sequences`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d413784d2fdc21baa6d8edb95f809db1b896a7a3d3522b0c43a9c3f924693105`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-sequences#sequences
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-sequences.md

## Retrieval Guidance

- Use When: Use this when the query is about inspecting sequence metadata in INFORMATION_SCHEMA or finding the SQL statements and functions related to sequences.
- Retrieval Keywords: INFORMATION_SCHEMA.SEQUENCES, SEQUENCES table, DESC SEQUENCES, SELECT * FROM SEQUENCES, TABLE_CATALOG, SEQUENCE_SCHEMA, SEQUENCE_NAME, CACHE, CACHE_VALUE, CYCLE, INCREMENT, MAX_VALUE, MIN_VALUE, START, COMMENT, CREATE SEQUENCE, ALTER SEQUENCE, DROP SEQUENCE, SHOW CREATE SEQUENCE, SELECT NEXTVAL(test.seq), Sequence functions
- Follow-up Guidance: The source also points to CREATE SEQUENCE, SHOW CREATE SEQUENCE, ALTER SEQUENCE, DROP SEQUENCE, and Sequence functions.
- Classification Note: This is reference content because it defines the INFORMATION_SCHEMA SEQUENCES table schema, shows example queries and output, and lists related sequence statements and functions.

## Official Source Content

# SEQUENCES

The `SEQUENCES` table provides information about sequences. The [sequences feature](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence) is modeled on a similar feature in MariaDB.

```sql
USE INFORMATION_SCHEMA;
DESC SEQUENCES;
```

The output is as follows:

```sql
+-----------------+--------------+------+------+---------+-------+
| Field           | Type         | Null | Key  | Default | Extra |
+-----------------+--------------+------+------+---------+-------+
| TABLE_CATALOG   | varchar(512) | NO   |      | NULL    |       |
| SEQUENCE_SCHEMA | varchar(64)  | NO   |      | NULL    |       |
| SEQUENCE_NAME   | varchar(64)  | NO   |      | NULL    |       |
| CACHE           | tinyint(0)   | NO   |      | NULL    |       |
| CACHE_VALUE     | bigint(21)   | YES  |      | NULL    |       |
| CYCLE           | tinyint(0)   | NO   |      | NULL    |       |
| INCREMENT       | bigint(21)   | NO   |      | NULL    |       |
| MAX_VALUE       | bigint(21)   | YES  |      | NULL    |       |
| MIN_VALUE       | bigint(21)   | YES  |      | NULL    |       |
| START           | bigint(21)   | YES  |      | NULL    |       |
| COMMENT         | varchar(64)  | YES  |      | NULL    |       |
+-----------------+--------------+------+------+---------+-------+
11 rows in set (0.00 sec)
```

Create a sequence `test.seq` and query the next value of the sequence:

```sql
CREATE SEQUENCE test.seq;
SELECT NEXTVAL(test.seq);
SELECT * FROM sequences\G
```

The output is as follows:

```sql
+-------------------+
| NEXTVAL(test.seq) |
+-------------------+
|                 1 |
+-------------------+
1 row in set (0.01 sec)
```

View all sequences:

```sql
SELECT * FROM SEQUENCES\G
```

The output is as follows:

```sql
*************************** 1. row ***************************
  TABLE_CATALOG: def
SEQUENCE_SCHEMA: test
  SEQUENCE_NAME: seq
          CACHE: 1
    CACHE_VALUE: 1000
          CYCLE: 0
      INCREMENT: 1
      MAX_VALUE: 9223372036854775806
      MIN_VALUE: 1
          START: 1
        COMMENT:
1 row in set (0.00 sec)
```
## See also

- [`CREATE SEQUENCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence)
- [`SHOW CREATE SEQUENCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-sequence)
- [`ALTER SEQUENCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-sequence)
- [`DROP SEQUENCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-sequence)
- [Sequence functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/sequence-functions)
