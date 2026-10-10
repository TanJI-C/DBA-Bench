# Optimistic transaction example code and language notes

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-optimistic-and-pessimistic-transaction.md`
- Source Title: `Optimistic Transactions and Pessimistic Transactions`
- Source Heading Path: `Optimistic Transactions and Pessimistic Transactions > Optimistic transactions > Write an optimistic transaction example`
- Source Line Ranges: `1003-1196`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `optimistic-transactions`, `java`, `golang`, `python`, `jdbc`, `retry`, `write-conflict`, `select-for-update`, `commit`, `rollback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0117_6c7c51718b`
- Source ID: `tidb-docs-8.1:develop/dev-guide-optimistic-and-pessimistic-transaction.md#write-an-optimistic-transaction-example`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `eabf073adb68cac3cff810626d4f39eb1864b597cdbefec58303b0f85e08cfc1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimistic-and-pessimistic-transaction#write-an-optimistic-transaction-example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-optimistic-and-pessimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an official optimistic transaction example with Java JDBC code, retry handling for commit conflicts, or language notes about Golang and Python support.
- Retrieval Keywords: begin optimistic, SELECT * FROM books where id = ? for update, commit, rollback, HikariDataSource, jdbc:mysql://localhost:4000/bookshop?useServerPrepStmts=true&cachePrepStmts=true, write conflicts, error code 9007, error code 8028, error code 8002, error code 8022, com.pingcap.txn.optimistic.TxnExample, pom.xml mainClass, Golang example already supports optimistic transactions, Python example already supports optimistic transactions
- Follow-up Guidance: The source also states that the Golang and Python examples in the pessimistic transaction section already support optimistic transactions and can be used directly without changes.
- Classification Note: This is reference content because it provides example code, exact SQL statements, error codes, and a mainClass identifier for optimistic transaction usage.

## Official Source Content

### Write an optimistic transaction example

<div label="Java" value="java">

**Coding**

