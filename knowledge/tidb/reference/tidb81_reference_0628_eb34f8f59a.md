# ROLLBACK statement syntax, example, and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-rollback.md`
- Source Title: `ROLLBACK | TiDB SQL Statement Reference`
- Source Heading Path: `ROLLBACK | ROLLBACK > Synopsis | ROLLBACK > Examples | ROLLBACK > MySQL compatibility | ROLLBACK > See also`
- Source Line Ranges: `5-50`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `transaction`, `rollback`, `syntax`, `examples`, `mysql-compatibility`, `savepoint`, `commit`, `begin`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0628_eb34f8f59a`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-rollback.md#rollback`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c8583e0f030aeee86ff17eaacc8358f8b253d6cbf951844bc1d27ac138196929`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback#rollback
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-rollback.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about the TiDB SQL ROLLBACK statement syntax, what it does to the current transaction, an example showing reverted changes, or how ROLLBACK AND CHAIN or ROLLBACK AND RELEASE behave in TiDB versus MySQL.
- Retrieval Keywords: ROLLBACK, RollbackStmt, CompletionTypeWithinTransaction, ROLLBACK AND CHAIN, ROLLBACK AND NO CHAIN, ROLLBACK AND RELEASE, ROLLBACK AND NO RELEASE, transaction, COMMIT, BEGIN, START TRANSACTION, SAVEPOINT, MySQL compatibility, parses but ignores, mysql_close()
- Follow-up Guidance: Related statements linked from this source are SAVEPOINT, COMMIT, BEGIN, and START TRANSACTION.
- Classification Note: This is reference content because it defines the ROLLBACK statement syntax, gives a transactional example, and states MySQL compatibility details for parsed but ignored options.

## Official Source Content

# ROLLBACK

This statement reverts all changes in the current transaction inside of TiDB. It is the opposite of a `COMMIT` statement.
## Synopsis

```ebnf+diagram
RollbackStmt ::=
    'ROLLBACK' CompletionTypeWithinTransaction?

CompletionTypeWithinTransaction ::=
    'AND' ( 'CHAIN' ( 'NO' 'RELEASE' )? | 'NO' 'CHAIN' ( 'NO'? 'RELEASE' )? )
|   'NO'? 'RELEASE'
```
## Examples

```sql
mysql> CREATE TABLE t1 (a INT NOT NULL PRIMARY KEY);
Query OK, 0 rows affected (0.12 sec)

mysql> BEGIN;
Query OK, 0 rows affected (0.00 sec)

mysql> INSERT INTO t1 VALUES (1);
Query OK, 1 row affected (0.00 sec)

mysql> ROLLBACK;
Query OK, 0 rows affected (0.01 sec)

mysql> SELECT * FROM t1;
Empty set (0.01 sec)
```
## MySQL compatibility

* TiDB parses but ignores the syntax `ROLLBACK AND [NO] RELEASE`. This functionality is used in MySQL to disconnect the client session immediately after rolling back the transaction. In TiDB, it is recommended to instead use the `mysql_close()` functionality of your client driver.
* TiDB parses but ignores the syntax `ROLLBACK AND [NO] CHAIN`. This functionality is used in MySQL to immediately start a new transaction with the same isolation level while the current transaction is being rolled back. In TiDB, it is recommended to instead start a new transaction.
## See also

* [SAVEPOINT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-savepoint)
* [COMMIT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-commit)
* [BEGIN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-begin)
* [START TRANSACTION](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-start-transaction)
