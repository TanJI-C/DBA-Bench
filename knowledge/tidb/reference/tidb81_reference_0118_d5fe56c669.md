# Optimistic transaction concurrency examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-optimistic-and-pessimistic-transaction.md`
- Source Title: `Optimistic Transactions and Pessimistic Transactions`
- Source Heading Path: `Optimistic Transactions and Pessimistic Transactions > Optimistic transactions > An example that does not involve overselling | Optimistic Transactions and Pessimistic Transactions > Optimistic transactions > An example that prevents overselling`
- Source Line Ranges: `1197-1369`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `optimistic-transactions`, `write-conflict`, `retry`, `overselling`, `inventory`, `commit`, `rollback`, `sql-example`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0118_d5fe56c669`
- Source ID: `tidb-docs-8.1:develop/dev-guide-optimistic-and-pessimistic-transaction.md#an-example-that-does-not-involve-overselling`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dc949e1e31caa3de23d42f72c6dfa72439d434d6e613b79b3efbcd9f7db68db1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimistic-and-pessimistic-transaction#an-example-that-does-not-involve-overselling
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-optimistic-and-pessimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when looking for official optimistic transaction concurrency examples with inventory updates, `9007 Write conflict`, application-side retry, and overselling prevention behavior.
- Retrieval Keywords: BEGIN OPTIMISTIC, 9007 Write conflict, retry 1 times, COMMIT, ROLLBACK, SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE, UPDATE `books` SET `stock` = `stock` - 6 WHERE `id` = 1 AND `stock` - 6 >= 0, UPDATE `books` SET `stock` = `stock` - 7 WHERE `id` = 1 AND `stock` - 7 >= 0, INSERT INTO `orders`, UPDATE `users` SET `balance`, affected_rows, out of stock, optimistic transaction mode, write conflict, prevents overselling
- Follow-up Guidance: The content also states that in optimistic transaction mode you should judge success by whether the final `COMMIT` returns an exception, and that write conflicts can be safely retried on the application side.
- Classification Note: This is a SQL reference example because the official content shows concrete optimistic transaction SQL sequences, conflict logs, retry behavior, and final query results for both normal completion and overselling prevention.

## Official Source Content

### An example that does not involve overselling

Run the sample program:

<div label="Java" value="java">

```shell
mvn clean package
java -jar target/plain-java-txn-0.0.1-jar-with-dependencies.jar ALICE_NUM=4 BOB_NUM=6
```

</div>

<div label="Golang" value="golang">

```shell
go build -o bin/txn
./bin/txn -a 4 -b 6 -o true
```

</div>

<div label="Python" value="python">

```shell
OPTIMISTIC=True ALICE=4 BOB=6 python3 txn_example.py
```

</div>

SQL statement execution process:

```sql
    /* txn 2 */ BEGIN OPTIMISTIC
/* txn 1 */ BEGIN OPTIMISTIC
    /* txn 2 */ SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE
    /* txn 2 */ UPDATE `books` SET `stock` = `stock` - 4 WHERE `id` = 1 AND `stock` - 4 >= 0
    /* txn 2 */ INSERT INTO `orders` (`id`, `book_id`, `user_id`, `quality`) VALUES (1001, 1, 1, 4)
    /* txn 2 */ UPDATE `users` SET `balance` = `balance` - 400.0 WHERE `id` = 2
    /* txn 2 */ COMMIT
/* txn 1 */ SELECT * FROM `books` WHERE `id` = 1 for UPDATE
/* txn 1 */ UPDATE `books` SET `stock` = `stock` - 6 WHERE `id` = 1 AND `stock` - 6 >= 0
/* txn 1 */ INSERT INTO `orders` (`id`, `book_id`, `user_id`, `quality`) VALUES (1000, 1, 1, 6)
/* txn 1 */ UPDATE `users` SET `balance` = `balance` - 600.0 WHERE `id` = 1
retry 1 times for 9007 Write conflict, txnStartTS=432618733006225412, conflictStartTS=432618733006225411, conflictCommitTS=432618733006225414, key={tableID=126, handle=1} primary={tableID=114, indexID=1, indexValues={1, 1000, }} [try again later]
/* txn 1 */ BEGIN OPTIMISTIC
/* txn 1 */ SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE
/* txn 1 */ UPDATE `books` SET `stock` = `stock` - 6 WHERE `id` = 1 AND `stock` - 6 >= 0
/* txn 1 */ INSERT INTO `orders` (`id`, `book_id`, `user_id`, `quality`) VALUES (1000, 1, 1, 6)
/* txn 1 */ UPDATE `users` SET `balance` = `balance` - 600.0 WHERE `id` = 1
/* txn 1 */ COMMIT
```

In the optimistic transaction mode, because the intermediate state is not necessarily correct, it is not possible to judge whether a statement is successfully executed through `affected_rows` as in the pessimistic transaction mode. You need to regard the transaction as a whole, and judge whether the current transaction has a write conflict by checking whether the final `COMMIT` statement returns an exception.

