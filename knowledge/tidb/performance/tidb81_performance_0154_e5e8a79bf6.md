# Performance feature details for TiFlash and TiDB

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.2.0.md`
- Source Title: `TiDB 7.2.0 Release Notes`
- Source Heading Path: `TiDB 7.2.0 Release Notes > Feature details > Performance`
- Source Line Ranges: `50-84`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `sql`
- Topic Tags: `window-functions`, `pushdown`, `pipeline-execution`, `schema-replication`, `statistics-collection`, `admin-check`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0154_e5e8a79bf6`
- Source ID: `tidb-docs-8.1:releases/release-7.2.0.md#performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0915f4eb5f26c7bd28491f9530119217a8ce81b1a7a5a2c29239409ddf1f440f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.2.0#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB 7.2.0 performance improvements related to TiFlash execution, window function pushdown, statistics collection, schema replication, or fast consistency checking.
- Retrieval Keywords: Performance, FIRST_VALUE, LAST_VALUE, TiFlash supported pushdown calculations, pipeline execution model, tidb_enable_tiflash_pipeline_model, schema replication, tables with TiFlash replicas, statistics collection, tidb_analyze_skip_column_types, JSON BLOB MEDIUMBLOB LONGBLOB TEXT, ADMIN CHECK TABLE, ADMIN CHECK INDEX, tidb_enable_fast_table_check
- Follow-up Guidance: Follow up with the related system variables or SQL statement details, such as tidb_enable_tiflash_pipeline_model, tidb_analyze_skip_column_types, or ADMIN CHECK [TABLE|INDEX], when the user asks how these features are controlled or identified.
- Classification Note: This is classified as a performance chunk because the official content lists performance-related enhancements for TiFlash and TiDB, including execution model, pushdown, schema replication, statistics collection, and data consistency checking.

## Official Source Content

### Performance

* Support pushing down the following two [window functions](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations) to TiFlash [#7427](https://github.com/pingcap/tiflash/issues/7427) @[xzhangxian1008](https://github.com/xzhangxian1008)

    * `FIRST_VALUE`
    * `LAST_VALUE`

* TiFlash supports the pipeline execution model (experimental) [#6518](https://github.com/pingcap/tiflash/issues/6518) @[SeaRise](https://github.com/SeaRise)

    Prior to v7.2.0, each task in the TiFlash engine must individually request thread resources during execution. TiFlash controls the number of tasks to limit thread resource usage and prevent overuse, but this issue could not be completely eliminated. To address this problem, starting from v7.2.0, TiFlash introduces a pipeline execution model. This model centrally manages all thread resources and schedules task execution uniformly, maximizing the utilization of thread resources while avoiding resource overuse. To enable or disable the pipeline execution model, modify the [`tidb_enable_tiflash_pipeline_model`](https://docs.pingcap.com/tidb/v7.2/system-variables#tidb_enable_tiflash_pipeline_model-new-in-v720) system variable.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-pipeline-model).

* TiFlash reduces the latency of schema replication [#7630](https://github.com/pingcap/tiflash/issues/7630) @[hongyunyan](https://github.com/hongyunyan)

    When the schema of a table changes, TiFlash needs to replicate the latest schema from TiKV in a timely manner. Before v7.2.0, when TiFlash accesses table data and detects a table schema change within a database, TiFlash needs to replicate the schemas of all tables in this database again, including those tables without TiFlash replicas. As a result, in a database with a large number of tables, even if you only need to read data from a single table using TiFlash, you might experience significant latency to wait for TiFlash to complete the schema replication of all tables.

    In v7.2.0, TiFlash optimizes the schema replication mechanism and supports only replicating schemas of tables with TiFlash replicas. When a schema change is detected for a table with TiFlash replicas, TiFlash only replicates the schema of that table, which reduces the latency of schema replication of TiFlash and minimizes the impact of DDL operations on TiFlash data replication. This optimization is automatically applied and does not require any manual configuration.

* Improve the performance of statistics collection [#44725](https://github.com/pingcap/tidb/issues/44725) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)

    TiDB v7.2.0 optimizes the statistics collection strategy, skipping some of the duplicate information and information that is of little value to the optimizer. The overall speed of statistics collection has been improved by 30%. This improvement allows TiDB to update the statistics of the database in a more timely manner, making the generated execution plans more accurate, thus improving the overall database performance.

    By default, statistics collection skips the columns of the `JSON`, `BLOB`, `MEDIUMBLOB`, and `LONGBLOB` types. You can modify the default behavior by setting the [`tidb_analyze_skip_column_types`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_skip_column_types-new-in-v720) system variable. TiDB supports skipping the `JSON`, `BLOB`, and `TEXT` types and their subtypes.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_skip_column_types-new-in-v720).

* Improve the performance of checking data and index consistency [#43693](https://github.com/pingcap/tidb/issues/43693) @[wjhuang2016](https://github.com/wjhuang2016)

    The [`ADMIN CHECK [TABLE|INDEX]`](/sql-statements/sql-statement-admin-check-table-index.md) statement is used to check the consistency between data in a table and its corresponding indexes. In v7.2.0, TiDB optimizes the method for checking data consistency and improves the execution efficiency of [`ADMIN CHECK [TABLE|INDEX]`](/sql-statements/sql-statement-admin-check-table-index.md) greatly. In scenarios with large amounts of data, this optimization can provide a performance boost of hundreds of times.

    The optimization is enabled by default ([`tidb_enable_fast_table_check`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_fast_table_check-new-in-v720) is `ON` by default) to greatly reduce the time required for data consistency checks in large-scale tables and enhance operational efficiency.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_fast_table_check-new-in-v720).
