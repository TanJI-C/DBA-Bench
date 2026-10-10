# Cast functions and operators reference and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/cast-functions-and-operators.md`
- Source Title: `Cast Functions and Operators`
- Source Heading Path: `Cast Functions and Operators | Cast Functions and Operators > BINARY | Cast Functions and Operators > CAST | Cast Functions and Operators > CONVERT | Cast Functions and Operators > MySQL compatibility`
- Source Line Ranges: `5-125`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `type-conversion`, `cast`, `binary`, `convert`, `character-sets`, `mysql-compatibility`, `deprecated`, `multi-valued-indexes`, `json`, `array`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0293_ff9dc10786`
- Source ID: `tidb-docs-8.1:functions-and-operators/cast-functions-and-operators.md#cast-functions-and-operators`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `17772be6dad993029d22df15daeaa92eb8eed796f26e899b1b5ceb5e63971462`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/cast-functions-and-operators#cast-functions-and-operators
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/cast-functions-and-operators.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB SQL cast and convert operators, supported CAST target types, multi-valued index ARRAY casting, or documented MySQL compatibility differences for cast behavior.
- Retrieval Keywords: Cast Functions and Operators, BINARY, CAST(), CONVERT(), CAST(<expression> AS <type> [ARRAY]), CAST(... AS BINARY), character sets, SELECT CAST(0x54694442 AS CHAR), SELECT CONVERT(0x616263 USING utf8mb4), Multi-valued indexes, CAST(j->'$.a' AS UNSIGNED ARRAY), 1 MEMBER OF(j->'$.a'), IndexMerge_10, index:idx_a(cast(json_extract(`j`, _utf8mb4'$.a') as unsigned array)), SELECT CAST(MeN AS CHAR), scientific notation, SPATIAL types, AT TIME ZONE, CAST(24 AS YEAR), #6347, #51742, #29629
- Follow-up Guidance: The source also includes examples for casting a HEX literal to CHAR, converting bytes with CONVERT(... USING utf8mb4), and defining a multi-valued index with CAST(... AS UNSIGNED ARRAY).
- Classification Note: This is a reference chunk because it lists cast operators, supported CAST target types, examples, and explicit MySQL compatibility notes from the official documentation.

## Official Source Content

# Cast Functions and Operators

