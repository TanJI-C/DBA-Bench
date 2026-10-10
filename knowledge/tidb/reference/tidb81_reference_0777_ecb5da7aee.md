# Schema file data type definitions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-cloud-storage.md`
- Source Title: `Replicate Data to Storage Services`
- Source Heading Path: `Replicate Data to Storage Services > Storage path structure > Data type | Replicate Data to Storage Services > Storage path structure > Data type > Integer types | Replicate Data to Storage Services > Storage path structure > Data type > Decimal types | Replicate Data to Storage Services > Storage path structure > Data type > Date and time types | Replicate Data to Storage Services > Storage path structure > Data type > String types | Replicate Data to Storage Services > Storage path structure > Data type > Enum and Set types`
- Source Line Ranges: `314-410`
- Source Scope: `cloud`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `schema-files`, `data-types`, `integer-types`, `decimal-types`, `datetime-types`, `string-types`, `enum-set`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0777_ecb5da7aee`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-cloud-storage.md#data-type`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d7c059b1b03f6df46056360bfb1cd6e574db4f4d37d8e6fd14ba8d7045ab3743`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-cloud-storage#data-type
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-cloud-storage.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting column type fields in TiCDC schema_{table-version}_{hash}.json files, especially ColumnType, ColumnPrecision, ColumnScale, and ColumnLength.
- Retrieval Keywords: schema_{table-version}_{hash}.json, Data type, Integer types, Decimal types, Date and time types, String types, Enum and Set types, ColumnType, ColumnPrecision, ColumnScale, ColumnLength, T(M[, D]), TINYINT, SMALLINT, MEDIUMINT, INT, BIGINT, BIT, FLOAT, DOUBLE, DECIMAL, NUMERIC, DATE, YEAR, TIME, DATETIME, TIMESTAMP, CHAR, VARCHAR, TEXT, BINARY, BLOB, JSON, ENUM, SET
- Follow-up Guidance: The source maps each TiDB type family to the exact schema file JSON representation for the corresponding column metadata fields.
- Classification Note: This is reference content because it defines the exact type encodings that appear in TiCDC schema files for different TiDB data type families.

## Official Source Content

### Data type

This section describes the data types used in the `schema_{table-version}_{hash}.json` file (hereafter referred to as "schema file" in the following sections). The data types are defined as `T(M[, D])`. For details, see [Data Types](https://docs.pingcap.com/tidb/stable/data-type-overview).
#### Integer types

Integer types in TiDB are defined as `IT[(M)] [UNSIGNED]`, where

- `IT` is the integer type, which can be `TINYINT`, `SMALLINT`, `MEDIUMINT`, `INT`, `BIGINT`, or `BIT`.
- `M` is the display width of the type.

Integer types are defined as follows in the schema file:

```json
{
    "ColumnName":"COL1",
    "ColumnType":"{IT} [UNSIGNED]",
    "ColumnPrecision":"{M}"
}
```
#### Decimal types

Decimal types in TiDB are defined as `DT[(M,D)][UNSIGNED]`, where

- `DT` is the floating-point type, which can be `FLOAT`, `DOUBLE`, `DECIMAL`, or `NUMERIC`.
- `M` is the precision of the data type, or the total number of digits.
- `D` is the number of digits following the decimal point.

Decimal types are defined as follows in the schema file:

```json
{
    "ColumnName":"COL1",
    "ColumnType":"{DT} [UNSIGNED]",
    "ColumnPrecision":"{M}",
    "ColumnScale":"{D}"
}
```
#### Date and time types

Date types in TiDB are defined as `DT`, where

- `DT` is the date type, which can be `DATE` or `YEAR`.

The date types are defined as follows in the schema file:

```json
{
    "ColumnName":"COL1",
    "ColumnType":"{DT}"
}
```

The time types in TiDB are defined as `TT[(M)]`, where

- `TT` is the time type, which can be `TIME`, `DATETIME`, or `TIMESTAMP`.
- `M` is the precision of seconds in the range from 0 to 6.

The time types are defined as follows in the schema file:

```json
{
    "ColumnName":"COL1",
    "ColumnType":"{TT}",
    "ColumnScale":"{M}"
}
```
#### String types

The string types in TiDB are defined as `ST[(M)]`, where

- `ST` is the string type, which can be `CHAR`, `VARCHAR`, `TEXT`, `BINARY`, `BLOB`, or `JSON`.
- `M` is the maximum length of the string.

The string types are defined as follows in the schema file:

```json
{
    "ColumnName":"COL1",
    "ColumnType":"{ST}",
    "ColumnLength":"{M}"
}
```
#### Enum and Set types

The Enum and Set types are defined as follows in the schema file:

```json
{
    "ColumnName":"COL1",
    "ColumnType":"{ENUM/SET}",
}
```
