# SQL and DB operations features in v8.0.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Feature details > SQL | TiDB 8.0.0 Release Notes > Feature details > DB operations`
- Source Line Ranges: `161-210`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `br`, `sql`
- Topic Tags: `release-notes`, `sql`, `dml`, `pipelined-dml`, `system-variables`, `default-values`, `division-precision`, `pitr`, `s3-object-lock`, `invisible-indexes`, `general-log`, `log-compression`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0577_3c7ff45c31`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#sql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b36f403d5fa59b8fb5d9f02257227cccdeb5a46c1d477dab7ee4755b9aad93a1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 8.0.0 release-note details about SQL and DB operations features such as Pipelined DML, expression default values, division precision, PITR Object Lock, invisible indexes, and general log file settings.
- Retrieval Keywords: TiDB 8.0.0 release notes SQL, Pipelined DML, tidb_dml_type, auto-commit enabled, INSERT UPDATE REPLACE DELETE, default column values expressions, UUID() default value, div_precision_increment, PITR Amazon S3 Object Lock, BR snapshot backups, tidb_opt_use_invisible_indexes, invisible indexes session level, tidb_general_log, log.general-log-file, log.file.compression, gzip rotated logs
- Follow-up Guidance: The content points to related documentation for `tidb_dml_type`, expression default values, `div_precision_increment`, backup storage features, invisible indexes, and TiDB configuration items `log.general-log-file` and `log.file.compression`.
- Classification Note: This is a release chunk because it lists new SQL and DB operations capabilities introduced in TiDB v8.0.0, including system variables, backup behavior, index visibility, and logging configuration.

## Official Source Content

### SQL

* Support a new DML type for handling a large amount of data (experimental) [#50215](https://github.com/pingcap/tidb/issues/50215) @[ekexium](https://github.com/ekexium)

    Before v8.0.0, TiDB stores all transaction data in memory before committing. When processing a large amount of data, the memory required for transactions becomes a bottleneck that limits the transaction size that TiDB can handle. Although TiDB introduces non-transactional DML to attempt to solve the transaction size limitation by splitting SQL statements, this feature has various limitations and does not provide an ideal experience in actual scenarios.

    Starting from v8.0.0, TiDB supports a DML type for handling a large amount of data. This DML type writes data to TiKV in a timely manner during execution, avoiding the continuous storage of all transaction data in memory, and thus supports handling a large amount of data that exceeds the memory limit. This DML type ensures transaction integrity and uses the same syntax as standard DML. `INSERT`, `UPDATE`, `REPLACE`, and `DELETE` statements can use this new DML type to execute large-scale DML operations.

    This DML type is implemented by the [Pipelined DML](https://github.com/pingcap/tidb/blob/release-8.0/docs/design/2024-01-09-pipelined-DML.md) feature and only takes effect on statements with auto-commit enabled. You can control whether to enable this DML type by setting the system variable [`tidb_dml_type`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_type-new-in-v800).

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_type-new-in-v800).

* Support using some expressions to set default column values when creating a table (experimental) [#50936](https://github.com/pingcap/tidb/issues/50936) @[zimulala](https://github.com/zimulala)

    Before v8.0.0, when you create a table, the default value of a column is limited to strings, numbers, and dates. Starting from v8.0.0, you can use some expressions as the default column values. For example, you can set the default value of a column to `UUID()`. This feature helps you meet more diverse requirements.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/data-type-default-values#specify-expressions-as-default-values).

* Support the `div_precision_increment` system variable [#51501](https://github.com/pingcap/tidb/issues/51501) @[yibin87](https://github.com/yibin87)

    MySQL 8.0 supports the variable `div_precision_increment`, which specifies the number of digits by which to increase the scale of the result of a division operation performed using the `/` operator. Before v8.0.0, TiDB does not support this variable, and division is performed to 4 decimal places. Starting from v8.0.0, TiDB supports this variable. You can specify the number of digits by which to increase the scale of the result of a division operation as desired.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#div_precision_increment-new-in-v800).
### DB operations

* PITR supports Amazon S3 Object Lock [#51184](https://github.com/pingcap/tidb/issues/51184) @[RidRisR](https://github.com/RidRisR)

    Amazon S3 Object Lock can help prevent backup data from accidental or intentional deletion during a specified retention period, enhancing the security and integrity of data. Starting from v6.3.0, BR supports Amazon S3 Object Lock for snapshot backups, adding an additional layer of security for full backups. Starting from v8.0.0, PITR also supports Amazon S3 Object Lock. Whether for full backups or log data backups, the Object Lock feature ensures more reliable data protection, further strengthening the security of data backup and recovery and meeting regulatory requirements.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages#other-features-supported-by-the-storage-service).

* Support making invisible indexes visible at the session level [#50653](https://github.com/pingcap/tidb/issues/50653) @[hawkingrei](https://github.com/hawkingrei)

    By default, the optimizer does not select [invisible indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#invisible-index). This mechanism is usually used to evaluate whether to delete an index. If there is uncertainty about the potential performance impact of deleting an index, you have the option to set the index to invisible temporarily and promptly restore it to visible when needed.

    Starting from v8.0.0, you can set the session-level system variable [`tidb_opt_use_invisible_indexes`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_use_invisible_indexes-new-in-v800) to `ON` to make the current session aware of invisible indexes. With this feature, you can create a new index and test its performance by making the index visible first, and then modifying the system variable in the current session for testing without affecting other sessions. This improvement enhances the safety of SQL tuning and helps to improve the stability of production databases.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#invisible-index).

* Support writing general logs to a separate file [#51248](https://github.com/pingcap/tidb/issues/51248) @[Defined2014](https://github.com/Defined2014)

    The general log is a MySQL-compatible feature that logs all executed SQL statements to help diagnose issues. TiDB also supports this feature. You can enable it by setting the variable [`tidb_general_log`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_general_log). However, in previous versions, the content of general logs can only be written to the TiDB instance log along with other information, which is inconvenient for users who need to keep logs for a long time.

    Starting from v8.0.0, you can write the general log to a specified file by setting the configuration item [`log.general-log-file`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#general-log-file-new-in-v800) to a valid filename. The general log follows the same rotation and retention policies as the instance log.

    In addition, to reduce the disk space occupied by historical log files, TiDB v8.0.0 introduces a native log compression option. You can set the configuration item [`log.file.compression`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#compression-new-in-v800) to `gzip` to automatically compress rotated logs using the [`gzip`](https://www.gzip.org/) format.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#general-log-file-new-in-v800).
