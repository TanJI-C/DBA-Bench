# CREATE TABLE examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-table.md`
- Source Title: `CREATE TABLE | TiDB SQL Statement Reference`
- Source Heading Path: `CREATE TABLE > Examples`
- Source Line Ranges: `188-269`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `create-table`, `examples`, `show-create-table`, `desc`, `insert`, `if-not-exists`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0562_27c28d345f`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-table.md#examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8115528955d8ce6b5b8473f613bb47f918cc28801a5d5a6b9deaad86992442d4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-table.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants concrete CREATE TABLE examples with DESC, SHOW CREATE TABLE, INSERT INTO, SELECT, or IF NOT EXISTS usage and resulting output.
- Retrieval Keywords: CREATE TABLE t1 (a int), DESC t1, SHOW CREATE TABLE t1, INSERT INTO t1 (a) VALUES (1), SELECT * FROM t1, DROP TABLE IF EXISTS t1, CREATE TABLE IF NOT EXISTS t1, PRIMARY KEY auto_increment, VARCHAR(200) NOT NULL, ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
- Follow-up Guidance: The examples include both a simple table creation flow and a conditional DROP TABLE IF EXISTS plus CREATE TABLE IF NOT EXISTS flow with DESC output.
- Classification Note: This is reference content presented as executable SQL examples and their returned results for CREATE TABLE behavior.

## Official Source Content

## Examples

Creating a simple table and inserting one row:

```sql
CREATE TABLE t1 (a int);
DESC t1;
SHOW CREATE TABLE t1\G
INSERT INTO t1 (a) VALUES (1);
SELECT * FROM t1;
```

```
mysql> drop table if exists t1;
Query OK, 0 rows affected (0.23 sec)

mysql> CREATE TABLE t1 (a int);
Query OK, 0 rows affected (0.09 sec)

mysql> DESC t1;
+-------+---------+------+------+---------+-------+
| Field | Type    | Null | Key  | Default | Extra |
+-------+---------+------+------+---------+-------+
| a     | int(11) | YES  |      | NULL    |       |
+-------+---------+------+------+---------+-------+
1 row in set (0.00 sec)

mysql> SHOW CREATE TABLE t1\G
*************************** 1. row ***************************
       Table: t1
Create Table: CREATE TABLE `t1` (
  `a` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
1 row in set (0.00 sec)

mysql> INSERT INTO t1 (a) VALUES (1);
Query OK, 1 row affected (0.03 sec)

mysql> SELECT * FROM t1;
+------+
| a    |
+------+
|    1 |
+------+
1 row in set (0.00 sec)
```

Dropping a table if it exists, and conditionally creating a table if it does not exist:

```sql
DROP TABLE IF EXISTS t1;
CREATE TABLE IF NOT EXISTS t1 (
 id BIGINT NOT NULL PRIMARY KEY auto_increment,
 b VARCHAR(200) NOT NULL
);
DESC t1;
```

```sql
mysql> DROP TABLE IF EXISTS t1;
Query OK, 0 rows affected (0.22 sec)

mysql> CREATE TABLE IF NOT EXISTS t1 (
         id BIGINT NOT NULL PRIMARY KEY auto_increment,
         b VARCHAR(200) NOT NULL
        );
Query OK, 0 rows affected (0.08 sec)

mysql> DESC t1;
+-------+--------------+------+------+---------+----------------+
| Field | Type         | Null | Key  | Default | Extra          |
+-------+--------------+------+------+---------+----------------+
| id    | bigint(20)   | NO   | PRI  | NULL    | auto_increment |
| b     | varchar(200) | NO   |      | NULL    |                |
+-------+--------------+------+------+---------+----------------+
2 rows in set (0.00 sec)
```
