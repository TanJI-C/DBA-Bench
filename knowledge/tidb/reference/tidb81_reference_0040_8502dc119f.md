# Collation coercibility and COLLATE clause

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/character-set-and-collation.md`
- Source Title: `Character Set and Collation`
- Source Heading Path: `Character Set and Collation > Coercibility values of collations in expressions | Character Set and Collation > `COLLATE` clause`
- Source Line Ranges: `570-610`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `collation`, `coercibility`, `expressions`, `collate-clause`, `string-comparison`, `priority-rules`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0040_8502dc119f`
- Source ID: `tidb-docs-8.1:character-set-and-collation.md#coercibility-values-of-collations-in-expressions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dda6a30956daea66fdf82540eeff02608de77fff02771cab0fa2fa37eb5a69a7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/character-set-and-collation#coercibility-values-of-collations-in-expressions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/character-set-and-collation.md

## Retrieval Guidance

- Use When: Use this chunk when determining how TiDB infers the collation of an expression with mixed collations, coercibility values, or an explicit COLLATE clause.
- Retrieval Keywords: coercibility values of collations in expressions, COLLATE clause, explicit COLLATE clause coercibility 0, column CAST() CONVERT() BINARY() coercibility 2, USER() VERSION() coercibility 3, constants coercibility 4, numbers or intermediate variables coercibility 5, NULL coercibility 6, binary > utf8mb4_bin > utf8mb4_general_ci > utf8mb4_unicode_ci > utf8_bin > utf8_general_ci > utf8_unicode_ci > latin1_bin > ascii_bin, TiDB cannot infer the collation and reports an error, incompatible collations returned type String, SELECT 'a' = _utf8mb4 'A' collate utf8mb4_general_ci
- Follow-up Guidance: The source includes an example using SELECT 'a' = _utf8mb4 'A' collate utf8mb4_general_ci and references Connection Character Sets and Collations for more details.
- Classification Note: This is reference content because it defines coercibility values, collation priority rules, error conditions, and the meaning of the COLLATE clause in TiDB SQL expressions.

## Official Source Content

## Coercibility values of collations in expressions

If an expression involves multiple clauses of different collations, you need to infer the collation used in the calculation. The rules are as follows:

+ The coercibility value of the explicit `COLLATE` clause is `0`.
+ If the collations of two strings are incompatible, the coercibility value of the concatenation of two strings with different collations is `1`.
+ The collation of the column, `CAST()`, `CONVERT()`, or `BINARY()` has a coercibility value of `2`.
+ The system constant (the string returned by `USER ()` or `VERSION ()`) has a coercibility value of `3`.
+ The coercibility value of constants is `4`.
+ The coercibility value of numbers or intermediate variables is `5`.
+ `NULL` or expressions derived from `NULL` has a coercibility value of `6`.

When inferring collations, TiDB prefers using the collation of expressions with lower coercibility values. If the coercibility values of two clauses are the same, the collation is determined according to the following priority:

binary > utf8mb4_bin > (utf8mb4_general_ci = utf8mb4_unicode_ci) > utf8_bin > (utf8_general_ci = utf8_unicode_ci) > latin1_bin > ascii_bin

TiDB cannot infer the collation and reports an error in the following situations:

- If the collations of two clauses are different and the coercibility value of both clauses is `0`.
- If the collations of two clauses are incompatible and the returned type of expression is `String`.
## `COLLATE` clause

TiDB supports using the `COLLATE` clause to specify the collation of an expression. The coercibility value of this expression is `0`, which has the highest priority. See the following example:

```sql
SELECT 'a' = _utf8mb4 'A' collate utf8mb4_general_ci;
```

```sql
+-----------------------------------------------+
| 'a' = _utf8mb4 'A' collate utf8mb4_general_ci |
+-----------------------------------------------+
|                                             1 |
+-----------------------------------------------+
1 row in set (0.00 sec)
```

For more details, see [Connection Character Sets and Collations](https://dev.mysql.com/doc/refman/8.0/en/charset-connection.html).
