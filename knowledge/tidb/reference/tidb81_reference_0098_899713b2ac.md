# Single-table query examples with SQL and Java

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-get-data-from-single-table.md`
- Source Title: `Query Data from a Single Table`
- Source Heading Path: `Query Data from a Single Table | Query Data from a Single Table > Before you begin | Query Data from a Single Table > Execute a simple query | Query Data from a Single Table > Filter results | Query Data from a Single Table > Sort results | Query Data from a Single Table > Limit the number of query results`
- Source Line Ranges: `5-321`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `single-table queries`, `select`, `where`, `order by`, `limit`, `prepared statements`, `jdbc`, `java`, `bookshop`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0098_899713b2ac`
- Source ID: `tidb-docs-8.1:develop/dev-guide-get-data-from-single-table.md#query-data-from-a-single-table`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4083874429c89e1c452db4671f5423c92a6ff41e0d7c19c22a330369878978b6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table#query-data-from-a-single-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-get-data-from-single-table.md

## Retrieval Guidance

- Use When: Use this chunk when you need examples of querying a single table in TiDB with SQL or Java JDBC, including SELECT, WHERE, ORDER BY, LIMIT, and PreparedStatement usage on the Bookshop authors table.
- Retrieval Keywords: Query Data from a Single Table, Bookshop, authors table, SELECT id, name FROM authors, SELECT * FROM authors WHERE birth_year = 1998, ORDER BY birth_year DESC, LIMIT 10, PreparedStatement, ResultSet, Statement stmt = conn.createStatement(), stmt.executeQuery, getAuthorsByBirthYear, getAuthorsSortByBirthYear, getAuthorsWithLimit, Java JDBC, AuthorDAO
- Follow-up Guidance: The source also points to related documentation for connecting to TiDB, prepared statements, data types, value range, and TopN and Limit.
- Classification Note: This is reference content because it provides concrete SQL statements, Java JDBC code snippets, and example query patterns for single-table data retrieval.

## Official Source Content

# Query Data from a Single Table

This document describes how to use SQL and various programming languages to query data from a single table in a database.
## Before you begin

The following content takes the [Bookshop](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design) application as an example to show how to query data from a single table in TiDB.

Before querying data, make sure that you have completed the following steps:

1. Build a TiDB cluster (using [TiDB Cloud](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) or [TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) is recommended).

1. Build a TiDB cluster using [TiDB Cloud](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud).

