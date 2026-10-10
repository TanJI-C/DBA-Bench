# SHOW CHARACTER SET syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-character-set.md`
- Source Title: `SHOW CHARACTER SET | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW CHARACTER SET | SHOW CHARACTER SET > Synopsis | SHOW CHARACTER SET > Examples | SHOW CHARACTER SET > MySQL compatibility | SHOW CHARACTER SET > See also`
- Source Line Ranges: `5-76`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `show character set`, `charset`, `collation`, `syntax`, `examples`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0645_1db5f076a4`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-character-set.md#show-character-set`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5c920bef4a419c1fc9cf6639ed71fa4e13f9898c6f0981c0f6e8bc82e43e7be7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-character-set#show-character-set
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-character-set.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for the syntax, examples, output columns, or MySQL compatibility of `SHOW CHARACTER SET` in TiDB.
- Retrieval Keywords: SHOW CHARACTER SET, SHOW CHARSET, SHOW CHAR SET, ShowCharsetStmt, SHOW CHARACTER SET LIKE 'utf8%', SHOW CHARACTER SET WHERE Description='UTF-8 Unicode', Charset, Description, Default collation, Maxlen, mysql compatibility, SHOW COLLATION, Character Set and Collation
- Follow-up Guidance: The source also points to `SHOW COLLATION` and `Character Set and Collation` for related information.
- Classification Note: This is reference content because it defines the statement synopsis, shows example queries and result sets, and notes compatibility behavior without describing a workflow.

## Official Source Content

# SHOW CHARACTER SET

This statement provides a static list of available character sets in TiDB. The output does not reflect any attributes of the current connection or user.
## Synopsis

```ebnf+diagram
ShowCharsetStmt ::=
    "SHOW" ( ("CHARACTER" | "CHAR") "SET" | "CHARSET" ) ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

```sql
SHOW CHARACTER SET;
```

```
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

```sql
SHOW CHARACTER SET LIKE 'utf8%';
```

```
+---------+---------------+-------------------+--------+
| Charset | Description   | Default collation | Maxlen |
+---------+---------------+-------------------+--------+
| utf8    | UTF-8 Unicode | utf8_bin          |      3 |
| utf8mb4 | UTF-8 Unicode | utf8mb4_bin       |      4 |
+---------+---------------+-------------------+--------+
2 rows in set (0.00 sec)
```

```sql
SHOW CHARACTER SET WHERE Description='UTF-8 Unicode';
```

```
+---------+---------------+-------------------+--------+
| Charset | Description   | Default collation | Maxlen |
+---------+---------------+-------------------+--------+
| utf8    | UTF-8 Unicode | utf8_bin          |      3 |
| utf8mb4 | UTF-8 Unicode | utf8mb4_bin       |      4 |
+---------+---------------+-------------------+--------+
2 rows in set (0.00 sec)
```
## MySQL compatibility

The usage of `SHOW CHARACTER SET` statement in TiDB is fully compatible with MySQL. However, charsets in TiDB might have different default collations compared with MySQL. For details, refer to [Compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility). If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [SHOW COLLATION](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-collation)
* [Character Set and Collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation)
