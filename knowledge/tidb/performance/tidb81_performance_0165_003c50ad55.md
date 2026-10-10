# Baseline capturing overview

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-management.md`
- Source Title: `SQL Plan Management (SPM)`
- Source Heading Path: `SQL Plan Management (SPM) > Baseline capturing`
- Source Line Ranges: `641-646`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `baseline-capturing`, `plan-baseline`, `plan-regression`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0165_003c50ad55`
- Source ID: `tidb-docs-8.1:sql-plan-management.md#baseline-capturing`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ac757bba8eea5b3ae64ce89c122fd08e34ef9467f2c7eb8edebcfaf96591548`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-management#baseline-capturing
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-management.md

## Retrieval Guidance

- Use When: Use this chunk when searching for what baseline capturing means in SQL Plan Management and how it relates to preventing execution plan regression during an upgrade.
- Retrieval Keywords: baseline capturing, plan baseline, prevent regression of execution plans during an upgrade, accepted plans, optimizer, SQL plan identifier, hint set, bind values, optimizer environment, creates bindings for these queries
- Follow-up Guidance: The source explains that baseline capturing captures queries that meet capturing conditions and creates bindings for them.
- Classification Note: This is classified as performance for the SQL component because it defines plan baselines and baseline capturing for execution plan stability and regression prevention.

## Official Source Content

## Baseline capturing

Used for [preventing regression of execution plans during an upgrade](#prevent-regression-of-execution-plans-during-an-upgrade), this feature captures queries that meet capturing conditions and creates bindings for these queries.

A plan baseline refers to a collection of accepted plans that the optimizer can use for executing a SQL statement. Generally, TiDB adds a plan into the plan baseline only after confirming that the plan performs well. A plan in this context encompasses all the necessary plan-related details (such as SQL plan identifier, hint set, bind values, and optimizer environment) that the optimizer requires to reproduce an execution plan.
