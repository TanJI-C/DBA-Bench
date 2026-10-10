# DXF overview, use cases, and task limit

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-distributed-execution-framework.md`
- Source Title: `TiDB Distributed eXecution Framework (DXF)`
- Source Heading Path: `TiDB Distributed eXecution Framework (DXF) | TiDB Distributed eXecution Framework (DXF) > Use cases | TiDB Distributed eXecution Framework (DXF) > Limitation`
- Source Line Ranges: `5-44`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `distributed-execution`, `task-scheduling`, `use-cases`, `limitations`, `add-index`, `import-into`, `resource-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0095_cf93ac2422`
- Source ID: `tidb-docs-8.1:tidb-distributed-execution-framework.md#tidb-distributed-execution-framework-dxf`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b1141e46314f53943882a2cd8160be2030281fe32fa6a8b6a62316b3c2dd90a4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework#tidb-distributed-execution-framework-dxf
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-distributed-execution-framework.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks what the TiDB Distributed eXecution Framework (DXF) is, which statements it currently supports, its use cases, or its simultaneous task limit.
- Retrieval Keywords: TiDB Distributed eXecution Framework, DXF, distributed execution, unified scheduling, unified resource management, ADD INDEX, IMPORT INTO, DDL operations, TTL, ANALYZE, Backup/Restore, up to 16 tasks simultaneously, ALTER TABLE t1 ADD INDEX idx1(c1), CREATE INDEX idx1 ON table t1(c1)
- Follow-up Guidance: The source also states that this feature is not available on Starter and Essential clusters.
- Classification Note: This is classified as architecture because the content explains the DXF goal, distributed framework role, supported task types, and the framework-level limitation.

## Official Source Content

# TiDB Distributed eXecution Framework (DXF)

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

TiDB adopts a computing-storage separation architecture with excellent scalability and elasticity. Starting from v7.1.0, TiDB introduces a **Distributed eXecution Framework (DXF)** to further leverage the resource advantages of the distributed architecture. The goal of the DXF is to implement unified scheduling and distributed execution of tasks, and to provide unified resource management capabilities for both overall and individual tasks, which better meets users' expectations for resource usage.

This document describes the use cases, limitations, usage, and implementation principles of the DXF.
## Use cases

In a database management system, in addition to the core transactional processing (TP) and analytical processing (AP) workloads, there are other important tasks, such as DDL operations, [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into), [TTL](https://docs.pingcap.com/tidb/stable/time-to-live), [`ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table), and Backup/Restore. These tasks need to process a large amount of data in database objects (tables), so they typically have the following characteristics:

- Need to process all data in a schema or a database object (table).
- Might need to be executed periodically, but at a low frequency.
- If the resources are not properly controlled, they are prone to affect TP and AP tasks, lowering the database service quality.

Enabling the DXF can solve the above problems and has the following three advantages:

- The framework provides unified capabilities for high scalability, high availability, and high performance.
- The DXF supports distributed execution of tasks, which can flexibly schedule the available computing resources of the entire TiDB cluster, thereby better utilizing the computing resources in a TiDB cluster.
- The DXF provides unified resource usage and management capabilities for both overall and individual tasks.

Currently, the DXF supports the distributed execution of the [`ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) and [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) statements.

- [`ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) is a DDL statement used to create indexes. For example:

    ```sql
    ALTER TABLE t1 ADD INDEX idx1(c1);
    CREATE INDEX idx1 ON table t1(c1);
    ```

- [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) is used to import data in formats such as CSV, SQL, and Parquet into an empty table.
## Limitation

The DXF can only schedule up to 16 tasks (including [`ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) tasks and [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) tasks) simultaneously.
