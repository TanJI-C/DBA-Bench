# Floating-point and fixed-point numeric data types

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/data-type-numeric.md`
- Source Title: `Numeric Types`
- Source Heading Path: `Numeric Types > Floating-point types | Numeric Types > Floating-point types > `FLOAT` type | Numeric Types > Floating-point types > `DOUBLE` type | Numeric Types > Fixed-point types | Numeric Types > Fixed-point types > `DECIMAL` type`
- Source Line Ranges: `98-173`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `numeric-types`, `floating-point-types`, `fixed-point-types`, `float`, `double`, `decimal`, `numeric`, `precision`, `scale`, `unsigned`, `zerofill`, `approximate-values`, `exact-values`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0078_bb664b5c8e`
- Source ID: `tidb-docs-8.1:data-type-numeric.md#floating-point-types`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ca72bf03800f3fe7cbbc2813ed25162509930f58e4aeffba24501fe1d76ca08c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/data-type-numeric#floating-point-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/data-type-numeric.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB floating-point or fixed-point numeric types, including FLOAT, DOUBLE, DECIMAL, NUMERIC, their syntax, precision and scale rules, storage, and approximate versus exact value behavior.
- Retrieval Keywords: Floating-point types, Fixed-point types, FLOAT[(M,D)] [UNSIGNED] [ZEROFILL], FLOAT(p) [UNSIGNED] [ZEROFILL], DOUBLE[(M,D)] [UNSIGNED] [ZEROFILL], DOUBLE PRECISION [(M,D)] [UNSIGNED] [ZEROFILL], REAL[(M,D)] [UNSIGNED] [ZEROFILL], DECIMAL[(M[,D])] [UNSIGNED] [ZEROFILL], NUMERIC[(M[,D])] [UNSIGNED] [ZEROFILL], FLOAT storage 4 bytes, FLOAT(p) 0 to 24, FLOAT(p) 25 to 53, DOUBLE storage 8 bytes, approximate values, exact fixed-point number, precision, scale, maximum number of digits 65, maximum supported decimals 30, default precision of FLOAT is 8 digits, MySQL default precision is 6 digits, scientific notation to CHAR, Cast functions and operators, currency use DECIMAL
- Follow-up Guidance: The source includes notes about FLOAT default precision differences from MySQL and a note that converting DOUBLE scientific notation to CHAR is displayed inconsistently with MySQL, with details in Cast functions and operators.
- Classification Note: This is reference content because it specifies floating-point and fixed-point numeric type syntax, storage, precision and scale semantics, and documented notes and warnings.

## Official Source Content

## Floating-point types

TiDB supports all the MySQL floating-point types, including `FLOAT`, and `DOUBLE`. For more information, see [Floating-Point Types (Approximate Value) - FLOAT, DOUBLE in MySQL](https://dev.mysql.com/doc/refman/8.0/en/floating-point-types.html).

The following table summarizes field descriptions:

| Syntax Element | Description |
| -------- | ------------------------------- |
| M | the total number of digits |
| D | the number of digits following the decimal point |
| UNSIGNED | UNSIGNED. If omitted, it is SIGNED. |
| ZEROFILL | If you specify ZEROFILL for a numeric column, TiDB automatically adds the UNSIGNED attribute to the column. |

The following table summarizes the required storage for floating-point types supported by TiDB:

| Data Type | Storage Required (bytes)|
| ----------- |----------|
| `FLOAT` | 4 |
| `FLOAT(p)` | If 0 <= p <= 24, it is 4; if 25 <= p <= 53, it is 8|
| `DOUBLE` | 8 |
### `FLOAT` type

The `FLOAT` type stores a single-precision floating-point number. Permissible values are -3.402823466E+38 to -1.175494351E-38, 0, and 1.175494351E-38 to 3.402823466E+38. These are the theoretical limits, based on the IEEE standard. The actual range might be slightly smaller depending on your hardware or operating system.

`FLOAT(p)` can be used to represent the required precision in bits. TiDB uses this value only to determine whether to use `FLOAT` or `DOUBLE` for the resulting data type. If p is from 0 to 24, the data type becomes FLOAT with no M or D values. If p is from 25 to 53, the data type becomes `DOUBLE` with no M or D values. The range of the resulting column is the same as for the single-precision `FLOAT` or double-precision `DOUBLE` data type.

```sql
FLOAT[(M,D)] [UNSIGNED] [ZEROFILL]
FLOAT(p) [UNSIGNED] [ZEROFILL]
```

> **Note:**
>
> As in MySQL, the `FLOAT` data type stores approximate values. For values such as currency, it is recommended to use the `DECIMAL` type instead.
>
> In TiDB, the default precision of the `FLOAT` data type is 8 digits, but in MySQL, the default precision is 6 digits. For example, assuming that you insert `123456789` and `1.23456789` into columns of the `FLOAT` type in both TiDB and MySQL, when you query the corresponding values in MySQL, you get `123457000` and `1.23457`, while in TiDB, you get `123456790` and `1.2345679`.
### `DOUBLE` type

The `DOUBLE` type, and its alias `DOUBLE PRECISION` stores a double-precision floating-point number. Permissible values are -1.7976931348623157E+308 to -2.2250738585072014E-308, 0, and 2.2250738585072014E-308 to 1.7976931348623157E+308. These are the theoretical limits, based on the IEEE standard. The actual range might be slightly smaller depending on your hardware or operating system.

```sql
DOUBLE[(M,D)] [UNSIGNED] [ZEROFILL]
DOUBLE PRECISION [(M,D)] [UNSIGNED] [ZEROFILL], REAL[(M,D)] [UNSIGNED] [ZEROFILL]
```

> **Warning:**
>
> As in MySQL, the `DOUBLE` data type stores approximate values. For values such as currency, it is recommended to use the `DECIMAL` type instead.

> **Note:**
>
> When TiDB converts a double-precision floating-point number represented in scientific notation to the `CHAR` type, the result is displayed inconsistently with that in MySQL. See [Cast functions and operators](https://docs.pingcap.com/tidb/stable/functions-and-operators/cast-functions-and-operators) for details.
## Fixed-point types

TiDB supports all the MySQL floating-point types, including DECIMAL, and NUMERIC. For more information, [Fixed-Point Types (Exact Value) - DECIMAL, NUMERIC in MySQL](https://dev.mysql.com/doc/refman/8.0/en/fixed-point-types.html).

The meaning of the fields:

| Syntax Element | Description |
| -------- | ------------------------------- |
| M | the total number of decimal digits  |
| D | the number of digits after the decimal point |
| UNSIGNED | UNSIGNED. If omitted, it is SIGNED. |
| ZEROFILL | If you specify ZEROFILL for a numeric column, TiDB automatically adds the UNSIGNED attribute to the column. |
### `DECIMAL` type

`DECIMAL` and its alias `NUMERIC` store a packed "exact" fixed-point number. M is the total number of decimal digits (the precision), and D is the number of digits after the decimal point (the scale). The decimal point and (for negative numbers) the - sign are not counted in M. If D is 0, values have no decimal point or fractional part. The maximum number of digits (M) for DECIMAL is 65. The maximum number of supported decimals (D) is 30. If D is omitted, the default is 0. If M is omitted, the default is 10.

```sql
DECIMAL[(M[,D])] [UNSIGNED] [ZEROFILL]
NUMERIC[(M[,D])] [UNSIGNED] [ZEROFILL]
```
