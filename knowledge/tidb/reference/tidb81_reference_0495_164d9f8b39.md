# Schema object naming, quoting, and identifier qualifiers

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/schema-object-names.md`
- Source Title: `Schema Object Names`
- Source Heading Path: `Schema Object Names | Schema Object Names > Identifier qualifiers`
- Source Line Ranges: `5-115`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `identifiers`, `schema-object-names`, `quoting`, `backticks`, `ansi_quotes`, `aliases`, `qualified-names`, `sql-mode`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0495_164d9f8b39`
- Source ID: `tidb-docs-8.1:schema-object-names.md#schema-object-names`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dbaa798e97eb000642658dc98387b9c22beb4584806ab2329fa2b9c0405260fb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/schema-object-names#schema-object-names
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/schema-object-names.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB SQL identifier naming, quoting with backticks or ANSI_QUOTES, aliases, qualified names like table_name.col_name, or related syntax errors such as no database selected.
- Retrieval Keywords: Schema Object Names, Identifier qualifiers, backticks, ANSI_QUOTES, sql_mode, SET SESSION sql_mode='ANSI_QUOTES', CREATE TABLE "test" (a varchar(10));, ERROR 1064 (42000), ERROR 1046 (3D000): No database selected, qualified name, table_name.col_name, `table_name`.`col_name`, `table_name.col_name`, special characters, reserved keyword, alias, SELECT 1 AS `identifier`, 2 AS 'string', double quotation marks as identifier
- Follow-up Guidance: The content also points to MySQL Schema Object Names and MySQL Identifier Qualifiers for more information.
- Classification Note: This is reference content because it defines how schema object identifiers are written and qualified in TiDB SQL statements, including quoting rules, aliases, and identifier qualifiers.

## Official Source Content

# Schema Object Names

This document introduces schema object names in TiDB SQL statements.

Schema object names are used to name all schema objects in TiDB, including database, table, index, column, and alias. You can quote these objects using identifiers in SQL statements.

You can use backticks to enclose the identifier. For example, `SELECT * FROM t` can also be written as `` SELECT * FROM `t` ``. But if the identifier includes one or more special characters or is a reserved keyword, it must be enclosed in backticks to quote the schema object it represents.

```sql
SELECT * FROM `table` WHERE `table`.id = 20;
```

If you set `ANSI_QUOTES` in SQL MODE, TiDB will recognize the string enclosed in double quotation marks `"` as an identifier.

```sql
CREATE TABLE "test" (a varchar(10));
```

```sql
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your TiDB version for the right syntax to use line 1 column 19 near ""test" (a varchar(10))" 
```

```sql
SET SESSION sql_mode='ANSI_QUOTES';
```

```sql
Query OK, 0 rows affected (0.000 sec)
```

```sql
CREATE TABLE "test" (a varchar(10));
```

```sql
Query OK, 0 rows affected (0.012 sec)
```

If you want to use the backtick character in the quoted identifier, repeat the backtick twice. For example, to create a table a`b:

```sql
CREATE TABLE `a``b` (a int);
```

In a `SELECT` statement, you can use an identifier or a string to specify an alias:

```sql
SELECT 1 AS `identifier`, 2 AS 'string';
```

```sql
+------------+--------+
| identifier | string |
+------------+--------+
|          1 |      2 |
+------------+--------+
1 row in set (0.00 sec)
```

For more information, see [MySQL Schema Object Names](https://dev.mysql.com/doc/refman/8.0/en/identifiers.html).
## Identifier qualifiers

Object names can be unqualified or qualified. For example, the following statement creates a table without a qualified name:

```sql
CREATE TABLE t (i int);
```

If you have not used the `USE` statement or the connection parameter to configure the database, the `ERROR 1046 (3D000): No database selected` error is displayed. At this time, you can specify the database qualified name:

```sql
CREATE TABLE test.t (i int);
```

White spaces can exist around `.`. `table_name.col_name` and `table_name . col_name` are equivalent.

To quote this identifier, use:

```sql
`table_name`.`col_name`
```

Instead of:

```sql
`table_name.col_name`
```

For more information, see [MySQL Identifier Qualifiers](https://dev.mysql.com/doc/refman/8.0/en/identifier-qualifiers.html).
