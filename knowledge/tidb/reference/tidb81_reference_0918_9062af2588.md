# Vector comparison, arithmetic, and cast section start

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-data-types.md`
- Source Title: `Vector Data Types`
- Source Heading Path: `Vector Data Types > Comparison | Vector Data Types > Arithmetic | Vector Data Types > Cast`
- Source Line Ranges: `80-150`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`
- Topic Tags: `vector`, `comparison`, `lexicographical-order`, `arithmetic`, `operators`, `casting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0918_9062af2588`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-data-types.md#comparison`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a484f65f310a35e2e88ab05d34e3be2e0997207711a1576c46a745c9de43aebf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types#comparison
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-data-types.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how vector values are compared, when lexicographical comparison applies, how vector arithmetic works, and why explicit casting with VEC_FROM_TEXT matters for constants.
- Retrieval Keywords: Comparison, Arithmetic, Cast, comparison operators, =, !=, <, >, <=, >=, element-wise numerically, lexicographical comparison, prefix of another, [] < [1], explicit cast, VEC_FROM_TEXT, SELECT '[12.0]' < '[4.0]', SELECT VEC_FROM_TEXT('[12.0]') < VEC_FROM_TEXT('[4.0]'), addition, subtraction, vectors have different dimensions: 1 and 3
- Follow-up Guidance: It refers to Vector Functions and Operators for the complete list of comparison operators and functions for vector data types.
- Classification Note: This is classified as reference content because it specifies the comparison semantics, arithmetic operator behavior, dimension mismatch error condition, and cast-related example for vector expressions.

## Official Source Content

## Comparison

You can compare vector data types using [comparison operators](https://docs.pingcap.com/tidb/stable/functions-and-operators/operators) such as `=`, `!=`, `<`, `>`, `<=`, and `>=`. For a complete list of comparison operators and functions for vector data types, see [Vector Functions and Operators](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-functions-and-operators).

Vector data types are compared element-wise numerically. For example:

- `[1] < [12]`
- `[1,2,3] < [1,2,5]`
- `[1,2,3] = [1,2,3]`
- `[2,2,3] > [1,2,3]`

Two vectors with different dimensions are compared using lexicographical comparison, with the following rules:

- Two vectors are compared element by element from the start, and each element is compared numerically.
- The first mismatching element determines which vector is lexicographically _less_ or _greater_ than the other.
- If one vector is a prefix of another, the shorter vector is lexicographically _less_ than the other. For example, `[1,2,3] < [1,2,3,0]`.
- Vectors of the same length with identical elements are lexicographically _equal_.
- An empty vector is lexicographically _less_ than any non-empty vector. For example, `[] < [1]`.
- Two empty vectors are lexicographically _equal_.

When comparing vector constants, consider performing an [explicit cast](#cast) from string to vector to avoid comparisons based on string values:

```sql
-- Because string is given, TiDB is comparing strings:
[tidb]> SELECT '[12.0]' < '[4.0]';
+--------------------+
| '[12.0]' < '[4.0]' |
+--------------------+
|                  1 |
+--------------------+
1 row in set (0.01 sec)

-- Cast to vector explicitly to compare by vectors:
[tidb]> SELECT VEC_FROM_TEXT('[12.0]') < VEC_FROM_TEXT('[4.0]');
+--------------------------------------------------+
| VEC_FROM_TEXT('[12.0]') < VEC_FROM_TEXT('[4.0]') |
+--------------------------------------------------+
|                                                0 |
+--------------------------------------------------+
1 row in set (0.01 sec)
```
## Arithmetic

Vector data types support arithmetic operations `+` (addition) and `-` (subtraction). However, arithmetic operations between vectors with different dimensions are not supported and will result in an error.

Examples:

```sql
[tidb]> SELECT VEC_FROM_TEXT('[4]') + VEC_FROM_TEXT('[5]');
+---------------------------------------------+
| VEC_FROM_TEXT('[4]') + VEC_FROM_TEXT('[5]') |
+---------------------------------------------+
| [9]                                         |
+---------------------------------------------+
1 row in set (0.01 sec)

[tidb]> SELECT VEC_FROM_TEXT('[2,3,4]') - VEC_FROM_TEXT('[1,2,3]');
+-----------------------------------------------------+
| VEC_FROM_TEXT('[2,3,4]') - VEC_FROM_TEXT('[1,2,3]') |
+-----------------------------------------------------+
| [1,1,1]                                             |
+-----------------------------------------------------+
1 row in set (0.01 sec)

[tidb]> SELECT VEC_FROM_TEXT('[4]') + VEC_FROM_TEXT('[1,2,3]');
ERROR 1105 (HY000): vectors have different dimensions: 1 and 3
```
## Cast
