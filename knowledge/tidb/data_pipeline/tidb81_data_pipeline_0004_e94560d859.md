# Bulk import and migration tools for large data loads

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-insert-data.md`
- Source Title: `Insert Data`
- Source Heading Path: `Insert Data > Bulk-Insert`
- Source Line Ranges: `231-254`
- Source Scope: `all`
- Primary Component: `shared`
- Related Components: `dumpling`, `lightning`, `dm`, `br`, `cloud`
- Topic Tags: `bulk-insert`, `data-import`, `data-export`, `replication`, `backup`, `restore`, `migration`, `csv`, `parquet`, `s3`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0004_e94560d859`
- Source ID: `tidb-docs-8.1:develop/dev-guide-insert-data.md#bulk-insert`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `af670646ba67cf7b785de427a896cc1b7e8ce73d26fbc0379f337bfb0e3f032a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data#bulk-insert
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-insert-data.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants official guidance on bulk-insert alternatives to INSERT statements for large data loads, migration, replication, or backup and restore into TiDB.
- Retrieval Keywords: Bulk-Insert, Dumpling, TiDB Lightning, TiDB Data Migration, DM, Backup & Restore (BR), Create Import, TiDB Cloud console, CSV, Parquet, Amazon S3, Amazon Aurora, bulk import large amount of data
- Follow-up Guidance: It identifies tools for data export, data import, data replication, and data backup and restore, including TiDB Cloud import and backup pages.
- Classification Note: This is data_pipeline content because it categorizes official bulk data movement tools and states that INSERT is not the best way for quickly importing a large amount of data.

## Official Source Content

## Bulk-Insert

If you need to quickly import a large amount of data into a TiDB cluster, it is recommended that you use a range of tools provided by **PingCAP** for data migration. Using the `INSERT` statement is not the best way, because it is not efficient and requires to handle exceptions and other issues on your own.

The following are the recommended tools for bulk-insert:

- Data export: [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview). You can export MySQL or TiDB data to local or Amazon S3.

- Data import: [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview). You can import **Dumpling** exported data, a **CSV** file, or [Migrate Data from Amazon Aurora to TiDB](https://docs.pingcap.com/tidb/stable/migrate-aurora-to-tidb). It also supports reading data from a local disk or Amazon S3 cloud disk.
- Data replication: [TiDB Data Migration](https://docs.pingcap.com/tidb/stable/dm/dm-overview). You can replicate MySQL, MariaDB, and Amazon Aurora databases to TiDB. It also supports merging and migrating the sharded instances and tables from the source databases.
- Data backup and restore: [Backup & Restore (BR)](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview). Compared to **Dumpling**, **BR** is more suitable for **_big data_** scenario.

- Data import: [Create Import](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-sample-data) page in the [TiDB Cloud console](https://tidbcloud.com/). You can upload local CSV files ({{{ .starter }}} only), and import **Dumpling** logical dumps (schema and data), **CSV**, or **Parquet** files stored in Cloud Storage. For details, see the [Import CSV Files into {{{ .starter }}}](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files-serverless) or [Import CSV Files into TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files).
- Data replication: [TiDB Data Migration](https://docs.pingcap.com/tidb/stable/dm-overview). You can replicate MySQL, MariaDB, and Amazon Aurora databases to TiDB. It also supports merging and migrating the sharded instances and tables from the source databases.
- Data backup and restore: [Backup](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore) page in the TiDB Cloud console. Compared to **Dumpling**, backup and restore is more suitable for **_big data_** scenario.
