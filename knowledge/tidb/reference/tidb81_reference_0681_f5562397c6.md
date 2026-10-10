# SHOW TABLE NEXT_ROW_ID syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-table-next-rowid.md`
- Source Title: `SHOW TABLE NEXT_ROW_ID`
- Source Heading Path: `SHOW TABLE NEXT_ROW_ID | SHOW TABLE NEXT_ROW_ID > Synopsis | SHOW TABLE NEXT_ROW_ID > Examples | SHOW TABLE NEXT_ROW_ID > MySQL compatibility | SHOW TABLE NEXT_ROW_ID > See also`
- Source Line Ranges: `5-68`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show statement`, `next_row_id`, `auto_increment`, `auto_random`, `sequence`, `_tidb_rowid`, `mysql compatibility`, `syntax`, `examples`, `auto_id_cache`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0681_f5562397c6`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-table-next-rowid.md#show-table-next-row-id`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `14264386751feb57414f28e522f6462818d9a826d4e43f6213f220e9838c36d9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-next-rowid#show-table-next-row-id
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-table-next-rowid.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for the syntax, output meaning, examples, or MySQL compatibility of SHOW TABLE ... NEXT_ROW_ID for _tidb_rowid, AUTO_INCREMENT, AUTO_RANDOM, or SEQUENCE.
- Retrieval Keywords: SHOW TABLE NEXT_ROW_ID, SHOW TABLE t NEXT_ROW_ID, ShowTableNextRowIDStmt, NEXT_GLOBAL_ROW_ID, _tidb_rowid, AUTO_INCREMENT, AUTO_RANDOM, SEQUENCE, AUTO_ID_CACHE, TiDB extension to MySQL syntax, DB_NAME TABLE_NAME COLUMN_NAME NEXT_GLOBAL_ROW_ID
- Follow-up Guidance: The source also points to related references for CREATE TABLE, AUTO_RANDOM, CREATE_SEQUENCE, and _tidb_rowid.
- Classification Note: This is reference content because it defines the SHOW TABLE NEXT_ROW_ID statement syntax, states what special columns it reports, and gives concrete SQL examples and compatibility notes.

## Official Source Content

# SHOW TABLE NEXT_ROW_ID

`SHOW TABLE NEXT_ROW_ID` is used to show the details of some special columns of a table, including:

* [`_tidb_rowid`](https://docs.pingcap.com/tidb/stable/tidb-rowid), the hidden row ID column automatically managed by TiDB for supported tables.
* `AUTO_INCREMENT` column created by users.
* [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/auto-random) column created by users.
* [`SEQUENCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence) created by users.
## Synopsis

```ebnf+diagram
ShowTableNextRowIDStmt ::=
    "SHOW" "TABLE" (SchemaName ".")? TableName "NEXT_ROW_ID"
```
## Examples

For newly created tables, `NEXT_GLOBAL_ROW_ID` is `1` because no Row ID is allocated.

```sql
CREATE TABLE t(a int);
Query OK, 0 rows affected (0.06 sec)
```

```sql
SHOW TABLE t NEXT_ROW_ID;
+---------+------------+-------------+--------------------+
| DB_NAME | TABLE_NAME | COLUMN_NAME | NEXT_GLOBAL_ROW_ID |
+---------+------------+-------------+--------------------+
| test    | t          | _tidb_rowid |                  1 |
+---------+------------+-------------+--------------------+
1 row in set (0.00 sec)
```

Data have been written to the table. The TiDB server that inserts the data allocates and caches 30000 IDs at once. Thus, NEXT_GLOBAL_ROW_ID is 30001 now. The number of IDs is controlled by [`AUTO_ID_CACHE`](https://docs.pingcap.com/tidb/stable/auto-increment#auto_id_cache).

```sql
INSERT INTO t VALUES (), (), ();
Query OK, 3 rows affected (0.02 sec)
Records: 3  Duplicates: 0  Warnings: 0
```

```sql
SHOW TABLE t NEXT_ROW_ID;
+---------+------------+-------------+--------------------+
| DB_NAME | TABLE_NAME | COLUMN_NAME | NEXT_GLOBAL_ROW_ID |
+---------+------------+-------------+--------------------+
| test    | t          | _tidb_rowid |              30001 |
+---------+------------+-------------+--------------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [AUTO_RANDOM](https://docs.pingcap.com/tidb/stable/auto-random)
* [CREATE_SEQUENCE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence)
* [_tidb_rowid](https://docs.pingcap.com/tidb/stable/tidb-rowid)
