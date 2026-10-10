# SAVEPOINT syntax, examples, and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-savepoint.md`
- Source Title: `SAVEPOINT | TiDB SQL Statement Reference`
- Source Heading Path: `SAVEPOINT | SAVEPOINT > Synopsis | SAVEPOINT > Examples | SAVEPOINT > MySQL compatibility | SAVEPOINT > See also`
- Source Line Ranges: `5-165`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `savepoint`, `transactions`, `rollback`, `release-savepoint`, `pessimistic-transactions`, `mysql-compatibility`, `syntax`, `examples`, `errors`, `locks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0629_09a8de2918`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-savepoint.md#savepoint`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `db5d591e040475fa119b1259559a60fb4e0d9ddce0f05866a35d929204f3e027`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-savepoint#savepoint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-savepoint.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB SAVEPOINT syntax, SAVEPOINT and ROLLBACK TO SAVEPOINT behavior, RELEASE SAVEPOINT semantics, related errors, or MySQL compatibility differences.
- Retrieval Keywords: SAVEPOINT identifier, ROLLBACK TO [SAVEPOINT] identifier, RELEASE SAVEPOINT identifier, ROLLBACK TO SAVEPOINT, ERROR 1305 (42000): SAVEPOINT identifier does not exist, tidb_constraint_check_in_place_pessimistic, TiDB Binlog enabled, pessimistic transaction locks are not rolled back, ROLLBACK WORK TO SAVEPOINT, MySQL compatibility, SAVEPOINT sp1, RELEASE SAVEPOINT sp2
- Follow-up Guidance: See also COMMIT, ROLLBACK, START TRANSACTION, TiDB Optimistic Transaction Mode, and TiDB Pessimistic Transaction Mode.
- Classification Note: This is reference content because it defines the SAVEPOINT, ROLLBACK TO SAVEPOINT, and RELEASE SAVEPOINT syntax, warnings, examples, errors, and MySQL compatibility details for SQL transactions.

## Official Source Content

# SAVEPOINT

`SAVEPOINT` is a feature introduced in TiDB v6.2.0. The syntax is as follows:

```sql
SAVEPOINT identifier
ROLLBACK TO [SAVEPOINT] identifier
RELEASE SAVEPOINT identifier
```

> **Warning:**
>
> - You cannot use `SAVEPOINT` with TiDB Binlog enabled.
> - You cannot use `SAVEPOINT` in pessimistic transactions when [`tidb_constraint_check_in_place_pessimistic`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place_pessimistic-new-in-v630) is disabled.

- `SAVEPOINT` is used to set a savepoint of a specified name in the current transaction. If a savepoint with the same name already exists, it will be deleted and a new savepoint with the same name will be set.

- `ROLLBACK TO SAVEPOINT` rolls back a transaction to the savepoint of a specified name and does not terminate the transaction. Data changes made to the table data after the savepoint will be reverted in the rollback, and all savepoints after the savepoint are deleted. In a pessimistic transaction, the locks held by the transaction are not rolled back. Instead, the locks will be released when the transaction ends.

    If the savepoint specified in the `ROLLBACK TO SAVEPOINT` statement does not exist, the statement returns the following error:

    ```
    ERROR 1305 (42000): SAVEPOINT identifier does not exist
    ```

- `RELEASE SAVEPOINT` statement removes the named savepoint and **all savepoints** after this savepoint from the current transaction, without committing or rolling back the current transaction. If the savepoint of the specified name does not exist, the following error is returned:

    ```
    ERROR 1305 (42000): SAVEPOINT identifier does not exist
    ```

    After the transaction is committed or rolled back, all savepoints in the transaction will be deleted.
## Synopsis

```ebnf+diagram
SavepointStmt ::=
    "SAVEPOINT" Identifier

RollbackToStmt ::=
    "ROLLBACK" "TO" "SAVEPOINT"? Identifier

ReleaseSavepointStmt ::=
    "RELEASE" "SAVEPOINT" Identifier
```
## Examples

Create a table `t1`:

```sql
CREATE TABLE t1 (a INT NOT NULL PRIMARY KEY);
```

```sql
Query OK, 0 rows affected (0.12 sec)
```

Start the current transaction:

```sql
BEGIN;
```

```sql
Query OK, 0 rows affected (0.00 sec)
```

Insert data into the table and set a savepoint `sp1`:

```sql
INSERT INTO t1 VALUES (1);
```

```sql
Query OK, 1 row affected (0.00 sec)
```

```sql
SAVEPOINT sp1;
```

```sql
Query OK, 0 rows affected (0.01 sec)
```

Insert data into the table again and set a savepoint `sp2`:

```sql
INSERT INTO t1 VALUES (2);
```

```sql
Query OK, 1 row affected (0.00 sec)
```

```sql
SAVEPOINT sp2;
```

```sql
Query OK, 0 rows affected (0.01 sec)
```

Release the savepoint `sp2`:

```sql
RELEASE SAVEPOINT sp2;
```

```sql
Query OK, 0 rows affected (0.01 sec)
```

Roll back to the savepoint `sp1`:

```sql
ROLLBACK TO SAVEPOINT sp1;
```

```sql
Query OK, 0 rows affected (0.01 sec)
```

Commit the transaction and query the table. Only the data inserted before `sp1` is returned.

```sql
COMMIT;
```

```sql
Query OK, 0 rows affected (0.01 sec)
```

```sql
SELECT * FROM t1;
```

```sql
+---+
| a |
+---+
| 1 |
+---+
1 row in set
```
## MySQL compatibility

When `ROLLBACK TO SAVEPOINT` is used to roll back a transaction to a specified savepoint, MySQL releases the locks held only after the specified savepoint, while in TiDB pessimistic transaction, TiDB does not immediately release the locks held after the specified savepoint. Instead, TiDB releases all locks when the transaction is committed or rolled back.

TiDB does not support the MySQL syntax `ROLLBACK WORK TO SAVEPOINT ...`.
## See also

* [COMMIT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-commit)
* [ROLLBACK](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback)
* [START TRANSACTION](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-start-transaction)
* [TiDB Optimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/optimistic-transaction)
* [TiDB Pessimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction)
