# TiCDC Canal-JSON field type descriptions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-canal-json.md`
- Source Title: `TiCDC Canal-JSON Protocol`
- Source Heading Path: `TiCDC Canal-JSON Protocol > Field descriptions | TiCDC Canal-JSON Protocol > Field descriptions > MySQL Type field | TiCDC Canal-JSON Protocol > Field descriptions > SQL Type field`
- Source Line Ranges: `177-216`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `shared`, `tidb`
- Topic Tags: `field-descriptions`, `mysqltype`, `sqltype`, `jdbc-types`, `data-types`, `type-mapping`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0757_25e03f99d2`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-canal-json.md#field-descriptions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1ba28719eba1b661e663fa151f40dd10436f991e4a7dba7efd9a076b0fd06fff`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-canal-json#field-descriptions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-canal-json.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how Canal-JSON records column types in `mysqlType` and `sqlType`, including the MySQL Type to Java SQL Type Code mapping.
- Retrieval Keywords: Field descriptions, mysqlType, sqlType, MySQL Type field, SQL Type field, Java SQL Type Code, JDBC, type mapping, Boolean -6, Float 7, Double 8, Decimal 3, Varchar 12, Datetime 93, Timestamp 93, Time 92, JSON 12
- Follow-up Guidance: It points to TiDB Data Types for more information about the MySQL type strings stored in `mysqlType`.
- Classification Note: The classification is reference because the content is a field-level type mapping reference for Canal-JSON metadata.

## Official Source Content

## Field descriptions

The Canal-JSON format records the corresponding data type in the `mysqlType` field and the `sqlType` field.
### MySQL Type field

In the `mysqlType` field, the Canal-JSON format records the string of MySQL Type in each column. For more information, see [TiDB Data Types](https://docs.pingcap.com/tidb/stable/data-type-overview).
### SQL Type field

In the `sqlType` field, the Canal-JSON format records Java SQL Type of each column, which is the data type corresponding to the data in JDBC. Its value can be calculated by MySQL Type and the specific data value. The mapping is as follows:

| MySQL Type | Java SQL Type Code |
| :----------| :----------------- |
| Boolean    | -6                 |
| Float      | 7                  |
| Double     | 8                  |
| Decimal    | 3                  |
| Char       | 1                  |
| Varchar    | 12                 |
| Binary     | 2004               |
| Varbinary  | 2004               |
| Tinytext   | 2005               |
| Text       | 2005               |
| Mediumtext | 2005               |
| Longtext   | 2005               |
| Tinyblob   | 2004               |
| Blob       | 2004               |
| Mediumblob | 2004               |
| Longblob   | 2004               |
| Date       | 91                 |
| Datetime   | 93                 |
| Timestamp  | 93                 |
| Time       | 92                 |
| Year       | 12                 |
| Enum       | 4                  |
| Set        | -7                 |
| Bit        | -7                 |
| JSON       | 12                 |
