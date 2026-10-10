# REGEXP_INSTR reference and compatibility notes

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Supported functions > [`REGEXP_INSTR()`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#function_regexp-instr)`
- Source Line Ranges: `1707-1845`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `string-functions`, `regular-expressions`, `regexp_instr`, `match-type`, `collation`, `mysql-compatibility`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0346_579a2361e5`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#regexp-instr-https-dev-mysql-com-doc-refman-8-0-en-regexp-html-function-regexp-instr`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f7df7a30afec4cd28448d7e1403107953cc055378f105bcf38ba9962951f0c66`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#regexp-instr-https-dev-mysql-com-doc-refman-8-0-en-regexp-html-function-regexp-instr
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax, examples, or compatibility notes for REGEXP_INSTR(), including start position, match occurrence, return position, match_type, and collation effects.
- Retrieval Keywords: REGEXP_INSTR(), REGEXP_INSTR(str, regexp, [start, [match, [ret, [match_type]]]]), regular expression compatibility with MySQL, match_type compatibility, case insensitive match, collation influences the matching, utf8mb4_general_ci, utf8mb4_bin, REGEXP_INSTR('abcabc','a',2), REGEXP_INSTR('abcabc','a',1,2), REGEXP_INSTR('abcabc','a',1,1,1), REGEXP_INSTR('abcabc','A',1,1,0,'i')
- Follow-up Guidance: The source points to regular expression compatibility with MySQL and match_type compatibility for more details, and includes examples showing how collation changes matching results.
- Classification Note: The official content is a SQL function reference for REGEXP_INSTR() with partial MySQL compatibility notes and argument-by-argument examples.

## Official Source Content

### [`REGEXP_INSTR()`](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#function_regexp-instr)

Return the starting index of the substring that matches the regular expression (Partly compatible with MySQL. For more details, see [Regular expression compatibility with MySQL](#regular-expression-compatibility-with-mysql)).

The `REGEXP_INSTR(str, regexp, [start, [match, [ret, [match_type]]]])` function returns the position of the match if the regular expression (`regexp`) matches the string (`str`).

If either the `str` or `regexp` is `NULL`, then the function returns `NULL`.

Examples:

In the example below you can see that the `^.b.$` matches `abc`.

```sql
SELECT REGEXP_INSTR('abc','^.b.$');
```

```
+-----------------------------+
| REGEXP_INSTR('abc','^.b.$') |
+-----------------------------+
|                           1 |
+-----------------------------+
1 row in set (0.00 sec)
```

The following example uses the third argument to look for a match with a different start position in the string.

```sql
SELECT REGEXP_INSTR('abcabc','a');
```

```
+----------------------------+
| REGEXP_INSTR('abcabc','a') |
+----------------------------+
|                          1 |
+----------------------------+
1 row in set (0.00 sec)
```

```sql
SELECT REGEXP_INSTR('abcabc','a',2);
```

```
+------------------------------+
| REGEXP_INSTR('abcabc','a',2) |
+------------------------------+
|                            4 |
+------------------------------+
1 row in set (0.00 sec)
```

The following example uses the 4th argument to look for the second match.

```sql
SELECT REGEXP_INSTR('abcabc','a',1,2);
```

```
+--------------------------------+
| REGEXP_INSTR('abcabc','a',1,2) |
+--------------------------------+
|                              4 |
+--------------------------------+
1 row in set (0.00 sec)
```

The following example uses the 5th argument to return the value _after_ the mach, instead of the value of the match.

```sql
SELECT REGEXP_INSTR('abcabc','a',1,1,1);
```

```
+----------------------------------+
| REGEXP_INSTR('abcabc','a',1,1,1) |
+----------------------------------+
|                                2 |
+----------------------------------+
1 row in set (0.00 sec)
```

The following example uses the 6th argument to add the `i` flag to get a case insensitive match. For more details about regular expression `match_type`, see [`match_type` compatibility](#match_type-compatibility).

```sql
SELECT REGEXP_INSTR('abcabc','A',1,1,0,'');
```

```
+-------------------------------------+
| REGEXP_INSTR('abcabc','A',1,1,0,'') |
+-------------------------------------+
|                                   0 |
+-------------------------------------+
1 row in set (0.00 sec)
```

```sql
SELECT REGEXP_INSTR('abcabc','A',1,1,0,'i');
```

```
+--------------------------------------+
| REGEXP_INSTR('abcabc','A',1,1,0,'i') |
+--------------------------------------+
|                                    1 |
+--------------------------------------+
1 row in set (0.00 sec)
```

Besides `match_type`, the [collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation) also influences the matching. The following example uses a case-sensitive and a case-insensitive collation to demonstrate this.

```sql
SELECT REGEXP_INSTR('abcabc','A' COLLATE utf8mb4_general_ci);
```

```
+-------------------------------------------------------+
| REGEXP_INSTR('abcabc','A' COLLATE utf8mb4_general_ci) |
+-------------------------------------------------------+
|                                                     1 |
+-------------------------------------------------------+
1 row in set (0.01 sec)
```

```sql
SELECT REGEXP_INSTR('abcabc','A' COLLATE utf8mb4_bin);
```

```
+------------------------------------------------+
| REGEXP_INSTR('abcabc','A' COLLATE utf8mb4_bin) |
+------------------------------------------------+
|                                              0 |
+------------------------------------------------+
1 row in set (0.00 sec)
```
