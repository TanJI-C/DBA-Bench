# Statistics and plan management statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-overview.md`
- Source Title: `SQL Statement Overview`
- Source Heading Path: `SQL Statement Overview > Statistics and plan management`
- Source Line Ranges: `319-334`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `statistics`, `plan-management`, `analyze`, `bindings`, `explain`, `show-statements`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0619_5a64fb1427`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-overview.md#statistics-and-plan-management`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `41fd457291e27e0452d5b3431505b4bf1beb0bf6ae4c9f2128398c1187e25199`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview#statistics-and-plan-management
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB SQL statement overview for statistics collection, execution plan bindings, EXPLAIN ANALYZE, or SHOW STATS and SHOW BINDINGS statements.
- Retrieval Keywords: Statistics and plan management, ANALYZE TABLE, CREATE BINDING, DROP BINDING, DROP STATS, EXPLAIN ANALYZE, LOAD STATS, SHOW ANALYZE STATUS, SHOW BINDINGS, SHOW STATS_HEALTHY, SHOW STATS_HISTOGRAMS, SHOW STATS_LOCKED, SHOW STATS_META, Collects statistics about a table, Creates an execution plan binding for a SQL statement, Shows created SQL bindings
- Follow-up Guidance: The source points to statement-specific pages for ANALYZE TABLE, CREATE BINDING, DROP BINDING, DROP STATS, EXPLAIN ANALYZE, LOAD STATS, SHOW ANALYZE STATUS, SHOW BINDINGS, SHOW STATS_HEALTHY, SHOW STATS_HISTOGRAMS, SHOW STATS_LOCKED, and SHOW STATS_META.
- Classification Note: This is reference content because it is a tabular overview of SQL statements in the Statistics and plan management section and briefly states what each statement does.

## Official Source Content

## Statistics and plan management

| SQL Statement | Description |
|---------------|-------------|
| [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) | Collects statistics about a table. |
| [`CREATE BINDING`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-binding) | Creates an execution plan binding for a SQL statement. |
| [`DROP BINDING`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-binding) | Drops an execution plan binding from a SQL statement. |
| [`DROP STATS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-stats) | Drops statistics from a table. |
| [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze) | Works similar to `EXPLAIN`, with the major difference that it will execute the statement. |
| [`LOAD STATS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-stats) | Loads statistics into TiDB. |
| [`SHOW ANALYZE STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-analyze-status) | Shows statistics collection tasks. |
| [`SHOW BINDINGS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-bindings) | Shows created SQL bindings. |
| [`SHOW STATS_HEALTHY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-healthy) | Shows an estimation of how accurate statistics are believed to be. |
| [`SHOW STATS_HISTOGRAMS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-histograms) | Shows the histogram information in statistics. |
| [`SHOW STATS_LOCKED`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-locked) | Shows the tables whose statistics are locked. |
| [`SHOW STATS_META`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-meta) | Shows how many rows are in a table and how many rows are changed in that table. |
