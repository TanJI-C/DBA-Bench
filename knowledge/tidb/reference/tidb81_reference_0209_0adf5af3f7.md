# View, query, and drop temporary tables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-use-temporary-tables.md`
- Source Title: `Temporary Tables`
- Source Heading Path: `Temporary Tables > View temporary tables | Temporary Tables > Query a temporary table | Temporary Tables > Drop a temporary table | Temporary Tables > Limitation | Temporary Tables > Read more | Temporary Tables > Need help?`
- Source Line Ranges: `197-273`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `temporary-tables`, `show-tables`, `query`, `join`, `performance`, `drop-table`, `cleanup`, `limitations`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0209_0adf5af3f7`
- Source ID: `tidb-docs-8.1:develop/dev-guide-use-temporary-tables.md#view-temporary-tables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ec603d15717e78c98dcc3945816bf5e6acec3497ae1776392f809946f69d0ecc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-temporary-tables#view-temporary-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-use-temporary-tables.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants to know how to list, query, join, or drop temporary tables in TiDB, or needs the documented visibility and cleanup behavior for local versus global temporary tables.
- Retrieval Keywords: SHOW FULL TABLES, information_schema.INNODB_TEMP_TABLE_INFO, global temporary tables visible in table list, local temporary tables not shown, SELECT * FROM top_50_eldest_authors, EXPLAIN SELECT ANY_VALUE, LEFT JOIN book_authors, temporary table query performance, DROP TEMPORARY TABLE, DROP GLOBAL TEMPORARY TABLE, top_50_eldest_authors_global, session ends, transaction ends, Compatibility restrictions with other TiDB features
- Follow-up Guidance: The source points to the Temporary Tables page for compatibility restrictions with other TiDB features.
- Classification Note: This is classified as reference content because it documents exact statements and documented behavior for viewing, querying, joining, and dropping temporary tables, plus stated limitations.

## Official Source Content

## View temporary tables

With the `SHOW [FULL] TABLES` statement, you can view a list of existing global temporary tables, but you cannot see any local temporary tables in the list. For now, TiDB does not have a similar `information_schema.INNODB_TEMP_TABLE_INFO` system table for storing temporary table information.

For example, you can see the global temporary table `top_50_eldest_authors_global` in the table list, but not the `top_50_eldest_authors` table.

```
+-------------------------------+------------+
| Tables_in_bookshop            | Table_type |
+-------------------------------+------------+
| authors                       | BASE TABLE |
| book_authors                  | BASE TABLE |
| books                         | BASE TABLE |
| orders                        | BASE TABLE |
| ratings                       | BASE TABLE |
| top_50_eldest_authors_global  | BASE TABLE |
| users                         | BASE TABLE |
+-------------------------------+------------+
9 rows in set (0.00 sec)
```
## Query a temporary table

Once the temporary table is ready, you can query it as a normal data table:

```sql
SELECT * FROM top_50_eldest_authors;
```

You can reference data from temporary tables to your query via [Multi-table join queries](https://docs.pingcap.com/tidb/stable/develop/dev-guide-join-tables):

```sql
EXPLAIN SELECT ANY_VALUE(ta.id) AS author_id, ANY_VALUE(ta.age), ANY_VALUE(ta.name), COUNT(*) AS books
FROM top_50_eldest_authors ta
LEFT JOIN book_authors ba ON ta.id = ba.author_id
GROUP BY ta.id;
```

Different from [view](https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-views), querying a temporary table gets data directly from the temporary table instead of executing the original query used in the data insert. In some cases, this can improve the query performance.
## Drop a temporary table

A local temporary table in a session is automatically dropped after the **session** ends, along with both data and table schema. A global temporary table in a transaction is automatically cleared at the end of the **transaction**, but the table schema remains and needs to be deleted manually.

To manually drop local temporary tables, use the `DROP TABLE` or `DROP TEMPORARY TABLE` syntax. For example:

```sql
DROP TEMPORARY TABLE top_50_eldest_authors;
```

To manually drop global temporary tables, use the `DROP TABLE` or `DROP GLOBAL TEMPORARY TABLE` syntax. For example:

```sql
DROP GLOBAL TEMPORARY TABLE top_50_eldest_authors_global;
```
## Limitation

For limitations of temporary tables in TiDB, see [Compatibility restrictions with other TiDB features](https://docs.pingcap.com/tidb/stable/temporary-tables#compatibility-restrictions-with-other-tidb-features).
## Read more

- [Temporary Tables](https://docs.pingcap.com/tidb/stable/temporary-tables)
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
