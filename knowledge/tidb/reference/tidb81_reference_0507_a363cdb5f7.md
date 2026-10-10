# ADMIN CHECK TABLE and INDEX syntax, principles, and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-check-table-index.md`
- Source Title: `ADMIN CHECK [TABLE|INDEX] | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN CHECK [TABLE|INDEX] | ADMIN CHECK [TABLE|INDEX] > Principles | ADMIN CHECK [TABLE|INDEX] > Synopsis | ADMIN CHECK [TABLE|INDEX] > Examples | ADMIN CHECK [TABLE|INDEX] > MySQL compatibility | ADMIN CHECK [TABLE|INDEX] > See also`
- Source Line Ranges: `6-68`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `admin check`, `table consistency`, `index consistency`, `syntax`, `examples`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0507_a363cdb5f7`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-check-table-index.md#admin-check-table-index`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `199f343a9761ebe12cc1c4f9be24b4427f2f423561f1b0a3c84a9a02493dfbd3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-check-table-index#admin-check-table-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-check-table-index.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax, behavior, limitations, or examples of `ADMIN CHECK TABLE` or `ADMIN CHECK INDEX` for checking table and index data consistency in TiDB.
- Retrieval Keywords: ADMIN CHECK TABLE, ADMIN CHECK INDEX, AdminCheckStmt, HandleRange, TableNameList, data consistency of tables and indexes, clustered primary key, FOREIGN KEY constraints, TiDB extension to MySQL syntax, ADMIN CHECK INDEX tbl_name idx_name, ADMIN CHECK TABLE tbl_name, (lower_val, upper_val)
- Follow-up Guidance: If `ADMIN CHECK [TABLE|INDEX]` finds issues, the content says you can resolve them by dropping and recreating the index, and if the issue is not resolved, report a bug.
- Classification Note: This is reference content because it defines statement purpose, unsupported cases, checking principles, formal synopsis, examples, and MySQL compatibility for the SQL statement.

## Official Source Content

# ADMIN CHECK [TABLE|INDEX]

The `ADMIN CHECK [TABLE|INDEX]` statement checks for data consistency of tables and indexes.

It does not support the following:

- Checking [FOREIGN KEY constraints](https://docs.pingcap.com/tidb/stable/foreign-key).
- Checking the PRIMARY KEY index if a [clustered primary key](https://docs.pingcap.com/tidb/stable/clustered-indexes) is used.

If `ADMIN CHECK [TABLE|INDEX]` finds any issues, you can resolve them by dropping and recreating the index. If the issue is not resolved, you can [report a bug](https://docs.pingcap.com/tidb/stable/support).
## Principles

The `ADMIN CHECK TABLE` statement takes the following steps to check the table:

1. For each index, it checks if the number of records in the index is the same as that in the table.

2. For each index, it loops over the values in each row and compares the values with that in the table.

If you use the `ADMIN CHECK INDEX` statement, it only checks the specified index.
## Synopsis

```ebnf+diagram
AdminCheckStmt ::=
    'ADMIN' 'CHECK' ( 'TABLE' TableNameList | 'INDEX' TableName Identifier ( HandleRange ( ',' HandleRange )* )? ) 

TableNameList ::=
    TableName ( ',' TableName )*

HandleRange ::= '(' Int64Num ',' Int64Num ')'
```
## Examples

To check the consistency of all the data and corresponding indexes in the `tbl_name` table, use `ADMIN CHECK TABLE`:

```sql
ADMIN CHECK TABLE tbl_name [, tbl_name] ...;
```

If the consistency check is passed, an empty result is returned. Otherwise, an error message is returned indicating that the data is inconsistent.

```sql
ADMIN CHECK INDEX tbl_name idx_name;
```

The above statement is used to check the consistency of the column data and index data corresponding to the `idx_name` index in the `tbl_name` table. If the consistency check is passed, an empty result is returned; otherwise, an error message is returned indicating that the data is inconsistent.

```sql
ADMIN CHECK INDEX tbl_name idx_name (lower_val, upper_val) [, (lower_val, upper_val)] ...;
```

The above statement is used to check the consistency of the column data and index data corresponding to the `idx_name` index in the `tbl_name` table, with the data range (to be checked) specified. If the consistency check is passed, an empty result is returned. Otherwise, an error message is returned indicating that the data is inconsistent.
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [`ADMIN REPAIR`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin#admin-repair-statement)
