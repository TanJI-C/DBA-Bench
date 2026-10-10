# Utility SQL functions for formatting bytes and nanosecond durations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/utility-functions.md`
- Source Title: `Utility Functions`
- Source Heading Path: `Utility Functions | Utility Functions > `FORMAT_BYTES()` | Utility Functions > `FORMAT_NANO_TIME()``
- Source Line Ranges: `5-42`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `utility-functions`, `sql-functions`, `formatting`, `bytes`, `nanoseconds`, `human-readable-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0358_3613cc1a8f`
- Source ID: `tidb-docs-8.1:functions-and-operators/utility-functions.md#utility-functions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8c0b4fb45a005c1e146943f8d2172604e6f2c9568e43c39a09e37bbdbd29a771`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/utility-functions#utility-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/utility-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB utility SQL functions that convert byte counts or nanosecond values into human-readable output.
- Retrieval Keywords: FORMAT_BYTES(), FORMAT_NANO_TIME(), utility functions, human-readable format, number of bytes, number of nanoseconds, SELECT FORMAT_BYTES(10*1024*1024), SELECT FORMAT_NANO_TIME(1000000), 10.00 MiB, 1.00 ms
- Follow-up Guidance: The source includes example SQL statements and outputs for `FORMAT_BYTES()` and `FORMAT_NANO_TIME()` showing `10.00 MiB` and `1.00 ms`.
- Classification Note: This is reference content because it defines supported utility SQL functions and shows their example input and output formatting behavior.

## Official Source Content

# Utility Functions

This document introduces utility functions supported in TiDB, designed to simplify common data conversions for better readability.
## `FORMAT_BYTES()`

The `FORMAT_BYTES()` function converts a number of bytes into a human-readable format.

```sql
SELECT FORMAT_BYTES(10*1024*1024);
```

```
+----------------------------+
| FORMAT_BYTES(10*1024*1024) |
+----------------------------+
| 10.00 MiB                  |
+----------------------------+
1 row in set (0.001 sec)
```
## `FORMAT_NANO_TIME()`

The `FORMAT_NANO_TIME()` function converts a number of nanoseconds into a human-readable time format.

```sql
SELECT FORMAT_NANO_TIME(1000000);
```

```
+---------------------------+
| FORMAT_NANO_TIME(1000000) |
+---------------------------+
| 1.00 ms                   |
+---------------------------+
1 row in set (0.001 sec)
```
