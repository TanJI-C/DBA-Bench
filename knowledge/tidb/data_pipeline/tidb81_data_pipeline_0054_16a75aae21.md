# BR backup restore and Lightning Dumpling data transfer updates

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0-rc.md`
- Source Title: `TiDB 5.0 RC Release Notes`
- Source Heading Path: `TiDB 5.0 RC Release Notes > Backup and restore | TiDB 5.0 RC Release Notes > Data import and export`
- Source Line Ranges: `159-170`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `lightning`, `dumpling`
- Topic Tags: `backup`, `restore`, `s3`, `gcs`, `import`, `export`, `aurora-snapshot`, `aws`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0054_16a75aae21`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0-rc.md#backup-and-restore`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a0100a2f900157153a3f240cb3190f801825a54c7a296453353d22fd3942875a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0-rc#backup-and-restore
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0-rc.md

## Retrieval Guidance

- Use When: Use this chunk when searching for BR, Lightning, or Dumpling support for AWS S3, Google Cloud GCS, Aurora snapshot import, or experimental export to Amazon S3 cloud storage.
- Retrieval Keywords: Backup and Restore tool BR, backing up data to AWS S3, Google Cloud GCS, restoring data from AWS S3, restoring data from Google Cloud GCS, TiDB Lightning, importing Aurora snapshot data, AWS S3 storage, Dumpling, exporting data from TiDB/MySQL to AWS S3 storage, experimental, backup and restore storages, export data to Amazon S3 cloud storage
- Follow-up Guidance: The source also includes a TPC-C import performance result for 1 TiB of data into DBaaS T1.standard, improving from 254 GiB/h to 366 GiB/h.
- Classification Note: This is classified as data_pipeline because the content covers backup, restore, import, and export capabilities across BR, Lightning, and Dumpling.

## Official Source Content

## Backup and restore

+ The Backup & Restore tool (BR) supports backing up data to AWS S3 and Google Cloud GCS. ([User document](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages))
+ The Backup & Restore tool (BR) supports restoring data from AWS S3 and Google Cloud GCS to TiDB. ([User document](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages))
+ Related issue: [#89](https://github.com/pingcap/br/issues/89)
## Data import and export

+ TiDB Lightning supports importing Aurora snapshot data from AWS S3 storage to TiDB. (Related issue: [#266](https://github.com/pingcap/tidb-lightning/issues/266))
+ In the TPC-C test of importing 1 TiB of data into DBaaS T1.standard, the performance improves by 40%, from 254 GiB/h to 366 GiB/h.
+ Dumpling supports exporting data from TiDB/MySQL to AWS S3 storage (experimental) (Related issue: [#8](https://github.com/pingcap/dumpling/issues/8), [User document](https://docs.pingcap.com/tidb/stable/dumpling-overview#export-data-to-amazon-s3-cloud-storage))
