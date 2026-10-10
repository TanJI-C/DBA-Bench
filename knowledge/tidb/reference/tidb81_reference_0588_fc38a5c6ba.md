# EXPLAIN overview syntax and output columns

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-explain.md`
- Source Title: `EXPLAIN | TiDB SQL Statement Reference`
- Source Heading Path: ``EXPLAIN` | `EXPLAIN` > Synopsis | `EXPLAIN` > `EXPLAIN` output format`
- Source Line Ranges: `5-57`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `explain`, `syntax`, `execution-plan`, `output-format`, `estrows`, `tasks`, `operators`, `mysql-client`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0588_fc38a5c6ba`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-explain.md#explain`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c2377a1537ba7fe5bd2a636272868e6d1387f7505e6ce898cc4b0284e49599fc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain#explain
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-explain.md

## Retrieval Guidance

- Use When: Use this content when you need the `EXPLAIN` syntax, aliases, or the meaning of the `id`, `estRows`, `task`, `access object`, and `operator info` output columns in a TiDB execution plan.
- Retrieval Keywords: EXPLAIN statement, DESC alias, DESCRIBE alias, EXPLAIN FOR CONNECTION, EXPLAIN output format, id estRows task access object operator info, ExplainStmt, ExplainableStmt, root task, cop task, tidb-server, TiKV, TiFlash, pager less -S, tidb_opt_enable_non_eval_scalar_subquery, ANALYZE TABLE
- Follow-up Guidance: If the `EXPLAIN` output does not match the expected result, the source says to consider executing `ANALYZE TABLE` on each table in the query to make sure the table statistics are up to date.
- Classification Note: This is reference content because it defines `EXPLAIN` syntax, aliases, supported forms, and the exact meanings of the returned execution plan columns.

## Official Source Content

# `EXPLAIN`

The `EXPLAIN` statement shows the execution plan for a query without executing it. It complements the `EXPLAIN ANALYZE` statement, which executes the query. If the output of `EXPLAIN` does not match the expected result, consider executing `ANALYZE TABLE` on each table in the query to make sure the table statistics are up to date.

> **Note:**
>
> Certain subqueries are pre-executed during the optimization phase to generate optimal execution plans, even in the `EXPLAIN` statement. For more information on this behavior and how to disable it, see [`tidb_opt_enable_non_eval_scalar_subquery`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_non_eval_scalar_subquery-new-in-v730) and [Disable the early execution of subqueries](https://docs.pingcap.com/tidb/stable/explain-walkthrough#disable-the-early-execution-of-subqueries).

The statements `DESC` and `DESCRIBE` are aliases of the `EXPLAIN` statement. The alternative usage of `EXPLAIN <tableName>` is documented in [`SHOW [FULL] COLUMNS FROM`](/sql-statements/sql-statement-show-columns-from.md).

TiDB supports the `EXPLAIN [options] FOR CONNECTION connection_id` statement. However, this statement is different from the `EXPLAIN FOR` statement in MySQL. For more details, see [`EXPLAIN FOR CONNECTION`](#explain-for-connection).
## Synopsis

```ebnf+diagram
ExplainSym ::=
    'EXPLAIN'
|   'DESCRIBE'
|   'DESC'

ExplainStmt ::=
    ExplainSym ( TableName ColumnName? | 'ANALYZE'? ExplainableStmt | 'FOR' 'CONNECTION' NUM | 'FORMAT' '=' ( stringLit | ExplainFormatType ) ( 'FOR' 'CONNECTION' NUM | ExplainableStmt ) )

ExplainableStmt ::=
    SelectStmt
|   DeleteFromStmt
|   UpdateStmt
|   InsertIntoStmt
|   ReplaceIntoStmt
|   UnionStmt
```
## `EXPLAIN` output format

> **Note:**
>
> When you use the MySQL client to connect to TiDB, to read the output result in a clearer way without line wrapping, you can use the `pager less -S` command. Then, after the `EXPLAIN` result is output, you can press the right arrow <kbd>→</kbd> button on your keyboard to horizontally scroll through the output.

> **Note:**
>
> In the returned execution plan, for all probe-side child nodes of `IndexJoin` and `Apply` operators, the meaning of `estRows` since v6.4.0 is different from that before v6.4.0. You can find details in [TiDB Query Execution Plan Overview](https://docs.pingcap.com/tidb/stable/explain-overview#understand-explain-output).

Currently, `EXPLAIN` in TiDB outputs 5 columns: `id`, `estRows`, `task`, `access object`, `operator info`. Each operator in the execution plan is described by these attributes, with each row in the `EXPLAIN` output describing an operator. The description of each attribute is as follows:

| Attribute name          | Description |
|:----------------|:----------------------------------------------------------------------------------------------------------|
| id            | The operator ID is the unique identifier of the operator in the entire execution plan. In TiDB 2.1, the ID is formatted to display the tree structure of the operator. Data flows from the child node to the parent node. One and only one parent node for each operator. |
| estRows       | The number of rows that the operator is expected to output. This number is estimated according to the statistics and the operator's logic. `estRows` is called `count` in the earlier versions of TiDB 4.0. |
| task          | The type of task the operator belongs to. Currently, the execution plans are divided into two tasks: **root** task, which is executed on tidb-server, and **cop** task, which is performed in parallel on TiKV or TiFlash. The topology of the execution plan at the task level is that a root task followed by many cop tasks. The root task uses the output of cop tasks as input. The cop tasks refer to tasks that TiDB pushes down to TiKV or TiFlash. Each cop task is distributed in the TiKV cluster or the TiFlash cluster, and is executed by multiple processes. |
| access object | Data item information accessed by the operator. The information includes `table`, `partition`, and `index` (if any). Only operators that directly access the data have such information. |
| operator info | Other information about the operator. `operator info` of each operator is different. You can refer to the following examples. |
