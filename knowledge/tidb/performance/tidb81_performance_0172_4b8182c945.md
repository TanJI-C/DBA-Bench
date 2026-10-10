# SQL tuning guide overview and query processing workflow

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide | A Practical Guide for SQL Tuning > SQL tuning guide > Understand query processing | A Practical Guide for SQL Tuning > SQL tuning guide > Understand query processing > Query processing workflow`
- Source Line Ranges: `128-170`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `query-processing`, `optimizer`, `ast`, `point-get`, `logical-transformation`, `cost-based-optimization`, `pushdown`, `execution-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0172_4b8182c945`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#sql-tuning-guide`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `460dd05d1582c355afd6a4e608a919fdbb554329867ea042a6e527d72ff56004`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#sql-tuning-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when the need is to understand the TiDB query processing workflow from SQL reception through optimization, plan generation, and distributed execution.
- Retrieval Keywords: SQL tuning guide, Understand query processing, Query processing workflow, protocol layer, optimizer, abstract syntax tree, AST, Point Get, Batch Point Get, logical transformation, cost-based optimization, statistics, physical execution plan, SQL executor, push down operators, coprocessors, TiKV, TiFlash, distributed architecture
- Follow-up Guidance: The content indicates that the guide also covers optimizer fundamentals, statistics management, understanding execution plans, index strategy in TiDB, and when to use TiFlash.
- Classification Note: This is classified as performance for the SQL component because the content explains how TiDB processes queries and uses optimization, statistics, and pushdown execution to improve query performance.

## Official Source Content

## SQL tuning guide

This guide provides practical advice for beginners on optimizing SQL queries in TiDB. By following these best practices, you can improve query performance and streamline SQL tuning. This guide covers the following topics:

- [Understand query processing](#understand-query-processing)
    - [Query processing workflow](#query-processing-workflow)
    - [Optimizer fundamentals](#optimizer-fundamentals)
    - [Statistics management](#statistics-management)
- [Understand execution plans](#understand-execution-plans)
    - [How TiDB builds an execution plan](#how-tidb-builds-an-execution-plan)
    - [Generate and display execution plans](#generate-and-display-execution-plans)
    - [Read execution plans: first child first](#read-execution-plans-first-child-first)
    - [Identify bottlenecks in execution plans](#identify-bottlenecks-in-execution-plans)
- [Index strategy in TiDB](#index-strategy-in-tidb)
    - [Composite index strategy guidelines](#composite-index-strategy-guidelines)
    - [The cost of indexing](#the-cost-of-indexing)
    - [SQL tuning with a covering index](#sql-tuning-with-a-covering-index)
    - [SQL tuning with a composite index involving sorting](#sql-tuning-with-a-composite-index-involving-sorting)
    - [SQL tuning with composite indexes for efficient filtering and sorting](#sql-tuning-with-composite-indexes-for-efficient-filtering-and-sorting)
- [When to use TiFlash](#when-to-use-tiflash)
    - [Analytical query](#analytical-query)
    - [SaaS arbitrary filtering workloads](#saas-arbitrary-filtering-workloads)
### Understand query processing

This section introduces the query processing workflow, optimizer fundamentals, and statistics management.
#### Query processing workflow

When a client sends a SQL statement to TiDB, the statement passes through the protocol layer of the TiDB server. This layer manages the connection between the TiDB server and the client, receives SQL statements, and returns data to the client.

![workflow](/media/sql-tuning/workflow-tiflash.png)

In the preceding figure, to the right of the protocol layer is the optimizer of the TiDB server, which processes SQL statements as follows:

1. The SQL statement arrives at the SQL optimizer through the protocol layer and is parsed into an abstract syntax tree (AST).
2. TiDB identifies whether it is a [Point Get](https://docs.pingcap.com/tidb/stable/explain-indexes#point_get-and-batch_point_get) statement, which involves a simple one-table lookup through a primary or unique key, such as `SELECT * FROM t WHERE pk_col = 1` or `SELECT * FROM t WHERE uk_col IN (1,2,3)`. For `Point Get` statements, TiDB skips subsequent optimization steps and proceeds directly to execution in the SQL executor.
3. If the query is not a `Point Get`, the AST undergoes logical transformation, where TiDB rewrites the SQL logically based on specific rules.
4. After logical transformation, TiDB processes the AST through cost-based optimization.
5. During cost-based optimization, the optimizer uses statistics to select appropriate operators and generates a physical execution plan.
6. The generated physical execution plan is sent to the SQL executor of the TiDB node for execution.
7. Unlike traditional single-node databases, TiDB pushes down operators or coprocessors to TiKV and/or TiFlash nodes containing the data. This approach processes parts of the execution plan where the data is stored, efficiently utilizing the distributed architecture, using resources in parallel, and reducing network data transfer. The TiDB node executor then assembles the final result and returns it to the client.
