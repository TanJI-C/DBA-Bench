# IMPORT INTO limitations and summary recommendation

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/import-into-vs-tidb-lightning.md`
- Source Title: `IMPORT INTO vs. TiDB Lightning`
- Source Heading Path: `IMPORT INTO vs. TiDB Lightning > Functionalities not supported by `IMPORT INTO` | IMPORT INTO vs. TiDB Lightning > Summary`
- Source Line Ranges: `113-133`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `lightning`, `tidb`
- Topic Tags: `limitations`, `logical-import`, `conflict-handling`, `multi-table-import`, `bulk-dml`, `summary`, `recommendation`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0933_8478ad6f2e`
- Source ID: `tidb-docs-8.1:tidb-lightning/import-into-vs-tidb-lightning.md#functionalities-not-supported-by-import-into`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `76c2349f71f50c5bd75ba270291e4dec3a08aa5ebebeecc0eec4397284bec475`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/import-into-vs-tidb-lightning#functionalities-not-supported-by-import-into
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/import-into-vs-tidb-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when checking which functionalities are not supported by `IMPORT INTO` or when looking for the summary comparison and recommendation versus TiDB Lightning.
- Retrieval Keywords: Functionalities not supported by IMPORT INTO, logical import, target table must be empty, LOAD DATA, bulk DML, tidb_dml_type, conflict data handling, primary keys PK, unique keys UK, task failures, multiple target tables, one target table per IMPORT INTO SQL statement, Summary, consider using IMPORT INTO instead of TiDB Lightning
- Follow-up Guidance: It states that future versions will add support for these functionalities and enhancements such as modifying concurrency during task execution and adjusting throughput for writing to TiKV.
- Classification Note: The chunk is classified as reference because the official content lists current `IMPORT INTO` limitations and provides a summary comparison with TiDB Lightning.

## Official Source Content

## Functionalities not supported by `IMPORT INTO`

Currently, `IMPORT INTO` still lacks some functionalities and cannot fully replace TiDB Lightning in some scenarios, such as:

- Logical import

    Before importing data with `IMPORT INTO`, the target table must be empty. If you need to import data into a table that already contains data, it is recommended to use methods such as [`LOAD DATA`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data) or direct insertion. Starting from v8.0, TiDB supports [bulk DML](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_type-new-in-v800) for executing large transactions.

- Conflict data handling

    `IMPORT INTO` currently does not support conflict data handling. Before the data import, you need to define the table schema properly to ensure that the data to be imported does not conflict with primary keys (PK) or unique keys (UK). Otherwise, it might cause task failures.

- Importing data into multiple target tables

    Currently, only one target table is allowed for one `IMPORT INTO` SQL statement. If you want to import data into multiple target tables, you need to submit multiple `IMPORT INTO` SQL statements.

In future versions, these functionalities will be supported by `IMPORT INTO`, along with additional enhancements to its capabilities, such as allowing modification of concurrency during task execution and adjusting throughput for writing to TiKV. This will make it more convenient for you to manage tasks.
## Summary

Compared with TiDB Lightning, `IMPORT INTO`can be directly executed on TiDB nodes, supports automated distributed task scheduling and [TiDB Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort), and offers significant improvements in deployment, resource utilization, task configuration convenience, ease of invocation and integration, high availability, and scalability. It is recommended that you consider using `IMPORT INTO` instead of TiDB Lightning in appropriate scenarios.
