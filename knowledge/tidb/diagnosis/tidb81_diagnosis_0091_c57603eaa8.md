# Data Migration precheck errors and solutions

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting.md`
- Source Title: `Precheck Errors, Migration Errors, and Alerts for Data Migration`
- Source Heading Path: `Precheck Errors, Migration Errors, and Alerts for Data Migration | Precheck Errors, Migration Errors, and Alerts for Data Migration > Precheck errors and solutions | Precheck Errors, Migration Errors, and Alerts for Data Migration > Precheck errors and solutions > Error message: Check whether mysql server_id has been greater than 0 | Precheck Errors, Migration Errors, and Alerts for Data Migration > Precheck errors and solutions > Error message: Check whether mysql binlog is enabled | Precheck Errors, Migration Errors, and Alerts for Data Migration > Precheck errors and solutions > Error message: Check whether mysql binlog_format is ROW | Precheck Errors, Migration Errors, and Alerts for Data Migration > Precheck errors and solutions > Error message: Check whether mysql binlog_row_image is FULL | Precheck Errors, Migration Errors, and Alerts for Data Migration > Precheck errors and solutions > Error message: Check whether migrated dbs are in binlog_do_db/binlog_ignore_db | Precheck Errors, Migration Errors, and Alerts for Data Migration > Precheck errors and solutions > Error message: Check if connection concurrency exceeds database's maximum connection limit`
- Source Line Ranges: `5-60`
- Source Scope: `cloud`
- Primary Component: `dm`
- Related Components: `cloud`, `sql`, `tidb`
- Topic Tags: `precheck`, `source-database`, `binlog`, `server-id`, `binlog-format`, `binlog-row-image`, `database-filters`, `max-connections`, `connectivity`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0091_c57603eaa8`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting.md#precheck-errors-migration-errors-and-alerts-for-data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `da7e21c4db2420e393d06a7e0a34e50517a2244f93ffcac7c01834468e633788`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting#precheck-errors-migration-errors-and-alerts-for-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting.md

## Retrieval Guidance

- Use When: Use this when a Data Migration precheck page shows errors about source MySQL settings, binlog requirements, database filters, or connection concurrency limits.
- Retrieval Keywords: Precheck errors and solutions, Precheck page, Check whether mysql server_id has been greater than 0, Check whether mysql binlog is enabled, Check whether mysql binlog_format is ROW, Check whether mysql binlog_row_image is FULL, Check whether migrated dbs are in binlog_do_db/binlog_ignore_db, Check if connection concurrency exceeds database's maximum connection limit, server_id, binlog_format, binlog_row_image, binlog_do_db, binlog_ignore_db, max_connections
- Follow-up Guidance: Review the error message and match it to the upstream database type or TiDB Cloud cluster guidance shown in the precheck section.
- Classification Note: This chunk classifies as diagnosis because it explains how to resolve specific precheck errors during data migration.

## Official Source Content

# Precheck Errors, Migration Errors, and Alerts for Data Migration

This document describes how to resolve precheck errors, troubleshoot migration errors, and subscribe to alerts when you [use Data Migration to migrate data](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration). 
## Precheck errors and solutions

This section describes the precheck errors and corresponding solutions during data migration. These errors are shown on the **Precheck** page when you [migrate data using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration).

The solutions vary depending on your upstream database.
### Error message: Check whether mysql server_id has been greater than 0

- Amazon Aurora MySQL or Amazon RDS: `server_id` is configured by default. You do not need to configure it. Make sure you are using Amazon Aurora MySQL writer instances to support both full and incremental data migration.
- MySQL: to configure `server_id` for MySQL, see [Setting the Replication Source Configuration](https://dev.mysql.com/doc/refman/8.0/en/replication-howto-masterbaseconfig.html).
### Error message: Check whether mysql binlog is enabled

- Amazon Aurora MySQL: see [How do I turn on binary logging for my Amazon Aurora MySQL-Compatible cluster](https://aws.amazon.com/premiumsupport/knowledge-center/enable-binary-logging-aurora/?nc1=h_ls). Make sure you are using Amazon Aurora MySQL writer instances to support both full and incremental data migration.
- Amazon RDS: see [Configuring MySQL binary logging](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.MySQL.BinaryFormat.html).
- Google Cloud SQL for MySQL: Google enables binary logging through point-in-time recovery for MySQL master databases. See [Enable point-in-time recovery](https://cloud.google.com/sql/docs/mysql/backup-recovery/pitr#enablingpitr).
- MySQL: see [Setting the Replication Source Configuration](https://dev.mysql.com/doc/refman/8.0/en/replication-howto-masterbaseconfig.html).
### Error message: Check whether mysql binlog_format is ROW

- Amazon Aurora MySQL: see [How do I turn on binary logging for my Amazon Aurora MySQL-Compatible cluster](https://aws.amazon.com/premiumsupport/knowledge-center/enable-binary-logging-aurora/?nc1=h_ls). Make sure you are using Amazon Aurora MySQL writer instances to support both full and incremental data migration.
- Amazon RDS: see [Configuring MySQL binary logging](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.MySQL.BinaryFormat.html).
- MySQL: execute `set global binlog_format=ROW;`. See [Setting The Binary Log Format](https://dev.mysql.com/doc/refman/8.0/en/binary-log-setting.html).
### Error message: Check whether mysql binlog_row_image is FULL

- Amazon Aurora MySQL: `binlog_row_image` is not configurable. This precheck item does not fail for it. Make sure you are using Amazon Aurora MySQL writer instances to support both full and incremental data migration.
- Amazon RDS: the process is similar to setting the `binlog_format` parameter. The only difference is that the parameter you need to change is `binlog_row_image` instead of `binlog_format`. See [Configuring MySQL binary logging](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.MySQL.BinaryFormat.html).
- MySQL: `set global binlog_row_image = FULL;`. See [Binary Logging Options and Variables](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_binlog_row_image).
### Error message: Check whether migrated dbs are in binlog_do_db/binlog_ignore_db

Make sure that binlog has been enabled in the upstream database. See [Check whether mysql binlog is enabled](#error-message-check-whether-mysql-binlog-is-enabled). After that, resolve the issue according to the message you get:

- If the message is similar to `These dbs xxx are not in binlog_do_db xxx`, make sure all the databases that you want to migrate are in the list. See [--binlog-do-db=db_name](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#option_mysqld_binlog-do-db).
- If the message is similar to `These dbs xxx are in binlog_ignore_db xxx`, make sure all the databases that you want to migrate are not in the ignore list. See [--binlog-ignore-db=db_name](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#option_mysqld_binlog-ignore-db).

For Amazon Aurora MySQL, this precheck item does not fail for it. Make sure you are using Amazon Aurora MySQL writer instances to support both full and incremental data migration.

For Amazon RDS, you need to change the following parameters: `replicate-do-db`, `replicate-do-table`, `replicate-ignore-db`, and `replicate-ignore-table`. See [Configuring MySQL binary logging](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.MySQL.BinaryFormat.html).
### Error message: Check if connection concurrency exceeds database's maximum connection limit

If the error occurs in the upstream database, set `max_connections` as follows:

- Amazon Aurora MySQL: the process is similar to setting the `binlog_format`. The only difference is that the parameter you change is `max_connections` instead of `binlog_format`. See [How do I turn on binary logging for my Amazon Aurora MySQL-Compatible cluster](https://aws.amazon.com/premiumsupport/knowledge-center/enable-binary-logging-aurora/?nc1=h_ls).
- Amazon RDS: the process is similar to setting the `binlog_format`. The only difference is that the parameter you change is `max_connections` instead of `binlog_format`.  See [Configuring MySQL binary logging](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.MySQL.BinaryFormat.html).
- MySQL: configure `max_connections` following the document [max_connections](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_max_connections).

If the error occurs in the TiDB Cloud cluster, configure `max_connections` following the document [max_connections](https://docs.pingcap.com/tidb/stable/system-variables#max_connections).
