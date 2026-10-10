# COMMIT statement syntax, example, and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-commit.md`
- Source Title: `COMMIT | TiDB SQL Statement Reference`
- Source Heading Path: `COMMIT | COMMIT > Synopsis | COMMIT > Examples | COMMIT > MySQL compatibility | COMMIT > See also`
- Source Line Ranges: `5-52`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `commit`, `transactions`, `autocommit`, `syntax`, `examples`, `mysql-compatibility`, `metadata-locking`, `pessimistic-locking`, `optimistic-locking`, `constraint-checking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0547_7cf044bbf9`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-commit.md#commit`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fc5d05ae58c823d514663efab85897feb1bb6aeeefb404c61b7f59d6ae136512`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-commit#commit
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-commit.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about the TiDB COMMIT statement syntax, a basic transaction commit example, autocommit behavior, or MySQL compatibility details that affect COMMIT.
- Retrieval Keywords: COMMIT, CommitStmt, CompletionTypeWithinTransaction, START TRANSACTION, BEGIN, autocommit, MySQL compatibility, Metadata Lock, MDL, Pessimistic Locking, Optimistic Locking, tidb_constraint_check_in_place, UNIQUE constraint checks deferred until statement commit, PRIMARY KEY constraint checks deferred until statement commit, COMMIT might fail because rows have been modified by another transaction, COMMIT AND CHAIN, COMMIT AND NO RELEASE, NO RELEASE, NO CHAIN
- Follow-up Guidance: See also START TRANSACTION, ROLLBACK, BEGIN, and Lazy checking of constraints.
- Classification Note: This is reference content because it defines COMMIT syntax, shows a SQL example, and lists compatibility behaviors such as metadata locking, pessimistic or optimistic locking, and deferred constraint checks.

## Official Source Content

# COMMIT

This statement commits a transaction inside of the TiDB server.

In the absence of a `BEGIN` or `START TRANSACTION` statement, the default behavior of TiDB is that every statement will be its own transaction and autocommit. This behavior ensures MySQL compatibility.
## Synopsis

```ebnf+diagram
CommitStmt ::=
    'COMMIT' CompletionTypeWithinTransaction?

CompletionTypeWithinTransaction ::=
    'AND' ( 'CHAIN' ( 'NO' 'RELEASE' )? | 'NO' 'CHAIN' ( 'NO'? 'RELEASE' )? )
|   'NO'? 'RELEASE'
```
## Examples

```sql
mysql> CREATE TABLE t1 (a int NOT NULL PRIMARY KEY);
Query OK, 0 rows affected (0.12 sec)

mysql> START TRANSACTION;
Query OK, 0 rows affected (0.00 sec)

mysql> INSERT INTO t1 VALUES (1);
Query OK, 1 row affected (0.00 sec)

mysql> COMMIT;
Query OK, 0 rows affected (0.01 sec)
```
## MySQL compatibility

* Currently, TiDB use Metadata Locking (MDL) to prevent DDL statements from modifying tables used by transactions by default. The behavior of metadata lock is different between TiDB and MySQL. For more details, see [Metadata Lock](https://docs.pingcap.com/tidb/stable/metadata-lock).
* By default, TiDB 3.0.8 and later versions use [Pessimistic Locking](https://docs.pingcap.com/tidb/stable/pessimistic-transaction). When using [Optimistic Locking](https://docs.pingcap.com/tidb/stable/optimistic-transaction), it is important to consider that a `COMMIT` statement might fail because rows have been modified by another transaction.
* When Optimistic Locking is enabled, `UNIQUE` and `PRIMARY KEY` constraint checks are deferred until statement commit. This results in additional situations where a `COMMIT` statement might fail. This behavior can be changed by setting `tidb_constraint_check_in_place=ON`.
* TiDB parses but ignores the syntax `ROLLBACK AND [NO] RELEASE`. This functionality is used in MySQL to disconnect the client session immediately after committing the transaction. In TiDB, it is recommended to instead use the `mysql_close()` functionality of your client driver.
* TiDB parses but ignores the syntax `ROLLBACK AND [NO] CHAIN`. This functionality is used in MySQL to immediately start a new transaction with the same isolation level while the current transaction is being committed. In TiDB, it is recommended to instead start a new transaction.
## See also

* [START TRANSACTION](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-start-transaction)
* [ROLLBACK](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback)
* [BEGIN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-begin)
* [Lazy checking of constraints](https://docs.pingcap.com/tidb/stable/transaction-overview#lazy-check-of-constraints)
