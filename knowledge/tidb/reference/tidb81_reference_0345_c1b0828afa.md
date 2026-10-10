# String function references: OCTET_LENGTH through REGEXP

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Supported functions > [`OCTET_LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_octet-length) | String Functions > Supported functions > [`ORD()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_ord) | String Functions > Supported functions > [`POSITION()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_position) | String Functions > Supported functions > [`QUOTE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_quote) | String Functions > Supported functions > [`REGEXP`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#operator_regexp)`
- Source Line Ranges: `1562-1706`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `string-functions`, `synonyms`, `character-codes`, `sql-escaping`, `regular-expressions`, `pattern-matching`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0345_c1b0828afa`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#octet-length-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-octet-length`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d93b5e0fabf90650d25bfb7472daf750b76f9308366122d68887564efbe4480a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#octet-length-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-octet-length
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when you need reference details or examples for the string functions OCTET_LENGTH(), ORD(), POSITION(), QUOTE(), or the REGEXP operator in SQL.
- Retrieval Keywords: OCTET_LENGTH(), LENGTH() synonym, ORD(), CHAR(), POSITION(), LOCATE() synonym, QUOTE(), escape the argument for use in an SQL statement, --skip-binary-as-hex, REGEXP, pattern matching using regular expressions, v REGEXP '^Ti', v REGEXP 'DB$', HEX('ë'), ORD('ë')
- Follow-up Guidance: The examples show REGEXP in both the SELECT clause and the WHERE clause, and show QUOTE() output display considerations with --skip-binary-as-hex.
- Classification Note: The official content is a SQL reference section that defines function behavior, notes synonyms, and provides executable examples for string and regular expression operations.

## Official Source Content

### [`OCTET_LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_octet-length)

Synonym for [`LENGTH()`](#length).
### [`ORD()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_ord)

Return the character code for the leftmost character of the given argument.

This function is similar to [`CHAR()`](#char) but works the other way around.

Examples:

Taking `a` and `A` as an example, `ORD()` returns `97` for `a` and `65` for `A`.

```sql
SELECT ORD('a'), ORD('A');
```

```
+----------+----------+
| ORD('a') | ORD('A') |
+----------+----------+
|       97 |       65 |
+----------+----------+
1 row in set (0.00 sec)
```

If you take the character code obtained from `ORD()` as input, you can get the original characters back using the `CHAR()` function. Note that the output format might vary depending on whether the `binary-as-hex` option is enabled in your MySQL client.

```sql
SELECT CHAR(97), CHAR(65);
```

```
+----------+----------+
| CHAR(97) | CHAR(65) |
+----------+----------+
| a        | A        |
+----------+----------+
1 row in set (0.01 sec)
```

The following example shows how `ORD()` handles multibyte characters. Here, both `101` and `0x65` are the UTF-8 encoded values for the `e` character, but in different formats. And both `50091` and `0xC3AB` represent the same values, but for the `ë` character.

```sql
SELECT ORD('e'), ORD('ë'), HEX('e'), HEX('ë');
```

```
+----------+-----------+----------+-----------+
| ORD('e') | ORD('ë')  | HEX('e') | HEX('ë')  |
+----------+-----------+----------+-----------+
|      101 |     50091 | 65       | C3AB      |
+----------+-----------+----------+-----------+
1 row in set (0.00 sec)
```
### [`POSITION()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_position)

Synonym for [`LOCATE()`](#locate).
### [`QUOTE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_quote)

Escape the argument for use in an SQL statement.

If the argument is `NULL`, the function returns `NULL`.

Example:

To display the result directly instead of showing a hexadecimal-encoded value, you need to start the MySQL client with the [`--skip-binary-as-hex`](https://dev.mysql.com/doc/refman/8.0/en/mysql-command-options.html#option_mysql_binary-as-hex) option.

The following example shows that the ASCII NULL character is escaped as `\0` and the single quote character `'` is escaped as `\'`:

```sql
SELECT QUOTE(0x002774657374);
```

```
+-----------------------+
| QUOTE(0x002774657374) |
+-----------------------+
| '\0\'test'            |
+-----------------------+
1 row in set (0.00 sec)
```
### [`REGEXP`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#operator_regexp)

Pattern matching using regular expressions.

Examples:

In this example a number of strings are matched against two regular expressions.

```sql
WITH vals AS (
    SELECT 'TiDB' AS v
    UNION ALL
    SELECT 'Titanium'
    UNION ALL
    SELECT 'Tungsten'
    UNION ALL
    SELECT 'Rust'
)
SELECT
    v,
    v REGEXP '^Ti' AS 'starts with "Ti"',
    v REGEXP '^.{4}$' AS 'Length is 4 characters'
FROM
    vals;
```

```
+----------+------------------+------------------------+
| v        | starts with "Ti" | Length is 4 characters |
+----------+------------------+------------------------+
| TiDB     |                1 |                      1 |
| Titanium |                1 |                      0 |
| Tungsten |                0 |                      0 |
| Rust     |                0 |                      1 |
+----------+------------------+------------------------+
4 rows in set (0.00 sec)
```

The following example demonstrates that `REGEXP` is not limited to the `SELECT` clause. For example, you can also use it in the `WHERE` clause of the query.

```sql
SELECT
    v
FROM (
        SELECT 'TiDB' AS v
    ) AS vals
WHERE
    v REGEXP 'DB$';
```

```
+------+
| v    |
+------+
| TiDB |
+------+
1 row in set (0.01 sec)
```
