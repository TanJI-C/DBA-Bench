# Full data migration with BR backup and restore

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-tidb-to-tidb.md`
- Source Title: `Migrate from one TiDB cluster to another TiDB cluster`
- Source Heading Path: `Migrate from One TiDB Cluster to Another TiDB Cluster > Step 2. Migrate full data`
- Source Line Ranges: `100-212`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tidb`, `ticdc`, `shared`
- Topic Tags: `full-migration`, `backup`, `restore`, `gc`, `backupts`, `validation`, `sync-diff-inspector`, `s3`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0039_eb5a2bcb0c`
- Source ID: `tidb-docs-8.1:migrate-from-tidb-to-tidb.md#step-2-migrate-full-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `08054b3ed700d27c3d2697d36c2da5118420ab4b86db4ab89683afab6ad4305e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-tidb-to-tidb#step-2-migrate-full-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-tidb-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to migrate full data between TiDB clusters with BR using the experimental `BACKUP` and `RESTORE` SQL statements, including GC handling, `BackupTS`, and optional validation with sync-diff-inspector.
- Retrieval Keywords: Step 2. Migrate full data, BR, BACKUP, RESTORE, SET GLOBAL tidb_gc_enable=FALSE, SELECT @@global.tidb_gc_enable, gc-ttl, TiCDC gc-ttl, BACKUP DATABASE * TO, RESTORE DATABASE * FROM, RATE_LIMIT = 120 MB/SECOND, BackupTS, incremental migration scanning by TiCDC, sync-diff-inspector, sync_diff_inspector -C ./config.yaml, snapshot, 431434047157698561, s3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://${HOST_IP}:6060&force-path-style=true
- Follow-up Guidance: The chunk notes that `BackupTS` is used as the end of data check and the start of incremental migration scanning by TiCDC, and it references the subsequent incremental replication task.
- Classification Note: This is classified as a data_pipeline chunk because the content covers full data backup, restore, and validation workflow across upstream and downstream TiDB clusters.

## Official Source Content

## Step 2. Migrate full data

After setting up the environment, you can use the backup and restore functions of [BR](https://github.com/pingcap/tidb/tree/release-8.1/br) to migrate full data. BR can be started in [three ways](https://docs.pingcap.com/tidb/stable/br/br-use-overview#deploy-and-use-br). In this document, we use the SQL statements, `BACKUP` and `RESTORE`.

> **Note:**
>
> - `BACKUP` and `RESTORE` SQL statements are experimental. It is not recommended that you use them in the production environment. They might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.
> - In production clusters, performing a backup with GC disabled might affect cluster performance. It is recommended that you back up data in off-peak hours, and set `RATE_LIMIT` to a proper value to avoid performance degradation.
> - If the versions of the upstream and downstream clusters are different, you should check [BR compatibility](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview#before-you-use). In this document, we assume that the upstream and downstream clusters are the same version.

1. Disable GC.

    To ensure that newly written data is not deleted during incremental migration, you should disable GC for the upstream cluster before backup. In this way, history data is not deleted.

    Run the following command to disable GC:

    ```sql
    MySQL [test]> SET GLOBAL tidb_gc_enable=FALSE;
    ```

    ```
    Query OK, 0 rows affected (0.01 sec)
    ```

    To verify that the change takes effect, query the value of `tidb_gc_enable`:

    ```sql
    MySQL [test]> SELECT @@global.tidb_gc_enable;
    ```

    ```
    +-------------------------+:
    | @@global.tidb_gc_enable |
    +-------------------------+
    |                       0 |
    +-------------------------+
    1 row in set (0.00 sec)
    ```

    > **Note:**
    >
    > TiCDC `gc-ttl` is 24 hours by default. If the backup and restore takes a long time, the default `gc-ttl` might not be sufficient, which could cause the subsequent [incremental replication task](#step-3-migrate-incremental-data) to fail. To avoid this situation, adjust the `gc-ttl` value according to your specific needs when starting the TiCDC server. For more information, see [What is `gc-ttl` in TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#what-is-gc-ttl-in-ticdc).

2. Back up data.

    Run the `BACKUP` statement in the upstream cluster to back up data:

    ```sql
    MySQL [(none)]> BACKUP DATABASE * TO 's3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://${HOST_IP}:6060&force-path-style=true' RATE_LIMIT = 120 MB/SECOND;
    ```

    ```
    +---------------+----------+--------------------+---------------------+---------------------+
    | Destination   | Size     | BackupTS           | Queue Time          | Execution Time      |
    +---------------+----------+--------------------+---------------------+---------------------+
    | s3://backup   | 10315858 | 431434047157698561 | 2022-02-25 19:57:59 | 2022-02-25 19:57:59 |
    +---------------+----------+--------------------+---------------------+---------------------+
    1 row in set (2.11 sec)
    ```

    After the `BACKUP` command is executed, TiDB returns metadata about the backup data. Pay attention to `BackupTS`, because data generated before it is backed up. In this document, we use `BackupTS` as **the end of data check** and **the start of incremental migration scanning by TiCDC**.

3. Restore data.

    Run the `RESTORE` command in the downstream cluster to restore data:

    ```sql
    mysql> RESTORE DATABASE * FROM 's3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://${HOST_IP}:6060&force-path-style=true';
    ```

    ```
    +--------------+-----------+--------------------+---------------------+---------------------+
    | Destination  | Size      | BackupTS           | Queue Time          | Execution Time      |
    +--------------+-----------+--------------------+---------------------+---------------------+
    | s3://backup  | 10315858  | 431434141450371074 | 2022-02-25 20:03:59 | 2022-02-25 20:03:59 |
    +--------------+-----------+--------------------+---------------------+---------------------+
    1 row in set (41.85 sec)
    ```

4. (Optional) Validate data.

    You can use [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview) to check data consistency between upstream and downstream at a certain time. The preceding `BACKUP` output shows that the upstream cluster finishes backup at 431434047157698561. The preceding `RESTORE` output shows that the downstream finishes restoration at 431434141450371074.

    ```shell
    sync_diff_inspector -C ./config.yaml
    ```

    For details about how to configure the sync-diff-inspector, see [Configuration file description](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview#configuration-file-description). In this document, the configuration is as follows:

    ```shell
    # Diff Configuration.
    ######################### Datasource config #########################
    [data-sources]
    [data-sources.upstream]
        host = "172.16.6.122" # Replace the value with the IP address of your upstream cluster
        port = 4000
        user = "root"
        password = ""
        snapshot = "431434047157698561" # Set snapshot to the actual backup time (BackupTS in the "Back up data" section in [Step 2. Migrate full data](#step-2-migrate-full-data))
    [data-sources.downstream]
        host = "172.16.6.125" # Replace the value with the IP address of your downstream cluster
        port = 4000
        user = "root"
        password = ""

    ######################### Task config #########################
    [task]
        output-dir = "./output"
        source-instances = ["upstream"]
        target-instance = "downstream"
        target-check-tables = ["*.*"]
    ```
