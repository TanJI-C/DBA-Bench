# Lightning CSV schema and format configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-data-source.md`
- Source Title: `TiDB Lightning Data Sources`
- Source Heading Path: `TiDB Lightning Data Sources > CSV | TiDB Lightning Data Sources > CSV > Schema | TiDB Lightning Data Sources > CSV > Configuration | TiDB Lightning Data Sources > CSV > Configuration > `separator` | TiDB Lightning Data Sources > CSV > Configuration > `delimiter` | TiDB Lightning Data Sources > CSV > Configuration > `terminator` | TiDB Lightning Data Sources > CSV > Configuration > `header` | TiDB Lightning Data Sources > CSV > Configuration > `not-null` and `null` | TiDB Lightning Data Sources > CSV > Configuration > `backslash-escape` | TiDB Lightning Data Sources > CSV > Configuration > `trim-last-separator` | TiDB Lightning Data Sources > CSV > Configuration > Non-configurable options`
- Source Line Ranges: `100-250`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `sql`, `tidb`
- Topic Tags: `csv`, `schema`, `mydumper-csv`, `separator`, `delimiter`, `terminator`, `header`, `null-handling`, `backslash-escape`, `deprecated-options`, `load-data-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0336_e5fb1e6452`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-data-source.md#csv`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c2f8a17ea94e39b8e30328db341c09014cdbf8fe450fd5135c70233c419e0957`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-data-source#csv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-data-source.md

## Retrieval Guidance

- Use When: Use this when you need the TiDB Lightning CSV schema requirements or the exact `[mydumper.csv]` format options such as separators, delimiters, line terminators, headers, NULL handling, backslash escaping, and deprecated `trim-last-separator` behavior.
- Retrieval Keywords: CSV, [mydumper.csv], ${db_name}.${table_name}-schema.sql, ${db_name}-schema-create.sql, separator, delimiter, terminator, header, not-null, null = '\\N', backslash-escape, trim-last-separator, FIELDS TERMINATED BY, FIELDS ENCLOSED BY, LINES TERMINATED BY, FIELDS ESCAPED BY '\\', LOAD DATA, IGNORE n LINES, LINES STARTING BY
- Follow-up Guidance: The content also explains that `trim-last-separator` is deprecated and shows changing from `separator = ','` with `trim-last-separator = true` to using `terminator = ",\n"` or `",\r\n"` according to the actual file.
- Classification Note: This chunk is classified as configuration because it specifies the CSV import schema prerequisites and the exact `[mydumper.csv]` options and meanings used by TiDB Lightning.

## Official Source Content

## CSV
### Schema

CSV files are schema-less. To import CSV files into TiDB, you must provide a table schema. You can provide schema by either of the following methods:

* Create files named `${db_name}.${table_name}-schema.sql` and `${db_name}-schema-create.sql` that contain DDL statements.
* Manually create the table schema in TiDB.
### Configuration

