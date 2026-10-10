# Batch paging for composite primary key tables using _tidb_rowid

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-paginate-results.md`
- Source Title: `Paginate Results`
- Source Heading Path: `Paginate Results > Paging batches for composite primary key tables | Paginate Results > Paging batches for composite primary key tables > Non-clustered index table`
- Source Line Ranges: `212-257`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `composite-primary-key`, `non-clustered-index`, `_tidb_rowid`, `pagination`, `row-number`, `show-create-table`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0125_a116ff883d`
- Source ID: `tidb-docs-8.1:develop/dev-guide-paginate-results.md#paging-batches-for-composite-primary-key-tables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `af4c212b1cfb1731f54e57060935512d834a08171802a56be3da48b96327a052`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-paginate-results#paging-batches-for-composite-primary-key-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-paginate-results.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs batch paging guidance for composite primary key tables that are non-clustered index tables and can use _tidb_rowid as the pagination key.
- Retrieval Keywords: composite primary key tables, Non-clustered index table, non-index-organized tables, _tidb_rowid, SHOW CREATE TABLE users;, clustered index, row_number () OVER (ORDER BY _tidb_rowid), min(t._tidb_rowid) AS start_key, max(t._tidb_rowid) AS end_key, FROM users
- Follow-up Guidance: It notes that SHOW CREATE TABLE users; can be used to check whether the table primary key uses clustered index.
- Classification Note: The chunk is classified as reference because it documents the pagination key and example query for non-clustered index tables using _tidb_rowid.

## Official Source Content

## Paging batches for composite primary key tables
### Non-clustered index table

For non-clustered index tables (also known as "non-index-organized tables"), the internal field `_tidb_rowid` can be used as a pagination key, and the pagination method is the same as that of single-field primary key tables.

> **Tip:**
>
> You can use the `SHOW CREATE TABLE users;` statement to check whether the table primary key uses [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes).

For example:

```sql
SELECT
    floor((t.row_num - 1) / 1000) + 1 AS page_num,
    min(t._tidb_rowid) AS start_key,
    max(t._tidb_rowid) AS end_key,
    count(*) AS page_size
FROM (
    SELECT _tidb_rowid, row_number () OVER (ORDER BY _tidb_rowid) AS row_num
    FROM users
) t
GROUP BY page_num
ORDER BY page_num;
```

The result is as follows:

```
+----------+-----------+---------+-----------+
| page_num | start_key | end_key | page_size |
+----------+-----------+---------+-----------+
|        1 |         1 |    1000 |      1000 |
|        2 |      1001 |    2000 |      1000 |
|        3 |      2001 |    3000 |      1000 |
|        4 |      3001 |    4000 |      1000 |
|        5 |      4001 |    5000 |      1000 |
|        6 |      5001 |    6000 |      1000 |
|        7 |      6001 |    7000 |      1000 |
|        8 |      7001 |    8000 |      1000 |
|        9 |      8001 |    9000 |      1000 |
|       10 |      9001 |    9990 |       990 |
+----------+-----------+---------+-----------+
10 rows in set (0.00 sec)
```
