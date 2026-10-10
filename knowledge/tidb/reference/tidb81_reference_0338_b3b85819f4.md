# String function references for concatenation, element lookup, bit export, and set position

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Supported functions > [`CONCAT_WS()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_concat-ws) | String Functions > Supported functions > [`ELT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_elt) | String Functions > Supported functions > [`EXPORT_SET()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_export-set) | String Functions > Supported functions > [`FIELD()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_field) | String Functions > Supported functions > [`FIND_IN_SET()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_find-in-set)`
- Source Line Ranges: `300-534`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `string-functions`, `concatenation`, `separator`, `null-handling`, `bit-operations`, `set-type`, `position-lookup`, `sql-examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0338_b3b85819f4`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#concat-ws-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-concat-ws`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0d74c87a9c0e07f82cde49945609319543609f670f5c48fbd320103c37138d1f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#concat-ws-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-concat-ws
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up SQL string functions for separator-based concatenation, indexed element lookup, bit-to-string export, or position lookup in argument lists and comma-separated sets.
- Retrieval Keywords: CONCAT_WS(), CONCAT_WS(separator,str1,str2,...), separator is NULL returns NULL, skip NULL arguments, does not skip empty strings, empty separator equivalent to CONCAT(), ELT(), ELT(3, 'This', 'is', 'TiDB'), EXPORT_SET(), EXPORT_SET(bits, on, off, [separator[, number_of_bits]]), number_of_bits default 64, rightmost lowest bit, FIELD(), return the index position of the first argument, FIND_IN_SET(), SET data type, FIND_IN_SET('Go', 'COBOL,BASIC,Rust,Go,Java,Fortran')
- Follow-up Guidance: The examples show exact SQL statements and outputs for CONCAT_WS(), ELT(), EXPORT_SET(), FIELD(), and FIND_IN_SET().
- Classification Note: This is reference content because it defines function behavior, syntax, and example results for SQL string functions.

## Official Source Content

### [`CONCAT_WS()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_concat-ws)

The `CONCAT_WS()` function is a form of [`CONCAT()`](#concat) with a separator, which returns a string concatenated by the specified separator.

Syntax:

```sql
CONCAT_WS(separator,str1,str2,...)
```

- `separator`: the first argument is the separator, which concatenates the remaining arguments that are not `NULL`.
- `str1, str2, ...`: a list of arguments to be concatenated. Each argument can be a string or a number.

Example:

```sql
SELECT CONCAT_WS(',', 'TiDB Server', 'TiKV', 'PD');
```

Output:

```sql
+---------------------------------------------+
| CONCAT_WS(',', 'TiDB Server', 'TiKV', 'PD') |
+---------------------------------------------+
| TiDB Server,TiKV,PD                         |
+---------------------------------------------+
```

- If the separator is an empty string, `CONCAT_WS()` is equivalent to `CONCAT()` and returns the concatenated string of the remaining arguments.

    Example:

    ```sql
    SELECT CONCAT_WS('', 'TiDB Server', 'TiKV', 'PD');
    ```

    Output:

    ```sql
    +--------------------------------------------+
    | CONCAT_WS('', 'TiDB Server', 'TiKV', 'PD') |
    +--------------------------------------------+
    | TiDB ServerTiKVPD                          |
    +--------------------------------------------+
    ```

- If the separator is `NULL`, `CONCAT_WS()` returns `NULL`.

    Example:

    ```sql
    SELECT CONCAT_WS(NULL, 'TiDB Server', 'TiKV', 'PD');
    ```

    Output:

    ```sql
    +----------------------------------------------+
    | CONCAT_WS(NULL, 'TiDB Server', 'TiKV', 'PD') |
    +----------------------------------------------+
    | NULL                                         |
    +----------------------------------------------+
    ```

- If only one of the arguments to be concatenated is not `NULL`, `CONCAT_WS()` returns that argument.

    Example:

    ```sql
    SELECT CONCAT_WS(',', 'TiDB Server', NULL);
    ```

    Output:

    ```sql
    +-------------------------------------+
    | CONCAT_WS(',', 'TiDB Server', NULL) |
    +-------------------------------------+
    | TiDB Server                         |
    +-------------------------------------+
    ```

- If there are `NULL` arguments to be concatenated, `CONCAT_WS()` skips these `NULL` arguments.

    Example:

    ```sql
    SELECT CONCAT_WS(',', 'TiDB Server', NULL, 'PD');
    ```

    Output:

    ```sql
    +-------------------------------------------+
    | CONCAT_WS(',', 'TiDB Server', NULL, 'PD') |
    +-------------------------------------------+
    | TiDB Server,PD                            |
    +-------------------------------------------+
    ```

- If there are empty strings to be concatenated, `CONCAT_WS()` does not skip empty strings.

    Example:

    ```sql
    SELECT CONCAT_WS(',', 'TiDB Server', '', 'PD');
    ```

    Output:

    ```sql
    +-----------------------------------------+
    | CONCAT_WS(',', 'TiDB Server', '', 'PD') |
    +-----------------------------------------+
    | TiDB Server,,PD                         |
    +-----------------------------------------+
    ```
### [`ELT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_elt)

The `ELT()` function returns the element at the index number.

```sql
SELECT ELT(3, 'This', 'is', 'TiDB');
```

```sql
+------------------------------+
| ELT(3, 'This', 'is', 'TiDB') |
+------------------------------+
| TiDB                         |
+------------------------------+
1 row in set (0.00 sec)
```

The preceding example returns the third element, which is `'TiDB'`.
### [`EXPORT_SET()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_export-set)

The `EXPORT_SET()` function returns a string that consists of a specified number (`number_of_bits`) of `on`/`off` values, optionally separated by `separator`. These values are based on whether the corresponding bit in the `bits` argument is `1`, where the first value corresponds to the rightmost (lowest) bit of `bits`.

Syntax:

```sql
EXPORT_SET(bits, on, off, [separator[, number_of_bits]])
```

- `bits`: an integer representing the bit value.
- `on`: the string to be returned if the corresponding bit is `1`.
- `off`: the string to be returned if the corresponding bit is `0`.
- `separator` (optional): the separator character in the result string.
- `number_of_bits` (optional): the number of bits to be processed. If it is not set, `64` (the max size of bits) is used by default, which means that `bits` is treated as an unsigned 64-bit integer.

Examples:

In the following example, `number_of_bits` is set to `5`, resulting in 5 values, separated by `|`. Because only 3 bits are given, the other bits are considered unset. Therefore, setting `number_of_bits` to either `101` or `00101` results in the same output.

```sql
SELECT EXPORT_SET(b'101',"ON",'off','|',5);
```

```sql
+-------------------------------------+
| EXPORT_SET(b'101',"ON",'off','|',5) |
+-------------------------------------+
| ON|off|ON|off|off                   |
+-------------------------------------+
1 row in set (0.00 sec)
```

In the following example, `bits` is set to `00001111`, `on` is set to `x`, and `off` is set to `_`. This causes the function to return `____` for the `0` bits and `xxxx` for the `1` bits. Therefore, when processing with the bits in `00001111` from right to left, the function returns `xxxx____`.

```sql
SELECT EXPORT_SET(b'00001111', 'x', '_', '', 8);
```

```sql
+------------------------------------------+
| EXPORT_SET(b'00001111', 'x', '_', '', 8) |
+------------------------------------------+
| xxxx____                                 |
+------------------------------------------+
1 row in set (0.00 sec)
```

In the following example, `bits` is set to `00001111`, `on` is set to `x`, and `off` is set to `_`. This causes the function to return `x` for each `1` bit and `_` for each `0` bit. Therefore, when processing with the bits in `01010101` from right to left, the function returns `x_x_x_x_`.

```sql
SELECT EXPORT_SET(b'01010101', 'x', '_', '', 8);
```

```sql
+------------------------------------------+
| EXPORT_SET(b'01010101', 'x', '_', '', 8) |
+------------------------------------------+
| x_x_x_x_                                 |
+------------------------------------------+
1 row in set (0.00 sec)
```
### [`FIELD()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_field)

Return the index (position) of the first argument in the subsequent arguments.

In the following example, the first argument of `FIELD()` is `needle`, and it matches the second argument in the following list, so the function returns `2`.

```sql
SELECT FIELD('needle', 'A', 'needle', 'in', 'a', 'haystack');
+-------------------------------------------------------+
| FIELD('needle', 'A', 'needle', 'in', 'a', 'haystack') |
+-------------------------------------------------------+
|                                                     2 |
+-------------------------------------------------------+
1 row in set (0.00 sec)
```
### [`FIND_IN_SET()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_find-in-set)

Return the index position of the first argument within the second argument.

This function is often used with the [`SET`](https://docs.pingcap.com/tidb/stable/data-type-string#set-type) data type.

In the following example, `Go` is the fourth element in the set `COBOL,BASIC,Rust,Go,Java,Fortran`, so the function returns `4`.

```sql
SELECT FIND_IN_SET('Go', 'COBOL,BASIC,Rust,Go,Java,Fortran');
+-------------------------------------------------------+
| FIND_IN_SET('Go', 'COBOL,BASIC,Rust,Go,Java,Fortran') |
+-------------------------------------------------------+
|                                                     4 |
+-------------------------------------------------------+
1 row in set (0.00 sec)
```
