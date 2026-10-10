# Type code mappings and binary encoding in Canal-JSON

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-canal-json.md`
- Source Title: `TiCDC Canal-JSON Protocol`
- Source Heading Path: `TiCDC Canal-JSON Protocol > Integer types | TiCDC Canal-JSON Protocol > Binary and Blob types | TiCDC Canal-JSON Protocol > Binary and Blob types > Example of the encoding`
- Source Line Ranges: `217-299`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`, `shared`
- Topic Tags: `canal-json`, `integer-types`, `sqltype`, `mysqltype`, `binary-types`, `blob-types`, `encoding`, `varbinary`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0758_b1fa84655c`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-canal-json.md#integer-types`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e1fbf5dfa8040112def80ace489a29de153f37cef97bdd4480d25bf7ac8f8166`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-canal-json#integer-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-canal-json.md

## Retrieval Guidance

- Use When: Use this chunk when identifying Canal-JSON `sqlType` code mappings for signed or unsigned integer ranges or when decoding how TiCDC represents `binary`, `blob`, or `VARBINARY` bytes in Canal-JSON output.
- Retrieval Keywords: TiCDC Canal-JSON integer types, Java SQL Type Code, sqlType, mysqlType, tinyint unsigned, smallint unsigned, int unsigned, bigint unsigned, DECIMAL 3, INTEGER 4, SMALLINT 5, BIGINT -5, TINYINT -6, Bit -7, Binary and Blob types, ISO/IEC 8859-1, UTF-8 escape, VARBINARY, c_varbinary, \u0005\u0007\n\u000f$2+cx\u003c\u0026ÿþ-7F
- Follow-up Guidance: The chunk also includes a byte-by-byte `VARBINARY` encoding example in a Canal-JSON `Update` event for the `c_varbinary` column.
- Classification Note: This is reference content because it provides exact mapping tables for MySQL integer ranges to Java SQL type codes and exact binary character encoding rules in TiCDC Canal-JSON.

## Official Source Content

## Integer types

You need to consider whether [integer types](https://docs.pingcap.com/tidb/stable/data-type-numeric#integer-types) have the `Unsigned` constraint and the value size, which corresponds to different Java SQL Type Codes respectively, as shown in the following table.

| MySQL Type String  | Value Range                                 | Java SQL Type Code |
| :------------------| :------------------------------------------ | :----------------- |
| tinyint            | [-128, 127]                                 | -6                 |
| tinyint unsigned   | [0, 127]                                    | -6                 |
| tinyint unsigned   | [128, 255]                                  | 5                  |
| smallint           | [-32768, 32767]                             | 5                  |
| smallint unsigned  | [0, 32767]                                  | 5                  |
| smallint unsigned  | [32768, 65535]                              | 4                  |
| mediumint          | [-8388608, 8388607]                         | 4                  |
| mediumint unsigned | [0, 8388607]                                | 4                  |
| mediumint unsigned | [8388608, 16777215]                         | 4                  |
| int                | [-2147483648, 2147483647]                   | 4                  |
| int unsigned       | [0, 2147483647]                             | 4                  |
| int unsigned       | [2147483648, 4294967295]                    | -5                 |
| bigint             | [-9223372036854775808, 9223372036854775807] | -5                 |
| bigint unsigned    | [0, 9223372036854775807]                    | -5                 |
| bigint unsigned    | [9223372036854775808, 18446744073709551615] | 3                  |

The following table shows the mapping relationships between Java SQL Types in TiCDC and their codes.

| Java SQL Type | Java SQL Type Code |
| :-------------| :------------------|
| CHAR          | 1                  |
| DECIMAL       | 3                  |
| INTEGER       | 4                  |
| SMALLINT      | 5                  |
| REAL          | 7                  |
| DOUBLE        | 8                  |
| VARCHAR       | 12                 |
| DATE          | 91                 |
| TIME          | 92                 |
| TIMESTAMP     | 93                 |
| BLOB          | 2004               |
| CLOB          | 2005               |
| BIGINT        | -5                 |
| TINYINT       | -6                 |
| Bit           | -7                 |

For more information about Java SQL Types, see [Java SQL Class Types](https://docs.oracle.com/javase/8/docs/api/java/sql/Types.html).
## Binary and Blob types

TiCDC encodes [binary types](https://docs.pingcap.com/tidb/stable/data-type-string#binary-type) in the Canal-JSON format by converting each byte to its character representation as follows:

- Printable characters are represented using the ISO/IEC 8859-1 character encodings. 
- Non-printable characters and certain characters with special meaning in HTML are represented using their UTF-8 escape sequence. 

The following table shows the detailed representation information.

| Character type                | Value range | Character representation |
| :---------------------------| :-----------| :---------------------|
| Control characters          | [0, 31]     | UTF-8 escape (such as `\u0000` through `\u001F`) |
| Horizontal tab              | [9]         | `\t`                    |
| Line feed                   | [10]        | `\n`                    |
| Carriage return              | [13]       | `\r`                    |
| Printable characters        | [32, 127]   | Literal character (such as `A`) |
| Ampersand                   | [38]        | `\u0026`                |
| Less-than sign              | [60]        | `\u0038`                |
| Greater-than sign           | [62]        | `\u003E`                |
| Extended control characters | [128, 159]  | Literal character   |
| ISO 8859-1 (Latin-1)        | [160, 255]  | Literal character   |
### Example of the encoding

For example, the following 16 bytes `[5 7 10 15 36 50 43 99 120 60 38 255 254 45 55 70]` stored in a `VARBINARY` column called `c_varbinary` are encoded in a Canal-JSON `Update` event as follows:

```json
{
    ...
    "data": [
        {
            ...
            "c_varbinary": "\u0005\u0007\n\u000f$2+cx\u003c\u0026ÿþ-7F"
        }
    ]
    ...
}
```
