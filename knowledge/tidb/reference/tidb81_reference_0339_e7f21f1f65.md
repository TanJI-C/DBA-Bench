# FORMAT, FROM_BASE64, and HEX string functions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Supported functions > [`FORMAT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_format) | String Functions > Supported functions > [`FROM_BASE64()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_from-base64) | String Functions > Supported functions > [`HEX()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_hex)`
- Source Line Ranges: `535-681`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `string-functions`, `sql-functions`, `formatting`, `base64`, `hexadecimal`, `examples`, `null-handling`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0339_e7f21f1f65`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#format-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-format`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `349afa4da883685925eda2000635344b57b31b1c145be7543a683c8316f78ca4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#format-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-format
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB SQL string function behavior and examples for FORMAT(), FROM_BASE64(), or HEX(), including rounding, locale formatting, Base64 decoding, hexadecimal conversion, NULL handling, and warnings.
- Retrieval Keywords: FORMAT(X,D[,locale]), FORMAT(), FROM_BASE64(), HEX(), TO_BASE64(), UNHEX(HEX('abc')), CONVERT(FROM_BASE64('SGVsbG8gVGlEQg==') USING utf8mb4), Warning (Code 1292), Truncated incorrect DOUBLE value, scientific notation, lc_time_names, en_US, --binary-as-hex, --skip-binary-as-hex, hexadecimal literal, CONV(n, 10, 16), HEX(NULL)
- Follow-up Guidance: The examples also show related expressions such as TO_BASE64(), UNHEX(), CONVERT(... USING utf8mb4), and CONV(HEX(255), 16, 10) for interpreting the results of FROM_BASE64() and HEX().
- Classification Note: This is reference content because it defines the syntax, arguments, behaviors, notes, warnings, NULL results, and SQL examples for the FORMAT(), FROM_BASE64(), and HEX() string functions.

## Official Source Content

### [`FORMAT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_format)

The `FORMAT(X,D[,locale])` function is used to format the number `X` to a format similar to `"#,###,###. ##"`, rounded to `D` decimal places, and return the result as a string.

Arguments:

- `X`: the number to be formatted. It can be a direct numeric value, a numeric string, or a number in scientific notation.
- `D`: the number of decimal places for the returned value. The function rounds the number `X` to `D` decimal places. If `D` is greater than the actual number of decimal places in `X`, the result is padded with zeros to the corresponding length.
- `[locale]`: specifies a locale setting to be used for grouping between decimal points, thousands separators, and separators for resultant numbers. A valid locale value is the same as the valid value of the [`lc_time_names`](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_lc_time_names) system variable. If not specified or the region setting is `NULL`, the `'en_US'` region setting is used by default. This argument is optional.

Behaviors:

- If the first argument is a string and contains only numbers, the function returns a result based on that numeric value. For example, `FORMAT('12.34', 1)` and `FORMAT(12.34, 1)` return the same result.
- If the first argument is a number represented in scientific notation (using `E/e`), the function returns the result based on that number. For example, `FORMAT('1E2', 3)` returns `100.000`.
- If the first argument is a string starting with non-numeric characters, the function returns zero and a warning `(Code 1292)`. For example, `FORMAT('q12.36', 5)` returns `0.00000`, but also includes a warning `Warning (Code 1292): Truncated incorrect DOUBLE value: 'q12.36'`.
- If the first argument is a string mixing numbers and non-numbers, the function returns a result based on the consecutive numeric part at the beginning of the argument, and also includes a warning `(Code 1292)`. For example, `FORMAT('12.36q56.78', 1)` returns the same numeric result as `FORMAT('12.36', 1)`, but includes a warning `Warning (Code 1292): Truncated incorrect DOUBLE value: '12.36q56.78'`.
- If the second argument is zero or a negative number, the function truncates the decimal part and returns an integer.
- If any of the arguments is `NULL`, the function returns `NULL`.

Examples:

The following examples show how to format the number 12.36 to different decimal places:

```sql
mysql> SELECT FORMAT(12.36, 1);
+------------------+
| FORMAT(12.36, 1) |
+------------------+
| 12.4             |
+------------------+
```

```sql
mysql> SELECT FORMAT(12.36, 5);
+------------------+
| FORMAT(12.36, 5) |
+------------------+
| 12.36000         |
+------------------+
```

```sql
mysql> SELECT FORMAT(12.36, 2);
+------------------+
| FORMAT(12.36, 2) |
+------------------+
| 12.36            |
+------------------+
```
### [`FROM_BASE64()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_from-base64)

