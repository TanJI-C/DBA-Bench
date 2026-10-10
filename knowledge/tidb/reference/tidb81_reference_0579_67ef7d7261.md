# DROP SEQUENCE syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-drop-sequence.md`
- Source Title: `DROP SEQUENCE`
- Source Heading Path: `DROP SEQUENCE | DROP SEQUENCE > Synopsis | DROP SEQUENCE > Examples | DROP SEQUENCE > MySQL compatibility | DROP SEQUENCE > See also`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `ddl`, `sequence`, `drop-sequence`, `syntax`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0579_67ef7d7261`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-drop-sequence.md#drop-sequence`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `80320de2de1fe8295e88db0a0a75e202b2422cac2d80b3a06f1272a7c78a1d40`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-sequence#drop-sequence
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-drop-sequence.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB SQL syntax, example statements, or compatibility note for dropping one or more sequence objects.
- Retrieval Keywords: DROP SEQUENCE, DROP SEQUENCE syntax, DROP SEQUENCE IF EXISTS, DropSequenceStmt, TableNameList, DROP SEQUENCE seq;, DROP SEQUENCE seq, seq2;, sequence object, TiDB extension, MariaDB sequences, MySQL compatibility
- Follow-up Guidance: Related statements listed here are CREATE SEQUENCE, ALTER SEQUENCE, and SHOW CREATE SEQUENCE.
- Classification Note: This is reference content because it defines the DROP SEQUENCE statement, provides the formal synopsis and examples, and notes MySQL compatibility.

## Official Source Content

# DROP SEQUENCE

The `DROP SEQUENCE` statement drops the sequence object in TiDB.
## Synopsis

```ebnf+diagram
DropSequenceStmt ::=
    'DROP' 'SEQUENCE' IfExists TableNameList

IfExists ::= ( 'IF' 'EXISTS' )?

TableNameList ::=
    TableName ( ',' TableName )*

TableName ::=
    Identifier ('.' Identifier)?
```
## Examples

```sql
DROP SEQUENCE seq;
```

```
Query OK, 0 rows affected (0.10 sec)
```

```sql
DROP SEQUENCE seq, seq2;
```

```
Query OK, 0 rows affected (0.03 sec)
```
## MySQL compatibility

This statement is a TiDB extension. The implementation is modeled on sequences available in MariaDB.
## See also

* [CREATE SEQUENCE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence)
* [ALTER SEQUENCE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-sequence)
* [SHOW CREATE SEQUENCE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-sequence)
