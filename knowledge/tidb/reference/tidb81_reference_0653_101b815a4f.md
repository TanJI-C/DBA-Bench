# SHOW CREATE SEQUENCE syntax and example output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-create-sequence.md`
- Source Title: `SHOW CREATE SEQUENCE`
- Source Heading Path: `SHOW CREATE SEQUENCE | SHOW CREATE SEQUENCE > Synopsis | SHOW CREATE SEQUENCE > Examples | SHOW CREATE SEQUENCE > MySQL compatibility | SHOW CREATE SEQUENCE > See also`
- Source Line Ranges: `5-48`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show create sequence`, `sequence`, `sql syntax`, `examples`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0653_101b815a4f`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-create-sequence.md#show-create-sequence`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ad675517dd7d712eb4ff3b09c83f308ff53e6aada1e6ca1e413fabedb734bbb2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-sequence#show-create-sequence
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-create-sequence.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the syntax, example output, or compatibility note for displaying the detailed definition of a sequence with SHOW CREATE SEQUENCE.
- Retrieval Keywords: SHOW CREATE SEQUENCE, ShowCreateSequenceStmt, SHOW CREATE SEQUENCE ( SchemaName "." )? TableName, SHOW CREATE SEQUENCE seq, CREATE SEQUENCE seq, Create Table, CREATE SEQUENCE `seq` start with 1 minvalue 1 maxvalue 9223372036854775806 increment by 1 cache 1000 nocycle ENGINE=InnoDB, sequence, TiDB extension, MariaDB
- Follow-up Guidance: The page also links to CREATE SEQUENCE, ALTER SEQUENCE, and DROP SEQUENCE.
- Classification Note: This is reference content because it defines the SHOW CREATE SEQUENCE statement syntax, shows example SQL and output, and notes MySQL compatibility.

## Official Source Content

# SHOW CREATE SEQUENCE

The `SHOW CREATE SEQUENCE` shows the detailed information of a sequence, which is similar to `SHOW CREATE TABLE`.
## Synopsis

```ebnf+diagram
ShowCreateSequenceStmt ::=
    "SHOW" "CREATE" "SEQUENCE" ( SchemaName "." )? TableName
```
## Examples

```sql
CREATE SEQUENCE seq;
```

```
Query OK, 0 rows affected (0.03 sec)
```

```sql
SHOW CREATE SEQUENCE seq;
```

```
+-------+----------------------------------------------------------------------------------------------------------------------------+
| Table | Create Table                                                                                                               |
+-------+----------------------------------------------------------------------------------------------------------------------------+
| seq   | CREATE SEQUENCE `seq` start with 1 minvalue 1 maxvalue 9223372036854775806 increment by 1 cache 1000 nocycle ENGINE=InnoDB |
+-------+----------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension. The implementation is modeled on sequences available in MariaDB.
## See also

* [CREATE SEQUENCE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence)
* [ALTER SEQUENCE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-sequence)
* [DROP SEQUENCE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-sequence)
