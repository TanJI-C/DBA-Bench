# String function support and examples: ASCII through CONCAT

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions | String Functions > Supported functions | String Functions > Supported functions > [`ASCII()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_ascii) | String Functions > Supported functions > [`BIN()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_bin) | String Functions > Supported functions > [`BIT_LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_bit-length) | String Functions > Supported functions > [`CHAR()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_char) | String Functions > Supported functions > [`CHAR_LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_char-length) | String Functions > Supported functions > [`CHARACTER_LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_character-length) | String Functions > Supported functions > [`CONCAT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_concat)`
- Source Line Ranges: `5-299`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `string-functions`, `sql-functions`, `ascii`, `binary-conversion`, `bit-length`, `character-length`, `concatenation`, `examples`, `mysql-compatibility`, `oracle-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0337_1612d04be8`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#string-functions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a091fb4a0d35d06e7c0231262a26eef7a5f99ae291b8c64edab78f1b7bbcd9c6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#string-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking for supported TiDB string functions and examples for ASCII(), BIN(), BIT_LENGTH(), CHAR(), CHAR_LENGTH(), CHARACTER_LENGTH(), or CONCAT(), including NULL behavior and sample SQL output.
- Retrieval Keywords: string functions, supported functions, ASCII(), BIN(), BIT_LENGTH(), CHAR(), CHAR_LENGTH(), CHARACTER_LENGTH(), CONCAT(), ASCII(str), CONCAT(str1,str2,...), Truncated incorrect INTEGER value: '123q123', BIN(-7), CHAR(65,66,67), SELECT CONCAT('TiDB', NULL, 'Server');, SELECT 'Ti' 'DB' ' ' 'Server';, Customers, CustomerName
- Follow-up Guidance: The source also notes that TiDB supports most MySQL 8.0 string functions and some Oracle 21 functions, and points to comparisons between functions and syntax of Oracle and TiDB.
- Classification Note: This is reference content because it lists supported SQL string functions with definitions, syntax, notes, and example queries and outputs.

## Official Source Content

# String Functions

TiDB supports most of the [string functions](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html) available in MySQL 8.0, and some of the [functions](https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlqr/SQL-Functions.html#GUID-93EC62F8-415D-4A7E-B050-5D5B2C127009) available in Oracle 21.

For comparisons between functions and syntax of Oracle and TiDB, see [Comparisons between Functions and Syntax of Oracle and TiDB](https://docs.pingcap.com/tidb/stable/oracle-functions-to-tidb).
## Supported functions
### [`ASCII()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_ascii)

The `ASCII(str)` function is used to get the ASCII value of the leftmost character in the given argument. The argument can be either a string or a number.

- If the argument is not empty, the function returns the ASCII value of the leftmost character.
- If the argument is an empty string, the function returns `0`.
- If the argument is `NULL`, the function returns `NULL`.

> **Note:**
>
> `ASCII(str)` only works for characters represented using 8 bits of binary digits (one byte).

Example:

```sql
SELECT ASCII('A'), ASCII('TiDB'), ASCII(23);
```

Output:

```sql
+------------+---------------+-----------+
| ASCII('A') | ASCII('TiDB') | ASCII(23) |
+------------+---------------+-----------+
|         65 |            84 |        50 |
+------------+---------------+-----------+
```
### [`BIN()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_bin)

The `BIN()` function is used to convert the given argument into a string representation of its binary value. The argument can be either a string or a number.

- If the argument is a positive number, the function returns a string representation of its binary value.
- If the argument is a negative number, the function converts the absolute value of the argument to its binary representation, inverts each bit of the binary value (changing `0` to `1` and `1` to `0`), and then adds `1` to the inverted value.
- If the argument is a string containing only digits, the function returns the result according to those digits. For example, the results for `"123"` and `123` are the same.
- If the argument is a string and its first character is not a digit (such as `"q123"`), the function returns `0`.
- If the argument is a string that consists of digits and non-digits, the function returns the result according to the consecutive digits at the beginning of the argument. For example, the results for `"123q123"` and `123` are the same, but `BIN('123q123')` generates a warning like `Truncated incorrect INTEGER value: '123q123'`.
- If the argument is `NULL`, the function returns `NULL`.

Example 1:

```sql
SELECT BIN(123), BIN('123q123');
```

Output 1:

```sql
+----------+----------------+
| BIN(123) | BIN('123q123') |
+----------+----------------+
| 1111011  | 1111011        |
+----------+----------------+
```

Example 2:

```sql
SELECT BIN(-7);
```

Output 2:

```sql
+------------------------------------------------------------------+
| BIN(-7)                                                          |
+------------------------------------------------------------------+
| 1111111111111111111111111111111111111111111111111111111111111001 |
+------------------------------------------------------------------+
```
### [`BIT_LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_bit-length)

The `BIT_LENGTH()` function is used to return the length of a given argument in bits.

Examples:

```sql
SELECT BIT_LENGTH("TiDB");

+--------------------+
| BIT_LENGTH("TiDB") |
+--------------------+
|                 32 |
+--------------------+
```

8 bits per character x 4 characters = 32 bits

```sql
SELECT BIT_LENGTH("PingCAP 123");

+---------------------------+
| BIT_LENGTH("PingCAP 123") |
+---------------------------+
|                        88 |
+---------------------------+
```

8 bits per character (space is counted because it is a non-alphanumeric character) x 11 characters = 88 bits

```sql
SELECT CustomerName, BIT_LENGTH(CustomerName) AS BitLengthOfName FROM Customers;

+--------------------+-----------------+
| CustomerName       | BitLengthOfName |
+--------------------+-----------------+
| Albert Einstein    |             120 |
| Robert Oppenheimer |             144 |
+--------------------+-----------------+
```

> **Note:**
>
> The preceding example operates under the assumption that there is a database with a table named `Customers` and a column inside the table named `CustomerName`.
### [`CHAR()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_char)

The `CHAR()` function is used to get the corresponding character of a specific ASCII value. It performs the opposite operation of `ASCII()`, which returns the ASCII value of a specific character. If multiple arguments are supplied, the function works on all arguments and are then concatenated together.

Examples:

```sql
SELECT CHAR(65);

+------------+
|  CHAR(65)  |
+------------+
|          A |
+------------+
```

```sql
SELECT CHAR(84);

+------------+
|  CHAR(84)  |
+------------+
|          T |
+------------+
```

The `CHAR()` function can also be used to get the corresponding character of ASCII values that extend beyond the standard ASCII range (`0` - `127`).

```sql
/*For extended ASCII: */

SELECT CHAR(128);

+------------+
|  CHAR(128) |
+------------+
|       0x80 |
+------------+
```

The `CHAR()` function can also get the corresponding character value of a unicode value.

```sql
/* For Unicode: */

--skip-binary-as-hex

SELECT CHAR(50089);

+--------------+
|  CHAR(50089) |
+--------------+
|            é |
+--------------+
```

```sql
SELECT CHAR(65,66,67);
```

```
+----------------+
| CHAR(65,66,67) |
+----------------+
| ABC            |
+----------------+
1 row in set (0.00 sec)
```
### [`CHAR_LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_char-length)

The `CHAR_LENGTH()` function is used to get the total number of characters in a given argument as an integer.

Examples:

```sql
SELECT CHAR_LENGTH("TiDB") AS LengthOfString;

+----------------+
| LengthOfString |
+----------------+
|              4 |
+----------------+
```

```sql
SELECT CustomerName, CHAR_LENGTH(CustomerName) AS LengthOfName FROM Customers;

+--------------------+--------------+
| CustomerName       | LengthOfName |
+--------------------+--------------+
| Albert Einstein    |           15 |
| Robert Oppenheimer |           18 |
+--------------------+--------------+
```

> **Note:**
>
> The preceding example operates under the assumption that there is a database with a table named `Customers` and a column inside the table named `CustomerName`.
### [`CHARACTER_LENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_character-length)

The `CHARACTER_LENGTH()` function is the same as the `CHAR_LENGTH()` function. Both functions can be used synonymously because they generate the same output.
### [`CONCAT()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_concat)

The `CONCAT()` function concatenates one or more arguments into a single string.

Syntax:

```sql
CONCAT(str1,str2,...)
```

`str1, str2, ...` is a list of arguments to be concatenated. Each argument can be a string or a number.

Example:

```sql
SELECT CONCAT('TiDB', ' ', 'Server', '-', 1, TRUE);
```

Output:

```sql
+---------------------------------------------+
| CONCAT('TiDB', ' ', 'Server', '-', 1, TRUE) |
+---------------------------------------------+
| TiDB Server-11                              |
+---------------------------------------------+
```

If any of the arguments is `NULL`, `CONCAT()` returns `NULL`.

Example:

```sql
SELECT CONCAT('TiDB', NULL, 'Server');
```

Output:

```sql
+--------------------------------+
| CONCAT('TiDB', NULL, 'Server') |
+--------------------------------+
| NULL                           |
+--------------------------------+
```

In addition to the `CONCAT()` function, you can concatenate strings by placing them adjacent to each other as in the following example. Note that this method does not support numeric types.

```sql
SELECT 'Ti' 'DB' ' ' 'Server';
```

Output:

```sql
+-------------+
| Ti          |
+-------------+
| TiDB Server |
+-------------+
```
