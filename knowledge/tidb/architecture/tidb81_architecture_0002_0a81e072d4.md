# DDL execution principles and statement types

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/ddl-introduction.md`
- Source Title: `Execution Principles and Best Practices of DDL Statements`
- Source Heading Path: `Execution Principles and Best Practices of DDL Statements | Execution Principles and Best Practices of DDL Statements > DDL execution principles | Execution Principles and Best Practices of DDL Statements > DDL execution principles > Types of DDL statements`
- Source Line Ranges: `5-37`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `ddl`, `online-ddl`, `asynchronous-execution`, `offline-ddl`, `logical-ddl`, `physical-ddl`, `reorg-ddl`, `add-index`, `schema-change`, `application-impact`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0002_0a81e072d4`
- Source ID: `tidb-docs-8.1:best-practices/ddl-introduction.md#execution-principles-and-best-practices-of-ddl-statements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7608c176a27ef04e388b225dd78b8b0f531c5c8b04a71833093a2e33b977da95`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction#execution-principles-and-best-practices-of-ddl-statements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/ddl-introduction.md

## Retrieval Guidance

- Use When: Use this chunk when explaining how TiDB executes DDL online and asynchronously and how offline, online, logical, and physical DDL statements differ in execution behavior and application impact.
- Retrieval Keywords: online and asynchronous DDL, offline DDL statements, online DDL statements, logical DDL statements, general DDL, physical DDL statements, reorg DDL, ADD INDEX, lossy column type changes, full table scan, DDL Owners, TiDB Distributed eXecution Framework, DXF, application impact, CPU and I/O resources from TiKV
- Follow-up Guidance: The source further states that physical DDL statements such as `ADD INDEX` and lossy column type changes can take a long time and consume TiKV and TiDB CPU resources during execution.
- Classification Note: This is classified as architecture content because it describes TiDB DDL execution principles, statement categories, and the resource and workload characteristics of online schema changes.

## Official Source Content

# Execution Principles and Best Practices of DDL Statements

This document provides an overview of the execution principles and best practices related to DDL statements in TiDB. The principles include the DDL Owner module and the online DDL change process.
## DDL execution principles

TiDB uses an online and asynchronous approach to execute DDL statements. This means that DML statements in other sessions are not blocked while DDL statements are being executed. In other words, you can change the definitions of database objects using online and asynchronous DDL statements while your applications are running.
### Types of DDL statements

Based on whether DDL statements block the user application during execution, DDL statements can be divided into the following types:

- **Offline DDL statements**: When the database receives a DDL statement from the user, it first locks the database object to be modified and then changes the metadata. During the DDL execution, the database blocks the user application from modifying data.

- **Online DDL statements**: When a DDL statement is executed in the database, a specific method is used to ensure that the statement does not block the user application. This allows the user to submit modifications during the DDL execution. The method also ensures the correctness and consistency of the corresponding database object during the execution process.

Based on whether to operate the data included in the target DDL object, DDL statements can be divided into the following types:

- **Logical DDL statements**: Logical DDL statements usually only modify the metadata of the database object, without processing the data stored in the object, for example, changing the table name or changing the column name.

    In TiDB, logical DDL statements are also referred to as "general DDL". These statements typically have a short execution time, often taking only a few tens of milliseconds or seconds to complete. As a result, they do not consume much system resource and do not affect the workload on the application.

- **Physical DDL statements**: Physical DDL statements not only modify the metadata of the object to be changed, but also modify the user data stored in the object. For example, when TiDB creates an index for a table, it not only changes the definition of the table, but also performs a full table scan to build the newly added index.

    In TiDB, physical DDL statements are also referred to as "reorg DDL", which stands for reorganization. Currently, physical DDL statements only include `ADD INDEX` and lossy column type changes (such as changing from an `INT` type to a `CHAR` type). These statements take a long time to execute, and the execution time is affected by the amount of data in the table, the machine configuration, and the application workload.

    Executing physical DDL statements can have an impact on the workload of the application for two reasons. On the one hand, it consumes CPU and I/O resources from TiKV to read data and write new data. On the other hand, **the TiDB node serving as DDL Owners** or **those TiDB nodes scheduled by the TiDB Distributed eXecution Framework (DXF) to execute `ADD INDEX` tasks** consume CPU resources from TiDB to perform the corresponding computations.

    > **Note:**
    >
    > The execution of a physical DDL task typically causes the greatest impact on the user application. Therefore, to minimize this impact, the key point is to optimize the design of physical DDL statements during execution. This helps to reduce the impact on the user application.
