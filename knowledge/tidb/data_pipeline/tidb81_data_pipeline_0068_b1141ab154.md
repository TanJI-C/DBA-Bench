# TiCDC CSV protocol configuration, format, and type mapping

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-csv.md`
- Source Title: `TiCDC CSV Protocol`
- Source Heading Path: `TiCDC CSV Protocol | TiCDC CSV Protocol > Use CSV | TiCDC CSV Protocol > Transactional constraints | TiCDC CSV Protocol > Data storage path structure | TiCDC CSV Protocol > Definition of the data format | TiCDC CSV Protocol > Data type mapping`
- Source Line Ranges: `5-104`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `shared`
- Topic Tags: `csv`, `cloud-storage`, `sink`, `changefeed`, `protocol`, `transactional-constraints`, `storage-path`, `data-format`, `type-mapping`, `commit-ts`, `old-value`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0068_b1141ab154`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-csv.md#ticdc-csv-protocol`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fac8300022e0f34376fade0c57617b017a30a2a2c0e8b89b1415493207c1850f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-csv#ticdc-csv-protocol
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-csv.md

## Retrieval Guidance

- Use When: Use this when the user asks about TiCDC CSV protocol configuration for a cloud storage sink, CSV row format, transactional constraints, storage path reference, or MySQL-to-CSV type mapping.
- Retrieval Keywords: TiCDC CSV Protocol, cloud storage service downstream sink, cdc cli changefeed create, --sink-uri="s3://bucket/prefix", changefeed.toml, [sink] protocol = "csv", terminator = "\n", [sink.csv], delimiter, quote, null = '\\N', include-commit-ts, output-old-value, Transactional constraints, commit-ts, same transactions of a single table are stored in the same CSV file, Data storage path structure, Storage path structure, operation-type indicator I U D, is-update, INSERT UPDATE DELETE, hr.employee, CREATE TABLE `employee`, Data type mapping, BOOLEAN TINYINT SMALLINT INT MEDIUMINT BIGINT, TIMESTAMP DATETIME, VARBINARY BLOB Base64 or hex encoded, DECIMAL, ENUM, SET
- Follow-up Guidance: The source also points to the cloud storage sink documentation for more information about the storage path structure.
- Classification Note: This chunk is classified as data_pipeline for the ticdc component because it documents the CSV sink protocol, changefeed sink configuration, event encoding format, and type mapping for sending DML events to cloud storage.

## Official Source Content

# TiCDC CSV Protocol

When using a cloud storage service as the downstream sink, you can send DML events to the cloud storage service in CSV format.
## Use CSV

The following is an example of the configuration when using the CSV protocol:

```shell
cdc cli changefeed create --server=http://127.0.0.1:8300 --changefeed-id="csv-test" --sink-uri="s3://bucket/prefix" --config changefeed.toml
```

The configuration in the `changefeed.toml` file is as follows:

```toml
[sink]
protocol = "csv"
terminator = "\n"

[sink.csv]
delimiter = ',' # Before v7.6.0, you can only set the delimiter to a single character. Starting from v7.6.0, you can set it to 1-3 characters. For example, `$^` or `|@|`.
quote = '"'
null = '\N'
include-commit-ts = true
output-old-value = false
```
## Transactional constraints

- In a single CSV file, the `commit-ts` of a row is equal to or smaller than that of the subsequent row.
- The same transactions of a single table are stored in the same CSV file.
- Multiple tables of the same transaction can be stored in different CSV files.
## Data storage path structure

