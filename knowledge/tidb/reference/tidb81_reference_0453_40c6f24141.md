# Optimizer hints syntax, query block scope, QB_NAME, and SET_VAR

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints | Optimizer Hints > Syntax | Optimizer Hints > Hints that take effect in query blocks | Optimizer Hints > Hints that take effect in query blocks > QB_NAME | Optimizer Hints > Hints that take effect in query blocks > SET_VAR(VAR_NAME=VAR_VALUE)`
- Source Line Ranges: `5-116`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `optimizer-hints`, `syntax`, `query-blocks`, `qb-name`, `session-variables`, `set-var`, `explain`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0453_40c6f24141`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#optimizer-hints`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `79fb14ccaad5b55b63343c1c2e89f6fcc1325ade910f24ee7f9c35771799e0d6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#optimizer-hints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax and scope rules for TiDB optimizer hints, including query block names, QB_NAME, SET_VAR, warnings behavior, and how to verify effects with EXPLAIN or EXPLAIN ANALYZE.
- Retrieval Keywords: optimizer hints syntax, /*+ ... */, SELECT INSERT UPDATE DELETE keyword, case insensitive hints, multiple hints separated by commas, EXPLAIN, EXPLAIN ANALYZE, query block, sel_1, sel_2, sel_3, del_1, upd_1, @QB_NAME, QB_NAME, SET_VAR(VAR_NAME=VAR_VALUE), MAX_EXECUTION_TIME, hints do not take effect, warning if a hint is not applicable
- Follow-up Guidance: If hints do not take effect, the source points to the section Troubleshoot common issues that hints do not take effect.
- Classification Note: This is reference content because it defines optimizer hint syntax, query block scope rules, QB_NAME naming behavior, and statement-level temporary system variable changes with SET_VAR.

## Official Source Content

# Optimizer Hints

TiDB supports optimizer hints, which are based on the comment-like syntax introduced in MySQL 5.7. For example, one of the common syntaxes is `/*+ HINT_NAME([t1_name [, t2_name] ...]) */`. Use of optimizer hints is recommended in cases where the TiDB optimizer selects a less optimal query plan.

If you encounter a situation where hints do not take effect, see [Troubleshoot common issues that hints do not take effect](#troubleshoot-common-issues-that-hints-do-not-take-effect).
## Syntax

Optimizer hints are case insensitive and specified within `/*+ ... */` comments following the `SELECT`, `INSERT`, `UPDATE` or `DELETE` keyword in a SQL statement.

Multiple hints can be specified by separating with commas. For example, the following query uses three different hints:

```sql
SELECT /*+ USE_INDEX(t1, idx1), HASH_AGG(), HASH_JOIN(t1) */ count(*) FROM t t1, t t2 WHERE t1.a = t2.b;
```

How optimizer hints affect query execution plans can be observed in the output of [`EXPLAIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain) and [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze).

An incorrect or incomplete hint will not result in a statement error. This is because hints are intended to have only a _hint_ (suggestion) semantic to query execution. Similarly, TiDB will at most return a warning if a hint is not applicable.

> **Note:**
>
> If the comments do not follow behind the specified keywords, they will be treated as common MySQL comments. The comments do not take effect, and no warning is reported.

Currently, TiDB supports two categories of hints, which are different in scope. The first category of hints takes effect in the scope of query blocks, such as [`/*+ HASH_AGG() */`](#hash_agg); the second category of hints takes effect in the whole query, such as [`/*+ MEMORY_QUOTA(1024 MB)*/`](#memory_quotan).

Each query or sub-query in a statement corresponds to a different query block, and each query block has its own name. For example:

```sql
SELECT * FROM (SELECT * FROM t) t1, (SELECT * FROM t) t2;
```

The above query statement has three query blocks: the outermost `SELECT` corresponds to the first query block, whose name is `sel_1`; the two `SELECT` sub-queries correspond to the second and the third query block, whose names are `sel_2` and `sel_3`, respectively. The sequence of the numbers is based on the appearance of `SELECT` from left to right. If you replace the first `SELECT` with `DELETE` or `UPDATE`, then the corresponding query block names are `del_1` or `upd_1`.
## Hints that take effect in query blocks

This category of hints can follow behind **any** `SELECT`, `UPDATE` or `DELETE` keywords. To control the effective scope of the hint, use the name of the query block in the hint. You can make the hint parameters clear by accurately identifying each table in the query (in case of duplicated table names or aliases). If no query block is specified in the hint, the hint takes effect in the current block by default.

For example:

```sql
SELECT /*+ HASH_JOIN(@sel_1 t1@sel_1, t3) */ * FROM (SELECT t1.a, t1.b FROM t t1, t t2 WHERE t1.a = t2.a) t1, t t3 WHERE t1.b = t3.b;
```

This hint takes effect in the `sel_1` query block, and its parameters are the `t1` and `t3` tables in `sel_1` (`sel_2` also contains a `t1` table).

As described above, you can specify the name of the query block in the hint in the following ways:

- Set the query block name as the first parameter of the hint, and separate it from other parameters with a space. In addition to `QB_NAME`, all the hints listed in this section also have another optional hidden parameter `@QB_NAME`. By using this parameter, you can specify the effective scope of this hint.
- Append `@QB_NAME` to a table name in the parameter to explicitly specify which query block this table belongs to.

> **Note:**
>
> You must put the hint in or before the query block where the hint takes effect. If the hint is put after the query block, it cannot take effect.
### QB_NAME

If the query statement is a complicated statement that includes multiple nested queries, the ID and name of a certain query block might be mistakenly identified. The hint `QB_NAME` can help us in this regard.

`QB_NAME` means Query Block Name. You can specify a new name to a query block. The specified `QB_NAME` and the previous default name are both valid. For example:

```sql
SELECT /*+ QB_NAME(QB1) */ * FROM (SELECT * FROM t) t1, (SELECT * FROM t) t2;
```

This hint specifies the outer `SELECT` query block's name to `QB1`, which makes `QB1` and the default name `sel_1` both valid for the query block.

> **Note:**
>
> In the above example, if the hint specifies the `QB_NAME` to `sel_2` and does not specify a new `QB_NAME` for the original second `SELECT` query block, then `sel_2` becomes an invalid name for the second `SELECT` query block.
### SET_VAR(VAR_NAME=VAR_VALUE)

You can temporarily modify the value of system variables during statement execution by using the `SET_VAR(VAR_NAME=VAR_VALUE)` hint. After the statement is executed, the value of the system variable in the current session is automatically restored to the original value. This hint can be used to modify some system variables related to the optimizer and executor. For a list of system variables that can be modified using this hint, refer to [System variables](https://docs.pingcap.com/tidb/stable/system-variables).

> **Warning:**
>
> It is strongly recommended not to modify variables that are not explicitly supported, as this might cause unpredictable behavior.

The following is an example:

```sql
SELECT /*+ SET_VAR(MAX_EXECUTION_TIME=1234) */ @@MAX_EXECUTION_TIME;
SELECT @@MAX_EXECUTION_TIME;
```

After executing the preceding SQL statements, the first query returns the value `1234` set in the hint, instead of the default value of `MAX_EXECUTION_TIME`. The second query returns the default value of the variable.

```sql
+----------------------+
| @@MAX_EXECUTION_TIME |
+----------------------+
|                 1234 |
+----------------------+
1 row in set (0.00 sec)
+----------------------+
| @@MAX_EXECUTION_TIME |
+----------------------+
|                    0 |
+----------------------+
1 row in set (0.00 sec)
```
