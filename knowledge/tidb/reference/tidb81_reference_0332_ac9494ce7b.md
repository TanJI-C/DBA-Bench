# Precision math overview and numeric types

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/precision-math.md`
- Source Title: `Precision Math`
- Source Heading Path: `Precision Math | Precision Math > Numeric types`
- Source Line Ranges: `5-21`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `precision math`, `numeric types`, `decimal`, `floating point`, `numeric literals`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0332_ac9494ce7b`
- Source ID: `tidb-docs-8.1:functions-and-operators/precision-math.md#precision-math`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a3804f7e4d865c2196d13070f02d4e626f75ea200dba7afb5e69230bcfd7d775`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/precision-math#precision-math
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/precision-math.md

## Retrieval Guidance

- Use When: Use this chunk when determining how TiDB classifies numeric types and numeric literals as exact-value or approximate-value in precision math.
- Retrieval Keywords: precision math, numeric types, exact-value data types, approximate-value data types, DECIMAL, FLOAT, DOUBLE, exact-value numeric literals, approximate-value numeric literals, scientific notation, 2.34, 2.34E0
- Follow-up Guidance: It also helps distinguish exact fixed-point literals such as `2.34` from approximate floating-point literals such as `2.34E0`.
- Classification Note: This is reference content because it defines precision math behavior for SQL numeric types and literals.

## Official Source Content

# Precision Math

The precision math support in TiDB is consistent with MySQL. For more information, see [Precision Math in MySQL](https://dev.mysql.com/doc/refman/8.0/en/precision-math.html).
## Numeric types

The scope of precision math for exact-value operations includes the exact-value data types (integer and DECIMAL types) and exact-value numeric literals. Approximate-value data types and numeric literals are handled as floating-point numbers.

Exact-value numeric literals have an integer part or fractional part, or both. They may be signed. Examples: `1`, `.2`, `3.4`, `-5`, `-6.78`, `+9.10`.

Approximate-value numeric literals are represented in scientific notation (power-of-10) with a mantissa and exponent. Either or both parts may be signed. Examples: `1.2E3`, `1.2E-3`, `-1.2E3`, `-1.2E-3`.

Two numbers that look similar might be treated differently. For example, `2.34` is an exact-value (fixed-point) number, whereas `2.34E0` is an approximate-value (floating-point) number.

The DECIMAL data type is a fixed-point type and the calculations are exact. The FLOAT and DOUBLE data types are floating-point types and calculations are approximate.