The `FROM_BASE64()` function is used to decode a [Base64](https://datatracker.ietf.org/doc/html/rfc4648) encoded string and return the decoded result in its hexadecimal form.

- This function accepts a single argument, that is, the Base64 encoded string to be decoded.
- If the argument is `NULL` or not a valid Base64 encoded string, the `FROM_BASE64()` function returns `NULL`.

Examples:

The following example shows how to decode the Base64 encoded string `'SGVsbG8gVGlEQg=='`. This string is the result of encoding `'Hello TiDB'`, using the [`TO_BASE64()`](#to_base64) function.

```sql
mysql> SELECT TO_BASE64('Hello TiDB');
+-------------------------+
| TO_BASE64('Hello TiDB') |
+-------------------------+
| SGVsbG8gVGlEQg==        |
+-------------------------+

mysql> SELECT FROM_BASE64('SGVsbG8gVGlEQg==');
+------------------------------------------------------------------+
| FROM_BASE64('SGVsbG8gVGlEQg==')                                  |
+------------------------------------------------------------------+
| 0x48656C6C6F2054694442                                           |
+------------------------------------------------------------------+
```

```sql
mysql> SELECT CONVERT(FROM_BASE64('SGVsbG8gVGlEQg==') USING utf8mb4);
+--------------------------------------------------------+
| CONVERT(FROM_BASE64('SGVsbG8gVGlEQg==') USING utf8mb4) |
+--------------------------------------------------------+
| Hello TiDB                                             |
+--------------------------------------------------------+
```

The following example shows how to decode the Base64 encoded number `MTIzNDU2`. This string is the result of encoding `123456`, which can be done using the [`TO_BASE64()`](#to_base64) function.

```sql
mysql> SELECT FROM_BASE64('MTIzNDU2');
+--------------------------------------------------+
| FROM_BASE64('MTIzNDU2')                          |
+--------------------------------------------------+
| 0x313233343536                                   |
+--------------------------------------------------+
```
### [`HEX()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_hex)

The `HEX()` function is used to convert the given argument into a string representation of its hexadecimal value. The argument can be either a string or a number.

- If the argument is a string, `HEX(str)` returns a hexadecimal string representation of `str`. The function converts each byte of each character in `str` into two hexadecimal digits. For example, the character `a` in a UTF-8 or ASCII character set is represented as a binary value of `00111101`, or `61` in hexadecimal notation.
- If the argument is a number, `HEX(n)` returns a hexadecimal string representation of `n`. The function treats the argument `n` as a `BIGINT` number, equivalent to using `CONV(n, 10, 16)`.
- If the argument is `NULL`, the function returns `NULL`.

> **Note:**
>
> In the MySQL client, the [`--binary-as-hex`](https://dev.mysql.com/doc/refman/8.0/en/mysql-command-options.html#option_mysql_binary-as-hex) option is enabled by default in interactive mode, causing the client to display data with an unknown character set as a [hexadecimal literal](https://dev.mysql.com/doc/refman/8.0/en/hexadecimal-literals.html). You can use the `--skip-binary-as-hex` option to disable this behavior.

Examples (with `mysql --skip-binary-as-hex`):

```sql
SELECT X'616263', HEX('abc'), UNHEX(HEX('abc')), 0x616263;
+-----------+------------+-------------------+----------+
| X'616263' | HEX('abc') | UNHEX(HEX('abc')) | 0x616263 |
+-----------+------------+-------------------+----------+
| abc       | 616263     | abc               | abc      |
+-----------+------------+-------------------+----------+
```

```sql
SELECT X'F09F8DA3', HEX('🍣'), UNHEX(HEX('🍣')), 0xF09F8DA3;
+-------------+-------------+--------------------+------------+
| X'F09F8DA3' | HEX('🍣')     | UNHEX(HEX('🍣'))     | 0xF09F8DA3 |
+-------------+-------------+--------------------+------------+
| 🍣            | F09F8DA3    | 🍣                   | 🍣           |
+-------------+-------------+--------------------+------------+
```

```sql
SELECT HEX(255), CONV(HEX(255), 16, 10);
+----------+------------------------+
| HEX(255) | CONV(HEX(255), 16, 10) |
+----------+------------------------+
| FF       | 255                    |
+----------+------------------------+
```

```sql
SELECT HEX(NULL);
+-----------+
| HEX(NULL) |
+-----------+
| NULL      |
+-----------+
```
