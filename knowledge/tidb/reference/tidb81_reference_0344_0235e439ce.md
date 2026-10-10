# String functions: LOWER, LPAD, LTRIM, MAKE_SET, MID, NOT LIKE, NOT REGEXP, OCT

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Supported functions > [`LOWER()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_lower) | String Functions > Supported functions > [`LPAD()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_lpad) | String Functions > Supported functions > [`LTRIM()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_ltrim) | String Functions > Supported functions > [`MAKE_SET()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_make-set) | String Functions > Supported functions > [`MID()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_mid) | String Functions > Supported functions > [`NOT LIKE`](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#operator_not-like) | String Functions > Supported functions > [`NOT REGEXP`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#operator_not-regexp) | String Functions > Supported functions > [`OCT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_oct)`
- Source Line Ranges: `1247-1561`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `string-functions`, `sql-functions`, `pattern-matching`, `regular-expressions`, `padding`, `trimming`, `substring`, `bitset`, `octal`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0344_0235e439ce`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#lower-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-lower`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bbb9ea58a63beec3b4d0d7d863522c126b859eef32c9b9a7b35fb2235306fd2c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#lower-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-lower
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB SQL string function behavior and examples for LOWER(), LPAD(), LTRIM(), MAKE_SET(), MID(), NOT LIKE, NOT REGEXP, or OCT().
- Retrieval Keywords: LOWER(str), LPAD(str, len, padstr), LTRIM(), MAKE_SET(bits, str1, str2, ...), MID(str, pos, len), two-argument variant of MID not supported, #52420, NOT LIKE, NOT REGEXP, OCT(), left-padded, leading spaces, space character U+0020, comma-separated strings, bit from the right, substring starting from pos, negation of LIKE, negation of REGEXP, octal representation
- Follow-up Guidance: The content also points to LIKE, REGEXP, CONCAT(), and a recursive common table expression (CTE) example used with OCT().
- Classification Note: This is reference content because it defines the semantics, NULL behavior, limitations, and SQL examples for multiple supported string functions and pattern-matching operators in TiDB.

## Official Source Content

### [`LOWER()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_lower)

The `LOWER(str)` function is used to convert all characters in the given argument `str` to lowercase. The argument can be either a string or a number.

- If the argument is a string, the function returns the string in lowercase.
- If the argument is a number, the function returns the number without leading zeros.
- If the argument is `NULL`, the function returns `NULL`.

Examples:

```sql
SELECT LOWER("TiDB");

+---------------+
| LOWER("TiDB") |
+---------------+
| tidb          |
+---------------+
```

```sql
SELECT LOWER(-012);

+-------------+
| LOWER(-012) |
+-------------+
| -12         |
+-------------+
```
### [`LPAD()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_lpad)

The `LPAD(str, len, padstr)` function returns the string argument, left-padded with the specified string `padstr` to a length of `len` characters.

- If `len` is less than the length of the string `str`, the function truncates the string `str` to the length of `len`.
- If `len` is a negative number, the function returns `NULL`.
- If any argument is `NULL`, the function returns `NULL`.

Examples:

```sql
SELECT LPAD('TiDB',8,'>');
+--------------------+
| LPAD('TiDB',8,'>') |
+--------------------+
| >>>>TiDB           |
+--------------------+
1 row in set (0.00 sec)
```

```sql
SELECT LPAD('TiDB',2,'>');
+--------------------+
| LPAD('TiDB',2,'>') |
+--------------------+
| Ti                 |
+--------------------+
1 row in set (0.00 sec)
```

```sql
SELECT LPAD('TiDB',-2,'>');
+---------------------+
| LPAD('TiDB',-2,'>') |
+---------------------+
| NULL                |
+---------------------+
1 row in set (0.00 sec)
```
### [`LTRIM()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_ltrim)

The `LTRIM()` function removes leading spaces from a given string.

If the argument is `NULL`, this function returns `NULL`.

> **Note:**
>
> This function only removes the space character (U+0020) and does not remove other space-like characters such as tab (U+0009) or non-breaking space (U+00A0).

Examples:

In the following example, the `LTRIM()` function removes the leading spaces from `'    hello'` and returns `hello`.

```sql
SELECT LTRIM('    hello');
```

```
+--------------------+
| LTRIM('    hello') |
+--------------------+
| hello              |
+--------------------+
1 row in set (0.00 sec)
```

