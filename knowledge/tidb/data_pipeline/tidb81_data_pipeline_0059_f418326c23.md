# Migrate incremental data with TiCDC changefeed and GC

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/replicate-between-primary-and-secondary-clusters.md`
- Source Title: `Replicate data between primary and secondary clusters`
- Source Heading Path: `Replicate Data Between Primary and Secondary Clusters > Step 3. Migrate incremental data`
- Source Line Ranges: `214-274`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `sql`, `tiup`
- Topic Tags: `incremental-replication`, `changefeed`, `redo-log`, `gc`, `start-ts`, `sink-uri`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0059_f418326c23`
- Source ID: `tidb-docs-8.1:replicate-between-primary-and-secondary-clusters.md#step-3-migrate-incremental-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6e5fe40625771add7fd60a4bcc4ff71bc753629e86ea3c7cee3289f56ad4d34b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/replicate-between-primary-and-secondary-clusters#step-3-migrate-incremental-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/replicate-between-primary-and-secondary-clusters.md

## Retrieval Guidance

- Use When: Use this chunk when finding how to create a TiCDC changefeed for incremental migration after full data migration and how GC is enabled and verified in that workflow.
- Retrieval Keywords: Step 3. Migrate incremental data, TiCDC, changefeed.toml, [consistent], level = "eventual", storage = "s3://redo, tiup cdc cli changefeed create, --server, --sink-uri, --changefeed-id, --start-ts, BackupTS, SET GLOBAL tidb_gc_enable=TRUE;, SELECT @@global.tidb_gc_enable;, GC safepoint
- Follow-up Guidance: The source notes that the changefeed start timestamp must be the backup time or BackupTS from Step 2 and points to TiCDC Changefeed Configurations and the TiCDC GC safepoint FAQ for more details.
- Classification Note: This is classified as a data_pipeline chunk because the official content describes configuring TiCDC changefeed-based incremental replication, redo log storage, and GC behavior for ongoing data movement.

## Official Source Content

## Step 3. Migrate incremental data

1. Deploy TiCDC.

    After finishing full data migration, deploy and configure a TiCDC to replicate incremental data. In production environments, deploy TiCDC as instructed in [Deploy TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc). In this document, a TiCDC node has been started upon the creation of the test clusters. Therefore, we skip the step of deploying TiCDC and proceed with changefeed configuration.

2. Create a changefeed.

    Create a changefeed configuration file `changefeed.toml`.

    ```shell
    [consistent]
    # Consistency level, eventual means enabling consistent replication
    level = "eventual"
    # Use S3 to store redo logs. Other options are local and nfs.
    storage = "s3://redo?access-key=minio&secret-access-key=miniostorage&endpoint=http://172.16.6.125:6060&force-path-style=true"
    ```

    In the upstream cluster, run the following command to create a changefeed from the upstream to the downstream clusters:

    ```shell
    tiup cdc cli changefeed create --server=http://172.16.6.122:8300 --sink-uri="mysql://root:@172.16.6.125:4000" --changefeed-id="primary-to-secondary" --start-ts="431434047157698561"
    ```

    In this command, the parameters are as follows:

    - `--server`: IP address of any node in the TiCDC cluster
    - `--sink-uri`: URI of the downstream cluster
    - `--start-ts`: start timestamp of the changefeed, must be the backup time (or BackupTS mentioned in [Step 2. Migrate full data](#step-2-migrate-full-data))

    For more information about the changefeed configurations, see [TiCDC Changefeed Configurations](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config).

3. Enable GC.

    In incremental migration using TiCDC, GC only removes history data that is replicated. Therefore, after creating a changefeed, you need to run the following command to enable GC. For details, see [What is the complete behavior of TiCDC garbage collection (GC) safepoint?](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#what-is-the-complete-behavior-of-ticdc-garbage-collection-gc-safepoint).

    To enable GC, run the following command:

    ```sql
    MySQL [test]> SET GLOBAL tidb_gc_enable=TRUE;
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
    |                       1 |
    +-------------------------+
    1 row in set (0.00 sec)
    ```
