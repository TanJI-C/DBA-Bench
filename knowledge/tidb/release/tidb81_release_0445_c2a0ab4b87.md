# SQL feature details in v7.1.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.0.md`
- Source Title: `TiDB 7.1.0 Release Notes`
- Source Heading Path: `TiDB 7.1.0 Release Notes > Feature details > SQL`
- Source Line Ranges: `202-239`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`
- Topic Tags: `sql`, `tiflash`, `insert-into-select`, `ga`, `multi-valued-indexes`, `json`, `partitioning`, `generated-columns`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0445_c2a0ab4b87`
- Source ID: `tidb-docs-8.1:releases/release-7.1.0.md#sql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9d898eead25826f6f18972adc4dc5eafa37e68844a2f50114e107ad11e436755`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.0#sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.0 SQL feature changes such as TiFlash `INSERT INTO SELECT` GA behavior, multi-valued indexes on JSON arrays, partition management additions, Range INTERVAL partitioning GA, or generated columns GA.
- Retrieval Keywords: TiDB 7.1.0 SQL feature details, INSERT INTO SELECT, TiFlash query results, result materialization, tidb_enable_tiflash_read_for_write_stmt, sql_mode, STRICT_TRANS_TABLES, STRICT_ALL_TABLES, multi-valued indexes, JSON column, MEMBER OF(), JSON_CONTAINS(), JSON_OVERLAPS(), Hash partitioned tables, Key partitioned tables, ADD PARTITION, COALESCE PARTITION, TRUNCATE PARTITION, Range INTERVAL partitioning, generated columns, virtual column, stored column
- Follow-up Guidance: The content points to documentation for TiFlash results materialization, multi-valued indexes, managing Hash and Key partitions, Range INTERVAL partitioning, and generated columns.
- Classification Note: This is classified as a release SQL chunk because it enumerates SQL-related features that become GA or gain new syntax or partition-management support in TiDB 7.1.0.

## Official Source Content

### SQL

* Support saving TiFlash query results using the `INSERT INTO SELECT` statement (GA) [#37515](https://github.com/pingcap/tidb/issues/37515) @[gengliqi](https://github.com/gengliqi)

    Starting from v6.5.0, TiDB supports pushing down the `SELECT` clause (analytical query) of the `INSERT INTO SELECT` statement to TiFlash. In this way, you can easily save the TiFlash query result to a TiDB table specified by `INSERT INTO` for further analysis, which takes effect as result caching (that is, result materialization).

    In v7.1.0, this feature is generally available. During the execution of the `SELECT` clause in the `INSERT INTO SELECT` statement, the optimizer can intelligently decide whether to push a query down to TiFlash based on the [SQL mode](https://docs.pingcap.com/tidb/stable/sql-mode) and the cost estimates of the TiFlash replica. Therefore, the `tidb_enable_tiflash_read_for_write_stmt` system variable introduced during the experimental phase is now deprecated. Note that the computation rules of `INSERT INTO SELECT` statements for TiFlash do not meet the `STRICT SQL Mode` requirement, so TiDB allows the `SELECT` clause in the `INSERT INTO SELECT` statement to be pushed down to TiFlash only when the [SQL mode](https://docs.pingcap.com/tidb/stable/sql-mode) of the current session is not strict, which means that the `sql_mode` value does not contain `STRICT_TRANS_TABLES` and `STRICT_ALL_TABLES`.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-results-materialization).

* MySQL-compatible multi-valued indexes become generally available (GA) [#39592](https://github.com/pingcap/tidb/issues/39592) @[xiongjiwei](https://github.com/xiongjiwei) @[qw4990](https://github.com/qw4990) @[YangKeao](https://github.com/YangKeao)

    Filtering the values of an array in a JSON column is a common operation, but normal indexes cannot help speed up such an operation. Creating a multi-valued index on an array can greatly improve filtering performance. If an array in the JSON column has a multi-valued index, you can use the multi-valued index to filter retrieval conditions in `MEMBER OF()`, `JSON_CONTAINS()`, and `JSON_OVERLAPS()` functions, thereby reducing I/O consumption and improving operation speed.

    In v7.1.0, the multi-valued indexes feature becomes generally available (GA). It supports more complete data types and is compatible with TiDB tools. You can use multi-valued indexes to speed up the search operations on JSON arrays in production environments.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#multi-valued-indexes).

* Improve the partition management for Hash and Key partitioned tables [#42728](https://github.com/pingcap/tidb/issues/42728) @[mjonss](https://github.com/mjonss)

    Before v7.1.0, Hash and Key partitioned tables in TiDB only support the `TRUNCATE PARTITION` partition management statement. Starting from v7.1.0, Hash and Key partitioned tables also support `ADD PARTITION` and `COALESCE PARTITION` partition management statements. Therefore, you can flexibly adjust the number of partitions in Hash and Key partitioned tables as needed. For example, you can increase the number of partitions with the `ADD PARTITION` statement, or decrease the number of partitions with the `COALESCE PARTITION` statement.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/partitioned-table#manage-hash-and-key-partitions).

* The syntax of Range INTERVAL partitioning becomes generally available (GA) [#35683](https://github.com/pingcap/tidb/issues/35683) @[mjonss](https://github.com/mjonss)

    The syntax of Range INTERVAL partitioning (introduced in v6.3.0) becomes GA. With this syntax, you can define Range partitioning by a desired interval without enumerating all partitions, which drastically reduces the length of Range partitioning DDL statements. The syntax is equivalent to that of the original Range partitioning.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/partitioned-table#range-interval-partitioning).

* Generated columns become generally available (GA) @[bb7133](https://github.com/bb7133)

    Generated columns are a valuable feature for a database. When creating a table, you can define that the value of a column is calculated based on the values of other columns in the table, rather than being explicitly inserted or updated by users. This generated column can be either a virtual column or a stored column. TiDB has supported MySQL-compatible generated columns since earlier versions, and this feature becomes GA in v7.1.0.

    Using generated columns can improve MySQL compatibility for TiDB, simplifying the process of migrating from MySQL. It also reduces data maintenance complexity and improves data consistency and query efficiency.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/generated-columns).
