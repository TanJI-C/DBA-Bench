# LIKE operator string pattern matching

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Supported functions > [`LIKE`](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#operator_like)`
- Source Line Ranges: `931-1067`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `string-functions`, `pattern-matching`, `like`, `collation`, `escape`, `wildcards`, `null-handling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0342_74b5e2a669`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#like-https-dev-mysql-com-doc-refman-8-0-en-string-comparison-functions-html-operator-like`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cc0f477cfb5b3db332d85cef0414a74e8a6821bdddd405d446dfc2b0e8efd5b8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#like-https-dev-mysql-com-doc-refman-8-0-en-string-comparison-functions-html-operator-like
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when you need the SQL `LIKE` operator syntax, wildcard behavior, `NULL` result rules, escape handling, numeric matching, or collation-sensitive pattern matching examples.
- Retrieval Keywords: LIKE operator, expr LIKE pat [ESCAPE 'escape_char'], % matches any number of characters, _ matches exactly one character, SELECT NULL LIKE '%', default escape character \\, ESCAPE '*', SELECT 'sushi_' LIKE 'sushi*_' ESCAPE '*', SELECT 10 LIKE '1%', COLLATE utf8mb4_unicode_ci LIKE '%SUSHI%', utf8mb4_bin, collation_connection
- Follow-up Guidance: The content also shows explicit examples of `COLLATE utf8mb4_unicode_ci` and `SET collation_connection='utf8mb4_bin'` affecting `LIKE` results.
- Classification Note: This is a SQL reference chunk because it defines the `LIKE` operator semantics and provides exact example statements and results.

## Official Source Content

### [`LIKE`](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#operator_like)

The `LIKE` operator is used for simple string matching. The expression `expr LIKE pat [ESCAPE 'escape_char']` returns `1` (`TRUE`) or `0` (`FALSE`). If either `expr` or `pat` is `NULL`, the result is `NULL`.

You can use the following two wildcard parameters with `LIKE`:

- `%` matches any number of characters, including zero characters.
- `_` matches exactly one character.

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
SELECT NULL LIKE '%' as result;
+--------+
| result |
+--------+
|   NULL |
+--------+
```

```sql
SELECT 'sushi!!!' LIKE 'sushi_' AS result;
+--------+
| result |
+--------+
|      0 |
+--------+
```

```sql
SELECT '🍣🍺sushi🍣🍺' LIKE '%sushi%' AS result;
+--------+
| result |
+--------+
|      1 |
+--------+
```

```sql
SELECT '🍣🍺sushi🍣🍺' LIKE '%SUSHI%' AS result;
+--------+
| result |
+--------+
|      0 |
+--------+
```

```sql
SELECT '🍣🍺sushi🍣🍺' LIKE '%🍣%' AS result;
+--------+
| result |
+--------+
|      1 |
+--------+
```

The default escape character is `\`:

```sql
SELECT 'sushi!!!' LIKE 'sushi\_' AS result;
+--------+
| result |
+--------+
|      0 |
+--------+
```

```sql
SELECT 'sushi_' LIKE 'sushi\_' AS result;
+--------+
| result |
+--------+
|      1 |
+--------+
```

To specify a different escape character, such as `*`, you can use the `ESCAPE` clause:

```sql
SELECT 'sushi_' LIKE 'sushi*_' ESCAPE '*' AS result;
+--------+
| result |
+--------+
|      1 |
+--------+
```

```sql
SELECT 'sushi!' LIKE 'sushi*_' ESCAPE '*' AS result;
+--------+
| result |
+--------+
|      0 |
+--------+
```

You can use the `LIKE` operator to match a numeric value:

```sql
SELECT 10 LIKE '1%' AS result;
+--------+
| result |
+--------+
|      1 |
+--------+
```

```sql
SELECT 10000 LIKE '12%' AS result;
+--------+
| result |
+--------+
|      0 |
+--------+
```

To specify a collation explicitly, such as `utf8mb4_unicode_ci`, you can use `COLLATE`:

```sql
SELECT '🍣🍺Sushi🍣🍺' COLLATE utf8mb4_unicode_ci LIKE '%SUSHI%' AS result;
+--------+
| result |
+--------+
|      1 |
+--------+
```
