# Data Migration runtime errors and recovery actions

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting.md`
- Source Title: `Precheck Errors, Migration Errors, and Alerts for Data Migration`
- Source Heading Path: `Precheck Errors, Migration Errors, and Alerts for Data Migration > Migration errors and solutions | Precheck Errors, Migration Errors, and Alerts for Data Migration > Migration errors and solutions > Error message: "The required binary log for migration no longer exists on the source database. Please make sure binary log files are kept for long enough time for migration to succeed." | Precheck Errors, Migration Errors, and Alerts for Data Migration > Migration errors and solutions > Error message: "Failed to connect to the source database using given parameters. Please make sure the source database is up and can be connected using the given parameters." | Precheck Errors, Migration Errors, and Alerts for Data Migration > Migration errors and solutions > The migration task is interrupted and contains the error "driver: bad connection" or "invalid connection" | Precheck Errors, Migration Errors, and Alerts for Data Migration > Migration errors and solutions > Error message: "Failed to connect to the TiDB cluster using the given user and password. Please make sure TiDB Cluster is up and can be connected to using the given user and password." | Precheck Errors, Migration Errors, and Alerts for Data Migration > Migration errors and solutions > Error message: "TiDB cluster storage is not enough. Please increase the node storage of TiKV." | Precheck Errors, Migration Errors, and Alerts for Data Migration > Migration errors and solutions > Error message: "Failed to connect to the source database. Please check whether the database is available or the maximum connections have been reached." | Precheck Errors, Migration Errors, and Alerts for Data Migration > Migration errors and solutions > Error message: "Error 1273: Unsupported collation when new collation is enabled: 'utf8mb4_0900_ai_ci'"`
- Source Line Ranges: `61-96`
- Source Scope: `cloud`
- Primary Component: `dm`
- Related Components: `cloud`, `tidb`, `tikv`, `sql`
- Topic Tags: `migration-errors`, `binlog-retention`, `source-connectivity`, `downstream-connectivity`, `restart`, `resume`, `storage-capacity`, `collation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0092_080c5bac41`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting.md#migration-errors-and-solutions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b87632d2e336847fb895bad166eb0d517c8c32900e3430ccfce3b7e04b5ed268`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting#migration-errors-and-solutions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting.md

## Retrieval Guidance

- Use When: Use this when a migration job details page shows source-connection failures, downstream connection failures, missing binary logs, storage shortage, or unsupported collation errors.
- Retrieval Keywords: Migration errors and solutions, Migration Job Details page, The required binary log for migration no longer exists on the source database, Failed to connect to the source database using given parameters, driver: bad connection, invalid connection, Failed to connect to the TiDB cluster using the given user and password, TiDB cluster storage is not enough. Please increase the node storage of TiKV., Failed to connect to the source database. Please check whether the database is available or the maximum connections have been reached., Error 1273: Unsupported collation when new collation is enabled: 'utf8mb4_0900_ai_ci', Restart, expire_logs_days
- Follow-up Guidance: After confirming the database or cluster is available, the task can be recovered or resumed by clicking Restart where the document states it.
- Classification Note: This chunk classifies as diagnosis because it maps migration error messages to their corresponding recovery guidance.

## Official Source Content

## Migration errors and solutions

This section describes the problems and solutions you might encounter during the migration. These error messages are shown on the **Migration Job Details** page.
### Error message: "The required binary log for migration no longer exists on the source database. Please make sure binary log files are kept for long enough time for migration to succeed."

This error means that the binlogs to be migrated have been cleaned up and can only be restored by creating a new task.

Ensure that the binlogs required for incremental migration exist. It is recommended to configure `expire_logs_days` to extend the duration of binlogs. Do not use `purge binary log` to clean up binlogs if it's needed by some migration job.
### Error message: "Failed to connect to the source database using given parameters. Please make sure the source database is up and can be connected using the given parameters."

This error means that the connection to the source database failed. Check whether the source database is started and can be connected to using the specified parameters. After confirming that the source database is available, you can try to recover the task by clicking **Restart**.
### The migration task is interrupted and contains the error "driver: bad connection" or "invalid connection"

This error means that the connection to the downstream TiDB cluster failed. Check whether the downstream TiDB cluster is in a normal state (including `Available` and `Modifying`) and can be connected with the username and password specified by the job. After confirming that the downstream TiDB cluster is available, you can try to resume the task by clicking **Restart**.
### Error message: "Failed to connect to the TiDB cluster using the given user and password. Please make sure TiDB Cluster is up and can be connected to using the given user and password."

Failed to connect to the TiDB cluster. It is recommended to check whether the TiDB cluster is in a normal state (including `Available` and `Modifying`). You can connect with the username and password specified by the job. After confirming that the TiDB cluster is available, you can try to resume the task by clicking **Restart**.
### Error message: "TiDB cluster storage is not enough. Please increase the node storage of TiKV."

The TiDB cluster storage is running low. It is recommended to [increase the TiKV node storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/scale-tidb-cluster#change-storage) and then resume the task by clicking **Restart**.
### Error message: "Failed to connect to the source database. Please check whether the database is available or the maximum connections have been reached."

Failed to connect to the source database. It is recommended to check whether the source database is started, the number of database connections has not reached the upper limit, and you can connect using the parameters specified by the job. After confirming that the source database is available, you can try to resume the job by clicking **Restart**.
### Error message: "Error 1273: Unsupported collation when new collation is enabled: 'utf8mb4_0900_ai_ci'"

Failed to create a schema in the downstream TiDB cluster. This error means that the collation used by the upstream MySQL is not supported by the TiDB cluster.

To resolve this issue, you can create a schema in the TiDB cluster based on a [supported collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation#character-sets-and-collations-supported-by-tidb), and then resume the task by clicking **Restart**.
