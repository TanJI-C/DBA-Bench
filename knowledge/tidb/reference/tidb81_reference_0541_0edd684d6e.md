# BEGIN statement syntax, usage, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-begin.md`
- Source Title: `BEGIN | TiDB SQL Statement Reference`
- Source Heading Path: `BEGIN | BEGIN > Synopsis | BEGIN > Examples | BEGIN > MySQL compatibility | BEGIN > See also`
- Source Line Ranges: `5-46`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `transactions`, `autocommit`, `syntax`, `examples`, `mysql-compatibility`, `pessimistic`, `optimistic`, `commit`, `rollback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0541_0edd684d6e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-begin.md#begin`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7683e7a08a989074865649f150fc05b6a18ef26d8f2bdfcc39ca3dda7bb74e1d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-begin#begin
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-begin.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about the BEGIN statement in TiDB, its syntax, autocommit behavior, examples, or MySQL compatibility including BEGIN PESSIMISTIC and BEGIN OPTIMISTIC.
- Retrieval Keywords: BEGIN, BEGIN PESSIMISTIC, BEGIN OPTIMISTIC, START TRANSACTION, SET autocommit=0, autocommit, MySQL compatibility, BeginTransactionStmt, READ WRITE, READ ONLY, WITH CONSISTENT SNAPSHOT, WITH TIMESTAMP BOUND, COMMIT, ROLLBACK
- Follow-up Guidance: The source also points to related statements and topics: COMMIT, ROLLBACK, START TRANSACTION, TiDB optimistic transaction model, and TiDB pessimistic transaction mode.
- Classification Note: This is a SQL reference chunk because it defines the BEGIN statement syntax, explains default transaction behavior, shows an example, and notes a TiDB syntax extension for transactional mode selection.

## Official Source Content

# BEGIN

This statement starts a new transaction inside of TiDB. It is similar to the statements `START TRANSACTION` and `SET autocommit=0`.

In the absence of a `BEGIN` statement, every statement will by default autocommit in its own transaction. This behavior ensures MySQL compatibility.
## Synopsis

```ebnf+diagram
BeginTransactionStmt ::=
    'BEGIN' ( 'PESSIMISTIC' | 'OPTIMISTIC' )?
|   'START' 'TRANSACTION' ( 'READ' ( 'WRITE' | 'ONLY' ( 'WITH' 'TIMESTAMP' 'BOUND' TimestampBound )? ) | 'WITH' 'CONSISTENT' 'SNAPSHOT' )?
```
## Examples

```sql
mysql> CREATE TABLE t1 (a int NOT NULL PRIMARY KEY);
Query OK, 0 rows affected (0.12 sec)

mysql> BEGIN;
Query OK, 0 rows affected (0.00 sec)

mysql> INSERT INTO t1 VALUES (1);
Query OK, 1 row affected (0.00 sec)

mysql> COMMIT;
Query OK, 0 rows affected (0.01 sec)
```
## MySQL compatibility

TiDB supports the syntax extension of `BEGIN PESSIMISTIC` or `BEGIN OPTIMISTIC`. This enables you to override the default transactional model for your transaction.
## See also

* [COMMIT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-commit)
* [ROLLBACK](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback)
* [START TRANSACTION](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-start-transaction)
* [TiDB optimistic transaction model](https://docs.pingcap.com/tidb/stable/optimistic-transaction)
* [TiDB pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction)
