# Bulk-delete example in Java, Golang, and Python

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-delete-data.md`
- Source Title: `Delete Data`
- Source Heading Path: `Delete Data > Bulk-delete > Bulk-delete example`
- Source Line Ranges: `225-378`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `delete`, `bulk-delete`, `batch-processing`, `examples`, `java`, `golang`, `python`, `limit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0054_e446da0fc7`
- Source ID: `tidb-docs-8.1:develop/dev-guide-delete-data.md#bulk-delete-example`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0d5a64aef8a6c7c440ea87afb23fa1b5971550d1d2a8080faf571ece4a0938cb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data#bulk-delete-example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-delete-data.md

## Retrieval Guidance

- Use When: Use this chunk when looking for language-specific examples of deleting many rows in batches from the `bookshop`.`ratings` table within a `rated_at` time range using `DELETE ... LIMIT 1000`.
- Retrieval Keywords: Bulk-delete example, DELETE FROM `bookshop`.`ratings`, `rated_at` >= ? AND `rated_at` <= ? LIMIT 1000, 2022-04-15 00:00:00, 2022-04-15 00:15:00, Java batchDelete, Golang deleteBatch, Python MySQLdb bulk delete, delete up to 1000 rows each iteration
- Follow-up Guidance: Each iteration deletes up to 1000 rows from `2022-04-15 00:00:00` to `2022-04-15 00:15:00`.
- Classification Note: This is classified as an operation chunk because it provides executable Java, Golang, and Python bulk-delete examples using SQL `DELETE` statements against TiDB.

## Official Source Content

### Bulk-delete example

Suppose you find an application error within a specific time period. You need to delete all the data for the [rating](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#ratings-table) within this period, for example, from `2022-04-15 00:00:00` to `2022-04-15 00:15:00`, and more than 10,000 records are written in 15 minutes. You can perform as follows.

<div label="Java" value="java">

In Java, the bulk-delete example is as follows:

```java
package com.pingcap.bulkDelete;

import com.mysql.cj.jdbc.MysqlDataSource;

import java.sql.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

public class BatchDeleteExample
{
    public static void main(String[] args) throws InterruptedException {
        // Configure the example database connection.

        // Create a mysql data source instance.
        MysqlDataSource mysqlDataSource = new MysqlDataSource();

        // Set server name, port, database name, username and password.
        mysqlDataSource.setServerName("localhost");
        mysqlDataSource.setPortNumber(4000);
        mysqlDataSource.setDatabaseName("bookshop");
        mysqlDataSource.setUser("root");
        mysqlDataSource.setPassword("");

        while (true) {
            batchDelete(mysqlDataSource);
            TimeUnit.SECONDS.sleep(1);
        }
    }

    public static void batchDelete (MysqlDataSource ds) {
        try (Connection connection = ds.getConnection()) {
            String sql = "DELETE FROM `bookshop`.`ratings` WHERE `rated_at` >= ? AND `rated_at` <= ? LIMIT 1000";
            PreparedStatement preparedStatement = connection.prepareStatement(sql);
            Calendar calendar = Calendar.getInstance();
            calendar.set(Calendar.MILLISECOND, 0);

            calendar.set(2022, Calendar.APRIL, 15, 0, 0, 0);
            preparedStatement.setTimestamp(1, new Timestamp(calendar.getTimeInMillis()));

            calendar.set(2022, Calendar.APRIL, 15, 0, 15, 0);
            preparedStatement.setTimestamp(2, new Timestamp(calendar.getTimeInMillis()));

            int count = preparedStatement.executeUpdate();
            System.out.println("delete " + count + " data");
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

In each iteration, `DELETE` deletes up to 1000 rows from `2022-04-15 00:00:00` to `2022-04-15 00:15:00`.

</div>

<div label="Golang" value="golang">

In Golang, the bulk-delete example is as follows:

```go
package main

import (
    "database/sql"
    "fmt"
    "time"

    _ "github.com/go-sql-driver/mysql"
)

func main() {
    db, err := sql.Open("mysql", "root:@tcp(127.0.0.1:4000)/bookshop")
    if err != nil {
        panic(err)
    }
    defer db.Close()

    affectedRows := int64(-1)
    startTime := time.Date(2022, 04, 15, 0, 0, 0, 0, time.UTC)
    endTime := time.Date(2022, 04, 15, 0, 15, 0, 0, time.UTC)

    for affectedRows != 0 {
        affectedRows, err = deleteBatch(db, startTime, endTime)
        if err != nil {
            panic(err)
        }
    }
}

// deleteBatch delete at most 1000 lines per batch
func deleteBatch(db *sql.DB, startTime, endTime time.Time) (int64, error) {
    bulkUpdateSql := fmt.Sprintf("DELETE FROM `bookshop`.`ratings` WHERE `rated_at` >= ? AND `rated_at` <= ? LIMIT 1000")
    result, err := db.Exec(bulkUpdateSql, startTime, endTime)
    if err != nil {
        return -1, err
    }
    affectedRows, err := result.RowsAffected()
    if err != nil {
        return -1, err
    }

    fmt.Printf("delete %d data\n", affectedRows)
    return affectedRows, nil
}
```

In each iteration, `DELETE` deletes up to 1000 rows from `2022-04-15 00:00:00` to `2022-04-15 00:15:00`.

</div>

<div label="Python" value="python">

In Python, the bulk-delete example is as follows:

```python
import MySQLdb
import datetime
import time
connection = MySQLdb.connect(
    host="127.0.0.1",
    port=4000,
    user="root",
    password="",
    database="bookshop",
    autocommit=True
)
with connection:
    with connection.cursor() as cursor:
        start_time = datetime.datetime(2022, 4, 15)
        end_time = datetime.datetime(2022, 4, 15, 0, 15)
        affect_rows = -1
        while affect_rows != 0:
            delete_sql = "DELETE FROM `bookshop`.`ratings` WHERE `rated_at` >= %s AND  `rated_at` <= %s LIMIT 1000"
            affect_rows = cursor.execute(delete_sql, (start_time, end_time))
            print(f'delete {affect_rows} data')
            time.sleep(1)
```

In each iteration, `DELETE` deletes up to 1000 rows from `2022-04-15 00:00:00` to `2022-04-15 00:15:00`.

</div>
