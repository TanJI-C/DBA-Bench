# Supported Parquet data types and troubleshooting for Serverless import

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-parquet-files-serverless.md`
- Source Title: `Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless`
- Source Heading Path: `Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Supported data types | Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Troubleshooting | Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Troubleshooting > Resolve warnings during data import | Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Troubleshooting > Zero rows in the imported tables`
- Source Line Ranges: `318-349`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `sql`
- Topic Tags: `supported-data-types`, `parquet`, `type-mapping`, `troubleshooting`, `warnings`, `zero-rows`, `naming-conventions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0801_144d7d7a4a`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-parquet-files-serverless.md#supported-data-types`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `564571934c720281fcc7d25feeb1e555a2aadd9600058e265df76c844843a1b5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files-serverless#supported-data-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-parquet-files-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the supported Parquet-to-TiDB type mappings for TiDB Cloud Serverless or troubleshooting import warnings and completed imports with zero rows.
- Retrieval Keywords: Supported data types, Parquet Primitive Type, Parquet Logical Type, Types in TiDB or MySQL, DOUBLE, FIXED_LEN_BYTE_ARRAY, DECIMAL(p,s), INT32, INT64, TIMESTAMP_MICROS, BYTE_ARRAY, STRING, SMALLINT, TINYINT, Resolve warnings during data import, can't find the corresponding source files, Naming Conventions for Data Import, Advanced Settings, Zero rows in the imported tables, Bucket URI, Completed
- Follow-up Guidance: If you see `can't find the corresponding source files` or imported tables have zero rows, the content says to provide the correct source file, rename it according to Naming Conventions for Data Import, or use Advanced Settings, and then import the data again.
- Classification Note: The official content is classified as reference because it provides a supported data type mapping table and troubleshooting guidance for warnings and zero-row import outcomes.

## Official Source Content

## Supported data types

The following table lists the supported Parquet data types that can be imported to TiDB Cloud Serverless.

| Parquet Primitive Type | Parquet Logical Type | Types in TiDB or MySQL |
|---|---|---|
| DOUBLE | DOUBLE | DOUBLE<br />FLOAT |
| FIXED_LEN_BYTE_ARRAY(9) | DECIMAL(20,0) | BIGINT UNSIGNED |
| FIXED_LEN_BYTE_ARRAY(N) | DECIMAL(p,s) | DECIMAL<br />NUMERIC |
| INT32 | DECIMAL(p,s) | DECIMAL<br />NUMERIC |
| INT32 | N/A | INT<br />MEDIUMINT<br />YEAR |
| INT64 | DECIMAL(p,s) | DECIMAL<br />NUMERIC |
| INT64 | N/A | BIGINT<br />INT UNSIGNED<br />MEDIUMINT UNSIGNED |
| INT64 | TIMESTAMP_MICROS | DATETIME<br />TIMESTAMP |
| BYTE_ARRAY | N/A | BINARY<br />BIT<br />BLOB<br />CHAR<br />LINESTRING<br />LONGBLOB<br />MEDIUMBLOB<br />MULTILINESTRING<br />TINYBLOB<br />VARBINARY |
| BYTE_ARRAY | STRING | ENUM<br />DATE<br />DECIMAL<br />GEOMETRY<br />GEOMETRYCOLLECTION<br />JSON<br />LONGTEXT<br />MEDIUMTEXT<br />MULTIPOINT<br />MULTIPOLYGON<br />NUMERIC<br />POINT<br />POLYGON<br />SET<br />TEXT<br />TIME<br />TINYTEXT<br />VARCHAR |
| SMALLINT | N/A | INT32 |
| SMALLINT UNSIGNED | N/A | INT32 |
| TINYINT | N/A | INT32 |
| TINYINT UNSIGNED | N/A | INT32 |
## Troubleshooting
### Resolve warnings during data import

After clicking **Start Import**, if you see a warning message such as `can't find the corresponding source files`, resolve this by providing the correct source file, renaming the existing one according to [Naming Conventions for Data Import](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import), or using **Advanced Settings** to make changes.

After resolving these issues, you need to import the data again.
### Zero rows in the imported tables

After the import progress shows **Completed**, check the imported tables. If the number of rows is zero, it means no data files matched the Bucket URI that you entered. In this case, resolve this issue by providing the correct source file, renaming the existing one according to [Naming Conventions for Data Import](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import), or using **Advanced Settings** to make changes. After that, import those tables again.