In the following example, [`CONCAT()`](#concat) is used to enclose the result of `LTRIM('    hello')` with `«` and `»`. This formatting makes it a bit easier to see that all leading spaces are removed.

```sql
SELECT CONCAT('«',LTRIM('    hello'),'»');
```

```
+------------------------------------+
| CONCAT('«',LTRIM('    hello'),'»') |
+------------------------------------+
| «hello»                            |
+------------------------------------+
1 row in set (0.00 sec)
```
### [`MAKE_SET()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_make-set)

The `MAKE_SET()` function returns a set of comma-separated strings based on whether a corresponding bit in the `bits` argument is set to `1`.

Syntax:

```sql
MAKE_SET(bits, str1, str2, ...)
```

- `bits`: controls which subsequent string arguments to include in the result set. If `bits` is set to `NULL`, the function returns `NULL`.
- `str1, str2, ...`: a list of strings. Each string corresponds to a bit in the `bits` argument from right to left. `str1` corresponds to the first bit from the right, `str2` corresponds to the second bit from the right, and so on. If the corresponding bit is `1`, the string is included in the result; otherwise, it is not included.

Examples:

In the following example, because all bits are set to `0` in the `bits` argument, the function does not include any subsequent strings in the result and returns an empty string.

```sql
SELECT MAKE_SET(b'000','foo','bar','baz');
```

```
+------------------------------------+
| MAKE_SET(b'000','foo','bar','baz') |
+------------------------------------+
|                                    |
+------------------------------------+
1 row in set (0.00 sec)
```

In the following example, because only the first bit from the right is `1`, the function only returns the first string `foo`.

```sql
SELECT MAKE_SET(b'001','foo','bar','baz');
```

```
+------------------------------------+
| MAKE_SET(b'001','foo','bar','baz') |
+------------------------------------+
| foo                                |
+------------------------------------+
1 row in set (0.00 sec)
```

In the following example, because only the second bit from the right is `1`, the function only returns the second string `bar`.

```sql
SELECT MAKE_SET(b'010','foo','bar','baz');
```

```
+------------------------------------+
| MAKE_SET(b'010','foo','bar','baz') |
+------------------------------------+
| bar                                |
+------------------------------------+
1 row in set (0.00 sec)
```

In the following example, because only the third bit from the right is `1`, the function only returns the third string `baz`.

```sql
SELECT MAKE_SET(b'100','foo','bar','baz');
```

```
+------------------------------------+
| MAKE_SET(b'100','foo','bar','baz') |
+------------------------------------+
| baz                                |
+------------------------------------+
1 row in set (0.00 sec)
```

In the following example, because all bits are `1`, the function returns all three strings in a comma-separated result set.

```sql
SELECT MAKE_SET(b'111','foo','bar','baz');
```

```
+------------------------------------+
| MAKE_SET(b'111','foo','bar','baz') |
+------------------------------------+
| foo,bar,baz                        |
+------------------------------------+
1 row in set (0.0002 sec)
```
### [`MID()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_mid)

The `MID(str, pos, len)` function returns a substring starting from the specified `pos` position with the `len` length.

If any of the arguments are `NULL`, the function returns `NULL`.

TiDB does not support the two-argument variant of this function. For more information, see [#52420](https://github.com/pingcap/tidb/issues/52420).

Examples:

In the following example, `MID()` returns the substring of the input string starting from the second character (`b`) with a length of `3` characters.

```sql
SELECT MID('abcdef',2,3);
```

```
+-------------------+
| MID('abcdef',2,3) |
+-------------------+
| bcd               |
+-------------------+
1 row in set (0.00 sec)
```
### [`NOT LIKE`](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#operator_not-like)

Negation of simple pattern matching.

This function performs the inverse operation of [`LIKE`](#like).

Examples:

In the following example, `NOT LIKE` returns `0` (False) because `aaa` matches the `a%` pattern.

```sql
SELECT 'aaa' LIKE 'a%', 'aaa' NOT LIKE 'a%';
```

```
+-----------------+---------------------+
| 'aaa' LIKE 'a%' | 'aaa' NOT LIKE 'a%' |
+-----------------+---------------------+
|               1 |                   0 |
+-----------------+---------------------+
1 row in set (0.00 sec)
```

In the following example, `NOT LIKE` returns `1` (True) because `aaa` does not match the `b%` pattern.

```sql
SELECT 'aaa' LIKE 'b%', 'aaa' NOT LIKE 'b%';
```

```
+-----------------+---------------------+
| 'aaa' LIKE 'b%' | 'aaa' NOT LIKE 'b%' |
+-----------------+---------------------+
|               0 |                   1 |
+-----------------+---------------------+
1 row in set (0.00 sec)
```
### [`NOT REGEXP`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#operator_not-regexp)

Negation of [`REGEXP`](#regexp).
### [`OCT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_oct)

Return a string containing [octal](https://en.wikipedia.org/wiki/Octal) (base 8) representation of a number.

Examples:

The following example generates a sequence of numbers from 0 to 20 using a [recursive common table expression (CTE)](https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-common-table-expression#recursive-cte) and then uses the `OCT()` function to convert each number to its octal representation. Decimal values from 0 to 7 have identical representations in octal. Decimal numbers from 8 to 15 correspond to octal numbers from 10 to 17.

```sql
WITH RECURSIVE nr(n) AS (
    SELECT 0 AS n
    UNION ALL
    SELECT n+1 FROM nr WHERE n<20
)
SELECT n, OCT(n) FROM nr;
```

```
+------+--------+
| n    | OCT(n) |
+------+--------+
|    0 | 0      |
|    1 | 1      |
|    2 | 2      |
|    3 | 3      |
|    4 | 4      |
|    5 | 5      |
|    6 | 6      |
|    7 | 7      |
|    8 | 10     |
|    9 | 11     |
|   10 | 12     |
|   11 | 13     |
|   12 | 14     |
|   13 | 15     |
|   14 | 16     |
|   15 | 17     |
|   16 | 20     |
|   17 | 21     |
|   18 | 22     |
|   19 | 23     |
|   20 | 24     |
+------+--------+
20 rows in set (0.00 sec)
```
