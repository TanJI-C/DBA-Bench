# Secondary index overview, prerequisites, and creation syntax

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-create-secondary-indexes.md`
- Source Title: `Create a Secondary Index`
- Source Heading Path: `Create a Secondary Index | Create a Secondary Index > Before you start | Create a Secondary Index > What is secondary index | Create a Secondary Index > Add a secondary index to an existing table | Create a Secondary Index > Create a secondary index when creating a new table | Create a Secondary Index > Rules in secondary index creation`
- Source Line Ranges: `5-67`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `secondary-index`, `create-index`, `create-table`, `schema-design`, `prerequisites`, `indexing-rules`, `sql-syntax`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0091_a9dc6e00ed`
- Source ID: `tidb-docs-8.1:develop/dev-guide-create-secondary-indexes.md#create-a-secondary-index`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `be98579299ede9af8385384a911cba01705c1faba7491940e5a62566b87bf707`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-secondary-indexes#create-a-secondary-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-create-secondary-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the overview, prerequisites, SQL syntax, or creation rules for adding a secondary index in TiDB or defining one during CREATE TABLE.
- Retrieval Keywords: Create a Secondary Index, secondary index, CREATE INDEX, CREATE TABLE, KEY `{index_name}` (`{column_names}`), {index_name}, {table_name}, {column_names}, add a secondary index to an existing table, create a secondary index when creating a new table, Rules in secondary index creation, Best Practices for Indexing, Schema Design Overview, Create a Database, Create a Table
- Follow-up Guidance: The source points to Best Practices for Indexing for the rules in secondary index creation.
- Classification Note: This chunk is reference content because it defines what a secondary index is, lists prerequisites, and gives the exact SQL syntax for CREATE INDEX and CREATE TABLE with KEY.

## Official Source Content

# Create a Secondary Index

This document describes how to create a secondary index using SQL and various programming languages and lists the rules of index creation. In this document, the [Bookshop](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design) application is taken as an example to walk you through the steps of secondary index creation.
## Before you start

Before creating a secondary index, do the following:

- [Build a {{{ .starter }}} Cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud).
- Read [Schema Design Overview](https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview).
- [Create a Database](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-database).
- [Create a Table](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table).
## What is secondary index

A secondary index is a logical object in a TiDB cluster. You can simply regard it as a sorting type of data that TiDB uses to improve the query performance. In TiDB, creating a secondary index is an online operation, which does not block any data read and write operations on a table. For each index, TiDB creates references for each row in a table and sorts the references by selected columns instead of by data directly.

For more information about secondary indexes, see [Secondary Indexes](https://docs.pingcap.com/tidb/stable/best-practices/tidb-best-practices#secondary-index).

For more information about secondary indexes, see [Secondary Indexes](https://docs.pingcap.com/tidb/stable/tidb-best-practices#secondary-index).

In TiDB, you can either [add a secondary index to an existing table](#add-a-secondary-index-to-an-existing-table) or [create a secondary index when creating a new table](#create-a-secondary-index-when-creating-a-new-table).
## Add a secondary index to an existing table

To add a secondary index to an existing table, you can use the [CREATE INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index) statement as follows:

```sql
CREATE INDEX {index_name} ON {table_name} ({column_names});
```

Parameter description:

- `{index_name}`: the name of a secondary index.
- `{table_name}`: the table name.
- `{column_names}`: the names of the columns to be indexed, separated by semi-colon commas.
## Create a secondary index when creating a new table

To create a secondary index at the same time as table creation, you can add a clause containing the `KEY` keyword to the end of the [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table) statement:

```sql
KEY `{index_name}` (`{column_names}`)
```

Parameter description:

- `{index_name}`: the name of a secondary index.
- `{column_names}`: the names of the columns to be indexed, separated by semi-colon commas.
## Rules in secondary index creation

See [Best Practices for Indexing](https://docs.pingcap.com/tidb/stable/develop/dev-guide-index-best-practice).
