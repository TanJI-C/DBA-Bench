# DECIMAL characteristics

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/precision-math.md`
- Source Title: `Precision Math`
- Source Heading Path: `Precision Math > DECIMAL data type characteristics`
- Source Line Ranges: `22-54`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `decimal`, `precision`, `scale`, `storage format`, `storage requirements`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0333_bd3dccca7f`
- Source ID: `tidb-docs-8.1:functions-and-operators/precision-math.md#decimal-data-type-characteristics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `853b766147f1e7a1ee76e31d822dee28d82c053b4bd32170c7850457e139aa35`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/precision-math#decimal-data-type-characteristics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/precision-math.md

## Retrieval Guidance

- Use When: Use this chunk when looking up DECIMAL precision, scale, storage format, storage requirements, or value range limits for `DECIMAL(M,D)` columns.
- Retrieval Keywords: DECIMAL(M,D), DECIMAL data type characteristics, precision, scale, 1<= M <= 65, 1 <= D <= 30, binary format, packs 9 decimal digits into 4 bytes, storage requirements, leftover digits, DECIMAL(18,9), DECIMAL(20,6), M - D digits to the left of the decimal point, mydecimal.go
- Follow-up Guidance: It includes the leftover-digits storage table and examples for `DECIMAL(18,9)` and `DECIMAL(20,6)`.
- Classification Note: This is reference content because it specifies DECIMAL column syntax, limits, storage layout, and range rules.

## Official Source Content

## DECIMAL data type characteristics

This section discusses the following topics of the characteristics of the DECIMAL data type (and its synonyms):

- Maximum number of digits
- Storage format
- Storage requirements

The declaration syntax for a DECIMAL column is `DECIMAL(M,D)`. The ranges of values for the arguments are as follows:

- M is the maximum number of digits (the precision). 1<= M <= 65.
- D is the number of digits to the right of the decimal point (the scale). 1 <= D <= 30 and D must be no larger than M.

The maximum value of 65 for M means that calculations on DECIMAL values are accurate up to 65 digits. This limit of 65 digits of precision also applies to exact-value numeric literals.

Values for DECIMAL columns are stored using a binary format that packs 9 decimal digits into 4 bytes. The storage requirements for the integer and fractional parts of each value are determined separately. Each multiple of 9 digits requires 4 bytes, and any remaining digits left over require some fraction of 4 bytes. The storage required for remaining digits is given by the following table.

| Leftover Digits | Number of Bytes |
| --- | --- |
| 0   | 0 |
| 1–2 | 1 |
| 3–4 | 2 |
| 5–6 | 3 |
| 7–9 | 4 |

For example, a `DECIMAL(18,9)` column has 9 digits on each side of the decimal point, so the integer part and the fractional part each require 4 bytes. A `DECIMAL(20,6)` column has 14 integer digits and 6 fractional digits. The integer digits require 4 bytes for 9 of the digits and 3 bytes for the remaining 5 digits. The 6 fractional digits require 3 bytes.

DECIMAL columns do not store a leading `+` character or `-` character or leading `0` digits. If you insert `+0003.1` into a `DECIMAL(5,1)` column, it is stored as `3.1`. For negative numbers, a literal `-` character is not stored.

DECIMAL columns do not permit values larger than the range implied by the column definition. For example, a `DECIMAL(3,0)` column supports a range of `-999` to `999`. A `DECIMAL(M,D)` column permits at most `M - D` digits to the left of the decimal point.

For more information about the internal format of the DECIMAL values, see [`mydecimal.go`](https://github.com/pingcap/tidb/blob/release-8.1/pkg/types/mydecimal.go) in TiDB source code.
