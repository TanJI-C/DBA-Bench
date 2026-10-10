# Troubleshooting CSV import warnings and zero-row results

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-csv-files-serverless.md`
- Source Title: `Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless`
- Source Heading Path: `Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Troubleshooting | Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Troubleshooting > Resolve warnings during data import | Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless > Troubleshooting > Zero rows in the imported tables`
- Source Line Ranges: `307-317`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `troubleshooting`, `warnings`, `source-files`, `naming-conventions`, `advanced-settings`, `zero-rows`, `reimport`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0084_b391a278b4`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-csv-files-serverless.md#troubleshooting`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `01eaacceb17e7c90b32f4b700ad2bbb99a4bd6491ccbf54cdedb86a27d3caef1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files-serverless#troubleshooting
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-csv-files-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiDB Cloud Serverless CSV imports that show a warning like `can't find the corresponding source files` or complete with zero rows in the imported tables.
- Retrieval Keywords: Troubleshooting, Resolve warnings during data import, can't find the corresponding source files, Zero rows in the imported tables, Naming Conventions for Data Import, Advanced Settings, source file, Bucket URI, Completed, import the data again, import those tables again
- Follow-up Guidance: After correcting the source file, renaming it according to Naming Conventions for Data Import, or using Advanced Settings, the content says to import the data again or import those tables again.
- Classification Note: This is classified as a diagnosis chunk because the content explains warning symptoms and zero-row results and ties them to source file matching, naming conventions, and Bucket URI issues.

## Official Source Content

## Troubleshooting
### Resolve warnings during data import

After clicking **Start Import**, if you see a warning message such as `can't find the corresponding source files`, resolve this by providing the correct source file, renaming the existing one according to [Naming Conventions for Data Import](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import), or using **Advanced Settings** to make changes.

After resolving these issues, you need to import the data again.
### Zero rows in the imported tables

After the import progress shows **Completed**, check the imported tables. If the number of rows is zero, it means no data files matched the Bucket URI that you entered. In this case, resolve this issue by providing the correct source file, renaming the existing one according to [Naming Conventions for Data Import](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import), or using **Advanced Settings** to make changes. After that, import those tables again.
