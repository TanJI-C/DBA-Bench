# Incremental replication and service cutover between TiDB clusters

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-tidb-to-tidb.md`
- Source Title: `Migrate from one TiDB cluster to another TiDB cluster`
- Source Heading Path: `Migrate from One TiDB Cluster to Another TiDB Cluster > Step 3. Migrate incremental data | Migrate from One TiDB Cluster to Another TiDB Cluster > Step 4. Migrate services to the new TiDB cluster`
- Source Line Ranges: `213-301`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`, `tiup`
- Topic Tags: `incremental-migration`, `changefeed`, `gc`, `replication`, `cutover`, `service-migration`, `traffic-switch`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0040_015322b5f9`
- Source ID: `tidb-docs-8.1:migrate-from-tidb-to-tidb.md#step-3-migrate-incremental-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fabb125eebb3eb07b42e052c4f939c7e6e54230c8710ea2e488e4b05916f5362`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-tidb-to-tidb#step-3-migrate-incremental-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-tidb-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when handling incremental migration between TiDB clusters with TiCDC, including creating a changefeed, enabling GC, and cutting over read and write traffic to the downstream cluster.
- Retrieval Keywords: TiCDC, tiup cdc cli changefeed create, --server, --sink-uri, --changefeed-id, --start-ts, BackupTS, upstream-to-downstream, SET GLOBAL tidb_gc_enable=TRUE, SELECT @@global.tidb_gc_enable, tiup cdc cli changefeed pause, tiup cdc cli changefeed list, checkpoint, state stopped, downstream-to-upstream, migrate incremental data, migrate services to the new TiDB cluster
- Follow-up Guidance: The content also covers verifying `tidb_gc_enable`, checking that the paused changefeed status is `stopped` and that the `checkpoint` time is later than the time of stopping writes, and then creating a reverse changefeed from downstream to upstream.
- Classification Note: This is classified as a self-managed TiCDC data pipeline migration chunk because it describes incremental replication setup and service cutover commands between an upstream and a downstream TiDB cluster using `tiup cdc cli` and TiDB SQL.

## Official Source Content

## Step 3. Migrate incremental data

1. Deploy TiCDC.

    After finishing full data migration, deploy and configure a TiCDC to replicate incremental data. In production environments, deploy TiCDC as instructed in [Deploy TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc). In this document, a TiCDC node has been started upon the creation of the test clusters. Therefore, you can skip the step of deploying TiCDC and proceed with changefeed configuration.

2. Create a changefeed.

    In the upstream cluster, run the following command to create a changefeed from the upstream to the downstream clusters:

    ```shell
    tiup cdc cli changefeed create --server=http://172.16.6.122:8300 --sink-uri="mysql://root:@172.16.6.125:4000" --changefeed-id="upstream-to-downstream" --start-ts="431434047157698561"
    ```

    In this command, the parameters are as follows:

    - `--server`: IP address of any node in the TiCDC cluster
    - `--sink-uri`: URI of the downstream cluster
    - `--changefeed-id`: changefeed ID, must be in the format of a regular expression, ^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$
    - `--start-ts`: start timestamp of the changefeed, must be the backup time (or BackupTS in the "Back up data" section in [Step 2. Migrate full data](#step-2-migrate-full-data))

    For more information about the changefeed configurations, see [Task configuration file](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config).

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
## Step 4. Migrate services to the new TiDB cluster

After creating a changefeed, data written to the upstream cluster is replicated to the downstream cluster with low latency. You can migrate read traffic to the downstream cluster gradually. Observe for a period. If the downstream cluster is stable, you can migrate write traffic to the downstream cluster by performing the following steps:

1. Stop write services in the upstream cluster. Make sure that all upstream data are replicated to downstream before stopping the changefeed.

    ```shell
    # Stop the changefeed from the upstream cluster to the downstream cluster
    tiup cdc cli changefeed pause -c "upstream-to-downstream" --server=http://172.16.6.122:8300

    # View the changefeed status
    tiup cdc cli changefeed list
    ```

    ```
    [
      {
        "id": "upstream-to-downstream",
        "summary": {
        "state": "stopped",  # Ensure that the status is stopped
        "tso": 431747241184329729,
        "checkpoint": "2022-03-11 15:50:20.387", # This time must be later than the time of stopping writing
        "error": null
        }
      }
    ]
    ```

2. Create a changefeed from downstream to upstream. You can leave `start-ts` unspecified so as to use the default setting, because the upstream and downstream data are consistent and there is no new data written to the cluster.

    ```shell
    tiup cdc cli changefeed create --server=http://172.16.6.125:8300 --sink-uri="mysql://root:@172.16.6.122:4000" --changefeed-id="downstream -to-upstream"
    ```

3. After migrating writing services to the downstream cluster, observe for a period. If the downstream cluster is stable, you can discard the upstream cluster.
