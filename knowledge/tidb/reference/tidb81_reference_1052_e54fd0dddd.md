# Transaction statements, autocommit, and rollback behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/transaction-overview.md`
- Source Title: `Transactions`
- Source Heading Path: `Transactions | Transactions > Common statements | Transactions > Common statements > Starting a transaction | Transactions > Common statements > Committing a transaction | Transactions > Common statements > Rolling back a transaction | Transactions > Autocommit | Transactions > Explicit and implicit transaction | Transactions > Lazy check of constraints | Transactions > Statement rollback`
- Source Line Ranges: `5-288`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `transactions`, `begin`, `commit`, `rollback`, `autocommit`, `explicit-transactions`, `implicit-transactions`, `constraint-checking`, `optimistic-transactions`, `pessimistic-transactions`, `statement-rollback`, `ddl`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1052_e54fd0dddd`
- Source ID: `tidb-docs-8.1:transaction-overview.md#transactions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `98439446d7eeeda68a3e8287503d529d216d58df0e082d2d7bd66d31ca817bd8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/transaction-overview#transactions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/transaction-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about TiDB transaction statements and behavior such as BEGIN or START TRANSACTION, COMMIT, ROLLBACK, autocommit, explicit versus implicit transactions, lazy constraint checking in optimistic transactions, or statement rollback after an error.
- Retrieval Keywords: BEGIN, START TRANSACTION, START TRANSACTION WITH CONSISTENT SNAPSHOT, START TRANSACTION WITH CAUSAL CONSISTENCY ONLY, COMMIT, ROLLBACK, @@autocommit, SET autocommit = 0, SET GLOBAL autocommit = 0, explicit transaction, implicit transaction, autocommit, BEGIN OPTIMISTIC, tidb_txn_mode, tidb_disable_txn_auto_retry, tidb_retry_limit, tidb_constraint_check_in_place, lazy check of constraints, Duplicate entry '1' for key 't1.PRIMARY', ERROR 1062 (23000), ERROR 1146 (42S02): Table 'test.tset' doesn't exist, statement rollback, DDL statements committed automatically, client connection aborted or closed
- Follow-up Guidance: The source also notes that TiDB uses pessimistic transaction mode by default starting from TiDB 3.0.8, and that some variables such as tidb_disable_txn_auto_retry and tidb_retry_limit only apply to optimistic transactions.
- Classification Note: This is reference content because it explains the semantics and syntax of transaction-related SQL statements, system variables, and error behaviors in TiDB.

## Official Source Content

# Transactions

