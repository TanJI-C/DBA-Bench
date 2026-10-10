# Optimistic vs pessimistic transactions and pessimistic example setup

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-optimistic-and-pessimistic-transaction.md`
- Source Title: `Optimistic Transactions and Pessimistic Transactions`
- Source Heading Path: `Optimistic Transactions and Pessimistic Transactions | Optimistic Transactions and Pessimistic Transactions > Pessimistic transactions | Optimistic Transactions and Pessimistic Transactions > Pessimistic transactions > Write a pessimistic transaction example`
- Source Line Ranges: `5-189`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `transactions`, `optimistic-transactions`, `pessimistic-transactions`, `concurrency`, `locking`, `rollback`, `overselling`, `java`, `golang`, `python`, `jdbc`, `connection-pool`, `maven`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0112_3d1c3661f0`
- Source ID: `tidb-docs-8.1:develop/dev-guide-optimistic-and-pessimistic-transaction.md#optimistic-transactions-and-pessimistic-transactions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f6f66362a79c66f817b158e6fd21a33b2c3ba825db5a294b46337912d0824d40`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimistic-and-pessimistic-transaction#optimistic-transactions-and-pessimistic-transactions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-optimistic-and-pessimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when comparing optimistic transaction and pessimistic transaction behavior in TiDB or when looking for the setup details of a pessimistic transaction concurrency example for a book purchase scenario.
- Retrieval Keywords: optimistic transaction, pessimistic transaction, transaction conflict, rollback, lock the resources, high conflict rates, low conflict rates, overselling, bookshop, buying books, Write a pessimistic transaction example, @@tidb_txn_mode, set @@tidb_txn_mode=?, pessimistic, optimistic, sql.DB concurrency-safe, HikariCP, mysqlclient, pom.xml, mysql-connector-java, maven-assembly-plugin, com.pingcap.txn.TxnExample
- Follow-up Guidance: The source continues into the Java configuration and coding example for the pessimistic transaction scenario, including Maven dependencies and application setup.
- Classification Note: This chunk is classified as reference because it explains the characteristics of optimistic and pessimistic transactions and provides concrete identifiers and setup elements for a pessimistic transaction example.

## Official Source Content

# Optimistic Transactions and Pessimistic Transactions

The [optimistic transaction](https://docs.pingcap.com/tidb/stable/optimistic-transaction) model commits the transaction directly, and rolls back when there is a conflict. By contrast, the [pessimistic transaction](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) model tries to lock the resources that need to be modified before actually committing the transaction, and only starts committing after ensuring that the transaction can be successfully executed.

The optimistic transaction model is suitable for scenarios with low conflict rates, because the direct commit has a high probability of success. But once a transaction conflict occurs, the cost of rollback is relatively high.

The advantage of the pessimistic transaction model is that for scenarios with high conflict rates, the cost of locking ahead is less than the cost of rollback afterwards. Moreover, it can solve the problem that multiple concurrent transactions fail to commit due to conflicts. However, the pessimistic transaction model is not as efficient as the optimistic transaction model in scenarios with low conflict rates.

The pessimistic transaction model is more intuitive and easier to implement on the application side. The optimistic transaction model requires complex application-side retry mechanisms.

The following is an example of a [bookshop](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design). It uses an example of buying books to show the pros and cons of optimistic and pessimistic transactions. The process of buying books mainly consists of the following:

1. Update the stock quantity
2. Create an order
3. Make the payment

These operations must either all succeed or all fail. You must ensure that overselling does not happen in the case of concurrent transactions.
## Pessimistic transactions

The following code uses two threads to simulate the process that two users buy the same book in a pessimistic transaction mode. There are 10 books left in the bookstore. Bob buys 6 books, and Alice buys 4 books. They complete the orders at nearly the same time. As a result, all books in inventory are sold out.

<div label="Java" value="java">

Because you use multiple threads to simulate the situation that multiple users insert data simultaneously, you need to use a connection object with safe threads. Here use Java's popular connection pool [HikariCP](https://github.com/brettwooldridge/HikariCP) for demo.

</div>

<div label="Golang" value="golang">

`sql.DB` in Golang is concurrency-safe, so there is no need to import a third-party package.

To adapt TiDB transactions, write a toolkit [util](https://github.com/pingcap-inc/tidb-example-golang/tree/main/util) according to the following code:

```go
package util

import (
    "context"
    "database/sql"
)

type TiDBSqlTx struct {
    *sql.Tx
    conn        *sql.Conn
    pessimistic bool
}

func TiDBSqlBegin(db *sql.DB, pessimistic bool) (*TiDBSqlTx, error) {
    ctx := context.Background()
    conn, err := db.Conn(ctx)
    if err != nil {
        return nil, err
    }
    if pessimistic {
        _, err = conn.ExecContext(ctx, "set @@tidb_txn_mode=?", "pessimistic")
    } else {
        _, err = conn.ExecContext(ctx, "set @@tidb_txn_mode=?", "optimistic")
    }
    if err != nil {
        return nil, err
    }
    tx, err := conn.BeginTx(ctx, nil)
    if err != nil {
        return nil, err
    }
    return &TiDBSqlTx{
        conn:        conn,
        Tx:          tx,
        pessimistic: pessimistic,
    }, nil
}

func (tx *TiDBSqlTx) Commit() error {
    defer tx.conn.Close()
    return tx.Tx.Commit()
}

func (tx *TiDBSqlTx) Rollback() error {
    defer tx.conn.Close()
    return tx.Tx.Rollback()
}
```

</div>

<div label="Python" value="python">

To ensure thread safety, you can use the mysqlclient driver to open multiple connections that are not shared between threads.

</div>
### Write a pessimistic transaction example

<div label="Java" value="java">

**Configuration file**

If you use Maven to manage the package, in the `<dependencies>` node in `pom.xml`, add the following dependencies to import `HikariCP`, and set the packaging target, and the main class of the JAR package startup. The following is an example of `pom.xml`.

```xml
<?xml version="1.0" encoding="UTF-8"?>

<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.pingcap</groupId>
  <artifactId>plain-java-txn</artifactId>
  <version>0.0.1</version>

  <name>plain-java-jdbc</name>

  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
  </properties>

  <dependencies>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
      <scope>test</scope>
    </dependency>

    <!-- https://mvnrepository.com/artifact/mysql/mysql-connector-java -->
    <dependency>
      <groupId>mysql</groupId>
      <artifactId>mysql-connector-java</artifactId>
      <version>8.0.28</version>
    </dependency>

    <dependency>
      <groupId>com.zaxxer</groupId>
      <artifactId>HikariCP</artifactId>
      <version>5.0.1</version>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-assembly-plugin</artifactId>
        <version>3.3.0</version>
        <configuration>
          <descriptorRefs>
            <descriptorRef>jar-with-dependencies</descriptorRef>
          </descriptorRefs>
          <archive>
            <manifest>
              <mainClass>com.pingcap.txn.TxnExample</mainClass>
            </manifest>
          </archive>

        </configuration>
        <executions>
          <execution>
            <id>make-assembly</id>
            <phase>package</phase>
            <goals>
              <goal>single</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>

</project>
```

**Coding**

Then write the code:
