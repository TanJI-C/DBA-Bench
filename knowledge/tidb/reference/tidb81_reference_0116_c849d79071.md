# Pessimistic overselling prevention example and transition to optimistic transactions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-optimistic-and-pessimistic-transaction.md`
- Source Title: `Optimistic Transactions and Pessimistic Transactions`
- Source Heading Path: `Optimistic Transactions and Pessimistic Transactions > Pessimistic transactions > An example that prevents overselling | Optimistic Transactions and Pessimistic Transactions > Optimistic transactions`
- Source Line Ranges: `919-1002`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `transactions`, `pessimistic-transactions`, `optimistic-transactions`, `overselling`, `row-locking`, `rollback`, `inventory`, `concurrency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0116_c849d79071`
- Source ID: `tidb-docs-8.1:develop/dev-guide-optimistic-and-pessimistic-transaction.md#an-example-that-prevents-overselling`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fa89eeef78d67dffd392c02548c12e1dcab9f584bffc6e43329951a4b66cbbb1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimistic-and-pessimistic-transaction#an-example-that-prevents-overselling
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-optimistic-and-pessimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an example of preventing overselling with pessimistic transactions and row locking, including how `SELECT * FROM books WHERE id = 1 FOR UPDATE` leads one transaction to roll back when stock is insufficient.
- Retrieval Keywords: BEGIN PESSIMISTIC, SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE, UPDATE `books` SET `stock` = `stock` - 7 WHERE `id` = 1 AND `stock` - 7 >= 0, affected_rows is 0, ROLLBACK, overselling, pessimistic transactions, optimistic transactions, books, orders, users, inventory, row locking
- Follow-up Guidance: The chunk then transitions to the optimistic transaction section, where two threads simulate two users buying the same book with 10 books left and Bob buying 6 while Alice buys 4.
- Classification Note: This is classified as reference content because it provides a concrete SQL transaction example, observed results in the `books`, `orders`, and `users` tables, and the stated outcome for pessimistic versus optimistic transaction behavior.

## Official Source Content

### An example that prevents overselling

The task in this example is more challenging. Suppose there are 10 books left in stock. Bob buys 7 books, Alice buys 4 books, and they place orders almost at the same time. What will happen? You can reuse the code from the previous example to solve this challenge, and change Bob's purchase quantity from 6 to 7.

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
./bin/txn -a 4 -b 7
```

</div>

<div label="Python" value="python">

```shell
OPTIMISTIC=False ALICE=4 BOB=7 python3 txn_example.py
```

</div>

```sql
/* txn 1 */ BEGIN PESSIMISTIC
    /* txn 2 */ BEGIN PESSIMISTIC
    /* txn 2 */ SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE
    /* txn 2 */ UPDATE `books` SET `stock` = `stock` - 4 WHERE `id` = 1 AND `stock` - 4 >= 0
    /* txn 2 */ INSERT INTO `orders` (`id`, `book_id`, `user_id`, `quality`) values (1001, 1, 1, 4)
    /* txn 2 */ UPDATE `users` SET `balance` = `balance` - 400.0 WHERE `id` = 2
    /* txn 2 */ COMMIT
/* txn 1 */ SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE
/* txn 1 */ UPDATE `books` SET `stock` = `stock` - 7 WHERE `id` = 1 AND `stock` - 7 >= 0
/* txn 1 */ ROLLBACK
```

Since `txn 2` preemptively gets the lock resource and updates the stock, the return value of `affected_rows` in `txn 1` is 0, and it enters the `rollback` process.

Let's check the order creation, user balance deduction, and book inventory deduction. Alice successfully ordered 4 books, Bob failed to order 7 books, and the remaining 6 books are in stock as expected.

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
| 1001 |       1 |       1 |       4 | 2022-04-19 11:03:03 |
+------+---------+---------+---------+---------------------+
1 row in set (0.00 sec)

mysql> SELECT * FROM users;
+----+----------+----------+
| id | balance  | nickname |
+----+----------+----------+
|  1 | 10000.00 | Bob      |
|  2 |  9600.00 | Alice    |
+----+----------+----------+
2 rows in set (0.01 sec)
```
## Optimistic transactions

The following code uses two threads to simulate the process that two users buy the same book in an optimistic transaction, just like the pessimistic transaction example. There are 10 books left in inventory. Bob buys 6 and Alice buys 4. They complete the order at about the same time. In the end, no books are left in inventory.
