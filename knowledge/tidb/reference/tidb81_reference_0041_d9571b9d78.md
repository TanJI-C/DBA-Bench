# GBK support and MySQL compatibility in TiDB

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/character-set-gbk.md`
- Source Title: `GBK`
- Source Heading Path: `GBK | GBK > MySQL compatibility | GBK > MySQL compatibility > Collations | GBK > MySQL compatibility > Illegal character compatibility | GBK > MySQL compatibility > Other MySQL compatibility`
- Source Line Ranges: `5-85`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `cloud`, `sql`
- Topic Tags: `gbk`, `character-set`, `collation`, `mysql-compatibility`, `illegal-characters`, `sql-mode`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0041_d9571b9d78`
- Source ID: `tidb-docs-8.1:character-set-gbk.md#gbk`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1ed5d1af0ace53660889db31deb4076346669d2d15c132eb6e19d19d57898514`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/character-set-gbk#gbk
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/character-set-gbk.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB GBK character set behavior, default collations, illegal GBK character handling, or MySQL compatibility details.
- Retrieval Keywords: GBK, gbk_chinese_ci, gbk_bin, SHOW CHARACTER SET WHERE CHARSET = 'gbk', SHOW COLLATION WHERE CHARSET = 'gbk', new_collations_enabled_on_first_bootstrap, new framework for collations, character_set_client, character_set_connection, SET NAMES gbk, STRICT_ALL_TABLES, STRICT_TRANS_TABLES, SELECT HEX('一a'), CREATE TABLE gbk_table(a VARCHAR(32) CHARACTER SET gbk), ALTER TABLE convert character set gbk, Unsupported character introducer: 'gbk', _gbk, ENUM, SET
- Follow-up Guidance: The source also states that TiDB does not support using `ALTER TABLE` to convert other character set types to `gbk` or from `gbk` to other character set types, does not support `_gbk`, and treats binary characters of `ENUM` and `SET` as the `utf8mb4` character set.
- Classification Note: This is a reference chunk because it lists official GBK support details, exact compatibility differences with MySQL, configuration-dependent collation behavior, and concrete SQL examples.

## Official Source Content

# GBK

Starting from v5.4.0, TiDB supports the GBK character set. This document provides the TiDB support and compatibility information of the GBK character set.

Starting from v6.0.0, TiDB enables the [new framework for collations](https://docs.pingcap.com/tidb/stable/character-set-and-collation#new-framework-for-collations) by default. The default collation for TiDB GBK character set is `gbk_chinese_ci`, which is consistent with MySQL.

```sql
SHOW CHARACTER SET WHERE CHARSET = 'gbk';
+---------+-------------------------------------+-------------------+--------+
| Charset | Description                         | Default collation | Maxlen |
+---------+-------------------------------------+-------------------+--------+
| gbk     | Chinese Internal Code Specification | gbk_chinese_ci    |      2 |
+---------+-------------------------------------+-------------------+--------+
1 row in set (0.00 sec)

