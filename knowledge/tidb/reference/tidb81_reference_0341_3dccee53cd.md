# LEFT and LENGTH string functions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Supported functions > [`LEFT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_left) | String Functions > Supported functions > [`LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_length)`
- Source Line Ranges: `814-930`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `string-functions`, `substring-extraction`, `byte-length`, `character-length`, `multibyte`, `null-handling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0341_3dccee53cd`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#left-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-left`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c51e526e154ae3de459f889c5d7955fad10b04594c930c9a594ec8ffa6c99cac`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#left-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-left
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how `LEFT()` extracts characters from the start of a string or how `LENGTH()` measures string size in bytes, especially for multibyte characters and `NULL` inputs.
- Retrieval Keywords: LEFT(str, len), LENGTH(), CHAR_LENGTH(), returns a specified number of characters from the left side of a string, length in bytes, multibyte character counted as a single code point, multibyte character counted as multiple bytes, len less than or equal to 0 returns empty string, len greater than or equal to length of str returns original str, returns NULL if argument is NULL, LEFT('🍣ABC', 3), LENGTH('🍣ABC'), CHAR_LENGTH('🍣ABC')
- Follow-up Guidance: The source also contrasts `LENGTH()` with `CHAR_LENGTH()`, stating that `LENGTH()` counts bytes while `CHAR_LENGTH()` counts a multibyte character as a single code point.
- Classification Note: This is classified as SQL reference content because it documents syntax, return behavior, multibyte handling, and examples for the `LEFT()` and `LENGTH()` string functions.

## Official Source Content

### [`LEFT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_left)

The `LEFT()` function returns a specified number of characters from the left side of a string.

Syntax:

```sql
LEFT(`str`, `len`)
```

- `str`: the original string to extract characters. If `str` contains a multibyte character, the function counts it as a single code point.
- `len`: the length of characters to be returned.
    - If `len` is equal to or less than 0, the function returns an empty string.
    - If `len` is equal to or greater than the length of `str`, the function returns the original `str`.
- If any argument is `NULL`, the function returns `NULL`.

Examples:

```sql
SELECT LEFT('ABCED', 3);
+------------------+
| LEFT('ABCED', 3) |
+------------------+
| ABC              |
+------------------+

SELECT LEFT('ABCED', 6);
+------------------+
| LEFT('ABCED', 6) |
+------------------+
| ABCED            |
+------------------+
```

```sql
SELECT LEFT('ABCED', 0);
+------------------+
| LEFT('ABCED', 0) |
+------------------+
|                  |
+------------------+

SELECT LEFT('ABCED', -1);
+-------------------+
| LEFT('ABCED', -1) |
+-------------------+
|                   |
+-------------------+
```

```sql
SELECT LEFT('🍣ABC', 3);
+--------------------+
| LEFT('🍣ABC', 3)     |
+--------------------+
| 🍣AB                 |
+--------------------+
```

```sql
SELECT LEFT('ABC', NULL);
+-------------------+
| LEFT('ABC', NULL) |
+-------------------+
| NULL              |
+-------------------+

SELECT LEFT(NULL, 3);
+------------------------------+
| LEFT(NULL, 3)                |
+------------------------------+
| NULL                         |
+------------------------------+
```
### [`LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_length)

The `LENGTH()` function returns the length of a string in bytes.

`LENGTH()` counts a multibyte character as multiple bytes while `CHAR_LENGTH()` counts a multibyte character as a single code point.

If the argument is `NULL`, the function returns `NULL`.

Examples:

```sql
SELECT LENGTH('ABC');
+---------------+
| LENGTH('ABC') |
+---------------+
|             3 |
+---------------+

SELECT LENGTH('🍣ABC');
+-------------------+
| LENGTH('🍣ABC')     |
+-------------------+
|                 7 |
+-------------------+

SELECT CHAR_LENGTH('🍣ABC');
+------------------------+
| CHAR_LENGTH('🍣ABC')     |
+------------------------+
|                      4 |
+------------------------+
```

```sql
SELECT LENGTH(NULL);
+--------------+
| LENGTH(NULL) |
+--------------+
|         NULL |
+--------------+
```
