# DM configuration details and migration troubleshooting

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-best-practices.md`
- Source Title: `TiDB Data Migration (DM) Best Practices`
- Source Heading Path: `TiDB Data Migration (DM) Best Practices > Before data migration > Details of configurations | TiDB Data Migration (DM) Best Practices > Before data migration > Details of configurations > Capitalization | TiDB Data Migration (DM) Best Practices > Before data migration > Details of configurations > Filter rules | TiDB Data Migration (DM) Best Practices > Before data migration > Details of configurations > Use the relay log | TiDB Data Migration (DM) Best Practices > Before data migration > Details of configurations > Use PT-osc/GH-ost in upstream | TiDB Data Migration (DM) Best Practices > Best practices during migration | TiDB Data Migration (DM) Best Practices > Best practices during migration > Inconsistent schemas in upstream and downstream`
- Source Line Ranges: `166-219`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `configuration`, `case-sensitivity`, `filter-rules`, `relay-log`, `online-ddl`, `schema-mismatch`, `troubleshooting`, `incremental-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0084_bb81343a91`
- Source ID: `tidb-docs-8.1:dm/dm-best-practices.md#details-of-configurations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `19bc6602b640d6a573866adf42a3fcf19e5061a7e902b9e724bba5d48769f7c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-best-practices#details-of-configurations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when configuring DM task details such as case sensitivity, filter rules, relay logs, online DDL tools, or when troubleshooting schema mismatch errors during migration.
- Retrieval Keywords: case-sensitive, lower_case_table_names:2, ERROR 1050 (42S01): Table '{tablename}' already exists, filter rules, Data Migration Task Configuration Guide, relay log, DM-worker, upstream binlogs, error 1236, binlog checksum mismatch, PT-osc, GH-ost, feature-online-ddl, Column count doesn't match value count: 3 (columns) vs 2 (values), Schema/Column doesn't match, Manage Table Schemas of Tables to be Migrated, Migrate Data to a Downstream TiDB Table with More Columns
- Follow-up Guidance: The source says to update the schema information cached in DM to match the downstream TiDB schema and references schema management and downstream-more-columns guidance.
- Classification Note: This is classified as operation content because it focuses on DM configuration behavior and migration troubleshooting scenarios described in the official documentation.

## Official Source Content

### Details of configurations
#### Capitalization

TiDB schema names are case-insensitive by default, that is, `lower_case_table_names:2`. But most upstream MySQL databases use Linux systems that are case-sensitive by default. In this case, you need to set `case-sensitive` to `true` in the DM task configuration file to ensure that the schema can be correctly migrated from the upstream.

In a special case, for example, if there is a database in the upstream that has both uppercase tables such as `Table` and lowercase tables such as `table`, then an error occurs when creating the schema:

`ERROR 1050 (42S01): Table '{tablename}' already exists`
#### Filter rules

You can configure the filter rules as soon as you start configuring the data source. For more information, see [Data Migration Task Configuration Guide](https://docs.pingcap.com/tidb/stable/dm/dm-task-configuration-guide). The benefits of configuring the filter rules are:

- Reduce the number of Binlog events that the downstream needs to process, thereby improving migration efficiency.
- Reduce unnecessary relay log storage, thereby saving disk space.

> **Note:**
>
> When you migrate and merge MySQL shards, if you have configured filter rules in the data source, you must make sure that the rules match between the data source and the migration task. If they do not match, it may cause the issue that the migration task cannot receive incremental data for a long time.
#### Use the relay log

In the MySQL master/standby mechanism, the standby node saves a copy of relay logs to ensure the reliability and efficiency of asynchronous replication. DM also supports saving a copy of relay logs on DM-worker. You can configure information such as the storage location and expiration time. This feature applies to the following scenarios:

- During full and incremental data migration, if the amount of full data is large, the entire process takes more time than the time for the upstream binlogs to be archived. It causes the incremental replication task to fail to start normally. If you enable the relay log, DM-worker will start receiving relay logs when the full migration is started. This avoids the failure of the incremental task.

- When you use DM to perform long-time data replication, sometimes the migration task is blocked for a long time due to various reasons. If you enable the relay log, you can effectively deal with the problem of upstream binlogs being recycled due to the blocking of the migration task.

There are some restrictions on using the relay log. DM supports high availability. When a DM-worker fails, it will try to promote an idle DM-worker instance to a working instance. If the upstream binlogs do not contain the necessary migration logs, it may cause interruption. You need to intervene manually to copy the relay log to the new DM-worker node as soon as possible, and modify the corresponding relay meta file. For details, see [Troubleshooting](https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#the-relay-unit-throws-error-event-from--in--diff-from-passed-in-event--or-a-migration-task-is-interrupted-with-failing-to-get-or-parse-binlog-errors-like-get-binlog-error-error-1236-hy000-and-binlog-checksum-mismatch-data-may-be-corrupted-returned).
#### Use PT-osc/GH-ost in upstream

In daily MySQL operation and maintenance, usually you use tools such as PT-osc/GH-ost to change the schema online to minimize impact on the business. However, the whole process will be logged to MySQL Binlog. Migrating such data to TiDB downstream will result in a lot of unnecessary write operations, which is neither efficient nor economical.

To resolve this issue, DM supports third-party data tools such as PT-osc and GH-ost when you configure the migration task. When you use such tools, DM does not migrate redundant data and ensure data consistency. For details, see [Migrate from Databases that Use GH-ost/PT-osc](https://docs.pingcap.com/tidb/stable/dm/feature-online-ddl).
## Best practices during migration

This section introduces how to troubleshoot problems you might encounter during migration.
### Inconsistent schemas in upstream and downstream

Common errors include:

- `messages: Column count doesn't match value count: 3 (columns) vs 2 (values)`
- `Schema/Column doesn't match`

Usually such issues are caused by changed or added indexes in the downstream TiDB, or there are more columns in the downstream. When such errors occur, check whether the upstream and downstream schemas are inconsistent.

To resolve such issues, update the schema information cached in DM to be consistent with the downstream TiDB schema. For details, see [Manage Table Schemas of Tables to be Migrated](https://docs.pingcap.com/tidb/stable/dm/dm-manage-schema).

If the downstream has more columns, see [Migrate Data to a Downstream TiDB Table with More Columns](https://docs.pingcap.com/tidb/stable/migrate-with-more-columns-downstream).
