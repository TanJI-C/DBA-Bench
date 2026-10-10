# TiDB Cloud Import Data CSV configuration options

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/csv-config-for-import-data.md`
- Source Title: `CSV Configurations for Importing Data`
- Source Heading Path: `CSV Configurations for Importing Data | CSV Configurations for Importing Data > Separator | CSV Configurations for Importing Data > Delimiter | CSV Configurations for Importing Data > Backslash escape | CSV Configurations for Importing Data > NULL value`
- Source Line Ranges: `5-76`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `csv`, `import-data`, `separator`, `delimiter`, `backslash-escape`, `null-value`, `parsing`, `cli`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0218_8ee0ad86a1`
- Source ID: `tidb-docs-8.1:tidb-cloud/csv-config-for-import-data.md#csv-configurations-for-importing-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d7835693e15d1cbfa035db38309145af836fdc6482619c482cd9695e7dac0d03`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/csv-config-for-import-data#csv-configurations-for-importing-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/csv-config-for-import-data.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud Import Data CSV configuration meanings, defaults, and parsing behavior for Separator, Delimiter, Backslash escape, or NULL value.
- Retrieval Keywords: TiDB Cloud Import Data CSV configurations, Separator, Delimiter, Backslash escape, NULL value, field separator, comma-separated values, tab-separated values, default ,, default ", default True, default \N, all fields are unquoted, "Michael""male" parse fail, standard CSV JSON field, Backslash escape = False, Backslash escape = True, custom null values are not supported in the console, TiDB Cloud CLI, ticloud serverless import start
- Follow-up Guidance: For importing CSV files and CLI-based custom NULL value configuration, the content points to Import CSV Files from Cloud Storage into TiDB Cloud Dedicated, TiDB Cloud CLI, and `ticloud serverless import start`.
- Classification Note: This chunk is classified as configuration because it defines CSV import options, their defaults, and how TiDB Cloud parses CSV content under those settings.

## Official Source Content

# CSV Configurations for Importing Data

This document introduces CSV configurations for the Import Data service on TiDB Cloud.

The following is the CSV Configuration window when you use the Import Data service on TiDB Cloud to import CSV files. For more information, see [Import CSV Files from Cloud Storage into TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files).

![CSV Configurations](/media/tidb-cloud/import-data-csv-config.png)
## Separator

- Definition: defines the field separator. It can be one or multiple characters, but must not be empty.

- Common values:

    * `,` for CSV (comma-separated values). As shown in the above screenshot, "1", "Michael", and "male" represent three fields.
    * `"\t"` for TSV (tab-separated values).

- Default: `,`
## Delimiter

- Definition: defines the delimiter used for quoting. If **Delimiter** is empty, all fields are unquoted.

- Common values:

    * `'"'` quotes fields with double-quote. As shown in the above screenshot, `"Michael","male"` represents two fields. Note that there must be a `,` between the two fields. If the data is `"Michael""male"` (without `,`), the import task will fail to parse. If the data is `"Michael,male"` (with only one double-quote), it is parsed as one field.
    * `''` disables quoting.

- Default: `"`
## Backslash escape

- Definition: whether to parse backslash inside fields as escape characters. If **Backslash escape** is `True`, the following sequences are recognized and converted:

    | Sequence | Converted to             |
    |----------|--------------------------|
    | `\0`     | Null character (`U+0000`)  |
    | `\b`     | Backspace (`U+0008`)       |
    | `\n`     | Line feed (`U+000A`)       |
    | `\r`     | Carriage return (`U+000D`) |
    | `\t`     | Tab (`U+0009`)             |
    | `\Z`     | Windows EOF (`U+001A`)     |

    In all other cases (for example, `\"`), the backslash is stripped, leaving the next character (`"`) in the field. The character left has no special roles (for example, delimiters) and is just an ordinary character. Quoting does not affect whether backslash is parsed as an escape character.

    Take the following fields as an example.

    - If the value is `True`, `"nick name is \"Mike\""` will be parsed as `nick name is "Mike"` and written to the target table.
    - If the value is `False`, it will be parsed as three fields: `"nick name is \"` , `Mike\`, and `""`. But it cannot be parsed correctly because the fields are not separated from each other.

    For standard CSV files, if there are double-quoted characters in a field to be recorded, you need to use two double-quotes for escaping. In this case, using `Backslash escape = True` will result in a parsing error, while using `Backslash escape = False` will correctly parse. A typical scenario is when the imported field contains JSON content. A standard CSV JSON field is normally stored as follows:

    `"{""key1"":""val1"", ""key2"": ""val2""}"`

    In this case, you can set `Backslash escape = False` and the field will be correctly escaped to the database as follows:

    `{"key1": "val1", "key2": "val2"}`

    If the content of the CSV source file is saved as JSON in the following way, then consider setting `Backslash escape = True` as follows. But this is not the standard format for CSV.

    `"{\"key1\": \"val1\", \"key2\":\"val2\" }"`

- Default: `True`
## NULL value

- Definition: defines the string that represents a `NULL` value in the CSV file.

- Default: `\N`

- Custom null values are not supported in the console. You can use the [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/get-started-with-cli) instead. For more information, see [`ticloud serverless import start`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-import-start).
