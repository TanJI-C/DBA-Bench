# Backup, restore, and migration feature updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.3.0.md`
- Source Title: `TiDB 6.3.0 Release Notes`
- Source Heading Path: `TiDB 6.3.0 Release Notes > New features > Backup and restore | TiDB 6.3.0 Release Notes > New features > Data migration`
- Source Line Ranges: `176-193`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `lightning`, `dm`
- Topic Tags: `pitr`, `gcs`, `azure-blob`, `s3-object-lock`, `parquet`, `hive`, `safe-mode-duration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0339_f6f1da7ada`
- Source ID: `tidb-docs-8.1:releases/release-6.3.0.md#backup-and-restore`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cbf5552ec2cce384720909d3a5d0976dc8c745f2a55e215dd3614cb1458d82c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.3.0#backup-and-restore
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.3.0 backup, restore, or migration updates involving PITR storage support, AWS S3 Object Lock, TiDB Lightning Parquet import, or the DM safe-mode-duration setting.
- Retrieval Keywords: TiDB 6.3.0 backup and restore, PITR GCS, PITR Azure Blob Storage, backup-and-restore-storages, BR AWS S3 Object Lock, S3 Object Lock, TiDB Lightning Parquet, Apache Hive Parquet import into TiDB, DM safe-mode-duration, task configuration file, automatic safe mode duration, default value is 60 seconds, "0s" error when DM tries to enter safe mode after an abnormal restart
- Follow-up Guidance: The content states that safe-mode-duration is a DM task configuration item with a default of 60 seconds, and setting it to "0s" causes an error when DM tries to enter safe mode after an abnormal restart.
- Classification Note: This is a release-note chunk for BR, TiDB Lightning, and DM feature updates across backup and restore plus data migration.

## Official Source Content

### Backup and restore

* PITR supports [GCS and Azure Blob Storage](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages) as backup storages @[joccau](https://github.com/joccau)

    If your TiDB cluster is deployed on Google Cloud or Azure, you can use the PITR feature after upgrading your cluster to v6.3.0.

* BR supports AWS S3 Object Lock [#13442](https://github.com/tikv/tikv/issues/13442) @[3pointer](https://github.com/3pointer)

    You can protect backup data on AWS from being tampered with or deleted by enabling [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html).
### Data migration

* TiDB Lightning supports [importing Parquet files exported by Apache Hive into TiDB](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-data-source#parquet) [#37536](https://github.com/pingcap/tidb/issues/37536) @[buchuitoudegou](https://github.com/buchuitoudegou)

* DM adds a new configuration item `safe-mode-duration` [#6224](https://github.com/pingcap/tiflow/issues/6224) @[okJiang](https://github.com/okJiang)

    This configuration item is added to the [task configuration file](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full). You can adjust the automatic safe mode duration after DM exits abnormally. The default value is 60 seconds. If `safe-mode-duration` is set to `"0s"`, an error is reported when DM tries to enter safe mode after an abnormal restart.
