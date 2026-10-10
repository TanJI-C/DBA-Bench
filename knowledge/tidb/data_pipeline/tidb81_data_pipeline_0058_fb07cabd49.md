# Full data migration with BR backup and restore

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/replicate-between-primary-and-secondary-clusters.md`
- Source Title: `Replicate data between primary and secondary clusters`
- Source Heading Path: `Replicate Data Between Primary and Secondary Clusters > Step 2. Migrate full data`
- Source Line Ranges: `99-213`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tidb`, `shared`
- Topic Tags: `full migration`, `backup`, `restore`, `gc disable`, `backupts`, `data validation`, `sync-diff-inspector`, `experimental sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0058_fb07cabd49`
- Source ID: `tidb-docs-8.1:replicate-between-primary-and-secondary-clusters.md#step-2-migrate-full-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c90dd5f91c1a66dab3bdd49ffcb06c531540320b7b731fcada0204c45c736f1b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/replicate-between-primary-and-secondary-clusters#step-2-migrate-full-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/replicate-between-primary-and-secondary-clusters.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented full data migration procedure between upstream and downstream clusters using BR SQL statements, including disabling GC, recording BackupTS, restoring data, and optional validation with sync-diff-inspector.
- Retrieval Keywords: Step 2. Migrate full data, BR, BACKUP, RESTORE, BACKUP DATABASE * TO, RESTORE DATABASE * FROM, tidb_gc_enable, SET GLOBAL tidb_gc_enable=FALSE, SELECT @@global.tidb_gc_enable, BackupTS, GC disabled, RATE_LIMIT = 120 MB/SECOND, sync-diff-inspector, sync_diff_inspector -C ./config.yaml, snapshot, 431434047157698561, 431434141450371074, experimental SQL statements, BR compatibility
- Follow-up Guidance: The source says to pay attention to BackupTS because it is used as the end of data check and the start of incremental migration scanning by TiCDC.
- Classification Note: This is classified as a data_pipeline chunk because the content covers full backup, restore, timestamp-based validation points, and consistency checking in the migration workflow.

## Official Source Content

## Step 2. Migrate full data

After setting up the environment, you can use the backup and restore functions of [BR](https://github.com/pingcap/tidb/tree/release-8.1/br) to migrate full data. BR can be started in [three ways](https://docs.pingcap.com/tidb/stable/br/br-use-overview#deploy-and-use-br). In this document, we use the SQL statements, `BACKUP` and `RESTORE`.

> **Note:**
>
> - `BACKUP` and `RESTORE` SQL statements are experimental. It is not recommended that you use them in the production environment. They might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.
> - In production clusters, performing a backup with GC disabled might affect cluster performance. It is recommended that you back up data in off-peak hours, and set RATE_LIMIT to a proper value to avoid performance degradation.
> - If the versions of the upstream and downstream clusters are different, you should check [BR compatibility](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview#some-tips). In this document, we assume that the upstream and downstream clusters are the same version.

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
    +-------------------------+
    | @@global.tidb_gc_enable |
    +-------------------------+
    |                       0 |
    +-------------------------+
    1 row in set (0.00 sec)
    ```

2. Back up data.

    Run the `BACKUP` statement in the upstream cluster to back up data:

    ```sql
    MySQL [(none)]> BACKUP DATABASE * TO 's3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://${HOST_IP}:6060&force-path-style=true' RATE_LIMIT = 120 MB/SECOND;
    ```

    ```
    +----------------------+----------+--------------------+---------------------+---------------------+
    | Destination          | Size     | BackupTS           | Queue Time          | Execution Time      |
    +----------------------+----------+--------------------+---------------------+---------------------+
    | local:///tmp/backup/ | 10315858 | 431434047157698561 | 2022-02-25 19:57:59 | 2022-02-25 19:57:59 |
    +----------------------+----------+--------------------+---------------------+---------------------+
    1 row in set (2.11 sec)
    ```

    After the `BACKUP` command is executed, TiDB returns metadata about the backup data. Pay attention to `BackupTS`, because data generated before it is backed up. In this document, we use `BackupTS` as **the end of data check** and **the start of incremental migration scanning by TiCDC**.

3. Restore data.

    Run the `RESTORE` command in the downstream cluster to restore data:

    ```sql
    mysql> RESTORE DATABASE * FROM 's3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://${HOST_IP}:6060&force-path-style=true';
    ```

    ```
    +----------------------+----------+--------------------+---------------------+---------------------+
    | Destination          | Size     | BackupTS           | Queue Time          | Execution Time      |
    +----------------------+----------+--------------------+---------------------+---------------------+
    | local:///tmp/backup/ | 10315858 | 431434141450371074 | 2022-02-25 20:03:59 | 2022-02-25 20:03:59 |
    +----------------------+----------+--------------------+---------------------+---------------------+
    1 row in set (41.85 sec)
    ```

4. (Optional) Validate data.

    Use [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview) to check data consistency between upstream and downstream at a certain time. The preceding `BACKUP` output shows that the upstream cluster finishes backup at 431434047157698561. The preceding `RESTORE` output shows that the downstream finishes restoration at 431434141450371074.

    ```shell
    sync_diff_inspector -C ./config.yaml
    ```

    For details about how to configure the sync-diff-inspector, see [Configuration file description](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview#configuration-file-description). In this document, the configuration is as follows:

    ```shell
    # Diff Configuration.
    ######################### Global config #########################
    check-thread-count = 4
    export-fix-sql = true
    check-struct-only = false

    ######################### Datasource config #########################
    [data-sources]
    [data-sources.upstream]
            host = "172.16.6.123" # Replace it with the IP address of your upstream cluster
            port = 4000
            user = "root"
            password = ""
            snapshot = "431434047157698561" # Set snapshot to the actual backup time
    [data-sources.downstream]
            host = "172.16.6.124" # Replace the value with the IP address of your downstream cluster
            port = 4000
            user = "root"
            password = ""
            snapshot = "431434141450371074" # Set snapshot to the actual restore time

    ######################### Task config #########################
    [task]
            output-dir = "./output"
            source-instances = ["upstream"]
            target-instance = "downstream"
            target-check-tables = ["*.*"]
    ```
