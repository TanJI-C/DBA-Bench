# Regular expression compatibility with MySQL

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/string-functions.md`
- Source Title: `String Functions`
- Source Heading Path: `String Functions > Regular expression compatibility with MySQL | String Functions > Regular expression compatibility with MySQL > Syntax compatibility | String Functions > Regular expression compatibility with MySQL > `match_type` compatibility | String Functions > Regular expression compatibility with MySQL > Data type compatibility | String Functions > Regular expression compatibility with MySQL > Other compatibility | String Functions > Regular expression compatibility with MySQL > Known issues`
- Source Line Ranges: `2328-2380`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `regular-expressions`, `mysql-compatibility`, `re2`, `icu`, `match-type`, `binary-strings`, `capturing-groups`, `known-issues`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0349_08db12c162`
- Source ID: `tidb-docs-8.1:functions-and-operators/string-functions.md#regular-expression-compatibility-with-mysql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ed5768c420dd80b35261066a2f8743111957f6a788853b2c675a797ffab6b1e3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#regular-expression-compatibility-with-mysql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/string-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB and MySQL regular expression compatibility details for `REGEXP_INSTR()`, `REGEXP_LIKE()`, `REGEXP_REPLACE()`, and `REGEXP_SUBSTR()`.
- Retrieval Keywords: Regular expression compatibility with MySQL, REGEXP_INSTR(), REGEXP_LIKE(), REGEXP_REPLACE(), REGEXP_SUBSTR(), RE2, ICU, match_type compatibility, c i m s n u, binary strings, capturing groups, SELECT REGEXP_LIKE(a, b, "s") FROM t1, REGEXP_REPLACE("", "^$", "123"), GitHub Issue #37981
- Follow-up Guidance: The chunk also points to a known issue at `GitHub Issue #37981` and includes the TiDB example `SELECT REGEXP_REPLACE('abcd','(.*)(.{2})$','\\1') AS s;`.
- Classification Note: This is a SQL reference chunk because it documents compatibility differences in regex syntax, `match_type`, data types, replacement behavior, and capturing groups between TiDB and MySQL.

## Official Source Content

## Regular expression compatibility with MySQL

The following sections describe the regular expression compatibility with MySQL, including `REGEXP_INSTR()`, `REGEXP_LIKE()`, `REGEXP_REPLACE()`, and `REGEXP_SUBSTR()`.
### Syntax compatibility

MySQL implements regular expression using International Components for Unicode (ICU), and TiDB uses RE2. To learn the syntax differences between the two libraries, you can refer to the [ICU documentation](https://unicode-org.github.io/icu/userguide/) and [RE2 Syntax](https://github.com/google/re2/wiki/Syntax).
### `match_type` compatibility

The value options of `match_type` between TiDB and MySQL are:

- Value options in TiDB are `"c"`, `"i"`, `"m"`, and `"s"`, and value options in MySQL are `"c"`, `"i"`, `"m"`, `"n"`, and `"u"`.
- The `"s"` in TiDB corresponds to `"n"` in MySQL. When `"s"` is set in TiDB, the `.` character also matches line terminators (`\n`).

    For example, the `SELECT REGEXP_LIKE(a, b, "n") FROM t1` in MySQL is the same as the `SELECT REGEXP_LIKE(a, b, "s") FROM t1` in TiDB.

- TiDB does not support `"u"`, which means Unix-only line endings in MySQL.

| `match_type` | MySQL | TiDB | Description                            |
|:------------:|-------|------|----------------------------------------|
| c            | Yes   | Yes  | Case-sensitive matching                |
| i            | Yes   | Yes  | Case-insensitive matching              |
| m            | Yes   | Yes  | Multi-line mode                        |
| s            | No    | Yes  | Matches newlines, same as `n` in MySQL |
| n            | Yes   | No   | Matches newlines, same as `s` in TiDB  |
| u            | Yes   | No   | UNIX&trade; line endings               |
### Data type compatibility

The difference between TiDB and MySQL support for the binary string type:

- MySQL does not support binary strings in regular expression functions since 8.0.22. For more details, refer to [MySQL documentation](https://dev.mysql.com/doc/refman/8.0/en/regexp.html). But in practice, regular functions can work in MySQL when all parameters or return types are binary strings. Otherwise, an error will be reported.
- Currently, TiDB prohibits using binary strings and an error will be reported under any circumstances.
### Other compatibility

- The behavior of replacing empty strings in TiDB is different from MySQL. Taking `REGEXP_REPLACE("", "^$", "123")` as an example:

    - MySQL does not replace the empty string and returns `""` as the result.
    - TiDB replaces the empty string and returns `"123"` as the result.

- The keyword used for capturing groups in TiDB is different from MySQL. MySQL uses `$` as the keyword, while TiDB uses `\\` as the keyword. In addition, TiDB only supports capturing groups numbered from `0` to `9`.

    For example, the following SQL statement returns `ab` in TiDB:

    ```sql
    SELECT REGEXP_REPLACE('abcd','(.*)(.{2})$','\\1') AS s;
    ```
### Known issues

- [GitHub Issue #37981](https://github.com/pingcap/tidb/issues/37981)