Cast functions and operators enable conversion of values from one data type to another. TiDB supports all of the [cast functions and operators](https://dev.mysql.com/doc/refman/8.0/en/cast-functions.html) available in MySQL 8.0.

| Name                                     | Description                      |
| ---------------------------------------- | -------------------------------- |
| [`BINARY`](#binary) | Cast a string to a binary string |
| [`CAST()`](#cast) | Cast a value as a certain type   |
| [`CONVERT()`](#convert) | Cast a value as a certain type   |

> **Note:**
>
> TiDB and MySQL display inconsistent results for `SELECT CAST(MeN AS CHAR)` (or its equivalent form `SELECT CONVERT(MeM, CHAR)`), where `MeN` represents a double-precision floating-point number in scientific notation. MySQL displays the complete numeric value when `-15 <= N <= 14` and the scientific notation when `N < -15` or `N > 14`. However, TiDB always displays the complete numeric value. For example, MySQL displays the result of `SELECT CAST(3.1415e15 AS CHAR)` as `3.1415e15`, while TiDB displays the result as `3141500000000000`.
## BINARY

The [`BINARY`](https://dev.mysql.com/doc/refman/8.0/en/cast-functions.html#operator_binary) operator has been deprecated since MySQL 8.0.27. It is recommended to use `CAST(... AS BINARY)` instead both in TiDB and MySQL.
## CAST

The [`CAST(<expression> AS <type> [ARRAY])`](https://dev.mysql.com/doc/refman/8.0/en/cast-functions.html#function_cast) function is used to cast an expression to a specific type.

This function is also used to create [Multi-valued indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#multi-valued-indexes).

The following types are supported:

| Type                 | Description      | Whether it can be used with multi-valued indexes                      |
|----------------------|------------------|------------------------------------------------------------|
| `BINARY(n)`          | Binary string    | No                                                         |
| `CHAR(n)`            | Character string | Yes, but only if a length is specified                     |
| `DATE`               | Date             | Yes                                                        |
| `DATETIME(fsp)`      | Date/time, where `fsp` is optional | Yes                                              |
| `DECIMAL(n, m)`      | Decimal number, where `n` and `m` are optional and are `10` and `0` if not specified | No   |
| `DOUBLE`             | Double precision floating-point number | No                                   |
| `FLOAT(n)`           | Floating-point number, where `n` is optional and should be between `0` and `53` | No |
| `JSON`               | JSON             | No                                                         |
| `REAL`               | Floating-point number | Yes                                                   |
| `SIGNED [INTEGER]`   | Signed integer   | Yes                                                        |
| `TIME(fsp)`          | Time             | Yes                                                        |
| `UNSIGNED [INTEGER]` | Unsigned integer | Yes                                                        |
| `YEAR`               | Year             | No                                                         |

Examples:

The following statement converts a binary string from a HEX literal to a `CHAR`.

```sql
SELECT CAST(0x54694442 AS CHAR);
```

```sql
+--------------------------+
| CAST(0x54694442 AS CHAR) |
+--------------------------+
| TiDB                     |
+--------------------------+
1 row in set (0.0002 sec)
```

The following statement casts the values of the `a` attribute extracted from the JSON column to an unsigned array. Note that casting to an array is only supported as part of an index definition for multi-valued indexes.

```sql
CREATE TABLE t (
    id INT PRIMARY KEY,
    j JSON,
    INDEX idx_a ((CAST(j->'$.a' AS UNSIGNED ARRAY)))
);
INSERT INTO t VALUES (1, JSON_OBJECT('a',JSON_ARRAY(1,2,3)));
INSERT INTO t VALUES (2, JSON_OBJECT('a',JSON_ARRAY(4,5,6)));
INSERT INTO t VALUES (3, JSON_OBJECT('a',JSON_ARRAY(7,8,9)));
ANALYZE TABLE t;
```

```sql
 EXPLAIN SELECT * FROM t WHERE 1 MEMBER OF(j->'$.a')\G
*************************** 1. row ***************************
           id: IndexMerge_10
      estRows: 2.00
         task: root
access object: 
operator info: type: union
*************************** 2. row ***************************
           id: ├─IndexRangeScan_8(Build)
      estRows: 2.00
         task: cop[tikv]
access object: table:t, index:idx_a(cast(json_extract(`j`, _utf8mb4'$.a') as unsigned array))
operator info: range:[1,1], keep order:false, stats:partial[j:unInitialized]
*************************** 3. row ***************************
           id: └─TableRowIDScan_9(Probe)
      estRows: 2.00
         task: cop[tikv]
access object: table:t
operator info: keep order:false, stats:partial[j:unInitialized]
3 rows in set (0.00 sec)
```
## CONVERT

The [`CONVERT()`](https://dev.mysql.com/doc/refman/8.0/en/cast-functions.html#function_convert) function is used to convert between [character sets](https://docs.pingcap.com/tidb/stable/character-set-and-collation).

Example:

```sql
SELECT CONVERT(0x616263 USING utf8mb4);
```

```sql
+---------------------------------+
| CONVERT(0x616263 USING utf8mb4) |
+---------------------------------+
| abc                             |
+---------------------------------+
1 row in set (0.0004 sec)
```
## MySQL compatibility

- TiDB does not support cast operations on `SPATIAL` types. For more information, see [#6347](https://github.com/pingcap/tidb/issues/6347).
- TiDB does not support `AT TIME ZONE` for `CAST()`. For more information, see [#51742](https://github.com/pingcap/tidb/issues/51742).
- `CAST(24 AS YEAR)` returns 2 digits in TiDB and 4 digits in MySQL. For more information, see [#29629](https://github.com/pingcap/tidb/issues/29629).
