# GORM connection and CRUD code snippets

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-golang-gorm.md`
- Source Title: `Connect to TiDB with GORM`
- Source Heading Path: `Connect to TiDB with GORM > Sample code snippets | Connect to TiDB with GORM > Sample code snippets > Connect to TiDB | Connect to TiDB with GORM > Sample code snippets > Insert data | Connect to TiDB with GORM > Sample code snippets > Query data | Connect to TiDB with GORM > Sample code snippets > Update data | Connect to TiDB with GORM > Sample code snippets > Delete data`
- Source Line Ranges: `180-238`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `code-snippets`, `gorm`, `dsn`, `connection`, `crud`, `insert`, `query`, `update`, `delete`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0136_cc524fc4cd`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-golang-gorm.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0c67e5669a5a4cdf884a1f48ae42dfbe944d1dced1565e5009cacb2f44c7ba14`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-golang-gorm#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-golang-gorm.md

## Retrieval Guidance

- Use When: Use this chunk when someone is looking for GORM code snippets to open a TiDB connection with a DSN and perform basic CRUD operations.
- Retrieval Keywords: Sample code snippets, createDB, gorm.Open, mysql.Open, dsn, charset=utf8mb4, tls=%s, logger.Default.LogMode(logger.Info), db.Create, db.Find, db.Save, db.Delete, Player, Insert data, Query data, Update data, Delete data, tidb-samples/tidb-golang-gorm-quickstart
- Follow-up Guidance: It also links to the full sample repository and to the TiDB developer guide pages for insert, query, update, and delete operations.
- Classification Note: This is classified as reference content because it provides example GORM connection and CRUD code patterns rather than environment setup or broader guidance.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-golang-gorm-quickstart](https://github.com/tidb-samples/tidb-golang-gorm-quickstart) repository.
### Connect to TiDB

```golang
func createDB() *gorm.DB {
    dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?charset=utf8mb4&tls=%s",
        ${tidb_user}, ${tidb_password}, ${tidb_host}, ${tidb_port}, ${tidb_db_name}, ${use_ssl})

    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
        Logger: logger.Default.LogMode(logger.Info),
    })
    if err != nil {
        panic(err)
    }

    return db
}
```

When using this function, you need to replace `${tidb_host}`, `${tidb_port}`, `${tidb_user}`, `${tidb_password}`, and `${tidb_db_name}` with the actual values of your TiDB cluster. {{{ .starter }}} requires a secure connection. Therefore, you need to set the value of `${use_ssl}` to `true`.
### Insert data

```golang
db.Create(&Player{ID: "id", Coins: 1, Goods: 1})
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

```golang
var queryPlayer Player
db.Find(&queryPlayer, "id = ?", "id")
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

```golang
db.Save(&Player{ID: "id", Coins: 100, Goods: 1})
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

```golang
db.Delete(&Player{ID: "id"})
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
