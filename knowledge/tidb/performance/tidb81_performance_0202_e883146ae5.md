# SQL performance tuning workflow and tools

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-sql-tuning-overview.md`
- Source Title: `SQL Tuning Overview`
- Source Heading Path: `SQL Tuning Overview | SQL Tuning Overview > Tune SQL performance | SQL Tuning Overview > Tune SQL performance > Use Statement on the Diagnosis page | SQL Tuning Overview > Tune SQL performance > Check the execution plan | SQL Tuning Overview > Tune SQL performance > Optimize the execution plan | SQL Tuning Overview > Tune SQL performance > Optimize full table scan | SQL Tuning Overview > Tune SQL performance > DML best practices | SQL Tuning Overview > Tune SQL performance > DDL best practices when selecting primary keys | SQL Tuning Overview > Tune SQL performance > Index best practices | SQL Tuning Overview > Tune SQL performance > Use the slow log memory mapping table`
- Source Line Ranges: `5-95`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `sql`, `tidb`, `tiflash`
- Topic Tags: `sql-tuning`, `slow-queries`, `statement-analysis`, `diagnosis`, `execution-plan`, `explain`, `full-table-scan`, `indexes`, `join-types`, `plan-cache`, `slow-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0202_e883146ae5`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-sql-tuning-overview.md#sql-tuning-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5600b13efcf5cb49c2112c0ad9eb155a0d8df59b42330bc529683f23e7d8a407`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sql-tuning-overview#sql-tuning-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-sql-tuning-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs TiDB Cloud SQL tuning guidance that covers Statement analysis on the Diagnosis page, EXPLAIN or EXPLAIN ANALYZE, execution plan optimization, full table scan causes, indexes, join types, TiFlash, or slow query analysis workflow.
- Retrieval Keywords: SQL Tuning Overview, TiDB Cloud, Diagnosis page, SQL Statement tab, Statement dashboard, SQL Template, SQL digest, SQL template ID, execution plan list, execution plan details, Related slow query, EXPLAIN, EXPLAIN ANALYZE, execution plan, SQL Logical Optimization, SQL Physical Optimization, PREPARE statement, Prepare Execution Plan Cache, full table scan, secondary index, covering index, primary index, join types, TiFlash, HTAP workloads, slow queries
- Follow-up Guidance: The chunk also points to DML best practices, primary key selection guidelines, indexing best practices, and execution plan cache for the PREPARE statement.
- Classification Note: This is classified as performance for the cloud component because the content describes TiDB Cloud tools and principles for analyzing and optimizing slow SQL statements and execution plans.

## Official Source Content

# SQL Tuning Overview

This document introduces how to tune SQL performance in TiDB Cloud. To get the best SQL performance, you can do the following:

- Tune SQL performance. There are many ways to optimize SQL performance, such as analyzing query statements, optimizing execution plans, and optimizing full table scan.
- Optimize schema design. Depending on your business workload type, you may need to optimize the schemas to avoid transaction conflicts or hotspots.
## Tune SQL performance

To improve the performance of SQL statements, consider the following principles.

