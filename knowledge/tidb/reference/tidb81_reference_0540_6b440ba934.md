# BATCH syntax, behavior, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-batch.md`
- Source Title: `BATCH`
- Source Heading Path: `BATCH | BATCH > Synopsis | BATCH > MySQL compatibility | BATCH > See also`
- Source Line Ranges: `5-56`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `batch`, `non-transactional-dml`, `insert`, `replace`, `update`, `delete`, `dry-run`, `syntax`, `mysql-compatibility`, `joins`, `ambiguity`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0540_6b440ba934`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-batch.md#batch`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1d6c13c0351c6a81dfe432521fdfe0f121dc27e0c0c18f0bc49eae814dc162c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-batch#batch
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-batch.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB-specific BATCH statement syntax, supported DML types, non-transactional behavior, dry-run options, or join-column ambiguity details.
- Retrieval Keywords: BATCH, NonTransactionalDMLStmt, DryRunOptions, ShardableStmt, BATCH ON ColumnName LIMIT NUM, DRY RUN, DRY RUN QUERY, non-transactional DML, INSERT, REPLACE, UPDATE, DELETE, MySQL compatibility, TiDB-specific, multi-table join, shard column must be fully specified, Non-transactional DML, shard column must be fully specified, Unknown column '<alias>.<column>' in 'where clause', table aliases might not be preserved
- Follow-up Guidance: For details about usage and restrictions, see Non-transactional DML statements, and use DRY RUN QUERY or DRY RUN to preview the split statements before execution.
- Classification Note: This is a SQL reference chunk because it defines BATCH syntax, execution behavior, supported statement forms, and compatibility notes for TiDB SQL.

## Official Source Content

# BATCH

The `BATCH` syntax splits a DML statement into multiple statements in TiDB for execution. This means that there are **no guarantees** of transactional atomicity and isolation. Therefore, it is a "non-transactional" statement.

Currently, `INSERT`, `REPLACE`, `UPDATE`, and `DELETE` are supported in `BATCH`.

Based on a column, the `BATCH` syntax divides a DML statement into multiple ranges of scope for execution. In each range, a single SQL statement is executed.

For details about the usage and restrictions, see [Non-transactional DML statements](https://docs.pingcap.com/tidb/stable/non-transactional-dml).

When you use multi-table join in a `BATCH` statement, you need to specify the full path of the column to avoid ambiguity:

```sql
BATCH ON test.t2.id LIMIT 1 INSERT INTO t SELECT t2.id, t2.v, t3.v FROM t2 JOIN t3 ON t2.k = t3.k;
```

The preceding statement specifies the column to be split as `test.t2.id`, which is unambiguous. If you use the `id` as follows, an error is reported:

```sql
BATCH ON id LIMIT 1 INSERT INTO t SELECT t2.id, t2.v, t3.v FROM t2 JOIN t3 ON t2.k = t3.k;

Non-transactional DML, shard column must be fully specified
```

> **Note:**
>
> The `BATCH` statement is internally rewritten and split into multiple DML statements during execution. In the current version, table aliases might not be preserved, which can result in errors such as `Unknown column '<alias>.<column>' in 'where clause'`. To avoid this issue, do not use table aliases. Before execution, use `DRY RUN QUERY` or `DRY RUN` to preview the split statements before execution. For more information, see [Non-Transactional DML Statements](https://docs.pingcap.com/tidb/stable/non-transactional-dml).
## Synopsis

```ebnf+diagram
NonTransactionalDMLStmt ::=
    'BATCH' ( 'ON' ColumnName )? 'LIMIT' NUM DryRunOptions? ShardableStmt

DryRunOptions ::=
    'DRY' 'RUN' 'QUERY'?

ShardableStmt ::=
    DeleteFromStmt
|   UpdateStmt
|   InsertIntoStmt
|   ReplaceIntoStmt
```
## MySQL compatibility

The `BATCH` syntax is TiDB-specific and not compatible with MySQL.
## See also

* [Non-transactional DML statements](https://docs.pingcap.com/tidb/stable/non-transactional-dml)
