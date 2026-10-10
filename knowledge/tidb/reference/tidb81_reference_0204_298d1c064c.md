# Statement-level Stale Read syntax, examples, and errors

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-use-stale-read.md`
- Source Title: `Stale Read`
- Source Heading Path: `Stale Read > Statement level`
- Source Line Ranges: `71-224`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `stale-read`, `as-of-timestamp`, `bounded-staleness`, `now-function`, `gc-life-time`, `gc-safe-point`, `sql-example`, `java-example`, `error-handling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0204_298d1c064c`
- Source ID: `tidb-docs-8.1:develop/dev-guide-use-stale-read.md#statement-level`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `29ce83411cad3004092541d45a8e582fa8b73c5630e3c4f151823304da0f7e0e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-stale-read#statement-level
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-use-stale-read.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about statement-level Stale Read SQL syntax, `AS OF TIMESTAMP` examples, bounded staleness functions, `NOW()` precision, GC Safe Point limits, or the related error messages and Java handling example.
- Retrieval Keywords: Statement level, AS OF TIMESTAMP, SELECT id, title, type, price FROM books AS OF TIMESTAMP '2022-04-20 15:20:00' ORDER BY published_at DESC LIMIT 5, AS OF TIMESTAMP NOW() - INTERVAL 10 SECOND, TIDB_BOUNDED_STALENESS('2016-10-08 16:45:26', '2016-10-08 16:45:29'), TIDB_BOUNDED_STALENESS(NOW() -INTERVAL 20 SECOND, NOW()), NOW(), NOW(3), GC Life Time, tidb_gc_life_time, GC Safe Point, ERROR 9006 (HY000): GC life time is shorter than transaction duration, ERROR 9006 (HY000): cannot set read timestamp to a future time, getTop5LatestBooksWithStaleRead, WARN: cannot set read timestamp to a future time., WARN: GC life time is shorter than transaction duration.
- Follow-up Guidance: The Java example shows `getTop5LatestBooksWithStaleRead(Integer seconds)` using `AS OF TIMESTAMP NOW() - INTERVAL ? SECOND` and handling SQLState `HY000` with error codes `1105` and `9006`.
- Classification Note: This is classified as reference because the content provides exact statement-level syntax, function forms, timestamp constraints, error text, and a concrete Java usage example for Stale Read.

## Official Source Content

## Statement level

<div label="SQL" value="sql">

To query the price of a book before a specific time, add an `AS OF TIMESTAMP <datetime>` clause in the above query statement.

```sql
SELECT id, title, type, price FROM books AS OF TIMESTAMP '2022-04-20 15:20:00' ORDER BY published_at DESC LIMIT 5;
```

The result is as follows:

```
+------------+------------------------------+-----------------------+--------+
| id         | title                        | type                  | price  |
+------------+------------------------------+-----------------------+--------+
| 3181093216 | The Story of Droolius Caesar | Novel                 | 100.00 |
| 1064253862 | Collin Rolfson               | Education & Reference |  92.85 |
| 1748583991 | The Documentary of cat       | Magazine              | 159.75 |
|  893930596 | Myrl Hills                   | Education & Reference | 356.85 |
| 3062833277 | Keven Wyman                  | Life                  | 477.91 |
+------------+------------------------------+-----------------------+--------+
5 rows in set (0.01 sec)
```

In addition to specifying an exact time, you can also specify the following:

- `AS OF TIMESTAMP NOW() - INTERVAL 10 SECOND` queries the latest data 10 seconds ago.
- `AS OF TIMESTAMP TIDB_BOUNDED_STALENESS('2016-10-08 16:45:26', '2016-10-08 16:45:29')` queries the latest data between `2016-10-08 16:45:26` and `2016-10-08 16:45:29`.
- `AS OF TIMESTAMP TIDB_BOUNDED_STALENESS(NOW() -INTERVAL 20 SECOND, NOW())` queries the latest data within 20 seconds.

