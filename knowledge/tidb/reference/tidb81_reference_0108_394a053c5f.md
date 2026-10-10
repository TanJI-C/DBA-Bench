# Join types with inner and left outer join examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-join-tables.md`
- Source Title: `Multi-table Join Queries`
- Source Heading Path: `Multi-table Join Queries | Multi-table Join Queries > Join types | Multi-table Join Queries > Join types > INNER JOIN | Multi-table Join Queries > Join types > LEFT OUTER JOIN`
- Source Line Ranges: `5-189`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `join`, `inner join`, `left outer join`, `sql syntax`, `java example`, `result set`, `null handling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0108_394a053c5f`
- Source ID: `tidb-docs-8.1:develop/dev-guide-join-tables.md#multi-table-join-queries`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `833236cbb77a18c0cc0637cd2bf399f139ea16e3656986a39ec435bed1b4ba2e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-join-tables#multi-table-join-queries
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-join-tables.md

## Retrieval Guidance

- Use When: Use this chunk when you need examples that contrast `INNER JOIN` and `LEFT JOIN`, including how unmatched rows are filtered or returned with `NULL` values.
- Retrieval Keywords: INNER JOIN, LEFT OUTER JOIN, LEFT JOIN, authors, book_authors, books, ratings, a.id = ba.author_id, b.id = r.book_id, ANY_VALUE(a.id) AS author_id, COUNT(ba.book_id) AS books, AVG(r.score) AS average_score, DELETE FROM ratings WHERE book_id = 3438991610, average_score NULL, Java ResultSet
- Follow-up Guidance: It also shows Java methods that execute these join queries and read `author_id`, `author_name`, `books`, `book_id`, `book_title`, and `average_score` from a `ResultSet`.
- Classification Note: This is reference content because it explains join semantics and provides concrete SQL and Java examples for `INNER JOIN` and `LEFT OUTER JOIN`.

## Official Source Content

# Multi-table Join Queries

In many scenarios, you need to use one query to get data from multiple tables. You can use the `JOIN` statement to combine the data from two or more tables.
## Join types

This section describes the Join types in detail.
### INNER JOIN

The join result of an inner join returns only rows that match the join condition.

![Inner Join](/media/develop/inner-join.png)

For example, if you want to know the most prolific author, you need to join the author table named `authors` with the book author table named `book_authors`.

<div label="SQL" value="sql">

In the following SQL statement, use the keyword `JOIN` to declare that you want to join the rows of the left table `authors` and the right table `book_authors` as an inner join with the join condition `a.id = ba.author_id`. The result set will only contain rows that satisfy the join condition. If an author has not written any books, then his record in `authors` table will not satisfy the join condition and will therefore not appear in the result set.

```sql
SELECT ANY_VALUE(a.id) AS author_id, ANY_VALUE(a.name) AS author_name, COUNT(ba.book_id) AS books
FROM authors a
JOIN book_authors ba ON a.id = ba.author_id
GROUP BY ba.author_id
ORDER BY books DESC
LIMIT 10;
```

The query results are as follows:

```
+------------+----------------+-------+
| author_id  | author_name    | books |
+------------+----------------+-------+
|  431192671 | Emilie Cassin  |     7 |
|  865305676 | Nola Howell    |     7 |
|  572207928 | Lamar Koch     |     6 |
| 3894029860 | Elijah Howe    |     6 |
| 1150614082 | Cristal Stehr  |     6 |
| 4158341032 | Roslyn Rippin  |     6 |
| 2430691560 | Francisca Hahn |     6 |
| 3346415350 | Leta Weimann   |     6 |
| 1395124973 | Albin Cole     |     6 |
| 2768150724 | Caleb Wyman    |     6 |
+------------+----------------+-------+
10 rows in set (0.01 sec)
```

</div>
<div label="Java" value="java">

```java
public List<Author> getTop10AuthorsOrderByBooks() throws SQLException {
    List<Author> authors = new ArrayList<>();
    try (Connection conn = ds.getConnection()) {
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("""
        SELECT ANY_VALUE(a.id) AS author_id, ANY_VALUE(a.name) AS author_name, COUNT(ba.book_id) AS books
        FROM authors a
        JOIN book_authors ba ON a.id = ba.author_id
        GROUP BY ba.author_id
        ORDER BY books DESC
        LIMIT 10;
        """);
        while (rs.next()) {
            Author author = new Author();
            author.setId(rs.getLong("author_id"));
            author.setName(rs.getString("author_name"));
            author.setBooks(rs.getInt("books"));
            authors.add(author);
        }
    }
    return authors;
}
```

</div>
### LEFT OUTER JOIN

The left outer join returns all the rows in the left table and the values ​​in the right table that match the join condition. If no rows are matched in the right table, it will be filled with `NULL`.

![Left Outer Join](/media/develop/left-outer-join.png)

In some cases, you want to use multiple tables to complete the data query, but do not want the data set to become too small because the join condition are not met.

For example, on the homepage of the Bookshop app, you want to display a list of new books with average ratings. In this case, the new books may not have been rated by anyone yet. Using inner joins will cause the information of these unrated books to be filtered out, which is not what you expect.

<div label="SQL" value="sql">

In the following SQL statement, use the `LEFT JOIN` keyword to declare that the left table `books` will be joined to the right table `ratings` in a left outer join, thus ensuring that all rows in the `books` table are returned.

```sql
SELECT b.id AS book_id, ANY_VALUE(b.title) AS book_title, AVG(r.score) AS average_score
FROM books b
LEFT JOIN ratings r ON b.id = r.book_id
GROUP BY b.id
ORDER BY b.published_at DESC
LIMIT 10;
```

The query results are as follows:

```
+------------+---------------------------------+---------------+
| book_id    | book_title                      | average_score |
+------------+---------------------------------+---------------+
| 3438991610 | The Documentary of lion         |        2.7619 |
| 3897175886 | Torey Kuhn                      |        3.0000 |
| 1256171496 | Elmo Vandervort                 |        2.5500 |
| 1036915727 | The Story of Munchkin           |        2.0000 |
|  270254583 | Tate Kovacek                    |        2.5000 |
| 1280950719 | Carson Damore                   |        3.2105 |
| 1098041838 | The Documentary of grasshopper  |        2.8462 |
| 1476566306 | The Adventures of Vince Sanford |        2.3529 |
| 4036300890 | The Documentary of turtle       |        2.4545 |
| 1299849448 | Antwan Olson                    |        3.0000 |
+------------+---------------------------------+---------------+
10 rows in set (0.30 sec)
```

It seems that the latest published book already has a lot of ratings. To verify the above method, let's delete all the ratings of the book _The Documentary of lion_ through the SQL statement:

```sql
DELETE FROM ratings WHERE book_id = 3438991610;
```

Query again. The book _The Documentary of lion_ still appears in the result set, but the `average_score` column calculated from `score` of the right table `ratings` is filled with `NULL`.

```
+------------+---------------------------------+---------------+
| book_id    | book_title                      | average_score |
+------------+---------------------------------+---------------+
| 3438991610 | The Documentary of lion         |          NULL |
| 3897175886 | Torey Kuhn                      |        3.0000 |
| 1256171496 | Elmo Vandervort                 |        2.5500 |
| 1036915727 | The Story of Munchkin           |        2.0000 |
|  270254583 | Tate Kovacek                    |        2.5000 |
| 1280950719 | Carson Damore                   |        3.2105 |
| 1098041838 | The Documentary of grasshopper  |        2.8462 |
| 1476566306 | The Adventures of Vince Sanford |        2.3529 |
| 4036300890 | The Documentary of turtle       |        2.4545 |
| 1299849448 | Antwan Olson                    |        3.0000 |
+------------+---------------------------------+---------------+
10 rows in set (0.30 sec)
```

What happens if you use `INNER JOIN`? It's up to you to have a try.

</div>
<div label="Java" value="java">

```java
public List<Book> getLatestBooksWithAverageScore() throws SQLException {
    List<Book> books = new ArrayList<>();
    try (Connection conn = ds.getConnection()) {
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("""
        SELECT b.id AS book_id, ANY_VALUE(b.title) AS book_title, AVG(r.score) AS average_score
        FROM books b
        LEFT JOIN ratings r ON b.id = r.book_id
        GROUP BY b.id
        ORDER BY b.published_at DESC
        LIMIT 10;
        """);
        while (rs.next()) {
            Book book = new Book();
            book.setId(rs.getLong("book_id"));
            book.setTitle(rs.getString("book_title"));
            book.setAverageScore(rs.getFloat("average_score"));
            books.add(book);
        }
    }
    return books;
}
```

</div>
