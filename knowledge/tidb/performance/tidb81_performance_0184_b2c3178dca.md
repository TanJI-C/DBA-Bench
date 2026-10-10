# SQL tuning overview and related concepts

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-overview.md`
- Source Title: `SQL Tuning Overview`
- Source Heading Path: `SQL Tuning Overview`
- Source Line Ranges: `5-16`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `sql-tuning`, `query-execution`, `execution-plan`, `explain`, `sql-optimization`, `plan-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0184_b2c3178dca`
- Source ID: `tidb-docs-8.1:sql-tuning-overview.md#sql-tuning-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `36a6d7ca6da23cbb72b60acae001f30ae3e89820102c9ff1eac878df024b10ff`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-overview#sql-tuning-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for a high-level introduction to SQL tuning in TiDB, including what an execution plan is, how TiDB optimizes declarative SQL, or where to start with EXPLAIN and plan control concepts.
- Retrieval Keywords: SQL Tuning Overview, TiDB SQL optimization, declarative language, query execution, execution plan, EXPLAIN statement, Understanding the Query Execution Plan, SQL Optimization Process, Control Execution Plans, plan control, suboptimal execution plan
- Follow-up Guidance: The source points to related topics on understanding the query execution plan with `EXPLAIN`, the SQL optimization process, and ways to control execution plans when TiDB chooses a suboptimal plan.
- Classification Note: This chunk is classified under performance and sql because it is an overview of how TiDB optimizes SQL query execution and introduces execution plans, EXPLAIN, optimization, and plan control.

## Official Source Content

# SQL Tuning Overview

SQL is a declarative language. That is, an SQL statement describes _what the final result should look like_ and not a set of steps to execute in sequence. TiDB will optimize the execution, and is semantically permitted to execute parts of the query in any order provided that it correctly returns the final result as described.

A useful comparison to SQL optimization, is to describe what happens when you use GPS navigation. From your provided address, _2955 Campus Drive San Mateo CA 94403_, the GPS software plans the most time-efficient way to route you. It may make use of various statistics such as previous trips, meta data such as speed limits, and in modern cases, a live feed of traffic information. Several of these analogies translate to TiDB.

This section introduces several concepts about query execution:

- [Understanding the Query Execution Plan](https://docs.pingcap.com/tidb/stable/explain-overview) introduces how to use the `EXPLAIN` statement to understand how TiDB has decided to execute a statement.
- [SQL Optimization Process](https://docs.pingcap.com/tidb/stable/sql-optimization-concepts) introduces what optimizations TiDB is capable of using to improve query execution performance.
- [Control Execution Plans](https://docs.pingcap.com/tidb/stable/control-execution-plan) introduces ways to control the generation of the execution plan. This can be useful in cases where the execution plan decided by TiDB is suboptimal.
