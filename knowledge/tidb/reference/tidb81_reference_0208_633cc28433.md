# Create local and global temporary tables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-use-temporary-tables.md`
- Source Title: `Temporary Tables`
- Source Heading Path: `Temporary Tables | Temporary Tables > Create a temporary table | Temporary Tables > Create a temporary table > Types of temporary tables | Temporary Tables > Create a temporary table > Create a local temporary table | Temporary Tables > Create a temporary table > Create a global temporary table`
- Source Line Ranges: `5-196`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `temporary-tables`, `create-table`, `local-temporary-table`, `global-temporary-table`, `session-scope`, `transaction-scope`, `permissions`, `autocommit`, `java`, `sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0208_633cc28433`
- Source ID: `tidb-docs-8.1:develop/dev-guide-use-temporary-tables.md#temporary-tables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a9f80edce17334255be4b1c996a33ffb7076d41ce91731c25fb32f0ca49d0ab0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-temporary-tables#temporary-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-use-temporary-tables.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the SQL or Java syntax to create local or global temporary tables in TiDB and understand session visibility, transaction visibility, permissions, or autocommit behavior.
- Retrieval Keywords: CREATE TEMPORARY TABLE, CREATE GLOBAL TEMPORARY TABLE, ON COMMIT DELETE ROWS, CREATE TEMPORARY TABLES, BEGIN, Auto Commit mode, conn.setAutoCommit(false);, conn.commit();, local temporary table, global temporary table, visible only to the current session, visible only to the current transaction, INSERT INTO top_50_eldest_authors SELECT, top_50_eldest_authors_global
- Follow-up Guidance: The source also explains that local temporary tables are automatically dropped after a session ends, while global temporary table data is cleared when the current transaction ends.
- Classification Note: This is classified as reference content because it provides exact SQL and Java examples, permission requirements, and behavioral definitions for creating temporary tables.

## Official Source Content

# Temporary Tables

Temporary tables can be thought of as a technique for reusing query results.

If you want to know something about the eldest authors in the [Bookshop](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design) application, you might write multiple queries that use the list of eldest authors.

For example, you can use the following statement to get the top 50 eldest authors from the `authors` table:

```sql
SELECT a.id, a.name, (IFNULL(a.death_year, YEAR(NOW())) - a.birth_year) AS age
FROM authors a
ORDER BY age DESC
LIMIT 50;
```

The result is as follows:

```
+------------+---------------------+------+
| id         | name                | age  |
+------------+---------------------+------+
| 4053452056 | Dessie Thompson     |   80 |
| 2773958689 | Pedro Hansen        |   80 |
| 4005636688 | Wyatt Keeling       |   80 |
| 3621155838 | Colby Parker        |   80 |
| 2738876051 | Friedrich Hagenes   |   80 |
| 2299112019 | Ray Macejkovic      |   80 |
| 3953661843 | Brandi Williamson   |   80 |
...
| 4100546410 | Maida Walsh         |   80 |
+------------+---------------------+------+
50 rows in set (0.01 sec)
```

For the convenience of subsequent queries, you need to cache the result of this query. When using general tables for storage, you should pay attention to how to avoid the table name duplication problem between different sessions, and the need of cleaning up intermediate results in time, as these tables might not be used after a batch query.
## Create a temporary table

To cache intermediate results, the temporary tables feature is introduced in TiDB v5.3.0. TiDB automatically drops a local temporary table after a session ends, which frees you from worrying about the management trouble caused by increasing intermediate results.
### Types of temporary tables

Temporary tables in TiDB are divided into two types: local temporary tables and global temporary tables.

- For a local temporary table, the table definition and data in the table are visible only to the current session. This type is suitable for temporarily storing intermediate data in the session.
- For a global temporary table, the table definition is visible to the entire TiDB cluster, and the data in the table is visible only to the current transaction. This type is suitable for temporarily storing intermediate data in a transaction.
### Create a local temporary table

Before creating a local temporary table, you need to add `CREATE TEMPORARY TABLES` permission to the current database user.

<div label="SQL" value="sql">

You can create a temporary table using the `CREATE TEMPORARY TABLE <table_name>` statement. The default type is a local temporary table, which is visible only to the current session.

```sql
CREATE TEMPORARY TABLE top_50_eldest_authors (
    id BIGINT,
    name VARCHAR(255),
    age INT,
    PRIMARY KEY(id)
);
```

After creating the temporary table, you can use the `INSERT INTO table_name SELECT ...` statement to insert the results of the above query into the temporary table you just created.

```sql
INSERT INTO top_50_eldest_authors
SELECT a.id, a.name, (IFNULL(a.death_year, YEAR(NOW())) - a.birth_year) AS age
FROM authors a
ORDER BY age DESC
LIMIT 50;
```

The result is as follows:

```
Query OK, 50 rows affected (0.03 sec)
Records: 50  Duplicates: 0  Warnings: 0
```

</div>
<div label="Java" value="java">

```java
public List<Author> getTop50EldestAuthorInfo() throws SQLException {
    List<Author> authors = new ArrayList<>();
    try (Connection conn = ds.getConnection()) {
        Statement stmt = conn.createStatement();
        stmt.executeUpdate("""
            CREATE TEMPORARY TABLE top_50_eldest_authors (
                id BIGINT,
                name VARCHAR(255),
                age INT,
                PRIMARY KEY(id)
            );
        """);

        stmt.executeUpdate("""
            INSERT INTO top_50_eldest_authors
            SELECT a.id, a.name, (IFNULL(a.death_year, YEAR(NOW())) - a.birth_year) AS age
            FROM authors a
            ORDER BY age DESC
            LIMIT 50;
        """);

        ResultSet rs = stmt.executeQuery("""
            SELECT id, name FROM top_50_eldest_authors;
        """);

        while (rs.next()) {
            Author author = new Author();
            author.setId(rs.getLong("id"));
            author.setName(rs.getString("name"));
            authors.add(author);
        }
    }
    return authors;
}
```

</div>
### Create a global temporary table

<div label="SQL" value="sql">

To create a global temporary table, you can add the `GLOBAL` keyword and end with `ON COMMIT DELETE ROWS`, which means the table will be deleted after the current transaction ends.

```sql
CREATE GLOBAL TEMPORARY TABLE IF NOT EXISTS top_50_eldest_authors_global (
    id BIGINT,
    name VARCHAR(255),
    age INT,
    PRIMARY KEY(id)
) ON COMMIT DELETE ROWS;
```

When inserting data to global temporary tables, you must explicitly declare the start of the transaction via `BEGIN`. Otherwise, the data will be cleared after the `INSERT INTO` statement is executed. Because in the Auto Commit mode, the transaction is automatically committed after the `INSERT INTO` statement is executed, and the global temporary table is cleared when the transaction ends.

</div>
<div label="Java" value="java">

When using global temporary tables, you need to turn off Auto Commit mode first. In Java, you can do this with the `conn.setAutoCommit(false);` statement, and you can commit the transaction explicitly with `conn.commit();`. The data added to the global temporary table during the transaction will be cleared after the transaction is committed or canceled.

```java
public List<Author> getTop50EldestAuthorInfo() throws SQLException {
    List<Author> authors = new ArrayList<>();
    try (Connection conn = ds.getConnection()) {
        conn.setAutoCommit(false);

        Statement stmt = conn.createStatement();
        stmt.executeUpdate("""
            CREATE GLOBAL TEMPORARY TABLE IF NOT EXISTS top_50_eldest_authors (
                id BIGINT,
                name VARCHAR(255),
                age INT,
                PRIMARY KEY(id)
            ) ON COMMIT DELETE ROWS;
        """);

        stmt.executeUpdate("""
            INSERT INTO top_50_eldest_authors
            SELECT a.id, a.name, (IFNULL(a.death_year, YEAR(NOW())) - a.birth_year) AS age
            FROM authors a
            ORDER BY age DESC
            LIMIT 50;
        """);

        ResultSet rs = stmt.executeQuery("""
            SELECT id, name FROM top_50_eldest_authors;
        """);

        conn.commit();
        while (rs.next()) {
            Author author = new Author();
            author.setId(rs.getLong("id"));
            author.setName(rs.getString("name"));
            authors.add(author);
        }
    }
    return authors;
}
```

</div>
