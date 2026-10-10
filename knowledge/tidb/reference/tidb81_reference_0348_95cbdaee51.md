# String function reference: substring, encoding, case, trim, hex, weight, unsupported

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Supported functions > [`SUBSTRING_INDEX()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_substring-index) | String Functions > Supported functions > [`TO_BASE64()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_to-base64) | String Functions > Supported functions > [`TRANSLATE()`](https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/TRANSLATE.html#GUID-80F85ACB-092C-4CC7-91F6-B3A585E3A690) | String Functions > Supported functions > [`TRIM()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_trim) | String Functions > Supported functions > [`UCASE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_ucase) | String Functions > Supported functions > [`UNHEX()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_unhex) | String Functions > Supported functions > [`UPPER()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_upper) | String Functions > Supported functions > [`WEIGHT_STRING()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_weight-string) | String Functions > Unsupported functions`
- Source Line Ranges: `2114-2327`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `string-functions`, `substring`, `base64`, `translate`, `trim`, `uppercase`, `hex`, `collation`, `unsupported-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0348_95cbdaee51`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#substring-index-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-substring-index`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d8a6d55bfddca7339760fb24a754de81a124836a8c72f9d68937e8c767fe30ae`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#substring-index-https-dev-mysql-com-doc-refman-8-0-en-string-functions-html-function-substring-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB string function reference details for `SUBSTRING_INDEX()`, `TO_BASE64()`, `TRANSLATE()`, `TRIM()`, `UCASE()`, `UNHEX()`, `UPPER()`, `WEIGHT_STRING()`, or the list of unsupported string functions.
- Retrieval Keywords: SUBSTRING_INDEX(), TO_BASE64(), TRANSLATE(), TRIM(), UCASE(), UNHEX(), UPPER(), WEIGHT_STRING(), LOAD_FILE(), MATCH(), SOUNDEX(), string functions, base-64 encoded form, weight string, Remove leading and trailing spaces, reverse operation of the HEX() function, AS CHAR(N), AS BINARY(N)
- Follow-up Guidance: The chunk also includes examples such as `SELECT SUBSTRING_INDEX('www.tidbcloud.com', '.', -1);`, `SELECT TO_BASE64('abc');`, `SELECT UNHEX('54694442');`, and `SELECT HEX(WEIGHT_STRING('ab' AS CHAR(3))) AS char_result, HEX(WEIGHT_STRING('ab' AS BINARY(3))) AS binary_result;`.
- Classification Note: This is a SQL reference chunk because it defines supported string functions, their syntax and behavior, gives example SQL statements, and lists unsupported functions.

## Official Source Content

### [`SUBSTRING_INDEX()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_substring-index)

The `SUBSTRING_INDEX()` function is used to extract a substring from a string based on a specified delimiter and count. This function is particularly useful when dealing with data separated by a specific delimiter, such as parsing CSV data or processing log files.

Syntax:

```sql
SUBSTRING_INDEX(str, delim, count)
```

- `str`: specifies the string to be processed.
- `delim`: specifies the delimiter in the string, which is case-sensitive.
- `count`: specifies the number of occurrences of the delimiter.
    - If `count` is a positive number, the function returns the substring before the `count` occurrences (counting from the left of the string) of the delimiter.
    - If `count` is a negative number, the function returns the substring after the `count` occurrences (counting from the right of the string) of the delimiter.
    - If `count` is `0`, the function returns an empty string.

Example 1:

```sql
SELECT SUBSTRING_INDEX('www.tidbcloud.com', '.', 2);
```

Output 1:

```sql
+-----------------------------------------+
| SUBSTRING_INDEX('www.tidbcloud.com', '.', 2) |
+-----------------------------------------+
| www.tidbcloud                                |
+-----------------------------------------+
```

Example 2:

```sql
SELECT SUBSTRING_INDEX('www.tidbcloud.com', '.', -1);
```

Output 2:

```sql
+------------------------------------------+
| SUBSTRING_INDEX('www.tidbcloud.com', '.', -1) |
+------------------------------------------+
| com                                      |
+------------------------------------------+
```
### [`TO_BASE64()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_to-base64)

The `TO_BASE64()` function is used to convert the given argument to a string in the base-64 encoded form and return the result according to the character set and collation of the current connection. A base-64 encoded string can be decoded using the [`FROM_BASE64()`](#from_base64) function.

Syntax:

```sql
TO_BASE64(str)
```

- If the argument is not a string, the function converts it to a string before base-64 encoding.
- If the argument is `NULL`, the function returns `NULL`.

Example 1:

```sql
SELECT TO_BASE64('abc');
```

Output 1:

```sql
+------------------+
| TO_BASE64('abc') |
+------------------+
| YWJj             |
+------------------+
```

Example 2:

```sql
SELECT TO_BASE64(6);
```

Output 2:

```sql
+--------------+
| TO_BASE64(6) |
+--------------+
| Ng==         |
+--------------+
```
### [`TRANSLATE()`](https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/TRANSLATE.html#GUID-80F85ACB-092C-4CC7-91F6-B3A585E3A690)

Replace all occurrences of characters by other characters in a string. It does not treat empty strings as `NULL` as Oracle does.
### [`TRIM()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_trim)

Remove leading and trailing spaces.
### [`UCASE()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_ucase)

The `UCASE()` function is used to convert a string to uppercase letters. This function is equivalent to the `UPPER()` function.

> **Note:**
>
> When the string is null, the `UCASE()` function returns `NULL`.

Example:

```sql
SELECT UCASE('bigdata') AS result_upper, UCASE(null) AS result_null;
```

Output:

```sql
+--------------+-------------+
| result_upper | result_null |
+--------------+-------------+
| BIGDATA      | NULL        |
+--------------+-------------+
```
### [`UNHEX()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_unhex)

The `UNHEX()` function performs the reverse operation of the `HEX()` function. It treats each pair of characters in the argument as a hexadecimal number and converts it to the character represented by that number, returning the result as a binary string.

> **Note:**
>
> - The argument must be a valid hexadecimal value that contains `0`–`9`, `A`–`F`, or `a`–`f`. If the argument is `NULL` or falls outside this range, the function returns `NULL`.
> - In the MySQL client, the [`--binary-as-hex`](https://dev.mysql.com/doc/refman/8.0/en/mysql-command-options.html#option_mysql_binary-as-hex) option is enabled by default in interactive mode, causing the client to display data with an unknown character set as a [hexadecimal literal](https://dev.mysql.com/doc/refman/8.0/en/hexadecimal-literals.html). You can use the `--skip-binary-as-hex` option to disable this behavior.

Example:

```sql
SELECT UNHEX('54694442');
```

Output:

```sql
+--------------------------------------+
| UNHEX('54694442')                    |
+--------------------------------------+
| 0x54694442                           |
+--------------------------------------+
```
### [`UPPER()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_upper)

The `UPPER()` function is used to convert a string to uppercase letters. This function is equivalent to the `UCASE()` function.

> **Note:**
>
> When the string is null, the `UPPER()` function returns `NULL`.

Example:

```sql
SELECT UPPER('bigdata') AS result_upper, UPPER(null) AS result_null;
```

Output:

```sql
+--------------+-------------+
| result_upper | result_null |
+--------------+-------------+
| BIGDATA      | NULL        |
+--------------+-------------+
```
### [`WEIGHT_STRING()`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_weight-string)

The `WEIGHT_STRING()` function returns the weight string (binary characters) for the input string, primarily used for sorting and comparison operations in multi-character set scenarios. If the argument is `NULL`, it returns `NULL`. The syntax is as follows:

```sql
WEIGHT_STRING(str [AS {CHAR|BINARY}(N)])
```

- `str`: the input string expression. If it is a non-binary string, such as a `CHAR`, `VARCHAR`, or `TEXT` value, the return value contains the collation weights for the string. If it is a binary string, such as a `BINARY`, `VARBINARY`, or `BLOB` value, the return value is the same as the input.

- `AS {CHAR|BINARY}(N)`: optional parameters used to specify the type and length of the output. `CHAR` represents the character data type, and `BINARY` represents the binary data type. `N` specifies the output length, which is an integer greater than or equal to 1.

> **Note:**
>
> If `N` is less than the string length, the string is truncated. If `N` exceeds the string length, `AS CHAR(N)` pads the string with spaces to the specified length, and `AS BINARY(N)` pads the string with `0x00` to the specified length.

Example:

```sql
SET NAMES 'utf8mb4';
SELECT HEX(WEIGHT_STRING('ab' AS CHAR(3))) AS char_result, HEX(WEIGHT_STRING('ab' AS BINARY(3))) AS binary_result;
```

Output:

```sql
+-------------+---------------+
| char_result | binary_result |
+-------------+---------------+
| 6162        | 616200        |
+-------------+---------------+
```
## Unsupported functions

* `LOAD_FILE()`
* `MATCH()`
* `SOUNDEX()`
