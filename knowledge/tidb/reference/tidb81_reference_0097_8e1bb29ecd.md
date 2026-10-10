# DELETE syntax, prerequisites, best practices, and usage example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-delete-data.md`
- Source Title: `Delete Data`
- Source Heading Path: `Delete Data | Delete Data > Before you start | Delete Data > SQL syntax | Delete Data > Best practices | Delete Data > Example`
- Source Line Ranges: `5-188`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `delete`, `sql-syntax`, `prerequisites`, `where-clause`, `truncate`, `bulk-delete`, `non-transactional-delete`, `examples`, `datetime`, `timestamp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0097_8e1bb29ecd`
- Source ID: `tidb-docs-8.1:develop/dev-guide-delete-data.md#delete-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7b428bfd65e3787bd309012d7edb47571f8603e314fa40b2a341b52cd573d250`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data#delete-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-delete-data.md

## Retrieval Guidance

- Use When: Use this chunk when you need the basic TiDB DELETE statement form, prerequisites, deletion best practices, or the ratings time-range example with DATETIME and TIMESTAMP notes.
- Retrieval Keywords: DELETE FROM {table} WHERE {filter}, DELETE syntax, WHERE clause, TRUNCATE, bulk-delete, Non-Transactional bulk-delete, ratings, rated_at, SELECT COUNT(*), DELETE FROM `ratings` WHERE `rated_at` >= "2022-04-15 00:00:00" AND `rated_at` <= "2022-04-15 00:15:00", txn-total-size-limit, DATETIME, TIMESTAMP, time zone, year 2038 problem
- Follow-up Guidance: If the delete affects more than 10,000 records, the source points to Bulk-Delete and Performance considerations for iterative deletion and related behavior.
- Classification Note: This is classified as reference because the content defines DELETE syntax, prerequisites, cautions such as using WHERE and TRUNCATE, and concrete SQL and language examples from the official documentation.

## Official Source Content

# Delete Data

This document describes how to use the [DELETE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete) SQL statement to delete the data in TiDB. If you need to periodically delete expired data, use the [time to live](https://docs.pingcap.com/tidb/stable/time-to-live) feature.
## Before you start

Before reading this document, you need to prepare the following:

- [Build a {{{ .starter }}} Cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud)
- Read [Schema Design Overview](https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview), [Create a Database](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-database), [Create a Table](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table), and [Create Secondary Indexes](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-secondary-indexes)
- [Insert Data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data)
## SQL syntax

The `DELETE` statement is generally in the following form:

```sql
DELETE FROM {table} WHERE {filter}
```

| Parameter Name | Description |
| :--------: | :------------: |
| `{table}`  |      Table name      |
| `{filter}` | Matching conditions of the filter|

This example only shows a simple use case of `DELETE`. For detailed information, see [DELETE syntax](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete).
## Best practices

The following are some best practices to follow when you delete data:

- Always specify the `WHERE` clause in the `DELETE` statement. If the `WHERE` clause is not specified, TiDB will delete **_ALL ROWS_** in the table.

- Use [bulk-delete](#bulk-delete) when you delete a large number of rows (for example, more than ten thousand), because TiDB limits the size of a single transaction ([txn-total-size-limit](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit), 100 MB by default).

- Use [bulk-delete](#bulk-delete) when you delete a large number of rows (for example, more than ten thousand), because TiDB limits the size of a single transaction to 100 MB by default.

- If you delete all the data in a table, do not use the `DELETE` statement. Instead, use the [`TRUNCATE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-truncate) statement.
- For performance considerations, see [Performance Considerations](#performance-considerations).
- In scenarios where large batches of data need to be deleted, [Non-Transactional bulk-delete](#non-transactional-bulk-delete) can significantly improve performance. However, this will lose the transactional of the deletion and therefore **CANNOT** be rolled back. Make sure that you select the correct operation.
## Example

Suppose you find an application error within a specific time period and you need to delete all the data for the [ratings](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#ratings-table) within this period, for example, from `2022-04-15 00:00:00` to `2022-04-15 00:15:00`. In this case, you can use the `SELECT` statement to check the number of records to be deleted.

```sql
SELECT COUNT(*) FROM `ratings` WHERE `rated_at` >= "2022-04-15 00:00:00" AND `rated_at` <= "2022-04-15 00:15:00";
```

If more than 10,000 records are returned, use [Bulk-Delete](#bulk-delete) to delete them.

If fewer than 10,000 records are returned, use the following example to delete them.

<div label="SQL" value="sql">

In SQL, the example is as follows:

```sql
DELETE FROM `ratings` WHERE `rated_at` >= "2022-04-15 00:00:00" AND `rated_at` <= "2022-04-15 00:15:00";
```

</div>

<div label="Java" value="java">

In Java, the example is as follows:

```java
// ds is an entity of com.mysql.cj.jdbc.MysqlDataSource

try (Connection connection = ds.getConnection()) {
    String sql = "DELETE FROM `bookshop`.`ratings` WHERE `rated_at` >= ? AND `rated_at` <= ?";
    PreparedStatement preparedStatement = connection.prepareStatement(sql);
    Calendar calendar = Calendar.getInstance();
    calendar.set(Calendar.MILLISECOND, 0);

    calendar.set(2022, Calendar.APRIL, 15, 0, 0, 0);
    preparedStatement.setTimestamp(1, new Timestamp(calendar.getTimeInMillis()));

    calendar.set(2022, Calendar.APRIL, 15, 0, 15, 0);
    preparedStatement.setTimestamp(2, new Timestamp(calendar.getTimeInMillis()));

    preparedStatement.executeUpdate();
} catch (SQLException e) {
    e.printStackTrace();
}
```

</div>

<div label="Golang" value="golang">

In Golang, the example is as follows:

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

    startTime := time.Date(2022, 04, 15, 0, 0, 0, 0, time.UTC)
    endTime := time.Date(2022, 04, 15, 0, 15, 0, 0, time.UTC)

    bulkUpdateSql := fmt.Sprintf("DELETE FROM `bookshop`.`ratings` WHERE `rated_at` >= ? AND `rated_at` <= ?")
    result, err := db.Exec(bulkUpdateSql, startTime, endTime)
    if err != nil {
        panic(err)
    }
    _, err = result.RowsAffected()
    if err != nil {
        panic(err)
    }
}
```

</div>

<div label="Python" value="python">

In Python, the example is as follows:

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
        delete_sql = "DELETE FROM `bookshop`.`ratings` WHERE `rated_at` >= %s AND `rated_at` <= %s"
        affect_rows = cursor.execute(delete_sql, (start_time, end_time))
        print(f'delete {affect_rows} data')
```

</div>

The `rated_at` field is of the `DATETIME` type in [Date and Time Types](https://docs.pingcap.com/tidb/stable/data-type-date-and-time). You can assume that it is stored as a literal quantity in TiDB, independent of the time zone. On the other hand, the `TIMESTAMP` type stores a timestamp and thus displays a different time string in a different [time zone](https://docs.pingcap.com/tidb/stable/configure-time-zone).

The `rated_at` field is of the `DATETIME` type in [Date and Time Types](https://docs.pingcap.com/tidb/stable/data-type-date-and-time). You can assume that it is stored as a literal quantity in TiDB, independent of the time zone. On the other hand, the `TIMESTAMP` type stores a timestamp and thus displays a different time string in a different time zone.

> **Note:**
>
> Like MySQL, the `TIMESTAMP` data type is affected by the [year 2038 problem](https://en.wikipedia.org/wiki/Year_2038_problem). It is recommended to use the `DATETIME` type if you store values larger than 2038.
