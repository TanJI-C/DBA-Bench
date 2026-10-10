# Date and time function compatibility and related system variable

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/date-and-time-functions.md`
- Source Title: `Date and Time Functions`
- Source Heading Path: `Date and Time Functions > MySQL compatibility | Date and Time Functions > Related system variables`
- Source Line Ranges: `82-103`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `mysql-compatibility`, `str_to_date`, `date-formatting`, `week-format`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0296_223bbf48fc`
- Source ID: `tidb-docs-8.1:functions-and-operators/date-and-time-functions.md#mysql-compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `da8f319b32f7d59f1bcada4893479c9f4972205e71a18d770337eb7d5062f475`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/date-and-time-functions#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/date-and-time-functions.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB support and limitations for STR_TO_DATE(), unsupported date and time format specifiers, or the system variable that affects WEEK().
- Retrieval Keywords: STR_TO_DATE(), MySQL compatibility, not implemented, date and time formatting options, %a, %D, %U, %u, %V, %v, %W, %w, %X, %x, default_week_format, WEEK() function, issue #30082
- Follow-up Guidance: The source also states that the default_week_format variable affects the WEEK() function.
- Classification Note: The official content is reference material because it lists MySQL compatibility details, unsupported format identifiers, and a related system variable for date and time functions.

## Official Source Content

## MySQL compatibility

The function `STR_TO_DATE()` is supported by TiDB, but is unable to parse all date and time values. In addition, the following date and time formatting options are **not implemented**:

| Format | Description                                                                           |
|--------|---------------------------------------------------------------------------------------|
| "%a"   | Abbreviated weekday name (Sun..Sat)                                                   |
| "%D"   | Day of the month with English suffix (0th, 1st, 2nd, 3rd)                             |
| "%U"   | Week (00..53), where Sunday is the first day of the week; WEEK() mode 0               |
| "%u"   | Week (00..53), where Monday is the first day of the week; WEEK() mode 1               |
| "%V"   | Week (01..53), where Sunday is the first day of the week; WEEK() mode 2; used with %X |
| "%v"   | Week (01..53), where Monday is the first day of the week; WEEK() mode 3; used with %x |
| "%W"   | Weekday name (Sunday..Saturday)                                                       |
| "%w"   | Day of the week (0=Sunday..6=Saturday)                                                |
| "%X"   | Year for the week where Sunday is the first day of the week, numeric, four digits.    |
| "%x"   | Year for the week, where Monday is the first day of the week, numeric, four digits.   |

See [issue #30082](https://github.com/pingcap/tidb/issues/30082) for more details.
## Related system variables

The [`default_week_format`](https://docs.pingcap.com/tidb/stable/system-variables#default_week_format) variable affects the `WEEK()` function.
