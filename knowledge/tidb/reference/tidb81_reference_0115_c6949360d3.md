# Pessimistic transaction example code and non-overselling run

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-optimistic-and-pessimistic-transaction.md`
- Source Title: `Optimistic Transactions and Pessimistic Transactions`
- Source Heading Path: `Optimistic Transactions and Pessimistic Transactions > Pessimistic transactions > Write a pessimistic transaction example | Optimistic Transactions and Pessimistic Transactions > Pessimistic transactions > An example that does not involve overselling`
- Source Line Ranges: `657-918`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `transactions`, `pessimistic-transactions`, `optimistic-transactions`, `sql-logs`, `concurrency`, `inventory`, `orders`, `verification`, `python`, `java`, `golang`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0115_c6949360d3`
- Source ID: `tidb-docs-8.1:develop/dev-guide-optimistic-and-pessimistic-transaction.md#write-a-pessimistic-transaction-example`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `faf07c493c470023db7e02d66e84cab3575f42de4252c95d2620e974fbd04372`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimistic-and-pessimistic-transaction#write-a-pessimistic-transaction-example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-optimistic-and-pessimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when looking for a concrete pessimistic transaction inventory-order example with concurrent buyers, SQL logs, and final verification queries showing a run that does not involve overselling.
- Retrieval Keywords: BEGIN PESSIMISTIC, SELECT `price` FROM books WHERE id = %s FOR UPDATE, SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE, update `books` set stock = stock - %s where id = %s and stock - %s >= 0, INSERT INTO `orders` (`id`, `book_id`, `user_id`, `quality`), UPDATE `users` SET `balance` = `balance` - 400.0 WHERE `id` = 2, OPTIMISTIC=False ALICE=4 BOB=6 python3 txn_example.py, mvn clean package, go build -o bin/txn, non-overselling, SQL logs, SELECT * FROM `books`, SELECT * FROM orders, SELECT * FROM users, buy_pessimistic, buy_optimistic, REPEATABLE_ERROR_CODE_SET, 9007, 8028, 8002, 8022
- Follow-up Guidance: The chunk also includes the sample program run commands for Java, Golang, and Python, plus final SELECT queries against `books`, `orders`, and `users` to verify the results.
- Classification Note: This is classified as reference because the content mainly provides runnable example code, exact SQL statements, error codes, command lines, and expected query results for pessimistic and optimistic transaction behavior.

## Official Source Content

