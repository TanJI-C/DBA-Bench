# Supported Parquet to TiDB data types

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-parquet-files.md`
- Source Title: `Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated`
- Source Heading Path: `Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated > Supported data types`
- Source Line Ranges: `239-259`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `parquet`, `data-types`, `type-mapping`, `schema-compatibility`, `import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0802_7e104a158a`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-parquet-files.md#supported-data-types`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e01b6d6ad4186a4fb940312da5ba7aa208787e3a51738b5cca2e426de797a7ba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files#supported-data-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-parquet-files.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether a Parquet primitive type and logical type can be imported into TiDB Cloud and what TiDB or MySQL type mapping is supported.
- Retrieval Keywords: Supported data types, Parquet Primitive Type, Parquet Logical Type, Types in TiDB or MySQL, DOUBLE, FIXED_LEN_BYTE_ARRAY(9), DECIMAL(20,0), BIGINT UNSIGNED, FIXED_LEN_BYTE_ARRAY(N), DECIMAL(p,s), INT32, INT64, TIMESTAMP_MICROS, BYTE_ARRAY, STRING, BINARY, VARBINARY, JSON, VARCHAR, DATETIME, TIMESTAMP
- Follow-up Guidance: 
- Classification Note: This is reference content because it is a type-mapping table listing supported Parquet data types and their corresponding TiDB or MySQL types for import.

## Official Source Content

## Supported data types

The following table lists the supported Parquet data types that can be imported to TiDB Cloud.

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
