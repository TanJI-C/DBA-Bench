# ENGINES information_schema table

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-engines.md`
- Source Title: `ENGINES`
- Source Heading Path: `ENGINES | ENGINES > See also`
- Source Line Ranges: `5-53`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `engines`, `storage-engine`, `compatibility`, `schema-reference`, `show-engines`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0390_60734d6fb7`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-engines.md#engines`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c34fc47943d32d7098bafbcf33bd384763ab8ac33f5391ed4ded2de43701bc9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-engines#engines
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-engines.md

## Retrieval Guidance

- Use When: Use this when the question asks about the `information_schema.ENGINES` table, `SHOW ENGINES`, or what storage engine information TiDB reports for compatibility.
- Retrieval Keywords: information_schema.ENGINES, ENGINES table, SHOW ENGINES, storage engines, InnoDB, SUPPORT DEFAULT, TRANSACTIONS, XA, SAVEPOINTS, SELECT * FROM engines, DESC engines
- Follow-up Guidance: The source also points to `SHOW ENGINES` as a related statement.
- Classification Note: This is a reference entry because it defines the `ENGINES` information_schema table schema, fixed returned values, and the meaning of each column in TiDB.

## Official Source Content

# ENGINES

The `ENGINES` table provides information about storage engines. For compatibility, TiDB will always describe InnoDB as the only supported engine. In addition, other column values in the `ENGINES` table are also fixed values.

```sql
USE information_schema;
DESC engines;
```

```sql
+--------------+-------------+------+------+---------+-------+
| Field        | Type        | Null | Key  | Default | Extra |
+--------------+-------------+------+------+---------+-------+
| ENGINE       | varchar(64) | YES  |      | NULL    |       |
| SUPPORT      | varchar(8)  | YES  |      | NULL    |       |
| COMMENT      | varchar(80) | YES  |      | NULL    |       |
| TRANSACTIONS | varchar(3)  | YES  |      | NULL    |       |
| XA           | varchar(3)  | YES  |      | NULL    |       |
| SAVEPOINTS   | varchar(3)  | YES  |      | NULL    |       |
+--------------+-------------+------+------+---------+-------+
6 rows in set (0.00 sec)
```

```sql
SELECT * FROM engines;
```

```
+--------+---------+------------------------------------------------------------+--------------+------+------------+
| ENGINE | SUPPORT | COMMENT                                                    | TRANSACTIONS | XA   | SAVEPOINTS |
+--------+---------+------------------------------------------------------------+--------------+------+------------+
| InnoDB | DEFAULT | Supports transactions, row-level locking, and foreign keys | YES          | YES  | YES        |
+--------+---------+------------------------------------------------------------+--------------+------+------------+
1 row in set (0.01 sec)
```

The description of columns in the `ENGINES` table is as follows:

* `ENGINES`: The name of the storage engine.
* `SUPPORT`: The level of support that the server has on the storage engine. In TiDB, the value is always `DEFAULT`.
* `COMMENT`: The brief comment on the storage engine.
* `TRANSACTIONS`: Whether the storage engine supports transactions.
* `XA`: Whether the storage engine supports XA transactions.
* `SAVEPOINTS`: Whether the storage engine supports `savepoints`.
## See also

- [`SHOW ENGINES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-engines)
