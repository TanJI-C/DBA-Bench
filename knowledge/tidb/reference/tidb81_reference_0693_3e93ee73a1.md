# START TRANSACTION syntax, examples, and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-start-transaction.md`
- Source Title: `START TRANSACTION | TiDB SQL Statement Reference`
- Source Heading Path: `START TRANSACTION | START TRANSACTION > Synopsis | START TRANSACTION > Examples | START TRANSACTION > MySQL compatibility | START TRANSACTION > See also`
- Source Line Ranges: `5-52`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `transactions`, `autocommit`, `syntax`, `examples`, `mysql-compatibility`, `commit`, `rollback`, `causal-consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0693_3e93ee73a1`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-start-transaction.md#start-transaction`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `67d20d6dda8ecb1e6ff4216801e5955340bb5289324ec5cf1144b003ff4d9db8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-start-transaction#start-transaction
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-start-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB START TRANSACTION syntax, autocommit behavior, examples with COMMIT, or MySQL compatibility details such as READ ONLY and WITH CONSISTENT SNAPSHOT.
- Retrieval Keywords: START TRANSACTION, BEGIN, BeginTransactionStmt, autocommit, START TRANSACTION READ ONLY, START TRANSACTION WITH CONSISTENT SNAPSHOT, START TRANSACTION WITH CAUSAL CONSISTENCY ONLY, AS OF TIMESTAMP, WITH TIMESTAMP BOUND, COMMIT, ROLLBACK, MySQL compatibility
- Follow-up Guidance: See also the related statements COMMIT, ROLLBACK, BEGIN, and START TRANSACTION WITH CAUSAL CONSISTENCY ONLY.
- Classification Note: This is reference content because it defines the START TRANSACTION statement syntax, shows a basic SQL example, and states TiDB-specific MySQL compatibility behavior.

## Official Source Content

# START TRANSACTION

This statement starts a new transaction inside of TiDB. It is similar to the statement `BEGIN`.

In the absence of a `START TRANSACTION` statement, every statement will by default autocommit in its own transaction. This behavior ensures MySQL compatibility.
## Synopsis

**BeginTransactionStmt:**

```ebnf+diagram
BeginTransactionStmt ::=
    'BEGIN' ( 'PESSIMISTIC' | 'OPTIMISTIC' )?
|   'START' 'TRANSACTION' ( 'READ' ( 'WRITE' | 'ONLY' ( ( 'WITH' 'TIMESTAMP' 'BOUND' TimestampBound )? | AsOfClause ) ) | 'WITH' 'CONSISTENT' 'SNAPSHOT' | 'WITH' 'CAUSAL' 'CONSISTENCY' 'ONLY' )?

AsOfClause ::=
    ( 'AS' 'OF' 'TIMESTAMP' Expression)
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

* `START TRANSACTION` immediately starts a transaction inside TiDB. This differs from MySQL, where `START TRANSACTION` lazily creates a transaction. But `START TRANSACTION` in TiDB is equivalent to MySQL's `START TRANSACTION WITH CONSISTENT SNAPSHOT`.

* The statement `START TRANSACTION READ ONLY` is parsed for compatibility with MySQL, but still allows write operations.
## See also

* [COMMIT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-commit)
* [ROLLBACK](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback)
* [BEGIN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-begin)
* [START TRANSACTION WITH CAUSAL CONSISTENCY ONLY](https://docs.pingcap.com/tidb/stable/transaction-overview#causal-consistency)
