# SHOW INDEXES syntax, examples, compatibility, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-indexes.md`
- Source Title: `SHOW INDEXES [FROM|IN] | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW INDEXES [FROM|IN] | SHOW INDEXES [FROM|IN] > Synopsis | SHOW INDEXES [FROM|IN] > Examples | SHOW INDEXES [FROM|IN] > MySQL compatibility | SHOW INDEXES [FROM|IN] > See also`
- Source Line Ranges: `5-69`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `show indexes`, `show keys`, `show index`, `syntax`, `examples`, `mysql compatibility`, `index metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0663_467bff4bec`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-indexes.md#show-indexes-from-in`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4685c7d770f08cff35275ac56465d3a71ee116b05392857ca2f1c17a6be60f5b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-indexes#show-indexes-from-in
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-indexes.md

## Retrieval Guidance

- Use When: Use this content when the user asks for the syntax, aliases, output columns, examples, or MySQL compatibility of listing indexes on a table with SHOW INDEXES, SHOW INDEX, or SHOW KEYS.
- Retrieval Keywords: SHOW INDEXES, SHOW INDEX, SHOW KEYS, SHOW INDEXES FROM, SHOW INDEX FROM, SHOW KEYS FROM, ShowIndexStmt, ShowLikeOrWhere, LIKE SimpleExpr, WHERE Expression, TableName, SchemaName, index metadata, Non_unique, Key_name, Seq_in_index, Column_name, Collation, Cardinality, Sub_part, Packed, Null, Index_type, Comment, Index_comment, Visible, Expression, HASH, BTREE, RTREE, information_schema.TIDB_INDEXES, information_schema.TIDB_INDEX_USAGE, information_schema.KEY_COLUMN_USAGE, sys.schema_unused_indexes, SHOW CREATE TABLE, DROP INDEX, CREATE INDEX
- Follow-up Guidance: The page also points to related statements and metadata sources including SHOW CREATE TABLE, DROP INDEX, CREATE INDEX, information_schema.TIDB_INDEXES, information_schema.TIDB_INDEX_USAGE, information_schema.KEY_COLUMN_USAGE, and sys.schema_unused_indexes.
- Classification Note: This chunk is reference documentation because it provides the formal SHOW INDEXES syntax, example result sets, alias compatibility with SHOW INDEX and SHOW KEYS, and related reference links.

## Official Source Content

# SHOW INDEXES [FROM|IN]

The statement `SHOW INDEXES [FROM|IN]` lists the indexes on a specified table. The statements `SHOW INDEX [FROM|IN]`, `SHOW KEYS [FROM|IN]` are aliases of this statement, and included for compatibility with MySQL.
## Synopsis

```ebnf+diagram
ShowIndexStmt ::=
    "SHOW" ( "INDEX" | "INDEXES" | "KEYS" ) ("FROM" | "IN" ) TableName (("FROM" | "IN") SchemaName )? ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

```sql
mysql> CREATE TABLE t1 (id int not null primary key AUTO_INCREMENT, col1 INT, INDEX(col1));
Query OK, 0 rows affected (0.12 sec)

mysql> SHOW INDEXES FROM t1;
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
| Table | Non_unique | Key_name | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment | Visible | Expression |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
| t1    |          0 | PRIMARY  |            1 | id          | A         |           0 |     NULL | NULL   |      | BTREE      |         |               | YES     | NULL       |
| t1    |          1 | col1     |            1 | col1        | A         |           0 |     NULL | NULL   | YES  | BTREE      |         |               | YES     | NULL       |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
2 rows in set (0.00 sec)

mysql> SHOW INDEX FROM t1;
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
| Table | Non_unique | Key_name | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment | Visible | Expression |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
| t1    |          0 | PRIMARY  |            1 | id          | A         |           0 |     NULL | NULL   |      | BTREE      |         |               | YES     | NULL       |
| t1    |          1 | col1     |            1 | col1        | A         |           0 |     NULL | NULL   | YES  | BTREE      |         |               | YES     | NULL       |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
2 rows in set (0.00 sec)

mysql> SHOW KEYS FROM t1;
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
| Table | Non_unique | Key_name | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment | Visible | Expression |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
| t1    |          0 | PRIMARY  |            1 | id          | A         |           0 |     NULL | NULL   |      | BTREE      |         |               | YES     | NULL       |
| t1    |          1 | col1     |            1 | col1        | A         |           0 |     NULL | NULL   | YES  | BTREE      |         |               | YES     | NULL       |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
2 rows in set (0.00 sec)
```

Note that TiDB accepts index types such as `HASH`, `BTREE` and `RTREE` in syntax for compatibility with MySQL, but ignores them.
## MySQL compatibility

The `SHOW INDEXES [FROM|IN]` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
* [DROP INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-index)
* [CREATE INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index)
* [`information_schema.TIDB_INDEXES`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-indexes)
* [`information_schema.TIDB_INDEX_USAGE`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-index-usage)
* [`information_schema.KEY_COLUMN_USAGE`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-key-column-usage)
* [`sys.schema_unused_indexes`](https://docs.pingcap.com/tidb/stable/sys-schema/sys-schema-unused-indexes)
