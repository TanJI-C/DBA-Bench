# MariaDB migration prerequisites and compatibility checks

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-mariadb.md`
- Source Title: `Migrate Data from MariaDB to TiDB`
- Source Heading Path: `Migrate Data from MariaDB to TiDB | Migrate Data from MariaDB to TiDB > Prerequisites | Migrate Data from MariaDB to TiDB > Check compatibility | Migrate Data from MariaDB to TiDB > Check compatibility > Authentication | Migrate Data from MariaDB to TiDB > Check compatibility > System-versioned tables | Migrate Data from MariaDB to TiDB > Check compatibility > Sequences | Migrate Data from MariaDB to TiDB > Check compatibility > Storage engines | Migrate Data from MariaDB to TiDB > Check compatibility > Syntax | Migrate Data from MariaDB to TiDB > Check compatibility > Data types | Migrate Data from MariaDB to TiDB > Check compatibility > Character set and collation`
- Source Line Ranges: `5-254`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dm`, `tidb`
- Topic Tags: `migration-strategy`, `prerequisites`, `compatibility`, `authentication`, `system-versioned-tables`, `sequences`, `storage-engines`, `sql-syntax`, `data-types`, `character-set`, `collation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0441_143c491c70`
- Source ID: `tidb-docs-8.1:migrate-from-mariadb.md#migrate-data-from-mariadb-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `44413c4b3ee8014dd9eec4ac96daf77bd0d4297272bda60ec9e6f25d5dec3267`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-mariadb#migrate-data-from-mariadb-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-mariadb.md

## Retrieval Guidance

- Use When: Use this chunk when assessing MariaDB-to-TiDB migration prerequisites, choosing between Dumpling plus TiDB Lightning or DM, and checking MariaDB-specific compatibility items before migration.
- Retrieval Keywords: Migrate Data from MariaDB to TiDB, Prerequisites, Check compatibility, dump data with Dumpling and restore data with TiDB Lightning, Replicate data with DM, DM Compatibility Catalog, SELECT plugin, COUNT(*) FROM mysql.user GROUP BY plugin, mysql.user, authentication methods, system-versioned tables, TABLE_TYPE='SYSTEM VERSIONED', ALTER TABLE t DROP SYSTEM VERSIONING, AS OF TIMESTAMP, CREATE SEQUENCE, TABLE_TYPE='SEQUENCE', storage engines, CONNECT storage engine, Spider, SELECT ENGINE, COUNT(*) FROM information_schema.tables GROUP BY ENGINE, RETURNING keyword, DELETE INSERT REPLACE RETURNING, UUID, INET4, INET6, information_schema.columns, latin1_swedish_ci, SHOW COLLATION, Character Set and Collation, SELECT TABLE_SCHEMA, COLLATION_NAME, COUNT(*) FROM information_schema.columns GROUP BY TABLE_SCHEMA, COLLATION_NAME
- Follow-up Guidance: The source also provides exact SQL checks for authentication plugins, system-versioned tables, sequences, storage engines, unsupported data types, and collations, plus references to Security Compatibility with MySQL and Character Set and Collation.
- Classification Note: This is reference content because it summarizes migration strategy prerequisites and compatibility checks, including exact SQL statements and feature limitations described in the official documentation.

## Official Source Content

# Migrate Data from MariaDB to TiDB

This document describes how to migrate data from a MariaDB server installation to a TiDB cluster.
## Prerequisites

Choose the right migration strategy:

- The first strategy is to [dump data with Dumpling and restore data with TiDB Lightning](#dump-data-with-dumpling-and-restore-data-with-tidb-lightning). This works for all versions of MariaDB. The drawback of this strategy is that it needs more downtime.
- The second strategy is to [Replicate data with DM](#replicate-data-with-dm) from MariaDB to TiDB with DM. DM does not support all versions of MariaDB. Supported versions are listed on the [DM Compatibility Catalog](https://docs.pingcap.com/tidb/stable/dm/dm-compatibility-catalog#compatibility-catalog-of-tidb-data-migration).

Besides these two strategies, there might be other strategies available specifically to your situation. For example:

- Use the functionality of your Object Relational Mapping (ORM) to re-deploy and migrate your data.
- Modify your application to write from both MariaDB and TiDB while the migration is ongoing.

This document only covers the first two strategies.

Prepare the following based on the strategy you choose:

- For the **dump and restore** strategy:
    - Install [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) and [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview).
    - Make sure you have the [required privileges](https://docs.pingcap.com/tidb/stable/dumpling-overview#required-privileges) on the MariaDB server for Dumpling to export data.
- For the **data replication** strategy, set up [Data Migration (DM)](https://docs.pingcap.com/tidb/stable/dm/dm-overview).
## Check compatibility

TiDB is [compatible with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility), and MySQL and MariaDB have a lot of functionality in common. However, there might be MariaDB-specific features that might not be compatible with TiDB that you should be aware of before migrating.

Besides checking the items in this section, it is recommended that you also check the [Compatibility and Differences](https://mariadb.com/docs/release-notes/community-server/about/compatibility-and-differences) in the MariaDB documentation.
### Authentication

The [Security Compatibility with MySQL](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql) document lists authentication methods that TiDB supports. TiDB does not support a few authentication methods in MariaDB. This means that you might have to create a new password hash for the account or take other specific measures.

To check what authentication methods are used, you can run the following statement:

```sql
SELECT
  plugin,
  COUNT(*)
