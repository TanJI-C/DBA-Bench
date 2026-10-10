# TiDB data types overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/data-type-overview.md`
- Source Title: `Data Types`
- Source Heading Path: `Data Types`
- Source Line Ranges: `5-15`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `data-types`, `mysql-compatibility`, `numeric-types`, `string-types`, `date-time-types`, `json`, `type-definition`, `precision`, `scale`, `fsp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0079_3c6d539b0f`
- Source ID: `tidb-docs-8.1:data-type-overview.md#data-types`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7aa474d29992a343048594ba57fe5d3394d8cf490ee8762be3883efa34f1cf32`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/data-type-overview#data-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/data-type-overview.md

## Retrieval Guidance

- Use When: Use this chunk when looking for a summary of TiDB-supported MySQL data types and the meaning of type definition notation such as T(M[, D]) and fsp.
- Retrieval Keywords: Data Types, TiDB supports all the data types in MySQL except the SPATIAL type, SPATIAL, numeric types, string types, date & time types, JSON type, T(M[, D]), maximum display width, precision, scale, fsp, TIME, DATETIME, TIMESTAMP, fractional seconds precision
- Follow-up Guidance: The source points to the numeric types, string types, date & time types, and JSON type pages for detailed type-specific information.
- Classification Note: This is reference content because it defines supported data type categories and explains the formal meanings of T, M, D, and fsp in type declarations.

## Official Source Content

# Data Types

TiDB supports all the data types in MySQL except the `SPATIAL` type. This includes all the [numeric types](https://docs.pingcap.com/tidb/stable/data-type-numeric), [string types](https://docs.pingcap.com/tidb/stable/data-type-string), [date & time types](https://docs.pingcap.com/tidb/stable/data-type-date-and-time), and [the JSON type](https://docs.pingcap.com/tidb/stable/data-type-json).

The definitions used for datatypes are specified as `T(M[, D])`. Where by:

- `T` indicates the specific data type.
- `M` indicates the maximum display width for integer types. For floating-point and fixed-point types, `M` is the total number of digits that can be stored (the precision). For string types, `M` is the maximum length. The maximum permissible value of M depends on the data type.
- `D` applies to floating-point and fixed-point types and indicates the number of digits following the decimal point (the scale).
- `fsp` applies to the `TIME`, `DATETIME`, and `TIMESTAMP` types and represents the fractional seconds precision. The `fsp` value, if given, must be in the range 0 to 6. A value of 0 signifies that there is no fractional part. If omitted, the default precision is 0.
