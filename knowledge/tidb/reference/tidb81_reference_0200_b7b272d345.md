# Update data with UPDATE statement

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-update-data.md`
- Source Title: `Update Data`
- Source Heading Path: `Update Data | Update Data > Before you start | Update Data > Use `UPDATE` | Update Data > Use `UPDATE` > `UPDATE` SQL syntax | Update Data > Use `UPDATE` > `UPDATE` best practices | Update Data > Use `UPDATE` > `UPDATE` example`
- Source Line Ranges: `5-95`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `update`, `sql-syntax`, `where-clause`, `best-practices`, `transactions`, `locks`, `examples`, `java`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0200_b7b272d345`
- Source ID: `tidb-docs-8.1:develop/dev-guide-update-data.md#update-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `094d4f7120d5ff340c409af34fc2cb19ae149596c0a13cdcb5ab1ff66393c799`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data#update-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-update-data.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB `UPDATE` statement syntax, `WHERE` clause guidance, transaction-size cautions, or a simple SQL and Java example for updating a row.
- Retrieval Keywords: UPDATE statement, UPDATE SQL syntax, UPDATE {table} SET {update_column} = {update_value} WHERE {filter_column} = {filter_value}, WHERE clause, update all rows, bulk-update, txn-total-size-limit, 100 MB by default, pessimistic transactions, optimistic transactions, authors, UPDATE `authors` SET `name` = "Helen Haruki" WHERE `id` = 1, PreparedStatement, executeUpdate
- Follow-up Guidance: For large updates, the document points to the Bulk-update section for iterative updates of a portion of rows at a time.
- Classification Note: This is classified as a SQL reference because the content defines `UPDATE` syntax, best practices, and example statements for updating table data.

## Official Source Content

# Update Data

This document describes how to use the following SQL statements to update the data in TiDB with various programming languages:

- [UPDATE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update): Used to modify the data in the specified table.
- [INSERT ON DUPLICATE KEY UPDATE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert): Used to insert data and update this data if there is a primary key or unique key conflict. It is **not recommended** to use this statement if there are multiple unique keys (including primary keys). This is because this statement updates the data once it detects any unique key (including primary key) conflict. When there are more than one row conflicts, it updates only one row.
## Before you start

Before reading this document, you need to prepare the following:

- [Build a {{{ .starter }}} Cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud).
- Read [Schema Design Overview](https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview), [Create a Database](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-database), [Create a Table](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table), and [Create Secondary Indexes](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-secondary-indexes).
- If you want to `UPDATE` data, you need to [insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data) first.
## Use `UPDATE`

To update an existing row in a table, you need to use an [`UPDATE` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update) with a `WHERE` clause to filter the columns for updating.

> **Note:**
>
> If you need to update a large number of rows, for example, more than ten thousand, it is recommended that you do **_NOT_** doing a complete update at once, but rather updating a portion at a time iteratively until all rows are updated. You can write scripts or programs to loop this operation.
> See [Bulk-update](#bulk-update) for details.
### `UPDATE` SQL syntax

In SQL, the `UPDATE` statement is generally in the following form:

```sql
UPDATE {table} SET {update_column} = {update_value} WHERE {filter_column} = {filter_value}
```

| Parameter Name | Description |
| :---------------: | :------------------: |
|     `{table}`     |         Table Name         |
| `{update_column}` |     Column names to be updated     |
| `{update_value}`  |   Column values to be updated   |
| `{filter_column}` | Column names matching filters |
| `{filter_value}`  | Column values matching filters |

For detailed information, see [UPDATE syntax](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update).
### `UPDATE` best practices

The following are some best practices for updating data:

- Always specify the `WHERE` clause in the `UPDATE` statement. If the `UPDATE` statement does not have a `WHERE` clause, TiDB will update **_ALL ROWS_** in the table.

- Use [bulk-update](#bulk-update) when you need to update a large number of rows (for example, more than ten thousand). Because TiDB limits the size of a single transaction ([txn-total-size-limit](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit), 100 MB by default), too many data updates at once will result in holding locks for too long ([pessimistic transactions](https://docs.pingcap.com/tidb/stable/pessimistic-transaction)) or cause conflicts ([optimistic transactions](https://docs.pingcap.com/tidb/stable/optimistic-transaction)).

- Use [bulk-update](#bulk-update) when you need to update a large number of rows (for example, more than ten thousand). Because TiDB limits the size of a single transaction to 100 MB by default, too many data updates at once will result in holding locks for too long ([pessimistic transactions](https://docs.pingcap.com/tidb/stable/pessimistic-transaction)) or cause conflicts ([optimistic transactions](https://docs.pingcap.com/tidb/stable/optimistic-transaction)).
### `UPDATE` example

Suppose an author changes her name to **Helen Haruki**. You need to change the [authors](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#authors-table) table. Assume that her unique `id` is **1**, and the filter should be: `id = 1`.

<div label="SQL" value="sql">

```sql
UPDATE `authors` SET `name` = "Helen Haruki" WHERE `id` = 1;
```

</div>

<div label="Java" value="java">

```java
// ds is an entity of com.mysql.cj.jdbc.MysqlDataSource
try (Connection connection = ds.getConnection()) {
    PreparedStatement pstmt = connection.prepareStatement("UPDATE `authors` SET `name` = ? WHERE `id` = ?");
    pstmt.setString(1, "Helen Haruki");
    pstmt.setInt(2, 1);
    pstmt.executeUpdate();
} catch (SQLException e) {
    e.printStackTrace();
}
```

</div>
