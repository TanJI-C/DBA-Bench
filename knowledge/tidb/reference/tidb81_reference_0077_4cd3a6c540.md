# Numeric types overview and integer data types

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/data-type-numeric.md`
- Source Title: `Numeric Types`
- Source Heading Path: `Numeric Types | Numeric Types > Integer types | Numeric Types > Integer types > `BIT` type | Numeric Types > Integer types > `BOOLEAN` type | Numeric Types > Integer types > `TINYINT` type | Numeric Types > Integer types > `SMALLINT` type | Numeric Types > Integer types > `MEDIUMINT` type | Numeric Types > Integer types > `INTEGER` type | Numeric Types > Integer types > `BIGINT` type`
- Source Line Ranges: `5-97`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `numeric-types`, `integer-types`, `bit`, `boolean`, `tinyint`, `smallint`, `mediumint`, `integer`, `bigint`, `unsigned`, `zerofill`, `storage-range`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0077_4cd3a6c540`
- Source ID: `tidb-docs-8.1:data-type-numeric.md#numeric-types`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b0ff24cb0c3b4636efac9d5641ade9474b56d29cac1f5d45d01a84c52a39fef7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/data-type-numeric#numeric-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/data-type-numeric.md

## Retrieval Guidance

- Use When: Use this chunk when identifying TiDB MySQL-compatible integer numeric types, their syntax, storage size, signed or unsigned ranges, or the meaning of BIT, BOOLEAN, UNSIGNED, and ZEROFILL.
- Retrieval Keywords: Numeric Types, Integer types, BIT[(M)], BOOLEAN, BOOL, TINYINT[(M)] [UNSIGNED] [ZEROFILL], SMALLINT[(M)] [UNSIGNED] [ZEROFILL], MEDIUMINT[(M)] [UNSIGNED] [ZEROFILL], INT[(M)] [UNSIGNED] [ZEROFILL], INTEGER[(M)] [UNSIGNED] [ZEROFILL], BIGINT[(M)] [UNSIGNED] [ZEROFILL], display width, UNSIGNED, ZEROFILL, TiDB automatically adds the UNSIGNED attribute, storage required bytes, signed values range, unsigned values range, TINYINT range, SMALLINT range, MEDIUMINT range, INT range, BIGINT range, BIT(M) 1 to 64, BOOLEAN equivalent to TINYINT(1), True is 1 and False is 0
- Follow-up Guidance: The source also points to the MySQL Integer Data Type Syntax reference for more information.
- Classification Note: This is reference content because it defines integer numeric data types, exact syntax forms, storage requirements, and value ranges in TiDB.

## Official Source Content

# Numeric Types

TiDB supports all the MySQL numeric types, including:

+ [Integer Types](#integer-types) (Exact Value)
+ [Floating-Point Types](#floating-point-types) (Approximate Value)
+ [Fixed-Point Types](#fixed-point-types) (Exact Value)
## Integer types

TiDB supports all the MySQL integer types, including `INTEGER`/`INT`, `TINYINT`, `SMALLINT`, `MEDIUMINT`, and `BIGINT`. For more information, see [Integer Data Type Syntax in MySQL](https://dev.mysql.com/doc/refman/8.0/en/integer-types.html).

The following table summarizes field descriptions:

| Syntax Element | Description |
| -------- | ------------------------------- |
| M | the display width of the type. Optional. |
| UNSIGNED | UNSIGNED. If omitted, it is SIGNED. |
| ZEROFILL | If you specify ZEROFILL for a numeric column, TiDB automatically adds the UNSIGNED attribute to the column. |

The following table summarizes the required storage and range for integer types supported by TiDB:

| Data Type | Storage Required (bytes) | Minimum Value (signed/unsigned) | Maximum value (signed/unsigned) |
| ------- | -------- | ----------- | ------------ |
| `TINYINT` | 1 | -128 / 0 | 127 / 255 |
| `SMALLINT` | 2 | -32768 / 0 | 32767 / 65535 |
| `MEDIUMINT` | 3 | -8388608 / 0 | 8388607 / 16777215 |
| `INT` | 4 | -2147483648 / 0 | 2147483647 / 4294967295 |
| `BIGINT` | 8 | -9223372036854775808 / 0 | 9223372036854775807 / 18446744073709551615 |
### `BIT` type

The BIT data type. A type of BIT(M) enables the storage of M-bit values. M can range from 1 to 64, with the default value of 1:

```sql
BIT[(M)]
```
### `BOOLEAN` type

The `BOOLEAN` type and its alias `BOOL` are equivalent to `TINYINT(1)`. If the value is `0`, it is considered as `False`; otherwise, it is considered `True`. As in MySQL, `True` is `1` and `False` is `0`:

```sql
BOOLEAN
```
### `TINYINT` type

The `TINYINT` data type stores signed values of range [-128, 127] and unsigned values of range [0, 255]:

```sql
TINYINT[(M)] [UNSIGNED] [ZEROFILL]
```
### `SMALLINT` type

The `SMALLINT` data type stores signed values of range [-32768, 32767], and unsigned values of range [0, 65535]:

```sql
SMALLINT[(M)] [UNSIGNED] [ZEROFILL]
```
### `MEDIUMINT` type

The `MEDIUMINT` data type stores signed values of range [-8388608, 8388607], and unsigned values of range [0, 16777215]:

```sql
MEDIUMINT[(M)] [UNSIGNED] [ZEROFILL]
```
### `INTEGER` type

The `INTEGER` type and its alias `INT` stores signed values of range [-2147483648, 2147483647], and unsigned values of range [0, 4294967295]:

```sql
INT[(M)] [UNSIGNED] [ZEROFILL]
```

You can also use another form:

```sql
INTEGER[(M)] [UNSIGNED] [ZEROFILL]
```
### `BIGINT` type

The `BIGINT` data type stores signed values of range [-9223372036854775808, 9223372036854775807], and unsigned values of range [0, 18446744073709551615]:

```sql
BIGINT[(M)] [UNSIGNED] [ZEROFILL]
```
