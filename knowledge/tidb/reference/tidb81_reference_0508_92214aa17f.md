# ADMIN CHECKSUM TABLE syntax and usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-checksum-table.md`
- Source Title: `ADMIN CHECKSUM TABLE | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN CHECKSUM TABLE | ADMIN CHECKSUM TABLE > Synopsis | ADMIN CHECKSUM TABLE > Examples | ADMIN CHECKSUM TABLE > MySQL compatibility`
- Source Line Ranges: `6-70`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `lightning`, `dm`
- Topic Tags: `checksum`, `crc64`, `table-integrity`, `import-validation`, `syntax`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0508_92214aa17f`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-checksum-table.md#admin-checksum-table`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b6aae877095520a1b64845c7acf0262df8ecebc9eb1060e5c4c1d14ba5226ce9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-checksum-table#admin-checksum-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-checksum-table.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, purpose, output fields, or import-validation behavior of the `ADMIN CHECKSUM TABLE` statement in TiDB.
- Retrieval Keywords: ADMIN CHECKSUM TABLE, AdminChecksumTableStmt, TableNameList, CRC64 checksum, Checksum_crc64_xor, Total_kvs, Total_bytes, table_id, validate data integrity, IMPORT INTO, TiDB Lightning, TiDB Data Migration, DM, MySQL compatibility, TiDB extension to MySQL syntax
- Follow-up Guidance: The source includes an example with `CREATE TABLE t1(id INT PRIMARY KEY)`, `INSERT INTO t1 VALUES (1),(2),(3)`, and `ADMIN CHECKSUM TABLE t1;` plus the returned checksum result columns.
- Classification Note: This is a SQL reference chunk because it defines the `ADMIN CHECKSUM TABLE` statement syntax, explains checksum behavior and import validation usage, shows example output, and notes MySQL compatibility.

## Official Source Content

# ADMIN CHECKSUM TABLE

The `ADMIN CHECKSUM TABLE` statement calculates a CRC64 checksum for the data and indexes of a table.

The [checksum](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#checksum) is calculated based on table data and properties such as `table_id`. This means that two tables with the same data but different `table_id` values will get different checksums.

After importing a table using [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview), [TiDB Data Migration](https://docs.pingcap.com/tidb/stable/dm/dm-overview), or [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into), `ADMIN CHECKSUM TABLE <table>` is executed by default to validate data integrity.

The [checksum](https://docs.pingcap.com/tidb/stable/tidb-lightning-glossary#checksum) is calculated over the table data and properties like the `table_id`. This means that two tables with the same data but different `table_id` values will get different checksums.

After importing a table using [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into), `ADMIN CHECKSUM TABLE <table>` is executed by default to validate data integrity.
## Synopsis

```ebnf+diagram
AdminChecksumTableStmt ::=
    'ADMIN' 'CHECKSUM' 'TABLE' TableNameList

TableNameList ::=
    TableName ( ',' TableName )*
```
## Examples

Create table `t1`:

```sql
CREATE TABLE t1(id INT PRIMARY KEY);
```

Insert some data into `t1`:

```sql
INSERT INTO t1 VALUES (1),(2),(3);
```

Calculate the checksum for `t1`:

```sql
ADMIN CHECKSUM TABLE t1;
```

The output is as follows:

```sql
+---------+------------+----------------------+-----------+-------------+
| Db_name | Table_name | Checksum_crc64_xor   | Total_kvs | Total_bytes |
+---------+------------+----------------------+-----------+-------------+
| test    | t1         | 10909174369497628533 |         3 |          75 |
+---------+------------+----------------------+-----------+-------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
