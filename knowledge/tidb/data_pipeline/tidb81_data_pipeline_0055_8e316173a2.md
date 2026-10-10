# Data migration and large-scale replication features

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.0.0-dmr.md`
- Source Title: `TiDB 6.0.0 Release Notes`
- Source Heading Path: `TiDB 6.0.0 Release Notes > New features > Data migration > TiDB Data Migration (DM) | TiDB 6.0.0 Release Notes > New features > Data migration > TiDB Lightning | TiDB 6.0.0 Release Notes > New features > TiDB data share subscription`
- Source Line Ranges: `183-239`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dm`, `lightning`, `ticdc`, `tidb`
- Topic Tags: `data-migration`, `webui`, `error-handling`, `s3-storage`, `start-time`, `import-errors`, `replication-scale`, `incremental-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0055_8e316173a2`
- Source ID: `tidb-docs-8.1:releases/release-6.0.0-dmr.md#tidb-data-migration-dm`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bfddfbe3bc35aa68dfe5edf99e95890a8a97a287b4cec2b17ed939c1a59124be`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.0.0-dmr#tidb-data-migration-dm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.0.0-dmr.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.0.0 release-note details about DM WebUI, DM error handling, Amazon S3 full-data storage, `--start-time` migration tasks, TiDB Lightning import error tolerance, or TiCDC large-scale table replication.
- Retrieval Keywords: TiDB 6.0.0 DM WebUI experimental, DM Dashboard manage migration tasks, dmctl same task known issue WebUI, binlog-schema update --from-source --from-target, inject replace skip revert DDL statement binlog position, DM Amazon S3 dump directory full data migration, DM --start-time safe-mode incremental migration, TiDB Lightning lightning.max-error, lightning.task-info-schema-name, lightning_task_info.type_error_v1, type error syntax errors not applicable, TiCDC replicating 100000 tables simultaneously
- Follow-up Guidance: The content also points to related user documents for the DM WebUI guide, schema management, task configuration, task creation flags, and TiDB Lightning type-error handling.
- Classification Note: This chunk is classified as data_pipeline because it introduces migration, import, error-handling, storage, and large-scale replication features across DM, Lightning, and TiCDC.

## Official Source Content

#### TiDB Data Migration (DM)

- Add WebUI (experimental)

    With the WebUI, you can easily manage a large number of migration tasks. On the WebUI, you can:

    - View migration tasks on Dashboard
    - Manage migration tasks
    - Configure upstream settings
    - Query replication status
    - View master and worker information

    WebUI is still experimental and is still under development. Therefore, it is recommended only for trial. A known issue is that problems might occur if you use WebUI and dmctl to operate the same task. This issue will be resolved in later versions.

    [User document](https://docs.pingcap.com/tidb/stable/dm/dm-webui-guide)

- Add an error handling mechanism

    More commands are introduced to address problems that interrupt a migration task. For example:

    - In case of a schema error, you can update the schema file by using the `--from-source/--from-target` parameter of the `binlog-schema update` command, instead of editing the schema file separately.
    - You can specify a binlog position to inject, replace, skip, or revert a DDL statement.

    [User document](https://docs.pingcap.com/tidb/stable/dm/dm-manage-schema)

- Support full data storage to Amazon S3

    When DM performs all or full data migration tasks, sufficient hard disk space is required for storing full data from upstream. Compared with EBS, Amazon S3 has nearly infinite storage at lower costs. Now, DM supports configuring Amazon S3 as the dump directory. That means you can use S3 to store full data when you perform all or full data migration tasks.

    [User document](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced)

- Support starting a migration task from specified time

    A new parameter `--start-time` is added to migration tasks. You can define time in the format of '2021-10-21 00:01:00' or '2021-10-21T00:01:00'.

    This feature is particularly useful in scenarios where you migrate and merge incremental data from shard mysql instances. Specifically, you do not need to set a binlog start point for each source in an incremental migration task. Instead, you can create an incremental migration task quickly by using the `--start-time` parameter in `safe-mode`.

    [User document](https://docs.pingcap.com/tidb/stable/dm/dm-create-task#flags-description)
#### TiDB Lightning

- Support configuring the maximum number of tolerable errors

    Added a configuration item `lightning.max-error`. The default value is 0. When the value is greater than 0, the max-error feature is enabled. If an error occurs in a row during encoding, a record containing this row is added to `lightning_task_info.type_error_v1` in the target TiDB and this row is ignored. When rows with errors exceed the threshold, TiDB Lightning exits immediately.

    Matching the `lightning.max-error` configuration, the `lightning.task-info-schema-name` configuration item records the name of the database that reports a data saving error.

    This feature does not cover all types of errors, for example, syntax errors are not applicable.

    [User document](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-error-resolution#type-error)
### TiDB data share subscription

- Support replicating 100,000 tables simultaneously

    By optimizing the data processing flow, TiCDC reduces the resource consumption of processing incremental data for each table, which greatly improves the replication stability and efficiency when replicating data in large clusters. The result of an internal test shows that TiCDC can stably support replicating 100,000 tables simultaneously.
