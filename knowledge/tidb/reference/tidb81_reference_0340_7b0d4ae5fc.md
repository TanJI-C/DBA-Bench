# INSERT, INSTR, and LCASE string functions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Supported functions > [`INSERT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_insert) | String Functions > Supported functions > [`INSTR()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_instr) | String Functions > Supported functions > [`LCASE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_lcase)`
- Source Line Ranges: `682-813`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `string-functions`, `substring-replacement`, `string-search`, `collation`, `case-sensitivity`, `lowercase`, `null-handling`, `multibyte`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0340_7b0d4ae5fc`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#insert-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-insert`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a6c8372f9e49db781df4efdb42215eac700093b52395ad2cda30d611ed5de1fa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#insert-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-insert
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how `INSERT()`, `INSTR()`, or `LCASE()` behave for substring replacement, substring position lookup, collation-based case sensitivity, multibyte strings, or `NULL` handling in SQL.
- Retrieval Keywords: INSERT(str, pos, len, newstr), INSTR(str, substr), LCASE(str), LOWER(str) synonym, LOCATE(substr, str) reversed arguments, utf8mb4_bin, utf8mb4_general_ci, _bin case-sensitive, _general_ci case-insensitive, _ai_ci case-insensitive, multibyte safe, returns 0 if substr is not in str, returns NULL if any argument is NULL, replace substring starting at position pos, number treated as string
- Follow-up Guidance: The source also notes that `INSTR(str, substr)` is the same as the two-argument version of `LOCATE(substr, str)` with the argument order reversed, and that `LCASE(str)` is a synonym for `LOWER(str)`.
- Classification Note: This is classified as SQL reference content because it defines exact semantics, edge cases, and examples for the string functions `INSERT()`, `INSTR()`, and `LCASE()`.

## Official Source Content

### [`INSERT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_insert)

The `INSERT(str, pos, len, newstr)` function is used to replace a substring in `str` (that starts at position `pos` and is `len` characters long) with the string `newstr`. This function is multibyte safe.

- If `pos` exceeds the length of `str`, the function returns the original string `str` without modification.
- If `len` exceeds the remaining length of `str` from position `pos`, the function replaces the rest of the string from position `pos`.
- If any argument is `NULL`, the function returns `NULL`.

Examples:

```sql
SELECT INSERT('He likes tennis', 4, 5, 'plays');
+------------------------------------------+
| INSERT('He likes tennis', 4, 5, 'plays') |
+------------------------------------------+
| He plays tennis                          |
+------------------------------------------+
```

```sql
SELECT INSERT('He likes tennis', -1, 5, 'plays');
+-------------------------------------------+
| INSERT('He likes tennis', -1, 5, 'plays') |
+-------------------------------------------+
| He likes tennis                           |
+-------------------------------------------+
```

```sql
SELECT INSERT('He likes tennis', 4, 100, 'plays');
+--------------------------------------------+
| INSERT('He likes tennis', 4, 100, 'plays') |
+--------------------------------------------+
| He plays                                   |
+--------------------------------------------+
```

```sql
SELECT INSERT('He likes tenis', 10, 100, '🍣');
+-------------------------------------------+
| INSERT('He likes tenis', 10, 100, '🍣')     |
+-------------------------------------------+
| He likes 🍣                                 |
+-------------------------------------------+
```

```sql
SELECT INSERT('あああああああ', 2, 3, 'いいい');
+----------------------------------------------------+
| INSERT('あああああああ', 2, 3, 'いいい')           |
+----------------------------------------------------+
| あいいいあああ                                     |
+----------------------------------------------------+
```

```sql
SELECT INSERT('あああああああ', 2, 3, 'xx');
+---------------------------------------------+
| INSERT('あああああああ', 2, 3, 'xx')        |
+---------------------------------------------+
| あxxあああ                                  |
+---------------------------------------------+
```
### [`INSTR()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_instr)

The `INSTR(str, substr)` function is used to get the position of the first occurrence of `substr` in `str`. Each argument can be either a string or a number. This function is the same as the two-argument version of [`LOCATE(substr, str)`](#locate), but with the order of the arguments reversed.

> **Note:**
>
> The case sensitivity of `INSTR(str, substr)` is determined by the [collations](https://docs.pingcap.com/tidb/stable/character-set-and-collation) used in TiDB. Binary collations (with the suffix `_bin`) are case-sensitive, while general collations (with the suffix `_general_ci` or `_ai_ci`, and) are case-insensitive.

- If either argument is a number, the function treats the number as a string.
- If `substr` is not in `str`, the function returns `0`. Otherwise, it returns the position of the first occurrence of `substr` in `str`.
- If either argument is `NULL`, the function returns `NULL`.

Examples:

```sql
SELECT INSTR("pingcap.com", "tidb");

+------------------------------+
| INSTR("pingcap.com", "tidb") |
+------------------------------+
|                            0 |
+------------------------------+
```

```sql
SELECT INSTR("pingcap.com/tidb", "tidb");

+-----------------------------------+
| INSTR("pingcap.com/tidb", "tidb") |
+-----------------------------------+
|                                13 |
+-----------------------------------+
```

```sql
SELECT INSTR("pingcap.com/tidb" COLLATE utf8mb4_bin, "TiDB");

+-------------------------------------------------------+
| INSTR("pingcap.com/tidb" COLLATE utf8mb4_bin, "TiDB") |
+-------------------------------------------------------+
|                                                     0 |
+-------------------------------------------------------+
```

```sql
SELECT INSTR("pingcap.com/tidb" COLLATE utf8mb4_general_ci, "TiDB");

+--------------------------------------------------------------+
| INSTR("pingcap.com/tidb" COLLATE utf8mb4_general_ci, "TiDB") |
+--------------------------------------------------------------+
|                                                           13 |
+--------------------------------------------------------------+
```

```sql
SELECT INSTR(0123, "12");

+-------------------+
| INSTR(0123, "12") |
+-------------------+
|                 1 |
+-------------------+
```
### [`LCASE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_lcase)

The `LCASE(str)` function is a synonym for [`LOWER(str)`](#lower), which returns the lowercase of the given argument.