For more information about the storage path structure of the data, see [Storage path structure](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-cloud-storage#storage-path-structure).
## Definition of the data format

In the CSV file, each column is defined as follows:

- Column 1: The operation-type indicator, including `I`, `U`, and `D`. `I` means `INSERT`, `U` means `UPDATE`, and `D` means `DELETE`.
- Column 2: Table name.
- Column 3: Schema name.
- Column 4: The `commit-ts` of the source transaction. This column is optional.
- Column 5: The `is-update` column only exists when the value of `output-old-value` is true, which is used to identify whether the row data change comes from the UPDATE event (the value of the column is true) or the INSERT/DELETE event (the value is false).
- Column 6 to the last column: One or more columns with data changes.

Assume that table `hr.employee` is defined as follows:

```sql
CREATE TABLE `employee` (
  `Id` int NOT NULL,
  `LastName` varchar(20) DEFAULT NULL,
  `FirstName` varchar(30) DEFAULT NULL,
  `HireDate` date DEFAULT NULL,
  `OfficeLocation` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

When `include-commit-ts = true` and `output-old-value = false`, the DML events of this table are stored in the CSV format as follows:

```shell
"I","employee","hr",433305438660591626,101,"Smith","Bob","2014-06-04","New York"
"U","employee","hr",433305438660591627,101,"Smith","Bob","2015-10-08","Los Angeles"
"D","employee","hr",433305438660591629,101,"Smith","Bob","2017-03-13","Dallas"
"I","employee","hr",433305438660591630,102,"Alex","Alice","2017-03-14","Shanghai"
"U","employee","hr",433305438660591630,102,"Alex","Alice","2018-06-15","Beijing"
```

When `include-commit-ts = true` and `output-old-value = true`, the DML events of this table are stored in the CSV format as follows:

```
"I","employee","hr",433305438660591626,false,101,"Smith","Bob","2014-06-04","New York"
"D","employee","hr",433305438660591627,true,101,"Smith","Bob","2015-10-08","Shanghai"
"I","employee","hr",433305438660591627,true,101,"Smith","Bob","2015-10-08","Los Angeles"
"D","employee","hr",433305438660591629,false,101,"Smith","Bob","2017-03-13","Dallas"
"I","employee","hr",433305438660591630,false,102,"Alex","Alice","2017-03-14","Shanghai"
"D","employee","hr",433305438660591630,true,102,"Alex","Alice","2017-03-14","Beijing"
"I","employee","hr",433305438660591630,true,102,"Alex","Alice","2018-06-15","Beijing"
```
## Data type mapping

| MySQL type                                          | CSV type | Example                          | Description                                   |
|-----------------------------------------------------|----------|------------------------------|---------------------------------------|
| `BOOLEAN`/`TINYINT`/`SMALLINT`/`INT`/`MEDIUMINT`/`BIGINT` | Integer | `123` | - |
| `FLOAT`/`DOUBLE`                                        | Float    | `153.123`                      |  -                                     |
| `NULL`                                                | Null     | `\N`                          | -                                      |
| `TIMESTAMP`/`DATETIME`                                  | String   | `"1973-12-30 15:30:00.123456"` | Format: `yyyy-MM-dd HH:mm:ss.%06d`         |
| `DATE`                                                | String   | `"2000-01-01"`                 | Format: `yyyy-MM-dd`                       |
| `TIME`                                                | String   | `"23:59:59"`                   | Format: `yyyy-MM-dd`                         |
| `YEAR`                                                | Integer  | `1970`                         |  -                                     |
| `VARCHAR`/`JSON`/`TINYTEXT`/`MEDIUMTEXT`/`LONGTEXT`/`TEXT`/`CHAR` | String   | `"test"`                       | UTF-8 encoded                       |
| `VARBINARY`/`TINYBLOB`/`MEDIUMBLOB`/`LONGBLOB`/`BLOB`/`BINARY`  | String   | `"6Zi/5pav"` or `"e998bfe696af"`                  | Base64 or hex encoded                      |
| `BIT`                                                 | Integer  | `81`                           | -                                      |
| `DECIMAL`                                             | String   | `"129012.1230000"`             | -                                      |
| `ENUM`                                                | String   | `"a"`                          | -                                     |
| `SET`                                                 | String   | `"a,b"`                        | -                                     |
