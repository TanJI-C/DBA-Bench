# Batch paging for single-field primary key tables

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-paginate-results.md`
- Source Title: `Paginate Results`
- Source Heading Path: `Paginate Results > Paging batches for single-field primary key tables`
- Source Line Ranges: `71-211`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `batch-processing`, `pagination`, `primary-key`, `row-number`, `window-function`, `delete`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0061_47ac401019`
- Source ID: `tidb-docs-8.1:develop/dev-guide-paginate-results.md#paging-batches-for-single-field-primary-key-tables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f9cd253a0bc8da6886639193b5d4167b8091e1a3aea4e52587dec8fa49a8206a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-paginate-results#paging-batches-for-single-field-primary-key-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-paginate-results.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants a more efficient batch paging method for single-field primary key tables that avoids large OFFSET sorting costs.
- Retrieval Keywords: single-field primary key tables, row_number() OVER (ORDER BY id), floor((t.row_num - 1) / 1000) + 1 AS page_num, start_key, end_key, page_size, WHERE id BETWEEN start_key AND end_key, DELETE FROM books WHERE id BETWEEN 268996 AND 213168525 ORDER BY id, PageMeta, getPageMetaList, deleteBooksByPageMeta
- Follow-up Guidance: It follows up with SQL and Java examples that compute page metadata and then delete books in batches using the start_key and end_key range.
- Classification Note: The chunk is classified as operation because it describes a batch processing method and concrete SQL and Java steps for paging and deleting data by key range.

## Official Source Content

## Paging batches for single-field primary key tables

Usually, you can write a pagination SQL statement using a primary key or unique index to sort results and the `offset` keyword in the `LIMIT` clause to split pages by a specified row count. Then the pages are wrapped into independent transactions to achieve flexible paging updates. However, the disadvantage is also obvious. As the primary key or unique index needs to be sorted, a larger offset consumes more computing resources, especially in the case of a large volume of data.

The following introduces a more efficient paging batching method:

<div label="SQL" value="sql">

First, sort the data by primary key and call the window function `row_number()` to generate a row number for each row. Then, call the aggregation function to group row numbers by the specified page size and calculate the minimum and maximum values of each page.

```sql
SELECT
    floor((t.row_num - 1) / 1000) + 1 AS page_num,
    min(t.id) AS start_key,
    max(t.id) AS end_key,
    count(*) AS page_size
FROM (
    SELECT id, row_number() OVER (ORDER BY id) AS row_num
    FROM books
) t
GROUP BY page_num
ORDER BY page_num;
```

The result is as follows:

```
+----------+------------+------------+-----------+
| page_num | start_key  | end_key    | page_size |
+----------+------------+------------+-----------+
|        1 |     268996 |  213168525 |      1000 |
|        2 |  213210359 |  430012226 |      1000 |
|        3 |  430137681 |  647846033 |      1000 |
|        4 |  647998334 |  848878952 |      1000 |
|        5 |  848899254 | 1040978080 |      1000 |
...
|       20 | 4077418867 | 4294004213 |      1000 |
+----------+------------+------------+-----------+
20 rows in set (0.01 sec)
```

Next, use the `WHERE id BETWEEN start_key AND end_key` statement to query the data of each slice. To update data more efficiently, you can use the above slice information when modifying the data.

To delete the basic information of all books on page 1, replace the `start_key` and `end_key` with values of page 1 in the above result:

```sql
DELETE FROM books
WHERE
    id BETWEEN 268996 AND 213168525
ORDER BY id;
```

</div>
<div label="Java" value="java">

In Java, define a `PageMeta` class to store page meta information.

```java
public class PageMeta<K> {
    private Long pageNum;
    private K startKey;
    private K endKey;
    private Long pageSize;

    // Skip the getters and setters.

}
```

Define a `getPageMetaList()` method to get the page meta information list, and then define a `deleteBooksByPageMeta()` method to delete data in batches according to the page meta information.

```java
public class BookDAO {
    public List<PageMeta<Long>> getPageMetaList() throws SQLException {
        List<PageMeta<Long>> pageMetaList = new ArrayList<>();
        try (Connection conn = ds.getConnection()) {
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("""
            SELECT
                floor((t.row_num - 1) / 1000) + 1 AS page_num,
                min(t.id) AS start_key,
                max(t.id) AS end_key,
                count(*) AS page_size
            FROM (
                SELECT id, row_number() OVER (ORDER BY id) AS row_num
                FROM books
            ) t
            GROUP BY page_num
            ORDER BY page_num;
            """);
            while (rs.next()) {
                PageMeta<Long> pageMeta = new PageMeta<>();
                pageMeta.setPageNum(rs.getLong("page_num"));
                pageMeta.setStartKey(rs.getLong("start_key"));
                pageMeta.setEndKey(rs.getLong("end_key"));
                pageMeta.setPageSize(rs.getLong("page_size"));
                pageMetaList.add(pageMeta);
            }
        }
        return pageMetaList;
    }

    public void deleteBooksByPageMeta(PageMeta<Long> pageMeta) throws SQLException {
        try (Connection conn = ds.getConnection()) {
            PreparedStatement stmt = conn.prepareStatement("DELETE FROM books WHERE id >= ? AND id <= ?");
            stmt.setLong(1, pageMeta.getStartKey());
            stmt.setLong(2, pageMeta.getEndKey());
            stmt.executeUpdate();
        }
    }
}
```

The following statement is to delete the data on page 1:

```java
List<PageMeta<Long>> pageMetaList = bookDAO.getPageMetaList();
if (pageMetaList.size() > 0) {
    bookDAO.deleteBooksByPageMeta(pageMetaList.get(0));
}
```

The following statement is to delete all book data in batches by paging:

```java
List<PageMeta<Long>> pageMetaList = bookDAO.getPageMetaList();
pageMetaList.forEach((pageMeta) -> {
    try {
        bookDAO.deleteBooksByPageMeta(pageMeta);
    } catch (SQLException e) {
        e.printStackTrace();
    }
});
```

</div>

This method significantly improves the efficiency of batch processing by avoiding wasting computing resources caused by frequent data sorting operations.