```python
import time

import MySQLdb
import os
import datetime
from threading import Thread

REPEATABLE_ERROR_CODE_SET = {
    9007,  # Transactions in TiKV encounter write conflicts.
    8028,  # table schema changes
    8002,  # "SELECT FOR UPDATE" commit conflict
    8022   # The transaction commit fails and has been rolled back
}


def create_connection():
    return MySQLdb.connect(
        host="127.0.0.1",
        port=4000,
        user="root",
        password="",
        database="bookshop",
        autocommit=False
    )


def prepare_data() -> None:
    connection = create_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO `books` (`id`, `title`, `type`, `published_at`, `price`, `stock`) "
                           "values (%s, %s, %s, %s, %s, %s)",
                           (1, "Designing Data-Intensive Application", "Science & Technology",
                            datetime.datetime(2018, 9, 1), 100, 10))

            cursor.executemany("INSERT INTO `users` (`id`, `nickname`, `balance`) VALUES (%s, %s, %s)",
                               [(1, "Bob", 10000), (2, "ALICE", 10000)])
            connection.commit()


def buy_optimistic(thread_id: int, order_id: int, book_id: int, user_id: int, amount: int,
                   optimistic_retry_times: int = 5) -> None:
    connection = create_connection()

    txn_log_header = f"/* txn {thread_id} */"
    if thread_id != 1:
        txn_log_header = "\t" + txn_log_header

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("BEGIN OPTIMISTIC")
            print(f'{txn_log_header} BEGIN OPTIMISTIC')
            time.sleep(1)

            try:
                # read the price of book
                select_book_for_update = "SELECT `price`, `stock` FROM books WHERE id = %s FOR UPDATE"
                cursor.execute(select_book_for_update, (book_id,))
                book = cursor.fetchone()
                if book is None:
                    raise Exception("book_id not exist")
                price, stock = book
                print(f'{txn_log_header} {select_book_for_update} successful')

                if stock < amount:
                    raise Exception("book not enough, rollback")

                # update book
                update_stock = "update `books` set stock = stock - %s where id = %s and stock - %s >= 0"
                rows_affected = cursor.execute(update_stock, (amount, book_id, amount))
                print(f'{txn_log_header} {update_stock} successful')

                if rows_affected == 0:
                    raise Exception("stock not enough, rollback")

                # insert order
                insert_order = "insert into `orders` (`id`, `book_id`, `user_id`, `quality`) values (%s, %s, %s, %s)"
                cursor.execute(insert_order, (order_id, book_id, user_id, amount))
                print(f'{txn_log_header} {insert_order} successful')

                # update user
                update_user = "update `users` set `balance` = `balance` - %s where id = %s"
                cursor.execute(update_user, (amount * price, user_id))
                print(f'{txn_log_header} {update_user} successful')

            except Exception as err:
                connection.rollback()

                print(f'something went wrong: {err}')
            else:
                # important here! you need deal the Exception from the TiDB
                try:
                    connection.commit()
                except MySQLdb.MySQLError as db_err:
                    code, desc = db_err.args
                    if code in REPEATABLE_ERROR_CODE_SET and optimistic_retry_times > 0:
                        print(f'retry, rest {optimistic_retry_times - 1} times, for {code} {desc}')
                        buy_optimistic(thread_id, order_id, book_id, user_id, amount, optimistic_retry_times - 1)


def buy_pessimistic(thread_id: int, order_id: int, book_id: int, user_id: int, amount: int) -> None:
    connection = create_connection()

    txn_log_header = f"/* txn {thread_id} */"
    if thread_id != 1:
        txn_log_header = "\t" + txn_log_header

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("BEGIN PESSIMISTIC")
            print(f'{txn_log_header} BEGIN PESSIMISTIC')
            time.sleep(1)

            try:
                # read the price of book
                select_book_for_update = "SELECT `price` FROM books WHERE id = %s FOR UPDATE"
                cursor.execute(select_book_for_update, (book_id,))
                book = cursor.fetchone()
                if book is None:
                    raise Exception("book_id not exist")
                price = book[0]
                print(f'{txn_log_header} {select_book_for_update} successful')

                # update book
                update_stock = "update `books` set stock = stock - %s where id = %s and stock - %s >= 0"
                rows_affected = cursor.execute(update_stock, (amount, book_id, amount))
                print(f'{txn_log_header} {update_stock} successful')

                if rows_affected == 0:
                    raise Exception("stock not enough, rollback")

                # insert order
                insert_order = "insert into `orders` (`id`, `book_id`, `user_id`, `quality`) values (%s, %s, %s, %s)"
                cursor.execute(insert_order, (order_id, book_id, user_id, amount))
                print(f'{txn_log_header} {insert_order} successful')

                # update user
                update_user = "update `users` set `balance` = `balance` - %s where id = %s"
                cursor.execute(update_user, (amount * price, user_id))
                print(f'{txn_log_header} {update_user} successful')

            except Exception as err:
                connection.rollback()
                print(f'something went wrong: {err}')
            else:
                connection.commit()


optimistic = os.environ.get('OPTIMISTIC')
alice = os.environ.get('ALICE')
bob = os.environ.get('BOB')

if not (optimistic and alice and bob):
    raise Exception("please use \"OPTIMISTIC=<is_optimistic> ALICE=<alice_num> "
                    "BOB=<bob_num> python3 txn_example.py\" to start this script")

prepare_data()

if bool(optimistic) is True:
    buy_func = buy_optimistic
else:
    buy_func = buy_pessimistic

bob_thread = Thread(target=buy_func, kwargs={
    "thread_id": 1, "order_id": 1000, "book_id": 1, "user_id": 1, "amount": int(bob)})
alice_thread = Thread(target=buy_func, kwargs={
    "thread_id": 2, "order_id": 1001, "book_id": 1, "user_id": 2, "amount": int(alice)})

bob_thread.start()
alice_thread.start()
bob_thread.join(timeout=10)
alice_thread.join(timeout=10)
```

The Python example already includes optimistic transactions.

</div>
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
./bin/txn -a 4 -b 6
```

</div>

<div label="Python" value="python">

```shell
OPTIMISTIC=False ALICE=4 BOB=6 python3 txn_example.py
```

</div>

SQL logs:

```sql
/* txn 1 */ BEGIN PESSIMISTIC
    /* txn 2 */ BEGIN PESSIMISTIC
    /* txn 2 */ SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE
    /* txn 2 */ UPDATE `books` SET `stock` = `stock` - 4 WHERE `id` = 1 AND `stock` - 4 >= 0
    /* txn 2 */ INSERT INTO `orders` (`id`, `book_id`, `user_id`, `quality`) VALUES (1001, 1, 1, 4)
    /* txn 2 */ UPDATE `users` SET `balance` = `balance` - 400.0 WHERE `id` = 2
    /* txn 2 */ COMMIT
/* txn 1 */ SELECT * FROM `books` WHERE `id` = 1 FOR UPDATE
/* txn 1 */ UPDATE `books` SET `stock` = `stock` - 6 WHERE `id` = 1 AND `stock` - 6 >= 0
/* txn 1 */ INSERT INTO `orders` (`id`, `book_id`, `user_id`, `quality`) VALUES (1000, 1, 1, 6)
/* txn 1 */ UPDATE `users` SET `balance` = `balance` - 600.0 WHERE `id` = 1
/* txn 1 */ COMMIT
```

Finally, check that the order is created, the user balance is deducted, and the book inventory is deducted as expected.

```sql
mysql> SELECT * FROM `books`;
+----+--------------------------------------+----------------------+---------------------+-------+--------+
| id | title                                | type                 | published_at        | stock | price  |
+----+--------------------------------------+----------------------+---------------------+-------+--------+
|  1 | Designing Data-Intensive Application | Science & Technology | 2018-09-01 00:00:00 |     0 | 100.00 |
+----+--------------------------------------+----------------------+---------------------+-------+--------+
1 row in set (0.00 sec)

mysql> SELECT * FROM orders;
+------+---------+---------+---------+---------------------+
| id   | book_id | user_id | quality | ordered_at          |
+------+---------+---------+---------+---------------------+
| 1000 |       1 |       1 |       6 | 2022-04-19 10:58:12 |
| 1001 |       1 |       1 |       4 | 2022-04-19 10:58:11 |
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