Note that the specified timestamp or interval cannot be too early or later than the current time. Additionally, `NOW()` defaults to second precision. To achieve higher precision, you can add a parameter, such as using `NOW(3)` for millisecond precision. For more information, see [MySQL documentation](https://dev.mysql.com/doc/refman/8.0/en/date-and-time-functions.html#function_now).

Expired data will be recycled by [Garbage Collection](https://docs.pingcap.com/tidb/stable/garbage-collection-overview) in TiDB, and the data will be retained for a short period before being cleared. The period is called [GC Life Time (default 10 minutes)](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50). When a GC starts, the current time minus the time period will be used as the **GC Safe Point**. If you try to read the data before GC Safe Point, TiDB will report the following error:

```
ERROR 9006 (HY000): GC life time is shorter than transaction duration...
```

If the given timestamp is a future time, TiDB will report the following error:

```
ERROR 9006 (HY000): cannot set read timestamp to a future time.
```

</div>
<div label="Java" value="java">

```java
public class BookDAO {

    // Omit some code...

    public List<Book> getTop5LatestBooks() throws SQLException {
        List<Book> books = new ArrayList<>();
        try (Connection conn = ds.getConnection()) {
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("""
            SELECT id, title, type, price FROM books ORDER BY published_at DESC LIMIT 5;
            """);
            while (rs.next()) {
                Book book = new Book();
                book.setId(rs.getLong("id"));
                book.setTitle(rs.getString("title"));
                book.setType(rs.getString("type"));
                book.setPrice(rs.getDouble("price"));
                books.add(book);
            }
        }
        return books;
    }

    public void updateBookPriceByID(Long id, Double price) throws SQLException {
        try (Connection conn = ds.getConnection()) {
            PreparedStatement stmt = conn.prepareStatement("""
            UPDATE books SET price = ? WHERE id = ?;
            """);
            stmt.setDouble(1, price);
            stmt.setLong(2, id);
            int affects = stmt.executeUpdate();
            if (affects == 0) {
                throw new SQLException("Failed to update the book with id: " + id);
            }
        }
    }

    public List<Book> getTop5LatestBooksWithStaleRead(Integer seconds) throws SQLException {
        List<Book> books = new ArrayList<>();
        try (Connection conn = ds.getConnection()) {
            PreparedStatement stmt = conn.prepareStatement("""
            SELECT id, title, type, price FROM books AS OF TIMESTAMP NOW() - INTERVAL ? SECOND ORDER BY published_at DESC LIMIT 5;
            """);
            stmt.setInt(1, seconds);
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                Book book = new Book();
                book.setId(rs.getLong("id"));
                book.setTitle(rs.getString("title"));
                book.setType(rs.getString("type"));
                book.setPrice(rs.getDouble("price"));
                books.add(book);
            }
        } catch (SQLException e) {
            if ("HY000".equals(e.getSQLState()) && e.getErrorCode() == 1105) {
                System.out.println("WARN: cannot set read timestamp to a future time.");
            } else if ("HY000".equals(e.getSQLState()) && e.getErrorCode() == 9006) {
                System.out.println("WARN: GC life time is shorter than transaction duration.");
            } else {
                throw e;
            }
        }
        return books;
    }
}
```

```java
List<Book> top5LatestBooks = bookDAO.getTop5LatestBooks();

if (top5LatestBooks.size() > 0) {
    System.out.println("The latest book price (before update): " + top5LatestBooks.get(0).getPrice());

    Book book = top5LatestBooks.get(0);
    bookDAO.updateBookPriceByID(book.getId(), book.price + 10);

    top5LatestBooks = bookDAO.getTop5LatestBooks();
    System.out.println("The latest book price (after update): " + top5LatestBooks.get(0).getPrice());

    // Use the stale read.
    top5LatestBooks = bookDAO.getTop5LatestBooksWithStaleRead(5);
    System.out.println("The latest book price (maybe stale): " + top5LatestBooks.get(0).getPrice());

    // Try to stale read the data at the future time.
    bookDAO.getTop5LatestBooksWithStaleRead(-5);

    // Try to stale read the data before 20 minutes.
    bookDAO.getTop5LatestBooksWithStaleRead(20 * 60);
}
```

The following result shows that the price returned by Stale Read is 100.00, which is the value before the update.

```
The latest book price (before update): 100.00
The latest book price (after update): 150.00
The latest book price (maybe stale): 100.00
WARN: cannot set read timestamp to a future time.
WARN: GC life time is shorter than transaction duration.
```

</div>