- Minimize the scope of the scanned data. It is always a best practice to scan only the minimum scope of data and avoid scanning all data.
- Use appropriate indexes. For each column in the `WHERE` clause in a SQL statement, make sure that there is a corresponding index. Otherwise, the `WHERE` clause will scan the full table and result in poor performance.
- Use appropriate Join types. Depending on the size and correlation of each table in the query, it is very important to choose the right Join type. Generally, the cost-based optimizer in TiDB automatically chooses the optimal Join type. However, in some cases, you may need to specify the Join type manually. For details, see [Explain Statements That Use Joins](https://docs.pingcap.com/tidb/stable/explain-joins).
- Use appropriate storage engines. It is recommended to use the TiFlash storage engine for Hybrid Transactional and Analytical Processing (HTAP) workloads. See [HTAP Queries](https://docs.pingcap.com/tidb/stable/develop/dev-guide-hybrid-oltp-and-olap-queries).

TiDB Cloud provides several tools to help you analyze slow queries on a cluster. The following sections describe several approaches to optimize slow queries.
### Use Statement on the Diagnosis page

The TiDB Cloud console provides a [**SQL Statement**](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#statement-analysis) tab on the [**Diagnosis**](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#view-the-diagnosis-page) page. It collects the execution statistics of SQL statements of all databases on the cluster. You can use it to identify and analyze SQL statements that consume a long time in total or in a single execution.

Note that on this page, SQL queries with the same structure (even if the query parameters do not match) are grouped into the same SQL statement. For example, `SELECT * FROM employee WHERE id IN (1, 2, 3)` and `select * from EMPLOYEE where ID in (4, 5)` are both part of the same SQL statement `select * from employee where id in (...)`.

You can view some key information in **SQL Statement**.

- **SQL Template**: including SQL digest, SQL template ID, the time range currently viewed, the number of execution plans, and the database where the execution takes place.

    ![Details0](/media/dashboard/dashboard-statement-detail0.png)

- Execution plan list: if a SQL statement has more than one execution plan, the list is displayed. You can select different execution plans and the details of the selected execution plan are displayed at the bottom of the list. If there is only one execution plan, the list will not be displayed.

    ![Details1](/media/dashboard/dashboard-statement-detail1.png)

- Execution plan details: shows the details of the selected execution plan. It collects the execution plans of each SQL type and the corresponding execution time from several perspectives to help you get more information. See [Execution plans](https://docs.pingcap.com/tidb/stable/dashboard-statement-details#execution-plans).

    ![Details2](/media/dashboard/dashboard-statement-detail2.png)

- Related slow query

In addition to the information in the **Statement** dashboard, there are also some SQL best practices for TiDB Cloud as described in the following sections.
### Check the execution plan

You can use [`EXPLAIN`](https://docs.pingcap.com/tidb/stable/explain-overview) to check the execution plan calculated by TiDB for a statement during compiling. In other words, TiDB estimates hundreds or thousands of possible execution plans and selects an optimal execution plan that consumes the least resource and executes the fastest.

If the execution plan selected by TiDB is not optimal, you can use EXPLAIN or [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze) to diagnose it.
### Optimize the execution plan

After parsing the original query text by `parser` and basic validity verification, TiDB first makes some logical equivalent changes to the query. For more information, see [SQL Logical Optimization](https://docs.pingcap.com/tidb/stable/sql-logical-optimization).

Through these equivalence changes, the query can become easier to handle in the logical execution plan. After the equivalence changes, TiDB gets a query plan structure that is equivalent to the original query, and then gets a final execution plan based on the data distribution and the specific execution overhead of an operator. For more information, see [SQL Physical Optimization](https://docs.pingcap.com/tidb/stable/sql-physical-optimization).

Also, TiDB can choose to enable execution plan cache to reduce the creation overhead of the execution plan when executing the `PREPARE` statement, as introduced in [Prepare Execution Plan Cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache).
### Optimize full table scan

The most common reason for slow SQL queries is that the `SELECT` statements perform full table scan or use incorrect indexes. You can use EXPLAIN or EXPLAIN ANALYZE to view the execution plan of a query and locate the cause of the slow execution. There are [three methods](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql) that you can use to optimize.

- Use secondary index
- Use covering index
- Use primary index
### DML best practices

See [DML best practices](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-best-practices#dml-best-practices).
### DDL best practices when selecting primary keys

See [Guidelines to follow when selecting primary keys](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#guidelines-to-follow-when-selecting-primary-key).
### Index best practices

[Best practices for indexing](https://docs.pingcap.com/tidb/stable/develop/dev-guide-index-best-practice) include best practices for creating indexes and using indexes.

The speed of creating indexes is conservative by default, and the index creation process can be accelerated by [modifying variables](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-best-practices#add-index-best-practices) in some scenarios.

<!--
### Use the slow log memory mapping table

You can query the contents of the slow query log by querying the [INFORMATION_SCHEMA.SLOW_QUERY](https://docs.pingcap.com/tidb/stable/identify-slow-queries#memory-mapping-in-slow-log) table, and find the structure in the [`SLOW_QUERY`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-slow-query) table. Using this table, you can perform queries using different fields to find potential problems.

The recommended analysis process for slow queries is as follows.

1. [Identify the performance bottleneck of the query](https://docs.pingcap.com/tidb/stable/analyze-slow-queries#identify-the-performance-bottleneck-of-the-query). That is, identify the part of the query process that takes long time.
2. [Analyze system issues](https://docs.pingcap.com/tidb/stable/analyze-slow-queries#analyze-system-issues). According to the bottleneck point, combine the monitoring, logging and other information at that time to find the possible causes.
3. [Analyze optimizer issues](https://docs.pingcap.com/tidb/stable/analyze-slow-queries#analyze-optimizer-issues). Analyze whether there is a better execution plan.
-->
