# Go-MySQL-Driver connection and CRUD code snippets

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-golang-sql-driver.md`
- Source Title: `Connect to TiDB with Go-MySQL-Driver`
- Source Heading Path: `Connect to TiDB with Go-MySQL-Driver > Sample code snippets | Connect to TiDB with Go-MySQL-Driver > Sample code snippets > Connect to TiDB | Connect to TiDB with Go-MySQL-Driver > Sample code snippets > Insert data | Connect to TiDB with Go-MySQL-Driver > Sample code snippets > Query data | Connect to TiDB with Go-MySQL-Driver > Sample code snippets > Update data | Connect to TiDB with Go-MySQL-Driver > Sample code snippets > Delete data | Connect to TiDB with Go-MySQL-Driver > Useful notes | Connect to TiDB with Go-MySQL-Driver > Useful notes > Using driver or ORM framework? | Connect to TiDB with Go-MySQL-Driver > Next steps`
- Source Line Ranges: `180-294`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `golang`, `mysql-driver`, `dsn`, `database-sql`, `crud`, `insert`, `query`, `update`, `delete`, `orm`, `developer-guide`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0138_67ef2fb175`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-golang-sql-driver.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `100fa85554c8c3a1f6023ffa391f61e8896c7148481a129e7ce72ae71ced4fa3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-golang-sql-driver#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-golang-sql-driver.md

## Retrieval Guidance

- Use When: Use this chunk when someone wants Go-MySQL-Driver `database/sql` code examples for connecting to TiDB with a DSN and performing basic CRUD on the `player` table.
- Retrieval Keywords: openDB, sql.Open, dsn, charset=utf8mb4, tls=%s, ${tidb_host}, ${tidb_port}, ${tidb_user}, ${tidb_password}, ${tidb_db_name}, ${use_ssl}, INSERT INTO player (id, coins, goods) VALUES (?, ?, ?), SELECT id, coins, goods FROM player WHERE id = ?, defer rows.Close(), rows.Scan, UPDATE player set goods = goods + ?, coins = coins + ? WHERE id = ?, DELETE FROM player WHERE id=?, Go-MySQL-Driver, GORM, ORM framework
- Follow-up Guidance: The source also notes the tradeoff between using the driver directly and using an ORM framework such as GORM, and lists next-step links for Go-MySQL-Driver documentation and the TiDB developer guide.
- Classification Note: This is classified as reference because it provides reusable connection and CRUD code snippets, exact SQL statements, and notes about direct driver usage versus an ORM framework.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-golang-sql-driver-quickstart](https://github.com/tidb-samples/tidb-golang-sql-driver-quickstart) repository.
### Connect to TiDB

```golang
func openDB(driverName string, runnable func(db *sql.DB)) {
    dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?charset=utf8mb4&tls=%s",
        ${tidb_user}, ${tidb_password}, ${tidb_host}, ${tidb_port}, ${tidb_db_name}, ${use_ssl})
    db, err := sql.Open(driverName, dsn)
    if err != nil {
        panic(err)
    }
    defer db.Close()

    runnable(db)
}
```

When using this function, you need to replace `${tidb_host}`, `${tidb_port}`, `${tidb_user}`, `${tidb_password}`, and `${tidb_db_name}` with the actual values of your TiDB cluster. {{{ .starter }}} and {{{ .essential }}} require a secure connection. Therefore, you need to set the value of `${use_ssl}` to `true`.
### Insert data

```golang
openDB("mysql", func(db *sql.DB) {
    insertSQL = "INSERT INTO player (id, coins, goods) VALUES (?, ?, ?)"
    _, err := db.Exec(insertSQL, "id", 1, 1)

    if err != nil {
        panic(err)
    }
})
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

```golang
openDB("mysql", func(db *sql.DB) {
    selectSQL = "SELECT id, coins, goods FROM player WHERE id = ?"
    rows, err := db.Query(selectSQL, "id")
    if err != nil {
        panic(err)
    }

    // This line is extremely important!
    defer rows.Close()

    id, coins, goods := "", 0, 0
    if rows.Next() {
        err = rows.Scan(&id, &coins, &goods)
        if err == nil {
            fmt.Printf("player id: %s, coins: %d, goods: %d\n", id, coins, goods)
        }
    }
})
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

```golang
openDB("mysql", func(db *sql.DB) {
    updateSQL = "UPDATE player set goods = goods + ?, coins = coins + ? WHERE id = ?"
    _, err := db.Exec(updateSQL, 1, -1, "id")

    if err != nil {
        panic(err)
    }
})
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

```golang
openDB("mysql", func(db *sql.DB) {
    deleteSQL = "DELETE FROM player WHERE id=?"
    _, err := db.Exec(deleteSQL, "id")

    if err != nil {
        panic(err)
    }
})
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
## Useful notes
### Using driver or ORM framework?

The Golang driver provides low-level access to the database, but it requires the developers to:

- Manually establish and release database connections.
- Manually manage database transactions.
- Manually map data rows to data objects.

Unless you need to write complex SQL statements, it is recommended to use [ORM](https://en.wikipedia.org/w/index.php?title=Object-relational_mapping) framework for development, such as [GORM](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-golang-gorm). It can help you:

- Reduce [boilerplate code](https://en.wikipedia.org/wiki/Boilerplate_code) for managing connections and transactions.
- Manipulate data with data objects instead of a number of SQL statements.
## Next steps

- Learn more usage of Go-MySQL-Driver from [the documentation of Go-MySQL-Driver](https://github.com/go-sql-driver/mysql/blob/master/README.md).
- Learn the best practices for TiDB application development with the chapters in the [Developer guide](https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview), such as [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data), [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data), [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data), [Single table reading](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table), [Transactions](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview), and [SQL performance optimization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview).
- Learn through the professional [TiDB developer courses](https://www.pingcap.com/education/) and earn [TiDB certifications](https://www.pingcap.com/education/certification/) after passing the exam.
