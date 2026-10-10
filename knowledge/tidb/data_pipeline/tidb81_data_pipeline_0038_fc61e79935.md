# Incremental replication with TiCDC and GC re-enable

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-tidb-to-mysql.md`
- Source Title: `Migrate Data from TiDB to MySQL-compatible Databases`
- Source Heading Path: `Migrate Data from TiDB to MySQL-compatible Databases > Step 3. Migrate incremental data`
- Source Line Ranges: `152-203`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `incremental-migration`, `changefeed`, `start-ts`, `gc-enable`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0038_fc61e79935`
- Source ID: `tidb-docs-8.1:migrate-from-tidb-to-mysql.md#step-3-migrate-incremental-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `08647321757b0c03bb224e1790f0503f927a58b82a24545b4897b2a1d6c442bd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-tidb-to-mysql#step-3-migrate-incremental-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-tidb-to-mysql.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented incremental migration procedure with TiCDC, including changefeed creation from a specific BackupTS and re-enabling GC after the changefeed is created.
- Retrieval Keywords: Step 3. Migrate incremental data, TiCDC, Deploy TiCDC, changefeed create, tiup cdc:v<CLUSTER_VERSION> cli changefeed create, --server=http://127.0.0.1:8300, --sink-uri="mysql://root:@127.0.0.1:3306", --changefeed-id="upstream-to-downstream", --start-ts="434217889191428107", start-ts must be the backup time, SET GLOBAL tidb_gc_enable=TRUE;, SELECT @@global.tidb_gc_enable;, tidb_gc_enable, GC safepoint
- Follow-up Guidance: The documented follow-up is to migrate services after the changefeed is created and incremental data is being replicated.
- Classification Note: This is classified as a data_pipeline chunk because it covers TiCDC-based incremental replication configuration and the related GC setting for ongoing data synchronization.

## Official Source Content

## Step 3. Migrate incremental data

1. Deploy TiCDC.

    After finishing full data migration, deploy and configure a TiCDC cluster to replicate incremental data. In production environments, deploy TiCDC as instructed in [Deploy TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc). In this document, a TiCDC node has been started upon the creation of the test cluster. Therefore, you can skip the step of deploying TiCDC and proceed with the next step to create a changefeed.

2. Create a changefeed.

    In the upstream cluster, run the following command to create a changefeed from the upstream to the downstream clusters:

    ```shell
    tiup cdc:v<CLUSTER_VERSION> cli changefeed create --server=http://127.0.0.1:8300 --sink-uri="mysql://root:@127.0.0.1:3306" --changefeed-id="upstream-to-downstream" --start-ts="434217889191428107"
    ```

    In this command, the parameters are as follows:

    - `--server`: IP address of any node in the TiCDC cluster
    - `--sink-uri`: URI of the downstream cluster
    - `--changefeed-id`: changefeed ID, must be in the format of a regular expression, `^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$`
    - `--start-ts`: start timestamp of the changefeed, must be the backup time (or BackupTS in the "Back up data" section in [Step 2. Migrate full data](#step-2-migrate-full-data))

    For more information about the changefeed configurations, see [Task configuration file](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config).

3. Enable GC.

    In incremental migration using TiCDC, GC only removes history data that is replicated. Therefore, after creating a changefeed, you need to run the following command to enable GC. For details, see [What is the complete behavior of TiCDC garbage collection (GC) safepoint](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#what-is-the-complete-behavior-of-ticdc-garbage-collection-gc-safepoint).

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
