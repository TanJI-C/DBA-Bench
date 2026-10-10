# SQL Physical Optimization overview

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-physical-optimization.md`
- Source Title: `SQL Physical Optimization`
- Source Heading Path: `SQL Physical Optimization`
- Source Line Ranges: `5-16`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `physical-optimization`, `cost-based-optimization`, `execution-plan`, `logical-plan`, `index-selection`, `statistics`, `distinct`, `cost-model`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0161_127c0ea400`
- Source ID: `tidb-docs-8.1:sql-physical-optimization.md#sql-physical-optimization`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7ce521a1ef7c1e664fb31f059746dad8b6f2c840243da23e897a55bc87c7a76b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-physical-optimization#sql-physical-optimization
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-physical-optimization.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for what SQL physical optimization is in TiDB, how a physical execution plan is chosen from a logical plan, or which topics are covered under physical optimization.
- Retrieval Keywords: SQL Physical Optimization, physical optimization, cost-based optimization, physical execution plan, logical execution plan, physical implementation, optimizer, statistics, smallest overall cost, Index Selection, Introduction to Statistics, Wrong Index Solution, Distinct Optimization, DISTINCT, Cost Model, execution plan
- Follow-up Guidance: The source points to related topics including Index Selection, Introduction to Statistics, Wrong Index Solution, Distinct Optimization, Cost Model, and Understand the Query Execution Plan.
- Classification Note: This is classified as performance for the SQL component because the content explains cost-based optimizer behavior, execution plan selection, index selection, statistics, DISTINCT optimization, and the cost model.

## Official Source Content

# SQL Physical Optimization

Physical optimization is cost-based optimization, which makes a physical execution plan for the logical execution plan generated in the previous stage. In this stage, the optimizer selects a specific physical implementation for each operator in the logical execution plan. Different physical implementations of logical operators have different time complexity, resource consumption and physical properties. In this process, the optimizer determines the cost of different physical implementations based on the statistics of the data, and selects the physical execution plan with the smallest overall cost.

[Understand the Query Execution Plan](https://docs.pingcap.com/tidb/stable/explain-overview) has introduced some physical operators. This chapter focuses on the following aspects:

- In [Index Selection](https://docs.pingcap.com/tidb/stable/choose-index), you will learn how to select the optimal index to access tables when TiDB has multiple indexes on a table.
- In [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics), you will learn what statistics TiDB collects to obtain the data distribution of a table.
- [Wrong Index Solution](https://docs.pingcap.com/tidb/stable/wrong-index-solution) introduces how to use the right index when you find the index is selected wrongly.
- [Distinct Optimization](https://docs.pingcap.com/tidb/stable/agg-distinct-optimization) introduces an optimization related to the `DISTINCT` keyword during physical optimization. In this section, you will learn its advantages and disadvantages and how to use it.
- [Cost Model](https://docs.pingcap.com/tidb/stable/cost-model) introduces how to choose a optimal execution plan based on the cost model during physical optimization.