You can configure the CSV format in the `[mydumper.csv]` section in the `tidb-lightning.toml` file. Most settings have a corresponding option in the [`LOAD DATA`](https://dev.mysql.com/doc/refman/8.0/en/load-data.html) statement of MySQL.

```toml
[mydumper.csv]
# The field separator. Can be one or multiple characters. The default is ','.
# If the data might contain commas, it is recommended to use '|+|' or other uncommon
# character combinations as a separator.
separator = ','
# Quoting delimiter. Empty value means no quoting.
delimiter = '"'
# Line terminator. Can be one or multiple characters. Empty value (default) means
# both "\n" (LF) and "\r\n" (CRLF) are line terminators.
terminator = ''
# Whether the CSV file contains a header.
# If `header` is true, the first line is skipped and mapped
# to the table columns.
header = true
# Whether the CSV file contains any NULL value.
# If `not-null` is true, all columns from CSV cannot be parsed as NULL.
not-null = false
# When `not-null` is false (that is, CSV can contain NULL),
# fields equal to this value will be treated as NULL.
null = '\N'
# Whether to parse backslash as escape character.
backslash-escape = true
# Whether to treat `separator` as the line terminator and trim all trailing separators.
trim-last-separator = false
```

If the input of a string field such as `separator`, `delimiter`, or `terminator` involves special characters, you can use a backslash to escape the special characters. The escape sequence must be a *double-quoted* string (`"…"`). For example, `separator = "\u001f"` means using the ASCII character `0X1F` as the separator.

You can use *single-quoted* strings (`'…'`) to suppress backslash escaping. For example, `terminator = '\n'` means using the two-character string, a backslash (`\`) followed by the letter `n`, as the terminator, rather than the LF `\n`.

For more details, see the [TOML v1.0.0 specification](https://toml.io/en/v1.0.0#string).
#### `separator`

- Defines the field separator.
- Can be one or multiple characters, but must not be empty.
- Common values:

    * `','` for CSV (comma-separated values).
    * `"\t"` for TSV (tab-separated values).
    * `"\u0001"` to use the ASCII character `0x01`.

- Corresponds to the `FIELDS TERMINATED BY` option in the LOAD DATA statement.
#### `delimiter`

- Defines the delimiter used for quoting.
- If `delimiter` is empty, all fields are unquoted.
- Common values:

    * `'"'` quotes fields with double-quote. The same as [RFC 4180](https://tools.ietf.org/html/rfc4180).
    * `''` disables quoting.

- Corresponds to the `FIELDS ENCLOSED BY` option in the `LOAD DATA` statement.
#### `terminator`

- Defines the line terminator.
- If `terminator` is empty, both `"\n"` (Line Feed) and `"\r\n"` (Carriage Return + Line Feed) are used as the line terminator.
- Corresponds to the `LINES TERMINATED BY` option in the `LOAD DATA` statement.
#### `header`

- Whether *all* CSV files contain a header row.
- If `header` is `true`, the first row is used as the *column names*. If `header` is `false`, the first row is treated as an ordinary data row.
#### `not-null` and `null`

- The `not-null` setting controls whether all fields are non-nullable.
- If `not-null` is `false`, the string specified by `null` is transformed to the SQL NULL instead of a specific value.
- Quoting does not affect whether a field is null.

    For example, in the following CSV file:

    ```csv
    A,B,C
    \N,"\N",
    ```

    In the default settings (`not-null = false; null = '\N'`), the columns `A` and `B` are both converted to NULL after being imported to TiDB. The column `C` is an empty string `''` but not NULL.
#### `backslash-escape`

- Whether to parse backslash inside fields as escape characters.
- If `backslash-escape` is true, the following sequences are recognized and converted:

    | Sequence | Converted to             |
    |----------|--------------------------|
    | `\0`     | Null character (`U+0000`)  |
    | `\b`     | Backspace (`U+0008`)       |
    | `\n`     | Line feed (`U+000A`)       |
    | `\r`     | Carriage return (`U+000D`) |
    | `\t`     | Tab (`U+0009`)             |
    | `\Z`     | Windows EOF (`U+001A`)     |

    In all other cases (for example, `\"`), the backslash is stripped, leaving the next character (`"`) in the field. The character left has no special roles (for example, delimiters) and is just an ordinary character.

- Quoting does not affect whether backslash is parsed as an escape character.

- Corresponds to the `FIELDS ESCAPED BY '\'` option in the `LOAD DATA` statement.
#### `trim-last-separator`

- Whether to treat `separator` as the line terminator and trim all trailing separators.

    For example, in the following CSV file:

    ```csv
    A,,B,,
    ```

    - When `trim-last-separator = false`, this is interpreted as a row of 5 fields `('A', '', 'B', '', '')`.
    - When `trim-last-separator = true`, this is interpreted as a row of 3 fields `('A', '', 'B')`.

- This option is deprecated. Use the `terminator` option instead.

    If your existing configuration is:

    ```toml
    separator = ','
    trim-last-separator = true
    ```

    It is recommended to change the configuration to:

    ```toml
    separator = ','
    terminator = ",\n" # Use ",\n" or ",'\r\n" according to your actual file.
    ```
#### Non-configurable options

TiDB Lightning does not support every option supported by the `LOAD DATA` statement. For example:

* There cannot be line prefixes (`LINES STARTING BY`).
* The header cannot be skipped (`IGNORE n LINES`) and must be valid column names.
