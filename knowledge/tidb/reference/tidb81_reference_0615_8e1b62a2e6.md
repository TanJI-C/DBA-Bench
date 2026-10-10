# Import export and backup restore statements overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-overview.md`
- Source Title: `SQL Statement Overview`
- Source Heading Path: `SQL Statement Overview > Data import and export | SQL Statement Overview > Backup & restore`
- Source Line Ranges: `124-145`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `lightning`, `br`, `tidb`
- Topic Tags: `import`, `export`, `load-data`, `physical-import`, `backup`, `restore`, `flashback`, `recovery`, `show-jobs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0615_8e1b62a2e6`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-overview.md#data-import-and-export`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f8b239bb84de88a7a9124e9e83ca19a71f4c9aecb0f290aef30a39abf17ae79`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview#data-import-and-export
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user is looking for the SQL statement overview for data import, export, backup, restore, flashback, recovery, or job status display.
- Retrieval Keywords: Data import and export, Backup & restore, CANCEL IMPORT JOB, IMPORT INTO, Physical Import Mode, TiDB Lightning, LOAD DATA, Amazon S3, Google Cloud Storage, SHOW IMPORT JOB, BACKUP, FLASHBACK CLUSTER, FLASHBACK DATABASE, FLASHBACK TABLE, RECOVER TABLE, RESTORE, SHOW BACKUPS, SHOW RESTORES
- Follow-up Guidance: The overview distinguishes import job statements such as `CANCEL IMPORT JOB` and `SHOW IMPORT JOB` from backup and restore statements such as `BACKUP`, `RESTORE`, `SHOW BACKUPS`, and `SHOW RESTORES`.
- Classification Note: This chunk is a reference overview because it enumerates import/export and backup/restore SQL statements with brief descriptions.

## Official Source Content

## Data import and export

| SQL Statement | Description |
|---------------|-------------|
| [`CANCEL IMPORT JOB`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-cancel-import-job) | Cancels an ongoing import job. |
| [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) | Imports data into a table via the [Physical Import Mode](https://docs.pingcap.com/tidb/stable/tidb-lightning-physical-import-mode) of TiDB Lightning. |
| [`LOAD DATA`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data) | Loads data into a table from Amazon S3 or Google Cloud Storage. |
| [`SHOW IMPORT JOB`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-import-job) | Shows the status of an import job. |
## Backup & restore

| SQL Statement | Description |
|---------------|-------------|
| [`BACKUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-backup) | Performs a distributed backup of the TiDB cluster. |
| [`FLASHBACK CLUSTER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster) | Restores the cluster to a specific snapshot. |
| [`FLASHBACK DATABASE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-database) | Restores a database and its data deleted by the `DROP` statement. |
| [`FLASHBACK TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-table) | Restore the tables and data dropped by the `DROP` or `TRUNCATE` operation. |
| [`RECOVER TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-recover-table) | Recovers a deleted table and the data on it. |
| [`RESTORE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-restore) | Restores a database from a backup. |
| [`SHOW BACKUPS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-backups) | Shows backup tasks. |
| [`SHOW RESTORES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-backups) | Shows restore tasks. |
