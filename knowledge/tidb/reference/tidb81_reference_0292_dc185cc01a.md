# Bit shift operators, compatibility, and known issues

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/bit-functions-and-operators.md`
- Source Title: `Bit Functions and Operators`
- Source Heading Path: `Bit Functions and Operators > [`<<` (left shift)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_left-shift) | Bit Functions and Operators > [`>>` (right shift)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_right-shift) | Bit Functions and Operators > MySQL compatibility | Bit Functions and Operators > Known issues`
- Source Line Ranges: `229-309`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `bitwise-operators`, `left-shift`, `right-shift`, `mysql-compatibility`, `known-issues`, `sql-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0292_dc185cc01a`
- Source ID: `tidb-docs-8.1:functions-and-operators/bit-functions-and-operators.md#left-shift-https-dev-mysql-com-doc-refman-8-0-en-bit-functions-html-operator-left-shift`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `72c0a54f057108cd726f74636cc1c842113b81a76185903261b2d4a1bfceec24`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/bit-functions-and-operators#left-shift-https-dev-mysql-com-doc-refman-8-0-en-bit-functions-html-operator-left-shift
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/bit-functions-and-operators.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB SQL bit shift operators `<<` and `>>`, their example behavior, MySQL 8.0 compatibility notes, or listed known issues for bit functions and operators.
- Retrieval Keywords: << operator, left shift, >> operator, right shift, bit functions and operators, WITH RECURSIVE cte(n), 1<<n, 1024>>n, LPAD(CONV(1<<n,10,2),11,0), LPAD(CONV(1024>>n,10,2),11,0), extracting a UNIX timestamp from a TiDB TSO timestamp, MySQL compatibility, TiDB aims to follow the behavior of MySQL 8.0, bitwise operations with binary arguments, #30637, BIT_COUNT(), #44621, MySQL 5.7, MySQL 8.0
- Follow-up Guidance: The source also points to the TiDB TSO page for the note that `>>` can be useful for extracting a UNIX timestamp from a TiDB TSO timestamp.
- Classification Note: This is reference content because it defines the `<<` and `>>` SQL operators with example queries and documents MySQL compatibility and known issues for bit functions and operators.

## Official Source Content

## [`<<` (left shift)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_left-shift)

The `<<` operator performs a left shift operation, which shifts the bits of a number to the left by a specified number of positions, filling the vacated bits with zeros on the right.

For example, the following statement uses `1<<n` to shift the binary value `1` to the left by `n` positions:

```sql
WITH RECURSIVE cte(n) AS (
    SELECT 0 AS n
    UNION ALL
    SELECT 1+n FROM cte WHERE n<10
)
SELECT n,1<<n,LPAD(CONV(1<<n,10,2),11,0) FROM cte;
```

```
+------+------+----------------------------+
| n    | 1<<n | LPAD(CONV(1<<n,10,2),11,0) |
+------+------+----------------------------+
|    0 |    1 | 00000000001                |
|    1 |    2 | 00000000010                |
|    2 |    4 | 00000000100                |
|    3 |    8 | 00000001000                |
|    4 |   16 | 00000010000                |
|    5 |   32 | 00000100000                |
|    6 |   64 | 00001000000                |
|    7 |  128 | 00010000000                |
|    8 |  256 | 00100000000                |
|    9 |  512 | 01000000000                |
|   10 | 1024 | 10000000000                |
+------+------+----------------------------+
11 rows in set (0.00 sec)
```
## [`>>` (right shift)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_right-shift)

The `>>` operator performs a right shift operation, which shifts the bits of a number to the right by a specified number of positions, filling the vacated bits with zeros on the left.

For example, the following statement uses `1024>>n` to shift a value of `1024` (`10000000000` in binary) to the right by `n` positions:

```sql
WITH RECURSIVE cte(n) AS (
    SELECT 0 AS n
    UNION ALL
    SELECT n+1 FROM cte WHERE n<11
)
SELECT n,1024>>n,LPAD(CONV(1024>>n,10,2),11,0) FROM cte;
```

```
+------+---------+-------------------------------+
| n    | 1024>>n | LPAD(CONV(1024>>n,10,2),11,0) |
+------+---------+-------------------------------+
|    0 |    1024 | 10000000000                   |
|    1 |     512 | 01000000000                   |
|    2 |     256 | 00100000000                   |
|    3 |     128 | 00010000000                   |
|    4 |      64 | 00001000000                   |
|    5 |      32 | 00000100000                   |
|    6 |      16 | 00000010000                   |
|    7 |       8 | 00000001000                   |
|    8 |       4 | 00000000100                   |
|    9 |       2 | 00000000010                   |
|   10 |       1 | 00000000001                   |
|   11 |       0 | 00000000000                   |
+------+---------+-------------------------------+
12 rows in set (0.00 sec)
```

The `>>` operator can also be useful for extracting specific parts of a larger number, such as extracting a UNIX timestamp from a TiDB [TSO](https://docs.pingcap.com/tidb/stable/tso) timestamp.
## MySQL compatibility

There are some differences between MySQL 8.0 and earlier versions of MySQL in handling bit functions and operators. TiDB aims to follow the behavior of MySQL 8.0.
## Known issues

In the following cases, the query results in TiDB are the same as MySQL 5.7 but different from MySQL 8.0.

- Bitwise operations with binary arguments. For more information, see [#30637](https://github.com/pingcap/tidb/issues/30637).
- The result of the `BIT_COUNT()` function. For more information, see [#44621](https://github.com/pingcap/tidb/issues/44621).
