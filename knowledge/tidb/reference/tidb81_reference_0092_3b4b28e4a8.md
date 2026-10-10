# Secondary index example output and follow-up resources

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-create-secondary-indexes.md`
- Source Title: `Create a Secondary Index`
- Source Heading Path: `Create a Secondary Index > Example | Create a Secondary Index > Next step | Create a Secondary Index > Need help?`
- Source Line Ranges: `171-199`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `secondary-index`, `show-index`, `example-output`, `next-steps`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0092_3b4b28e4a8`
- Source ID: `tidb-docs-8.1:develop/dev-guide-create-secondary-indexes.md#example`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e66624193f111d17dad7c0733e313d9c86c499c1dd4d215fd1703f5ffede6ae5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-secondary-indexes#example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-create-secondary-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when someone wants the example SHOW INDEX-style output after creating a secondary index on the books table and the documented next-step links for adding read and write features.
- Retrieval Keywords: books, PRIMARY, idx_book_published_at, published_at, BTREE, Visible, Clustered, SHOW INDEX example output, secondary index example output, Next step, develop/dev-guide-insert-data, develop/dev-guide-get-data-from-single-table, Discord, Slack, support ticket
- Follow-up Guidance: After creating a database and adding tables and secondary indexes to it, you can start adding the data write and read features to your application, and the page also points to Discord, Slack, and support ticket resources.
- Classification Note: This is reference content because it provides a concrete example output table for a secondary index and lists follow-up documentation and support resources from the official page.

## Official Source Content

The following is an example output:

```
+-------+------------+-----------------------+--------------+--------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+-----------+
| Table | Non_unique | Key_name              | Seq_in_index | Column_name  | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment | Visible | Expression | Clustered |
+-------+------------+-----------------------+--------------+--------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+-----------+
| books |          0 | PRIMARY               |            1 | id           | A         |           0 |     NULL | NULL   |      | BTREE      |         |               | YES     | NULL       | YES       |
| books |          1 | idx_book_published_at |            1 | published_at | A         |           0 |     NULL | NULL   |      | BTREE      |         |               | YES     | NULL       | NO        |
+-------+------------+-----------------------+--------------+--------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+-----------+
2 rows in set (1.63 sec)
```
## Next step

After creating a database and adding tables and secondary indexes to it, you can start adding the data [write](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data) and [read](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table) features to your application.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
