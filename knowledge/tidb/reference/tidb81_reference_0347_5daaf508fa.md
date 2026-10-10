# String functions: regexp and string operations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Supported functions > [`REGEXP_LIKE()`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#function_regexp-like) | String Functions > Supported functions > [`REGEXP_REPLACE()`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#function_regexp-replace) | String Functions > Supported functions > [`REGEXP_SUBSTR()`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#function_regexp-substr) | String Functions > Supported functions > [`REPEAT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_repeat) | String Functions > Supported functions > [`REPLACE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_replace) | String Functions > Supported functions > [`REVERSE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_reverse) | String Functions > Supported functions > [`RIGHT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_right) | String Functions > Supported functions > [`RLIKE`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#operator_regexp) | String Functions > Supported functions > [`RPAD()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_rpad) | String Functions > Supported functions > [`RTRIM()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_rtrim) | String Functions > Supported functions > [`SPACE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_space) | String Functions > Supported functions > [`STRCMP()`](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#function_strcmp) | String Functions > Supported functions > [`SUBSTR()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_substr) | String Functions > Supported functions > [`SUBSTRING()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_substring)`
- Source Line Ranges: `1846-2113`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `string-functions`, `regular-expressions`, `string-comparison`, `substring`, `replace`, `repeat`, `padding`, `trimming`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0347_5daaf508fa`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#regexp-like-https-dev-mysql-com-doc-refman-8-0-en-regexp-html-function-regexp-like`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7fea8107a22de3b1111252fcbd71481d7b82b148e88be5809a6b63e481fbec7d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#regexp-like-https-dev-mysql-com-doc-refman-8-0-en-regexp-html-function-regexp-like
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB SQL string and regular expression functions such as matching, replacing, extracting substrings, repeating, trimming, padding, reversing, comparing, or right-side substring operations.
- Retrieval Keywords: REGEXP_LIKE(), REGEXP_REPLACE(), REGEXP_SUBSTR(), REPEAT(), REPLACE(), REVERSE(), RIGHT(), RLIKE, RPAD(), RTRIM(), SPACE(), STRCMP(), SUBSTR(), SUBSTRING(), match_type, regular expression compatibility with MySQL, case insensitive matching, SELECT REGEXP_LIKE('abc','^A','i'), SELECT REGEXP_REPLACE('TooDB', 'o{2}', 'i'), SELECT REGEXP_SUBSTR('This is TiDB','Ti.{2}'), SELECT REPEAT('ha',3)
- Follow-up Guidance: The chunk also points to regular expression compatibility with MySQL and match_type compatibility for the REGEXP functions.
- Classification Note: This is reference content for the SQL component because it enumerates supported string functions and operators and shows their syntax and example SQL results.

## Official Source Content

### [`REGEXP_LIKE()`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#function_regexp-like)

