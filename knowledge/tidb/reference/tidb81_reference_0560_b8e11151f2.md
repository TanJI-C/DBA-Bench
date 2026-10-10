# CREATE TABLE LIKE syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-table-like.md`
- Source Title: `CREATE TABLE LIKE | TiDB SQL Statement Reference`
- Source Heading Path: `CREATE TABLE LIKE | CREATE TABLE LIKE > Synopsis | CREATE TABLE LIKE > Examples | CREATE TABLE LIKE > Pre-split region | CREATE TABLE LIKE > MySQL compatibility | CREATE TABLE LIKE > See also`
- Source Line Ranges: `5-67`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `create-table-like`, `ddl`, `syntax`, `examples`, `pre-split-regions`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0560_b8e11151f2`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-table-like.md#create-table-like`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3927f9011167feb851a929dceeff5fedbc4d2397955845130442765bb2a44d09`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table-like#create-table-like
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-table-like.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about the SQL syntax, behavior, examples, pre-split region inheritance, or MySQL compatibility of `CREATE TABLE LIKE`.
- Retrieval Keywords: CREATE TABLE LIKE, CreateTableLikeStmt, LIKE TableName, OptTemporary, GLOBAL TEMPORARY, ON COMMIT DELETE ROWS, CREATE TABLE t2 LIKE t1, copies the definition of an existing table, without copying any data, PRE_SPLIT_REGIONS, MySQL compatibility, SHOW CREATE TABLE
- Follow-up Guidance: The source also points to `CREATE TABLE` for `PRE_SPLIT_REGIONS` details and to `SHOW CREATE TABLE` in See also.
- Classification Note: This is classified as a SQL reference because the content provides formal syntax, example statements, and compatibility notes for the `CREATE TABLE LIKE` statement.

## Official Source Content

# CREATE TABLE LIKE

This statement copies the definition of an existing table, without copying any data.
## Synopsis

```ebnf+diagram
CreateTableLikeStmt ::=
    'CREATE' OptTemporary 'TABLE' IfNotExists TableName LikeTableWithOrWithoutParen OnCommitOpt

OptTemporary ::=
    ( 'TEMPORARY' | ('GLOBAL' 'TEMPORARY') )?

LikeTableWithOrWithoutParen ::=
    'LIKE' TableName
|   '(' 'LIKE' TableName ')'

OnCommitOpt ::=
    ('ON' 'COMMIT' 'DELETE' 'ROWS')?
```
## Examples

```sql
mysql> CREATE TABLE t1 (a INT NOT NULL);
Query OK, 0 rows affected (0.13 sec)

mysql> INSERT INTO t1 VALUES (1),(2),(3),(4),(5);
Query OK, 5 rows affected (0.02 sec)
Records: 5  Duplicates: 0  Warnings: 0

mysql> SELECT * FROM t1;
+---+
| a |
+---+
| 1 |
| 2 |
| 3 |
| 4 |
| 5 |
+---+
5 rows in set (0.00 sec)

mysql> CREATE TABLE t2 LIKE t1;
Query OK, 0 rows affected (0.10 sec)

mysql> SELECT * FROM t2;
Empty set (0.00 sec)
```
## Pre-split region

If the table to be copied is defined with the `PRE_SPLIT_REGIONS` attribute, the table created using the `CREATE TABLE LIKE` statement inherits this attribute, and the Region on the new table will be split. For details of `PRE_SPLIT_REGIONS`, see [`CREATE TABLE` Statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table).
## MySQL compatibility

The `CREATE TABLE LIKE` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
