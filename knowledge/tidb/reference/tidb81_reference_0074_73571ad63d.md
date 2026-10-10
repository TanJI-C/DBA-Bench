# Fractional precision, type conversions, and two-digit year rules

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/data-type-date-and-time.md`
- Source Title: `Date and Time Types`
- Source Heading Path: `Date and Time Types > Decimal part of time value | Date and Time Types > Conversions between date and time types | Date and Time Types > Two-digit year-portion contained in the date`
- Source Line Ranges: `172-261`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `datetime`, `timestamp`, `time`, `date`, `year`, `fractional-seconds`, `fsp`, `type-conversion`, `cast`, `rounding`, `numeric-conversion`, `two-digit-year`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0074_73571ad63d`
- Source ID: `tidb-docs-8.1:data-type-date-and-time.md#decimal-part-of-time-value`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ccae4fc743949b6932d5dfe07f6bfa0b589a6105dd8b61615c09220979c9801f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/data-type-date-and-time#decimal-part-of-time-value
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/data-type-date-and-time.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about fractional seconds precision in TIME, DATETIME, or TIMESTAMP, conversions among date and time types, numeric conversion behavior, or two-digit year interpretation rules.
- Retrieval Keywords: TIME(fsp), DATETIME(fsp), TIMESTAMP(fsp), fsp, fractional part up to 6 digits, microseconds, rounding fractional seconds, CREATE TABLE t1 (t TIME(3), dt DATETIME(6)), CREATE TABLE fractest( c1 TIME(2), c2 DATETIME(2), c3 TIMESTAMP(2) ), CAST(datetime_col AS DATE), DATE to DATETIME, DATE to TIMESTAMP, DATE to TIME, DATETIME to DATE, TIMESTAMP to DATE, DATETIME to TIME, TIME to DATE, CURRENT_DATE(), CURTIME()+0, NOW()+0, TIME to numeric format, DATETIME to numeric format, 1968-01-01 converted to TIMESTAMP becomes 0, TIMESTAMP range 1970 to 2038-01-19 03:14:07 UTC, two-digit year, 01 to 69 becomes 2001 to 2069, 70 to 99 becomes 1970 to 1999, YEAR(4) 00 becomes 0000, MIN() and MAX() two-digit year
- Follow-up Guidance: The source also notes that two-digit year values might not be properly calculated in functions such as MIN() and MAX(), and that four-digit format suits these functions better.
- Classification Note: This is reference content because it defines exact storage precision, conversion rules, ranges, SQL examples, and two-digit year mapping behavior for SQL date and time types.

## Official Source Content

## Decimal part of time value

`DATETIME` and `TIMESTAMP` values can contain a fractional part of up to 6 digits which is accurate to microseconds. In any column of `DATETIME` or `TIMESTAMP` types, a fractional part is stored instead of being discarded. With a fractional part, the value is in the format of 'YYYY-MM-DD HH:MM:SS[.fraction]', and the fraction ranges from 000000 to 999999. A decimal point must be used to separate the fraction from the rest.

+ Use `type_name(fsp)` to define a column that supports fractional precision, where `type_name` can be `TIME`, `DATETIME` or `TIMESTAMP`. For example,

    ```sql
    CREATE TABLE t1 (t TIME(3), dt DATETIME(6));
    ```

  `fsp` must range from 0 to 6.

  `0` means there is no fractional part. If `fsp` is omitted, the default is 0.

+ When inserting `TIME`, `DATETIME` or `TIMESTAMP` which contain a fractional part, if the number of digit of the fraction is too few, or too many, rounding might be needed in the situation. For example:

    ```sql
    mysql> CREATE TABLE fractest( c1 TIME(2), c2 DATETIME(2), c3 TIMESTAMP(2) );
    Query OK, 0 rows affected (0.33 sec)

    mysql> INSERT INTO fractest VALUES
         > ('17:51:04.777', '2014-09-08 17:51:04.777',   '2014-09-08 17:51:04.777');
    Query OK, 1 row affected (0.03 sec)

    mysql> SELECT * FROM fractest;
    +-------------|------------------------|------------------------+
    | c1          | c2                     | c3                     |
    +-------------|------------------------|------------------------+
    | 17:51:04.78 | 2014-09-08 17:51:04.78 | 2014-09-08 17:51:04.78 |
    +-------------|------------------------|------------------------+
    1 row in set (0.00 sec)
    ```
## Conversions between date and time types

Sometimes we need to make conversions between date and time types. But some conversions might lead to information loss. For example, `DATE`, `DATETIME` and `TIMESTAMP` values all have their own respective ranges. `TIMESTAMP` should be no earlier than the year 1970 in UTC time or no later than UTC time '2038-01-19 03:14:07'. Based on this rule, '1968-01-01' is a valid date value of `DATE` or `DATETIME`, but becomes 0 when it is converted to `TIMESTAMP`.

The conversions of `DATE`:

+ When `DATE` is converted to `DATETIME` or `TIMESTAMP`, a time-portion '00:00:00' is added, because DATE does not contain any time information
+ When `DATE` is converted to `TIME`, the result is '00:00:00'

Conversions of `DATETIME` or `TIMESTAMP`:

+ When `DATETIME` or `TIMESTAMP` is converted to `DATE`, the time and fractional part is discarded. For example, '1999-12-31 23:59:59.499' is converted to '1999-12-31'
+ When `DATETIME` or `TIMESTAMP` is converted to TIME, the date-portion is discarded, because `TIME` does not contain any date information

When we convert `TIME` to other time and date formats, the date-portion is automatically specified as `CURRENT_DATE()`. The final converted result is a date that consists of `TIME` and `CURRENT_DATE()`. This is to say that if the value of TIME is beyond the range from '00:00:00' to '23:59:59', the converted date-portion does not indicate the current day.

When `TIME` is converted to `DATE`, the process is similar, and the time-portion is discarded.

Using the `CAST()` function can explicitly convert a value to a `DATE` type. For example:

```sql
date_col = CAST(datetime_col AS DATE)
```

Converting `TIME` and `DATETIME` to numeric format. For example:

```sql
mysql> SELECT CURTIME(), CURTIME()+0, CURTIME(3)+0;
+-----------|-------------|--------------+
| CURTIME() | CURTIME()+0 | CURTIME(3)+0 |
+-----------|-------------|--------------+
| 09:28:00  |       92800 |    92800.887 |
+-----------|-------------|--------------+
mysql> SELECT NOW(), NOW()+0, NOW(3)+0;
+---------------------|----------------|--------------------+
| NOW()               | NOW()+0        | NOW(3)+0           |
+---------------------|----------------|--------------------+
| 2012-08-15 09:28:00 | 20120815092800 | 20120815092800.889 |
+---------------------|----------------|--------------------+
```
## Two-digit year-portion contained in the date

The two-digit year-portion contained in date does not explicitly indicate the actual year and is ambiguous.

For `DATETIME`, `DATE` and `TIMESTAMP` types, TiDB follows the following rules to eliminate ambiguity:

- Values between 01 and 69 is converted to a value between 2001 and 2069
- Values between 70 and 99 is converted to a value between 1970 and 1999

These rules also apply to the `YEAR` type, with one exception:

When numeral `00` is inserted to `YEAR(4)`, the result is 0000 rather than 2000.

If you want the result to be 2000, specify the value to be 2000.

The two-digit year-portion might not be properly calculated in some functions such `MIN()` and `MAX()`. For these functions, the four-digit format suites better.
