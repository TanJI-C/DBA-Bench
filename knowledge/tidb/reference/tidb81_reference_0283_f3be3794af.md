# SHOW PROCESSLIST session ID behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/sql-faq.md`
- Source Title: `SQL FAQs`
- Source Heading Path: `SQL FAQs > Does `SHOW PROCESSLIST` display the system process ID?`
- Source Line Ranges: `195-201`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show-processlist`, `session-id`, `mysql-compatibility`, `stateless`, `parallel-query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0283_f3be3794af`
- Source ID: `tidb-docs-8.1:faq/sql-faq.md#does-show-processlist-display-the-system-process-id`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e3abf15e08e80137b74222631c6c51b714497671b2e27e0445395bfb7a24846`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/sql-faq#does-show-processlist-display-the-system-process-id
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/sql-faq.md

## Retrieval Guidance

- Use When: Use this chunk when clarifying what TiDB `SHOW PROCESSLIST` displays, especially whether the ID is a system process ID or a session ID and why results differ from MySQL.
- Retrieval Keywords: SHOW PROCESSLIST, TiDB SHOW PROCESSLIST, system process ID, current session ID, MySQL compatibility, tidb-server stateless engine, session list executed in the tidb-server instance, State column not continually updated, parallel query
- Follow-up Guidance: The source explains that `SHOW PROCESSLIST` shows sessions only for the `tidb-server` instance the user logs in to, and that the `State` column is not continually updated because a statement might be in multiple states at once.
- Classification Note: This is classified as reference content because it defines the displayed fields and behavior of the `SHOW PROCESSLIST` SQL statement in TiDB.

## Official Source Content

## Does `SHOW PROCESSLIST` display the system process ID?

The display content of TiDB `SHOW PROCESSLIST` is almost the same as that of MySQL `SHOW PROCESSLIST`. TiDB `SHOW PROCESSLIST` does not display the system process ID. The ID that it displays is the current session ID. The differences between TiDB `SHOW PROCESSLIST` and MySQL `SHOW PROCESSLIST` are as follows:

- As TiDB is a distributed database, the `tidb-server` instance is a stateless engine for parsing and executing the SQL statements (for details, see [TiDB architecture](https://docs.pingcap.com/tidb/stable/tidb-architecture)). `SHOW PROCESSLIST` displays the session list executed in the `tidb-server` instance that the user logs in to from the MySQL client, not the list of all the sessions running in the cluster. But MySQL is a standalone database and its `SHOW PROCESSLIST` displays all the SQL statements executed in MySQL.
- The `State` column in TiDB is not continually updated during query execution. Because TiDB supports parallel query, each statement might be in multiple _states_ at once, and so it is difficult to simplify to a single value.