2. [Import table schema and sample data of the Bookshop application](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#import-table-structures-and-data).

3. [Connect to TiDB](https://docs.pingcap.com/tidb/stable/develop/dev-guide-connect-to-tidb).

3. [Connect to TiDB](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster).
## Execute a simple query

In the database of the Bookshop application, the `authors` table stores the basic information of authors. You can use the `SELECT ... FROM ...` statement to query data from the database.

<div label="SQL" value="sql">

Execute the following SQL statement in a MySQL client:

```sql
SELECT id, name FROM authors;
```

The output is as follows:

```
+------------+--------------------------+
| id         | name                     |
+------------+--------------------------+
|       6357 | Adelle Bosco             |
|     345397 | Chanelle Koepp           |
|     807584 | Clementina Ryan          |
|     839921 | Gage Huel                |
|     850070 | Ray Armstrong            |
|     850362 | Ford Waelchi             |
|     881210 | Jayme Gutkowski          |
|    1165261 | Allison Kuvalis          |
|    1282036 | Adela Funk               |
...
| 4294957408 | Lyla Nitzsche            |
+------------+--------------------------+
20000 rows in set (0.05 sec)
```

</div>
<div label="Java" value="java">

In Java, to store the basic information of authors, you can declare a class `Author`. You should choose appropriate Java data types according to the [Data types](https://docs.pingcap.com/tidb/stable/data-type-overview) and [Value range](https://docs.pingcap.com/tidb/stable/data-type-numeric) in the database. For example:

- Use a variable of type `Int` to store data of type `int`.
- Use a variable of type `Long` to store data of type `bigint`.
- Use a variable of type `Short` to store data of type `tinyint`.
- Use a variable of type `String` to store data of type `varchar`.

```java
public class Author {
    private Long id;
    private String name;
    private Short gender;
    private Short birthYear;
    private Short deathYear;

    public Author() {}

     // Skip the getters and setters.
}
```

```java
public class AuthorDAO {

    // Omit initialization of instance variables.

    public List<Author> getAuthors() throws SQLException {
        List<Author> authors = new ArrayList<>();

        try (Connection conn = ds.getConnection()) {
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT id, name FROM authors");
            while (rs.next()) {
                Author author = new Author();
                author.setId(rs.getLong("id"));
                author.setName(rs.getString("name"));
                authors.add(author);
            }
        }
        return authors;
    }
}
```

- After [connecting to TiDB using the JDBC driver](https://docs.pingcap.com/tidb/stable/develop/dev-guide-connect-to-tidb#jdbc), you can create a `Statement` object with `conn.createStatus()`.

- After [connecting to TiDB using the JDBC driver](https://docs.pingcap.com/tidb/stable/develop/dev-guide-choose-driver-or-orm#java-drivers), you can create a `Statement` object with `conn.createStatus()`.

- Then call `stmt.executeQuery("query_sql")` to initiate a database query request to TiDB.
- The query results are stored in a `ResultSet` object. By traversing `ResultSet`, the returned results can be mapped to the `Author` object.

</div>
## Filter results

To filter query results, you can use the `WHERE` statement.

For example, the following command queries authors who were born in 1998 among all authors:

<div label="SQL" value="sql">

Add filter conditions in the `WHERE` statement:

```sql
SELECT * FROM authors WHERE birth_year = 1998;
```

</div>
<div label="Java" value="java">

In Java, you can use the same SQL to handle data query requests with dynamic parameters.

This can be done by concatenating parameters into a SQL statement. However, this method poses a potential [SQL Injection](https://en.wikipedia.org/wiki/SQL_injection) risk to the security of the application.

To deal with such queries, use a [Prepared statement](https://docs.pingcap.com/tidb/stable/develop/dev-guide-prepared-statement) instead of a normal statement.

```java
public List<Author> getAuthorsByBirthYear(Short birthYear) throws SQLException {
    List<Author> authors = new ArrayList<>();
    try (Connection conn = ds.getConnection()) {
        PreparedStatement stmt = conn.prepareStatement("""
        SELECT * FROM authors WHERE birth_year = ?;
        """);
        stmt.setShort(1, birthYear);
        ResultSet rs = stmt.executeQuery();
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
## Sort results

To sort query results, you can use the `ORDER BY` statement.

For example, the following SQL statement is to get a list of the youngest authors by sorting the `authors` table in descending order (`DESC`) according to the `birth_year` column.

<div label="SQL" value="sql">

```sql
SELECT id, name, birth_year
FROM authors
ORDER BY birth_year DESC;
```

</div>

<div label="Java" value="java">

```java
public List<Author> getAuthorsSortByBirthYear() throws SQLException {
    List<Author> authors = new ArrayList<>();
    try (Connection conn = ds.getConnection()) {
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("""
            SELECT id, name, birth_year
            FROM authors
            ORDER BY birth_year DESC;
            """);

        while (rs.next()) {
            Author author = new Author();
            author.setId(rs.getLong("id"));
            author.setName(rs.getString("name"));
            author.setBirthYear(rs.getShort("birth_year"));
            authors.add(author);
        }
    }
    return authors;
}
```

</div>

The result is as follows:

```
+-----------+------------------------+------------+
| id        | name                   | birth_year |
+-----------+------------------------+------------+
| 83420726  | Terrance Dach          | 2000       |
| 57938667  | Margarita Christiansen | 2000       |
| 77441404  | Otto Dibbert           | 2000       |
| 61338414  | Danial Cormier         | 2000       |
| 49680887  | Alivia Lemke           | 2000       |
| 45460101  | Itzel Cummings         | 2000       |
| 38009380  | Percy Hodkiewicz       | 2000       |
| 12943560  | Hulda Hackett          | 2000       |
| 1294029   | Stanford Herman        | 2000       |
| 111453184 | Jeffrey Brekke         | 2000       |
...
300000 rows in set (0.23 sec)
```
## Limit the number of query results

To limit the number of query results, you can use the `LIMIT` statement.

<div label="SQL" value="sql">

```sql
SELECT id, name, birth_year
FROM authors
ORDER BY birth_year DESC
LIMIT 10;
```

</div>

<div label="Java" value="java">

```java
public List<Author> getAuthorsWithLimit(Integer limit) throws SQLException {
    List<Author> authors = new ArrayList<>();
    try (Connection conn = ds.getConnection()) {
        PreparedStatement stmt = conn.prepareStatement("""
            SELECT id, name, birth_year
            FROM authors
            ORDER BY birth_year DESC
            LIMIT ?;
            """);
        stmt.setInt(1, limit);
        ResultSet rs = stmt.executeQuery();
        while (rs.next()) {
            Author author = new Author();
            author.setId(rs.getLong("id"));
            author.setName(rs.getString("name"));
            author.setBirthYear(rs.getShort("birth_year"));
            authors.add(author);
        }
    }
    return authors;
}
```

</div>

The result is as follows:

```
+-----------+------------------------+------------+
| id        | name                   | birth_year |
+-----------+------------------------+------------+
| 83420726  | Terrance Dach          | 2000       |
| 57938667  | Margarita Christiansen | 2000       |
| 77441404  | Otto Dibbert           | 2000       |
| 61338414  | Danial Cormier         | 2000       |
| 49680887  | Alivia Lemke           | 2000       |
| 45460101  | Itzel Cummings         | 2000       |
| 38009380  | Percy Hodkiewicz       | 2000       |
| 12943560  | Hulda Hackett          | 2000       |
| 1294029   | Stanford Herman        | 2000       |
| 111453184 | Jeffrey Brekke         | 2000       |
+-----------+------------------------+------------+
10 rows in set (0.11 sec)
```

With the `LIMIT` statement, the query time is significantly reduced from `0.23 sec` to `0.11 sec` in this example. For more information, see [TopN and Limit](https://docs.pingcap.com/tidb/stable/topn-limit-push-down).
