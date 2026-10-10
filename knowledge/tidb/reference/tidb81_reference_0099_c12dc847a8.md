# Aggregate queries on a single table

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-get-data-from-single-table.md`
- Source Title: `Query Data from a Single Table`
- Source Heading Path: `Query Data from a Single Table > Aggregate queries`
- Source Line Ranges: `322-399`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `group-by`, `aggregate-functions`, `count`, `distinct`, `order-by`, `sql-example`, `java-example`, `single-table-query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0099_c12dc847a8`
- Source ID: `tidb-docs-8.1:develop/dev-guide-get-data-from-single-table.md#aggregate-queries`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3b808399804c0dcf54c4993926440cebcf799571aaad5508028a38212bd14458`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table#aggregate-queries
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-get-data-from-single-table.md

## Retrieval Guidance

- Use When: Use this chunk when the request is about aggregating rows from a single table with GROUP BY, COUNT(DISTINCT), and ORDER BY, including the authors and birth_year example.
- Retrieval Keywords: GROUP BY, COUNT(DISTINCT id), ORDER BY author_count DESC, authors, birth_year, author_count, SELECT birth_year, COUNT(DISTINCT id) AS author_count FROM authors GROUP BY birth_year ORDER BY author_count DESC, Aggregate queries on a single table, Aggregate (GROUP BY) Functions, Java ResultSet getShort("birth_year"), Java ResultSet getInt("author_count"), getAuthorCountsByBirthYear
- Follow-up Guidance: The source also notes that TiDB supports aggregate functions beyond COUNT and points to Aggregate (GROUP BY) Functions for more information.
- Classification Note: This is reference content because it shows a concrete SQL and Java example for single-table aggregate queries using GROUP BY and COUNT(DISTINCT).

## Official Source Content

## Aggregate queries

To have a better understanding of the overall data situation, you can use the `GROUP BY` statement to aggregate query results.

For example, if you want to know which years there are more authors born, you can group the `authors` table by the `birth_year` column, and then count for each year:

<div label="SQL" value="sql">

```sql
SELECT birth_year, COUNT (DISTINCT id) AS author_count
FROM authors
GROUP BY birth_year
ORDER BY author_count DESC;
```

</div>

<div label="Java" value="java">

```java
public class AuthorCount {
    private Short birthYear;
    private Integer authorCount;

    public AuthorCount() {}

     // Skip the getters and setters.
}

public List<AuthorCount> getAuthorCountsByBirthYear() throws SQLException {
    List<AuthorCount> authorCounts = new ArrayList<>();
    try (Connection conn = ds.getConnection()) {
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("""
            SELECT birth_year, COUNT(DISTINCT id) AS author_count
            FROM authors
            GROUP BY birth_year
            ORDER BY author_count DESC;
            """);

        while (rs.next()) {
            AuthorCount authorCount = new AuthorCount();
            authorCount.setBirthYear(rs.getShort("birth_year"));
            authorCount.setAuthorCount(rs.getInt("author_count"));
            authorCounts.add(authorCount);
        }
    }
    return authorCount;
}
```

</div>

The result is as follows:

```
+------------+--------------+
| birth_year | author_count |
+------------+--------------+
|       1932 |          317 |
|       1947 |          290 |
|       1939 |          282 |
|       1935 |          289 |
|       1968 |          291 |
|       1962 |          261 |
|       1961 |          283 |
|       1986 |          289 |
|       1994 |          280 |
...
|       1972 |          306 |
+------------+--------------+
71 rows in set (0.00 sec)
```

In addition to the `COUNT` function, TiDB also supports other aggregate functions. For more information, see [Aggregate (GROUP BY) Functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/aggregate-group-by-functions).