FROM
  mysql.user
GROUP BY
  plugin;
```

```sql
+-----------------------+----------+
| plugin                | COUNT(*) |
+-----------------------+----------+
| mysql_native_password |       11 |
+-----------------------+----------+
1 row in set (0.002 sec)
```
### System-versioned tables

TiDB does not support [system-versioned tables](https://mariadb.com/docs/server/reference/sql-structure/temporal-tables/system-versioned-tables). However, TiDB does support [`AS OF TIMESTAMP`](https://docs.pingcap.com/tidb/stable/as-of-timestamp) which might replace some of the use cases of system-versioned tables.

You can check for affected tables with the following statement:

```sql
SELECT
  TABLE_SCHEMA,
  TABLE_NAME
FROM
  information_schema.tables
WHERE
  TABLE_TYPE='SYSTEM VERSIONED';
```

```sql
+--------------+------------+
| TABLE_SCHEMA | TABLE_NAME |
+--------------+------------+
| test         | t          |
+--------------+------------+
1 row in set (0.005 sec)
```

To remove system versioning, execute the `ALTER TABLE` statement:

```sql
MariaDB [test]> ALTER TABLE t DROP SYSTEM VERSIONING;
Query OK, 0 rows affected (0.071 sec)
Records: 0  Duplicates: 0  Warnings: 0
```
### Sequences

Both MariaDB and TiDB support [`CREATE SEQUENCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence). However, it is currently not supported by DM. It is recommended that you do not create, modify, or remove sequences during the migration and test this specifically after migration.

To check if you are using sequences, execute the following statement:

```sql
SELECT
  TABLE_SCHEMA,
  TABLE_NAME
FROM
  information_schema.tables
WHERE
  TABLE_TYPE='SEQUENCE';
```

```sql
+--------------+------------+
| TABLE_SCHEMA | TABLE_NAME |
+--------------+------------+
| test         | s1         |
+--------------+------------+
1 row in set (0.016 sec)
```
### Storage engines

MariaDB offers storage engines for local data such as `InnoDB`, `MyISAM` and `Aria`. While the data format is not directly supported by TiDB, migrating these works fine. However, some engines place data outside of the server, such as the `CONNECT` storage engine and `Spider`. While you can migrate such tables to TiDB, TiDB does not provide the functionality to store data outside of the TiDB cluster.

To check what storage engines you are using, execute the following statement:

```sql
SELECT
  ENGINE,
  COUNT(*)
FROM
  information_schema.tables
GROUP BY
  ENGINE;
```

```sql
+--------------------+----------+
| ENGINE             | COUNT(*) |
+--------------------+----------+
| NULL               |      101 |
| Aria               |       38 |
| CSV                |        2 |
| InnoDB             |        6 |
| MEMORY             |       67 |
| MyISAM             |        1 |
| PERFORMANCE_SCHEMA |       81 |
+--------------------+----------+
7 rows in set (0.009 sec)
```
### Syntax

