# Insert rows with SQL and application drivers

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-insert-data.md`
- Source Title: `Insert Data`
- Source Heading Path: `Insert Data > Insert rows`
- Source Line Ranges: `19-230`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `shared`
- Topic Tags: `insert`, `multi-row-insert`, `batch-insert`, `jdbc`, `golang`, `python`, `prepared-statements`, `connection-strings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0003_970ff22e09`
- Source ID: `tidb-docs-8.1:develop/dev-guide-insert-data.md#insert-rows`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0cbb6bb3f189ec06b2958b08c8a9706b71859f5231dd5ec3088e1e84613cd973`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data#insert-rows
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-insert-data.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to insert multiple rows into a TiDB table with SQL, JDBC, Golang, or Python, or asks about batch insert performance settings for MySQL JDBC Driver.
- Retrieval Keywords: INSERT INTO `player` (`id`, `coins`, `goods`) VALUES, multi-line insertion statement, single-line insertion statements, PreparedStatement, executeBatch, useServerPrepStmts, cachePrepStmts, prepStmtCacheSqlLimit, prepStmtCacheSize, rewriteBatchedStatements, allowMultiQueries, useConfigs=maxPerformance, jdbc:mysql://127.0.0.1:4000/test, buildBulkInsertSQL, executemany, insert multiple rows
- Follow-up Guidance: The chunk also links to complete examples for JDBC, Hibernate, Spring Boot, Go-MySQL-Driver, GORM, PyMySQL, mysqlclient, MySQL Connector/Python, SQLAlchemy, and peewee.
- Classification Note: This is data_pipeline content because it demonstrates row insertion and batching patterns across SQL and application drivers, including connection and prepared statement settings.

## Official Source Content

## Insert rows

There are two ways to insert multiple rows of data. For example, if you need to insert **3** players' data.

- A **multi-line insertion statement**:

    ```sql
    INSERT INTO `player` (`id`, `coins`, `goods`) VALUES (1, 1000, 1), (2, 230, 2), (3, 300, 5);
    ```

- Multiple **single-line insertion statements**:

    ```sql
    INSERT INTO `player` (`id`, `coins`, `goods`) VALUES (1, 1000, 1);
    INSERT INTO `player` (`id`, `coins`, `goods`) VALUES (2, 230, 2);
    INSERT INTO `player` (`id`, `coins`, `goods`) VALUES (3, 300, 5);
    ```

Generally the `multi-line insertion statement` runs faster than the multiple `single-line insertion statements`.

<div label="SQL">

```sql
CREATE TABLE `player` (`id` INT, `coins` INT, `goods` INT);
INSERT INTO `player` (`id`, `coins`, `goods`) VALUES (1, 1000, 1), (2, 230, 2);
```

