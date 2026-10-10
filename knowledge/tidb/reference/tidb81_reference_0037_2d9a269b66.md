# Character set and collation concepts, supported values, and utf8 vs utf8mb4 behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/character-set-and-collation.md`
- Source Title: `Character Set and Collation`
- Source Heading Path: `Character Set and Collation | Character Set and Collation > Concepts | Character Set and Collation > Character sets and collations supported by TiDB | Character Set and Collation > `utf8` and `utf8mb4` in TiDB`
- Source Line Ranges: `5-210`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `character-set`, `collation`, `utf8`, `utf8mb4`, `latin1`, `gbk`, `default-collation`, `connection-collation`, `string-comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0037_2d9a269b66`
- Source ID: `tidb-docs-8.1:character-set-and-collation.md#character-set-and-collation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b42a61ea12785bf8c9dcec62aeadbe5808bb11d59ecdd7611074375920d0209a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/character-set-and-collation#character-set-and-collation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/character-set-and-collation.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about TiDB character set or collation concepts, supported values from SHOW CHARACTER SET or SHOW COLLATION, default utf8mb4 behavior, latin1 warning, connection collation effects, or the difference between utf8 and utf8mb4 for 4-byte characters.
- Retrieval Keywords: SHOW CHARACTER SET, SHOW COLLATION, SHOW COLLATION WHERE Charset = 'utf8mb4', utf8mb4, utf8, ascii, binary, gbk, latin1, utf8mb4_bin, utf8mb4_general_ci, utf8mb4_unicode_ci, utf8mb4_0900_ai_ci, utf8mb4_0900_bin, utf8_general_ci, utf8_unicode_ci, gbk_chinese_ci, latin1_bin, SET NAMES utf8mb4 COLLATE utf8mb4_bin, SET NAMES utf8mb4 COLLATE utf8mb4_general_ci, SELECT 'A' = 'a', tidb_check_mb4_value_in_utf8, ERROR 1366 (HY000): incorrect utf8 value, 4-byte emoji, connection collation, default collations in TiDB, latin1 as a subset of utf8
- Follow-up Guidance: The chunk also points to the new framework for collations, the GBK document, and the system variable tidb_check_mb4_value_in_utf8 for the utf8 3-byte limit behavior.
- Classification Note: This is reference content because it defines character set and collation concepts, lists supported character sets and collations, and demonstrates documented utf8 versus utf8mb4 behavior with exact SQL and error output.

## Official Source Content

# Character Set and Collation

This document introduces the character sets and collations supported by TiDB.
## Concepts

A character set is a set of symbols and encodings. The default character set in TiDB is `utf8mb4`, which matches the default character set in MySQL 8.0 and later.

A collation is a set of rules for comparing characters in a character set, and the sorting order of characters. For example in a binary collation `A` and `a` do not compare as equal:

```sql
SET NAMES utf8mb4 COLLATE utf8mb4_bin;
SELECT 'A' = 'a';
SET NAMES utf8mb4 COLLATE utf8mb4_general_ci;
SELECT 'A' = 'a';
```

```sql
SELECT 'A' = 'a';
```

```sql
+-----------+
| 'A' = 'a' |
+-----------+
|         0 |
+-----------+
1 row in set (0.00 sec)
```

```sql
SET NAMES utf8mb4 COLLATE utf8mb4_general_ci;
```

```sql
Query OK, 0 rows affected (0.00 sec)
```

```sql
SELECT 'A' = 'a';
```

```sql
+-----------+
| 'A' = 'a' |
+-----------+
|         1 |
+-----------+
1 row in set (0.00 sec)
```
## Character sets and collations supported by TiDB

Currently, TiDB supports the following character sets:

```sql
SHOW CHARACTER SET;
```

```sql
+---------+-------------------------------------+-------------------+--------+
| Charset | Description                         | Default collation | Maxlen |
+---------+-------------------------------------+-------------------+--------+
| ascii   | US ASCII                            | ascii_bin         |      1 |
| binary  | binary                              | binary            |      1 |
| gbk     | Chinese Internal Code Specification | gbk_chinese_ci    |      2 |
| latin1  | Latin1                              | latin1_bin        |      1 |
| utf8    | UTF-8 Unicode                       | utf8_bin          |      3 |
| utf8mb4 | UTF-8 Unicode                       | utf8mb4_bin       |      4 |
+---------+-------------------------------------+-------------------+--------+
6 rows in set (0.00 sec)
```

TiDB supports the following collations:

```sql
SHOW COLLATION;
```

```sql
+--------------------+---------+------+---------+----------+---------+
| Collation          | Charset | Id   | Default | Compiled | Sortlen |
+--------------------+---------+------+---------+----------+---------+
| ascii_bin          | ascii   |   65 | Yes     | Yes      |       1 |
| binary             | binary  |   63 | Yes     | Yes      |       1 |
| gbk_bin            | gbk     |   87 |         | Yes      |       1 |
| gbk_chinese_ci     | gbk     |   28 | Yes     | Yes      |       1 |
| latin1_bin         | latin1  |   47 | Yes     | Yes      |       1 |
| utf8_bin           | utf8    |   83 | Yes     | Yes      |       1 |
| utf8_general_ci    | utf8    |   33 |         | Yes      |       1 |
| utf8_unicode_ci    | utf8    |  192 |         | Yes      |       1 |
| utf8mb4_0900_ai_ci | utf8mb4 |  255 |         | Yes      |       1 |
| utf8mb4_0900_bin   | utf8mb4 |  309 |         | Yes      |       1 |
| utf8mb4_bin        | utf8mb4 |   46 | Yes     | Yes      |       1 |
| utf8mb4_general_ci | utf8mb4 |   45 |         | Yes      |       1 |
| utf8mb4_unicode_ci | utf8mb4 |  224 |         | Yes      |       1 |
+--------------------+---------+------+---------+----------+---------+
13 rows in set (0.00 sec)
```

> **Warning:**
>
> TiDB incorrectly treats latin1 as a subset of utf8. This can lead to unexpected behaviors when you store characters that differ between latin1 and utf8 encodings. It is strongly recommended to the utf8mb4 character set. See [TiDB #18955](https://github.com/pingcap/tidb/issues/18955) for more details.

> **Note:**
>
> The default collations in TiDB (binary collations, with the suffix `_bin`) are different than [the default collations in MySQL](https://dev.mysql.com/doc/refman/8.0/en/charset-charsets.html) (typically general collations, with the suffix `_general_ci` or `_ai_ci`). This can cause incompatible behavior when specifying an explicit character set but relying on the implicit default collation to be chosen.
>
> However, the default collations in TiDB are also affected by the [connection collation](https://dev.mysql.com/doc/refman/8.0/en/charset-connection.html#charset-connection-system-variables) settings of your clients. For example, the MySQL 8.x client defaults to `utf8mb4_0900_ai_ci` as the connection collation for the `utf8mb4` character set.
>
> - Before TiDB v7.4.0, if your client uses `utf8mb4_0900_ai_ci` as the [connection collation](https://dev.mysql.com/doc/refman/8.0/en/charset-connection.html#charset-connection-system-variables), TiDB falls back to using the TiDB server default collation `utf8mb4_bin` because TiDB does not support the `utf8mb4_0900_ai_ci` collation.
> - Starting from v7.4.0, if your client uses `utf8mb4_0900_ai_ci` as the [connection collation](https://dev.mysql.com/doc/refman/8.0/en/charset-connection.html#charset-connection-system-variables), TiDB follows the client's configuration to use `utf8mb4_0900_ai_ci` as the default collation.

You can use the following statement to view the collations (under the [new framework for collations](#new-framework-for-collations)) that corresponds to the character set.

```sql
SHOW COLLATION WHERE Charset = 'utf8mb4';
```

```sql
+--------------------+---------+------+---------+----------+---------+
| Collation          | Charset | Id   | Default | Compiled | Sortlen |
+--------------------+---------+------+---------+----------+---------+
| utf8mb4_0900_ai_ci | utf8mb4 |  255 |         | Yes      |       1 |
| utf8mb4_0900_bin   | utf8mb4 |  309 |         | Yes      |       1 |
| utf8mb4_bin        | utf8mb4 |   46 | Yes     | Yes      |       1 |
| utf8mb4_general_ci | utf8mb4 |   45 |         | Yes      |       1 |
| utf8mb4_unicode_ci | utf8mb4 |  224 |         | Yes      |       1 |
+--------------------+---------+------+---------+----------+---------+
5 rows in set (0.00 sec)
```

For details about the TiDB support of the GBK character set, see [GBK](https://docs.pingcap.com/tidb/stable/character-set-gbk).
## `utf8` and `utf8mb4` in TiDB

In MySQL, the character set `utf8` is limited to a maximum of three bytes. This is sufficient to store characters in the Basic Multilingual Plane (BMP), but not enough to store characters such as emojis. For this, it is recommended to use the character set `utf8mb4` instead.

By default, TiDB also limits the character set `utf8` to a maximum of three bytes to ensure that data created in TiDB can still safely be restored in MySQL. You can disable it by changing the value of the system variable [`tidb_check_mb4_value_in_utf8`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_check_mb4_value_in_utf8) to `OFF`.

The following demonstrates the default behavior when inserting a 4-byte emoji character into a table. The `INSERT` statement fails for the `utf8` character set, but succeeds for `utf8mb4`:

```sql
CREATE TABLE utf8_test (
     c char(1) NOT NULL
    ) CHARACTER SET utf8;
```

```sql
Query OK, 0 rows affected (0.09 sec)
```

```sql
CREATE TABLE utf8m4_test (
     c char(1) NOT NULL
    ) CHARACTER SET utf8mb4;
```

```sql
Query OK, 0 rows affected (0.09 sec)
```

```sql
INSERT INTO utf8_test VALUES ('😉');
```

```sql
ERROR 1366 (HY000): incorrect utf8 value f09f9889(😉) for column c
```

```sql
INSERT INTO utf8m4_test VALUES ('😉');
```

```sql
Query OK, 1 row affected (0.02 sec)
```

```sql
SELECT char_length(c), length(c), c FROM utf8_test;
```

```sql
Empty set (0.01 sec)
```

```sql
SELECT char_length(c), length(c), c FROM utf8m4_test;
```

```sql
+----------------+-----------+------+
| char_length(c) | length(c) | c    |
+----------------+-----------+------+
|              1 |         4 | 😉     |
+----------------+-----------+------+
1 row in set (0.00 sec)
```