Whether the string matches the regular expression (Partly compatible with MySQL. For more details, see [Regular expression compatibility with MySQL](#regular-expression-compatibility-with-mysql)).

The `REGEXP_LIKE(str, regex, [match_type])` function is used to test if a regular expression matches a string. Optionally the `match_type` can be used to change the matching behavior.

Examples:

The following example shows that `^a` matches `abc`.

```sql
SELECT REGEXP_LIKE('abc','^a');
```

```
+-------------------------+
| REGEXP_LIKE('abc','^a') |
+-------------------------+
|                       1 |
+-------------------------+
1 row in set (0.00 sec)
```

This following example shows that `^A` does not match `abc`.

```sql
SELECT REGEXP_LIKE('abc','^A');
```

```
+-------------------------+
| REGEXP_LIKE('abc','^A') |
+-------------------------+
|                       0 |
+-------------------------+
1 row in set (0.00 sec)
```

This example matches `^A` against `abc`, which now matches because of the `i` flag which enabled case insensitive matching. For more details about the regular expression `match_type`, see [`match_type` compatibility](#match_type-compatibility).

```sql
SELECT REGEXP_LIKE('abc','^A','i');
```

```
+-----------------------------+
| REGEXP_LIKE('abc','^A','i') |
+-----------------------------+
|                           1 |
+-----------------------------+
1 row in set (0.00 sec)
```
### [`REGEXP_REPLACE()`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#function_regexp-replace)

Replace substrings that match the regular expression (Partly compatible with MySQL. For more details, see [Regular expression compatibility with MySQL](#regular-expression-compatibility-with-mysql)).

The `REGEXP_REPLACE(str, regexp, replace, [start, [match, [match_type]]])` function can be used to replace strings based on regular expressions.

Examples:

In the following example, two o's are replaced by `i`.

```sql
SELECT REGEXP_REPLACE('TooDB', 'o{2}', 'i');
```

```
+--------------------------------------+
| REGEXP_REPLACE('TooDB', 'o{2}', 'i') |
+--------------------------------------+
| TiDB                                 |
+--------------------------------------+
1 row in set (0.00 sec)
```

The following example starts the match at the third character, causing the regular expression not to match and not do any replacement.

```sql
SELECT REGEXP_REPLACE('TooDB', 'o{2}', 'i',3);
```

```
+----------------------------------------+
| REGEXP_REPLACE('TooDB', 'o{2}', 'i',3) |
+----------------------------------------+
| TooDB                                  |
+----------------------------------------+
1 row in set (0.00 sec)
```

In the following example, the 5th argument is used to set if the first or the second match is used for the replacement.

```sql
SELECT REGEXP_REPLACE('TooDB', 'o', 'i',1,1);
```

```
+---------------------------------------+
| REGEXP_REPLACE('TooDB', 'o', 'i',1,1) |
+---------------------------------------+
| TioDB                                 |
+---------------------------------------+
1 row in set (0.00 sec)
```

```sql
SELECT REGEXP_REPLACE('TooDB', 'o', 'i',1,2);
```

```
+---------------------------------------+
| REGEXP_REPLACE('TooDB', 'o', 'i',1,2) |
+---------------------------------------+
| ToiDB                                 |
+---------------------------------------+
1 row in set (0.00 sec)
```

The following example uses the 6th argument to set the `match_type` for case insensitive matching. For more details about the regular expression `match_type`, see [`match_type` compatibility](#match_type-compatibility).

```sql
SELECT REGEXP_REPLACE('TooDB', 'O{2}','i',1,1);
```

```
+-----------------------------------------+
| REGEXP_REPLACE('TooDB', 'O{2}','i',1,1) |
+-----------------------------------------+
| TooDB                                   |
+-----------------------------------------+
1 row in set (0.00 sec)
```

```sql
SELECT REGEXP_REPLACE('TooDB', 'O{2}','i',1,1,'i');
```

```
+---------------------------------------------+
| REGEXP_REPLACE('TooDB', 'O{2}','i',1,1,'i') |
+---------------------------------------------+
| TiDB                                        |
+---------------------------------------------+
1 row in set (0.00 sec)
```
### [`REGEXP_SUBSTR()`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#function_regexp-substr)

Return the substring that matches the regular expression (Partly compatible with MySQL. For more details, see [Regular expression compatibility with MySQL](#regular-expression-compatibility-with-mysql)).

The `REGEXP_SUBSTR(str, regexp, [start, [match, [match_type]]])` function is used to get a substring based on a regular expression.

The following example uses the `Ti.{2}` regular expression to get the `TiDB` substring of the `This is TiDB` string.

```sql
SELECT REGEXP_SUBSTR('This is TiDB','Ti.{2}');
```

```
+----------------------------------------+
| REGEXP_SUBSTR('This is TiDB','Ti.{2}') |
+----------------------------------------+
| TiDB                                   |
+----------------------------------------+
1 row in set (0.00 sec)
```
### [`REPEAT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_repeat)

Repeat a string the specified number of times.

Examples:

The following example generates a sequence of numbers from 1 to 20 using a [recursive common table expression (CTE)](https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-common-table-expression#recursive-cte). For each number in the sequence, the character `x` is repeated the number of times equal to the number itself.

```sql
WITH RECURSIVE nr(n) AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n+1 FROM nr WHERE n<20
)
SELECT n, REPEAT('x',n) FROM nr;
```

```
+------+----------------------+
| n    | REPEAT('x',n)        |
+------+----------------------+
|    1 | x                    |
|    2 | xx                   |
|    3 | xxx                  |
|    4 | xxxx                 |
|    5 | xxxxx                |
|    6 | xxxxxx               |
|    7 | xxxxxxx              |
|    8 | xxxxxxxx             |
|    9 | xxxxxxxxx            |
|   10 | xxxxxxxxxx           |
|   11 | xxxxxxxxxxx          |
|   12 | xxxxxxxxxxxx         |
|   13 | xxxxxxxxxxxxx        |
|   14 | xxxxxxxxxxxxxx       |
|   15 | xxxxxxxxxxxxxxx      |
|   16 | xxxxxxxxxxxxxxxx     |
|   17 | xxxxxxxxxxxxxxxxx    |
|   18 | xxxxxxxxxxxxxxxxxx   |
|   19 | xxxxxxxxxxxxxxxxxxx  |
|   20 | xxxxxxxxxxxxxxxxxxxx |
+------+----------------------+
20 rows in set (0.01 sec)
```

The following example demonstrates that `REPEAT()` can operate on strings consisting of multiple characters.

```sql
SELECT REPEAT('ha',3);
```

```
+----------------+
| REPEAT('ha',3) |
+----------------+
| hahaha         |
+----------------+
1 row in set (0.00 sec)
```
### [`REPLACE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_replace)

Replace occurrences of a specified string.
### [`REVERSE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_reverse)

Reverse the characters in a string.
### [`RIGHT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_right)

Return the specified rightmost number of characters.
### [`RLIKE`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#operator_regexp)

Synonym for [`REGEXP`](#regexp).
### [`RPAD()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_rpad)

Append string the specified number of times.
### [`RTRIM()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_rtrim)

Remove trailing spaces.
### [`SPACE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_space)

Return a string of the specified number of spaces.
### [`STRCMP()`](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#function_strcmp)

Compare two strings.
### [`SUBSTR()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_substr)

Return the substring as specified.
### [`SUBSTRING()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_substring)

Return the substring as specified.
