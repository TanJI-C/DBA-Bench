# Set up forward TiCDC replication and verify consistency

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-upgrade-migration-guide.md`
- Source Title: `Migrate and Upgrade a TiDB Cluster`
- Source Heading Path: `Migrate and Upgrade a TiDB Cluster > Step 3: Replicate incremental data | Migrate and Upgrade a TiDB Cluster > Step 3: Replicate incremental data > 1. Establish a forward data replication channel | Migrate and Upgrade a TiDB Cluster > Step 3: Replicate incremental data > 2. Verify data consistency`
- Source Line Ranges: `117-178`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `pd`, `tikv`, `tidb`, `shared`
- Topic Tags: `changefeed`, `start-ts`, `checkpoint`, `replication-lag`, `gc-ttl`, `consistency-check`, `sync-diff-inspector`, `syncpoint`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0118_9e704b7c09`
- Source ID: `tidb-docs-8.1:tidb-upgrade-migration-guide.md#step-3-replicate-incremental-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6219a969cb306007655fea42df574516295353b85cf323598eba5b08e1ff0f17`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-upgrade-migration-guide#step-3-replicate-incremental-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-upgrade-migration-guide.md

## Retrieval Guidance

- Use When: Use this chunk when setting up forward TiCDC replication from the old cluster to the upgraded new cluster and verifying replication progress and data consistency.
- Retrieval Keywords: Step 3: Replicate incremental data, Establish a forward data replication channel, TiCDC component version must match the major version of the old cluster, changefeed create, --start-ts ${tso}, exact backup TSO recorded in Step 2, tiup ctl:${cluster_version} cdc changefeed create, tiup ctl:${cluster_version} cdc changefeed list, state normal, checkpoint, tso continuously advancing, Changefeed checkpoint lag, within 5 minutes, Sink flush rows/s, TiCDC logs, gc-ttl, defaults to 24 hours, PD's GC safe point, failed state, sync-diff-inspector, ./sync_diff_inspector --config=./config.toml, Syncpoint, Upstream and Downstream Clusters Data Validation and Snapshot Read, comparing table row counts
- Follow-up Guidance: After replication is stable and consistency is verified, the source proceeds to switching traffic to the new cluster and setting up reverse replication.
- Classification Note: This is classified as a data_pipeline chunk because it focuses on TiCDC Changefeed creation, replication monitoring, retention settings, and consistency validation between clusters.

## Official Source Content

## Step 3: Replicate incremental data
### 1. Establish a forward data replication channel

At this stage, the old cluster remains at its original version, while the new cluster has been upgraded to the target version. In this step, you need to establish a forward data replication channel from the old cluster to the new cluster.

> **Note:**
>
> The TiCDC component version must match the major version of the old cluster.

- Create a Changefeed task and set the incremental replication starting point (`${tso}`) to the exact backup TSO recorded in [Step 2](#step-2-prepare-the-new-cluster) to prevent data loss:

    ```shell
    tiup ctl:${cluster_version} cdc changefeed create --server http://${cdc_host}:${cdc_port} --sink-uri="mysql://${username}:${password}@${tidb_endpoint}:${port}" --config config.toml --start-ts ${tso}
    ```

- Check the replication task status and confirm that `tso` or `checkpoint` is continuously advancing:

    ```shell
    tiup ctl:${cluster_version} cdc changefeed list --server http://${cdc_host}:${cdc_port}
    ```

    The output is as follows:

    ```shell
    [{
        "id": "cdcdb-cdc-task-standby",
        "summary": {
          "state": "normal",
          "tso": 417886179132964865,
          "checkpoint": "202x-xx-xx xx:xx:xx.xxx",
          "error": null
        }
    }]
    ```

During incremental data replication, continuously monitor the replication channel status and adjust settings if needed:

- Latency metrics: ensure that `Changefeed checkpoint lag` remains within an acceptable range, such as within 5 minutes.
- Throughput health: ensure that `Sink flush rows/s` consistently exceeds the business write rate.
- Errors and alerts: regularly check TiCDC logs and alert information.
- (Optional) Test data replication: update test data and verify that Changefeed correctly replicates it to the new cluster.
- (Optional) Adjust the TiCDC configuration item [`gc-ttl`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-server-config) (defaults to 24 hours).

    If a replication task is unavailable or interrupted and cannot be resolved in time, `gc-ttl` ensures that data needed by TiCDC is retained in TiKV without being cleaned by garbage collection (GC). If this duration is exceeded, the replication task enters a `failed` state and cannot recover. In this case, PD's GC safe point continues advancing, requiring a new backup to restart the process.

    Increasing the value of `gc-ttl` accumulates more MVCC data, similar to increasing `tidb_gc_life_time`. It is recommended to set it to a reasonably long but appropriate value.
### 2. Verify data consistency

After data replication is complete, verify data consistency between the old and new clusters using the following methods:

- Use the [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview) tool:

    ```shell
    ./sync_diff_inspector --config=./config.toml
    ```

- Use the snapshot configuration of [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview) with the [Syncpoint](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-upstream-downstream-check) feature of TiCDC to verify data consistency without stopping Changefeed replication. For more information, see [Upstream and Downstream Clusters Data Validation and Snapshot Read](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-upstream-downstream-check).

- Perform manual validation of business data, such as comparing table row counts.
