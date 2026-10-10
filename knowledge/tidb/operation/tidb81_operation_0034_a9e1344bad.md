# UNIQUE KEY in pessimistic transactions and deferred constraint checking

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/constraints.md`
- Source Title: `Constraints`
- Source Heading Path: `Constraints > UNIQUE KEY > Pessimistic transactions`
- Source Line Ranges: `231-345`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `unique-key`, `pessimistic-transactions`, `constraint-checking`, `deferred-check`, `write-conflict`, `duplicate-entry`, `transaction-rollback`, `lazy-uniqueness-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0034_a9e1344bad`
- Source ID: `tidb-docs-8.1:constraints.md#pessimistic-transactions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7fd6d49e6c64feb11a7c05cad4309067f2bb28f79d7b598b66981cf1c36c7a30`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/constraints#pessimistic-transactions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/constraints.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about UNIQUE KEY behavior in pessimistic transactions, especially deferred constraint checking with `tidb_constraint_check_in_place_pessimistic` and related `Duplicate entry`, `Write conflict`, or `LazyUniquenessCheckFailure` errors.
- Retrieval Keywords: tidb_constraint_check_in_place_pessimistic, BEGIN PESSIMISTIC, UNIQUE KEY, deferred unique constraint check, Duplicate entry, ERROR 1062 (23000), Write conflict, ERROR 9007 (HY000), LazyUniquenessCheck, Pessimistic lock not found, ERROR 8147 (23000), LazyUniquenessCheckFailure, SELECT * FROM users FOR UPDATE, COMMIT
- Follow-up Guidance: The content explains that with `tidb_constraint_check_in_place_pessimistic = OFF`, TiDB can defer unique index checks until a later lock or commit, and the current transaction is rolled back when `Duplicate entry`, `Write conflict`, or `8147: LazyUniquenessCheckFailure` occurs.
- Classification Note: This is classified as an operation topic because it describes runtime behavior and transaction error cases for pessimistic transactions under a specific system variable.

## Official Source Content

### Pessimistic transactions

In pessimistic transactions, by default, TiDB checks `UNIQUE` constraints when a SQL statement that requires inserting or updating unique indexes is executed.

```sql
DROP TABLE IF EXISTS users;
CREATE TABLE users (
 id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
 username VARCHAR(60) NOT NULL,
 UNIQUE KEY (username)
);
INSERT INTO users (username) VALUES ('dave'), ('sarah'), ('bill');

BEGIN PESSIMISTIC;
INSERT INTO users (username) VALUES ('jane'), ('chris'), ('bill');
```

```
ERROR 1062 (23000): Duplicate entry 'bill' for key 'users.username'
```

To achieve better performance of pessimistic transactions, you can set the [`tidb_constraint_check_in_place_pessimistic`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place_pessimistic-new-in-v630) variable to `OFF`, which allows TiDB to defer the unique constraint check of a unique index (to the next time when this index requires a lock or to the time when the transaction is committed) and skip the corresponding pessimistic lock. When using this variable, pay attention to the following:

- Due to the deferred unique constraint check, TiDB might read results that do not meet the unique constraints and return a `Duplicate entry` error when you commit a pessimistic transaction. When this error occurs, TiDB rolls back the current transaction.

    The following example skips the lock to `bill`, so TiDB might get results that do not satisfy the uniqueness constraints.

    ```sql
    SET tidb_constraint_check_in_place_pessimistic = OFF;
    BEGIN PESSIMISTIC;
    INSERT INTO users (username) VALUES ('jane'), ('chris'), ('bill'); -- Query OK, 3 rows affected
    SELECT * FROM users FOR UPDATE;
    ```

   As in the following example output, the query results of TiDB contain two `bills`, which does not satisfy the uniqueness constraints.

    ```sql
    +----+----------+
    | id | username |
    +----+----------+
    | 1  | dave     |
    | 2  | sarah    |
    | 3  | bill     |
    | 7  | jane     |
    | 8  | chris    |
    | 9  | bill     |
    +----+----------+
    ```

    At this time, if the transaction is committed, TiDB will perform a unique constraint check, report a `Duplicate entry` error, and roll back the transaction.

    ```sql
    COMMIT;
    ```

    ```
    ERROR 1062 (23000): Duplicate entry 'bill' for key 'users.username'
    ```

- When this variable is disabled, committing a pessimistic transaction that needs to write data might return a `Write conflict` error. When this error occurs, TiDB rolls back the current transaction.

    As in the following example, if two concurrent transactions need to insert data to the same table, skipping the pessimistic lock causes TiDB to return a `Write conflict` error when you commit a transaction. And the transaction will be rolled back.

    ```sql
    DROP TABLE IF EXISTS users;
    CREATE TABLE users (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(60) NOT NULL,
    UNIQUE KEY (username)
    );

    SET tidb_constraint_check_in_place_pessimistic = OFF;
    BEGIN PESSIMISTIC;
    INSERT INTO users (username) VALUES ('jane'), ('chris'), ('bill'); -- Query OK, 3 rows affected
    ```

    At the same time, another session inserts `bill` to the same table.

    ```sql
    INSERT INTO users (username) VALUES ('bill'); -- Query OK, 1 row affected
    ```

    Then, when you commit the transaction in the first session, TiDB reports a `Write conflict` error.

    ```sql
    COMMIT;
    ```

    ```
    ERROR 9007 (HY000): Write conflict, txnStartTS=435688780611190794, conflictStartTS=435688783311536129, conflictCommitTS=435688783311536130, key={tableID=74, indexID=1, indexValues={bill, }} primary={tableID=74, indexID=1, indexValues={bill, }}, reason=LazyUniquenessCheck [try again later]
    ```

- When this variable is disabled, if there is a write conflict among multiple pessimistic transactions, the pessimistic lock might be forced to roll back when other pessimistic transactions are committed, thus resulting in a `Pessimistic lock not found` error. When this error occurs, it means that deferring the unique constraint check of the pessimistic transaction is not suitable for your application scenario. In this case, consider adjusting the application logic to avoid the conflict or retrying the transaction after an error occurs.

- When this variable is disabled, executing a DML statement in a pessimistic transaction might return an error `8147: LazyUniquenessCheckFailure`.

    > **Note:**
    >
    > When the `8147` error occurs, TiDB rolls back the current transaction.

    As in the following example, at the execution of the `INSERT` statement, TiDB skips a lock. Then, at the execution of the `DELETE` statement, TiDB locks the unique index and checks the unique constraints, so you will see an error is reported at the `DELETE` statement.

    ```sql
    SET tidb_constraint_check_in_place_pessimistic = OFF;
    BEGIN PESSIMISTIC;
    INSERT INTO users (username) VALUES ('jane'), ('chris'), ('bill'); -- Query OK, 3 rows affected
    DELETE FROM users where username = 'bill';
    ```

    ```
    ERROR 8147 (23000): transaction aborted because lazy uniqueness check is enabled and an error occurred: [kv:1062]Duplicate entry 'bill' for key 'users.username'
    ```

- When this variable is disabled, the `1062 Duplicate entry` error might be not from the current SQL statement. Therefore, when a transaction operates on multiple tables that have indexes with the same name, you need to check the `1062` error message to find which index the error is actually from.
