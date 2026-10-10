# Date and time types overview and SQL mode behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/data-type-date-and-time.md`
- Source Title: `Date and Time Types`
- Source Heading Path: `Date and Time Types`
- Source Line Ranges: `5-79`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `date-types`, `time-types`, `sql-mode`, `zero-values`, `type-conversion`, `invalid-values`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0071_d5370be95e`
- Source ID: `tidb-docs-8.1:data-type-date-and-time.md#date-and-time-types`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8771f4244bc16752a5f654474f3febb6d762c41663f21252770610c3c9706f1e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/data-type-date-and-time#date-and-time-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/data-type-date-and-time.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB date and time type zero values, invalid temporal value conversion, date format expectations, numeric conversion of temporal values, or SQL mode effects such as NO_ZERO_DATE.
- Retrieval Keywords: DATE, TIME, DATETIME, TIMESTAMP, YEAR, sql_mode, @@sql_mode, NO_ZERO_DATE, NO_ZERO_IN_DATE, STRICT_TRANS_TABLES, zero value, invalid values, type conversion, Truncated incorrect time value, ERROR 1292 (22007), NOW()+0, NOW(3)+0, DATE_SUB(), DATE_ADD(), 0000-00-00, 00:00:00, 0000-00-00 00:00:00
- Follow-up Guidance: The examples show that changing @@sql_mode can change whether an invalid temporal input raises ERROR 1292 or is converted to a zero value such as 00:00:00.
- Classification Note: This is reference content because it summarizes supported temporal types, their zero values, and SQL mode dependent behavior for invalid date and time inputs.

## Official Source Content

# Date and Time Types

TiDB supports all MySQL date and time data types to store temporal values: [`DATE`](#date-type), [`TIME`](#time-type), [`DATETIME`](#datetime-type), [`TIMESTAMP`](#timestamp-type), and [`YEAR`](#year-type). For more information, see [Date and Time Data Types in MySQL](https://dev.mysql.com/doc/refman/8.0/en/date-and-time-types.html).

Each of these types has its range of valid values, and uses a zero value to indicate that it is an invalid value. In addition, the `TIMESTAMP` and `DATETIME` types can automatically generate new time values on modification.

When dealing with date and time value types, note:

+ Although TiDB tries to interpret different formats, the date-portion must be in the format of year-month-day (for example, '1998-09-04'), rather than month-day-year or day-month-year.
+ If the year-portion of a date is specified as 2 digits, TiDB converts it based on [specific rules](#two-digit-year-portion-contained-in-the-date).
+ If a numeric value is needed in the context, TiDB automatically converts the date or time value into a numeric type. For example:

    ```sql
    mysql> SELECT NOW(), NOW()+0, NOW(3)+0;
    +---------------------+----------------+--------------------+
    | NOW()               | NOW()+0        | NOW(3)+0           |
    +---------------------+----------------+--------------------+
    | 2012-08-15 09:28:00 | 20120815092800 | 20120815092800.889 |
    +---------------------+----------------+--------------------+
    ```

+ TiDB might automatically convert invalid values or values beyond the supported range to a zero value of that type. This behavior is dependent on the SQL Mode set. For example:

    ```sql
    mysql> show create table t1;
    +-------+---------------------------------------------------------------------------------------------------------+
    | Table | Create Table                                                                                            |
    +-------+---------------------------------------------------------------------------------------------------------+
    | t1    | CREATE TABLE `t1` (
      `a` time DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin |
    +-------+---------------------------------------------------------------------------------------------------------+
    1 row in set (0.00 sec)

    mysql> select @@sql_mode;
    +-------------------------------------------------------------------------------------------------------------------------------------------+
    | @@sql_mode                                                                                                                                |
    +-------------------------------------------------------------------------------------------------------------------------------------------+
    | ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION |
    +-------------------------------------------------------------------------------------------------------------------------------------------+
    1 row in set (0.00 sec)

    mysql> insert into t1 values ('2090-11-32:22:33:44');
    ERROR 1292 (22007): Truncated incorrect time value: '2090-11-32:22:33:44'
    mysql> set @@sql_mode='';                                                                                                                                                                                                                     Query OK, 0 rows affected (0.01 sec)

    mysql> insert into t1 values ('2090-11-32:22:33:44');
    Query OK, 1 row affected, 1 warning (0.01 sec)

    mysql> select * from t1;
    +----------+
    | a        |
    +----------+
    | 00:00:00 |
    +----------+
    1 row in set (0.01 sec)
    ```

+ Setting different SQL modes can change TiDB behaviors.
+ If the SQL mode `NO_ZERO_DATE` is not enabled, TiDB allows month or day in the columns of `DATE` and `DATETIME` to be zero value, for example, '2009-00-00' or '2009-01-00'. If this date type is to be calculated in a function, for example, in `DATE_SUB()` or `DATE_ADD()`, the result can be incorrect.
+ By default, TiDB enables the SQL mode `NO_ZERO_DATE`. This mode prevents storing zero values such as '0000-00-00'.

Different types of zero value are shown in the following table:

| Date Type | "Zero" Value |
| :------   |  :----       |
| DATE      | '0000-00-00' |
| TIME      | '00:00:00'   |
| DATETIME  | '0000-00-00 00:00:00' |
| TIMESTAMP | '0000-00-00 00:00:00' |
| YEAR      | 0000         |

Invalid `DATE`, `DATETIME`, `TIMESTAMP` values are automatically converted to the corresponding type of zero value ( '0000-00-00' or '0000-00-00 00:00:00' ) if the SQL mode permits such usage.
