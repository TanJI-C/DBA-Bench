# Insert or update with duplicate key handling

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-update-data.md`
- Source Title: `Update Data`
- Source Heading Path: `Update Data > Use `INSERT ON DUPLICATE KEY UPDATE` | Update Data > Use `INSERT ON DUPLICATE KEY UPDATE` > `INSERT ON DUPLICATE KEY UPDATE` SQL Syntax | Update Data > Use `INSERT ON DUPLICATE KEY UPDATE` > `INSERT ON DUPLICATE KEY UPDATE` best practices | Update Data > Use `INSERT ON DUPLICATE KEY UPDATE` > `INSERT ON DUPLICATE KEY UPDATE` example`
- Source Line Ranges: `96-161`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `insert-on-duplicate-key-update`, `sql-syntax`, `unique-key`, `primary-key`, `best-practices`, `examples`, `java`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0201_4a5c823508`
- Source ID: `tidb-docs-8.1:develop/dev-guide-update-data.md#use-insert-on-duplicate-key-update`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `690ba8bb5a0d80424a4f5966c03dc4a50882cf3ddad177815acd9777fb2acc80`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data#use-insert-on-duplicate-key-update
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-update-data.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to insert a row or update the first conflicted record with `INSERT ... ON DUPLICATE KEY UPDATE` and wants the limitations around unique keys.
- Retrieval Keywords: INSERT ON DUPLICATE KEY UPDATE, INSERT ... ON DUPLICATE KEY UPDATE ..., unique key conflicts, primary key is also a unique key, first conflicted record will be updated, one unique key, multiple unique keys, only one row will be updated, ratings, joint primary keys of `book_id` and `user_id`, INSERT INTO `ratings`, ON DUPLICATE KEY UPDATE `score` = 5, `rated_at` = NOW(), PreparedStatement
- Follow-up Guidance: The example shows updating or creating a rating in the `ratings` table for `book_id` and `user_id` using `NOW()` and `ON DUPLICATE KEY UPDATE`.
- Classification Note: This is classified as a SQL reference because the content gives the statement form, best-practice constraints for unique keys, and SQL and Java examples.

## Official Source Content

## Use `INSERT ON DUPLICATE KEY UPDATE`

If you need to insert new data into a table, but if there are unique key (a primary key is also a unique key) conflicts, the first conflicted record will be updated. You can use `INSERT ... ON DUPLICATE KEY UPDATE ...` statement to insert or update.
### `INSERT ON DUPLICATE KEY UPDATE` SQL Syntax

In SQL, the `INSERT ... ON DUPLICATE KEY UPDATE ...` statement is generally in the following form:

```sql
INSERT INTO {table} ({columns}) VALUES ({values})
    ON DUPLICATE KEY UPDATE {update_column} = {update_value};
```

| Parameter Name | Description |
| :---------------: | :--------------: |
|     `{table}`     |       Table name       |
|    `{columns}`    |   Column names to be inserted   |
|    `{values}`     | Column values to be inserted |
| `{update_column}` |   Column names to be updated   |
| `{update_value}`  | Column values to be updated |
### `INSERT ON DUPLICATE KEY UPDATE` best practices

- Use `INSERT ON DUPLICATE KEY UPDATE` only for a table with one unique key. This statement updates the data if any **_UNIQUE KEY_** (including the primary key) conflicts are detected. If there are more than one row of conflicts, only one row will be updated. Therefore, it is not recommended to use the `INSERT ON DUPLICATE KEY UPDATE` statement in tables with multiple unique keys unless you can guarantee that there is only one row of conflict.
- Use this statement when you create data or update data.
### `INSERT ON DUPLICATE KEY UPDATE` example

For example, you need to update the [ratings](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#ratings-table) table to include the user's ratings for the book. If the user has not yet rated the book, a new rating will be created. If the user has already rated it, his previous rating will be updated.

In the following example, the primary key is the joint primary keys of `book_id` and `user_id`. A user `user_id = 1` gives a rating of `5` to a book `book_id = 1000`.

<div label="SQL" value="sql">

```sql
INSERT INTO `ratings`
    (`book_id`, `user_id`, `score`, `rated_at`)
VALUES
    (1000, 1, 5, NOW())
ON DUPLICATE KEY UPDATE `score` = 5, `rated_at` = NOW();
```

</div>

<div label="Java" value="java">

```java
// ds is an entity of com.mysql.cj.jdbc.MysqlDataSource

try (Connection connection = ds.getConnection()) {
    PreparedStatement p = connection.prepareStatement("INSERT INTO `ratings` (`book_id`, `user_id`, `score`, `rated_at`)
VALUES (?, ?, ?, NOW()) ON DUPLICATE KEY UPDATE `score` = ?, `rated_at` = NOW()");
    p.setInt(1, 1000);
    p.setInt(2, 1);
    p.setInt(3, 5);
    p.setInt(4, 5);
    p.executeUpdate();
} catch (SQLException e) {
    e.printStackTrace();
}
```

</div>