As you can see from the above SQL log, because two transactions are executed concurrently and the same record is modified, a `9007 Write conflict` exception is thrown after `txn 1` COMMIT. For write conflicts in the optimistic transaction mode, you can safely retry on the application side. After one retry, the data is committed successfully. The final execution result is as expected:

```sql
mysql> SELECT * FROM books;
+----+--------------------------------------+----------------------+---------------------+-------+--------+
| id | title                                | type                 | published_at        | stock | price  |
+----+--------------------------------------+----------------------+---------------------+-------+--------+
|  1 | Designing Data-Intensive Application | Science & Technology | 2018-09-01 00:00:00 |     0 | 100.00 |
+----+--------------------------------------+----------------------+---------------------+-------+--------+
1 row in set (0.01 sec)

mysql> SELECT * FROM orders;
+------+---------+---------+---------+---------------------+
| id   | book_id | user_id | quality | ordered_at          |
+------+---------+---------+---------+---------------------+
| 1000 |       1 |       1 |       6 | 2022-04-19 03:18:19 |
| 1001 |       1 |       1 |       4 | 2022-04-19 03:18:17 |
+------+---------+---------+---------+---------------------+
2 rows in set (0.01 sec)

mysql> SELECT * FROM users;
+----+---------+----------+
| id | balance | nickname |
+----+---------+----------+
|  1 | 9400.00 | Bob      |
|  2 | 9600.00 | Alice    |
+----+---------+----------+
2 rows in set (0.00 sec)
```
### An example that prevents overselling

This section describes an optimistic transaction example that prevents overselling. Suppose there are 10 books left in inventory. Bob buys 7 books,and Alice buys 4 books. They place orders almost at the same time. What will happen? You can reuse the code from the optimistic transaction example to address this requirement. Change Bob's purchases from 6 to 7.

Run the sample program:

<div label="Java" value="java">

```shell
mvn clean package
java -jar target/plain-java-txn-0.0.1-jar-with-dependencies.jar ALICE_NUM=4 BOB_NUM=7
```

</div>

<div label="Golang" value="golang">

```shell
go build -o bin/txn
./bin/txn -a 4 -b 7 -o true
```

</div>

<div label="Python" value="python">

```shell
OPTIMISTIC=True ALICE=4 BOB=7 python3 txn_example.py
```

</div>

```sql
/* txn 1 */ BEGIN OPTIMISTIC
    /* txn 2 */ BEGIN OPTIMISTIC
    /* txn 2 */ SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE
    /* txn 2 */ UPDATE `books` SET `stock` = `stock` - 4 WHERE `id` = 1 AND `stock` - 4 >= 0
    /* txn 2 */ INSERT INTO `orders` (`id`, `book_id`, `user_id`, `quality`) VALUES (1001, 1, 1, 4)
    /* txn 2 */ UPDATE `users` SET `balance` = `balance` - 400.0 WHERE `id` = 2
    /* txn 2 */ COMMIT
/* txn 1 */ SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE
/* txn 1 */ UPDATE `books` SET `stock` = `stock` - 7 WHERE `id` = 1 AND `stock` - 7 >= 0
/* txn 1 */ INSERT INTO `orders` (`id`, `book_id`, `user_id`, `quality`) VALUES (1000, 1, 1, 7)
/* txn 1 */ UPDATE `users` SET `balance` = `balance` - 700.0 WHERE `id` = 1
retry 1 times for 9007 Write conflict, txnStartTS=432619094333980675, conflictStartTS=432619094333980676, conflictCommitTS=432619094333980678, key={tableID=126, handle=1} primary={tableID=114, indexID=1, indexValues={1, 1000, }} [try again later]
/* txn 1 */ BEGIN OPTIMISTIC
/* txn 1 */ SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE
Fail -> out of stock
/* txn 1 */ ROLLBACK
```

You can see from the above SQL log that `txn 1` is retried on the application side due to a write conflict in the first execution. By comparing the latest snapshots, you can find that the stock is running out. The application side throws `out of stock`, and ends abnormally.

```sql
mysql> SELECT * FROM books;
+----+--------------------------------------+----------------------+---------------------+-------+--------+
| id | title                                | type                 | published_at        | stock | price  |
+----+--------------------------------------+----------------------+---------------------+-------+--------+
|  1 | Designing Data-Intensive Application | Science & Technology | 2018-09-01 00:00:00 |     6 | 100.00 |
+----+--------------------------------------+----------------------+---------------------+-------+--------+
1 row in set (0.00 sec)

mysql> SELECT * FROM orders;
+------+---------+---------+---------+---------------------+
| id   | book_id | user_id | quality | ordered_at          |
+------+---------+---------+---------+---------------------+
| 1001 |       1 |       1 |       4 | 2022-04-19 03:41:16 |
+------+---------+---------+---------+---------------------+
1 row in set (0.00 sec)

mysql> SELECT * FROM users;
+----+----------+----------+
| id | balance  | nickname |
+----+----------+----------+
|  1 | 10000.00 | Bob      |
|  2 |  9600.00 | Alice    |
+----+----------+----------+
2 rows in set (0.00 sec)
```