```java
package com.pingcap.txn.optimistic;

import com.zaxxer.hikari.HikariDataSource;

import java.math.BigDecimal;
import java.sql.*;
import java.util.Arrays;
import java.util.concurrent.*;

public class TxnExample {
    public static void main(String[] args) throws SQLException, InterruptedException {
        System.out.println(Arrays.toString(args));
        int aliceQuantity = 0;
        int bobQuantity = 0;

        for (String arg: args) {
            if (arg.startsWith("ALICE_NUM")) {
                aliceQuantity = Integer.parseInt(arg.replace("ALICE_NUM=", ""));
            }

            if (arg.startsWith("BOB_NUM")) {
                bobQuantity = Integer.parseInt(arg.replace("BOB_NUM=", ""));
            }
        }

        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:mysql://localhost:4000/bookshop?useServerPrepStmts=true&cachePrepStmts=true");
        ds.setUsername("root");
        ds.setPassword("");

        // prepare data
        Connection connection = ds.getConnection();
        createBook(connection, 1L, "Designing Data-Intensive Application", "Science & Technology",
                Timestamp.valueOf("2018-09-01 00:00:00"), new BigDecimal(100), 10);
        createUser(connection, 1L, "Bob", new BigDecimal(10000));
        createUser(connection, 2L, "Alice", new BigDecimal(10000));

        CountDownLatch countDownLatch = new CountDownLatch(2);
        ExecutorService threadPool = Executors.newFixedThreadPool(2);

        final int finalBobQuantity = bobQuantity;
        threadPool.execute(() -> {
            buy(ds, 1, 1000L, 1L, 1L, finalBobQuantity, 5);
            countDownLatch.countDown();
        });
        final int finalAliceQuantity = aliceQuantity;
        threadPool.execute(() -> {
            buy(ds, 2, 1001L, 1L, 2L, finalAliceQuantity, 5);
            countDownLatch.countDown();
        });

        countDownLatch.await(5, TimeUnit.SECONDS);
    }

    public static void createUser(Connection connection, Long id, String nickname, BigDecimal balance) throws SQLException  {
        PreparedStatement insert = connection.prepareStatement(
                "INSERT INTO `users` (`id`, `nickname`, `balance`) VALUES (?, ?, ?)");
        insert.setLong(1, id);
        insert.setString(2, nickname);
        insert.setBigDecimal(3, balance);
        insert.executeUpdate();
    }

    public static void createBook(Connection connection, Long id, String title, String type, Timestamp publishedAt, BigDecimal price, Integer stock) throws SQLException {
        PreparedStatement insert = connection.prepareStatement(
                "INSERT INTO `books` (`id`, `title`, `type`, `published_at`, `price`, `stock`) values (?, ?, ?, ?, ?, ?)");
        insert.setLong(1, id);
        insert.setString(2, title);
        insert.setString(3, type);
        insert.setTimestamp(4, publishedAt);
        insert.setBigDecimal(5, price);
        insert.setInt(6, stock);

        insert.executeUpdate();
    }

    public static void buy (HikariDataSource ds, Integer threadID, Long orderID, Long bookID,
                            Long userID, Integer quantity, Integer retryTimes) {
        String txnComment = "/* txn " + threadID + " */ ";

        try (Connection connection = ds.getConnection()) {
            try {

                connection.setAutoCommit(false);
                connection.createStatement().executeUpdate(txnComment + "begin optimistic");

                // waiting for other thread ran the 'begin optimistic' statement
                TimeUnit.SECONDS.sleep(1);

                BigDecimal price = null;

                // read price of book
                PreparedStatement selectBook = connection.prepareStatement(txnComment + "SELECT * FROM books where id = ? for update");
                selectBook.setLong(1, bookID);
                ResultSet res = selectBook.executeQuery();
                if (!res.next()) {
                    throw new RuntimeException("book not exist");
                } else {
                    price = res.getBigDecimal("price");
                    int stock = res.getInt("stock");
                    if (stock < quantity) {
                        throw new RuntimeException("book not enough");
                    }
                }

                // update book
                String updateBookSQL = "update `books` set stock = stock - ? where id = ? and stock - ? >= 0";
                PreparedStatement updateBook = connection.prepareStatement(txnComment + updateBookSQL);
                updateBook.setInt(1, quantity);
                updateBook.setLong(2, bookID);
                updateBook.setInt(3, quantity);
                updateBook.executeUpdate();

                // insert order
                String insertOrderSQL = "insert into `orders` (`id`, `book_id`, `user_id`, `quality`) values (?, ?, ?, ?)";
                PreparedStatement insertOrder = connection.prepareStatement(txnComment + insertOrderSQL);
                insertOrder.setLong(1, orderID);
                insertOrder.setLong(2, bookID);
                insertOrder.setLong(3, userID);
                insertOrder.setInt(4, quantity);
                insertOrder.executeUpdate();

                // update user
                String updateUserSQL = "update `users` set `balance` = `balance` - ? where id = ?";
                PreparedStatement updateUser = connection.prepareStatement(txnComment + updateUserSQL);
                updateUser.setBigDecimal(1, price.multiply(new BigDecimal(quantity)));
                updateUser.setLong(2, userID);
                updateUser.executeUpdate();

                connection.createStatement().executeUpdate(txnComment + "commit");
            } catch (Exception e) {
                connection.createStatement().executeUpdate(txnComment + "rollback");
                System.out.println("error occurred: " + e.getMessage());

                if (e instanceof SQLException sqlException) {
                    switch (sqlException.getErrorCode()) {
                        // You can get all error codes at https://docs.pingcap.com/tidb/stable/error-codes
                        case 9007: // Transactions in TiKV encounter write conflicts.
                        case 8028: // table schema changes
                        case 8002: // "SELECT FOR UPDATE" commit conflict
                        case 8022: // The transaction commit fails and has been rolled back
                            if (retryTimes != 0) {
                                System.out.println("rest " + retryTimes + " times. retry for " + e.getMessage());
                                buy(ds, threadID, orderID, bookID, userID, quantity, retryTimes - 1);
                            }
                    }
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

**Configuration changes**

Change the startup class in `pom.xml`:

```xml
<mainClass>com.pingcap.txn.TxnExample</mainClass>
```

Change it to the following to point to the optimistic transaction example.

```xml
<mainClass>com.pingcap.txn.optimistic.TxnExample</mainClass>
```

</div>

<div label="Golang" value="golang">
The Golang example in the [Write a pessimistic transaction example](#write-a-pessimistic-transaction-example) section already supports optimistic transactions and can be used directly without changes.

</div>

<div label="Python" value="python">

The Python example in the [Write a pessimistic transaction example](#write-a-pessimistic-transaction-example) section already supports optimistic transactions and can be used directly without changes.

</div>
