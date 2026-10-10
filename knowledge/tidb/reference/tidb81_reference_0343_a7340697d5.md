# LOCATE function substring position search

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Supported functions > [`LOCATE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_locate)`
- Source Line Ranges: `1068-1246`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `string-functions`, `locate`, `substring-search`, `collation`, `multibyte`, `binary-strings`, `null-handling`, `case-sensitivity`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0343_a7340697d5`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#locate-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-locate`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `34b5c767227dcca6635e989f8d811477079266661ffd7464552e48ae5522cea8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#locate-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-locate
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when you need the SQL `LOCATE(substr, str[, pos])` function behavior, including start position, `0` and `NULL` return cases, multibyte handling, or binary-string case sensitivity examples.
- Retrieval Keywords: LOCATE(substr, str[, pos]), LOCATE function, position of first occurrence, returns 0 if substring not present, returns NULL if any argument is NULL, multibyte safe, case-sensitive search only if at least one argument is a binary string, SELECT LOCATE('bar', 'foobarbar'), SELECT LOCATE('bar', 'foobarbar', 5), SELECT LOCATE('い', 'たいでぃーびー', 3), SELECT LOCATE('b', _binary'aBcde'), SELECT LOCATE(_binary'B', 'aBcde'), utf8mb4_bin, utf8mb4_unicode_ci
- Follow-up Guidance: The content also compares `LOCATE` results under `utf8mb4_bin` and `utf8mb4_unicode_ci`, including multibyte examples with Japanese characters and emoji.
- Classification Note: This is a SQL reference chunk because it specifies `LOCATE()` function semantics, argument behavior, and exact examples for collation and binary-string matching.

## Official Source Content

### [`LOCATE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_locate)

The `LOCATE(substr, str[, pos])` function is used to get the position of the first occurrence of a specified substring `substr` in a string `str`. The `pos` argument is optional and specifies the starting position for the search.

- If the substring `substr` is not present in `str`, the function returns `0`.
- If any argument is `NULL`, the function returns `NULL`.
- This function is multibyte safe and performs a case-sensitive search only if at least one argument is a binary string.

The following examples use the `utf8mb4_bin` collation:

```sql
SET collation_connection='utf8mb4_bin';
SHOW VARIABLES LIKE 'collation_connection';
+----------------------+-------------+
| Variable_name        | Value       |
+----------------------+-------------+
| collation_connection | utf8mb4_bin |
+----------------------+-------------+
```

```sql
SELECT LOCATE('bar', 'foobarbar');
+----------------------------+
| LOCATE('bar', 'foobarbar') |
+----------------------------+
|                          4 |
+----------------------------+
```

```sql
SELECT LOCATE('baz', 'foobarbar');
+----------------------------+
| LOCATE('baz', 'foobarbar') |
+----------------------------+
|                          0 |
+----------------------------+
```

```sql
SELECT LOCATE('bar', 'fooBARBAR');
+----------------------------+
| LOCATE('bar', 'fooBARBAR') |
+----------------------------+
|                          0 |
+----------------------------+
```

```sql
SELECT LOCATE('bar', 'foobarBAR', 100);
+---------------------------------+
| LOCATE('bar', 'foobarBAR', 100) |
+---------------------------------+
|                               0 |
+---------------------------------+
```

```sql
SELECT LOCATE('bar', 'foobarbar', 5);
+-------------------------------+
| LOCATE('bar', 'foobarbar', 5) |
+-------------------------------+
|                             7 |
+-------------------------------+
```

```sql
SELECT LOCATE('bar', NULL);
+---------------------+
| LOCATE('bar', NULL) |
+---------------------+
|                NULL |
+---------------------+
```

```sql
SELECT LOCATE('い', 'たいでぃーびー');
+----------------------------------------+
| LOCATE('い', 'たいでぃーびー')         |
+----------------------------------------+
|                                      2 |
+----------------------------------------+
```

```sql
SELECT LOCATE('い', 'たいでぃーびー', 3);
+-------------------------------------------+
| LOCATE('い', 'たいでぃーびー', 3)         |
+-------------------------------------------+
|                                         0 |
+-------------------------------------------+
```

The following examples use the `utf8mb4_unicode_ci` collation:

```sql
SET collation_connection='utf8mb4_unicode_ci';
SHOW VARIABLES LIKE 'collation_connection';
+----------------------+--------------------+
| Variable_name        | Value              |
+----------------------+--------------------+
| collation_connection | utf8mb4_unicode_ci |
+----------------------+--------------------+
```

```sql
SELECT LOCATE('い', 'たいでぃーびー', 3);
+-------------------------------------------+
| LOCATE('い', 'たいでぃーびー', 3)         |
+-------------------------------------------+
|                                         4 |
+-------------------------------------------+
```

```sql
SELECT LOCATE('🍺', '🍣🍣🍣🍺🍺');
+----------------------------------------+
| LOCATE('🍺', '🍣🍣🍣🍺🍺')            |
+----------------------------------------+
|                                      1 |
+----------------------------------------+
```

The following multibyte and binary string examples use the `utf8mb4_bin` collation:

```sql
SET collation_connection='utf8mb4_bin';
SHOW VARIABLES LIKE 'collation_connection';
+----------------------+-------------+
| Variable_name        | Value       |
+----------------------+-------------+
| collation_connection | utf8mb4_bin |
+----------------------+-------------+
```

```sql
SELECT LOCATE('🍺', '🍣🍣🍣🍺🍺');
+----------------------------------------+
| LOCATE('🍺', '🍣🍣🍣🍺🍺')                         |
+----------------------------------------+
|                                      4 |
+----------------------------------------+
```

```sql
SELECT LOCATE('b', _binary'aBcde');
+-----------------------------+
| LOCATE('b', _binary'aBcde') |
+-----------------------------+
|                           0 |
+-----------------------------+
```

```sql
SELECT LOCATE('B', _binary'aBcde');
+-----------------------------+
| LOCATE('B', _binary'aBcde') |
+-----------------------------+
|                           2 |
+-----------------------------+
```
```sql
SELECT LOCATE(_binary'b', 'aBcde');
+-----------------------------+
| LOCATE(_binary'b', 'aBcde') |
+-----------------------------+
|                           0 |
+-----------------------------+
```

```sql
SELECT LOCATE(_binary'B', 'aBcde');
+-----------------------------+
| LOCATE(_binary'B', 'aBcde') |
+-----------------------------+
|                           2 |
+-----------------------------+
```
