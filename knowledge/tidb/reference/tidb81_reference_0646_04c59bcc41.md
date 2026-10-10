# SHOW COLLATION syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-collation.md`
- Source Title: `SHOW COLLATION | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW COLLATION | SHOW COLLATION > Synopsis | SHOW COLLATION > Examples | SHOW COLLATION > MySQL compatibility | SHOW COLLATION > See also`
- Source Line Ranges: `5-97`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show collation`, `collation`, `character set`, `mysql compatibility`, `syntax`, `examples`, `where clause`, `new collation framework`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0646_04c59bcc41`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-collation.md#show-collation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fe8d66c7811460ef51c6fd60b2c6e871c8f7d44d984ca25933645e4812ea16aa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-collation#show-collation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-collation.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about the syntax, output, filtering, or MySQL compatibility of the `SHOW COLLATION` statement, including how results change with the new collation framework.
- Retrieval Keywords: SHOW COLLATION, ShowCollationStmt, SHOW COLLATION LIKE, SHOW COLLATION WHERE, ShowLikeOrWhere, WHERE Charset="utf8mb4", new collation framework, utf8_general_ci, utf8mb4_general_ci, utf8mb4_0900_ai_ci, utf8mb4_0900_bin, binary collations, MySQL compatibility, Character Set and Collation, SHOW CHARACTER SET
- Follow-up Guidance: The source also points to `SHOW CHARACTER SET`, `Character Set and Collation`, and MySQL compatibility details for related information.
- Classification Note: This is reference content because it defines the `SHOW COLLATION` statement syntax, shows example outputs and filtering with `WHERE`, and states compatibility notes from the official documentation.

## Official Source Content

# SHOW COLLATION

This statement provides a static list of collations, and is included to provide compatibility with MySQL client libraries.

> **Note:**
>
> Results of `SHOW COLLATION` vary when the ["new collation framework"](https://docs.pingcap.com/tidb/stable/character-set-and-collation#new-framework-for-collations) is enabled. For new collation framework details, refer to [Character Set and Collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation).
## Synopsis

```ebnf+diagram
ShowCollationStmt ::=
    "SHOW" "COLLATION" ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

When new collation framework is disabled, only binary collations are displayed.

```sql
SHOW COLLATION;
```

```
+-------------+---------+------+---------+----------+---------+
| Collation   | Charset | Id   | Default | Compiled | Sortlen |
+-------------+---------+------+---------+----------+---------+
| utf8mb4_bin | utf8mb4 |   46 | Yes     | Yes      |       1 |
| latin1_bin  | latin1  |   47 | Yes     | Yes      |       1 |
| binary      | binary  |   63 | Yes     | Yes      |       1 |
| ascii_bin   | ascii   |   65 | Yes     | Yes      |       1 |
| utf8_bin    | utf8    |   83 | Yes     | Yes      |       1 |
+-------------+---------+------+---------+----------+---------+
5 rows in set (0.02 sec)
```

When new collation framework is enabled, `utf8_general_ci` and `utf8mb4_general_ci` are additionally supported.

```sql
SHOW COLLATION;
```

```
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
| utf8mb4_bin        | utf8mb4 |   46 | Yes     | Yes      |       1 |
| utf8mb4_general_ci | utf8mb4 |   45 |         | Yes      |       1 |
| utf8mb4_unicode_ci | utf8mb4 |  224 |         | Yes      |       1 |
+--------------------+---------+------+---------+----------+---------+
11 rows in set (0.001 sec)
```

To filter on the character set, you can add a `WHERE` clause.

```sql
SHOW COLLATION WHERE Charset="utf8mb4";
```

```sql
+--------------------+---------+-----+---------+----------+---------+
| Collation          | Charset | Id  | Default | Compiled | Sortlen |
+--------------------+---------+-----+---------+----------+---------+
| utf8mb4_0900_ai_ci | utf8mb4 | 255 |         | Yes      |       1 |
| utf8mb4_0900_bin   | utf8mb4 | 309 |         | Yes      |       1 |
| utf8mb4_bin        | utf8mb4 |  46 | Yes     | Yes      |       1 |
| utf8mb4_general_ci | utf8mb4 |  45 |         | Yes      |       1 |
| utf8mb4_unicode_ci | utf8mb4 | 224 |         | Yes      |       1 |
+--------------------+---------+-----+---------+----------+---------+
5 rows in set (0.00 sec)
```
## MySQL compatibility

The usage of the `SHOW COLLATION` statement in TiDB is fully compatible with MySQL. However, charsets in TiDB might have different default collations compared with MySQL. For details, refer to [Compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility). If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [SHOW CHARACTER SET](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-character-set)
* [Character Set and Collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation)
