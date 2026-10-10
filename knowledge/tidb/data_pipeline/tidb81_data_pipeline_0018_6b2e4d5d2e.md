# Bootstrap secondary cluster with backup restore and TiCDC incremental replication

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-secondary-cluster.md`
- Source Title: `DR Solution Based on Primary and Secondary Clusters`
- Source Heading Path: `DR Solution Based on Primary and Secondary Clusters > Set up primary and secondary clusters based on TiCDC > Replicate data from the primary cluster to the secondary cluster > Migrate data | DR Solution Based on Primary and Secondary Clusters > Set up primary and secondary clusters based on TiCDC > Replicate data from the primary cluster to the secondary cluster > Replicate incremental data`
- Source Line Ranges: `146-282`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `br`, `tidb`, `sql`
- Topic Tags: `backup`, `restore`, `incremental-replication`, `changefeed`, `redo-log`, `gc`, `backupts`, `migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0018_6b2e4d5d2e`
- Source ID: `tidb-docs-8.1:dr-secondary-cluster.md#migrate-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6623d05956e94d9651eb1fa31c9124fd5c27d63b6bc2407e17872fc6ff963b9f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-secondary-cluster#migrate-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-secondary-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when finding the documented sequence to bootstrap a secondary cluster with BR backup and restore, then start TiCDC incremental replication from BackupTS with redo log consistency.
- Retrieval Keywords: SET GLOBAL tidb_gc_enable=FALSE, SELECT @@global.tidb_gc_enable, BACKUP DATABASE * TO, BackupTS, RESTORE DATABASE * FROM, Replicate incremental data, changefeed.toml, [consistent], level = "eventual", max-log-size, flush-interval, storage = "s3://redo, tiup cdc cli changefeed create, --changefeed-id="dr-primary-to-secondary", --start-ts, tiup cdc cli changefeed query -s, state normal, checkpoint, SET GLOBAL tidb_gc_enable=TRUE
- Follow-up Guidance: The chunk also shows how to verify the changefeed with `tiup cdc cli changefeed query -s` and how to re-enable GC after the changefeed is created.
- Classification Note: This is classified as data_pipeline because the content covers backup and restore migration plus TiCDC changefeed setup for incremental replication between primary and secondary clusters.

## Official Source Content

#### Migrate data

Use the [backup and restore feature](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview) to migrate data from the primary cluster to the secondary cluster.

1. Disable GC. To ensure that newly written data is not deleted during incremental migration, you should disable GC for the upstream cluster before backup. In this way, history data is not deleted.

    Execute the following statement to disable GC:

    ```sql
    SET GLOBAL tidb_gc_enable=FALSE;
    ```

    To verify that the change takes effect, query the value of `tidb_gc_enable`:

    ```sql
    SELECT @@global.tidb_gc_enable;
    ```

    If the value is `0`, it means that GC is disabled:

    ```
    +-------------------------+
    | @@global.tidb_gc_enable |
    +-------------------------+
    |                       0 |
    +-------------------------+
    1 row in set (0.00 sec)
    ```

    > **Note:**
    >
    > In production clusters, performing a backup with GC disabled might affect cluster performance. It is recommended that you back up data during off-peak hours, and set `RATE_LIMIT` to a proper value to avoid performance degradation.

2. Back up data. Execute the `BACKUP` statement in the upstream cluster to back up data:

    ```sql
    BACKUP DATABASE * TO '`s3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://10.0.1.10:6060&force-path-style=true`';
    ```

    ```
    +----------------------+----------+--------------------+---------------------+---------------------+
    | Destination          | Size     | BackupTS           | Queue Time          | Execution Time      |
    +----------------------+----------+--------------------+---------------------+---------------------+
    | s3://backup          | 10315858 | 431434047157698561 | 2022-02-25 19:57:59 | 2022-02-25 19:57:59 |
    +----------------------+----------+--------------------+---------------------+---------------------+
    1 row in set (2.11 sec)
    ```

    After the `BACKUP` statement is executed, TiDB returns metadata about the backup data. Pay attention to `BackupTS`, because data generated before it is backed up. In this document, `BackupTS` is used as **the start of incremental migration**.

3. Restore data. Execute the `RESTORE` statement in the secondary cluster to restore data:

    ```sql
    RESTORE DATABASE * FROM '`s3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://10.0.1.10:6060&force-path-style=true`';
    ```

    ```
    +----------------------+----------+----------+---------------------+---------------------+
    | Destination          | Size     | BackupTS | Queue Time          | Execution Time      |
    +----------------------+----------+----------+---------------------+---------------------+
    | s3://backup          | 10315858 | 0        | 2022-02-25 20:03:59 | 2022-02-25 20:03:59 |
    +----------------------+----------+----------+---------------------+---------------------+
    1 row in set (41.85 sec)
    ```
#### Replicate incremental data

After migrating data as described in the preceding section, you can replicate incremental data from the primary cluster to the secondary cluster starting from the **BackupTS**.

1. Create a changefeed.

    Create a changefeed configuration file `changefeed.toml`.

    ```toml
    [consistent]
    # eventual consistency: redo logs are used to ensure eventual consistency in disaster scenarios.
    level = "eventual"
    # The size of a single redo log, in MiB. The default value is 64, and the recommended value is less than 128.
    max-log-size = 64
    # The interval for refreshing or uploading redo logs to Amazon S3, in milliseconds. The default value is 1000, and the recommended value range is 500-2000.
    flush-interval = 2000
    # The path where redo logs are saved.
    storage = "s3://redo?access-key=minio&secret-access-key=miniostorage&endpoint=http://10.0.1.10:6060&force-path-style=true"
    ```

    In the primary cluster, run the following command to create a changefeed from the primary to the secondary cluster:

    ```shell
    tiup cdc cli changefeed create --server=http://10.1.1.9:8300 \
    --sink-uri="mysql://{username}:{password}@10.1.1.4:4000" \
    --changefeed-id="dr-primary-to-secondary" --start-ts="431434047157698561"
    ```

    For more information about the changefeed configurations, see [TiCDC Changefeed Configurations](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config).

2. To check whether a changefeed task runs properly, run the `changefeed query` command. The query result includes the task information and the task state. You can specify the `--simple` or `-s` argument to display only the basic replication state and the checkpoint information. If you do not specify this argument, the output includes detailed task configuration, replication state, and replication table information.

    ```shell
    tiup cdc cli changefeed query -s --server=http://10.1.1.9:8300 --changefeed-id="dr-primary-to-secondary"
    ```

    ```shell
    {
    "state": "normal",
    "tso": 431434047157998561,  # The TSO to which the changefeed has been replicated
    "checkpoint": "2020-08-27 10:12:19.579", # The physical time corresponding to the TSO
    "error": null
    }
    ```

3. Enable GC.

    TiCDC ensures that history data is not garbage collected before it is replicated. Therefore, after creating a changefeed from the primary cluster to the secondary cluster, you can execute the following statement to enable GC again.

   Execute the following statement to enable GC:

    ```sql
    SET GLOBAL tidb_gc_enable=TRUE;
    ```

    To verify that the change takes effect, query the value of `tidb_gc_enable`:

    ```sql
    SELECT @@global.tidb_gc_enable;
    ```

    If the value is `1`, it means that GC is enabled:

    ```
    +-------------------------+
    | @@global.tidb_gc_enable |
    +-------------------------+
    |                       1 |
    +-------------------------+
    1 row in set (0.00 sec)
    ```
