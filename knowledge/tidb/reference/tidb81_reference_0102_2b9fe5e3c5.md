# Workbench timeout FAQ and follow-up resources

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-gui-mysql-workbench.md`
- Source Title: `Connect to TiDB with MySQL Workbench`
- Source Heading Path: `Connect to TiDB with MySQL Workbench > FAQs | Connect to TiDB with MySQL Workbench > FAQs > How to handle the connection timeout error "Error Code: 2013. Lost connection to MySQL server during query"? | Connect to TiDB with MySQL Workbench > Next steps | Connect to TiDB with MySQL Workbench > Need help?`
- Source Line Ranges: `154-185`
- Source Scope: `all`
- Primary Component: `ecosystem`
- Related Components: `sql`
- Topic Tags: `timeout`, `faq`, `workbench preferences`, `support`, `community`, `documentation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0102_2b9fe5e3c5`
- Source ID: `tidb-docs-8.1:develop/dev-guide-gui-mysql-workbench.md#faqs`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bedf9275463fdc8c8369c38fe1f3e644310f9d30e2feefbf2b8c5456aae1d2ec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-mysql-workbench#faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-gui-mysql-workbench.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about the MySQL Workbench timeout error "Error Code: 2013. Lost connection to MySQL server during query" or wants follow-up learning and support resources after connecting.
- Retrieval Keywords: Error Code: 2013. Lost connection to MySQL server during query, Workbench Preferences, SQL Editor, MySQL Session, DBMS connection read timeout interval (in seconds), MySQL Workbench frequently asked questions, Next steps, Developer guide, Insert data, Update data, Delete data, Single table reading, Transactions, SQL performance optimization, Discord, Slack, submit a support ticket
- Follow-up Guidance: The source points to MySQL Workbench documentation, TiDB Developer guide chapters, TiDB developer courses and certifications, and community or support channels including Discord, Slack, and support tickets.
- Classification Note: This is classified as reference because the content provides an FAQ explanation for a specific timeout error plus documentation, learning, and help links rather than core setup steps.

## Official Source Content

## FAQs
### How to handle the connection timeout error "Error Code: 2013. Lost connection to MySQL server during query"?

This error indicates that the query execution time exceeds the timeout limit. To resolve this issue, you can adjust the timeout settings by the following steps:

1. Launch MySQL Workbench and navigate to the **Workbench Preferences** page.
2. In the **SQL Editor** > **MySQL Session** section, configure the **DBMS connection read timeout interval (in seconds)** option. This sets the maximum amount of time (in seconds) that a query can take before MySQL Workbench disconnects from the server.

    ![MySQL Workbench: adjust timeout option in SQL Editor settings](/media/develop/mysql-workbench-adjust-sqleditor-read-timeout.jpg)

For more information, see [MySQL Workbench frequently asked questions](https://dev.mysql.com/doc/workbench/en/workbench-faq.html).
## Next steps

- Learn more usage of MySQL Workbench from [the documentation of MySQL Workbench](https://dev.mysql.com/doc/workbench/en/).
- Learn the best practices for TiDB application development with the chapters in the [Developer guide](https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview), such as [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data), [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data), [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data), [Single table reading](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table), [Transactions](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview), and [SQL performance optimization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview).
- Learn through the professional [TiDB developer courses](https://www.pingcap.com/education/) and earn [TiDB certifications](https://www.pingcap.com/education/certification/) after passing the exam.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
