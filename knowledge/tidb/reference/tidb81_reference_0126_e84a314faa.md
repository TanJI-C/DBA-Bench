# Clustered index table pagination batches

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-paginate-results.md`
- Source Title: `Paginate Results`
- Source Heading Path: `Paginate Results > Paging batches for composite primary key tables > Clustered index table`
- Source Line Ranges: `258-336`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`
- Topic Tags: `pagination`, `composite-primary-key`, `clustered-index`, `window-functions`, `concat`, `lpad`, `full-table-scan`, `tiflash`, `batch-query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0126_e84a314faa`
- Source ID: `tidb-docs-8.1:develop/dev-guide-paginate-results.md#clustered-index-table`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4816eb8fcba294f1563afcd4a10ecf0a954e1806f1a1854b0edbea613987b4b9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-paginate-results#clustered-index-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-paginate-results.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to paginate a clustered index table with a composite primary key by building fixed-length concatenated keys and deriving page boundaries with a window function.
- Retrieval Keywords: clustered index table, index-organized tables, composite primary key, concat, LPAD, row_number() OVER (ORDER BY book_id, user_id), min(mvalue), max(mvalue), start_key, end_key, page_num, page_size, ratings, TableFullScan, TiFlash, paging batches
- Follow-up Guidance: The chunk also includes an example query that replaces page 1 start_key and end_key values to select rating records in that page ordered by book_id and user_id.
- Classification Note: This is reference content because it provides exact SQL patterns, function names, and retrieval boundary concepts for pagination on clustered index tables.

## Official Source Content

### Clustered index table

For clustered index tables (also known as "index-organized tables"), you can use the `concat` function to concatenate values of multiple columns as a key, and then use a window function to query the paging information.

It should be noted that the key is a string at this time, and you must ensure that the length of the string is always the same, to obtain the correct `start_key` and `end_key` in the slice through the `min` and `max` aggregation function. If the length of the field for string concatenation is not fixed, you can use the `LPAD` function to pad it.

For example, you can implement a paging batch for the data in the `ratings` table as follows:

Create the meta information table by using the following statement. As the key concatenated by `book_id` and `user_id`, which are `bigint` types, is unable to convert to the same length, the `LPAD` function is used to pad the length with `0` according to the maximum bits 19 of `bigint`.

```sql
SELECT
    floor((t1.row_num - 1) / 10000) + 1 AS page_num,
    min(mvalue) AS start_key,
    max(mvalue) AS end_key,
    count(*) AS page_size
FROM (
    SELECT
        concat('(', LPAD(book_id, 19, 0), ',', LPAD(user_id, 19, 0), ')') AS mvalue,
        row_number() OVER (ORDER BY book_id, user_id) AS row_num
    FROM ratings
) t1
GROUP BY page_num
ORDER BY page_num;
```

> **Note:**
>
> The preceding SQL statement is executed as `TableFullScan`. When the data volume is large, the query will be slow, and you can [use TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#use-tiflash) to speed up it.

The result is as follows:

```
+----------+-------------------------------------------+-------------------------------------------+-----------+
| page_num | start_key                                 | end_key                                   | page_size |
+----------+-------------------------------------------+-------------------------------------------+-----------+
|        1 | (0000000000000268996,0000000000092104804) | (0000000000140982742,0000000000374645100) |     10000 |
|        2 | (0000000000140982742,0000000000456757551) | (0000000000287195082,0000000004053200550) |     10000 |
|        3 | (0000000000287196791,0000000000191962769) | (0000000000434010216,0000000000237646714) |     10000 |
|        4 | (0000000000434010216,0000000000375066168) | (0000000000578893327,0000000002167504460) |     10000 |
|        5 | (0000000000578893327,0000000002457322286) | (0000000000718287668,0000000001502744628) |     10000 |
...
|       29 | (0000000004002523918,0000000000902930986) | (0000000004147203315,0000000004090920746) |     10000 |
|       30 | (0000000004147421329,0000000000319181561) | (0000000004294004213,0000000003586311166) |      9972 |
+----------+-------------------------------------------+-------------------------------------------+-----------+
30 rows in set (0.28 sec)
```

To delete all rating records on page 1, replace the `start_key` and `end_key` with values of page 1 in the above result:

```sql
SELECT *
FROM ratings
WHERE (
        268996 = 140982742
        AND book_id = 268996
        AND user_id >= 92104804
        AND user_id <= 374645100
    )
    OR (
        268996 != 140982742
        AND (
            (
                book_id > 268996
                AND book_id < 140982742
            )
            OR (
                book_id = 268996
                AND user_id >= 92104804
            )
            OR (
                book_id = 140982742
                AND user_id <= 374645100
            )
        )
    )
ORDER BY book_id, user_id;
```
