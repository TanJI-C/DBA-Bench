# Check whether a primary key is clustered

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clustered-indexes.md`
- Source Title: `Clustered Indexes`
- Source Heading Path: `Clustered Indexes > Usages > Check whether the primary key is a clustered index`
- Source Line Ranges: `93-140`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `clustered-index`, `primary-key`, `show-create-table`, `show-index`, `information-schema`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0032_cfe2da7646`
- Source ID: `tidb-docs-8.1:clustered-indexes.md#check-whether-the-primary-key-is-a-clustered-index`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5d742f89a9f3c6b0415aa0fc01ad243c486f0f5b5c0252e6e14946e79057738f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clustered-indexes#check-whether-the-primary-key-is-a-clustered-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clustered-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when you need to verify whether a table primary key is a clustered index in TiDB using SQL output or system table metadata.
- Retrieval Keywords: Check whether the primary key is a clustered index, SHOW CREATE TABLE, SHOW INDEX FROM, information_schema.tables, TIDB_PK_TYPE, Clustered column, CLUSTERED, NONCLUSTERED, SELECT TIDB_PK_TYPE FROM information_schema.tables WHERE table_schema = 'test' AND table_name = 't'
- Follow-up Guidance: The source gives three exact verification methods: inspect PRIMARY KEY in SHOW CREATE TABLE, inspect the Clustered column in SHOW INDEX FROM, or query information_schema.tables.TIDB_PK_TYPE.
- Classification Note: This is operation content because it describes concrete verification methods and exact SQL statements to check whether a primary key is clustered.

## Official Source Content

### Check whether the primary key is a clustered index

You can check whether the primary key of a table is a clustered index using one of the following methods:

- Execute the command `SHOW CREATE TABLE`.
- Execute the command `SHOW INDEX FROM`.
- Query the `TIDB_PK_TYPE` column in the system table `information_schema.tables`.

By running the command `SHOW CREATE TABLE`, you can see whether the attribute of `PRIMARY KEY` is `CLUSTERED` or `NONCLUSTERED`. For example:

```sql
mysql> SHOW CREATE TABLE t;
+-------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Table | Create Table                                                                                                                                                                                      |
+-------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t     | CREATE TABLE `t` (
  `a` bigint(20) NOT NULL,
  `b` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`a`) /*T![clustered_index] CLUSTERED */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin |
+-------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.01 sec)
```

By running the command `SHOW INDEX FROM`, you can check whether the result in the column `Clustered` shows `YES` or `NO`. For example:

```sql
mysql> SHOW INDEX FROM t;
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+-----------+
| Table | Non_unique | Key_name | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment | Visible | Expression | Clustered |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+-----------+
| t     |          0 | PRIMARY  |            1 | a           | A         |           0 |     NULL | NULL   |      | BTREE      |         |               | YES     | NULL       | YES       |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+-----------+
1 row in set (0.01 sec)
```

You can also query the column `TIDB_PK_TYPE` in the system table `information_schema.tables` to see whether the result is `CLUSTERED` or `NONCLUSTERED`. For example:

```sql
mysql> SELECT TIDB_PK_TYPE FROM information_schema.tables WHERE table_schema = 'test' AND table_name = 't';
+--------------+
| TIDB_PK_TYPE |
+--------------+
| CLUSTERED    |
+--------------+
1 row in set (0.03 sec)
```
