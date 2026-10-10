# DM binlog value filter overview

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/feature-expression-filter.md`
- Source Title: `Filter DMLs Using SQL Expressions`
- Source Heading Path: `Filter DMLs Using SQL Expressions | Filter DMLs Using SQL Expressions > Overview`
- Source Line Ranges: `5-14`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `incremental-migration`, `binlog`, `row-format`, `dml-filtering`, `sql-expressions`, `binlog-value-filter`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0012_62f98fdb53`
- Source ID: `tidb-docs-8.1:dm/feature-expression-filter.md#filter-dmls-using-sql-expressions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6fd9ef23182bd2b205a8d9f179959f237807ac6191b2c393256b09dc1f79a9b3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/feature-expression-filter#filter-dmls-using-sql-expressions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/feature-expression-filter.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about filtering specific row changes during incremental migration in DM based on SQL expressions over binlog column values.
- Retrieval Keywords: DM, binlog value filter, Filter DMLs Using SQL Expressions, incremental data migration, ROW format, binlog events, filter specific row of DELETE events, SQL expressions, row change evaluates TRUE, will not migrate downstream, Filter Binlog Events
- Follow-up Guidance: For detailed operation and implementation, see Filter DML Events Using SQL Expressions.
- Classification Note: The content is classified under data_pipeline for the dm component because it describes incremental migration filtering of DML row changes using binlog value filter.

## Official Source Content

# Filter DMLs Using SQL Expressions
## Overview

In the process of incremental data migration, you can filter certain types of binlog events using the [Filter Binlog Events](https://docs.pingcap.com/tidb/stable/filter-binlog-event) feature. For example, for archiving or auditing purposes, you can filter out `DELETE` events when migrating data to the downstream. However, Binlog Event Filter cannot judge with a greater granularity on whether to filter out a specific row of `DELETE` events.

To solve the above issue, DM supports filtering data during incremental migration using `binlog value filter` since v2.0.5. The binlog in the `ROW` format supported by DM has the values of all columns in binlog events. You can configure SQL expressions according to these values. If the SQL expressions evaluate a row change as `TRUE`, DM will not migrate the row change downstream.

For detailed operation and implementation, see [Filter DML Events Using SQL Expressions](https://docs.pingcap.com/tidb/stable/filter-dml-event).
