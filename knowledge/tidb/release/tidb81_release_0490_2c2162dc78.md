# SQL, DDL, data migration, and compatibility changes in v7.2.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.2.0.md`
- Source Title: `TiDB 7.2.0 Release Notes`
- Source Heading Path: `TiDB 7.2.0 Release Notes > Feature details > SQL | TiDB 7.2.0 Release Notes > Feature details > DB operations | TiDB 7.2.0 Release Notes > Feature details > Data migration | TiDB 7.2.0 Release Notes > Compatibility changes | TiDB 7.2.0 Release Notes > Compatibility changes > Behavior changes`
- Source Line Ranges: `126-177`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `lightning`, `ticdc`, `sql`
- Topic Tags: `check-constraints`, `ddl`, `pause-resume`, `import-into`, `data-import`, `latin1`, `compatibility`, `behavior-changes`, `system-variables`, `update-events`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0490_2c2162dc78`
- Source ID: `tidb-docs-8.1:releases/release-7.2.0.md#sql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8bfe325a99ed96f53934e148fec69b6ae2c72107245b39a643e38bfbf5a28663`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.2.0#sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB v7.2.0 SQL, DDL, data import, TiDB Lightning character set support, or compatibility behavior changes such as TiCDC update splitting and subquery ORDER BY handling.
- Retrieval Keywords: CHECK constraints, tidb_enable_check_constraint, ADMIN PAUSE DDL JOBS, ADMIN RESUME DDL JOBS, DDL jobs support pause and resume operations, IMPORT INTO, Physical Import Mode, TiDB Distributed eXecution Framework, DXF, CSV, SQL, PARQUET, empty table, TiDB Lightning, character-set = "latin1", Latin-1 character set, TiCDC splits an event into delete and insert events, primary key or non-null unique index value is modified, tidb_remove_orderby_in_subquery, ORDER BY clauses from subqueries
- Follow-up Guidance: The content links to documentation for CHECK constraints, DDL-related commands, the IMPORT INTO statement, TiDB Lightning task configuration, TiCDC split update behavior, and the tidb_remove_orderby_in_subquery system variable.
- Classification Note: This is classified as a TiDB release feature and compatibility change because it covers new SQL and DDL capabilities, data migration behavior, and behavior changes introduced in v7.2.0.

## Official Source Content

### SQL

* Support the `CHECK` constraints [#41711](https://github.com/pingcap/tidb/issues/41711) @[fzzf678](https://github.com/fzzf678)

    Starting from v7.2.0, you can use `CHECK` constraints to restrict the values of one or more columns in a table to meet your specified conditions. When a `CHECK` constraint is added to a table, TiDB checks whether the constraint is satisfied before inserting or updating data in the table. Only the data that satisfies the constraint can be written.

     This feature is disabled by default. You can set the [`tidb_enable_check_constraint`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_check_constraint-new-in-v720) system variable to `ON` to enable it.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/constraints#check).
### DB operations

* DDL jobs support pause and resume operations (experimental) [#18015](https://github.com/pingcap/tidb/issues/18015) @[godouxm](https://github.com/godouxm)

    Before TiDB v7.2.0, when a DDL job encounters a business peak during execution, you can only manually cancel the DDL job to reduce its impact on the business. In v7.2.0, TiDB introduces pause and resume operations for DDL jobs. These operations let you pause DDL jobs during a peak and resume them after the peak ends, thus avoiding impact on your application workloads.

    For example, you can pause and resume multiple DDL jobs using `ADMIN PAUSE DDL JOBS` or `ADMIN RESUME DDL JOBS`:

    ```sql
    ADMIN PAUSE DDL JOBS 1,2;
    ADMIN RESUME DDL JOBS 1,2;
    ```

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction#ddl-related-commands).
### Data migration

* Introduce a new SQL statement `IMPORT INTO` to improve data import efficiency greatly (experimental) [#42930](https://github.com/pingcap/tidb/issues/42930) @[D3Hunter](https://github.com/D3Hunter)

    The `IMPORT INTO` statement integrates the [Physical Import Mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode) capability of TiDB Lightning. With this statement, you can quickly import data in formats such as CSV, SQL, and PARQUET into an empty table in TiDB. This import method eliminates the need for a separate deployment and management of TiDB Lightning, thereby reducing the complexity of data import and greatly improving import efficiency.

    For data files stored in Amazon S3 or GCS, when the [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework) is enabled, `IMPORT INTO` also supports splitting a data import job into multiple sub-jobs and scheduling them to multiple TiDB nodes for parallel import, which further enhances import performance.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into).

* TiDB Lightning supports importing source files with the Latin-1 character set into TiDB [#44434](https://github.com/pingcap/tidb/issues/44434) @[lance6716](https://github.com/lance6716)

    With this feature, you can directly import source files with the Latin-1 character set into TiDB using TiDB Lightning. Before v7.2.0, importing such files requires your additional preprocessing or conversion. Starting from v7.2.0, you only need to specify `character-set = "latin1"` when configuring the TiDB Lightning import task. Then, TiDB Lightning automatically handles the character set conversion during the import process to ensure data integrity and accuracy.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task).
## Compatibility changes

> **Note:**
>
> This section provides compatibility changes you need to know when you upgrade from v7.1.0 to the current version (v7.2.0). If you are upgrading from v7.0.0 or earlier versions to the current version, you might also need to check the compatibility changes introduced in intermediate versions.
### Behavior changes

- When processing update event, TiCDC splits an event into delete and insert events if the primary key or non-null unique index value is modified in the event. For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior#transactions-containing-a-single-update-change).
- Changes the default value of [`tidb_remove_orderby_in_subquery`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_remove_orderby_in_subquery-new-in-v610) from `OFF` to `ON`, meaning that the optimizer removes `ORDER BY` clauses from subqueries to avoid unnecessary sorting operations. This change might result in a different order of rows in query results. The ISO/IEC SQL standard does not require query results to follow the `ORDER BY` sorting specified in subqueries. If you need to ensure a specific order in the final result, add an `ORDER BY` clause to the outer query. If your applications rely on subquery sorting, you can set this variable to `OFF`. Clusters upgraded from earlier versions retain the previous behavior by default.
