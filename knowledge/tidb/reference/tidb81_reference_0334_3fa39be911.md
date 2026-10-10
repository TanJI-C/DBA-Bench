# Expression evaluation and rounding

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/precision-math.md`
- Source Title: `Precision Math`
- Source Heading Path: `Precision Math > Expression handling | Precision Math > Rounding behavior`
- Source Line Ranges: `55-139`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `expression handling`, `sql mode`, `rounding`, `overflow`, `division by zero`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0334_3fa39be911`
- Source ID: `tidb-docs-8.1:functions-and-operators/precision-math.md#expression-handling`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d351b4ef70e7b735f4ba453665038f8ba1a821acca342dc88a07027ff2f41d01`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/precision-math#expression-handling
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/precision-math.md

## Retrieval Guidance

- Use When: Use this chunk when checking how TiDB evaluates numeric expressions, handles truncation or overflow under SQL mode, treats division by zero, or rounds exact and approximate values.
- Retrieval Keywords: Expression handling, Rounding behavior, strict SQL mode, sql_mode, TRADITIONAL, ERROR_FOR_DIVISION_BY_ZERO, floating-point arithmetic, DECIMAL exact arithmetic, BIGINT (64 bits), string to number conversion, division by 0, INSERT INTO t SET i = 1/0;, ROUND(), round half up, round half away from zero
- Follow-up Guidance: It provides the `sql_mode` result table for `INSERT INTO t SET i = 1/0;` and examples showing `ROUND(2.5)` and `ROUND(25E-1)`.
- Classification Note: This is reference content because it documents SQL expression evaluation, SQL mode effects, and rounding behavior with concrete examples.

## Official Source Content

## Expression handling

For expressions with precision math, TiDB uses the exact-value numbers as given whenever possible. For example, numbers in comparisons are used exactly as given without a change in value. In strict SQL mode, if you add an exact data type into a column, a number is inserted with its exact value if it is within the column range. When retrieved, the value is the same as what is inserted. If strict SQL mode is not enabled, truncation for INSERT is permitted in TiDB.

How to handle a numeric expression depends on the values of the expression:

- If the expression contains any approximate values, the result is approximate. TiDB evaluates the expression using floating-point arithmetic.
- If the expression contains no approximate values are present, which means only exact values are contained, and if any exact value contains a fractional part, the expression is evaluated using DECIMAL exact arithmetic and has a precision of 65 digits.
- Otherwise, the expression contains only integer values. The expression is exact. TiDB evaluates the expression using integer arithmetic and has a precision the same as BIGINT (64 bits).

If a numeric expression contains strings, the strings are converted to double-precision floating-point values and the result of the expression is approximate.

Inserts into numeric columns are affected by the SQL mode. The following discussions mention strict mode and `ERROR_FOR_DIVISION_BY_ZERO`. To turn on all the restrictions, you can simply use the `TRADITIONAL` mode, which includes both strict mode values and `ERROR_FOR_DIVISION_BY_ZERO`:

```sql
SET sql_mode = 'TRADITIONAL`;
```

If a number is inserted into an exact type column (DECIMAL or integer), it is inserted with its exact value if it is within the column range. For this number:

- If the value has too many digits in the fractional part, rounding occurs and a warning is generated.
- If the value has too many digits in the integer part, it is too large and is handled as follows:
    - If strict mode is not enabled, the value is truncated to the nearest legal value and a warning is generated.
    - If strict mode is enabled, an overflow error occurs.

To insert strings into numeric columns, TiDB handles the conversion from string to number as follows if the string has nonnumeric contents:

- In strict mode, a string (including an empty string) that does not begin with a number cannot be used as a number. An error, or a warning occurs.
- A string that begins with a number can be converted, but the trailing nonnumeric portion is truncated. In strict mode, if the truncated portion contains anything other than spaces, an error, or a warning occurs.

By default, the result of the division by 0 is NULL and no warning. By setting the SQL mode appropriately, division by 0 can be restricted. If you enable the `ERROR_FOR_DIVISION_BY_ZERO` SQL mode, TiDB handles division by 0 differently:

- In strict mode, inserts and updates are prohibited, and an error occurs.
- If it's not in the strict mode, a warning occurs.

In the following SQL statement:

```sql
INSERT INTO t SET i = 1/0;
```

The following results are returned in different SQL modes:

| `sql_mode` Value | Result |
| :--- | :--- |
| '' | No warning, no error; i is set to NULL.|
| strict | No warning, no error; i is set to NULL. |
| `ERROR_FOR_DIVISION_BY_ZERO` | Warning, no error; i is set to NULL. |
| strict, `ERROR_FOR_DIVISION_BY_ZERO` | Error; no row is inserted. |
## Rounding behavior

The result of the `ROUND()` function depends on whether its argument is exact or approximate:

- For exact-value numbers, the `ROUND()` function uses the "round half up" rule.
- For approximate-value numbers, the results in TiDB differs from that in MySQL:

    ```sql
    TiDB > SELECT ROUND(2.5), ROUND(25E-1);
    +------------+--------------+
    | ROUND(2.5) | ROUND(25E-1) |
    +------------+--------------+
    |          3 |            3 |
    +------------+--------------+
    1 row in set (0.00 sec)
    ```

For inserts into a DECIMAL or integer column, the rounding uses [round half away from zero](https://en.wikipedia.org/wiki/Rounding#Round_half_away_from_zero).

```sql
TiDB > CREATE TABLE t (d DECIMAL(10,0));
Query OK, 0 rows affected (0.01 sec)

TiDB > INSERT INTO t VALUES(2.5),(2.5E0);
Query OK, 2 rows affected, 2 warnings (0.00 sec)

TiDB > SELECT d FROM t;
+------+
| d    |
+------+
|    3 |
|    3 |
+------+
2 rows in set (0.00 sec)
```