For more information on how to use this SQL, see [Connecting to a TiDB Cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud#step-2-connect-to-a-cluster) and follow the steps to enter the SQL statement after connecting to a TiDB cluster using a client.

</div>

<div label="Java">

```java
// ds is an entity of com.mysql.cj.jdbc.MysqlDataSource
try (Connection connection = ds.getConnection()) {
    connection.setAutoCommit(false);

    PreparedStatement pstmt = connection.prepareStatement("INSERT INTO player (id, coins, goods) VALUES (?, ?, ?)"))

    // first player
    pstmt.setInt(1, 1);
    pstmt.setInt(2, 1000);
    pstmt.setInt(3, 1);
    pstmt.addBatch();

    // second player
    pstmt.setInt(1, 2);
    pstmt.setInt(2, 230);
    pstmt.setInt(3, 2);
    pstmt.addBatch();

    pstmt.executeBatch();
    connection.commit();
} catch (SQLException e) {
    e.printStackTrace();
}
```

Due to the default MySQL JDBC Driver settings, you need to change some parameters to get better bulk insert performance.

|            Parameter            |                 Means                  |   Recommended Scenario   | Recommended Configuration|
| :------------------------: | :-----------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------: | :----------------------: |
|    `useServerPrepStmts`    |    Whether to use the server side to enable prepared statements    |  When you need to use a prepared statement more than once                                                             |          `true`          |
|      `cachePrepStmts`      |       Whether the client caches prepared statements        |                                                           `useServerPrepStmts=true`                                                             |          `true`          |
|  `prepStmtCacheSqlLimit`   |  Maximum size of a prepared statement (256 characters by default)  | When the prepared statement is greater than 256 characters | Configured according to the actual size of the prepared statement |
|    `prepStmtCacheSize`     | Maximum number of prepared statement caches (25 by default) | When the number of prepared statements is greater than 25  | Configured according to the actual number of prepared statements |
| `rewriteBatchedStatements` |          Whether to rewrite **Batched** statements          | When batch operations are required |          `true`          |
|    `allowMultiQueries`     |             Start batch operations              | Because a [client bug](https://bugs.mysql.com/bug.php?id=96623) requires this to be set when `rewriteBatchedStatements = true` and `useServerPrepStmts = true` |          `true`          |

MySQL JDBC Driver also provides an integrated configuration: `useConfigs`. When it is configured with `maxPerformance`, it is equivalent to configuring a set of configurations. Taking `mysql:mysql-connector-java:8.0.28` as an example, `useConfigs=maxPerformance` contains:

```properties
cachePrepStmts=true
cacheCallableStmts=true
cacheServerConfiguration=true
useLocalSessionState=true
elideSetAutoCommits=true
alwaysSendSetIsolation=false
enableQueryTimeouts=false
connectionAttributes=none
useInformationSchema=true
```

You can check `mysql-connector-java-{version}.jar!/com/mysql/cj/configurations/maxPerformance.properties` to get the configurations contained in `useConfigs=maxPerformance` for the corresponding version of MySQL JDBC Driver.

The following is a typical scenario of JDBC connection string configurations. In this example, Host: `127.0.0.1`, Port: `4000`, User name: `root`, Password: null, Default database: `test`:

```
jdbc:mysql://127.0.0.1:4000/test?user=root&useConfigs=maxPerformance&useServerPrepStmts=true&prepStmtCacheSqlLimit=2048&prepStmtCacheSize=256&rewriteBatchedStatements=true&allowMultiQueries=true
```

For complete examples in Java, see:

- [Connect to TiDB with JDBC](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-jdbc)
- [Connect to TiDB with Hibernate](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-hibernate)
- [Connect to TiDB with Spring Boot](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-spring-boot)

</div>

<div label="Golang">

```go
package main

import (
    "database/sql"
    "strings"

    _ "github.com/go-sql-driver/mysql"
)

type Player struct {
    ID    string
    Coins int
    Goods int
}

func bulkInsertPlayers(db *sql.DB, players []Player, batchSize int) error {
    tx, err := db.Begin()
    if err != nil {
        return err
    }

    stmt, err := tx.Prepare(buildBulkInsertSQL(batchSize))
    if err != nil {
        return err
    }

    defer stmt.Close()

    for len(players) > batchSize {
        if _, err := stmt.Exec(playerToArgs(players[:batchSize])...); err != nil {
            tx.Rollback()
            return err
        }

        players = players[batchSize:]
    }

    if len(players) != 0 {
        if _, err := tx.Exec(buildBulkInsertSQL(len(players)), playerToArgs(players)...); err != nil {
            tx.Rollback()
            return err
        }
    }

    if err := tx.Commit(); err != nil {
        tx.Rollback()
        return err
    }

    return nil
}

func playerToArgs(players []Player) []interface{} {
    var args []interface{}
    for _, player := range players {
        args = append(args, player.ID, player.Coins, player.Goods)
    }
    return args
}

func buildBulkInsertSQL(amount int) string {
    return "INSERT INTO player (id, coins, goods) VALUES (?, ?, ?)" + strings.Repeat(",(?,?,?)", amount-1)
}
```

For complete examples in Golang, see:

- [Connect to TiDB with Go-MySQL-Driver](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-golang-sql-driver)
- [Connect to TiDB with GORM](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-golang-gorm)

</div>

<div label="Python">

```python
import MySQLdb
connection = MySQLdb.connect(
    host="127.0.0.1",
    port=4000,
    user="root",
    password="",
    database="bookshop",
    autocommit=True
)

with get_connection(autocommit=True) as connection:
    with connection.cursor() as cur:
        player_list = random_player(1919)
        for idx in range(0, len(player_list), 114):
            cur.executemany("INSERT INTO player (id, coins, goods) VALUES (%s, %s, %s)", player_list[idx:idx + 114])
```

For complete examples in Python, see:
- [Connect to TiDB with PyMySQL](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-pymysql)
- [Connect to TiDB with mysqlclient](https://github.com/tidb-samples/tidb-python-mysqlclient-quickstart)
- [Connect to TiDB with MySQL Connector/Python](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-mysql-connector)
- [Connect to TiDB with SQLAlchemy](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-sqlalchemy)
- [Connect to TiDB with peewee](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-peewee)

</div>
