# Supported DATE TIME DATETIME TIMESTAMP and YEAR types

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/data-type-date-and-time.md`
- Source Title: `Date and Time Types`
- Source Heading Path: `Date and Time Types > Supported types | Date and Time Types > Supported types > `DATE` type | Date and Time Types > Supported types > `TIME` type | Date and Time Types > Supported types > `DATETIME` type | Date and Time Types > Supported types > `TIMESTAMP` type | Date and Time Types > Supported types > `TIMESTAMP` type > Timezone Handling | Date and Time Types > Supported types > `YEAR` type`
- Source Line Ranges: `80-147`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `date`, `time`, `datetime`, `timestamp`, `year`, `fractional-seconds`, `timezone`, `range-limits`, `year-2038`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0072_2c8554e4b4`
- Source ID: `tidb-docs-8.1:data-type-date-and-time.md#supported-types`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `893b1cf66dcc9e94c9b414fb745f0b2ea063bb9ff956a71a52bdfa896da1af25`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/data-type-date-and-time#supported-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/data-type-date-and-time.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for the supported TiDB DATE, TIME, DATETIME, TIMESTAMP, or YEAR types, their valid ranges, fractional seconds precision, timezone handling, or two-digit YEAR conversion rules.
- Retrieval Keywords: DATE type, TIME type, DATETIME type, TIMESTAMP type, YEAR type, TIME[(fsp)], DATETIME[(fsp)], TIMESTAMP[(fsp)], YEAR[(4)], fractional seconds precision, fsp, HH:MM:SS[.fraction], YYYY-MM-DD, YYYY-MM-DD HH:MM:SS[.fraction], timezone handling, time_zone, UTC time, Year 2038 Problem, 1970-01-01 00:00:01.000000, 2038-01-19 03:14:07.999999, 1901 to 2155, 0000
- Follow-up Guidance: This chunk also states that TIMESTAMP values are converted between the current time zone and UTC, while DATETIME is not handled in this way.
- Classification Note: This is reference content because it defines each temporal type syntax, value range, formatting, timezone behavior, and YEAR input rules.

## Official Source Content

## Supported types
### `DATE` type

`DATE` only contains date-portion and no time-portion, displayed in `YYYY-MM-DD` format. The supported range is '0000-01-01' to '9999-12-31':

```sql
DATE
```
### `TIME` type

For the `TIME` type, the format is `HH:MM:SS[.fraction]` and valid values range from '-838:59:59.000000' to '838:59:59.000000'. `TIME` is used not only to indicate the time within a day but also to indicate the time interval between 2 events. An optional `fsp` value in the range from 0 to 6 may be given to specify fractional seconds precision. If omitted, the default precision is 0:

```sql
TIME[(fsp)]
```

> **Note:**
>
> Pay attention to the abbreviated form of `TIME`. For example, '11:12' means '11:12:00' instead of '00:11:12'. However, '1112' means '00:11:12'. These differences are caused by the presence or absence of the `:` character.
### `DATETIME` type

`DATETIME` contains both date-portion and time-portion. Valid values range from '0000-01-01 00:00:00.000000' to '9999-12-31 23:59:59.999999'.

TiDB displays `DATETIME` values in `YYYY-MM-DD HH:MM:SS[.fraction]` format, but permits assignment of values to `DATETIME` columns using either strings or numbers. An optional fsp value in the range from 0 to 6 may be given to specify fractional seconds precision. If omitted, the default precision is 0:

```sql
DATETIME[(fsp)]
```
### `TIMESTAMP` type

`TIMESTAMP` contains both date-portion and time-portion. Valid values range from '1970-01-01 00:00:01.000000' to '2038-01-19 03:14:07.999999' in UTC time. An optional fsp value in the range from 0 to 6 may be given to specify fractional seconds precision. If omitted, the default precision is 0.

In `TIMESTAMP`, zero is not permitted to appear in the month-portion or day-portion. The only exception is zero value itself '0000-00-00 00:00:00'.

```sql
TIMESTAMP[(fsp)]
```
#### Timezone Handling

When `TIMESTAMP` is to be stored, TiDB converts the `TIMESTAMP` value from the current time zone to UTC time zone. When `TIMESTAMP` is to be retrieved, TiDB converts the stored `TIMESTAMP` value from UTC time zone to the current time zone (Note: `DATETIME` is not handled in this way). The default time zone for each connection is the server's local time zone, which can be modified by the environment variable `time_zone`.

> **Warning:**
>
> As in MySQL, the `TIMESTAMP` data type suffers from the [Year 2038 Problem](https://en.wikipedia.org/wiki/Year_2038_problem). For storing values that may span beyond 2038, please consider using the `DATETIME` type instead.
### `YEAR` type

The `YEAR` type is specified in the format 'YYYY'. Supported values range from 1901 to 2155, or the zero value of 0000:

```sql
YEAR[(4)]
```

`YEAR` follows the following format rules:

+ Four-digit numeral ranges from 1901 to 2155
+ Four-digit string ranges from '1901' to '2155'
+ One-digit or two-digit numeral ranges from 1 to 99. Accordingly, 1-69 is converted to 2001-2069 and 70-99 is converted to 1970-1999
+ One-digit or two-digit string ranges from '0' to '99'
+ Value 0 is taken as 0000 whereas the string '0' or '00' is taken as 2000

Invalid `YEAR` value is automatically converted to 0000 (if users are not using the `NO_ZERO_DATE` SQL mode).
