# Storage sink file layout, metadata, and DDL schema files

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-cloud-storage.md`
- Source Title: `Replicate Data to Storage Services`
- Source Heading Path: `Replicate Data to Storage Services > Storage path structure > Data change records | Replicate Data to Storage Services > Storage path structure > Index files | Replicate Data to Storage Services > Storage path structure > Metadata | Replicate Data to Storage Services > Storage path structure > DDL events | Replicate Data to Storage Services > Storage path structure > DDL events at the table level | Replicate Data to Storage Services > Storage path structure > DDL events at the database level`
- Source Line Ranges: `155-313`
- Source Scope: `cloud`
- Primary Component: `ticdc`
- Related Components: `cloud`, `tidb`
- Topic Tags: `storage-paths`, `change-records`, `index-files`, `metadata`, `ddl-events`, `schema-files`, `table-version`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0776_b877541b7e`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-cloud-storage.md#data-change-records`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ddda8c2b9105519e87b7246066342bcc890c64af2cb1aea3b1be0a291c33858e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-cloud-storage#data-change-records
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-cloud-storage.md

## Retrieval Guidance

- Use When: Use this chunk when locating TiCDC storage sink path structure, file naming, metadata, index files, or schema JSON files for data change records and DDL events in cloud storage.
- Retrieval Keywords: {scheme}://{prefix}/{schema}/{table}/{table-version-separator}/{partition-separator}/{date-separator}/CDC{num}.{extension}, CDC.index, {protocol}://{prefix}/metadata, checkpoint-ts, schema_{table-version}_{hash}.json, data change records, index files, DDL events at the table level, DDL events at the database level, TableVersion, Query, TableColumns, TableColumnsTotal, date-separator, table version changes
- Follow-up Guidance: The source also defines the schema file JSON fields and points to the Data type section for how ColumnType, ColumnLength, ColumnPrecision, and ColumnScale are represented.
- Classification Note: This is reference content because it specifies exact storage paths, metadata JSON, index file behavior, and schema file formats used by the TiCDC storage sink.

## Official Source Content

### Data change records

Data change records are saved to the following path:

```shell
{scheme}://{prefix}/{schema}/{table}/{table-version-separator}/{partition-separator}/{date-separator}/CDC{num}.{extension}
```

- `scheme`: specifies the storage type, for example, `s3`, `gcs`, `azure`, or `file`.
- `prefix`: specifies the user-defined parent directory, for example, <code>s3://**bucket/bbb/ccc**</code>.
- `schema`: specifies the schema name, for example, <code>s3://bucket/bbb/ccc/**test**</code>.
- `table`: specifies the table name, for example, <code>s3://bucket/bbb/ccc/test/**table1**</code>.
- `table-version-separator`: specifies the separator that separates the path by the table version, for example, <code>s3://bucket/bbb/ccc/test/table1/**9999**</code>.
- `partition-separator`: specifies the separator that separates the path by the table partition, for example, <code>s3://bucket/bbb/ccc/test/table1/9999/**20**</code>.
- `date-separator`: classifies the files by the transaction commit date. The default value is `day`. Value options are:
    - `none`: no `date-separator`. For example, all files with `test.table1` version being `9999` are saved to `s3://bucket/bbb/ccc/test/table1/9999`.
    - `year`: the separator is the year of the transaction commit date, for example, <code>s3://bucket/bbb/ccc/test/table1/9999/**2022**</code>.
    - `month`: the separator is the year and month of the transaction commit date, for example, <code>s3://bucket/bbb/ccc/test/table1/9999/**2022-01**</code>.
    - `day`: the separator is the year, month, and day of the transaction commit date, for example, <code>s3://bucket/bbb/ccc/test/table1/9999/**2022-01-02**</code>.
- `num`: saves the serial number of the file that records the data change, for example, <code>s3://bucket/bbb/ccc/test/table1/9999/2022-01-02/CDC**000005**.csv</code>.
- `extension`: specifies the extension of the file. TiDB v6.5.0 supports the CSV and Canal-JSON formats.

> **Note:**
>
> The table version changes in the following scenarios:
>
> - The upstream TiDB performs a DDL operation on the table.
> - TiCDC schedules the table across nodes.
> - The changefeed to which the table belongs restarts.
> 
> Note that the change of the table version does not mean the change of the table schema. For example, adding a comment to a column does not cause the schema file content to change.
### Index files