SHOW COLLATION WHERE CHARSET = 'gbk';
+----------------+---------+------+---------+----------+---------+
| Collation      | Charset | Id   | Default | Compiled | Sortlen |
+----------------+---------+------+---------+----------+---------+
| gbk_bin        | gbk     |   87 |         | Yes      |       1 |
| gbk_chinese_ci | gbk     |   28 | Yes     | Yes      |       1 |
+----------------+---------+------+---------+----------+---------+
2 rows in set (0.00 sec)
```
## MySQL compatibility

This section provides the compatibility information between MySQL and TiDB.
### Collations

The default collation of the GBK character set in MySQL is `gbk_chinese_ci`. The default collation for the GBK character set in TiDB depends on the value of the TiDB configuration item [`new_collations_enabled_on_first_bootstrap`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#new_collations_enabled_on_first_bootstrap):

- By default, the TiDB configuration item [`new_collations_enabled_on_first_bootstrap`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#new_collations_enabled_on_first_bootstrap) is set to `true`, which means that the [new framework for collations](https://docs.pingcap.com/tidb/stable/character-set-and-collation#new-framework-for-collations) is enabled and the default collation for the GBK character set is `gbk_chinese_ci`.
- When the TiDB configuration item [`new_collations_enabled_on_first_bootstrap`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#new_collations_enabled_on_first_bootstrap) is set to `false`, the [new framework for collations](https://docs.pingcap.com/tidb/stable/character-set-and-collation#new-framework-for-collations) is disabled, and the default collation for the GBK character set is `gbk_bin`.

By default, TiDB Cloud enables the [new framework for collations](https://docs.pingcap.com/tidb/stable/character-set-and-collation#new-framework-for-collations) and the default collation for the GBK character set is `gbk_chinese_ci`.

Additionally, because TiDB converts GBK to `utf8mb4` and then uses a binary collation, the `gbk_bin` collation in TiDB is not the same as the `gbk_bin` collation in MySQL.
### Illegal character compatibility

* If the system variables [`character_set_client`](https://docs.pingcap.com/tidb/stable/system-variables#character_set_client) and [`character_set_connection`](https://docs.pingcap.com/tidb/stable/system-variables#character_set_connection) are not set to `gbk` at the same time, TiDB handles illegal characters in the same way as MySQL.
* If `character_set_client` and `character_set_connection` are both set to `gbk`, TiDB handles illegal characters differently than MySQL.

    - MySQL handles illegal GBK character sets in reading and writing operations differently.
    - TiDB handles illegal GBK character sets in reading and writing operations in the same way. In the SQL strict mode, TiDB reports an error when either reading or writing illegal GBK characters. In the non-strict mode, TiDB replaces illegal GBK characters with `?` when either reading or writing illegal GBK characters.

For example, after `SET NAMES gbk`, if you create a table using the `CREATE TABLE gbk_table(a VARCHAR(32) CHARACTER SET gbk)` statement in MySQL and TiDB respectively and then execute the SQL statements in the following table, you can see the detailed differences.

| Database    |    If the configured SQL mode contains either `STRICT_ALL_TABLES` or `STRICT_TRANS_TABLES`                                               | If the configured SQL mode contains neither `STRICT_ALL_TABLES` nor `STRICT_TRANS_TABLES`                                                                     |
|-------|-------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| MySQL | `SELECT HEX('一a');` <br /> `e4b88061`<br /><br />`INSERT INTO gbk_table values('一a');`<br /> `Incorrect Error`       | `SELECT HEX('一a');` <br /> `e4b88061`<br /><br />`INSERT INTO gbk_table VALUES('一a');`<br />`SELECT HEX(a) FROM gbk_table;`<br /> `e4b8` |
| TiDB  | `SELECT HEX('一a');` <br /> `Incorrect Error`<br /><br />`INSERT INTO gbk_table VALUES('一a');`<br /> `Incorrect Error` | `SELECT HEX('一a');` <br /> `e4b83f`<br /><br />`INSERT INTO gbk_table VALUES('一a');`<br />`SELECT HEX(a) FROM gbk_table;`<br /> `e4b83f`  |

In the above table, the result of `SELECT HEX('a');` in the `utf8mb4` byte set is `e4b88061`.
### Other MySQL compatibility

- Currently, TiDB does not support using the `ALTER TABLE` statement to convert other character set types to `gbk` or from `gbk` to other character set types.

* TiDB does not support the use of `_gbk`. For example:

  ```sql
  CREATE TABLE t(a CHAR(10) CHARSET BINARY);
  Query OK, 0 rows affected (0.00 sec)
  INSERT INTO t VALUES (_gbk'啊');
  ERROR 1115 (42000): Unsupported character introducer: 'gbk'
  ```

- Currently, for binary characters of the `ENUM` and `SET` types, TiDB deals with them as the `utf8mb4` character set.