TiDB supports distributed transactions using either [pessimistic](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) or [optimistic](https://docs.pingcap.com/tidb/stable/optimistic-transaction) transaction mode. Starting from TiDB 3.0.8, TiDB uses the pessimistic transaction mode by default.

This document introduces commonly used transaction-related statements, explicit and implicit transactions, isolation levels, lazy check for constraints, and transaction sizes.

The common variables include [`autocommit`](#autocommit), [`tidb_disable_txn_auto_retry`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_disable_txn_auto_retry), [`tidb_retry_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_retry_limit), and [`tidb_txn_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_txn_mode).

> **Note:**
>
> The [`tidb_disable_txn_auto_retry`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_disable_txn_auto_retry) and [`tidb_retry_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_retry_limit) variables only apply to optimistic transactions, not to pessimistic transactions.
## Common statements
### Starting a transaction

The statements [`BEGIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-begin) and [`START TRANSACTION`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-start-transaction) can be used interchangeably to explicitly start a new transaction.

Syntax:

```sql
BEGIN;
```

```sql
START TRANSACTION;
```

```sql
START TRANSACTION WITH CONSISTENT SNAPSHOT;
```

```sql
START TRANSACTION WITH CAUSAL CONSISTENCY ONLY;
```

If the current session is in the process of a transaction when one of these statements is executed, TiDB automatically commits the current transaction before starting a new transaction.

> **Note:**
>
> Unlike MySQL, TiDB takes a snapshot of the current database after executing the statements above. MySQL's `BEGIN` and `START TRANSACTION` take a snapshot after executing the first `SELECT` statement (not `SELECT FOR UPDATE`) that reads data from InnoDB after a transaction is started. `START TRANSACTION WITH CONSISTENT SNAPSHOT` takes a snapshot during the execution of the statement. As a result, `BEGIN`, `START TRANSACTION`, and `START TRANSACTION WITH CONSISTENT SNAPSHOT` are equivalent to `START TRANSACTION WITH CONSISTENT SNAPSHOT` in MySQL.
### Committing a transaction

The statement [`COMMIT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-commit) instructs TiDB to apply all changes made in the current transaction.

Syntax:

```sql
COMMIT;
```

> **Tip:**
>
> Make sure that your application correctly handles that a `COMMIT` statement could return an error before enabling [optimistic transactions](https://docs.pingcap.com/tidb/stable/optimistic-transaction). If you are unsure of how your application handles this, it is recommended to instead use the default of [pessimistic transactions](https://docs.pingcap.com/tidb/stable/pessimistic-transaction).
### Rolling back a transaction

The statement [`ROLLBACK`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback) rolls back and cancels all changes in the current transaction.

Syntax:

```sql
ROLLBACK;
```

Transactions are also automatically rolled back if the client connection is aborted or closed.
## Autocommit

As required for MySQL compatibility, TiDB will by default _autocommit_ statements immediately following their execution.

For example:

```sql
mysql> CREATE TABLE t1 (
     id INT NOT NULL PRIMARY KEY auto_increment,
     pad1 VARCHAR(100)
    );
Query OK, 0 rows affected (0.09 sec)

mysql> SELECT @@autocommit;
+--------------+
| @@autocommit |
+--------------+
| 1            |
+--------------+
1 row in set (0.00 sec)

mysql> INSERT INTO t1 VALUES (1, 'test');
Query OK, 1 row affected (0.02 sec)

mysql> ROLLBACK;
Query OK, 0 rows affected (0.01 sec)

mysql> SELECT * FROM t1;
+----+------+
| id | pad1 |
+----+------+
|  1 | test |
+----+------+
1 row in set (0.00 sec)
```

In the above example, the `ROLLBACK` statement has no effect. This is because the `INSERT` statement is executed in autocommit. That is, it was the equivalent of the following single-statement transaction:

```sql
START TRANSACTION;
INSERT INTO t1 VALUES (1, 'test');
COMMIT;
```

Autocommit will not apply if a transaction has been explicitly started. In the following example, the `ROLLBACK` statement successfully reverts the `INSERT` statement:

```sql
mysql> CREATE TABLE t2 (
     id INT NOT NULL PRIMARY KEY auto_increment,
     pad1 VARCHAR(100)
    );
Query OK, 0 rows affected (0.10 sec)

mysql> SELECT @@autocommit;
+--------------+
| @@autocommit |
+--------------+
| 1            |
+--------------+
1 row in set (0.00 sec)

mysql> START TRANSACTION;
Query OK, 0 rows affected (0.00 sec)

mysql> INSERT INTO t2 VALUES (1, 'test');
Query OK, 1 row affected (0.02 sec)

mysql> ROLLBACK;
Query OK, 0 rows affected (0.00 sec)

mysql> SELECT * FROM t2;
Empty set (0.00 sec)
```

The [`autocommit`](https://docs.pingcap.com/tidb/stable/system-variables#autocommit) system variable [can be changed](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-variable) on either a global or session basis.

For example:

```sql
SET autocommit = 0;
```

```sql
SET GLOBAL autocommit = 0;
```
## Explicit and implicit transaction

> **Note:**
>
> Some statements are committed implicitly. For example, executing `[BEGIN|START TRANSACTION]` implicitly commits the last transaction and starts a new transaction. This behavior is required for MySQL compatibility. Refer to [implicit commit](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html) for more details.

TiDB supports explicit transactions (use `[BEGIN|START TRANSACTION]` and `COMMIT` to define the start and end of the transaction) and implicit transactions (`SET autocommit = 1`).

If you set the value of `autocommit` to `1` and start a new transaction through the `[BEGIN|START TRANSACTION]` statement, the autocommit is disabled before `COMMIT` or `ROLLBACK` which makes the transaction becomes explicit.

For DDL statements, the transaction is committed automatically and does not support rollback. If you run the DDL statement while the current session is in the process of a transaction, the DDL statement is executed after the current transaction is committed.
## Lazy check of constraints

By default, optimistic transactions will not check the [primary key](https://docs.pingcap.com/tidb/stable/constraints#primary-key) or [unique constraints](https://docs.pingcap.com/tidb/stable/constraints#unique-key) when a DML statement is executed. These checks are instead performed on transaction `COMMIT`.

For example:

```sql
CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY);
INSERT INTO t1 VALUES (1);
BEGIN OPTIMISTIC;
INSERT INTO t1 VALUES (1); -- MySQL returns an error; TiDB returns success.
INSERT INTO t1 VALUES (2);
COMMIT; -- It is successfully committed in MySQL; TiDB returns an error and the transaction rolls back.
SELECT * FROM t1; -- MySQL returns 1 2; TiDB returns 1.
```

```sql
mysql> CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY);
Query OK, 0 rows affected (0.10 sec)

mysql> INSERT INTO t1 VALUES (1);
Query OK, 1 row affected (0.02 sec)

mysql> BEGIN OPTIMISTIC;
Query OK, 0 rows affected (0.00 sec)

mysql> INSERT INTO t1 VALUES (1); -- MySQL returns an error; TiDB returns success.
Query OK, 1 row affected (0.00 sec)

mysql> INSERT INTO t1 VALUES (2);
Query OK, 1 row affected (0.00 sec)

mysql> COMMIT; -- It is successfully committed in MySQL; TiDB returns an error and the transaction rolls back.
ERROR 1062 (23000): Duplicate entry '1' for key 't1.PRIMARY'
mysql> SELECT * FROM t1; -- MySQL returns 1 2; TiDB returns 1.
+----+
| id |
+----+
|  1 |
+----+
1 row in set (0.01 sec)
```

The lazy check optimization improves performance by batching constraint checks and reducing network communication. The behavior can be disabled by setting [`tidb_constraint_check_in_place=ON`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place).

> **Note:**
>
> + This optimization only applies to optimistic transactions.
> + This optimization does not take effect for `INSERT IGNORE` and `INSERT ON DUPLICATE KEY UPDATE`, but only for normal `INSERT` statements.
## Statement rollback

TiDB supports atomic rollback after statement execution failure. If a statement results in an error, the changes it made will not take effect. The transaction will remain open, and additional changes can be made before issuing a `COMMIT` or `ROLLBACK` statement.

```sql
CREATE TABLE test (id INT NOT NULL PRIMARY KEY);
BEGIN;
INSERT INTO test VALUES (1);
INSERT INTO tset VALUES (2);  -- Statement does not take effect because "test" is misspelled as "tset".
INSERT INTO test VALUES (1),(2);  -- Entire statement does not take effect because it violates a PRIMARY KEY constraint
INSERT INTO test VALUES (3);
COMMIT;
SELECT * FROM test;
```

```sql
mysql> CREATE TABLE test (id INT NOT NULL PRIMARY KEY);
Query OK, 0 rows affected (0.09 sec)

mysql> BEGIN;
Query OK, 0 rows affected (0.00 sec)

mysql> INSERT INTO test VALUES (1);
Query OK, 1 row affected (0.02 sec)

mysql> INSERT INTO tset VALUES (2);  -- Statement does not take effect because "test" is misspelled as "tset".
ERROR 1146 (42S02): Table 'test.tset' doesn't exist
mysql> INSERT INTO test VALUES (1),(2);  -- Entire statement does not take effect because it violates a PRIMARY KEY constraint
ERROR 1062 (23000): Duplicate entry '1' for key 'test.PRIMARY'
mysql> INSERT INTO test VALUES (3);
Query OK, 1 row affected (0.00 sec)

mysql> COMMIT;
Query OK, 0 rows affected (0.01 sec)

mysql> SELECT * FROM test;
+----+
| id |
+----+
|  1 |
|  3 |
+----+
2 rows in set (0.00 sec)
```

In the above example, the transaction remains open after the failed `INSERT` statements. The final insert statement is then successful and changes are committed.
