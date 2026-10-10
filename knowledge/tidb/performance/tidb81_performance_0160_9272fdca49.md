# SQL optimization process overview

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-optimization-concepts.md`
- Source Title: `SQL Optimization Process`
- Source Heading Path: `SQL Optimization Process`
- Source Line Ranges: `5-16`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `sql-optimization`, `logical-optimization`, `physical-optimization`, `execution-plan`, `plan-cache`, `prepare`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0160_9272fdca49`
- Source ID: `tidb-docs-8.1:sql-optimization-concepts.md#sql-optimization-process`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cb28b92e2c3d307a718244c5d917c278843518302bc0c1f091297d28ee031897`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-optimization-concepts#sql-optimization-process
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-optimization-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for an overview of how TiDB turns a query into a final execution result, including logical optimization, physical optimization, and plan cache in the SQL optimization process.
- Retrieval Keywords: SQL Optimization Process, parser, logical optimization, SQL Logical Optimization, logical execution plan, physical optimization, SQL Physical Optimization, final execution plan, data distribution, execution cost of an operator, PREPARE, Execution Plan Cache, sql-prepared-plan-cache
- Follow-up Guidance: The source points to SQL Logical Optimization, SQL Physical Optimization, and Execution Plan Cache for more detailed information.
- Classification Note: This is classified under performance because the content explains how TiDB generates and optimizes execution plans and mentions caching to reduce execution plan generation cost.

## Official Source Content

# SQL Optimization Process

In TiDB, the process from inputting a query to getting the execution result according to the final execution plan is illustrated as follows:

![SQL Optimization Process](/media/sql-optimization.png)

After parsing the original query text by `parser` and some simple validity checks, TiDB first makes some logically equivalent changes to the query. For detailed changes, see [SQL Logical Optimization](https://docs.pingcap.com/tidb/stable/sql-logical-optimization).

Through these equivalent changes, this query becomes easier to handle in the logical execution plan. After the equivalent change is done, TiDB obtains a query plan structure equivalent to the original query, and then obtains a final execution plan based on the data distribution and the specific execution cost of an operator. For details, see [SQL Physical Optimization](https://docs.pingcap.com/tidb/stable/sql-physical-optimization).

At the same time, when TiDB executes the [`PREPARE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-prepare) statement, you can choose to enable caching to reduce the cost of generating the execution plan in TiDB. For details, see [Execution Plan Cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache).
