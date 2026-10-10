# View RU consumption for SQL statements

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-resource-control.md`
- Source Title: `Use Resource Control to Achieve Resource Isolation`
- Source Heading Path: `Use Resource Control to Achieve Resource Isolation > View RU consumption | Use Resource Control to Achieve Resource Isolation > View RU consumption > View the RU consumption by SQL | Use Resource Control to Achieve Resource Isolation > View RU consumption > View the RU consumption by SQL > View the RUs consumed by the last SQL execution by querying the system variable `tidb_last_query_info` | Use Resource Control to Achieve Resource Isolation > View RU consumption > View the RU consumption by SQL > View RUs consumed during SQL execution by `EXPLAIN ANALYZE` | Use Resource Control to Achieve Resource Isolation > View RU consumption > View the RU consumption by SQL > Slow queries and the corresponding system table | Use Resource Control to Achieve Resource Isolation > View RU consumption > View the RU consumption by SQL > View RU statistics by `statements_summary``
- Source Line Ranges: `517-585`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `ru`, `sql-observability`, `last-query-info`, `explain-analyze`, `slow-query`, `statements-summary`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0112_f3f35c1891`
- Source ID: `tidb-docs-8.1:tidb-resource-control.md#view-ru-consumption`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2ba3316216a93923bdf6262474c987f9187ae0b27a8c5938e491d15d2529419`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-resource-control#view-ru-consumption
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-resource-control.md

## Retrieval Guidance

- Use When: Use this content when looking up where RU consumption of SQL statements can be viewed, including the last executed DML, `EXPLAIN ANALYZE`, slow query data, and `statements_summary`.
- Retrieval Keywords: tidb_last_query_info, SELECT @@tidb_last_query_info, ru_consumption, EXPLAIN ANALYZE, INFORMATION_SCHEMA.SLOW_QUERY, slow query log, INFORMATION_SCHEMA.statements_summary, resource group name, time spent waiting for available RUs, View RU consumption
- Follow-up Guidance: The example shows querying `@@tidb_last_query_info` after an `UPDATE`, and the page also points to `EXPLAIN ANALYZE`, `INFORMATION_SCHEMA.SLOW_QUERY`, and `INFORMATION_SCHEMA.statements_summary` for RU-related fields.
- Classification Note: This is classified as observability because the content focuses on viewing and analyzing RU consumption metrics and related SQL execution information from system variables, logs, and system tables.

## Official Source Content

## View RU consumption

You can view information about RU consumption.
### View the RU consumption by SQL

You can view the RU consumption of SQL statements in the following ways:

- The system variable `tidb_last_query_info`
- `EXPLAIN ANALYZE`
- Slow queries and corresponding system table
- `statements_summary`
#### View the RUs consumed by the last SQL execution by querying the system variable `tidb_last_query_info`

TiDB provides the system variable [`tidb_last_query_info`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_last_query_info-new-in-v4014). This system variable records the information of the last DML statement executed, including the RUs consumed by the SQL execution.

Example:

1. Run the `UPDATE` statement:

    ```sql
    UPDATE sbtest.sbtest1 SET k = k + 1 WHERE id = 1;
    ```

    ```
    Query OK, 1 row affected (0.01 sec)
    Rows matched: 1  Changed: 1  Warnings: 0
    ```

2. Query the system variable `tidb_last_query_info` to view the information of the last executed statement:

    ```sql
    SELECT @@tidb_last_query_info;
    ```

    ```
    +------------------------------------------------------------------------------------------------------------------------+
    | @@tidb_last_query_info                                                                                                 |
    +------------------------------------------------------------------------------------------------------------------------+
    | {"txn_scope":"global","start_ts":446809472210829315,"for_update_ts":446809472210829315,"ru_consumption":4.34885578125} |
    +------------------------------------------------------------------------------------------------------------------------+
    1 row in set (0.01 sec)
    ```

    In the result, `ru_consumption` is the RUs consumed by the execution of this SQL statement.
#### View RUs consumed during SQL execution by `EXPLAIN ANALYZE`

You can use the [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze#ru-request-unit-consumption) statement to get the amount of RUs consumed during SQL execution. Note that the amount of RUs is affected by the cache (for example, [coprocessor cache](https://docs.pingcap.com/tidb/stable/coprocessor-cache)). When the same SQL is executed multiple times, the amount of RUs consumed by each execution might be different. The RU value does not represent the exact value for each execution, but can be used as a reference for estimation.
#### Slow queries and the corresponding system table

When you enable resource control, the [slow query log](https://docs.pingcap.com/tidb/stable/identify-slow-queries) of TiDB and the corresponding system table [`INFORMATION_SCHEMA.SLOW_QUERY`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-slow-query) contain the resource group, RU consumption of the corresponding SQL, and the time spent waiting for available RUs.

When you enable resource control, the system table [`INFORMATION_SCHEMA.SLOW_QUERY`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-slow-query) contains the resource group, RU consumption of the corresponding SQL, and the time spent waiting for available RUs.
#### View RU statistics by `statements_summary`

The system table [`INFORMATION_SCHEMA.statements_summary`](https://docs.pingcap.com/tidb/stable/statement-summary-tables#statements_summary) in TiDB stores the normalized and aggregated statistics of SQL statements. You can use the system table to view and analyze the execution performance of SQL statements. It also contains statistics about resource control, including the resource group name, RU consumption, and the time spent waiting for available RUs. For more details, see [`statements_summary` fields description](https://docs.pingcap.com/tidb/stable/statement-summary-tables#statements_summary-fields-description).
