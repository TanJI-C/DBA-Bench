# TiDB 2.0 RC3 overview and TiDB changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0-rc.3.md`
- Source Title: `TiDB 2.0 RC3 Release Notes`
- Source Heading Path: `TiDB 2.0 RC3 Release Notes | TiDB 2.0 RC3 Release Notes > TiDB`
- Source Line Ranges: `5-29`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `release-notes`, `mysql-compatibility`, `sql-optimization`, `stability`, `ddl`, `indexing`, `memory-control`, `join-reorder`, `disaster-recovery`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0022_f3d27b30a6`
- Source ID: `tidb-docs-8.1:releases/release-2.0-rc.3.md#tidb-2-0-rc3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5488dfb84fbb20aac99b40d4f15a062983b84cc2cc2524d42231dbc0e100f14b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0-rc.3#tidb-2-0-rc3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0-rc.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 2.0 RC3 release-note items about MySQL compatibility, SQL optimization, DDL visibility, index recovery, or specific SQL and configuration features added or fixed in TiDB.
- Retrieval Keywords: TiDB 2.0 RC3, MAX/MIN wrong result, Sort Merge Join order of Join Key, uint and int boundary conditions, floating point length and precision, time type parsing error log, IndexLookupExecutor memory, ADD INDEX speed, Stream Aggregation, GROUP BY substatement is empty, Join Reorder, STRAIGHT_JOIN, ADMIN SHOW DDL JOBS, ADMIN SHOW DDL JOB QUERIES, ADMIN RECOVER INDEX, lower priority ADD INDEX, JSON type parameters SUM AVG, lower_case_table_names, OGG data replication tool, Navicat, implicit RowID CRUD
- Follow-up Guidance: The source also states that TiDB 2.0 RC3 improves DDL job status output in `ADMIN SHOW DDL JOBS` and supports querying original statements with `ADMIN SHOW DDL JOB QUERIES`.
- Classification Note: This is a TiDB release-notes chunk because the content lists TiDB 2.0 RC3 changes in SQL behavior, optimizer features, DDL statements, configuration compatibility, and disaster recovery commands.

## Official Source Content

# TiDB 2.0 RC3 Release Notes

On March 23, 2018, TiDB 2.0 RC3 is released. This release has great improvement in MySQL compatibility, SQL optimization and stability.
## TiDB

- Fix the wrong result issue of `MAX/MIN` in some scenarios
- Fix the issue that the result of `Sort Merge Join` does not show in order of Join Key in some scenarios
- Fix the error of comparison between `uint` and `int` in boundary conditions
- Optimize checks on length and precision of the floating point type, to improve compatibility with MySQL
- Improve the parsing error log of time type and add more error information
- Improve memory control and add statistics about `IndexLookupExecutor` memory
- Optimize the execution speed of `ADD INDEX` to greatly increase the speed in some scenarios
- Use the Stream Aggregation operator when the `GROUP BY` substatement is empty, to increase the speed
- Support closing the `Join Reorder` optimization in the optimizer using `STRAIGHT_JOIN`
- Output more detailed status information of DDL jobs in `ADMIN SHOW DDL JOBS`
- Support querying the original statements of currently running DDL jobs using `ADMIN SHOW DDL JOB QUERIES`
- Support recovering the index data using `ADMIN RECOVER INDEX` for disaster recovery
- Attach a lower priority to the `ADD INDEX` operation to reduce the impact on online business
- Support aggregation functions with JSON type parameters, such as `SUM/AVG`
- Support modifying the `lower_case_table_names` system variable in the configuration file, to support the OGG data replication tool
- Improve compatibility with the Navicat management tool
- Support using implicit RowID in CRUD operations
