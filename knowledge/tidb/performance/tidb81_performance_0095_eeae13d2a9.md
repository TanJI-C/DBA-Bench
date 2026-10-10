# DML performance best practices

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-optimize-sql-best-practices.md`
- Source Title: `Performance Tuning Best Practices`
- Source Heading Path: `Performance Tuning Best Practices | Performance Tuning Best Practices > DML best practices | Performance Tuning Best Practices > DML best practices > Use multi-row statements | Performance Tuning Best Practices > DML best practices > Use `PREPARE` | Performance Tuning Best Practices > DML best practices > Only query the columns you need | Performance Tuning Best Practices > DML best practices > Use bulk delete | Performance Tuning Best Practices > DML best practices > Use bulk update | Performance Tuning Best Practices > DML best practices > Use `TRUNCATE` instead of `DELETE` for full table data`
- Source Line Ranges: `5-118`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `dml`, `multi-row-statements`, `prepare`, `prepared-statements`, `select-columns`, `bulk-delete`, `bulk-update`, `truncate`, `delete`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0095_eeae13d2a9`
- Source ID: `tidb-docs-8.1:develop/dev-guide-optimize-sql-best-practices.md#performance-tuning-best-practices`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b287b2fe9a481053973ad127ec295295da2af6e449f2f018c09ddba0528aaac7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-best-practices#performance-tuning-best-practices
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-optimize-sql-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB DML performance best practices around multi-row statements, PREPARE, selective column queries, bulk delete or update, and TRUNCATE versus DELETE.
- Retrieval Keywords: DML performance best practices, Use multi-row statements, INSERT INTO t VALUES (1, 'a'), (2, 'b'), (3, 'c'), DELETE FROM t WHERE id IN (1, 2, 3), Use PREPARE, PREPARE statement, do not execute the PREPARE statement repeatedly, PreparedStatement, Only query the columns you need, SELECT *, SELECT title, price FROM books WHERE title = 'Marian Yost', Use bulk delete, Use bulk update, Use TRUNCATE instead of DELETE for full table data, TRUNCATE TABLE t, DELETE FROM t
- Follow-up Guidance: The source also points to bulk delete and bulk update guidance for deleting or updating a large amount of data.
- Classification Note: This is classified as performance for SQL because the content gives DML usage patterns that reduce parsing overhead, avoid unnecessary data retrieval, and improve statement efficiency.

## Official Source Content

# Performance Tuning Best Practices

This document introduces some best practices for using TiDB databases.
## DML best practices

This section describes the best practices involved when you use DML with TiDB.
### Use multi-row statements

When you need to modify multiple rows of table, it is recommended to use multi-row statements:

```sql
INSERT INTO t VALUES (1, 'a'), (2, 'b'), (3, 'c');

DELETE FROM t WHERE id IN (1, 2, 3);
```

It is not recommended to use multiple single-row statements:

```sql
INSERT INTO t VALUES (1, 'a');
INSERT INTO t VALUES (2, 'b');
INSERT INTO t VALUES (3, 'c');

DELETE FROM t WHERE id = 1;
DELETE FROM t WHERE id = 2;
DELETE FROM t WHERE id = 3;
```
### Use `PREPARE`

When you need to execute a SQL statement for multiple times, it is recommended to use the `PREPARE` statement to avoid the overhead of repeatedly parsing the SQL syntax.

<div label="Golang">

```go
func BatchInsert(db *sql.DB) error {
    stmt, err := db.Prepare("INSERT INTO t (id) VALUES (?), (?), (?), (?), (?)")
    if err != nil {
        return err
    }
    for i := 0; i < 1000; i += 5 {
        values := []interface{}{i, i + 1, i + 2, i + 3, i + 4}
        _, err = stmt.Exec(values...)
        if err != nil {
            return err
        }
    }
    return nil
}
```

</div>

<div label="Java">

```java
public void batchInsert(Connection connection) throws SQLException {
    PreparedStatement statement = connection.prepareStatement(
            "INSERT INTO `t` (`id`) VALUES (?), (?), (?), (?), (?)");
    for (int i = 0; i < 1000; i ++) {
        statement.setInt(i % 5 + 1, i);

        if (i % 5 == 4) {
            statement.executeUpdate();
        }
    }
}
```

</div>

Do not execute the `PREPARE` statement repeatedly. Otherwise, the execution efficiency cannot be improved.
### Only query the columns you need

If you do not need data from all columns, do not use `SELECT *` to return all columns data. The following query is inefficient:

```sql
SELECT * FROM books WHERE title = 'Marian Yost';
```

You should only query the columns you need. For example:

```sql
SELECT title, price FROM books WHERE title = 'Marian Yost';
```
### Use bulk delete

When you delete a large amount of data, it is recommended to use [bulk delete](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data#bulk-delete).
### Use bulk update

When you update a large amount of data, it is recommended to use [bulk update](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data#bulk-update).
### Use `TRUNCATE` instead of `DELETE` for full table data

When you need to delete all data from a table, it is recommended to use the `TRUNCATE` statement:

```sql
TRUNCATE TABLE t;
```

It is not recommended to use `DELETE` for full table data:

```sql
DELETE FROM t;
```