MariaDB supports the `RETURNING` keyword for `DELETE`, `INSERT`, and `REPLACE` statements. TiDB does not support them. You might want to look into your application and query logging to see if it affects your migration.
### Data types

MariaDB supports some data types that TiDB does not support, such as `UUID`, `INET4`, and `INET6`.

To check for these datatypes, execute the following statement:

```sql
SELECT
  TABLE_SCHEMA,
  TABLE_NAME,
  COLUMN_NAME,
  DATA_TYPE
FROM
  information_schema.columns
WHERE
  DATA_TYPE IN('INET4','INET6','UUID');
```

```sql
+--------------+------------+-------------+-----------+
| TABLE_SCHEMA | TABLE_NAME | COLUMN_NAME | DATA_TYPE |
+--------------+------------+-------------+-----------+
| test         | u1         | u           | uuid      |
| test         | u1         | i4          | inet4     |
| test         | u1         | i6          | inet6     |
+--------------+------------+-------------+-----------+
3 rows in set (0.026 sec)

```
### Character set and collation

TiDB does not support the `latin1_swedish_ci` collation that is often used in MariaDB.

To see what collations TiDB supports, execute this statement on TiDB:

```sql
SHOW COLLATION;
```

```sql
+--------------------+---------+-----+---------+----------+---------+
| Collation          | Charset | Id  | Default | Compiled | Sortlen |
+--------------------+---------+-----+---------+----------+---------+
| ascii_bin          | ascii   |  65 | Yes     | Yes      |       1 |
| binary             | binary  |  63 | Yes     | Yes      |       1 |
| gbk_bin            | gbk     |  87 |         | Yes      |       1 |
| gbk_chinese_ci     | gbk     |  28 | Yes     | Yes      |       1 |
| latin1_bin         | latin1  |  47 | Yes     | Yes      |       1 |
| utf8_bin           | utf8    |  83 | Yes     | Yes      |       1 |
| utf8_general_ci    | utf8    |  33 |         | Yes      |       1 |
| utf8_unicode_ci    | utf8    | 192 |         | Yes      |       1 |
| utf8mb4_0900_ai_ci | utf8mb4 | 255 |         | Yes      |       1 |
| utf8mb4_0900_bin   | utf8mb4 | 309 |         | Yes      |       1 |
| utf8mb4_bin        | utf8mb4 |  46 | Yes     | Yes      |       1 |
| utf8mb4_general_ci | utf8mb4 |  45 |         | Yes      |       1 |
| utf8mb4_unicode_ci | utf8mb4 | 224 |         | Yes      |       1 |
+--------------------+---------+-----+---------+----------+---------+
13 rows in set (0.0012 sec)
```

To check what collations the columns of your current tables are using, you can use this statement:

```sql
SELECT
  TABLE_SCHEMA,
  COLLATION_NAME,
  COUNT(*)
FROM
  information_schema.columns
GROUP BY
  TABLE_SCHEMA, COLLATION_NAME
ORDER BY
  COLLATION_NAME;
```

```sql
+--------------------+--------------------+----------+
| TABLE_SCHEMA       | COLLATION_NAME     | COUNT(*) |
+--------------------+--------------------+----------+
| sys                | NULL               |      562 |
| test               | NULL               |       14 |
| mysql              | NULL               |       84 |
| performance_schema | NULL               |      892 |
| information_schema | NULL               |      421 |
| mysql              | latin1_swedish_ci  |       34 |
| performance_schema | utf8mb3_bin        |       38 |
| mysql              | utf8mb3_bin        |       61 |
| sys                | utf8mb3_bin        |       40 |
| information_schema | utf8mb3_general_ci |      375 |
| performance_schema | utf8mb3_general_ci |      244 |
| sys                | utf8mb3_general_ci |      386 |
| mysql              | utf8mb3_general_ci |       67 |
| mysql              | utf8mb4_bin        |        8 |
+--------------------+--------------------+----------+
14 rows in set (0.045 sec)
```

See also [Character Set and Collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation).
