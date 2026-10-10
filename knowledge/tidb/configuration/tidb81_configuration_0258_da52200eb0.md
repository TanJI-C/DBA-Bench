# Serverless export filtering formats and compression

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-export.md`
- Source Title: `Export Data from TiDB Cloud Serverless`
- Source Heading Path: `Export Data from TiDB Cloud Serverless > Export options | Export Data from TiDB Cloud Serverless > Export options > Data filtering | Export Data from TiDB Cloud Serverless > Export options > Data formats | Export Data from TiDB Cloud Serverless > Export options > Data compression`
- Source Line Ranges: `84-126`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `shared`
- Topic Tags: `export-options`, `data-filtering`, `sql-statements`, `table-filters`, `csv`, `sql-format`, `parquet`, `compression`, `gzip`, `snappy`, `zstd`, `naming-conventions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0258_da52200eb0`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-export.md#export-options`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `58628f77d3da4d3262fa4fcc43ae279889f009238fb463cd0513641fc771e017`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-export#export-options
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-export.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Cloud Serverless export filtering methods, supported export formats, file naming conventions, or compression options for SQL, CSV, and Parquet exports.
- Retrieval Keywords: Export options, Data filtering, TiDB Cloud console selected databases and tables, TiDB Cloud CLI SQL statements, table filters, Data formats, SQL, CSV, Parquet, delimiter, separator, header, null-value, default delimiter is '"', default separator is ',', default value is true, default value is \N, {database}-schema-create.sql, {database}.{table}-schema.sql, {database}.{table}.{0001}.{csv|parquet|sql}, compression-type, Data compression, gzip default, snappy, zstd, none, Parquet zstd default
- Follow-up Guidance: The source distinguishes console-based filtering by selected databases and tables from CLI-based filtering with SQL statements and table filters, and it lists different default compression algorithms for CSV or SQL versus Parquet.
- Classification Note: This is classified as configuration for the cloud component because the content defines export option settings, including filtering behavior, format parameters, naming rules, and compression choices.

## Official Source Content

## Export options
### Data filtering

- TiDB Cloud console supports exporting data with the selected databases and tables.
- TiDB Cloud CLI supports exporting data with SQL statements and [table filters](https://docs.pingcap.com/tidb/stable/table-filter).
### Data formats

You can export data in the following formats:

- `SQL`: export data in SQL format.
- `CSV`: export data in CSV format. You can specify the following options:
    - `delimiter`: specify the delimiter used in the exported data. The default delimiter is `"`.
    - `separator`: specify the character used to separate fields in the exported data. The default separator is `,`.
    - `header`: specify whether to include a header row in the exported data. The default value is `true`.
    - `null-value`: specify the string that represents a NULL value in the exported data. The default value is `\N`.
- `Parquet`: export data in Parquet format.

The schema and data are exported according to the following naming conventions:

| Item            | Not compressed                                        | Compressed                                                                                                          |
|-----------------|-------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Database schema | {database}-schema-create.sql                          | {database}-schema-create.sql.{compression-type}                                                                     |
| Table schema    | {database}.{table}-schema.sql                         | {database}.{table}-schema.sql.{compression-type}                                                                    |
| Data            | {database}.{table}.{0001}.{csv&#124;parquet&#124;sql} | {database}.{table}.{0001}.{csv&#124;sql}.{compression-type}<br/>{database}.{table}.{0001}.{compression-type}.parquet |
### Data compression

You can compress the exported CSV and SQL data using the following algorithms:

- `gzip` (default): compress the exported data with `gzip`.
- `snappy`: compress the exported data with `snappy`.
- `zstd`: compress the exported data with `zstd`.
- `none`: do not compress the exported `data`.

You can compress the exported Parquet data using the following algorithms:

- `zstd` (default): compress the Parquet file with `zstd`.
- `gzip`: compress the Parquet file with `gzip`.
- `snappy`: compress the Parquet file with `snappy`.
- `none`: do not compress the Parquet file.
