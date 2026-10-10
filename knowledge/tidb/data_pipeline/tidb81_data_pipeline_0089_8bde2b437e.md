# Import snapshot files overview and naming requirement

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-snapshot-files.md`
- Source Title: `Import Snapshot Files into TiDB Cloud`
- Source Heading Path: `Import Snapshot Files into TiDB Cloud`
- Source Line Ranges: `5-10`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `snapshot-import`, `aurora`, `rds`, `mysql`, `parquet`, `cloud-storage`, `naming-conventions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0089_8bde2b437e`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-snapshot-files.md#import-snapshot-files-into-tidb-cloud`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b14fd34b62c43fe28a4d8b5b5f0975570835166f783cd2c079c2a19229e8c754`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-snapshot-files#import-snapshot-files-into-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-snapshot-files.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about importing Amazon Aurora or RDS for MySQL snapshot files into TiDB Cloud and the required naming of `.parquet` files in `{db_name}.{table_name}/` folders.
- Retrieval Keywords: Import Snapshot Files into TiDB Cloud, Amazon Aurora snapshot files, RDS for MySQL snapshot files, TiDB Cloud, `.parquet` suffix, {db_name}.{table_name}/ folder, naming convention, Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated
- Follow-up Guidance: The source states that the process of importing snapshot files is similar to importing Parquet files and points to the Parquet import documentation for more information.
- Classification Note: This is classified under data_pipeline for the cloud component because the content describes importing snapshot data files into TiDB Cloud and the file naming requirement for that import process.

## Official Source Content

# Import Snapshot Files into TiDB Cloud

You can import Amazon Aurora or RDS for MySQL snapshot files into TiDB Cloud. Note that all source data files with the `.parquet` suffix in the `{db_name}.{table_name}/` folder must conform to the [naming convention](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import).

The process of importing snapshot files is similar to that of importing Parquet files. For more information, see [Import Apache Parquet Files from Cloud Storage into TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files).
