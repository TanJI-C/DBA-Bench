# Paginate query results with LIMIT

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-paginate-results.md`
- Source Title: `Paginate Results`
- Source Heading Path: `Paginate Results | Paginate Results > Paginate query results`
- Source Line Ranges: `5-70`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `pagination`, `limit`, `offset`, `order-by`, `sql`, `java`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0124_066b3c620f`
- Source ID: `tidb-docs-8.1:develop/dev-guide-paginate-results.md#paginate-results`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9ad1163b746810a84e54faeafceeeabae61bd63c154f57e98d6543c9e928aa6b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-paginate-results#paginate-results
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-paginate-results.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs SQL or Java examples for paginating query results with LIMIT, OFFSET, and ORDER BY.
- Retrieval Keywords: LIMIT offset, row_count, LIMIT row_count OFFSET offset, ORDER BY, SELECT * FROM table_a t ORDER BY gmt_modified DESC LIMIT offset, row_count, SELECT * FROM books ORDER BY published_at DESC LIMIT 0, 10, page_number, page_size, PreparedStatement, LIMIT ?, ?, getLatestBooksPage
- Follow-up Guidance: It also shows a Java method that converts page_number and page_size to offset and limit before executing a paginated SELECT on books.
- Classification Note: The chunk is classified as reference because it explains LIMIT-based pagination syntax and gives example queries and application code.

## Official Source Content

# Paginate Results

To page through a large query result, you can get your desired part in a "paginated" manner.
## Paginate query results

In TiDB, you can paginate query results using the `LIMIT` statement. For example:

```sql
SELECT * FROM table_a t ORDER BY gmt_modified DESC LIMIT offset, row_count;
```

`offset` indicates the beginning number of records and `row_count` indicates the number of records per page. TiDB also supports `LIMIT row_count OFFSET offset` syntax.

When pagination is used, it is recommended that you sort query results with the `ORDER BY` statement unless there is a need to display data randomly.

<div label="SQL" value="sql">

For example, to let users of the [Bookshop](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design) application view the latest published books in a paginated manner, you can use the `LIMIT 0, 10` statement, which returns the first page of the result list, with a maximum of 10 records per page. To get the second page, you can change the statement to `LIMIT 10, 10`.

```sql
SELECT *
FROM books
ORDER BY published_at DESC
LIMIT 0, 10;
```

</div>
<div label="Java" value="java">

In application development, the backend program receives the `page_number` parameter (which means the number of the page being requested) and the `page_size` parameter (which controls how many records per page) from the frontend instead of the `offset` parameter. Therefore, some conversions needed to be done before querying.

```java
public List<Book> getLatestBooksPage(Long pageNumber, Long pageSize) throws SQLException {
    pageNumber = pageNumber < 1L ? 1L : pageNumber;
    pageSize = pageSize < 10L ? 10L : pageSize;
    Long offset = (pageNumber - 1) * pageSize;
    Long limit = pageSize;
    List<Book> books = new ArrayList<>();
    try (Connection conn = ds.getConnection()) {
        PreparedStatement stmt = conn.prepareStatement("""
        SELECT id, title, published_at
        FROM books
        ORDER BY published_at DESC
        LIMIT ?, ?;
        """);
        stmt.setLong(1, offset);
        stmt.setLong(2, limit);
        ResultSet rs = stmt.executeQuery();
        while (rs.next()) {
            Book book = new Book();
            book.setId(rs.getLong("id"));
            book.setTitle(rs.getString("title"));
            book.setPublishedAt(rs.getDate("published_at"));
            books.add(book);
        }
    }
    return books;
}
```

</div>
