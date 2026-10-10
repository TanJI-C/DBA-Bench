# Bulk-update example in Golang with schema flag and batched UPDATE loop

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-update-data.md`
- Source Title: `Update Data`
- Source Heading Path: `Update Data > Bulk-update > Example`
- Source Line Ranges: `184-288`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `bulk-update`, `update-loop`, `batching`, `primary-key-ordering`, `ddl`, `boolean-flag`, `idempotency`, `resource-throttling`, `golang`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0006_26628e08fc`
- Source ID: `tidb-docs-8.1:develop/dev-guide-update-data.md#example`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `12113575842c6db6b3d020226b7eaab939a63dd7359f83ac0ef03052459de158`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data#example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-update-data.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the Golang bulk-update example that adds a BOOL ten_point flag, selects up to 1000 primary keys from bookshop.ratings in primary-key order, and updates score = score * 2 in batches.
- Retrieval Keywords: Golang bulk-update example, ALTER TABLE `bookshop`.`ratings` ADD COLUMN `ten_point` BOOL NOT NULL DEFAULT FALSE, SELECT `book_id`, `user_id` FROM `bookshop`.`ratings` WHERE `ten_point` != true ORDER BY `book_id`, `user_id` LIMIT 1000, UPDATE `bookshop`.`ratings` SET `ten_point` = true, `score` = `score` * 2, placeHolder, time.Sleep(time.Second), ADD COLUMN, online DDL, bookshop ratings ten_point
- Follow-up Guidance: The chunk notes that TiDB executes DDL change operations online and points to ADD COLUMN for more information.
- Classification Note: This is classified as data_pipeline for developer-facing SQL workflow content because it shows a batched application pattern for updating table data with ordering, idempotency marking, and throttling.

## Official Source Content

### Example

Suppose that you have had a lot of book ratings from users on your `bookshop` website over the past year, but the original design of a 5-point scale has resulted in a lack of differentiation in book ratings. Most books are rated `3`. You decide to switch from a 5-point scale to a 10-point scale to differentiate ratings.

You need to multiply by `2` the data in the `ratings` table from the previous 5-point scale, and add a new column to the ratings table to indicate whether the rows have been updated. Using this column, you can filter out rows that have been updated in `SELECT`, which will prevent the script from crashing and updating the rows multiple times, resulting in unreasonable data.

For example, you create a column named `ten_point` with the data type [BOOL](https://docs.pingcap.com/tidb/stable/data-type-numeric#boolean-type) as an identifier of whether it is a 10-point scale:

```sql
ALTER TABLE `bookshop`.`ratings` ADD COLUMN `ten_point` BOOL NOT NULL DEFAULT FALSE;
```

> **Note:**
>
> This bulk-update application uses the **DDL** statements to make schema changes to the data tables. All DDL change operations for TiDB are executed online. For more information, see [ADD COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-column).

<div label="Golang" value="golang">

In Golang, a bulk-update application is similar to the following:

```go
package main

import (
    "database/sql"
    "fmt"
    _ "github.com/go-sql-driver/mysql"
    "strings"
    "time"
)

func main() {
    db, err := sql.Open("mysql", "root:@tcp(127.0.0.1:4000)/bookshop")
    if err != nil {
        panic(err)
    }
    defer db.Close()

    bookID, userID := updateBatch(db, true, 0, 0)
    fmt.Println("first time batch update success")
    for {
        time.Sleep(time.Second)
        bookID, userID = updateBatch(db, false, bookID, userID)
        fmt.Printf("batch update success, [bookID] %d, [userID] %d\n", bookID, userID)
    }
}

// updateBatch select at most 1000 lines data to update score
func updateBatch(db *sql.DB, firstTime bool, lastBookID, lastUserID int64) (bookID, userID int64) {
    // select at most 1000 primary keys in five-point scale data
    var err error
    var rows *sql.Rows

    if firstTime {
        rows, err = db.Query("SELECT `book_id`, `user_id` FROM `bookshop`.`ratings` " +
            "WHERE `ten_point` != true ORDER BY `book_id`, `user_id` LIMIT 1000")
    } else {
        rows, err = db.Query("SELECT `book_id`, `user_id` FROM `bookshop`.`ratings` "+
            "WHERE `ten_point` != true AND `book_id` > ? AND `user_id` > ? "+
            "ORDER BY `book_id`, `user_id` LIMIT 1000", lastBookID, lastUserID)
    }

    if err != nil || rows == nil {
        panic(fmt.Errorf("error occurred or rows nil: %+v", err))
    }

    // joint all id with a list
    var idList []interface{}
    for rows.Next() {
        var tempBookID, tempUserID int64
        if err := rows.Scan(&tempBookID, &tempUserID); err != nil {
            panic(err)
        }
        idList = append(idList, tempBookID, tempUserID)
        bookID, userID = tempBookID, tempUserID
    }

    bulkUpdateSql := fmt.Sprintf("UPDATE `bookshop`.`ratings` SET `ten_point` = true, "+
        "`score` = `score` * 2 WHERE (`book_id`, `user_id`) IN (%s)", placeHolder(len(idList)))
    db.Exec(bulkUpdateSql, idList...)

    return bookID, userID
}

// placeHolder format SQL place holder
func placeHolder(n int) string {
    holderList := make([]string, n/2, n/2)
    for i := range holderList {
        holderList[i] = "(?,?)"
    }
    return strings.Join(holderList, ",")
}
```

In each iteration, `SELECT` queries in order of the primary key. It selects primary key values for up to `1000` rows that have not been updated to the 10-point scale (`ten_point` is `false`). Each `SELECT` statement selects primary keys larger than the largest of the previous `SELECT` results to prevent duplication. Then, it uses bulk-update, multiples its `score` column by `2`, and sets `ten_point` to `true`. The purpose of updating `ten_point` is to prevent the update application from repeatedly updating the same row in case of restart after crashing, which can cause data corruption. `time.Sleep(time.Second)` in each loop makes the update application pause for 1 second to prevent the update application from consuming too many hardware resources.

</div>

<div label="Java (JDBC)" value="jdbc">

In Java (JDBC), a bulk-update application might be similar to the following:

**Code:**