An index file is used to prevent written data from being overwritten by mistake. It is stored in the same path as the data change records.

```shell
{scheme}://{prefix}/{schema}/{table}/{table-version-separator}/{partition-separator}/{date-separator}/meta/CDC.index
```

The index file records the largest file name used in the current directory. For example:

```
CDC000005.csv
```

In this example, the files `CDC000001.csv` through `CDC000004.csv` in this directory are occupied. When a table scheduling or node restart occurs in the TiCDC cluster, the new node reads the index file and determines if `CDC000005.csv` is occupied. If it is not occupied, the new node writes the file starting from `CDC000005.csv`. If it is occupied, it starts writing from `CDC000006.csv`, which prevents overwriting data written by other nodes.
### Metadata

Metadata is saved in the following path:

```shell
{protocol}://{prefix}/metadata
```

Metadata is a JSON-formatted file, for example:

```json
{
    "checkpoint-ts":433305438660591626
}
```

- `checkpoint-ts`: Transactions with `commit-ts` smaller than `checkpoint-ts` are written to the target storage in the downstream.
### DDL events
### DDL events at the table level

When a DDL event of an upstream table causes a table version change, TiCDC automatically does the following:

- Switches to a new path to write data change records. For example, when the version of `test.table1` changes to `441349361156227074`, TiCDC changes to the `s3://bucket/bbb/ccc/test/table1/441349361156227074/2022-01-02/` path to write data change records.
- Generates a schema file in the following path to store the table schema information:

    ```shell
    {scheme}://{prefix}/{schema}/{table}/meta/schema_{table-version}_{hash}.json
    ```

Taking the `schema_441349361156227074_3131721815.json` schema file as an example, the table schema information in this file is as follows:

```json
{
    "Table":"table1",
    "Schema":"test",
    "Version":1,
    "TableVersion":441349361156227074,
    "Query":"ALTER TABLE test.table1 ADD OfficeLocation blob(20)",
    "Type":5,
    "TableColumns":[
        {
            "ColumnName":"Id",
            "ColumnType":"INT",
            "ColumnNullable":"false",
            "ColumnIsPk":"true"
        },
        {
            "ColumnName":"LastName",
            "ColumnType":"CHAR",
            "ColumnLength":"20"
        },
        {
            "ColumnName":"FirstName",
            "ColumnType":"VARCHAR",
            "ColumnLength":"30"
        },
        {
            "ColumnName":"HireDate",
            "ColumnType":"DATETIME"
        },
        {
            "ColumnName":"OfficeLocation",
            "ColumnType":"BLOB",
            "ColumnLength":"20"
        }
    ],
    "TableColumnsTotal":"5"
}
```

- `Table`: Table name.
- `Schema`: Schema name.
- `Version`: Protocol version of the storage sink.
- `TableVersion`: Table version.
- `Query`: DDL statement.
- `Type`: DDL type.
- `TableColumns`: An array of one or more maps, each of which describes a column in the source table.
    - `ColumnName`: Column name.
    - `ColumnType`: Column type. For details, see [Data type](#data-type).
    - `ColumnLength`: Column length. For details, see [Data type](#data-type).
    - `ColumnPrecision`: Column precision. For details, see [Data type](#data-type).
    - `ColumnScale`: The number of digits following the decimal point (the scale). For details, see [Data type](#data-type).
    - `ColumnNullable`: The column can be NULL when the value of this option is `true`.
    - `ColumnIsPk`: The column is part of the primary key when the value of this option is `true`.
- `TableColumnsTotal`: The size of the `TableColumns` array.
### DDL events at the database level

When a database-level DDL event is performed in the upstream database, TiCDC automatically generates a schema file in the following path to store the database schema information:

```shell
{scheme}://{prefix}/{schema}/meta/schema_{table-version}_{hash}.json
```

Taking the `schema_441349361156227000_3131721815.json` schema file as an example, the database schema information in this file is as follows:

```json
{
  "Table": "",
  "Schema": "schema1",
  "Version": 1,
  "TableVersion": 441349361156227000,
  "Query": "CREATE DATABASE `schema1`",
  "Type": 1,
  "TableColumns": null,
  "TableColumnsTotal": 0
}
```
