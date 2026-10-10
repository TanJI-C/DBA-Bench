# QUERY WATCH statement syntax and references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-query-watch.md`
- Source Title: `QUERY WATCH`
- Source Heading Path: `QUERY WATCH | QUERY WATCH > Synopsis | QUERY WATCH > Parameters | QUERY WATCH > MySQL compatibility | QUERY WATCH > See also`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `query-watch`, `runaway-queries`, `resource-groups`, `sql-syntax`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0621_4bb077ab0f`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-query-watch.md#query-watch`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4118e3ee4bab66b9cd4fa929b6a7960c04681a5b6199a09a5219af90a963008b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-query-watch#query-watch
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-query-watch.md

## Retrieval Guidance

- Use When: Use this content when looking for the SQL syntax, parameters reference, or compatibility note for manually managing the watch list of runaway queries with the QUERY WATCH statement in a resource group.
- Retrieval Keywords: QUERY WATCH, QUERY WATCH ADD, QUERY WATCH REMOVE, AddQueryWatchStmt, DropQueryWatchStmt, QueryWatchOptionList, RESOURCE GROUP, ACTION, SQL DIGEST, PLAN DIGEST, SQL TEXT EXACT TO, SQL TEXT SIMILAR TO, SQL TEXT PLAN TO, ResourceGroupRunawayActionOption, runaway queries, resource group, TiDB extension to MySQL syntax
- Follow-up Guidance: The source points to QUERY WATCH parameters and the Runaway Queries section in TiDB resource control documentation.
- Classification Note: This is reference content because it defines the QUERY WATCH statement syntax, parameter entry points, and MySQL compatibility note for the SQL feature.

## Official Source Content

# QUERY WATCH

The `QUERY WATCH` statement is used to manually manage the watch list of runaway queries in a resource group.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
AddQueryWatchStmt ::=
    "QUERY" "WATCH" "ADD" QueryWatchOptionList
QueryWatchOptionList ::=
    QueryWatchOption
|   QueryWatchOptionList QueryWatchOption
|   QueryWatchOptionList ',' QueryWatchOption
QueryWatchOption ::=
    "RESOURCE" "GROUP" ResourceGroupName
|   "RESOURCE" "GROUP" UserVariable
|   "ACTION" EqOpt ResourceGroupRunawayActionOption
|   QueryWatchTextOption
ResourceGroupName ::=
    Identifier
|   "DEFAULT"
QueryWatchTextOption ::=
    "SQL" "DIGEST" SimpleExpr
|   "PLAN" "DIGEST" SimpleExpr
|   "SQL" "TEXT" ResourceGroupRunawayWatchOption "TO" SimpleExpr

ResourceGroupRunawayWatchOption ::=
    "EXACT"
|   "SIMILAR"
|   "PLAN"

DropQueryWatchStmt ::=
    "QUERY" "WATCH" "REMOVE" NUM
```
## Parameters

See [`QUERY WATCH` parameters](https://docs.pingcap.com/tidb/stable/tidb-resource-control#query-watch-parameters).
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Runaway Queries](https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries)
