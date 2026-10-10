# DM FAQ: compatibility, DDL limits, task reset, and gh-ost online DDL handling

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-faq.md`
- Source Title: `TiDB Data Migration FAQs`
- Source Heading Path: `TiDB Data Migration FAQs | TiDB Data Migration FAQs > Does DM support migrating data from Alibaba RDS or other cloud databases? | TiDB Data Migration FAQs > Does the regular expression of the block and allow list in the task configuration support `non-capturing (?!)`? | TiDB Data Migration FAQs > If a statement executed upstream contains multiple DDL operations, does DM support such migration? | TiDB Data Migration FAQs > How to handle incompatible DDL statements? | TiDB Data Migration FAQs > Does DM replicate view-related DDL statements and DML statements to TiDB? | TiDB Data Migration FAQs > How to reset the data migration task? | TiDB Data Migration FAQs > How to handle the error returned by the DDL operation related to the gh-ost table, after `online-ddl: true` is set?`
- Source Line Ranges: `5-80`
- Source Scope: `shared`
- Primary Component: `dm`
- Related Components: `tidb`, `sql`
- Topic Tags: `compatibility`, `cloud-rds`, `regex`, `ddl`, `views`, `task-reset`, `online-ddl`, `gh-ost`, `binlog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0092_9d0ce20db4`
- Source ID: `tidb-docs-8.1:dm/dm-faq.md#tidb-data-migration-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f8569ce76e0ffb22ee7b9e1c445f94b6aab77cf566de5bc53ef3588a6c70d60e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-faq#tidb-data-migration-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-faq.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting DM support limits or task handling for cloud RDS binlog compatibility, regex syntax, multi-DDL statements, unsupported DDL, view replication, task reset, or gh-ost online DDL errors.
- Retrieval Keywords: Alibaba Cloud RDS, HUAWEI Cloud RDS, standard version of MySQL or MariaDB binlog, hidden primary key column, block and allow list, non-capturing (?!), Golang standard library, re2-syntax, multiple DDL operations, Handle failed DDL statements, MySQL Compatibility, view-related DDL statements, view-related DML statements, stop-task, start-task --remove-meta, online-ddl: true, gh-ost table, online ddls on ghost table, dm_meta.{task_name}_onlineddl, block-allow-list.ignore-tables, _{table_name}_gho, _{table_name}_ghc, _{table_name}_del
- Follow-up Guidance: The content also lists the reset sequence with `stop-task`, downstream purge, and restart options, and describes the gh-ost workaround steps involving `online-ddl-scheme` or `online-ddl` and `block-allow-list.ignore-tables`.
- Classification Note: This chunk is classified as operation because it describes support boundaries and operational handling for DM tasks, DDL processing, view replication, task reset, and gh-ost online DDL behavior.

## Official Source Content

# TiDB Data Migration FAQs

This document collects the frequently asked questions (FAQs) about TiDB Data Migration (DM).
## Does DM support migrating data from Alibaba RDS or other cloud databases?

Currently, DM only supports decoding the standard version of MySQL or MariaDB binlog. It has not been tested for Alibaba Cloud RDS or other cloud databases. If you are confirmed that its binlog is in standard format, then it is supported.

It is a known issue that for an upstream table with no primary key in Alibaba Cloud RDS, its binlog still contains a hidden primary key column, which is inconsistent with the original table structure.

Here are some known incompatible issues:

- In **Alibaba Cloud RDS**, for an upstream table with no primary key, its binlog still contains a hidden primary key column, which is inconsistent with the original table structure.
- In **HUAWEI Cloud RDS**, directly reading binlog files is not supported. For more details, see [Can HUAWEI Cloud RDS Directly Read Binlog Backup Files?](https://support.huaweicloud.com/en-us/rds_faq/rds_faq_0210.html)
## Does the regular expression of the block and allow list in the task configuration support `non-capturing (?!)`?

Currently, DM does not support it and only supports the regular expressions of the Golang standard library. See regular expressions supported by Golang via [re2-syntax](https://github.com/google/re2/wiki/Syntax).
## If a statement executed upstream contains multiple DDL operations, does DM support such migration?

DM will attempt to split a single statement containing multiple DDL change operations into multiple statements containing only one DDL operation, but might not cover all cases. It is recommended to include only one DDL operation in a statement executed upstream, or verify it in the test environment. If it is not supported, you can file an [issue](https://github.com/pingcap/tiflow/issues) to the `pingcap/tiflow` repository.
## How to handle incompatible DDL statements?

When you encounter a DDL statement unsupported by TiDB, you need to manually handle it using dmctl (skipping the DDL statement or replacing the DDL statement with a specified DDL statement). For details, see [Handle failed DDL statements](https://docs.pingcap.com/tidb/stable/dm/handle-failed-ddl-statements).

> **Note:**
>
> Currently, TiDB is not compatible with all the DDL statements that MySQL supports. See [MySQL Compatibility](https://docs.pingcap.com/tidb/stable/mysql-compatibility#ddl-operations).
## Does DM replicate view-related DDL statements and DML statements to TiDB?

Currently, DM does not replicate view-related DDL statements to the downstream TiDB cluster, nor does it replicate view-related DML statements to the downstream TiDB cluster.
## How to reset the data migration task?

When an exception occurs during data migration and the data migration task cannot be resumed, you need to reset the task and re-migrate the data:

1. Execute the `stop-task` command to stop the abnormal data migration task.

2. Purge the data migrated to the downstream.

3. Use one of the following ways to restart the data migration task.

   - Specify a new task name in the task configuration file. Then execute `start-task {task-config-file}`.
   - Execute `start-task --remove-meta {task-config-file}`.
## How to handle the error returned by the DDL operation related to the gh-ost table, after `online-ddl: true` is set?

```
[unit=Sync] ["error information"="{\"msg\":\"[code=36046:class=sync-unit:scope=internal:level=high] online ddls on ghost table `xxx`.`_xxxx_gho`\\ngithub.com/pingcap/tiflow/pkg/terror.(*Error).Generate ......
```

The above error can be caused by the following reason:

In the last `rename ghost_table to origin table` step, DM reads the DDL information in memory, and restores it to the DDL of the origin table.

However, the DDL information in memory is obtained in either of the two ways:

- DM [processes the gh-ost table during the `alter ghost_table` operation](https://docs.pingcap.com/tidb/stable/dm/feature-online-ddl#online-schema-change-gh-ost) and records the DDL information of `ghost_table`;
- When DM-worker is restarted to start the task, DM reads the DDL from `dm_meta.{task_name}_onlineddl`.

Therefore, in the process of incremental replication, if the specified Pos has skipped the `alter ghost_table` DDL but the Pos is still in the online-ddl process of gh-ost, the ghost_table is not written into memory or `dm_meta.{task_name}_onlineddl` correctly. In such cases, the above error is returned.

You can avoid this error by the following steps:

1. Remove the `online-ddl-scheme` or `online-ddl` configuration of the task.

2. Configure `_{table_name}_gho`, `_{table_name}_ghc`, and `_{table_name}_del` in `block-allow-list.ignore-tables`.

3. Execute the upstream DDL in the downstream TiDB manually.

4. After the Pos is replicated to the position after the gh-ost process, re-enable the `online-ddl-scheme` or `online-ddl` configuration and comment out `block-allow-list.ignore-tables`.
