# Parquet data conversion mapping for serverless export

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-export.md`
- Source Title: `Export Data from TiDB Cloud Serverless`
- Source Heading Path: `Export Data from TiDB Cloud Serverless > Export options > Data conversion`
- Source Line Ranges: `127-170`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `export`, `parquet`, `data-conversion`, `type-mapping`, `schema`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0827_58466b93b3`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-export.md#data-conversion`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `71e80aadccf74f273bb279809fb7f7e9ab41cd727cfeb1a0ead9b48a4379e3dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-export#data-conversion
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-export.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Cloud Serverless to Parquet data type conversion mapping for exported data.
- Retrieval Keywords: TiDB Cloud Serverless Parquet type mapping, Data conversion, VARCHAR BYTE_ARRAY String(UTF8), DECIMAL(1<=p<=9) INT32 DECIMAL(p,s), DECIMAL(10<=p<=18) INT64 DECIMAL(p,s), DECIMAL(p>=19) BYTE_ARRAY String(UTF8), TIMESTAMP(unit=MICROS,isAdjustedToUTC=false), UNSIGNED INT FIXED_LEN_BYTE_ARRAY(9) DECIMAL(20,0), BIGINT FIXED_LEN_BYTE_ARRAY(9) DECIMAL(20,0), UNSIGNED BIGINT BYTE_ARRAY String(UTF8), VECTOR BYTE_ARRAY String(UTF8), Parquet primitive type, Parquet logical type
- Follow-up Guidance: 
- Classification Note: This is reference content because it is a lookup table that defines exact Parquet primitive and logical type mappings for TiDB Cloud Serverless export types.

## Official Source Content

### Data conversion

When exporting data to the Parquet format, the data conversion between TiDB Cloud Serverless and Parquet is as follows:

| TiDB Cloud Serverless Type | Parquest primitive type | Parquet logical type                         |
|----------------------------|-------------------------|----------------------------------------------|
| VARCHAR                    | BYTE_ARRAY              | String(UTF8)                                 |
| TIME                       | BYTE_ARRAY              | String(UTF8)                                 |
| TINYTEXT                   | BYTE_ARRAY              | String(UTF8)                                 |
| MEDIUMTEXT                 | BYTE_ARRAY              | String(UTF8)                                 |
| TEXT                       | BYTE_ARRAY              | String(UTF8)                                 |
| LONGTEXT                   | BYTE_ARRAY              | String(UTF8)                                 |
| SET                        | BYTE_ARRAY              | String(UTF8)                                 |
| JSON                       | BYTE_ARRAY              | String(UTF8)                                 |
| DATE                       | BYTE_ARRAY              | String(UTF8)                                 |
| CHAR                       | BYTE_ARRAY              | String(UTF8)                                 |
| VECTOR                     | BYTE_ARRAY              | String(UTF8)                                 |
| DECIMAL(1<=p<=9)           | INT32                   | DECIMAL(p,s)                                 |
| DECIMAL(10<=p<=18)         | INT64                   | DECIMAL(p,s)                                 |
| DECIMAL(p>=19)             | BYTE_ARRAY              | String(UTF8)                                 |
| ENUM                       | BYTE_ARRAY              | String(UTF8)                                 |
| TIMESTAMP                  | INT64                   | TIMESTAMP(unit=MICROS,isAdjustedToUTC=false) |
| DATETIME                   | INT64                   | TIMESTAMP(unit=MICROS,isAdjustedToUTC=false) |
| YEAR                       | INT32                   | /                                            |
| TINYINT                    | INT32                   | /                                            |
| UNSIGNED TINYINT           | INT32                   | /                                            |
| SMALLINT                   | INT32                   | /                                            |
| UNSIGNED SMALLINT          | INT32                   | /                                            |
| MEDIUMINT                  | INT32                   | /                                            |
| UNSIGNED MEDIUMINT         | INT32                   | /                                            |
| INT                        | INT32                   | /                                            |
| UNSIGNED INT               | FIXED_LEN_BYTE_ARRAY(9) | DECIMAL(20,0)                                |
| BIGINT                     | FIXED_LEN_BYTE_ARRAY(9) | DECIMAL(20,0)                                |
| UNSIGNED BIGINT            | BYTE_ARRAY              | String(UTF8)                                 |
| FLOAT                      | FLOAT                   | /                                            |
| DOUBLE                     | DOUBLE                  | /                                            |
| BLOB                       | BYTE_ARRAY              | /                                            |
| TINYBLOB                   | BYTE_ARRAY              | /                                            |
| MEDIUMBLOB                 | BYTE_ARRAY              | /                                            |
| LONGBLOB                   | BYTE_ARRAY              | /                                            |
| BINARY                     | BYTE_ARRAY              | /                                            |
| VARBINARY                  | BYTE_ARRAY              | /                                            |
| BIT                        | BYTE_ARRAY              | /                                            |
