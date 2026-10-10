# Troubleshooting import warnings and zero-row results

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-parquet-files.md`
- Source Title: `Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated`
- Source Heading Path: `Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated > Troubleshooting | Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated > Troubleshooting > Resolve warnings during data import | Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated > Troubleshooting > Zero rows in the imported tables`
- Source Line Ranges: `260-270`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `troubleshooting`, `warnings`, `source-files`, `bucket-uri`, `naming-conventions`, `reimport`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0086_50ac5535fd`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-parquet-files.md#troubleshooting`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `01eaacceb17e7c90b32f4b700ad2bbb99a4bd6491ccbf54cdedb86a27d3caef1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files#troubleshooting
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-parquet-files.md

## Retrieval Guidance

- Use When: Use this chunk when an Apache Parquet import in TiDB Cloud shows the warning `can't find the corresponding source files` or completes with zero rows in the imported tables.
- Retrieval Keywords: Troubleshooting, Resolve warnings during data import, can't find the corresponding source files, Zero rows in the imported tables, Completed, Bucket URI, Naming Conventions for Data Import, Advanced Settings, Start Import, import the data again, import those tables again
- Follow-up Guidance: The content says to provide the correct source file, rename the existing one according to Naming Conventions for Data Import, or use Advanced Settings to make changes, and then import again.
- Classification Note: This is diagnosis content because it describes warning and zero-row symptoms during import and the documented causes related to source files, naming conventions, and Bucket URI matching.

## Official Source Content

## Troubleshooting
### Resolve warnings during data import

After clicking **Start Import**, if you see a warning message such as `can't find the corresponding source files`, resolve this by providing the correct source file, renaming the existing one according to [Naming Conventions for Data Import](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import), or using **Advanced Settings** to make changes.

After resolving these issues, you need to import the data again.
### Zero rows in the imported tables

After the import progress shows **Completed**, check the imported tables. If the number of rows is zero, it means no data files matched the Bucket URI that you entered. In this case, resolve this issue by providing the correct source file, renaming the existing one according to [Naming Conventions for Data Import](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import), or using **Advanced Settings** to make changes. After that, import those tables again.
